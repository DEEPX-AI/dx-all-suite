#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Parse OpenCode session data into self-contained HTML.

Supports two input sources:
- OpenCode CLI ``--format json`` stream output (NDJSON)
- OpenCode SQLite databases (global or project-local)

The DB parser prefers richer persistent data when available, then falls back to
stream JSONL parsing.
"""

from __future__ import annotations

# --- self-bootstrap: make the `dx_transcripts` package importable when this
# --- module is run as a standalone script (parents[1] == .deepx/tools/src).
import sys as _sys
from pathlib import Path as _Path
_SRC = str(_Path(__file__).resolve().parents[1])
if _SRC not in _sys.path:
    _sys.path.insert(0, _SRC)

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from dx_transcripts.session_common import (
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


OPENCODE_DB_PATH = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
_PROJECT_DB_RELATIVE_PATH = Path(".opencode") / "opencode.db"

logger = logging.getLogger(__name__)


@dataclass
class SessionMetadata:
    session_id: str = ""
    scenario_key: str = ""
    total_tokens: int = 0
    total_cost: float = 0.0
    step_count: int = 0
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    title: str = ""
    start_time: str = ""
    end_time: str = ""
    source_format: str = "stream"


@dataclass
class ConversationTurn:
    role: str = ""  # "user" | "assistant" | "tool"
    content: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    timestamp_ms: int = 0

    @property
    def assistant_content(self) -> str:
        return self.content if self.role == "assistant" else ""

    @property
    def user_content(self) -> str:
        return self.content if self.role == "user" else ""


@dataclass
class ParsedSession:
    metadata: SessionMetadata = field(default_factory=SessionMetadata)
    turns: List[ConversationTurn] = field(default_factory=list)


def count_user_turns(parsed: ParsedSession) -> int:
    """Return the number of non-empty user turns in the session.

    Used by lib/cost.py:compute_estimated_pr() as the primary signal for
    Premium Request estimation via ``user_turn_count × multiplier``.  Empty
    or whitespace-only user content (system pings, automated prompts) does
    not count as a user-driven turn.
    """
    return sum(1 for t in parsed.turns if t.user_content.strip())


def _parse_iso_to_ms(timestamp: Optional[str]) -> Optional[int]:
    if not timestamp:
        return None
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)
    except (ValueError, TypeError):
        return None


def _db_has_table(conn: sqlite3.Connection, name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (name,),
    ).fetchone()
    return row is not None


def _coerce_json(value: Any, fallback: Any) -> Any:
    if value is None:
        return fallback
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return fallback
    return fallback


def _json_dump(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return value
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    return json.dumps(value, indent=2, ensure_ascii=False)


def _tool_output_to_text(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2, ensure_ascii=False)


def _tool_status_to_success(status: Any) -> Optional[bool]:
    if status in (True, False):
        return bool(status)
    if not status:
        return None
    status_str = str(status).lower()
    if status_str in {"completed", "success", "succeeded", "ok"}:
        return True
    if status_str in {"failed", "error", "cancelled", "canceled"}:
        return False
    return None


def _part_timestamp_ms(part: Dict[str, Any], fallback_ms: int = 0) -> int:
    data = part.get("data", {}) if isinstance(part.get("data"), dict) else {}

    for candidate in (
        part.get("created_at"),
        part.get("time_created"),
        part.get("timestamp"),
        data.get("created_at"),
        data.get("time_created"),
        data.get("finished_at"),
    ):
        if isinstance(candidate, (int, float)):
            return int(candidate)

    for time_obj in (part.get("time"), data.get("time")):
        if isinstance(time_obj, dict):
            for key in ("start", "end", "created", "finished"):
                candidate = time_obj.get(key)
                if isinstance(candidate, (int, float)):
                    return int(candidate)

    return int(fallback_ms or 0)


def _append_text_turn(
    turns: List[ConversationTurn],
    role: str,
    text_chunks: List[str],
    timestamp_ms: int,
) -> None:
    content = "\n".join(chunk for chunk in text_chunks if chunk).strip()
    if not content:
        return
    turns.append(ConversationTurn(role=role, content=content, timestamp_ms=timestamp_ms))


def _append_tool_turn(turns: List[ConversationTurn], tool_call: ToolCall, timestamp_ms: int) -> None:
    turns.append(ConversationTurn(role="tool", tool_calls=[tool_call], timestamp_ms=timestamp_ms))


def _consume_parts(
    session: ParsedSession,
    *,
    role: str,
    parts: Iterable[Dict[str, Any]],
    fallback_ts: int,
    accumulate_usage: bool,
) -> None:
    text_chunks: List[str] = []
    text_ts = int(fallback_ts or 0)
    pending_calls: Dict[str, ToolCall] = {}

    def flush_text() -> None:
        nonlocal text_chunks, text_ts
        if text_chunks:
            _append_text_turn(session.turns, role, text_chunks, text_ts)
            text_chunks = []
            text_ts = int(fallback_ts or 0)

    for raw_part in parts:
        if not isinstance(raw_part, dict):
            continue
        ptype = raw_part.get("type", "")
        ptype_norm = str(ptype).replace("-", "_")
        data = raw_part.get("data") if isinstance(raw_part.get("data"), dict) else raw_part
        part_ts = _part_timestamp_ms(raw_part, fallback_ts)

        if ptype_norm == "text":
            text = data.get("text") or raw_part.get("text") or ""
            if text:
                if not text_chunks:
                    text_ts = part_ts or int(fallback_ts or 0)
                text_chunks.append(str(text))
            continue

        if ptype_norm in {"reasoning", "thinking"}:
            flush_text()
            thinking = data.get("thinking") or data.get("text") or raw_part.get("thinking") or raw_part.get("text") or ""
            if thinking:
                _append_tool_turn(
                    session.turns,
                    ToolCall(
                        tool_call_id=f"thinking-{len(session.turns)}-{part_ts}",
                        tool_name="🧠 thinking",
                        success=True,
                        result_content=str(thinking),
                    ),
                    part_ts,
                )
            continue

        if ptype_norm in {"tool_call", "tool_use"}:
            flush_text()
            call_id = str(data.get("id") or data.get("tool_call_id") or raw_part.get("id") or f"tool-{len(pending_calls)}")
            pending_calls[call_id] = ToolCall(
                tool_call_id=call_id,
                tool_name=str(data.get("name") or data.get("tool") or "unknown"),
                arguments=_json_dump(data.get("input", "")),
                success=True if data.get("finished") is True else None,
            )
            continue

        if ptype_norm == "tool_result":
            flush_text()
            call_id = str(data.get("tool_call_id") or data.get("id") or "")
            tool_call = pending_calls.pop(call_id, ToolCall(tool_call_id=call_id))
            if not tool_call.tool_name:
                tool_call.tool_name = str(data.get("name") or "unknown")
            tool_call.result_content = _tool_output_to_text(data.get("content") or data.get("result") or data.get("output") or "")
            tool_call.success = not bool(data.get("is_error"))
            _append_tool_turn(session.turns, tool_call, part_ts)
            continue

        if ptype_norm in {"tool", "tool_use"}:
            flush_text()
            state = data.get("state") if isinstance(data.get("state"), dict) else raw_part.get("state", {})
            tool_call = ToolCall(
                tool_call_id=str(data.get("callID") or data.get("call_id") or data.get("id") or raw_part.get("callID") or ""),
                tool_name=str(data.get("tool") or data.get("name") or raw_part.get("tool") or raw_part.get("name") or "unknown"),
                arguments=_json_dump(state.get("input", "")),
                result_content=_tool_output_to_text(state.get("output", "")),
                success=_tool_status_to_success(state.get("status")),
            )
            _append_tool_turn(session.turns, tool_call, part_ts)
            continue

        if ptype_norm == "step_start":
            session.metadata.step_count += 1
            continue

        if ptype_norm == "step_finish":
            if accumulate_usage:
                tokens = data.get("tokens", {}) if isinstance(data.get("tokens"), dict) else {}
                prompt = int(tokens.get("input", 0) or 0)
                completion = int(tokens.get("output", 0) or 0)
                session.metadata.prompt_tokens += prompt
                session.metadata.completion_tokens += completion
                session.metadata.total_tokens = (
                    session.metadata.prompt_tokens + session.metadata.completion_tokens
                )
                session.metadata.total_cost += float(data.get("cost", 0) or 0.0)
            continue

    flush_text()
    for tool_call in pending_calls.values():
        _append_tool_turn(session.turns, tool_call, fallback_ts)


def parse_opencode_jsonl(jsonl_path: Path) -> ParsedSession:
    """Parse OpenCode NDJSON file into a structured session."""
    session = ParsedSession()
    session.metadata.source_format = "stream"
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
        ts = int(event.get("timestamp", 0) or 0)

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
            if current_texts:
                _append_text_turn(session.turns, "assistant", current_texts, current_ts)
                current_texts = []
                current_ts = 0

            state = part.get("state", {})
            tc = ToolCall(
                tool_name=str(part.get("tool", "unknown")),
                arguments=_json_dump(state.get("input", {})),
                result_content=_tool_output_to_text(state.get("output", "")),
                success=(state.get("status", "") == "completed"),
            )
            _append_tool_turn(session.turns, tc, ts)

        elif etype == "step_start":
            session.metadata.step_count += 1

        elif etype == "step_finish":
            tokens = part.get("tokens", {}) if isinstance(part.get("tokens"), dict) else {}
            prompt = int(tokens.get("input", 0) or 0)
            completion = int(tokens.get("output", 0) or 0)
            session.metadata.prompt_tokens += prompt
            session.metadata.completion_tokens += completion
            session.metadata.total_tokens = (
                session.metadata.prompt_tokens + session.metadata.completion_tokens
            )
            session.metadata.total_cost += float(part.get("cost", 0) or 0.0)

    if current_texts:
        _append_text_turn(session.turns, "assistant", current_texts, current_ts)

    return session


def _find_opencode_session_in_db(
    db_path: Path,
    after_utc: Optional[str],
    before_utc: Optional[str],
) -> Optional[str]:
    """Find the most recent OpenCode session in a UTC time window."""
    if not db_path.exists():
        return None

    after_ms = _parse_iso_to_ms(after_utc)
    before_ms = _parse_iso_to_ms(before_utc)

    _VALID_TABLES = {"sessions": "updated_at", "session": "time_updated"}

    with sqlite3.connect(db_path) as conn:
        table: Optional[str] = None
        updated_col: Optional[str] = None
        for t, col in _VALID_TABLES.items():
            if _db_has_table(conn, t):
                table, updated_col = t, col
                break
        if table is None or updated_col is None:
            return None

        clauses: List[str] = []
        params: List[int] = []
        if after_ms is not None:
            clauses.append(f"{updated_col} >= ?")
            params.append(after_ms)
        if before_ms is not None:
            clauses.append(f"{updated_col} <= ?")
            params.append(before_ms)

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        row = conn.execute(
            f"SELECT id FROM {table} {where_sql} ORDER BY {updated_col} DESC LIMIT 1",
            params,
        ).fetchone()
        return str(row[0]) if row else None


def _parse_plural_schema_db(conn: sqlite3.Connection, session_id: str) -> ParsedSession:
    session = ParsedSession()
    session.metadata.source_format = "db"

    row = conn.execute(
        "SELECT id, title, prompt_tokens, completion_tokens, cost, created_at, updated_at FROM sessions WHERE id = ?",
        (session_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"OpenCode session not found: {session_id}")

    (
        session.metadata.session_id,
        session.metadata.title,
        prompt_tokens,
        completion_tokens,
        session.metadata.total_cost,
        created_at,
        updated_at,
    ) = row
    session.metadata.prompt_tokens = int(prompt_tokens or 0)
    session.metadata.completion_tokens = int(completion_tokens or 0)
    session.metadata.total_tokens = session.metadata.prompt_tokens + session.metadata.completion_tokens
    session.metadata.start_time = ts_from_ms(int(created_at or 0))
    session.metadata.end_time = ts_from_ms(int(updated_at or 0))

    msg_rows = conn.execute(
        "SELECT id, role, parts, model, created_at, updated_at, finished_at FROM messages WHERE session_id = ? ORDER BY created_at",
        (session_id,),
    ).fetchall()

    for _, role, parts_json, model, created_at, _updated_at, _finished_at in msg_rows:
        if model and not session.metadata.model:
            session.metadata.model = str(model)
        parts = _coerce_json(parts_json, [])
        _consume_parts(
            session,
            role=str(role or "assistant"),
            parts=parts,
            fallback_ts=int(created_at or 0),
            accumulate_usage=False,
        )

    return session


def _parse_singular_schema_db(conn: sqlite3.Connection, session_id: str) -> ParsedSession:
    session = ParsedSession()
    session.metadata.source_format = "db"

    row = conn.execute(
        "SELECT id, title, time_created, time_updated FROM session WHERE id = ?",
        (session_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"OpenCode session not found: {session_id}")

    (
        session.metadata.session_id,
        session.metadata.title,
        created_at,
        updated_at,
    ) = row
    session.metadata.start_time = ts_from_ms(int(created_at or 0))
    session.metadata.end_time = ts_from_ms(int(updated_at or 0))

    message_rows = conn.execute(
        "SELECT id, time_created, data FROM message WHERE session_id = ? ORDER BY time_created",
        (session_id,),
    ).fetchall()
    part_rows = conn.execute(
        "SELECT message_id, time_created, data FROM part WHERE session_id = ? ORDER BY time_created",
        (session_id,),
    ).fetchall()

    parts_by_message: Dict[str, List[Dict[str, Any]]] = {}
    for message_id, part_created_at, data_json in part_rows:
        part = _coerce_json(data_json, {})
        if isinstance(part, dict):
            part.setdefault("time_created", int(part_created_at or 0))
            parts_by_message.setdefault(str(message_id), []).append(part)

    for message_id, message_created_at, data_json in message_rows:
        msg = _coerce_json(data_json, {})
        role = str(msg.get("role", "assistant"))
        model_info = msg.get("model", {}) if isinstance(msg.get("model"), dict) else {}
        if not session.metadata.model:
            model = model_info.get("modelID") or msg.get("model") or ""
            if model:
                session.metadata.model = str(model)
        _consume_parts(
            session,
            role=role,
            parts=parts_by_message.get(str(message_id), []),
            fallback_ts=int(message_created_at or 0),
            accumulate_usage=True,
        )

    return session


def parse_opencode_db(db_path: Path, session_id: str) -> ParsedSession:
    """Parse an OpenCode SQLite DB session into structured turns."""
    db_path = Path(db_path).expanduser()
    if not db_path.exists():
        raise FileNotFoundError(db_path)

    with sqlite3.connect(db_path) as conn:
        if _db_has_table(conn, "sessions") and _db_has_table(conn, "messages"):
            return _parse_plural_schema_db(conn, session_id)
        if _db_has_table(conn, "session") and _db_has_table(conn, "message") and _db_has_table(conn, "part"):
            return _parse_singular_schema_db(conn, session_id)
        raise ValueError(f"Unsupported OpenCode DB schema: {db_path}")


def parse_opencode_session(
    jsonl_path: Path,
    *,
    session_id: str = "",
    db_path: Optional[Path] = None,
    workdir: Optional[Path] = None,
    after_utc: Optional[str] = None,
    before_utc: Optional[str] = None,
) -> ParsedSession:
    """Parse OpenCode session data, preferring SQLite DB data over stream JSONL."""
    jsonl_path = Path(jsonl_path)
    candidate_dbs: List[Path] = []

    if db_path is not None:
        candidate_dbs.append(Path(db_path).expanduser())
    if workdir is not None:
        candidate_dbs.append(Path(workdir) / _PROJECT_DB_RELATIVE_PATH)
    candidate_dbs.append(jsonl_path.parent / _PROJECT_DB_RELATIVE_PATH)
    candidate_dbs.append(OPENCODE_DB_PATH)

    seen: set[str] = set()
    for candidate in candidate_dbs:
        candidate = candidate.expanduser()
        key = str(candidate)
        if key in seen or not candidate.exists():
            continue
        seen.add(key)
        db_session_id = session_id or _find_opencode_session_in_db(candidate, after_utc, before_utc)
        if not db_session_id:
            continue
        try:
            return parse_opencode_db(candidate, db_session_id)
        except (ValueError, KeyError) as exc:
            logger.debug("OpenCode DB parse failed for %s/%s: %s", candidate, db_session_id, exc)
            continue
        except sqlite3.DatabaseError as exc:
            logger.warning("OpenCode DB error for %s: %s", candidate, exc)
            continue

    if jsonl_path.exists():
        return parse_opencode_jsonl(jsonl_path)

    raise FileNotFoundError(f"No OpenCode session source found for {jsonl_path}")


def _render_turn_html(turn: ConversationTurn, index: int) -> str:
    """Render a single conversation turn to HTML using .entry CSS classes from session_common."""
    parts: List[str] = []

    ts_str = ts_from_ms(turn.timestamp_ms) if turn.timestamp_ms else ""
    ts_html = f'<span class="time">{ts_str}</span>' if ts_str else ""

    if turn.role == "user":
        body = md_to_html_simple(html_escape(turn.content))
        parts.append(
            f'<div class="entry user" id="entry-{index}">'
            f'<div class="entry-hdr">'
            f'<span class="icon">&#x1F464;</span>'
            f'<span class="label">User</span>'
            f'{ts_html}'
            f'</div>'
            f'<div class="entry-body">{body}</div>'
            f'</div>'
        )

    elif turn.role == "assistant":
        body = md_to_html_simple(html_escape(turn.content))
        parts.append(
            f'<div class="entry assistant" id="entry-{index}">'
            f'<div class="entry-hdr">'
            f'<span class="icon">&#x1F4AC;</span>'
            f'<span class="label">Assistant</span>'
            f'{ts_html}'
            f'</div>'
            f'<div class="entry-body">{body}</div>'
            f'</div>'
        )

    elif turn.role == "tool":
        for tc in turn.tool_calls:
            success = True if tc.success is None else bool(tc.success)
            status_cls = "tool-ok" if success else "tool-fail"
            status_icon = "&#x2705;" if success else "&#x274C;"
            args_html = ""
            if tc.arguments and tc.arguments != "{}":
                args_html = f'<div class="tool-args"><code>{html_escape(truncate(tc.arguments, 3000))}</code></div>'
            result_html = ""
            if tc.result_content:
                result_html = f'<div class="tool-result"><pre>{html_escape(truncate(tc.result_content, 3000))}</pre></div>'
            parts.append(
                f'<div class="entry {status_cls} collapsed" id="entry-{index}">'
                f'<div class="entry-hdr">'
                f'<span class="icon">{status_icon}</span>'
                f'<span class="label">{html_escape(tc.tool_name)}</span>'
                f'<span class="time">click to expand</span>'
                f'</div>'
                f'<div class="entry-body">{args_html}{result_html}</div>'
                f'</div>'
            )

    return "\n".join(parts)


def _thinking_summary_items(
    thinking_mode: str,
    thinking_args: Optional[Dict[str, str]],
    intended_model: str,
) -> List[str]:
    """Summary <li> items describing runner-supplied thinking metadata."""
    out: List[str] = []
    if thinking_mode:
        label = (
            "ON (TH — extended thinking / high reasoning effort)" if thinking_mode == "TH"
            else "OFF (NT — default reasoning)" if thinking_mode == "NT"
            else thinking_mode
        )
        out.append(f"<li><strong>확장사고 (Thinking):</strong> {html_escape(label)}</li>")
    if thinking_args:
        for k, v in thinking_args.items():
            out.append(
                f"<li><strong>Reasoning Arg:</strong> <code>{html_escape(k)}={html_escape(v)}</code></li>"
            )
    if intended_model:
        out.append(
            f"<li><strong>Intended Model (runner-set):</strong> <code>{html_escape(intended_model)}</code></li>"
        )
    return out


def _build_html(
    session: ParsedSession,
    scenario_key: str = "",
    *,
    thinking_mode: str = "",
    thinking_args: Optional[Dict[str, str]] = None,
    intended_model: str = "",
) -> str:
    """Build self-contained HTML document from parsed session.

    ``thinking_*`` kwargs append runner-supplied metadata to the summary box
    when provided.
    """
    meta = session.metadata
    title = scenario_key or meta.title or meta.session_id or "OpenCode Session"

    turns_html = "\n".join(
        _render_turn_html(t, i) for i, t in enumerate(session.turns)
    )

    output_dirs = extract_output_dirs_from_turns(session.turns)
    has_start = has_start_sentinel_in_turns(session.turns)

    summary_items = [
        f"<li><strong>Session ID:</strong> {html_escape(meta.session_id)}</li>",
        f"<li><strong>Title:</strong> {html_escape(meta.title)}</li>" if meta.title else "",
        f"<li><strong>Scenario:</strong> {html_escape(scenario_key)}</li>" if scenario_key else "",
        f"<li><strong>Source format:</strong> {html_escape(meta.source_format)}</li>",
        f"<li><strong>Model:</strong> {html_escape(meta.model)}</li>" if meta.model else "",
        f"<li><strong>Start:</strong> {html_escape(meta.start_time)}</li>" if meta.start_time else "",
        f"<li><strong>End:</strong> {html_escape(meta.end_time)}</li>" if meta.end_time else "",
        f"<li><strong>Steps:</strong> {meta.step_count}</li>",
        f"<li><strong>Prompt tokens:</strong> {meta.prompt_tokens:,}</li>",
        f"<li><strong>Completion tokens:</strong> {meta.completion_tokens:,}</li>",
        f"<li><strong>Total tokens:</strong> {meta.total_tokens:,}</li>",
        f"<li><strong>Total cost:</strong> ${meta.total_cost:,.4f}</li>",
        f"<li><strong>Turns:</strong> {len(session.turns)}</li>",
        f"<li><strong>Tool calls:</strong> {sum(len(t.tool_calls) for t in session.turns)}</li>",
        f"<li><strong>START sentinel:</strong> {'✅' if has_start else '❌'}</li>",
        f"<li><strong>Output dirs:</strong> {', '.join(output_dirs) if output_dirs else 'none detected'}</li>",
    ]
    summary_items.extend(_thinking_summary_items(thinking_mode, thinking_args, intended_model))
    summary_html = "\n".join(s for s in summary_items if s)

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<title>{html_escape(title)}</title>
<style>
{HTML_CSS}
.summary-box {{ background: var(--code-bg); border: 1px solid var(--border); border-radius: 6px;
              padding: 16px; margin-bottom: 20px; }}
.summary-box ul {{ list-style: none; padding: 0; margin: 0; }}
.summary-box li {{ padding: 3px 0; }}
</style>
</head>
<body>
<div class=\"container\">
  <h1>🟢 OpenCode Session — {html_escape(title)}</h1>
  <div class=\"summary-box\">
    <h3>Session Summary</h3>
    <ul>
      {summary_html}
    </ul>
  </div>
  <div class=\"conversation\">
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
    *,
    db_path: Optional[Path] = None,
    workdir: Optional[Path] = None,
    after_utc: Optional[str] = None,
    before_utc: Optional[str] = None,
    thinking_mode: str = "",
    thinking_args: Optional[Dict[str, str]] = None,
    intended_model: str = "",
) -> Optional[str]:
    """Render OpenCode session data to self-contained HTML.

    Runner metadata (``thinking_*``) is forwarded to ``_build_html`` so the
    summary box reflects whether ``--thinking`` was applied.
    """
    try:
        session = parse_opencode_session(
            jsonl_path,
            session_id=session_id_override,
            db_path=db_path,
            workdir=workdir,
            after_utc=after_utc,
            before_utc=before_utc,
        )

        if session_id_override:
            session.metadata.session_id = session_id_override
        if scenario_key:
            session.metadata.scenario_key = scenario_key

        html = _build_html(
            session,
            scenario_key=scenario_key,
            thinking_mode=thinking_mode,
            thinking_args=thinking_args,
            intended_model=intended_model,
        )
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
