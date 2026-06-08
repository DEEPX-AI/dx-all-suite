#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Build-time calibration: derive coach pose templates from the sample clips.

For each stage's sample clip we run pose inference, keep the frames where the
classifier fires for that stage, normalize the dominant skeleton into canonical
figure space (origin = mid-hip, unit = leg scale, X mirrored so the *raised*
hand is consistent), and take the per-coordinate median. The result is written
to ``pose_templates.json`` and consumed by the coach avatar at runtime.

This is an OFFLINE build tool, not the inference app: it uses InferenceEngine
directly (the SyncRunner/IFactory rule governs the *app*, not calibration).

Usage:
    python calibrate_templates.py -m <model.dxnn> [--sample-dir <dir>]
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import cv2


def _setup_paths():
    here = Path(__file__).resolve().parent
    pe_root = None
    for parent in [here, *here.parents]:
        if (parent / "src" / "python_example" / "common").is_dir():
            pe_root = parent / "src" / "python_example"
            break
    if pe_root is None:
        raise RuntimeError("Could not locate src/python_example/common")
    for p in (str(here), str(pe_root)):
        if p not in sys.path:
            sys.path.insert(0, p)
    return pe_root


PE_ROOT = _setup_paths()

from dx_engine import InferenceEngine                       # noqa: E402
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor  # noqa: E402
from stretch_game_engine import StretchClassifier           # noqa: E402
from coach_avatar import (                                   # noqa: E402
    NEUTRAL_TEMPLATE, FALLBACK_TEMPLATES, STAGE_KEYS,
    NOSE, L_SH, R_SH, L_WR, R_WR, L_HIP, R_HIP, L_ANKLE, R_ANKLE,
)

STAGE_CLIP = {
    "overhead": "stretching_extending_both_arms.mp4",
    "fold": "stretching_bending_at_the_waist.mp4",
    "neck": "stretching_pulling_the_head.mp4",
}

MIN_MATCH_FRAMES = 5


def _normalize_skeleton(kps, clf: StretchClassifier, key: str):
    """Return a (17,2) canonical template from a detected skeleton, or None."""
    pts = np.zeros((17, 2), dtype=np.float32)
    conf = np.zeros(17, dtype=np.float32)
    for i, kp in enumerate(kps[:17]):
        pts[i] = (kp.x, kp.y)
        conf[i] = kp.confidence

    # Need hips for the origin and a vertical scale.
    if conf[L_HIP] < clf.kpt_conf or conf[R_HIP] < clf.kpt_conf:
        return None
    mid_hip = (pts[L_HIP] + pts[R_HIP]) * 0.5
    scale = clf.body_scale(kps)
    if scale <= 1e-3:
        return None

    norm = (pts - mid_hip) / scale   # origin mid-hip, +y down, unit leg

    # Mirror X so the *raised* hand is always on the same side (right, +x)
    # for the neck stretch — keeps the coach template consistent.
    if key == "neck":
        msh_y = (norm[L_SH, 1] + norm[R_SH, 1]) * 0.5
        l_up = conf[L_WR] >= clf.kpt_conf and norm[L_WR, 1] < msh_y
        if l_up:
            norm[:, 0] = -norm[:, 0]   # flip so raised hand -> +x side
    # Fill any low-confidence joints from the neutral template so the figure
    # stays complete and drawable.
    for i in range(17):
        if conf[i] < clf.kpt_conf:
            norm[i] = NEUTRAL_TEMPLATE[i]
    return norm


def calibrate_clip(ie, pre, post, clf, clip_path, key):
    cap = cv2.VideoCapture(clip_path)
    if not cap.isOpened():
        print(f"  [WARN] cannot open {clip_path}")
        return None, 0
    collected = []
    frames = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames += 1
        tensor, ctx = pre.process(frame)
        outputs = ie.run([tensor])
        results = post.process(outputs, ctx)
        # dominant person
        best, area = None, -1
        for r in results:
            if not r.keypoints or not r.box:
                continue
            a = abs((r.box[2] - r.box[0]) * (r.box[3] - r.box[1]))
            if a > area:
                best, area = r, a
        if best is None:
            continue
        scale = clf.body_scale(best.keypoints, best.box)
        if key in clf.classify(best.keypoints, scale):
            norm = _normalize_skeleton(best.keypoints, clf, key)
            if norm is not None:
                collected.append(norm)
    cap.release()
    if len(collected) < MIN_MATCH_FRAMES:
        return None, len(collected)
    stack = np.stack(collected, axis=0)
    template = np.median(stack, axis=0).astype(np.float32)
    return template, len(collected)


def main():
    ap = argparse.ArgumentParser(description="Derive coach templates from clips")
    ap.add_argument("--model", "-m", required=True)
    ap.add_argument("--sample-dir", default=str(PE_ROOT.parent.parent / "sample"))
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "pose_templates.json"))
    ap.add_argument("--config", default=str(Path(__file__).resolve().parent / "config.json"))
    args = ap.parse_args()

    config = {}
    if os.path.isfile(args.config):
        config = json.load(open(args.config))
    clf = StretchClassifier(config)

    ie = InferenceEngine(args.model)
    ti = ie.get_input_tensors_info()[0]["shape"]
    if ti[-1] in (1, 3, 4):
        ih, iw = ti[1], ti[2]
    else:
        ih, iw = ti[2], ti[3]
    pre = LetterboxPreprocessor(iw, ih)
    post = YOLOv8PosePostprocessor(iw, ih, config)

    out = {"neutral": NEUTRAL_TEMPLATE.tolist()}
    for key in STAGE_KEYS:
        clip = os.path.join(args.sample_dir, STAGE_CLIP[key])
        print(f"[{key}] {clip}")
        tmpl, n = (None, 0)
        if os.path.isfile(clip):
            tmpl, n = calibrate_clip(ie, pre, post, clf, clip, key)
        if tmpl is None:
            print(f"  -> only {n} matching frames (<{MIN_MATCH_FRAMES}); "
                  f"using hand-authored fallback")
            tmpl = FALLBACK_TEMPLATES[key]
        else:
            print(f"  -> derived from {n} matching frames")
        out[key] = np.asarray(tmpl, dtype=np.float32).tolist()

    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    keys = [k for k in STAGE_KEYS if k in out]
    print(f"WROTE {args.out} with stages: {keys}")
    assert all(k in out for k in STAGE_KEYS), "missing a stage template"
    print("RESULT: PASS")


if __name__ == "__main__":
    main()
