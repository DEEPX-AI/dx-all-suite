# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""Unit tests for the pure squat game logic (no NPU / OpenCV needed)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from factory.squat_logic import SquatCounter, compute_angle


def test_compute_angle_straight_leg():
    # hip above knee, ankle below knee -> straight (180 deg)
    assert abs(compute_angle((0, 0), (0, 10), (0, 20)) - 180.0) < 1e-3


def test_compute_angle_right_angle():
    # 90 degrees at the knee vertex
    assert abs(compute_angle((0, 0), (0, 10), (10, 10)) - 90.0) < 1e-3


def test_compute_angle_degenerate_returns_none():
    assert compute_angle((0, 0), (0, 0), (1, 1)) is None


def test_single_full_squat_counts_one():
    c = SquatCounter(stand_angle=160, squat_angle=100)
    assert c.update(175) is False          # standing
    assert c.update(90) is False           # went down (no count yet)
    assert c.update(170) is True           # stood back up -> +1
    assert c.count == 1
    assert c.state == SquatCounter.UP


def test_three_reps():
    c = SquatCounter()
    for _ in range(3):
        c.update(175)
        c.update(85)
        c.update(170)
    assert c.count == 3


def test_hysteresis_no_double_count_in_midrange():
    # bouncing in the mid-range (between squat and stand) must not add reps
    c = SquatCounter(stand_angle=160, squat_angle=100)
    c.update(175)            # UP
    c.update(95)             # DOWN
    assert c.update(130) is False   # mid-range, still DOWN, no count
    assert c.update(135) is False
    assert c.count == 0
    assert c.update(165) is True    # finally stands -> +1
    assert c.count == 1


def test_partial_squat_not_counted():
    # never reaches squat depth -> no rep
    c = SquatCounter(stand_angle=160, squat_angle=100)
    c.update(175)
    c.update(120)            # not deep enough (>100)
    c.update(175)
    assert c.count == 0


def test_none_reading_holds_state():
    c = SquatCounter()
    c.update(175)            # UP
    c.update(90)             # DOWN
    assert c.update(None) is False   # dropout — hold
    assert c.state == SquatCounter.DOWN
    assert c.update(170) is True     # recovers and completes the rep
    assert c.count == 1


def test_invalid_thresholds_raise():
    try:
        SquatCounter(stand_angle=100, squat_angle=160)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_depth_pct_bounds():
    c = SquatCounter(stand_angle=160, squat_angle=100)
    assert c.depth_pct(160) == 0.0      # standing -> 0%
    assert c.depth_pct(100) == 100.0    # deepest -> 100%
    assert c.depth_pct(200) == 0.0      # clamped
    assert c.depth_pct(50) == 100.0     # clamped
