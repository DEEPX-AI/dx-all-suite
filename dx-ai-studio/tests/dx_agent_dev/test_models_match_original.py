"""Models + reasoning-effort per agent must match the original .deepx/e2e/test.sh:
  claude   default claude-sonnet-4-6 (+ --effort supported)
  copilot  default claude-sonnet-4.6, passes --model
  opencode default github-copilot/claude-sonnet-4.6, lists models dynamically
  cursor   dynamic list (cursor-agent --list-models), effort via bracket
"""
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_claude_default_and_effort():
    from core.agents_config import AGENTS
    assert AGENTS["claude"]["default_model"] == "claude-sonnet-4-6"
    assert AGENTS["claude"]["reasoning_efforts"]  # --effort supported


def test_copilot_exposes_model_and_passes_it():
    from core.agents_config import AGENTS
    assert AGENTS["copilot"]["default_model"] == "claude-sonnet-4.6"  # original default
    assert "claude-sonnet-4.6" in AGENTS["copilot"]["models"]
    from core.adapters import make_adapter
    cmd = make_adapter("copilot", model="claude-sonnet-4.6").build_command("x", Path("/s"), ["/h"])
    assert "--model" in cmd and "claude-sonnet-4.6" in cmd


def test_opencode_default_matches_original():
    from core.agents_config import AGENTS
    assert AGENTS["opencode"]["default_model"] == "github-copilot/claude-sonnet-4.6"
    # static fallback must use REAL providers (github-copilot/…), not anthropic/openai
    assert all("/" in m for m in AGENTS["opencode"]["models"])
    assert any(m.startswith("github-copilot/") for m in AGENTS["opencode"]["models"])


def test_opencode_lists_models_dynamically():
    from core.adapters.opencode import OpenCodeAdapter
    from core.adapters.base import SubprocessAdapter
    # opencode overrides list_models (dynamic `opencode models`), not the base None stub
    assert OpenCodeAdapter.list_models is not SubprocessAdapter.list_models


@pytest.mark.skipif(not shutil.which("opencode"), reason="opencode not installed")
def test_opencode_dynamic_list_returns_real_models():
    from core.adapters import make_adapter
    models = make_adapter("opencode").list_models()
    assert models and any("github-copilot/" in m for m in models)


def test_claude_lists_full_model_set():
    """claude CLI has no model-list command → static set must be the full current
    catalog (alias/full-name both accepted by `claude --model`), not a 3-item stub."""
    from core.agents_config import AGENTS
    models = AGENTS["claude"]["models"]
    # flagship + current tiers all present
    for m in ("claude-opus-4-8", "claude-sonnet-4-6", "claude-haiku-4-5", "claude-fable-5"):
        assert m in models, f"{m} missing from claude model list"
    assert len(models) >= 6


def test_copilot_lists_full_model_set():
    """copilot CLI has no model-list command → static set derived from the live
    github-copilot provider catalog (Anthropic + OpenAI + Gemini families)."""
    from core.agents_config import AGENTS
    models = AGENTS["copilot"]["models"]
    assert "auto" in models
    assert "claude-sonnet-4.6" in models  # original default preserved
    assert any(m.startswith("claude-opus-4.") for m in models)
    assert any(m.startswith("gpt-") for m in models)
    assert any(m.startswith("gemini-") for m in models)
    assert len(models) >= 8


def test_copilot_exposes_reasoning_effort():
    """copilot CLI supports --effort/--reasoning-effort → expose it (was hidden: empty)."""
    from core.agents_config import AGENTS
    assert AGENTS["copilot"]["reasoning_efforts"]      # non-empty
    assert AGENTS["copilot"]["default_effort"]
    from core.adapters import make_adapter
    cmd = make_adapter("copilot", model="claude-sonnet-4.6", effort="medium").build_command(
        "x", Path("/s"), ["/h"])
    assert "--effort" in cmd and "medium" in cmd


def test_opencode_exposes_reasoning_effort_via_variant():
    """opencode CLI supports --variant (provider reasoning effort) → expose it."""
    from core.agents_config import AGENTS
    assert AGENTS["opencode"]["reasoning_efforts"]     # non-empty
    assert AGENTS["opencode"]["default_effort"]
    from core.adapters import make_adapter
    cmd = make_adapter("opencode", model="github-copilot/claude-sonnet-4.6",
                       effort="high").build_command("x", Path("/s"), ["/h"])
    assert "--variant" in cmd and "high" in cmd
