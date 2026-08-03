"""Tests for profile-based inference launch policy."""
from types import SimpleNamespace


def test_launcher_blocks_inference_modules_without_active_profile(monkeypatch):
    from launcher import launcher

    blocked = SimpleNamespace(allowed=False, reason=SimpleNamespace(check_id="profile.active"))
    monkeypatch.setattr(launcher, "_runtime_module_start_policy", lambda module: blocked)

    status = launcher.module_start_policy("dx_stream")

    assert status.allowed is False
    assert status.reason.check_id == "profile.active"


def test_launcher_allows_non_inference_modules_without_runtime_profile(monkeypatch):
    from launcher import launcher

    allowed = SimpleNamespace(allowed=True, reason=None)
    monkeypatch.setattr(launcher, "_runtime_module_start_policy", lambda module: allowed)

    assert launcher.module_start_policy("dx_modelzoo").allowed is True