#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
End-to-end game-logic verification on the real NPU pipeline.

1. Per-clip recognition separation: for each stretch's sample clip, the matching
   stretch must be the DOMINANT one (fires on the most frames), proving the
   recognizers are well separated.
2. End-to-end: drive StretchGameVisualizer over stretching_demo.mp4 (all three
   stretches in sequence) and assert it reaches CLEAR! (stage_idx advanced 0->3).

Exit 0 + "RESULT: PASS" only if all checks pass; otherwise exit 1 + "RESULT: FAIL".
"""

import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent


def _bootstrap():
    d = _HERE
    for _ in range(8):
        if (d / "src" / "python_example" / "common").is_dir():
            pe = d / "src" / "python_example"
            for p in (str(pe), str(_HERE)):
                if p not in sys.path:
                    sys.path.insert(0, p)
            return d / "dx_app" if (d / "dx_app").is_dir() else d
        d = d.parent
    raise RuntimeError("cannot find src/python_example/common")


_bootstrap()

import cv2  # noqa: E402
import json  # noqa: E402
from common.processors import LetterboxPreprocessor, YOLOv8PosePostprocessor  # noqa: E402
from stretch_pose_rules import (  # noqa: E402
    is_overhead_reach, is_forward_fold, is_neck_stretch, DEFAULT_RULE_CFG,
)

_DXAPP = _HERE.parents[1]  # session = dx_app/dx-agentic-dev/<sid> -> parents[1] = dx_app
MODEL = _DXAPP / "assets" / "models" / "yolo26n-pose.dxnn"
SAMPLE = _DXAPP / "sample"
CLIPS = {
    "overhead": "stretching_extending_both_arms.mp4",
    "fold": "stretching_bending_at_the_waist.mp4",
    "neck": "stretching_pulling_the_head.mp4",
}
RECOG = {"overhead": is_overhead_reach, "fold": is_forward_fold, "neck": is_neck_stretch}


def _kp(pose):
    a = np.zeros((17, 3), dtype=np.float32)
    for i, k in enumerate(pose.keypoints[:17]):
        a[i] = (k.x, k.y, k.confidence)
    return a


def _largest(results):
    ppl = [r for r in results if r.keypoints and len(r.keypoints) >= 17]
    return max(ppl, key=lambda r: (r.box[2]-r.box[0])*(r.box[3]-r.box[1])) if ppl else None


def main():
    if not MODEL.is_file():
        print(f"ONNX/DXNN inference failed: model missing {MODEL}")
        print("RESULT: FAIL")
        return 1
    from dx_engine import InferenceEngine
    ie = InferenceEngine(str(MODEL))
    shp = ie.get_input_tensors_info()[0]["shape"]
    ih, iw = (shp[1], shp[2]) if shp[-1] in (1, 3, 4) else (shp[2], shp[3])
    pre = LetterboxPreprocessor(iw, ih)
    post = YOLOv8PosePostprocessor(iw, ih, {"score_threshold": 0.4, "nms_threshold": 0.45})

    ok = True

    # ---- 1. per-clip separation ----
    print("== per-clip recognizer separation ==")
    for key, fname in CLIPS.items():
        cap = cv2.VideoCapture(str(SAMPLE / fname))
        counts = {k: 0 for k in RECOG}
        n = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            n += 1
            t, ctx = pre.process(frame)
            pose = _largest(post.process(ie.run([t]), ctx))
            if pose is None:
                continue
            kp = _kp(pose)
            for k, fn in RECOG.items():
                if fn(kp, DEFAULT_RULE_CFG):
                    counts[k] += 1
        cap.release()
        dominant = max(counts, key=counts.get)
        share = counts[key] / max(1, n)
        verdict = "OK" if (dominant == key and counts[key] > 0) else "BAD"
        if verdict == "BAD":
            ok = False
        print(f"  {key:9s} clip: counts={counts} dominant={dominant} "
              f"({share*100:.1f}% own) -> {verdict}")

    # ---- 2. end-to-end CLEAR! on the combined demo ----
    print("== end-to-end (stretching_demo.mp4) ==")
    demo = SAMPLE / "stretching_demo.mp4"
    if demo.is_file():
        cfg = json.loads((_HERE / "config.json").read_text())
        coach = json.loads((_HERE / "coach_poses.json").read_text())
        from game_visualizer import StretchGameVisualizer
        viz = StretchGameVisualizer(cfg, coach)
        cap = cv2.VideoCapture(str(demo))
        frames = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames += 1
            t, ctx = pre.process(frame)
            results = post.process(ie.run([t]), ctx)
            viz.visualize(frame, results)
        cap.release()
        print(f"  processed {frames} frames; final stage_idx={viz.stage_idx} "
              f"cleared={viz.cleared}")
        if not viz.cleared:
            ok = False
            print("  end-to-end did NOT reach CLEAR!")
    else:
        print(f"  SKIP: {demo} not found (per-clip checks still apply)")

    print("RESULT: PASS" if ok else "RESULT: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
