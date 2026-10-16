"""Graph Composer Phase 3 in a browser: the Export C++ project button and its dialog.

/api/graph/* is answered in the page: the recorded catalog (fixtures/graph/catalog.json, with or without the export
capability), a clean or failing --check, the recorded export plan (export_plan.json) and export answer
(export_done.json). The server side has its own tests (test_graph_export.py, test_graph_routes.py).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "graph"
CATALOG = json.loads((FIX / "catalog.json").read_text(encoding="utf-8"))
PLAN = json.loads((FIX / "export_plan.json").read_text(encoding="utf-8"))
DONE = dict(json.loads((FIX / "export_done.json").read_text(encoding="utf-8")), name="person-attributes",
            folder="/home/u/outputs/dx_app/graph/exports/person-attributes-20261015-120000/person-attributes",
            zip_url="/outputs/graph/exports/person-attributes-20261015-120000/person-attributes.zip",
            zip_bytes=9 * 1048576)


class FakeApi:
    """In-page answers for /api/graph/*; `posted` keeps (route, body) of every call."""

    def __init__(self, export=True, check_ok=True, plan=None, done=None):
        self.posted, self.export, self.check_ok = [], export, check_ok
        self.plan, self.done = plan or (PLAN, 200), done or (DONE, 200)

    def handle(self, route):
        req = route.request
        url = req.url.split("?")[0]
        body = json.loads(req.post_data) if req.post_data else {}
        self.posted.append((url.rsplit("/api/graph/", 1)[1], body))
        status = 200
        if url.endswith("/api/graph/catalog"):
            out = json.loads(json.dumps(CATALOG))
            out["capabilities"] = dict(out["capabilities"], export=self.export)
        elif url.endswith("/api/graph/validate"):
            errors = [] if self.check_ok else [{"code": "GRAPH_EDGE", "where": "graph", "what": "x", "how": "",
                                                "node": None, "edge": "od->attr"}]
            out = {"ok": self.check_ok, "errors": errors, "models": [], "missing": [], "unusable": {}, "notes": [],
                   "available": True, "engine_ignored": False}
        elif url.endswith("/api/graph/memory"):
            out = {"nodes": {}, "engines": [], "total_bytes": 0, "device": {}, "over_budget": False,
                   "unknown_models": [], "suggestions": []}
        elif url.endswith("/api/graph/projects"):
            out = {"projects": []}
        elif url.endswith("/api/graph/export/plan"):
            out, status = self.plan
        elif url.endswith("/api/graph/export"):
            out, status = self.done
        else:
            out = {"error": "not found"}
        route.fulfill(status=status, content_type="application/json", body=json.dumps(out))


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    srv, port = start_module_server("dx_app")
    from dx_app.core import config
    mp = pytest.MonkeyPatch()
    mp.setattr(config, "OUTPUTS_DIR", tmp_path_factory.mktemp("outputs"))
    yield port
    mp.undo()
    srv.shutdown()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _page(browser, server, fake, lang="en"):
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    ctx.add_init_script("try { localStorage.setItem('dx-tutorial-mode', 'off'); localStorage.setItem('dx-lang', '%s');"
                        " localStorage.removeItem('dx-graph-draft'); window.confirm = () => true; } catch (e) {}" % lang)
    ctx.route("**/api/graph/**", fake.handle)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"http://127.0.0.1:{server}/", wait_until="domcontentloaded")
    page.wait_for_function("() => typeof nav === 'function' && window.GraphComposer && window.GraphExport")
    page.evaluate("nav('graph')")
    page.wait_for_function("() => GraphComposer.state().catalog", timeout=20000)
    page.evaluate("GraphComposer.loadExample('cascade_od_attr')")
    page.wait_for_function("() => GraphComposer.state().check", timeout=10000)
    return ctx, page, errors


@pytest.fixture
def ui(browser, server):
    fake = FakeApi()
    ctx, page, errors = _page(browser, server, fake)
    yield page, fake
    assert not errors, errors
    ctx.close()


def _open_dialog(page):
    page.wait_for_function("() => !document.getElementById('gc-export-cpp').disabled")
    page.click("#gc-export-cpp")
    page.wait_for_selector("#gc-export-dialog[open] .gc-export-table td")


@pytest.mark.parametrize("export, check_ok", [(False, True), (True, False)])
def test_the_button_waits_for_an_exporter_and_a_clean_graph(browser, server, export, check_ok):
    ctx, page, errors = _page(browser, server, FakeApi(export=export, check_ok=check_ok))
    assert page.is_disabled("#gc-export-cpp")
    assert page.get_attribute("#gc-export-cpp", "title") == \
        "Export needs a graph without problems and a dx_app that can export projects."
    assert not errors, errors
    ctx.close()


def test_the_dialog_shows_the_plan_and_exports_a_zip(ui):
    page, fake = ui
    _open_dialog(page)
    assert page.get_attribute("#gc-export-cpp", "title") is None
    assert page.input_value("#gc-export-name") == "person-attributes"
    assert page.evaluate("document.activeElement.id") == "gc-export-name"
    assert page.inner_text(".gc-export-table").split() == ["yolov8-n_640x640", "8", "MB"]
    inputs = page.inner_text(".gc-export-inputs")
    assert "inputs/sample_people.jpg" in inputs and "for source cam" in inputs
    assert "An uploaded image is not exported" in page.inner_text("#gc-export-plan")
    assert page.is_hidden("#gc-export-models-why")
    stubs = page.inner_text(".gc-export-stubs")
    assert "user_logic/tag_people.cpp" in stubs and "for node tag (input: boxes)" in stubs
    assert not page.is_checked("#gc-export-models") and page.is_enabled("#gc-export-models")
    assert page.inner_text("#gc-export-size") == "Include the model files (8 MB)"
    plan_body = [b for r, b in fake.posted if r == "export/plan"][0]
    assert plan_body["graph"]["nodes"] and plan_body["inputs"] == {}
    page.click("#gc-export-go")
    page.wait_for_selector("#gc-export-zip")
    route, body = fake.posted[-1]
    assert route == "export" and body["name"] == "person-attributes" and body["include_models"] is False
    assert page.get_attribute("#gc-export-zip", "href") == DONE["zip_url"]
    assert "Download .zip (9 MB)" in page.inner_text("#gc-export-zip")
    assert DONE["folder"] in page.inner_text("#gc-export-result")
    assert "./setup.sh" in page.inner_text(".gc-export-cmd")
    assert page.evaluate("document.activeElement.id") == "gc-export-zip"


def test_the_name_and_the_model_choice_reach_the_export(ui):
    page, fake = ui
    _open_dialog(page)
    page.fill("#gc-export-name", "9lives")
    assert page.is_disabled("#gc-export-go") and page.get_attribute("#gc-export-name", "aria-invalid") == "true"
    page.fill("#gc-export-name", "my-project_2")
    assert page.is_enabled("#gc-export-go")
    page.check("#gc-export-models")
    page.press("#gc-export-name", "Enter")
    page.wait_for_selector("#gc-export-zip")
    assert fake.posted[-1][1]["name"] == "my-project_2" and fake.posted[-1][1]["include_models"] is True


def test_a_missing_model_file_turns_the_model_choice_off(browser, server):
    plan = json.loads(json.dumps(PLAN))
    plan["models"][0].update(present=False, bytes=0)
    plan["model_bytes"] = 0
    ctx, page, errors = _page(browser, server, FakeApi(plan=(plan, 200)))
    _open_dialog(page)
    assert page.is_disabled("#gc-export-models") and not page.is_checked("#gc-export-models")
    # An older dx_app says 0 bytes for a file it does not have: that is not a size.
    assert page.inner_text(".gc-export-table").split("\t")[-1].strip() == "not installed, size unknown"
    assert page.inner_text("#gc-export-size") == "Include the model files (size unknown)"
    assert page.inner_text("#gc-export-models-why") == "Every model must be installed to include the files."
    assert "gc-export-models-why" in page.get_attribute("#gc-export-models", "aria-describedby")
    assert not errors, errors
    ctx.close()


def test_an_unknown_model_size_is_never_shown_as_a_size(browser, server):
    """The exporter gives bytes null for a model not installed whose download size it does not know, and the
    download size when it knows it: the table says which, and the total is a lower bound while a size is unknown."""
    plan = json.loads(json.dumps(PLAN))
    known = plan["models"][0]
    plan["models"] = [known,
                      dict(known, model="casvit-t_224x224", file="casvit-t_224x224.dxnn", present=False, bytes=None),
                      dict(known, model="resnet50_224x224", file="resnet50_224x224.dxnn", present=False,
                           bytes=3 * 1048576)]
    plan["model_bytes"], plan["model_bytes_unknown"] = known["bytes"] + 3 * 1048576, 1
    ctx, page, errors = _page(browser, server, FakeApi(plan=(plan, 200)))
    _open_dialog(page)
    rows = [r.split("\t") for r in page.inner_text(".gc-export-table").strip().split("\n")]
    assert [c.strip() for c in rows[1]] == ["casvit-t_224x224", "not installed, size unknown"]
    assert [c.strip() for c in rows[2]] == ["resnet50_224x224", "not installed (3 MB)"]
    assert page.inner_text("#gc-export-size") == "Include the model files (at least 11 MB)"
    assert page.is_disabled("#gc-export-models")
    page.evaluate("DXI18n.setLang('ko')")
    page.wait_for_function("() => document.getElementById('gc-export-size').textContent.startsWith('모델')")
    assert page.inner_text("#gc-export-size") == "모델 파일 포함 (최소 11 MB)"
    assert "설치 안 됨, 크기 알 수 없음" in page.inner_text(".gc-export-table")
    assert not errors, errors
    ctx.close()


def test_a_refusal_says_why_and_the_dialog_stays_usable(browser, server):
    refusal = ({"ok": False, "error": "node 'u': \"name\" 'class' must be a C++ name", "error_key": "user_name_invalid"}, 400)
    ctx, page, errors = _page(browser, server, FakeApi(done=refusal))
    _open_dialog(page)
    page.click("#gc-export-go")
    page.wait_for_function("() => !document.getElementById('gc-export-error').hidden")
    text = page.inner_text("#gc-export-error")
    assert text.startswith("A User logic block's name must be a C++ name") and "'class'" in text
    assert page.is_enabled("#gc-export-go") and not page.query_selector("#gc-export-zip")
    assert not errors, errors
    ctx.close()


def test_no_space_names_both_sizes(browser, server):
    full = ({"ok": False, "error": "x", "error_key": "export_no_space", "need_bytes": 300 * 1048576,
             "free_bytes": 100 * 1048576}, 507)
    ctx, page, errors = _page(browser, server, FakeApi(done=full))
    _open_dialog(page)
    page.click("#gc-export-go")
    page.wait_for_function("() => !document.getElementById('gc-export-error').hidden")
    assert page.inner_text("#gc-export-error") == "Not enough disk space: the export needs 300 MB and 100 MB is free."
    assert not errors, errors
    ctx.close()


def test_escape_closes_and_leaving_the_page_closes_it(ui):
    page, _ = ui
    _open_dialog(page)
    page.keyboard.press("Escape")
    assert not page.evaluate("GraphExport.isOpen()")
    _open_dialog(page)
    page.evaluate("nav('models')")
    assert not page.evaluate("GraphExport.isOpen()")


def test_the_dialog_follows_a_language_change(browser, server):
    ctx, page, errors = _page(browser, server, FakeApi(), lang="ko")
    _open_dialog(page)
    assert page.inner_text("#gc-export-title").strip() == "C++ 프로젝트 내보내기"
    assert page.inner_text("#gc-export-size") == "모델 파일 포함 (8 MB)"
    page.evaluate("DXI18n.setLang('en')")
    page.wait_for_function("() => document.getElementById('gc-export-size').textContent.startsWith('Include')")
    assert page.inner_text("#gc-export-close") == "Close"
    assert not errors, errors
    ctx.close()


def test_a_ticked_model_choice_does_not_outlive_the_dialog(ui):
    """Each opening starts from the default: the model files left out."""
    page, fake = ui
    _open_dialog(page)
    page.check("#gc-export-models")
    page.keyboard.press("Escape")
    _open_dialog(page)
    assert not page.is_checked("#gc-export-models")
    page.click("#gc-export-go")
    page.wait_for_selector("#gc-export-zip")
    assert fake.posted[-1][1]["include_models"] is False


def test_typing_keeps_the_caret_when_the_plan_arrives(ui):
    page, _ = ui
    _open_dialog(page)
    page.fill("#gc-export-name", "abcdef")
    page.evaluate("() => { const n = document.getElementById('gc-export-name'); n.setSelectionRange(2, 2); }")
    page.evaluate("GraphExport.refreshLanguage()")
    assert page.evaluate("document.activeElement.id") == "gc-export-name"
    assert page.evaluate("document.getElementById('gc-export-name').selectionStart") == 2
