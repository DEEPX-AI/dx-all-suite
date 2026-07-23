"""Test autopilot flag threading: RunContext.autopilot → copilot --no-ask-user."""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "dx_agent_dev"))

from core.adapters.copilot import CopilotAdapter
from core.run_context import RunContext


def _cmd(autopilot, tmp_path):
    ctx = RunContext(conversation_id="c", autopilot=autopilot)
    return CopilotAdapter("copilot").build_command("p", tmp_path, [tmp_path], ctx)


def test_copilot_autopilot_adds_no_ask(tmp_path):
    assert "--no-ask-user" in _cmd(True, tmp_path)


def test_copilot_interactive_no_flag(tmp_path):
    assert "--no-ask-user" not in _cmd(False, tmp_path)


def test_runcontext_has_autopilot_default_false():
    assert RunContext(conversation_id="c").autopilot is False
