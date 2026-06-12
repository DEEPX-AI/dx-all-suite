"""
Abstract Factory interface for model component creation

This interface defines the Abstract Factory pattern for creating
matching sets of preprocessor, postprocessor, and visualizer components.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from .i_processor import IPreprocessor, IPostprocessor
from .i_visualizer import IVisualizer


class _FactoryConfigMixin:
    """Mixin providing load_config() for all factory interfaces."""

    # Alias mapping so that a single config.json works for both C++ and Python.
    # C++ uses 'score_threshold'; Python postprocessors use 'conf_threshold'.
    _CONFIG_ALIASES = {
        "score_threshold": "conf_threshold",
    }

    def load_config(self, config: dict) -> None:
        """
        Load configuration from an external dictionary (e.g. parsed from JSON).

        Override in concrete factories for custom behaviour.
        Default implementation merges into ``self.config`` if it exists,
        applying alias translations (e.g. score_threshold → conf_threshold).
        """
        if hasattr(self, "config") and isinstance(self.config, dict):
            for key, value in config.items():
                alias = self._CONFIG_ALIASES.get(key)
                if alias and alias not in config:
                    self.config[alias] = value
                self.config[key] = value


class IDetectionFactory(_FactoryConfigMixin, ABC):
    """
    Abstract Factory interface for object detection models.
    
    Creates matching sets of components for object detection models.
    Each concrete factory (e.g., YOLOv5Factory) creates components
    that are guaranteed to work together correctly.
    """
    
    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int) -> IPreprocessor:
        """Create a preprocessor for this model."""
        pass
    
    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int) -> IPostprocessor:
        """Create a postprocessor for this model."""
        pass
    
    @abstractmethod
    def create_visualizer(self) -> IVisualizer:
        """Create a visualizer for this model."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name this factory is for."""
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        """Get the task type this factory is for."""
        pass


class ISegmentationFactory(_FactoryConfigMixin, ABC):
    """Abstract Factory interface for semantic segmentation models."""
    
    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int) -> IPreprocessor:
        pass
    
    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int) -> IPostprocessor:
        pass
    
    @abstractmethod
    def create_visualizer(self) -> IVisualizer:
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass


class IClassificationFactory(_FactoryConfigMixin, ABC):
    """Abstract Factory interface for classification models."""
    
    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int) -> IPreprocessor:
        pass
    
    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int) -> IPostprocessor:
        pass
    
    @abstractmethod
    def create_visualizer(self) -> IVisualizer:
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass


class IPoseFactory(_FactoryConfigMixin, ABC):
    """
    Abstract Factory interface for pose estimation models.
    
    Creates matching sets of components for pose estimation models
    like YOLOv5-pose, YOLOv8-pose.
    """
    
    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int) -> IPreprocessor:
        """Create a preprocessor for this model."""
        pass
    
    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int) -> IPostprocessor:
        """Create a postprocessor for this model."""
        pass
    
    @abstractmethod
    def create_visualizer(self) -> IVisualizer:
        """Create a visualizer for this model (draws skeleton)."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass
    
    @abstractmethod
    def get_num_keypoints(self) -> int:
        """Get number of keypoints (e.g., 17 for COCO)."""
        pass


class IInstanceSegFactory(_FactoryConfigMixin, ABC):
    """
    Abstract Factory interface for instance segmentation models.
    
    Creates matching sets of components for instance segmentation models
    like YOLOv8-seg, Mask R-CNN.
    """
    
    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int) -> IPreprocessor:
        """Create a preprocessor for this model."""
        pass
    
    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int) -> IPostprocessor:
        """Create a postprocessor for this model."""
        pass
    
    @abstractmethod
    def create_visualizer(self) -> IVisualizer:
        """Create a visualizer for this model (draws masks)."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass


class IFaceFactory(_FactoryConfigMixin, ABC):
    """
    Abstract Factory interface for face detection models.
    
    Creates matching sets of components for face detection models
    like SCRFD, YOLOv5Face with facial keypoints.
    """
    
    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int) -> IPreprocessor:
        """Create a preprocessor for this model."""
        pass
    
    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int) -> IPostprocessor:
        """Create a postprocessor for this model."""
        pass
    
    @abstractmethod
    def create_visualizer(self) -> IVisualizer:
        """Create a visualizer for this model (draws face keypoints)."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass
    
    @abstractmethod
    def get_num_keypoints(self) -> int:
        """Get number of facial keypoints (e.g., 5 for standard face)."""
        pass


class IDepthEstimationFactory(_FactoryConfigMixin, ABC):
    """
    Abstract Factory interface for depth estimation models.
    
    Creates matching sets of components for depth estimation models
    like FastDepth, MiDaS.
    """
    
    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int) -> IPreprocessor:
        """Create a preprocessor for this model."""
        pass
    
    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int) -> IPostprocessor:
        """Create a postprocessor for this model."""
        pass
    
    @abstractmethod
    def create_visualizer(self) -> IVisualizer:
        """Create a visualizer for this model (depth colormap)."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass


class IRestorationFactory(_FactoryConfigMixin, ABC):
    """
    Abstract Factory interface for image restoration models.
    
    Creates matching sets of components for image restoration models
    like DnCNN (denoising).
    """
    
    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int) -> IPreprocessor:
        """Create a preprocessor for this model."""
        pass
    
    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int) -> IPostprocessor:
        """Create a postprocessor for this model."""
        pass
    
    @abstractmethod
    def create_visualizer(self) -> IVisualizer:
        """Create a visualizer for this model (side-by-side comparison)."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass


class IOBBFactory(_FactoryConfigMixin, ABC):
    """
    Abstract Factory interface for OBB (Oriented Bounding Box) detection models.
    
    Creates matching sets of components for OBB detection models
    like YOLOv26-OBB for aerial/satellite image object detection.
    """
    
    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int) -> IPreprocessor:
        """Create a preprocessor for this model."""
        pass
    
    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int) -> IPostprocessor:
        """Create a postprocessor for this model."""
        pass
    
    @abstractmethod
    def create_visualizer(self) -> IVisualizer:
        """Create a visualizer for this model (draws rotated bounding boxes)."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass


class IEmbeddingFactory(_FactoryConfigMixin, ABC):
    """
    Abstract Factory interface for embedding / feature extraction models.
    
    Creates matching sets of components for models that produce
    vector embeddings (CLIP image/text encoders, ArcFace, etc.).
    """
    
    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int) -> IPreprocessor:
        """Create a preprocessor for this model."""
        pass
    
    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int) -> IPostprocessor:
        """Create a postprocessor for this model."""
        pass
    
    @abstractmethod
    def create_visualizer(self) -> IVisualizer:
        """Create a visualizer for this model (displays embedding info)."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass


class IFaceAlignmentFactory(_FactoryConfigMixin, ABC):
    """
    Abstract Factory interface for face alignment / 3D face reconstruction models.
    
    Creates matching sets of components for models that output
    3DMM parameters and facial landmarks (3DDFA v2, etc.).
    """
    
    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int) -> IPreprocessor:
        """Create a preprocessor for this model."""
        pass
    
    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int) -> IPostprocessor:
        """Create a postprocessor for this model."""
        pass
    
    @abstractmethod
    def create_visualizer(self) -> IVisualizer:
        """Create a visualizer for this model (draws landmarks + pose)."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass


class IHandLandmarkFactory(_FactoryConfigMixin, ABC):
    """
    Abstract Factory interface for hand landmark detection models.
    
    Creates matching sets of components for models that output
    hand keypoints (MediaPipe HandLandmark, etc.).
    """
    
    @abstractmethod
    def create_preprocessor(self, input_width: int, input_height: int) -> IPreprocessor:
        """Create a preprocessor for this model."""
        pass
    
    @abstractmethod
    def create_postprocessor(self, input_width: int, input_height: int) -> IPostprocessor:
        """Create a postprocessor for this model."""
        pass
    
    @abstractmethod
    def create_visualizer(self) -> IVisualizer:
        """Create a visualizer for this model (draws hand skeleton)."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass
