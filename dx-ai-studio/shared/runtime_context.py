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
    allow_unjournaled: bool = False,
) -> ActiveRuntimeContext:
    """Resolve launch facts only for a journaled, fully validated profile.

    ``allow_unjournaled`` is for a launch the gate already allowed on the degraded path (the module's
    own contracts validated live — ``shared.runtime_gate``); use :func:`resolve_launch_context`."""
    state = (state_store or RuntimeStateStore()).load()
    journaled = state.phase is RuntimePhase.ACTIVE and bool(state.active_version)
    if not journaled and not allow_unjournaled:
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
        version=state.active_version if journaled else "unvalidated",
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


def resolve_launch_context(module: str, *, state_store: Optional[RuntimeStateStore] = None,
                           **facts) -> ActiveRuntimeContext:
    """The launch context for ``module`` exactly when the launch gate allows it.

    The gate allows dx_stream when the journal is ACTIVE *or* when Stream's own contracts validate live;
    the context must accept both, or a board that never ran the managed runtime transaction could not
    launch Stream at all (``profile.context``)."""
    from shared.runtime_gate import module_start_policy
    policy = module_start_policy(module, state_store)
    if not policy.allowed:
        raise RuntimeContextError(policy.reason.observed if policy.reason else "launch not allowed")
    return resolve_active_runtime_context(state_store=state_store, allow_unjournaled=policy.degraded, **facts)

