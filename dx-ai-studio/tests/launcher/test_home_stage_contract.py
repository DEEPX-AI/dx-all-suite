"""Skeleton of the launcher home stage.

Each role has its place: tour · hero · work · deck (widget · icons · widget) · bar below.
This file checks the places and what is gone. Size and one-screen fit are checked by test_home_stage_browser.py.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "launcher" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")


def _css() -> str:
    """Checking an empty string when the file is missing would make every 'forbidden' contract pass by itself."""
    path = STATIC / "home-stage.css"
    assert path.is_file(), "launcher/static/home-stage.css 가 없다"
    return path.read_text(encoding="utf-8")


def _region(region_id: str) -> str:
    """From the opening tag with the id until the matching closing tag of the same name."""
    m = re.search(r"<(\w+)\b[^>]*\bid=\"" + region_id + r"\"", HTML)
    assert m, f"#{region_id} 가 없다"
    tag, start, depth = m.group(1), m.start(), 0
    for t in re.finditer(r"<(/?)" + tag + r"\b[^>]*>", HTML[start:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return HTML[start:start + t.end()]
    raise AssertionError(f"#{region_id} 가 닫히지 않는다")


def test_regions_appear_in_reading_order():
    order = ["homeTour", "homeStage", "homeStageWork", "homeDeck", "homeBar"]
    positions = [HTML.index(f'id="{r}"') for r in order]
    assert positions == sorted(positions), order


@pytest.mark.parametrize("region,ids", [
    ("homeStage", ["homeAskForm", "homeAsk", "homeAskChips", "setupFold", "setupDegraded",
                   "landingPoster", "ecosystemPoster"]),
    ("homeStageWork", ["homeAnswer", "homeWork", "answerClose", "workClose"]),
    ("homeDevice", ["heroDeviceChip", "homeCores", "homeDeviceLine",
                    "studioVersionHub", "hubLauncherPort"]),
    ("homeMeasured", ["measuredCount"]),
    ("homeBar", ["deepxLinks", "studioVersionFooter"]),
    ("homeTour", ["replayBtn"]),
])
def test_each_element_lives_in_its_region(region, ids):
    body = _region(region)
    for i in ids:
        assert f'id="{i}"' in body, f"#{i} 가 #{region} 밖에 있다"


def test_the_agent_line_belongs_to_the_input():
    assert 'id="setupFold"' in _region("homeAskForm")


def test_deck_holds_two_widgets_around_the_grid():
    deck = _region("homeDeck")
    a, g, b = (deck.index(f'id="{i}"') for i in ("homeDevice", "studioGrid", "homeMeasured"))
    assert a < g < b


def test_grid_is_eleven_tiles_in_spec_order():
    grid = _region("studioGrid")
    tiles = re.findall(r'class="(orbital-card|about-book-card(?: sdk-card)?)"(?:[^>]*data-app="(\w+)")?', grid)
    got = [app or ("sdk" if "sdk" in cls else "about") for cls, app in tiles]
    assert got == ["app", "stream", "zoo", "compiler", "benchmark", "planner",
                   "dx_monitor", "agent", "edge", "sdk", "about"]


@pytest.mark.parametrize("gone", [
    'id="portalNav"', 'class="portal-nav', 'id="measured"', 'id="perfRows"', 'id="measuredCats"',
    'id="measuredSearch"', 'id="measuredEmpty"', 'id="perfAll"', 'id="wsRunning"',
    'id="moduleUpCount"', 'class="ws-flow"', 'class="ws-side"', 'id="resources"',
    'class="studio-col"', 'class="studio-group"', 'class="landing-footer"', 'id="workspace"',
])
def test_removed_parts_are_gone(gone):
    assert gone not in HTML


def test_stage_css_is_loaded_after_style_css():
    assert HTML.index('href="/style.css"') < HTML.index('href="/home-stage.css"')


def test_launcher_serves_the_stage_css():
    assert 'path == "/home-stage.css"' in (ROOT / "launcher" / "launcher.py").read_text(encoding="utf-8")


def test_docked_state_is_derived_from_what_is_visible():
    """While working, the stage makes room for the work, which takes the full width. If JS toggled that with a
    class, every path that opens an answer would have to remember it; :has() cannot be forgotten."""
    for panel in ("homeAnswer", "homeWork"):
        assert f"#landing:has(#{panel}:not([hidden]))" in _css(), panel
    console_js = (STATIC / "home-console.js").read_text(encoding="utf-8")
    assert "$('workspace')" not in console_js, "옛 오른쪽 열 토글이 남아 있다"
    for js in ("home-console.js", "home-answer.js"):
        assert "is-docked" not in (STATIC / js).read_text(encoding="utf-8"), js


def test_home_places_nothing_with_absolute_or_fixed():
    """The tour and bar are placed by the grid too; no overlapping floating furniture."""
    body = re.sub(r"/\*.*?\*/", "", _css(), flags=re.S)
    assert not re.search(r"position\s*:\s*(absolute|fixed)", body)


def test_stage_css_breakpoints_come_from_the_scale():
    """Read @media conditions only; scanning the whole file would read a tooltip's max-width: 200px as a
    breakpoint (same scope as scripts/breakpoint_gate.py)."""
    for query in re.findall(r"@media([^{]*)\{", _css()):
        for w in re.findall(r"(?:max|min)-width:\s*(\d+)px", query):
            assert int(w) in (600, 900, 1200, 1440), w
