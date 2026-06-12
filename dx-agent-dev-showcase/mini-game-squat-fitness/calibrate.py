#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Calibrate squat-detection thresholds from a real video.

Runs the actual yolo26n-pose NPU pipeline over the sample squat video, measures
the per-frame knee (hip-knee-ankle) and hip (shoulder-hip-knee) angle
distributions, and derives data-driven DOWN/UP thresholds with a hysteresis
gap. 2D knee angles at squat bottom rarely reach the textbook 90 degrees, so
fixed cutoffs miscount — hence calibration. Results are written into config.json.

Usage:
    python calibrate.py [--model <dxnn>] [--video <mp4>]
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import cv2

_HERE = Path(__file__).resolve().parent


def _find_dev_common_root(start: Path):
    d = start
    for _ in range(8):
        cand = d / "src" / "python_example"
        if (cand / "common" / "__init__.py").is_file():
            return cand
        d = d.parent
    return None


_dev_root = _find_dev_common_root(_HERE)
if _dev_root is not None and str(_dev_root) not in sys.path:
    sys.path.insert(0, str(_dev_root))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from dx_engine import InferenceEngine                # noqa: E402
from factory import SquatGameFactory                 # noqa: E402
from factory.squat_game_visualizer import SquatGameVisualizer  # noqa: E402


def _suite_root(start: Path):
    d = start
    for _ in range(8):
        if (d / "dx-runtime").is_dir() and (d / "dx-compiler").is_dir():
            return d
        d = d.parent
    return None


def _model_filename():
    """Model filename, sourced from app.yaml (config — not hardcoded in code)."""
    y = _HERE / "app.yaml"
    if y.is_file():
        for line in y.read_text().splitlines():
            s = line.strip()
            if s.startswith("dxnn_file:"):
                return s.split(":", 1)[1].strip()
    return None


def _default_model():
    import glob
    name = _model_filename()
    search = [_HERE, _HERE.parent.parent / "assets" / "models"]
    sr = _suite_root(_HERE)
    if sr:
        search.append(sr / "dx-runtime" / "dx_app" / "assets" / "models")
    for d in search:
        if name and (Path(d) / name).is_file():
            return str(Path(d) / name)
        hits = sorted(glob.glob(str(Path(d) / ("*pose*" + os.extsep + "dxnn"))))
        if hits:
            return hits[0]
    return str(_HERE.parent.parent / "assets" / "models" / (name or "model"))


def _default_video():
    for cand in [_HERE / "sample" / "squat_demo.mp4",
                 _HERE.parent.parent / "sample" / "squat_demo.mp4"]:
        if cand.is_file():
            return str(cand)
    return str(_HERE.parent.parent / "sample" / "squat_demo.mp4")


def main():
    ap = argparse.ArgumentParser(description="Calibrate squat thresholds")
    ap.add_argument("--model", "-m", default=_default_model())
    ap.add_argument("--video", "-v", default=_default_video())
    ap.add_argument("--max-frames", type=int, default=100000)
    args = ap.parse_args()

    if not os.path.isfile(args.model):
        print(f"[ERROR] model not found: {args.model}")
        sys.exit(1)
    if not os.path.isfile(args.video):
        print(f"[ERROR] video not found: {args.video}")
        sys.exit(1)

    cfg_path = _HERE / "config.json"
    config = json.load(open(cfg_path)) if cfg_path.is_file() else {}

    ie = InferenceEngine(args.model)
    info = ie.get_input_tensors_info()[0]
    shape = info["shape"]
    if len(shape) >= 4 and shape[-1] in (1, 3, 4):
        ih, iw = shape[1], shape[2]
    elif len(shape) >= 4:
        ih, iw = shape[2], shape[3]
    else:
        ih, iw = shape[1], shape[2]

    factory = SquatGameFactory(config)
    pre = factory.create_preprocessor(iw, ih)
    post = factory.create_postprocessor(iw, ih)
    helper = SquatGameVisualizer(config)  # reuse angle extraction

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        print(f"[ERROR] cannot open video: {args.video}")
        sys.exit(1)

    knees, hips = [], []
    frames = 0
    while frames < args.max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        frames += 1
        tensor, ctx = pre.process(frame)
        outputs = ie.run([tensor])
        results = post.process(outputs, ctx)
        person = helper._largest_person(results) if results else None
        if person is None:
            continue
        k = helper._knee_angle(person.keypoints)
        hh = helper._hip_angle(person.keypoints)
        if k is not None:
            knees.append(k)
        if hh is not None:
            hips.append(hh)
    cap.release()

    print(f"\nFrames processed: {frames}  | valid knee angles: {len(knees)}"
          f"  | valid hip angles: {len(hips)}")

    if len(knees) < 10:
        print("[WARN] too few valid knee samples; keeping existing thresholds.")
        sys.exit(0)

    ka = np.array(knees)
    low = float(np.percentile(ka, 15))   # near squat bottom
    high = float(np.percentile(ka, 85))  # near standing
    span = max(1.0, high - low)
    knee_down = round(low + 0.35 * span, 1)
    knee_up = round(low + 0.70 * span, 1)
    if knee_up - knee_down < 8.0:         # enforce min hysteresis gap
        mid = (knee_up + knee_down) / 2.0
        knee_down = round(mid - 5.0, 1)
        knee_up = round(mid + 5.0, 1)

    print("Knee angle distribution (deg):")
    for p in (5, 15, 25, 50, 75, 85, 95):
        print(f"   p{p:02d} = {np.percentile(ka, p):6.1f}")
    print(f"   min={ka.min():.1f}  max={ka.max():.1f}  mean={ka.mean():.1f}")

    if hips:
        ha = np.array(hips)
        hip_down = round(float(np.percentile(ha, 85)), 1)  # permissive gate
        print("Hip angle distribution (deg):")
        for p in (5, 25, 50, 75, 95):
            print(f"   p{p:02d} = {np.percentile(ha, p):6.1f}")
    else:
        hip_down = config.get("hip_down_angle", 150.0)

    config["knee_down_angle"] = knee_down
    config["knee_up_angle"] = knee_up
    config["hip_down_angle"] = hip_down
    config.setdefault("kpt_conf_threshold", 0.3)

    with open(cfg_path, "w") as f:
        json.dump(config, f, indent=4)
        f.write("\n")

    print(f"\nCalibrated thresholds written to {cfg_path.name}:")
    print(f"   knee_down_angle = {knee_down}")
    print(f"   knee_up_angle   = {knee_up}")
    print(f"   hip_down_angle  = {hip_down}")


if __name__ == "__main__":
    main()
