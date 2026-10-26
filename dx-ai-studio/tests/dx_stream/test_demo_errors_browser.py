"""Stream launch errors stay on the selected stage, not only in a toast."""
from __future__ import annotations

import json

import pytest

from tests.dx_stream.test_demo_cards_browser import DEMOS, page  # noqa: F401


@pytest.fixture
def stream_page(page):
    routes = []

    def route(pattern, handler):
        page.route(pattern, handler)
        routes.append((pattern, handler))

    page.add_route = route
    page.evaluate("() => DXStream.demoInit()")
    yield page
    for pattern, handler in routes:
        page.unroute(pattern, handler)
    page.evaluate("() => localStorage.setItem('dx-lang', 'en')")
    page.reload(wait_until="load")
    page.evaluate("() => DXStream.nav('demo')")
    page.wait_for_selector("#start-demo-0")


def _reply(route, body, status=200):
    route.fulfill(status=status, content_type="application/json", body=json.dumps(body))


def _inline_error(page):
    error = page.locator(".dds-stage .stream-demo-error[role=alert]")
    error.wait_for(state="visible", timeout=2500)
    return error


def test_contract_error_persists_across_stage_reopen_and_successful_retry_clears_it(stream_page):
    page = stream_page
    failure = {
        "error": "contract_failed", "message": "Runtime contract failed: profile.context",
        "detail": "No interpreter <img src=x onerror=window.__streamXss=1>. Run DX-Runtime Dependencies in Setup.",
    }
    calls = []

    def start(route):
        calls.append(True)
        if len(calls) == 1:
            _reply(route, failure, 424)
        else:
            route.fallback()

    page.add_route("**/api/demos/0/start", start)
    page.click("#start-demo-0")
    error = _inline_error(page)
    assert "profile.context" in error.inner_text()
    assert "contract_failed" in error.inner_text()
    assert failure["detail"] in error.inner_text()
    assert error.locator("img").count() == 0
    assert page.evaluate("window.__streamXss") is None
    assert page.locator(".dds-state").get_attribute("data-kind") == "failed"
    page.evaluate("() => document.getElementById('toast-container').replaceChildren()")
    page.click(".dds-card[data-id='2']")
    assert page.locator(".stream-demo-error").count() == 0
    page.click(".dds-card[data-id='0']")
    assert _inline_error(page).is_visible()
    page.evaluate("() => DXStream.nav('setup')")
    page.evaluate("() => DXStream.nav('demo')")
    assert _inline_error(page).is_visible()
    assert page.locator(".dds-stage .dds-setup").is_visible()
    page.click("#start-demo-0")
    page.wait_for_function("() => DXStream._runningDemoId === 0")
    assert page.locator(".stream-demo-error").count() == 0
    assert page.evaluate("DXStream._demoErrors[0]") is None
    page.click("#btn-demo-stop")


@pytest.mark.parametrize("failure", ["network", "json", "empty", "preflight"])
def test_transport_and_invalid_response_errors_are_inline_and_retryable(stream_page, failure):
    page = stream_page

    def start(route):
        if failure == "network":
            route.abort("failed")
        else:
            route.fulfill(status=200, content_type="application/json",
                          body="not-json" if failure == "json" else "null")

    page.add_route("**/api/demos/0/start", start)
    if failure == "preflight":
        page.evaluate("""() => { DXStream.webrtc.preferredPayloadTypes = async function () {
            throw new Error('Codec capability probe failed');
        }; }""")
    page.evaluate("() => DXStream._startDemo(0)")
    assert _inline_error(page).inner_text().strip()
    assert page.locator(".dds-state").get_attribute("data-kind") == "failed"
    assert page.locator("#start-demo-0").is_enabled()
    assert page.locator("#start-demo-0").inner_text().strip() == "Retry"
    assert page.evaluate("DXStream._startingDemo") is False


@pytest.mark.parametrize("stopped", [False, True])
def test_mjpeg_fallback_failures_remain_inline_after_server_sync(stream_page, stopped):
    page = stream_page
    page.click("#start-demo-0")
    page.wait_for_function("() => DXStream._runningDemoId === 0")
    failure = {
        "error": "pipeline_error" if stopped else "contract_failed",
        "message": "Demo playback stopped." if stopped else "Runtime contract failed: profile.context",
        "detail": "Missing plugin; run Setup and retry.",
    }
    if stopped:
        failure["playback_active"] = False
    page.add_route("**/api/demos/0/start", lambda route: _reply(route, failure, 424))
    page.evaluate("() => DXStream._fallbackToMjpeg(0)")
    assert failure["detail"] in _inline_error(page).inner_text()
    page.evaluate("() => DXStream._demoSyncWithServer({running: false})")
    assert failure["detail"] in _inline_error(page).inner_text()
    assert page.locator(".dds-state").get_attribute("data-kind") == "failed"


def test_runtime_readiness_refreshes_after_setup_and_keeps_the_selected_stage(stream_page):
    page = stream_page
    entries = [dict(DEMOS[0])]
    entries[0].update(available=False, availability={
        "available": False, "reason": "Runtime contract failed: profile.context",
        "reason_items": [{"code": "contract_failed", "message": "Runtime contract failed: profile.context",
                          "detail": "No active runtime interpreter. Run DX-Runtime Dependencies in Setup."}],
    })
    page.add_route("**/api/demos", lambda route: _reply(route, entries))
    page.evaluate("() => { DXStream._demoCtl = null; return DXStream.demoInit(); }")
    assert "DX-Runtime Dependencies" in page.locator(".dds-none").inner_text()
    page.click(".dds-card[data-id='0']")
    assert page.locator(".dds-state").get_attribute("data-kind") == "unready"
    assert "DX-Runtime Dependencies" in page.locator(".dds-stage").inner_text()
    assert page.locator("#start-demo-0").count() == 0
    page.locator(".dds-stage .dds-setup").click()
    assert page.evaluate("DXStream.S.currentPage") == "setup"
    entries[0].update(available=True, availability={"available": True})
    page.evaluate("() => DXStream.nav('demo')")
    page.wait_for_selector("#start-demo-0")
    assert page.locator(".dds-state").get_attribute("data-kind") == "ready"


def test_launch_error_survives_readiness_changing_to_needs_setup(stream_page):
    page = stream_page
    failure = {"error": "contract_failed", "message": "Runtime contract failed: profile.context",
               "detail": "Runtime changed. Run DX-Runtime Dependencies in Setup."}
    page.add_route("**/api/demos/0/start", lambda route: _reply(route, failure, 424))
    page.click("#start-demo-0")
    assert failure["detail"] in _inline_error(page).inner_text()
    unavailable = dict(DEMOS[0], available=False, availability={
        "available": False, "reason_items": [dict(failure, code="contract_failed")],
    })
    page.add_route("**/api/demos", lambda route: _reply(route, [unavailable]))
    page.evaluate("() => DXStream.demoInit()")
    assert failure["detail"] in _inline_error(page).inner_text()
    assert page.locator("#start-demo-0").count() == 0
    assert page.locator(".dds-stage .dds-setup").first.is_visible()


def test_inline_failure_translates_sentences_but_preserves_server_fields(stream_page):
    page = stream_page
    failure = {"error": "pipeline_error", "message": "Demo playback stopped.",
               "detail": "No output backend became ready.",
               "remediation": "Verify the selected input and Stream output dependencies, then retry.",
               "playback_active": False}
    page.add_route("**/api/demos/0/start", lambda route: _reply(route, failure, 500))
    page.evaluate("() => DXI18n.setLang('ko')")
    page.wait_for_selector("#start-demo-0")
    page.click("#start-demo-0")
    error = _inline_error(page)
    assert "데모 재생이 멈췄습니다." in error.inner_text()
    assert "영상 출력이 준비되지 않았습니다." in error.inner_text()
    assert failure["remediation"] not in error.inner_text()
    assert page.evaluate("DXStream._demoErrors[0].detail") == failure["detail"]
    assert "pipeline_error" in error.inner_text()


@pytest.mark.parametrize("with_error", [False, True])
def test_running_demo_can_stop_after_reopening_with_all_demos_unready(stream_page, with_error):
    page = stream_page
    page.click("#start-demo-0")
    page.wait_for_function("() => DXStream._runningDemoId === 0")
    starts = len(page.starts)
    stopped = []
    if with_error:
        page.evaluate("() => _demoSetError(0, {error: 'playback_failed', detail: 'Retry playback or use Setup.'})")

    def stop(route):
        stopped.append(route.request.url)
        route.fallback()

    unavailable = dict(DEMOS[0], available=False, availability={
        "available": False, "reason_items": [{
            "code": "contract_failed", "message": "Runtime contract failed: profile.context",
            "detail": "Runtime changed. Run DX-Runtime Dependencies in Setup.",
        }],
    })
    page.add_route("**/api/demos", lambda route: _reply(route, [unavailable]))
    page.add_route("**/api/demos/0/stop", stop)
    page.evaluate("() => DXStream.nav('setup')")
    page.evaluate("() => DXStream.nav('demo')")
    page.wait_for_selector(".dds-stage #btn-demo-stop")
    assert page.locator(".dds-stage .dds-run:not(.is-stop)").count() == 0

    with page.expect_request("**/api/demos/0/stop", timeout=2500):
        page.click(".dds-stage #btn-demo-stop")
    page.wait_for_function("() => DXStream._runningDemoId === null")
    assert len(stopped) == 1
    assert len(page.starts) == starts
    assert page.locator(".dds-stage .dds-run").count() == 0
    assert page.locator(".dds-stage .dds-setup").first.is_visible()


def test_a_korean_ui_shows_the_whole_profile_context_refusal_in_korean(stream_page):
    """SR-843: the refusal the server really sends (separate detail / remediation) reads
    entirely in Korean — the observed sentence and the Setup instruction included."""
    page = stream_page
    failure = {"error": "contract_failed", "message": "Runtime contract failed: profile.context",
               "detail": "Active runtime profile has no complete inference Python.",
               "remediation": "Run the DX-Runtime Dependencies step in Setup, then try again."}
    page.add_route("**/api/demos/0/start", lambda route: _reply(route, failure, 424))
    page.evaluate("() => DXI18n.setLang('ko')")
    page.wait_for_selector("#start-demo-0")
    page.click("#start-demo-0")
    text = _inline_error(page).inner_text()
    assert "런타임 점검을 통과하지 못했습니다 (profile.context)" in text
    assert "활성 런타임 profile에 사용할 수 있는 추론용 Python이 없습니다." in text
    assert "Setup에서 DX-Runtime 종속성 설치 단계를 실행한 뒤 다시 시도하세요." in text
    for english in (failure["message"], failure["detail"], failure["remediation"]):
        assert english not in text
