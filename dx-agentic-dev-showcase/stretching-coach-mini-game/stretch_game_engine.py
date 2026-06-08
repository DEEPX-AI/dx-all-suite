#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Stretch game engine — the stateful IVisualizer that IS the mini-game.

The DEEPX SyncRunner calls ``visualize(frame, results)`` once per frame. We
exploit that hook: each frame we pick the dominant person, classify the held
pose from COCO-17 keypoints, advance a frame-based state machine, and composite
the arcade UI (player skeleton + STAGE banner + animated coach panel + HOLD bar
+ GOOD!/CLEAR! feedback) onto the frame.

Timing is **frame-based** (not wall-clock): hold/animation are measured in
frames at a configured ``fps``. This makes the game deterministic and makes the
saved annotated video fill the HOLD bar over ``hold_seconds`` of *video* time,
identically on replay and in verify.py.
"""

import os
from typing import List, Optional, Set

import numpy as np
import cv2

from coach_avatar import (
    load_templates, render_coach_panel,
    NOSE, L_SH, R_SH, L_EL, R_EL, L_WR, R_WR,
    L_HIP, R_HIP, L_KNEE, R_KNEE, L_ANKLE, R_ANKLE,
)

try:
    from common.utility.skeleton import SKELETON, POSE_LIMB_COLOR
except Exception:  # pragma: no cover - standalone/self-test fallback
    SKELETON = [
        [15, 13], [13, 11], [16, 14], [14, 12], [11, 12], [5, 11], [6, 12],
        [5, 6], [5, 7], [6, 8], [7, 9], [8, 10], [1, 2], [0, 1], [0, 2],
        [1, 3], [2, 4], [3, 5], [4, 6],
    ]
    POSE_LIMB_COLOR = [(0, 255, 0)] * len(SKELETON)

# Stage table: (classifier key, display name, instruction).
STAGES = [
    ("overhead", "REACH FOR THE SKY", "Extend both arms straight overhead"),
    ("fold", "TOUCH YOUR TOES", "Bend forward, reach down to your feet"),
    ("neck", "NECK RELEASE", "Pull your head to one side with one hand"),
]

ACCENT = (0, 235, 255)   # amber
GOOD_COLOR = (60, 230, 60)
BAR_BG = (60, 60, 60)


# =====================================================================
# Pose classifier
# =====================================================================

class StretchClassifier:
    """Scale-normalized geometric classifier for the three stretch poses."""

    def __init__(self, config: dict = None):
        config = config or {}
        self.kpt_conf = float(config.get("kpt_conf", 0.3))
        self.overhead_margin = float(config.get("overhead_margin", 0.05))
        self.fold_shoulder_hip = float(config.get("fold_shoulder_hip", 0.55))
        self.fold_wrist = float(config.get("fold_wrist", 0.15))
        self.neck_x = float(config.get("neck_x", 0.55))

    def _pt(self, kps, idx: int) -> Optional[np.ndarray]:
        if idx >= len(kps):
            return None
        kp = kps[idx]
        if kp.confidence < self.kpt_conf:
            return None
        return np.array([kp.x, kp.y], dtype=np.float32)

    @staticmethod
    def _mean(a, b):
        if a is None or b is None:
            return a if b is None else b
        return (a + b) * 0.5

    def body_scale(self, kps, box=None) -> float:
        """Vertical body unit ~ one leg (hip->ankle). Robust fallbacks."""
        legs = []
        for hip, ankle in ((L_HIP, L_ANKLE), (R_HIP, R_ANKLE)):
            h, a = self._pt(kps, hip), self._pt(kps, ankle)
            if h is not None and a is not None:
                legs.append(abs(a[1] - h[1]))
        if legs:
            return max(1e-3, float(np.mean(legs)))
        # Fallback: shoulder->hip span * 2.
        msh = self._mean(self._pt(kps, L_SH), self._pt(kps, R_SH))
        mhip = self._mean(self._pt(kps, L_HIP), self._pt(kps, R_HIP))
        if msh is not None and mhip is not None:
            return max(1e-3, abs(mhip[1] - msh[1]) * 2.0)
        # Final fallback: bounding-box height.
        if box is not None:
            return max(1e-3, abs(box[3] - box[1]))
        return 1.0

    def classify(self, kps, scale: float) -> Set[str]:
        """Return the subset of {'overhead','fold','neck'} currently matched."""
        matched: Set[str] = set()
        nose = self._pt(kps, NOSE)
        lsh, rsh = self._pt(kps, L_SH), self._pt(kps, R_SH)
        lwr, rwr = self._pt(kps, L_WR), self._pt(kps, R_WR)
        lhip, rhip = self._pt(kps, L_HIP), self._pt(kps, R_HIP)
        msh = self._mean(lsh, rsh)
        mhip = self._mean(lhip, rhip)

        # --- Stage 1: both wrists clearly above the head ---
        if nose is not None and lwr is not None and rwr is not None:
            thr = nose[1] - self.overhead_margin * scale
            if lwr[1] < thr and rwr[1] < thr:
                matched.add("overhead")

        # --- Stage 2: forward fold (torso dropped, head down) ---
        if nose is not None and msh is not None and mhip is not None:
            sh_hip_gap = mhip[1] - msh[1]               # +ve when standing tall
            head_dropped = nose[1] > msh[1] - 0.05 * scale
            torso_folded = sh_hip_gap < self.fold_shoulder_hip * scale
            if torso_folded and head_dropped:
                matched.add("fold")

        # --- Stage 3: exactly one hand raised beside the head ---
        if nose is not None and msh is not None \
                and lwr is not None and rwr is not None:
            def raised_beside(w):
                return (w[1] < msh[1]) and (abs(w[0] - nose[0]) < self.neck_x * scale)
            def hanging(w):
                return w[1] > msh[1]
            l_up, r_up = raised_beside(lwr), raised_beside(rwr)
            if (l_up and hanging(rwr)) or (r_up and hanging(lwr)):
                if not (l_up and r_up):   # exclude the overhead "both up" case
                    matched.add("neck")
        return matched


# =====================================================================
# Game engine / visualizer
# =====================================================================

class StretchGameVisualizer:
    """Stateful arcade game rendered as a dx_app IVisualizer."""

    def __init__(self, config: dict = None, start_stage: int = 0,
                 templates_path: Optional[str] = None):
        config = config or {}
        self.cfg = config
        self.classifier = StretchClassifier(config)

        fps = float(config.get("fps", 30.0))
        self.hold_frames = max(1, int(round(float(config.get("hold_seconds", 1.2)) * fps)))
        self.grace_frames = max(0, int(round(float(config.get("release_grace", 0.3)) * fps)))
        self.flash_frames = max(1, int(round(float(config.get("flash_seconds", 0.8)) * fps)))
        self.cycle_frames = max(2, int(round(float(config.get("coach_cycle", 1.6)) * fps)))
        self.kpt_conf = float(config.get("kpt_conf", 0.3))

        if templates_path is None:
            templates_path = os.path.join(os.path.dirname(__file__),
                                          "pose_templates.json")
        self.templates = load_templates(templates_path)

        # State.
        self.stage = max(0, min(start_stage, len(STAGES) - 1))
        self.hold = 0
        self.grace = 0
        self.flash = 0
        self.anim = 0
        self.mode = "PLAYING"   # PLAYING -> GAME_CLEAR
        self.completed = 0      # stages cleared this run

    # ----- public state accessors (used by verify.py) -----
    def is_game_clear(self) -> bool:
        return self.mode == "GAME_CLEAR"

    # ----- helpers -----
    @staticmethod
    def _dominant(results):
        best, best_area = None, -1.0
        for r in results or []:
            if not getattr(r, "keypoints", None) or not getattr(r, "box", None):
                continue
            x1, y1, x2, y2 = r.box
            area = abs((x2 - x1) * (y2 - y1))
            if area > best_area:
                best, best_area = r, area
        return best

    def _draw_player_skeleton(self, img, kps):
        for i, (a, b) in enumerate(SKELETON):
            if a >= len(kps) or b >= len(kps):
                continue
            ka, kb = kps[a], kps[b]
            if ka.confidence < self.kpt_conf or kb.confidence < self.kpt_conf:
                continue
            color = POSE_LIMB_COLOR[i] if i < len(POSE_LIMB_COLOR) else (0, 255, 255)
            cv2.line(img, (int(ka.x), int(ka.y)), (int(kb.x), int(kb.y)), color, 2, cv2.LINE_AA)
        for kp in kps:
            if kp.confidence >= self.kpt_conf:
                cv2.circle(img, (int(kp.x), int(kp.y)), 3, (255, 255, 255), -1, cv2.LINE_AA)

    def _coach_phase(self) -> float:
        p = (self.anim % self.cycle_frames) / float(self.cycle_frames)
        return 1.0 - abs(2.0 * p - 1.0)   # triangle 0->1->0

    # ----- main hook -----
    def visualize(self, frame: np.ndarray, results: List) -> np.ndarray:
        out = frame.copy()
        h, w = out.shape[:2]
        self.anim += 1

        person = self._dominant(results)
        matched_now = False
        if person is not None:
            self._draw_player_skeleton(out, person.keypoints)
            if self.mode == "PLAYING":
                scale = self.classifier.body_scale(person.keypoints, person.box)
                keys = self.classifier.classify(person.keypoints, scale)
                matched_now = STAGES[self.stage][0] in keys

        if self.mode == "PLAYING":
            if matched_now:
                self.hold += 1
                self.grace = 0
            else:
                self.grace += 1
                if self.grace > self.grace_frames:
                    self.hold = max(0, self.hold - 1)   # gentle decay
            if self.hold >= self.hold_frames:
                self.completed += 1
                self.flash = self.flash_frames
                self.hold = 0
                self.grace = 0
                if self.stage + 1 >= len(STAGES):
                    self.mode = "GAME_CLEAR"
                else:
                    self.stage += 1

        self._draw_ui(out, w, h, matched_now)
        if self.flash > 0:
            self.flash -= 1
        return out

    # ----- UI compositing -----
    def _draw_ui(self, out, w, h, matched_now):
        # Top banner.
        cv2.rectangle(out, (0, 0), (w, 44), (20, 20, 20), -1)
        if self.mode == "GAME_CLEAR":
            banner = "ALL STRETCHES COMPLETE"
        else:
            banner = f"STAGE {self.stage + 1}/{len(STAGES)}  -  {STAGES[self.stage][1]}"
        cv2.putText(out, banner, (14, 31), cv2.FONT_HERSHEY_DUPLEX, 0.8,
                    ACCENT, 2, cv2.LINE_AA)

        # Coach panel (top-left, below banner).
        panel_w = max(180, int(w * 0.24))
        panel_h = max(220, int(h * 0.46))
        panel_w = min(panel_w, w // 2)
        panel_h = min(panel_h, h - 60)
        if self.mode == "GAME_CLEAR":
            key, name, instr = STAGES[-1]
            phase = self._coach_phase()
        else:
            key, name, instr = STAGES[self.stage]
            phase = self._coach_phase()
        panel = render_coach_panel(panel_w, panel_h, self.templates["neutral"],
                                   self.templates.get(key, self.templates["neutral"]),
                                   phase, name, instr, ACCENT)
        y0 = 50
        out[y0:y0 + panel_h, 10:10 + panel_w] = panel

        # HOLD progress bar (bottom center) while playing.
        if self.mode == "PLAYING":
            bar_w = int(w * 0.5)
            bar_h = 26
            bx = (w - bar_w) // 2
            by = h - 50
            cv2.rectangle(out, (bx, by), (bx + bar_w, by + bar_h), BAR_BG, -1)
            frac = min(1.0, self.hold / float(self.hold_frames))
            fill = int(bar_w * frac)
            col = GOOD_COLOR if matched_now else ACCENT
            if fill > 0:
                cv2.rectangle(out, (bx, by), (bx + fill, by + bar_h), col, -1)
            cv2.rectangle(out, (bx, by), (bx + bar_w, by + bar_h), (230, 230, 230), 2)
            label = "HOLD IT!" if matched_now else "STRIKE THE POSE"
            cv2.putText(out, label, (bx, by - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (230, 230, 230), 2, cv2.LINE_AA)

        # GOOD! flash.
        if self.flash > 0 and self.mode != "GAME_CLEAR":
            self._center_text(out, w, h, "GOOD!", 2.2, GOOD_COLOR)
        elif self.flash > 0 and self.mode == "GAME_CLEAR":
            pass  # CLEAR! handled below

        # CLEAR! screen.
        if self.mode == "GAME_CLEAR":
            self._center_text(out, w, h, "CLEAR!", 2.6, GOOD_COLOR)
            cv2.putText(out, "Great stretching!", (int(w * 0.5) - 150, int(h * 0.5) + 60),
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)

    @staticmethod
    def _center_text(out, w, h, text, scale, color):
        font = cv2.FONT_HERSHEY_DUPLEX
        (tw, th), _ = cv2.getTextSize(text, font, scale, 4)
        x = (w - tw) // 2
        y = (h + th) // 2
        cv2.putText(out, text, (x + 3, y + 3), font, scale, (0, 0, 0), 7, cv2.LINE_AA)
        cv2.putText(out, text, (x, y), font, scale, color, 4, cv2.LINE_AA)


# =====================================================================
# Self-test
# =====================================================================

if __name__ == "__main__":
    class _KP:
        def __init__(self, x, y, c=0.9):
            self.x, self.y, self.confidence = x, y, c

    def make(scale=200.0):
        """Neutral standing skeleton at image scale (y down)."""
        cx, hip_y = 320.0, 400.0
        kps = [_KP(cx, hip_y - 1.9 * scale)]  # nose approx
        # fill 17 with rough standing positions
        pts = {
            0: (cx, hip_y - 1.9 * scale),
            5: (cx - 0.4 * scale, hip_y - 1.4 * scale),
            6: (cx + 0.4 * scale, hip_y - 1.4 * scale),
            7: (cx - 0.48 * scale, hip_y - 0.8 * scale),
            8: (cx + 0.48 * scale, hip_y - 0.8 * scale),
            9: (cx - 0.52 * scale, hip_y - 0.2 * scale),
            10: (cx + 0.52 * scale, hip_y - 0.2 * scale),
            11: (cx - 0.24 * scale, hip_y),
            12: (cx + 0.24 * scale, hip_y),
            13: (cx - 0.24 * scale, hip_y + 0.5 * scale),
            14: (cx + 0.24 * scale, hip_y + 0.5 * scale),
            15: (cx - 0.24 * scale, hip_y + 1.0 * scale),
            16: (cx + 0.24 * scale, hip_y + 1.0 * scale),
            1: (cx - 0.1 * scale, hip_y - 1.95 * scale),
            2: (cx + 0.1 * scale, hip_y - 1.95 * scale),
            3: (cx - 0.18 * scale, hip_y - 1.9 * scale),
            4: (cx + 0.18 * scale, hip_y - 1.9 * scale),
        }
        return [_KP(*pts[i]) for i in range(17)]

    clf = StretchClassifier()
    scale = 200.0

    stand = make(scale)
    assert clf.classify(stand, clf.body_scale(stand)) == set(), "standing should match nothing"

    overhead = make(scale)
    overhead[9] = _KP(310, 400 - 2.4 * scale)   # L wrist way up
    overhead[10] = _KP(330, 400 - 2.4 * scale)  # R wrist way up
    assert "overhead" in clf.classify(overhead, clf.body_scale(overhead)), "overhead fail"

    fold = make(scale)
    # shoulders drop to ~hip level, nose below shoulders, wrists near ankles
    fold[5] = _KP(300, 400 - 0.15 * scale); fold[6] = _KP(340, 400 - 0.15 * scale)
    fold[0] = _KP(320, 400 + 0.05 * scale)
    fold[9] = _KP(305, 400 + 0.7 * scale); fold[10] = _KP(335, 400 + 0.7 * scale)
    assert "fold" in clf.classify(fold, clf.body_scale(fold)), "fold fail"

    neck = make(scale)
    neck[10] = _KP(330, 400 - 1.6 * scale)  # R wrist up beside head (near nose.x)
    assert "neck" in clf.classify(neck, clf.body_scale(neck)), "neck fail"
    assert "overhead" not in clf.classify(neck, clf.body_scale(neck)), "neck must not be overhead"

    print("PASS: classifier recognizes stand/overhead/fold/neck correctly")
