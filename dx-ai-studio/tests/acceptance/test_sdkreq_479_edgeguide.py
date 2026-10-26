"""SDKREQ-479 [EdgeGuide] product recommendation — DX EdgeGuide inside a real ./launcher.sh studio."""
from __future__ import annotations

from tests.acceptance.conftest import module_frame, wait_home


def _planner(pages, lang="en"):
    page = pages.new("/", lang=lang)
    page.add_init_script("try{localStorage.removeItem('dxPlanner.state.v1');}catch(e){}")
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('planner')")
    return page, module_frame(page, "planner", ready="#workflowSteps")


def _steps(frame):
    return [t.strip() for t in frame.locator("#workflowSteps .workflow-step[data-step] span[data-i18n]").all_inner_texts()]


def _recommend_cctv(frame):
    frame.locator('.scenario-chip[data-preset="cctv"]').click()
    frame.locator('#requirementsStep2[aria-hidden="false"]').wait_for(timeout=10000)
    frame.locator("#btnRecommend").click()
    frame.locator("#recommend-cards .rec-card").first.wait_for(timeout=30000)


def test_four_workflow_steps_in_english_and_korean(pages):
    page, frame = _planner(pages)
    keys = frame.locator("#workflowSteps .workflow-step[data-step]").evaluate_all("els => els.map(e => e.dataset.step)")
    assert keys == ["requirements", "recommendations", "details", "commerce"]
    assert _steps(frame) == ["Scenario", "Pick", "Evidence", "Buy"]
    page2, frame2 = _planner(pages, lang="ko")
    assert _steps(frame2) == ["시나리오", "추천", "근거", "구매"]


def test_a_scenario_chip_fills_the_conditions_and_opens_the_priority_panel(pages):
    page, frame = _planner(pages, lang="ko")
    chip = frame.locator('.scenario-chip[data-preset="cctv"]')
    assert "4채널 CCTV OD" in chip.inner_text()
    assert frame.locator(".scenario-chip[data-preset]").count() >= 3
    chip.click()
    frame.locator('#requirementsStep2[aria-hidden="false"]').wait_for(timeout=10000)
    assert frame.locator("#channelValue").inner_text().strip().startswith("4") or \
        frame.locator("#channelValue").input_value().startswith("4")
    assert frame.locator("input[name=priority]").evaluate_all("els => els.map(e => e.value)") == [
        "channels", "performance", "power"]


def test_recommendation_ranks_dx_products_with_a_chart_and_explains_the_method(pages):
    page, frame = _planner(pages)
    _recommend_cctv(frame)
    assert frame.locator("#recommend-cards .rank-disc--top").count() == 1
    names = " ".join(frame.locator("#recommend-cards .rec-card h3").all_inner_texts())
    assert "DX-M1" in names and "DX-H1" in names, names
    frame.wait_for_function("() => { const c = document.getElementById('overviewChart'); return c && c.width > 0; }")
    frame.locator("[data-open-methodology]").first.click()
    frame.locator("#methodologyDialog[open]").wait_for(timeout=10000)
    assert frame.locator("#methodologyDialog .methodology-card, #methodologyDialog article, #methodologyDialog li").count() > 0
    frame.locator("#methodologyClose").click()


def test_a_card_details_show_evidence_and_the_buy_panel(pages):
    page, frame = _planner(pages)
    _recommend_cctv(frame)
    frame.locator("#recommend-cards .rec-card .btn-detail").first.click()
    frame.locator("#commercePanel:not([hidden])").wait_for(timeout=15000)
    assert "shop_now" in frame.locator("#commercePanel a.btn-commerce-primary").get_attribute("href")
    assert "contact-us" in frame.locator("#commercePanel a.btn-commerce-secondary").get_attribute("href")
    frame.locator('.workflow-step[data-step="commerce"].is-active').wait_for(timeout=10000)
    frame.locator("#radarChart").wait_for(state="attached")
    frame.locator("#benchmark-table").wait_for(state="attached")


def test_opened_from_benchmark_it_recommends_for_those_conditions_at_once(pages):
    page = pages.new("/")
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('benchmark')")
    bench = module_frame(page, "benchmark", ready="#edgeguideBtn")
    bench.locator("#edgeguideBtn").click()
    page.wait_for_function("() => DXLauncher.currentApp === 'planner'", timeout=15000)
    planner = module_frame(page, "planner", ready="#workflowSteps")
    assert "task=" in planner.url
    planner.locator("#recommend-cards .rec-card").first.wait_for(timeout=30000)
