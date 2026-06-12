"""
PPU (Post-Processing Unit) Postprocessor

Unified postprocessor for models compiled with PPU support.

Hardware PPU output struct layouts (from dxrt/datatype.h):

  DeviceBoundingBox_t (32 bytes) — used by YOLOv5/YOLOv7 PPU:
    float x, y, w, h;  uint8 grid_y, grid_x, box_idx, layer_idx;
    float score; uint32 label; char padding[4];

  DeviceFace_t (64 bytes) — used by SCRFD PPU:
    float x, y, w, h;  uint8 grid_y, grid_x, box_idx, layer_idx;
    float score; float kpts[5][2];

  DevicePose_t (256 bytes) — used by YOLOv5Pose PPU:
    float x, y, w, h;  uint8 grid_y, grid_x, box_idx, layer_idx;
    float score; uint32 label; float kpts[17][3]; char padding[24];

Backward-compatible aliases:
  YOLOv5PPUPostprocessor  = PPUPostprocessor(model_type='yolov5_ppu')
  YOLOv7PPUPostprocessor  = PPUPostprocessor(model_type='yolov7_ppu')
  SCRFDPPUPostprocessor   — full FACE keypoint extraction (DeviceFace_t)
  YOLOv5PosePPUPostprocessor — full POSE keypoint extraction (DevicePose_t)
"""

import numpy as np
import cv2
from typing import List

from ..base import IPostprocessor, PreprocessContext, DetectionResult, Keypoint, PoseResult
from .face_postprocessor import FaceResult


class PPUPostprocessor(IPostprocessor):
    """
    Unified PPU postprocessor for YOLO-family models.

    PPU output format (per detection, 32 bytes):
      - [:, :16]  -> boxes   (4 × float32)
      - [:, 16:20] -> grid info (g_y, g_x, anchor_idx, layer_idx as uint8)
      - [:, 20:24] -> scores  (float32)
      - [:, 24:28] -> labels  (uint32)

    Args:
      model_type: identifier returned by ``get_model_name()``.
      config: optional dict for conf_threshold, nms_threshold.
    """

    # YOLOv5-style anchors (shared by all current PPU models)
    ANCHORS = {
        8:  np.array([[10, 13], [16, 30], [33, 23]], dtype=np.float32),
        16: np.array([[30, 61], [62, 45], [59, 119]], dtype=np.float32),
        32: np.array([[116, 90], [156, 198], [373, 326]], dtype=np.float32),
    }

    STRIDES = np.array([8, 16, 32], dtype=np.float32)

    def __init__(self, input_width: int, input_height: int,
                 config: dict = None, *, model_type: str = "yolov5_ppu"):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self._model_type = model_type

        self.score_threshold = self.config.get('conf_threshold', 0.25)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)

        # Allow caller to override per-model anchors and strides via config
        custom_anchors = self.config.get('anchors', None)
        if custom_anchors is not None:
            self.ANCHORS = {
                k: np.array(v, dtype=np.float32)
                for k, v in custom_anchors.items()
            }
        custom_strides = self.config.get('strides', None)
        if custom_strides is not None:
            self.STRIDES = np.array(custom_strides, dtype=np.float32)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        if len(outputs) == 0 or outputs[0].ndim == 2:
            return []

        output_tensor = outputs[0][0]

        if output_tensor.shape[1] != 32:
            return []

        # Parse PPU output format
        boxes = output_tensor[:, :16].view(np.float32).reshape(-1, 4)

        grid_info = output_tensor[:, 16:20].view(np.uint8)
        g_y = grid_info[:, 0].astype(np.float32)
        g_x = grid_info[:, 1].astype(np.float32)
        anchor_idx = grid_info[:, 2]
        layer_idx = grid_info[:, 3]

        scores = output_tensor[:, 20:24].view(np.float32).flatten()
        labels = output_tensor[:, 24:28].view(np.uint32).flatten()

        # Get stride for each detection
        stride = self.STRIDES[layer_idx]

        # Get anchor dimensions
        anchor_w = np.zeros(len(boxes), dtype=np.float32)
        anchor_h = np.zeros(len(boxes), dtype=np.float32)

        for s in self.ANCHORS.keys():
            stride_mask = stride == s
            if np.any(stride_mask):
                anchors = self.ANCHORS[s]
                anchor_w[stride_mask] = anchors[anchor_idx[stride_mask], 0]
                anchor_h[stride_mask] = anchors[anchor_idx[stride_mask], 1]

        # Decode boxes
        boxes_cx = (boxes[:, 0] * 2.0 - 0.5 + g_x) * stride
        boxes_cy = (boxes[:, 1] * 2.0 - 0.5 + g_y) * stride
        boxes_w = (boxes[:, 2] ** 2 * 4.0) * anchor_w
        boxes_h = (boxes[:, 3] ** 2 * 4.0) * anchor_h

        # Convert to x1y1x2y2
        boxes_x1y1x2y2 = np.column_stack([
            boxes_cx - boxes_w * 0.5,
            boxes_cy - boxes_h * 0.5,
            boxes_cx + boxes_w * 0.5,
            boxes_cy + boxes_h * 0.5,
        ])

        # Convert to x1y1wh for NMS
        boxes_x1y1wh = np.column_stack([
            boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 1],
            boxes_x1y1x2y2[:, 2] - boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 3] - boxes_x1y1x2y2[:, 1],
        ])

        # Apply NMS
        indices = cv2.dnn.NMSBoxes(
            boxes_x1y1wh.tolist(),
            scores.tolist(),
            self.score_threshold,
            self.nms_threshold,
        )

        if len(indices) == 0:
            return []

        keep = np.array(indices).reshape(-1)

        # Convert to original coordinates
        results = []
        gain = max(ctx.scale, 1e-6)
        pad_x = ctx.pad_x
        pad_y = ctx.pad_y

        for idx in keep:
            box = boxes_x1y1x2y2[idx].copy()
            box[0] = np.clip((box[0] - pad_x) / gain, 0, ctx.original_width - 1)
            box[1] = np.clip((box[1] - pad_y) / gain, 0, ctx.original_height - 1)
            box[2] = np.clip((box[2] - pad_x) / gain, 0, ctx.original_width - 1)
            box[3] = np.clip((box[3] - pad_y) / gain, 0, ctx.original_height - 1)

            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(scores[idx]),
                class_id=int(labels[idx])
            ))

        return results

    def get_model_name(self) -> str:
        return self._model_type


# ---------------------------------------------------------------------------
# Backward-compatible aliases
# ---------------------------------------------------------------------------
class YOLOv5PPUPostprocessor(PPUPostprocessor):
    """YOLOv5 PPU — default model_type."""
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        super().__init__(input_width, input_height, config, model_type="yolov5_ppu")


class YOLOv7PPUPostprocessor(PPUPostprocessor):
    """YOLOv7 PPU — same decode logic as YOLOv5 PPU."""
    def __init__(self, input_width: int, input_height: int, config: dict = None):
        super().__init__(input_width, input_height, config, model_type="yolov7_ppu")


class YOLOv8PPUPostprocessor(IPostprocessor):
    """
    YOLOv8 PPU — anchor-free detection postprocessor.

    Unlike YOLOv5/v7 PPU which use anchor-based decoding, YOLOv8 PPU outputs
    direct x, y, w, h values in DeviceBoundingBox_t format (32 bytes):
      Bytes  0-15: x, y, w, h (float32) — direct center coords and dimensions
      Bytes 16-19: grid_y, grid_x, box_idx, layer_idx (uint8) — unused for decoding
      Bytes 20-23: score (float32)
      Bytes 24-27: label (uint32)
      Bytes 28-31: padding

    Box decoding (anchor-free):
      cx = x,  cy = y,  w = w,  h = h  (no anchor/stride transformation)
      x1 = cx - w/2,  y1 = cy - h/2,  x2 = cx + w/2,  y2 = cy + h/2
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.score_threshold = self.config.get('conf_threshold',
                                               self.config.get('score_threshold', 0.4))
        self.nms_threshold = self.config.get('nms_threshold', 0.5)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        if len(outputs) == 0 or outputs[0].ndim == 2:
            return []

        output_tensor = outputs[0][0]  # remove batch dim → [N, 32]

        if output_tensor.ndim != 2 or output_tensor.shape[1] != 32:
            return []

        n = output_tensor.shape[0]
        if n == 0:
            return []

        # Parse DeviceBoundingBox_t fields
        boxes_raw = output_tensor[:, :16].view(np.float32).reshape(-1, 4)  # x, y, w, h
        scores = output_tensor[:, 20:24].view(np.float32).flatten()
        labels = output_tensor[:, 24:28].view(np.uint32).flatten()

        # Score filter
        mask = scores >= self.score_threshold
        if not np.any(mask):
            return []

        boxes_raw = boxes_raw[mask]
        scores = scores[mask]
        labels = labels[mask]

        # Anchor-free box decoding: direct x/y/w/h
        cx = boxes_raw[:, 0]
        cy = boxes_raw[:, 1]
        w = boxes_raw[:, 2]
        h = boxes_raw[:, 3]

        boxes_x1y1x2y2 = np.column_stack([
            cx - w * 0.5,
            cy - h * 0.5,
            cx + w * 0.5,
            cy + h * 0.5,
        ])

        # Convert to x1y1wh for NMS
        boxes_x1y1wh = np.column_stack([
            boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 1],
            boxes_x1y1x2y2[:, 2] - boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 3] - boxes_x1y1x2y2[:, 1],
        ])

        # Apply NMS
        indices = cv2.dnn.NMSBoxes(
            boxes_x1y1wh.tolist(),
            scores.tolist(),
            self.score_threshold,
            self.nms_threshold,
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

            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(scores[idx]),
                class_id=int(labels[idx])
            ))

        return results

    def get_model_name(self) -> str:
        return "yolov8_ppu"


class SCRFDPPUPostprocessor(IPostprocessor):
    """
    SCRFD PPU — face detection with 5 facial keypoints.

    Handles DeviceFace_t PPU output (64 bytes per element):
      Bytes  0-15: x, y, w, h (float32) — bbox distance deltas from grid
      Bytes 16-19: grid_y, grid_x, box_idx, layer_idx (uint8)
      Bytes 20-23: score (float32)
      Bytes 24-63: kpts[5][2] (float32) — 5 facial landmarks

    Box decoding (SCRFD distance-from-grid style):
      x1 = (grid_x - x) * stride,  y1 = (grid_y - y) * stride
      x2 = (grid_x + w) * stride,  y2 = (grid_y + h) * stride

    Keypoint decoding:
      lx = (grid_x + kpts[k][0]) * stride
      ly = (grid_y + kpts[k][1]) * stride
    """

    STRIDES = np.array([8, 16, 32], dtype=np.float32)

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.score_threshold = self.config.get('conf_threshold', 0.3)
        self.nms_threshold = self.config.get('nms_threshold', 0.4)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[FaceResult]:
        if len(outputs) == 0:
            return []

        output_tensor = outputs[0][0]  # remove batch dim → [N, 64]

        if output_tensor.ndim != 2 or output_tensor.shape[1] != 64:
            return []

        n = output_tensor.shape[0]
        if n == 0:
            return []

        # Parse DeviceFace_t fields
        boxes_raw = output_tensor[:, :16].view(np.float32).reshape(-1, 4)  # x, y, w, h
        grid_info = output_tensor[:, 16:20].view(np.uint8)
        g_y = grid_info[:, 0].astype(np.float32)
        g_x = grid_info[:, 1].astype(np.float32)
        layer_idx = grid_info[:, 3]
        scores = output_tensor[:, 20:24].view(np.float32).flatten()
        kpts_raw = output_tensor[:, 24:64].view(np.float32).reshape(-1, 5, 2)

        # Score filter
        mask = scores >= self.score_threshold
        if not np.any(mask):
            return []

        boxes_raw = boxes_raw[mask]
        g_y, g_x = g_y[mask], g_x[mask]
        layer_idx = layer_idx[mask]
        scores = scores[mask]
        kpts_raw = kpts_raw[mask]

        stride = self.STRIDES[layer_idx]

        # SCRFD box decoding: distance from grid center
        x1 = (g_x - boxes_raw[:, 0]) * stride
        y1 = (g_y - boxes_raw[:, 1]) * stride
        x2 = (g_x + boxes_raw[:, 2]) * stride
        y2 = (g_y + boxes_raw[:, 3]) * stride
        boxes_x1y1x2y2 = np.column_stack([x1, y1, x2, y2])

        # Keypoint decoding
        lx = (g_x[:, None] + kpts_raw[:, :, 0]) * stride[:, None]
        ly = (g_y[:, None] + kpts_raw[:, :, 1]) * stride[:, None]

        # NMS
        boxes_xywh = np.column_stack([
            boxes_x1y1x2y2[:, 0], boxes_x1y1x2y2[:, 1],
            boxes_x1y1x2y2[:, 2] - boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 3] - boxes_x1y1x2y2[:, 1],
        ])
        indices = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(), scores.tolist(),
            self.score_threshold, self.nms_threshold,
        )
        if len(indices) == 0:
            return []
        keep = np.array(indices).reshape(-1)

        # Convert to original coordinates
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
                kp_x = np.clip((lx[idx, k] - pad_x) / gain, 0, ctx.original_width - 1)
                kp_y = np.clip((ly[idx, k] - pad_y) / gain, 0, ctx.original_height - 1)
                keypoints.append(Keypoint(x=float(kp_x), y=float(kp_y), confidence=1.0))

            results.append(FaceResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(scores[idx]),
                class_id=0,
                keypoints=keypoints,
            ))

        return results

    def get_model_name(self) -> str:
        return "scrfd_ppu"


class YOLOv5PosePPUPostprocessor(IPostprocessor):
    """
    YOLOv5Pose PPU — person detection with 17 pose keypoints.

    Handles DevicePose_t PPU output (256 bytes per element):
      Bytes   0-15: x, y, w, h (float32) — bbox deltas (YOLO-style)
      Bytes  16-19: grid_y, grid_x, box_idx, layer_idx (uint8)
      Bytes  20-23: score (float32)
      Bytes  24-27: label (uint32)
      Bytes 28-231: kpts[17][3] (float32) — 17 keypoints (x, y, confidence)
      Bytes 232-255: padding

    Box decoding (YOLO-style, same as DeviceBoundingBox_t):
      cx = (x * 2 - 0.5 + grid_x) * stride
      cy = (y * 2 - 0.5 + grid_y) * stride
      w  = (w^2 * 4) * anchor_w,  h = (h^2 * 4) * anchor_h

    Keypoint decoding:
      lx = (grid_x - 0.5 + kpts[k][0] * 2) * stride
      ly = (grid_y - 0.5 + kpts[k][1] * 2) * stride
      ls = kpts[k][2]  (confidence score)
    """

    # YOLOv5Pose-specific anchors (4 strides)
    ANCHORS = {
        8:  np.array([[19, 27], [44, 40], [38, 94]], dtype=np.float32),
        16: np.array([[96, 68], [86, 152], [180, 137]], dtype=np.float32),
        32: np.array([[140, 301], [303, 264], [238, 542]], dtype=np.float32),
        64: np.array([[436, 615], [739, 380], [925, 792]], dtype=np.float32),
    }

    STRIDES = np.array([8, 16, 32, 64], dtype=np.float32)

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.score_threshold = self.config.get('conf_threshold', 0.25)
        self.nms_threshold = self.config.get('nms_threshold', 0.45)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[PoseResult]:
        if len(outputs) == 0:
            return []

        output_tensor = outputs[0][0]  # remove batch dim → [N, 256]

        if output_tensor.ndim != 2 or output_tensor.shape[1] != 256:
            return []

        n = output_tensor.shape[0]
        if n == 0:
            return []

        # Parse DevicePose_t fields
        boxes_raw = output_tensor[:, :16].view(np.float32).reshape(-1, 4)  # x, y, w, h
        grid_info = output_tensor[:, 16:20].view(np.uint8)
        g_y = grid_info[:, 0].astype(np.float32)
        g_x = grid_info[:, 1].astype(np.float32)
        box_idx = grid_info[:, 2]
        layer_idx = grid_info[:, 3]
        scores = output_tensor[:, 20:24].view(np.float32).flatten()
        # bytes 24-27: label (uint32) — not used for pose
        # bytes 28-231: kpts[17][3] = 51 floats = 204 bytes
        kpts_raw = output_tensor[:, 28:232].view(np.float32).reshape(-1, 17, 3)

        # Score filter
        mask = scores >= self.score_threshold
        if not np.any(mask):
            return []

        boxes_raw = boxes_raw[mask]
        g_y, g_x = g_y[mask], g_x[mask]
        box_idx, layer_idx = box_idx[mask], layer_idx[mask]
        scores = scores[mask]
        kpts_raw = kpts_raw[mask]

        stride = self.STRIDES[layer_idx]

        # Get anchor dimensions for each detection
        anchor_w = np.zeros(len(boxes_raw), dtype=np.float32)
        anchor_h = np.zeros(len(boxes_raw), dtype=np.float32)
        for s_val, anchors in self.ANCHORS.items():
            stride_mask = stride == s_val
            if np.any(stride_mask):
                bidx = box_idx[stride_mask]
                # Clamp box_idx to valid anchor range
                bidx = np.clip(bidx, 0, len(anchors) - 1)
                anchor_w[stride_mask] = anchors[bidx, 0]
                anchor_h[stride_mask] = anchors[bidx, 1]

        # YOLO-style box decoding
        boxes_cx = (boxes_raw[:, 0] * 2.0 - 0.5 + g_x) * stride
        boxes_cy = (boxes_raw[:, 1] * 2.0 - 0.5 + g_y) * stride
        boxes_w = (boxes_raw[:, 2] ** 2 * 4.0) * anchor_w
        boxes_h = (boxes_raw[:, 3] ** 2 * 4.0) * anchor_h

        boxes_x1y1x2y2 = np.column_stack([
            boxes_cx - boxes_w * 0.5,
            boxes_cy - boxes_h * 0.5,
            boxes_cx + boxes_w * 0.5,
            boxes_cy + boxes_h * 0.5,
        ])

        # Keypoint decoding: lx = (grid_x - 0.5 + kpts[k][0] * 2) * stride
        lx = (g_x[:, None] - 0.5 + kpts_raw[:, :, 0] * 2.0) * stride[:, None]
        ly = (g_y[:, None] - 0.5 + kpts_raw[:, :, 1] * 2.0) * stride[:, None]
        # Apply sigmoid to raw keypoint confidence (logit → probability)
        ls_raw = kpts_raw[:, :, 2]
        ls = 1.0 / (1.0 + np.exp(-np.clip(ls_raw, -50, 50)))

        # NMS
        boxes_xywh = np.column_stack([
            boxes_x1y1x2y2[:, 0], boxes_x1y1x2y2[:, 1],
            boxes_x1y1x2y2[:, 2] - boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 3] - boxes_x1y1x2y2[:, 1],
        ])
        indices = cv2.dnn.NMSBoxes(
            boxes_xywh.tolist(), scores.tolist(),
            self.score_threshold, self.nms_threshold,
        )
        if len(indices) == 0:
            return []
        keep = np.array(indices).reshape(-1)

        # Convert to original coordinates
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
            for k in range(17):
                kp_x = np.clip((lx[idx, k] - pad_x) / gain, 0, ctx.original_width - 1)
                kp_y = np.clip((ly[idx, k] - pad_y) / gain, 0, ctx.original_height - 1)
                keypoints.append(Keypoint(
                    x=float(kp_x), y=float(kp_y), confidence=float(ls[idx, k])
                ))

            results.append(PoseResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(scores[idx]),
                class_id=0,
                keypoints=keypoints,
            ))

        return results

    def get_model_name(self) -> str:
        return "yolov5pose_ppu"


class YOLOv10PPUPostprocessor(IPostprocessor):
    """
    YOLOv10 PPU — anchor-free detection postprocessor (corner format).

    Unlike YOLOv8/v11/v12 PPU which output center (cx, cy, w, h),
    YOLOv10 PPU outputs corner (x1, y1, x2, y2) directly in the
    DeviceBoundingBox_t x, y, w, h fields. No center-to-corner conversion.

    DeviceBoundingBox_t layout (32 bytes):
      Bytes  0-15: x1, y1, x2, y2 (float32) — corner coordinates
      Bytes 16-19: grid_y, grid_x, box_idx, layer_idx (uint8) — unused
      Bytes 20-23: score (float32)
      Bytes 24-27: label (uint32)
      Bytes 28-31: padding
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.score_threshold = self.config.get('conf_threshold',
                                               self.config.get('score_threshold', 0.4))
        self.nms_threshold = self.config.get('nms_threshold', 0.5)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        if len(outputs) == 0:
            return []

        output_tensor = outputs[0][0]  # remove batch dim → [N, 32]

        if output_tensor.ndim != 2 or output_tensor.shape[1] != 32:
            return []

        n = output_tensor.shape[0]
        if n == 0:
            return []

        # Parse DeviceBoundingBox_t fields (corner format for YOLOv10)
        boxes_raw = output_tensor[:, :16].view(np.float32).reshape(-1, 4)  # x1, y1, x2, y2
        scores = output_tensor[:, 20:24].view(np.float32).flatten()
        labels = output_tensor[:, 24:28].view(np.uint32).flatten()

        # Score filter
        mask = scores >= self.score_threshold
        if not np.any(mask):
            return []

        boxes_x1y1x2y2 = boxes_raw[mask]
        scores = scores[mask]
        labels = labels[mask]

        # Convert to x1y1wh for NMS
        boxes_x1y1wh = np.column_stack([
            boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 1],
            boxes_x1y1x2y2[:, 2] - boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 3] - boxes_x1y1x2y2[:, 1],
        ])

        indices = cv2.dnn.NMSBoxes(
            boxes_x1y1wh.tolist(),
            scores.tolist(),
            self.score_threshold,
            self.nms_threshold,
        )

        if len(indices) == 0:
            return []

        keep = np.array(indices).reshape(-1)

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

            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(scores[idx]),
                class_id=int(labels[idx])
            ))

        return results

    def get_model_name(self) -> str:
        return "yolov10_ppu"


class YOLOXPPUPostprocessor(IPostprocessor):
    """
    YOLOX PPU — anchor-free detection postprocessor.

    YOLOX PPU output uses DeviceBoundingBox_t (32 bytes) but with a different
    box encoding from the anchor-based YOLOv5/v7 PPU:
      Bytes  0-15: tx, ty, tw, th (float32) — raw (pre-sigmoid) grid offsets
      Bytes 16-19: grid_y, grid_x, box_idx, layer_idx (uint8)
      Bytes 20-23: score (float32)
      Bytes 24-27: label (uint32)
      Bytes 28-31: padding

    Anchor-free box decoding (YOLOX style):
      cx = (tx + grid_x) * stride
      cy = (ty + grid_y) * stride
      w  = exp(tw) * stride
      h  = exp(th) * stride
    """

    STRIDES = np.array([8, 16, 32], dtype=np.float32)

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.score_threshold = self.config.get('conf_threshold',
                                               self.config.get('score_threshold', 0.25))
        self.nms_threshold = self.config.get('nms_threshold', 0.45)

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        if len(outputs) == 0 or outputs[0].ndim == 2:
            return []

        output_tensor = outputs[0][0]  # remove batch dim → [N, 32]

        if output_tensor.ndim != 2 or output_tensor.shape[1] != 32:
            return []

        n = output_tensor.shape[0]
        if n == 0:
            return []

        # Parse DeviceBoundingBox_t fields
        boxes_raw = output_tensor[:, :16].view(np.float32).reshape(-1, 4)  # tx, ty, tw, th
        grid_info = output_tensor[:, 16:20].view(np.uint8)
        g_y = grid_info[:, 0].astype(np.float32)
        g_x = grid_info[:, 1].astype(np.float32)
        layer_idx = grid_info[:, 3]
        scores = output_tensor[:, 20:24].view(np.float32).flatten()
        labels = output_tensor[:, 24:28].view(np.uint32).flatten()

        # Score filter
        mask = scores >= self.score_threshold
        if not np.any(mask):
            return []

        boxes_raw = boxes_raw[mask]
        scores = scores[mask]
        labels = labels[mask]
        g_x = g_x[mask]
        g_y = g_y[mask]
        layer_idx = layer_idx[mask]

        # Anchor-free YOLOX decode: cx=(tx+gx)*s, cy=(ty+gy)*s, w=exp(tw)*s, h=exp(th)*s
        stride = self.STRIDES[layer_idx]
        cx = (boxes_raw[:, 0] + g_x) * stride
        cy = (boxes_raw[:, 1] + g_y) * stride
        tw_clipped = np.clip(boxes_raw[:, 2], -10, 10)  # avoid exp overflow
        th_clipped = np.clip(boxes_raw[:, 3], -10, 10)
        w = np.exp(tw_clipped) * stride
        h = np.exp(th_clipped) * stride

        boxes_x1y1x2y2 = np.column_stack([
            cx - w * 0.5,
            cy - h * 0.5,
            cx + w * 0.5,
            cy + h * 0.5,
        ])

        # Convert to x1y1wh for NMS
        boxes_x1y1wh = np.column_stack([
            boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 1],
            boxes_x1y1x2y2[:, 2] - boxes_x1y1x2y2[:, 0],
            boxes_x1y1x2y2[:, 3] - boxes_x1y1x2y2[:, 1],
        ])

        # Apply NMS
        indices = cv2.dnn.NMSBoxes(
            boxes_x1y1wh.tolist(),
            scores.tolist(),
            self.score_threshold,
            self.nms_threshold,
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

            results.append(DetectionResult(
                box=[float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                confidence=float(scores[idx]),
                class_id=int(labels[idx])
            ))

        return results

    def get_model_name(self) -> str:
        return "yolox_ppu"
