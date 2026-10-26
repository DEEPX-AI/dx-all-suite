"""The intro's second and third working scenes.

App: a line of light sweeps top to bottom over real drive footage, the area it passes turns into the segmentation
a DX-M1 produced, and playback continues. Compiler: the real 384-node graph of Ultralytics YOLO26n spreads out and
is drawn into the DX-M1 chip. All three scenes use the full screen, so there is no card (.cue-scene).
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_FRESH = "try{sessionStorage.removeItem('dx-splash-seen');localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}"


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


@pytest.fixture(scope="module")
def port():
    server, port = start_module_server("launcher")
    yield port
    server.shutdown()


def _open(browser, port, block=None):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script(_FRESH)
    if block:
        ctx.route(block, lambda route: route.abort())
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=60000)
    return ctx, page


def _answer(page):
    return page.evaluate("document.getElementById('splashCueAnswer').textContent")


def test_the_app_beat_reveals_the_segmentation_and_plays_it(browser, port):
    ctx, page = _open(browser, port)
    try:
        page.wait_for_selector(".intro-app.is-on", state="attached", timeout=25000)
        assert page.evaluate("document.getElementById('splashOverlay').classList.contains('is-scene')")
        assert not page.evaluate("!!document.querySelector('.cue-scene')"), "옛 card 가 남아 있다"
        page.wait_for_selector(".intro-app.is-revealed", state="attached", timeout=5000)
        page.wait_for_timeout(900)
        got = page.evaluate("""(() => { const v = document.querySelector('.intro-app video');
          return { t: v.currentTime, err: !!v.error, shown: getComputedStyle(v).opacity === '1',
                   still: getComputedStyle(document.querySelector('.iap-seg')).backgroundImage }; })()""")
        assert "seg-first.webp" in got["still"], "영상 밑에는 늘 정지 mask 그림이 깔린다"
        if got["err"]:
            assert not got["shown"], "decode 가 실패한 영상은 정지 그림을 덮으면 안 된다"
        else:
            assert got["t"] > 0 and got["shown"], got
        page.wait_for_function("document.getElementById('splashCueText').textContent === 'segment a video file'",
                               timeout=5000)
        page.wait_for_function("document.getElementById('splashCueAnswer').textContent.startsWith('App')",
                               timeout=5000)
        assert _answer(page) == "App · segformer · 200 fps on one DX-M1"
    finally:
        ctx.close()


def test_the_compiler_beat_draws_the_real_graph_into_the_chip(browser, port):
    ctx, page = _open(browser, port)
    try:
        page.wait_for_selector(".intro-compile.is-on", state="attached", timeout=30000)
        assert page.evaluate("document.querySelector('.intro-compile canvas').dataset.nodes") == "384"
        page.wait_for_selector(".intro-compile.is-forged", state="attached", timeout=5000)
        chip = page.evaluate("(() => { const r = document.querySelector('.icp-chip').getBoundingClientRect();"
                             " return [r.width, r.height]; })()")
        assert chip[0] > 100 and chip[1] > 100, chip
        page.wait_for_function("document.getElementById('splashCueAnswer').textContent.startsWith('Compiler')",
                               timeout=5000)
        assert _answer(page) == "Compiler · yolo26n → DXNN · 212 fps on DX-M1"
    finally:
        ctx.close()


def test_without_their_material_the_beats_are_the_prompts_alone(browser, port):
    ctx, page = _open(browser, port, block="**/img/intro/{app,compile}/**")
    try:
        page.wait_for_function("document.getElementById('splashCueText').textContent === 'segment a video file'",
                               timeout=25000)
        assert not page.evaluate("!!document.querySelector('.intro-app.is-on')")
        page.wait_for_function("document.getElementById('splashCueText').textContent === 'compile yolo26n to DXNN'",
                               timeout=12000)
        assert not page.evaluate("!!document.querySelector('.intro-compile.is-on')")
    finally:
        ctx.close()
