"""런처 프록시 동작 테스트 — no-auth 로컬 모드."""
import os
import sys
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# 런처 모듈은 import 시점에 환경변수를 읽어 인증 상태를 초기화하므로,
# import 전에 인증 관련 환경변수를 제거하여 no-auth 모드로 테스트한다.
os.environ.pop("DX_AUTH_ENABLED", None)
os.environ.pop("DX_AUTH_STATE_FILE", None)

import launcher.launcher as lmod



def _get(base, path, headers=None):
    req = urllib.request.Request(f"{base}{path}", headers=headers or {})
    return urllib.request.urlopen(req, timeout=5)



@pytest.fixture()
def live_server(monkeypatch):
    monkeypatch.delenv("DX_AUTH_ENABLED", raising=False)
    monkeypatch.delenv("DX_AUTH_STATE_FILE", raising=False)
    monkeypatch.delenv("DX_AUTH_TEST_PIN", raising=False)
    monkeypatch.delenv("DX_AUTH_TEST_TTL", raising=False)
    for name in ("_auth_state", "_auth_state_file", "_startup_pin", "_auth_session_ttl"):
        if hasattr(lmod, name):
            setattr(lmod, name, None)

    srv = ThreadingHTTPServer(("127.0.0.1", 0), lmod.LauncherHandler)
    host, port = srv.server_address
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield {"server": srv, "base": f"http://127.0.0.1:{port}"}
    srv.shutdown()
    srv.server_close()



def test_proxy_preserves_reverse_proxy_forwarded_host(live_server, monkeypatch):
    observed = {}

    class TargetHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return

        def do_GET(self):
            observed["forwarded_host"] = self.headers.get("X-Forwarded-Host")
            observed["forwarded_proto"] = self.headers.get("X-Forwarded-Proto")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok": true}')

    target = ThreadingHTTPServer(("127.0.0.1", 0), TargetHandler)
    thread = threading.Thread(target=target.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setitem(lmod._LAUNCHER_PROXY_PORTS, "dx_app", target.server_address[1])
    try:
        resp = _get(
            live_server["base"],
            "/app/api/health",
            headers={"X-Forwarded-Host": "studio.example.com", "X-Forwarded-Proto": "https"},
        )
        assert resp.status == 200
    finally:
        target.shutdown()
        target.server_close()

    assert observed == {
        "forwarded_host": "studio.example.com",
        "forwarded_proto": "https",
    }


def test_proxy_does_not_inject_auth_fetch_bridge(live_server, monkeypatch):
    class TargetHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return

        def do_GET(self):
            body = b"<html><head><script id='app-boot'>window.appBoot = true;</script></head><body>app</body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    target = ThreadingHTTPServer(("127.0.0.1", 0), TargetHandler)
    thread = threading.Thread(target=target.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setitem(lmod._LAUNCHER_PROXY_PORTS, "dx_app", target.server_address[1])
    try:
        resp = _get(live_server["base"], "/app/")
        html = resp.read().decode()
    finally:
        target.shutdown()
        target.server_close()

    assert "dx-auth-fetch-bridge" not in html
    assert "app-boot" in html
