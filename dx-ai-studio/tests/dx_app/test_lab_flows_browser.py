"""DX App Lab flows in the browser (2026-10-11 real-use audit).

- Add Model offered a Postprocessor list from every category and failed on apply; it now copies an existing
  example, so "Start from" lists the examples of the chosen category that have code in the chosen language.
- Experiment sat on "compile / pending" forever; the run now advances on the server and the page polls it to
  the end and shows the throughput.
- Safety Center's Rollback only said "preview only"; an applied change is rolled back after typing
  rollback:<name>, and an applied change that overwrote files says so instead.
"""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_app")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','en')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
    pg.evaluate("nav('lab')")
    pg.wait_for_function("() => window.LabPortal && LabPortal.capabilities() && LabPortal.capabilities().reference_examples",
                         timeout=20000)
    # Lab opens the Composer into #lab-flow-root once it is ready; let that land before a test opens a flow
    pg.wait_for_selector("#lab-flow-root .lab-composer", timeout=20000)
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def test_start_from_follows_category_and_language(page):
    page.click('[data-lab-flow="add-model"]')
    page.wait_for_selector("#wiz-base-model")
    refs = page.evaluate("LabPortal.capabilities().reference_examples")
    cats = page.eval_on_selector_all("#wiz-category option", "els => els.map(e => e.value)")
    assert cats and all(refs.get(c) for c in cats), "only categories with an example to copy are offered"
    cat = "object_detection" if "object_detection" in cats else cats[0]
    page.select_option("#wiz-category", cat)
    for lang, need in (("both", {"python", "cpp"}), ("python", {"python"}), ("cpp", {"cpp"})):
        page.select_option("#wiz-lang", lang)
        shown = page.eval_on_selector_all("#wiz-base-model option", "els => els.map(e => e.value)")
        expected = [r["name"] for r in refs[cat] if need <= set(r["langs"])]
        assert shown == (expected or [""]), (lang, shown[:3], expected[:3])
    assert not page.query_selector("#wiz-postprocessor")


def test_experiment_polls_to_the_end_and_shows_throughput(page):
    states = iter([
        {"status": "running", "current_step": "smoke",
         "steps": [{"id": "inspect", "status": "done"}, {"id": "smoke", "status": "current"},
                   {"id": "benchmark", "status": "pending"}], "log_tail": ["$ run_model -s"]},
        {"status": "completed", "current_step": "benchmark", "result": {"fps": 183.05},
         "steps": [{"id": "inspect", "status": "done"}, {"id": "smoke", "status": "done"},
                   {"id": "benchmark", "status": "done"}], "log_tail": ["  - FPS : 183.05"]},
    ])
    base = {"id": "run_1_test", "inputs": {}, "blockers": [], "created_at": 0, "updated_at": 0}

    def start(route):
        body = dict(base, status="pending", current_step="inspect", log_tail=[],
                    steps=[{"id": s, "status": "current" if s == "inspect" else "pending"}
                           for s in ("inspect", "smoke", "benchmark")])
        route.fulfill(status=200, content_type="application/json", body=json.dumps(body))

    def poll(route):
        route.fulfill(status=200, content_type="application/json", body=json.dumps(dict(base, **next(states))))

    page.route("**/api/lab/experiment/start", start)
    page.route("**/api/lab/experiment/run_1_test", poll)
    try:
        page.click('[data-lab-flow="experiment"]')
        page.fill("#exp-source-path", "outputs/m.dxnn")
        page.click(".btn-experiment-start")
        page.wait_for_selector(".exp-run-completed", timeout=10000)
        text = page.inner_text("#exp-run-display")
        assert "Throughput: 183.1 FPS" in text
        assert [t.strip() for t in page.eval_on_selector_all(".exp-step", "els => els.map(e => e.textContent)")] == \
            ["Read the model", "One inference", "Benchmark"]
        assert page.eval_on_selector_all(".exp-step-done", "els => els.length") == 3
    finally:
        page.unroute("**/api/lab/experiment/start")
        page.unroute("**/api/lab/experiment/run_1_test")


def test_safety_center_rolls_back_only_after_the_typed_confirmation(page):
    manifests = {"manifests": [
        {"id": "lab_1_a", "kind": "add_model", "status": "applied", "summary": "Add my_net to object_detection",
         "rollback": {"supported": True, "paths": ["src/python_example/object_detection/my_net"],
                      "confirmation": {"key": "rollback", "expected": "rollback:my_net"}}},
        {"id": "lab_1_b", "kind": "add_model", "status": "applied", "summary": "Add old_net to object_detection",
         "rollback": {"supported": False, "paths": []}},
    ]}
    posted = []
    page.route("**/api/lab/manifests", lambda r: r.fulfill(status=200, content_type="application/json",
                                                           body=json.dumps(manifests)))

    def rollback(route):
        posted.append(json.loads(route.request.post_data or "{}"))
        route.fulfill(status=200, content_type="application/json",
                      body=json.dumps({"ok": True, "removed": ["src/python_example/object_detection/my_net"]}))

    page.route("**/api/lab/rollback", rollback)
    try:
        page.click('[data-lab-flow="safety"]')
        page.wait_for_selector(".btn-safety-rollback")
        assert page.eval_on_selector_all(".btn-safety-rollback", "els => els.length") == 1
        assert "overwrote existing files" in page.inner_text("#lab-flow-root")
        btn = page.locator(".btn-safety-rollback")
        assert btn.is_disabled()
        page.fill(".safety-rollback-confirm", "rollback:other")
        assert btn.is_disabled()
        page.fill(".safety-rollback-confirm", "rollback:my_net")
        btn.click()
        page.wait_for_selector(".safety-ok", timeout=5000)
        assert posted == [{"manifest_id": "lab_1_a", "confirmations": {"rollback": "rollback:my_net"}}]
    finally:
        page.unroute("**/api/lab/manifests")
        page.unroute("**/api/lab/rollback")


def test_change_preview_paths_wrap_inside_the_card_at_phone_width(page):
    """At 390 px the dry-run paths (src/python_example/<category>/<name>) ran out of the card, clipped."""
    page.set_viewport_size({"width": 390, "height": 900})
    try:
        page.click('[data-lab-flow="add-model"]')
        page.wait_for_selector("#wiz-base-model")
        page.fill("#wiz-model-name", "a_rather_long_model_name_for_a_phone")
        page.click(".btn-dry-run")
        page.wait_for_selector(".manifest-ops li")
        over = page.evaluate("""() => { const card = document.getElementById('lab-flow-root').getBoundingClientRect();
            return [...document.querySelectorAll('.manifest-ops li')].filter(li => li.scrollWidth > li.clientWidth + 1
                || li.getBoundingClientRect().right > card.right + 1).length; }""")
        assert over == 0
    finally:
        page.set_viewport_size({"width": 1440, "height": 900})
