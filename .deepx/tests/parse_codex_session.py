#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Parse Codex CLI session logs (JSONL) into self-contained HTML.

Codex ``exec --json`` emits line-delimited JSON events such as:
- ``thread.started``
- ``turn.started`` / ``turn.completed``
- ``item.completed``
- ``error``

This module parses those events into a lightweight session model and renders
an HTML transcript using shared helpers from ``session_common.py``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from session_common import (
    HTML_CSS,
    HTML_JS,
    ToolCall,
    extract_output_dirs_from_turns,
    format_timestamp,
    has_start_sentinel_in_turns,
    html_escape,
    md_to_html_simple,
    truncate,
)


@dataclass
class SessionMetadata:
    """Session metadata extracted from Codex JSONL."""

    session_id: str = ""
    cwd: str = ""
    summary: str = ""
    jsonl_path: Path = field(default_factory=Path)


@dataclass
class ConversationTurn:
    """A single conversation turn."""

    turn_index: int = 0
    user_content: str = ""
    assistant_content: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    timestamp: str = ""


@dataclass
class ParsedSession:
    """Fully parsed Codex session."""

    metadata: SessionMetadata
    selected_model: str = ""
    start_time: str = ""
    end_time: str = ""
    turns: List[ConversationTurn] = field(default_factory=list)
    raw_event_count: int = 0
    agent_label: str = "Codex"
    token_usage: Dict[str, int] = field(default_factory=dict)
    files_changed: List[Dict[str, str]] = field(default_factory=list)
    total_commands: int = 0
    failed_commands: int = 0


def extract_output_dirs(parsed: ParsedSession) -> List[str]:
    """Extract output-dir values from DONE sentinels in assistant responses."""
    return extract_output_dirs_from_turns(parsed.turns)


def has_start_sentinel(parsed: ParsedSession) -> bool:
    """Check whether any assistant turn contains the START sentinel."""
    return has_start_sentinel_in_turns(parsed.turns)


def parse_codex_jsonl(
    jsonl_path: Path,
    *,
    session_id_override: Optional[str] = None,
    scenario_key: Optional[str] = None,
    title: Optional[str] = None,
) -> ParsedSession:
    """Parse a Codex CLI JSONL file into a structured session."""
    jsonl_path = Path(jsonl_path)
    lines = jsonl_path.read_text(encoding="utf-8", errors="replace").splitlines()

    meta = SessionMetadata(summary=scenario_key or title or "")
    meta.jsonl_path = jsonl_path

    turns: List[ConversationTurn] = []
    current_turn: Optional[ConversationTurn] = None
    selected_model = ""
    start_time = ""
    end_time = ""
    token_usage: Dict[str, int] = {}
    files_changed: List[Dict[str, str]] = []
    total_commands = 0
    failed_commands = 0

    for raw_line in lines:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            continue

        etype = str(event.get("type", ""))
        event_ts = _extract_timestamp(event)
        if event_ts and not start_time:
            start_time = event_ts
        if event_ts:
            end_time = event_ts

        if etype == "thread.started":
            meta.session_id = (
                session_id_override
                or event.get("thread_id", "")
                or _dig(event, "thread", "id")
                or meta.session_id
            )
            meta.cwd = (
                event.get("cwd", "")
                or _dig(event, "thread", "cwd")
                or _dig(event, "thread", "workdir")
                or meta.cwd
            )
            selected_model = (
                event.get("model", "")
                or _dig(event, "thread", "model")
                or selected_model
            )
            continue

        if etype == "turn.started":
            if current_turn is not None:
                turns.append(current_turn)
            current_turn = ConversationTurn(
                turn_index=len(turns),
                user_content=_extract_user_text(event),
                timestamp=event_ts,
            )
            continue

        if etype == "item.completed":
            if current_turn is None:
                current_turn = ConversationTurn(turn_index=len(turns), timestamp=event_ts)
            item = event.get("item", {}) or {}
            item_type = str(item.get("type", ""))
            if item_type == "agent_message":
                text = _extract_agent_text(item)
                if text:
                    if current_turn.assistant_content:
                        current_turn.assistant_content += "\n" + text
                    else:
                        current_turn.assistant_content = text
            elif item_type == "file_change":
                fc_path = item.get("path", item.get("filename", ""))
                fc_kind = item.get("kind", item.get("action", "update"))
                if fc_path:
                    files_changed.append({"path": fc_path, "kind": fc_kind})
                tool_call = _extract_tool_call(item)
                if tool_call is not None:
                    current_turn.tool_calls.append(tool_call)
            elif item_type == "command_execution":
                total_commands += 1
                exit_code = item.get("exit_code")
                if exit_code is not None and exit_code != 0:
                    failed_commands += 1
                tool_call = _extract_tool_call(item)
                if tool_call is not None:
                    current_turn.tool_calls.append(tool_call)
            else:
                tool_call = _extract_tool_call(item)
                if tool_call is not None:
                    current_turn.tool_calls.append(tool_call)
            continue

        if etype == "turn.completed":
            usage = event.get("usage", {})
            if usage:
                for k, v in usage.items():
                    if isinstance(v, (int, float)):
                        token_usage[k] = token_usage.get(k, 0) + int(v)
            if current_turn is None:
                continue
            if not current_turn.user_content:
                current_turn.user_content = _extract_user_text(event)
            if not current_turn.assistant_content:
                text = _extract_agent_text(event.get("turn", {}) or {})
                if text:
                    current_turn.assistant_content = text
            if not current_turn.timestamp:
                current_turn.timestamp = event_ts
            turns.append(current_turn)
            current_turn = None
            continue

        if etype == "error":
            if current_turn is None:
                current_turn = ConversationTurn(turn_index=len(turns), timestamp=event_ts)
            message = (
                event.get("message", "")
                or event.get("error", "")
                or json.dumps(event, ensure_ascii=False)
            )
            current_turn.tool_calls.append(
                ToolCall(
                    tool_call_id=f"error-{len(current_turn.tool_calls)}",
                    tool_name="error",
                    arguments="",
                    success=False,
                    result_content=str(message),
                )
            )
            continue

    if current_turn is not None:
        turns.append(current_turn)

    if session_id_override:
        meta.session_id = session_id_override

    return ParsedSession(
        metadata=meta,
        selected_model=selected_model,
        start_time=start_time,
        end_time=end_time,
        turns=turns,
        raw_event_count=len(lines),
        agent_label="Codex",
        token_usage=token_usage,
        files_changed=files_changed,
        total_commands=total_commands,
        failed_commands=failed_commands,
    )


def render_html(session: ParsedSession, *, title: Optional[str] = None) -> str:
    """Render a ParsedSession as a self-contained HTML page."""
    meta = session.metadata
    page_title = title or meta.summary or f"{session.agent_label} Session {meta.session_id[:8]}"
    page_title = html_escape(page_title)

    entries: List[str] = []
    entry_idx = 0

    for turn in session.turns:
        time_label = format_timestamp(turn.timestamp) if turn.timestamp else ""

        if turn.user_content:
            entry_idx += 1
            entries.append(
                f'<div class="entry user" id="entry-{entry_idx}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">&#x1F464;</span>'
                f'<span class="label">User</span>'
                f'<span class="time">{time_label}</span>'
                f'</div>'
                f'<div class="entry-body">{html_escape(turn.user_content)}</div>'
                f'</div>'
            )

        for tc in turn.tool_calls:
            entry_idx += 1
            status_cls = "tool-ok" if tc.success else "tool-fail" if tc.success is False else "tool-ok"
            status_icon = "&#x2705;" if tc.success else "&#x274C;" if tc.success is False else "&#x2699;"
            args_html = ""
            if tc.arguments and tc.arguments != "{}":
                args_html = f'<div class="tool-args"><code>{html_escape(tc.arguments)}</code></div>'
            result_html = ""
            if tc.result_content:
                result_html = f'<div class="tool-result"><pre>{html_escape(truncate(tc.result_content, 4000))}</pre></div>'
            entries.append(
                f'<div class="entry {status_cls} collapsed" id="entry-{entry_idx}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">{status_icon}</span>'
                f'<span class="label">{html_escape(tc.tool_name)}</span>'
                f'<span class="time">click to expand</span>'
                f'</div>'
                f'<div class="entry-body">{args_html}{result_html}</div>'
                f'</div>'
            )

        if turn.assistant_content:
            entry_idx += 1
            entries.append(
                f'<div class="entry assistant" id="entry-{entry_idx}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">&#x1F4AC;</span>'
                f'<span class="label">{html_escape(session.agent_label)}</span>'
                f'<span class="time">{time_label}</span>'
                f'</div>'
                f'<div class="entry-body">{md_to_html_simple(turn.assistant_content)}</div>'
                f'</div>'
            )

    total_tools = sum(len(t.tool_calls) for t in session.turns)
    summary_rows = [
        f"<tr><td>Turns</td><td>{len(session.turns)}</td></tr>",
        f"<tr><td>Tool calls</td><td>{total_tools}</td></tr>",
        f"<tr><td>Commands</td><td>{session.total_commands} total, {session.failed_commands} failed</td></tr>",
        f"<tr><td>Events (raw)</td><td>{session.raw_event_count}</td></tr>",
    ]
    if session.selected_model:
        summary_rows.append(
            f"<tr><td>Model</td><td><code>{html_escape(session.selected_model)}</code></td></tr>"
        )
    if session.files_changed:
        fc_list = ", ".join(f"{fc.get('kind', '?')}: {fc.get('path', '?')}" for fc in session.files_changed[:20])
        if len(session.files_changed) > 20:
            fc_list += f" ... (+{len(session.files_changed) - 20} more)"
        summary_rows.append(
            f"<tr><td>Files changed</td><td>{len(session.files_changed)} — {html_escape(fc_list)}</td></tr>"
        )
    if session.token_usage:
        usage_parts = []
        for k in ["input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"]:
            v = session.token_usage.get(k, 0)
            if v:
                label = k.replace("_", " ").title()
                usage_parts.append(f"{label}: {v:,}")
        if usage_parts:
            summary_rows.append(
                f"<tr><td>Token Usage</td><td>{html_escape(', '.join(usage_parts))}</td></tr>"
            )

    summary_html = (
        '<div class="summary-section">'
        '<h2>Session Summary</h2>'
        '<table class="summary-table">'
        + "\n".join(summary_rows)
        + "</table></div>"
    )

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\" />
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
<title>{page_title}</title>
<style>{HTML_CSS}</style>
</head>
<body>
<div class=\"container\">
<h1>{page_title}</h1>
<table class=\"meta-table\">
<tr><td>Session ID</td><td><code>{html_escape(meta.session_id)}</code></td></tr>
<tr><td>Working Directory</td><td><code>{html_escape(meta.cwd)}</code></td></tr>
{f'<tr><td>Model</td><td><code>{html_escape(session.selected_model)}</code></td></tr>' if session.selected_model else ''}
<tr><td>Turns / Events</td><td>{len(session.turns)} turns, {session.raw_event_count} events</td></tr>
</table>
<hr />
{"".join(entries)}
{summary_html}
<div class=\"footer\">Generated by <code>parse_codex_session.py</code> at {now_utc}</div>
</div>
<script>{HTML_JS}</script>
</body>
</html>"""


def render_codex_html(jsonl_path: Path, output_path: Path, **kwargs) -> Optional[str]:
    """Convenience: parse a Codex JSONL and render to HTML in one call."""
    try:
        title = kwargs.pop("title", None)
        session = parse_codex_jsonl(jsonl_path, **kwargs)
        html = render_html(session, title=title)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
        return html
    except Exception:
        return None


def _extract_timestamp(event: Dict[str, Any]) -> str:
    """Extract a display timestamp from common Codex event fields."""
    for key in ("timestamp", "created_at"):
        value = event.get(key)
        if isinstance(value, str) and value:
            return value
    for key in ("timestamp_ms", "created_at_ms"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value / 1000.0).strftime("%Y-%m-%dT%H:%M:%S")
    return ""


def _extract_user_text(payload: Dict[str, Any]) -> str:
    """Extract user input text from turn-level payloads."""
    candidates = [
        payload.get("input"),
        _dig(payload, "turn", "input"),
        _dig(payload, "turn", "user_message"),
        _dig(payload, "turn", "prompt"),
        _dig(payload, "message", "text"),
    ]
    for value in candidates:
        text = _stringify_content(value)
        if text:
            return text
    return ""


def _extract_agent_text(payload: Dict[str, Any]) -> str:
    """Extract assistant text from a Codex agent-message payload."""
    candidates = [
        payload.get("text"),
        payload.get("content"),
        _dig(payload, "message", "content"),
        _dig(payload, "message", "text"),
        _dig(payload, "output", "text"),
        _dig(payload, "result", "text"),
    ]
    for value in candidates:
        text = _stringify_content(value)
        if text:
            return text
    return ""


def _extract_tool_call(item: Dict[str, Any]) -> Optional[ToolCall]:
    """Extract a tool call from a non-agent Codex item payload."""
    if not isinstance(item, dict):
        return None

    item_type = item.get("type", "")

    # Specialized handling for command_execution
    if item_type == "command_execution":
        command = item.get("command", "")
        output = item.get("aggregated_output", item.get("output", ""))
        exit_code = item.get("exit_code")
        success = (exit_code == 0) if exit_code is not None else None
        exit_badge = f" [exit: {exit_code}]" if exit_code is not None else ""
        return ToolCall(
            tool_call_id=str(item.get("id", f"cmd-{hash(str(command)) % 10000}")),
            tool_name=f"bash{exit_badge}",
            arguments=_stringify_content(command),
            success=success,
            result_content=_stringify_content(output),
        )

    # Specialized handling for file_change
    if item_type == "file_change":
        fc_path = item.get("path", item.get("filename", "unknown"))
        fc_kind = item.get("kind", item.get("action", "update"))
        icon = {"create": "📄+", "update": "📝", "delete": "🗑️"}.get(fc_kind, "📄")
        return ToolCall(
            tool_call_id=str(item.get("id", f"file-{fc_path}")),
            tool_name=f"file_change ({icon} {fc_kind})",
            arguments=fc_path,
            success=True,
            result_content=item.get("content", f"{fc_kind}: {fc_path}"),
        )

    tool_name = (
        item.get("name")
        or item.get("tool_name")
        or item.get("type")
        or item.get("role")
        or "tool"
    )
    arguments_obj = (
        item.get("arguments")
        or item.get("input")
        or item.get("params")
        or item.get("command")
        or {}
    )
    result_obj = (
        item.get("output")
        or item.get("result")
        or item.get("response")
        or item.get("error")
        or ""
    )
    success = None if "error" not in item else False
    if isinstance(result_obj, dict) and "error" in result_obj:
        success = False
    elif result_obj not in ("", None):
        success = True if success is None else success

    arguments = _stringify_content(arguments_obj) or ""
    result_content = _stringify_content(result_obj) or ""
    if tool_name == "agent_message" and not result_content and not arguments:
        return None
    return ToolCall(
        tool_call_id=str(item.get("id", "") or item.get("call_id", "") or f"tool-{tool_name}"),
        tool_name=str(tool_name),
        arguments=arguments,
        success=success,
        result_content=result_content,
    )


def _stringify_content(value: Any) -> str:
    """Convert a Codex content payload into readable text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        parts = [_stringify_content(v) for v in value]
        return "\n".join(part for part in parts if part)
    if isinstance(value, dict):
        for key in ("text", "content", "output_text", "message"):
            if key in value:
                text = _stringify_content(value[key])
                if text:
                    return text
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)
    return str(value)


def _dig(obj: Any, *keys: str) -> Any:
    """Safely walk nested dictionaries."""
    cur = obj
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur
