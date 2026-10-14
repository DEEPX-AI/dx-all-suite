"""/api/graph/* routes: Lab-session and same-origin guards on every route, then each route reaches its module."""
from __future__ import annotations

import pytest

from dx_app.core import config, graph_catalog, graph_memory, graph_routes, graph_run, graph_validate
from dx_app.core.developer import lab_session

GET_ROUTES = ("/api/graph/catalog", "/api/graph/run/poll", "/api/graph/run/result", "/api/graph/projects",
              "/api/graph/project", "/api/graph/project/versions")
POST_ROUTES = ("/api/graph/validate", "/api/graph/memory", "/api/graph/run", "/api/graph/run/stop",
               "/api/graph/project/save", "/api/graph/project/delete")
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
