"""
Depth Estimation Postprocessor

Handles depth estimation models (FastDepth, MiDaS, etc.) that output a
depth map in NCHW format:
  - output[0]: [1, 1, H, W]  depth map (raw depth values)
"""

import cv2
import numpy as np
from typing import List
from dataclasses import dataclass

from ..base import IPostprocessor, PreprocessContext


@dataclass
class DepthResult:
    """Result from depth estimation model."""
    depth_map: np.ndarray       # raw depth map [H, W]
    depth_colormap: np.ndarray  # colorized depth map [H, W, 3] uint8


class DepthEstimationPostprocessor(IPostprocessor):
    """
    Postprocessor for monocular depth estimation.

    Converts raw depth output to colorized visualization.
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.colormap = self.config.get('colormap', cv2.COLORMAP_MAGMA)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext):
        """
        Process depth estimation output.

        Args:
            outputs: [depth_tensor]  shape [1, 1, H, W]
            ctx: PreprocessContext

        Returns:
            DepthResult with depth map and colorized version
        """
        depth = np.squeeze(outputs[0])  # [H, W]

        # Normalize depth to 0-255 for visualization
        d_min = depth.min()
        d_max = depth.max()
        if d_max - d_min > 1e-6:
            depth_norm = ((depth - d_min) / (d_max - d_min) * 255).astype(np.uint8)
        else:
            depth_norm = np.zeros_like(depth, dtype=np.uint8)

        # Apply colormap
        depth_color = cv2.applyColorMap(depth_norm, self.colormap)

        # Resize to original image size
        depth_color = cv2.resize(depth_color, (ctx.original_width, ctx.original_height))

        return [DepthResult(
            depth_map=depth,
            depth_colormap=depth_color,
        )]

    def get_model_name(self) -> str:
        return "depth"
