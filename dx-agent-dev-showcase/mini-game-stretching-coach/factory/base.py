"""Local factory interfaces for the stretch-coach app (no source-tree import).

These mirror the dx_app `common.base.IFactory` / `IPoseFactory` contract so the
session is self-contained even when relocated. The runtime still binds the real
`common.processors` / `common.visualizers` via the entry script's path walker.
"""

from abc import ABC, abstractmethod


class IFactory(ABC):
    """5-method abstract factory required by SyncRunner/AsyncRunner."""

    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int):
        """Create and return the preprocessor for this model."""

    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int):
        """Create and return the postprocessor for this model."""

    @abstractmethod
    def create_visualizer(self):
        """Create and return the visualizer for this model's output."""

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name (e.g., 'yolo26n_pose')."""

    @abstractmethod
    def get_task_type(self) -> str:
        """Return the AI task type (e.g., 'pose_estimation')."""


class IPoseFactory(IFactory):
    """Pose-estimation factory — adds keypoint count metadata."""

    def get_num_keypoints(self) -> int:
        """COCO body keypoints (17 for YOLO-pose)."""
        return 17

    def load_config(self, config: dict) -> None:
        """Merge a runtime config dict (called by SyncRunner if present)."""
        if config:
            existing = getattr(self, "config", None) or {}
            existing.update(config)
            self.config = existing
