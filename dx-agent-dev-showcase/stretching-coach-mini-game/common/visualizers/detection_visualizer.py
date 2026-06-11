"""
Detection Visualizer

Draws bounding boxes and labels for object detection results.
Used by YOLO family, SCRFD, etc.
"""

import numpy as np
import cv2
from typing import List

from ..base import IVisualizer, DetectionResult
from ..utility import get_labels


class DetectionVisualizer(IVisualizer):
    """
    Visualizer for object detection results.
    
    Draws bounding boxes with class labels and confidence scores.
    """
    
    def __init__(self, label_set: str = 'coco80', custom_labels: List[str] = None):
        """
        Initialize detection visualizer.
        
        Args:
            label_set: Predefined label set name ('coco80', 'coco', 'voc', etc.)
            custom_labels: Custom label list (overrides label_set)
        """
        if custom_labels is not None:
            self.labels = custom_labels
        else:
            self.labels = get_labels(label_set)
        
        # Generate random colors for each class
        self.color_palette = np.random.uniform(0, 255, size=(len(self.labels), 3))
    
    def visualize(self, image: np.ndarray, results: List[DetectionResult]) -> np.ndarray:
        """
        Draw detection results on image.
        
        Args:
            image: Original image (BGR format)
            results: List of DetectionResult objects
            
        Returns:
            Image with drawn detections
        """
        output = image.copy()
        
        for det in results:
            x1, y1, x2, y2 = [int(v) for v in det.box]
            class_id = det.class_id
            score = det.confidence
            
            # Get color
            color = self.color_palette[class_id % len(self.color_palette)]
            
            # Draw bounding box
            cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
            
            # Prepare label text
            label_text = self.labels[class_id] if class_id < len(self.labels) else f"class_{class_id}"
            label = f"{label_text}: {score:.2f}"
            
            # Get text size
            (label_width, label_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            
            # Position label
            label_x = x1
            label_y = y1 - 10 if y1 - 10 > label_height else y1 + 10
            
            # Draw label background
            cv2.rectangle(
                output,
                (label_x, label_y - label_height),
                (label_x + label_width, label_y + label_height),
                color,
                cv2.FILLED
            )
            
            # Draw label text
            cv2.putText(
                output,
                label,
                (label_x, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA
            )
        
        return output
