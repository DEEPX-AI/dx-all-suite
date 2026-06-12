#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
yolo26n-pose Squat-Counting Fitness Mini-Game — Synchronous Inference.

Runs yolo26n-pose on the DEEPX NPU via the IFactory + SyncRunner pattern, counts
squat repetitions from body keypoints (knee + hip angles), and overlays an
arcade game UI. Works on a video file or a live camera, selectable at runtime.

Usage:
    # video file (and save an annotated output video)
    python yolo26n_pose_squat_sync.py -m <yolo26n-pose.dxnn> --video sample/squat_demo.mp4 --save
    # live camera
    python yolo26n_pose_squat_sync.py -m <yolo26n-pose.dxnn> --camera 0
    # custom goal
    python yolo26n_pose_squat_sync.py -m <yolo26n-pose.dxnn> --video sample/squat_demo.mp4 --target-reps 15

All standard SyncRunner options (--video/-v, --camera/-c, --image/-i, --save/-s,
--no-display, --config, --loop ...) are inherited from parse_common_args.
"""

import os
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# Self-contained import resolution (NO PYTHONPATH required).
# Priority: this app dir (vendored ./common + ./factory) THEN, for in-place
# dev, dx_app/src/python_example. So the folder runs even when copied entirely
# outside dx-all-suite (any machine with the DEEPX runtime).
# ----------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent


def _find_dev_common_root(start: Path):
    """Walk up to locate dx_app/src/python_example (in-place dev fallback)."""
    d = start
    for _ in range(8):
        cand = d / "src" / "python_example"
        if (cand / "common" / "__init__.py").is_file():
            return cand
        d = d.parent
    return None


_dev_root = _find_dev_common_root(_HERE)
if _dev_root is not None and str(_dev_root) not in sys.path:
    sys.path.insert(0, str(_dev_root))      # lower priority (dev fallback)
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))          # highest priority (vendored ./common)

from factory import SquatGameFactory                       # noqa: E402
from common.runner import SyncRunner, parse_common_args     # noqa: E402


def _pop_target_reps(argv):
    """Extract --target-reps[=N] from argv so parse_common_args stays intact."""
    target = None
    out = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--target-reps":
            if i + 1 < len(argv):
                target = int(argv[i + 1])
                i += 2
                continue
            i += 1
            continue
        if a.startswith("--target-reps="):
            target = int(a.split("=", 1)[1])
            i += 1
            continue
        out.append(a)
        i += 1
    return target, out


def main():
    target, remaining = _pop_target_reps(sys.argv[1:])
    sys.argv = [sys.argv[0]] + remaining

    overrides = {}
    if target is not None:
        if target < 1:
            print("[ERROR] --target-reps must be >= 1", file=sys.stderr)
            sys.exit(2)
        overrides["target_reps"] = target

    args = parse_common_args(
        "yolo26n-pose Squat-Counting Fitness Mini-Game (sync)")

    factory = SquatGameFactory(overrides)
    runner = SyncRunner(factory)
    runner.run(args)


if __name__ == "__main__":
    main()
