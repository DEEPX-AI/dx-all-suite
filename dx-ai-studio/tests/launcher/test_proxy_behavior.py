"""Launcher proxy behaviour tests in no-auth local mode."""
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

# The launcher module reads environment variables at import to set up auth, so the auth
# variables are removed before import to test no-auth mode.
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


class _ChunkedTarget(BaseHTTPRequestHandler):
    """A module streaming its answer the way shared/dx_server does: HTTP/1.1, chunked, no Content-Length."""
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        return

    def _chunk(self, data: bytes):
        self.wfile.write(b"%x\r\n%s\r\n" % (len(data), data))

    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        sse = self.path.endswith("/chat")
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream" if sse else "application/x-ndjson")
        if sse:
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Accel-Buffering", "no")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        for part in (b'data: {"token": "hel"}\n\n', b'data: {"token": "lo"}\n\n', b"data: [DONE]\n\n"):
            self._chunk(part)
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()


@pytest.mark.parametrize("path", ["/app/api/chat", "/app/api/stream_lines"])
def test_a_streamed_response_ends_and_headers_are_not_doubled(live_server, monkeypatch, path):
    """A Chat answer relayed by the proxy must end where the module's stream ends, with no duplicated headers
    (Server / Date / Cache-Control / X-Accel-Buffering). A de-chunked stream relayed with neither a length nor
    chunking on a kept-alive HTTP/1.1 connection leaves the browser unable to tell where the response stops, so each
    answer would hold a connection open."""
    import http.client
    import time

    target = ThreadingHTTPServer(("127.0.0.1", 0), _ChunkedTarget)
    threading.Thread(target=target.serve_forever, daemon=True).start()
    monkeypatch.setitem(lmod._LAUNCHER_PROXY_PORTS, "dx_app", target.server_address[1])
    host, port = live_server["base"].rsplit("/", 1)[-1].split(":")
    conn = http.client.HTTPConnection(host, int(port), timeout=5)
    try:
        t0 = time.monotonic()
        conn.request("POST", path, body=b'{"message": "hi"}',
                     headers={"Content-Type": "application/json", "Origin": live_server["base"]})
        resp = conn.getresponse()
        body = resp.read()   # times out if the response has no end
        assert time.monotonic() - t0 < 4
        assert body.endswith(b"data: [DONE]\n\n")
        names = [k.lower() for k, _ in resp.getheaders()]
        doubled = sorted({n for n in names if names.count(n) > 1})
        assert doubled == []
    finally:
        conn.close()
        target.shutdown()
        target.server_close()
