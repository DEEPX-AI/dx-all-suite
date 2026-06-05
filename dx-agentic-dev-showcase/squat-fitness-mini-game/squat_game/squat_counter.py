"""Pure-Python squat rep counter (no NPU / OpenCV dependency).

Kept import-free of dx_engine so the core logic is unit-testable on any host.
"""
import math
from typing import Optional, Sequence


def compute_angle(a: Sequence[float], b: Sequence[float], c: Sequence[float]) -> float:
    """Interior angle ABC (degrees) at vertex ``b``, clamped to [0, 180].

    Used for joint angles such as the knee ``angle(hip, knee, ankle)`` or the
    hip ``angle(shoulder, hip, knee)``. Degenerate (zero-length) limbs return
    180.0 so a missing/coincident keypoint reads as "straight", never crashes.
    """
    bax, bay = a[0] - b[0], a[1] - b[1]
    bcx, bcy = c[0] - b[0], c[1] - b[1]
    na = math.hypot(bax, bay)
    nc = math.hypot(bcx, bcy)
    if na == 0.0 or nc == 0.0:
        return 180.0
    cos = (bax * bcx + bay * bcy) / (na * nc)
    cos = max(-1.0, min(1.0, cos))
    return math.degrees(math.acos(cos))


class SquatCounter:
    """Hysteresis rep counter driven by a single joint (knee) angle.

    State machine::

        UP   --(angle < down_angle)-->  DOWN
        DOWN --(angle > up_angle)----->  UP   (rep += 1)

    The ``down_angle < up_angle`` dead-band rejects jitter so hovering near a
    single threshold cannot double-count. Defaults are calibrated for 2D
    YOLO-pose knee angles, which bottom out near 120-140 deg (NOT the textbook
    90 deg) due to camera projection.
    """

    def __init__(self, down_angle: float = 140.0, up_angle: float = 160.0):
        if down_angle >= up_angle:
            raise ValueError(
                f"down_angle ({down_angle}) must be < up_angle ({up_angle})")
        self.down_angle = float(down_angle)
        self.up_angle = float(up_angle)
        self.state = "UP"
        self.reps = 0
        self.last_angle: Optional[float] = None
        self.just_completed = False

    def update(self, angle: Optional[float]) -> bool:
        """Feed a knee angle; return True iff a rep just completed this call.

        ``None`` (no confident pose this frame) is ignored: state and rep count
        are preserved so a brief detection dropout does not reset progress.
        """
        self.just_completed = False
        if angle is None:
            return False
        self.last_angle = angle
        if self.state == "UP" and angle < self.down_angle:
            self.state = "DOWN"
        elif self.state == "DOWN" and angle > self.up_angle:
            self.state = "UP"
            self.reps += 1
            self.just_completed = True
        return self.just_completed
