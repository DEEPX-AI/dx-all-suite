"""Find a Chromium for Playwright: the test gates and tools/release_audit.py use the same one.

Playwright's own headless-shell download may be missing on a board, so an explicit
DX_PLAYWRIGHT_EXECUTABLE or a system Chrome/Chromium is preferred. A snap-packaged Chromium
(Ubuntu's default) is the exception when Playwright has its own: snap confinement gives it a
private /tmp, so file:// pages and downloads under a temp dir fail.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

_CHROMIUM_CANDIDATES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
)


def _is_snap(path: str) -> bool:
    """/snap/bin/<app> is a symlink to /usr/bin/snap, which runs the app confined."""
    return path.startswith("/snap/") or os.path.basename(os.path.realpath(path)) == "snap"


def _playwright_chromium_installed() -> bool:
    """Playwright has finished downloading a Chromium (it writes INSTALLATION_COMPLETE last)."""
    root = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    base = Path(root) if root and root != "0" else Path.home() / ".cache" / "ms-playwright"
    try:
        return any((d / "INSTALLATION_COMPLETE").is_file()
                   for d in base.iterdir() if d.name.startswith(("chromium-", "chromium_headless_shell-")))
    except OSError:
        return False


def resolve_chromium_executable() -> str | None:
    """Return a usable explicit or system Chromium executable, or None to let Playwright use its own."""
    override = os.environ.get("DX_PLAYWRIGHT_EXECUTABLE")
    if override and Path(override).is_file() and os.access(override, os.X_OK):
        return override
    system = [c for c in (shutil.which(name) for name in _CHROMIUM_CANDIDATES)
              if c and Path(c).is_file() and os.access(c, os.X_OK)]
    unconfined = [c for c in system if not _is_snap(c)]
    if unconfined:
        return unconfined[0]
    if system and not _playwright_chromium_installed():
        return system[0]
    return None
