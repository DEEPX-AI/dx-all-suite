#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Unit tests for squat-game pure logic (angle math + rep FSM).

These tests intentionally import ONLY ``factory.squat_logic`` — no cv2,
no dx_engine, no NPU — so the squat-detection logic can be validated in
isolation (TDD Red/Green).

Run:
    python -m pytest test_squat_logic.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from factory.squat_logic import angle_3pt, SquatCounter


# ----------------------------------------------------------------------
# angle_3pt
# ----------------------------------------------------------------------

def test_angle_straight_is_180():
    # Vertical straight leg: hip above, knee mid, ankle below -> ~180 deg
    hip = (100.0, 100.0)
    knee = (100.0, 200.0)
    ankle = (100.0, 300.0)
    assert abs(angle_3pt(hip, knee, ankle) - 180.0) < 1e-3


def test_angle_right_is_90():
    # Right angle at the knee vertex
    hip = (100.0, 100.0)
    knee = (100.0, 200.0)
    ankle = (200.0, 200.0)
    assert abs(angle_3pt(hip, knee, ankle) - 90.0) < 1e-3


def test_angle_acute():
    hip = (100.0, 100.0)
    knee = (100.0, 200.0)
    ankle = (150.0, 110.0)
    a = angle_3pt(hip, knee, ankle)
    assert 0.0 < a < 90.0


def test_angle_degenerate_returns_180():
    # Coincident points must not crash; treat as fully extended
    p = (50.0, 50.0)
    assert angle_3pt(p, p, p) == 180.0


# ----------------------------------------------------------------------
# SquatCounter FSM
# ----------------------------------------------------------------------

def _feed(counter, knee_seq, hip_angle=120.0):
    reps_completed = 0
    states = []
    for k in knee_seq:
        state, completed = counter.update(k, hip_angle)
        states.append(state)
        if completed:
            reps_completed += 1
    return reps_completed, states


def test_single_rep_counted():
    c = SquatCounter(knee_down=140.0, knee_up=160.0, hip_down=150.0)
    # stand -> squat -> stand  (one full rep)
    reps, _ = _feed(c, [175, 170, 135, 130, 138, 165, 172])
    assert reps == 1
    assert c.reps == 1


def test_no_dip_no_rep():
    c = SquatCounter(knee_down=140.0, knee_up=160.0, hip_down=150.0)
    reps, _ = _feed(c, [175, 172, 168, 170, 174])  # never dips below down
    assert reps == 0


def test_hysteresis_blocks_double_count():
    c = SquatCounter(knee_down=140.0, knee_up=160.0, hip_down=150.0)
    # one dip, then jitter in the dead-band (140..160) must NOT add reps
    reps, _ = _feed(c, [175, 130, 145, 150, 148, 152, 165, 158, 150, 155])
    assert reps == 1  # only the 130->165 transition counts


def test_three_reps():
    c = SquatCounter(knee_down=140.0, knee_up=160.0, hip_down=150.0)
    seq = []
    for _ in range(3):
        seq += [175, 130, 165]  # down then up
    reps, _ = _feed(c, seq)
    assert reps == 3


def test_hip_gate_blocks_down_when_hip_not_flexed():
    # If hip angle stays large (not flexed past hip_down), a knee dip should
    # NOT register as a squat (guards against e.g. sitting/leaning artifacts).
    c = SquatCounter(knee_down=140.0, knee_up=160.0, hip_down=150.0)
    reps, states = _feed(c, [175, 130, 165], hip_angle=175.0)  # hip never flexes
    assert reps == 0
    assert "DOWN" not in states


def test_starts_in_up_state():
    c = SquatCounter(knee_down=140.0, knee_up=160.0, hip_down=150.0)
    assert c.state == "UP"
    assert c.reps == 0


if __name__ == "__main__":
    import pytest
    raise SystemExit(pytest.main([__file__, "-v"]))
