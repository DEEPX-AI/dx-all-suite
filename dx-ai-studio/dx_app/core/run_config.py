"""Run-page config merge — schema-aligned, forward-compatible with new models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from dx_app.core.config import CPP_DIR, PY_DIR

# Tunable keys the Run UI may send. Unknown keys in config.json are preserved on merge
# but not exposed in the UI until a binding is added.
RUN_TUNABLE_KEYS = frozenset({
    "score_threshold",
    "nms_threshold",
    "obj_threshold",
    "confidence_threshold",
    "top_k",
    "alpha",
})

CONF_SCORE_ALIASES = ("score_threshold", "confidence_threshold", "conf_threshold")


def load_model_config(category: str, model_name: str) -> Dict[str, Any]:
    """Load config.json from cpp/python example dirs (first match wins)."""
    for base in (CPP_DIR, PY_DIR):
        cfp = base / category / model_name / "config.json"
        if cfp.exists():
            try:
                data = json.loads(cfp.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
            except (json.JSONDecodeError, OSError):
                return {}
    return {}


def sanitize_config_overrides(overrides: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Keep only known tunable keys with JSON-serializable scalar values."""
    if not overrides or not isinstance(overrides, dict):
        return {}
    clean: Dict[str, Any] = {}
    for key, value in overrides.items():
        if key not in RUN_TUNABLE_KEYS:
            continue
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            clean[key] = value
        elif isinstance(value, str) and value.strip():
            try:
                if "." in value:
                    clean[key] = float(value)
                else:
                    clean[key] = int(value)
            except ValueError:
                continue
    return clean


def merge_legacy_thresholds(
    config_overrides: Optional[Dict[str, Any]],
    conf_threshold: Optional[float],
    nms_threshold: Optional[float],
) -> Dict[str, Any]:
    """Map legacy conf_threshold / nms_threshold API fields into config_overrides."""
    merged = sanitize_config_overrides(config_overrides)
    if conf_threshold is not None and "score_threshold" not in merged:
        merged["score_threshold"] = conf_threshold
    if nms_threshold is not None and "nms_threshold" not in merged:
        merged["nms_threshold"] = nms_threshold
    return merged


def build_run_config(
    category: str,
    model_name: str,
    config_overrides: Optional[Dict[str, Any]] = None,
    conf_threshold: Optional[float] = None,
    nms_threshold: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """Merge on-disk config.json with UI overrides. None when nothing to pass."""
    overrides = merge_legacy_thresholds(config_overrides, conf_threshold, nms_threshold)
    if not overrides:
        return None
    cfg = dict(load_model_config(category, model_name))
    cfg.update(overrides)
    return cfg
