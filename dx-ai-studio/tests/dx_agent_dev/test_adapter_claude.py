"""Claude 어댑터: claude -p --add-dir --model --output-format stream-json."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_claude_registered():
    from core.adapters import get_adapter
    from core.adapters.claude import ClaudeAdapter
    assert get_adapter("claude") is ClaudeAdapter


def test_claude_build_command(tmp_path):
    from core.adapters import make_adapter
    a = make_adapter("claude", model="claude-sonnet-4-6")
    cmd = a.build_command("build x", tmp_path, ["/h1"])
    assert "-p" in cmd and "build x" in cmd
    assert "--add-dir" in cmd
    assert str(tmp_path) in cmd and "/h1" in cmd
    assert "--model" in cmd and "claude-sonnet-4-6" in cmd
    assert "--output-format" in cmd and "stream-json" in cmd


def test_claude_cwd_mode_harness(tmp_path):
    """Faithful to .deepx/e2e/test.sh: cwd = target workdir (harness_dirs[0]),
    so the agent discovers project CLAUDE.md + .claude/skills."""
    from core.adapters import make_adapter
    a = make_adapter("claude")
    assert a._resolve_cwd(tmp_path, ["/h"]) == "/h"


def test_claude_normalize_invalid_json_message_fallback():
    from core.adapters.claude import ClaudeAdapter
    a = ClaudeAdapter()
    ev = a.normalize("plain text line")
    assert ev["type"] == "message"
    assert ev["text"] == "plain text line"
