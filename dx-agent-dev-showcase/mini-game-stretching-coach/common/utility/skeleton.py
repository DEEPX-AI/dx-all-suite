"""
Skeleton Constants for Pose Estimation

COCO format skeleton connections and colors for visualization.
Used by PoseVisualizer and related pose estimation models.
"""

from typing import List, Tuple

# Human skeleton connections (COCO 17-keypoint format)
# Each pair represents connected keypoint indices
SKELETON: List[List[int]] = [
    [15, 13],  # left_ankle - left_knee
    [13, 11],  # left_knee - left_hip
    [16, 14],  # right_ankle - right_knee
    [14, 12],  # right_knee - right_hip
    [11, 12],  # left_hip - right_hip
    [5, 11],   # left_shoulder - left_hip
    [6, 12],   # right_shoulder - right_hip
    [5, 6],    # left_shoulder - right_shoulder
    [5, 7],    # left_shoulder - left_elbow
    [6, 8],    # right_shoulder - right_elbow
    [7, 9],    # left_elbow - left_wrist
    [8, 10],   # right_elbow - right_wrist
    [1, 2],    # left_eye - right_eye
    [0, 1],    # nose - left_eye
    [0, 2],    # nose - right_eye
    [1, 3],    # left_eye - left_ear
    [2, 4],    # right_eye - right_ear
    [3, 5],    # left_ear - left_shoulder
    [4, 6],    # right_ear - right_shoulder
]

# Colors for skeleton limbs (BGR format)
POSE_LIMB_COLOR: List[Tuple[int, int, int]] = [
    (51, 153, 255),   # 0: left_ankle - left_knee
    (51, 153, 255),   # 1: left_knee - left_hip
    (51, 153, 255),   # 2: right_ankle - right_knee
    (51, 153, 255),   # 3: right_knee - right_hip
    (255, 51, 255),   # 4: left_hip - right_hip
    (255, 51, 255),   # 5: left_shoulder - left_hip
    (255, 51, 255),   # 6: right_shoulder - right_hip
    (255, 128, 0),    # 7: left_shoulder - right_shoulder
    (255, 128, 0),    # 8: left_shoulder - left_elbow
    (255, 128, 0),    # 9: right_shoulder - right_elbow
    (255, 128, 0),    # 10: left_elbow - left_wrist
    (255, 128, 0),    # 11: right_elbow - right_wrist
    (0, 255, 0),      # 12: left_eye - right_eye
    (0, 255, 0),      # 13: nose - left_eye
    (0, 255, 0),      # 14: nose - right_eye
    (0, 255, 0),      # 15: left_eye - left_ear
    (0, 255, 0),      # 16: right_eye - right_ear
    (0, 255, 0),      # 17: left_ear - left_shoulder
    (0, 255, 0),      # 18: right_ear - right_shoulder
]

# Colors for keypoints (BGR format)
# 0-4: head (green), 5-10: arms (orange), 11-16: legs (blue)
POSE_KPT_COLOR: List[Tuple[int, int, int]] = [
    (0, 255, 0),      # 0: nose
    (0, 255, 0),      # 1: left_eye
    (0, 255, 0),      # 2: right_eye
    (0, 255, 0),      # 3: left_ear
    (0, 255, 0),      # 4: right_ear
    (255, 128, 0),    # 5: left_shoulder
    (255, 128, 0),    # 6: right_shoulder
    (255, 128, 0),    # 7: left_elbow
    (255, 128, 0),    # 8: right_elbow
    (255, 128, 0),    # 9: left_wrist
    (255, 128, 0),    # 10: right_wrist
    (51, 153, 255),   # 11: left_hip
    (51, 153, 255),   # 12: right_hip
    (51, 153, 255),   # 13: left_knee
    (51, 153, 255),   # 14: right_knee
    (51, 153, 255),   # 15: left_ankle
    (51, 153, 255),   # 16: right_ankle
]

# Keypoint names (COCO format)
KEYPOINT_NAMES: List[str] = [
    "nose",
    "left_eye",
    "right_eye",
    "left_ear",
    "right_ear",
    "left_shoulder",
    "right_shoulder",
    "left_elbow",
    "right_elbow",
    "left_wrist",
    "right_wrist",
    "left_hip",
    "right_hip",
    "left_knee",
    "right_knee",
    "left_ankle",
    "right_ankle",
]

# CenterPose 3D bounding box edges (8-keypoint cuboid)
# Vertex ordering: [front-tl, front-tr, front-br, front-bl, back-tl, back-tr, back-br, back-bl]
CENTERPOSE_EDGES: List[List[int]] = [
    [0, 1], [1, 2], [2, 3], [3, 0],  # front face
    [4, 5], [5, 6], [6, 7], [7, 4],  # back face
    [0, 4], [1, 5], [2, 6], [3, 7],  # connecting edges
]

# Face keypoint names (5-point)
FACE_KEYPOINT_NAMES: List[str] = [
    "left_eye",
    "right_eye",
    "nose",
    "left_mouth",
    "right_mouth",
]

# Face keypoint colors (BGR)
FACE_KPT_COLOR: List[Tuple[int, int, int]] = [
    (0, 255, 0),      # left_eye
    (0, 255, 0),      # right_eye
    (255, 128, 0),    # nose
    (255, 0, 128),    # left_mouth
    (255, 0, 128),    # right_mouth
]
