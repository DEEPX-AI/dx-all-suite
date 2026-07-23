"""Single locator for the sibling **dx-runtime** tree: NPU library dirs, the
dx-runtime venv python, and dx_engine/_pydxrt discovery.

This module PORTS (verbatim, behavior-preserving) logic that used to be duplicated
across dx_app/core/inference.py, dx_app/core/config.py, dx_app/core/setup_steps.py
and dx_stream/core/metadata.py. Do not "simplify" any of the orderings below — the
NPU LD_LIBRARY_PATH hot path and the `_pydxrt` shadow-avoidance fix both depend on
the exact directory lists and probe order.

Roots are derived from shared.paths (DX_RUNTIME_ROOT / SUITE_ROOT), never re-derived.
"""
from __future__ import annotations  # PEP 563: keeps `X | None` hints valid on Python 3.8+
import os
import shutil
import subprocess
import sys
from pathlib import Path

from shared.paths import DX_RUNTIME_ROOT, SUITE_ROOT

DX_RT_ROOT = DX_RUNTIME_ROOT / "dx_rt"


def runtime_lib_dirs() -> list[Path]:
    """Candidate directories to prepend to LD_LIBRARY_PATH for NPU inference
    subprocesses. Ports the identical `_lib_dirs` list duplicated in
    dx_app/core/inference.py's run_inference() (sync path) and _build_ld_path()
    (live/Xvfb path). Order matters: system dirs first, then the dx_rt build lib,
    then the dx_rt installed lib."""
    return [
        Path("/usr/local/lib"),
        Path("/usr/lib"),
        DX_RT_ROOT / "build_x86_64" / "lib",
        DX_RT_ROOT / "lib",
    ]


def ld_library_path() -> str:
    """Build the LD_LIBRARY_PATH string: only the runtime_lib_dirs() that actually
    exist, joined with ':', with any current os.environ LD_LIBRARY_PATH prepended.
    Ports the identical existing-dir-filter + join + prepend logic duplicated at
    both call sites in dx_app/core/inference.py."""
    existing = [str(d) for d in runtime_lib_dirs() if d.is_dir()]
    ld = ":".join(existing)
    cur = os.environ.get("LD_LIBRARY_PATH")
    if cur:
        ld = cur + ":" + ld
    return ld


def runtime_venv_roots() -> list[Path]:
    """Candidate venv-dx-runtime roots, in probe order. Ports the identical 2-item
    list duplicated in dx_app/core/config.py's _find_runtime_python()/_load_dx()
    and dx_app/core/setup_steps.py's python-venv setup check."""
    return [DX_RUNTIME_ROOT / "venv-dx-runtime", SUITE_ROOT / "venv-dx-runtime"]


def runtime_python() -> str:
    """The dx-runtime venv python if it can actually import numpy+cv2, else the
    current interpreter / a python3-on-PATH fallback.

    Ports dx_app/core/config.py's _find_runtime_python() verbatim: python_example
    demo scripts hard-depend on numpy+cv2, but venv-dx-runtime is frequently an
    otherwise-empty venv (dx_engine is injected via PYTHONPATH, not pip-installed),
    so every candidate is probed and skipped if it can't import numpy+cv2 — falling
    back all the way to the gui server's own python if none qualify."""
    cands = []
    for root in runtime_venv_roots():
        for name in ("python3", "python"):
            p = root / "bin" / name
            if p.is_file():
                cands.append(str(p))
    cands.append(sys.executable)
    for name in ("python3", "python"):
        p = shutil.which(name)
        if p:
            cands.append(p)
    seen = set()
    for py in cands:
        if not py or py in seen:
            continue
        seen.add(py)
        try:
            if subprocess.run([py, "-c", "import numpy,cv2"],
                               capture_output=True, timeout=15).returncode == 0:
                return py
        except Exception:
            pass
    return shutil.which("python3") or sys.executable


def runtime_python_has_dx_engine(python: str | None = None) -> bool:
    """True if `python` (default: runtime_python()) can import a WORKING dx_engine
    on its own (e.g. from its own venv site-packages).

    Ports dx_app/core/config.py's _runtime_python_has_dx_engine() verbatim. Used to
    decide whether the uncompiled dx_rt/python_package/src source tree may safely be
    added to a child subprocess's PYTHONPATH — adding it when the interpreter already
    has a compiled dx_engine SHADOWS the working install and breaks every
    python-variant example subprocess with `ImportError: _pydxrt`."""
    py = python or runtime_python()
    try:
        return subprocess.run(
            [py, "-c", "from dx_engine import InferenceEngine"],
            capture_output=True, timeout=15).returncode == 0
    except Exception:
        return False


def dx_engine_search_paths() -> list[Path]:
    """Existing sys.path-insertable directories where dx_engine/_pydxrt live, in
    fallback order: venv-dx-runtime site-packages roots (+ the roots themselves),
    then the dx_rt source tree's site-packages-shaped layout.

    Ports dx_app/core/config.py's _load_dx() fallback-root loop verbatim (used to
    inject dx_engine into the STUDIO SERVER'S OWN sys.path, e.g. so
    shared/hardware.py's DeviceStatus is real instead of mocked). Callers should try
    a direct `import dx_engine` FIRST and only fall back to inserting these paths —
    that ordering (not reproduced here) is itself part of the _pydxrt shadow fix and
    stays in the caller."""
    paths: list[Path] = []
    for root in runtime_venv_roots() + [DX_RT_ROOT / "python_package" / "src"]:
        if not root.is_dir():
            continue
        for sp in list(root.glob("lib/python*/site-packages")) + [root]:
            if sp.is_dir():
                paths.append(sp)
    return paths


def dx_engine_pythonpath_dirs(python: str | None = None) -> list[Path]:
    """dx_rt source-tree directories to prepend to a CHILD subprocess's PYTHONPATH
    so it can `import dx_engine` — but ONLY when `python` (default: runtime_python())
    does not already provide a working dx_engine of its own.

    Ports dx_app/core/config.py's `_DX_ENGINE_SRC_DIRS` conditional verbatim — this
    IS the `_pydxrt` shadow fix: unconditionally adding dx_rt/python_package/src to
    PYTHONPATH would shadow an already-working compiled dx_engine with the uncompiled
    source tree, breaking with `ImportError: _pydxrt`."""
    if runtime_python_has_dx_engine(python):
        return []
    return [DX_RT_ROOT / "python_package" / "src", DX_RT_ROOT / "python_package"]


def dx_rt_cli_python() -> str:
    """Python interpreter for invoking dx_rt CLI tools (e.g. `cli.parse_model`),
    preferring the dx_rt-local venv, else 'python3' on PATH.

    Ports dx_stream/core/metadata.py's _RT_VENV_PYTHON/_FALLBACK_PYTHON selection
    verbatim. NOTE: this venv is named 'venv-dx_rt' (underscore), distinct from the
    app-level 'venv-dx-runtime' (hyphen) used by runtime_python()/runtime_venv_roots()
    — do not conflate the two."""
    p = DX_RT_ROOT / "venv-dx_rt" / "bin" / "python3"
    return str(p) if p.exists() else "python3"


def dx_rt_cli_pythonpath() -> Path:
    """PYTHONPATH for dx_rt CLI subprocess invocations (e.g. `cli.parse_model`).
    Ports dx_stream/core/metadata.py's `pythonpath` literal verbatim."""
    return DX_RT_ROOT / "python_package"
