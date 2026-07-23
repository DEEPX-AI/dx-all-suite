"""detail.js must not conflate Metric (name) with Accuracy (eval value).

Two real bugs seen on casvit_xs (metric={"name":"TopK1, TopK5"}, no evaluation):
  1. Specification "Metric" rendered the dict literally as "name: TopK1, TopK5"
     instead of the metric name "TopK1, TopK5".
  2. Key-Facts "Accuracy" fell back to the metric object's first value, so it
     mirrored the Metric ("TopK1, TopK5") instead of showing "Not provided by source".
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DETAIL = ROOT / "dx_modelzoo" / "static" / "js" / "detail.js"


def test_spec_metric_uses_metric_text_not_raw_stringify():
    src = DETAIL.read_text(encoding="utf-8")
    # renderSpecification must route the metric through _metricText (which unwraps
    # {name:...}), never the raw "${k}: ${v}" entries-join that leaks "name: ...".
    assert "['Metric', _metricText(spec.metric)]" in src
    assert "Object.entries(spec.metric)" not in src, (
        "Metric row must not stringify the metric object → leaks 'name: <value>'"
    )


def test_best_accuracy_does_not_fall_back_to_metric():
    src = DETAIL.read_text(encoding="utf-8")
    # _bestAccuracy must rely solely on evaluation[*].accuracy and return '' otherwise.
    # The metric fallback (Object.values(metric)[0]) made Accuracy mirror Metric.
    assert "function _bestAccuracy(" in src
    body = src.split("function _bestAccuracy(", 1)[1].split("\nfunction ", 1)[0]
    assert "Object.values(metric)" not in body, (
        "_bestAccuracy must not fall back to the metric spec"
    )
    assert "metric['Top-1']" not in body
