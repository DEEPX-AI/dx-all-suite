"""
Abstract interfaces for pre-processor and post-processor

These interfaces define the contract for all preprocessing and postprocessing operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Optional
import numpy as np


@dataclass
class PreprocessContext:
    """
    Preprocessing context containing metadata needed for postprocessing.
    
    This structure holds information about the preprocessing transformations
    that need to be reversed during postprocessing (e.g., letterbox padding).
    """
    pad_x: int = 0
    pad_y: int = 0
    # Uniform scale (used for letterbox-preserving preprocessors). For
    # non-uniform resizing (stretch), prefer `scale_x`/`scale_y` below.
    scale: float = 1.0
    # Per-axis scale factors: model_input_width / original_width,
    # and model_input_height / original_height respectively. These are
    # populated by preprocessors that perform independent axis scaling.
    scale_x: float = 0.0
    scale_y: float = 0.0
    original_width: int = 0
    original_height: int = 0
    input_width: int = 0
    input_height: int = 0
    original_image: Optional[np.ndarray] = None  # BGR original for color restoration
    normalized_input: Optional[np.ndarray] = None  # [C,H,W] float32 [0,1] for enhancement models


@dataclass
class DetectionResult:
    """Base detection result structure."""
    box: List[float] = field(default_factory=list)  # x1, y1, x2, y2
    confidence: float = 0.0
    class_id: int = 0
    class_name: str = ""
    keypoints: Optional[List] = None  # Optional keypoints for face/pose models
    
    def area(self) -> float:
        """Calculate bounding box area."""
        if len(self.box) < 4:
            return 0.0
        return (self.box[2] - self.box[0]) * (self.box[3] - self.box[1])
    
    def iou(self, other: 'DetectionResult') -> float:
        """Calculate intersection over union with another detection."""
        if len(self.box) < 4 or len(other.box) < 4:
            return 0.0
        
        x_left = max(self.box[0], other.box[0])
        y_top = max(self.box[1], other.box[1])
        x_right = min(self.box[2], other.box[2])
        y_bottom = min(self.box[3], other.box[3])
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        union = self.area() + other.area() - intersection
        
        return intersection / union if union > 0 else 0.0


@dataclass
class Keypoint:
    """Single keypoint with position and confidence."""
    x: float = 0.0
    y: float = 0.0
    confidence: float = 0.0


@dataclass
class PoseResult:
    """
    Pose estimation result structure.
    
    Contains detection box + keypoints for pose estimation models
    like YOLOv5-pose, YOLOv8-pose.
    """
    box: List[float] = field(default_factory=list)  # x1, y1, x2, y2
    confidence: float = 0.0
    class_id: int = 0
    class_name: str = "person"
    keypoints: List[Keypoint] = field(default_factory=list)  # 17 keypoints for COCO
    
    def get_keypoint(self, idx: int) -> Optional[Keypoint]:
        """Get keypoint by index."""
        if 0 <= idx < len(self.keypoints):
            return self.keypoints[idx]
        return None


@dataclass
class InstanceSegResult:
    """
    Instance segmentation result structure.
    
    Contains detection box + per-instance mask for models
    like YOLOv8-seg, Mask R-CNN.
    """
    box: List[float] = field(default_factory=list)  # x1, y1, x2, y2
    confidence: float = 0.0
    class_id: int = 0
    class_name: str = ""
    mask: np.ndarray = field(default_factory=lambda: np.array([]))  # H*W binary mask


@dataclass
class SegmentationResult:
    """Semantic segmentation result structure."""
    mask: np.ndarray = field(default_factory=lambda: np.array([]))  # H*W mask with class IDs
    width: int = 0
    height: int = 0
    class_ids: List[int] = field(default_factory=list)
    class_names: List[str] = field(default_factory=list)


@dataclass
class ClassificationResult:
    """Classification result structure."""
    class_id: int = 0
    class_name: str = ""
    confidence: float = 0.0
    top_k: List[Tuple[int, float]] = field(default_factory=list)


@dataclass
class OBBResult:
    """
    Oriented Bounding Box (OBB) detection result structure.
    
    Uses center-based representation: [cx, cy, w, h, angle]
    where angle is the rotation angle in radians.
    """
    cx: float = 0.0           # Center x coordinate
    cy: float = 0.0           # Center y coordinate
    width: float = 0.0        # Box width (before rotation)
    height: float = 0.0       # Box height (before rotation)
    angle: float = 0.0        # Rotation angle in radians
    confidence: float = 0.0
    class_id: int = 0
    class_name: str = ""


class IPreprocessor(ABC):
    """
    Abstract interface for preprocessors.
    
    Preprocessors transform input images into the format expected by the model.
    """
    
    @abstractmethod
    def process(self, input_image: np.ndarray) -> Tuple[np.ndarray, PreprocessContext]:
        """
        Preprocess an input image for model inference.
        
        Args:
            input_image: Original input image (BGR format)
            
        Returns:
            Tuple of (preprocessed_image, preprocessing_context)
        """
        pass
    
    @abstractmethod
    def get_input_width(self) -> int:
        """Get the expected input width for the model."""
        pass
    
    @abstractmethod
    def get_input_height(self) -> int:
        """Get the expected input height for the model."""
        pass


@dataclass
class EmbeddingResult:
    """Result from embedding models (CLIP, ArcFace, etc.)."""
    embedding: np.ndarray = field(default_factory=lambda: np.array([]))  # L2-normalized feature vector
    model_type: str = ""  # "image_encoder", "text_encoder", "face_embedding"


@dataclass
class SuperResolutionResult:
    """Result from super-resolution models (ESPCN, etc.)."""
    output_image: np.ndarray = field(default_factory=lambda: np.array([]))  # upscaled HWC uint8
    scale_factor: int = 2


@dataclass
class EnhancedImageResult:
    """Result from image enhancement models (Zero-DCE, etc.)."""
    output_image: np.ndarray = field(default_factory=lambda: np.array([]))  # enhanced HWC uint8


@dataclass
class FaceAlignmentResult:
    """Result from 3D face alignment models (3DDFA, etc.)."""
    params: np.ndarray = field(default_factory=lambda: np.array([]))  # raw 3DMM parameters
    landmarks_2d: np.ndarray = field(default_factory=lambda: np.array([]))  # [68, 2] projected 2D landmarks
    landmarks_3d: np.ndarray = field(default_factory=lambda: np.array([]))  # [68, 3] 3D face landmarks
    pose: List[float] = field(default_factory=list)  # [yaw, pitch, roll] in degrees


@dataclass
class HandLandmarkResult:
    """Result from hand landmark detection models (MediaPipe HandLandmark, etc.)."""
    landmarks: np.ndarray = field(default_factory=lambda: np.array([]))  # [21, 3] hand keypoints (x, y, z)
    confidence: float = 0.0  # hand detection confidence
    handedness: str = "Unknown"  # "Left" or "Right"


class IPostprocessor(ABC):
    """
    Abstract interface for postprocessors.
    
    Postprocessors transform model outputs into usable detection/segmentation results.
    """
    
    @abstractmethod
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[Any]:
        """
        Process model outputs into results.
        
        Args:
            outputs: Model output tensors
            ctx: Preprocessing context for coordinate transformation
            
        Returns:
            List of processed results
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name this postprocessor is designed for."""
        pass
