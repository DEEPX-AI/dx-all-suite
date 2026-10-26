"""Immediate front-end feedback on preprocessing values.

The server refuses bad values with a 400, but on its own the user learns that only
after pressing Generate. `validateCalibNum` and `validateInputShapes` already warn as
the user types — preprocessing must do the same, in the same place.

More importantly, **front-end and server rules must match**. A stricter front end
blocks values the server would accept; a looser one lets the user hit a 400 with no
warning. Both confuse the user.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = ROOT / "dx_compiler" / "static" / "js" / "config_wizard.js"
HTML = ROOT / "dx_compiler" / "templates" / "partials" / "config_wizard.html"


def js() -> str:
    return JS.read_text(encoding="utf-8")


def test_the_wizard_warns_about_unusable_preprocessing_values():
    assert "validatePreprocessings" in js(), (
        "전처리에 대한 즉시 피드백이 없다 — 차원과 calibration_num 은 이미 그렇게 한다")


def test_the_warning_element_exists_and_is_announced():
    """A warning shown on screen but not announced to screen readers is only half done."""
    html = HTML.read_text(encoding="utf-8")
    assert 'id="wiz-prep-warning"' in html, "경고를 띄울 자리가 없다"
    block = html[html.index('id="wiz-prep-warning"') - 200:
                 html.index('id="wiz-prep-warning"') + 200]
    assert 'aria-live' in block, "wiz-shape-warning 과 달리 aria-live 가 없다"


def test_the_listener_is_delegated_to_the_pipeline_container():
    """Preprocessing entries are added and removed over time. A listener on each input
    would silently miss entries added later — the same reason as input-shapes-list."""
    src = js()
    assert re.search(r"prepPipeline\.addEventListener\('input', validatePreprocessings\)", src), \
        "컨테이너 위임이 아니다 — 나중에 추가한 전처리가 검사에서 빠진다"


def test_the_front_end_checks_the_same_size_parameters_as_the_server():
    """The server requires width, height, size and scale to be positive. So must the front end."""
    from dx_compiler.core.validation import _POSITIVE_PARAMS
    src = js()
    m = re.search(r"var PREP_POSITIVE = \[([^\]]*)\]", src)
    assert m, "프론트에 크기 파라미터 목록이 없다"
    front = {t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()}
    assert front == set(_POSITIVE_PARAMS), (
        f"프론트와 서버의 규칙이 다르다 — 프론트 {sorted(front)} / "
        f"서버 {sorted(_POSITIVE_PARAMS)}")


def test_the_front_end_also_catches_a_zero_std():
    """A division by zero can be reported before Generate is pressed."""
    src = js()
    assert "'std'" in src and "n === 0" in src, "std 의 0 을 프론트가 잡지 않는다"


def test_the_front_end_does_not_police_what_the_server_leaves_alone():
    """axis, x and pad_value may be a scalar or a list, with either sign.

    Numeric operands must not be incorrectly restricted to positive scalars.
    """
    src = js()
    m = re.search(r"var PREP_POSITIVE = \[([^\]]*)\]", src)
    front = {t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()}
    for loose in ("axis", "x", "pad_value", "channel"):
        assert loose not in front, (
            f"{loose} 는 스칼라도 리스트도 되는데 프론트가 양수로 제한한다")


def test_the_front_end_checks_the_same_arithmetic_transforms_as_the_server():
    from dx_compiler.core.validation import _ARITHMETIC_TRANSFORMS

    match = re.search(r"var PREP_ARITHMETIC = \[([^\]]*)\]", js())
    assert match
    front = {t.strip().strip("'\"") for t in match.group(1).split(",") if t.strip()}
    assert front == set(_ARITHMETIC_TRANSFORMS)
