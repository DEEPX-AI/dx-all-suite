"""Aggregate per-session evaluations into per-tool / per-round / per-scenario tables."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _is_env_failure(ev: "SessionEval") -> bool:
    """Thin wrapper around skip_analyzer.is_env_failure_eval.

    Avoids circular import by importing lazily.  Falls back to False on error.
    """
    try:
        from .skip_analyzer import is_env_failure_eval
        return is_env_failure_eval(ev)
    except Exception:
        return False


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
    # Runnability (parsed from runnability_report.md — 0 if not evaluated)
    runnability_score: float = 0.0
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
    runnability_pct: float = 0.0,
    has_runnability: bool = False,
) -> float:
    """Weighted overall:
      - 25% Compliance (HARD GATE checks — sentinel 포함)
      - 20% Quality (static syntax + anti-pattern detection)
      - 10% Verdict (artifact existence — 1차 산출물 PASS/FAIL)
      - 25% ExecutionTrace (실제 명령 실행 흔적: session.log + compile_out.log + 성공 마커)
      - 15% Runnability (end-user 실행 가능성 — LLM 판정)

    Sentinel (START/DONE)은 Compliance 체크 항목으로만 반영.
    별도 보너스 없음 (이전 +5% 보너스는 이중 반영이므로 제거).

    Verdict 는 파일 존재만 확인하므로 가중치를 낮추고, 실제 실행 증거(Execution)와
    end-user 관점의 실행 가능성(Runnability)에 더 높은 비중을 둠.

    Runnability 데이터가 없는 세션은 기존 4-factor 가중치를 비례 배분하여 backward
    compatible 하게 처리.

    pytest 의 round-level exit code 는 미포함 (시나리오 분해 불가; 정보용 컬럼만).
    """
    if has_runnability:
        return min(100.0, (0.25 * comp_pct + 0.20 * qual_pct + 0.10 * verdict_pct
                           + 0.25 * execution_pct + 0.15 * runnability_pct))
    else:
        # No runnability data — redistribute 15% proportionally among the other 4
        # Effective weights: 31.25%C + 25%Q + 12.5%V + 31.25%E (sum = 100%)
        return min(100.0, (0.25 / 0.80 * comp_pct + 0.20 / 0.80 * qual_pct
                           + 0.10 / 0.80 * verdict_pct + 0.25 / 0.80 * execution_pct))


def _stdev(values: List[float]) -> float:
    """Population stdev (or 0 if <2 values)."""
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return var ** 0.5


def aggregate_per_tool(evals: List[SessionEval]) -> Dict[str, Dict[str, float]]:
    """Compute averages + stdev per tool. Stdev = consistency indicator (lower = more consistent).

    Environment failure sessions (rate limit, TLS error, CLI crash) are excluded
    from score averages but counted separately as 'env_failures'.
    """
    by_tool: Dict[str, List[SessionEval]] = {}
    for e in evals:
        by_tool.setdefault(e.tool, []).append(e)
    out: Dict[str, Dict[str, float]] = {}
    for tool, lst in by_tool.items():
        n_total = len(lst)
        if n_total == 0:
            continue
        env_fails = [e for e in lst if _is_env_failure(e)]
        scored = [e for e in lst if not _is_env_failure(e)]
        n = len(scored) or 1  # avoid division by zero
        overalls = [e.overall_score for e in scored]
        durations = [e.duration_sec for e in scored if e.duration_sec]
        out[tool] = {
            "sessions": n_total,
            "sessions_scored": len(scored),
            "env_failures": len(env_fails),
            "avg_compliance_pct": sum(e.compliance_score_pct for e in scored) / n,
            "avg_quality_score": sum(e.quality_score for e in scored) / n,
            "avg_overall_score": sum(overalls) / n,
            "stdev_overall_score": _stdev(overalls),
            "avg_duration_sec": sum(durations) / max(1, len(durations)),
            "stdev_duration_sec": _stdev(durations),
            "pct_with_start_sentinel": 100.0 * sum(1 for e in scored if e.has_start) / n,
            "pct_with_done_sentinel": 100.0 * sum(1 for e in scored if e.has_done) / n,
            "pct_exit_0": 100.0 * sum(1 for e in lst if e.exit_status == 0) / n_total,
            "avg_tool_calls": sum(e.tool_call_count for e in scored) / n,
            "avg_python_loc": sum(e.python_loc for e in scored) / n,
        }
    return out


def aggregate_per_round_tool(evals: List[SessionEval]) -> Dict[tuple, Dict[str, float]]:
    """key = (round_index, tool) → metrics. Env failures excluded from averages."""
    by_key: Dict[tuple, List[SessionEval]] = {}
    for e in evals:
        by_key.setdefault((e.round_index, e.tool), []).append(e)
    out: Dict[tuple, Dict[str, float]] = {}
    for key, lst in by_key.items():
        n_total = len(lst)
        scored = [e for e in lst if not _is_env_failure(e)]
        n = len(scored) or 1
        out[key] = {
            "sessions": n_total,
            "sessions_scored": len(scored),
            "env_failures": n_total - len(scored),
            "avg_compliance_pct": sum(e.compliance_score_pct for e in scored) / n,
            "avg_quality_score": sum(e.quality_score for e in scored) / n,
            "avg_overall_score": sum(e.overall_score for e in scored) / n,
            "avg_duration_sec":
                sum(e.duration_sec or 0 for e in scored if e.duration_sec) /
                max(1, sum(1 for e in scored if e.duration_sec)),
            "pct_with_start_sentinel": 100.0 * sum(1 for e in scored if e.has_start) / n,
            "pct_with_done_sentinel": 100.0 * sum(1 for e in scored if e.has_done) / n,
        }
    return out


def aggregate_per_scenario_tool(evals: List[SessionEval]) -> Dict[tuple, Dict[str, float]]:
    """key = (scenario, tool) → detailed metrics. Env failures excluded from averages."""
    by_key: Dict[tuple, List[SessionEval]] = {}
    for e in evals:
        by_key.setdefault((e.scenario, e.tool), []).append(e)
    out: Dict[tuple, Dict[str, float]] = {}
    for key, lst in by_key.items():
        n_total = len(lst)
        scored = [e for e in lst if not _is_env_failure(e)]
        n = len(scored) or 1
        n_with_dur = max(1, sum(1 for e in scored if e.duration_sec))
        out[key] = {
            "sessions": n_total,
            "sessions_scored": len(scored),
            "env_failures": n_total - len(scored),
            "avg_compliance_pct": sum(e.compliance_score_pct for e in scored) / n,
            "avg_quality_score": sum(e.quality_score for e in scored) / n,
            "avg_verdict_score": sum(e.verdict_score for e in scored) / n,
            "avg_overall_score": sum(e.overall_score for e in scored) / n,
            "avg_duration_sec": sum(e.duration_sec or 0 for e in scored if e.duration_sec) / n_with_dur,
            "pct_pass": 100.0 * sum(1 for e in scored if e.verdict == "PASS") / n,
            "pct_partial": 100.0 * sum(1 for e in scored if e.verdict == "PARTIAL") / n,
            "pct_fail": 100.0 * sum(1 for e in scored if e.verdict == "FAIL") / n,
            "avg_tool_calls": sum(e.tool_call_count for e in scored) / n,
            "avg_python_loc": sum(e.python_loc for e in scored) / n,
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
