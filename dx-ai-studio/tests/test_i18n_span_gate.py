"""Ratchet that keeps per-language sibling span groups from growing.

Markup that writes one phrase six times (`<span class="ko">…</span><span class="en">…</span>…`)
keeps translations in two places, the dictionary and the markup, and once the two drift nobody
knows which is right. The remaining groups hold two phrases under one key and need a human
decision, so the gate only blocks new ones.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.i18n_span_gate import BASELINE_PATH, count_groups, scan
from scripts.migrate_i18n_spans import MODULES, _load_dict, _markup_files

ROOT = Path(__file__).resolve().parent.parent


def test_count_groups_needs_two_adjacent_language_spans():
    assert count_groups('<span class="ko">가</span>') == 0
    assert count_groups('<span class="ko">가</span><span class="en">a</span>') == 1


def test_no_file_exceeds_its_lang_span_baseline():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    counts = scan()
    over = {
        rel: (n, baseline.get(rel, 0))
        for rel, n in counts.items()
        if n > baseline.get(rel, 0)
    }
    assert not over, (
        "언어별 span 뭉치가 늘었다 — data-i18n=\"English key\" 를 쓰고 번역은 "
        f"모듈 사전에 넣으세요: {over}"
    )


def test_lang_span_baseline_has_no_stale_headroom():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    counts = scan()
    stale = {
        rel: (counts.get(rel, 0), allowed)
        for rel, allowed in baseline.items()
        if counts.get(rel, 0) < allowed
    }
    assert not stale, (
        "baseline 에 여유분이 남았다. `python scripts/i18n_span_gate.py --write` 로 "
        f"조인다: {stale}"
    )


_KEY = re.compile(r'data-i18n(?:-html)?="([^"]*)"')
GAP_BASELINE = ROOT / "config" / "i18n_key_gaps.json"
WANTED = ("ko", "ja", "zh-CN", "zh-TW", "es")


def _key_gaps() -> dict[str, dict[str, list[str]]]:
    """Keys the markup uses that the dictionary cannot fill → missing languages."""
    import html as _html

    out: dict[str, dict[str, list[str]]] = {}
    for name, (root, dict_rel) in MODULES.items():
        dictionary = _load_dict(dict_rel)
        for path in _markup_files(root):
            for raw in _KEY.findall(path.read_text()):
                key = _html.unescape(raw)
                entry = dictionary.get(key)
                if entry is None:
                    out.setdefault(name, {})[key] = list(WANTED)
                elif isinstance(entry, dict):
                    gaps = [lang for lang in WANTED if not entry.get(lang)]
                    if gaps:
                        out.setdefault(name, {})[key] = gaps
    return out


def test_no_new_untranslated_data_i18n_key():
    """A key the dictionary cannot fill shows in English on screen — the count must not grow.

    The remaining gaps are spots that only ever had ko/en text, so ja/zh/es fall back to
    English; the gate keeps that behavior and blocks new gaps. The launcher's about* keys are
    filled by ABOUT_NAV_LABELS in about-deepx.js, not by the dictionary.
    """
    baseline = json.loads(GAP_BASELINE.read_text(encoding="utf-8"))
    gaps = _key_gaps()
    new: dict[str, dict[str, list[str]]] = {}
    for module, keys in gaps.items():
        known = baseline.get(module, {})
        for key, langs in keys.items():
            grew = [lang for lang in langs if lang not in known.get(key, [])]
            if grew:
                new.setdefault(module, {})[key] = grew
    assert not new, (
        "번역이 없는 data-i18n key 가 늘었다 — 모듈 사전에 번역을 넣으세요: "
        f"{new}"
    )


def test_key_gap_baseline_has_no_stale_entries():
    baseline = json.loads(GAP_BASELINE.read_text(encoding="utf-8"))
    gaps = _key_gaps()
    stale = {
        module: [k for k in keys if k not in gaps.get(module, {})]
        for module, keys in baseline.items()
    }
    stale = {m: k for m, k in stale.items() if k}
    assert not stale, f"채워진 key 가 baseline 에 남아 있다: {stale}"
