"""Theme toggle contract, checked as source contracts without a browser
(runtime behavior is covered by the visual suite's per-theme baselines)."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
THEME_JS = ROOT / "shared" / "static" / "dx-theme.js"
TOOLBAR_JS = ROOT / "shared" / "static" / "toolbar.js"

SURFACES = (
    "dx_app/templates/index.html",
    "dx_stream/templates/index.html",
    "dx_benchmark/templates/index.html",
    "dx_monitor/templates/index.html",
    "dx_modelzoo/templates/index.html",
    "dx_planner/templates/index.html",
    "dx_compiler/templates/base.html",
    "dx_agent_dev/templates/index.html",
    "launcher/static/index.html",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_theme_js_exposes_the_documented_api():
    js = read(THEME_JS)
    for symbol in ("window.DXTheme", "setTheme", "getTheme", "resolved", "cycle",
                   "onThemeChange"):
        assert symbol in js, f"DXTheme API에 {symbol} 가 없다"


def test_theme_js_persists_under_the_shared_storage_key():
    js = read(THEME_JS)
    assert "'dx-theme'" in js, "언어(dx-lang)와 같은 규약의 저장 키를 써야 한다"
    assert "localStorage" in js


def test_theme_js_supports_system_as_a_real_third_state():
    js = read(THEME_JS)
    assert "'system'" in js, "system은 dark/light와 별개의 상태다"
    assert "removeAttribute('data-theme')" in js, (
        "system일 때 data-theme를 지워야 prefers-color-scheme가 동작한다"
    )


def test_theme_js_reacts_to_os_theme_changes_while_on_system():
    js = read(THEME_JS)
    assert "matchMedia" in js
    assert "prefers-color-scheme" in js


def test_theme_js_syncs_across_the_launcher_iframe_boundary():
    js = read(THEME_JS)
    assert "postMessage" in js
    assert "dx-theme-change" in js, "언어 동기화(dx-lang-change)와 같은 메시지 규약"


def test_incoming_theme_messages_do_not_echo_back():
    """If parent and child re-broadcast each other's messages, they echo forever."""
    js = read(THEME_JS)
    m = re.search(r"'dx-theme-change'\)\s*return;(.*?)\}\);", js, re.S)
    assert m, "message 핸들러를 못 찾았다"
    assert "silent: true" in m.group(1), "수신 시 silent로 적용해야 한다"


def test_theme_js_applies_before_paint_to_avoid_a_flash():
    js = read(THEME_JS)
    assert re.search(r"^\s*_apply\(_theme\);", js, re.M), (
        "모듈 로드 시점에 즉시 적용해야 첫 프레임이 깜빡이지 않는다"
    )


def test_toolbar_builds_a_theme_button():
    js = read(TOOLBAR_JS)
    assert "dxToolbarTheme" in js, "toolbar에 테마 버튼이 없다"
    assert "DXTheme.cycle()" in js, "toolbar가 DXTheme.cycle을 호출하지 않는다"
    assert "DXTheme.onThemeChange" in js, (
        "다른 서피스에서 테마가 바뀌면 버튼 글리프도 따라가야 한다"
    )


def test_theme_button_glyphs_are_monochrome_not_emoji():
    """Emoji render differently per OS and jump in size in a 36px button, and symbol glyphs such as
    the half circle (U+25D2) can render as "-" headless — the three states are shared sprite icon names."""
    js = read(TOOLBAR_JS)
    m = re.search(r"THEME_ICON = \{([^}]*)\}", js)
    assert m, "THEME_ICON 을 못 찾았다"
    assert re.findall(r"'([a-z]+)'", m.group(1)) == ["moon", "sun", "theme"], m.group(1)


@pytest.mark.parametrize("rel", SURFACES)
def test_every_surface_loads_theme_js_inside_head(rel):
    html = read(ROOT / rel)
    assert html.count('src="/static/shared/dx-theme.js"') == 1, f"{rel}"
    assert html.index('src="/static/shared/dx-theme.js"') < html.index("</head>"), (
        f"{rel}: dx-theme.js가 </head> 뒤에 있으면 첫 페인트가 깜빡인다"
    )


@pytest.mark.parametrize("rel", SURFACES)
def test_theme_js_loads_after_the_theme_stylesheets(rel):
    html = read(ROOT / rel)
    assert html.index("dx-theme-light.css") < html.index("dx-theme.js"), f"{rel}"
