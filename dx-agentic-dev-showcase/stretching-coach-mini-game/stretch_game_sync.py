#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Stretch Arcade — yolo26n-pose mini-game (synchronous, SyncRunner).

A 3-stage stretching mini-game on the DEEPX NPU:
  STAGE 1  overhead arm reach
  STAGE 2  forward fold at the waist
  STAGE 3  one-hand neck stretch
An animated stick-figure coach (derived from the sample clips) demonstrates each
target pose; holding the matching pose briefly clears the stage; CLEAR! when all
three are done.

Usage:
    python stretch_game_sync.py --model <yolo26n-pose.dxnn> --video <file> --save
    python stretch_game_sync.py --model <yolo26n-pose.dxnn> --camera 0

SyncRunner is used (not AsyncRunner) because the game is stateful and requires
strictly ordered frames.
"""

import sys
from pathlib import Path

# --- Portable framework resolution (NO PYTHONPATH) -------------------------
# Prefer a vendored ./common (created by setup.sh; lets this folder run even when
# copied entirely outside dx-all-suite). Fall back to dx_app's src/python_example
# for in-place development.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
if (_HERE / "common").is_dir():
    pass  # vendored: _HERE already on path provides `common`
else:
    _d = _HERE
    for _ in range(10):
        _cand = _d / "src" / "python_example"
        if (_cand / "common").is_dir():
            sys.path.insert(0, str(_cand))
            break
        _d = _d.parent
    else:
        sys.exit("ERROR: cannot find the dx_app 'common' framework. "
                 "Run setup.sh to vendor it into ./common.")

from factory import StretchGameFactory          # noqa: E402
from common.runner import SyncRunner, parse_common_args  # noqa: E402


def main():
    args = parse_common_args("Stretch Arcade (yolo26n-pose) Sync Mini-Game")
    runner = SyncRunner(StretchGameFactory())
    runner.run(args)


if __name__ == "__main__":
    main()
