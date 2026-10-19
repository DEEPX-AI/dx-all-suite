"""RecommendEngine source contracts.

The behaviour is tested by running recommend.js in Chromium
(test_recommend_engine_browser.py), which needs no Node.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECOMMEND_JS = ROOT / "dx_planner/static/js/recommend.js"


def test_recommend_engine_source_contracts():
    src = RECOMMEND_JS.read_text(encoding="utf-8")
    for token in [
        "per_channel_fps",        # measured capacity
        "total_fps",              # T_sat for estimates
        "EXTRAPOLATION_CAP",      # estimates are bounded
        "npu_throttled",          # thermal flag
        "case 'channels'", "case 'performance'", "case 'power'",
    ]:
        assert token in src, f"expected token {token!r} in recommend.js"
    # Policy layers that must stay out: no pricing, no CPU gate, no headroom fudge factor.
    for gone in ["fpsHeadroom", "confidenceTier", "avg_cpu_pct", "cpuBudget", "costPerChannel", "price_usd"]:
        assert gone not in src, f"removed token {gone!r} should be gone from recommend.js"


def test_ai_help_knowledge_describes_the_current_engine():
    """AI Help answered from a page describing a Lowest Cost priority, Interpolated/Theoretical tiers, an FPS
    headroom input, a Host-limited flag and per-channel prices — none of which the page has had for months."""
    kb = (ROOT / "shared/chat/knowledge/dx_planner.md").read_text(encoding="utf-8")
    for gone in ["Lowest Cost", "Interpolated", "Theoretical", "headroom", "Host-limited", "채널당 대략적 비용", "8096"]:
        assert gone not in kb, gone
    for now in ["Most channels", "Best Performance", "Lowest Power", "Estimated", "T_sat", "throttle"]:
        assert now in kb, now
