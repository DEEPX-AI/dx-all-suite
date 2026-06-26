"""
Config schema validation for DX-APP model parameters.

Provides lightweight runtime validation of config.json values.
Warns on invalid values but never raises — maintains backward compatibility.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

CONFIG_SCHEMA: Dict[str, Dict[str, Any]] = {
    "score_threshold":      {"type": (int, float), "min": 0.0, "max": 1.0},
    "nms_threshold":        {"type": (int, float), "min": 0.0, "max": 1.0},
    "obj_threshold":        {"type": (int, float), "min": 0.0, "max": 1.0},
    "confidence_threshold": {"type": (int, float), "min": 0.0, "max": 1.0},
    "top_k":                {"type": int,          "min": 1,   "max": 1000},
    "num_classes":          {"type": int,          "min": 1,   "max": 10000},
    "reg_max":              {"type": int,          "min": 1,   "max": 100},
    "num_protos":           {"type": int,          "min": 1,   "max": 1000},
    "has_background":       {"type": bool},
}


def validate_config(config: Dict[str, Any]) -> List[str]:
    """Validate config values against the known schema.

    Returns a list of warning messages.  Empty list means all values are valid.
    Unknown keys are silently ignored (forward-compatible).
    """
    warnings: List[str] = []
    for key, value in config.items():
        if key not in CONFIG_SCHEMA:
            continue  # unknown keys are allowed for forward compatibility
        schema = CONFIG_SCHEMA[key]
        expected = schema["type"]
        if not isinstance(value, expected):
            type_name = expected.__name__ if isinstance(expected, type) else str(expected)
            warnings.append(
                f"'{key}': expected {type_name}, got {type(value).__name__} ({value!r})"
            )
            continue
        if "min" in schema and value < schema["min"]:
            warnings.append(f"'{key}': value {value} is below minimum {schema['min']}")
        if "max" in schema and value > schema["max"]:
            warnings.append(f"'{key}': value {value} exceeds maximum {schema['max']}")
    return warnings
