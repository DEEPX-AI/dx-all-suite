# dx_app/core/demos.py
"""Parse dx-runtime/dx_app/run_demo.sh bash arrays into a normalized demo list.

Hybrid design: the demo catalog (labels, groups, models, sample media, mode/input
constraints) is the single source of truth in run_demo.sh. We parse it so the studio
GUI stays in sync with the CLI demos automatically. Execution reuses run_inference.
Stdlib only.
"""
from __future__ import annotations
import re
from pathlib import Path

_ARRAYS = ("DEMO_LABELS", "DEMO_GROUPS", "DEMO_CPP_BASE", "DEMO_PY_DIR",
           "DEMO_PY_BASE", "DEMO_MODEL", "DEMO_VIDEO", "DEMO_IMAGE",
           "DEMO_PY_ASYNC", "DEMO_IMAGE_ONLY")


def _extract_array(text: str, name: str) -> list[str]:
    """Return the elements of a bash array `name=( ... )`.
    Handles quoted ("a b") and bare (tok) elements and strips `# ...` comments."""
    m = re.search(r'^%s=\(\s*(.*?)\n\)' % re.escape(name), text, re.S | re.M)
    if not m:
        raise ValueError("array not found: %s" % name)
    body = m.group(1)
    items: list[str] = []
    for line in body.splitlines():
        line = re.sub(r'#.*$', '', line).strip()   # strip inline/whole-line comments
        if not line:
            continue
        # Quoted strings first, then remaining bare tokens (quoted segments removed).
        for qm in re.finditer(r'"([^"]*)"', line):
            items.append(qm.group(1))
        items.extend(re.sub(r'"[^"]*"', ' ', line).split())
    return items


def parse_run_demo(run_demo_path: Path) -> list[dict]:
    """Parse run_demo.sh into a list of demo dicts (source order). [] on any error."""
    try:
        text = Path(run_demo_path).read_text(encoding="utf-8")
        cols = {name: _extract_array(text, name) for name in _ARRAYS}
        n = len(cols["DEMO_LABELS"])
        if n == 0 or any(len(v) != n for v in cols.values()):
            return []
        demos = []
        for i in range(n):
            py_dir = cols["DEMO_PY_DIR"][i]
            category, _, model_name = py_dir.partition("/")
            demos.append({
                "idx": i,
                "label": cols["DEMO_LABELS"][i],
                "group": cols["DEMO_GROUPS"][i],
                "model": cols["DEMO_MODEL"][i],
                "category": category,
                "model_name": model_name,
                "py_base": cols["DEMO_PY_BASE"][i],
                "cpp_base": cols["DEMO_CPP_BASE"][i],
                "default_video": cols["DEMO_VIDEO"][i],
                "default_image": cols["DEMO_IMAGE"][i],
                "async_full": cols["DEMO_PY_ASYNC"][i] == "full",
                "image_only": cols["DEMO_IMAGE_ONLY"][i] == "1",
            })
        return demos
    except Exception:
        return []


def list_demos() -> dict:
    """Public entry: parse the real run_demo.sh (path from config) → grouped payload.
    {"demos": [], "groups": [], "ok": False} on any failure (import, path, or parse)."""
    try:
        try:
            from dx_app.core.config import DX_RT_ROOT
        except Exception:
            from config import DX_RT_ROOT  # dx_app/core on sys.path (studio runtime)
        path = DX_RT_ROOT.parent / "dx_app" / "run_demo.sh"
        demos = parse_run_demo(path)
        groups = list(dict.fromkeys(d["group"] for d in demos))
        return {"demos": demos, "groups": groups, "ok": bool(demos)}
    except Exception:
        return {"demos": [], "groups": [], "ok": False}


def build_demos_payload() -> dict:
    """list_demos() joined with per-model availability + the registry run identity.

    A demo's model_name is the example script dir (e.g. "yolov7"); the registry key/name
    may differ (e.g. "yolov7_640x640"). We match by category + (name prefix or model_file)
    and attach both `avail` (toggle enablement) and `run_ref` (exact /api/run identity)."""
    base = list_demos()
    try:
        from dx_app.core.models import get_models
    except Exception:
        from models import get_models
    try:
        models = get_models()
    except Exception:
        models = []
    _AVAIL_KEYS = ("cpp_sync","cpp_async","py_sync","py_async",
                   "py_sync_cpp_postprocess","py_async_cpp_postprocess","model_exists")
    def _match(cat, mname, model_file):
        return next((x for x in models
                     if x.get('category') == cat and
                     (x.get('model_file') == model_file
                      or (x.get('name') or '').startswith(mname))), None)
    for d in base["demos"]:
        m = _match(d["category"], d["model_name"], d["model"]) or {}
        d["avail"] = {k: bool(m.get(k)) for k in _AVAIL_KEYS}
        d["run_ref"] = {"model_name": m.get("name") or d["model_name"],
                        "category": m.get("category") or d["category"],
                        "model_file": m.get("model_file") or d["model"]}
    return base
