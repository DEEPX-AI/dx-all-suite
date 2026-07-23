"""OpenCode 어댑터: opencode run -m, cwd=harness, 텍스트 출력."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_opencode_registered():
    from core.adapters import get_adapter
    from core.adapters.opencode import OpenCodeAdapter
    assert get_adapter("opencode") is OpenCodeAdapter


def test_opencode_build_command(tmp_path):
    from core.adapters import make_adapter
    a = make_adapter("opencode", model="anthropic/claude-sonnet-4-6")
    cmd = a.build_command("build x", tmp_path, ["/harness"])
    assert "run" in cmd and "build x" in cmd
    assert "-m" in cmd and "anthropic/claude-sonnet-4-6" in cmd


def test_opencode_cwd_mode_harness(tmp_path):
    from core.adapters import make_adapter
    a = make_adapter("opencode")
    assert a._resolve_cwd(tmp_path, ["/harness"]) == "/harness"


def test_opencode_normalize_text_heuristic():
    """텍스트 출력 도구: 기본 휴리스틱 상속."""
    from core.adapters.opencode import OpenCodeAdapter
    a = OpenCodeAdapter()
    assert a.normalize("$ run")["type"] == "command"
    assert a.normalize("doing work")["type"] == "message"
