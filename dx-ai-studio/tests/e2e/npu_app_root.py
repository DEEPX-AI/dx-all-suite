"""Resolve a real ``DX_APP_ROOT`` for the NPU tier of the inference triple gate.

Two shapes are supported, in order:

1. **Installed tree** — the model named by ``DX_E2E_NPU_MODEL`` is already under
   ``dx-runtime/dx_app/assets/models/``, i.e. the machine ran dx_app's setup.sh.
   The real root is used unchanged; nothing is created.
2. **Overlay** — the model lives elsewhere (``DX_E2E_NPU_MODEL_FILE``, e.g. a
   ModelZoo download cache). A throwaway root is built from symlinks to the real
   bin/src/config/sample plus an ``assets/models/`` holding just that model.

The overlay exists because ``dx_app/assets/`` is root-owned on a provisioned
board: dropping a model in requires sudo, and a test must not need it — nor
should it mutate the runtime tree to run.

Returns None when the prerequisites are absent, so the tier skips rather than
failing on a machine without an NPU or a model.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

NPU_DEVICE = Path("/dev/dxrt0")
_MODEL_ENV = "DX_E2E_NPU_MODEL"
_MODEL_FILE_ENV = "DX_E2E_NPU_MODEL_FILE"

# Symlinked wholesale into the overlay; each is read-only from the studio's side.
_LINKED_TOP_LEVEL = ("bin", "src", "config", "sample", "scripts")


def _real_root() -> Path:
    from shared.paths import SUITE_ROOT

    return SUITE_ROOT / "dx-runtime" / "dx_app"


def registry_lookup(real_root: Path, model_name: str) -> str | None:
    """model_file for *model_name* from dx_app's test_models.conf, or None.

    *model_name* is the name /api/models and the picker show — the conf's 4th column
    (``yolo26-n_640x640``). The 1st column is a family shared by many rows
    (``yolo26`` → l, m, n, s, x), so it cannot name one model.
    """
    conf = real_root / "config" / "test_models.conf"
    if not conf.is_file():
        return None
    for line in conf.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("\t")]
        if len(parts) >= 4 and parts[3] == model_name:
            return parts[2]
    return None


def _build_overlay(real_root: Path, model_file: str, dxnn: Path) -> Path:
    root = Path(tempfile.mkdtemp(prefix="dx-e2e-npu-root-"))
    for name in _LINKED_TOP_LEVEL:
        src = real_root / name
        if src.exists():
            (root / name).symlink_to(src)

    assets = root / "assets"
    assets.mkdir()
    real_videos = real_root / "assets" / "videos"
    if real_videos.exists():
        (assets / "videos").symlink_to(real_videos)

    target = root / model_file
    target.parent.mkdir(parents=True, exist_ok=True)
    target.symlink_to(dxnn)
    return root


def resolve() -> tuple[Path, str, str] | None:
    """Return (app_root, model_name, model_file) or None if unavailable.

    A returned overlay root registers itself for cleanup via ``cleanup()``.
    """
    model_name = os.environ.get(_MODEL_ENV, "").strip()
    if not model_name or not NPU_DEVICE.exists():
        return None

    real_root = _real_root()
    model_file = registry_lookup(real_root, model_name)
    if not model_file:
        return None

    if (real_root / model_file).is_file():
        return real_root, model_name, model_file

    override = os.environ.get(_MODEL_FILE_ENV, "").strip()
    if not override:
        return None
    dxnn = Path(override)
    if not dxnn.is_file():
        return None

    overlay = _build_overlay(real_root, model_file, dxnn)
    _OVERLAYS.append(overlay)
    return overlay, model_name, model_file


_OVERLAYS: list[Path] = []


def cleanup() -> None:
    while _OVERLAYS:
        shutil.rmtree(_OVERLAYS.pop(), ignore_errors=True)


def unavailable_reason() -> str:
    """Human-readable reason the tier cannot run, for the skip message."""
    if not os.environ.get(_MODEL_ENV, "").strip():
        return f"{_MODEL_ENV} not set — the real-NPU tier is opt-in"
    if not NPU_DEVICE.exists():
        return f"no NPU device node ({NPU_DEVICE})"
    real_root = _real_root()
    model_name = os.environ[_MODEL_ENV].strip()
    model_file = registry_lookup(real_root, model_name)
    if not model_file:
        return f"{model_name!r} is not in dx_app's test_models.conf"
    return (
        f"{model_file} is not under {real_root} and {_MODEL_FILE_ENV} "
        "does not point at a readable .dxnn"
    )
