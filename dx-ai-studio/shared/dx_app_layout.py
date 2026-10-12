"""dx_app example layout — the one place that builds example paths.

dx_app comes in two shapes:

- **legacy**: ``src/<lang>_example/<task>/<model>/<model>_<variant>.{py,cpp}``
- **per_model**: ``src/<lang>_example/<task>/<family>/<stem>/<stem>_<variant>.{py,cpp}`` — the stem is the
  ``.dxnn`` name and the registry's ``variant``. There is no shim for the legacy paths.

Either way the C++ binary is ``<build>/<name>_<variant>`` (name = the legacy model, or the per_model stem), so
only the **example folder** differs. Callers pass (task, name) and the folder is resolved here.

Model files are looked up in ``assets/models`` and then in the suite's ``workspace/res/models`` (the same order as
run_demo.sh / run_demo.py). A 0-byte file is a partial download and counts as missing.

Contract: tests/dx_app/test_layout.py
"""
from __future__ import annotations

import json
import struct
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Iterable, Optional

LEGACY = "legacy"
PER_MODEL = "per_model"
LANGS = ("python", "cpp")
_SKIP = {"common", "build", "sample", "__pycache__", "utils", "factory"}
_SUFFIX = {"python": ".py", "cpp": ".cpp"}


@dataclass(frozen=True)
class Example:
    task: str
    name: str                      # legacy: model dir · per_model: stem (= .dxnn name)
    family: Optional[str] = None   # per_model only
    py_dir: Optional[Path] = None
    cpp_dir: Optional[Path] = None

    def dir(self, lang: str) -> Optional[Path]:
        return self.py_dir if lang == "python" else self.cpp_dir


def _base(root: Path, lang: str) -> Path:
    return Path(root) / "src" / f"{lang}_example"


def _is_example_dir(d: Path, lang: str) -> bool:
    suf = _SUFFIX[lang]
    return any((d / f"{d.name}_{v}{suf}").is_file() for v in ("sync", "async"))


@lru_cache(maxsize=8)
def _detect(root: str) -> str:
    reg = Path(root) / "config" / "model_registry.json"
    try:
        data = json.loads(reg.read_text(encoding="utf-8"))
        rows = data if isinstance(data, list) else list(data.values()) if isinstance(data, dict) else []
        if any(isinstance(r, dict) and r.get("variant") and r.get("family") for r in rows[:50]):
            return PER_MODEL
    except (OSError, ValueError):
        pass
    # No registry: per_model if any <task>/<family>/<stem>/<stem>_sync.* exists in the tree
    for lang in LANGS:
        base = _base(Path(root), lang)
        if not base.is_dir():
            continue
        for task in base.iterdir():
            if not task.is_dir() or task.name in _SKIP:
                continue
            for fam in task.iterdir():
                if fam.is_dir() and any(s.is_dir() and _is_example_dir(s, lang) for s in fam.iterdir()):
                    return PER_MODEL
    return LEGACY


def detect(root) -> str:
    return _detect(str(root))


@lru_cache(maxsize=8)
def _index(root: str) -> dict:
    kind = _detect(root)
    found: dict = {}
    for lang in LANGS:
        base = _base(Path(root), lang)
        if not base.is_dir():
            continue
        for task in sorted(p for p in base.iterdir() if p.is_dir() and p.name not in _SKIP):
            if kind == LEGACY:
                cands = [(None, d) for d in task.iterdir() if d.is_dir() and d.name not in _SKIP]
            else:
                cands = [(fam.name, d) for fam in task.iterdir() if fam.is_dir() and fam.name not in _SKIP
                         for d in fam.iterdir() if d.is_dir() and d.name not in _SKIP]
                # add_model.sh creates <task>/<model>/ — such a folder inside a per-model tree is an example too
                cands += [(None, d) for d in task.iterdir() if d.is_dir() and d.name not in _SKIP]
            for family, d in cands:
                if not _is_example_dir(d, lang):
                    continue
                key = (task.name, d.name)
                cur = found.get(key) or Example(task=task.name, name=d.name, family=family)
                found[key] = Example(cur.task, cur.name, cur.family or family,
                                     d if lang == "python" else cur.py_dir,
                                     d if lang == "cpp" else cur.cpp_dir)
    return found


def clear_cache() -> None:
    _detect.cache_clear()
    _index.cache_clear()


def examples(root) -> Iterable[Example]:
    return list(_index(str(root)).values())


def find(root, task: str, name: str) -> Optional[Example]:
    ex = _index(str(root)).get((task, name))
    if ex is None and task:
        # Called by an old name (e.g. a legacy task key): use the example if exactly one has this name
        hits = [e for e in _index(str(root)).values() if e.name == name]
        ex = hits[0] if len(hits) == 1 else None
    return ex


def _registry_variants(root: str) -> dict:
    reg = Path(root) / "config" / "model_registry.json"
    try:
        data = json.loads(reg.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    rows = data if isinstance(data, list) else list(data.values()) if isinstance(data, dict) else []
    return {r["model_name"]: r["variant"] for r in rows
            if isinstance(r, dict) and r.get("model_name") and r.get("variant")}


def example_name(root, task: str, name: str, model_file: str = "") -> str:
    """The caller's name → this tree's example name. Unknown names come back unchanged.

    Model Zoo calls with a catalog id (`rtdetr_r18vd_6x_640x640`), older clients with the registry model_name
    (`yolo26n`). Per-model example names are .dxnn stems. Order: given name → model_file stem → registry variant.
    (Contract: tests/dx_app/test_layout.py — without this, dx_app would borrow another model's binary of the same
    task.)"""
    if find(root, task, name):
        return name
    stem = Path(model_file).name[: -len(".dxnn")] if str(model_file).endswith(".dxnn") else ""
    if stem and stem != name and find(root, task, stem):
        return stem
    variant = _registry_variants(str(root)).get(name)
    if variant and find(root, task, variant):
        return variant
    return name


def example_dir(root, lang: str, task: str, name: str) -> Path:
    """The example folder. An unknown example gets a legacy-shaped path that does not exist, so the caller's
    "missing" check still applies."""
    ex = find(root, task, name)
    d = ex.dir(lang) if ex else None
    return d if d is not None else _base(Path(root), lang) / task / name


def python_script(root, task: str, name: str, variant: str) -> Path:
    return example_dir(root, "python", task, name) / f"{name}_{variant}.py"


def cpp_source(root, task: str, name: str, variant: str) -> Path:
    return example_dir(root, "cpp", task, name) / f"{name}_{variant}.cpp"


def cpp_binary(build_dir, name: str, variant: str) -> Path:
    return Path(build_dir) / f"{name}_{variant}"


def config_path(root, task: str, name: str) -> Optional[Path]:
    for lang in ("cpp", "python"):
        p = example_dir(root, lang, task, name) / "config.json"
        if p.is_file():
            return p
    return None


def load_config(root, task: str, name: str) -> dict:
    p = config_path(root, task, name)
    if p is None:
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def flat_config(data: dict) -> dict:
    """A per_model config.json is nested, with thresholds under ``config``. What is passed to a run is always flat
    — the C++ ``--config`` reader reads flat keys only."""
    if isinstance(data, dict) and "variant" in data and isinstance(data.get("config"), dict):
        return dict(data["config"])
    return dict(data or {})


def threshold_config(root, task: str, name: str) -> dict:
    return flat_config(load_config(root, task, name))


# ── model files ─────────────────────────────────────────────────────────────────────────
def model_locations(root, suite_root=None) -> list:
    locs = [Path(root) / "assets" / "models"]
    if suite_root is not None:
        locs.append(Path(suite_root) / "workspace" / "res" / "models")
    return locs


def find_model(model_file: str, root, suite_root=None, models_dir=None) -> Optional[Path]:
    """``assets/models/x.dxnn`` or ``x.dxnn`` → the actual file (0-byte files excluded). Absolute paths are only
    checked."""
    p = PurePosixPath(model_file)
    if p.is_absolute():
        q = Path(model_file)
        return q if q.is_file() and q.stat().st_size > 0 else None
    rel = p.parts[2:] if p.parts[:2] == ("assets", "models") else p.parts
    locs = ([Path(models_dir)] if models_dir else []) + model_locations(root, suite_root)
    if p.parts[:2] != ("assets", "models") and len(p.parts) > 1:
        locs = [Path(root)] + locs            # a relative path outside the model tree, e.g. sample/...
        rel = p.parts
    for base in locs:
        q = base.joinpath(*rel)
        try:
            if q.is_file() and q.stat().st_size > 0:
                return q
        except OSError:
            continue
    return None


def container_version(path) -> Optional[int]:
    """.dxnn container version: the little-endian uint32 after 'DXNN' (reads 8 bytes, no NPU needed)."""
    try:
        with open(path, "rb") as f:
            head = f.read(8)
    except OSError:
        return None
    if len(head) < 8 or head[:4] != b"DXNN":
        return None
    v = struct.unpack("<I", head[4:8])[0]
    # Not a version (e.g. a test fixture with text after 'DXNN'): unknown, and unknown never blocks
    return v if 0 < v < 256 else None
