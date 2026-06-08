"""
Instance Segmentation Visualizer

Draws bounding boxes with semi-transparent masks overlaid on the image.
Each instance gets a unique color. Used by YOLOv8-seg, YOLOv5-seg, YOLOv26-seg.
"""

import numpy as np
import cv2
from typing import List

from ..base import IVisualizer


# 20 distinct colors for instance segmentation
INSTANCE_COLORS = [
    (255, 56, 56), (255, 157, 151), (255, 112, 31), (255, 178, 29),
    (207, 210, 49), (72, 249, 10), (146, 204, 23), (61, 219, 134),
    (26, 147, 52), (0, 212, 187), (44, 153, 168), (0, 194, 255),
    (52, 69, 147), (100, 115, 255), (0, 24, 236), (132, 56, 255),
    (82, 0, 133), (203, 56, 255), (255, 149, 200), (255, 55, 199),
]


class InstanceSegVisualizer(IVisualizer):
    """Visualizer for instance segmentation with mask overlay."""
    
    def __init__(self, label_set: str = 'coco80', labels: List[str] = None,
                 show_boxes: bool = True):
        self.label_set = label_set
        self.labels = labels if labels is not None else self._load_labels(label_set)
        self.color_palette = INSTANCE_COLORS
        self.show_boxes = show_boxes
    
    def _load_labels(self, label_set: str) -> List[str]:
        if label_set == 'coco80':
            return [
                "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train",
                "truck", "boat", "traffic light", "fire hydrant", "stop sign",
                "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep",
                "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
                "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
                "sports ball", "kite", "baseball bat", "baseball glove", "skateboard",
                "surfboard", "tennis racket", "bottle", "wine glass", "cup", "fork",
                "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
                "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
                "couch", "potted plant", "bed", "dining table", "toilet", "tv",
                "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave",
                "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase",
                "scissors", "teddy bear", "hair drier", "toothbrush"
            ]
        return []
    
    def visualize(self, image: np.ndarray, results: List) -> np.ndarray:
        output = image.copy()
        overlay = image.copy()

        # For class-agnostic models (1 class), sort by area descending so large
        # segments are drawn first and smaller ones overlay on top — cleaner look.
        draw_order = list(range(len(results)))
        if len(self.labels) == 1 and len(results) > 1:
            draw_order.sort(key=lambda i: -((
                results[i].box[2] - results[i].box[0]) * (
                results[i].box[3] - results[i].box[1])))

        for i in draw_order:
            r = results[i]
            color = INSTANCE_COLORS[i % len(INSTANCE_COLORS)]
            x1, y1, x2, y2 = [int(v) for v in r.box]
            
            # Draw mask overlay
            if hasattr(r, 'mask') and r.mask is not None and r.mask.size > 0:
                mask = r.mask
                if mask.shape[:2] == image.shape[:2]:
                    mask_bool = mask > 0
                    overlay[mask_bool] = color
            
            # Draw bounding box and label (skip for mask-only mode)
            if self.show_boxes:
                cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
                
                # Label
                label = f"{r.class_id}"
                if self.labels and r.class_id < len(self.labels):
                    label = self.labels[r.class_id]
                # For class-agnostic models (1 class), show instance index instead
                if len(self.labels) == 1:
                    text = f"{label} {i+1} {r.confidence:.2f}"
                else:
                    text = f"{label} {r.confidence:.2f}"
                
                (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(output, (x1, y1 - th - 6), (x1 + tw, y1), color, -1)
                cv2.putText(output, text, (x1, y1 - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Blend mask overlay
        output = cv2.addWeighted(overlay, 0.4, output, 0.6, 0)
        
        return output
