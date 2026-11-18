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

def _snap_browser(tmp_path: Path) -> Path:
    """A /snap/bin entry is a symlink to /usr/bin/snap; mimic that shape under tmp."""
    snap = _browser_file(tmp_path / "usr-bin-snap", executable=True)
    link = tmp_path / "snap" / "bin" / "chromium"
    link.parent.mkdir(parents=True)
    link.symlink_to(snap)
    return link


def test_snap_chromium_is_skipped_when_playwright_has_its_own(monkeypatch, tmp_path):
    """Snap confinement gives Chromium a private /tmp: file:// pages and downloads under pytest's tmp_path fail."""
    import shared.chromium as ch
    snap = _snap_browser(tmp_path)
    monkeypatch.delenv("DX_PLAYWRIGHT_EXECUTABLE", raising=False)
    monkeypatch.setattr(ch.shutil, "which", lambda name: str(snap) if name == "chromium" else None)
    monkeypatch.setattr(ch, "_is_snap", lambda path: path == str(snap))
    monkeypatch.setattr(ch, "_playwright_chromium_installed", lambda: True)
    assert resolve_chromium_executable() is None          # → Playwright launches its own Chromium


def test_snap_chromium_is_still_used_when_it_is_the_only_one(monkeypatch, tmp_path):
    import shared.chromium as ch
    snap = _snap_browser(tmp_path)
    monkeypatch.delenv("DX_PLAYWRIGHT_EXECUTABLE", raising=False)
    monkeypatch.setattr(ch.shutil, "which", lambda name: str(snap) if name == "chromium" else None)
    monkeypatch.setattr(ch, "_is_snap", lambda path: path == str(snap))
    monkeypatch.setattr(ch, "_playwright_chromium_installed", lambda: False)
    assert resolve_chromium_executable() == str(snap)


def test_is_snap_recognises_the_snap_launcher():
    import shared.chromium as ch
    assert ch._is_snap("/snap/bin/chromium")
    assert not ch._is_snap("/usr/bin/google-chrome")


def test_playwright_install_is_found_in_its_browsers_path(monkeypatch, tmp_path):
    import shared.chromium as ch
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", str(tmp_path))
    assert ch._playwright_chromium_installed() is False
    d = tmp_path / "chromium_headless_shell-1254"
    (d / "chrome-headless-shell-linux-arm64").mkdir(parents=True)
    assert ch._playwright_chromium_installed() is False   # an interrupted download is not an install
    (d / "INSTALLATION_COMPLETE").write_text("")
    assert ch._playwright_chromium_installed() is True
