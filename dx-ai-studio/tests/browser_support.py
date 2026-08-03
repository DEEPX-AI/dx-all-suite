"""Shared browser selection for DX AI Studio test gates."""
from __future__ import annotations

import os
from pathlib import Path
import shutil


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