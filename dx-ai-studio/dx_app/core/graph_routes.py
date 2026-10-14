"""/api/graph/* — the Graph Composer's server API.

Every route is guarded like the Lab routes: a cross-origin caller is refused first (Origin/Referer must be local,
DX_ALLOW_REMOTE_ORIGIN aside), then the X-Lab-Token session is required, for reads as well as writes, since runs start
NPU work and the catalog lists local model files.

    GET  /api/graph/catalog[?refresh=1]       models, CPU ops, examples, capabilities
    POST /api/graph/validate   {graph}        dx_app --check, errors pinned to nodes/edges
    POST /api/graph/memory     {graph}        NPU memory estimate and suggestions
    POST /api/graph/run        {graph, variant, inputs, uploads, max_inflight, frames}
    GET  /api/graph/run/poll?id=   GET /api/graph/run/result?id=   POST /api/graph/run/stop {id}
    GET  /api/graph/projects   GET /api/graph/project?id=[&version=]   GET /api/graph/project/versions?id=
    POST /api/graph/project/save {id?, project}   POST /api/graph/project/delete {id}

Contract: tests/dx_app/test_graph_routes.py
"""
from __future__ import annotations

from dx_app.core import graph_catalog, graph_memory, graph_projects, graph_run, graph_validate
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
            return graph_run.poll(q("id", "") or ""), 200
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
    if path in ("/api/graph/validate", "/api/graph/memory", "/api/graph/run"):
        g, bad = _graph(data)
        if bad:
            return bad
        if path == "/api/graph/validate":
            return graph_validate.validate(g), 200
        if path == "/api/graph/memory":
            return graph_memory.estimate(g), 200
        return graph_run.start(g, variant=data.get("variant", "sync"), inputs=data.get("inputs"),
                               uploads=data.get("uploads"), max_inflight=data.get("max_inflight"),
                               frames=data.get("frames"))
    if path == "/api/graph/run/stop":
        return graph_run.stop(str(data.get("id") or "")), 200
    if path == "/api/graph/project/save":
        return _project_call(graph_projects.save, data.get("project"), data.get("id") or None)
    if path == "/api/graph/project/delete":
        return _project_call(graph_projects.delete, data.get("id") or "")
    return {"error": "not found"}, 404
