"""
Instance Segmentation Postprocessor

Unified postprocessor for YOLO-family instance segmentation models.
- YOLOv8-seg:  transposed output [1, C, N], no objectness score
- YOLO26-seg:  post-NMS output [1, N, C], score+class_id (not one-hot)
- YOLOv5-seg:  non-transposed output [1, N, C], objectness score

All use prototype masks from output[1] combined with per-detection mask coefficients.
Output format: List of InstanceSegResult with box, confidence, class_id, and per-instance mask.

Format auto-detection:
  shape[0] < shape[1]  → C×N, transpose needed (yolov8 pre-NMS)
  shape[0] > shape[1]  → N×C, no transpose
    non_mask_cols == 6  → post-NMS (score + class_id)
    non_mask_cols >  6  → pre-NMS with objectness (yolov5)

Backward-compatible aliases:
  YOLOv8InstanceSegPostprocessor = InstanceSegPostprocessor  (default: transposed=True, has_objectness=False)
  YOLOv5InstanceSegPostprocessor = InstanceSegPostprocessor(transposed=False, has_objectness=True)
"""

import numpy as np
import cv2
from functools import partial
from typing import List

from ..base import IPostprocessor, PreprocessContext, InstanceSegResult


class InstanceSegPostprocessor(IPostprocessor):
    """
    Unified YOLO instance segmentation postprocessor.

    Args:
      input_width / input_height: model input dimensions.
      transposed: True → output[0] is [1, 4+C+32, N] (v8/v26 style),
                  False → output[0] is [1, N, 4+1+C+32] (v5 style).
      has_objectness: True → index 4 is objectness, class scores start at 5 (v5 style),
                      False → no objectness, class scores start at 4 (v8 style).
      config: optional dict for score_threshold, nms_threshold, obj_threshold,
              num_classes, num_masks.
    """

    def __init__(self, input_width: int, input_height: int,
                 config: dict = None, *,
                 transposed: bool = True, has_objectness: bool = False):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.transposed = transposed
        self.has_objectness = has_objectness

        self.obj_threshold = self.config.get('obj_threshold', 0.25)
        self.score_threshold = self.config.get('score_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)
        self.num_classes = self.config.get('num_classes', 80)
        self.num_masks = self.config.get('num_masks', 32)
        self.max_detections = self.config.get('max_detections', 0)

    # ---- output alignment ------------------------------------------------
    def _align_outputs(self, outputs: List[np.ndarray]):
        """Identify detection and proto tensors by shape (like C++ align_tensors).

        Detection tensor: 3-D [1, C, N] or [1, N, C] where
            C == 4 + num_classes + num_masks.
        Proto tensor: 4-D [1, num_masks, H, W].

        Returns (detection_raw, proto_raw) with batch dim intact.
        """
        expected_det_c = 4 + self.num_classes + self.num_masks
        det_tensor = None
        proto_tensor = None

        for t in outputs:
            s = t.shape
            ndim = len(s)
            if ndim == 4 and (s[1] == self.num_masks or s[-1] == self.num_masks):
                proto_tensor = t
            elif ndim == 3 and (s[1] == expected_det_c or s[2] == expected_det_c):
                det_tensor = t

        # Fallback: use original order if shape matching failed
        if det_tensor is None:
            det_tensor = outputs[0]
        if proto_tensor is None and len(outputs) > 1:
            proto_tensor = outputs[1]

        return det_tensor, proto_tensor

    # ---- detection decode ------------------------------------------------
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[InstanceSegResult]:
        # 0) Robust output alignment (like C++ align_tensors)
        det_raw, proto_raw = self._align_outputs(outputs)

        # 1) Auto-detect format and transpose if needed
        squeezed = np.squeeze(det_raw)
        if squeezed.ndim < 2:
            return []

        need_transpose = squeezed.shape[0] < squeezed.shape[1]
        output = np.transpose(squeezed) if need_transpose else squeezed

        total_cols = output.shape[1]
        non_mask_cols = total_cols - self.num_masks
        post_nms = (non_mask_cols == 6 and not need_transpose)

        output, confidences, cls_ids, mask_coefs = self._parse_detections(output, non_mask_cols, post_nms)
        if output is None:
            return []

        if post_nms:
            # YOLO26 post-NMS: cols 0-3 are [x1, y1, x2, y2] already
            boxes_x1y1x2y2 = output[:, :4].copy()
        else:
            # Pre-NMS: cols 0-3 are [cx, cy, w, h] → convert to [x1, y1, x2, y2]
            boxes_cxcywh = output[:, :4]
            boxes_x1y1x2y2 = np.column_stack([
                boxes_cxcywh[:, 0] - boxes_cxcywh[:, 2] * 0.5,
                boxes_cxcywh[:, 1] - boxes_cxcywh[:, 3] * 0.5,
                boxes_cxcywh[:, 0] + boxes_cxcywh[:, 2] * 0.5,
                boxes_cxcywh[:, 1] + boxes_cxcywh[:, 3] * 0.5,
            ])

        # Defensive: some model variants output normalized coordinates (0..1)
        # while others output pixel coordinates. If values look normalized
        # (max <= 1.01) convert to input-pixel coordinates so downstream
        # mask resizing / cropping works correctly.
        if np.max(np.abs(boxes_x1y1x2y2)) <= 1.01 and self.input_width > 1 and self.input_height > 1:
            boxes_x1y1x2y2[:, 0] = boxes_x1y1x2y2[:, 0] * self.input_width
            boxes_x1y1x2y2[:, 2] = boxes_x1y1x2y2[:, 2] * self.input_width
            boxes_x1y1x2y2[:, 1] = boxes_x1y1x2y2[:, 1] * self.input_height
            boxes_x1y1x2y2[:, 3] = boxes_x1y1x2y2[:, 3] * self.input_height

        # Defensive: some model variants output normalized coordinates (0..1)
        # while others output pixel coordinates. If values look normalized
        # (max <= 1.01) convert to input-pixel coordinates so downstream
        # mask resizing / cropping works correctly.
        if np.max(np.abs(boxes_x1y1x2y2)) <= 1.01 and self.input_width > 1 and self.input_height > 1:
            boxes_x1y1x2y2[:, 0] = boxes_x1y1x2y2[:, 0] * self.input_width
            boxes_x1y1x2y2[:, 2] = boxes_x1y1x2y2[:, 2] * self.input_width
            boxes_x1y1x2y2[:, 1] = boxes_x1y1x2y2[:, 1] * self.input_height
            boxes_x1y1x2y2[:, 3] = boxes_x1y1x2y2[:, 3] * self.input_height

        # 3) NMS
        boxes_xywh = np.column_stack([
            boxes_x1y1x2y2[:, 0], boxes_x1y1x2y2[:, 1],
            boxes_x1y1x2y2[:, 2] - boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 3] - boxes_x1y1x2y2[:, 1],
        ])
        indices = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(), confidences.tolist(),
            self.score_threshold, self.nms_threshold,
        )
        if len(indices) == 0:
            return []
        keep = np.array(indices).reshape(-1)

        # 3-b) Limit to top-k detections by confidence
        if self.max_detections > 0 and len(keep) > self.max_detections:
            top_k = np.argsort(confidences[keep])[::-1][:self.max_detections]
            keep = keep[top_k]

        # 4) Generate, scale, and crop prototype masks
        scaled_masks = self._generate_scaled_masks(mask_coefs[keep], proto_raw, keep, boxes_x1y1x2y2)

        # 5) Convert to original coordinates
        gain = max(ctx.scale, 1e-6)
        pad_x, pad_y = ctx.pad_x, ctx.pad_y
        results = []
        for i, idx in enumerate(keep):
            box = boxes_x1y1x2y2[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)
            orig_mask = self._crop_mask_to_original(scaled_masks[i], ctx)
            results.append(InstanceSegResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(confidences[idx]),
                class_id=int(cls_ids[idx]),
                mask=(orig_mask > 0.5).astype(np.uint8),
            ))
        return results

    def _parse_detections(self, output, non_mask_cols, post_nms):
        """Parse detection tensor into (output, confidences, cls_ids, mask_coefs).

        Returns output (possibly filtered), or (None, None, None, None) if empty.
        """
        if post_nms:
            return output, output[:, 4], output[:, 5].astype(int), output[:, 6:]
        if self.has_objectness:
            obj_scores = output[:, 4]
            obj_mask = obj_scores >= self.obj_threshold
            if not np.any(obj_mask):
                return None, None, None, None
            output = output[obj_mask]
            obj_scores = obj_scores[obj_mask]
            actual_num_classes = non_mask_cols - 5
            cls_scores = output[:, 5:5 + actual_num_classes]
            cls_ids = np.argmax(cls_scores, axis=1)
            mask_coefs = output[:, 5 + actual_num_classes:]
            return output, obj_scores * np.max(cls_scores, axis=1), cls_ids, mask_coefs
        # yolov8-seg
        actual_num_classes = non_mask_cols - 4
        cls_scores = output[:, 4:4 + actual_num_classes]
        cls_ids = np.argmax(cls_scores, axis=1)
        mask_coefs = output[:, 4 + actual_num_classes:]
        return output, np.max(cls_scores, axis=1), cls_ids, mask_coefs

    def _generate_scaled_masks(self, kept_mask_coefs, proto_raw, keep, boxes_x1y1x2y2):
        """Generate sigmoid masks, upsample to input size, and crop to bboxes."""
        proto = np.squeeze(proto_raw)
        # Ensure NCHW layout: proto should be [C, H, W] where C == num_masks
        if proto.ndim == 3 and proto.shape[-1] == self.num_masks and proto.shape[0] != self.num_masks:
            proto = np.transpose(proto, (2, 0, 1))  # HWC → CHW
        c, mh, mw = proto.shape
        masks = 1.0 / (1.0 + np.exp(-(kept_mask_coefs @ proto.reshape(c, -1))))
        masks = masks.reshape(-1, mh, mw)

        scaled_masks = np.zeros((len(masks), self.input_height, self.input_width), dtype=np.float32)
        for i, mask in enumerate(masks):
            scaled_masks[i] = cv2.resize(mask, (self.input_width, self.input_height), interpolation=cv2.INTER_LINEAR)

        for i, box in enumerate(boxes_x1y1x2y2[keep][:, :4]):
            x1, y1, x2, y2 = box.astype(int)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(self.input_width, x2), min(self.input_height, y2)
            scaled_masks[i, :y1, :] = 0
            scaled_masks[i, y2:, :] = 0
            scaled_masks[i, :, :x1] = 0
            scaled_masks[i, :, x2:] = 0
        return scaled_masks

    def _crop_mask_to_original(self, mask_input, ctx) -> np.ndarray:
        """Remove letterbox padding from mask and resize to original image dimensions."""
        gain = max(ctx.scale, 1e-6)
        unpad_h = int(round(ctx.original_height * gain))
        unpad_w = int(round(ctx.original_width * gain))
        top, left = int(ctx.pad_y), int(ctx.pad_x)
        mask_crop = mask_input[top:top + unpad_h, left:left + unpad_w]
        if mask_crop.size > 0:
            return cv2.resize(mask_crop, (ctx.original_width, ctx.original_height), interpolation=cv2.INTER_LINEAR)
        return np.zeros((ctx.original_height, ctx.original_width), dtype=np.float32)

    def get_model_name(self) -> str:
        return "instance_seg"


# ---------------------------------------------------------------------------
# Backward-compatible aliases (drop-in replacements for existing factories)
# ---------------------------------------------------------------------------
class YOLOv8InstanceSegPostprocessor(InstanceSegPostprocessor):
    """YOLOv8/v26-seg — transposed, no objectness."""
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        super().__init__(input_width, input_height, config,
                         transposed=True, has_objectness=False)

    def get_model_name(self) -> str:
        return "yolov8seg"


class YOLOv5InstanceSegPostprocessor(InstanceSegPostprocessor):
    """YOLOv5-seg — non-transposed, objectness."""
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        super().__init__(input_width, input_height, config,
                         transposed=False, has_objectness=True)

    def get_model_name(self) -> str:
        return "yolov5seg"
