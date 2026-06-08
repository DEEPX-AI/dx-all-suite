#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Arcade Stretching Mini-Game (yolo26n-pose, synchronous).

Guides the player through three stretches — overhead reach, forward fold, neck
stretch — one stage at a time, with an animated coach avatar, HOLD progress, and
GOOD!/CLEAR! feedback. Uses the IFactory + SyncRunner pattern; the game logic
lives in StretchGameVisualizer (created by StretchGameFactory). SyncRunner keeps
frames ordered, which is required for correct hold-timing.

Usage:
    # video file (saves an annotated output.mp4 with --save)
    python stretch_game_sync.py -m <model.dxnn> --video sample/stretching_demo.mp4 --save
    # live camera
    python stretch_game_sync.py -m <model.dxnn> --camera 0
"""

import sys
from pathlib import Path

# ---- dynamic path walker: add src/python_example (for `common`) + this dir ---
_HERE = Path(__file__).resolve().parent


def _bootstrap_paths():
    d = _HERE
    for _ in range(8):
        for pe in (d / "src" / "python_example",
                   # relocated showcase: dx_app lives under dx-runtime/ from suite root
                   d / "dx-runtime" / "dx_app" / "src" / "python_example"):
            if (pe / "common").is_dir():
                for p in (str(pe), str(_HERE)):
                    if p not in sys.path:
                        sys.path.insert(0, p)
                return
        d = d.parent
    raise RuntimeError("Could not locate src/python_example/common from "
                       f"{_HERE}")


_bootstrap_paths()

from factory import StretchGameFactory          # noqa: E402
from common.runner import SyncRunner, parse_common_args  # noqa: E402


def main():
    args = parse_common_args("YOLO26n-Pose Arcade Stretching Game (sync)")
    runner = SyncRunner(StretchGameFactory())
    runner.run(args)


if __name__ == "__main__":
    main()
