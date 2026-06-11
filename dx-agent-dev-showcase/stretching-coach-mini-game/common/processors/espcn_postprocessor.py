"""
ESPCN (Efficient Sub-Pixel Convolutional Network) Postprocessor

Single-image super-resolution model.

Input:  [1, 1, H, W]  — single-channel (Y of YCbCr) normalized to [0, 1]
Output: [1, 1, H*scale, W*scale]  — upscaled Y channel

Unlike DnCNN (which outputs noise residual), ESPCN directly outputs
the upscaled image. The output is clipped to [0, 1] and converted to uint8.

Scale factors: X2, X3, X4 (auto-detected from output/input ratio).
"""

import numpy as np
import cv2
from typing import List

from ..base import IPostprocessor, PreprocessContext, SuperResolutionResult


class ESPCNPostprocessor(IPostprocessor):
    """
    Postprocessor for ESPCN super-resolution models.

    Handles the direct upscaled output (not a residual).
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.scale_factor = self.config.get('scale_factor', 0)  # 0 = auto-detect

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext):
        """
        Process ESPCN output.

        Args:
            outputs: [upscaled_image] shape [1, 1, H_out, W_out] or [1, C, H_out, W_out]
            ctx: PreprocessContext

        Returns:
            SuperResolutionResult with upscaled image (HWC uint8)
        """
        output = np.squeeze(outputs[0])

        # Handle multi-channel output
        if output.ndim == 3:
            # [C, H, W] → [H, W, C]
            output = np.transpose(output, (1, 2, 0))
        elif output.ndim == 2:
            # [H, W] — single channel (Y of YCbCr)
            pass
        else:
            # Unexpected shape, try to use as-is
            output = output.reshape(-1)

        # Auto-detect scale factor
        if self.scale_factor == 0:
            if output.ndim >= 2:
                out_h = output.shape[0]
                scale = max(1, round(out_h / self.input_height))
            else:
                scale = 2
        else:
            scale = self.scale_factor

        # Clip to [0, 1] and convert
        output = np.clip(output, 0.0, 1.0)

        # YCbCr color restoration for single-channel (Y) output
        if output.ndim == 2 and hasattr(ctx, 'original_image') and ctx.original_image is not None:
            # ESPCN works on Y channel; restore color using Cb/Cr from original
            sr_y = (output * 255.0).astype(np.uint8)
            out_h, out_w = sr_y.shape

            # Convert original BGR to YCrCb (OpenCV uses YCrCb, not YCbCr)
            original_bgr = ctx.original_image
            original_ycrcb = cv2.cvtColor(original_bgr, cv2.COLOR_BGR2YCrCb)
            # Bicubic upsample Cr and Cb to match SR output size
            cr_upscaled = cv2.resize(original_ycrcb[:, :, 1], (out_w, out_h),
                                      interpolation=cv2.INTER_CUBIC)
            cb_upscaled = cv2.resize(original_ycrcb[:, :, 2], (out_w, out_h),
                                      interpolation=cv2.INTER_CUBIC)
            # Merge SR Y with upscaled Cr, Cb
            merged_ycrcb = np.stack([sr_y, cr_upscaled, cb_upscaled], axis=2)
            output_uint8 = cv2.cvtColor(merged_ycrcb, cv2.COLOR_YCrCb2BGR)
        else:
            output_uint8 = (output * 255.0).astype(np.uint8)

        return [SuperResolutionResult(
            output_image=output_uint8,
            scale_factor=scale,
        )]

    def get_model_name(self) -> str:
        return "espcn"
