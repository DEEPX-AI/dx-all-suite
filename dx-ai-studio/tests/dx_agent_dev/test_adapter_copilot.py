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
