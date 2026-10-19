"""Home's module list carries the numbers each module reports about itself.

Eight rows of a name plus one line of prose do not tell modules apart, and the list reads as one block.
The Model Zoo approach (`/zoo/api/catalog` through the proxy, written into `.card-desc`, e.g.
`347 models · 22 tasks`) applies to the others too.

**One table.** One function per module would add another copy with every new module, a pattern this
repo avoids elsewhere (`_CHIP_DIRS`, `MZ_CHIPS`).

Compiler and EdgeGuide are left out on purpose: they have nothing to count (`/api/listdir`, `/api/mkdir`
and `/api/hb` only), and adding an endpoint just to show a number is not the goal. Keeping the asymmetry
is the honest choice.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "launcher" / "static" / "home-sections.js"


def source() -> str:
    assert SRC.is_file(), "launcher/static/home-sections.js is missing"
    return SRC.read_text(encoding="utf-8")


def _facts_block() -> str:
    src = source()
    m = re.search(r"MODULE_FACTS\s*=\s*\[(.*?)\n\s*\];", src, re.S)
    assert m, "MODULE_FACTS 표가 없다 — 모듈마다 함수를 따로 두면 안 된다"
    return m.group(1)


def test_every_module_with_a_number_is_in_the_table():
    block = _facts_block()
    for app in ("zoo", "app", "stream", "agent", "benchmark", "dx_monitor"):
        assert f"'{app}'" in block, f"MODULE_FACTS 에 {app} 이 없다"


def test_modules_with_nothing_to_count_are_left_out():
    """Compiler and EdgeGuide have nothing to count; forcing them in would produce empty numbers."""
    block = _facts_block()
    for app in ("compiler", "planner"):
        assert f"'{app}'" not in block, (
            f"{app} 은 셀 API 가 없는데 MODULE_FACTS 에 있다"
        )


def test_each_entry_fetches_through_the_launcher_proxy():
    """Each module is on its own port; home reaches them only through the launcher proxy (/zoo/, /app/ …)."""
    block = _facts_block()
    urls = re.findall(r"url:\s*'([^']+)'", block)
    assert len(urls) >= 6, f"url 이 {len(urls)}개뿐이다"
    for u in urls:
        assert u.startswith("/"), f"프록시 경로가 아니다: {u}"
        assert "://" not in u, f"절대 URL 은 프록시를 우회한다: {u}"


def test_counts_are_written_to_the_description_not_the_state_slot():
    """`card-state` belongs to Running. A number taking that slot would hide the state."""
    src = source()
    paint = src[src.index("function _paintFacts") :] if "function _paintFacts" in src else ""
    assert paint, "_paintFacts 가 없다"
    body = paint[: paint.index("\n  }")]
    assert "card-desc" in body, "숫자는 설명 줄에 써야 한다"
    assert "card-state" not in body, "숫자가 Running 상태 슬롯을 덮어쓴다"
    assert "data-role=\"state\"" not in body
