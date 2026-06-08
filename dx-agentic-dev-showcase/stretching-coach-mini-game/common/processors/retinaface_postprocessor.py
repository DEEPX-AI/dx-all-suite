"""
RetinaFace Postprocessor

Anchor-based face detection with 5-point landmarks.

Output format: 3 tensors (auto-sorted by last dimension):
  - bbox regression: [1, N, 4]    (anchor deltas: dx, dy, dw, dh)
  - classification:  [1, N, 2]    (background/face softmax or sigmoid)
  - landmarks:       [1, N, 10]   (5 keypoints × 2 coordinates)

Anchors generated from multi-scale feature maps with strides [8, 16, 32].
Box decoding uses variance = [0.1, 0.2].
"""

import numpy as np
import cv2
from itertools import product
from typing import List, Optional

from ..base import IPostprocessor, PreprocessContext, Keypoint
from .face_postprocessor import FaceResult


class RetinaFacePostprocessor(IPostprocessor):
    """
    Postprocessor for RetinaFace anchor-based face detection.

    Generates prior boxes, decodes bbox & landmark deltas, applies NMS.
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

        self.score_threshold = self.config.get('score_threshold', 0.5)
        self.nms_threshold = self.config.get('nms_threshold', 0.4)
        self.variance = self.config.get('variance', [0.1, 0.2])
        self.strides = self.config.get('strides', [8, 16, 32])
        self.min_sizes = self.config.get('min_sizes', [[16, 32], [64, 128], [256, 512]])
        self.top_k = self.config.get('top_k', 750)

        # Pre-generate anchors
        self._priors: Optional[np.ndarray] = None

    def _generate_priors(self) -> np.ndarray:
        """Generate prior boxes (anchors) for all feature map scales."""
        anchors = []
        for k, stride in enumerate(self.strides):
            feat_h = (self.input_height + stride - 1) // stride
            feat_w = (self.input_width + stride - 1) // stride
            min_s = self.min_sizes[k] if k < len(self.min_sizes) else self.min_sizes[-1]
            for i, j in product(range(feat_h), range(feat_w)):
                for min_size in min_s:
                    cx = (j + 0.5) * stride / self.input_width
                    cy = (i + 0.5) * stride / self.input_height
                    s_kx = min_size / self.input_width
                    s_ky = min_size / self.input_height
                    anchors.append([cx, cy, s_kx, s_ky])
        return np.array(anchors, dtype=np.float32)

    @property
    def priors(self) -> np.ndarray:
        if self._priors is None:
            self._priors = self._generate_priors()
        return self._priors

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _identify_tensors(self, outputs):
        """Return (bbox_t, score_t, lmk_t) by inspecting last dimension."""
        bbox_t = score_t = lmk_t = None
        for t in [np.squeeze(o) for o in outputs]:
            if t.ndim < 2:
                continue
            last_dim = t.shape[-1]
            if last_dim == 4 and bbox_t is None:
                bbox_t = t
            elif last_dim == 2 and score_t is None:
                score_t = t
            elif last_dim == 10 and lmk_t is None:
                lmk_t = t
        return bbox_t, score_t, lmk_t

    def _filter_by_score(self, bbox_t, score_t, lmk_t, priors):
        """Top-k filter then threshold mask. Returns filtered arrays."""
        if score_t.shape[-1] == 2:
            face_scores = self._softmax(score_t)[:, 1]
        else:
            face_scores = score_t.flatten()

        n = min(bbox_t.shape[0], face_scores.shape[0], priors.shape[0])
        bbox_t = bbox_t[:n]
        face_scores = face_scores[:n]
        priors = priors[:n]
        if lmk_t is not None:
            lmk_t = lmk_t[:n]

        order = face_scores.argsort()[::-1][:self.top_k]
        face_scores = face_scores[order]
        bbox_t = bbox_t[order]
        priors = priors[order]
        if lmk_t is not None:
            lmk_t = lmk_t[order]

        mask = face_scores >= self.score_threshold
        return bbox_t[mask], face_scores[mask], lmk_t[mask] if lmk_t is not None else None, priors[mask]

    def _decode_boxes(self, bbox_t, priors):
        """Decode center-form bbox deltas into (x1, y1, x2, y2) pixel coords."""
        var0, var1 = self.variance
        cx = priors[:, 0] + bbox_t[:, 0] * var0 * priors[:, 2]
        cy = priors[:, 1] + bbox_t[:, 1] * var0 * priors[:, 3]
        w = priors[:, 2] * np.exp(bbox_t[:, 2] * var1)
        h = priors[:, 3] * np.exp(bbox_t[:, 3] * var1)
        x1 = (cx - w / 2) * self.input_width
        y1 = (cy - h / 2) * self.input_height
        x2 = (cx + w / 2) * self.input_width
        y2 = (cy + h / 2) * self.input_height
        return x1, y1, x2, y2

    def _decode_landmarks(self, lmk_t, priors):
        """Decode landmark deltas into pixel coords. Returns array or None."""
        if lmk_t is None:
            return None
        var0 = self.variance[0]
        decoded = np.zeros_like(lmk_t)
        for k in range(5):
            decoded[:, k * 2] = (priors[:, 0] + lmk_t[:, k * 2] * var0 * priors[:, 2]) * self.input_width
            decoded[:, k * 2 + 1] = (priors[:, 1] + lmk_t[:, k * 2 + 1] * var0 * priors[:, 3]) * self.input_height
        return decoded

    def _build_results(self, keep, x1, y1, x2, y2, face_scores, lmk_decoded, ctx):
        """Scale detections back to original image coordinates."""
        gain = max(ctx.scale, 1e-6)
        pad_x, pad_y = ctx.pad_x, ctx.pad_y
        ow, oh = ctx.original_width - 1, ctx.original_height - 1

        results = []
        for idx in keep:
            bx1 = float(np.clip((x1[idx] - pad_x) / gain, 0, ow))
            by1 = float(np.clip((y1[idx] - pad_y) / gain, 0, oh))
            bx2 = float(np.clip((x2[idx] - pad_x) / gain, 0, ow))
            by2 = float(np.clip((y2[idx] - pad_y) / gain, 0, oh))

            keypoints = []
            if lmk_decoded is not None:
                for kp in lmk_decoded[idx].reshape(5, 2):
                    kx = float(np.clip((kp[0] - pad_x) / gain, 0, ow))
                    ky = float(np.clip((kp[1] - pad_y) / gain, 0, oh))
                    keypoints.append(Keypoint(x=kx, y=ky, confidence=1.0))

            results.append(FaceResult(
                box=[bx1, by1, bx2, by2],
                confidence=float(face_scores[idx]),
                class_id=0,
                keypoints=keypoints,
            ))
        return results

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[FaceResult]:
        """
        Process RetinaFace outputs.

        Auto-detects tensor roles by last dimension: 4=bbox, 2=score, 10=landmarks.
        """
        bbox_t, score_t, lmk_t = self._identify_tensors(outputs)
        if bbox_t is None or score_t is None:
            return []

        bbox_t, face_scores, lmk_t, priors = self._filter_by_score(bbox_t, score_t, lmk_t, self.priors)
        if face_scores.size == 0:
            return []

        x1, y1, x2, y2 = self._decode_boxes(bbox_t, priors)

        boxes_xywh = np.column_stack([x1, y1, x2 - x1, y2 - y1])
        indices = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(), face_scores.tolist(),
            self.score_threshold, self.nms_threshold)
        if len(indices) == 0:
            return []

        keep = np.array(indices).reshape(-1)
        lmk_decoded = self._decode_landmarks(lmk_t, priors)
        return self._build_results(keep, x1, y1, x2, y2, face_scores, lmk_decoded, ctx)

    @staticmethod
    def _softmax(x: np.ndarray) -> np.ndarray:
        """Row-wise softmax."""
        e = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return e / np.sum(e, axis=-1, keepdims=True)

    def get_model_name(self) -> str:
        return "retinaface"
