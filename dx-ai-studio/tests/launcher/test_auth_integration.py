"""런처 no-auth 로컬 모드 통합 테스트.

인증 게이트가 제거된 런처의 동작을 검증한다.
"""
import json
import os
import sys
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

import pytest

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

os.environ.pop("DX_AUTH_ENABLED", None)
os.environ.pop("DX_AUTH_STATE_FILE", None)

import launcher.launcher as lmod



def _get(base, path, headers=None):
    req = urllib.request.Request(f"{base}{path}", headers=headers or {})
    return urllib.request.urlopen(req, timeout=5)


def _post(base, path, data=None, headers=None):
    body = json.dumps(data).encode() if data else b""
    hdrs = {"Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(f"{base}{path}", data=body, headers=hdrs, method="POST")
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



class TestLauncherShutdown:
    def test_signal_shutdown_does_not_call_blocking_http_shutdown(self, monkeypatch):
        calls = []

        class FakeServer:
            def __init__(self):
                self.shutdown_called = False
                self.server_close_called = False

            def shutdown(self):
                self.shutdown_called = True
                raise AssertionError("shutdown() deadlocks when called from the signal thread")

            def server_close(self):
                self.server_close_called = True

        def fake_exit(code):
            calls.append(("exit", code))
            raise SystemExit(code)

        monkeypatch.setattr(lmod, "stop_all", lambda: calls.append(("stop_all", None)))
        server = FakeServer()

        with pytest.raises(SystemExit) as excinfo:
            lmod._shutdown_launcher_server(server, exit_fn=fake_exit)

        assert excinfo.value.code == 0
        assert calls == [("stop_all", None), ("exit", 0)]
        assert server.server_close_called is True
        assert server.shutdown_called is False

    def test_signal_shutdown_closes_server_even_when_stop_all_fails(self, monkeypatch):
        calls = []

        class FakeServer:
            def __init__(self):
                self.server_close_called = False

            def server_close(self):
                calls.append(("server_close", None))
                self.server_close_called = True

        def fail_stop_all():
            calls.append(("stop_all", None))
            raise RuntimeError("cleanup failed")

        def fake_exit(code):
            calls.append(("exit", code))
            raise SystemExit(code)

        monkeypatch.setattr(lmod, "stop_all", fail_stop_all)
        server = FakeServer()

        with pytest.raises(SystemExit) as excinfo:
            lmod._shutdown_launcher_server(server, exit_fn=fake_exit)

        assert excinfo.value.code == 0
        assert calls == [("stop_all", None), ("server_close", None), ("exit", 0)]
        assert server.server_close_called is True

    def test_signal_shutdown_exits_even_when_server_close_fails(self, monkeypatch):
        calls = []

        class FakeServer:
            def server_close(self):
                calls.append(("server_close", None))
                raise RuntimeError("close failed")

        def fake_exit(code):
            calls.append(("exit", code))
            raise SystemExit(code)

        monkeypatch.setattr(lmod, "stop_all", lambda: calls.append(("stop_all", None)))

        with pytest.raises(SystemExit) as excinfo:
            lmod._shutdown_launcher_server(FakeServer(), exit_fn=fake_exit)

        assert excinfo.value.code == 0
        assert calls == [("stop_all", None), ("server_close", None), ("exit", 0)]



class TestNoAuthLocalMode:
    def test_status_reports_auth_disabled_and_unlocked(self, live_server):
        resp = _get(live_server["base"], "/api/auth/status")
        data = json.loads(resp.read())

        assert resp.status == 200
        assert data == {
            "ok": True,
            "auth_enabled": False,
            "locked": False,
            "authenticated": True,
        }

    def test_unlock_is_noop_and_does_not_set_cookie(self, live_server):
        resp = _post(live_server["base"], "/api/auth/unlock", {"pin": "anything"})
        data = json.loads(resp.read())

        assert resp.status == 200
        assert data == {"ok": True, "auth_enabled": False, "csrf": ""}
        assert resp.headers.get("Set-Cookie") is None

    def test_logout_and_relock_are_noop_no_content(self, live_server):
        for path in ("/api/auth/logout", "/api/auth/relock"):
            resp = _post(live_server["base"], path, {})
            assert resp.status == 204
            assert resp.read() == b""
            assert resp.headers.get("Set-Cookie") is None

    def test_shell_html_has_no_auth_modal(self, live_server):
        resp = _get(live_server["base"], "/index.html", headers={"Accept": "text/html"})
        html = resp.read().decode()

        assert resp.status == 200
        assert "dxAuthModal" not in html
        assert "Startup PIN" not in html

    def test_deep_link_serves_shell_without_auth_modal(self, live_server):
        with mock.patch.object(lmod, "_proxy") as mock_proxy:
            resp = _get(
                live_server["base"],
                "/app/some/deep/link",
                headers={"Accept": "text/html", "Sec-Fetch-Dest": "document"},
            )
            html = resp.read().decode()

        assert resp.status == 200
        assert "dxAuthModal" not in html
        mock_proxy.assert_not_called()
