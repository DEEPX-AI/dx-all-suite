# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Pure squat-detection logic — angle math + rep-counting FSM.

Kept dependency-light (only the stdlib ``math``) so it can be unit-tested in
isolation without cv2, dx_engine, or the NPU. The stateful game visualizer
(``squat_game_visualizer.py``) imports these primitives.
"""

import math
from typing import Sequence, Tuple


def angle_3pt(a: Sequence[float], b: Sequence[float], c: Sequence[float]) -> float:
    """Return the angle (degrees) at vertex ``b`` formed by points a-b-c.

    Used for the knee angle (hip-knee-ankle) and the hip angle
    (shoulder-hip-knee). Returns 180.0 for degenerate (coincident) inputs so a
    missing/overlapping joint reads as "fully extended" rather than crashing.
    """
    bax = a[0] - b[0]
    bay = a[1] - b[1]
    bcx = c[0] - b[0]
    bcy = c[1] - b[1]

    na = math.hypot(bax, bay)
    nc = math.hypot(bcx, bcy)
    if na == 0.0 or nc == 0.0:
        return 180.0

    cos_ang = (bax * bcx + bay * bcy) / (na * nc)
    cos_ang = max(-1.0, min(1.0, cos_ang))  # clamp for acos domain safety
    return math.degrees(math.acos(cos_ang))


class SquatCounter:
    """Two-state (UP/DOWN) squat repetition FSM with hysteresis.

    A rep is completed on a full DOWN->UP cycle. The knee angle drives the
    transitions; the hip angle is a corroborating gate so that a knee dip
    without a matching hip flexion (e.g. odd pose artifacts) is not counted.

    Args:
        knee_down: knee angle (deg) at/below which the user is considered DOWN.
        knee_up:   knee angle (deg) at/above which the user is considered UP.
                   Must be > ``knee_down`` to create a dead-band (hysteresis).
        hip_down:  if set, the hip angle must also be <= this value for a DOWN
                   transition to register. ``None`` disables the hip gate.
    """

    def __init__(self, knee_down: float, knee_up: float,
                 hip_down: float = None):
        if knee_up <= knee_down:
            raise ValueError(
                f"knee_up ({knee_up}) must be > knee_down ({knee_down}) "
                f"for hysteresis")
        self.knee_down = float(knee_down)
        self.knee_up = float(knee_up)
        self.hip_down = float(hip_down) if hip_down is not None else None
        self.state = "UP"
        self.reps = 0

    def update(self, knee_angle: float, hip_angle: float) -> Tuple[str, bool]:
        """Advance the FSM with the latest frame's angles.

        Returns ``(state, rep_just_completed)`` where ``state`` is "UP" or
        "DOWN" and ``rep_just_completed`` is True exactly on the frame that
        finishes a rep (the DOWN->UP transition).
        """
        if self.state == "UP":
            hip_ok = self.hip_down is None or hip_angle <= self.hip_down
            if knee_angle <= self.knee_down and hip_ok:
                self.state = "DOWN"
            return self.state, False

        # state == "DOWN"
        if knee_angle >= self.knee_up:
            self.state = "UP"
            self.reps += 1
            return self.state, True
        return self.state, False
