"""DX-APP Developer mode — model management, skeleton generation, git."""

import os, re, json, time, hashlib, subprocess, shutil, base64, secrets
from pathlib import Path
from dx_app.core import config
from dx_app.core.config import (DX_APP_ROOT, CPP_DIR, PY_DIR, ASSETS_DIR, SCRIPTS_DIR,
                    OUTPUTS_DIR, _lab_sessions, _lab_lock,
                    _LAB_SESSION_MAX, _LAB_SESSION_TTL_SECONDS)
from dx_app.core.dx_app_security import resolve_existing_file, resolve_under
from dx_app.core.models import _reload_reg, _sanitize_model_name, _to_class_name

SKIP_CAT = config.SKIP_CAT
_LAB_NAME_RE = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')


def _require_lab_model_name(model_name):
    if not model_name or not isinstance(model_name, str) or not _LAB_NAME_RE.fullmatch(model_name):
        return {"error": "Invalid model name. Use letters, numbers, underscores; start with a letter.", "status": 400}
    return None


def _require_lab_category(category):
    if not category or not isinstance(category, str):
        return {"error": "category is required", "status": 400}
    if "/" in category or "\\" in category or ".." in category:
        return {"error": f"Invalid category: {category!r}", "status": 400}
    if category not in config.CATEGORIES:
        return {"error": f"Unknown category: {category!r}", "status": 400}
    return None


def _parse_multipart(handler):
    content_type=handler.headers.get("Content-Type","")
    if "multipart/form-data" not in content_type:return {},{}
    boundary=None
    for part in content_type.split(";"):
        part=part.strip()
        if part.startswith("boundary="):boundary=part[9:].strip('"');break
    if not boundary:return {},{}
    length=int(handler.headers.get("Content-Length",0))
    body=handler.rfile.read(length)
    fields={};files={}
    bnd=f"--{boundary}".encode()
    parts=body.split(bnd)
    for part in parts[1:]:
        if part.strip()==b"--" or part.strip()==b"":continue
        try:
            hdr_end=part.index(b"\r\n\r\n")
            hdr=part[:hdr_end].decode("utf-8","replace")
            data=part[hdr_end+4:]
            if data.endswith(b"\r\n"):data=data[:-2]
            m_name=re.search(r'name="([^"]+)"',hdr)
            m_file=re.search(r'filename="([^"]*)"',hdr)
            name=m_name.group(1) if m_name else "unknown"
            if m_file:
                files[name]={"filename":m_file.group(1),"data":data}
            else:
                fields[name]=data.decode("utf-8","replace")
        except Exception:continue
    return fields,files


# ── Lab session auth (replaces password-based dev auth) ────────────────────────
def _evict_expired_lab_sessions(now):
    for tok, created_at in list(_lab_sessions.items()):
        try:
            expired = now - float(created_at) > _LAB_SESSION_TTL_SECONDS
        except (TypeError, ValueError):
            expired = True
        if expired:
            _lab_sessions.pop(tok, None)


def lab_session(origin=None, server_host=None, referer=None):
    """Mint a lab session token. Rejects non-local cross-origin callers."""
    reject = _check_origin_local(origin, server_host, referer=referer)
    if reject:
        return reject
    tok = secrets.token_urlsafe(24)
    now = time.time()
    with _lab_lock:
        _evict_expired_lab_sessions(now)
        while len(_lab_sessions) >= _LAB_SESSION_MAX:
            _lab_sessions.popitem(last=False)  # evict oldest
        _lab_sessions[tok] = now
    return {"ok": True, "token": tok, "local": True}


def lab_check(tok):
    with _lab_lock:
        if not tok or tok not in _lab_sessions:
            return False
        created_at = _lab_sessions.get(tok)
        now = time.time()
        try:
            expired = now - float(created_at) > _LAB_SESSION_TTL_SECONDS
        except (TypeError, ValueError):
            expired = True
        if expired:
            _lab_sessions.pop(tok, None)
            return False
        _lab_sessions.move_to_end(tok)
        return True


def _is_local_origin(origin_str, server_host=None):
    """Return True if origin_str represents a local address.

    DX_ALLOW_REMOTE_ORIGIN=1 accepts any origin — set it to expose the privileged
    Lab over a trusted LAN (default off keeps Lab local-only for CSRF safety).
    """
    if os.environ.get("DX_ALLOW_REMOTE_ORIGIN", "").strip().lower() in ("1", "true", "yes"):
        return True
    if not origin_str:
        return True  # absent Origin = same-origin (non-CORS)
    from urllib.parse import urlparse
    parsed = urlparse(origin_str)
    host = (parsed.hostname or "").lower()
    local_hosts = {"localhost", "127.0.0.1", "[::1]", "::1"}
    if server_host:
        local_hosts.add(server_host.lower())
    return host in local_hosts


def _check_origin_local(origin, server_host=None, referer=None):
    """Return an error dict if origin or referer is non-local, else None."""
    if origin is not None and not _is_local_origin(origin, server_host):
        return {"error": "Cross-origin access denied", "status": 403}
    if origin is None and referer is not None and not _is_local_origin(referer, server_host):
        return {"error": "Cross-origin access denied", "status": 403}
    return None


def require_lab(tok):
    if not lab_check(tok):
        return {"error": "Lab session required", "status": 403}
    return None


_TASK_TYPE_MAP={
    "object_detection":"detection","classification":"classification",
    "semantic_segmentation":"semantic_segmentation","instance_segmentation":"instance_segmentation",
    "pose_estimation":"pose","face_detection":"face_detection","obb_detection":"obb",
    "depth_estimation":"depth_estimation","image_denoising":"image_denoising",
    "super_resolution":"super_resolution","image_enhancement":"image_enhancement",
    "embedding":"embedding","ppu":"ppu",
}


# add_model.sh copies a reference example and renames it. Its built-in references are legacy folders
# (object_detection/yolov8n …) that the per-model layout no longer has, so Studio always names the
# reference itself with --base-model: an example of the same category that has a factory in every
# requested language. With --category and --base-model the task type only labels the script's output,
# but it must be one the script accepts.
_SCRIPT_LANG={"python":"py","cpp":"cpp","both":"both"}
_SCRIPT_TASK_TYPES={"detection","classification","semantic_segmentation","instance_segmentation","pose",
    "face_detection","obb","depth_estimation","image_denoising","super_resolution","image_enhancement",
    "ppu","embedding","hand_landmark","attribute_recognition","reid"}
_ANSI_RE=re.compile(r"\x1b\[[0-9;]*m")


def _script_task_type(cat):
    tt=_TASK_TYPE_MAP.get(cat,cat)
    if tt in _SCRIPT_TASK_TYPES:return tt
    for key,val in (("classification","classification"),("segmentation","semantic_segmentation"),
                    ("pose","pose"),("oriented","obb"),("depth","depth_estimation"),("face","face_detection"),
                    ("hand","hand_landmark"),("reid","reid"),("attribute","attribute_recognition"),
                    ("enhancement","image_enhancement"),("retrieval","embedding"),("recognition","embedding")):
        if key in cat:return val
    return "detection"


def _has_factory(d,name,lang):
    return bool(d) and (d/"factory"/f"{name}_factory{'.py' if lang=='python' else '.hpp'}").is_file()


def reference_examples(root=None):
    """{category: [{"name", "family", "langs"}]} — the examples Add Model can start from.

    An example qualifies per language when it has ``factory/<name>_factory.{py,hpp}`` (add_model.sh reads the
    class names from it). A name that appears under two tasks is left out: add_model.sh finds the base by
    folder name alone and would pick either one.
    """
    from collections import Counter
    from shared import dx_app_layout as _layout
    root=Path(root or DX_APP_ROOT)
    _layout.clear_cache()
    exs=sorted(_layout.examples(root),key=lambda e:(e.task,e.name))
    seen=Counter(e.name for e in exs)
    out={}
    for ex in exs:
        if seen[ex.name]>1:continue
        langs=[l for l in ("python","cpp") if _has_factory(ex.dir(l),ex.name,l)]
        if langs:out.setdefault(ex.task,[]).append({"name":ex.name,"family":ex.family,"langs":langs})
    return out


def pick_reference(cat,lang,base_model=""):
    """(name, None) or (None, error) — the example Add Model copies for this category and language."""
    need=["python","cpp"] if lang=="both" else [lang]
    cands=[r for r in reference_examples().get(cat,[]) if all(l in r["langs"] for l in need)]
    if base_model:
        if any(r["name"]==base_model for r in cands):return base_model,None
        return None,{"error":f"{base_model} is not a {cat} example with {' and '.join(need)} code to start from",
                     "error_code":"unknown_base_model","status":400}
    if not cands:
        return None,{"error":f"No {cat} example has {' and '.join(need)} code to start from",
                     "error_code":"no_reference","status":400}
    return cands[0]["name"],None


def _rename_copied_variant(cat,mn,ref,bases):
    """add_model.sh renames files and classes but not the variant a per-model example is pinned to —
    without this the copy dies with "no variant config '<ref>'"."""
    for base in bases:
        d=base/cat/mn
        cfg=d/"config.json"
        if cfg.is_file():
            try:
                data=json.loads(cfg.read_text(encoding="utf-8"))
                if isinstance(data,dict) and data.get("variant")==ref:
                    data["variant"]=mn
                    cfg.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
            except (OSError,ValueError):pass
        for py in d.glob("*.py"):
            text=py.read_text(encoding="utf-8")
            new=(text.replace(f'_FIXED_VARIANT = "{ref}"',f'_FIXED_VARIANT = "{mn}"')
                 .replace(f'description="{ref} ',f'description="{mn} ').replace(f'"""{ref} ',f'"""{mn} '))
            if new!=text:py.write_text(new,encoding="utf-8")


def dev_add(tok,mn,tt,lang,cat,pp,sync_only=False,confirm_overwrite=False,base_model=""):
    err=require_lab(tok)
    if err:return err
    err=_require_lab_model_name(mn)
    if err:return err
    err=_require_lab_category(cat)
    if err:return err
    sh=SCRIPTS_DIR/"add_model.sh"
    if not sh.exists():return{"error":"add_model.sh not found"}
    if lang not in _SCRIPT_LANG:lang="both"
    bases={"cpp":[CPP_DIR],"python":[PY_DIR],"both":[CPP_DIR,PY_DIR]}[lang]
    existing=[];absent=[]
    for base in bases:
        try:
            target=resolve_under(str(base/cat/mn),(base,))
        except ValueError as e:
            return{"error":str(e),"status":400}
        rel=str(target.relative_to(DX_APP_ROOT)) if DX_APP_ROOT in target.parents else str(target)
        (existing if target.exists() else absent).append(rel)
    if existing and not confirm_overwrite:
        return{"error":"Overwrite confirmation required","status":400,"existing":existing}
    ref,err=pick_reference(cat,lang,base_model)
    if err:return err
    cmd=["bash",str(sh),mn,_script_task_type(cat),"--lang",_SCRIPT_LANG[lang],"--category",cat,"--base-model",ref]
    if sync_only:cmd.append("--sync-only")
    try:
        r=subprocess.run(cmd,capture_output=True,text=True,cwd=str(DX_APP_ROOT),timeout=120)
    except Exception as e:return{"error":str(e)}
    out=_ANSI_RE.sub("",r.stdout+r.stderr)
    from shared import dx_app_layout as _layout
    _layout.clear_cache()
    if r.returncode!=0:
        lines=[l.strip() for l in out.splitlines() if l.strip()]
        reason=next((l for l in reversed(lines) if "ERROR" in l or "error" in l),lines[-1] if lines else "add_model.sh failed")
        return{"ok":False,"error":reason,"output":out,"reference":ref}
    _rename_copied_variant(cat,mn,ref,bases)
    created=[rel for rel in absent if (DX_APP_ROOT/rel).is_dir()]
    return{"ok":True,"output":out,"reference":ref,"created":created,"overwrote":existing}

def dev_delete(tok,mn,lang="both",confirm=""):
    err=require_lab(tok)
    if err:return err
    err=_require_lab_model_name(mn)
    if err:return err
    if confirm != f"delete:{mn}":
        return {"error": "Delete confirmation required", "status": 400}
    deleted=[]
    bases={"cpp":[CPP_DIR],"python":[PY_DIR],"both":[CPP_DIR,PY_DIR]}.get(lang,[CPP_DIR,PY_DIR])
    # 예제 폴더는 resolver 가 찾는다 — legacy <task>/<model>, per-model <task>/<family>/<stem> (shared/dx_app_layout.py)
    from shared import dx_app_layout as _layout
    _layout.clear_cache()
    for base in bases:
        lang_key="cpp" if base==CPP_DIR else "python"
        targets=[ex.dir(lang_key) for ex in _layout.examples(base.parent.parent) if ex.name==mn and ex.dir(lang_key)]
        for tgt in targets:
            try:
                t=resolve_under(str(tgt),(base,))
            except ValueError:
                continue
            if t.is_dir():shutil.rmtree(t);deleted.append(str(t.relative_to(DX_APP_ROOT)))
    _layout.clear_cache()
    return{"ok":True,"deleted":deleted}

def dev_git(tok,msg,push=False,confirm_push=""):
    err=require_lab(tok)
    if err:return err
    if push and confirm_push != "push":
        return {"error": "Push confirmation required", "status": 400}
    try:
        r1=subprocess.run(["git","add","."],capture_output=True,text=True,cwd=str(DX_APP_ROOT),timeout=30)
        r2=subprocess.run(["git","commit","-m",msg],capture_output=True,text=True,cwd=str(DX_APP_ROOT),timeout=30)
        out=r1.stdout+r2.stdout+r2.stderr
        if push and r2.returncode==0:
            r3=subprocess.run(["git","push"],capture_output=True,text=True,cwd=str(DX_APP_ROOT),timeout=60)
            out+="\n"+r3.stdout+r3.stderr
        return{"ok":r2.returncode==0,"output":out}
    except Exception as e:return{"error":str(e)}

MODEL_INPUT_ROOTS = (DX_APP_ROOT, ASSETS_DIR, OUTPUTS_DIR)


def extract_model_package(model_path, lang="both"):
    """Public extraction — validates path against allowed roots."""
    sh = SCRIPTS_DIR / "extract_model_package.sh"
    if not sh.exists():
        return {"error": "extract_model_package.sh not found"}
    # The extract script packages a model's EXAMPLE SOURCES from a "category/model"
    # directory (e.g. classification/densenet169) that lives under src/python_example and
    # src/cpp_example — it is NOT a .dxnn/.onnx weight file under DX_APP_ROOT. Validate the
    # path as a source directory under those roots (traversal-safe via resolve_under).
    raw_path = Path(model_path)
    src_dir = None
    for root in (PY_DIR, CPP_DIR):
        probe = str(raw_path) if raw_path.is_absolute() else str(root / raw_path)
        try:
            cand = resolve_under(probe, (root,))
        except ValueError:
            continue
        if cand.is_dir():
            src_dir = cand
            break
    if src_dir is None:
        return {"error": f"Model source not found: {model_path}"}
    out_dir = str(OUTPUTS_DIR)
    langs = ["cpp", "py"] if lang == "both" else [lang if lang != "python" else "py"]
    results = []
    for l in langs:
        try:
            r = subprocess.run(["bash", str(sh), model_path, "--lang", l, "--output-dir", out_dir],
                               capture_output=True, text=True, cwd=str(DX_APP_ROOT), timeout=60)
            results.append({"lang": l, "ok": r.returncode == 0, "output": (r.stdout + r.stderr)[-500:]})
        except Exception as e:
            results.append({"lang": l, "ok": False, "error": str(e)})
    # 추출기는 outputs/<lang>/<model_path>/ 에 만든다. 예전에는 outputs 바로 아래에서 이름이 맞는 폴더를 찾아
    # per-model layout (py/object_detection/yolo26/yolo26-n_640x640) 에서는 아무것도 못 찾아 download_url 이
    # 비었다. python 은 config.json 이 이름으로 부르는 processor 가 빠지지 않게 common/ 을 채운다 (2026-10-11 audit).
    download_url = None
    model_name = model_path.rstrip("/").split("/")[-1]
    pkg_dirs = []
    for l in langs:
        d = OUTPUTS_DIR / l / model_path.strip("/")
        if d.is_dir():
            if l == "py":
                try:
                    from dx_app.core.lab_package import _complete_python_common
                    _complete_python_common(DX_APP_ROOT, d)
                except Exception as ex:
                    print(f"[EXTRACT] common/ completion failed: {ex}")
            pkg_dirs.append((l, d))
    try:
        import tarfile
        if pkg_dirs:
            tar_name = f"pkg_{model_name}_{lang}_{int(time.time())}.tar.gz"
            with tarfile.open(OUTPUTS_DIR / tar_name, "w:gz") as tar:
                for l, d in pkg_dirs:
                    tar.add(d, arcname=f"{l}/{model_name}", filter=lambda ti: None if "__pycache__" in ti.name else ti)
            download_url = f"/outputs/{tar_name}"
    except Exception as ex:
        print(f"[EXTRACT] tar.gz creation failed: {ex}")
    return {"ok": all(r["ok"] for r in results), "results": results, "output_dir": out_dir,
            "download_url": download_url}


def dev_extract(tok, model_path, lang="both"):
    """Lab-authenticated extraction."""
    err = require_lab(tok)
    if err:
        return err
    return extract_model_package(model_path, lang)


_VALID_SCAFFOLD_TYPES = {"full", "postprocessor"}
_VALID_LANGS = {"both", "cpp", "python"}


def _task_name_normalize(task_name):
    """Validate and normalize a task name. Returns (normalized, error_dict_or_None)."""
    if not task_name or not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', task_name):
        return None, {"error": "Invalid task name. Use lowercase letters, numbers, underscores.", "status": 400}
    return task_name.lower().replace("-", "_"), None


def build_task_file_plan(task_name, lang="both", scaffold_type="full", cpp_dir=None, py_dir=None):
    """Return list of (absolute_path, content) tuples for task skeleton files.

    Pure computation — does not write to disk or validate auth.
    Returns (file_plan, error_dict_or_None).
    """
    task_name, err = _task_name_normalize(task_name)
    if err:
        return [], err
    if scaffold_type not in _VALID_SCAFFOLD_TYPES:
        return [], {"error": f"Unknown scaffold_type: {scaffold_type!r}. Use one of: {', '.join(sorted(_VALID_SCAFFOLD_TYPES))}", "status": 400}
    if lang not in _VALID_LANGS:
        return [], {"error": f"Unknown lang: {lang!r}. Use one of: {', '.join(sorted(_VALID_LANGS))}", "status": 400}

    if cpp_dir is None:
        cpp_dir = CPP_DIR
    if py_dir is None:
        py_dir = PY_DIR

    task_upper = "".join(w.capitalize() for w in task_name.split("_"))
    files = []

    cpp_base = cpp_dir / "common"
    py_base = py_dir / "common"

    cpp_templates = {}
    if scaffold_type == "full":
        cpp_templates = {
            cpp_base / "base" / f"i_{task_name}_factory.hpp": f"""/**
 * @file i_{task_name}_factory.hpp
 * @brief {task_upper} Abstract Factory interface
 * AUTO-GENERATED by DX-APP GUI
 */
#pragma once
#include <memory>
#include "common/processors/{task_name}_postprocessor.hpp"
#include "common/visualizers/{task_name}_visualizer.hpp"
#include "common/inputs/preprocessor.hpp"

class I{task_upper}Factory {{
public:
    virtual ~I{task_upper}Factory() = default;
    virtual std::unique_ptr<IPreprocessor> createPreprocessor() = 0;
    virtual std::unique_ptr<IPostprocessor> createPostprocessor() = 0;
    virtual std::unique_ptr<{task_upper}Visualizer> createVisualizer() = 0;
    virtual std::string getModelName() const = 0;
}};
""",
            cpp_base / "processors" / f"{task_name}_postprocessor.hpp": f"""/**
 * @file {task_name}_postprocessor.hpp
 * @brief {task_upper} Postprocessor
 * AUTO-GENERATED by DX-APP GUI
 */
#pragma once
#include <vector>
#include <string>
#include <opencv2/opencv.hpp>
#include "dx/dxrt.h"

struct {task_upper}Result {{
    // TODO(TEMPLATE-PLACEHOLDER): Add fields specific to {task_name} outputs
    float confidence{{0.0f}};
    cv::Mat output_map;
}};

class {task_upper}Postprocessor {{
public:
    {task_upper}Postprocessor(int input_w = 640, int input_h = 640)
        : input_w_(input_w), input_h_(input_h) {{}}
    virtual ~{task_upper}Postprocessor() = default;
    virtual std::vector<{task_upper}Result> postprocess(
        const std::vector<dx_tensor_t>& output_tensors, int orig_w, int orig_h) {{
        (void)output_tensors; (void)orig_w; (void)orig_h;
        return {{}};
    }}
    virtual std::vector<std::string> get_npu_output_names() const {{ return {{"output"}}; }}
    virtual std::vector<std::string> get_cpu_output_names() const {{ return {{"output"}}; }}
protected:
    int input_w_; int input_h_;
}};
""",
            cpp_base / "visualizers" / f"{task_name}_visualizer.hpp": f"""/**
 * @file {task_name}_visualizer.hpp
 * @brief {task_upper} result visualizer
 * AUTO-GENERATED by DX-APP GUI
 */
#pragma once
#include <opencv2/opencv.hpp>
#include "common/processors/{task_name}_postprocessor.hpp"

class {task_upper}Visualizer {{
public:
    virtual ~{task_upper}Visualizer() = default;
    virtual cv::Mat draw(const cv::Mat& frame, const std::vector<{task_upper}Result>& results) {{
        cv::Mat output = frame.clone();
        // TODO(TEMPLATE-PLACEHOLDER): Draw results on output image
        return output;
    }}
}};
""",
            cpp_base / "runner" / f"sync_{task_name}_runner.hpp": f"""/**
 * @file sync_{task_name}_runner.hpp
 * @brief Synchronous {task_upper} inference runner
 * AUTO-GENERATED by DX-APP GUI — see sync_detection_runner.hpp for reference
 */
#pragma once
#include "common/base/i_{task_name}_factory.hpp"

class Sync{task_upper}Runner {{
public:
    static int run(I{task_upper}Factory& factory, int argc, char* argv[]) {{
        (void)factory; (void)argc; (void)argv;
        // TODO(TEMPLATE-PLACEHOLDER): Implement sync inference loop
        return 0;
    }}
}};
""",
            cpp_base / "runner" / f"async_{task_name}_runner.hpp": f"""/**
 * @file async_{task_name}_runner.hpp
 * @brief Asynchronous {task_upper} inference runner
 * AUTO-GENERATED by DX-APP GUI — see async_detection_runner.hpp for reference
 */
#pragma once
#include "common/base/i_{task_name}_factory.hpp"

class Async{task_upper}Runner {{
public:
    static int run(I{task_upper}Factory& factory, int argc, char* argv[]) {{
        (void)factory; (void)argc; (void)argv;
        // TODO(TEMPLATE-PLACEHOLDER): Implement async inference loop
        return 0;
    }}
}};
""",
        }
    elif scaffold_type == "postprocessor":
        cpp_templates = {
            cpp_base / "processors" / f"{task_name}_postprocessor.hpp": f"""/**
 * @file {task_name}_postprocessor.hpp
 * @brief {task_upper} Postprocessor
 * AUTO-GENERATED by DX-APP GUI
 */
#pragma once
#include <vector>
#include <string>
#include <opencv2/opencv.hpp>
#include "dx/dxrt.h"

struct {task_upper}Result {{
    // TODO(TEMPLATE-PLACEHOLDER): Add fields specific to {task_name} outputs
    float confidence{{0.0f}};
    cv::Mat output_map;
}};

class {task_upper}Postprocessor {{
public:
    {task_upper}Postprocessor(int input_w = 640, int input_h = 640)
        : input_w_(input_w), input_h_(input_h) {{}}
    virtual ~{task_upper}Postprocessor() = default;
    virtual std::vector<{task_upper}Result> postprocess(
        const std::vector<dx_tensor_t>& output_tensors, int orig_w, int orig_h) {{
        (void)output_tensors; (void)orig_w; (void)orig_h;
        return {{}};
    }}
    virtual std::vector<std::string> get_npu_output_names() const {{ return {{"output"}}; }}
    virtual std::vector<std::string> get_cpu_output_names() const {{ return {{"output"}}; }}
protected:
    int input_w_; int input_h_;
}};
""",
        }

    task_camel = "".join(w.capitalize() for w in task_name.split("_"))
    py_templates = {}
    if scaffold_type == "full":
        py_templates = {
            py_base / "processors" / f"{task_name}_postprocessor.py": f'''"""
{task_name}_postprocessor.py - {task_camel} Postprocessor
AUTO-GENERATED by DX-APP GUI
"""
import numpy as np
from typing import List, Dict, Any

class {task_camel}Postprocessor:
    def __init__(self, input_width=640, input_height=640):
        self.input_width = input_width
        self.input_height = input_height

    def postprocess(self, outputs, orig_width, orig_height):
        # TODO(TEMPLATE-PLACEHOLDER): Parse output tensors
        return []
''',
            py_base / "visualizers" / f"{task_name}_visualizer.py": f'''"""
{task_name}_visualizer.py - {task_camel} Visualizer
AUTO-GENERATED by DX-APP GUI
"""
import cv2
import numpy as np

class {task_camel}Visualizer:
    def draw(self, frame, results):
        output = frame.copy()
        # TODO(TEMPLATE-PLACEHOLDER): Draw results
        return output
''',
        }
    elif scaffold_type == "postprocessor":
        py_templates = {
            py_base / "processors" / f"{task_name}_postprocessor.py": f'''"""
{task_name}_postprocessor.py - {task_camel} Postprocessor
AUTO-GENERATED by DX-APP GUI
"""
import numpy as np
from typing import List, Dict, Any

class {task_camel}Postprocessor:
    def __init__(self, input_width=640, input_height=640):
        self.input_width = input_width
        self.input_height = input_height

    def postprocess(self, outputs, orig_width, orig_height):
        # TODO(TEMPLATE-PLACEHOLDER): Parse output tensors
        return []
''',
        }

    if lang in ("both", "cpp"):
        files.extend(cpp_templates.items())
    if lang in ("both", "python"):
        files.extend(py_templates.items())

    return files, None


def dev_new_task(tok,task_name,lang="both",confirm_overwrite=False,scaffold_type="full"):
    """Create new task skeleton files (dx_tool.sh option 7)."""
    err=require_lab(tok)
    if err:return err

    file_plan, plan_err = build_task_file_plan(task_name, lang, scaffold_type)
    if plan_err:
        return plan_err

    task_name, _ = _task_name_normalize(task_name)
    task_upper = "".join(w.capitalize() for w in task_name.split("_"))

    existing=[str(fp) for fp, _ in file_plan if fp.exists()]
    if existing and not confirm_overwrite:
        return{"error":"Overwrite confirmation required","status":400,"existing":existing}

    created=[]
    for fp, content in file_plan:
        fp.parent.mkdir(parents=True,exist_ok=True)
        fp.write_text(content)
        created.append(str(fp.relative_to(DX_APP_ROOT)))
    return{"ok":True,"task_name":task_name,"task_upper":task_upper,"files":created,"count":len(created)}


def bug_report(model_name=None,error_log=None,model_config=None):
    import platform
    from shared.hardware import get_sysinfo, get_hw
    r={"generated_at":time.strftime("%Y-%m-%d %H:%M:%S"),"system":get_sysinfo(),
       "hw_status":get_hw(),"model_name":model_name,"error_log":error_log,"model_config":model_config}
    try:r["uname"]=subprocess.check_output(["uname","-a"],text=True,timeout=5).strip()
    except Exception:r["uname"]=platform.uname()._asdict()
    try:r["npu_driver"]=subprocess.check_output(["dxrt-cli","--version"],text=True,timeout=5).strip()
    except Exception:r["npu_driver"]="N/A"
    ts=time.strftime("%Y%m%d_%H%M%S");dst=OUTPUTS_DIR/f"bugreport_{ts}.json"
    dst.write_text(json.dumps(r,indent=2,default=str));r["saved_to"]=f"outputs/bugreport_{ts}.json"
    return r

def save_capture(img_b64,filename=None):
    if not filename:filename=f"capture_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
    fn=re.sub(r'[^\w\-_.]','_',filename);dst=OUTPUTS_DIR/fn
    try:dst.write_bytes(base64.b64decode(img_b64));return{"ok":True,"url":f"/outputs/{fn}","filename":fn}
    except Exception as e:return{"error":str(e)}
