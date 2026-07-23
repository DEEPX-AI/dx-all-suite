"""Tests for launcher router deep-link / F5-reload behaviour.

Top-level browser navigations (Sec-Fetch-Dest: document) to sub-app prefixes
must serve the launcher shell so the JS router can restore the correct view.
Iframe loads and API/static/resource requests must still proxy to modules.
"""

import importlib.util
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent


def _load_launcher_module():
    spec = importlib.util.spec_from_file_location(
        "dx_launcher_deeplink_test",
        ROOT / "launcher" / "launcher.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _install_proxy_spy(monkeypatch, module):
    calls = []

    def fake_proxy(handler, target_port, path, inject_widget=True):
        calls.append({
            "target_port": target_port,
            "path": path,
            "inject_widget": inject_widget,
            "method": handler.command,
        })
        handler.send_json({
            "proxied": True,
            "target_port": target_port,
            "path": path,
            "inject_widget": inject_widget,
        })

    monkeypatch.setattr(module, "_proxy", fake_proxy)
    return calls


def _start_launcher_server(handler_cls):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"



_BROWSER_NAV_HEADERS = {
    "Accept": "text/html,application/xhtml+xml",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
}


def _assert_launcher_shell(body):
    """Assert the response body is the launcher shell with LauncherRouter bootstrap."""
    assert 'id="appFrame"' in body, "LauncherRouter shell must contain appFrame container"
    assert 'src="/launcher-app-frame.js' in body, (
        "LauncherRouter shell must load router bootstrap script launcher-app-frame.js"
    )
    assert 'src="/launcher.js' in body, (
        "LauncherRouter shell must load router bootstrap script launcher.js"
    )



@pytest.mark.parametrize("subapp_path", [
    "/stream/",
    "/app/",
    "/zoo/model/resnet50?tab=demo",
    "/compiler/",
    "/planner/",
    "/benchmark/",
    "/dx_monitor/",
])
def test_top_level_subapp_html_navigation_serves_launcher_index(monkeypatch, subapp_path):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}{subapp_path}",
            headers=_BROWSER_NAV_HEADERS,
        )
        resp = urlopen(req, timeout=5)
        body = resp.read().decode("utf-8")
        assert resp.status == 200
        _assert_launcher_shell(body)
        assert calls == [], f"Should NOT proxy for top-level nav to {subapp_path}"
    finally:
        server.shutdown()
        server.server_close()



def test_iframe_document_request_stays_proxied(monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/stream/",
            headers={
                "Accept": "text/html,application/xhtml+xml",
                "Sec-Fetch-Dest": "iframe",
                "Sec-Fetch-Mode": "navigate",
                "Referer": f"{base_url}/",
            },
        )
        resp = urlopen(req, timeout=5)
        assert resp.status == 200
        assert calls == [{
            "target_port": module.STREAM_PORT,
            "path": "/",
            "inject_widget": True,
            "method": "GET",
        }]
    finally:
        server.shutdown()
        server.server_close()


def test_static_js_request_stays_proxied(monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/stream/static/js/app.js",
            headers={
                "Accept": "*/*",
                "Sec-Fetch-Dest": "script",
                "Sec-Fetch-Mode": "no-cors",
            },
        )
        resp = urlopen(req, timeout=5)
        assert resp.status == 200
        assert len(calls) == 1
        assert calls[0]["target_port"] == module.STREAM_PORT
        assert calls[0]["path"] == "/static/js/app.js"
    finally:
        server.shutdown()
        server.server_close()


def test_api_status_request_stays_proxied(monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/stream/api/status",
            headers={
                "Accept": "application/json",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
            },
        )
        resp = urlopen(req, timeout=5)
        assert resp.status == 200
        assert len(calls) == 1
        assert calls[0]["target_port"] == module.STREAM_PORT
        assert calls[0]["path"] == "/api/status"
    finally:
        server.shutdown()
        server.server_close()


def test_post_api_request_stays_proxied(monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/app/api/chat",
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Referer": f"{base_url}/app/",
            },
            data=b'{"message":"hello"}',
        )
        resp = urlopen(req, timeout=5)
        assert resp.status == 200
        assert len(calls) == 1
        assert calls[0]["target_port"] == module.APP_PORT
        assert calls[0]["path"] == "/api/chat"
        assert calls[0]["method"] == "POST"
    finally:
        server.shutdown()
        server.server_close()




def test_subapp_referer_navigation_stays_proxied(monkeypatch):
    """GET /stream/ with browser-nav headers + subapp Referer must proxy, not shell."""
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/stream/",
            headers={
                **_BROWSER_NAV_HEADERS,
                "Referer": f"{base_url}/stream/",
            },
        )
        resp = urlopen(req, timeout=5)
        assert resp.status == 200
        assert calls == [{
            "target_port": module.STREAM_PORT,
            "path": "/",
            "inject_widget": True,
            "method": "GET",
        }]
    finally:
        server.shutdown()
        server.server_close()




def test_sdk_library_with_query_params_serves_launcher_shell(monkeypatch):
    """Top-level browser nav to /sdk-library?doc=<encoded>&q=<encoded>&view=list
    must serve launcher shell, NOT proxy to any module."""
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/sdk-library?doc=%2Fapi%2Fconv2d&q=convolution&view=list",
            headers=_BROWSER_NAV_HEADERS,
        )
        resp = urlopen(req, timeout=5)
        body = resp.read().decode("utf-8")
        assert resp.status == 200
        _assert_launcher_shell(body)
        assert calls == [], "SDK library direct entry must NOT proxy"
    finally:
        server.shutdown()
        server.server_close()



def test_unknown_top_level_html_navigation_serves_launcher_shell(monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/not-a-real-page",
            headers={
                "Accept": "text/html",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
            },
        )
        resp = urlopen(req, timeout=5)
        body = resp.read().decode("utf-8")
        assert resp.status == 200
        _assert_launcher_shell(body)
        assert 'id="landing"' in body
        assert calls == []
    finally:
        server.shutdown()
        server.server_close()
