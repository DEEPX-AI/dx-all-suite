"""Model Zoo → inference panel → Build C++ runner, on screen.

The build endpoints and the catalog answer are routed fixtures, so nothing is compiled on this machine."""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from shared.chromium import resolve_chromium_executable  # noqa: E402
from tests.server_helpers import start_module_server  # noqa: E402

MODEL = "alexnet"


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_modelzoo")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True, executable_path=resolve_chromium_executable())
    try:
        yield br, port
    finally:
        br.close()
        pw.stop()
        srv.shutdown()
        srv.server_close()


def _open(browser, start=None, log=None, lang="en"):
    """start: the /proxy/model-build answer; log: list of /log answers (the last one repeats)."""
    br, port = browser
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script(f"localStorage.setItem('dx-lang','{lang}');localStorage.setItem('dx-tutorial-mode','off');")
    page = ctx.new_page()
    state = {"built": False, "posts": [], "stops": 0, "polls": 0}

    def catalog(route, *_):
        resp = route.fetch()
        data = resp.json()
        m = data["model"]
        m.update(downloaded=True, downloaded_qlite=True)
        if state["built"]:
            m.update(cpp_buildable=False, variants={"cpp": ["sync", "async"], "python": ["sync", "async"]})
        else:
            m.update(cpp_buildable=True, variants={"python": ["sync", "async"]})
        route.fulfill(response=resp, json=data)

    def health(route, *_):
        route.fulfill(json={"ok": True, "dx_app_alive": True})

    def build(route, *_):
        state["posts"].append(route.request.post_data_json)
        route.fulfill(json=start or {"ok": True, "started": True})

    def poll(route, *_):
        answers = log or [{"log": "", "done": True, "exit_code": 0}]
        a = answers[min(state["polls"], len(answers) - 1)]
        state["polls"] += 1
        if a.get("done") and a.get("exit_code") == 0:
            state["built"] = True
        route.fulfill(json=a)

    def stop(route, *_):
        state["stops"] += 1
        route.fulfill(json={"ok": True})

    page.route(f"**/api/catalog/{MODEL}", catalog)
    page.route("**/api/health", health)
    page.route("**/api/proxy/model-build", build)
    page.route("**/api/proxy/model-build/log", poll)
    page.route("**/api/proxy/model-build/stop", stop)
    page.goto(f"http://127.0.0.1:{port}/#model={MODEL}", wait_until="load")
    page.locator("#sectionExample details > summary").click(timeout=20000)    # "Run Inference", as a user opens it
    page.locator("#btnBuildCpp:not([disabled])").wait_for(timeout=20000)
    return ctx, page, state


def test_buildable_model_offers_the_button_and_success_selects_cpp_sync(browser):
    log = [{"log": "[ 50%] Building CXX\n", "done": False},
           {"log": "[ 50%] Building CXX\n[100%] Built target alexnet_sync\n", "done": True, "exit_code": 0}]
    ctx, page, state = _open(browser, log=log)
    try:
        page.click("#btnBuildCpp")
        page.locator(".mz-cpp-build-ok").wait_for(timeout=20000)
        assert state["posts"][0]["model_name"] == MODEL
        assert page.locator("#infExecPath").input_value() == "cpp|sync"
        assert page.locator("#btnBuildCpp").count() == 0      # the panel re-rendered without the build row
    finally:
        ctx.close()


def test_failure_shows_retry_and_opens_the_log(browser):
    log = [{"log": "error: undefined reference to foo\n", "done": True, "exit_code": 2}]
    ctx, page, state = _open(browser, log=log)
    try:
        page.click("#btnBuildCpp")
        retry = page.locator("#mzCppBuildProgress button", has_text="Retry")
        retry.wait_for(timeout=10000)
        assert page.locator("#mzCppBuildProgress details").get_attribute("open") is not None
        assert "undefined reference" in page.locator(".mz-cpp-build-log").inner_text()
        assert page.locator("#btnBuildCpp").is_enabled()
        retry.click()
        page.wait_for_function("() => !document.querySelector('#mzCppBuildProgress button')"
                               " || document.querySelector('#btnCancelCpp')")
        assert len(state["posts"]) == 2
    finally:
        ctx.close()


def test_busy_setup_job_is_reported_not_started(browser):
    ctx, page, state = _open(browser, start={"ok": False, "error": "Another process is already running"})
    try:
        page.click("#btnBuildCpp")
        msg = page.locator("#mzCppBuildProgress")
        msg.wait_for(state="visible")
        assert "Setup is running" in msg.inner_text()
        assert state["polls"] == 0
    finally:
        ctx.close()


def test_cancel_calls_stop(browser):
    ctx, page, state = _open(browser, log=[{"log": "building\n", "done": False}])
    try:
        page.click("#btnBuildCpp")
        with page.expect_request("**/api/proxy/model-build/stop"):
            page.locator("#btnCancelCpp").click()
        assert state["stops"] == 1
    finally:
        ctx.close()


def test_korean_page_shows_korean_build_ui(browser):
    ctx, page, _ = _open(browser, lang="ko", log=[{"log": "building\n", "done": False}])
    try:
        text = page.locator("#mzCppBuild").inner_text()
        assert "Build C++ runner" not in text and "C++ runner not built" not in text
    finally:
        ctx.close()


def test_a_long_build_line_stays_inside_the_panel(browser):
    """make prints object paths wider than the panel; the last-line preview must clip, not overflow."""
    line = "[ 92%] Building CXX object " + "src/cpp_example/classification/alexnet/CMakeFiles/x.dir/" * 4 + "x.cpp.o"
    ctx, page, _ = _open(browser, log=[{"log": line + "\n", "done": False}])
    try:
        page.click("#btnBuildCpp")
        page.locator(".mz-cpp-build-last").filter(has_text="Building CXX").wait_for(timeout=10000)
        box = page.locator("#mzCppBuild").bounding_box()
        last = page.locator(".mz-cpp-build-last").bounding_box()
        assert last["x"] + last["width"] <= box["x"] + box["width"] + 1
    finally:
        ctx.close()
