#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""Factory for the yolo26n-pose stretch mini-game.

Reuses the framework's LetterboxPreprocessor + YOLOv8PosePostprocessor and pairs
them with the stateful StretchGameVisualizer (which holds the game across frames).
"""

import json
from pathlib import Path

from common.base import IPoseFactory
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor

from stretch_game_visualizer import StretchGameVisualizer


def _load_templates() -> dict:
    """Load the coach skeletons baked from the sample clips by the calibrator."""
    path = Path(__file__).resolve().parent.parent / "pose_templates.json"
    if path.is_file():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


class StretchGameFactory(IPoseFactory):
    """Creates the components for the arcade stretch game."""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self._templates = _load_templates()

    def create_preprocessor(self, input_width: int, input_height: int):
        return LetterboxPreprocessor(input_width, input_height)

    def create_postprocessor(self, input_width: int, input_height: int):
        return YOLOv8PosePostprocessor(input_width, input_height, self.config)

    def create_visualizer(self):
        return StretchGameVisualizer(self.config, self._templates)

    def get_model_name(self) -> str:
        return "yolo26n_pose"

    def get_task_type(self) -> str:
        return "pose_estimation"

    def get_num_keypoints(self) -> int:
        return 17
