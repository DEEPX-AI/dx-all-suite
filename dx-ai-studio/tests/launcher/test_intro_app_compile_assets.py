"""Assets for the intro's App and Compiler scenes.

App is a clip baked by running the official segformer on a DX-M1 over every frame of the official sample drive
video (`scripts/intro/bake_app.py`); Compiler is the real ONNX graph of Ultralytics' official YOLO26n
(`scripts/intro/bake_compile.py`). This checks that the baked outputs keep the shape and weight the screen relies on.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INTRO = ROOT / "launcher" / "static" / "img" / "intro"
APP = INTRO / "app"
COMPILE = INTRO / "compile"


def test_the_app_scene_has_its_frames_and_a_light_clip():
    assert (APP / "first.webp").stat().st_size <= 250_000
    assert (APP / "seg-first.webp").stat().st_size <= 250_000
    clip = (APP / "seg.mp4").read_bytes()
    assert clip[4:8] == b"ftyp", "seg.mp4 는 MP4 여야 한다"
    assert clip.find(b"moov") < clip.find(b"mdat"), "faststart — moov 가 앞에 와야 받는 중에 재생된다"
    assert len(clip) <= 900_000
    assert not (APP / "seg.webm").exists()


def test_the_app_source_names_the_video_the_model_and_the_speed():
    src = (APP / "SOURCE.md").read_text(encoding="utf-8")
    for needle in ("blackbox-city-road.mp4", "segformer_mit-b0_512x1024.dxnn", "sample_videos.tar.gz", "FPS"):
        assert needle in src, needle


def test_the_compile_graph_is_the_real_yolo26n():
    g = json.loads((COMPILE / "graph.json").read_text(encoding="utf-8"))
    assert (COMPILE / "graph.json").stat().st_size <= 40_000
    nodes, edges = g["nodes"], g["edges"]
    assert len(nodes) == 384, "Ultralytics YOLO26n 의 ONNX node 수"
    assert sum(1 for n in nodes if n[2] == "conv") == 102
    w, h = g["stage"]
    for x, y, kind in nodes:
        assert 0 <= x <= w and 0 <= y <= h and kind in {"conv", "act", "other"}
    assert edges and all(0 <= a < len(nodes) and 0 <= b < len(nodes) and a != b for a, b in edges)


def test_the_compile_source_names_the_onnx_and_the_compiled_model():
    src = (COMPILE / "SOURCE.md").read_text(encoding="utf-8")
    for needle in ("yolo26n.onnx", "yolo26-n_640x640.dxnn", "384", "FPS"):
        assert needle in src, needle


def test_only_the_splash_timeline_owns_the_scene_flag():
    """`is-scene` (prompt moved down, logo out of the way) is switched on and off in one place in the splash per
    beat, by "is this beat's scene up". If each scene switched it off itself, a late-starting scene's timer could fire
    after the next scene switched it on, and the prompt would jump to the centre over the chip mid-Compiler."""
    static = ROOT / "launcher" / "static"
    for js in ("intro-stream.js", "intro-app.js", "intro-compile.js"):
        assert "is-scene" not in (static / js).read_text(encoding="utf-8"), js
    splash = (static / "launcher-splash.js").read_text(encoding="utf-8")
    assert "classList.toggle('is-scene'" in splash
