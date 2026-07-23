"""Detect the dx-agent-dev/<session>/ dir the agent creates per CLAUDE.md
(mirrors the original test.sh detect_new_sessions)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_detect_session_dirs_finds_subproject_session(tmp_path):
    from core.agent_runner import detect_session_dirs
    # agent writes to <target>/<sub>/<subsub>/dx-agent-dev/<session>/ per CLAUDE.md
    base = tmp_path / "dx-runtime" / "dx_app" / "dx-agent-dev"
    base.mkdir(parents=True)
    before = detect_session_dirs(tmp_path)
    new = base / "20260622-120000_claude_opus48_demo"
    new.mkdir()
    after = detect_session_dirs(tmp_path)
    fresh = after - before
    assert str(new.resolve()) in fresh


def test_detect_session_dirs_direct_child(tmp_path):
    from core.agent_runner import detect_session_dirs
    d = tmp_path / "dx-agent-dev" / "20260622-130000_cursor_auto_soccer"
    d.mkdir(parents=True)
    found = detect_session_dirs(tmp_path)
    assert str(d.resolve()) in found


def test_detect_session_dirs_empty_when_none(tmp_path):
    from core.agent_runner import detect_session_dirs
    assert detect_session_dirs(tmp_path) == set()


def test_detect_session_dirs_missing_target_is_safe():
    from core.agent_runner import detect_session_dirs
    assert detect_session_dirs("/nonexistent/path/xyz") == set()
