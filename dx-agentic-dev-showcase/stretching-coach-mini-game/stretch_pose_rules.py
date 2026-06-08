#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Stretch-pose recognition from COCO-17 body keypoints.

Pure geometry — no model / NPU dependency — so it is unit-testable in isolation.
A "keypoints" argument is a numpy array of shape (17, 3): (x, y, confidence) in
*original image* pixel coordinates (y grows downward).

Design notes
------------
All thresholds are **scale-invariant**: every distance is normalized by a
**leg-based body scale** (hip->ankle). This matters because the forward-fold
pose collapses the torso's vertical extent toward zero in 2D projection, so a
torso-normalized (shoulder->hip) metric explodes and misfires. The legs stay
vertical during a waist bend, so a leg scale is stable across all three poses.
(Thresholds calibrated by measuring yolo26n-pose over the sample clips.)
"""

from typing import Optional, List
import numpy as np

# COCO-17 keypoint indices
NOSE = 0
L_EYE, R_EYE = 1, 2
L_EAR, R_EAR = 3, 4
L_SHO, R_SHO = 5, 6
L_ELB, R_ELB = 7, 8
L_WRI, R_WRI = 9, 10
L_HIP, R_HIP = 11, 12
L_KNEE, R_KNEE = 13, 14
L_ANK, R_ANK = 15, 16

# Default rule configuration (overridable via config.json["rules"]).
DEFAULT_RULE_CFG = {
    "kpt_conf": 0.3,            # minimum keypoint confidence to trust a point
    "overhead_nose_margin": 0.0,    # wrist must clear the nose by margin * leg
    "overhead_above_shoulder": 0.15,  # wrist must clear the shoulder by this * leg
    "fold_shoulder_hip_ratio": -0.30,  # (shoulder_y - hip_y)/leg above this => torso folded
    "fold_hands_below_hip": -0.15,  # (wrist_y - hip_y)/leg above this => hands dropped
    "neck_head_low": -0.35,     # lower bound of (nose_y - wrist_y)/leg for a head-height hand
    "neck_head_high": 1.0,      # upper bound (excludes a fully-overhead arm)
    "neck_lateral": 0.60,       # |wrist_x - ear_x|/leg below this => hand beside the head
}


def _conf(cfg) -> float:
    return float(cfg.get("kpt_conf", DEFAULT_RULE_CFG["kpt_conf"]))


def _valid(kp: np.ndarray, idx: int, conf: float) -> bool:
    return bool(kp[idx, 2] >= conf)


def _mean_y(kp: np.ndarray, idxs: List[int], conf: float) -> Optional[float]:
    ys = [kp[i, 1] for i in idxs if _valid(kp, i, conf)]
    return float(np.mean(ys)) if ys else None


def body_scale(kp: np.ndarray, cfg=DEFAULT_RULE_CFG) -> Optional[float]:
    """Leg-based body scale in pixels: hip->ankle, fallback hip->knee*1.9,
    fallback |hip - shoulder|. Returns None if no usable lower/upper body."""
    conf = _conf(cfg)
    legs: List[float] = []
    for hip, ank, knee in ((L_HIP, L_ANK, L_KNEE), (R_HIP, R_ANK, R_KNEE)):
        if _valid(kp, hip, conf) and _valid(kp, ank, conf):
            legs.append(abs(kp[ank, 1] - kp[hip, 1]))
        elif _valid(kp, hip, conf) and _valid(kp, knee, conf):
            legs.append(abs(kp[knee, 1] - kp[hip, 1]) * 1.9)
    if legs:
        s = max(legs)
        if s > 1e-3:
            return float(s)
    # fallback: torso height (only when legs are unavailable)
    torso: List[float] = []
    for hip, sho in ((L_HIP, L_SHO), (R_HIP, R_SHO)):
        if _valid(kp, hip, conf) and _valid(kp, sho, conf):
            torso.append(abs(kp[hip, 1] - kp[sho, 1]))
    if torso:
        s = max(torso)
        if s > 1e-3:
            return float(s)
    return None


def is_overhead_reach(kp: np.ndarray, cfg=DEFAULT_RULE_CFG) -> bool:
    """Both wrists raised clearly above the head (above nose and above shoulders)."""
    leg = body_scale(kp, cfg)
    if leg is None or not _valid(kp, NOSE, _conf(cfg)):
        return False
    conf = _conf(cfg)
    margin = cfg.get("overhead_nose_margin", DEFAULT_RULE_CFG["overhead_nose_margin"])
    above_sho = cfg.get("overhead_above_shoulder", DEFAULT_RULE_CFG["overhead_above_shoulder"])
    for wri, sho in ((L_WRI, L_SHO), (R_WRI, R_SHO)):
        if not (_valid(kp, wri, conf) and _valid(kp, sho, conf)):
            return False
        if (kp[NOSE, 1] - kp[wri, 1]) / leg < margin:
            return False
        if (kp[sho, 1] - kp[wri, 1]) / leg < above_sho:
            return False
    return True


def is_forward_fold(kp: np.ndarray, cfg=DEFAULT_RULE_CFG) -> bool:
    """Torso folded at the waist: shoulders dropped toward the hips and hands
    lowered toward/below the hips. Leg-normalized for stability."""
    leg = body_scale(kp, cfg)
    if leg is None:
        return False
    conf = _conf(cfg)
    sho_y = _mean_y(kp, [L_SHO, R_SHO], conf)
    hip_y = _mean_y(kp, [L_HIP, R_HIP], conf)
    wri_y = _mean_y(kp, [L_WRI, R_WRI], conf)
    if sho_y is None or hip_y is None or wri_y is None:
        return False
    fold_ratio = cfg.get("fold_shoulder_hip_ratio", DEFAULT_RULE_CFG["fold_shoulder_hip_ratio"])
    hands_below = cfg.get("fold_hands_below_hip", DEFAULT_RULE_CFG["fold_hands_below_hip"])
    torso_folded = (sho_y - hip_y) / leg > fold_ratio
    hands_dropped = (wri_y - hip_y) / leg > hands_below
    return bool(torso_folded and hands_dropped)


def is_neck_stretch(kp: np.ndarray, cfg=DEFAULT_RULE_CFG) -> bool:
    """Exactly one hand raised beside the head (head-height + laterally close to
    the ear); the other hand stays low."""
    leg = body_scale(kp, cfg)
    if leg is None or not _valid(kp, NOSE, _conf(cfg)):
        return False
    conf = _conf(cfg)
    head_lo = cfg.get("neck_head_low", DEFAULT_RULE_CFG["neck_head_low"])
    head_hi = cfg.get("neck_head_high", DEFAULT_RULE_CFG["neck_head_high"])
    lat = cfg.get("neck_lateral", DEFAULT_RULE_CFG["neck_lateral"])
    raised = 0
    for wri, ear in ((L_WRI, L_EAR), (R_WRI, R_EAR)):
        if not _valid(kp, wri, conf):
            continue
        height = (kp[NOSE, 1] - kp[wri, 1]) / leg
        ref = ear if _valid(kp, ear, conf) else NOSE
        lateral = abs(kp[wri, 0] - kp[ref, 0]) / leg
        if head_lo < height < head_hi and lateral < lat:
            raised += 1
    return raised == 1


class StretchTracker:
    """Counts consecutive matching frames with a small miss-tolerance so brief
    keypoint dropouts don't reset the hold. Frame-based (deterministic)."""

    def __init__(self, hold_frames: int, miss_tolerance: int = 5):
        self.hold_frames = max(1, int(hold_frames))
        self.miss_tolerance = max(0, int(miss_tolerance))
        self.count = 0
        self.miss = 0

    def update(self, matched: bool) -> int:
        if matched:
            self.count += 1
            self.miss = 0
        else:
            self.miss += 1
            if self.miss > self.miss_tolerance:
                self.count = 0
        return self.count

    @property
    def progress(self) -> float:
        return min(1.0, self.count / float(self.hold_frames))

    @property
    def complete(self) -> bool:
        return self.count >= self.hold_frames

    def reset(self) -> None:
        self.count = 0
        self.miss = 0


# Stage definitions, in play order.
STRETCHES = [
    {
        "key": "overhead",
        "name": "OVERHEAD REACH",
        "instruction": "Extend BOTH arms straight overhead",
        "fn": is_overhead_reach,
    },
    {
        "key": "fold",
        "name": "FORWARD FOLD",
        "instruction": "Bend forward at the waist, reach hands down",
        "fn": is_forward_fold,
    },
    {
        "key": "neck",
        "name": "NECK STRETCH",
        "instruction": "Pull your head to one side with one hand",
        "fn": is_neck_stretch,
    },
]
