#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Parse Copilot CLI session logs (events.jsonl) into human-readable Markdown.

Copilot CLI stores session data in ``~/.copilot/session-state/<UUID>/``.
Each session directory contains:

- ``workspace.yaml`` — session metadata (cwd, branch, timestamps)
- ``events.jsonl``   — line-delimited JSON event log (conversation + tool calls)

This script:

1. Finds matching sessions by ``--cwd`` and/or ``--after``/``--before`` timestamps
2. Parses all 14 event types from ``events.jsonl``
3. Generates a Markdown report: metadata, conversation flow, tool calls, token usage

Usage::

    # Find sessions matching a working directory after a timestamp
    python parse_copilot_session.py \\
        --cwd /path/to/project \\
        --after 2026-04-01T00:00:00 \\
        --output session_logs.md

    # Parse a specific session by UUID
    python parse_copilot_session.py \\
        --session-id 010c6a0d-78ad-4790-bc5c-0d5ced24f919 \\
        --output session_logs.md

    # Use as a library
    from parse_copilot_session import find_sessions, parse_session, render_markdown
    sessions = find_sessions(cwd="/path/to/project", after="2026-04-01T00:00:00")
    for session in sessions:
        parsed = parse_session(session)
        md = render_markdown(parsed)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml  # PyYAML

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COPILOT_SESSION_STATE_DIR = Path.home() / ".copilot" / "session-state"

# All known event types (Copilot CLI 1.x)
EVENT_TYPES = {
    "session.start",
    "session.resume",
    "session.shutdown",
    "session.mode_changed",
    "session.model_change",
    "user.message",
    "assistant.turn_start",
    "assistant.message",
    "assistant.turn_end",
    "tool.execution_start",
    "tool.execution_complete",
    "skill.invoked",
    "subagent.started",
    "subagent.completed",
    "system.notification",
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class SessionMetadata:
    """Parsed workspace.yaml fields."""

    session_id: str = ""
    cwd: str = ""
    git_root: str = ""
    repository: str = ""
    branch: str = ""
    summary: str = ""
    created_at: str = ""
    updated_at: str = ""
    session_dir: Path = field(default_factory=Path)


@dataclass
class ToolCall:
    """A single tool invocation with result."""

    tool_call_id: str = ""
    tool_name: str = ""
    arguments: str = ""
    success: Optional[bool] = None
    result_content: str = ""
    duration_ms: Optional[float] = None


@dataclass
class SubagentCall:
    """A subagent invocation."""

    tool_call_id: str = ""
    agent_name: str = ""
    agent_display_name: str = ""
    description: str = ""
    model: str = ""
    total_tool_calls: int = 0
    total_tokens: int = 0
    duration_ms: float = 0.0


@dataclass
class ConversationTurn:
    """A single conversation turn (user message + assistant response)."""

    turn_index: int = 0
    user_content: str = ""
    assistant_content: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    subagent_calls: List[SubagentCall] = field(default_factory=list)
    skills_invoked: List[str] = field(default_factory=list)
    output_tokens: int = 0
    timestamp: str = ""


@dataclass
class TokenUsage:
    """Token usage summary from session.shutdown."""

    total_premium_requests: int = 0
    total_api_duration_ms: float = 0.0
    lines_added: int = 0
    lines_removed: int = 0
    files_modified: List[str] = field(default_factory=list)
    model_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    current_model: str = ""
    current_tokens: int = 0
    system_tokens: int = 0
    conversation_tokens: int = 0
    tool_definitions_tokens: int = 0


@dataclass
class ParsedSession:
    """Fully parsed session data."""

    metadata: SessionMetadata
    copilot_version: str = ""
    selected_model: str = ""
    start_time: str = ""
    end_time: str = ""
    shutdown_type: str = ""
    turns: List[ConversationTurn] = field(default_factory=list)
    token_usage: Optional[TokenUsage] = None
    raw_event_count: int = 0
    unknown_events: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Sentinel extraction
# ---------------------------------------------------------------------------

# Matches: [DX-AGENTIC-DEV: DONE (output-dir: some/path/here)]
_SENTINEL_OUTPUT_DIR_RE = re.compile(
    r"\[DX-AGENTIC-DEV:\s*DONE\s*\(output-dir:\s*([^)]+)\)\]"
)

# Matches: [DX-AGENTIC-DEV: START]
_SENTINEL_START_RE = re.compile(r"\[DX-AGENTIC-DEV:\s*START\]")


def extract_output_dirs(parsed: ParsedSession) -> List[str]:
    """Extract output-dir values from DONE sentinels in assistant responses.

    Searches all assistant turn content for the sentinel marker and returns
    a deduplicated list of output-dir paths in order of appearance.
    """
    seen: set[str] = set()
    result: List[str] = []
    for turn in parsed.turns:
        for m in _SENTINEL_OUTPUT_DIR_RE.finditer(turn.assistant_content):
            path = m.group(1).strip().rstrip("/")
            if path and path not in seen:
                seen.add(path)
                result.append(path)
    return result


def has_start_sentinel(parsed: ParsedSession) -> bool:
    """Check whether any assistant turn contains the START sentinel.

    Returns ``True`` if at least one assistant response includes the
    ``[DX-AGENTIC-DEV: START]`` marker.  This is expected to appear in
    the agent's very first text output for each user prompt.
    """
    for turn in parsed.turns:
        if _SENTINEL_START_RE.search(turn.assistant_content):
            return True
    return False


# ---------------------------------------------------------------------------
# YAML parsing (with fallback for missing PyYAML)
# ---------------------------------------------------------------------------


def _parse_yaml(filepath: Path) -> Dict[str, Any]:
    """Parse a YAML file, falling back to simple key-value parsing if PyYAML is unavailable."""
    text = filepath.read_text(encoding="utf-8")
    if HAS_YAML:
        return yaml.safe_load(text) or {}

    # Fallback: simple line-by-line key: value parser (handles flat YAML)
    result: Dict[str, Any] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


# ---------------------------------------------------------------------------
# Session discovery
# ---------------------------------------------------------------------------


def find_sessions(
    cwd: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
    session_id: Optional[str] = None,
    session_state_dir: Optional[Path] = None,
) -> List[SessionMetadata]:
    """Find Copilot CLI sessions matching the given criteria.

    Args:
        cwd: Filter by working directory (exact match or prefix match).
        after: ISO 8601 timestamp — only sessions created after this time.
        before: ISO 8601 timestamp — only sessions created before this time.
        session_id: Directly specify a session UUID.
        session_state_dir: Override the session state directory
            (default: ``~/.copilot/session-state/``).

    Returns:
        List of matching SessionMetadata, sorted by created_at ascending.
    """
    base_dir = session_state_dir or COPILOT_SESSION_STATE_DIR
    if not base_dir.exists():
        return []

    # Parse time boundaries
    after_dt = _parse_iso(after) if after else None
    before_dt = _parse_iso(before) if before else None

    # If session_id is given, look up directly
    if session_id:
        session_dir = base_dir / session_id
        if session_dir.exists():
            meta = _read_workspace_yaml(session_dir)
            if meta:
                return [meta]
        return []

    # Scan all sessions
    results: List[SessionMetadata] = []
    for child in base_dir.iterdir():
        if not child.is_dir():
            continue
        workspace_yaml = child / "workspace.yaml"
        events_jsonl = child / "events.jsonl"
        if not workspace_yaml.exists() or not events_jsonl.exists():
            continue

        meta = _read_workspace_yaml(child)
        if meta is None:
            continue

        # Filter by cwd
        if cwd:
            # Resolve symlinks and normalize paths for comparison.
            # Copilot stores the realpath in workspace.yaml while the
            # caller may pass a symlink-containing path (e.g.
            # /home/user/... vs /data/home/user/...).
            normalized_cwd = os.path.realpath(cwd).rstrip("/")
            normalized_meta_cwd = os.path.realpath(meta.cwd).rstrip("/")
            if normalized_meta_cwd != normalized_cwd and not normalized_meta_cwd.startswith(
                normalized_cwd + "/"
            ):
                continue

        # Filter by time range
        if meta.created_at:
            created_dt = _parse_iso(meta.created_at)
            if created_dt:
                if after_dt and created_dt < after_dt:
                    continue
                if before_dt and created_dt > before_dt:
                    continue

        results.append(meta)

    # Sort by created_at ascending
    results.sort(key=lambda m: m.created_at or "")
    return results


def _read_workspace_yaml(session_dir: Path) -> Optional[SessionMetadata]:
    """Read and parse workspace.yaml from a session directory."""
    workspace_file = session_dir / "workspace.yaml"
    if not workspace_file.exists():
        return None
    try:
        data = _parse_yaml(workspace_file)
    except Exception:
        return None

    return SessionMetadata(
        session_id=str(data.get("id", session_dir.name)),
        cwd=str(data.get("cwd", "")),
        git_root=str(data.get("git_root", "")),
        repository=str(data.get("repository", "")),
        branch=str(data.get("branch", "")),
        summary=str(data.get("summary", "")),
        created_at=str(data.get("created_at", "")),
        updated_at=str(data.get("updated_at", "")),
        session_dir=session_dir,
    )


def _parse_iso(timestamp_str: str) -> Optional[datetime]:
    """Parse an ISO 8601 timestamp string to datetime (timezone-aware)."""
    if not timestamp_str:
        return None
    try:
        # Handle various ISO formats
        ts = timestamp_str.strip()
        # Replace Z with +00:00 for fromisoformat compatibility
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Event parsing
# ---------------------------------------------------------------------------


def parse_session(metadata: SessionMetadata) -> ParsedSession:
    """Parse events.jsonl for a session into a structured ParsedSession.

    Args:
        metadata: SessionMetadata with session_dir pointing to the session.

    Returns:
        Fully parsed session data.
    """
    events_file = metadata.session_dir / "events.jsonl"
    if not events_file.exists():
        return ParsedSession(metadata=metadata)

    events = _read_events(events_file)
    return _process_events(metadata, events)


def _read_events(events_file: Path) -> List[Dict[str, Any]]:
    """Read events.jsonl line by line."""
    events: List[Dict[str, Any]] = []
    text = events_file.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _process_events(
    metadata: SessionMetadata,
    events: List[Dict[str, Any]],
) -> ParsedSession:
    """Process a list of events into a ParsedSession."""
    session = ParsedSession(metadata=metadata, raw_event_count=len(events))

    # State tracking
    current_user_content = ""
    current_assistant_content = ""
    current_tool_calls: List[ToolCall] = []
    current_subagents: List[SubagentCall] = []
    current_skills: List[str] = []
    current_output_tokens = 0
    current_timestamp = ""
    turn_index = 0
    in_turn = False

    # Pending tool calls (tool_call_id -> ToolCall)
    pending_tools: Dict[str, ToolCall] = {}
    # Pending subagents (tool_call_id -> SubagentCall)
    pending_subagents: Dict[str, SubagentCall] = {}

    for event in events:
        etype = event.get("type", "")
        data = event.get("data", {})
        timestamp = event.get("timestamp", "")

        if etype == "session.start":
            session.copilot_version = data.get("copilotVersion", "")
            session.selected_model = data.get("selectedModel", "")
            session.start_time = data.get("startTime", timestamp)

        elif etype == "session.resume":
            # Session resumed — just note the timestamp
            pass

        elif etype == "session.shutdown":
            session.end_time = timestamp
            session.shutdown_type = data.get("shutdownType", "")
            session.token_usage = _parse_token_usage(data)

        elif etype == "session.mode_changed":
            # Mode change (e.g., "ask" -> "agent")
            pass

        elif etype == "session.model_change":
            # Model change — update selected model
            session.selected_model = data.get("newModel", session.selected_model)

        elif etype == "user.message":
            # If there's a pending turn, flush it
            if in_turn and (current_user_content or current_assistant_content):
                turn_index += 1
                session.turns.append(
                    ConversationTurn(
                        turn_index=turn_index,
                        user_content=current_user_content,
                        assistant_content=current_assistant_content,
                        tool_calls=current_tool_calls,
                        subagent_calls=current_subagents,
                        skills_invoked=current_skills,
                        output_tokens=current_output_tokens,
                        timestamp=current_timestamp,
                    )
                )
            # Start new user turn
            current_user_content = data.get("content", "")
            current_assistant_content = ""
            current_tool_calls = []
            current_subagents = []
            current_skills = []
            current_output_tokens = 0
            current_timestamp = timestamp
            in_turn = True

        elif etype == "assistant.turn_start":
            pass  # Turn boundaries handled by user.message

        elif etype == "assistant.message":
            content = data.get("content", "")
            if content:
                if current_assistant_content:
                    current_assistant_content += "\n\n" + content
                else:
                    current_assistant_content = content

            # Track output tokens
            tokens = data.get("outputTokens", 0)
            if tokens:
                current_output_tokens += tokens

            # Parse tool requests from this message
            for tr in data.get("toolRequests", []):
                tc = ToolCall(
                    tool_call_id=tr.get("toolCallId", ""),
                    tool_name=tr.get("name", ""),
                    arguments=_truncate(
                        json.dumps(tr.get("arguments", {}), ensure_ascii=False), 500
                    ),
                )
                pending_tools[tc.tool_call_id] = tc
                current_tool_calls.append(tc)

        elif etype == "assistant.turn_end":
            pass  # Turn boundaries handled by user.message

        elif etype == "tool.execution_start":
            tc_id = data.get("toolCallId", "")
            if tc_id not in pending_tools:
                # Tool started without a prior assistant.message request
                tc = ToolCall(
                    tool_call_id=tc_id,
                    tool_name=data.get("toolName", ""),
                    arguments=_truncate(
                        json.dumps(data.get("arguments", {}), ensure_ascii=False), 500
                    ),
                )
                pending_tools[tc_id] = tc
                current_tool_calls.append(tc)

        elif etype == "tool.execution_complete":
            tc_id = data.get("toolCallId", "")
            tc = pending_tools.get(tc_id)
            if tc:
                tc.success = data.get("success", None)
                result_data = data.get("result", {})
                tc.result_content = _truncate(
                    str(result_data.get("content", "")), 1000
                )
                telemetry = data.get("toolTelemetry", {})
                tc.duration_ms = telemetry.get("elapsed_ms")
            # Remove from pending
            pending_tools.pop(tc_id, None)

        elif etype == "skill.invoked":
            skill_name = data.get("name", "unknown")
            current_skills.append(skill_name)

        elif etype == "subagent.started":
            sa = SubagentCall(
                tool_call_id=data.get("toolCallId", ""),
                agent_name=data.get("agentName", ""),
                agent_display_name=data.get("agentDisplayName", ""),
                description=data.get("agentDescription", ""),
            )
            pending_subagents[sa.tool_call_id] = sa
            current_subagents.append(sa)

        elif etype == "subagent.completed":
            tc_id = data.get("toolCallId", "")
            sa = pending_subagents.get(tc_id)
            if sa:
                sa.model = data.get("model", "")
                sa.total_tool_calls = data.get("totalToolCalls", 0)
                sa.total_tokens = data.get("totalTokens", 0)
                sa.duration_ms = data.get("durationMs", 0.0)
            pending_subagents.pop(tc_id, None)

        elif etype == "system.notification":
            pass  # System notifications are informational

        else:
            if etype and etype not in session.unknown_events:
                session.unknown_events.append(etype)

    # Flush the last turn
    if in_turn and (current_user_content or current_assistant_content):
        turn_index += 1
        session.turns.append(
            ConversationTurn(
                turn_index=turn_index,
                user_content=current_user_content,
                assistant_content=current_assistant_content,
                tool_calls=current_tool_calls,
                subagent_calls=current_subagents,
                skills_invoked=current_skills,
                output_tokens=current_output_tokens,
                timestamp=current_timestamp,
            )
        )

    return session


def _parse_token_usage(data: Dict[str, Any]) -> TokenUsage:
    """Parse token usage from session.shutdown data."""
    code_changes = data.get("codeChanges", {})
    model_metrics = data.get("modelMetrics", {})

    return TokenUsage(
        total_premium_requests=data.get("totalPremiumRequests", 0),
        total_api_duration_ms=data.get("totalApiDurationMs", 0.0),
        lines_added=code_changes.get("linesAdded", 0),
        lines_removed=code_changes.get("linesRemoved", 0),
        files_modified=code_changes.get("filesModified", []),
        model_metrics=model_metrics,
        current_model=data.get("currentModel", ""),
        current_tokens=data.get("currentTokens", 0),
        system_tokens=data.get("systemTokens", 0),
        conversation_tokens=data.get("conversationTokens", 0),
        tool_definitions_tokens=data.get("toolDefinitionsTokens", 0),
    )


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_markdown(session: ParsedSession) -> str:
    """Render a ParsedSession as a Markdown report.

    Returns:
        Markdown-formatted string.
    """
    lines: List[str] = []
    meta = session.metadata

    # Title
    lines.append(f"# Copilot CLI Session Log")
    lines.append("")

    # Metadata table
    lines.append("## Session Metadata")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    lines.append(f"| Session ID | `{meta.session_id}` |")
    lines.append(f"| Working Directory | `{meta.cwd}` |")
    if meta.repository:
        lines.append(f"| Repository | `{meta.repository}` |")
    if meta.branch:
        lines.append(f"| Branch | `{meta.branch}` |")
    lines.append(f"| Model | `{session.selected_model}` |")
    if session.copilot_version:
        lines.append(f"| Copilot Version | `{session.copilot_version}` |")
    lines.append(f"| Started | {_format_timestamp(session.start_time or meta.created_at)} |")
    if session.end_time:
        lines.append(f"| Ended | {_format_timestamp(session.end_time)} |")
    if session.shutdown_type:
        lines.append(f"| Shutdown | `{session.shutdown_type}` |")
    lines.append(f"| Total Events | {session.raw_event_count} |")
    if meta.summary:
        lines.append(f"| Summary | {meta.summary} |")
    lines.append("")

    # Conversation flow
    if session.turns:
        lines.append("## Conversation Flow")
        lines.append("")
        lines.append(f"Total turns: {len(session.turns)}")
        lines.append("")

        for turn in session.turns:
            lines.append(f"### Turn {turn.turn_index}")
            if turn.timestamp:
                lines.append(f"*{_format_timestamp(turn.timestamp)}*")
            lines.append("")

            # User message
            lines.append("**User:**")
            lines.append("")
            user_text = _truncate(turn.user_content, 2000)
            lines.append(f"> {_indent_blockquote(user_text)}")
            lines.append("")

            # Skills invoked
            if turn.skills_invoked:
                lines.append(f"**Skills invoked:** {', '.join(f'`{s}`' for s in turn.skills_invoked)}")
                lines.append("")

            # Assistant response
            if turn.assistant_content:
                lines.append("**Assistant:**")
                lines.append("")
                assistant_text = _truncate(turn.assistant_content, 3000)
                lines.append(assistant_text)
                lines.append("")

            # Tool calls
            if turn.tool_calls:
                lines.append(f"**Tool Calls** ({len(turn.tool_calls)}):")
                lines.append("")
                for i, tc in enumerate(turn.tool_calls, 1):
                    status = ""
                    if tc.success is True:
                        status = " ✓"
                    elif tc.success is False:
                        status = " ✗"
                    duration = f" ({tc.duration_ms:.0f}ms)" if tc.duration_ms else ""
                    lines.append(f"{i}. **`{tc.tool_name}`**{status}{duration}")
                    if tc.arguments and tc.arguments != "{}":
                        lines.append(f"   - Args: `{tc.arguments}`")
                    if tc.result_content:
                        result_preview = _truncate(tc.result_content, 200)
                        lines.append(f"   - Result: {result_preview}")
                lines.append("")

            # Subagent calls
            if turn.subagent_calls:
                lines.append(f"**Subagent Calls** ({len(turn.subagent_calls)}):")
                lines.append("")
                for sa in turn.subagent_calls:
                    duration = f" ({sa.duration_ms / 1000:.1f}s)" if sa.duration_ms else ""
                    tokens = f", {sa.total_tokens:,} tokens" if sa.total_tokens else ""
                    tools = f", {sa.total_tool_calls} tool calls" if sa.total_tool_calls else ""
                    lines.append(
                        f"- **{sa.agent_display_name or sa.agent_name}**{duration}{tokens}{tools}"
                    )
                    if sa.description:
                        lines.append(f"  - {_truncate(sa.description, 200)}")
                lines.append("")

            # Token count
            if turn.output_tokens:
                lines.append(f"*Output tokens: {turn.output_tokens:,}*")
                lines.append("")

            lines.append("---")
            lines.append("")

    # Token usage summary
    if session.token_usage:
        tu = session.token_usage
        lines.append("## Token Usage Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|---|---|")
        lines.append(f"| Premium Requests | {tu.total_premium_requests} |")
        lines.append(
            f"| Total API Duration | {tu.total_api_duration_ms / 1000:.1f}s |"
        )
        if tu.current_model:
            lines.append(f"| Current Model | `{tu.current_model}` |")
        if tu.current_tokens:
            lines.append(f"| Context Window | {tu.current_tokens:,} tokens |")
        if tu.system_tokens:
            lines.append(f"| System Tokens | {tu.system_tokens:,} |")
        if tu.conversation_tokens:
            lines.append(f"| Conversation Tokens | {tu.conversation_tokens:,} |")
        if tu.tool_definitions_tokens:
            lines.append(f"| Tool Definitions | {tu.tool_definitions_tokens:,} |")
        lines.append("")

        # Code changes
        if tu.lines_added or tu.lines_removed or tu.files_modified:
            lines.append("### Code Changes")
            lines.append("")
            lines.append(f"- Lines added: **{tu.lines_added}**")
            lines.append(f"- Lines removed: **{tu.lines_removed}**")
            if tu.files_modified:
                lines.append(f"- Files modified: **{len(tu.files_modified)}**")
                for f in tu.files_modified[:20]:
                    lines.append(f"  - `{f}`")
                if len(tu.files_modified) > 20:
                    lines.append(
                        f"  - ... and {len(tu.files_modified) - 20} more"
                    )
            lines.append("")

        # Per-model metrics
        if tu.model_metrics:
            lines.append("### Per-Model Metrics")
            lines.append("")
            lines.append("| Model | Requests | Input Tokens | Output Tokens | Cache Read | Cache Write |")
            lines.append("|---|---|---|---|---|---|")
            for model_name, metrics in tu.model_metrics.items():
                requests = metrics.get("requests", {})
                usage = metrics.get("usage", {})
                req_count = requests.get("count", 0)
                input_tok = usage.get("inputTokens", 0)
                output_tok = usage.get("outputTokens", 0)
                cache_read = usage.get("cacheReadTokens", 0)
                cache_write = usage.get("cacheWriteTokens", 0)
                lines.append(
                    f"| `{model_name}` | {req_count} | {input_tok:,} | {output_tok:,} | {cache_read:,} | {cache_write:,} |"
                )
            lines.append("")

    # Unknown events
    if session.unknown_events:
        lines.append("## Unknown Event Types")
        lines.append("")
        for ue in session.unknown_events:
            lines.append(f"- `{ue}`")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append(
        f"*Generated by `parse_copilot_session.py` at "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to max_len characters, adding ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _indent_blockquote(text: str) -> str:
    """Indent text for Markdown blockquote (handle multi-line)."""
    lines = text.splitlines()
    if len(lines) <= 1:
        return text
    return "\n> ".join(lines)


def _format_timestamp(ts: str) -> str:
    """Format an ISO timestamp for display."""
    if not ts:
        return "—"
    dt = _parse_iso(ts)
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    return ts


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

# Minimal CSS for self-contained HTML (inspired by Copilot /share html).
_HTML_CSS = """\
:root {
  --bg: #0d1117; --bg-muted: #151b23; --fg: #f0f6fc; --fg-muted: #9198a1;
  --border: #3d444d; --accent: #4493f8; --success: #3fb950; --warning: #d29922;
  --error: #f85149; --brand: #ab7df8; --code-bg: #1c2128;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg: #ffffff; --bg-muted: #f6f8fa; --fg: #1f2328; --fg-muted: #59636e;
    --border: #d1d9e0; --accent: #0969da; --success: #1a7f37; --warning: #9a6700;
    --error: #cf222e; --brand: #8250df; --code-bg: #f6f8fa;
  }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
       background: var(--bg); color: var(--fg); line-height: 1.5; padding: 0; }
.container { max-width: 960px; margin: 0 auto; padding: 16px; }
h1 { font-size: 1.4em; margin: 0 0 8px; }
h2 { font-size: 1.15em; margin: 16px 0 8px; color: var(--fg-muted); }
.meta-table { width: 100%; border-collapse: collapse; font-size: 0.85em; margin-bottom: 16px; }
.meta-table td { padding: 4px 8px; border-bottom: 1px solid var(--border); }
.meta-table td:first-child { color: var(--fg-muted); white-space: nowrap; width: 140px; }
.entry { border-left: 3px solid var(--border); margin: 12px 0; padding: 8px 12px;
         background: var(--bg-muted); border-radius: 0 6px 6px 0; }
.entry.user { border-left-color: var(--accent); }
.entry.assistant { border-left-color: var(--brand); }
.entry.tool-ok { border-left-color: var(--success); }
.entry.tool-fail { border-left-color: var(--error); }
.entry.subagent { border-left-color: var(--warning); }
.entry-hdr { display: flex; gap: 8px; align-items: center; font-size: 0.82em;
             color: var(--fg-muted); cursor: pointer; user-select: none; }
.entry-hdr .icon { font-size: 1.1em; }
.entry-hdr .label { font-weight: 600; color: var(--fg); }
.entry-hdr .time { margin-left: auto; }
.entry-body { margin-top: 6px; white-space: pre-wrap; word-break: break-word; font-size: 0.9em; }
.entry.collapsed .entry-body { display: none; }
pre, code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 0.88em; }
pre { background: var(--code-bg); border: 1px solid var(--border); border-radius: 6px;
      padding: 10px; overflow-x: auto; margin: 6px 0; }
code { background: var(--code-bg); padding: 2px 5px; border-radius: 3px; }
.tool-args { color: var(--fg-muted); font-size: 0.82em; margin-top: 4px; }
.tool-result { margin-top: 4px; }
.token-badge { display: inline-block; font-size: 0.75em; color: var(--fg-muted);
               border: 1px solid var(--border); border-radius: 10px; padding: 1px 8px; margin-left: 4px; }
.summary-section { margin: 16px 0; padding: 12px; background: var(--bg-muted);
                   border: 1px solid var(--border); border-radius: 6px; }
.summary-table { width: 100%; border-collapse: collapse; font-size: 0.85em; }
.summary-table th, .summary-table td { padding: 4px 8px; border-bottom: 1px solid var(--border); text-align: left; }
.summary-table th { color: var(--fg-muted); font-weight: 500; }
hr { border: none; border-top: 1px solid var(--border); margin: 16px 0; }
.footer { font-size: 0.78em; color: var(--fg-muted); margin-top: 24px; text-align: center; }
"""

_HTML_JS = """\
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.entry-hdr').forEach(function(hdr) {
    hdr.addEventListener('click', function() {
      hdr.parentElement.classList.toggle('collapsed');
    });
  });
});
"""


def _html_escape(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _md_to_html_simple(text: str) -> str:
    """Convert Markdown text to simple HTML (code blocks, inline code, paragraphs).

    This is intentionally minimal — covers the patterns commonly seen in
    Copilot assistant responses without requiring a full Markdown library.
    """
    import re as _re

    # Fenced code blocks: ```lang\n...\n```
    def _code_block(m: re.Match) -> str:
        lang = _html_escape(m.group(1) or "")
        code = _html_escape(m.group(2))
        lang_attr = f' data-lang="{lang}"' if lang else ""
        return f"<pre{lang_attr}><code>{code}</code></pre>"

    text = _re.sub(r"```(\w*)\n(.*?)```", _code_block, text, flags=_re.DOTALL)

    # Inline code: `...`
    text = _re.sub(r"`([^`\n]+)`", lambda m: f"<code>{_html_escape(m.group(1))}</code>", text)

    # Bold: **...**
    text = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    # Split into paragraphs on blank lines (but preserve <pre> blocks)
    parts = _re.split(r"(<pre.*?</pre>)", text, flags=_re.DOTALL)
    result_parts = []
    for part in parts:
        if part.startswith("<pre"):
            result_parts.append(part)
        else:
            paragraphs = _re.split(r"\n{2,}", part.strip())
            for p in paragraphs:
                p = p.strip()
                if p:
                    result_parts.append(f"<p>{p}</p>")
    return "\n".join(result_parts)


def render_html(session: ParsedSession) -> str:
    """Render a ParsedSession as a self-contained HTML page.

    The output mirrors the structure of Copilot CLI ``/share html`` but is
    generated entirely from ``events.jsonl`` data, so it works after the
    interactive session has ended.

    Returns:
        Complete HTML document string.
    """
    meta = session.metadata
    title = _html_escape(meta.summary or f"Copilot Session {meta.session_id[:8]}")

    entries: List[str] = []
    entry_idx = 0

    for turn in session.turns:
        # User message
        entry_idx += 1
        user_text = _html_escape(turn.user_content)
        time_label = _format_timestamp(turn.timestamp) if turn.timestamp else ""
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

        # Tool calls (shown before assistant response for chronological order)
        for tc in turn.tool_calls:
            entry_idx += 1
            status_cls = "tool-ok" if tc.success else "tool-fail" if tc.success is False else "tool-ok"
            status_icon = "&#x2705;" if tc.success else "&#x274C;" if tc.success is False else "&#x2699;"
            duration = f" ({tc.duration_ms:.0f}ms)" if tc.duration_ms else ""
            args_html = ""
            if tc.arguments and tc.arguments != "{}":
                args_html = f'<div class="tool-args"><code>{_html_escape(tc.arguments)}</code></div>'
            result_html = ""
            if tc.result_content:
                result_html = f'<div class="tool-result"><pre>{_html_escape(tc.result_content)}</pre></div>'
            entries.append(
                f'<div class="entry {status_cls} collapsed" id="entry-{entry_idx}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">{status_icon}</span>'
                f'<span class="label">{_html_escape(tc.tool_name)}</span>'
                f'<span>{duration}</span>'
                f'<span class="time">click to expand</span>'
                f'</div>'
                f'<div class="entry-body">{args_html}{result_html}</div>'
                f'</div>'
            )

        # Subagent calls
        for sa in turn.subagent_calls:
            entry_idx += 1
            duration = f" ({sa.duration_ms / 1000:.1f}s)" if sa.duration_ms else ""
            tokens = f" &middot; {sa.total_tokens:,} tokens" if sa.total_tokens else ""
            entries.append(
                f'<div class="entry subagent collapsed" id="entry-{entry_idx}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">&#x1F916;</span>'
                f'<span class="label">{_html_escape(sa.agent_display_name or sa.agent_name)}</span>'
                f'<span>{duration}{tokens}</span>'
                f'<span class="time">click to expand</span>'
                f'</div>'
                f'<div class="entry-body">{_html_escape(sa.description)}</div>'
                f'</div>'
            )

        # Assistant response
        if turn.assistant_content:
            entry_idx += 1
            assistant_html = _md_to_html_simple(turn.assistant_content)
            token_badge = (
                f' <span class="token-badge">{turn.output_tokens:,} tokens</span>'
                if turn.output_tokens
                else ""
            )
            entries.append(
                f'<div class="entry assistant" id="entry-{entry_idx}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">&#x1F4AC;</span>'
                f'<span class="label">Copilot</span>'
                f'{token_badge}'
                f'<span class="time">{time_label}</span>'
                f'</div>'
                f'<div class="entry-body">{assistant_html}</div>'
                f'</div>'
            )

    # Token usage summary
    usage_html = ""
    if session.token_usage:
        tu = session.token_usage
        rows = []
        rows.append(f"<tr><td>Premium Requests</td><td>{tu.total_premium_requests}</td></tr>")
        rows.append(f"<tr><td>API Duration</td><td>{tu.total_api_duration_ms / 1000:.1f}s</td></tr>")
        if tu.current_model:
            rows.append(f"<tr><td>Model</td><td><code>{_html_escape(tu.current_model)}</code></td></tr>")
        if tu.current_tokens:
            rows.append(f"<tr><td>Context Window</td><td>{tu.current_tokens:,} tokens</td></tr>")
        if tu.lines_added or tu.lines_removed:
            rows.append(f"<tr><td>Lines +/-</td><td>+{tu.lines_added} / -{tu.lines_removed}</td></tr>")
        if tu.files_modified:
            rows.append(f"<tr><td>Files Modified</td><td>{len(tu.files_modified)}</td></tr>")
        usage_html = (
            '<div class="summary-section">'
            "<h2>Token Usage</h2>"
            '<table class="summary-table">'
            + "\n".join(rows)
            + "</table></div>"
        )

    # Assemble page
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<style>{_HTML_CSS}</style>
</head>
<body>
<div class="container">
<h1>{title}</h1>
<table class="meta-table">
<tr><td>Session ID</td><td><code>{_html_escape(meta.session_id)}</code></td></tr>
<tr><td>Working Directory</td><td><code>{_html_escape(meta.cwd)}</code></td></tr>
{"<tr><td>Repository</td><td>" + _html_escape(meta.repository) + "</td></tr>" if meta.repository else ""}
{"<tr><td>Branch</td><td>" + _html_escape(meta.branch) + "</td></tr>" if meta.branch else ""}
<tr><td>Model</td><td><code>{_html_escape(session.selected_model)}</code></td></tr>
<tr><td>Started</td><td>{_format_timestamp(session.start_time or meta.created_at)}</td></tr>
{"<tr><td>Ended</td><td>" + _format_timestamp(session.end_time) + "</td></tr>" if session.end_time else ""}
<tr><td>Turns / Events</td><td>{len(session.turns)} turns, {session.raw_event_count} events</td></tr>
</table>
<hr />
{"".join(entries)}
{usage_html}
<div class="footer">
Generated by <code>parse_copilot_session.py</code> at {now_utc}
</div>
</div>
<script>{_HTML_JS}</script>
</body>
</html>"""


def render_multi_session_html(sessions: List[ParsedSession]) -> str:
    """Render multiple sessions into a single HTML document.

    For a single session, delegates to ``render_html``.  For multiple
    sessions, concatenates them with separator headings.
    """
    if not sessions:
        return "<html><body><p>No sessions found.</p></body></html>"
    if len(sessions) == 1:
        return render_html(sessions[0])

    # For multiple sessions, render each and wrap in a combined page
    meta_title = f"Copilot CLI — {len(sessions)} Sessions"
    parts = []
    for i, s in enumerate(sessions, 1):
        sid = s.metadata.session_id[:8]
        parts.append(f'<h2>Session {i}: {_html_escape(s.metadata.summary or sid)}</h2>')
        # Render inner content (strip <html>/<body> wrappers)
        inner = render_html(s)
        # Extract just the container div content
        start = inner.find('<div class="container">')
        end = inner.rfind("</div>\n<script>")
        if start >= 0 and end >= 0:
            parts.append(inner[start:end + len("</div>")])
        else:
            parts.append(inner)
        parts.append("<hr />")

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{meta_title}</title>
<style>{_HTML_CSS}</style>
</head>
<body>
<div class="container">
<h1>{meta_title}</h1>
{"".join(parts)}
<div class="footer">Generated by <code>parse_copilot_session.py</code> at {now_utc}</div>
</div>
<script>{_HTML_JS}</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Multi-session rendering
# ---------------------------------------------------------------------------


def render_multi_session_markdown(sessions: List[ParsedSession]) -> str:
    """Render multiple sessions into a single Markdown document.

    Args:
        sessions: List of ParsedSession objects.

    Returns:
        Combined Markdown report.
    """
    if not sessions:
        return "# Copilot CLI Session Logs\n\nNo sessions found.\n"

    if len(sessions) == 1:
        return render_markdown(sessions[0])

    lines: List[str] = []
    lines.append("# Copilot CLI Session Logs")
    lines.append("")
    lines.append(f"Found **{len(sessions)}** matching sessions.")
    lines.append("")

    # Summary table
    lines.append("## Sessions Overview")
    lines.append("")
    lines.append("| # | Session ID | CWD | Model | Created | Turns | Events |")
    lines.append("|---|---|---|---|---|---|---|")
    for i, s in enumerate(sessions, 1):
        sid_short = s.metadata.session_id[:8] + "..."
        cwd_short = _truncate(s.metadata.cwd, 40)
        created = _format_timestamp(s.start_time or s.metadata.created_at)
        lines.append(
            f"| {i} | `{sid_short}` | `{cwd_short}` | `{s.selected_model}` "
            f"| {created} | {len(s.turns)} | {s.raw_event_count} |"
        )
    lines.append("")

    # Individual sessions
    for i, s in enumerate(sessions, 1):
        lines.append(f"---")
        lines.append("")
        # Re-render each session as a subsection
        individual = render_markdown(s)
        # Downgrade headers by one level (# -> ##, ## -> ###, etc.)
        for line in individual.splitlines():
            if line.startswith("# "):
                lines.append(f"## Session {i}: {line[2:]}")
            elif line.startswith("## "):
                lines.append(f"### {line[3:]}")
            elif line.startswith("### "):
                lines.append(f"#### {line[4:]}")
            else:
                lines.append(line)
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public convenience function (for library usage)
# ---------------------------------------------------------------------------


def parse_and_render(
    cwd: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
    session_id: Optional[str] = None,
    output: Optional[Path] = None,
    session_state_dir: Optional[Path] = None,
    fmt: str = "md",
) -> Optional[str]:
    """Find, parse, and render Copilot sessions.

    This is the primary entry point for library usage. Combines
    ``find_sessions``, ``parse_session``, and ``render_markdown`` /
    ``render_html``.

    Args:
        cwd: Filter by working directory.
        after: ISO 8601 timestamp — sessions after this time.
        before: ISO 8601 timestamp — sessions before this time.
        session_id: Directly specify a session UUID.
        output: If given, write output to this file path.
        session_state_dir: Override the session state directory.
        fmt: Output format — ``"md"`` (default) or ``"html"``.

    Returns:
        Rendered string (Markdown or HTML), or None if no sessions found.
    """
    sessions = find_sessions(
        cwd=cwd,
        after=after,
        before=before,
        session_id=session_id,
        session_state_dir=session_state_dir,
    )

    if not sessions:
        return None

    parsed = [parse_session(s) for s in sessions]

    if fmt == "html":
        rendered = render_multi_session_html(parsed)
    else:
        rendered = render_multi_session_markdown(parsed)

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")

    return rendered


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """CLI entry point for parse_copilot_session.py."""
    parser = argparse.ArgumentParser(
        description="Parse Copilot CLI session logs (events.jsonl) into Markdown or HTML.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Find sessions for a working directory\n"
            "  %(prog)s --cwd /path/to/project --output session_logs.md\n"
            "\n"
            "  # Export as self-contained HTML\n"
            "  %(prog)s --cwd /path/to/project --format html --output session.html\n"
            "\n"
            "  # Parse sessions after a timestamp\n"
            "  %(prog)s --cwd /path/to/project --after 2026-04-01T00:00:00\n"
            "\n"
            "  # Parse a specific session by UUID\n"
            "  %(prog)s --session-id <uuid> --output session_logs.md\n"
            "\n"
            "  # List matching sessions without parsing\n"
            "  %(prog)s --cwd /path/to/project --list\n"
        ),
    )
    parser.add_argument(
        "--cwd",
        help="Filter sessions by working directory (exact or prefix match)",
    )
    parser.add_argument(
        "--after",
        help="Only sessions created after this ISO 8601 timestamp",
    )
    parser.add_argument(
        "--before",
        help="Only sessions created before this ISO 8601 timestamp",
    )
    parser.add_argument(
        "--session-id",
        help="Parse a specific session by UUID",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "--session-state-dir",
        help=f"Override session state directory (default: {COPILOT_SESSION_STATE_DIR})",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List matching sessions without full parsing",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output (show progress to stderr)",
    )
    parser.add_argument(
        "--extract-output-dir",
        action="store_true",
        help="Extract output-dir from DONE sentinels and print to stdout (one per line)",
    )
    parser.add_argument(
        "--check-start-sentinel",
        action="store_true",
        help="Check if START sentinel was emitted; exit 0 if found, 1 if missing",
    )
    parser.add_argument(
        "--extract-session-id",
        action="store_true",
        help="Print session UUID(s) to stdout (one per line); no event parsing",
    )
    parser.add_argument(
        "--extract-session-dir",
        action="store_true",
        help="Print session state directory path(s) to stdout (one per line); no event parsing",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["md", "html"],
        default="md",
        dest="output_format",
        help="Output format: md (Markdown, default) or html (self-contained HTML)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.cwd and not args.session_id and not args.after:
        parser.error("At least one of --cwd, --session-id, or --after is required")

    session_state_dir = Path(args.session_state_dir) if args.session_state_dir else None

    # Find sessions
    sessions = find_sessions(
        cwd=args.cwd,
        after=args.after,
        before=args.before,
        session_id=args.session_id,
        session_state_dir=session_state_dir,
    )

    if not sessions:
        print("No matching sessions found.", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"Found {len(sessions)} matching session(s).", file=sys.stderr)

    # List mode
    if args.list:
        print(f"{'Session ID':<40} {'Created':<25} {'CWD'}")
        print("-" * 100)
        for meta in sessions:
            created = _format_timestamp(meta.created_at)
            print(f"{meta.session_id:<40} {created:<25} {meta.cwd}")
        return 0

    # Extract session-id mode: print UUID(s) without full event parsing
    if args.extract_session_id:
        for s in sessions:
            print(s.session_id)
        return 0

    # Extract session-dir mode: print state directory path(s) without parsing
    if args.extract_session_dir:
        for s in sessions:
            print(s.session_dir)
        return 0

    # Parse and render
    if args.verbose:
        print("Parsing events...", file=sys.stderr)

    parsed = [parse_session(s) for s in sessions]

    # Extract output-dir mode: print sentinel output-dir values and exit
    if args.extract_output_dir:
        all_dirs: List[str] = []
        for p in parsed:
            all_dirs.extend(extract_output_dirs(p))
        if all_dirs:
            for d in all_dirs:
                print(d)
            return 0
        else:
            if args.verbose:
                print("No DONE sentinel with output-dir found.", file=sys.stderr)
            return 1

    # Check START sentinel mode: verify at least one session has the marker
    if args.check_start_sentinel:
        found = False
        for p in parsed:
            if has_start_sentinel(p):
                found = True
                if args.verbose:
                    print(
                        f"START sentinel found in session {p.session_id}",
                        file=sys.stderr,
                    )
        if found:
            print("OK: START sentinel detected.")
            return 0
        else:
            print(
                "FAIL: No [DX-AGENTIC-DEV: START] sentinel found in any session.",
                file=sys.stderr,
            )
            return 1

    # Render in requested format
    if args.output_format == "html":
        rendered = render_multi_session_html(parsed)
    else:
        rendered = render_multi_session_markdown(parsed)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        if args.verbose:
            print(f"Written to {output_path}", file=sys.stderr)
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    sys.exit(main())
