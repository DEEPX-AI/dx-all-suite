# SPDX-License-Identifier: Apache-2.0
"""Tests for the Premium Request estimation refactor (Phases A-D).

Covers:
- _lookup_multiplier: exact match, alias match, substring containment, default
- estimate_cost opencode-cli path: user_turn × multiplier primary, tool_call
  calibration fallback, token ratio tertiary fallback
- claude-code / cursor stream parsing: user_turn_count extraction from real
  result-dir samples (skipped if samples are not present on the system)

Run from .deepx/tests/:
    python3 -m pytest agent_analyzer/tests/test_pr_estimation.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Setup: import paths for the analyzer + parsers
# ---------------------------------------------------------------------------

THIS_DIR = Path(__file__).resolve().parent
ANALYZER_DIR = THIS_DIR.parent  # agent_analyzer/
TESTS_DIR = ANALYZER_DIR.parent  # tests/
sys.path.insert(0, str(ANALYZER_DIR))
sys.path.insert(0, str(TESTS_DIR))

from lib.cost import _lookup_multiplier, estimate_cost, CalibrationRatios  # noqa: E402
from lib.session import SessionData  # noqa: E402


# ---------------------------------------------------------------------------
# _lookup_multiplier
# ---------------------------------------------------------------------------

@pytest.fixture
def multiplier_table():
    """Subset of config.yaml's copilot_request_multiplier for unit tests."""
    return {
        "gpt-5-mini": 0,
        "claude-haiku-4.5": 0.33,
        "claude-sonnet-4.6": 1.0,
        "sonnet46": 1.0,
        "claude-opus-4.6": 3.0,
        "gpt-5.5": 7.5,
        "claude-opus-4.7": 15.0,
        "composer-2.5": 0,
        "composer25": 0,
        "_default": 1.0,
    }


def test_lookup_exact_match(multiplier_table):
    assert _lookup_multiplier("claude-sonnet-4.6", multiplier_table) == 1.0
    assert _lookup_multiplier("claude-opus-4.7", multiplier_table) == 15.0
    assert _lookup_multiplier("gpt-5.5", multiplier_table) == 7.5


def test_lookup_case_insensitive(multiplier_table):
    assert _lookup_multiplier("CLAUDE-SONNET-4.6", multiplier_table) == 1.0
    assert _lookup_multiplier("Claude-Opus-4.7", multiplier_table) == 15.0


def test_lookup_alias(multiplier_table):
    # "sonnet46" alias (used in session dir naming)
    assert _lookup_multiplier("sonnet46", multiplier_table) == 1.0


def test_lookup_substring_containment(multiplier_table):
    # Long model names containing a known key (e.g. thinking variant)
    # should fall through to substring matching, longest-key-first.
    assert _lookup_multiplier(
        "claude-sonnet-4.6-thinking-medium", multiplier_table
    ) == 1.0
    assert _lookup_multiplier(
        "claude-opus-4.7-thinking-high-fast", multiplier_table
    ) == 15.0


def test_lookup_default_for_unknown(multiplier_table):
    assert _lookup_multiplier("unknown-model", multiplier_table) == 1.0
    assert _lookup_multiplier("", multiplier_table) == 1.0
    assert _lookup_multiplier(None, multiplier_table) == 1.0  # type: ignore[arg-type]


def test_lookup_cursor_composer(multiplier_table):
    # Composer 2.5 = no PR (subscription model)
    assert _lookup_multiplier("composer-2.5", multiplier_table) == 0
    assert _lookup_multiplier("composer25", multiplier_table) == 0


def test_lookup_empty_table_returns_one():
    assert _lookup_multiplier("anything", {}) == 1.0


# ---------------------------------------------------------------------------
# estimate_cost — Phase D path priorities
# ---------------------------------------------------------------------------

@pytest.fixture
def pricing_config(multiplier_table):
    return {
        "copilot_premium_request": {"usd_per_request": 0.033},
        "copilot_request_multiplier": multiplier_table,
    }


# NOTE: the user_turn × multiplier PR estimator was removed (commit "drop
# user_turn × multiplier PR estimator"). tool_call × 0.741 is now the PRIMARY
# estimate; token-ratio is the fallback. These tests assert that landed behavior.

def test_opencode_tool_call_primary(pricing_config):
    """PRIMARY path: tool_call × 0.741 calibration (user_turn no longer used)."""
    cb = estimate_cost(
        tool="opencode-cli", model="claude-sonnet-4.6",
        input_tokens=1000, output_tokens=500,
        cache_read_tokens=0, cache_write_tokens=0,
        premium_requests=0,
        config_pricing=pricing_config,
        user_turn_count=3, tool_call_count=50,
    )
    assert cb.estimated_premium_requests == pytest.approx(37.05)  # 50 × 0.741
    assert "tool_call calibration" in cb.pricing_basis
    assert cb.usd_premium == pytest.approx(37.05 * 0.033)


def test_opencode_no_signal_when_tool_call_zero(pricing_config):
    """tool_call=0 + no token signal → no calibration signal (0 PR).

    Replaces the removed user_turn × opus-multiplier path: the request
    multiplier is no longer applied (the estimator it fed was removed)."""
    cb = estimate_cost(
        tool="opencode-cli", model="claude-opus-4.7",
        input_tokens=0, output_tokens=0, cache_read_tokens=0, cache_write_tokens=0,
        premium_requests=0,
        config_pricing=pricing_config,
        user_turn_count=2, tool_call_count=0,
    )
    assert cb.estimated_premium_requests == 0.0
    assert "calibration_unavailable" in cb.pricing_basis


def test_codex_tool_call_primary(pricing_config):
    """codex-cli also uses tool_call × 0.741 calibration (primary)."""
    cb = estimate_cost(
        tool="codex-cli", model="gpt-5.3-codex",
        input_tokens=0, output_tokens=0, cache_read_tokens=0, cache_write_tokens=0,
        premium_requests=0,
        config_pricing=pricing_config,
        user_turn_count=4, tool_call_count=10,
    )
    assert cb.estimated_premium_requests == pytest.approx(7.41)  # 10 × 0.741
    assert "Codex CLI" in cb.notes


def test_tool_call_calibration_is_primary(pricing_config):
    """tool_call × 0.741 is the PRIMARY premium-request estimate."""
    cb = estimate_cost(
        tool="opencode-cli", model="claude-sonnet-4.6",
        input_tokens=1000, output_tokens=500,
        cache_read_tokens=0, cache_write_tokens=0,
        premium_requests=0,
        config_pricing=pricing_config,
        user_turn_count=0, tool_call_count=100,
    )
    assert cb.estimated_premium_requests == pytest.approx(74.1)  # 100 × 0.741
    assert "tool_call calibration" in cb.pricing_basis
    assert "primary" in cb.pricing_basis


def test_fallback_to_token_ratio(pricing_config):
    """TERTIARY: no user_turn AND no tool_call → token ratio fallback."""
    calib = CalibrationRatios(tokens_per_premium=537.0)
    cb = estimate_cost(
        tool="opencode-cli", model="claude-sonnet-4.6",
        input_tokens=10000, output_tokens=5000,
        cache_read_tokens=0, cache_write_tokens=0,
        premium_requests=0,
        config_pricing=pricing_config,
        calibration=calib,
        user_turn_count=0, tool_call_count=0,
    )
    assert cb.estimated_premium_requests == pytest.approx(15000 / 537.0, rel=0.01)
    assert "token ratio" in cb.pricing_basis


def test_copilot_actual_premium_unchanged(pricing_config):
    """copilot-cli with actual premium_requests uses direct path, not user_turn."""
    cb = estimate_cost(
        tool="copilot-cli", model="claude-sonnet-4.6",
        input_tokens=10000, output_tokens=5000,
        cache_read_tokens=0, cache_write_tokens=0,
        premium_requests=12,
        config_pricing=pricing_config,
        user_turn_count=99, tool_call_count=99,   # would be ignored
    )
    assert cb.usd_premium == pytest.approx(12 * 0.033)
    assert "actual" in cb.pricing_basis


def test_cursor_auto_zero_cost(pricing_config):
    """cursor-cli with auto/composer model → 0 USD (subscription)."""
    cb = estimate_cost(
        tool="cursor-cli", model="auto",
        input_tokens=999999, output_tokens=999999,
        cache_read_tokens=0, cache_write_tokens=0,
        premium_requests=0,
        config_pricing=pricing_config,
        user_turn_count=10, tool_call_count=100,
    )
    assert cb.total_usd == 0.0
    assert "subscription" in cb.pricing_basis


# ---------------------------------------------------------------------------
# Stream parsing — Phase C user_turn extraction
# ---------------------------------------------------------------------------

# Real result-dir samples (skip if not present — keeps test portable across CI)
_RESULTS_ROOT = Path(
    "/data/home/dhyang/github/dx-all-suite-full-e2e/dx-agent-dev/e2e-tests/results"
)


def _find_sample(pattern: str) -> Path:
    if not _RESULTS_ROOT.is_dir():
        pytest.skip(f"results root not present: {_RESULTS_ROOT}")
    matches = sorted(_RESULTS_ROOT.glob(pattern))
    if not matches:
        pytest.skip(f"no sample matching: {pattern}")
    return matches[0]


def test_claude_code_user_turn_extraction():
    """claude-code stream: filter type=user with text content (not tool_result)."""
    from lib.session import _parse_claude_code_stream
    jsonl = _find_sample("*/*claude-code-autopilot/claude_code__compiler/*-stream.jsonl")
    sd = SessionData()
    _parse_claude_code_stream(jsonl, sd)
    # Real session has ~5 user prompts despite 50+ type=user wrapped events
    assert 1 <= sd.user_turn_count <= 20, (
        f"claude-code user_turn_count out of expected range: {sd.user_turn_count}"
    )


def test_cursor_user_turn_extraction():
    """cursor stream: 1 type=user per autopilot session (initial prompt)."""
    from lib.session import _parse_cursor_stream
    jsonl = _find_sample("*/*cursor-cli-autopilot/cursor_cli__compiler/*-stream.jsonl")
    sd = SessionData()
    _parse_cursor_stream(jsonl, sd)
    assert sd.user_turn_count >= 1, (
        f"cursor user_turn_count should be ≥1 (initial prompt), got {sd.user_turn_count}"
    )
