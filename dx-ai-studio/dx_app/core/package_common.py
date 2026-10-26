"""Helpers shared by model-package exports (developer.extract_model_package, `/api/extract`).

extract_model_package.sh trims a Python example's `common/` to what the runner and factory import statically, but
per-model examples name their pre/postprocessor in config.json and resolve it at run time (common.variant_config).
A trimmed package dies outside the Studio with "processor class 'LetterboxPreprocessor' is exported by neither
common.processors nor common.visualizers", so the whole `common/` (about 1.3 MB of Python) goes next to the runner.
Contract: tests/dx_app/test_package_common.py
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path


def copy_regular(source: Path, destination: Path) -> None:
    """Copy one regular file; a symlink or anything that is not a file is refused."""
    if source.is_symlink() or not source.is_file():
        raise ValueError("unsafe source file")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    os.chmod(destination, source.stat().st_mode & 0o777)
    if destination.is_symlink() or not destination.is_file():
        raise ValueError("package copy is not a regular file")


def complete_python_common(source_root: Path, runner_dir: Path) -> None:
    """Put dx_app's whole python `common/` next to the runner (see the module docstring)."""
    source_common = source_root / "src" / "python_example" / "common"
    if not source_common.is_dir():
        return
    target = runner_dir / "common" if (runner_dir / "common").is_dir() else runner_dir.parent.parent / "common"
    for path in source_common.rglob("*"):
        if "__pycache__" in path.parts:
            continue
        if path.is_symlink():
            raise ValueError("unsafe source directory symlink")
        dest = target / path.relative_to(source_common)
        if path.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            copy_regular(path, dest)
