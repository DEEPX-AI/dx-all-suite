"""The detail page's CLI command is one that runs.

Building it from the catalog id gives './yolo26n_sync -m {}/assets/models/yolo26n.dxnn -i
sample/img/sample_street.jpg': a literal '{}', a binary and a model file that do not exist (the real ones are
yolo26-n_640x640), and the street image even for point-cloud, denoising and ReID models.
"""
from __future__ import annotations

import importlib
import json


def _touch(p, data=b"x"):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def test_the_command_uses_the_example_binary_the_model_file_and_its_own_input(tmp_path, monkeypatch):
    from shared import dx_app_layout as layout
    cat = importlib.import_module("dx_modelzoo.core.catalog")
    root = tmp_path / "dx_app"
    _touch(root / "src/cpp_example/object_detection/yolo26/yolo26-n_640x640/yolo26-n_640x640_sync.cpp")
    _touch(root / "src/python_example/object_detection/yolo26/yolo26-n_640x640/yolo26-n_640x640_sync.py")
    _touch(root / "config/model_registry.json", json.dumps([{"model_name": "yolo26n", "variant": "yolo26-n_640x640",
           "family": "yolo26", "task": "object_detection"}]).encode())
    layout.clear_cache()
    monkeypatch.setattr(cat, "DX_APP_ROOT", root)
    demo = cat._build_demo_info("yolo26n", "object_detection", "assets/models/yolo26-n_640x640.dxnn",
                                "sample/img/sample_dog.jpg")
    lines = demo["cli_command"].splitlines()
    assert lines[0] == "cd dx-runtime/dx_app"
    assert lines[1].startswith("./build.sh --target yolo26-n_640x640_sync")
    assert lines[2] == "./bin/yolo26-n_640x640_sync -m assets/models/yolo26-n_640x640.dxnn -i sample/img/sample_dog.jpg"
    assert "{}" not in demo["cli_command"]
    assert demo["cpp_example"].endswith("yolo26/yolo26-n_640x640/")
    assert demo["python_example"].endswith("yolo26/yolo26-n_640x640/")
    layout.clear_cache()


def test_a_model_without_an_example_has_no_command(tmp_path, monkeypatch):
    from shared import dx_app_layout as layout
    cat = importlib.import_module("dx_modelzoo.core.catalog")
    root = tmp_path / "dx_app"
    root.mkdir()
    layout.clear_cache()
    monkeypatch.setattr(cat, "DX_APP_ROOT", root)
    demo = cat._build_demo_info("nothing", "object_detection", "assets/models/nothing.dxnn", None)
    assert demo == {"cpp_example": "", "python_example": "", "cli_command": ""}
    layout.clear_cache()
