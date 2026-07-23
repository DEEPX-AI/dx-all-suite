"""Run-page config merge contracts."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "dx_app" / "core"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))


def test_sanitize_ignores_unknown_keys():
    from run_config import sanitize_config_overrides

    assert sanitize_config_overrides({"score_threshold": 0.4, "num_classes": 80, "future_x": 1}) == {
        "score_threshold": 0.4,
    }


def test_merge_legacy_maps_conf_without_touching_obj(tmp_path, monkeypatch):
    import run_config as rc
    from run_config import build_run_config

    app_root = tmp_path / "dx_app"
    py_dir = app_root / "python_example" / "instance_segmentation" / "yolov5l_seg"
    py_dir.mkdir(parents=True)
    (py_dir / "config.json").write_text(
        json.dumps({"score_threshold": 0.5, "nms_threshold": 0.45, "obj_threshold": 0.25}),
        encoding="utf-8",
    )
    monkeypatch.setattr(rc, "PY_DIR", app_root / "python_example")
    monkeypatch.setattr(rc, "CPP_DIR", app_root / "cpp_example")

    merged = build_run_config(
        "instance_segmentation",
        "yolov5l_seg",
        config_overrides={"score_threshold": 0.35, "nms_threshold": 0.4},
    )

    assert merged["score_threshold"] == 0.35
    assert merged["nms_threshold"] == 0.4
    assert merged["obj_threshold"] == 0.25


def test_merge_legacy_conf_threshold_alias(tmp_path, monkeypatch):
    import run_config as rc
    from run_config import build_run_config

    app_root = tmp_path / "dx_app"
    py_dir = app_root / "python_example" / "object_detection" / "yolov8n"
    py_dir.mkdir(parents=True)
    (py_dir / "config.json").write_text(
        json.dumps({"score_threshold": 0.4, "nms_threshold": 0.45}),
        encoding="utf-8",
    )
    monkeypatch.setattr(rc, "PY_DIR", app_root / "python_example")
    monkeypatch.setattr(rc, "CPP_DIR", app_root / "cpp_example")

    merged = build_run_config(
        "object_detection",
        "yolov8n",
        config_overrides=None,
        conf_threshold=0.3,
        nms_threshold=0.5,
    )

    assert merged == {"score_threshold": 0.3, "nms_threshold": 0.5}


def test_load_model_config_reads_python_example(tmp_path, monkeypatch):
    import run_config as rc
    from run_config import load_model_config

    app_root = tmp_path / "dx_app"
    py_dir = app_root / "python_example" / "classification" / "efficientnet"
    py_dir.mkdir(parents=True)
    (py_dir / "config.json").write_text(json.dumps({"top_k": 7}), encoding="utf-8")
    monkeypatch.setattr(rc, "PY_DIR", app_root / "python_example")
    monkeypatch.setattr(rc, "CPP_DIR", app_root / "cpp_example")

    assert load_model_config("classification", "efficientnet") == {"top_k": 7}


def test_run_tunable_keys_cover_schema_thresholds():
    from run_config import RUN_TUNABLE_KEYS

    for key in ("score_threshold", "nms_threshold", "obj_threshold", "top_k"):
        assert key in RUN_TUNABLE_KEYS


def test_inference_run_writes_merged_config_for_python(tmp_path, monkeypatch):
    inference, app_root = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    model_dir = app_root / "python_example" / "classification" / "demo"
    model_dir.mkdir(parents=True)
    (model_dir / "config.json").write_text(json.dumps({"top_k": 3}), encoding="utf-8")
    (model_dir / "demo_sync.py").write_text("print('ok')\n", encoding="utf-8")
    (app_root / "input.jpg").write_bytes(b"input")

    captured = {}

    class FakeProc:
        returncode = 0

        def __init__(self, cmd, stdout=None, **_kwargs):
            captured["cmd"] = cmd
            if "--config" in cmd:
                cfg_path = cmd[cmd.index("--config") + 1]
                captured["config"] = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
            Path(_kwargs["env"]["DXAPP_SAVE_IMAGE"]).write_bytes(b"result")
            if stdout:
                stdout.write("[INFO] done\n")
                stdout.flush()

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(inference.subprocess, "Popen", FakeProc)

    inference.run_inference(
        "demo",
        "classification",
        "model.dxnn",
        lang="python",
        variant="sync",
        input_type="image",
        image_path="input.jpg",
        timeout=1,
        config_overrides={"top_k": 9},
        save_output=False,
    )

    assert "--config" in captured["cmd"]
    assert captured["config"]["top_k"] == 9


def _prepare_dx_app_runtime(tmp_path, monkeypatch):
    import inference

    app_root = tmp_path / "dx_app_root"
    build_dir = app_root / "build"
    outputs_dir = app_root / "outputs"
    cpp_dir = app_root / "cpp_example"
    py_dir = app_root / "python_example"
    for path in (build_dir, outputs_dir, cpp_dir, py_dir):
        path.mkdir(parents=True, exist_ok=True)

    (app_root / "model.dxnn").write_bytes(b"model")

    monkeypatch.setattr(inference, "DX_APP_ROOT", app_root)
    monkeypatch.setattr(inference, "BUILD_DIR", build_dir)
    monkeypatch.setattr(inference, "OUTPUTS_DIR", outputs_dir)
    monkeypatch.setattr(inference, "CPP_DIR", cpp_dir)
    monkeypatch.setattr(inference, "PY_DIR", py_dir)
    monkeypatch.setattr(inference, "get_hw", lambda: {})
    monkeypatch.setattr(inference, "_parse_perf", lambda stdout: {"overall_fps": "30"})

    return inference, app_root
