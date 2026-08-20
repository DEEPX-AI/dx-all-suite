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
_INSTALLED_RUNTIME_LIBRARY_DIRS = (
    Path("/usr/local/lib"),
    Path("/usr/lib"),
)


def installed_runtime_lib_dirs() -> list[Path]:
    """Native library locations supplied by installed runtime packages only.

    This deliberately excludes checkout paths.  It is for validated App/Stream
    launch contexts; legacy callers retain ``runtime_lib_dirs()`` below.
    """
    return list(_INSTALLED_RUNTIME_LIBRARY_DIRS)


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


def runtime_python() -> str | None:
    """Return an interpreter that imports numpy, cv2, and dx_engine together.

    A Python demo cannot safely run with a partial numpy/cv2 interpreter and an
    injected source-tree dx_engine: that combination can shadow the compiled
    extension and fail at runtime.  Callers must repair the Studio-owned inference
    venv when no complete interpreter exists.
    """
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

    # The python-variant demos need all three imports.  A full probe is mandatory;
    # returning a partial candidate creates a child that is guaranteed to fail later.
    for py in ordered:
        if _has_numpy_cv2_dxengine(py):
            return py
    return None


def telemetry_python() -> str | None:
    """Return the first interpreter compatible with telemetry imports.

    Unlike ``runtime_python()``, this selection intentionally tests the telemetry
    API surface itself.  It is used only by the telemetry worker so Studio never
    imports native ``dx_engine`` modules in its own interpreter.
    """
    candidates: list[str] = []
    for root in runtime_venv_roots():
        for name in ("python3", "python"):
            python = root / "bin" / name
            if python.is_file():
                candidates.append(str(python))
    candidates.append(sys.executable)
    for name in ("python3", "python"):
        python = shutil.which(name)
        if python:
            candidates.append(python)

    probe = (
        "from dx_engine.device_status import DeviceStatus; "
        "from dx_engine.configuration import Configuration; "
        "print(DeviceStatus.get_device_count())"
    )
    for python in dict.fromkeys(candidates):
        try:
            result = subprocess.run(
                [python, "-c", probe],
                capture_output=True,
                text=True,
                timeout=20,
            )
        except Exception:
            continue
        if result.returncode == 0:
            return python
    return None


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

        - Reuses the Studio-owned venv when it already imports numpy+cv2+dx_engine.
        - Otherwise builds that Studio-owned venv seeded (`--system-site-packages`) from an interpreter
      that HAS a working dx_engine (so the compiled `_pydxrt` is inherited, ABI-matched), then
      pip-installs opencv-python-headless + numpy INTO that venv only. The base interpreter and
      dx-runtime's venv are never touched.
    - Returns the ready interpreter path, or None if no dx_engine-capable interpreter exists yet
      (the runtime must be installed first — dx_engine is not on PyPI).

    Idempotent and safe to call repeatedly (a satisfied state is a fast no-op)."""
    def _say(m):
        if log:
            log(m)

    venv_py = STUDIO_INFER_VENV / "bin" / "python3"
    if venv_py.is_file() and _has_numpy_cv2_dxengine(str(venv_py)):
        return str(venv_py)

    # Pick a seed interpreter for the isolated venv. Two ways to get a known-good dx_engine into
    # it (see _install_working_dx_engine): install a matching self-contained WHEEL, or COPY a
    # working install. So a seed qualifies if EITHER a dx_engine wheel matches its ABI (no
    # pre-existing dx_engine needed — this covers a freshly built wheel on a box where nothing is
    # installed yet) OR it already imports dx_engine (for the copy path).
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
    seed = next(
        (s for s in dict.fromkeys(seeds)
         if _find_dx_engine_wheel(_abi_tag(s)) is not None or runtime_python_has_dx_engine(s)),
        None,
    )
    if not seed:
        _say("No dx_engine wheel and no interpreter with a working dx_engine — build/install the "
             "DX runtime python package first (dx_engine is not on PyPI).")
        return None

    # A previous partial/broken attempt (e.g. a --system-site-packages venv that inherited a
    # mismatched system dx_engine) may already be there — rebuild from scratch.
    if STUDIO_INFER_VENV.exists():
        shutil.rmtree(STUDIO_INFER_VENV, ignore_errors=True)

    try:
        # ISOLATED venv — NOT --system-site-packages. Seeding a venv with system-site-packages
        # inherits the BASE interpreter's system dist-packages, which on a mixed/partial install
        # can hold a dx_engine whose compiled _pydxrt is ABI-mismatched with the installed
        # libdxrt (dlopen "undefined symbol" on import) AND lets it SHADOW the good copy. So
        # isolate, then install a KNOWN-GOOD dx_engine explicitly (self-contained wheel first,
        # else a verbatim copy of the seed's working install).
        _say(f"Creating isolated studio inference venv (seed: {seed}) …")
        r = subprocess.run([seed, "-m", "venv", str(STUDIO_INFER_VENV)],
                           capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            _say("venv creation failed: " + (r.stderr or "")[-300:])
            return None
        # numpy + opencv FIRST: dx_engine imports numpy at import time, so a dx_engine
        # verification before numpy is present would fail spuriously.
        _say("Installing numpy + opencv-python-headless into the inference venv …")
        r = subprocess.run([str(venv_py), "-m", "pip", "install", "--upgrade",
                            "numpy", "opencv-python-headless"],
                           capture_output=True, text=True, timeout=900)
        if r.returncode != 0:
            _say("pip install (numpy/opencv) failed: " + (r.stderr or "")[-300:])
            return None
        if not _install_working_dx_engine(str(venv_py), seed, _say):
            return None
    except (OSError, subprocess.SubprocessError) as exc:
        _say(f"inference venv setup error: {exc}")
        return None

    if _has_numpy_cv2_dxengine(str(venv_py)):
        _say("Inference venv ready: " + str(venv_py))
        return str(venv_py)
    _say("Inference venv still missing numpy/cv2/dx_engine after install.")
    return None


def _abi_tag(python: str) -> str | None:
    """The interpreter's CPython ABI tag (e.g. 'cp312') for matching a dx_engine wheel."""
    try:
        out = subprocess.run(
            [python, "-c", "import sys;print('cp%d%d' % sys.version_info[:2])"],
            capture_output=True, text=True, timeout=15)
        return out.stdout.strip() or None
    except Exception:
        return None


def _find_dx_engine_wheel(tag: str | None) -> Path | None:
    """Locate a self-contained dx_engine wheel matching the interpreter ABI tag.

    Prefers dx_rt/python_package (auditwheel output — bundles libdxrt, so it is immune to a
    mismatched system libdxrt), then any dx_engine wheel under the dx-runtime tree."""
    if not tag:
        return None
    for root in (DX_RT_ROOT / "python_package", DX_RUNTIME_ROOT):
        if not root.is_dir():
            continue
        try:
            hit = next(iter(sorted(root.rglob(f"dx_engine-*-{tag}-*.whl"))), None)
        except OSError:
            hit = None
        if hit is not None:
            return hit
    return None


def _copy_dx_engine_from(seed_py: str, target_py: str, say) -> bool:
    """Copy the working dx_engine package (+ bundled dx_engine.libs and .dist-info) from an
    interpreter that imports it into the target venv's site-packages. Preserves the exact
    ABI-matched build (and any auditwheel-bundled libdxrt) the seed proved importable."""
    try:
        src = subprocess.run(
            [seed_py, "-c",
             "import dx_engine, os; print(os.path.dirname(os.path.abspath(dx_engine.__file__)))"],
            capture_output=True, text=True, timeout=15)
        pkg = Path(src.stdout.strip())
        if not pkg.is_dir():
            return False
        site = subprocess.run(
            [target_py, "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
            capture_output=True, text=True, timeout=15)
        dest = Path(site.stdout.strip())
        if not dest.is_dir():
            return False
        sp = pkg.parent
        say(f"Copying working dx_engine from {pkg} …")
        shutil.copytree(pkg, dest / "dx_engine", dirs_exist_ok=True)
        libs = sp / "dx_engine.libs"
        if libs.is_dir():
            shutil.copytree(libs, dest / "dx_engine.libs", dirs_exist_ok=True)
        for info in sp.glob("dx_engine-*.dist-info"):
            shutil.copytree(info, dest / info.name, dirs_exist_ok=True)
        return runtime_python_has_dx_engine(target_py)
    except Exception as exc:
        say(f"dx_engine copy failed: {exc}")
        return False


def _install_working_dx_engine(target_py: str, seed_py: str, say) -> bool:
    """Install a known-good dx_engine into the isolated inference venv: a matching
    self-contained wheel first (bundles libdxrt — immune to system libdxrt skew), else a
    verbatim copy of the seed interpreter's working install."""
    wheel = _find_dx_engine_wheel(_abi_tag(target_py))
    if wheel is not None:
        say(f"Installing dx_engine wheel: {wheel.name}")
        try:
            r = subprocess.run([target_py, "-m", "pip", "install", str(wheel)],
                               capture_output=True, text=True, timeout=600)
            if r.returncode == 0 and runtime_python_has_dx_engine(target_py):
                return True
            say("wheel install did not yield a working dx_engine; trying package copy …")
        except (OSError, subprocess.SubprocessError) as exc:
            say(f"wheel install error: {exc}; trying package copy …")
    if _copy_dx_engine_from(seed_py, target_py, say):
        return True
    say("Could not install a working dx_engine into the inference venv.")
    return False


def runtime_python_has_dx_engine(python: str | None = None) -> bool:
    """True if `python` (default: runtime_python()) can import a WORKING dx_engine
    on its own (e.g. from its own venv site-packages).

    Ports dx_app/core/config.py's _runtime_python_has_dx_engine() verbatim. Used to
    decide whether the uncompiled dx_rt/python_package/src source tree may safely be
    added to a child subprocess's PYTHONPATH — adding it when the interpreter already
    has a compiled dx_engine SHADOWS the working install and breaks every
    python-variant example subprocess with `ImportError: _pydxrt`."""
    py = python or runtime_python()
    if not py:
        return False
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


def telemetry_worker_env(python: str) -> dict[str, str]:
    """Build an isolated environment for the telemetry worker subprocess.

    Native runtime paths and the source-tree ``dx_engine`` fallback are applied
    only to this child environment; the Studio server environment is unchanged.
    """
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = ld_library_path()
    if not runtime_python_has_dx_engine(python):
        pythonpath_dirs = [str(path) for path in dx_engine_pythonpath_dirs(python)]
        if pythonpath_dirs:
            existing_pythonpath = env.get("PYTHONPATH")
            env["PYTHONPATH"] = ":".join(
                pythonpath_dirs + ([existing_pythonpath] if existing_pythonpath else [])
            )
    return env


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
