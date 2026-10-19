"""SDKREQ-473 [Launcher] entry and moving between modules — against a real ./launcher.sh studio.

The module list is the launcher's own registry (DXLauncher.APP_PATHS / /api/health), never a fixed
count, so a new module is covered without editing this file.
"""
from __future__ import annotations

import json
import re

import pytest

from tests.acceptance.conftest import module_frame, wait_home


def _registry(page) -> dict:
    return page.evaluate("() => Object.assign({}, DXLauncher.APP_PATHS)")


def _go_home(page):
    page.evaluate("() => DXLauncher.goHome()")
    page.wait_for_function("() => DXLauncher.currentApp === null")


def test_launcher_prints_the_studio_url(studio):
    out = studio.launcher_output()
    assert re.search(rf"OPEN THE STUDIO:\s+http://localhost:{studio.port}\b", out), out[-2000:]


@pytest.mark.parametrize("how", ["Enter", "Space", "Escape", "click"])
def test_the_intro_plays_once_and_any_key_or_click_skips_it(pages, how):
    page = pages.new("/", quiet=False)
    page.locator("#splashOverlay.is-running").wait_for(state="attached", timeout=30000)
    if how == "click":
        page.locator("#splashOverlay").click()
    else:
        page.keyboard.press(how)
    page.locator("#splashOverlay").wait_for(state="detached", timeout=10000)
    wait_home(page)
    assert page.locator("#studioGrid .orbital-card").first.is_visible()


def test_home_has_a_card_for_every_module_and_a_click_loads_it(pages):
    page = pages.new("/")
    wait_home(page)
    registry = _registry(page)
    assert len(registry) >= 9, registry
    cards = page.eval_on_selector_all("#studioGrid .orbital-card[data-app]", "els => els.map(e => e.dataset.app)")
    assert sorted(cards) == sorted(registry), (cards, registry)
    assert page.locator("#studioGrid .sdk-card").count() == 1
    assert page.locator("#studioGrid .about-book-card:not(.sdk-card)").count() == 1
    for key in cards:
        page.locator(f'#studioGrid .orbital-card[data-app="{key}"]').click()
        page.wait_for_function("(k) => DXLauncher.currentApp === k", arg=key)
        frame = module_frame(page, key)
        assert frame.url.rstrip("/").endswith(registry[key].rstrip("/")), (key, frame.url)
        assert page.evaluate("() => location.pathname").rstrip("/") == registry[key].rstrip("/")
        _go_home(page)


def test_about_and_sdk_library_cards_open_their_views(pages):
    page = pages.new("/")
    wait_home(page)
    page.locator("#studioGrid .about-book-card:not(.sdk-card)").click()
    page.locator("#about-view.visible").wait_for()
    tabs = page.locator("#aboutNav .about-nav-tab")
    assert tabs.count() == 7
    page.wait_for_function(
        "(want) => [...document.querySelectorAll('#aboutNav .about-nav-tab')].map(t => t.textContent.trim())"
        ".join('|') === want", arg="Developer|Company|Technology|Products|Partners|Awards|News", timeout=15000)
    tabs.nth(3).click()
    # The tab scrolls its section into view (About is one page with scroll-spy anchors).
    page.wait_for_function("() => { const r = document.getElementById('aboutProducts').getBoundingClientRect();"
                           " return r.top >= 0 && r.top < innerHeight * 0.6; }", timeout=10000)
    _go_home(page)
    page.locator("#studioGrid .sdk-card").click()
    page.locator("#sdk-library-view.visible").wait_for()
    assert page.evaluate("() => location.pathname") == "/sdk-library"


def test_top_nav_escape_and_alt_digit_shortcuts_move_between_modules(pages):
    page = pages.new("/")
    wait_home(page)
    registry = _registry(page)
    order = ["app", "stream", "zoo", "compiler", "planner", "benchmark", "dx_monitor", "agent", "edge"]
    assert set(order) <= set(registry), registry
    # Alt+1 … Alt+9, pressed with focus in the launcher
    for digit, key in enumerate(order, start=1):
        page.locator("body").focus()
        page.keyboard.press(f"Alt+{digit}")
        page.wait_for_function("(k) => DXLauncher.currentApp === k", arg=key, timeout=15000)
    # Top nav: Home + every module + SDK Library + About
    nav = page.eval_on_selector_all("#navTabs .nav-tab[data-app]", "els => els.map(e => e.dataset.app)")
    assert nav == order + ["sdk-library", "about"], nav
    assert page.locator("#navTabs .nav-tab.home-btn").count() == 1
    page.locator('#navTabs .nav-tab[data-app="zoo"]').click()
    page.wait_for_function("() => DXLauncher.currentApp === 'zoo'")
    page.locator('#navTabs .nav-tab[data-app="about"]').click()
    page.locator("#about-view.visible").wait_for()
    page.locator('#navTabs .nav-tab[data-app="planner"]').click()
    page.wait_for_function("() => DXLauncher.currentApp === 'planner'")
    # Escape from a module goes home
    page.locator("body").focus()
    page.keyboard.press("Escape")
    page.wait_for_function("() => DXLauncher.currentApp === null && location.pathname === '/'")
    wait_home(page)


def test_a_module_that_is_down_is_dimmed_on_home(pages):
    page = pages.new(None)

    def health(route):
        resp = route.fetch()
        body = resp.json()
        body["zoo"] = {"port": body["zoo"]["port"], "alive": False}
        route.fulfill(response=resp, body=json.dumps(body))

    page.route("**/api/health", health)
    page.goto(pages.studio.base + "/", wait_until="domcontentloaded")
    page.locator('#studioGrid .orbital-card[data-app="zoo"].is-down').wait_for(timeout=30000)
    assert page.locator('#studioGrid .orbital-card[data-app="app"].is-down').count() == 0


@pytest.mark.parametrize("path,check", [
    ("/zoo", "DXLauncher.currentApp === 'zoo'"),
    ("/app", "DXLauncher.currentApp === 'app'"),
    ("/about", "document.querySelector('#about-view.visible') !== null"),
    ("/sdk-library?doc=docs/source/index.md", "document.querySelector('#sdkBookViewer.open') !== null"),
])
def test_a_direct_url_and_f5_reopen_the_same_view(pages, path, check):
    page = pages.new(path)
    page.wait_for_function(f"() => {check}", timeout=60000)
    page.reload(wait_until="domcontentloaded")
    page.wait_for_function(f"() => {check}", timeout=60000)


def test_home_reloads_itself_when_the_launcher_restarts(pages):
    page = pages.new(None)
    boot = {"id": None}

    def health(route):
        resp = route.fetch()
        body = resp.json()
        if boot["id"]:
            body["launcher_boot"] = boot["id"]
        route.fulfill(response=resp, body=json.dumps(body))

    page.route("**/api/health", health)
    page.goto(pages.studio.base + "/", wait_until="domcontentloaded")
    wait_home(page)
    page.evaluate("() => { window.__beforeRestart = true; }")
    boot["id"] = "1-424242"                      # what a restarted launcher reports
    page.wait_for_function("() => window.__beforeRestart !== true", timeout=30000)
    wait_home(page)
