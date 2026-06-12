"""
ArcFace Postprocessor

Face recognition feature embedding extraction.

Input:  [1, 3, 112, 112]  — aligned and cropped face image
Output: [1, D]             — face embedding vector (D=128 or 512)

The output embedding is L2-normalized for cosine similarity-based
face verification/identification.

Inherits from GenericEmbeddingPostprocessor — same algorithm
(flatten → L2 normalize → EmbeddingResult), different defaults.
"""

from typing import List

from .embedding_postprocessor import GenericEmbeddingPostprocessor


class ArcFacePostprocessor(GenericEmbeddingPostprocessor):
    """
    Postprocessor for ArcFace face recognition models.

    Thin wrapper around GenericEmbeddingPostprocessor with
    face-specific defaults (112x112 input, model_type="face_embedding").
    """

    def __init__(self, input_width: int = 112, input_height: int = 112, config: dict = None):
        super().__init__(
            input_width=input_width,
            input_height=input_height,
            config=config,
            model_type="face_embedding",
            model_name="arcface",
        )
