import importlib.util
import json
import re
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest


ROOT = Path(__file__).resolve().parent.parent.parent


def _load_launcher_module():
    spec = importlib.util.spec_from_file_location(
        "dx_launcher_under_test",
        ROOT / "launcher" / "launcher.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_launcher_handler():
    return _load_launcher_module().LauncherHandler


def _start_launcher_server(handler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


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


@pytest.fixture(scope="module")
def launcher_server():
    LauncherHandler = _load_launcher_handler()
    server = ThreadingHTTPServer(("127.0.0.1", 0), LauncherHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def test_launcher_serves_shared_css_foundation(launcher_server):
    for path in (
        "/static/shared/dx-fonts.css",
        "/static/shared/dx-tokens.css",
        "/static/shared/dx-base.css",
        "/static/shared/dx-utilities.css",
    ):
        resp = urlopen(f"{launcher_server}{path}", timeout=5)
        body = resp.read().decode()
        assert resp.status == 200
        assert body.strip()


def test_launcher_serves_shared_font_binary(launcher_server):
    resp = urlopen(
        f"{launcher_server}/static/shared/fonts/inter-v20-latin-regular.woff2",
        timeout=5,
    )
    body = resp.read()
    assert resp.status == 200
    assert len(body) > 1000


@pytest.mark.parametrize(
    "asset_path",
    (
        "/static/shared/chat-widget.css",
        "/static/shared/chat-widget.js",
    ),
)
def test_launcher_serves_shared_chat_widget_static(launcher_server, asset_path):
    resp = urlopen(f"{launcher_server}{asset_path}", timeout=5)
    body = resp.read().decode()
    assert resp.status == 200
    assert body.strip()


@pytest.mark.parametrize(
    "asset_path",
    (
        "/static/sdk-library-data.json",
        "/static/about-data.json",
        "/static/fonts/inter-v20-latin-regular.woff2",
        "/static/img/deepx-logo.svg",
        "/static/img/about/dx-m1-die.jpg",
    ),
)
def test_launcher_serves_public_static_assets(launcher_server, asset_path):
    resp = urlopen(f"{launcher_server}{asset_path}", timeout=5)
    body = resp.read()
    assert resp.status == 200
    assert body


def test_launcher_index_references_existing_static_images():
    html = (ROOT / "launcher" / "static" / "index.html").read_text(encoding="utf-8")
    image_paths = sorted(set(
        urlsplit(match).path
        for match in re.findall(r'(?:src|href)="(/static/img/[^"]+)"', html)
    ))
    assert image_paths
    missing = []
    for image_path in image_paths:
        rel = unquote((image_path[8:] if image_path.startswith("/static/") else image_path))
        if not (ROOT / "launcher" / "static" / rel).is_file():
            missing.append(image_path)
    assert missing == []


def test_launcher_serves_general_static_images_even_with_subapp_referer(launcher_server):
    req = Request(
        f"{launcher_server}/static/img/deepx-logo.svg",
        headers={"Referer": f"{launcher_server}/app/"},
    )
    resp = urlopen(req, timeout=5)
    body = resp.read()
    assert resp.status == 200
    assert body.startswith(b"<svg")


def test_launcher_rejects_shared_static_path_traversal(launcher_server):
    traversal_path = "/static/shared/%2e%2e/%2e%2e/PROJECT_CONTEXT.md"
    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"{launcher_server}{traversal_path}", timeout=5)
    assert exc_info.value.code == 403


def test_launcher_rejects_shared_chat_widget_path_traversal(launcher_server):
    traversal_path = "/static/shared/chat-widget/%2e%2e/%2e%2e/PROJECT_CONTEXT.md"
    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"{launcher_server}{traversal_path}", timeout=5)
    assert exc_info.value.code == 403


def test_launcher_rejects_shared_chat_widget_subdirectories(launcher_server):
    nested_dir = ROOT / "shared" / "chat" / "static" / "chat-widget"
    nested_file = nested_dir / "nested.css"
    nested_dir.mkdir(exist_ok=True)
    nested_file.write_text("body { color: red; }", encoding="utf-8")
    try:
        with pytest.raises(HTTPError) as exc_info:
            urlopen(f"{launcher_server}/static/shared/chat-widget/nested.css", timeout=5)
        assert exc_info.value.code == 403
    finally:
        nested_file.unlink(missing_ok=True)
        nested_dir.rmdir()


@pytest.mark.parametrize(
    "traversal_path",
    (
        "/static/fonts/%2e%2e/%2e%2e/launcher.py",
        "/static/img/%2e%2e/%2e%2e/launcher.py",
        "/static/img/about/%2e%2e/%2e%2e/%2e%2e/launcher.py",
    ),
)
def test_launcher_rejects_public_static_path_traversal(
    launcher_server, traversal_path
):
    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"{launcher_server}{traversal_path}", timeout=5)
    assert exc_info.value.code == 403


def test_launcher_prefixed_app_chat_stays_proxied(monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        resp = urlopen(f"{base_url}/app/api/chat", timeout=5)
        data = resp.read().decode()
        assert '"proxied": true' in data
        assert calls == [{
            "target_port": module.APP_PORT,
            "path": "/api/chat",
            "inject_widget": True,
            "method": "GET",
        }]
    finally:
        server.shutdown()
        server.server_close()


def test_launcher_subapp_referer_api_chat_stays_proxied(monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/api/chat",
            data=b'{"message":"hello"}',
            headers={"Content-Type": "application/json", "Referer": f"{base_url}/app/"},
            method="POST",
        )
        resp = urlopen(req, timeout=5)
        data = resp.read().decode()
        assert '"proxied": true' in data
        assert calls == [{
            "target_port": module.APP_PORT,
            "path": "/api/chat",
            "inject_widget": True,
            "method": "POST",
        }]
    finally:
        server.shutdown()
        server.server_close()


def test_launcher_subapp_referer_static_stays_proxied(monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/static/js/app.js",
            headers={"Referer": f"{base_url}/stream/"},
            method="GET",
        )
        resp = urlopen(req, timeout=5)
        data = resp.read().decode()
        assert '"proxied": true' in data
        assert calls == [{
            "target_port": module.STREAM_PORT,
            "path": "/static/js/app.js",
            "inject_widget": True,
            "method": "GET",
        }]
    finally:
        server.shutdown()
        server.server_close()


def _read_all_launcher_js():
    """Read concatenated launcher JS source (all split modules + bootstrap)."""
    parts = []
    for name in (
        "launcher-state.js", "launcher-language.js", "launcher-splash.js",
        "platform-info.js", "launcher-app-frame.js", "launcher.js",
    ):
        parts.append((ROOT / "launcher" / "static" / name).read_text(encoding="utf-8"))
    return "\n".join(parts)


def test_launcher_launch_uses_canonical_iframe_paths():
    launcher_js = _read_all_launcher_js()
    assert "APP_PATHS" in launcher_js
    for app, path in {
        "zoo": "/zoo/",
        "planner": "/planner/",
        "dx_monitor": "/dx_monitor/",
        "benchmark": "/benchmark/",
    }.items():
        assert f"{app}: '{path}'" in launcher_js or f'{app}: "{path}"' in launcher_js
    assert "let url  = `/${app}/`;" not in launcher_js


def test_launcher_tutorial_mode_defaults_on():
    # Tutorial mode is ON by default (guided onboarding); it is off only when the user has
    # explicitly turned it off (stored 'off'). The first launcher step shows how to turn it off.
    tutorial_js = (ROOT / "launcher" / "static" / "tutorial.js").read_text(encoding="utf-8")
    assert "_stored !== 'off'" in tutorial_js
    assert "_stored === 'on'" not in tutorial_js
    assert "type: _tutorialMode ? 'dx-tutorial-start' : 'dx-tutorial-stop'" in tutorial_js
    # first step spotlights the Tutorial Mode on/off card so users know where to turn it off
    assert "#dxt-tutorial-card" in tutorial_js
    assert tutorial_js.index("target: '#dxt-tutorial-card'") < tutorial_js.index("target: '.top-bar'")


def test_launcher_index_rewrites_root_assets_with_content_hashes():
    module = _load_launcher_module()
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        resp = urlopen(f"{base_url}/", timeout=5)
        html = resp.read().decode()
    finally:
        server.shutdown()
        server.server_close()

    assert resp.headers["Cache-Control"] == "no-cache"
    for asset in (
        "/style.css", "/launcher.js", "/tutorial.js", "/about-deepx.css",
        "/about-deepx.js", "/sdk-library.css", "/sdk-library.js", "/sdk-tutorial.js",
        "/launcher-state.js", "/launcher-language.js", "/launcher-splash.js",
        "/platform-info.js", "/launcher-app-frame.js",
    ):
        assert f'{asset}?v=' in html, f"Missing content-hash for {asset}"
        assert f'{asset}?m=' not in html, f"Unexpected m= param for root asset {asset}"
    assert "v=202605" not in html


def test_launcher_shell_css_is_not_long_cached():
    module = _load_launcher_module()
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        resp = urlopen(f"{base_url}/style.css", timeout=5)
        assert resp.status == 200
        assert resp.headers["Cache-Control"] == "no-cache, must-revalidate"
    finally:
        server.shutdown()
        server.server_close()


def test_launcher_health_includes_boot_id_for_stale_tab_reload():
    frame_js = (ROOT / "launcher" / "static" / "launcher-app-frame.js").read_text(encoding="utf-8")
    assert "_maybeReloadForLauncherBoot" in frame_js
    assert "launcher_boot" in frame_js
    assert "ensureStudioReady" in frame_js
    assert "shouldPlayIntroSplash" in frame_js
    assert "showBootGate" in frame_js
    assert "studioBootGate" in frame_js
    bootstrap_js = (ROOT / "launcher" / "static" / "launcher.js").read_text(encoding="utf-8")
    assert "shouldPlayIntroSplash()" in bootstrap_js
    assert "initSplashV2()" in bootstrap_js
    # During the intro splash the boot gate is concealed (kept in the DOM) rather than
    # removed, so an early splash-skip can re-show it while the modules finish booting
    # instead of leaving a blank screen. The splash branch therefore calls
    # ensureStudioReady() with no showBootGate override.
    assert "hideStudioBootGate({ conceal: true })" in frame_js
    assert "showStudioBootGate" in frame_js
    launcher_py = (ROOT / "launcher" / "launcher.py").read_text(encoding="utf-8")
    assert '"launcher_boot": _LAUNCHER_BOOT_ID' in launcher_py
    assert '"studio_ready": _STUDIO_READY' in launcher_py
    assert "_send_shell_asset" in launcher_py
    index_html = (ROOT / "launcher" / "static" / "index.html").read_text(encoding="utf-8")
    assert 'id="studioBootGate"' in index_html
    assert 'class="launcher-boot-pending"' in index_html
    assert 'launcher-boot-critical' in index_html
    assert 'queueRouteRestore' in frame_js
    assert 'isLauncherShellBlocked' in frame_js


def test_launcher_split_assets_are_served_from_root():
    module = _load_launcher_module()
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        for asset in (
            "/launcher-state.js",
            "/launcher-language.js",
            "/launcher-splash.js",
            "/platform-info.js",
            "/launcher-app-frame.js",
        ):
            resp = urlopen(f"{base_url}{asset}", timeout=5)
            body = resp.read().decode()
            assert resp.status == 200
            assert resp.headers["Cache-Control"] == "no-cache, must-revalidate"
            assert "javascript" in resp.headers.get("Content-Type", "").lower()
            assert body.strip(), f"{asset} returned empty body"
    finally:
        server.shutdown()
        server.server_close()


def test_subapp_module_static_urls_are_cache_isolated():
    pattern = re.compile(r'(?:src|href)="(/static/(?:js|css)/[^"]+)"')
    for template in sorted((ROOT).glob("dx_*/templates/*.html")):
        module = template.parts[-3]
        html = template.read_text(encoding="utf-8")
        for url in pattern.findall(html):
            assert f"?m={module}" in url or f"&m={module}" in url, (
                f"{template.relative_to(ROOT)} uses cache-shared module asset {url}"
            )


def test_launcher_referer_proxies_benchmark_api_catalog(monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/api/catalog",
            headers={"Referer": f"{base_url}/benchmark/"},
            method="GET",
        )
        resp = urlopen(req, timeout=5)
        data = resp.read().decode()
        assert '"proxied": true' in data
        assert calls == [{
            "target_port": module.BENCHMARK_PORT,
            "path": "/api/catalog",
            "inject_widget": True,
            "method": "GET",
        }]
    finally:
        server.shutdown()
        server.server_close()


def test_launcher_no_referer_api_chat_keeps_dx_app_fallback(monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/api/chat",
            data=b'{"message":"hello"}',
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urlopen(req, timeout=5)
        data = resp.read().decode()
        assert '"proxied": true' in data
        assert calls == [{
            "target_port": module.APP_PORT,
            "path": "/api/chat",
            "inject_widget": True,
            "method": "POST",
        }]
    finally:
        server.shutdown()
        server.server_close()


def test_launcher_owned_api_chat_uses_launcher_chat_engine(tmp_path, monkeypatch):
    monkeypatch.setenv("DX_CHAT_CONFIG_DIR", str(tmp_path))
    import shared.chat.config as chat_config
    chat_config._cached_config = None
    chat_config._cached_mtime = 0.0
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/api/chat",
            data=b'{"message":"hello","lang":"en"}',
            headers={"Content-Type": "application/json", "Referer": f"{base_url}/"},
            method="POST",
        )
        resp = urlopen(req, timeout=5)
        body = resp.read().decode()
        assert resp.headers.get_content_type() == "text/event-stream"
        assert "data:" in body
        assert calls == []
    finally:
        server.shutdown()
        server.server_close()
        chat_config._cached_config = None
        chat_config._cached_mtime = 0.0


def test_launcher_referer_query_does_not_trigger_subapp_chat_proxy(tmp_path, monkeypatch):
    monkeypatch.setenv("DX_CHAT_CONFIG_DIR", str(tmp_path))
    import shared.chat.config as chat_config
    chat_config._cached_config = None
    chat_config._cached_mtime = 0.0
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/api/chat",
            data=b'{"message":"hello","lang":"en"}',
            headers={
                "Content-Type": "application/json",
                "Referer": f"{base_url}/about?next=/app",
            },
            method="POST",
        )
        resp = urlopen(req, timeout=5)
        body = resp.read().decode()
        assert resp.headers.get_content_type() == "text/event-stream"
        assert "data:" in body
        assert calls == []
    finally:
        server.shutdown()
        server.server_close()
        chat_config._cached_config = None
        chat_config._cached_mtime = 0.0


@pytest.mark.parametrize(
    ("path", "method", "body"),
    (
        ("/api/chat", "POST", b'{"message":"hello","lang":"en"}'),
        ("/api/chat/config", "GET", None),
        (
            "/api/chat/config",
            "POST",
            b'{"provider":"custom","api_key":"sk-test","model":"local"}',
        ),
        (
            "/api/chat/config/test",
            "POST",
            b'{"provider":"custom","api_key":"sk-test","model":"local"}',
        ),
    ),
)
def test_launcher_rejects_cross_origin_chat_requests(path, method, body, monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        headers = {
            "Origin": "https://evil.example",
            "Referer": "https://evil.example/app/",
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
        req = Request(
            f"{base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        with pytest.raises(HTTPError) as exc_info:
            urlopen(req, timeout=5)
        assert exc_info.value.code == 403
        assert calls == []
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.parametrize(
    ("path", "method", "body"),
    (
        ("/app/api/chat", "POST", b'{"message":"hello","lang":"en"}'),
        ("/app/api/chat/config", "GET", None),
        (
            "/compiler/api/chat/config/test",
            "POST",
            b'{"provider":"custom","api_key":"sk-test","model":"local"}',
        ),
    ),
)
def test_launcher_rejects_cross_origin_prefixed_chat_requests(path, method, body, monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        headers = {
            "Origin": "https://evil.example",
            "Referer": "https://evil.example/app/",
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
        req = Request(
            f"{base_url}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        with pytest.raises(HTTPError) as exc_info:
            urlopen(req, timeout=5)
        assert exc_info.value.code == 403
        assert calls == []
    finally:
        server.shutdown()
        server.server_close()


def test_launcher_subapp_referer_chat_config_get_stays_proxied(monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/api/chat/config",
            headers={"Referer": f"{base_url}/app/"},
            method="GET",
        )
        resp = urlopen(req, timeout=5)
        data = resp.read().decode()
        assert '"proxied": true' in data
        assert calls == [{
            "target_port": module.APP_PORT,
            "path": "/api/chat/config",
            "inject_widget": True,
            "method": "GET",
        }]
    finally:
        server.shutdown()
        server.server_close()


def test_launcher_chat_config_rejects_unsupported_methods(monkeypatch):
    module = _load_launcher_module()
    calls = _install_proxy_spy(monkeypatch, module)
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/api/chat/config",
            data=b'{}',
            headers={"Content-Type": "application/json"},
            method="PUT",
        )
        with pytest.raises(HTTPError) as exc_info:
            urlopen(req, timeout=5)
        assert exc_info.value.code == 405
        assert calls == []
    finally:
        server.shutdown()
        server.server_close()


def test_launcher_chat_config_get_includes_settings_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("DX_CHAT_CONFIG_DIR", str(tmp_path))
    import shared.chat.config as chat_config
    chat_config._cached_config = None
    chat_config._cached_mtime = 0.0
    chat_config.save_config(
        provider="custom",
        api_key="sk-test123456",
        model="local-model",
        endpoint="http://localhost:11434/v1",
        temperature=0.42,
    )

    module = _load_launcher_module()
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        resp = urlopen(f"{base_url}/api/chat/config", timeout=5)
        data = json.loads(resp.read().decode())
        assert data["configured"] is True
        assert data["provider"] == "custom"
        assert data["model"] == "local-model"
        assert data["endpoint"] == "http://localhost:11434/v1"
        assert data["temperature"] == 0.42
        assert data["api_key"] != "sk-test123456"
        assert "••••" in data["api_key"]
    finally:
        server.shutdown()
        server.server_close()
        chat_config._cached_config = None
        chat_config._cached_mtime = 0.0


@pytest.mark.parametrize("temperature", ["bad", "nan", "inf", -0.1, 2.1])
def test_launcher_chat_config_rejects_invalid_temperature(tmp_path, monkeypatch, temperature):
    monkeypatch.setenv("DX_CHAT_CONFIG_DIR", str(tmp_path))
    import shared.chat.config as chat_config
    chat_config._cached_config = None
    chat_config._cached_mtime = 0.0

    module = _load_launcher_module()
    server, base_url = _start_launcher_server(module.LauncherHandler)
    try:
        req = Request(
            f"{base_url}/api/chat/config",
            data=json.dumps({
                "provider": "custom",
                "api_key": "sk-test",
                "model": "local-model",
                "temperature": temperature,
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(HTTPError) as exc_info:
            urlopen(req, timeout=5)
        assert exc_info.value.code == 400
        body = json.loads(exc_info.value.read().decode())
        assert "temperature" in body.get("error", "").lower()
        assert not (tmp_path / "chat_config.json").exists()
    finally:
        server.shutdown()
        server.server_close()
        chat_config._cached_config = None
        chat_config._cached_mtime = 0.0


def test_sdk_doc_rejects_missing_path(launcher_server):
    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"{launcher_server}/api/sdk-doc", timeout=5)
    assert exc_info.value.code == 400


@pytest.mark.parametrize("path", ("", "/etc/passwd", "../PROJECT_CONTEXT.md", "%2e%2e/PROJECT_CONTEXT.md"))
def test_sdk_doc_rejects_invalid_paths(launcher_server, path):
    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"{launcher_server}/api/sdk-doc?path={path}", timeout=5)
    assert exc_info.value.code == 400


def test_sdk_doc_returns_404_for_unregistered_missing_path(launcher_server):
    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"{launcher_server}/api/sdk-doc?path=docs/does-not-exist.md", timeout=5)
    assert exc_info.value.code == 404


def test_sdk_doc_returns_404_for_unregistered_path(launcher_server):
    """A safe relative path not listed in sdk-library-data.json must return 404."""
    with pytest.raises(HTTPError) as exc_info:
        urlopen(f"{launcher_server}/api/sdk-doc?path=dx-ai-studio/PROJECT_CONTEXT.md", timeout=5)
    assert exc_info.value.code == 404


def test_sdk_doc_serves_allowed_text_file(launcher_server):
    resp = urlopen(f"{launcher_server}/api/sdk-doc?path=docs/source/05_FAQ_Troubleshooting_Guide.md", timeout=5)
    body = resp.read().decode("utf-8")
    assert resp.status == 200
    assert body.strip()


def test_templates_do_not_hardcode_cache_busters_for_css_js():
    """Source-level scan: CSS/JS asset versions must come from runtime content hashes."""
    css_js_url = re.compile(r'(?:src|href)="([^"]*\.(?:css|js)(?:\?[^"]*)?)"')
    violations = []
    targets = list(ROOT.glob("dx_*/templates/*.html"))
    targets.append(ROOT / "launcher" / "static" / "index.html")
    for path in sorted(targets):
        html = path.read_text(encoding="utf-8")
        for m in css_js_url.finditer(html):
            url = m.group(1)
            if re.search(r'(?:[?&])v=', url) and "{{" not in url:
                violations.append(f"{path.relative_to(ROOT)}:{url}")
    assert violations == [], (
        "Templates still contain hardcoded cache busters:\n"
        + "\n".join(violations)
    )




def _function_body(source, name):
    start = source.index(f"function {name}")
    brace_start = source.index("{", start)
    depth = 0
    for index in range(brace_start, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace_start + 1:index]
    raise AssertionError(f"function {name} body not found")


def test_launcher_router_owns_deep_link_and_history_contracts():
    source = _read_all_launcher_js()
    assert "LauncherRouter" in source
    assert "restoreFromLocation" in source
    assert "history.replaceState" in source or "replaceState" in source
    assert "history.pushState" in source or "pushState" in source
    for path in ("/about", "/sdk-library", "/stream", "/compiler", "/planner", "/benchmark", "/dx_monitor"):
        assert path in source
    assert "popstate" in source


def test_launcher_js_keeps_legacy_sdk_library_delegate():
    source = _read_all_launcher_js()
    normalized = re.sub(r"\s+", "", source)
    assert "functionshowSdkLibrary(){LauncherRouter.navigate('sdk-library');}" in normalized or \
           "functionshowSdkLibrary(){ns.LauncherRouter.navigate('sdk-library');}" in normalized


def test_launcher_app_navigation_removes_stale_loading_overlay_before_recreate():
    source = _read_all_launcher_js()
    body = _function_body(source, "_showApp")
    # _showApp must remove stale overlay before health resolution triggers new state
    assert "document.getElementById('loadingOverlay')" in body
    assert ".remove()" in body
    # Health-gated loading is delegated to renderModuleLoading
    assert "renderModuleLoading" in body or "resolveModuleHealth" in body


def test_launcher_sdk_view_uses_public_sdk_library_api_only():
    launcher_source = _read_all_launcher_js()
    sdk_source = (ROOT / "launcher" / "static" / "sdk-library.js").read_text(encoding="utf-8")
    body = _function_body(launcher_source, "_showSdk")
    assert "window.SDKLibrary" in body or "SDKLibrary" in body
    assert "SDKLibrary.init()" in body or "SDKLibrary).init()" in body
    assert "_sdkShowView" not in body
    assert "window._sdkShowView" not in sdk_source


def test_launcher_unknown_path_uses_single_home_replace():
    source = _read_all_launcher_js()
    body = _function_body(source, "restoreFromLocation")
    assert "_showHome()" in body


def test_about_and_sdk_views_do_not_own_cross_view_routing():
    about = (ROOT / "launcher" / "static" / "about-deepx.js").read_text(encoding="utf-8")
    sdk = (ROOT / "launcher" / "static" / "sdk-library.js").read_text(encoding="utf-8")
    assert "window.AboutDeepX" in about
    assert "window.SDKLibrary" in sdk
    assert "history.pushState" not in about
    assert "history.pushState" not in sdk
    assert "document.getElementById('landing')" not in sdk
    assert 'document.getElementById("landing")' not in sdk


def test_about_view_uses_dxi18n_and_retryable_error_ui():
    source = (ROOT / "launcher" / "static" / "about-deepx.js").read_text(encoding="utf-8")
    assert "DXI18n.onLangChange" in source
    assert "renderAboutError" in source
    assert "retry" in source.lower()
    assert "SUPPORTED_LANGS" in source or "zh-CN" in source
    init_pos = source.index("async function initAboutView")
    load_pos = source.index("await loadData()", init_pos)
    initialized_pos = source.index("_aboutInitialized = true", init_pos)
    assert initialized_pos > load_pos


def test_about_data_load_preserves_fetch_error_for_error_ui():
    source = (ROOT / "launcher" / "static" / "about-deepx.js").read_text(encoding="utf-8")
    body = _function_body(source, "loadData")
    assert "throw new Error('HTTP ' + r.status)" in body
    assert "return null" not in body


def test_sdk_library_is_lazy_initialized_and_i18n_aware():
    source = (ROOT / "launcher" / "static" / "sdk-library.js").read_text(encoding="utf-8")
    assert "window.SDKLibrary" in source
    assert "labelText" in source or "localizedLabel" in source
    assert "renderSdkError" in source
    assert "DOMContentLoaded', initSdkLibrary" not in source
    assert "DXI18n.onLangChange" in source



def test_stream_template_uses_shared_chart_vendor():
    """dx_stream/templates/index.html loads Chart.js from /static/shared/vendor/."""
    html = (ROOT / "dx_stream" / "templates" / "index.html").read_text(encoding="utf-8")
    assert '/static/shared/vendor/chart.umd.min.js' in html


def test_stream_template_no_old_chart_relative_path():
    """dx_stream must not use old relative chart.umd.min.js path."""
    html = (ROOT / "dx_stream" / "templates" / "index.html").read_text(encoding="utf-8")
    assert 'src="static/js/chart.umd.min.js"' not in html


def test_shared_dx_charts_exports_required_globals():
    """shared/static/dx-charts.js must contain all required chart helper globals."""
    source = (ROOT / "shared" / "static" / "dx-charts.js").read_text(encoding="utf-8")
    required = [
        "drawLineChart", "drawBarChart", "drawGauge",
        "renderWaterfall", "renderPerfCards", "renderPipelineTable",
        "renderSparkline", "renderDetSummary", "renderTaskSummary",
        "_prepareChartCanvas",
    ]
    for name in required:
        assert name in source, f"{name} not found in dx-charts.js"
        assert f"window.{name}=" in source, f"{name} is not explicitly exported on window"




def test_launcher_loads_split_scripts_in_order():
    """Split launcher JS modules must appear in index.html in correct order."""
    html = (ROOT / "launcher" / "static" / "index.html").read_text(encoding="utf-8")
    expected = [
        "/launcher-state.js",
        "/launcher-language.js",
        "/launcher-splash.js",
        "/platform-info.js",
        "/launcher-app-frame.js",
        "/launcher.js",
    ]
    positions = [html.index(src) for src in expected]
    assert positions == sorted(positions), (
        f"Scripts not in expected order: {list(zip(expected, positions))}"
    )


def test_launcher_state_module_defines_namespace():
    """launcher-state.js must define window.DXLauncher namespace."""
    source = (ROOT / "launcher" / "static" / "launcher-state.js").read_text(encoding="utf-8")
    assert "window.DXLauncher" in source


def test_launcher_split_modules_exist():
    """All split launcher JS modules must exist as files."""
    for name in (
        "launcher-state.js",
        "launcher-language.js",
        "launcher-splash.js",
        "platform-info.js",
        "launcher-app-frame.js",
    ):
        path = ROOT / "launcher" / "static" / name
        assert path.is_file(), f"Missing split module: {name}"


def test_launcher_state_contains_shared_state():
    """launcher-state.js must contain core shared state variables."""
    source = (ROOT / "launcher" / "static" / "launcher-state.js").read_text(encoding="utf-8")
    for state_name in ("_splashTimers", "_splashActive", "currentApp"):
        assert state_name in source, f"Shared state '{state_name}' missing from launcher-state.js"


def test_launcher_split_legacy_globals_preserved():
    """launcher.js must re-export inline handler globals for backward compat."""
    source = (ROOT / "launcher" / "static" / "launcher.js").read_text(encoding="utf-8")
    required_globals = [
        "openPlatformInfo", "closePlatformInfo",
        "skipSplash", "replaySplash",
        "goHome", "launch", "showAboutView", "showSdkLibrary",
    ]
    for name in required_globals:
        assert f"window.{name}" in source, (
            f"Legacy global '{name}' not re-exported in launcher.js"
        )


def test_reset_launcher_ui_blockers_preserves_active_intro_splash():
    """studio_ready route restore must not fade-out intro splash mid-animation."""
    source = (ROOT / "launcher" / "static" / "launcher-app-frame.js").read_text(encoding="utf-8")
    fn_match = re.search(
        r"function\s+resetLauncherUiBlockers\b(.*?)(\n\s*function\b|\n\s*function\s+setVisibleView\b)",
        source,
        re.DOTALL,
    )
    assert fn_match, "resetLauncherUiBlockers must exist"
    body = fn_match.group(1)
    assert "isIntroSplashPlaying" in body, (
        "resetLauncherUiBlockers must guard splash fade-out while intro splash plays"
    )
    splash_guard = re.search(
        r"function\s+isIntroSplashPlaying\b(.*?)(\n\s*function\b)",
        source,
        re.DOTALL,
    )
    assert splash_guard, "isIntroSplashPlaying must exist"
    assert "splashOverlay" in splash_guard.group(1), (
        "isIntroSplashPlaying must track splash overlay presence"
    )


def test_launcher_state_avoids_stale_primitive_legacy_aliases():
    """Primitive launcher state must not be mirrored into stale local globals."""
    source = (ROOT / "launcher" / "static" / "launcher-state.js").read_text(encoding="utf-8")
    for alias in ("var _splashActive", "var currentApp"):
        assert alias not in source, f"Stale primitive alias remains in launcher-state.js: {alias}"


def test_launcher_inline_legacy_globals_registered_only_in_bootstrap():
    """Inline handler globals should be centralized in launcher.js."""
    split_modules = [
        "launcher-language.js",
        "launcher-splash.js",
        "platform-info.js",
        "launcher-app-frame.js",
    ]
    inline_globals = [
        "skipSplash", "replaySplash",
        "goHome", "launch", "showAboutView", "showSdkLibrary",
        "openPlatformInfo", "closePlatformInfo",
    ]

    bootstrap = (ROOT / "launcher" / "static" / "launcher.js").read_text(encoding="utf-8")
    for name in inline_globals:
        assert f"window.{name} = ns.{name}" in bootstrap

    for module_name in split_modules:
        source = (ROOT / "launcher" / "static" / module_name).read_text(encoding="utf-8")
        for name in inline_globals:
            assert f"window.{name} =" not in source, (
                f"{name} legacy global should be registered only in launcher.js, not {module_name}"
            )
