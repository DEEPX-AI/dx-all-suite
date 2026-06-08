#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Unit tests for the stretch-pose recognition module.

These tests use *synthetic* COCO-17 keypoint arrays (shape (17, 3): x, y, conf)
to assert that each stretch archetype triggers ONLY its own recognizer and not
the other two. No NPU / model needed — pure geometry.

Run:
    pytest test_stretch_rules.py -v
"""

import numpy as np
import pytest

from stretch_pose_rules import (
    is_overhead_reach, is_forward_fold, is_neck_stretch,
    body_scale, StretchTracker, DEFAULT_RULE_CFG,
    NOSE, L_EYE, R_EYE, L_EAR, R_EAR, L_SHO, R_SHO,
    L_ELB, R_ELB, L_WRI, R_WRI, L_HIP, R_HIP,
    L_KNEE, R_KNEE, L_ANK, R_ANK,
)

CFG = DEFAULT_RULE_CFG


def _neutral():
    """A standing neutral skeleton in image coords (y grows downward). leg ~ 260px."""
    kp = np.zeros((17, 3), dtype=np.float32)
    kp[NOSE]  = (300, 100, 1)
    kp[L_EYE] = (310,  90, 1)
    kp[R_EYE] = (290,  90, 1)
    kp[L_EAR] = (320,  95, 1)
    kp[R_EAR] = (280,  95, 1)
    kp[L_SHO] = (340, 160, 1)
    kp[R_SHO] = (260, 160, 1)
    kp[L_ELB] = (360, 230, 1)
    kp[R_ELB] = (240, 230, 1)
    kp[L_WRI] = (370, 300, 1)
    kp[R_WRI] = (230, 300, 1)
    kp[L_HIP] = (330, 320, 1)
    kp[R_HIP] = (270, 320, 1)
    kp[L_KNEE] = (335, 450, 1)
    kp[R_KNEE] = (265, 450, 1)
    kp[L_ANK] = (338, 580, 1)
    kp[R_ANK] = (262, 580, 1)
    return kp


def _overhead():
    kp = _neutral()
    # both arms raised straight overhead, wrists above the nose
    kp[L_ELB] = (335,  90, 1)
    kp[R_ELB] = (265,  90, 1)
    kp[L_WRI] = (330,  40, 1)
    kp[R_WRI] = (270,  40, 1)
    return kp


def _fold():
    kp = _neutral()
    # torso folded forward: shoulders drop to ~hip level, head drops, hands near feet
    kp[NOSE]  = (300, 350, 1)
    kp[L_EYE] = (308, 345, 1)
    kp[R_EYE] = (292, 345, 1)
    kp[L_EAR] = (318, 348, 1)
    kp[R_EAR] = (282, 348, 1)
    kp[L_SHO] = (340, 300, 1)
    kp[R_SHO] = (260, 300, 1)
    kp[L_ELB] = (345, 320, 1)
    kp[R_ELB] = (255, 320, 1)
    kp[L_WRI] = (345, 330, 1)
    kp[R_WRI] = (255, 330, 1)
    # legs stay vertical (the whole point of leg-based scale)
    return kp


def _neck():
    kp = _neutral()
    # exactly one hand raised beside the head (left), other hand stays low
    kp[L_ELB] = (300, 130, 1)
    kp[L_WRI] = (322,  90, 1)   # near the left ear (320, 95)
    return kp


# ---- archetype separation ----------------------------------------------

def test_overhead_fires_only_for_overhead():
    assert is_overhead_reach(_overhead(), CFG) is True
    assert is_overhead_reach(_fold(), CFG) is False
    assert is_overhead_reach(_neck(), CFG) is False
    assert is_overhead_reach(_neutral(), CFG) is False


def test_fold_fires_only_for_fold():
    assert is_forward_fold(_fold(), CFG) is True
    assert is_forward_fold(_overhead(), CFG) is False
    assert is_forward_fold(_neck(), CFG) is False
    assert is_forward_fold(_neutral(), CFG) is False


def test_neck_fires_only_for_neck():
    assert is_neck_stretch(_neck(), CFG) is True
    assert is_neck_stretch(_overhead(), CFG) is False
    assert is_neck_stretch(_fold(), CFG) is False
    assert is_neck_stretch(_neutral(), CFG) is False


def test_body_scale_is_leg_based_and_stable_in_fold():
    # leg scale must stay ~constant between standing and folded (legs vertical)
    s_stand = body_scale(_neutral(), CFG)
    s_fold = body_scale(_fold(), CFG)
    assert s_stand is not None and s_fold is not None
    assert abs(s_stand - s_fold) / s_stand < 0.05


def test_body_scale_none_when_no_lower_body():
    kp = _neutral()
    kp[[L_HIP, R_HIP, L_KNEE, R_KNEE, L_ANK, R_ANK], 2] = 0.0  # hide lower body
    # with shoulders still visible, falls back to |hip-shoulder|? hips hidden too.
    assert body_scale(kp, CFG) is None


# ---- hold tracker -------------------------------------------------------

def test_tracker_completes_after_hold_frames():
    t = StretchTracker(hold_frames=5, miss_tolerance=2)
    for _ in range(4):
        t.update(True)
    assert not t.complete
    t.update(True)
    assert t.complete
    assert t.progress == pytest.approx(1.0)


def test_tracker_tolerates_brief_misses_but_resets_on_long_gap():
    t = StretchTracker(hold_frames=10, miss_tolerance=2)
    for _ in range(5):
        t.update(True)
    t.update(False)            # within tolerance
    t.update(False)            # within tolerance
    assert t.count == 5
    t.update(False)            # exceeds tolerance -> reset
    assert t.count == 0


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
