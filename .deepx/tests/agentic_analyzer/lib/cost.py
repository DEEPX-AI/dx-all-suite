"""Cost estimation — convert token counts + premium requests → estimated USD.

Per-tool billing model:

  claude-code  → Anthropic API direct billing (per-token, by model)
  copilot-cli  → GitHub Copilot Premium Requests (per-request, flat rate)
  cursor-cli   → depends on model:
                   - claude-* / opus-* → Anthropic rates (proxy)
                   - auto              → Cursor subscription (effectively free)
  opencode-cli → uses copilot provider → backend Copilot Premium Requests
                  ★ Premium count is NOT in stream.jsonl — REVERSE-ENGINEERED
                  from token usage × copilot's avg (tokens / premium request) ratio.

⚠ All values are **estimates**. Verify against provider dashboards (see config.yaml).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CostBreakdown:
    """Per-session cost estimate."""
    usd_input: float = 0.0
    usd_output: float = 0.0
    usd_cache_read: float = 0.0
    usd_cache_write: float = 0.0
    usd_premium: float = 0.0
    total_usd: float = 0.0
    pricing_basis: str = "unknown"          # how we computed
    notes: str = ""                         # human-readable
    estimated_premium_requests: float = 0.0 # filled for opencode (and zero for others)


@dataclass
class CalibrationRatios:
    """Cross-tool calibration derived from observed copilot-cli data.

    Used to reverse-engineer premium request counts for tools that DON'T
    expose them directly (e.g., OpenCode using copilot provider).
    """
    tokens_per_premium: Optional[float] = None
    copilot_session_count: int = 0
    notes: str = ""


def compute_calibration_ratios(evals) -> CalibrationRatios:
    """Compute copilot-cli's avg (input+output tokens / premium request).

    This ratio is used to ESTIMATE premium request count for OpenCode sessions
    that use copilot provider (backend Copilot, premium count not in stream).
    """
    cr = CalibrationRatios()
    cop = [e for e in evals if e.tool == "copilot-cli" and e.premium_requests > 0]
    if not cop:
        cr.notes = "No copilot-cli sessions with premium_requests data — calibration unavailable"
        return cr
    total_tokens = sum(e.input_tokens + e.output_tokens for e in cop)
    total_premium = sum(e.premium_requests for e in cop)
    cr.copilot_session_count = len(cop)
    if total_premium > 0:
        cr.tokens_per_premium = total_tokens / total_premium
        cr.notes = (
            f"Calibrated from {len(cop)} copilot-cli sessions: "
            f"{total_tokens:,} (input+output) tokens / {total_premium:,} premium reqs "
            f"= {cr.tokens_per_premium:,.0f} tokens per premium request"
        )
    else:
        cr.notes = "copilot-cli has no premium_requests — calibration not derivable"
    return cr


def _is_cursor_auto(model: str) -> bool:
    """Check if cursor session used 'auto' (subscription, free)."""
    if not model:
        return False
    m = model.lower()
    return "auto" in m or "non-standard" in m


def _normalize_model_name(model: str) -> str:
    """Map various model name spellings → canonical config key."""
    m = (model or "").lower().replace("_", "-").replace(".", "-")
    if "opus" in m and ("4-6" in m or "4-7" in m or "46" in m):
        return "anthropic_claude_opus_4_6"
    if "sonnet" in m:
        return "anthropic_claude_sonnet_4_6"
    return "anthropic_claude_sonnet_4_6"   # default fallback


def _token_cost(input_tokens, output_tokens, cache_read, cache_write, rates) -> CostBreakdown:
    """Pure token-based costing (Anthropic-style)."""
    cb = CostBreakdown()
    cb.usd_input = input_tokens * float(rates.get("input_per_1m", 0)) / 1_000_000
    cb.usd_output = output_tokens * float(rates.get("output_per_1m", 0)) / 1_000_000
    cb.usd_cache_read = cache_read * float(rates.get("cache_read_per_1m", 0)) / 1_000_000
    cb.usd_cache_write = cache_write * float(rates.get("cache_write_per_1m", 0)) / 1_000_000
    cb.total_usd = cb.usd_input + cb.usd_output + cb.usd_cache_read + cb.usd_cache_write
    return cb


def estimate_cost(
    tool: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int,
    cache_write_tokens: int,
    premium_requests: int,
    config_pricing: dict,
    calibration: Optional[CalibrationRatios] = None,
) -> CostBreakdown:
    """Compute estimated USD for a single session, tool/model-aware.

    Strategy per tool:

    - **copilot-cli** (premium_requests > 0):
        cost = premium_requests × usd_per_request × multiplier(model)

    - **cursor-cli**:
        - if model is 'auto' → 0 USD (subscription, free within quota)
        - else → Anthropic rates (proxy — Cursor doesn't bill per-token directly)

    - **opencode-cli** (uses copilot provider):
        - Estimate premium req count from token ratio: premium ≈ (input+output) / tokens_per_premium
        - cost = est_premium × usd_per_request
        - Falls back to Anthropic proxy if calibration unavailable

    - **claude-code** (or unknown tool):
        - Anthropic API direct billing → token-based using configured rates
    """
    cb = CostBreakdown()

    # ===== Cursor with auto model — subscription, effectively free =====
    if tool == "cursor-cli" and _is_cursor_auto(model):
        cb.pricing_basis = "cursor_subscription_free"
        cb.notes = (
            "Cursor 'auto' model — usage within subscription quota, "
            "no per-token cost (free within $20/mo Pro or $40/mo Business tier limit)"
        )
        cb.total_usd = 0.0
        return cb

    # ===== Copilot CLI — premium request based (direct from stream) =====
    if tool == "copilot-cli" and premium_requests > 0:
        prem_cfg = config_pricing.get("copilot_premium_request", {}) or {}
        usd_per = float(prem_cfg.get("usd_per_request", 0.033))
        mult_cfg = config_pricing.get("copilot_request_multiplier", {}) or {}
        mult = 1.0
        for k, v in mult_cfg.items():
            if k.lower() in (model or "").lower():
                mult = float(v)
                break
        cb.usd_premium = premium_requests * usd_per * mult
        cb.total_usd = cb.usd_premium
        cb.pricing_basis = "copilot_premium_request (actual)"
        cb.notes = (
            f"{premium_requests} actual premium requests × ${usd_per:.3f}"
            + (f" × {mult}" if mult != 1.0 else "")
        )
        return cb

    # ===== OpenCode CLI — copilot provider, reverse-engineer premium count =====
    if tool == "opencode-cli":
        if calibration and calibration.tokens_per_premium:
            tpr = calibration.tokens_per_premium
            total_io = input_tokens + output_tokens
            est_premium = total_io / tpr if tpr > 0 else 0.0
            cb.estimated_premium_requests = est_premium
            prem_cfg = config_pricing.get("copilot_premium_request", {}) or {}
            usd_per = float(prem_cfg.get("usd_per_request", 0.033))
            cb.usd_premium = est_premium * usd_per
            cb.total_usd = cb.usd_premium
            cb.pricing_basis = "copilot_premium_request (estimated)"
            cb.notes = (
                f"OpenCode uses copilot provider — premium count NOT in stream. "
                f"Estimated {est_premium:.1f} reqs = {total_io:,} (input+output) / {tpr:,.0f} (calibration ratio)"
            )
            return cb
        # Calibration unavailable → fall back to noting this
        cb.pricing_basis = "opencode_calibration_unavailable"
        cb.notes = (
            "OpenCode uses copilot provider but no copilot-cli data available to "
            "calibrate token→premium ratio. Cost cannot be reliably estimated."
        )
        return cb

    # ===== Claude Code or unknown tool — Anthropic direct billing =====
    pricing_key = _normalize_model_name(model)
    rates = config_pricing.get(pricing_key, {}) or {}
    if not rates:
        cb.pricing_basis = "no_pricing_data"
        cb.notes = f"No pricing config found for model '{model}' (key: {pricing_key})"
        return cb

    cb = _token_cost(input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, rates)
    cb.pricing_basis = pricing_key
    if tool == "cursor-cli":
        cb.notes = (
            f"Cursor with model '{model}' — Anthropic rates proxy "
            f"(Cursor itself bills via subscription, not per-token; this is the equivalent cost if metered)"
        )
    else:
        cb.notes = f"Direct Anthropic API rates for {pricing_key}"
    return cb
