"""dx_agent_dev 환경 감지 테스트."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_detect_returns_contract_keys():
    from core import environment
    env = environment.detect_environment()
    for k in ("available", "cli", "harness_dirs", "reason"):
        assert k in env


def test_unavailable_when_cli_missing(monkeypatch):
    monkeypatch.delenv("DX_AGENT_ADAPTER", raising=False)  # mock 우선분기 중화 → 실제 감지 검증
    from core import environment
    monkeypatch.setattr(environment.shutil, "which", lambda _: None)
    env = environment.detect_environment()
    assert env["available"] is False
    assert env["reason"] == "cli_missing"


def test_unavailable_when_harness_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("DX_AGENT_ADAPTER", raising=False)  # mock 우선분기 중화
    from core import environment
    monkeypatch.setattr(environment.shutil, "which", lambda _: "/usr/bin/copilot")
    monkeypatch.setattr(environment, "find_harness_dirs", lambda: [])
    env = environment.detect_environment()
    assert env["available"] is False
    assert env["reason"] == "harness_missing"


def test_available_when_both_present(monkeypatch, tmp_path):
    monkeypatch.delenv("DX_AGENT_ADAPTER", raising=False)  # mock 우선분기 중화
    from core import environment
    (tmp_path / ".deepx").mkdir()
    monkeypatch.setattr(environment.shutil, "which", lambda _: "/usr/bin/copilot")
    monkeypatch.setattr(environment, "harness_search_paths", lambda: [tmp_path])
    env = environment.detect_environment()
    assert env["available"] is True
    assert str(tmp_path) in env["harness_dirs"]


def test_force_mock_env(monkeypatch):
    monkeypatch.setenv("DX_AGENT_ADAPTER", "mock")
    from core import environment
    env = environment.detect_environment()
    assert env["available"] is True
    assert env["forced_mock"] is True
