#!/usr/bin/env python3
"""dx-agentic-dev E2E Analyzer — main entry point.

Usage:
    python analyze.py [--results-root PATH] [--config PATH] [--output-dir PATH]
                       [--tool TOOL ...] [--scenario SCEN ...] [--round N ...]

Defaults (when invoked from .deepx/tests/agentic_analyzer/):
    --results-root: <suite-root>/dx-agentic-dev/e2e-tests/results
    --config:       ./config.yaml
    --output-dir:   <suite-root>/dx-agentic-dev/e2e-tests/analyzer_reports/<UTC ts>/

Examples:
    # Analyze all current sessions
    python3 analyze.py

    # Filter to specific tool + round
    python3 analyze.py --tool claude-code copilot-cli --round 1 2 3

    # Custom results location (e.g., after adding 5 more rounds)
    python3 analyze.py --results-root /path/to/more/results

    # Skip auto-invoking insights.py
    python3 analyze.py --insights off
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Allow running from any cwd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def _find_suite_root() -> Path:
    """Walk up from HERE to find dx-all-suite root.
    Marker: presence of both `.deepx/` AND `dx-runtime/` siblings.
    Fallback: HERE.parent.parent.parent (3 levels up from .deepx/tests/agentic_analyzer/).
    """
    p = HERE
    for _ in range(8):
        if (p / ".deepx").is_dir() and (p / "dx-runtime").is_dir():
            return p
        if p.parent == p:
            break
        p = p.parent
    return HERE.parent.parent.parent


SUITE_ROOT = _find_suite_root()
DEFAULT_RESULTS_ROOT = SUITE_ROOT / "dx-agentic-dev" / "e2e-tests" / "results"
DEFAULT_REPORTS_BASE = SUITE_ROOT / "dx-agentic-dev" / "e2e-tests" / "analyzer_reports"

from lib.discover import discover_all, ScenarioRef
from lib.session import parse_session
from lib.compliance import evaluate_compliance
from lib.quality import evaluate_quality
from lib.functional import infer_verdict, verdict_score, count_lines_of_code
from lib.execution import evaluate_execution
from lib.pytest_data import collect_pytest_round
from lib.cost import estimate_cost, compute_calibration_ratios
from lib.aggregate import SessionEval, composite_score
from lib.report import write_markdown, write_json, write_csv, write_html, md_file_to_html
from lib.runnability_parser import parse_runnability_report, aggregate_runnability


def _load_config(path: Path) -> dict:
    """Minimal YAML loader. Try pyyaml first; fall back to a tiny custom parser."""
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError:
        # Fallback: very small parser is risky; require pyyaml.
        print("ERROR: pyyaml not available. Install with: pip install pyyaml",
              file=sys.stderr)
        sys.exit(2)


def _resolve_model(tool: str, session_id: str, config: dict) -> str:
    """Determine the model used for a session by tool/config/overrides."""
    overrides = config.get("model_overrides", []) or []
    for ov in overrides:
        if ov.get("session_id_pattern", "") in session_id:
            return ov.get("model", "unknown")
    return config.get("default_models", {}).get(tool, "unknown")


def evaluate_scenario(ref: ScenarioRef, config: dict) -> SessionEval:
    """Run all per-session evaluators for one ScenarioRef and combine into SessionEval."""
    rules = config.get("compliance_rules", {}) or {}
    scenarios_cfg = config.get("scenarios", {}) or {}
    sd = parse_session(ref)
    comp = evaluate_compliance(ref, sd, scenarios_cfg, rules)

    # Quality: evaluate union over all output dirs (sum file counts, etc.)
    placeholder_hits = 0
    direct_engine = 0
    python_files = 0
    syntax_total = 0
    syntax_ok_total = 0
    loc_python = 0
    loc_bash = 0
    loc_json = 0
    code_files_count = 0
    notes: List[str] = []
    for od in ref.output_dirs:
        q = evaluate_quality(od)
        placeholder_hits += len(q.placeholder_hits)
        direct_engine += len(q.direct_engine_use)
        python_files += q.python_files
        syntax_total += q.python_files + q.json_files + q.bash_files
        syntax_ok_total += q.python_syntax_ok + q.json_valid + q.bash_syntax_ok
        loc = count_lines_of_code(od)
        loc_python += loc["python_loc"]
        loc_bash += loc["bash_loc"]
        loc_json += loc["json_loc"]
        code_files_count += loc["files"]
        if q.placeholder_hits:
            notes.append(f"placeholder@{od.name}: {q.placeholder_hits[0]}")
    syntax_pct = 100.0 * syntax_ok_total / syntax_total if syntax_total else 100.0
    quality_score = syntax_pct
    quality_score -= min(30, 5 * placeholder_hits)
    quality_score -= min(15, 5 * direct_engine)
    quality_score = max(0.0, quality_score)

    # Functional verdict (inferred from artifact presence)
    verdict, reason = infer_verdict(ref, scenarios_cfg=config.get("scenarios", {}) or {})
    vscore = verdict_score(verdict)

    # Cost estimation will be computed AFTER initial pass (needs cross-tool calibration).
    # Here we just resolve the model.
    resolved_model = _resolve_model(ref.parent.tool, ref.parent.session_id, config)

    # Execution trace — analyze log files for actual command execution evidence
    execution_score = 0.0
    execution_breakdown: Dict[str, float] = {}
    suspected_timeout = False
    for od in ref.output_dirs:
        er = evaluate_execution(od, ref.scenario)
        # Take max across output dirs (suite has multiple)
        if er.score > execution_score:
            execution_score = er.score
            execution_breakdown = er.score_breakdown
        if er.suspected_timeout:
            suspected_timeout = True

    overall = composite_score(comp.score_pct, quality_score, vscore, execution_score,
                              sd.has_start_sentinel, sd.has_done_sentinel)

    # Runnability will be merged in post-pass if runnability_report.md exists

    return SessionEval(
        round_index=ref.parent.round_index,
        tool=ref.parent.tool,
        scenario=ref.scenario,
        model=_resolve_model(ref.parent.tool, ref.parent.session_id, config),
        session_id=ref.parent.session_id,
        output_dirs=[str(p) for p in ref.output_dirs],
        exit_status=ref.parent.manifest.get("exit_status"),
        duration_sec=sd.duration_sec,
        has_start=sd.has_start_sentinel,
        has_done=sd.has_done_sentinel,
        tool_call_count=sd.tool_call_count,
        transcript_length=sd.transcript_length,
        input_tokens=sd.total_input_tokens,
        output_tokens=sd.total_output_tokens,
        cache_read_tokens=sd.total_cache_read_tokens,
        cache_write_tokens=sd.total_cache_write_tokens,
        reasoning_tokens=sd.total_reasoning_tokens,
        premium_requests=sd.premium_requests,
        cost_units=sd.cost_units,
        # estimated_usd / cost_basis are filled in by the post-pass
        python_loc=loc_python,
        bash_loc=loc_bash,
        json_loc=loc_json,
        code_files=code_files_count,
        verdict=verdict,
        verdict_reason=reason,
        verdict_score=vscore,
        execution_score=execution_score,
        execution_breakdown=execution_breakdown,
        suspected_timeout=suspected_timeout,
        compliance_score_pct=comp.score_pct,
        compliance_passed=comp.score_passed,
        compliance_total=comp.score_total,
        compliance_checks=comp.checks,
        quality_score=quality_score,
        syntax_pct=syntax_pct,
        python_files=python_files,
        placeholder_hits=placeholder_hits,
        direct_engine_use=direct_engine,
        overall_score=overall,
        notes=notes,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="dx-agentic-dev E2E Analyzer")
    parser.add_argument(
        "--results-root",
        default=str(DEFAULT_RESULTS_ROOT),
        help=f"Path to results/ directory (default: {DEFAULT_RESULTS_ROOT})",
    )
    parser.add_argument(
        "--config",
        default=str(HERE / "config.yaml"),
        help="Path to config.yaml (default: ./config.yaml)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help=f"Where to write reports (default: {DEFAULT_REPORTS_BASE}/<timestamp>/)",
    )
    parser.add_argument("--tool", action="append", help="Filter to specific tools (repeatable)")
    parser.add_argument("--scenario", action="append", help="Filter to specific scenarios (repeatable)")
    parser.add_argument("--round", action="append", type=int, help="Filter to specific rounds (repeatable)")
    parser.add_argument(
        "--insights",
        choices=["off", "auto", "copilot", "claude", "cursor", "opencode", "codex"],
        default="auto",
        help=(
            "Automatically invoke insights.py after analysis (default: auto). "
            "'auto' tries copilot first, falls back to other CLIs if missing. "
            "'off' skips entirely."
        ),
    )
    parser.add_argument(
        "--insights-runnability",
        action="store_true",
        default=True,
        help="Run insights.py --mode runnability on a sample of sessions (default: True). Use --no-insights-runnability to skip.",
    )
    parser.add_argument(
        "--no-insights-runnability",
        action="store_false",
        dest="insights_runnability",
        help="Skip runnability evaluation",
    )
    parser.add_argument(
        "--insights-sample",
        type=int,
        default=8,
        help="(with --insights-runnability) number of sample sessions to evaluate. "
             "Use 0 (or --insights-all) for EXHAUSTIVE.",
    )
    parser.add_argument(
        "--insights-all",
        action="store_true",
        help="(with --insights-runnability) evaluate every session, not just a sample.",
    )
    parser.add_argument(
        "--insights-model",
        default=None,
        help="(forwarded to insights.py) override the chosen CLI's default model "
             "(e.g. 'gpt-4.1', 'claude-sonnet-4-6'). Defaults to the CLI's "
             "free_default_model unless --insights-allow-paid is set.",
    )
    parser.add_argument(
        "--insights-allow-paid",
        action="store_true",
        help="(forwarded to insights.py) permit paid/billed model selections "
             "in the auto chain. Default: only free combinations.",
    )

    args = parser.parse_args(argv)

    results_root = Path(args.results_root).resolve()
    if not results_root.is_dir():
        print(f"ERROR: results-root not found: {results_root}", file=sys.stderr)
        return 2

    config_path = Path(args.config).resolve()
    if not config_path.is_file():
        print(f"ERROR: config not found: {config_path}", file=sys.stderr)
        return 2
    config = _load_config(config_path)
    tools_cfg = config.get("tools", {}) or {}
    scenarios_cfg = config.get("scenarios", {}) or {}

    # Discovery
    all_refs = discover_all(results_root, tools_cfg, scenarios_cfg)
    print(f"Discovered {len(all_refs)} scenario sessions across "
          f"{len({(r.parent.tool, r.parent.round_index) for r in all_refs})} (tool, round) combos.")

    # Filtering
    if args.tool:
        all_refs = [r for r in all_refs if r.parent.tool in args.tool]
    if args.scenario:
        all_refs = [r for r in all_refs if r.scenario in args.scenario]
    if args.round:
        all_refs = [r for r in all_refs if r.parent.round_index in args.round]
    print(f"After filters: {len(all_refs)} sessions to evaluate")

    # Evaluate each scenario
    evals: List[SessionEval] = []
    for i, ref in enumerate(all_refs, 1):
        if i % 10 == 0 or i == len(all_refs):
            print(f"  [{i}/{len(all_refs)}] {ref.parent.tool} R{ref.parent.round_index} {ref.scenario}")
        try:
            evals.append(evaluate_scenario(ref, config))
        except Exception as e:
            print(f"  WARN: evaluation failed for {ref.parent.session_id}/{ref.scenario}: {e}",
                  file=sys.stderr)

    # ---------------- Post-pass: compute cost with cross-tool calibration ----------------
    # Why post-pass: OpenCode (uses copilot provider) doesn't expose premium_requests in
    # its stream. We REVERSE-ENGINEER its premium count from token volume × copilot-cli's
    # observed (tokens/premium) ratio. This requires copilot-cli evals to exist first.
    calibration = compute_calibration_ratios(evals)
    if calibration.tokens_per_premium:
        print(f"\nCalibration: {calibration.notes}")
    else:
        print(f"\nCalibration: {calibration.notes}", file=sys.stderr)

    config_pricing = config.get("pricing", {}) or {}
    for e in evals:
        cb = estimate_cost(
            tool=e.tool,
            model=e.model,
            input_tokens=e.input_tokens,
            output_tokens=e.output_tokens,
            cache_read_tokens=e.cache_read_tokens,
            cache_write_tokens=e.cache_write_tokens,
            premium_requests=e.premium_requests,
            config_pricing=config_pricing,
            calibration=calibration,
        )
        e.estimated_usd = cb.total_usd
        e.cost_basis = cb.pricing_basis
        e.cost_note = cb.notes
        e.estimated_premium_requests = cb.estimated_premium_requests

    # Output directory
    if args.output_dir:
        out_dir = Path(args.output_dir).resolve()
    else:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        out_dir = DEFAULT_REPORTS_BASE / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    # Meta
    caveats = []
    overrides = config.get("model_overrides", []) or []
    for ov in overrides:
        caveats.append(
            f"`{ov.get('session_id_pattern', '?')}` → model `{ov.get('model', '?')}` "
            f"({ov.get('note', '').rstrip('.')})"
        )
    meta = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "results_root": str(results_root),
        "config": str(config_path),
        "session_count": len(evals),
        "tools": sorted({e.tool for e in evals}),
        "rounds": sorted({e.round_index for e in evals}),
        "scenarios": sorted({e.scenario for e in evals}),
        "caveats": caveats,
    }

    # Write outputs
    md_path = out_dir / "analysis.md"
    json_path = out_dir / "analysis.json"
    csv_path = out_dir / "per_session.csv"
    html_path = out_dir / "analysis.html"
    write_markdown(evals, md_path, meta)
    write_json(evals, json_path, meta)
    write_csv(evals, csv_path)
    write_html(evals, html_path, meta)

    print()
    print(f"Wrote: {md_path}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {csv_path}")
    print(f"Wrote: {html_path}")

    # ---------------- Insights pipeline (correct ordering) ----------------
    # The pipeline ORDER MATTERS:
    #   1. runnability  → writes runnability_report.md
    #   2. merge        → folds runnability into Overall scores; rewrites
    #                     analysis.md/json/csv/html
    #   3. insights     → reads the UPDATED analysis.md so qualitative analysis
    #                     reflects runnability data
    #   4. comprehensive → assembles the final summary report
    #
    # Earlier versions ran insights BEFORE runnability, which meant the
    # insights.md was based on stale Overall scores (no Runn% factored in).
    if args.insights != "off":
        effective_sample = 0 if args.insights_all else args.insights_sample
        chosen_cli = _resolve_insights_cli(
            args.insights, allow_paid=args.insights_allow_paid,
        )
        # --- Step 1: runnability ---
        if args.insights_runnability and chosen_cli:
            _run_runnability_step(
                out_dir, chosen_cli, effective_sample,
                model=args.insights_model, allow_paid=args.insights_allow_paid,
            )

        # --- Step 2: merge runnability scores into analysis.md ---
        runnability_path = out_dir / "runnability_report.md"
        if runnability_path.is_file():
            print("\n→ Parsing runnability_report.md and recomputing Overall scores...")
            runn_entries = parse_runnability_report(runnability_path)
            runn_agg = aggregate_runnability(runn_entries)
            updated = 0
            for e in evals:
                key = (e.tool, e.scenario)
                if key in runn_agg:
                    e.runnability_score = runn_agg[key]
                    e.overall_score = composite_score(
                        e.compliance_score_pct, e.quality_score, e.verdict_score,
                        e.execution_score, e.has_start, e.has_done,
                        runnability_pct=e.runnability_score, has_runnability=True,
                    )
                    updated += 1
            if updated > 0:
                print(f"  Updated {updated} sessions with runnability scores")
                write_markdown(evals, md_path, meta)
                write_json(evals, json_path, meta)
                write_csv(evals, csv_path)
                write_html(evals, html_path, meta)
                print(f"  Rewrote: {md_path}")

        # --- Step 3: insights (now reads updated analysis.md) ---
        if chosen_cli:
            _run_insights_step(
                out_dir, chosen_cli,
                model=args.insights_model, allow_paid=args.insights_allow_paid,
            )

    # ---------------- Step 4: Comprehensive report (slim Part 3) ----------------
    _generate_comprehensive_report(out_dir)

    return 0


def _generate_comprehensive_report(report_dir: Path) -> None:
    """Assemble analysis + insights + slim runnability summary into one report.

    Part 3 (runnability) is now a tight summary — distribution tables, skip
    classification, top FAILs, common PARTIAL patterns — with the raw per-
    session details linked rather than inlined. This keeps comprehensive_report
    a digestible single document while still pointing to the full data.
    """
    parts: List[str] = []
    parts.append("# DEEPX Agentic Development — 종합 보고서 (Comprehensive Report)")
    parts.append("")
    parts.append(f"> 생성 시각: {datetime.now().isoformat(timespec='seconds')}")
    parts.append("> 이 보고서는 analysis.md(정량) + insights.md(정성) + runnability 요약을 통합한 종합본입니다.")
    parts.append("> Raw 데이터는 마지막 §참고 섹션의 링크로 제공됩니다.")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Part 1: analysis.md
    analysis_path = report_dir / "analysis.md"
    if analysis_path.is_file():
        parts.append("# Part 1: 정량 분석 (analysis.md)")
        parts.append("")
        parts.append(analysis_path.read_text(encoding="utf-8"))
        parts.append("")
        parts.append("---")
        parts.append("")

    # Part 2: insights.md
    insights_path = report_dir / "insights.md"
    if insights_path.is_file():
        parts.append("# Part 2: 정성 인사이트 (insights.md)")
        parts.append("")
        parts.append(insights_path.read_text(encoding="utf-8"))
        parts.append("")
        parts.append("---")
        parts.append("")
    else:
        prompt_path = report_dir / "insights_prompt.md"
        if prompt_path.is_file():
            parts.append("# Part 2: 정성 인사이트 (미생성)")
            parts.append("")
            parts.append("> insights.md가 아직 생성되지 않았습니다.")
            parts.append(f"> 프롬프트: `{prompt_path}`")
            parts.append("> 수동 실행: `python3 insights.py --mode insights --report-dir <dir> --cli <copilot|claude>`")
            parts.append("")
            parts.append("---")
            parts.append("")

    # Part 3: SLIM runnability summary (no raw inline)
    parts.append(_render_runnability_summary(report_dir))
    parts.append("")

    # §참고: links to raw data
    parts.append("---")
    parts.append("")
    parts.append("## 참고 / Raw 데이터")
    parts.append("")
    parts.append("- 정성 평가 (세션별 raw): [`runnability_report.md`](./runnability_report.md)")
    parts.append("- 정량 분석 (세션 단위 raw JSON): [`analysis.json`](./analysis.json)")
    parts.append("- 세션 행 단위 CSV: [`per_session.csv`](./per_session.csv)")
    parts.append("- 분석 단계별 .md: [`analysis.md`](./analysis.md) · [`insights.md`](./insights.md)")
    parts.append("")

    out_path = report_dir / "comprehensive_report.md"
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"\n✓ Wrote comprehensive report: {out_path}")

    # Generate HTML version of comprehensive report
    html_out = report_dir / "comprehensive_report.html"
    md_file_to_html(out_path, html_out, title="DEEPX Agentic Development — 종합 보고서")


def _render_runnability_summary(report_dir: Path) -> str:
    """Build the slim Part 3 (runnability summary) — tables + key cases, no raw."""
    import json as _json
    import re as _re

    runn_path = report_dir / "runnability_report.md"
    analysis_json_path = report_dir / "analysis.json"

    if not runn_path.is_file():
        return ("# Part 3: End-User Runnability — 요약 (미실행)\n\n"
                "> runnability 평가가 실행되지 않았습니다.\n"
                "> 실행: `python3 insights.py --mode runnability --report-dir <dir> "
                "--cli <copilot|claude> --all`\n")

    runn_text = runn_path.read_text(encoding="utf-8", errors="ignore")
    # Parse each evaluation block: split by '### R<round> <tool> <scenario>'.
    block_pat = _re.compile(
        r"###\s+R(?P<round>\d+)\s+(?P<tool>\S+)\s+(?P<scenario>\S+)\s*\n"
        r"(?P<body>.*?)(?=\n###\s+R\d+\s+\S+\s+\S+|\Z)",
        _re.DOTALL,
    )
    verdict_pat = _re.compile(
        r"\*\*end-user runnability\*\*\s*:\s*(PASS|PARTIAL|FAIL)", _re.IGNORECASE
    )
    issue_pat = _re.compile(
        r"\*\*Key issues\*\*[^\n]*:\s*\n((?:\s*[-*][^\n]*\n?)+)", _re.IGNORECASE
    )
    verdict_oneline = _re.compile(
        r"\*\*One-sentence verdict\*\*\s*:\s*([^\n]+)", _re.IGNORECASE
    )

    blocks = list(block_pat.finditer(runn_text))
    parsed: List[Dict[str, str]] = []
    for m in blocks:
        body = m.group("body")
        vmatch = verdict_pat.search(body)
        verdict = vmatch.group(1).upper() if vmatch else "?"
        imatch = issue_pat.search(body)
        issues_text = imatch.group(1) if imatch else ""
        # Extract individual bullets
        issue_bullets = [
            ln.strip("-* ").strip()
            for ln in issues_text.splitlines() if ln.strip()
        ]
        vone = verdict_oneline.search(body)
        parsed.append({
            "round":    m.group("round"),
            "tool":     m.group("tool"),
            "scenario": m.group("scenario"),
            "verdict":  verdict,
            "issues":   issue_bullets,
            "verdict_oneline": (vone.group(1).strip() if vone else "").rstrip("."),
        })

    # ---- Distribution tables (per-tool, per-scenario) ----
    by_tool: Dict[str, Dict[str, int]] = {}
    by_scenario: Dict[str, Dict[str, int]] = {}
    for p in parsed:
        for d, k in ((by_tool, p["tool"]), (by_scenario, p["scenario"])):
            row = d.setdefault(k, {"PASS": 0, "PARTIAL": 0, "FAIL": 0, "?": 0})
            row[p["verdict"]] += 1

    lines: List[str] = []
    lines.append("# Part 3: End-User Runnability — 요약")
    lines.append("")
    lines.append(f"> 평가된 세션: **{len(parsed)}** (raw: [`runnability_report.md`](./runnability_report.md))")
    lines.append("")
    lines.append("## 3.1 분포 — Tool별")
    lines.append("")
    lines.append("| Tool | PASS | PARTIAL | FAIL | Total | Runn % |")
    lines.append("|------|----:|-------:|----:|-----:|------:|")
    for tool in sorted(by_tool):
        row = by_tool[tool]
        tot = row["PASS"] + row["PARTIAL"] + row["FAIL"]
        runn_pct = ((row["PASS"] * 100 + row["PARTIAL"] * 50) / tot) if tot else 0
        lines.append(f"| **{tool}** | {row['PASS']} | {row['PARTIAL']} | "
                     f"{row['FAIL']} | {tot} | {runn_pct:.1f} |")
    lines.append("")
    lines.append("## 3.2 분포 — Scenario별")
    lines.append("")
    lines.append("| Scenario | PASS | PARTIAL | FAIL | Total | Runn % |")
    lines.append("|----------|----:|-------:|----:|-----:|------:|")
    for sc in sorted(by_scenario):
        row = by_scenario[sc]
        tot = row["PASS"] + row["PARTIAL"] + row["FAIL"]
        runn_pct = ((row["PASS"] * 100 + row["PARTIAL"] * 50) / tot) if tot else 0
        lines.append(f"| {sc} | {row['PASS']} | {row['PARTIAL']} | "
                     f"{row['FAIL']} | {tot} | {runn_pct:.1f} |")
    lines.append("")

    # ---- Skip categorization (from analysis.json) ----
    if analysis_json_path.is_file():
        try:
            sys.path.insert(0, str(HERE))
            from lib.skip_analyzer import (  # type: ignore
                categorize_skipped_sessions, render_skip_summary_markdown,
            )
        finally:
            sys.path.pop(0)
        data = _json.loads(analysis_json_path.read_text(encoding="utf-8"))
        sessions = data.get("sessions", [])
        skip_report = categorize_skipped_sessions(sessions)
        lines.append("## 3.3 Skipped 세션 분류")
        lines.append("")
        lines.append(render_skip_summary_markdown(skip_report, heading_level=4))
        lines.append("")

    # ---- FAIL cases (full list, max ~12 to keep readable) ----
    fails = [p for p in parsed if p["verdict"] == "FAIL"]
    lines.append(f"## 3.4 FAIL 사례 ({len(fails)}건)")
    lines.append("")
    if not fails:
        lines.append("_없음._")
    else:
        for p in fails[:12]:
            lines.append(f"- **{p['tool']} R{p['round']} {p['scenario']}** — "
                         f"{p['verdict_oneline']}")
        if len(fails) > 12:
            lines.append(f"- _… (+{len(fails) - 12}건 더; raw 참조)_")
    lines.append("")

    # ---- PARTIAL common-issue keyword frequency ----
    partials = [p for p in parsed if p["verdict"] == "PARTIAL"]
    if partials:
        keywords = [
            ("verify.py", "verify.py 미제공"),
            ("SUITE_ROOT", "SUITE_ROOT 미사용 (상대경로 의존)"),
            ("session.log", "session.log 부재/부족"),
            ("setup.sh", "setup.sh 환경 구성 불완전"),
            ("venv", "venv 처리 부재"),
            ("dx_engine", "dx_engine bridging 누락"),
            ("ImportError", "ImportError / import 실패"),
            ("README", "README 안내 부족"),
            ("path", "경로 하드코딩"),
            ("permission", "권한 / write target 문제"),
        ]
        counts: List[tuple] = []
        for kw, label in keywords:
            n = sum(
                1 for p in partials
                if any(kw.lower() in iss.lower() for iss in p["issues"])
            )
            if n:
                counts.append((n, label))
        counts.sort(reverse=True)
        lines.append(f"## 3.5 PARTIAL 공통 패턴 ({len(partials)}건 중 키워드 빈도)")
        lines.append("")
        if counts:
            lines.append("| 패턴 | 등장 세션 수 |")
            lines.append("|------|-----------:|")
            for n, label in counts[:8]:
                lines.append(f"| {label} | {n} |")
        else:
            lines.append("_키워드 매칭 없음._")
        lines.append("")

    return "\n".join(lines)


def _resolve_insights_cli(mode: str, *, allow_paid: bool = False) -> Optional[str]:
    """Pick the CLI to use for insights/runnability subprocesses.

    `mode == 'auto'` walks insights.AUTO_CHAIN_FREE (or AUTO_CHAIN_PAID if paid
    is allowed) and returns the first installed binary. A named mode passes
    through. Returns None if nothing is available.
    """
    import shutil

    sys.path.insert(0, str(HERE))
    try:
        from insights import (  # type: ignore
            AUTO_CHAIN_FREE, AUTO_CHAIN_PAID, CLI_CONFIG,
        )
    finally:
        sys.path.pop(0)

    if mode == "auto":
        candidates = list(AUTO_CHAIN_PAID) if allow_paid else list(AUTO_CHAIN_FREE)
    else:
        candidates = [mode]

    for c in candidates:
        binary = CLI_CONFIG.get(c, {}).get("binary", c)
        if shutil.which(binary):
            return c

    chain_label = "paid" if allow_paid else "free"
    print()
    print(f"⚠ No agentic CLI available in {chain_label} chain ({candidates}). "
          f"Skipping insights/runnability steps.")
    return None


def _insights_common_args(report_dir: Path, chosen: str,
                           model: Optional[str], allow_paid: bool) -> List[str]:
    args = ["--report-dir", str(report_dir), "--cli", chosen]
    if model:
        args += ["--model", model]
    if allow_paid:
        args += ["--allow-paid"]
    return args


def _run_runnability_step(report_dir: Path, chosen: str, sample: int,
                           *, model: Optional[str] = None,
                           allow_paid: bool = False) -> None:
    """Invoke insights.py --mode runnability. Runs FIRST so its scores can be
    merged into analysis.md before the insights step reads it.
    """
    import subprocess

    insights_script = HERE / "insights.py"
    if not insights_script.is_file():
        return
    sample_label = "EXHAUSTIVE" if sample <= 0 else f"sample={sample}"
    runn_timeout = 14400 if sample <= 0 else 1800  # 4h vs 30min
    common = _insights_common_args(report_dir, chosen, model, allow_paid)
    print()
    print(f"→ Step 1: insights.py --mode runnability --cli {chosen} "
          f"({sample_label})...")
    try:
        r = subprocess.run(
            ["python3", str(insights_script), "--mode", "runnability"] + common
            + (["--all"] if sample <= 0 else ["--sample", str(sample)]),
            check=False, timeout=runn_timeout,
        )
        if r.returncode == 0:
            print("✓ runnability_report.md generated")
    except subprocess.TimeoutExpired:
        print(f"⚠ runnability check timed out (>{runn_timeout}s)")
    except Exception as e:
        print(f"⚠ runnability check failed: {e}")


def _run_insights_step(report_dir: Path, chosen: str,
                        *, model: Optional[str] = None,
                        allow_paid: bool = False) -> None:
    """Invoke insights.py --mode insights. Runs AFTER runnability merge so the
    qualitative analysis reflects updated Overall scores.
    """
    import subprocess

    insights_script = HERE / "insights.py"
    if not insights_script.is_file():
        return
    common = _insights_common_args(report_dir, chosen, model, allow_paid)
    print()
    print(f"→ Step 3: insights.py --mode insights --cli {chosen} "
          f"(model={model or 'default'})...")
    try:
        r = subprocess.run(
            ["python3", str(insights_script), "--mode", "insights"] + common,
            check=False, timeout=1200,
        )
        if r.returncode == 0:
            print(f"✓ insights.md generated (via {chosen})")
    except subprocess.TimeoutExpired:
        print("⚠ insights.py timed out (>20min); prompt saved for manual retry")
    except Exception as e:
        print(f"⚠ insights.py failed: {e}")


if __name__ == "__main__":
    sys.exit(main())
