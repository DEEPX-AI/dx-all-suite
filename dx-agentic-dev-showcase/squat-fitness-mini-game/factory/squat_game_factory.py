"""IFactory for the yolo26n_pose squat fitness mini-game.

Reuses the stock pose preprocessor/postprocessor unchanged; the only
model-specific customization is the visualizer, which carries the game logic.
"""
from common.base import IPoseFactory
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor

from squat_game import SquatGameVisualizer


class SquatGameFactory(IPoseFactory):
    """Factory producing the yolo26n_pose squat-game pipeline components."""

    def __init__(self, config: dict = None):
        self.config = config or {}

    def create_preprocessor(self, input_width: int, input_height: int):
        return LetterboxPreprocessor(input_width, input_height)

    def create_postprocessor(self, input_width: int, input_height: int):
        return YOLOv8PosePostprocessor(input_width, input_height, self.config)

    def create_visualizer(self):
        # SyncRunner calls load_config() before create_visualizer(), so
        # self.config already holds config.json values (thresholds, target).
        return SquatGameVisualizer(self.config)

    def get_model_name(self) -> str:
        return "yolo26n_pose"

    def get_task_type(self) -> str:
        return "pose_estimation"

    def get_num_keypoints(self) -> int:
        """YOLO-Pose uses COCO 17-point body keypoints."""
        return 17
