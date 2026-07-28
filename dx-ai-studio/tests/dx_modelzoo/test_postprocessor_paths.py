"""Tests for dx_app postprocessor path resolution."""

from dx_modelzoo.core.catalog import reload_catalog
from dx_modelzoo.core.postprocessor_paths import (
    format_postprocessor_path,
    resolve_postprocessor_path,
)


def test_format_postprocessor_path_uses_dx_app_prefix():
    assert format_postprocessor_path("yolov8") == (
        "dx_app/src/python_example/common/processors/yolov8_postprocessor.py"
    )


def test_resolve_postprocessor_path_for_yolo_model():
    path = resolve_postprocessor_path({"id": "yolov8n", "category": "object_detection"})
    assert path == "dx_app/src/python_example/common/processors/yolov8_postprocessor.py"


def test_resolve_postprocessor_path_for_ppu_model():
    path = resolve_postprocessor_path({"id": "scrfd500m_ppu", "category": "ppu"})
    assert path == "dx_app/src/python_example/common/processors/scrfd_ppu_postprocessor.py"


def test_resolve_postprocessor_path_for_classification_model():
    path = resolve_postprocessor_path({"id": "deit_base", "category": "classification"})
    assert path.endswith("/deit_postprocessor.py")


def test_reload_catalog_fills_postprocessor_for_all_models():
    reload_catalog()
    from dx_modelzoo.core.catalog import get_catalog

    models = get_catalog()["models"]
    assert models
    missing = [m["id"] for m in models if not (m.get("technical") or {}).get("postprocessor")]
    assert not missing, f"missing postprocessor path: {missing[:5]}"
