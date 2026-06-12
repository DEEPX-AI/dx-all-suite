#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Stretch Coach — arcade mini-game core.

Three modules in one file (they change together):
  * PoseClassifier  — recognises the 3 target stretches from COCO-17 keypoints,
                      using scale-invariant metrics calibrated from the demo video.
  * HumanoidCoach   — renders a FILLED, procedural humanoid (round head, filled
                      torso/pelvis, tapered limb capsules + joint circles) and
                      animates it by looping between a neutral pose and the
                      current stage's target pose. NOT a stick figure.
  * StretchGame     — the stage state machine (hold -> advance -> GOOD! -> CLEAR!)
                      plus the arcade overlay drawn onto each video frame.

Keypoint data comes from the framework's YOLOv8PosePostprocessor as a list of
PoseResult (each with .box and 17 .keypoints[x,y,confidence]).
"""

import math
from typing import List, Optional

import numpy as np
import cv2

# COCO-17 indices
NOSE = 0
L_EYE, R_EYE, L_EAR, R_EAR = 1, 2, 3, 4
L_SHO, R_SHO = 5, 6
L_ELB, R_ELB = 7, 8
L_WRI, R_WRI = 9, 10
L_HIP, R_HIP = 11, 12
L_KNE, R_KNE = 13, 14
L_ANK, R_ANK = 15, 16

# Skeleton edges for the light player overlay (COCO-17)
PLAYER_EDGES = [
    (5, 7), (7, 9), (6, 8), (8, 10), (5, 6), (5, 11), (6, 12), (11, 12),
    (11, 13), (13, 15), (12, 14), (14, 16), (0, 5), (0, 6),
]

# Limbs for the humanoid coach: (a, b, radius_a_frac, radius_b_frac) in shoulder-width units
COACH_LIMBS = [
    (L_HIP, L_KNE, 0.22, 0.16),   # left thigh
    (L_KNE, L_ANK, 0.16, 0.11),   # left shin
    (R_HIP, R_KNE, 0.22, 0.16),   # right thigh
    (R_KNE, R_ANK, 0.16, 0.11),   # right shin
    (L_SHO, L_ELB, 0.17, 0.12),   # left upper arm
    (L_ELB, L_WRI, 0.12, 0.085),  # left forearm
    (R_SHO, R_ELB, 0.17, 0.12),   # right upper arm
    (R_ELB, R_WRI, 0.12, 0.085),  # right forearm
]

# ---------------------------------------------------------------------------
# Canonical normalised target poses (COCO-17), panel space x,y in [0,1], y down.
# Authored procedurally so the coach is robust (independent of noisy video kpts).
# ---------------------------------------------------------------------------

def _pose(d):
    """Build a 17x2 array from an index->(x,y) dict."""
    a = np.zeros((17, 2), dtype=np.float32)
    for i, (x, y) in d.items():
        a[i] = (x, y)
    return a


NEUTRAL = _pose({
    NOSE: (0.50, 0.13), L_EYE: (0.475, 0.115), R_EYE: (0.525, 0.115),
    L_EAR: (0.45, 0.125), R_EAR: (0.55, 0.125),
    L_SHO: (0.40, 0.28), R_SHO: (0.60, 0.28),
    L_ELB: (0.36, 0.43), R_ELB: (0.64, 0.43),
    L_WRI: (0.34, 0.57), R_WRI: (0.66, 0.57),
    L_HIP: (0.44, 0.57), R_HIP: (0.56, 0.57),
    L_KNE: (0.43, 0.76), R_KNE: (0.57, 0.76),
    L_ANK: (0.42, 0.95), R_ANK: (0.58, 0.95),
})

OVERHEAD = _pose({
    NOSE: (0.50, 0.15), L_EYE: (0.475, 0.135), R_EYE: (0.525, 0.135),
    L_EAR: (0.45, 0.145), R_EAR: (0.55, 0.145),
    L_SHO: (0.40, 0.30), R_SHO: (0.60, 0.30),
    L_ELB: (0.42, 0.17), R_ELB: (0.58, 0.17),
    L_WRI: (0.44, 0.03), R_WRI: (0.56, 0.03),
    L_HIP: (0.44, 0.58), R_HIP: (0.56, 0.58),
    L_KNE: (0.43, 0.77), R_KNE: (0.57, 0.77),
    L_ANK: (0.42, 0.96), R_ANK: (0.58, 0.96),
})

# Forward fold: hips high (peak of the bend), shoulders folded below hips, head
# hanging down between the arms, arms reaching toward the ankles.
FORWARD_FOLD = _pose({
    NOSE: (0.50, 0.66), L_EYE: (0.48, 0.65), R_EYE: (0.52, 0.65),
    L_EAR: (0.465, 0.63), R_EAR: (0.535, 0.63),
    L_SHO: (0.41, 0.56), R_SHO: (0.59, 0.56),
    L_ELB: (0.40, 0.68), R_ELB: (0.60, 0.68),
    L_WRI: (0.41, 0.82), R_WRI: (0.59, 0.82),
    L_HIP: (0.45, 0.44), R_HIP: (0.55, 0.44),
    L_KNE: (0.44, 0.68), R_KNE: (0.56, 0.68),
    L_ANK: (0.43, 0.93), R_ANK: (0.57, 0.93),
})

# Neck stretch: upright, RIGHT hand raised to the side of the head, head tilted
# toward it, LEFT arm hanging down.
NECK = _pose({
    NOSE: (0.525, 0.15), L_EYE: (0.50, 0.135), R_EYE: (0.55, 0.135),
    L_EAR: (0.48, 0.145), R_EAR: (0.575, 0.145),
    L_SHO: (0.40, 0.30), R_SHO: (0.60, 0.30),
    L_ELB: (0.37, 0.45), R_ELB: (0.66, 0.20),
    L_WRI: (0.36, 0.59), R_WRI: (0.565, 0.115),
    L_HIP: (0.44, 0.58), R_HIP: (0.56, 0.58),
    L_KNE: (0.43, 0.77), R_KNE: (0.57, 0.77),
    L_ANK: (0.42, 0.96), R_ANK: (0.58, 0.96),
})


# ===========================================================================
# Pose classification
# ===========================================================================

class PoseClassifier:
    """Recognise the 3 stretches from a PoseResult using calibrated thresholds."""

    def __init__(self, config: dict = None):
        c = config or {}
        self.kp_conf = float(c.get("kp_conf", 0.30))
        self.overhead_margin = float(c.get("overhead_margin", 0.35))
        self.fold_ratio_max = float(c.get("fold_ratio_max", 1.25))
        self.neck_head_dist = float(c.get("neck_head_dist", 1.10))
        self.neck_other_low = float(c.get("neck_other_low", 0.55))

    @staticmethod
    def pick_person(results: List) -> Optional[object]:
        """Return the largest-box pose, or None."""
        if not results:
            return None
        return max(results, key=lambda r: (r.box[2] - r.box[0]) * (r.box[3] - r.box[1])
                   if len(r.box) >= 4 else 0.0)

    def metrics(self, pose) -> Optional[dict]:
        """Scale-invariant metrics (normalised by shoulder width). None if torso hidden."""
        if pose is None or len(pose.keypoints) < 17:
            return None
        k = pose.keypoints
        ls, rs, lh, rh = k[L_SHO], k[R_SHO], k[L_HIP], k[R_HIP]
        lw, rw, nose = k[L_WRI], k[R_WRI], k[NOSE]
        if min(ls.confidence, rs.confidence, lh.confidence, rh.confidence) < self.kp_conf:
            return None
        sho = np.array([(ls.x + rs.x) / 2, (ls.y + rs.y) / 2], np.float32)
        hip = np.array([(lh.x + rh.x) / 2, (lh.y + rh.y) / 2], np.float32)
        S = float(math.hypot(ls.x - rs.x, ls.y - rs.y)) or 1.0
        head = np.array([nose.x, nose.y], np.float32) if nose.confidence >= self.kp_conf else sho

        def above_nose(w):
            return (head[1] - w.y) / S if w.confidence >= self.kp_conf else -9.0

        def below_sho(w):
            return (w.y - sho[1]) / S if w.confidence >= self.kp_conf else -9.0

        def head_dist(w):
            return math.hypot(w.x - head[0], w.y - head[1]) / S if w.confidence >= self.kp_conf else 9.0

        return {
            "S": S,
            "lw_above_nose": above_nose(lw), "rw_above_nose": above_nose(rw),
            "lw_below_sho": below_sho(lw), "rw_below_sho": below_sho(rw),
            "fold_ratio": (hip[1] - head[1]) / S,
            "min_head_dist": min(head_dist(lw), head_dist(rw)),
        }

    # --- per-stage detectors -------------------------------------------------

    def is_overhead(self, m) -> bool:
        return (m is not None
                and m["lw_above_nose"] > self.overhead_margin
                and m["rw_above_nose"] > self.overhead_margin)

    def is_forward_fold(self, m) -> bool:
        return m is not None and m["fold_ratio"] < self.fold_ratio_max

    def is_neck(self, m) -> bool:
        if m is None:
            return False
        both_up = (m["lw_above_nose"] > self.overhead_margin
                   and m["rw_above_nose"] > self.overhead_margin)
        one_hand_at_head = m["min_head_dist"] < self.neck_head_dist
        other_hand_low = max(m["lw_below_sho"], m["rw_below_sho"]) > self.neck_other_low
        return one_hand_at_head and other_hand_low and not both_up


# ===========================================================================
# Humanoid coach (filled, procedural, animated)
# ===========================================================================

class HumanoidCoach:
    """Draw a filled humanoid by morphing NEUTRAL <-> target in a looping cycle."""

    BODY = (150, 196, 232)      # warm skin/body fill (BGR)
    BODY_SHADE = (110, 150, 200)
    OUTLINE = (40, 60, 90)
    HEAD = (160, 205, 240)

    def __init__(self, frames_per_cycle: int = 72):
        self.fpc = max(12, int(frames_per_cycle))

    @staticmethod
    def _lerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
        return a * (1.0 - t) + b * t

    def _to_px(self, norm_pose: np.ndarray, region) -> np.ndarray:
        x0, y0, w, h = region
        pts = np.empty((17, 2), np.float32)
        pts[:, 0] = x0 + norm_pose[:, 0] * w
        pts[:, 1] = y0 + norm_pose[:, 1] * h
        return pts

    @staticmethod
    def _tapered_capsule(img, p1, p2, r1, r2, color):
        p1 = np.asarray(p1, np.float32)
        p2 = np.asarray(p2, np.float32)
        d = p2 - p1
        L = float(np.hypot(d[0], d[1]))
        if L < 1e-3:
            cv2.circle(img, (int(p1[0]), int(p1[1])), int(max(r1, r2)), color, -1, cv2.LINE_AA)
            return
        n = np.array([-d[1], d[0]], np.float32) / L
        quad = np.array([p1 + n * r1, p2 + n * r2, p2 - n * r2, p1 - n * r1], np.int32)
        cv2.fillConvexPoly(img, quad, color, cv2.LINE_AA)
        cv2.circle(img, (int(p1[0]), int(p1[1])), int(r1), color, -1, cv2.LINE_AA)
        cv2.circle(img, (int(p2[0]), int(p2[1])), int(r2), color, -1, cv2.LINE_AA)

    def render(self, img, region, target_pose: np.ndarray, frame_idx: int):
        """Draw the animated humanoid into `region` = (x0, y0, w, h) on img."""
        # Looping morph: 0 -> 1 -> 0 (smooth), demonstrates the stretch repeatedly.
        cycle = (frame_idx % self.fpc) / float(self.fpc)
        t = (1.0 - math.cos(2.0 * math.pi * cycle)) * 0.5
        pose = self._lerp(NEUTRAL, target_pose, t)
        pts = self._to_px(pose, region)

        S = float(np.hypot(pts[L_SHO, 0] - pts[R_SHO, 0], pts[L_SHO, 1] - pts[R_SHO, 1])) or 1.0

        def P(i):
            return pts[i]

        # ---- body fill pass (limbs + torso), then outline pass for definition ----
        for color, grow, is_outline in ((self.OUTLINE, 3.0, True), (self.BODY, 0.0, False)):
            # legs (drawn first / behind)
            for a, b, ra, rb in COACH_LIMBS:
                self._tapered_capsule(img, P(a), P(b), ra * S + grow, rb * S + grow, color)
            # torso polygon (shoulders -> hips) with rounded corners
            torso = np.array([P(L_SHO), P(R_SHO), P(R_HIP), P(L_HIP)], np.int32)
            cv2.fillConvexPoly(img, torso, color, cv2.LINE_AA)
            for j, r in ((L_SHO, 0.18), (R_SHO, 0.18), (L_HIP, 0.20), (R_HIP, 0.20)):
                cv2.circle(img, (int(P(j)[0]), int(P(j)[1])), int(r * S + grow), color, -1, cv2.LINE_AA)
            # pelvis bridge
            self._tapered_capsule(img, P(L_HIP), P(R_HIP), 0.20 * S + grow, 0.20 * S + grow, color)
            # neck
            neck_top = (P(NOSE) + (P(L_SHO) + P(R_SHO)) * 0.5) * 0.5
            self._tapered_capsule(img, (P(L_SHO) + P(R_SHO)) * 0.5, neck_top,
                                  0.13 * S + grow, 0.11 * S + grow, color)
            # head
            cv2.circle(img, (int(P(NOSE)[0]), int(P(NOSE)[1])),
                       int(0.30 * S + grow), color, -1, cv2.LINE_AA)

        # ---- shading / highlight so it reads as a body, not a flat blob ----
        for a, b, ra, rb in COACH_LIMBS:
            self._tapered_capsule(img, P(a), P(b), 0.45 * (ra * S), 0.40 * (rb * S), self.HEAD)
        torso = np.array([
            self._lerp(P(L_SHO), (P(L_SHO) + P(R_HIP)) * 0.5, 0.18),
            self._lerp(P(R_SHO), (P(R_SHO) + P(L_HIP)) * 0.5, 0.18),
            self._lerp(P(R_HIP), (P(R_HIP) + P(L_SHO)) * 0.5, 0.18),
            self._lerp(P(L_HIP), (P(L_HIP) + P(R_SHO)) * 0.5, 0.18),
        ], np.int32)
        cv2.fillConvexPoly(img, torso, self.BODY_SHADE, cv2.LINE_AA)
        # head highlight + simple face hint
        hx, hy, hr = int(P(NOSE)[0]), int(P(NOSE)[1]), int(0.30 * S)
        cv2.circle(img, (hx - int(hr * 0.28), hy - int(hr * 0.28)), int(hr * 0.5), self.HEAD, -1, cv2.LINE_AA)
        cv2.circle(img, (hx, hy), hr, self.OUTLINE, max(1, int(0.03 * S) + 1), cv2.LINE_AA)


# ===========================================================================
# Game state machine + arcade overlay
# ===========================================================================

class _Stage:
    def __init__(self, name, instruction, target, detector_name):
        self.name = name
        self.instruction = instruction
        self.target = target
        self.detector_name = detector_name


STAGES = [
    _Stage("OVERHEAD REACH",
           "Reach BOTH arms straight up overhead and hold.",
           OVERHEAD, "is_overhead"),
    _Stage("FORWARD FOLD",
           "Bend forward at the waist, let your hands fall toward the floor.",
           FORWARD_FOLD, "is_forward_fold"),
    _Stage("NECK STRETCH",
           "Raise ONE hand beside your head and gently tilt your head to the side.",
           NECK, "is_neck"),
]


class StretchGame:
    """Drives stage progression and renders the arcade overlay on each frame."""

    GREEN = (90, 230, 120)
    AMBER = (60, 200, 255)
    CYAN = (235, 220, 60)
    WHITE = (245, 245, 245)
    DARK = (30, 30, 38)

    def __init__(self, config: dict = None, model_name: str = "yolo26n-pose"):
        c = config or {}
        self.cfg = c
        self.model_name = model_name
        self.classifier = PoseClassifier(c)
        hold_fps = float(c.get("hold_fps", 24.0))
        self.hold_target = max(1, int(round(float(c.get("hold_seconds", 1.2)) * hold_fps)))
        self.good_frames = max(1, int(round(float(c.get("good_seconds", 0.8)) * hold_fps)))
        self.debounce = int(c.get("debounce_frames", 6))
        self.coach = HumanoidCoach(frames_per_cycle=int(round(3.0 * hold_fps)))

        self.stage_idx = 0
        self.hold = 0
        self.miss = 0
        self.good_timer = 0
        self.finished = False
        self.frame_idx = 0
        self.stages_cleared = 0
        self.person_frames = 0   # frames where the NPU produced a usable person pose
        self._fps_ema = 0.0
        import time as _t
        self._t = _t
        self._last_ts = None

    # --- logic ---------------------------------------------------------------

    def update(self, results) -> None:
        self.frame_idx += 1
        self._tick_fps()
        if self.good_timer > 0:
            self.good_timer -= 1
        if self.finished:
            return

        pose = self.classifier.pick_person(results)
        m = self.classifier.metrics(pose)
        if m is not None:
            self.person_frames += 1
        stage = STAGES[self.stage_idx]
        matched = getattr(self.classifier, stage.detector_name)(m)

        if matched:
            self.hold += 1
            self.miss = 0
        else:
            self.miss += 1
            if self.miss > self.debounce:
                self.hold = 0

        if self.hold >= self.hold_target:
            self.stages_cleared += 1
            self.hold = 0
            self.miss = 0
            self.good_timer = self.good_frames
            if self.stage_idx + 1 < len(STAGES):
                self.stage_idx += 1
            else:
                self.finished = True

    @property
    def cleared(self) -> bool:
        return self.finished

    def _tick_fps(self):
        now = self._t.perf_counter()
        if self._last_ts is not None:
            dt = now - self._last_ts
            if dt > 0:
                fps = 1.0 / dt
                self._fps_ema = fps if self._fps_ema == 0 else 0.9 * self._fps_ema + 0.1 * fps
        self._last_ts = now

    # --- rendering -----------------------------------------------------------

    @staticmethod
    def _panel(img, x0, y0, x1, y1, color, alpha):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(img.shape[1], x1), min(img.shape[0], y1)
        if x1 <= x0 or y1 <= y0:
            return
        roi = img[y0:y1, x0:x1]
        overlay = np.full_like(roi, color, dtype=np.uint8)
        cv2.addWeighted(overlay, alpha, roi, 1 - alpha, 0, roi)

    @staticmethod
    def _wrap(text, max_chars):
        words, lines, cur = text.split(), [], ""
        for w in words:
            if len(cur) + len(w) + 1 <= max_chars:
                cur = (cur + " " + w).strip()
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def _draw_player(self, img, results):
        pose = self.classifier.pick_person(results)
        if pose is None:
            return
        kc = self.classifier.kp_conf
        k = pose.keypoints
        for a, b in PLAYER_EDGES:
            if a < len(k) and b < len(k) and k[a].confidence >= kc and k[b].confidence >= kc:
                cv2.line(img, (int(k[a].x), int(k[a].y)), (int(k[b].x), int(k[b].y)),
                         (0, 220, 255), 3, cv2.LINE_AA)
        for kp in k:
            if kp.confidence >= kc:
                cv2.circle(img, (int(kp.x), int(kp.y)), 4, (40, 140, 255), -1, cv2.LINE_AA)

    def draw_overlay(self, img, results) -> np.ndarray:
        H, W = img.shape[:2]
        self._draw_player(img, results)
        stage = STAGES[self.stage_idx]

        # --- top stage bar ---
        self._panel(img, 0, 0, W, 52, self.DARK, 0.62)
        label = "CLEAR!" if self.finished else f"STAGE {self.stage_idx + 1}/{len(STAGES)}"
        cv2.putText(img, label, (16, 36), cv2.FONT_HERSHEY_DUPLEX, 1.0,
                    self.GREEN if self.finished else self.CYAN, 2, cv2.LINE_AA)
        if not self.finished:
            cv2.putText(img, stage.name, (200, 36), cv2.FONT_HERSHEY_DUPLEX, 0.95,
                        self.WHITE, 2, cv2.LINE_AA)

        # --- coach panel (top-left) ---
        px0, py0, pw, ph = 12, 64, 388, 300
        self._panel(img, px0, py0, px0 + pw, py0 + ph, (54, 40, 30), 0.55)
        cv2.rectangle(img, (px0, py0), (px0 + pw, py0 + ph), self.CYAN, 2, cv2.LINE_AA)
        cv2.putText(img, "COACH", (px0 + 12, py0 + 26), cv2.FONT_HERSHEY_DUPLEX,
                    0.7, self.CYAN, 1, cv2.LINE_AA)
        coach_region = (px0 + 8, py0 + 36, 188, ph - 60)
        self.coach.render(img, coach_region, stage.target, self.frame_idx)

        # name + instruction to the RIGHT of the coach
        tx = px0 + 206
        cv2.putText(img, stage.name, (tx, py0 + 64), cv2.FONT_HERSHEY_DUPLEX,
                    0.66, self.WHITE, 2, cv2.LINE_AA)
        for i, line in enumerate(self._wrap(stage.instruction, 22)):
            cv2.putText(img, line, (tx, py0 + 96 + i * 26), cv2.FONT_HERSHEY_SIMPLEX,
                        0.52, (210, 210, 210), 1, cv2.LINE_AA)

        # --- HOLD progress bar (under the coach panel) ---
        if not self.finished:
            bx0, by0, bw, bh = px0, py0 + ph + 14, pw, 26
            self._panel(img, bx0, by0, bx0 + bw, by0 + bh, self.DARK, 0.6)
            cv2.rectangle(img, (bx0, by0), (bx0 + bw, by0 + bh), self.WHITE, 1, cv2.LINE_AA)
            frac = min(1.0, self.hold / float(self.hold_target))
            fillw = int((bw - 4) * frac)
            if fillw > 0:
                cv2.rectangle(img, (bx0 + 2, by0 + 2), (bx0 + 2 + fillw, by0 + bh - 2),
                              self.GREEN if frac >= 0.999 else self.AMBER, -1, cv2.LINE_AA)
            cv2.putText(img, f"HOLD  {int(frac * 100):3d}%", (bx0 + 10, by0 + 19),
                        cv2.FONT_HERSHEY_DUPLEX, 0.55, self.DARK if frac > 0.5 else self.WHITE,
                        1, cv2.LINE_AA)

        # --- GOOD! flash ---
        if self.good_timer > 0 and not self.finished:
            self._big_center(img, "GOOD!", self.GREEN)

        # --- CLEAR! banner ---
        if self.finished:
            self._big_center(img, "CLEAR!", self.GREEN, sub="All 3 stretches complete!")
            if self.good_timer > 0:
                pass

        # --- status line (bottom) ---
        self._panel(img, 0, H - 30, W, H, self.DARK, 0.6)
        fps = self._fps_ema
        cv2.putText(img,
                    f"DEEPX DX-M1 NPU | {self.model_name} | pose-estimation | {fps:4.1f} FPS",
                    (12, H - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 230, 180), 1, cv2.LINE_AA)
        cv2.putText(img, "STRETCH COACH", (W - 220, H - 9), cv2.FONT_HERSHEY_DUPLEX,
                    0.55, self.CYAN, 1, cv2.LINE_AA)
        return img

    def _big_center(self, img, text, color, sub=None):
        H, W = img.shape[:2]
        scale = 3.2
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, scale, 6)
        x = (W - tw) // 2
        y = (H + th) // 2
        # shadow + main
        cv2.putText(img, text, (x + 3, y + 3), cv2.FONT_HERSHEY_DUPLEX, scale, self.DARK, 8, cv2.LINE_AA)
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, scale, color, 6, cv2.LINE_AA)
        if sub:
            (sw, sh), _ = cv2.getTextSize(sub, cv2.FONT_HERSHEY_DUPLEX, 0.9, 2)
            cv2.putText(img, sub, ((W - sw) // 2, y + 50), cv2.FONT_HERSHEY_DUPLEX,
                        0.9, self.WHITE, 2, cv2.LINE_AA)
