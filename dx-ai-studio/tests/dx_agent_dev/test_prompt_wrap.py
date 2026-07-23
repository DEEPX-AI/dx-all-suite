"""Console prompt wrapping for web chat UX."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "dx_agent_dev"))

from core.prompt_wrap import wrap_autopilot_prompt, wrap_console_prompt  # noqa: E402


def test_wraps_user_prompt_with_console_rules():
    out = wrap_console_prompt("축구 선수 추적 앱 만들고 싶어")
    assert out.startswith("[DX Agent Dev Console")
    assert "축구 선수 추적" in out


def test_followup_skips_console_rules():
    out = wrap_console_prompt("1", is_followup=True)
    assert out == "1"
    assert "[DX Agent Dev Console" not in out


def test_idempotent_when_already_wrapped():
    once = wrap_console_prompt("hello")
    twice = wrap_console_prompt(once)
    assert twice == once


def test_autopilot_directive_present_and_no_console_ux():
    out = wrap_autopilot_prompt("Compile yolo11n")
    assert "Compile yolo11n" in out
    assert "do not ask" in out.lower() and "default" in out.lower()
    assert "[DX Agent Dev Console" not in out  # not the interactive wrap


def test_autopilot_idempotent_and_empty():
    assert wrap_autopilot_prompt("") == ""
    once = wrap_autopilot_prompt("x")
    assert wrap_autopilot_prompt(once) == once  # no double-prepend


def test_console_wrap_still_interactive():
    assert "[DX Agent Dev Console" in wrap_console_prompt("hi")
