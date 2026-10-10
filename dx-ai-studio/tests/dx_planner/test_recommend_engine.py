"""RecommendEngine source contracts.

The behaviour is tested by running recommend.js in Chromium
(test_recommend_engine_browser.py — spec 2026-10-11-edgeguide-recommendation-design.md).
The Node VM test that used to live here pinned the 2026-07-23 rule that a throttled row is
excluded and nothing is estimated; that rule zeroed 231 of 240 combos at 60 FPS, and the test
skipped silently wherever Node was missing.
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
    # Policy layers that stay removed: no pricing, no CPU gate, no headroom fudge factor.
    for gone in ["fpsHeadroom", "confidenceTier", "avg_cpu_pct", "cpuBudget", "costPerChannel", "price_usd"]:
        assert gone not in src, f"removed token {gone!r} should be gone from recommend.js"
