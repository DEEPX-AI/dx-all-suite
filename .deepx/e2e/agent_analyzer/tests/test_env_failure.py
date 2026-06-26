# SPDX-License-Identifier: Apache-2.0
"""Tests for lib/env_failure — shared env-failure detection (PR2).

Consolidates the env-failure classification used by both the analyzer
(skip_analyzer) and the runner repair. Covers the R11-R15 real cases:
  - claude R2-R5:   cert/SSL (partial output, no START)  → env failure
  - cursor R2-R4:   cert (0-byte stream)                 → env failure
  - opencode R2-R4: cert (UnknownError)                  → env failure
  - codex R1-R4:    model-refresh + 0 commands           → env failure
  - codex R5 compiler: model-refresh + 96 commands       → NOT env (real work)
  - claude/cursor incomplete (real work, no DONE)        → NOT env
"""
from __future__ import annotations

import sys
from pathlib import Path

_ANALYZER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ANALYZER))

from lib import env_failure as ef  # noqa: E402


# --- detect_env_signature ---------------------------------------------------

def test_detect_cert_claude_variant():
    assert ef.detect_env_signature("API Error: SSL certificate verification failed") == "cert"
    assert ef.detect_env_signature("Unable to connect to API: ...") == "cert"
    assert ef.detect_env_signature("proxy or corporate SSL certificate") == "cert"


def test_detect_cert_node_variant():
    assert ef.detect_env_signature("Error: unable to verify the first certificate") == "cert"


def test_detect_cert_opencode_unknownerror():
    txt = '{"type":"error","error":{"name":"UnknownError","data":{"message":"unable to verify"}}}'
    assert ef.detect_env_signature(txt) == "cert"


def test_detect_model_refresh_zero_commands():
    txt = "ERROR codex_models_manager: failed to refresh available models: timeout"
    assert ef.detect_env_signature(txt, command_count=0) == "model-refresh-timeout"


def test_model_refresh_with_commands_is_not_env():
    # codex R5 compiler: warning present but 96 commands of real work → NOT env
    txt = "failed to refresh available models: timeout\n... 96 commands ..."
    assert ef.detect_env_signature(txt, command_count=96) == ""


def test_detect_clean_text():
    assert ef.detect_env_signature("Inference complete. 39.6 FPS. RESULT: PASS") == ""
    assert ef.detect_env_signature("") == ""


# --- is_env_failure ---------------------------------------------------------

def test_cert_partial_output_no_start_is_env():
    # claude R2 compiler: cert error, some tokens, no START, no DONE
    assert ef.is_env_failure(
        env_signature="cert", has_start=False, has_done=False,
        has_output_dirs=True, output_tokens=500, tool_call_count=3,
    ) is True


def test_cert_no_output_is_env():
    # cursor/opencode suite: cert, no output at all
    assert ef.is_env_failure(
        env_signature="cert", has_start=False, has_done=False,
        has_output_dirs=False, output_tokens=0, tool_call_count=0,
    ) is True


def test_model_refresh_zero_commands_is_env():
    assert ef.is_env_failure(
        env_signature="model-refresh-timeout", has_start=False, has_done=False,
        has_output_dirs=True, output_tokens=10, tool_call_count=0,
    ) is True


def test_model_refresh_with_work_not_env():
    # codex R5 compiler: signature dropped by detect (command_count>0) → "" here
    assert ef.is_env_failure(
        env_signature="", has_start=False, has_done=False,
        has_output_dirs=True, output_tokens=5000, tool_call_count=96,
    ) is False


def test_valid_done_not_env():
    assert ef.is_env_failure(
        env_signature="", has_start=True, has_done=True,
        has_output_dirs=True, output_tokens=5000, tool_call_count=50,
    ) is False


def test_incomplete_with_exit_fail_is_env_b():
    # has_start, no DONE, exit != 0 (criterion B)
    assert ef.is_env_failure(
        env_signature="", has_start=True, has_done=False, exit_status=1,
        has_output_dirs=True, output_tokens=1000, tool_call_count=10,
    ) is True


def test_pre_execution_no_output_no_start_zero_tokens_is_env_a():
    assert ef.is_env_failure(
        env_signature="", has_start=False, has_done=False,
        has_output_dirs=False, output_tokens=0, tool_call_count=0,
    ) is True


def test_artifact_bug_not_env():
    # has_start + has_done but no output_dirs → artifact collection bug, not env
    assert ef.is_env_failure(
        env_signature="", has_start=True, has_done=True,
        has_output_dirs=False, output_tokens=100, tool_call_count=5,
    ) is False


# --- R11-R15 real-case verdict table (regression / SSOT parity guard) --------
# Locks in the field decisions made for the R11-R15 thinking batch. Both the
# analyzer (skip_analyzer.is_env_failure_eval) and the runner repair
# (PR3 e2e_runner --redo-env-failures) route through lib.env_failure, so this
# table is the single source of truth they must both agree with.
#
# Each row: (label, kwargs, expected_env_failure)
R11_R15_CASES = [
    # claude R2-R5: SSL cert error, partial tokens, no START/DONE → DELETE
    ("claude R2 compiler (cert)",
     dict(env_signature="cert", has_start=False, has_done=False,
          has_output_dirs=True, output_tokens=600, tool_call_count=4), True),
    ("claude R3 dx_app (cert)",
     dict(env_signature="cert", has_start=False, has_done=False,
          has_output_dirs=False, output_tokens=0, tool_call_count=0), True),
    # claude R1: completed with DONE → KEEP (scored)
    ("claude R1 (valid DONE)",
     dict(env_signature="", has_start=True, has_done=True,
          has_output_dirs=True, output_tokens=8000, tool_call_count=60), False),
    # codex R1-R4: model-refresh timeout, 0 commands → DELETE
    ("codex R1 (model-refresh, 0 cmd)",
     dict(env_signature="model-refresh-timeout", has_start=False, has_done=False,
          has_output_dirs=True, output_tokens=20, tool_call_count=0), True),
    # codex R5 compiler: model-refresh warning BUT 96 commands of real work.
    # detect_env_signature(command_count=96) returns "" upstream → not env.
    ("codex R5 compiler (96 cmd, incomplete-success)",
     dict(env_signature="", has_start=False, has_done=False,
          has_output_dirs=True, output_tokens=6000, tool_call_count=96), False),
    # opencode R1: UnknownError-wrapped cert → DELETE
    ("opencode R1 (UnknownError cert)",
     dict(env_signature="cert", has_start=False, has_done=False,
          has_output_dirs=False, output_tokens=0, tool_call_count=0), True),
    # cursor R1/R5 suite: real work (344/208 tool calls) then ECONNRESET, no DONE,
    # round exit non-zero → criterion B incomplete → treated as env (re-runnable).
    ("cursor R1 suite (ECONNRESET, exit!=0)",
     dict(env_signature="", has_start=True, has_done=False, exit_status=1,
          has_output_dirs=True, output_tokens=4000, tool_call_count=344), True),
    # copilot R1/R3/R5: completed → KEEP
    ("copilot R5 (valid DONE)",
     dict(env_signature="", has_start=True, has_done=True,
          has_output_dirs=True, output_tokens=7000, tool_call_count=55), False),
]


def test_r11_r15_verdict_table():
    failures = []
    for label, kwargs, expected in R11_R15_CASES:
        got = ef.is_env_failure(**kwargs)
        if got is not expected:
            failures.append(f"{label}: expected env={expected}, got {got}")
    assert not failures, "R11-R15 verdict mismatches:\n" + "\n".join(failures)


# --- rate-limit / session-limit (Anthropic CLI quota exhaustion) -------------

def test_detect_rate_limit_session_limit():
    assert ef.detect_env_signature(
        "You've hit your session limit · resets 8:40pm (Asia/Seoul)") == "rate-limit"
    assert ef.detect_env_signature("session limit · resets 9:00am") == "rate-limit"

def test_rate_limit_is_env_even_with_partial_output():
    # claude R3 suite: rate-limit text, derived out_dirs present, no START/DONE
    assert ef.is_env_failure(
        env_signature="rate-limit", has_start=False, has_done=False,
        has_output_dirs=True, output_tokens=0, tool_call_count=0) is True

def test_cert_priority_over_rate_limit():
    # cert is checked first; a mixed-signal blob must classify as cert, not rate-limit
    assert ef.detect_env_signature("API Error: SSL certificate verification failed") == "cert"
    assert ef.detect_env_signature(
        "SSL certificate verification failed; also hit your session limit") == "cert"

def test_bare_rate_limit_phrase_does_not_false_match():
    # benign mentions of "rate limit" must NOT be flagged (only specific phrasings)
    assert ef.detect_env_signature("Note: no rate limit applied to this endpoint.") == ""


# --- criterion-A derived-dir masking fix -------------------------------------

def test_zero_tokens_no_start_is_env_even_with_derived_dirs():
    # suite scenario inherits compiler/dx_app dirs (derived) but produced 0 tokens
    # and never emitted START → must be env failure, not a scored session.
    assert ef.is_env_failure(
        env_signature="", has_start=False, has_done=False,
        has_output_dirs=True, output_tokens=0, tool_call_count=0) is True

def test_real_work_with_dirs_still_not_env():
    # regression: codex R5 (96 cmds, 5000 tokens, real artifacts) stays non-env
    assert ef.is_env_failure(
        env_signature="", has_start=False, has_done=False,
        has_output_dirs=True, output_tokens=5000, tool_call_count=96) is False
