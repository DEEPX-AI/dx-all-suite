"""Metric direction and quantization delta.

An accuracy number alone cannot be compared. The public catalog uses 18 kinds of
`metric` with mixed directions — Top1 is better higher, RMSE is better lower — so
coloring a delta requires knowing which way is good.

Direction is not inferred from the data: judging by the mean change before and after
quantization flips the sign on metrics with few samples (`Accuracy`, n=4). It is domain
knowledge about the metric name, so it lives in an explicit table.

Metrics not in the table are **neutral**: the sign is shown but not colored good or bad.
Pretending to know is worse than leaving it uncolored. (New metrics can appear in the
public catalog, so this path is really used.)
"""
from __future__ import annotations

# Measured: 18 kinds across 354 models. The two sets below cover 350+ of them.
HIGHER_IS_BETTER = frozenset({
    "Top1", "Top5", "Accuracy", "Average Accuracy",
    "mAP", "mAP50", "mAP_BEV@0.5", "det_mAP50",
    "AP", "AP(Easy)", "AP(Medium)", "AP(Hard)", "AP@0.5", "AR10",
    "mIoU", "PSNR", "Recall@1", "HEA",
})
LOWER_IS_BETTER = frozenset({"RMSE", "NME", "MNAE", "ADD"})


def direction_of(metric):
    """'higher' | 'lower' | None (unknown)."""
    if not metric:
        return None
    name = str(metric).strip()
    if name in HIGHER_IS_BETTER:
        return "higher"
    if name in LOWER_IS_BETTER:
        return "lower"
    return None


def format_delta(metric, baseline, value):
    """(delta, verdict) — verdict is 'better' | 'worse' | None (unknown).

    The delta is computed at render time, not stored: it derives from the baseline,
    and a stored copy could drift from it.
    """
    if baseline is None or value is None:
        return (None, None)
    delta = round(float(value) - float(baseline), 6)
    direction = direction_of(metric)
    if direction is None or delta == 0:
        return (delta, None)
    improved = delta > 0 if direction == "higher" else delta < 0
    return (delta, "better" if improved else "worse")
