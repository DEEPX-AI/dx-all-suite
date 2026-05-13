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
from lib.report import write_markdown, write_json, write_csv
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
        help="(with --insights-runnability) number of sample sessions to evaluate",
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
    write_markdown(evals, md_path, meta)
    write_json(evals, json_path, meta)
    write_csv(evals, csv_path)

    print()
    print(f"Wrote: {md_path}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {csv_path}")

    # ---------------- Optional: auto-invoke insights.py ----------------
    if args.insights != "off":
        _run_insights_chain(out_dir, args.insights, args.insights_runnability,
                            args.insights_sample)

    # ---------------- Post-insights: merge runnability into scores ----------------
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
            # Rewrite reports with updated scores
            write_markdown(evals, md_path, meta)
            write_json(evals, json_path, meta)
            write_csv(evals, csv_path)
            print(f"  Rewrote: {md_path}")

    # ---------------- Comprehensive report ----------------
    _generate_comprehensive_report(out_dir)

    return 0


def _generate_comprehensive_report(report_dir: Path) -> None:
    """Merge analysis.md + insights.md + runnability_report.md into one comprehensive report."""
    parts: List[str] = []
    parts.append("# DEEPX Agentic Development — 종합 보고서 (Comprehensive Report)")
    parts.append("")
    parts.append(f"> 생성 시각: {datetime.now().isoformat(timespec='seconds')}")
    parts.append(f"> 이 보고서는 analysis.md, insights.md, runnability_report.md를 통합한 종합본입니다.")
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

    # Part 3: runnability_report.md
    runnability_path = report_dir / "runnability_report.md"
    if runnability_path.is_file():
        parts.append("# Part 3: End-User Runnability 평가 (runnability_report.md)")
        parts.append("")
        parts.append(runnability_path.read_text(encoding="utf-8"))
        parts.append("")
    else:
        parts.append("# Part 3: End-User Runnability 평가 (미실행)")
        parts.append("")
        parts.append("> runnability 평가가 실행되지 않았습니다.")
        parts.append("> 실행: `python3 insights.py --mode runnability --report-dir <dir> --cli <copilot|claude> --sample 8`")
        parts.append("")

    out_path = report_dir / "comprehensive_report.md"
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"\n✓ Wrote comprehensive report: {out_path}")


def _run_insights_chain(report_dir: Path, mode: str, also_runnability: bool,
                         sample: int) -> None:
    """Try to invoke insights.py automatically after analysis.

    `mode == 'auto'`: try copilot first, then claude, then cursor, then opencode.
    Otherwise: use the named CLI.

    Always saves the prompt file (insights_prompt.md) regardless of CLI availability,
    so the user can re-run manually.
    """
    import shutil
    import subprocess

    insights_script = HERE / "insights.py"
    if not insights_script.is_file():
        return

    candidates = []
    if mode == "auto":
        # Preferred order — copilot first per user guidance
        candidates = ["copilot", "claude", "cursor", "opencode", "codex"]
    else:
        candidates = [mode]

    # Map cli name → expected binary name
    binaries = {
        "copilot": "copilot", "claude": "claude",
        "cursor": "agent", "opencode": "opencode",
        "codex": "codex",
    }
    chosen = None
    for c in candidates:
        if shutil.which(binaries.get(c, c)):
            chosen = c
            break

    if not chosen:
        # No CLI available — still save the prompt so user can run later
        print()
        print(f"⚠ No agentic CLI available ({candidates}). Saving prompt only.")
        try:
            subprocess.run(
                ["python3", str(insights_script), "--mode", "insights",
                 "--report-dir", str(report_dir), "--cli", "copilot"],
                check=False, capture_output=True, timeout=30,
            )
        except Exception:
            pass
        print(f"  → run manually: python3 insights.py --mode insights "
              f"--report-dir {report_dir} --cli <claude|copilot|cursor|opencode>")
        return

    print()
    print(f"→ Invoking insights.py --mode insights --cli {chosen} (auto chain)...")
    try:
        r = subprocess.run(
            ["python3", str(insights_script), "--mode", "insights",
             "--report-dir", str(report_dir), "--cli", chosen],
            check=False, timeout=1200,
        )
        if r.returncode == 0:
            print(f"✓ insights.md generated (via {chosen})")
    except subprocess.TimeoutExpired:
        print(f"⚠ insights.py timed out (>20min); prompt saved for manual retry")
    except Exception as e:
        print(f"⚠ insights.py failed: {e}")

    if also_runnability:
        print()
        print(f"→ Invoking insights.py --mode runnability --cli {chosen} (sample={sample})...")
        try:
            r = subprocess.run(
                ["python3", str(insights_script), "--mode", "runnability",
                 "--report-dir", str(report_dir), "--cli", chosen,
                 "--sample", str(sample)],
                check=False, timeout=1800,
            )
            if r.returncode == 0:
                print(f"✓ runnability_report.md generated")
        except subprocess.TimeoutExpired:
            print(f"⚠ runnability check timed out")
        except Exception as e:
            print(f"⚠ runnability check failed: {e}")


if __name__ == "__main__":
    sys.exit(main())
