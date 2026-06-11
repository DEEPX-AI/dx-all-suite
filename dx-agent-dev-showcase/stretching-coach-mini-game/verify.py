#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""End-to-end validation for the stretch mini-game.

Drives the REAL deployed StretchGameVisualizer (created by StretchGameFactory)
over the sample clips on the NPU and asserts:
  * each per-pose clip clears its target stage (seeded at that stage),
  * the combined stretching_demo.mp4 reaches full CLEAR! from a fresh game,
and saves an annotated output video for each run.

Exit code 0 + "RESULT: PASS" on success; exit 1 otherwise.

Usage: python verify.py [--model PATH]
"""

import argparse
import json
import sys
from pathlib import Path

import cv2

import _bootstrap
_bootstrap.setup()

import game_eval  # noqa: E402
from factory import StretchGameFactory  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "outputs"
SAVE_FPS = 24.0  # sample clips are 24 fps


def _find_dx_app_root() -> Path:
    d = HERE
    for _ in range(10):
        if (d / "assets" / "models").is_dir() and (d / "sample").is_dir():
            return d
        d = d.parent
    raise FileNotFoundError("Could not locate dx_app root.")


def _run_clip(runner, config, clip_path, seed_stage, out_name, expect_clear):
    factory = StretchGameFactory()
    factory.load_config(config)
    vis = factory.create_visualizer()
    vis.game.idx = seed_stage
    start_idx = vis.game.idx

    OUT_DIR.mkdir(exist_ok=True)
    writer = None
    out_path = OUT_DIR / out_name
    frames = 0
    for _idx, frame, results in game_eval.iter_results(runner, clip_path):
        out = vis.visualize(frame, results)
        if writer is None:
            h, w = out.shape[:2]
            writer = cv2.VideoWriter(str(out_path),
                                     cv2.VideoWriter_fourcc(*"mp4v"), SAVE_FPS, (w, h))
        writer.write(out)
        frames += 1
    if writer is not None:
        writer.release()

    g = vis.game
    if expect_clear:
        ok = g.cleared
        detail = f"cleared={g.cleared} reached_stage={g.stage_number}/{g.total_stages}"
    else:
        ok = g.idx > start_idx
        detail = f"advanced {start_idx}->{g.idx} (target stage cleared={ok})"
    print(f"  [{'PASS' if ok else 'FAIL'}] {out_name}: {frames} frames, {detail}, "
          f"saved {out_path.name}")
    return ok


def main():
    ap = argparse.ArgumentParser(description="Verify the stretch mini-game")
    ap.add_argument("--model", default=None, help="Path to yolo26n-pose.dxnn")
    args = ap.parse_args()

    root = _find_dx_app_root()
    model = args.model or str(root / "assets" / "models" / "yolo26n-pose.dxnn")
    if not Path(model).is_file():
        print(f"RESULT: FAIL — model not found: {model}")
        return 1
    config = json.loads((HERE / "config.json").read_text())

    print(f"[verify] model = {model}")
    runner = game_eval.build_runner(model)

    sample = root / "sample"
    cases = [
        # (clip, seed_stage, out_name, expect_clear)
        (sample / "stretching_extending_both_arms.mp4", 0, "overhead.mp4", False),
        (sample / "stretching_bending_at_the_waist.mp4", 1, "fold.mp4", False),
        (sample / "stretching_pulling_the_head.mp4", 2, "neck.mp4", False),
        (sample / "stretching_demo.mp4", 0, "demo_full.mp4", True),
    ]
    print("[verify] === per-clip stage clears + end-to-end CLEAR ===")
    results = []
    for clip, seed, name, expect in cases:
        if not clip.is_file():
            print(f"  [FAIL] missing clip: {clip}")
            results.append(False)
            continue
        results.append(_run_clip(runner, config, str(clip), seed, name, expect))

    ok = all(results)
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
