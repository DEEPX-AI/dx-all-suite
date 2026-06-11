"""
Zero-DCE (Zero-Reference Deep Curve Estimation) Postprocessor

Low-light image enhancement using learned curve parameters.

Supports two output formats:
  1. [1, 24, H, W]  — 8 iterations × 3 channels of curve parameter maps (α)
     Enhancement formula (per iteration):
       enhanced = enhanced + α * enhanced * (1 - enhanced)
  2. [1, 3, H, W]   — Enhanced image output directly (no curve application needed)

The postprocessor auto-detects the format based on channel count.
"""

import numpy as np
import cv2
from typing import List

from ..base import IPostprocessor, PreprocessContext, EnhancedImageResult


class ZeroDCEPostprocessor(IPostprocessor):
    """
    Postprocessor for Zero-DCE low-light enhancement models.

    Applies iterative Light Enhancement (LE) curve using predicted parameters.
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.num_iterations = self.config.get('num_iterations', 8)

    def _get_initial_enhanced(self, ctx: PreprocessContext, h: int, w: int) -> np.ndarray:
        """Reconstruct initial enhanced image from preprocessing context."""
        if hasattr(ctx, 'normalized_input') and ctx.normalized_input is not None:
            enhanced = ctx.normalized_input.copy()
            if enhanced.ndim == 3 and enhanced.shape[2] == 3:
                enhanced = np.transpose(enhanced, (2, 0, 1))  # HWC → CHW
        else:
            enhanced = np.full((3, h, w), 0.5, dtype=np.float32)

        if enhanced.shape[1] != h or enhanced.shape[2] != w:
            resized = np.zeros((3, h, w), dtype=np.float32)
            for c in range(3):
                resized[c] = cv2.resize(enhanced[c], (w, h), interpolation=cv2.INTER_LINEAR)
            enhanced = resized
        return enhanced

    def _apply_le_curve(self, enhanced: np.ndarray, params: np.ndarray, n_iters: int) -> np.ndarray:
        """Apply iterative LE curve: E = E + α * E * (1 - E)."""
        num_channels = 3
        for i in range(n_iters):
            alpha = np.clip(params[i * num_channels:(i + 1) * num_channels], 0.0, 1.0)
            enhanced = enhanced + alpha * enhanced * (1.0 - enhanced)
        return np.clip(enhanced, 0.0, 1.0)

    def _to_bgr_uint8(self, enhanced: np.ndarray, ctx: PreprocessContext) -> np.ndarray:
        """Convert CHW float32 to HWC BGR uint8, resize to original if needed."""
        enhanced_bgr = np.ascontiguousarray(
            np.transpose(enhanced, (1, 2, 0))[:, :, ::-1])
        if ctx.original_width > 0 and ctx.original_height > 0:
            if enhanced_bgr.shape[1] != ctx.original_width or enhanced_bgr.shape[0] != ctx.original_height:
                enhanced_bgr = cv2.resize(
                    enhanced_bgr, (ctx.original_width, ctx.original_height),
                    interpolation=cv2.INTER_LINEAR)
        return np.clip(enhanced_bgr * 255.0, 0, 255).astype(np.uint8)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext):
        """Process Zero-DCE output."""
        params = np.squeeze(outputs[0])  # [C, H, W] where C is 3 or 24

        if params.ndim == 2:
            enhanced_uint8 = (np.clip(params, 0.0, 1.0) * 255.0).astype(np.uint8)
            return [EnhancedImageResult(output_image=enhanced_uint8)]

        h, w = params.shape[1], params.shape[2]
        n_channels = params.shape[0]

        # Direct enhanced image output: [3, H, W] — use as-is
        if n_channels == 3:
            enhanced = np.clip(params, 0.0, 1.0)
            return [EnhancedImageResult(output_image=self._to_bgr_uint8(enhanced, ctx))]

        # Curve parameter output: [24, H, W] — apply LE curve iterations
        n_iters = n_channels // 3
        enhanced = self._get_initial_enhanced(ctx, h, w)
        enhanced = self._apply_le_curve(enhanced, params, n_iters)
        return [EnhancedImageResult(output_image=self._to_bgr_uint8(enhanced, ctx))]

    def get_model_name(self) -> str:
        return "zero_dce"
