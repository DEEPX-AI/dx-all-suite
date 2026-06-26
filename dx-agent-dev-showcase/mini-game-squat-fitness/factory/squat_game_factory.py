# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
SquatGameFactory — yolo26n-pose Squat Fitness Mini-Game (IFactory pattern).

Implements the IPoseFactory 5-method contract. The squat-game behavior lives in
the custom visualizer (SquatGameVisualizer); preprocessor/postprocessor are the
standard YOLO-pose components, matching the verified yolo26n_pose example.
"""

from common.base import IPoseFactory
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor

from .squat_game_visualizer import SquatGameVisualizer


class SquatGameFactory(IPoseFactory):
    """Factory for the yolo26n-pose squat-counting mini-game."""

    def __init__(self, config: dict = None):
        self.config = config or {}

    def _game_cfg(self) -> dict:
        return self.config.get("squat_game", {}) if isinstance(self.config, dict) else {}

    def create_preprocessor(self, input_width: int, input_height: int):
        return LetterboxPreprocessor(input_width, input_height)

    def create_postprocessor(self, input_width: int, input_height: int):
        return YOLOv8PosePostprocessor(input_width, input_height, self.config)

    def create_visualizer(self):
        g = self._game_cfg()
        return SquatGameVisualizer(
            stand_angle=float(g.get("stand_angle", 160.0)),
            squat_angle=float(g.get("squat_angle", 100.0)),
            keypoint_confidence=float(g.get("keypoint_confidence", 0.3)),
        )

    def get_model_name(self) -> str:
        return "yolo26n_pose"

    def get_task_type(self) -> str:
        return "pose_estimation"

    def get_num_keypoints(self) -> int:
        """COCO 17-point body keypoints."""
        return 17

    # load_config() is inherited from _FactoryConfigMixin (merges config.json into
    # self.config with the score_threshold->conf_threshold alias). SyncRunner calls
    # it BEFORE create_visualizer/create_postprocessor, so squat_game thresholds and
    # the postprocessor conf alias are both available at component-creation time.
