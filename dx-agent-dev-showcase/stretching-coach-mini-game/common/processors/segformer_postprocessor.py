"""
SegFormer Postprocessor

Thin convenience alias for ``SemanticSegmentationPostprocessor`` with
*upsample_to_input* and *resize_to_original* enabled by default.

SegFormer models typically output logits at 1/4 of the input resolution
(H/4, W/4).  The base class handles bilinear upsampling, argmax, and
optional resize to the original image size — see
``segmentation_postprocessor.py`` for the full algorithm.

Usage is unchanged::

    from common.processors import SegFormerPostprocessor
    pp = SegFormerPostprocessor(1024, 512, config)

This is equivalent to::

    from common.processors import SemanticSegmentationPostprocessor
    pp = SemanticSegmentationPostprocessor(
        1024, 512, config,
        upsample_to_input=True,
        resize_to_original=True,
    )
"""

from typing import Optional

from .segmentation_postprocessor import SemanticSegmentationPostprocessor


class SegFormerPostprocessor(SemanticSegmentationPostprocessor):
    """
    Convenience subclass for SegFormer (and similar transformer-based)
    semantic segmentation models.

    Enables bilinear upsampling from reduced-resolution logits and
    automatic resize to the original image size.
    """

    def __init__(
        self,
        input_width: int = 1024,
        input_height: int = 512,
        config: dict = None,
    ):
        super().__init__(
            input_width=input_width,
            input_height=input_height,
            config=config,
            upsample_to_input=True,
            resize_to_original=True,
        )

    def get_model_name(self) -> str:
        return "segformer"
