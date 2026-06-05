"""Unit tests for the pure-Python squat rep core (no NPU dependency)."""
import pytest

from squat_game.squat_counter import compute_angle, SquatCounter


def test_straight_leg_is_180():
    # hip, knee, ankle perfectly collinear and vertical -> 180 deg
    assert compute_angle((0, 0), (0, 1), (0, 2)) == pytest.approx(180.0, abs=1e-3)


def test_right_angle_is_90():
    assert compute_angle((0, 0), (0, 1), (1, 1)) == pytest.approx(90.0, abs=1e-3)


def test_degenerate_zero_length_returns_180():
    # coincident points must not crash; treated as "straight"
    assert compute_angle((0, 0), (0, 0), (0, 0)) == pytest.approx(180.0, abs=1e-3)


def test_one_full_squat_counts_one_rep():
    c = SquatCounter(down_angle=140.0, up_angle=160.0)
    for a in [175, 170, 150, 135, 130, 138, 155, 165, 175]:
        c.update(a)
    assert c.reps == 1
    assert c.state == "UP"


def test_two_full_squats_count_two_reps():
    c = SquatCounter(down_angle=140.0, up_angle=160.0)
    seq = [175, 130, 175, 130, 175]  # two clean descents + recoveries
    for a in seq:
        c.update(a)
    assert c.reps == 2


def test_jitter_in_deadband_does_not_double_count():
    c = SquatCounter(down_angle=140.0, up_angle=160.0)
    for a in [175, 130, 165, 158, 162, 159, 161, 175]:
        c.update(a)
    assert c.reps == 1


def test_shallow_dip_above_down_threshold_counts_zero():
    c = SquatCounter(down_angle=140.0, up_angle=160.0)
    for a in [175, 150, 145, 150, 175]:  # never crosses 140
        c.update(a)
    assert c.reps == 0


def test_update_returns_true_only_on_completion():
    c = SquatCounter(down_angle=140.0, up_angle=160.0)
    completions = [c.update(a) for a in [175, 130, 175]]
    assert completions == [False, False, True]
    assert c.just_completed is True


def test_none_angle_is_ignored():
    c = SquatCounter(down_angle=140.0, up_angle=160.0)
    for a in [175, None, 130, None, 175]:
        c.update(a)
    assert c.reps == 1


def test_invalid_thresholds_raise():
    with pytest.raises(ValueError):
        SquatCounter(down_angle=160.0, up_angle=140.0)
