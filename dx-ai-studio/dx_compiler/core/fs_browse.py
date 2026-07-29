"""Safe server-side directory browsing for the Output Directory picker.

Pure functions (no HTTP) so they are unit-testable; server.py exposes them as
GET /api/listdir and POST /api/mkdir. All access is constrained by
config.is_safe_path (allowed roots: /home, /tmp, /data, /mnt, /opt + upload dir),
since the compiler UI is a localhost tool operating on the user's own machine.
"""
from __future__ import annotations

import os
from pathlib import Path

from dx_compiler.core.config import is_safe_path


def _default_start() -> str:
    """A safe, existing directory to open the browser at when no path is given."""
    candidates = []
    try:
        candidates.append(Path.home())
    except (RuntimeError, OSError):
        pass
    candidates += [Path("/home"), Path("/tmp")]
    for c in candidates:
        try:
            if c.is_dir() and is_safe_path(str(c)):
                return str(c)
        except OSError:
            continue
    return "/tmp"


def list_directory(path: str | None, file_ext: str | None = None) -> dict:
    """List immediate sub-directories of *path*.

    Returns {ok, path, parent, dirs, files, writable}. Raises ValueError for an
    unsafe, missing, or non-directory path. When *file_ext* is given (e.g.
    ".json"), regular files with that extension are also returned in ``files``
    (case-insensitive); otherwise ``files`` is empty (folder-only picker).
    """
    if not path:
        path = _default_start()
    if not is_safe_path(path):
        raise ValueError("unsafe path")
    p = Path(path).resolve()
    if not p.is_dir():
        raise ValueError("not a directory")

    ext = file_ext.lower() if file_ext else None
    dirs: list[str] = []
    files: list[str] = []
    try:
        children = sorted(p.iterdir(), key=lambda c: c.name.lower())
    except (PermissionError, OSError) as exc:
        raise ValueError("cannot read directory") from exc
    for child in children:
        try:
            if child.name.startswith("."):
                continue  # hide dotfiles/dirs
            if child.is_dir():
                dirs.append(child.name)
            elif ext and child.is_file() and child.name.lower().endswith(ext):
                files.append(child.name)
        except OSError:
            continue  # unreadable entry — skip, don't fail the whole listing

    parent = p.parent
    parent_str = str(parent) if (parent != p and is_safe_path(str(parent))) else None

    return {
        "ok": True,
        "path": str(p),
        "parent": parent_str,
        "dirs": dirs,
        "files": files,
        "writable": os.access(str(p), os.W_OK),
    }


def make_directory(parent: str, name: str) -> dict:
    """Create sub-directory *name* under *parent*. Returns {ok, path}.

    Raises ValueError for an unsafe parent or an invalid name (empty, dotfile,
    containing a path separator, or attempting traversal).
    """
    if not parent or not is_safe_path(parent):
        raise ValueError("unsafe parent")
    if (not name or name in (".", "..") or name.startswith(".")
            or "/" in name or "\\" in name):
        raise ValueError("invalid name")

    base = Path(parent).resolve()
    if not base.is_dir():
        raise ValueError("parent not a directory")

    target = (base / name).resolve()
    # target must stay directly under base (defence in depth vs. traversal)
    if target.parent != base or not is_safe_path(str(target)):
        raise ValueError("invalid target")

    target.mkdir(parents=False, exist_ok=True)
    return {"ok": True, "path": str(target)}
