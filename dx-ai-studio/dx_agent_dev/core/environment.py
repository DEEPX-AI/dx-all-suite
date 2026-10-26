"""Detect agent CLIs and harness directories."""
import concurrent.futures
import os
import shutil
import time

from dx_agent_dev.core.config import harness_search_paths

_models_cache = {}      # name -> (ts, models): short-lived cache, CLI queries are costly
_MODELS_TTL = 120.0
# Each adapter's list_models() has its own subprocess timeout (cursor/opencode: 20s), but a cap here
# keeps a (future) implementation without a timeout from blocking the /api/agent/models response.
_MODELS_CALL_TIMEOUT = 15.0


def list_agent_models(name):
    """The agent's selectable model ids (the models of agent_model_info)."""
    return agent_model_info(name)["models"]


def agent_model_info(name):
    """{"models": selectable ids, "default_model": id, "catalog": [{id, name, usage, enabled}] or None}.

    Prefers the adapter's live query and falls back to the static config. CLI queries cost time, so they are
    cached briefly, and a hard timeout (_MODELS_CALL_TIMEOUT) keeps an unresponsive CLI from blocking the endpoint.

    copilot gets the account's list (ACP) and **shows everything but lets only the account's models be picked**:
    catalog = the account list (enabled) + entries only in the static table (enabled False: blocked for this
    account or retired). Plans and company policies differ, so each account may use different models.
    """
    from dx_agent_dev.core.agents_config import AGENTS
    from dx_agent_dev.core.adapters import make_adapter
    now = time.time()
    cached = _models_cache.get(name)
    if cached and (now - cached[0]) < _MODELS_TTL:
        return cached[1]
    cfg = AGENTS.get(name, {})
    info = None
    try:
        adapter = make_adapter(name)
        if adapter is not None:
            # shutdown(wait=False): a hung call must not block this one — don't wait for the worker.
            probe = getattr(adapter, "account_models", None) or adapter.list_models
            pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            try:
                got = pool.submit(probe).result(timeout=_MODELS_CALL_TIMEOUT)
            finally:
                pool.shutdown(wait=False)
            if isinstance(got, dict) and got.get("models"):
                account = got["models"]
                ids = {m["id"] for m in account}
                catalog = list(account) + [{"id": m, "name": m, "usage": None, "enabled": False}
                                           for m in cfg.get("models", []) if m not in ids]
                pickable = [m["id"] for m in account if m["enabled"]]
                info = {"models": pickable, "catalog": catalog,
                        "default_model": got.get("default") if got.get("default") in pickable
                        else (pickable[0] if pickable else cfg.get("default_model"))}
            elif isinstance(got, list) and got:
                info = {"models": got, "catalog": None, "default_model": cfg.get("default_model")}
    except Exception:
        info = None
    if info is None:
        info = {"models": list(cfg.get("models", [])), "catalog": None, "default_model": cfg.get("default_model")}
    _models_cache[name] = (now, info)
    return info

COPILOT_BIN = "copilot"
_HARNESS_MARKER = ".deepx"


def find_harness_dirs():
    """Candidate paths that carry the harness marker (.deepx)."""
    found = []
    for base in harness_search_paths():
        try:
            if base and (base / _HARNESS_MARKER).is_dir():
                found.append(base)
        except OSError:
            continue
    return found


def detect_available_agents():
    """Installed CLI adapters (name/models/default_model/authenticated), for the dynamic dropdown.

    authenticated: True/False (certain) or None (unknown), from the adapter's cheap credential check.
    """
    from dx_agent_dev.core.agents_config import AGENTS
    pinned = os.environ.get("DX_AGENT_DEV_PIN_AGENTS")
    if pinned is not None:
        # Pinned for visual regression: return the given names in order, all logged in, instead of the
        # developer's PATH and login state. Contract: tests/dx_agent_dev/test_agents_can_be_pinned.py
        names = [n.strip() for n in pinned.split(",") if n.strip() in AGENTS]
        return [_agent_entry(n, AGENTS[n], True) for n in names]
    from dx_agent_dev.core.adapters import make_adapter
    from dx_agent_dev.core.adapters.base import find_cli
    out = []
    for name, cfg in AGENTS.items():
        if find_cli(cfg["cli_bin"]):
            try:
                adapter = make_adapter(name)
                authed = adapter.is_authenticated() if adapter else None
            except Exception:
                authed = None
            out.append(_agent_entry(name, cfg, authed))
    return out


def _agent_entry(name, cfg, authed):
    return {
        "name": name,
        "models": list(cfg["models"]),
        "default_model": cfg["default_model"],
        "authenticated": authed,
        "reasoning_efforts": list(cfg.get("reasoning_efforts", [])),
        "default_effort": cfg.get("default_effort"),
    }


def detect_environment():
    """Decide whether runs are possible. DX_AGENT_ADAPTER=mock forces Mock (for checks).

    The result includes "agents" (the detect_available_agents() result) so a caller can reuse it in the
    same request instead of calling detect_available_agents() again. The forced_mock early return skips
    that computation and so has no "agents" key (callers do not use it when forced_mock is set).
    """
    if os.environ.get("DX_AGENT_ADAPTER") == "mock":
        return {"available": True, "forced_mock": True, "cli": None,
                "harness_dirs": [], "reason": None}
    from dx_agent_dev.core.adapters.base import find_cli
    cli = find_cli(COPILOT_BIN)
    # Usable if any agent is installed (claude/codex/cursor/opencode count, not just copilot).
    # detect_available_agents() includes copilot too, so cli is kept only for display and the default.
    agents = detect_available_agents()
    has_agent = bool(agents) or bool(cli)
    harness = find_harness_dirs()
    if not has_agent:
        reason = "cli_missing"
    elif not harness:
        reason = "harness_missing"
    else:
        reason = None
    return {
        "available": has_agent and bool(harness),
        "forced_mock": False,
        "cli": cli,
        "harness_dirs": [str(h) for h in harness],
        "reason": reason,
        "agents": agents,
    }
