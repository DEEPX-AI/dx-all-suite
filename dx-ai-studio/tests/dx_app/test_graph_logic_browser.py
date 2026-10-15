"""Graph Composer Phase 2 in a browser: logic blocks, the zone and line editor, events and Live.

/api/graph/* is answered in the page from the recorded dx_app Phase 2 fixtures (list_ops.json, examples/*.json,
events.jsonl), so neither an NPU nor a graph binary is needed; the server modules have their own tests
(test_graph_ops.py, test_graph_events.py, test_graph_frame.py, test_graph_live.py).
"""
from __future__ import annotations

import base64
import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "graph"
from dx_app.core.graph_ops import parse_list_ops  # noqa: E402

OPS = parse_list_ops((FIX / "list_ops.json").read_text(encoding="utf-8"))
EXAMPLES = []
for _p in sorted((FIX / "examples").glob("*.json")):
    _g = json.loads(_p.read_text(encoding="utf-8"))
    _ops = sorted({n["op"] for n in _g["nodes"] if n.get("type") == "logic"})
    EXAMPLES.append({"id": _p.stem, "name": _g["name"], "graph": _g,
                     "models": sorted({n["model"] for n in _g["nodes"] if n.get("model")}),
                     "nodes": len(_g["nodes"]), "edges": len(_g["edges"]), "logic": True, "ops": _ops,
                     "thumb": "/static/shared/favicons/dx_app.svg" if _p.stem == "zone_intrusion" else None})
CATALOG = json.loads((FIX / "catalog.json").read_text(encoding="utf-8"))
CATALOG.update(logic_ops=OPS, logic_error=None, examples=CATALOG["examples"] + EXAMPLES,
               limits={"uploads_total_b64": 20 * 1024 * 1024})
CATALOG["capabilities"].update(list_ops=True, events=True, loop=True)
EVENTS = [dict(json.loads(line), seq=i + 1) for i, line in
          enumerate(l for l in (FIX / "events.jsonl").read_text().splitlines() if l.strip())][:3]
for _e in EVENTS:
    _e.setdefault("track_id", None)


def _png(w=320, h=180):
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (40, 60, 80)).save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


class FakeApi:
    """In-page answers for /api/graph/*: catalog, --check, memory, frame, a run with events, Live."""

    def __init__(self, video_url=None):
        self.posted, self.live_polls, self.live_running, self.video_url = [], 0, False, video_url
        self.limit = CATALOG["limits"]["uploads_total_b64"]

    def handle(self, route):
        req = route.request
        url = req.url.split("?")[0]
        body = json.loads(req.post_data) if req.post_data else {}
        self.posted.append((url.rsplit("/api/graph/", 1)[1], body))
        if url.endswith("/api/graph/catalog"):
            out = dict(CATALOG, limits={"uploads_total_b64": self.limit})
        elif url.endswith("/api/graph/validate"):
            out = {"ok": True, "errors": [], "models": [], "missing": [], "unusable": {}, "notes": [],
                   "available": True, "engine_ignored": False}
        elif url.endswith("/api/graph/memory"):
            out = {"nodes": {}, "engines": [], "total_bytes": 0, "device": {}, "over_budget": False,
                   "unknown_models": [], "suggestions": []}
        elif url.endswith("/api/graph/frame"):
            out = {"image": _png(), "width": 1920, "height": 1080, "uri": "x"}
        elif url.endswith("/api/graph/run"):
            out = {"job_id": "job1", "status": "started"}
        elif url.endswith("/api/graph/run/poll"):
            out = {"running": False, "frames": 2, "fps": 8.1, "avg_fps": 8.1, "node_ms": {"od": 39.7}, "elapsed": 1.0,
                   "has_result": True, "events": EVENTS, "event_total": 3,
                   "event_counts": {"zone": {"enter": 2}, "alarm": {"intrusion": 1}}}
        elif url.endswith("/api/graph/run/result"):
            outputs = [{"url": self.video_url, "kind": "video", "name": "result.webm", "fps": 10.0}] if self.video_url else []
            out = {"ok": True, "exit_code": 0, "frames": 2, "error_frames": 0, "fps": 8.1, "avg_fps": 8.1, "elapsed": 1.0,
                   "node_ms": {"od": 39.7}, "errors": [], "log_tail": "", "outputs": outputs, "nodes": {},
                   "events": EVENTS, "event_total": 3, "event_counts": {"zone": {"enter": 2}, "alarm": {"intrusion": 1}},
                   "events_truncated": False, "events_url": "/outputs/graph/runs/job1/events.jsonl"}
        elif url.endswith("/api/graph/live/start"):
            self.live_running = True
            out = {"job_id": "L1", "status": "started", "frame_url": "/api/graph/live/frame?id=L1"}
        elif url.endswith("/api/graph/live/poll"):
            self.live_polls += 1
            after = int(req.url.split("events_after=")[1]) if "events_after=" in req.url else 0
            out = {"running": self.live_running, "frames": 10 * self.live_polls, "fps": 25.0, "avg_fps": 24.5,
                   "node_ms": {"od": 12.5, "zone": 0.2}, "elapsed": float(self.live_polls),
                   "events": [e for e in EVENTS if e["seq"] > after], "event_total": 3,
                   "event_counts": {"zone": {"enter": 2}, "alarm": {"intrusion": 1}}}
            if not self.live_running:
                out.update(exit_code=0, errors=[], stopped_by="user", events_url="/outputs/graph/live/L1/events.jsonl")
        elif url.endswith("/api/graph/live/stop"):
            self.live_running = False
            out = {"status": "stopping"}
        elif url.endswith("/api/graph/projects"):
            out = {"projects": []}
        else:
            out = {"error": "not found"}
        route.fulfill(status=200, content_type="application/json", body=json.dumps(out))


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


@pytest.fixture(scope="module")
def webm(tmp_path_factory):
    if not shutil.which("ffmpeg"):
        return None
    out = tmp_path_factory.mktemp("video") / "result.webm"
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=160x90:rate=10:duration=3",
                        "-c:v", "libvpx", str(out)], capture_output=True, timeout=60)
    return out.read_bytes() if r.returncode == 0 else None


def _serve_ranges(route, body, content_type):
    """Answer a media request with byte ranges, as a file server does: without them Chrome cannot seek the video."""
    first, last = 0, len(body) - 1
    spec = (route.request.headers.get("range") or "").partition("=")[2]
    if not spec:
        route.fulfill(status=200, content_type=content_type, body=body, headers={"Accept-Ranges": "bytes"})
        return
    a, _, b = spec.partition("-")
    first, last = int(a or 0), min(int(b) if b else last, last)
    route.fulfill(status=206, content_type=content_type, body=body[first:last + 1],
                  headers={"Accept-Ranges": "bytes", "Content-Range": f"bytes {first}-{last}/{len(body)}"})


def _page(browser, server, fake, webm=None):
    ctx = browser.new_context(viewport={"width": 1440, "height": 1000})
    ctx.add_init_script("try { localStorage.setItem('dx-tutorial-mode', 'off'); localStorage.setItem('dx-lang', 'en');"
                        " localStorage.removeItem('dx-graph-draft'); window.confirm = () => true; } catch (e) {}")
    ctx.route("**/api/graph/**", fake.handle)
    # Registered last, so it wins over the catch-all above: the Live view is one still frame.
    ctx.route("**/api/graph/live/frame*", lambda r: r.fulfill(status=200, content_type="image/png",
                                                              body=base64.b64decode(_png().split(",", 1)[1])))
    if webm:
        ctx.route("**/fake/result.webm", lambda r: _serve_ranges(r, webm, "video/webm"))
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"http://127.0.0.1:{server}/", wait_until="domcontentloaded")
    page.wait_for_function("() => typeof nav === 'function' && window.GraphComposer")
    page.evaluate("nav('graph')")
    page.wait_for_selector("[data-group='logic'] .gc-item", timeout=20000)
    return ctx, page, errors


@pytest.fixture
def ui(browser, server):
    fake = FakeApi()
    ctx, page, errors = _page(browser, server, fake)
    yield page, fake
    assert not errors, errors
    ctx.close()


def _fit(page):
    """Where the frame sits in the zone editor's drawing, in page pixels (x, y: the drawing's corner; ox, oy, w, h:
    the letterboxed frame), once the dialog's opening animation has ended: a scaled dialog reports a smaller
    rectangle."""
    js = """() => { const s = GraphZoneEditor.state(), r = document.querySelector('.gc-zone-canvas').getBoundingClientRect();
      return Object.assign(GraphZoneGeom.fit(s.frame.width, s.frame.height, r.width, r.height), {x: r.left, y: r.top}); }"""
    last = page.evaluate(js)
    for _ in range(40):
        page.wait_for_timeout(100)
        now = page.evaluate(js)
        if all(abs(now[k] - last[k]) < 0.5 for k in ("x", "y", "w", "h")):
            return now
        last = now
    return last


def _open(page, example_id):
    page.click(f".gc-template[data-id='{example_id}'] button")
    page.wait_for_function("() => GraphComposer.state().check && GraphComposer.state().check.ok", timeout=10000)


def _engine(page):
    return page.evaluate("GraphComposer.ctx().engine()")


def _node(page, nid):
    return [n for n in _engine(page)["nodes"] if n["id"] == nid][0]


def test_the_palette_offers_templates_with_thumbnails_and_the_logic_blocks(ui):
    page, _ = ui
    names = page.eval_on_selector_all("[data-group='logic'] .gc-item-name", "els => els.map(e => e.textContent)")
    assert names == ["Filter", "Zone", "Line crossing", "Count", "Dwell", "Condition → Event", "Gallery match", "User logic"]
    assert page.get_attribute(".gc-template[data-id='zone_intrusion'] img.gc-thumb", "alt") == "Result of zone-intrusion"
    assert page.locator(".gc-template").count() == 6
    groups = page.eval_on_selector_all("#gc-palette-list .gc-group:not(.is-empty)", "els => els.map(e => e.dataset.group)")
    assert groups[:3] == ["templates", "examples", "sources"] and groups[-2:] == ["logic", "cpu"]


def test_a_logic_block_joins_the_graph_with_its_defaults_and_connection_rules(ui):
    page, _ = ui
    _open(page, "line_counting")
    page.evaluate("GraphComposer.canvas().select({nodes: []})")
    page.click("[data-group='logic'] .gc-item:has-text('Zone') .gc-add")
    zone = _node(page, "zone")
    assert zone == {"id": "zone", "type": "logic", "op": "zone",
                    "params": {"polygon": [0.25, 0.25, 0.75, 0.25, 0.75, 0.75, 0.25, 0.75]}}
    r = page.evaluate("GraphComposer.canvas().connect('cam', 'zone')")
    assert r["ok"] is False and r["reason"] == "A logic block takes results, not frames"
    assert page.evaluate("GraphComposer.canvas().connect('person', 'zone').kind") == "result"
    assert {"from": "person", "to": "zone", "carry": "result"} in _engine(page)["edges"]
    assert page.evaluate("GraphComposer.canvas().connect('od', 'zone').reason") == "This logic block takes no more inputs"
    assert page.evaluate("GraphComposer.canvas().connect('line', 'zone').ok") is False, "records are not boxes"


def test_the_inspector_builds_the_form_from_list_ops_and_offers_tracking(ui):
    page, _ = ui
    _open(page, "line_counting")
    page.evaluate("""() => { const cv = GraphComposer.canvas(); const g = cv.getGraph();
      const od = g.nodes.find(n => n.id === 'od'); const d = JSON.parse(JSON.stringify(od.data)); delete d.track;
      cv.updateNode('od', {data: d}); cv.select({nodes: ['line']}); }""")
    body = page.inner_text("#gc-inspector-body")
    assert "counts tracked boxes crossing a line" in body, "the op's summary from --list-ops"
    assert "Takes boxes, obboxes, instances · hands on records" in body and "Fires: cross" in body
    assert "This block needs track ids" in body
    page.click("#gc-inspector-body button:has-text('Track objects on od')")
    assert _node(page, "od")["track"] == {"algo": "iou", "iou": 0.3, "max_age": 30}
    page.select_option("#gc-inspector-body .gc-fg[data-param='direction'] select", "in")
    assert _node(page, "line")["params"]["direction"] == "in"
    page.evaluate("GraphComposer.canvas().undo()")
    assert _node(page, "line")["params"]["direction"] == "both", "one undo step per edit"
    page.evaluate("GraphComposer.canvas().select({nodes: ['person']})")
    classes = page.locator("#gc-inspector-body .gc-fg[data-param='classes'] input")
    classes.fill("person, rider")
    classes.dispatch_event("change")
    assert _node(page, "person")["params"]["classes"] == ["person", "rider"]


def test_a_condition_suggests_the_values_its_input_writes(ui):
    page, _ = ui
    _open(page, "line_counting")
    page.evaluate("GraphComposer.canvas().select({nodes: []})")
    page.click("[data-group='logic'] .gc-item:has-text('Condition') .gc-add")
    page.evaluate("GraphComposer.canvas().connect('line', 'condition')")
    page.evaluate("GraphComposer.canvas().select({nodes: ['condition']})")
    opts = page.eval_on_selector_all("#gc-inspector-body datalist option", "els => els.map(e => e.value)")
    assert opts == ["count", "in", "out", "total"]
    assert page.get_attribute("#gc-inspector-body .gc-fg[data-param='value'] input", "placeholder") == "count"
    assert "Fires: condition" in page.inner_text("#gc-inspector-body"), "the event takes the node id by default"


def test_a_zone_is_edited_on_the_frame_with_mouse_keyboard_and_undo(ui):
    page, _ = ui
    _open(page, "zone_intrusion")
    page.evaluate("GraphComposer.canvas().select({nodes: ['zone']})")
    page.click("#gc-inspector-body .gc-zone-edit")
    page.wait_for_function("() => GraphZoneEditor.state() && GraphZoneEditor.state().img")
    assert page.evaluate("GraphZoneEditor.state().frame.width") == 1920
    f = _fit(page)
    # drag the first point (0.45, 0.35) to (0.40, 0.30)
    x0, y0 = f["x"] + f["ox"] + 0.45 * f["w"], f["y"] + f["oy"] + 0.35 * f["h"]
    page.mouse.move(x0, y0)
    page.mouse.down()
    page.mouse.move(x0 - f["w"] * 0.05, y0 - f["h"] * 0.05, steps=4)
    page.mouse.up()
    moved = _node(page, "zone")["params"]["polygon"][:2]
    assert abs(moved[0] - 0.40) < 0.01 and abs(moved[1] - 0.30) < 0.01, moved
    # keyboard: pick point 2, move it right, then delete point 1
    page.focus(".gc-zone-canvas")
    page.keyboard.press("]")
    page.keyboard.press("ArrowRight")
    page.wait_for_timeout(700)
    assert _node(page, "zone")["params"]["polygon"][2] == 1.0, "clamped at the frame's edge"
    assert "Point 2 of 4" in page.inner_text("#gc-zone-live")
    page.keyboard.press("Delete")
    assert len(_node(page, "zone")["params"]["polygon"]) == 6
    page.keyboard.press("Delete")
    assert len(_node(page, "zone")["params"]["polygon"]) == 6, "a zone keeps 3 points"
    page.keyboard.press("Control+z")
    assert len(_node(page, "zone")["params"]["polygon"]) == 8, "undo is the canvas history"
    page.wait_for_function("() => GraphZoneEditor.state().shapes[0].points.length === 4")
    page.click("#gc-zone-done")
    assert page.evaluate("GraphZoneEditor.isOpen()") is False


def test_another_zone_is_another_node_fed_by_the_same_input(ui):
    page, _ = ui
    _open(page, "zone_intrusion")
    page.evaluate("GraphComposer.canvas().select({nodes: ['zone']})")
    page.click("#gc-inspector-body .gc-zone-edit")
    page.wait_for_function("() => GraphZoneEditor.state() && GraphZoneEditor.state().img")
    page.click("#gc-zone-body button:has-text('Add zone')")
    zone2 = _node(page, "zone_2")
    assert zone2["params"]["polygon"] == [0.3, 0.3, 0.7, 0.3, 0.7, 0.7, 0.3, 0.7]
    assert {"from": "person", "to": "zone_2", "carry": "result"} in _engine(page)["edges"]
    assert page.eval_on_selector_all(".gc-zone-list button", "els => els.map(e => [e.textContent, e.getAttribute('aria-pressed')])") \
        == [["zone", "false"], ["zone_2", "true"]]
    page.focus(".gc-zone-canvas")
    page.keyboard.press("PageDown")
    assert page.evaluate("GraphZoneEditor.state().targets[GraphZoneEditor.state().cur].nodeId") == "zone"


def test_a_zone_is_redrawn_point_by_point_and_escape_keeps_the_old_one(ui):
    page, _ = ui
    _open(page, "zone_intrusion")
    page.evaluate("GraphComposer.canvas().select({nodes: ['zone']})")
    page.click("#gc-inspector-body .gc-zone-edit")
    page.wait_for_function("() => GraphZoneEditor.state() && GraphZoneEditor.state().img")
    before = _node(page, "zone")["params"]["polygon"]
    page.click("#gc-zone-body button:has-text('Redraw zone')")
    f = _fit(page)
    page.mouse.click(f["x"] + f["ox"] + 0.1 * f["w"], f["y"] + f["oy"] + 0.1 * f["h"])
    page.keyboard.press("Escape")
    assert _node(page, "zone")["params"]["polygon"] == before and page.evaluate("GraphZoneEditor.isOpen()")
    page.click("#gc-zone-body button:has-text('Redraw zone')")
    for nx, ny in ((0.6, 0.1), (0.9, 0.1), (0.9, 0.3)):
        page.mouse.click(f["x"] + f["ox"] + nx * f["w"], f["y"] + f["oy"] + ny * f["h"])
    page.keyboard.press("Enter")
    assert [round(v, 2) for v in _node(page, "zone")["params"]["polygon"]] == [0.6, 0.1, 0.9, 0.1, 0.9, 0.3]


def test_two_zones_of_one_input_are_drawn_together(ui):
    page, _ = ui
    _open(page, "zone_people_count")
    page.evaluate("GraphComposer.canvas().select({nodes: ['right']})")
    page.click("#gc-inspector-body .gc-zone-edit")
    page.wait_for_function("() => GraphZoneEditor.state() && GraphZoneEditor.state().img")
    st = page.evaluate("({ids: GraphZoneEditor.state().targets.map(t => t.nodeId), cur: GraphZoneEditor.state().cur})")
    assert st == {"ids": ["left", "right"], "cur": 1}
    f = _fit(page)
    page.mouse.click(f["x"] + f["ox"] + 0.2 * f["w"], f["y"] + f["oy"] + 0.7 * f["h"])
    assert page.evaluate("GraphZoneEditor.state().cur") == 0, "a click inside the other zone edits it"


def test_a_line_is_flipped_and_typed_in_numbers(ui):
    page, _ = ui
    _open(page, "line_counting")
    page.evaluate("GraphComposer.canvas().select({nodes: ['line']})")
    page.click("#gc-inspector-body .gc-zone-edit")
    page.wait_for_function("() => GraphZoneEditor.state() && GraphZoneEditor.state().img")
    page.click("#gc-zone-body button:has-text('Flip direction')")
    assert _node(page, "line")["params"]["line"] == [0.3, 0.0, 0.3, 1.0]
    x = page.locator("#gc-zone-body input[aria-label='Point 1 x']")
    x.fill("0.25")
    x.dispatch_event("change")
    assert _node(page, "line")["params"]["line"][0] == 0.25
    page.keyboard.press("Escape")
    assert page.evaluate("GraphZoneEditor.isOpen()") is False


def test_run_events_are_listed_filtered_badged_and_downloadable(browser, server, webm):
    fake = FakeApi(video_url="/fake/result.webm" if webm else None)
    ctx, page, errors = _page(browser, server, fake, webm)
    try:
        _open(page, "zone_intrusion")
        page.click("#gc-run")
        page.wait_for_selector("#gc-run-events .gc-ev-table tbody tr")
        assert page.locator("#gc-run-events tbody tr").count() == 3
        assert page.get_attribute("#gc-run-events .gc-ev-download", "href") == "/outputs/graph/runs/job1/events.jsonl"
        page.select_option("#gc-run-ev-node", "zone")
        assert page.locator("#gc-run-events tbody tr").count() == 2
        page.fill("#gc-run-ev-track", "3")
        assert page.locator("#gc-run-events tbody tr").count() == 1
        assert "1 of 3 events" in page.inner_text("#gc-run-events .gc-ev-summary")
        pins = page.evaluate("GraphDoc.pins(null, null, GraphComposer.state().run, k => k).badges")
        assert pins["zone"] == [{"kind": "events", "text": "Events: 2"}]
        if webm:
            page.wait_for_function("() => document.querySelector('.gc-run-media').readyState >= 1", timeout=10000)
            page.click("#gc-run-events tbody tr button")
            # frame 1 of the stream at the video's 10 fps, in the middle of the frame
            page.wait_for_function("() => Math.abs(document.querySelector('.gc-run-media').currentTime - 0.15) < 0.02")
        assert page.evaluate("GraphComposer.canvas().selection().nodes") == ["zone"]
        assert not errors, errors
    finally:
        ctx.close()


def test_live_starts_streams_lists_events_and_stops(ui):
    page, fake = ui
    _open(page, "zone_intrusion")
    page.click("#gc-live")
    assert page.get_attribute("#gc-tab-live", "aria-selected") == "true" and page.is_visible("#gc-live-body")
    page.wait_for_function("() => document.getElementById('gc-live-view').src.includes('/api/graph/live/frame?id=L1')")
    page.wait_for_selector("#gc-live-events tbody tr")
    assert "25.0 FPS" in page.inner_text("#gc-live-body .gc-run-progress")
    assert not page.is_enabled("#gc-run") and not page.is_enabled("#gc-live")
    started = [b for path, b in fake.posted if path == "live/start"][0]
    assert started["inputs"] == {} and [n.get("type") for n in started["graph"]["nodes"]].count("logic") == 3
    page.click("#gc-live-stop")
    page.wait_for_selector("#gc-live-body .gc-ok")
    assert page.inner_text("#gc-live-body .gc-ok") == "Live stopped."
    assert page.is_hidden("#gc-live-view") and page.is_enabled("#gc-live")
    assert page.get_attribute("#gc-live-events .gc-ev-download", "href") == "/outputs/graph/live/L1/events.jsonl"


def test_live_takes_a_camera_or_an_rtsp_address_and_stops_when_the_page_is_left(ui):
    page, fake = ui
    _open(page, "zone_intrusion")
    page.click("#gc-tab-live")
    page.select_option("#gc-live-input-cam", "__rtsp__")
    page.fill("#gc-live-rtsp-cam", "rtsp://10.0.0.2/stream1")
    page.dispatch_event("#gc-live-rtsp-cam", "change")
    page.click("#gc-live-start")
    page.wait_for_function("() => GraphLive.running()")
    started = [b for path, b in fake.posted if path == "live/start"][-1]
    assert started["inputs"] == {"cam": "rtsp://10.0.0.2/stream1"}
    page.evaluate("nav('models')")
    for _ in range(50):
        if any(path == "live/stop" for path, _ in fake.posted):
            break
        page.wait_for_timeout(100)
    assert any(path == "live/stop" for path, _ in fake.posted), "leaving the page stops Live"


def test_the_tabs_follow_the_arrow_keys(ui):
    page, _ = ui
    page.focus("#gc-tab-once")
    page.keyboard.press("ArrowRight")
    assert page.evaluate("document.activeElement.id") == "gc-tab-live" and page.is_visible("#gc-live-body")
    page.keyboard.press("Home")
    assert page.is_visible("#gc-run-body") and page.is_hidden("#gc-live-body")


def test_the_logic_pieces_follow_a_language_change(ui):
    page, _ = ui
    _open(page, "zone_intrusion")
    page.evaluate("GraphComposer.canvas().select({nodes: ['zone']})")
    page.evaluate("DXI18n.setLang('ko')")
    page.wait_for_function("() => document.querySelector(\"[data-group='templates'] .gc-group-title\").textContent === 'Template'")
    names = page.eval_on_selector_all("[data-group='logic'] .gc-item-name", "els => els.map(e => e.textContent)")
    assert names[:3] == ["필터", "구역", "선 통과"]
    assert "프레임 위에서 편집" in page.inner_text("#gc-inspector-body") and "점 4개" in page.inner_text("#gc-inspector-body")
    assert page.inner_text("#gc-tab-live") .strip() == "Live"
    # dx_app's op texts are English only; Studio's translations stand in for them, field labels included.
    body = page.inner_text("#gc-inspector-body")
    assert "기준점이 다각형 안" in body and "keeps the boxes" not in body, body
    assert page.inner_text("#gc-inspector-body .gc-fg[data-param='mode'] label") == "방식"
    assert "통과시킬 박스" in page.inner_text("#gc-inspector-body .gc-fg[data-param='mode']")
    assert page.inner_text("#gc-inspector-body .gc-drawn[data-param='polygon'] .gc-drawn-label").startswith("다각형")
    # A text this Studio has no translation for (dx_app reworded it, or a new op) shows dx_app's own words.
    page.evaluate("""() => { GraphComposer.state().ops.zone.summary = 'keeps boxes in a polygon (reworded)';
      const cv = GraphComposer.canvas(); cv.select({nodes: ['od']}); cv.select({nodes: ['zone']}); }""")
    assert "keeps boxes in a polygon (reworded)" in page.inner_text("#gc-inspector-body")
    page.evaluate("DXI18n.setLang('en')")
    assert page.text_content("#gc-inspector-body .gc-fg[data-param='mode'] label") == "Mode", "text_content: CSS draws labels in capitals"

class FakeGallery:
    """/api/graph/gallery/{build,poll,stop}: a build that runs for `polls` polls, then ends as `result`; `hold` keeps it
    running until it is stopped (then it ends as gallery_stopped, as graph_gallery.stop does)."""

    def __init__(self, result=None, polls=1, hold=False):
        self.posted, self.polled, self.stopped = [], 0, False
        self.result, self.polls, self.hold = result, polls, hold

    def handle(self, route):
        req = route.request
        url = req.url.split("?")[0]
        if url.endswith("/build"):
            self.posted.append(json.loads(req.post_data))
            out = {"job_id": "G1", "status": "started", "images": 12}
        elif url.endswith("/stop"):
            self.stopped = json.loads(req.post_data)
            out = {"status": "stopping"}
        else:
            self.polled += 1
            if self.stopped:
                out = {"job_id": "G1", "state": "failed", "elapsed": 2.0, "error_key": "gallery_stopped",
                       "error": "the gallery build was stopped", "log_tail": ""}
            elif self.hold or self.polled <= self.polls:
                out = {"job_id": "G1", "state": "running", "elapsed": float(self.polled), "images": 12}
            else:
                out = dict(self.result, job_id="G1", elapsed=3.0)
        route.fulfill(status=200, content_type="application/json", body=json.dumps(out))


GALLERY_DONE = {"state": "done", "path": "outputs/dx_app/graph/galleries/staff.bin",
                "gallery": "/srv/studio/outputs/dx_app/graph/galleries/staff.bin",
                "url": "/outputs/graph/galleries/staff.bin", "name": "staff", "model": "repvgg-a0-reid_256x128",
                "images": 12, "people": 3, "names": ["ann", "bob", "cy"], "dim": 512, "log_tail": ""}
_GB = "#gc-inspector-body .gc-gallery-build"


def _gallery_page(page, fake):
    page.context.route("**/api/graph/gallery/**", fake.handle)
    _open(page, "gallery_known_person")
    page.evaluate("GraphComposer.canvas().select({nodes: ['known']})")


def test_a_gallery_block_builds_its_gallery_from_an_image_folder(ui):
    page, _ = ui
    fake = FakeGallery(result=GALLERY_DONE)
    _gallery_page(page, fake)
    model = page.locator(f"{_GB} .gc-fg:has(label:text-is('Embedding model')) input")
    assert model.input_value() == "repvgg-a0-reid_256x128", "the model feeding the block"
    page.fill(f"{_GB} .gc-fg:has(label:text-is('Image folder')) input", "sample/people")
    page.fill(f"{_GB} .gc-fg:has(label:text-is('Gallery name (optional)')) input", "staff")
    page.click(f"{_GB} button:has-text('Build gallery')")
    page.wait_for_selector(f"{_GB} .gc-gallery-status:has-text('Gallery built: 3 people, 12 images')", timeout=10000)
    assert fake.posted == [{"folder": "sample/people", "model": "repvgg-a0-reid_256x128", "name": "staff"}]
    assert _node(page, "known")["params"]["gallery"] == GALLERY_DONE["gallery"]
    assert page.evaluate("GraphComposer.state().dirty") is True
    page.evaluate("GraphComposer.canvas().undo()")
    assert _node(page, "known")["params"]["gallery"] == "sample/gallery/reid_repvgg-a0-reid_256x128.bin", "one undo step"


def test_a_gallery_build_shows_its_time_can_be_stopped_and_says_why_it_ended(ui):
    page, _ = ui
    fake = FakeGallery(hold=True)
    _gallery_page(page, fake)
    page.fill(f"{_GB} .gc-fg:has(label:text-is('Image folder')) input", "sample/people")
    page.click(f"{_GB} button:has-text('Build gallery')")
    page.wait_for_selector(f"{_GB} .gc-gallery-status:has-text('Building the gallery…') .spin", timeout=10000)
    page.wait_for_selector(f"{_GB} .gc-gallery-status:has-text(' s')", timeout=10000)
    assert page.is_disabled(f"{_GB} button:has-text('Build gallery')")
    assert fake.posted == [{"folder": "sample/people", "model": "repvgg-a0-reid_256x128"}], "no name: none sent"
    page.click(f"{_GB} button:has-text('Stop')")
    page.wait_for_selector(f"{_GB} .gc-gallery-status.gc-error:has-text('the gallery build was stopped')", timeout=10000)
    assert fake.stopped == {"id": "G1"}
    assert page.locator(f"{_GB} button:has-text('Stop')").count() == 0
    assert not page.is_disabled(f"{_GB} button:has-text('Build gallery')")
    assert _node(page, "known")["params"]["gallery"] == "sample/gallery/reid_repvgg-a0-reid_256x128.bin"
    # In Korean the error key is translated and the server's English message follows it.
    page.evaluate("DXI18n.setLang('ko')")
    page.evaluate("GraphComposer.canvas().select({nodes: ['known']})")
    status = page.inner_text(f"{_GB} .gc-gallery-status")
    assert status.startswith("Gallery") and "the gallery build was stopped" in status, status


def test_a_frame_too_large_to_show_says_why_and_the_shapes_stay_editable(ui):
    page, _ = ui
    page.context.route("**/api/graph/frame*", lambda r: r.fulfill(status=413, content_type="application/json", body=json.dumps(
        {"error": "the file is 900 MB; a video up to 512 MB is shown", "error_key": "frame_too_large"})))
    _open(page, "zone_intrusion")
    page.evaluate("GraphComposer.canvas().select({nodes: ['zone']})")
    page.click("#gc-inspector-body .gc-zone-edit")
    page.wait_for_selector("#gc-zone-body :text('the file is 900 MB; a video up to 512 MB is shown')", timeout=10000)
    assert "shapes are drawn on an empty 16:9 frame" in page.inner_text("#gc-zone-body")
    assert page.evaluate("GraphZoneEditor.state().shapes[0].points.length") == 4


def test_the_event_list_names_several_tracks_seeks_each_streams_video_and_says_when_partial(ui):
    page, _ = ui
    r = page.evaluate("""() => {
      const host = document.createElement('div'); document.body.appendChild(host);
      const vid = () => ({ currentTime: -1, pause() {}, focus() {} });
      const a = vid(), b = vid(), picked = [];
      const ev = GraphEvents.create(host, GraphComposer.ctx(), { idPrefix: 'gc-t-ev', onSelectNode: id => picked.push(id) });
      ev.set([
        {seq: 1, frame: 4, time: 0.16, stream: 'cam_a', node: 'alarm', event: 'intrusion', track_id: -1, data: {track_ids: '3,7'}},
        {seq: 2, frame: 4, time: 0.16, stream: 'cam_b', node: 'zone', event: 'enter', track_id: 7, data: {count: 1}},
        {seq: 3, frame: 5, time: 0.2, stream: 'cam_c', node: 'zone', event: 'enter', track_id: -1, data: {}}],
        {total: 9, partial: true, videos: [{video: a, fps: 10, stream: 'cam_a'}, {video: b, fps: 20, stream: 'cam_b'}]});
      const rows = [...host.querySelectorAll('tbody tr')].map(tr => [...tr.cells].map(td => td.textContent));
      const go = host.querySelectorAll('tbody tr button');
      go[0].click(); go[1].click(); go[2].click();
      const summary = host.querySelector('.gc-ev-summary').textContent;
      const track = host.querySelector('#gc-t-ev-track'), counts = {};
      for (const t of ['3', '7']) { track.value = t; track.dispatchEvent(new Event('input'));
                                    counts[t] = host.querySelectorAll('tbody tr').length; }
      host.remove();
      return {rows, a: a.currentTime, b: b.currentTime, picked, summary, counts};
    }""")
    assert [row[4] for row in r["rows"]] == ["3,7", "7", "-"], "track_id -1 with track_ids: several tracks"
    assert r["a"] == 0.45 and r["b"] == 0.225, "frames count per stream: each stream's own video and fps"
    assert r["picked"] == ["alarm", "zone", "zone"], "an event of a stream without a video still selects its node"
    assert r["counts"] == {"3": 1, "7": 2}, "the track filter reads track_ids too"
    assert "3 of 9 events" in r["summary"]
    assert "Only the end of the log was read: the total and the counts are partial." in r["summary"]


def test_a_refused_run_says_why_in_the_page_language(ui):
    page, _ = ui
    page.context.route("**/api/graph/run", lambda r: r.fulfill(status=409, content_type="application/json", body=json.dumps(
        {"error": "a graph run is already running", "error_key": "graph_run_busy"})))
    _open(page, "zone_intrusion")
    page.evaluate("DXI18n.setLang('ko')")
    page.click("#gc-run")
    page.wait_for_function("() => /그래프 실행이 진행 중입니다/.test(document.querySelector('#gc-run-panel').textContent)", timeout=10000)


def test_live_says_why_it_could_not_start_or_why_it_ended(ui):
    page, _ = ui
    refuse = lambda r: r.fulfill(status=409, content_type="application/json", body=json.dumps(
        {"error": "another job took the NPU while this one was being prepared; start it again", "error_key": "npu_hold_lost"}))
    page.context.route("**/api/graph/live/start", refuse)
    _open(page, "zone_intrusion")
    page.evaluate("DXI18n.setLang('ko')")
    page.click("#gc-tab-live")
    page.click("#gc-live-start")
    page.wait_for_function("() => /다른 작업이 NPU를 사용하기 시작했습니다/.test(document.querySelector('#gc-live-body').textContent)",
                           timeout=10000)
    page.evaluate("DXI18n.setLang('en')")
    page.context.unroute("**/api/graph/live/start", refuse)
    page.context.route("**/api/graph/live/poll*", lambda r: r.fulfill(status=404, content_type="application/json", body=json.dumps(
        {"error": "unknown_job", "error_key": "unknown_job"})))
    page.click("#gc-live-start")
    page.wait_for_selector("#gc-live-body .gc-error:has-text('This run is no longer known to the server')", timeout=10000)
    assert not page.evaluate("GraphLive.running()") and page.is_enabled("#gc-live-start")


def test_the_drawing_dialog_keeps_the_input_path_case_and_live_shows_time_bars(ui):
    page, _ = ui
    _open(page, "zone_intrusion")
    page.evaluate("GraphComposer.canvas().select({nodes: ['zone']})")
    page.click("#gc-inspector-body .gc-zone-edit")
    page.wait_for_function("() => GraphZoneEditor.state() && GraphZoneEditor.state().img")
    uri = page.locator("#gc-zone-title-text .gc-zone-uri")
    assert uri.inner_text() == "sample/img/sample_people.jpg", "the h2 is upper case; the path is not"
    page.keyboard.press("Escape")
    page.click("#gc-live")
    page.wait_for_selector("#gc-live-body .gc-ms .gc-ms-fill")
    widths = page.eval_on_selector_all("#gc-live-body .gc-ms-fill", "els => els.map(e => e.style.width)")
    assert widths == ["98%", "2%"], "per-node time drawn as in Run once"
    page.click("#gc-live-stop")
    page.wait_for_selector("#gc-live-body .gc-ok")


@pytest.mark.parametrize("width,height,least", [(1440, 900, 0.8), (1024, 768, 0.7)])
def test_a_long_template_opens_wrapped_into_rows_at_a_readable_zoom(browser, server, width, height, least):
    """zone_intrusion is a chain of five (cam -> od -> person -> zone -> alarm): in one row it is wider than the canvas
    and opens at about half size; the layout wraps it into rows that fit the canvas's shape instead."""
    fake = FakeApi()
    ctx, page, errors = _page(browser, server, fake)
    try:
        page.set_viewport_size({"width": width, "height": height})
        page.wait_for_timeout(300)
        _open(page, "zone_intrusion")
        got = page.evaluate("""() => { const cv = GraphComposer.canvas(), g = cv.getGraph();
          const rows = {}; g.nodes.forEach(n => { rows[n.y] = (rows[n.y] || 0) + 1; });
          const host = cv.element.getBoundingClientRect();
          return {zoom: cv.view().zoom, rows: Object.keys(rows).length, w: host.width, h: host.height,
                  order: g.nodes.slice().sort((a, b) => (a.y - b.y) || (a.x - b.x)).map(n => n.id)}; }""")
        assert got["zoom"] >= least, got
        assert got["rows"] >= 2, got
        assert got["order"] == ["cam", "od", "person", "zone", "alarm"], "rows read left to right, top to bottom"
        # A project with stored positions opens as it was saved: only a graph without them is laid out.
        flat = page.evaluate("""() => { const g = GraphComposer.canvas().getGraph();
          g.nodes.forEach((n, i) => { n.x = 40 + i * 280; n.y = 40; });
          return JSON.stringify(GraphDoc.makeProject(g, {name: 'flat'}, null)); }""")
        page.set_input_files("#gc-import-file", files=[{"name": "flat.json", "mimeType": "application/json",
                                                         "buffer": flat.encode()}])
        page.wait_for_function("() => GraphComposer.state().name === 'flat'")
        kept = page.evaluate("GraphComposer.canvas().getGraph().nodes.map(n => [n.x, n.y])")
        assert kept == [[40 + i * 280, 40] for i in range(5)], kept
    finally:
        ctx.close()
    assert not errors, errors
