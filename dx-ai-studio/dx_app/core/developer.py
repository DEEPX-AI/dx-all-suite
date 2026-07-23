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
        except:continue
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


def dev_add(tok,mn,tt,lang,cat,pp,sync_only=False,confirm_overwrite=False):
    err=require_lab(tok)
    if err:return err
    err=_require_lab_model_name(mn)
    if err:return err
    err=_require_lab_category(cat)
    if err:return err
    sh=SCRIPTS_DIR/"add_model.sh"
    if not sh.exists():return{"error":"add_model.sh not found"}
    bases={"cpp":[CPP_DIR],"python":[PY_DIR],"both":[CPP_DIR,PY_DIR]}.get(lang,[CPP_DIR,PY_DIR])
    existing=[]
    for base in bases:
        try:
            target=resolve_under(str(base/cat/mn),(base,))
        except ValueError as e:
            return{"error":str(e),"status":400}
        if target.exists():
            existing.append(str(target.relative_to(DX_APP_ROOT)) if DX_APP_ROOT in target.parents else str(target))
    if existing and not confirm_overwrite:
        return{"error":"Overwrite confirmation required","status":400,"existing":existing}
    # Map GUI task type (e.g. "object_detection") to add_model.sh type (e.g. "detection")
    script_tt=_TASK_TYPE_MAP.get(tt,tt)
    # --category uses the directory name (object_detection, pose_estimation, etc.)
    cmd=["bash",str(sh),mn,script_tt,"--lang",lang,"--category",cat]
    if pp:cmd+=["--postprocessor",pp]
    if sync_only:cmd.append("--sync-only")
    try:
        r=subprocess.run(cmd,capture_output=True,text=True,cwd=str(DX_APP_ROOT),timeout=120)
        return{"ok":r.returncode==0,"output":r.stdout+r.stderr}
    except Exception as e:return{"error":str(e)}

def dev_delete(tok,mn,lang="both",confirm=""):
    err=require_lab(tok)
    if err:return err
    err=_require_lab_model_name(mn)
    if err:return err
    if confirm != f"delete:{mn}":
        return {"error": "Delete confirmation required", "status": 400}
    deleted=[]
    bases={"cpp":[CPP_DIR],"python":[PY_DIR],"both":[CPP_DIR,PY_DIR]}.get(lang,[CPP_DIR,PY_DIR])
    for base in bases:
        for cd in base.iterdir():
            if not cd.is_dir() or cd.name in SKIP_CAT:continue
            try:
                t=resolve_under(str(cd/mn),(base,))
            except ValueError:
                continue
            if t.is_dir():shutil.rmtree(t);deleted.append(str(t.relative_to(DX_APP_ROOT)))
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
    raw_path = Path(model_path)
    candidate = str(DX_APP_ROOT / raw_path) if not raw_path.is_absolute() else str(raw_path)
    try:
        resolve_existing_file(candidate, MODEL_INPUT_ROOTS, (".dxnn", ".onnx"))
    except ValueError as e:
        return {"error": str(e)}
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
    download_url = None
    model_name = model_path.split("/")[-1] if "/" in model_path else model_path
    try:
        import tarfile
        tar_name = f"pkg_{model_name}_{lang}_{int(time.time())}.tar.gz"
        tar_path = OUTPUTS_DIR / tar_name
        pkg_dirs = [p for p in OUTPUTS_DIR.iterdir() if p.is_dir() and model_name in p.name]
        if pkg_dirs:
            with tarfile.open(tar_path, "w:gz") as tar:
                for d in pkg_dirs:
                    tar.add(d, arcname=d.name)
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
    except:r["uname"]=platform.uname()._asdict()
    try:r["npu_driver"]=subprocess.check_output(["dxrt-cli","--version"],text=True,timeout=5).strip()
    except:r["npu_driver"]="N/A"
    ts=time.strftime("%Y%m%d_%H%M%S");dst=OUTPUTS_DIR/f"bugreport_{ts}.json"
    dst.write_text(json.dumps(r,indent=2,default=str));r["saved_to"]=f"outputs/bugreport_{ts}.json"
    return r

def save_capture(img_b64,filename=None):
    if not filename:filename=f"capture_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
    fn=re.sub(r'[^\w\-_.]','_',filename);dst=OUTPUTS_DIR/fn
    try:dst.write_bytes(base64.b64decode(img_b64));return{"ok":True,"url":f"/outputs/{fn}","filename":fn}
    except Exception as e:return{"error":str(e)}
