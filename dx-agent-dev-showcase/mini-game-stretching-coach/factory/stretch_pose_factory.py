"""
StretchPoseFactory — IPoseFactory for the yolo26n-pose Stretch Coach mini-game.

Reuses the framework's LetterboxPreprocessor + YOLOv8PosePostprocessor (the
yolo26n-pose registry postprocessor 'yolov26pose' uses the YOLOv8/26 post-NMS
head) and supplies a CUSTOM visualizer that turns per-frame pose keypoints into
the arcade stretching game (state machine + animated humanoid coach + overlay).

This stays fully inside the IFactory + SyncRunner contract: SyncRunner calls
visualizer.visualize(frame, results) once per frame and, with --save, writes the
returned (annotated) frames to an output video.
"""

import numpy as np

from common.base import IPoseFactory, IVisualizer
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor

from game import StretchGame


class StretchGameVisualizer(IVisualizer):
    """IVisualizer that runs the stretch mini-game and renders its overlay."""

    def __init__(self, config: dict = None, model_name: str = "yolo26n-pose"):
        self.game = StretchGame(config or {}, model_name=model_name)

    def visualize(self, frame: np.ndarray, results) -> np.ndarray:
        out = frame.copy()
        self.game.update(results)
        return self.game.draw_overlay(out, results)


class StretchPoseFactory(IPoseFactory):
    """Factory wiring yolo26n-pose components to the Stretch Coach game."""

    def __init__(self, config: dict = None):
        # Defaults mirror config.json; load_config() overrides them at runtime.
        self.config = {
            "score_threshold": 0.4,
            "nms_threshold": 0.45,
            "num_keypoints": 17,
        }
        if config:
            self.config.update(config)
        self._visualizer = None

    def create_preprocessor(self, input_width: int, input_height: int):
        return LetterboxPreprocessor(input_width, input_height)

    def create_postprocessor(self, input_width: int, input_height: int):
        return YOLOv8PosePostprocessor(input_width, input_height, self.config)

    def create_visualizer(self) -> IVisualizer:
        self._visualizer = StretchGameVisualizer(self.config, model_name=self.get_model_name())
        return self._visualizer

    def get_model_name(self) -> str:
        return "yolo26n_pose"

    def get_task_type(self) -> str:
        return "pose_estimation"

    def get_num_keypoints(self) -> int:
        return 17
