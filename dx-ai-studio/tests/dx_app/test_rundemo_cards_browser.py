"""dx_app Run Demo: a result stage plus cards used for picking.

Cards only select a demo; options, Run and results live in the stage at the top of the page (the shared
DXDemoStage), so a result never stretches a narrow card.

/api/demos and the run APIs are fixtures, independent of which models are installed on this machine.
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

READY = {"cpp_sync": True, "cpp_async": True, "py_sync": True, "py_async": True,
         "py_sync_cpp_postprocess": False, "py_async_cpp_postprocess": False, "model_exists": True}
MISSING = {k: False for k in READY}
PY_POST = {"cpp_sync": False, "cpp_async": False, "py_sync": True, "py_async": False,
           "py_sync_cpp_postprocess": True, "py_async_cpp_postprocess": False, "model_exists": True}


def _demo(idx, label, group, cat, name, avail):
    return {"idx": idx, "label": label, "group": group, "model": f"{name}.dxnn", "category": cat,
            "model_name": name, "py_base": name, "cpp_base": name, "default_video": "assets/videos/boat.mp4",
            "default_image": "sample/img/sample_street.jpg", "async_full": True, "image_only": False,
            "avail": dict(avail), "run_ref": {"model_name": name, "category": cat, "model_file": f"{name}.dxnn"},
            "thumbnail": f"/api/demo-thumb?f={name}.jpg"}


DEMOS = [
    _demo(0, "Object Detection         (YOLOv7)", "Detection", "object_detection", "yolov7", READY),
    _demo(1, "Face Detection           (SCRFD500M)", "Detection", "face_detection", "scrfd500m", MISSING),
    _demo(2, "Object Detection + Semantic Segmentation (YOLOv7 + BiSeNet)", "Segmentation",
          "object_detection_x_semantic_segmentation", "yolov7_bisenet", MISSING),
    _demo(3, "Pose Estimation          (YOLOv8s-Pose)", "Keypoint & Pose", "pose_estimation", "yolov8s_pose", PY_POST),
]
DEMOS[3]["media"] = {"video": False, "image": True}     # sample video not downloaded on this PC

# 1×1 png: only checks that the result image lands in the stage media
PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
RESULT = {"running": False, "exit_code": 0, "fps": 2.8, "latency": 56.2, "elapsed_s": 0.93, "result_image": PNG,
          "perf": {"pipeline": [{"step": "Read", "latency_ms": 202.0}, {"step": "Pre", "latency_ms": 16.0},
                                {"step": "Infer", "latency_ms": 57.0}, {"step": "Post", "latency_ms": 0.4}]},
          "output": "[INFO] done"}


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_app")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off');")
    pg = ctx.new_page()
    pg.route("**/api/demos", lambda route, *_: route.fulfill(
        status=200, content_type="application/json",
        body=json.dumps({"ok": True, "demos": DEMOS, "groups": ["Detection", "Segmentation", "Keypoint & Pose"]})))
    pg.bodies = []

    def _run_async(route, request):
        pg.bodies.append(json.loads(request.post_data or "{}"))
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"job_id": "j1"}))

    pg.route("**/api/run_async", _run_async)
    pg.route("**/api/run_poll?*", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps({"running": False})))
    pg.route("**/api/run_result?*", lambda route, *_: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(RESULT)))
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.evaluate("() => nav('rundemo')")
    pg.wait_for_selector("#rundemo-root .dds-card[data-id='3']", timeout=10000)
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _task(page, sel):
    return page.evaluate(f"""() => {{ const t = document.querySelector("{sel} .dds-task");
      return [t.querySelector('use').getAttribute('href').split('#')[1], t.textContent.trim()]; }}""")


def test_cards_name_the_task_once_and_title_the_model(page):
    assert _task(page, ".dds-card[data-id='0']") == ["task-object_detection", "Object Detection"]
    assert page.inner_text(".dds-card[data-id='0'] .dds-ctitle").strip() == "YOLOv7"
    assert _task(page, ".dds-card[data-id='2']")[0] == "task-object_detection"
    assert page.inner_text(".dds-card[data-id='2'] .dds-ctitle").strip() == "YOLOv7 + BiSeNet"


def test_the_first_ready_demo_is_open_on_the_stage(page):
    assert page.inner_text("#rundemo-root .dds-stage .dds-title").strip() == "YOLOv7"
    assert page.inner_text("#rundemo-root .dds-stage .dds-model").strip() == "yolov7.dxnn"
    assert page.get_attribute("#rundemo-root .dds-media img", "src").endswith("yolov7.jpg")


def test_options_and_run_live_on_the_stage_not_on_cards(page):
    assert page.locator(".dds-card[data-id='0'] button:not(.dds-cpick)").count() == 0
    for axis in ("input", "code", "mode"):
        assert page.is_visible(f".dds-stage [data-axis-row='{axis}']"), axis
    assert page.is_visible(".dds-stage .dds-run")
    # Plain text, not monospace capitals (INPUT · CODE)
    tt, ff, text = page.evaluate("""() => { const l = document.querySelector('.dds-stage .dds-opt-label');
      const cs = getComputedStyle(l); return [cs.textTransform, cs.fontFamily, l.textContent]; }""")
    assert tt == "none" and "mono" not in ff.lower() and text == "Input", (tt, ff, text)


def test_filters_are_the_groups(page):
    keys = page.evaluate("[...document.querySelectorAll('.dds-filter button')].map(b => b.dataset.key)")
    assert keys == ["all", "Detection", "Segmentation", "Keypoint & Pose"]
    page.click(".dds-filter button[data-key='Segmentation']")
    try:
        assert page.evaluate("[...document.querySelectorAll('.dds-card')].filter(c => c.offsetParent).map(c => c.dataset.id)") == ["2"]
    finally:
        page.click(".dds-filter button[data-key='all']")


def test_a_not_ready_card_gives_one_short_reason(page):
    reason = page.locator(".dds-card[data-id='1'] .dds-reason")
    assert reason.inner_text().strip() == "Model not installed"
    assert "scrfd500m.dxnn" in reason.get_attribute("title")
    page.click(".dds-card[data-id='1'] .dds-setup")
    page.wait_for_function("() => document.getElementById('page-setup').classList.contains('active')", timeout=5000)
    page.evaluate("() => nav('rundemo')")
    assert page.inner_text(".dds-stage .dds-title").strip() == "YOLOv7", "Set up 은 card 를 고르지 않는다"


def test_run_puts_the_result_on_the_stage(page):
    page.bodies.clear()
    page.click(".dds-card[data-id='0']")
    page.click(".dds-stage [data-axis='input'][data-val='image']")
    page.click(".dds-stage .dds-run")
    page.wait_for_function("() => document.querySelector('.dds-state')?.dataset.kind === 'done'", timeout=10000)
    assert page.evaluate("document.querySelector('.dds-media img').src.startsWith('data:image')")
    assert page.bodies[0]["input_type"] == "image" and page.bodies[0]["image_path"] == "sample/img/sample_street.jpg"
    metrics = page.evaluate("[...document.querySelectorAll('.dds-metric')].map(m => m.innerText.replace(/\\s+/g, ' ').trim())")
    assert metrics == ["2.8 FPS", "56.2 ms NPU latency", "0.93 s Total"], metrics
    assert page.locator(".dds-bars .dds-bar i").count() == 4
    assert "Infer 57 ms" in page.inner_text(".dds-bars")
    assert "Full output" in page.inner_text(".dds-extra")
    assert page.bodies and page.bodies[0]["model_name"] == "yolov7" and page.bodies[0]["lang"] == "cpp"


def test_the_result_comes_back_when_the_demo_is_opened_again(page):
    page.click(".dds-card[data-id='3']")
    assert page.locator(".dds-metric").count() == 0
    page.click(".dds-card[data-id='0']")
    assert page.locator(".dds-metric").count() == 3


def test_cpp_postprocess_reaches_the_run(page):
    """Choosing Postprocess 'C++' must give a *_cpp_postprocess variant."""
    page.bodies.clear()
    page.click(".dds-card[data-id='3']")
    page.click(".dds-stage [data-axis='post'][data-val='on']")
    page.click(".dds-stage .dds-run")
    page.wait_for_function("() => document.querySelector('.dds-state')?.dataset.kind === 'done'", timeout=10000)
    assert page.bodies[0]["lang"] == "python" and page.bodies[0]["variant"] == "sync_cpp_postprocess", page.bodies


def test_the_result_marks_are_icons(page):
    out = page.evaluate("""() => { const el = document.createElement('div'); document.body.appendChild(el);
      window.renderInferenceResult(el, { _cat: 'object_detection', exit_code: 1, fps: 30, output: 'log' });
      return [...el.querySelectorAll('svg.res-mark use')].map(u => u.getAttribute('href').split('#')[1]); }""")
    assert out == ["x", "alert", "file"], out


def test_the_task_name_follows_the_language_without_redrawing(page):
    page.evaluate("() => { document.querySelector(\".dds-card[data-id='0']\").dataset.probe = '1'; DXI18n.setLang('ko'); }")
    page.wait_for_timeout(300)
    try:
        assert page.inner_text(".dds-card[data-id='0'] .dds-task").strip() == "객체 탐지"
        assert page.get_attribute(".dds-card[data-id='0']", "data-probe") == "1", "card 를 다시 그렸다 (고른 설정 · 결과가 사라진다)"
    finally:
        page.evaluate("() => DXI18n.setLang('en')")


def test_a_sample_video_that_is_not_downloaded_is_not_the_default(page):
    page.click(".dds-card[data-id='3']")
    video = page.locator(".dds-stage [data-axis='input'][data-val='video']")
    assert video.is_disabled()
    assert "not downloaded" in (video.get_attribute("title") or "")
    assert "is-on" in page.get_attribute(".dds-stage [data-axis='input'][data-val='image']", "class")


def test_the_stage_and_card_words_follow_the_language(page):
    """Switching language changes the stage's options, Run, status and metric names, and the reason on cards that
    are not ready; cards are not re-rendered and the stage keeps its result."""
    page.click(".dds-card[data-id='0']")            # the demo with the previous test's result (Done)
    page.evaluate("() => { document.querySelector(\".dds-card[data-id='1']\").dataset.probe = '1'; DXI18n.setLang('ko'); }")
    page.wait_for_timeout(300)
    try:
        assert page.inner_text(".dds-stage .dds-opt-label >> nth=0").strip() == "입력"
        assert page.inner_text(".dds-stage .dds-run").strip() == "실행"
        assert page.inner_text(".dds-stage .dds-state").strip() == "완료"
        assert "NPU 지연" in page.inner_text(".dds-metrics")
        assert page.evaluate("document.querySelector('.dds-media img').src.startsWith('data:image')"), "결과가 남는다"
        assert page.inner_text(".dds-card[data-id='1'] .dds-reason").strip() == "모델 미설치"
        assert page.inner_text(".dds-card[data-id='1'] .dds-cstate").strip() == "설치 필요"
        assert page.inner_text(".dds-card[data-id='1'] .dds-setup").strip() == "설정하기"
        assert page.get_attribute(".dds-card[data-id='1']", "data-probe") == "1", "card 를 다시 그렸다"
    finally:
        page.evaluate("() => DXI18n.setLang('en')")
