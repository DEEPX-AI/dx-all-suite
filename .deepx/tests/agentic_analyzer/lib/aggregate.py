"""Aggregate per-session evaluations into per-tool / per-round / per-scenario tables."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SessionEval:
    """Combined evaluation row for one scenario session."""
    round_index: int
    tool: str
    scenario: str
    model: str
    session_id: str
    output_dirs: List[str]
    exit_status: Optional[int]              # pytest round-level exit code (round-wide)
    duration_sec: Optional[float]
    has_start: bool
    has_done: bool
    tool_call_count: int
    transcript_length: int
    # Token usage (now extracted per-tool)
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    reasoning_tokens: int = 0
    # Cost / billing
    premium_requests: int = 0           # Copilot CLI only (actual from stream)
    estimated_premium_requests: float = 0.0  # OpenCode: reverse-engineered from token ratio
    cost_units: float = 0.0             # Copilot: requests.cost, OpenCode: part.cost sum
    estimated_usd: float = 0.0          # Computed from pricing config (informational)
    cost_basis: str = "unknown"         # Which pricing rule was applied
    cost_note: str = ""                 # Human-readable explanation
    # Code metrics
    python_loc: int = 0
    bash_loc: int = 0
    json_loc: int = 0
    code_files: int = 0
    # Functional verdict (inferred from artifacts)
    verdict: str = "UNKNOWN"               # PASS / PARTIAL / FAIL / UNKNOWN
    verdict_reason: str = ""
    verdict_score: float = 0.0             # 0-100
    # Execution trace evidence
    execution_score: float = 0.0           # 0-100 — how well agent actually ran commands
    execution_breakdown: Dict[str, float] = field(default_factory=dict)
    suspected_timeout: bool = False        # informational only — does not affect Overall
    # Compliance breakdown
    compliance_score_pct: float = 0.0
    compliance_passed: int = 0
    compliance_total: int = 0
    compliance_checks: Dict[str, bool] = field(default_factory=dict)
    # Quality breakdown
    quality_score: float = 0.0
    syntax_pct: float = 0.0
    python_files: int = 0
    placeholder_hits: int = 0
    direct_engine_use: int = 0
    # Composite
    overall_score: float = 0.0
    notes: List[str] = field(default_factory=list)


def composite_score(
    comp_pct: float,
    qual_pct: float,
    verdict_pct: float,
    execution_pct: float,
    has_start: bool,
    has_done: bool,
) -> float:
    """Weighted overall:
      - 30% Compliance (HARD GATE checks)
      - 25% Quality (static syntax + anti-pattern detection)
      - 25% Verdict (artifact existence — 1차 산출물 PASS/FAIL)
      - 15% ExecutionTrace (실제 명령 실행 흔적: session.log + compile_out.log + 성공 마커)
      - 5% sentinel bonus (START/DONE)

    pytest 의 round-level exit code 는 미포함 (시나리오 분해 불가; 정보용 컬럼만).
    """
    base = 0.30 * comp_pct + 0.25 * qual_pct + 0.25 * verdict_pct + 0.15 * execution_pct
    sentinel_bonus = 2.5 if has_start else 0.0
    sentinel_bonus += 2.5 if has_done else 0.0
    return min(100.0, base + sentinel_bonus)


def _stdev(values: List[float]) -> float:
    """Population stdev (or 0 if <2 values)."""
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return var ** 0.5


def aggregate_per_tool(evals: List[SessionEval]) -> Dict[str, Dict[str, float]]:
    """Compute averages + stdev per tool. Stdev = consistency indicator (lower = more consistent)."""
    by_tool: Dict[str, List[SessionEval]] = {}
    for e in evals:
        by_tool.setdefault(e.tool, []).append(e)
    out: Dict[str, Dict[str, float]] = {}
    for tool, lst in by_tool.items():
        n = len(lst)
        if n == 0:
            continue
        overalls = [e.overall_score for e in lst]
        durations = [e.duration_sec for e in lst if e.duration_sec]
        out[tool] = {
            "sessions": n,
            "avg_compliance_pct": sum(e.compliance_score_pct for e in lst) / n,
            "avg_quality_score": sum(e.quality_score for e in lst) / n,
            "avg_overall_score": sum(overalls) / n,
            "stdev_overall_score": _stdev(overalls),
            "avg_duration_sec": sum(durations) / max(1, len(durations)),
            "stdev_duration_sec": _stdev(durations),
            "pct_with_start_sentinel": 100.0 * sum(1 for e in lst if e.has_start) / n,
            "pct_with_done_sentinel": 100.0 * sum(1 for e in lst if e.has_done) / n,
            "pct_exit_0": 100.0 * sum(1 for e in lst if e.exit_status == 0) / n,
            "avg_tool_calls": sum(e.tool_call_count for e in lst) / n,
            "avg_python_loc": sum(e.python_loc for e in lst) / n,
        }
    return out


def aggregate_per_round_tool(evals: List[SessionEval]) -> Dict[tuple, Dict[str, float]]:
    """key = (round_index, tool) → metrics."""
    by_key: Dict[tuple, List[SessionEval]] = {}
    for e in evals:
        by_key.setdefault((e.round_index, e.tool), []).append(e)
    out: Dict[tuple, Dict[str, float]] = {}
    for key, lst in by_key.items():
        n = len(lst)
        out[key] = {
            "sessions": n,
            "avg_compliance_pct": sum(e.compliance_score_pct for e in lst) / n,
            "avg_quality_score": sum(e.quality_score for e in lst) / n,
            "avg_overall_score": sum(e.overall_score for e in lst) / n,
            "avg_duration_sec":
                sum(e.duration_sec or 0 for e in lst if e.duration_sec) /
                max(1, sum(1 for e in lst if e.duration_sec)),
            "pct_with_start_sentinel": 100.0 * sum(1 for e in lst if e.has_start) / n,
            "pct_with_done_sentinel": 100.0 * sum(1 for e in lst if e.has_done) / n,
        }
    return out


def aggregate_per_scenario_tool(evals: List[SessionEval]) -> Dict[tuple, Dict[str, float]]:
    """key = (scenario, tool) → detailed metrics."""
    by_key: Dict[tuple, List[SessionEval]] = {}
    for e in evals:
        by_key.setdefault((e.scenario, e.tool), []).append(e)
    out: Dict[tuple, Dict[str, float]] = {}
    for key, lst in by_key.items():
        n = len(lst)
        n_with_dur = max(1, sum(1 for e in lst if e.duration_sec))
        out[key] = {
            "sessions": n,
            "avg_compliance_pct": sum(e.compliance_score_pct for e in lst) / n,
            "avg_quality_score": sum(e.quality_score for e in lst) / n,
            "avg_verdict_score": sum(e.verdict_score for e in lst) / n,
            "avg_overall_score": sum(e.overall_score for e in lst) / n,
            "avg_duration_sec": sum(e.duration_sec or 0 for e in lst if e.duration_sec) / n_with_dur,
            "pct_pass": 100.0 * sum(1 for e in lst if e.verdict == "PASS") / n,
            "pct_partial": 100.0 * sum(1 for e in lst if e.verdict == "PARTIAL") / n,
            "pct_fail": 100.0 * sum(1 for e in lst if e.verdict == "FAIL") / n,
            "avg_tool_calls": sum(e.tool_call_count for e in lst) / n,
            "avg_python_loc": sum(e.python_loc for e in lst) / n,
        }
    return out


def aggregate_per_round_scenario_tool(evals: List[SessionEval]) -> Dict[tuple, Dict[str, float]]:
    """key = (round, scenario, tool) — most granular view."""
    by_key: Dict[tuple, List[SessionEval]] = {}
    for e in evals:
        by_key.setdefault((e.round_index, e.scenario, e.tool), []).append(e)
    out: Dict[tuple, Dict[str, float]] = {}
    for key, lst in by_key.items():
        # Should be 1 session per (round, scenario, tool) usually
        e = lst[0]
        out[key] = {
            "verdict": e.verdict,
            "verdict_reason": e.verdict_reason,
            "compliance_pct": e.compliance_score_pct,
            "quality_score": e.quality_score,
            "overall_score": e.overall_score,
            "duration_sec": e.duration_sec or 0,
            "tool_calls": e.tool_call_count,
            "python_loc": e.python_loc,
        }
    return out
