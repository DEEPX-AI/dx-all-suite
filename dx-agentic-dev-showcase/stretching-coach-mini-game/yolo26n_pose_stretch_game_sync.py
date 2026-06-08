#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
YOLO26n-Pose Arcade Stretching Mini-Game (synchronous).

Guides the player through three stretches (overhead reach, forward fold, neck
release) with an animated stick-figure coach, pose recognition, hold timers, and
an arcade UI overlay. Built on the dx_app IFactory + SyncRunner framework.

Usage:
    # Video file (saves an annotated output video):
    python yolo26n_pose_stretch_game_sync.py -m <model.dxnn> --video clip.mp4 --save
    # Live camera:
    python yolo26n_pose_stretch_game_sync.py -m <model.dxnn> --camera 0
"""

import sys
from pathlib import Path


def _setup_paths() -> None:
    """Put the session dir (factory + engine modules) and the python_example
    root (common package) on sys.path WITHOUT requiring a manual PYTHONPATH."""
    here = Path(__file__).resolve().parent
    # Walk up to locate the src/python_example root that holds `common/`.
    pe_root = None
    for parent in [here, *here.parents]:
        if (parent / "common" / "runner").is_dir() and parent.name == "python_example":
            pe_root = parent
            break
        if (parent / "src" / "python_example" / "common").is_dir():
            pe_root = parent / "src" / "python_example"
            break
        # Relocated showcase: dx_app lives under dx-runtime/ from the suite root.
        if (parent / "dx-runtime" / "dx_app" / "src" / "python_example" / "common").is_dir():
            pe_root = parent / "dx-runtime" / "dx_app" / "src" / "python_example"
            break
    if pe_root is None:
        raise RuntimeError(
            "Could not locate src/python_example/common from "
            f"{here}. Run from within the dx_app tree.")
    for p in (str(here), str(pe_root)):
        if p not in sys.path:
            sys.path.insert(0, p)


_setup_paths()

from common.runner import SyncRunner, parse_common_args   # noqa: E402
from factory import StretchGameFactory                    # noqa: E402


def main() -> None:
    args = parse_common_args("YOLO26n-Pose Stretch Game (sync)")
    factory = StretchGameFactory()
    runner = SyncRunner(factory)
    runner.run(args)


if __name__ == "__main__":
    main()
