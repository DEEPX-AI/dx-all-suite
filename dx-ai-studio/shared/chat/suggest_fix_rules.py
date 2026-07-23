"""Rule-based Suggest Fix patches (no LLM)."""

from __future__ import annotations

import re
from typing import Any

from shared.chat.suggest_fix_schema import validate_result


def _patch_form(field: str, value: Any, reason: str) -> dict[str, Any]:
    return {
        "target": "form",
        "field": field,
        "action": "set",
        "value": value,
        "reason": reason,
    }


def _patch_wizard(field: str, value: Any, reason: str) -> dict[str, Any]:
    return {
        "target": "wizard",
        "field": field,
        "action": "set",
        "value": value,
        "reason": reason,
    }


def match_rules(
    error: str,
    log_tail: str,
    *,
    resume_mode: bool = False,
    capabilities: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Return a validated suggest-fix result from rules, or None if no match."""
    blob = f"{error}\n{log_tail}".lower()
    caps = capabilities or {}
    patches: list[dict[str, Any]] = []
    manual_steps: list[str] = []
    summary = ""
    cause = error or "Compilation failed"

    if "dx_com" in blob and ("not installed" in blob or "no module" in blob):
        return validate_result({
            "summary": "dx_com is not available",
            "cause": cause,
            "confidence": "high",
            "patches": [],
            "manual_steps": [
                "Open Setup panel and install the Compiler SDK.",
                "Verify /feature-check returns compile: true.",
            ],
            "cannot_auto_fix": True,
        }, resume_mode=resume_mode)

    if "node_selection_unsupported" in blob or "subprocess compile mode" in blob:
        patches.append(_patch_form(
            "node_selection", False,
            "Node selection is unavailable in subprocess mode; disable to continue.",
        ))
        summary = "Disable compile range selection"

    if "timed out" in blob or "timeout" in blob:
        patches.append(_patch_form(
            "opt_level", 0,
            "Lower optimization level to reduce compile time.",
        ))
        if not summary:
            summary = "Reduce optimization level after timeout"

    if "aggressive" not in blob and any(
        kw in blob for kw in ("cpu fallback", "cpu_fallback", "unsupported_op", "on cpu")
    ):
        patches.append(_patch_form(
            "aggressive_partitioning", True,
            "Try aggressive partitioning to keep more nodes on NPU.",
        ))
        if not summary:
            summary = "Enable aggressive partitioning"

    if "dynamic" in blob and "shape" in blob:
        manual_steps.append(
            "Fix dynamic input shapes: use Build Config wizard or set fixed shapes in config.json.",
        )
        patches.append(_patch_wizard("open", True, "Open config wizard to set fixed input shapes."))
        if not summary:
            summary = "Dynamic shapes detected — configure fixed inputs"

    if any(kw in blob for kw in ("input not found", "key mismatch", "inputs", "input name")):
        manual_steps.append("Ensure config.json inputs keys match ONNX input names exactly.")
        patches.append(_patch_wizard("open", True, "Open config wizard to fix input name/shape."))
        if not summary:
            summary = "Input name or shape mismatch"

    if "calibration" in blob or "dataset" in blob:
        manual_steps.append("Verify calibration dataset path exists and is readable on the server.")
        patches.append({
            "target": "wizard",
            "field": "open",
            "action": "set",
            "value": True,
            "reason": "Open config wizard to fix calibration dataset path.",
        })
        if not summary:
            summary = "Calibration dataset issue"

    if "batch" in blob and re.search(r"batch\s*[>!=]+\s*1|batch size", blob):
        manual_steps.append("Re-export ONNX with batch size 1.")
        if not summary:
            summary = "Batch size must be 1 for NPU"

    if not caps.get("node_selection", True) and not resume_mode:
        # Subprocess warning already emitted — suggest disabling if enabled in form
        if "node selection" in blob:
            patches.append(_patch_form("node_selection", False, "Node selection requires in-process dx_com."))

    if not patches and not manual_steps:
        return None

    confidence = "high" if patches else "medium"
    return validate_result({
        "summary": summary or "Suggested manual steps",
        "cause": cause,
        "confidence": confidence,
        "patches": patches,
        "manual_steps": manual_steps,
        "cannot_auto_fix": False,
    }, resume_mode=resume_mode)
