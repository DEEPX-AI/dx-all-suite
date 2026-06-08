"""
Restoration / Depth Visualizers

Visualizers for image restoration (denoising) and depth estimation tasks.
"""

import cv2
import numpy as np

from ..base import IVisualizer


class RestorationVisualizer(IVisualizer):
    """
    Visualizer for image restoration (denoising) results.
    
    Shows side-by-side: input (noisy) | output (denoised).
    For grayscale models, converts to BGR for display.
    """

    def visualize(self, image: np.ndarray, results: list) -> np.ndarray:
        """
        Args:
            image: original input image (BGR)
            results: List containing RestorationResult with .output_image field  (HW or HWC)
        """
        result = results[0]
        denoised = result.output_image

        # Handle grayscale output
        if len(denoised.shape) == 2:
            denoised = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)

        h, w = image.shape[:2]
        denoised_resized = cv2.resize(denoised, (w, h))

        # Side-by-side: input | output
        canvas = np.hstack([image, denoised_resized])
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(canvas, "Input", (10, 30), font, 1.0, (0, 255, 0), 2)
        cv2.putText(canvas, "Denoised", (w + 10, 30), font, 1.0, (0, 255, 0), 2)
        return canvas


class DepthVisualizer(IVisualizer):
    """
    Visualizer for depth estimation results.
    
    Shows side-by-side: input | depth colormap.
    """

    def visualize(self, image: np.ndarray, results: list) -> np.ndarray:
        """
        Args:
            image: original input image (BGR)
            results: List containing DepthResult with .depth_colormap field
        """
        result = results[0]
        depth_color = result.depth_colormap

        # Resize to match original and return depth result directly
        # (GUI CMP slider handles before/after comparison)
        h, w = image.shape[:2]
        return cv2.resize(depth_color, (w, h))
