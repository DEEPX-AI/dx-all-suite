"""
C++ Postprocess Compatibility Layer

Provides Python fallback implementations for PostProcess classes
that are either missing from or incompatible with dx_postprocess.so.

Two categories of fallback:

1. **PythonFallbackPostProcess** (generic adapter)
   For auto-generated models whose output tensor shapes differ from
   the reference models that dx_postprocess.so was compiled against.
   This delegates to the runner's existing Python postprocessor,
   ensuring all models work regardless of C++ compatibility.

   Usage in *_sync_cpp_postprocess.py (auto-generated models):
       from common.processors.cpp_compat import PythonFallbackPostProcess

       def on_engine_init(runner):
           runner._cpp_postprocessor = PythonFallbackPostProcess(runner)
           runner._cpp_convert_fn = None

2. **Specific fallback classes** (EmbeddingPostProcess, ZeroDCEPostProcess)
   For postprocessor types not yet present in dx_postprocess.so v1.0.0.
   These match the C++ pybind11 interface: postprocess(ie_output) -> np.ndarray

When dx_postprocess.so is updated to support these models natively,
the try/except import pattern in reference files will prefer C++ automatically.
"""

from __future__ import annotations

import numpy as np
from typing import List


class PythonFallbackPostProcess:
    """
    Generic Python fallback that delegates to the runner's Python postprocessor.

    Used by auto-generated models when the C++ dx_postprocess.so classes
    crash on non-reference model output shapes. This adapter bridges the
    C++ postprocess interface (``postprocess(ie_output)``) to the Python
    postprocessor interface (``process(outputs, ctx)``).

    The runner must store ``_preprocess_ctx`` before calling postprocess().
    SyncRunner and AsyncRunner both do this automatically.

    Args:
        runner: The SyncRunner or AsyncRunner instance.
                Must have ``.postprocessor`` (IPostprocessor) and
                ``._preprocess_ctx`` (set per-frame by the runner).
    """

    def __init__(self, runner) -> None:
        self._runner = runner

    def postprocess(self, ie_output: List[np.ndarray]):
        """
        Delegate to the Python postprocessor.

        Args:
            ie_output: Model output tensors (same as passed to C++ postprocess).

        Returns:
            Result objects (DetectionResult, ClassificationResult, etc.)
            directly — no numpy conversion needed since _cpp_convert_fn
            should be set to None when using this fallback.
        """
        ctx = getattr(self._runner, '_preprocess_ctx', None)
        return self._runner.postprocessor.process(ie_output, ctx)


class EmbeddingPostProcess:
    """
    Python fallback for face/image embedding postprocessor.

    Matches C++ PostProcess interface:
        postprocess(ie_output: list[np.ndarray]) -> np.ndarray

    Input:  ie_output[0] shape [1, D] — raw embedding vector (D=128 or 512)
    Output: np.ndarray [D] float32 — L2-normalized embedding vector

    Used by ArcFace, CLIP (image encoder), and CLIP (text encoder).
    The output is L2-normalized so that cosine similarity can be computed
    via a simple dot product.
    """

    def __init__(self) -> None:
        pass  # No instance state needed; all logic is stateless

    def postprocess(self, ie_output: List[np.ndarray]) -> np.ndarray:
        """
        L2-normalize the embedding vector.

        Args:
            ie_output: List containing model output tensor(s).
                       ie_output[0] expected shape: [1, D] or [D]

        Returns:
            np.ndarray of shape [D] with float32 dtype, L2-normalized
        """
        if not ie_output or ie_output[0] is None:
            return np.array([], dtype=np.float32)

        embedding = ie_output[0].flatten().astype(np.float32)

        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding


class ZeroDCEPostProcess:
    """
    Python fallback for Zero-DCE low-light enhancement postprocessor.

    Matches C++ PostProcess interface:
        postprocess(ie_output: list[np.ndarray]) -> np.ndarray

    Input:  ie_output[0] shape [1, 24, H, W] — curve parameters (8 iters × 3 ch)
    Output: np.ndarray [24, H, W] float32 — raw curve parameters
    """

    def __init__(self, input_width: int = 0, input_height: int = 0) -> None:
        self._input_width = input_width
        self._input_height = input_height

    def postprocess(self, ie_output: List[np.ndarray]) -> np.ndarray:
        if not ie_output or ie_output[0] is None:
            return np.array([], dtype=np.float32)

        params = np.squeeze(ie_output[0]).astype(np.float32)
        return params


class ClassificationPostProcess:
    """
    Python fallback for classification postprocessor.

    Matches C++ PostProcess interface:
        postprocess(ie_output: list[np.ndarray]) -> np.ndarray

    Input:  ie_output[0] shape [1, num_classes] — class logits/probabilities
    Output: np.ndarray [num_classes] float32 — softmax probabilities
    """

    def __init__(self, num_classes: int = 1000, top_k: int = 5) -> None:
        self._num_classes = num_classes
        self._top_k = top_k

    def postprocess(self, ie_output: List[np.ndarray]) -> np.ndarray:
        if not ie_output or ie_output[0] is None:
            return np.array([], dtype=np.float32)

        logits = ie_output[0].flatten().astype(np.float32)
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)
        return probs
