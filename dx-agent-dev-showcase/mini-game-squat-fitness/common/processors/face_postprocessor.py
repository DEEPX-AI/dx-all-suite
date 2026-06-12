"""
Face Detection Postprocessors

Supports different face detection architectures:
- SCRFDPostprocessor: Multi-scale anchor-free face detection
- YOLOv5FacePostprocessor: YOLO-based face detection with 5 keypoints

Output format: FaceResult with box, confidence, class_id, and 5 keypoints
"""

import numpy as np
import cv2
from typing import List, Any
from dataclasses import dataclass, field

from ..base import IPostprocessor, PreprocessContext, Keypoint


@dataclass
class FaceResult:
    """Face detection result with keypoints."""
    box: List[float] = field(default_factory=list)  # x1, y1, x2, y2
    confidence: float = 0.0
    class_id: int = 0
    keypoints: List[Keypoint] = field(default_factory=list)  # 5 facial landmarks
    
    def get_keypoint_array(self) -> np.ndarray:
        """Get keypoints as numpy array (5, 2)."""
        return np.array([[kp.x, kp.y] for kp in self.keypoints])


class SCRFDPostprocessor(IPostprocessor):
    """
    SCRFD Postprocessor for multi-scale anchor-free face detection.
    
    Output format: 9 tensors (3 scales x (score, bbox, keypoints))
    """
    
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        
        self.score_threshold = self.config.get('score_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.4)
        self.num_keypoints = self.config.get('num_keypoints', 5)
        self.num_anchors = self.config.get('num_anchors', 2)
    
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[FaceResult]:
        """
        Process SCRFD outputs.
        """
        buckets = self._group_tensors_by_spatial(outputs)
        triplets = self._build_triplets(buckets)

        all_boxes, all_scores, all_keypoints = self._decode_all_triplets(triplets)
        if not all_boxes:
            return []

        boxes_x1y1wh = np.vstack(all_boxes)
        scores = np.concatenate(all_scores)
        keypoints_array = np.vstack(all_keypoints)

        indices = cv2.dnn.NMSBoxes(
            boxes_x1y1wh.tolist(), scores.tolist(),
            self.score_threshold, self.nms_threshold,
        )
        if len(indices) == 0:
            return []

        keep = np.array(indices).reshape(-1)
        return self._build_scrfd_results(keep, boxes_x1y1wh, scores, keypoints_array, ctx)

    def _group_tensors_by_spatial(self, outputs: List[np.ndarray]) -> dict:
        """Group tensors by spatial dimension (n) and classify by channel count."""
        buckets = {}
        for t in outputs:
            if t.ndim != 3:
                continue
            b, n, c = t.shape
            if b != 1:
                continue
            entry = buckets.setdefault(n, {})
            if c == 1:
                entry["score"] = t
            elif c == 4:
                entry["bbox"] = t
            elif c == self.num_keypoints * 2:
                entry["kps"] = t
        return buckets

    def _build_triplets(self, buckets: dict) -> list:
        """Build (stride, score_t, bbox_t, kps_t) triplets from grouped tensors."""
        triplets = []
        for n, d in buckets.items():
            if {"score", "bbox", "kps"} <= d.keys():
                stride = self.input_width // max(1, int(round(np.sqrt(n // self.num_anchors))))
                triplets.append((stride, d["score"], d["bbox"], d["kps"]))
        return triplets

    def _decode_all_triplets(self, triplets: list):
        """Decode anchors, boxes, and keypoints for all scale triplets."""
        all_boxes, all_scores, all_keypoints = [], [], []
        for stride, score_t, bbox_t, kps_t in triplets:
            score = score_t.reshape(-1)
            bbox = bbox_t.reshape(-1, 4)
            kps = kps_t.reshape(-1, self.num_keypoints * 2)
            n = score.size
            if n == 0:
                continue
            hw = max(1, int(round(np.sqrt(n // self.num_anchors))))
            loc = np.arange(n) // self.num_anchors
            gx, gy = loc % hw, loc // hw
            cx, cy = gx * stride, gy * stride
            x1 = cx - bbox[:, 0] * stride
            y1 = cy - bbox[:, 1] * stride
            x2 = cx + bbox[:, 2] * stride
            y2 = cy + bbox[:, 3] * stride
            kx = cx[:, None] + kps[:, 0::2] * stride
            ky = cy[:, None] + kps[:, 1::2] * stride
            all_boxes.append(np.column_stack([x1, y1, x2 - x1, y2 - y1]))
            all_scores.append(score)
            all_keypoints.append(np.stack((kx, ky), axis=-1).reshape(n, -1))
        return all_boxes, all_scores, all_keypoints

    def _build_scrfd_results(self, keep, boxes_x1y1wh, scores, keypoints_array, ctx) -> List[FaceResult]:
        """Scale kept detections to original image coordinates."""
        gain = max(ctx.scale, 1e-6)
        pad_x, pad_y = ctx.pad_x, ctx.pad_y
        results = []
        for idx in keep:
            x1 = boxes_x1y1wh[idx, 0]
            y1 = boxes_x1y1wh[idx, 1]
            x2 = x1 + boxes_x1y1wh[idx, 2]
            y2 = y1 + boxes_x1y1wh[idx, 3]
            x1 = np.clip((x1 - pad_x) / gain, 0, ctx.original_width - 1)
            y1 = np.clip((y1 - pad_y) / gain, 0, ctx.original_height - 1)
            x2 = np.clip((x2 - pad_x) / gain, 0, ctx.original_width - 1)
            y2 = np.clip((y2 - pad_y) / gain, 0, ctx.original_height - 1)
            kps_raw = keypoints_array[idx].reshape(-1, 2)
            keypoints = [
                Keypoint(
                    x=float(np.clip((kp[0] - pad_x) / gain, 0, ctx.original_width - 1)),
                    y=float(np.clip((kp[1] - pad_y) / gain, 0, ctx.original_height - 1)),
                    confidence=1.0,
                )
                for kp in kps_raw
            ]
            results.append(FaceResult(
                box=[float(x1), float(y1), float(x2), float(y2)],
                confidence=float(scores[idx]),
                class_id=0,
                keypoints=keypoints,
            ))
        return results
    
    def get_model_name(self) -> str:
        return "scrfd"


class YOLOv5FacePostprocessor(IPostprocessor):
    """
    YOLOv5Face Postprocessor.
    
    Output format: [1, N, 16] -> [cx, cy, w, h, obj, kp1_x, ..., kp5_y, class_score]
    """
    
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        
        self.obj_threshold = self.config.get('obj_threshold', 0.25)
        self.score_threshold = self.config.get('score_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)
        self.num_keypoints = self.config.get('num_keypoints', 5)
    
    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[FaceResult]:
        """
        Process YOLOv5Face/YOLOv7Face outputs.
        Auto-detects layout by output column count:
          - 16 cols: YOLOv5Face [cx,cy,w,h,obj, kp1x,kp1y,...,kp5x,kp5y, cls]
          - 21 cols: YOLOv7Face [cx,cy,w,h,obj, (kp_conf,kp_x,kp_y)*5, cls_logit]
        """
        output = np.squeeze(outputs[0])

        if output.ndim == 2 and output.shape[1] >= 21:
            return self._process_v7face(output, ctx)

        return self._process_v5face(output, ctx)

    def _process_v5face(self, output: np.ndarray, ctx: PreprocessContext) -> List[FaceResult]:

        obj_scores = output[:, 4]
        obj_mask = obj_scores >= self.obj_threshold
        if not np.any(obj_mask):
            return []

        filtered = output[obj_mask]
        filtered_obj = obj_scores[obj_mask]
        keypoints_raw = filtered[:, 5:15]
        class_scores = filtered[:, 15]
        confidences = filtered_obj * class_scores

        boxes_x1y1x2y2 = self._cxcywh_to_xyxy(filtered[:, :4])
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
        return self._build_yolo_face_results(keep, boxes_x1y1x2y2, confidences, keypoints_raw, ctx)

    @staticmethod
    def _cxcywh_to_xyxy(boxes_cxcywh: np.ndarray) -> np.ndarray:
        """Convert center-format boxes to corner-format boxes."""
        return np.column_stack([
            boxes_cxcywh[:, 0] - boxes_cxcywh[:, 2] * 0.5,
            boxes_cxcywh[:, 1] - boxes_cxcywh[:, 3] * 0.5,
            boxes_cxcywh[:, 0] + boxes_cxcywh[:, 2] * 0.5,
            boxes_cxcywh[:, 1] + boxes_cxcywh[:, 3] * 0.5,
        ])

    def _build_yolo_face_results(
        self, keep, boxes_x1y1x2y2, confidences, keypoints_raw, ctx
    ) -> List[FaceResult]:
        """Scale kept detections to original image coordinates."""
        gain = max(ctx.scale, 1e-6)
        pad_x, pad_y = ctx.pad_x, ctx.pad_y
        results = []
        for idx in keep:
            box = boxes_x1y1x2y2[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)
            kps_raw = keypoints_raw[idx].reshape(-1, 2)
            keypoints = [
                Keypoint(
                    x=float(np.clip((kp[0] - pad_x) / gain, 0, ctx.original_width - 1)),
                    y=float(np.clip((kp[1] - pad_y) / gain, 0, ctx.original_height - 1)),
                    confidence=1.0,
                )
                for kp in kps_raw
            ]
            results.append(FaceResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(confidences[idx]),
                class_id=0,
                keypoints=keypoints,
            ))
        return results
    
    @staticmethod
    def _sigmoid(x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))

    def _process_v7face(self, output: np.ndarray, ctx: PreprocessContext) -> List[FaceResult]:
        """
        Process YOLOv7Face 21-column output.

        Layout: [cx,cy,w,h, obj, (kp_conf,kp_x,kp_y)*5, cls_logit]
        - obj is sigmoid-applied, cls is raw logit → apply sigmoid
        - kp_conf is sigmoid-applied, kp_x/y are pixel coords
        """
        obj_scores = output[:, 4]
        obj_mask = obj_scores >= self.obj_threshold
        if not np.any(obj_mask):
            return []

        filtered = output[obj_mask]
        filtered_obj = obj_scores[obj_mask]

        # cls at col 20 is raw logit
        cls_scores = self._sigmoid(filtered[:, 20])
        confidences = filtered_obj * cls_scores

        boxes_x1y1x2y2 = self._cxcywh_to_xyxy(filtered[:, :4])

        # Keypoints: (conf, x, y) triplets at cols 5..19
        kp_confs = np.column_stack([filtered[:, 5+k*3] for k in range(5)])
        kp_xs    = np.column_stack([filtered[:, 6+k*3] for k in range(5)])
        kp_ys    = np.column_stack([filtered[:, 7+k*3] for k in range(5)])

        # NMS
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

        gain = max(ctx.scale, 1e-6)
        pad_x, pad_y = ctx.pad_x, ctx.pad_y
        results = []
        for idx in keep:
            box = boxes_x1y1x2y2[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)

            keypoints = []
            for k in range(5):
                kx = float(np.clip((kp_xs[idx, k] - pad_x) / gain, 0, ctx.original_width - 1))
                ky = float(np.clip((kp_ys[idx, k] - pad_y) / gain, 0, ctx.original_height - 1))
                keypoints.append(Keypoint(x=kx, y=ky, confidence=float(kp_confs[idx, k])))

            results.append(FaceResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(confidences[idx]),
                class_id=0,
                keypoints=keypoints,
            ))

        return results
    
    def get_model_name(self) -> str:
        return "yolov5face"


class YOLOv7FacePostprocessor(IPostprocessor):
    """
    YOLOv7Face Postprocessor.

    Output format: [1, N, 21]
      col  0- 3: cx, cy, w, h  (decoded pixel coords)
      col  4   : objectness    (sigmoid-applied)
      col  5   : kp1_conf      (sigmoid-applied)
      col  6- 7: kp1_x, kp1_y  (pixel coords)
      col  8   : kp2_conf
      col  9-10: kp2_x, kp2_y
      col 11   : kp3_conf
      col 12-13: kp3_x, kp3_y
      col 14   : kp4_conf
      col 15-16: kp4_x, kp4_y
      col 17   : kp5_conf
      col 18-19: kp5_x, kp5_y
      col 20   : class_score    (raw logit — needs sigmoid)

    Unlike YOLOv5Face (16-col format where kp_x/y pairs are contiguous,
    conf is always 1.0, and scores are pre-sigmoid), YOLOv7Face interleaves
    per-keypoint confidence and the class score is a raw logit.
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

        self.obj_threshold = self.config.get('obj_threshold', 0.25)
        self.score_threshold = self.config.get('score_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)
        self.num_keypoints = 5

    @staticmethod
    def _sigmoid(x):
        return 1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[FaceResult]:
        output = np.squeeze(outputs[0])  # [N, 21]

        if output.ndim != 2 or output.shape[1] < 21:
            return []

        obj_scores = output[:, 4]  # already sigmoid
        obj_mask = obj_scores >= self.obj_threshold
        if not np.any(obj_mask):
            return []

        filtered = output[obj_mask]
        filtered_obj = obj_scores[obj_mask]

        # Class score at col 20 — raw logit, apply sigmoid
        cls_scores = self._sigmoid(filtered[:, 20])
        confidences = filtered_obj * cls_scores

        # Box: cx,cy,w,h already decoded pixel coords
        boxes_x1y1x2y2 = np.column_stack([
            filtered[:, 0] - filtered[:, 2] * 0.5,
            filtered[:, 1] - filtered[:, 3] * 0.5,
            filtered[:, 0] + filtered[:, 2] * 0.5,
            filtered[:, 1] + filtered[:, 3] * 0.5,
        ])

        # Keypoints: (conf, x, y) triplets at cols 5..19
        # kp_k: conf=col[5+k*3], x=col[6+k*3], y=col[7+k*3]
        kp_confs = np.column_stack([filtered[:, 5+k*3] for k in range(5)])   # [M, 5]
        kp_xs    = np.column_stack([filtered[:, 6+k*3] for k in range(5)])   # [M, 5]
        kp_ys    = np.column_stack([filtered[:, 7+k*3] for k in range(5)])   # [M, 5]

        # NMS
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

        # Build results with coordinate rescaling
        gain = max(ctx.scale, 1e-6)
        pad_x, pad_y = ctx.pad_x, ctx.pad_y
        results = []
        for idx in keep:
            box = boxes_x1y1x2y2[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)

            keypoints = []
            for k in range(5):
                kx = float(np.clip((kp_xs[idx, k] - pad_x) / gain, 0, ctx.original_width - 1))
                ky = float(np.clip((kp_ys[idx, k] - pad_y) / gain, 0, ctx.original_height - 1))
                keypoints.append(Keypoint(x=kx, y=ky, confidence=float(kp_confs[idx, k])))

            results.append(FaceResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(confidences[idx]),
                class_id=0,
                keypoints=keypoints,
            ))

        return results

    def get_model_name(self) -> str:
        return "yolov7face"
