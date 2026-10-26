"""The model table must render in the same place **whatever is installed locally**.

models.js adds a `📊 Graph` button only for installed models and lengthens the
download label from Download to Re-download. ACTIONS is the last column, so when
its width changes the columns to its left narrow and the whole table reflows.

That hurts twice:

1. **UX** — the table jumps every time a model is downloaded.
2. **Gate** — the visual baselines are captured with no models installed, so
   installing one (normal use of the product) shifts 8 baselines by up to 22%.
   Masking the ACTIONS column does not help, because the reflow happens outside
   the mask (22.58% → 22.17%). Removing the cause is the fix.

Measured in chromium at all four widths (650/860/1150/1320):
    installed       maxWidth 246px
    not installed   maxWidth 175px
The value is the same at every width, so one fixed value works without a media
query, and the breakpoint ratchet is untouched.

This file is a source contract; the visual suite catches the actual rendered width.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSS = ROOT / "dx_app" / "static" / "css" / "style.css"
JS = ROOT / "dx_app" / "static" / "js" / "models.js"


def _actions_rule() -> str:
    css = CSS.read_text(encoding="utf-8")
    m = re.search(r"\.m-actions\{([^}]*)\}", css)
    assert m, ".m-actions 규칙을 찾을 수 없다"
    return m.group(1)


def test_the_actions_column_has_a_pinned_width():
    """Without a fixed width the column grows with its content and pushes the table."""
    rule = _actions_rule()
    assert re.search(r"min-width:\s*\d+px", rule), (
        "ACTIONS 열에 고정 폭이 없다 — 설치된 모델 수에 따라 표가 리플로우된다. "
        f"현재 규칙: {rule!r}"
    )


def test_the_pinned_width_fits_the_widest_state():
    """The widest state (installed, Graph + Re-download) measured 246px.

    Any narrower and the buttons clip or wrap and the row height changes —
    that only moves the reflow to the vertical axis.
    """
    rule = _actions_rule()
    px = int(re.search(r"min-width:\s*(\d+)px", rule).group(1))
    assert px >= 246, f"min-width {px}px 는 가장 넓은 상태(246px)보다 좁다"


def test_the_buttons_still_cannot_wrap():
    """Without flex-wrap:nowrap the buttons fold inside the fixed width and the row height changes."""
    assert "flex-wrap:nowrap" in _actions_rule()


def test_the_install_state_is_what_changes_the_content():
    """Tie the reason for this contract to the code.

    As long as models.js draws different buttons by `model_exists`, this column's
    width depends on local state. If that branch disappears the test loses its
    point, so it checks that the branch is still there.
    """
    js = JS.read_text(encoding="utf-8")
    assert "model_exists" in js, "설치 여부로 갈리는 렌더가 사라졌다 — 계약을 재검토할 것"
    assert "Re-download" in js, "Download/Re-download 라벨 분기가 사라졌다"
