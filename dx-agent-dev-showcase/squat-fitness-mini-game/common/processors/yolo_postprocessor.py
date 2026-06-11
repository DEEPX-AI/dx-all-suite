"""
YOLO Family Postprocessors

Supports different YOLO architectures:
- YOLOv5Postprocessor: YOLOv5, YOLOv7, YOLOX (with objectness score)
- YOLOv8Postprocessor: YOLOv8, YOLOv9, YOLOv10, YOLOv11, YOLOv12 (no objectness)
- YOLOXPostprocessor: YOLOX specific (same as YOLOv5 format)
"""

import numpy as np
import cv2
from typing import List, Any

from ..base import IPostprocessor, PreprocessContext, DetectionResult
from .nms_utils import cxcywh_to_x1y1x2y2 as _cxcywh_to_x1y1x2y2
from .nms_utils import nms as _nms_impl


def _nms(boxes, scores, class_ids, conf_threshold, nms_threshold):
    return _nms_impl(boxes, scores, class_ids, conf_threshold, nms_threshold)


class YOLOv5Postprocessor(IPostprocessor):
    """
    Postprocessor for YOLOv5/YOLOv7/YOLOX style outputs.
    
    Output format (ORT/single-tensor): [1, N, 5+num_classes]
      - [x, y, w, h, objectness, class_scores...] (already decoded)
    
    Output format (NPU/multi-tensor): 3 tensors of [1, C, H, W]
      - C = num_anchors * (5 + num_classes), e.g. 255 for COCO
      - Raw logits, need sigmoid + anchor/grid decode
    """
    
    # Standard YOLOv5 COCO anchors per stride
    ANCHORS = {
        8:  [(10, 13), (16, 30), (33, 23)],
        16: [(30, 61), (62, 45), (59, 119)],
        32: [(116, 90), (156, 198), (373, 326)],
    }
    STRIDES = [8, 16, 32]
    
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        
        self.obj_threshold = self.config.get('obj_threshold', 0.25)
        self.conf_threshold = self.config.get('conf_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)
        self.num_classes = self.config.get('num_classes', 80)

        # Allow per-model anchor/stride override via config
        custom_anchors = self.config.get('anchors', None)
        if custom_anchors is not None:
            self.ANCHORS = custom_anchors
        custom_strides = self.config.get('strides', None)
        if custom_strides is not None:
            self.STRIDES = custom_strides
    
    @staticmethod
    def _sigmoid(x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))
    
    def _decode_multi_scale_outputs(self, outputs: list) -> np.ndarray:
        """
        Decode 3-tensor NPU outputs with anchor-based grid decoding.
        
        Each tensor: [1, num_anchors*(5+C), grid_h, grid_w]  (NCHW, raw logits)
        
        Decoding (YOLOv5 standard):
          cx = (sigmoid(tx)*2 - 0.5 + grid_x) * stride
          cy = (sigmoid(ty)*2 - 0.5 + grid_y) * stride
          w  = (sigmoid(tw)*2)^2 * anchor_w
          h  = (sigmoid(th)*2)^2 * anchor_h
          obj = sigmoid(obj_logit)
          cls = sigmoid(cls_logit)
          conf = obj * cls
        
        Returns:
            np.ndarray of shape [N, 5+num_classes] (decoded, post-sigmoid)
        """
        num_fields = 5 + self.num_classes  # 85 for COCO
        num_anchors = 3
        
        # Sort tensors by spatial size descending (stride 8 first)
        # Use max of the two middle dims to handle both NCHW and NHWC
        def _spatial_size(t):
            s = t.squeeze().shape
            return max(s[0], s[-1]) * max(s[0], s[-1])
        sorted_outputs = sorted(outputs, key=lambda t: t.size, reverse=True)
        
        all_detections = []
        
        for scale_idx, tensor in enumerate(sorted_outputs):
            data = np.squeeze(tensor)  # [C, H, W] or [H, W, C]
            
            # Detect NHWC layout and transpose to NCHW
            if data.shape[0] == num_anchors * num_fields:
                pass  # Already NCHW: [C, H, W]
            elif data.shape[-1] == num_anchors * num_fields:
                data = data.transpose(2, 0, 1)  # NHWC → NCHW: [H, W, C] → [C, H, W]
            
            grid_h, grid_w = data.shape[1], data.shape[2]
            # Compute stride from input size and grid size
            stride = self.input_height // grid_h
            if stride not in self.ANCHORS:
                continue  # skip scales without matching anchors (e.g. P6)
            anchors = self.ANCHORS[stride]
            
            # Reshape to [num_anchors, num_fields, grid_h, grid_w]
            data = data.reshape(num_anchors, num_fields, grid_h, grid_w)
            
            # Build grid
            gx = np.arange(grid_w, dtype=np.float32).reshape(1, 1, 1, grid_w)
            gy = np.arange(grid_h, dtype=np.float32).reshape(1, 1, grid_h, 1)
            
            # Decode boxes
            tx = self._sigmoid(data[:, 0:1, :, :])  # [A, 1, H, W]
            ty = self._sigmoid(data[:, 1:2, :, :])
            tw = self._sigmoid(data[:, 2:3, :, :])
            th = self._sigmoid(data[:, 3:4, :, :])
            
            cx = (tx * 2.0 - 0.5 + gx) * stride
            cy = (ty * 2.0 - 0.5 + gy) * stride
            
            # Anchor scaling
            anchor_w = np.array([a[0] for a in anchors], dtype=np.float32).reshape(num_anchors, 1, 1, 1)
            anchor_h = np.array([a[1] for a in anchors], dtype=np.float32).reshape(num_anchors, 1, 1, 1)
            w = (tw * 2.0) ** 2 * anchor_w
            h = (th * 2.0) ** 2 * anchor_h
            
            # Objectness and class scores
            obj = self._sigmoid(data[:, 4:5, :, :])               # [A, 1, H, W]
            cls = self._sigmoid(data[:, 5:5+self.num_classes, :, :])  # [A, C, H, W]
            
            # Reshape to [A*H*W, fields]
            # Note: cx/cy/w/h/obj have middle dim=1 so reshape is unambiguous.
            # cls has shape [A, C, H, W] — must transpose to [A, H, W, C] first
            # so that the class dimension becomes the last axis before flattening.
            n = num_anchors * grid_h * grid_w
            cx_flat = cx.reshape(n, 1)
            cy_flat = cy.reshape(n, 1)
            w_flat = w.reshape(n, 1)
            h_flat = h.reshape(n, 1)
            obj_flat = obj.reshape(n, 1)
            cls_flat = cls.transpose(0, 2, 3, 1).reshape(n, self.num_classes)
            
            # Stack: [cx, cy, w, h, obj, cls_scores...]
            scale_det = np.concatenate([cx_flat, cy_flat, w_flat, h_flat, obj_flat, cls_flat], axis=1)
            all_detections.append(scale_det)
        
        return np.concatenate(all_detections, axis=0)  # [N_total, 5+C]
    
    def _decode_raw_multi_scale(self, outputs: list) -> np.ndarray:
        """Decode [1, A, H, W, C] raw YOLOv5 feature maps with anchor-based grid decoding."""
        num_fields = 5 + self.num_classes
        # Sort by spatial size descending (stride 8 first = largest H*W)
        sorted_outputs = sorted(outputs, key=lambda t: t.shape[2] * t.shape[3], reverse=True)

        all_detections = []
        for scale_idx, tensor in enumerate(sorted_outputs):
            data = tensor[0]  # [A, H, W, C]
            num_anchors = data.shape[0]
            grid_h, grid_w = data.shape[1], data.shape[2]
            # Compute stride from input size and grid size
            stride = self.input_height // grid_h
            if stride not in self.ANCHORS:
                continue  # skip scales without matching anchors (e.g. P6)
            anchors = self.ANCHORS[stride]

            # Transpose to [A, C, H, W] for consistent processing
            data = data.transpose(0, 3, 1, 2)  # [A, C, H, W]

            gx = np.arange(grid_w, dtype=np.float32).reshape(1, 1, 1, grid_w)
            gy = np.arange(grid_h, dtype=np.float32).reshape(1, 1, grid_h, 1)

            tx = self._sigmoid(data[:, 0:1, :, :])
            ty = self._sigmoid(data[:, 1:2, :, :])
            tw = self._sigmoid(data[:, 2:3, :, :])
            th = self._sigmoid(data[:, 3:4, :, :])

            cx = (tx * 2.0 - 0.5 + gx) * stride
            cy = (ty * 2.0 - 0.5 + gy) * stride

            anchor_w = np.array([a[0] for a in anchors], dtype=np.float32).reshape(num_anchors, 1, 1, 1)
            anchor_h = np.array([a[1] for a in anchors], dtype=np.float32).reshape(num_anchors, 1, 1, 1)
            w = (tw * 2.0) ** 2 * anchor_w
            h = (th * 2.0) ** 2 * anchor_h

            obj = self._sigmoid(data[:, 4:5, :, :])
            cls = self._sigmoid(data[:, 5:5+self.num_classes, :, :])

            n = num_anchors * grid_h * grid_w
            cx_flat = cx.reshape(n, 1)
            cy_flat = cy.reshape(n, 1)
            w_flat = w.reshape(n, 1)
            h_flat = h.reshape(n, 1)
            obj_flat = obj.reshape(n, 1)
            cls_flat = cls.transpose(0, 2, 3, 1).reshape(n, self.num_classes)

            scale_det = np.concatenate([cx_flat, cy_flat, w_flat, h_flat, obj_flat, cls_flat], axis=1)
            all_detections.append(scale_det)

        return np.concatenate(all_detections, axis=0)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        """
        Process YOLOv5-style outputs.
        
        Args:
            outputs: Single tensor [1, N, 5+num_classes] (ORT mode)
                     or 3 tensors [1, C, H, W] each (NPU mode)
                     or 2 tensors: boxes [1, N, (1,) 4] + confs [1, N, C] (YOLOv4 etc.)
            ctx: Preprocessing context
            
        Returns:
            List of DetectionResult objects
        """
        # Detect multi-scale NPU output (3+ tensors with 4D shape)
        if len(outputs) >= 3 and all(o.ndim == 4 for o in outputs):
            output = self._decode_multi_scale_outputs(outputs)
        elif len(outputs) >= 2 and all(o.ndim == 5 for o in outputs):
            first = outputs[0]
            # [1, A, H, W, C] raw YOLOv5 format (A=num_anchors, C=5+num_classes)
            if first.shape[1] == 3 and first.shape[-1] == (5 + self.num_classes):
                output = self._decode_raw_multi_scale(outputs)
            else:
                # YOLOv4 DarkNet format: [1, H, W, num_anchors, 5+C] already decoded
                parts = [o.reshape(-1, o.shape[-1]) for o in outputs]
                output = np.concatenate(parts, axis=0)
        elif len(outputs) == 2:
            # 2-tensor format: separate boxes + confs (e.g. YOLOv4 TFLite)
            return self._process_separate_boxes_confs(outputs, ctx)
        else:
            output = np.squeeze(outputs[0])
        
        # Filter by objectness
        obj_scores = output[:, 4]
        obj_mask = obj_scores >= self.obj_threshold
        
        if not np.any(obj_mask):
            return []
        
        filtered = output[obj_mask]
        filtered_obj = obj_scores[obj_mask]
        
        # Class scores
        cls_scores = filtered[:, 5:5+self.num_classes]
        cls_max_scores = np.max(cls_scores, axis=1)
        cls_ids = np.argmax(cls_scores, axis=1)
        
        # Final confidence
        confidences = filtered_obj * cls_max_scores
        
        # Box conversion (center to corner)
        boxes = _cxcywh_to_x1y1x2y2(filtered[:, :4])
        
        # NMS
        indices = _nms(boxes, confidences, cls_ids, self.conf_threshold, self.nms_threshold)
        
        if len(indices) == 0:
            return []
        
        # Convert to original coordinates and create results
        results = []
        gain = max(ctx.scale, 1e-6)
        pad_x = ctx.pad_x
        pad_y = ctx.pad_y
        
        for idx in indices:
            box = boxes[idx].copy()
            # Restore to original coordinates
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)
            
            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(confidences[idx]),
                class_id=int(cls_ids[idx])
            ))
        
        return results
    
    def get_model_name(self) -> str:
        return "yolov5"

    def _process_separate_boxes_confs(
        self, outputs: List[np.ndarray], ctx: PreprocessContext
    ) -> List[DetectionResult]:
        """
        Handle 2-tensor YOLO outputs with separate boxes and class-confs.
        E.g. YOLOv4 TFLite: boxes [1, N, (1,) 4] + confs [1, N, C]
        No objectness column — class conf is the final score.
        """
        # Identify boxes vs confs by last dimension
        a = outputs[0].squeeze()
        b = outputs[1].squeeze()
        # The tensor whose last dim is 4 is boxes
        if a.shape[-1] == 4:
            boxes_raw = a.reshape(-1, 4)
            confs_raw = b.reshape(boxes_raw.shape[0], -1)
        elif b.shape[-1] == 4:
            boxes_raw = b.reshape(-1, 4)
            confs_raw = a.reshape(boxes_raw.shape[0], -1)
        else:
            # Last resort: smaller last-dim → boxes
            if a.shape[-1] < b.shape[-1]:
                boxes_raw = a.reshape(-1, a.shape[-1])
                confs_raw = b.reshape(boxes_raw.shape[0], -1)
            else:
                boxes_raw = b.reshape(-1, b.shape[-1])
                confs_raw = a.reshape(boxes_raw.shape[0], -1)

        cls_max_scores = np.max(confs_raw, axis=1)
        cls_ids = np.argmax(confs_raw, axis=1)

        mask = cls_max_scores >= self.conf_threshold
        if not np.any(mask):
            return []

        filtered_boxes = boxes_raw[mask]
        filtered_scores = cls_max_scores[mask]
        filtered_cls_ids = cls_ids[mask]

        # Auto-detect box format
        box_format = self.config.get('box_format', 'auto')
        if box_format == 'xyxy':
            boxes = filtered_boxes.copy()
        elif box_format == 'cxcywh':
            boxes = _cxcywh_to_x1y1x2y2(filtered_boxes)
        else:
            # Heuristic: in x1y1x2y2, col2 > col0 and col3 > col1 for most boxes
            frac_x2_gt_x1 = np.mean(filtered_boxes[:, 2] > filtered_boxes[:, 0])
            frac_y2_gt_y1 = np.mean(filtered_boxes[:, 3] > filtered_boxes[:, 1])
            if frac_x2_gt_x1 > 0.8 and frac_y2_gt_y1 > 0.8:
                boxes = filtered_boxes.copy()  # already x1y1x2y2
            else:
                boxes = _cxcywh_to_x1y1x2y2(filtered_boxes)

        # If normalised (values mostly 0-1), scale to input dims
        if np.percentile(np.abs(boxes), 95) < 2.0:
            boxes[:, [0, 2]] *= self.input_width
            boxes[:, [1, 3]] *= self.input_height

        indices = _nms(boxes, filtered_scores, filtered_cls_ids, self.conf_threshold, self.nms_threshold)
        if not indices:
            return []

        # Use per-axis scale when available (SimpleResizePreprocessor),
        # fall back to uniform scale+pad (LetterboxPreprocessor).
        scale_x = getattr(ctx, 'scale_x', 0) or max(ctx.scale, 1e-6)
        scale_y = getattr(ctx, 'scale_y', 0) or max(ctx.scale, 1e-6)
        pad_x = ctx.pad_x
        pad_y = ctx.pad_y
        results = []
        for idx in indices:
            box = boxes[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / scale_x, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / scale_y, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / scale_x, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / scale_y, 0, ctx.original_height - 1)
            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(filtered_scores[idx]),
                class_id=int(filtered_cls_ids[idx]),
            ))
        return results


class YOLOv8Postprocessor(IPostprocessor):
    """
    Postprocessor for YOLOv8/v9/v10/v11/v12 style outputs.
    
    Output format: [4+num_classes, N] (transposed)
    - No objectness score
    - class_scores directly used as confidence
    """
    
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        
        self.conf_threshold = self.config.get('conf_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)
        self.num_classes = self.config.get('num_classes', 80)
    
    def _decode_multi_scale_outputs(self, outputs: List[np.ndarray]) -> np.ndarray:
        """
        Decode 6-tensor DFL outputs (ort_off mode) into fused [4+C, N] tensor.
        
        When ORT is disabled, the model outputs 6 separate tensors:
        3 classification heads (channels=num_classes) and 3 regression heads (channels=64).
        This method applies DFL (Distribution Focal Loss) softmax decoding and
        anchor-point reconstruction to produce the same format as the fused single-tensor output.
        
        Args:
            outputs: List of 6 numpy arrays from multi-scale heads
            
        Returns:
            Fused tensor of shape [1, 4+num_classes, N]
        """
        cls_outputs = sorted(
            [t for t in outputs if t.shape[1] == self.num_classes],
            key=lambda x: x.shape[2],
            reverse=True,
        )
        reg_outputs = sorted(
            [t for t in outputs if t.shape[1] == 64],
            key=lambda x: x.shape[2],
            reverse=True,
        )
        
        # Concat class scores: [1, C, N_total]
        class_scores = np.concatenate(
            [t.reshape(1, self.num_classes, -1) for t in cls_outputs], axis=2
        )
        
        # DFL decode regression outputs
        dfl_weights = np.arange(16, dtype=np.float32).reshape(1, 1, 16, 1)
        reg_list = []
        for reg_t in reg_outputs:
            reg_reshaped = reg_t.reshape(1, 4, 16, -1)
            max_val = np.max(reg_reshaped, axis=2, keepdims=True)
            exp_val = np.exp(reg_reshaped - max_val)
            softmax_val = exp_val / np.sum(exp_val, axis=2, keepdims=True)
            reg_list.append(np.sum(softmax_val * dfl_weights, axis=2))
        predicted_distances = np.concatenate(reg_list, axis=2)
        
        # Convert distances to cxcywh
        dist_tl = predicted_distances[:, 0:2, :]
        dist_br = predicted_distances[:, 2:4, :]
        relative_wh = dist_tl + dist_br
        relative_cxcy = (dist_br - dist_tl) / 2.0
        relative_cxcywh = np.concatenate([relative_cxcy, relative_wh], axis=1)
        
        # Build anchor points
        strides = [8, 16, 32]
        grid_shapes = [(self.input_height // s, self.input_width // s) for s in strides]
        anchor_points_list = []
        stride_tensor_list = []
        for i, stride in enumerate(strides):
            h, w = grid_shapes[i]
            x = np.arange(0, w) + 0.5
            y = np.arange(0, h) + 0.5
            xv, yv = np.meshgrid(x, y)
            grid = np.stack((xv, yv), 2).reshape(-1, 2).T
            anchor_points_list.append(grid)
            stride_tensor_list.append(np.full((1, h * w), stride))
        
        anchor_points = np.concatenate(anchor_points_list, axis=1).reshape(1, 2, -1)
        stride_tensor = np.concatenate(stride_tensor_list, axis=1).reshape(1, 1, -1)
        
        final_cxcy = (relative_cxcywh[:, 0:2, :] + anchor_points) * stride_tensor
        final_wh = relative_cxcywh[:, 2:4, :] * stride_tensor
        
        return np.concatenate([final_cxcy, final_wh, class_scores], axis=1)
    
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        """
        Process YOLOv8-style outputs.
        
        Args:
            outputs: Model outputs [1, 4+num_classes, N] (single tensor)
                     or 6 tensors (3 cls + 3 reg) when ORT is off
                     or [1, 300, 6] end-to-end output (v10/v26)
            ctx: Preprocessing context
            
        Returns:
            List of DetectionResult objects
        """
        # End-to-end output detection: [1, 300, 6] = [x1, y1, x2, y2, score, class_id]
        first = np.squeeze(outputs[0])
        if len(outputs) == 1 and first.ndim == 2 and first.shape[-1] == 6:
            return self._process_end_to_end(first, ctx)
        
        # Handle multi-scale outputs (ort_off mode: 6 tensors)
        if len(outputs) == 6:
            fused = self._decode_multi_scale_outputs(outputs)
            output = np.transpose(np.squeeze(fused))
        else:
            # Single fused tensor: [4+C, N] -> [N, 4+C]
            output = np.transpose(np.squeeze(outputs[0]))
        
        # Extract class scores (no objectness in v8+)
        cls_scores = output[:, 4:4+self.num_classes]
        cls_max_scores = np.max(cls_scores, axis=1)
        cls_ids = np.argmax(cls_scores, axis=1)
        
        # Box conversion
        boxes = _cxcywh_to_x1y1x2y2(output[:, :4])
        
        # NMS
        indices = _nms(boxes, cls_max_scores, cls_ids, self.conf_threshold, self.nms_threshold)
        
        if len(indices) == 0:
            return []
        
        # Convert to original coordinates
        results = []
        gain = max(ctx.scale, 1e-6)
        pad_x = ctx.pad_x
        pad_y = ctx.pad_y
        
        for idx in indices:
            box = boxes[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)
            
            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(cls_max_scores[idx]),
                class_id=int(cls_ids[idx])
            ))
        
        return results
    
    def _process_end_to_end(self, output: np.ndarray, ctx: PreprocessContext) -> List[DetectionResult]:
        """
        Process end-to-end output [N, 6] = [x1, y1, x2, y2, score, class_id].
        
        Used by YOLOv10/YOLOv26 models that output already-decoded detections.
        Values are in input-space coordinates; no sigmoid/DFL/anchor decode needed.
        Only score thresholding and coordinate rescaling are applied.
        """
        # Score filter
        scores = output[:, 4]
        mask = scores >= self.conf_threshold
        if not np.any(mask):
            return []
        
        filtered = output[mask]
        
        # Coordinates are already x1,y1,x2,y2 in input space
        boxes = filtered[:, :4]
        scores_f = filtered[:, 4]
        class_ids = filtered[:, 5].astype(np.int32)
        
        # NMS (some end-to-end models may already have NMS, but apply for safety)
        indices = _nms(boxes, scores_f, class_ids, self.conf_threshold, self.nms_threshold)
        if len(indices) == 0:
            return []
        
        # Convert to original coordinates
        results = []
        gain = max(ctx.scale, 1e-6)
        pad_x = ctx.pad_x
        pad_y = ctx.pad_y
        
        for idx in indices:
            box = boxes[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)
            
            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(scores_f[idx]),
                class_id=int(class_ids[idx])
            ))
        
        return results
    
    def get_model_name(self) -> str:
        return "yolov8"


class YOLOXPostprocessor(IPostprocessor):
    """
    Postprocessor for YOLOX models.

    YOLOX NPU outputs a single fused tensor [1, N, 5+num_classes] where
    bbox values are **raw logits** (not decoded), unlike YOLOv5 which outputs
    already-decoded coordinates.  Grid decode is required:

        cx = (cx_raw + grid_x) * stride
        cy = (cy_raw + grid_y) * stride
        w  = exp(w_raw)  * stride
        h  = exp(h_raw)  * stride

    Objectness and class scores are already sigmoid-applied.
    """

    STRIDES = [8, 16, 32]

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

        self.obj_threshold = self.config.get('obj_threshold', 0.25)
        self.conf_threshold = self.config.get('conf_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)
        self.num_classes = self.config.get('num_classes', 80)

        # Lazy-built grid
        self._grids = None
        self._strides_expanded = None

    def _build_grid(self, input_h: int, input_w: int):
        """Build anchor grid and stride tensor for all scales."""
        grids = []
        strides_expanded = []
        for stride in self.STRIDES:
            gh = input_h // stride
            gw = input_w // stride
            yv, xv = np.meshgrid(np.arange(gh), np.arange(gw), indexing='ij')
            grid = np.stack([xv.ravel(), yv.ravel()], axis=1).astype(np.float32)
            grids.append(grid)
            strides_expanded.append(np.full(gh * gw, stride, dtype=np.float32))
        self._grids = np.concatenate(grids, axis=0)            # [N, 2]
        self._strides_expanded = np.concatenate(strides_expanded)  # [N]

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        """
        Process YOLOX outputs with grid decode.

        Args:
            outputs: Single tensor [1, N, 5+num_classes] (fused, raw logits)
                     or 3 tensors [1, C, H, W] each (NPU multi-scale raw)
            ctx: Preprocessing context

        Returns:
            List of DetectionResult objects
        """
        # Detect multi-scale NPU output (3 tensors with 4D shape)
        if len(outputs) == 3 and all(o.ndim == 4 for o in outputs):
            output = self._decode_multi_scale_outputs(outputs)
        else:
            output = np.squeeze(outputs[0])  # [N, 5+C]

        n_anchors = output.shape[0]

        # Build grid if needed
        if self._grids is None or self._grids.shape[0] != n_anchors:
            self._build_grid(self.input_height, self.input_width)

        if self._grids.shape[0] != n_anchors:
            # Mismatch — fall back to treating as already decoded
            return self._process_decoded(output, ctx)

        # Grid decode for YOLOX
        grids = self._grids        # [N, 2]  (grid_x, grid_y)
        strides = self._strides_expanded  # [N]

        cx = (output[:, 0] + grids[:, 0]) * strides
        cy = (output[:, 1] + grids[:, 1]) * strides
        w = np.exp(np.clip(output[:, 2], -10, 10)) * strides
        h = np.exp(np.clip(output[:, 3], -10, 10)) * strides

        # obj and class scores are already sigmoid-applied
        obj_scores = output[:, 4]

        # Filter by objectness
        obj_mask = obj_scores >= self.obj_threshold
        if not np.any(obj_mask):
            return []

        cx_f = cx[obj_mask]
        cy_f = cy[obj_mask]
        w_f = w[obj_mask]
        h_f = h[obj_mask]
        obj_f = obj_scores[obj_mask]
        cls_scores = output[obj_mask, 5:5+self.num_classes]

        cls_max_scores = np.max(cls_scores, axis=1)
        cls_ids = np.argmax(cls_scores, axis=1)
        confidences = obj_f * cls_max_scores

        # Convert to x1y1x2y2
        boxes = np.column_stack([
            cx_f - w_f * 0.5,
            cy_f - h_f * 0.5,
            cx_f + w_f * 0.5,
            cy_f + h_f * 0.5,
        ])

        # NMS
        indices = _nms(boxes, confidences, cls_ids, self.conf_threshold, self.nms_threshold)
        if len(indices) == 0:
            return []

        # Convert to original coordinates
        results = []
        gain = max(ctx.scale, 1e-6)
        pad_x = ctx.pad_x
        pad_y = ctx.pad_y

        for idx in indices:
            box = boxes[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)

            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(confidences[idx]),
                class_id=int(cls_ids[idx])
            ))

        return results

    def _decode_multi_scale_outputs(self, outputs: list) -> np.ndarray:
        """Decode 3-tensor NPU outputs for YOLOX (no anchors, just grid+stride)."""
        num_fields = 5 + self.num_classes
        sorted_outputs = sorted(outputs, key=lambda t: t.shape[-1] * t.shape[-2], reverse=True)

        all_detections = []
        for scale_idx, tensor in enumerate(sorted_outputs):
            data = np.squeeze(tensor)  # [C, H, W]
            stride = self.STRIDES[scale_idx]
            grid_h, grid_w = data.shape[1], data.shape[2]

            # YOLOX: no anchors, just 1 prediction per grid cell
            # data shape: [num_fields, H, W]
            data = data.reshape(num_fields, grid_h, grid_w)

            gx = np.arange(grid_w, dtype=np.float32).reshape(1, 1, grid_w)
            gy = np.arange(grid_h, dtype=np.float32).reshape(1, grid_h, 1)

            # Grid decode
            cx = (data[0:1, :, :] + gx) * stride
            cy = (data[1:2, :, :] + gy) * stride
            w = np.exp(np.clip(data[2:3, :, :], -10, 10)) * stride
            h = np.exp(np.clip(data[3:4, :, :], -10, 10)) * stride

            # Sigmoid on obj + cls (may already be applied for some outputs)
            obj = data[4:5, :, :]
            cls = data[5:5+self.num_classes, :, :]

            n = grid_h * grid_w
            # cls has shape [C, H, W] — transpose to [H, W, C] before reshaping
            # so class dimension stays as columns, not mixed with spatial dims.
            scale_det = np.concatenate([
                cx.reshape(n, 1), cy.reshape(n, 1),
                w.reshape(n, 1), h.reshape(n, 1),
                obj.reshape(n, 1),
                cls.transpose(1, 2, 0).reshape(n, self.num_classes)
            ], axis=1)
            all_detections.append(scale_det)

        return np.concatenate(all_detections, axis=0)

    def _process_decoded(self, output: np.ndarray, ctx: PreprocessContext) -> List[DetectionResult]:
        """Fallback: process already-decoded output (same as YOLOv5)."""
        obj_scores = output[:, 4]
        obj_mask = obj_scores >= self.obj_threshold
        if not np.any(obj_mask):
            return []

        filtered = output[obj_mask]
        filtered_obj = obj_scores[obj_mask]
        cls_scores = filtered[:, 5:5+self.num_classes]
        cls_max_scores = np.max(cls_scores, axis=1)
        cls_ids = np.argmax(cls_scores, axis=1)
        confidences = filtered_obj * cls_max_scores
        boxes = _cxcywh_to_x1y1x2y2(filtered[:, :4])
        indices = _nms(boxes, confidences, cls_ids, self.conf_threshold, self.nms_threshold)
        if len(indices) == 0:
            return []
        results = []
        gain = max(ctx.scale, 1e-6)
        pad_x, pad_y = ctx.pad_x, ctx.pad_y
        for idx in indices:
            box = boxes[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)
            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(confidences[idx]),
                class_id=int(cls_ids[idx])
            ))
        return results

    def get_model_name(self) -> str:
        return "yolox"
