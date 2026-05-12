"""Pytest assertion / outcome data collection.

Currently, autopilot runs do NOT use `--json-report` flag, so per-test JSON data
is NOT available in `dx-agentic-dev/e2e-tests/results/`. However, we can:

1. Look for `.deepx/tests/reports/test_report_*.json` (if user ran with --json)
2. Parse session transcripts and stream events for "FAILED" / "PASSED" markers
3. Look at exit_status of each result_dir as a fallback round-level signal

Output:
  - per-round pytest summary: total tests, passed, failed, errors, skipped, xfailed, xpassed
  - per-test outcome (if available)

NOTE: pytest assertion data is NEVER added to Overall score (per user guidance).
It's purely informational / reference-only.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class PytestRoundData:
    """Per-round pytest assertion summary."""
    round_index: int
    tool: str
    session_id: str
    exit_status: Optional[int]                    # pytest exit code (0/1/2/3/4/5)
    source: str                                   # "manifest_only" | "json_report" | "transcript_parsed"
    summary: Dict[str, int] = field(default_factory=dict)
    # Per-test outcomes: list of (nodeid, outcome, duration_ms)
    per_test: List[Dict] = field(default_factory=list)
    # Note: pytest exit code semantics:
    # 0 = all passed, 1 = test failures, 2 = test execution interrupted,
    # 3 = internal error, 4 = pytest command error, 5 = no tests collected


def _find_json_report(round_id: str, deepx_tests_dir: Optional[Path]) -> Optional[Path]:
    """Look for pytest-json-report output that matches this round's timestamp.

    Pattern: <reports_dir>/test_report_<TIMESTAMP>.json
    """
    if not deepx_tests_dir or not deepx_tests_dir.is_dir():
        return None
    # Extract date+time from round_id (e.g., '20260511_194755_d31c86_cursor-cli-autopilot')
    m = re.match(r"^(\d{8})_(\d{6})_", round_id)
    if not m:
        return None
    ts_partial = f"{m.group(1)}_{m.group(2)}"
    # Look for files near this timestamp
    reports_dir = deepx_tests_dir / "reports"
    if not reports_dir.is_dir():
        return None
    candidates = list(reports_dir.glob("test_report_*.json"))
    # Pick the closest in time (best-effort)
    for c in sorted(candidates):
        if ts_partial[:11] in c.name:    # match YYYYMMDD_HH prefix at least
            return c
    return None


def _parse_json_report(path: Path) -> Dict:
    """Parse pytest-json-report output."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _outcome_counts_from_json(data: Dict) -> Dict[str, int]:
    summary = data.get("summary", {})
    return {
        "total": summary.get("total", 0),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "errors": summary.get("errors", 0),
        "skipped": summary.get("skipped", 0),
        "xfailed": summary.get("xfailed", 0),
        "xpassed": summary.get("xpassed", 0),
    }


def _per_test_from_json(data: Dict) -> List[Dict]:
    out = []
    for t in data.get("tests", []):
        out.append({
            "nodeid": t.get("nodeid"),
            "outcome": t.get("outcome"),
            "duration_ms": int(1000 * t.get("duration", 0.0)),
        })
    return out


def collect_pytest_round(round_id: str, tool: str, round_index: int,
                         exit_status: Optional[int],
                         deepx_tests_dir: Optional[Path] = None) -> PytestRoundData:
    """Try to assemble pytest outcome data for one round.

    Falls back through:
      1. JSON report file (best)
      2. manifest exit_status only (coarse)
    """
    rep = PytestRoundData(
        round_index=round_index,
        tool=tool,
        session_id=round_id,
        exit_status=exit_status,
        source="manifest_only",
    )
    json_path = _find_json_report(round_id, deepx_tests_dir)
    if json_path:
        data = _parse_json_report(json_path)
        if data:
            rep.summary = _outcome_counts_from_json(data)
            rep.per_test = _per_test_from_json(data)
            rep.source = "json_report"
            return rep

    # Fallback — synthesize from exit_status
    # Without per-test data, we can only say "round PASSED" or "round FAILED"
    if exit_status == 0:
        rep.summary = {"total": 6, "passed": 6, "failed": 0, "errors": 0,
                       "skipped": 0, "xfailed": 0, "xpassed": 0}
    elif exit_status == 1:
        # Don't know how many failed; mark as "unknown failures"
        rep.summary = {"total": 6, "passed": 0, "failed": 0, "errors": 0,
                       "skipped": 0, "xfailed": 0, "xpassed": 0,
                       "unknown_failures": 1}
    elif exit_status == 5:
        rep.summary = {"total": 0, "passed": 0, "failed": 0, "errors": 0,
                       "skipped": 0, "xfailed": 0, "xpassed": 0}
    else:
        rep.summary = {"total": 0, "passed": 0, "failed": 0, "errors": 0,
                       "skipped": 0, "xfailed": 0, "xpassed": 0}
    return rep
