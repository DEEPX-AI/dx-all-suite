#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""yolo26n_pose Squat Fitness Mini-Game (synchronous).

Counts squat reps from body keypoints on the DEEPX NPU and overlays an
arcade-style game HUD. Input source and annotated-video saving are provided by
the shared framework (SyncRunner + parse_common_args).

Usage:
    # video file -> annotated output video (saved under artifacts/.../output.mp4)
    python yolo26n_pose_squat_sync.py -m <model.dxnn> --video sample/squat_demo.mp4 --save

    # live camera
    python yolo26n_pose_squat_sync.py -m <model.dxnn> --camera 0
"""
import sys
from pathlib import Path

# --- resolve shared 'common' package + local packages (factory, squat_game) ---
# Walk up looking for dx_app's shared example tree. Two layouts are supported:
#   1. living inside dx_app           -> <parent>/src/python_example
#   2. living anywhere in the suite   -> <parent>/dx-runtime/dx_app/src/python_example
# so this app runs both from its original dx-agentic-dev session dir and from
# the relocated dx-agentic-dev-showcase/ directory.
_session_dir = Path(__file__).resolve().parent
_walk = _session_dir
for _ in range(8):
    for _cand in (_walk / "src" / "python_example",
                  _walk / "dx-runtime" / "dx_app" / "src" / "python_example"):
        if _cand.is_dir():
            if str(_cand) not in sys.path:
                sys.path.insert(0, str(_cand))
            break
    else:
        _walk = _walk.parent
        continue
    break
if str(_session_dir) not in sys.path:
    sys.path.insert(0, str(_session_dir))

from common.runner import SyncRunner, parse_common_args  # noqa: E402
from factory import SquatGameFactory  # noqa: E402


def main():
    args = parse_common_args("yolo26n_pose Squat Fitness Mini-Game (sync)")
    SyncRunner(SquatGameFactory()).run(args)


if __name__ == "__main__":
    main()
