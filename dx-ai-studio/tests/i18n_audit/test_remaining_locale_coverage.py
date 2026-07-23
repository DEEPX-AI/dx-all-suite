"""Gate test: zero missing-language findings for ja, ko, zh-CN, zh-TW.

Runs the live extraction + classification pipeline and asserts that no
'missing-language' findings mentioning any of the four target locales
remain.  Must FAIL on the current baseline and PASS after all locale
values are added.
"""
from __future__ import annotations

from pathlib import Path

from tools.i18n_audit.classify import classify_records
from tools.i18n_audit.extractors import extract_inventory

_REPO_ROOT = Path(__file__).resolve().parents[2]

_TARGET_LOCALES = {"ja", "ko", "zh-CN", "zh-TW"}


def _mentioned_targets(message: str) -> set[str]:
    """Return the subset of target locales listed in a missing-language message."""
    prefix = "Missing locale values: "
    if not message.startswith(prefix):
        return set()
    locales = {loc.strip() for loc in message[len(prefix):].split(",")}
    return locales & _TARGET_LOCALES


def test_no_remaining_locale_missing_language_findings():
    """Every i18n record must include ja, ko, zh-CN, and zh-TW locale coverage."""
    records = extract_inventory(_REPO_ROOT)
    findings = classify_records(records)

    target_missing = [
        f for f in findings
        if f.issue_type == "missing-language" and _mentioned_targets(f.message)
    ]

    if target_missing:
        from collections import Counter
        by_lang: Counter[str] = Counter()
        for m in target_missing:
            for loc in _mentioned_targets(m.message):
                by_lang[loc] += 1
        summary_lines = [f"  {m.record_id}: {m.message}" for m in target_missing[:20]]
        raise AssertionError(
            f"{len(target_missing)} remaining missing-language finding(s) "
            f"for target locales {dict(by_lang)}:\n" + "\n".join(summary_lines)
        )
