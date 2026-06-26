"""
OBB (Oriented Bounding Box) Visualizer

Draws rotated bounding boxes and labels for OBB detection results.
Used by YOLOv26-OBB and similar models for aerial/satellite image detection.
"""

import numpy as np
import cv2
from typing import List

from ..base import IVisualizer, OBBResult


class OBBVisualizer(IVisualizer):
    """
    Visualizer for OBB (Oriented Bounding Box) detection results.
    
    Draws rotated bounding boxes with class labels and confidence scores.
    Computes 4 corner points from center-based representation (cx, cy, w, h, angle).
    """
    
    def __init__(self, custom_labels: List[str] = None):
        """
        Initialize OBB visualizer.
        
        Args:
            custom_labels: Custom label list (defaults to DOTA v1 labels)
        """
        if custom_labels is not None:
            self.labels = custom_labels
        else:
            from ..processors.obb_postprocessor import DOTAV1_LABELS
            self.labels = DOTAV1_LABELS
        
        # Generate random colors for each class
        self.color_palette = np.random.uniform(0, 255, size=(len(self.labels), 3))
    
    def visualize(self, image: np.ndarray, results: List[OBBResult]) -> np.ndarray:
        """
        Draw OBB detection results on image.
        
        Args:
            image: Original image (BGR format)
            results: List of OBBResult objects
            
        Returns:
            Image with drawn rotated bounding boxes
        """
        output = image.copy()
        
        for obb in results:
            # Compute 4 corner points from center-based representation
            corners = self._xywhr_to_corners(obb.cx, obb.cy, obb.width, obb.height, obb.angle)
            poly = corners.astype(np.int32)
            
            # Get color
            color = self.color_palette[obb.class_id % len(self.color_palette)]
            
            # Draw rotated bounding box
            cv2.polylines(output, [poly], True, color, 2)
            
            # Prepare label text
            label_text = obb.class_name if obb.class_name else f"class_{obb.class_id}"
            label = f"{label_text}: {obb.confidence:.2f}"
            
            # Get text size
            (label_width, label_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            
            # Position label at top-left corner of rotated box
            box_x = int(np.min(poly[:, 0]))
            box_y = int(np.min(poly[:, 1]))
            
            label_x = box_x
            label_y = box_y - 10 if box_y - 10 > label_height else box_y + 10
            
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
    
    @staticmethod
    def _xywhr_to_corners(cx: float, cy: float, w: float, h: float, 
                           angle: float) -> np.ndarray:
        """
        Convert center-based OBB representation to 4 corner points.
        
        Args:
            cx, cy: Center coordinates
            w, h: Width and height (before rotation)
            angle: Rotation angle in radians
            
        Returns:
            Array of shape (4, 2) with corner coordinates
        """
        cos_v = np.cos(angle)
        sin_v = np.sin(angle)
        
        vec1 = np.array([w / 2 * cos_v, w / 2 * sin_v])
        vec2 = np.array([-h / 2 * sin_v, h / 2 * cos_v])
        
        ctr = np.array([cx, cy])
        
        pt1 = ctr + vec1 + vec2
        pt2 = ctr + vec1 - vec2
        pt3 = ctr - vec1 - vec2
        pt4 = ctr - vec1 + vec2
        
        return np.array([pt1, pt2, pt3, pt4], dtype=np.float32)
