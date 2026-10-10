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


def test_the_run_reports_where_the_agent_wrote_the_app(tmp_path):
    """done.session_dir is Studio's tracking folder (var/dx_agent_dev/sessions/…); the console only showed that,
    so users could not find the app the agent wrote into <project>/dx-agent-dev/<session>/ (2026-10-11)."""
    from core.agent_runner import AgentRunner, MockAdapter

    target = tmp_path / "suite"
    target.mkdir()

    class Writer(MockAdapter):
        def run(self, prompt, session_dir, harness_dirs, run_ctx=None):
            (target / "dx_app" / "dx-agent-dev" / "20261011_demo").mkdir(parents=True)
            yield {"type": "done", "text": "ok", "session_dir": str(session_dir)}

    events = list(AgentRunner(Writer(), tmp_path / "ws").run("x", [str(target)]))
    arts = [e for e in events if e["type"] == "artifacts"]
    assert arts and arts[0]["dirs"] == [str((target / "dx_app/dx-agent-dev/20261011_demo").resolve())]
