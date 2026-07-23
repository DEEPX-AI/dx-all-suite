"""Static file transport performance contract tests.

These tests lock the expected HTTP transport behavior for DXBaseHandler.send_file()
and serve_static(): HTTP/1.1, cache headers, ETag, Last-Modified, 304 responses,
gzip for safe text assets, and keep-alive connection reuse.
"""

import gzip
import http.client
import socket
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from shared.dx_server import DXBaseHandler

# Per RFC 7232 §4.1, a 304 response MUST NOT contain a body.
# Content-Length MUST be omitted for 304 responses.


def _assert_304_no_content_length(headers):
    cl = headers.get("Content-Length")
    assert cl is None, (
        f"304 response must omit Content-Length, got {cl!r}"
    )


class StaticPerfHandler(DXBaseHandler):
    server_name = "StaticPerfTest"
    log_silent = True


def test_dx_base_handler_suppresses_client_disconnect_tracebacks(capsys):
    """Client aborts should not print BrokenPipe tracebacks from request handling."""
    class AbortHandler(DXBaseHandler):
        log_silent = True

        def route(self):
            payload = b"x" * (2 * 1024 * 1024)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            for _ in range(8):
                self.wfile.write(payload)
                self.wfile.flush()

    server = ThreadingHTTPServer(("127.0.0.1", 0), AbortHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with socket.create_connection(("127.0.0.1", server.server_address[1]), timeout=5) as sock:
            sock.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
            sock.recv(128)
        thread.join(timeout=0.2)
    finally:
        server.shutdown()
        server.server_close()

    captured = capsys.readouterr()
    assert "BrokenPipeError" not in captured.err
    assert "ConnectionResetError" not in captured.err


@pytest.fixture
def static_server(tmp_path):
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "app.js").write_text("window.answer = 42;\n", encoding="utf-8")
    (static_dir / "style.css").write_text("body { color: white; }\n", encoding="utf-8")
    (static_dir / "index.html").write_text("<html><body>Hello</body></html>\n", encoding="utf-8")
    (static_dir / "font.woff2").write_bytes(b"\x00woff2" + b"x" * 256)

    _sd = static_dir

    class Handler(StaticPerfHandler):
        static_dir = _sd

        def route(self):
            if self.url_path == "/sse":
                self.start_sse()
                self.send_sse_data({"ok": True})
                self.end_sse()
                return
            return super().route()

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def test_static_response_uses_http11_cache_headers_and_validators(static_server):
    resp = urlopen(f"{static_server}/static/app.js", timeout=5)
    body = resp.read()
    assert resp.version == 11
    assert body == b"window.answer = 42;\n"
    assert resp.headers["Cache-Control"] == "no-cache, must-revalidate"
    assert resp.headers["ETag"].startswith('W/"')
    assert resp.headers["Last-Modified"]
    assert resp.headers["Access-Control-Allow-Origin"] == "*"
    assert resp.headers["Vary"] == "Accept-Encoding"


def test_static_response_returns_304_for_matching_etag(static_server):
    first = urlopen(f"{static_server}/static/app.js", timeout=5)
    etag = first.headers["ETag"]
    first.read()
    req = Request(f"{static_server}/static/app.js", headers={"If-None-Match": etag})
    with pytest.raises(HTTPError) as exc_info:
        urlopen(req, timeout=5)
    assert exc_info.value.code == 304
    assert exc_info.value.headers["ETag"] == etag
    _assert_304_no_content_length(exc_info.value.headers)


def test_static_response_returns_304_for_matching_if_modified_since(static_server):
    first = urlopen(f"{static_server}/static/app.js", timeout=5)
    last_modified = first.headers["Last-Modified"]
    first.read()
    req = Request(
        f"{static_server}/static/app.js",
        headers={"If-Modified-Since": last_modified},
    )
    with pytest.raises(HTTPError) as exc_info:
        urlopen(req, timeout=5)
    assert exc_info.value.code == 304
    assert exc_info.value.headers["Last-Modified"] == last_modified
    _assert_304_no_content_length(exc_info.value.headers)


def test_safe_text_static_gzip_preserves_decompressed_content(static_server):
    req = Request(f"{static_server}/static/style.css", headers={"Accept-Encoding": "gzip"})
    resp = urlopen(req, timeout=5)
    body = resp.read()
    assert resp.headers["Content-Encoding"] == "gzip"
    assert resp.headers["Vary"] == "Accept-Encoding"
    assert int(resp.headers["Content-Length"]) == len(body)
    assert gzip.decompress(body) == b"body { color: white; }\n"


def test_html_sse_and_binary_are_not_gzipped(static_server):
    html_req = Request(f"{static_server}/static/index.html", headers={"Accept-Encoding": "gzip"})
    html_resp = urlopen(html_req, timeout=5)
    assert html_resp.headers.get("Content-Encoding") is None
    assert html_resp.headers["Cache-Control"] == "no-cache"
    assert html_resp.read() == b"<html><body>Hello</body></html>\n"

    font_req = Request(f"{static_server}/static/font.woff2", headers={"Accept-Encoding": "gzip"})
    font_resp = urlopen(font_req, timeout=5)
    assert font_resp.headers.get("Content-Encoding") is None
    assert font_resp.headers["Cache-Control"] == "public, max-age=86400, must-revalidate"

    sse_req = Request(f"{static_server}/sse", headers={"Accept-Encoding": "gzip"})
    sse_resp = urlopen(sse_req, timeout=5)
    assert sse_resp.headers.get("Content-Encoding") is None
    assert "text/event-stream" in sse_resp.headers["Content-Type"]


def test_http11_keep_alive_handles_sequential_static_requests(static_server):
    host = (static_server[7:] if static_server.startswith("http://") else static_server)
    conn = http.client.HTTPConnection(host, timeout=5)
    try:
        conn.request("GET", "/static/app.js")
        first = conn.getresponse()
        assert first.status == 200
        assert first.read() == b"window.answer = 42;\n"

        conn.request("GET", "/static/style.css", headers={"Accept-Encoding": "gzip"})
        second = conn.getresponse()
        compressed = second.read()
        assert second.status == 200
        assert second.getheader("Content-Encoding") == "gzip"
        assert gzip.decompress(compressed) == b"body { color: white; }\n"
    finally:
        conn.close()


def test_sse_uses_chunked_transfer_encoding_no_content_length(static_server):
    """SSE responses use Transfer-Encoding: chunked and omit Content-Length."""
    host = (static_server[7:] if static_server.startswith("http://") else static_server)
    conn = http.client.HTTPConnection(host, timeout=5)
    try:
        conn.request("GET", "/sse")
        resp = conn.getresponse()
        assert resp.status == 200
        assert "text/event-stream" in resp.getheader("Content-Type", "")
        assert resp.getheader("Transfer-Encoding") == "chunked"
        assert resp.getheader("Content-Length") is None
        body = resp.read().decode("utf-8")
        assert "data:" in body
    finally:
        conn.close()


def test_304_includes_cache_headers_but_no_content_length(static_server):
    """304 must include cache validators but omit Content-Length."""
    host = (static_server[7:] if static_server.startswith("http://") else static_server)
    conn = http.client.HTTPConnection(host, timeout=5)
    try:
        conn.request("GET", "/static/style.css")
        first = conn.getresponse()
        etag = first.getheader("ETag")
        first.read()

        conn.request("GET", "/static/style.css", headers={"If-None-Match": etag})
        second = conn.getresponse()
        second.read()
        assert second.status == 304
        assert second.getheader("Content-Length") is None
        assert second.getheader("ETag") == etag
        assert second.getheader("Cache-Control") is not None
        assert second.getheader("Last-Modified") is not None
        assert second.getheader("Access-Control-Allow-Origin") == "*"
        assert second.getheader("Vary") == "Accept-Encoding"
    finally:
        conn.close()




def test_serve_template_rewrites_local_assets_with_content_hash(tmp_path):
    """serve_template() rewrites local /static/js and /static/css URLs with m= and v=."""
    static_dir = tmp_path / "dx_sample" / "static"
    templates_dir = tmp_path / "dx_sample" / "templates"
    shared_dir = Path(__file__).resolve().parents[2] / "shared" / "static"
    static_dir.mkdir(parents=True)
    templates_dir.mkdir(parents=True)
    (static_dir / "js").mkdir()
    (static_dir / "css").mkdir()
    (static_dir / "js" / "app.js").write_text("window.hashTest = 1;\n", encoding="utf-8")
    (static_dir / "css" / "style.css").write_text("body { color: red; }\n", encoding="utf-8")
    (templates_dir / "index.html").write_text(
        '<link rel="stylesheet" href="/static/css/style.css?v=old">'
        '<script src="/static/js/app.js?m=wrong&v=old"></script>'
        '<script src="/static/shared/i18n.js"></script>'
        '<script src="https://example.com/app.js?v=old"></script>',
        encoding="utf-8",
    )

    _sd = static_dir
    _td = templates_dir

    class Handler(StaticPerfHandler):
        static_dir = _sd
        templates_dir = _td

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        resp = urlopen(f"http://127.0.0.1:{server.server_address[1]}/", timeout=5)
        html = resp.read().decode()
    finally:
        server.shutdown()
        server.server_close()

    # Cache-Control must be no-cache for template HTML
    assert resp.headers["Cache-Control"] == "no-cache"
    # Module-local assets get m=<module> and v=<hash>
    assert '/static/css/style.css?m=dx_sample&v=' in html
    assert '/static/js/app.js?m=dx_sample&v=' in html
    # Old manual v= and wrong m= must be replaced in local URLs
    assert "/static/css/style.css?v=old" not in html
    assert "/static/js/app.js?m=wrong" not in html
    assert "/static/js/app.js?v=old" not in html
    # Shared assets get v= but no m=
    assert '/static/shared/i18n.js?v=' in html
    assert '/static/shared/i18n.js?m=' not in html
    # External URLs are unchanged
    assert 'https://example.com/app.js?v=old' in html


def test_asset_hash_rewrite_ignores_protocol_relative_urls(tmp_path):
    """Protocol-relative CDN URLs must not be treated as local launcher root assets."""
    static_root = tmp_path / "launcher_static"
    static_root.mkdir()
    (static_root / "app.js").write_text("window.localAsset = true;\n", encoding="utf-8")

    _root = static_root

    class Handler(StaticPerfHandler):
        static_dir = _root

    handler = object.__new__(Handler)
    html = (
        '<script src="//cdn.example.com/app.js?v=cdn"></script>'
        '<script src="/app.js?v=old"></script>'
    )

    rewritten = handler.render_html_with_asset_hashes(
        html,
        asset_scope=None,
        extra_static_roots=[static_root],
    )

    assert '//cdn.example.com/app.js?v=cdn' in rewritten
    assert '/app.js?v=' in rewritten
    assert '/app.js?v=old' not in rewritten


def test_asset_hash_changes_when_content_changes(tmp_path):
    """Content hash changes when file content changes, always 8 chars."""
    static_dir = tmp_path / "dx_hash" / "static"
    static_dir.mkdir(parents=True)
    asset = static_dir / "app.js"
    asset.write_text("one\n", encoding="utf-8")

    first = DXBaseHandler.asset_content_hash(asset)
    asset.write_text("two\n", encoding="utf-8")
    second = DXBaseHandler.asset_content_hash(asset)

    assert first != second
    assert len(first) == 8
    assert len(second) == 8


def test_static_path_containment_rejects_sibling_prefix_traversal(tmp_path):
    base = tmp_path / "static"
    sibling = tmp_path / "staticevil"
    base.mkdir()
    sibling.mkdir()
    (sibling / "secret.txt").write_text("SECRET", encoding="utf-8")

    _base = base

    class Handler(StaticPerfHandler):
        static_dir = _base

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with pytest.raises(HTTPError) as exc_info:
            urlopen(f"http://127.0.0.1:{server.server_address[1]}/static/../staticevil/secret.txt", timeout=5)
        assert exc_info.value.code == 403
    finally:
        server.shutdown()
        server.server_close()


def test_asset_hash_cache_replaces_old_entry_for_same_path(tmp_path):
    static_dir = tmp_path / "dx_hash" / "static"
    static_dir.mkdir(parents=True)
    asset = static_dir / "app.js"

    DXBaseHandler._asset_hash_cache.clear()
    asset.write_text("one\n", encoding="utf-8")
    first = DXBaseHandler.asset_content_hash(asset)
    asset.write_text("two\n", encoding="utf-8")
    second = DXBaseHandler.asset_content_hash(asset)

    keys_for_asset = [
        key for key in DXBaseHandler._asset_hash_cache
        if key[0] == str(asset.resolve())
    ]
    assert first != second
    assert len(keys_for_asset) == 1


def test_production_sse_handlers_call_end_sse():
    """All production SSE handlers must call end_sse() in finally blocks."""
    import ast

    handler_files = {
        "dx_stream/server.py": ["_sse"],
        "dx_monitor/server.py": ["_sse"],
        "dx_compiler/server.py": ["_sse_progress", "_sse_setup"],
        "dx_benchmark/server.py": ["_serve_benchmark_sse"],
    }
    base = Path(__file__).resolve().parents[2]
    for rel_path, methods in handler_files.items():
        src = (base / rel_path).read_text(encoding="utf-8")
        tree = ast.parse(src, filename=rel_path)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if node.name not in methods:
                continue
            # Verify end_sse() is called inside a finally block (ast.Try.finalbody)
            found_in_finally = False
            for child in ast.walk(node):
                if not isinstance(child, ast.Try) or not child.finalbody:
                    continue
                for fb_node in ast.walk(ast.Module(body=child.finalbody, type_ignores=[])):
                    if (
                        isinstance(fb_node, ast.Call)
                        and isinstance(fb_node.func, ast.Attribute)
                        and fb_node.func.attr == "end_sse"
                        and isinstance(fb_node.func.value, ast.Name)
                        and fb_node.func.value.id == "self"
                    ):
                        found_in_finally = True
                        break
                if found_in_finally:
                    break
            assert found_in_finally, (
                f"{rel_path}::{node.name} must call self.end_sse() inside a finally block"
            )