"""Execution Trace analysis — detect whether the agent actually executed commands.

Looks for evidence files (session.log, compile_out.log, *.pid, error.log) and
success/failure markers to score how well the agent's execution went.

This is **distinct from Verdict** (which is just artifact existence):
  - Verdict says: did the primary deliverable exist?
  - ExecutionTrace says: did the agent actually run commands + did those commands succeed?

Useful because an agent could write all the files (high Verdict) but never run them
(low ExecutionTrace), suggesting incomplete work.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


# Success / failure marker patterns
SUCCESS_MARKERS = [
    r"\bSanity check PASSED\b",
    r"\bCompilation DONE\b",
    r"\bCompilation complete\b",
    r"\bSuccess(?:fully)?\b",
    r"\b(?:RESULT|VERDICT):\s*PASS\b",
    r"\bRESULT:\s*PASS\b",
    r"\bAll checks passed\b",
    r"\bgenerated successfully\b",
]

FAILURE_MARKERS = [
    r"Traceback \(most recent call last\)",
    r"\bError:",
    r"\bERROR:",
    r"\bFAIL(?:ED)?\b",
    r"\bRESULT:\s*FAIL\b",
    r"NotImplementedError",
    r"\bImportError\b",
    r"\bModuleNotFoundError\b",
    r"PEP 668",
    r"externally-managed-environment",
]

TIMEOUT_MARKERS = [
    r"\btimeout\b",
    r"\bTimeout\b",
    r"\bTIMEOUT\b",
    r"\bkilled\b",
    r"signal.*SIGKILL",
    r"signal.*SIGTERM",
    r"killed.*timeout",
    r"Process exceeded.*timeout",
]


@dataclass
class ExecutionReport:
    """Per-output-dir execution trace summary."""
    has_session_log: bool = False
    session_log_size: int = 0
    has_compile_log: bool = False
    has_pid_file: bool = False
    has_error_log: bool = False
    error_log_nonempty: bool = False
    has_verify_script: bool = False
    success_markers: List[str] = field(default_factory=list)
    failure_markers: List[str] = field(default_factory=list)
    timeout_markers: List[str] = field(default_factory=list)
    primary_artifact_size_bytes: int = 0
    suspected_timeout: bool = False
    # Composite 0-100
    score: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)


def _scan_file_for_markers(path: Path, patterns: List[str], limit: int = 50_000) -> List[str]:
    """Scan first `limit` chars of file for marker patterns. Returns first match per pattern."""
    if not path.is_file():
        return []
    try:
        with path.open(encoding="utf-8", errors="ignore") as f:
            text = f.read(limit)
    except Exception:
        return []
    hits = []
    for p in patterns:
        m = re.search(p, text)
        if m:
            hits.append(m.group(0)[:60])
    return hits


def _scan_dir_for_markers(out_dir: Path, log_globs: List[str], patterns: List[str]) -> List[str]:
    """Aggregate marker hits across all log files matching globs in out_dir."""
    if not out_dir.is_dir():
        return []
    hits = []
    for glob in log_globs:
        for f in out_dir.rglob(glob):
            if f.is_file():
                file_hits = _scan_file_for_markers(f, patterns)
                hits.extend(file_hits)
    # Deduplicate
    return list(dict.fromkeys(hits))[:5]


def evaluate_execution(out_dir: Path, scenario: str) -> ExecutionReport:
    """Inspect log files in out_dir to score execution evidence."""
    rep = ExecutionReport()
    if not out_dir.is_dir():
        return rep

    # File detections
    session_log = out_dir / "session.log"
    if session_log.is_file():
        rep.has_session_log = True
        try:
            rep.session_log_size = session_log.stat().st_size
        except Exception:
            pass

    error_log = out_dir / "error.log"
    if error_log.is_file():
        rep.has_error_log = True
        try:
            if error_log.stat().st_size > 0:
                rep.error_log_nonempty = True
        except Exception:
            pass

    if any(out_dir.glob("compile.pid")):
        rep.has_pid_file = True
    if any(out_dir.glob("*compile*.log")):
        rep.has_compile_log = True
    if (out_dir / "verify.py").is_file():
        rep.has_verify_script = True

    # Primary artifact size — meaningful when present
    if scenario == "compiler":
        for dxnn in out_dir.glob("*.dxnn"):
            try:
                rep.primary_artifact_size_bytes = max(rep.primary_artifact_size_bytes,
                                                       dxnn.stat().st_size)
            except Exception:
                pass

    # Marker scans across multiple log files
    log_globs = ["session.log", "compile_out.log", "compile_output.log",
                 "compiler.log", "verify_out.log", "error.log", "*.log"]
    rep.success_markers = _scan_dir_for_markers(out_dir, log_globs, SUCCESS_MARKERS)
    rep.failure_markers = _scan_dir_for_markers(out_dir, log_globs, FAILURE_MARKERS)
    rep.timeout_markers = _scan_dir_for_markers(out_dir, log_globs, TIMEOUT_MARKERS)

    # ============== Scoring ==============
    score = 0.0
    bd: Dict[str, float] = {}

    # Has session.log with meaningful content (not just placeholder)
    if rep.has_session_log:
        if rep.session_log_size >= 1024:
            bd["session_log_substantial"] = 20.0
        else:
            bd["session_log_present"] = 10.0
    score += bd.get("session_log_substantial", bd.get("session_log_present", 0.0))

    # Has command-execution evidence files (PID file, dedicated compile log)
    if rep.has_pid_file or rep.has_compile_log:
        bd["execution_evidence"] = 15.0
        score += 15.0

    # Has verify script
    if rep.has_verify_script:
        bd["verify_script_present"] = 5.0
        score += 5.0

    # Success markers detected
    if rep.success_markers:
        marker_score = min(25.0, 5.0 * len(rep.success_markers))
        bd["success_markers"] = marker_score
        score += marker_score

    # No failure markers (error.log empty, no Error: in logs)
    if not rep.failure_markers and not rep.error_log_nonempty:
        bd["clean_logs"] = 15.0
        score += 15.0
    else:
        # Partial credit if some markers but not many
        if rep.failure_markers:
            penalty = min(15.0, 5.0 * len(rep.failure_markers))
            bd["failure_markers_penalty"] = -penalty

    # Compiler-specific: primary artifact size (real compilation produces MB-sized .dxnn)
    if scenario == "compiler":
        size_mb = rep.primary_artifact_size_bytes / (1024 * 1024)
        if size_mb >= 1.0:
            bd["dxnn_realistic_size"] = 20.0
            score += 20.0
        elif size_mb > 0:
            bd["dxnn_tiny"] = 5.0
            score += 5.0

    # Timeout — informational only; do NOT penalize (per user guidance Q2)
    # Mark for flagging
    if rep.timeout_markers:
        rep.suspected_timeout = True
        bd["timeout_detected"] = 0.0  # informational

    rep.score = max(0.0, min(100.0, score))
    rep.score_breakdown = bd
    return rep
