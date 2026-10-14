"""Graph Composer projects in the Studio workspace.

    outputs/dx_app/graph/projects/<id>/project.json      the latest save
    outputs/dx_app/graph/projects/<id>/versions/<n>.json every save, newest MAX_VERSIONS kept

A project file is {"schema": 1, "graph": <dx_app graph JSON>, "layout": {...}, "meta": {...}}. layout and meta stay
outside "graph" because dx_app rejects unknown keys, so "graph" alone is what runs. Contract: tests/dx_app/test_graph_projects.py
"""
from __future__ import annotations

import json
import re
import shutil
import threading
import time
from pathlib import Path

from dx_app.core import config

SCHEMA = 1
MAX_VERSIONS = 50
MAX_BYTES = 1024 * 1024
_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_lock = threading.Lock()


def projects_dir() -> Path:
    d = Path(config.OUTPUTS_DIR) / "graph" / "projects"
    d.mkdir(parents=True, exist_ok=True)
    return d


def slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(name or "").lower()).strip("-")[:48]
    return s or "graph"


def _dir(pid) -> Path:
    if not isinstance(pid, str) or not _ID.fullmatch(pid):
        raise ValueError("invalid project id")
    return projects_dir() / pid


def validate_project(p) -> str | None:
    if not isinstance(p, dict):
        return "a project must be an object"
    if p.get("schema") != SCHEMA:
        return "unsupported project schema"
    g = p.get("graph")
    if not isinstance(g, dict) or not isinstance(g.get("nodes"), list) or not isinstance(g.get("edges", []), list):
        return "the project graph is invalid"
    if not isinstance(p.get("layout", {}), dict) or not isinstance(p.get("meta", {}), dict):
        return "layout and meta must be objects"
    if len(json.dumps(p)) > MAX_BYTES:
        return "the project is too large"
    return None


def _versions(d: Path) -> list:
    nums = []
    for f in (d / "versions").glob("*.json"):
        if f.stem.isdigit():
            nums.append(int(f.stem))
    return sorted(nums)


def save(project, pid=None):
    err = validate_project(project)
    if err:
        return {"error": err, "error_key": "invalid_project"}, 400
    name = str((project.get("meta") or {}).get("name") or project["graph"].get("name") or "graph")[:80]
    with _lock:
        if pid in (None, ""):
            base, pid, i = slug(name), slug(name), 2
            while (projects_dir() / pid).exists():
                pid, i = f"{base}-{i}", i + 1
        d = _dir(pid)
        (d / "versions").mkdir(parents=True, exist_ok=True)
        nums = _versions(d)
        n = nums[-1] + 1 if nums else 1
        data = dict(project)
        data["meta"] = dict(project.get("meta") or {}, name=name, saved_at=time.time(), version=n)
        text = json.dumps(data, indent=2, ensure_ascii=False)
        (d / "versions" / f"{n}.json").write_text(text, encoding="utf-8")
        tmp = d / "project.json.tmp"
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(d / "project.json")
        for old in (nums + [n])[:-MAX_VERSIONS]:
            (d / "versions" / f"{old}.json").unlink(missing_ok=True)
    return {"id": pid, "version": n, "name": name}, 200


def list_projects() -> list:
    out = []
    for d in projects_dir().iterdir():
        if not (d.is_dir() and _ID.fullmatch(d.name) and (d / "project.json").is_file()):
            continue
        try:
            meta = json.loads((d / "project.json").read_text(encoding="utf-8")).get("meta") or {}
        except (OSError, ValueError):
            continue
        out.append({"id": d.name, "name": meta.get("name") or d.name, "version": meta.get("version"),
                    "saved_at": meta.get("saved_at"), "versions": len(_versions(d))})
    return sorted(out, key=lambda p: -(p["saved_at"] or 0))


def load(pid, version=None):
    d = _dir(pid)
    if version not in (None, ""):
        if not str(version).isdigit():
            raise ValueError("invalid version")
        f = d / "versions" / f"{int(version)}.json"
    else:
        f = d / "project.json"
    if not f.is_file():
        return {"error": "project not found", "error_key": "project_not_found"}, 404
    project = json.loads(f.read_text(encoding="utf-8"))
    return {"id": pid, "version": (project.get("meta") or {}).get("version"), "project": project}, 200


def versions(pid):
    d = _dir(pid)
    if not d.is_dir():
        return {"error": "project not found", "error_key": "project_not_found"}, 404
    out = []
    for n in reversed(_versions(d)):
        try:
            meta = json.loads((d / "versions" / f"{n}.json").read_text(encoding="utf-8")).get("meta") or {}
        except (OSError, ValueError):
            meta = {}
        out.append({"version": n, "saved_at": meta.get("saved_at")})
    return {"id": pid, "versions": out}, 200


def delete(pid):
    d = _dir(pid)
    if not d.is_dir():
        return {"error": "project not found", "error_key": "project_not_found"}, 404
    with _lock:
        shutil.rmtree(d)
    return {"ok": True, "id": pid}, 200
