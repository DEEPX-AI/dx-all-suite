"""
Image Restoration Postprocessor

Handles image restoration models (DnCNN, etc.) that output a single-channel
or multi-channel image in NCHW format:
  - output[0]: [1, C, H, W]  restored/denoised image

DnCNN outputs the denoised image directly (values in [0, 1] range).
"""

import numpy as np
from typing import List
from dataclasses import dataclass

from ..base import IPostprocessor, PreprocessContext


@dataclass
class RestorationResult:
    """Result from image restoration model."""
    output_image: np.ndarray  # restored image in HWC uint8 format


class DnCNNPostprocessor(IPostprocessor):
    """
    Postprocessor for DnCNN denoising model.

    DnCNN outputs the denoised image directly in [1, 1, H, W] format.
    Values are clamped to [0, 1] and scaled to uint8.
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext):
        """
        Process DnCNN output.

        Args:
            outputs: Model output shape [1, 1, H, W] — denoised image in [0, 1]
            ctx: PreprocessContext (contains preprocessed input info)

        Returns:
            RestorationResult with denoised image
        """
        raw = np.squeeze(outputs[0])  # [H, W] or [C, H, W] or [H, W, C] for color

        # CHW → HWC for color models, but skip if already HWC (NHWC models like UNet)
        if raw.ndim == 3:
            if raw.shape[2] <= 4 and raw.shape[0] > 4:
                pass  # Already HWC (e.g. unet output [256, 256, 3])
            else:
                raw = np.transpose(raw, (1, 2, 0))  # CHW → HWC

        # Model outputs denoised image directly — use as-is
        denoised = raw

        # Normalize to uint8: handle different output value ranges
        dmin, dmax = float(denoised.min()), float(denoised.max())
        if dmax - dmin < 1e-6:
            denoised_uint8 = np.zeros_like(denoised, dtype=np.uint8)
        elif dmin >= -0.1 and dmax <= 1.1:
            # [0, 1] range — standard DnCNN output
            denoised_uint8 = (np.clip(denoised, 0.0, 1.0) * 255.0).astype(np.uint8)
        elif dmin >= -1.0 and dmax <= 256.0:
            # Roughly [0, 255] range
            denoised_uint8 = np.clip(denoised, 0.0, 255.0).astype(np.uint8)
        else:
            # Arbitrary range — min-max normalize to [0, 255]
            denoised_uint8 = ((denoised - dmin) / (dmax - dmin) * 255.0).astype(np.uint8)

        return [RestorationResult(output_image=denoised_uint8)]

    def get_model_name(self) -> str:
        return "dncnn"
