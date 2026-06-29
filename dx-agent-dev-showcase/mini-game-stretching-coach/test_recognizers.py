#!/usr/bin/env python3
"""Pure-logic unit tests for the stretch pose recognizers (no NPU needed).

Builds synthetic COCO-17 keypoints (image coords, y DOWN) for a standing person
and the three target stretches, and asserts each recognizer fires only on its
own pose. Run: python test_recognizers.py
"""
import sys
from stretch_coach import (
    recognize_overhead, recognize_forward_fold, recognize_neck_stretch,
    NOSE, L_EYE, R_EYE, L_EAR, R_EAR, L_SHO, R_SHO, L_ELB, R_ELB,
    L_WRI, R_WRI, L_HIP, R_HIP, L_KNE, R_KNE, L_ANK, R_ANK,
)

CFG = {
    "keypoint_confidence_threshold": 0.3,
    "overhead_wrist_above_nose_ratio": 0.15,
    "fold_torso_collapse_ratio": 0.45,
    "fold_head_drop_ratio": -0.1,
    "neck_hand_horizontal_ratio": 0.95,
    "neck_hand_top_ratio": 0.6,
}


def make_kps(coords):
    """coords: dict idx->(x,y). Returns 17 (x,y,conf) triplets, conf=0 if absent."""
    out = []
    for i in range(17):
        if i in coords:
            x, y = coords[i]
            out.append((float(x), float(y), 0.9))
        else:
            out.append((0.0, 0.0, 0.0))
    return out


def standing():
    # Upright person, arms hanging. Shoulders width 100, hips below shoulders.
    return make_kps({
        NOSE: (200, 60), L_EYE: (190, 55), R_EYE: (210, 55),
        L_SHO: (150, 120), R_SHO: (250, 120),
        L_ELB: (145, 200), R_ELB: (255, 200),
        L_WRI: (140, 280), R_WRI: (260, 280),
        L_HIP: (165, 300), R_HIP: (235, 300),
        L_KNE: (165, 420), R_KNE: (235, 420),
        L_ANK: (165, 540), R_ANK: (235, 540),
    })


def overhead():
    k = standing()
    # Raise both wrists/elbows well above the nose (smaller y).
    k[L_ELB] = (160, 70, 0.9); k[R_ELB] = (240, 70, 0.9)
    k[L_WRI] = (170, 10, 0.9); k[R_WRI] = (230, 10, 0.9)
    return k


def forward_fold():
    # Back horizontal: shoulders dropped to near hip level, head down near hips.
    return make_kps({
        NOSE: (200, 300),
        L_SHO: (160, 280), R_SHO: (240, 280),
        L_ELB: (165, 330), R_ELB: (235, 330),
        L_WRI: (170, 380), R_WRI: (230, 380),
        L_HIP: (165, 300), R_HIP: (235, 300),
        L_KNE: (165, 430), R_KNE: (235, 430),
        L_ANK: (165, 540), R_ANK: (235, 540),
    })


def neck_stretch():
    k = standing()
    # Right hand raised beside the head (~head height, near nose x); left hangs.
    k[R_ELB] = (250, 90, 0.9)
    k[R_WRI] = (215, 55, 0.9)   # beside head, y just above shoulders, x near nose
    # left wrist stays low (hanging) from standing()
    return k


def check(name, kps, expect_overhead, expect_fold, expect_neck):
    o = recognize_overhead(kps, CFG)
    f = recognize_forward_fold(kps, CFG)
    n = recognize_neck_stretch(kps, CFG)
    ok = (o == expect_overhead) and (f == expect_fold) and (n == expect_neck)
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name:14s} overhead={o} fold={f} neck={n} "
          f"(expected {expect_overhead}/{expect_fold}/{expect_neck})")
    return ok


def main():
    results = [
        check("standing", standing(), False, False, False),
        check("overhead", overhead(), True, False, False),
        check("forward_fold", forward_fold(), False, True, False),
        check("neck_stretch", neck_stretch(), False, False, True),
    ]
    if all(results):
        print("RESULT: PASS — all recognizers behave correctly")
        return 0
    print("RESULT: FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
