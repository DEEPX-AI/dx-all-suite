"""Single server-side path: adapter events → sanitized SSE payloads."""
from __future__ import annotations

from typing import Any, Optional

from dx_agent_dev.core.message_sanitize import extract_model_notice, is_harness_status_line, sanitize_assistant_text

# Agents that support native CLI thread resume (tested contract).
CLI_RESUME_AGENTS = frozenset({"cursor", "claude"})


def extract_cli_session_event(raw: dict) -> Optional[dict]:
    """Pull CLI session id from stream-json init events."""
    if not isinstance(raw, dict):
        return None
    kind = raw.get("type") or ""
    subtype = raw.get("subtype") or ""
    if kind == "system" and subtype == "init":
        sid = raw.get("session_id") or raw.get("sessionId")
        if sid:
            return {"type": "session", "cli_session_id": str(sid)}
    return None


def strip_harness_delta(chunk: str) -> str:
    """Fast path for streaming chunks — drop obvious harness fragments.

    Preserve whitespace-only deltas: in a token stream, a chunk that is just spaces/newlines
    is a real content separator between sentences/paragraphs. is_harness_status_line() treats
    blank as harness (correct for whole-line filtering, wrong here) — applying it to deltas
    swallowed the separators and ran text together ("…입니다.무엇을…"). Only test non-blank
    chunks against the harness matcher.
    """
    if not chunk:
        return ""
    if chunk.strip() and is_harness_status_line(chunk):
        return ""
    if "[DX-AGENT-DEV:" in chunk and "on-device NPU" in chunk:
        return ""
    return chunk


def prepare_message_text(text: str, *, delta: bool = False, final: bool = False) -> tuple[str, Optional[str]]:
    """Return (visible_text, model_notice)."""
    if not text:
        return "", None
    if delta and not final:
        return strip_harness_delta(text), None
    body, notice = extract_model_notice(text)
    return sanitize_assistant_text(body), notice


def prepare_sse_event(ev: dict) -> Optional[dict]:
    """Filter/normalize one adapter event for SSE. Returns None to skip send."""
    if not ev:
        return None
    if ev.get("type") == "session":
        return None
    if ev.get("hidden"):
        return None

    etype = ev.get("type")
    if etype != "message":
        return ev

    text = ev.get("text") or ""
    is_delta = bool(ev.get("delta"))
    is_final = bool(ev.get("final"))
    clean, notice = prepare_message_text(text, delta=is_delta, final=is_final)
    if not clean and is_delta:
        return None

    out = dict(ev)
    out["text"] = clean
    if notice:
        out["model_notice"] = notice
    return out
