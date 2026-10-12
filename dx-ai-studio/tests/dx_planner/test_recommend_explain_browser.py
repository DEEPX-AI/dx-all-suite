"""EdgeGuide: every number explains itself.

In a non-English UI (e.g. Korean, object detection · 8 cameras · 60 FPS):
1. the methodology "This session" line is translated (not "max 8 ch · estimated" or raw object_detection);
2. the bottleneck rule (NPU ≥ 85 % busy → NPU, else host) is explained;
3. "Estimated+" is explained;
4. the formula boxes are translated;
5. each card shows its arithmetic (534 FPS ÷ 60 FPS = 8.9 → 8 ch).
"""
from __future__ import annotations

import math
import re

import pytest

pytest.importorskip("playwright.sync_api")

from tests.dx_planner.test_recommend_engine_browser import _inputs, _platform, _recommend, _rows  # noqa: E402
from tests.server_helpers import start_module_server  # noqa: E402

LANGS = ["ko", "ja", "es", "zh-CN", "zh-TW"]


# ── the real page ───────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def planner():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_planner")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br, port
    br.close()
    pw.stop()
    srv.shutdown()


def _open(planner, lang, fps="60", cameras=8):
    br, port = planner
    ctx = br.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off');"
                        f"localStorage.setItem('dx-lang','{lang}');localStorage.removeItem('dxPlanner.state.v1');")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.click('.task-btn[data-task="object_detection"]')
    pg.evaluate("n => { const s = document.getElementById('channelSlider'); s.value = n;"
                " s.dispatchEvent(new Event('input', {bubbles: true})); }", cameras)
    pg.select_option("#targetFps", fps)
    pg.click("#btnSetupNext")
    pg.wait_for_selector("#btnRecommend:not([disabled])", timeout=10000)
    pg.click("#btnRecommend")
    pg.wait_for_selector("#recommend-cards .card-why", timeout=15000)
    return ctx, pg


def test_an_estimated_card_shows_the_division(planner):
    ctx, pg = _open(planner, "en")
    try:
        lines = pg.eval_on_selector_all("#recommend-cards .card-why", "els => els.map(e => e.innerText)")
        shown = [re.search(r"([\d,.]+) FPS ÷ 60 FPS = ([\d.]+) → (\d+) ch", line) for line in lines]
        shown = [m for m in shown if m]
        assert shown, lines
        for m in shown:
            total, quotient, n = float(m.group(1).replace(",", "")), float(m.group(2)), int(m.group(3))
            assert quotient == math.floor(total / 60 * 10) / 10      # cut, never rounded up past the floor
            assert n == math.floor(total / 60)
    finally:
        ctx.close()


def test_the_limit_chip_shows_the_npu_load(planner):
    ctx, pg = _open(planner, "en")
    try:
        chips = pg.eval_on_selector_all("#recommend-cards .card-why-note", "els => els.map(e => e.innerText)")
        limits = [c for c in chips if c.startswith("Limit")]
        assert limits and all(re.search(r"NPU \d+%", c) for c in limits), limits
    finally:
        ctx.close()


def test_capped_and_measured_lines_say_so(planner):
    ctx, pg = _open(planner, "en")
    try:
        capped = pg.evaluate("""() => CardRenderer._whyHtml({why: {kind: 'estimated', n: 36, tSat: 760, target: 30,
            raw: 760 / 30, maxTested: 18, capped: true}, bottleneck: null})""")
        assert "760 FPS ÷ 30 FPS = 25.3 → 36 ch+" in capped and "2 × 18" in capped, capped
        measured = pg.evaluate("""() => CardRenderer._whyHtml({why: {kind: 'measured', n: 8, atFps: 31.7, target: 30,
            nextN: 9, nextFps: 28.1}, bottleneck: null})""")
        assert "31.7 FPS each ≥ 30 FPS" in measured and "9 ch dropped to 28.1 FPS" in measured, measured
    finally:
        ctx.close()


@pytest.mark.parametrize("lang", LANGS)
def test_the_methodology_speaks_the_language(planner, lang):
    ctx, pg = _open(planner, lang)
    try:
        pg.click("[data-open-methodology]")
        pg.wait_for_selector("#methodologyDialog[open]")
        live = pg.inner_text("#methodologyLiveSummary")
        for english in ("max ", " ch ·", "estimated", "measured", "object_detection", "Top pick"):
            assert english not in live, (lang, live)
        task = pg.inner_text('.task-btn[data-task="object_detection"]').strip()
        assert task in live, (lang, task, live)
        formulas = pg.inner_text("#methodologyDialog .methodology-grid")
        for english in ("lowest measured total FPS", "largest measured stream count", "if every count holds it",
                        "the same, on an estimate"):
            assert english not in formulas, (lang, english)
        assert "85" in formulas, "the NPU / host limit rule is explained"
        assert "T_sat" in formulas and "floor" in formulas
    finally:
        ctx.close()


def test_english_methodology_explains_the_plus_and_the_limit(planner):
    ctx, pg = _open(planner, "en")
    try:
        pg.click("[data-open-methodology]")
        text = pg.inner_text("#methodologyDialog")
        assert "Estimated+" in text and "twice" in text
        assert "85%" in text and "host" in text
    finally:
        ctx.close()


# ── engine: why carries what the card needs ────────────────────────────────

def test_an_estimate_carries_target_quotient_and_npu_load(engine):
    rows = _rows((3, 40.0, False, 62.0), (4, 30.5, False, 70.0))      # tSat 120, nothing measured at 60
    r = _recommend(engine, _inputs(targetFps=60), [_platform("p", rows)])[0]
    assert r["why"]["kind"] == "estimated"
    assert r["why"]["target"] == 60
    assert r["why"]["raw"] == pytest.approx(120 / 60)
    assert r["npuPct"] == pytest.approx(70.0)


def test_a_measured_answer_carries_its_target(engine):
    rows = _rows((2, 35.0), (3, 29.0))
    r = _recommend(engine, _inputs(targetFps=30), [_platform("p", rows)])[0]
    assert r["why"]["kind"] == "measured" and r["why"]["target"] == 30



@pytest.fixture()
def engine(planner):
    """RecommendEngine as the planner page loads it."""
    br, port = planner
    ctx = br.new_context()
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.wait_for_function("typeof RecommendEngine !== 'undefined'")
    yield pg
    ctx.close()


