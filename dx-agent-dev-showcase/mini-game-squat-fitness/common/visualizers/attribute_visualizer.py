"""
Attribute Recognition Visualizer

Displays person/face attribute predictions as a text list overlay.
"""

import numpy as np
import cv2
from typing import List

from ..base import IVisualizer, ClassificationResult


class AttributeVisualizer(IVisualizer):
    """
    Visualizer for attribute recognition results.

    Displays activated attributes as a text list on the left side of the image.
    """

    def visualize(self, image: np.ndarray,
                  results: List[ClassificationResult]) -> np.ndarray:
        output = image.copy()
        if not results:
            return output

        h, w = output.shape[:2]
        line_h = 22
        pad = 8
        box_w = min(w - 20, 320)
        box_h = pad * 2 + (len(results) + 1) * line_h

        # Semi-transparent background
        overlay = output.copy()
        cv2.rectangle(overlay, (10, 10), (10 + box_w, 10 + box_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.55, output, 0.45, 0, output)

        # Title
        y = 10 + pad + line_h
        cv2.putText(output, "[Person Attributes]", (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA)
        y += line_h

        # Attribute list
        for res in results:
            text = f"{res.class_name}: {res.confidence * 100:.0f}%"
            color = (0, 255, 0) if res.confidence > 0.7 else (0, 200, 200)
            cv2.putText(output, text, (25, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, color, 1, cv2.LINE_AA)
            y += line_h

        return output
