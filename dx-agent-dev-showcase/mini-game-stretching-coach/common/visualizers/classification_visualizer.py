"""
Classification Visualizer

Displays classification results as text overlay.
"""

import numpy as np
import cv2
from typing import List

from ..base import IVisualizer, ClassificationResult
from ..utility import get_labels


class ClassificationVisualizer(IVisualizer):
    """
    Visualizer for classification results.
    
    Displays class name and confidence as text overlay.
    """
    
    def __init__(self, label_set: str = 'imagenet1000', custom_labels: List[str] = None):
        """
        Initialize classification visualizer.
        
        Args:
            label_set: Predefined label set name ('imagenet1000', etc.)
            custom_labels: Custom label list (overrides label_set)
        """
        if custom_labels is not None:
            self.labels = custom_labels
        else:
            self.labels = get_labels(label_set)
    
    def visualize(self, image: np.ndarray, results: List[ClassificationResult]) -> np.ndarray:
        """
        Draw classification results on image.
        
        Args:
            image: Original image (BGR format)
            results: List of ClassificationResult objects (top-k)
            
        Returns:
            Image with classification text overlay
        """
        output = image.copy()
        
        if not results:
            return output
        
        # Draw semi-transparent background for text
        h, w = output.shape[:2]
        overlay = output.copy()
        cv2.rectangle(overlay, (10, 10), (min(w - 10, 400), 30 + len(results) * 25), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, output, 0.5, 0, output)
        
        # Draw results
        y_offset = 30
        for i, res in enumerate(results):
            class_id = res.class_id
            conf = res.confidence
            
            # Get label
            if class_id < len(self.labels):
                label = self.labels[class_id]
            else:
                label = f"class_{class_id}"
            
            # Format text
            if conf is not None:
                text = f"#{i+1}: {label} ({conf*100:.1f}%)"
            else:
                text = f"#{i+1}: {label}"
            
            # Draw text
            cv2.putText(
                output,
                text,
                (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )
            y_offset += 25
        
        return output
