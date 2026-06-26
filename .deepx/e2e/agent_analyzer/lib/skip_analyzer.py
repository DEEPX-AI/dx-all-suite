"""Categorize sessions skipped by the runnability evaluator.

A session is "skipped" when it has no output_dirs in analysis.json — meaning
the original autopilot test produced zero artifacts. This module classifies
the underlying cause from observable signals (duration, tool, scenario).

Categories (heuristic; first match wins):
  - anthropic_rate_limit  : claude-code + duration < 5s  → API quota rejection
                            (Anthropic 5h rolling cap)
  - pytest_timeout        : duration >= 1800s (30min)    → pytest test timeout
  - subprocess_crash      : 5s <= duration < 300s        → agent process died
  - agent_self_abort      : 300s <= duration < 900s      → agent gave up
  - other                 : everything else

Environment failure categories (false alarms — excluded from scoring):
  anthropic_rate_limit, subprocess_crash are classified as environment failures
  because they reflect infrastructure/network issues, not tool capability.
"""
from __future__ import annotations
from collections import defaultdict
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .aggregate import SessionEval


CATEGORY_LABELS = {
    "anthropic_rate_limit": "Anthropic 5h rate limit (claude-code)",
    "pytest_timeout":       "pytest safety-net timeout (4h)",
    "subprocess_crash":     "Subprocess crash (early termination)",
    "agent_self_abort":     "Agent self-abort (mid-run termination)",
    "other":                "Other / Unknown",
}

# Categories that represent environment/infrastructure failures, not tool capability.
# Sessions in these categories are excluded from score averages (false alarms).
ENV_FAILURE_CATEGORIES = frozenset({
    "anthropic_rate_limit",
    "subprocess_crash",
})


def _classify(session: Dict[str, Any]) -> str:
    """Return one of the CATEGORY_LABELS keys for this skipped session."""
    tool = session.get("tool") or ""
    duration = session.get("duration_sec") or 0.0
    if tool == "claude-code" and duration < 5:
        return "anthropic_rate_limit"
    if duration >= 1800:
        return "pytest_timeout"
    if 5 <= duration < 300:
        return "subprocess_crash"
    if 300 <= duration < 900:
        return "agent_self_abort"
    return "other"


def is_env_failure_eval(ev: "SessionEval") -> bool:
    """Check if a SessionEval represents an environment failure (false alarm).

    Delegates to the shared ``lib.env_failure.is_env_failure`` decision so the
    analyzer and the runner repair (goalB_repair) classify env failures
    identically. The signals are pulled off the SessionEval row:

    (0) SIGNATURE — explicit cert / rate-limit / model-refresh signature
        scanned from the transcript (``ev.env_failure_signature``). Highest
        priority: a cert/SSL error, Anthropic session-limit, or codex
        model-refresh timeout (with no real work) is an env failure even when
        partial tokens / (derived) artifacts exist.

    (B) Incomplete session — has_start + no DONE + non-zero round exit →
        agent terminated mid-execution (Bash hang, CLI crash, SIGKILL).

    (A) Pre-execution infra failure — output_tokens==0 AND no START → API
        rate limit / TLS error before any LLM call. Fires even when
        output_dirs is True (the suite-fallback derives dirs from compiler+
        dx_app, which must not mask a session that produced zero tokens).

    Sessions WITH a DONE sentinel, or with real artifacts + has_start but
    no signature, are NOT env failures (artifact-collection bug, not infra).
    """
    from . import env_failure as ef

    return ef.is_env_failure(
        env_signature=getattr(ev, "env_failure_signature", "") or "",
        has_start=ev.has_start,
        has_done=ev.has_done,
        exit_status=ev.exit_status,
        has_output_dirs=bool(ev.output_dirs),
        output_tokens=ev.output_tokens,
        tool_call_count=ev.tool_call_count,
    )


def categorize_skipped_sessions(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Identify skipped sessions (no output_dirs) and group by inferred cause.

    Returns
    -------
    dict with keys:
        total_sessions  : int — total sessions seen
        skipped_count   : int — number with empty output_dirs
        by_category     : dict[str, list[dict]] keyed by CATEGORY_LABELS key.
                          Each entry is {tool, round, scenario, duration_sec}.
        category_counts : dict[str, int] for quick summary.
    """
    skipped: List[Dict[str, Any]] = [
        s for s in sessions if not s.get("output_dirs")
    ]
    by_category: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for s in skipped:
        cat = _classify(s)
        by_category[cat].append({
            "tool":          s.get("tool"),
            "round":         s.get("round_index"),
            "scenario":      s.get("scenario"),
            "duration_sec":  s.get("duration_sec") or 0.0,
        })

    category_counts = {k: len(v) for k, v in by_category.items()}
    return {
        "total_sessions":  len(sessions),
        "skipped_count":   len(skipped),
        "by_category":     dict(by_category),
        "category_counts": category_counts,
    }


def render_skip_summary_markdown(skip_report: Dict[str, Any],
                                  *, heading_level: int = 2) -> str:
    """Render the categorization as a Markdown section."""
    if skip_report["skipped_count"] == 0:
        h = "#" * heading_level
        return f"{h} Skipped 세션 분류\n\n_없음 (전체 세션이 평가됨)_\n"

    h = "#" * heading_level
    lines: List[str] = []
    lines.append(f"{h} Skipped 세션 분류 "
                 f"({skip_report['skipped_count']}/{skip_report['total_sessions']})")
    lines.append("")
    lines.append("| 원인 | 건수 | 영향 도구·라운드·시나리오 |")
    lines.append("|------|----:|-----------------------|")
    # Stable iteration order: as listed in CATEGORY_LABELS
    for key, label in CATEGORY_LABELS.items():
        entries = skip_report["by_category"].get(key, [])
        if not entries:
            continue
        # Compact representation of affected sessions
        bits = []
        for e in entries[:6]:
            bits.append(f"{e['tool']} R{e['round']} {e['scenario']} ({e['duration_sec']:.0f}s)")
        affected = "; ".join(bits)
        if len(entries) > 6:
            affected += f"; … (+{len(entries) - 6})"
        lines.append(f"| {label} | {len(entries)} | {affected} |")
    lines.append("")
    lines.append("> 분류는 휴리스틱입니다 — duration·tool 신호 기반. "
                 "정확한 원인은 해당 세션의 raw transcript를 참조하세요.")
    lines.append("")
    return "\n".join(lines)
