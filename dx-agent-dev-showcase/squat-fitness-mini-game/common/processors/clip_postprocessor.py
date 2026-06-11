"""
CLIP (Contrastive Language-Image Pre-Training) Postprocessor

Feature embedding extraction for both image and text encoders.

Image Encoder:
  Input:  [1, 3, H, W]  — preprocessed image
  Output: [1, D]         — image feature vector (D=512, 768, 1024 depending on backbone)
  → Uses GenericEmbeddingPostprocessor (same algorithm as ArcFace)

Text Encoder:
  Input:  [1, 77]  or [1, 77, D_token]  — tokenized text
  Output: [1, D]   — text feature vector
  → Specialized: needs EOS token extraction from 3D tensor

The output embedding is L2-normalized for cosine similarity computation.
Image-text similarity = dot(image_embedding, text_embedding)
"""

import numpy as np
from typing import List

from ..base import IPostprocessor, PreprocessContext, EmbeddingResult
from .embedding_postprocessor import GenericEmbeddingPostprocessor


class CLIPImagePostprocessor(GenericEmbeddingPostprocessor):
    """
    Postprocessor for CLIP image encoder.

    Thin wrapper around GenericEmbeddingPostprocessor with
    CLIP-specific defaults (model_type="image_encoder").
    """

    def __init__(self, input_width: int = 224, input_height: int = 224, config: dict = None):
        super().__init__(
            input_width=input_width,
            input_height=input_height,
            config=config,
            model_type="image_encoder",
            model_name="clip_image",
        )


class CLIPTextPostprocessor(IPostprocessor):
    """
    Postprocessor for CLIP text encoder.

    Extracts and L2-normalizes the text feature embedding.
    """

    def __init__(self, input_width: int = 77, input_height: int = 512, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.normalize = self.config.get('normalize', True)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[EmbeddingResult]:
        """
        Process CLIP text encoder output.

        Args:
            outputs: [feature_vector] shape [1, D] or [1, seq_len, D]
            ctx: PreprocessContext

        Returns:
            List with single EmbeddingResult
        """
        output = outputs[0]

        # If output is [1, seq_len, D], take the EOS token embedding
        if output.ndim == 3:
            # CLIP text encoder: EOS token is at the position of the highest token ID
            # (end-of-text token = 49407 in CLIP tokenizer)
            # If we have token IDs in a second output, use those; otherwise use heuristic
            if len(outputs) > 1 and outputs[1].ndim >= 2:
                # Token IDs available — find EOS position
                token_ids = outputs[1].flatten()
                eos_pos = int(np.argmax(token_ids))  # EOS has highest token ID
                embedding = output[0, eos_pos, :].flatten().astype(np.float32)
            else:
                # Heuristic: CLIP pads with zeros after EOS.
                # Find last non-zero row by L2 norm of each position
                seq_norms = np.linalg.norm(output[0], axis=1)  # [seq_len]
                nonzero_mask = seq_norms > 1e-6
                if np.any(nonzero_mask):
                    # EOS is typically the last non-zero position
                    eos_pos = int(np.where(nonzero_mask)[0][-1])
                    embedding = output[0, eos_pos, :].flatten().astype(np.float32)
                else:
                    # Fallback to last position
                    embedding = output[0, -1, :].flatten().astype(np.float32)
        else:
            embedding = output.flatten().astype(np.float32)

        # L2 normalize
        if self.normalize:
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

        return [EmbeddingResult(
            embedding=embedding,
            model_type="text_encoder",
        )]

    def get_model_name(self) -> str:
        return "clip_text"
