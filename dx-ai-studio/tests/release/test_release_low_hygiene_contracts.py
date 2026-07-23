import re
from pathlib import Path


_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent.parent
_DX_APP_TEMPLATE = _PROJECT_ROOT / "dx_app" / "templates" / "index.html"
_DX_APP_COMPILER_JS = _PROJECT_ROOT / "dx_app" / "static" / "js" / "compiler.js"
_DX_APP_I18N_JS = _PROJECT_ROOT / "dx_app" / "static" / "js" / "i18n.js"
_DX_APP_OUTPUTS_JS = _PROJECT_ROOT / "dx_app" / "static" / "js" / "outputs.js"
_DX_APP_INFERENCE_JS = _PROJECT_ROOT / "dx_app" / "static" / "js" / "inference.js"
_DX_COMPILER_I18N_JS = _PROJECT_ROOT / "dx_compiler" / "static" / "js" / "compiler-i18n.js"
_CHAT_WIDGET_JS = _PROJECT_ROOT / "shared" / "chat" / "static" / "chat-widget.js"
_SDK_LIBRARY_JS = _PROJECT_ROOT / "launcher" / "static" / "sdk-library.js"
_LAUNCHER_PY = _PROJECT_ROOT / "launcher" / "launcher.py"


def test_dx_app_internal_iframes_do_not_grant_same_origin():
    paths = [_DX_APP_TEMPLATE]
    if _DX_APP_COMPILER_JS.is_file():
        paths.append(_DX_APP_COMPILER_JS)
    for path in paths:
        src = path.read_text(encoding="utf-8")
        assert 'allow="same-origin"' not in src, (
            f"{path.relative_to(_PROJECT_ROOT)} must not grant same-origin to "
            "internal iframe content"
        )


def test_chat_widget_launcher_prefixes_exclude_removed_sandbox_route():
    src = _CHAT_WIDGET_JS.read_text(encoding="utf-8")
    route_match = re.search(r"\.match\(\s*/\^\s*\\/\(([^)]*)\)", src)
    assert route_match, "chat-widget.js must define the launcher route prefix regex"
    prefixes = set(route_match.group(1).split("|"))
    assert "sandbox" not in prefixes


def _js_object_body(src: str, key: str) -> str:
    match = re.search(rf"{re.escape(repr(key))}\s*:\s*\{{(?P<body>.*?)\n\s*\}},", src, re.S)
    assert match, f"{key!r} entry missing"
    return match.group("body")


def test_release_brand_entries_include_spanish_translations():
    dx_app_i18n = _DX_APP_I18N_JS.read_text(encoding="utf-8")
    compiler_i18n = _DX_COMPILER_I18N_JS.read_text(encoding="utf-8")
    sdk_library = _SDK_LIBRARY_JS.read_text(encoding="utf-8")

    assert "es:" in _js_object_body(dx_app_i18n, "DX EdgeGuide")
    assert "es:" in _js_object_body(compiler_i18n, "DX Compiler")
    assert re.search(r"subtitle\s*:\s*\{[^}]*\bes\s*:", sdk_library, re.S), (
        "SDK Library brand subtitle must include an es translation"
    )


def test_outputs_view_refreshes_after_inference_completion():
    outputs_js = _DX_APP_OUTPUTS_JS.read_text(encoding="utf-8")
    inference_js = _DX_APP_INFERENCE_JS.read_text(encoding="utf-8")

    assert "function refreshOutputsIfVisible" in outputs_js
    assert "page-outputs" in outputs_js
    assert "loadOutputs()" in outputs_js
    assert inference_js.count("typeof refreshOutputsIfVisible === 'function'") >= 2
    assert re.search(
        r"renderRunResult\(res\);\s*if\(typeof refreshOutputsIfVisible === 'function'\)refreshOutputsIfVisible\(\);",
        inference_js,
        re.S,
    )
    assert re.search(
        r"function\s+contFinish\(results\).*?if\(typeof refreshOutputsIfVisible === 'function'\)refreshOutputsIfVisible\(\);",
        inference_js,
        re.S,
    )


def test_dev_only_launcher_routes_are_debug_mode_gated():
    src = _LAUNCHER_PY.read_text(encoding="utf-8")

    assert "DX_DEBUG_MODE" in src
    assert "_debug_routes_enabled" in src
    assert 'path == "/mockup" and _debug_routes_enabled()' in src
    assert 'path.startswith("/brainstorm/") and _debug_routes_enabled()' in src
