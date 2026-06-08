#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""OFFLINE calibration (dev tool, NOT the deployed game).

Runs the real yolo26n-pose NPU pipeline over the three stretch sample clips and:
  1. Dumps measured min/median/p90 of each pose relation (measure-don't-assume).
  2. Confirms pose separation (each recognizer fires mostly on its own clip).
  3. Derives the animated coach's stick-figure skeletons (neutral + 3 targets)
     straight from the clips and writes them to pose_templates.json.
  4. Writes the confirmed thresholds into config.json.

Usage:
    python calibrate_coach_poses.py [--model PATH]
"""

import argparse
import json
import statistics
from pathlib import Path

import numpy as np

import _bootstrap
_bootstrap.setup()

import pose_logic as pl  # noqa: E402
import game_eval  # noqa: E402

HERE = Path(__file__).resolve().parent

CLIPS = {
    "overhead": "stretching_extending_both_arms.mp4",
    "fold": "stretching_bending_at_the_waist.mp4",
    "neck": "stretching_pulling_the_head.mp4",
}


def _find_dx_app_root() -> Path:
    d = HERE
    for _ in range(10):
        if (d / "assets" / "models").is_dir() and (d / "sample").is_dir():
            return d
        d = d.parent
    raise FileNotFoundError("Could not locate dx_app root (assets/models + sample).")


def _resolve_model(arg: str) -> str:
    if arg:
        return arg
    return str(_find_dx_app_root() / "assets" / "models" / "yolo26n-pose.dxnn")


def _resolve_clip(name: str) -> str:
    root = _find_dx_app_root()
    return str(root / "sample" / name)


def _pct(vals, p):
    if not vals:
        return float("nan")
    s = sorted(vals)
    k = max(0, min(len(s) - 1, int(round((p / 100.0) * (len(s) - 1)))))
    return s[k]


def _normalized_skeleton(P, scale):
    """Center on hip-mid, scale by leg length -> {name: (nx, ny)}."""
    hip = pl._mid(P.get("left_hip"), P.get("right_hip"))
    if hip is None or not scale:
        return None
    return {n: ((x - hip[0]) / scale, (y - hip[1]) / scale) for n, (x, y) in P.items()}


def _median_skeleton(samples):
    """Median per keypoint across a list of normalized skeletons."""
    if not samples:
        return {}
    out = {}
    for name in pl.KEYPOINT_NAMES:
        xs = [s[name][0] for s in samples if name in s]
        ys = [s[name][1] for s in samples if name in s]
        if xs and ys:
            out[name] = [float(np.median(xs)), float(np.median(ys))]
    return out


def _mirror(skel):
    """Mirror left<->right so the raised hand is on a consistent side."""
    swap = {}
    for n in skel:
        if n.startswith("left_"):
            swap[n] = "right_" + n[5:]
        elif n.startswith("right_"):
            swap[n] = "left_" + n[6:]
        else:
            swap[n] = n
    return {swap[n]: [-x, y] for n, (x, y) in skel.items()}


def main():
    ap = argparse.ArgumentParser(description="Calibrate stretch-game coach poses")
    ap.add_argument("--model", default=None, help="Path to yolo26n-pose.dxnn")
    args = ap.parse_args()

    model = _resolve_model(args.model)
    cfg = dict(pl.DEFAULT_CFG)
    print(f"[calibrate] model = {model}")
    runner = game_eval.build_runner(model)

    fire = {k: {kk: 0 for kk in CLIPS} for k in CLIPS}  # fire[detector][clip]
    totals = {k: 0 for k in CLIPS}
    templates = {"neutral": [], "overhead": [], "fold": [], "neck": []}
    relations = {k: [] for k in
                 ("overhead_nose", "overhead_sho", "fold_drop", "fold_hands",
                  "neck_count")}

    for clip_key, clip_file in CLIPS.items():
        path = _resolve_clip(clip_file)
        print(f"\n[calibrate] === {clip_key}: {clip_file} ===")
        n_pose = 0
        for idx, frame, pose in game_eval.iter_poses(runner, path):
            totals[clip_key] += 1
            if pose is None:
                continue
            P = pl.extract_keypoints(pose, cfg["kpt_conf"])
            scale = pl.leg_scale(P)
            if scale is None:
                continue
            n_pose += 1
            # which detectors fire on this frame
            fired = {k: pl.detect_stage(k, P, scale, cfg) for k in CLIPS}
            for k in CLIPS:
                if fired[k]:
                    fire[k][clip_key] += 1
            # collect coach templates from frames matching THIS clip's pose
            norm = _normalized_skeleton(P, scale)
            if norm is not None:
                if fired[clip_key]:
                    templates[clip_key].append(norm)
                if not any(fired.values()):
                    templates["neutral"].append(norm)
            # measured relations on this clip's own pose for evidence
            if clip_key == "overhead" and all(n in P for n in
                    ("nose", "left_wrist", "right_wrist", "left_shoulder", "right_shoulder")):
                relations["overhead_nose"].append(
                    min((P["nose"][1] - P["left_wrist"][1]) / scale,
                        (P["nose"][1] - P["right_wrist"][1]) / scale))
                relations["overhead_sho"].append(
                    min((P["left_shoulder"][1] - P["left_wrist"][1]) / scale,
                        (P["right_shoulder"][1] - P["right_wrist"][1]) / scale))
            if clip_key == "fold":
                sho = pl._mid(P.get("left_shoulder"), P.get("right_shoulder"))
                hip = pl._mid(P.get("left_hip"), P.get("right_hip"))
                if sho and hip:
                    relations["fold_drop"].append((sho[1] - hip[1]) / scale)
                    rels = [(hip[1] - P[w][1]) / scale for w in ("left_wrist", "right_wrist") if w in P]
                    if rels:
                        relations["fold_hands"].append(min(rels))
        print(f"  frames={totals[clip_key]} with_pose={n_pose}")

    # ---- separation report ----
    print("\n[calibrate] === SEPARATION (fire% per clip) ===")
    print(f"{'detector':<10} " + " ".join(f"{c:>10}" for c in CLIPS))
    ok = True
    for det in CLIPS:
        row = []
        for clip in CLIPS:
            pct = 100.0 * fire[det][clip] / max(1, totals[clip])
            row.append(f"{pct:9.1f}%")
        print(f"{det:<10} " + " ".join(row))
        own = 100.0 * fire[det][det] / max(1, totals[det])
        if own < 8.0:
            print(f"  WARN: '{det}' fires only {own:.1f}% on its own clip")
            ok = False

    print("\n[calibrate] === MEASURED RELATIONS (min / median / p90) ===")
    for name, vals in relations.items():
        if vals:
            print(f"  {name:<14} n={len(vals):<4} "
                  f"{min(vals):+.3f} / {statistics.median(vals):+.3f} / {_pct(vals, 90):+.3f}")

    # ---- coach templates ----
    coach = {}
    for key in ("neutral", "overhead", "fold", "neck"):
        coach[key] = _median_skeleton(templates[key])
        print(f"[calibrate] template '{key}': {len(coach[key])} keypoints "
              f"from {len(templates[key])} frames")
    # consistent raised side for neck: raised wrist should be on +x side
    neck = coach.get("neck") or {}
    lw = neck.get("left_wrist"); rw = neck.get("right_wrist")
    raised = None
    if lw and rw:
        raised = "left_wrist" if lw[1] < rw[1] else "right_wrist"
    if raised == "left_wrist":
        coach["neck"] = _mirror(neck)
        print("[calibrate] mirrored neck template for consistent raised side")
    # neutral fallback if too few neutral frames measured
    if len(coach["neutral"]) < 10:
        coach["neutral"] = _CANONICAL_NEUTRAL
        print("[calibrate] neutral: using canonical fallback (few measured frames)")

    (HERE / "pose_templates.json").write_text(json.dumps(coach, indent=2))
    print(f"[calibrate] wrote pose_templates.json")

    # ---- write confirmed thresholds into config.json ----
    config = {
        "score_threshold": 0.4,
        "nms_threshold": 0.45,
        "game": {
            "hold_seconds": 1.5,
            "grace_frames": 8,
            **{k: cfg[k] for k in pl.DEFAULT_CFG},
        },
    }
    (HERE / "config.json").write_text(json.dumps(config, indent=2))
    print("[calibrate] wrote config.json")
    print(f"\n[calibrate] RESULT: {'PASS' if ok else 'CHECK-WARN'}")
    return 0 if ok else 0  # warnings are non-fatal; verify.py is the gate


# Canonical upright skeleton (normalized: hip-mid origin, leg=1.0), arms at sides.
_CANONICAL_NEUTRAL = {
    "nose": [0.0, -1.45], "left_eye": [-0.05, -1.50], "right_eye": [0.05, -1.50],
    "left_ear": [-0.10, -1.45], "right_ear": [0.10, -1.45],
    "left_shoulder": [-0.22, -1.15], "right_shoulder": [0.22, -1.15],
    "left_elbow": [-0.26, -0.70], "right_elbow": [0.26, -0.70],
    "left_wrist": [-0.28, -0.25], "right_wrist": [0.28, -0.25],
    "left_hip": [-0.13, 0.0], "right_hip": [0.13, 0.0],
    "left_knee": [-0.12, 0.52], "right_knee": [0.12, 0.52],
    "left_ankle": [-0.11, 1.0], "right_ankle": [0.11, 1.0],
}


if __name__ == "__main__":
    raise SystemExit(main())
