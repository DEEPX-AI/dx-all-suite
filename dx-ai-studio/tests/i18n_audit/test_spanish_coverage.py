"""Gate test: zero Spanish missing-language findings across all modules.

Runs the live extraction + classification pipeline and asserts that no
'missing-language' findings mentioning 'es' remain.  Must FAIL on the
current baseline (4 536 Spanish findings) and PASS after all Spanish
locale values are added.
"""

from pathlib import Path

from tools.i18n_audit.classify import classify_records
from tools.i18n_audit.extractors import extract_inventory

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _mentions_es(message: str) -> bool:
    """Check if a missing-language message specifically lists 'es' as a missing locale."""
    # message format: "Missing locale values: es" or "Missing locale values: ja, es, zh-CN"
    prefix = "Missing locale values: "
    if not message.startswith(prefix):
        return False
    locales = [loc.strip() for loc in message[len(prefix):].split(",")]
    return "es" in locales


def test_no_spanish_missing_language_findings():
    """Every i18n record must include Spanish (es) locale coverage."""
    records = extract_inventory(_REPO_ROOT)
    findings = classify_records(records)

    spanish_missing = [
        f for f in findings
        if f.issue_type == "missing-language" and _mentions_es(f.message)
    ]

    if spanish_missing:
        summary = "\n".join(
            f"  {m.record_id}: {m.message}" for m in spanish_missing[:20]
        )
        raise AssertionError(
            f"{len(spanish_missing)} Spanish missing-language finding(s) remain:\n{summary}"
        )
