"""DX-APP 보안 헬퍼 — 경로/파일명 검증 유틸리티.

Phase 5 Task 1.1: Audit IDs 1-5, 18, 85-88
"""
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
    full = candidate.expanduser()
    if not full.is_absolute():
        full = root_abs / full
    if ".." in full.parts:
        return None
    try:
        full.relative_to(root_abs)
    except ValueError:
        return None
    return full


def resolve_under(path: str, roots: tuple[Path, ...]) -> Path:
    """경로를 해석하고 허용된 루트 목록 안에 있는지 검증.

    허용된 루트 자체 또는 그 하위 디렉토리/파일만 통과.
    """
    candidate = Path(path).expanduser()
    for root in roots:
        contained = _absolute_under_root(candidate, root)
        if contained is not None:
            return contained
    raise ValueError(f"Path is outside allowed roots: {path}")


def sanitize_filename(name: str, allowed_extensions: tuple[str, ...]) -> str:
    """업로드 파일명을 안전한 basename으로 정리.

    - 경로 구분자(/ \\)로 분리 후 마지막 요소만 사용
    - '.' 또는 '..' 만으로 된 이름 거부
    - 허용되지 않은 확장자 거부
    - 빈 이름 거부
    """
    if not name or not name.strip():
        raise ValueError("Filename must not be empty")

    # 경로 구분자 제거 → basename만 추출
    base = name.replace("\\", "/").split("/")[-1].strip()

    if not base or base in (".", ".."):
        raise ValueError(f"Invalid filename: {name}")

    # 확장자 검증
    ext = os.path.splitext(base)[1].lower()
    if ext not in allowed_extensions:
        raise ValueError(
            f"Extension '{ext}' not allowed. Allowed: {allowed_extensions}"
        )

    return base


def resolve_existing_file(path: str, roots: tuple[Path, ...],
                         allowed_extensions: tuple[str, ...] | None = None) -> Path:
    """경로를 해석하고 파일이 존재하며 허용된 확장자인지 검증."""
    candidate = resolve_under(path, roots)
    if not candidate.is_file():
        raise ValueError(f"File not found: {path}")
    if allowed_extensions and candidate.suffix.lower() not in allowed_extensions:
        raise ValueError(f"Extension '{candidate.suffix.lower()}' not allowed")
    return candidate


def resolve_existing_path(path: str, roots: tuple[Path, ...],
                          allowed_extensions: tuple[str, ...] | None = None) -> Path:
    """파일 또는 디렉터리를 해석/검증 (허용 루트 안에 존재해야 함).

    reid/embedding 데모는 이미지 쌍 디렉터리(sample/img/person_pair, face_pair)를
    입력으로 받으므로 디렉터리도 허용한다. 디렉터리는 확장자 검사를 건너뛰고,
    파일은 allowed_extensions를 적용한다. 경로 탈출 방지는 resolve_under가 담당.
    """
    candidate = resolve_under(path, roots)
    if not candidate.exists():
        raise ValueError(f"Path not found: {path}")
    if candidate.is_file() and allowed_extensions and candidate.suffix.lower() not in allowed_extensions:
        raise ValueError(f"Extension '{candidate.suffix.lower()}' not allowed")
    return candidate


def resolve_output_child(name: str, root: Path) -> Path:
    """출력 하위 경로를 해석하고 root 안에 있는지 검증."""
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
    """Content-Disposition 헤더 값을 안전하게 생성.

    파일명에서 경로 구분자를 제거하고, 따옴표를 이스케이프하여 인용.
    """
    # basename만 추출
    safe = filename.replace("\\", "/").split("/")[-1]
    if safe in (".", ".."):
        safe = "download"
    # 따옴표 이스케이프
    safe = safe.replace('"', '\\"')
    return f'{disposition}; filename="{safe}"'
