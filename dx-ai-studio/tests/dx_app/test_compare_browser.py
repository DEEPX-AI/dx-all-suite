"""DX App A/B compare — what a user saw running two models side by side (found on the DX-M1 board).

- The language select was always "C++ (Compiled) / Python" with C++ first, also for a model that
  has only a Python example: the run failed and the slot just said "No visual result".
- A failed slot never showed why (the run's `error`), and printed "Exit code: undefined".
- The shared input defaulted to the first entry, a pair FOLDER (sample/img/face_pair): the
  "Original" thumbnail was a broken image.
/api/models · /api/images · /api/videos · /api/run_multi are fixtures.
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

MODELS = [
    {"name": "both_640", "category": "object_detection", "category_label": "Object Detection",
     "model_file": "assets/models/both_640.dxnn", "model_exists": True,
     "cpp": True, "python": True, "cpp_sync": True, "py_sync": True},
    {"name": "py_only_640", "category": "object_detection", "category_label": "Object Detection",
     "model_file": "assets/models/py_only_640.dxnn", "model_exists": True,
     "cpp": False, "python": True, "cpp_sync": False, "py_sync": True},
]
IMAGES = ["sample/img/face_pair", "sample/img/sample_dog.jpg"]
RUN = [{"exit_code": 0, "fps": 40.1, "latency": 25.0, "result_image": ""},
       {"error": "Binary not found: py_only_640_sync — run build.sh", "error_code": "binary_not_found"}]


def _json(body):
    return lambda route, *_: route.fulfill(status=200, content_type="application/json", body=json.dumps(body))


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_app")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off'); localStorage.setItem('dx-lang','en');")
    pg = ctx.new_page()
    pg.route("**/api/models", _json(MODELS))
    pg.route("**/api/images", _json(IMAGES))
    pg.route("**/api/videos", _json([]))
    pg.route("**/api/run_multi", _json(RUN))
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    pg.evaluate("() => nav('compare')")
    pg.wait_for_selector("#ab-model-1", timeout=10000)
    pg.wait_for_function("() => document.querySelectorAll('#ab-img option').length >= 2", timeout=10000)
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def _langs(page, i):
    return page.evaluate(f"[...document.getElementById('ab-lang-{i}').options].map(o => o.value)")


def test_the_language_choice_follows_the_model(page):
    page.select_option("#ab-model-0", "both_640")
    page.select_option("#ab-model-1", "py_only_640")
    assert _langs(page, 0) == ["cpp", "python"]
    assert _langs(page, 1) == ["python"]
    assert page.input_value("#ab-lang-1") == "python"


def test_the_shared_input_defaults_to_an_image_file_not_a_folder(page):
    assert page.input_value("#ab-img") == "sample/img/sample_dog.jpg"


def test_a_failed_slot_says_why(page):
    page.select_option("#ab-model-0", "both_640")
    page.select_option("#ab-model-1", "py_only_640")
    page.click("#ab-run-btn")
    page.wait_for_function("() => /Binary not found/.test(document.getElementById('ab-res-1').textContent)",
                           timeout=10000)
    assert "undefined" not in page.inner_text("#ab-res-1")
    assert "40.1" in page.inner_text("#ab-res-0")
