"""StretchGame Factory — DX-APP IFactory for the yolo26n-pose stretching game.

Wires the verified pose preprocessor/postprocessor with the game visualizer:
- LetterboxPreprocessor      : YOLO letterbox resize (auto input size from model)
- YOLOv8PosePostprocessor    : YOLO26-pose post-NMS [1,300,57] → PoseResult/Keypoint
- StretchCoachVisualizer     : per-frame game state machine + arcade UI + coach

All inference/engine handling stays inside SyncRunner; this factory only
constructs components, per the IFactory contract.
"""

from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor

from factory.base import IPoseFactory
from stretch_coach import StretchCoachVisualizer


class StretchGameFactory(IPoseFactory):
    """Factory for the stretch-coach pose game (model: yolo26n_pose)."""

    def __init__(self, config: dict = None):
        self.config = config or {}

    def create_preprocessor(self, input_width: int, input_height: int):
        return LetterboxPreprocessor(input_width, input_height)

    def create_postprocessor(self, input_width: int, input_height: int):
        return YOLOv8PosePostprocessor(input_width, input_height, self.config)

    def create_visualizer(self):
        return StretchCoachVisualizer(self.config)

    def get_model_name(self) -> str:
        return "yolo26n_pose"

    def get_task_type(self) -> str:
        return "pose_estimation"

    def get_num_keypoints(self) -> int:
        return 17
