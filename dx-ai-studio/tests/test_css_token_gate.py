"""Ratchet that keeps raw hex colors in module CSS (instead of tokens) going only down.

Existing uses are recorded in a baseline that may never rise, so any new raw hex fails at once.
"""
from __future__ import annotations

import json
from pathlib import Path

from scripts.css_token_gate import BASELINE_PATH, count_raw_hex, scan_modules

ROOT = Path(__file__).resolve().parent.parent


def test_scan_finds_every_module_css():
    counts = scan_modules(ROOT)
    assert "dx_app/static/css/style.css" in counts
    assert "launcher/static/style.css" in counts
    assert "shared/static/dx-tokens.css" not in counts, "primitive 토큰 파일은 대상이 아니다"


def test_count_raw_hex_ignores_css_variable_definitions():
    css = ":root{--a:#638CFF}\n.card{color:#FF0000;background:var(--a)}"
    assert count_raw_hex(css) == 1


def test_no_module_exceeds_its_baseline():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    counts = scan_modules(ROOT)
    over = {
        rel: (n, baseline.get(rel, 0))
        for rel, n in counts.items()
        if n > baseline.get(rel, 0)
    }
    assert not over, f"raw hex가 baseline을 초과했다 (토큰을 쓰세요): {over}"


def test_baseline_has_no_stale_headroom():
    """A baseline above the real count defeats the ratchet — when counts drop, lower the baseline too."""
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    counts = scan_modules(ROOT)
    stale = {
        rel: (counts.get(rel, 0), allowed)
        for rel, allowed in baseline.items()
        if counts.get(rel, 0) < allowed
    }
    assert not stale, (
        "baseline에 여유분이 남았다. `python scripts/css_token_gate.py --write`로 조인다: "
        f"{stale}"
    )
