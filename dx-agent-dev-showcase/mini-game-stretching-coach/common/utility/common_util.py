"""
Common utility functions for neural network operations.
"""

import os
import subprocess
from typing import List, Tuple
import numpy as np
import cv2


# ---------------------------------------------------------------------------
# Screen-aware display window
# ---------------------------------------------------------------------------
_window_initialized = False


def _get_screen_resolution():
    """Return (width, height) of the primary monitor.

    Detection order:
      1. DXAPP_SCREEN_W / DXAPP_SCREEN_H environment variables
      2. xdpyinfo (X11)
      3. Fallback 1920×1080
    """
    env_w = os.environ.get("DXAPP_SCREEN_W")
    env_h = os.environ.get("DXAPP_SCREEN_H")
    if env_w and env_h:
        try:
            w, h = int(env_w), int(env_h)
            if w > 0 and h > 0:
                return w, h
        except ValueError:
            pass

    try:
        result = subprocess.run(
            ["xdpyinfo"], capture_output=True, text=True, timeout=2,
        )
        for line in result.stdout.splitlines():
            if "dimensions" in line:
                # "  dimensions:    2560x1440 pixels ..."
                part = line.split(":")[1].strip().split()[0]
                w, h = part.split("x")
                return int(w), int(h)
    except Exception:
        pass

    return 1920, 1080


def show_output(img, winname: str = "Output"):
    """Display *img* in a resizable OpenCV window.

    On the first call the window is created and sized to half the screen
    width and half the screen height (≈ 1/4 screen area), preserving the
    frame's aspect ratio.  Subsequent calls just update the image.
    """
    if img is None:
        return
    global _window_initialized
    if not _window_initialized:
        cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
        screen_w, screen_h = _get_screen_resolution()
        target_w = screen_w // 2
        target_h = screen_h // 2
        h, w = img.shape[:2]
        if h > 0 and w > 0:
            scale = min(target_w / w, target_h / h)
            cv2.resizeWindow(winname, int(w * scale), int(h * scale))
        _window_initialized = True
    cv2.imshow(winname, img)


def sigmoid(x: np.ndarray) -> np.ndarray:
    """
    Compute sigmoid activation.
    
    Args:
        x: Input array
        
    Returns:
        Sigmoid-activated array
    """
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Compute softmax activation.
    
    Args:
        x: Input array
        axis: Axis to apply softmax over
        
    Returns:
        Softmax-activated array
    """
    exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return exp_x / np.sum(exp_x, axis=axis, keepdims=True)


def argmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """
    Get argmax indices.
    
    Args:
        x: Input array
        axis: Axis to find argmax over
        
    Returns:
        Array of indices
    """
    return np.argmax(x, axis=axis)


def iou(box1: np.ndarray, box2: np.ndarray) -> float:
    """
    Calculate Intersection over Union for two boxes.
    
    Args:
        box1: First box [x1, y1, x2, y2]
        box2: Second box [x1, y1, x2, y2]
        
    Returns:
        IoU value
    """
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])
    
    if x_right < x_left or y_bottom < y_top:
        return 0.0
    
    intersection = (x_right - x_left) * (y_bottom - y_top)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0.0


def nms(boxes: np.ndarray, scores: np.ndarray, 
        iou_threshold: float = 0.45) -> List[int]:
    """
    Apply Non-Maximum Suppression.
    
    Args:
        boxes: Array of boxes [N, 4] in [x1, y1, x2, y2] format
        scores: Array of confidence scores [N]
        iou_threshold: IoU threshold for suppression
        
    Returns:
        List of indices to keep
    """
    if len(boxes) == 0:
        return []
    
    # Sort by score
    indices = np.argsort(scores)[::-1]
    keep = []
    
    while len(indices) > 0:
        current = indices[0]
        keep.append(int(current))
        
        if len(indices) == 1:
            break
        
        # Calculate IoU with remaining boxes
        remaining = indices[1:]
        ious = np.array([iou(boxes[current], boxes[i]) for i in remaining])
        
        # Keep boxes with IoU below threshold
        indices = remaining[ious < iou_threshold]
    
    return keep


def nms_by_class(boxes: np.ndarray, scores: np.ndarray, 
                 class_ids: np.ndarray, iou_threshold: float = 0.45) -> List[int]:
    """
    Apply NMS per class.
    
    Args:
        boxes: Array of boxes [N, 4]
        scores: Array of confidence scores [N]
        class_ids: Array of class IDs [N]
        iou_threshold: IoU threshold for suppression
        
    Returns:
        List of indices to keep
    """
    if len(boxes) == 0:
        return []
    
    keep = []
    unique_classes = np.unique(class_ids)
    
    for cls in unique_classes:
        mask = class_ids == cls
        cls_indices = np.where(mask)[0]
        cls_keep = nms(boxes[mask], scores[mask], iou_threshold)
        keep.extend([cls_indices[i] for i in cls_keep])
    
    return sorted(keep)


def xywh_to_xyxy(boxes: np.ndarray) -> np.ndarray:
    """
    Convert boxes from [x_center, y_center, width, height] to [x1, y1, x2, y2].
    
    Args:
        boxes: Array of boxes [N, 4] in xywh format
        
    Returns:
        Array of boxes [N, 4] in xyxy format
    """
    result = np.zeros_like(boxes)
    result[:, 0] = boxes[:, 0] - boxes[:, 2] / 2  # x1
    result[:, 1] = boxes[:, 1] - boxes[:, 3] / 2  # y1
    result[:, 2] = boxes[:, 0] + boxes[:, 2] / 2  # x2
    result[:, 3] = boxes[:, 1] + boxes[:, 3] / 2  # y2
    return result


def xyxy_to_xywh(boxes: np.ndarray) -> np.ndarray:
    """
    Convert boxes from [x1, y1, x2, y2] to [x_center, y_center, width, height].
    
    Args:
        boxes: Array of boxes [N, 4] in xyxy format
        
    Returns:
        Array of boxes [N, 4] in xywh format
    """
    result = np.zeros_like(boxes)
    result[:, 0] = (boxes[:, 0] + boxes[:, 2]) / 2  # x_center
    result[:, 1] = (boxes[:, 1] + boxes[:, 3]) / 2  # y_center
    result[:, 2] = boxes[:, 2] - boxes[:, 0]  # width
    result[:, 3] = boxes[:, 3] - boxes[:, 1]  # height
    return result


def clip_boxes(boxes: np.ndarray, width: int, height: int) -> np.ndarray:
    """
    Clip boxes to image boundaries.
    
    Args:
        boxes: Array of boxes [N, 4] in xyxy format
        width: Image width
        height: Image height
        
    Returns:
        Clipped boxes
    """
    result = boxes.copy()
    result[:, 0] = np.clip(result[:, 0], 0, width)
    result[:, 1] = np.clip(result[:, 1], 0, height)
    result[:, 2] = np.clip(result[:, 2], 0, width)
    result[:, 3] = np.clip(result[:, 3], 0, height)
    return result


def convert_cpp_detections(detections: np.ndarray) -> List:
    """
    Convert C++ postprocessor output (numpy array) to DetectionResult objects.
    
    C++ postprocessors return numpy arrays of shape [N, 6] where each row is:
    [x1, y1, x2, y2, confidence, class_id]
    
    Args:
        detections: numpy array of shape [N, 6] from C++ postprocessor
        
    Returns:
        List of DetectionResult-compatible objects
    """
    from ..base import DetectionResult
    
    results = []
    if detections is None or len(detections) == 0:
        return results
    
    for det in detections:
        result = DetectionResult(
            box=[float(det[0]), float(det[1]), float(det[2]), float(det[3])],
            confidence=float(det[4]),
            class_id=int(det[5])
        )
        results.append(result)
    
    return results


def convert_cpp_face_detections(detections: np.ndarray) -> List:
    """
    Convert C++ face postprocessor output (numpy array) to FaceResult with keypoints.
    
    Args:
        detections: numpy array [N, 6+keypoints] from C++ postprocessor
                   [x1, y1, x2, y2, confidence, class_id, kp1_x, kp1_y, ...]
    
    Returns:
        List of FaceResult objects with Keypoint objects
    """
    from ..processors.face_postprocessor import FaceResult
    from ..base import Keypoint
    
    results = []
    if detections is None or len(detections) == 0:
        return results
    
    NUM_FACE_KEYPOINTS = 5  # SCRFD / YOLOv5Face: 5 landmarks
    for det in detections:
        # Parse keypoints as Keypoint objects (x, y pairs)
        kp_data = det[6:].flatten() if hasattr(det[6:], 'flatten') else list(det[6:])
        # Limit to expected number of keypoints to ignore trailing garbage data
        max_values = NUM_FACE_KEYPOINTS * 2
        kp_data = kp_data[:max_values]
        keypoints = []
        for i in range(0, len(kp_data) - 1, 2):
            keypoints.append(Keypoint(
                x=float(kp_data[i]),
                y=float(kp_data[i + 1]),
                confidence=1.0
            ))
        
        result = FaceResult(
            box=[float(det[0]), float(det[1]), float(det[2]), float(det[3])],
            confidence=float(det[4]),
            class_id=int(det[5]),
            keypoints=keypoints
        )
        results.append(result)
    
    return results


def convert_cpp_pose_detections(detections: np.ndarray) -> List:
    """
    Convert C++ pose postprocessor output (numpy array) to PoseResult objects.
    
    Args:
        detections: numpy array [N, 6+keypoints] from C++ postprocessor
                   [x1, y1, x2, y2, confidence, class_id, kp1_x, kp1_y, kp1_conf, ...]
    
    Returns:
        List of PoseResult-compatible objects with keypoints
    """
    from ..base import PoseResult, Keypoint
    
    results = []
    if detections is None or len(detections) == 0:
        return results
    
    for det in detections:
        keypoint_data = det[6:] if len(det) > 6 else []
        keypoints = []
        
        # Parse keypoints (x, y, conf) triplets
        for i in range(0, len(keypoint_data) - 2, 3):
            kp = Keypoint(
                x=float(keypoint_data[i]),
                y=float(keypoint_data[i + 1]),
                confidence=float(keypoint_data[i + 2])
            )
            keypoints.append(kp)
        
        result = PoseResult(
            box=[float(det[0]), float(det[1]), float(det[2]), float(det[3])],
            confidence=float(det[4]),
            class_id=int(det[5]),
            keypoints=keypoints
        )
        results.append(result)
    
    return results


def convert_cpp_classification(predictions: np.ndarray) -> List:
    """
    Convert C++ classification postprocessor output to ClassificationResult objects.

    Args:
        predictions: numpy array [K, 2] where each row is [class_id, confidence]

    Returns:
        List of ClassificationResult
    """
    from ..base import ClassificationResult

    results = []
    if predictions is None or len(predictions) == 0:
        return results

    for pred in predictions:
        results.append(ClassificationResult(
            class_id=int(pred[0]),
            confidence=float(pred[1]),
            class_name=""
        ))

    return results


def convert_cpp_obb_detections(detections: np.ndarray) -> List:
    """
    Convert C++ OBB postprocessor output to OBBResult objects.

    Args:
        detections: numpy array [N, 7] where each row is
                   [cx, cy, w, h, confidence, class_id, angle]

    Returns:
        List of OBBResult
    """
    from ..base import OBBResult
    from ..processors.obb_postprocessor import DOTAV1_LABELS

    results = []
    if detections is None or len(detections) == 0:
        return results

    for det in detections:
        cid = int(det[5])
        class_name = DOTAV1_LABELS[cid] if 0 <= cid < len(DOTAV1_LABELS) else f"class_{cid}"
        results.append(OBBResult(
            cx=float(det[0]),
            cy=float(det[1]),
            width=float(det[2]),
            height=float(det[3]),
            confidence=float(det[4]),
            class_id=cid,
            angle=float(det[6]),
            class_name=class_name
        ))

    return results


def convert_cpp_embedding(embedding: np.ndarray) -> List:
    """
    Convert C++ embedding postprocessor output to EmbeddingResult.

    Args:
        embedding: numpy array [D] - L2-normalized embedding vector

    Returns:
        List containing a single EmbeddingResult
    """
    from ..base import EmbeddingResult

    if embedding is None or len(embedding) == 0:
        return []

    return [EmbeddingResult(embedding=embedding)]


def convert_cpp_hand_landmark(result_tuple, ctx=None) -> list:
    """
    Convert C++ HandLandmarkPostProcess output to HandLandmarkResult list.

    Args:
        result_tuple: tuple(landmarks[21,3], confidence, handedness) from dx_postprocess.
        ctx: Optional PreprocessContext for coordinate scaling.

    Returns:
        List containing a single HandLandmarkResult.
    """
    from ..base import HandLandmarkResult

    landmarks, confidence, handedness = result_tuple
    landmarks = np.asarray(landmarks, dtype=np.float32)

    if landmarks.size == 0:
        return []

    # Scale normalized [0,1] coords to original image space if context available
    if ctx is not None:
        landmarks[:, 0] *= ctx.original_width
        landmarks[:, 1] *= ctx.original_height

    result = HandLandmarkResult(
        landmarks=landmarks,
        confidence=float(confidence),
        handedness=str(handedness)
    )
    return [result]


def convert_cpp_zero_dce(image: np.ndarray, ctx=None) -> list:
    """
    Convert C++ Zero-DCE postprocessor output to EnhancedImageResult list.

    Args:
        image: numpy array - raw curve params [24, H, W] or enhanced image
               [C, H, W] float32 / [H, W, C] uint8.
        ctx: Optional PreprocessContext with normalized_input for LE curve application.

    Returns:
        List containing a single EnhancedImageResult
    """
    from ..base import EnhancedImageResult

    if image is None:
        return []

    img = np.asarray(image)

    if img.ndim == 3 and img.shape[0] not in (1, 3):
        return _apply_le_curves_from_params(img, ctx)

    if img.ndim == 3 and img.shape[0] in (1, 3) and img.dtype in (np.float32, np.float64):
        if img.shape[0] == 3:
            img = np.transpose(img, (1, 2, 0))  # CHW → HWC
        else:
            img = img.squeeze(0)  # 1HW → HW
        img = np.clip(img, 0.0, 1.0)
        if img.ndim == 3 and img.shape[2] == 3:
            img = img[:, :, ::-1]  # RGB → BGR
        img = (img * 255.0).astype(np.uint8)

    return [EnhancedImageResult(output_image=img)]


def convert_cpp_face3d(params: np.ndarray, ctx=None) -> list:
    """
    Convert C++ Face3DPostProcess output to FaceAlignmentResult list.

    Uses BFM (Basel Face Model) data to reconstruct 68 facial landmarks
    from the 62 raw 3DMM parameters output by 3DDFA v2.

    Args:
        params: numpy array of raw 3DMM parameters (62 floats)
        ctx: Optional PreprocessContext with original image dimensions.

    Returns:
        List containing a single FaceAlignmentResult
    """
    from ..base import FaceAlignmentResult
    from ..processors._bfm_data import load_bfm as _load_bfm
    import math

    if params is None or len(params) == 0:
        return []

    raw = np.asarray(params, dtype=np.float32).flatten()
    result = FaceAlignmentResult()
    result.params = raw

    INPUT_W, INPUT_H = 120, 120

    bfm = _load_bfm()

    # Denormalize
    p = raw * bfm['param_std'] + bfm['param_mean']

    # Parse affine
    R_ = p[:12].reshape(3, 4)
    R = R_[:, :3]
    offset = R_[:, 3:].reshape(3, 1)
    alpha_shp = p[12:52].reshape(-1, 1)
    alpha_exp = p[52:62].reshape(-1, 1)

    # Euler angles
    sy = float(np.clip(R[2, 0], -1.0, 1.0))
    pitch = math.asin(sy)
    cp = math.cos(pitch)
    if abs(cp) > 1e-6:
        yaw = math.atan2(float(R[2, 1]) / cp, float(R[2, 2]) / cp)
        roll = math.atan2(float(R[1, 0]) / cp, float(R[0, 0]) / cp)
    else:
        yaw = 0.0
        roll = math.atan2(float(-R[0, 1]), float(R[1, 1]))
    result.pose = [math.degrees(yaw), math.degrees(pitch), math.degrees(roll)]

    # Reconstruct 68 landmarks: pts3d = R @ (u + W_shp@a_shp + W_exp@a_exp) + offset
    shp_deform = np.einsum('ijk,kl->ij', bfm['w_shp_base'], alpha_shp)
    exp_deform = np.einsum('ijk,kl->ij', bfm['w_exp_base'], alpha_exp)
    vertices = bfm['u_base'] + shp_deform + exp_deform
    pts3d = R @ vertices + offset  # (3, 68)

    # y-flip: BFM y-up → image y-down
    pts3d[0, :] -= 1
    pts3d[1, :] = INPUT_H - pts3d[1, :]

    ow = ctx.original_width if ctx and hasattr(ctx, 'original_width') and ctx.original_width > 0 else INPUT_W
    oh = ctx.original_height if ctx and hasattr(ctx, 'original_height') and ctx.original_height > 0 else INPUT_H
    sx, sy_s = ow / INPUT_W, oh / INPUT_H

    lmks = np.zeros((68, 2), dtype=np.float32)
    lmks[:, 0] = pts3d[0, :] * sx
    lmks[:, 1] = pts3d[1, :] * sy_s

    result.landmarks_2d = lmks
    result.landmarks_3d = np.column_stack([lmks, np.zeros(len(lmks))])
    return [result]


def _apply_le_curves_from_params(params: np.ndarray, ctx) -> list:
    """Apply iterative LE curves from raw curve parameters [24, H, W]."""
    from ..base import EnhancedImageResult

    h, w = params.shape[1], params.shape[2]
    n_iters = params.shape[0] // 3

    if ctx is not None and hasattr(ctx, 'normalized_input') and ctx.normalized_input is not None:
        enhanced = ctx.normalized_input.copy().astype(np.float32)
        if enhanced.ndim == 3 and enhanced.shape[0] != 3 and enhanced.shape[2] == 3:
            enhanced = np.transpose(enhanced, (2, 0, 1))
        if enhanced.shape[1] != h or enhanced.shape[2] != w:
            resized = np.zeros((3, h, w), dtype=np.float32)
            for c in range(3):
                resized[c] = cv2.resize(enhanced[c], (w, h), interpolation=cv2.INTER_LINEAR)
            enhanced = resized
    else:
        enhanced = np.full((3, h, w), 0.5, dtype=np.float32)

    for i in range(n_iters):
        alpha = params[i * 3:(i + 1) * 3]
        enhanced = enhanced + alpha * enhanced * (1.0 - enhanced)
    enhanced = np.clip(enhanced, 0.0, 1.0)

    img_out = np.transpose(enhanced, (1, 2, 0))[:, :, ::-1]  # CHW RGB → HWC BGR

    if ctx is not None and hasattr(ctx, 'original_width') and ctx.original_width > 0 and ctx.original_height > 0:
        if img_out.shape[1] != ctx.original_width or img_out.shape[0] != ctx.original_height:
            img_out = cv2.resize(img_out, (ctx.original_width, ctx.original_height),
                                 interpolation=cv2.INTER_LINEAR)

    return [EnhancedImageResult(output_image=(img_out * 255.0).astype(np.uint8))]
