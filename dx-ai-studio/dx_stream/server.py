#!/usr/bin/env python3
"""DX Stream web server — port 8093, built on DXBaseHandler."""
from __future__ import annotations

import json
import logging
import os
import re
import threading
import uuid
from pathlib import Path

from shared.dx_server import DXBaseHandler, DXServer, RequestBodyError
from shared.chat import ChatEngine
from shared.chat import module_fallbacks as _module_fallbacks
from shared.runtime_context import RuntimeContextError, resolve_active_runtime_context
from shared.runtime_contract import ContractResult, validate_stream_contract
from shared.runtime_environment import build_child_environment
from shared.runtime_gate import module_start_policy
from shared.runtime_profile import ContractCheck
from shared.runtime_validation import validate_stream_pipeline
from dx_stream.core import config, demos, elements, gst_env, models, setup, status
from dx_stream.core.config import DEFAULT_PORT, STATIC_DIR, TEMPLATES_DIR, SERVER_NAME
from shared.shell import ShellSpec

log = logging.getLogger(__name__)
WEBRTC_INITIAL_ERROR_TIMEOUT = 0.25

# GStreamer-dependent modules are optional: the server still serves pages without them
_pipeline_mgr = None
_webrtc_handler = None
try:
    from dx_stream.core.pipeline import PipelineManager, detect_encoder, pipeline_json_to_gst, get_webrtc_sink_str
    from dx_stream.core.webrtc import WebRTCHandler
    _pipeline_mgr = PipelineManager()
    _webrtc_handler = WebRTCHandler()
except Exception:
    pass

# Shared playback state
_playback_lock = threading.RLock()
_current_output_mode = None
_current_pipeline_id = None
_current_demo_id = None   # demo now playing (the dashboard shows its name)

def _active_stream_context() -> tuple[ContractResult, object | None]:
    """Resolve the validated profile context shared by every Stream launch path."""
    policy = module_start_policy("dx_stream")
    if not policy.allowed:
        assert policy.reason is not None
        return ContractResult((policy.reason,)), None
    try:
        # When degraded launch is allowed (the Stream contract passes now), build the context from the same facts
        # even if the journal is not ACTIVE
        return ContractResult(()), resolve_active_runtime_context(allow_unjournaled=policy.degraded)
    except RuntimeContextError as exc:
        return ContractResult((ContractCheck(
            check_id="profile.context",
            required="resolved active runtime launch context",
            observed=str(exc),
            passed=False,
            remediation="Run the DX-Runtime Dependencies step in Setup, then try again.",
        ),)), None


def _contract_failure_payload(failure: ContractCheck) -> dict:
    """A refused launch as separate fields: what was observed and what to do.

    The front end translates each field on its own (shared/static/server-error-i18n.js
    anchors every pattern to a whole sentence), so they are never joined into one string
    here (SR-843). check_id is already part of the message, so it is not repeated.
    """
    payload = {
        "error": "contract_failed",
        "message": "Runtime contract failed: {}".format(failure.check_id),
    }
    if failure.observed:
        payload["detail"] = failure.observed
    if failure.remediation:
        payload["remediation"] = failure.remediation
    return payload


def _stream_launch_contract(
    demo: dict, *, active_context: tuple[ContractResult, object | None] | None = None,
) -> tuple[ContractResult, object | None]:
    """Return launch admission, sharing read-only context facts within one listing."""
    activation, context = active_context if active_context is not None else _active_stream_context()
    if not activation.passed:
        return activation, None
    assert context is not None

    selected = dict(demo)
    if isinstance(demo.get("model"), str):
        selected["model_file"] = demos._model_file(demo["model"])
    if isinstance(demo.get("models"), list):
        selected["model_files"] = [demos._model_file(name) for name in demo["models"]]
    contract = validate_stream_contract(
        context,
        selected,
        models_dir=config.MODELS_DIR,
        videos_dir=config.VIDEOS_DIR,
        configs_dir=config.CONFIGS_DIR,
        pipelines_dir=config.PIPELINES_DIR,
    )
    return ContractResult(activation.checks + contract.checks), context


def _stream_demo_entries() -> list[dict]:
    """Use the launch contract without activating or repairing the runtime from GET."""
    active_context = _active_stream_context()

    def availability(demo: dict) -> dict:
        contract, _ = _stream_launch_contract(demo, active_context=active_context)
        reasons = []
        for check in contract.checks:
            if check.passed:
                continue
            item = _contract_failure_payload(check)
            item["code"] = item.pop("error")
            item["check_id"] = check.check_id
            reasons.append(item)
        return {
            "available": contract.passed,
            # Plain-text summary for callers without the structured items (English).
            "reason": "; ".join(
                " — ".join(item[key] for key in ("message", "detail", "remediation") if item.get(key))
                for item in reasons
            ) if reasons else "Ready to run",
            "reason_items": reasons,
            "demo_id": demo["id"],
        }

    return demos.list_demo_entries(availability_check=availability)


def _deepx_element_types(body: object) -> set[str]:
    """Return DX element types from Pipeline Builder nodes, never rendered properties."""
    if not isinstance(body, dict):
        return set()
    nodes = body.get("nodes")
    if not isinstance(nodes, list):
        return set()

    deepx_types = set()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        element_type = node.get("type")
        if not isinstance(element_type, str):
            continue
        normalized = element_type.strip()
        if len(normalized) > 2 and normalized.lower().startswith("dx"):
            deepx_types.add(normalized)
    return deepx_types


def _check_webrtc_available() -> bool:
    """Whether WebRTC streaming is available (gstreamer1.0-nice installed)."""
    try:
        from dx_stream.core.pipeline import Gst as _G
        if _G is None:
            return False
        return _G.ElementFactory.find("nicesrc") is not None
    except Exception:
        return False


def _stop_all_playback() -> None:
    """Stop both the WebRTC and MJPEG backends."""
    global _current_output_mode, _current_pipeline_id, _current_demo_id
    with _playback_lock:
        if _pipeline_mgr is not None:
            try:
                _pipeline_mgr.stop()
            except Exception:
                log.debug("WebRTC pipeline stop failed during cleanup", exc_info=True)
        try:
            from dx_stream.core import mjpeg
            mjpeg.stop()
        except Exception:
            log.debug("MJPEG pipeline stop failed during cleanup", exc_info=True)
        try:
            from dx_stream.core import fmp4
            fmp4.stop()
        except Exception:
            log.debug("fMP4 pipeline stop failed during cleanup", exc_info=True)
        _current_output_mode = None
        _current_pipeline_id = None
        _current_demo_id = None


def _playback_running() -> bool:
    """Whether anything is playing over WebRTC, MJPEG or fMP4. Checking WebRTC alone would report a demo
    running over MJPEG as Idle."""
    if _pipeline_mgr is not None and _pipeline_mgr.is_running():
        return True
    try:
        if _current_output_mode == "mjpeg":
            from dx_stream.core import mjpeg
            return bool(mjpeg.is_streaming())
        if _current_output_mode == "fmp4":
            from dx_stream.core import fmp4
            return bool(fmp4.is_streaming())
    except Exception:
        return False
    return False


def _demo_launch_failure_payload(attempted_modes: list[str], demo: dict | None = None) -> dict:
    """Return a stable, browser-safe error after demo playback was stopped.

    The RTSP demo reads public network cameras on the internet, so on a closed network it
    fails for that reason alone — say so instead of pointing at Stream dependencies.
    """
    if demo and demo.get("pipeline_type") == "rtsp":
        detail = "The RTSP network camera streams did not respond."
        remediation = ("This demo plays public cameras on the internet. Check that this "
                       "machine can reach them, then retry.")
    else:
        detail = "No output backend became ready."
        remediation = "Verify the selected input and Stream output dependencies, then retry."
    return {
        "error": "pipeline_error",
        "message": "Unable to start demo playback.",
        "detail": detail,
        "attempted_modes": attempted_modes,
        "remediation": remediation,
        "playback_active": False,
    }


def _apply_webrtc_payload_types(encoder: dict, payload_types) -> dict:
    """Apply the RTP payload types the browser offered to the encoder settings."""
    adjusted = dict(encoder)
    if not isinstance(payload_types, dict):
        return adjusted

    encoding_name = str(adjusted.get("encoding_name", "")).upper()
    raw_value = None
    for key in (encoding_name, encoding_name.lower()):
        if key in payload_types:
            raw_value = payload_types[key]
            break
    if raw_value is None:
        return adjusted

    try:
        payload_type = int(raw_value)
    except (TypeError, ValueError):
        log.warning("Ignoring invalid WebRTC payload type for %s: %r", encoding_name, raw_value)
        return adjusted
    if 0 <= payload_type <= 127:
        adjusted["payload_type"] = payload_type
    else:
        log.warning("Ignoring out-of-range WebRTC payload type for %s: %r", encoding_name, raw_value)
    return adjusted


def _webrtc_enabled() -> bool:
    """WebRTC on by default (low-latency, no re-encode); MJPEG is the automatic fallback when
    it fails to start. WebRTC media is peer-to-peer UDP and connects when the browser and board
    share a direct path (localhost / same LAN) — the normal case here, now that the unreachable
    public STUN server is gone. Set DX_STREAM_WEBRTC=0 to force MJPEG (e.g. cross-subnet/NAT
    viewers with no LAN TURN, where P2P UDP can't be established)."""
    return os.environ.get("DX_STREAM_WEBRTC", "1").strip().lower() not in ("0", "false", "no", "off")


def _try_start_webrtc_pipeline(pipeline_str: str, extra_env: dict | None = None) -> str | None:
    """Try to start a WebRTC pipeline. Return its pipeline_id, or None on failure."""
    global _current_output_mode, _current_pipeline_id
    with _playback_lock:
        if not _webrtc_enabled():
            return None
        if _pipeline_mgr is None or _webrtc_handler is None or not _check_webrtc_available():
            return None
        try:
            pid = _pipeline_mgr.start(pipeline_str, extra_env=extra_env)
        except Exception as e:
            log.warning("WebRTC pipeline start failed; falling back to MJPEG: %s", e)
            try:
                _pipeline_mgr.stop()
            except Exception:
                log.debug("WebRTC pipeline cleanup failed after start error", exc_info=True)
            return None
        if _pipeline_mgr.get_webrtcbin() is None:
            log.warning("WebRTC pipeline start failed; webrtcbin element not found")
            _pipeline_mgr.stop()
            return None
        if hasattr(_pipeline_mgr, 'wait_for_initial_error'):
            err = _pipeline_mgr.wait_for_initial_error(timeout=WEBRTC_INITIAL_ERROR_TIMEOUT)
        else:
            err = _pipeline_mgr.get_last_error()
        if err:
            log.warning("WebRTC pipeline start failed; falling back to MJPEG: %s", err)
            _pipeline_mgr.stop()
            return None
        _current_output_mode = "webrtc"
        _current_pipeline_id = pid
        return pid

_chat_engine = ChatEngine(
    app_name="dx_stream",
    fallback_rules=_module_fallbacks.rules("dx_stream")
)



# ── Shared App Shell ──────────────────────────────────────────
# The eight pages are tabs in the top row (no sidebar).
# Labels are the English text, which is also the i18n dictionary key. Icon ids come from shared/static/dx-icons.svg.
DX_STREAM_PAGES = (
    ("setup", "Setup", "setup"),
    ("dashboard", "Dashboard", "dashboard"),
    ("demo", "Demo Launcher", "run"),
    ("pipeline", "Pipeline Builder", "stream"),
    ("models", "Model Catalog", "models"),
    ("elements", "Element Reference", "puzzle"),
    ("custom", "Custom Library", "wrench"),
    ("reference", "Reference", "book"),
)

# The pipeline status badge is specific to dx_stream, so it goes inside the shared header's .toolbar slot.
# Outside it, it would not line up with the buttons DXToolbar creates.
# The per-language sibling spans are the legacy i18n path (data-i18n is the newer one).
_PIPELINE_BADGE = (
    '<span class="stream-badge" id="pipeline-status">'
    '<span class="ko">대기</span><span class="en">Idle</span>'
    '<span class="es">Inactivo</span><span class="ja">待機</span>'
    '<span class="zh-CN">待机</span><span class="zh-TW">待機</span>'
    "</span>"
)

DX_STREAM_SHELL = ShellSpec(
    module_key="stream",
    pages=DX_STREAM_PAGES,
    active_page="dashboard",
    toolbar_extra=_PIPELINE_BADGE,
)

class DXStreamHandler(DXBaseHandler):
    """DX Stream HTTP request handler."""

    server_name = SERVER_NAME
    static_dir = STATIC_DIR
    templates_dir = TEMPLATES_DIR
    shell_spec = DX_STREAM_SHELL
    log_silent = True

    def _error(self, code: int, error: str, message: str, detail: str = ""):
        """JSON error response (keeps the original format)."""
        payload = {"error": error, "message": message}
        if detail:
            payload["detail"] = detail
        self.send_json(payload, code)

    def _sse(self, generator):
        """Server-Sent Events stream response."""
        self.start_sse()
        try:
            for line in generator:
                if not self.send_sse_data(line):
                    break
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self.end_sse()

    def _safe_read_json(self):
        """Parse the JSON body. On failure, send an error response and return None."""
        try:
            return self.read_json_body()
        except RequestBodyError:
            raise
        except (json.JSONDecodeError, Exception):
            self._error(400, "bad_request", "Invalid JSON body")
            return None

    def _drain_request_body(self) -> None:
        """Drain the body of a POST that ignores it, so leftover bytes do not break keep-alive."""
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (AttributeError, TypeError, ValueError):
            length = 0
        if length <= 0:
            return
        rfile = getattr(self, "rfile", None)
        if rfile is not None:
            rfile.read(length)

    def route(self):
        if self.handle_chat_routes(_chat_engine):
            return

        if self.route_common():
            return

        path = self.url_path

        if self.command == "GET":
            if path == "/api/status":
                return self.send_json(status.check_system(pipeline_mgr=_pipeline_mgr))
            if path == "/api/demos":
                return self.send_json(_stream_demo_entries())
            if path == "/api/models":
                catalog_source = models.get_catalog_source()
                model_list = models.get_models()
                model_status = models.get_model_status()
                for m in model_list:
                    st = model_status.get(m["file"], {})
                    m["installed"] = st.get("installed", False)
                    m["file_size"] = st.get("size", 0)
                return self.send_json({"catalog_source": catalog_source, "models": model_list})
            if path == "/api/elements":
                return self.send_json(elements.get_elements())
            if path == "/api/pipeline/assets":
                # Models, videos, libraries and configs for the property dropdowns
                from dx_stream.core.config import MODELS_DIR, VIDEOS_DIR, CONFIGS_DIR
                import glob as _glob
                _models = sorted([f.name for f in MODELS_DIR.iterdir()
                                  if f.is_file() or f.is_symlink()]) if MODELS_DIR.is_dir() else []
                _videos = sorted([f.name for f in VIDEOS_DIR.iterdir()
                                  if f.is_file() or f.is_symlink()]) if VIDEOS_DIR.is_dir() else []
                _libs = sorted([f.name for f in Path("/usr/local/share/gstdxstream/lib").iterdir()
                                if f.suffix == ".so"]) if Path("/usr/local/share/gstdxstream/lib").is_dir() else []
                _configs = sorted([d.name for d in CONFIGS_DIR.iterdir()
                                   if d.is_dir()]) if CONFIGS_DIR.is_dir() else []
                from dx_stream.core.so_exports import exported_functions
                _lib_dir = Path("/usr/local/share/gstdxstream/lib")
                return self.send_json({
                    "models": _models,
                    "videos": _videos,
                    "libraries": _libs,
                    # function-name candidates per library
                    "functions": {lib: exported_functions(_lib_dir / lib) for lib in _libs},
                    "configs": _configs,
                    "models_dir": str(MODELS_DIR),
                    "videos_dir": str(VIDEOS_DIR),
                    "libs_dir": "/usr/local/share/gstdxstream/lib",
                    "configs_dir": str(CONFIGS_DIR),
                })
            if path == "/api/pipeline/elements":
                cats = elements.get_elements_by_category()
                rules = elements.get_connection_rules()
                return self.send_json({"categories": cats, **rules})
            if path == "/api/pipeline/status":
                running = _playback_running()
                webrtc = _pipeline_mgr is not None and _pipeline_mgr.is_running()
                return self.send_json({
                    "running": running,
                    "pipeline_id": (_pipeline_mgr.get_pipeline_id() if webrtc else _current_pipeline_id) if running else None,
                    "output_mode": (_current_output_mode or ("webrtc" if webrtc else None)) if running else None,
                    "demo_id": _current_demo_id if running else None,
                })
            if path == "/api/pipeline/list":
                from dx_stream.core.config import PIPELINES_DIR
                PIPELINES_DIR.mkdir(parents=True, exist_ok=True)
                files = sorted(f.stem for f in PIPELINES_DIR.glob("*.json"))
                return self.send_json(files)
            if path.startswith("/api/pipeline/load/"):
                name = path.split("/")[-1]
                if not name or "/" in name or name.startswith("."):
                    return self._error(400, "bad_request", "Invalid pipeline name")
                from dx_stream.core.config import PIPELINES_DIR
                fpath = PIPELINES_DIR / f"{name}.json"
                if not fpath.is_file():
                    return self._error(404, "not_found", f"Pipeline not found: {name}")
                return self.send_json(json.loads(fpath.read_text()))
            if path == "/api/setup/log":
                from urllib.parse import urlparse, parse_qs
                qs = parse_qs(urlparse(self.path).query)
                step_id = qs.get("step", [None])[0]
                return self.send_json(setup.get_log_state(step_id))
            if path == "/api/setup/status":
                return self.send_json(setup.get_setup_status())
            if path == "/api/diagnostics":
                from dx_stream.core.diagnostics import deep_diagnostics
                return self.send_json(deep_diagnostics())
            if path == "/api/webrtc/ice":
                if _webrtc_handler is None:
                    return self.send_json([])
                return self.send_json(_webrtc_handler.get_server_ice_candidates())
            if path == "/api/stream/mjpeg":
                return self._handle_mjpeg_stream()
            if path == "/api/stream/snapshot":
                return self._handle_mjpeg_snapshot()
            if path == "/api/stream/fmp4":
                return self._handle_fmp4_stream()
            if path == "/api/stream/stats":
                # Server-side counter → reliable liveness/FPS for the active backend (client diffs).
                from dx_stream.core import mjpeg, fmp4
                if _current_output_mode == "fmp4":
                    return self.send_json({
                        "mode": "fmp4",
                        "frames": fmp4.get_fragment_count(),
                        "streaming": fmp4.is_streaming(),
                    })
                return self.send_json({
                    "mode": _current_output_mode,
                    "frames": mjpeg.get_frame_count(),
                    "streaming": mjpeg.is_streaming(),
                })

            if path.startswith("/api/models/") and path.endswith("/metadata"):
                return self._handle_model_metadata(path)

            if path == "/api/custom-library":
                from dx_stream.core.custom_library import CustomLibraryManager
                mgr = CustomLibraryManager()
                return self.send_json(mgr.list_libraries())
            if path == "/api/custom-library/available-so":
                from dx_stream.core.custom_library import CustomLibraryManager
                mgr = CustomLibraryManager()
                return self.send_json(mgr.get_available_so())
            if path == "/api/custom-library/build-log":
                from dx_stream.core.custom_library import CustomLibraryManager
                return self.send_json(CustomLibraryManager.get_build_log())

            if path.startswith("/api/"):
                return self._error(404, "not_found", f"Unknown API endpoint: {path}")

        if self.command == "POST":
            if path.startswith("/api/demos/") and path.endswith("/start"):
                return self._handle_demo_start(path)
            if path.startswith("/api/demos/") and path.endswith("/stop"):
                return self._handle_demo_stop(path)

            if path == "/api/webrtc/offer":
                return self._handle_webrtc_offer()
            if path == "/api/webrtc/ice":
                return self._handle_webrtc_ice()

            if path == "/api/pipeline/validate-connection":
                body = self._safe_read_json()
                if body is None:
                    return
                result = elements.validate_connection(
                    body.get("from_elem", ""), body.get("to_elem", ""))
                return self.send_json(result)

            if path == "/api/pipeline/validate":
                return self._handle_pipeline_validate()
            if path == "/api/pipeline/run":
                return self._handle_pipeline_run()
            if path == "/api/pipeline/stop":
                return self._handle_pipeline_stop()
            if path == "/api/pipeline/save":
                body = self._safe_read_json()
                if body is None:
                    return
                name = body.get("name", "").strip()
                if not name or "/" in name or name.startswith("."):
                    return self._error(400, "bad_request", "Invalid pipeline name")
                from dx_stream.core.config import PIPELINES_DIR
                PIPELINES_DIR.mkdir(parents=True, exist_ok=True)
                fpath = PIPELINES_DIR / f"{name}.json"
                fpath.write_text(json.dumps(body, indent=2))
                return self.send_json({"saved": True, "name": name})
            if path.startswith("/api/pipeline/delete/"):
                self._drain_request_body()
                name = path.split("/")[-1]
                if not name or "/" in name or name.startswith("."):
                    return self._error(400, "bad_request", "Invalid pipeline name")
                from dx_stream.core.config import PIPELINES_DIR
                fpath = PIPELINES_DIR / f"{name}.json"
                if fpath.is_file():
                    fpath.unlink()
                return self.send_json({"deleted": True, "name": name})

            if path == "/api/setup/stream-deps":
                return self._handle_setup_step("stream-deps")
            if path == "/api/setup/build":
                return self._handle_setup_step("build")
            if path == "/api/setup/download-models":
                return self._handle_setup_step("download-models")
            if path == "/api/setup/runtime-deps":
                return self._handle_setup_step("runtime-deps")
            if path == "/api/setup/driver":
                return self._handle_setup_step("driver")
            if path == "/api/setup/webrtc-deps":
                return self._handle_setup_step("webrtc-deps")
            if path == "/api/setup/download-model":
                return self._handle_download_model()
            if path == "/api/setup/stop":
                self._drain_request_body()
                return self.send_json(setup.stop_step())

            if path == "/api/models/upload":
                return self._handle_model_upload()

            if path == "/api/custom-library/upload":
                return self._handle_custom_upload()
            if path.startswith("/api/custom-library/") and path.endswith("/build"):
                return self._handle_custom_build(path)

            return self._error(404, "not_found", f"Unknown POST endpoint: {path}")

        self.route_legacy()

    def _handle_model_metadata(self, path: str):
        """Return model metadata."""
        from dx_stream.core.metadata import get_model_metadata
        from dx_stream.core.config import MODELS_DIR
        parts = path.split("/")
        model_file = parts[3] if len(parts) >= 5 else ""
        # Path traversal / empty string guard
        if not model_file or '/' in model_file or model_file.startswith('.'):
            return self._error(400, "bad_request", "Invalid model filename")
        model_path = MODELS_DIR / model_file
        if not model_path.is_file():
            return self._error(404, "not_found", f"Model not found: {model_file}")
        result = get_model_metadata(str(model_path))
        self.send_json(result)

    def _handle_demo_start(self, path: str):
        """Start a demo pipeline — WebRTC first, MJPEG as fallback."""
        global _current_output_mode, _current_pipeline_id, _current_demo_id
        attempted_modes: list[str] = []
        playback_stopped = False
        body = self._safe_read_json()
        if body is None:
            return
        payload_types = body.get("webrtcPayloadTypes") if isinstance(body, dict) else None
        parts = path.split("/")
        try:
            demo_id = int(parts[3])
        except (IndexError, ValueError):
            self._error(400, "bad_request", "Invalid demo ID")
            return

        if demo_id < 0 or demo_id >= len(demos.DEMOS):
            self._error(404, "not_found", f"Demo {demo_id} not found")
            return

        if _pipeline_mgr is None:
            self._error(503, "unavailable", "GStreamer not available")
            return

        contract, runtime_context = _stream_launch_contract(demos.DEMOS[demo_id])
        if not contract.passed:
            failure = contract.first_failure
            assert failure is not None
            self.send_json(_contract_failure_payload(failure), 424)
            return

        try:
            from dx_stream.core import mjpeg, fmp4
            encoder = _apply_webrtc_payload_types(detect_encoder(), payload_types)
            # Honor a user-selected sample video; otherwise build_pipeline_str falls back
            # to the demo's own task-appropriate default (face/pose -> people clips, etc).
            _sel = body.get("video") if isinstance(body, dict) else None
            _vuri = None
            if _sel:
                _vp = demos._video_path(_sel)
                _vuri = f"file://{_vp}" if _vp else (_sel if "://" in _sel else None)
            # Remote viewers (SSH tunnel / NAT) can't use WebRTC (UDP) and MJPEG saturates the
            # link, so they request output="fmp4" — HW H264 over HTTP via MSE. forceMjpeg is the
            # last-resort software path (e.g. a browser without MSE).
            _out = body.get("output") if isinstance(body, dict) else None
            want_fmp4 = (_out == "fmp4")
            force_mjpeg = bool(body.get("forceMjpeg")) if isinstance(body, dict) else False
            # Build (and so admit) the webrtcbin graph only when WebRTC will be tried. Without
            # gstreamer1.0-nice webrtcbin cannot link, and probing that variant rejected every
            # demo before the MJPEG/fMP4 fallback below could run.
            webrtc_ok = (not force_mjpeg and not want_fmp4 and _webrtc_enabled()
                         and _check_webrtc_available())
            pipeline_str = demos.build_pipeline_str(demo_id, encoder, video_uri=_vuri,
                                                    webrtc_ok=webrtc_ok)

            assert runtime_context is not None
            extra_env = build_child_environment(runtime_context)
            pipeline_contract = validate_stream_pipeline(
                pipeline_str,
                # GStreamer parse probe needs PyGObject; the active context python is the
                # isolated dx_app inference venv (no gi). Use a gi-capable interpreter so a
                # playable demo is not rejected by a false admission failure.
                python_executable=gst_env.gi_capable_python(runtime_context.python_executable),
                environment=extra_env,
            )
            if not pipeline_contract.passed:
                failure = pipeline_contract.first_failure
                assert failure is not None
                return self.send_json(_contract_failure_payload(failure), 424)

            with _playback_lock:
                _stop_all_playback()
                playback_stopped = True

                pid = None
                if webrtc_ok:
                    attempted_modes.append("webrtc")
                    pid = _try_start_webrtc_pipeline(pipeline_str, extra_env=extra_env)
                if pid is not None:
                    _current_demo_id = demo_id
                    return self.send_json({
                        "started": True, "pipeline_id": pid,
                        "demo_id": demo_id, "output_mode": "webrtc"
                    })

                if want_fmp4:
                    attempted_modes.append("fmp4")
                    fmp4_pipeline = fmp4.build_fmp4_pipeline(pipeline_str)
                    fmp4.start(fmp4_pipeline, extra_env=extra_env)
                    ready, error = fmp4.wait_until_ready(timeout=20.0)
                    if ready:
                        _current_output_mode = "fmp4"
                        _current_pipeline_id = "fmp4-demo-" + str(demo_id)
                        _current_demo_id = demo_id
                        return self.send_json({
                            "started": True, "pipeline_id": _current_pipeline_id,
                            "demo_id": demo_id, "output_mode": "fmp4"
                        })
                    fmp4.stop()
                    log.warning("fMP4 start failed (%s); falling back to MJPEG for demo %d",
                                error, demo_id)

                log.info("WebRTC unavailable, falling back to MJPEG for demo %d", demo_id)
                attempted_modes.append("mjpeg")
                mjpeg_pipeline = mjpeg.build_mjpeg_pipeline(pipeline_str)
                mjpeg.start(mjpeg_pipeline, extra_env=extra_env)
                ready, error = mjpeg.wait_until_ready(timeout=15.0, require_frame=True)
                if not ready:
                    mjpeg.stop()
                    log.warning("Demo %d output start failed after %s", demo_id, attempted_modes)
                    return self.send_json(
                        _demo_launch_failure_payload(attempted_modes, demos.DEMOS[demo_id]), 500)

                _current_output_mode = "mjpeg"
                _current_pipeline_id = "mjpeg-demo-" + str(demo_id)
                _current_demo_id = demo_id
                self.send_json({
                    "started": True, "pipeline_id": _current_pipeline_id,
                    "demo_id": demo_id, "output_mode": "mjpeg"
                })
        except Exception:
            log.exception("Demo %s start failed", demo_id)
            if playback_stopped:
                return self.send_json(
                    _demo_launch_failure_payload(attempted_modes, demos.DEMOS[demo_id]), 500)
            self._error(500, "pipeline_error", "Unable to prepare the demo pipeline.")

    def _handle_demo_stop(self, path: str):
        """Stop the demo pipeline and clean up both backends."""
        self._drain_request_body()
        parts = path.split("/")
        try:
            demo_id = int(parts[3])
        except (IndexError, ValueError):
            self._error(400, "bad_request", "Invalid demo ID")
            return

        try:
            _stop_all_playback()
            self.send_json({"stopped": True, "demo_id": demo_id})
        except Exception as e:
            self._error(500, "pipeline_error", str(e))

    def _handle_mjpeg_stream(self):
        """MJPEG streaming as a multipart/x-mixed-replace response."""
        from dx_stream.core import mjpeg
        if not mjpeg.is_streaming():
            self._error(503, "unavailable", "No active stream")
            return

        self.send_response(200)
        self.send_header("Content-Type",
                         "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-cache, no-store")
        self.send_header("Connection", "close")
        self.end_headers()

        try:
            for chunk in mjpeg.generate_frames():
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _handle_fmp4_stream(self):
        """Fragmented-MP4 (H264) streaming — a continuous video/mp4 byte stream (init segment +
        media fragments) that the browser plays via MSE. Used for remote/tunnel viewers where
        WebRTC's UDP can't reach and MJPEG's bitrate saturates the link."""
        from dx_stream.core import fmp4
        if not fmp4.is_streaming():
            self._error(503, "unavailable", "No active stream")
            return

        self.send_response(200)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Cache-Control", "no-cache, no-store")
        self.send_header("Connection", "close")
        self.end_headers()

        try:
            for chunk in fmp4.generate():
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _handle_mjpeg_snapshot(self):
        """Return the current frame as one JPEG."""
        from dx_stream.core import mjpeg
        frame = mjpeg.get_latest_frame()
        if frame is None:
            self._error(503, "unavailable", "No frame available")
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(frame)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(frame)

    def _handle_webrtc_offer(self):
        """WebRTC SDP offer → answer."""
        body = self._safe_read_json()
        if body is None:
            return
        sdp = body.get("sdp", "")
        if not sdp:
            self._error(400, "bad_request", "Missing 'sdp' field")
            return
        if _webrtc_handler is None or _pipeline_mgr is None:
            self._error(503, "unavailable", "WebRTC not available")
            return
        try:
            answer_sdp = _webrtc_handler.handle_offer(sdp, _pipeline_mgr)
            self.send_json({"sdp": answer_sdp})
        except Exception as e:
            self._error(500, "webrtc_error", str(e))

    def _handle_webrtc_ice(self):
        """Add a WebRTC ICE candidate."""
        body = self._safe_read_json()
        if body is None:
            return
        mline = body.get("sdpMLineIndex")
        candidate = body.get("candidate", "")
        if mline is None:
            self._error(400, "bad_request", "Missing 'sdpMLineIndex'")
            return
        if _webrtc_handler is None or _pipeline_mgr is None:
            self._error(503, "unavailable", "WebRTC not available")
            return
        try:
            _webrtc_handler.handle_ice(mline, candidate, _pipeline_mgr)
            self.send_json({"ok": True})
        except Exception as e:
            self._error(500, "webrtc_error", str(e))

    def _handle_pipeline_validate(self):
        """Validate a pipeline JSON definition and return its gst-launch string."""
        body = self._safe_read_json()
        if body is None:
            return
        if _pipeline_mgr is None:
            self._error(503, "unavailable", "GStreamer not available")
            return
        try:
            gst_str = pipeline_json_to_gst(body)
            self.send_json({"valid": True, "pipeline": gst_str})
        except Exception as e:
            self._error(400, "validation_error", str(e))

    @staticmethod
    def _missing_pipeline_assets(gst_str):
        """Basenames of model/video files the pipeline references but that don't exist
        on disk — so a run can fail fast with a clear message instead of a raw GStreamer
        preroll error. Mirrors pipeline._resolve_props' MODELS_DIR/VIDEOS_DIR resolution."""
        from dx_stream.core.config import MODELS_DIR, VIDEOS_DIR
        missing = []
        for raw in re.findall(r'model-path=(\S+)', gst_str or ""):
            p = Path(raw)
            if not p.is_absolute():
                cand = MODELS_DIR / raw
                if not cand.exists() and not raw.endswith(".dxnn"):
                    cand = MODELS_DIR / (raw + ".dxnn")
                p = cand
            if not p.exists():
                missing.append(Path(raw).name)
        for raw in re.findall(r'location=(\S+)', gst_str or ""):
            if not re.search(r'\.(mp4|mov|avi|mkv|webm)$', raw, re.I):
                continue  # only sample-video locations, not config/other file props
            p = Path(raw)
            if not p.is_absolute():
                p = VIDEOS_DIR / raw
            if not p.exists():
                missing.append(Path(raw).name)
        seen, out = set(), []
        for m in missing:
            if m not in seen:
                seen.add(m)
                out.append(m)
        return out

    def _handle_pipeline_run(self):
        """Start a pipeline from its JSON definition — WebRTC first, MJPEG as fallback."""
        global _current_output_mode, _current_pipeline_id
        attempted_modes = []
        playback_stopped = False
        body = self._safe_read_json()
        if body is None:
            return
        if _pipeline_mgr is None:
            self._error(503, "unavailable", "GStreamer not available")
            return
        activation, runtime_context = _active_stream_context()
        if not activation.passed:
            failure = activation.first_failure
            assert failure is not None
            return self.send_json(_contract_failure_payload(failure), 424)
        try:
            from dx_stream.core import mjpeg

            gst_str = pipeline_json_to_gst(body)
            if not gst_str or not gst_str.strip():
                return self._error(
                    400,
                    "empty_pipeline",
                    "Pipeline is empty — add elements (or choose a Preset) before running.",
                )

            deepx_types = _deepx_element_types(body)
            if deepx_types and not gst_env.plugin_available():
                return self._error(
                    424,
                    "missing_dxstream_plugin",
                    "This pipeline uses DEEPX elements ("
                    + ", ".join(sorted(deepx_types))
                    + ") but the dxstream GStreamer plugin (libgstdxstream.so) is not "
                    "installed. Run the Build / Runtime-Deps setup step, then retry.",
                )

            # Pre-flight: a preset/pipeline may reference a model .dxnn (or sample video)
            # that isn't downloaded yet. Without this, GStreamer fails deep inside dxinfer
            # ("model-path file does not exist" → "pipeline doesn't want to preroll") and the
            # user only sees a cryptic 500. Fail fast with a clear, actionable message.
            missing_assets = self._missing_pipeline_assets(gst_str)
            if missing_assets:
                return self._error(
                    424,
                    "missing_asset",
                    "Required file(s) not installed: " + ", ".join(missing_assets)
                    + '. Download them from the Setup panel ("Model & Video Download"), then retry.',
                )

            # Classify the sinks
            sink_keywords = [
                "fpsdisplaysink", "webrtcbin", "autovideosink",
                "ximagesink", "waylandsink", "fakesink", "fdsink"
            ]
            has_sink = any(s in gst_str for s in sink_keywords)
            has_webrtcbin = "webrtcbin" in gst_str
            has_display_sink = "fpsdisplaysink" in gst_str

            # Choose the WebRTC sink
            payload_types = body.get("webrtcPayloadTypes") if isinstance(body, dict) else None
            encoder = _apply_webrtc_payload_types(detect_encoder(), payload_types)
            if has_webrtcbin:
                webrtc_pipeline = gst_str
            elif has_display_sink:
                webrtc_pipeline = re.sub(
                    r'fpsdisplaysink\b[^!]*',
                    get_webrtc_sink_str(encoder),
                    gst_str
                )
            elif not has_sink:
                webrtc_pipeline = gst_str + " ! " + get_webrtc_sink_str(encoder)
            else:
                webrtc_pipeline = None

            # Same Local/Remote choice as the demo page: remote viewers (SSH tunnel/NAT) request
            # output="fmp4" (HW H264 over HTTP via MSE); forceMjpeg is the no-MSE fallback.
            _out = body.get("output") if isinstance(body, dict) else None
            want_fmp4 = (_out == "fmp4")
            force_mjpeg = bool(body.get("forceMjpeg")) if isinstance(body, dict) else False

            assert runtime_context is not None
            extra_env = build_child_environment(runtime_context)
            pipeline_contract = validate_stream_pipeline(
                gst_str,
                # GStreamer parse probe needs PyGObject; the active context python is the
                # isolated dx_app inference venv (no gi). Use a gi-capable interpreter so a
                # runnable Pipeline Builder graph is not rejected by a false admission failure.
                python_executable=gst_env.gi_capable_python(runtime_context.python_executable),
                environment=extra_env,
            )
            if not pipeline_contract.passed:
                failure = pipeline_contract.first_failure
                assert failure is not None
                return self.send_json(_contract_failure_payload(failure), 424)

            with _playback_lock:
                _stop_all_playback()
                playback_stopped = True

                if webrtc_pipeline is not None and not want_fmp4 and not force_mjpeg:
                    attempted_modes.append("webrtc")
                    pid = _try_start_webrtc_pipeline(webrtc_pipeline, extra_env=extra_env)
                    if pid is not None:
                        return self.send_json({
                            "started": True, "pipeline_id": pid,
                            "pipeline": webrtc_pipeline, "output_mode": "webrtc"
                        })
                    log.info("WebRTC start failed, falling back to MJPEG for Pipeline Builder run")
                elif webrtc_pipeline is None:
                    log.info("Pipeline has no WebRTC-eligible sink, using MJPEG for Pipeline Builder run")

                if want_fmp4:
                    from dx_stream.core import fmp4
                    attempted_modes.append("fmp4")
                    if not has_sink:
                        fmp4_str = gst_str + " ! " + fmp4.get_sink_str()
                    elif has_webrtcbin or has_display_sink:
                        fmp4_str = fmp4.build_fmp4_pipeline(gst_str)
                    else:
                        fmp4_str = gst_str
                    fmp4.start(fmp4_str, extra_env=extra_env)
                    ready, error = fmp4.wait_until_ready(timeout=20.0)
                    if ready:
                        _current_output_mode = "fmp4"
                        _current_pipeline_id = "fmp4-pipeline"
                        return self.send_json({
                            "started": True, "pipeline_id": _current_pipeline_id,
                            "pipeline": fmp4_str, "output_mode": "fmp4"
                        })
                    fmp4.stop()
                    log.warning("fMP4 start failed (%s); falling back to MJPEG for Pipeline Builder run", error)

                from dx_stream.core.mjpeg import get_sink_str, build_mjpeg_pipeline
                if not has_sink:
                    fallback_str = gst_str + " ! " + get_sink_str()
                elif has_webrtcbin or has_display_sink:
                    fallback_str = build_mjpeg_pipeline(gst_str)
                else:
                    fallback_str = gst_str

                attempted_modes.append("mjpeg")
                mjpeg.start(fallback_str, extra_env=extra_env)
                ready, error = mjpeg.wait_until_ready(timeout=15.0, require_frame=True)
                if not ready:
                    mjpeg.stop()
                    log.warning("Pipeline Builder output start failed after %s: %s", attempted_modes, error)
                    return self.send_json(_demo_launch_failure_payload(attempted_modes), 500)

                _current_output_mode = "mjpeg"
                _current_pipeline_id = "mjpeg-pipeline"
                self.send_json({
                    "started": True, "pipeline_id": _current_pipeline_id,
                    "pipeline": fallback_str, "output_mode": "mjpeg"
                })
        except Exception as e:
            log.exception("Pipeline Builder start failed")
            if playback_stopped:
                return self.send_json(_demo_launch_failure_payload(attempted_modes), 500)
            self._error(500, "pipeline_error", str(e))

    def _handle_pipeline_stop(self):
        """Stop the current pipeline and clean up both backends."""
        self._drain_request_body()
        try:
            with _playback_lock:
                _stop_all_playback()
                self.send_json({"stopped": True})
        except Exception as e:
            self._error(500, "pipeline_error", str(e))

    def _handle_setup_step(self, step_id: str):
        """Run a setup step. A step that needs sudo takes the password from the body."""
        body = self._safe_read_json()
        sudo_password = body.get("password") if body else None
        opts = {k: v for k, v in (body or {}).items() if k != 'password'} if body else None
        try:
            setup.run_step(step_id, sudo_password=sudo_password, opts=opts)
            self.send_json({"started": True})
        except KeyError:
            self._error(404, "not_found", f"Unknown setup step: {step_id}")
        except PermissionError as e:
            # Bad/expired sudo password — client re-prompts on this specific code.
            self._error(401, "sudo_auth", str(e))
        except RuntimeError as e:
            self._error(409, "conflict", str(e))
        except ValueError as e:
            self._error(400, "bad_request", str(e))
        except FileNotFoundError as e:
            self._error(404, "not_found", str(e))
        except Exception as e:
            self._error(500, "setup_error", str(e))

    def _handle_download_model(self):
        """Download one model."""
        body = self._safe_read_json()
        if body is None:
            return
        model_name = body.get("model", "")
        if not model_name:
            return self._error(400, "bad_request", "Missing 'model' field")
        try:
            setup.install_model(model_name)
            self.send_json({"started": True, "model": model_name})
        except RuntimeError as e:
            self._error(409, "conflict", str(e))
        except Exception as e:
            self._error(500, "server_error", str(e))

    def _handle_model_upload(self):
        """Store a user-supplied DXNN file without transforming its binary contents."""
        from dx_stream.core.config import MODELS_DIR

        try:
            _fields, files = self.parse_multipart()
        except RequestBodyError as exc:
            return self._error(exc.status_code, "bad_request", exc.message)

        uploaded = files.get("model") if isinstance(files, dict) else None
        if uploaded is None and isinstance(files, dict) and files:
            uploaded = next(iter(files.values()))
        if not isinstance(uploaded, dict) or "data" not in uploaded:
            return self._error(400, "bad_request", "No model file uploaded")

        raw_name = str(uploaded.get("filename") or "").replace("\\", "/").rsplit("/", 1)[-1]
        safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", raw_name)
        if (
            not safe_name
            or safe_name.startswith(".")
            or ".." in safe_name
            or not safe_name.lower().endswith(".dxnn")
        ):
            return self._error(400, "bad_request", "Model file must have a valid .dxnn name")

        target = MODELS_DIR / safe_name
        temporary = MODELS_DIR / f".upload-{uuid.uuid4().hex}"
        try:
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            with temporary.open("xb") as stream:
                stream.write(uploaded["data"])
            os.link(temporary, target)
        except FileExistsError:
            return self._error(409, "conflict", f"Model already exists: {safe_name}")
        except OSError as exc:
            return self._error(500, "write_failed", f"Failed to save model: {exc}")
        finally:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                log.warning("Failed to remove temporary upload %s", temporary, exc_info=True)
        return self.send_json({"uploaded": True, "name": safe_name})

    def _handle_custom_upload(self):
        """Upload a custom library source (JSON body with base64 content)."""
        from dx_stream.core.custom_library import CustomLibraryManager
        import base64
        body = self._safe_read_json()
        if body is None:
            return
        name = body.get("name", "")
        files_b64 = body.get("files", {})
        if not name or not files_b64:
            return self._error(400, "bad_request", "Missing 'name' or 'files'")
        try:
            files = {k: base64.b64decode(v).decode("utf-8") for k, v in files_b64.items()}
        except (UnicodeDecodeError, ValueError):
            return self._error(
                400,
                "bad_request",
                "Custom library files must be text source (.c/.cpp/.h), not a binary file.",
            )
        mgr = CustomLibraryManager()
        try:
            result = mgr.save_upload(name, files)
        except ValueError as e:
            return self._error(400, "bad_request", str(e))
        self.send_json(result)

    def _handle_custom_build(self, path: str):
        """Build a custom library. Body {password?} is for `sudo meson install`, as in Setup."""
        from dx_stream.core.custom_library import CustomLibraryManager, SudoAuthFailed, SudoRequired
        body = self._safe_read_json()
        if body is None:
            return
        parts = path.split("/")
        name = parts[3] if len(parts) >= 5 else ""
        if not name:
            return self._error(400, "bad_request", "Missing library name")
        mgr = CustomLibraryManager()
        try:
            mgr.build(name, sudo_password=(body or {}).get("password") or None)
            self.send_json({"started": True, "name": name})
        except SudoRequired as e:
            self._error(401, "need_sudo", str(e))
        except SudoAuthFailed as e:
            self._error(401, "sudo_auth", str(e))
        except FileNotFoundError as e:
            self._error(404, "not_found", str(e))
        except ValueError as e:
            self._error(400, "bad_request", str(e))
        except Exception as e:
            self._error(500, "server_error", str(e))


def _prepare_runtime_env():
    """Two startup fixups so GStreamer demos work regardless of how the server was launched:

    1) CWD → DX_STREAM_ROOT. The multi/secondary demos (8, 10) run config JSONs whose
       `model_path` is RELATIVE ("./dx_stream/samples/models/...") and dxinfer resolves it
       against the process CWD. The mjpeg/fmp4 subprocess paths already pass cwd=DX_STREAM_ROOT,
       but the in-process WebRTC path (Gst.parse_launch) inherits the server's CWD — so if the
       server was started elsewhere those demos fail with "model-path ... does not exist"
       (surfaces as an internal data-stream error). Pinning CWD here fixes it for every path.
    2) DISPLAY/XAUTHORITY adoption. dxosd renders the OSD overlay on the GPU and needs access
       to the primary DRM node, which requires an authenticated X session. When the server is
       launched from a bare SSH shell (no DISPLAY) the overlay demos fail to preroll
       (amdgpu ACCEL_WORKING -13). If a local X session is running, adopt its DISPLAY + auth so
       the pipelines can reach the GPU the same way a desktop-launched run does.
    """
    from dx_stream.core.config import DX_STREAM_ROOT
    try:
        if DX_STREAM_ROOT.is_dir():
            os.chdir(str(DX_STREAM_ROOT))
            log.info("CWD pinned to DX_STREAM_ROOT: %s", DX_STREAM_ROOT)
    except OSError as e:
        log.warning("Could not chdir to DX_STREAM_ROOT (%s): %s", DX_STREAM_ROOT, e)

    if not os.environ.get("DISPLAY"):
        disp, xauth = _detect_local_x_session()
        if disp:
            os.environ["DISPLAY"] = disp
            if xauth:
                os.environ["XAUTHORITY"] = xauth
            # Headless/SSH-launched: the adopted DISPLAY gives dxosd GPU access via DRI3 (clears
            # the amdgpu ACCEL_WORKING -13), but with a DISPLAY present decodebin auto-plugs the
            # HW VAAPI decoder, whose GPU-surface buffers dxosd CANNOT map ("Failed to map video
            # frame for OSD rendering"). Demote the VAAPI *decoders* so decodebin uses software
            # decode → CPU-mappable buffers → dxosd maps and renders. VAAPI *encoders* stay ranked
            # (HW H264 for fMP4 is unaffected). This makes every overlay demo work over SSH, not
            # just from the local desktop session. Verified: demos 0/8/10 preroll→PLAYING.
            _demote = "vaapih264dec:0,vaapidecodebin:0,vah264dec:0,vaapih265dec:0,vah265dec:0"
            _existing = os.environ.get("GST_PLUGIN_FEATURE_RANK", "")
            os.environ["GST_PLUGIN_FEATURE_RANK"] = (
                _existing + "," + _demote if _existing else _demote)
            log.info("Adopted local X session for GPU access: DISPLAY=%s XAUTHORITY=%s "
                     "(+ VAAPI decoders demoted so dxosd can map frames headless)",
                     disp, xauth or "(none)")
        else:
            log.info("No local X session found; overlay (dxosd) demos need a desktop session "
                     "or a launcher-provided DISPLAY to reach the GPU.")


def _detect_local_x_session():
    """Best-effort discovery of a running local X server's DISPLAY + XAUTHORITY.
    Returns (display, xauthority) or (None, None). Reads the Xorg process's own -auth/-display
    args first (most reliable), then falls back to common socket + auth locations."""
    import glob
    try:
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            try:
                with open(f"/proc/{pid}/cmdline", "rb") as f:
                    parts = f.read().split(b"\0")
            except OSError:
                continue
            if not parts or not parts[0].endswith(b"Xorg"):
                continue
            args = [p.decode("utf-8", "replace") for p in parts if p]
            disp = next((a for a in args if re.fullmatch(r":\d+", a)), None)
            xauth = None
            if "-auth" in args:
                i = args.index("-auth")
                if i + 1 < len(args):
                    xauth = args[i + 1]
            if disp:
                return disp, (xauth if xauth and os.path.exists(xauth) else None)
    except OSError:
        pass
    # Fallback: a socket in /tmp/.X11-unix + a discoverable auth file.
    socks = sorted(glob.glob("/tmp/.X11-unix/X*"))
    if socks:
        disp = ":" + socks[0].rsplit("X", 1)[-1]
        uid = os.getuid()
        for cand in (f"/run/user/{uid}/gdm/Xauthority",
                     os.path.expanduser("~/.Xauthority")):
            if os.path.exists(cand):
                return disp, cand
        return disp, None
    return None, None


def create_server(port=DEFAULT_PORT):
    """Server factory for tests: return an HTTPServer instance."""
    from http.server import ThreadingHTTPServer
    srv = ThreadingHTTPServer(("127.0.0.1", port), DXStreamHandler)
    srv.daemon_threads = True
    return srv


if __name__ == "__main__":
    _prepare_runtime_env()
    DXServer(DXStreamHandler, SERVER_NAME, DEFAULT_PORT).start()
