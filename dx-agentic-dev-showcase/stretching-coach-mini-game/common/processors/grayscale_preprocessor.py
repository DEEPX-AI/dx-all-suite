"""
Grayscale Preprocessor

Converts BGR input to single-channel grayscale and resizes.
Used for models like DnCNN that expect [1, H, W, 1] uint8 input.
Also stores the normalized (float [0,1]) version in ctx for denoising.
"""

import cv2
import numpy as np
from typing import Tuple

from ..base import IPreprocessor, PreprocessContext


class GrayscaleResizePreprocessor(IPreprocessor):
    """
    Preprocessor for grayscale models:
      1. Convert BGR → grayscale
      2. Resize to target size
      3. Add channel dim → [H, W, 1]
      4. Store normalized version in ctx for post-processing usage

    Args:
        store_original: If True, saves the original BGR image in ctx.original_image.
                        Needed for ESPCN-style color restoration (YCrCb merge).
    """

    def __init__(self, input_width: int, input_height: int, store_original: bool = False):
        self.input_width = input_width
        self.input_height = input_height
        self.store_original = store_original

    def process(self, image: np.ndarray) -> Tuple[np.ndarray, PreprocessContext]:
        h, w = image.shape[:2]

        # Convert to grayscale
        if len(image.shape) == 3 and image.shape[2] == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif len(image.shape) == 2:
            gray = image
        else:
            gray = image[:, :, 0]

        # Resize
        resized = cv2.resize(gray, (self.input_width, self.input_height))

        # Store normalized version in context (for DnCNN: denoised = input - residual)
        ctx = PreprocessContext(
            original_width=w,
            original_height=h,
            scale=1.0,
            pad_x=0,
            pad_y=0,
        )
        ctx.normalized_input = resized.astype(np.float32) / 255.0
        if self.store_original:
            ctx.original_image = image  # BGR, for YCrCb color restoration

        # Model input: [H, W, 1] uint8
        input_tensor = resized[:, :, np.newaxis]

        return input_tensor, ctx

    def get_input_width(self) -> int:
        return self.input_width

    def get_input_height(self) -> int:
        return self.input_height
