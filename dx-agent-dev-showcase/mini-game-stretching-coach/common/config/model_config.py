"""
Lightweight JSON configuration loader for model parameters.

Reads a flat JSON config file (config.json) so that Factory parameters
(thresholds, class counts, etc.) can be changed at runtime without
modifying source code.

Usage:
    from common.config import load_config
    config = load_config("config.json")
    # config = {"score_threshold": 0.3, "nms_threshold": 0.45, ...}
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import logging

from .config_schema import validate_config

logger = logging.getLogger(__name__)

class ModelConfig:
    """Simple wrapper around a dict loaded from a JSON file."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self._data: Dict[str, Any] = data or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a typed value with a default fallback."""
        return self._data.get(key, default)

    def as_dict(self) -> Dict[str, Any]:
        """Return the raw dictionary (for passing to Factory(config=...))."""
        return dict(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    def __repr__(self) -> str:
        return f"ModelConfig({self._data})"

    @classmethod
    def from_file(cls, path: str, verbose: bool = False) -> "ModelConfig":
        """Load config from a JSON file.  Returns empty config if file is missing."""
        if not os.path.isfile(path):
            return cls()
        with open(path, "r") as f:
            data = json.load(f)
        warnings = validate_config(data)
        for w in warnings:
            logger.warning(f"Config {path}: {w}")
        if verbose:
            logger.info(f"Config loaded: {path} ({len(data)} keys)")
        return cls(data)


def load_config(path: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Load a JSON config file and return a plain dict.

    Returns an empty dict if the file does not exist.
    This is the simplest entry point — pass the result directly
    to ``Factory(config=...)``.
    """
    if not os.path.isfile(path):
        return {}
    with open(path, "r") as f:
        data = json.load(f)
    warnings = validate_config(data)
    for w in warnings:
        logger.warning(f"Config {path}: {w}")
    if verbose:
        logger.info(f"Config loaded: {path} ({len(data)} keys)")
    return data


def find_config(model_file: str, config_name: str = "config.json") -> Optional[str]:
    """
    Auto-discover config.json relative to a model script.

    Searches the directory containing *model_file* and its parent
    for *config_name*.  Returns the path if found, else None.
    """
    base_dir = Path(model_file).resolve().parent
    candidate = base_dir / config_name
    if candidate.is_file():
        return str(candidate)
    # Try parent (in case script is in a subdirectory)
    candidate = base_dir.parent / config_name
    if candidate.is_file():
        return str(candidate)
    return None
