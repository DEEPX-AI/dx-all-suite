"""P5b: reasoning-effort(사고 강도) 컨트롤 — capability-gated.

claude는 `--effort <low|medium|high|xhigh|max>`를 지원(일반망 검증). 미지원 agent는 무시.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_claude_build_command_includes_effort():
    from core.adapters.claude import ClaudeAdapter
    a = ClaudeAdapter(cli_path="/usr/bin/claude", model="claude-sonnet-4-6", effort="high")
    cmd = a.build_command("hi", Path("/tmp/s"), [])
    assert "--effort" in cmd
    assert cmd[cmd.index("--effort") + 1] == "high"


def test_claude_build_command_no_effort_when_unset():
    from core.adapters.claude import ClaudeAdapter
    a = ClaudeAdapter(cli_path="/usr/bin/claude", model="claude-sonnet-4-6")
    assert "--effort" not in a.build_command("hi", Path("/tmp/s"), [])


def test_make_adapter_binds_effort():
    from core.adapters import make_adapter
    a = make_adapter("claude", "claude-sonnet-4-6", effort="medium")
    assert a is not None and a.effort == "medium"


def test_make_adapter_effort_optional():
    from core.adapters import make_adapter
    a = make_adapter("claude", "claude-sonnet-4-6")
    assert a is not None and a.effort is None


def test_detect_available_agents_exposes_reasoning_efforts(monkeypatch):
    from core import environment
    monkeypatch.setattr(
        environment.shutil, "which",
        lambda n: "/usr/bin/" + n if n == "claude" else None,
    )
    agents = environment.detect_available_agents()
    claude = next(a for a in agents if a["name"] == "claude")
    assert "reasoning_efforts" in claude
    assert "high" in claude["reasoning_efforts"]


def test_cursor_build_command_includes_effort_bracket():
    from core.adapters.cursor import CursorAdapter
    a = CursorAdapter(cli_path="/usr/bin/cursor-agent", model="sonnet-4.6", effort="high")
    cmd = a.build_command("hi", Path("/tmp/s"), [])
    assert "--model" in cmd
    assert cmd[cmd.index("--model") + 1] == "sonnet-4.6[effort=high]"


def test_cursor_build_command_skips_bracket_when_model_has_params():
    from core.adapters.cursor import CursorAdapter
    a = CursorAdapter(cli_path="/usr/bin/cursor-agent", model="auto", effort="high")
    cmd = a.build_command("hi", Path("/tmp/s"), [])
    assert cmd[cmd.index("--model") + 1] == "auto"


def test_copilot_exposes_effort(monkeypatch):
    # copilot CLI supports --effort/--reasoning-effort, so it now exposes effort options
    # (previously hidden with an empty list — runtime-verified the flag is accepted).
    # Verbatim from `copilot --help`: none|low|medium|high|xhigh|max.
    from core import environment
    monkeypatch.setattr(
        environment.shutil, "which",
        lambda n: "/usr/bin/" + n if n == "copilot" else None,
    )
    agents = environment.detect_available_agents()
    copilot = next(a for a in agents if a["name"] == "copilot")
    assert copilot.get("reasoning_efforts") == ["none", "low", "medium", "high", "xhigh", "max"]
    assert copilot.get("default_effort") == "medium"


def test_codex_build_command_includes_reasoning_effort_config_override():
    """codex has NO --effort flag — effort goes via -c model_reasoning_effort=<level>."""
    from core.adapters.codex import CodexAdapter
    a = CodexAdapter(cli_path="/usr/bin/codex", model="gpt-5.6-terra", effort="high")
    cmd = a.build_command("hi", Path("/tmp/s"), [])
    assert "--effort" not in cmd
    assert "-c" in cmd
    assert "model_reasoning_effort=high" in cmd
