"""Session-level data: parse stream.jsonl + session.md, extract model/duration/sentinels."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

SENTINEL_START = "[DX-AGENT-DEV: START]"
SENTINEL_DONE_RE = re.compile(r"\[DX-AGENT-DEV:\s*DONE(?:\s*\(output-dir:\s*([^)]*)\))?\]")
SESSION_ID_RE = re.compile(
    r"^(\d{8})-(\d{6})_(claude|copilot|cursor|opencode|codex)_([a-zA-Z0-9_]+)$"
)


@dataclass
class SessionData:
    """Parsed transcript-level info for one scenario session."""
    has_start_sentinel: bool = False
    has_done_sentinel: bool = False
    done_output_dirs: List[str] = field(default_factory=list)
    model: Optional[str] = None
    duration_sec: Optional[float] = None
    # Token counts — per-tool extraction (see _parse_*_stream functions)
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cache_read_tokens: int = 0
    total_cache_write_tokens: int = 0
    total_reasoning_tokens: int = 0
    # Cost / billing
    premium_requests: int = 0           # Copilot CLI: data.modelMetrics.<model>.requests.count
    cost_units: float = 0.0             # Tool-specific cost (Copilot: requests.cost; OpenCode: part.cost sum)
    # User turn count — informational metadata (not used for PR estimation;
    # agent-driven loops accumulate PR per LLM round-trip, not per user turn)
    user_turn_count: int = 0
    # Tool call count (sum of distinct tool invocations)
    tool_call_count: int = 0
    transcript_length: int = 0          # transcript .md file size in bytes
    errors_detected: List[str] = field(default_factory=list)
    # Environment-failure signature (PR2): "cert" | "model-refresh-timeout" | "".
    # Scanned from rendered transcript (claude SSL wording) AND stream.jsonl
    # (cursor/opencode "first certificate", codex model-refresh). See
    # lib/env_failure.py for the shared catalogue used by analyzer + runner.
    env_failure_signature: str = ""


def _parse_jsonl(path: Path):
    """Yield parsed JSON objects from a JSONL file, ignoring malformed lines."""
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except Exception:
        return


def _parse_claude_code_stream(stream: Path, sd: SessionData) -> None:
    """Claude Code stream-json: extract model, duration, tokens, tool calls."""
    first_ts = None
    last_ts = None
    for ev in _parse_jsonl(stream):
        ev_type = ev.get("type")
        if ev_type == "system" and ev.get("subtype") == "init":
            if not sd.model:
                sd.model = ev.get("model")
        elif ev_type == "user":
            # Phase C: count user turns from stream. claude-code emits both
            # "real" user prompts AND tool_result-wrapped-as-user events; only
            # the former (non-empty text content) is a user-driven turn.
            msg = ev.get("message", {}) or {}
            content = msg.get("content", "")
            has_user_text = False
            if isinstance(content, str) and content.strip():
                has_user_text = True
            elif isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text" and (c.get("text") or "").strip():
                        has_user_text = True
                        break
            if has_user_text:
                sd.user_turn_count += 1
        elif ev_type == "assistant":
            msg = ev.get("message", {}) or {}
            usage = msg.get("usage", {}) or {}
            sd.total_input_tokens += int(usage.get("input_tokens", 0) or 0)
            sd.total_output_tokens += int(usage.get("output_tokens", 0) or 0)
            sd.total_cache_read_tokens += int(usage.get("cache_read_input_tokens", 0) or 0)
            sd.total_cache_write_tokens += int(usage.get("cache_creation_input_tokens", 0) or 0)
            for content in msg.get("content", []) or []:
                if isinstance(content, dict) and content.get("type") == "tool_use":
                    sd.tool_call_count += 1
        elif ev_type == "result":
            duration = ev.get("duration_ms")
            if duration is not None:
                try:
                    sd.duration_sec = float(duration) / 1000.0
                except Exception:
                    pass
        # Track first/last timestamps as a fallback for duration
        for tk in ("timestamp", "created_at"):
            if tk in ev:
                ts = ev[tk]
                if first_ts is None:
                    first_ts = ts
                last_ts = ts
    # Duration fallback from timestamps if not set by result event
    if sd.duration_sec is None and first_ts and last_ts:
        try:
            t1 = datetime.fromisoformat(str(first_ts).replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(str(last_ts).replace("Z", "+00:00"))
            sd.duration_sec = (t2 - t1).total_seconds()
        except Exception:
            pass


def _ts_to_seconds(ts) -> Optional[float]:
    """Convert a timestamp value (str ISO / int Unix ms / int Unix s) to epoch seconds."""
    if ts is None:
        return None
    # Numeric: heuristic — ms if > 10^12, else seconds
    if isinstance(ts, (int, float)):
        v = float(ts)
        return v / 1000.0 if v > 1e12 else v
    if isinstance(ts, str):
        # Try ISO first
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
        except Exception:
            pass
        # Numeric string
        try:
            v = float(ts)
            return v / 1000.0 if v > 1e12 else v
        except Exception:
            return None
    return None


def _parse_copilot_events(stream: Path, sd: SessionData) -> None:
    """Copilot CLI events-*.jsonl: extract token usage and premium request count.

    Format: `session.shutdown` event has cumulative `data.modelMetrics.<model>`
    containing `requests.{count,cost}` + `usage.{input,output,cacheRead,cacheWrite,reasoning}Tokens`.

    ⚠ IMPORTANT: Copilot's `inputTokens` is the **TOTAL** input (NEW + cache_read + cache_write),
    NOT NEW-only as Anthropic's convention. We MUST subtract cacheRead + cacheWrite to get
    the true NEW (non-cached) input — comparable to claude-code / cursor / opencode.

    Example (one compiler session):
      inputTokens=6,458,020  cacheReadTokens=6,332,847  cacheWriteTokens=125,084
      → NEW input = 6,458,020 - 6,332,847 - 125,084 ≈ 89   (vs raw 6.4M)
    """
    first_ts_seen = None
    last_ts_seen = None
    counted_tool_ids = set()
    raw_input_total = 0      # Copilot's raw inputTokens (cumulative, includes cache)
    raw_cache_read = 0
    raw_cache_write = 0
    for ev in _parse_jsonl(stream):
        ev_type = str(ev.get("type") or "").lower()
        # Cumulative token usage in session.shutdown
        data = ev.get("data", {}) or {}
        mm = data.get("modelMetrics") or {}
        for model_name, mdata in mm.items():
            if not sd.model:
                sd.model = model_name
            usage = (mdata or {}).get("usage", {}) or {}
            reqs = (mdata or {}).get("requests", {}) or {}
            # Track raw cumulative values
            raw_input_total = int(usage.get("inputTokens", raw_input_total) or 0)
            raw_cache_read = int(usage.get("cacheReadTokens", raw_cache_read) or 0)
            raw_cache_write = int(usage.get("cacheWriteTokens", raw_cache_write) or 0)
            sd.total_output_tokens = int(usage.get("outputTokens", sd.total_output_tokens) or 0)
            sd.total_reasoning_tokens = int(usage.get("reasoningTokens", sd.total_reasoning_tokens) or 0)
            sd.premium_requests = int(reqs.get("count", sd.premium_requests) or 0)
            try:
                sd.cost_units = float(reqs.get("cost", sd.cost_units) or 0.0)
            except Exception:
                pass

        # Tool call counting — count once per unique tool.execution_complete
        if ev_type.endswith("execution_complete") or ev_type.endswith("execution_completed"):
            tid = ev.get("id") or ev.get("data", {}).get("id") if isinstance(ev.get("data"), dict) else None
            if tid and tid not in counted_tool_ids:
                counted_tool_ids.add(tid)
                sd.tool_call_count += 1
            elif not tid:
                sd.tool_call_count += 1

        # Timestamp tracking
        for tk in ("timestamp", "timestamp_ms"):
            if tk in ev:
                conv = _ts_to_seconds(ev[tk])
                if conv is not None:
                    if first_ts_seen is None or conv < first_ts_seen:
                        first_ts_seen = conv
                    if last_ts_seen is None or conv > last_ts_seen:
                        last_ts_seen = conv
                break
    # Normalize Copilot's TOTAL inputTokens → NEW input only (Anthropic-style),
    # to match claude-code/cursor/opencode token semantics.
    sd.total_cache_read_tokens = raw_cache_read
    sd.total_cache_write_tokens = raw_cache_write
    new_input = raw_input_total - raw_cache_read - raw_cache_write
    sd.total_input_tokens = max(0, new_input)   # negative is impossible — clip to 0

    if sd.duration_sec is None and first_ts_seen and last_ts_seen:
        sd.duration_sec = max(0.0, last_ts_seen - first_ts_seen)


def _parse_opencode_stream(stream: Path, sd: SessionData) -> None:
    """OpenCode stream.jsonl: tokens are PER-STEP (incremental); must be SUMMED.

    Format: each `step_finish` or `text` event with `.part.tokens.*` + `.part.cost`.
    Tokens are NOT cumulative — each step records its own input/output for that step.
    """
    first_ts_seen = None
    last_ts_seen = None
    for ev in _parse_jsonl(stream):
        ev_type = str(ev.get("type") or "").lower()
        if not sd.model:
            # OpenCode model name often in part data
            mdl = ev.get("part", {}).get("model") if isinstance(ev.get("part"), dict) else None
            if mdl:
                sd.model = str(mdl)

        # Sum per-step tokens
        part = ev.get("part") if isinstance(ev.get("part"), dict) else {}
        tokens = part.get("tokens") if isinstance(part, dict) else None
        if isinstance(tokens, dict):
            sd.total_input_tokens += int(tokens.get("input", 0) or 0)
            sd.total_output_tokens += int(tokens.get("output", 0) or 0)
            sd.total_reasoning_tokens += int(tokens.get("reasoning", 0) or 0)
            cache = tokens.get("cache", {}) if isinstance(tokens.get("cache"), dict) else {}
            sd.total_cache_read_tokens += int(cache.get("read", 0) or 0)
            sd.total_cache_write_tokens += int(cache.get("write", 0) or 0)
        # Cost — sum incremental
        if isinstance(part, dict) and "cost" in part:
            try:
                sd.cost_units += float(part.get("cost", 0) or 0)
            except Exception:
                pass

        # Tool calls
        if ev_type in ("tool_use", "tool_call"):
            sd.tool_call_count += 1

        # Timestamp tracking
        for tk in ("timestamp", "timestamp_ms"):
            if tk in ev:
                conv = _ts_to_seconds(ev[tk])
                if conv is not None:
                    if first_ts_seen is None or conv < first_ts_seen:
                        first_ts_seen = conv
                    if last_ts_seen is None or conv > last_ts_seen:
                        last_ts_seen = conv
                break

    if sd.duration_sec is None and first_ts_seen and last_ts_seen:
        sd.duration_sec = max(0.0, last_ts_seen - first_ts_seen)

    # OpenCode autopilot: 1 user turn (initial prompt). Stream doesn't expose
    # user messages — only agent steps. Default to 1 for autopilot sessions
    # (matches the e2e harness invariant: one prompt sent per scenario).
    # Phase C note: claude-code / cursor / codex stream parsers now increment
    # user_turn_count from explicit user events. opencode and the generic
    # fallback path still rely on this default. copilot does NOT use this
    # function (see _parse_generic_stream which it falls into) — its
    # user_turn_count is also defaulted to 1 by the same fallback in any
    # path that reaches here with count == 0.
    if sd.user_turn_count == 0:
        sd.user_turn_count = 1


def _parse_cursor_stream(stream: Path, sd: SessionData) -> None:
    """Cursor stream.jsonl: tokens in 'result' event (cumulative) OR sum from assistant events."""
    first_ts_seen = None
    last_ts_seen = None
    session_result_duration_ms = None
    counted_tool_ids = set()
    cumulative_from_result = False

    for ev in _parse_jsonl(stream):
        ev_type = str(ev.get("type") or "").lower()
        ev_subtype = str(ev.get("subtype") or "").lower()

        if not sd.model:
            for k in ("model", "model_id"):
                if k in ev and ev[k]:
                    sd.model = str(ev[k])
                    break

        # Phase C: count user turns. Cursor stream emits a single ``type=user``
        # event per autopilot session (the initial prompt); follow-up tool
        # results travel under different types. text-content empty checks
        # are still applied to guard against future shape changes.
        if ev_type == "user":
            msg = ev.get("message", {}) or {}
            content = msg.get("content", "")
            has_user_text = False
            if isinstance(content, str) and content.strip():
                has_user_text = True
            elif isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text" and (c.get("text") or "").strip():
                        has_user_text = True
                        break
            if has_user_text:
                sd.user_turn_count += 1

        # Cursor 'result' event has cumulative usage + total duration
        if ev_type == "result":
            usage = ev.get("usage", {}) or {}
            if usage:
                sd.total_input_tokens = int(usage.get("inputTokens", 0) or 0)
                sd.total_output_tokens = int(usage.get("outputTokens", 0) or 0)
                sd.total_cache_read_tokens = int(usage.get("cacheReadTokens", 0) or 0)
                sd.total_cache_write_tokens = int(usage.get("cacheWriteTokens", 0) or 0)
                cumulative_from_result = True
            if isinstance(ev.get("duration_ms"), (int, float)):
                session_result_duration_ms = float(ev["duration_ms"])

        # If no result event, sum per-event usage as fallback
        if not cumulative_from_result and isinstance(ev.get("usage"), dict):
            u = ev["usage"]
            sd.total_input_tokens += int(u.get("inputTokens", 0) or 0)
            sd.total_output_tokens += int(u.get("outputTokens", 0) or 0)
            sd.total_cache_read_tokens += int(u.get("cacheReadTokens", 0) or 0)
            sd.total_cache_write_tokens += int(u.get("cacheWriteTokens", 0) or 0)

        # Tool call counting — count tool_call/completed events
        if ev_type == "tool_call" and ev_subtype == "completed":
            tid = ev.get("call_id")
            if tid and tid not in counted_tool_ids:
                counted_tool_ids.add(tid)
                sd.tool_call_count += 1

        # Timestamps
        for tk in ("timestamp_ms", "timestamp"):
            if tk in ev:
                conv = _ts_to_seconds(ev[tk])
                if conv is not None:
                    if first_ts_seen is None or conv < first_ts_seen:
                        first_ts_seen = conv
                    if last_ts_seen is None or conv > last_ts_seen:
                        last_ts_seen = conv
                break

    if session_result_duration_ms is not None:
        sd.duration_sec = session_result_duration_ms / 1000.0
    elif sd.duration_sec is None and first_ts_seen and last_ts_seen:
        sd.duration_sec = max(0.0, last_ts_seen - first_ts_seen)


def _parse_generic_stream(stream: Path, sd: SessionData) -> None:
    """Generic fallback for unknown formats."""
    first_ts_seen = None
    last_ts_seen = None
    session_result_duration_ms = None    # only set from a 'result' event
    counted_tool_event_ids = set()
    for ev in _parse_jsonl(stream):
        ev_type = str(ev.get("type") or ev.get("event") or "").lower()
        ev_subtype = str(ev.get("subtype") or "").lower()

        # Model detection (e.g., Cursor init event)
        if not sd.model:
            for k in ("model", "model_id", "model_name"):
                if k in ev and ev[k]:
                    sd.model = str(ev[k])
                    break

        # Session-total duration_ms — ONLY accept from 'result' event (not per-tool durations)
        if ev_type == "result" and isinstance(ev.get("duration_ms"), (int, float)):
            session_result_duration_ms = float(ev["duration_ms"])

        # Tool call counting — handle multiple formats:
        # 1) cursor: type=tool_call, subtype=started|completed
        # 2) copilot: type=tool.execution_start | tool.execution_complete
        # 3) opencode: type=tool_use
        is_tool_event = False
        is_completion = False
        if ev_type in ("tool_use", "tool_call", "tool_invocation"):
            is_tool_event = True
            is_completion = (ev_subtype == "completed")
        elif ev_type.startswith("tool."):
            is_tool_event = True
            # copilot: tool.execution_complete signals one completed call
            is_completion = ev_type.endswith("complete") or ev_type.endswith("completed")
        elif ev_type == "tool":
            is_tool_event = True
            is_completion = (ev_subtype == "completed")

        if is_tool_event:
            call_id = ev.get("call_id") or ev.get("id") or ev.get("uuid")
            if is_completion:
                # Count once per unique 'completion' event to avoid double-counting
                if call_id:
                    if call_id not in counted_tool_event_ids:
                        counted_tool_event_ids.add(call_id)
                        sd.tool_call_count += 1
                else:
                    sd.tool_call_count += 1
            elif not is_completion and not call_id:
                # Some formats only emit a single 'tool_use' (e.g., opencode) with no separate completion
                # In that case, count each tool_use as one call
                sd.tool_call_count += 1

        # Track timestamps — accept ISO, Unix ms (int/float), Unix s
        for tk in ("timestamp_ms", "timestamp", "time", "created_at", "ts"):
            if tk in ev:
                converted = _ts_to_seconds(ev[tk])
                if converted is not None:
                    if first_ts_seen is None or converted < first_ts_seen:
                        first_ts_seen = converted
                    if last_ts_seen is None or converted > last_ts_seen:
                        last_ts_seen = converted
                break  # one timestamp per event

    if session_result_duration_ms is not None:
        sd.duration_sec = session_result_duration_ms / 1000.0
    elif sd.duration_sec is None and first_ts_seen is not None and last_ts_seen is not None:
        sd.duration_sec = max(0.0, last_ts_seen - first_ts_seen)


def _scan_transcript_md(md: Path, sd: SessionData) -> None:
    """Parse session.md for sentinels and basic error patterns."""
    try:
        text = md.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return
    sd.transcript_length = len(text)
    if SENTINEL_START in text:
        sd.has_start_sentinel = True
    for m in SENTINEL_DONE_RE.finditer(text):
        sd.has_done_sentinel = True
        captured = m.group(1)
        if captured:
            # output-dir may be a single path OR multiple separated by " + "
            for p in captured.split("+"):
                p = p.strip()
                if p:
                    sd.done_output_dirs.append(p)
    # Cheap error sniff
    for needle in ["Error:", "Traceback", "FAIL"]:
        if needle in text:
            sd.errors_detected.append(needle)
            break  # one is enough for the flag


def _scan_transcript_html(html: Path, sd: SessionData) -> None:
    """Fallback: scan HTML transcript for sentinels when MD is unavailable or incomplete."""
    try:
        text = html.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return
    if not sd.transcript_length:
        sd.transcript_length = len(text)
    if not sd.has_start_sentinel and SENTINEL_START in text:
        sd.has_start_sentinel = True
    if not sd.has_done_sentinel:
        for m in SENTINEL_DONE_RE.finditer(text):
            sd.has_done_sentinel = True
            captured = m.group(1)
            if captured:
                for p in captured.split("+"):
                    p = p.strip()
                    if p:
                        sd.done_output_dirs.append(p)


def _parse_codex_stream(stream: Path, sd: SessionData,
                        persistent_jsonl: Optional[Path] = None) -> None:
    """Codex CLI exec JSONL: extract model, duration, tokens, tool calls.

    Format variants:
    - Exec format (*-session.jsonl): turn.completed has cumulative usage,
      item.completed has command_execution/file_change as tool calls.
      NO timestamps in exec format.
    - Persistent format (*-persistent.jsonl): response_item has function_call,
      event_msg has token_count, turn_context has model, all events have timestamps.

    Token fields (exec): input_tokens, cached_input_tokens, output_tokens, reasoning_output_tokens.
    ⚠ input_tokens is TOTAL (includes cached) — same semantics as Copilot's inputTokens.
    Fresh input = input_tokens − cached_input_tokens.
    """
    # --- Parse exec format for tokens and tool calls ---
    for ev in _parse_jsonl(stream):
        ev_type = str(ev.get("type") or "")

        if ev_type == "turn.completed":
            sd.user_turn_count += 1
            usage = ev.get("usage", {}) or {}
            if usage:
                raw_input = int(usage.get("input_tokens", 0) or 0)
                cached = int(usage.get("cached_input_tokens", 0) or 0)
                sd.total_input_tokens = max(0, raw_input - cached)  # fresh (non-cached)
                sd.total_output_tokens = int(usage.get("output_tokens", 0) or 0)
                sd.total_cache_read_tokens = cached
                sd.total_reasoning_tokens = int(usage.get("reasoning_output_tokens", 0) or 0)

        if ev_type == "item.completed":
            item = ev.get("item", {}) or {}
            item_type = item.get("type", "")
            if item_type in ("command_execution", "file_change"):
                sd.tool_call_count += 1

    # --- Parse persistent format for model and timestamps ---
    if persistent_jsonl and persistent_jsonl.is_file():
        first_ts = None
        last_ts = None
        for ev in _parse_jsonl(persistent_jsonl):
            ev_type = str(ev.get("type") or "")
            payload = ev.get("payload", {}) or {}

            ts_str = ev.get("timestamp")
            if ts_str:
                conv = _ts_to_seconds(ts_str)
                if conv is not None:
                    if first_ts is None or conv < first_ts:
                        first_ts = conv
                    if last_ts is None or conv > last_ts:
                        last_ts = conv

            if ev_type == "turn_context" and not sd.model:
                sd.model = payload.get("model")
            if ev_type == "session_meta" and not sd.model:
                sd.model = payload.get("model")

        if sd.duration_sec is None and first_ts is not None and last_ts is not None:
            sd.duration_sec = max(0.0, last_ts - first_ts)


def _duration_from_mtime(scenario_ref, sd: SessionData) -> None:
    """Strong fallback: use file mtimes across artifact + output dirs as session duration.

    More reliable than first/last stream event when the stream is truncated or
    missing timestamps. Walks artifact_path AND all output_dirs.
    """
    if sd.duration_sec is not None and sd.duration_sec > 1.0:
        return
    try:
        mtimes = []
        # Scan artifact dir
        art = scenario_ref.artifact_path
        if art and art.is_dir():
            for f in art.iterdir():
                if f.is_file():
                    mtimes.append(f.stat().st_mtime)
        # Scan all linked output dirs (one level only — speed)
        for od in scenario_ref.output_dirs:
            if not od.is_dir():
                continue
            for f in od.iterdir():
                if f.is_file():
                    mtimes.append(f.stat().st_mtime)
        if len(mtimes) >= 2:
            sd.duration_sec = max(mtimes) - min(mtimes)
    except Exception:
        pass


def _scan_env_failure_signature(scenario_ref, sd: SessionData) -> None:
    """Detect a cert/SSL or codex model-refresh env-failure signature.

    Scans BOTH the rendered transcript (claude's "SSL certificate verification
    failed" wording surfaces there) AND the raw stream.jsonl (cursor/opencode's
    node "unable to verify the first certificate" + opencode's UnknownError
    wrapper land there). Reads are capped to keep large transcripts cheap.

    For codex, ``sd.tool_call_count`` is passed as the command-count proxy so a
    model-refresh warning that nonetheless did real work (R5 compiler, 96
    commands) is NOT flagged — only model-refresh with 0 work is an env failure.
    """
    from . import env_failure as ef

    CAP = 400_000  # bytes per source — cert errors appear early/late, both ends matter
    chunks: List[str] = []
    for p in (getattr(scenario_ref, "transcript_md", None),
              getattr(scenario_ref, "transcript_html", None),
              getattr(scenario_ref, "stream_jsonl", None),
              getattr(scenario_ref, "secondary_jsonl", None)):
        if p and Path(p).is_file():
            try:
                chunks.append(Path(p).read_text(encoding="utf-8", errors="ignore")[:CAP])
            except Exception:
                continue
    if not chunks:
        return
    text = "\n".join(chunks)
    sig = ef.detect_env_signature(text, command_count=sd.tool_call_count)
    if sig:
        sd.env_failure_signature = sig


def parse_session(scenario_ref) -> SessionData:
    """Top-level: produce SessionData from a ScenarioRef."""
    sd = SessionData()
    if scenario_ref.transcript_md and scenario_ref.transcript_md.is_file():
        _scan_transcript_md(scenario_ref.transcript_md, sd)
    # HTML fallback: if sentinel not found in MD (or no MD), try HTML transcript
    if (not sd.has_start_sentinel or not sd.has_done_sentinel):
        if scenario_ref.transcript_html and scenario_ref.transcript_html.is_file():
            _scan_transcript_html(scenario_ref.transcript_html, sd)
    if scenario_ref.stream_jsonl and scenario_ref.stream_jsonl.is_file():
        tool = scenario_ref.parent.tool
        if tool == "claude-code":
            _parse_claude_code_stream(scenario_ref.stream_jsonl, sd)
        elif tool == "copilot-cli":
            _parse_copilot_events(scenario_ref.stream_jsonl, sd)
        elif tool == "opencode-cli":
            _parse_opencode_stream(scenario_ref.stream_jsonl, sd)
        elif tool == "cursor-cli":
            _parse_cursor_stream(scenario_ref.stream_jsonl, sd)
        elif tool == "codex-cli":
            _parse_codex_stream(scenario_ref.stream_jsonl, sd,
                                persistent_jsonl=getattr(scenario_ref, 'secondary_jsonl', None))
        else:
            _parse_generic_stream(scenario_ref.stream_jsonl, sd)
    # If duration not detected, or seems too small (< 1s), use mtime as fallback
    if sd.duration_sec is None or (sd.duration_sec is not None and sd.duration_sec < 1.0):
        _duration_from_mtime(scenario_ref, sd)
    # Env-failure signature scan (after tool_call_count is populated, so the
    # codex model-refresh-with-work guard has its command-count proxy).
    _scan_env_failure_signature(scenario_ref, sd)
    return sd


def parse_session_id(name: str):
    """Return (date, time, agent, task) if matches the canonical session_id format.

    name: 20260512-114929_claude_yolo26n_detection
    """
    m = SESSION_ID_RE.match(name)
    if not m:
        return None
    return {
        "date": m.group(1),
        "time": m.group(2),
        "agent": m.group(3),
        "task": m.group(4),
    }
