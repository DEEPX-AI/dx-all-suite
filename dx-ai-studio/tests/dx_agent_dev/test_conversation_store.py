"""conversation_store unit tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "dx_agent_dev"))

from core.conversation_store import ConversationStore  # noqa: E402


def test_create_and_roundtrip(tmp_path):
    store = ConversationStore(tmp_path)
    conv = store.create(agent="cursor", model="sonnet-4.6")
    conv.add_user("build soccer tracker")
    conv.add_assistant("Which input source?")
    store.bind_session_dir(conv, str(tmp_path / "sess1"))
    store.bind_cli_session(conv, "cli-abc")

    loaded = store.get(conv.id)
    assert loaded is not None
    assert loaded.agent == "cursor"
    assert loaded.cli_session_id == "cli-abc"
    assert loaded.session_dir.endswith("sess1")
    assert len(loaded.turns) == 2
    assert loaded.is_followup is True

    loaded.add_user("1")
    assert loaded.is_followup is True
