"""SDK Library viewer: every image loads and every link either goes somewhere in the viewer or is plain text.

Found by opening all 181 library docs in a browser:
- `image.png#only-light` / `#only-dark` (MkDocs Material) went into the image path, so the DX All Suite
  architecture figure was a broken image.
- `[x](#section)` opened the Studio again in a new tab instead of scrolling the doc.
- `[x](other.md#section)` opened the doc at the top.
- `<a href="./x/README.md">` written as HTML (showcase index) opened a 404 in a new tab.
- A link to an md the library does not list (it shows only the docs users need) or a file that is not a doc
  (.py, .sh, LICENSE) looked like a link and did nothing or opened a 404.
"""
from __future__ import annotations

import base64
import json
from urllib.parse import parse_qs, urlparse

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")

LIB = {"drawers": [{"id": "d", "title": "Docs", "color": "blue", "sections": [{"id": "s", "title": "S", "files": [
    {"path": "docs/arch.md", "title": "Architecture", "type": "md"},
    {"path": "docs/guide.md", "title": "Guide", "type": "md"},
    {"path": "showcase/README.md", "title": "Showcase", "type": "md"},
    {"path": "showcase/game/README.md", "title": "Game", "type": "md"},
    {"path": "docs/code.md", "title": "Code", "type": "md"},
]}]}]}

FILLER = "\n\n".join(f"Paragraph {i} " + "text " * 60 for i in range(30))

DOCS = {
    "docs/arch.md": (
        "# Architecture\n\n"
        "![](./resources/full.png#only-light)\n![](./resources/full-dark.png#only-dark)\n\n"
        "Jump to [the runtime](#model-runtime-environment) or read the [guide setup](guide.md#first-setup).\n\n"
        f"{FILLER}\n\n## Model Runtime Environment\n\nRuntime text.\n\n{FILLER}\n\n"
        "See [internal notes](../internal/NOTES.md), [the build script](../build.sh) and [License](../LICENSE).\n"
    ),
    "docs/guide.md": (f"# Guide\n\nGo to [the composer](#graph-composer).\n\n{FILLER}\n\n## First Setup\n\nSetup text.\n\n"
                      f"{FILLER}\n\n## Graph Composer {{#graph-composer}}\n\nComposer text.\n\n{FILLER}\n"),
    "showcase/README.md": (
        "# Showcase\n\n"
        '<a href="./game/README.md"><img src="./game/demo.png" height="40"></a>\n\n'
        "Plain text after.\n"
    ),
    "showcase/game/README.md": "# Game\n\nThe game.\n",
    "docs/code.md": ("# Code\n\n- `<variant>_sync.cpp`: one variant\n\n"
                     "Include `<dxrt/dxrt_api.h>`, run `--lang <lang>`, write `**x**` or `[a](b.md)` literally.\n"),
}
IMAGES = {"docs/resources/full.png", "docs/resources/full-dark.png", "showcase/game/demo.png"}


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


@pytest.fixture()
def viewer(browser):
    server, port = start_module_server("launcher")
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script(
        "try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-tutorial-launcher-autostarted','1');localStorage.setItem('dx-lang','en');"
        "localStorage.setItem('dx-tutorial-mode','off');}catch(e){}")
    page = ctx.new_page()
    page.route("**/api/sdk-library*", lambda r: r.fulfill(
        status=200, content_type="application/json", body=json.dumps(LIB)))

    def doc(route):
        p = parse_qs(urlparse(route.request.url).query).get("path", [""])[0]
        if p in DOCS:
            route.fulfill(status=200, content_type="text/plain; charset=utf-8", body=DOCS[p])
        else:
            route.fulfill(status=404, body="not found")

    def image(route):
        p = parse_qs(urlparse(route.request.url).query).get("path", [""])[0]
        if p in IMAGES:
            route.fulfill(status=200, content_type="image/png", body=PNG)
        else:
            route.fulfill(status=404, body="not found")

    page.route("**/api/sdk-doc?*", doc)
    page.route("**/api/sdk-doc-image?*", image)
    popups = []
    ctx.on("page", lambda p: popups.append(p.url))
    try:
        yield page, port, popups
    finally:
        ctx.close()
        server.shutdown()


def _open(page, port, path, theme=None):
    if theme:
        page.add_init_script(f"try{{localStorage.setItem('dx-theme','{theme}')}}catch(e){{}}")
    page.goto(f"http://127.0.0.1:{port}/sdk-library?doc={path}", wait_until="load", timeout=60000)
    page.wait_for_function("document.querySelector('#sdkViewerBody h1') !== null", timeout=20000)
    page.wait_for_timeout(800)


def _wait_section_on_top(page, title_re):
    """Scrolling is smooth (scroll-behavior), so wait for it to settle instead of a fixed pause."""
    page.wait_for_function("""(re) => { const h = [...document.querySelectorAll('#sdkViewerBody h2')]
        .find(e => new RegExp(re).test(e.textContent));
      const b = document.getElementById('sdkViewerBody');
      return h && Math.abs(h.getBoundingClientRect().top - b.getBoundingClientRect().top) < 200; }""",
                           arg=title_re, timeout=5000)


SHOWN_IMAGES = """() => [...document.querySelectorAll('#sdkViewerBody img')]
  .filter(i => getComputedStyle(i).display !== 'none')
  .map(i => ({src: decodeURIComponent(i.getAttribute('src')), w: i.naturalWidth}))"""


def test_theme_images_load_and_only_the_one_for_the_theme_shows(viewer):
    page, port, _ = viewer
    _open(page, port, "docs/arch.md")
    page.evaluate("document.documentElement.setAttribute('data-theme', 'light')")
    shown = page.evaluate(SHOWN_IMAGES)
    assert [s["src"].split("path=")[-1].split("#")[0] for s in shown] == ["docs/resources/full.png"], shown
    assert all(s["w"] > 0 for s in shown), shown
    page.evaluate("document.documentElement.setAttribute('data-theme', 'dark')")
    shown = page.evaluate(SHOWN_IMAGES)
    assert [s["src"].split("path=")[-1].split("#")[0] for s in shown] == ["docs/resources/full-dark.png"], shown
    assert all(s["w"] > 0 for s in shown), shown


def test_a_section_link_scrolls_the_doc_and_opens_no_tab(viewer):
    page, port, popups = viewer
    _open(page, port, "docs/arch.md")
    page.click("#sdkViewerBody a:has-text('the runtime')")
    _wait_section_on_top(page, "Model Runtime")
    assert popups == [], popups
    top = page.evaluate("""() => {
      const h = [...document.querySelectorAll('#sdkViewerBody h2')].find(e => /Model Runtime/.test(e.textContent));
      const body = document.getElementById('sdkViewerBody');
      return h.getBoundingClientRect().top - body.getBoundingClientRect().top; }""")
    assert 0 <= top < 200, f"heading not scrolled into view: {top}"


def test_a_link_to_a_section_of_another_doc_opens_it_there(viewer):
    page, port, popups = viewer
    _open(page, port, "docs/arch.md")
    page.click("#sdkViewerBody a:has-text('guide setup')")
    page.wait_for_function("/First Setup/.test(document.getElementById('sdkViewerBody').textContent)", timeout=10000)
    _wait_section_on_top(page, "First Setup")
    assert popups == [], popups
    top = page.evaluate("""() => {
      const h = [...document.querySelectorAll('#sdkViewerBody h2')].find(e => /First Setup/.test(e.textContent));
      const body = document.getElementById('sdkViewerBody');
      return h.getBoundingClientRect().top - body.getBoundingClientRect().top; }""")
    assert 0 <= top < 200, f"opened at the top, not at the section: {top}"


def test_an_html_link_to_a_doc_opens_in_the_viewer(viewer):
    page, port, popups = viewer
    _open(page, port, "showcase/README.md")
    shown = page.evaluate(SHOWN_IMAGES)
    assert shown and all(s["w"] > 0 for s in shown), shown
    page.click("#sdkViewerBody a:has(img)")
    page.wait_for_function("/The game/.test(document.getElementById('sdkViewerBody').textContent)", timeout=10000)
    assert popups == [], popups


def test_links_that_lead_nowhere_are_plain_text(viewer):
    page, port, _ = viewer
    _open(page, port, "docs/arch.md")
    links = page.evaluate("[...document.querySelectorAll('#sdkViewerBody a')].map(a => a.textContent)")
    for dead in ("internal notes", "the build script", "License"):
        assert dead not in links, f"{dead!r} still looks like a link: {links}"
        assert dead in page.inner_text("#sdkViewerBody")


def test_a_heading_with_its_own_id_is_found_and_the_id_is_not_shown(viewer):
    """`## Graph Composer {#graph-composer}` (MkDocs attr_list) — DX AI Studio's own DX App manual uses it."""
    page, port, _ = viewer
    _open(page, port, "docs/guide.md")
    titles = page.evaluate("[...document.querySelectorAll('#sdkViewerBody h2')].map(h => h.textContent)")
    assert "Graph Composer" in titles, titles
    page.click("#sdkViewerBody a:has-text('the composer')")
    page.wait_for_function("""() => { const h = document.getElementById('graph-composer');
      const b = document.getElementById('sdkViewerBody');
      return h && Math.abs(h.getBoundingClientRect().top - b.getBoundingClientRect().top) < 200; }""", timeout=5000)
    top = page.evaluate("""() => {
      const h = document.getElementById('graph-composer');
      const body = document.getElementById('sdkViewerBody');
      return h ? h.getBoundingClientRect().top - body.getBoundingClientRect().top : null; }""")
    assert top is not None and 0 <= top < 200, top


def test_inline_code_shows_exactly_what_the_doc_wrote(viewer):
    """`<variant>_sync.cpp` showed as `_sync.cpp` and `#include <dxrt/dxrt_api.h>` as `dxrt_api.h`: the text
    inside backticks went into the page as HTML. 72 library docs have `<…>` in inline code."""
    page, port, _ = viewer
    _open(page, port, "docs/code.md")
    codes = page.evaluate("[...document.querySelectorAll('#sdkViewerBody code')].map(c => c.textContent)")
    assert codes == ["<variant>_sync.cpp", "<dxrt/dxrt_api.h>", "--lang <lang>", "**x**", "[a](b.md)"], codes
