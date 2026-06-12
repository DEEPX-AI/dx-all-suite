#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Calibration probe for the Stretch Coach mini-game.

Runs the REAL yolo26n-pose model on the DX-M1 NPU over sampled frames of the
demo video and prints, per sampled frame, the scale-invariant pose metrics used
by the game's PoseClassifier. This is how the pose thresholds in config.json are
derived from representative frames of the actual video (not guessed).

Usage:
    python calibrate.py [--model <path>] [--video <path>] [--every 0.4]
"""

import argparse
import sys
from pathlib import Path

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

import numpy as np
import cv2
from dx_engine import InferenceEngine

from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor

# COCO-17 indices
NOSE, L_EYE, R_EYE, L_EAR, R_EAR = 0, 1, 2, 3, 4
L_SHO, R_SHO, L_ELB, R_ELB, L_WRI, R_WRI = 5, 6, 7, 8, 9, 10
L_HIP, R_HIP = 11, 12


def _xy(kp):
    return np.array([kp.x, kp.y], dtype=np.float32)


def metrics_for(pose, kp_conf=0.30):
    """Return dict of scale-invariant metrics, or None if torso not visible."""
    kps = pose.keypoints
    if len(kps) < 17:
        return None
    nose, ls, rs = kps[NOSE], kps[L_SHO], kps[R_SHO]
    lh, rh, lw, rw = kps[L_HIP], kps[R_HIP], kps[L_WRI], kps[R_WRI]
    if min(ls.confidence, rs.confidence, lh.confidence, rh.confidence) < kp_conf:
        return None
    sho_mid = (_xy(ls) + _xy(rs)) / 2.0
    hip_mid = (_xy(lh) + _xy(rh)) / 2.0
    S = float(np.linalg.norm(_xy(ls) - _xy(rs))) or 1.0
    head = _xy(nose) if nose.confidence >= kp_conf else sho_mid
    m = {
        "S": S,
        # overhead: how far each wrist is ABOVE the nose, in shoulder-widths (+ = above)
        "lw_above_nose": (head[1] - lw.y) / S if lw.confidence >= kp_conf else -9,
        "rw_above_nose": (head[1] - rw.y) / S if rw.confidence >= kp_conf else -9,
        "lw_above_sho": (sho_mid[1] - lw.y) / S if lw.confidence >= kp_conf else -9,
        "rw_above_sho": (sho_mid[1] - rw.y) / S if rw.confidence >= kp_conf else -9,
        # forward fold: head height above hips in shoulder-widths (small => folded)
        "fold_ratio": (hip_mid[1] - head[1]) / S,
        # neck: min distance of either wrist to head, in shoulder-widths
        "lw_head_dist": float(np.linalg.norm(_xy(lw) - head)) / S if lw.confidence >= kp_conf else 9,
        "rw_head_dist": float(np.linalg.norm(_xy(rw) - head)) / S if rw.confidence >= kp_conf else 9,
        # how far each wrist is BELOW the shoulder (+ = below/low)
        "lw_below_sho": (lw.y - sho_mid[1]) / S if lw.confidence >= kp_conf else -9,
        "rw_below_sho": (rw.y - sho_mid[1]) / S if rw.confidence >= kp_conf else -9,
    }
    return m


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Stretch game calibration probe")
    default_model = here.parents[1] / "assets" / "models" / "yolo26n-pose.dxnn"
    ap.add_argument("--model", default=str(default_model))
    ap.add_argument("--video", default=str(here / "sample" / "stretching_demo.mp4"))
    ap.add_argument("--every", type=float, default=0.4, help="sample interval (s)")
    args = ap.parse_args()

    ie = InferenceEngine(args.model)
    shape = ie.get_input_tensors_info()[0]["shape"]
    if len(shape) >= 4 and shape[-1] in (1, 3, 4):
        ih, iw = shape[1], shape[2]
    else:
        ih, iw = shape[2], shape[3]
    pre = LetterboxPreprocessor(iw, ih)
    post = YOLOv8PosePostprocessor(iw, ih, {"score_threshold": 0.4, "nms_threshold": 0.45})

    cap = cv2.VideoCapture(args.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, int(round(args.every * fps)))
    print(f"Model {iw}x{ih} | video fps={fps:.1f} frames={total} | sampling every {step} frames")
    print(f"{'t(s)':>5} {'det':>3} {'foldR':>6} {'lwAboveN':>8} {'rwAboveN':>8} "
          f"{'minHeadD':>8} {'lwLow':>6} {'rwLow':>6}  guess")

    fi = 0
    detected = 0
    agg = {"fold_ratio": [], "overhead_min": [], "neck_min_head": []}
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if fi % step != 0:
            fi += 1
            continue
        t = fi / fps
        tensor, ctx = pre.process(frame)
        outputs = ie.run([tensor])
        results = post.process(outputs, ctx)
        if not results:
            print(f"{t:5.1f} {0:3d}   (no person)")
            fi += 1
            continue
        detected += 1
        pose = max(results, key=lambda r: (r.box[2] - r.box[0]) * (r.box[3] - r.box[1]))
        m = metrics_for(pose)
        if m is None:
            print(f"{t:5.1f} {len(results):3d}   (torso not visible)")
            fi += 1
            continue
        oh_min = min(m["lw_above_nose"], m["rw_above_nose"])
        min_head = min(m["lw_head_dist"], m["rw_head_dist"])
        # naive guess for inspection only
        guess = "stand"
        if m["lw_above_nose"] > 0.15 and m["rw_above_nose"] > 0.15:
            guess = "OVERHEAD"
        elif m["fold_ratio"] < 1.3:
            guess = "FOLD"
        elif (min_head < 1.1 and max(m["lw_below_sho"], m["rw_below_sho"]) > 0.55
              and min(m["lw_above_nose"], m["rw_above_nose"]) < 0.1):
            guess = "NECK"
        agg["fold_ratio"].append(m["fold_ratio"])
        agg["overhead_min"].append(oh_min)
        agg["neck_min_head"].append(min_head)
        print(f"{t:5.1f} {len(results):3d} {m['fold_ratio']:6.2f} "
              f"{m['lw_above_nose']:8.2f} {m['rw_above_nose']:8.2f} "
              f"{min_head:8.2f} {m['lw_below_sho']:6.2f} {m['rw_below_sho']:6.2f}  {guess}")
        fi += 1
    cap.release()

    print(f"\nFrames with detection: {detected}")
    for k, v in agg.items():
        if v:
            arr = np.array(v)
            print(f"  {k:14s} min={arr.min():6.2f} median={np.median(arr):6.2f} max={arr.max():6.2f}")
    print("RESULT: PASS" if detected > 0 else "RESULT: FAIL")
    sys.exit(0 if detected > 0 else 1)


if __name__ == "__main__":
    main()
