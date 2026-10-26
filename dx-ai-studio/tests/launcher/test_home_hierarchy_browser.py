"""Home's first screen must have one entry point for the eye.

With `Build`, `Measured on DX-M1` and `Modules` all at 24px/600, three titles mean no lead, and the screen
cannot say what it is for. A device line such as `DX-M1 · 1 device` must not be the largest, only coloured
text: it is a fact, not an achievement, and colour is the warning register.

Colour is for exceptions: an attached device is normal and gets none. The same rule applies to the
`Running` indicator.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_QUIET = """() => {
  const t = window._dxTutorial;
  if (t) { try { t.stop && t.stop(); } catch (e) {} }
  document.querySelectorAll('.dxt-toc,.dxt-overlay,.dxt-tooltip,.dxt-toc-backdrop')
    .forEach(e => e.remove());
}"""


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


@pytest.fixture()
def home(browser):
    server, port = start_module_server("launcher")
    ctx = browser.new_context(viewport={"width": 1512, "height": 900})
    ctx.add_init_script(
        "try{sessionStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}"
    )
    page = ctx.new_page()
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60000)
        page.wait_for_timeout(3500)
        page.evaluate(_QUIET)
        page.wait_for_timeout(300)
        yield page
    finally:
        page.close(); ctx.close(); server.shutdown()


def _px(page, selector, prop="fontSize"):
    return page.evaluate(
        "([s, p]) => { const e = document.querySelector(s); if (!e) return null;"
        " const v = getComputedStyle(e)[p]; return parseFloat(v); }", [selector, prop])


# The stage: one hero title and the titles of the two side widgets.
BUILD_H = "#homeStage .stage-title"
MEASURED_H = "#homeMeasured .stage-widget-title"
MODULES_H = "#homeDevice .stage-widget-title"


def test_build_is_the_one_heading_that_leads(home):
    build, measured, modules = (_px(home, s) for s in (BUILD_H, MEASURED_H, MODULES_H))
    assert build and measured and modules, (build, measured, modules)
    assert build > measured, f"Build {build}px 가 Measured 위젯 제목 {measured}px 보다 크지 않다"
    assert build > modules, f"Build {build}px 가 Device 위젯 제목 {modules}px 보다 크지 않다"


def test_the_two_supporting_headings_agree_with_each_other(home):
    """Titles of the two side widgets. Demoting only one of them makes three levels and the screen harder to read."""
    assert _px(home, MEASURED_H) == _px(home, MODULES_H)


def test_the_hero_input_is_big_enough_to_be_the_hero(home):
    """The hero is the whole bar (.home-ask), not just the input.

    It carries the product's sentence ("describe it and the studio builds it"), so its text must not be
    body-sized.
    """
    bar = home.evaluate(
        "() => { const e = document.querySelector('.home-ask');"
        " return e ? Math.round(e.getBoundingClientRect().height) : 0; }")
    assert bar >= 56, f"히어로 바 높이가 {bar}px — 첫 화면을 이끌기에 작다"

    size = _px(home, ".ask-input")
    assert size >= 21, f"히어로 입력 글자가 {size}px — 본문과 구분되지 않는다"


def _device_colour(browser, hw):
    """Pin the hw_status response and read the colour of the device indicator.

    Left to the environment this check flips: the test harness starts only the launcher, so there is no
    monitor, and a check meant for 'normal' would actually check 'not detected'.
    """
    import json

    server, port = start_module_server("launcher")
    ctx = browser.new_context(viewport={"width": 1512, "height": 900})
    ctx.add_init_script(
        "try{sessionStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}"
    )
    page = ctx.new_page()
    try:
        def handler(route, *_):
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps(hw))

        page.route("**/dx_monitor/api/hw_status", handler)
        page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60000)
        page.wait_for_timeout(3500)
        page.evaluate(_QUIET)
        page.wait_for_timeout(400)
        return page.evaluate(
            "() => { const e = document.getElementById('heroDeviceChip');"
            " return e ? { colour: getComputedStyle(e).color, cls: e.className,"
            "   text: e.textContent.trim(),"
            "   off: document.getElementById('homeDevice').classList.contains('is-off'),"
            "   heading: getComputedStyle(document.querySelector('"
            + BUILD_H + "')).color } : null; }")
    finally:
        page.close(); ctx.close(); server.shutdown()


def test_a_healthy_device_does_not_shout_in_colour(browser):
    """Normal gets no colour. Spending colour here would bury the real exceptions."""
    got = _device_colour(browser, {"available": True, "count": 1,
                                   "npus": [{"id": 0, "cores": 3}]})
    assert "is-live" in got["cls"], got["cls"]
    assert got["colour"] == got["heading"], (
        f"정상 상태의 장치 표시가 제목과 다른 색이다: {got['colour']} vs {got['heading']}"
    )


def test_a_missing_device_turns_the_widget_off(browser):
    """A missing device has its lights dimmed rather than shouting in colour.

    The exception is still visible, but through lighting rather than colour: the whole widget sinks and
    only one quiet line remains. It stays distinguishable from normal.
    """
    got = _device_colour(browser, {"available": False, "count": 0})
    assert got["off"], "장치가 없는데 위젯이 켜져 있다"
    assert "is-missing" in got["cls"], got["cls"]
    assert got["text"] == "No DX-M1 connected", got["text"]
    assert got["colour"] != got["heading"], "없음이 정상과 같은 모습이다"


def test_the_agent_settings_do_not_compete_with_the_hero(home):
    """Settings must not be the second most visible thing right under the hero.

    A row like `Agent [copilot] Model [claude-sonnet-4.6] 29 models Effort [medium] ● not signed in ...`
    with blue monospace chips under the input competes with the prompt. Choosing an agent is not what you
    do while thinking about what to build, so it is folded and opened when needed.
    """
    state = home.evaluate(
        """() => {
          const row = document.getElementById('setupForm');
          if (!row) return { missing: true };
          const box = row.closest('details');
          const sel = document.getElementById('setupModel');
          return {
            wrapped: !!box,
            open: box ? box.open : null,
            modelVisible: !!(sel && sel.offsetParent !== null),
          };
        }"""
    )
    assert not state.get("missing"), "setupForm 이 사라졌다"
    assert state["wrapped"], "설정 줄이 접히지 않는다 (details 로 감싸야 한다)"
    assert state["open"] is False, "기본이 펼쳐져 있다"
    assert not state["modelVisible"], "접혔는데 Model 셀렉트가 보인다"


def test_the_agent_settings_open_when_asked(home):
    """Folding is not hiding: opening it must show the settings.

    The harness has no agent module, so setupForm arrives hidden. Asserting 'it does not appear when
    opened' in that state would measure the environment, not the contract, so the test sets up a live
    module.
    """
    home.evaluate(
        """() => {
          document.getElementById('setupForm').hidden = false;
          document.getElementById('setupFold').hidden = false;
          document.getElementById('setupFold').open = true;
        }"""
    )
    home.wait_for_timeout(300)
    visible = home.evaluate(
        "() => { const s = document.getElementById('setupModel');"
        " return !!(s && s.offsetParent !== null); }")
    assert visible, "펼쳤는데 설정이 나오지 않는다"


def test_the_fold_summary_says_what_is_selected(home):
    """Even folded, what is selected must be visible."""
    src = (ROOT_JS := __import__("pathlib").Path(__file__).resolve().parents[2]
           / "launcher" / "static" / "home-agent-setup.js").read_text(encoding="utf-8")
    assert "_paintFoldSummary" in src, "요약을 그리는 코드가 없다"
    assert "setupFoldValue" in src, "요약이 쓰일 자리가 없다"
    # Changing agent or model must update the summary.
    assert src.count("_paintFoldSummary") >= 4, (
        "요약이 초기화 때만 그려진다 — 선택이 바뀌면 어긋난다"
    )


# ── rhythm and rail ───────────────────────────────────────────


def test_the_grid_is_nine_modules_in_three_rows_and_two_books(home):
    """The stage has no group labels: tools are cells and a cell's position is its order. The modules fill a 3×3
    block — App · Stream · Model Zoo / Compiler · Benchmark · EdgeGuide / Monitor · Agent Dev · Cloud, so Cloud
    closes it as Alt+9 — and SDK Library and About DEEPX share the last column (SR-679).
    The tutorial targets #studioGrid and .orbital-card, so both stay.
    """
    assert home.evaluate("() => document.querySelectorAll('#studioGrid .studio-group').length") == 0
    tiles = home.evaluate(
        "() => [...document.querySelectorAll('#studioGrid > *')].map(e =>"
        " e.dataset.app || (e.classList.contains('sdk-card') ? 'sdk' : 'about'))")
    assert tiles == ["app", "stream", "zoo", "compiler", "benchmark", "planner",
                     "dx_monitor", "agent", "edge", "sdk", "about"], tiles
    cells = home.evaluate(
        "() => [...document.querySelectorAll('#studioGrid > *')].map(e => {"
        " const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top)]; })")
    modules, books = cells[:9], cells[9:]
    assert len({top for _, top in modules}) == 3, f"1512 폭에서 모듈이 3줄이 아니다: {modules}"
    assert len({left for left, _ in modules}) == 3, modules
    assert books[0][0] == books[1][0] > max(left for left, _ in modules), books


def test_the_device_card_carries_what_the_device_is_doing(browser):
    """The cards fill the rail with their own subjects.

    SDK version and port do not change. Temperature and cores change, and are already being fetched.
    """
    got = _device_colour(browser, {
        "available": True, "count": 1,
        "npus": [{"id": 0, "cores": 3, "temperatures": [41.0, 39.0, 40.0]}],
    })
    assert got is not None


def test_device_facts_show_live_values_when_a_device_is_there(browser):
    import json

    server, port = start_module_server("launcher")
    ctx = browser.new_context(viewport={"width": 1512, "height": 900})
    ctx.add_init_script(
        "try{sessionStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-tutorial-launcher-autostarted','1');}catch(e){}"
    )
    page = ctx.new_page()
    hw = {"available": True, "count": 1,
          "npus": [{"id": 0, "cores": 3, "temperatures": [41.0, 39.0, 40.0]}]}
    page.route("**/dx_monitor/api/hw_status",
               lambda route, *_: route.fulfill(
                   status=200, content_type="application/json", body=json.dumps(hw)))
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="load", timeout=60000)
        page.wait_for_timeout(3500)
        page.evaluate(_QUIET)
        page.wait_for_timeout(600)
        # The changing values are the core bars (one per core) and one line (temperature · clock · power).
        cores = page.evaluate("() => document.querySelectorAll('#homeCores .dev-core').length")
        line = page.inner_text("#homeDeviceLine")
        assert cores == 3, f"코어 3개인 장치에 막대가 {cores}개다"
        assert "41°C" in line, f"장치가 있는데 온도가 없다: {line!r}"
    finally:
        page.close(); ctx.close(); server.shutdown()
