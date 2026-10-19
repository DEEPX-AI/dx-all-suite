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

def _drop_suffix(text: str, suffix: str) -> str:
    """str.removesuffix is 3.9+, but pyproject supports 3.8 (tests/shared/test_python_floor.py)."""
    return text[: -len(suffix)] if suffix and text.endswith(suffix) else text


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
        # per-model layout: DEMO_PY_DIR is task/family and the model is DEMO_MODEL's stem; the studio's
        # model name and run path use the stem too.
        from shared import dx_app_layout as _layout
        per_model = _layout.detect(Path(run_demo_path).parent) == _layout.PER_MODEL
        demos = []
        for i in range(n):
            py_dir = cols["DEMO_PY_DIR"][i]
            category, _, model_name = py_dir.partition("/")
            family = None
            if per_model:
                family, model_name = model_name, _drop_suffix(cols["DEMO_MODEL"][i].rsplit("/", 1)[-1], ".dxnn")
            demos.append({
                "idx": i,
                "label": cols["DEMO_LABELS"][i],
                "group": cols["DEMO_GROUPS"][i],
                "model": cols["DEMO_MODEL"][i],
                "category": category,
                "model_name": model_name,
                "family": family,
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


def _dx_app_root():
    """dx_app root (follows the DX_APP_ROOT setting): run_demo.sh lives here and sample media paths are relative to it."""
    try:
        from dx_app.core.config import DX_APP_ROOT
    except Exception:
        from config import DX_APP_ROOT  # dx_app/core on sys.path (studio runtime)
    return Path(DX_APP_ROOT)


def list_demos() -> dict:
    """Public entry: parse the real run_demo.sh (path from config) → grouped payload.
    {"demos": [], "groups": [], "ok": False} on any failure (import, path, or parse)."""
    try:
        path = _dx_app_root() / "run_demo.sh"
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
        # A per-model stem (yolov7_640x640) is far from the Model Zoo thumbnail name (yolov7d6.jpg), so also look
        # up the family and the registry's old name.
        thumb = _resolve_thumb(d["model_name"], d["run_ref"]["model_name"], d.get("model"),
                               _legacy_name(d["model_name"]), d.get("family"))
        d["thumbnail"] = ("/api/demo-thumb?f=" + thumb) if thumb else None
        d["media"] = {"video": _media_exists(d.get("default_video")), "image": _media_exists(d.get("default_image"))}
    return base


_LEGACY_NAMES = None


def _legacy_name(stem):
    """per-model registry stem -> old model_name (yolov7_640x640 -> yolov7). None if unknown."""
    global _LEGACY_NAMES
    if _LEGACY_NAMES is None:
        _LEGACY_NAMES = {}
        try:
            import json as _json
            rows = _json.loads((_dx_app_root() / "config" / "model_registry.json").read_text(encoding="utf-8"))
            for r in rows if isinstance(rows, list) else []:
                if isinstance(r, dict) and r.get("variant") and r.get("model_name"):
                    _LEGACY_NAMES[r["variant"]] = r["model_name"]
        except (OSError, ValueError):
            pass
    return _LEGACY_NAMES.get(stem)


def _media_exists(rel) -> bool:
    """Is a demo's sample file on disk? Unknown root → True (never hide an input we can't check).
    The Run Demo stage defaults away from, and disables, a sample that isn't downloaded."""
    if not rel:
        return False
    try:
        p = Path(rel)
        q = p if p.is_absolute() else _dx_app_root() / p
        return q.is_file() or q.is_dir()    # face_pair and person_pair are folders of image pairs
    except Exception:
        return True


# ── Model preview thumbnails (dx_modelzoo/data/thumbnails/*.jpg) ─────────────────────
# The Run Demo cards show the model's ModelZoo thumbnail as a preview. Demo model_names
# don't always equal a thumbnail filename (yolov7 → yolov7d6.jpg), so match by a normalized
# key: exact first, then the shortest thumbnail whose name starts with the demo key.
_THUMBS_DIR = Path(__file__).resolve().parents[2] / "dx_modelzoo" / "data" / "thumbnails"
# The original folder is gitignored; a clone only has the repo copy the Model Zoo screen uses (<stem>-jpg.webp)
# (contract: tests/dx_app/test_demo_thumbs_committed.py)
_OPT_THUMBS_DIR = Path(__file__).resolve().parents[2] / "dx_modelzoo" / "data" / "optimized" / "thumbnails"
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
            for p in sorted(_OPT_THUMBS_DIR.glob("*-jpg.webp")):
                _THUMB_INDEX.setdefault(_thumb_norm(p.name[:-len("-jpg.webp")]), p.name)
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
    for base in (_THUMBS_DIR, _OPT_THUMBS_DIR):
        try:
            p = (base / fname).resolve()
            p.relative_to(base.resolve())
        except (ValueError, OSError):
            continue
        if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            return p
    return None
