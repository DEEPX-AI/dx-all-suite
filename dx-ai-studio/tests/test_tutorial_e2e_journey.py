"""E2E tutorial journey — real UI clicks through Start → Next → Continue."""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402
from tests.tutorial_e2e_runner import mock_left_over, run_ui_journey, summarize  # noqa: E402

JOURNEY_MODULES = [
    {
        # 런처가 빠져 있었다. 이 브랜치가 가장 많이 다시 그린 화면인데, 그 튜토리얼을
        # 구동하는 테스트가 하나도 없어서 홈 재설계가 지운 요소를 가리키는 스텝이
        # 그대로 살아남았다 — 사용자에게는 4번이 건너뛰어지는 것으로 보였다.
        # 스플래시를 먼저 건너뛰어야 한다: 오버레이가 DOM 에 있는 동안 튜토리얼
        # 엔진이 열리지 않고(tutorial-init.js 의 셸 차단 조건), 인트로는 12초짜리다.
        "id": "launcher",
        "server": "launcher",
        "setup": "() => {}",
        "wait": "#studioGrid",
        "ready": "() => window._dxTutorial && document.getElementById('studioGrid')",
        "ready_timeout": 60000,
    },
    {
        "id": "dx_modelzoo",
        "server": "dx_modelzoo",
        "setup": "() => {}",
        "wait": "#dxToolbar",
        "ready": "() => window._dxTutorial && document.querySelector('.mz-card')",
        "ready_timeout": 60000,
    },
    {
        "id": "dx_app",
        "server": "dx_app",
        "setup": "() => {}",
        "wait": "#dxToolbar",
        "ready": "() => typeof nav==='function' && window._dxTutorial",
    },
    {
        "id": "dx_stream",
        "server": "dx_stream",
        "setup": "() => { const d = document.getElementById('dx-input-modal'); if (d && d.open) d.close(); }",
        "wait": "#dxToolbar",
        "ready": "() => typeof DXStream!=='undefined' && window._dxTutorial",
    },
    {
        # 빠져 있었다 — Compiler 는 튜토리얼이 있는데 구동하는 테스트가 없었다 (2026-10-11 audit).
        "id": "dx_compiler",
        "server": "dx_compiler",
        "setup": "() => {}",
        "wait": "#dxToolbar",
        "ready": "() => window._dxTutorial && document.getElementById('compile-main-btn')",
    },
    {
        "id": "dx_planner",
        "server": "dx_planner",
        "setup": "() => {}",
        "wait": "#plannerWorkspace",
        "ready": "() => window._dxTutorial",
    },
    {
        "id": "dx_benchmark",
        "server": "dx_benchmark",
        "setup": "() => {}",
        "wait": "#dxToolbar",
        "ready": "() => typeof BenchApp!=='undefined' && window._dxTutorial",
    },
    {
        "id": "dx_monitor",
        "server": "dx_monitor",
        "setup": "() => {}",
        "wait": ".monitor-main",
        "ready": "() => window._dxTutorial",
    },
    {
        "id": "dx_agent_dev",
        "server": "dx_agent_dev",
        "setup": "() => {}",
        "wait": ".agent-layout",
        "ready": "() => window._dxTutorial",
    },
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
    # 런처만 해당된다. 12초짜리 인트로가 DOM 에 있는 동안 튜토리얼 엔진은 열리지
    # 않고(tutorial-init.js), 자동 워크스루가 돌면 저니가 구동하는 투어와 싸운다.
    # 다른 모듈에는 스플래시도 자동 워크스루도 없어 무해하다.
    ctx.add_init_script(
        "try {"
        " sessionStorage.setItem('dx-splash-seen', '1');"
        " localStorage.setItem('dx-splash-seen', '1');"
        " localStorage.setItem('dx-tutorial-launcher-autostarted', '1');"
        "} catch (e) {}"
    )
    pg = ctx.new_page()
    try:
        yield pg
    finally:
        pg.close()
        ctx.close()


# 투어는 요소를 **픽셀 좌표로 겨눈다.** 번역문은 길이가 달라서 — `Re-download`
# 가 `다시 다운로드` 가 되면 버튼이 커지고, 그 옆 요소가 접히거나 밀려난다 —
# 영어에서만 맞고 다른 언어에서 어긋날 수 있다. 실제로 이번 세션에 ACTIONS 열
# 하나가 71px 늘자 표 전체가 22% 밀리는 것을 봤다.
#
# 그런데 이 스위트는 오랫동안 `lang="en"` 하나만 돌렸다. 러너에는 `set_lang`
# 헬퍼와 `lang` 인자가 **이미 있었는데** 테스트가 쓰지 않았다.
#
# 일본어를 고른 이유: 한국어·중국어보다 라벨이 길어지는 경향이 있고(가타카나
# 외래어), 스페인어와 달리 줄바꿈 규칙이 달라 레이아웃을 더 흔든다.
# 언어 하나당 8모듈 · 약 8분이므로 전 언어를 돌리지 않는다 — 깨지는 종류를
# 찾는 것이 목적이지 전수 검증이 목적이 아니다.
JOURNEY_LANGS = ["en", "ja"]

_JOURNEY_AXES = [(m, lang) for m in JOURNEY_MODULES for lang in JOURNEY_LANGS]


@pytest.mark.parametrize(
    ("mod", "lang"), _JOURNEY_AXES,
    ids=[f"{m['id']}-{lang}" for m, lang in _JOURNEY_AXES],
)
def test_tutorial_ui_journey_no_visual_defects(page, mod, lang):
    server, port = start_module_server(mod["server"])
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="domcontentloaded", timeout=60000)
        results = run_ui_journey(
            page,
            lang=lang,
            module_setup=mod["setup"],
            wait_selector=mod["wait"],
            ready_script=mod["ready"],
            ready_timeout=mod.get("ready_timeout", 20000),
        )
        failures = summarize(results)
        assert results, f"{mod['id']}[{lang}]: journey produced no step checks"
        assert not failures, (
            f"{mod['id']} UI journey defects [{lang}]:\n" + "\n".join(failures[:30]))

        # 주입한 프리뷰는 투어가 끝나면 사라져야 한다. 스텝이 살아 있는 동안의
        # 존재는 정상이므로 analyze_step 이 아니라 여기서 센다.
        left = mock_left_over(page)
        assert not left, f"{mod['id']}[{lang}]: 투어 종료 후에도 남은 튜토리얼 주입 요소: {left}"
    finally:
        server.shutdown()
