#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Shared utilities for session parsers (Copilot, Cursor, Claude).

This module contains:
- Common dataclasses (ToolCall)
- HTML rendering utilities (CSS, JS, escape, Markdown-to-HTML)
- Sentinel extraction helpers
- Timestamp and text formatting
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List, Optional, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Sentinel extraction
# ---------------------------------------------------------------------------

_SENTINEL_OUTPUT_DIR_RE = re.compile(
    r"\[DX-AGENT-DEV:\s*DONE\s*\(output-dir:\s*([^)]+)\)\]"
)

_SENTINEL_START_RE = re.compile(r"\[DX-AGENT-DEV:\s*START\]")


@runtime_checkable
class HasTurns(Protocol):
    """Protocol for objects with conversation turns."""

    @property
    def turns(self) -> list: ...


def extract_output_dirs_from_turns(turns: list) -> List[str]:
    """Extract output-dir values from DONE sentinels in assistant responses.

    Works with any turn objects that have an ``assistant_content`` attribute.
    """
    seen: set[str] = set()
    result: List[str] = []
    for turn in turns:
        content = getattr(turn, "assistant_content", "")
        for m in _SENTINEL_OUTPUT_DIR_RE.finditer(content):
            path = m.group(1).strip().rstrip("/")
            if path and path not in seen:
                seen.add(path)
                result.append(path)
    return result


def has_start_sentinel_in_turns(turns: list) -> bool:
    """Check whether any turn contains the START sentinel."""
    for turn in turns:
        content = getattr(turn, "assistant_content", "")
        if _SENTINEL_START_RE.search(content):
            return True
    return False


# ---------------------------------------------------------------------------
# Common dataclass
# ---------------------------------------------------------------------------


@dataclass
class ToolCall:
    """A single tool invocation with result."""

    tool_call_id: str = ""
    tool_name: str = ""
    arguments: str = ""
    success: Optional[bool] = None
    result_content: str = ""
    duration_ms: Optional[float] = None


# ---------------------------------------------------------------------------
# HTML constants
# ---------------------------------------------------------------------------

HTML_CSS = """\
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
.entry.thinking { border-left-color: var(--warning); }
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

HTML_JS = """\
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.entry-hdr').forEach(function(hdr) {
    hdr.addEventListener('click', function() {
      hdr.parentElement.classList.toggle('collapsed');
    });
  });
});
"""


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------


def html_escape(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def md_to_html_simple(text: str) -> str:
    """Convert Markdown text to simple HTML (code blocks, inline code, paragraphs).

    Intentionally minimal — covers patterns commonly seen in agent responses.
    """
    # Fenced code blocks: ```lang\n...\n```
    def _code_block(m: re.Match) -> str:
        lang = html_escape(m.group(1) or "")
        code = html_escape(m.group(2))
        lang_attr = f' data-lang="{lang}"' if lang else ""
        return f"<pre{lang_attr}><code>{code}</code></pre>"

    text = re.sub(r"```(\w*)\n(.*?)```", _code_block, text, flags=re.DOTALL)

    # Split into paragraphs on blank lines (but preserve <pre> blocks)
    parts = re.split(r"(<pre.*?</pre>)", text, flags=re.DOTALL)
    result_parts = []
    for part in parts:
        if part.startswith("<pre"):
            result_parts.append(part)
        else:
            safe_part = html_escape(part)

            # Inline code: `...`
            safe_part = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", safe_part)

            # Bold: **...**
            safe_part = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe_part)

            paragraphs = re.split(r"\n{2,}", safe_part.strip())
            for p in paragraphs:
                p = p.strip()
                if p:
                    result_parts.append(f"<p>{p}</p>")
    return "\n".join(result_parts)


def format_timestamp(ts: str) -> str:
    """Format an ISO timestamp for display."""
    if not ts:
        return "—"
    dt = parse_iso(ts)
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    return ts


def format_timestamp_short(ts: str) -> str:
    """Format an ISO timestamp to a short display format (HH:MM:SS)."""
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except (ValueError, TypeError):
        return ts[:19] if len(ts) >= 19 else ts


def truncate(text: str, max_len: int = 500) -> str:
    """Truncate text to max_len characters, adding ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def indent_blockquote(text: str) -> str:
    """Indent text for Markdown blockquote (handle multi-line)."""
    lines = text.splitlines()
    if len(lines) <= 1:
        return text
    return "\n> ".join(lines)


def parse_iso(timestamp_str: str) -> Optional[datetime]:
    """Parse an ISO timestamp string to datetime."""
    if not timestamp_str:
        return None
    try:
        ts = timestamp_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def ts_from_ms(ts_ms: int) -> str:
    """Convert epoch milliseconds to ISO 8601 local timestamp."""
    try:
        dt = datetime.fromtimestamp(ts_ms / 1000.0)
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        return ""
