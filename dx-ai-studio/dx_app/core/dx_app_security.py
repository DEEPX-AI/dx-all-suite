"""DX-APP security helpers: path and filename validation."""
from __future__ import annotations

import os
from pathlib import Path


def _absolute_under_root(candidate: Path, root: Path) -> Path | None:
    """Return absolute candidate path if it is lexically under root (no symlink follow).

    Symlinks under an allowed root (e.g. assets/videos/*.mp4 → workspace/) must pass
    validation even when the symlink target resolves outside the root.
    Path traversal via ``..`` is rejected.
    """
    root_abs = root.expanduser().resolve()
    # The root as written, too: when the root itself is reached through a symlink (a suite whose
    # dx_app links to an SDK checkout elsewhere) callers build paths under the link, which are
    # not lexically under the resolved target.
    root_lexical = Path(os.path.abspath(root.expanduser()))
    full = candidate.expanduser()
    if not full.is_absolute():
        full = root_abs / full
    if ".." in full.parts:
        return None
    for base in (root_abs, root_lexical):
        try:
            full.relative_to(base)
        except ValueError:
            continue
        return full
    return None


def resolve_under(path: str, roots: tuple[Path, ...]) -> Path:
    """Resolve a path and check that it lies inside one of the allowed roots.

    Only an allowed root itself or a directory/file below it passes.
    """
    candidate = Path(path).expanduser()
    for root in roots:
        contained = _absolute_under_root(candidate, root)
        if contained is not None:
            return contained
    raise ValueError(f"Path is outside allowed roots: {path}")


def sanitize_filename(name: str, allowed_extensions: tuple[str, ...]) -> str:
    """Reduce an uploaded filename to a safe basename.

    - split on path separators (/ \\) and keep only the last part
    - reject names made only of '.' or '..'
    - reject extensions that are not allowed
    - reject empty names
    """
    if not name or not name.strip():
        raise ValueError("Filename must not be empty")

    # Drop path separators -> keep only the basename
    base = name.replace("\\", "/").split("/")[-1].strip()

    if not base or base in (".", ".."):
        raise ValueError(f"Invalid filename: {name}")

    # Check the extension
    ext = os.path.splitext(base)[1].lower()
    if ext not in allowed_extensions:
        raise ValueError(
            f"Extension '{ext}' not allowed. Allowed: {allowed_extensions}"
        )

    return base


def resolve_existing_file(path: str, roots: tuple[Path, ...],
                         allowed_extensions: tuple[str, ...] | None = None) -> Path:
    """Resolve a path and check that the file exists and has an allowed extension."""
    candidate = resolve_under(path, roots)
    if not candidate.is_file():
        raise ValueError(f"File not found: {path}")
    if allowed_extensions and candidate.suffix.lower() not in allowed_extensions:
        raise ValueError(f"Extension '{candidate.suffix.lower()}' not allowed")
    return candidate


def resolve_existing_path(path: str, roots: tuple[Path, ...],
                          allowed_extensions: tuple[str, ...] | None = None) -> Path:
    """Resolve and check a file or directory (must exist inside an allowed root).

    The reid/embedding demos take image-pair directories (sample/img/person_pair, face_pair) as input,
    so directories are allowed. Directories skip the extension check; files get allowed_extensions.
    resolve_under prevents path escapes.
    """
    candidate = resolve_under(path, roots)
    if not candidate.exists():
        raise ValueError(f"Path not found: {path}")
    if candidate.is_file() and allowed_extensions and candidate.suffix.lower() not in allowed_extensions:
        raise ValueError(f"Extension '{candidate.suffix.lower()}' not allowed")
    return candidate


def resolve_output_child(name: str, root: Path) -> Path:
    """Resolve an output sub-path and check that it lies inside root."""
    if not name or not str(name).strip():
        raise ValueError("Output directory must not be empty")
    raw = Path(str(name))
    if raw.is_absolute() or ".." in raw.parts:
        raise ValueError("Output path must stay under compiler output directory")
    candidate = (root / raw).resolve()
    resolved_root = root.resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise ValueError("Output path is outside allowed root")
    return candidate


def existing_onnx(path: str, roots: tuple[Path, ...]) -> Path:
    return resolve_existing_file(path, roots, (".onnx",))


def existing_dxnn(path: str, roots: tuple[Path, ...]) -> Path:
    return resolve_existing_file(path, roots, (".dxnn",))


def existing_json(path: str, roots: tuple[Path, ...]) -> Path:
    return resolve_existing_file(path, roots, (".json",))


def safe_content_disposition(disposition: str, filename: str) -> str:
    """Build a safe Content-Disposition header value.

    Removes path separators from the filename and quotes it with quotes escaped.
    """
    # Keep only the basename
    safe = filename.replace("\\", "/").split("/")[-1]
    if safe in (".", ".."):
        safe = "download"
    # Escape quotes
    safe = safe.replace('"', '\\"')
    return f'{disposition}; filename="{safe}"'
