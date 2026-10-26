"""Model catalog — embedded metadata plus the runtime manifest.

When the runtime manifest exists its model list is the catalog;
otherwise the embedded fallback list is used.
"""
from __future__ import annotations

from dx_stream.core.config import DX_STREAM_ROOT, MODELS_DIR
from dx_stream.core.runtime import load_model_manifest

# Embedded model metadata (the files are downloaded by setup.sh)
_EMBEDDED_MODELS = [
    {"name": "YOLOv26n", "file": "yolo26n.dxnn", "category": "object_detection",
     "description_ko": "경량 객체 감지 모델", "description_en": "Lightweight object detection"},
    {"name": "YOLOv5S", "file": "YoloV5S.dxnn", "category": "object_detection",
     "description_ko": "YOLOv5 Small 객체 감지", "description_en": "YOLOv5 Small object detection"},
    {"name": "YOLOv7", "file": "YoloV7.dxnn", "category": "object_detection",
     "description_ko": "YOLOv7 객체 감지", "description_en": "YOLOv7 object detection"},
    {"name": "YOLOv8N", "file": "YoloV8N.dxnn", "category": "object_detection",
     "description_ko": "YOLOv8 Nano 객체 감지", "description_en": "YOLOv8 Nano object detection"},
    {"name": "YOLOv9S", "file": "YoloV9S.dxnn", "category": "object_detection",
     "description_ko": "YOLOv9 Small 객체 감지", "description_en": "YOLOv9 Small object detection"},
    {"name": "YOLOXs", "file": "YoloXS.dxnn", "category": "object_detection",
     "description_ko": "YOLOX Small 객체 감지", "description_en": "YOLOX Small object detection"},
    {"name": "YOLOv11N", "file": "YOLOV11N.dxnn", "category": "object_detection",
     "description_ko": "YOLOv11 Nano 객체 감지", "description_en": "YOLOv11 Nano object detection"},
    {"name": "YOLOv5S PPU", "file": "YoloV5S_PPU.dxnn", "category": "object_detection",
     "description_ko": "YOLOv5S 하드웨어 후처리", "description_en": "YOLOv5S with PPU"},
    {"name": "YOLOv5s Face", "file": "YOLOv5s_Face.dxnn", "category": "face_detection",
     "description_ko": "YOLOv5s 얼굴 감지", "description_en": "YOLOv5s face detection"},
    {"name": "SCRFD500M", "file": "SCRFD500M.dxnn", "category": "face_detection",
     "description_ko": "SCRFD 500M 얼굴 감지", "description_en": "SCRFD 500M face detection"},
    {"name": "SCRFD500M PPU", "file": "SCRFD500M_PPU.dxnn", "category": "face_detection",
     "description_ko": "SCRFD500M 하드웨어 후처리", "description_en": "SCRFD500M with PPU"},
    {"name": "YOLOv26n Pose", "file": "yolo26n-pose.dxnn", "category": "pose_estimation",
     "description_ko": "YOLOv26n 자세 추정", "description_en": "YOLOv26n pose estimation"},
    {"name": "YOLOv8m Pose", "file": "yolov8m_pose.dxnn", "category": "pose_estimation",
     "description_ko": "YOLOv8m 자세 추정", "description_en": "YOLOv8m pose estimation"},
    {"name": "YOLOV5Pose PPU", "file": "YOLOV5Pose_PPU.dxnn", "category": "pose_estimation",
     "description_ko": "YOLOV5Pose 하드웨어 후처리", "description_en": "YOLOV5Pose with PPU"},
    {"name": "YOLOv26n Seg", "file": "yolo26n-seg.dxnn", "category": "segmentation",
     "description_ko": "YOLOv26n 인스턴스 세그멘테이션", "description_en": "YOLOv26n instance segmentation"},
    {"name": "EfficientNet Lite0", "file": "EfficientNet_Lite0.dxnn", "category": "classification",
     "description_ko": "EfficientNet Lite0 분류", "description_en": "EfficientNet Lite0 classification"},
    {"name": "YOLO26n OBB", "file": "yolo26n-obb.dxnn", "category": "obb_detection",
     "description_ko": "YOLOv26n 회전 바운딩 박스 감지", "description_en": "YOLOv26n oriented bounding box detection"},
    # Keyed by its MANIFEST filename, not a legacy name: yolo26-depth shipped after the
    # v2_4_0 rename, so it never had an old-style name and needs no _MANIFEST_ALIAS entry
    # (_build_catalog tries the exact filename first). dx-runtime/dx_stream ships the full
    # pipeline for it — pipelines/single_network/depth_estimation/run_yolo26n-depth.sh,
    # libpostprocess_yolo26depth.so, and DxOsd::draw_depth's MAGMA colormap — so the studio
    # exposing it is catching up with the runtime, not adding an unusable card.
    {"name": "YOLO26n Depth", "file": "yolo26-depth-n_768x768.dxnn", "category": "depth_estimation",
     "description_ko": "YOLOv26n 깊이 추정", "description_en": "YOLOv26n depth estimation"},
]


# model_list.json v2_4_0 renamed most sample models to <slug>_<resolution>.dxnn
# (PPU models kept their legacy names). Map each new manifest filename back to the
# embedded metadata key so the catalog can categorize them instead of dropping every
# renamed model into 'uncategorized' in the DX Stream UI. Mirrors demos._MODEL_ALIAS
# (old -> new) but covers the full catalog, not just demo-backed models.
_MANIFEST_ALIAS = {
    "efficientnet-lite0_224x224.dxnn": "EfficientNet_Lite0.dxnn",
    "scrfd-500m_640x640.dxnn": "SCRFD500M.dxnn",
    "yolov5-s_640x640_ppu.dxnn": "YoloV5S_PPU.dxnn",
    "yolov5-s-face_640x640.dxnn": "YOLOv5s_Face.dxnn",
    "yolo26-n_640x640.dxnn": "yolo26n.dxnn",
    "yolo26-n-pose_640x640.dxnn": "yolo26n-pose.dxnn",
    "yolo26-n-seg_640x640.dxnn": "yolo26n-seg.dxnn",
    "yolov5-s_640x640.dxnn": "YoloV5S.dxnn",
    "yolov7_640x640.dxnn": "YoloV7.dxnn",
    "yolov8-n_640x640.dxnn": "YoloV8N.dxnn",
    "yolov9-s_640x640.dxnn": "YoloV9S.dxnn",
    "yolox-s_640x640.dxnn": "YoloXS.dxnn",
    "yolo11-n_640x640.dxnn": "YOLOV11N.dxnn",
    "yolov8-m-pose_640x640.dxnn": "yolov8m_pose.dxnn",
}


def _known_metadata_by_file() -> dict[str, dict]:
    return {m["file"]: dict(m) for m in _EMBEDDED_MODELS}


def _build_catalog() -> tuple[list[dict], str]:
    manifest = load_model_manifest(DX_STREAM_ROOT)
    if manifest.source == "manifest":
        known = _known_metadata_by_file()
        catalog = []
        for mf in manifest.models:
            # Exact match first (legacy-named manifests + PPU models), then the
            # v2_4_0 rename alias, then fall back to an uncategorized entry.
            meta = known.get(mf) or known.get(_MANIFEST_ALIAS.get(mf, ""))
            entry = dict(meta or {
                "name": mf.replace(".dxnn", ""),
                "category": "uncategorized",
                "description_ko": f"{mf} (자동 감지)",
                "description_en": f"{mf} (auto-detected)",
            })
            entry["file"] = mf
            catalog.append(entry)
        return catalog, "manifest"
    return [dict(m) for m in _EMBEDDED_MODELS], "fallback"


_MODELS, _CATALOG_SOURCE = _build_catalog()


def get_catalog_source() -> str:
    return _CATALOG_SOURCE


def get_models() -> list[dict]:
    """The whole model catalog (copies of the dicts)."""
    return [dict(m) for m in _MODELS]


def get_model_status() -> dict:
    """Install state per model — {file name: {installed, size}}."""
    result = {}
    for m in _MODELS:
        p = MODELS_DIR / m["file"]
        if p.exists():
            result[m["file"]] = {"installed": True, "size": p.stat().st_size}
        else:
            result[m["file"]] = {"installed": False, "size": 0}
    return result


def get_models_by_category() -> dict[str, list[dict]]:
    """Models grouped by category (copies of the dicts)."""
    cats: dict[str, list[dict]] = {}
    for m in _MODELS:
        cats.setdefault(m["category"], []).append(dict(m))
    return cats
