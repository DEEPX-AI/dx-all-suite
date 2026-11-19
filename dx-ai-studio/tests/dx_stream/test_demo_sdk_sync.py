"""DX Stream Demo Launcher follows the dx_stream SDK that is installed.

Two dead ends on a board set up entirely through Studio (dx_stream at v2.5.0):
- Secondary Inference looked for efficientnet-lite0_256x256.dxnn; the SDK's model_list.json and its own
  secondary_mode pipeline ship efficientnet-lite0_224x224.dxnn, so the card stayed "Needs setup".
- Face Detection PPU and Pose Estimation PPU point at run_SCRFD500M_PPU.sh / run_YOLOV5Pose_PPU.sh and models
  the SDK no longer ships; no Setup step can install them, so they stayed "Needs setup" forever.
"""
from __future__ import annotations

import pytest

from dx_stream.core import demos


@pytest.fixture
def sdk(tmp_path, monkeypatch):
    models, pipelines = tmp_path / "models", tmp_path / "pipelines"
    models.mkdir()
    pipelines.mkdir()
    monkeypatch.setattr(demos, "MODELS_DIR", models)
    monkeypatch.setattr(demos, "PIPELINES_DIR", pipelines)
    for d in demos.DEMOS:
        script = d.get("runtime_script")
        if script and "PPU.sh" not in script.replace("YoloV5S_PPU.sh", ""):
            (pipelines / script).parent.mkdir(parents=True, exist_ok=True)
            (pipelines / script).write_text("#!/bin/sh\n")
    return models, pipelines


def test_efficientnet_resolves_to_the_file_the_sdk_ships(sdk):
    models, _ = sdk
    (models / "efficientnet-lite0_224x224.dxnn").write_bytes(b"x")
    assert demos._model_file("EfficientNet_Lite0.dxnn") == "efficientnet-lite0_224x224.dxnn"


def test_efficientnet_still_finds_an_older_256_download(sdk):
    models, _ = sdk
    (models / "efficientnet-lite0_256x256.dxnn").write_bytes(b"x")
    assert demos._model_file("EfficientNet_Lite0.dxnn") == "efficientnet-lite0_256x256.dxnn"


def test_nothing_downloaded_yet_names_the_current_sdk_file(sdk):
    assert demos._model_file("EfficientNet_Lite0.dxnn") == "efficientnet-lite0_224x224.dxnn"


def test_secondary_inference_is_ready_with_the_sdk_models(sdk, monkeypatch):
    models, _ = sdk
    for f in ("yolov5-s_640x640_ppu.dxnn", "efficientnet-lite0_224x224.dxnn", "scrfd-500m_640x640.dxnn"):
        (models / f).write_bytes(b"x")
    monkeypatch.setattr(demos, "_npu_exists", lambda: True)
    monkeypatch.setattr(demos, "_plugin_exists", lambda: True)
    monkeypatch.setattr(demos, "_video_path", lambda name: "/v.mp4")
    sec = next(d for d in demos.DEMOS if d.get("runtime_script", "").startswith("secondary_mode/"))
    items = demos.check_demo_available(sec["id"])["reason_items"]
    assert not [i for i in items if i["code"] == "missing_model"], items


def test_demos_the_installed_sdk_no_longer_ships_are_not_listed(sdk):
    names = [e["runtime_script"] for e in demos.list_demo_entries(lambda d: {"available": True})]
    assert not any(s.endswith(("run_SCRFD500M_PPU.sh", "run_YOLOV5Pose_PPU.sh")) for s in names), names
    assert any(s.endswith("run_yolo26n.sh") for s in names)


def test_before_dx_stream_is_installed_every_demo_is_listed(tmp_path, monkeypatch):
    monkeypatch.setattr(demos, "PIPELINES_DIR", tmp_path / "not-installed")
    assert len(demos.list_demo_entries(lambda d: {"available": False})) == len(demos.DEMOS)
