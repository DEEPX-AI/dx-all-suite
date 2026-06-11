"""
NanoDet Postprocessor

Handles NanoDet/NanoDet-Plus output with Distribution Focal Loss (DFL):
  - output[0]: [1, N, num_classes + 4 * (reg_max + 1)]
    Combined tensor with class scores (raw logits) and bbox distribution values.

Auto-detects reg_max and anchor grid from the actual tensor shape so that the
same postprocessor works for all NanoDet variants:
  - NanoDet (416, strides [8,16,32], reg_max=10)  →  3549 × 124
  - NanoDet-Plus M (416, strides [8,16,32,64], reg_max=7)  →  3598 × 112
  - NanoDet-RepVGGA1 (640, strides [8,16,32], reg_max=10)  →  8400 × 124

DFL decoding:
  For each of the 4 sides (left, top, right, bottom):
    softmax(bins values) → weighted sum with [0,1,...,reg_max] → distance in stride units
  Then convert distances from anchor center to x1y1x2y2.
"""

import math
import cv2
import numpy as np
from typing import List

from ..base import IPostprocessor, DetectionResult, PreprocessContext


class NanoDetPostprocessor(IPostprocessor):
    """
    Postprocessor for NanoDet-Plus style outputs with DFL bbox regression.
    Auto-detects reg_max and anchor grid from the actual model output.
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

        self.conf_threshold = self.config.get('conf_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)
        self.num_classes = self.config.get('num_classes', 80)

        # reg_max / strides will be auto-detected from actual tensor shape
        self._hint_reg_max = self.config.get('reg_max', None)
        self._hint_strides = self.config.get('strides', None)

        # Lazy-built on first process() call
        self._anchor_centers = None
        self._stride_tensor = None
        self._effective_reg_max = None
        self._dfl_weights = None

    # ------------------------------------------------------------------ #
    #                         anchor helpers                              #
    # ------------------------------------------------------------------ #
    def _build_anchors(self, input_size: int, strides: list, use_ceil: bool = False):
        """
        Build per-anchor center coordinates and corresponding strides.
        Returns: (centers [N,2], strides_arr [N])
        """
        centers_list = []
        strides_list = []
        for stride in strides:
            if use_ceil:
                h = math.ceil(input_size / stride)
                w = math.ceil(input_size / stride)
            else:
                h = input_size // stride
                w = input_size // stride
            x = (np.arange(w) + 0.5) * stride
            y = (np.arange(h) + 0.5) * stride
            xv, yv = np.meshgrid(x, y)
            centers_list.append(np.stack([xv.ravel(), yv.ravel()], axis=1))
            strides_list.append(np.full(h * w, stride, dtype=np.float32))
        return np.concatenate(centers_list, axis=0), np.concatenate(strides_list, axis=0)

    @staticmethod
    def _anchor_total(size: int, strides: list, use_ceil: bool) -> int:
        """Compute the total number of anchor points for given parameters."""
        if use_ceil:
            return sum(math.ceil(size / s) ** 2 for s in strides)
        return sum((size // s) ** 2 for s in strides)

    def _try_rebuild_anchors(self, target_n: int) -> bool:
        """
        Search for (input_size, strides, ceil_mode) that produce exactly
        target_n anchor points.
        """
        candidate_sizes = [self.input_width, 416, 320, 384, 448, 480, 512, 640]
        candidate_strides = [[8, 16, 32], [8, 16, 32, 64]]

        # Prioritize hint strides if provided
        if self._hint_strides:
            candidate_strides = [self._hint_strides] + [
                s for s in candidate_strides if s != self._hint_strides
            ]

        import itertools
        for size, strides, use_ceil in itertools.product(
                candidate_sizes, candidate_strides, [False, True]):
            if self._anchor_total(size, strides, use_ceil) == target_n:
                self._anchor_centers, self._stride_tensor = \
                    self._build_anchors(size, strides, use_ceil)
                return True
        return False

    # ------------------------------------------------------------------ #
    #                         DFL decode                                  #
    # ------------------------------------------------------------------ #
    def _dfl_decode(self, reg: np.ndarray, bins: int) -> np.ndarray:
        """
        Decode DFL distribution to distance values.

        Args:
            reg: [N, 4*bins]  raw distribution logits
            bins: reg_max + 1

        Returns:
            distances: [N, 4]  (left, top, right, bottom) in stride units
        """
        n = reg.shape[0]
        dfl_weights = np.arange(bins, dtype=np.float32)
        reg4 = reg.reshape(n, 4, bins)             # [N, 4, bins]
        # Softmax per side
        max_val = np.max(reg4, axis=2, keepdims=True)
        exp_val = np.exp(reg4 - max_val)
        softmax_val = exp_val / np.sum(exp_val, axis=2, keepdims=True)
        # Weighted sum: [N, 4]
        distances = np.sum(softmax_val * dfl_weights, axis=2)
        return distances

    # ------------------------------------------------------------------ #
    #                         main process                                #
    # ------------------------------------------------------------------ #
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        """
        Args:
            outputs: single-tensor [1, N, C + 4*(reg_max+1)]
            ctx: PreprocessContext
        Returns:
            List of DetectionResult
        """
        pred = np.squeeze(outputs[0])  # [N, total_cols]
        n, total_cols = pred.shape[0], pred.shape[-1]

        # --- Auto-detect reg_max from tensor shape ---
        reg_cols = total_cols - self.num_classes
        bins = reg_cols // 4  # reg_max + 1

        # Use hint if provided and consistent with tensor shape
        if self._hint_reg_max is not None:
            hint_bins = self._hint_reg_max + 1
            if hint_bins * 4 == reg_cols:
                bins = hint_bins

        if bins < 2 or reg_cols % 4 != 0:
            raise ValueError(
                f"NanoDet: unexpected output shape [{n}, {total_cols}] "
                f"with num_classes={self.num_classes}. "
                f"reg_cols={reg_cols} is not divisible by 4 for DFL decode."
            )

        # --- Rebuild anchors if needed ---
        if self._anchor_centers is None or self._anchor_centers.shape[0] != n:
            if not self._try_rebuild_anchors(n):
                raise ValueError(
                    f"NanoDet: cannot find (size, strides) matching "
                    f"anchor count N={n}. Check model input dimensions."
                )

        cls_raw = pred[:, :self.num_classes]              # [N, C]
        reg_raw = pred[:, self.num_classes:]              # [N, 4*bins]

        # Auto-detect: if all values in [0,1], output is already post-sigmoid;
        # otherwise apply sigmoid to raw logits.
        if cls_raw.min() >= 0.0 and cls_raw.max() <= 1.0:
            cls_scores = cls_raw
        else:
            cls_scores = 1.0 / (1.0 + np.exp(-cls_raw))

        cls_max_scores = np.max(cls_scores, axis=1)
        cls_ids = np.argmax(cls_scores, axis=1)

        mask = cls_max_scores >= self.conf_threshold
        if not np.any(mask):
            return []

        filtered_scores = cls_max_scores[mask]
        filtered_cls_ids = cls_ids[mask]
        filtered_reg = reg_raw[mask]
        filtered_centers = self._anchor_centers[mask]
        filtered_strides = self._stride_tensor[mask]

        # DFL decode → distances [M, 4]  (left, top, right, bottom)
        distances = self._dfl_decode(filtered_reg, bins)
        distances *= filtered_strides[:, None]  # scale by stride

        # Convert to x1y1x2y2
        x1 = filtered_centers[:, 0] - distances[:, 0]
        y1 = filtered_centers[:, 1] - distances[:, 1]
        x2 = filtered_centers[:, 0] + distances[:, 2]
        y2 = filtered_centers[:, 1] + distances[:, 3]
        boxes = np.column_stack([x1, y1, x2, y2])

        # NMS
        boxes_xywh = np.column_stack([
            boxes[:, 0], boxes[:, 1],
            boxes[:, 2] - boxes[:, 0], boxes[:, 3] - boxes[:, 1],
        ])
        indices = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(),
            filtered_scores.tolist(),
            self.conf_threshold,
            self.nms_threshold,
        )
        if len(indices) == 0:
            return []

        indices = np.array(indices).reshape(-1)

        # Restore to original coordinates
        gain = max(ctx.scale, 1e-6)
        pad_x = ctx.pad_x
        pad_y = ctx.pad_y

        results = []
        for idx in indices:
            box = boxes[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)

            # Skip degenerate boxes (zero width or height after clip)
            if box[2] <= box[0] or box[3] <= box[1]:
                continue

            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(filtered_scores[idx]),
                class_id=int(filtered_cls_ids[idx]),
            ))

        return results

    def get_model_name(self) -> str:
        return "nanodet"
