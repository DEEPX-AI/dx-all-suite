# SPDX-License-Identifier: Apache-2.0
"""Unit tests for ``generate_transcripts`` — the reusable helper that produces
all three transcript formats (jsonl + md + html) for a Claude Code session, so
transcripts are ALWAYS available, not only inside test.sh autopilot/manual runs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# dx_transcripts is on PYTHONPATH=.deepx/tools/src (see tools/tests run command)
from dx_transcripts import parse_claude_session as pcs
from dx_transcripts import generate_transcripts as gt

_UUID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def _make_store(tmp_path, monkeypatch):
    """Create a fake ~/.claude/projects store with one minimal session jsonl."""
    fake_projects = tmp_path / "projects"
    proj_dir = fake_projects / "-any-encoded-name"
    proj_dir.mkdir(parents=True)
    f = proj_dir / f"{_UUID}.jsonl"
    f.write_text(
        '{"type":"user","timestamp":"2026-05-22T11:00:00.000Z",'
        '"sessionId":"' + _UUID + '","cwd":"/anything","gitBranch":"main",'
        '"version":"x","userType":"external",'
        '"message":{"role":"user","content":"hello world"}}\n'
        '{"type":"assistant","timestamp":"2026-05-22T11:00:05.000Z",'
        '"sessionId":"' + _UUID + '",'
        '"message":{"role":"assistant","content":[{"type":"text","text":"hi there"}]}}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(pcs, "CLAUDE_PROJECTS_DIR", fake_projects)
    return f


def test_generate_all_three_formats(tmp_path, monkeypatch):
    src = _make_store(tmp_path, monkeypatch)
    out = tmp_path / "out"
    written = gt.generate(out_dir=out, prefix="demo", session_id=_UUID)

    for key in ("md", "html", "jsonl"):
        assert key in written, f"missing {key} in result"
        p = Path(written[key])
        assert p.exists() and p.stat().st_size > 0, f"{key} not written / empty"

    assert Path(written["md"]).name == "demo-session.md"
    assert Path(written["html"]).name == "demo-session.html"
    assert Path(written["jsonl"]).name == "demo-stream.jsonl"

    # HTML must actually be HTML
    assert "<" in Path(written["html"]).read_text(encoding="utf-8")[:300].lower()
    # jsonl is a faithful copy of the source session store file
    assert Path(written["jsonl"]).read_text(encoding="utf-8") == src.read_text(encoding="utf-8")


def test_stream_json_override_used_for_jsonl(tmp_path, monkeypatch):
    """When an explicit --stream-json log is given, it is copied as the .jsonl."""
    _make_store(tmp_path, monkeypatch)
    custom = tmp_path / "custom-stream.jsonl"
    custom.write_text('{"type":"system","subtype":"init"}\n', encoding="utf-8")
    out = tmp_path / "out2"
    written = gt.generate(out_dir=out, prefix="rec", session_id=_UUID,
                          stream_json=str(custom))
    assert Path(written["jsonl"]).read_text(encoding="utf-8") == custom.read_text(encoding="utf-8")


def test_missing_session_raises(tmp_path, monkeypatch):
    _make_store(tmp_path, monkeypatch)
    with pytest.raises(gt.NoSessionFound):
        gt.generate(out_dir=tmp_path / "o", prefix="x",
                    session_id="ffffffff-0000-0000-0000-000000000000")


def test_explicit_tool_claude(tmp_path, monkeypatch):
    """`tool="claude"` uses the existing parse_claude_session renderers."""
    _make_store(tmp_path, monkeypatch)
    out = tmp_path / "o"
    written = gt.generate(out_dir=out, prefix="d", session_id=_UUID, tool="claude")
    assert all(Path(written[k]).exists() for k in ("md", "html", "jsonl"))


def test_unsupported_tool_raises(tmp_path, monkeypatch):
    """A tool without a registered loader raises a clear error (not silently empty)."""
    _make_store(tmp_path, monkeypatch)
    with pytest.raises(gt.UnsupportedTool):
        gt.generate(out_dir=tmp_path / "o", prefix="d", session_id=_UUID, tool="bogus")


def test_claude_is_registered():
    """claude must be a supported tool."""
    assert "claude" in gt.SUPPORTED_TOOLS


def test_all_five_tools_registered():
    """All five agent-driven CLIs have a registered loader (stage 2a)."""
    assert set(gt.SUPPORTED_TOOLS) == {"claude", "copilot", "codex", "cursor", "opencode"}


# ---------------------------------------------------------------------------
# session-id auto-resolution from each CLI's own env var
# ---------------------------------------------------------------------------

def test_resolve_session_id_from_env_known_tools(monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "cc-123")
    monkeypatch.setenv("CODEX_THREAD_ID", "cx-456")
    monkeypatch.setenv("COPILOT_AGENT_SESSION_ID", "cp-789")
    assert gt._resolve_session_id_from_env("claude") == "cc-123"
    assert gt._resolve_session_id_from_env("codex") == "cx-456"
    assert gt._resolve_session_id_from_env("copilot") == "cp-789"


def test_resolve_session_id_from_env_absent_for_cursor_opencode(monkeypatch):
    # cursor/opencode expose no usable session-id env var → None (cwd-scoped fallback)
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID", raising=False)
    assert gt._resolve_session_id_from_env("cursor") is None
    assert gt._resolve_session_id_from_env("opencode") is None
    monkeypatch.delenv("CODEX_THREAD_ID", raising=False)
    assert gt._resolve_session_id_from_env("codex") is None  # empty/missing → None


def test_main_resolves_claude_env_when_no_session_id(tmp_path, monkeypatch):
    src = _make_store(tmp_path, monkeypatch)
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", _UUID)
    out = tmp_path / "envout"
    rc = gt.main(["--tool", "claude", "--out-dir", str(out), "--prefix", "e"])
    assert rc == 0
    assert (out / "e-session.md").exists()


# ---------------------------------------------------------------------------
# cursor cwd-scoping + empty-session skip
# ---------------------------------------------------------------------------

def _cursor_jsonl_payload():
    return (
        '{"type":"user","message":{"role":"user","content":"hi"},"session_id":"S"}\n'
        '{"type":"assistant","message":{"content":[{"type":"text","text":"yo"}]}}\n'
    )


def test_find_cursor_jsonl_cwd_scoped_skips_other_dirs(tmp_path, monkeypatch):
    base = tmp_path / ".cursor" / "projects"
    # a DIFFERENT (polluting) project dir with a NEWER transcript
    other = base / "tmp" / "agent-transcripts" / "other-uuid"
    other.mkdir(parents=True)
    (other / "other-uuid.jsonl").write_text(_cursor_jsonl_payload(), encoding="utf-8")
    # the real cwd's encoded dir
    cwd = tmp_path / "ws" / "proj"
    cwd.mkdir(parents=True)
    enc = gt._encode_cursor_project_dir(cwd)
    mine = base / enc / "agent-transcripts" / "my-uuid"
    mine.mkdir(parents=True)
    mine_jsonl = mine / "my-uuid.jsonl"
    mine_jsonl.write_text(_cursor_jsonl_payload(), encoding="utf-8")
    # make the polluting one strictly newer
    import os as _os
    _os.utime(other / "other-uuid.jsonl", (10**9 + 100, 10**9 + 100))
    _os.utime(mine_jsonl, (10**9, 10**9))

    monkeypatch.setattr(gt.Path, "home", classmethod(lambda cls: tmp_path))
    picked = gt._find_cursor_jsonl(session_id=None, project_path=str(cwd))
    assert picked == mine_jsonl  # cwd-scoped, not the newer /tmp one


def test_find_cursor_jsonl_skips_empty_transcript(tmp_path, monkeypatch):
    base = tmp_path / ".cursor" / "projects"
    cwd = tmp_path / "ws"
    cwd.mkdir(parents=True)
    enc = gt._encode_cursor_project_dir(cwd)
    at = base / enc / "agent-transcripts"
    # empty (1-line) but NEWER session
    empty = at / "empty"; empty.mkdir(parents=True)
    (empty / "empty.jsonl").write_text('{"type":"system"}\n', encoding="utf-8")
    # substantive but OLDER session
    full = at / "full"; full.mkdir(parents=True)
    full_jsonl = full / "full.jsonl"
    full_jsonl.write_text(_cursor_jsonl_payload(), encoding="utf-8")
    import os as _os
    _os.utime(empty / "empty.jsonl", (10**9 + 100, 10**9 + 100))
    _os.utime(full_jsonl, (10**9, 10**9))

    monkeypatch.setattr(gt.Path, "home", classmethod(lambda cls: tmp_path))
    picked = gt._find_cursor_jsonl(session_id=None, project_path=str(cwd))
    assert picked == full_jsonl  # empty 1-line transcript skipped


# ---------------------------------------------------------------------------
# opencode cwd-scoping via session.directory + time_updated
# ---------------------------------------------------------------------------

def _make_opencode_db(path):
    import sqlite3
    c = sqlite3.connect(str(path))
    c.execute("CREATE TABLE session (id TEXT, directory TEXT, time_updated INTEGER)")
    c.execute("CREATE TABLE message (id TEXT, session_id TEXT)")
    c.commit()
    return c


def test_pick_opencode_session_cwd_scoped(tmp_path):
    db = tmp_path / "opencode.db"
    c = _make_opencode_db(db)
    # newest overall but in a DIFFERENT directory
    c.execute("INSERT INTO session VALUES ('ses_other', '/tmp', 200)")
    c.execute("INSERT INTO message VALUES ('m0', 'ses_other')")
    # my cwd, older, with a message
    c.execute("INSERT INTO session VALUES ('ses_mine', '/work/proj', 100)")
    c.execute("INSERT INTO message VALUES ('m1', 'ses_mine')")
    c.commit(); c.close()
    assert gt._pick_opencode_session(db, project_path="/work/proj") == "ses_mine"


def test_pick_opencode_session_skips_empty(tmp_path):
    db = tmp_path / "opencode.db"
    c = _make_opencode_db(db)
    # newest in cwd but NO messages (empty)
    c.execute("INSERT INTO session VALUES ('ses_empty', '/work', 300)")
    # older in cwd WITH a message
    c.execute("INSERT INTO session VALUES ('ses_real', '/work', 100)")
    c.execute("INSERT INTO message VALUES ('m1', 'ses_real')")
    c.commit(); c.close()
    assert gt._pick_opencode_session(db, project_path="/work") == "ses_real"


# ---------------------------------------------------------------------------
# output-dir placement policy (skip 0 / copy into all N)
# ---------------------------------------------------------------------------

def test_generate_into_output_dirs_skips_when_none(tmp_path, monkeypatch):
    _make_store(tmp_path, monkeypatch)
    assert gt.generate_into_output_dirs("claude", [], session_id=_UUID) == {}
    # non-existent dirs are filtered → still skipped
    assert gt.generate_into_output_dirs(
        "claude", [str(tmp_path / "does-not-exist")], session_id=_UUID) == {}


def test_generate_into_output_dirs_copies_into_all(tmp_path, monkeypatch):
    _make_store(tmp_path, monkeypatch)
    d1 = tmp_path / "compile"; d1.mkdir()
    d2 = tmp_path / "inference"; d2.mkdir()
    res = gt.generate_into_output_dirs("claude", [str(d1), str(d2)], session_id=_UUID)
    # primary rendered, prefix defaults to tool name
    assert (d1 / "claude-session.md").exists()
    assert (d1 / "claude-session.html").exists()
    # option A: every output dir carries the transcript
    assert (d2 / "claude-session.md").exists()
    assert (d2 / "claude-session.html").exists()
    assert set(res.keys()) == {str(d1), str(d2)}


def test_copy_into_output_dirs(tmp_path):
    log_dir = tmp_path / "logs"; log_dir.mkdir()
    (log_dir / "suite-claude-code-session.md").write_text("# t", encoding="utf-8")
    (log_dir / "suite-claude-code-session.html").write_text("<html>", encoding="utf-8")
    d1 = tmp_path / "out1"; d1.mkdir()
    d2 = tmp_path / "out2"; d2.mkdir()
    out = gt.copy_into_output_dirs(
        log_dir,
        ["suite-claude-code-session.md", "suite-claude-code-session.html", "absent.jsonl"],
        [d1, d2],
    )
    for d in (d1, d2):
        assert (d / "suite-claude-code-session.md").read_text(encoding="utf-8") == "# t"
        assert (d / "suite-claude-code-session.html").exists()
    # originals are left in place (transient log_dir)
    assert (log_dir / "suite-claude-code-session.md").exists()
    assert "absent.jsonl" not in out[str(d1)]


def test_copy_into_output_dirs_skips_when_none(tmp_path):
    log_dir = tmp_path / "logs"; log_dir.mkdir()
    (log_dir / "x-session.md").write_text("x", encoding="utf-8")
    assert gt.copy_into_output_dirs(log_dir, ["x-session.md"], []) == {}


def test_agent_path_supports_only_claude_copilot():
    assert gt._AGENT_SUPPORTED == {"claude", "copilot"}


@pytest.mark.parametrize("tool", ["cursor", "codex", "opencode"])
def test_unsupported_tools_skip_with_guidance(tool, tmp_path, monkeypatch, capsys):
    """codex/opencode/cursor are NOT auto-supported in the agent path: raise
    AgentTranscriptUnsupported, and the CLI prints a manual-generation guide
    (rc 0, no content-empty/partial transcript written)."""
    d = tmp_path / "out"; d.mkdir()
    with pytest.raises(gt.AgentTranscriptUnsupported):
        gt.generate_into_output_dirs(tool, [str(d)], project_path=str(tmp_path))
    rc = gt.main(["--tool", tool, "--project", str(tmp_path),
                  "--into-output-dirs", str(d)])
    assert rc == 0
    out = capsys.readouterr().out.lower()
    assert "not supported" in out and "manual" in out
    assert not list(d.glob("*session*"))  # nothing written


def test_unsupported_tool_still_renderable_with_explicit_stream(tmp_path):
    """A real stdout stream bypasses the agent-path guard (harness/manual flow)."""
    d = tmp_path / "o"; d.mkdir()
    jl = tmp_path / "real.jsonl"
    jl.write_text(_cursor_jsonl_payload(), encoding="utf-8")
    gt.generate_into_output_dirs("cursor", [str(d)], stream_json=str(jl))
    assert (d / "cursor-session.html").exists()


def test_unsupported_guard_is_agent_path_only():
    """The restriction lives ONLY in the in-session agent path; the manual path
    (generate/--out-dir, run post-exit) still supports codex/opencode/cursor."""
    import inspect
    assert "_AGENT_SUPPORTED" in inspect.getsource(gt.generate_into_output_dirs)
    assert "_AGENT_SUPPORTED" not in inspect.getsource(gt.generate)


def test_settle_file_returns_on_stable(tmp_path):
    """_settle_file returns promptly when the file is already stable."""
    f = tmp_path / "s.jsonl"; f.write_text("x\n", encoding="utf-8")
    import time as _t
    t0 = _t.monotonic()
    gt._settle_file(f, max_wait=2.0, interval=0.1)
    assert _t.monotonic() - t0 < 2.0  # did not burn the full max_wait


def test_main_into_output_dirs_skip_message(tmp_path, monkeypatch, capsys):
    _make_store(tmp_path, monkeypatch)
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", _UUID)
    rc = gt.main(["--tool", "claude", "--into-output-dirs"])  # zero dirs
    assert rc == 0
    assert "skipped" in capsys.readouterr().out.lower()
