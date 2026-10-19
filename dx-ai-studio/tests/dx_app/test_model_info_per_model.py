"""Model detail on a per-model dx_app tree.

get_model_info must walk the per-model layout, not only the flat one (<lang>/<task>/<name>), and find the model
beyond DX_APP_ROOT/<file>; otherwise an installed model's Detail dialog shows no category, no files and
"Model File ✗ N/A".
"""
from __future__ import annotations

import importlib
import json


def _touch(p, data=b"x"):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return p


def test_the_detail_finds_the_example_files_and_the_installed_model(tmp_path, monkeypatch):
    from shared import dx_app_layout as layout
    models = importlib.import_module("dx_app.core.models")
    root = tmp_path / "dx_app"
    ex = root / "src/python_example/face_detection/scrfd/scrfd-500m_640x640"
    _touch(ex / "scrfd-500m_640x640_sync.py")
    _touch(ex / "config.json", json.dumps({"variant": "scrfd-500m_640x640", "config": {"score_threshold": 0.5}}).encode())
    _touch(root / "src/cpp_example/face_detection/scrfd/scrfd-500m_640x640/scrfd-500m_640x640_sync.cpp")
    _touch(root / "config/model_registry.json", json.dumps([
        {"model_name": "SCRFD500M", "variant": "scrfd-500m_640x640", "family": "scrfd", "task": "face_detection",
         "dxnn_file": "scrfd-500m_640x640.dxnn"}]).encode())
    _touch(root / "assets/models/scrfd-500m_640x640.dxnn", b"DXNN")
    layout.clear_cache()
    monkeypatch.setattr(models, "DX_APP_ROOT", root)
    monkeypatch.setattr(models, "CPP_DIR", root / "src/cpp_example")
    monkeypatch.setattr(models, "PY_DIR", root / "src/python_example")
    monkeypatch.setattr(models, "_REG", {"SCRFD500M": {"file": "assets/models/scrfd-500m_640x640.dxnn"},
                                         "scrfd-500m_640x640": {"file": "assets/models/scrfd-500m_640x640.dxnn"}})
    for name in ("scrfd-500m_640x640", "SCRFD500M"):
        info = models.get_model_info(name)
        assert info["model_exists"] is True, name
        assert info["category"] == "face_detection", name
        assert any(f.endswith("scrfd-500m_640x640_sync.py") for f in info["files"]["python"]), name
        assert any(f.endswith("_sync.cpp") for f in info["files"]["cpp"]), name
        assert info["config"]["config"]["score_threshold"] == 0.5
    layout.clear_cache()
