"""The internal source's 20-column table has the shape the parser assumes.

The fixture is a representative slice of a real response (3 header rows of the 20-column table plus 3 data rows),
and these tests pin that shape.

Why: the public page broke in exactly this silent way. Its table was replaced by inline JSON, the scraper did not
follow, and the route returned 500 without any gate noticing. The internal source carries the same risk.
"""
from __future__ import annotations

from pathlib import Path

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "internal_modelzoo_table.html"


def _models():
    from dx_app.core.modelzoo import _parse_models

    return _parse_models(FIXTURE.read_text(encoding="utf-8"))


def test_the_twenty_column_table_still_parses():
    models = _models()
    assert models, "internal 레이아웃에서 한 건도 못 읽었다"


def test_a_row_carries_the_fields_the_screen_uses():
    m = _models()[0]
    for key in ("name", "task", "qlite", "qpro"):
        assert key in m, f"{key} 가 없다: {sorted(m)}"
    assert m["qlite"].get("dxnn_url", "").endswith(".dxnn"), m["qlite"]


def test_internal_rows_carry_only_two_tiers():
    """The public source offers Q-Master but this one does not; pin that asymmetry.

    `_CHIP_DIRS` and the frontend's `MZ_CHIPS` iterate over three tiers, but rows built here have no `qmaster`
    key at all. That is handled quietly (`m.get(chip)` → None, `m[chip.key]` → undefined → '–'); this test makes
    it a contract rather than an accident. The internal source lists no Q-Master models.
    """
    m = _models()[0]
    assert "qmaster" not in m, (
        "internal 이 qmaster 를 내기 시작했다 — 화면과 설치 경로를 다시 확인할 것"
    )


def test_missing_numbers_are_dashes_here_not_nulls():
    """Public gives numbers or None; internal gives the string '-'.

    The same screen reads both sources, so the difference must be known: in sorting or arithmetic it would go wrong
    silently.
    """
    m = _models()[0]
    for key in ("fps", "fps_per_watt"):
        assert isinstance(m.get(key), str), f"{key} 가 문자열이 아니다: {m.get(key)!r}"
