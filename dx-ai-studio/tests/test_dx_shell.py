"""Structure contract for the shared App Shell (rail + top tabs).

CSS/JS/sprite are checked as source contracts without a browser; runtime
rendering is covered by the visual suite across themes and locales.
"""
from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree

import pytest

ROOT = Path(__file__).resolve().parent.parent
SHARED_STATIC = ROOT / "shared" / "static"
ICONS = SHARED_STATIC / "dx-icons.svg"
SHELL_CSS = SHARED_STATIC / "dx-shell.css"
TABS_JS = SHARED_STATIC / "dx-tabs.js"

MODULE_ICON_IDS = ("app", "stream", "zoo", "compiler", "edge", "bench", "monitor", "agent")
PAGE_ICON_IDS = (
    "setup", "models", "run", "demo", "compare", "download",
    "lab", "folder", "book", "home", "dev", "chev", "chevd", "dots",
)

SHELL_PARTS = (
    ".dx-shell",
    ".dx-shell-rail",
    ".dx-shell-body",
    ".dx-shell-header",
    ".dx-shell-tabs",
    ".dx-shell-main",
    ".dx-shell-status",
)


def _rule(css: str, selector: str) -> str:
    m = re.search(r"^\s*" + re.escape(selector) + r"\s*\{([^}]*)\}", css, re.M)
    assert m, f"{selector} rule을 못 찾았다"
    return m.group(1).replace(" ", "").replace("\n", "")


# ── Icon sprite ─────────────────────────────────────────────────
def test_icon_sprite_exists_and_parses():
    assert ICONS.is_file(), "shared/static/dx-icons.svg 가 없다"
    ElementTree.fromstring(ICONS.read_text(encoding="utf-8"))


def test_sprite_defines_every_module_and_page_icon():
    ids = set(re.findall(r'<symbol[^>]*id="([^"]+)"', ICONS.read_text(encoding="utf-8")))
    missing = [i for i in MODULE_ICON_IDS + PAGE_ICON_IDS if i not in ids]
    assert not missing, f"스프라이트에 없는 아이콘: {missing}"


def test_every_symbol_has_a_viewbox():
    """Without a viewBox, sizing through <use> silently fails."""
    for m in re.finditer(r"<symbol([^>]*)>", ICONS.read_text(encoding="utf-8")):
        sid = re.search(r'id="([^"]+)"', m.group(1))
        assert "viewBox=" in m.group(1), (
            f"symbol {sid.group(1) if sid else '?'} 에 viewBox가 없다"
        )


def test_icons_recolor_with_currentcolor():
    """A literal color would keep the icon in the old color when the theme changes."""
    text = ICONS.read_text(encoding="utf-8")
    hexes = re.findall(r"#[0-9a-fA-F]{3,8}\b", text)
    assert not hexes, f"아이콘에 리터럴 색이 있다: {sorted(set(hexes))}"
    assert "currentColor" in text


# ── shell CSS ──────────────────────────────────────────────────
def test_shell_css_defines_every_structural_part():
    css = SHELL_CSS.read_text(encoding="utf-8")
    missing = [
        p for p in SHELL_PARTS
        if not re.search(r"^\s*" + re.escape(p) + r"\s*\{", css, re.M)
    ]
    assert not missing, f"dx-shell.css에 없는 구조: {missing}"


def test_rail_is_56px_and_never_shrinks():
    body = _rule(SHELL_CSS.read_text(encoding="utf-8"), ".dx-shell-rail")
    assert "width:56px" in body, "레일 폭은 56px 고정이다"
    assert "flex-shrink:0" in body, "레일이 줄어들면 아이콘이 잘린다"


def test_shell_has_no_240px_nav_column():
    """The shared App Shell has no left nav column; one showing up means another layout leaked in."""
    assert ".dx-shell-nav" not in SHELL_CSS.read_text(encoding="utf-8")


def test_shell_uses_semantic_tokens_only():
    stripped = re.sub(r"--[\w-]+\s*:[^;}]*", "", SHELL_CSS.read_text(encoding="utf-8"))
    hexes = re.findall(r"#[0-9a-fA-F]{3,8}\b", stripped)
    assert not hexes, f"shell이 리터럴 색을 썼다: {sorted(set(hexes))}"


def test_tabs_row_never_wraps_to_a_second_line():
    """Wrapping would turn the 42px row into two lines and break the header height contract."""
    body = _rule(SHELL_CSS.read_text(encoding="utf-8"), ".dx-shell-tabs")
    assert "flex-wrap:nowrap" in body
    assert "overflow:hidden" in body


def test_no_tabs_modifier_exists_for_single_screen_modules():
    assert ".dx-shell--no-tabs" in SHELL_CSS.read_text(encoding="utf-8"), (
        "단일 화면 모듈(monitor/modelzoo/agent_dev)용 수정자가 없다"
    )


def test_active_rail_button_is_not_signalled_by_colour_alone():
    css = SHELL_CSS.read_text(encoding="utf-8")
    assert '.dx-rail-btn[aria-current="page"]::before' in css, (
        "활성 모듈을 색으로만 구분하면 색각 이상 사용자가 못 읽는다"
    )


# ── Tab overflow ───────────────────────────────────────────────
def test_tabs_js_exposes_init_and_reflow():
    js = TABS_JS.read_text(encoding="utf-8")
    assert "window.DXTabs" in js
    assert "init: init" in js
    assert "reflowAll: reflowAll" in js


def test_tabs_js_reflows_on_container_resize():
    assert "ResizeObserver" in TABS_JS.read_text(encoding="utf-8"), (
        "폭이 바뀌면 다시 계산해야 한다"
    )


def test_tabs_js_reflows_on_language_change():
    """Overflow depends on translation length, not just width — recount on every language change."""
    assert "dx-lang-applied" in TABS_JS.read_text(encoding="utf-8"), (
        "언어 변경 이벤트를 듣지 않으면 긴 번역에서 탭이 잘린다"
    )


@pytest.mark.parametrize("banned", ("text-overflow", "substring(", "slice(0,", "…"))
def test_tabs_js_never_truncates_labels(banned):
    assert banned not in TABS_JS.read_text(encoding="utf-8"), (
        f"라벨을 자르는 흔적: {banned} — 6개 언어에서 의미가 무너진다"
    )


def test_active_tab_is_always_kept_in_the_row():
    js = TABS_JS.read_text(encoding="utf-8")
    assert "aria-current" in js, "활성 탭은 드롭다운으로 밀려나면 안 된다"
    assert "activeIdx" in js
