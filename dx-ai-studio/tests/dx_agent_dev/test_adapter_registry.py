"""Adapter registry: class lookup and instance creation with a bound model."""
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
    # copilot defaults to "auto" (the CLI picks): which models an account may use differs per plan
    # and org policy, and a fixed default such as claude-sonnet-4.6 may not be offered to the
    # account. The account's own default arrives with its model list (ACP).
    assert a.model == "auto"


def test_make_adapter_explicit_model():
    from core.adapters import make_adapter
    a = make_adapter("copilot", model="whatever")
    assert a.model == "whatever"
    assert a.name == "copilot"


def test_make_adapter_unknown_returns_none():
    from core.adapters import make_adapter
    assert make_adapter("nope") is None
