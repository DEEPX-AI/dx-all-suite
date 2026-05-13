#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Parse OpenCode CLI stream-json (NDJSON) into self-contained HTML.

OpenCode ``--format json`` emits line-delimited JSON events:
- ``step_start`` — beginning of a model step
- ``text`` — assistant text output
- ``tool_use`` — tool invocation with input/output
- ``step_finish`` — end of a model step with token/cost info

This module parses those events into a lightweight session model and renders
an HTML transcript using shared helpers from ``session_common.py``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from session_common import (
    HTML_CSS,
    HTML_JS,
    ToolCall,
    extract_output_dirs_from_turns,
    has_start_sentinel_in_turns,
    html_escape,
    md_to_html_simple,
    truncate,
    ts_from_ms,
)


@dataclass
class SessionMetadata:
    session_id: str = ""
    scenario_key: str = ""
    total_tokens: int = 0
    total_cost: float = 0.0
    step_count: int = 0


@dataclass
class ConversationTurn:
    role: str = ""  # "assistant" | "tool"
    content: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    timestamp_ms: int = 0


@dataclass
class ParsedSession:
    metadata: SessionMetadata = field(default_factory=SessionMetadata)
    turns: List[ConversationTurn] = field(default_factory=list)


def parse_opencode_jsonl(jsonl_path: Path) -> ParsedSession:
    """Parse OpenCode NDJSON file into a structured session."""
    session = ParsedSession()
    current_texts: List[str] = []
    current_ts: int = 0

    raw = jsonl_path.read_text(encoding="utf-8", errors="replace")

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        etype = event.get("type", "")
        part = event.get("part", {})
        ts = event.get("timestamp", 0)

        if not session.metadata.session_id:
            sid = event.get("sessionID", "")
            if sid:
                session.metadata.session_id = sid

        if etype == "text":
            text = part.get("text", "")
            if text:
                current_texts.append(text)
                if not current_ts:
                    current_ts = ts

        elif etype == "tool_use":
            # Flush pending text as an assistant turn
            if current_texts:
                session.turns.append(ConversationTurn(
                    role="assistant",
                    content="\n".join(current_texts),
                    timestamp_ms=current_ts,
                ))
                current_texts = []
                current_ts = 0

            state = part.get("state", {})
            tool_name = part.get("tool", "unknown")
            tool_input_raw = state.get("input", {})
            tool_output_raw = state.get("output", "")
            status = state.get("status", "")

            # Format input
            if isinstance(tool_input_raw, dict):
                tool_input_str = json.dumps(tool_input_raw, indent=2, ensure_ascii=False)
            else:
                tool_input_str = str(tool_input_raw)

            # Truncate large outputs
            tool_output_str = str(tool_output_raw)
            if len(tool_output_str) > 8000:
                tool_output_str = tool_output_str[:8000] + "\n... (truncated)"

            tc = ToolCall(
                tool_name=tool_name,
                arguments=tool_input_str,
                result_content=tool_output_str,
                success=(status == "completed"),
            )
            session.turns.append(ConversationTurn(
                role="tool",
                tool_calls=[tc],
                timestamp_ms=ts,
            ))

        elif etype == "step_start":
            session.metadata.step_count += 1

        elif etype == "step_finish":
            tokens = part.get("tokens", {})
            session.metadata.total_tokens += tokens.get("total", 0)
            session.metadata.total_cost += part.get("cost", 0)

    # Flush remaining text
    if current_texts:
        session.turns.append(ConversationTurn(
            role="assistant",
            content="\n".join(current_texts),
            timestamp_ms=current_ts,
        ))

    return session


def _render_turn_html(turn: ConversationTurn, index: int) -> str:
    """Render a single conversation turn to HTML."""
    parts: List[str] = []

    ts_str = ts_from_ms(turn.timestamp_ms) if turn.timestamp_ms else ""
    ts_badge = f'<span class="timestamp">{ts_str}</span>' if ts_str else ""

    if turn.role == "assistant":
        parts.append(f'<div class="turn assistant">')
        parts.append(f'  <div class="turn-header">🤖 Assistant {ts_badge}</div>')
        parts.append(f'  <div class="turn-content">{md_to_html_simple(html_escape(turn.content))}</div>')
        parts.append(f'</div>')

    elif turn.role == "tool":
        for tc in turn.tool_calls:
            status_class = "success" if tc.success else "error"
            status_icon = "✅" if tc.success else "❌"
            status_text = "completed" if tc.success else "failed"
            parts.append(f'<div class="turn tool">')
            parts.append(f'  <details>')
            parts.append(f'    <summary class="tool-summary">')
            parts.append(f'      🔧 <strong>{html_escape(tc.tool_name)}</strong> '
                         f'<span class="status-{status_class}">{status_icon} {status_text}</span> '
                         f'{ts_badge}')
            parts.append(f'    </summary>')
            if tc.arguments:
                parts.append(f'    <div class="tool-section">')
                parts.append(f'      <div class="tool-label">Input:</div>')
                parts.append(f'      <pre class="tool-io">{html_escape(truncate(tc.arguments, 3000))}</pre>')
                parts.append(f'    </div>')
            if tc.result_content:
                parts.append(f'    <div class="tool-section">')
                parts.append(f'      <div class="tool-label">Output:</div>')
                parts.append(f'      <pre class="tool-io">{html_escape(truncate(tc.result_content, 3000))}</pre>')
                parts.append(f'    </div>')
            parts.append(f'  </details>')
            parts.append(f'</div>')

    return "\n".join(parts)


def _build_html(session: ParsedSession, scenario_key: str = "") -> str:
    """Build self-contained HTML document from parsed session."""
    meta = session.metadata
    title = scenario_key or meta.session_id or "OpenCode Session"

    turns_html = "\n".join(
        _render_turn_html(t, i) for i, t in enumerate(session.turns)
    )

    output_dirs = extract_output_dirs_from_turns(session.turns)
    has_start = has_start_sentinel_in_turns(session.turns)

    summary_items = [
        f"<li><strong>Session ID:</strong> {html_escape(meta.session_id)}</li>",
        f"<li><strong>Scenario:</strong> {html_escape(scenario_key)}</li>" if scenario_key else "",
        f"<li><strong>Steps:</strong> {meta.step_count}</li>",
        f"<li><strong>Total tokens:</strong> {meta.total_tokens:,}</li>",
        f"<li><strong>Turns:</strong> {len(session.turns)}</li>",
        f"<li><strong>Tool calls:</strong> {sum(len(t.tool_calls) for t in session.turns)}</li>",
        f"<li><strong>START sentinel:</strong> {'✅' if has_start else '❌'}</li>",
        f"<li><strong>Output dirs:</strong> {', '.join(output_dirs) if output_dirs else 'none detected'}</li>",
    ]
    summary_html = "\n".join(s for s in summary_items if s)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_escape(title)}</title>
<style>
{HTML_CSS}
.tool-summary {{ cursor: pointer; padding: 6px 10px; border-radius: 4px; }}
.tool-summary:hover {{ background: #333; }}
.tool-section {{ margin: 8px 0 8px 20px; }}
.tool-label {{ font-weight: bold; color: #8b949e; font-size: 0.85em; margin-bottom: 4px; }}
.tool-io {{ background: #161b22; padding: 10px; border-radius: 4px; font-size: 0.82em;
             max-height: 400px; overflow-y: auto; white-space: pre-wrap; word-break: break-word; }}
.status-success {{ color: #3fb950; }}
.status-error {{ color: #f85149; }}
.timestamp {{ color: #8b949e; font-size: 0.8em; margin-left: 8px; }}
.summary-box {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px;
                padding: 16px; margin-bottom: 20px; }}
.summary-box ul {{ list-style: none; padding: 0; margin: 0; }}
.summary-box li {{ padding: 3px 0; }}
</style>
</head>
<body>
<div class="container">
  <h1>🟢 OpenCode Session — {html_escape(title)}</h1>
  <div class="summary-box">
    <h3>Session Summary</h3>
    <ul>
      {summary_html}
    </ul>
  </div>
  <div class="conversation">
    {turns_html}
  </div>
</div>
<script>
{HTML_JS}
</script>
</body>
</html>"""


def render_opencode_html(
    jsonl_path: Path,
    output_path: Path,
    session_id_override: str = "",
    scenario_key: str = "",
) -> Optional[str]:
    """Render OpenCode JSONL to self-contained HTML.

    Args:
        jsonl_path: Path to the OpenCode stream JSONL file.
        output_path: Where to write the HTML.
        session_id_override: Override the session ID from the JSONL.
        scenario_key: Scenario key for the report title.

    Returns:
        The session ID extracted (or overridden), or ``None`` on failure.
    """
    try:
        if not jsonl_path.exists():
            return None

        session = parse_opencode_jsonl(jsonl_path)

        if session_id_override:
            session.metadata.session_id = session_id_override
        if scenario_key:
            session.metadata.scenario_key = scenario_key

        html = _build_html(session, scenario_key=scenario_key)
        output_path.write_text(html, encoding="utf-8")

        return session.metadata.session_id or None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <opencode-stream.jsonl> [output.html]")
        sys.exit(1)

    jsonl = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else jsonl.with_suffix(".html")

    sid = render_opencode_html(jsonl, out, scenario_key=jsonl.stem)
    if sid:
        print(f"✓ Wrote {out} (session: {sid}, size: {out.stat().st_size:,} bytes)")
    else:
        print(f"✗ Failed to parse {jsonl}", file=sys.stderr)
        sys.exit(1)
