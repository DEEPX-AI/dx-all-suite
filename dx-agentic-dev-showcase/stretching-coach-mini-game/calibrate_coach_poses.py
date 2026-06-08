#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Derive the coach-avatar target poses DIRECTLY from the sample clips.

For each stretch, run yolo26n-pose over its sample clip, keep the frames whose
recognizer fires, normalize each matching skeleton into a unit box (aspect
preserved), and store the per-keypoint median as that stretch's target pose.
A neutral standing pose is derived from frames where no stretch fires. The
result overwrites coach_poses.json (the app then animates neutral<->target).

This is an offline calibration tool (requires the NPU). The deployed game app
itself uses the IFactory + SyncRunner pattern; this script only extracts data.

Usage:
    python calibrate_coach_poses.py [-m <model.dxnn>] [--out coach_poses.json]
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

# ---- dynamic path walker: locate src/python_example/common ----------------
_HERE = Path(__file__).resolve().parent


def _find_common_root() -> Path:
    d = _HERE
    for _ in range(8):
        cand = d / "src" / "python_example" / "common"
        if cand.is_dir():
            return d / "src" / "python_example"
        d = d.parent
    raise RuntimeError("Could not locate src/python_example/common")


_PE = _find_common_root()
if str(_PE) not in sys.path:
    sys.path.insert(0, str(_PE))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import cv2  # noqa: E402
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor  # noqa: E402
from stretch_pose_rules import (  # noqa: E402
    STRETCHES, body_scale, DEFAULT_RULE_CFG,
    is_overhead_reach, is_forward_fold, is_neck_stretch,
    L_WRI, R_WRI, L_EAR, R_EAR, L_SHO, R_SHO,
)

_DXAPP_ROOT = _PE.parent.parent  # .../dx_app
_DEFAULT_MODEL = _DXAPP_ROOT / "assets" / "models" / "yolo26n-pose.dxnn"
_SAMPLE_DIR = _DXAPP_ROOT / "sample"

CLIPS = {
    "overhead": "stretching_extending_both_arms.mp4",
    "fold": "stretching_bending_at_the_waist.mp4",
    "neck": "stretching_pulling_the_head.mp4",
}


def _result_to_kp(pose) -> np.ndarray:
    kp = np.zeros((17, 3), dtype=np.float32)
    for i, k in enumerate(pose.keypoints[:17]):
        kp[i] = (k.x, k.y, k.confidence)
    return kp


def _largest(results):
    if not results:
        return None
    return max(results, key=lambda r: (r.box[2] - r.box[0]) * (r.box[3] - r.box[1])
               if r.box and len(r.box) >= 4 else 0.0)


def _normalize(kp: np.ndarray, conf: float) -> np.ndarray:
    """Translate/scale valid keypoints into a unit box, aspect preserved.
    Invalid keypoints are placed at the body centroid (so limbs stay sane)."""
    valid = kp[:, 2] >= conf
    pts = kp[valid, :2]
    if len(pts) < 5:
        return None
    minx, miny = pts[:, 0].min(), pts[:, 1].min()
    w = max(pts[:, 0].max() - minx, 1e-3)
    h = max(pts[:, 1].max() - miny, 1e-3)
    s = max(w, h)
    out = np.zeros((17, 2), dtype=np.float32)
    cx = (pts[:, 0].mean() - minx) / s
    cy = (pts[:, 1].mean() - miny) / s
    # horizontal centering offset so the figure sits mid-panel
    xoff = 0.5 - cx
    for i in range(17):
        if kp[i, 2] >= conf:
            out[i, 0] = (kp[i, 0] - minx) / s + xoff
            out[i, 1] = (kp[i, 1] - miny) / s
        else:
            out[i, 0] = 0.5
            out[i, 1] = cy
    return out


def _mirror_to_left(kp: np.ndarray, conf: float) -> np.ndarray:
    """For the neck stretch, ensure the RAISED hand is the viewer-left one so the
    coach demo is consistent regardless of which side the sample subject used."""
    leg = body_scale(kp, DEFAULT_RULE_CFG)
    if leg is None:
        return kp
    # which wrist is higher (smaller y) = raised
    lw, rw = kp[L_WRI], kp[R_WRI]
    if lw[2] >= conf and rw[2] >= conf and rw[1] < lw[1]:
        # raised hand is the right one -> mirror horizontally
        cx = float(np.mean(kp[kp[:, 2] >= conf, 0]))
        m = kp.copy()
        m[:, 0] = 2 * cx - kp[:, 0]
        # swap L/R pairs to keep skeleton edges valid
        for a, b in ((1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12), (13, 14), (15, 16)):
            m[[a, b]] = m[[b, a]]
        return m
    return kp


def main() -> int:
    ap = argparse.ArgumentParser(description="Calibrate coach poses from clips")
    ap.add_argument("-m", "--model", default=str(_DEFAULT_MODEL))
    ap.add_argument("--out", default=str(_HERE / "coach_poses.json"))
    ap.add_argument("--sample-dir", default=str(_SAMPLE_DIR))
    args = ap.parse_args()

    if not Path(args.model).is_file():
        print(f"[calibrate] model not found: {args.model} — keeping fallback poses")
        return 0

    from dx_engine import InferenceEngine
    ie = InferenceEngine(args.model)
    info = ie.get_input_tensors_info()[0]
    shape = info["shape"]
    if len(shape) >= 4 and shape[-1] in (1, 3, 4):
        ih, iw = shape[1], shape[2]
    else:
        ih, iw = shape[2], shape[3]
    pre = LetterboxPreprocessor(iw, ih)
    post = YOLOv8PosePostprocessor(iw, ih, {"score_threshold": 0.4, "nms_threshold": 0.45})
    conf = DEFAULT_RULE_CFG["kpt_conf"]
    recog = {"overhead": is_overhead_reach, "fold": is_forward_fold, "neck": is_neck_stretch}

    targets = {}
    neutrals = []
    for key in ("overhead", "fold", "neck"):
        clip = Path(args.sample_dir) / CLIPS[key]
        cap = cv2.VideoCapture(str(clip))
        matched, scanned = [], 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            scanned += 1
            tensor, ctx = pre.process(frame)
            outs = ie.run([tensor])
            pose = _largest(post.process(outs, ctx))
            if pose is None or len(pose.keypoints) < 17:
                continue
            kp = _result_to_kp(pose)
            if recog[key](kp, DEFAULT_RULE_CFG):
                if key == "neck":
                    kp = _mirror_to_left(kp, conf)
                norm = _normalize(kp, conf)
                if norm is not None:
                    matched.append(norm)
            elif not any(recog[k](kp, DEFAULT_RULE_CFG) for k in recog):
                norm = _normalize(kp, conf)
                if norm is not None:
                    neutrals.append(norm)
        cap.release()
        if matched:
            targets[key] = np.median(np.stack(matched), axis=0).tolist()
            print(f"[calibrate] {key}: {len(matched)}/{scanned} matching frames -> target derived")
        else:
            print(f"[calibrate] {key}: 0 matching frames -> keeping fallback")

    out_path = Path(args.out)
    data = json.loads(out_path.read_text()) if out_path.is_file() else {}
    data.setdefault("targets", {})
    data["targets"].update(targets)
    if neutrals:
        data["neutral"] = np.median(np.stack(neutrals), axis=0).tolist()
        print(f"[calibrate] neutral: {len(neutrals)} standing frames -> derived")
    data["source"] = "clip-calibrated" if targets else data.get("source", "fallback-hand-derived")
    out_path.write_text(json.dumps(data, indent=2))
    print(f"[calibrate] wrote {out_path} (source={data['source']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
