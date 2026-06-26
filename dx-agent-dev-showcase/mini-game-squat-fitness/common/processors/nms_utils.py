"""
NMS / Box conversion utilities shared across postprocessors.
"""

import cv2
import numpy as np
from typing import List


def cxcywh_to_x1y1x2y2(boxes: np.ndarray) -> np.ndarray:
    """Convert center format [cx, cy, w, h] to corner format [x1, y1, x2, y2]."""
    result = np.zeros_like(boxes)
    result[:, 0] = boxes[:, 0] - boxes[:, 2] * 0.5  # x1
    result[:, 1] = boxes[:, 1] - boxes[:, 3] * 0.5  # y1
    result[:, 2] = boxes[:, 0] + boxes[:, 2] * 0.5  # x2
    result[:, 3] = boxes[:, 1] + boxes[:, 3] * 0.5  # y2
    return result


def nms(boxes: np.ndarray, scores: np.ndarray, class_ids: np.ndarray,
        conf_threshold: float, nms_threshold: float) -> List[int]:
    """Apply NMS using cv2.dnn.NMSBoxes (x1y1x2y2 input)."""
    boxes_xywh = np.column_stack([
        boxes[:, 0], boxes[:, 1],
        boxes[:, 2] - boxes[:, 0], boxes[:, 3] - boxes[:, 1]
    ])
    indices = cv2.dnn.NMSBoxes(
        boxes_xywh.tolist(), scores.tolist(),
        conf_threshold, nms_threshold
    )
    if len(indices) > 0:
        return np.array(indices).reshape(-1).tolist()
    return []


def per_class_nms(boxes_xywh: np.ndarray, scores: np.ndarray,
                  class_ids: np.ndarray,
                  conf_threshold: float, nms_threshold: float) -> List[int]:
    """Run NMS independently per class to avoid cross-class suppression."""
    keep: List[int] = []
    for cls in np.unique(class_ids):
        cls_mask = class_ids == cls
        cls_indices = np.where(cls_mask)[0]
        cls_boxes = boxes_xywh[cls_mask]
        cls_scores = scores[cls_mask]
        nms_idx = cv2.dnn.NMSBoxes(
            cls_boxes.tolist(), cls_scores.tolist(),
            conf_threshold, nms_threshold,
        )
        if len(nms_idx) > 0:
            keep.extend(cls_indices[np.array(nms_idx).reshape(-1)].tolist())
    return sorted(keep)
