"""runtime.py tests — dx-runtime/dx_stream contract adapter."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))


DEV_MODELS = [
    "EfficientNet_Lite0.dxnn",
    "SCRFD500M.dxnn",
    "YoloV5S_PPU.dxnn",
    "YOLOv5s_Face.dxnn",
    "yolo26n.dxnn",
    "yolo26n-pose.dxnn",
    "yolo26n-seg.dxnn",
    "YoloV5S.dxnn",
    "YoloV7.dxnn",
    "YoloV8N.dxnn",
    "YoloV9S.dxnn",
    "YoloXS.dxnn",
    "YOLOV11N.dxnn",
    "yolov8m_pose.dxnn",
    "SCRFD500M_PPU.dxnn",
    "YOLOV5Pose_PPU.dxnn",
]


def _write_dev_runtime(root: Path) -> Path:
    (root / "dx_stream" / "configs" / "YoloV5S_PPU").mkdir(parents=True)
    for name in ["preprocess_config.json", "inference_config.json", "postprocess_config.json"]:
        (root / "dx_stream" / "configs" / "YoloV5S_PPU" / name).write_text("{}", encoding="utf-8")
    (root / "dx_stream" / "configs" / "tracker_config.json").write_text("{}", encoding="utf-8")
    (root / "dx_stream" / "pipelines" / "single_network" / "object_detection").mkdir(parents=True)
    (root / "dx_stream" / "pipelines" / "single_network" / "object_detection" / "run_yolo26n.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    (root / "model_list.json").write_text(json.dumps({"version": "2_3_0", "models": DEV_MODELS}), encoding="utf-8")
    (root / "setup.sh").write_text("Usage\n  [--model=<modelname>]\n", encoding="utf-8")
    (root / "build.sh").write_text("Usage\n  [--type=TYPE]\n", encoding="utf-8")
    return root


def test_load_model_manifest_manifest_mode(tmp_path):
    from core.runtime import load_model_manifest

    root = _write_dev_runtime(tmp_path)

    manifest = load_model_manifest(root)

    assert manifest.source == "manifest"
    assert manifest.version == "2_3_0"
    assert len(manifest.models) == len(DEV_MODELS)
    assert "EfficientNet_Lite0.dxnn" in manifest.models
    assert "yolo26n-obb.dxnn" not in manifest.models


def test_load_model_manifest_fallback_mode(tmp_path):
    from core.runtime import load_model_manifest

    manifest = load_model_manifest(tmp_path)

    assert manifest.source == "fallback"
    assert manifest.models == []


def test_required_config_files_reports_missing(tmp_path):
    from core.runtime import required_config_files, missing_paths

    root = _write_dev_runtime(tmp_path)

    missing_required = required_config_files(root, "EfficientNet_Lite0")
    assert missing_required
    assert missing_paths(missing_required) == missing_required

    present_required = required_config_files(root, "YoloV5S_PPU")
    assert present_required
    assert missing_paths(present_required) == []


def test_setup_build_command_uses_equals_type(tmp_path):
    from core.runtime import build_step_command

    root = _write_dev_runtime(tmp_path)

    assert build_step_command(root, clean=True, debug=False) == [
        "bash", str(root / "build.sh"), "--clean", "--type=Release"
    ]
    assert build_step_command(root, clean=False, debug=True) == [
        "bash", str(root / "build.sh"), "--type=Debug"
    ]


def test_load_model_manifest_invalid_json(tmp_path):
    from core.runtime import load_model_manifest

    (tmp_path / "model_list.json").write_text("{bad json", encoding="utf-8")

    manifest = load_model_manifest(tmp_path)

    assert manifest.source == "manifest"
    assert manifest.models == []
    assert manifest.error is not None


def test_load_model_manifest_invalid_models_payload(tmp_path):
    from core.runtime import load_model_manifest

    # models is not a list
    (tmp_path / "model_list.json").write_text(
        json.dumps({"version": "1_0_0", "models": "not-a-list"}), encoding="utf-8"
    )
    manifest = load_model_manifest(tmp_path)
    assert manifest.source == "manifest"
    assert manifest.models == []
    assert manifest.version == "1_0_0"
    assert manifest.error == "Invalid model_list.json models"

    # models list contains a non-string element
    (tmp_path / "model_list.json").write_text(
        json.dumps({"version": "2_0_0", "models": ["valid.dxnn", 42]}), encoding="utf-8"
    )
    manifest = load_model_manifest(tmp_path)
    assert manifest.source == "manifest"
    assert manifest.models == []
    assert manifest.version == "2_0_0"
    assert manifest.error == "Invalid model_list.json models"


def test_path_helpers(tmp_path):
    from core.runtime import (
        runtime_src, configs_dir, pipelines_dir, samples_dir,
        models_dir, videos_dir, tracker_config_file, pipeline_script,
    )

    root = tmp_path
    assert runtime_src(root) == root / "dx_stream"
    assert configs_dir(root) == root / "dx_stream" / "configs"
    assert pipelines_dir(root) == root / "dx_stream" / "pipelines"
    assert samples_dir(root) == root / "dx_stream" / "samples"
    assert models_dir(root) == root / "dx_stream" / "samples" / "models"
    assert videos_dir(root) == root / "dx_stream" / "samples" / "videos"
    assert tracker_config_file(root) == root / "dx_stream" / "configs" / "tracker_config.json"
    assert pipeline_script(root, "single_network/object_detection/run_yolo26n.sh") == (
        root / "dx_stream" / "pipelines" / "single_network" / "object_detection" / "run_yolo26n.sh"
    )


def test_download_command_dev_full_setup_only(tmp_path):
    from core.runtime import setup_assets_command, setup_single_model_command

    root = _write_dev_runtime(tmp_path)

    assert setup_assets_command(root) == ["bash", str(root / "setup.sh")]
    assert "--models-only" not in setup_assets_command(root)
    assert "--videos-only" not in setup_assets_command(root)
    assert setup_single_model_command(root, "yolo26n.dxnn") == [
        "bash", str(root / "setup.sh"), "--model=yolo26n.dxnn"
    ]
