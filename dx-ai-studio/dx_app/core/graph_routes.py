"""/api/graph/* — the Graph Composer's server API.

Every route is guarded like the Lab routes: a cross-origin caller is refused first (Origin/Referer must be local,
DX_ALLOW_REMOTE_ORIGIN aside), then the X-Lab-Token session is required, for reads as well as writes, since runs start
NPU work and the catalog lists local model files.

    GET  /api/graph/catalog[?refresh=1]       models, CPU ops, examples, capabilities
    POST /api/graph/validate   {graph}        dx_app --check, errors pinned to nodes/edges
    POST /api/graph/memory     {graph}        NPU memory estimate and suggestions
    POST /api/graph/run        {graph, variant, inputs, uploads, max_inflight, frames}
    GET  /api/graph/run/poll?id=[&events_after=N]   GET /api/graph/run/result?id=   POST /api/graph/run/stop {id}
    GET  /api/graph/frame?uri=                 one frame of an input (zone and line drawing)
    POST /api/graph/run/frame  {run_id | graph, inputs, variant; stream, time_s | frame}
                                              one frame of a run's video run again with per-node layers (blocks)
    POST /api/graph/live/start {graph, variant, inputs, max_inflight, draw}
    GET  /api/graph/live/poll?id=[&events_after=N]   POST /api/graph/live/stop {id}
    POST /api/graph/gallery/build {folder, model, name?}   a gallery .bin for the gallery op (graph_gallery.py)
    GET  /api/graph/gallery/poll?id=   POST /api/graph/gallery/stop {id}
    POST /api/graph/export/plan {graph, name?, inputs?}    what a C++ project export holds (graph_export.py)
    POST /api/graph/export {graph, name, include_models?, inputs?}   the project folder and its zip (models: only when
                                                                     include_models is true)
    GET  /api/graph/projects   GET /api/graph/project?id=[&version=]   GET /api/graph/project/versions?id=
    POST /api/graph/project/save {id?, project}   POST /api/graph/project/delete {id}

GET /api/graph/live/frame?id= (the MJPEG stream of a Live) is served by dx_app/server.py, because an <img> cannot
send the X-Lab-Token header: it checks the origin and needs the running Live's job id, which only a caller holding a
session received from /api/graph/live/start.
Contract: tests/dx_app/test_graph_routes.py
"""
from __future__ import annotations

from dx_app.core import (graph_catalog, graph_export, graph_frame, graph_gallery, graph_live, graph_memory,
                         graph_projects, graph_run, graph_validate)
from dx_app.core.developer import _check_origin_local, require_lab

MAX_NODES = graph_validate.MAX_NODES


def _strip(err: dict) -> tuple:
    return {k: v for k, v in err.items() if k != "status"}, err.get("status", 403)


def _graph(data):
    g = data.get("graph")
    if not isinstance(g, dict) or not isinstance(g.get("nodes"), list) or not isinstance(g.get("edges", []), list):
        return None, ({"error": "graph is required", "error_key": "invalid_payload"}, 400)
    if len(g["nodes"]) > MAX_NODES:
        return None, ({"error": f"a graph may have at most {MAX_NODES} nodes", "error_key": "invalid_payload"}, 400)
    return g, None


def _project_call(fn, *args):
    try:
        return fn(*args)
    except ValueError as e:
        return {"error": str(e), "error_key": "invalid_project_id"}, 400
    except OSError as e:
        return {"error": f"the project could not be read or written: {e}", "error_key": "project_io_error"}, 500


def handle(method: str, path: str, query, data, headers, server_host) -> tuple:
    """(body, status) for one /api/graph/* request. `query(name, default)` reads the query string."""
    origin_err = _check_origin_local(headers.get("Origin"), server_host, referer=headers.get("Referer"))
    if origin_err:
        return _strip(origin_err)
    err = require_lab(headers.get("X-Lab-Token", ""))
    if err:
        return _strip(err)
    q = query or (lambda name, default=None: default)
    if method == "GET":
        if path == "/api/graph/catalog":
            return graph_catalog.catalog(refresh=q("refresh", "") == "1"), 200
        if path == "/api/graph/run/poll":
            return graph_run.poll(q("id", "") or "", q("events_after", "0")), 200
        if path == "/api/graph/live/poll":
            return graph_live.poll(q("id", "") or "", q("events_after", "0")), 200
        if path == "/api/graph/frame":
            return graph_frame.first_frame(q("uri", "") or "")
        if path == "/api/graph/gallery/poll":
            return graph_gallery.poll(q("id", "") or "")
        if path == "/api/graph/run/result":
            return graph_run.result(q("id", "") or ""), 200
        if path == "/api/graph/projects":
            return {"projects": graph_projects.list_projects()}, 200
        if path == "/api/graph/project":
            return _project_call(graph_projects.load, q("id", "") or "", q("version", None))
        if path == "/api/graph/project/versions":
            return _project_call(graph_projects.versions, q("id", "") or "")
        return {"error": "not found"}, 404
    data = data if isinstance(data, dict) else {}
    if path in ("/api/graph/validate", "/api/graph/memory", "/api/graph/run", "/api/graph/live/start"):
        g, bad = _graph(data)
        if bad:
            return bad
        if path == "/api/graph/validate":
            return graph_validate.validate(g), 200
        if path == "/api/graph/memory":
            return graph_memory.estimate(g), 200
        if path == "/api/graph/live/start":
            return graph_live.start(g, variant=data.get("variant", "sync"), inputs=data.get("inputs"),
                                    max_inflight=data.get("max_inflight"), draw=data.get("draw"))
        return graph_run.start(g, variant=data.get("variant", "sync"), inputs=data.get("inputs"),
                               uploads=data.get("uploads"), max_inflight=data.get("max_inflight"),
                               frames=data.get("frames"))
    if path in ("/api/graph/export/plan", "/api/graph/export"):
        g, bad = _graph(data)
        if bad:
            return bad
        if path == "/api/graph/export/plan":
            return graph_export.plan(g, name=data.get("name"), inputs=data.get("inputs"))
        return graph_export.export(g, data.get("name"), include_models=data.get("include_models") is True,
                                   inputs=data.get("inputs"))
    if path == "/api/graph/run/frame":
        if "graph" in data:
            _g, bad = _graph(data)
            if bad:
                return bad
        return graph_frame.inspect(data)
    if path == "/api/graph/run/stop":
        return graph_run.stop(str(data.get("id") or "")), 200
    if path == "/api/graph/live/stop":
        return graph_live.stop(str(data.get("id") or "")), 200
    if path == "/api/graph/gallery/build":
        return graph_gallery.start(data.get("folder"), data.get("model"), data.get("name"))
    if path == "/api/graph/gallery/stop":
        return graph_gallery.stop(str(data.get("id") or "")), 200
    if path == "/api/graph/project/save":
        return _project_call(graph_projects.save, data.get("project"), data.get("id") or None)
    if path == "/api/graph/project/delete":
        return _project_call(graph_projects.delete, data.get("id") or "")
    return {"error": "not found"}, 404
