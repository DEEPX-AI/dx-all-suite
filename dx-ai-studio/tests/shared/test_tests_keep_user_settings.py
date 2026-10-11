"""Tests never touch the user's own Studio settings (2026-10-11).

Home now saves the picked agent (POST /api/studio/agent) and Chat settings are saved after a test. A browser test
that changes the agent wrote ~/.dx-ai-studio/agent.json of whoever ran the suite. tests/conftest.py points
DX_CHAT_CONFIG_DIR at a temp dir for the whole session; module servers started by tests inherit it.
"""
import os
import tempfile
from pathlib import Path


def test_the_settings_dir_is_a_temp_dir_for_the_session():
    d = os.environ.get("DX_CHAT_CONFIG_DIR")
    assert d, "DX_CHAT_CONFIG_DIR must be set by tests/conftest.py"
    assert Path(d).resolve().is_relative_to(Path(tempfile.gettempdir()).resolve())
    assert not Path(d).resolve().is_relative_to((Path.home() / ".dx-ai-studio").resolve())


def test_studio_agent_writes_land_there():
    from shared import agent_cli
    assert agent_cli._studio_path().parent == Path(os.environ["DX_CHAT_CONFIG_DIR"])
