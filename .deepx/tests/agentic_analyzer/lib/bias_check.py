"""Cursor (auto-model) bias analysis.

Cursor's 'auto' model is Cursor's proprietary composer LLM, NOT Claude Sonnet 4.6.
This module checks whether any of our metrics are inherently biased in favor of
cursor (e.g., metrics that reward fast/short responses that cursor's lightweight
model produces by design).

Outputs a markdown section that flags potential bias indicators.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def _avg(vals):
    return sum(vals) / max(1, len(vals))


def analyze_bias(evals) -> str:
    """Produce a markdown-formatted bias check report."""
    tools = sorted({e.tool for e in evals})
    by_tool = {t: [e for e in evals if e.tool == t] for t in tools}

    lines: List[str] = []
    lines.append("## 11. Cursor 'auto' 모델 편향 점검 (Q4)")
    lines.append("")
    lines.append("Cursor 의 'auto' 모델은 Cursor 자체 compose LLM 이며 Claude Sonnet 4.6 이 아닙니다. "
                 "다음 지표들에서 cursor 에 유리한 편향이 있을 수 있는지 점검합니다.")
    lines.append("")
    lines.append("### 11.1 메트릭별 도구간 비교")
    lines.append("")
    lines.append("| Metric | claude-code | copilot-cli | cursor-cli | opencode-cli | cursor 편향 가능성 |")
    lines.append("|--------|------------:|------------:|-----------:|-------------:|:----------------:|")

    # Helper to format an average row + suspicion flag
    def _row(name: str, getter, flag_if):
        vals = {t: _avg([getter(e) for e in by_tool[t]]) for t in tools}
        cursor_v = vals.get("cursor-cli", 0)
        # Suspicion = flag_if returns True
        suspicion = flag_if(vals)
        sus_emoji = "⚠️" if suspicion else "—"
        cells = [f"{vals.get(t, 0):.1f}" for t in tools]
        lines.append(f"| {name} | " + " | ".join(cells) + f" | {sus_emoji} |")

    # 1) Duration — cursor faster = neutral (just fact); but very low duration with high score suspicious
    _row("Avg Duration (sec)",
         lambda e: e.duration_sec or 0,
         lambda v: v.get("cursor-cli", 0) < min(v.get("claude-code", 9999),
                                                  v.get("copilot-cli", 9999)) * 0.5)

    # 2) Tool calls — interpret with care (see §11.4)
    _row("Avg Tool Calls",
         lambda e: e.tool_call_count,
         lambda v: False)  # No simple flag — see narrative analysis below

    # 3) Compliance — high → no bias issue (HARD GATE)
    _row("Compliance %",
         lambda e: e.compliance_score_pct,
         lambda v: False)  # high compliance is fine

    # 4) Quality % — same
    _row("Quality %",
         lambda e: e.quality_score,
         lambda v: False)

    # 5) Verdict % — primary deliverable existence
    _row("Verdict %",
         lambda e: e.verdict_score,
         lambda v: False)

    # 6) Python LOC — too low could mean stub-ish code; too high could mean verbose
    _row("Avg Python LOC",
         lambda e: e.python_loc,
         lambda v: v.get("cursor-cli", 0) < min(v.get("claude-code", 9999),
                                                  v.get("copilot-cli", 9999)) * 0.5)

    # 7) Execution Trace — actual command running (independent of agent style)
    _row("Execution Trace %",
         lambda e: e.execution_score,
         lambda v: v.get("cursor-cli", 0) > max(v.get("claude-code", 0),
                                                 v.get("copilot-cli", 0)) * 1.5)

    # 8) Placeholder hits — low is good (clean code)
    _row("Placeholder Hits",
         lambda e: e.placeholder_hits,
         lambda v: False)

    # 9) Direct engine.run() use — HARD GATE violation
    _row("Direct engine.run()",
         lambda e: e.direct_engine_use,
         lambda v: False)

    lines.append("")
    lines.append("### 11.2 분석 결과")
    lines.append("")

    # Per-metric verdict
    cursor_evals = by_tool.get("cursor-cli", [])
    others = [e for t, lst in by_tool.items() for e in lst if t != "cursor-cli"]
    findings: List[str] = []

    # Duration check
    cur_dur = _avg([e.duration_sec or 0 for e in cursor_evals])
    oth_dur = _avg([e.duration_sec or 0 for e in others])
    if cur_dur > 0 and cur_dur < oth_dur * 0.7:
        findings.append(
            f"⚠️ Cursor 의 평균 duration ({cur_dur/60:.1f}m) 이 다른 도구 평균 "
            f"({oth_dur/60:.1f}m) 의 70% 이하 — 자체 compose 모델이 적은 horizon 으로 "
            f"빠르게 응답하는 경향. **fair 비교를 위해 sonnet 4.6 으로 재실행 필요.**"
        )

    # Tool call count — only a flag, NOT "efficiency". See §11.4 below.
    cur_tc = _avg([e.tool_call_count for e in cursor_evals])
    oth_tc = _avg([e.tool_call_count for e in others])
    if cur_tc > 0 and oth_tc > 0 and abs(cur_tc - oth_tc) / max(cur_tc, oth_tc) > 0.2:
        findings.append(
            f"📊 Cursor 의 평균 tool calls ({cur_tc:.0f}/세션) 가 다른 도구 평균 ({oth_tc:.0f}) 와 "
            f"20% 이상 차이 — 직접적 효율 판단 금지 (§11.4 참고)."
        )

    # LOC check (cursor's code shorter or longer?)
    cur_loc = _avg([e.python_loc for e in cursor_evals])
    oth_loc = _avg([e.python_loc for e in others])
    if cur_loc > 0 and oth_loc > 0:
        ratio = cur_loc / oth_loc
        if 0.85 < ratio < 1.15:
            findings.append(
                f"✓ Cursor 의 코드 LOC ({cur_loc:.0f}) 가 다른 도구 ({oth_loc:.0f}) 와 "
                f"비슷한 수준 (±15%) — 코드 분량 측면에서는 편향 없음."
            )
        elif ratio < 0.85:
            findings.append(
                f"⚠️ Cursor 의 코드 LOC ({cur_loc:.0f}) 가 다른 도구 ({oth_loc:.0f}) 의 "
                f"{int(ratio*100)}% — 더 짧은 코드를 생성. stub-ish 가능성 점검 필요."
            )

    # Verdict comparison
    cur_v = _avg([e.verdict_score for e in cursor_evals])
    oth_v = _avg([e.verdict_score for e in others])
    if abs(cur_v - oth_v) < 5:
        findings.append(
            f"✓ Cursor 의 Verdict % ({cur_v:.1f}) 가 타 도구 평균 ({oth_v:.1f}) 과 비슷 — "
            f"산출물 PASS 측면에서 편향 없음 (cursor 가 산출물을 더 자주 PASS 시키는 것은 아님)."
        )

    # Overall score gap
    cur_ov = _avg([e.overall_score for e in cursor_evals])
    oth_ov = _avg([e.overall_score for e in others])
    if cur_ov > oth_ov:
        findings.append(
            f"📊 Cursor 의 Overall ({cur_ov:.1f}) > 타 도구 평균 ({oth_ov:.1f}) — "
            f"우위는 주로 duration/tool calls 효율에서 옴. sonnet 4.6 재실행 후 변화 모니터링 필요."
        )

    if not findings:
        findings.append("관찰된 명확한 편향 없음.")

    for f in findings:
        lines.append(f"- {f}")
    lines.append("")
    lines.append("### 11.3 권장 사항")
    lines.append("")
    lines.append("1. **Sonnet 4.6 으로 재실행**: cursor 가 다른 도구와 동일한 모델로 비교되어야 fair.")
    lines.append("2. **Cursor 의 Execution Trace 가 다른 도구 대비 비슷한 수준**: 산출물 단순 존재가 아닌 실제 실행 흔적까지 비슷하다면 편향 가능성 낮음.")
    lines.append("3. **Duration 가중치 조정 검토**: 만약 cursor 의 우위가 거의 duration 차이에서만 온다면, Overall 에 duration 을 직접 반영하지 않는 현재 가중치 정책이 적절.")
    lines.append("")
    lines.append("### 11.4 'Tool Calls' 메트릭 해석 가이드 (⚠ 효율 ≠ 적은 호출)")
    lines.append("")
    lines.append("**왜 이 섹션이 추가되었나**: 이전 리포트 요약에서 *'tool calls 효율 (58 vs 76) 에서 옴'* 이라는 표현을 사용했습니다. "
                 "이는 **부정확한 해석**이었습니다. 적은 tool call 수가 곧 효율적 작업을 의미하지 않으며, "
                 "오히려 다음 두 가지 상반된 해석이 가능합니다.")
    lines.append("")
    lines.append("**가능한 해석 (Pro)** — 적은 호출이 좋은 경우:")
    lines.append("- 모델이 처음에 정확히 의도를 파악해 fewer trial-and-error")
    lines.append("- planning 이 명확해서 redundant read/grep 이 적음")
    lines.append("- 더 큰 patch 를 한 번에 적용 (다수 작은 edit 대신)")
    lines.append("")
    lines.append("**가능한 해석 (Con)** — 적은 호출이 나쁜 경우:")
    lines.append("- 컨텍스트 검증을 충분히 하지 않음 (e.g., 기존 코드를 안 읽고 추측)")
    lines.append("- 자가-검증을 안 함 (validate_app.py 미실행, 단순히 생성만)")
    lines.append("- 산출물에 대한 self-test/debugging 단계 생략")
    lines.append("")
    lines.append("**메트릭 자체의 한계**:")
    lines.append("- '1 tool call' 의 weight 가 도구마다 다름 (cursor의 한 tool call 이 더 무거운 일을 할 수도 있음)")
    lines.append("- Claude Code 는 `Bash` 한 호출에 multi-line 명령을 묶지만, OpenCode/Copilot 은 multiple 호출로 분해할 수 있음")
    lines.append("- counting 자체에 노이즈: stream-json 의 `tool_call/started + completed` 이중 이벤트 카운팅 (분석기 중복 제거 적용은 했지만 도구 간 정확도 차이는 잔존)")
    lines.append("")
    lines.append("**올바른 평가 방법**:")
    lines.append("- Tool calls 단독으로 효율을 판단 ❌")
    lines.append("- Tool calls × **Verdict (PASS 비율)** × **ExecutionTrace** 조합으로 평가 ✅")
    lines.append("- 즉, *'적은 호출로 더 많은 PASS + 더 풍부한 실행 흔적'* 이 진정한 효율")
    lines.append("")

    # Compute the 'true efficiency' indicator
    lines.append("**복합 효율 지표 (Tool Calls Efficiency Index)**:")
    lines.append("")
    lines.append("```")
    lines.append("Efficiency = (Verdict% × ExecutionTrace%) / (Tool Calls + 1)    × 100 (스케일링)")
    lines.append("            높은 PASS+Execution을 적은 tool call 로 달성할수록 큰 값")
    lines.append("```")
    lines.append("")
    lines.append("| Tool | Avg Tool Calls | Avg Verdict % | Avg Exec % | **Efficiency Index** |")
    lines.append("|------|---------------:|--------------:|-----------:|---------------------:|")
    for tool in tools:
        tc = _avg([e.tool_call_count for e in by_tool[tool]])
        ver = _avg([e.verdict_score for e in by_tool[tool]])
        exec_p = _avg([e.execution_score for e in by_tool[tool]])
        eff = (ver * exec_p) / (tc + 1) * 100  # scaled
        lines.append(f"| **{tool}** | {tc:.1f} | {ver:.1f} | {exec_p:.1f} | **{eff:.1f}** |")
    lines.append("")
    lines.append("→ Efficiency Index 가 가장 높은 도구가 '진정한 효율' 면에서 우위. "
                 "단순 tool call 수 만으로 비교했을 때와 결과가 달라질 수 있음.")
    lines.append("")

    return "\n".join(lines)
