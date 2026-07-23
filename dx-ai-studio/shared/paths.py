"""Single source of truth for studio/suite/runtime roots and path-safety.
Env vars are honored; fallbacks derive from this file's location."""
from __future__ import annotations  # PEP 563: keeps `X | None` hints valid on Python 3.8+
import os
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
    """User-viewable results root (STUDIO_ROOT/outputs[/app]); created on demand."""
    d = STUDIO_ROOT / "outputs" / app if app else STUDIO_ROOT / "outputs"
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
