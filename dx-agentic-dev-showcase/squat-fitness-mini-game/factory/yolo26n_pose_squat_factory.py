#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Factory for the YOLO26n-Pose squat-counting fitness game.

Reuses the framework's LetterboxPreprocessor + YOLOv8PosePostprocessor unchanged
(yolo26n-pose is a standard YOLOv8-style pose head) and supplies a custom
SquatGameVisualizer that hosts the rep-counting state machine + arcade HUD.

The game tuning lives under the ``game`` key of config.json; SyncRunner calls
``load_config`` (which merges into ``self.config``) BEFORE ``create_visualizer``,
so the visualizer always receives the calibrated thresholds.
"""

from common.base import IPoseFactory
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor

from squat_game_visualizer import SquatGameVisualizer


class Yolo26nPoseSquatFactory(IPoseFactory):
    """Creates matching components for the yolo26n-pose squat game."""

    def __init__(self, config: dict = None):
        self.config = config or {}

    def create_preprocessor(self, input_width: int, input_height: int):
        return LetterboxPreprocessor(input_width, input_height)

    def create_postprocessor(self, input_width: int, input_height: int):
        return YOLOv8PosePostprocessor(input_width, input_height, self.config)

    def create_visualizer(self):
        # `game` block holds target_reps / score_per_rep / calibrated thresholds.
        return SquatGameVisualizer(self.config.get("game", {}))

    def get_model_name(self) -> str:
        return "yolo26n_pose"

    def get_task_type(self) -> str:
        return "pose_estimation"

    def get_num_keypoints(self) -> int:
        """YOLOv8/26-Pose uses COCO 17-point body keypoints."""
        return 17
