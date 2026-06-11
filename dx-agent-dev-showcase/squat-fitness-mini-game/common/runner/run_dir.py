#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Structured run-directory utilities for DX-APP inference examples.

Mirrors the OLD yolov5 ``create_run_dir`` / ``write_run_info`` pattern,
generalised for all models.

Every ``--save`` or ``--dump-tensors`` invocation gets a timestamped
directory so that outputs never collide::

    artifacts/python_example/
      yolov5s_sync-image-photo-20260318-143022/
        run_info.txt
        photo_result.jpg
        tensors/
          input_tensor.npy
          output_0.npy
"""

import os
import shlex
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

import numpy as np


# ======================================================================
# Run directory creation
# ======================================================================

def _default_base_dir() -> Path:
    """Return ``PROJECT_ROOT / artifacts / python_example``."""
    # Walk up from this file to the project root
    here = Path(__file__).resolve()
    # run_dir.py → runner → common → python_example → src → PROJECT_ROOT
    project_root = here.parent.parent.parent.parent.parent
    return project_root / "artifacts" / "python_example"


def _script_stem() -> str:
    """Return the stem of the entry-point script, e.g. ``yolov5s_sync``."""
    import __main__
    return Path(getattr(__main__, "__file__", "unknown")).stem


def create_run_dir(
    run_kind: str,
    run_name: str,
    save_dir: Optional[str] = None,
) -> Path:
    """Create a timestamped run directory.

    Pattern: ``{script_stem}-{run_kind}-{run_name}-{YYYYMMDD-HHMMSS}``

    Args:
        run_kind: ``"image"`` | ``"image-dir"`` | ``"stream"``
        run_name: Descriptive name (e.g. filename, directory name, ``"camera0"``)
        save_dir: Explicit base directory.  If *None*, defaults to
                  ``artifacts/python_example/``.

    Returns:
        :class:`Path` to the created directory.
    """
    base = Path(save_dir) if save_dir else _default_base_dir()
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    # Sanitise run_name for filesystem
    safe_name = run_name.replace("/", "_").replace("\\", "_").replace(":", "_")
    dirname = f"{_script_stem()}-{run_kind}-{safe_name}-{ts}"
    run_dir = base / dirname
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


# ======================================================================
# Run metadata
# ======================================================================

def _resolve_path_text(value: object) -> str:
    """Recursively resolve a value to a human-readable path string."""
    if isinstance(value, (list, tuple)):
        inner = ", ".join(_resolve_path_text(v) for v in value)
        return f"[{inner}]"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        if value.lower().startswith("rtsp://") or value.lower().startswith("camera:"):
            return value
        try:
            return str(Path(value).expanduser().resolve(strict=False))
        except (OSError, ValueError):
            return value
    return str(value)


def write_run_info(
    run_dir: Path,
    model_path: str,
    input_value: object,
) -> None:
    """Write ``run_info.txt`` into *run_dir*.

    Fields written:
    - **script** — absolute path of the entry-point script
    - **model** — resolved model path
    - **input** — resolved input path / value
    - **command** — full ``sys.argv`` as a shell command
    """
    import __main__

    script_path = str(Path(getattr(__main__, "__file__", "unknown")).expanduser().resolve(strict=False))
    model_text = str(Path(model_path).expanduser().resolve(strict=False))
    input_text = _resolve_path_text(input_value)
    command_text = shlex.join(sys.argv)

    info_path = run_dir / "run_info.txt"
    with open(info_path, "w") as f:
        f.write(f"script:  {script_path}\n")
        f.write(f"model:   {model_text}\n")
        f.write(f"input:   {input_text}\n")
        f.write(f"command: {command_text}\n")


# ======================================================================
# Tensor dump
# ======================================================================

def dump_tensors(
    input_tensor: Optional[np.ndarray],
    output_tensors: List[np.ndarray],
    session_dir: Path,
    frame_index: Optional[int] = None,
    reason: Optional[str] = None,
) -> Path:
    """Dump input **and** output tensors to ``.npy`` files.

    Args:
        input_tensor: Pre-processed input tensor (may be *None*).
        output_tensors: Raw inference outputs.
        session_dir: Base directory for this dump session.
        frame_index: If given, creates a ``frame{:06d}`` sub-directory.
        reason: If given, also writes ``reason.txt`` (e.g. traceback).

    Returns:
        :class:`Path` to the directory where tensors were saved.
    """
    if frame_index is not None:
        dump_dir = session_dir / f"frame{frame_index:06d}"
    else:
        dump_dir = session_dir
    dump_dir.mkdir(parents=True, exist_ok=True)

    if input_tensor is not None:
        np.save(str(dump_dir / "input_tensor.npy"), input_tensor)

    for i, tensor in enumerate(output_tensors):
        np.save(str(dump_dir / f"output_tensor_{i}.npy"), tensor)

    if reason:
        with open(dump_dir / "reason.txt", "w") as f:
            f.write(reason)

    return dump_dir


def dump_tensors_on_exception(
    input_tensor: Optional[np.ndarray],
    output_tensors: List[np.ndarray],
    session_dir: Path,
    frame_index: Optional[int] = None,
) -> Path:
    """Convenience wrapper that captures ``traceback.format_exc()`` as reason."""
    return dump_tensors(
        input_tensor,
        output_tensors,
        session_dir,
        frame_index=frame_index,
        reason=traceback.format_exc(),
    )
