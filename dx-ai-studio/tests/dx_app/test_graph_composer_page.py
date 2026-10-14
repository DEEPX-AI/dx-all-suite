"""Graph Composer page: its place in DX App, the template regions, script/style order, and the DOM rules its scripts
follow (no innerHTML, a language hook in every script that writes text)."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "dx_app" / "templates" / "index.html"
UTILS = ROOT / "dx_app" / "static" / "js" / "utils.js"
JS = ROOT / "dx_app" / "static" / "js"
PAGE_SCRIPTS = ("graph-composer.js", "graph-palette.js", "graph-inspector.js", "graph-run.js")


def _page_html() -> str:
    html = INDEX.read_text(encoding="utf-8")
    return html[html.index('<div id="page-graph"'):html.index("<!-- ═══ PAGE: Lab")]


def test_the_tab_sits_between_modelzoo_and_lab():
    from dx_app.server import DX_APP_PAGES

    order = [page_id for page_id, _label, _icon in DX_APP_PAGES]
    assert order.index("modelzoo") + 1 == order.index("graph") == order.index("lab") - 1
    assert ("graph", "Graph Composer", "graph") in DX_APP_PAGES


def test_nav_opens_the_composer():
    src = UTILS.read_text(encoding="utf-8")
    assert "'graph'" in re.search(r"const PAGES=\[([^\]]*)\]", src).group(1)
    assert "if(page==='graph'&&window.GraphComposer)GraphComposer.open();" in src


@pytest.mark.parametrize("region", ["gc-toolbar", "gc-name", "gc-new", "gc-projects", "gc-versions", "gc-save",
                                    "gc-delete", "gc-import", "gc-import-file", "gc-export", "gc-status",
                                    "gc-validate", "gc-run", "gc-palette", "gc-search", "gc-palette-list",
                                    "gc-canvas-host", "gc-memory", "gc-inspector", "gc-inspector-body",
                                    "gc-run-panel", "gc-run-body", "gc-samples"])
def test_the_template_has_every_region(region):
    assert f'id="{region}"' in _page_html()


def test_every_visible_text_of_the_page_is_a_dictionary_key():
    from tests.dx_app.test_i18n import dict_keys

    keys = dict_keys()
    used = set(re.findall(r'data-i18n(?:-placeholder|-aria-label|-title)?="([^"]+)"', _page_html()))
    assert used and not sorted(k for k in used if k not in keys)


def test_scripts_and_styles_load_in_order():
    html = INDEX.read_text(encoding="utf-8")
    order = ["/static/js/lang-refresh.js", "/static/shared/dx-graph-core.js", "/static/shared/dx-graph-canvas.js",
             "/static/js/graph-doc.js"] + [f"/static/js/{s}" for s in PAGE_SCRIPTS] + ["/static/js/app.js"]
    positions = [html.index(s) for s in order]
    assert positions == sorted(positions)
    assert html.index("/static/shared/dx-components.css") < html.index("/static/shared/dx-graph-canvas.css")
    assert html.index("/static/css/style.css") < html.index("/static/css/graph-composer.css")


# The page scripts arrive one task at a time; each is checked as soon as it exists.
_PRESENT = [n for n in PAGE_SCRIPTS if (JS / n).is_file()]


@pytest.mark.parametrize("path", [f"dx_app/static/js/{s}" for s in ["graph-doc.js"] + _PRESENT]
                         + ["shared/static/dx-graph-canvas.js", "shared/static/dx-graph-core.js"])
def test_graph_scripts_build_the_dom_without_inner_html(path):
    assert "innerHTML" not in (ROOT / path).read_text(encoding="utf-8")


@pytest.mark.parametrize("name", _PRESENT)
def test_every_page_script_follows_a_language_change(name):
    assert "registerLangRefresher" in (JS / name).read_text(encoding="utf-8")


def test_the_toast_close_button_has_a_name():
    """The accessible-names sweep visits every tab; a toast left open by any page showed an unnamed button."""
    assert "cb.setAttribute('aria-label',T('Close'))" in UTILS.read_text(encoding="utf-8")
