#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Headless validation for the stretch mini-game.

Drives the actual game engine (StretchGameVisualizer) over the three sample
clips on the NPU and asserts:
  1. Per clip: starting at that clip's stage, the stage is cleared.
  2. End-to-end: one game instance fed [overhead, fold, neck] clips in order
     reaches GAME_CLEAR.

Exit 0 + "RESULT: PASS" only if every assertion holds; else exit 1 + FAIL.

Usage:
    python verify.py [-m <model.dxnn>]
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Stay headless even if a display is exported (avoids GUI calls in cv2).
os.environ.pop("DISPLAY", None)
os.environ.pop("WAYLAND_DISPLAY", None)

import numpy as np   # noqa: E402
import cv2           # noqa: E402


def _setup_paths():
    here = Path(__file__).resolve().parent
    pe_root = None
    for parent in [here, *here.parents]:
        if (parent / "src" / "python_example" / "common").is_dir():
            pe_root = parent / "src" / "python_example"
            break
    if pe_root is None:
        raise RuntimeError("Could not locate src/python_example/common")
    for p in (str(here), str(pe_root)):
        if p not in sys.path:
            sys.path.insert(0, p)
    return pe_root


HERE = Path(__file__).resolve().parent
PE_ROOT = _setup_paths()
SAMPLE_DIR = PE_ROOT.parent.parent / "sample"

from dx_engine import InferenceEngine                       # noqa: E402
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor  # noqa: E402
from stretch_game_engine import StretchGameVisualizer, STAGES  # noqa: E402

STAGE_CLIP = {
    "overhead": "stretching_extending_both_arms.mp4",
    "fold": "stretching_bending_at_the_waist.mp4",
    "neck": "stretching_pulling_the_head.mp4",
}
STAGE_IDX = {key: i for i, (key, _, _) in enumerate(STAGES)}


def _make_io(model):
    ie = InferenceEngine(model)
    ti = ie.get_input_tensors_info()[0]["shape"]
    if ti[-1] in (1, 3, 4):
        ih, iw = ti[1], ti[2]
    else:
        ih, iw = ti[2], ti[3]
    return ie, iw, ih


def _drive_clip(ie, pre, post, vis, clip_path, save_writer=None):
    """Feed every frame of a clip through the game engine. Returns frame count."""
    cap = cv2.VideoCapture(clip_path)
    if not cap.isOpened():
        raise RuntimeError(f"cannot open {clip_path}")
    n = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        n += 1
        tensor, ctx = pre.process(frame)
        outputs = ie.run([tensor])
        results = post.process(outputs, ctx)
        out = vis.visualize(frame, results)
        if save_writer is not None:
            save_writer.write(out)
    cap.release()
    return n


def main():
    ap = argparse.ArgumentParser(description="Verify the stretch game")
    ap.add_argument("--model", "-m",
                    default=str(PE_ROOT.parent.parent / "assets" / "models" / "yolo26n-pose.dxnn"))
    ap.add_argument("--config", default=str(HERE / "config.json"))
    args = ap.parse_args()

    config = json.load(open(args.config)) if os.path.isfile(args.config) else {}
    templates = str(HERE / "pose_templates.json")

    if not os.path.isfile(args.model):
        print(f"DXNN model not found: {args.model}")
        print("RESULT: FAIL")
        sys.exit(1)

    ie, iw, ih = _make_io(args.model)
    pre = LetterboxPreprocessor(iw, ih)
    post = YOLOv8PosePostprocessor(iw, ih, config)

    ok = True

    # --- Test 1: per-clip stage clear ---
    print("== Test 1: per-clip stage clear ==")
    for key, clip in STAGE_CLIP.items():
        path = str(SAMPLE_DIR / clip)
        if not os.path.isfile(path):
            print(f"  [{key}] MISSING clip {path}")
            ok = False
            continue
        vis = StretchGameVisualizer(config, start_stage=STAGE_IDX[key],
                                    templates_path=templates)
        frames = _drive_clip(ie, pre, post, vis, path)
        cleared = vis.completed >= 1
        print(f"  [{key}] frames={frames} cleared={cleared} "
              f"(completed={vis.completed})")
        ok = ok and cleared

    # --- Test 2: end-to-end full sequence -> GAME_CLEAR ---
    print("== Test 2: end-to-end sequence -> CLEAR ==")
    vis = StretchGameVisualizer(config, start_stage=0, templates_path=templates)
    seq = ["overhead", "fold", "neck"]
    for key in seq:
        path = str(SAMPLE_DIR / STAGE_CLIP[key])
        if not os.path.isfile(path):
            print(f"  MISSING clip {path}")
            ok = False
            break
        _drive_clip(ie, pre, post, vis, path)
        print(f"  after {key}: stage={vis.stage} completed={vis.completed} "
              f"mode={vis.mode}")
    game_clear = vis.is_game_clear()
    print(f"  GAME_CLEAR reached: {game_clear}")
    ok = ok and game_clear

    if ok:
        print("RESULT: PASS")
        sys.exit(0)
    print("RESULT: FAIL")
    sys.exit(1)


if __name__ == "__main__":
    main()
