"""Module open / close transition: one path to open, and the document is never reloaded."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "launcher" / "static"
FRAME = (STATIC / "launcher-app-frame.js").read_text(encoding="utf-8")
ANSWER = (STATIC / "home-answer.js").read_text(encoding="utf-8")
STYLE = (STATIC / "style.css").read_text(encoding="utf-8")


def _fn(src: str, name: str) -> str:
    start = src.index("function " + name + "(")
    return src[start:src.index("\n  }", start)]


def test_launch_takes_options_and_still_takes_a_query_string():
    body = _fn(FRAME, "launch")
    assert "typeof" in body and "from" in body, "launch 가 { from } 을 받지 않는다"
    assert "query" in body


def test_home_icons_open_from_themselves():
    routing = _fn(FRAME, "initHomeClickRouting")
    assert "launch(card.dataset.app, { from: card })" in routing


def test_the_answer_leaves_through_launch_not_a_reload():
    """Passing a string to loadAppIframeIfNeeded throws → catch → location.href reloads the document."""
    body = _fn(ANSWER, "_leaveHome")
    assert "loadAppIframeIfNeeded" not in body
    assert "ns2.launch(" in body
    assert "from:" in body and "hash" in body
    route = _fn(ANSWER, "_openRoute")
    assert "_leaveHome(path, btn)" in route


def test_the_hash_rides_into_the_iframe_and_history():
    show = FRAME[FRAME.index("function _showApp(appKey, opts)"):FRAME.index("function navigate(target, opts)")]
    assert "if (opts.hash) iframePath += opts.hash" in show
    assert "if (opts.hash) historyUrl += opts.hash" in show


def test_the_open_and_close_lengths_are_the_spec_ones():
    assert re.search(r"OPEN_MS\s*=\s*420\b", FRAME)
    assert re.search(r"CLOSE_MS\s*=\s*360\b", FRAME)


def test_the_veil_moves_not_the_iframe():
    """Scaling the iframe repaints the whole module every frame; only a plain colour panel moves."""
    veil = FRAME[FRAME.index("function _makeVeil("):FRAME.index("function playClose(")]
    assert "open-veil" in veil and ".animate(" in veil
    assert "iframe" not in veil
    assert "prefers-reduced-motion: reduce" in FRAME[FRAME.index("function _veilStill("):]
    assert re.search(r"\.open-veil\s*\{[^}]*position:\s*fixed", STYLE)
    assert re.search(r"\.open-veil\s*\{[^}]*pointer-events:\s*none", STYLE)
