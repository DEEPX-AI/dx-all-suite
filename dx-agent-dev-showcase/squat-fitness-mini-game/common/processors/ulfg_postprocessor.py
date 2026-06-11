"""
ULFG (Ultra-Light-Fast-Generic) Face Detector Postprocessor

SSD-style lightweight face detection without keypoints.

Output format: 2 tensors
  - scores: [1, N, 2]  (background/face softmax)
  - boxes:  [1, N, 4]  (face bounding boxes)

Two variants:
  - With postprocessing:    boxes are decoded (normalized [x1, y1, x2, y2])
  - Without postprocessing: boxes are SSD deltas requiring prior decoding

Auto-detects format based on value range.
"""

import numpy as np
import cv2
from typing import List

from ..base import IPostprocessor, PreprocessContext
from .face_postprocessor import FaceResult


class ULFGPostprocessor(IPostprocessor):
    """
    Postprocessor for ULFG face detection (SSD-based, no landmarks).
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

        self.score_threshold = self.config.get('score_threshold', 0.7)
        self.nms_threshold = self.config.get('nms_threshold', 0.3)
        self.top_k = self.config.get('top_k', 200)
        # SSD prior variance for decoding anchor deltas
        self.variance = self.config.get('variance', [0.1, 0.2])
        # SSD prior box configuration for ULFG 320×240
        self._priors = None

    def _generate_priors(self):
        """Generate SSD prior boxes for ULFG face detector."""
        min_sizes_list = [[10, 16, 24], [32, 48], [64, 96], [128, 192, 256]]
        strides = [8, 16, 32, 64]
        priors = []
        for k, (min_sizes, stride) in enumerate(zip(min_sizes_list, strides)):
            fh = int(np.ceil(self.input_height / stride))
            fw = int(np.ceil(self.input_width / stride))
            for i in range(fh):
                for j in range(fw):
                    for min_size in min_sizes:
                        cx = (j + 0.5) * stride / self.input_width
                        cy = (i + 0.5) * stride / self.input_height
                        w = min_size / self.input_width
                        h = min_size / self.input_height
                        priors.append([cx, cy, w, h])
        return np.array(priors, dtype=np.float32)

    def _decode_ssd_deltas(self, boxes_raw):
        """Decode SSD-style anchor deltas to [x1, y1, x2, y2] in pixel coords."""
        if self._priors is None:
            self._priors = self._generate_priors()
        priors = self._priors
        n = min(len(boxes_raw), len(priors))
        boxes_raw = boxes_raw[:n]
        priors = priors[:n]

        cx = priors[:, 0] + boxes_raw[:, 0] * self.variance[0] * priors[:, 2]
        cy = priors[:, 1] + boxes_raw[:, 1] * self.variance[0] * priors[:, 3]
        w = priors[:, 2] * np.exp(boxes_raw[:, 2] * self.variance[1])
        h = priors[:, 3] * np.exp(boxes_raw[:, 3] * self.variance[1])

        x1 = (cx - w / 2) * self.input_width
        y1 = (cy - h / 2) * self.input_height
        x2 = (cx + w / 2) * self.input_width
        y2 = (cy + h / 2) * self.input_height
        return x1, y1, x2, y2

    def _identify_tensors(self, t0, t1):
        """Identify which tensor is scores and which is boxes."""
        if t0.ndim == 2 and t0.shape[-1] == 2:
            return t0, t1.reshape(-1, 4)
        if t1.ndim == 2 and t1.shape[-1] == 2:
            return t1, t0.reshape(-1, 4)
        if t0.ndim == 2 and t0.shape[-1] == 4:
            return t1.reshape(-1, 2), t0
        return t0.reshape(-1, 2), t1.reshape(-1, 4)

    def _decode_boxes(self, boxes_raw):
        """Convert boxes to pixel coordinates.

        Handles three formats:
        1. Normalized [x1,y1,x2,y2] in [0,1] → multiply by input dims
        2. Pixel [x1,y1,x2,y2] → pass through
        3. SSD deltas [dcx,dcy,dw,dh] → decode with prior boxes

        SSD deltas are detected when box values include negatives
        (normalized and pixel coords are non-negative for valid boxes).
        """
        # SSD delta detection: if many values are negative, these are anchor deltas
        neg_ratio = np.mean(boxes_raw < 0)
        if neg_ratio > 0.1:
            return self._decode_ssd_deltas(boxes_raw)

        if np.percentile(np.abs(boxes_raw), 95) < 2.0:
            return (
                boxes_raw[:, 0] * self.input_width,
                boxes_raw[:, 1] * self.input_height,
                boxes_raw[:, 2] * self.input_width,
                boxes_raw[:, 3] * self.input_height,
            )
        return boxes_raw[:, 0], boxes_raw[:, 1], boxes_raw[:, 2], boxes_raw[:, 3]

    def _apply_topk_nms(self, face_scores, x1, y1, x2, y2):
        """Apply top-K filtering and NMS, return keep indices."""
        if len(face_scores) > self.top_k:
            top_idx = np.argsort(face_scores)[::-1][:self.top_k]
            face_scores = face_scores[top_idx]
            x1, y1, x2, y2 = x1[top_idx], y1[top_idx], x2[top_idx], y2[top_idx]
        boxes_xywh = np.column_stack([x1, y1, x2 - x1, y2 - y1])
        indices = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(), face_scores.tolist(),
            self.score_threshold, self.nms_threshold)
        keep = np.array(indices).reshape(-1) if len(indices) > 0 else np.array([])
        return face_scores, x1, y1, x2, y2, keep

    def _scale_box(self, x1, y1, x2, y2, ctx):
        """Scale a single box back to original image coordinates."""
        if ctx.pad_x == 0 and ctx.pad_y == 0:
            # Use per-axis scale from preprocessor context for correct
            # inverse mapping (handles non-square resize like 320×240).
            if hasattr(ctx, 'scale_x') and hasattr(ctx, 'scale_y') and ctx.scale_x > 0 and ctx.scale_y > 0:
                sx = 1.0 / ctx.scale_x
                sy = 1.0 / ctx.scale_y
            else:
                sx = ctx.original_width / self.input_width
                sy = ctx.original_height / self.input_height
            return (
                np.clip(x1 * sx, 0, ctx.original_width - 1),
                np.clip(y1 * sy, 0, ctx.original_height - 1),
                np.clip(x2 * sx, 0, ctx.original_width - 1),
                np.clip(y2 * sy, 0, ctx.original_height - 1),
            )
        gain = max(ctx.scale, 1e-6)
        return (
            np.clip((x1 - ctx.pad_x) / gain, 0, ctx.original_width - 1),
            np.clip((y1 - ctx.pad_y) / gain, 0, ctx.original_height - 1),
            np.clip((x2 - ctx.pad_x) / gain, 0, ctx.original_width - 1),
            np.clip((y2 - ctx.pad_y) / gain, 0, ctx.original_height - 1),
        )

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[FaceResult]:
        """
        Process ULFG face detection outputs.

        Args:
            outputs: [scores, boxes] or [boxes, scores] — auto-detected
            ctx: Preprocessing context

        Returns:
            List of FaceResult (no keypoints)
        """
        t0 = np.squeeze(outputs[0])
        t1 = np.squeeze(outputs[1])

        scores_raw, boxes_raw = self._identify_tensors(t0, t1)

        n = min(scores_raw.shape[0], boxes_raw.shape[0])
        scores_raw = scores_raw[:n]
        boxes_raw = boxes_raw[:n]

        face_scores = scores_raw[:, 1] if (scores_raw.ndim == 2 and scores_raw.shape[-1] >= 2) else scores_raw.flatten()
        x1, y1, x2, y2 = self._decode_boxes(boxes_raw)

        mask = face_scores >= self.score_threshold
        if not np.any(mask):
            return []

        face_scores, x1, y1, x2, y2 = face_scores[mask], x1[mask], y1[mask], x2[mask], y2[mask]
        face_scores, x1, y1, x2, y2, keep = self._apply_topk_nms(face_scores, x1, y1, x2, y2)

        if len(keep) == 0:
            return []

        results = []
        for idx in keep:
            bx1, by1, bx2, by2 = self._scale_box(x1[idx], y1[idx], x2[idx], y2[idx], ctx)
            results.append(FaceResult(
                box=[float(bx1), float(by1), float(bx2), float(by2)],
                confidence=float(face_scores[idx]),
                class_id=0,
                keypoints=[],
            ))
        return results

    def get_model_name(self) -> str:
        return "ulfg"
