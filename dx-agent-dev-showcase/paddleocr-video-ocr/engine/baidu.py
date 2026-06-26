import logging
from typing import List, Tuple
from dataclasses import dataclass
from PIL import Image, ImageOps
import cv2
import numpy as np

# Configure logging - set to INFO to reduce noise from PIL and multipart
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress debug logs from PIL and multipart
logging.getLogger('PIL').setLevel(logging.INFO)
logging.getLogger('multipart').setLevel(logging.INFO)

det_preprocess = [           
            {
                "resize": {
                    "mode": "ppocr",
                    "size": [640, 640],
                }
            },
            {
                "div": {
                    "x": 255
                }
            },
            {
                "normalize": {
                    "std": [0.229, 0.224, 0.225],
                    "mean": [0.485, 0.456, 0.406],
                }
            },
            {
                "transpose": {"axis": [2, 0, 1]}
            },
        ]

cls_preprocess = [
            {
                "resize": {
                    "mode": "default",
                    "size": [80, 160],
                }
            },
            {
                "div": {
                    "x": 255
                }
            },
            {
                "normalize": {
                    "std": [0.229, 0.224, 0.225],
                    "mean": [0.485, 0.456, 0.406],
                }
            },
            {
                "transpose": {"axis": [2, 0, 1]}
            },
        ]

rec_preprocess = [
            {
                "resize": {
                    "mode": "ppocr",
                    "size": [48, 320],
                },
            },
            {
                "div": {
                    "x": 255
                }
            },
            {
                "normalize": {
                    "std": [0.5, 0.5, 0.5],
                    "mean": [0.5, 0.5, 0.5],
                }
            },
            {
                "transpose": {"axis": [2, 0, 1]}
            },
        ]

doc_ori_preprocess = [
            {
                "resize": {
                    "mode": "short",  # PaddleClas resize_short: resize shorter side to 256
                    "size": [256, 256],
                }
            },
            {
                "centercrop": {
                    "height": 224,  # PaddleClas center crop to 224x224
                    "width": 224,
                }
            },
            {
                "div": {
                    "x": 255  # Scale to [0, 1]
                }
            },
            {
                "normalize": {
                    "std": [0.229, 0.224, 0.225],  # ImageNet std
                    "mean": [0.485, 0.456, 0.406],  # ImageNet mean
                }
            },
            {
                "transpose": {"axis": [2, 0, 1]}  # HWC -> CHW
            },
        ]

uvdoc_preprocess =  [
            {
                "resize": {
                    "mode": "default",
                    "size": [712, 488],
                }
            },
            {
                "div": {
                    "x": 255
                }
            },
            {
                "transpose": {"axis": [2, 0, 1]}
            },
        ]

def add_white_border(img: Image):
    border_width = 200
    border_color = (255, 255, 255)
    img_with_border = ImageOps.expand(img, border=border_width, fill=border_color)
    return img_with_border

def poly2bbox(poly):
    L = poly[0]
    U = poly[1]
    R = poly[2]
    D = poly[5]
    L, R = min(L, R), max(L, R)
    U, D = min(U, D), max(U, D)
    bbox = [L, U, R, D]
    return bbox

@dataclass
class OCRResult:
    """Class to store OCR detection and recognition results"""
    text: str
    confidence: float
    bbox: List[List[float]]
    type: str = "text"


def resize_align_corners(image: np.ndarray, target_size: Tuple[int, int], mode: str = "linear") -> np.ndarray:
    src_h, src_w = image.shape[:2]
    target_h, target_w = target_size
    
    if src_h == target_h and src_w == target_w:
        return image.copy()
    
    if target_h > 1:
        y_ratio = (src_h - 1) / (target_h - 1)
        y_coords = np.arange(target_h) * y_ratio
    else:
        y_coords = np.zeros(target_h)
    
    if target_w > 1:
        x_ratio = (src_w - 1) / (target_w - 1)
        x_coords = np.arange(target_w) * x_ratio
    else:
        x_coords = np.zeros(target_w)
    
    x_grid, y_grid = np.meshgrid(x_coords, y_coords)
    
    if mode == "linear":
        interpolation = cv2.INTER_LINEAR
    elif mode == "nearest":
        x_grid = np.round(x_grid)
        y_grid = np.round(y_grid)
        interpolation = cv2.INTER_NEAREST
    else:
        interpolation = cv2.INTER_LINEAR
    
    resized = cv2.remap(
        image,
        x_grid.astype(np.float32),
        y_grid.astype(np.float32),
        interpolation=interpolation,
        borderMode=cv2.BORDER_REPLICATE
    )
    
    return resized