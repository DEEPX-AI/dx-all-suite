"""
Visualization utilities for drawing inference results.
"""

from typing import List, Tuple, Optional
import numpy as np
import cv2

from ..base.i_processor import DetectionResult, SegmentationResult, PreprocessContext

_COCO_LABELS = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush",
]


def get_class_color(class_id: int) -> Tuple[int, int, int]:
    """
    Generate a consistent color for a class ID.
    
    Args:
        class_id: Class identifier
        
    Returns:
        BGR color tuple
    """
    colors = [
        (56, 56, 255),    # Red
        (151, 157, 255),  # Light red
        (31, 112, 255),   # Orange
        (29, 178, 255),   # Yellow
        (49, 210, 207),   # Light yellow
        (10, 249, 72),    # Green
        (23, 204, 146),   # Teal
        (134, 219, 61),   # Light green
        (211, 188, 0),    # Cyan
        (209, 85, 0),     # Light blue
        (255, 0, 0),      # Blue
        (255, 149, 0),    # Sky blue
        (255, 115, 100),  # Light purple
        (255, 64, 255),   # Pink
        (240, 40, 200),   # Magenta
        (128, 0, 128),    # Purple
    ]
    return colors[class_id % len(colors)]


def draw_detection(image: np.ndarray,
                   det: DetectionResult,
                   color: Optional[Tuple[int, int, int]] = None,
                   thickness: int = 2,
                   font_scale: float = 0.5,
                   show_label: bool = True,
                   show_confidence: bool = True) -> np.ndarray:
    """
    Draw a single detection result on an image.
    
    Args:
        image: Input image (will be modified in-place)
        det: Detection result to draw
        color: Override color (auto-generated if None)
        thickness: Line thickness
        font_scale: Font scale for labels
        show_label: Whether to show class label
        show_confidence: Whether to show confidence score
        
    Returns:
        Image with detection drawn
    """
    if len(det.box) < 4:
        return image
    
    x1, y1, x2, y2 = [int(v) for v in det.box[:4]]
    
    # Use class-based color if not specified
    if color is None:
        color = get_class_color(det.class_id)
    
    # Draw bounding box
    cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
    
    # Draw label
    if show_label or show_confidence:
        label_parts = []
        if show_label:
            label_parts.append(det.class_name if det.class_name else f"cls_{det.class_id}")
        if show_confidence:
            label_parts.append(f"{det.confidence:.2f}")
        
        label = ": ".join(label_parts) if len(label_parts) == 2 else label_parts[0]
        
        # Calculate label size
        (label_w, label_h), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1
        )
        
        # Draw label background
        cv2.rectangle(image, (x1, y1 - label_h - 10), (x1 + label_w + 5, y1), color, -1)
        
        # Draw label text
        cv2.putText(image, label, (x1 + 2, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 1)
    
    return image


def draw_detections(image: np.ndarray,
                    detections: List[DetectionResult],
                    thickness: int = 2,
                    font_scale: float = 0.5,
                    show_labels: bool = True,
                    show_confidence: bool = True,
                    copy: bool = True) -> np.ndarray:
    """
    Draw multiple detection results on an image.
    
    Args:
        image: Input image
        detections: List of DetectionResult objects
        thickness: Line thickness
        font_scale: Font scale for labels
        show_labels: Whether to show class labels
        show_confidence: Whether to show confidence scores
        copy: Whether to make a copy of the image
        
    Returns:
        Image with detections drawn
    """
    result = image.copy() if copy else image
    
    for det in detections:
        draw_detection(result, det, thickness=thickness, font_scale=font_scale,
                       show_label=show_labels, show_confidence=show_confidence)
    
    return result


def draw_segmentation(image: np.ndarray,
                      seg_result: SegmentationResult,
                      alpha: float = 0.5,
                      copy: bool = True) -> np.ndarray:
    """
    Draw segmentation mask overlay on an image.
    
    Args:
        image: Input image
        seg_result: Segmentation result with mask
        alpha: Overlay transparency (0.0 to 1.0)
        copy: Whether to make a copy of the image
        
    Returns:
        Image with segmentation overlay
    """
    result = image.copy() if copy else image
    
    if seg_result.mask.size == 0:
        return result
    
    # Resize mask to image size if needed
    h, w = result.shape[:2]
    mask = seg_result.mask
    
    if mask.shape[:2] != (h, w):
        mask = cv2.resize(mask.astype(np.float32), (w, h), 
                          interpolation=cv2.INTER_NEAREST).astype(np.int32)
    
    # Create color overlay
    overlay = np.zeros_like(result)
    unique_classes = np.unique(mask)
    
    for class_id in unique_classes:
        if class_id == 0:  # Skip background
            continue
        color = get_class_color(int(class_id))
        overlay[mask == class_id] = color
    
    # Blend with original image
    result = cv2.addWeighted(result, 1 - alpha, overlay, alpha, 0)
    
    return result


def draw_classification_result(image: np.ndarray,
                               class_name: str,
                               confidence: float,
                               position: Tuple[int, int] = (10, 30),
                               font_scale: float = 1.0,
                               color: Tuple[int, int, int] = (0, 255, 0),
                               copy: bool = True) -> np.ndarray:
    """
    Draw classification result text on an image.
    
    Args:
        image: Input image
        class_name: Predicted class name
        confidence: Confidence score
        position: Text position (x, y)
        font_scale: Font scale
        color: Text color (BGR)
        copy: Whether to make a copy of the image
        
    Returns:
        Image with classification text
    """
    result = image.copy() if copy else image
    
    text = f"{class_name}: {confidence:.2%}"
    
    # Draw background rectangle
    (text_w, text_h), _ = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2
    )
    x, y = position
    cv2.rectangle(result, (x - 5, y - text_h - 10), (x + text_w + 5, y + 5), (0, 0, 0), -1)
    
    # Draw text
    cv2.putText(result, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 2)
    
    return result


def add_fps_counter(image: np.ndarray,
                    fps: float,
                    position: Tuple[int, int] = (10, 30),
                    font_scale: float = 0.8,
                    copy: bool = True) -> np.ndarray:
    """
    Add FPS counter to an image.
    
    Args:
        image: Input image
        fps: Current FPS value
        position: Text position (x, y)
        font_scale: Font scale
        copy: Whether to make a copy of the image
        
    Returns:
        Image with FPS counter
    """
    result = image.copy() if copy else image
    
    text = f"FPS: {fps:.1f}"
    cv2.putText(result, text, position, cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, (0, 255, 0), 2)
    
    return result


# --- C++ postprocessor visualization helpers ---

# VOC 21-class color palette (used by DeepLabv3)
_VOC_PALETTE = [
    (0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128),
    (128, 0, 128), (0, 128, 128), (128, 128, 128), (64, 0, 0), (192, 0, 0),
    (64, 128, 0), (192, 128, 0), (64, 0, 128), (192, 0, 128), (64, 128, 128),
    (192, 128, 128), (0, 64, 0), (128, 64, 0), (0, 192, 0), (128, 192, 0),
    (0, 64, 128),
]


def deeplabv3_cpp_visualize(image: np.ndarray, class_map: np.ndarray,
                            visualizer, ctx=None) -> np.ndarray:
    """Visualize semantic segmentation C++ postprocessor results."""
    if class_map is None or class_map.size == 0:
        return image

    h, w = image.shape[:2]
    color_palette = getattr(visualizer, 'color_palette', _VOC_PALETTE)

    cm_h, cm_w = class_map.shape[:2]
    colored_mask_small = np.zeros((cm_h, cm_w, 3), dtype=np.uint8)
    for class_id in range(len(color_palette)):
        if class_id == 0:
            continue
        mask = class_map.astype(np.int32) == class_id
        if np.any(mask):
            colored_mask_small[mask] = color_palette[class_id]

    colored_mask = cv2.resize(colored_mask_small, (w, h), interpolation=cv2.INTER_LINEAR)

    alpha = 0.6
    output = image.copy()
    cv2.addWeighted(output, 1 - alpha, colored_mask, alpha, 0, dst=output)
    return output


def yolov8seg_cpp_visualize(image: np.ndarray, results,
                            visualizer, ctx=None) -> np.ndarray:
    """
    Visualize YOLOv8-Seg C++ postprocessor results (detections + masks).

    Masks from the C++ postprocessor are in model input space (with letterbox
    padding). This function removes padding before resizing masks to the
    original image dimensions, and scales bounding box coordinates accordingly.
    """
    from .preprocessing import scale_to_original

    detections, masks = results
    h, w = image.shape[:2]
    output = image.copy()

    has_padding = ctx is not None and (ctx.pad_x > 0 or ctx.pad_y > 0)

    for i, mask in enumerate(masks):
        if i >= len(detections):
            break
        # Use instance index for color so each segment gets a distinct color
        # (important for class-agnostic models like FastSAM where all class_id=0)
        color = visualizer.color_palette[i % len(visualizer.color_palette)]

        if has_padding:
            gain = max(ctx.scale, 1e-6)
            unpad_h = int(round(ctx.original_height * gain))
            unpad_w = int(round(ctx.original_width * gain))
            top, left = int(ctx.pad_y), int(ctx.pad_x)
            mask_crop = mask[top:top + unpad_h, left:left + unpad_w]
            if mask_crop.size == 0:
                continue
            mask_resized = cv2.resize(mask_crop, (w, h), interpolation=cv2.INTER_LINEAR)
        else:
            mask_resized = cv2.resize(mask, (w, h), interpolation=cv2.INTER_LINEAR)

        m = mask_resized > (127 if mask_resized.dtype == np.uint8 else 0.5)
        output[m] = (output[m] * 0.6 + np.array(color) * 0.4).astype(np.uint8)

    # Draw bounding boxes and labels (skip if visualizer has show_boxes=False)
    show_boxes = getattr(visualizer, 'show_boxes', True)
    if show_boxes:
        for det in detections:
            x1, y1, x2, y2, score, class_id = det[:6]
            if ctx is not None:
                x1, y1 = scale_to_original(float(x1), float(y1), ctx)
                x2, y2 = scale_to_original(float(x2), float(y2), ctx)
            color = visualizer.color_palette[int(class_id) % len(visualizer.color_palette)]
            cv2.rectangle(output, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cls_id = int(class_id)
            # Use visualizer labels if available, fall back to COCO
            labels = getattr(visualizer, 'labels', None) or _COCO_LABELS
            cls_name = labels[cls_id] if cls_id < len(labels) else str(cls_id)
            label = f"{cls_name} {score:.2f}"
            cv2.putText(output, label, (int(x1), int(y1) - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    return output


def depth_cpp_visualize(image: np.ndarray, depth_map: np.ndarray,
                        _visualizer, ctx=None) -> np.ndarray:
    """
    Visualize DepthPostProcess C++ results (uint8 depth map).

    Resizes depth map to original image size and applies colormap.

    Args:
        image: Original input image (BGR)
        depth_map: uint8 depth map from C++ postprocessor [H, W]
        _visualizer: Visualizer instance (unused but required by interface)

    Returns:
        Colorized depth image
    """
    h, w = image.shape[:2]
    depth_resized = cv2.resize(
        depth_map.astype(np.uint8), (w, h), interpolation=cv2.INTER_LINEAR
    )
    depth_color = cv2.applyColorMap(depth_resized, cv2.COLORMAP_MAGMA)
    return depth_color
