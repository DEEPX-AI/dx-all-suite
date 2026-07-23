"""Gate test: zero stale-copy findings across all modules and locales."""

from pathlib import Path

from tools.i18n_audit.classify import classify_stale_copy
from tools.i18n_audit.extractors import extract_inventory

_REPO_ROOT = Path(__file__).resolve().parents[2]


def test_no_stale_copy_findings():
    """No locale should copy English verbatim when translation is expected."""
    records = extract_inventory(_REPO_ROOT)
    findings = classify_stale_copy(records)

    if findings:
        summary = "\n".join(
            f"  {f.record_id}: {f.message}" for f in findings[:20]
        )
        raise AssertionError(
            f"{len(findings)} stale-copy finding(s) remain:\n{summary}"
        )
