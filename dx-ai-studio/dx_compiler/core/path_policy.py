"""Compile path policy: only real files and folders inside the allowed roots.

Checks the paths (model_path, config_path, qxnn_path, dataset_path, output_dir) taken by `/compile`,
`/compile/resume`, `/config/generate` and compiler_service.submit / submit_resume before anything runs.

- Allowed roots: suite root, studio `var/`, the user's home, `/media`, `/mnt`, plus ``DX_COMPILER_ALLOWED_ROOTS``
  (``os.pathsep``-separated). All are resolved before comparing.
- Containment is decided on the **components** of the resolved path (``Path.relative_to``), so ``/ws-evil`` is
  not under ``/ws``. Symlinks are resolved to their real location, so one pointing outside is rejected.
- Rejection messages never include server paths.

The server binds to all interfaces by default, so compile paths cannot rely on staying on localhost.

Contract: tests/dx_compiler/test_path_policy.py
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from shared.paths import STUDIO_ROOT, SUITE_ROOT


class PathPolicyError(ValueError):
    """Path is outside the policy; reported as HTTP 400."""


def _default_roots() -> list[Path]:
    roots = [SUITE_ROOT, STUDIO_ROOT / "var", Path.home(), Path("/media"), Path("/mnt")]
    return [r for r in roots if str(r)]


def _jobs_root() -> Path:
    env_root = os.environ.get("DX_COMPILER_JOB_ROOT", "").strip()   # same value as compiler_service
    return Path(env_root) if env_root else STUDIO_ROOT / "var" / "compiler" / "jobs"


def allowed_roots() -> list[Path]:
    extra = [Path(p) for p in os.environ.get("DX_COMPILER_ALLOWED_ROOTS", "").split(os.pathsep) if p.strip()]
    out = []
    for r in [*_default_roots(), *extra]:
        try:
            out.append(r.resolve())
        except (OSError, RuntimeError):
            continue
    return out


def _inside(path: Path, roots: Iterable[Path]) -> bool:
    for root in roots:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def _text(raw, field: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise PathPolicyError(f"{field} is required")
    if "\x00" in raw:
        raise PathPolicyError(f"{field} is not a valid path")
    return raw.strip()


def check_input_file(raw, field: str) -> Path:
    """An existing regular file inside the allowed roots; returns the resolved path."""
    try:
        p = Path(_text(raw, field)).expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        raise PathPolicyError(f"{field} does not exist") from None
    if not _inside(p, allowed_roots()):
        raise PathPolicyError(f"{field} is outside the allowed folders")
    if not p.is_file():
        raise PathPolicyError(f"{field} is not a file")
    return p


def check_input_dir(raw, field: str) -> Path:
    """An existing directory inside the allowed roots (dataset_path)."""
    try:
        p = Path(_text(raw, field)).expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        raise PathPolicyError(f"{field} does not exist") from None
    if not _inside(p, allowed_roots()):
        raise PathPolicyError(f"{field} is outside the allowed folders")
    if not p.is_dir():
        raise PathPolicyError(f"{field} is not a folder")
    return p


def check_output_dir(raw, field: str = "output_dir") -> Path:
    """A folder to write to. If it does not exist yet, check its nearest existing parent. Never creates it."""
    p = Path(_text(raw, field)).expanduser()
    if not p.is_absolute():
        p = Path.cwd() / p
    tail: list[str] = []
    cur = p
    while not cur.exists():
        if cur.parent == cur:
            raise PathPolicyError(f"{field} is not a valid path")
        tail.append(cur.name)
        cur = cur.parent
    try:
        base = cur.resolve(strict=True)
    except (OSError, RuntimeError):
        raise PathPolicyError(f"{field} is not a valid path") from None
    if not base.is_dir():
        raise PathPolicyError(f"{field} is not a folder")
    if any(part in ("..", ".") for part in tail):
        raise PathPolicyError(f"{field} is not a valid path")
    resolved = base.joinpath(*reversed(tail))
    roots = allowed_roots()
    if not _inside(base, roots) or not _inside(resolved, roots):
        raise PathPolicyError(f"{field} is outside the allowed folders")
    # The compiler's per-job internal folders (other jobs' outputs) are not valid output locations
    try:
        if _inside(resolved, [_jobs_root().resolve()]):
            raise PathPolicyError(f"{field} cannot be a compiler job folder")
    except (OSError, RuntimeError):
        pass
    return resolved


def would_overwrite_input(destination: Path, inputs: Iterable[str]) -> bool:
    """Would the published output land on an input file? (compared after resolving)"""
    try:
        dest = Path(destination).resolve()
    except (OSError, RuntimeError):
        return True
    for raw in inputs:
        if not raw:
            continue
        try:
            if Path(raw).resolve() == dest:
                return True
        except (OSError, RuntimeError):
            continue
    return False
