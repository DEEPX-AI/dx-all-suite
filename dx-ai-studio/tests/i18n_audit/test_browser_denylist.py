"""Offline tests for browser stale-English denylist."""
from __future__ import annotations

from tools.i18n_audit.browser_denylist import (
    STALE_ENGLISH_PHRASES,
    find_stale_english_phrases,
)


def test_denylist_is_non_empty():
    assert len(STALE_ENGLISH_PHRASES) >= 5


def test_english_locale_skips_denylist():
    assert find_stale_english_phrases(
        "en",
        ("Select a model", "Agent running"),
    ) == []


def test_non_english_detects_stale_phrase():
    hits = find_stale_english_phrases(
        "ko",
        ("모델 선택", "Agent running"),
    )
    assert hits == ["Agent running"]


def test_runtime_not_switching_skips_denylist():
    assert find_stale_english_phrases(
        "ko",
        ("Agent running",),
        issue_type="runtime-not-switching",
    ) == []


def test_load_browser_evidence_denylist_gate():
    from pathlib import Path

    from tools.i18n_audit.browser_evidence import load_browser_evidence
    from tools.i18n_audit.browser_denylist import find_stale_english_phrases

    raw = __import__("os").environ.get("DX_I18N_AUDIT_ARTIFACT_DIR", "")
    if not raw:
        return
    violations: list[str] = []
    for obs in load_browser_evidence(Path(raw)):
        hits = find_stale_english_phrases(
            obs.get("locale", ""),
            tuple(obs.get("visible_text_sample") or ()),
            issue_type=obs.get("issue_type", "observed"),
        )
        if hits:
            violations.append(
                f"{obs.get('module')}/{obs.get('state')}@{obs.get('locale')}: {hits}"
            )
    assert violations == []
