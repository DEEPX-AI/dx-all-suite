"""P5b-ext: 동적 agent 모델 조회 — cursor 등 CLI에서 실제 모델 목록을 파싱.

정적 임시목록(예: cursor ["sonnet-4.6","gpt-5"]) 대신 `cursor-agent --list-models`의
실제 목록(auto 포함 수십 개)을 노출한다. 미지원 agent는 None → 정적 목록 폴백.
"""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))

_CURSOR_OUTPUT = """Available models

auto - Auto
gpt-5.3-codex-low - Codex 5.3 Low
gpt-5.3-codex - Codex 5.3
gpt-5.2 - GPT-5.2
sonnet-4.6 - Claude Sonnet 4.6
sonnet-4.6-thinking - Claude Sonnet 4.6 Thinking
"""


def test_cursor_parse_models_extracts_ids():
    from core.adapters.cursor import CursorAdapter
    models = CursorAdapter._parse_models(_CURSOR_OUTPUT)
    assert "auto" in models
    assert "gpt-5.3-codex" in models
    assert "sonnet-4.6-thinking" in models
    assert "Available models" not in models  # header excluded
    assert "" not in models                   # blanks excluded


def test_cursor_list_models_runs_cli(monkeypatch):
    from core.adapters import cursor as cursor_mod
    from core.adapters.cursor import CursorAdapter

    def fake_run(cmd, capture_output=True, text=True, timeout=None):
        assert "--list-models" in cmd
        return SimpleNamespace(stdout=_CURSOR_OUTPUT, returncode=0, stderr="")

    monkeypatch.setattr(cursor_mod.subprocess, "run", fake_run)
    models = CursorAdapter(cli_path="/usr/bin/cursor-agent").list_models()
    assert models and "auto" in models


def test_base_list_models_none_by_default():
    from core.adapters.base import SubprocessAdapter

    class Bare(SubprocessAdapter):
        cli_bin = "x"

    assert Bare(cli_path="/usr/bin/x").list_models() is None


def test_list_agent_models_falls_back_to_static(monkeypatch):
    """동적 조회 불가(None) → agents_config 정적 목록으로 폴백."""
    from core import environment
    # claude는 동적 list_models 미구현 → 정적 목록(claude-*)을 돌려줘야 함
    models = environment.list_agent_models("claude")
    assert isinstance(models, list) and any("claude" in m for m in models)
