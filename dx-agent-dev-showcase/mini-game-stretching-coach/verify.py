#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Verification for the Stretch Coach mini-game.

Runs the game over the ENTIRE demo video on the DX-M1 NPU (headless), via the
real IFactory + SyncRunner path with --save, then asserts:
  1) the NPU pose pipeline produced person detections,
  2) the game state machine reached CLEAR! (all 3 stages cleared),
  3) an annotated output video was written and is non-trivial in size.

Exit code 0 on success, 1 on any failure. Run inside the dx-runtime venv
(setup.sh provides dx_engine).
"""

import argparse
import glob
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

# --- Dynamic root finder (vendored ./common first; no PYTHONPATH) ---
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
for _path in [str(_v3_dir), str(_current)]:
    if _path and _path not in sys.path:
        sys.path.insert(0, _path)

from factory import StretchPoseFactory
from common.runner import SyncRunner


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Stretch Coach verification")
    ap.add_argument("--model", default=str(here.parents[1] / "assets" / "models" / "yolo26n-pose.dxnn"))
    ap.add_argument("--video", default=str(here / "sample" / "stretching_demo.mp4"))
    args_cli = ap.parse_args()

    save_dir = str(here / "output")
    config_path = str(here / "config.json")

    print("=" * 60)
    print("Stretch Coach — verification (full demo video on NPU)")
    print(f"  model:  {args_cli.model}")
    print(f"  video:  {args_cli.video}")
    print("=" * 60)

    if not os.path.isfile(args_cli.model):
        print(f"[FAIL] model not found: {args_cli.model}")
        print("RESULT: FAIL")
        sys.exit(1)
    if not os.path.isfile(args_cli.video):
        print(f"[FAIL] demo video not found: {args_cli.video}")
        print("RESULT: FAIL")
        sys.exit(1)

    factory = StretchPoseFactory()
    runner = SyncRunner(factory)

    run_args = SimpleNamespace(
        model=args_cli.model, image=None, video=args_cli.video, camera=None, rtsp=None,
        display=False, save=True, save_dir=save_dir, loop=1, dump_tensors=False,
        config=config_path, show_log=False,
    )
    runner.run(run_args)

    game = factory._visualizer.game
    checks = []

    ok_det = game.person_frames > 0
    checks.append(("NPU produced person detections", ok_det,
                   f"{game.person_frames} frames with pose"))

    ok_clear = bool(game.finished) and game.stages_cleared >= 3
    checks.append(("State machine reached CLEAR! (3/3 stages)", ok_clear,
                   f"stages_cleared={game.stages_cleared} finished={game.finished}"))

    vids = sorted(glob.glob(os.path.join(save_dir, "**", "output.mp4"), recursive=True)
                  + glob.glob(os.path.join(save_dir, "**", "output.avi"), recursive=True))
    out_video = vids[-1] if vids else None
    size = os.path.getsize(out_video) if out_video else 0
    ok_video = out_video is not None and size > 50_000
    checks.append(("Annotated output video written", ok_video,
                   f"{out_video} ({size} bytes)" if out_video else "no output video found"))

    print("\n--- checks ---")
    all_ok = True
    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {detail}")
        all_ok = all_ok and ok

    if out_video:
        print(f"\nAnnotated output video: {out_video}")
    print("\nRESULT: PASS" if all_ok else "\nRESULT: FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
