"""Pixel visual-regression gate.

What it is NOT: tests/test_ux_visual_gate.py, which audits tutorial
spotlight geometry through the DOM. That catches "the highlight points at nothing";
it cannot catch "the header lost its border" or "the hub tiles shifted 20px".

Each module's landing page is screenshotted at a fixed viewport and compared to a
committed baseline. Determinism was measured, not assumed — with a fresh context
per capture, reduced motion, animations disabled and the tutorial TOC closed, all
nine modules reproduce byte-identically (0 changed pixels) except dx_monitor, whose
live telemetry is masked.

Baselines are HOST-SPECIFIC (font rendering differs across machines), so this suite
is advisory in CI and its baselines are captured on the self-hosted runner. Refresh
them with:

    DX_VISUAL_UPDATE=1 ./.venv/bin/python -m pytest tests/visual/ -q
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")
pytest.importorskip("PIL")

from tests.server_helpers import start_module_server  # noqa: E402
from tests.visual.baseline_spec import (  # noqa: E402
    PAGE_SPECS,
    RESPONSIVE_HEIGHT,
    RESPONSIVE_LOCALE,
    RESPONSIVE_THEME,
    SPECS,
    VIEWPORT,
    axes,
    baseline_name,
    page_axes,
    page_baseline_name,
    responsive_axes,
    responsive_baseline_name,
)
from tests.visual.compare import compare  # noqa: E402
from tests.visual.conftest import STABILISE_INIT  # noqa: E402

BASELINE_DIR = Path(__file__).resolve().parent / "baselines"
ARTIFACT_DIR = Path(__file__).resolve().parents[2] / "var" / "visual-diffs"

# Repeat captures of the same commit differ by EXACTLY 0 pixels on all nine
# modules, so the threshold only has to absorb host-to-host AA jitter — and
# baselines are per-host anyway. 0.02% is measured, not felt: at 0.1% a global
# --accent change moves only 1 of 9 modules past the limit, i.e. the gate would
# wave through a palette change on eight pages.
MAX_CHANGED_RATIO = float(os.environ.get("DX_VISUAL_MAX_RATIO", "0.0002"))
UPDATE = os.environ.get("DX_VISUAL_UPDATE") == "1"


def _fixed_json(payload):
    body = json.dumps(payload)
    return lambda route, *_: route.fulfill(status=200, content_type="application/json", body=body)


def _capture(
    browser,
    module: str,
    spec: dict,
    theme: str,
    locale: str,
    out: Path,
    viewport: dict | None = None,
) -> None:
    server, port = start_module_server(module)
    try:
        ctx = browser.new_context(
            viewport=viewport or VIEWPORT,
            reduced_motion="reduce",
            locale=f"{locale}-US",
        )
        ctx.add_init_script(STABILISE_INIT)
        # Host state the page reads (spec["routes"]) is answered with a fixed payload.
        for pattern, payload in spec.get("routes", {}).items():
            ctx.route(pattern, _fixed_json(payload))
        # Theme and language must be settled before any page script for the first
        # paint to be right. dx-theme.js stamps data-theme from <head> immediately, so
        # without seeding them here a dark baseline is captured as light.
        ctx.add_init_script(
            "try {"
            f" localStorage.setItem('dx-theme', '{theme}');"
            f" localStorage.setItem('dx-lang', '{locale}');"
            " } catch (e) {}"
        )
        page = ctx.new_page()
        try:
            page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60_000)
            page.wait_for_timeout(spec["settle_ms"])
            # The tutorial TOC opens asynchronously and would cover the page.
            # Belt and braces: close the TOC, stop anything still running, and
            # return to the top. A tour that already scrolled leaves the page
            # where it left it, and hideTOC does not undo that.
            page.evaluate(
                "() => { const t = window._dxTutorial;"
                " if (t) { try { if (t.hideTOC) t.hideTOC();"
                "                if (t.stop) t.stop(); } catch (e) {} }"
                " window.scrollTo(0, 0); }"
            )
            page.wait_for_timeout(500)
            # A page behind a tab (PAGE_SPECS): open it and wait until its data has landed.
            if spec.get("setup"):
                page.evaluate(spec["setup"])
                page.wait_for_function(spec["wait"], timeout=20_000)
                page.evaluate("() => { const t = window._dxTutorial; if (t && t.hideTOC) t.hideTOC(); window.scrollTo(0, 0); }")
                page.wait_for_timeout(800)
            masks = [
                page.locator(sel)
                for sel in spec.get("mask", ())
                if page.locator(sel).count()
            ]
            out.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(out), animations="disabled", mask=masks)
        finally:
            page.close()
            ctx.close()
    finally:
        server.shutdown()


_AXES = axes()


def test_axes_cover_every_module_theme_and_locale():
    """If any axis is missing, regressions in that combination are never caught."""
    from tests.visual.baseline_spec import LOCALES, THEMES

    assert len(_AXES) == len(SPECS) * len(THEMES) * len(LOCALES)
    assert ("dx_app", "light", "es") in _AXES


@pytest.mark.visual
@pytest.mark.parametrize(
    ("module", "theme", "locale"),
    _AXES,
    ids=[f"{m}-{t}-{loc}" for m, t, loc in _AXES],
)
def test_module_landing_page_matches_baseline(
    visual_browser, module, theme, locale, tmp_path
):
    engine, browser = visual_browser
    spec = SPECS[module]
    name = baseline_name(module, theme, locale)

    baseline = BASELINE_DIR / engine / name
    if UPDATE:
        _capture(browser, module, spec, theme, locale, baseline)
        pytest.skip(f"baseline written: {baseline.relative_to(BASELINE_DIR.parent)}")

    if not baseline.is_file():
        pytest.skip(
            f"no baseline for {engine}/{name} — create it with "
            f"DX_VISUAL_UPDATE=1 pytest tests/visual/"
        )

    candidate = tmp_path / name
    _capture(browser, module, spec, theme, locale, candidate)

    diff_out = ARTIFACT_DIR / engine / f"{name[:-4]}-diff.png"
    result = compare(baseline, candidate, diff_out)

    assert result["same_size"], (
        f"{engine}/{name}: viewport changed — baseline {result['baseline_size']} "
        f"vs current {result['candidate_size']}"
    )
    assert result["changed_ratio"] <= MAX_CHANGED_RATIO, (
        f"{engine}/{name}: {result['changed_pixels']} px "
        f"({result['changed_ratio'] * 100:.4f}%) differ, limit "
        f"{MAX_CHANGED_RATIO * 100:.4f}%. Diff: {diff_out}"
    )


@pytest.mark.visual
@pytest.mark.parametrize(
    ("module", "width"),
    responsive_axes(),
    ids=[f"{m}-w{w}" for m, w in responsive_axes()],
)
def test_module_landing_page_matches_baseline_at_width(
    visual_browser, module, width, tmp_path
):
    """The axis that shows what changes when a breakpoint moves.

    The other baselines are all 1280 wide, so moving a fold from 900 to 960 would
    turn no test red. These widths cover those ranges.
    """
    engine, browser = visual_browser
    spec = SPECS[module]
    name = responsive_baseline_name(module, width)
    viewport = {"width": width, "height": RESPONSIVE_HEIGHT}

    baseline = BASELINE_DIR / engine / name
    if UPDATE:
        _capture(
            browser, module, spec, RESPONSIVE_THEME, RESPONSIVE_LOCALE,
            baseline, viewport=viewport,
        )
        pytest.skip(f"baseline written: {baseline.relative_to(BASELINE_DIR.parent)}")

    if not baseline.is_file():
        pytest.skip(
            f"no baseline for {engine}/{name} — create it with "
            f"DX_VISUAL_UPDATE=1 pytest tests/visual/"
        )

    candidate = tmp_path / name
    _capture(
        browser, module, spec, RESPONSIVE_THEME, RESPONSIVE_LOCALE,
        candidate, viewport=viewport,
    )

    diff_out = ARTIFACT_DIR / engine / f"{name[:-4]}-diff.png"
    result = compare(baseline, candidate, diff_out)

    assert result["same_size"], (
        f"{engine}/{name}: viewport changed — baseline {result['baseline_size']} "
        f"vs current {result['candidate_size']}"
    )
    assert result["changed_ratio"] <= MAX_CHANGED_RATIO, (
        f"{engine}/{name}: {result['changed_pixels']} px "
        f"({result['changed_ratio'] * 100:.4f}%) differ, limit "
        f"{MAX_CHANGED_RATIO * 100:.4f}%. Diff: {diff_out}"
    )


_PAGE_AXES = page_axes()


def test_page_axes_cover_both_themes_in_en_and_ko():
    assert ("dx_app_graph", "dark", "ko") in _PAGE_AXES
    assert len(_PAGE_AXES) == 4 * len(PAGE_SPECS)


@pytest.mark.visual
@pytest.mark.parametrize(
    ("page_key", "theme", "locale"),
    _PAGE_AXES,
    ids=[f"{p}-{t}-{loc}" for p, t, loc in _PAGE_AXES],
)
def test_module_page_matches_baseline(visual_browser, page_key, theme, locale, tmp_path):
    """Pages behind a tab, drawn from data (PAGE_SPECS): the Graph Composer with one example open."""
    engine, browser = visual_browser
    spec = PAGE_SPECS[page_key]
    name = page_baseline_name(page_key, theme, locale)

    baseline = BASELINE_DIR / engine / name
    if UPDATE:
        _capture(browser, spec["module"], spec, theme, locale, baseline)
        pytest.skip(f"baseline written: {baseline.relative_to(BASELINE_DIR.parent)}")

    if not baseline.is_file():
        pytest.skip(
            f"no baseline for {engine}/{name} — create it with "
            f"DX_VISUAL_UPDATE=1 pytest tests/visual/"
        )

    candidate = tmp_path / name
    _capture(browser, spec["module"], spec, theme, locale, candidate)

    diff_out = ARTIFACT_DIR / engine / f"{name[:-4]}-diff.png"
    result = compare(baseline, candidate, diff_out)

    assert result["same_size"], (
        f"{engine}/{name}: viewport changed — baseline {result['baseline_size']} "
        f"vs current {result['candidate_size']}"
    )
    assert result["changed_ratio"] <= MAX_CHANGED_RATIO, (
        f"{engine}/{name}: {result['changed_pixels']} px "
        f"({result['changed_ratio'] * 100:.4f}%) differ, limit "
        f"{MAX_CHANGED_RATIO * 100:.4f}%. Diff: {diff_out}"
    )
