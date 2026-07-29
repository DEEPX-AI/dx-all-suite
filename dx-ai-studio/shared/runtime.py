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

# Studio-owned inference venv (Option 1). Holds numpy+cv2+dx_engine in ONE interpreter for the
# python-variant demos, WITHOUT modifying dx-runtime or the base interpreter. Created lazily by
# ensure_inference_venv() only when no existing interpreter already has all three. Lives under
# the studio tree (shared/ is dx-ai-studio/shared).
STUDIO_ROOT = Path(__file__).resolve().parent.parent          # dx-ai-studio/
STUDIO_INFER_VENV = STUDIO_ROOT / "venv-dx-studio-infer"


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
    # The studio-owned inference venv (Option 1), if built, is the FIRST choice — it is the one
    # interpreter we can guarantee has numpy+cv2+dx_engine together.
    _studio_py = STUDIO_INFER_VENV / "bin" / "python3"
    if _studio_py.is_file():
        cands.append(str(_studio_py))
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
    ordered = []
    seen = set()
    for py in cands:
        if py and py not in seen:
            seen.add(py)
            ordered.append(py)

    def _can_import(py: str, snippet: str) -> bool:
        try:
            return subprocess.run([py, "-c", snippet],
                                  capture_output=True, timeout=20).returncode == 0
        except Exception:
            return False

    # PASS 1 — strongly prefer an interpreter that ALREADY has numpy + cv2 + a working
    # dx_engine. The python-variant demos need all three; when they don't coexist, picking a
    # numpy+cv2 python that lacks dx_engine makes every python demo die with `ImportError:
    # _pydxrt` (dx_engine's C++ ext). This happens on boards where dx_engine lives in one
    # interpreter (system python / venv-dx-runtime) but cv2 in another — e.g. an existing
    # runtime install has all three in the SYSTEM python while an earlier venv candidate is
    # missing cv2. Choose the complete interpreter regardless of candidate order.
    for py in ordered:
        if _can_import(py, "import numpy, cv2; from dx_engine import InferenceEngine"):
            return py
    # PASS 2 — fall back to numpy+cv2 (dx_engine is then injected via
    # dx_engine_pythonpath_dirs(), which only kicks in when the chosen python lacks it).
    for py in ordered:
        if _can_import(py, "import numpy, cv2"):
            return py
    return shutil.which("python3") or sys.executable


def _has_numpy_cv2_dxengine(python: str) -> bool:
    """True if `python` can import numpy + cv2 + a WORKING dx_engine, all on its own."""
    try:
        return subprocess.run(
            [python, "-c", "import numpy, cv2; from dx_engine import InferenceEngine"],
            capture_output=True, timeout=25).returncode == 0
    except Exception:
        return False


def ensure_inference_venv(log=None) -> str | None:
    """Guarantee ONE interpreter with numpy+cv2+dx_engine for the python-variant demos, without
    modifying dx-runtime or any base interpreter (Option 1).

    - If runtime_python() already resolves to a complete interpreter (numpy+cv2+dx_engine),
      nothing is built — returns it.
    - Otherwise builds a studio-owned venv seeded (`--system-site-packages`) from an interpreter
      that HAS a working dx_engine (so the compiled `_pydxrt` is inherited, ABI-matched), then
      pip-installs opencv-python-headless + numpy INTO that venv only. The base interpreter and
      dx-runtime's venv are never touched.
    - Returns the ready interpreter path, or None if no dx_engine-capable interpreter exists yet
      (the runtime must be installed first — dx_engine is not on PyPI).

    Idempotent and safe to call repeatedly (a satisfied state is a fast no-op)."""
    def _say(m):
        if log:
            log(m)

    current = runtime_python()
    if _has_numpy_cv2_dxengine(current):
        return current

    venv_py = STUDIO_INFER_VENV / "bin" / "python3"
    if venv_py.is_file() and _has_numpy_cv2_dxengine(str(venv_py)):
        return str(venv_py)

    # Find an interpreter with a WORKING dx_engine to seed from (system python, venv-dx-runtime…).
    seeds = []
    for root in runtime_venv_roots():
        p = root / "bin" / "python3"
        if p.is_file():
            seeds.append(str(p))
    seeds.append(sys.executable)
    for name in ("python3", "python"):
        w = shutil.which(name)
        if w:
            seeds.append(w)
    seed = next((s for s in dict.fromkeys(seeds) if runtime_python_has_dx_engine(s)), None)
    if not seed:
        _say("No interpreter with a working dx_engine found — install the DX runtime first "
             "(dx_engine is not on PyPI).")
        return None

    try:
        _say(f"Creating studio inference venv (seed: {seed}) …")
        r = subprocess.run([seed, "-m", "venv", "--system-site-packages", str(STUDIO_INFER_VENV)],
                           capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            _say("venv creation failed: " + (r.stderr or "")[-300:])
            return None
        _say("Installing opencv-python-headless + numpy into the inference venv …")
        r = subprocess.run([str(venv_py), "-m", "pip", "install", "--upgrade",
                            "opencv-python-headless", "numpy"],
                           capture_output=True, text=True, timeout=900)
        if r.returncode != 0:
            _say("pip install failed: " + (r.stderr or "")[-300:])
            return None
    except (OSError, subprocess.SubprocessError) as exc:
        _say(f"inference venv setup error: {exc}")
        return None

    if _has_numpy_cv2_dxengine(str(venv_py)):
        _say("Inference venv ready: " + str(venv_py))
        return str(venv_py)
    _say("Inference venv still missing numpy/cv2/dx_engine after install.")
    return None


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
