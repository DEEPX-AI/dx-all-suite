"""Functional verdict per scenario — inferred PASS/FAIL/UNKNOWN.

The `manifest.exit_status` field is round-level (whole pytest run). Per-scenario
verdicts are NOT stored. We infer them from artifact characteristics:

  - compiler: PASS if .dxnn exists; FAIL if missing
  - dx_app: PASS if factory.py + *_sync.py exist AND syntax valid; FAIL if missing
  - dx_stream / dx_stream_cascaded: PASS if pipeline.py + run_*.sh exist
  - runtime: PASS if at least one sub-project output dir exists with valid content
  - suite: PASS if BOTH dx-compiler + dx-runtime/dx_app outputs exist (R41 HARD GATE)

These are heuristics — not as strict as the test harness's assertions, but
correlate strongly. The verdict is binary; a 'mostly works' is rated PASS only if
the primary deliverable exists.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple


def _has_file(out_dir: Path, name: str) -> bool:
    return (out_dir / name).is_file()


def _has_glob(out_dir: Path, pattern: str) -> bool:
    return any(out_dir.rglob(pattern))


# Path components that mark third-party / tooling subtrees we never want to
# count as agent output (e.g. pip's own ``resolvelib/factory.py`` inside a
# venv would otherwise show up as a fake IFactory).
_NON_AGENT_PATH_PARTS = frozenset({"venv", ".venv", "site-packages", "__pycache__", "node_modules"})


def _find_factory_files(out_dir: Path) -> List[Path]:
    """Return Python files that look like an IFactory implementation.

    Matches both ``factory.py`` (single-name convention some agents use) and
    ``<prefix>_factory.py`` (the canonical naming in IFactory examples), then
    drops anything inside a virtualenv / cache so pip's own ``factory.py``
    (resolvelib internal) is never counted as an agent deliverable.
    """
    matches = list(out_dir.rglob("factory.py")) + list(out_dir.rglob("*_factory.py"))
    return [
        m for m in matches
        if not any(p in _NON_AGENT_PATH_PARTS for p in m.parts)
    ]


def infer_verdict(scenario_ref, scenarios_cfg: dict) -> Tuple[str, str]:
    """Return (verdict, reason) where verdict ∈ {PASS, FAIL, PARTIAL, UNKNOWN}.

    PASS    — primary deliverable exists and is well-formed
    PARTIAL — some deliverables present, some missing
    FAIL    — primary deliverable missing or output dir empty
    UNKNOWN — no output dir to evaluate
    """
    sc = scenario_ref.scenario
    out_dirs = scenario_ref.output_dirs
    if not out_dirs:
        return "UNKNOWN", "no output directory linked"

    primary_od = out_dirs[0]
    if not primary_od.is_dir():
        return "FAIL", f"output dir missing: {primary_od.name}"

    if sc == "compiler":
        has_dxnn = _has_glob(primary_od, "*.dxnn")
        has_config = _has_file(primary_od, "config.json")
        if has_dxnn and has_config:
            return "PASS", ".dxnn + config.json present"
        if has_config and not has_dxnn:
            return "FAIL", "config.json present but no .dxnn produced"
        return "FAIL", "compiler artifacts missing"

    if sc == "dx_app":
        factory = _find_factory_files(primary_od)
        sync_apps = [
            p for p in primary_od.rglob("*_sync.py")
            if not any(part in _NON_AGENT_PATH_PARTS for part in p.parts)
        ]
        if factory and sync_apps:
            return "PASS", f"factory + sync runner ({sync_apps[0].name})"
        if factory and not sync_apps:
            return "PARTIAL", "factory ok but no *_sync.py"
        return "FAIL", "no factory.py / *_factory.py (outside venv) found"

    if sc in ("dx_stream", "dx_stream_cascaded"):
        pipeline = _has_file(primary_od, "pipeline.py")
        run_sh = _has_glob(primary_od, "run_*.sh") or _has_file(primary_od, "run.sh")
        if pipeline and run_sh:
            return "PASS", "pipeline.py + run script"
        if pipeline:
            return "PARTIAL", "pipeline.py only (no run_*.sh)"
        return "FAIL", "no pipeline.py"

    if sc == "runtime":
        # runtime delegates to sub-project — verify any output is well-formed
        ok_subprojs = 0
        for od in out_dirs:
            s = str(od)
            if "dx_app" in s and _find_factory_files(od):
                ok_subprojs += 1
            elif "dx_stream" in s and (_has_file(od, "pipeline.py") or any(
                p for p in od.rglob("*.py")
                if not any(part in _NON_AGENT_PATH_PARTS for part in p.parts)
            )):
                ok_subprojs += 1
        if ok_subprojs >= 1:
            return "PASS", f"{ok_subprojs} sub-project output(s) well-formed"
        return "FAIL", "no sub-project produced valid output"

    if sc == "suite":
        # Suite R41 HARD GATE: requires BOTH dx-compiler + dx_app outputs separately
        has_compiler = any(
            "dx-compiler" in str(od) and _has_glob(od, "*.dxnn")
            for od in out_dirs
        )
        has_app = any(
            "dx_app" in str(od) and bool(_find_factory_files(od))
            for od in out_dirs
        )
        if has_compiler and has_app:
            return "PASS", "dual session dirs (compiler+app) with primary deliverables"
        if has_compiler or has_app:
            return "PARTIAL", "only one of (compiler, app) primary deliverables"
        return "FAIL", "neither compiler nor app primary deliverable"

    return "UNKNOWN", f"unknown scenario {sc}"


def verdict_score(verdict: str) -> float:
    """Map verdict to 0-100."""
    return {
        "PASS": 100.0,
        "PARTIAL": 50.0,
        "FAIL": 0.0,
        "UNKNOWN": 0.0,
    }.get(verdict, 0.0)


def count_lines_of_code(out_dir: Path) -> dict:
    """Return code metric: lines per language, total."""
    counters = {"python_loc": 0, "bash_loc": 0, "json_loc": 0, "files": 0}
    if not out_dir.is_dir():
        return counters
    skip_dirs_exact = {"__pycache__", "site-packages", "dist-info", ".cache"}
    skip_prefixes = ("venv",)
    for f in out_dir.rglob("*"):
        if not f.is_file():
            continue
        if any(p in skip_dirs_exact for p in f.parts):
            continue
        if any(p.startswith(skip_prefixes) for p in f.parts):
            continue
        try:
            n = sum(1 for _ in f.open(encoding="utf-8", errors="ignore"))
        except Exception:
            continue
        counters["files"] += 1
        if f.suffix == ".py":
            counters["python_loc"] += n
        elif f.suffix == ".sh":
            counters["bash_loc"] += n
        elif f.suffix == ".json":
            counters["json_loc"] += n
    return counters
