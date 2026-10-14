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
    """The projects folder; only save() creates it, so opening the page leaves the workspace untouched."""
    return Path(config.OUTPUTS_DIR) / "graph" / "projects"


def slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(name or "").lower()).strip("-")[:48]
    return s or "graph"


def _dir(pid) -> Path:
    if not isinstance(pid, str) or not _ID.fullmatch(pid):
        raise ValueError("invalid project id")
    d = projects_dir() / pid
    if d.is_symlink():
        raise ValueError("the project folder is a link; Studio does not follow it")
    return d


_CORRUPT = ({"error": "the project file is damaged and cannot be read", "error_key": "project_corrupt"}, 422)


def _read(f: Path):
    """A project or version file as a dict; None when it is a link, not JSON, or not an object."""
    try:
        if f.is_symlink():
            return None
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


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
    if not projects_dir().is_dir():
        return out
    for d in projects_dir().iterdir():
        if d.is_symlink() or not (d.is_dir() and _ID.fullmatch(d.name) and (d / "project.json").is_file()):
            continue
        project = _read(d / "project.json")
        if project is None:
            continue
        meta = project.get("meta") if isinstance(project.get("meta"), dict) else {}
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
    if not f.is_file() and not f.is_symlink():
        return {"error": "project not found", "error_key": "project_not_found"}, 404
    project = _read(f)
    if project is None:
        return _CORRUPT
    meta = project.get("meta") if isinstance(project.get("meta"), dict) else {}
    return {"id": pid, "version": meta.get("version"), "project": project}, 200


def versions(pid):
    d = _dir(pid)
    if not d.is_dir():
        return {"error": "project not found", "error_key": "project_not_found"}, 404
    out = []
    for n in reversed(_versions(d)):
        meta = (_read(d / "versions" / f"{n}.json") or {}).get("meta")
        meta = meta if isinstance(meta, dict) else {}
        out.append({"version": n, "saved_at": meta.get("saved_at")})
    return {"id": pid, "versions": out}, 200


def delete(pid):
    d = _dir(pid)
    if not d.is_dir():
        return {"error": "project not found", "error_key": "project_not_found"}, 404
    with _lock:
        shutil.rmtree(d)
    return {"ok": True, "id": pid}, 200
