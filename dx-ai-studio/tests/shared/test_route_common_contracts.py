#!/usr/bin/env python3
"""Route common source-contract and HTTP behavior tests."""

import json
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError

from shared.dx_server import DXBaseHandler

# dx-ai-studio repo root
REPO_ROOT = Path(__file__).resolve().parents[2]

# Production server files that must call route_common()
PRODUCTION_SERVERS = [
    "dx_app/server.py",
    "dx_stream/server.py",
    "dx_compiler/server.py",
    "dx_monitor/server.py",
    "dx_planner/server.py",
    "dx_benchmark/server.py",
    "dx_modelzoo/server.py",
]


class TestRouteCommonSourceContracts(unittest.TestCase):
    """Source-level contracts: production servers use route_common()."""

    def test_all_production_servers_call_route_common(self):
        for rel_path in PRODUCTION_SERVERS:
            full_path = REPO_ROOT / rel_path
            if not full_path.is_file():
                continue  # skip if module not present
            source = full_path.read_text(encoding="utf-8")
            with self.subTest(server=rel_path):
                self.assertIn(
                    "route_common()",
                    source,
                    f"{rel_path} must call route_common()",
                )

    def test_no_direct_serve_shared_static_in_production_servers(self):
        """Production servers must not directly call serve_shared_static().

        The shared implementation (shared/dx_server.py) is excluded because
        it defines and internally uses serve_shared_static().
        """
        for rel_path in PRODUCTION_SERVERS:
            full_path = REPO_ROOT / rel_path
            if not full_path.is_file():
                continue
            source = full_path.read_text(encoding="utf-8")
            with self.subTest(server=rel_path):
                self.assertNotIn(
                    "serve_shared_static(",
                    source,
                    f"{rel_path} must not directly call serve_shared_static(); use route_common() instead",
                )


class TestRouteCommonHTTPBehavior(unittest.TestCase):
    """HTTP-level tests using a minimal handler with route_common()."""

    @classmethod
    def setUpClass(cls):
        """Start a minimal HTTP server using route_common()."""

        class MinimalHandler(DXBaseHandler):
            server_name = "RouteCommonContractTest"
            static_dir = None
            templates_dir = None
            log_silent = True

            def route(self):
                if self.route_common():
                    return
                if self.url_path == "/api/health":
                    return self.send_json({"ok": True})
                self.send_error_json(404, "Not found")

        cls.handler_class = MinimalHandler
        cls.server = HTTPServer(("127.0.0.1", 0), MinimalHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def _get(self, path: str):
        return urlopen(f"http://127.0.0.1:{self.port}{path}")

    def test_shared_static_serves_existing_file(self):
        """GET /static/shared/vendor/chart.umd.min.js returns 200."""
        resp = self._get("/static/shared/vendor/chart.umd.min.js")
        self.assertEqual(resp.status, 200)
        body = resp.read()
        self.assertGreater(len(body), 0)

    def test_shared_static_serves_i18n(self):
        """GET /static/shared/i18n.js returns shared i18n module."""
        resp = self._get("/static/shared/i18n.js")
        self.assertEqual(resp.status, 200)
        content = resp.read().decode("utf-8", errors="replace")
        self.assertIn("DXI18n", content)

    def test_chat_widget_fallback_path(self):
        """GET /static/shared/<chat-static-file> falls back to chat/static/."""
        # shared/chat/static/ should have files; try common widget assets
        chat_static = REPO_ROOT / "shared" / "chat" / "static"
        if not chat_static.is_dir():
            self.skipTest("shared/chat/static/ does not exist")
        # Find any file in chat/static for testing
        chat_files = [f for f in chat_static.iterdir() if f.is_file()]
        if not chat_files:
            self.skipTest("No files in shared/chat/static/")
        target = chat_files[0].name
        # Ensure it doesn't exist in shared/static/ (true fallback)
        shared_static = REPO_ROOT / "shared" / "static"
        if (shared_static / target).is_file():
            self.skipTest(f"{target} exists in both dirs, not a true fallback test")
        resp = self._get(f"/static/shared/{target}")
        self.assertEqual(resp.status, 200)

    def test_shared_static_404_for_missing_file(self):
        """GET /static/shared/nonexistent_xyz.js returns 404."""
        with self.assertRaises(HTTPError) as ctx:
            self._get("/static/shared/nonexistent_xyz_404.js")
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
