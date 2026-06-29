"""
Face Detection Visualizer

Draws bounding boxes and facial keypoints for face detection results.
Used by SCRFD, YOLOv5Face, etc.
"""

import numpy as np
import cv2
from typing import List, Union

from ..base import IVisualizer
from ..processors.face_postprocessor import FaceResult
from ..utility.skeleton import FACE_KPT_COLOR, FACE_KEYPOINT_NAMES


class FaceVisualizer(IVisualizer):
    """
    Visualizer for face detection results with keypoints.
    
    Draws bounding boxes and 5 facial landmarks (eyes, nose, mouth corners).
    """
    
    def __init__(self, draw_keypoints: bool = True, keypoint_radius: int = 3):
        """
        Initialize face visualizer.
        
        Args:
            draw_keypoints: Whether to draw facial keypoints
            keypoint_radius: Radius for keypoint circles
        """
        self.draw_keypoints = draw_keypoints
        self.keypoint_radius = keypoint_radius
        self.box_color = (0, 255, 0)  # Green for face boxes
    
    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _draw_box_label(self, output: np.ndarray, x1: int, y1: int, x2: int, y2: int, score: float) -> None:
        """Draw bounding box and confidence label."""
        cv2.rectangle(output, (x1, y1), (x2, y2), self.box_color, 2)

        label = f"face: {score:.2f}"
        (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        label_y = y1 - 10 if y1 - 10 > label_height else y1 + 10

        cv2.rectangle(output, (x1, label_y - label_height),
                      (x1 + label_width, label_y + label_height), self.box_color, cv2.FILLED)
        cv2.putText(output, label, (x1, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    @staticmethod
    def _parse_kp_coords(keypoints):
        """Normalise keypoints to a list of (x, y) int tuples regardless of input format."""
        if hasattr(keypoints[0], 'x'):
            return [(int(round(float(kp.x))), int(round(float(kp.y)))) for kp in keypoints]
        return [(int(round(float(keypoints[k * 2]))), int(round(float(keypoints[k * 2 + 1]))))
                for k in range(len(keypoints) // 2)]

    def _draw_keypoints(self, output: np.ndarray, keypoints) -> None:
        """Draw facial keypoints on the output image."""
        h, w = output.shape[:2]
        for i, (kp_x, kp_y) in enumerate(self._parse_kp_coords(keypoints)):
            if abs(kp_x) > w * 2 or abs(kp_y) > h * 2:
                continue
            color = tuple(int(c) for c in FACE_KPT_COLOR[i]) if i < len(FACE_KPT_COLOR) else (0, 255, 255)
            cv2.circle(output, (kp_x, kp_y), int(self.keypoint_radius), color, -1)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def visualize(self, image: np.ndarray, results: List[FaceResult]) -> np.ndarray:
        """
        Draw face detection results on image.

        Args:
            image: Original image (BGR format)
            results: List of FaceResult objects

        Returns:
            Image with drawn detections
        """
        output = image.copy()

        for face in results:
            x1, y1, x2, y2 = [int(v) for v in face.box]
            self._draw_box_label(output, x1, y1, x2, y2, face.confidence)
            if self.draw_keypoints and face.keypoints:
                self._draw_keypoints(output, face.keypoints)

        return output
    
    def visualize_with_labels(
        self, 
        image: np.ndarray, 
        results: List[FaceResult],
        show_keypoint_names: bool = False
    ) -> np.ndarray:
        """
        Draw face detection results with optional keypoint labels.
        
        Args:
            image: Original image (BGR format)
            results: List of FaceResult objects
            show_keypoint_names: Whether to show keypoint names
            
        Returns:
            Image with drawn detections and labels
        """
        output = self.visualize(image, results)
        
        if show_keypoint_names:
            for face in results:
                if face.keypoints:
                    for i, kp in enumerate(face.keypoints):
                        if i < len(FACE_KEYPOINT_NAMES):
                            name = FACE_KEYPOINT_NAMES[i]
                            cv2.putText(
                                output,
                                name,
                                (int(kp.x) + 5, int(kp.y) - 5),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.3,
                                (255, 255, 255),
                                1,
                                cv2.LINE_AA
                            )
        
        return output
