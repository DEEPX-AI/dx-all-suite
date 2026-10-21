"""Live startup errors stay visible at the controls and survive a reset, without hiding successful slots."""
import pytest

from tests.server_helpers import start_module_server

pytest.importorskip("playwright.sync_api")

MODELS = [
    {"name": f"detector_{i}", "category": "object_detection", "model_file": f"assets/models/detector_{i}.dxnn",
     "model_exists": True, "cpp": True, "cpp_sync": True, "cpp_async": True, "python": False}
    for i in range(2)
]
MISSING = {"error_key": "live_deps_missing", "error": "Live streaming requires: Xvfb (sudo apt install xvfb)"}


@pytest.fixture(scope="module")
def live_browser():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_app")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        yield browser, port
        browser.close()
    srv.shutdown()
    srv.server_close()


@pytest.fixture
def page(live_browser):
    browser, port = live_browser
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','en');")
    page = ctx.new_page()
    for path, data in (("models", MODELS), ("videos", []), ("images", []),
                       ("cameras", [{"index": 0, "device": "/dev/video0", "available": True, "width": 640, "height": 480}])):
        page.route(f"**/api/{path}", lambda route, _request, data=data: route.fulfill(json=data))
    page.route("**/api/live_poll?*", lambda route: route.fulfill(json={"running": True, "frames": 1}))
    page.route("**/api/live_frame?*", lambda route: route.abort())
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.evaluate("nav('run')")
    page.wait_for_function("() => S.models.length === 2")
    page.evaluate("toggleRunTab('continuous')")
    page.select_option("#c-input-type", "camera")
    page.wait_for_function("() => document.querySelector('#c-camera option[value=\"0\"]')")
    page.select_option("#c-camera", "0")
    page.select_option('#c-slots .cont-slot-cfg select >> nth=0', "object_detection")
    page.select_option('#c-slots .cont-slot-cfg select >> nth=1', "detector_0")
    yield page
    ctx.close()


def _start(page):
    page.click("#c-start-btn")
    page.wait_for_function("() => !document.getElementById('c-start-btn').classList.contains('hidden')"
                           " || LIVE.slots.length > 0")


def test_missing_dependency_stays_visible_after_toasts_expire_and_retry_clears_it(page):
    calls = []

    def run(route):
        calls.append(route.request.post_data_json)
        route.fulfill(status=409 if len(calls) == 1 else 200,
                      json=MISSING if len(calls) == 1 else {"job_id": "retry-ok"})

    page.route("**/api/run_live", run)
    _start(page)
    error = page.locator("#c-live-errors")
    assert error.is_visible(), "a failed Live start must leave a persistent inline error"
    assert "Slot 1" in error.inner_text() and "detector_0" in error.inner_text()
    assert "Xvfb" in error.inner_text() and "sudo apt install xvfb" in error.inner_text()
    page.wait_for_timeout(4500)
    assert error.is_visible()
    assert page.locator("#c-start-btn").is_visible() and page.locator("#c-start-btn").is_enabled()
    assert page.locator("#c-stop-btn").is_hidden()
    _start(page)
    assert len(calls) == 2 and page.evaluate("LIVE.slots[0].jobId") == "retry-ok"
    assert error.is_hidden(), "successful retry clears the old diagnostic"
    assert page.locator("#c-stop-btn").is_visible()


def test_partial_success_keeps_live_slot_stop_controls_and_failed_slot_diagnostic(page):
    stopped = []
    page.click("#c-add-btn")
    slot = page.locator("#c-slots .cont-slot-cfg").nth(1)
    slot.locator("select").nth(0).select_option("object_detection")
    slot.locator("select").nth(1).select_option("detector_1")
    page.route("**/api/run_live", lambda route: route.fulfill(
        status=200 if route.request.post_data_json["slot_idx"] == 0 else 409,
        json={"job_id": "slot-ok"} if route.request.post_data_json["slot_idx"] == 0 else MISSING))
    page.route("**/api/live_stop", lambda route: (stopped.append(True), route.fulfill(json={"ok": True})))
    page.route("**/api/live_result?*", lambda route: route.fulfill(json={"frames": 1, "elapsed": 1}))
    _start(page)
    page.wait_for_function("() => !document.getElementById('c-live-errors')?.classList.contains('hidden')"
                           " && document.getElementById('c-live-errors')?.textContent.includes('Slot 2')")
    assert page.locator("#c-live-errors").is_visible()
    assert "detector_1" in page.locator("#c-live-errors").inner_text()
    assert page.locator("#c-live-view").is_visible()
    assert page.locator("#c-ls-img-0").is_visible()
    assert page.evaluate("LIVE.slots.map(s => s.jobId)") == ["slot-ok"]
    assert page.locator("#c-start-btn").is_hidden() and page.locator("#c-stop-btn").is_visible()
    page.click("#c-stop-btn")
    page.wait_for_function("() => !CONT.running", timeout=10000)
    assert stopped
    assert page.locator("#c-start-btn").is_visible() and page.locator("#c-stop-btn").is_hidden()
    assert page.locator("#c-live-errors").is_visible(), "Stop/reset must not erase a startup failure"


def test_transport_failure_is_inline_and_retryable(page):
    page.route("**/api/run_live", lambda route: route.abort("failed"))
    _start(page)
    assert page.locator("#c-live-errors").is_visible()
    assert page.locator("#c-live-errors").inner_text().strip()
    assert page.locator("#c-start-btn").is_visible() and page.locator("#c-start-btn").is_enabled()


def test_all_failed_slots_keep_their_individual_diagnostics_after_reset(page):
    page.click("#c-add-btn")
    slot = page.locator("#c-slots .cont-slot-cfg").nth(1)
    slot.locator("select").nth(0).select_option("object_detection")
    slot.locator("select").nth(1).select_option("detector_1")
    page.route("**/api/run_live", lambda route: route.fulfill(status=409, json=(
        MISSING if route.request.post_data_json["slot_idx"] == 0 else
        {"error_key": "binary_not_found", "error": "detector_1_sync is not executable"})))
    _start(page)
    error = page.locator("#c-live-errors")
    text = error.inner_text()
    assert error.is_visible()
    assert "Slot 1" in text and "Xvfb" in text and "Slot 2" in text and "detector_1_sync" in text
    assert not page.evaluate("CONT.running")
    assert page.locator("#c-start-btn").is_enabled() and page.locator("#c-stop-btn").is_hidden()


def test_setup_reports_xvfb_as_a_separate_optional_requirement_without_running_it(page):
    """Xvfb is not installed by any step (dx_app install.sh --all never does), so it is shown
    beside the list as an optional Live requirement with the exact command, not as a step gate."""
    started = []
    page.on("request", lambda request: started.append(request.url)
            if request.method == "POST" and request.url.endswith("/api/setup/run") else None)
    page.route("**/api/setup/status", lambda route: route.fulfill(json={
        **{key: {"ok": True, "detail": "ready"} for key in
           ("dx-app-deps", "dx-rt-deps", "dx-rt-build", "dx-driver", "dx-app-build", "dx-app-setup")},
        "live-display": {"ok": False, "optional": True, "hint": "sudo apt install xvfb",
                         "detail": "Xvfb not installed · sudo apt install xvfb"},
    }))
    with page.expect_response(lambda response: response.url.endswith("/api/setup/status")):
        page.evaluate("nav('setup')")
    box = page.locator("#setup-live-display")
    page.wait_for_function("() => document.getElementById('setup-live-display').dataset.ok === 'false'")
    assert box.is_visible()
    assert "sudo apt install xvfb" in box.inner_text()
    assert "Optional" in box.inner_text() and "Xvfb not installed" in box.inner_text()
    assert "xvfb" not in page.locator('[data-step="dx-app-deps"]').inner_text().lower()
    assert page.locator('[data-step="dx-app-deps"]').get_attribute("data-state") == "done"
    assert not started, "an optional requirement is reported, never installed"


def test_quick_start_describes_the_demo_preparation_and_never_runs_it_on_status_read(page):
    started = []
    page.on("request", lambda request: started.append(request.url)
            if request.method == "POST" and request.url.endswith("/api/setup/run") else None)
    page.route("**/api/setup/status", lambda route: route.fulfill(json={
        "dx-app-build": {"ok": False, "detail": "Graph binaries missing"},
        "dx-app-setup": {"ok": False, "detail": "Unverified sample assets"},
    }))
    with page.expect_response(lambda response: response.url.endswith("/api/setup/status")):
        page.evaluate("nav('setup')")
    text = page.locator("#setup-quickstart").inner_text()
    assert "demo C++ runners and demo models" in text
    assert "full C++ build" not in text
    assert not started, "checking missing prerequisites must never start an installer"


def test_quick_start_runs_the_demo_form_of_the_build_and_asset_steps(page):
    runs = []

    def run(route):
        runs.append(route.request.post_data_json)
        route.fulfill(json={"ok": True, "started": True})

    page.route("**/api/setup/quick-start-plan", lambda route: route.fulfill(json={"plan": ["dx-app-setup"]}))
    page.route("**/api/setup/run", run)
    page.route("**/api/setup/log", lambda route: route.fulfill(json={"log": "", "done": True, "exit_code": 0}))
    page.evaluate("nav('setup')")
    page.evaluate("setupDemoQuickStart()")
    page.wait_for_function("() => document.getElementById('setup-try-demo').style.display === ''")
    assert runs and runs[0]["step"] == "dx-app-setup" and runs[0]["demo_only"] is True
    assert page.evaluate("_setupDemoParams('dx-app-build')") == {"demo_only": True}
    assert page.evaluate("_setupDemoParams('dx-rt-build')") == {}


def test_camera_runtime_failure_is_not_reported_as_no_cameras_and_can_retry(page):
    page.route("**/api/cameras", lambda route: route.fulfill(status=503, json={
        "error_key": "media_runtime_unavailable", "error": "OpenCV probe failed: install Python Inference Deps in Setup"}))
    page.evaluate("loadCameras()")
    page.wait_for_function("() => document.getElementById('c-camera').value === ''")
    assert "OpenCV probe failed" in page.locator("#c-camera").inner_text()
    assert "No cameras found" not in page.locator("#c-camera").inner_text()
    assert page.locator("#c-live-errors").is_visible()
    assert "Setup" in page.locator("#c-live-errors").inner_text()
    page.unroute("**/api/cameras")
    page.route("**/api/cameras", lambda route: route.fulfill(json=[
        {"index": 0, "device": "/dev/video0", "available": True, "width": 640, "height": 480}]))
    page.evaluate("loadCameras()")
    page.wait_for_function("() => document.getElementById('c-camera').value === '0'")
    assert page.locator("#c-live-errors").is_hidden()


def test_acceptance_benchmark_selects_the_rendered_cpp_model_not_downloaded_python_preference(page, monkeypatch):
    from tests.acceptance import test_sdkreq_474_dx_app as acceptance

    models = [
        {**MODELS[0], "name": acceptance.PREFERRED_MODELS[0], "cpp": False, "cpp_sync": False, "python": True,
         "py_sync": True},
        MODELS[1],
    ]
    page.route("**/api/models", lambda route: route.fulfill(json=models))
    page.evaluate("(models) => { S.models = models; }", models)
    monkeypatch.setattr(acceptance, "_app", lambda _pages: (page, page))
    page.set_default_timeout(5000)
    acceptance.test_benchmark_runs_the_checked_models_and_shows_results_and_a_chart(object())


def test_graph_missing_build_guidance_uses_full_build_in_every_language(page):
    key = "The graph runner is not built. Build dx_app (./build.sh) to use the Graph Composer."
    for lang in ("en", "ko", "ja", "zh-CN", "zh-TW", "es"):
        text = page.evaluate("([lang, key]) => { DXI18n.setLang(lang); return T(key); }", [lang, key])
        assert "./build.sh --all" in text, (lang, text)


def test_benchmark_selection_respects_the_rendered_filter_and_selected_variant(page):
    from tests.acceptance import test_sdkreq_474_dx_app as acceptance

    models = [
        {**MODELS[0], "name": acceptance.PREFERRED_MODELS[0]},
        {**MODELS[1], "category": "image_classification"},
    ]
    page.route("**/api/models", lambda route: route.fulfill(json=models))
    page.evaluate("(models) => { S.models = models; nav('bench'); }", models)
    page.select_option("#b-cat", "image_classification")
    page.select_option("#b-mode", "async")
    page.evaluate("filterBenchModels()")
    model = acceptance._benchmark_model(page)
    assert model["name"] == "detector_1"
    assert model["cpp_async"]
