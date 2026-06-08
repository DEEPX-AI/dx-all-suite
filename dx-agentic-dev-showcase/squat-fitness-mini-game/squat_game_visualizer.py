#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
SquatGameVisualizer — arcade-style squat-counting HUD.

Extends the framework ``PoseVisualizer`` so the COCO skeleton is still drawn,
then layers a fitness-game HUD on top. ``SyncRunner`` calls ``visualize(frame,
results)`` once per frame, which makes this the natural place to host the
stateful rep counter — no standalone loop, no direct engine calls.

The HUD shows: rep counter (reps / target), score, a progress bar, the live
knee angle, and large feedback text (DOWN / UP / GOOD! / GOAL!).
"""

import logging
from typing import List, Optional

import cv2
import numpy as np

from common.visualizers import PoseVisualizer
from common.base import PoseResult

from squat_rep_counter import SquatRepCounter, compute_angle

logger = logging.getLogger(__name__)

# COCO-17 keypoint indices
L_SHOULDER, R_SHOULDER = 5, 6
L_HIP, R_HIP = 11, 12
L_KNEE, R_KNEE = 13, 14
L_ANKLE, R_ANKLE = 15, 16

# HUD palette (BGR)
_C_PANEL = (28, 28, 28)
_C_ACCENT = (0, 215, 255)     # amber
_C_GOOD = (0, 255, 0)         # green
_C_DOWN = (0, 165, 255)       # orange
_C_UP = (255, 255, 255)
_C_GOAL = (0, 255, 0)
_C_BAR_BG = (70, 70, 70)
_C_TEXT = (255, 255, 255)

_FLASH_FRAMES = 12            # how long GOOD! stays on screen after a rep


class SquatGameVisualizer(PoseVisualizer):
    """Pose visualizer with a stateful squat-counting arcade HUD."""

    def __init__(self, game_config: Optional[dict] = None):
        super().__init__(
            draw_box=True, draw_skeleton=True, draw_keypoints=True,
            keypoint_confidence_threshold=float(
                (game_config or {}).get("keypoint_confidence_threshold", 0.3)),
        )
        self.counter = SquatRepCounter(game_config)
        self._flash = 0
        self._last_status = {
            "state": "UP", "reps": 0, "score": 0,
            "target_reps": self.counter.target_reps,
            "feedback": "GO!", "knee_angle": None, "goal_reached": False,
        }

    # ---------------------------------------------------------------- angles

    @staticmethod
    def _kp_ok(kp, thr: float) -> bool:
        return kp is not None and kp.confidence >= thr

    def _side_angles(self, kps, shoulder, hip, knee, ankle, thr):
        """Return (knee_angle, hip_angle) for one body side, or (None, None)."""
        s, h, k, a = (kps[shoulder], kps[hip], kps[knee], kps[ankle])
        knee_ang = hip_ang = None
        if all(self._kp_ok(p, thr) for p in (h, k, a)):
            knee_ang = compute_angle((h.x, h.y), (k.x, k.y), (a.x, a.y))
        if all(self._kp_ok(p, thr) for p in (s, h, k)):
            hip_ang = compute_angle((s.x, s.y), (h.x, h.y), (k.x, k.y))
        return knee_ang, hip_ang

    def _extract_angles(self, pose: PoseResult):
        """Average left/right knee & hip angles from visible keypoints."""
        kps = pose.keypoints
        if not kps or len(kps) < 17:
            return None, None
        thr = self.kpt_conf_threshold
        lk, lh = self._side_angles(kps, L_SHOULDER, L_HIP, L_KNEE, L_ANKLE, thr)
        rk, rh = self._side_angles(kps, R_SHOULDER, R_HIP, R_KNEE, R_ANKLE, thr)
        knee = self._mean([lk, rk])
        hip = self._mean([lh, rh])
        return knee, hip

    @staticmethod
    def _mean(vals):
        vals = [v for v in vals if v is not None]
        return sum(vals) / len(vals) if vals else None

    @staticmethod
    def _primary_pose(results: List[PoseResult]) -> Optional[PoseResult]:
        """Largest-box person is the player."""
        best, best_area = None, -1.0
        for p in results:
            if p.box and len(p.box) >= 4:
                area = max(0.0, p.box[2] - p.box[0]) * max(0.0, p.box[3] - p.box[1])
            else:
                area = 0.0
            if area > best_area:
                best, best_area = p, area
        return best

    # ----------------------------------------------------------- main hook

    def visualize(self, image: np.ndarray, results: List[PoseResult]) -> np.ndarray:
        output = super().visualize(image, results)

        pose = self._primary_pose(results)
        if pose is not None:
            knee, hip = self._extract_angles(pose)
            status = self.counter.update(knee, hip)
            if status["just_completed"]:
                self._flash = _FLASH_FRAMES
                logger.info(
                    "Squat rep %d counted (score %d/%d)%s",
                    status["reps"], status["score"],
                    status["target_reps"],
                    "  -- GOAL REACHED!" if status["goal_reached"] else "")
            self._last_status = status
        # if no person this frame, keep last status (no update) so the HUD is stable

        if self._flash > 0:
            self._flash -= 1

        self._draw_hud(output, self._last_status, player_present=pose is not None)
        return output

    # ----------------------------------------------------------------- HUD

    def _draw_hud(self, img: np.ndarray, status: dict, player_present: bool) -> None:
        h, w = img.shape[:2]
        reps = status["reps"]
        target = status["target_reps"]
        score = status["score"]
        knee = status.get("knee_angle")
        state = status["state"]

        # --- translucent top panel ---
        panel_h = max(70, int(h * 0.13))
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (w, panel_h), _C_PANEL, -1)
        cv2.addWeighted(overlay, 0.55, img, 0.45, 0, img)
        cv2.line(img, (0, panel_h), (w, panel_h), _C_ACCENT, 2)

        fs = max(0.6, w / 1280.0)        # font scale relative to width

        # --- title ---
        cv2.putText(img, "SQUAT ARCADE", (16, int(panel_h * 0.42)),
                    cv2.FONT_HERSHEY_DUPLEX, 0.7 * fs, _C_ACCENT, 2, cv2.LINE_AA)

        # --- reps + score ---
        cv2.putText(img, f"REPS {reps:02d}/{target:02d}",
                    (16, int(panel_h * 0.85)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8 * fs, _C_TEXT, 2, cv2.LINE_AA)
        score_txt = f"SCORE {score:04d}"
        (sw, _), _ = cv2.getTextSize(score_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.8 * fs, 2)
        cv2.putText(img, score_txt, (w - sw - 16, int(panel_h * 0.85)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8 * fs, _C_ACCENT, 2, cv2.LINE_AA)

        # --- progress bar ---
        bar_x0, bar_x1 = 16, w - 16
        bar_y = panel_h + 14
        bar_h = 14
        cv2.rectangle(img, (bar_x0, bar_y), (bar_x1, bar_y + bar_h), _C_BAR_BG, -1)
        frac = 0.0 if target <= 0 else min(1.0, reps / float(target))
        fill_x = int(bar_x0 + frac * (bar_x1 - bar_x0))
        cv2.rectangle(img, (bar_x0, bar_y), (fill_x, bar_y + bar_h), _C_GOOD, -1)
        cv2.rectangle(img, (bar_x0, bar_y), (bar_x1, bar_y + bar_h), _C_TEXT, 1)

        # --- live knee angle ---
        if knee is not None:
            cv2.putText(img, f"knee {knee:5.1f}deg",
                        (16, bar_y + bar_h + 26),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5 * fs, _C_TEXT, 1, cv2.LINE_AA)

        # --- big feedback text ---
        self._draw_feedback(img, status, player_present, fs)

    def _draw_feedback(self, img, status, player_present, fs):
        h, w = img.shape[:2]
        if not player_present and status["reps"] == 0:
            text, color = "STEP INTO FRAME", _C_ACCENT
        elif status["goal_reached"]:
            text, color = "GOAL!", _C_GOAL
        elif self._flash > 0:
            text, color = "GOOD!", _C_GOOD
        elif status["state"] == "DOWN":
            text, color = "DOWN", _C_DOWN
        else:
            text, color = "UP", _C_UP

        scale = 1.8 * fs
        thick = max(2, int(3 * fs))
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, scale, thick)
        cx = (w - tw) // 2
        cy = int(h * 0.86)
        # shadow for readability over any background
        cv2.putText(img, text, (cx + 2, cy + 2),
                    cv2.FONT_HERSHEY_DUPLEX, scale, (0, 0, 0), thick + 2, cv2.LINE_AA)
        cv2.putText(img, text, (cx, cy),
                    cv2.FONT_HERSHEY_DUPLEX, scale, color, thick, cv2.LINE_AA)
