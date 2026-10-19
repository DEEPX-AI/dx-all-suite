"""One resolver for both dx_app example layouts.

- legacy: ``src/<lang>_example/<task>/<model>/<model>_<variant>.py``
- per_model: ``src/<lang>_example/<task>/<family>/<stem>/<stem>_<variant>.py``
  (stem = the ``.dxnn`` name, the registry's ``variant``)
"""
from __future__ import annotations

import json
import struct

import pytest

from shared import dx_app_layout as layout


def _touch(p, data=b"x"):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    return p


@pytest.fixture
def legacy(tmp_path):
    root = tmp_path / "legacy" / "dx_app"
    _touch(root / "src/python_example/object_detection/yolo26n/yolo26n_sync.py")
    _touch(root / "src/python_example/object_detection/yolo26n/config.json", b'{"score_threshold": 0.3}')
    _touch(root / "src/cpp_example/object_detection/yolo26n/yolo26n_sync.cpp")
    _touch(root / "src/python_example/ppu/yolov5s_ppu/yolov5s_ppu_async.py")
    _touch(root / "src/python_example/common/runner/entry.py")
    _touch(root / "config/model_registry.json", json.dumps([{"model_name": "yolo26n", "dxnn_file": "yolo26n.dxnn"}]).encode())
    layout.clear_cache()
    return root


@pytest.fixture
def per_model(tmp_path):
    root = tmp_path / "per_model" / "dx_app"
    ex = root / "src/python_example/object_detection/yolo26/yolo26-n_640x640"
    _touch(ex / "yolo26-n_640x640_sync.py")
    _touch(ex / "yolo26-n_640x640_sync_cpp_postprocess.py")
    _touch(ex / "config.json", json.dumps({"variant": "yolo26-n_640x640", "task": "object_detection",
                                            "config": {"score_threshold": 0.25, "nms_threshold": 0.45}}).encode())
    _touch(ex / "factory/yolo26-n_640x640_factory.py")
    _touch(root / "src/cpp_example/object_detection/yolo26/yolo26-n_640x640/yolo26-n_640x640_sync.cpp")
    _touch(root / "src/python_example/object_detection/yolo_ppu/yolov5-s_640x640_ppu/yolov5-s_640x640_ppu_sync.py")
    _touch(root / "src/python_example/object_detection/yolov5/yolov5n_sync_ort_off.py")   # leftover piece, not an example
    _touch(root / "src/python_example/object_detection/yolov5/__init__.py")
    _touch(root / "config/model_registry.json", json.dumps([
        {"model_name": "yolo26n", "variant": "yolo26-n_640x640", "family": "yolo26", "task": "object_detection",
         "task_legacy": "object_detection", "dxnn_file": "yolo26-n_640x640.dxnn", "published": True}]).encode())
    layout.clear_cache()
    return root


def test_the_layout_is_detected(legacy, per_model):
    assert layout.detect(legacy) == layout.LEGACY
    assert layout.detect(per_model) == layout.PER_MODEL


def test_legacy_examples_keep_their_paths(legacy):
    ex = layout.find(legacy, "object_detection", "yolo26n")
    assert ex.family is None
    assert layout.python_script(legacy, "object_detection", "yolo26n", "sync") == \
        legacy / "src/python_example/object_detection/yolo26n/yolo26n_sync.py"
    names = {(e.task, e.name) for e in layout.examples(legacy)}
    assert names == {("object_detection", "yolo26n"), ("ppu", "yolov5s_ppu")}


def test_per_model_examples_are_task_family_stem(per_model):
    names = {(e.task, e.family, e.name) for e in layout.examples(per_model)}
    assert names == {("object_detection", "yolo26", "yolo26-n_640x640"),
                     ("object_detection", "yolo_ppu", "yolov5-s_640x640_ppu")}
    ex = layout.find(per_model, "object_detection", "yolo26-n_640x640")
    assert ex.py_dir == per_model / "src/python_example/object_detection/yolo26/yolo26-n_640x640"
    assert ex.cpp_dir == per_model / "src/cpp_example/object_detection/yolo26/yolo26-n_640x640"
    assert layout.python_script(per_model, "object_detection", "yolo26-n_640x640", "sync_cpp_postprocess") == \
        ex.py_dir / "yolo26-n_640x640_sync_cpp_postprocess.py"
    assert layout.find(per_model, "object_detection", "nope") is None


def test_a_binary_is_named_after_the_model(tmp_path):
    assert layout.cpp_binary(tmp_path / "bin", "yolo26-n_640x640", "async") == tmp_path / "bin/yolo26-n_640x640_async"


def test_the_threshold_config_is_the_nested_block(per_model, legacy):
    assert layout.threshold_config(per_model, "object_detection", "yolo26-n_640x640") == \
        {"score_threshold": 0.25, "nms_threshold": 0.45}
    assert layout.threshold_config(legacy, "object_detection", "yolo26n") == {"score_threshold": 0.3}
    assert layout.threshold_config(legacy, "object_detection", "missing") == {}


def test_models_are_found_in_assets_then_the_workspace(tmp_path):
    root, suite = tmp_path / "suite/dx-runtime/dx_app", tmp_path / "suite"
    _touch(suite / "workspace/res/models/b.dxnn", b"DXNN" + struct.pack("<I", 8))
    _touch(suite / "workspace/res/models/empty.dxnn", b"")
    _touch(root / "assets/models/a.dxnn", b"DXNN" + struct.pack("<I", 8))
    _touch(suite / "workspace/res/models/a.dxnn", b"DXNN" + struct.pack("<I", 9))
    assert layout.find_model("assets/models/a.dxnn", root, suite) == root / "assets/models/a.dxnn"
    assert layout.find_model("b.dxnn", root, suite) == suite / "workspace/res/models/b.dxnn"
    assert layout.find_model("empty.dxnn", root, suite) is None, "0 byte 는 설치된 것이 아니다"


def test_the_container_version_is_read_from_the_header(tmp_path):
    assert layout.container_version(_touch(tmp_path / "v9.dxnn", b"DXNN" + struct.pack("<I", 9) + b"rest")) == 9
    assert layout.container_version(_touch(tmp_path / "v6.dxnn", b"DXNN" + struct.pack("<I", 6))) == 6
    assert layout.container_version(_touch(tmp_path / "junk.dxnn", b"PK\x03\x04....")) is None
    assert layout.container_version(tmp_path / "missing.dxnn") is None
    assert layout.container_version(_touch(tmp_path / "fixture.dxnn", b"DXNN\x00fixture-not-a-real-model\n")) is None


def test_a_model_added_by_add_model_sh_is_found_in_a_per_model_tree(per_model):
    """add_model.sh creates <task>/<model>/ on the per-model layout too."""
    _touch(per_model / "src/python_example/object_detection/my_custom/my_custom_sync.py")
    layout.clear_cache()
    ex = layout.find(per_model, "object_detection", "my_custom")
    assert ex is not None and ex.family is None
    assert layout.find(per_model, "object_detection", "yolo26-n_640x640").family == "yolo26"


def test_a_caller_naming_the_model_its_own_way_still_reaches_its_example(per_model):
    """Model Zoo calls a model by its catalog id (`rtdetr_r18vd_6x_640x640`); the dx_app example name is the .dxnn stem
    (`rtdetr-r18vd-6x_640x640`). If the lookup misses, dx_app borrows another binary of the same task (yolov7) and
    shows wrong boxes as if the run had succeeded."""
    task = "object_detection"
    assert layout.example_name(per_model, task, "yolo26-n_640x640", "") == "yolo26-n_640x640"
    assert layout.example_name(per_model, task, "yolo26_n_640x640",
                               "assets/models/yolo26-n_640x640.dxnn") == "yolo26-n_640x640"
    assert layout.example_name(per_model, task, "yolo26n", "") == "yolo26-n_640x640", "registry model_name → variant"
    assert layout.example_name(per_model, task, "something_else", "other.dxnn") == "something_else"


def test_the_inference_entry_runs_the_models_own_example(monkeypatch, per_model):
    import importlib
    srv = importlib.import_module("dx_app.server")
    monkeypatch.setattr(srv, "DX_APP_ROOT", per_model, raising=False)
    monkeypatch.setattr(srv, "_require_model_file", lambda f: None)   # this test looks at names only
    data = {"category": "object_detection", "model_name": "yolo26_n_640x640",
            "model_file": "assets/models/yolo26-n_640x640.dxnn", "lang": "cpp", "variant": "sync",
            "input_type": "image"}
    err, _ = srv._validate_inference_payload(data)
    assert err is None
    assert data["model_name"] == "yolo26-n_640x640"
