"""에이전트 어댑터 레지스트리.

AGENT_REGISTRY는 도구명→어댑터 클래스. 신규 어댑터는 자신의 모듈에서 import 후
아래 dict에 등록한다(Chunk 2). model은 make_adapter 생성 시 바인딩 → run arity 불변.
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
    """레지스트리 클래스 조회(없으면 None)."""
    return AGENT_REGISTRY.get(name)


def make_adapter(name, model=None, effort=None):
    """config 기반 인스턴스 생성 + name/model/effort 바인딩(없으면 None)."""
    cls = AGENT_REGISTRY.get(name)
    if cls is None:
        return None
    cfg = AGENTS.get(name, {})
    resolved = model or cfg.get("default_model")
    # effort는 해당 agent가 지원할 때만 바인딩(미지원이면 무시).
    efforts = cfg.get("reasoning_efforts", [])
    bound_effort = effort if (effort and effort in efforts) else None
    inst = cls(model=resolved, effort=bound_effort)
    inst.name = name
    return inst


__all__ = ["AgentAdapter", "SubprocessAdapter", "MockAdapter", "CopilotAdapter",
           "CodexAdapter", "ClaudeAdapter", "OpenCodeAdapter", "CursorAdapter",
           "AGENT_REGISTRY", "get_adapter", "make_adapter"]
