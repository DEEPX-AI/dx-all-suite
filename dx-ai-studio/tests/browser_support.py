"""Shared browser selection for DX AI Studio test gates."""
from __future__ import annotations

import os
from pathlib import Path
import shutil

from shared.chromium import resolve_chromium_executable  # noqa: F401  (re-exported for the suites)


def resolve_node_executable() -> str | None:
    """Return a Node.js binary: the one on PATH, else the one Playwright ships with.

    The Node harness tests (widget, i18n runtime, telemetry states, markdown render ...) used to skip
    whenever ``node`` was not on PATH, which is the normal state of this box, so six of them broke
    without anyone seeing it (found 2026-10-11). Playwright is a test dependency and carries its
    own Node, so those tests can always run.
    """
    found = shutil.which("node")
    if found:
        return found
    try:
        import playwright
    except ImportError:
        return None
    bundled = Path(playwright.__file__).resolve().parent / "driver" / "node"
    return str(bundled) if bundled.is_file() and os.access(bundled, os.X_OK) else None


# --- Multi-engine selection (Phase 2 cross-browser) -------------------------

ENGINES = ("chromium", "firefox", "webkit")
DEFAULT_ENGINE = "chromium"
_ENGINES_ENV = "DX_BROWSER_ENGINES"


def selected_engines() -> tuple[str, ...]:
    """Engines to run browser suites against.

    Defaults to chromium alone so the BLOCKING gate stays fast and single-engine.
    The cross-browser job opts in with ``DX_BROWSER_ENGINES=chromium,firefox``.
    Unknown names are rejected loudly — a typo that silently ran nothing would be
    worse than a failure.
    """
    raw = os.environ.get(_ENGINES_ENV, "").strip()
    if not raw:
        return (DEFAULT_ENGINE,)
    names = tuple(n.strip().lower() for n in raw.split(",") if n.strip())
    unknown = [n for n in names if n not in ENGINES]
    if unknown:
        raise ValueError(f"{_ENGINES_ENV} has unknown engine(s) {unknown}; known: {list(ENGINES)}")
    return names or (DEFAULT_ENGINE,)


def launch_browser(playwright, engine: str, **kwargs):
    """Launch ``engine``, reusing a host Chromium when Playwright has no cache.

    Only chromium gets the system-binary fallback: Playwright ships PATCHED
    Firefox/WebKit builds, so a distro firefox is not a substitute and pointing
    executable_path at one produces confusing protocol errors rather than a clean
    "not installed" message.
    """
    if engine not in ENGINES:
        raise ValueError(f"unknown engine {engine!r}; known: {list(ENGINES)}")
    if engine == "chromium":
        executable = resolve_chromium_executable()
        if executable:
            kwargs.setdefault("executable_path", executable)
    return getattr(playwright, engine).launch(headless=True, **kwargs)
