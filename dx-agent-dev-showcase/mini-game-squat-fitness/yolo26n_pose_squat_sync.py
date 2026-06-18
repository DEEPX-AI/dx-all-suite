#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
yolo26n-pose Squat Fitness Mini-Game — Synchronous Inference (DX-APP v3.0.0)

Counts squats in real time from yolo26n-pose keypoints on the DEEPX DX-M1 NPU
and renders a game HUD (rep counter, depth bar, GOOD REP banner).

Usage:
    python yolo26n_pose_squat_sync.py --model yolo26n-pose.dxnn \
        --video sample/squat_demo.mp4 --no-display --save
"""

import sys
from pathlib import Path

# Dynamic root finder (standalone, no PYTHONPATH). Prefers a vendored ./common
# (fully portable — runs even when copied OUTSIDE dx-all-suite), else falls back
# to dx_app's src/python_example (in-place dev). NEVER use static parent.parent.
_module_dir = Path(__file__).parent
_current = Path(__file__).resolve().parent
if (_current / 'common').is_dir():
    _v3_dir = _current
else:
    _v3_dir = None
    for _a in [_current, *_current.parents]:
        for _cand in (_a / 'src' / 'python_example',
                      _a / 'dx-runtime' / 'dx_app' / 'src' / 'python_example'):
            if (_cand / 'common').exists():
                _v3_dir = _cand
                break
        if _v3_dir is not None:
            break
for _path in [str(_v3_dir), str(_module_dir)]:
    if _path and _path not in sys.path:
        sys.path.insert(0, _path)

from factory import SquatGameFactory
from common.runner import SyncRunner, parse_common_args


def parse_args():
    return parse_common_args("yolo26n-pose Squat Fitness Mini-Game (Sync)")


def main():
    args = parse_args()
    factory = SquatGameFactory()
    runner = SyncRunner(factory)
    runner.run(args)
    # Final score summary
    try:
        vis = runner.visualizer
        if vis is not None and hasattr(vis, "counter"):
            print(f"\n[SQUAT GAME] Final score — total squats counted: "
                  f"{vis.counter.count}")
    except Exception:
        pass


if __name__ == "__main__":
    main()
