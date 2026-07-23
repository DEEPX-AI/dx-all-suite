"""DX-APP Model registry — scanning, loading, and model info."""

import os, re, json
from pathlib import Path
from dx_app.core.config import (CPP_DIR, PY_DIR, ASSETS_DIR, CONFIG_FILE, SAMPLE_DIR,
                    SKIP_CAT, CATEGORIES, CAT_LABEL, CAT_IMAGE, CAT_VIDEO,
                    TASK_TYPES, POSTPROCESSORS, DX_APP_ROOT)
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
        fd=CPP_DIR/cat/mn/"factory"
        if fd.is_dir():
            for hpp in fd.glob("*.hpp"):
                m=re.search(r'#include\s+"[^"]*?([a-z_]+_postprocessor)\.hpp"',hpp.read_text(errors="replace"))
                if m:
                    i["name"]=m.group(1);pp=CPP_DIR/"common"/"processors"/f"{i['name']}.hpp"
                    if pp.exists():i["file"]=str(pp.relative_to(DX_APP_ROOT))
                break
    else:
        fd=PY_DIR/cat/mn/"factory"
        if fd.is_dir():
            for pyf in fd.glob("*.py"):
                if "__init__" in pyf.name:continue
                m=re.search(r'from\s+\S*?([a-z_]+_postprocessor)\s+import|import\s+.*?([a-z_]+_postprocessor)',pyf.read_text(errors="replace"))
                if m:
                    i["name"]=m.group(1) or m.group(2);pp=PY_DIR/"common"/"processors"/f"{i['name']}.py"
                    if pp.exists():i["file"]=str(pp.relative_to(DX_APP_ROOT))
                break
    return i

def get_models():
    models={}
    for lang,base in[("cpp",CPP_DIR),("python",PY_DIR)]:
        if not base.is_dir():continue
        for cd in sorted(base.iterdir()):
            if not cd.is_dir() or cd.name in SKIP_CAT:continue
            cat=cd.name
            for md in sorted(cd.iterdir()):
                if not md.is_dir() or md.name in SKIP_CAT or md.name.startswith("_"):continue
                mn=md.name;ext=".cpp" if lang=="cpp" else ".py"
                hs=(md/f"{mn}_sync{ext}").exists();ha=(md/f"{mn}_async{ext}").exists()
                if not hs and not ha:continue
                key=f"{cat}/{mn}"
                if key not in models:
                    reg=_REG.get(mn,{});mf=reg.get("file","")
                    if mf.startswith("-"):
                        import shlex as _shlex
                        _args=_shlex.split(mf)
                        _mexists=all((DX_APP_ROOT/a).exists() for a in _args if not a.startswith("-") and a.endswith(".dxnn"))
                    else:
                        _mexists=bool(mf)and(DX_APP_ROOT/mf).exists()
                    models[key]={"name":mn,"category":cat,"category_label":CAT_LABEL.get(cat,cat),
                     "cpp":False,"python":False,"cpp_sync":False,"cpp_async":False,
                     "py_sync":False,"py_async":False,"model_file":mf,
                     "model_exists":_mexists,
                     "npu_core":"","dataset":"","input_resolution":"","config":{}}
                    cf=md/"config.json"
                    if cf.exists():
                        try:
                            cfg=json.loads(cf.read_text())
                            models[key].update({"config":cfg,
                             "npu_core":cfg.get("npu_core",cfg.get("NPU_CORE","")),
                             "dataset":cfg.get("dataset",cfg.get("DATASET","")),
                             "input_resolution":cfg.get("input_size",cfg.get("INPUT_SIZE",""))})
                        except:pass
                if lang=="cpp":models[key].update({"cpp":True,"cpp_sync":hs,"cpp_async":ha})
                else:models[key].update({"python":True,"py_sync":hs,"py_async":ha})
    # Also include registry-only models (deployed via compiler but no source code yet)
    for mn,reg in _REG.items():
        cat=reg.get("category","custom")
        key=f"{cat}/{mn}"
        if key not in models:
            mf=reg.get("file","")
            if mf.startswith("-"):
                import shlex as _shlex
                _args=_shlex.split(mf)
                _mexists=all((DX_APP_ROOT/a).exists() for a in _args if not a.startswith("-") and a.endswith(".dxnn"))
            else:
                _mexists=bool(mf) and (DX_APP_ROOT/mf).exists()
            if _mexists:  # only show if the model file actually exists
                models[key]={"name":mn,"category":cat,"category_label":CAT_LABEL.get(cat,cat),
                 "cpp":True,"python":False,"cpp_sync":True,"cpp_async":False,
                 "py_sync":False,"py_async":False,"model_file":mf,
                 "model_exists":True,
                 "npu_core":"","dataset":"","input_resolution":"","config":{}}
    return list(models.values())

def get_model_info(name):
    info={"name":name,"files":{},"postprocessors":{}};reg=_REG.get(name,{})
    mf=reg.get("file","")
    if mf.startswith("-"):
        import shlex as _shlex
        _args=_shlex.split(mf)
        _mexists=all((DX_APP_ROOT/a).exists() for a in _args if not a.startswith("-") and a.endswith(".dxnn"))
    else:
        _mexists=bool(mf)and(DX_APP_ROOT/mf).exists()
    info.update({"model_file":mf,"model_exists":_mexists})
    for lang,base in[("cpp",CPP_DIR),("python",PY_DIR)]:
        for cd in base.iterdir():
            if not cd.is_dir() or cd.name in SKIP_CAT:continue
            md=cd/name
            if not md.is_dir():continue
            info["category"]=cd.name;info["category_label"]=CAT_LABEL.get(cd.name,cd.name)
            lk="cpp" if lang=="cpp" else "python"
            info["files"][lk]=[str(f.relative_to(DX_APP_ROOT)) for f in sorted(md.rglob("*")) if f.is_file()]
            cf=md/"config.json"
            if cf.exists():
                try:info["config"]=json.loads(cf.read_text())
                except:info["config"]={}
            pp=_pp_info(lk,cd.name,name)
            if pp["name"]:info["postprocessors"][lk]=pp
    return info
