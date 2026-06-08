#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Threshold calibration tool for the squat game.

Runs the yolo26n-pose model over a reference video, measures the per-frame
(smoothed) knee angle, and suggests ``knee_down_angle`` / ``knee_up_angle`` from
the OBSERVED distribution — because a 2D knee angle bottoms out around 120-140
degrees, not 90, and the right thresholds are data-dependent.

This is an offline measurement *tool*, not the inference demo. It reuses the
framework's own SyncRunner pipeline (preprocess/infer/postprocess) and the
game's angle-extraction logic, so the measured angles match what the live app
sees frame-for-frame.

Usage:
    python calibrate_squat.py --model <path.dxnn> --video <path.mp4>
"""

import argparse
import sys
from collections import deque
from pathlib import Path

import cv2

_module_dir = Path(__file__).resolve().parent
if str(_module_dir) not in sys.path:
    sys.path.insert(0, str(_module_dir))
_pe = None
for _p in [_module_dir, *_module_dir.parents]:
    cand = _p / "src" / "python_example"
    if (cand / "common").is_dir():
        _pe = cand
        break
if _pe is None:
    raise RuntimeError("Could not locate src/python_example.")
if str(_pe) not in sys.path:
    sys.path.insert(0, str(_pe))

from factory import Yolo26nPoseSquatFactory          # noqa: E402
from common.runner import SyncRunner                 # noqa: E402
from squat_rep_counter import SquatRepCounter        # noqa: E402


def percentile(sorted_vals, q):
    if not sorted_vals:
        return None
    idx = min(len(sorted_vals) - 1, max(0, int(round(q * (len(sorted_vals) - 1)))))
    return sorted_vals[idx]


def main():
    ap = argparse.ArgumentParser(description="Calibrate squat knee-angle thresholds")
    ap.add_argument("--model", "-m", required=True)
    ap.add_argument("--video", "-v", required=True)
    ap.add_argument("--config", default=str(_module_dir / "config.json"))
    ap.add_argument("--smoothing-window", type=int, default=5)
    args = ap.parse_args()

    factory = Yolo26nPoseSquatFactory()
    runner = SyncRunner(factory)
    runner._verbose = False
    runner._model_path = args.model
    runner._init_engine(args.model, args.config)   # framework engine + components

    viz = factory.create_visualizer()              # reuse angle extraction
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"ERROR: cannot open video {args.video}")
        return 1

    hist = deque(maxlen=max(1, args.smoothing_window))
    angles = []
    frames = 0
    with_person = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames += 1
        tensor, ctx = runner.preprocess(frame)
        outputs = runner.infer(tensor)
        results = runner.postprocess(outputs, ctx)
        pose = viz._primary_pose(results)
        if pose is None:
            continue
        knee, _hip = viz._extract_angles(pose)
        if knee is None:
            continue
        with_person += 1
        hist.append(knee)
        angles.append(sum(hist) / len(hist))
    cap.release()

    if not angles:
        print(f"Frames={frames}, person+knee frames=0 -> NO ANGLES MEASURED")
        return 1

    angles_sorted = sorted(angles)
    a_min = angles_sorted[0]
    a_max = angles_sorted[-1]
    p10 = percentile(angles_sorted, 0.10)
    p90 = percentile(angles_sorted, 0.90)

    # Suggested thresholds: place down/up between the bottom and top clusters with
    # margin, ensuring a clear hysteresis gap.
    down = round(p10 + 0.30 * (p90 - p10), 1)
    up = round(p90 - 0.20 * (p90 - p10), 1)
    if up - down < 8:           # guarantee a usable hysteresis band
        mid = (up + down) / 2.0
        down, up = round(mid - 6, 1), round(mid + 6, 1)

    # How many reps would these thresholds detect on this clip?
    test_cfg = {"knee_down_angle": down, "knee_up_angle": up,
                "smoothing_window": args.smoothing_window, "min_state_frames": 3,
                "target_reps": 999}
    c = SquatRepCounter(test_cfg)
    for a in angles:
        c.update(a)

    print("==================== SQUAT CALIBRATION ====================")
    print(f"video                 : {args.video}")
    print(f"frames total          : {frames}")
    print(f"frames with knee angle: {with_person}")
    print(f"knee angle  min / max : {a_min:.1f} / {a_max:.1f} deg")
    print(f"knee angle  p10 / p90 : {p10:.1f} / {p90:.1f} deg")
    print(f"suggested knee_down   : {down} deg")
    print(f"suggested knee_up     : {up} deg")
    print(f"reps detected @ above : {c.reps}")
    print("===========================================================")
    # Machine-readable line for scripted threshold update:
    print(f"SUGGEST knee_down_angle={down} knee_up_angle={up} reps={c.reps}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
