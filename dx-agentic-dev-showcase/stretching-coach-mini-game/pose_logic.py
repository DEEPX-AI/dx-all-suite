#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Pure (NPU-free) pose logic for the yolo26n-pose stretch mini-game.

Everything here operates on plain COCO-17 keypoint data so it is unit-testable
without the NPU/dx_engine. The recognizers are **leg-normalized** — the hip->ankle
length is used as the scale because legs stay roughly vertical even during a waist
bend, whereas the torso's vertical extent collapses toward zero in 2D projection
(which makes torso-normalized fold metrics explode). See the session README.

COCO-17 keypoint order (matches common/utility/skeleton.py KEYPOINT_NAMES):
 0 nose        1 left_eye    2 right_eye   3 left_ear    4 right_ear
 5 left_shoulder 6 right_shoulder 7 left_elbow 8 right_elbow
 9 left_wrist  10 right_wrist 11 left_hip   12 right_hip
13 left_knee   14 right_knee  15 left_ankle 16 right_ankle
"""

import math
from typing import Dict, List, Optional, Tuple

KEYPOINT_NAMES: List[str] = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
]
KP = {name: i for i, name in enumerate(KEYPOINT_NAMES)}

Point = Tuple[float, float]
PoseMap = Dict[str, Point]


# ---------------------------------------------------------------------------
# Keypoint extraction & geometry
# ---------------------------------------------------------------------------

def extract_keypoints(pose, conf_thr: float = 0.3) -> PoseMap:
    """Build {name: (x, y)} for keypoints whose confidence >= conf_thr.

    ``pose`` is anything with a ``keypoints`` list of objects exposing
    ``.x``, ``.y``, ``.confidence`` (e.g. common.base.PoseResult).
    """
    out: PoseMap = {}
    kpts = getattr(pose, "keypoints", None) or []
    for name, idx in KP.items():
        if idx < len(kpts):
            k = kpts[idx]
            if getattr(k, "confidence", 0.0) >= conf_thr:
                out[name] = (float(k.x), float(k.y))
    return out


def _dist(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _mid(a: Optional[Point], b: Optional[Point]) -> Optional[Point]:
    if a is not None and b is not None:
        return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    return a if a is not None else b


def leg_scale(P: PoseMap) -> Optional[float]:
    """Body scale = hip->ankle length (px). Robust during a waist bend.

    Falls back to hip->knee * 1.9, then |hip - shoulder| if legs are not visible.
    Returns None if no scale can be derived.
    """
    legs = []
    for hip, ankle in (("left_hip", "left_ankle"), ("right_hip", "right_ankle")):
        if hip in P and ankle in P:
            legs.append(_dist(P[hip], P[ankle]))
    if legs:
        return max(legs)
    knees = []
    for hip, knee in (("left_hip", "left_knee"), ("right_hip", "right_knee")):
        if hip in P and knee in P:
            knees.append(_dist(P[hip], P[knee]) * 1.9)
    if knees:
        return max(knees)
    hip = _mid(P.get("left_hip"), P.get("right_hip"))
    sho = _mid(P.get("left_shoulder"), P.get("right_shoulder"))
    if hip is not None and sho is not None:
        d = _dist(hip, sho)
        if d > 1e-3:
            return d * 2.2
    return None


# ---------------------------------------------------------------------------
# Pose recognizers (thresholds come from config; defaults are clip-measured)
# ---------------------------------------------------------------------------

DEFAULT_CFG = {
    "kpt_conf": 0.3,
    "overhead_margin": 0.0,    # wrists above nose by this * scale
    "overhead_above_sho": 0.15,  # wrists above shoulders by this * scale
    "fold_shoulder_drop": -0.30,  # (shoulder_y - hip_y)/scale must exceed this
    "fold_hands_below_hip": -0.15,  # (hip_y - wrist_y)/scale must be below this
    "neck_head_lo": -0.35,     # (nose_y - wrist_y)/scale lower bound
    "neck_head_hi": 1.0,       # ... upper bound (wrist near head height)
    "neck_lateral": 0.6,       # |wrist_x - ear_x|/scale upper bound
}


def detect_overhead(P: PoseMap, scale: float, cfg: dict) -> bool:
    """Both wrists raised above the head: above the nose AND the shoulders."""
    need = ("nose", "left_shoulder", "right_shoulder", "left_wrist", "right_wrist")
    if not all(n in P for n in need) or not scale:
        return False
    nose_y = P["nose"][1]
    margin = cfg["overhead_margin"] * scale
    above_sho = cfg["overhead_above_sho"] * scale
    for wr, sho in (("left_wrist", "left_shoulder"), ("right_wrist", "right_shoulder")):
        if not (nose_y - P[wr][1] > margin):
            return False
        if not (P[sho][1] - P[wr][1] > above_sho):
            return False
    return True


def detect_fold(P: PoseMap, scale: float, cfg: dict) -> bool:
    """Forward fold at the waist: shoulders dropped toward the hips and hands
    reaching down to/below hip level."""
    sho = _mid(P.get("left_shoulder"), P.get("right_shoulder"))
    hip = _mid(P.get("left_hip"), P.get("right_hip"))
    if sho is None or hip is None or not scale:
        return False
    shoulder_drop = (sho[1] - hip[1]) / scale  # ~ -0.6 standing, -> 0 when folded
    if not (shoulder_drop > cfg["fold_shoulder_drop"]):
        return False
    # lowest visible wrist relative to hip; negative => below the hip
    rels = []
    for wr in ("left_wrist", "right_wrist"):
        if wr in P:
            rels.append((hip[1] - P[wr][1]) / scale)
    if not rels:
        return False
    return min(rels) < cfg["fold_hands_below_hip"]


def detect_neck(P: PoseMap, scale: float, cfg: dict) -> bool:
    """Neck stretch: exactly one hand raised beside the head (near head height
    and laterally close to an ear); the other hand is not raised."""
    if not scale:
        return False
    nose = P.get("nose")
    if nose is None:
        return False
    qualifying = 0
    for wr, ear in (("left_wrist", "left_ear"), ("right_wrist", "right_ear")):
        if wr not in P:
            continue
        head_rel = (nose[1] - P[wr][1]) / scale
        if not (cfg["neck_head_lo"] < head_rel < cfg["neck_head_hi"]):
            continue
        # lateral distance to the nearest available ear (same side preferred)
        ear_pt = P.get(ear) or P.get("right_ear" if ear == "left_ear" else "left_ear") or nose
        if abs(P[wr][0] - ear_pt[0]) / scale < cfg["neck_lateral"]:
            qualifying += 1
    return qualifying == 1


STAGE_DEFS = [
    {"key": "overhead", "name": "OVERHEAD REACH",
     "instruction": "Raise BOTH arms straight overhead", "detector": detect_overhead},
    {"key": "fold", "name": "FORWARD FOLD",
     "instruction": "Bend at the waist, reach hands toward your feet", "detector": detect_fold},
    {"key": "neck", "name": "NECK STRETCH",
     "instruction": "Raise ONE hand beside your head", "detector": detect_neck},
]


def detect_stage(stage_key: str, P: PoseMap, scale: Optional[float], cfg: dict) -> bool:
    """Run the recognizer for a given stage key."""
    if scale is None:
        return False
    for s in STAGE_DEFS:
        if s["key"] == stage_key:
            return bool(s["detector"](P, scale, cfg))
    return False


# ---------------------------------------------------------------------------
# Game state machine (frame-based hold for deterministic video + verify)
# ---------------------------------------------------------------------------

class StretchGame:
    """Stage progression with a frame-based hold counter.

    update(matched) once per frame:
      * matched True increments the hold; reaching hold_frames clears the stage.
      * a short grace tolerates brief detection dropouts before resetting hold.
    Exposes current_stage, hold_progress (0..1), cleared, and flash counters for
    GOOD!/CLEAR! feedback.
    """

    def __init__(self, stages: List[dict], hold_frames: int, grace: int = 8,
                 flash_frames: int = 24):
        self.stages = stages
        self.hold_frames = max(1, int(hold_frames))
        self.grace = int(grace)
        self.flash_frames = int(flash_frames)
        self.idx = 0
        self.hold = 0
        self.miss = 0
        self.cleared = False
        self.good_flash = 0
        self.clear_flash = 0

    def update(self, matched: bool) -> None:
        if self.good_flash > 0:
            self.good_flash -= 1
        if self.cleared:
            if self.clear_flash > 0:
                self.clear_flash -= 1
            return
        if matched:
            self.hold += 1
            self.miss = 0
            if self.hold >= self.hold_frames:
                self.hold = 0
                self.idx += 1
                self.good_flash = self.flash_frames
                if self.idx >= len(self.stages):
                    self.cleared = True
                    self.clear_flash = self.flash_frames * 4
        else:
            self.miss += 1
            if self.miss > self.grace:
                self.hold = 0

    @property
    def stage_number(self) -> int:
        return min(self.idx + 1, len(self.stages))

    @property
    def total_stages(self) -> int:
        return len(self.stages)

    @property
    def current_stage(self) -> Optional[dict]:
        if self.cleared or self.idx >= len(self.stages):
            return None
        return self.stages[self.idx]

    @property
    def hold_progress(self) -> float:
        return min(1.0, self.hold / self.hold_frames)
