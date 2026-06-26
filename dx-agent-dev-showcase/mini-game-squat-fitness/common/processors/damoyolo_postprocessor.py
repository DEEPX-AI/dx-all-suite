"""
DamoYOLO Postprocessor

Handles DamoYOLO split-head output format:
  - output[0]: [1, N, num_classes]  class scores (sigmoid'd)
  - output[1]: [1, N, 4]           bounding boxes (x1, y1, x2, y2 in pixel scale)
No objectness score (anchor-free like YOLOv8).
"""

import cv2
import numpy as np
from typing import List

from ..base import IPostprocessor, DetectionResult, PreprocessContext
from .nms_utils import per_class_nms as _per_class_nms


class DamoYoloPostprocessor(IPostprocessor):
    """
    Postprocessor for DamoYOLO-style split-head outputs.

    Two separate tensors:
      scores  [1, N, C]  – already sigmoid, values in [0, 1]
      boxes   [1, N, 4]  – decoded pixel coordinates (x1 y1 x2 y2)
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

        self.conf_threshold = self.config.get('conf_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)
        self.num_classes = self.config.get('num_classes', 80)
        # Per-class NMS: run NMS independently per class to avoid cross-class suppression
        self.per_class_nms = self.config.get('per_class_nms', False)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        """
        Process DamoYOLO outputs.

        Args:
            outputs: [scores_tensor, boxes_tensor]
            ctx: Preprocessing context with scale/pad info

        Returns:
            List of DetectionResult
        """
        scores = np.squeeze(outputs[0])   # [N, C]
        boxes  = np.squeeze(outputs[1])   # [N, 4]

        # Max class score per box
        cls_max_scores = np.max(scores[:, :self.num_classes], axis=1)
        cls_ids = np.argmax(scores[:, :self.num_classes], axis=1)

        # Filter by confidence
        mask = cls_max_scores >= self.conf_threshold
        if not np.any(mask):
            return []

        filtered_scores = cls_max_scores[mask]
        filtered_cls_ids = cls_ids[mask]
        filtered_boxes = boxes[mask]  # already x1y1x2y2

        # NMS
        boxes_xywh = np.column_stack([
            filtered_boxes[:, 0],
            filtered_boxes[:, 1],
            filtered_boxes[:, 2] - filtered_boxes[:, 0],
            filtered_boxes[:, 3] - filtered_boxes[:, 1],
        ])

        if self.per_class_nms:
            indices = _per_class_nms(
                boxes_xywh, filtered_scores, filtered_cls_ids,
                self.conf_threshold, self.nms_threshold)
        else:
            nms_idx = cv2.dnn.NMSBoxes(
                boxes_xywh.tolist(),
                filtered_scores.tolist(),
                self.conf_threshold,
                self.nms_threshold,
            )
            indices = np.array(nms_idx).reshape(-1) if len(nms_idx) > 0 else []

        if len(indices) == 0:
            return []

        # Restore to original image coordinates
        gain = max(ctx.scale, 1e-6)
        pad_x = ctx.pad_x
        pad_y = ctx.pad_y

        results = []
        for idx in indices:
            box = filtered_boxes[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)

            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(filtered_scores[idx]),
                class_id=int(filtered_cls_ids[idx]),
            ))

        return results

    def get_model_name(self) -> str:
        return "damoyolo"
