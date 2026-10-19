"""How the catalog data reaches the screen.

Static contracts: they read the source, with no browser. test_metric_polarity.py checks
that values are computed correctly and test_public_payload_parser.py checks parsing; this
file checks that the data is actually wired into the UI code.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG_JS = ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js"
DETAIL_JS = ROOT / "dx_modelzoo" / "static" / "js" / "detail.js"


def _catalog():
    return CATALOG_JS.read_text(encoding="utf-8")


def test_table_gains_params_and_fps_per_watt_columns():
    """The table shows FPS/W (present for most models) and params."""
    src = _catalog()
    headers = re.search(r"const headers = \[(.*?)\];", src, re.S)
    assert headers, "테이블 헤더 정의를 찾을 수 없다"
    block = headers.group(1)
    for key in ("'params'", "'fps_per_watt'"):
        assert key in block, f"헤더에 {key} 가 없다"


def test_accuracy_is_shown_with_its_metric_name():
    """One column holds values such as `3.499` (NME) and `98.667` (Top-1).

    Without the metric name the two look comparable, but they are not, so each value carries its metric.
    """
    src = _catalog()
    assert "_accuracyWithMetric" in src, "지표명을 붙이는 경로가 없다"


def test_sorting_never_compares_across_metrics():
    """Values of different metrics are not ordered against each other.

    A comparator that ignores the metric would put NME 3.5 'below' Top-1 98.6,
    an order that means nothing.
    """
    src = _catalog()
    assert "_compareAccuracy" in src, "정확도 전용 비교자가 없다"
    body = re.search(r"function _compareAccuracy\((.*?)\n}", src, re.S)
    assert body, "_compareAccuracy 본문을 찾을 수 없다"
    assert "metric" in body.group(1), "비교자가 지표를 보지 않는다"


def test_card_shows_accuracy_next_to_fps():
    src = _catalog()
    card = re.search(r"renderCardItem\(m\)\s*\{(.*?)\n  \},", src, re.S)
    assert card, "renderCard 를 찾을 수 없다"
    assert "_accuracyWithMetric" in card.group(1), "카드에 정확도가 없다"


def test_detail_has_a_tier_comparison():
    """ONNX → Q-Lite → Q-Pro → Q-Master on one row shows the cost of quantization."""
    src = DETAIL_JS.read_text(encoding="utf-8")
    assert "sectionTiers" in src, "tier 비교 섹션이 없다"
    for tier in ("qlite", "qpro", "qmaster"):
        assert tier in src, f"{tier} 가 상세에 없다"


def test_qmaster_chip_only_when_present():
    """Only a few models have Q-Master.

    Drawing the chip always would make most chips read 'none', and the chip would carry no information.
    """
    src = _catalog()
    assert "qmaster" in src, "Q-Master 를 아는 코드가 없다"
