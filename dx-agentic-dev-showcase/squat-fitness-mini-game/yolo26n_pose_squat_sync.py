#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
YOLO26n-Pose Squat-Counting Fitness Mini-Game — Synchronous Inference

Real-time squat rep counter on the DEEPX NPU. Detects squats from body
keypoints (knee + hip angles) and overlays an arcade-style game HUD.

Usage:
    # Video file (annotated output video is saved with --save):
    python yolo26n_pose_squat_sync.py \
        --model ../../assets/models/yolo26n-pose.dxnn \
        --video ../../sample/squat_demo.mp4 --save

    # Live camera:
    python yolo26n_pose_squat_sync.py \
        --model ../../assets/models/yolo26n-pose.dxnn --camera 0

Framework note: this uses the mandatory IFactory + SyncRunner pattern. All
game logic lives in SquatGameVisualizer (called once per frame by SyncRunner).
"""

import sys
from pathlib import Path

# --- path setup (no PYTHONPATH required) ---------------------------------
_module_dir = Path(__file__).resolve().parent
# 1) session dir itself -> local modules: factory/, squat_rep_counter,
#    squat_game_visualizer
if str(_module_dir) not in sys.path:
    sys.path.insert(0, str(_module_dir))
# 2) walk up to locate the dx_app package root (src/python_example holding
#    `common`). The session dir lives at an arbitrary depth under dx_app, so we
#    search rather than assume a fixed number of `..`.
_pe = None
for _p in [_module_dir, *_module_dir.parents]:
    for cand in (_p / "src" / "python_example",
                 # relocated showcase: dx_app lives under dx-runtime/ from suite root
                 _p / "dx-runtime" / "dx_app" / "src" / "python_example"):
        if (cand / "common").is_dir():
            _pe = cand
            break
    if _pe is not None:
        break
if _pe is None:
    raise RuntimeError(
        "Could not locate src/python_example under any parent of "
        f"{_module_dir}. Run this app from within the dx_app tree.")
if str(_pe) not in sys.path:
    sys.path.insert(0, str(_pe))
# -------------------------------------------------------------------------

from factory import Yolo26nPoseSquatFactory          # noqa: E402
from common.runner import SyncRunner, parse_common_args  # noqa: E402


def main():
    args = parse_common_args("YOLO26n-Pose Squat Game (Sync)")
    factory = Yolo26nPoseSquatFactory()
    runner = SyncRunner(factory)
    runner.run(args)


if __name__ == "__main__":
    main()
