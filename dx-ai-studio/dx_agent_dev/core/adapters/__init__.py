"""Agent adapter registry.

AGENT_REGISTRY maps a tool name to its adapter class. A new adapter is imported from its own module and
registered in the dict below. The model is bound when make_adapter builds the instance, so run() keeps its arity.
"""
from dx_agent_dev.core.agents_config import AGENTS
from dx_agent_dev.core.adapters.base import AgentAdapter, SubprocessAdapter
from dx_agent_dev.core.adapters.mock import MockAdapter
from dx_agent_dev.core.adapters.copilot import CopilotAdapter
from dx_agent_dev.core.adapters.codex import CodexAdapter
from dx_agent_dev.core.adapters.claude import ClaudeAdapter
from dx_agent_dev.core.adapters.opencode import OpenCodeAdapter
from dx_agent_dev.core.adapters.cursor import CursorAdapter

AGENT_REGISTRY = {
    "copilot": CopilotAdapter,
    "codex": CodexAdapter,
    "claude": ClaudeAdapter,
    "opencode": OpenCodeAdapter,
    "cursor": CursorAdapter,
}


def get_adapter(name):
    """Look up the registry class (None if unknown)."""
    return AGENT_REGISTRY.get(name)


def make_adapter(name, model=None, effort=None):
    """Build an instance from config and bind name/model/effort (None if unknown)."""
    cls = AGENT_REGISTRY.get(name)
    if cls is None:
        return None
    cfg = AGENTS.get(name, {})
    resolved = model or cfg.get("default_model")
    # Bind effort only when the agent supports it; otherwise ignore it.
    efforts = cfg.get("reasoning_efforts", [])
    bound_effort = effort if (effort and effort in efforts) else None
    inst = cls(model=resolved, effort=bound_effort)
    inst.name = name
    return inst


__all__ = ["AgentAdapter", "SubprocessAdapter", "MockAdapter", "CopilotAdapter",
           "CodexAdapter", "ClaudeAdapter", "OpenCodeAdapter", "CursorAdapter",
           "AGENT_REGISTRY", "get_adapter", "make_adapter"]
