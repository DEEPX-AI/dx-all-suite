"""The wizard (front end) must not silently pass on unusable dimensions.

The backend refuses them with a 400, but on its own the user learns "why not" only
after pressing Generate. `validateCalibNum` already warns as the user types —
dimensions must warn the same way, in the same place.

The parser must also not drop bad values. A parser like

    .split(',').map(d => parseInt(d.trim())).filter(d => !isNaN(d))

turns `1,3,abc,224` into `[1,3,224]`: `abc` **silently disappears**, four dimensions
go in and three are sent, and nobody says so.
"""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "dx_compiler" / "static" / "js" / "config_wizard.js"


def source() -> str:
    return SRC.read_text(encoding="utf-8")


def test_the_wizard_warns_about_unusable_dimensions():
    src = source()
    assert "validateInputShapes" in src, (
        "차원에 대한 즉시 피드백이 없다 — calibration_num 은 이미 그렇게 한다"
    )


def test_bad_dimensions_are_not_silently_dropped():
    """`filter(d => !isNaN(d))` drops mistyped values and changes the number of dimensions."""
    src = source()
    m = re.search(r"\.split\(','\)[^;]*", src, re.S)
    assert m, "차원 파싱 부분을 찾을 수 없다"
    body = m.group(0)
    assert "filter(d => !isNaN(d))" not in body, (
        "잘못된 값을 조용히 버린다 — 4차원을 넣었는데 3차원이 전송된다"
    )


def test_the_warning_uses_the_same_mechanism_as_calibration():
    """If warnings are shown in two different ways, one of them will go stale."""
    src = source()
    assert src.count("style.display = msg ? '' : 'none'") >= 2, (
        "차원 경고가 기존 경고와 다른 방식으로 그려진다"
    )
