"""DX-APP Model registry — scanning, loading, and model info."""

import os, re, json
from pathlib import Path
from dx_app.core.config import (BUILD_DIR, CPP_DIR, PY_DIR, ASSETS_DIR, CONFIG_FILE, SAMPLE_DIR,
                    SKIP_CAT, CATEGORIES, CAT_LABEL, CAT_IMAGE, CAT_VIDEO,
                    TASK_TYPES, POSTPROCESSORS, DX_APP_ROOT, resolve_model_path)
from dx_app.core.inference_exec import _find_fallback_binary, _is_executable_file, _python_runtime_ready
from shared import dx_app_layout as _layout
from shared.paths import SUITE_ROOT as _SUITE_ROOT
from shared.tasks import canonical as _canonical_task
from shared.catalog_sources import parse_test_models_conf as _shared_parse_test_models_conf

_BUNDLED_MODEL_CATALOG = Path(__file__).resolve().parents[2] / "dx_modelzoo" / "data" / "model_catalog.json"
_CATALOG_ALIASES = {
    "efficientnet": "efficientnet_lite0",
    "scrfd": "scrfd500m",
    "yolox": "yoloxs",
    "yolov5": "yolov5s",
    "yolov5face": "yolov5s_face",
    "yolov5pose": "yolov5pose_ppu",
    "yolov5_ppu": "yolov5s_ppu",
    "yolov7": "yolov7",
    "yolov7_ppu": "yolov7_ppu",
    "yolov8": "yolov8n",
    "yolov8seg": "yolov8n_seg",
    "yolov9": "yolov9s",
    "yolov10": "yolov10n",
    "yolov11": "yolov11n",
    "yolov12": "yolov12n_ppu",
    "yolov26": "yolo26s",
    "yolov26cls": "yolo26s_cls",
    "yolov26pose": "yolo26s_pose",
    "yolov26seg": "yolo26s_seg",
    "yolov26obb": "yolo26s_obb",
    "deeplabv3": "deeplabv3plusmobilenetv2",
}
_MULTI_MODEL_ALIASES = {
    "yolov7_x_deeplabv3": "-m_det assets/models/YoloV7.dxnn -m_seg assets/models/DeepLabV3PlusMobileNetV2.dxnn",
}

def _load_catalog_reg():
    if not _BUNDLED_MODEL_CATALOG.exists():
        return {}
    try:
        data=json.loads(_BUNDLED_MODEL_CATALOG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[WARNING] Failed to load bundled model catalog: {exc}")
        return {}
    catalog_models=data.get("models", [])
    if not isinstance(catalog_models, list):
        print("[WARNING] Bundled model catalog has invalid 'models' payload")
        return {}
    by_id={}
    reg={}
    for model in catalog_models:
        if not isinstance(model, dict):
            continue
        model_id=str(model.get("id","")).strip()
        model_file=str(model.get("model_file","")).strip()
        if not model_id or not model_file:
            continue
        entry={"category":str(model.get("category","")).strip(),"file":model_file}
        by_id[model_id]=entry
        reg[model_id]=entry.copy()
    for alias,target in _CATALOG_ALIASES.items():
        if target in by_id:
            reg[alias]=by_id[target].copy()
    for alias,model_file in _MULTI_MODEL_ALIASES.items():
        reg[alias]={"category":"object_detection_x_semantic_segmentation","file":model_file}
    return reg

def _load_reg():
    r=_load_catalog_reg()
    for m in _shared_parse_test_models_conf(CONFIG_FILE):
        r[m["id"]]={"category":m["category"],"file":m["model_file"]}
    return r
_REG=_load_reg()

def _reload_reg():
    """Reload _REG in-place so newly deployed models are visible without restart."""
    global _REG
    _REG=_load_reg()

def _sanitize_model_name(name):
    """Convert user input to a safe model_name: lowercase, only [a-z0-9_], no leading digit."""
    import re as _re
    s=_re.sub(r'[^a-zA-Z0-9_]','_',name).strip('_')
    if s and s[0].isdigit():s='m_'+s
    return s.lower() or 'model'

def _to_class_name(model_name):
    """Convert model_name to a CamelCase factory class name."""
    return ''.join(w.capitalize() for w in model_name.split('_') if w)

def _pp_info(lang,cat,mn):
    i={"name":None,"file":None}
    if lang=="cpp":
        fd=_layout.example_dir(DX_APP_ROOT,"cpp",cat,mn)/"factory"
        if fd.is_dir():
            for hpp in fd.glob("*.hpp"):
                m=re.search(r'#include\s+"[^"]*?([a-z_]+_postprocessor)\.hpp"',hpp.read_text(errors="replace"))
                if m:
                    i["name"]=m.group(1);pp=CPP_DIR/"common"/"processors"/f"{i['name']}.hpp"
                    if pp.exists():i["file"]=str(pp.relative_to(DX_APP_ROOT))
                break
    else:
        fd=_layout.example_dir(DX_APP_ROOT,"python",cat,mn)/"factory"
        if fd.is_dir():
            for pyf in fd.glob("*.py"):
                if "__init__" in pyf.name:continue
                m=re.search(r'from\s+\S*?([a-z_]+_postprocessor)\s+import|import\s+.*?([a-z_]+_postprocessor)',pyf.read_text(errors="replace"))
                if m:
                    i["name"]=m.group(1) or m.group(2);pp=PY_DIR/"common"/"processors"/f"{i['name']}.py"
                    if pp.exists():i["file"]=str(pp.relative_to(DX_APP_ROOT))
                break
    return i


_config_cache = {}  # str(path) -> (mtime_ns, parsed_dict_or_None)

def _read_config_cached(cf):
    try:
        st = cf.stat()
    except OSError:
        return None
    key = str(cf)
    hit = _config_cache.get(key)
    if hit is not None and hit[0] == st.st_mtime_ns:
        return hit[1]
    try:
        parsed = json.loads(cf.read_text())
    except Exception:
        parsed = None
    _config_cache[key] = (st.st_mtime_ns, parsed)
    return parsed


def _installed(path):
    """Whether this is an installed model file; 0 bytes means a partial download."""
    try:
        return path.is_file() and path.stat().st_size > 0
    except OSError:
        return False


def _required_dxnn_exists(model_file):
    if model_file.startswith("-"):
        import shlex as _shlex
        _args=_shlex.split(model_file)
        return all(_installed(resolve_model_path(a, DX_APP_ROOT)) for a in _args if not a.startswith("-") and a.endswith(".dxnn"))
    return bool(model_file)and _installed(resolve_model_path(model_file, DX_APP_ROOT))


def _cpp_runner_ready(category,model_name,variant,allow_fallback=True):
    direct=BUILD_DIR/f"{model_name}_{variant}"
    if _is_executable_file(direct):
        return True
    # A per-model layout binary has its own model's pre/postprocessing built in; another model's binary gives wrong
    # results. A borrowed binary is only for custom models without an example (registry-only).
    if not allow_fallback:
        return False
    return _is_executable_file(_find_fallback_binary(category,variant,build_dir=BUILD_DIR))


def _python_runner_ready(category,model_name,variant,runtime_ready):
    if not runtime_ready:return False
    if (PY_DIR/category/model_name/f"{model_name}_{variant}.py").is_file():return True
    return _layout.python_script(DX_APP_ROOT,category,model_name,variant).is_file()


def get_models():
    models={}
    # The resolver finds example folders, both legacy (<task>/<model>) and per-model (<task>/<family>/<stem>)
    # (shared/dx_app_layout.py).
    _per_model=_layout.detect(DX_APP_ROOT)==_layout.PER_MODEL
    for ex in sorted(_layout.examples(DX_APP_ROOT),key=lambda e:(e.task,e.name)):
        cat,mn=ex.task,ex.name
        key=f"{cat}/{mn}"
        for lang,md in(("cpp",ex.cpp_dir),("python",ex.py_dir)):
            if md is None:continue
            ext=".cpp" if lang=="cpp" else ".py"
            hs=(md/f"{mn}_sync{ext}").exists();ha=(md/f"{mn}_async{ext}").exists()
            if ext==".py":hsp=(md/f"{mn}_sync_cpp_postprocess.py").exists();hap=(md/f"{mn}_async_cpp_postprocess.py").exists()
            if not hs and not ha:continue
            if key not in models:
                spec=_read_config_cached(md/"config.json")
                spec=spec if isinstance(spec,dict) else {}
                nested=_per_model and "variant" in spec
                if nested and spec.get("dxnn_file"):mf="assets/models/"+spec["dxnn_file"]
                else:reg=_REG.get(mn,{});mf=reg.get("file","")
                _mexists=_required_dxnn_exists(mf)
                cfg=_layout.flat_config(spec) if spec else {}
                models[key]={"name":mn,"category":cat,"category_label":CAT_LABEL.get(cat,cat),
                 "family":ex.family,
                 "cpp":False,"python":False,"cpp_sync":False,"cpp_async":False,
                 "py_sync":False,"py_async":False,
                 "py_sync_cpp_postprocess":False,"py_async_cpp_postprocess":False,"model_file":mf,
                 "model_exists":_mexists,
                 "npu_core":"","dataset":"","input_resolution":"","config":cfg}
                if nested:
                    models[key].update({"image_only":bool(spec.get("image_only")),
                     "default_image":spec.get("default_image") or "","default_video":spec.get("default_video") or "",
                     "input_resolution":f"{spec.get('input_width')}x{spec.get('input_height')}" if spec.get("input_width") else ""})
                elif cfg:
                    models[key].update({"npu_core":cfg.get("npu_core",cfg.get("NPU_CORE","")),
                     "dataset":cfg.get("dataset",cfg.get("DATASET","")),
                     "input_resolution":cfg.get("input_size",cfg.get("INPUT_SIZE",""))})
            if lang=="cpp":models[key].update({"cpp":True,"cpp_sync":hs,"cpp_async":ha})
            else:models[key].update({"python":True,"py_sync":hs,"py_async":ha,
                 "py_sync_cpp_postprocess":hsp,"py_async_cpp_postprocess":hap})
    # Also include registry-only models (deployed via compiler but no source code yet)
    # In the per-model layout the registry's old names (yolo26n, …) already exist as stem examples; only model
    # files no example uses (custom models deployed by the Compiler) are added as registry-only.
    _covered={(m.get("model_file") or "").rsplit("/",1)[-1] for m in models.values()} if _per_model else set()
    for mn,reg in _REG.items():
        cat=reg.get("category","custom")
        key=f"{cat}/{mn}"
        if _per_model and ((reg.get("file") or "").rsplit("/",1)[-1] in _covered or not _required_dxnn_exists(reg.get("file",""))):
            continue
        # Old names (yolo26n, efficientnet_lite0, …) become their example's name at run time and never borrow a binary
        # (server _validate_inference_payload). Listed separately, they would offer C++ and fail with "Binary not found".
        if _per_model and _layout.example_name(DX_APP_ROOT,cat,mn,reg.get("file",""))!=mn:
            continue
        if _per_model:
            cat=_canonical_task(cat);key=f"{cat}/{mn}"
        if key not in models:
            mf=reg.get("file","")
            _mexists=_required_dxnn_exists(mf)
            models[key]={"name":mn,"category":cat,"category_label":CAT_LABEL.get(cat,cat),"registry_only":True,
             "cpp":True,"python":False,"cpp_sync":True,"cpp_async":False,
             "py_sync":False,"py_async":False,"model_file":mf,
             "model_exists":_mexists,
             "npu_core":"","dataset":"","input_resolution":"","config":{}}
    _py_modes=("py_sync","py_async","py_sync_cpp_postprocess","py_async_cpp_postprocess")
    _cpp_modes=("cpp_sync","cpp_async")
    _python_ready=_python_runtime_ready() if any(any(m.get(k) for k in _py_modes) for m in models.values()) else False
    for m in models.values():
        for key in _cpp_modes:
            m[key]=bool(m.get(key) and _cpp_runner_ready(m["category"],m["name"],key[4:],
                        allow_fallback=not _per_model or m.get("registry_only",False)))
        for key in _py_modes:
            m[key]=bool(m.get(key) and _python_runner_ready(m["category"],m["name"],key[3:],_python_ready))
        m["cpp"]=any(m[key] for key in _cpp_modes)
        m["python"]=any(m[key] for key in _py_modes)
    models={key:m for key,m in models.items() if m["model_exists"] and (m["cpp"] or m["python"])}
    # Containers DX-RT cannot read (Model Zoo 2_5_0 = v9, while DX-RT 3.4.2 reads 6–8) stay listed with a reason.
    # run_inference blocks running them.
    from shared import dxrt as _dxrt
    for m in models.values():
        mf=m.get("model_file") or ""
        m["needs_dxrt"]=None if mf.startswith("-") else _dxrt.needs_for_file(resolve_model_path(mf, DX_APP_ROOT))
    # Attach the ModelZoo Q-Lite download link so the Models table can pull a not-yet-installed
    # model straight from the catalog, same as the ModelZoo page. Join by any of: the .dxnn
    # filename, the normalized class_name, or the normalized model name — local example-dir
    # names (e.g. "regnetx1_6gf_v2") don't always equal a filename but do map to the gateway's
    # class_name ("RegNetX-1.6GF (v2)"), so multiple keys are needed for full coverage.
    _dl = _download_index()
    for d in models.values():
        fn = (d.get("model_file") or "").rsplit("/", 1)[-1]
        nm = d.get("name")
        info = (_dl.get(_norm(fn)) or _dl.get(_norm(fn[:-5]) if fn.endswith(".dxnn") else "")
                or _dl.get(_norm(nm)) or _dl.get(_norm(_DL_ALIAS.get(nm))))
        if info:
            d["mz_name"] = info["name"]
            d["dxnn_url"] = info["dxnn_url"]
            d["json_url"] = info.get("json_url")
    return list(models.values())


# ── ModelZoo download-link join (Q-Lite) ─────────────────────────────────────────────
# Map a .dxnn filename → its ModelZoo download entry, so a Models-table row (which only
# knows the local filename) can trigger the SAME download the ModelZoo page uses. Computed
# once from the gateway; best-effort — if the gateway is unavailable no links are attached
# and the download button simply doesn't render.
_DL_URLS = None


def _norm(s) -> str:
    return "".join(ch for ch in str(s or "").lower() if ch.isalnum())


# A few local example-dir names diverge from the catalog's model naming enough that no
# normalized key matches (resolution/version shorthand). Map local name → a key present in the
# download index. Verified against the live catalog.
_DL_ALIAS = {
    "yolov5m6_1280": "yolov5-m6_1280x1280",
    "yolov5n_6_1":   "yolov5-n6_1280x1280_v6.1",
    "yolov5s_6_1":   "yolov5-s6_1280x1280_v6.1",
}


def _download_index() -> dict:
    """Normalized-key → Q-Lite download record, unioned from two catalog sources so every
    site model is reachable: the ModelZoo gateway (Q-Lite/Q-Pro structured, primary) and the
    run_demo manifest (flat dxnn_url — carries a few PPU/edge models the gateway list omits).
    Keyed by class_name, name, and .dxnn filename (stem + full)."""
    global _DL_URLS
    if _DL_URLS is not None:
        return _DL_URLS
    idx = {}

    def _add(keys, rec):
        for k in keys:
            nk = _norm(k)
            if nk:
                idx.setdefault(nk, rec)

    # 1) ModelZoo catalog (primary) — BAKED snapshot first (offline-safe; avoids a 6s network
    #    timeout on air-gapped installs), then the live gateway when no snapshot exists.
    try:
        r = None
        _baked = Path(__file__).resolve().parents[1] / "scripts" / "modelzoo_catalog_public.json"
        if _baked.exists():
            try:
                r = json.loads(_baked.read_text(encoding="utf-8"))
            except Exception:
                r = None
        if r is None:
            from dx_app.core.modelzoo_gateway import ModelZooGateway
            r = ModelZooGateway().list_models("public")
        for g in (r.get("models") if isinstance(r, dict) else r) or []:
            v = (g.get("qlite") or {})
            u = v.get("dxnn_url")
            if not u:
                continue
            fn = u.rsplit("/", 1)[-1]
            _add((g.get("class_name"), g.get("name"), fn, fn[:-5] if fn.endswith(".dxnn") else None),
                 {"name": g.get("name") or g.get("class_name"), "dxnn_url": u, "json_url": v.get("json_url")})
    except Exception:
        pass

    # 2) run_demo manifest (secondary union — fills gateway gaps like *_PPU).
    try:
        mp = DX_APP_ROOT / "scripts" / "modelzoo_manifest.json"
        data = json.loads(mp.read_text(encoding="utf-8"))
        for e in (data.get("models") if isinstance(data, dict) else data) or []:
            u = e.get("dxnn_url")
            if not u:
                continue
            fn = u.rsplit("/", 1)[-1]
            _add((e.get("name"), fn, fn[:-5] if fn.endswith(".dxnn") else None),
                 {"name": e.get("name"), "dxnn_url": u, "json_url": e.get("json_url")})
    except Exception:
        pass

    _DL_URLS = idx
    return _DL_URLS

def _find_example(name, model_file=""):
    """name (registry model_name, example name or catalog name) -> this tree's example. The task is unknown."""
    stem = Path(model_file).name[:-5] if str(model_file).endswith(".dxnn") else ""
    _variants = _layout._registry_variants(str(DX_APP_ROOT))
    variant = _variants.get(name) or next((v for k, v in _variants.items() if k.lower() == str(name).lower()), "")
    for cand in (name, stem, variant):
        if not cand:
            continue
        hits = [e for e in _layout.examples(DX_APP_ROOT) if e.name == cand]
        if hits:
            return hits[0]
    return None


def get_model_info(name):
    """Detail dialog of the Models table, for either layout (shared.dx_app_layout). Model files are looked up in both
    layouts, so category, files and 'Model File' are filled in the per-model tree too."""
    info={"name":name,"files":{},"postprocessors":{}}
    # A catalog name (SCRFD10G) differs from its registry key (scrfd10g) only in case
    reg=_REG.get(name) or next((v for k,v in _REG.items() if k.lower()==str(name).lower()),{})
    mf=reg.get("file","")
    if mf.startswith("-"):
        import shlex as _shlex
        _args=[a for a in _shlex.split(mf) if not a.startswith("-") and a.endswith(".dxnn")]
        _mexists=bool(_args) and all(_layout.find_model(a,DX_APP_ROOT,_SUITE_ROOT) is not None for a in _args)
    else:
        _mexists=bool(mf) and _layout.find_model(mf,DX_APP_ROOT,_SUITE_ROOT) is not None
    info.update({"model_file":mf,"model_exists":_mexists})
    ex=_find_example(name, mf if not mf.startswith("-") else "")
    if ex is None:
        return info
    info["category"]=ex.task;info["category_label"]=CAT_LABEL.get(ex.task,ex.task)
    for lk in ("cpp","python"):
        d=ex.dir(lk)
        if d is None or not d.is_dir():
            continue
        info["files"][lk]=[str(f.relative_to(DX_APP_ROOT)) for f in sorted(d.rglob("*")) if f.is_file()]
        pp=_pp_info(lk,ex.task,ex.name)
        if pp["name"]:info["postprocessors"][lk]=pp
    cfg=_layout.load_config(DX_APP_ROOT,ex.task,ex.name)
    if cfg:
        info["config"]=cfg
    return info


_GENERATED_CATALOG = Path(__file__).resolve().parents[2] / "dx_modelzoo" / "data" / "generated_catalog.json"


def _generated_catalog_rows():
    """generated catalog -> [{name, task (label), dxnn_url, json_url, class_name}] ([] if missing)."""
    try:
        data = json.loads(_GENERATED_CATALOG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    try:
        from dx_modelzoo.core.config import CATEGORIES as _MZ_CATS
    except Exception:
        _MZ_CATS = {}
    rows = []
    for gm in data.get("models", []) if isinstance(data, dict) else []:
        disp = gm.get("display") or {}
        arts = gm.get("artifacts") or {}

        def url(tier, kind):
            u = ((arts.get(f"{tier}_{kind}") or {}).get("remote_url")) or None
            return u if u and u not in ("-",) else None
        from shared.tasks import legacy as _legacy_task
        task = _legacy_task(disp.get("task") or "")     # the same grouping as Model Zoo (image_classification -> classification)
        label = (_MZ_CATS.get(task) or {}).get("label_en") or task.replace("_", " ").title() or "Other"
        rows.append({"name": disp.get("name") or gm.get("id"), "task": label,
                     "dxnn_url": url("qlite", "dxnn") or url("qpro", "dxnn") or url("qmaster", "dxnn"),
                     "json_url": url("qlite", "json") or url("qpro", "json"),
                     "class_name": disp.get("class_name") or gm.get("id")})
    return rows


def get_catalog():
    """Full ModelZoo catalog for the Models page: every model on the ModelZoo homepage (the
    gateway list) PLUS the two PPU builds it omits — 352 + 2 = 354. Each entry merges local
    run/install state so a row can show Run (when a local example exists), the installed badge,
    and Download (always, from the catalog). Kept separate from get_models() (the runnable-only
    list the Run/Benchmark/Compare pickers use) so those pages are unaffected."""
    local = get_models()
    lk = {}
    for m in local:
        fn = (m.get("model_file") or "").rsplit("/", 1)[-1]
        for k in (_norm(fn[:-5] if fn.endswith(".dxnn") else fn), _norm(m.get("name"))):
            if k:
                lk.setdefault(k, m)
    _MODE_KEYS = ("cpp", "python", "cpp_sync", "cpp_async", "py_sync", "py_async",
                  "py_sync_cpp_postprocess", "py_async_cpp_postprocess")
    _INFO_KEYS = ("npu_core", "dataset", "input_resolution", "config")
    # Per-category OR of the run-mode flags across all local examples. The ModelZoo catalog
    # splits one architecture into many resolution/version variants while dx_app ships fewer,
    # coarser examples — so a downloaded variant with no exact example still needs sensible
    # Sync/Async marks. Its category's runner handles any .dxnn of that task, so inherit the
    # category's capability. (Whether Run actually shows is gated on model_exists client-side.)
    cat_modes = {}
    for m in local:
        c = m.get("category")
        if not c:
            continue
        cm = cat_modes.setdefault(c, {k: False for k in _MODE_KEYS})
        for k in _MODE_KEYS:
            if m.get(k):
                cm[k] = True

    def mk(name, category, dxnn_url, json_url, class_name=None):
        fn = dxnn_url.rsplit("/", 1)[-1] if dxnn_url else None
        # Always point at THIS variant's own .dxnn (not a matched sibling example's file),
        # so Run/exists reflect the exact row the user sees and downloaded.
        model_file = ("assets/models/" + fn) if fn else ""
        # resolve_model_path honours DX_APP_MODELS_DIR, like every other install check on this page.
        exists = bool(fn) and _installed(resolve_model_path(model_file, DX_APP_ROOT))
        lm = None
        for k in (_norm(fn[:-5] if fn and fn.endswith(".dxnn") else fn), _norm(class_name), _norm(name)):
            if k and k in lk:
                lm = lk[k]
                break
        ent = {"name": name, "category": category, "category_label": category,
               "cpp": False, "python": False, "cpp_sync": False, "cpp_async": False,
               "py_sync": False, "py_async": False,
               "py_sync_cpp_postprocess": False, "py_async_cpp_postprocess": False,
               "model_file": (model_file or (lm.get("model_file") if lm else "")),
               "model_exists": bool(exists or (lm.get("model_exists") if lm else False)),
               "dxnn_url": dxnn_url, "json_url": json_url, "mz_name": name,
               "npu_core": "", "dataset": "", "input_resolution": "", "config": {}}
        src = lm or cat_modes.get(category)  # exact example first, else category sibling
        if src:
            for k in _MODE_KEYS:
                ent[k] = src.get(k, ent[k])
        if lm:
            for k in _INFO_KEYS:
                ent[k] = lm.get(k, ent[k])
        return ent

    # Catalog source 1: the Model Zoo module's own catalog (dx_modelzoo/data/generated_catalog.json, synced
    # from the internal publish page) — the same list the Model Zoo page shows, so App > Models does not
    # drift from it (the baked public snapshot below is older and smaller). The snapshot / live listing
    # remain the fallback.
    out = []
    gen_rows = _generated_catalog_rows()
    for g in gen_rows:
        out.append(mk(g["name"], g["task"], g["dxnn_url"], g["json_url"], g.get("class_name")))

    # Catalog source 2: prefer the BAKED snapshot (offline-safe). ModelZoo's live listing is a
    # network fetch (developer.deepx.ai), so on an air-gapped / closed-network install the live
    # call times out and the Models page would collapse to almost nothing. A snapshot baked at
    # release time (scripts/modelzoo_catalog_public.json, refreshed by scripts/bake_modelzoo_catalog.py)
    # lets offline users still see the full catalog. Fall back to live only when no snapshot exists.
    r = {"models": []} if gen_rows else None
    _baked = Path(__file__).resolve().parents[1] / "scripts" / "modelzoo_catalog_public.json"
    if r is None and _baked.exists():
        try:
            r = json.loads(_baked.read_text(encoding="utf-8"))
        except Exception:
            r = None
    if r is None:
        try:
            from dx_app.core.modelzoo_gateway import ModelZooGateway
            r = ModelZooGateway().list_models("public")
        except Exception:
            r = None
    try:
        for g in (r.get("models") if isinstance(r, dict) else r) or []:
            ql = g.get("qlite") or {}
            qp = g.get("qpro") or {}
            out.append(mk(g.get("name"), g.get("task") or "Other",
                          ql.get("dxnn_url") or qp.get("dxnn_url"),
                          ql.get("json_url") or qp.get("json_url"), g.get("class_name")))
    except Exception:
        pass
    try:
        data = json.loads((DX_APP_ROOT / "scripts" / "modelzoo_manifest.json").read_text(encoding="utf-8"))
        byname = {_norm(e.get("name")): e for e in ((data.get("models") if isinstance(data, dict) else data) or [])}
        for pn in ("SCRFD500M_PPU", "YOLOV5Pose_PPU"):
            e = byname.get(_norm(pn))
            if e:
                out.append(mk(e.get("name"), e.get("category") or "PPU", e.get("dxnn_url"), e.get("json_url")))
    except Exception:
        pass
    return out


_LANGS = ("en", "ko", "ja", "zh-CN", "zh-TW", "es")


def category_labels():
    """slug -> {language: name}, so the screen never shows raw snake_case.

    Names come from Model Zoo's category table (6 languages), so both modules call a task the same. When dx_app's slug
    differs (legacy <-> per-model, shared.tasks) its pair is used; failing that, the slug spelled out in English."""
    try:
        from dx_modelzoo.core.config import CATEGORIES as _MZ
    except Exception:
        _MZ = {}
    from shared.tasks import canonical, legacy
    out = {}
    for slug in sorted(set(CATEGORIES) | set(_MZ)):
        info = _MZ.get(slug) or _MZ.get(canonical(slug)) or _MZ.get(legacy(slug)) or {}
        en = info.get("label_en") or " ".join(w.upper() if w in ("ppu", "obb", "3d") else w.capitalize()
                                             for w in slug.split("_"))
        out[slug] = {lang: info.get(f"label_{lang}") or en for lang in _LANGS}
    return out
