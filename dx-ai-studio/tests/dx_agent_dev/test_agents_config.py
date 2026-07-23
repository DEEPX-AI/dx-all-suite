"""에이전트 설정 테이블 계약."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))

EXPECTED_AGENTS = {"copilot", "codex", "claude", "opencode", "cursor"}


def test_all_five_agents_present():
    from core.agents_config import AGENTS
    assert set(AGENTS) == EXPECTED_AGENTS


def test_each_agent_has_contract_keys():
    from core.agents_config import AGENTS
    for name, cfg in AGENTS.items():
        for k in ("cli_bin", "models", "default_model", "output_format"):
            assert k in cfg, f"{name} missing {k}"
        assert isinstance(cfg["models"], list)
        assert cfg["output_format"] in ("text", "json", "stream-json")


def test_default_model_in_models_or_none():
    from core.agents_config import AGENTS
    for name, cfg in AGENTS.items():
        if cfg["default_model"] is not None:
            assert cfg["default_model"] in cfg["models"], name


def test_model_short_maps_are_strings():
    from core.agents_config import MODEL_SHORT
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in MODEL_SHORT.items())
