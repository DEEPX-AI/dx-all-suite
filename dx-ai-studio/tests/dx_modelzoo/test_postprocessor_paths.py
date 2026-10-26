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
    # Models only on the publish page (anomaly · matting …) have no dx_app example here, so their
    # postprocessor is unknown; in the per-model layout their config.json names it.
    missing = [m["id"] for m in models if not (m.get("technical") or {}).get("postprocessor")
               and not m.get("publish_only")]
    assert not missing, f"missing postprocessor path: {missing[:5]}"


def test_a_per_model_example_names_its_postprocessor_in_config_json(tmp_path, monkeypatch):
    """In a per-model dx_app, one factory per family builds its processor from ``postprocessor.class`` in
    config.json, so importing the factory does not reveal it. The common/processors file that defines that class
    is shown instead (efficientad, patchcore and CLIP depend on this)."""
    import json
    from dx_modelzoo.core import postprocessor_paths as pp
    from shared import dx_app_layout as layout

    root = tmp_path / "dx_app"
    py = root / "src/python_example"
    ex = py / "anomaly_detection/patchcore/patchcore_224x224"
    ex.mkdir(parents=True)
    (ex / "patchcore_224x224_sync.py").write_text("")
    (ex / "config.json").write_text(json.dumps({"variant": "patchcore_224x224",
                                                "postprocessor": {"class": "AnomalyFeaturePostprocessor"}}))
    (py / "common/processors").mkdir(parents=True)
    (py / "common/runner").mkdir(parents=True)
    (py / "common/processors/anomaly_postprocessor.py").write_text("class AnomalyFeaturePostprocessor:\n    pass\n")
    monkeypatch.setattr(pp, "DX_APP_ROOT", root)
    monkeypatch.setattr(pp, "PY_DIR", py)
    layout.clear_cache()
    pp._processor_files.cache_clear()
    try:
        path = pp.resolve_postprocessor_path({"id": "patchcore_224x224", "category": "anomaly_detection",
                                              "model_file": "assets/models/patchcore_224x224.dxnn"})
    finally:
        layout.clear_cache()
        pp._processor_files.cache_clear()
    assert path == "dx_app/src/python_example/common/processors/anomaly_postprocessor.py"
