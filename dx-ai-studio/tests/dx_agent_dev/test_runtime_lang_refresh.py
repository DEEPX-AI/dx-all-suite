"""DX Agent Dev runtime language refresh contracts."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONSOLE = ROOT / "dx_agent_dev/static/js/console.js"


def _func_body(name):
    src = CONSOLE.read_text(encoding="utf-8")
    marker = "function " + name + "("
    start = src.index(marker)
    rest = src[start + len(marker):]
    nxt = re.search(r"\n  (?:async )?function ", rest)
    return rest[:nxt.start()] if nxt else rest


def test_applylang_refreshes_model_picker_and_turns():
    body = _func_body("applyLang")
    assert "fillModels(agent)" in body
    assert "relocalizeOpenTurns()" in body
    assert "relocalizeStatusBar()" in body


def test_status_line_uses_i18n_key_not_text_compare():
    src = CONSOLE.read_text(encoding="utf-8")
    assert "getAttribute('data-i18n-key')" in src
    assert "textContent === T('Agent running..." not in src
