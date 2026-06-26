"""Produce Markdown + JSON + CSV + HTML reports from aggregated evaluations."""

from __future__ import annotations

import csv
import html as html_mod
import json
import re
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .aggregate import (
    GROUP_KEYS,
    SessionEval,
    _is_env_failure,
    aggregate_per_group_tool,
    aggregate_per_round_tool,
    aggregate_per_scenario_tool,
    aggregate_per_tool,
    aggregate_per_round_scenario_tool,
)
from .bias_check import analyze_bias


def render_no_done_causes(evals, *, heading_level: int = 2) -> str:
    """Render a per-tool breakdown of no-DONE causes (T4). Empty causes (sessions
    WITH DONE) are excluded — this section is only about sessions WITHOUT it."""
    from collections import Counter
    h = "#" * heading_level
    per_tool = {}
    for ev in evals:
        cause = getattr(ev, "no_done_cause", "")
        if cause:
            per_tool.setdefault(ev.tool, Counter())[cause] += 1
    if not per_tool:
        return f"{h} no-DONE 원인 분류\n\n_없음 (전 세션이 DONE 발행)_\n"
    lines = [
        f"{h} no-DONE 원인 분류",
        "",
        "| 도구 | env-rate-limit | env-cert | env-model-refresh-timeout | sentinel-omission | incomplete-planstop |",
        "|------|---:|---:|---:|---:|---:|",
    ]
    for tool, c in sorted(per_tool.items()):
        lines.append(
            f"| {tool} | {c.get('env-rate-limit',0)} | {c.get('env-cert',0)} "
            f"| {c.get('env-model-refresh-timeout',0)} "
            f"| {c.get('sentinel-omission',0)} | {c.get('incomplete-planstop',0)} |"
        )
    lines += [
        "",
        "> **env-***: 환경결함 (채점 제외·재실행 대상). "
        "**sentinel-omission**: 작업 완료·DONE 마커 누락 (codex 흔함). "
        "**incomplete-planstop**: 실제 미완성 (모델이 plan→실행 경계에서 종료).",
        "",
    ]
    return "\n".join(lines)


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


def _discover_comparison_axes(profile: dict) -> Dict[str, List[Dict[str, str]]]:
    """Walk ``study_profile['groups']`` and derive pairwise comparison axes.

    Returns a dict with three keys ``thinking`` / ``model`` / ``combined``.
    Each value is a list of pair definitions ``{a, b, label_a, label_b, subtitle}``.

    Axis rules (auto-discovered, no hardcoded labels):
        thinking → same backend, mode NT vs TH
        model    → same mode, backend pairwise
        combined → both mode and backend differ (one direction only,
                   alphabetical-pair to dedupe)
    Empty lists mean the dataset does not provide that axis (e.g. a single
    backend sweep has no model axis), which lets the caller skip the heading
    entirely.
    """
    groups = profile.get("groups", {}) or {}
    by_pair: Dict[Tuple[str, str], str] = {}
    for name, info in groups.items():
        m = (info or {}).get("thinking_mode", "") or ""
        b = (info or {}).get("backend_model", "") or ""
        if m and b:
            by_pair[(m, b)] = name

    axes: Dict[str, List[Dict[str, str]]] = {
        "thinking": [],
        "model": [],
        "combined": [],
    }

    # Thinking axis — same backend, NT vs TH.
    for b in sorted({bb for (_, bb) in by_pair}):
        nt = by_pair.get(("NT", b))
        th = by_pair.get(("TH", b))
        if nt and th:
            axes["thinking"].append({
                "axis": "thinking",
                "a": nt,
                "b": th,
                "label_a": f"NT/{b}",
                "label_b": f"TH/{b}",
                "subtitle": f"backend `{b}` — NT → TH",
            })

    # Model axis — same mode, backend pairwise.
    for mode in sorted({m for (m, _) in by_pair}):
        backends = sorted([b for (m2, b) in by_pair if m2 == mode])
        for i, ba in enumerate(backends):
            for bb in backends[i + 1:]:
                ga = by_pair.get((mode, ba))
                gb = by_pair.get((mode, bb))
                if ga and gb:
                    axes["model"].append({
                        "axis": "model",
                        "a": ga,
                        "b": gb,
                        "label_a": f"{mode}/{ba}",
                        "label_b": f"{mode}/{bb}",
                        "subtitle": f"{mode} mode — `{ba}` → `{bb}`",
                    })

    # Combined axis — both mode and backend differ. One direction per
    # unordered pair (sorted by group name) so the list does not double up.
    items = sorted(by_pair.items())
    for i, ((ma, ba), ga) in enumerate(items):
        for (mb, bb), gb in items[i + 1:]:
            if ma != mb and ba != bb:
                axes["combined"].append({
                    "axis": "combined",
                    "a": ga,
                    "b": gb,
                    "label_a": f"{ma}/{ba}",
                    "label_b": f"{mb}/{bb}",
                    "subtitle": f"`{ma}/{ba}` → `{mb}/{bb}`",
                })

    return axes


def _emit_axis_delta_table(
    block: List[str],
    pair: Dict[str, str],
    per_group: dict,
    tools: List[str],
) -> None:
    """Emit one ΔOverall/ΔCompl/ΔQual/ΔExec/ΔRunn delta table for one axis pair."""
    ga, gb = pair["a"], pair["b"]
    la, lb = pair["label_a"], pair["label_b"]

    rows: List[Tuple[str, ...]] = []
    for tool in tools:
        a_data = per_group.get((ga, tool))
        b_data = per_group.get((gb, tool))
        if not a_data or not b_data:
            continue

        def _d(key: str, a=a_data, b=b_data) -> str:
            try:
                return f"{(float(b.get(key, 0) or 0) - float(a.get(key, 0) or 0)):+.1f}"
            except (TypeError, ValueError):
                return "—"

        rows.append((
            tool,
            f"{(a_data.get('avg_overall_score', 0) or 0):.1f}",
            f"{(b_data.get('avg_overall_score', 0) or 0):.1f}",
            _d("avg_overall_score"),
            _d("avg_compliance_pct"),
            _d("avg_quality_score"),
            _d("avg_execution_score"),
            _d("avg_runnability_score"),
            f"{a_data.get('sessions', 0)}/{b_data.get('sessions', 0)}",
        ))

    block.append(f"#### {pair['subtitle']}  (`{ga}` → `{gb}`)")
    block.append("")
    if not rows:
        block.append("> _데이터 없음 (도구가 두 그룹 모두에 sessions 없음)._")
        block.append("")
        return
    block.append(
        f"| Tool | {la} Overall | {lb} Overall | ΔOverall | ΔCompl | ΔQual | ΔExec | ΔRunn | Sessions (A/B) |"
    )
    block.append("|------|---:|---:|---:|---:|---:|---:|---:|:---:|")
    for r in rows:
        block.append(
            f"| **{r[0]}** | {r[1]} | {r[2]} | **{r[3]}** | {r[4]} | {r[5]} | {r[6]} | {r[7]} | {r[8]} |"
        )
    block.append("")


def _emit_dynamic_group_rank(
    block: List[str],
    evals: List[SessionEval],
    profile: dict,
) -> bool:
    """Emit per-group tool ranking. Returns True if anything was emitted.

    Skipped automatically for single-tool sweeps (ranking of 1 is noise) and
    when the discovered groups dict is empty.
    """
    if profile.get("is_single_tool"):
        return False
    groups = profile.get("groups", {}) or {}
    if not groups:
        return False

    per_group = aggregate_per_group_tool(evals)
    medals = ["🥇", "🥈", "🥉", "4", "5"]
    block.append("### 그룹별 도구 순위 (자동 발견된 그룹)")
    block.append("")
    block.append(
        "> 각 (mode × backend) 그룹의 도구 ranking. 단일 도구 sweep이면 본 절은 생략됩니다."
    )
    block.append("")
    for g_name, g_info in groups.items():
        rs = (g_info or {}).get("rounds", []) or []
        rs_disp = f"R{min(rs)}–R{max(rs)}" if rs else "—"
        backend = (g_info or {}).get("backend_model", "") or "—"
        mode = (g_info or {}).get("thinking_mode", "") or "—"
        block.append(
            f"#### `{g_name}` — {rs_disp} (backend `{backend}`, mode `{mode}`)"
        )
        block.append("")

        rows = []
        for (gn, tool), data in per_group.items():
            if gn != g_name:
                continue
            rows.append({
                "tool": tool,
                "overall": float(data.get("avg_overall_score", 0) or 0),
                "exec": float(data.get("avg_execution_score", 0) or 0),
                "runn": float(data.get("avg_runnability_score", 0) or 0),
                "sessions": int(data.get("sessions", 0) or 0),
            })
        if not rows:
            block.append("> _데이터 없음._")
            block.append("")
            continue
        rows.sort(key=lambda r: r["overall"], reverse=True)
        block.append("| Rank | Tool | Overall | ExecutionTrace | Runnability | Sessions |")
        block.append("|:----:|------|--------:|---------------:|------------:|--------:|")
        for i, r in enumerate(rows):
            medal = medals[i] if i < len(medals) else str(i + 1)
            block.append(
                f"| {medal} | **{r['tool']}** | **{r['overall']:.1f}** "
                f"| {r['exec']:.1f} | {r['runn']:.1f} | {r['sessions']} |"
            )
        block.append("")
    return True


def _compute_dynamic_findings(
    axes: Dict[str, List[Dict[str, str]]],
    per_group: dict,
    tools: List[str],
) -> List[str]:
    """Extract deterministic findings from per_group data + discovered axes.

    All findings are derived from the axes dict (no hardcoded sonnet/opus/codex
    labels). Returns a list of markdown bullet strings (without leading dash).
    """
    out: List[str] = []

    def _delta(pair: Dict[str, str], tool: str, key: str = "avg_overall_score") -> Optional[float]:
        a = per_group.get((pair["a"], tool))
        b = per_group.get((pair["b"], tool))
        if not a or not b:
            return None
        try:
            return float(b.get(key, 0) or 0) - float(a.get(key, 0) or 0)
        except (TypeError, ValueError):
            return None

    # 1) Largest |ΔOverall| across all axes/tools
    largest: Optional[Tuple[float, str, str, Dict[str, str]]] = None
    for axis_name in ("thinking", "model", "combined"):
        for pair in axes.get(axis_name, []):
            for t in tools:
                d = _delta(pair, t)
                if d is None:
                    continue
                if largest is None or abs(d) > abs(largest[0]):
                    largest = (d, t, axis_name, pair)
    if largest:
        d, t, ax_name, pair = largest
        out.append(
            f"**가장 큰 효과**: `{t}` × {ax_name} axis "
            f"(`{pair['a']}` → `{pair['b']}`) 에서 ΔOverall **{d:+.1f}**."
        )

    # 2) Per-axis consistency check (sign agreement across pairs/tools)
    for axis_name in ("thinking", "model"):
        pairs = axes.get(axis_name, [])
        if not pairs:
            continue
        deltas: List[float] = []
        for pair in pairs:
            for t in tools:
                d = _delta(pair, t)
                if d is not None:
                    deltas.append(d)
        if not deltas:
            continue
        pos = sum(1 for d in deltas if d > 1.0)
        neg = sum(1 for d in deltas if d < -1.0)
        avg = sum(deltas) / len(deltas)
        if pos and neg == 0:
            out.append(
                f"**{axis_name} 효과 일관**: 모든 비교 pair에서 ΔOverall > +1.0 "
                f"(평균 {avg:+.1f}, {pos}/{len(deltas)} positive)."
            )
        elif neg and pos == 0:
            out.append(
                f"**{axis_name} 효과 음의 일관**: 모든 비교 pair에서 ΔOverall < -1.0 "
                f"(평균 {avg:+.1f}, {neg}/{len(deltas)} negative)."
            )
        elif pos and neg:
            out.append(
                f"**{axis_name} 효과 혼합**: pair마다 방향 다름 "
                f"({pos} positive, {neg} negative, |Δ|<1.0 제외; 평균 {avg:+.1f})."
            )

    # 3) thinking 효과 vs model 효과 상대 크기 (per tool)
    th_pairs = axes.get("thinking", [])
    md_pairs = axes.get("model", [])
    if th_pairs and md_pairs:
        for t in tools:
            th_max = max(
                (abs(_delta(p, t) or 0) for p in th_pairs),
                default=None,
            )
            md_max = max(
                (abs(_delta(p, t) or 0) for p in md_pairs),
                default=None,
            )
            if th_max is None or md_max is None:
                continue
            if th_max <= 0 and md_max <= 0:
                continue
            if md_max > th_max * 1.3:
                out.append(
                    f"**`{t}`: model 업그레이드 효과 > thinking 효과** "
                    f"(|Δ|max model = {md_max:.1f}, thinking = {th_max:.1f})."
                )
            elif th_max > md_max * 1.3:
                out.append(
                    f"**`{t}`: thinking 효과 > model 업그레이드 효과** "
                    f"(|Δ|max thinking = {th_max:.1f}, model = {md_max:.1f})."
                )
    return out


def append_group_sections_to_md(
    md_path: Path,
    evals: List[SessionEval],
) -> bool:
    """Append a deterministic, study_profile-driven group block to a md file.

    The block is built **entirely from the discovered study_profile**:

    * per-group tool rank — only when the sweep covers more than one tool
    * Thinking axis — pairs of (NT, TH) discovered for the same backend
    * Model axis    — pairs of backends discovered for the same mode
    * Combined axis — pairs where both mode and backend differ
    * findings      — derived from the axes themselves (LLM-free)

    If none of those produce any rows (single-group sweep with no comparable
    axis) the function emits nothing and returns False. This is what makes
    ``--insights off`` plus a degenerate sweep produce a clean analysis.md /
    insights.md without opinionated group rollups.

    All sub-section headings are plain (no §3.5/§3.6/… numbering) so they
    don't conflict with whatever main-doc numbering the caller uses.
    """
    from .aggregate import build_study_profile

    if not evals:
        return False
    profile = build_study_profile(evals)
    axes = _discover_comparison_axes(profile)
    per_group = aggregate_per_group_tool(evals)
    tools = profile.get("tools") or sorted({e.tool for e in evals})

    sub_blocks: List[str] = []

    # 1) Per-group tool rank (multi-tool sweeps only).
    rank_block: List[str] = []
    if _emit_dynamic_group_rank(rank_block, evals, profile):
        sub_blocks.extend(rank_block)

    # 2) Axis-based delta tables. Skip a whole axis when it has no pair.
    axis_titles = {
        "thinking": "### 그룹 비교 — Thinking 효과",
        "model":    "### 그룹 비교 — 모델 등급 효과 (mode 고정)",
        "combined": "### 그룹 비교 — 종합 효과 (mode + model 동시 변경, 참고용)",
    }
    for axis_name in ("thinking", "model", "combined"):
        pairs = axes.get(axis_name, [])
        if not pairs:
            continue
        sub_blocks.append(axis_titles[axis_name])
        sub_blocks.append("")
        for pair in pairs:
            _emit_axis_delta_table(sub_blocks, pair, per_group, tools)

    # 3) Deterministic findings derived from axes.
    findings = _compute_dynamic_findings(axes, per_group, tools)
    if findings:
        sub_blocks.append("### 핵심 발견 (정량 그룹 비교)")
        sub_blocks.append("")
        for line in findings:
            sub_blocks.append(f"- {line}")
        sub_blocks.append("")
        sub_blocks.append(
            "> 본 발견은 분석기가 ``per_group_tool`` + 자동 도출된 axes 에서 추출한 "
            "결정론적 결과입니다 (LLM 미사용)."
        )
        sub_blocks.append("")

    if not sub_blocks:
        # Nothing emit-worthy. Don't even drop the wrapper header.
        return False

    block: List[str] = [
        "",
        "---",
        "",
        "## 그룹 비교 (자동 집계)",
        "",
        "> 본 섹션은 ``study_profile``에서 자동 발견된 (mode × backend_model) 그룹과 "
        "그들 사이의 비교 가능한 axis만 emit합니다. 발견되지 않은 axis는 출력되지 않습니다. "
        "모든 수치는 ``per_group_tool`` 결정론적 집계 (LLM 미사용).",
        "",
    ]
    block.extend(sub_blocks)
    md_path.write_text(
        md_path.read_text(encoding="utf-8") + "\n".join(block) + "\n",
        encoding="utf-8",
    )
    return True


def _classify_group(e: SessionEval) -> str:
    """Return the canonical group key for an eval (NT_opus48 / TH_sonnet / …).

    Falls back to "—" when no predicate in GROUP_KEYS matches (typically when
    mode or backend_model is missing on legacy manifests).
    """
    for group_name, predicate in GROUP_KEYS.items():
        if predicate(e):
            return group_name
    return "—"


def _round_group_boundaries(
    evals: List[SessionEval],
    rounds: List[int],
) -> List[Tuple[str, List[int]]]:
    """Walk ``rounds`` in order and return contiguous-same-group runs.

    Example: ``[(TH_opus46, [1,2,3,4,5]), (NT_opus46, [6,7,8,9,10]), ...]``.
    Assumes a round's group is consistent across its sessions (the e2e runner
    keeps mode/backend_model fixed within a round). The first eval encountered
    for each round wins; rounds with no evals get group "—".
    """
    round_to_group: Dict[int, str] = {}
    for e in evals:
        if e.round_index not in round_to_group:
            round_to_group[e.round_index] = _classify_group(e)
    boundaries: List[Tuple[str, List[int]]] = []
    current_group: Optional[str] = None
    current_runs: List[int] = []
    for r in rounds:
        g = round_to_group.get(r, "—")
        if g == current_group:
            current_runs.append(r)
        else:
            if current_runs:
                boundaries.append((current_group or "—", current_runs))
            current_group = g
            current_runs = [r]
    if current_runs:
        boundaries.append((current_group or "—", current_runs))
    return boundaries


def _emit_round_output_dirs_collapsible(
    lines: List[str],
    evals: List[SessionEval],
    rounds: List[int],
    tools: List[str],
) -> None:
    """Append a hidden-by-default <details> block listing per (round, tool)
    summary statistics and the session symlink directory.

    Two-row layout per entry (raw HTML so we can use rowspan/colspan):
      Row 1: Round | Tool | Score | Group | Comp % | Qual % | Exec % | Runn %
      Row 2 (colspan=4 under the first 4 rowspan'd cells):
             Session 디렉토리  (results/<run_id>/<session_id>/)

    Score columns are the average across the 6 scenarios of that round/tool.
    """
    # (round, tool) -> running aggregates
    bucket: Dict[Tuple[int, str], Dict[str, object]] = {}
    for e in evals:
        if not e.result_session_dir:
            continue
        key = (e.round_index, e.tool)
        slot = bucket.setdefault(key, {
            "dir": e.result_session_dir,
            "n": 0,
            "group": _classify_group(e),
            "overall": 0.0,
            "comp": 0.0,
            "qual": 0.0,
            "exec": 0.0,
            "runn": 0.0,
        })
        slot["overall"] += float(e.overall_score or 0)
        slot["comp"]    += float(e.compliance_score_pct or 0)
        slot["qual"]    += float(e.quality_score or 0)
        slot["exec"]    += float(e.execution_score or 0)
        slot["runn"]    += float(e.runnability_score or 0)
        slot["n"]       += 1
    if not bucket:
        return
    lines.append("<details>")
    lines.append("<summary>📁 라운드별 results 디렉토리 (session symlink) — 클릭하여 펼치기</summary>")
    lines.append("")
    lines.append("<table>")
    lines.append("<thead>")
    lines.append(
        "<tr>"
        "<th>Round</th><th>Tool</th><th>Score</th><th>Group</th>"
        "<th>Comp %</th><th>Qual %</th><th>Exec %</th><th>Runn %</th>"
        "</tr>"
    )
    lines.append("</thead>")
    lines.append("<tbody>")
    for r in rounds:
        for tool in tools:
            slot = bucket.get((r, tool))
            if not slot:
                continue
            n = slot["n"] or 1
            avg_overall = slot["overall"] / n
            avg_comp = slot["comp"] / n
            avg_qual = slot["qual"] / n
            avg_exec = slot["exec"] / n
            avg_runn = slot["runn"] / n
            # Row 1 — first 4 cells span both rows; metric cells only here
            lines.append(
                f'<tr>'
                f'<td rowspan="2">R{r}</td>'
                f'<td rowspan="2"><code>{tool}</code></td>'
                f'<td rowspan="2">{_fmt_num(avg_overall)}</td>'
                f'<td rowspan="2"><code>{slot["group"]}</code></td>'
                f'<td>{_fmt_num(avg_comp)}</td>'
                f'<td>{_fmt_num(avg_qual)}</td>'
                f'<td>{_fmt_num(avg_exec)}</td>'
                f'<td>{_fmt_num(avg_runn)}</td>'
                f'</tr>'
            )
            # Row 2 — session symlink directory under colspan
            lines.append(
                f'<tr><td colspan="4"><small>'
                f'<strong>Session 디렉토리</strong>: <code>{slot["dir"]}</code>'
                f'</small></td></tr>'
            )
    lines.append("</tbody>")
    lines.append("</table>")
    lines.append("")
    lines.append("</details>")
    lines.append("")


def _emit_scenario_output_dirs_collapsible(
    lines: List[str],
    evals: List[SessionEval],
    scenario: str,
    rounds: List[int],
    tools: List[str],
) -> None:
    """Per-scenario collapsible — listed under each §4 verdict subsection.

    Three-row HTML layout per (round, tool) entry:
      Row 1: Round (rs=3) | Tool | Score | Group | Model · Exec · Runn · Comp · Qual
      Row 2: Duration · S/D · pytest · ToolCalls · LOC · PH · Eng · Reason  (colspan=4)
      Row 3: Symlink + 실제 경로  (colspan=4)

    Row 1 first column (Round) spans all 3 rows so the entry is visually a
    single block. Row 2 / Row 3 receive a colspan=4 cell that covers the
    Tool/Score/Group/Detail columns.
    """
    # (round, tool) -> SessionEval (first match per (round, tool, scenario))
    bucket: Dict[Tuple[int, str], SessionEval] = {}
    for e in evals:
        if e.scenario != scenario:
            continue
        if not e.result_scenario_dir and not e.output_dirs:
            continue
        bucket.setdefault((e.round_index, e.tool), e)
    if not bucket:
        return
    verdict_emoji = {"PASS": "✅", "PARTIAL": "🟡", "FAIL": "❌", "UNKNOWN": "❓"}
    lines.append("<details>")
    lines.append(f"<summary>📁 {scenario} — 라운드별 results 디렉토리 (펼치기)</summary>")
    lines.append("")
    lines.append("<table>")
    lines.append("<thead>")
    lines.append(
        "<tr>"
        "<th>Round</th><th>Tool</th><th>Score</th><th>Group</th>"
        "<th>Exec %</th><th>Runn %</th><th>Comp %</th><th>Qual %</th>"
        "</tr>"
    )
    lines.append("</thead>")
    lines.append("<tbody>")
    for r in rounds:
        for tool in tools:
            e = bucket.get((r, tool))
            if e is None:
                continue
            score_cell = (
                f"{verdict_emoji.get(e.verdict, '')} {_fmt_num(e.overall_score)}".strip()
            )
            group_disp = _classify_group(e)
            sd_marker = ("✓" if e.has_start else "✗") + "/" + ("✓" if e.has_done else "✗")
            pytest_disp = str(e.exit_status) if e.exit_status is not None else "-"
            runn_disp = _fmt_num(e.runnability_score) if e.runnability_score > 0 else "-"
            reason = (e.verdict_reason or "").strip() or "—"
            sym_cell = (
                f"<code>{e.result_scenario_dir}</code>" if e.result_scenario_dir else "—"
            )
            abs_cell = (
                "<br>".join(f"<code>{d}</code>" for d in e.output_dirs)
                if e.output_dirs else "—"
            )
            # Row 1 — 8 cells (Round rowspan=3 covers row 2/3 first column)
            lines.append(
                f'<tr>'
                f'<td rowspan="3">R{r}</td>'
                f'<td><code>{tool}</code></td>'
                f'<td>{score_cell}</td>'
                f'<td><code>{group_disp}</code></td>'
                f'<td>{_fmt_num(e.execution_score)}</td>'
                f'<td>{runn_disp}</td>'
                f'<td>{_fmt_num(e.compliance_score_pct)}</td>'
                f'<td>{_fmt_num(e.quality_score)}</td>'
                f'</tr>'
            )
            # Row 2 — runtime / volume / failure context (colspan=7 covers
            # everything except the rowspan'd Round cell).
            row2_detail = " · ".join([
                f"<strong>Duration</strong>: {_fmt_duration(e.duration_sec)}",
                f"<strong>S/D</strong>: {sd_marker}",
                f"<strong>pytest</strong>: {pytest_disp}",
                f"<strong>ToolCalls</strong>: {e.tool_call_count}",
                f"<strong>LOC</strong>: {e.python_loc}",
                f"<strong>PH</strong>: {e.placeholder_hits}",
                f"<strong>Eng</strong>: {e.direct_engine_use}",
                f"<strong>Reason</strong>: {reason}",
            ])
            lines.append(
                f'<tr><td colspan="7"><small>{row2_detail}</small></td></tr>'
            )
            # Row 3 — paths (symlink + resolved abs)
            row3_paths = (
                f"<strong>Symlink</strong>: {sym_cell}<br>"
                f"<strong>실제 경로</strong>: {abs_cell}"
            )
            lines.append(
                f'<tr><td colspan="7"><small>{row3_paths}</small></td></tr>'
            )
    lines.append("</tbody>")
    lines.append("</table>")
    lines.append("")
    lines.append("</details>")
    lines.append("")


def write_markdown(evals: List[SessionEval], out_path: Path, meta: Dict) -> None:
    per_tool = aggregate_per_tool(evals)
    per_rt = aggregate_per_round_tool(evals)
    per_st = aggregate_per_scenario_tool(evals)
    per_rst = aggregate_per_round_scenario_tool(evals)

    tools = sorted({e.tool for e in evals})
    rounds = sorted({e.round_index for e in evals})
    scenarios = sorted({e.scenario for e in evals})

    lines: List[str] = []
    lines.append(f"# DEEPX Agent-Driven Development — E2E Autopilot 분석 리포트")
    lines.append("")
    lines.append(f"> 생성 시각: {meta.get('generated_at')}  ·  Rubric: **{meta.get('rubric_version', 'v1')}** (시나리오별 ExecutionTrace + Overall 가중치 v2)")
    lines.append(f"> 분석 대상 sessions: **{len(evals)}** "
                 f"({len(tools)} tools × {len(rounds)} rounds × {len(scenarios)} scenarios)")
    lines.append(f"> Results root: `{meta.get('results_root')}`")
    lines.append("")
    if meta.get("caveats"):
        lines.append("## ⚠️ 주의 사항")
        for c in meta["caveats"]:
            lines.append(f"- {c}")
        lines.append("")
    lines.append("## 📖 점수 산정 방식 (Quick Reference, Rubric v2)")
    lines.append("")
    lines.append("Overall 가중치는 시나리오별로 다릅니다 (v2):")
    lines.append("")
    lines.append("| 시나리오 | Compliance | Quality | ExecutionTrace | Runnability |")
    lines.append("|---|---:|---:|---:|---:|")
    lines.append("| compiler | 30% | 15% | **35%** | 20% |")
    lines.append("| dx_app / dx_stream / dx_stream_cascaded | 30% | 20% | 25% | **25%** |")
    lines.append("| runtime | 30% | 20% | 25% | **25%** |")
    lines.append("| suite | 30% | 15% | **35%** | 20% |")
    lines.append("")
    lines.append("- **Compliance** = HARD GATE 통과율 (sentinel START/DONE, output isolation, mandatory deliverables, IFactory, session_log authentic, suite dual dirs). runtime 시나리오에서 `session_log_authentic`은 soft-warning으로 강등 (multi-domain 라우팅 특성상 단일 session.log가 부자연스러움).")
    lines.append("- **Quality** = py_compile + JSON parse + bash -n 통과율, placeholder/anti-pattern 페널티. 코드 생성 본질 시나리오(dx_app/dx_stream/cascaded)에서 비중↑.")
    lines.append("- **ExecutionTrace (v2)** = 시나리오별 컴포넌트 (각 시나리오 만점 합 100): compiler는 dxnn artifact size + compile evidence 중심, dx_app은 factory_smoke_test + inference 흔적, dx_stream은 pipeline.dot/video + gst element 사용, runtime은 dx_app/dx_stream 양 sub-project 독립 평가, suite는 compile artifact + app-consumes-dxnn chain.")
    lines.append("- **Runnability** = End-user가 README/setup.sh/run.sh 따라 실제 실행 가능한지 LLM 판정. runtime에서 비중↑ (cross-domain end-user가 핵심).")
    lines.append("- **Verdict** (정보용) = 산출물 PASS/PARTIAL/FAIL 판정 — 점수 미반영, 시각화 참조용.")
    lines.append("- **Exit 0 %** = pytest 라운드 전체 exit 코드 (라운드 단위). Overall 미반영.")
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
                _env_rounds = sorted({e.round_index for e in el})
                rounds_str = ", ".join(f"R{r}" for r in _env_rounds)
                lines.append(f"| {t} | {len(el)} | {rounds_str} |")
            lines.append("")

    # no-DONE 원인 분류 — placed right after the env-failure exclusion block
    lines.append(render_no_done_causes(evals, heading_level=3))
    lines.append("")

    # Compute scenario-level pass/fail aggregates per tool (scored only)
    scored_evals = [e for e in evals if not is_env_failure_eval(e)]
    pass_per_tool = {t: sum(1 for e in scored_evals if e.tool == t and e.verdict == "PASS") for t in tools}
    partial_per_tool = {t: sum(1 for e in scored_evals if e.tool == t and e.verdict == "PARTIAL") for t in tools}
    fail_per_tool = {t: sum(1 for e in scored_evals if e.tool == t and e.verdict == "FAIL") for t in tools}
    # Build rows sorted by overall score for ranking
    _tool_rows_s1 = []
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
        overall = float(m.get('avg_overall_score', 0) or 0)
        _tool_rows_s1.append((tool, overall, m, sessions_display, verdict_avg, exec_avg,
                              runn_display, ppf, timeouts))
    _tool_rows_s1.sort(key=lambda x: x[1], reverse=True)

    # --- Table A: Overall 점수 구성 요소 (점수에 직접 반영되는 컬럼) ---
    lines.append("### 1-A. Overall 점수 구성 요소")
    lines.append("")
    lines.append("| Rank | Tool | Scored/Total | Compl % | Qual % | Exec % | Runn % | **Overall %** | σ(Overall) |")
    lines.append("|-----:|------|------------:|-------:|------:|------:|------:|----------:|----------:|")
    _medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    for _rank, (tool, _ov, m, sessions_display, verdict_avg, exec_avg,
                runn_display, ppf, timeouts) in enumerate(_tool_rows_s1, 1):
        medal = _medals.get(_rank, str(_rank))
        lines.append(
            f"| {medal} | **{tool}** | {sessions_display} | "
            f"{_fmt_num(m.get('avg_compliance_pct'))} | "
            f"{_fmt_num(m.get('avg_quality_score'))} | "
            f"{_fmt_num(exec_avg)} | "
            f"{runn_display} | "
            f"**{_fmt_num(m.get('avg_overall_score'))}** | "
            f"{_fmt_num(m.get('stdev_overall_score'))} |"
        )
    lines.append("")
    lines.append("> Overall % = 0.30·Compl + 0.20·Qual + 0.30·Exec + 0.20·Runn. "
                 "**σ** = stdev (낮을수록 일관성이 높음). **Exec %** = ExecutionTrace 점수 (실제 명령 실행 흔적). "
                 "**Scored/Total** = 점수 산정 포함 세션 / 전체 세션 (환경 실패 제외).")
    lines.append("")

    # --- Table B: 정보성 지표 (Overall 점수에 미반영) ---
    lines.append("### 1-B. 정보성 지표 (참고용, Overall 미반영)")
    lines.append("")
    lines.append("| Tool | START % | DONE % | Verdict % | Pass/Part/Fail | pytest Exit0 % | ⏱ Timeout | Avg Duration | ToolCalls | LOC |")
    lines.append("|------|--------:|-------:|----------:|:--------------:|---------------:|----------:|-------------:|---------:|----:|")
    for _rank, (tool, _ov, m, sessions_display, verdict_avg, exec_avg,
                runn_display, ppf, timeouts) in enumerate(_tool_rows_s1, 1):
        lines.append(
            f"| **{tool}** | "
            f"{_fmt_num(m.get('pct_with_start_sentinel'))} | "
            f"{_fmt_num(m.get('pct_with_done_sentinel'))} | "
            f"{_fmt_num(verdict_avg)} | "
            f"{ppf} | "
            f"{_fmt_num(m.get('pct_exit_0'))} | "
            f"{timeouts} | "
            f"{_fmt_duration(m.get('avg_duration_sec'))} | "
            f"{_fmt_num(m.get('avg_tool_calls'))} | "
            f"{int(m.get('avg_python_loc', 0))} |"
        )
    lines.append("")
    lines.append("> **START/DONE %** = sentinel 준수율 (Compliance %에 이미 반영됨). "
                 "**Verdict %** = PASS/PARTIAL/FAIL 산출물 판정 (Overall 미반영, 정보용). "
                 "**⏱ Timeout** = 의심 timeout 발생 세션 수. **pytest Exit0 %** = 라운드 단위 exit 코드 (시나리오 단위 ≠).")
    lines.append("")

    # ----------------------------------------------------------
    # 2. 평가 메트릭 해설 + 시나리오별 데이터 (§5+§10 통합)
    # ----------------------------------------------------------
    lines.append("## 2. 평가 메트릭 해설 및 시나리오별 세분화")
    lines.append("")
    lines.append("> 각 메트릭의 정의와 측정 방법을 설명한 뒤, 바로 도구 × 시나리오별 데이터를 제시합니다.")
    lines.append("")

    header2 = "| Rank | Tool | " + " | ".join(scenarios) + " | 평균 |"
    sep2 = "|-----:|------|" + "|".join(":-----:" for _ in scenarios) + "|-----:|"

    # lower_is_better metrics for ranking direction
    _lower_better_metrics = {"avg_duration_sec", "pct_fail"}

    def _metric_table(title: str, metric: str, fmt=_fmt_num):
        """Emit a ranked scenario × tool table with a sub-header."""
        lines.append(f"##### {title}")
        lines.append("")
        lines.append(header2)
        lines.append(sep2)
        _trows = []
        for tool in tools:
            cells = []
            vals = []
            for sc in scenarios:
                m = per_st.get((sc, tool))
                v = m.get(metric) if m else None
                cells.append(fmt(v) if v is not None else "-")
                if v is not None:
                    vals.append(float(v))
            avg = sum(vals) / len(vals) if vals else 0.0
            _trows.append((tool, cells, avg))
        reverse = metric not in _lower_better_metrics
        _trows.sort(key=lambda x: x[2], reverse=reverse)
        _m5 = {1: "🥇", 2: "🥈", 3: "🥉"}
        for rank, (tool, cells, avg) in enumerate(_trows, 1):
            medal = _m5.get(rank, str(rank))
            lines.append(f"| {medal} | **{tool}** | " + " | ".join(cells) + f" | {fmt(avg)} |")
        lines.append("")

    # --- 2.1 Overall % ---
    lines.append("### 2.1 Overall % (종합 점수)")
    lines.append("")
    lines.append("```")
    lines.append("Overall = 0.30×Compliance + 0.20×Quality + 0.30×ExecutionTrace + 0.20×Runnability")
    lines.append("```")
    lines.append("")
    lines.append("- Runnability 데이터가 없는 세션은 나머지 3-factor 비례 배분 (backward compatible)")
    lines.append("- Verdict는 Compliance mandatory_deliverables와 중복이므로 점수 미반영 (정보용 매트릭스만 표시)")
    lines.append("")
    _metric_table("Overall %", "avg_overall_score")

    # NOTE: Per-group (A/B/C) tool rankings were previously emitted here as
    # §2.1, but moved to ``append_group_sections_to_md`` so that group-level
    # comparisons only appear when the insights step runs (and reflect the
    # actual groups discovered in the data instead of a hardcoded layout).

    # --- 2.2 Compliance % ---
    lines.append("### 2.2 Compliance % (HARD GATE 체크 통과율, 가중치 30%)")
    lines.append("")
    lines.append("- `sentinel_start` — 응답 첫 줄 `[DX-AGENT-DEV: START]`")
    lines.append("- `sentinel_done` — 마지막 줄 `[DX-AGENT-DEV: DONE (output-dir: ...)]`")
    lines.append("- `output_isolation_present` — 산출물이 `dx-agent-dev/<session_id>/` 하위")
    lines.append("- `session_id_format` — `YYYYMMDD-HHMMSS_<agent>_<model>_<task>` 패턴")
    lines.append("- `mandatory_deliverables` — 시나리오별 필수 파일 존재 (setup.sh, run.sh, README.md, session.log, factory, *_sync.py 등)")
    lines.append("- `ifactory_5_methods` — dx_app factory 5-method 패턴")
    lines.append("- `session_log_authentic` — session.log 가 hand-written heredoc 아님")
    lines.append("- `suite_dual_session_dirs` — suite 시나리오에서 2개 별도 sub-project dir 생성 (R41 HARD GATE)")
    lines.append("")
    _metric_table("Compliance %", "avg_compliance_pct")

    # --- 2.3 Quality % ---
    lines.append("### 2.3 Quality % (정적 코드 품질, 가중치 20%)")
    lines.append("")
    lines.append("- 모든 `.py` 파일 `py_compile` → 통과율")
    lines.append("- 모든 `.json` 파일 `json.load` → 통과율")
    lines.append("- 모든 `.sh` 파일 `bash -n` → 통과율")
    lines.append("- **Placeholder** 페널티: `# TODO: implement`, 주석된 import, `np.zeros(...)` 등 (hit 당 5점, cap 30)")
    lines.append("- **Direct engine use** 페널티: factory 외부 `engine.run()` — HARD GATE 위반 (hit 당 5점, cap 15)")
    lines.append("")
    _metric_table("Quality %", "avg_quality_score")

    # Note: Verdict %는 §1-B 와 §4 매트릭스에서 이미 제공됨.
    # 별도 §2.4 평균 표는 Compliance.mandatory_deliverables 와 측정 대상이
    # 중복되고, §4 매트릭스가 raw label 을 그대로 보여주므로 제거.

    # --- 2.4 ExecutionTrace % ---
    lines.append("### 2.4 ExecutionTrace % (실제 실행 흔적, 가중치 30%)")
    lines.append("")
    lines.append("- session.log substantive (실질적 내용 포함)")
    lines.append("- 성공 마커 존재 (compile success, inference output 등)")
    lines.append("- .dxnn realistic size (>1KB)")
    lines.append("- no failure markers (traceback, error 등)")
    lines.append("")
    # Compute scenario-level execution avg ad-hoc
    exec_avg_per_scen_tool = {}
    for sc in scenarios:
        for tool in tools:
            evals_st = [e for e in evals if e.scenario == sc and e.tool == tool]
            n = max(1, len(evals_st))
            exec_avg_per_scen_tool[(sc, tool)] = sum(e.execution_score for e in evals_st) / n

    lines.append(header2)
    lines.append(sep2)
    _exec_rows = []
    for tool in tools:
        cells = []
        vals = []
        for sc in scenarios:
            v = exec_avg_per_scen_tool.get((sc, tool), 0.0)
            cells.append(_fmt_num(v))
            vals.append(v)
        avg = sum(vals) / len(vals) if vals else 0.0
        _exec_rows.append((tool, cells, avg))
    _exec_rows.sort(key=lambda x: x[2], reverse=True)
    _m5x = {1: "🥇", 2: "🥈", 3: "🥉"}
    for rank, (tool, cells, avg) in enumerate(_exec_rows, 1):
        medal = _m5x.get(rank, str(rank))
        lines.append(f"| {medal} | **{tool}** | " + " | ".join(cells) + f" | {_fmt_num(avg)} |")
    lines.append("")

    # --- 2.5 Runnability % ---
    lines.append("### 2.5 Runnability % (End-user 실행 가능성, 가중치 20%)")
    lines.append("")
    lines.append("- End-user가 README/setup.sh/run.sh 따라 실제 실행 가능한지 LLM 판정")
    lines.append("- PASS(100)/PARTIAL(50)/FAIL(0) + 세부 1-5점 스케일")
    lines.append("- `runnability_report.md` 없으면 나머지 3-factor 비례 배분")
    lines.append("")
    # Build runnability per scenario×tool
    runn_per_scen_tool = {}
    for sc in scenarios:
        for tool in tools:
            evals_st = [e for e in evals if e.scenario == sc and e.tool == tool and e.runnability_score > 0]
            if evals_st:
                runn_per_scen_tool[(sc, tool)] = sum(e.runnability_score for e in evals_st) / len(evals_st)
            else:
                runn_per_scen_tool[(sc, tool)] = None

    lines.append(header2)
    lines.append(sep2)
    _runn_rows = []
    for tool in tools:
        cells = []
        vals = []
        for sc in scenarios:
            v = runn_per_scen_tool.get((sc, tool))
            cells.append(_fmt_num(v) if v is not None else "-")
            if v is not None:
                vals.append(float(v))
        avg = sum(vals) / len(vals) if vals else 0.0
        _runn_rows.append((tool, cells, avg))
    _runn_rows.sort(key=lambda x: x[2], reverse=True)
    for rank, (tool, cells, avg) in enumerate(_runn_rows, 1):
        medal = _m5x.get(rank, str(rank))
        lines.append(f"| {medal} | **{tool}** | " + " | ".join(cells) + f" | {_fmt_num(avg)} |")
    lines.append("")

    # --- 2.6 보조 메트릭 ---
    lines.append("### 2.6 보조 메트릭 (Overall 점수에 미반영)")
    lines.append("")
    lines.append("#### Duration (실행 시간)")
    lines.append("")
    lines.append("- Claude Code: `result.duration_ms` (stream-json 최종 이벤트)")
    lines.append("- Cursor: `result` event 의 `duration_ms`")
    lines.append("- OpenCode: `timestamp` (Unix ms) 첫/마지막 이벤트 차이")
    lines.append("- Copilot: events-*.jsonl 의 첫/마지막 이벤트 timestamp")
    lines.append("- Fallback: artifact + output dir 파일 mtime 의 최대-최소 차이")
    lines.append("")
    _metric_table("Avg Duration", "avg_duration_sec", _fmt_duration)

    lines.append("#### Tool Calls & Python LOC")
    lines.append("")
    _metric_table("Avg Tool Calls", "avg_tool_calls")
    _metric_table("Avg Python LOC", "avg_python_loc")

    lines.append("#### Tool Calls Efficiency Index")
    lines.append("")
    lines.append("단순 tool call 수는 효율을 직접 나타내지 않습니다. "
                 "적은 호출이 높은 성공률과 결합될 때만 의미 있습니다.")
    lines.append("")
    lines.append("```")
    lines.append("Efficiency Index = (Compliance% × ExecutionTrace%) / (Tool Calls + 1) × 100")
    lines.append("```")
    lines.append("")
    # Compute efficiency and rank
    from .bias_check import _avg as _bias_avg
    by_tool_evals = {t: [e for e in evals if e.tool == t] for t in tools}
    eff_data = []
    for tool in tools:
        tc = _bias_avg([e.tool_call_count for e in by_tool_evals[tool]])
        comp = _bias_avg([e.compliance_score_pct for e in by_tool_evals[tool]])
        exec_p = _bias_avg([e.execution_score for e in by_tool_evals[tool]])
        eff = (comp * exec_p) / (tc + 1) * 100
        eff_data.append((tool, tc, comp, exec_p, eff))
    eff_data.sort(key=lambda x: x[4], reverse=True)

    lines.append("| Rank | Tool | Avg Tool Calls | Avg Compl % | Avg Exec % | **Efficiency Index** |")
    lines.append("|-----:|------|---------------:|------------:|-----------:|---------------------:|")
    for rank, (tool, tc, comp, exec_p, eff) in enumerate(eff_data, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, str(rank))
        lines.append(f"| {medal} | **{tool}** | {tc:.1f} | {comp:.1f} | {exec_p:.1f} | **{eff:.1f}** |")
    lines.append("")
    lines.append("> **해석 유의사항**: tool call 당 작업 granularity는 도구마다 다릅니다 "
                 "(Claude Code는 1 Bash에 multi-line 명령을 묶고, Copilot/OpenCode는 개별 호출로 분해). "
                 "따라서 Efficiency Index는 도구 간 상대 비교보다 동일 도구 내 회차별 추세 파악에 더 적합합니다.")
    lines.append("")

    lines.append("#### pytest Exit 0 %")
    lines.append("")
    lines.append("- pytest 의 round-level exit code (한 라운드에 6개 시나리오; 그 중 한 assertion 실패 시 1)")
    lines.append("- **Overall 점수에는 미반영** (라운드 단위 → 시나리오 단위로 분해 불가). 별도 컬럼으로 표시.")
    lines.append("- 진정한 시나리오별 pass/fail 은 Verdict 컬럼이 더 정확.")
    lines.append("")

    # ----------------------------------------------------------
    # 3. 회차별 추이
    # ----------------------------------------------------------
    lines.append("## 3. 도구별 회차별 추이")
    lines.append("")
    header = "| Rank | Tool | " + " | ".join(f"R{r}" for r in rounds) + " | 평균 |"
    sep = "|-----:|------|" + "|".join(":-----:" for _ in rounds) + "|-----:|"

    def _ranked_round_rows(metric_key, fmt=_fmt_num):
        """Compute per-tool rows with averages, return sorted by avg descending."""
        _rows = []
        for tool in tools:
            row_cells = []
            sum_v, count_v = 0.0, 0
            for r in rounds:
                m = per_rt.get((r, tool))
                v = m.get(metric_key) if m else None
                row_cells.append(fmt(v) if v is not None else "-")
                if v is not None:
                    sum_v += float(v)
                    count_v += 1
            avg = sum_v / count_v if count_v else 0.0
            _rows.append((tool, row_cells, avg))
        _rows.sort(key=lambda x: x[2], reverse=True)
        return _rows

    _medals_rt = {1: "🥇", 2: "🥈", 3: "🥉"}

    lines.append("### 3.1 Overall %")
    lines.append("")
    rows_s2 = _ranked_round_rows("avg_overall_score")
    # Raw HTML table with a group-name banner row using colspan over the
    # rounds that share the same (mode × backend_model) group. The data row
    # cells are reused verbatim from _ranked_round_rows (already markdown-
    # free numeric strings).
    _boundaries = _round_group_boundaries(evals, rounds)
    lines.append("<table>")
    lines.append("<thead>")
    _group_row = '<tr><th rowspan="2">Rank</th><th rowspan="2">Tool</th>'
    for _g, _rs in _boundaries:
        _group_row += f'<th colspan="{len(_rs)}">{_g}</th>'
    _group_row += '<th rowspan="2">평균</th></tr>'
    lines.append(_group_row)
    lines.append('<tr>' + ''.join(f'<th>R{r}</th>' for r in rounds) + '</tr>')
    lines.append("</thead>")
    lines.append("<tbody>")
    for rank, (tool, cells, avg) in enumerate(rows_s2, 1):
        medal = _medals_rt.get(rank, str(rank))
        _row = f'<tr><td>{medal}</td><td><strong>{tool}</strong></td>'
        for c in cells:
            _row += f'<td>{c}</td>'
        _row += f'<td>{_fmt_num(avg)}</td></tr>'
        lines.append(_row)
    lines.append("</tbody>")
    lines.append("</table>")
    lines.append("")
    _emit_round_output_dirs_collapsible(lines, evals, rounds, tools)

    lines.append("### 3.2 Compliance %")
    lines.append("")
    rows_s3 = _ranked_round_rows("avg_compliance_pct")
    lines.append(header)
    lines.append(sep)
    for rank, (tool, cells, avg) in enumerate(rows_s3, 1):
        medal = _medals_rt.get(rank, str(rank))
        lines.append(f"| {medal} | **{tool}** | " + " | ".join(cells) + f" | {_fmt_num(avg)} |")
    lines.append("")

    # Sub-metric tables (§3.3-3.5) — same per-round-per-tool ranking layout as
    # Compliance, using the new aggregate keys. Each is sorted by row average
    # descending so the best tool ranks first.
    for _sub_title, _metric_key in [
        ("### 3.3 Quality %",        "avg_quality_score"),
        ("### 3.4 ExecutionTrace %", "avg_execution_score"),
        ("### 3.5 Runnability %",    "avg_runnability_score"),
    ]:
        lines.append(_sub_title)
        lines.append("")
        _rows_sub = _ranked_round_rows(_metric_key)
        lines.append(header)
        lines.append(sep)
        for rank, (tool, cells, avg) in enumerate(_rows_sub, 1):
            medal = _medals_rt.get(rank, str(rank))
            lines.append(f"| {medal} | **{tool}** | " + " | ".join(cells) + f" | {_fmt_num(avg)} |")
        lines.append("")

    lines.append("### 3.6 Avg Duration")
    lines.append("")
    _dur_rows = []
    for tool in tools:
        row_cells = []
        sum_v, count_v = 0.0, 0
        for r in rounds:
            m = per_rt.get((r, tool))
            v = m.get("avg_duration_sec") if m else None
            row_cells.append(_fmt_duration(v) if v is not None else "-")
            if v is not None:
                sum_v += float(v)
                count_v += 1
        avg_dur = sum_v / count_v if count_v else 9999.0
        m_tool = per_tool.get(tool, {})
        _dur_rows.append((tool, row_cells, avg_dur, m_tool.get('avg_duration_sec')))
    _dur_rows.sort(key=lambda x: x[2])  # ascending — faster is better
    lines.append(header)
    lines.append(sep)
    for rank, (tool, cells, _ad, avg_dur_raw) in enumerate(_dur_rows, 1):
        medal = _medals_rt.get(rank, str(rank))
        lines.append(
            f"| {medal} | **{tool}** | " + " | ".join(cells) +
            f" | {_fmt_duration(avg_dur_raw)} |"
        )
    lines.append("")

    # NOTE: Group comparison sections (§3.5/§3.6/§3.7 Thinking/Model/Combined,
    # §3.8 Opus 4.8 axes, §3.9 핵심 발견) used to be emitted right here but
    # were moved into ``append_group_sections_to_md`` so they only appear
    # alongside the insights step. Running with ``--insights off`` therefore
    # produces a strictly quantitative analysis.md with no opinionated group
    # rollups.

    # ----------------------------------------------------------
    # 4. Verdict 매트릭스
    # ----------------------------------------------------------
    lines.append("## 4. 회차 × 시나리오 × 도구 — Verdict 매트릭스")
    lines.append("")
    verdict_emoji = {"PASS": "✅", "PARTIAL": "🟡", "FAIL": "❌", "UNKNOWN": "❓"}
    _boundaries_v = _round_group_boundaries(evals, rounds)
    for sc in scenarios:
        lines.append(f"### {sc}")
        lines.append("")
        lines.append("<table>")
        lines.append("<thead>")
        _group_row = '<tr><th rowspan="2">Tool</th>'
        for _g, _rs in _boundaries_v:
            _group_row += f'<th colspan="{len(_rs)}">{_g}</th>'
        _group_row += '</tr>'
        lines.append(_group_row)
        lines.append('<tr>' + ''.join(f'<th>R{r}</th>' for r in rounds) + '</tr>')
        lines.append("</thead>")
        lines.append("<tbody>")
        for tool in tools:
            _row = f'<tr><td><strong>{tool}</strong></td>'
            for r in rounds:
                m = per_rst.get((r, sc, tool))
                if m:
                    _row += f'<td>{verdict_emoji.get(m["verdict"], "?")} {_fmt_num(m["overall_score"])}</td>'
                else:
                    _row += '<td>-</td>'
            _row += '</tr>'
            lines.append(_row)
        lines.append("</tbody>")
        lines.append("</table>")
        lines.append("")
        _emit_scenario_output_dirs_collapsible(lines, evals, sc, rounds, tools)

    # ----------------------------------------------------------
    # 5. FAIL 분석
    # ----------------------------------------------------------
    lines.append("## 5. 회차별 FAIL Verdict 카운트")
    lines.append("")
    _fail_header = "| Rank | Tool | " + " | ".join(f"R{r}" for r in rounds) + " | 합계 |"
    _fail_sep = "|-----:|------|" + "|".join(":-----:" for _ in rounds) + "|-----:|"
    lines.append(_fail_header)
    lines.append(_fail_sep)
    _fail_rows = []
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
        _fail_rows.append((tool, row_cells, total_fail))
    _fail_rows.sort(key=lambda x: x[2])  # ascending — fewer fails is better
    _mf = {1: "🥇", 2: "🥈", 3: "🥉"}
    for rank, (tool, row_cells, total_fail) in enumerate(_fail_rows, 1):
        medal = _mf.get(rank, str(rank))
        lines.append(f"| {medal} | **{tool}** | " + " | ".join(row_cells) + f" | **{total_fail}** |")
    lines.append("")

    # ----------------------------------------------------------
    # 6. 토큰 사용량 + 비용 효율성 (핵심 → 배경 순)
    # ----------------------------------------------------------
    lines.append("## 6. 토큰 사용량 + 비용 효율성")
    lines.append("")

    # --- 6.1 비용 대비 성능 종합 판단 (핵심 → 상단) ---
    lines.append("### 6.1 비용 대비 성능 종합 판단")
    lines.append("")
    lines.append("아래는 당사 구독 형태, 도구 사용 방법, E2E 테스트 결과를 종합한 비용 현황입니다. "
                 "**일관된 기준의 도구 간 비용 비교는 현실적으로 불가능**하므로, 현황 데이터만 제시합니다.")
    lines.append("")

    # Compute tool overall scores
    tool_overall = {}
    for tool in tools:
        ev = [e for e in evals if e.tool == tool]
        scored = [e for e in ev if not _is_env_failure(e)]
        if scored:
            tool_overall[tool] = sum(e.overall_score for e in scored) / len(scored)
        else:
            tool_overall[tool] = 0.0

    # --- Group A: Copilot Provider (PR 기반) ---
    lines.append("#### A. Copilot Provider 사용 도구 (PR 단위 과금)")
    lines.append("")
    lines.append("copilot-cli, opencode-cli, codex-cli는 GitHub Copilot backend를 사용하며, "
                 "초과 사용 시 Premium Request 단위로 과금됩니다.")
    lines.append("")

    copilot_tools = ["copilot-cli", "opencode-cli", "codex-cli"]
    # Method 1 (tool_call × 0.741) is calibrated against copilot-cli's observed
    # totalPremiumRequests and tracks it within ~15% — used as the primary
    # ranking basis. Method 2 (token ratio) is shown only for reference.
    # Efficiency = Overall / PR (higher = more score per premium request).
    rows = []
    for tool in copilot_tools:
        if tool not in tools:
            continue
        ev = [e for e in evals if e.tool == tool]
        n = max(1, len(ev))
        ov = tool_overall.get(tool, 0)
        total_obs = sum(e.premium_requests for e in ev)
        avg_obs = total_obs / n if total_obs > 0 else 0.0
        avg_tc  = sum(e.pr_by_tool_call   for e in ev) / n
        avg_tr  = sum(e.pr_by_token_ratio for e in ev) / n
        eff_tc  = (ov / avg_tc) if avg_tc > 0 else 0.0
        eff_tr  = (ov / avg_tr) if avg_tr > 0 else 0.0
        rows.append((tool, ov, avg_obs, avg_tc, eff_tc, avg_tr, eff_tr))

    # Rank by efficiency under method 1 (primary)
    rows.sort(key=lambda r: r[4], reverse=True)
    medals = ["🥇", "🥈", "🥉"]

    lines.append(
        "| Rank | 도구 | E2E Overall | 관측 PR | 예측 1: tool_call × 0.741 | "
        "효율 (Overall ÷ 예측 1) | 참고: 예측 2 (token ratio) | 참고: 효율 (Overall ÷ 예측 2) |"
    )
    lines.append(
        "|:----:|------|----------:|--------:|-----------------:|----------------------:|"
        "----------------:|----------------------:|"
    )
    for i, (tool, ov, avg_obs, avg_tc, eff_tc, avg_tr, eff_tr) in enumerate(rows, 1):
        rank = medals[i - 1] if i <= len(medals) else str(i)
        cell_obs = f"{avg_obs:.1f}" if avg_obs > 0 else "—"
        cell_tc  = f"{avg_tc:.1f}"  if avg_tc > 0  else "—"
        cell_ef1 = f"{eff_tc:.2f}"  if eff_tc > 0  else "—"
        cell_tr  = f"{avg_tr:.1f}"  if avg_tr > 0  else "—"
        cell_ef2 = f"{eff_tr:.2f}"  if eff_tr > 0  else "—"
        lines.append(
            f"| {rank} | **{tool}** | {ov:.1f} | {cell_obs} | {cell_tc} | "
            f"**{cell_ef1}** | {cell_tr} | {cell_ef2} |"
        )
    lines.append("")
    lines.append(
        "> **랭킹 기준**: 예측 1(tool_call × 0.741) 기반의 '효율' 컬럼(Overall ÷ PR) 내림차순. "
        "값이 클수록 한 PR(Premium Request)당 더 높은 Overall 점수를 만든다는 의미. "
        "**예측 1**은 copilot-cli 관측치와 자릿수 일치(±15%) 입증된 calibrated ratio라 "
        "agent-driven 도구에서 가장 신뢰성 있는 비교 기준입니다. "
        "**예측 2(token ratio)** 와 그 효율 컬럼은 참고용 — 도구별 token 보고 의미론이 달라 "
        "자릿수 변동이 큽니다 (§6.4 참조). "
        "copilot-cli는 `session.shutdown.totalPremiumRequests` 실측을 제공하지만, opencode/codex는 "
        "stream에 PR 미노출이라 예측에 의존합니다."
    )
    lines.append("")

    # --- Group B: 정액 구독 (한도 내) ---
    lines.append("#### B. 정액 구독 도구 (한도 내 사용)")
    lines.append("")
    fixed_tools = ["claude-code", "cursor-cli"]
    lines.append("| 도구 | E2E Overall | 과금 체계 | 비고 |")
    lines.append("|------|----------:|---------|------|")
    for tool in fixed_tools:
        if tool not in tools:
            continue
        ov = tool_overall.get(tool, 0)
        if tool == "claude-code":
            lines.append(f"| **{tool}** | {ov:.1f} | Anthropic Team Plan 정액 | 세션/주간 한도 내 사용, 추가 비용 없음 |")
        elif tool == "cursor-cli":
            lines.append(f"| **{tool}** | {ov:.1f} | Cursor Team Plan 정액 | auto 모델 한도 내, 초과 시 제한됨 |")
    lines.append("")
    lines.append("> **결론**: 정액 구독 도구는 토큰 사용량과 무관하게 월 고정 비용만 발생하므로, "
                 "**비용 효율성은 '동일 구독 한도 내에서 더 많은 성공적 세션을 완료하는가'로 판단**하는 것이 적절합니다. "
                 "E2E Overall Score가 이 기준에 가장 가까운 지표입니다.")
    lines.append("")

    # --- 6.2 Premium Request 예측 방법론 ---
    lines.append("### 6.2 Premium Request 측정 및 예측 방법론")
    lines.append("")
    lines.append("#### 관측 현황")
    lines.append("")
    lines.append("| 도구 | PR 관측 가능 여부 | 방식 |")
    lines.append("|------|:--------------:|------|")
    lines.append("| **copilot-cli** | ✅ 가능 | `session.shutdown.totalPremiumRequests` (정확도 이슈 있음 — [#1764](https://github.com/github/copilot-cli/issues/1764)) |")
    lines.append("| **opencode-cli** | ❌ 불가 | stream에 PR 정보 미노출 |")
    lines.append("| **codex-cli** | ❌ 불가 | stream에 PR 정보 미노출 |")
    lines.append("")
    lines.append("> 참고: claude-code (Anthropic Team Plan), cursor-cli (Cursor Team Plan)는 PR 개념이 없는 정액 구독입니다.")
    lines.append("")
    lines.append("#### 예측 공식 1순위 — tool_call × 0.741 (calibrated)")
    lines.append("")
    lines.append("agent-driven 도구는 한 번의 사용자 프롬프트 안에서 수십 회의 LLM round-trip을 "
                 "발생시킵니다. GitHub의 청구도 round-trip 단위로 누적되므로, **세션의 tool_call 수**를 "
                 "PR 예측 지표로 사용하는 것이 자연스럽습니다.")
    lines.append("")
    lines.append("copilot-cli의 실측 데이터(관측 PR / tool_call 비율)로 calibration ratio를 산출:")
    lines.append("")
    lines.append("```")
    lines.append("TOOL_CALL_PR_RATIO ≈ 0.741   # = 5232 PR / 7061 tool_calls (copilot-cli 실측)")
    lines.append("estimated_PR = tool_call_count × TOOL_CALL_PR_RATIO")
    lines.append("```")
    lines.append("")
    lines.append("이 방식은 copilot 관측치(38.7)와 자릿수 일치(~41, ±15%)를 보이며, "
                 "동일 backend의 opencode/codex에도 일관성 있게 적용됩니다.")
    lines.append("")
    lines.append("#### 예측 공식 2순위 — token ratio (fallback)")
    lines.append("")
    lines.append("tool_call_count가 0인 예외 세션을 위해 token-ratio 역산을 보조로 둡니다:")
    lines.append("")
    lines.append("```")
    lines.append("calibration_ratio = copilot-cli 총 (input+output) tokens / 총 premium requests")
    lines.append("estimated_PR = (input+output) tokens / calibration_ratio")
    lines.append("```")
    lines.append("")
    lines.append("> ⚠ **한계**: 도구별 token 보고 의미론이 다르기 때문에 자릿수 변동이 큽니다. "
                 "tool_call 신호가 있는 모든 세션은 1순위 공식을 사용하며, fallback은 1% 미만 케이스에서만 사용됩니다.")
    lines.append("")
    lines.append("#### 참고 — copilot-cli 관측 PR의 USD 단가 (multiplier 적용 대상)")
    lines.append("")
    lines.append("copilot-cli의 실측 PR 수치에 USD를 부여할 때 모델별 multiplier가 적용됩니다 "
                 "(예측치 계산에는 사용되지 않음).")
    lines.append("")
    lines.append("#### 예측 2순위 — token ratio 역산 (fallback)")
    lines.append("")
    lines.append("#### 향후 개선 계획")
    lines.append("")
    lines.append("1. copilot-bridge 프록시 경유 시 opencode/codex의 round-trip별 PR 실측 수집 가능 "
                 "([xjin6/codex-copilot-bridge](https://github.com/xjin6/codex-copilot-bridge))")
    lines.append("2. 2026.06 GitHub Copilot usage-based billing 전환 후 token usage × 단가로 산정 방식 전환 예정")
    lines.append("")
    lines.append("#### ⚠ 2026.06 과금 체계 변경 예정")
    lines.append("")
    lines.append("GitHub는 **request-based → usage-based billing**으로 전환합니다 ([공식 블로그](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)). "
                 "Premium Request Unit(PRU)이 사라지고 **GitHub AI Credits** (input/output/cached token 기반)로 변경되므로, "
                 "이후에는 token usage × 모델 단가로 비용을 산정해야 합니다.")
    lines.append("")
    lines.append("**참고 자료:**")
    lines.append("")
    lines.append("- [GitHub Docs — Requests in GitHub Copilot](https://docs.github.com/en/copilot/concepts/billing/copilot-requests)")
    lines.append("- [GitHub Docs — Models and Pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)")
    lines.append("- [GitHub Blog — Moving to usage-based billing](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)")
    lines.append("- [Monitoring your Copilot usage](https://docs.github.com/copilot/how-tos/monitoring-your-copilot-usage-and-entitlements)")
    lines.append("- [copilot-cli #1764 — Est. 0 Premium requests](https://github.com/github/copilot-cli/issues/1764)")
    lines.append("- [anomalyco/opencode #768 — Tracking Premium Requests](https://github.com/anomalyco/opencode/issues/768)")
    lines.append("- [anomalyco/opencode #14539 — Tool usages consumes premium request](https://github.com/anomalyco/opencode/issues/14539)")
    lines.append("")

    # --- 6.3 Raw token table ---
    n_sessions = len(evals)
    lines.append(f"### 6.3 도구별 누적 토큰 — Raw (전체 {n_sessions} sessions 합계)")
    lines.append("")
    lines.append("> ⚠ **토큰 의미론이 도구별로 다릅니다.** 아래 표의 수치는 각 도구 stream에서 추출한 원본(raw) 값이며, "
                 "직접 비교에는 주의가 필요합니다. 차이 원인은 §6.4에서 설명합니다.")
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

    # --- 6.4 Token semantics ---
    lines.append("### 6.4 도구별 토큰 보고 의미론 차이")
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

    # --- 6.5 External benchmarks ---
    lines.append("### 6.5 외부 벤치마크 기반 모델 비용 효율성 참고")
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

    # --- 6.6 Provider dashboards ---
    lines.append("### 6.6 외부 Provider Usage Dashboard (실제 사용량 검증용)")
    lines.append("")
    lines.append("| Provider | Dashboard | 비고 |")
    lines.append("|----------|-----------|------|")
    lines.append("| **Anthropic** | https://console.anthropic.com/settings/usage | claude-code 실사용량 |")
    lines.append("| **GitHub Copilot** | https://github.com/organizations/`<ORG>`/settings/copilot/usage | copilot-cli PR 소비량 |")
    lines.append("| **Cursor** | https://cursor.com/dashboard | cursor-cli 사용량 |")
    lines.append("")

    # ----------------------------------------------------------
    # 7. 세션별 상세 — 헤더는 목차에 노출, 본문은 <details>로 접어둠.
    # ----------------------------------------------------------
    lines.append("## 7. 세션별 상세")
    lines.append("")
    lines.append(f"> 총 {len(evals)}개 세션. HTML 보고서에서는 접기/펼치기로 제공됩니다.")
    lines.append("")
    lines.append("<details>")
    lines.append("<summary>전체 (클릭하여 펼치기)</summary>")
    lines.append("")
    # Multi-run aggregation: include run_id column when 2+ run_ids are present.
    # Three-row layout per session:
    #   Row 1 — dense numeric metrics
    #   Row 2 — runtime / volume / failure detail (S/D · ToolCalls · LOC ·
    #            PH · Eng · Reason)
    #   Row 3 — copyable Symlink path on its own line
    # The Model column is intentionally absent: ``e.model`` is the config
    # default and the actual backend is already encoded in the Group cell
    # (e.g. ``NT_opus46`` / ``TH_opus48``).
    distinct_run_ids = sorted({e.run_id for e in evals})
    multi_run = len(distinct_run_ids) > 1
    primary_cols = (["Run"] if multi_run else []) + [
        "R", "Tool", "Group", "Scenario", "Verdict",
        "Exec %", "Runn %", "⏱", "pytest", "Duration",
        "Comp %", "Qual %", "Overall %",
    ]
    total_cols = len(primary_cols)
    lines.append("<table>")
    lines.append("<thead>")
    lines.append("<tr>" + "".join(f"<th>{c}</th>" for c in primary_cols) + "</tr>")
    lines.append("</thead>")
    lines.append("<tbody>")
    for e in sorted(evals, key=lambda x: (x.run_id, x.round_index, x.tool, x.scenario)):
        verdict_disp = f"{verdict_emoji.get(e.verdict, '?')} {e.verdict[:4]}"
        sd_marker = ("✓" if e.has_start else "✗") + "/" + ("✓" if e.has_done else "✗")
        timeout_mark = "⏱" if e.suspected_timeout else ""
        runn_disp = _fmt_num(e.runnability_score) if e.runnability_score > 0 else "-"
        group_disp = _classify_group(e)
        symlink_disp = f"<code>{e.result_scenario_dir}</code>" if e.result_scenario_dir else "-"
        pytest_disp = str(e.exit_status) if e.exit_status is not None else "-"
        # Row 1 — dense numeric snapshot (Model column intentionally removed).
        row1 = "<tr>"
        if multi_run:
            row1 += f"<td>{e.run_id}</td>"
        row1 += (
            f"<td>{e.round_index}</td>"
            f"<td>{e.tool}</td>"
            f"<td><code>{group_disp}</code></td>"
            f"<td>{e.scenario}</td>"
            f"<td>{verdict_disp}</td>"
            f"<td>{_fmt_num(e.execution_score)}</td>"
            f"<td>{runn_disp}</td>"
            f"<td>{timeout_mark}</td>"
            f"<td>{pytest_disp}</td>"
            f"<td>{_fmt_duration(e.duration_sec)}</td>"
            f"<td>{_fmt_num(e.compliance_score_pct)}</td>"
            f"<td>{_fmt_num(e.quality_score)}</td>"
            f"<td>{_fmt_num(e.overall_score)}</td>"
            f"</tr>"
        )
        lines.append(row1)
        # Row 2 — runtime / volume / failure detail (no Symlink).
        reason = (e.verdict_reason or "").strip()
        detail_parts = [
            f"<strong>S/D</strong>: {sd_marker}",
            f"<strong>ToolCalls</strong>: {e.tool_call_count}",
            f"<strong>LOC</strong>: {e.python_loc}",
            f"<strong>PH</strong>: {e.placeholder_hits}",
            f"<strong>Eng</strong>: {e.direct_engine_use}",
            f"<strong>Reason</strong>: {reason or '—'}",
        ]
        lines.append(
            f'<tr><td colspan="{total_cols}"><small>'
            + " · ".join(detail_parts)
            + "</small></td></tr>"
        )
        # Row 3 — symlink on its own row so the path can be copied without
        # collateral text in the way.
        lines.append(
            f'<tr><td colspan="{total_cols}"><small>'
            f'<strong>Symlink</strong>: {symlink_disp}'
            f'</small></td></tr>'
        )
    lines.append("</tbody>")
    lines.append("</table>")
    lines.append("")
    lines.append("</details>")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_json(evals: List[SessionEval], out_path: Path, meta: Dict) -> None:
    from .aggregate import build_study_profile
    payload = {
        "meta": meta,
        "study_profile": build_study_profile(evals),
        "per_tool": aggregate_per_tool(evals),
        "per_round_tool": {
            f"R{k[0]}__{k[1]}": v for k, v in aggregate_per_round_tool(evals).items()
        },
        "per_scenario_tool": {
            f"{k[0]}__{k[1]}": v for k, v in aggregate_per_scenario_tool(evals).items()
        },
        "per_group_tool": {
            f"{k[0]}__{k[1]}": v for k, v in aggregate_per_group_tool(evals).items()
        },
        "sessions": [asdict(e) for e in evals],
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(
    evals: List[SessionEval],
    out_path: Path,
    *,
    extra_columns: Optional[List[Tuple[str, Callable[[SessionEval], Any]]]] = None,
) -> None:
    """Write per_session.csv.

    ``extra_columns`` appends additional columns after the base set. Each entry
    is ``(column_name, getter)`` where ``getter(SessionEval) -> Any``. Used to
    surface fields that may not exist on every SessionEval (e.g. PR2's
    ``env_failure_signature`` or T4's ``no_done_cause``) without coupling
    callers to the internal column order.
    """
    columns = [
        "run_id", "round", "tool", "scenario", "model", "verdict", "verdict_score", "verdict_reason",
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
    extras = list(extra_columns or [])
    columns = columns + [name for name, _ in extras]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for e in evals:
            row = {
                "run_id": e.run_id,
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
            }
            for name, getter in extras:
                row[name] = getter(e)
            w.writerow(row)


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
    in_details = False  # track <details> block for §7
    code_lines: List[str] = []
    _heading_counter = [0]

    def _slug(text: str) -> str:
        """Create URL-friendly slug from heading text."""
        clean = re.sub(r'<[^>]+>', '', text)  # strip HTML tags
        clean = re.sub(r'[^\w\s가-힣-]', '', clean)  # keep alphanumeric, Korean, hyphens
        clean = clean.strip().replace(' ', '-').lower()
        _heading_counter[0] += 1
        return f"sec-{_heading_counter[0]}-{clean[:40]}"

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

        # Raw HTML pass-through for <details>/<summary> collapsibles AND
        # raw <table> blocks (used by §3.1 / §4 main tables that need colspan
        # group headers). Tags are emitted verbatim so the browser respects
        # them; markdown content between the tags continues to flow through
        # the normal converter below.
        if re.match(
            r"^</?(details|summary|table|thead|tbody|tfoot|tr|th|td|colgroup|col|caption)\b",
            stripped,
        ):
            if in_table:
                html_parts.append("</tbody></table>")
                in_table = False
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(stripped)
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
                hid = _slug(text)

                # Close previous <details> if a new h2 starts
                if in_details and level <= 2:
                    html_parts.append("</details>")
                    in_details = False

                # Stable cross-document anchors: counter-based IDs change as
                # the report structure evolves, breaking links in
                # _render_summary_extras_from_insights. Emit a stable <a id>
                # alias right before well-known section headings so
                # "#hypothesis-verification" / "#recommendations" stay valid.
                raw = m.group(2).strip()
                if level == 2:
                    if "가설 검증" in raw and "종합" not in raw:
                        html_parts.append('<a id="hypothesis-verification"></a>')
                    elif "향후 운영" in raw and raw.startswith(("8.", "8 ")):
                        html_parts.append('<a id="recommendations"></a>')

                # §7 ("## 7. 세션별 상세") and others all flow through as a
                # regular heading. The collapsing is now done by explicit
                # <details>/<summary> emitted in write_markdown itself, which
                # keeps the heading visible in the sidebar TOC.
                html_parts.append(f'<h{level} id="{hid}">{text}</h{level}>')
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
    if in_details:
        html_parts.append("</details>")
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
    # Restore intentional <br> tokens (used in table cells to stack multiple
    # paths). Escape happens first so any other tags stay as text.
    text = re.sub(r"&lt;br\s*/?&gt;", "<br>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Markdown links: [text](url) → <a href="url">text</a>.
    # Placed AFTER bold/code conversions so that link text containing inline
    # code (e.g. [`dashboard.html`](./dashboard.html)) still renders the
    # <code> tag inside the anchor. Pattern: text = any chars except ']';
    # url = any chars except whitespace and ')'.
    text = re.sub(
        r'\[([^\]]+)\]\(([^)\s]+)\)',
        r'<a href="\2">\1</a>',
        text,
    )
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
    title = "DEEPX Agent-Driven Development — E2E Autopilot Analysis"

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
