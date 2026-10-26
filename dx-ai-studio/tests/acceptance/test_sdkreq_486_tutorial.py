"""SDKREQ-486 [Common] tutorial mode and help — in a real ./launcher.sh studio.

Tutorial mode is the home card switch (localStorage dx-tutorial-mode, ON when unset). ON opens each
module's Tutorial Guide by itself; OFF leaves it to the toolbar button. Modules come from the launcher
registry, so a new module must ship a guide too.
"""
from __future__ import annotations

from tests.acceptance.conftest import module_frame, wait_home


def _toc_opens_by_itself(frame, timeout=8000) -> bool:
    try:
        frame.locator(".dxt-toc.open").wait_for(timeout=timeout)
        return True
    except Exception:  # noqa: BLE001 - playwright TimeoutError: it did not open
        return False


def test_home_tutorial_card_is_on_by_default_and_the_switch_is_remembered(pages):
    page = pages.new("/", tutorial=None)
    wait_home(page)
    switch = page.locator("#dxt-mode-switch")
    switch.wait_for(state="attached", timeout=15000)
    assert switch.get_attribute("aria-checked") == "true"
    assert page.locator("#dxt-mode-label").text_content().strip() == "ON"
    switch.click()
    page.wait_for_function("() => localStorage.getItem('dx-tutorial-mode') === 'off'")
    assert switch.get_attribute("aria-checked") == "false"
    page.reload(wait_until="domcontentloaded")
    wait_home(page)
    page.wait_for_function("() => document.getElementById('dxt-mode-switch')?.getAttribute('aria-checked') === 'false'")
    assert page.locator("#dxt-mode-label").text_content().strip() == "OFF"


def test_on_the_first_home_visit_starts_the_launcher_tour(pages):
    page = pages.new("/", tutorial=None, launcher_tour=True)
    wait_home(page)
    page.locator(".dxt-tooltip.active").wait_for(timeout=30000)
    assert page.locator(".dxt-tooltip.active .dxt-tip-next").count() == 1


def test_with_tutorial_mode_on_every_module_opens_its_guide_by_itself(pages):
    page = pages.new("/", tutorial="on")
    wait_home(page)
    missing = []
    for key in page.evaluate("() => Object.keys(DXLauncher.APP_PATHS)"):
        page.evaluate("(k) => DXLauncher.launch(k)", key)
        frame = module_frame(page, key)
        if not _toc_opens_by_itself(frame):
            missing.append(key)
        page.evaluate("() => DXLauncher.goHome()")
        page.wait_for_function("() => DXLauncher.currentApp === null")
    assert not missing, f"no Tutorial Guide opened by itself in {missing}"


def test_with_tutorial_mode_off_nothing_opens_until_the_toolbar_button(pages):
    page = pages.new("/", tutorial="off")
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('planner')")
    frame = module_frame(page, "planner")
    assert not _toc_opens_by_itself(frame, timeout=3000)
    assert frame.locator(".dxt-tooltip.active").count() == 0
    frame.locator("#dxToolbarTutorial").click()
    frame.locator(".dxt-toc.open").wait_for(timeout=10000)
    frame.locator(".dxt-toc-btn-start").click()
    frame.locator(".dxt-tooltip.active").wait_for(timeout=10000)


def test_a_tour_steps_with_previous_next_and_done_in_korean(pages):
    page = pages.new("/", lang="ko", tutorial="off")
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('planner')")
    frame = module_frame(page, "planner")
    frame.locator("#dxToolbarTutorial").click()
    frame.locator(".dxt-toc-btn-start").click()
    tip = frame.locator(".dxt-tooltip.active")
    tip.wait_for(timeout=10000)
    prev, nxt = tip.locator(".dxt-tip-prev"), tip.locator(".dxt-tip-next")
    assert prev.is_disabled() and "이전" in prev.inner_text()
    assert "다음" in nxt.inner_text()
    assert "건너뛰기" in tip.locator(".dxt-tip-skip").inner_text()
    first = tip.inner_text()
    nxt.click()
    frame.wait_for_function("(t) => document.querySelector('.dxt-tooltip.active')?.innerText !== t", arg=first)
    assert not tip.locator(".dxt-tip-prev").is_disabled()
    tip.locator(".dxt-tip-prev").click()
    frame.wait_for_function("(t) => document.querySelector('.dxt-tooltip.active')?.innerText === t", arg=first)
    for _ in range(40):
        if "완료" in tip.locator(".dxt-tip-next").inner_text():
            break
        tip.locator(".dxt-tip-next").click()
        frame.wait_for_timeout(150)
    assert "완료" in tip.locator(".dxt-tip-next").inner_text(), "the last step of a section says 완료"
    tip.locator(".dxt-tip-next").click()
    frame.locator(".dxt-confirm-overlay").wait_for(timeout=10000)
    assert "섹션 완료" in frame.locator(".dxt-confirm-overlay").inner_text()


def test_about_has_no_tour_and_sdk_library_has_its_own(pages):
    page = pages.new("/about", tutorial="off")
    page.locator("#about-view.visible").wait_for(timeout=60000)
    page.wait_for_function("() => document.getElementById('dxToolbarTutorial')?.disabled === true", timeout=15000)
    page.evaluate("() => DXLauncher.goHome()")
    wait_home(page)
    page.locator("#studioGrid .sdk-card").click()
    page.locator("#sdk-library-view.visible").wait_for()
    page.wait_for_function("() => document.getElementById('dxToolbarTutorial')?.disabled === false", timeout=15000)
    page.locator("#dxToolbarTutorial").click()
    page.locator(".dxt-toc.open").wait_for(timeout=10000)
    page.locator(".dxt-toc-btn-start").click()
    page.locator(".dxt-tooltip.active").wait_for(timeout=10000)


def test_context_help_popups_work_with_tutorial_mode_off(pages):
    page = pages.new("/", tutorial="off")
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('planner')")
    frame = module_frame(page, "planner")
    frame.locator("[data-open-methodology]").first.click()
    frame.locator("#methodologyDialog[open]").wait_for(timeout=10000)
    frame.locator("#methodologyClose").click()
    frame.wait_for_function("() => !document.querySelector('#methodologyDialog[open]')")
