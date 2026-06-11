"""
Palm Detection Postprocessor

Handles MediaPipe PalmDetection (BlazePalm) output format:
  - output[0]: [1, N, 18]  regression (4 box values + 7×2 keypoint values)
  - output[1]: [1, N, 1]   classification scores (sigmoid logit, single class)

Box format: the 4 regression values are [cx, cy, w, h] offsets relative
to SSD-style anchors.  We generate the anchors using the same scheme as
MediaPipe's SSD anchor generator (feature map sizes computed from input
size and strides).
"""

import cv2
import math
import numpy as np
from typing import List

from ..base import IPostprocessor, DetectionResult, PreprocessContext


class PalmDetectionPostprocessor(IPostprocessor):
    """
    Postprocessor for MediaPipe PalmDetection (BlazePalm) SSD outputs.
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

        self.conf_threshold = self.config.get('conf_threshold', 0.5)
        self.nms_threshold = self.config.get('nms_threshold', 0.3)

        # Build SSD anchors (MediaPipe style)
        self._anchors = None  # lazy-built on first call

    def _build_anchors(self, num_anchors: int) -> np.ndarray:
        """
        Generate SSD anchors compatible with MediaPipe PalmDetection.
        The model uses 2 anchors per cell at strides [8, 16, 16, 16]
        for a 192-input or 2 anchors at [8, 16] for a 128/256-input.

        Returns:
            anchors: [N, 4] with columns [cx, cy, 1, 1] (normalized 0-1)
        """
        # MediaPipe BlazePalm anchors config:
        #   strides: [8, 16, 16, 16]  for 192 input  → 576 + 144 + 144 + 144 = 1008
        #   strides: [8, 16]          for 256 input  → 1024 + 256 = 1280
        #   for 128 input with [8, 16]: 256 + 64 = 320, 2 anchors each = 640
        #   for 224 input: need to find matching scheme

        # Try common stride configs until anchor count matches
        for strides, anchors_per_cell in [
            ([8, 16, 16, 16], 2),
            ([8, 16], 2),
            ([8, 16, 32], 2),
            ([8, 16, 16, 16], 1),
            ([8, 16], 1),
            ([4, 8, 16], 2),
            ([4, 8], 2),
        ]:
            total = sum(
                math.ceil(self.input_height / s) * math.ceil(self.input_width / s) * anchors_per_cell
                for s in strides
            )
            if total == num_anchors:
                return self._generate_anchors(strides, anchors_per_cell)

        # Fallback: uniform grid anchors
        side = int(math.sqrt(num_anchors))
        if side * side == num_anchors:
            cx = (np.arange(side) + 0.5) / side
            cy = (np.arange(side) + 0.5) / side
            xv, yv = np.meshgrid(cx, cy)
            anchors = np.column_stack([
                xv.ravel(), yv.ravel(),
                np.ones(num_anchors), np.ones(num_anchors)
            ])
            return anchors.astype(np.float32)

        # last resort: evenly spaced
        anchors = np.zeros((num_anchors, 4), dtype=np.float32)
        anchors[:, 0] = 0.5
        anchors[:, 1] = np.linspace(0, 1, num_anchors)
        anchors[:, 2] = 1.0
        anchors[:, 3] = 1.0
        return anchors

    def _generate_anchors(self, strides, anchors_per_cell):
        anchors = []
        for stride in strides:
            grid_h = math.ceil(self.input_height / stride)
            grid_w = math.ceil(self.input_width / stride)
            for y in range(grid_h):
                cy = (y + 0.5) / grid_h
                for x in range(grid_w):
                    cx = (x + 0.5) / grid_w
                    for _ in range(anchors_per_cell):
                        anchors.append([cx, cy, 1.0, 1.0])
        return np.array(anchors, dtype=np.float32)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        """
        Args:
            outputs: [regression [1,N,18], scores [1,N,1]]  (order auto-detected)
        """
        # Figure out which output is scores (last_dim == 1) vs regression
        a = np.squeeze(outputs[0])
        b = np.squeeze(outputs[1])

        if a.ndim == 1 or (a.ndim == 2 and a.shape[-1] == 1):
            scores_raw = a.reshape(-1)
            reg_raw = b
        elif b.ndim == 1 or (b.ndim == 2 and b.shape[-1] == 1):
            scores_raw = b.reshape(-1)
            reg_raw = a
        else:
            # Smaller last-dim → scores
            if a.shape[-1] < b.shape[-1]:
                scores_raw = a.reshape(-1)
                reg_raw = b
            else:
                scores_raw = b.reshape(-1)
                reg_raw = a

        n = reg_raw.shape[0]

        # Build anchors lazily
        if self._anchors is None or self._anchors.shape[0] != n:
            self._anchors = self._build_anchors(n)

        # Sigmoid on score logits
        scores = 1.0 / (1.0 + np.exp(-np.clip(scores_raw, -50, 50)))

        mask = scores >= self.conf_threshold
        if not np.any(mask):
            return []

        filtered_scores = scores[mask]
        filtered_reg = reg_raw[mask, :4]       # only box values (ignore keypoints)
        filtered_anchors = self._anchors[mask]

        # Decode boxes: offsets relative to anchors (normalized)
        # cx = anchor_cx + dx / input_width
        # cy = anchor_cy + dy / input_height
        # w  = dw / input_width
        # h  = dh / input_height
        cx = filtered_anchors[:, 0] + filtered_reg[:, 0] / self.input_width
        cy = filtered_anchors[:, 1] + filtered_reg[:, 1] / self.input_height
        w = filtered_reg[:, 2] / self.input_width
        h = filtered_reg[:, 3] / self.input_height

        # Convert to x1y1x2y2 pixel coords
        x1 = (cx - w * 0.5) * self.input_width
        y1 = (cy - h * 0.5) * self.input_height
        x2 = (cx + w * 0.5) * self.input_width
        y2 = (cy + h * 0.5) * self.input_height

        boxes = np.column_stack([x1, y1, x2, y2])

        # NMS
        boxes_xywh = np.column_stack([
            boxes[:, 0], boxes[:, 1],
            boxes[:, 2] - boxes[:, 0], boxes[:, 3] - boxes[:, 1]
        ])
        nms_idx = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(), filtered_scores.tolist(),
            self.conf_threshold, self.nms_threshold
        )
        if len(nms_idx) == 0:
            return []
        indices = np.array(nms_idx).reshape(-1)

        # Scale to original (letterbox-aware)
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
            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(filtered_scores[idx]),
                class_id=0,
            ))
        return results

    def get_model_name(self) -> str:
        return "palm"
