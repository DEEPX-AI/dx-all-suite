#!/usr/bin/env python3
"""
Serialize postprocess results to JSON for numerical verification.

Activated by DXAPP_VERIFY=1 environment variable.
Writes one JSON per inference to ``logs/verify/{model_name}.json``.

Supported result types:
  - DetectionResult, FaceResult  → detections[]
  - PoseResult                   → detections[] + keypoints[]
  - InstanceSegResult            → detections[] + has_mask
  - SegmentationResult           → mask_shape, unique_classes
  - ClassificationResult         → classifications[]
  - OBBResult                    → detections[] + angle
  - EmbeddingResult              → embedding{dim, l2_norm, has_nan}
  - HandLandmarkResult           → detections[] + landmarks[]
  - SuperResolutionResult        → output_shape, output_stats
  - EnhancedImageResult          → output_shape, output_stats
  - Other / raw numpy            → output_stats
"""

import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


def is_verify_enabled() -> bool:
    """Check if DXAPP_VERIFY=1 is set."""
    return os.environ.get("DXAPP_VERIFY", "0") == "1"


def _get_verify_dir() -> Path:
    """Return and create the verify output directory."""
    d = Path(os.environ.get("DXAPP_VERIFY_DIR", "logs/verify"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _np_stats(arr: np.ndarray) -> dict:
    """Safe statistics for a numpy array."""
    flat = arr.astype(np.float64).ravel()
    return {
        "shape": list(arr.shape),
        "dtype": str(arr.dtype),
        "min": float(np.min(flat)) if flat.size > 0 else 0.0,
        "max": float(np.max(flat)) if flat.size > 0 else 0.0,
        "mean": float(np.mean(flat)) if flat.size > 0 else 0.0,
        "std": float(np.std(flat)) if flat.size > 0 else 0.0,
        "has_nan": bool(np.isnan(flat).any()),
        "has_inf": bool(np.isinf(flat).any()),
    }


def _ser_detection(items, img_h, img_w):
    return {
        "image_height": img_h, "image_width": img_w,
        "detections": [
            {"bbox": list(map(float, d.box)), "conf": float(d.confidence),
             "class_id": int(d.class_id), "class_name": str(d.class_name)}
            for d in items
        ],
    }


def _ser_face(items, img_h, img_w):
    return {
        "image_height": img_h, "image_width": img_w,
        "detections": [
            {"bbox": list(map(float, d.box)), "conf": float(d.confidence),
             "class_id": int(d.class_id),
             "keypoints": [{"x": float(kp.x), "y": float(kp.y), "conf": float(kp.confidence)}
                           for kp in (d.keypoints or [])]}
            for d in items
        ],
    }


def _ser_pose(items, img_h, img_w):
    return {
        "image_height": img_h, "image_width": img_w,
        "detections": [
            {"bbox": list(map(float, d.box)), "conf": float(d.confidence),
             "class_id": int(d.class_id),
             "keypoints": [{"x": float(kp.x), "y": float(kp.y), "conf": float(kp.confidence)}
                           for kp in d.keypoints]}
            for d in items
        ],
    }


def _ser_instance_seg(items, img_h, img_w):
    return {
        "image_height": img_h, "image_width": img_w,
        "detections": [
            {"bbox": list(map(float, d.box)), "conf": float(d.confidence),
             "class_id": int(d.class_id), "class_name": str(d.class_name),
             "has_mask": d.mask is not None and d.mask.size > 0,
             "mask_shape": list(d.mask.shape) if d.mask is not None and d.mask.size > 0 else []}
            for d in items
        ],
    }


def _ser_depth(items, img_h, img_w):
    first = items[0]
    return {
        "image_height": img_h, "image_width": img_w,
        "output_stats": _np_stats(first.depth_map)
        if hasattr(first, "depth_map") and first.depth_map is not None else {},
    }


def _ser_segmentation(items, img_h, img_w):
    first = items[0]
    unique = int(len(np.unique(first.mask))) if first.mask.size > 0 else 0
    return {
        "image_height": img_h, "image_width": img_w,
        "mask_shape": [int(first.height), int(first.width)],
        "unique_classes": unique,
        "class_ids": [int(c) for c in first.class_ids],
    }


def _ser_classification(items, img_h, img_w):
    first = items[0]
    top_k_confs = [float(conf) for _, conf in first.top_k] if first.top_k else []
    return {
        "image_height": img_h, "image_width": img_w,
        "classifications": [
            {"class_id": int(first.class_id), "class_name": str(first.class_name),
             "conf": float(first.confidence)}
        ],
        "top_k_confs": top_k_confs,
    }


def _ser_obb(items, img_h, img_w):
    return {
        "image_height": img_h, "image_width": img_w,
        "detections": [
            {"cx": float(d.cx), "cy": float(d.cy),
             "width": float(d.width), "height": float(d.height),
             "angle": float(d.angle), "conf": float(d.confidence),
             "class_id": int(d.class_id), "class_name": str(d.class_name)}
            for d in items
        ],
    }


def _ser_embedding(items, img_h, img_w):
    first = items[0]
    vec = first.embedding
    return {
        "image_height": img_h, "image_width": img_w,
        "embedding": {
            "dim": int(vec.size) if vec is not None else 0,
            "l2_norm": float(np.linalg.norm(vec))
            if vec is not None and vec.size > 0 else 0.0,
            "has_nan": bool(np.isnan(vec).any())
            if vec is not None and vec.size > 0 else False,
            "model_type": str(first.model_type),
        },
    }


def _ser_hand_landmark(items, img_h, img_w):
    return {
        "image_height": img_h, "image_width": img_w,
        "detections": [
            {"confidence": float(d.confidence), "handedness": str(d.handedness),
             "landmarks": [{"x": float(d.landmarks[i, 0]),
                            "y": float(d.landmarks[i, 1]),
                            "z": float(d.landmarks[i, 2])}
                           for i in range(d.landmarks.shape[0])]
             if d.landmarks is not None and d.landmarks.size > 0 else []}
            for d in items
        ],
    }


def _ser_image_output(items, img_h, img_w):
    """SuperResolutionResult / EnhancedImageResult — identical schema."""
    first = items[0]
    return {
        "image_height": img_h, "image_width": img_w,
        "output_shape": list(first.output_image.shape)
        if first.output_image.size > 0 else [],
        "input_image_shape": [img_h, img_w],
        "output_stats": _np_stats(first.output_image)
        if first.output_image.size > 0 else {},
    }


_SERIALIZER_MAP = {
    "DetectionResult":        _ser_detection,
    "FaceResult":             _ser_face,
    "PoseResult":             _ser_pose,
    "InstanceSegResult":      _ser_instance_seg,
    "DepthResult":            _ser_depth,
    "SegmentationResult":     _ser_segmentation,
    "ClassificationResult":   _ser_classification,
    "OBBResult":              _ser_obb,
    "EmbeddingResult":        _ser_embedding,
    "HandLandmarkResult":     _ser_hand_landmark,
    "SuperResolutionResult":  _ser_image_output,
    "EnhancedImageResult":    _ser_image_output,
}


def _serialize_results(results: Any, image_hw: tuple) -> dict:
    """
    Convert postprocess results to a JSON-serializable dictionary.

    Parameters
    ----------
    results : list or single result
        Output from postprocessor.process()
    image_hw : tuple (height, width)
        Original image dimensions for metadata.

    Returns
    -------
    dict with standardized fields depending on result type.
    """
    img_h, img_w = image_hw

    # Handle empty results
    if isinstance(results, (list, tuple)) and len(results) == 0:
        return {"image_height": img_h, "image_width": img_w, "detections": []}

    items = results if isinstance(results, (list, tuple)) else [results]
    first = items[0]
    cls_name = type(first).__name__

    # Dispatch by result type name
    serializer = _SERIALIZER_MAP.get(cls_name)
    if serializer is not None:
        return serializer(items, img_h, img_w)

    # Fallback: numpy array
    if isinstance(first, np.ndarray):
        return {"image_height": img_h, "image_width": img_w,
                "output_stats": _np_stats(first)}

    # Truly unknown
    return {"image_height": img_h, "image_width": img_w,
            "result_type": cls_name, "repr": str(results)[:500]}


def dump_verify_json(
    results: Any,
    image_path: str,
    model_path: str,
    task: str,
    image_hw: tuple,
    verbose: bool = False,
) -> Optional[str]:
    """
    Serialize results and write to ``logs/verify/<model>.json``.

    Parameters
    ----------
    results : postprocess output
    image_path : path to input image
    model_path : path to .dxnn file
    task : task category string
    image_hw : (height, width)

    Returns
    -------
    Path to written JSON file, or None on error.
    """
    try:
        data = _serialize_results(results, image_hw)
        data["task"] = task
        data["model"] = os.path.basename(model_path)
        data["model_path"] = model_path
        data["input_image"] = image_path

        verify_dir = _get_verify_dir()
        model_stem = Path(model_path).stem
        json_path = verify_dir / f"{model_stem}.json"

        with open(json_path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        if verbose:
            print(f"[VERIFY] Dumped → {json_path}")
        return str(json_path)

    except Exception as e:
        print(f"[WARN] verify_serialize failed: {e}")
        return None
