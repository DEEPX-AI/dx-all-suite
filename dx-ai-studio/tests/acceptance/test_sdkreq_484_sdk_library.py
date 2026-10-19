"""SDKREQ-484 [SDK Library] technical document hub — against a real ./launcher.sh studio."""
from __future__ import annotations

from tests.acceptance.conftest import wait_home


def _open_library(pages, path="/sdk-library"):
    page = pages.new(path)
    page.locator("#sdk-library-view.visible").wait_for(timeout=60000)
    page.locator(".sdk-list-sidebar .sdk-sidebar-group").first.wait_for(timeout=60000)
    return page


def _open_first_doc_from_the_list(page):
    """Open the first Markdown document the List view offers (PDFs open in an embedded viewer)."""
    heads = page.locator(".sdk-list-sidebar .sdk-sidebar-group-head")
    for g in range(heads.count()):
        heads.nth(g).click()
        cards = page.locator("#sdkListContent .file-card")
        cards.first.wait_for(timeout=30000)
        for i in range(min(cards.count(), 8)):
            cards.nth(i).click()
            page.locator("#sdkBookViewer.open").wait_for(timeout=30000)
            if page.evaluate("() => decodeURIComponent(location.search).endsWith('.md')"):
                page.locator("#sdkViewerBody h1, #sdkViewerBody h2").first.wait_for(timeout=30000)
                return
            page.locator("#sdkBookViewer .sdk-viewer-close").click()
            page.wait_for_function("() => !document.querySelector('#sdkBookViewer.open')")
    raise AssertionError("no Markdown document in the List view")


def test_list_and_cabinet_views_open_a_document_in_the_viewer(pages):
    page = _open_library(pages)
    assert page.locator(".sdk-list-sidebar .sdk-sidebar-group").count() >= 5
    _open_first_doc_from_the_list(page)
    title = page.locator("#sdkBookViewer .sdk-viewer-title").inner_text().strip()
    assert title, "the viewer shows the document title"
    assert len(page.locator("#sdkViewerBody").inner_text()) > 200, "the Markdown body is rendered"
    assert "doc=" in page.evaluate("() => location.search")
    page.locator("#sdkBookViewer .sdk-viewer-close").click()
    page.wait_for_function("() => !document.querySelector('#sdkBookViewer.open')")
    page.locator('.sdk-toggle-btn[data-mode="cabinet"]').click()
    face = page.locator(".drawer-unit .drawer-face").first
    face.wait_for(timeout=30000)
    face.click()
    card = page.locator(".drawer-unit .file-card").first
    card.wait_for(timeout=30000)
    card.click()
    page.locator("#sdkBookViewer.open").wait_for(timeout=30000)
    assert page.locator("#sdkBookViewer .sdk-viewer-title").inner_text().strip()


def test_viewer_search_highlights_and_counts_and_close_or_escape_stays_in_the_library(pages):
    page = _open_library(pages, "/sdk-library?doc=docs/source/index.md")
    page.locator("#sdkBookViewer.open").wait_for(timeout=60000)
    page.locator("#sdkViewerBody h1").wait_for(timeout=30000)
    page.locator("#sdkViewerSearch").fill("DEEPX")
    page.locator("#sdkViewerBody mark.sdk-search-hit").first.wait_for(timeout=10000)
    hits = page.locator("#sdkViewerBody mark.sdk-search-hit").count()
    assert hits > 0
    info = page.locator("#sdkViewerSearchInfo").inner_text()
    assert f"/{hits}" in info.replace(" ", ""), info
    page.locator("#sdkBookViewer .sdk-viewer-close").click()
    page.wait_for_function("() => !document.querySelector('#sdkBookViewer.open')")
    assert page.locator("#sdk-library-view.visible").count() == 1
    _open_first_doc_from_the_list(page)
    page.locator("#sdkViewerBody").click()
    page.keyboard.press("Escape")
    page.wait_for_function("() => !document.querySelector('#sdkBookViewer.open')")
    assert page.evaluate("() => DXLauncher.currentApp") == "sdk-library"
    assert page.locator("#sdk-library-view.visible").count() == 1


def test_escape_in_the_library_search_clears_it_and_stays_in_the_library(pages):
    page = _open_library(pages)
    box = page.locator("#sdkLibSearch")
    box.fill("compiler")
    box.press("Escape")
    page.wait_for_function("() => document.getElementById('sdkLibSearch').value === ''")
    assert page.evaluate("() => DXLauncher.currentApp") == "sdk-library"
    assert page.locator("#sdk-library-view.visible").count() == 1


def test_top_nav_switches_between_about_and_sdk_library(pages):
    page = pages.new("/")
    wait_home(page)
    page.locator("#studioGrid .about-book-card:not(.sdk-card)").click()
    page.locator("#about-view.visible").wait_for()
    page.locator('#navTabs .nav-tab[data-app="sdk-library"]').click()
    page.locator("#sdk-library-view.visible").wait_for()
    assert page.evaluate("() => location.pathname") == "/sdk-library"
    assert page.locator("#about-view.visible").count() == 0
    page.locator('#navTabs .nav-tab[data-app="about"]').click()
    page.locator("#about-view.visible").wait_for()
    assert page.evaluate("() => location.pathname") == "/about"
    assert page.locator("#sdk-library-view.visible").count() == 0


def test_a_document_that_fails_to_load_offers_retry_that_works(pages):
    page = pages.new(None)
    page.route("**/api/sdk-doc?*", lambda route: route.abort())
    page.goto(pages.studio.base + "/sdk-library?doc=docs/source/index.md", wait_until="domcontentloaded")
    retry = page.locator("#sdkViewerBody .sdk-retry-btn")
    retry.wait_for(timeout=60000)
    page.unroute("**/api/sdk-doc?*")
    retry.click()
    page.locator("#sdkViewerBody h1").wait_for(timeout=30000)


def test_a_library_that_fails_to_load_offers_retry_that_works(pages):
    page = pages.new(None)
    page.route("**/api/sdk-library*", lambda route: route.abort())
    page.route("**/sdk-library-data.json*", lambda route: route.abort())
    page.goto(pages.studio.base + "/sdk-library", wait_until="domcontentloaded")
    retry = page.locator("#sdkCabinet .sdk-retry-btn")
    retry.wait_for(timeout=60000)
    page.unroute("**/api/sdk-library*")
    page.unroute("**/sdk-library-data.json*")
    retry.click()
    page.locator(".sdk-list-sidebar .sdk-sidebar-group").first.wait_for(timeout=30000)
