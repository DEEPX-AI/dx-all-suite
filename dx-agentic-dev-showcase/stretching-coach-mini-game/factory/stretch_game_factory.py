#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
StretchGameFactory — IFactory for the arcade stretching mini-game.

Wires the stock yolo26n-pose components (LetterboxPreprocessor +
YOLOv8PosePostprocessor) together with the custom StretchGameVisualizer, which
carries the game state machine and arcade UI. Used by SyncRunner exactly like
any other pose example — the game is realised purely through the visualizer, so
the IFactory + SyncRunner contract is unchanged.
"""

import json
import os

from common.base import IPoseFactory
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor

from game_visualizer import StretchGameVisualizer


def _load_coach_poses():
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(here, "coach_poses.json")
    with open(path) as f:
        return json.load(f)


class StretchGameFactory(IPoseFactory):
    """Factory for the yolo26n-pose stretching game."""

    def __init__(self, config: dict = None):
        self.config = config or {}

    def create_preprocessor(self, input_width: int, input_height: int):
        return LetterboxPreprocessor(input_width, input_height)

    def create_postprocessor(self, input_width: int, input_height: int):
        return YOLOv8PosePostprocessor(input_width, input_height, self.config)

    def create_visualizer(self):
        return StretchGameVisualizer(self.config, _load_coach_poses())

    def get_model_name(self) -> str:
        return "yolo26n_pose"

    def get_task_type(self) -> str:
        return "pose_estimation"

    def get_num_keypoints(self) -> int:
        return 17
