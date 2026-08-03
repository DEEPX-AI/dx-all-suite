#!/usr/bin/env python3
"""DX Monitor Server — Hardware dashboard (port 8098)."""
import argparse
import os
import signal
import socket
import sys
import threading
import time
import webbrowser
from http.server import ThreadingHTTPServer
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

from dx_monitor.core.config import DEFAULT_PORT, STATIC_DIR, TEMPLATES_DIR, SERVER_NAME, DX_APP_ROOT
from dx_monitor.core import hardware_init, events

if os.environ.get("DX_MONITOR_SKIP_HARDWARE_INIT") == "1":
    from shared.hardware import init_hw
    init_hw(ds=None, dx_ok=False, app_root=DX_APP_ROOT)
    _telemetry_supervisor = None
else:
    _telemetry_supervisor = hardware_init.init()
    events.init()

from shared.hardware import get_hw, get_sysinfo
from shared.dx_server import DXBaseHandler, DXServer, _resolve_bind_host
from shared.chat import ChatEngine

PORT = DEFAULT_PORT

_lifecycle_lock = threading.Lock()
_lifecycle_owners = set()
_lifecycle_shutdown = False

_chat_engine = ChatEngine(
    app_name="dx_monitor",
    fallback_rules=[
        (["hardware", "monitor", "npu", "하드웨어", "모니터", "상태"], {
            "ko": "DX Monitor에서 NPU, CPU, 메모리, 디스크 상태를 실시간으로 확인할 수 있습니다.",
            "en": "Use DX Monitor to check NPU, CPU, memory, and disk status in real time.",
        }),
        (["event", "events", "로그", "이벤트"], {
            "ko": "Events API와 화면 로그에서 최근 하드웨어 상태 변화를 확인할 수 있습니다.",
            "en": "Use the Events API and on-screen logs to review recent hardware status changes.",
        }),
    ],
)

class MonitorHandler(DXBaseHandler):
    server_name = SERVER_NAME
    static_dir = STATIC_DIR
    templates_dir = TEMPLATES_DIR
    log_filter = ["/static/", "/api/hw", "/api/hb"]

    def _sse(self):
        self.start_sse()
        try:
            while True:
                d = get_hw()
                if not self.send_sse_data(d):
                    break
                time.sleep(1.5)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self.end_sse()

    def route(self):
        if self.handle_chat_routes(_chat_engine):
            return

        if self.route_common():
            return

        if self.command == "GET":
            if self.url_path == "/api/hw_status":
                return self.send_json(get_hw())
            if self.url_path == "/api/hw_stream":
                return self._sse()
            if self.url_path == "/api/system_info":
                return self.send_json(get_sysinfo())
            if self.url_path == "/api/hb":
                return self.send_json({"ok": True})
            if self.url_path == "/api/events":
                since = self.read_query_param("since", "0")
                return self.send_json(events.get_events(since=since))

        self.route_legacy()


def _claim_hardware_lifecycle(server):
    """Register a server that must close before Monitor telemetry can stop."""
    with _lifecycle_lock:
        if _lifecycle_shutdown:
            return False
        _lifecycle_owners.add(server)
        return True


def _release_hardware_lifecycle(server):
    """Stop Monitor telemetry only after the final owning server closes."""
    global _lifecycle_shutdown
    with _lifecycle_lock:
        if server not in _lifecycle_owners:
            return False
        _lifecycle_owners.remove(server)
        if _lifecycle_owners or _lifecycle_shutdown:
            return False
        _lifecycle_shutdown = True
    hardware_init.shutdown()
    return True


class _MonitorHTTPServer(ThreadingHTTPServer):
    """HTTP server with shared, idempotent Monitor telemetry ownership."""

    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address, request_handler_class, address_family=None):
        if address_family is not None:
            self.address_family = address_family
        # ThreadingHTTPServer calls server_close() when bind fails.  Initialise
        # lifecycle state first so that cleanup preserves the original OSError.
        self._hardware_lifecycle_lock = threading.Lock()
        self._hardware_lifecycle_owner = False
        self._hardware_lifecycle_released = True
        super().__init__(server_address, request_handler_class)
        self._hardware_lifecycle_owner = _claim_hardware_lifecycle(self)
        self._hardware_lifecycle_released = False

    def server_bind(self):
        if self.address_family == socket.AF_INET6:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()

    def _release_hardware_lifecycle(self):
        with self._hardware_lifecycle_lock:
            if self._hardware_lifecycle_released:
                return
            self._hardware_lifecycle_released = True
            owns_lifecycle = self._hardware_lifecycle_owner
        if owns_lifecycle:
            _release_hardware_lifecycle(self)

    def shutdown(self):
        try:
            super().shutdown()
        finally:
            self._release_hardware_lifecycle()

    def server_close(self):
        try:
            super().server_close()
        finally:
            self._release_hardware_lifecycle()


def create_server(port: int = PORT):
    """Create a testable DX Monitor HTTP server."""
    return _MonitorHTTPServer(("127.0.0.1", port), MonitorHandler)


class _MonitorServerRunner(DXServer):
    """DXServer runner that preserves bind behavior with Monitor lifecycle hooks."""

    def __init__(self, handler_class, name: str, default_port: int):
        super().__init__(handler_class, name, default_port)
        self._shutdown_lock = threading.Lock()
        self._shutdown_requested = False

    def start(self):
        """Create and serve Monitor without the blocking DXServer signal handler."""
        parser = argparse.ArgumentParser(description=f"{self.name} Server")
        parser.add_argument("--port", "-p", type=int, default=self.default_port)
        parser.add_argument("--no-browser", action="store_true",
                            help="브라우저 자동 열기 억제")
        args = parser.parse_args()

        server = self.create_http_server(args.port)
        if server is None:
            sys.exit(1)

        actual_port = server.server_address[1]
        self.register_signals()
        self.print_banner(actual_port)

        if not args.no_browser:
            url = f"http://localhost:{actual_port}"
            threading.Timer(1.0, lambda: webbrowser.open(url)).start()

        server.serve_forever()

    def _register_signals(self):
        """Request shutdown from a worker so signal delivery cannot deadlock serving."""
        def _shutdown(*_):
            print(f"\n  [{self.name}] Shutting down...")
            with self._shutdown_lock:
                if self._shutdown_requested or self._server is None:
                    return
                self._shutdown_requested = True
                threading.Thread(
                    target=self._server.shutdown,
                    name=f"{self.name}-shutdown",
                    daemon=True,
                ).start()

        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

    def _create_server(self, port: int, max_attempts: int = 5):
        bind_host = _resolve_bind_host()
        for attempt in range(max_attempts):
            if port != 0 and (self._is_port_open(port) or attempt > 0):
                print(f"  [{self.name}] Port {port} in use — releasing "
                      f"(attempt {attempt + 1}/{max_attempts})...")
                self._force_free_port(port)

            if bind_host:
                try:
                    return _MonitorHTTPServer((bind_host, port), self.handler_class)
                except OSError as exc:
                    if attempt == max_attempts - 1:
                        print(f"  [{self.name}] ERROR: Cannot bind {bind_host}:{port}: {exc}")
                        return None
                    print(f"  [{self.name}] Bind failed ({exc}), retrying...")
                    continue

            try:
                return _MonitorHTTPServer(
                    ("::", port),
                    self.handler_class,
                    address_family=socket.AF_INET6,
                )
            except OSError:
                pass

            try:
                return _MonitorHTTPServer(("0.0.0.0", port), self.handler_class)
            except OSError as exc:
                if attempt == max_attempts - 1:
                    print(f"  [{self.name}] ERROR: Cannot bind port {port}: {exc}")
                    return None
                print(f"  [{self.name}] Bind failed ({exc}), retrying...")

        return None


def run_server():
    """Run Monitor with the same lifecycle-aware server in every entry path."""
    runner = _MonitorServerRunner(MonitorHandler, SERVER_NAME, PORT)
    try:
        runner.start()
    except KeyboardInterrupt:
        pass
    finally:
        if runner._server is not None:
            runner._server.shutdown()
            runner._server.server_close()


if __name__ == "__main__":
    run_server()
