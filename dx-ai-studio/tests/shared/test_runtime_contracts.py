"""Tests for Studio-owned App and Stream runtime contracts."""
from pathlib import Path
from types import SimpleNamespace


def _ready_profile(root):
    plugin_dir = root / "plugin"
    plugin_dir.mkdir()
    (plugin_dir / "libgstdxstream.so").touch()
    postprocess = root / "postprocess"
    postprocess.mkdir()
    return SimpleNamespace(
        python_executable=Path("/usr/bin/python3"),
        plugin_dir=plugin_dir,
        postprocess_lib_dir=postprocess,
    )


def test_stream_contract_blocks_missing_selected_asset_not_unrelated_demo_asset(tmp_path):
    from shared.runtime_contract import validate_stream_contract

    profile = _ready_profile(tmp_path)
    result = validate_stream_contract(
        profile,
        demo={"model": "selected.dxnn", "required_videos": ["selected.mp4"]},
        root=tmp_path / "assets",
    )

    assert result.first_failure.check_id == "asset.selected_model"
    assert "unrelated" not in result.first_failure.observed.lower()
    assert result.first_failure.remediation


def test_stream_contract_reports_missing_plugin_with_stable_check_id(tmp_path):
    from shared.runtime_contract import validate_stream_contract

    profile = SimpleNamespace(
        python_executable=Path("/usr/bin/python3"),
        plugin_dir=tmp_path / "missing-plugin",
        postprocess_lib_dir=tmp_path / "postprocess",
    )
    result = validate_stream_contract(profile, demo={}, root=tmp_path / "assets")

    assert result.first_failure.check_id == "gst.plugin"
    assert result.first_failure.remediation


def test_stream_contract_uses_declared_runtime_asset_directories(tmp_path):
    from shared.runtime_contract import validate_stream_contract

    profile = _ready_profile(tmp_path)
    models_dir = tmp_path / "samples" / "models"
    videos_dir = tmp_path / "samples" / "videos"
    configs_dir = tmp_path / "configs"
    models_dir.mkdir(parents=True)
    videos_dir.mkdir(parents=True)
    (configs_dir / "detector").mkdir(parents=True)
    (models_dir / "selected.dxnn").touch()
    (videos_dir / "selected.mp4").touch()
    for name in ("preprocess_config.json", "inference_config.json", "postprocess_config.json"):
        (configs_dir / "detector" / name).write_text("{}", encoding="utf-8")

    result = validate_stream_contract(
        profile,
        demo={
            "model": "selected.dxnn",
            "required_videos": ["selected.mp4"],
            "required_configs": ["detector"],
        },
        models_dir=models_dir,
        videos_dir=videos_dir,
        configs_dir=configs_dir,
    )

    assert result.passed