# SPDX-License-Identifier: Apache-2.0
"""Unit tests for build_comparison._report_rel (BUG-2 fix).

Covers two cases:
  1. report_dir IS inside an analyzer_reports/ tree  →  the original
     depth-counting relative path is produced.
  2. report_dir is NOT inside an analyzer_reports/ tree (e.g. a durable
     archive at $HOME/shared/coding_agent_diff_report/<label>/old/)  →
     falls back to ``<dirname>/comprehensive_report.html``.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ANALYZER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ANALYZER))

import build_comparison as bc  # noqa: E402


def test_report_rel_with_analyzer_reports_in_path():
    """Classic path: .../analyzer_reports/<run_id>/<ts>/  →  depth-counting link."""
    # Simulate: /some/project/analyzer_reports/20260612_123456/20260612_123456_v1/
    report_dir = Path("/some/project/analyzer_reports/20260612_123456/20260612_123456_v1")
    result = bc._report_rel(report_dir)
    # depth after "analyzer_reports" = 2 tokens ("20260612_123456" + "20260612_123456_v1")
    # → "../" * 2 + relative_to(parents[2]) = "analyzer_reports/20260612_123456/20260612_123456_v1"
    # full expected = "../../analyzer_reports/20260612_123456/20260612_123456_v1/comprehensive_report.html"
    assert result.endswith("/comprehensive_report.html")
    assert result.startswith("../../")
    assert "analyzer_reports" in result


def test_report_rel_without_analyzer_reports_in_path():
    """Durable-archive path without analyzer_reports → sibling fallback."""
    # Simulate: $HOME/shared/coding_agent_diff_report/20260612_opus48_vs_fable5_NTH/old
    report_dir = Path("/home/user/shared/coding_agent_diff_report/20260612_opus48_vs_fable5_NTH/old")
    result = bc._report_rel(report_dir)
    # comparison.html is written at <label>/ level; report_dir.name == "old"
    assert result == "old/comprehensive_report.html"


def test_report_rel_without_analyzer_reports_new_dir():
    """Same fallback for the 'new' (thinking) directory."""
    report_dir = Path("/home/user/shared/coding_agent_diff_report/20260612_opus48_vs_fable5_NTH/new")
    result = bc._report_rel(report_dir)
    assert result == "new/comprehensive_report.html"
