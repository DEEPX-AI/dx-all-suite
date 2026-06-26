"""
Pose Estimation Postprocessors

Supports different pose estimation architectures:
- YOLOv5PosePostprocessor: YOLOv5-pose style (17 keypoints)
- YOLOv8PosePostprocessor: YOLOv8-pose style (17 keypoints, transposed output)

Output format: PoseResult with box, confidence, class_id, and 17 keypoints
"""

import numpy as np
import cv2
from typing import List, Any

from ..base import IPostprocessor, PreprocessContext, PoseResult, Keypoint


class YOLOv5PosePostprocessor(IPostprocessor):
    """
    YOLOv5-pose Postprocessor.
    
    Output format: [1, N, 57] -> [cx, cy, w, h, obj, class_score, kp1_x, kp1_y, kp1_conf, ...]
    17 keypoints x 3 (x, y, confidence) = 51 values
    """
    
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        
        self.obj_threshold = self.config.get('obj_threshold', 0.25)
        self.score_threshold = self.config.get('score_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)
        self.num_keypoints = self.config.get('num_keypoints', 17)
    
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[PoseResult]:
        """
        Process YOLOv5-pose outputs.
        
        Args:
            outputs: Model outputs [1, N, 57]
            ctx: Preprocessing context
            
        Returns:
            List of PoseResult objects
        """
        output = np.squeeze(outputs[0])
        
        # Filter by objectness
        obj_scores = output[:, 4]
        obj_mask = obj_scores >= self.obj_threshold
        
        if not np.any(obj_mask):
            return []
        
        filtered = output[obj_mask]
        filtered_obj = obj_scores[obj_mask]
        
        # Class score and keypoints
        class_scores = filtered[:, 5]
        keypoints_raw = filtered[:, 6:]  # 17 * 3 = 51 values
        
        # Final confidence = obj * class
        confidences = filtered_obj * class_scores
        
        # Box conversion (center to corner)
        boxes_cxcywh = filtered[:, :4]
        boxes_x1y1x2y2 = np.column_stack([
            boxes_cxcywh[:, 0] - boxes_cxcywh[:, 2] * 0.5,
            boxes_cxcywh[:, 1] - boxes_cxcywh[:, 3] * 0.5,
            boxes_cxcywh[:, 0] + boxes_cxcywh[:, 2] * 0.5,
            boxes_cxcywh[:, 1] + boxes_cxcywh[:, 3] * 0.5,
        ])
        
        # NMS
        boxes_xywh = np.column_stack([
            boxes_x1y1x2y2[:, 0], boxes_x1y1x2y2[:, 1],
            boxes_x1y1x2y2[:, 2] - boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 3] - boxes_x1y1x2y2[:, 1]
        ])
        
        indices = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(),
            confidences.tolist(),
            self.score_threshold,
            self.nms_threshold
        )
        
        if len(indices) == 0:
            return []
        
        keep = np.array(indices).reshape(-1)
        
        # Convert to original coordinates
        gain = max(ctx.scale, 1e-6)
        pad_x = ctx.pad_x
        pad_y = ctx.pad_y
        
        results = []
        for idx in keep:
            box = boxes_x1y1x2y2[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)
            
            # Parse keypoints (x, y, conf) triplets
            kps_raw = keypoints_raw[idx].reshape(-1, 3)
            keypoints = []
            for kp in kps_raw:
                kp_x = np.clip((kp[0] - pad_x) / gain, 0, ctx.original_width - 1)
                kp_y = np.clip((kp[1] - pad_y) / gain, 0, ctx.original_height - 1)
                keypoints.append(Keypoint(x=float(kp_x), y=float(kp_y), confidence=float(kp[2])))
            
            results.append(PoseResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(confidences[idx]),
                class_id=0,  # person
                keypoints=keypoints
            ))
        
        return results
    
    def get_model_name(self) -> str:
        return "yolov5pose"


class YOLOv8PosePostprocessor(IPostprocessor):
    """
    YOLOv8/YOLO26-pose Postprocessor.

    Handles two output formats automatically:
    - YOLOv8 pre-NMS:  [1, 56, N] (C×N, needs transpose)
      layout: [cx,cy,w,h, score, kp*51]
    - YOLO26 post-NMS: [1, 300, 57] (N×C, already correct)
      layout: [cx,cy,w,h, score, class_id, kp*51]

    Auto-detects format from tensor shape.
    """
    
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        
        self.score_threshold = self.config.get('score_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)
        self.num_keypoints = self.config.get('num_keypoints', 17)
    
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[PoseResult]:
        """
        Process YOLOv8/YOLO26-pose outputs.
        
        Args:
            outputs: Model outputs [1, 56, N] or [1, N, 57]
            ctx: Preprocessing context
            
        Returns:
            List of PoseResult objects
        """
        # Auto-detect format and transpose if needed
        squeezed = np.squeeze(outputs[0])
        if squeezed.ndim < 2:
            return []
        if squeezed.shape[0] < squeezed.shape[1]:
            # [C, N] format (e.g. yolov8 [56, 8400]) → transpose to [N, C]
            output = np.transpose(squeezed)
            is_end_to_end = False
        else:
            # [N, C] format (e.g. yolo26 [300, 57]) → already correct
            output = squeezed
            is_end_to_end = True  # Post-NMS: boxes are [x1,y1,x2,y2]

        total_cols = output.shape[1]
        kp_values = self.num_keypoints * 3  # typically 51

        # Determine keypoint start column:
        # yolov8: [cx,cy,w,h, score, kp*51] → 56 cols, kps at col 5
        # yolo26: [x1,y1,x2,y2, score, class_id, kp*51] → 57 cols, kps at col 6
        kp_start = total_cols - kp_values
        
        # Filter by score (always at column 4)
        scores = output[:, 4]
        mask = scores >= self.score_threshold
        
        if not np.any(mask):
            return []
        
        filtered = output[mask]
        filtered_scores = scores[mask]
        
        # Keypoints — use auto-detected start column
        keypoints_raw = filtered[:, kp_start:]

        if is_end_to_end:
            # YOLO26 post-NMS: cols 0-3 are [x1, y1, x2, y2] already
            boxes_x1y1x2y2 = filtered[:, :4].copy()
        else:
            # YOLOv8 pre-NMS: cols 0-3 are [cx, cy, w, h]
            boxes_cxcywh = filtered[:, :4]
            boxes_x1y1x2y2 = np.column_stack([
                boxes_cxcywh[:, 0] - boxes_cxcywh[:, 2] * 0.5,
                boxes_cxcywh[:, 1] - boxes_cxcywh[:, 3] * 0.5,
                boxes_cxcywh[:, 0] + boxes_cxcywh[:, 2] * 0.5,
                boxes_cxcywh[:, 1] + boxes_cxcywh[:, 3] * 0.5,
            ])
        
        # NMS
        boxes_xywh = np.column_stack([
            boxes_x1y1x2y2[:, 0], boxes_x1y1x2y2[:, 1],
            boxes_x1y1x2y2[:, 2] - boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 3] - boxes_x1y1x2y2[:, 1]
        ])
        
        indices = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(),
            filtered_scores.tolist(),
            self.score_threshold,
            self.nms_threshold
        )
        
        if len(indices) == 0:
            return []
        
        keep = np.array(indices).reshape(-1)
        
        # Convert to original coordinates
        gain = max(ctx.scale, 1e-6)
        pad_x = ctx.pad_x
        pad_y = ctx.pad_y
        
        results = []
        for idx in keep:
            box = boxes_x1y1x2y2[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)
            
            # Parse keypoints
            kps_raw = keypoints_raw[idx].reshape(-1, 3)
            keypoints = []
            for kp in kps_raw:
                kp_x = np.clip((kp[0] - pad_x) / gain, 0, ctx.original_width - 1)
                kp_y = np.clip((kp[1] - pad_y) / gain, 0, ctx.original_height - 1)
                keypoints.append(Keypoint(x=float(kp_x), y=float(kp_y), confidence=float(kp[2])))
            
            results.append(PoseResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(filtered_scores[idx]),
                class_id=0,
                keypoints=keypoints
            ))
        
        return results
    
    def get_model_name(self) -> str:
        return "yolov8pose"
