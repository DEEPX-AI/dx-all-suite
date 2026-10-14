"""Model list, run paths and config in the per-model layout.

The layout: ``src/<lang>_example/<task>/<family>/<stem>/``, config.json is a nested spec, binaries are
``bin/<stem>_<variant>``, models live in ``assets/models`` or the suite's ``workspace/res/models``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

STEM = "yolo26-n_640x640"


def _exe(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("#!/bin/sh\nexit 0\n")
    p.chmod(0o755)


@pytest.fixture
def per_model(tmp_path, monkeypatch):
    from dx_app.core import config, models, run_config
    from shared import dx_app_layout as layout

    suite = tmp_path / "suite"
    root = suite / "dx-runtime" / "dx_app"
    cfg = {"variant": STEM, "dxnn_file": f"{STEM}.dxnn", "task": "object_detection", "family": "yolo26",
           "image_only": False, "default_image": "sample/img/sample_street.jpg",
           "default_video": "assets/videos/snowboard.mp4",
           "config": {"score_threshold": 0.25, "nms_threshold": 0.45}, "cli": {}}
    for lang, suf in (("python", ".py"), ("cpp", ".cpp")):
        d = root / "src" / f"{lang}_example" / "object_detection" / "yolo26" / STEM
        d.mkdir(parents=True)
        (d / f"{STEM}_sync{suf}").write_text("")
        (d / "config.json").write_text(json.dumps(cfg))
    (root / "src/python_example/object_detection/yolo26" / STEM / f"{STEM}_async.py").write_text("")
    (root / "config").mkdir(parents=True)
    (root / "config/model_registry.json").write_text(json.dumps([
        {"model_name": "yolo26n", "variant": STEM, "family": "yolo26", "task": "object_detection",
         "task_legacy": "object_detection", "dxnn_file": f"{STEM}.dxnn", "image_only": False, "published": True}]))
    ws = suite / "workspace/res/models"
    ws.mkdir(parents=True)
    (ws / f"{STEM}.dxnn").write_bytes(b"DXNN\x08\x00\x00\x00")
    _exe(root / "bin" / f"{STEM}_sync")
    layout.clear_cache()
    # If another test reloads config, the resolve_model_path held by models belongs to the old module; patch the
    # globals that function actually reads.
    for fn in (config.resolve_model_path, models.resolve_model_path):
        monkeypatch.setitem(fn.__globals__, "_SUITE_ROOT", suite)
        monkeypatch.setitem(fn.__globals__, "_MODELS_DIR_ENV", "")
    for mod in (models,):
        monkeypatch.setattr(mod, "DX_APP_ROOT", root)
        monkeypatch.setattr(mod, "CPP_DIR", root / "src" / "cpp_example")
        monkeypatch.setattr(mod, "PY_DIR", root / "src" / "python_example")
        monkeypatch.setattr(mod, "BUILD_DIR", root / "bin", raising=False)
        monkeypatch.setattr(mod, "CONFIG_FILE", root / "config" / "test_models.conf")
    # A registry entry under an old name (bundled catalog) must not create the same model a second time
    monkeypatch.setattr(models, "_REG", {"yolo26n": {"category": "object_detection", "file": "assets/models/yolo26n.dxnn"}})
    monkeypatch.setattr(models, "_download_index", lambda: {})
    monkeypatch.setattr(models, "_python_runtime_ready", lambda: True, raising=False)
    monkeypatch.setattr(run_config, "DX_APP_ROOT", root, raising=False)
    yield root
    layout.clear_cache()


def test_models_are_listed_by_stem_with_their_own_config(per_model):
    from dx_app.core import models

    found = models.get_models()
    assert [m["name"] for m in found] == [STEM], found
    m = found[0]
    assert m["category"] == "object_detection" and m["family"] == "yolo26"
    assert m["model_file"] == f"assets/models/{STEM}.dxnn"
    assert m["model_exists"], "workspace/res/models 에 있는 model 도 설치된 것이다"
    assert m["config"] == {"score_threshold": 0.25, "nms_threshold": 0.45}
    assert m["image_only"] is False and m["default_image"] == "sample/img/sample_street.jpg"
    assert m["cpp_sync"] and m["py_sync"] and m["py_async"] and not m["cpp_async"]


def test_the_model_path_falls_back_to_the_workspace(per_model):
    from dx_app.core import config

    p = config.resolve_model_path(f"assets/models/{STEM}.dxnn", per_model)
    assert p == per_model.parents[1] / "workspace/res/models" / f"{STEM}.dxnn"


def test_a_zero_byte_model_is_not_installed(per_model):
    from dx_app.core import models

    ws = per_model.parents[1] / "workspace/res/models" / f"{STEM}.dxnn"
    ws.write_bytes(b"")
    assert models.get_models() == []


def test_the_python_script_is_found_in_the_stem_folder(per_model):
    from dx_app.core.inference_exec import _python_script_path

    p = _python_script_path("object_detection", STEM, "async", py_dir=per_model / "src" / "python_example")
    assert p == per_model / "src/python_example/object_detection/yolo26" / STEM / f"{STEM}_async.py"


def test_the_run_config_passed_to_the_runner_is_flat(per_model, monkeypatch):
    from dx_app.core import run_config

    monkeypatch.setattr(run_config, "CPP_DIR", per_model / "src" / "cpp_example")
    monkeypatch.setattr(run_config, "PY_DIR", per_model / "src" / "python_example")
    cfg = run_config.build_run_config("object_detection", STEM, {"score_threshold": 0.4})
    assert cfg == {"score_threshold": 0.4, "nms_threshold": 0.45}, cfg


def test_a_model_with_its_own_example_never_borrows_another_binary(per_model):
    """A per-model binary has its model's pre- and postprocessing built in; another model's gives wrong results."""
    from dx_app.core import models

    _exe(per_model / "bin" / "yolov5s_async")          # the binary a fallback lookup would pick up
    m = models.get_models()[0]
    assert m["cpp_sync"] and not m["cpp_async"], m


def test_an_old_name_of_an_example_is_not_listed_as_a_second_model(per_model, monkeypatch):
    """The bundled catalog still carries pre-layout ids (yolo26n, efficientnet_lite0 …) with an
    installed file. A run under that name is renamed to the example (server
    _validate_inference_payload → example_name), which has no borrowed binary — so the extra
    row offered C++ and every C++ run failed with "Binary not found … run build.sh"."""
    from dx_app.core import models

    other = per_model.parents[1] / "workspace/res/models/yolo26-n_640x640_old.dxnn"
    other.write_bytes(b"DXNN\x08\x00\x00\x00")
    monkeypatch.setattr(models, "_REG", {"yolo26n": {"category": "object_detection",
                                                     "file": "assets/models/yolo26-n_640x640_old.dxnn"}})
    _exe(per_model / "bin" / "yolov5s_sync")           # a binary the old row would have borrowed

    assert [m["name"] for m in models.get_models()] == [STEM]


def test_the_run_route_accepts_stem_names_but_not_paths():
    """Per-model model names are .dxnn stems and may use '-' and '.'; path-like names are still rejected."""
    import pytest as _pytest
    from dx_app import server

    for ok in ("yolo26-n_640x640", "3ddfa-v2_mobilenet-0.5_120x120", "yolov5s_ppu"):
        server._require_model_name(ok)
    for bad in ("../x", "a/b", ".hidden", "a..b", "", "a b"):
        with _pytest.raises(ValueError):
            server._require_model_name(bad)
