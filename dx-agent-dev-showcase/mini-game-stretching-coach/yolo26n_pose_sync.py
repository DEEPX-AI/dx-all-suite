#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Stretch Arcade — yolo26n-pose stretching mini-game (Synchronous, DX-M1 NPU).

Runs yolo26n-pose on the DEEPX NPU and overlays an arcade-style 3-stage
stretching coach. Game logic lives in the visualizer (StretchCoachVisualizer);
this entry just wires the IFactory into SyncRunner, so it inherits the standard
input/output options.

Usage:
    # Validate on the bundled demo video (headless, save annotated output)
    python yolo26n_pose_sync.py --model <yolo26n-pose.dxnn> \
        --video sample/stretching_demo.mp4 --no-display --save

    # Live camera
    python yolo26n_pose_sync.py --model <yolo26n-pose.dxnn> --camera 0
"""

import sys
from pathlib import Path

# Dynamic root finder (standalone, no PYTHONPATH). Resolves the shared `common`
# package from ANY location: src/python_example/<task>/<model>/, dx-agent-dev/
# <session>/, AND when relocated outside dx_app (a vendored ./common is preferred,
# so the app folder runs even when copied OUTSIDE dx-all-suite).
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

from factory import StretchGameFactory
from common.runner import SyncRunner, parse_common_args


def parse_args():
    return parse_common_args("Stretch Arcade (yolo26n-pose) Sync Inference")


def main():
    args = parse_args()
    factory = StretchGameFactory()
    runner = SyncRunner(factory)
    runner.run(args)


if __name__ == "__main__":
    main()
