"""
Segmentation Postprocessors

Unified postprocessor for all semantic segmentation models
(DeepLabV3, FCN, PIDNet, BiseNet, SegFormer, etc.).

Features (controlled via constructor flags):
  - argmax on NCHW / CHW / HW logits
  - optional bilinear upsample when model outputs at reduced resolution
    (e.g. SegFormer outputs at 1/4 resolution)
  - optional resize back to original image dimensions (handles both
    SimpleResize and Letterbox padding)

Backward-compatible: defaults keep legacy behaviour (no upsample, no
resize), so all existing factory code works without change.
"""

import numpy as np
import cv2
from typing import List, Any

from ..base import IPostprocessor, PreprocessContext, SegmentationResult


class SemanticSegmentationPostprocessor(IPostprocessor):
    """
    Unified postprocessor for semantic segmentation models.

    Supports two optional post-processing steps (off by default):

    1. **upsample_to_input** — bilinear-upsample logits from a reduced
       output resolution (e.g. 1/4) to the full model-input resolution
       *before* argmax, improving boundary accuracy.

    2. **resize_to_original** — resize the final class map back to the
       original image size recorded in *PreprocessContext*.  Handles both
       simple-resize and letterbox-padded preprocessing automatically.

    Usage::

        # Legacy behaviour  (DeepLabV3, FCN, PIDNet, …)
        pp = SemanticSegmentationPostprocessor(w, h, config)

        # SegFormer-style  (reduced output + resize to original)
        pp = SemanticSegmentationPostprocessor(
            w, h, config,
            upsample_to_input=True,
            resize_to_original=True,
        )
    """

    def __init__(
        self,
        input_width: int = 512,
        input_height: int = 512,
        config: dict = None,
        *,
        upsample_to_input: bool = False,
        resize_to_original: bool = False,
    ):
        """
        Args:
            input_width:  Model input width.
            input_height: Model input height.
            config:       Optional configuration dict
                          (key ``num_classes`` recognised, default 19).
            upsample_to_input:  If *True*, bilinear-upsample logits to
                ``(input_width, input_height)`` when the model output is
                smaller than the input.  Typical for transformer-based
                models (SegFormer, SegViT, …).
            resize_to_original: If *True*, resize the class map to the
                original image size using ``ctx.original_width/height``.
        """
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.num_classes = self.config.get('num_classes', 19)
        self._upsample_to_input = upsample_to_input
        self._resize_to_original = resize_to_original

    # ------------------------------------------------------------------
    # Core processing
    # ------------------------------------------------------------------
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[SegmentationResult]:
        """
        Process semantic segmentation model outputs.

        Args:
            outputs: Model outputs — expected shape ``[1, C, H, W]``,
                     ``[C, H, W]``, or ``[H, W]`` (pre-argmaxed).
            ctx:     Preprocessing context.

        Returns:
            List containing a single ``SegmentationResult``.
        """
        output = outputs[0]

        # ---- parse shape ---------------------------------------------------
        if output.ndim == 4:
            logits = output[0]           # [C, H, W] or [H, W, C] (NHWC)
            # Pre-argmaxed: single-channel or integer type → skip upsample+argmax
            if logits.shape[0] == 1 or np.issubdtype(logits.dtype, np.integer):
                class_map = logits.squeeze().astype(np.int32)
                class_map = self._maybe_resize_to_original(class_map, ctx)
                return [self._make_result(class_map)]
            # NHWC detection: last dim is small class count, first dims are spatial
            if logits.ndim == 3 and logits.shape[2] < logits.shape[0] and logits.shape[2] < logits.shape[1]:
                logits = np.transpose(logits, (2, 0, 1))  # [H, W, C] → [C, H, W]
        elif output.ndim == 3:
            # Could be [C, H, W] logits OR [1, H, W] pre-argmaxed (NPU).
            # Heuristic: if first dim == 1 or dtype is integer → pre-argmaxed.
            if output.shape[0] == 1 or np.issubdtype(output.dtype, np.integer):
                class_map = output.squeeze().astype(np.int32)  # [H, W]
                class_map = self._maybe_resize_to_original(class_map, ctx)
                return [self._make_result(class_map)]
            logits = output              # [C, H, W]
        elif output.ndim == 2:
            # already argmaxed → skip upsample (no logits)
            class_map = output.astype(np.int32)
            class_map = self._maybe_resize_to_original(class_map, ctx)
            return [self._make_result(class_map)]
        else:
            return []

        # ---- optional upsample logits to input resolution ------------------
        if self._upsample_to_input:
            logits = self._upsample_logits(logits)

        # ---- argmax --------------------------------------------------------
        class_map = np.argmax(logits, axis=0).astype(np.int32)  # [H, W]

        # ---- optional resize to original image size ------------------------
        if self._resize_to_original:
            class_map = self._maybe_resize_to_original(class_map, ctx)

        return [self._make_result(class_map)]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _upsample_logits(self, logits: np.ndarray) -> np.ndarray:
        """Bilinear-upsample logits [C, H, W] to (input_height, input_width)."""
        out_h, out_w = logits.shape[1], logits.shape[2]
        if out_h >= self.input_height and out_w >= self.input_width:
            return logits
        upsampled = np.zeros(
            (logits.shape[0], self.input_height, self.input_width),
            dtype=np.float32,
        )
        for c in range(logits.shape[0]):
            upsampled[c] = cv2.resize(
                logits[c],
                (self.input_width, self.input_height),
                interpolation=cv2.INTER_LINEAR,
            )
        return upsampled

    @staticmethod
    def _maybe_resize_to_original(
        class_map: np.ndarray,
        ctx: PreprocessContext,
    ) -> np.ndarray:
        """Resize class map to original image size if available in *ctx*."""
        if ctx.original_width <= 0 or ctx.original_height <= 0:
            return class_map

        if ctx.pad_x == 0 and ctx.pad_y == 0:
            # SimpleResize — no padding
            if (class_map.shape[1] != ctx.original_width
                    or class_map.shape[0] != ctx.original_height):
                class_map = cv2.resize(
                    class_map.astype(np.float32),
                    (ctx.original_width, ctx.original_height),
                    interpolation=cv2.INTER_NEAREST,
                ).astype(np.int32)
        else:
            # Letterbox — crop padding then resize
            gain = max(ctx.scale, 1e-6)
            unpad_h = int(round(ctx.original_height * gain))
            unpad_w = int(round(ctx.original_width * gain))
            top, left = int(ctx.pad_y), int(ctx.pad_x)
            cropped = class_map[top:top + unpad_h, left:left + unpad_w]
            if cropped.size > 0:
                class_map = cv2.resize(
                    cropped.astype(np.float32),
                    (ctx.original_width, ctx.original_height),
                    interpolation=cv2.INTER_NEAREST,
                ).astype(np.int32)

        return class_map

    @staticmethod
    def _make_result(class_map: np.ndarray) -> SegmentationResult:
        h, w = class_map.shape
        unique_classes = np.unique(class_map).tolist()
        return SegmentationResult(
            mask=class_map,
            width=w,
            height=h,
            class_ids=unique_classes,
            class_names=[],
        )

    def get_model_name(self) -> str:
        return "semantic_segmentation"
