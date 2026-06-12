# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
SquatGameFactory — IFactory wiring for the yolo26n-pose squat mini-game.

Reuses the framework's pose components unchanged (``LetterboxPreprocessor`` +
``YOLOv8PosePostprocessor`` — exactly what the working ``yolo26n_pose`` example
uses) and swaps in the stateful ``SquatGameVisualizer`` so the game logic runs
inside the standard SyncRunner pipeline.
"""

from common.base import IPoseFactory
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor

from .squat_game_visualizer import SquatGameVisualizer


class SquatGameFactory(IPoseFactory):
    """Factory creating the squat-game pose components."""

    def __init__(self, config: dict = None):
        # ``config`` passed at construction carries CLI overrides (e.g.
        # --target-reps). These must win over config.json values that arrive
        # later via load_config(), so remember them separately.
        self.config = dict(config or {})
        self._overrides = dict(config or {})

    def load_config(self, config: dict) -> None:
        # Merge config.json (with score_threshold->conf_threshold alias) ...
        super().load_config(config)
        # ... then re-apply CLI overrides so they take precedence.
        self.config.update(self._overrides)

    def create_preprocessor(self, input_width: int, input_height: int):
        return LetterboxPreprocessor(input_width, input_height)

    def create_postprocessor(self, input_width: int, input_height: int):
        return YOLOv8PosePostprocessor(input_width, input_height, self.config)

    def create_visualizer(self):
        return SquatGameVisualizer(self.config)

    def get_model_name(self) -> str:
        return "yolo26n_pose"

    def get_task_type(self) -> str:
        return "pose_estimation"

    def get_num_keypoints(self) -> int:
        """YOLO-pose uses COCO 17-point body keypoints."""
        return 17
