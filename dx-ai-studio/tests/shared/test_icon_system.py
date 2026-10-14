"""The studio's single icon set.

Every icon is a symbol in `shared/static/dx-icons.svg`, drawn in the same two layers as home's module glyphs (24
grid, a light fill + a 2px stroke), colored only with currentColor. Outside CSS cannot reach into a `<use>` shadow
tree, so the look changes only through inherited CSS variables (--ico-fill, --ico-fill-o, --ico-stroke).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPRITE = (ROOT / "shared" / "static" / "dx-icons.svg").read_text(encoding="utf-8")
COMPONENTS = (ROOT / "shared" / "static" / "dx-components.css").read_text(encoding="utf-8")

MODULES = ["app", "stream", "zoo", "compiler", "edge", "bench", "monitor", "agent"]
EXISTING = MODULES + ["home", "setup", "models", "run", "demo", "compare", "download", "lab", "folder",
                      "book", "dev", "chev", "chevd", "dots", "dashboard", "puzzle", "wrench"]
NEW = ["library", "globe", "theme", "graduation", "gear", "check", "alert", "x", "info", "spinner", "lock",
       "trash", "chat", "send", "play", "stop", "refresh", "search", "upload", "image", "video", "camera",
       "file", "clipboard", "copy", "eye", "external"]
# Marks that read from the stroke alone; a fill would only blur them.
MARKS = {"chev", "chevd", "dots", "check", "x", "external", "send", "refresh", "spinner", "search", "circle", "menu", "plus", "minus"}
DOCUMENTS = [
    "launcher/static/index.html",
    "dx_app/templates/index.html",
    "dx_stream/templates/index.html",
    "dx_modelzoo/templates/index.html",
    "dx_compiler/templates/base.html",
    "dx_benchmark/templates/index.html",
    "dx_planner/templates/index.html",
    "dx_monitor/templates/index.html",
    "dx_agent_dev/templates/index.html",
]


def _symbols() -> dict[str, str]:
    return {m.group(1): m.group(0) for m in re.finditer(r'<symbol id="([^"]+)"[^>]*>.*?</symbol>', SPRITE, re.S)}


def test_the_graph_composer_icons_are_there():
    """The Graph Composer tab and the shared graph canvas toolbar (scripts/build_icon_sprite.py)."""
    symbols = _symbols()
    for name in ("graph", "undo", "redo", "fit"):
        assert name in symbols, name
        assert 'viewBox="0 0 24 24"' in symbols[name] and '<g class="l"' in symbols[name]
    assert '<g class="f"' in symbols["graph"], "the graph glyph has the faint fill like the other glyphs"


LOGIC_OPS = ("filter", "zone", "line", "count", "dwell", "condition", "gallery", "user")


def test_every_logic_block_has_its_glyph():
    """The Graph Composer's logic blocks: palette items and canvas nodes draw logic-<op> (graph-doc.js decorate)."""
    symbols = _symbols()
    for op in LOGIC_OPS:
        sym = symbols.get(f"logic-{op}")
        assert sym, op
        assert 'viewBox="0 0 24 24"' in sym and '<g class="l"' in sym and '<g class="f"' in sym, op


def test_every_name_the_studio_uses_is_there():
    missing = [n for n in EXISTING + NEW if n not in _symbols()]
    assert not missing, missing


@pytest.mark.parametrize("name", EXISTING + NEW)
def test_each_symbol_is_the_home_glyph_style(name):
    sym = _symbols()[name]
    assert 'viewBox="0 0 24 24"' in sym, f"{name}: 24 격자가 아니다"
    assert '<g class="l"' in sym, f"{name}: 선 층이 없다"
    if name not in MARKS:
        assert '<g class="f"' in sym, f"{name}: 면 층이 없다"


def test_the_layers_take_their_shape_from_inherited_variables():
    line = re.search(r'<g class="l" style="([^"]+)"', SPRITE).group(1)
    fill = re.search(r'<g class="f" style="([^"]+)"', SPRITE).group(1)
    assert "stroke: currentColor" in line and "var(--ico-stroke" in line
    assert "fill: currentColor" in fill and "var(--ico-fill" in fill and "var(--ico-fill-o" in fill


def test_the_sprite_names_no_colour_of_its_own():
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b", SPRITE)
    assert not re.search(r'(fill|stroke)="(?!none|currentColor)[^"]+"', SPRITE)


def test_the_module_glyphs_are_the_home_ones():
    """A module looks the same in the rail, the tabs and home (24 grid, two layers)."""
    app = _symbols()["app"]
    assert 'd="M10.5 8.2v4.6l4-2.3z"' in app, "home 의 App glyph 가 아니다"


def test_the_icon_class_is_shared():
    rule = re.search(r"\.dx-ico\s*\{([^}]*)\}", COMPONENTS)
    assert rule and "width: 1em" in rule.group(1) and "height: 1em" in rule.group(1)


@pytest.mark.parametrize("doc", DOCUMENTS)
def test_every_document_loads_the_helper_before_the_toolbar(doc):
    html = (ROOT / doc).read_text(encoding="utf-8")
    assert "/static/shared/dx-icon.js" in html, doc
    assert html.index("/static/shared/dx-icon.js") < html.index("/static/shared/toolbar.js"), doc


def test_the_helper_hides_decoration_and_names_meaning():
    js = (ROOT / "shared" / "static" / "dx-icon.js").read_text(encoding="utf-8")
    assert "window.DXIcon" in js
    assert "aria-hidden" in js and "role" in js and "aria-label" in js
    # Hashed URL from <meta name="dx-icons">, else the unhashed path (test_the_helper_takes_the_hashed_sprite_url_from_the_page)
    assert "'/static/shared/dx-icons.svg'" in js


def test_the_home_uses_the_sprite_for_its_glyphs():
    html = (ROOT / "launcher" / "static" / "index.html").read_text(encoding="utf-8")
    for key in ["app", "stream", "zoo", "compiler", "edge", "bench", "monitor", "agent", "library", "book"]:
        assert f'<use href="/static/shared/dx-icons.svg#{key}"' in html, key
    assert 'class="g-fill"' not in html, "인라인 glyph 가 남아 있다"


FAVICONS = {
    "launcher/static/index.html": "launcher", "dx_app/templates/index.html": "dx_app",
    "dx_stream/templates/index.html": "dx_stream", "dx_modelzoo/templates/index.html": "dx_modelzoo",
    "dx_compiler/templates/base.html": "dx_compiler", "dx_benchmark/templates/index.html": "dx_benchmark",
    "dx_planner/templates/index.html": "dx_planner", "dx_monitor/templates/index.html": "dx_monitor",
    "dx_agent_dev/templates/index.html": "dx_agent_dev",
}


@pytest.mark.parametrize("doc,mod", sorted(FAVICONS.items()))
def test_every_module_tab_shows_its_glyph(doc, mod):
    """Tab icons (favicons) come from the same set, not emoji data-URIs or the browser default.
    scripts/build_icon_sprite.py draws each module glyph on a dark tile into shared/static/favicons/."""
    html = (ROOT / doc).read_text(encoding="utf-8")
    assert f'<link rel="icon" type="image/svg+xml" href="/static/shared/favicons/{mod}.svg">' in html
    assert "data:image/svg+xml" not in html.split("</head>")[0], "이모지 data-URI favicon 이 남아 있다"
    svg = (ROOT / "shared" / "static" / "favicons" / f"{mod}.svg").read_text(encoding="utf-8")
    assert svg.startswith("<svg") and 'viewBox="0 0 32 32"' in svg


def test_the_helper_takes_the_hashed_sprite_url_from_the_page():
    """The server announces the hashed sprite URL in <meta name="dx-icons">.
    <use> and DXIcon.load() must use the same URL so the sprite is a single cache entry."""
    js = (ROOT / "shared" / "static" / "dx-icon.js").read_text(encoding="utf-8")
    assert 'meta[name="dx-icons"]' in js
    assert "DXIcon.url = " in js


def test_no_script_spells_the_sprite_path_itself():
    """Spelling the sprite path directly fetches it again under the unhashed URL; use DXIcon.url()."""
    offenders = []
    for base in [ROOT / "shared", *sorted(ROOT.glob("*/static"))]:
        for p in base.rglob("*.js"):
            if p.name == "dx-icon.js" or "vendor" in p.parts or "node_modules" in p.parts:
                continue
            if "dx-icons.svg#" in p.read_text(encoding="utf-8", errors="ignore"):
                offenders.append(p.relative_to(ROOT).as_posix())
    assert offenders == []
