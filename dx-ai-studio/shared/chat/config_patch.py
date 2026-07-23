"""Apply structured patches to compiler config.json objects."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

CONFIG_JSON_FIELDS = frozenset({
    "inputs",
    "dataset_path",
    "calibration_num",
    "calibration_method",
    "file_extensions",
})


def _set_nested(obj: dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    cur = obj
    for key in parts[:-1]:
        nxt = cur.get(key)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[key] = nxt
        cur = nxt
    cur[parts[-1]] = value


def apply_config_patches(config: dict[str, Any], patches: list[dict[str, Any]]) -> dict[str, Any]:
    """Return new config dict with config_json target patches applied."""
    out = deepcopy(config)
    for patch in patches:
        if patch.get("target") != "config_json":
            continue
        field = patch.get("field", "")
        value = patch.get("value")
        if field == "inputs" and isinstance(value, dict):
            out["inputs"] = value
        elif field == "dataset_path" and isinstance(value, str):
            dl = out.setdefault("default_loader", {})
            if isinstance(dl, dict):
                dl["dataset_path"] = value
        elif field == "calibration_num":
            try:
                out["calibration_num"] = int(value)
            except (TypeError, ValueError):
                continue
        elif field == "calibration_method" and isinstance(value, str):
            out["calibration_method"] = value
        elif field == "file_extensions" and isinstance(value, list):
            dl = out.setdefault("default_loader", {})
            if isinstance(dl, dict):
                dl["file_extensions"] = value
        elif "." in field:
            _set_nested(out, field, value)
    return out


def validate_config_json_patch(patch: dict[str, Any]) -> dict[str, Any] | None:
    field = patch.get("field")
    if field not in CONFIG_JSON_FIELDS and "." not in str(field):
        return None
    value = patch.get("value")
    if field == "inputs" and not isinstance(value, dict):
        return None
    if field == "dataset_path" and not isinstance(value, str):
        return None
    if field == "calibration_method" and not isinstance(value, str):
        return None
    if field == "calibration_num":
        try:
            value = int(value)
        except (TypeError, ValueError):
            return None
    reason = patch.get("reason", "")
    return {
        "target": "config_json",
        "field": field,
        "action": "set",
        "value": value,
        "reason": str(reason)[:500],
    }


def patch_config_file(path: str, patches: list[dict[str, Any]], *, safe_check) -> dict[str, Any]:
    """Load config from path, apply patches, write back. Returns updated config."""
    if not safe_check(path):
        raise PermissionError("Config path not allowed")
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Config not found: {path}")
    raw = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Config root must be a JSON object")
    updated = apply_config_patches(raw, patches)
    p.write_text(json.dumps(updated, indent=2), encoding="utf-8")
    return updated
