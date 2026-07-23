#!/usr/bin/env python3
"""DX Monitor Server — Hardware dashboard (port 8098)."""
import os
import sys
import time
from http.server import ThreadingHTTPServer
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

from dx_monitor.core.config import DEFAULT_PORT, STATIC_DIR, TEMPLATES_DIR, SERVER_NAME, DX_APP_ROOT
from dx_monitor.core import hardware_init, events

if os.environ.get("DX_MONITOR_SKIP_HARDWARE_INIT") == "1":
    from shared.hardware import init_hw
    init_hw(ds=None, dx_ok=False, app_root=DX_APP_ROOT)
else:
    hardware_init.init()
    events.init()

from shared.hardware import get_hw, get_sysinfo
from shared.dx_server import DXBaseHandler
from shared.chat import ChatEngine

PORT = DEFAULT_PORT

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
                since = float(self.read_query_param("since", "0"))
                return self.send_json(events.get_events(since=since))

        self.route_legacy()

def create_server(port: int = PORT):
    """Create a testable DX Monitor HTTP server."""
    return ThreadingHTTPServer(("127.0.0.1", port), MonitorHandler)


if __name__ == "__main__":
    from shared.dx_server import DXServer
    DXServer(MonitorHandler, SERVER_NAME, PORT).start()
