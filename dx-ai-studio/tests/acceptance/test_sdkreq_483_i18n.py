"""SDKREQ-483 [Common] i18n — one language choice drives the launcher and every module, and is kept."""
from __future__ import annotations

import pytest

from tests.acceptance.conftest import module_frame, wait_home

LANGS = ["en", "ja", "ko", "es", "zh-CN", "zh-TW"]


def _frame_lang(frame) -> str:
    return frame.evaluate("() => (window.DXI18n && DXI18n.lang) || document.documentElement.lang")


def test_the_language_menu_offers_six_languages(pages):
    page = pages.new("/", lang=None)
    wait_home(page)
    page.locator("#dxToolbar .dx-lang-btn").click()
    items = page.locator(".dx-lang-menu .dx-lang-item")
    items.first.wait_for(state="visible")
    assert items.evaluate_all("els => els.map(e => e.dataset.lang)") == LANGS
    assert [t.strip() for t in items.all_inner_texts()] == [
        "English", "日本語", "한국어", "Español", "简体中文", "繁體中文"]


def test_a_choice_in_one_module_switches_the_launcher_and_every_open_module_and_survives_reload(pages):
    page = pages.new("/", lang=None)            # no forced language: the choice itself must persist
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('app')")
    app = module_frame(page, "app")
    page.evaluate("() => DXLauncher.launch('planner')")
    planner = module_frame(page, "planner")
    assert _frame_lang(app) == "en" and _frame_lang(planner) == "en"

    planner.locator("#dxToolbar .dx-lang-btn").click()
    planner.locator('.dx-lang-menu .dx-lang-item[data-lang="ko"]').click()

    page.wait_for_function("() => document.documentElement.lang === 'ko'", timeout=15000)
    app.wait_for_function("() => window.DXI18n && DXI18n.lang === 'ko'", timeout=15000)
    app.wait_for_function(
        "() => document.querySelector('.dx-tab[data-page=\"run\"]')?.textContent.includes('추론 실행')", timeout=15000)
    # Module names in the top nav are product names and stay English; the Home button is translated.
    page.wait_for_function(
        "() => document.querySelector('#navTabs .nav-tab.home-btn')?.title === '홈으로'", timeout=15000)

    page.evaluate("() => DXLauncher.goHome()")
    wait_home(page)
    page.wait_for_function(
        "() => document.querySelector('#studioGrid .orbital-card[data-app=\"edge\"] .card-desc')"
        "?.textContent.includes('AWS 클라우드 컴파일')", timeout=15000)

    page.reload(wait_until="domcontentloaded")
    wait_home(page)
    assert page.evaluate("() => document.documentElement.lang") == "ko"
    page.evaluate("() => DXLauncher.launch('zoo')")
    zoo = module_frame(page, "zoo")
    zoo.wait_for_function("() => window.DXI18n && DXI18n.lang === 'ko'", timeout=15000)


@pytest.mark.parametrize("lang,home", [("ja", "ホーム"), ("es", "Inicio"), ("zh-CN", "首页"), ("zh-TW", "首頁")])
def test_the_launcher_menu_switches_the_whole_studio(pages, lang, home):
    page = pages.new("/", lang=None)
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('compiler')")
    compiler = module_frame(page, "compiler")
    page.evaluate("() => DXLauncher.goHome()")
    wait_home(page)
    page.locator("#dxToolbar .dx-lang-btn").click()
    page.locator(f'.dx-lang-menu .dx-lang-item[data-lang="{lang}"]').click()
    page.wait_for_function("(l) => document.documentElement.lang === l", arg=lang, timeout=15000)
    compiler.wait_for_function("(l) => window.DXI18n && DXI18n.lang === l", arg=lang, timeout=15000)
    page.evaluate("() => DXLauncher.launch('dx_monitor')")
    monitor = module_frame(page, "dx_monitor")
    monitor.wait_for_function("(l) => window.DXI18n && DXI18n.lang === l", arg=lang, timeout=15000)
    page.wait_for_function(
        "(t) => document.querySelector('#navTabs .nav-tab.home-btn')?.title === t", arg=home, timeout=15000)
