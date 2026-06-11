"""
Common Processors - Reusable preprocessors and postprocessors
DX-APP
"""

from .letterbox_preprocessor import LetterboxPreprocessor
from .simple_resize_preprocessor import SimpleResizePreprocessor
from .grayscale_preprocessor import GrayscaleResizePreprocessor
from .yolo_postprocessor import (
    YOLOv5Postprocessor,
    YOLOv8Postprocessor,
    YOLOXPostprocessor,
)
from .classification_postprocessor import ClassificationPostprocessor
from .segmentation_postprocessor import SemanticSegmentationPostprocessor
from .face_postprocessor import (
    FaceResult,
    SCRFDPostprocessor,
    YOLOv5FacePostprocessor,
    YOLOv7FacePostprocessor,
)
from .pose_postprocessor import (
    YOLOv5PosePostprocessor,
    YOLOv8PosePostprocessor,
)
from .instance_seg_postprocessor import (
    InstanceSegPostprocessor,
    YOLOv8InstanceSegPostprocessor,
    YOLOv5InstanceSegPostprocessor,
)
from .damoyolo_postprocessor import DamoYoloPostprocessor
from .ssd_postprocessor import SSDPostprocessor
from .tflite_det_postprocessor import TFLiteDetectionPostprocessor
from .nanodet_postprocessor import NanoDetPostprocessor
from .depth_postprocessor import DepthEstimationPostprocessor, DepthResult
from .restoration_postprocessor import DnCNNPostprocessor, RestorationResult
from .obb_postprocessor import OBBPostprocessor
from .ppu_postprocessor import (
    PPUPostprocessor,
    YOLOv5PPUPostprocessor,
    YOLOv7PPUPostprocessor,
    YOLOv8PPUPostprocessor,
    YOLOv10PPUPostprocessor,
    YOLOXPPUPostprocessor,
    SCRFDPPUPostprocessor,
    YOLOv5PosePPUPostprocessor,
)
from .centernet_postprocessor import CenterNetPostprocessor
from .efficientdet_postprocessor import EfficientDetPostprocessor
from .retinaface_postprocessor import RetinaFacePostprocessor
from .ulfg_postprocessor import ULFGPostprocessor
from .centerpose_postprocessor import CenterPosePostprocessor
from .yolact_postprocessor import YOLACTPostprocessor
from .espcn_postprocessor import ESPCNPostprocessor
from .zero_dce_postprocessor import ZeroDCEPostprocessor
from .clip_postprocessor import CLIPImagePostprocessor, CLIPTextPostprocessor
from .arcface_postprocessor import ArcFacePostprocessor
from .segformer_postprocessor import SegFormerPostprocessor
from .palm_postprocessor import PalmDetectionPostprocessor
from .tddfa_postprocessor import TDDFAPostprocessor
from .hand_landmark_postprocessor import HandLandmarkPostprocessor
from .attribute_postprocessor import AttributePostprocessor
from .cpp_compat import EmbeddingPostProcess, ZeroDCEPostProcess, PythonFallbackPostProcess

__all__ = [
    # Preprocessors
    'LetterboxPreprocessor',
    'SimpleResizePreprocessor',
    'GrayscaleResizePreprocessor',
    # Detection Postprocessors
    'YOLOv5Postprocessor',
    'YOLOv8Postprocessor', 
    'YOLOXPostprocessor',
    # Classification Postprocessors
    'ClassificationPostprocessor',
    # Segmentation Postprocessors
    'SemanticSegmentationPostprocessor',
    # Face Detection Postprocessors
    'FaceResult',
    'SCRFDPostprocessor',
    'YOLOv5FacePostprocessor',
    'YOLOv7FacePostprocessor',
    # Pose Estimation Postprocessors
    'YOLOv5PosePostprocessor',
    'YOLOv8PosePostprocessor',
    # Instance Segmentation Postprocessors
    'InstanceSegPostprocessor',
    'YOLOv8InstanceSegPostprocessor',
    'YOLOv5InstanceSegPostprocessor',
    # DamoYOLO Postprocessor
    'DamoYoloPostprocessor',
    # SSD Postprocessor
    'SSDPostprocessor',
    # TFLite Detection Postprocessor
    'TFLiteDetectionPostprocessor',
    # NanoDet Postprocessor
    'NanoDetPostprocessor',
    # Depth Estimation Postprocessor
    'DepthEstimationPostprocessor',
    'DepthResult',
    # Image Restoration Postprocessor
    'DnCNNPostprocessor',
    'RestorationResult',
    # OBB Postprocessors
    'OBBPostprocessor',
    # PPU Postprocessors
    'PPUPostprocessor',
    'YOLOv5PPUPostprocessor',
    'YOLOv7PPUPostprocessor',
    'YOLOv8PPUPostprocessor',
    'YOLOv10PPUPostprocessor',
    'YOLOXPPUPostprocessor',
    'SCRFDPPUPostprocessor',
    'YOLOv5PosePPUPostprocessor',
    # CenterNet Postprocessor
    'CenterNetPostprocessor',
    # EfficientDet Postprocessor
    'EfficientDetPostprocessor',
    # RetinaFace Postprocessor
    'RetinaFacePostprocessor',
    # ULFG Postprocessor
    'ULFGPostprocessor',
    # CenterPose Postprocessor
    'CenterPosePostprocessor',
    # YOLACT Postprocessor
    'YOLACTPostprocessor',
    # ESPCN Super-Resolution Postprocessor
    'ESPCNPostprocessor',
    # Zero-DCE Enhancement Postprocessor
    'ZeroDCEPostprocessor',
    # CLIP Postprocessors
    'CLIPImagePostprocessor',
    'CLIPTextPostprocessor',
    # ArcFace Postprocessor
    'ArcFacePostprocessor',
    # SegFormer Postprocessor
    'SegFormerPostprocessor',
    # Palm Detection Postprocessor
    'PalmDetectionPostprocessor',
    # 3DDFA Face Alignment Postprocessor
    'TDDFAPostprocessor',
    # Hand Landmark Postprocessor
    'HandLandmarkPostprocessor',
    # Attribute Recognition Postprocessor
    'AttributePostprocessor',
    # C++ Postprocess Compatibility (Python fallbacks for missing dx_postprocess.so classes)
    'EmbeddingPostProcess',
    'ZeroDCEPostProcess',
    'PythonFallbackPostProcess',
]
