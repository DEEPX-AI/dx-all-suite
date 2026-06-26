#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Stretch-Coach game logic + rendering for the yolo26n-pose arcade mini-game.

This module is the per-frame brain of the app. SyncRunner calls
``StretchCoachVisualizer.visualize(frame, results)`` once per frame; everything
the game does — pose recognition, the hold-to-advance state machine, the
animated procedural humanoid coach, and the arcade HUD — happens there.

Coordinate convention: OpenCV image space, x→right, y→DOWN.

Pose recognition uses COCO-17 keypoints and is scale-invariant: every threshold
is normalized by the player's shoulder width (a stable body unit), so the game
works regardless of how far the player stands from the camera. Keypoints with
confidence below ``keypoint_confidence_threshold`` are treated as missing, and a
stretch that needs a missing keypoint cannot match.
"""

import math
from typing import List, Optional, Tuple

import numpy as np
import cv2

# ----------------------------------------------------------------------------
# COCO-17 keypoint indices
# ----------------------------------------------------------------------------
NOSE = 0
L_EYE, R_EYE = 1, 2
L_EAR, R_EAR = 3, 4
L_SHO, R_SHO = 5, 6
L_ELB, R_ELB = 7, 8
L_WRI, R_WRI = 9, 10
L_HIP, R_HIP = 11, 12
L_KNE, R_KNE = 13, 14
L_ANK, R_ANK = 15, 16

# COCO skeleton edges (for the light player overlay)
SKELETON_EDGES = [
    (L_SHO, R_SHO), (L_SHO, L_ELB), (L_ELB, L_WRI),
    (R_SHO, R_ELB), (R_ELB, R_WRI), (L_SHO, L_HIP), (R_SHO, R_HIP),
    (L_HIP, R_HIP), (L_HIP, L_KNE), (L_KNE, L_ANK),
    (R_HIP, R_KNE), (R_KNE, R_ANK), (NOSE, L_SHO), (NOSE, R_SHO),
]


# ----------------------------------------------------------------------------
# Keypoint access helpers (work on common.base.Keypoint OR plain (x,y,conf))
# ----------------------------------------------------------------------------
def _kp(kps, idx: int, conf_thr: float) -> Optional[Tuple[float, float]]:
    """Return (x, y) for keypoint idx if present & confident, else None."""
    if idx >= len(kps):
        return None
    k = kps[idx]
    if hasattr(k, "x"):
        x, y, c = float(k.x), float(k.y), float(getattr(k, "confidence", 1.0))
    else:
        x, y, c = float(k[0]), float(k[1]), float(k[2] if len(k) > 2 else 1.0)
    if c < conf_thr:
        return None
    return (x, y)


def _mid(a, b):
    return ((a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5)


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


class PoseMetrics:
    """Normalized body metrics for one person. None fields = missing keypoints."""

    __slots__ = ("nose", "lsho", "rsho", "lwri", "rwri", "lhip", "rhip",
                 "lelb", "relb", "sho_c", "hip_c", "shoulder_w", "scale", "ok")

    def __init__(self, kps, conf_thr: float):
        self.nose = _kp(kps, NOSE, conf_thr)
        self.lsho = _kp(kps, L_SHO, conf_thr)
        self.rsho = _kp(kps, R_SHO, conf_thr)
        self.lwri = _kp(kps, L_WRI, conf_thr)
        self.rwri = _kp(kps, R_WRI, conf_thr)
        self.lhip = _kp(kps, L_HIP, conf_thr)
        self.rhip = _kp(kps, R_HIP, conf_thr)
        self.lelb = _kp(kps, L_ELB, conf_thr)
        self.relb = _kp(kps, R_ELB, conf_thr)

        self.sho_c = _mid(self.lsho, self.rsho) if self.lsho and self.rsho else None
        self.hip_c = _mid(self.lhip, self.rhip) if self.lhip and self.rhip else None

        # Shoulder width is the primary scale; fall back to hip width or torso.
        if self.lsho and self.rsho:
            self.shoulder_w = _dist(self.lsho, self.rsho)
        elif self.lhip and self.rhip:
            self.shoulder_w = _dist(self.lhip, self.rhip)
        else:
            self.shoulder_w = 0.0
        # A robust scale unit: prefer shoulder width, but never let it collapse to ~0.
        self.scale = max(self.shoulder_w, 1e-3)
        # We need shoulders to do anything meaningful.
        self.ok = self.sho_c is not None


def recognize_overhead(kps, cfg) -> bool:
    """Both arms straight overhead: both wrists clearly above the head."""
    conf = cfg.get("keypoint_confidence_threshold", 0.3)
    m = PoseMetrics(kps, conf)
    if not m.ok or m.nose is None or m.lwri is None or m.rwri is None:
        return False
    margin = cfg.get("overhead_wrist_above_nose_ratio", 0.15) * m.scale
    # y grows downward → "above" means smaller y.
    above_nose = (m.lwri[1] < m.nose[1] - margin) and (m.rwri[1] < m.nose[1] - margin)
    above_sho = (m.lwri[1] < m.sho_c[1]) and (m.rwri[1] < m.sho_c[1])
    return above_nose and above_sho


def recognize_forward_fold(kps, cfg) -> bool:
    """Forward fold: shoulders dropped toward hips and head dropped down."""
    conf = cfg.get("keypoint_confidence_threshold", 0.3)
    m = PoseMetrics(kps, conf)
    if not m.ok or m.hip_c is None or m.nose is None:
        return False
    # Standing: shoulders well above hips → (hip_y - sho_y)/scale is large (~1.3-2.0).
    # Folding forward collapses that vertical gap as the back goes horizontal.
    torso_v_norm = (m.hip_c[1] - m.sho_c[1]) / m.scale
    collapsed = torso_v_norm < cfg.get("fold_torso_collapse_ratio", 0.45)
    # Head has dropped to (or below) shoulder line — strong fold signal.
    head_drop_norm = (m.nose[1] - m.sho_c[1]) / m.scale
    head_dropped = head_drop_norm > cfg.get("fold_head_drop_ratio", -0.1)
    return collapsed and head_dropped


def recognize_neck_stretch(kps, cfg) -> bool:
    """Neck stretch: exactly one hand raised beside the head, the other hanging."""
    conf = cfg.get("keypoint_confidence_threshold", 0.3)
    m = PoseMetrics(kps, conf)
    if not m.ok or m.nose is None or m.lwri is None or m.rwri is None:
        return False
    h_ratio = cfg.get("neck_hand_horizontal_ratio", 0.95) * m.scale
    top = m.nose[1] - cfg.get("neck_hand_top_ratio", 0.6) * m.scale   # not far above head
    bottom = m.sho_c[1]                                                # down to shoulder line

    def beside_head(w):
        return (top < w[1] < bottom) and (abs(w[0] - m.nose[0]) < h_ratio)

    def hanging(w):
        return w[1] > m.sho_c[1]  # below shoulders

    l_up, r_up = beside_head(m.lwri), beside_head(m.rwri)
    l_dn, r_dn = hanging(m.lwri), hanging(m.rwri)
    # Exactly one hand beside head, the other hanging low.
    return (l_up and r_dn and not r_up) or (r_up and l_dn and not l_up)


# Ordered stage table: (key, display name, instruction, recognizer)
STAGES = [
    ("overhead", "OVERHEAD REACH",
     "Reach both arms straight up overhead", recognize_overhead),
    ("fold", "FORWARD FOLD",
     "Bend forward at the waist, hands toward the floor", recognize_forward_fold),
    ("neck", "NECK STRETCH",
     "Raise one hand beside your head and tilt", recognize_neck_stretch),
]


# ============================================================================
# Animated procedural humanoid coach
# ============================================================================
# Normalized coach poses in panel-local coords ([0,1] x [0,1], y DOWN).
# Each is a dict idx -> (x, y) using COCO indices. The coach is drawn as a
# FILLED humanoid (head + torso + tapered limb capsules), not a stick figure.

_POSE_NEUTRAL = {
    NOSE: (0.50, 0.13),
    L_SHO: (0.41, 0.30), R_SHO: (0.59, 0.30),
    L_ELB: (0.35, 0.46), R_ELB: (0.65, 0.46),
    L_WRI: (0.32, 0.61), R_WRI: (0.68, 0.61),
    L_HIP: (0.44, 0.58), R_HIP: (0.56, 0.58),
    L_KNE: (0.43, 0.77), R_KNE: (0.57, 0.77),
    L_ANK: (0.43, 0.95), R_ANK: (0.57, 0.95),
}

_POSE_OVERHEAD = {
    NOSE: (0.50, 0.16),
    L_SHO: (0.41, 0.31), R_SHO: (0.59, 0.31),
    L_ELB: (0.44, 0.17), R_ELB: (0.56, 0.17),
    L_WRI: (0.46, 0.03), R_WRI: (0.54, 0.03),
    L_HIP: (0.44, 0.58), R_HIP: (0.56, 0.58),
    L_KNE: (0.43, 0.77), R_KNE: (0.57, 0.77),
    L_ANK: (0.43, 0.95), R_ANK: (0.57, 0.95),
}

_POSE_FOLD = {
    NOSE: (0.50, 0.55),
    L_SHO: (0.42, 0.49), R_SHO: (0.58, 0.49),
    L_ELB: (0.45, 0.63), R_ELB: (0.55, 0.63),
    L_WRI: (0.47, 0.76), R_WRI: (0.53, 0.76),
    L_HIP: (0.44, 0.50), R_HIP: (0.56, 0.50),
    L_KNE: (0.44, 0.74), R_KNE: (0.56, 0.74),
    L_ANK: (0.44, 0.95), R_ANK: (0.56, 0.95),
}

_POSE_NECK = {
    NOSE: (0.53, 0.16),
    L_SHO: (0.41, 0.31), R_SHO: (0.59, 0.31),
    L_ELB: (0.66, 0.22), R_ELB: (0.66, 0.22),   # placeholder, overwritten below
    L_WRI: (0.34, 0.61), R_WRI: (0.49, 0.08),
    L_HIP: (0.44, 0.58), R_HIP: (0.56, 0.58),
    L_KNE: (0.43, 0.77), R_KNE: (0.57, 0.77),
    L_ANK: (0.43, 0.95), R_ANK: (0.57, 0.95),
}
# Neck: right arm reaches over the head; left arm hangs.
_POSE_NECK[R_ELB] = (0.66, 0.20)
_POSE_NECK[L_ELB] = (0.35, 0.46)

_TARGET_POSE = {
    "overhead": _POSE_OVERHEAD,
    "fold": _POSE_FOLD,
    "neck": _POSE_NECK,
}


def _lerp_pose(a, b, t):
    """Interpolate two normalized poses. t in [0,1]."""
    out = {}
    for idx in a:
        ax, ay = a[idx]
        bx, by = b.get(idx, a[idx])
        out[idx] = (ax + (bx - ax) * t, ay + (by - ay) * t)
    return out


def _smoothstep(t):
    return t * t * (3.0 - 2.0 * t)


def _draw_capsule(img, p0, p1, r0, r1, color, edge=None):
    """Draw a tapered filled capsule (limb segment) with smooth round joints."""
    p0 = (float(p0[0]), float(p0[1]))
    p1 = (float(p1[0]), float(p1[1]))
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    if length < 1e-3:
        cv2.circle(img, (int(p0[0]), int(p0[1])), int(max(r0, r1)), color, -1, cv2.LINE_AA)
        return
    # Unit perpendicular.
    nx, ny = -dy / length, dx / length
    quad = np.array([
        [p0[0] + nx * r0, p0[1] + ny * r0],
        [p1[0] + nx * r1, p1[1] + ny * r1],
        [p1[0] - nx * r1, p1[1] - ny * r1],
        [p0[0] - nx * r0, p0[1] - ny * r0],
    ], dtype=np.int32)
    if edge is not None:
        cv2.polylines(img, [quad], True, edge, 3, cv2.LINE_AA)
        cv2.circle(img, (int(p0[0]), int(p0[1])), int(r0) + 1, edge, 2, cv2.LINE_AA)
        cv2.circle(img, (int(p1[0]), int(p1[1])), int(r1) + 1, edge, 2, cv2.LINE_AA)
    cv2.fillConvexPoly(img, quad, color, cv2.LINE_AA)
    cv2.circle(img, (int(p0[0]), int(p0[1])), int(r0), color, -1, cv2.LINE_AA)
    cv2.circle(img, (int(p1[0]), int(p1[1])), int(r1), color, -1, cv2.LINE_AA)


def draw_humanoid(img, pose_norm, origin, size, body=(70, 200, 250),
                  edge=(30, 90, 140)):
    """Render a filled humanoid from a normalized pose into img at origin/size.

    body color is BGR (default warm orange). Limbs are tapered capsules; the
    torso is a filled rounded polygon; the head is a shaded circle. The result
    reads as a human silhouette, never a stick figure.
    """
    ox, oy = origin
    w, h = size

    def P(idx):
        x, y = pose_norm[idx]
        return (ox + x * w, oy + y * h)

    unit = (w + h) * 0.5
    r_limb_u = unit * 0.045   # upper-limb radius
    r_limb_l = unit * 0.033   # lower-limb (wrist/ankle) radius
    r_joint = unit * 0.050
    head_r = unit * 0.085

    sho_c = _mid(P(L_SHO), P(R_SHO))
    hip_c = _mid(P(L_HIP), P(R_HIP))

    # --- torso/pelvis: filled rounded polygon shoulders→hips ---
    torso = np.array([P(L_SHO), P(R_SHO), P(R_HIP), P(L_HIP)], dtype=np.int32)
    cv2.fillConvexPoly(img, torso, edge, cv2.LINE_AA)        # dark backing
    torso_in = np.array([
        _mid(P(L_SHO), sho_c), _mid(P(R_SHO), sho_c),
        _mid(P(R_HIP), hip_c), _mid(P(L_HIP), hip_c)], dtype=np.int32)
    # neck capsule
    _draw_capsule(img, P(NOSE), sho_c, head_r * 0.55, r_joint, body, edge)
    # pelvis capsule (joins hips)
    _draw_capsule(img, P(L_HIP), P(R_HIP), r_joint, r_joint, body, edge)
    # torso fill on top of dark backing for a beveled look
    cv2.fillConvexPoly(img, torso, body, cv2.LINE_AA)
    cv2.polylines(img, [torso], True, edge, 2, cv2.LINE_AA)

    # --- limbs (capsules), drawn with dark edge then body fill ---
    limbs = [
        (L_SHO, L_ELB, r_limb_u, r_limb_u), (L_ELB, L_WRI, r_limb_u, r_limb_l),
        (R_SHO, R_ELB, r_limb_u, r_limb_u), (R_ELB, R_WRI, r_limb_u, r_limb_l),
        (L_HIP, L_KNE, r_joint, r_limb_u), (L_KNE, L_ANK, r_limb_u, r_limb_l),
        (R_HIP, R_KNE, r_joint, r_limb_u), (R_KNE, R_ANK, r_limb_u, r_limb_l),
    ]
    for a, b, ra, rb in limbs:
        _draw_capsule(img, P(a), P(b), ra, rb, body, edge)

    # --- joints: smooth filled circles ---
    for idx in (L_SHO, R_SHO, L_ELB, R_ELB, L_HIP, R_HIP, L_KNE, R_KNE):
        c = P(idx)
        cv2.circle(img, (int(c[0]), int(c[1])), int(r_joint), body, -1, cv2.LINE_AA)
    # hands & feet caps
    for idx, rr in ((L_WRI, r_limb_l), (R_WRI, r_limb_l),
                    (L_ANK, r_limb_l), (R_ANK, r_limb_l)):
        c = P(idx)
        cv2.circle(img, (int(c[0]), int(c[1])), int(rr), body, -1, cv2.LINE_AA)

    # --- head: shaded circle + simple face ---
    hc = P(NOSE)
    hc_i = (int(hc[0]), int(hc[1]))
    cv2.circle(img, hc_i, int(head_r) + 2, edge, -1, cv2.LINE_AA)
    cv2.circle(img, hc_i, int(head_r), body, -1, cv2.LINE_AA)
    # highlight (top-left)
    hi = (int(hc[0] - head_r * 0.3), int(hc[1] - head_r * 0.3))
    hl = tuple(min(255, int(c + 45)) for c in body)
    cv2.circle(img, hi, int(head_r * 0.45), hl, -1, cv2.LINE_AA)


class CoachRenderer:
    """Renders the animated humanoid coach for the current stage."""

    def __init__(self, period_frames: int = 70):
        self.period = max(8, period_frames)

    def render(self, panel, origin, size, stage_key: str, frame_idx: int):
        """Draw the coach (neutral↔target loop) onto `panel` at origin/size."""
        target = _TARGET_POSE.get(stage_key, _POSE_NEUTRAL)
        phase = (math.sin(2.0 * math.pi * frame_idx / self.period) + 1.0) * 0.5
        t = _smoothstep(phase)
        pose = _lerp_pose(_POSE_NEUTRAL, target, t)
        draw_humanoid(panel, pose, origin, size)
        return t


# ============================================================================
# Game state + arcade-UI visualizer (the SyncRunner per-frame hook)
# ============================================================================

# Arcade palette (BGR)
_C_BG = (28, 22, 18)
_C_ACCENT = (70, 200, 250)     # warm orange
_C_GOOD = (90, 230, 120)       # green
_C_WHITE = (245, 245, 245)
_C_DIM = (160, 160, 160)
_C_BAR_BG = (60, 60, 60)


class StretchCoachVisualizer:
    """IVisualizer-compatible game renderer.

    SyncRunner calls ``visualize(frame, results)`` once per frame. We pick the
    main player, run the current stage's recognizer, integrate a frame-based
    hold meter, advance on completion, and draw the full arcade overlay.
    """

    def __init__(self, config: dict = None):
        cfg = config or {}
        self.cfg = cfg
        # Frame-based hold (deterministic for both video files and live camera).
        self.hold_frames = int(cfg.get("hold_frames", 14))
        self.decay = float(cfg.get("hold_decay", 2.0))
        self.good_flash_frames = int(cfg.get("good_flash_frames", 18))

        self.coach = CoachRenderer(int(cfg.get("coach_period_frames", 70)))
        self.kpt_conf = float(cfg.get("keypoint_confidence_threshold", 0.3))

        self.stage_idx = 0
        self.hold = 0.0
        self.frame_idx = 0
        self.flash = 0          # >0 → showing GOOD! ; counts down
        self.cleared = False
        self.debug = bool(cfg.get("debug"))

    # -- player selection --
    @staticmethod
    def pick_main_person(results):
        """Largest-area detection = closest player."""
        best, best_area = None, -1.0
        for r in results or []:
            box = getattr(r, "box", None)
            if not box or len(box) < 4:
                continue
            area = abs((box[2] - box[0]) * (box[3] - box[1]))
            if area > best_area:
                best, best_area = r, area
        return best

    # -- main per-frame hook --
    def visualize(self, image: np.ndarray, results) -> np.ndarray:
        self.frame_idx += 1
        out = image
        person = self.pick_main_person(results)
        kps = getattr(person, "keypoints", None) if person else None

        matched = False
        if not self.cleared and self.flash == 0 and kps:
            recognizer = STAGES[self.stage_idx][3]
            matched = recognizer(kps, self.cfg)

        # Hold meter / state machine
        if not self.cleared:
            if self.flash > 0:
                self.flash -= 1
                if self.flash == 0:
                    self.stage_idx += 1
                    self.hold = 0.0
                    if self.stage_idx >= len(STAGES):
                        self.cleared = True
            else:
                if matched:
                    self.hold = min(self.hold_frames, self.hold + 1.0)
                else:
                    self.hold = max(0.0, self.hold - self.decay)
                if self.hold >= self.hold_frames:
                    self.flash = self.good_flash_frames

        if self.debug and (self.frame_idx % 5 == 0 or matched):
            key = "CLEAR" if self.cleared else STAGES[self.stage_idx][0]
            print(f"[game] f={self.frame_idx} stage={key} matched={matched} "
                  f"hold={self.hold:.0f}/{self.hold_frames} flash={self.flash}",
                  flush=True)

        # --- draw player skeleton (faint, self-correction aid) ---
        if kps:
            self._draw_player_skeleton(out, kps)

        self._draw_overlay(out, person is not None)
        return out

    # -- rendering helpers --
    def _draw_player_skeleton(self, img, kps):
        for a, b in SKELETON_EDGES:
            pa = _kp(kps, a, self.kpt_conf)
            pb = _kp(kps, b, self.kpt_conf)
            if pa and pb:
                cv2.line(img, (int(pa[0]), int(pa[1])), (int(pb[0]), int(pb[1])),
                         (90, 220, 255), 2, cv2.LINE_AA)
        for i in range(17):
            p = _kp(kps, i, self.kpt_conf)
            if p:
                cv2.circle(img, (int(p[0]), int(p[1])), 3, (255, 255, 255), -1, cv2.LINE_AA)

    @staticmethod
    def _alpha_rect(img, x, y, w, h, color, alpha):
        x2, y2 = min(img.shape[1], x + w), min(img.shape[0], y + h)
        x, y = max(0, x), max(0, y)
        if x2 <= x or y2 <= y:
            return
        roi = img[y:y2, x:x2]
        overlay = np.full_like(roi, color, dtype=np.uint8)
        cv2.addWeighted(overlay, alpha, roi, 1 - alpha, 0, roi)

    def _draw_overlay(self, img, have_person: bool):
        H, W = img.shape[:2]
        s = W / 1280.0  # scale UI to frame width

        # --- top banner ---
        self._alpha_rect(img, 0, 0, W, int(64 * s), _C_BG, 0.6)
        if self.cleared:
            title = "ALL STRETCHES COMPLETE"
        else:
            name = STAGES[self.stage_idx][1]
            title = f"STAGE {self.stage_idx + 1}/{len(STAGES)}   -   {name}"
        cv2.putText(img, "STRETCH ARCADE", (int(20 * s), int(42 * s)),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9 * s, _C_ACCENT, max(1, int(2 * s)), cv2.LINE_AA)
        (tw, _), _ = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 0.8 * s, 2)
        cv2.putText(img, title, (W - tw - int(20 * s), int(42 * s)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8 * s, _C_WHITE, max(1, int(2 * s)), cv2.LINE_AA)

        if self.cleared:
            self._draw_clear(img)
            return

        # --- coach card (top-left) ---
        cx, cy = int(20 * s), int(80 * s)
        cw, ch = int(300 * s), int(330 * s)
        self._alpha_rect(img, cx, cy, cw, ch, (40, 32, 26), 0.72)
        cv2.rectangle(img, (cx, cy), (cx + cw, cy + ch), _C_ACCENT, max(1, int(2 * s)), cv2.LINE_AA)
        cv2.putText(img, "COACH", (cx + int(12 * s), cy + int(26 * s)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6 * s, _C_DIM, max(1, int(1 * s)), cv2.LINE_AA)
        key = STAGES[self.stage_idx][0]
        self.coach.render(img, (cx + int(20 * s), cy + int(34 * s)),
                          (cw - int(40 * s), ch - int(50 * s)), key, self.frame_idx)

        # --- stretch name + instruction (right of coach) ---
        tx = cx + cw + int(28 * s)
        cv2.putText(img, STAGES[self.stage_idx][1], (tx, cy + int(40 * s)),
                    cv2.FONT_HERSHEY_DUPLEX, 1.0 * s, _C_ACCENT, max(1, int(2 * s)), cv2.LINE_AA)
        self._wrap_text(img, STAGES[self.stage_idx][2], tx, cy + int(80 * s),
                        int(560 * s), 0.7 * s, _C_WHITE)

        # --- HOLD progress (radial on coach card + bar) ---
        progress = self.hold / max(1, self.hold_frames)
        self._draw_hold_ring(img, cx + cw - int(40 * s), cy + int(40 * s), int(24 * s), progress)
        self._draw_hold_bar(img, tx, cy + int(150 * s), int(420 * s), int(26 * s), progress, s)

        if not have_person:
            msg = "Step into frame so the camera can see your whole body"
            (mw, _), _ = cv2.getTextSize(msg, cv2.FONT_HERSHEY_SIMPLEX, 0.7 * s, 2)
            cv2.putText(img, msg, ((W - mw) // 2, H - int(40 * s)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7 * s, _C_DIM, max(1, int(2 * s)), cv2.LINE_AA)

        # --- GOOD! flash ---
        if self.flash > 0:
            self._center_banner(img, "GOOD!", _C_GOOD)

        # --- stage pips (bottom) ---
        self._draw_pips(img, s)

    def _wrap_text(self, img, text, x, y, max_w, scale, color):
        words = text.split()
        line, yy = "", y
        for wd in words:
            test = (line + " " + wd).strip()
            (tw, th), _ = cv2.getTextSize(test, cv2.FONT_HERSHEY_SIMPLEX, scale, 2)
            if tw > max_w and line:
                cv2.putText(img, line, (x, yy), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2, cv2.LINE_AA)
                yy += int(th * 1.8)
                line = wd
            else:
                line = test
        if line:
            cv2.putText(img, line, (x, yy), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2, cv2.LINE_AA)

    def _draw_hold_ring(self, img, cx, cy, r, progress):
        cv2.circle(img, (cx, cy), r, _C_BAR_BG, 4, cv2.LINE_AA)
        if progress > 0:
            end = int(-90 + 360 * progress)
            cv2.ellipse(img, (cx, cy), (r, r), 0, -90, end, _C_GOOD, 4, cv2.LINE_AA)

    def _draw_hold_bar(self, img, x, y, w, h, progress, s):
        cv2.rectangle(img, (x, y), (x + w, y + h), _C_BAR_BG, -1, cv2.LINE_AA)
        fill = int(w * progress)
        col = _C_GOOD if progress >= 0.999 else _C_ACCENT
        if fill > 0:
            cv2.rectangle(img, (x, y), (x + fill, y + h), col, -1, cv2.LINE_AA)
        cv2.rectangle(img, (x, y), (x + w, y + h), _C_WHITE, max(1, int(1 * s)), cv2.LINE_AA)
        cv2.putText(img, f"HOLD {int(progress * 100)}%", (x, y - int(8 * s)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6 * s, _C_WHITE, max(1, int(1 * s)), cv2.LINE_AA)

    def _center_banner(self, img, text, color):
        H, W = img.shape[:2]
        s = W / 1280.0
        scale = 3.0 * s
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, scale, 6)
        x, y = (W - tw) // 2, (H + th) // 2
        self._alpha_rect(img, x - int(40 * s), y - th - int(30 * s),
                         tw + int(80 * s), th + int(60 * s), _C_BG, 0.55)
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, scale, color,
                    max(2, int(6 * s)), cv2.LINE_AA)

    def _draw_pips(self, img, s):
        H, W = img.shape[:2]
        n = len(STAGES)
        r = int(12 * s)
        gap = int(44 * s)
        total = (n - 1) * gap
        x0 = (W - total) // 2
        y = H - int(36 * s)
        for i in range(n):
            x = x0 + i * gap
            if i < self.stage_idx or self.cleared:
                cv2.circle(img, (x, y), r, _C_GOOD, -1, cv2.LINE_AA)
            elif i == self.stage_idx:
                cv2.circle(img, (x, y), r, _C_ACCENT, -1, cv2.LINE_AA)
            else:
                cv2.circle(img, (x, y), r, _C_BAR_BG, -1, cv2.LINE_AA)
            cv2.circle(img, (x, y), r, _C_WHITE, max(1, int(1 * s)), cv2.LINE_AA)

    def _draw_clear(self, img):
        H, W = img.shape[:2]
        s = W / 1280.0
        self._alpha_rect(img, 0, 0, W, H, _C_BG, 0.45)
        self._center_banner(img, "CLEAR!", _C_GOOD)
        sub = "Great job - you completed all 3 stretches"
        (sw, _), _ = cv2.getTextSize(sub, cv2.FONT_HERSHEY_SIMPLEX, 0.9 * s, 2)
        cv2.putText(img, sub, ((W - sw) // 2, int(H * 0.66)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9 * s, _C_WHITE, max(1, int(2 * s)), cv2.LINE_AA)
        self._draw_pips(img, s)
