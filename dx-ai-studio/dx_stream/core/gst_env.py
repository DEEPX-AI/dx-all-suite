"""Unified DEEPX GStreamer plugin discovery + environment helpers.

Historically three call sites detected the ``dxstream`` plugin three different ways
(``core/status.py``, ``core/diagnostics.py``, ``core/demos.py``), each checking a
different path — so a plugin installed in a location one of them didn't know about read
as "not installed", and the pipeline run path never propagated ``GST_PLUGIN_PATH`` at all
(reported as "general GStreamer plugins not provided / pipeline unusable"). This module is
the single source of truth: it finds ``libgstdxstream.so`` across every known location and
produces an environment whose ``GST_PLUGIN_PATH`` includes the plugin directory so both the
in-process GI binding and the ``gst-launch-1.0`` subprocess can load it.
"""

import os
import logging
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

PLUGIN_SO = "libgstdxstream.so"

# Every directory any historical detector looked in, most-specific first.
_KNOWN_DIRS = (
    "/usr/local/lib/x86_64-linux-gnu/gstreamer-1.0",
    "/usr/local/lib/gstreamer-1.0",
    "/usr/lib/x86_64-linux-gnu/gstreamer-1.0",
    "/usr/lib/gstreamer-1.0",
)
# Broader trees to rglob as a last resort (bounded — only these roots).
_SEARCH_ROOTS = ("/usr/local/lib", "/usr/lib")


def find_dxstream_plugin(*, prefer_environment: bool = True) -> Optional[Path]:
    """Return the path to libgstdxstream.so, or None.

    By default an explicit ``GST_PLUGIN_PATH`` takes precedence so diagnostics can
    inspect a deployment-selected custom build. Canonical lookup skips inherited
    paths and resolves only installed locations for deterministic pre-GI startup.
    """
    if prefer_environment:
        for d in os.environ.get("GST_PLUGIN_PATH", "").split(os.pathsep):
            if d:
                p = Path(d) / PLUGIN_SO
                if p.exists():
                    return p
    for d in _KNOWN_DIRS:
        p = Path(d) / PLUGIN_SO
        if p.exists():
            return p
    for root in _SEARCH_ROOTS:
        try:
            hit = next(Path(root).rglob(PLUGIN_SO), None)
        except OSError as exc:
            log.warning("Unable to search GStreamer plugin root %s: %s", root, exc)
            hit = None
        if hit:
            return hit
    return None


def plugin_dir(*, prefer_environment: bool = True) -> Optional[str]:
    """Directory containing libgstdxstream.so, or None."""
    p = find_dxstream_plugin(prefer_environment=prefer_environment)
    return str(p.parent) if p else None


def plugin_available() -> bool:
    return find_dxstream_plugin() is not None


def augmented_env(base: Optional[dict] = None, *, prefer_environment: bool = True) -> dict:
    """Return a copy of *base* (default os.environ) with the dxstream plugin directory
    prepended to GST_PLUGIN_PATH, so gst-launch/GI can load it even when it lives outside
    the default registry path. Canonical mode replaces inherited plugin entries."""
    env = dict(os.environ if base is None else base)
    d = plugin_dir(prefer_environment=prefer_environment)
    if d:
        if not prefer_environment:
            env["GST_PLUGIN_PATH"] = d
            return env
        existing = env.get("GST_PLUGIN_PATH", "")
        parts = [d] + [x for x in existing.split(os.pathsep) if x and x != d]
        env["GST_PLUGIN_PATH"] = os.pathsep.join(parts)
    return env


def refresh_plugin_environment(gst=None, *, prefer_environment: bool = True) -> Optional[str]:
    """Refresh GST_PLUGIN_PATH and scan a plugin installed after GI initialization."""
    env = augmented_env(prefer_environment=prefer_environment)
    directory = plugin_dir(prefer_environment=prefer_environment)
    if not directory:
        return None

    os.environ["GST_PLUGIN_PATH"] = env["GST_PLUGIN_PATH"]
    if gst is not None:
        try:
            scanned = gst.Registry.get().scan_path(directory)
            element_factory = getattr(gst, "ElementFactory", None)
            dxinfer_factory = (
                element_factory.find("dxinfer")
                if element_factory is not None
                else None
            )
            if not scanned and dxinfer_factory is None:
                log.warning(
                    "GStreamer registry could not load dxinfer while scanning %s; "
                    "verify libgstdxstream.so and its dependencies",
                    directory,
                )
        except Exception:
            log.warning(
                "Unable to scan dxstream GStreamer plugin directory %s",
                directory,
                exc_info=True,
            )
    return directory
