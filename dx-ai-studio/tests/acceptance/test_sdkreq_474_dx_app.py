"""SDKREQ-474 [DX App] integrated workflow — DX App inside a real ./launcher.sh studio.

DX App runs on the real dx-runtime/dx_app tree. NPU checks run real inference on the board's DX-M1
and are separate tests (and separate AC) so their time shows on their own. Where a check would
download or change files (ModelZoo download, benchmark runs) the API is answered by the test.
"""
from __future__ import annotations

import json
import re

from tests.acceptance.conftest import http_get, module_frame, wait_home
from tests.acceptance.hardware import need

PAGES = ["setup", "models", "run", "rundemo", "bench", "compare", "modelzoo", "graph", "lab", "outputs", "reference"]
PAGES_KO = ["설치", "모델", "추론 실행", "데모 실행", "벤치마크", "A/B 비교", "모델 저장소", "그래프 Composer", "실험실",
            "출력물", "레퍼런스"]
RESULT_IMG = "#r-result .cmp-after-clip img, #r-result img.res-img"
PREFERRED_MODELS = ("yolov8-n_640x640", "yolo26n_640x640", "yolov5s_640x640")


def _app(pages, lang="en", **kw):
    page = pages.new("/", lang=lang, **kw)
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('app')")
    return page, module_frame(page, "app", ready=".dx-shell-tabs .dx-tab")


def _nav(frame, page_id):
    frame.locator(f'.dx-shell-tabs .dx-tab[data-page="{page_id}"]').click()
    frame.locator(f"#page-{page_id}.active").wait_for(timeout=15000)


def _runnable_model(frame) -> dict:
    models = frame.evaluate("async () => { const r = await (await fetch('api/models')).json();"
                            " return Array.isArray(r) ? r : (r.models || []); }")
    by_name = {m["name"]: m for m in models if m.get("model_exists")}
    for name in PREFERRED_MODELS:
        if name in by_name:
            return by_name[name]
    det = [m for m in by_name.values() if m.get("category") == "object_detection"]
    assert det, "no object detection model with a .dxnn on disk"
    return det[0]


def test_eleven_top_tabs_switch_pages_and_developer_tools_live_in_lab(pages):
    page, frame = _app(pages, lang="ko")
    tabs = frame.locator(".dx-shell-tabs .dx-tab")
    assert tabs.evaluate_all("els => els.map(e => e.dataset.page)") == PAGES
    labels = [t.strip() for t in tabs.evaluate_all("els => els.map(e => e.textContent)")]
    assert labels == PAGES_KO, labels
    for pid in PAGES:
        frame.evaluate("(p) => nav(p)", pid)   # overflow (+N) tabs are not all visible at 1440 px
        frame.locator(f"#page-{pid}.active").wait_for(timeout=15000)
    _nav(frame, "lab")
    frame.locator("#lab-advanced-tools").wait_for(state="attached", timeout=15000)


def test_setup_lists_six_steps_runs_deep_diagnostics_and_has_a_run_log(pages):
    page, frame = _app(pages)
    _nav(frame, "setup")
    steps = frame.locator("#setup-steps li.dx-step[data-step]")
    steps.first.wait_for(timeout=30000)
    assert steps.evaluate_all("els => els.map(e => e.dataset.step)") == [
        "dx-app-deps", "dx-rt-deps", "dx-rt-build", "dx-driver", "dx-app-build", "dx-app-setup"]
    assert frame.locator("#setup-run-all").count() == 1 and frame.locator("#setup-quickstart-btn").count() == 1
    assert frame.locator("#setup-log").count() == 1
    frame.locator("#diag-run-btn").click()
    frame.locator("#diag-results .diag-card").first.wait_for(timeout=120000)
    assert frame.locator("#diag-results .diag-card").count() >= 5


def test_models_search_category_detail_and_run_button(pages):
    page, frame = _app(pages)
    _nav(frame, "models")
    # The table first shows the runnable models, then the full catalog once it has loaded.
    frame.wait_for_function("() => typeof S !== 'undefined' && S.catalog && S.catalog.length > 0", timeout=60000)
    frame.locator("#m-search").fill("yolo")
    frame.wait_for_function("() => [...document.querySelectorAll('#m-table tbody tr')].every("
                            "r => /yolo/i.test(r.cells[0].textContent))", timeout=15000)
    cat = frame.locator("#m-table tbody tr:has(.m-action-run) td .badge.b-cat").first.inner_text().strip()
    frame.locator("#cat-chips .chip").filter(has_text=re.compile(rf"^\s*{re.escape(cat)}\s*$")).first.click()
    frame.wait_for_function("(c) => [...document.querySelectorAll('#m-table tbody tr')].every("
                            "r => r.cells[1].textContent.trim() === c)", arg=cat, timeout=15000)
    rows = frame.locator("#m-table tbody tr")
    row = frame.locator("#m-table tbody tr:has(.m-action-run)").first
    name = row.locator("td").first.inner_text().strip()
    row.locator(".m-action-detail").click()
    frame.locator("#modal-detail[open]").wait_for(timeout=15000)
    detail = frame.locator("#modal-detail").inner_text().replace("\u200b", "")
    assert name.replace("\u200b", "").lower() in detail.lower()
    frame.wait_for_function("() => document.querySelector('#md-body .badge.b-cat')?.textContent.trim().length > 0")
    assert "N/A" not in detail, "a runnable model's detail names its .dxnn"
    frame.locator("#modal-detail[open]").press("Escape")
    frame.wait_for_function("() => !document.querySelector('#modal-detail[open]')")
    assert rows.count() >= 1
    row.locator(".m-action-run").click()
    frame.locator("#page-run.active").wait_for(timeout=15000)
    frame.wait_for_function("() => !!document.getElementById('r-model').value", timeout=15000)


def test_run_inference_offers_image_video_camera_and_rtsp_inputs(pages):
    page, frame = _app(pages)
    _nav(frame, "run")
    assert frame.locator('.run-tab[data-rtab="single"]').count() == 1
    assert frame.locator("#r-upload").count() == 1 and frame.locator("#r-input-vid").count() == 1
    frame.locator('.run-tab[data-rtab="continuous"]').click()
    kinds = frame.locator("#c-input-type option").evaluate_all("els => els.map(e => e.value)")
    assert {"video", "camera", "rtsp"} <= set(kinds), kinds
    cams = json.loads(http_get(pages.studio.base + "/app/api/cameras", headers={"Sec-Fetch-Dest": "empty"})[2])
    assert isinstance(cams, list)
    frame.select_option("#c-input-type", "camera")
    if not cams:
        frame.wait_for_function(
            "() => (document.getElementById('c-camera')?.textContent || '').includes('No cameras found')", timeout=15000)
    frame.select_option("#c-input-type", "rtsp")
    frame.locator("#c-rtsp-ip").wait_for(state="visible", timeout=10000)


def test_run_inference_on_the_npu_shows_the_result_image_and_fps(pages):
    need("npu")
    page, frame = _app(pages)
    model = _runnable_model(frame)
    _nav(frame, "run")
    frame.select_option("#r-cat", model["category"])
    frame.wait_for_function("(n) => [...document.getElementById('r-model').options].some(o => o.value === n)",
                            arg=model["name"], timeout=30000)
    frame.select_option("#r-model", model["name"])
    frame.locator(".img-item").first.click()
    frame.locator("#r-run-btn").click()
    frame.wait_for_function("(s) => { const i = document.querySelector(s); return i && i.complete && i.naturalWidth > 0; }",
                            arg=RESULT_IMG, timeout=180000)
    fps = frame.evaluate("() => { const c = [...document.querySelectorAll('#r-result .pcard')]"
                         ".find(e => (e.querySelector('.pk')?.textContent || '').includes('FPS'));"
                         " return c ? c.querySelector('.pv').textContent : ''; }")
    m = re.search(r"\d+(\.\d+)?", fps or "")
    assert m and float(m.group()) > 0, fps


def test_continuous_camera_inference_on_the_npu_shows_live_frames(pages):
    """Not exercised on a board without a camera: the AC is NOT RUN there (hardware.need)."""
    need("camera", "npu")
    page, frame = _app(pages)
    model = _runnable_model(frame)
    _nav(frame, "run")
    frame.locator('.run-tab[data-rtab="continuous"]').click()
    frame.select_option("#c-input-type", "camera")
    frame.wait_for_function("() => [...document.getElementById('c-camera').options].some(o => o.value !== '')",
                            timeout=30000)
    slot_model = frame.locator("#c-slots select").first
    slot_model.wait_for(timeout=15000)
    if model["name"] in slot_model.locator("option").evaluate_all("els => els.map(e => e.value)"):
        slot_model.select_option(model["name"])
    frame.locator("#c-start-btn").click()
    frame.wait_for_function("() => { const i = document.getElementById('c-ls-img-0');"
                            " return i && i.complete && i.naturalWidth > 0; }", timeout=120000)
    frame.locator("#c-stop-btn").click()


def test_run_demo_on_the_npu_puts_the_result_on_the_stage(pages):
    need("npu")
    page, frame = _app(pages)
    _nav(frame, "rundemo")
    frame.locator(".dds-card").first.wait_for(timeout=30000)
    ready = frame.locator(".dds-card:not(:has(.dds-reason))")
    assert ready.count() > 0, "no demo is ready on this board"
    ready.first.click()
    frame.locator(".dds-run").first.click()
    frame.wait_for_function(
        "() => { const i = document.querySelector('.dds-media img'); return i && i.complete && i.naturalWidth > 0; }",
        timeout=240000)
    frame.locator(".dds-metric").first.wait_for(timeout=60000)


def test_benchmark_runs_the_checked_models_and_shows_results_and_a_chart(pages):
    page, frame = _app(pages)
    model = _runnable_model(frame)

    def run(route):
        route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "exit_code": 0, "fps": 123.4, "latency_ms": 8.1, "output": "", "elapsed": 1.2, "perf": {"fps": 123.4}}))

    # DX App calls /api/... from inside its iframe; the launcher routes it to DX App by the frame it came from.
    page.route("**/api/run", run)
    _nav(frame, "bench")
    chk = frame.locator(f'.b-chk[value="{model["name"]}"]')
    chk.wait_for(state="attached", timeout=30000)
    chk.check()
    frame.locator("#b-run-btn").click()
    frame.locator("#bench-res tbody tr").first.wait_for(timeout=60000)
    assert model["name"] in frame.locator("#bench-res").inner_text()
    frame.locator("#bench-chart").wait_for(state="attached", timeout=15000)


def test_ab_compare_has_two_to_eight_slots_and_shows_each_result(pages):
    page, frame = _app(pages)
    _nav(frame, "compare")
    for n in (2, 4, 6, 8):
        frame.locator(f'#ab-cols .btn[onclick="setABCols({n})"]').click()
        frame.wait_for_function("(n) => document.querySelectorAll('.ab-panel').length === n", arg=n)
    frame.locator('#ab-cols .btn[onclick="setABCols(2)"]').click()

    def run_multi(route):
        reqs = json.loads(route.request.post_data or "{}").get("requests", [])
        route.fulfill(status=200, content_type="application/json", body=json.dumps([
            {"exit_code": 0, "fps": 100 + i, "latency": 9.0, "output": "ok"} for i, _ in enumerate(reqs)]))

    page.route("**/api/run_multi", run_multi)
    model = _runnable_model(frame)
    for i in range(2):
        frame.wait_for_function("(id) => document.getElementById(id)?.options.length > 1", arg=f"ab-model-{i}",
                                timeout=30000)
        frame.select_option(f"#ab-model-{i}", model["name"])
    frame.wait_for_function("() => [...document.getElementById('ab-img').options].some(o => o.value)", timeout=30000)
    first_input = frame.evaluate("() => [...document.getElementById('ab-img').options].find(o => o.value).value")
    frame.select_option("#ab-img", first_input)
    frame.locator("#ab-run-btn").click()
    for i in range(2):
        frame.wait_for_function("(id) => (document.getElementById(id)?.textContent || '').includes('FPS')",
                                arg=f"ab-res-{i}", timeout=30000)
    frame.locator("#ab-cmp-table").wait_for(state="attached", timeout=15000)


def test_modelzoo_page_shows_sources_cart_and_download_all(pages):
    page, frame = _app(pages)
    sent = {}

    def download(route):
        sent["body"] = json.loads(route.request.post_data or "{}")
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"ok": True, "started": True}))

    page.route("**/api/modelzoo/download", download)
    # Offline, the default Public source answers slowly with an error. Make it slow on purpose: switching to
    # Internal meanwhile must not be undone by Public's late answer.
    frame.evaluate("""() => { const f = window.fetch; window.fetch = async (u, o) => {
        if (String(u).includes('modelzoo/list?source=public')) await new Promise(r => setTimeout(r, 3000));
        return f(u, o); }; }""")
    _nav(frame, "modelzoo")
    assert frame.locator("#mz-source option").evaluate_all("els => els.map(e => e.value)") == ["public", "internal"]
    frame.select_option("#mz-source", "internal")
    frame.locator("#mz-tbody tr").nth(5).wait_for(state="attached", timeout=60000)
    frame.wait_for_timeout(3500)     # Public's late answer arrives now
    assert frame.locator("#mz-tbody tr").count() > 5, "the Internal list stays after Public answers late"
    # Tiers already on disk show a "Downloaded" badge instead of a cart box; take the first box offered.
    box = frame.locator('input[onchange^="mzToggleChip"]').first
    box.wait_for(state="attached", timeout=30000)
    chip = re.search(r"'(qlite|qpro|qmaster)'", box.get_attribute("onchange")).group(1)
    box.click(force=True)   # the row re-renders as soon as the tier joins the cart
    cart = frame.locator("#mz-cart")
    cart.wait_for(state="visible", timeout=10000)
    assert re.search(r"\(\d+\)", cart.inner_text())
    frame.locator("#mz-cart button", has_text="Download All").click()
    frame.wait_for_function("() => true")
    for _ in range(20):
        if sent:
            break
        page.wait_for_timeout(250)
    assert sent.get("body", {}).get("items"), sent
    assert sent["body"]["items"][0]["chip"] == chip


def test_lab_offers_its_flows_and_opens_graph_composer(pages):
    page, frame = _app(pages)
    _nav(frame, "lab")
    flows = frame.locator("#lab-home [data-lab-flow]").evaluate_all("els => els.map(e => e.dataset.labFlow)")
    assert {"graph", "add-model", "create-task", "experiment", "generated", "safety"} <= set(flows), flows
    frame.locator('#lab-home [data-lab-flow="graph"]').first.click()
    frame.locator("#page-graph.active").wait_for(timeout=15000)


def test_graph_composer_runs_an_example_once_on_the_npu(pages):
    need("npu")
    page, frame = _app(pages)
    _nav(frame, "graph")
    frame.locator("#gc-palette-list .gc-example button").first.click()
    frame.wait_for_function("() => GraphComposer.state().check && GraphComposer.state().check.ok", timeout=30000)
    frame.locator("#gc-run").click()
    frame.locator(".gc-run-table tbody tr").first.wait_for(timeout=300000)
    result = frame.locator(".gc-run-result", has_text="Done").first
    result.wait_for(timeout=60000)
    assert "error" not in result.inner_text().lower()


def test_outputs_filter_and_view_and_reference_points_to_the_compiler(pages):
    page, frame = _app(pages)
    _nav(frame, "outputs")
    frame.locator(".out-filter-chip").first.wait_for(state="attached", timeout=15000)
    chips = frame.locator(".out-filter-chip").evaluate_all("els => els.map(e => e.dataset.filter)")
    assert chips == ["all", "image", "video", "archive", "other"], chips
    frame.locator('.out-view-btn[data-view="table"]').click()
    frame.locator('.out-view-btn[data-view="grid"]').click()
    _nav(frame, "reference")
    frame.locator("#ref-search").fill("compiler")
    card = frame.locator('.ref-topic-card[data-ref-id="compiler"]')
    card.wait_for(state="visible", timeout=10000)
    card.click()
    frame.wait_for_function("() => /Compiler/.test(document.getElementById('page-reference').innerText)")


def test_a_bad_run_request_gets_a_clear_error(studio):
    import urllib.request

    req = urllib.request.Request(studio.base + "/app/api/run", data=json.dumps({"category": "bogus", "model": "x"}).encode(),
                                 headers={"Content-Type": "application/json", "Origin": studio.base}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status, body = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, body = e.code, e.read()
    assert status in (400, 403, 404), status
    assert json.loads(body).get("error"), body
