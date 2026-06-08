#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Unit tests for the pure SquatRepCounter state machine.

Runs with pytest OR standalone:  python test_squat_rep_counter.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from squat_rep_counter import compute_angle, SquatRepCounter


# ---------------------------------------------------------------- angle math

def test_compute_angle_right_angle():
    # vertex at origin, arms along +y and +x -> 90 degrees
    ang = compute_angle((0.0, 1.0), (0.0, 0.0), (1.0, 0.0))
    assert ang is not None and abs(ang - 90.0) < 1e-6, ang


def test_compute_angle_straight():
    # straight line -> 180 degrees
    ang = compute_angle((0.0, 1.0), (0.0, 0.0), (0.0, -1.0))
    assert ang is not None and abs(ang - 180.0) < 1e-6, ang


def test_compute_angle_degenerate_returns_none():
    assert compute_angle((0.0, 0.0), (0.0, 0.0), (1.0, 0.0)) is None


# ---------------------------------------------------- rep counting behaviour

_CFG = {"knee_down_angle": 140.0, "knee_up_angle": 160.0,
        "smoothing_window": 5, "min_state_frames": 3,
        "target_reps": 10, "score_per_rep": 10}


def _feed(counter, angle, n):
    last = None
    for _ in range(n):
        last = counter.update(angle, hip_angle=angle)
    return last


def test_single_full_cycle_counts_one_rep():
    c = SquatRepCounter(_CFG)
    _feed(c, 172.0, 8)          # standing
    _feed(c, 128.0, 8)          # squat down
    res = _feed(c, 172.0, 8)    # stand up -> rep
    assert res["reps"] == 1, res
    assert res["score"] == 10, res
    assert res["state"] == "UP", res


def test_three_cycles_count_three():
    c = SquatRepCounter(_CFG)
    for _ in range(3):
        _feed(c, 170.0, 8)
        _feed(c, 125.0, 8)
    res = _feed(c, 170.0, 8)
    assert res["reps"] == 3, res


def test_partial_squat_does_not_count():
    # only dips to 150 (between down=140 and up=160) -> never reaches DOWN
    c = SquatRepCounter(_CFG)
    _feed(c, 172.0, 8)
    _feed(c, 150.0, 8)
    res = _feed(c, 172.0, 8)
    assert res["reps"] == 0, res


def test_jitter_near_threshold_does_not_double_count():
    c = SquatRepCounter(_CFG)
    _feed(c, 172.0, 8)
    _feed(c, 125.0, 8)
    _feed(c, 172.0, 8)          # 1 rep committed
    # now jitter right around the up threshold while already standing
    for a in [158.0, 162.0, 159.0, 161.0, 158.0, 162.0]:
        res = c.update(a, hip_angle=a)
    assert res["reps"] == 1, res


def test_brief_noise_during_down_does_not_prematurely_count():
    # debounce: a single stray "up" frame mid-squat must not commit a rep
    c = SquatRepCounter(_CFG)
    _feed(c, 172.0, 8)
    _feed(c, 125.0, 8)          # solidly DOWN
    c.update(165.0, hip_angle=165.0)   # one noisy frame only (< min_state_frames)
    res = _feed(c, 125.0, 6)           # back down
    assert res["reps"] == 0, res
    assert res["state"] == "DOWN", res


def test_goal_feedback_at_target():
    cfg = dict(_CFG, target_reps=2)
    c = SquatRepCounter(cfg)
    for _ in range(2):
        _feed(c, 170.0, 8)
        _feed(c, 125.0, 8)
    res = _feed(c, 170.0, 8)
    assert res["reps"] == 2, res
    assert res["goal_reached"] is True, res
    assert res["feedback"] == "GOAL!", res


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS: {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL: {fn.__name__}: {e}")
        except Exception as e:  # noqa
            failed += 1
            print(f"ERROR: {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
