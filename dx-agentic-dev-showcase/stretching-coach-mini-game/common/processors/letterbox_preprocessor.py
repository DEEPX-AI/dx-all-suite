"""
Letterbox Preprocessor

Maintains aspect ratio while resizing with padding.
Used by YOLO family (v5-v12, X), SCRFD, YOLOv8seg, etc.
"""

import numpy as np
import cv2
from typing import Tuple

from ..base import IPreprocessor, PreprocessContext


class LetterboxPreprocessor(IPreprocessor):
    """
    Letterbox resize preprocessor.
    
    Maintains aspect ratio and adds padding to reach target size.
    Stores gain and pad in context for coordinate restoration.
    """
    
    def __init__(self, input_width: int, input_height: int, pad_color: Tuple[int, int, int] = (114, 114, 114)):
        """
        Initialize preprocessor.
        
        Args:
            input_width: Model input width
            input_height: Model input height
            pad_color: Padding color (default: gray 114, 114, 114)
        """
        self._input_width = input_width
        self._input_height = input_height
        self._pad_color = pad_color
    
    def _letterbox(self, img: np.ndarray) -> Tuple[np.ndarray, float, Tuple[int, int]]:
        """
        Apply letterbox transformation.
        
        Args:
            img: Input image (HWC format, any color space)
            
        Returns:
            Tuple of (letterboxed image, gain, (top_pad, left_pad))
        """
        shape = img.shape[:2]  # (height, width)
        
        # Calculate scale ratio
        gain = min(self._input_height / shape[0], self._input_width / shape[1])
        
        # New unpadded size (width, height)
        new_unpad = int(round(shape[1] * gain)), int(round(shape[0] * gain))
        
        # Padding
        dw = (self._input_width - new_unpad[0]) / 2
        dh = (self._input_height - new_unpad[1]) / 2
        
        # Resize if needed
        if shape[::-1] != new_unpad:
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        
        # Add border
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        
        img = cv2.copyMakeBorder(
            img, top, bottom, left, right,
            cv2.BORDER_CONSTANT, value=self._pad_color
        )
        
        return img, gain, (top, left)
    
    def process(self, input_image: np.ndarray) -> Tuple[np.ndarray, PreprocessContext]:
        """
        Preprocess image with letterbox transformation.
        
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
        ctx.original_image = input_image.copy()  # BGR original for color restoration
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        
        # Apply letterbox
        result, gain, pad = self._letterbox(rgb)
        
        # Store in context for coordinate restoration
        ctx.scale = gain
        ctx.pad_y = pad[0]  # top
        ctx.pad_x = pad[1]  # left
        
        return result, ctx
    
    def get_input_width(self) -> int:
        return self._input_width
    
    def get_input_height(self) -> int:
        return self._input_height
