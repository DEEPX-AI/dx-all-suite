"""Gate test: zero High-severity findings for non-launcher modules.

This test runs the full extraction + classification pipeline across
all non-launcher modules and asserts that no High-severity findings
remain.  It must FAIL on the current baseline (51 non-launcher Highs)
and PASS after all i18n attribute and dictionary fixes are applied.
"""

from pathlib import Path

from tools.i18n_audit.classify import classify_records
from tools.i18n_audit.extractors import extract_inventory

_REPO_ROOT = Path(__file__).resolve().parents[2]

NON_LAUNCHER_MODULES = {
    "dx_app", "dx_stream", "dx_modelzoo",
    "dx_compiler", "dx_planner", "dx_benchmark", "dx_monitor",
    "shared", "unknown",
}


def test_no_high_findings_in_non_launcher_modules():
    """All non-launcher modules must have zero High-severity findings."""
    records = extract_inventory(_REPO_ROOT)
    findings = classify_records(records)

    non_launcher_highs = [
        f for f in findings
        if f.severity == "High"
        and not f.record_id.startswith("launcher:")
    ]

    if non_launcher_highs:
        summary = "\n".join(
            f"  {h.record_id}: {h.message}" for h in non_launcher_highs[:20]
        )
        raise AssertionError(  # noqa: intentional — pytest catches this
            f"{len(non_launcher_highs)} non-launcher High finding(s) remain:\n{summary}"
        )
