"""
CenterNet Postprocessor

Handles CenterNet keypoint-based detection models.
CenterNet outputs 3 heatmap-based tensors:
  - output[0]: [1, 2, H/4, W/4]   size (w, h) regression
  - output[1]: [1, 2, H/4, W/4]   center offset (dx, dy)
  - output[2]: [1, C, H/4, W/4]   center heatmap (class-wise, after relu/sigmoid)

The postprocessor decodes center points from heatmap peaks, then
applies offset correction and reads the bounding box size.

Stride = 4 (feature_map_size = input_size / 4)
"""

import numpy as np
import cv2
from typing import List

from ..base import IPostprocessor, DetectionResult, PreprocessContext


class CenterNetPostprocessor(IPostprocessor):
    """
    Postprocessor for CenterNet (Objects as Points) detection models.

    Supports the standard 3-output format:
      outputs sorted by channel count → heatmap (C channels), size (2ch), offset (2ch)
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

        self.score_threshold = self.config.get('score_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.5)
        self.num_classes = self.config.get('num_classes', 80)
        self.top_k = self.config.get('top_k', 100)
        self.stride = self.config.get('stride', 4)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        """
        Process CenterNet outputs.

        Args:
            outputs: 3 tensors — heatmap, size, offset (order auto-detected by channels)
            ctx: Preprocessing context

        Returns:
            List of DetectionResult
        """
        # Sort outputs to identify: heatmap (C ch), size (2ch), offset (2ch)
        squeezed = [np.squeeze(o) for o in outputs]

        heatmap = None
        size_tensor = None
        offset_tensor = None

        # Heatmap has the most channels (num_classes); size and offset have 2 channels each
        # Sort by channel count descending
        sorted_by_ch = sorted(squeezed, key=lambda t: t.shape[0], reverse=True)

        heatmap = sorted_by_ch[0]  # [C, H, W] — most channels
        # The remaining two both have 2 channels; size values are typically larger
        t1, t2 = sorted_by_ch[1], sorted_by_ch[2]
        if np.mean(np.abs(t1)) > np.mean(np.abs(t2)):
            size_tensor = t1   # [2, H, W] — w, h (larger values)
            offset_tensor = t2  # [2, H, W] — dx, dy (small corrections)
        else:
            size_tensor = t2
            offset_tensor = t1

        num_classes = heatmap.shape[0]
        feat_h, feat_w = heatmap.shape[1], heatmap.shape[2]

        # 1. Pseudo-NMS on heatmap: keep only local maxima (3x3 max pool)
        heatmap_max = np.zeros_like(heatmap)
        for c in range(num_classes):
            # Max pooling with kernel 3
            padded = np.pad(heatmap[c], 1, mode='constant', constant_values=-1)
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    heatmap_max[c] = np.maximum(
                        heatmap_max[c],
                        padded[1+dy:1+dy+feat_h, 1+dx:1+dx+feat_w]
                    )
        # Keep only peaks
        keep_mask = (heatmap == heatmap_max)
        heatmap = heatmap * keep_mask

        # 2. Find top-K scores across all classes
        flat = heatmap.reshape(-1)
        top_k = min(self.top_k, flat.size)
        top_indices = np.argpartition(flat, -top_k)[-top_k:]
        top_scores = flat[top_indices]

        # Filter by threshold
        valid = top_scores >= self.score_threshold
        top_indices = top_indices[valid]
        top_scores = top_scores[valid]

        if len(top_indices) == 0:
            return []

        # Decode indices → (class_id, y, x)
        class_ids = top_indices // (feat_h * feat_w)
        spatial_idx = top_indices % (feat_h * feat_w)
        ys = spatial_idx // feat_w
        xs = spatial_idx % feat_w

        # 3. Apply offset and size
        cx = (xs.astype(np.float32) + offset_tensor[0, ys, xs]) * self.stride
        cy = (ys.astype(np.float32) + offset_tensor[1, ys, xs]) * self.stride
        w = size_tensor[0, ys, xs] * self.stride
        h = size_tensor[1, ys, xs] * self.stride

        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2

        # 4. NMS
        boxes_xywh = np.column_stack([x1, y1, w, h])
        indices = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(),
            top_scores.tolist(),
            self.score_threshold,
            self.nms_threshold,
        )

        if len(indices) == 0:
            return []

        keep = np.array(indices).reshape(-1)

        # 5. Scale back to original coordinates
        gain = max(ctx.scale, 1e-6)
        pad_x = ctx.pad_x
        pad_y = ctx.pad_y

        results = []
        for idx in keep:
            bx1 = np.clip((x1[idx] - pad_x) / gain, 0, ctx.original_width - 1)
            by1 = np.clip((y1[idx] - pad_y) / gain, 0, ctx.original_height - 1)
            bx2 = np.clip((x2[idx] - pad_x) / gain, 0, ctx.original_width - 1)
            by2 = np.clip((y2[idx] - pad_y) / gain, 0, ctx.original_height - 1)

            results.append(DetectionResult(
                box=[float(bx1), float(by1), float(bx2), float(by2)],
                confidence=float(top_scores[idx]),
                class_id=int(class_ids[idx]),
            ))

        return results

    def get_model_name(self) -> str:
        return "centernet"
