#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generate jsonl + md + html transcripts for an agent-driven CLI session.

Reusable *dispatcher* over the SAME per-CLI rendering logic the e2e harness
already uses (``parse_<tool>_session`` modules) — there is NO parallel renderer
implementation here, so transcript rendering is not duplicated.

Per-tool capability (bound by each module's existing renderers):
  - claude   : md + html + jsonl   (render_markdown / render_html; store jsonl)
  - copilot  : md + html + jsonl   (render_markdown / render_html; events.jsonl)
  - codex    : md + html + jsonl   (render_codex_md / render_codex_html; rollout jsonl)
  - cursor   : html + jsonl        (render_cursor_html only — no md renderer)
  - opencode : html                (render_opencode_html only — DB-backed, no jsonl/md)

Session id is resolved (in the CLI entry point) from each tool's own env var
when not given explicitly — claude/codex/copilot expose an exact id; cursor and
opencode do not, so those fall back to cwd-scoped "most recent" selection. The
agent-driven flow (session-sentinels rule 8) renders the transcript directly
INTO the session output dir(s) via ``--into-output-dirs`` — no hook involved.

API
    generate(out_dir, prefix="session", session_id=None, project_path=None,
             tool="claude", stream_json=None, include_thinking=False) -> dict[str, Path]
    generate_into_output_dirs(tool, output_dirs, ...) -> dict[str, dict[str, Path]]
"""

from __future__ import annotations

# --- self-bootstrap: make the `dx_transcripts` package importable when this
# --- module is run as a standalone script (parents[1] == .deepx/tools/src).
import sys as _sys
from pathlib import Path as _Path
_SRC = str(_Path(__file__).resolve().parents[1])
if _SRC not in _sys.path:
    _sys.path.insert(0, _SRC)

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))


class NoSessionFound(RuntimeError):
    """Raised when no session matches the given id / project path."""


class UnsupportedTool(ValueError):
    """Raised when a tool has no registered transcript loader."""


class AgentTranscriptUnsupported(RuntimeError):
    """Raised by the agent-driven path (``generate_into_output_dirs``) for tools
    that cannot produce a good transcript *in-session*. The message carries a
    manual-generation guide for the user. Only claude/copilot are auto-supported
    (they commit the DONE turn to the store before the generator runs); codex
    (single-shot exec) and opencode (DB commit at turn end) only finalize the
    last turn at process exit, and cursor redacts assistant text in its store."""


# Tools whose live session store is complete+usable when rendered right after
# the DONE line; only these are auto-supported in the agent-driven path.
_AGENT_SUPPORTED = {"claude", "copilot"}

# Per-tool manual-generation guidance for the unsupported tools.
_AGENT_GUIDANCE = {
    "codex": (
        "codex (exec) commits its final turn only at process exit, so an "
        "in-session transcript would miss the end. AFTER the session ends, render "
        "the complete transcript from the finalized store:\n"
        "  python3 <generate_transcripts.py> --tool codex --project . --out-dir <DIR>"
    ),
    "opencode": (
        "opencode commits its final turn to the DB at session end, so an "
        "in-session transcript would miss the end. AFTER the session ends, render "
        "the complete transcript from the finalized DB:\n"
        "  python3 <generate_transcripts.py> --tool opencode --project . --out-dir <DIR>"
    ),
    "cursor": (
        "cursor's persisted transcript redacts assistant text (real text lives "
        "only in the live stdout stream). Capture it with "
        "`agent -p --output-format stream-json > run.jsonl` and render with "
        "`--tool cursor --stream-json run.jsonl`, or use your IDE session history."
    ),
}


# ---------------------------------------------------------------------------
# session-id resolution
# ---------------------------------------------------------------------------

# Each CLI injects its own session-id into the agent shell's environment.
# claude/codex/copilot expose an exact id; cursor/opencode do NOT (verified
# empirically), so those fall back to cwd-scoped "most recent" selection in
# their loaders.  NOTE: opencode's OPENCODE_RUN_ID is a process-run UUID that
# does NOT map to the DB ``ses_*`` id, so it is intentionally absent here.
_SESSION_ENV_VARS: Dict[str, str] = {
    "claude": "CLAUDE_CODE_SESSION_ID",
    "codex": "CODEX_THREAD_ID",
    "copilot": "COPILOT_AGENT_SESSION_ID",
}


def _resolve_session_id_from_env(tool: str) -> Optional[str]:
    """Return the tool's own session id from its env var, or None.

    Only meaningful inside the live agent shell of that CLI (the agent-driven
    transcript step).  Library callers that already know the id should pass it
    explicitly — env resolution is applied in the CLI entry point only, so
    importing callers are never surprised by ambient env contamination.
    """
    var = _SESSION_ENV_VARS.get(tool)
    if not var:
        return None
    val = os.environ.get(var, "").strip()
    return val or None


def _jsonl_line_count(path: Path) -> int:
    try:
        with open(path, "rb") as fh:
            return sum(1 for _ in fh)
    except Exception:
        return 0


def _settle_file(path, max_wait: float = 5.0, interval: float = 0.3) -> None:
    """Wait until *path* stops growing (size stable across two reads), bounded by
    *max_wait*. Used in the agent-driven path so a transcript rendered right after
    the DONE line captures the final, fully-flushed turn instead of a mid-write
    snapshot. No-op if the file is missing or already stable."""
    try:
        p = Path(path)
        prev, stable, waited = -1, 0, 0.0
        while waited < max_wait:
            cur = p.stat().st_size if p.exists() else -1
            if cur == prev and cur >= 0:
                stable += 1
                if stable >= 2:
                    return
            else:
                stable = 0
            prev = cur
            time.sleep(interval)
            waited += interval
    except Exception:
        return


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _write_text(out_dir: Path, prefix: str, suffix: str, text: str) -> Path:
    p = out_dir / f"{prefix}-{suffix}"
    p.write_text(text, encoding="utf-8")
    return p


def _copy_jsonl(out_dir: Path, prefix: str, src) -> Optional[Path]:
    if not src:
        return None
    src = Path(src)
    if not src.exists():
        return None
    p = out_dir / f"{prefix}-stream.jsonl"
    shutil.copy2(str(src), str(p))
    # Also emit a session-stem alias so the jsonl naming matches the md/html
    # (`<prefix>-session.md/.html`). `-stream.jsonl` is kept for back-compat
    # (several tools/tests reference it).
    try:
        shutil.copy2(str(src), str(out_dir / f"{prefix}-session.jsonl"))
    except Exception:
        pass
    return p


def _session_metrics(jsonl_path) -> Optional[dict]:
    """Pull usage/cost/tool metrics from a session jsonl.

    Works for both the `-p --output-format stream-json` stdout (has a top-level
    ``result`` event with ``usage`` + ``total_cost_usd``) and a session-store
    jsonl (no result event — output tokens summed from per-message usage, cost
    left None). Returns None if nothing useful is found. Best-effort."""
    import collections
    if not jsonl_path or not Path(jsonl_path).exists():
        return None
    model = None
    results = []
    tools = collections.Counter()
    skills = []
    toolsets = []
    out_sum = 0
    turns = 0
    try:
        with open(jsonl_path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                t = o.get("type")
                if t == "system" and o.get("subtype") == "init":
                    model = model or o.get("model")
                if t == "result":
                    results.append(o)
                msg = o.get("message") if isinstance(o.get("message"), dict) else None
                if msg:
                    model = model or msg.get("model")
                    u = msg.get("usage") or {}
                    if u.get("output_tokens"):
                        out_sum += u.get("output_tokens", 0)
                    if t == "assistant" or msg.get("role") == "assistant":
                        turns += 1
                        for c in (msg.get("content") or []):
                            if isinstance(c, dict) and c.get("type") == "tool_use":
                                nm = c.get("name")
                                tools[nm] += 1
                                inp = c.get("input") or {}
                                if nm == "Skill":
                                    sk = inp.get("skill")
                                    if sk and sk not in skills:
                                        skills.append(sk)
                                elif nm == "Read":
                                    fp = inp.get("file_path") or ""
                                    if "/.deepx/toolsets/" in fp and fp.endswith(".md"):
                                        ts = fp.rsplit("/", 1)[-1][:-3]
                                        if ts not in toolsets:
                                            toolsets.append(ts)
    except Exception:
        return None
    m = {"model": model, "tools": dict(tools), "skills": skills, "toolsets": toolsets,
         "output_tokens": None, "total_cost_usd": None,
         "num_turns": turns or None, "duration_ms": None}
    if results:
        # A long build can emit MULTIPLE result events (e.g. a resumed `-p` session):
        # duration/turns/output_tokens are PER-SEGMENT (sum them); total_cost_usd is
        # CUMULATIVE (take the last). Using only the last result would under-report a
        # 20-min build as the few-second final fragment.
        last = results[-1]
        dur = sum(r.get("duration_ms") or 0 for r in results)
        nturns = sum(r.get("num_turns") or 0 for r in results)
        otok = sum((r.get("usage") or {}).get("output_tokens") or 0 for r in results)
        m["output_tokens"] = otok or None
        m["total_cost_usd"] = last.get("total_cost_usd")
        m["num_turns"] = nturns or m["num_turns"]
        m["duration_ms"] = dur or None
    if not m["output_tokens"] and out_sum:
        m["output_tokens"] = out_sum
    if not m["model"] and not m["output_tokens"]:
        return None
    return m


def _metrics_rows(m):
    rows = []
    if m.get("model"):
        rows.append(("Model", f"`{m['model']}`"))
    if m.get("duration_ms"):
        rows.append(("Wall-clock", f"~{round(m['duration_ms'] / 60000, 1)} min"))
    if m.get("num_turns"):
        rows.append(("Agent turns", str(m["num_turns"])))
    if m.get("output_tokens"):
        rows.append(("Output tokens", f"{m['output_tokens']:,}"))
    if m.get("total_cost_usd") is not None:
        rows.append(("Cost (reported)", f"${m['total_cost_usd']:.2f}"))
    if m.get("tools"):
        rows.append(("Tools", ", ".join(f"{k}×{v}" for k, v in
                                         sorted(m["tools"].items(), key=lambda x: -x[1]))))
    if m.get("skills"):
        rows.append(("Skills", " → ".join(m["skills"])))
    if m.get("toolsets"):
        rows.append(("Toolsets", ", ".join(f"`{ts}`" for ts in m["toolsets"])))
    elif m.get("skills"):
        # KB-driven session (skills used) that read no .deepx/toolsets — surface it
        rows.append(("Toolsets", "— (none read)"))
    return rows


def _inject_metrics(written: dict, jsonl_path, store_jsonl=None) -> None:
    """Prepend a 'Session summary' block (model/turns/tools/tokens/cost) to the
    rendered md + html, computed from the session jsonl. Best-effort; never raises.

    When ``jsonl_path`` is a ``-p`` STREAM capture and ``store_jsonl`` is the session
    store, MERGE the two: the stream's ``result`` events carry the authoritative
    cumulative **cost** + **wall-clock** (the store has neither), while the store carries
    the accurate per-message **output_tokens** + **turns** + full **tool/skill** history.
    The stream's ``result.usage`` is only the final-result usage per segment, so on a
    multi-segment build it badly under-reports total output tokens — hence we prefer the
    store for tokens/turns whenever it is available."""
    try:
        m = _session_metrics(jsonl_path)
        if store_jsonl and str(store_jsonl) != str(jsonl_path):
            ms = _session_metrics(store_jsonl)
            if ms:
                base = dict(m or {})
                # store-accurate fields override the stream's result-based ones
                for k in ("output_tokens", "num_turns", "tools", "skills", "toolsets"):
                    if ms.get(k):
                        base[k] = ms[k]
                if not base.get("model"):
                    base["model"] = ms.get("model")
                # keep duration_ms + total_cost_usd from the stream (m); store lacks them
                m = base
        rows = _metrics_rows(m) if m else []
        if not rows:
            return
        md = ("## Session summary\n\n| Metric | Value |\n|---|---|\n"
              + "\n".join(f"| {k} | {v} |" for k, v in rows) + "\n\n")
        import html as _html
        hrows = "".join(
            f"<tr><td><b>{_html.escape(k)}</b></td><td>{_html.escape(v)}</td></tr>"
            for k, v in rows)
        hblock = ('<div class="session-summary"><h2>Session summary</h2>'
                  '<table border="1" cellpadding="4" style="border-collapse:collapse">'
                  + hrows + "</table></div>\n")
        mdp = written.get("md")
        if mdp and Path(mdp).exists():
            txt = Path(mdp).read_text(encoding="utf-8")
            lines = txt.split("\n")
            if lines and lines[0].startswith("#"):
                txt = lines[0] + "\n\n" + md + "\n".join(lines[1:])
            else:
                txt = md + txt
            Path(mdp).write_text(txt, encoding="utf-8")
        hp = written.get("html")
        if hp and Path(hp).exists():
            h = Path(hp).read_text(encoding="utf-8")
            bi = h.lower().find("<body")
            if bi != -1:
                ins = h.find(">", bi) + 1
                h = h[:ins] + "\n" + hblock + h[ins:]
            else:
                h = hblock + h
            Path(hp).write_text(h, encoding="utf-8")
    except Exception:
        return


def _turns_to_md(label: str, session_id, turns) -> str:
    """Render a ParsedSession's turns to a simple Markdown log.

    Used for tools whose parse_<tool>_session has no render_markdown (cursor,
    opencode). Mirrors the conftest ``_save_<tool>_session_log`` md shape, built
    from the ParsedSession.turns (each turn exposes user_content/assistant_content).
    """
    lines = [
        f"# {label} Session",
        "",
        f"- **Session ID:** {session_id or 'unknown'}",
        "",
        "## Conversation",
        "",
    ]
    for t in turns or []:
        user = (getattr(t, "user_content", "") or "").strip()
        asst = (getattr(t, "assistant_content", "") or "").strip()
        if user:
            lines += ["### User", "", user, ""]
        if asst:
            lines += ["### Assistant", "", asst, ""]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# per-tool loaders — each reuses its parse_<tool>_session renderers
# loader(out_dir, prefix, session_id, project_path, include_thinking, stream_json) -> dict
# ---------------------------------------------------------------------------

def _load_claude(out_dir, prefix, session_id, project_path, include_thinking, stream_json, wait_settle=False):
    from dx_transcripts.parse_claude_session import (
        find_sessions, parse_session, render_html, render_markdown,
    )
    if session_id:
        sessions = find_sessions(session_id=session_id)
    elif project_path:
        sessions = find_sessions(project_path=str(project_path))
    else:
        raise ValueError("provide session_id or project_path")
    if not sessions:
        raise NoSessionFound(f"claude: no session (id={session_id!r})")
    meta = sessions[0]
    if wait_settle and not stream_json:
        _settle_file(getattr(meta, "jsonl_path", None))
    parsed = parse_session(meta, include_thinking=include_thinking)
    written = {
        "md": _write_text(out_dir, prefix, "session.md", render_markdown(parsed)),
        "html": _write_text(out_dir, prefix, "session.html", render_html(parsed)),
    }
    _src = stream_json or getattr(meta, "jsonl_path", None)
    jl = _copy_jsonl(out_dir, prefix, _src)
    if jl:
        written["jsonl"] = jl
    # When rendering from a stream capture, merge store-accurate tokens/turns in.
    _inject_metrics(written, _src, store_jsonl=getattr(meta, "jsonl_path", None))
    return written


def _load_copilot(out_dir, prefix, session_id, project_path, include_thinking, stream_json, wait_settle=False):
    from dx_transcripts.parse_copilot_session import (
        find_sessions, parse_session, render_html, render_markdown,
    )
    if session_id:
        sessions = find_sessions(session_id=session_id)
    elif project_path:
        sessions = find_sessions(cwd=str(project_path))
    else:
        raise ValueError("provide session_id or project_path")
    if not sessions:
        raise NoSessionFound(f"copilot: no session (id={session_id!r})")
    meta = sessions[0]
    if wait_settle and not stream_json:
        sd = getattr(meta, "session_dir", None)
        if sd:
            _settle_file(Path(sd) / "events.jsonl")
    parsed = parse_session(meta)
    written = {
        "md": _write_text(out_dir, prefix, "session.md", render_markdown(parsed)),
        "html": _write_text(out_dir, prefix, "session.html", render_html(parsed)),
    }
    events = stream_json
    if not events:
        sd = getattr(meta, "session_dir", None)
        if sd:
            events = Path(sd) / "events.jsonl"
    jl = _copy_jsonl(out_dir, prefix, events)
    if jl:
        written["jsonl"] = jl
    _inject_metrics(written, events)
    return written


def _find_codex_jsonl(session_id=None) -> Optional[Path]:
    base = Path.home() / ".codex" / "sessions"
    if not base.exists():
        return None
    if session_id:
        hits = sorted(base.rglob(f"*{session_id}*.jsonl"))
        return hits[0] if hits else None
    # no id (agent-driven --project): the just-finished session = newest rollout
    cands = list(base.rglob("rollout-*.jsonl"))
    return max(cands, key=lambda p: p.stat().st_mtime) if cands else None


def _load_codex(out_dir, prefix, session_id, project_path, include_thinking, stream_json, wait_settle=False):
    jsonl = Path(stream_json) if stream_json else _find_codex_jsonl(session_id)
    if not jsonl or not Path(jsonl).exists():
        raise NoSessionFound(f"codex: no rollout jsonl (id={session_id!r})")
    if wait_settle and not stream_json:
        _settle_file(jsonl)
    from dx_transcripts.parse_codex_session import render_codex_html, render_codex_md
    written = {}
    md_p = out_dir / f"{prefix}-session.md"
    render_codex_md(Path(jsonl), md_p)
    if md_p.exists():
        written["md"] = md_p
    html_p = out_dir / f"{prefix}-session.html"
    render_codex_html(Path(jsonl), html_p)
    if html_p.exists():
        written["html"] = html_p
    jl = _copy_jsonl(out_dir, prefix, jsonl)
    if jl:
        written["jsonl"] = jl
    return written


def _encode_cursor_project_dir(project_path) -> str:
    """Cursor encodes a workspace cwd as ``<abs-path>`` with the leading slash
    dropped and every remaining ``/`` turned into ``-`` (e.g. ``/data/home/x``
    → ``data-home-x``)."""
    return str(Path(project_path).resolve()).lstrip("/").replace("/", "-")


def _find_cursor_jsonl(session_id=None, project_path=None) -> Optional[Path]:
    base = Path.home() / ".cursor" / "projects"
    if not base.exists():
        return None
    if session_id:
        hits = sorted(base.rglob(f"agent-transcripts/{session_id}/{session_id}.jsonl"))
        if hits:
            return hits[0]
        hits = sorted(base.rglob(f"{session_id}.jsonl"))
        return hits[0] if hits else None
    # no id (cursor exposes no session-id env): pick the newest transcript,
    # SCOPED to this cwd's encoded project dir when available (global newest
    # is easily polluted by concurrent sessions in other dirs — e.g. /tmp).
    # Also skip near-empty transcripts (< 2 lines) so a degenerate 1-line test
    # session does not shadow the real one.
    proj_dir = base / _encode_cursor_project_dir(project_path) if project_path else None
    root = proj_dir if (proj_dir and proj_dir.is_dir()) else base
    cands = list(root.rglob("agent-transcripts/*/*.jsonl"))
    if not cands:
        return None
    substantive = [c for c in cands if _jsonl_line_count(c) >= 2]
    pool = substantive or cands
    return max(pool, key=lambda p: p.stat().st_mtime)


def _load_cursor(out_dir, prefix, session_id, project_path, include_thinking, stream_json, wait_settle=False):
    jsonl = Path(stream_json) if stream_json else _find_cursor_jsonl(session_id, project_path)
    if not jsonl or not Path(jsonl).exists():
        raise NoSessionFound(f"cursor: no transcript jsonl (id={session_id!r})")
    # When picked by cwd-scope (no explicit id), the transcript file stem IS the
    # session uuid — surface it so the md/html carry the real id, not "unknown".
    if not session_id:
        session_id = Path(jsonl).stem
    from dx_transcripts.parse_cursor_session import render_cursor_html, parse_cursor_transcript
    written = {}
    # md: cursor has no render_markdown — build from ParsedSession.turns
    try:
        ps = parse_cursor_transcript(Path(jsonl))
        written["md"] = _write_text(
            out_dir, prefix, "session.md",
            _turns_to_md("Cursor CLI", session_id, ps.turns),
        )
    except Exception:
        pass
    html_p = out_dir / f"{prefix}-session.html"
    render_cursor_html(Path(jsonl), html_p, session_id_override=session_id or "")
    if html_p.exists():
        written["html"] = html_p
    jl = _copy_jsonl(out_dir, prefix, jsonl)
    if jl:
        written["jsonl"] = jl
    return written


def _pick_opencode_session(db_path, project_path=None) -> Optional[str]:
    """Most-recently-updated non-empty opencode session, cwd-scoped when possible."""
    import sqlite3
    try:
        c = sqlite3.connect(str(db_path))
    except Exception:
        return None
    try:
        def _q(where, params):
            sql = (
                "SELECT s.id FROM session s "
                "WHERE EXISTS (SELECT 1 FROM message m WHERE m.session_id = s.id)"
                + (f" AND {where}" if where else "")
                + " ORDER BY s.time_updated DESC LIMIT 1"
            )
            try:
                return c.execute(sql, params).fetchone()
            except Exception:
                return None
        row = None
        if project_path:
            cands = {str(project_path), str(Path(project_path).resolve())}
            placeholders = ",".join("?" * len(cands))
            row = _q(f"s.directory IN ({placeholders})", tuple(cands))
        if not row:
            row = _q("", ())
        if not row:
            # last resort: ignore the non-empty filter
            try:
                row = c.execute(
                    "SELECT id FROM session ORDER BY time_updated DESC LIMIT 1"
                ).fetchone()
            except Exception:
                row = None
        return row[0] if row else None
    finally:
        c.close()


def _settle_opencode(db_path, session_id, max_wait: float = 5.0, interval: float = 0.4) -> None:
    """Wait until the session's message count in the DB stops growing."""
    import sqlite3
    try:
        c = sqlite3.connect(str(db_path))
    except Exception:
        return
    try:
        prev, stable, waited = -1, 0, 0.0
        while waited < max_wait:
            try:
                cur = c.execute(
                    "SELECT COUNT(*) FROM message WHERE session_id=?", (session_id,)
                ).fetchone()[0]
            except Exception:
                return
            if cur == prev:
                stable += 1
                if stable >= 2:
                    return
            else:
                stable = 0
            prev = cur
            time.sleep(interval)
            waited += interval
    finally:
        c.close()


def _load_opencode(out_dir, prefix, session_id, project_path, include_thinking, stream_json, wait_settle=False):
    from dx_transcripts.parse_opencode_session import (
        OPENCODE_DB_PATH, render_opencode_html, parse_opencode_db,
    )
    if not session_id:
        # no id (opencode's OPENCODE_RUN_ID does not map to ses_*): pick the
        # most-recently-updated session, SCOPED to this cwd via the session
        # table's ``directory`` column, and only sessions that actually have
        # messages (skip empty). Global most-recent is the last-resort fallback.
        session_id = _pick_opencode_session(OPENCODE_DB_PATH, project_path)
    if not session_id:
        raise NoSessionFound("opencode: no session_id and no session in DB")
    if wait_settle and not stream_json:
        _settle_opencode(OPENCODE_DB_PATH, session_id)
    written = {}
    # md: opencode has no render_markdown — build from ParsedSession.turns (DB)
    try:
        ps = parse_opencode_db(OPENCODE_DB_PATH, session_id)
        written["md"] = _write_text(
            out_dir, prefix, "session.md",
            _turns_to_md("OpenCode", session_id, ps.turns),
        )
    except Exception:
        pass
    html_p = out_dir / f"{prefix}-session.html"
    jsonl_arg = Path(stream_json) if stream_json else Path(os.devnull)
    render_opencode_html(
        jsonl_arg, html_p,
        session_id_override=session_id,
        db_path=OPENCODE_DB_PATH,
    )
    if html_p.exists() and html_p.stat().st_size > 0:
        written["html"] = html_p
    jl = _copy_jsonl(out_dir, prefix, stream_json)
    if jl:
        written["jsonl"] = jl
    if not written:
        raise NoSessionFound(f"opencode: no session in DB (id={session_id!r})")
    return written  # md + html (+ jsonl if stdout provided); DB-backed


_TOOL_LOADERS: Dict[str, Callable] = {
    "claude": _load_claude,
    "copilot": _load_copilot,
    "codex": _load_codex,
    "cursor": _load_cursor,
    "opencode": _load_opencode,
}
SUPPORTED_TOOLS = tuple(sorted(_TOOL_LOADERS))


def generate(
    out_dir,
    prefix: str = "session",
    session_id: Optional[str] = None,
    project_path: Optional[str] = None,
    tool: str = "claude",
    stream_json: Optional[str] = None,
    include_thinking: bool = False,
    wait_settle: bool = False,
) -> Dict[str, Path]:
    """Render available transcript formats for *tool* into *out_dir*.

    Returns a dict with the subset of ``{"jsonl","md","html"}`` actually produced
    (cursor omits md; opencode omits md and — without a stdout jsonl — jsonl).
    *wait_settle* (agent-driven path) waits for the live session store to stop
    growing before rendering, so a transcript taken right after the DONE line is
    complete. Raises :class:`UnsupportedTool` / :class:`NoSessionFound`.
    """
    loader = _TOOL_LOADERS.get(tool)
    if loader is None:
        raise UnsupportedTool(
            f"tool {tool!r} not supported (have: {', '.join(SUPPORTED_TOOLS)})"
        )
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return loader(out_dir, prefix, session_id, project_path, include_thinking,
                  stream_json, wait_settle)


def _existing_dirs(output_dirs) -> list:
    out = []
    for d in output_dirs or []:
        if not d:
            continue
        p = Path(d)
        if p.is_dir() and p not in out:
            out.append(p)
    return out


def generate_into_output_dirs(
    tool: str,
    output_dirs,
    *,
    project_path: Optional[str] = None,
    session_id: Optional[str] = None,
    stream_json: Optional[str] = None,
    include_thinking: bool = False,
    prefix: Optional[str] = None,
) -> Dict[str, Dict[str, Path]]:
    """Render the transcript directly INTO the session output dir(s).

    Policy (per design decision): the transcript lives with the artifacts it
    documents for traceability —
      * 0 output dirs  -> generation is SKIPPED (returns ``{}``)
      * 1 output dir   -> rendered into it
      * N output dirs  -> rendered into the first, then COPIED into the rest
                          (option A — every output dir carries the transcript)

    File names use ``<prefix>-session.{md,html}`` / ``<prefix>-stream.jsonl``
    with *prefix* defaulting to the tool name, so each session dir holds one
    predictably-named transcript. Returns ``{output_dir: {kind: path}}``.
    """
    # Only claude/copilot produce a complete in-session transcript (their store
    # has the DONE turn committed before the generator runs). codex/opencode
    # finalize the last turn at process exit and cursor redacts its store, so the
    # agent path skips them and hands back a manual-generation guide (unless a
    # real stdout stream is supplied, which the harness/manual flow can do).
    if tool not in _AGENT_SUPPORTED and not stream_json:
        raise AgentTranscriptUnsupported(_AGENT_GUIDANCE.get(
            tool, f"{tool}: auto-transcript not supported in the agent path."))
    dirs = _existing_dirs(output_dirs)
    if not dirs:
        return {}
    prefix = prefix or tool
    primary = dirs[0]
    written = generate(
        out_dir=primary, prefix=prefix, session_id=session_id,
        project_path=project_path, tool=tool, stream_json=stream_json,
        include_thinking=include_thinking, wait_settle=True,
    )
    results: Dict[str, Dict[str, Path]] = {str(primary): written}
    for d in dirs[1:]:
        copied: Dict[str, Path] = {}
        for kind, src in written.items():
            try:
                dst = d / Path(src).name
                shutil.copy2(str(src), str(dst))
                copied[kind] = dst
            except Exception:
                pass
        results[str(d)] = copied
    return results


def copy_into_output_dirs(log_dir, filenames, output_dirs) -> Dict[str, Dict[str, Path]]:
    """Copy already-generated ``log_dir`` transcript files into each detected
    session output dir (option A). Used by the e2e harness (conftest/test.sh),
    which renders its own scenario-tagged transcripts into ``log_dir`` first.

    Same placement policy as :func:`generate_into_output_dirs`: 0 dirs -> no-op,
    N dirs -> copied into every dir. The ``log_dir`` originals are left in place
    (transient artifacts dir). Best-effort; returns ``{output_dir: {name: dst}}``.
    """
    dirs = _existing_dirs(output_dirs)
    if not dirs:
        return {}
    out: Dict[str, Dict[str, Path]] = {}
    for d in dirs:
        placed: Dict[str, Path] = {}
        for name in filenames:
            src = Path(log_dir) / name
            if not src.exists():
                continue
            try:
                dst = d / name
                shutil.copy2(str(src), str(dst))
                placed[name] = dst
            except Exception:
                pass
        out[str(d)] = placed
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Generate jsonl+md+html transcripts for an agent-driven CLI session."
    )
    ap.add_argument("--tool", default="claude",
                    help=f"CLI tool ({', '.join(SUPPORTED_TOOLS)})")
    ap.add_argument("--session-id", help="session id/UUID (preferred; "
                    "auto-resolved from the CLI's own env var when omitted)")
    ap.add_argument("--project", help="workdir path (most recent session)")
    ap.add_argument("--out-dir", help="explicit output dir (single transcript)")
    ap.add_argument("--into-output-dirs", nargs="*", metavar="DIR",
                    help="session output dir(s); transcript written into each "
                         "(option A). Pass none/empty to SKIP generation.")
    ap.add_argument("--prefix", default="session")
    ap.add_argument("--stream-json", help="raw stream-json log to use/copy as .jsonl")
    ap.add_argument("--include-thinking", action="store_true")
    a = ap.parse_args(argv)

    # Auto-resolve the session id from this CLI's own env var when not given
    # (claude/codex/copilot expose it exactly; cursor/opencode return None and
    # fall back to cwd-scoped selection in their loaders).
    if not a.session_id:
        a.session_id = _resolve_session_id_from_env(a.tool)

    # Agent-driven placement: render into the session output dir(s).
    if a.into_output_dirs is not None:
        try:
            results = generate_into_output_dirs(
                a.tool, a.into_output_dirs, project_path=a.project,
                session_id=a.session_id, stream_json=a.stream_json,
                include_thinking=a.include_thinking,
                prefix=(a.prefix if a.prefix != "session" else None),
            )
        except AgentTranscriptUnsupported as exc:
            print(f"transcript auto-generation not supported for {a.tool} — "
                  f"skipped. Manual transcript guide:\n{exc}")
            return 0
        except (NoSessionFound, UnsupportedTool) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        if not results:
            print("no output dir produced — transcript generation skipped")
            return 0
        for d, files in results.items():
            for key in ("jsonl", "md", "html"):
                if key in files:
                    print(f"{key}: {files[key]}")
        return 0

    if not a.out_dir:
        ap.error("provide --into-output-dirs or --out-dir")
    if not a.session_id and not a.project:
        ap.error("one of --session-id / --project is required")
    try:
        written = generate(
            out_dir=a.out_dir, prefix=a.prefix, session_id=a.session_id,
            project_path=a.project, tool=a.tool, stream_json=a.stream_json,
            include_thinking=a.include_thinking,
        )
    except (NoSessionFound, UnsupportedTool) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    for key in ("jsonl", "md", "html"):
        if key in written:
            print(f"{key}: {written[key]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
