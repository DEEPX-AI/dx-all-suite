"""
Simple Resize Preprocessor

Direct resize without aspect ratio preservation.
Used by EfficientNet, DeepLabV3, etc.
"""

import numpy as np
import cv2
from typing import Tuple

from ..base import IPreprocessor, PreprocessContext


class SimpleResizePreprocessor(IPreprocessor):
    """
    Simple resize preprocessor.
    
    Directly resizes image to target size without padding.
    Suitable for classification and semantic segmentation models.
    
    Args:
        input_width: Model input width
        input_height: Model input height
        normalize_float: If True, return float32 NCHW [0,1] tensor
                         (for models that require normalized float input)
    """
    
    def __init__(self, input_width: int, input_height: int,
                 normalize_float: bool = False):
        self._input_width = input_width
        self._input_height = input_height
        self._normalize_float = normalize_float
    
    def process(self, input_image: np.ndarray) -> Tuple[np.ndarray, PreprocessContext]:
        """
        Preprocess image with simple resize.
        
        Args:
            input_image: Input image (BGR, HWC format)
            
        Returns:
            Tuple of (preprocessed_image, context)
        """
        ctx = PreprocessContext()
        ctx.original_height = input_image.shape[0]
        ctx.original_width = input_image.shape[1]
        ctx.input_width = self._input_width
        ctx.input_height = self._input_height
        # For simple direct resize we have independent scale factors per axis
        # because the aspect ratio may change (stretch). Use scale_x/scale_y
        # for inverse mapping back to original image coordinates.
        ctx.scale_x = float(self._input_width) / float(input_image.shape[1])
        ctx.scale_y = float(self._input_height) / float(input_image.shape[0])
        # Keep `scale` for backwards compatibility (set to geometric mean).
        ctx.scale = min(ctx.scale_x, ctx.scale_y)
        ctx.pad_x = 0
        ctx.pad_y = 0
        ctx.original_image = input_image.copy()  # BGR original for color restoration
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        
        # Direct resize
        resized = cv2.resize(rgb, (self._input_width, self._input_height), 
                            interpolation=cv2.INTER_LINEAR)
        
        # Store normalized input (RGB float32 [0,1] CHW) for models that need it
        # (e.g., Zero-DCE low-light enhancement)
        resized_float = resized.astype(np.float32) / 255.0
        ctx.normalized_input = np.transpose(resized_float, (2, 0, 1))  # HWC → CHW
        
        if self._normalize_float:
            return ctx.normalized_input, ctx
        return resized, ctx
    
    def get_input_width(self) -> int:
        return self._input_width
    
    def get_input_height(self) -> int:
        return self._input_height
