"""dx_app Setup uses the shared step list (DXSteps).

One vertical list: finished steps collapse to a single line and only the next step expands, so the order reads
top to bottom and it is clear what to press next. The flow (sudo, log, Run All, demos, hidden inference-venv) is
unchanged.
"""
from __future__ import annotations

import importlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "dx_app" / "templates" / "index.html").read_text(encoding="utf-8")
SETUP_JS = (ROOT / "dx_app" / "static" / "js" / "setup.js").read_text(encoding="utf-8")
TUTORIAL = (ROOT / "dx_app" / "static" / "js" / "tutorial.js").read_text(encoding="utf-8")
gate = importlib.import_module("scripts.emoji_gate")

STEPS = ["dx-app-deps", "dx-rt-deps", "dx-rt-build", "dx-driver", "dx-app-build", "dx-app-setup"]


def _page() -> str:
    start = HTML.index('<div id="page-setup"')
    return HTML[start:HTML.index("<!-- ═══ PAGE:", start + 10)]


def test_the_page_is_one_step_list():
    page = _page()
    assert page.count('class="dx-steps"') == 1 and "data-steps" in page
    assert re.findall(r'<li class="dx-step" data-step="([^"]+)"', page) == STEPS
    assert "setup-grid" not in page, "옛 2열 카드 격자가 남아 있다"


def test_every_step_keeps_its_ids_and_handler():
    """Tutorial targets resolve only through the template's onclick strings and ids (tests/dx_app/test_tutorial.py)."""
    page = _page()
    for step in STEPS:
        li = page[page.index(f'data-step="{step}"'):]
        li = li[:li.index("</li>")]
        assert f'id="setup-badge-{step}"' in li and 'class="dx-step-state"' in li, step
        assert f'id="setup-detail-{step}"' in li, step
        assert f"onclick=\"setupRun('{step}')\"" in li, step
    for kept in ('id="setup-run-all"', 'id="setup-quickstart-btn"', 'id="setup-stop-btn"', 'id="setup-log"',
                 'id="diag-run-btn"', 'id="setup-version-card"', 'id="setup-try-demo"'):
        assert kept in page, kept


def test_the_header_counts_and_runs_the_rest():
    page = _page()
    assert "data-steps-count" in page and 'class="dx-steps-bar"' in page
    run = re.search(r'<button[^>]*id="setup-run-all"[^>]*>', page).group(0)
    assert "data-steps-run" in run


def test_no_emoji_left_in_setup():
    assert gate.count(_page()) == 0, sorted({c for c in _page() if gate.count(c)})
    assert gate.count(SETUP_JS) == 0, sorted({c for c in SETUP_JS if gate.count(c)})


def test_setup_js_reports_state_instead_of_painting_badges():
    assert "DXSteps.set(" in SETUP_JS
    assert "comp-status-badge cs-ok" not in SETUP_JS and "comp-status-badge cs-warn" not in SETUP_JS


def test_the_flows_are_untouched():
    """sudo re-prompt · append-only log · remembering the step just finished · hidden inference-venv · demo_only."""
    for needle in ("SETUP_SUDO_STEPS", "setupPromptSudoPassword", "compRenderLogAppend(logEl,r.log,SETUP);",
                   "setupCheckAll().then(function(){setupMarkStepDone(completedStep);});",
                   "'inference-venv'", "demo_only"):
        assert needle in SETUP_JS, needle


def test_the_setup_tutorial_opens_collapsed_steps_before_pointing_at_them():
    """A finished step collapses to zero size, so pointing at a button inside it sends the journey to TARGET_HIDDEN."""
    sec = TUTORIAL[re.search(r"id:\s*'setup'", TUTORIAL).start():]
    sec = sec[:sec.index("\n    },", 10)]
    for step in STEPS:
        m = re.search(r"target:\s*'button\[onclick\*=\"" + re.escape(step) + r"\"\]'(.{0,400})", sec, re.S)
        assert m, step
        assert f"DXSteps.open" in m.group(1) or "_openSetupStep('" + step + "')" in m.group(1), step


def test_backend_details_are_words_not_marks():
    src = (ROOT / "dx_app" / "core" / "setup_steps.py").read_text(encoding="utf-8")
    body = src[src.index("def setup_status("):]
    body = body[:body.index("\ndef ", 10)]
    assert gate.count(body) == 0, sorted({c for c in body if gate.count(c)})
