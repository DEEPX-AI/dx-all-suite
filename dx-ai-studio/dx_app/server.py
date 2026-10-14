#!/usr/bin/env python3
"""DX-APP Server — HTTP server entry point with all routes."""
import os, sys, json, time, re, signal, threading, webbrowser, mimetypes, shlex
import shutil
from pathlib import Path

from shared.dx_server import DXBaseHandler, DXServer, RequestBodyError
from shared import debug_log

from dx_app.core import config
from dx_app.core.config import (resolve_model_path, SCRIPT_DIR, DX_APP_ROOT, STATIC_DIR, TEMPLATES_DIR, SERVER_NAME, OUTPUTS_DIR,
                    CATEGORIES, TASK_TYPES, POSTPROCESSORS,
                    _HEARTBEAT, _HB_TIMEOUT, ASSETS_DIR, SAMPLE_DIR)
from dx_app.core.dx_app_security import (resolve_under, sanitize_filename, safe_content_disposition,
                             resolve_existing_file, resolve_existing_path, existing_onnx)

ONNX_INPUT_ROOTS = (OUTPUTS_DIR,)
from shared.paths import SUITE_ROOT as _SUITE_FOR_MODELS
_WORKSPACE_MODELS = _SUITE_FOR_MODELS / "workspace" / "res" / "models"
MODEL_INPUT_ROOTS = (DX_APP_ROOT, ASSETS_DIR, ASSETS_DIR / "models", OUTPUTS_DIR, _WORKSPACE_MODELS)
TEST_RUN_INPUT_ROOTS = (DX_APP_ROOT, SAMPLE_DIR, ASSETS_DIR, OUTPUTS_DIR)
_SAFE_ID_RE = re.compile(r'^[A-Za-z0-9_]+$')
# Model name: per-model layout stems are .dxnn names and contain '-' and '.' (3ddfa-v2_mobilenet-0.5_120x120).
# Path separators, '..' and a leading '.' are still refused.
_MODEL_NAME_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.\-]*$')
_RUN_LANGS = {"cpp", "python"}
# *_cpp_postprocess variants run the Python app with the C++ dx_postprocess pybind
# extension; they exist only as Python scripts (no C++ binary), so they're python-only.
_RUN_VARIANTS = {"sync", "async", "sync_cpp_postprocess", "async_cpp_postprocess"}
_RUN_INPUT_TYPES = {"image", "video", "camera", "rtsp"}


def _error_payload(error_key, error):
    return {"error_key": error_key, "error": error}


def _validation_error_key(message):
    if "outside allowed roots" in message:
        return "path_outside_allowed_roots"
    if "File not found" in message:
        return "model_not_found"
    if "Extension" in message:
        return "file_extension_not_allowed"
    return "invalid_payload"


def _task_defaults():
    """task -> default input, image-only, old key, so JS uses the same table as the server instead of its own copy.
    per-model layout task keys also find the values of their old key (shared/tasks.py)."""
    from dx_app.core.config import CAT_IMAGE, CAT_VIDEO, IMAGE_ONLY_CATEGORIES
    from shared.tasks import legacy
    return {c: {"image": CAT_IMAGE.get(c, ""), "video": CAT_VIDEO.get(c, ""),
                "image_only": c in IMAGE_ONLY_CATEGORIES, "legacy": legacy(c)} for c in CATEGORIES}


def _require_category(category):
    """Validate category is a known value with no path traversal. Raises ValueError."""
    if not category or not isinstance(category, str):
        raise ValueError("category is required")
    if "/" in category or "\\" in category or ".." in category:
        raise ValueError(f"Invalid category: {category!r}")
    if category in CATEGORIES:
        return category
    # legacy <-> per-model pair names (obb_detection <-> oriented_object_detection, …): older recent runs, links and
    # clients send the other layout's name (contract: tests/dx_app/test_category_alias.py)
    from shared.tasks import canonical, legacy
    for alt in (canonical(category), legacy(category)):
        if alt != category and alt in CATEGORIES:
            return alt
    raise ValueError(f"Unknown category: {category!r}")


def _require_safe_id(value, label):
    if not value or not isinstance(value, str) or not _SAFE_ID_RE.fullmatch(value):
        raise ValueError(f"Invalid {label}: {value!r}")


def _require_model_name(value):
    if not value or not isinstance(value, str) or not _MODEL_NAME_RE.fullmatch(value) or ".." in value:
        raise ValueError(f"Invalid model_name: {value!r}")


def _candidate_path(value):
    raw = Path(str(value))
    return str(raw if raw.is_absolute() else DX_APP_ROOT / raw)


def _require_model_file(model_file):
    if not model_file or not isinstance(model_file, str):
        raise ValueError("model_file is required")
    if model_file.startswith("-"):
        try:
            parts = shlex.split(model_file)
        except ValueError as e:
            raise ValueError(f"Invalid model_file arguments: {e}") from e
        for part in parts:
            if part.startswith("-"):
                continue
            has_path_shape = "/" in part or "\\" in part or ".." in part or part.endswith(".dxnn")
            if has_path_shape:
                resolve_existing_file(_candidate_path(part), MODEL_INPUT_ROOTS, (".dxnn",))
        return
    # If missing from assets/models, look in the suite's workspace/res/models (config.resolve_model_path)
    cand = _candidate_path(model_file)
    if not Path(model_file).is_absolute() and not Path(cand).is_file():
        cand = str(resolve_model_path(model_file, DX_APP_ROOT))
    resolve_existing_file(cand, MODEL_INPUT_ROOTS, (".dxnn",))


def _require_optional_input_path(value, label, allow_dir=False):
    if not value:
        return
    # image_path may be a directory for reid/embedding pair demos (sync runner expands it).
    resolver = resolve_existing_path if allow_dir else resolve_existing_file
    resolver(_candidate_path(value), TEST_RUN_INPUT_ROOTS, None)


def _validate_inference_payload(data, live=False):
    if not isinstance(data, dict):
        return _error_payload("invalid_payload", "request must be an object"), 400
    try:
        data["category"] = _require_category(data.get("category", ""))
        _require_model_name(data.get("model_name", ""))
        _require_model_file(data.get("model_file", ""))
        # Caller's name (a Model Zoo catalog id etc.) -> this dx_app's example name. Without one, another binary is borrowed
        if not str(data["model_file"]).startswith("-"):
            from shared import dx_app_layout as _layout
            data["model_name"] = _layout.example_name(DX_APP_ROOT, data["category"], data["model_name"],
                                                      data["model_file"])
        lang = data.get("lang", "cpp")
        if lang not in _RUN_LANGS:
            raise ValueError(f"Invalid lang: {lang!r}")
        variant = data.get("variant", "sync")
        if variant not in _RUN_VARIANTS:
            raise ValueError(f"Invalid variant: {variant!r}")
        if variant.endswith("_cpp_postprocess") and lang != "python":
            raise ValueError(f"variant {variant!r} is only available for lang='python'")
        input_type = data.get("input_type", "camera" if live else "image")
        if input_type not in _RUN_INPUT_TYPES:
            raise ValueError(f"Invalid input_type: {input_type!r}")
        if live and input_type not in {"camera", "rtsp", "video"}:
            raise ValueError("Live mode only supports camera/rtsp/video")
        _require_optional_input_path(data.get("upload_path"), "upload_path")
        _require_optional_input_path(data.get("image_path"), "image_path", allow_dir=True)
        _require_optional_input_path(data.get("video_path"), "video_path")
    except ValueError as e:
        msg = str(e)
        code = 403 if "outside allowed roots" in msg or "File not found" in msg or "Extension" in msg else 400
        return _error_payload(_validation_error_key(msg), msg), code
    return None, None
from dx_app.core.models import get_models, get_model_info, get_catalog
from dx_app.core.demos import build_demos_payload
from dx_app.core.assets import get_file_content, get_images, get_videos, list_outputs, delete_output
from dx_app.core.inference import (run_inference, stop_inference, run_multi, list_cameras,
                      run_inference_live, poll_inference, stop_inference_live,
                      get_inference_result, capture_live_frame, shutdown_live_processes)

def _json_bool(value, default=False):
    """Parse a JSON/query-string value into a Python bool."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False
    return bool(value)

from shared.chat import ChatEngine
from shared.chat import module_fallbacks as _module_fallbacks
from dx_app.core.modelzoo_gateway import ModelZooGateway
from dx_app.core.filesystem import fs_list
from dx_app.core.setup_steps import SETUP_STEPS, setup_status, setup_run, deep_diagnostics, setup_log, setup_input, quick_start_plan
from dx_app.core.developer import (lab_session, lab_check, require_lab, _check_origin_local, dev_add,
                       dev_delete, dev_git, dev_extract, extract_model_package,
                       dev_new_task, bug_report, save_capture)
from dx_app.core.lab_portal import lab_capabilities, plan_add_model, plan_add_model_response, apply_add_model, smoke_add_model, plan_task_scaffold_response, apply_task_scaffold, generated_files_for_manifest, validate_lab_manifest_id, start_experiment_run, launch_experiment_run, get_experiment_run, cancel_experiment_run, active_experiment_run_for_source, list_lab_manifests, change_summary_by_root, rollback_manifest, scoped_git_plan, plan_composer_quick_start, plan_composer_template, customize_composer_workflow, plan_composer_plugin_scaffold_response, apply_composer_plugin_scaffold, run_composer_workflow, export_composer_package, export_composer_recipe, import_composer_recipe
from shared.shell import ShellSpec

_modelzoo_gw = ModelZooGateway()


def _server_host_for_origin(handler):
    """Derive the server's own hostname for origin checks (never trust client Host header)."""
    _MEANINGLESS = {"", "0.0.0.0", "::", None}
    try:
        name = getattr(handler.server, "server_name", None)
        if name and name not in _MEANINGLESS:
            return name
    except AttributeError:
        pass
    try:
        addr = getattr(handler.server, "server_address", None)
        if addr and addr[0] not in _MEANINGLESS:
            return addr[0]
    except (AttributeError, IndexError, TypeError):
        pass
    return None


def _check_handler_origin_local(handler):
    """Check Origin/Referer using server-side host. Returns error dict or None."""
    origin = handler.headers.get("Origin")
    referer = handler.headers.get("Referer")
    return _check_origin_local(origin, server_host=_server_host_for_origin(handler), referer=referer)

DEFAULT_PORT = 8080
_gui_port=8080

def _hb_touch():
    config._HEARTBEAT=time.time()

_chat_engine = ChatEngine(
    app_name="dx_app",
    context_callback=lambda: {"models": [m.get("name","") for m in get_models()[:20]]},
    fallback_rules=_module_fallbacks.rules("dx_app")
)


# ── Shared App Shell ──────────────────────────────────────────
# The ten pages sit in a top tab row (no left sidebar).
# Labels are the English source text = i18n dictionary keys. Icon ids come from shared/static/dx-icons.svg.
DX_APP_PAGES = (
    ("setup", "Setup", "setup"),
    ("models", "Models", "models"),
    ("run", "Run Inference", "run"),
    ("rundemo", "Run Demo", "demo"),
    ("bench", "Benchmark", "bench"),
    ("compare", "A/B Compare", "compare"),
    ("modelzoo", "ModelZoo", "download"),
    ("lab", "Lab", "lab"),
    ("outputs", "Outputs", "folder"),
    ("reference", "Reference", "book"),
)

# The notification bell is a dx_app-only control, so it goes into the shared header's .toolbar slot.
_NOTIF_BELL = (
    '<button class="notif-bell" onclick="toggleNotifDrawer()" title="Notifications"'
    ' data-i18n-title="Notifications">\U0001F514'
    '<span class="notif-badge" id="notif-badge" style="display:none"></span></button>'
)

DX_APP_SHELL = ShellSpec(
    module_key="app",
    pages=DX_APP_PAGES,
    active_page="models",
    toolbar_extra=_NOTIF_BELL,
)

class Handler(DXBaseHandler):
    server_name = SERVER_NAME
    static_dir = STATIC_DIR
    templates_dir = TEMPLATES_DIR
    shell_spec = DX_APP_SHELL
    log_filter = ["/file/", "/static/"]
    # A graph run may carry its input images base64-encoded (graph_run allows 20 MB per image).
    json_max_bytes_by_path = {"/api/graph/run": 24 * 1024 * 1024}

    def _mjpeg_stream(self):
        slot_idx = int(self.read_query_param("slot", "0"))
        self.send_response(200)
        self.send_header("Content-Type","multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control","no-cache")
        self.end_headers()
        try:
            while True:
                frame=capture_live_frame(slot_idx)
                if frame:
                    self.wfile.write(b"--frame\r\nContent-Type: image/jpeg\r\n")
                    self.wfile.write(f"Content-Length: {len(frame)}\r\n\r\n".encode())
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
                    self.wfile.flush()
                time.sleep(0.08)  # ~12fps
        except(BrokenPipeError,ConnectionResetError):pass

    def route(self):
        path = self.url_path
        method = self.command
        _hb_touch()

        if self.handle_chat_routes(_chat_engine):
            return

        if self.route_common():
            return

        if method == "GET":
            if path.startswith("/outputs/"):
                fname=path[9:];fp=OUTPUTS_DIR/fname
                try:safe_fp=resolve_under(str(fp),(OUTPUTS_DIR,))
                except ValueError:self.send_error(403);return
                cd="attachment" if fp.suffix not in{".mp4",".webm",".jpg",".png"} else "inline"
                return self.send_file(safe_fp,cache_control="no-cache, must-revalidate",
                                      content_disposition=safe_content_disposition(cd,fname))
            if path.startswith("/file/"):
                fp=DX_APP_ROOT/path[6:]
                try:
                    safe_fp=resolve_under(str(fp),(DX_APP_ROOT,))
                except ValueError:
                    self.send_error(403);return
                return self.send_file(safe_fp)
            if path=="/api/demo-thumb":
                from dx_app.core.demos import thumbnail_path
                fp=thumbnail_path(self.read_query_param("f") or "")
                if not fp:self.send_error(404);return
                d=fp.read_bytes();self.send_response(200)
                self.send_header("Content-Type",mimetypes.guess_type(str(fp))[0] or "image/jpeg")
                self.send_header("Content-Length",len(d))
                self.send_header("Cache-Control","public, max-age=86400");self.end_headers();self.wfile.write(d)
                return
            if path=="/api/asset-thumb":
                # Downscaled preview for the composer asset grid (82x54px) — avoids
                # downloading+decoding full-res sample images. Cached on disk by src+mtime+w.
                from dx_app.core.assets import sample_thumbnail
                w=self.read_query_param("w") or "160"
                try:width=max(32,min(512,int(w)))
                except (TypeError,ValueError):width=160
                tp=sample_thumbnail(self.read_query_param("f") or "",width)
                if not tp:self.send_error(404);return
                return self.send_file(tp)
            if path=="/api/models":return self.send_json(get_models())
            if path=="/api/catalog":return self.send_json(get_catalog())
            if path=="/api/demos":return self.send_json(build_demos_payload())
            if path=="/api/model_info":
                n=self.read_query_param("name")
                return self.send_json(get_model_info(n) if n else{"error":"name required"},400 if not n else 200)
            if path=="/api/file_content":
                c=get_file_content(self.read_query_param("path"))
                return self.send_json({"content":c} if c else{"error":"not found"},404 if not c else 200)
            if path=="/api/images":return self.send_json(get_images(self.read_query_param("category") or None))
            if path=="/api/videos":return self.send_json(get_videos(self.read_query_param("category") or None))
            if path=="/api/categories":return self.send_json(CATEGORIES)
            if path=="/api/category_labels":
                from dx_app.core.models import category_labels
                return self.send_json(category_labels())
            if path=="/api/task_defaults":return self.send_json(_task_defaults())
            if path=="/api/recent_runs":
                with config._history_lock:data=list(config._recent_runs)
                return self.send_json(data)
            if path=="/api/outputs":return self.send_json(list_outputs())
            if path=="/api/postprocessors":return self.send_json(POSTPROCESSORS)
            if path=="/api/task_types":return self.send_json(TASK_TYPES)
            if path=="/api/cameras":return self.send_json(list_cameras())
            if path=="/api/live_poll":return self.send_json(poll_inference(self.read_query_param("id")))
            if path=="/api/live_result":return self.send_json(get_inference_result(self.read_query_param("id")))
            if path=="/api/run_poll":
                from dx_app.core.run_progress import poll_run
                return self.send_json(poll_run(self.read_query_param("id") or ""))
            if path=="/api/run_result":
                from dx_app.core.run_progress import get_run_result
                return self.send_json(get_run_result(self.read_query_param("id") or ""))
            if path=="/api/live_frame":return self._mjpeg_stream()
            if path=="/api/setup/status":return self.send_json(setup_status())
            if path=="/api/setup/quick-start-plan":return self.send_json({"plan":quick_start_plan()})
            if path=="/api/setup/log":return self.send_json(setup_log())
            if path=="/api/setup/diagnostics":return self.send_json(deep_diagnostics())
            if path=="/api/modelzoo/list":return self.send_json(_modelzoo_gw.list_models(self.read_query_param("source","public")))
            if path=="/api/modelzoo/status":return self.send_json(_modelzoo_gw.status())
            if path=="/api/fs/list":
                fp_list=self.read_query_param("path") or str(Path.home())
                origin_err=_check_handler_origin_local(self)
                if origin_err:return self.send_json({k:v for k,v in origin_err.items() if k!="status"},origin_err.get("status",403))
                return self.send_json(fs_list(fp_list))
            if path=="/api/fs/read":
                fp=self.read_query_param("path");rp=Path(fp).expanduser().resolve() if fp else None
                if not fp:return self.send_json({"error":"File not found"},404)
                try:resolve_under(str(rp), (Path.home(),))
                except ValueError:return self.send_json({"error":"Path is outside allowed roots"},403)
                # In-home path: still block cross-origin reads (prevents malicious web pages
                # from exfiltrating files under $HOME while dx_app runs).
                origin_err=_check_handler_origin_local(self)
                if origin_err:return self.send_json({k:v for k,v in origin_err.items() if k!="status"},origin_err.get("status",403))
                if not rp.exists() or not rp.is_file():return self.send_json({"error":"File not found"},404)
                if rp.stat().st_size>5*1024*1024:return self.send_json({"error":"File too large (exceeds 5 MB)"},400)
                try:return self.send_json({"content":rp.read_text(errors="replace")})
                except Exception as ex:return self.send_json({"error":str(ex)})
            if path.startswith("/api/graph/"):
                from dx_app.core import graph_routes
                body, code = graph_routes.handle("GET", path, self.read_query_param, None, self.headers,
                                                 _server_host_for_origin(self))
                return self.send_json(body, code)
            if path=="/api/lab/session":
                origin = self.headers.get("Origin")
                referer = self.headers.get("Referer")
                res = lab_session(origin=origin, server_host=_server_host_for_origin(self), referer=referer)
                code = res.pop("status", 200) if isinstance(res, dict) and "status" in res else 200
                return self.send_json(res, code)
            if path == "/api/lab/capabilities":
                origin_err = _check_handler_origin_local(self)
                if origin_err:
                    body = {k: v for k, v in origin_err.items() if k != "status"}
                    return self.send_json(body, origin_err.get("status", 403))
                err = require_lab(self.headers.get("X-Lab-Token"))
                if err:
                    body = {k: v for k, v in err.items() if k != "status"}
                    return self.send_json(body, err.get("status", 403))
                return self.send_json(lab_capabilities())
            if path == "/api/lab/manifests":
                origin_err = _check_handler_origin_local(self)
                if origin_err:
                    body = {k: v for k, v in origin_err.items() if k != "status"}
                    return self.send_json(body, origin_err.get("status", 403))
                err = require_lab(self.headers.get("X-Lab-Token"))
                if err:
                    body = {k: v for k, v in err.items() if k != "status"}
                    return self.send_json(body, err.get("status", 403))
                manifests = list_lab_manifests()
                enriched = []
                for manifest in manifests:
                    item = dict(manifest)
                    summary, code = change_summary_by_root(manifest["id"])
                    if code == 200:
                        item["change_summary"] = summary
                    enriched.append(item)
                return self.send_json({"manifests": enriched})
            if path.startswith("/api/lab/generated/"):
                manifest_id = path[len("/api/lab/generated/"):]
                origin_err = _check_handler_origin_local(self)
                if origin_err:
                    body = {k: v for k, v in origin_err.items() if k != "status"}
                    return self.send_json(body, origin_err.get("status", 403))
                err = require_lab(self.headers.get("X-Lab-Token"))
                if err:
                    body = {k: v for k, v in err.items() if k != "status"}
                    return self.send_json(body, err.get("status", 403))
                id_err = validate_lab_manifest_id(manifest_id)
                if id_err:
                    return self.send_json({"error": id_err}, 400)
                data, code = generated_files_for_manifest(manifest_id)
                return self.send_json(data, code)
            if path.startswith("/api/lab/experiment/") and not path.endswith("/cancel"):
                run_id = path[len("/api/lab/experiment/"):]
                origin_err = _check_handler_origin_local(self)
                if origin_err:
                    body = {k: v for k, v in origin_err.items() if k != "status"}
                    return self.send_json(body, origin_err.get("status", 403))
                err = require_lab(self.headers.get("X-Lab-Token"))
                if err:
                    body = {k: v for k, v in err.items() if k != "status"}
                    return self.send_json(body, err.get("status", 403))
                from dx_app.core.lab_portal import _validate_run_id
                id_err = _validate_run_id(run_id)
                if id_err:
                    return self.send_json(id_err[0], id_err[1])
                data, code = get_experiment_run(run_id)
                return self.send_json(data, code)
            if path=="/api/serve_onnx":
                onnx_path=self.read_query_param("path")
                if not onnx_path:return self.send_json({"error":"path required"},400)
                try:
                    op=existing_onnx(onnx_path, ONNX_INPUT_ROOTS)
                except ValueError as e:
                    return self.send_json({"error":str(e)},403)
                if not op.exists() or not op.is_file():self.send_error(404);return
                d=op.read_bytes();self.send_response(200)
                self.send_header("Content-Type","application/octet-stream")
                self.send_header("Content-Length",len(d))
                self.send_header("Content-Disposition",safe_content_disposition("inline",op.name))
                self.send_header("Cache-Control","no-cache")
                self.end_headers();self.wfile.write(d);return
            return self.route_legacy()

        if method == "POST":
            try:data=self.read_json_body()
            except RequestBodyError:raise
            except Exception:return self.send_json({"error":"Invalid JSON"},400)

            if path.startswith("/api/graph/"):
                if path == "/api/graph/run":
                    debug_log.log_action("dx_app", "graph_run",
                                         {"variant": data.get("variant", "sync") if isinstance(data, dict) else None})
                from dx_app.core import graph_routes
                body, code = graph_routes.handle("POST", path, None, data, self.headers, _server_host_for_origin(self))
                return self.send_json(body, code)

            # Lab mutating routes use X-Lab-Token only (no X-Dev-Token alias)
            _LAB_ROUTES = {"/api/dev/auth", "/api/dev/add_model", "/api/dev/delete_model",
                           "/api/dev/git_commit", "/api/dev/extract", "/api/dev/new_task",
                           "/api/lab/add_model/dry_run", "/api/lab/add_model/apply",
                           "/api/lab/add_model/smoke",
                           "/api/lab/task/dry_run", "/api/lab/task/apply",
                           "/api/lab/experiment/start",
                           "/api/lab/rollback", "/api/lab/git/plan",
                           "/api/lab/composer/quick_start", "/api/lab/composer/template",
                           "/api/lab/composer/customize",
                           "/api/lab/composer/plugin/dry_run", "/api/lab/composer/plugin/apply",
                           "/api/lab/composer/run", "/api/lab/composer/run_async",
                           "/api/lab/composer/export",
                           "/api/lab/composer/recipe/export",
                           "/api/lab/composer/recipe/import"}
            is_lab_route = path in _LAB_ROUTES or (path.startswith('/api/lab/experiment/') and path.endswith('/cancel'))
            if is_lab_route:
                tok = self.headers.get("X-Lab-Token", "")
                origin_err = _check_handler_origin_local(self)
                if origin_err:
                    body = {k: v for k, v in origin_err.items() if k != "status"}
                    return self.send_json(body, origin_err.get("status", 403))
                err = require_lab(tok)
                if err:
                    body = {k: v for k, v in err.items() if k != "status"}
                    return self.send_json(body, err.get("status", 403))
            else:
                tok = self.headers.get("X-Lab-Token") or self.headers.get("X-Dev-Token", "")

            if path=="/api/run":
                debug_log.log_action("dx_app", "run", data)
                err, code = _validate_inference_payload(data)
                if err:
                    return self.send_json(err, code)
                r=run_inference(
                    model_name=data.get("model_name",""),category=data.get("category",""),
                    model_file=data.get("model_file",""),lang=data.get("lang","cpp"),
                    variant=data.get("variant","sync"),input_type=data.get("input_type","image"),
                    image_path=data.get("image_path"),video_path=data.get("video_path"),
                    device_id=data.get("device_id"),
                    conf_threshold=data.get("conf_threshold"),nms_threshold=data.get("nms_threshold"),
                    config_overrides=data.get("config_overrides"),
                    upload_path=data.get("upload_path"),loop=data.get("loop"),
                    camera_id=data.get("camera_id"),rtsp_url=data.get("rtsp_url"),
                    save_output=_json_bool(data.get("save_output", True), default=True),
                    image_base64=data.get("image_base64"))
                return self.send_json(r)

            if path=="/api/run_async":
                debug_log.log_action("dx_app", "run_async", data)
                # Non-blocking variant of /api/run: starts the SAME run_inference in a
                # background thread and returns a job_id the client polls (/api/run_poll,
                # /api/run_result) for live frame progress. Sync /api/run stays untouched.
                err, code = _validate_inference_payload(data)
                if err:
                    return self.send_json(err, code)
                params=dict(
                    model_name=data.get("model_name",""),category=data.get("category",""),
                    model_file=data.get("model_file",""),lang=data.get("lang","cpp"),
                    variant=data.get("variant","sync"),input_type=data.get("input_type","image"),
                    image_path=data.get("image_path"),video_path=data.get("video_path"),
                    device_id=data.get("device_id"),
                    conf_threshold=data.get("conf_threshold"),nms_threshold=data.get("nms_threshold"),
                    config_overrides=data.get("config_overrides"),
                    upload_path=data.get("upload_path"),loop=data.get("loop"),
                    camera_id=data.get("camera_id"),rtsp_url=data.get("rtsp_url"),
                    save_output=_json_bool(data.get("save_output", True), default=True),
                    image_base64=data.get("image_base64"))
                from dx_app.core.run_progress import start_run
                return self.send_json({"job_id":start_run(run_inference,params),"status":"started"})

            if path=="/api/run_stop":
                from dx_app.core.run_progress import stop_run
                return self.send_json(stop_run(data.get("id") or data.get("job_id") or ""))

            if path=="/api/run_multi":
                debug_log.log_action("dx_app", "run_multi", {"count": len(data.get("requests", []))})
                reqs=data.get("requests",[])
                if not reqs:return self.send_json({"error":"requests required"},400)
                for idx, req in enumerate(reqs):
                    err, code = _validate_inference_payload(req)
                    if err:
                        err["slot"] = idx
                        return self.send_json(err, code)
                return self.send_json(run_multi(reqs))

            if path=="/api/stop":return self.send_json(stop_inference())

            if path=="/api/run_live":
                err, code = _validate_inference_payload(data, live=True)
                if err:
                    return self.send_json(err, code)
                r=run_inference_live(
                    model_name=data.get("model_name",""),category=data.get("category",""),
                    model_file=data.get("model_file",""),lang=data.get("lang","cpp"),
                    variant=data.get("variant","sync"),input_type=data.get("input_type","camera"),
                    camera_id=data.get("camera_id"),rtsp_url=data.get("rtsp_url"),
                    video_path=data.get("video_path"),
                    device_id=data.get("device_id"),slot_idx=int(data.get("slot_idx",0)),
                    n_total_slots=int(data.get("n_total_slots",1)))
                return self.send_json(r)

            if path=="/api/live_stop":return self.send_json(stop_inference_live(data.get("slot_idx")))

            if path=="/api/extract":
                mp=data.get("model_path","");lang=data.get("lang","both")
                if not mp:return self.send_json({"error":"model_path required"},400)
                res=extract_model_package(mp,lang)
                code=res.pop("status",200) if isinstance(res,dict) and "status" in res else 200
                if "error" in res and code==200:code=400
                return self.send_json(res,code)

            if path=="/api/outputs/delete":
                name=data.get("name","")
                if not name:return self.send_json({"error":"name required"},400)
                return self.send_json(delete_output(name))

            if path=="/api/save_capture":
                img=data.get("image_b64","");fn=data.get("filename")
                if not img:return self.send_json({"error":"image_b64 required"},400)
                return self.send_json(save_capture(img,fn))

            if path=="/api/bug_report":
                return self.send_json(bug_report(data.get("model_name"),data.get("error_log"),data.get("model_config")))

            if path=="/api/dev/auth":
                origin = self.headers.get("Origin")
                referer = self.headers.get("Referer")
                res=lab_session(origin=origin, server_host=_server_host_for_origin(self), referer=referer)
                code=res.pop("status",200) if isinstance(res,dict) and "status" in res else 200
                return self.send_json(res,code)
            if path=="/api/dev/add_model":
                res=dev_add(tok,data.get("model_name",""),data.get("task_type",""),
                 data.get("lang","both"),data.get("category","object_detection"),
                 data.get("postprocessor",""),data.get("sync_only",False),
                 data.get("confirm_overwrite",False),base_model=data.get("base_model",""))
                code=res.pop("status",200) if isinstance(res,dict) and "status" in res else 200
                return self.send_json(res,code)
            if path=="/api/dev/delete_model":
                res=dev_delete(tok,data.get("model_name",""),data.get("lang","both"),
                 data.get("confirm",""))
                code=res.pop("status",200) if isinstance(res,dict) and "status" in res else 200
                return self.send_json(res,code)
            if path=="/api/dev/git_commit":
                res=dev_git(tok,data.get("message","chore: update"),data.get("push",False),
                 data.get("confirm_push",""))
                code=res.pop("status",200) if isinstance(res,dict) and "status" in res else 200
                return self.send_json(res,code)
            if path=="/api/dev/extract":
                res=dev_extract(tok,data.get("model_path",""),data.get("lang","both"))
                code=res.pop("status",200) if isinstance(res,dict) and "status" in res else 200
                return self.send_json(res,code)
            if path=="/api/dev/new_task":
                res=dev_new_task(tok,data.get("task_name",""),data.get("lang","both"),
                 data.get("confirm_overwrite",False))
                code=res.pop("status",200) if isinstance(res,dict) and "status" in res else 200
                return self.send_json(res,code)

            if path=="/api/lab/add_model/dry_run":
                res, code = plan_add_model_response(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/add_model/apply":
                res, code = apply_add_model(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/add_model/smoke":
                res, code = smoke_add_model(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/task/dry_run":
                res, code = plan_task_scaffold_response(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/task/apply":
                res, code = apply_task_scaffold(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/experiment/start":
                res, code = start_experiment_run(data)
                if code == 200:
                    launch_experiment_run(res["id"])
                return self.send_json(res, code)

            if path.startswith("/api/lab/experiment/") and path.endswith("/cancel"):
                run_id = path[len("/api/lab/experiment/"):-len("/cancel")]
                from dx_app.core.lab_portal import _validate_run_id
                id_err = _validate_run_id(run_id)
                if id_err:
                    return self.send_json(id_err[0], id_err[1])
                res, code = cancel_experiment_run(run_id)
                return self.send_json(res, code)

            if path == "/api/lab/rollback":
                manifest_id = data.get("manifest_id", "")
                id_err = validate_lab_manifest_id(manifest_id)
                if id_err:
                    return self.send_json({"error": id_err}, 400)
                res, code = rollback_manifest(manifest_id, data)
                return self.send_json(res, code)

            if path == "/api/lab/git/plan":
                manifest_id = data.get("manifest_id", "")
                id_err = validate_lab_manifest_id(manifest_id)
                if id_err:
                    return self.send_json({"error": id_err}, 400)
                res, code = scoped_git_plan(manifest_id, data)
                return self.send_json(res, code)

            if path == "/api/lab/composer/quick_start":
                res, code = plan_composer_quick_start(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/composer/template":
                res, code = plan_composer_template(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/composer/customize":
                res, code = customize_composer_workflow(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/composer/plugin/dry_run":
                res, code = plan_composer_plugin_scaffold_response(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/composer/plugin/apply":
                res, code = apply_composer_plugin_scaffold(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/composer/run":
                debug_log.log_action("dx_app", "composer_run", data)
                res, code = run_composer_workflow(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/composer/run_async":
                debug_log.log_action("dx_app", "composer_run_async", data)
                # Non-blocking composer run — same run_progress registry as the Run page, so it
                # shares /api/run_poll and /api/run_result. The worker unwraps the (result,code)
                # tuple to store just the result dict (what the composer UI renders).
                from dx_app.core.run_progress import start_run
                def _composer_job(job_id=None, tok=None, payload=None):
                    r = run_composer_workflow(tok, payload, job_id=job_id)
                    return r[0] if isinstance(r, tuple) else r
                jid = start_run(_composer_job, {"tok": tok, "payload": data})
                return self.send_json({"job_id": jid, "status": "started"})

            if path == "/api/lab/composer/export":
                res, code = export_composer_package(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/composer/recipe/export":
                res, code = export_composer_recipe(tok, data)
                return self.send_json(res, code)

            if path == "/api/lab/composer/recipe/import":
                res, code = import_composer_recipe(tok, data)
                return self.send_json(res, code)

            if path=="/api/setup/run":
                debug_log.log_action("dx_app", "setup_run", data)
                return self.send_json(setup_run(data.get("step",""),data))

            if path=="/api/setup/input":
                return self.send_json(setup_input(data.get("text","")))

            if path=="/api/setup/stop":
                from dx_app.core.setup_steps import setup_stop
                return self.send_json(setup_stop())

            if path=="/api/modelzoo/download":
                items=data.get("items",[])
                source=data.get("source","public")
                if not items:return self.send_json({"error":"items required"},400)
                return self.send_json(_modelzoo_gw.download(items,source))
            if path=="/api/modelzoo/stop":return self.send_json(_modelzoo_gw.stop())

            # (chat routes handled by handle_chat_routes above)

            return self.route_legacy()

        return self.route_legacy()

def _idle_shutdown_enabled():
    """A standalone dx_app (its own browser tab) shuts down after an hour without requests. Under the launcher
    (DX_PORT_FILE set) the launcher owns the lifecycle; stopping there would break Model Zoo inference until the
    launcher noticed and respawned it."""
    return not os.environ.get("DX_PORT_FILE")


def _watchdog(srv):
    while True:
        time.sleep(5)
        if time.time()-config._HEARTBEAT>_HB_TIMEOUT:
            print("\n[AUTO] No heartbeat — shutting down.")
            stop_inference();shutdown_live_processes()
            from dx_app.core import graph_run
            graph_run.stop_all();srv.shutdown();return

def create_server(port=DEFAULT_PORT):
    """Server factory for tests: returns an HTTPServer instance."""
    from http.server import ThreadingHTTPServer
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    srv.daemon_threads = True
    return srv


def main():
    global _gui_port
    import argparse
    parser = argparse.ArgumentParser(description="DX App")
    parser.add_argument("--port", "-p", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    _gui_port = args.port

    dx = DXServer(Handler, "DX App", DEFAULT_PORT)
    srv = dx.create_http_server(args.port)
    if srv is None:
        sys.exit(1)

    dx.register_signals()
    _hb_touch()
    if _idle_shutdown_enabled():
        threading.Thread(target=_watchdog, args=(srv,), daemon=True).start()
    dx.print_banner(args.port)

    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{args.port}")).start()

    srv.serve_forever()
    print("Server stopped.")

if __name__=="__main__":main()
