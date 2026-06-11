#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
End-to-end verification for the yolo26n-pose squat mini-game.

Drives the REAL game path on the NPU: for each frame of the sample squat video
it runs preprocess -> NPU inference -> postprocess -> SquatGameVisualizer.visualize
(the exact stateful game hook SyncRunner uses) and checks:

  1. the DXNN model loads and runs on the NPU,
  2. at least one frame yields a PoseResult with 17 COCO keypoints,
  3. the game visualize() path runs without error on every frame, and
  4. at least one squat repetition is counted on sample/squat_demo.mp4.

Exit code 0 + "RESULT: PASS" on success; exit code 1 + "RESULT: FAIL" otherwise.

Usage:
    python verify.py [--model <dxnn>] [--video <mp4>]
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import cv2

_HERE = Path(__file__).resolve().parent


def _find_dev_common_root(start: Path):
    d = start
    for _ in range(8):
        cand = d / "src" / "python_example"
        if (cand / "common" / "__init__.py").is_file():
            return cand
        d = d.parent
    return None


_dev_root = _find_dev_common_root(_HERE)
if _dev_root is not None and str(_dev_root) not in sys.path:
    sys.path.insert(0, str(_dev_root))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


def _fail(msg: str):
    print(f"[verify] {msg}")
    print("RESULT: FAIL")
    sys.exit(1)


def _suite_root(start: Path):
    d = start
    for _ in range(8):
        if (d / "dx-runtime").is_dir() and (d / "dx-compiler").is_dir():
            return d
        d = d.parent
    return None


def _model_filename():
    """Model filename, sourced from app.yaml (config — not hardcoded in code)."""
    import glob  # noqa: F401  (kept local to discovery)
    y = _HERE / "app.yaml"
    if y.is_file():
        for line in y.read_text().splitlines():
            s = line.strip()
            if s.startswith("dxnn_file:"):
                return s.split(":", 1)[1].strip()
    return None


def _default_model():
    import glob
    name = _model_filename()
    search = [_HERE, _HERE.parent.parent / "assets" / "models"]
    sr = _suite_root(_HERE)
    if sr:
        search.append(sr / "dx-runtime" / "dx_app" / "assets" / "models")
    for d in search:
        if name and (Path(d) / name).is_file():
            return str(Path(d) / name)
        hits = sorted(glob.glob(str(Path(d) / ("*pose*" + os.extsep + "dxnn"))))
        if hits:
            return hits[0]
    return str(_HERE.parent.parent / "assets" / "models" / (name or "model"))


def _default_video():
    for cand in [_HERE / "sample" / "squat_demo.mp4",
                 _HERE.parent.parent / "sample" / "squat_demo.mp4"]:
        if cand.is_file():
            return str(cand)
    return str(_HERE.parent.parent / "sample" / "squat_demo.mp4")


def main():
    ap = argparse.ArgumentParser(description="Verify squat game E2E")
    ap.add_argument("--model", "-m", default=_default_model())
    ap.add_argument("--video", "-v", default=_default_video())
    args = ap.parse_args()

    try:
        import json
        from dx_engine import InferenceEngine
        from factory import SquatGameFactory
        from factory.squat_game_visualizer import SquatGameVisualizer
    except Exception as e:  # noqa: BLE001
        _fail(f"import failed: {e}")

    if not os.path.isfile(args.model):
        _fail(f"model not found: {args.model}")
    if not os.path.isfile(args.video):
        _fail(f"video not found: {args.video}")

    cfg_path = _HERE / "config.json"
    config = json.load(open(cfg_path)) if cfg_path.is_file() else {}

    try:
        ie = InferenceEngine(args.model)
    except Exception as e:  # noqa: BLE001
        _fail(f"NPU inference engine init failed: {e}")

    info = ie.get_input_tensors_info()[0]
    shape = info["shape"]
    if len(shape) >= 4 and shape[-1] in (1, 3, 4):
        ih, iw = shape[1], shape[2]
    elif len(shape) >= 4:
        ih, iw = shape[2], shape[3]
    else:
        ih, iw = shape[1], shape[2]

    factory = SquatGameFactory(config)
    pre = factory.create_preprocessor(iw, ih)
    post = factory.create_postprocessor(iw, ih)
    viz = factory.create_visualizer()
    if not isinstance(viz, SquatGameVisualizer):
        _fail("factory did not produce a SquatGameVisualizer")

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        _fail(f"cannot open video: {args.video}")

    frames = 0
    frames_with_pose = 0
    saw_17_kpts = False
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames += 1
            tensor, ctx = pre.process(frame)
            outputs = ie.run([tensor])
            results = post.process(outputs, ctx)
            if results:
                frames_with_pose += 1
                for r in results:
                    if getattr(r, "keypoints", None) and len(r.keypoints) == 17:
                        saw_17_kpts = True
                        break
            # Exercise the REAL game hook (rep FSM + HUD draw) on every frame.
            out = viz.visualize(frame, results)
            if out is None or out.shape != frame.shape:
                _fail(f"visualize() returned bad frame at #{frames}")
    except Exception as e:  # noqa: BLE001
        _fail(f"pipeline raised at frame {frames}: {e}")
    finally:
        cap.release()

    reps = viz.counter.reps
    print(f"[verify] frames={frames}  frames_with_pose={frames_with_pose}  "
          f"saw_17_keypoints={saw_17_kpts}  reps_counted={reps}  "
          f"score={viz.score}")
    print(f"[verify] thresholds: knee_down={viz.knee_down} "
          f"knee_up={viz.knee_up} hip_down={viz.hip_down} "
          f"target_reps={viz.target_reps}")

    if frames == 0:
        _fail("no frames read from video")
    if not saw_17_kpts:
        _fail("no PoseResult with 17 COCO keypoints produced")
    if reps < 1:
        _fail("no squat repetitions counted on the sample squat video")

    print("RESULT: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
