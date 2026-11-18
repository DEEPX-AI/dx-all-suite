"""Single source of truth for studio/suite/runtime roots and path-safety.
Env vars are honored; fallbacks derive from this file's location."""
from __future__ import annotations  # PEP 563: keeps `X | None` hints valid on Python 3.8+
import os
import platform
from pathlib import Path

STUDIO_ROOT = Path(__file__).resolve().parent.parent          # dx-ai-studio/
SUITE_ROOT = STUDIO_ROOT.parent                                # dx-all-suite/

def _root(env, *rel):
    v = os.environ.get(env)
    return Path(v) if v else SUITE_ROOT.joinpath(*rel)

DX_RUNTIME_ROOT = _root("DX_RUNTIME_ROOT", "dx-runtime")
DX_APP_ROOT = _root("DX_APP_ROOT", "dx-runtime", "dx_app")
DX_COMPILER_ROOT = _root("DX_COMPILER_ROOT", "dx-compiler")

def outputs_dir(app: str | None = None) -> Path:
    """User-viewable results root (STUDIO_ROOT/outputs[/app]); created on demand.

    DX_STUDIO_OUTPUTS moves the root — the inference E2E tests point it at a temporary folder so their results do not
    land in the user's DX App gallery."""
    base = Path(os.environ["DX_STUDIO_OUTPUTS"]) if os.environ.get("DX_STUDIO_OUTPUTS") else STUDIO_ROOT / "outputs"
    d = base / app if app else base
    d.mkdir(parents=True, exist_ok=True)
    return d

def var_dir(app: str, kind: str) -> Path:
    """Internal transient dir (STUDIO_ROOT/var/<app>/<kind>); created on demand."""
    d = STUDIO_ROOT / "var" / app / kind
    d.mkdir(parents=True, exist_ok=True)
    return d

def is_safe_path(target, roots) -> bool:
    try:
        rt = Path(target).resolve()
    except OSError:
        return False
    for r in roots:
        try:
            rt.relative_to(Path(r).resolve()); return True
        except ValueError:
            continue
    return False


_ARCH_ALIASES = {"arm64": "aarch64", "amd64": "x86_64"}
_KNOWN_ARCHES = ("x86_64", "aarch64")


def host_arch() -> str:
    """This machine's CPU arch in dx_app build.sh terms (x86_64 | aarch64)."""
    m = platform.machine().lower()
    return _ARCH_ALIASES.get(m, m)


def build_dir_candidates(dx_app_root) -> list:
    """C++ runner dirs, host arch first: a leftover build of the other arch must not shadow ours."""
    root = Path(dx_app_root)
    host = host_arch()
    arches = [host] + [a for a in _KNOWN_ARCHES if a != host]
    return [root / f"build_{a}" / "src" / "cpp_example" for a in arches] + [root / "bin"]


def pick_build_dir(dx_app_root) -> Path:
    """First candidate that exists, else the host-arch source-build path (where build.sh will put it)."""
    cands = build_dir_candidates(dx_app_root)
    return next((d for d in cands if d.is_dir()), cands[0])
