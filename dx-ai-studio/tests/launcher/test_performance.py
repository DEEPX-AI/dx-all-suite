"""Launcher transport performance contract tests.

RED contract tests that lock expected launcher behaviour:
- /api/health response shape and port-probe TTL caching
- Reverse proxy gzip static header forwarding
- Reverse proxy HTML widget injection (uncompressed)
- SSE proxy timeout must be 300 s (not 30 s)
"""

import gzip
import importlib.util
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

import pytest

LAUNCHER_PY = Path(__file__).resolve().parent.parent.parent / "launcher" / "launcher.py"


def load_launcher_module():
    spec = importlib.util.spec_from_file_location("launcher", LAUNCHER_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def start_server(handler_cls):
    """Start a ThreadingHTTPServer on a free port and return (server, base_url)."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{port}"


EXPECTED_MODULE_KEYS = sorted([
    "app", "benchmark", "compiler", "monitor",
    "planner", "stream", "zoo", "agent",
])
EXPECTED_ITEM_KEYS = {"port", "alive"}


def test_health_response_shape_and_ttl_caching():
    """Health endpoint must return stable keys and cache port probes for 2 s."""
    launcher = load_launcher_module()

    # Track _is_port_open calls
    call_count = 0
    original_is_port_open = launcher._is_port_open

    def counting_port_open(port):
        nonlocal call_count
        call_count += 1
        return False

    launcher._is_port_open = counting_port_open

    # Fake clock
    fake_time = [1000.0]
    launcher.time = type("FakeTime", (), {
        "time": staticmethod(lambda: fake_time[0]),
        "sleep": staticmethod(lambda _: None),
    })()

    server = None
    try:
        server, base_url = start_server(launcher.LauncherHandler)

        # First call
        resp1 = urlopen(f"{base_url}/api/health", timeout=5)
        data1 = json.loads(resp1.read())

        # Second call at same time — should use cache
        resp2 = urlopen(f"{base_url}/api/health", timeout=5)
        data2 = json.loads(resp2.read())

        # Shape assertions
        assert "launcher_boot" in data1
        assert "studio_ready" in data1
        meta_keys = {"launcher_boot", "studio_ready"}
        module_keys = sorted(k for k in data1 if k not in meta_keys)
        assert module_keys == EXPECTED_MODULE_KEYS
        assert sorted(k for k in data2 if k not in meta_keys) == EXPECTED_MODULE_KEYS
        for key in EXPECTED_MODULE_KEYS:
            assert set(data1[key].keys()) == EXPECTED_ITEM_KEYS
            assert set(data2[key].keys()) == EXPECTED_ITEM_KEYS

        # Responses should be equal (cached)
        assert data1 == data2

        # With TTL caching, only 8 calls (one per service) on first request
        assert call_count == 8, (
            f"Expected 8 _is_port_open calls (cached second call), got {call_count}"
        )

        # Advance fake time past 2 s TTL
        fake_time[0] += 2.1

        resp3 = urlopen(f"{base_url}/api/health", timeout=5)
        data3 = json.loads(resp3.read())

        assert sorted(k for k in data3 if k not in meta_keys) == EXPECTED_MODULE_KEYS
        assert call_count == 16, (
            f"Expected 16 _is_port_open calls after TTL expiry, got {call_count}"
        )
    finally:
        if server:
            server.shutdown()
            server.server_close()


def test_proxy_preserves_gzip_headers():
    """Proxy must forward Content-Encoding: gzip and body unchanged for static."""
    launcher = load_launcher_module()

    original_css = b"body { color: red; }\n"
    gzipped_css = gzip.compress(original_css)

    class GzipBackend(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/css")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Vary", "Accept-Encoding")
            self.send_header("Content-Length", str(len(gzipped_css)))
            self.end_headers()
            self.wfile.write(gzipped_css)

        def log_message(self, *args):
            pass

    backend = None
    proxy = None
    try:
        backend, backend_url = start_server(GzipBackend)
        backend_port = backend.server_address[1]

        class ProxyHandler(launcher.LauncherHandler):
            def route(self):
                launcher._proxy(self, backend_port, self.url_path, inject_widget=True)

        proxy, proxy_url = start_server(ProxyHandler)

        resp = urlopen(f"{proxy_url}/static/style.css", timeout=5)
        headers = resp.headers
        body = resp.read()

        assert headers.get("Content-Encoding") == "gzip", (
            f"Expected Content-Encoding: gzip, got {headers.get('Content-Encoding')}"
        )
        assert headers.get("Vary") == "Accept-Encoding"
        assert gzip.decompress(body) == original_css
    finally:
        if proxy:
            proxy.shutdown()
            proxy.server_close()
        if backend:
            backend.shutdown()
            backend.server_close()


def test_proxy_html_injection_uncompressed():
    """Widget injection into HTML must produce uncompressed output."""
    launcher = load_launcher_module()

    # Monkeypatch widget cache
    launcher._WIDGET_CACHE = b"<script>widget()</script>"

    html_body = b"<html><body><p>hello</p></body></html>"

    class HtmlBackend(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_body)))
            self.end_headers()
            self.wfile.write(html_body)

        def log_message(self, *args):
            pass

    backend = None
    proxy = None
    try:
        backend, backend_url = start_server(HtmlBackend)
        backend_port = backend.server_address[1]

        class ProxyHandler(launcher.LauncherHandler):
            def route(self):
                launcher._proxy(self, backend_port, self.url_path, inject_widget=True)

        proxy, proxy_url = start_server(ProxyHandler)

        resp = urlopen(f"{proxy_url}/index.html", timeout=5)
        headers = resp.headers
        body = resp.read()

        # Must NOT be compressed
        assert headers.get("Content-Encoding") is None, (
            f"Injected HTML must not be compressed, got Content-Encoding: {headers.get('Content-Encoding')}"
        )
        # Must contain injected widget before </body>
        assert b"<script>widget()</script>" in body
        assert b"<script>widget()</script></body>" in body
    finally:
        if proxy:
            proxy.shutdown()
            proxy.server_close()
        if backend:
            backend.shutdown()
            backend.server_close()


def test_proxy_reloads_hw_widget_when_widget_file_changes(tmp_path):
    """Launcher proxy must not keep injecting stale hardware widget markup."""
    launcher = load_launcher_module()

    widget_dir = tmp_path / "shared" / "hw_widget"
    widget_dir.mkdir(parents=True)
    widget_file = widget_dir / "widget.html"
    widget_file.write_text("<script>oldWidget()</script>", encoding="utf-8")
    launcher.STUDIO_DIR = tmp_path
    launcher._load_widget_cache()
    widget_file.write_text("<script>newWidget()</script>", encoding="utf-8")

    html_body = b"<html><body><p>hello</p></body></html>"

    class HtmlBackend(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_body)))
            self.end_headers()
            self.wfile.write(html_body)

        def log_message(self, *args):
            pass

    backend = None
    proxy = None
    try:
        backend, _ = start_server(HtmlBackend)
        backend_port = backend.server_address[1]

        class ProxyHandler(launcher.LauncherHandler):
            def route(self):
                launcher._proxy(self, backend_port, self.url_path, inject_widget=True)

        proxy, proxy_url = start_server(ProxyHandler)

        body = urlopen(f"{proxy_url}/index.html", timeout=5).read()

        assert b"<script>newWidget()</script>" in body
        assert b"<script>oldWidget()</script>" not in body
    finally:
        if proxy:
            proxy.shutdown()
            proxy.server_close()
        if backend:
            backend.shutdown()
            backend.server_close()


def test_sse_proxy_timeout_extended():
    """SSE proxy timeout must be 300 s, not the default 30 s."""
    source = LAUNCHER_PY.read_text(encoding="utf-8")
    assert "conn.sock.settimeout(30)" not in source, (
        "SSE proxy uses 30 s timeout — must be extended to 300 s"
    )
    assert "conn.sock.settimeout(300)" in source, (
        "SSE proxy timeout must be set to 300 s"
    )
