# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
SquatGameVisualizer — arcade-style squat-counting fitness mini-game overlay.

This is the stateful game hook. ``SyncRunner`` calls ``visualize(frame, results)``
once per frame with ``PoseResult`` keypoints already scaled to original-image
coordinates. The visualizer:

  1. selects the most prominent person (largest box),
  2. computes the knee (hip-knee-ankle) and hip (shoulder-hip-knee) angles from
     COCO-17 keypoints, averaging the left + right sides when both are visible,
  3. advances the squat FSM (``SquatCounter``) with hysteresis,
  4. tracks reps / score / a "GOOD!" feedback flash,
  5. draws the pose skeleton (via the parent ``PoseVisualizer``) plus an
     arcade HUD (rep counter, target, score, DOWN/UP/GOOD! banner, progress bar).

All inference stays in the IFactory + SyncRunner framework — this class only
consumes the decoded keypoints.
"""

import numpy as np
import cv2

from common.visualizers import PoseVisualizer
from .squat_logic import angle_3pt, SquatCounter

# COCO-17 keypoint indices
L_SHOULDER, R_SHOULDER = 5, 6
L_HIP, R_HIP = 11, 12
L_KNEE, R_KNEE = 13, 14
L_ANKLE, R_ANKLE = 15, 16


class SquatGameVisualizer(PoseVisualizer):
    """Pose visualizer that turns squats into an arcade rep-counting game."""

    def __init__(self, config: dict = None):
        super().__init__(keypoint_confidence_threshold=0.3)
        cfg = config or {}
        self.knee_down = float(cfg.get("knee_down_angle", 140.0))
        self.knee_up = float(cfg.get("knee_up_angle", 160.0))
        self.hip_down = cfg.get("hip_down_angle", 150.0)
        self.hip_down = float(self.hip_down) if self.hip_down is not None else None
        self.target_reps = int(cfg.get("target_reps", 10))
        self.kpt_conf_threshold = float(cfg.get("kpt_conf_threshold", 0.3))

        self.counter = SquatCounter(self.knee_down, self.knee_up, self.hip_down)
        self.score = 0
        self.score_per_rep = int(cfg.get("score_per_rep", 10))
        self._good_flash = 0          # frames remaining to show "GOOD!"
        self._good_flash_frames = 12
        self._last_knee = None
        self._last_hip = None
        self._won = False

    # ------------------------------------------------------------------
    # Angle extraction
    # ------------------------------------------------------------------

    def _kp(self, keypoints, idx):
        """Return (x, y) if keypoint idx is confident enough, else None."""
        if idx >= len(keypoints):
            return None
        kp = keypoints[idx]
        if kp.confidence < self.kpt_conf_threshold:
            return None
        return (float(kp.x), float(kp.y))

    def _side_angle(self, keypoints, a_idx, b_idx, c_idx):
        a = self._kp(keypoints, a_idx)
        b = self._kp(keypoints, b_idx)
        c = self._kp(keypoints, c_idx)
        if a is None or b is None or c is None:
            return None
        return angle_3pt(a, b, c)

    def _knee_angle(self, keypoints):
        left = self._side_angle(keypoints, L_HIP, L_KNEE, L_ANKLE)
        right = self._side_angle(keypoints, R_HIP, R_KNEE, R_ANKLE)
        vals = [v for v in (left, right) if v is not None]
        return sum(vals) / len(vals) if vals else None

    def _hip_angle(self, keypoints):
        left = self._side_angle(keypoints, L_SHOULDER, L_HIP, L_KNEE)
        right = self._side_angle(keypoints, R_SHOULDER, R_HIP, R_KNEE)
        vals = [v for v in (left, right) if v is not None]
        return sum(vals) / len(vals) if vals else None

    @staticmethod
    def _largest_person(results):
        best = None
        best_area = -1.0
        for pose in results:
            if not getattr(pose, "keypoints", None):
                continue
            box = getattr(pose, "box", None)
            area = 0.0
            if box and len(box) >= 4:
                area = abs((box[2] - box[0]) * (box[3] - box[1]))
            if area >= best_area:
                best_area = area
                best = pose
        return best

    # ------------------------------------------------------------------
    # Per-frame entry
    # ------------------------------------------------------------------

    def visualize(self, image: np.ndarray, results) -> np.ndarray:
        # 1) draw the skeleton/keypoints using the parent implementation
        output = super().visualize(image, results)

        # 2) game logic on the most prominent person
        knee = hip = None
        state = self.counter.state
        person = self._largest_person(results) if results else None
        if person is not None:
            knee = self._knee_angle(person.keypoints)
            hip = self._hip_angle(person.keypoints)
            if knee is not None:
                # hip may be missing (e.g. occluded shoulder); if so, pass a
                # value that satisfies the gate so the knee drives detection.
                hip_for_fsm = hip if hip is not None else 0.0
                prev_reps = self.counter.reps
                state, completed = self.counter.update(knee, hip_for_fsm)
                if completed:
                    self.score += self.score_per_rep
                    self._good_flash = self._good_flash_frames
                if self.counter.reps >= self.target_reps:
                    self._won = True
                self._last_knee = knee
                self._last_hip = hip

        if self._good_flash > 0:
            self._good_flash -= 1

        # 3) arcade HUD
        self._draw_hud(output, state, knee, hip)
        return output

    # ------------------------------------------------------------------
    # HUD rendering
    # ------------------------------------------------------------------

    def _draw_hud(self, img, state, knee, hip):
        h, w = img.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX

        # --- top translucent header bar ---
        bar_h = max(70, int(h * 0.13))
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (w, bar_h), (28, 28, 28), -1)
        cv2.addWeighted(overlay, 0.55, img, 0.45, 0, img)
        cv2.line(img, (0, bar_h), (w, bar_h), (0, 215, 255), 2)

        title = "SQUAT  CHALLENGE"
        cv2.putText(img, title, (16, int(bar_h * 0.42)), font,
                    0.9, (0, 215, 255), 2, cv2.LINE_AA)

        # REPS counter (big)
        reps_txt = f"REPS  {self.counter.reps:02d}/{self.target_reps:02d}"
        cv2.putText(img, reps_txt, (16, int(bar_h * 0.85)), font,
                    1.0, (255, 255, 255), 2, cv2.LINE_AA)

        # SCORE (right aligned-ish)
        score_txt = f"SCORE  {self.score:04d}"
        (sw, _), _ = cv2.getTextSize(score_txt, font, 0.9, 2)
        cv2.putText(img, score_txt, (w - sw - 16, int(bar_h * 0.85)), font,
                    0.9, (80, 255, 80), 2, cv2.LINE_AA)

        # --- progress bar ---
        pb_x1, pb_x2 = 16, w - 16
        pb_y = bar_h + 14
        frac = min(1.0, self.counter.reps / max(1, self.target_reps))
        cv2.rectangle(img, (pb_x1, pb_y), (pb_x2, pb_y + 16), (70, 70, 70), -1)
        fill_x = int(pb_x1 + (pb_x2 - pb_x1) * frac)
        cv2.rectangle(img, (pb_x1, pb_y), (fill_x, pb_y + 16), (0, 215, 255), -1)
        cv2.rectangle(img, (pb_x1, pb_y), (pb_x2, pb_y + 16), (255, 255, 255), 1)

        # --- center feedback banner ---
        if self._won:
            text, color = "WIN!  COMPLETE", (80, 255, 80)
        elif self._good_flash > 0:
            text, color = "GOOD!", (80, 255, 80)
        elif state == "DOWN":
            text, color = "DOWN", (255, 200, 0)
        else:
            text, color = "UP", (0, 215, 255)

        scale = 2.4 if text in ("GOOD!", "WIN!  COMPLETE") else 1.8
        (tw, th), _ = cv2.getTextSize(text, font, scale, 5)
        tx = (w - tw) // 2
        ty = int(h * 0.62)
        # shadow then text for arcade pop
        cv2.putText(img, text, (tx + 3, ty + 3), font, scale, (0, 0, 0), 8, cv2.LINE_AA)
        cv2.putText(img, text, (tx, ty), font, scale, color, 5, cv2.LINE_AA)

        # --- angle readout (bottom-left) ---
        if knee is not None:
            ka = f"knee {knee:5.1f}"
            ha = f"hip {hip:5.1f}" if hip is not None else "hip   --"
            cv2.putText(img, f"{ka}   {ha}", (16, h - 16), font,
                        0.6, (200, 200, 200), 1, cv2.LINE_AA)
        else:
            cv2.putText(img, "no person detected", (16, h - 16), font,
                        0.6, (60, 60, 230), 2, cv2.LINE_AA)
