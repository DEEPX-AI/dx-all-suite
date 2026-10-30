"""The studio's bundled benchmark data must mirror the standalone dx-benchmark tool."""

import json
import filecmp
from pathlib import Path

import pytest

_STUDIO = Path(__file__).resolve().parents[2]
_UPSTREAM = _STUDIO.parent / "dx-benchmark" / "results"

pytestmark = pytest.mark.skipif(
    not _UPSTREAM.is_dir(), reason="dx-benchmark is not checked out next to dx-ai-studio"
)


def test_dataset_matches_upstream_dashboard_dataset():
    studio = json.loads((_STUDIO / "dx_benchmark" / "dataset.json").read_text(encoding="utf-8"))
    upstream = json.loads((_UPSTREAM / "dashboard" / "dataset.json").read_text(encoding="utf-8"))
    assert studio == upstream


def test_results_tree_matches_upstream():
    studio_results = _STUDIO / "dx_benchmark" / "results"
    mismatches = []
    for env in sorted(p for p in _UPSTREAM.iterdir() if p.is_dir() and p.name != "dashboard"):
        cmp = filecmp.dircmp(env, studio_results / env.name)
        stack = [cmp]
        while stack:
            c = stack.pop()
            mismatches += [f"{c.left}: {n}" for n in c.left_only + c.right_only + c.diff_files]
            stack += list(c.subdirs.values())
    assert not mismatches, mismatches[:10]


def test_trend_chart_stacks_overlapping_labels():
    js = (_STUDIO / "dx_benchmark" / "static" / "js" / "dashboard.js").read_text(encoding="utf-8")
    assert "_stackTrendLabels" in js
    assert "TREND_LABEL_GAP" in js


def test_thermal_cooldown_display_matches_upstream_protocol():
    src = (_STUDIO / "dx_benchmark" / "server.py").read_text(encoding="utf-8")
    assert "CONFIG_THERMAL_COOLDOWN_MAX_SEC = 1000.0" in src
