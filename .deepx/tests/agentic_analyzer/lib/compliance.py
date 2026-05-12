"""HARD GATE compliance checks against the dx-agentic-dev harness intent.

Computes a compliance score per scenario, where each check contributes points.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .session import SessionData, parse_session_id


@dataclass
class ComplianceReport:
    """Per-scenario compliance breakdown."""
    checks: Dict[str, bool] = field(default_factory=dict)
    notes: Dict[str, str] = field(default_factory=dict)
    score_passed: int = 0
    score_total: int = 0

    @property
    def score_pct(self) -> float:
        if self.score_total == 0:
            return 0.0
        return 100.0 * self.score_passed / self.score_total

    def add(self, name: str, passed: bool, note: str = "") -> None:
        self.checks[name] = passed
        if note:
            self.notes[name] = note
        self.score_total += 1
        if passed:
            self.score_passed += 1


def _check_session_id_format(name: str) -> tuple[bool, str]:
    parsed = parse_session_id(name)
    if not parsed:
        return False, f"unrecognized session_id format: {name}"
    return True, f"agent={parsed['agent']} task={parsed['task']}"


def _check_output_dir_under_session_id(out_dir: Path) -> tuple[bool, str]:
    """Verify the path is dx-agentic-dev/<session_id>/ with valid agent prefix."""
    parts = out_dir.parts
    if "dx-agentic-dev" not in parts:
        return False, "not under dx-agentic-dev/"
    idx = parts.index("dx-agentic-dev")
    if idx + 1 >= len(parts):
        return False, "no session_id segment"
    sid = parts[idx + 1]
    ok, note = _check_session_id_format(sid)
    return ok, note


def _files_exist_under(out_dir: Path, names: List[str]) -> Dict[str, bool]:
    return {n: (out_dir / n).is_file() for n in names}


def _glob_exists(out_dir: Path, pattern: str) -> bool:
    return any(True for _ in out_dir.rglob(pattern))


def _has_factory_methods(out_dir: Path, required: List[str]) -> tuple[bool, str]:
    """Scan for *_factory.py and check that all 5 IFactory methods appear."""
    factory_files = list(out_dir.rglob("*_factory.py"))
    if not factory_files:
        return False, "no *_factory.py file found"
    # Take the first; in real apps multiple factories may exist but each should follow pattern
    sample = factory_files[0]
    try:
        body = sample.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False, "factory read failed"
    missing = [m for m in required if f"def {m}" not in body]
    if missing:
        return False, f"factory missing methods: {', '.join(missing)}"
    return True, f"factory ok ({sample.name})"


def _check_prohibited_in_session_log(out_dir: Path, patterns: List[str]) -> tuple[bool, str]:
    log = out_dir / "session.log"
    if not log.is_file():
        return False, "session.log missing"
    try:
        body = log.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False, "session.log read failed"
    hits = [p for p in patterns if p in body or re.search(p, body)]
    if hits:
        return False, f"prohibited pattern(s) found: {hits[:3]}"
    return True, "session.log clean (no fabrication markers)"


def evaluate_compliance(
    scenario_ref,
    session_data: SessionData,
    scenarios_cfg: dict,
    rules: dict,
) -> ComplianceReport:
    """Run compliance checks for one ScenarioRef."""
    rep = ComplianceReport()
    scen_conf = scenarios_cfg.get(scenario_ref.scenario, {})
    mandatory = scen_conf.get("mandatory_files", []) or []
    file_globs = scen_conf.get("file_globs", []) or []
    requires_two_outputs = scen_conf.get("requires_two_outputs", False)
    expected_dirs = scen_conf.get("expected_output_dirs", []) or []

    # 1. START sentinel emitted
    rep.add("sentinel_start", session_data.has_start_sentinel)

    # 2. DONE sentinel emitted (skip for sessions that produced no files)
    rep.add("sentinel_done", session_data.has_done_sentinel)

    # 3. At least one output dir under dx-agentic-dev/<session_id>/
    out_dirs = scenario_ref.output_dirs
    rep.add("output_isolation_present",
            any("dx-agentic-dev" in str(p) for p in out_dirs),
            note=f"{len(out_dirs)} symlinks")

    # 4. Session ID format for each output dir
    if out_dirs:
        all_ok = True
        notes_list = []
        for od in out_dirs:
            ok, note = _check_output_dir_under_session_id(od)
            if not ok:
                all_ok = False
            notes_list.append(f"{od.name}: {note}")
        rep.add("session_id_format", all_ok, note="; ".join(notes_list[:3]))
    else:
        rep.add("session_id_format", False, note="no output dirs to check")

    # 5. Suite-specific: requires TWO distinct session dirs (R41 HARD GATE)
    if requires_two_outputs:
        # Check unique parent sub-projects in output dirs
        sub_projs = set()
        for od in out_dirs:
            s = str(od)
            for marker in expected_dirs:
                if marker in s:
                    sub_projs.add(marker)
        ok = len(sub_projs) >= len(expected_dirs)
        rep.add("suite_dual_session_dirs",
                ok,
                note=f"found {sorted(sub_projs)} (expected {expected_dirs})")

    # 6. Mandatory deliverables — applied per output dir
    if mandatory:
        for od in out_dirs[:1]:  # check the first/primary output dir
            existence = _files_exist_under(od, mandatory)
            missing = [n for n, ok in existence.items() if not ok]
            present_count = sum(1 for ok in existence.values() if ok)
            rep.add(
                "mandatory_deliverables",
                len(missing) == 0,
                note=f"{present_count}/{len(mandatory)} present"
                     + (f"; missing: {missing}" if missing else ""),
            )
        if not out_dirs:
            rep.add("mandatory_deliverables", False, note="no output dirs")

    # 7. File-glob deliverables (e.g., *.dxnn, run_*.sh)
    for pat in file_globs:
        for od in out_dirs[:1]:
            rep.add(f"file_present[{pat}]", _glob_exists(od, pat))

    # 8. IFactory 5-method (only for dx_app/runtime/suite app outputs)
    if scenario_ref.scenario in ("dx_app", "runtime", "suite"):
        required_methods = rules.get("required_in_factory", []) or []
        # Find a dx_app output dir among out_dirs
        target = None
        for od in out_dirs:
            if "dx_app" in str(od) or scenario_ref.scenario == "dx_app":
                target = od
                break
        if target is not None and required_methods:
            ok, note = _has_factory_methods(target, required_methods)
            rep.add("ifactory_5_methods", ok, note=note)

    # 9. session.log clean (no fabricated heredoc / echo)
    prohibited_log = rules.get("prohibited_in_session_log", []) or []
    if prohibited_log and out_dirs:
        ok, note = _check_prohibited_in_session_log(out_dirs[0], prohibited_log)
        rep.add("session_log_authentic", ok, note=note)

    return rep
