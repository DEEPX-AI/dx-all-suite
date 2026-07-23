"""Suggest Fix orchestrator — rules first, optional LLM fallback."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from shared.chat.config import load_config
from shared.chat.prompt_builder import build_system_prompt
from shared.chat.providers import stream_chat, ChatAPIError
from shared.chat.suggest_fix_rules import match_rules
from shared.chat.suggest_fix_schema import empty_result, parse_llm_json, validate_result

_SUGGEST_FIX_INSTRUCTION = """
You are a DX Compiler error analyst. Respond with ONLY a JSON object (no markdown prose outside JSON).
Schema:
{
  "summary": "one line",
  "cause": "detailed cause",
  "confidence": "high|medium|low",
  "patches": [
    {"target":"form|dxq|wizard|resume|config_json","field":"...","action":"set|enable|disable","value":...,"reason":"..."}
  ],
  "manual_steps": ["..."],
  "cannot_auto_fix": false
}
Rules:
- Max 5 patches. Only suggest fields the user can change in the compile form.
- Never change model_path unless the error clearly indicates a typo pattern.
- For config.json issues use target config_json with field inputs|dataset_path|calibration_num|calibration_method
- Or target wizard with field input_shapes|dataset_path for Build Config mode
- If unsure, set cannot_auto_fix true and list manual_steps.
"""


def _knowledge_dir() -> Path:
    return Path(__file__).parent / "knowledge"


def _complete_chat(messages: list[dict], temperature: float = 0.2) -> str:
    config = load_config()
    if config is None:
        return ""
    chunks: list[str] = []
    try:
        for token in stream_chat(
            provider=config["provider"],
            api_key=config.get("api_key", ""),
            model=config["model"],
            messages=messages,
            endpoint=config.get("endpoint"),
            temperature=temperature,
        ):
            if token:
                chunks.append(token)
    except (ChatAPIError, ValueError):
        return ""
    return "".join(chunks)


def build_job_context(
    job: Any,
    *,
    form_snapshot: dict[str, Any] | None = None,
    log_tail: str = "",
    feature_check: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "job_id": getattr(job, "job_id", ""),
        "status": getattr(job, "status", ""),
        "error": getattr(job, "error", "") or "",
        "phase": getattr(job, "current_phase", "") or "",
        "mode": getattr(job, "mode", "compile"),
        "model_path": getattr(job, "model_path", ""),
        "config_path": getattr(job, "config_path", ""),
        "output_dir": getattr(job, "output_dir", ""),
        "opt_level": getattr(job, "opt_level", 1),
        "aggressive_partitioning": getattr(job, "aggressive_partitioning", False),
        "quant_diagnosis": getattr(job, "quant_diagnosis", False),
        "node_selection": getattr(job, "node_selection_enabled", False),
        "use_q_pro": getattr(job, "use_q_pro", False),
        "log_tail": log_tail[-8000:] if log_tail else "",
    }
    if form_snapshot:
        ctx["form_snapshot"] = form_snapshot
    if feature_check:
        ctx["feature_check"] = feature_check
    buf = getattr(job, "log_buffer", None)
    if buf and not ctx["log_tail"]:
        lines = buf.get_new_lines(0)
        ctx["log_tail"] = "\n".join(lines[-200:])
    return ctx


def suggest_fix(
    job: Any,
    *,
    form_snapshot: dict[str, Any] | None = None,
    log_tail: str = "",
    feature_check: dict[str, Any] | None = None,
    lang: str = "en",
    use_llm: bool = True,
) -> dict[str, Any]:
    """Produce a validated suggest-fix result for a failed compile job."""
    resume_mode = getattr(job, "mode", "compile") == "resume"
    error = getattr(job, "error", "") or ""
    ctx = build_job_context(
        job,
        form_snapshot=form_snapshot,
        log_tail=log_tail,
        feature_check=feature_check,
    )
    tail = ctx.get("log_tail", "") or log_tail
    caps = (feature_check or {}).get("capabilities", {})

    ruled = match_rules(error, tail, resume_mode=resume_mode, capabilities=caps)
    if ruled and ruled.get("patches") and ruled.get("confidence") == "high":
        return ruled

    if use_llm and load_config() is not None:
        user_msg = (
            f"Analyze this compile failure and suggest fixes.\n"
            f"Error: {error}\n"
            f"Context: {ctx}\n"
            f"Language hint for manual_steps: {lang}"
        )
        system = build_system_prompt(
            knowledge_dir=_knowledge_dir(),
            app_name="dx_compiler",
            user_message=user_msg + " error fix",
            runtime_context={"mode": "suggest_fix", **ctx},
        )
        system = system + "\n\n" + _SUGGEST_FIX_INSTRUCTION
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ]
        raw_text = _complete_chat(messages, temperature=0.2)
        parsed = parse_llm_json(raw_text)
        if parsed:
            llm_result = validate_result(parsed, resume_mode=resume_mode)
            if llm_result.get("patches") or llm_result.get("manual_steps"):
                return llm_result

    if ruled:
        return ruled

    return validate_result({
        "summary": "No automatic fix identified",
        "cause": error or "Unknown error",
        "confidence": "low",
        "patches": [],
        "manual_steps": [
            "Review the compiler log for the first error line.",
            "Check model path, config.json, and output directory.",
            "Open AI chat (FAB) for detailed guidance.",
        ],
        "cannot_auto_fix": True,
    }, resume_mode=resume_mode)


def explain_prompt_context(ctx: dict[str, Any]) -> str:
    """Extra system context for explain-only chat mode."""
    return (
        "The user clicked Explain error. Explain the failure clearly. "
        "Do NOT propose automatic changes unless asked. "
        f"Job context: {ctx}"
    )
