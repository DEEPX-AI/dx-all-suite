"""
SSD Postprocessor

Handles SSD (MobileNet V1 / V2-Lite etc.) output format:
  - output[0]: [1, N, num_classes+1]  class scores (softmax, class 0 = background)
  - output[1]: [1, N, 4]             bounding boxes (normalized or decoded)

VOC 20-class + 1 background = 21 total.
Coordinates may be in [ymin, xmin, ymax, xmax] normalized (0–1) or
in [cx, cy, w, h] normalized – auto-detected based on value range.
"""

import cv2
import numpy as np
from typing import List

from ..base import IPostprocessor, DetectionResult, PreprocessContext
from .nms_utils import per_class_nms as _per_class_nms


class SSDPostprocessor(IPostprocessor):
    """
    Postprocessor for SSD-style detection outputs with background class.
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

        self.conf_threshold = self.config.get('conf_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)
        # SSD typically uses VOC (20 classes) or COCO (80 classes)
        self.num_classes = self.config.get('num_classes', 20)
        # If True, class 0 is background and foreground starts at 1
        self.has_background = self.config.get('has_background', True)
        # Per-class NMS: run NMS independently per class to avoid cross-class suppression
        self.per_class_nms = self.config.get('per_class_nms', False)

    def _parse_outputs(self, outputs):
        """Parse and normalize raw SSD outputs to (scores, boxes) arrays."""
        out0, out1 = outputs[0], outputs[1]
        if out0.ndim == 3 and out0.shape[1] < out0.shape[2]:
            out0 = out0.transpose(0, 2, 1)
        if out1.ndim == 3 and out1.shape[1] < out1.shape[2]:
            out1 = out1.transpose(0, 2, 1)
        if out0.shape[-1] == 4:
            boxes_tensor, scores_tensor = out0, out1
        elif out1.shape[-1] == 4:
            scores_tensor, boxes_tensor = out0, out1
        else:
            scores_tensor, boxes_tensor = out0, out1
        scores_raw = scores_tensor.reshape(-1, scores_tensor.shape[-1])
        fg_scores = scores_raw[:, 1:] if self.has_background else scores_raw
        return fg_scores, boxes_tensor.reshape(-1, 4)

    def _apply_nms(self, boxes_xywh, scores, cls_ids):
        """Run NMS and return kept indices."""
        if self.per_class_nms:
            return _per_class_nms(boxes_xywh, scores, cls_ids, self.conf_threshold, self.nms_threshold)
        nms_idx = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(), scores.tolist(), self.conf_threshold, self.nms_threshold)
        return np.array(nms_idx).reshape(-1) if len(nms_idx) > 0 else []

    def _scale_box(self, box: np.ndarray, ctx: PreprocessContext) -> np.ndarray:
        """Scale box from model input space back to original image space."""
        box = box.copy()
        if hasattr(ctx, 'pad_x') and ctx.pad_x == 0 and ctx.pad_y == 0:
            sx = ctx.original_width / self.input_width
            sy = ctx.original_height / self.input_height
            box[0] = np.clip(box[0] * sx, 0, ctx.original_width - 1)
            box[1] = np.clip(box[1] * sy, 0, ctx.original_height - 1)
            box[2] = np.clip(box[2] * sx, 0, ctx.original_width - 1)
            box[3] = np.clip(box[3] * sy, 0, ctx.original_height - 1)
        else:
            gain = max(ctx.scale, 1e-6)
            box[0] = np.clip((box[0] - ctx.pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - ctx.pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - ctx.pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - ctx.pad_y) / gain, 0, ctx.original_height - 1)
        return box

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        """Process SSD outputs."""
        fg_scores, boxes_raw = self._parse_outputs(outputs)
        cls_max_scores = np.max(fg_scores, axis=1)
        cls_ids = np.argmax(fg_scores, axis=1)

        mask = cls_max_scores >= self.conf_threshold
        if not np.any(mask):
            return []

        filtered_scores = cls_max_scores[mask]
        filtered_cls_ids = cls_ids[mask]
        filtered_boxes = self._decode_boxes(boxes_raw[mask])

        boxes_xywh = np.column_stack([
            filtered_boxes[:, 0], filtered_boxes[:, 1],
            filtered_boxes[:, 2] - filtered_boxes[:, 0],
            filtered_boxes[:, 3] - filtered_boxes[:, 1],
        ])
        indices = self._apply_nms(boxes_xywh, filtered_scores, filtered_cls_ids)
        if len(indices) == 0:
            return []

        return [
            DetectionResult(
                box=[float(b) for b in self._scale_box(filtered_boxes[idx], ctx)],
                confidence=float(filtered_scores[idx]),
                class_id=int(filtered_cls_ids[idx]),
            )
            for idx in indices
        ]

    def _decode_boxes(self, boxes: np.ndarray) -> np.ndarray:
        """
        Convert SSD box format to x1y1x2y2 in input pixel space.

        SSD typically outputs [ymin, xmin, ymax, xmax] normalized to [0, 1].
        We convert to [x1, y1, x2, y2] in pixel coordinates of the input image.
        """
        # If values are small, treat as normalized coordinates (0..1);
        # otherwise assume pixel coordinates. Some models output
        # [ymin,xmin,ymax,xmax] while others use [xmin,ymin,xmax,ymax].
        # Try both normalized orderings and pick the one that yields
        # sensible (positive, bounded) widths/heights.
        boxes_arr = boxes.astype(np.float32)
        if np.max(np.abs(boxes_arr)) < 5.0:
            # SSD standard format: [ymin, xmin, ymax, xmax] normalized
            x1_a = boxes_arr[:, 1] * self.input_width
            y1_a = boxes_arr[:, 0] * self.input_height
            x2_a = boxes_arr[:, 3] * self.input_width
            y2_a = boxes_arr[:, 2] * self.input_height
            w_a = x2_a - x1_a
            h_a = y2_a - y1_a

            # Alternative: [xmin, ymin, xmax, ymax] normalized
            x1_b = boxes_arr[:, 0] * self.input_width
            y1_b = boxes_arr[:, 1] * self.input_height
            x2_b = boxes_arr[:, 2] * self.input_width
            y2_b = boxes_arr[:, 3] * self.input_height
            w_b = x2_b - x1_b
            h_b = y2_b - y1_b

            def sensible_count(w, h):
                ok = (w > 1.0) & (h > 1.0)
                ok = ok & (w < self.input_width * 1.2) & (h < self.input_height * 1.2)
                return int(np.sum(ok))

            score_a = sensible_count(w_a, h_a)
            score_b = sensible_count(w_b, h_b)

            # Prefer interpretation A (SSD standard [ymin,xmin,ymax,xmax]) only
            # when it produces strictly more sensible boxes. Otherwise default to
            # B ([x1,y1,x2,y2]) — DXNN runtime typically outputs in this format.
            if score_a > score_b:  # tie(0==0): default to B (DXNN standard [x1,y1,x2,y2])
                return np.column_stack([x1_a, y1_a, x2_a, y2_a])
            return np.column_stack([x1_b, y1_b, x2_b, y2_b])

        # Pixel-space coordinates: try [x1,y1,x2,y2] first, then fallback
        # to swapped ordering if needed.
        x1 = boxes_arr[:, 0]
        y1 = boxes_arr[:, 1]
        x2 = boxes_arr[:, 2]
        y2 = boxes_arr[:, 3]
        w = x2 - x1
        h = y2 - y1
        if np.all(w > 0) and np.all(h > 0):
            return boxes_arr

        # Fallback: assume [y1,x1,y2,x2]
        x1 = boxes_arr[:, 1]
        y1 = boxes_arr[:, 0]
        x2 = boxes_arr[:, 3]
        y2 = boxes_arr[:, 2]
        return np.column_stack([x1, y1, x2, y2])

    def get_model_name(self) -> str:
        return "ssd"
