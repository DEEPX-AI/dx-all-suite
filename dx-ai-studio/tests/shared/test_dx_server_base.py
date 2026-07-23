#!/usr/bin/env python3
"""DXBaseHandler + DXServer 단위 테스트."""

import io
import json
import sys
import tempfile
import threading
import time
import unittest
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.request import urlopen, Request
from urllib.error import HTTPError

from shared.dx_server import DXBaseHandler, DXServer


class HandlerUnderTest(DXBaseHandler):
    """테스트용 핸들러."""
    server_name = "TestServer"
    cache_enabled = True
    cache_max = 3
    cache_ttl = 2
    log_silent = True

    # 각 인스턴스가 별도 캐시를 갖도록 클래스 변수 리셋
    _cache = {}
    _cache_lock = threading.Lock()


def _make_handler():
    """테스트용 mock handler 생성."""
    handler = HandlerUnderTest.__new__(HandlerUnderTest)
    handler.wfile = io.BytesIO()
    handler.headers = {}
    handler._headers_buffer = []

    # mock send_response, send_header, end_headers
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()
    return handler


class TestSendJson(unittest.TestCase):
    def test_send_json_200(self):
        handler = _make_handler()
        data = {"ok": True, "value": 42}
        handler.send_json(data)

        handler.send_response.assert_called_once_with(200)
        written = handler.wfile.getvalue()
        parsed = json.loads(written)
        self.assertEqual(parsed["ok"], True)
        self.assertEqual(parsed["value"], 42)

    def test_send_json_custom_code(self):
        handler = _make_handler()
        handler.send_json({"error": "bad"}, code=400)
        handler.send_response.assert_called_once_with(400)

    def test_send_json_unicode(self):
        handler = _make_handler()
        handler.send_json({"msg": "한글 테스트"})
        written = handler.wfile.getvalue()
        self.assertIn("한글", written.decode("utf-8"))


class TestSendErrorJson(unittest.TestCase):
    def test_error_json_structure(self):
        handler = _make_handler()
        handler.send_error_json(404, "Not found")

        written = handler.wfile.getvalue()
        parsed = json.loads(written)
        self.assertEqual(parsed["error"], "Not found")
        handler.send_response.assert_called_once_with(404)


class TestCache(unittest.TestCase):
    def setUp(self):
        HandlerUnderTest._cache = {}

    def test_cache_get_set(self):
        handler = _make_handler()
        data = {"key": "value"}
        result = {"computed": True}

        # 캐시 미스
        self.assertIsNone(handler.cache_get("test", data))

        # 캐시 저장
        handler.cache_set("test", data, result)

        # 캐시 히트
        cached = handler.cache_get("test", data)
        self.assertEqual(cached, result)

    def test_cache_ttl_expiry(self):
        handler = _make_handler()
        handler.cache_ttl = 0  # 즉시 만료

        data = {"key": "val"}
        handler.cache_set("test", data, {"r": 1})
        time.sleep(0.1)
        self.assertIsNone(handler.cache_get("test", data))

    def test_cache_lru_eviction(self):
        handler = _make_handler()
        # cache_max = 3, 4개 넣으면 가장 오래된 것 제거
        for i in range(4):
            handler.cache_set("p", {"i": i}, {"result": i})
            time.sleep(0.01)  # 순서 보장

        # 첫 번째 (i=0) 항목이 제거됨
        self.assertIsNone(handler.cache_get("p", {"i": 0}))
        # 나머지는 존재
        self.assertIsNotNone(handler.cache_get("p", {"i": 1}))
        self.assertIsNotNone(handler.cache_get("p", {"i": 2}))
        self.assertIsNotNone(handler.cache_get("p", {"i": 3}))

    def test_cache_clear(self):
        handler = _make_handler()
        handler.cache_set("a", {"x": 1}, "r1")
        handler.cache_set("b", {"x": 2}, "r2")
        count = handler.cache_clear()
        self.assertEqual(count, 2)
        self.assertIsNone(handler.cache_get("a", {"x": 1}))

    def test_cache_stats(self):
        handler = _make_handler()
        handler.cache_set("a", {"x": 1}, "r1")
        stats = handler.cache_stats()
        self.assertEqual(stats["cached_entries"], 1)
        self.assertEqual(stats["max"], 3)

    def test_cache_disabled(self):
        handler = _make_handler()
        handler.cache_enabled = False
        handler.cache_set("test", {"k": "v"}, "result")
        self.assertIsNone(handler.cache_get("test", {"k": "v"}))


class TestIsSafePath(unittest.TestCase):
    def test_safe_path_within_dir(self):
        allowed = "/tmp"
        self.assertTrue(DXBaseHandler.is_safe_path("/tmp/file.txt", allowed))

    def test_traversal_rejected(self):
        allowed = "/tmp"
        self.assertFalse(DXBaseHandler.is_safe_path("/tmp/../etc/passwd", allowed))

    def test_sibling_prefix_rejected(self):
        allowed = "/tmp/static"
        self.assertFalse(DXBaseHandler.is_safe_path("/tmp/staticevil/secret.txt", allowed))

    def test_safe_path_no_allowed_dir(self):
        self.assertTrue(DXBaseHandler.is_safe_path("subdir/file.txt"))

    def test_traversal_no_allowed_dir(self):
        self.assertFalse(DXBaseHandler.is_safe_path("../etc/passwd"))


class TestSanitizeId(unittest.TestCase):
    def test_valid_id(self):
        self.assertEqual(DXBaseHandler.sanitize_id("model_v2-3"), "model_v2-3")

    def test_valid_id_with_dot(self):
        self.assertEqual(DXBaseHandler.sanitize_id("model.onnx"), "model.onnx")

    def test_invalid_id_slash(self):
        self.assertIsNone(DXBaseHandler.sanitize_id("../etc/passwd"))

    def test_invalid_id_empty(self):
        self.assertIsNone(DXBaseHandler.sanitize_id(""))

    def test_invalid_id_space(self):
        self.assertIsNone(DXBaseHandler.sanitize_id("bad id"))


class TestParseRequest(unittest.TestCase):
    def test_parse_basic_url(self):
        handler = _make_handler()
        handler.path = "/api/test?key=value&flag=true"
        handler._parse_request_url()

        self.assertEqual(handler.url_path, "/api/test")
        self.assertEqual(handler.query["key"], ["value"])
        self.assertEqual(handler.query["flag"], ["true"])

    def test_parse_root_slash(self):
        handler = _make_handler()
        handler.path = "/"
        handler._parse_request_url()
        self.assertEqual(handler.url_path, "/")

    def test_parse_trailing_slash(self):
        handler = _make_handler()
        handler.path = "/api/test/"
        handler._parse_request_url()
        self.assertEqual(handler.url_path, "/api/test")

    def test_parse_encoded_url(self):
        handler = _make_handler()
        handler.path = "/api/test%20space"
        handler._parse_request_url()
        self.assertEqual(handler.url_path, "/api/test space")


class TestSendHtml(unittest.TestCase):
    def test_send_html_string(self):
        handler = _make_handler()
        handler.send_html("<h1>Hello</h1>")
        handler.send_response.assert_called_once_with(200)
        self.assertIn(b"<h1>Hello</h1>", handler.wfile.getvalue())

    def test_send_html_bytes(self):
        handler = _make_handler()
        handler.send_html(b"<p>bytes</p>")
        self.assertIn(b"<p>bytes</p>", handler.wfile.getvalue())


class TestCheckSameOrigin(unittest.TestCase):
    """_check_same_origin() reverse-proxy origin 검증 테스트."""

    @staticmethod
    def _make_handler_with_headers(headers: dict):
        h = _make_handler()
        h.headers = headers
        return h

    def test_forwarded_https_accepts_https_origin(self):
        h = self._make_handler_with_headers({
            "Host": "127.0.0.1:8090",
            "Origin": "https://studio.example.com",
            "X-Forwarded-Host": "studio.example.com",
            "X-Forwarded-Proto": "https",
        })
        self.assertTrue(h._check_same_origin())

    def test_forwarded_https_rejects_http_origin(self):
        h = self._make_handler_with_headers({
            "Host": "127.0.0.1:8090",
            "Origin": "http://studio.example.com",
            "X-Forwarded-Host": "studio.example.com",
            "X-Forwarded-Proto": "https",
        })
        self.assertFalse(h._check_same_origin())

    def test_loopback_forwarded_host_accepts_matching_origin(self):
        h = self._make_handler_with_headers({
            "Host": "127.0.0.1:8080",
            "X-Forwarded-Host": "mypc.local:8080",
            "Origin": "http://mypc.local:8080",
        })
        self.assertTrue(h._check_same_origin())

    def test_loopback_forwarded_host_rejects_mismatched_origin(self):
        h = self._make_handler_with_headers({
            "Host": "127.0.0.1:8080",
            "X-Forwarded-Host": "mypc.local:8080",
            "Origin": "http://evil.example.com",
        })
        self.assertFalse(h._check_same_origin())

    def test_loopback_forwarded_host_accepts_matching_referer(self):
        h = self._make_handler_with_headers({
            "Host": "localhost:8080",
            "X-Forwarded-Host": "office-pc.lan:8080",
            "Referer": "http://office-pc.lan:8080/page",
        })
        self.assertTrue(h._check_same_origin())

    def test_non_loopback_host_ignores_forwarded_host(self):
        h = self._make_handler_with_headers({
            "Host": "production.example.com",
            "X-Forwarded-Host": "attacker.com",
            "Origin": "http://attacker.com",
        })
        self.assertFalse(h._check_same_origin())


class TestLogMessage(unittest.TestCase):
    def test_log_filter(self):
        handler = _make_handler()
        handler.log_silent = False
        handler.log_filter = ["/static/"]
        # 이 호출이 에러 없이 완료되면 성공
        handler.log_message("%s", "GET /static/js/app.js")

    def test_log_silent(self):
        handler = _make_handler()
        handler.log_silent = True
        handler.log_message("%s", "GET /api/test")


class TestCommonRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.static_dir = cls.root / "static"
        cls.templates_dir = cls.root / "templates"
        cls.static_dir.mkdir()
        cls.templates_dir.mkdir()
        (cls.static_dir / "app.txt").write_text("local-static", encoding="utf-8")
        (cls.templates_dir / "index.html").write_text("<h1>Common OK</h1>", encoding="utf-8")

        class CommonRouteHandler(DXBaseHandler):
            server_name = "CommonRouteTest"
            static_dir = cls.static_dir
            templates_dir = cls.templates_dir
            log_silent = True

            def route(self):
                if self.route_common():
                    return
                if self.url_path == "/api/pilot":
                    return self.send_json({"pilot": True})
                return self.route_legacy()

        cls.handler_class = CommonRouteHandler
        cls.server = HTTPServer(("127.0.0.1", 0), CommonRouteHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.tmp.cleanup()

    def test_route_common_serves_root_template(self):
        resp = urlopen(f"http://127.0.0.1:{self.port}/")
        self.assertEqual(resp.status, 200)
        self.assertIn("Common OK", resp.read().decode())

    def test_route_common_serves_index_template(self):
        resp = urlopen(f"http://127.0.0.1:{self.port}/index.html")
        self.assertEqual(resp.status, 200)
        self.assertIn("Common OK", resp.read().decode())

    def test_route_common_serves_local_static(self):
        resp = urlopen(f"http://127.0.0.1:{self.port}/static/app.txt")
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.read().decode(), "local-static")

    def test_route_common_serves_shared_static(self):
        resp = urlopen(f"http://127.0.0.1:{self.port}/static/shared/i18n.js")
        self.assertEqual(resp.status, 200)
        self.assertIn("DXI18n", resp.read().decode())

    def test_route_common_allows_app_routes_after_common_routes(self):
        resp = urlopen(f"http://127.0.0.1:{self.port}/api/pilot")
        data = json.loads(resp.read())
        self.assertEqual(data["pilot"], True)

    def test_route_legacy_returns_404(self):
        with self.assertRaises(HTTPError) as ctx:
            urlopen(f"http://127.0.0.1:{self.port}/missing")
        self.assertEqual(ctx.exception.code, 404)


class TestIntegration(unittest.TestCase):
    """실제 HTTP 서버를 띄워서 E2E 테스트."""

    @classmethod
    def setUpClass(cls):
        class IntegrationHandler(DXBaseHandler):
            server_name = "IntegrationTest"
            log_silent = True
            _cache = {}
            _cache_lock = threading.Lock()

            def route(self):
                if self.url_path == "/":
                    return self.send_html("<h1>OK</h1>")
                if self.url_path == "/api/test":
                    return self.send_json({"status": "ok"})
                if self.url_path == "/api/error":
                    return self.send_error_json(400, "Bad request")
                self.send_error(404)

        cls.server = HTTPServer(("127.0.0.1", 0), IntegrationHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_root_html(self):
        resp = urlopen(f"http://127.0.0.1:{self.port}/")
        self.assertEqual(resp.status, 200)
        self.assertIn("text/html", resp.headers["Content-Type"])
        body = resp.read().decode()
        self.assertIn("<h1>OK</h1>", body)

    def test_api_json(self):
        resp = urlopen(f"http://127.0.0.1:{self.port}/api/test")
        self.assertEqual(resp.status, 200)
        self.assertIn("application/json", resp.headers["Content-Type"])
        data = json.loads(resp.read())
        self.assertEqual(data["status"], "ok")

    def test_api_error(self):
        try:
            urlopen(f"http://127.0.0.1:{self.port}/api/error")
        except HTTPError as e:
            self.assertEqual(e.code, 400)
            data = json.loads(e.read())
            self.assertEqual(data["error"], "Bad request")

    def test_404(self):
        try:
            urlopen(f"http://127.0.0.1:{self.port}/nonexistent")
        except HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_options_cors(self):
        req = Request(f"http://127.0.0.1:{self.port}/api/test", method="OPTIONS")
        resp = urlopen(req)
        self.assertEqual(resp.status, 204)


if __name__ == "__main__":
    unittest.main()
