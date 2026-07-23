"""Cursor 어댑터: cursor-agent -p --model --output-format stream-json, cwd=harness."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_cursor_registered():
    from core.adapters import get_adapter
    from core.adapters.cursor import CursorAdapter
    assert get_adapter("cursor") is CursorAdapter


def test_cursor_cli_bin_is_cursor_agent():
    from core.adapters.cursor import CursorAdapter
    assert CursorAdapter.cli_bin == "cursor-agent"


def test_cursor_build_command(tmp_path):
    from core.adapters import make_adapter
    from core.run_context import RunContext
    a = make_adapter("cursor", model="sonnet-4.6")
    cmd = a.build_command("build x", tmp_path, ["/harness"])
    assert "-p" in cmd and "build x" in cmd
    assert "--model" in cmd and "sonnet-4.6" in cmd
    assert "--output-format" in cmd and "stream-json" in cmd
    assert "--stream-partial-output" in cmd
    assert "--trust" in cmd


def test_cursor_resume_on_followup(tmp_path):
    from core.adapters import make_adapter
    from core.run_context import RunContext
    a = make_adapter("cursor", model="sonnet-4.6")
    ctx = RunContext(conversation_id="c1", is_followup=True, cli_session_id="chat-99")
    cmd = a.build_command("1", tmp_path, ["/harness"], run_ctx=ctx)
    assert "--resume" in cmd
    assert "chat-99" in cmd


def test_cursor_normalize_invalid_json_message_fallback():
    from core.adapters.cursor import CursorAdapter
    a = CursorAdapter()
    ev = a.normalize("raw text")
    assert ev["type"] == "message"
    assert ev["text"] == "raw text"
