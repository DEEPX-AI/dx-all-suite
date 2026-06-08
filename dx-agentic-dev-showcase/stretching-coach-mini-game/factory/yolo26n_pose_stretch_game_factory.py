#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""StretchGameFactory — IPoseFactory wiring for the stretch mini-game.

Reuses the standard letterbox preprocessor and YOLOv8/26-pose postprocessor;
only the visualizer is swapped for the stateful StretchGameVisualizer game
engine. The session dir is on sys.path (set by the entry script), so the
sibling ``stretch_game_engine`` module imports directly.
"""

from common.base import IPoseFactory
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor

from stretch_game_engine import StretchGameVisualizer


class StretchGameFactory(IPoseFactory):
    """Factory for the yolo26n-pose stretch game."""

    def __init__(self, config: dict = None, start_stage: int = 0,
                 templates_path: str = None):
        self.config = config or {}
        self._start_stage = start_stage
        self._templates_path = templates_path

    def create_preprocessor(self, input_width: int, input_height: int):
        return LetterboxPreprocessor(input_width, input_height)

    def create_postprocessor(self, input_width: int, input_height: int):
        return YOLOv8PosePostprocessor(input_width, input_height, self.config)

    def create_visualizer(self):
        return StretchGameVisualizer(
            self.config, start_stage=self._start_stage,
            templates_path=self._templates_path)

    def get_model_name(self) -> str:
        return "yolo26n_pose"

    def get_task_type(self) -> str:
        return "pose_estimation"

    def get_num_keypoints(self) -> int:
        return 17
