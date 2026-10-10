"""Copilot 어댑터 build_command 계약 + 경로 생성자 하위호환."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_copilot_path_constructor_preserved():
    """기존 CopilotAdapter('/usr/bin/copilot') 위치인자 생성자 유지."""
    from core.adapters.copilot import CopilotAdapter
    a = CopilotAdapter("/usr/bin/copilot")
    assert a._cli == "/usr/bin/copilot"
    assert a.is_available() is True


def test_copilot_build_command_has_add_dir_and_yolo(tmp_path):
    from core.adapters.copilot import CopilotAdapter
    a = CopilotAdapter("/usr/bin/copilot")
    cmd = a.build_command("build x", tmp_path, ["/h1"])
    assert cmd[0] == "/usr/bin/copilot"
    assert "-p" in cmd and "build x" in cmd
    assert "--add-dir" in cmd
    assert str(tmp_path) in cmd and "/h1" in cmd
    # Faithful to the original `copilot -i ... --yolo`: full tool autonomy.
    assert "--yolo" in cmd


def test_copilot_cwd_mode_harness(tmp_path):
    """Faithful: cwd = target workdir (harness_dirs[0]), not the isolated session dir."""
    from core.adapters.copilot import CopilotAdapter
    a = CopilotAdapter("/usr/bin/copilot")
    assert a._resolve_cwd(tmp_path, ["/h"]) == "/h"


def test_mock_adapter_moved_and_compatible(tmp_path):
    from core.adapters.mock import MockAdapter
    events = list(MockAdapter().run("x", tmp_path, []))
    assert events[-1]["type"] == "done"
    assert MockAdapter().is_available() is True
    # name 미설정 → session_id uuid 폴백 대상
    assert getattr(MockAdapter(), "name", None) is None


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "copilot_output_json.jsonl"


def _events(lines):
    from core.adapters.copilot import CopilotAdapter
    a = CopilotAdapter("/usr/bin/copilot")
    return [a.normalize(l) for l in lines]


def _visible(events, kind):
    return [e for e in events if e.get("type") == kind and not e.get("hidden")]


def test_copilot_runs_with_json_output(tmp_path):
    """Text mode handed the whole CLI transcript (● tool lines, │ commands, tool output, the
    "AI Credits / Tokens / Resume" footer) to the chat as one assistant reply, and the Activity
    panel stayed empty. JSONL separates them."""
    from core.adapters.copilot import CopilotAdapter
    cmd = CopilotAdapter("/usr/bin/copilot").build_command("build x", tmp_path, ["/h1"])
    i = cmd.index("--output-format")
    assert cmd[i + 1] == "json"


def test_copilot_json_events_map_to_command_log_and_reply():
    """Real `copilot -p … --output-format json` output (fixture recorded from copilot CLI)."""
    events = _events(FIXTURE.read_text(encoding="utf-8").splitlines())

    assert [e["text"] for e in _visible(events, "command")] == ["→ bash: echo hello-dx"]
    assert any("hello-dx" in e["text"] for e in _visible(events, "log"))
    deltas = "".join(e["text"] for e in _visible(events, "message") if e.get("delta"))
    assert deltas == 'The command executed successfully and output "hello-dx".'
    finals = [e for e in _visible(events, "message") if e.get("final")]
    assert [e["text"] for e in finals] == ['The command executed successfully and output "hello-dx".']
    assert any(e.get("type") == "status" and "claude-haiku-4.5" in e.get("text", "")
               for e in events if not e.get("hidden"))
    assert not _visible(events, "error")
    for e in _visible(events, "message"):
        assert not e["text"].lstrip().startswith("{"), "raw JSON must not reach the chat"


def test_copilot_turns_are_separated_and_a_failed_result_is_an_error():
    import json
    lines = [json.dumps(o) for o in (
        {"type": "assistant.message_start", "data": {"messageId": "a"}},
        {"type": "assistant.message_delta", "data": {"messageId": "a", "deltaContent": "Checking."}},
        {"type": "assistant.message", "data": {"messageId": "a", "content": "Checking."}},
        {"type": "assistant.message_start", "data": {"messageId": "b"}},
        {"type": "assistant.message_delta", "data": {"messageId": "b", "deltaContent": "Done."}},
        {"type": "assistant.message", "data": {"messageId": "b", "content": "Done."}},
        {"type": "result", "exitCode": 1, "sessionId": "s"},
    )]
    events = _events(lines)
    deltas = "".join(e["text"] for e in _visible(events, "message") if e.get("delta"))
    assert deltas == "Checking.\n\nDone."
    assert _visible(events, "error")


def test_copilot_plain_lines_still_work():
    """stderr is merged into stdout: a warning line is not JSON and must not crash the run."""
    ev = _events(["Warning: something odd"])[0]
    assert ev["type"] in ("message", "status", "log", "command")
