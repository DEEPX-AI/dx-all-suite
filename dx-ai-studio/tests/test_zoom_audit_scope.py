"""Records **what the zoom audit checks and what it does not**.

**The zoom audit checks exactly one thing** — document-wide horizontal overflow
(`documentElement.scrollWidth - clientWidth`). It runs 5 zooms × 3 viewports, but many
axes still measure only that one thing.

So these pass the audit unnoticed:

  - an element hidden because an `overflow:hidden` ancestor **clips** it
  - text shrunk until it is hard to read
  - **vertical** overflow
  - a button pushed off screen so it **cannot be clicked**

This file is not a gate. It **states the audit's scope truthfully**, so nobody reads
"zoom is already thoroughly covered" into a zero-findings result. If the scope grows, these
tests fail; update this description then.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FULL = ROOT / "test_zoom_full_audit.py"
AUDIT = ROOT / "tests" / "test_zoom_full_audit.py"


def _src() -> str:
    return AUDIT.read_text(encoding="utf-8")


def test_the_audit_measures_document_level_overflow_only():
    """Confirm the measurement formula from the code."""
    src = _src()
    assert "scrollWidth - el.clientWidth" in src, (
        "측정식이 바뀌었다 — 이 파일의 설명을 다시 써야 한다")


def test_it_asserts_nothing_else():
    """There is only one assertion — more means the blind-spot description is stale."""
    src = _src()
    asserts = [ln.strip() for ln in src.splitlines() if ln.strip().startswith("assert ")]
    assert len(asserts) == 1, f"단언이 {len(asserts)}개로 늘었다: {asserts}"
    assert "overflow == 0" in asserts[0]


def test_the_axes_are_wide_but_the_check_is_narrow():
    """Many axes (5 zooms × 3 viewports) make it look thorough, yet it measures one thing.
    That contrast is what misleads readers, so the numbers are pinned."""
    src = _src()
    zooms = re.search(r"ZOOMS = \((.*?)\)", src).group(1)
    viewports = re.search(r"VIEWPORTS = \((.*?)\)\n", src, re.S).group(1)
    assert len(zooms.split(",")) == 5
    assert viewports.count("(") == 3


def test_element_level_clipping_is_not_checked():
    """The fact that element-level clipping is not checked is itself the contract.

    The audit zooms with `body.style.zoom`, which fires no resize event, so tab overflow
    calculations are not refreshed and element positions can be misleading (e.g. `.dx-tab`
    placed outside an `overflow:hidden` parent while document overflow is 0). Measuring that
    needs real browser zoom (CDP `Emulation.setPageScaleFactor` or deviceScaleFactor) or a
    narrow viewport; until then it is recorded only as "not covered".
    """
    src = _src()
    for token in ("getComputedStyle", "overflow:hidden", "clientWidth + 2"):
        assert token not in src, f"요소 단위 검사가 들어왔다({token}) — 설명을 갱신할 것"
