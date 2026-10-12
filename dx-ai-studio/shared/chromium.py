"""Find a Chromium for Playwright: the test gates and tools/release_audit.py use the same one.

Playwright's own headless-shell download may be missing on a board, so an explicit
DX_PLAYWRIGHT_EXECUTABLE or a system Chrome/Chromium is preferred.
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


def resolve_chromium_executable() -> str | None:
    """Return a usable explicit or system Chromium executable, if available."""
    override = os.environ.get("DX_PLAYWRIGHT_EXECUTABLE")
    candidates = [override] if override else []
    candidates.extend(shutil.which(name) for name in _CHROMIUM_CANDIDATES)

    for candidate in candidates:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    return None
