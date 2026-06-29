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


# Calibrated ratio: copilot-cli observed PR / tool_call ≈ 0.741 (5232 PR / 7061
# tool_calls across pilot runs). Used as method-1 PR estimator for tools that
# share GitHub Copilot backend but don't expose `totalPremiumRequests` in their
# stream (opencode-cli, codex-cli). In practice this method tracks copilot's
# own observed PR within ~15% — by far the most reliable estimator for
# agent-driven multi-turn sessions.
TOOL_CALL_PR_RATIO = 0.741


def _resolve_multiplier(model: str, mult_cfg: dict) -> float:
    """Look up the GitHub Copilot Premium Request multiplier for *model*.

    Used by the copilot-cli observed-PR USD calculation to scale the per-request
    rate by model class (e.g. Sonnet 1×, Opus 3×). Falls back to 1.0 if not listed.
    """
    if not mult_cfg or not model:
        return 1.0
    lower = model.lower()
    for k, v in mult_cfg.items():
        if k.lower() in lower:
            return float(v)
    return 1.0


# Backward-compat alias — the feature/user-turn-pr-estimation branch named the
# same lookup `_lookup_multiplier`. Both names refer to the same function so
# test_pr_estimation.py (which imports `_lookup_multiplier`) keeps passing.
_lookup_multiplier = _resolve_multiplier


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
    estimated_premium_requests: float = 0.0 # final PR used for USD calc

    # PR estimates from each method — kept side-by-side in §6.1 for transparency.
    # Note: a user_turn × multiplier estimator was tried and removed — it
    # understated agent-driven loops by ~35× vs copilot-cli's observed PR, making
    # it meaningless for this domain.
    pr_observed: float = 0.0                # method 0 — copilot-cli totalPremiumRequests
    pr_by_tool_call: float = 0.0            # method 1 — tool_call × 0.741 (calibrated, primary)
    pr_by_token_ratio: float = 0.0          # method 2 — (input+output) / tokens_per_premium (fallback)


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
    if "opus" in m and (
        "4-5" in m or "4-6" in m or "4-7" in m or "4-8" in m
        or "45" in m or "46" in m or "47" in m or "48" in m
    ):
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
    user_turn_count: int = 0,
    tool_call_count: int = 0,
) -> CostBreakdown:
    """Compute estimated USD for a single session, tool/model-aware.

    Strategy per tool:

    - **copilot-cli** (premium_requests > 0):
        cost = premium_requests × usd_per_request × multiplier(model)

    - **cursor-cli**:
        - if model is 'auto' → 0 USD (subscription, free within quota)
        - else → Anthropic rates (proxy — Cursor doesn't bill per-token directly)

    - **opencode-cli / codex-cli** (uses copilot provider):
        - Primary: tool_call_count × TOOL_CALL_PR_RATIO (calibrated from copilot-cli)
        - Fallback: token ratio reverse-engineering (input+output) / tokens_per_premium
        - cost = est_premium × usd_per_request

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
        mult = _resolve_multiplier(model, mult_cfg)
        cb.usd_premium = premium_requests * usd_per * mult
        cb.total_usd = cb.usd_premium
        cb.pricing_basis = "copilot_premium_request (actual)"
        cb.notes = (
            f"{premium_requests} actual premium requests × ${usd_per:.3f}"
            + (f" × {mult}" if mult != 1.0 else "")
        )
        # Compute both predictions for §6.1 cross-method comparison
        cb.pr_observed = float(premium_requests)
        cb.pr_by_tool_call = (tool_call_count * TOOL_CALL_PR_RATIO) if tool_call_count > 0 else 0.0
        if calibration and calibration.tokens_per_premium:
            cb.pr_by_token_ratio = (input_tokens + output_tokens) / calibration.tokens_per_premium
        cb.estimated_premium_requests = cb.pr_observed
        return cb

    # ===== OpenCode CLI / Codex CLI — copilot provider =====
    if tool in ("opencode-cli", "codex-cli"):
        tool_label = "OpenCode" if tool == "opencode-cli" else "Codex CLI"
        prem_cfg = config_pricing.get("copilot_premium_request", {}) or {}
        usd_per = float(prem_cfg.get("usd_per_request", 0.033))

        # Compute both prediction methods for transparency — reported side-by-side
        # in §6.1. Method 1 (tool_call calibration) is primary because empirically
        # it matches copilot-cli's observed totalPremiumRequests within ~15%.
        pr_tc = (tool_call_count * TOOL_CALL_PR_RATIO) if tool_call_count > 0 else 0.0
        pr_tr = 0.0
        if calibration and calibration.tokens_per_premium:
            tpr = calibration.tokens_per_premium
            total_io = input_tokens + output_tokens
            pr_tr = total_io / tpr if tpr > 0 else 0.0

        cb.pr_observed = 0.0  # not exposed by these tools
        cb.pr_by_tool_call = pr_tc
        cb.pr_by_token_ratio = pr_tr

        # Choose primary estimate (method 1 → 2 priority) for USD computation
        if pr_tc > 0:
            est_premium = pr_tc
            cb.pricing_basis = "copilot_premium_request (tool_call calibration — primary)"
            cb.notes = (
                f"{tool_label}: {tool_call_count} tool_calls × {TOOL_CALL_PR_RATIO:.3f} "
                f"= {pr_tc:.1f} PR (primary). token_ratio estimate: {pr_tr:.1f}."
            )
        elif pr_tr > 0:
            est_premium = pr_tr
            cb.pricing_basis = "copilot_premium_request (token ratio fallback)"
            cb.notes = (
                f"{tool_label}: token-ratio fallback = {pr_tr:.1f} PR "
                f"(tool_call unavailable)."
            )
        else:
            est_premium = 0.0
            cb.pricing_basis = f"{tool.replace('-', '_')}_calibration_unavailable"
            cb.notes = (
                f"{tool_label} uses copilot provider but no signal available "
                f"(tool_call=0, no token calibration)."
            )

        cb.estimated_premium_requests = est_premium
        cb.usd_premium = est_premium * usd_per
        cb.total_usd = cb.usd_premium
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
