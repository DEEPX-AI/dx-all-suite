"""Deterministic child-process environments for Studio App and Stream launches."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Mapping, Optional


class RuntimeEnvironmentError(RuntimeError):
    """Raised when an active runtime profile lacks launch-environment facts."""


_INHERITED_KEYS = (
    "HOME",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "TERM",
    "DISPLAY",
    "WAYLAND_DISPLAY",
    "XAUTHORITY",
    "XDG_RUNTIME_DIR",
)
_PROXY_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "no_proxy",
)


def _profile_path(profile: object, name: str) -> Path:
    value = getattr(profile, name, None)
    if value is None:
        raise RuntimeEnvironmentError("Active runtime profile is missing {}.".format(name))
    return Path(value)


def _profile_paths(profile: object, name: str) -> tuple[Path, ...]:
    values = getattr(profile, name, None)
    if not values:
        raise RuntimeEnvironmentError("Active runtime profile is missing {}.".format(name))
    return tuple(Path(value) for value in values)


def _is_child_path(path: str, parent: Optional[str]) -> bool:
    if not parent:
        return False
    try:
        Path(path).resolve().relative_to(Path(parent).resolve())
        return True
    except (OSError, ValueError):
        return False


def _sanitized_path(parent: Mapping[str, str], interpreter: Path) -> str:
    inherited_venv = parent.get("VIRTUAL_ENV")
    entries = [str(interpreter.parent)]
    entries.extend(
        entry
        for entry in parent.get("PATH", "").split(os.pathsep)
        if entry and not _is_child_path(entry, inherited_venv)
    )
    return os.pathsep.join(dict.fromkeys(entries))


def build_child_environment(
    profile: object,
    parent: Optional[Mapping[str, str]] = None,
) -> dict[str, str]:
    """Build an App/Stream child environment from an active Studio profile.

    The parent process contributes locale, display, home, and proxy settings only.
    Python, virtualenv, native-library, and GStreamer state must be declared by the
    profile, so a user's shell cannot inject a mismatched runtime.
    """
    source = os.environ if parent is None else parent
    interpreter = _profile_path(profile, "python_executable")
    venv_root = _profile_path(profile, "venv_root")
    library_dirs = _profile_paths(profile, "library_dirs")
    plugin_dir = _profile_path(profile, "plugin_dir")
    postprocess_lib_dir = _profile_path(profile, "postprocess_lib_dir")

    environment = {
        key: source[key]
        for key in _INHERITED_KEYS + _PROXY_KEYS
        if source.get(key)
    }
    environment.update(
        {
            "PATH": _sanitized_path(source, interpreter),
            "VIRTUAL_ENV": str(venv_root),
            "LD_LIBRARY_PATH": os.pathsep.join(str(path) for path in library_dirs),
            "GST_PLUGIN_PATH": str(plugin_dir),
            "DXSTREAM_POSTPROCESS_LIB_PATH": str(postprocess_lib_dir),
            "PYTHONNOUSERSITE": "1",
        }
    )
    return environment