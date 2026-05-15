"""Produce Markdown + JSON + CSV + HTML reports from aggregated evaluations."""

from __future__ import annotations

import csv
import html as html_mod
import json
import re
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .aggregate import (
    SessionEval,
    _is_env_failure,
    aggregate_per_round_tool,
    aggregate_per_scenario_tool,
    aggregate_per_tool,
    aggregate_per_round_scenario_tool,
)
from .bias_check import analyze_bias


def _fmt_num(v, suffix: str = "", decimals: int = 1) -> str:
    if v is None:
        return "-"
    try:
        return f"{float(v):.{decimals}f}{suffix}"
    except Exception:
        return str(v)


def _fmt_duration(sec) -> str:
    if not sec:
        return "-"
    try:
        s = float(sec)
        if s < 60:
            return f"{s:.1f}s"
        m = s / 60.0
        if m < 60:
            return f"{m:.1f}m"
        return f"{m / 60:.1f}h"
    except Exception:
        return str(sec)


def write_markdown(evals: List[SessionEval], out_path: Path, meta: Dict) -> None:
    per_tool = aggregate_per_tool(evals)
    per_rt = aggregate_per_round_tool(evals)
    per_st = aggregate_per_scenario_tool(evals)
    per_rst = aggregate_per_round_scenario_tool(evals)

    tools = sorted({e.tool for e in evals})
    rounds = sorted({e.round_index for e in evals})
    scenarios = sorted({e.scenario for e in evals})

    lines: List[str] = []
    lines.append(f"# DEEPX Agentic Development — E2E Autopilot 분석 리포트")
    lines.append("")
    lines.append(f"> 생성 시각: {meta.get('generated_at')}")
    lines.append(f"> 분석 대상 sessions: **{len(evals)}** "
                 f"({len(tools)} tools × {len(rounds)} rounds × {len(scenarios)} scenarios)")
    lines.append(f"> Results root: `{meta.get('results_root')}`")
    lines.append("")
    if meta.get("caveats"):
        lines.append("## ⚠️ 주의 사항")
        for c in meta["caveats"]:
            lines.append(f"- {c}")
        lines.append("")
    lines.append("## 📖 점수 산정 방식 (Quick Reference)")
    lines.append("")
    lines.append("```")
    lines.append("Overall % = 0.25·Compliance% + 0.20·Quality% + 0.10·Verdict% + 0.25·ExecutionTrace% + 0.15·Runnability% + 2.5(START) + 2.5(DONE)")
    lines.append("Verdict   = PASS(100) / PARTIAL(50) / FAIL(0) / UNKNOWN(0)  — 시나리오 산출물 inferred")
    lines.append("Runnability = End-user 실행 가능성 (LLM 판정) — runnability_report.md 없으면 나머지 4-factor 비례 배분")
    lines.append("```")
    lines.append("")
    lines.append("- **Compliance** (25%) = HARD GATE 체크 통과율 (sentinel/output isolation/IFactory/필수파일/...)")
    lines.append("- **Quality** (20%) = py_compile + JSON parse + bash -n 통과율, placeholder/anti-pattern 페널티")
    lines.append("- **Verdict** (10%) = 시나리오 1차 산출물 존재성 (compiler→.dxnn, dx_app→factory+sync, suite→dual dir)")
    lines.append("- **ExecutionTrace** (25%) = 실제 실행 흔적 — session.log substantive + 성공 마커 + .dxnn realistic size + no failure markers")
    lines.append("- **Runnability** (15%) = End-user가 README/setup.sh/run.sh 따라 실제 실행 가능한지 LLM 판정 (PASS/PARTIAL/FAIL + 세부 1-5점)")
    lines.append("- **Exit 0 %** = pytest 라운드 전체의 exit 코드 (라운드 단위, **시나리오 단위 ≠**). **Overall 에는 미반영** — 정보용. timeout 케이스는 자가-개선 iteration 으로 인한 경우가 많아 페널티 부여하지 않음 (별도 ⏱ 마커 표시).")
    lines.append("")

    # ----------------------------------------------------------
    # 1. Per-tool 종합
    # ----------------------------------------------------------
    lines.append("## 1. 도구별 종합 점수")
    lines.append("")

    # Check for env failures and add note if any
    try:
        from .skip_analyzer import is_env_failure_eval
    except ImportError:
        is_env_failure_eval = lambda e: False  # noqa: E731
    total_env_failures = sum(1 for e in evals if is_env_failure_eval(e))
    if total_env_failures > 0:
        lines.append(f"> ⚠️ **가성 결함(False Alarm) 제외**: 환경 문제(API rate limit, TLS error, CLI crash)로 "
                     f"인한 완전 실패 세션 **{total_env_failures}건**이 점수 평균 산정 모수에서 제외되었습니다. "
                     f"이 세션들은 도구 능력이 아닌 인프라 문제를 반영하므로 가성 결함으로 분류됩니다.")
        lines.append("")
        # Per-tool breakdown of env failures
        env_by_tool = {}
        for e in evals:
            if is_env_failure_eval(e):
                env_by_tool.setdefault(e.tool, []).append(e)
        if env_by_tool:
            lines.append("| 도구 | 제외 세션 수 | 원인 |")
            lines.append("|------|----------:|------|")
            for t in sorted(env_by_tool.keys()):
                el = env_by_tool[t]
                rounds = sorted({e.round_index for e in el})
                rounds_str = ", ".join(f"R{r}" for r in rounds)
                lines.append(f"| {t} | {len(el)} | {rounds_str} |")
            lines.append("")

    # Compute scenario-level pass/fail aggregates per tool (scored only)
    scored_evals = [e for e in evals if not is_env_failure_eval(e)]
    pass_per_tool = {t: sum(1 for e in scored_evals if e.tool == t and e.verdict == "PASS") for t in tools}
    partial_per_tool = {t: sum(1 for e in scored_evals if e.tool == t and e.verdict == "PARTIAL") for t in tools}
    fail_per_tool = {t: sum(1 for e in scored_evals if e.tool == t and e.verdict == "FAIL") for t in tools}
    lines.append("| Tool | Scored/Total | Compl % | Qual % | Verdict % | Exec % | Runn % | Overall % | σ(Overall) | Avg Duration | START % | DONE % | Pass/Part/Fail | pytest Exit0 % | ⏱ Timeout | ToolCalls | LOC |")
    lines.append("|------|------------:|-------:|------:|----------:|------:|------:|----------:|----------:|-------------:|--------:|-------:|:--------------:|---------------:|----------:|---------:|----:|")
    for tool in tools:
        m = per_tool.get(tool, {})
        n_scored = int(m.get("sessions_scored", m.get("sessions", 0)))
        n_total = int(m.get("sessions", 0))
        n_env = int(m.get("env_failures", 0))
        sessions_display = f"{n_scored}/{n_total}" if n_env > 0 else str(n_total)
        verdict_avg = sum(e.verdict_score for e in scored_evals if e.tool == tool) / max(1, n_scored)
        exec_avg = sum(e.execution_score for e in scored_evals if e.tool == tool) / max(1, n_scored)
        runn_scores = [e.runnability_score for e in scored_evals if e.tool == tool and e.runnability_score > 0]
        runn_avg = sum(runn_scores) / len(runn_scores) if runn_scores else 0.0
        runn_display = _fmt_num(runn_avg) if runn_scores else "-"
        ppf = f"{pass_per_tool[tool]} / {partial_per_tool[tool]} / {fail_per_tool[tool]}"
        timeouts = sum(1 for e in scored_evals if e.tool == tool and e.suspected_timeout)
        lines.append(
            f"| **{tool}** | {sessions_display} | "
            f"{_fmt_num(m.get('avg_compliance_pct'))} | "
            f"{_fmt_num(m.get('avg_quality_score'))} | "
            f"{_fmt_num(verdict_avg)} | "
            f"{_fmt_num(exec_avg)} | "
            f"{runn_display} | "
            f"{_fmt_num(m.get('avg_overall_score'))} | "
            f"{_fmt_num(m.get('stdev_overall_score'))} | "
            f"{_fmt_duration(m.get('avg_duration_sec'))} | "
            f"{_fmt_num(m.get('pct_with_start_sentinel'))} | "
            f"{_fmt_num(m.get('pct_with_done_sentinel'))} | "
            f"{ppf} | "
            f"{_fmt_num(m.get('pct_exit_0'))} | "
            f"{timeouts} | "
            f"{_fmt_num(m.get('avg_tool_calls'))} | "
            f"{int(m.get('avg_python_loc', 0))} |"
        )
    lines.append("")
    lines.append("> **σ (sigma)** = stdev (낮을수록 일관성이 높음). **Exec %** = ExecutionTrace 점수 (실제 명령 실행 흔적). **⏱ Timeout** = 의심 timeout 발생 세션 수 (참고용; 점수에 페널티 없음). **Scored/Total** = 점수 산정 포함 세션 / 전체 세션 (환경 실패 제외).")
    lines.append("")

    # ----------------------------------------------------------
    # 2. Per round × tool — Overall %
    # ----------------------------------------------------------
    lines.append("## 2. 도구별 회차별 — Overall %")
    lines.append("")
    header = "| Tool | " + " | ".join(f"R{r}" for r in rounds) + " | 평균 |"
    sep = "|------|" + "|".join(":-----:" for _ in rounds) + "|-----:|"
    lines.append(header)
    lines.append(sep)
    for tool in tools:
        row_cells = []
        sum_v, count_v = 0.0, 0
        for r in rounds:
            m = per_rt.get((r, tool))
            v = m.get("avg_overall_score") if m else None
            row_cells.append(_fmt_num(v) if v is not None else "-")
            if v is not None:
                sum_v += v
                count_v += 1
        avg = sum_v / count_v if count_v else 0.0
        lines.append(f"| **{tool}** | " + " | ".join(row_cells) + f" | {_fmt_num(avg)} |")
    lines.append("")

    lines.append("## 3. 도구별 회차별 — Compliance %")
    lines.append("")
    lines.append(header)
    lines.append(sep)
    for tool in tools:
        row_cells = []
        sum_v, count_v = 0.0, 0
        for r in rounds:
            m = per_rt.get((r, tool))
            v = m.get("avg_compliance_pct") if m else None
            row_cells.append(_fmt_num(v) if v is not None else "-")
            if v is not None:
                sum_v += v
                count_v += 1
        avg = sum_v / count_v if count_v else 0.0
        lines.append(f"| **{tool}** | " + " | ".join(row_cells) + f" | {_fmt_num(avg)} |")
    lines.append("")

    lines.append("## 4. 도구별 회차별 — Avg Duration")
    lines.append("")
    lines.append(header)
    lines.append(sep)
    for tool in tools:
        row_cells = []
        for r in rounds:
            m = per_rt.get((r, tool))
            v = m.get("avg_duration_sec") if m else None
            row_cells.append(_fmt_duration(v) if v is not None else "-")
        m_tool = per_tool.get(tool, {})
        lines.append(
            f"| **{tool}** | " + " | ".join(row_cells) +
            f" | {_fmt_duration(m_tool.get('avg_duration_sec'))} |"
        )
    lines.append("")

    # ----------------------------------------------------------
    # 5. Per scenario × tool — 세분화된 다차원 표
    # ----------------------------------------------------------
    header2 = "| Tool | " + " | ".join(scenarios) + " | 평균 |"
    sep2 = "|------|" + "|".join(":-----:" for _ in scenarios) + "|-----:|"

    def _table(title: str, metric: str, fmt=_fmt_num):
        lines.append(f"### 5.{metric_index[0]} {title}")
        metric_index[0] += 1
        lines.append("")
        lines.append(header2)
        lines.append(sep2)
        for tool in tools:
            cells = []
            vals = []
            for sc in scenarios:
                m = per_st.get((sc, tool))
                v = m.get(metric) if m else None
                cells.append(fmt(v) if v is not None else "-")
                if v is not None:
                    vals.append(v)
            avg = sum(vals) / len(vals) if vals else 0.0
            lines.append(f"| **{tool}** | " + " | ".join(cells) + f" | {fmt(avg)} |")
        lines.append("")

    lines.append("## 5. 도구별 시나리오별 — 세분화")
    lines.append("")
    metric_index = [1]
    _table("Overall %", "avg_overall_score")
    _table("Compliance %", "avg_compliance_pct")
    _table("Quality %", "avg_quality_score")
    _table("Verdict % (산출물 PASS=100/PARTIAL=50/FAIL=0)", "avg_verdict_score")
    _table("PASS 비율 %", "pct_pass")
    _table("FAIL 비율 %", "pct_fail")
    _table("Avg Duration", "avg_duration_sec", _fmt_duration)
    _table("Avg Tool Calls", "avg_tool_calls")
    _table("Avg Python LOC", "avg_python_loc")

    # Compute scenario-level execution avg ad-hoc
    exec_avg_per_scen_tool = {}
    for sc in scenarios:
        for tool in tools:
            evals_st = [e for e in evals if e.scenario == sc and e.tool == tool]
            n = max(1, len(evals_st))
            exec_avg_per_scen_tool[(sc, tool)] = sum(e.execution_score for e in evals_st) / n

    lines.append(f"### 5.{metric_index[0]} ExecutionTrace %")
    metric_index[0] += 1
    lines.append("")
    lines.append(header2)
    lines.append(sep2)
    for tool in tools:
        cells = []
        vals = []
        for sc in scenarios:
            v = exec_avg_per_scen_tool.get((sc, tool), 0.0)
            cells.append(_fmt_num(v))
            vals.append(v)
        avg = sum(vals) / len(vals) if vals else 0.0
        lines.append(f"| **{tool}** | " + " | ".join(cells) + f" | {_fmt_num(avg)} |")
    lines.append("")

    # ----------------------------------------------------------
    # 6. Round × Scenario × Tool — 가장 granular 한 표 (verdict 표시)
    # ----------------------------------------------------------
    lines.append("## 6. 회차 × 시나리오 × 도구 — Verdict 매트릭스")
    lines.append("")
    verdict_emoji = {"PASS": "✅", "PARTIAL": "🟡", "FAIL": "❌", "UNKNOWN": "❓"}
    for sc in scenarios:
        lines.append(f"### {sc}")
        lines.append("")
        lines.append("| Tool | " + " | ".join(f"R{r}" for r in rounds) + " |")
        lines.append("|------|" + "|".join(":-----:" for _ in rounds) + "|")
        for tool in tools:
            cells = []
            for r in rounds:
                m = per_rst.get((r, sc, tool))
                if m:
                    cells.append(f"{verdict_emoji.get(m['verdict'], '?')} {_fmt_num(m['overall_score'])}")
                else:
                    cells.append("-")
            lines.append(f"| **{tool}** | " + " | ".join(cells) + " |")
        lines.append("")

    # ----------------------------------------------------------
    # 7. Per-session 상세 (모든 행)
    # ----------------------------------------------------------
    lines.append("## 7. 세션별 상세 (전체)")
    lines.append("")
    lines.append("| R | Tool | Scenario | Model | Verdict | Exec % | Runn % | ⏱ | pytest | Duration | Comp % | Qual % | Overall % | S/D | ToolCalls | LOC | PH | Eng | Reason |")
    lines.append("|--:|------|----------|-------|:------:|------:|------:|:--:|:------:|---------:|------:|------:|---------:|:--:|---------:|---:|---:|----:|-------|")
    for e in sorted(evals, key=lambda x: (x.round_index, x.tool, x.scenario)):
        model_short = (e.model or "").replace("claude-sonnet-", "").replace("(non-standard)", "⚠")[:18]
        verdict_disp = f"{verdict_emoji.get(e.verdict, '?')} {e.verdict[:4]}"
        sd_marker = ("✓" if e.has_start else "✗") + "/" + ("✓" if e.has_done else "✗")
        timeout_mark = "⏱" if e.suspected_timeout else ""
        runn_disp = _fmt_num(e.runnability_score) if e.runnability_score > 0 else "-"
        lines.append(
            f"| {e.round_index} | {e.tool} | {e.scenario} | {model_short} | "
            f"{verdict_disp} | "
            f"{_fmt_num(e.execution_score)} | "
            f"{runn_disp} | "
            f"{timeout_mark} | "
            f"{e.exit_status if e.exit_status is not None else '-'} | "
            f"{_fmt_duration(e.duration_sec)} | "
            f"{_fmt_num(e.compliance_score_pct)} | "
            f"{_fmt_num(e.quality_score)} | "
            f"{_fmt_num(e.overall_score)} | "
            f"{sd_marker} | "
            f"{e.tool_call_count} | "
            f"{e.python_loc} | "
            f"{e.placeholder_hits} | {e.direct_engine_use} | "
            f"{e.verdict_reason[:60]} |"
        )
    lines.append("")

    # ----------------------------------------------------------
    # 8. 회차별 실패 시나리오 카운트
    # ----------------------------------------------------------
    lines.append("## 8. 회차별 FAIL Verdict 카운트")
    lines.append("")
    lines.append(header)
    lines.append(sep)
    for tool in tools:
        row_cells = []
        total_fail = 0
        for r in rounds:
            fails = sum(
                1 for e in evals
                if e.tool == tool and e.round_index == r and e.verdict == "FAIL"
            )
            row_cells.append(str(fails))
            total_fail += fails
        lines.append(f"| **{tool}** | " + " | ".join(row_cells) + f" | **{total_fail}** |")
    lines.append("")

    # ----------------------------------------------------------
    # 9. 토큰 사용량 + 비용 효율성
    # ----------------------------------------------------------
    lines.append("## 9. 토큰 사용량 + 비용 효율성")
    lines.append("")

    # --- 9.1 Raw token table (as-recorded) ---
    n_rounds = len(set(e.round_index for e in evals if e.round_index))
    n_scenarios = len(set(e.scenario for e in evals if e.scenario))
    n_sessions = len(evals)
    lines.append(f"### 9.1 도구별 누적 토큰 — Raw (전체 {n_sessions} sessions 합계)")
    lines.append("")
    lines.append("> ⚠ **토큰 의미론이 도구별로 다릅니다.** 아래 표의 수치는 각 도구 stream에서 추출한 원본(raw) 값이며, "
                 "직접 비교에는 주의가 필요합니다. 차이 원인은 §9.2에서 설명합니다.")
    lines.append("")
    lines.append("| Tool | Sessions | Fresh Input | Output | Cache Read (raw) | Cache Write | Reasoning | Avg Output/Sess |")
    lines.append("|------|--------:|-----------:|-------:|-----------------:|------------:|----------:|----------------:|")
    for tool in tools:
        ev = [e for e in evals if e.tool == tool]
        n = max(1, len(ev))
        n_with = sum(1 for e in ev if e.input_tokens > 0 or e.output_tokens > 0 or e.cache_read_tokens > 0)
        ti = sum(e.input_tokens for e in ev)
        to = sum(e.output_tokens for e in ev)
        tcr = sum(e.cache_read_tokens for e in ev)
        tcw = sum(e.cache_write_tokens for e in ev)
        tre = sum(e.reasoning_tokens for e in ev)
        lines.append(f"| **{tool}** | {n_with}/{n} | {ti:,} | {to:,} | {tcr:,} | {tcw:,} | {tre:,} | {int(to/n):,} |")
    lines.append("")

    # --- 9.2 Token semantics note ---
    lines.append("### 9.2 도구별 토큰 보고 의미론 차이")
    lines.append("")
    lines.append("각 도구/provider의 stream 형식에 따라 토큰 필드의 의미가 다릅니다:")
    lines.append("")
    lines.append("| 도구 | `input_tokens` 의미 | `cache_read` 의미 | 보정 방법 |")
    lines.append("|------|-------------------|------------------|----------|")
    lines.append("| **claude-code** | Fresh only (Anthropic API native) | **Per-turn SUM** — 매 turn마다 전체 캐시 컨텍스트를 재보고 → 누적 합산 시 ~100× 과대 | 마지막 turn의 cache_read가 실제 context window |")
    lines.append("| **copilot-cli** | Fresh (total − cache_read − cache_write로 보정 완료) | Session 합계 ✅ | 이미 보정됨 |")
    lines.append("| **codex-cli** | Fresh (total − cached로 보정 완료) | Session cached ✅ | 이미 보정됨 |")
    lines.append("| **cursor-cli** | Fresh (Anthropic backend, result event) | Session 합계 ✅ | 보정 불필요 |")
    lines.append("| **opencode-cli** | Per-step incremental SUM | Per-step cache SUM | provider 의존, 대체로 정상 |")
    lines.append("")
    lines.append("> **결론**: `Fresh Input`과 `Output`은 도구 간 비교 가능합니다. "
                 "`Cache Read`는 claude-code만 per-turn 합산으로 과대 보고되므로 직접 비교에 부적합합니다.")
    lines.append("")

    # --- 9.3 Premium Requests (observed) ---
    lines.append("### 9.3 도구별 Premium Requests (관측치)")
    lines.append("")
    lines.append("| Tool | Total Premium Req | Avg PR/Session | 측정 방식 |")
    lines.append("|------|------------------:|---------------:|----------|")
    pr_notes = {
        "claude-code": "해당 없음 (Anthropic Team Plan 구독, PR 개념 없음)",
        "copilot-cli": "`session.shutdown.totalPremiumRequests` (actual)",
        "cursor-cli": "해당 없음 (Cursor Team Plan 구독, PR 개념 없음)",
        "opencode-cli": "Copilot provider 경유 — PR 소비량 stream 미노출",
        "codex-cli": "Copilot provider 경유 — PR 소비량 stream 미노출",
    }
    for tool in tools:
        ev = [e for e in evals if e.tool == tool]
        n = max(1, len(ev))
        total_prem = sum(e.premium_requests for e in ev)
        avg_prem = total_prem / n
        note = pr_notes.get(tool, "-")
        if total_prem > 0:
            lines.append(f"| **{tool}** | {total_prem:,} | {avg_prem:.1f} | {note} |")
        else:
            lines.append(f"| **{tool}** | — | — | {note} |")
    lines.append("")

    # --- 9.4 Cost comparison limitation ---
    lines.append("### 9.4 비용 산정 한계 및 실제 구독 현황")
    lines.append("")
    lines.append("**일관된 기준의 도구 간 비용 비교는 현실적으로 불가능합니다.** 각 도구의 과금 체계가 근본적으로 다르기 때문입니다:")
    lines.append("")
    lines.append("| 도구 | 구독 | 초과 허용 | 산정 방식 |")
    lines.append("|------|------|---------|---------|")
    lines.append("| **claude-code** | 정액제 | 정액 구독 한도 내 | 토큰 사용량 방식 |")
    lines.append("| **copilot-cli** | 정액제 | 초과 허용 | Premium Request 단위 과금 |")
    lines.append("| **cursor-cli** | 정액제 | 정액 구독 한도 내 | — |")
    lines.append("| **opencode-cli** | 정액제 | 초과 허용 | Premium Request 단위 과금 |")
    lines.append("| **codex-cli** | 정액제 | 초과 허용 | Premium Request 단위 과금 |")
    lines.append("")
    lines.append("> **핵심 제약**: copilot-cli만 실제 Premium Request 소비량이 stream에 기록됩니다. "
                 "opencode-cli와 codex-cli는 동일한 Copilot backend를 사용하지만 PR 소비량이 stream에 노출되지 않아 "
                 "copilot-cli와의 비용 비교가 불가능합니다. claude-code와 cursor-cli는 정액 구독이므로 "
                 "토큰 사용량과 무관하게 월 고정 비용만 발생합니다.")
    lines.append("")

    # --- 9.5 External benchmarks for cost-efficiency context ---
    lines.append("### 9.5 외부 벤치마크 기반 모델 비용 효율성 참고")
    lines.append("")
    lines.append("도구 간 직접 비용 비교가 불가능하므로, 외부 벤치마크의 **모델별 성능 대비 비용** 데이터를 참고로 제시합니다.")
    lines.append("")
    lines.append("#### A. Aider Polyglot Coding Benchmark (2025.11)")
    lines.append("")
    lines.append("출처: [aider.chat/docs/leaderboards](https://aider.chat/docs/leaderboards/) — "
                 "225 exercises (C++, Go, Java, JS, Python, Rust)")
    lines.append("")
    lines.append("| Model | Edit Accuracy | Run Cost | 비고 |")
    lines.append("|-------|-------------:|--------:|------|")
    lines.append("| GPT-5 (high) | 88.0% | $29.08 | 최고 정확도 |")
    lines.append("| GPT-5 (medium) | 86.7% | $17.69 | 비용 대비 최고 효율 |")
    lines.append("| Claude Opus 4 (no think) | 70.7% | $68.63 | 높은 비용 |")
    lines.append("| Claude Opus 4 (32k think) | 72.0% | $65.75 | thinking 효과 미미 |")
    lines.append("| Claude Sonnet 4 (32k think) | 61.3% | $26.58 | |")
    lines.append("| Claude Sonnet 4 (no think) | 56.4% | $15.82 | |")
    lines.append("| GPT-4.1 | 52.4% | $9.86 | 저비용 |")
    lines.append("| DeepSeek-V3.2-Exp (Reasoner) | 74.2% | $1.30 | **극히 저렴** |")
    lines.append("")
    lines.append("> ⚠ Claude Sonnet **4.6**, Opus **4.6/4.7**, GPT-5.x-**Codex** 변형은 아직 Aider 리더보드에 미등재 "
                 "(2025.11 기준). 위 수치는 이전 세대 모델 기준입니다.")
    lines.append("")
    lines.append("#### B. SWE-Bench Verified (실제 GitHub Issue 해결률)")
    lines.append("")
    lines.append("출처: [github.com/swe-bench/experiments](https://github.com/swe-bench/experiments) — 500 issues")
    lines.append("")
    lines.append("| Agent + Model | Resolve Rate | 날짜 |")
    lines.append("|--------------|------------:|------|")
    lines.append("| OpenHands + Claude Opus 4.5 | 77.6% (388/500) | 2025.11 |")
    lines.append("| Sonar Foundation + Claude Sonnet 4.5 | 74.8% (374/500) | 2025.11 |")
    lines.append("")
    lines.append("> SWE-bench는 2025.11부터 학술 팀 + 오픈소스 방법론만 접수하는 정책으로 변경되어, "
                 "최신 상용 모델(Sonnet 4.6, Opus 4.6/4.7)의 공식 결과는 부재합니다.")
    lines.append("")
    lines.append("#### C. GitHub Copilot Premium Request 모델별 Multiplier (2026.06 이전)")
    lines.append("")
    lines.append("출처: [GitHub Docs — Models and Pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)")
    lines.append("")
    lines.append("| Model | 현재 Multiplier | 2026.06+ Multiplier |")
    lines.append("|-------|---------------:|-------------------:|")
    lines.append("| **Claude Sonnet 4.6** | **1×** | **9×** |")
    lines.append("| **Claude Opus 4.6** | **3×** | **27×** |")
    lines.append("| Claude Opus 4.7 | 15× | 27× |")
    lines.append("| GPT-5.2-Codex | 1× | 3× |")
    lines.append("| GPT-5.3-Codex | 1× | 6× |")
    lines.append("| GPT-4.1 (included) | 0× | 1× |")
    lines.append("| GPT-5 mini (included) | 0× | 0.33× |")
    lines.append("")
    lines.append("> ⚠ **2026.06 가격 인상 예정**: Sonnet 4.6은 1× → 9×, Opus 4.6은 3× → 27×로 대폭 인상. "
                 "Copilot provider 기반 도구(copilot-cli, opencode-cli, codex-cli)의 실질 비용이 크게 증가할 전망입니다.")
    lines.append("")
    lines.append("#### D. Anthropic API Token 단가 (참고용)")
    lines.append("")
    lines.append("| Model | Input /MTok | Output /MTok | Cache Read /MTok | Cache Write /MTok |")
    lines.append("|-------|----------:|----------:|----------:|----------:|")
    lines.append("| Claude Sonnet 4.6 | $3.00 | $15.00 | $0.30 | $3.75 |")
    lines.append("| Claude Opus 4.6 | $5.00 | $25.00 | $0.50 | $6.25 |")
    lines.append("| Claude Opus 4.7 | $5.00 | $25.00 | $0.50 | $6.25 |")
    lines.append("| Claude Haiku 4.5 | $1.00 | $5.00 | $0.10 | $1.25 |")
    lines.append("")

    # --- 9.6 Comprehensive cost-performance assessment ---
    lines.append("### 9.6 비용 대비 성능 종합 판단")
    lines.append("")
    lines.append("아래는 당사 구독 형태, 도구 사용 방법, E2E 테스트 결과, 외부 벤치마크를 종합한 비용 효율성 평가입니다:")
    lines.append("")
    # Build ranked data with subscription info
    sub_info = {
        "claude-code": ("정액제", "정액 구독 한도 내", "토큰 사용량 방식"),
        "copilot-cli": ("정액제", "초과 허용", "Premium Request 단위 과금"),
        "cursor-cli": ("정액제", "정액 구독 한도 내", "—"),
        "opencode-cli": ("정액제", "초과 허용", "Premium Request 단위 과금"),
        "codex-cli": ("정액제", "초과 허용", "Premium Request 단위 과금"),
    }
    lines.append("| 도구 | E2E Overall | 구독 | 초과 허용 | 산정 방식 | 효율성 판단 |")
    lines.append("|------|----------:|------|---------|---------|----------|")
    # Get overall scores from aggregated data
    tool_overall = {}
    for tool in tools:
        ev = [e for e in evals if e.tool == tool]
        scored = [e for e in ev if not _is_env_failure(e)]
        if scored:
            tool_overall[tool] = sum(e.overall_score for e in scored) / len(scored)
        else:
            tool_overall[tool] = 0.0
    for tool in tools:
        sub, overage, method = sub_info.get(tool, ("?", "?", "?"))
        ov = tool_overall.get(tool, 0)
        # Efficiency judgment
        if ov >= 78:
            eff = "✅ 높음"
        elif ov >= 75:
            eff = "⚠ 보통"
        else:
            eff = "△ 개선 필요"
        lines.append(f"| **{tool}** | {ov:.1f} | {sub} | {overage} | {method} | {eff} |")
    lines.append("")
    lines.append("> **종합 의견**: 현재 모든 도구가 구독 기반 정액 또는 Enterprise PR 충전 체계를 사용하고 있어, "
                 "토큰 단위 비용 비교는 의미가 제한적입니다. **비용 효율성은 '동일 구독료 내에서 더 많은 성공적 세션을 "
                 "완료할 수 있는가'로 판단하는 것이 적절합니다.** E2E Overall Score가 이 기준에 가장 가까운 지표입니다.")
    lines.append("")

    # --- 9.7 Provider dashboards ---
    lines.append("### 9.7 외부 Provider Usage Dashboard (실제 사용량 검증용)")
    lines.append("")
    lines.append("| Provider | Dashboard | 비고 |")
    lines.append("|----------|-----------|------|")
    lines.append("| **Anthropic** | https://console.anthropic.com/settings/usage | claude-code 실사용량 |")
    lines.append("| **GitHub Copilot** | https://github.com/organizations/`<ORG>`/settings/copilot/usage | copilot-cli PR 소비량 |")
    lines.append("| **Cursor** | https://cursor.com/dashboard | cursor-cli 사용량 |")
    lines.append("")

    # ----------------------------------------------------------
    # 10. 평가 방법 (자세)
    # ----------------------------------------------------------
    lines.append("## 10. 평가 방법 (자세)")
    lines.append("")
    lines.append("### Compliance % (HARD GATE 체크 통과율)")
    lines.append("- `sentinel_start` — 응답 첫 줄 `[DX-AGENTIC-DEV: START]`")
    lines.append("- `sentinel_done` — 마지막 줄 `[DX-AGENTIC-DEV: DONE (output-dir: ...)]`")
    lines.append("- `output_isolation_present` — 산출물이 `dx-agentic-dev/<session_id>/` 하위")
    lines.append("- `session_id_format` — `YYYYMMDD-HHMMSS_<agent>_<model>_<task>` 패턴")
    lines.append("- `mandatory_deliverables` — 시나리오별 필수 파일 존재 (setup.sh, run.sh, README.md, session.log, factory, *_sync.py 등)")
    lines.append("- `ifactory_5_methods` — dx_app factory 5-method 패턴 (`create_preprocessor`, `create_postprocessor`, `create_visualizer`, `get_model_name`, `get_task_type`)")
    lines.append("- `session_log_authentic` — session.log 가 hand-written heredoc 아님 (실 명령 출력)")
    lines.append("- `suite_dual_session_dirs` — suite 시나리오에서 2개 별도 sub-project dir 생성 (R41 HARD GATE)")
    lines.append("")
    lines.append("### Quality % (정적 코드 품질)")
    lines.append("- 모든 `.py` 파일 `py_compile` → 통과율")
    lines.append("- 모든 `.json` 파일 `json.load` → 통과율")
    lines.append("- 모든 `.sh` 파일 `bash -n` → 통과율")
    lines.append("- **Placeholder** 페널티: `# TODO: implement`, 주석된 dx_engine/dxnn_sdk import, `np.zeros(...)` 등 (hit 당 5점, cap 30)")
    lines.append("- **Direct engine use** 페널티: factory 외부 `engine.run()/.run_async()` 호출 — HARD GATE 위반 (hit 당 5점, cap 15)")
    lines.append("")
    lines.append("### Verdict (시나리오 1차 산출물 PASS/PARTIAL/FAIL — 정적 추론)")
    lines.append("- `compiler`: PASS = `*.dxnn` + `config.json` 존재 / FAIL = `.dxnn` 미생성")
    lines.append("- `dx_app`: PASS = factory + `*_sync.py` 둘 다 / PARTIAL = factory 만 / FAIL = factory 없음")
    lines.append("- `dx_stream` / `dx_stream_cascaded`: PASS = `pipeline.py` + `run_*.sh` / PARTIAL = pipeline 만 / FAIL = pipeline 없음")
    lines.append("- `runtime`: PASS = sub-project 출력 중 하나 이상이 형식 통과")
    lines.append("- `suite`: PASS = dx-compiler + dx_app 둘 다 자체 dir 으로 (R41 HARD GATE) / PARTIAL = 하나만 / FAIL = 둘 다 없음")
    lines.append("")
    lines.append("### Overall % (composite)")
    lines.append("```")
    lines.append("Overall = 0.25 × Compliance + 0.20 × Quality + 0.10 × Verdict + 0.25 × ExecutionTrace + 0.15 × Runnability + 2.5(START) + 2.5(DONE)")
    lines.append("```")
    lines.append("- Runnability 데이터가 없는 세션은 나머지 4-factor 비례 배분 (backward compatible)")
    lines.append("- Verdict 는 파일 존재만 확인하므로 가중치 낮음 (10%); 실제 실행 증거(Execution 25%)와 end-user 관점(Runnability 15%)에 높은 비중")
    lines.append("")
    lines.append("### pytest Exit 0 %")
    lines.append("- pytest 의 round-level exit code (한 라운드에 6개 시나리오; 그 중 한 assertion 실패 시 1)")
    lines.append("- **Overall 점수에는 미반영** (라운드 단위 → 시나리오 단위로 분해 불가). 별도 컬럼으로 표시.")
    lines.append("- 진정한 시나리오별 pass/fail 은 Verdict 컬럼이 더 정확.")
    lines.append("")
    lines.append("### Duration")
    lines.append("- Claude Code: `result.duration_ms` (stream-json 최종 이벤트)")
    lines.append("- Cursor: `result` event 의 `duration_ms` (개별 tool_call 의 duration_ms는 제외 — 세션 총합과 구분)")
    lines.append("- OpenCode: `timestamp` (Unix ms) 첫/마지막 이벤트 차이")
    lines.append("- Copilot: events-*.jsonl 의 첫/마지막 이벤트 timestamp")
    lines.append("- Fallback: artifact + output dir 파일 mtime 의 최대-최소 차이")
    lines.append("")

    # Q4 — Cursor bias check section
    lines.append(analyze_bias(evals))

    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_json(evals: List[SessionEval], out_path: Path, meta: Dict) -> None:
    payload = {
        "meta": meta,
        "per_tool": aggregate_per_tool(evals),
        "per_round_tool": {
            f"R{k[0]}__{k[1]}": v for k, v in aggregate_per_round_tool(evals).items()
        },
        "per_scenario_tool": {
            f"{k[0]}__{k[1]}": v for k, v in aggregate_per_scenario_tool(evals).items()
        },
        "sessions": [asdict(e) for e in evals],
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(evals: List[SessionEval], out_path: Path) -> None:
    columns = [
        "round", "tool", "scenario", "model", "verdict", "verdict_score", "verdict_reason",
        "exit_status_round", "duration_sec",
        "has_start", "has_done", "compliance_pct", "quality_score",
        "execution_score", "runnability_score", "overall_score",
        "tool_call_count", "python_files", "python_loc", "bash_loc", "json_loc",
        "placeholder_hits", "direct_engine_use",
        "input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens", "reasoning_tokens",
        "premium_requests", "estimated_premium_requests",
        "cost_units", "estimated_usd", "cost_basis", "cost_note",
        "suspected_timeout",
        "session_id", "output_dirs",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for e in evals:
            w.writerow({
                "round": e.round_index,
                "tool": e.tool,
                "scenario": e.scenario,
                "model": e.model,
                "verdict": e.verdict,
                "verdict_score": e.verdict_score,
                "verdict_reason": e.verdict_reason,
                "exit_status_round": e.exit_status,
                "duration_sec": e.duration_sec,
                "has_start": e.has_start,
                "has_done": e.has_done,
                "compliance_pct": e.compliance_score_pct,
                "quality_score": e.quality_score,
                "execution_score": e.execution_score,
                "runnability_score": e.runnability_score,
                "overall_score": e.overall_score,
                "tool_call_count": e.tool_call_count,
                "python_files": e.python_files,
                "python_loc": e.python_loc,
                "bash_loc": e.bash_loc,
                "json_loc": e.json_loc,
                "placeholder_hits": e.placeholder_hits,
                "direct_engine_use": e.direct_engine_use,
                "input_tokens": e.input_tokens,
                "output_tokens": e.output_tokens,
                "cache_read_tokens": e.cache_read_tokens,
                "cache_write_tokens": e.cache_write_tokens,
                "reasoning_tokens": e.reasoning_tokens,
                "premium_requests": e.premium_requests,
                "estimated_premium_requests": e.estimated_premium_requests,
                "cost_units": e.cost_units,
                "estimated_usd": e.estimated_usd,
                "cost_basis": e.cost_basis,
                "cost_note": e.cost_note,
                "suspected_timeout": e.suspected_timeout,
                "session_id": e.session_id,
                "output_dirs": "; ".join(e.output_dirs),
            })


# ---------------------------------------------------------------------------
# HTML Report
# ---------------------------------------------------------------------------

_HTML_CSS = """\
:root { --bg: #0d1117; --fg: #e6edf3; --muted: #8b949e; --border: #30363d;
        --accent: #58a6ff; --green: #3fb950; --red: #f85149; --yellow: #d29922;
        --table-bg: #161b22; --table-stripe: #1c2333; }
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--fg); font-family: -apple-system, BlinkMacSystemFont,
       'Segoe UI', Helvetica, Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
.container { max-width: 1400px; margin: 0 auto; }
h1 { border-bottom: 1px solid var(--border); padding-bottom: 12px; }
h2 { color: var(--accent); margin-top: 2em; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
h3 { color: var(--muted); margin-top: 1.5em; }
table { border-collapse: collapse; width: 100%; margin: 12px 0 24px; font-size: 0.88em; }
th { background: var(--table-bg); color: var(--accent); padding: 8px 10px; text-align: left;
     border: 1px solid var(--border); position: sticky; top: 0; }
td { padding: 6px 10px; border: 1px solid var(--border); }
tr:nth-child(even) { background: var(--table-stripe); }
tr:hover { background: #21262d; }
blockquote { border-left: 3px solid var(--accent); padding-left: 16px; color: var(--muted);
             margin: 12px 0; }
code { background: #1c2333; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
pre { background: #161b22; padding: 14px; border-radius: 6px; overflow-x: auto;
      border: 1px solid var(--border); }
pre code { background: transparent; padding: 0; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; font-weight: 600; }
.badge-pass { background: #238636; color: #fff; }
.badge-fail { background: #da3633; color: #fff; }
.badge-partial { background: #9e6a03; color: #fff; }
ul { padding-left: 1.5em; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.timestamp { color: var(--muted); font-size: 0.85em; }
"""


def _md_to_html(md_text: str) -> str:
    """Convert Markdown text to HTML (lightweight, table-aware)."""
    lines = md_text.split("\n")
    html_parts: List[str] = []
    in_table = False
    in_code = False
    in_list = False
    code_lines: List[str] = []

    for line in lines:
        stripped = line.strip()

        # Code blocks
        if stripped.startswith("```"):
            if in_code:
                html_parts.append(f'<pre><code>{html_mod.escape(chr(10).join(code_lines))}</code></pre>')
                code_lines = []
                in_code = False
            else:
                if in_list:
                    html_parts.append("</ul>")
                    in_list = False
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue

        # Empty line
        if not stripped:
            if in_table:
                html_parts.append("</tbody></table>")
                in_table = False
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            continue

        # Table separator (|---|...)
        if re.match(r"^\|[\s\-:|]+\|$", stripped):
            continue

        # Table row
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not in_table:
                html_parts.append('<table>')
                html_parts.append("<thead><tr>" + "".join(f"<th>{_inline_md(c)}</th>" for c in cells) + "</tr></thead>")
                html_parts.append("<tbody>")
                in_table = True
            else:
                html_parts.append("<tr>" + "".join(f"<td>{_inline_md(c)}</td>" for c in cells) + "</tr>")
            continue

        if in_table:
            html_parts.append("</tbody></table>")
            in_table = False

        # Headers
        if stripped.startswith("#"):
            m = re.match(r"^(#{1,6})\s+(.*)", stripped)
            if m:
                level = len(m.group(1))
                text = _inline_md(m.group(2))
                html_parts.append(f"<h{level}>{text}</h{level}>")
                continue

        # Blockquote
        if stripped.startswith(">"):
            text = _inline_md(stripped.lstrip("> "))
            html_parts.append(f"<blockquote>{text}</blockquote>")
            continue

        # List items
        if re.match(r"^[-*]\s", stripped):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            text = _inline_md(stripped[2:])
            html_parts.append(f"<li>{text}</li>")
            continue

        if in_list:
            html_parts.append("</ul>")
            in_list = False

        # Regular paragraph
        html_parts.append(f"<p>{_inline_md(stripped)}</p>")

    # Close any open tags
    if in_table:
        html_parts.append("</tbody></table>")
    if in_list:
        html_parts.append("</ul>")
    if in_code:
        html_parts.append(f'<pre><code>{html_mod.escape(chr(10).join(code_lines))}</code></pre>')

    return "\n".join(html_parts)


def _inline_md(text: str) -> str:
    """Convert inline Markdown (bold, code, links) to HTML."""
    text = html_mod.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Verdict badges
    text = text.replace("✅", '<span class="badge badge-pass">✅</span>')
    text = text.replace("❌", '<span class="badge badge-fail">❌</span>')
    text = text.replace("❓", '<span class="badge badge-partial">❓</span>')
    return text


def write_html(evals: List[SessionEval], out_path: Path, meta: Dict) -> None:
    """Generate self-contained HTML report from evaluations.

    Reads the companion ``.md`` file (must already exist) and converts it.
    """
    md_path = out_path.with_suffix(".md")
    if not md_path.exists():
        return

    md_content = md_path.read_text(encoding="utf-8")
    body = _md_to_html(md_content)
    title = "DEEPX Agentic Development — E2E Autopilot Analysis"

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_mod.escape(title)}</title>
<style>
{_HTML_CSS}
</style>
</head>
<body>
<div class="container">
{body}
</div>
</body>
</html>"""

    out_path.write_text(html, encoding="utf-8")


def md_file_to_html(md_path: Path, html_path: Path, title: str = "") -> None:
    """Convert any Markdown file to a self-contained HTML file."""
    if not md_path.exists():
        return

    md_content = md_path.read_text(encoding="utf-8")
    body = _md_to_html(md_content)
    title = title or md_path.stem

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_mod.escape(title)}</title>
<style>
{_HTML_CSS}
</style>
</head>
<body>
<div class="container">
{body}
</div>
</body>
</html>"""

    html_path.write_text(html, encoding="utf-8")
