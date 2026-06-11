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
    # Run-id grouping (propagated from ResultDir.run_id)
    run_id: str = "legacy"
    # Stable copyable symlink paths under results/<run_id>/<session_id>/.
    # result_session_dir   = results/<run_id>/<session_id>/                 (round-level)
    # result_scenario_dir  = results/<run_id>/<session_id>/<artifact_key>/  (scenario-level symlink)
    # Empty string for legacy analysis.json files written before this field existed.
    result_session_dir: str = ""
    result_scenario_dir: str = ""
    # Thinking mode + canonical backend model — used by §4 group comparison
    # tables and the hypothesis verification prompt to slice (NT vs TH) and
    # (sonnet vs opus). "NA" for cursor-cli (Composer 2.5 has no thinking
    # variant); empty string for legacy manifests without metadata.
    mode: str = ""
    backend_model: str = ""
    # Environment-failure signature detected in the transcript (PR2):
    # "cert" | "rate-limit" | "model-refresh-timeout" | "" (none). When set,
    # the session is an env failure regardless of duration heuristics — see
    # lib/env_failure.py.
    env_failure_signature: str = ""
    # T4 no-DONE cause classification: "" | env-<sig> | sentinel-omission | incomplete-planstop
    no_done_cause: str = ""
    # Token usage (now extracted per-tool)
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    reasoning_tokens: int = 0
    # Cost / billing
    premium_requests: int = 0           # Copilot CLI only (actual from stream)
    estimated_premium_requests: float = 0.0  # Primary PR estimate used for USD calc (method 1 → 2 priority)
    # PR estimation methods kept side-by-side for §6.1 transparency
    pr_observed: float = 0.0            # method 0 — totalPremiumRequests (copilot-cli only)
    pr_by_tool_call: float = 0.0        # method 1 — tool_call × 0.741 (calibrated, primary)
    pr_by_token_ratio: float = 0.0      # method 2 — (input+output) / tokens_per_premium (fallback)
    user_turn_count: int = 0            # Informational metadata (not used for PR estimation in agent-driven loops)
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


def classify_no_done_cause(*, has_done: bool, env_failure_signature: str,
                           has_output_dirs: bool, execution_score: float) -> str:
    """Classify WHY a session has no DONE sentinel (empty when it has one).

    Priority: env signature (rate-limit/cert/model-refresh) > sentinel-omission
    (real artifacts + execution evidence) > incomplete-planstop (ran but no
    verifiable deliverable). The signature path prefixes with ``env-`` so the
    report can group all env causes together (env-rate-limit, env-cert, ...).
    """
    if has_done:
        return ""
    if env_failure_signature:
        return f"env-{env_failure_signature}"
    if has_output_dirs and execution_score > 0:
        return "sentinel-omission"
    return "incomplete-planstop"


# Scenario-aware Overall weights (v2.1). Each row sums to 1.00.
#
# Rationale:
#   compiler / suite      → ExecutionTrace is the dominant evidence channel
#                           (.dxnn artifact + chain validation), so it carries
#                           a higher weight (35%) than the default.
#   dx_app / dx_stream / dx_stream_cascaded
#                         → code-generation scenarios. v2.0 had Quality=25%
#                           assuming static syntax checks would discriminate,
#                           but the first batch showed inter-tool Quality
#                           spread was only 2.2 pts (σ 0.8) — almost no
#                           discrimination — while Runnability spread was
#                           16.7 pts (σ 6.7). v2.1 reallocates 5pt from
#                           Quality (25→20) to Runnability (20→25) so the
#                           Overall score better reflects observed end-user
#                           runnability differences between tools.
#   runtime               → multi-domain routing; Runnability already 25%.
#   default (unknown)     → conservative original 30/20/30/20.
COMPOSITE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "compiler":           {"comp": 0.30, "qual": 0.15, "exec": 0.35, "runn": 0.20},
    "dx_app":             {"comp": 0.30, "qual": 0.20, "exec": 0.25, "runn": 0.25},
    "dx_stream":          {"comp": 0.30, "qual": 0.20, "exec": 0.25, "runn": 0.25},
    "dx_stream_cascaded": {"comp": 0.30, "qual": 0.20, "exec": 0.25, "runn": 0.25},
    "runtime":            {"comp": 0.30, "qual": 0.20, "exec": 0.25, "runn": 0.25},
    "suite":              {"comp": 0.30, "qual": 0.15, "exec": 0.35, "runn": 0.20},
    # legacy fallback (used when scenario is None / unknown)
    "_default":           {"comp": 0.30, "qual": 0.20, "exec": 0.30, "runn": 0.20},
}


def composite_score(
    comp_pct: float,
    qual_pct: float,
    verdict_pct: float,
    execution_pct: float,
    has_start: bool,
    has_done: bool,
    runnability_pct: float = 0.0,
    has_runnability: bool = False,
    scenario: Optional[str] = None,
) -> float:
    """Weighted overall (100-point scale), scenario-aware weights (v2).

    Per-scenario weights are looked up in COMPOSITE_WEIGHTS. When `scenario`
    is None or unknown, the legacy 30/20/30/20 weights are used so callers that
    haven't been updated yet still get sensible numbers.

    Verdict (산출물 존재 여부)는 Compliance mandatory_deliverables와 중복이므로
    별도 가중치 없이 정보용으로만 표시. verdict_pct 인자는 backward compat 유지.

    Runnability 데이터가 없는 세션은 runn 가중치를 나머지 3-factor에 비례 재분배.

    pytest 의 round-level exit code 는 미포함 (시나리오 분해 불가; 정보용 컬럼만).
    """
    w = COMPOSITE_WEIGHTS.get(scenario or "_default", COMPOSITE_WEIGHTS["_default"])
    if has_runnability:
        return min(100.0,
                   w["comp"] * comp_pct
                   + w["qual"] * qual_pct
                   + w["exec"] * execution_pct
                   + w["runn"] * runnability_pct)
    # No runnability → redistribute runn weight proportionally across the other 3
    remaining = w["comp"] + w["qual"] + w["exec"]
    if remaining <= 0:
        return 0.0
    return min(100.0,
               (w["comp"] / remaining) * comp_pct
               + (w["qual"] / remaining) * qual_pct
               + (w["exec"] / remaining) * execution_pct)


def _stdev(values: List[float]) -> float:
    """Population stdev (or 0 if <2 values)."""
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return var ** 0.5


def canonical_backend_model(tool: str, intended_models: dict) -> str:
    """Normalize manifest.intended_models → canonical tag for grouping.

    Returns one of:
      - "sonnet-4.6", "opus-4.6", "opus-4.8"  (Anthropic Claude variants)
      - "gpt-5.3-codex", "gpt-5.5"             (OpenAI variants)
      - "auto"                                  (cursor-cli Composer 2.5 fallback)
      - ""                                      (manifest has no model — pre-backfill data)

    The same canonical value covers both naming variants used across tools
    (e.g. ``claude-sonnet-4-6`` ≡ ``claude-sonnet-4.6`` ≡ ``github-copilot/claude-sonnet-4.6``).
    Opus variants are disambiguated by minor version: "4.8"/"4-8" → opus-4.8,
    otherwise → opus-4.6 (legacy default for pre-opus-4.8 manifests).
    """
    if not intended_models:
        return ""
    # Pick the most likely source key for this tool. The dict usually has one
    # entry but may contain multiple env vars — search by value content.
    raw = ""
    for v in intended_models.values():
        if v:
            raw = str(v).lower()
            break
    if not raw:
        return ""
    if "opus" in raw:
        if "4.8" in raw or "4-8" in raw:
            return "opus-4.8"
        return "opus-4.6"
    if "sonnet" in raw:
        return "sonnet-4.6"
    if "gpt-5.3-codex" in raw or "gpt-5-3-codex" in raw:
        return "gpt-5.3-codex"
    if "gpt-5.5" in raw or "gpt-5-5" in raw:
        return "gpt-5.5"
    if "auto" in raw:
        return "auto"
    return raw


# Group definitions for §3.X comparison tables and §7 hypothesis verification.
# Each group is a (mode, backend_model_family) tuple — sessions in the same
# group are averaged together per tool/scenario.
#
# Comparison axes used in the report:
#   §3.5  thinking effect = TH_sonnet   vs  NT_sonnet   (model fixed, mode differs)
#   §3.6  model tier      = TH_opus46   vs  TH_sonnet   (mode fixed, model differs)
#         opus-4.8 axis   = NT_opus46 vs NT_opus48 / NT_opus48 vs TH_opus48 / TH_opus46 vs TH_opus48
#   §3.7  combined        = TH_opus46   vs  NT_sonnet   (both differ — reference)
# cursor-cli is excluded automatically because its sessions land in NA_auto.
#
# Opus 4.6 and Opus 4.8 are first-class separate canonical models. The
# legacy alias "TH_opus" maps to TH_opus46 below for backward compatibility
# with reports generated before opus-4.8 evaluation existed.
GROUP_KEYS: Dict[str, callable] = {
    "NT_sonnet":     lambda e: e.mode == "NT" and (e.backend_model or "") == "sonnet-4.6",
    "TH_sonnet":     lambda e: e.mode == "TH" and (e.backend_model or "") == "sonnet-4.6",
    "NT_opus46":     lambda e: e.mode == "NT" and (e.backend_model or "") == "opus-4.6",
    "TH_opus46":     lambda e: e.mode == "TH" and (e.backend_model or "") == "opus-4.6",
    "NT_opus48":     lambda e: e.mode == "NT" and (e.backend_model or "") == "opus-4.8",
    "TH_opus48":     lambda e: e.mode == "TH" and (e.backend_model or "") == "opus-4.8",
    "NT_gpt53codex": lambda e: e.mode == "NT" and (e.backend_model or "") == "gpt-5.3-codex",
    "TH_gpt53codex": lambda e: e.mode == "TH" and (e.backend_model or "") == "gpt-5.3-codex",
    "TH_gpt55":      lambda e: e.mode == "TH" and (e.backend_model or "") == "gpt-5.5",
    "NA_auto":       lambda e: e.mode == "NA",  # cursor-cli
}


def aggregate_per_group_tool(
    evals: List[SessionEval],
) -> Dict[tuple, Dict[str, float]]:
    """key = (group, tool) → per-(group, tool) average metrics.

    Used by §4 comparison tables to compute Δ (TH−NT, opus−sonnet) per tool.
    Environment-failure sessions are excluded from averages.
    """
    by_key: Dict[tuple, List[SessionEval]] = {}
    for e in evals:
        if _is_env_failure(e):
            continue
        for group_name, predicate in GROUP_KEYS.items():
            try:
                if predicate(e):
                    by_key.setdefault((group_name, e.tool), []).append(e)
                    break
            except Exception:
                continue
    out: Dict[tuple, Dict[str, float]] = {}
    for key, lst in by_key.items():
        n = len(lst) or 1
        out[key] = {
            "sessions": len(lst),
            "avg_overall_score":    sum(e.overall_score for e in lst) / n,
            "avg_compliance_pct":   sum(e.compliance_score_pct for e in lst) / n,
            "avg_quality_score":    sum(e.quality_score for e in lst) / n,
            "avg_execution_score":  sum(e.execution_score for e in lst) / n,
            "avg_runnability_score": sum(e.runnability_score for e in lst) / n,
            "avg_duration_sec":
                sum(e.duration_sec or 0 for e in lst if e.duration_sec) /
                max(1, sum(1 for e in lst if e.duration_sec)),
        }
    return out


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
            "avg_execution_score": sum(e.execution_score for e in scored) / n,
            "avg_runnability_score": sum(e.runnability_score for e in scored) / n,
            # PR estimation methods — averaged for §6.1 cross-method comparison
            "avg_pr_observed": sum(e.pr_observed for e in scored) / n,
            "avg_pr_by_tool_call": sum(e.pr_by_tool_call for e in scored) / n,
            "avg_pr_by_token_ratio": sum(e.pr_by_token_ratio for e in scored) / n,
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
            "avg_execution_score": sum(e.execution_score for e in scored) / n,
            "avg_runnability_score": sum(e.runnability_score for e in scored) / n,
            # None when all sessions are env-failures (no scored data → gap in trend chart)
            "avg_overall_score": (sum(e.overall_score for e in scored) / n) if scored else None,
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


def build_study_profile(evals: List[SessionEval]) -> Dict[str, object]:
    """Return a JSON-serialisable profile describing the actual experiment.

    The analyzer originally hardcoded a "5 tools × 3 groups × 5 rounds"
    layout, which breaks for single-tool sweeps or opus-4.8 evaluations.
    This helper inspects the loaded evals and returns the *real* shape so
    the hypothesis prompt and the experiment-conditions section can adapt
    to whichever subset was actually run.
    """
    tools = sorted({e.tool for e in evals if e.tool})
    run_ids = sorted({e.run_id for e in evals if e.run_id})
    scenarios = sorted({e.scenario for e in evals if e.scenario})
    rounds = sorted({e.round_index for e in evals if e.round_index})
    thinking_modes = sorted({e.mode for e in evals if e.mode})
    backend_models = sorted({e.backend_model for e in evals if e.backend_model})

    # Discovered groups (only those with at least one matching session).
    groups: Dict[str, Dict[str, object]] = {}
    for group_name, predicate in GROUP_KEYS.items():
        members = [e for e in evals if predicate(e)]
        if not members:
            continue
        groups[group_name] = {
            "session_count": len(members),
            "rounds": sorted({e.round_index for e in members}),
            "tools": sorted({e.tool for e in members}),
            "run_ids": sorted({e.run_id for e in members}),
            "thinking_mode": next(iter({e.mode for e in members if e.mode}), ""),
            "backend_model": next(iter({e.backend_model for e in members if e.backend_model}), ""),
        }

    # (run_id, tool) → mode/backend_model pairing for run-level summary
    runs: List[Dict[str, object]] = []
    seen: set = set()
    for e in evals:
        key = (e.run_id, e.tool, e.mode, e.backend_model)
        if key in seen:
            continue
        seen.add(key)
        runs.append({
            "run_id": e.run_id,
            "tool": e.tool,
            "mode": e.mode,
            "backend_model": e.backend_model,
            "round_count": sum(
                1 for rr in {x.round_index for x in evals
                             if x.run_id == e.run_id and x.tool == e.tool}
            ),
        })

    return {
        "tools": tools,
        "run_ids": run_ids,
        "scenarios": scenarios,
        "rounds": rounds,
        "thinking_modes": thinking_modes,
        "backend_models": backend_models,
        "groups": groups,
        "runs": runs,
        "session_count": len(evals),
        # Quick flags so callers can branch without recomputing
        "is_single_tool": len(tools) == 1,
        "has_thinking_axis": len(thinking_modes) > 1,
        "has_model_axis": len(backend_models) > 1,
    }
