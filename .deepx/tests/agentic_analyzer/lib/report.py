"""Produce Markdown + JSON + CSV reports from aggregated evaluations."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .aggregate import (
    SessionEval,
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
    lines.append("Overall % = 0.30·Compliance% + 0.25·Quality% + 0.25·Verdict% + 0.15·ExecutionTrace% + 2.5(START) + 2.5(DONE)")
    lines.append("Verdict   = PASS(100) / PARTIAL(50) / FAIL(0) / UNKNOWN(0)  — 시나리오 산출물 inferred")
    lines.append("```")
    lines.append("")
    lines.append("- **Compliance** = HARD GATE 체크 통과율 (sentinel/output isolation/IFactory/필수파일/...)")
    lines.append("- **Quality** = py_compile + JSON parse + bash -n 통과율, placeholder/anti-pattern 페널티")
    lines.append("- **Verdict** = 시나리오 1차 산출물 존재성 (compiler→.dxnn, dx_app→factory+sync, suite→dual dir)")
    lines.append("- **ExecutionTrace** = 실제 실행 흔적 — session.log substantive + 성공 마커 + .dxnn realistic size + no failure markers")
    lines.append("- **Exit 0 %** = pytest 라운드 전체의 exit 코드 (라운드 단위, **시나리오 단위 ≠**). **Overall 에는 미반영** — 정보용. timeout 케이스는 자가-개선 iteration 으로 인한 경우가 많아 페널티 부여하지 않음 (별도 ⏱ 마커 표시).")
    lines.append("")

    # ----------------------------------------------------------
    # 1. Per-tool 종합
    # ----------------------------------------------------------
    lines.append("## 1. 도구별 종합 점수")
    lines.append("")
    # Compute scenario-level pass/fail aggregates per tool
    pass_per_tool = {t: sum(1 for e in evals if e.tool == t and e.verdict == "PASS") for t in tools}
    partial_per_tool = {t: sum(1 for e in evals if e.tool == t and e.verdict == "PARTIAL") for t in tools}
    fail_per_tool = {t: sum(1 for e in evals if e.tool == t and e.verdict == "FAIL") for t in tools}
    lines.append("| Tool | Sessions | Compl % | Qual % | Verdict % | Exec % | Overall % | σ(Overall) | Avg Duration | START % | DONE % | Pass/Part/Fail | pytest Exit0 % | ⏱ Timeout | ToolCalls | LOC |")
    lines.append("|------|---------:|-------:|------:|----------:|------:|----------:|----------:|-------------:|--------:|-------:|:--------------:|---------------:|----------:|---------:|----:|")
    for tool in tools:
        m = per_tool.get(tool, {})
        verdict_avg = sum(e.verdict_score for e in evals if e.tool == tool) / max(1, m.get("sessions", 1))
        exec_avg = sum(e.execution_score for e in evals if e.tool == tool) / max(1, m.get("sessions", 1))
        ppf = f"{pass_per_tool[tool]} / {partial_per_tool[tool]} / {fail_per_tool[tool]}"
        timeouts = sum(1 for e in evals if e.tool == tool and e.suspected_timeout)
        lines.append(
            f"| **{tool}** | {int(m.get('sessions', 0))} | "
            f"{_fmt_num(m.get('avg_compliance_pct'))} | "
            f"{_fmt_num(m.get('avg_quality_score'))} | "
            f"{_fmt_num(verdict_avg)} | "
            f"{_fmt_num(exec_avg)} | "
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
    lines.append("> **σ (sigma)** = stdev (낮을수록 일관성이 높음). **Exec %** = ExecutionTrace 점수 (실제 명령 실행 흔적). **⏱ Timeout** = 의심 timeout 발생 세션 수 (참고용; 점수에 페널티 없음).")
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
    lines.append("| R | Tool | Scenario | Model | Verdict | Exec % | ⏱ | pytest | Duration | Comp % | Qual % | Overall % | S/D | ToolCalls | LOC | PH | Eng | Reason |")
    lines.append("|--:|------|----------|-------|:------:|------:|:--:|:------:|---------:|------:|------:|---------:|:--:|---------:|---:|---:|----:|-------|")
    for e in sorted(evals, key=lambda x: (x.round_index, x.tool, x.scenario)):
        model_short = (e.model or "").replace("claude-sonnet-", "").replace("(non-standard)", "⚠")[:18]
        verdict_disp = f"{verdict_emoji.get(e.verdict, '?')} {e.verdict[:4]}"
        sd_marker = ("✓" if e.has_start else "✗") + "/" + ("✓" if e.has_done else "✗")
        timeout_mark = "⏱" if e.suspected_timeout else ""
        lines.append(
            f"| {e.round_index} | {e.tool} | {e.scenario} | {model_short} | "
            f"{verdict_disp} | "
            f"{_fmt_num(e.execution_score)} | "
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
    # 9. 토큰 사용량 + 비용 + premium requests
    # ----------------------------------------------------------
    lines.append("## 9. 토큰 사용량 + 비용 + Premium Requests")
    lines.append("")
    lines.append("### 9.1 도구별 누적 토큰 (5라운드 × 6시나리오 = 30 sessions 합계)")
    lines.append("")
    lines.append("| Tool | Total Input | Total Output | Cache Read | Cache Write | Reasoning | Avg Output/Session |")
    lines.append("|------|------------:|-------------:|-----------:|------------:|----------:|-------------------:|")
    for tool in tools:
        ev = [e for e in evals if e.tool == tool]
        n = max(1, len(ev))
        ti = sum(e.input_tokens for e in ev)
        to = sum(e.output_tokens for e in ev)
        tcr = sum(e.cache_read_tokens for e in ev)
        tcw = sum(e.cache_write_tokens for e in ev)
        tre = sum(e.reasoning_tokens for e in ev)
        lines.append(f"| **{tool}** | {ti:,} | {to:,} | {tcr:,} | {tcw:,} | {tre:,} | {int(to/n):,} |")
    lines.append("")
    lines.append("### 9.2 도구별 Premium Requests / Cost")
    lines.append("")
    lines.append("| Tool | Total Premium Requests | Total Cost Units | Avg Premium/Session | Notes |")
    lines.append("|------|----------------------:|----------------:|--------------------:|-------|")
    notes_map = {
        "claude-code": "Anthropic API (subscription-based; no premium request concept)",
        "copilot-cli": "`requests.count` = GitHub Copilot Premium Requests consumed",
        "cursor-cli": "Token-based pricing — no premium request",
        "opencode-cli": "`part.cost` summed across steps (USD); copilot provider = uses Copilot premium",
    }
    for tool in tools:
        ev = [e for e in evals if e.tool == tool]
        n = max(1, len(ev))
        total_prem = sum(e.premium_requests for e in ev)
        total_cost = sum(e.cost_units for e in ev)
        avg_prem = total_prem / n
        note = notes_map.get(tool, "-")
        lines.append(f"| **{tool}** | {total_prem:,} | {total_cost:.2f} | {avg_prem:.1f} | {note} |")
    lines.append("")
    lines.append("> **Note**: OpenCode 의 `cost` 는 USD (provider에 따라 다름). copilot provider 로 실행 시 "
                 "premium request 는 underlying Copilot 백엔드에서 측정되지만 OpenCode stream 에 직접 노출되지 않음 — "
                 "별도 `gh copilot status` 또는 GitHub 대시보드에서 확인 필요.")
    lines.append("")
    lines.append("### 9.3 시나리오별 평균 비용 비교 (per-session)")
    lines.append("")
    lines.append("| Tool | Avg Input Tokens | Avg Output Tokens | Avg Premium/Session | Avg Cost/Session |")
    lines.append("|------|-----------------:|------------------:|--------------------:|-----------------:|")
    for tool in tools:
        ev = [e for e in evals if e.tool == tool]
        n = max(1, len(ev))
        avg_in = sum(e.input_tokens for e in ev) / n
        avg_out = sum(e.output_tokens for e in ev) / n
        avg_pr = sum(e.premium_requests for e in ev) / n
        avg_co = sum(e.cost_units for e in ev) / n
        lines.append(f"| **{tool}** | {int(avg_in):,} | {int(avg_out):,} | {avg_pr:.1f} | {avg_co:.3f} |")
    lines.append("")
    lines.append("### 9.4 추정 비용 — 도구별 차등 적용 (실제 / 역산 / 무료)")
    lines.append("")
    lines.append("> **Pricing 출처**: `config.yaml` 의 `pricing:` 섹션 (편집 가능). 검증은 각 provider 대시보드 (§9.5).")
    lines.append("")
    lines.append("**도구별 산정 로직**:")
    lines.append("- `claude-code` → Anthropic API direct: token × per-million rate (input/output/cache)")
    lines.append("- `copilot-cli` → Premium Request **(actual)**: stream의 `requests.count` × $/req")
    lines.append("- `cursor-cli` (sonnet/opus 모델) → Anthropic rates proxy (Cursor 자체는 구독제이나 token 사용량을 동일 모델 기준으로 환산)")
    lines.append("- `cursor-cli` (**auto 모델**) → **$0** (Cursor 구독 정액 한도 내 무료)")
    lines.append("- `opencode-cli` (copilot provider) → Premium Request **(estimated)**: copilot-cli의 `tokens/req` 비율로 역산")
    lines.append("")

    # Calibration info
    cop_total_tok = sum(e.input_tokens + e.output_tokens for e in evals if e.tool == "copilot-cli" and e.premium_requests > 0)
    cop_total_prem = sum(e.premium_requests for e in evals if e.tool == "copilot-cli" and e.premium_requests > 0)
    if cop_total_prem > 0:
        tpr = cop_total_tok / cop_total_prem
        lines.append(f"> **OpenCode 역산 calibration**: {cop_total_tok:,} (copilot-cli input+output tokens) ÷ "
                     f"{cop_total_prem:,} (premium reqs) = **{tpr:,.0f} tokens/req** ← 이 비율로 opencode premium req 추정")
        lines.append("")

    lines.append("**도구별 종합 비용 + 토큰 + Premium Request 정보** (30 sessions 합계):")
    lines.append("")
    lines.append("| Tool | Total Input | Total Output | Cache Read | Premium Req (actual / estimated) | Total USD | Avg USD/sess | Cost Basis |")
    lines.append("|------|------------:|-------------:|-----------:|----------------------------------:|----------:|-------------:|-----------|")
    for tool in tools:
        ev = [e for e in evals if e.tool == tool]
        n = max(1, len(ev))
        ti = sum(e.input_tokens for e in ev)
        to = sum(e.output_tokens for e in ev)
        tcr = sum(e.cache_read_tokens for e in ev)
        total_premium_actual = sum(e.premium_requests for e in ev)
        total_premium_est = sum(e.estimated_premium_requests for e in ev)
        prem_display = (
            f"{total_premium_actual:,} (actual)" if total_premium_actual > 0
            else f"~{total_premium_est:,.0f} (est)" if total_premium_est > 0
            else "—"
        )
        total_usd = sum(e.estimated_usd for e in ev)
        basis_counts: dict = {}
        for e in ev:
            basis_counts[e.cost_basis] = basis_counts.get(e.cost_basis, 0) + 1
        basis_primary = max(basis_counts, key=basis_counts.get) if basis_counts else "?"
        lines.append(
            f"| **{tool}** | {ti:,} | {to:,} | {tcr:,} | {prem_display} | "
            f"${total_usd:.4f} | ${total_usd/n:.4f} | `{basis_primary}` |"
        )
    lines.append("")
    lines.append("**Per-session 평균 (보다 직관적인 비교용)**:")
    lines.append("")
    lines.append("| Tool | Avg Input | Avg Output | Avg Cache Read | Avg Premium Req | Avg USD/session |")
    lines.append("|------|----------:|-----------:|---------------:|----------------:|----------------:|")
    for tool in tools:
        ev = [e for e in evals if e.tool == tool]
        n = max(1, len(ev))
        ai = sum(e.input_tokens for e in ev) / n
        ao = sum(e.output_tokens for e in ev) / n
        ac = sum(e.cache_read_tokens for e in ev) / n
        prem_actual = sum(e.premium_requests for e in ev) / n
        prem_est = sum(e.estimated_premium_requests for e in ev) / n
        prem_avg = prem_actual if prem_actual > 0 else prem_est
        prem_suffix = " (actual)" if prem_actual > 0 else (" (est)" if prem_est > 0 else "")
        avg_usd = sum(e.estimated_usd for e in ev) / n
        lines.append(
            f"| **{tool}** | {int(ai):,} | {int(ao):,} | {int(ac):,} | "
            f"{prem_avg:.1f}{prem_suffix} | ${avg_usd:.4f} |"
        )
    lines.append("")
    # Cursor caveat — auto sessions are free
    cursor_auto_sessions = sum(1 for e in evals
                                if e.tool == "cursor-cli" and "auto" in (e.model or "").lower())
    if cursor_auto_sessions > 0:
        lines.append(f"> ⚠ **Cursor 의 {cursor_auto_sessions} 세션**이 'auto' 모델로 실행되어 USD $0 으로 처리됨 "
                     f"(Cursor 구독 정액 내 무료). 실제 한도 소진은 cursor.com/dashboard 에서 확인.")
        lines.append("")
    lines.append("### 9.5 외부 Provider Usage Dashboard / API (ground-truth 검증용)")
    lines.append("")
    lines.append("| Provider | Dashboard (web) | API endpoint | CLI command |")
    lines.append("|----------|-----------------|--------------|-------------|")
    lines.append("| **Anthropic** | https://console.anthropic.com/settings/usage | `GET /v1/organizations/{org}/usage_report/messages` (admin only) | (interactive `/usage` only) |")
    lines.append("| **GitHub Copilot (personal)** | https://github.com/settings/copilot/usage | (user-level API not public) | — |")
    lines.append("| **GitHub Copilot (org)** | https://github.com/organizations/`<ORG>`/settings/copilot/usage | `GET /orgs/{org}/copilot/usage` (admin) | `gh api /orgs/<ORG>/copilot/usage` |")
    lines.append("| **Cursor** | https://cursor.com/dashboard | (no public usage API) | `agent status` (auth only) |")
    lines.append("| **OpenCode** | — | — | `opencode stats [--days N] [--models]` |")
    lines.append("")
    lines.append("> **권장 검증 절차**: 분석기 추정 USD 와 provider 대시보드 실제 사용량을 라운드 단위로 비교 → "
                 "큰 차이 발생 시 `config.yaml` 의 `pricing:` 값을 조정.")
    lines.append("")
    lines.append("> **`opencode stats` 활용**: OpenCode 의 경우 `opencode stats --days 7 --models` 로 "
                 "정확한 토큰/USD 사용량을 도구 자체에서 받을 수 있음 (가장 정확). 다른 도구는 분석기 추정 + 외부 대시보드 교차 검증 필요.")
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
    lines.append("Overall = 0.40 × Compliance + 0.30 × Quality + 0.25 × Verdict + 2.5(START) + 2.5(DONE)")
    lines.append("```")
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
        "execution_score", "overall_score",
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
