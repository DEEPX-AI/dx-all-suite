#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Pure squat repetition state machine.

This module is deliberately free of OpenCV / dx_engine / NumPy dependencies so
it can be unit-tested in isolation. It consumes joint angles (degrees) and emits
the current game state, rep count, score, and feedback text.

Squat detection logic
----------------------
A squat is one full ``UP -> DOWN -> UP`` cycle of the knee joint. We track the
**knee angle** = angle(hip, knee, ankle); the **hip angle** = angle(shoulder,
hip, knee) is accepted for future use / robustness but the rep decision is driven
by the knee, which is the most reliable squat signal in a 2D frontal view.

Robustness:
  * Sliding-window mean smooths per-frame jitter (``smoothing_window``).
  * Hysteresis: ``UP -> DOWN`` requires knee <= ``knee_down_angle``;
    ``DOWN -> UP`` requires knee >= ``knee_up_angle``. The gap between the two
    prevents oscillation near a single threshold.
  * Debounce: a candidate transition must persist for ``min_state_frames``
    consecutive frames before it commits, rejecting single-frame noise.

NOTE on thresholds: in a 2D view the knee angle at the bottom of a squat does
NOT reach 90 degrees (camera foreshortening) — it commonly bottoms out around
120-140 degrees. ``knee_down_angle`` / ``knee_up_angle`` must therefore be
calibrated from measured data (see ``calibrate_squat.py``), not assumed.
"""

import math
from collections import deque
from typing import Optional, Tuple

Point = Tuple[float, float]

DEFAULTS = {
    "target_reps": 10,
    "score_per_rep": 10,
    "knee_down_angle": 140.0,
    "knee_up_angle": 160.0,
    "smoothing_window": 5,
    "min_state_frames": 3,
}


def compute_angle(a: Point, b: Point, c: Point) -> Optional[float]:
    """Return the angle (degrees, 0..180) at vertex ``b`` formed by a-b-c.

    Returns ``None`` if either arm has zero length (degenerate / missing point).
    """
    v1 = (a[0] - b[0], a[1] - b[1])
    v2 = (c[0] - b[0], c[1] - b[1])
    n1 = math.hypot(v1[0], v1[1])
    n2 = math.hypot(v2[0], v2[1])
    if n1 == 0.0 or n2 == 0.0:
        return None
    cos_theta = (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    return math.degrees(math.acos(cos_theta))


class SquatRepCounter:
    """Stateful squat-rep state machine driven by per-frame knee angles."""

    def __init__(self, config: Optional[dict] = None):
        cfg = {**DEFAULTS, **(config or {})}
        self.target_reps = int(cfg["target_reps"])
        self.score_per_rep = int(cfg["score_per_rep"])
        self.knee_down_angle = float(cfg["knee_down_angle"])
        self.knee_up_angle = float(cfg["knee_up_angle"])
        self.window = max(1, int(cfg["smoothing_window"]))
        self.min_state_frames = max(1, int(cfg["min_state_frames"]))

        self._knee_hist = deque(maxlen=self.window)
        self.state = "UP"          # start standing
        self.reps = 0
        self.score = 0
        self.last_knee_angle: Optional[float] = None
        self.deepest_angle: Optional[float] = None   # min knee angle in current rep
        self._candidate: Optional[str] = None
        self._candidate_frames = 0

    def update(self, knee_angle: Optional[float],
               hip_angle: Optional[float] = None) -> dict:
        """Advance the state machine by one frame. Returns a status dict."""
        just_completed = False

        if knee_angle is not None:
            self._knee_hist.append(float(knee_angle))

        smoothed = (sum(self._knee_hist) / len(self._knee_hist)
                    if self._knee_hist else None)
        self.last_knee_angle = smoothed

        if smoothed is not None:
            if self.state == "DOWN":
                # track squat depth for form feedback
                self.deepest_angle = (smoothed if self.deepest_angle is None
                                      else min(self.deepest_angle, smoothed))

            if self.state == "UP":
                target = "DOWN" if smoothed <= self.knee_down_angle else None
            else:  # DOWN
                target = "UP" if smoothed >= self.knee_up_angle else None

            if target is None:
                self._candidate = None
                self._candidate_frames = 0
            else:
                if self._candidate == target:
                    self._candidate_frames += 1
                else:
                    self._candidate = target
                    self._candidate_frames = 1

                if self._candidate_frames >= self.min_state_frames:
                    if target == "DOWN":
                        self.state = "DOWN"
                        self.deepest_angle = smoothed
                    else:  # committed DOWN -> UP : one rep
                        self.state = "UP"
                        self.reps += 1
                        self.score += self.score_per_rep
                        just_completed = True
                    self._candidate = None
                    self._candidate_frames = 0

        return {
            "state": self.state,
            "reps": self.reps,
            "score": self.score,
            "target_reps": self.target_reps,
            "just_completed": just_completed,
            "goal_reached": self.reps >= self.target_reps,
            "knee_angle": smoothed,
            "feedback": self._feedback(just_completed),
        }

    def _feedback(self, just_completed: bool) -> str:
        if self.reps >= self.target_reps:
            return "GOAL!"
        if just_completed:
            return "GOOD!"
        if self.state == "DOWN":
            return "DOWN"
        return "UP"
