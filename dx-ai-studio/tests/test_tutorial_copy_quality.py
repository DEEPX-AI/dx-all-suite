"""Tutorial copy / translation quality — static audit over tutorial.js i18n maps."""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.i18n_audit.tutorial_copy import audit_tutorial_copy, extract_tutorial_records, format_report

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = (
    ROOT
    / "dx-agent-dev"
    / "20260625-094846_cursor_gpt55_tutorial_audit"
    / "tutorial-copy-quality-report.md"
)


def test_tutorial_records_cover_all_modules():
    records = extract_tutorial_records(ROOT)
    modules = {r.module for r in records}
    expected = {
        "dx_app",
        "dx_stream",
        "dx_modelzoo",
        "dx_planner",
        "dx_benchmark",
        "dx_monitor",
        "dx_agent_dev",
        "dx_compiler",
        "launcher",
    }
    missing = expected - modules
    assert not missing, f"tutorial.js missing for modules: {sorted(missing)}"


def test_tutorial_copy_no_missing_languages():
    findings, _ = audit_tutorial_copy(ROOT)
    missing = [f for f in findings if f.issue_type == "missing-language"]
    assert not missing, "\n".join(
        f"{f.record_id}: {f.message}" for f in missing[:40]
    )


def test_tutorial_js_has_no_dom_mock_markers():
    offenders = []
    for rel in ROOT.glob("**/static/js/tutorial.js"):
        if "dx_agent_dev" in rel.parts:
            continue
        src = rel.read_text(encoding="utf-8")
        if "data-dxt-tutorial-mock" in src:
            offenders.append(str(rel.relative_to(ROOT)))
    assert not offenders, "tutorial DOM mock markers forbidden: " + ", ".join(offenders)


def test_tutorial_copy_locale_and_tone_quality():
    """Long tutorial/help body fields must be translated (not identical to en)."""
    _, extra = audit_tutorial_copy(ROOT)
    hard = [e for e in extra if not e.startswith("[tone-hint]")]
    assert not hard, "\n".join(hard[:40])


def test_tutorial_copy_quality_report_written():
    """Run copy-quality scan and write report (informational counts — not a zero-defect gate)."""
    findings, extra = audit_tutorial_copy(ROOT)
    stale = [f for f in findings if f.issue_type == "stale-copy"]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    body = format_report(findings, extra)
    body += (
        f"\n\n## Summary counts\n\n"
        f"- Total findings: {len(findings)}\n"
        f"- Stale-copy: {len(stale)}\n"
        f"- Locale heuristics: {len(extra)}\n"
    )
    REPORT_PATH.write_text(body, encoding="utf-8")
    assert REPORT_PATH.exists()
