# SPDX-License-Identifier: Apache-2.0
"""build_comparison must exclude env-failures via the lib.env_failure SSOT (T5).

Without this, the comparison report's tool-level means include rate-limit /
cert / model-refresh / incomplete-env sessions and drift from §6.3 (which
excludes them). See plan section 'Task 5'.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ANALYZER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ANALYZER))

import build_comparison as bc  # noqa: E402


def _row(**kw):
    base = dict(
        tool="claude-code", scenario="suite",
        overall_score="40", compliance_pct="60", quality_score="90",
        execution_score="0", runnability_score="50",
        has_start="False", has_done="False", exit_status_round="1",
        output_dirs="", output_tokens="0", tool_call_count="0",
        env_failure_signature="rate-limit", no_done_cause="env-rate-limit",
    )
    base.update(kw)
    return base


def test_env_failure_rows_excluded_from_aggregate_by_tool():
    good = _row(overall_score="96", has_done="True", env_failure_signature="",
                no_done_cause="", output_dirs="/x", output_tokens="2000",
                execution_score="85", exit_status_round="0")
    envf = _row()  # rate-limit env failure
    agg = bc.aggregate_by_tool([good, envf])
    # mean reflects ONLY the good row (96), not (96+40)/2=68
    assert abs(agg["claude-code"]["overall"] - 96.0) < 0.01


def test_env_failure_rows_excluded_from_pair_aggregate():
    good = _row(overall_score="96", has_done="True", env_failure_signature="",
                no_done_cause="", output_dirs="/x", output_tokens="2000",
                execution_score="85", exit_status_round="0")
    envf = _row()
    agg = bc.aggregate([good, envf])
    assert abs(agg[("claude-code", "suite")]["overall"] - 96.0) < 0.01


def test_csv_without_env_columns_falls_back_to_generic_criteria():
    # Older per_session.csv (pre-T3) has no env_failure_signature column.
    # The filter must still work using the generic A/B criteria (has_start,
    # has_done, exit_status_round, output_dirs, output_tokens, tool_call_count).
    rows = [
        # valid (has DONE) — keep
        {"tool": "t", "scenario": "s", "overall_score": "90", "compliance_pct":"90",
         "quality_score":"90", "execution_score":"90", "runnability_score":"90",
         "has_start":"True", "has_done":"True", "exit_status_round":"0",
         "output_dirs":"/x", "output_tokens":"1500", "tool_call_count":"20"},
        # incomplete env (criterion B: started, no done, exit!=0) — drop
        {"tool": "t", "scenario": "s", "overall_score": "30", "compliance_pct":"30",
         "quality_score":"30", "execution_score":"0", "runnability_score":"30",
         "has_start":"True", "has_done":"False", "exit_status_round":"1",
         "output_dirs":"", "output_tokens":"500", "tool_call_count":"5"},
    ]
    agg = bc.aggregate_by_tool(rows)
    assert abs(agg["t"]["overall"] - 90.0) < 0.01
