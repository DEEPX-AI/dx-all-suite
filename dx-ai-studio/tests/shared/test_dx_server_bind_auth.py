"""Optional bind-local and API-token contracts for DXBaseHandler / DXServer."""
from __future__ import annotations

import io
import json
import os
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import MagicMock, patch

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from shared.dx_server import (  # noqa: E402
    DXBaseHandler,
    DXServer,
    _configured_api_token,
    _resolve_bind_host,
)


class _AuthProbeHandler(DXBaseHandler):
    server_name = "AuthProbe"
    log_silent = True

    def route(self):
        self.send_json({"ok": True})


class TestBindHostResolution(unittest.TestCase):
    def test_default_is_all_interfaces(self):
        env = os.environ
        for key in ("DX_BIND_LOCAL", "DX_BIND_HOST"):
            env.pop(key, None)
        self.assertIsNone(_resolve_bind_host())

    def test_bind_local_flag(self):
        with patch.dict(os.environ, {"DX_BIND_LOCAL": "1"}, clear=False):
            self.assertEqual(_resolve_bind_host(), "127.0.0.1")

    def test_explicit_bind_host(self):
        with patch.dict(os.environ, {"DX_BIND_HOST": "192.168.1.5"}, clear=False):
            self.assertEqual(_resolve_bind_host(), "192.168.1.5")


class TestApiTokenGate(unittest.TestCase):
    def test_no_token_configured_allows_request(self):
        handler = _AuthProbeHandler.__new__(_AuthProbeHandler)
        handler.headers = {}
        handler.wfile = io.BytesIO()
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("DX_API_TOKEN", None)
            self.assertFalse(handler._enforce_auth())

    def test_missing_token_rejects(self):
        handler = _AuthProbeHandler.__new__(_AuthProbeHandler)
        handler.headers = {}
        handler.wfile = io.BytesIO()
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        with patch.dict(os.environ, {"DX_API_TOKEN": "secret"}, clear=False):
            self.assertTrue(handler._enforce_auth())
        body = json.loads(handler.wfile.getvalue())
        self.assertEqual(body["error"], "Unauthorized")

    def test_bearer_token_accepts(self):
        handler = _AuthProbeHandler.__new__(_AuthProbeHandler)
        handler.headers = {"Authorization": "Bearer secret"}
        handler.wfile = io.BytesIO()
        with patch.dict(os.environ, {"DX_API_TOKEN": "secret"}, clear=False):
            self.assertFalse(handler._enforce_auth())

    def test_configured_api_token_helper(self):
        with patch.dict(os.environ, {"DX_API_TOKEN": "abc"}, clear=False):
            self.assertEqual(_configured_api_token(), "abc")


class TestLocalBindCreatesLoopbackServer(unittest.TestCase):
    def test_create_server_respects_bind_local(self):
        srv_wrapper = DXServer(_AuthProbeHandler, "BindProbe", 0)
        with patch.dict(os.environ, {"DX_BIND_LOCAL": "1"}, clear=False):
            httpd = srv_wrapper._create_server(0)
        self.addCleanup(httpd.server_close)
        host, _port = httpd.server_address
        self.assertIn(host, ("127.0.0.1", "::1"))


if __name__ == "__main__":
    unittest.main()
