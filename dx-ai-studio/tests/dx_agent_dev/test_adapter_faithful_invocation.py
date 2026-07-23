"""Faithful replication of the original .deepx/e2e/test.sh invocation:
per-tool full-permission flag + harness cwd (so the agent discovers CLAUDE.md / .claude/skills
from the project workdir, exactly like `cd "$_workdir" && <cli> <perm-flag> ...`)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def _cmd(name, **kw):
    from core.adapters import make_adapter
    a = make_adapter(name, **kw)
    return a, a.build_command("do x", Path("/tmp/sess"), ["/harness"])


def test_claude_skip_permissions_and_harness():
    from core.adapters.claude import ClaudeAdapter
    _a, cmd = _cmd("claude", model="sonnet-4.6")
    assert "--dangerously-skip-permissions" in cmd
    assert ClaudeAdapter.cwd_mode == "harness"


def test_copilot_yolo_and_harness():
    from core.adapters.copilot import CopilotAdapter
    _a, cmd = _cmd("copilot")
    assert "--yolo" in cmd
    assert CopilotAdapter.cwd_mode == "harness"


def test_codex_full_access_harness():  # regression — already faithful
    from core.adapters.codex import CodexAdapter
    _a, cmd = _cmd("codex", model="gpt-5")
    assert "danger-full-access" in cmd
    assert CodexAdapter.cwd_mode == "harness"


def test_cursor_force_trust_harness():  # regression — already faithful
    from core.adapters.cursor import CursorAdapter
    _a, cmd = _cmd("cursor", model="auto")
    assert "--force" in cmd and "--trust" in cmd
    assert CursorAdapter.cwd_mode == "harness"


def test_opencode_skip_permissions_and_harness():
    # opencode `run` supports --dangerously-skip-permissions; pass it for full-autonomy
    # parity (claude/copilot/cursor all run with full perms) and to avoid a headless
    # permission-prompt hang.
    from core.adapters.opencode import OpenCodeAdapter
    _a, cmd = _cmd("opencode", model="github-copilot/claude-haiku-4.5")
    assert "--dangerously-skip-permissions" in cmd
    assert OpenCodeAdapter.cwd_mode == "harness"


def test_harness_cwd_resolves_to_target(tmp_path):
    """In harness mode, cwd is the target workdir (harness_dirs[0]), not the session dir."""
    from core.adapters import make_adapter
    a = make_adapter("claude", model="sonnet-4.6")
    sess = tmp_path / "sess"
    tgt = tmp_path / "tgt"
    assert str(a._resolve_cwd(sess, [str(tgt)])) == str(tgt)
