#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""Unit tests for the NPU-free stretch-game pose logic.

Run: pytest test_pose_logic.py -v
These tests need NO model/NPU — they validate the recognizers and the state
machine against synthetic COCO-17 keypoint layouts.
"""

import pose_logic as pl

CFG = dict(pl.DEFAULT_CFG)


def _standing() -> pl.PoseMap:
    """A plausible upright person at ~1280x720 scale (legs ~270 px)."""
    return {
        "nose": (640, 150),
        "left_eye": (630, 142), "right_eye": (650, 142),
        "left_ear": (620, 150), "right_ear": (660, 150),
        "left_shoulder": (600, 220), "right_shoulder": (680, 220),
        "left_elbow": (590, 320), "right_elbow": (690, 320),
        "left_wrist": (585, 415), "right_wrist": (695, 415),
        "left_hip": (615, 420), "right_hip": (665, 420),
        "left_knee": (612, 560), "right_knee": (668, 560),
        "left_ankle": (610, 690), "right_ankle": (670, 690),
    }


def _overhead() -> pl.PoseMap:
    P = _standing()
    P["left_wrist"] = (605, 90)   # above nose (150) and shoulder (220)
    P["right_wrist"] = (675, 90)
    P["left_elbow"] = (600, 160)
    P["right_elbow"] = (680, 160)
    return P


def _fold() -> pl.PoseMap:
    P = _standing()
    # shoulders dropped toward hips (waist bend)
    P["left_shoulder"] = (610, 380); P["right_shoulder"] = (670, 380)
    # hands reaching down past the hips toward the feet
    P["left_wrist"] = (615, 500); P["right_wrist"] = (665, 500)
    P["left_elbow"] = (612, 440); P["right_elbow"] = (668, 440)
    return P


def _neck() -> pl.PoseMap:
    P = _standing()
    # right hand raised beside the head (near right ear), left hand stays down
    P["right_wrist"] = (662, 150); P["right_elbow"] = (690, 210)
    return P


def _scale(P):
    return pl.leg_scale(P)


def test_leg_scale_reasonable():
    s = pl.leg_scale(_standing())
    assert s is not None and 250 < s < 320


def test_overhead_fires_only_on_overhead():
    assert pl.detect_overhead(_overhead(), _scale(_overhead()), CFG) is True
    assert pl.detect_overhead(_standing(), _scale(_standing()), CFG) is False
    assert pl.detect_overhead(_fold(), _scale(_fold()), CFG) is False
    assert pl.detect_overhead(_neck(), _scale(_neck()), CFG) is False


def test_fold_fires_only_on_fold():
    assert pl.detect_fold(_fold(), _scale(_fold()), CFG) is True
    assert pl.detect_fold(_standing(), _scale(_standing()), CFG) is False
    assert pl.detect_fold(_overhead(), _scale(_overhead()), CFG) is False
    assert pl.detect_fold(_neck(), _scale(_neck()), CFG) is False


def test_neck_fires_only_on_neck():
    assert pl.detect_neck(_neck(), _scale(_neck()), CFG) is True
    assert pl.detect_neck(_standing(), _scale(_standing()), CFG) is False
    assert pl.detect_neck(_overhead(), _scale(_overhead()), CFG) is False  # both up
    assert pl.detect_neck(_fold(), _scale(_fold()), CFG) is False


def test_extract_respects_confidence():
    class _K:
        def __init__(self, x, y, c):
            self.x, self.y, self.confidence = x, y, c

    class _P:
        keypoints = [_K(i, i, 0.9 if i % 2 == 0 else 0.1) for i in range(17)]

    P = pl.extract_keypoints(_P(), conf_thr=0.3)
    # only even-index keypoints survive the 0.3 threshold
    assert "nose" in P and "left_eye" not in P


def test_state_machine_clears_after_hold_and_advances():
    g = pl.StretchGame(pl.STAGE_DEFS, hold_frames=5, grace=3)
    assert g.current_stage["key"] == "overhead" and g.stage_number == 1
    for _ in range(5):
        g.update(True)
    assert g.good_flash > 0 and g.current_stage["key"] == "fold"
    for _ in range(5):
        g.update(True)
    assert g.current_stage["key"] == "neck"
    for _ in range(5):
        g.update(True)
    assert g.cleared is True and g.current_stage is None and g.clear_flash > 0


def test_hold_resets_after_grace():
    g = pl.StretchGame(pl.STAGE_DEFS, hold_frames=10, grace=2)
    for _ in range(4):
        g.update(True)
    assert g.hold == 4
    for _ in range(3):  # exceed grace
        g.update(False)
    assert g.hold == 0 and g.current_stage["key"] == "overhead"
