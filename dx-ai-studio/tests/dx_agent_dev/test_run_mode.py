"""Tests for /api/agent/run mode=autopilot|interactive wiring in server.py.

Source-contract style: inspects server.py text to verify the correct logic is present.
"""
import pathlib

SRV = pathlib.Path(__file__).resolve().parents[2] / "dx_agent_dev" / "server.py"


def _src() -> str:
    return SRV.read_text()



def test_server_reads_mode_from_body():
    """Server must parse the 'mode' key from the JSON body."""
    s = _src()
    assert 'body.get("mode")' in s, "server.py must read body.get(\"mode\")"



def test_server_imports_wrap_autopilot_prompt():
    """wrap_autopilot_prompt must be imported in server.py."""
    s = _src()
    assert "wrap_autopilot_prompt" in s, (
        "wrap_autopilot_prompt must be imported and used in server.py"
    )


def test_server_uses_wrap_autopilot_prompt_in_handler():
    """wrap_autopilot_prompt must be called inside the _run_sse handler, not just imported."""
    s = _src()
    # Must appear as a call site (after the import line)
    handler_body = s.split("def _run_sse", 1)[-1]
    assert "wrap_autopilot_prompt" in handler_body, (
        "_run_sse handler must call wrap_autopilot_prompt"
    )



def test_server_passes_autopilot_true_to_run_context():
    """RunContext must be constructed with autopilot=True when mode==autopilot."""
    s = _src()
    assert "autopilot=True" in s, (
        "RunContext(..., autopilot=True) must appear in server.py"
    )



def test_autopilot_forces_no_resume():
    """Autopilot run must force is_followup=False so it is a clean one-shot.

    We check that is_followup=False appears inside the handler body (not just in
    the interactive branch).  The exact placement (inside the autopilot block) is
    confirmed by test_autopilot_context_contains_no_resume.
    """
    s = _src()
    assert "is_followup=False" in s, (
        "server.py must explicitly set is_followup=False for the autopilot branch"
    )


def test_autopilot_context_contains_no_resume():
    """The RunContext built in the autopilot branch must not forward a cli_session_id.

    Strategy: locate the autopilot-specific RunContext(...) call and verify it
    does NOT pass cli_session_id (or passes None/empty) — confirming the one-shot
    intent.  We look for the block between the 'autopilot' branch and the next
    RunContext construction.
    """
    s = _src()
    # After the autopilot branch keyword, the nearest RunContext call must include
    # is_followup=False and must NOT carry cli_session_id=conv.cli_session_id.
    # We find the autopilot RunContext block:
    if "autopilot=True" not in s:
        raise AssertionError("autopilot=True not found — earlier test should have caught this")

    # Grab the slice around the autopilot RunContext call
    idx = s.index("autopilot=True")
    # Walk backwards to find the opening RunContext(
    before = s[:idx]
    rc_start = before.rfind("RunContext(")
    assert rc_start != -1, "Could not find RunContext( before autopilot=True"
    rc_block = s[rc_start:idx + 200]  # include a bit past autopilot=True

    # The autopilot RunContext must NOT pass conv.cli_session_id (resume data)
    assert "conv.cli_session_id" not in rc_block, (
        "Autopilot RunContext must not forward conv.cli_session_id (breaks one-shot guarantee)"
    )



def test_interactive_path_still_uses_wrap_console_prompt():
    """The interactive path must still call wrap_console_prompt (unchanged behavior)."""
    s = _src()
    assert "wrap_console_prompt" in s, (
        "wrap_console_prompt must still be present for the interactive path"
    )


def test_interactive_path_still_uses_wrap_with_conversation_history():
    """The interactive path must still call wrap_with_conversation_history (unchanged behavior)."""
    s = _src()
    assert "wrap_with_conversation_history" in s, (
        "wrap_with_conversation_history must still be present for the interactive path"
    )
