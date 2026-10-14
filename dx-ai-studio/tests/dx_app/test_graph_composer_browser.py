"""Graph Composer page in a browser, with the graph API answered from recorded fixtures.

The server modules have their own tests against recorded CLI output; here the page is checked end to end: palette,
canvas, inspector edits that change the dx_app graph, validation pins, the memory bar and its suggestions, a run,
projects and a language switch. /api/graph/* is routed to fixed payloads so no NPU or graph binary is needed.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "graph"
CATALOG = json.loads((FIX / "catalog.json").read_text(encoding="utf-8"))
MB = 1024 * 1024
RESULT = {"ok": True, "exit_code": 0, "frames": 2, "error_frames": 0, "fps": 14.7, "avg_fps": 14.7, "elapsed": 1.2,
          "node_ms": {"attr": 6.0, "od": 10.0}, "errors": [], "log_tail": "",
          "outputs": [{"url": "/static/shared/favicons/dx_app.svg", "kind": "image", "name": "result.jpg"}],
          "nodes": {"od": {"shape": "boxes", "frames": 2, "items_total": 3, "crops_total": 0,
                           "last_items": [{"class_name": "person", "score": 0.9}]},
                    "attr": {"shape": "scores", "frames": 2, "items_total": 0, "crops_total": 3, "last_items": []}}}


class FakeGraphApi:
    """In-page answers for /api/graph/*: --check, memory, run and projects."""

    def __init__(self):
        self.projects, self.runs, self.over_budget, self.posted = {}, 0, False, []

    def check(self, graph):
        errors = []
        for e in graph.get("edges", []):
            if e["to"] == "depth" and "roi" in e:
                errors.append({"code": "GRAPH_EDGE", "where": 'edge "%s"->"depth"' % e["from"],
                               "what": '"depth" requires a full frame', "how": 'remove "roi" from this edge',
                               "node": None, "edge": e["from"] + "->depth"})
        for n in graph.get("nodes", []):
            if n.get("model") == "no_such_model":
                errors.append({"code": "MODEL_UNKNOWN", "where": 'node "%s"' % n["id"], "what": "unknown model",
                               "how": "run --list-models", "node": n["id"], "edge": None})
        return {"ok": not errors, "errors": errors, "models": [], "missing": [], "notes": [], "available": True,
                "engine_ignored": False}

    def memory(self, graph):
        nodes = [n for n in graph.get("nodes", []) if n.get("model")]
        per = {n["id"]: {"model": n["model"], "bytes": 118 * MB, "shared_with": [], "buffers": 6} for n in nodes}
        sug = [{"kind": "share", "model": nodes[0]["model"], "nodes": [nodes[0]["id"]], "saves_bytes": 100 * MB}] if nodes else []
        return {"nodes": per, "engines": [{"model": n["model"], "nodes": [n["id"]], "buffers": None, "bytes": 118 * MB} for n in nodes],
                "total_bytes": 118 * MB * len(nodes), "device": {"total_bytes": 4000 * MB, "used_bytes": 0,
                "free_bytes": (100 if self.over_budget else 4000) * MB, "source": "device_status"},
                "over_budget": self.over_budget, "unknown_models": [], "suggestions": sug if self.over_budget else []}

    def handle(self, route):
        req = route.request
        url = req.url.split("?")[0]
        body = json.loads(req.post_data) if req.post_data else {}
        self.posted.append((url.rsplit("/api/graph/", 1)[1], body))
        q = dict(p.split("=", 1) for p in req.url.split("?", 1)[1].split("&")) if "?" in req.url else {}
        if url.endswith("/api/graph/catalog"):
            out = CATALOG
        elif url.endswith("/api/graph/validate"):
            out = self.check(body["graph"])
        elif url.endswith("/api/graph/memory"):
            out = self.memory(body["graph"])
        elif url.endswith("/api/graph/run"):
            self.runs += 1
            out = {"job_id": "job1", "status": "started"}
        elif url.endswith("/api/graph/run/poll"):
            out = {"running": False, "frames": 2, "fps": 14.7, "avg_fps": 14.7, "node_ms": {"od": 10.2, "attr": 5.9},
                   "elapsed": 1.2, "has_result": True}
        elif url.endswith("/api/graph/run/result"):
            out = RESULT
        elif url.endswith("/api/graph/projects"):
            out = {"projects": [{"id": k, "name": v["meta"]["name"], "version": v["meta"]["version"], "saved_at": 0,
                                 "versions": v["meta"]["version"]} for k, v in self.projects.items()]}
        elif url.endswith("/api/graph/project/save"):
            pid = body.get("id") or "my-graph"
            prev = self.projects.get(pid, {"meta": {"version": 0}})["meta"]["version"]
            project = body["project"]
            project["meta"] = dict(project["meta"], version=prev + 1)
            self.projects[pid] = project
            out = {"id": pid, "version": prev + 1, "name": project["meta"]["name"]}
        elif url.endswith("/api/graph/project/versions"):
            p = self.projects.get(q.get("id"))
            out = {"id": q.get("id"), "versions": [{"version": p["meta"]["version"], "saved_at": 0}] if p else []}
        elif url.endswith("/api/graph/project"):
            p = self.projects[q["id"]]
            out = {"id": q["id"], "version": p["meta"]["version"], "project": p}
        else:
            out = {"error": "not found"}
        route.fulfill(status=200, content_type="application/json", body=json.dumps(out))


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    srv, port = start_module_server("dx_app")
    # /api/graph/* is answered in the page, but should anything reach the server, its projects and runs land in a
    # temporary outputs folder, never in the user's outputs/dx_app/graph/.
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


@pytest.fixture
def ui(browser, server):
    fake = FakeGraphApi()
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    ctx.add_init_script("try { localStorage.setItem('dx-tutorial-mode', 'off'); localStorage.setItem('dx-lang', 'en');"
                        " localStorage.removeItem('dx-graph-draft'); window.confirm = () => true; } catch (e) {}")
    ctx.route("**/api/graph/**", fake.handle)
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"http://127.0.0.1:{server}/", wait_until="domcontentloaded")
    page.wait_for_function("() => typeof nav === 'function' && window.GraphComposer")
    page.evaluate("nav('graph')")
    page.wait_for_selector("#gc-palette-list .gc-group[data-group='examples'] .gc-item", timeout=20000)
    yield page, fake
    assert not errors, errors
    ctx.close()


def _open_example(page):
    page.click("#gc-palette-list .gc-example button")
    page.wait_for_function("() => GraphComposer.state().check && GraphComposer.state().check.ok", timeout=10000)


def _engine(page):
    return page.evaluate("GraphComposer.ctx().engine()")


def test_the_palette_offers_examples_sources_models_and_cpu_ops(ui):
    page, _ = ui
    groups = page.eval_on_selector_all("#gc-palette-list .gc-group:not(.is-empty)", "els => els.map(e => e.dataset.group)")
    assert groups[:2] == ["examples", "sources"] and groups[-1] == "cpu"
    assert "task:object_detection" in groups
    page.click("[data-group='task:object_detection'] .gc-group-head")
    states = page.eval_on_selector_all("[data-group='task:object_detection'] .gc-item",
                                       "els => els.map(e => [e.querySelector('.gc-item-name').textContent, e.querySelector('.badge').textContent])")
    assert ["yolo26-n_640x640_pre-optimized", "Not installed"] in states and ["yolov8-n_640x640", "Installed"] in states
    assert page.locator("[data-group='task:object_detection'] .gc-item .btn", has_text="Download").count() == 2


def test_an_example_opens_as_a_valid_graph_ready_to_run(ui):
    page, _ = ui
    _open_example(page)
    eng = _engine(page)
    assert [n["id"] for n in eng["nodes"]] == ["cam", "od", "attr"]
    assert eng["edges"][1] == {"from": "od", "to": "attr", "roi": {"classes": ["person"], "pad": 0.05}}
    assert page.inner_text("#gc-status") == "Ready to run"
    assert page.is_enabled("#gc-run")


def test_inspector_edits_change_the_dx_app_graph(ui):
    page, _ = ui
    _open_example(page)
    page.evaluate("GraphComposer.canvas().select({nodes: ['od']})")
    page.fill(".gc-param input[aria-label='score_threshold']", "0.5")
    page.dispatch_event(".gc-param input[aria-label='score_threshold']", "change")
    assert _engine(page)["nodes"][1]["params"] == {"score_threshold": 0.5}
    page.evaluate("GraphComposer.canvas().select({edge: 'od->attr'})")
    classes = page.locator("#gc-inspector-body .gc-fg", has_text="Classes").locator("input")
    classes.fill("person, rider")
    classes.dispatch_event("change")
    assert _engine(page)["edges"][1]["roi"]["classes"] == ["person", "rider"]
    assert page.evaluate("GraphComposer.canvas().getGraph().edges[1].label") == "ROI · person, rider"


def test_check_errors_are_pinned_and_block_the_run(ui):
    page, _ = ui
    _open_example(page)
    page.evaluate("GraphComposer.canvas().select({nodes: ['attr']})")
    model = page.locator("#gc-inspector-body .gc-fg", has_text="Model").locator("select")
    page.evaluate("""() => { const s = [...document.querySelectorAll('#gc-inspector-body select')][0];
      const o = document.createElement('option'); o.value = 'no_such_model'; s.appendChild(o); }""")
    model.select_option("no_such_model")
    page.wait_for_function("() => GraphComposer.state().check && !GraphComposer.state().check.ok")
    assert page.inner_text("#gc-status") == "1 problems to fix"
    assert not page.is_enabled("#gc-run")
    assert "MODEL_UNKNOWN" in page.inner_text("#gc-inspector-body .gc-error")


def test_memory_over_budget_offers_a_fix(ui):
    page, fake = ui
    fake.over_budget = True
    _open_example(page)
    page.wait_for_selector("#gc-memory.is-over .gc-mem-tips button")
    assert "Share one engine between od" in page.inner_text("#gc-memory")
    assert not page.is_enabled("#gc-run")
    page.click("#gc-memory .gc-mem-tips button")
    assert _engine(page)["nodes"][1]["engine"] == {"share": True}


def test_a_run_shows_progress_results_and_per_node_time(ui):
    page, fake = ui
    _open_example(page)
    page.click("#gc-run")
    page.wait_for_selector(".gc-run-table tbody tr")
    assert fake.runs == 1
    posted = [b for path, b in fake.posted if path == "run"][0]
    assert posted["variant"] == "sync" and [n["id"] for n in posted["graph"]["nodes"]] == ["cam", "od", "attr"]
    assert "Done: 2 frames in 1.2 s" in page.inner_text(".gc-run-result")
    rows = page.eval_on_selector_all(".gc-run-table tbody tr", "els => els.map(e => e.textContent)")
    assert any(r.startswith("od") and r.endswith("10.0") for r in rows)
    page.click(".gc-run-table tbody button:text('attr')")
    assert page.evaluate("GraphComposer.canvas().selection().nodes") == ["attr"]
    assert "Last run" in page.inner_text("#gc-inspector-body")


def test_projects_save_and_open_again(ui):
    page, _ = ui
    _open_example(page)
    page.fill("#gc-name", "My graph")
    page.dispatch_event("#gc-name", "change")
    page.click("#gc-save")
    page.wait_for_function("() => GraphComposer.state().projectId === 'my-graph'")
    page.click("#gc-new")
    assert page.evaluate("GraphComposer.canvas().getGraph().nodes.length") == 0
    page.select_option("#gc-projects", "my-graph")
    page.wait_for_function("() => GraphComposer.canvas().getGraph().nodes.length === 3")
    assert page.input_value("#gc-name") == "My graph"
    assert page.input_value("#gc-versions") == "1"


def test_the_page_follows_a_language_change(ui):
    page, _ = ui
    _open_example(page)
    page.evaluate("DXI18n.setLang('ko')")
    page.wait_for_function("() => document.querySelector(\"[data-group='examples'] .gc-group-title\").textContent === '예제'")
    assert page.inner_text("#gc-status") == "실행 준비 완료"
    assert page.get_attribute(".dxg-canvas", "aria-label").startswith("그래프 캔버스")
