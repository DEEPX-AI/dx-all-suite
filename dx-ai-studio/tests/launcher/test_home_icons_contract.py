"""The stage's icons and books: contracts on their shape.

Size and state are measured on screen by test_home_icons_browser.py. This file checks that the markup and
rules promise that shape.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "launcher" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
APPS = ["app", "stream", "zoo", "compiler", "benchmark", "planner", "dx_monitor", "agent"]


def _css() -> str:
    path = STATIC / "home-stage.css"
    assert path.is_file(), "launcher/static/home-stage.css 가 없다"
    return re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)


def _glyph(app: str) -> str:
    m = re.search(r'<span class="mod-tile" data-mod="' + app + r'"[^>]*>(<svg.*?</svg>)</span>', HTML, re.S)
    assert m, f"{app} 의 glyph 가 없다"
    return m.group(1)


def test_icon_size_is_one_variable():
    """72 normally, 48 in the Dock: one size variable so both states use the same rule."""
    css = _css()
    assert re.search(r"--icon:\s*72px", css)
    assert re.search(r"--icon:\s*48px", css), "Dock 크기가 없다"
    tile = re.search(r"\.stage-deck \.mod-tile\s*\{([^}]*)\}", css)
    assert tile and "var(--icon)" in tile.group(1)


def test_icon_glass_is_mixed_from_the_module_colour():
    """Module colours come from the single --mod-tint in style.css; no new hex values."""
    tile = re.search(r"\.stage-deck \.mod-tile\s*\{([^}]*)\}", _css()).group(1)
    assert "var(--mod-tint)" in tile
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", _css()), "home-stage.css 에 hex 가 생겼다"


# Tile module key → symbol in the shared sprite (same shapes as the rail and tabs).
SYMBOL = {"app": "app", "stream": "stream", "zoo": "zoo", "compiler": "compiler", "benchmark": "bench",
          "planner": "edge", "dx_monitor": "monitor", "agent": "agent"}
SPRITE = (ROOT / "shared" / "static" / "dx-icons.svg").read_text(encoding="utf-8")


@pytest.mark.parametrize("app", APPS)
def test_each_glyph_is_two_layers_of_glass(app):
    """A thin single stroke (1.7) disappears on the glass panel: a heavy stroke plus a filled face behind it.
    The glyph is a symbol in the shared sprite, and that symbol carries both layers."""
    g = _glyph(app)
    assert f'dx-icons.svg#{SYMBOL[app]}"' in g, f"{app}: sprite 를 쓰지 않는다"
    sym = re.search(r'<symbol id="' + SYMBOL[app] + r'"[^>]*>(.*?)</symbol>', SPRITE, re.S).group(1)
    assert '<g class="f"' in sym, f"{app}: 채움 층이 없다"
    assert '<g class="l"' in sym, f"{app}: 선 층이 없다"


def test_glyph_line_weight_reads_on_glass():
    css = _css()
    rule = re.search(r"\.stage-deck \.mod-glyph\s*\{([^}]*)\}", css)
    assert rule, "무대의 glyph 규칙이 없다"
    width = re.search(r"--ico-stroke:\s*([\d.]+)", rule.group(1))   # sprite strokes take their width from a variable
    assert width and float(width.group(1)) >= 2


def test_description_is_a_tooltip_not_a_second_line():
    """The description stays in the DOM (_paintFacts writes numbers there; screen readers read it). It is not visible at rest."""
    css = _css()
    rest = re.search(r"\.stage-deck \.studio-grid :is\(\.card-desc, \.orbital-port\)\s*\{([^}]*)\}", css)
    assert rest and re.search(r"opacity:\s*0\b", rest.group(1))
    assert re.search(r":is\(:hover, :focus-visible\)[^{]*:is\(\.card-desc, \.orbital-port\)\s*\{[^}]*opacity:\s*1", css)
    assert HTML.count('class="card-desc"') == 9


def test_a_module_that_is_down_is_dimmed_not_hidden():
    """Only modules confirmed down (is-down) are dimmed. Keying on 'no is-up' would dim everything before the
    first health response."""
    css = _css()
    assert re.search(r"\.orbital-card\.is-down[^{]*\{[^}]*opacity", css)
    assert not re.search(r"\.orbital-card:not\(\.is-up\)", css)
    js = (STATIC / "home-sections.js").read_text(encoding="utf-8")
    assert "classList.toggle('is-down', !alive)" in js


def test_books_have_a_cover():
    css = _css()
    cover = re.search(r"\.stage-deck \.about-book-card \.orbital-icon\s*\{([^}]*)\}", css)
    assert cover, "책 표지 규칙이 없다"
    body = cover.group(1)
    assert "56px" in body and "72px" in body
