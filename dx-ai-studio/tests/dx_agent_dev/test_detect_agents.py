"""설치된 CLI 어댑터 감지 — 드롭다운 동적 노출용(기존 detect_environment와 별개)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_detect_available_agents_returns_list(monkeypatch):
    from core import environment
    # copilot·codex만 설치된 것으로 가정
    installed = {"copilot": "/usr/bin/copilot", "codex": "/usr/bin/codex"}
    monkeypatch.setattr(environment.shutil, "which", lambda n: installed.get(n))
    agents = environment.detect_available_agents()
    names = [a["name"] for a in agents]
    assert "copilot" in names and "codex" in names
    assert "claude" not in names


def test_detect_available_agents_includes_models(monkeypatch):
    from core import environment
    monkeypatch.setattr(environment.shutil, "which", lambda n: "/usr/bin/" + n if n == "claude" else None)
    agents = environment.detect_available_agents()
    assert len(agents) == 1
    a = agents[0]
    assert a["name"] == "claude"
    assert isinstance(a["models"], list) and a["models"]
    assert "default_model" in a


def test_detect_available_agents_empty_when_none(monkeypatch):
    from core import environment
    monkeypatch.setattr(environment.shutil, "which", lambda n: None)
    assert environment.detect_available_agents() == []
