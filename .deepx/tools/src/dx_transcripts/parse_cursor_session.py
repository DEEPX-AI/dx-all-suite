#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Parse Cursor session data into HTML.

Supports two input sources:
- Cursor CLI ``--output-format stream-json`` NDJSON
- Cursor persistent agent transcripts under ``~/.cursor/projects/.../agent-transcripts/``

Usage::

    # As a library
    from dx_transcripts.parse_cursor_session import parse_cursor_session, render_cursor_html
    session = parse_cursor_session(Path("path/to/stream.jsonl"))
    html = render_html(session)

    # Convenience: parse + write HTML in one call
    render_cursor_html(Path("stream.jsonl"), Path("output.html"))
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dx_transcripts.session_common import (
    HTML_CSS,
    HTML_JS,
    ToolCall,
    extract_output_dirs_from_turns,
    format_timestamp,
    has_start_sentinel_in_turns,
    html_escape,
    md_to_html_simple,
    truncate,
    ts_from_ms,
)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class SessionMetadata:
    """Session metadata from Cursor session sources."""

    session_id: str = ""
    cwd: str = ""
    summary: str = ""
    session_dir: Path = field(default_factory=Path)
    source_format: str = "stream"


@dataclass
class ConversationTurn:
    """A single conversation turn (user message + assistant response)."""

    turn_index: int = 0
    user_content: str = ""
    assistant_content: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    skills_invoked: List[str] = field(default_factory=list)
    timestamp: str = ""


@dataclass
class ParsedSession:
    """Fully parsed Cursor session data."""

    metadata: SessionMetadata
    selected_model: str = ""
    start_time: str = ""
    end_time: str = ""
    turns: List[ConversationTurn] = field(default_factory=list)
    raw_event_count: int = 0
    agent_label: str = "Cursor"


CURSOR_TRANSCRIPTS_BASE = Path.home() / ".cursor" / "projects"


# ---------------------------------------------------------------------------
# Sentinel helpers (delegate to session_common)
# ---------------------------------------------------------------------------


def extract_output_dirs(parsed: ParsedSession) -> List[str]:
    """Extract output-dir values from DONE sentinels in assistant responses."""
    return extract_output_dirs_from_turns(parsed.turns)


def has_start_sentinel(parsed: ParsedSession) -> bool:
    """Check whether any assistant turn contains the START sentinel."""
    return has_start_sentinel_in_turns(parsed.turns)


# ---------------------------------------------------------------------------
# Parser helpers
# ---------------------------------------------------------------------------


def count_user_turns(parsed: ParsedSession) -> int:
    """Return the number of non-empty user turns in the session.

    Used by lib/cost.py:compute_estimated_pr() as the primary signal for
    Premium Request estimation via user_turn_count × multiplier.  Empty
    or whitespace-only user content (system pings, automated prompts) does
    not count as a user-driven turn.
    """
    return sum(1 for t in parsed.turns if t.user_content.strip())


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def _encode_cursor_project_path(workdir: Path) -> str:
    workdir = Path(workdir).expanduser().resolve()
    return str(workdir).lstrip("/").replace("/", "-")


def _find_cursor_transcript(workdir: Path, after_utc: str, before_utc: str) -> Optional[Path]:
    project_dir = CURSOR_TRANSCRIPTS_BASE / _encode_cursor_project_path(Path(workdir)) / "agent-transcripts"
    if not project_dir.exists():
        return None

    after_dt = _parse_iso_datetime(after_utc)
    before_dt = _parse_iso_datetime(before_utc)
    candidates: List[Path] = []
    for candidate in project_dir.glob("*/*.jsonl"):
        if "subagents" in candidate.parts or not candidate.is_file():
            continue
        mtime = datetime.fromtimestamp(candidate.stat().st_mtime, tz=timezone.utc)
        if after_dt and mtime < after_dt:
            continue
        if before_dt and mtime > before_dt:
            continue
        candidates.append(candidate)

    if not candidates:
        return None
    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[0]


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def parse_cursor_stream_json(
    jsonl_path: Path,
    *,
    session_id_override: Optional[str] = None,
    scenario_key: Optional[str] = None,
) -> ParsedSession:
    """Parse a Cursor CLI ``--output-format stream-json`` NDJSON file.

    Converts Cursor events into a :class:`ParsedSession` structure.

    Args:
        jsonl_path: Path to the ``.jsonl`` file.
        session_id_override: Override session ID (for display).
        scenario_key: Scenario label shown in the HTML title.

    Returns:
        A :class:`ParsedSession` ready for :func:`render_html`.
    """
    jsonl_path = Path(jsonl_path)
    lines = jsonl_path.read_text(encoding="utf-8", errors="replace").splitlines()

    meta = SessionMetadata()
    meta.session_dir = jsonl_path.parent
    meta.source_format = "stream"

    turns: List[ConversationTurn] = []
    current_turn: Optional[ConversationTurn] = None
    thinking_parts: List[str] = []
    tc_start_ts: Dict[str, int] = {}
    selected_model = ""

    for raw_line in lines:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            continue

        etype = event.get("type", "")
        esubtype = event.get("subtype", "")
        ts_ms = event.get("timestamp_ms")

        # --- system/init ---
        if etype == "system" and esubtype == "init":
            meta.session_id = session_id_override or event.get("session_id", "")
            meta.cwd = event.get("cwd", "")
            meta.summary = scenario_key or ""
            selected_model = event.get("model", "")
            continue

        # --- user ---
        if etype == "user":
            msg = event.get("message", {})
            content_parts = []
            if isinstance(msg, dict):
                for cp in msg.get("content", []):
                    if isinstance(cp, dict):
                        content_parts.append(cp.get("text", ""))
                    elif isinstance(cp, str):
                        content_parts.append(cp)
            user_text = "\n".join(content_parts)
            current_turn = ConversationTurn(
                turn_index=len(turns),
                user_content=user_text,
                timestamp=ts_from_ms(ts_ms) if ts_ms else "",
            )
            turns.append(current_turn)
            thinking_parts.clear()
            continue

        # --- thinking ---
        if etype == "thinking":
            if esubtype == "delta":
                thinking_parts.append(event.get("text", ""))
            elif esubtype == "completed":
                if thinking_parts and current_turn is not None:
                    thinking_text = "".join(thinking_parts)
                    current_turn.tool_calls.append(ToolCall(
                        tool_call_id=f"thinking-{len(current_turn.tool_calls)}",
                        tool_name="🧠 thinking",
                        arguments="",
                        success=True,
                        result_content=thinking_text,
                    ))
                thinking_parts.clear()
            continue

        # --- tool_call ---
        if etype == "tool_call":
            if current_turn is None:
                current_turn = ConversationTurn(turn_index=len(turns))
                turns.append(current_turn)

            call_id = event.get("call_id", "")
            tc_data = event.get("tool_call", {})

            if esubtype == "started":
                if ts_ms:
                    tc_start_ts[call_id] = ts_ms
                tool_name, args_str = _extract_cursor_tool(tc_data)
                current_turn.tool_calls.append(ToolCall(
                    tool_call_id=call_id,
                    tool_name=tool_name,
                    arguments=args_str,
                    success=None,
                ))

            elif esubtype == "completed":
                for tc in reversed(current_turn.tool_calls):
                    if tc.tool_call_id == call_id:
                        tool_name_c, result_str = _extract_cursor_tool_result(tc_data)
                        tc.success = True
                        tc.result_content = result_str
                        if call_id in tc_start_ts and ts_ms:
                            tc.duration_ms = float(ts_ms - tc_start_ts[call_id])
                        break
            continue

        # --- assistant ---
        if etype == "assistant":
            if current_turn is None:
                current_turn = ConversationTurn(turn_index=len(turns))
                turns.append(current_turn)
            msg = event.get("message", {})
            if isinstance(msg, dict):
                for cp in msg.get("content", []):
                    if isinstance(cp, dict):
                        txt = cp.get("text", "")
                        if txt:
                            if current_turn.assistant_content:
                                current_turn.assistant_content += "\n" + txt
                            else:
                                current_turn.assistant_content = txt
            continue

        # --- result ---
        if etype == "result":
            continue

    session = ParsedSession(
        metadata=meta,
        selected_model=selected_model,
        turns=turns,
        raw_event_count=len(lines),
        agent_label="Cursor",
    )
    return session


def parse_cursor_jsonl(
    jsonl_path: Path,
    *,
    session_id_override: Optional[str] = None,
    scenario_key: Optional[str] = None,
) -> ParsedSession:
    """Backward-compatible alias for stream-json parsing."""
    return parse_cursor_stream_json(
        jsonl_path,
        session_id_override=session_id_override,
        scenario_key=scenario_key,
    )


def parse_cursor_transcript(transcript_path: Path) -> ParsedSession:
    """Parse a Cursor persistent agent transcript JSONL file."""
    transcript_path = Path(transcript_path).expanduser()
    lines = transcript_path.read_text(encoding="utf-8", errors="replace").splitlines()

    meta = SessionMetadata(
        session_id=transcript_path.stem,
        session_dir=transcript_path.parent,
        source_format="transcript",
    )
    turns: List[ConversationTurn] = []

    for raw_line in lines:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            entry = json.loads(raw_line)
        except json.JSONDecodeError:
            continue

        role = str(entry.get("role", ""))
        message = entry.get("message", {}) if isinstance(entry.get("message"), dict) else {}
        content = message.get("content", []) if isinstance(message.get("content"), list) else []
        turn = ConversationTurn(turn_index=len(turns))

        text_parts: List[str] = []
        for part in content:
            if not isinstance(part, dict):
                continue
            ptype = str(part.get("type", ""))
            if ptype == "text":
                text = part.get("text", "")
                if text:
                    text_parts.append(str(text))
                continue
            if ptype == "tool_use":
                tool_name = str(part.get("name", "unknown"))
                tool_input = part.get("input", {})
                turn.tool_calls.append(ToolCall(
                    tool_call_id=str(part.get("id", f"tool-{len(turn.tool_calls)}")),
                    tool_name=tool_name,
                    arguments=json.dumps(tool_input, indent=2, ensure_ascii=False) if isinstance(tool_input, (dict, list)) else str(tool_input),
                    success=True,
                    result_content="[transcript - no result recorded]",
                ))
                continue
            if ptype == "thinking":
                thinking_text = part.get("thinking") or part.get("text") or ""
                turn.tool_calls.append(ToolCall(
                    tool_call_id=str(part.get("id", f"thinking-{len(turn.tool_calls)}")),
                    tool_name="🧠 thinking",
                    arguments="",
                    success=True,
                    result_content=str(thinking_text),
                ))

        combined_text = "\n".join(text_parts).strip()
        if role == "user":
            turn.user_content = combined_text
        elif role == "assistant":
            turn.assistant_content = combined_text
        else:
            continue

        if turn.user_content or turn.assistant_content or turn.tool_calls:
            turns.append(turn)

    return ParsedSession(
        metadata=meta,
        turns=turns,
        raw_event_count=len(lines),
        agent_label="Cursor",
    )


def parse_cursor_session(
    jsonl_path: Path,
    *,
    session_id_override: Optional[str] = None,
    scenario_key: Optional[str] = None,
    workdir: Optional[Path] = None,
    after_utc: Optional[str] = None,
    before_utc: Optional[str] = None,
) -> ParsedSession:
    """Parse Cursor session data, preferring persistent transcripts over stream JSONL."""
    transcript_path: Optional[Path] = None
    if workdir is not None and (after_utc or before_utc):
        transcript_path = _find_cursor_transcript(Path(workdir), after_utc or "", before_utc or "")
    if transcript_path is not None:
        session = parse_cursor_transcript(transcript_path)
        session.metadata.summary = scenario_key or session.metadata.summary
        if session_id_override:
            session.metadata.session_id = session_id_override
        if workdir is not None:
            session.metadata.cwd = str(Path(workdir))
        return session
    return parse_cursor_stream_json(
        jsonl_path,
        session_id_override=session_id_override,
        scenario_key=scenario_key,
    )


# ---------------------------------------------------------------------------
# Tool extraction helpers
# ---------------------------------------------------------------------------


def _extract_cursor_tool(tc_data: Any) -> tuple:
    """Extract tool name and args string from Cursor tool_call/started data.

    Cursor uses ``{"readToolCall": {"args": {...}}}`` format.

    Returns:
        ``(tool_name, args_str)``
    """
    if not isinstance(tc_data, dict):
        return ("unknown", str(tc_data)[:200])
    for key, val in tc_data.items():
        nice_name = key.replace("ToolCall", "").replace("Tool", "")
        args = ""
        if isinstance(val, dict):
            args_dict = val.get("args", {})
            if isinstance(args_dict, dict):
                if "path" in args_dict:
                    args = args_dict["path"]
                elif "command" in args_dict:
                    args = args_dict["command"]
                else:
                    args = json.dumps(args_dict, ensure_ascii=False)
            else:
                args = str(args_dict)
        return (nice_name, args)
    return ("unknown", "")


def _extract_cursor_tool_result(tc_data: Any) -> tuple:
    """Extract tool name and result string from Cursor tool_call/completed data.

    Per-tool extractors handle the structurally different ``result.success``
    payloads emitted by Cursor for ``read``, ``shell``, ``edit``, and ``grep``.
    A common ``error`` short-circuit surfaces failures regardless of tool type.

    Returns:
        ``(tool_name, result_str)``
    """
    if not isinstance(tc_data, dict):
        return ("unknown", str(tc_data)[:500])
    for key, val in tc_data.items():
        nice_name = key.replace("ToolCall", "").replace("Tool", "")
        if not isinstance(val, dict):
            return (nice_name, str(val)[:2000])
        res = val.get("result", {})
        if not isinstance(res, dict):
            return (nice_name, str(res)[:2000])
        error = res.get("error", "")
        if error:
            return (nice_name, f"ERROR: {error}"[:2000])
        success = res.get("success", {})
        if not isinstance(success, dict):
            return (nice_name, str(success)[:2000] if success else "")
        result_str = _format_cursor_success(nice_name, success)
        return (nice_name, result_str[:2000])
    return ("unknown", "")


def _format_cursor_success(tool: str, success: Dict[str, Any]) -> str:
    """Format the ``success`` payload for a Cursor tool call into a string.

    Each Cursor tool emits a different ``success`` shape:
    - ``read``: ``{"content": "<file body>"}``
    - ``shell``: ``{"stdout", "stderr", "interleavedOutput", "exitCode", ...}``
    - ``edit``: ``{"path", "linesAdded", "linesRemoved", "diffString"}``
    - ``grep``: ``{"workspaceResults": {<root>: {"content": {"matches": [...]}}}}``
    """
    name = tool.lower()
    if name == "read":
        return str(success.get("content", ""))
    if name == "shell":
        stdout = success.get("stdout", "") or ""
        stderr = success.get("stderr", "") or ""
        if not stdout and not stderr:
            stdout = success.get("interleavedOutput", "") or ""
        exit_code = success.get("exitCode", 0)
        parts: List[str] = []
        if stdout:
            parts.append(stdout)
        if stderr:
            parts.append(f"[stderr]\n{stderr}")
        if exit_code:
            parts.append(f"[exit code: {exit_code}]")
        return "\n".join(parts)
    if name == "edit":
        diff = success.get("diffString", "") or ""
        path = success.get("path", "") or ""
        added = success.get("linesAdded", 0)
        removed = success.get("linesRemoved", 0)
        header = f"{path} (+{added}/-{removed})" if path else f"(+{added}/-{removed})"
        if diff:
            return f"{header}\n{diff}"
        return header
    if name == "grep":
        ws = success.get("workspaceResults", {}) or {}
        lines: List[str] = []
        if isinstance(ws, dict):
            for _root, body in ws.items():
                if not isinstance(body, dict):
                    continue
                content = body.get("content", {}) or {}
                matches = content.get("matches", []) if isinstance(content, dict) else []
                if not isinstance(matches, list):
                    continue
                for m in matches:
                    if not isinstance(m, dict):
                        continue
                    file_ = m.get("file", "")
                    inner = m.get("matches", [])
                    if isinstance(inner, list):
                        for hit in inner:
                            if isinstance(hit, dict):
                                line = hit.get("line", "")
                                text = hit.get("text", "")
                                lines.append(f"{file_}:{line}: {text}".rstrip())
                            else:
                                lines.append(f"{file_}: {hit}")
                    else:
                        lines.append(f"{file_}: {inner}")
        if lines:
            return "\n".join(lines)
        return json.dumps(success, ensure_ascii=False)
    if "content" in success:
        return str(success.get("content", ""))
    return json.dumps(success, ensure_ascii=False)


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------


def _thinking_html_rows(
    thinking_mode: str,
    thinking_args: Optional[Dict[str, str]],
    intended_model: str,
) -> List[str]:
    """HTML <tr> rows describing runner-supplied thinking metadata."""
    out: List[str] = []
    if thinking_mode:
        label = (
            "ON (TH — extended thinking / high reasoning effort)" if thinking_mode == "TH"
            else "OFF (NT — default reasoning)" if thinking_mode == "NT"
            else thinking_mode
        )
        out.append(f"<tr><td>확장사고 (Thinking)</td><td>{html_escape(label)}</td></tr>")
    if thinking_args:
        for k, v in thinking_args.items():
            out.append(
                f"<tr><td>Reasoning Arg</td><td><code>{html_escape(k)}={html_escape(v)}</code></td></tr>"
            )
    if intended_model:
        out.append(
            f"<tr><td>Intended Model</td><td><code>{html_escape(intended_model)}</code></td></tr>"
        )
    return out


def _build_html(
    session: ParsedSession,
    *,
    thinking_mode: str = "",
    thinking_args: Optional[Dict[str, str]] = None,
    intended_model: str = "",
) -> str:
    """Render a ParsedSession as a self-contained HTML page.

    ``thinking_*`` kwargs accept runner-supplied metadata appended to the
    meta-table when provided.
    """
    meta = session.metadata
    if meta.summary:
        title = html_escape(f"{session.agent_label} Session — {meta.summary}")
    else:
        title = html_escape(f"{session.agent_label} Session {meta.session_id[:8]}")

    entries: List[str] = []
    entry_idx = 0

    for turn in session.turns:
        time_label = format_timestamp(turn.timestamp) if turn.timestamp else ""

        if turn.user_content:
            entry_idx += 1
            user_text = html_escape(turn.user_content)
            entries.append(
                f'<div class="entry user" id="entry-{entry_idx}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">&#x1F464;</span>'
                f'<span class="label">User</span>'
                f'<span class="time">{time_label}</span>'
                f'</div>'
                f'<div class="entry-body">{user_text}</div>'
                f'</div>'
            )

        for tc in turn.tool_calls:
            entry_idx += 1
            status_cls = "tool-ok" if tc.success else "tool-fail" if tc.success is False else "tool-ok"
            status_icon = "&#x2705;" if tc.success else "&#x274C;" if tc.success is False else "&#x2699;"
            duration = f" ({tc.duration_ms:.0f}ms)" if tc.duration_ms else ""
            args_html = ""
            if tc.arguments and tc.arguments != "{}":
                args_html = f'<div class="tool-args"><code>{html_escape(tc.arguments)}</code></div>'
            result_html = ""
            if tc.result_content:
                truncated = truncate(tc.result_content, 1000)
                result_html = f'<div class="tool-result"><pre>{html_escape(truncated)}</pre></div>'

            if tc.tool_name == "🧠 thinking":
                status_cls = "thinking collapsed"
                status_icon = "&#x1F4AD;"
                duration = ""

            entries.append(
                f'<div class="entry {status_cls} collapsed" id="entry-{entry_idx}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">{status_icon}</span>'
                f'<span class="label">{html_escape(tc.tool_name)}</span>'
                f'<span>{duration}</span>'
                f'<span class="time">click to expand</span>'
                f'</div>'
                f'<div class="entry-body">{args_html}{result_html}</div>'
                f'</div>'
            )

        if turn.assistant_content:
            entry_idx += 1
            assistant_html = md_to_html_simple(turn.assistant_content)
            entries.append(
                f'<div class="entry assistant" id="entry-{entry_idx}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">&#x1F4AC;</span>'
                f'<span class="label">{html_escape(session.agent_label)}</span>'
                f'<span class="time">{time_label}</span>'
                f'</div>'
                f'<div class="entry-body">{assistant_html}</div>'
                f'</div>'
            )

    total_tools = sum(len(t.tool_calls) for t in session.turns)
    summary_rows = [
        f"<tr><td>Turns</td><td>{len(session.turns)}</td></tr>",
        f"<tr><td>Tool calls</td><td>{total_tools}</td></tr>",
        f"<tr><td>Events (raw)</td><td>{session.raw_event_count}</td></tr>",
        f"<tr><td>Source format</td><td><code>{html_escape(meta.source_format)}</code></td></tr>",
    ]
    if session.selected_model:
        summary_rows.append(f"<tr><td>Model</td><td><code>{html_escape(session.selected_model)}</code></td></tr>")

    summary_html = (
        '<div class="summary-section">'
        "<h2>Session Summary</h2>"
        '<table class="summary-table">'
        + "\n".join(summary_rows)
        + "</table></div>"
    )

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<style>{HTML_CSS}</style>
</head>
<body>
<div class="container">
<h1>{title}</h1>
<table class="meta-table">
<tr><td>Session ID</td><td><code>{html_escape(meta.session_id)}</code></td></tr>
<tr><td>Working Directory</td><td><code>{html_escape(meta.cwd)}</code></td></tr>
<tr><td>Source format</td><td><code>{html_escape(meta.source_format)}</code></td></tr>
{f"<tr><td>Model</td><td><code>{html_escape(session.selected_model)}</code></td></tr>" if session.selected_model else ""}
<tr><td>Turns / Events</td><td>{len(session.turns)} turns, {session.raw_event_count} events</td></tr>
{chr(10).join(_thinking_html_rows(thinking_mode, thinking_args, intended_model))}
</table>
<hr />
{"".join(entries)}
{summary_html}
<div class="footer">
Generated by <code>parse_cursor_session.py</code> at {now_utc}
</div>
</div>
<script>{HTML_JS}</script>
</body>
</html>"""


def render_html(
    session: ParsedSession,
    *,
    thinking_mode: str = "",
    thinking_args: Optional[Dict[str, str]] = None,
    intended_model: str = "",
) -> str:
    return _build_html(
        session,
        thinking_mode=thinking_mode,
        thinking_args=thinking_args,
        intended_model=intended_model,
    )


def render_cursor_html(
    jsonl_path: Path,
    output_path: Path,
    *,
    session_id_override: Optional[str] = None,
    scenario_key: Optional[str] = None,
    workdir: Optional[Path] = None,
    after_utc: Optional[str] = None,
    before_utc: Optional[str] = None,
    thinking_mode: str = "",
    thinking_args: Optional[Dict[str, str]] = None,
    intended_model: str = "",
) -> Optional[str]:
    """Convenience: parse a Cursor session source and render to HTML.

    Runner metadata (``thinking_*``) is forwarded to ``_build_html``.
    """
    try:
        session = parse_cursor_session(
            jsonl_path,
            session_id_override=session_id_override,
            scenario_key=scenario_key,
            workdir=workdir,
            after_utc=after_utc,
            before_utc=before_utc,
        )
        html = _build_html(
            session,
            thinking_mode=thinking_mode,
            thinking_args=thinking_args,
            intended_model=intended_model,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
        return html
    except Exception:
        return None
