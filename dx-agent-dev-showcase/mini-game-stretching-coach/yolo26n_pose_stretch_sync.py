#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Stretch Coach — arcade stretching mini-game (yolo26n-pose, DX-M1 NPU).

Guides the player through 3 stretches, one stage at a time, recognising each
pose from COCO-17 keypoints and advancing when the pose is held briefly:
    1) OVERHEAD REACH  2) FORWARD FOLD  3) NECK STRETCH

Built on the IFactory + SyncRunner framework: StretchPoseFactory reuses the
yolo26n-pose preprocessor/postprocessor and supplies a custom visualizer that
runs the game. SyncRunner drives the per-frame loop for both video and camera
and (with --save) writes an annotated output video.

Usage:
    # video file (saves annotated output video)
    python yolo26n_pose_stretch_sync.py --model <path>.dxnn \
        --video sample/stretching_demo.mp4 --save --save-dir ./output

    # live camera
    python yolo26n_pose_stretch_sync.py --model <path>.dxnn --camera 0
"""

import sys
from pathlib import Path

# --- Dynamic root finder (standalone, no PYTHONPATH). Prefer a vendored ./common
# so the app runs even when copied OUTSIDE dx-all-suite; otherwise fall back to
# dx_app's src/python_example (in-place dev), searching ancestors incl. a
# suite-root hop. ---
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
_module_dir = Path(__file__).parent
for _path in [str(_v3_dir), str(_module_dir)]:
    if _path and _path not in sys.path:
        sys.path.insert(0, _path)

from factory import StretchPoseFactory
from common.runner import SyncRunner, parse_common_args


def main():
    args = parse_common_args("yolo26n-pose Stretch Coach mini-game")
    factory = StretchPoseFactory()
    runner = SyncRunner(factory)
    runner.run(args)


if __name__ == "__main__":
    main()
