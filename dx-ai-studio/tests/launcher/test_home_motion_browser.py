"""Home's continuous effects: they run, they stop when they should, and they are not heavy.

Device and catalog are pinned with fixtures (same reason as test_home_widgets_browser.py).
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_SEEN = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
         "localStorage.setItem('dx-tutorial-launcher-autostarted','1');"
         "localStorage.setItem('dx-tutorial-mode','off');}catch(e){}")
FIRST = "Build a squat-counting fitness mini-game using yolo26n-pose on DEEPX NPU"
SECOND = "Build an OCR inference app whose text detection + recognition runs on the DEEPX DX-M1 NPU."


def _hw(util):
    return {"available": True, "count": 1, "npus": [{
        "id": 0, "cores": 3, "temperatures": [41.0] * 3, "temp_avg": 41.0,
        "clock_avg": 1000.0, "power_est_mW": 375.0, "utilization": util}]}


CATALOG = {"models": [{"id": "yolo26n", "name": "yolo26n", "display": {"task": "object_detection"},
                       "performance": {"fps": 321}}]}


@pytest.fixture(scope="module")
def server():
    srv, port = start_module_server("launcher")
    yield port
    srv.shutdown()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _open(browser, port, *, still=False, hw=None, width=1440, height=900, fx="full"):
    """fx: effect level. Headless has no GPU, so the default is 'lite' (cursor light off). Tests that look at the
    light turn on 'full'; the budget test uses the default (None)."""
    ctx = browser.new_context(viewport={"width": width, "height": height},
                              reduced_motion="reduce" if still else "no-preference")
    ctx.add_init_script(_SEEN + (f"try{{localStorage.setItem('dx-fx','{fx}');}}catch(e){{}}" if fx else ""))
    page = ctx.new_page()
    page.route("**/dx_monitor/api/hw_stream", lambda route, *_: route.abort())
    page.route("**/dx_monitor/api/hw_status", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(hw or _hw([10.0, 55.0, 90.0]))))
    page.route("**/zoo/api/catalog", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(CATALOG)))
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.wait_for_selector("#studioGrid .orbital-card", state="visible")
    return ctx, page


def _samples(page, ms, every=60, expr="() => document.getElementById('homeAsk').placeholder"):
    return page.evaluate(f"""() => new Promise(done => {{
      const out = [], read = {expr};
      const t = setInterval(() => out.push(read()), {every});
      setTimeout(() => {{ clearInterval(t); done(out); }}, {ms});
    }})""")


# ── placeholder ───────────────────────────────────────────────────────────

def test_the_placeholder_erases_and_types_the_next_request(browser, server):
    ctx, page = _open(browser, server)
    try:
        seen = _samples(page, 7000)
        assert seen[0] == FIRST, seen[0]
        assert any(0 < len(s) < len(FIRST) and FIRST.startswith(s) for s in seen), "지우지 않았다"
        assert any(len(s) > 8 and SECOND.startswith(s) for s in seen), "다음 문장을 치지 않았다"
    finally:
        ctx.close()


def test_focus_stops_the_typing_and_clears_it(browser, server):
    ctx, page = _open(browser, server)
    try:
        page.wait_for_timeout(2500)
        page.focus("#homeAsk")
        seen = _samples(page, 1200)
        assert set(seen) == {""}, set(seen)
    finally:
        ctx.close()


def test_reduced_motion_leaves_the_first_request_standing(browser, server):
    ctx, page = _open(browser, server, still=True)
    try:
        assert set(_samples(page, 3000)) == {FIRST}
    finally:
        ctx.close()


def test_the_typing_speaks_the_ui_language(browser, server):
    ctx, page = _open(browser, server)
    try:
        page.evaluate("() => DXI18n.setLang('ko')")
        seen = _samples(page, 6000)
        assert not any(s.startswith("Build an OCR") for s in seen), "한국어 화면에서 영어를 친다"
        assert any(s and not s.isascii() for s in seen), seen[-5:]
    finally:
        ctx.close()


# ── core bars ─────────────────────────────────────────────────────────────

def test_core_bars_ease_toward_the_new_value(browser, server):
    ctx, page = _open(browser, server)
    try:
        page.wait_for_function("() => document.querySelectorAll('#homeCores .dev-core').length === 3", timeout=8000)
        t = page.evaluate("() => getComputedStyle(document.querySelector('#homeCores .dev-core i')).transition")
        assert "transform 0.3s" in t, t
        page.wait_for_timeout(500)
        h = page.evaluate("() => [...document.querySelectorAll('#homeCores .dev-core i')].map(e => e.getBoundingClientRect().height)")
        assert h[0] < h[1] < h[2] and abs(h[2] / h[1] - 90 / 55) < 0.15, h
    finally:
        ctx.close()


def test_an_idle_device_breathes(browser, server):
    ctx, page = _open(browser, server, hw=_hw([0.0, 1.0, 0.0]))
    try:
        page.wait_for_function("() => document.getElementById('homeDevice').classList.contains('is-idle')", timeout=8000)
        name = page.evaluate("() => getComputedStyle(document.querySelector('#homeCores .dev-core i')).animationName")
        assert name == "dev-breathe"
    finally:
        ctx.close()


def test_a_busy_device_does_not_breathe(browser, server):
    ctx, page = _open(browser, server)
    try:
        page.wait_for_function("() => document.querySelectorAll('#homeCores .dev-core').length === 3", timeout=8000)
        assert not page.evaluate("() => document.getElementById('homeDevice').classList.contains('is-idle')")
    finally:
        ctx.close()


# ── count-up ──────────────────────────────────────────────────────────────

def test_the_headline_counts_up_to_the_measured_value(browser, server):
    ctx, page = _open(browser, server)
    try:
        page.wait_for_function("() => document.getElementById('homeProofFps').textContent.trim() !== ''", timeout=8000)
        seen = _samples(page, 1100, every=40, expr="() => document.getElementById('homeProofFps').textContent.trim()")
        nums = [int(s.replace(",", "")) for s in seen if s]
        assert nums[-1] == 321, nums
        assert nums[0] < 321, f"처음부터 끝 값이었다: {nums[:5]}"
        assert nums == sorted(nums), "거꾸로 셌다"
    finally:
        ctx.close()


def test_reduced_motion_shows_the_value_at_once(browser, server):
    ctx, page = _open(browser, server, still=True)
    try:
        page.wait_for_function("() => document.getElementById('homeProofFps').textContent.trim() !== ''", timeout=8000)
        assert page.inner_text("#homeProofFps").strip() == "321"
    finally:
        ctx.close()


# ── cursor light ──────────────────────────────────────────────────────────

def _light(page):
    return page.evaluate("""() => { const i = document.querySelector('#landing .stage-light > i');
      const r = i.getBoundingClientRect();
      return {x: r.left + r.width / 2, y: r.top + r.height / 2, o: parseFloat(getComputedStyle(i).opacity)}; }""")


def test_the_light_follows_the_cursor(browser, server):
    ctx, page = _open(browser, server)
    try:
        assert _light(page)["o"] == 0, "움직이기 전부터 켜져 있다"
        # Wait until the stage's entry translateY (animateIn) ends; a position measured during it lasts until the next move.
        page.wait_for_function("() => { const l = document.getElementById('landing');"
                               " return l.getAnimations().every(a => a.playState !== 'running'); }", timeout=3000)
        page.mouse.move(400, 300)
        page.mouse.move(420, 320)
        page.wait_for_timeout(600)
        light = _light(page)
        assert abs(light["x"] - 420) <= 4 and abs(light["y"] - 320) <= 4, light
        assert light["o"] > 0.5
        # The layer clips, so if it does not cover the stage the light is invisible even when correctly placed
        # (a zero-height layer, from .landing's align-items: center, passes a position-and-opacity check).
        wrap = page.evaluate("""() => { const r = document.querySelector('#landing .stage-light').getBoundingClientRect();
          return [r.left, r.top, r.right, r.bottom]; }""")
        assert wrap[0] <= 0 and wrap[1] <= 44 and wrap[2] >= 1440 and wrap[3] >= 900 - 12, f"빛의 층이 무대를 덮지 않는다: {wrap}"
    finally:
        ctx.close()


def test_the_light_never_makes_the_page_scroll(browser, server):
    ctx, page = _open(browser, server, width=1280, height=800)
    try:
        for x, y in ((1275, 795), (5, 795), (1275, 60)):
            page.mouse.move(x, y)
            page.wait_for_timeout(150)
            size = page.evaluate("() => [document.scrollingElement.scrollWidth, document.scrollingElement.scrollHeight]")
            assert size == [1280, 800], (x, y, size)
    finally:
        ctx.close()


def test_without_gpu_the_light_stays_off(browser, server):
    """Headless Chromium is a software rasterizer, so at the default level the cursor light does not turn on."""
    ctx, page = _open(browser, server, fx=None)
    try:
        page.mouse.move(400, 300)
        page.mouse.move(420, 320)
        page.wait_for_timeout(300)
        assert _light(page)["o"] == 0
    finally:
        ctx.close()


def test_reduced_motion_keeps_the_light_off(browser, server):
    ctx, page = _open(browser, server, still=True)
    try:
        page.mouse.move(400, 300)
        page.mouse.move(420, 320)
        page.wait_for_timeout(300)
        assert _light(page)["o"] == 0
    finally:
        ctx.close()


# ── budget ────────────────────────────────────────────────────────────────

def test_everything_running_at_once_leaves_no_long_frame(browser, server):
    """Cursor movement + placeholder + widgets running together: no long frame (>50 ms) in 5 s.
    Measured at this machine's default level (fx=None); without a GPU the cursor light stays off."""
    ctx, page = _open(browser, server, fx=None)
    try:
        page.wait_for_timeout(1000)   # measure only after the first paint
        page.evaluate("""() => { window.__long = [];
          const type = PerformanceObserver.supportedEntryTypes.includes('long-animation-frame')
            ? 'long-animation-frame' : 'longtask';
          new PerformanceObserver(l => l.getEntries().forEach(e => { if (e.duration > 50) window.__long.push(e.duration); }))
            .observe({type}); }""")
        for i in range(50):
            page.mouse.move(200 + (i * 23) % 1000, 150 + (i * 37) % 600, steps=4)
            page.wait_for_timeout(100)
        assert page.evaluate("() => window.__long") == []
    finally:
        ctx.close()
