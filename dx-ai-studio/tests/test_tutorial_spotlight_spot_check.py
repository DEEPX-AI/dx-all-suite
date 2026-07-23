"""Spot-check tutorial steps that previously had misaligned spotlights."""
from __future__ import annotations

import math

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

ALIGN_JS = """() => {
  const engine = window._dxTutorial;
  if (!engine || !engine._curSection) return { ok: false, reason: 'no engine' };
  if (engine._refreshHighlight) engine._refreshHighlight();
  const step = engine._curSection.steps[engine._curStep];
  const selector = step && step.target ? step.target : null;
  let target = null;
  if (selector && engine._queryTarget) target = engine._queryTarget(selector);
  else if (selector) target = document.querySelector(selector);
  const sp = document.querySelector('.dxt-spotlight.active');
  const tip = document.querySelector('.dxt-tooltip.active');
  const tr = target ? target.getBoundingClientRect() : null;
  const sr = sp ? sp.getBoundingClientRect() : null;
  const floating = !!(tip && tip.style.transform && tip.style.transform.indexOf('translate(-50%') >= 0);
  let overlap = 0;
  if (tr && sr && tr.width > 0 && tr.height > 0) {
    const ix = Math.max(0, Math.min(tr.right, sr.right) - Math.max(tr.left, sr.left));
    const iy = Math.max(0, Math.min(tr.bottom, sr.bottom) - Math.max(tr.top, sr.top));
    overlap = (ix * iy) / (tr.width * tr.height);
  }
  return {
    sectionId: engine._curSection.id,
    stepIndex: engine._curStep,
    selector,
    hasTarget: !!target,
    targetVisible: !!(tr && (tr.width > 2 || tr.height > 2)),
    targetRect: tr ? { x: tr.x, y: tr.y, w: tr.width, h: tr.height } : null,
    spotlightActive: !!sp,
    spotlightRect: sr ? { x: sr.x, y: sr.y, w: sr.width, h: sr.height } : null,
    overlap,
    floating,
    lightboxOpen: !!(document.getElementById('gallery-lightbox') && document.getElementById('gallery-lightbox').open),
    modalOpen: !!(document.getElementById('model-detail-modal') && document.getElementById('model-detail-modal').open),
  };
}"""

GOTO_STEP_JS = """async ([sectionId, stepIndex]) => {
  const engine = window._dxTutorial;
  if (!engine) return false;
  const ap = engine._appProgress();
  ['setup', 'models'].forEach(id => {
    if (!ap.completed.includes(id)) ap.completed.push(id);
  });
  engine._saveProgress();
  const sec = engine.sections.find(s => s.id === sectionId);
  if (!sec) return false;
  engine._buildDOM();
  engine._curSection = sec;
  engine._curStep = stepIndex;
  engine._overlay.classList.add('active');
  window.addEventListener('resize', engine._resizeHandler);
  window.addEventListener('scroll', engine._scrollHandler, true);
  if (sec.beforeStart) {
    const bs = sec.beforeStart();
    if (bs && typeof bs.then === 'function') await bs;
  }
  for (let i = 0; i < stepIndex; i++) {
    engine._invokeAfterStep(sec.steps[i]);
  }
  await engine._showStep();
  return true;
}"""

SPOT_CHECKS = [
    # dx_app — user-reported problem steps
    ("dx_app", "global", 5, "#dxt-mock-toast", 0.35),
    ("dx_app", "run-single", None, "#r-export-btn", 0.25),  # step index resolved at runtime
    ("dx_app", "modelzoo", None, "#mz-cart", 0.25),
    ("dx_app", "outputs", None, "#gallery-lightbox", 0.20),
    # dx_stream
    ("dx_stream", "global", None, "#dxt-mock-stream-toast", 0.35),
    ("dx_stream", "demo", None, "#demo-pipeline-info", 0.25),
    ("dx_stream", "pipeline", None, ".palette-item", 0.20),
    ("dx_stream", "models", None, "#model-detail-modal", 0.15),
    ("dx_stream", "models", None, "#model-detail-download-btn", 0.20),
    ("dx_stream", "models", None, ".download-model-btn", 0.25),
    ("dx_stream", "setup", None, "#setup-env-tbody", 0.25),
]

APP_EXPORT_STEP = None
APP_CART_STEP = None
APP_LIGHTBOX_STEP = None
STREAM_TOAST_STEP = None
STREAM_PIPELINE_STEP = None
STREAM_PALETTE_STEP = None
STREAM_MODAL_STEP = None
STREAM_DL_BTN_STEP = None
STREAM_INDIV_DL_STEP = None
STREAM_ENV_STEP = None


def _resolve_step_indices():
    global APP_EXPORT_STEP, APP_CART_STEP, APP_LIGHTBOX_STEP
    global STREAM_TOAST_STEP, STREAM_PIPELINE_STEP, STREAM_PALETTE_STEP
    global STREAM_MODAL_STEP, STREAM_DL_BTN_STEP, STREAM_INDIV_DL_STEP, STREAM_ENV_STEP
    from pathlib import Path
    import re

    app_src = (Path(__file__).resolve().parents[1] / "dx_app/static/js/tutorial.js").read_text()
    stream_src = (Path(__file__).resolve().parents[1] / "dx_stream/static/js/tutorial.js").read_text()

    def idx(src: str, section: str, target: str) -> int:
        sec = re.search(rf"id:\s*'{section}'[\s\S]*?steps:\s*\[([\s\S]*?)\n\s*\]", src)
        assert sec, section
        steps = re.findall(r"target:\s*'([^']+)'", sec.group(1))
        return steps.index(target)

    APP_EXPORT_STEP = idx(app_src, "run-single", "#r-export-btn")
    APP_CART_STEP = idx(app_src, "modelzoo", "#mz-cart")
    APP_LIGHTBOX_STEP = idx(app_src, "outputs", "#gallery-lightbox")
    STREAM_TOAST_STEP = idx(stream_src, "global", "#dxt-mock-stream-toast")
    STREAM_PIPELINE_STEP = idx(stream_src, "demo", "#demo-pipeline-info")
    STREAM_PALETTE_STEP = idx(stream_src, "pipeline", ".palette-item")
    STREAM_MODAL_STEP = idx(stream_src, "models", "#model-detail-modal")
    STREAM_DL_BTN_STEP = idx(stream_src, "models", "#model-detail-download-btn")
    STREAM_INDIV_DL_STEP = idx(stream_src, "models", "#dxt-stream-mock-download-btn")
    STREAM_ENV_STEP = idx(stream_src, "setup", "#setup-env-tbody")


_resolve_step_indices()

RESOLVED_CHECKS = [
    ("dx_app", "global", 5, "#dxt-mock-toast", 0.35),
    ("dx_app", "run-single", APP_EXPORT_STEP, "#r-export-btn", 0.25),
    ("dx_app", "modelzoo", APP_CART_STEP, "#mz-cart", 0.25),
    ("dx_app", "outputs", APP_LIGHTBOX_STEP, "#gallery-lightbox", 0.20),
    ("dx_stream", "global", STREAM_TOAST_STEP, "#dxt-mock-stream-toast", 0.35),
    ("dx_stream", "demo", STREAM_PIPELINE_STEP, "#demo-pipeline-info", 0.25),
    ("dx_stream", "pipeline", STREAM_PALETTE_STEP, ".palette-item", 0.20),
    ("dx_stream", "models", STREAM_MODAL_STEP, "#model-detail-modal", 0.15),
    ("dx_stream", "models", STREAM_DL_BTN_STEP, "#model-detail-download-btn", 0.20),
    ("dx_stream", "models", STREAM_INDIV_DL_STEP, "#dxt-stream-mock-download-btn", 0.25),
    ("dx_stream", "setup", STREAM_ENV_STEP, "#setup-env-tbody", 0.25),
]


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


@pytest.fixture()
def page(browser):
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    pg = ctx.new_page()
    try:
        yield pg
    finally:
        pg.close()
        ctx.close()


@pytest.mark.parametrize(
    "server_name,section,step_idx,selector,min_overlap",
    RESOLVED_CHECKS,
    ids=[f"{m[0]}:{m[1]}:{m[3]}" for m in RESOLVED_CHECKS],
)
def test_tutorial_spotlight_alignment(page, server_name, section, step_idx, selector, min_overlap):
    server, port = start_module_server(server_name)
    try:
        setup = "() => { const d = document.getElementById('dx-input-modal'); if (d && d.open) d.close(); }" if server_name == "dx_stream" else "() => {}"
        page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=60000)
        page.evaluate(setup)
        page.wait_for_selector("#dxToolbar", timeout=30000)
        page.wait_for_function("() => window._dxTutorial", timeout=30000)
        page.evaluate("() => window._dxTutorial.resetProgress()")
        page.evaluate(GOTO_STEP_JS, [section, step_idx])
        page.wait_for_timeout(600)
        m = page.evaluate(ALIGN_JS)

        assert m.get("hasTarget"), f"{server_name} {section} step {step_idx}: target {selector!r} missing"
        assert m.get("targetVisible"), f"{server_name} {section} step {step_idx}: target {selector!r} zero bbox {m.get('targetRect')}"
        assert m.get("spotlightActive"), f"{server_name} {section} step {step_idx}: no active spotlight"
        assert not m.get("floating"), f"{server_name} {section} step {step_idx}: floating fallback for {selector!r}"
        assert m.get("overlap", 0) >= min_overlap, (
            f"{server_name} {section} step {step_idx}: spotlight overlap {m.get('overlap'):.2f} < {min_overlap} "
            f"target={m.get('targetRect')} spotlight={m.get('spotlightRect')}"
        )

        if selector == "#gallery-lightbox":
            assert m.get("targetVisible"), "lightbox should be visible for preview step"
        if selector == "#model-detail-modal":
            assert m.get("targetVisible"), "model detail modal should be visible"
    finally:
        server.shutdown()
