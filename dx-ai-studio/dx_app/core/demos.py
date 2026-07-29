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
try:
    from dx_app.core.config import IMAGE_ONLY_CATEGORIES as _IMAGE_ONLY_CATEGORIES
except Exception:
    _IMAGE_ONLY_CATEGORIES = {"embedding", "reid", "attribute_recognition",
                              "object_pose_estimation", "3d_object_detection"}

def _demo_image_only(category, curated):
    """image-only iff the category's runner truly rejects video (config is the single
    source of truth). Ignores the stale curated column for correctness."""
    return category in _IMAGE_ONLY_CATEGORIES

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
                # Authoritative image-only gate = config.IMAGE_ONLY_CATEGORIES (the 5 runners
                # that truly reject video), not the curated column — which wrongly flagged
                # hand_* and hid their working video mode.
                "image_only": _demo_image_only(category, cols["DEMO_IMAGE_ONLY"][i]),
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
        thumb = _resolve_thumb(d["model_name"], d["run_ref"]["model_name"], d.get("model"))
        d["thumbnail"] = ("/api/demo-thumb?f=" + thumb) if thumb else None
    return base


# ── Model preview thumbnails (dx_modelzoo/data/thumbnails/*.jpg) ─────────────────────
# The Run Demo cards show the model's ModelZoo thumbnail as a preview. Demo model_names
# don't always equal a thumbnail filename (yolov7 → yolov7d6.jpg), so match by a normalized
# key: exact first, then the shortest thumbnail whose name starts with the demo key.
_THUMBS_DIR = Path(__file__).resolve().parents[2] / "dx_modelzoo" / "data" / "thumbnails"
_THUMB_INDEX = None


def _thumb_norm(s) -> str:
    return "".join(ch for ch in str(s or "").lower() if ch.isalnum())


def _thumb_index() -> dict:
    global _THUMB_INDEX
    if _THUMB_INDEX is None:
        _THUMB_INDEX = {}
        try:
            for p in sorted(_THUMBS_DIR.glob("*.jpg")):
                _THUMB_INDEX.setdefault(_thumb_norm(p.stem), p.name)
        except OSError:
            _THUMB_INDEX = {}
    return _THUMB_INDEX


def _resolve_thumb(*names):
    idx = _thumb_index()
    keys = [k for k in (_thumb_norm(n) for n in names) if k]
    for k in keys:
        if k in idx:
            return idx[k]
    for k in keys:
        for tk, fn in sorted(idx.items(), key=lambda x: len(x[0])):
            if tk.startswith(k):
                return fn
    return None


def thumbnail_path(fname: str):
    """Resolve a requested thumbnail filename to a real file under the thumbnails dir, or None
    if it escapes the directory or does not exist (path-traversal safe)."""
    try:
        p = (_THUMBS_DIR / fname).resolve()
        p.relative_to(_THUMBS_DIR.resolve())
    except (ValueError, OSError):
        return None
    return p if (p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")) else None
