"""The tutorial's cart demo must not lose to the catalog loading order.

Otherwise the `#mz-cart` check in `tests/test_tutorial_spotlight_spot_check.py` fails now
and then. That looks flaky, but the cause is ordering, not timing:

    nav('modelzoo') → initModelZoo()  (async, not awaited)
                        └ if MZ.models is empty, await mzLoadModels()
    _prepModelzooCartDemo() carries on synchronously
                        └ no models yet, so _mockModelzooCartFallback()
                          (writes innerHTML only, does not fill MZ.cart)
    fetch done → initModelZoo() calls mzRenderCart() again
                        └ MZ.cart is empty, so display:none  ← wipes what was just built

When the catalog is already loaded, the first branch builds a real cart that
survives. So the demo usually wins and sometimes loses.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "dx_app" / "static" / "js" / "tutorial.js"


def _prep_body() -> str:
    src = SRC.read_text(encoding="utf-8")
    start = src.index("function _prepModelzooCartDemo")
    return src[start: src.index("\n  }", start)]


def test_the_demo_does_not_block_the_step():
    """Waiting in beforeStep lets the step be replaced in the meantime.

    The journey runner presses Next every 350ms, so a beforeStep that takes 2.5s
    changes the engine's _stepToken; the step never renders and falls back to
    floating — a worse symptom than the one being fixed. The fix is not to wait
    but to keep the cart from being overwritten later.
    """
    body = _prep_body()
    assert "_waitForModels" not in body, "beforeStep 이 카탈로그를 기다린다"


def test_the_fallback_does_not_leave_the_cart_unowned():
    """Writing innerHTML alone gets wiped by the next mzRenderCart()."""
    src = SRC.read_text(encoding="utf-8")
    start = src.index("function _mockModelzooCartFallback")
    body = src[start: src.index("\n  }", start)]
    assert "MZ.cart" in body or "_dxtPinned" in body, (
        "fallback 이 만든 카트를 아무도 소유하지 않는다"
    )


def test_the_demo_cart_is_built_from_the_chip_table():
    """Hand-written tiers silently drift when names change.

    A `{ qlite: true, qpro: false }` literal works only by accident (qmaster is
    undefined, hence falsy); the cart must be built from `MZ_CHIPS`.
    """
    body = _prep_body()
    assert not re.search(r"\{\s*qlite:", body), (
        "장바구니 모양을 손으로 적고 있다 — MZ_CHIPS 에서 만들어야 한다"
    )
