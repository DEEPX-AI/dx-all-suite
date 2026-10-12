"""dx_app Run Demo sits on the shared result stage.

Cards must not hold their own options, Run and result (``.rd-card``, ``.rundemo-result``, inline styles that
squeeze a result into a narrow card); a result drawn there stretches the card. Run Demo uses the shared component
(``shared/static/dx-demo-stage.{js,css}``) and fills in only its own options, run and result.
On-screen behaviour is covered by test_rundemo_cards_browser.py.
"""
from __future__ import annotations

import importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = (ROOT / "dx_app" / "static" / "js" / "rundemo.js").read_text(encoding="utf-8")
INF = (ROOT / "dx_app" / "static" / "js" / "inference.js").read_text(encoding="utf-8")
CSS = (ROOT / "dx_app" / "static" / "css" / "style.css").read_text(encoding="utf-8")
HTML = (ROOT / "dx_app" / "templates" / "index.html").read_text(encoding="utf-8")
gate = importlib.import_module("scripts.emoji_gate")


def test_run_demo_sits_on_the_shared_stage():
    assert "DXDemoStage.mount(" in JS
    assert HTML.index("/static/shared/dx-demo-stage.js") < HTML.index("/static/js/rundemo.js")
    assert "/static/shared/dx-demo-stage.css" in HTML


def test_the_old_in_card_result_is_gone():
    for old in (".rd-card", ".rundemo-result", ".rundemo-grid", ".rd-controls"):
        assert old not in CSS, old
    for old in ("rundemo-result-", "rundemo-block-", "_rundemoInjectStyle", "rundemoRunLive"):
        assert old not in JS, old


def test_the_postprocess_toggle_reaches_the_body():
    """sel.post is a boolean and rundemoBody checks for 'on'; a mismatch silently drops C++ postprocessing."""
    run = JS[JS.index("function rundemoRun("):]
    run = run[:run.index("\n}\n")]
    assert "post: sel.post ? 'on' : 'off'" in run


def test_no_emoji_in_the_demo_page_or_the_result():
    assert gate.count(JS) == 0, sorted({c for c in JS if gate.count(c)})
    result = INF[INF.index("window.renderInferenceError="):INF.index("function previewImg(")]
    assert gate.count(result) == 0, sorted({c for c in result if gate.count(c)})
    page = HTML[HTML.index('<div id="page-rundemo"'):]
    page = page[:page.index("</div>")]
    assert gate.count(page) == 0
