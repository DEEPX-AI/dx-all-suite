"""
YOLACT Postprocessor

SSD-based instance segmentation with prototype masks.

Output: 4 tensors
  - loc:        [1, N, 4]       SSD-style bbox regression (normalized decoded or deltas)
  - conf:       [1, N, C+1]    class scores with background (softmax)
  - mask_coeff: [1, N, 32]     mask prototype coefficients
  - proto:      [1, H, W, 32]  prototype mask features (or [1, 32, H, W])

Algorithm:
  1. Parse class scores (skip background = class 0)
  2. Filter by confidence threshold
  3. NMS per class
  4. Generate instance masks: sigmoid(coeff @ proto.T)
  5. Crop masks to bbox region
"""

import numpy as np
import cv2
from typing import List

from ..base import IPostprocessor, PreprocessContext, InstanceSegResult


class YOLACTPostprocessor(IPostprocessor):
    """
    Postprocessor for YOLACT instance segmentation.

    Handles SSD-style detection with prototype mask generation.
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

        self.score_threshold = self.config.get('score_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.5)
        self.num_classes = self.config.get('num_classes', 80)
        self.has_background = self.config.get('has_background', True)
        self.num_masks = self.config.get('num_masks', 32)
        self.top_k = self.config.get('top_k', 200)

        # Lazily generated — rebuilt on first process() to match model output N
        self._anchors = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _first_pass_classify(self, squeezed):
        """Initial classification pass: assign loc/conf/mask_coeff/proto by tensor shape."""
        loc_t = conf_t = mask_coeff_t = proto_t = None
        for t in squeezed:
            if t.ndim == 3:
                if proto_t is None:
                    proto_t = t
                continue
            if t.ndim != 2:
                continue
            last_dim = t.shape[-1]
            if last_dim == 4 and loc_t is None:
                loc_t = t
            elif last_dim == self.num_masks and mask_coeff_t is None:
                mask_coeff_t = t
            elif last_dim > 4 and last_dim != self.num_masks and conf_t is None:
                conf_t = t
        return loc_t, conf_t, mask_coeff_t, proto_t

    def _fallback_classify_2d(self, squeezed, loc_t, conf_t, mask_coeff_t):
        """Fallback: sort 2-D tensors by last dim to assign loc/conf/mask_coeff."""
        tensors_2d = sorted([t for t in squeezed if t.ndim == 2], key=lambda t: t.shape[-1])
        if len(tensors_2d) >= 3:
            return tensors_2d[0], tensors_2d[2], tensors_2d[1]
        return loc_t, conf_t, mask_coeff_t

    def _identify_tensors(self, outputs):
        """Return (loc_t, conf_t, mask_coeff_t, proto_t) from raw outputs."""
        squeezed = [np.squeeze(o) for o in outputs]
        loc_t, conf_t, mask_coeff_t, proto_t = self._first_pass_classify(squeezed)
        if any(v is None for v in (conf_t, loc_t, mask_coeff_t)):
            loc_t, conf_t, mask_coeff_t = self._fallback_classify_2d(squeezed, loc_t, conf_t, mask_coeff_t)
        if proto_t is None:
            proto_t = next((t for t in squeezed if t.ndim == 3), None)
        return loc_t, conf_t, mask_coeff_t, proto_t

    def _filter_detections(self, conf_t, loc_t, mask_coeff_t):
        """Score-threshold + top-K filter. Returns (scores, cls_ids, boxes, coeffs, orig_indices)."""
        fg_scores = conf_t[:, 1:] if self.has_background else conf_t
        cls_ids = np.argmax(fg_scores, axis=1)
        cls_max_scores = np.max(fg_scores, axis=1)

        mask = cls_max_scores >= self.score_threshold
        if not np.any(mask):
            return None

        idx = np.nonzero(mask)[0]
        scores = cls_max_scores[idx]
        cls_ids = cls_ids[idx]
        boxes = loc_t[idx]
        coeffs = mask_coeff_t[idx]

        if len(scores) > self.top_k:
            top = np.argsort(scores)[::-1][:self.top_k]
            scores, cls_ids, boxes, coeffs = scores[top], cls_ids[top], boxes[top], coeffs[top]
            idx = idx[top]

        return scores, cls_ids, boxes, coeffs, idx

    def _compute_masks(self, kept_coeffs, proto_t):
        """Compute sigmoid masks from coefficients and prototype features."""
        mask_h, mask_w = proto_t.shape[0], proto_t.shape[1]
        proto_flat = proto_t.reshape(-1, self.num_masks)
        raw = kept_coeffs @ proto_flat.T
        masks = 1.0 / (1.0 + np.exp(-raw))
        return masks.reshape(-1, mask_h, mask_w), mask_h, mask_w

    def _fast_nms(self, boxes: np.ndarray, scores: np.ndarray,
                  iou_threshold: float) -> np.ndarray:
        """
        YOLACT-style Fast NMS — more aggressive than standard greedy NMS.

        Any detection whose max IoU with *any* higher-scoring detection
        exceeds the threshold is removed, even if that higher-scoring
        detection is itself suppressed.  This eliminates the transitive
        duplicates that greedy NMS leaves behind.
        """
        n = len(scores)
        if n == 0:
            return np.array([], dtype=int)

        order = np.argsort(scores)[::-1]
        boxes_sorted = boxes[order]

        # Vectorised pairwise overlap
        x1 = np.maximum(boxes_sorted[:, 0:1], boxes_sorted[:, 0:1].T)
        y1 = np.maximum(boxes_sorted[:, 1:2], boxes_sorted[:, 1:2].T)
        x2 = np.minimum(boxes_sorted[:, 2:3], boxes_sorted[:, 2:3].T)
        y2 = np.minimum(boxes_sorted[:, 3:4], boxes_sorted[:, 3:4].T)
        inter = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
        area = ((boxes_sorted[:, 2] - boxes_sorted[:, 0])
                * (boxes_sorted[:, 3] - boxes_sorted[:, 1]))
        union = area[:, None] + area[None, :] - inter
        iou = inter / (union + 1e-6)

        # Containment ratio: intersection / min(area_a, area_b).
        # Catches a small box fully inside a large box (low IoU but high
        # containment) which standard IoU-only NMS misses.  Scaled by 0.65
        # so that a box must be ~77 %+ contained to be suppressed — this
        # avoids killing distinct objects that merely overlap partially.
        min_area = np.minimum(area[:, None], area[None, :])
        iomin = inter / (min_area + 1e-6)
        overlap = np.maximum(iou, iomin * 0.65)

        # Upper triangle only (column j compared with rows 0..j-1)
        overlap = np.triu(overlap, k=1)

        # For each detection, max overlap with any higher-scoring detection
        max_overlap = np.max(overlap, axis=0)
        keep_mask = max_overlap <= iou_threshold

        return order[keep_mask]

    def _scale_masks_and_crop(self, masks, boxes_pixel_keep):
        """Upscale masks to input size and zero out pixels outside bbox."""
        k = len(masks)
        scaled = np.zeros((k, self.input_height, self.input_width), dtype=np.float32)
        for i, m in enumerate(masks):
            scaled[i] = cv2.resize(m, (self.input_width, self.input_height),
                                   interpolation=cv2.INTER_LINEAR)
        for i, box in enumerate(boxes_pixel_keep):
            bx1, by1 = max(0, int(box[0])), max(0, int(box[1]))
            bx2, by2 = min(self.input_width, int(box[2])), min(self.input_height, int(box[3]))
            scaled[i, :by1, :] = 0
            scaled[i, by2:, :] = 0
            scaled[i, :, :bx1] = 0
            scaled[i, :, bx2:] = 0
        return scaled

    def _to_original_coords(self, box, scaled_mask_i, ctx):
        """Map a single box+mask from input space back to original image space."""
        box = box.copy()
        gain = max(ctx.scale, 1e-6)
        pad_x, pad_y = ctx.pad_x, ctx.pad_y
        ow, oh = ctx.original_width, ctx.original_height

        if pad_x == 0 and pad_y == 0:
            sx, sy = ow / self.input_width, oh / self.input_height
            box[0] = np.clip(box[0] * sx, 0, ow - 1)
            box[1] = np.clip(box[1] * sy, 0, oh - 1)
            box[2] = np.clip(box[2] * sx, 0, ow - 1)
            box[3] = np.clip(box[3] * sy, 0, oh - 1)
            orig_mask = cv2.resize(scaled_mask_i, (ow, oh), interpolation=cv2.INTER_LINEAR)
        else:
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ow - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, oh - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ow - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, oh - 1)
            unpad_h = int(round(oh * gain))
            unpad_w = int(round(ow * gain))
            m_crop = scaled_mask_i[int(pad_y):int(pad_y) + unpad_h,
                                   int(pad_x):int(pad_x) + unpad_w]
            orig_mask = (cv2.resize(m_crop, (ow, oh), interpolation=cv2.INTER_LINEAR)
                         if m_crop.size > 0
                         else np.zeros((oh, ow), dtype=np.float32))

        return box, orig_mask

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[InstanceSegResult]:
        """
        Process YOLACT outputs.

        Args:
            outputs: 4 tensors [loc, conf, mask_coeff, proto]
            ctx: Preprocessing context

        Returns:
            List of InstanceSegResult
        """
        loc_t, conf_t, mask_coeff_t, proto_t = self._identify_tensors(outputs)
        if any(v is None for v in (conf_t, loc_t, mask_coeff_t, proto_t)):
            return []

        # Rebuild anchors on first call (or when N changes) to match model output
        if self._anchors is None or self._anchors.shape[0] != loc_t.shape[0]:
            self._anchors = self._generate_ssd_anchors(target_n=loc_t.shape[0])

        # Ensure proto is [H_mask, W_mask, num_masks]
        if proto_t.shape[0] == self.num_masks or proto_t.shape[0] < proto_t.shape[-1]:
            proto_t = np.transpose(proto_t, (1, 2, 0))

        filtered = self._filter_detections(conf_t, loc_t, mask_coeff_t)
        if filtered is None:
            return []
        scores_f, cls_ids_f, boxes_f, coeff_f, orig_indices = filtered

        boxes_pixel = self._decode_boxes(boxes_f, orig_indices)

        # Reject degenerate or near-full-image boxes
        img_area = self.input_width * self.input_height
        bw = boxes_pixel[:, 2] - boxes_pixel[:, 0]
        bh = boxes_pixel[:, 3] - boxes_pixel[:, 1]
        valid = (bw >= 1) & (bh >= 1) & ((bw * bh) / img_area <= 0.65)
        if not np.any(valid):
            return []
        boxes_pixel = boxes_pixel[valid]
        scores_f = scores_f[valid]
        cls_ids_f = cls_ids_f[valid]
        coeff_f = coeff_f[valid]

        keep = self._fast_nms(boxes_pixel, scores_f, self.nms_threshold)
        if len(keep) == 0:
            return []

        masks, _, _ = self._compute_masks(coeff_f[keep], proto_t)
        scaled_masks = self._scale_masks_and_crop(masks, boxes_pixel[keep])

        results = []
        for i, idx in enumerate(keep):
            box, orig_mask = self._to_original_coords(boxes_pixel[idx], scaled_masks[i], ctx)
            results.append(InstanceSegResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(scores_f[idx]),
                class_id=int(cls_ids_f[idx]),
                mask=(orig_mask > 0.5).astype(np.uint8),
            ))

        return results

    def _decode_boxes(self, boxes: np.ndarray, orig_indices: np.ndarray = None) -> np.ndarray:
        """
        Decode box coordinates to pixel [x1, y1, x2, y2] in input space.

        YOLACT always uses SSD-encoded deltas (tx, ty, tw, th) relative to
        anchors.  Previous heuristic-based auto-detection was unreliable and
        caused box coordinate errors.  Now always uses SSD delta decoding
        (matching the C++ postprocessor).

        Args:
            boxes: Filtered box values [M, 4]
            orig_indices: Original row indices into the full loc tensor (and
                          therefore into self._anchors). Required for correct
                          SSD delta decoding after score-threshold filtering.
        """
        if self._anchors is None:
            return self._decode_normalized(boxes)

        # Select matching anchors for filtered detections
        if orig_indices is not None:
            anchors = self._anchors[orig_indices]
        elif boxes.shape[0] <= self._anchors.shape[0]:
            anchors = self._anchors[:boxes.shape[0]]
        else:
            return self._decode_normalized(boxes)

        # SSD delta decoding with standard variances (matching C++ implementation)
        variance = [0.1, 0.2]
        a_cx, a_cy, a_w, a_h = anchors[:, 0], anchors[:, 1], anchors[:, 2], anchors[:, 3]

        cx = boxes[:, 0] * variance[0] * a_w + a_cx
        cy = boxes[:, 1] * variance[0] * a_h + a_cy
        w = a_w * np.exp(np.clip(boxes[:, 2] * variance[1], -10, 10))
        h = a_h * np.exp(np.clip(boxes[:, 3] * variance[1], -10, 10))

        x1 = (cx - w / 2) * self.input_width
        y1 = (cy - h / 2) * self.input_height
        x2 = (cx + w / 2) * self.input_width
        y2 = (cy + h / 2) * self.input_height
        return np.column_stack([x1, y1, x2, y2])

    def _decode_normalized(self, boxes: np.ndarray) -> np.ndarray:
        """Decode normalized [0,1] boxes to pixel coordinates."""
        x1 = boxes[:, 0] * self.input_width
        y1 = boxes[:, 1] * self.input_height
        x2 = boxes[:, 2] * self.input_width
        y2 = boxes[:, 3] * self.input_height
        return np.column_stack([x1, y1, x2, y2])

    def _cell_anchors(self, cx, cy, scales, aspect_ratios):
        """Generate anchor entries for one grid cell.

        Ordering: scale (outer) → aspect_ratio (inner), matching RetinaNet/YOLACT
        DXNN model convention.
        """
        result = []
        for s in scales:
            for ar in aspect_ratios:
                result.append([cx, cy,
                                s * np.sqrt(ar) / self.input_width,
                                s / np.sqrt(ar) / self.input_height])
        return result

    def _generate_ssd_anchors(self, target_n: int = 0) -> np.ndarray:
        """
        Generate SSD-style prior boxes matching YOLACT config.

        Uses RetinaNet-style anchor scales: [base, base*2^(1/3), base*2^(2/3)]
        with Scale→AR ordering.
        """
        strides = [8, 16, 32, 64, 128]
        base_sizes = [24, 48, 96, 192, 384]
        r13 = 2 ** (1.0 / 3)
        r23 = 2 ** (2.0 / 3)
        total_cells = sum(
            ((self.input_height + s - 1) // s) * ((self.input_width + s - 1) // s)
            for s in strides
        )

        # Candidate anchor configurations: (scales_per_level, aspect_ratios)
        configs = [
            # RetinaNet 3 scales × 3 ARs = 9 anchors/cell (primary)
            ([[b, b * r13, b * r23] for b in base_sizes],
             [[1, 0.5, 2]] * 5),
            # 1 scale × 3 ARs = 3 anchors/cell (YOLACT default)
            ([[b] for b in base_sizes],
             [[1, 0.5, 2]] * 5),
        ]

        for scales_list, ar_list in configs:
            anchors_per_cell = len(scales_list[0]) * len(ar_list[0])
            expected = total_cells * anchors_per_cell
            if target_n > 0 and expected != target_n:
                continue
            anchors = []
            for fpn, stride in enumerate(strides):
                conv_h = (self.input_height + stride - 1) // stride
                conv_w = (self.input_width + stride - 1) // stride
                for i in range(conv_h):
                    for j in range(conv_w):
                        anchors.extend(self._cell_anchors(
                            (j + 0.5) * stride / self.input_width,
                            (i + 0.5) * stride / self.input_height,
                            scales_list[fpn], ar_list[fpn]))
            return np.array(anchors, dtype=np.float32) if anchors else None

        # No config matched — fall back without target constraint
        return self._generate_ssd_anchors(target_n=0)

    def get_model_name(self) -> str:
        return "yolact"
