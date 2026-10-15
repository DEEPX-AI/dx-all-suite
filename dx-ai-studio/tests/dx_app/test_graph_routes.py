"""/api/graph/* routes: Lab-session and same-origin guards on every route, then each route reaches its module."""
from __future__ import annotations

import pytest

from dx_app.core import config, graph_catalog, graph_export, graph_memory, graph_routes, graph_run, graph_validate
from dx_app.core.developer import lab_session

GET_ROUTES = ("/api/graph/catalog", "/api/graph/run/poll", "/api/graph/run/result", "/api/graph/projects",
              "/api/graph/project", "/api/graph/project/versions", "/api/graph/frame", "/api/graph/live/poll",
              "/api/graph/gallery/poll")
POST_ROUTES = ("/api/graph/validate", "/api/graph/memory", "/api/graph/run", "/api/graph/run/stop",
               "/api/graph/project/save", "/api/graph/project/delete", "/api/graph/live/start",
               "/api/graph/live/stop", "/api/graph/gallery/build", "/api/graph/gallery/stop", "/api/graph/run/frame",
               "/api/graph/export/plan", "/api/graph/export")
LOCAL = {"Origin": "http://localhost:8080"}
GRAPH = {"version": 1, "name": "g", "nodes": [{"id": "cam", "type": "source", "uri": "x.jpg"}], "edges": []}


def _route(method, path, payload=None, headers=None, query=None):
    """Drive dx_app's real Handler.route() without a socket (as tests/dx_app/test_server.py does)."""
    from dx_app import server

    captured = {}
    q = dict(query or {})
    handler = object.__new__(server.Handler)
    handler.command = method
    handler.url_path = path
    handler.query = {k: [v] for k, v in q.items()}
    handler.headers = headers or {}
    handler.handle_chat_routes = lambda _engine: False
    handler.read_json_body = lambda: payload if payload is not None else {}
    handler.send_json = lambda data, code=200: captured.update({"data": data, "code": code})
    handler.send_error = lambda code, *args, **kwargs: captured.update({"code": code})
    handler.route()
    return captured


def _token():
    return lab_session()["token"]


@pytest.mark.parametrize("method, path", [("GET", p) for p in GET_ROUTES] + [("POST", p) for p in POST_ROUTES])
def test_every_graph_route_needs_a_lab_session(method, path):
    r = _route(method, path, headers=dict(LOCAL))
    assert (r["code"], r["data"]["error"]) == (403, "Lab session required")


@pytest.mark.parametrize("method, path", [("GET", p) for p in GET_ROUTES] + [("POST", p) for p in POST_ROUTES])
def test_every_graph_route_refuses_another_origin_even_with_a_token(method, path):
    r = _route(method, path, headers={"X-Lab-Token": _token(), "Origin": "https://evil.example.com"})
    assert (r["code"], r["data"]["error"]) == (403, "Cross-origin access denied")


def test_catalog_with_a_session(monkeypatch):
    seen = {}

    def fake_catalog(refresh=False):
        seen["refresh"] = refresh
        return {"models": []}

    monkeypatch.setattr(graph_catalog, "catalog", fake_catalog)
    r = _route("GET", "/api/graph/catalog", headers={"X-Lab-Token": _token(), **LOCAL}, query={"refresh": "1"})
    assert r["code"] == 200 and seen == {"refresh": True}


def test_validate_and_memory_take_a_graph(monkeypatch):
    monkeypatch.setattr(graph_validate, "validate", lambda g: {"ok": True, "n": len(g["nodes"])})
    monkeypatch.setattr(graph_memory, "estimate", lambda g: {"total_bytes": 1})
    h = {"X-Lab-Token": _token(), **LOCAL}
    assert _route("POST", "/api/graph/validate", {"graph": GRAPH}, h)["data"] == {"ok": True, "n": 1}
    assert _route("POST", "/api/graph/memory", {"graph": GRAPH}, h)["data"] == {"total_bytes": 1}
    bad = _route("POST", "/api/graph/validate", {"graph": "x"}, h)
    assert (bad["code"], bad["data"]["error_key"]) == (400, "invalid_payload")
    big = {"nodes": [{"id": f"n{i}"} for i in range(graph_routes.MAX_NODES + 1)], "edges": []}
    assert _route("POST", "/api/graph/memory", {"graph": big}, h)["code"] == 400


def test_run_passes_its_options(monkeypatch):
    seen = {}

    def fake_start(g, **kw):
        seen.update(kw)
        return {"job_id": "j1", "status": "started"}, 200

    monkeypatch.setattr(graph_run, "start", fake_start)
    r = _route("POST", "/api/graph/run", {"graph": GRAPH, "variant": "async", "inputs": {"cam": "a.jpg"},
                                          "max_inflight": 4, "frames": 3}, {"X-Lab-Token": _token(), **LOCAL})
    assert r["data"] == {"job_id": "j1", "status": "started"}
    assert seen == {"variant": "async", "inputs": {"cam": "a.jpg"}, "uploads": None, "max_inflight": 4, "frames": 3}


def test_projects_round_trip_through_the_routes(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "OUTPUTS_DIR", tmp_path)
    h = {"X-Lab-Token": _token(), **LOCAL}
    project = {"schema": 1, "graph": GRAPH, "layout": {}, "meta": {"name": "My graph"}}
    saved = _route("POST", "/api/graph/project/save", {"project": project}, h)
    assert saved["code"] == 200 and saved["data"]["id"] == "my-graph"
    assert _route("GET", "/api/graph/projects", headers=h)["data"]["projects"][0]["id"] == "my-graph"
    loaded = _route("GET", "/api/graph/project", headers=h, query={"id": "my-graph"})
    assert loaded["data"]["project"]["graph"] == GRAPH
    assert _route("GET", "/api/graph/project", headers=h, query={"id": "../etc"})["code"] == 400
    assert _route("POST", "/api/graph/project/delete", {"id": "my-graph"}, h)["code"] == 200


def test_unknown_graph_paths_are_not_found():
    h = {"X-Lab-Token": _token(), **LOCAL}
    assert _route("GET", "/api/graph/nope", headers=h)["code"] == 404
    assert _route("POST", "/api/graph/nope", {}, h)["code"] == 404


# The shared server caps JSON bodies at 1 MB; /api/graph/run carries uploaded images, so it alone may be larger.
def _read_body(path, length, body=b""):
    import io

    from dx_app import server

    h = object.__new__(server.Handler)
    h.url_path = path
    h.headers = {"Content-Length": str(length)}
    h.rfile = io.BytesIO(body)
    return h.read_json_body()


def test_a_run_may_carry_a_five_megabyte_image():
    import base64
    import json

    png = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\0" * (5 * 1024 * 1024 * 3 // 4)).decode()
    body = json.dumps({"graph": GRAPH, "uploads": {"cam": "data:image/png;base64," + png}}).encode()
    assert len(body) > 5 * 1024 * 1024
    assert _read_body("/api/graph/run", len(body), body)["uploads"]["cam"].startswith("data:image/png")


def test_a_25_megabyte_run_and_a_large_body_elsewhere_are_refused_with_the_limit():
    from shared.dx_server import RequestBodyError

    with pytest.raises(RequestBodyError) as e:
        _read_body("/api/graph/run", 25 * 1024 * 1024)
    assert e.value.status_code == 413 and "24 MB" in e.value.message
    with pytest.raises(RequestBodyError) as e:
        _read_body("/api/graph/validate", 5 * 1024 * 1024)
    assert e.value.status_code == 413 and "1 MB" in e.value.message


def test_a_corrupt_or_unwritable_project_is_a_clear_error(tmp_path, monkeypatch):
    from dx_app.core import graph_projects

    monkeypatch.setattr(config, "OUTPUTS_DIR", tmp_path)
    h = {"X-Lab-Token": _token(), **LOCAL}
    graph_projects.save({"schema": 1, "graph": GRAPH, "meta": {"name": "p"}}, "p")
    (graph_projects.projects_dir() / "p" / "project.json").write_text("{not json")
    r = _route("GET", "/api/graph/project", headers=h, query={"id": "p"})
    assert (r["code"], r["data"]["error_key"]) == (422, "project_corrupt")

    def full(*_a, **_k):
        raise OSError(28, "No space left on device")
    monkeypatch.setattr(graph_projects, "save", full)
    r = _route("POST", "/api/graph/project/save", {"project": {"schema": 1, "graph": GRAPH}}, h)
    assert (r["code"], r["data"]["error_key"]) == (500, "project_io_error") and "No space" in r["data"]["error"]


# Phase 2: events on the run poll, the frame for zone drawing, Live.

def test_the_run_poll_passes_the_event_cursor(monkeypatch):
    seen = {}
    monkeypatch.setattr(graph_run, "poll", lambda jid, after="0": seen.update(id=jid, after=after) or {"running": True})
    r = _route("GET", "/api/graph/run/poll", headers={"X-Lab-Token": _token(), **LOCAL},
               query={"id": "j1", "events_after": "7"})
    assert r["code"] == 200 and seen == {"id": "j1", "after": "7"}


def test_the_frame_route_answers_with_the_frame_or_why_not(monkeypatch):
    from dx_app.core import graph_frame
    monkeypatch.setattr(graph_frame, "first_frame", lambda uri: ({"error_key": "live_source"}, 409) if uri.startswith(
        "camera:") else ({"image": "data:image/jpeg;base64,AA==", "width": 4, "height": 2, "uri": uri}, 200))
    h = {"X-Lab-Token": _token(), **LOCAL}
    ok = _route("GET", "/api/graph/frame", headers=h, query={"uri": "sample/img/a.jpg"})
    assert ok["code"] == 200 and ok["data"]["width"] == 4
    assert _route("GET", "/api/graph/frame", headers=h, query={"uri": "camera:0"})["code"] == 409


def test_live_start_poll_and_stop_reach_graph_live(monkeypatch):
    from dx_app.core import graph_live
    seen = {}
    monkeypatch.setattr(graph_live, "start", lambda g, **kw: seen.update(start=kw) or ({"job_id": "L1"}, 200))
    monkeypatch.setattr(graph_live, "poll", lambda jid, after="0": seen.update(poll=(jid, after)) or {"running": True})
    monkeypatch.setattr(graph_live, "stop", lambda jid: seen.update(stop=jid) or {"status": "stopping"})
    h = {"X-Lab-Token": _token(), **LOCAL}
    r = _route("POST", "/api/graph/live/start", {"graph": GRAPH, "variant": "async",
                                                 "inputs": {"cam": "camera:0"}, "max_inflight": 2}, h)
    assert r["data"] == {"job_id": "L1"} and seen["start"] == {"variant": "async", "inputs": {"cam": "camera:0"},
                                                               "max_inflight": 2, "draw": None}
    _route("POST", "/api/graph/live/start", {"graph": GRAPH, "draw": ["od", "zone"]}, h)
    assert seen["start"]["draw"] == ["od", "zone"]
    assert _route("GET", "/api/graph/live/poll", headers=h, query={"id": "L1", "events_after": "3"})["code"] == 200
    assert seen["poll"] == ("L1", "3")
    assert _route("POST", "/api/graph/live/stop", {"id": "L1"}, h)["data"] == {"status": "stopping"}
    assert _route("POST", "/api/graph/live/start", {"graph": "x"}, h)["code"] == 400


def _stream(query, headers, monkeypatch, frames):
    """GET /api/graph/live/frame through Handler.route() with a byte buffer as the socket."""
    import io

    from dx_app import server
    from dx_app.core import graph_live

    answers = iter(frames)
    state = {"left": len(frames)}

    def ok(jid):
        return jid == "L1" and state["left"] > 0

    def frame(jid):
        state["left"] -= 1
        return next(answers)
    monkeypatch.setattr(graph_live, "frame_ok", ok)
    monkeypatch.setattr(graph_live, "frame", frame)
    monkeypatch.setattr(server.time, "sleep", lambda _s: None)
    captured = {"headers": {}}
    h = object.__new__(server.Handler)
    h.command, h.url_path, h.headers = "GET", "/api/graph/live/frame", headers
    h.query = {k: [v] for k, v in query.items()}
    h.handle_chat_routes = lambda _engine: False
    h.wfile = io.BytesIO()
    h.send_json = lambda data, code=200: captured.update(data=data, code=code)
    h.send_response = lambda code: captured.update(code=code)
    h.send_header = lambda k, v: captured["headers"].update({k: v})
    h.end_headers = lambda: None
    h.route()
    captured["body"] = h.wfile.getvalue()
    return captured


def test_the_live_frame_stream_needs_the_running_job_and_a_local_origin(monkeypatch):
    r = _stream({"id": "L1"}, dict(LOCAL), monkeypatch, [b"JPEG1", b"JPEG2"])
    assert r["code"] == 200 and r["headers"]["Content-Type"].startswith("multipart/x-mixed-replace")
    assert r["body"].count(b"--frame") == 2 and b"JPEG2" in r["body"]
    assert _stream({"id": "other"}, dict(LOCAL), monkeypatch, [b"x"])["code"] == 404
    bad = _stream({"id": "L1"}, {"Origin": "https://evil.example.com"}, monkeypatch, [b"x"])
    assert (bad["code"], bad["data"]["error"]) == (403, "Cross-origin access denied") and bad["body"] == b""


def test_gallery_build_poll_and_stop_reach_graph_gallery(monkeypatch):
    from dx_app.core import graph_gallery
    seen = {}
    monkeypatch.setattr(graph_gallery, "start", lambda folder, model, name=None: seen.update(args=(folder, model, name))
                        or ({"job_id": "G1", "status": "started", "images": 3}, 200))
    monkeypatch.setattr(graph_gallery, "poll", lambda jid: seen.update(poll=jid)
                        or ({"error": "unknown_job", "error_key": "unknown_job"}, 404))
    monkeypatch.setattr(graph_gallery, "stop", lambda jid: seen.update(stop=jid) or {"status": "stopping"})
    h = {"X-Lab-Token": _token(), **LOCAL}
    r = _route("POST", "/api/graph/gallery/build", {"folder": "sample/gallery/staff", "model": "osnet",
                                                    "name": "staff"}, h)
    assert (r["code"], r["data"]["job_id"]) == (200, "G1")
    assert seen["args"] == ("sample/gallery/staff", "osnet", "staff")
    _route("POST", "/api/graph/gallery/build", {"folder": "f", "model": "m"}, h)
    assert seen["args"] == ("f", "m", None)
    r = _route("GET", "/api/graph/gallery/poll", headers=h, query={"id": "G1"})
    assert (r["code"], r["data"]["error_key"], seen["poll"]) == (404, "unknown_job", "G1")
    r = _route("POST", "/api/graph/gallery/stop", {"id": "G1"}, h)
    assert (r["code"], r["data"], seen["stop"]) == (200, {"status": "stopping"}, "G1")


# Results view: the layers of one frame of a run's video.

def test_the_run_frame_route_reaches_graph_frame_inspect(monkeypatch):
    from dx_app.core import graph_frame
    seen = {}
    monkeypatch.setattr(graph_frame, "inspect", lambda data: seen.update(data) or ({"ok": True, "stream": "cam"}, 200))
    h = {"X-Lab-Token": _token(), **LOCAL}
    r = _route("POST", "/api/graph/run/frame", {"run_id": "a" * 32, "stream": "cam", "time_s": 1.5}, h)
    assert (r["code"], r["data"]) == (200, {"ok": True, "stream": "cam"})
    assert seen == {"run_id": "a" * 32, "stream": "cam", "time_s": 1.5}
    big = {"nodes": [{"id": f"n{i}"} for i in range(graph_routes.MAX_NODES + 1)], "edges": []}
    bad = _route("POST", "/api/graph/run/frame", {"graph": big, "stream": "cam", "time_s": 0}, h)
    assert (bad["code"], bad["data"]["error_key"]) == (400, "invalid_payload")


def test_export_plan_and_export_reach_graph_export(monkeypatch):
    seen = []
    monkeypatch.setattr(graph_export, "plan", lambda g, name=None, inputs=None: (
        seen.append(("plan", len(g["nodes"]), name, inputs)) or ({"ok": True, "dry_run": True}, 200)))
    monkeypatch.setattr(graph_export, "export", lambda g, name, include_models=False, inputs=None: (
        seen.append(("export", name, include_models, inputs)) or ({"ok": True, "zip_url": "/outputs/x.zip"}, 200)))
    h = {"X-Lab-Token": _token(), **LOCAL}
    r = _route("POST", "/api/graph/export/plan", {"graph": GRAPH, "inputs": {"cam": "a.jpg"}}, h)
    assert (r["code"], r["data"]) == (200, {"ok": True, "dry_run": True})
    r = _route("POST", "/api/graph/export", {"graph": GRAPH, "name": "g1", "include_models": True}, h)
    assert (r["code"], r["data"]["zip_url"]) == (200, "/outputs/x.zip")
    _route("POST", "/api/graph/export", {"graph": GRAPH, "name": "g2"}, h)       # no field: the models stay out
    assert seen == [("plan", 1, None, {"cam": "a.jpg"}), ("export", "g1", True, None), ("export", "g2", False, None)]
    bad = _route("POST", "/api/graph/export", {"graph": "x", "name": "g"}, h)
    assert (bad["code"], bad["data"]["error_key"]) == (400, "invalid_payload")
