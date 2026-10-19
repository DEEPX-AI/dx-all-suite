"""Structured session_id: YYYYMMDD-HHMMSS_<agent>_<model>_default_chat with an agent, a uuid without one."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


class NamedAdapter:
    def __init__(self, name, model):
        self.name = name
        self.model = model

    def is_available(self): return True
    def run(self, p, s, h, run_ctx=None):
        yield {"type": "done", "text": "ok"}
    def cancel(self): pass


def test_structured_session_id_with_agent(tmp_path):
    from core.agent_runner import AgentRunner
    runner = AgentRunner(NamedAdapter("claude", "claude-sonnet-4-6"), tmp_path)
    list(runner.run("build x", []))
    sessions = [p.name for p in tmp_path.iterdir()]
    assert len(sessions) == 1
    sid = sessions[0]
    assert "_claude_" in sid
    assert "sonnet46" in sid  # MODEL_SHORT mapping
    assert sid.endswith("_default_chat") or "_default_chat" in sid
    assert re.match(r"\d{8}-\d{6}_", sid)
    assert "_auto_" not in sid  # harness naming rule


def test_uuid_fallback_when_no_name(tmp_path):
    """An adapter without a name (Mock/default) falls back to a uuid4 hex."""
    from core.agent_runner import AgentRunner
    from core.adapters.mock import MockAdapter
    runner = AgentRunner(MockAdapter(), tmp_path)
    list(runner.run("x", []))
    sessions = [p.name for p in tmp_path.iterdir()]
    assert len(sessions) == 1
    assert re.fullmatch(r"[0-9a-f]{32}", sessions[0])  # uuid4().hex


def test_session_id_unknown_model_uses_raw(tmp_path):
    from core.agent_runner import AgentRunner
    runner = AgentRunner(NamedAdapter("codex", "exotic-model-x"), tmp_path)
    list(runner.run("x", []))
    sid = [p.name for p in tmp_path.iterdir()][0]
    assert "exotic-model-x" in sid
