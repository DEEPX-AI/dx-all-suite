"""
Image preprocessing utilities.
"""

from typing import Tuple
import numpy as np
import cv2

from ..base.i_processor import PreprocessContext


def calculate_letterbox_params(original_width: int, original_height: int,
                               target_width: int, target_height: int) -> Tuple[float, int, int]:
    """
    Calculate letterbox scaling parameters.
    
    Args:
        original_width: Original image width
        original_height: Original image height
        target_width: Target (model input) width
        target_height: Target (model input) height
        
    Returns:
        Tuple of (scale_factor, pad_x, pad_y)
    """
    scale = min(target_width / original_width, target_height / original_height)
    
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)
    
    pad_x = (target_width - new_width) // 2
    pad_y = (target_height - new_height) // 2
    
    return scale, pad_x, pad_y


def make_letterbox_image(image: np.ndarray,
                         target_width: int,
                         target_height: int,
                         color: Tuple[int, int, int] = (114, 114, 114),
                         return_context: bool = True) -> Tuple[np.ndarray, PreprocessContext]:
    """
    Create a letterboxed image maintaining aspect ratio.
    
    This is the standard preprocessing for YOLO models that maintains
    aspect ratio and pads with a solid color.
    
    Args:
        image: Input image (BGR format)
        target_width: Target output width
        target_height: Target output height
        color: Padding color (B, G, R)
        return_context: Whether to return preprocessing context
        
    Returns:
        Tuple of (letterboxed_image, preprocessing_context)
    """
    original_height, original_width = image.shape[:2]

    # Legacy-style letterbox (matches original implementation)
    r = min(target_height / original_height, target_width / original_width)
    new_unpad_w = int(round(original_width * r))
    new_unpad_h = int(round(original_height * r))

    dw = (target_width - new_unpad_w) / 2
    dh = (target_height - new_unpad_h) / 2

    if (original_width, original_height) != (new_unpad_w, new_unpad_h):
        resized = cv2.resize(image, (new_unpad_w, new_unpad_h), interpolation=cv2.INTER_LINEAR)
    else:
        resized = image

    top = int(round(dh - 0.1))
    bottom = int(round(dh + 0.1))
    left = int(round(dw - 0.1))
    right = int(round(dw + 0.1))

    letterboxed = cv2.copyMakeBorder(
        resized,
        top,
        bottom,
        left,
        right,
        cv2.BORDER_CONSTANT,
        value=color,
    )

    ctx = PreprocessContext(
        pad_x=left,
        pad_y=top,
        scale=r,
        original_width=original_width,
        original_height=original_height,
        input_width=target_width,
        input_height=target_height,
    )

    return letterboxed, ctx


def scale_to_original(x: float, y: float, ctx: PreprocessContext) -> Tuple[float, float]:
    """
    Scale coordinates from model space back to original image space.
    
    Args:
        x: X coordinate in model input space
        y: Y coordinate in model input space
        ctx: Preprocessing context with scale and padding info
        
    Returns:
        Tuple of (original_x, original_y)
    """
    # Remove padding
    x = x - ctx.pad_x
    y = y - ctx.pad_y

    # Inverse scale. If per-axis scale factors are provided, use them
    # (correct for stretched resize). Otherwise fall back to uniform scale.
    if hasattr(ctx, 'scale_x') and hasattr(ctx, 'scale_y') and ctx.scale_x > 0 and ctx.scale_y > 0:
        x = x / ctx.scale_x
        y = y / ctx.scale_y
    elif ctx.scale > 0:
        x = x / ctx.scale
        y = y / ctx.scale
    
    # Clamp to original bounds
    x = max(0.0, min(x, ctx.original_width - 1))
    y = max(0.0, min(y, ctx.original_height - 1))
    
    return x, y


def resize_with_padding(image: np.ndarray,
                        target_size: Tuple[int, int],
                        mode: str = 'letterbox') -> Tuple[np.ndarray, PreprocessContext]:
    """
    Resize image with various padding strategies.
    
    Args:
        image: Input image (BGR format)
        target_size: (width, height) tuple
        mode: 'letterbox', 'stretch', or 'crop'
        
    Returns:
        Tuple of (resized_image, preprocessing_context)
    """
    target_width, target_height = target_size
    
    if mode == 'letterbox':
        return make_letterbox_image(image, target_width, target_height)
    
    elif mode == 'stretch':
        original_height, original_width = image.shape[:2]
        resized = cv2.resize(image, (target_width, target_height))
        ctx = PreprocessContext(
            pad_x=0, pad_y=0,
            scale=min(target_width / original_width, target_height / original_height),
            original_width=original_width,
            original_height=original_height,
            input_width=target_width,
            input_height=target_height
        )
        return resized, ctx
    
    elif mode == 'crop':
        original_height, original_width = image.shape[:2]
        
        # Calculate crop to maintain aspect ratio
        aspect = target_width / target_height
        if original_width / original_height > aspect:
            new_width = int(original_height * aspect)
            start_x = (original_width - new_width) // 2
            cropped = image[:, start_x:start_x + new_width]
        else:
            new_height = int(original_width / aspect)
            start_y = (original_height - new_height) // 2
            cropped = image[start_y:start_y + new_height, :]
        
        resized = cv2.resize(cropped, (target_width, target_height))
        ctx = PreprocessContext(
            pad_x=0, pad_y=0,
            scale=1.0,
            original_width=original_width,
            original_height=original_height,
            input_width=target_width,
            input_height=target_height
        )
        return resized, ctx
    
    else:
        raise ValueError(f"Unknown resize mode: {mode}")


def normalize_image(image: np.ndarray,
                    mean: Tuple[float, float, float] = (0.485, 0.456, 0.406),
                    std: Tuple[float, float, float] = (0.229, 0.224, 0.225)) -> np.ndarray:
    """
    Normalize image for ImageNet-pretrained models.
    
    Args:
        image: Input image (0-255 range, HWC format)
        mean: Per-channel mean (RGB order)
        std: Per-channel standard deviation (RGB order)
        
    Returns:
        Normalized image as float32
    """
    img = image.astype(np.float32) / 255.0
    
    # Convert BGR to RGB if needed (assuming input is BGR from OpenCV)
    img = img[:, :, ::-1]
    
    # Normalize
    img = (img - np.array(mean)) / np.array(std)
    
    return img.astype(np.float32)


def hwc_to_chw(image: np.ndarray) -> np.ndarray:
    """Convert HWC (Height, Width, Channels) to CHW format."""
    return np.transpose(image, (2, 0, 1))


def chw_to_hwc(image: np.ndarray) -> np.ndarray:
    """Convert CHW (Channels, Height, Width) to HWC format."""
    return np.transpose(image, (1, 2, 0))
