"""Resolve dx_app postprocessor source paths for Model Zoo display.

Official Model Zoo HTML does not publish postprocessor metadata. The canonical
implementation lives under dx_app example trees. This module derives a stable
``dx_app/src/...`` path per model for the detail UI (replacing blank/pending).
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from dx_modelzoo.core.config import DATA_DIR, DX_APP_ROOT, PY_DIR

_MAP_FILE = DATA_DIR / "model_postprocessor_map.json"

_RE_FACTORY_IMPORT = re.compile(
    r"(?:from\s+\S*?([a-z_]+_postprocessor)\s+import|import\s+.*?([a-z_]+_postprocessor))",
    re.IGNORECASE,
)

# Longest-prefix-first heuristics when factory/registry/map are unavailable.
_PREFIX_STEMS: tuple[tuple[str, str], ...] = (
    ("damoyolo_tinynasl20_m", "damoyolo"),
    ("damoyolo_tinynasl20_t", "damoyolo"),
    ("damoyolo_tinynasl25_s", "damoyolo"),
    ("damoyolo", "damoyolo"),
    ("yolo26", "yolov26"),
    ("yolov26", "yolov26"),
    ("yolov12", "yolov12"),
    ("yolo11", "yolov11"),
    ("yolov11", "yolov11"),
    ("yolov10", "yolov10"),
    ("yolov9", "yolov9"),
    ("yolov8seg", "yolov8seg"),
    ("yolov8pose", "yolov8pose"),
    ("yolov8", "yolov8"),
    ("yolov7face", "yolov7face"),
    ("yolov7", "yolov7"),
    ("yolov6", "yolov5"),
    ("yolov5face", "yolov5face"),
    ("yolov5pose", "yolov5pose"),
    ("yolov5seg", "yolov5seg"),
    ("yolov5", "yolov5"),
    ("yolov4", "yolov4"),
    ("yolov3", "yolov3"),
    ("yolox", "yolox"),
    ("efficientdet", "efficientdet"),
    ("centernet", "centernet"),
    ("nanodet", "nanodet"),
    ("ssdmv", "ssd"),
    ("ssd", "ssd"),
    ("scrfd", "scrfd"),
    ("retinaface", "retinaface"),
    ("ulfg", "ulfg"),
    ("centerpose", "centerpose"),
    ("yolact", "yolact"),
    ("segformer", "segformer"),
    ("deeplab", "deeplabv3"),
    ("bisenetv2", "bisenetv2"),
    ("bisenetv1", "bisenetv1"),
    ("bisenet", "bisenetv1"),
    ("efficientnet", "efficientnet"),
    ("mobilenet", "mobilenet"),
    ("resnet", "resnet"),
    ("deit", "deit"),
    ("vit", "vit"),
    ("beit", "beit"),
    ("swin", "swin"),
    ("convnext", "convnext"),
    ("fastdepth", "fastdepth"),
    ("dncnn", "dncnn"),
    ("espcn", "espcn"),
    ("realesrgan", "realesrgan"),
    ("zero_dce", "zero_dce"),
    ("arcface", "arcface"),
    ("clip", "clip"),
    ("obb", "obb"),
)

_CATEGORY_DEFAULT_STEM = {
    "classification": "classification",
    "object_detection": "yolov8",
    "face_detection": "scrfd",
    "pose_estimation": "yolov8pose",
    "instance_segmentation": "yolov8seg",
    "semantic_segmentation": "deeplabv3",
    "depth_estimation": "fastdepth",
    "image_denoising": "dncnn",
    "super_resolution": "espcn",
    "image_enhancement": "zero_dce",
    "embedding": "arcface",
    "ppu": "yolov5_ppu",
    "obb_detection": "obb",
    "attribute_recognition": "classification",
    "reid": "classification",
    "hand_landmark": "classification",
    "face_alignment": "classification",
    "keypoint_detection": "centerpose",
    "object_pose_estimation": "centerpose",
    "panoptic_driving_perception": "semantic_segmentation",
    "3d_object_detection": "object_detection",
    "hand_detection": "classification",
}


def format_postprocessor_path(stem: str, *, lang: str = "python") -> str:
    """Return a suite-relative path string for UI (always prefixed with dx_app/)."""
    stem = stem.removesuffix("_postprocessor")
    if lang == "cpp":
        rel = f"src/cpp_example/common/processors/{stem}_postprocessor.hpp"
    else:
        rel = f"src/python_example/common/processors/{stem}_postprocessor.py"
    return f"dx_app/{rel}"


@lru_cache(maxsize=1)
def _load_postprocessor_map() -> dict[str, str]:
    if not _MAP_FILE.is_file():
        return {}
    try:
        raw = json.loads(_MAP_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    out: dict[str, str] = {}
    for model_id, value in raw.items():
        if not model_id or value in (None, ""):
            continue
        if isinstance(value, dict):
            stem = value.get("stem") or value.get("postprocessor") or value.get("path")
        else:
            stem = str(value)
        if not stem:
            continue
        if "/" in stem:
            out[str(model_id)] = stem if stem.startswith("dx_app/") else f"dx_app/{stem.lstrip('/')}"
        else:
            out[str(model_id)] = format_postprocessor_path(stem)
    return out


def _scan_factory_postprocessor(category: str, model_id: str) -> str | None:
    """Read the model factory import when dx_app sources are present locally."""
    if not PY_DIR.is_dir():
        return None
    factory_dir = PY_DIR / category / model_id / "factory"
    if not factory_dir.is_dir():
        return None
    for pyf in sorted(factory_dir.glob("*.py")):
        if pyf.name == "__init__.py":
            continue
        try:
            text = pyf.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = _RE_FACTORY_IMPORT.search(text)
        if not match:
            continue
        pp_name = match.group(1) or match.group(2)
        if not pp_name:
            continue
        stem = pp_name.removesuffix("_postprocessor")
        proc_py = PY_DIR / "common" / "processors" / f"{pp_name}.py"
        if proc_py.is_file():
            rel = proc_py.relative_to(DX_APP_ROOT).as_posix()
            return f"dx_app/{rel}"
        return format_postprocessor_path(stem)
    return None


def _infer_stem(model_id: str, category: str) -> str | None:
    mid = (model_id or "").lower()
    cat = (category or "").lower()
    if cat == "ppu":
        if "scrfd" in mid:
            return "scrfd_ppu"
        if "pose" in mid:
            return "yolov5pose_ppu"
        if "yolov7" in mid:
            return "yolov7_ppu"
        if "yolov5" in mid or "yolo" in mid:
            return "yolov5_ppu"
        return "yolov5_ppu"
    for prefix, stem in _PREFIX_STEMS:
        if mid.startswith(prefix) or prefix in mid:
            return stem
    return _CATEGORY_DEFAULT_STEM.get(cat)


def resolve_postprocessor_path(model: dict) -> str | None:
    """Best-effort postprocessor source path for a catalog model entry."""
    model_id = model.get("id") or ""
    category = model.get("category") or model.get("display", {}).get("task") or ""

    mapped = _load_postprocessor_map().get(model_id)
    if mapped:
        return mapped

    scanned = _scan_factory_postprocessor(category, model_id)
    if scanned:
        return scanned

    tech = model.get("technical") or {}
    registry_pp = tech.get("postprocessor")
    if registry_pp and not str(registry_pp).startswith("dx_app/"):
        return format_postprocessor_path(str(registry_pp))

    stem = _infer_stem(model_id, category)
    if stem:
        return format_postprocessor_path(stem)
    return None
