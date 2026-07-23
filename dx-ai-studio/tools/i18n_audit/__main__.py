from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Six-Language Copy Audit CLI")
    parser.add_argument("--repo", type=Path, required=True, help="Repository root to scan")
    parser.add_argument("--browser-evidence-dir", type=Path, default=None, help="Directory with browser evidence JSON")
    parser.add_argument("--output-json", type=Path, required=True, help="Output JSON report path")
    parser.add_argument("--output-md", type=Path, required=True, help="Output Markdown report path")
    parser.add_argument("--fail-on-findings", action="store_true", help="Exit 2 if missing-language findings exist")
    parser.add_argument("--fail-on-runtime-not-switching", action="store_true", help="Exit 2 if runtime-not-switching evidence exists")
    parser.add_argument("--fail-on-integrity-issues", action="store_true", help="Exit 2 if placeholder/HTML integrity issues exist")
    parser.add_argument("--fail-on-runtime-gaps", action="store_true", help="Exit 2 if JS runtime lang-hook gaps exist")
    args = parser.parse_args()

    from .browser_evidence import load_browser_evidence
    from .classify import classify_records
    from .extractors import extract_inventory
    from .integrity import check_findings_gate, check_integrity_gate, check_runtime_switching_gate
    from .report import build_payload, write_json, write_markdown
    from .runtime_refresh import classify_runtime_gaps, extract_runtime_inventory, check_runtime_gaps_gate

    records = extract_inventory(args.repo)
    findings = classify_records(records)
    runtime_records = extract_runtime_inventory(args.repo)
    runtime_findings = classify_runtime_gaps(runtime_records)
    findings = findings + runtime_findings

    coverage_states = None
    if args.browser_evidence_dir and args.browser_evidence_dir.is_dir():
        coverage_states = load_browser_evidence(args.browser_evidence_dir)

    payload = build_payload(records, findings, coverage_states=coverage_states)
    write_json(payload, args.output_json)
    write_markdown(payload, args.output_md)

    print(f"records={len(records)} findings={len(findings)} runtime_js={len(runtime_records)}")

    # Strict gates — check after reports are written so output is always available
    if args.fail_on_integrity_issues:
        issues = check_integrity_gate(records)
        if issues:
            print("\n".join(issues), file=sys.stderr)
            return 2

    if args.fail_on_findings:
        msg = check_findings_gate(findings)
        if msg:
            print(msg, file=sys.stderr)
            return 2

    if args.fail_on_runtime_not_switching:
        msg = check_runtime_switching_gate(coverage_states)
        if msg:
            print(msg, file=sys.stderr)
            return 2

    if args.fail_on_runtime_gaps:
        msg = check_runtime_gaps_gate(runtime_findings)
        if msg:
            print(msg, file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
