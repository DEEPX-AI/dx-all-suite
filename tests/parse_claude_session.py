#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Parse Claude Code session logs (JSONL) into human-readable HTML or Markdown.

Claude Code stores session data in ``~/.claude/projects/<encoded-path>/<UUID>.jsonl``.
Each JSONL file contains line-delimited JSON messages in Anthropic API format with
extensions (timestamps, sessionId, tool_use/tool_result blocks, thinking blocks, etc.).

This script:

1. Finds matching sessions by project path, UUID, and/or time range
2. Parses Claude JSONL message types (user, assistant, attachment, ai-title, etc.)
3. Generates an HTML report (matching Copilot CLI /share html style) or Markdown

Usage::

    # Parse a specific session by UUID
    python parse_claude_session.py \\
        --session-id fe119090-f04e-4c04-afb9-7f19f969cdab \\
        --format html \\
        --output session_report.html

    # Find recent sessions for a project
    python parse_claude_session.py \\
        --project /data/home/dhyang/github/dx-all-suite \\
        --recent 5

    # Parse most recent session for a project
    python parse_claude_session.py \\
        --project /data/home/dhyang/github/dx-all-suite \\
        --format html \\
        --output latest.html

    # Include thinking blocks in output
    python parse_claude_session.py \\
        --session-id <UUID> \\
        --include-thinking \\
        --format html \\
        --output report.html
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
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
CLAUDE_HISTORY_FILE = Path.home() / ".claude" / "history.jsonl"

# ---------------------------------------------------------------------------
# Data model (mirrors parse_copilot_session.py for consistency)
# ---------------------------------------------------------------------------


@dataclass
class SessionMetadata:
    """Session metadata extracted from Claude JSONL."""

    session_id: str = ""
    cwd: str = ""
    git_branch: str = ""
    version: str = ""
    permission_mode: str = ""
    entrypoint: str = ""
    title: str = ""
    project_path: str = ""
    jsonl_path: Path = field(default_factory=Path)


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
class ThinkingBlock:
    """A thinking/reasoning block from assistant."""

    content: str = ""


@dataclass
class ConversationTurn:
    """A single conversation turn (user message + assistant response)."""

    turn_index: int = 0
    user_content: str = ""
    assistant_content: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    thinking_blocks: List[ThinkingBlock] = field(default_factory=list)
    skills_invoked: List[str] = field(default_factory=list)
    timestamp: str = ""


@dataclass
class ParsedSession:
    """Fully parsed Claude Code session."""

    metadata: SessionMetadata
    claude_version: str = ""
    model: str = ""
    start_time: str = ""
    end_time: str = ""
    turns: List[ConversationTurn] = field(default_factory=list)
    attachments: List[str] = field(default_factory=list)
    raw_message_count: int = 0


# ---------------------------------------------------------------------------
# Sentinel extraction (shared with parse_copilot_session.py)
# ---------------------------------------------------------------------------

_SENTINEL_OUTPUT_DIR_RE = re.compile(
    r"\[DX-AGENTIC-DEV:\s*DONE\s*\(output-dir:\s*([^)]+)\)\]"
)
_SENTINEL_START_RE = re.compile(r"\[DX-AGENTIC-DEV:\s*START\]")


def extract_output_dirs(parsed: ParsedSession) -> List[str]:
    """Extract output directories from DONE sentinels in assistant messages."""
    dirs: List[str] = []
    for turn in parsed.turns:
        for m in _SENTINEL_OUTPUT_DIR_RE.finditer(turn.assistant_content):
            raw = m.group(1).strip()
            for part in raw.split("+"):
                part = part.strip().rstrip("/")
                if part:
                    dirs.append(part)
    return dirs


def has_start_sentinel(parsed: ParsedSession) -> bool:
    """Check if the session has a [DX-AGENTIC-DEV: START] sentinel."""
    for turn in parsed.turns:
        if _SENTINEL_START_RE.search(turn.assistant_content):
            return True
    return False


# ---------------------------------------------------------------------------
# Session discovery
# ---------------------------------------------------------------------------


def encode_project_path(project_path: str) -> str:
    """Encode a project path to Claude's directory naming convention.

    Claude replaces '/' with '-' in the project path to create the directory name.
    Example: /data/home/dhyang/github/dx-all-suite → -data-home-dhyang-github-dx-all-suite
    """
    return project_path.replace("/", "-")


def find_project_dir(project_path: str) -> Optional[Path]:
    """Find the Claude projects directory for a given project path."""
    encoded = encode_project_path(project_path)
    project_dir = CLAUDE_PROJECTS_DIR / encoded
    if project_dir.is_dir():
        return project_dir
    return None


def find_sessions(
    project_path: Optional[str] = None,
    session_id: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
) -> List[SessionMetadata]:
    """Find Claude Code sessions matching the given criteria.

    Args:
        project_path: Absolute path to the project directory.
        session_id: Specific session UUID to find.
        after: ISO timestamp — only sessions modified after this time.
        before: ISO timestamp — only sessions modified before this time.

    Returns:
        List of SessionMetadata objects sorted by modification time (newest first).
    """
    results: List[SessionMetadata] = []

    if session_id:
        # Search all project dirs for the specific session
        if CLAUDE_PROJECTS_DIR.is_dir():
            for project_dir in CLAUDE_PROJECTS_DIR.iterdir():
                if not project_dir.is_dir():
                    continue
                jsonl_path = project_dir / f"{session_id}.jsonl"
                if jsonl_path.is_file():
                    meta = _extract_metadata(jsonl_path)
                    if meta:
                        results.append(meta)
                    break
        return results

    if project_path:
        project_dir = find_project_dir(project_path)
        if not project_dir:
            return []
    else:
        # If no project path, search all
        if not CLAUDE_PROJECTS_DIR.is_dir():
            return []
        # Just return empty — require at least project_path or session_id
        return []

    # Parse time filters
    after_dt = _parse_iso(after) if after else None
    before_dt = _parse_iso(before) if before else None

    for jsonl_file in project_dir.glob("*.jsonl"):
        mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime, tz=timezone.utc)
        if after_dt and mtime < after_dt:
            continue
        if before_dt and mtime > before_dt:
            continue

        meta = _extract_metadata(jsonl_file)
        if meta:
            results.append(meta)

    # Sort by file modification time (newest first)
    results.sort(
        key=lambda m: m.jsonl_path.stat().st_mtime if m.jsonl_path.exists() else 0,
        reverse=True,
    )
    return results


def _extract_metadata(jsonl_path: Path) -> Optional[SessionMetadata]:
    """Extract metadata from the first few lines of a Claude JSONL file."""
    meta = SessionMetadata(jsonl_path=jsonl_path)
    meta.session_id = jsonl_path.stem

    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 30:  # Only scan first 30 lines for metadata
                    break
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                entry_type = entry.get("type", "")

                if entry_type == "user" and not meta.cwd:
                    meta.cwd = entry.get("cwd", "")
                    meta.git_branch = entry.get("gitBranch", "")
                    meta.version = entry.get("version", "")
                    meta.permission_mode = entry.get("permissionMode", "")
                    meta.entrypoint = entry.get("entrypoint", "")
                    meta.session_id = entry.get("sessionId", meta.session_id)

                elif entry_type == "ai-title":
                    content = entry.get("aiTitle", entry.get("content", ""))
                    if content:
                        meta.title = content

    except (OSError, PermissionError):
        return None

    return meta


# ---------------------------------------------------------------------------
# Session parsing
# ---------------------------------------------------------------------------


def parse_session(meta: SessionMetadata, include_thinking: bool = False) -> ParsedSession:
    """Parse a Claude Code JSONL session file into a ParsedSession.

    Args:
        meta: SessionMetadata with jsonl_path set.
        include_thinking: Whether to include thinking blocks in output.

    Returns:
        Fully parsed session.
    """
    session = ParsedSession(metadata=meta)

    entries = _read_jsonl(meta.jsonl_path)
    session.raw_message_count = len(entries)

    _process_entries(entries, session, include_thinking)

    return session


def _read_jsonl(filepath: Path) -> List[Dict[str, Any]]:
    """Read all JSON lines from a file."""
    entries: List[Dict[str, Any]] = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except (OSError, PermissionError):
        pass
    return entries


def _process_entries(
    entries: List[Dict[str, Any]],
    session: ParsedSession,
    include_thinking: bool,
) -> None:
    """Process all JSONL entries into the ParsedSession structure."""
    # Collect tool_results by tool_use_id for matching
    tool_results: Dict[str, str] = {}  # tool_use_id -> result content

    # First pass: collect all tool_results
    for entry in entries:
        if entry.get("type") == "user":
            content = entry.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        tool_use_id = block.get("tool_use_id", "")
                        result = block.get("content", "")
                        if isinstance(result, str):
                            tool_results[tool_use_id] = result
                        elif isinstance(result, list):
                            # Content blocks (text, image, etc.)
                            parts = []
                            for rb in result:
                                if isinstance(rb, dict) and rb.get("type") == "text":
                                    parts.append(rb.get("text", ""))
                            tool_results[tool_use_id] = "\n".join(parts)

    # Second pass: build conversation turns
    current_turn: Optional[ConversationTurn] = None
    turn_index = 0

    for entry in entries:
        entry_type = entry.get("type", "")
        timestamp = entry.get("timestamp", "")

        # Update session metadata from first entries
        if entry_type == "user" and not session.start_time:
            session.start_time = timestamp
            version = entry.get("version", "")
            if version:
                session.claude_version = version

        if entry_type == "ai-title":
            title = entry.get("aiTitle", entry.get("content", ""))
            if title:
                session.metadata.title = title

        elif entry_type == "attachment":
            content = entry.get("content", "")
            if content:
                session.attachments.append(content)

        elif entry_type == "user":
            msg = entry.get("message", {})
            content = msg.get("content", "")

            # Extract user text (skip tool_result entries)
            user_text = _extract_user_text(content)

            if user_text:
                # Start a new turn
                if current_turn and (current_turn.user_content or current_turn.assistant_content):
                    session.turns.append(current_turn)

                turn_index += 1
                current_turn = ConversationTurn(
                    turn_index=turn_index,
                    user_content=user_text,
                    timestamp=timestamp,
                )

        elif entry_type == "assistant":
            msg = entry.get("message", {})
            content = msg.get("content", [])

            if not current_turn:
                turn_index += 1
                current_turn = ConversationTurn(turn_index=turn_index, timestamp=timestamp)

            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue

                    block_type = block.get("type", "")

                    if block_type == "text":
                        text = block.get("text", "")
                        if text:
                            if current_turn.assistant_content:
                                current_turn.assistant_content += "\n" + text
                            else:
                                current_turn.assistant_content = text

                    elif block_type == "tool_use":
                        tool_id = block.get("id", "")
                        tool_name = block.get("name", "")
                        tool_input = block.get("input", {})

                        # Format arguments
                        if isinstance(tool_input, dict):
                            args_str = json.dumps(tool_input, ensure_ascii=False)
                        else:
                            args_str = str(tool_input)

                        tc = ToolCall(
                            tool_call_id=tool_id,
                            tool_name=tool_name,
                            arguments=args_str,
                            result_content=tool_results.get(tool_id, ""),
                            success=True if tool_id in tool_results else None,
                        )
                        current_turn.tool_calls.append(tc)

                        # Track skill invocations
                        if tool_name == "Skill":
                            skill_name = tool_input.get("skill", "") if isinstance(tool_input, dict) else ""
                            if skill_name:
                                current_turn.skills_invoked.append(skill_name)

                    elif block_type == "thinking" and include_thinking:
                        thinking_text = block.get("thinking", "")
                        if thinking_text:
                            current_turn.thinking_blocks.append(
                                ThinkingBlock(content=thinking_text)
                            )

            # Update end_time
            if timestamp:
                session.end_time = timestamp

    # Append last turn
    if current_turn and (current_turn.user_content or current_turn.assistant_content):
        session.turns.append(current_turn)


def _extract_user_text(content) -> str:
    """Extract user text from message content, skipping tool_result blocks."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                # Skip tool_result blocks — they're tool responses, not user input
        return "\n".join(parts)

    return ""


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

_HTML_CSS = """\
:root {
  --bg: #0d1117; --bg-muted: #151b23; --fg: #f0f6fc; --fg-muted: #9198a1;
  --border: #3d444d; --accent: #4493f8; --success: #3fb950; --warning: #d29922;
  --error: #f85149; --brand: #ab7df8; --code-bg: #1c2128; --thinking-bg: #1a1f2b;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg: #ffffff; --bg-muted: #f6f8fa; --fg: #1f2328; --fg-muted: #59636e;
    --border: #d1d9e0; --accent: #0969da; --success: #1a7f37; --warning: #9a6700;
    --error: #cf222e; --brand: #8250df; --code-bg: #f6f8fa; --thinking-bg: #f0f4f8;
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
.entry.thinking { border-left-color: var(--warning); background: var(--thinking-bg); }
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
    """Convert Markdown text to simple HTML (code blocks, inline code, paragraphs)."""
    # Fenced code blocks: ```lang\n...\n```
    def _code_block(m: re.Match) -> str:
        lang = _html_escape(m.group(1) or "")
        code = _html_escape(m.group(2))
        lang_attr = f' data-lang="{lang}"' if lang else ""
        return f"<pre{lang_attr}><code>{code}</code></pre>"

    text = re.sub(r"```(\w*)\n(.*?)```", _code_block, text, flags=re.DOTALL)

    # Inline code: `...`
    text = re.sub(r"`([^`\n]+)`", lambda m: f"<code>{_html_escape(m.group(1))}</code>", text)

    # Bold: **...**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    # Split into paragraphs on blank lines (but preserve <pre> blocks)
    parts = re.split(r"(<pre.*?</pre>)", text, flags=re.DOTALL)
    result_parts = []
    for part in parts:
        if part.startswith("<pre"):
            result_parts.append(part)
        else:
            paragraphs = re.split(r"\n{2,}", part.strip())
            for p in paragraphs:
                p = p.strip()
                if p:
                    result_parts.append(f"<p>{p}</p>")
    return "\n".join(result_parts)


def _format_timestamp(ts: str) -> str:
    """Format an ISO timestamp to a short display format."""
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except (ValueError, TypeError):
        return ts[:19] if len(ts) >= 19 else ts


def _truncate(text: str, max_len: int = 500) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


def render_html(session: ParsedSession) -> str:
    """Render a ParsedSession as a self-contained HTML page.

    Returns:
        Complete HTML document string.
    """
    meta = session.metadata
    title = _html_escape(meta.title or f"Claude Code Session {meta.session_id[:8]}")

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

        # Thinking blocks (if included)
        for tb in turn.thinking_blocks:
            entry_idx += 1
            thinking_html = _html_escape(_truncate(tb.content, 2000))
            entries.append(
                f'<div class="entry thinking collapsed" id="entry-{entry_idx}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">&#x1F4AD;</span>'
                f'<span class="label">Thinking</span>'
                f'<span class="time">click to expand</span>'
                f'</div>'
                f'<div class="entry-body"><pre>{thinking_html}</pre></div>'
                f'</div>'
            )

        # Tool calls
        for tc in turn.tool_calls:
            entry_idx += 1
            status_cls = "tool-ok" if tc.success else "tool-fail" if tc.success is False else "tool-ok"
            status_icon = "&#x2705;" if tc.success else "&#x274C;" if tc.success is False else "&#x2699;"

            # Format tool arguments (show key info)
            args_display = _format_tool_args(tc.tool_name, tc.arguments)
            args_html = f'<div class="tool-args"><code>{_html_escape(args_display)}</code></div>' if args_display else ""

            result_html = ""
            if tc.result_content:
                truncated_result = _truncate(tc.result_content, 1000)
                result_html = f'<div class="tool-result"><pre>{_html_escape(truncated_result)}</pre></div>'

            entries.append(
                f'<div class="entry {status_cls} collapsed" id="entry-{entry_idx}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">{status_icon}</span>'
                f'<span class="label">{_html_escape(tc.tool_name)}</span>'
                f'<span class="time">click to expand</span>'
                f'</div>'
                f'<div class="entry-body">{args_html}{result_html}</div>'
                f'</div>'
            )

        # Assistant response
        if turn.assistant_content:
            entry_idx += 1
            assistant_html = _md_to_html_simple(turn.assistant_content)
            entries.append(
                f'<div class="entry assistant" id="entry-{entry_idx}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">&#x1F4AC;</span>'
                f'<span class="label">Claude</span>'
                f'<span class="time">{time_label}</span>'
                f'</div>'
                f'<div class="entry-body">{assistant_html}</div>'
                f'</div>'
            )

    # Summary section
    summary_rows: List[str] = []
    total_tool_calls = sum(len(t.tool_calls) for t in session.turns)
    total_turns = len(session.turns)
    skills = set()
    for t in session.turns:
        skills.update(t.skills_invoked)

    summary_rows.append(f"<tr><td>Turns</td><td>{total_turns}</td></tr>")
    summary_rows.append(f"<tr><td>Tool calls</td><td>{total_tool_calls}</td></tr>")
    summary_rows.append(f"<tr><td>Messages (raw)</td><td>{session.raw_message_count}</td></tr>")
    if skills:
        summary_rows.append(f"<tr><td>Skills invoked</td><td>{', '.join(sorted(skills))}</td></tr>")

    # Tool usage breakdown
    tool_counts: Dict[str, int] = {}
    for t in session.turns:
        for tc in t.tool_calls:
            tool_counts[tc.tool_name] = tool_counts.get(tc.tool_name, 0) + 1
    if tool_counts:
        tool_str = ", ".join(f"{name}: {count}" for name, count in sorted(tool_counts.items(), key=lambda x: -x[1]))
        summary_rows.append(f"<tr><td>Tool breakdown</td><td>{_html_escape(tool_str)}</td></tr>")

    summary_html = (
        '<div class="summary-section">'
        "<h2>Session Summary</h2>"
        '<table class="summary-table">'
        + "\n".join(summary_rows)
        + "</table></div>"
    )

    # Metadata table
    meta_rows: List[str] = []
    meta_rows.append(f"<tr><td>Session ID</td><td><code>{_html_escape(meta.session_id)}</code></td></tr>")
    if meta.cwd:
        meta_rows.append(f"<tr><td>Working Dir</td><td><code>{_html_escape(meta.cwd)}</code></td></tr>")
    if meta.git_branch:
        meta_rows.append(f"<tr><td>Branch</td><td>{_html_escape(meta.git_branch)}</td></tr>")
    if session.claude_version:
        meta_rows.append(f"<tr><td>Claude Code</td><td>v{_html_escape(session.claude_version)}</td></tr>")
    if meta.permission_mode:
        meta_rows.append(f"<tr><td>Permission Mode</td><td>{_html_escape(meta.permission_mode)}</td></tr>")
    if session.start_time:
        meta_rows.append(f"<tr><td>Start</td><td>{_html_escape(session.start_time)}</td></tr>")
    if session.end_time:
        meta_rows.append(f"<tr><td>End</td><td>{_html_escape(session.end_time)}</td></tr>")

    meta_html = '<table class="meta-table">' + "\n".join(meta_rows) + "</table>"

    # Assemble full HTML
    entries_html = "\n".join(entries)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
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
{meta_html}
<hr />
{entries_html}
<hr />
{summary_html}
<div class="footer">
Generated by parse_claude_session.py &middot; {now_str}
</div>
</div>
<script>{_HTML_JS}</script>
</body>
</html>"""

    return html


def _format_tool_args(tool_name: str, args_json: str) -> str:
    """Format tool arguments for display — show the most relevant info."""
    try:
        args = json.loads(args_json)
    except (json.JSONDecodeError, TypeError):
        return _truncate(args_json, 200)

    if not isinstance(args, dict):
        return _truncate(str(args), 200)

    if tool_name == "Bash":
        cmd = args.get("command", "")
        return _truncate(cmd, 300)
    elif tool_name == "Read":
        return args.get("file_path", args.get("path", ""))
    elif tool_name in ("Write", "Edit"):
        return args.get("file_path", args.get("path", ""))
    elif tool_name == "Skill":
        return args.get("skill", "")
    elif tool_name in ("Grep", "Search"):
        return args.get("pattern", args.get("query", ""))
    else:
        return _truncate(args_json, 200)


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_markdown(session: ParsedSession) -> str:
    """Render a ParsedSession as Markdown text."""
    meta = session.metadata
    lines: List[str] = []

    title = meta.title or f"Claude Code Session {meta.session_id[:8]}"
    lines.append(f"# {title}")
    lines.append("")

    # Metadata
    lines.append("## Session Info")
    lines.append("")
    lines.append(f"- **Session ID:** `{meta.session_id}`")
    if meta.cwd:
        lines.append(f"- **Working Dir:** `{meta.cwd}`")
    if meta.git_branch:
        lines.append(f"- **Branch:** {meta.git_branch}")
    if session.claude_version:
        lines.append(f"- **Claude Code:** v{session.claude_version}")
    if meta.permission_mode:
        lines.append(f"- **Permission Mode:** {meta.permission_mode}")
    if session.start_time:
        lines.append(f"- **Start:** {session.start_time}")
    if session.end_time:
        lines.append(f"- **End:** {session.end_time}")
    lines.append("")

    # Conversation
    lines.append("## Conversation")
    lines.append("")

    for turn in session.turns:
        time_str = _format_timestamp(turn.timestamp)
        lines.append(f"### Turn {turn.turn_index} [{time_str}]")
        lines.append("")

        if turn.user_content:
            lines.append("**User:**")
            lines.append("")
            lines.append(f"> {turn.user_content}")
            lines.append("")

        for tc in turn.tool_calls:
            status = "✅" if tc.success else "❌" if tc.success is False else "⚙️"
            args_display = _format_tool_args(tc.tool_name, tc.arguments)
            lines.append(f"{status} **{tc.tool_name}** `{_truncate(args_display, 100)}`")
            if tc.result_content:
                result_preview = _truncate(tc.result_content, 200)
                lines.append(f"  > {result_preview}")
            lines.append("")

        if turn.assistant_content:
            lines.append("**Claude:**")
            lines.append("")
            lines.append(turn.assistant_content)
            lines.append("")

        lines.append("---")
        lines.append("")

    # Summary
    total_tools = sum(len(t.tool_calls) for t in session.turns)
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Turns:** {len(session.turns)}")
    lines.append(f"- **Tool calls:** {total_tools}")
    lines.append(f"- **Raw messages:** {session.raw_message_count}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse Claude Code session JSONL into HTML or Markdown reports."
    )
    parser.add_argument(
        "--session-id",
        help="Specific session UUID to parse.",
    )
    parser.add_argument(
        "--project",
        help="Project path (used to locate sessions). Defaults to cwd.",
    )
    parser.add_argument(
        "--after",
        help="Only sessions modified after this ISO timestamp.",
    )
    parser.add_argument(
        "--before",
        help="Only sessions modified before this ISO timestamp.",
    )
    parser.add_argument(
        "--recent",
        type=int,
        help="List N most recent sessions (no parsing, just metadata).",
    )
    parser.add_argument(
        "--format",
        choices=["html", "md", "markdown"],
        default="html",
        help="Output format (default: html).",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path. If not specified, prints to stdout.",
    )
    parser.add_argument(
        "--include-thinking",
        action="store_true",
        help="Include thinking/reasoning blocks in output.",
    )

    args = parser.parse_args()

    # Determine project path
    project_path = args.project or os.getcwd()

    # List recent sessions mode
    if args.recent:
        sessions = find_sessions(project_path=project_path, after=args.after, before=args.before)
        if not sessions:
            print(f"No sessions found for project: {project_path}", file=sys.stderr)
            return 1

        print(f"Recent sessions for: {project_path}")
        print(f"{'─' * 80}")
        for i, meta in enumerate(sessions[: args.recent]):
            mtime = datetime.fromtimestamp(meta.jsonl_path.stat().st_mtime)
            title = meta.title or "(no title)"
            print(f"  {i + 1}. {meta.session_id}")
            print(f"     Title: {title}")
            print(f"     Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            if meta.git_branch:
                print(f"     Branch: {meta.git_branch}")
            print()
        return 0

    # Find session
    sessions = find_sessions(
        project_path=project_path,
        session_id=args.session_id,
        after=args.after,
        before=args.before,
    )

    if not sessions:
        print("No matching sessions found.", file=sys.stderr)
        return 1

    # Parse the first (or specified) session
    meta = sessions[0]
    session = parse_session(meta, include_thinking=args.include_thinking)

    # Render
    if args.format == "html":
        output = render_html(session)
    else:
        output = render_markdown(session)

    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
        print(f"Written to: {output_path}", file=sys.stderr)
    else:
        print(output)

    return 0


def _parse_iso(timestamp_str: str) -> Optional[datetime]:
    """Parse an ISO timestamp string to datetime."""
    if not timestamp_str:
        return None
    try:
        ts = timestamp_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


if __name__ == "__main__":
    sys.exit(main())
