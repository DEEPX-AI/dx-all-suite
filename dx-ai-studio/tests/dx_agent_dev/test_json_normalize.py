"""stream-json / result 이벤트 → UI 슬롯 매핑 계약."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_system_init_emits_session_event():
    from core.adapters.base import _map_json_event
    import json

    raw = json.dumps({"type": "system", "subtype": "init", "session_id": "sess-1", "model": "auto"})
    ev = _map_json_event(json.loads(raw), raw)
    assert ev["type"] == "session"
    assert ev["cli_session_id"] == "sess-1"
    assert "Session started" in ev["status_text"]


def test_result_event_extracts_result_field():
    from core.adapters.base import _map_json_event

    raw = json.dumps({"type": "result", "subtype": "success", "result": "Hello **world**"})
    ev = _map_json_event(json.loads(raw), raw)
    assert ev["type"] == "message"
    assert ev["text"] == "Hello **world**"
    assert ev.get("final") is True


def test_result_event_does_not_dump_raw_json():
    from core.adapters.base import _map_json_event

    obj = {"type": "result", "subtype": "success", "duration_ms": 1000, "usage": {}}
    raw = json.dumps(obj)
    ev = _map_json_event(obj, raw)
    assert ev["type"] == "status"
    assert "duration" in ev["text"].lower() or "Finished" in ev["text"]


def test_connection_lost_is_status_not_message():
    from core.adapters.base import classify_plain_line

    ev = classify_plain_line("Connection lost, reconnecting to https://example (attempt 1)...")
    assert ev["type"] == "status"
    assert "Connection lost" in ev["text"]


def test_assistant_stream_json_message():
    from core.adapters.base import _map_json_event

    obj = {
        "type": "assistant",
        "message": {"role": "assistant", "content": [{"type": "text", "text": "Plan A"}]},
    }
    raw = json.dumps(obj)
    ev = _map_json_event(obj, raw)
    assert ev["type"] == "message"
    assert ev["text"] == "Plan A"


def test_tool_call_goes_to_command():
    from core.adapters.base import _map_json_event

    obj = {"type": "tool_call", "subtype": "started", "tool_call": {"shellToolCall": {"name": "bash"}}}
    raw = json.dumps(obj)
    ev = _map_json_event(obj, raw)
    assert ev["type"] == "command"


def test_user_event_hidden():
    from core.adapters.base import _map_json_event

    obj = {"type": "user", "message": {"content": [{"type": "text", "text": "hi"}]}}
    ev = _map_json_event(obj, json.dumps(obj))
    assert ev.get("hidden") is True


def test_claude_stream_event_text_delta():
    from core.adapters.base import _map_json_event

    obj = {
        "type": "stream_event",
        "event": {"delta": {"type": "text_delta", "text": "Hello"}},
    }
    ev = _map_json_event(obj, json.dumps(obj))
    assert ev["type"] == "message"
    assert ev["text"] == "Hello"
    assert ev.get("delta") is True


def test_claude_assistant_tool_use_goes_to_command():
    from core.adapters.base import _map_json_event

    obj = {
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [{"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}],
        },
    }
    ev = _map_json_event(obj, json.dumps(obj))
    assert ev["type"] == "command"
    assert "Bash" in ev["text"]


def test_codex_thread_started_is_status():
    from core.adapters.base import _map_json_event

    obj = {"type": "thread.started", "model": "gpt-5-codex"}
    ev = _map_json_event(obj, json.dumps(obj))
    assert ev["type"] == "status"
    assert "gpt-5-codex" in ev["text"]


def test_codex_agent_message_delta():
    from core.adapters.base import _map_json_event

    obj = {
        "type": "item.completed",
        "item": {"type": "agent_message", "text": "Building app"},
    }
    ev = _map_json_event(obj, json.dumps(obj))
    assert ev["type"] == "message"
    assert ev["text"] == "Building app"
    assert ev.get("delta") is True


def test_codex_command_execution():
    from core.adapters.base import _map_json_event

    obj = {
        "type": "item.completed",
        "item": {"type": "command_execution", "command": "npm test"},
    }
    ev = _map_json_event(obj, json.dumps(obj))
    assert ev["type"] == "command"
    assert "npm test" in ev["text"]
