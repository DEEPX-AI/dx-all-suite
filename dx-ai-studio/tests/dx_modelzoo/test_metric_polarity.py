"""Each metric has its own direction of better and worse.

The public catalog's `metric` field mixes directions: Top1 is better when higher, RMSE when
lower. Painting a quantization delta as "loss", as the homepage does, is right **only for
higher-is-better metrics**; a lower RMSE is an improvement.

Polarity is not inferred from the data: averaging the change before and after quantization flips
the sign for metrics with few samples (`Accuracy`, n=4). Polarity is domain knowledge tied to the
metric name, not a statistic.

Unknown metrics stay neutral. Pretending to know is worse than leaving the value uncolored.
"""
from __future__ import annotations

import pytest

from dx_modelzoo.core.metrics import direction_of, format_delta


@pytest.mark.parametrize("metric", ["Top1", "mAP", "mIoU", "PSNR", "AP(Easy)", "Accuracy"])
def test_higher_is_better_metrics(metric):
    assert direction_of(metric) == "higher"


@pytest.mark.parametrize("metric", ["RMSE", "NME", "MNAE"])
def test_lower_is_better_metrics(metric):
    assert direction_of(metric) == "lower"


def test_unknown_metric_is_neutral_not_guessed():
    assert direction_of("SomeNewScore") is None
    assert direction_of(None) is None


def test_delta_carries_sign_and_verdict_for_known_metrics():
    # Top1: the value dropped, so it got worse
    assert format_delta("Top1", 74.436, 73.97) == (-0.466, "worse")
    # RMSE: the value rose, so it got worse
    assert format_delta("RMSE", 0.607, 0.616) == (0.009, "worse")
    # RMSE going down is an improvement
    assert format_delta("RMSE", 0.616, 0.607) == (-0.009, "better")


def test_delta_for_unknown_metric_has_no_verdict():
    """Show the sign but do not color it as better/worse."""
    delta, verdict = format_delta("SomeNewScore", 10.0, 9.0)
    assert delta == -1.0
    assert verdict is None


def test_delta_is_none_when_a_side_is_missing():
    assert format_delta("Top1", 74.4, None) == (None, None)
    assert format_delta("Top1", None, 73.9) == (None, None)
