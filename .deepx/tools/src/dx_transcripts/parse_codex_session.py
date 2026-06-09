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
import re
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
)


_EXIT_CODE_RE = re.compile(r"(?:Process )?exited with code\s+(\d+)", re.IGNORECASE)
_WALL_TIME_RE = re.compile(r"Wall time:\s*([0-9.]+)\s*seconds", re.IGNORECASE)


@dataclass
class SessionMetadata:
    """Session metadata extracted from Codex JSONL."""

    session_id: str = ""
    cwd: str = ""
    summary: str = ""
    jsonl_path: Path = field(default_factory=Path)
    repository: str = ""
    branch: str = ""
    git_sha: str = ""
    model_provider: str = ""
    cli_version: str = ""


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


def count_user_turns(parsed: ParsedSession) -> int:
    """Return the number of non-empty user turns in the session.

    Used by lib/cost.py:compute_estimated_pr() as the primary signal for
    Premium Request estimation via user_turn_count × multiplier.  Empty
    or whitespace-only user content (system pings, automated prompts) does
    not count as a user-driven turn.
    """
    return sum(1 for t in parsed.turns if t.user_content.strip())


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

    events: List[Dict[str, Any]] = []
    for raw_line in lines:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            events.append(json.loads(raw_line))
        except json.JSONDecodeError:
            continue

    if events and str(events[0].get("type", "")) == "session_meta":
        return _parse_persistent_format(
            events,
            jsonl_path,
            raw_event_count=len(lines),
            session_id_override=session_id_override,
            scenario_key=scenario_key,
            title=title,
        )

    return _parse_exec_format(
        events,
        jsonl_path,
        raw_event_count=len(lines),
        session_id_override=session_id_override,
        scenario_key=scenario_key,
        title=title,
    )


def _parse_exec_format(
    events: List[Dict[str, Any]],
    jsonl_path: Path,
    *,
    raw_event_count: int,
    session_id_override: Optional[str] = None,
    scenario_key: Optional[str] = None,
    title: Optional[str] = None,
) -> ParsedSession:
    """Parse the original ``codex exec --json`` event stream."""
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

    for event in events:
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
        raw_event_count=raw_event_count,
        agent_label="Codex",
        token_usage=token_usage,
        files_changed=files_changed,
        total_commands=total_commands,
        failed_commands=failed_commands,
    )


def _parse_persistent_format(
    events: List[Dict[str, Any]],
    jsonl_path: Path,
    *,
    raw_event_count: int,
    session_id_override: Optional[str] = None,
    scenario_key: Optional[str] = None,
    title: Optional[str] = None,
) -> ParsedSession:
    """Parse persistent Codex JSONL sessions stored under ``~/.codex/sessions``."""
    meta = SessionMetadata(summary=scenario_key or title or "")
    meta.jsonl_path = jsonl_path

    turns: List[ConversationTurn] = []
    current_turn: Optional[ConversationTurn] = None
    pending_tool_calls: Dict[str, ToolCall] = {}
    pending_tool_names: Dict[str, str] = {}
    pending_tool_commands: Dict[str, bool] = {}
    selected_model = ""
    start_time = ""
    end_time = ""
    token_usage: Dict[str, int] = {}
    files_changed: List[Dict[str, str]] = []
    total_commands = 0
    failed_commands = 0
    last_user_text = ""
    deferred_outputs: Dict[str, tuple] = {}  # call_id → (payload, ts, name) for out-of-order outputs

    def flush_current_turn() -> None:
        nonlocal current_turn
        if current_turn is None:
            return
        if current_turn.user_content or current_turn.assistant_content or current_turn.tool_calls:
            current_turn.turn_index = len(turns)
            turns.append(current_turn)
        current_turn = None

    def ensure_current_turn(timestamp: str = "") -> ConversationTurn:
        nonlocal current_turn
        if current_turn is None:
            current_turn = ConversationTurn(turn_index=len(turns), timestamp=timestamp)
        elif timestamp and not current_turn.timestamp:
            current_turn.timestamp = timestamp
        return current_turn

    def append_user_text(text: str, timestamp: str = "") -> None:
        nonlocal current_turn, last_user_text
        text = text.strip()
        if not text:
            return
        if _normalized_text(text) == _normalized_text(last_user_text):
            return
        flush_current_turn()
        current_turn = ConversationTurn(turn_index=len(turns), user_content=text, timestamp=timestamp)
        last_user_text = text

    def append_assistant_text(text: str, timestamp: str = "") -> None:
        nonlocal current_turn
        text = text.strip()
        if not text:
            return
        if current_turn is None:
            current_turn = ConversationTurn(turn_index=len(turns), timestamp=timestamp)
        elif current_turn.assistant_content or current_turn.tool_calls:
            flush_current_turn()
            current_turn = ConversationTurn(turn_index=len(turns), timestamp=timestamp)
        elif timestamp and not current_turn.timestamp:
            current_turn.timestamp = timestamp
        current_turn.assistant_content = text

    def append_tool_call(tool_call: ToolCall, timestamp: str = "") -> None:
        turn = ensure_current_turn(timestamp)
        turn.tool_calls.append(tool_call)

    for event in events:
        etype = str(event.get("type", ""))
        payload = event.get("payload", {}) or {}
        event_ts = _extract_timestamp(event)
        if event_ts and not start_time:
            start_time = event_ts
        if event_ts:
            end_time = event_ts

        if etype == "session_meta":
            meta.session_id = (
                session_id_override
                or payload.get("id", "")
                or meta.session_id
            )
            meta.cwd = payload.get("cwd", "") or meta.cwd
            meta.model_provider = payload.get("model_provider", "") or meta.model_provider
            meta.cli_version = payload.get("cli_version", "") or meta.cli_version
            git_info = payload.get("git", {}) or {}
            meta.repository = (
                git_info.get("repository")
                or git_info.get("repository_url")
                or meta.repository
            )
            meta.branch = (
                git_info.get("branch")
                or git_info.get("branch_name")
                or meta.branch
            )
            meta.git_sha = (
                git_info.get("commit_hash")
                or git_info.get("sha")
                or git_info.get("commit")
                or meta.git_sha
            )
            start_time = payload.get("timestamp", "") or start_time
            continue

        if etype == "turn_context":
            meta.cwd = payload.get("cwd", "") or meta.cwd
            selected_model = (
                payload.get("model", "")
                or _dig(payload, "collaboration_mode", "settings", "model")
                or selected_model
            )
            git_info = payload.get("git", {}) or {}
            meta.repository = (
                git_info.get("repository")
                or git_info.get("repository_url")
                or meta.repository
            )
            meta.branch = (
                git_info.get("branch")
                or git_info.get("branch_name")
                or meta.branch
            )
            meta.git_sha = (
                git_info.get("commit_hash")
                or git_info.get("sha")
                or git_info.get("commit")
                or meta.git_sha
            )
            continue

        if etype == "event_msg":
            payload_type = str(payload.get("type", ""))
            if payload_type == "agent_message":
                append_assistant_text(_stringify_content(payload.get("message")), event_ts)
                continue
            if payload_type == "user_message":
                append_user_text(_stringify_content(payload.get("message")), event_ts)
                continue
            if payload_type == "task_complete":
                end_time = event_ts or end_time
                continue
            if payload_type == "token_count":
                for source in (payload.get("info"), payload.get("rate_limits")):
                    if isinstance(source, dict):
                        for k, v in source.items():
                            if isinstance(v, (int, float)):
                                token_usage[k] = token_usage.get(k, 0) + int(v)
                continue
            continue

        if etype != "response_item":
            continue

        payload_type = str(payload.get("type", ""))
        if payload_type == "reasoning":
            continue

        if payload_type == "message":
            role = str(payload.get("role", ""))
            text = _extract_message_text(payload.get("content"))
            if role == "assistant":
                append_assistant_text(text, event_ts)
            elif role == "user" and text and not _should_skip_persistent_user_message(text):
                append_user_text(text, event_ts)
            continue

        if payload_type in {"function_call", "custom_tool_call"}:
            tool_call = _extract_persistent_tool_call(payload)
            call_id = tool_call.tool_call_id or str(payload.get("call_id", ""))
            if call_id and call_id in deferred_outputs:
                # Merge with previously-buffered output (out-of-order case)
                out_payload, out_ts, _ = deferred_outputs.pop(call_id)
                raw_output = out_payload.get("output", "")
                output_text, output_meta = _extract_persistent_output(raw_output)
                tool_call.result_content = output_text
                tool_call.success = _infer_tool_success(output_text, output_meta)
                tool_call.duration_ms = _infer_tool_duration_ms(output_text, output_meta)
                append_tool_call(tool_call, out_ts or event_ts)
                if _is_command_tool_call(payload):
                    total_commands += 1
                    if tool_call.success is False:
                        failed_commands += 1
                files_changed.extend(_extract_files_changed(tool_call.result_content))
            elif call_id:
                pending_tool_calls[call_id] = tool_call
                pending_tool_names[call_id] = str(payload.get("name", tool_call.tool_name))
                pending_tool_commands[call_id] = _is_command_tool_call(payload)
            else:
                append_tool_call(tool_call, event_ts)
                if _is_command_tool_call(payload):
                    total_commands += 1
                    if tool_call.success is False:
                        failed_commands += 1
            continue

        if payload_type in {"function_call_output", "custom_tool_call_output"}:
            call_id = str(payload.get("call_id", ""))
            tool_call = pending_tool_calls.pop(call_id, None)
            original_name = pending_tool_names.pop(call_id, "")
            is_command = pending_tool_commands.pop(call_id, False)
            if tool_call is None:
                # Output arrived before its function_call (rare race).
                # Buffer it; if the matching call arrives later we merge.
                deferred_outputs[call_id] = (payload, event_ts, original_name)
                continue
            raw_output = payload.get("output", "")
            output_text, output_meta = _extract_persistent_output(raw_output)
            tool_call.result_content = output_text
            tool_call.success = _infer_tool_success(output_text, output_meta)
            tool_call.duration_ms = _infer_tool_duration_ms(output_text, output_meta)
            if not tool_call.tool_name:
                tool_call.tool_name = original_name or "tool"
            append_tool_call(tool_call, event_ts)
            if is_command:
                total_commands += 1
                if tool_call.success is False:
                    failed_commands += 1
            files_changed.extend(_extract_files_changed(tool_call.result_content))
            continue

    for call_id, tool_call in pending_tool_calls.items():
        append_tool_call(tool_call, "")
        if pending_tool_commands.get(call_id):
            total_commands += 1
            if tool_call.success is False:
                failed_commands += 1

    # Flush any deferred outputs that never got a matching function_call
    for call_id, (out_payload, out_ts, out_name) in deferred_outputs.items():
        raw_output = out_payload.get("output", "")
        output_text, output_meta = _extract_persistent_output(raw_output)
        orphan = ToolCall(
            tool_call_id=call_id,
            tool_name=out_name or str(out_payload.get("name", "tool")),
            result_content=output_text,
            success=_infer_tool_success(output_text, output_meta),
            duration_ms=_infer_tool_duration_ms(output_text, output_meta),
        )
        append_tool_call(orphan, out_ts)

    flush_current_turn()

    if session_id_override:
        meta.session_id = session_id_override

    return ParsedSession(
        metadata=meta,
        selected_model=selected_model,
        start_time=start_time,
        end_time=end_time,
        turns=turns,
        raw_event_count=raw_event_count,
        agent_label="Codex",
        token_usage=token_usage,
        files_changed=files_changed,
        total_commands=total_commands,
        failed_commands=failed_commands,
    )


def _thinking_md_lines(
    thinking_mode: str,
    thinking_args: Optional[Dict[str, str]],
    intended_model: str,
) -> List[str]:
    """Markdown bullets describing runner-supplied thinking metadata."""
    out: List[str] = []
    if thinking_mode:
        label = (
            "ON (TH — extended thinking / high reasoning effort)" if thinking_mode == "TH"
            else "OFF (NT — default reasoning)" if thinking_mode == "NT"
            else thinking_mode
        )
        out.append(f"- **확장사고 (Thinking):** {label}")
    if thinking_args:
        for k, v in thinking_args.items():
            out.append(f"- **Reasoning Arg:** `{k}={v}`")
    if intended_model:
        out.append(f"- **Intended Model (runner-set):** `{intended_model}`")
    return out


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


def render_html(
    session: ParsedSession,
    *,
    title: Optional[str] = None,
    thinking_mode: str = "",
    thinking_args: Optional[Dict[str, str]] = None,
    intended_model: str = "",
) -> str:
    """Render a ParsedSession as a self-contained HTML page.

    ``thinking_mode`` / ``thinking_args`` / ``intended_model`` are optional
    runner-supplied metadata appended to the meta-table when provided.
    """
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
    if meta.model_provider:
        summary_rows.append(
            f"<tr><td>Provider</td><td><code>{html_escape(meta.model_provider)}</code></td></tr>"
        )
    if meta.cli_version:
        summary_rows.append(
            f"<tr><td>CLI Version</td><td><code>{html_escape(meta.cli_version)}</code></td></tr>"
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

    repo_display = _display_repository(meta.repository)
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
{f'<tr><td>Repository</td><td><code>{html_escape(repo_display)}</code></td></tr>' if repo_display else ''}
{f'<tr><td>Branch</td><td><code>{html_escape(meta.branch)}</code></td></tr>' if meta.branch else ''}
{f'<tr><td>Started</td><td>{html_escape(format_timestamp(session.start_time))}</td></tr>' if session.start_time else ''}
{f'<tr><td>Ended</td><td>{html_escape(format_timestamp(session.end_time))}</td></tr>' if session.end_time else ''}
{f'<tr><td>Model</td><td><code>{html_escape(session.selected_model)}</code></td></tr>' if session.selected_model else ''}
<tr><td>Turns / Events</td><td>{len(session.turns)} turns, {session.raw_event_count} events</td></tr>
{chr(10).join(_thinking_html_rows(thinking_mode, thinking_args, intended_model))}
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
    """Convenience: parse a Codex JSONL and render to HTML in one call.

    Recognised render kwargs (passed through to ``render_html``):
    ``title``, ``thinking_mode``, ``thinking_args``, ``intended_model``.
    All other kwargs are forwarded to ``parse_codex_jsonl``.
    """
    try:
        render_kwargs = {
            k: kwargs.pop(k, None if k == "title" else "" if k != "thinking_args" else None)
            for k in ("title", "thinking_mode", "thinking_args", "intended_model")
            if k in kwargs
        }
        session = parse_codex_jsonl(jsonl_path, **kwargs)
        html = render_html(session, **render_kwargs)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
        return html
    except Exception:
        return None


def render_markdown(
    session: ParsedSession,
    *,
    thinking_mode: str = "",
    thinking_args: Optional[Dict[str, str]] = None,
    intended_model: str = "",
) -> str:
    """Render a ParsedSession as Markdown text.

    ``thinking_mode`` / ``thinking_args`` / ``intended_model`` carry runner
    metadata; appended to the Session Info block when provided.
    """
    meta = session.metadata
    title = meta.summary or f"Codex CLI Session {meta.session_id[:8] if meta.session_id else 'unknown'}"
    lines: List[str] = [f"# {title}", ""]

    lines.append("## Session Info")
    lines.append("")
    lines.append(f"- **Session ID:** `{meta.session_id or 'unknown'}`")
    if meta.cwd:
        lines.append(f"- **Working Dir:** `{meta.cwd}`")
    if meta.repository:
        lines.append(f"- **Repository:** `{meta.repository}`")
    if meta.branch:
        lines.append(f"- **Branch:** `{meta.branch}`")
    if session.selected_model:
        lines.append(f"- **Model:** `{session.selected_model}`")
    if meta.model_provider:
        lines.append(f"- **Provider:** `{meta.model_provider}`")
    if session.start_time:
        lines.append(f"- **Started:** {session.start_time}")
    if session.end_time:
        lines.append(f"- **Ended:** {session.end_time}")
    lines.append(f"- **Turns:** {len(session.turns)}")
    lines.append(f"- **Commands:** {session.total_commands} total, {session.failed_commands} failed")
    lines.extend(_thinking_md_lines(thinking_mode, thinking_args, intended_model))
    lines.append("")

    lines.append("## Conversation")
    lines.append("")

    for turn in session.turns:
        if turn.user_content:
            lines.append("### User")
            lines.append("")
            lines.append(turn.user_content)
            lines.append("")

        for tc in turn.tool_calls:
            status = "✅" if tc.success else "❌" if tc.success is False else "⚙️"
            lines.append(f"### {status} Tool: {tc.tool_name}")
            lines.append("")
            if tc.arguments and tc.arguments != "{}":
                lines.append(f"```\n{tc.arguments[:2000]}\n```")
            if tc.result_content:
                content = tc.result_content[:2000]
                if len(tc.result_content) > 2000:
                    content += f"\n... ({len(tc.result_content) - 2000} chars truncated)"
                lines.append(f"**Result:**\n```\n{content}\n```")
            lines.append("")

        if turn.assistant_content:
            lines.append("### Assistant")
            lines.append("")
            lines.append(turn.assistant_content)
            lines.append("")

    return "\n".join(lines)


def render_codex_md(jsonl_path: Path, output_path: Path, **kwargs) -> Optional[str]:
    """Convenience: parse a Codex JSONL and render to Markdown in one call.

    Runner-supplied metadata kwargs (``thinking_mode``, ``thinking_args``,
    ``intended_model``) are pulled out and forwarded to ``render_markdown``;
    everything else is forwarded to ``parse_codex_jsonl``.
    """
    try:
        render_kwargs = {
            k: kwargs.pop(k)
            for k in ("thinking_mode", "thinking_args", "intended_model")
            if k in kwargs
        }
        session = parse_codex_jsonl(jsonl_path, **kwargs)
        md = render_markdown(session, **render_kwargs)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md, encoding="utf-8")
        return md
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


def _extract_persistent_tool_call(payload: Dict[str, Any]) -> ToolCall:
    """Build a ToolCall shell from a persistent-format tool invocation."""
    tool_name = str(payload.get("name", "") or payload.get("type", "") or "tool")
    arguments_obj = payload.get("arguments", payload.get("input", ""))
    arguments_text = _stringify_content(arguments_obj)
    command = ""
    if payload.get("type") == "function_call":
        command = _extract_command_from_arguments(arguments_obj)
    label = truncate(command or tool_name, 140)
    if payload.get("type") == "custom_tool_call":
        label = tool_name
    return ToolCall(
        tool_call_id=str(payload.get("call_id", "") or f"tool-{tool_name}"),
        tool_name=label,
        arguments=command or arguments_text,
        success=None,
        result_content="",
    )


def _extract_persistent_output(raw_output: Any) -> tuple[str, Dict[str, Any]]:
    """Extract displayable text and metadata from persistent tool output payloads."""
    output_text = _stringify_content(raw_output)
    output_meta: Dict[str, Any] = {}
    if isinstance(raw_output, str):
        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            output_meta = parsed.get("metadata", {}) or {}
            output_text = _stringify_content(parsed.get("output", raw_output))
    elif isinstance(raw_output, dict):
        output_meta = raw_output.get("metadata", {}) or {}
        output_text = _stringify_content(raw_output.get("output", raw_output))
    return output_text, output_meta


def _extract_message_text(content: Any) -> str:
    """Extract text from response_item message content arrays."""
    return _stringify_content(content).strip()


def _should_skip_persistent_user_message(text: str) -> bool:
    """Ignore injected system/developer blobs serialized as user messages."""
    normalized = _normalized_text(text)
    skip_markers = (
        "ag\u0065nts.md instructions for",
        "<instructions>",
        "<permissions instructions>",
        "<skills_instructions>",
        "filesystem sandboxing defines",
    )
    return any(marker in normalized for marker in skip_markers)


def _extract_command_from_arguments(arguments: Any) -> str:
    """Extract a shell command string from tool-call arguments when possible."""
    parsed: Any = arguments
    if isinstance(arguments, str):
        try:
            parsed = json.loads(arguments)
        except json.JSONDecodeError:
            return arguments
    if isinstance(parsed, dict):
        for key in ("cmd", "command"):
            value = parsed.get(key)
            if isinstance(value, str) and value:
                return value
    return _stringify_content(arguments)


def _is_command_tool_call(payload: Dict[str, Any]) -> bool:
    """Heuristic: treat exec-like calls as command executions."""
    name = str(payload.get("name", "") or "")
    if name in {"exec_command", "run_command", "bash", "shell"}:
        return True
    if payload.get("type") == "function_call":
        parsed = _extract_command_from_arguments(payload.get("arguments", ""))
        return bool(parsed)
    return False


def _infer_tool_success(output_text: str, output_meta: Dict[str, Any]) -> Optional[bool]:
    """Infer success from exec output text or embedded metadata."""
    exit_code = output_meta.get("exit_code")
    if isinstance(exit_code, int):
        return exit_code == 0
    match = _EXIT_CODE_RE.search(output_text)
    if match:
        return int(match.group(1)) == 0
    lowered = output_text.lower()
    if lowered.startswith("error:") or "traceback" in lowered:
        return False
    if output_text:
        return True
    return None


def _infer_tool_duration_ms(output_text: str, output_meta: Dict[str, Any]) -> Optional[float]:
    """Infer duration in milliseconds from exec output text or metadata."""
    duration_seconds = output_meta.get("duration_seconds")
    if isinstance(duration_seconds, (int, float)):
        return float(duration_seconds) * 1000.0
    match = _WALL_TIME_RE.search(output_text)
    if match:
        try:
            return float(match.group(1)) * 1000.0
        except ValueError:
            return None
    return None


def _extract_files_changed(output_text: str) -> List[Dict[str, str]]:
    """Best-effort extraction of edited files from apply_patch output."""
    files: List[Dict[str, str]] = []
    capture = False
    for line in output_text.splitlines():
        if "Updated the following files:" in line:
            capture = True
            continue
        if not capture:
            continue
        stripped = line.strip()
        if not stripped:
            break
        if len(stripped) > 2 and stripped[1] == " ":
            kind = {"M": "update", "A": "create", "D": "delete"}.get(stripped[0], "update")
            files.append({"path": stripped[2:].strip(), "kind": kind})
        else:
            break
    return files


def _display_repository(repository: str) -> str:
    """Normalize repository URLs for compact HTML display."""
    repository = repository.strip()
    if repository.startswith("https://github.com/"):
        repository = repository[len("https://github.com/"):]
    if repository.endswith(".git"):
        repository = repository[:-4]
    return repository


def _normalized_text(text: str) -> str:
    """Normalize whitespace for duplicate detection."""
    return " ".join(text.split()).strip().lower()


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
