# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Squat game logic — pure, NPU-free, unit-testable.

`SquatCounter` is a hysteresis state machine that counts completed squats from a
stream of knee-angle measurements. `compute_angle` is the geometry helper that
turns three 2D joints (hip, knee, ankle) into the interior angle at the knee.

No OpenCV / dx_engine imports here on purpose — this module is fully testable
without hardware (see test_squat_logic.py).
"""

import math
from typing import Optional, Tuple

# COCO-17 keypoint indices (yolo26n-pose output order)
L_HIP, R_HIP = 11, 12
L_KNEE, R_KNEE = 13, 14
L_ANKLE, R_ANKLE = 15, 16

Point = Tuple[float, float]


def compute_angle(a: Point, b: Point, c: Point) -> Optional[float]:
    """Interior angle (degrees) at vertex ``b`` formed by segments b->a and b->c.

    Returns None if either segment has (near) zero length.
    """
    bax, bay = a[0] - b[0], a[1] - b[1]
    bcx, bcy = c[0] - b[0], c[1] - b[1]
    na = math.hypot(bax, bay)
    nc = math.hypot(bcx, bcy)
    if na < 1e-6 or nc < 1e-6:
        return None
    cos_v = (bax * bcx + bay * bcy) / (na * nc)
    cos_v = max(-1.0, min(1.0, cos_v))
    return math.degrees(math.acos(cos_v))


class SquatCounter:
    """Counts squats from a sequence of knee-angle readings.

    State machine (with hysteresis to prevent jitter double-counting):
      - UP   (standing):  knee angle >= ``stand_angle``
      - DOWN (squatting): knee angle <= ``squat_angle``
      - A rep is counted on the DOWN -> UP transition (one full squat).

    A ``None`` reading (no/low-confidence keypoints for the frame) holds the
    current state and does not change the count — robust to brief dropouts.
    """

    UP = "UP"
    DOWN = "DOWN"

    def __init__(self, stand_angle: float = 160.0, squat_angle: float = 100.0):
        if squat_angle >= stand_angle:
            raise ValueError("squat_angle must be < stand_angle")
        self.stand_angle = float(stand_angle)
        self.squat_angle = float(squat_angle)
        self.count = 0
        self.state = self.UP
        self.last_angle: Optional[float] = None

    def update(self, knee_angle: Optional[float]) -> bool:
        """Feed one knee-angle reading. Returns True iff a rep was just counted."""
        if knee_angle is None:
            return False
        self.last_angle = float(knee_angle)
        if self.state == self.UP:
            if knee_angle <= self.squat_angle:
                self.state = self.DOWN
            return False
        # state == DOWN
        if knee_angle >= self.stand_angle:
            self.state = self.UP
            self.count += 1
            return True
        return False

    def depth_pct(self, knee_angle: Optional[float] = None) -> float:
        """Map knee angle to a 0..100 squat-depth percentage (100 = deepest)."""
        angle = self.last_angle if knee_angle is None else knee_angle
        if angle is None:
            return 0.0
        span = self.stand_angle - self.squat_angle
        pct = (self.stand_angle - angle) / span * 100.0
        return max(0.0, min(100.0, pct))
