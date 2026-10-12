"""Shared demo stage, cards and filter.

App Run Demo and the Stream Demo Launcher use the same component: a result stage at the top of the page (media on
the left, panel on the right), with the filter and the cards to choose from below it. These tests check that the
component itself keeps those promises, independent of any module.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

PAGE = """<!doctype html><html data-theme="light"><head><meta charset="utf-8">
<link rel="stylesheet" href="/static/shared/dx-tokens.css"><link rel="stylesheet" href="/static/shared/dx-semantic.css">
<link rel="stylesheet" href="/static/shared/dx-theme-light.css"><link rel="stylesheet" href="/static/shared/dx-base.css">
<link rel="stylesheet" href="/static/shared/dx-components.css"><link rel="stylesheet" href="/static/shared/dx-demo-stage.css">
<script src="/static/shared/dx-icon.js"></script><script src="/static/shared/dx-demo-stage.js"></script>
</head><body style="margin:0;padding:24px"><h1 style="margin:0 0 12px">Run Demo</h1><div id="root"></div></body></html>"""

ITEMS = """[
  {id: 'a', title: 'YOLOv7', category: 'detection', task: {icon: 'task-object_detection', label: 'Object Detection'},
   ready: false, reason: 'Model not installed', reasonTitle: 'Model not installed: yolov7.dxnn', thumb: ''},
  {id: 'b', title: 'YOLO26N-OBB', category: 'detection', task: {icon: 'task-obb_detection', label: 'OBB Detection'},
   ready: true, sub: 'yolo26-n-obb_1024x1024.dxnn', thumb: ''},
  {id: 'c', title: 'YOLOv8s-Pose', category: 'pose', task: {icon: 'task-pose_estimation', label: 'Pose Estimation'},
   ready: true, sub: 'yolov8s-pose.dxnn', thumb: ''}
]"""


@pytest.fixture(scope="module")
def port():
    server, port = start_module_server("launcher")
    yield port
    server.shutdown()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _page(browser, port, items=ITEMS, width=1440, height=900):
    page = browser.new_page(viewport={"width": width, "height": height})
    page.route(f"http://127.0.0.1:{port}/__stage", lambda r: r.fulfill(status=200, content_type="text/html", body=PAGE))
    page.goto(f"http://127.0.0.1:{port}/__stage", wait_until="load")
    page.evaluate(f"""() => {{
      window.__picked = []; window.__setup = 0;
      window.__stage = DXDemoStage.mount(document.getElementById('root'), {{
        items: {items},
        filters: [{{key: 'all', label: 'All'}}, {{key: 'detection', label: 'Detection'}}, {{key: 'pose', label: 'Pose'}}],
        labels: {{setup: 'Set up', none: 'Install a model in Setup to run a demo.', ready: 'Ready',
                  running: 'Running', unready: 'Needs setup'}},
        onSelect: (item, stage) => {{ window.__picked.push(item.id);
          stage.opts.innerHTML = '<div class="probe-opts">opts for ' + item.id + '</div>'; }},
        onSetup: () => {{ window.__setup += 1; }},
      }});
    }}""")
    return page


def test_the_first_ready_demo_opens_on_the_stage(browser, port):
    page = _page(browser, port)
    try:
        assert page.evaluate("window.__picked") == ["b"]
        assert page.inner_text(".dds-stage .dds-title") == "YOLO26N-OBB"
        assert page.inner_text(".dds-stage .probe-opts") == "opts for b"
        assert page.evaluate("document.querySelector('.dds-card[data-id=\"b\"]').classList.contains('is-selected')")
    finally:
        page.close()


def test_a_card_opens_its_demo_on_the_stage(browser, port):
    page = _page(browser, port)
    try:
        page.click(".dds-card[data-id='c']")
        assert page.inner_text(".dds-stage .dds-title") == "YOLOv8s-Pose"
        assert page.evaluate("window.__picked") == ["b", "c"]
        assert page.locator(".dds-card.is-selected").count() == 1
    finally:
        page.close()


def test_a_card_is_for_choosing_only(browser, port):
    """Options and Run live on the stage — a card has no buttons (except Set up on a card that is not ready)."""
    page = _page(browser, port)
    try:
        assert page.locator(".dds-card[data-id='b'] button:not(.dds-cpick)").count() == 0
        assert page.locator(".dds-card[data-id='a'] button:not(.dds-cpick)").count() == 1
        heights = page.evaluate("[...document.querySelectorAll('.dds-card')].map(c => Math.round(c.getBoundingClientRect().height))")
        assert len(set(heights)) == 1, f"card 높이가 같아야 한다: {heights}"
    finally:
        page.close()


def test_a_card_is_chosen_from_the_keyboard_without_a_button_inside_a_button(browser, port):
    """A card must not be role=button with the not-ready card's Set up inside it (axe: nested-interactive).
    A hidden .dds-cpick button does the choosing from the keyboard; the card draws its focus ring."""
    page = _page(browser, port)
    try:
        assert page.locator(".dds-card[role], .dds-card[tabindex]").count() == 0
        assert page.locator("[role=button] button, button button").count() == 0
        page.focus(".dds-card[data-id='c'] .dds-cpick")
        page.keyboard.press("Enter")
        assert page.evaluate("document.querySelector('.dds-card[data-id=\"c\"]').classList.contains('is-selected')")
        assert page.get_attribute(".dds-card[data-id='c'] .dds-cpick", "aria-pressed") == "true"
        assert page.get_attribute(".dds-card[data-id='b'] .dds-cpick", "aria-pressed") == "false"
        page.keyboard.press("Shift+Tab")
        page.keyboard.press("Tab")
        ring = page.evaluate("getComputedStyle(document.querySelector('.dds-card[data-id=\"c\"]')).outlineStyle")
        assert ring == "solid", ring
        assert page.inner_text(".dds-card[data-id='c'] .dds-cpick").strip() == \
            page.inner_text(".dds-card[data-id='c'] .dds-ctitle").strip()
    finally:
        page.close()


def test_a_not_ready_card_gives_one_short_reason(browser, port):
    page = _page(browser, port)
    try:
        reason = page.locator(".dds-card[data-id='a'] .dds-reason")
        assert reason.inner_text() == "Model not installed"
        assert reason.get_attribute("title") == "Model not installed: yolov7.dxnn"
        page.click(".dds-card[data-id='a'] .dds-setup")
        assert page.evaluate("window.__setup") == 1
        assert page.inner_text(".dds-stage .dds-title") != "YOLOv7", "Set up 은 card 를 고르지 않는다"
    finally:
        page.close()


def test_filters_narrow_the_cards(browser, port):
    page = _page(browser, port)
    try:
        page.click(".dds-filter button[data-key='pose']")
        visible = page.evaluate("[...document.querySelectorAll('.dds-card')].filter(c => c.offsetParent).map(c => c.dataset.id)")
        assert visible == ["c"]
        page.click(".dds-filter button[data-key='all']")
        assert page.evaluate("[...document.querySelectorAll('.dds-card')].filter(c => c.offsetParent).length") == 3
    finally:
        page.close()


def test_with_nothing_ready_the_stage_says_how_to_start(browser, port):
    page = _page(browser, port, items="[{id: 'a', title: 'YOLOv7', category: 'detection', ready: false, reason: 'Model not installed'}]")
    try:
        assert page.evaluate("window.__picked") == []
        assert "Install a model in Setup" in page.inner_text(".dds-stage")
        page.click(".dds-stage .dds-none button")
        assert page.evaluate("window.__setup") == 1
    finally:
        page.close()


def test_the_stage_and_the_first_card_row_fit_one_screen(browser, port):
    page = _page(browser, port)
    try:
        top = page.evaluate("document.querySelector('.dds-card').getBoundingClientRect().top")
        assert top < 900 - 60, f"1440×900 에서 card 첫 줄이 보여야 한다 (top {top:.0f})"
        m = page.evaluate("(() => { const b = document.querySelector('.dds-media').getBoundingClientRect(); return b.width / b.height; })()")
        assert abs(m - 16 / 9) < 0.02, m
    finally:
        page.close()


def test_on_a_narrow_screen_the_panel_goes_under_the_media(browser, port):
    page = _page(browser, port, width=900, height=1000)
    try:
        media, side = page.evaluate("""() => ['.dds-media', '.dds-side'].map(s => {
          const b = document.querySelector(s).getBoundingClientRect(); return [b.top, b.bottom]; })""")
        assert side[0] >= media[1] - 1, (media, side)
    finally:
        page.close()


def test_metrics_and_stage_bars_render(browser, port):
    page = _page(browser, port)
    try:
        page.evaluate("""() => { __stage.stage.setMetrics([{value: '2.8', label: 'FPS', accent: true},
            {value: '56 ms', label: 'NPU latency'}, {value: '0.93 s', label: 'Total'}]);
          __stage.stage.setBars([{label: 'Read', ms: 202}, {label: 'Pre', ms: 16}, {label: 'Infer', ms: 57}, {label: 'Post', ms: 0}]);
          __stage.stage.setState('done', 'Done'); }""")
        assert page.locator(".dds-metric").count() == 3
        assert page.inner_text(".dds-metric >> nth=0") .startswith("2.8")
        assert page.locator(".dds-bars .dds-bar i").count() == 4
        assert "Infer" in page.inner_text(".dds-bars")
        assert page.evaluate("document.querySelector('.dds-state').dataset.kind") == "done"
    finally:
        page.close()


def test_many_filters_stay_on_one_line(browser, port):
    """Many groups still fit the filter on one line — wrapping to two lines pushes the first card row off screen."""
    many = "[" + ",".join(f"{{id: 'm{i}', title: 'M{i}', category: 'group_{i}', task: {{label: 'Task'}}, ready: true}}"
                          for i in range(14)) + "]"
    page = _page(browser, port, items=many)
    try:
        page.evaluate("""() => { const f = document.querySelector('.dds-filter');
          ['Detection','Pose & Landmark','Segmentation','Classification','Depth Estimation','Image Restoration',
           'Recognition','PPU','Keypoint & Pose','Driving & 3D','Hand Detection','Retrieval & Matting','More'].forEach(t => {
             const b = document.createElement('button'); b.className = 'dds-fbtn'; b.textContent = t; f.appendChild(b); }); }""")
        tops = page.evaluate("[...new Set([...document.querySelectorAll('.dds-filter button')].map(b => Math.round(b.getBoundingClientRect().top)))]")
        assert len(tops) == 1, tops
    finally:
        page.close()
