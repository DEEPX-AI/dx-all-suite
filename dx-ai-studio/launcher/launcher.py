#!/usr/bin/env python3
"""
DX AI Studio Launcher — Single entry-point for DX App + DX Stream.

Usage:
    python3 -m launcher.launcher                    # default port 8890
    python3 -m launcher.launcher --port 9000        # custom port

Architecture:
    launcher (8890)
      ├── /               → Launcher landing page
      ├── /app/*           → Reverse proxy → DX App    (8080)

      ├── /stream/*        → Reverse proxy → DX Stream (8093)
      └── /api/health      → All sub-server health status
"""
from __future__ import annotations

import http.client
import json
import os
import secrets
import signal
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)

if __name__ == "__main__" and not __package__:
    os.execv(
        sys.executable,
        [sys.executable, "-m", "launcher.launcher", *sys.argv[1:]],
    )

from shared.dx_server import DXBaseHandler
from shared.auth_policy import map_launcher_proxy
from shared.chat import ChatEngine
from shared.runtime_gate import module_start_policy as _runtime_module_start_policy
from shared import debug_log
from shared import remote_access as _ra

# Ports are env-overridable so the studio can coexist with other services on a
# shared host (defaults unchanged → release behavior + tests unaffected). Set e.g.
# DX_APP_PORT=8081 when 8080 is taken by nginx, or DX_LAUNCHER_PORT / --port for 8890.
def _port(env_name: str, default: int) -> int:
    try:
        return int(os.environ.get(env_name, default))
    except (TypeError, ValueError):
        return default

LAUNCHER_PORT = _port("DX_LAUNCHER_PORT", 8890)
APP_PORT      = _port("DX_APP_PORT", 8080)
STREAM_PORT   = _port("DX_STREAM_PORT", 8093)
ZOO_PORT      = _port("DX_ZOO_PORT", 8094)
COMPILER_PORT = _port("DX_COMPILER_PORT", 8095)
PLANNER_PORT  = _port("DX_PLANNER_PORT", 8096)
BENCHMARK_PORT = _port("DX_BENCHMARK_PORT", 8097)
MONITOR_PORT  = _port("DX_MONITOR_PORT", 8098)
AGENT_PORT    = _port("DX_AGENT_PORT", 8099)
_LAUNCHER_PROXY_PORTS = {
    "dx_app": APP_PORT,
    "dx_stream": STREAM_PORT,
    "dx_modelzoo": ZOO_PORT,
    "dx_compiler": COMPILER_PORT,
    "dx_planner": PLANNER_PORT,
    "dx_benchmark": BENCHMARK_PORT,
    "dx_monitor": MONITOR_PORT,
    "dx_agent_dev": AGENT_PORT,
}

# Short JS keys → canonical dx_* keys (dx_monitor is the same in both)
MODULE_KEY_ALIASES = {
    "app": "dx_app",
    "stream": "dx_stream",
    "zoo": "dx_modelzoo",
    "compiler": "dx_compiler",
    "planner": "dx_planner",
    "benchmark": "dx_benchmark",
    "agent": "dx_agent_dev",
}

_MODULE_PROXY_PATHS = {
    "dx_app": "/app/",
    "dx_stream": "/stream/",
    "dx_modelzoo": "/zoo/",
    "dx_compiler": "/compiler/",
    "dx_planner": "/planner/",
    "dx_benchmark": "/benchmark/",
    "dx_monitor": "/dx_monitor/",
    "dx_agent_dev": "/agent/",
}


def module_start_policy(module: str):
    """Return the Studio inference-launch policy without blocking setup pages."""
    return _runtime_module_start_policy(_resolve_module_key(module))


def _debug_routes_enabled() -> bool:
    return os.environ.get("DX_DEBUG_MODE", "").lower() in {"1", "true", "yes", "on"}


# Display name → canonical key mapping for _procs cleanup
_DISPLAY_NAME_TO_CANONICAL = {
    "DX App": "dx_app",
    "DX Stream": "dx_stream",
    "DX Model Zoo": "dx_modelzoo",
    "DX Compiler": "dx_compiler",
    "DX EdgeGuide": "dx_planner",
    "DX Benchmark": "dx_benchmark",
    "DX Monitor": "dx_monitor",
    "DX Agent Dev": "dx_agent_dev",
}

_CANONICAL_TO_DISPLAY_NAME = {v: k for k, v in _DISPLAY_NAME_TO_CANONICAL.items()}


def _resolve_module_key(key):
    """Resolve a short JS key or dx_* key to the canonical dx_* key."""
    return MODULE_KEY_ALIASES.get(key, key)

BASE_DIR  = Path(__file__).resolve().parent
STUDIO_DIR = BASE_DIR.parent           # dx-ai-studio/
SUITE_ROOT = STUDIO_DIR.parent         # <suite> root — holds the DX-AllSuite release.ver
PORTS_DIR = BASE_DIR / ".ports"        # sub-servers report their OS-assigned (:0) port here
APP_DIR    = STUDIO_DIR / "dx_app"

# Fallback shown only if <suite>/release.ver is missing/unreadable (e.g. a partial checkout).
_SDK_VERSION_FALLBACK = "v2.4.0"


def _suite_sdk_version() -> str:
    """The DX-AllSuite (DXNN SDK) version, read live from <suite>/release.ver.

    release.ver is the single source of truth the release tooling writes, so read it at serve
    time and normalize to a leading-'v' tag. Any failure falls back to a known-good constant.
    """
    try:
        raw = (SUITE_ROOT / "release.ver").read_text(encoding="utf-8").strip()
    except OSError:
        return _SDK_VERSION_FALLBACK
    if not raw:
        return _SDK_VERSION_FALLBACK
    return raw if raw.lower().startswith("v") else "v" + raw
STREAM_DIR = STUDIO_DIR / "dx_stream"
ZOO_DIR    = STUDIO_DIR / "dx_modelzoo"
COMPILER_DIR = STUDIO_DIR / "dx_compiler"
PLANNER_DIR  = STUDIO_DIR / "dx_planner"
BENCHMARK_DIR  = STUDIO_DIR / "dx_benchmark"
MONITOR_DIR   = STUDIO_DIR / "dx_monitor"
AGENT_DIR     = STUDIO_DIR / "dx_agent_dev"

_procs = {}

WATCHDOG_MAX_RESTARTS = 3
WATCHDOG_RESTART_WINDOW_SECONDS = 120


def _WATCHDOG_POLL_SECONDS():
    try:
        return float(os.environ.get("DX_WATCHDOG_POLL_SECONDS", "5"))
    except (ValueError, TypeError):
        return 5.0


def _WATCHDOG_RESTART_DEADLINE_SECONDS():
    try:
        return float(os.environ.get("DX_WATCHDOG_RESTART_DEADLINE_SECONDS", "20"))
    except (ValueError, TypeError):
        return 20.0


# Registry: {module_key: {port, cwd, proc, status, restart_count, ...}}
_watchdog_registry = {}
_watchdog_lock = threading.Lock()
_watchdog_thread = None
_watchdog_running = False


def _register_module(name, port, cwd, proc):
    """Register a module for watchdog monitoring."""
    with _watchdog_lock:
        _watchdog_registry[name] = {
            "port": port,
            "cwd": cwd,
            "proc": proc,
            "status": "alive",
            "restart_count": 0,
            "restart_window_start": None,
            "restart_at": None,
            "last_error": None,
        }


def _watchdog_check_once():
    """Single watchdog poll cycle: check each registered module."""
    now = time.monotonic()
    with _watchdog_lock:
        entries = list(_watchdog_registry.items())

    for name, entry in entries:
        proc = entry.get("proc")
        port = entry.get("port")

        # Check if process is alive (outside lock — no mutation)
        proc_alive = proc is not None and proc.poll() is None
        port_open = _is_port_open(port) if port else False

        # I-B fix: all status reads and writes happen inside one locked section
        with _watchdog_lock:
            cur_status = entry.get("status")

            # Skip modules currently being restarted
            if cur_status == "restarting":
                continue

            if proc_alive and port_open:
                entry["status"] = "alive"
                # A module that missed one check and answered again drops its pending restart. Left in place, the
                # next blip would find the deadline already past and kill a healthy module with no grace period.
                # A manual restart is synchronous and has already finished by now.
                entry["restart_at"] = None
                continue

            # Module is down — re-check status was not changed concurrently
            if entry["restart_window_start"] is not None:
                elapsed = now - entry["restart_window_start"]
                if elapsed > WATCHDOG_RESTART_WINDOW_SECONDS:
                    entry["restart_count"] = 0
                    entry["restart_window_start"] = None

            if entry["restart_count"] >= WATCHDOG_MAX_RESTARTS:
                entry["status"] = "unavailable"
                entry["last_error"] = f"Max restarts ({WATCHDOG_MAX_RESTARTS}) exceeded"
                continue

            entry["status"] = "dead"
            # Only schedule restart_at if not already pending
            if entry["restart_at"] is None:
                deadline = _WATCHDOG_RESTART_DEADLINE_SECONDS()
                entry["restart_at"] = now + deadline
            if entry.get("last_error_pid") != (proc.pid if proc else None):
                entry["last_error"] = _exit_description(name, proc)
                entry["last_error_pid"] = proc.pid if proc else None
                print(f"  [Launcher] {name}: {entry['last_error']}", file=sys.stderr)


def _watchdog_do_restarts():
    """Execute pending restarts that have reached their deadline."""
    now = time.monotonic()
    with _watchdog_lock:
        entries = list(_watchdog_registry.items())

    for name, entry in entries:
        # I-A fix: atomically check and claim the restart under lock
        with _watchdog_lock:
            restart_at = entry.get("restart_at")
            if restart_at is None or now < restart_at:
                continue
            if entry["status"] != "dead":
                continue
            # Claim: clear restart_at and set restarting so no other thread fires
            entry["restart_at"] = None
            entry["status"] = "restarting"
            if entry["restart_window_start"] is None:
                entry["restart_window_start"] = now
            entry["restart_count"] += 1

        _do_module_restart(name, entry)


def _do_module_restart(name, entry):
    """Restart a single module using its tracked metadata."""
    port = entry["port"]
    cwd = entry.get("cwd", "")
    cwd_path = Path(cwd) if cwd else None

    # Kill old process if still lingering
    proc = entry.get("proc")
    if proc and proc.poll() is None:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            proc.wait(timeout=3)
        except Exception:
            try:
                os.kill(proc.pid, signal.SIGKILL)
            except Exception:
                pass

    if _is_port_open(port):
        _force_free_port(port)

    server_id = name  # module keys are already server_ids like "dx_app"

    # Clean up stale display-name _procs entry before restart
    display_name = _CANONICAL_TO_DISPLAY_NAME.get(name)
    if display_name and display_name in _procs and display_name != name:
        del _procs[display_name]

    if cwd_path and (cwd_path / "server.py").exists():
        # start_sub_server re-spawns on a fresh ephemeral port and BLOCKS until the server
        # reports it (= bound/listening), updating _LAUNCHER_PROXY_PORTS[server_id].
        ok = start_sub_server(name, cwd_path, server_id=server_id)
        new_port = _LAUNCHER_PROXY_PORTS.get(server_id)
        if ok and new_port:
            new_proc = _procs.get(name)
            with _watchdog_lock:
                entry["proc"] = new_proc
                entry["port"] = new_port   # ephemeral port changes on every restart
                entry["status"] = "alive"  # port report already confirms it's listening
        else:
            with _watchdog_lock:
                entry["status"] = "dead"
                entry["last_error"] = "start_sub_server failed / no port reported"
    else:
        with _watchdog_lock:
            entry["status"] = "dead"
            entry["last_error"] = f"server.py not found in {cwd}"


def _watchdog_loop():
    """Background watchdog loop."""
    global _watchdog_running
    while _watchdog_running:
        try:
            _watchdog_check_once()
            _watchdog_do_restarts()
        except Exception as e:
            print(f"  [Watchdog] Error: {e}", file=sys.stderr)
        time.sleep(_WATCHDOG_POLL_SECONDS())


def _watchdog_start():
    """Start the watchdog background thread."""
    global _watchdog_thread, _watchdog_running
    if _watchdog_thread is not None and _watchdog_thread.is_alive():
        return
    _watchdog_running = True
    _watchdog_thread = threading.Thread(target=_watchdog_loop, daemon=True)
    _watchdog_thread.start()


def _watchdog_stop():
    """Stop the watchdog background thread."""
    global _watchdog_running, _watchdog_thread
    _watchdog_running = False
    if _watchdog_thread is not None:
        _watchdog_thread.join(timeout=5)
        _watchdog_thread = None
    with _watchdog_lock:
        _watchdog_registry.clear()


def get_module_watchdog_status(module_key):
    """Return watchdog status for a specific module."""
    canonical = _resolve_module_key(module_key)
    with _watchdog_lock:
        entry = _watchdog_registry.get(canonical)
        if entry is None:
            return {"status": "unknown", "module": canonical}
        return {
            "status": entry["status"],
            "module": canonical,
            "port": entry["port"],
            "path": _MODULE_PROXY_PATHS.get(canonical, ""),
            "restart_count": entry["restart_count"],
            "last_error": entry.get("last_error"),
        }


def _handle_module_restart(module_key):
    """Handle a restart request for a specific module. Returns result dict."""
    canonical = _resolve_module_key(module_key)
    if canonical not in _LAUNCHER_PROXY_PORTS:
        return {"ok": False, "error": f"Unknown module: {module_key}"}

    with _watchdog_lock:
        entry = _watchdog_registry.get(canonical)

    if entry is None:
        return {"ok": True, "module": canonical, "note": "Module not tracked by watchdog"}

    with _watchdog_lock:
        # If a restart is already in-flight, don't stomp it
        if entry.get("status") == "restarting":
            return {
                "ok": True,
                "module": canonical,
                "status": "restarting",
                "note": "Restart already in progress",
            }
        # Reset restart counter and attempt restart
        entry["restart_count"] = max(0, entry["restart_count"] - 1)
        entry["restart_window_start"] = None  # reset window to avoid re-saturation
        entry["status"] = "dead"
        entry["restart_at"] = time.monotonic()  # restart immediately

    _watchdog_do_restarts()

    with _watchdog_lock:
        return {
            "ok": True,
            "module": canonical,
            "status": entry["status"],
        }

_chat_engine = ChatEngine(app_name="launcher")

# Widget cache for HW float injection
_WIDGET_CACHE = b''
_WIDGET_CACHE_SIG = None
import hashlib  # widget cache signature is content-based (see _widget_sig)

def _widget_cache_path():
    return STUDIO_DIR / "shared" / "hw_widget" / "widget.html"

def _widget_sig(widget_path, data):
    """Content-based cache signature.

    Previously (path, st_mtime_ns, st_size); on filesystems with coarse mtime_ns a
    same-size rewrite (content changed, mtime/size unchanged) was missed and stale
    widget markup kept being injected. widget.html is tiny, so hash its content."""
    return (str(widget_path.resolve()), len(data), hashlib.sha256(data).hexdigest()[:16])

def _load_widget_cache():
    global _WIDGET_CACHE, _WIDGET_CACHE_SIG
    widget_path = _widget_cache_path()
    try:
        data = widget_path.read_bytes()
        _WIDGET_CACHE = data
        _WIDGET_CACHE_SIG = _widget_sig(widget_path, data)
    except OSError as e:
        print(f"[Launcher] WARNING: widget.html not found: {e}", file=sys.stderr)
        _WIDGET_CACHE = b''
        _WIDGET_CACHE_SIG = None


def _get_widget_cache():
    widget_path = _widget_cache_path()
    if _WIDGET_CACHE and _WIDGET_CACHE_SIG is None:
        return _WIDGET_CACHE
    try:
        data = widget_path.read_bytes()
    except OSError:
        if _WIDGET_CACHE or _WIDGET_CACHE_SIG is not None:
            _load_widget_cache()
        return _WIDGET_CACHE
    if _widget_sig(widget_path, data) != _WIDGET_CACHE_SIG:
        _load_widget_cache()
    return _WIDGET_CACHE

# PID file for tracking sub-servers across restarts
_PIDFILE = BASE_DIR / ".launcher_pids"


def _save_pids():
    """Persist sub-server PIDs to disk so they can be cleaned up after a crash."""
    data = {}
    for name, proc in _procs.items():
        if proc and proc.poll() is None:  # still alive
            data[name] = proc.pid
    try:
        _PIDFILE.write_text(json.dumps(data))
    except Exception:
        pass


def _is_our_sub_server(pid):
    """Whether pid looks like a server start_sub_server spawned (`python <STUDIO_DIR>/<module>/server.py ...`).

    False when it cannot be checked (no /proc, no permission, already gone): never kill what we cannot identify.
    """
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return False
    studio = Path(STUDIO_DIR).resolve()
    for arg in raw.split(b"\0")[1:]:
        if not arg.endswith(b"server.py"):
            continue
        try:
            script = Path(os.fsdecode(arg)).resolve()
        except (OSError, ValueError):
            continue
        if script.parent.parent == studio:
            return True
    return False


def _cleanup_old_pids():
    """Kill sub-servers left behind by a previous crashed launcher."""
    if not _PIDFILE.exists():
        return
    try:
        data = json.loads(_PIDFILE.read_text())
    except Exception:
        _PIDFILE.unlink(missing_ok=True)
        return
    if not isinstance(data, dict):  # a corrupt file must not block launcher startup
        _PIDFILE.unlink(missing_ok=True)
        return

    for name, pid in data.items():
        # PIDs get reused (after a reboot, or when the server died first). Only kill a process that
        # still looks like one of our sub-servers. Contract: tests/launcher/test_cleanup_old_pids.py
        if not isinstance(pid, int) or not _is_our_sub_server(pid):
            continue
        try:
            # start_sub_server uses setsid, so our server leads its own group. Otherwise the group
            # belongs to someone else (e.g. the shell that started the launcher): signal the pid only.
            if os.getpgid(pid) == pid:
                os.killpg(pid, signal.SIGTERM)
            else:
                os.kill(pid, signal.SIGTERM)
            time.sleep(0.3)
            # Force kill if still alive — re-check, the pid may have been reused within 0.3 s
            try:
                if _is_our_sub_server(pid):
                    os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        except (ProcessLookupError, PermissionError):
            pass  # already dead

    _PIDFILE.unlink(missing_ok=True)


def _force_free_port(port):
    """Kill whatever is holding a port, using fuser/lsof."""
    if not _is_port_open(port):
        return
    port = int(port)
    subprocess.run(["fuser", "-k", f"{port}/tcp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Also kill via IPv6
    subprocess.run(["fuser", "-k", f"{port}/tcp6"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)


def _port_file(server_id):
    """Path where sub-server <server_id> reports its OS-assigned port."""
    return str(PORTS_DIR / f"{server_id}.port")


def _await_reported_port(port_file, timeout=15):
    """Block until a sub-server writes its (ephemeral) port to port_file. int or None."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            txt = Path(port_file).read_text().strip()
            if txt:
                return int(txt)
        except (OSError, ValueError):
            pass
        time.sleep(0.1)
    return None


def _wait_for_port(port, timeout=15):
    """Block until a TCP port is accepting connections or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(("127.0.0.1", port))
            s.close()
            return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.5)
    return False


def _is_port_open(port):
    """Non-blocking port check."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        result = s.connect_ex(("127.0.0.1", port))
        s.close()
        return result == 0
    except Exception:
        return False


def _can_bind(port):
    """True if we can actually bind the port now.

    Distinct from `_is_port_open`: a port held by a FOREIGN process (one that
    `fuser -k` cannot kill because we don't own it) stays unbindable even after
    _force_free_port. This is what lets us detect "8080 is taken by someone else".
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", int(port)))
        s.close()
        return True
    except OSError:
        return False


def _resolve_port(preferred, used):
    """Return `preferred` if it is free/bindable, else the next free port.

    Skips ports already claimed in `used` (this run) and ports held by foreign
    processes. Used so the studio coexists with unrelated services on a shared host
    instead of silently failing to bind (which made inference proxy to the wrong server).
    """
    preferred = int(preferred)
    if preferred not in used and _can_bind(preferred):
        return preferred
    for p in range(preferred + 1, preferred + 100):
        if p not in used and _can_bind(p):
            return p
    return preferred  # give up — caller will surface the bind failure


_HEALTH_CACHE_TTL_SEC = 2.0
_health_cache_lock = threading.Lock()
_health_cache_ts = 0.0
_health_cache_data = None
_LAUNCHER_BOOT_ID: str | None = None
# True by default so handler-only tests / import paths stay usable; main() clears until boot finishes.
_STUDIO_READY: bool = True
_SHELL_CACHE = "no-cache, must-revalidate"


def _build_health_status():
    """Build the health-status dict (same shape as /api/health response).

    Ports are the discovered ephemeral ports in _LAUNCHER_PROXY_PORTS (filled by the
    port-file handshake at boot), not fixed constants.
    """
    m = _LAUNCHER_PROXY_PORTS

    def st(server_id):
        p = m.get(server_id)
        return {"port": p, "alive": _is_port_open(p) if p else False}

    return {
        "launcher_boot": _LAUNCHER_BOOT_ID,
        "studio_ready": _STUDIO_READY,
        "app":       st("dx_app"),
        "stream":    st("dx_stream"),
        "zoo":       st("dx_modelzoo"),
        "compiler":  st("dx_compiler"),
        "planner":   st("dx_planner"),
        "benchmark": st("dx_benchmark"),
        "monitor":   st("dx_monitor"),
        "agent":     st("dx_agent_dev"),
    }


def _get_health_status():
    """Return cached health status, rebuilding if stale."""
    global _health_cache_ts, _health_cache_data
    now = time.time()
    with _health_cache_lock:
        if _health_cache_data is not None and now - _health_cache_ts < _HEALTH_CACHE_TTL_SEC:
            return _health_cache_data
        _health_cache_data = _build_health_status()
        _health_cache_ts = time.time()
        return _health_cache_data


# Remote access: pairing code and sessions. main() creates it, so a bare import never prints a code
# or writes to ~/.config.
REMOTE_ACCESS = None
_PAIR_PAGE = Path(__file__).resolve().parent / "static" / "pair.html"


def _lan_addresses():
    """IPv4 addresses other computers reach this board on, shown in the connected-browsers view and the console.

    Read per interface with SIOCGIFADDR, which sends no packets (the studio must work offline). Loopback,
    link-local and container/virtual bridges are skipped. Empty when not on Linux or nothing can be read."""
    import fcntl
    import ipaddress
    import struct
    out = []
    try:
        names = [n for _, n in socket.if_nameindex()]
    except (AttributeError, OSError):
        return out
    skip = ("lo", "docker", "br-", "veth", "virbr", "cni", "flannel", "tun", "tap")
    for name in names:
        if name.startswith(skip):
            continue
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            packed = fcntl.ioctl(s.fileno(), 0x8915, struct.pack("256s", name[:15].encode()))  # SIOCGIFADDR
            ip = ipaddress.ip_address(socket.inet_ntoa(packed[20:24]))
        except OSError:
            continue
        finally:
            s.close()
        if ip.is_loopback or ip.is_link_local or ip.is_unspecified:
            continue
        if str(ip) not in out:
            out.append(str(ip))
    return out
# Modules listen on loopback only; requests the launcher relays carry this secret in X-DX-Proxy (passed to
# children via env). It is also set in the launcher's own env so modules running in the same process (the browser
# suite's tests/server_helpers) read the same value and a reload keeps it. Local processes are trusted anyway, so
# this grants nothing new.
PROXY_SECRET = os.environ.setdefault("DX_PROXY_SECRET", secrets.token_hex(32))


def start_sub_server(name, directory, port=0, server_id=None):
    """Start a sub-server on an OS-assigned ephemeral port (:0) and discover it via the
    port-file handshake. The discovered port is stored in _LAUNCHER_PROXY_PORTS[server_id].
    Returns True on success. (`port` is ignored except 0; kept for signature compatibility.)"""
    server_py = directory / "server.py"
    if not server_py.exists():
        print(f"  [Launcher] ERROR: {server_py} not found", file=sys.stderr)
        return False

    PORTS_DIR.mkdir(parents=True, exist_ok=True)
    pf = _port_file(server_id or name)
    try:
        os.unlink(pf)  # drop a stale report so we don't read an old port
    except OSError:
        pass

    # --port 0 → the OS assigns a guaranteed-free port (zero collision with foreign services).
    cmd = [sys.executable, str(server_py), "--port", "0", "--no-browser"]

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # Ensure the spawned module server can import `shared` / `dx_*` without an editable install
    # (repo root on PYTHONPATH). Its own package dir is already on sys.path via the script path.
    env["PYTHONPATH"] = _REPO_ROOT + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["DX_PORT_FILE"] = pf
    # Modules always bind loopback — DX_BIND_HOST/LOCAL given for the launcher must not reach them
    env.pop("DX_BIND_LOCAL", None)
    env["DX_BIND_HOST"] = "127.0.0.1"
    env["DX_PROXY_SECRET"] = PROXY_SECRET
    if server_id:
        env["DX_SERVER_ID"] = server_id
    # modelzoo's inference proxy reads DX_APP_PORT at import — feed it the already-discovered
    # dx_app port (dx_app is started before modelzoo in main()).
    if _LAUNCHER_PROXY_PORTS.get("dx_app") is not None:
        env["DX_APP_PORT"] = str(_LAUNCHER_PROXY_PORTS["dx_app"])
    # dx_app gets a new port when it restarts — pass the file holding it so the Zoo reads it per request
    env["DX_APP_PORT_FILE"] = str(PORTS_DIR / "dx_app.port")

    # stdout is dropped: some modules print a line per request. stderr (tracebacks, warnings, faulthandler dumps
    # of native crashes) goes to a size-capped log per module, so a module that dies leaves a reason behind.
    env["PYTHONFAULTHANDLER"] = "1"
    proc = subprocess.Popen(
        cmd,
        cwd=str(directory),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=os.setsid,
    )
    _start_module_log(server_id or name, proc)
    _procs[name] = proc
    _save_pids()

    actual = _await_reported_port(pf, timeout=20)
    if actual is None:
        print(f"  [Launcher] WARNING: {server_id or name} did not report a port in time", file=sys.stderr)
        # Clear the stale default (e.g. 8080) so the proxy/health never route to a
        # foreign process squatting on that port. port=None → proxy falls
        # through to 404 and health reports alive=false.
        if server_id:
            _LAUNCHER_PROXY_PORTS[server_id] = None
        return False
    if server_id:
        _LAUNCHER_PROXY_PORTS[server_id] = actual
    return True


_MODULE_LOG_CAP_BYTES = 1024 * 1024
_module_log_threads = {}


def _module_log_path(server_id):
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base) / "dx-ai-studio" / "logs" / f"{server_id}.log"


def _pump_module_stderr(pipe, log_path, cap_bytes=_MODULE_LOG_CAP_BYTES):
    """Copy a module's stderr into log_path; past cap_bytes the log becomes <log>.1 and a new one starts."""
    log_path = Path(log_path)
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        out = open(log_path, "ab")
    except OSError:
        for _ in iter(pipe.readline, b""):
            pass
        return
    try:
        for line in iter(pipe.readline, b""):
            out.write(line)
            out.flush()
            if out.tell() > cap_bytes:
                out.close()
                os.replace(log_path, log_path.with_name(log_path.name + ".1"))
                out = open(log_path, "ab")
    except (OSError, ValueError):
        pass
    finally:
        try:
            out.close()
        except OSError:
            pass


def _start_module_log(server_id, proc):
    pipe = getattr(proc, "stderr", None)
    if pipe is None:
        return
    path = _module_log_path(server_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "ab") as f:
            f.write(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} start pid={proc.pid} ===\n".encode())
    except OSError:
        pass
    t = threading.Thread(target=_pump_module_stderr, args=(pipe, path), name=f"log-{server_id}", daemon=True)
    t.start()
    _module_log_threads[server_id] = t


def _exit_description(name, proc):
    if proc is None:
        return "No process"
    code = proc.poll()
    if code is None:
        return f"Port closed (pid={proc.pid})"
    detail = f"Process exited (pid={proc.pid}, code {code}"
    if isinstance(code, int) and code < 0:
        try:
            detail += f" {signal.Signals(-code).name}"
        except ValueError:
            pass
    return detail + f"); log: {_module_log_path(name)}"


def stop_all():
    """Terminate all sub-servers."""
    for name, proc in list(_procs.items()):
        try:
            if proc.poll() is None:  # still running
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                proc.wait(timeout=3)
                print(f"  [Launcher] Stopped {name}")
        except Exception:
            # Force kill if SIGTERM didn't work
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                pass
    _procs.clear()
    # Clean up PID file
    try:
        _PIDFILE.unlink(missing_ok=True)
    except Exception:
        pass


def _shutdown_launcher_server(server, exit_fn=sys.exit):
    print("\n  [Launcher] Shutting down...")
    try:
        stop_all()
    except Exception as exc:
        print(f"  [Launcher] WARNING: shutdown cleanup failed: {exc}", file=sys.stderr)
    finally:
        try:
            server.server_close()
        except Exception as exc:
            print(f"  [Launcher] WARNING: server close failed: {exc}", file=sys.stderr)
    exit_fn(0)


def _should_inject_widget(inject_widget: bool, is_html: bool,
                          fetch_dest: str, has_no_widget_header: bool) -> bool:
    """Decide whether the NPU-monitor float may be injected into a proxied response.

    Inject ONLY into a module's top-level shell page. Suppress for:
      * non-HTML or non-widget targets (dx_monitor),
      * fetch/XHR fragments (Sec-Fetch-Dest empty/cors) spliced in via innerHTML,
      * responses the module explicitly stamps X-DX-No-Widget (nested sub-iframes such
        as the compiler's sandboxed quant-diagnosis report).
    Each of these would otherwise render a duplicate float.
    """
    if not (inject_widget and is_html):
        return False
    if has_no_widget_header:
        return False
    if (fetch_dest or "").lower() in ("empty", "cors"):
        return False
    return True


def _inject_before_body_close(body: bytes, snippet: bytes) -> bytes:
    lower = body.lower()
    idx = lower.rfind(b"</body>")
    if idx == -1:
        return body + snippet
    return body[:idx] + snippet + body[idx:]


def _proxy(handler, target_port, path, inject_widget=True):
    """Forward an HTTP request to a target port and relay the response.
    SSE (text/event-stream) streams are flushed line-by-line so events
    reach the browser immediately instead of being buffered."""
    conn = None
    _t0 = time.monotonic()
    _status = 502
    try:
        conn = http.client.HTTPConnection("127.0.0.1", target_port, timeout=180)

        # Read request body if present
        content_len = int(handler.headers.get("Content-Length", 0))
        body = handler.rfile.read(content_len) if content_len > 0 else None

        # Forward headers (skip hop-by-hop)
        headers = {}
        skip = {"host", "connection", "transfer-encoding", "keep-alive",
                "proxy-authenticate", "proxy-authorization", "te", "trailers",
                "upgrade",
                # drop client-forged values — only the launcher's own values are set below
                "x-dx-proxy", "x-forwarded-for"}
        for key, val in handler.headers.items():
            if key.lower() not in skip:
                headers[key] = val
        forwarded_host = handler.headers.get("X-Forwarded-Host")
        if forwarded_host:
            headers["X-Forwarded-Host"] = forwarded_host
        else:
            headers["X-Forwarded-Host"] = handler.headers.get("Host", "")
        headers["Host"] = f"127.0.0.1:{target_port}"
        headers["X-Forwarded-For"] = handler.client_address[0]
        headers["X-DX-Proxy"] = PROXY_SECRET   # tells the module the launcher already authenticated it (shared/dx_server._is_local)

        conn.request(handler.command, path, body=body, headers=headers)
        resp = conn.getresponse()
        _status = resp.status

        # Detect SSE stream
        content_type = resp.getheader("Content-Type", "")
        is_sse = "text/event-stream" in content_type

        # Detect HTML injection target. The NPU-monitor float must be injected ONLY
        # into a module's top-level shell page — never into HTML *fragments* (partials
        # fetched via XHR and spliced in with innerHTML) nor into *nested* sub-iframes
        # (e.g. the compiler's sandboxed quant-diagnosis report). Injecting there
        # produces a second, duplicate float. Two guards prevent that:
        #   1. Sec-Fetch-Dest: a fetch/XHR partial arrives as "empty" — only inject for
        #      document/iframe *navigations* (the module shell load).
        #   2. X-DX-No-Widget response header: modules stamp it on report/partial
        #      responses that ARE navigations (nested <iframe src=...>) but must not
        #      carry the float. The header is stripped from the relayed response.
        is_html = "text/html" in content_type
        fetch_dest = handler.headers.get("Sec-Fetch-Dest", "")
        has_no_widget = resp.getheader("X-DX-No-Widget") is not None
        may_inject = _should_inject_widget(inject_widget, is_html, fetch_dest, has_no_widget)
        widget_cache = _get_widget_cache() if may_inject else b""
        is_html_inject = bool(widget_cache)

        # http.client de-chunks the module's response. Relaying a body of unknown length (SSE, chunked) as is over an
        # HTTP/1.1 keep-alive connection leaves the browser unable to see where it ends (a Chat answer would hang
        # after [DONE]), so such responses are re-chunked.
        bodyless = handler.command == "HEAD" or resp.status in (204, 304) or 100 <= resp.status < 200
        rechunk = (not is_html_inject and not bodyless and resp.getheader("Content-Length") is None)

        handler.send_response(resp.status)
        for key, val in resp.getheaders():
            low = key.lower()
            # send_response already writes Server and Date — copying them would send them twice
            if low in ("connection", "transfer-encoding", "server", "date"):
                continue
            if is_sse and low in ("cache-control", "x-accel-buffering"):
                continue
            if low == "x-dx-no-widget":
                continue  # internal signal — do not leak to the browser
            if is_html_inject and low == "content-length":
                continue
            handler.send_header(key, val)
        if is_sse:
            handler.send_header("Cache-Control", "no-cache")
            handler.send_header("X-Accel-Buffering", "no")
        if rechunk:
            handler.send_header("Transfer-Encoding", "chunked")

        def _relay(data):
            if rechunk:
                handler.wfile.write(b"%x\r\n%s\r\n" % (len(data), data))
            else:
                handler.wfile.write(data)

        if is_html_inject:
            body = resp.read()
            if widget_cache:
                # the module page was hash-rewritten by its own server; this snippet was not
                snippet = DXBaseHandler.version_sprite_refs(widget_cache.decode("utf-8", "ignore"))
                body = _inject_before_body_close(body, snippet.encode("utf-8"))
            handler.send_header('Content-Length', len(body))
            handler.end_headers()
            handler.wfile.write(body)
        elif is_sse:
            handler.end_headers()
            if hasattr(conn, "sock") and conn.sock:
                conn.sock.settimeout(300)
            while True:
                line = resp.readline()
                if not line:
                    break
                _relay(line)
                if line in (b"\n", b"\r\n") or line.startswith(b"data:"):
                    handler.wfile.flush()
            if rechunk:
                handler.wfile.write(b"0\r\n\r\n")
            handler.wfile.flush()
        else:
            handler.end_headers()
            while True:
                chunk = resp.read1(65536) if rechunk else resp.read(65536)
                if not chunk:
                    break
                _relay(chunk)
                if rechunk:
                    handler.wfile.flush()
            if rechunk:
                handler.wfile.write(b"0\r\n\r\n")
            handler.wfile.flush()

    except Exception as e:
        try:
            handler.send_error(502, f"Proxy error: {e}")
        except Exception:
            pass
    finally:
        if conn:
            conn.close()
        try:
            debug_log.log_http("proxy", handler.command, path, _status,
                               (time.monotonic() - _t0) * 1000.0, handler.client_address[0])
        except Exception:
            pass


def _accepts_html(headers):
    accept = headers.get("Accept", "")
    return "text/html" in accept or "application/xhtml+xml" in accept


def _is_api_or_static_path(path):
    # NOTE: .html is intentionally excluded from the extension tuple.
    # Direct HTML navigations under subapp prefixes should be handled by the
    # launcher shell (for deep-link / F5-reload restoration) unless a subapp
    # referer guard, iframe guard, or resource-type guard applies first.
    return (
        path.startswith("/api/")
        or path == "/api"
        or path.startswith("/static/")
        or path.endswith((".js", ".css", ".json", ".png", ".jpg", ".jpeg",
                          ".webp", ".svg", ".ico", ".woff2", ".ttf"))
    )


def _is_iframe_navigation(headers):
    return headers.get("Sec-Fetch-Dest", "").lower() == "iframe"


class LauncherHandler(DXBaseHandler):
    """Route requests: launcher pages or proxy to sub-servers."""

    server_name = "DX AI Studio"
    log_silent = True

    def _send_contained_file(
        self,
        root: Path,
        rel_path: str,
        content_type: str | None = None,
    ):
        """Serve a file only when the resolved path stays under root."""
        if "\x00" in rel_path:
            self.send_error(400, "Invalid path")
            return
        safe_root = root.resolve()
        target = (safe_root / rel_path).resolve()
        try:
            target.relative_to(safe_root)
        except ValueError:
            self.send_error(403, "Forbidden")
            return
        self.send_file(target, content_type)

    def _send_shell_asset(self, filepath, content_type: str | None = None):
        """Launcher shell JS/CSS — always revalidate (avoid stale UI after ./launcher.sh)."""
        self.send_file(filepath, content_type, cache_control=_SHELL_CACHE)

    _sdk_doc_paths_cache: set | None = None
    _sdk_doc_paths_mtime: float | None = None
    _sdk_doc_paths_lock = threading.Lock()

    _sdk_library_cache: tuple | None = None   # (json mtime, built at, augmented catalog)

    @classmethod
    def _sdk_library(cls):
        """sdk-library-data.json + the suite's md on disk (live sizes, new docs, no duplicates —
        launcher/sdk_library.py). Rebuilt when the JSON changes or every 30 s (a new md file)."""
        from launcher import sdk_library as _lib
        data_path = BASE_DIR / "static" / "sdk-library-data.json"
        try:
            mtime = data_path.stat().st_mtime
        except Exception:
            return None
        with cls._sdk_doc_paths_lock:
            c = cls._sdk_library_cache
            if c is not None and c[0] == mtime and time.time() - c[1] < 30:
                return c[2]
            try:
                data = json.loads(data_path.read_text(encoding="utf-8"))
            except Exception:
                return None
            out = _lib.augment(data, BASE_DIR.parent.parent)
            cls._sdk_library_cache = (mtime, time.time(), out)
            return out

    @classmethod
    def _load_sdk_doc_paths(cls) -> set:
        """Return the set of relative paths the SDK Library lists (registered + picked up from disk)."""
        from launcher import sdk_library as _lib
        data_path = BASE_DIR / "static" / "sdk-library-data.json"
        try:
            mtime = data_path.stat().st_mtime
        except Exception:
            return set()
        data = cls._sdk_library()
        if data is None:
            return set()
        with cls._sdk_doc_paths_lock:
            if cls._sdk_doc_paths_cache is not None and cls._sdk_doc_paths_mtime == (mtime, id(data)):
                return cls._sdk_doc_paths_cache
            allowed = _lib.allowed_paths(data)
            cls._sdk_doc_paths_cache = allowed
            cls._sdk_doc_paths_mtime = (mtime, id(data))
            return allowed

    def _serve_sdk_library(self):
        data = self._sdk_library()
        if data is None:
            self.send_error(404, "Not found")
            return
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_sdk_doc(self, parsed):
        """Serve a markdown file from dx-all-suite by relative path."""
        import urllib.parse as _up
        qs = _up.parse_qs(parsed.query)
        rel = qs.get("path", [""])[0]
        if not rel or "\x00" in rel:
            self.send_error(400, "Invalid path")
            return
        rel_path = Path(rel)
        if rel_path.is_absolute() or any(part == ".." for part in rel_path.parts):
            self.send_error(400, "Invalid path")
            return
        safe_root = BASE_DIR.parent.parent.resolve()
        target = (safe_root / rel_path).resolve()
        try:
            target.relative_to(safe_root)
        except ValueError:
            self.send_error(400, "Invalid path")
            return
        if rel not in self._load_sdk_doc_paths():
            self.send_error(404, "Not found")
            return
        if not target.is_file():
            self.send_error(404, "Not found")
            return
        try:
            import re as _re, posixpath as _pp
            text = target.read_text(encoding="utf-8", errors="ignore")

            # Expand MkDocs `{% include-markdown "rel" ... %}` directives — the SDK
            # Library uses a plain markdown renderer (not MkDocs), so unexpanded
            # directives would render as literal text. Inline the referenced file and
            # rewrite its relative image/link URLs to resolve against the host doc
            # (mirrors the plugin's rewrite-relative-urls).
            _inc_re = _re.compile(
                r'\{%\s*include(?:-markdown)?\s+["\']([^"\']+)["\'][^%]*%\}', _re.S)

            def _fix_url(u, from_dir, to_dir):
                u = u.strip()
                if _re.match(r'^(https?:|data:|/|#|mailto:)', u, _re.I):
                    return u
                absp = _pp.normpath(_pp.join(from_dir, u))
                return _pp.relpath(absp, to_dir) if to_dir else absp

            def _rewrite(txt, from_dir, to_dir):
                txt = _re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',
                              lambda m: '![%s](%s)' % (m.group(1), _fix_url(m.group(2), from_dir, to_dir)), txt)
                txt = _re.sub(r'(<img\b[^>]*?\bsrc\s*=\s*["\'])([^"\']+)(["\'])',
                              lambda m: m.group(1) + _fix_url(m.group(2), from_dir, to_dir) + m.group(3), txt, flags=_re.I)
                txt = _re.sub(r'(?<!\!)\[([^\]]+)\]\(([^)]+)\)',
                              lambda m: '[%s](%s)' % (m.group(1), _fix_url(m.group(2), from_dir, to_dir)), txt)
                return txt

            def _expand(txt, doc_rel, depth=0):
                if depth > 4:
                    return txt
                doc_dir = _pp.dirname(doc_rel)

                def _repl(m):
                    tgt_rel = _pp.normpath(_pp.join(doc_dir, m.group(1).strip()))
                    if tgt_rel.startswith(".."):
                        return ""
                    tgt = (safe_root / tgt_rel).resolve()
                    try:
                        tgt.relative_to(safe_root)
                    except ValueError:
                        return ""
                    if not tgt.is_file():
                        return ""
                    inc_txt = _rewrite(tgt.read_text(encoding="utf-8", errors="ignore"),
                                       _pp.dirname(tgt_rel), doc_dir)
                    return _expand(inc_txt, tgt_rel, depth + 1)

                return _inc_re.sub(_repl, txt)

            from launcher import sdk_library as _lib
            data = _lib.expand_snippets(_expand(text, rel), rel, safe_root).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(500, str(e))

    _SDK_IMAGE_TYPES = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp",
        ".bmp": "image/bmp", ".ico": "image/x-icon",
    }

    def _serve_sdk_doc_image(self, parsed):
        """Serve an image referenced by an SDK Library markdown doc.

        Images are relative to the doc inside dx-all-suite, so the doc renderer
        rewrites `![](rel)` to this endpoint. Read-only, image extensions only,
        confined to the suite root, no traversal.
        """
        import urllib.parse as _up
        qs = _up.parse_qs(parsed.query)
        rel = qs.get("path", [""])[0]
        if not rel or "\x00" in rel or "\\" in rel:
            self.send_error(400, "Invalid path")
            return
        rel_path = Path(rel)
        if rel_path.is_absolute() or any(part == ".." for part in rel_path.parts):
            self.send_error(400, "Invalid path")
            return
        ctype = self._SDK_IMAGE_TYPES.get(rel_path.suffix.lower())
        if ctype is None:
            self.send_error(404, "Not found")
            return
        safe_root = BASE_DIR.parent.parent.resolve()
        target = (safe_root / rel_path).resolve()
        try:
            target.relative_to(safe_root)
        except ValueError:
            self.send_error(400, "Invalid path")
            return
        if not target.is_file():
            self.send_error(404, "Not found")
            return
        try:
            data = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(500, str(e))

    def _serve_sdk_pdf_status(self, parsed):
        """Report whether a registered SDK Library PDF is packaged."""
        import urllib.parse as _up
        qs = _up.parse_qs(parsed.query)
        rel = qs.get("path", [""])[0]
        if not rel or "\x00" in rel or "\\" in rel:
            self.send_error(400, "Invalid path")
            return
        rel_path = Path(rel)
        if rel_path.is_absolute() or any(part == ".." for part in rel_path.parts):
            self.send_error(400, "Invalid path")
            return
        if not rel.startswith("pdfs/") or not rel.lower().endswith(".pdf"):
            self.send_error(404, "Not found")
            return
        if rel not in self._load_sdk_doc_paths():
            self.send_error(404, "Not found")
            return

        pdf_root = (BASE_DIR / "static" / "pdfs").resolve()
        target = (BASE_DIR / "static" / rel).resolve()
        try:
            target.relative_to(pdf_root)
        except ValueError:
            self.send_error(400, "Invalid path")
            return

        if target.is_file():
            self.send_json({
                "path": rel,
                "available": True,
                "url": f"/static/{rel}",
            })
            return
        self.send_json({
            "path": rel,
            "available": False,
            "reason": "missing",
        })

    # (prefix, server_id, inject_widget) — port is resolved at request time from the live
    # _LAUNCHER_PROXY_PORTS map (ephemeral ports discovered via the handshake), not a constant.
    _SUBAPP_REFERER_TARGETS = (
        ("/zoo", "dx_modelzoo", True),
        ("/stream", "dx_stream", True),
        ("/compiler", "dx_compiler", True),
        ("/planner", "dx_planner", True),
        ("/benchmark", "dx_benchmark", True),
        ("/dx_monitor", "dx_monitor", False),
        ("/agent", "dx_agent_dev", False),
        ("/app", "dx_app", True),
    )

    _LAUNCHER_OWNED_STATIC_PREFIXES = (
        "/static/shared/",
        "/static/sdk-library-data",
        "/static/about-data",
        "/static/img/",
        "/static/fonts/",
        "/static/pdfs/",
        "/assets/",
    )

    _CHAT_ENDPOINTS = (
        "/api/chat",
        "/api/chat/config",
        "/api/chat/config/test",
    )

    def _request_hosts(self) -> set:
        """Host aliases this request may legitimately arrive under. Behind a port
        forwarder (VS Code / devtunnels / Codespaces) the browser keeps the public
        host in Referer/Origin while the proxy may rewrite Host to 127.0.0.1:PORT,
        so a Host-only same-origin check wrongly rejects the browser's own Referer
        and breaks Referer-based module routing (module /static/* assets 404). Accept
        the standard X-Forwarded-Host as well."""
        hosts = set()
        host = self.headers.get("Host", "").lower()
        if host:
            hosts.add(host)
        xfh = self.headers.get("X-Forwarded-Host", "")
        if xfh:
            # may be a comma-separated chain; the first entry is the original client host
            hosts.add(xfh.split(",")[0].strip().lower())
        return hosts

    def _request_host(self) -> str:
        return self.headers.get("Host", "").lower()

    def _is_same_origin_url(self, value: str) -> bool:
        parsed = urlparse(value)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return False
        return parsed.netloc.lower() in self._request_hosts()

    @classmethod
    def _chat_endpoint_for_path(cls, path: str) -> str | None:
        """Return the chat endpoint matched by *path*, with optional sub-app prefix."""
        if path in cls._CHAT_ENDPOINTS:
            return path
        for prefix, _, _ in cls._SUBAPP_REFERER_TARGETS:
            if path.startswith(prefix + "/"):
                sub_path = path[len(prefix):]
                if sub_path in cls._CHAT_ENDPOINTS:
                    return sub_path
        return None

    def _is_cross_origin_chat_request(self, path: str) -> bool:
        if self._chat_endpoint_for_path(path) is None:
            return False
        origin = self.headers.get("Origin", "")
        if origin:
            return not self._is_same_origin_url(origin)
        referer = self.headers.get("Referer", "")
        return bool(referer) and not self._is_same_origin_url(referer)

    def _referer_path(self) -> str:
        referer = self.headers.get("Referer", "")
        if not referer or not self._is_same_origin_url(referer):
            return ""
        return urlparse(referer).path

    @staticmethod
    def _path_matches_prefix(path: str, prefix: str) -> bool:
        return path == prefix or path.startswith(prefix + "/")

    def _has_subapp_referer(self) -> bool:
        ref_path = self._referer_path()
        return any(
            self._path_matches_prefix(ref_path, prefix)
            for prefix, _, _ in self._SUBAPP_REFERER_TARGETS
        )

    def _proxy_by_referer(self, path: str, parsed) -> bool:
        ref_path = self._referer_path()
        full_path = path + ("?" + parsed.query if parsed.query else "")
        for prefix, server_id, inject_widget in self._SUBAPP_REFERER_TARGETS:
            if self._path_matches_prefix(ref_path, prefix):
                port = _LAUNCHER_PROXY_PORTS.get(server_id)
                if not port:
                    return False
                _proxy(self, port, full_path, inject_widget=inject_widget)
                return True
        return False

    def _is_launcher_owned_static_path(self, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in self._LAUNCHER_OWNED_STATIC_PREFIXES)

    def _is_launcher_chat_request(self, path: str) -> bool:
        if path != "/api/chat" or self.command != "POST":
            return False
        referer = self.headers.get("Referer", "")
        return bool(referer) and self._is_same_origin_url(referer) and not self._has_subapp_referer()

    def _is_top_level_browser_navigation(self, path: str) -> bool:
        if self.command != "GET":
            return False
        if _is_api_or_static_path(path):
            return False
        if _is_iframe_navigation(self.headers):
            return False
        if self._has_subapp_referer():
            return False
        dest = self.headers.get("Sec-Fetch-Dest", "").lower()
        mode = self.headers.get("Sec-Fetch-Mode", "").lower()
        if dest == "document" and mode in ("navigate", "") and _accepts_html(self.headers):
            return True
        if not dest and _accepts_html(self.headers):
            return True
        return False

    def _serve_index(self):
        """Read launcher index.html, rewrite asset URLs with content hashes, send no-cache."""
        html = (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")
        # Inject the live DX-AllSuite version (from release.ver) into the hub, instead of a
        # stale hard-coded string.
        html = html.replace("{{SDK_VERSION}}", _suite_sdk_version())
        # Inject the shared NPU Monitor float into the launcher shell so the launcher-native
        # views (About DEEPX, SDK Library) show the same collapsible monitor as the proxied
        # module pages. Visibility is gated client-side (setVisibleView adds .hw-native-visible
        # only on those views), so it never doubles up with a module iframe's own widget nor
        # clutters the home splash. Injected before the hash rewrite so its asset and sprite
        # URLs get the content hash too.
        widget = _get_widget_cache()
        if widget:
            snippet = widget.decode("utf-8", "ignore")
            low = html.lower()
            idx = low.rfind("</body>")
            html = (html[:idx] + snippet + html[idx:]) if idx != -1 else (html + snippet)
        html = self.render_html_with_asset_hashes(
            html,
            asset_scope=None,
            extra_static_roots=[BASE_DIR / "static"],
        )
        self.send_html_no_cache(html)

    def _client_id(self) -> str:
        return self.client_address[0]

    def _read_json_body(self) -> dict | None:
        """Parse a size-limited JSON body. On failure, send 400 and return None."""
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            self._send_auth_json({"error": "Invalid Content-Length"}, 400)
            return None
        if length > 65536:
            self._send_auth_json({"error": "Body too large"}, 400)
            return None
        if length <= 0:
            self._send_auth_json({"error": "Empty body"}, 400)
            return None
        try:
            raw = self.rfile.read(length)
            body = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            self._send_auth_json({"error": "Invalid JSON"}, 400)
            return None
        if not isinstance(body, dict):
            self._send_auth_json({"error": "Invalid JSON object"}, 400)
            return None
        return body

    def _send_auth_json(self, payload, status=200):
        """Auth responses never use wildcard CORS, so the CSRF nonce cannot leak."""
        resp = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        for c in getattr(self, "_set_cookies", ()):
            self.send_header("Set-Cookie", c)
        self._set_cookies = ()   # so they don't stick to the next response on a keep-alive connection
        self.send_header("Content-Length", len(resp))
        self.end_headers()
        if self._is_head_request():
            return
        self.wfile.write(resp)

    # ── Remote access — pairing and sessions ───────────────────────────────────
    def _remote(self):
        return REMOTE_ACCESS

    _AUTH_OPEN = {("GET", "/api/auth/status"), ("HEAD", "/api/auth/status"),
                  ("POST", "/api/auth/unlock"), ("GET", "/favicon.ico")}

    def _auth_exempt(self):
        return (self.command, self.url_path) in self._AUTH_OPEN

    def _send_unauthorized(self):
        """The pairing page for a remote browser's page request, 401 JSON otherwise."""
        accept = self.headers.get("Accept", "")
        if self.command in ("GET", "HEAD") and ("text/html" in accept or self.url_path == "/"):
            body = _PAIR_PAGE.read_bytes() if _PAIR_PAGE.is_file() else b"<h1 id=\"dx-pair\">Pairing required</h1>"
            self.send_response(401)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
            return
        self._send_auth_json({"error": "Unauthorized", "pairing": REMOTE_ACCESS is not None}, 401)

    def _cookie(self, value, max_age):
        secure = "; Secure" if self.headers.get("X-Forwarded-Proto", "").lower() == "https" else ""
        return (f"{_ra.SESSION_COOKIE}={value}; Path=/; HttpOnly; SameSite=Strict; "
                f"Max-Age={int(max_age)}{secure}")

    def _handle_auth_status(self):
        local = self._is_local()
        payload = {
            "ok": True,
            "auth_enabled": not local,
            "locked": False,
            "local": local,
            "authenticated": local or getattr(self, "auth_kind", None) in ("token", "session")
            or bool(self._session()),
            "pairing": REMOTE_ACCESS is not None and REMOTE_ACCESS.pairing is not None,
        }
        # Board only: addresses other computers can open (connected-browsers view). Never the code (console only).
        if local and REMOTE_ACCESS is not None:
            port = self.server.server_address[1]
            payload["addresses"] = [f"http://{ip}:{port}" for ip in _lan_addresses()]
        self._send_auth_json(payload)

    def _handle_auth_unlock(self):
        body = self._read_json_body()
        if body is None:
            return
        ra = REMOTE_ACCESS
        if ra is None or ra.pairing is None:
            return self._send_auth_json({"error": "Pairing is not available"}, 403)
        result = ra.pairing.verify(body.get("code"))
        if result == "locked":
            return self._send_auth_json({"error": "Too many attempts — a new code is on the board console."}, 429)
        if result != "ok":
            return self._send_auth_json({"error": "Wrong code"}, 401)
        token, sid = ra.sessions.create(user_agent=self.headers.get("User-Agent", ""), ip=self._peer_ip())
        self._set_cookies = [self._cookie(token, ra.sessions.ttl)]
        print(f"  [Launcher] Remote browser paired ({self._peer_ip()}).", flush=True)
        self._send_auth_json({"ok": True, "id": sid})

    def _send_no_content(self):
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _handle_auth_logout(self):
        ra = REMOTE_ACCESS
        token = ra.cookie_value(self.headers.get("Cookie", "")) if ra is not None else ""
        if not token:
            return self._send_no_content()   # no session: 204 without a cookie
        ra.sessions.revoke_token(token)
        self._set_cookies = [self._cookie("", 0)]
        self._send_auth_json({"ok": True})

    def _handle_auth_relock(self):
        self._handle_auth_logout()

    def _handle_auth_sessions(self):
        ra = REMOTE_ACCESS
        items = [] if ra is None else sorted(ra.sessions.list(), key=lambda v: -float(v.get("last_seen", 0)))
        mine = (self._session() or {}).get("id")
        # Full list on the board only — a remote browser sees its own row, never other computers' IPs
        if not self._is_local():
            items = [v for v in items if v.get("id") == mine]
        self._send_auth_json({"sessions": [
            {"id": v.get("id"), "created": v.get("created"), "last_seen": v.get("last_seen"),
             "user_agent": v.get("user_agent", ""), "ip": v.get("ip", ""), "current": v.get("id") == mine}
            for v in items]})

    def _handle_auth_revoke(self):
        body = self._read_json_body()
        if body is None:
            return
        ra = REMOTE_ACCESS
        if not self._is_local():
            # Only the board disconnects other browsers. A remote browser disconnects itself via /api/auth/logout.
            return self._send_auth_json({"error": "Only the studio computer can disconnect other browsers"}, 403)
        ok = ra is not None and isinstance(body.get("id"), str) and ra.sessions.revoke(body["id"])
        self._send_auth_json({"ok": bool(ok)}, 200 if ok else 404)

    def route(self):
        path = self.url_path
        parsed = self.parsed

        if path == "/api/auth/status" and self.command in ("GET", "HEAD"):
            return self._handle_auth_status()
        if path == "/api/auth/unlock" and self.command == "POST":
            return self._handle_auth_unlock()
        if path == "/api/auth/logout" and self.command == "POST":
            return self._handle_auth_logout()
        if path == "/api/auth/relock" and self.command == "POST":
            return self._handle_auth_relock()
        if path == "/api/auth/sessions" and self.command in ("GET", "HEAD"):
            return self._handle_auth_sessions()
        if path == "/api/auth/sessions/revoke" and self.command == "POST":
            return self._handle_auth_revoke()

        # Always serve launcher health for /api/health
        # (sub-app iframes have their own status endpoints)
        if path == "/api/health":
            return self.send_json(_get_health_status())

        if path.startswith("/api/modules/") and path.endswith("/restart") and self.command == "POST":
            parts = path.split("/")
            # /api/modules/<module_key>/restart → parts = ['', 'api', 'modules', '<key>', 'restart']
            if len(parts) == 5:
                module_key = parts[3]
                result = _handle_module_restart(module_key)
                code = 200 if result.get("ok") else 400
                return self.send_json(result, code)

        if path.startswith("/api/modules/") and path.endswith("/status") and self.command in ("GET", "HEAD"):
            parts = path.split("/")
            if len(parts) == 5:
                module_key = parts[3]
                return self.send_json(get_module_watchdog_status(module_key))

        if self._is_cross_origin_chat_request(path):
            return self.send_error_json(403, "Cross-origin chat requests are not allowed")

        if self._is_top_level_browser_navigation(path):
            self._serve_index()
            return

        proxy_target = map_launcher_proxy(path)
        if proxy_target is not None:
            target_id, sub_path = proxy_target
            port = _LAUNCHER_PROXY_PORTS.get(target_id)
            if port is not None:
                if parsed.query:
                    sub_path += "?" + parsed.query
                # Inject the NPU Monitor float into every proxied module EXCEPT dx_monitor
                # itself (it already shows full hardware telemetry).
                _proxy(self, port, sub_path, inject_widget=(target_id != "dx_monitor"))
                return

        if self._has_subapp_referer():
            ambiguous = (
                path.startswith("/api/")
                or (path.startswith("/static/") and not self._is_launcher_owned_static_path(path))
            )
            if ambiguous and self._proxy_by_referer(path, parsed):
                return

        # Every shared chat route but the chat stream itself (its referer rule is below).
        if path in self._CHAT_ROUTES and path != "/api/chat":
            if self.handle_chat_routes(_chat_engine):
                return
            return self.send_error_json(405, "Method not allowed")

        if self._is_launcher_chat_request(path):
            if self.handle_chat_routes(_chat_engine):
                return

        if path == "/" or path == "/index.html" or path == "/sdk-library" or path == "/about":
            self._serve_index()
        elif path == "/design-system":
            # Live token/component catalog. It loads only the shared foundation,
            # so what shows here is what the product shows.
            self._send_shell_asset(BASE_DIR.parent / "docs/design-system.html", "text/html")
        elif path == "/style.css":
            self._send_shell_asset(BASE_DIR / "static/style.css", "text/css")
        elif path == "/launcher.js":
            self._send_shell_asset(BASE_DIR / "static/launcher.js", "application/javascript")
        elif path == "/launcher-state.js":
            self._send_shell_asset(BASE_DIR / "static/launcher-state.js", "application/javascript")
        elif path == "/launcher-language.js":
            self._send_shell_asset(BASE_DIR / "static/launcher-language.js", "application/javascript")
        elif path == "/launcher-splash.js":
            self._send_shell_asset(BASE_DIR / "static/launcher-splash.js", "application/javascript")
        elif path == "/intro-stream.js":
            self._send_shell_asset(BASE_DIR / "static/intro-stream.js", "application/javascript")
        elif path == "/intro-app.js":
            self._send_shell_asset(BASE_DIR / "static/intro-app.js", "application/javascript")
        elif path == "/intro-compile.js":
            self._send_shell_asset(BASE_DIR / "static/intro-compile.js", "application/javascript")
        elif path == "/platform-info.js":
            self._send_shell_asset(BASE_DIR / "static/platform-info.js", "application/javascript")
        elif path == "/launcher-app-frame.js":
            self._send_shell_asset(BASE_DIR / "static/launcher-app-frame.js", "application/javascript")
        elif path == "/home-router.js":
            self._send_shell_asset(BASE_DIR / "static/home-router.js", "application/javascript")
        elif path == "/home-prompts.js":
            self._send_shell_asset(BASE_DIR / "static/home-prompts.js", "application/javascript")
        elif path == "/home-answer.js":
            self._send_shell_asset(BASE_DIR / "static/home-answer.js", "application/javascript")
        elif path == "/home-console.js":
            self._send_shell_asset(BASE_DIR / "static/home-console.js", "application/javascript")
        elif path == "/home-agent-setup.js":
            self._send_shell_asset(BASE_DIR / "static/home-agent-setup.js", "application/javascript")
        elif path == "/home-widgets.js":
            self._send_shell_asset(BASE_DIR / "static/home-widgets.js", "application/javascript")
        elif path == "/remote-access.js":
            self._send_shell_asset(BASE_DIR / "static/remote-access.js", "application/javascript")
        elif path == "/home-bar.js":
            self._send_shell_asset(BASE_DIR / "static/home-bar.js", "application/javascript")
        elif path == "/home-effects.js":
            self._send_shell_asset(BASE_DIR / "static/home-effects.js", "application/javascript")
        elif path == "/home-sections.js":
            self._send_shell_asset(BASE_DIR / "static/home-sections.js", "application/javascript")
        elif path == "/tutorial.js":
            self._send_shell_asset(BASE_DIR / "static/tutorial.js", "application/javascript")
        elif path == "/about-deepx.css":
            self._send_shell_asset(BASE_DIR / "static/about-deepx.css", "text/css")
        elif path == "/about-deepx.js":
            self._send_shell_asset(BASE_DIR / "static/about-deepx.js", "application/javascript")
        elif path == "/home-stage.css":
            self._send_shell_asset(BASE_DIR / "static/home-stage.css", "text/css")
        elif path == "/sdk-library.css":
            self._send_shell_asset(BASE_DIR / "static/sdk-library.css", "text/css")
        elif path == "/sdk-library.js":
            self._send_shell_asset(BASE_DIR / "static/sdk-library.js", "application/javascript")
        elif path == "/sdk-tutorial.js":
            self._send_shell_asset(BASE_DIR / "static/sdk-tutorial.js", "application/javascript")
        elif path.startswith("/static/sdk-library-data"):
            self._send_contained_file(BASE_DIR / "static", path[len("/static/"):])
        elif path == "/api/sdk-library":
            self._serve_sdk_library()
        elif path == "/api/sdk-doc":
            self._serve_sdk_doc(parsed)
        elif path == "/api/sdk-doc-image":
            self._serve_sdk_doc_image(parsed)
        elif path == "/api/sdk-pdf-status":
            self._serve_sdk_pdf_status(parsed)
        elif path.startswith("/static/about-data"):
            self._send_contained_file(BASE_DIR / "static", path[len("/static/"):])
        elif path.startswith("/static/img/about/"):
            self._send_contained_file(
                BASE_DIR / "static" / "img" / "about",
                path[len("/static/img/about/"):],
            )
        elif path.startswith("/static/img/"):
            self._send_contained_file(
                BASE_DIR / "static" / "img",
                path[len("/static/img/"):],
            )
        elif path.startswith("/assets/"):
            self._send_contained_file(
                BASE_DIR / "static" / "assets",
                path[len("/assets/"):],
            )
        elif path.startswith("/static/fonts/"):
            self._send_contained_file(
                BASE_DIR / "static" / "fonts",
                path[len("/static/fonts/"):],
            )
        elif path.startswith("/static/pdfs/"):
            self._send_contained_file(
                BASE_DIR / "static" / "pdfs",
                path[len("/static/pdfs/"):],
            )
        elif path.startswith("/static/shared/chat-widget"):
            chat_widget_file = path[len("/static/shared/"):]
            if "/" in chat_widget_file or "\\" in chat_widget_file:
                self.send_error(403, "Forbidden")
                return
            self._send_contained_file(
                STUDIO_DIR / "shared" / "chat" / "static",
                chat_widget_file,
            )
        elif path.startswith("/static/shared/"):
            self._send_contained_file(
                STUDIO_DIR / "shared" / "static",
                path[len("/static/shared/"):],
            )
        elif path == "/mockup" and _debug_routes_enabled():
            self.send_file(BASE_DIR / "static/archive-layout.html", "text/html")
        elif path.startswith("/brainstorm/") and _debug_routes_enabled():
            fname = path.split("/")[-1]
            bp = STUDIO_DIR / ".superpowers" / "brainstorm" / fname
            self.send_file(bp, "text/html")
        else:
            if self._proxy_by_referer(path, parsed):
                return

            # No useful Referer — fall back to DX App API patterns
            # (EventSource / fetch may not send Referer in all browsers)
            full_path = path + ("?" + parsed.query if parsed.query else "")
            _DX_MONITOR_APIS = (
                "/api/hw_stream", "/api/hw_status", "/api/system_info",
            )
            _DX_APP_APIS = (
                "/api/recent_runs", "/api/hb", "/api/models", "/api/chat",
                "/api/run", "/api/runner", "/api/history",
                "/api/file", "/file/", "/outputs/",
                "/api/images", "/api/videos",
            )
            if any(path.startswith(p) for p in _DX_MONITOR_APIS):
                _proxy(self, _LAUNCHER_PROXY_PORTS.get("dx_monitor"), full_path, inject_widget=False)
            elif any(path.startswith(p) for p in _DX_APP_APIS):
                _proxy(self, _LAUNCHER_PROXY_PORTS.get("dx_app"), full_path)
            else:
                self.send_error(404)


def _open_browser(url):
    """Open the studio URL in a browser, quietly.

    In remote / VS Code / SSH terminals, Python's webbrowser delegates to a helper
    that can spam stderr when the vscode-ipc socket is stale (and there's no local
    display to open anyway). In those contexts we skip auto-open — the URL is printed
    in the completion banner and is click-/forward-able. Otherwise open normally.
    """
    if (os.environ.get("DX_NO_BROWSER")
            or os.environ.get("VSCODE_IPC_HOOK_CLI")
            or os.environ.get("SSH_CONNECTION")
            or os.environ.get("REMOTE_CONTAINERS")):
        return
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    # Declared global up-front: these are reassigned below by the free-port resolver,
    # and Python requires the global declaration before any use within the function.
    global APP_PORT, STREAM_PORT, ZOO_PORT, COMPILER_PORT, PLANNER_PORT, BENCHMARK_PORT, MONITOR_PORT, AGENT_PORT, _LAUNCHER_BOOT_ID, _STUDIO_READY
    _STUDIO_READY = False
    port = LAUNCHER_PORT
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])

    _load_widget_cache()

    # Pre-sync the shared SDK chat knowledge ONCE, here in the launcher process. This is the
    # single writer: knowledge_sync.generate() writes atomically (temp file + os.replace), but
    # we still want exactly one process regenerating it rather than all 8 module servers racing
    # to lazily resync on first chat. Module servers just read the already-fresh file (see
    # shared/chat/engine.py's env-gated lazy fallback for the standalone-without-launcher case).
    #
    # Run it in a daemon thread so it never blocks boot: walking the multi-GB .deepx source tree
    # adds latency before the first module even starts, and boot correctness does not depend on
    # it finishing first. The write is atomic, so a chat that arrives mid-sync reads either the
    # previous complete file or the new one — never a torn read. Best-effort: a failure is
    # logged and ignored.
    def _presync_chat_knowledge():
        try:
            from shared.chat.knowledge_sync import sync_if_stale
            if sync_if_stale():
                print("  [Launcher] SDK chat knowledge resynced (sources changed).")
        except Exception as _e:
            print(f"  [Launcher] SDK chat knowledge sync skipped ({_e}).")

    threading.Thread(
        target=_presync_chat_knowledge, name="launcher-chat-presync", daemon=True
    ).start()

    boot_modules = {
        "DX App": APP_PORT, "DX Stream": STREAM_PORT,
        "DX Model Zoo": ZOO_PORT,
        "DX Compiler": COMPILER_PORT, "DX EdgeGuide": PLANNER_PORT,
        "DX Benchmark": BENCHMARK_PORT,
        "DX Monitor": MONITOR_PORT,
        "DX Agent Dev": AGENT_PORT,
    }

    from .boot_animation import show_logo, show_boot_progress, show_system_check, show_completion_banner
    # DX_LAUNCHER_FAST=1 (or `launcher.sh --fast`) skips the cosmetic boot animation.
    _fast = os.environ.get("DX_LAUNCHER_FAST", "").lower() in {"1", "true", "yes", "on"}

    # ── Bind + start serving the launcher port BEFORE booting modules. The launcher port is
    #    the ONLY URL the user — and any editor that auto-links terminal URLs (VS Code remote)
    #    — touches. Binding first means a click during boot lands on a LIVE server (modules
    #    simply report "booting" until their ephemeral ports come up) instead of a refused
    #    connection that VS Code-remote caches as a permanently broken port-forward. This is
    #    why the clickable banner below is printed AFTER bind, not by launcher.sh beforehand.
    class _LauncherServer(ThreadingHTTPServer):
        allow_reuse_address = True

    # Bind host: default all-interfaces (so a headless board is reachable from a
    # dev laptop). DX_BIND_LOCAL=1 → 127.0.0.1 only (no LAN exposure; reach it via an
    # SSH tunnel). DX_BIND_HOST=<host> → explicit override. Mirrors shared/dx_server.py
    # so the whole studio (hub + modules) binds consistently.
    _bind_host = "0.0.0.0"
    if os.environ.get("DX_BIND_LOCAL", "").strip().lower() in ("1", "true", "yes"):
        _bind_host = "127.0.0.1"
    elif os.environ.get("DX_BIND_HOST", "").strip():
        _bind_host = os.environ["DX_BIND_HOST"].strip()

    srv = None
    for attempt in range(5):
        if _is_port_open(port):
            print(f"  [Launcher] Port {port} in use — releasing (attempt {attempt + 1})...")
            _force_free_port(port)
            time.sleep(1.5)
        try:
            srv = _LauncherServer((_bind_host, port), LauncherHandler)
            _LAUNCHER_BOOT_ID = f"{port}-{os.getpid()}"
            os.environ["DX_STUDIO_BOOT"] = _LAUNCHER_BOOT_ID
            break
        except OSError as e:
            if attempt < 4:
                print(f"  [Launcher] Bind failed ({e}), retrying...")
            else:
                print(f"  [Launcher] ERROR: Cannot bind port {port}: {e}")
                stop_all()
                sys.exit(1)

    if srv is None:
        stop_all()
        sys.exit(1)

    def _shutdown(*_):
        _shutdown_launcher_server(srv)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    # Socket is now LISTENING (HTTPServer binds+listens in its constructor). Serve in a daemon
    # thread so the cosmetic boot below runs while the port already accepts connections.
    threading.Thread(target=srv.serve_forever, name="launcher-http", daemon=True).start()

    # Remote browser pairing — skipped when bound to loopback only, since nothing remote can connect
    global REMOTE_ACCESS
    if not (_bind_host in ("127.0.0.1", "::1", "localhost")):
        REMOTE_ACCESS = _ra.RemoteAccess()

    # Unmissable, now-LIVE URL banner — safe to surface here because the port is bound.
    _studio_url = f"http://localhost:{port}"
    print("\n  ┌──────────────────────────────────────────────────┐")
    print(f"  │  👉  OPEN THE STUDIO:  {_studio_url:<25} │")
    if REMOTE_ACCESS is not None:
        # Addresses for other computers — the first visit asks for the remote access code
        for _ip in _lan_addresses()[:3]:
            _lan_url = f"http://{_ip}:{port}"
            print(f"  │      other computers:  {_lan_url:<25} │")
    print("  └──────────────────────────────────────────────────┘\n")

    show_logo(animate=not _fast)
    show_system_check(module_count=len(boot_modules), animate=not _fast)

    # Clean up orphan processes from previous crash
    _cleanup_old_pids()

    # Sub-servers bind OS-assigned ephemeral ports (--port 0) — zero collision with foreign
    # services, no port juggling. start_sub_server discovers each port via the port-file
    # handshake and fills _LAUNCHER_PROXY_PORTS[server_id]. (Started in order so dx_app's port
    # is known before modelzoo, whose inference proxy needs DX_APP_PORT.)
    _SUBS = [
        ("DX App",       APP_DIR,       "dx_app"),
        ("DX Stream",    STREAM_DIR,    "dx_stream"),
        ("DX Model Zoo", ZOO_DIR,       "dx_modelzoo"),
        ("DX Compiler",  COMPILER_DIR,  "dx_compiler"),
        ("DX EdgeGuide", PLANNER_DIR,   "dx_planner"),
        ("DX Benchmark", BENCHMARK_DIR, "dx_benchmark"),
        ("DX Monitor",   MONITOR_DIR,   "dx_monitor"),
        ("DX Agent Dev", AGENT_DIR,     "dx_agent_dev"),
    ]
    for _name, _dir, _sid in _SUBS:
        start_sub_server(_name, _dir, server_id=_sid)

    # Register modules for watchdog monitoring (using the discovered ephemeral ports)
    for _name, _dir, _sid in _SUBS:
        _register_module(_sid, port=_LAUNCHER_PROXY_PORTS.get(_sid), cwd=str(_dir), proc=_procs.get(_name))

    boot_modules = {_name: _LAUNCHER_PROXY_PORTS.get(_sid) for _name, _dir, _sid in _SUBS}

    show_boot_progress(boot_modules, poll_interval=0.12, min_ticks=1 if _fast else 6)
    _STUDIO_READY = True
    show_completion_banner(port)

    # Start watchdog after boot completes
    _watchdog_start()

    threading.Timer(1.0, lambda: _open_browser(f"http://localhost:{port}")).start()

    # Block forever — the HTTP server runs in the daemon thread above; SIGINT/SIGTERM
    # invoke _shutdown (stop sub-servers + close socket + exit).
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        _shutdown()


if __name__ == "__main__":
    main()
