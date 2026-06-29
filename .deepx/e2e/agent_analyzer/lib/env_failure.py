# SPDX-License-Identifier: Apache-2.0
"""Shared environment-failure detection for the agent-driven E2E pipeline (PR2).

Single source of truth used by BOTH:
  - the analyzer (skip_analyzer.is_env_failure_eval) to exclude env-failed
    sessions from score averages, and
  - the runner repair (delete + re-run env-failed rounds).

An *environment failure* is a session that produced no useful work due to an
infrastructure issue (TLS/SSL cert, copilot empty session, codex model-refresh
timeout) — NOT a model-capability or compliance issue. Same root cause shows
different wording per CLI runtime, so all variants are catalogued here.

DONE-sentinel detection lives in session.py and scans the RENDERED transcript
(session.md/.html) only — never raw stream.jsonl — because the agent's `read`
tool can echo AGENTS.md/CLAUDE.md text containing the sentinel format
(false positive). Env *signature* detection, by contrast, may scan stream.jsonl
because the cert error genuinely lands there for cursor/opencode.
"""
from __future__ import annotations

from typing import Optional

# --- environment-failure signatures (same root cause, per-CLI wording) ------
CERT_SIGNATURES = (
    # cursor / opencode (node https)
    "unable to verify the first certificate",
    "verify the first certificate",
    # claude-code (Anthropic CLI)
    "SSL certificate verification failed",
    "Unable to connect to API",
    "proxy or corporate SSL certificate",
    # opencode wraps the cert error as an UnknownError event
    '"name":"UnknownError"',
)

# codex CLI cannot reach the copilot model-list endpoint
CODEX_INFRA_SIGNATURES = (
    "failed to refresh available models",
    "timeout waiting for child process",
)

# Anthropic/CLI usage-quota exhaustion (agent cannot run until reset). Environment
# failure, NOT capability — the round should be deleted + re-run after reset.
RATE_LIMIT_SIGNATURES = (
    "hit your session limit",
    "session limit · resets",
    "usage limit reached",
    # Specific quota phrasings only — the bare substring "rate limit" is avoided
    # because it false-matches benign text (e.g. "no rate limit applied", docs).
    "rate limit reached",
    "rate limit exceeded",
)


def detect_env_signature(text: str, *, command_count: Optional[int] = None) -> str:
    """Classify the env-failure signature in transcript ``text``.

    Returns one of: ``"cert"`` | ``"rate-limit"`` | ``"model-refresh-timeout"`` | ``""``.

    For codex model-refresh: when ``command_count`` is provided and > 0, the
    agent recovered and did real work (e.g. R5 compiler: 96 commands), so it is
    NOT an env failure — returns ``""``. Only 0/None commands → env failure.
    """
    if not text:
        return ""
    if any(sig in text for sig in CERT_SIGNATURES):
        return "cert"
    if any(sig in text for sig in RATE_LIMIT_SIGNATURES):
        return "rate-limit"
    if any(sig in text for sig in CODEX_INFRA_SIGNATURES):
        if command_count is not None and command_count > 0:
            return ""  # recovered, did real work → not an env failure
        return "model-refresh-timeout"
    return ""


def is_env_failure(
    *,
    env_signature: str = "",
    has_start: bool = False,
    has_done: bool = False,
    exit_status: Optional[int] = None,
    has_output_dirs: bool = False,
    output_tokens: int = 0,
    tool_call_count: int = 0,
) -> bool:
    """Return True if a session is an environment failure (exclude from scoring).

    Priority:
      1. SIGNATURE — explicit cert/rate-limit/model-refresh signature + no DONE.
         (model-refresh with real tool work is treated as non-env upstream by
         detect_env_signature returning "", but guard here too.)
      2. INCOMPLETE (criterion B) — started, no DONE, non-zero round exit.
      3. PRE-EXECUTION (criterion A) — zero output tokens + no START. Fires
         even when has_output_dirs is True, because those dirs are derived /
         inherited (e.g. the suite-fallback copies compiler+dx_app dirs) and
         must not mask a session that produced zero LLM output.
    A session WITH a DONE sentinel is never an env failure.
    """
    if has_done:
        return False

    # (1) explicit env signature
    if env_signature:
        if env_signature == "model-refresh-timeout" and tool_call_count > 0:
            return False  # recovered + did work
        return True

    # (2) incomplete: started but cut off with a failing exit
    if has_start and (exit_status or 0) != 0:
        return True

    # (3) pre-execution infra failure. A session that produced ZERO LLM output
    # tokens and never emitted START is an env failure even if has_output_dirs is
    # True — those dirs are derived/inherited (e.g. the suite fallback copies
    # compiler+dx_app dirs) and must not mask a session that did nothing.
    if output_tokens == 0 and not has_start:
        return True
    if has_output_dirs:
        return False
    if has_start:
        return False  # ran but artifacts not captured → artifact bug, not env
    # Unreachable for env=True: the zero-token / no-start case was handled above.
    # Kept defensive: if output_tokens is somehow negative/None-coerced upstream,
    # this returns False (not env) — safer than asserting.
    return False
