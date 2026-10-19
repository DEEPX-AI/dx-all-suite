"""SDKREQ-481 [Benchmark] performance dashboard — DX Benchmark inside a real ./launcher.sh studio.

Benchmark shows the bundled benchmark data set (it does not run benchmarks itself).
"""
from __future__ import annotations

from tests.acceptance.conftest import module_frame, wait_home

SUBTABS = ["fps-compare", "overview", "detail", "version-trend", "ort-compare"]
SUBTABS_EN = ["E2E FPS Overview", "Full Metrics", "Detailed Data", "Version Trend", "ORT ON/OFF"]
TASKS = {"object_detection", "pose_estimation", "segmentation", "oriented_bbox", "classification"}


def _bench(pages):
    page = pages.new("/")
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('benchmark')")
    return page, module_frame(page, "benchmark", ready=".dx-tab[data-page]")


def test_dashboard_results_and_settings_tabs(pages):
    page, frame = _bench(pages)
    tabs = frame.locator(".dx-tab[data-page]")
    assert tabs.evaluate_all("els => els.map(e => e.dataset.page)") == ["dashboard", "results", "settings"]
    for tab in ("results", "settings", "dashboard"):
        frame.locator(f'.dx-tab[data-page="{tab}"]').click()
        frame.locator(f"#tab-{tab}.active").wait_for(timeout=10000)


def test_five_dashboard_subtabs_draw_their_charts_and_tables(pages):
    page, frame = _bench(pages)
    sub = frame.locator(".dashboard-tab[data-tab]")
    sub.first.wait_for(timeout=15000)
    assert sub.evaluate_all("els => els.map(e => e.dataset.tab)") == SUBTABS
    assert [t.strip() for t in sub.all_inner_texts()] == SUBTABS_EN
    targets = {"fps-compare": "#fpsCompareChart", "overview": "#mainChart", "detail": "#detailTables",
               "version-trend": "#trendChartsGrid", "ort-compare": "#ortCompareChart"}
    for key in SUBTABS:
        frame.locator(f'.dashboard-tab[data-tab="{key}"]').click()
        frame.locator(f"#tab-{key}.active").wait_for(timeout=10000)
        frame.wait_for_function(
            "(s) => { const e = document.querySelector(s); if (!e) return false;"
            " if (e.tagName === 'CANVAS') return e.width > 0 && e.offsetParent !== null;"
            " return e.children.length > 0 || e.innerText.trim().length > 0; }", arg=targets[key], timeout=15000)


def test_run_selection_and_task_filter(pages):
    page, frame = _bench(pages)
    frame.locator('.dashboard-tab[data-tab="fps-compare"]').click()
    selects = frame.locator("#fpsRunSelectors select[data-run-env]")
    selects.first.wait_for(timeout=15000)
    assert selects.count() >= 2
    tasks = set(frame.locator("#fpsTaskFilter option").evaluate_all("els => els.map(e => e.value)"))
    assert TASKS <= tasks, tasks
    before = frame.locator("#fpsChartSubtitle").inner_text()
    frame.select_option("#fpsTaskFilter", "pose_estimation")
    frame.wait_for_function("(t) => document.getElementById('fpsChartSubtitle').innerText !== t", arg=before,
                            timeout=10000)
    options = selects.first.locator("option").evaluate_all("els => els.map(e => e.value).filter(Boolean)")
    if len(options) > 1:
        selects.first.select_option(options[-1])


def test_results_open_a_run_by_hardware_and_settings_load(pages):
    page, frame = _bench(pages)
    frame.locator('.dx-tab[data-page="results"]').click()
    hw = frame.locator(".hw-card[data-hw-id]").first
    hw.wait_for(timeout=15000)
    hw.click()
    run = frame.locator(".run-item[data-run-id]").first
    run.wait_for(timeout=15000)
    run.click()
    frame.locator("#runDetail .run-detail").wait_for(timeout=15000)
    frame.locator('.dx-tab[data-page="settings"]').click()
    frame.wait_for_function("() => (document.getElementById('settIterations')?.value || '').length > 0", timeout=15000)


def test_the_edgeguide_button_opens_edgeguide_with_the_conditions(pages):
    page, frame = _bench(pages)
    frame.locator("#edgeguideBtn").click()
    page.wait_for_function("() => DXLauncher.currentApp === 'planner'", timeout=15000)
    planner = module_frame(page, "planner")
    for part in ("task=", "size=", "ort="):
        assert part in planner.url, planner.url
