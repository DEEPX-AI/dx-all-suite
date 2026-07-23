"""Configuration management for the unified chat engine."""
from __future__ import annotations

import json
import os
import stat
from pathlib import Path

_cached_config: dict | None = None
_cached_mtime: float = 0.0


def get_config_path() -> Path:
    """Return path to chat_config.json, respecting DX_CHAT_CONFIG_DIR env var."""
    config_dir = os.environ.get("DX_CHAT_CONFIG_DIR")
    if config_dir:
        return Path(config_dir) / "chat_config.json"
    return Path.home() / ".dx-ai-studio" / "chat_config.json"


def load_config() -> dict | None:
    """Load config from JSON file. Returns None if missing or corrupted.

    Caches in memory; re-reads only when file mtime changes.
    """
    global _cached_config, _cached_mtime

    path = get_config_path()
    if not path.exists():
        return None

    mtime = path.stat().st_mtime
    if _cached_config is not None and mtime == _cached_mtime:
        return _cached_config

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        print(f"Warning: corrupted config file at {path}")
        return None

    _cached_config = data
    _cached_mtime = mtime
    return _cached_config


def save_config(
    provider: str,
    api_key: str,
    model: str,
    endpoint: str | None = None,
    temperature: float = 0.7,
) -> None:
    """Save config as JSON. Creates parent dir if needed, sets file to 0600."""
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "provider": provider,
        "api_key": api_key,
        "model": model,
        "endpoint": endpoint,
        "temperature": temperature,
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    # Invalidate cache so next load picks up the new data
    global _cached_config, _cached_mtime
    _cached_config = None
    _cached_mtime = 0.0


def mask_api_key(key: str | None) -> str | None:
    """Mask an API key for display.

    None → None
    Short (≤8) → middle replaced with ••
    Long → first 3 + •••• + last 4
    """
    if key is None:
        return None
    if len(key) <= 8:
        if len(key) <= 2:
            return "••"
        return key[0] + "••" + key[-1]
    return key[:3] + "••••" + key[-4:]
