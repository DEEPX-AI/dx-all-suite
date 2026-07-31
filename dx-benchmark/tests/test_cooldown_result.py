"""Tests for wait_until_cool returning (final_temp, waited_sec)."""

from types import SimpleNamespace

import pytest

import benchmark.runner_pipeline as rp


def _cfg(**overrides):
    base = dict(
        thermal_idle_temp_c=40.0,
        thermal_cooldown_target_delta_c=10.0,
        thermal_cooldown_abs_cap_c=55.0,
        thermal_cooldown_max_sec=30.0,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_cooldown_immediate(monkeypatch):
    """Already cool: returns final temp and ~zero wait."""
    monkeypatch.setattr(rp, "read_npu_temp_c", lambda: 42.0)
    temp, waited = rp.wait_until_cool(_cfg())
    assert temp == 42.0
    assert 0.0 <= waited < 1.0


def test_cooldown_waits_then_returns(monkeypatch):
    """Hot at first, cools over successive polls: returns final temp + wait time."""
    temps = iter([60.0, 58.0, 45.0])
    monkeypatch.setattr(rp, "read_npu_temp_c", lambda: next(temps))
    monkeypatch.setattr(rp.time, "sleep", lambda s: None)
    temp, waited = rp.wait_until_cool(_cfg())
    assert temp == 45.0
    assert waited >= 0.0


def test_cooldown_no_sensor(monkeypatch):
    """Temperature unreadable: returns (-1.0, waited) without raising."""
    monkeypatch.setattr(rp, "read_npu_temp_c", lambda: None)
    temp, waited = rp.wait_until_cool(_cfg())
    assert temp == -1.0
    assert waited >= 0.0


def test_cooldown_timeout_raises(monkeypatch):
    """Never cools: still raises RuntimeError (abort/skip semantics unchanged)."""
    monkeypatch.setattr(rp, "read_npu_temp_c", lambda: 80.0)
    monkeypatch.setattr(rp.time, "sleep", lambda s: None)
    with pytest.raises(RuntimeError):
        rp.wait_until_cool(_cfg(thermal_cooldown_max_sec=0.2))
