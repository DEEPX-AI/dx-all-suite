"""Optional activity logging for DX AI Studio, enabled by launcher.sh --debug.

OFF unless env DX_STUDIO_DEBUG=1. Writes one compact JSON object per line to a machine-local,
rotating log so a developer can reproduce a user-reported issue from a server-side action
trace. Never raises into a request path; never logs bodies, tokens, or passwords.
"""
from __future__ import annotations
import json, logging, os, re, threading, time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from shared.paths import STUDIO_ROOT

_ENABLED = os.environ.get("DX_STUDIO_DEBUG") == "1"
_logger = None
_logger_lock = threading.Lock()


def enabled() -> bool:
    return _ENABLED


def _log_path() -> Path:
    override = os.environ.get("DX_STUDIO_DEBUG_LOG")
    return Path(override) if override else STUDIO_ROOT / "var" / "log" / "studio-debug.log"


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    with _logger_lock:
        if _logger is not None:
            return _logger
        path = _log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        lg = logging.getLogger("dx_studio_debug")
        lg.setLevel(logging.INFO)
        lg.propagate = False
        # Clear old handlers to allow reinitializing with a new path
        for h in lg.handlers[:]:
            lg.removeHandler(h)
            h.close()
        # NOTE: launcher + each module process each own a handler on this one file.
        # Per-process append+lock keeps records intact; at the 10MB rollover the
        # processes can race (a lost line / clobbered backup). Accepted: debug-only,
        # rollover-boundary-only, errors swallowed — single-file keeps the timeline chronological.
        h = RotatingFileHandler(str(path), maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
        h.setFormatter(logging.Formatter("%(message)s"))
        lg.addHandler(h)
        _logger = lg
        return lg


_NOISE_EXACT = {
    "/api/hw_stream", "/api/hw_status", "/api/live_poll", "/api/live_result", "/api/live_frame",
    "/api/run_poll", "/api/run_result", "/api/health", "/favicon.ico",
}
_NOISE_PREFIX = ("/static/", "/file/", "/api/asset-thumb", "/api/demo-thumb")


def _is_noise(path: str) -> bool:
    p = (path or "").split("?", 1)[0]
    return p in _NOISE_EXACT or any(p.startswith(pre) for pre in _NOISE_PREFIX)


_SECRET_HINTS = ("password", "token", "secret", "authorization", "image_base64", "config_overrides")


def _is_secret_key(k) -> bool:
    kl = str(k).lower()
    return any(h in kl for h in _SECRET_HINTS)


_ACTION_WHITELIST = ("model_name", "category", "variant", "input_type", "step", "manifest_id", "name", "lang", "count")


def _whitelist(params) -> dict:
    out = {}
    if isinstance(params, dict):
        for k in _ACTION_WHITELIST:
            if k in params and not _is_secret_key(k):
                v = params[k]
                if v is None or isinstance(v, (str, int, float, bool)):
                    out[k] = v
    return out


_USERINFO_RE = re.compile(r"://[^/@\s]*@")


def _redact_cmd(cmd) -> str:
    try:
        parts = cmd if isinstance(cmd, (list, tuple)) else [str(cmd)]
        red, mask_next = [], False
        for a in parts:
            a = str(a)
            if mask_next:
                red.append("***"); mask_next = False; continue
            # scheme://user:pass@host -> scheme://***@host (RTSP/HTTP creds never hit disk)
            a = _USERINFO_RE.sub("://***@", a)
            # inline secret form --token=VALUE / password=VALUE -> mask only the value
            if "=" in a:
                k = a.partition("=")[0]
                if _is_secret_key(k):
                    red.append(f"{k}=***"); continue
            red.append(a)
            if _is_secret_key(a):
                mask_next = True
        return " ".join(red)[:500]
    except Exception:
        return ""


def _emit(ev: dict):
    try:
        ev.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "Z")
        ev.setdefault("boot", os.environ.get("DX_STUDIO_BOOT", ""))
        _get_logger().info(json.dumps(ev, ensure_ascii=False, separators=(",", ":")))
    except Exception:
        pass


def log_http(src, method, path, status, ms, client, extra=None):
    if not _ENABLED:
        return
    try:
        st = int(status)
        if st == 304:
            return
        if _is_noise(path) and st < 400:
            return
        ev = {"type": "http", "src": src, "method": method,
              "path": (path or "").split("?", 1)[0], "status": int(status),
              "ms": round(ms, 1), "client": client}
        if extra:
            ev.update(_whitelist(extra))
        _emit(ev)
    except Exception:
        pass


def log_action(src, action, params=None):
    if not _ENABLED:
        return
    try:
        _emit({"type": "action", "src": src, "action": action, "params": _whitelist(params or {})})
    except Exception:
        pass


def log_exec(src, cmd, exit_code, ms, extra=None):
    if not _ENABLED:
        return
    try:
        ev = {"type": "exec", "src": src, "cmd": _redact_cmd(cmd), "exit": exit_code, "ms": round(ms, 1)}
        if extra:
            ev.update(_whitelist(extra))
        _emit(ev)
    except Exception:
        pass
