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
import hashlib
import html as html_mod
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Allow running from any cwd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


# Known tool name aliases — keys without the -cli suffix that can appear in
# hypothesis.json expected_ranking arrays generated before the canonical names
# were stabilised.
_TOOL_NAME_ALIASES: dict = {
    "opencode": "opencode-cli",
    "codex":    "codex-cli",
    "cursor":   "cursor-cli",
    "copilot":  "copilot-cli",
}


def _normalize_hypothesis_tools(hypothesis_data: dict) -> dict:
    """Return a copy of hypothesis_data with tool names normalised in all
    expected_ranking arrays.  No-op if hypothesis_data is None or empty."""
    import copy
    if not hypothesis_data:
        return hypothesis_data
    data = copy.deepcopy(hypothesis_data)
    for h in data.get("hypotheses", []):
        ranking = h.get("expected_ranking")
        if isinstance(ranking, list):
            h["expected_ranking"] = [
                _TOOL_NAME_ALIASES.get(t, t) for t in ranking
            ]
    return data


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


def evaluate_scenario(
    ref: ScenarioRef,
    config: dict,
    rubric_version: str = "v3",
) -> SessionEval:
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

    # Execution trace — rubric evaluates ALL output_dirs at once (multi-dir
    # scenarios like runtime / suite are scored holistically rather than via
    # per-dir max).
    er = evaluate_execution(ref.output_dirs, ref.scenario, rubric_version=rubric_version)
    execution_score = er.score
    execution_breakdown = er.score_breakdown
    suspected_timeout = er.suspected_timeout

    overall = composite_score(comp.score_pct, quality_score, vscore, execution_score,
                              sd.has_start_sentinel, sd.has_done_sentinel,
                              scenario=ref.scenario)

    # Runnability will be merged in post-pass if runnability_report.md exists

    return SessionEval(
        round_index=ref.parent.round_index,
        tool=ref.parent.tool,
        scenario=ref.scenario,
        model=_resolve_model(ref.parent.tool, ref.parent.session_id, config),
        session_id=ref.parent.session_id,
        output_dirs=[str(p) for p in ref.output_dirs],
        exit_status=ref.parent.manifest.get("exit_status"),
        run_id=ref.parent.run_id,
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
        user_turn_count=sd.user_turn_count,
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
        "--run-id",
        dest="run_id",
        action="append",
        help=(
            "Restrict analysis to this run_id (repeatable). "
            "When omitted, all run_ids (and legacy flat results) are aggregated. "
            "Multiple --run-id flags produce one combined report in "
            "analyzer_reports/multi_<sha8>/."
        ),
    )
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
        help="Run insights.py --mode runnability on all sessions (default: True). Use --no-insights-runnability to skip.",
    )
    parser.add_argument(
        "--no-insights-runnability",
        action="store_false",
        dest="insights_runnability",
        help="Skip runnability evaluation",
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
        action=argparse.BooleanOptionalAction,
        default=None,
        help="(forwarded to insights.py) permit paid/billed model selections. "
             "Mode-specific defaults when unset: insights/hypothesis → PAID "
             "(copilot + claude-sonnet-4.6), runnability → FREE (gpt-4.1). "
             "Use --no-insights-allow-paid to force free models for all stages.",
    )
    parser.add_argument(
        "--existing-runnability",
        default=None,
        help="Path to an existing runnability_report.md from a previous run. "
             "Passed to insights.py via --existing-report for incremental "
             "runnability evaluation (skip already-evaluated sessions, merge "
             "new results). Useful when adding new rounds to an existing report.",
    )
    parser.add_argument(
        "--rubric-version",
        dest="rubric_version",
        choices=["v2", "v3"],
        default="v3",
        help=(
            "ExecutionTrace rubric version (default: v3). "
            "v3 = expanded marker dictionary + verify_py reallocation. "
            "v2 preserved for data lineage / reproducibility — see "
            "lib/execution.py EXECUTION_RUBRIC_V3 docstring."
        ),
    )
    parser.add_argument(
        "--hypothesis",
        default=None,
        help="Path to hypothesis prompt (.md) or pre-built hypothesis (.json). "
             "When provided, generates hypothesis.json via LLM (Stage 4.5) and "
             "adds Part 0 '실험 설계' to comprehensive report. If insights are "
             "also enabled, §8 '가설 검증' is added to insights.md.",
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

    # Run-ID scope (single, multiple, or all)
    run_ids: Optional[List[str]] = args.run_id or None
    if run_ids:
        print(f"Run-ID scope: {', '.join(run_ids)}")

    # Discovery
    all_refs = discover_all(results_root, tools_cfg, scenarios_cfg, run_ids=run_ids)
    print(f"Discovered {len(all_refs)} scenario sessions across "
          f"{len({(r.parent.run_id, r.parent.tool, r.parent.round_index) for r in all_refs})} "
          f"(run_id, tool, round) combos.")

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
            evals.append(evaluate_scenario(ref, config, rubric_version=args.rubric_version))
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
            user_turn_count=e.user_turn_count,
            tool_call_count=e.tool_call_count,
        )
        e.estimated_usd = cb.total_usd
        e.cost_basis = cb.pricing_basis
        e.cost_note = cb.notes
        e.estimated_premium_requests = cb.estimated_premium_requests
        e.pr_observed = cb.pr_observed
        e.pr_by_tool_call = cb.pr_by_tool_call
        e.pr_by_user_turn = cb.pr_by_user_turn
        e.pr_by_token_ratio = cb.pr_by_token_ratio

    # Output directory — keyed by run_id scope when --output-dir not given:
    #   * No --run-id          → analyzer_reports/_all/<ts>/
    #   * Single --run-id ID   → analyzer_reports/<ID>/<ts>/
    #   * Multiple --run-id    → analyzer_reports/multi_<sha8>/<ts>/ (+ multi_manifest.json)
    multi_manifest: Optional[dict] = None
    if args.output_dir:
        out_dir = Path(args.output_dir).resolve()
    else:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        # Suffix with rubric version so v2 / v3 reports for the same run-id
        # can coexist for direct comparison.
        ts = f"{ts}_{args.rubric_version}"
        if not run_ids:
            out_dir = DEFAULT_REPORTS_BASE / "_all" / ts
        elif len(run_ids) == 1:
            out_dir = DEFAULT_REPORTS_BASE / run_ids[0] / ts
        else:
            sorted_ids = sorted(run_ids)
            digest = hashlib.sha1("+".join(sorted_ids).encode("utf-8")).hexdigest()[:8]
            out_dir = DEFAULT_REPORTS_BASE / f"multi_{digest}" / ts
            multi_manifest = {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "run_ids": sorted_ids,
                "digest": digest,
            }
    out_dir.mkdir(parents=True, exist_ok=True)
    if multi_manifest is not None:
        (out_dir / "multi_manifest.json").write_text(
            json.dumps(multi_manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # Meta
    caveats = []
    overrides = config.get("model_overrides", []) or []
    for ov in overrides:
        caveats.append(
            f"`{ov.get('session_id_pattern', '?')}` → model `{ov.get('model', '?')}` "
            f"({ov.get('note', '').rstrip('.')})"
        )
    # Use the CLI-selected rubric (single source of truth across this run)
    _exec_rubric_v = args.rubric_version

    meta = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "results_root": str(results_root),
        "config": str(config_path),
        "session_count": len(evals),
        "tools": sorted({e.tool for e in evals}),
        "rounds": sorted({e.round_index for e in evals}),
        "scenarios": sorted({e.scenario for e in evals}),
        "run_ids": sorted({e.run_id for e in evals}),
        "rubric_version": _exec_rubric_v,
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
        chosen_cli = _resolve_insights_cli(
            args.insights, allow_paid=args.insights_allow_paid,
        )
        # --- Step 1: runnability ---
        if args.insights_runnability and chosen_cli:
            _run_runnability_step(
                out_dir, chosen_cli,
                model=args.insights_model, allow_paid=args.insights_allow_paid,
                existing_report=Path(args.existing_runnability).resolve() if args.existing_runnability else None,
            )
    else:
        chosen_cli = None

    # --- Step 1.5: copy existing runnability report when insights is off ---
    # When --insights off skips Step 1 but --existing-runnability is provided,
    # copy the file so Step 2 merge can find it.
    if args.existing_runnability and not (out_dir / "runnability_report.md").is_file():
        import shutil
        src = Path(args.existing_runnability).resolve()
        if src.is_file():
            shutil.copy2(src, out_dir / "runnability_report.md")
            print(f"\n  ✓ runnability_report.md copied from {src.name}")

    # --- Step 2: merge runnability scores into analysis.md ---
    # (runs regardless of --insights flag — pure computation, no LLM needed)
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
                    scenario=e.scenario,
                )
                updated += 1
        if updated > 0:
            print(f"  Updated {updated} sessions with runnability scores")
            write_markdown(evals, md_path, meta)
            write_json(evals, json_path, meta)
            write_csv(evals, csv_path)
            write_html(evals, html_path, meta)
            print(f"  Rewrote: {md_path}")

    # --- Step 2.5: hypothesis generation (optional) ---
    # (runs regardless of --insights flag — copies JSON or invokes LLM)
    if getattr(args, 'hypothesis', None):
        hp = Path(args.hypothesis)
        if hp.suffix.lower() == ".json":
            import shutil
            dest = out_dir / "hypothesis.json"
            if hp.resolve() != dest.resolve():
                shutil.copy2(hp, dest)
                print(f"\n  ✓ hypothesis.json copied from {hp}")
            else:
                print(f"\n  ✓ hypothesis.json already in output directory")
        else:
            hyp_cli = chosen_cli or _resolve_insights_cli("auto", allow_paid=True)
            if hyp_cli:
                _run_hypothesis_step(
                    out_dir, hyp_cli, hp,
                    model=args.insights_model,
                    allow_paid=args.insights_allow_paid,
                )

    if args.insights != "off" and chosen_cli:
        # --- Step 3: insights (now reads updated analysis.md) ---
        _run_insights_step(
            out_dir, chosen_cli,
            model=args.insights_model, allow_paid=args.insights_allow_paid,
        )

    # ---------------- Step 4: Comprehensive report (slim Part 3) ----------------
    _generate_comprehensive_report(out_dir)

    return 0


_DEFAULT_EXPERIMENT_DESIGN = """\
# 실험 결과 요약(Summary)

## 실험 제목

DEEPX Agentic Development E2E 평가

## 실험 목적

5개 AI 코딩 도구(Claude Code, Copilot CLI, Cursor CLI, OpenCode, Codex CLI)를 사용하여 \
NPU(Neural Processing Unit) 추론 앱을 자동 생성하는 "Agentic Development" 워크플로우의 \
실용성과 도구 간 성능 차이를 정량적으로 비교 평가한다.

## 실험 조건

- **시나리오**: 6개 (compiler, app-python 4종, cross-project)
- **반복 횟수**: 라운드당 도구×시나리오 = 30 세션
- **평가 지표**: 규칙 준수(Compliance), 코드 품질(Quality), 실행 가능성(Runnability), 산출물 완성도(Execution), 종합 점수(Overall)
- **통제 변수**: 동일 프롬프트, 동일 하드웨어(DX-M1 NPU), 동일 모델(Claude Sonnet 4.6 계열)
"""


_SECTION_HEADING_RE = __import__("re").compile(r'^##\s+\d+\.\s+(.*)$', __import__("re").MULTILINE)


def _extract_insights_section(insights_text: str, title_keyword: str) -> str:
    """Extract the body of an insights.md `## N. <title>` section.

    *title_keyword* is matched against the heading text (case-insensitive substring).
    Returns the section body (everything between the matching heading and the next
    `## ` heading or EOF), stripped. Empty string if not found.
    """
    re = __import__("re")
    headings = list(_SECTION_HEADING_RE.finditer(insights_text))
    target_idx = None
    for i, m in enumerate(headings):
        if title_keyword.lower() in m.group(1).lower():
            target_idx = i
            break
    if target_idx is None:
        return ""
    start = headings[target_idx].end()
    end = headings[target_idx + 1].start() if target_idx + 1 < len(headings) else len(insights_text)
    return insights_text[start:end].strip()


def _render_summary_extras_from_insights(insights_path: Path) -> str:
    """Pull condensed 가설 검증 + 향후 운영 권장 subsections from insights.md.

    These appear as sub-sections under the Summary section of the comprehensive
    report so a reader gets the headline conclusions without scrolling to
    Part 3. The full text remains in insights.md (rendered as Part 3 later).
    """
    if not insights_path.is_file():
        return ""
    try:
        text = insights_path.read_text(encoding="utf-8")
    except OSError:
        return ""

    parts: List[str] = []

    # Hypothesis verification — surface the 가설 검증 종합 table + 종합 시사점.
    # Link target: Part-3 (insights.md) § "7. 가설 검증 …" heading.
    # We use the stable HTML alias `#hypothesis-verification` injected by
    # lib/report._md_to_html (counter-based sec-N-* IDs change as the report
    # structure evolves, so they cannot be hardcoded here).
    HYP_ANCHOR = "#hypothesis-verification"
    HYP_LINK = f"> 상세: [§7 가설 검증 — 벤치마크 vs 실측 간극 분석]({HYP_ANCHOR})"

    hyp_body = _extract_insights_section(text, "가설 검증")
    parts.append("## 가설 검증")
    parts.append("")
    parts.append(HYP_LINK)
    parts.append("")
    if hyp_body:
        # Prefer the 종합 sub-block when present; otherwise fall back to the
        # full §-body so we never leave the Summary section empty for runs
        # where the LLM skipped the explicit 종합 heading.
        import re as _re
        summary_match = _re.search(r'###\s+가설 검증 종합', hyp_body)
        if summary_match:
            hyp_summary = hyp_body[summary_match.start():].strip()
        else:
            hyp_summary = hyp_body
        parts.append(hyp_summary)
    else:
        # Fallback when insights.md doesn't contain a 가설 검증 section
        # (e.g. analyzer ran without --hypothesis, or LLM skipped it).
        # Preserves report structure so the anchor link still resolves
        # if/when insights.md is regenerated.
        parts.append(
            "> _이번 실행에는 가설 검증 결과가 포함되지 않았습니다. "
            "`--hypothesis <prompt|json>` 옵션과 함께 재실행하면 위 anchor에 상세 분석이 표시됩니다._"
        )
    parts.append("")

    # Recommendations — surface 향후 운영 권장 bullets. Same stable-alias pattern.
    REC_ANCHOR = "#recommendations"
    REC_LINK = f"> 상세: [§8 향후 운영 권장]({REC_ANCHOR})"

    rec_body = _extract_insights_section(text, "향후 운영")
    parts.append("## 향후 운영 권장")
    parts.append("")
    parts.append(REC_LINK)
    parts.append("")
    if rec_body:
        parts.append(rec_body)
    else:
        parts.append(
            "> _이번 실행에는 향후 운영 권장 섹션이 포함되지 않았습니다._"
        )
    parts.append("")

    return "\n".join(parts)


def _render_experiment_design(
    hypothesis_path: Optional[Path],
    insights_path: Optional[Path] = None,
) -> str:
    """Render the Summary section (originally 'Part 0: 실험 설계').

    Always returns the default experiment purpose/conditions.
    When hypothesis.json exists, appends benchmarks and hypotheses.
    When insights.md exists, also injects condensed 가설 검증 + 향후 운영 권장
    subsections so the Summary section is self-contained.
    """
    base = _DEFAULT_EXPERIMENT_DESIGN

    extras_from_insights = (
        _render_summary_extras_from_insights(insights_path)
        if insights_path is not None
        else ""
    )

    if hypothesis_path is None or not hypothesis_path.is_file():
        return base + ("\n\n" + extras_from_insights if extras_from_insights else "")

    try:
        data = json.loads(hypothesis_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return base

    exp = data.get("experiment", {})
    lines: List[str] = []

    # Enrich purpose if hypothesis provides one
    if exp.get("purpose"):
        lines.append(f"\n> **가설 기반 실험 목적:** {exp['purpose']}")
        lines.append("")
    if exp.get("background"):
        lines.append(f"## 실험 배경\n\n{exp['background']}")
        lines.append("")

    benchmarks = data.get("benchmarks", [])
    if benchmarks:
        lines.append("## 참조 벤치마크")
        lines.append("")
        for bm in benchmarks:
            lines.append(f"### {bm.get('name', 'N/A')}")
            lines.append("")
            lines.append(f"- URL: {bm.get('url', 'N/A')}")
            lines.append(f"- 조회일: {bm.get('retrieved_date', 'N/A')}")
            lines.append(f"- Metric: {bm.get('metric', 'N/A')}")
            scores = bm.get("scores", {})
            if scores:
                for model_name, score in scores.items():
                    lines.append(f"  - {model_name}: {score}")
            if bm.get("notes"):
                lines.append(f"- 비고: {bm['notes']}")
            lines.append("")

    hypotheses = data.get("hypotheses", [])
    if hypotheses:
        lines.append("## 사전 가설")
        lines.append("")
        for h in hypotheses:
            lines.append(f"### {h.get('id', '?')}: {h.get('statement', 'N/A')}")
            lines.append("")
            lines.append(f"- **근거:** {h.get('rationale', 'N/A')}")
            lines.append(f"- **측정 지표:** {h.get('metric', 'N/A')}")
            ranking = h.get("expected_ranking", [])
            if ranking:
                lines.append(f"- **예상 순위:** {' > '.join(ranking)}")
            lines.append(f"- **신뢰도:** {h.get('confidence', 'N/A')}")
            basis = h.get("benchmark_basis", [])
            if basis:
                lines.append(f"- **벤치마크 근거:** {', '.join(basis)}")
            lines.append("")

    # 도구별 검증 결과 요약 + Visual Summary placeholder are emitted
    # UNCONDITIONALLY (with or without hypothesis.json). When hypotheses
    # exist this section sits right after 사전 가설; otherwise it appears
    # as the first sub-section of the Summary block. The {{CHART_SECTION}}
    # placeholder is replaced by _build_chart_section() during HTML
    # rendering (see analyze.py:_write_comprehensive_html).
    lines.append("## 도구별 검증 결과 요약")
    lines.append("")
    lines.append("{{CHART_SECTION}}")
    lines.append("")

    body = base + "\n".join(lines)
    if extras_from_insights:
        body += "\n\n" + extras_from_insights
    return body



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

    # Summary section (always present; enriched if hypothesis.json exists;
    # also pulls condensed 가설 검증 + 향후 운영 권장 from insights.md if present
    # so the headline conclusions land at the top of the report).
    hypothesis_path = report_dir / "hypothesis.json"
    insights_path = report_dir / "insights.md"
    parts.append(_render_experiment_design(
        hypothesis_path if hypothesis_path.is_file() else None,
        insights_path if insights_path.is_file() else None,
    ))
    parts.append("")
    parts.append("---")
    parts.append("")

    # Executive Summary — ranked tool table
    parts.append(_render_executive_summary(report_dir))
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

    # Part 2: Runnability summary (computed before insights, so insights
    # reflect updated Overall scores that include runnability)
    parts.append(_render_runnability_summary(report_dir))
    parts.append("")

    # Part 3: insights.md (qualitative, generated AFTER runnability merge)
    insights_path = report_dir / "insights.md"
    if insights_path.is_file():
        parts.append("# Part 3: 정성 인사이트 (insights.md)")
        parts.append("")
        parts.append(insights_path.read_text(encoding="utf-8"))
        parts.append("")
        parts.append("---")
        parts.append("")
    else:
        prompt_path = report_dir / "insights_prompt.md"
        if prompt_path.is_file():
            parts.append("# Part 3: 정성 인사이트 (미생성)")
            parts.append("")
            parts.append("> insights.md가 아직 생성되지 않았습니다.")
            parts.append(f"> 프롬프트: `{prompt_path}`")
            parts.append("> 수동 실행: `python3 insights.py --mode insights --report-dir <dir> --cli <copilot|claude>`")
            parts.append("")
            parts.append("---")
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
    parts.append("- 인터랙티브 대시보드: [`dashboard.html`](./dashboard.html)")
    parts.append("")

    out_path = report_dir / "comprehensive_report.md"
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"\n✓ Wrote comprehensive report: {out_path}")

    # Generate HTML version of comprehensive report (enhanced with Chart.js)
    html_out = report_dir / "comprehensive_report.html"
    _write_comprehensive_html(out_path, html_out, report_dir)

    # Generate HTML version of runnability report (if md exists)
    runn_md = report_dir / "runnability_report.md"
    if runn_md.is_file():
        _write_runnability_html(runn_md, report_dir / "runnability_report.html")

    # Generate standalone interactive dashboard
    _generate_dashboard_html(report_dir)


def _render_executive_summary(report_dir: Path) -> str:
    """Build Executive Summary with sorted tool rankings from analysis.json."""
    import json as _json

    json_path = report_dir / "analysis.json"
    if not json_path.is_file():
        return ""

    data = _json.loads(json_path.read_text(encoding="utf-8"))
    per_tool = data.get("per_tool", {})
    if not per_tool:
        return ""

    # Build ranked list sorted by avg_overall_score descending
    ranked = []
    for tool, m in per_tool.items():
        ranked.append({
            "tool": tool,
            "overall": m.get("avg_overall_score", 0),
            "compliance": m.get("avg_compliance_pct", 0),
            "quality": m.get("avg_quality_score", 0),
            "sessions": m.get("sessions", 0),
            "sessions_scored": m.get("sessions_scored", m.get("sessions", 0)),
            "env_failures": m.get("env_failures", 0),
            "duration": m.get("avg_duration_sec", 0),
            "stdev_overall": m.get("stdev_overall_score", 0),
            "start_sentinel": m.get("pct_with_start_sentinel", 0),
            "done_sentinel": m.get("pct_with_done_sentinel", 0),
            "exit_0": m.get("pct_exit_0", 0),
            "tool_calls": m.get("avg_tool_calls", 0),
            "python_loc": m.get("avg_python_loc", 0),
        })
    ranked.sort(key=lambda x: x["overall"], reverse=True)

    meta = data.get("meta", {})
    total_sessions = meta.get("session_count", sum(r["sessions"] for r in ranked))
    total_rounds = len(meta.get("rounds", []))
    total_scenarios = len(meta.get("scenarios", []))

    lines = []
    lines.append("# Executive Summary — 도구별 종합 순위")
    lines.append("")
    lines.append(f"> **{total_sessions}** sessions = "
                 f"**{len(ranked)}** tools × **{total_rounds}** rounds × "
                 f"**{total_scenarios}** scenarios")
    lines.append("")

    # Main ranking table
    lines.append("## 종합 순위 (Overall Score 기준)")
    lines.append("")
    # Top-level ranking shows only the composite Overall and dispersion — the
    # 4 sub-scores (Compliance / Quality / ExecutionTrace / Runnability) are
    # detailed in §1-A and §2.2~§2.5 of the comprehensive report. Showing only
    # 2 of the 4 sub-scores here was confusing (R65 feedback).
    lines.append("| Rank | Tool | Overall | σ(Overall) | Sessions | Avg Duration |")
    lines.append("|:----:|------|--------:|-----------:|--------:|-------------:|")
    medals = ["🥇", "🥈", "🥉", "4", "5"]
    for i, r in enumerate(ranked):
        dur_min = int(r["duration"] // 60)
        dur_sec = int(r["duration"] % 60)
        sess_display = (f"{r['sessions_scored']}/{r['sessions']}"
                        if r['env_failures'] > 0 else str(r['sessions']))
        lines.append(
            f"| {medals[i] if i < 5 else i+1} "
            f"| **{r['tool']}** "
            f"| **{r['overall']:.1f}** "
            f"| ±{r['stdev_overall']:.1f} "
            f"| {sess_display} "
            f"| {dur_min}m {dur_sec}s |"
        )
    lines.append("")

    # Environment failure (false alarm) notice
    total_env = sum(r['env_failures'] for r in ranked)
    if total_env > 0:
        lines.append("## 가성 결함 제외 (False Alarm Exclusion)")
        lines.append("")
        lines.append(f"환경 문제(API rate limit, TLS error, CLI crash)로 인한 완전 실패 세션 "
                     f"**{total_env}건**이 점수 평균 산정 모수에서 제외되었습니다.")
        lines.append("이 세션들은 도구 능력이 아닌 인프라 문제를 반영하므로 가성 결함으로 분류됩니다.")
        lines.append("")
        lines.append("| 도구 | 제외 세션 수 | 유효 세션 수 | 제외 비율 |")
        lines.append("|------|----------:|----------:|--------:|")
        for r in ranked:
            if r['env_failures'] > 0:
                pct = 100.0 * r['env_failures'] / r['sessions'] if r['sessions'] else 0
                lines.append(
                    f"| {r['tool']} | {r['env_failures']} | "
                    f"{r['sessions_scored']}/{r['sessions']} | {pct:.1f}% |")
        lines.append("")
        lines.append("> 판정 기준: output_dirs 없음 + START sentinel 없음 + output_tokens == 0 → CLI가 agent를 시작하지 못한 환경 장애 (TLS 오류·API quota 등으로 LLM 미응답)")
        lines.append("")

    # Key findings
    best = ranked[0]
    worst = ranked[-1]
    lines.append("## 주요 발견 (Key Findings)")
    lines.append("")
    lines.append(f"- **최고 종합 점수**: {best['tool']} ({best['overall']:.1f})")
    lines.append(f"- **최저 종합 점수**: {worst['tool']} ({worst['overall']:.1f})")
    lines.append(f"- **점수 차이**: {best['overall'] - worst['overall']:.1f}점 "
                 f"({((best['overall'] - worst['overall']) / worst['overall'] * 100):.1f}% 격차)")
    # Find best per dimension
    best_compliance = max(ranked, key=lambda x: x["compliance"])
    best_quality = max(ranked, key=lambda x: x["quality"])
    fastest = min(ranked, key=lambda x: x["duration"])
    lines.append(f"- **최고 Compliance**: {best_compliance['tool']} ({best_compliance['compliance']:.1f}%)")
    lines.append(f"- **최고 Quality**: {best_quality['tool']} ({best_quality['quality']:.1f})")
    lines.append(f"- **최단 평균 실행시간**: {fastest['tool']} "
                 f"({int(fastest['duration']//60)}m {int(fastest['duration']%60)}s)")
    lines.append("")
    lines.append("> 📊 **인터랙티브 차트**: [`dashboard.html`](./dashboard.html) 에서 "
                 "시각적 비교 그래프를 확인할 수 있습니다.")
    lines.append("")

    return "\n".join(lines)


def _write_runnability_html(md_path: Path, html_path: Path) -> None:
    """Convert runnability_report.md to a standalone HTML file."""
    if not md_path.is_file():
        return
    md_content = md_path.read_text(encoding="utf-8")
    body = _md_to_html_import(md_content)
    title = "DEEPX Agentic Development — Runnability Report"
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px auto; max-width: 1100px; padding: 0 20px; line-height: 1.6; color: #333; }}
h1, h2, h3 {{ color: #1a1a2e; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #f0f4ff; }}
pre {{ background: #f5f5f5; padding: 12px; border-radius: 5px; overflow-x: auto; }}
code {{ background: #f0f0f0; padding: 2px 5px; border-radius: 3px; font-size: 0.9em; }}
blockquote {{ border-left: 4px solid #4a9eff; padding-left: 15px; margin-left: 0; color: #555; }}
a {{ color: #4a9eff; }}
</style>
</head>
<body>
{body}
</body>
</html>"""
    html_path.write_text(html, encoding="utf-8")
    print(f"  ✓ {html_path.name} written")


def _write_comprehensive_html(md_path: Path, html_path: Path, report_dir: Path) -> None:
    """Write comprehensive_report.html with Chart.js charts injected at the top."""
    import json as _json

    if not md_path.exists():
        return

    md_content = md_path.read_text(encoding="utf-8")
    body = _md_to_html_import(md_content)
    title = "DEEPX Agentic Development — 종합 보고서"

    # Load analysis.json for chart data
    json_path = report_dir / "analysis.json"
    hypothesis_path = report_dir / "hypothesis.json"
    chart_section = ""
    if json_path.is_file():
        data = _json.loads(json_path.read_text(encoding="utf-8"))
        chart_section = _build_chart_section(
            data,
            hypothesis_path if hypothesis_path.is_file() else None,
        )

    # Place chart_section AFTER 사전 가설 heading (under the "도구별 검증 결과
    # 요약" section we emitted in _render_experiment_design). The markdown
    # carries a literal "{{CHART_SECTION}}" placeholder; once md→html
    # conversion runs, that string survives unchanged inside a <p> wrapper
    # — replace it with the chart HTML and drop the now-empty paragraph.
    placeholder = "<p>{{CHART_SECTION}}</p>"
    if placeholder in body:
        body = body.replace(placeholder, chart_section)
        chart_section_for_top = ""  # already injected mid-body
    else:
        # Fallback for older reports without hypothesis section — keep legacy
        # behavior of showing charts at the top of the document.
        chart_section_for_top = chart_section

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_mod.escape(title)}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
{_get_comprehensive_css()}
</style>
</head>
<body>
<nav id="sidebar" class="sidebar">
  <div class="sidebar-toggle" id="sidebar-toggle">☰ 목차</div>
  <div class="sidebar-content" id="sidebar-nav"></div>
</nav>
<div class="container">
{chart_section_for_top}
{body}
</div>
<script>
// Sidebar toggle
document.getElementById('sidebar-toggle').addEventListener('click', function() {{
  var sb = document.getElementById('sidebar');
  sb.classList.toggle('collapsed');
  document.body.style.paddingLeft = sb.classList.contains('collapsed') ? '60px' : '280px';
}});
// Build sidebar navigation from headings
(function() {{
  const nav = document.getElementById('sidebar-nav');
  const headings = document.querySelectorAll('h1[id], h2[id], h3[id]');
  headings.forEach(h => {{
    const a = document.createElement('a');
    a.href = '#' + h.id;
    a.textContent = h.textContent.replace(/[🥇🥈🥉]/g, '').trim();
    a.className = 'nav-' + h.tagName.toLowerCase();
    nav.appendChild(a);
  }});
}})();
</script>
</body>
</html>"""

    html_path.write_text(html, encoding="utf-8")


def _build_chart_section(data: dict, hypothesis_path: Optional[Path] = None) -> str:
    """Build HTML section with Chart.js charts from analysis.json data."""
    import json as _json

    hypothesis_data = None
    if hypothesis_path is not None and hypothesis_path.is_file():
        try:
            hypothesis_data = _normalize_hypothesis_tools(
                _json.loads(hypothesis_path.read_text(encoding="utf-8"))
            )
        except Exception:
            hypothesis_data = None

    per_tool = data.get("per_tool", {})
    if not per_tool:
        return ""

    # Sort tools by overall score
    ranked = sorted(per_tool.items(), key=lambda x: x[1].get("avg_overall_score", 0), reverse=True)
    tools = [t[0] for t in ranked]
    overall = [round(t[1].get("avg_overall_score", 0), 1) for t in ranked]
    compliance = [round(t[1].get("avg_compliance_pct", 0), 1) for t in ranked]
    quality = [round(t[1].get("avg_quality_score", 0), 1) for t in ranked]
    duration = [round(t[1].get("avg_duration_sec", 0) / 60, 1) for t in ranked]
    start_s = [round(t[1].get("pct_with_start_sentinel", 0), 1) for t in ranked]
    done_s = [round(t[1].get("pct_with_done_sentinel", 0), 1) for t in ranked]

    # Round trend data
    per_rt = data.get("per_round_tool", {})
    rounds_set = sorted({int(k.split("__")[0][1:]) for k in per_rt})
    tool_set = sorted(per_tool.keys())
    trend_data = {}
    for tool in tool_set:
        trend_data[tool] = []
        for r in rounds_set:
            key = f"R{r}__{tool}"
            val = per_rt.get(key, {}).get("avg_overall_score", None)
            trend_data[tool].append(round(val, 1) if val is not None else None)

    colors = [
        "rgba(54, 162, 235, 0.8)",   # blue - copilot
        "rgba(75, 192, 192, 0.8)",   # teal - opencode
        "rgba(255, 159, 64, 0.8)",   # orange - codex
        "rgba(153, 102, 255, 0.8)",  # purple - cursor
        "rgba(255, 99, 132, 0.8)",   # red - claude
    ]
    border_colors = [c.replace("0.8", "1") for c in colors]

    # Assign colors by tool name (stable mapping)
    tool_color_map = {
        "copilot-cli": 0, "opencode-cli": 1, "codex-cli": 2,
        "cursor-cli": 3, "claude-code": 4,
    }

    def _tc(tool_name):
        idx = tool_color_map.get(tool_name, hash(tool_name) % len(colors))
        return colors[idx]

    def _tbc(tool_name):
        idx = tool_color_map.get(tool_name, hash(tool_name) % len(colors))
        return border_colors[idx]

    return f"""
<div class="chart-dashboard">
  <h2>📊 Visual Summary — Tool Comparison Charts</h2>
  <p class="chart-subtitle">analysis.json 기반 자동 생성 | 인터랙티브 차트는
    <a href="./dashboard.html">dashboard.html</a> 참조</p>

  <div class="chart-grid">
    <div class="chart-card">
      <h3>Overall Score (종합 점수)</h3>
      <canvas id="chartOverall" height="200"></canvas>
    </div>
    <div class="chart-card">
      <h3>Compliance vs Quality</h3>
      <canvas id="chartCompQual" height="200"></canvas>
    </div>
    <div class="chart-card">
      <h3>Sentinel 준수율</h3>
      <canvas id="chartSentinel" height="200"></canvas>
    </div>
    <div class="chart-card">
      <h3>평균 실행시간 (분)</h3>
      <canvas id="chartDuration" height="200"></canvas>
    </div>
  </div>

  <div class="chart-card chart-wide">
    <h3>Round별 Overall Score 추이</h3>
    <canvas id="chartTrend" height="120"></canvas>
  </div>

  <div class="chart-card chart-wide" id="hypothesisChartContainer" style="display:none">
    <h3>🔬 Hypothesis vs Actual (가설 검증)</h3>
    <canvas id="chartHypothesis" height="150"></canvas>
  </div>
</div>

<script>
(function() {{
  const tools = {_json.dumps(tools)};
  const overall = {_json.dumps(overall)};
  const compliance = {_json.dumps(compliance)};
  const quality = {_json.dumps(quality)};
  const duration = {_json.dumps(duration)};
  const startS = {_json.dumps(start_s)};
  const doneS = {_json.dumps(done_s)};
  const hypothesisData = {_json.dumps(hypothesis_data)};
  const toolColors = tools.map(t => ({{
    'copilot-cli': 'rgba(54,162,235,0.8)',
    'opencode-cli': 'rgba(75,192,192,0.8)',
    'codex-cli': 'rgba(255,159,64,0.8)',
    'cursor-cli': 'rgba(153,102,255,0.8)',
    'claude-code': 'rgba(255,99,132,0.8)',
  }})[t] || 'rgba(128,128,128,0.8)');
  const toolBorders = toolColors.map(c => c.replace('0.8', '1'));

  // 1. Overall Score bar chart
  new Chart(document.getElementById('chartOverall'), {{
    type: 'bar',
    data: {{
      labels: tools,
      datasets: [{{ label: 'Overall Score', data: overall,
        backgroundColor: toolColors, borderColor: toolBorders, borderWidth: 1 }}]
    }},
    options: {{
      indexAxis: 'y',
      scales: {{ x: {{ min: 0, max: 100 }} }},
      plugins: {{ legend: {{ display: false }} }}
    }}
  }});

  // 2. Compliance vs Quality grouped bar
  new Chart(document.getElementById('chartCompQual'), {{
    type: 'bar',
    data: {{
      labels: tools,
      datasets: [
        {{ label: 'Compliance %', data: compliance,
           backgroundColor: 'rgba(54,162,235,0.6)', borderColor: 'rgba(54,162,235,1)', borderWidth: 1 }},
        {{ label: 'Quality', data: quality,
           backgroundColor: 'rgba(75,192,192,0.6)', borderColor: 'rgba(75,192,192,1)', borderWidth: 1 }}
      ]
    }},
    options: {{ scales: {{ y: {{ min: 50, max: 100 }} }} }}
  }});

  // 3. Sentinel compliance grouped bar
  new Chart(document.getElementById('chartSentinel'), {{
    type: 'bar',
    data: {{
      labels: tools,
      datasets: [
        {{ label: 'START Sentinel %', data: startS,
           backgroundColor: 'rgba(54,162,235,0.6)', borderWidth: 1 }},
        {{ label: 'DONE Sentinel %', data: doneS,
           backgroundColor: 'rgba(255,206,86,0.6)', borderWidth: 1 }}
      ]
    }},
    options: {{ scales: {{ y: {{ min: 50, max: 100 }} }} }}
  }});

  // 4. Duration bar
  new Chart(document.getElementById('chartDuration'), {{
    type: 'bar',
    data: {{
      labels: tools,
      datasets: [{{ label: 'Avg Duration (min)', data: duration,
        backgroundColor: toolColors, borderColor: toolBorders, borderWidth: 1 }}]
    }},
    options: {{ plugins: {{ legend: {{ display: false }} }} }}
  }});

  // 5. Round trend line chart
  const trendData = {_json.dumps(trend_data)};
  const rounds = {_json.dumps([f"R{r}" for r in rounds_set])};
  const trendDatasets = Object.keys(trendData).sort().map(tool => ({{
    label: tool,
    data: trendData[tool],
    borderColor: ({{
      'copilot-cli': 'rgba(54,162,235,1)',
      'opencode-cli': 'rgba(75,192,192,1)',
      'codex-cli': 'rgba(255,159,64,1)',
      'cursor-cli': 'rgba(153,102,255,1)',
      'claude-code': 'rgba(255,99,132,1)',
    }})[tool] || 'rgba(128,128,128,1)',
    fill: false,
    tension: 0.3,
    pointRadius: 2,
    spanGaps: true,
  }}));

  new Chart(document.getElementById('chartTrend'), {{
    type: 'line',
    data: {{ labels: rounds, datasets: trendDatasets }},
    options: {{
      scales: {{ y: {{ min: 30, max: 100 }} }},
      plugins: {{ legend: {{ position: 'bottom' }} }}
    }}
  }});

  // 6. Hypothesis vs Actual rank comparison
  if (hypothesisData && Array.isArray(hypothesisData.hypotheses)) {{
    const oh = hypothesisData.hypotheses.find(h => h.metric === 'overall_score' && Array.isArray(h.expected_ranking));
    if (oh) {{
      const expectedRanking = oh.expected_ranking.filter(t => tools.includes(t));
      if (expectedRanking.length) {{
        const actualRanked = [...tools];
        const labels = expectedRanking;
        const expectedPos = expectedRanking.map((_, i) => i + 1);
        const actualPos = expectedRanking.map(t => {{
          const idx = actualRanked.indexOf(t);
          return idx >= 0 ? idx + 1 : null;
        }});
        const rankMax = Math.max(expectedRanking.length, actualRanked.length, 5);
        const hypTitle = oh.statement
          ? `가설: ${{oh.statement.length > 80 ? oh.statement.slice(0, 77) + '...' : oh.statement}}`
          : 'Expected Rank vs Actual Rank';

        document.getElementById('hypothesisChartContainer').style.display = 'block';
        new Chart(document.getElementById('chartHypothesis'), {{
          type: 'bar',
          data: {{
            labels,
            datasets: [
              {{
                label: 'Expected Rank',
                data: expectedPos,
                backgroundColor: 'rgba(54,162,235,0.6)',
                borderColor: 'rgba(54,162,235,1)',
                borderWidth: 1,
              }},
              {{
                label: 'Actual Rank',
                data: actualPos,
                backgroundColor: 'rgba(255,99,132,0.6)',
                borderColor: 'rgba(255,99,132,1)',
                borderWidth: 1,
              }}
            ]
          }},
          options: {{
            scales: {{
              y: {{
                reverse: true,
                min: 1,
                max: rankMax,
                ticks: {{ stepSize: 1 }},
                title: {{ display: true, text: 'Rank (lower is better)' }}
              }}
            }},
            plugins: {{
              legend: {{ position: 'bottom' }},
              title: {{ display: true, text: hypTitle }}
            }}
          }}
        }});
      }}
    }}
  }}
}})();
</script>
"""


def _get_comprehensive_css() -> str:
    """CSS for comprehensive_report.html (report + charts + sidebar)."""
    return """
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       margin: 0; padding: 20px; padding-left: 280px; background: #fafafa; color: #333;
       transition: padding-left 0.3s; }
.container { max-width: 1200px; background: #fff; padding: 30px; border-radius: 8px;
             box-shadow: 0 1px 3px rgba(0,0,0,.1); margin: 0 auto; }
h1 { color: #1a1a2e; border-bottom: 2px solid #16213e; padding-bottom: 10px; }
h2 { color: #16213e; margin-top: 30px; }
h3 { color: #0f3460; }
table { border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 14px; }
th { background: #16213e; color: #fff; padding: 10px 12px; text-align: left; position: sticky; top: 0; z-index: 1; }
th code { background: rgba(255,255,255,0.15); color: #fff; }
td { padding: 8px 12px; border-bottom: 1px solid #e0e0e0; }
tr:hover td { background: #f0f4ff; }
blockquote { border-left: 4px solid #16213e; padding: 10px 15px; margin: 15px 0;
             background: #f8f9fa; color: #555; }
code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
pre { background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 5px; overflow-x: auto; }
pre code { background: transparent; color: inherit; padding: 0; }
ul { padding-left: 25px; }
li { margin-bottom: 5px; }
a { color: #0066cc; }
.badge-pass { color: #28a745; }
.badge-fail { color: #dc3545; }
.badge-partial { color: #ffc107; }
/* Sidebar navigation */
.sidebar { position: fixed; top: 0; left: 0; width: 260px; height: 100vh; background: #1a1a2e;
           color: #ccc; overflow-y: auto; z-index: 100; transition: width 0.3s;
           box-shadow: 2px 0 8px rgba(0,0,0,.15); }
.sidebar.collapsed { width: 44px; overflow: hidden; }
.sidebar.collapsed .sidebar-content { display: none; }
.sidebar-toggle { padding: 12px 15px; cursor: pointer; background: #16213e; color: #fff;
                  font-size: 14px; font-weight: bold; position: sticky; top: 0; z-index: 2;
                  white-space: nowrap; }
.sidebar.collapsed .sidebar-toggle { padding: 12px; text-align: center; }
.sidebar-content { padding: 10px 0; }
.sidebar-content a { display: block; padding: 5px 15px; color: #aab; text-decoration: none;
                     font-size: 13px; line-height: 1.4; border-left: 3px solid transparent; }
.sidebar-content a:hover { background: #16213e; color: #fff; border-left-color: #4a9eff; }
.sidebar-content a.nav-h1 { font-weight: bold; font-size: 14px; padding-top: 10px; color: #eee; }
.sidebar-content a.nav-h2 { padding-left: 20px; color: #ccd; }
.sidebar-content a.nav-h3 { padding-left: 35px; font-size: 12px; color: #99a; }
/* Collapsible details */
details { margin: 15px 0; }
details summary { cursor: pointer; padding: 10px 15px; background: #f0f4ff; border-radius: 5px;
                  border: 1px solid #d0d9f0; font-weight: bold; color: #16213e; }
details summary:hover { background: #e0e8ff; }
details[open] summary { border-radius: 5px 5px 0 0; }
/* Chart dashboard */
.chart-dashboard { margin: 30px 0; padding: 20px; background: #f4f7ff; border-radius: 10px;
                   border: 1px solid #d0d9f0; }
.chart-dashboard h2 { color: #1a1a2e; margin-top: 0; }
.chart-subtitle { color: #666; font-size: 0.9em; margin-bottom: 20px; }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
.chart-card { background: #fff; padding: 15px; border-radius: 8px;
              box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.chart-card h3 { margin: 0 0 10px 0; font-size: 0.95em; color: #333; }
.chart-wide { grid-column: 1 / -1; }
@media (max-width: 900px) {
  body { padding-left: 20px; }
  .sidebar { width: 44px; overflow: hidden; }
  .sidebar .sidebar-content { display: none; }
  .sidebar:not(.collapsed) { width: 260px; overflow-y: auto; }
  .sidebar:not(.collapsed) .sidebar-content { display: block; }
  .chart-grid { grid-template-columns: 1fr; }
}
"""


def _md_to_html_import(md_text: str) -> str:
    """Delegate to lib/report._md_to_html for comprehensive report."""
    sys.path.insert(0, str(HERE))
    try:
        from lib.report import _md_to_html  # type: ignore
    finally:
        sys.path.pop(0)
    return _md_to_html(md_text)


def _generate_dashboard_html(report_dir: Path) -> None:
    """Generate a standalone interactive dashboard.html from analysis.json."""
    import json as _json

    json_path = report_dir / "analysis.json"
    if not json_path.is_file():
        return

    data = _json.loads(json_path.read_text(encoding="utf-8"))
    per_tool = data.get("per_tool", {})
    per_rt = data.get("per_round_tool", {})
    per_st = data.get("per_scenario_tool", {})
    meta = data.get("meta", {})

    if not per_tool:
        return

    # Prepare data
    ranked = sorted(per_tool.items(), key=lambda x: x[1].get("avg_overall_score", 0), reverse=True)
    tools = [t[0] for t in ranked]
    tools_sorted_alpha = sorted(per_tool.keys())

    # Round trend
    rounds_set = sorted({int(k.split("__")[0][1:]) for k in per_rt})
    trend_data = {}
    for tool in tools_sorted_alpha:
        trend_data[tool] = []
        for r in rounds_set:
            key = f"R{r}__{tool}"
            val = per_rt.get(key, {}).get("avg_overall_score", None)
            trend_data[tool].append(round(val, 1) if val is not None else None)

    # Scenario breakdown
    scenarios = sorted(meta.get("scenarios", []))
    scenario_data = {}
    for tool in tools_sorted_alpha:
        scenario_data[tool] = {}
        for sc in scenarios:
            key = f"{sc}__{tool}"
            val = per_st.get(key, {}).get("avg_overall_score", None)
            scenario_data[tool][sc] = round(val, 1) if val is not None else 0

    hyp_path = report_dir / "hypothesis.json"
    hypothesis_data = None
    if hyp_path.is_file():
        try:
            hypothesis_data = _normalize_hypothesis_tools(
                _json.loads(hyp_path.read_text(encoding="utf-8"))
            )
        except Exception:
            hypothesis_data = None

    # Radar dimensions (normalize to 0-100) — all 4 sub-scores + sentinel signals
    radar_dims = ["Overall", "Compliance", "Quality", "ExecutionTrace",
                  "Runnability", "START Sentinel", "DONE Sentinel"]
    radar_data = {}
    for tool, m in per_tool.items():
        radar_data[tool] = [
            round(m.get("avg_overall_score", 0), 1),
            round(m.get("avg_compliance_pct", 0), 1),
            round(m.get("avg_quality_score", 0), 1),
            round(m.get("avg_execution_score", 0), 1),
            round(m.get("avg_runnability_score", 0), 1),
            round(m.get("pct_with_start_sentinel", 0), 1),
            round(m.get("pct_with_done_sentinel", 0), 1),
        ]

    dashboard_data = {
        "meta": meta,
        "tools": tools,
        "tools_alpha": tools_sorted_alpha,
        "per_tool": {t: {
            "overall": round(m.get("avg_overall_score", 0), 1),
            "compliance": round(m.get("avg_compliance_pct", 0), 1),
            "quality": round(m.get("avg_quality_score", 0), 1),
            "execution": round(m.get("avg_execution_score", 0), 1),
            "runnability": round(m.get("avg_runnability_score", 0), 1),
            "stdev": round(m.get("stdev_overall_score", 0), 1),
            "duration_min": round(m.get("avg_duration_sec", 0) / 60, 1),
            "sessions": m.get("sessions", 0),
            "start_sentinel": round(m.get("pct_with_start_sentinel", 0), 1),
            "done_sentinel": round(m.get("pct_with_done_sentinel", 0), 1),
            "exit_0": round(m.get("pct_exit_0", 0), 1),
            "tool_calls": round(m.get("avg_tool_calls", 0), 1),
            "python_loc": round(m.get("avg_python_loc", 0), 0),
        } for t, m in per_tool.items()},
        "rounds": [f"R{r}" for r in rounds_set],
        "trend": trend_data,
        "scenarios": scenarios,
        "scenario_data": scenario_data,
        "radar_dims": radar_dims,
        "radar_data": radar_data,
        "hypothesis": hypothesis_data,
    }

    html = _DASHBOARD_TEMPLATE.replace("__DATA_PLACEHOLDER__", _json.dumps(dashboard_data, indent=2))
    out_path = report_dir / "dashboard.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"✓ Wrote dashboard: {out_path}")


_DASHBOARD_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DEEPX Agentic Development — E2E Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: #0f172a; color: #e2e8f0; }
.header { background: linear-gradient(135deg, #1e293b, #334155); padding: 30px 40px;
           border-bottom: 3px solid #3b82f6; }
.header h1 { font-size: 1.8em; color: #f1f5f9; margin-bottom: 5px; }
.header p { color: #94a3b8; font-size: 0.95em; }
.main { max-width: 1400px; margin: 0 auto; padding: 30px; }
.rank-section { margin-bottom: 30px; }
.rank-section h2 { color: #93c5fd; margin-bottom: 15px; font-size: 1.3em; }
.rank-table { width: 100%; border-collapse: collapse; background: #1e293b;
              border-radius: 8px; overflow: hidden; }
.rank-table th { background: #334155; color: #93c5fd; padding: 12px 15px;
                 text-align: left; font-size: 0.85em; text-transform: uppercase;
                 letter-spacing: 0.5px; }
.rank-table td { padding: 10px 15px; border-bottom: 1px solid #334155; font-size: 0.95em; }
.rank-table tr:hover td { background: #283548; }
.rank-table .medal { font-size: 1.2em; }
.rank-table .tool-name { font-weight: 600; color: #f1f5f9; }
.rank-table .score { font-weight: 700; }
.rank-table .score-high { color: #4ade80; }
.rank-table .score-mid { color: #facc15; }
.rank-table .score-low { color: #f87171; }
.score-bar { display: inline-block; height: 8px; border-radius: 4px; margin-left: 8px; vertical-align: middle; }
.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 25px 0; }
.chart-card { background: #1e293b; border-radius: 10px; padding: 20px;
              border: 1px solid #334155; }
.chart-card h3 { color: #93c5fd; margin-bottom: 12px; font-size: 1em; }
.chart-wide { grid-column: 1 / -1; }
.findings { background: #1e293b; border-radius: 10px; padding: 20px; margin: 25px 0;
            border: 1px solid #334155; }
.findings h2 { color: #93c5fd; margin-bottom: 15px; }
.findings ul { list-style: none; padding: 0; }
.findings li { padding: 8px 0; border-bottom: 1px solid #334155; font-size: 0.95em; }
.findings li:last-child { border-bottom: none; }
.findings .label { color: #94a3b8; display: inline-block; min-width: 180px; }
.findings .value { color: #f1f5f9; font-weight: 600; }
.footer { text-align: center; padding: 20px; color: #64748b; font-size: 0.85em; }
a { color: #60a5fa; }
@media (max-width: 900px) { .chart-grid { grid-template-columns: 1fr; } .main { padding: 15px; } }
</style>
</head>
<body>
<div class="header">
  <h1>📊 DEEPX Agentic Development — E2E Dashboard</h1>
  <p id="subtitle">Loading...</p>
</div>
<div class="main">
  <div class="rank-section"><h2>🏆 Tool Rankings (Overall Score)</h2>
    <table class="rank-table"><thead><tr>
      <th>Rank</th><th>Tool</th><th>Overall</th><th>Compliance</th>
      <th>Quality</th><th>ExecutionTrace</th><th>Runnability</th>
      <th>σ</th><th>Sessions</th><th>Avg Duration</th>
    </tr></thead><tbody id="rankBody"></tbody></table>
  </div>

  <div class="chart-grid">
    <div class="chart-card"><h3>Overall Score Comparison</h3><canvas id="cOverall"></canvas></div>
    <div class="chart-card"><h3>Radar — Multi-Dimension</h3><canvas id="cRadar"></canvas></div>
    <div class="chart-card"><h3>4 Sub-Scores (Compl / Qual / Exec / Runn)</h3><canvas id="cSubScores"></canvas></div>
    <div class="chart-card"><h3>Average Duration (min)</h3><canvas id="cDuration"></canvas></div>
    <div class="chart-card chart-wide"><h3>Round-over-Round Overall Score Trend</h3><canvas id="cTrend" height="100"></canvas></div>
    <div class="chart-card chart-wide"><h3>Scenario Breakdown (Overall Score per Tool × Scenario)</h3><canvas id="cScenario" height="100"></canvas></div>
    <div class="chart-card chart-wide" id="dashHypContainer" style="display:none"><h3>🔬 Hypothesis vs Actual — 가설 검증 차트</h3><canvas id="cHypothesis" height="120"></canvas></div>
  </div>

  <div class="findings"><h2>📋 Key Findings</h2><ul id="findingsList"></ul></div>
  <div class="footer">
    Generated by <code>analyze.py</code> | Data: <a href="./analysis.json">analysis.json</a>
    | Full report: <a href="./comprehensive_report.html">comprehensive_report.html</a>
  </div>
</div>

<script>
const D = __DATA_PLACEHOLDER__;
const COLORS = {
  'copilot-cli':  {bg:'rgba(54,162,235,0.7)',  border:'rgba(54,162,235,1)'},
  'opencode-cli': {bg:'rgba(75,192,192,0.7)',  border:'rgba(75,192,192,1)'},
  'codex-cli':    {bg:'rgba(255,159,64,0.7)',  border:'rgba(255,159,64,1)'},
  'cursor-cli':   {bg:'rgba(153,102,255,0.7)', border:'rgba(153,102,255,1)'},
  'claude-code':  {bg:'rgba(255,99,132,0.7)',  border:'rgba(255,99,132,1)'},
};
function tc(t) { return COLORS[t] || {bg:'rgba(128,128,128,0.7)',border:'rgba(128,128,128,1)'}; }
const medals = ['🥇','🥈','🥉'];

// Subtitle
document.getElementById('subtitle').textContent =
  `${D.meta.session_count} sessions | ${D.meta.tools.length} tools | ${D.meta.rounds.length} rounds | ${D.meta.scenarios.length} scenarios`;

// Ranking table
const rb = document.getElementById('rankBody');
D.tools.forEach((t,i) => {
  const m = D.per_tool[t];
  const cls = m.overall >= 75 ? 'score-high' : m.overall >= 65 ? 'score-mid' : 'score-low';
  const dur = `${Math.floor(m.duration_min)}m ${Math.round((m.duration_min%1)*60)}s`;
  const barW = Math.round(m.overall);
  rb.innerHTML += `<tr>
    <td class="medal">${i<3?medals[i]:i+1}</td>
    <td class="tool-name">${t}</td>
    <td class="score ${cls}">${m.overall}
      <span class="score-bar" style="width:${barW}px;background:${tc(t).bg}"></span></td>
    <td>${m.compliance}%</td><td>${m.quality}</td>
    <td>${m.execution}</td><td>${m.runnability}</td>
    <td>±${m.stdev}</td><td>${m.sessions}</td><td>${dur}</td></tr>`;
});

// Chart defaults
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = '#334155';

// 1. Overall bar (horizontal)
new Chart(document.getElementById('cOverall'), {
  type: 'bar',
  data: { labels: D.tools,
    datasets: [{ data: D.tools.map(t=>D.per_tool[t].overall),
      backgroundColor: D.tools.map(t=>tc(t).bg), borderColor: D.tools.map(t=>tc(t).border), borderWidth:1 }]
  },
  options: { indexAxis:'y', scales:{x:{min:0,max:100}}, plugins:{legend:{display:false}} }
});

// 2. Radar
new Chart(document.getElementById('cRadar'), {
  type: 'radar',
  data: { labels: D.radar_dims,
    datasets: D.tools_alpha.map(t=>({
      label: t, data: D.radar_data[t],
      borderColor: tc(t).border, backgroundColor: tc(t).bg.replace('0.7','0.15'),
      borderWidth: 2, pointRadius: 3,
    }))
  },
  options: { scales: { r: { min:50, max:100, ticks:{stepSize:10} } },
             plugins: { legend: { position:'bottom' } } }
});

// 3. 4 sub-scores grouped bar (Compl / Qual / Exec / Runn)
new Chart(document.getElementById('cSubScores'), {
  type: 'bar',
  data: { labels: D.tools,
    datasets: [
      { label:'Compliance %',   data: D.tools.map(t=>D.per_tool[t].compliance),
        backgroundColor:'rgba(54,162,235,0.6)' },
      { label:'Quality',        data: D.tools.map(t=>D.per_tool[t].quality),
        backgroundColor:'rgba(75,192,192,0.6)' },
      { label:'ExecutionTrace', data: D.tools.map(t=>D.per_tool[t].execution),
        backgroundColor:'rgba(255,159,64,0.6)' },
      { label:'Runnability',    data: D.tools.map(t=>D.per_tool[t].runnability),
        backgroundColor:'rgba(153,102,255,0.6)' }
    ]
  },
  options: { scales:{y:{min:0,max:100}}, plugins:{legend:{position:'bottom'}} }
});

// 4. Duration bar
new Chart(document.getElementById('cDuration'), {
  type: 'bar',
  data: { labels: D.tools,
    datasets: [{ data: D.tools.map(t=>D.per_tool[t].duration_min),
      backgroundColor: D.tools.map(t=>tc(t).bg), borderWidth:1 }]
  },
  options: { plugins:{legend:{display:false}} }
});

// 5. Round trend line
new Chart(document.getElementById('cTrend'), {
  type: 'line',
  data: { labels: D.rounds,
    datasets: D.tools_alpha.map(t=>({
      label: t, data: D.trend[t],
      borderColor: tc(t).border, fill:false, tension:0.3, pointRadius:2, spanGaps:true,
    }))
  },
  options: { scales:{y:{min:20,max:100}}, plugins:{legend:{position:'bottom'}} }
});

// 6. Scenario breakdown grouped bar
const scDatasets = D.tools_alpha.map(t=>({
  label: t, data: D.scenarios.map(s => D.scenario_data[t][s] || 0),
  backgroundColor: tc(t).bg, borderColor: tc(t).border, borderWidth:1,
}));
new Chart(document.getElementById('cScenario'), {
  type: 'bar',
  data: { labels: D.scenarios, datasets: scDatasets },
  options: { scales:{y:{min:0,max:100}}, plugins:{legend:{position:'bottom'}} }
});

// 7. Hypothesis vs Actual
if (D.hypothesis && Array.isArray(D.hypothesis.hypotheses)) {
  const oh = D.hypothesis.hypotheses.find(h => h.metric === 'overall_score' && Array.isArray(h.expected_ranking));
  if (oh) {
    const expRank = oh.expected_ranking.filter(t => D.tools.includes(t));
    if (expRank.length) {
      document.getElementById('dashHypContainer').style.display = 'block';
      const actualRanked = [...D.tools];
      const expectedPos = expRank.map((_, i) => i + 1);
      const actualPos = expRank.map(t => {
        const idx = actualRanked.indexOf(t);
        return idx >= 0 ? idx + 1 : null;
      });
      const hypTitle = oh.statement
        ? `가설: ${oh.statement.length > 80 ? oh.statement.slice(0, 77) + '...' : oh.statement}`
        : 'Expected Rank vs Actual Rank';

      new Chart(document.getElementById('cHypothesis'), {
        type: 'bar',
        data: {
          labels: expRank,
          datasets: [
            {
              label: 'Expected Rank',
              data: expectedPos,
              backgroundColor: 'rgba(54,162,235,0.6)',
              borderColor: 'rgba(54,162,235,1)',
              borderWidth: 1,
            },
            {
              label: 'Actual Rank',
              data: actualPos,
              backgroundColor: 'rgba(255,99,132,0.6)',
              borderColor: 'rgba(255,99,132,1)',
              borderWidth: 1,
            }
          ]
        },
        options: {
          scales: {
            y: {
              reverse: true,
              min: 1,
              max: Math.max(expRank.length, actualRanked.length, 5),
              ticks: { stepSize: 1 },
              title: { display: true, text: 'Rank (lower is better)' }
            }
          },
          plugins: {
            legend: { position: 'bottom' },
            title: { display: true, text: hypTitle }
          }
        }
      });
    }
  }
}

// Key findings
const fl = document.getElementById('findingsList');
const best = D.tools[0], worst = D.tools[D.tools.length-1];
const bm = D.per_tool[best], wm = D.per_tool[worst];
const fastest = D.tools_alpha.reduce((a,b) => D.per_tool[a].duration_min < D.per_tool[b].duration_min ? a : b);
const bestComp = D.tools_alpha.reduce((a,b) => D.per_tool[a].compliance > D.per_tool[b].compliance ? a : b);
const bestQual = D.tools_alpha.reduce((a,b) => D.per_tool[a].quality > D.per_tool[b].quality ? a : b);
[
  ['최고 종합 점수', `${best} (${bm.overall})`],
  ['최저 종합 점수', `${worst} (${wm.overall})`],
  ['점수 격차', `${(bm.overall-wm.overall).toFixed(1)}점 (${((bm.overall-wm.overall)/wm.overall*100).toFixed(1)}%)`],
  ['최고 Compliance', `${bestComp} (${D.per_tool[bestComp].compliance}%)`],
  ['최고 Quality', `${bestQual} (${D.per_tool[bestQual].quality})`],
  ['최단 평균 실행시간', `${fastest} (${Math.floor(D.per_tool[fastest].duration_min)}m ${Math.round((D.per_tool[fastest].duration_min%1)*60)}s)`],
].forEach(([lbl,val]) => { fl.innerHTML += `<li><span class="label">${lbl}</span><span class="value">${val}</span></li>`; });
</script>
</body>
</html>
"""


def _render_runnability_summary(report_dir: Path) -> str:
    """Build the slim Part 2 (runnability summary) — tables + key cases, no raw."""
    import json as _json
    import re as _re

    runn_path = report_dir / "runnability_report.md"
    analysis_json_path = report_dir / "analysis.json"

    if not runn_path.is_file():
        return ("# Part 2: End-User Runnability — 요약 (미실행)\n\n"
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
    lines.append("# Part 2: End-User Runnability — 요약")
    lines.append("")
    lines.append(f"> 평가된 세션: **{len(parsed)}** (raw: [`runnability_report.html`](./runnability_report.html))")
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


def _resolve_insights_cli(mode: str, *, allow_paid: Optional[bool] = None) -> Optional[str]:
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

    effective_allow_paid = True if allow_paid is None else allow_paid

    if mode == "auto":
        candidates = list(AUTO_CHAIN_PAID) if effective_allow_paid else list(AUTO_CHAIN_FREE)
    else:
        candidates = [mode]

    for c in candidates:
        binary = CLI_CONFIG.get(c, {}).get("binary", c)
        if shutil.which(binary):
            return c

    chain_label = "paid" if effective_allow_paid else "free"
    print()
    print(f"⚠ No agentic CLI available in {chain_label} chain ({candidates}). "
          f"Skipping insights/runnability steps.")
    return None


def _insights_common_args(report_dir: Path, chosen: str,
                           model: Optional[str], allow_paid: Optional[bool]) -> List[str]:
    args = ["--report-dir", str(report_dir), "--cli", chosen]
    if model:
        args += ["--model", model]
    if allow_paid is True:
        args += ["--allow-paid"]
    elif allow_paid is False:
        args += ["--no-allow-paid"]
    return args


def _run_runnability_step(report_dir: Path, chosen: str,
                           *, model: Optional[str] = None,
                           allow_paid: Optional[bool] = None,
                           existing_report: Optional[Path] = None) -> None:
    """Invoke insights.py --mode runnability (always exhaustive).
    Runs FIRST so its scores can be merged into analysis.md before the insights
    step reads it.
    """
    import subprocess

    insights_script = HERE / "insights.py"
    if not insights_script.is_file():
        return
    runn_timeout = 7200  # 2h for exhaustive evaluation
    common = _insights_common_args(report_dir, chosen, model, allow_paid)
    extra_args = []
    if existing_report and existing_report.is_file():
        extra_args += ["--existing-report", str(existing_report)]
        print(f"  (incremental: reusing {existing_report.name})")
    print()
    print(f"→ Step 1: insights.py --mode runnability --cli {chosen} "
          f"(EXHAUSTIVE)...")
    try:
        r = subprocess.run(
            ["python3", str(insights_script), "--mode", "runnability"] + common
            + extra_args,
            check=False, timeout=runn_timeout,
        )
        if r.returncode == 0:
            print("✓ runnability_report.md generated")
    except subprocess.TimeoutExpired:
        print(f"⚠ runnability check timed out (>{runn_timeout}s)")
    except Exception as e:
        print(f"⚠ runnability check failed: {e}")


def _run_hypothesis_step(report_dir: Path, chosen: str, prompt_path: Path,
                         *, model: Optional[str] = None,
                         allow_paid: Optional[bool] = None) -> None:
    """Invoke insights.py --mode hypothesis."""
    import subprocess

    insights_script = HERE / "insights.py"
    if not insights_script.is_file():
        return
    cmd = [sys.executable, str(insights_script),
           "--mode", "hypothesis",
           "--prompt", str(prompt_path),
           "--report-dir", str(report_dir),
           "--cli", chosen]
    if model:
        cmd.extend(["--model", model])
    if allow_paid is True:
        cmd.append("--allow-paid")
    elif allow_paid is False:
        cmd.append("--no-allow-paid")
    # When None → insights.py applies mode-specific default (paid for hypothesis)
    print(f"\n{'='*60}")
    print(f"Stage 4.5: Hypothesis generation via '{chosen}'")
    print(f"{'='*60}")
    try:
        r = subprocess.run(cmd, check=False, timeout=900)
        if r.returncode == 0:
            print("✓ hypothesis.json generated")
        else:
            print(f"⚠ hypothesis generation returned exit {r.returncode}")
    except subprocess.TimeoutExpired:
        print("⚠ hypothesis generation timed out (>900s)")
    except Exception as e:
        print(f"⚠ hypothesis generation failed: {e}")



def _run_insights_step(report_dir: Path, chosen: str,
                        *, model: Optional[str] = None,
                        allow_paid: Optional[bool] = None) -> None:
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
