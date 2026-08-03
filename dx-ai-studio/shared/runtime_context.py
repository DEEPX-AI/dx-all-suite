"""Resolved Studio runtime facts used to launch App and Stream children."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from shared.runtime import installed_runtime_lib_dirs, runtime_python
from shared.runtime_state import RuntimePhase, RuntimeStateStore
from shared.runtime_validation import default_plugin_directory


class RuntimeContextError(RuntimeError):
    """Raised when Studio has no validated runtime launch context."""


@dataclass(frozen=True)
class ActiveRuntimeContext:
    """Immutable launch facts derived only from Studio state and installed paths."""

    version: str
    python_executable: Path
    venv_root: Path
    library_dirs: tuple[Path, ...]
    plugin_dir: Path
    postprocess_lib_dir: Path


def resolve_active_runtime_context(
    *,
    state_store: Optional[RuntimeStateStore] = None,
    python_executable: Optional[Path] = None,
    library_dirs: Optional[Sequence[Path]] = None,
    plugin_dir: Optional[Path] = None,
    postprocess_lib_dir: Optional[Path] = None,
) -> ActiveRuntimeContext:
    """Resolve launch facts only for a journaled, fully validated profile."""
    state = (state_store or RuntimeStateStore()).load()
    if state.phase is not RuntimePhase.ACTIVE or not state.active_version:
        raise RuntimeContextError("Studio runtime profile is not active and validated.")

    interpreter_value = python_executable or runtime_python()
    if not interpreter_value:
        raise RuntimeContextError("Active runtime profile has no complete inference Python.")
    interpreter = Path(interpreter_value)
    if not interpreter.is_file():
        raise RuntimeContextError("Active runtime Python executable is missing: {}".format(interpreter))

    libraries = tuple(
        Path(path)
        for path in (
            library_dirs if library_dirs is not None else installed_runtime_lib_dirs()
        )
        if Path(path).is_dir()
    )
    if not libraries:
        raise RuntimeContextError("Active runtime profile has no native library directories.")

    return ActiveRuntimeContext(
        version=state.active_version,
        python_executable=interpreter,
        venv_root=interpreter.parent.parent,
        library_dirs=libraries,
        plugin_dir=Path(plugin_dir) if plugin_dir is not None else default_plugin_directory(),
        postprocess_lib_dir=(
            Path(postprocess_lib_dir)
            if postprocess_lib_dir is not None
            else Path("/usr/local/share/gstdxstream/lib")
        ),
    )
