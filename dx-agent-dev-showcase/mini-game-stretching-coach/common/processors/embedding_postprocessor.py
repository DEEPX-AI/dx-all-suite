"""
Generic Embedding Postprocessor

Base class for all embedding/feature extraction postprocessors.
Shared by CLIP image encoder, ArcFace, ReID, and similar models.

Input:  [1, D] or [D] — feature vector output
Output: EmbeddingResult with L2-normalized feature vector

Used to eliminate duplication between CLIPImagePostprocessor and
ArcFacePostprocessor which are algorithmically identical
(flatten → optional L2 normalize → EmbeddingResult).
"""

import numpy as np
from typing import List

from ..base import IPostprocessor, PreprocessContext, EmbeddingResult


class GenericEmbeddingPostprocessor(IPostprocessor):
    """
    Generic postprocessor for embedding/feature extraction models.

    Extracts feature vector and optionally L2-normalizes it.
    Can be used directly or subclassed with different model_type/model_name.
    """

    def __init__(self, input_width: int = 224, input_height: int = 224,
                 config: dict = None, model_type: str = "embedding",
                 model_name: str = "generic_embedding"):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.normalize = self.config.get('normalize', True)
        self._model_type = model_type
        self._model_name = model_name

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[EmbeddingResult]:
        """
        Process embedding model output.

        Args:
            outputs: [feature_vector] shape [1, D] or [D]
            ctx: PreprocessContext

        Returns:
            List with single EmbeddingResult
        """
        output = outputs[0]

        # Handle 3D output [1, seq_len, D] — take last token or pooled output
        if output.ndim == 3:
            output = output[0, -1, :]  # take last position

        embedding = output.flatten().astype(np.float32)

        # Optional L2 normalization
        if self.normalize:
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

        return [EmbeddingResult(
            embedding=embedding,
            model_type=self._model_type,
        )]

    def get_model_name(self) -> str:
        return self._model_name
