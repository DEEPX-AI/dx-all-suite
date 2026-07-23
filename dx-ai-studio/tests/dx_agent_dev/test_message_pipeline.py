"""message_pipeline unit tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "dx_agent_dev"))

from core.message_pipeline import (  # noqa: E402
    extract_cli_session_event,
    prepare_message_text,
    prepare_sse_event,
)


def test_extract_cli_session_from_system_init():
    ev = extract_cli_session_event({"type": "system", "subtype": "init", "session_id": "abc-123"})
    assert ev["cli_session_id"] == "abc-123"


def test_prepare_message_text_strips_inline_harness():
    raw = "[DX-AGENT-DEV:START]```████ on-device NPU```\n\nHello"
    clean, _ = prepare_message_text(raw, final=True)
    assert "on-device NPU" not in clean
    assert "Hello" in clean


def test_prepare_sse_event_hides_session_type():
    assert prepare_sse_event({"type": "session", "cli_session_id": "x"}) is None


def test_prepare_sse_event_sanitizes_final_message():
    out = prepare_sse_event({
        "type": "message",
        "text": "[DX-AGENT-DEV: START]\n\nReply body",
        "final": True,
    })
    assert out is not None
    assert "[DX-AGENT-DEV" not in out["text"]
    assert "Reply body" in out["text"]
