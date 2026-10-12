"""shell markup helpers, so the eight modules do not each copy the rail/header HTML."""
from __future__ import annotations

import re

import pytest

from shared.shell import MODULES, render_header, render_rail, render_tabs


def test_modules_registry_lists_all_eight_in_hub_order():
    assert [m.key for m in MODULES] == [
        "app", "stream", "zoo", "compiler", "edge", "bench", "monitor", "agent",
    ]


@pytest.mark.parametrize("m", MODULES, ids=[m.key for m in MODULES])
def test_every_module_has_an_icon_and_an_absolute_path(m):
    assert m.icon, f"{m.key} 아이콘 누락"
    assert m.path.startswith("/") and m.path.endswith("/"), f"{m.key} 경로 형식"
    assert m.name, f"{m.key} 표시 이름 누락"


def test_rail_marks_the_active_module_only_once():
    html = render_rail("app")
    assert html.count('aria-current="page"') == 1
    assert 'href="/app/"' in html


def test_rail_renders_all_modules_plus_a_hub_link():
    html = render_rail("bench")
    for m in MODULES:
        assert f"#{m.icon}" in html, f"{m.key} 아이콘 <use> 누락"
    assert "#home" in html, "허브 복귀 버튼이 없다"
    assert 'href="/"' in html


def test_rail_rejects_an_unknown_module():
    with pytest.raises(ValueError, match="unknown module"):
        render_rail("nope")


def test_header_carries_brand_page_name_and_toolbar_slot():
    html = render_header("DX App", "Run Inference")
    assert 'id="dxBrand"' in html, "brand.js가 마운트할 자리가 필요하다"
    assert 'class="dx-brand-slot"' in html
    assert "Run Inference" in html
    assert "toolbar" in html.split('class="dx-shell-header-right ')[1][:20], (
        "DXToolbar.init({container:'.toolbar'})가 붙을 자리가 필요하다"
    )
    assert 'id="dxShellPage"' in html, "nav()가 페이지명을 갱신할 훅이 필요하다"


def test_header_does_not_print_the_module_name_twice():
    """brand.js inserts the name, so a header that also prints it shows it twice."""
    html = render_header("DX App", "Run Inference")
    assert html.count("DX App") == 1, "aria-label 한 번만 나와야 한다"
    assert 'aria-label="DX App"' in html


def test_header_escapes_untrusted_page_titles():
    html = render_header("DX App", '<img src=x onerror="alert(1)">')
    assert "<img" not in html
    assert "&lt;img" in html


def test_tabs_marks_the_active_page_and_uses_i18n_keys():
    html = render_tabs(
        [("setup", "Setup", "setup"), ("run", "Run Inference", "run")], active="run"
    )
    assert html.count('aria-current="page"') == 1
    assert 'data-i18n="Run Inference"' in html, "라벨은 사전 키로 나가야 한다"
    assert 'data-page="run"' in html
    assert 'data-page="setup"' in html


def test_tabs_returns_empty_for_single_screen_modules():
    assert render_tabs([], active=None) == ""


def test_tabs_with_no_match_marks_nothing_active():
    html = render_tabs([("setup", "Setup", "setup")], active="nope")
    assert "aria-current" not in html


def test_rendered_markup_has_no_emoji():
    """Emoji render differently per OS and cannot be sized or coloured."""
    html = (
        render_rail("app")
        + render_header("DX App", "Run")
        + render_tabs([("setup", "Setup", "setup")], active="setup")
    )
    found = re.findall(r"[\U0001F300-\U0001FAFF]", html)
    assert not found, f"shell 마크업에 이모지가 있다: {found}"


def test_rendered_markup_references_only_sprite_icons():
    """Inline paths scattered around would let the icons drift apart again."""
    html = render_rail("app") + render_header("DX App", "Run")
    assert "<path" not in html
    assert html.count("/static/shared/dx-icons.svg#") == html.count("<use ")
