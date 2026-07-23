"""Structured patch schema for Compiler Suggest Fix."""

from __future__ import annotations

import json
from typing import Any

MAX_PATCHES = 8

FORM_FIELDS: dict[str, type] = {
    "model_path": str,
    "config_path": str,
    "output_dir": str,
    "opt_level": int,
    "aggressive_partitioning": bool,
    "gen_log": bool,
    "quant_diagnosis": bool,
    "node_selection": bool,
    "use_q_pro": bool,
}

RESUME_FIELDS: dict[str, type] = {
    "qxnn_path": str,
    "output_dir": str,
    "recalibration_method": str,
    "dataset_path": str,
    "use_q_pro": bool,
}

DXQ_KEYS = frozenset({"DXQ-P0", "DXQ-P1", "DXQ-P2", "DXQ-P3", "DXQ-P4", "DXQ-P5"})

VALID_ACTIONS = frozenset({"set", "enable", "disable"})
VALID_TARGETS = frozenset({"form", "dxq", "wizard", "resume", "config_json"})
VALID_CONFIDENCE = frozenset({"high", "medium", "low"})


def empty_result() -> dict[str, Any]:
    return {
        "summary": "",
        "cause": "",
        "confidence": "low",
        "patches": [],
        "manual_steps": [],
        "cannot_auto_fix": True,
    }


def _coerce_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        low = value.strip().lower()
        if low in ("true", "1", "yes", "on"):
            return True
        if low in ("false", "0", "no", "off"):
            return False
    return None


def validate_patch(patch: Any, *, resume_mode: bool = False) -> dict[str, Any] | None:
    if not isinstance(patch, dict):
        return None
    target = patch.get("target")
    action = patch.get("action")
    field = patch.get("field")
    if target not in VALID_TARGETS or action not in VALID_ACTIONS:
        return None
    if not isinstance(field, str) or not field.strip():
        return None

    allowed = RESUME_FIELDS if (resume_mode and target == "resume") else FORM_FIELDS
    if target == "form" and field not in allowed:
        return None
    if target == "resume" and field not in RESUME_FIELDS:
        return None
    if target == "dxq" and field not in DXQ_KEYS:
        return None
    if target == "wizard" and field not in ("open", "input_shapes", "calibration_dataset", "dataset_path", "calibration_num", "calibration_method"):
        return None

    value = patch.get("value")
    if target == "config_json":
        from shared.chat.config_patch import validate_config_json_patch
        return validate_config_json_patch({
            "field": field,
            "value": value,
            "reason": patch.get("reason", ""),
        })

    if action in ("enable", "disable"):
        if target != "dxq":
            return None
        value = action == "enable"
        action = "set"

    if target == "form":
        expected = allowed[field]
        if expected is int:
            try:
                value = int(value)
            except (TypeError, ValueError):
                return None
            if field == "opt_level" and value not in (0, 1):
                return None
        elif expected is bool:
            coerced = _coerce_bool(value)
            if coerced is None:
                return None
            value = coerced
        elif expected is str and not isinstance(value, str):
            return None

    if target == "resume" and field == "recalibration_method":
        if value is not None and value not in ("", "minmax", "ema", "iqr"):
            return None

    reason = patch.get("reason", "")
    if not isinstance(reason, str):
        reason = str(reason)

    out: dict[str, Any] = {
        "target": target,
        "field": field,
        "action": "set",
        "value": value,
        "reason": reason[:500],
    }
    if target == "dxq" and isinstance(patch.get("params"), dict):
        out["params"] = patch["params"]
    return out


def validate_result(raw: Any, *, resume_mode: bool = False) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return empty_result()

    confidence = raw.get("confidence", "low")
    if confidence not in VALID_CONFIDENCE:
        confidence = "low"

    patches_in = raw.get("patches", [])
    if not isinstance(patches_in, list):
        patches_in = []

    patches: list[dict[str, Any]] = []
    for item in patches_in[:MAX_PATCHES]:
        validated = validate_patch(item, resume_mode=resume_mode)
        if validated:
            patches.append(validated)

    manual = raw.get("manual_steps", [])
    if not isinstance(manual, list):
        manual = []
    manual_steps = [str(m)[:500] for m in manual[:10]]

    return {
        "summary": str(raw.get("summary", ""))[:500],
        "cause": str(raw.get("cause", ""))[:2000],
        "confidence": confidence,
        "patches": patches,
        "manual_steps": manual_steps,
        "cannot_auto_fix": bool(raw.get("cannot_auto_fix", False)) and not patches,
    }


def apply_patches_to_form(form: dict[str, Any], patches: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a new form dict with validated patches applied."""
    out = dict(form)
    enhanced = out.get("enhanced_scheme")
    if isinstance(enhanced, str) and enhanced.strip():
        try:
            enhanced = json.loads(enhanced)
        except json.JSONDecodeError:
            enhanced = {}
    elif not isinstance(enhanced, dict):
        enhanced = {}

    for patch in patches:
        target = patch["target"]
        field = patch["field"]
        value = patch.get("value")

        if target == "form":
            out[field] = value
        elif target == "resume":
            out[field] = value
        elif target == "dxq":
            if value:
                params = patch.get("params") if isinstance(patch.get("params"), dict) else {}
                if field == "DXQ-P1":
                    enhanced[field] = True
                else:
                    enhanced[field] = params or True
            else:
                enhanced.pop(field, None)
            out["enhanced_scheme"] = enhanced
            out["use_q_pro"] = False
        elif target == "wizard":
            wizard = out.setdefault("_wizard_actions", [])
            wizard.append({"field": field, "value": value, "reason": patch.get("reason", "")})
        elif target == "config_json":
            cfg = out.setdefault("_config_json_patches", [])
            cfg.append({"field": field, "value": value, "reason": patch.get("reason", "")})

    if enhanced:
        out["enhanced_scheme"] = enhanced
    return out


def parse_llm_json(text: str) -> dict[str, Any] | None:
    """Extract JSON object from LLM response."""
    text = (text or "").strip()
    if not text:
        return None
    if text.startswith("```"):
        lines = text.splitlines()
        body = []
        in_fence = False
        for line in lines:
            if line.strip().startswith("```"):
                if in_fence:
                    break
                in_fence = True
                continue
            if in_fence:
                body.append(line)
        text = "\n".join(body).strip()
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                obj = json.loads(text[start : end + 1])
                return obj if isinstance(obj, dict) else None
            except json.JSONDecodeError:
                return None
    return None
