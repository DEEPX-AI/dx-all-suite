"""
CenterPose Postprocessor

CenterNet-based object 6-DoF pose estimation from multi-head heatmap outputs.

Output: 6 tensors at stride 4 (e.g. 128×128 for 512×512 input):
  - heatmap (hm):       [1, C, H/4, W/4]  object center heatmap (num_classes channels)
  - size (wh):          [1, 2, H/4, W/4]  bbox width/height regression
  - offset (reg):       [1, 2, H/4, W/4]  subpixel center offset
  - hps (kps):          [1, K*2, H/4, W/4]  keypoint offset from center
  - hm_hp:              [1, K, H/4, W/4]  keypoint heatmaps
  - hp_offset:          [1, 2, H/4, W/4]  keypoint subpixel offset

Tensors are auto-sorted by channel count to identify roles.
Keypoints: 8 for CenterPose (8 corners of 3D bounding box).
"""

import numpy as np
import cv2
from typing import List

from ..base import IPostprocessor, PreprocessContext, PoseResult, Keypoint


class CenterPosePostprocessor(IPostprocessor):
    """
    Postprocessor for CenterPose 6-DoF object pose estimation.

    Handles multi-head heatmap outputs with flexible tensor ordering.
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

        self.score_threshold = self.config.get('score_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.5)
        self.num_keypoints = self.config.get('num_keypoints', 8)
        self.top_k = self.config.get('top_k', 100)
        self.stride = self.config.get('stride', 4)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[PoseResult]:
        """
        Process CenterPose outputs.

        Args:
            outputs: 6 tensors (hm, wh, reg, hps, hm_hp, hp_offset)
            ctx: Preprocessing context

        Returns:
            List of PoseResult with 8 keypoints
        """
        squeezed = [np.squeeze(o) for o in outputs]
        heatmap, hps_tensor, hm_hp_tensor, wh_tensor, reg_tensor = self._identify_tensors(squeezed)

        if heatmap is None:
            return []

        # Auto-detect num_keypoints from tensor shapes if not explicitly set
        if hps_tensor is not None and hps_tensor.shape[0] != self.num_keypoints * 2:
            if hps_tensor.shape[0] % 2 == 0:
                self.num_keypoints = hps_tensor.shape[0] // 2

        # Apply sigmoid if heatmap values look like raw logits (values outside 0-1)
        if np.min(heatmap) < -0.1 or np.max(heatmap) > 1.1:
            heatmap = 1.0 / (1.0 + np.exp(-np.clip(heatmap, -50, 50)))

        feat_h, feat_w = heatmap.shape[1], heatmap.shape[2]
        hm_nms = self._heatmap_nms(heatmap)

        top_indices, top_scores, class_ids, ys, xs = self._decode_center_peaks(hm_nms, feat_h, feat_w)
        if len(top_indices) == 0:
            return []

        # Apply offset
        if reg_tensor is not None:
            cx = (xs.astype(np.float32) + reg_tensor[0, ys, xs]) * self.stride
            cy = (ys.astype(np.float32) + reg_tensor[1, ys, xs]) * self.stride
        else:
            cx = xs.astype(np.float32) * self.stride
            cy = ys.astype(np.float32) * self.stride

        # Get bbox size
        if wh_tensor is not None:
            w = wh_tensor[0, ys, xs] * self.stride
            h = wh_tensor[1, ys, xs] * self.stride
        else:
            w = np.full(len(xs), 50.0)
            h = np.full(len(xs), 50.0)

        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2

        keypoints_arr = self._decode_keypoints(xs, ys, cx, cy, w, hps_tensor, hm_hp_tensor, feat_h, feat_w)

        boxes_xywh = np.column_stack([x1, y1, w, h])
        indices = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(), top_scores.tolist(),
            self.score_threshold, self.nms_threshold)

        if len(indices) == 0:
            return []

        keep = np.array(indices).reshape(-1)
        return self._build_pose_results(keep, x1, y1, x2, y2, top_scores, class_ids, keypoints_arr, ctx)

    def _classify_multi_ch(self, tensors):
        """Assign heatmap, hps_tensor, hm_hp_tensor from multi-channel 3-D tensors.
        
        Strategy: sort by channel count descending. The tensor with most channels
        is hps (K*2), the second largest is hm_hp (K), and the smallest is heatmap (num_classes).
        """
        sorted_by_c = sorted(tensors, key=lambda t: t.shape[0], reverse=True)
        heatmap = hps_tensor = hm_hp_tensor = None
        
        if len(sorted_by_c) >= 3:
            hps_tensor = sorted_by_c[0]    # largest C
            hm_hp_tensor = sorted_by_c[1]  # second largest
            heatmap = sorted_by_c[2]       # smallest (num_classes)
        elif len(sorted_by_c) == 2:
            hps_tensor = sorted_by_c[0]
            heatmap = sorted_by_c[1]
        elif len(sorted_by_c) == 1:
            heatmap = sorted_by_c[0]
        
        return heatmap, hps_tensor, hm_hp_tensor

    def _classify_2ch(self, two_ch_tensors):
        """Assign wh_tensor, reg_tensor from 2-channel tensors sorted by magnitude."""
        if len(two_ch_tensors) >= 2:
            s = sorted(two_ch_tensors, key=lambda t: np.mean(np.abs(t)), reverse=True)
            return s[0], s[1]
        if len(two_ch_tensors) == 1:
            return two_ch_tensors[0], None
        return None, None

    def _identify_tensors(self, squeezed):
        """Identify and categorize CenterPose output tensors by channel count."""
        # Expand 2D tensors (e.g. squeezed [1,1,H,W] → [H,W]) back to [1,H,W]
        expanded = []
        for t in squeezed:
            if t.ndim == 2:
                expanded.append(t[np.newaxis, ...])  # [H,W] → [1,H,W]
            else:
                expanded.append(t)

        sorted_t = sorted(expanded, key=lambda t: t.shape[0] if t.ndim == 3 else 0, reverse=True)
        two_ch = [t for t in sorted_t if t.ndim == 3 and t.shape[0] == 2]
        multi_ch = [t for t in sorted_t if t.ndim == 3 and t.shape[0] != 2]
        if not multi_ch:
            return None, None, None, None, None
        heatmap, hps_tensor, hm_hp_tensor = self._classify_multi_ch(multi_ch)
        wh_tensor, reg_tensor = self._classify_2ch(two_ch)
        return heatmap, hps_tensor, hm_hp_tensor, wh_tensor, reg_tensor

    def _decode_center_peaks(self, hm_nms, feat_h, feat_w):
        """Find top-K heatmap peaks above the score threshold."""
        flat = hm_nms.reshape(-1)
        top_k = min(self.top_k, flat.size)
        top_indices = np.argpartition(flat, -top_k)[-top_k:]
        top_scores = flat[top_indices]

        valid = top_scores >= self.score_threshold
        top_indices = top_indices[valid]
        top_scores = top_scores[valid]

        class_ids = top_indices // (feat_h * feat_w)
        spatial_idx = top_indices % (feat_h * feat_w)
        ys = spatial_idx // feat_w
        xs = spatial_idx % feat_w
        return top_indices, top_scores, class_ids, ys, xs

    def _decode_keypoints(self, xs, ys, cx, cy, w, hps_tensor, hm_hp_tensor, feat_h, feat_w):
        """Decode keypoints from hps offsets and optionally refine with hm_hp."""
        keypoints_arr = np.zeros((len(xs), self.num_keypoints, 2), dtype=np.float32)
        if hps_tensor is not None:
            for ki in range(self.num_keypoints):
                dx_idx, dy_idx = ki * 2, ki * 2 + 1
                if dx_idx < hps_tensor.shape[0] and dy_idx < hps_tensor.shape[0]:
                    keypoints_arr[:, ki, 0] = cx + hps_tensor[dx_idx, ys, xs] * self.stride
                    keypoints_arr[:, ki, 1] = cy + hps_tensor[dy_idx, ys, xs] * self.stride
        if hm_hp_tensor is not None:
            self._refine_keypoints_with_hm_hp(keypoints_arr, xs, ys, w, hm_hp_tensor, feat_h, feat_w)
        return keypoints_arr

    def _refine_keypoints_with_hm_hp(self, keypoints_arr, xs, ys, w, hm_hp_tensor, feat_h, feat_w):
        """Refine keypoint positions using per-keypoint heatmap peaks."""
        for ki in range(min(self.num_keypoints, hm_hp_tensor.shape[0])):
            kp_hm_nms = self._heatmap_nms_2d(hm_hp_tensor[ki])
            for di in range(len(xs)):
                search_r = max(2, int(w[di] / self.stride / 2))
                cy_i, cx_i = int(ys[di]), int(xs[di])
                r_y1, r_y2 = max(0, cy_i - search_r), min(feat_h, cy_i + search_r + 1)
                r_x1, r_x2 = max(0, cx_i - search_r), min(feat_w, cx_i + search_r + 1)
                region = kp_hm_nms[r_y1:r_y2, r_x1:r_x2]
                if region.size > 0 and np.max(region) > 0.1:
                    peak = np.unravel_index(np.argmax(region), region.shape)
                    keypoints_arr[di, ki, 0] = (peak[1] + r_x1) * self.stride
                    keypoints_arr[di, ki, 1] = (peak[0] + r_y1) * self.stride

    def _build_pose_results(self, keep, x1, y1, x2, y2, top_scores, class_ids, keypoints_arr, ctx):
        """Scale detected poses to original image coordinates and build result list."""
        gain = max(ctx.scale, 1e-6)
        pad_x, pad_y = ctx.pad_x, ctx.pad_y
        results = []
        for idx in keep:
            bx1 = np.clip((x1[idx] - pad_x) / gain, 0, ctx.original_width - 1)
            by1 = np.clip((y1[idx] - pad_y) / gain, 0, ctx.original_height - 1)
            bx2 = np.clip((x2[idx] - pad_x) / gain, 0, ctx.original_width - 1)
            by2 = np.clip((y2[idx] - pad_y) / gain, 0, ctx.original_height - 1)
            keypoints = []
            for ki in range(self.num_keypoints):
                kp_x = np.clip((keypoints_arr[idx, ki, 0] - pad_x) / gain, 0, ctx.original_width - 1)
                kp_y = np.clip((keypoints_arr[idx, ki, 1] - pad_y) / gain, 0, ctx.original_height - 1)
                keypoints.append(Keypoint(x=float(kp_x), y=float(kp_y), confidence=1.0))
            results.append(PoseResult(
                box=[float(bx1), float(by1), float(bx2), float(by2)],
                confidence=float(top_scores[idx]),
                class_id=int(class_ids[idx]),
                class_name="",
                keypoints=keypoints,
            ))
        return results

    def _heatmap_nms(self, heatmap: np.ndarray, kernel: int = 3) -> np.ndarray:
        """Apply 3×3 max-pool NMS on multi-channel heatmap [C, H, W]."""
        result = np.zeros_like(heatmap)
        pad = kernel // 2
        for c in range(heatmap.shape[0]):
            padded = np.pad(heatmap[c], pad, mode='constant', constant_values=-1)
            maxpool = np.zeros_like(heatmap[c])
            for dy in range(-pad, pad + 1):
                for dx in range(-pad, pad + 1):
                    h, w = heatmap.shape[1], heatmap.shape[2]
                    maxpool = np.maximum(maxpool,
                                          padded[pad + dy:pad + dy + h, pad + dx:pad + dx + w])
            result[c] = heatmap[c] * (heatmap[c] == maxpool)
        return result

    @staticmethod
    def _heatmap_nms_2d(hm: np.ndarray, kernel: int = 3) -> np.ndarray:
        """Apply 3×3 max-pool on single-channel heatmap [H, W]."""
        pad = kernel // 2
        padded = np.pad(hm, pad, mode='constant', constant_values=-1)
        maxpool = np.zeros_like(hm)
        for dy in range(-pad, pad + 1):
            for dx in range(-pad, pad + 1):
                h, w = hm.shape
                maxpool = np.maximum(maxpool, padded[pad + dy:pad + dy + h, pad + dx:pad + dx + w])
        return hm * (hm == maxpool)

    def get_model_name(self) -> str:
        return "centerpose"
