"""Coding-agent CLIs on this PC: which are installed and logged in, and which one Studio uses.

Chat (shared/chat) and Agent Dev (dx_agent_dev) both read this, so the login rules live in one place.
shared must not import dx_agent_dev (layering).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from pathlib import Path

# Preference order when nothing was chosen (same as dx_agent_dev's degraded order and the chat CLI fallback).
AGENT_ORDER = ("claude", "copilot", "cursor", "codex", "opencode")
BINS = {"claude": "claude", "copilot": "copilot", "cursor": "cursor-agent", "codex": "codex", "opencode": "opencode"}
LOGIN_HINTS = {"claude": "claude", "copilot": "copilot login", "cursor": "cursor-agent login",
               "codex": "codex login", "opencode": "opencode auth login"}
_MODEL_MAX = 200

# Not an installed CLI but an "install it?" prompt that VS Code's Copilot Chat puts on PATH. Running it stops at
# "Cannot find GitHub Copilot CLI … Install? [y/N]".
_INSTALL_SHIMS = ("/github.copilot-chat/copilotCli/",)


def _is_shim(path) -> bool:
    return any(s in str(path).replace(os.sep, "/") for s in _INSTALL_SHIMS)


def find_cli(binary: str) -> str | None:
    """shutil.which, skipping install shims; if a shim is found first, look again on PATH without it."""
    found = shutil.which(binary)
    if not found or not _is_shim(found):
        return found
    rest = [d for d in os.environ.get("PATH", "").split(os.pathsep)
            if d and not _is_shim(os.path.join(d, binary))]
    return shutil.which(binary, path=os.pathsep.join(rest)) if rest else None


def installed(name: str) -> str | None:
    binary = BINS.get(name)
    return find_cli(binary) if binary else None


def _json_flag(rel: tuple, key: str):
    path = Path.home().joinpath(*rel)
    try:
        if not path.is_file():
            return False
        text = re.sub(r"^\s*//.*$", "", path.read_text(encoding="utf-8"), flags=re.M)
        return bool(json.loads(text).get(key))
    except (ValueError, OSError, AttributeError):
        return None


def authenticated(name: str):
    """True / False when a cheap check is certain, None when it cannot tell (never a false "logged out")."""
    if name == "claude":
        return _json_flag((".claude", ".credentials.json"), "claudeAiOauth")
    if name == "cursor":
        return _json_flag((".cursor", "cli-config.json"), "authInfo")
    if name == "copilot":
        # `copilot login` keeps the token in the OS keyring and lists the account in ~/.copilot/config.json.
        if any(os.environ.get(v) for v in ("COPILOT_GITHUB_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")):
            return True
        return _json_flag((".copilot", "config.json"), "loggedInUsers")
    return None


def detect() -> list[dict]:
    rows = []
    for name in AGENT_ORDER:
        is_in = bool(installed(name))
        rows.append({"name": name, "installed": is_in,
                     "authenticated": authenticated(name) if is_in else None,
                     "login_hint": LOGIN_HINTS[name]})
    return rows


def _config_dir() -> Path:
    d = os.environ.get("DX_CHAT_CONFIG_DIR")
    return Path(d) if d else Path.home() / ".dx-ai-studio"


def _studio_path() -> Path:
    return _config_dir() / "agent.json"


def studio_agent() -> dict | None:
    """The agent picked in Home or Agent Dev, or None when nobody picked one."""
    try:
        data = json.loads(_studio_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or data.get("agent") not in BINS:
        return None
    model = data.get("model")
    return {"agent": data["agent"], "model": model if isinstance(model, str) and model else None}


def set_studio_agent(agent: str, model: str | None) -> None:
    if agent not in BINS:
        raise ValueError(f"unknown agent: {agent!r}")
    if model is not None and (not isinstance(model, str) or len(model) > _MODEL_MAX):
        raise ValueError("model must be a string of at most 200 characters")
    path = _studio_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".agent.", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"agent": agent, "model": model or None}, f)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def resolve_chat_source(config: dict | None) -> dict:
    """Which AI answers Chat: saved config > Studio agent > first logged-in CLI > first unknown-login CLI > none."""
    if config and config.get("provider"):
        provider = config["provider"]
        model = config.get("model")
        agent = (model or "").split("::")[0] or None if provider == "agent-cli" else None
        return {"kind": "saved", "provider": provider, "agent": agent, "model": model}
    usable = {r["name"]: r for r in detect() if r["installed"]}
    pref = studio_agent()
    if pref and pref["agent"] in usable and usable[pref["agent"]]["authenticated"] is not False:
        return {"kind": "studio", "provider": "agent-cli", "agent": pref["agent"], "model": pref["model"]}
    for want in (True, None):
        for name in AGENT_ORDER:
            row = usable.get(name)
            if row and row["authenticated"] is want:
                return {"kind": "auto", "provider": "agent-cli", "agent": name, "model": None}
    return {"kind": "none", "provider": None, "agent": None, "model": None}
