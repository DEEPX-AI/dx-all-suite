"""어댑터 레지스트리: 클래스 조회 + 인스턴스 생성(model 바인딩)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_get_adapter_returns_class():
    from core.adapters import get_adapter
    from core.adapters.copilot import CopilotAdapter
    assert get_adapter("copilot") is CopilotAdapter


def test_get_adapter_unknown_returns_none():
    from core.adapters import get_adapter
    assert get_adapter("nope") is None


def test_make_adapter_binds_name_and_default_model():
    from core.adapters import make_adapter
    a = make_adapter("copilot")
    assert a is not None
    assert a.name == "copilot"
    # copilot now defaults to the original harness model (claude-sonnet-4.6)
    assert a.model == "claude-sonnet-4.6"


def test_make_adapter_explicit_model():
    from core.adapters import make_adapter
    a = make_adapter("copilot", model="whatever")
    assert a.model == "whatever"
    assert a.name == "copilot"


def test_make_adapter_unknown_returns_none():
    from core.adapters import make_adapter
    assert make_adapter("nope") is None
