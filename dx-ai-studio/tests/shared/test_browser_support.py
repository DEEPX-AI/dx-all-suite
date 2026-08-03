"""Regression tests for the centralized Playwright browser resolver."""
from pathlib import Path

from tests.browser_support import resolve_chromium_executable


def _browser_file(path: Path, executable: bool) -> Path:
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(0o755 if executable else 0o644)
    return path


def test_explicit_executable_override_has_priority(monkeypatch, tmp_path):
    override = _browser_file(tmp_path / "custom-chrome", executable=True)
    monkeypatch.setenv("DX_PLAYWRIGHT_EXECUTABLE", str(override))
    monkeypatch.setattr("tests.browser_support.shutil.which", lambda _name: None)

    assert resolve_chromium_executable() == str(override)


def test_non_executable_override_falls_through_to_system_browser(monkeypatch, tmp_path):
    override = _browser_file(tmp_path / "custom-chrome", executable=False)
    system_browser = _browser_file(tmp_path / "google-chrome", executable=True)
    monkeypatch.setenv("DX_PLAYWRIGHT_EXECUTABLE", str(override))
    monkeypatch.setattr(
        "tests.browser_support.shutil.which",
        lambda name: str(system_browser) if name == "google-chrome" else None,
    )

    assert resolve_chromium_executable() == str(system_browser)


def test_missing_candidates_return_none(monkeypatch):
    monkeypatch.delenv("DX_PLAYWRIGHT_EXECUTABLE", raising=False)
    monkeypatch.setattr("tests.browser_support.shutil.which", lambda _name: None)

    assert resolve_chromium_executable() is None