"""
Pose Estimation Visualizer

Draws bounding boxes, skeleton connections, and keypoints for pose estimation results.
Used by YOLOv5-pose, YOLOv8-pose, etc.
"""

import numpy as np
import cv2
from typing import List

from ..base import IVisualizer, PoseResult
from ..utility.skeleton import SKELETON, POSE_LIMB_COLOR, POSE_KPT_COLOR, KEYPOINT_NAMES, CENTERPOSE_EDGES


class PoseVisualizer(IVisualizer):
    """
    Visualizer for pose estimation results.
    
    Draws bounding boxes, skeleton connections, and 17 body keypoints.
    """
    
    def __init__(
        self, 
        draw_skeleton: bool = True, 
        draw_keypoints: bool = True,
        draw_box: bool = True,
        keypoint_radius: int = 5,
        skeleton_thickness: int = 2,
        keypoint_confidence_threshold: float = 0.3
    ):
        """
        Initialize pose visualizer.
        
        Args:
            draw_skeleton: Whether to draw skeleton connections
            draw_keypoints: Whether to draw keypoints
            draw_box: Whether to draw bounding box
            keypoint_radius: Radius for keypoint circles
            skeleton_thickness: Thickness for skeleton lines
            keypoint_confidence_threshold: Minimum confidence to draw keypoint
        """
        self.draw_skeleton = draw_skeleton
        self.draw_keypoints = draw_keypoints
        self.draw_box = draw_box
        self.keypoint_radius = keypoint_radius
        self.skeleton_thickness = skeleton_thickness
        self.kpt_conf_threshold = keypoint_confidence_threshold
        self.box_color = (0, 255, 0)  # Green for person boxes
    
    def _draw_box_label(self, output: np.ndarray, pose) -> None:
        """Draw bounding box and confidence label for a single pose."""
        if not (self.draw_box and pose.box):
            return
        x1, y1, x2, y2 = [int(v) for v in pose.box]
        cv2.rectangle(output, (x1, y1), (x2, y2), self.box_color, 2)

        label = f"person: {pose.confidence:.2f}"
        (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        label_y = y1 - 10 if y1 - 10 > label_height else y1 + 10

        cv2.rectangle(output, (x1, label_y - label_height),
                      (x1 + label_width, label_y + label_height), self.box_color, cv2.FILLED)
        cv2.putText(output, label, (x1, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    def visualize(self, image: np.ndarray, results: List[PoseResult]) -> np.ndarray:
        """
        Draw pose estimation results on image.
        
        Args:
            image: Original image (BGR format)
            results: List of PoseResult objects
            
        Returns:
            Image with drawn poses
        """
        output = image.copy()
        
        for pose in results:
            self._draw_box_label(output, pose)
            if self.draw_skeleton and pose.keypoints:
                self._draw_skeleton(output, pose.keypoints)
            if self.draw_keypoints and pose.keypoints:
                self._draw_keypoints(output, pose.keypoints)
        
        return output
    
    def _draw_skeleton(self, image: np.ndarray, keypoints: List) -> None:
        """Draw skeleton connections between keypoints.
        
        Adapts to different keypoint formats:
        - 17 keypoints: COCO body skeleton
        - 8 keypoints: CenterPose 3D bounding box cuboid
        - Other counts: skip skeleton (keypoints still drawn separately)
        """
        num_kpts = len(keypoints)

        if num_kpts == 17:
            edges = SKELETON
            colors = POSE_LIMB_COLOR
        elif num_kpts == 8:
            edges = CENTERPOSE_EDGES
            colors = None  # uniform color for cuboid
        else:
            return  # no known skeleton for this keypoint count

        for i, (start_idx, end_idx) in enumerate(edges):
            if start_idx >= num_kpts or end_idx >= num_kpts:
                continue

            kp_start = keypoints[start_idx]
            kp_end = keypoints[end_idx]

            if kp_start.confidence < self.kpt_conf_threshold:
                continue
            if kp_end.confidence < self.kpt_conf_threshold:
                continue

            start_point = (int(kp_start.x), int(kp_start.y))
            end_point = (int(kp_end.x), int(kp_end.y))

            if colors and i < len(colors):
                color = colors[i]
            else:
                color = (0, 255, 255)  # cyan for CenterPose cuboid

            cv2.line(image, start_point, end_point, color, self.skeleton_thickness)
    
    def _draw_keypoints(self, image: np.ndarray, keypoints: List) -> None:
        """Draw keypoint circles."""
        for i, kp in enumerate(keypoints):
            if kp.confidence < self.kpt_conf_threshold:
                continue
            
            # Get color
            color = POSE_KPT_COLOR[i] if i < len(POSE_KPT_COLOR) else (255, 255, 255)
            
            center = (int(kp.x), int(kp.y))
            cv2.circle(image, center, self.keypoint_radius, color, -1)
            
            # Draw outline
            cv2.circle(image, center, self.keypoint_radius, (255, 255, 255), 1)
    
    def _draw_kpt_label(self, output: np.ndarray, kp, idx: int,
                         show_keypoint_names: bool, show_confidence: bool) -> None:
        """Overlay optional name/confidence text near a single keypoint."""
        if kp.confidence < self.kpt_conf_threshold:
            return
        text_parts = []
        if show_keypoint_names and idx < len(KEYPOINT_NAMES):
            text_parts.append(KEYPOINT_NAMES[idx])
        if show_confidence:
            text_parts.append(f"{kp.confidence:.2f}")
        if not text_parts:
            return
        cv2.putText(output, " ".join(text_parts),
                    (int(kp.x) + 8, int(kp.y) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1, cv2.LINE_AA)

    def visualize_with_labels(
        self,
        image: np.ndarray,
        results: List[PoseResult],
        show_keypoint_names: bool = False,
        show_confidence: bool = False
    ) -> np.ndarray:
        """
        Draw pose results with optional keypoint labels.

        Args:
            image: Original image (BGR format)
            results: List of PoseResult objects
            show_keypoint_names: Whether to show keypoint names
            show_confidence: Whether to show keypoint confidence

        Returns:
            Image with drawn poses and labels
        """
        output = self.visualize(image, results)
        for pose in results:
            if pose.keypoints:
                for i, kp in enumerate(pose.keypoints):
                    self._draw_kpt_label(output, kp, i, show_keypoint_names, show_confidence)
        return output
