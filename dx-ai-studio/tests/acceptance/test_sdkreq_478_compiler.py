"""SDKREQ-478 [Compiler] ONNX compile and graph viewer — DX Compiler inside a real ./launcher.sh studio.

The viewer parses a real sample ONNX. A real dx_com compile runs only when dx_com is installed and the
disk has room for it; the progress UI and the "dx_com missing" notice are checked by answering the
compiler's own calls. Agentic auto compile never starts a real agent CLI in tests: the console uses the
mock adapter and the run request is answered by the test.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from tests.acceptance.conftest import module_frame, wait_home
from tests.acceptance.hardware import SUITE, need

LAUNCHER_ENV = {"DX_AGENT_ADAPTER": "mock", "DX_AGENT_DEV_PIN_AGENTS": "claude,copilot"}
SAMPLES = SUITE / "dx-compiler" / "dx_com" / "sample_models"
ONNX = SAMPLES / "onnx" / "MobileNetV2-1.onnx"
CONFIG = SAMPLES / "json" / "MobileNetV2-1.json"
PHASES = ["input", "prepared", "surgery", "partition", "qxnn", "dxnn"]
PHASES_EN = ["Input", "Prepared", "Surgery", "Partition", "Quant Diagnosis", "DXNN"]


def _compiler(pages, page=None):
    page = page or pages.new("/")
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('compiler')")
    return page, module_frame(page, "compiler", ready="#compile-form")


def _load_sample(frame):
    assert ONNX.exists(), f"sample model missing: {ONNX}"
    frame.locator("#model_path").fill(str(ONNX))
    frame.locator("#model_path").dispatch_event("change")
    frame.locator("#graph-content g.node-group").first.wait_for(timeout=60000)


def test_six_viewer_tabs_and_only_input_before_a_compile(pages):
    page, frame = _compiler(pages)
    tabs = frame.locator(".viewer-tab[data-phase]")
    assert tabs.evaluate_all("els => els.map(e => e.dataset.phase)") == PHASES
    assert [t.strip() for t in tabs.all_inner_texts()] == PHASES_EN
    _load_sample(frame)
    enabled = tabs.evaluate_all("els => els.filter(e => !e.disabled && !e.classList.contains('disabled')).map(e => e.dataset.phase)")
    assert enabled == ["input"], enabled


def test_explorer_search_node_details_and_legend(pages):
    page, frame = _compiler(pages)
    _load_sample(frame)
    frame.locator("#explorer-toggle").click()
    frame.locator("#explorer-panel .explorer-category-header").first.wait_for(timeout=15000)
    frame.locator("#explorer-panel .explorer-category-header").first.click()      # categories open on click
    sub = frame.locator("#explorer-panel .explorer-category-body.expanded [class*='header']:visible")
    if sub.count():
        sub.first.click()                                                          # op-type groups open too
    item = frame.locator("#explorer-panel .explorer-node-item:visible").first
    item.wait_for(timeout=15000)
    item.click()
    frame.locator("#node-info").wait_for(state="visible", timeout=10000)
    frame.locator("#explorer-close").click()
    frame.locator("#search-input").fill("Conv")
    frame.locator("#search-dropdown *").first.wait_for(timeout=10000)
    assert "Conv" in frame.locator("#search-dropdown").inner_text()
    assert frame.locator("#legend").count() == 1


def test_zoom_and_fit_change_the_view(pages):
    page, frame = _compiler(pages)
    _load_sample(frame)
    zoom = frame.locator("#status-zoom")
    z0 = zoom.inner_text()
    frame.locator("#zoom-in").click()
    frame.wait_for_function("(z) => document.getElementById('status-zoom').innerText !== z", arg=z0)
    z1 = zoom.inner_text()
    frame.locator("#zoom-out").click()
    frame.wait_for_function("(z) => document.getElementById('status-zoom').innerText !== z", arg=z1)
    frame.locator("#zoom-fit").click()
    assert frame.locator("#collapse-all").count() == 1 and frame.locator("#expand-all").count() == 1


def test_compile_shows_progress_and_log_then_done(pages):
    page = pages.new(None)
    job = "acc0001"
    sse = ("event: log\ndata: " + json.dumps({"lines": ["[dxcom] parsing model", "[dxcom] quantizing"]}) + "\n\n"
           "event: progress\ndata: " + json.dumps({"progress": 60, "phase": "Quantization"}) + "\n\n"
           "event: complete\ndata: " + json.dumps({}) + "\n\n")
    page.route("**/compile", lambda route: route.fulfill(
        status=200, content_type="text/html",
        body=Path(__file__).resolve().parents[2].joinpath("dx_compiler/templates/partials/progress.html")
        .read_text().replace("{{ job_id }}", job)) if route.request.method == "POST" else route.continue_())
    page.route(f"**/progress/{job}", lambda route: route.fulfill(status=200, content_type="text/event-stream", body=sse))
    page.goto(pages.studio.base + "/", wait_until="domcontentloaded")
    page, frame = _compiler(pages, page)
    frame.locator("#model_path").fill(str(ONNX))
    frame.locator("#config_path").fill(str(CONFIG))
    frame.locator("#output_dir").fill(str(SUITE / "dx-ai-studio" / "var" / "compiler"))
    frame.wait_for_function("() => !document.getElementById('compile-main-btn').disabled", timeout=30000)
    frame.locator("#compile-main-btn").click()
    frame.locator("#log-content").wait_for(state="visible", timeout=30000)
    frame.wait_for_function("() => /quantizing/.test(document.getElementById('log-content').textContent)", timeout=30000)
    frame.wait_for_function("() => /Compilation Complete/.test(document.querySelector('.progress-container h3').textContent)",
                            timeout=30000)
    assert not frame.locator("#save-summary-btn").is_disabled()
    assert not frame.locator("#download-dxnn-btn").is_disabled()


def test_without_dx_com_compile_is_locked_with_a_clear_reason(pages):
    page = pages.new(None)

    def feature(route):
        resp = route.fetch()
        body = resp.json()
        body["compile"] = False
        route.fulfill(response=resp, body=json.dumps(body))

    page.route("**/feature-check*", feature)
    page.goto(pages.studio.base + "/", wait_until="domcontentloaded")
    page, frame = _compiler(pages, page)
    frame.wait_for_function("() => document.getElementById('compile-main-btn').disabled", timeout=30000)
    reason = frame.locator("#compile-gate-reason")
    reason.wait_for(state="visible", timeout=15000)
    assert "dx_com" in reason.inner_text()


def test_a_real_dx_com_compile_produces_a_dxnn_and_a_summary(pages, studio):
    need("dx_com")
    page, frame = _compiler(pages)
    out = Path(studio.run_dir).parent / "compile-out"
    out.mkdir(exist_ok=True)
    frame.locator("#model_path").fill(str(ONNX))
    frame.locator("#config_path").fill(str(CONFIG))
    frame.locator("#output_dir").fill(str(out))
    frame.locator("#compile-main-btn").click()
    frame.wait_for_function("() => /Compilation (Complete|Failed)/.test(document.querySelector('.progress-container h3')?.textContent || '')",
                            timeout=1500000)
    assert "Complete" in frame.locator(".progress-container h3").inner_text(), frame.locator("#log-content").inner_text()[-2000:]
    with page.expect_download(timeout=120000):
        frame.locator("#save-summary-btn").click()
    assert any(out.rglob("*.dxnn"))


def test_auto_compile_sends_autopilot_and_interactive_runs_to_the_agent(pages):
    page = pages.new(None)
    sent = []

    def run(route):
        sent.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=200, content_type="text/event-stream", body='data: {"type": "done", "exit_code": 0}\n\n')

    page.route("**/agent/api/agent/run", run)
    page.route("**/agent/api/agent/models*", lambda route: route.fulfill(
        status=200, content_type="application/json", body=json.dumps({"models": [{"id": "default", "label": "Default"}]})))
    page.goto(pages.studio.base + "/", wait_until="domcontentloaded")
    page, frame = _compiler(pages, page)
    frame.locator("#agentic-model-input").fill(str(ONNX))
    for button, mode in (("#auto-compile-noninteractive", "autopilot"), ("#auto-compile-interactive", "interactive")):
        frame.wait_for_function("(b) => !document.querySelector(b).disabled", arg=button, timeout=30000)
        frame.locator(button).click()
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline and not any(p.get("mode") == mode for p in sent):
            page.wait_for_timeout(250)
        hit = [p for p in sent if p.get("mode") == mode]
        assert hit and hit[-1].get("target") == "dx-compiler", sent
