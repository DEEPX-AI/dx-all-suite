"""dx_stream Setup uses the shared step list (DXSteps).

One vertical list, as in dx_app: finished steps collapse to one line and only the next step is expanded, with no
emoji on cards or buttons. The flow covers the sudo re-prompt, append-only log polling, Run All and download
progress.
"""
from __future__ import annotations

import importlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "dx_stream" / "templates" / "index.html").read_text(encoding="utf-8")
SETUP_JS = (ROOT / "dx_stream" / "static" / "js" / "stream-setup.js").read_text(encoding="utf-8")
TUTORIAL = (ROOT / "dx_stream" / "static" / "js" / "tutorial.js").read_text(encoding="utf-8")
gate = importlib.import_module("scripts.emoji_gate")

# (step id = POST path, badge id, log id)
STEPS = [("stream-deps", "stream-deps", "stream-deps"), ("runtime-deps", "runtime", "runtime"),
         ("driver", "driver", "driver"), ("build", "build", "build"),
         ("download-models", "download", "download"), ("webrtc-deps", "webrtc-deps", "webrtc-deps")]


def _page() -> str:
    start = HTML.index('<div class="page" id="page-setup"')
    return HTML[start:HTML.index("<!-- ═══ PAGE:", start + 10)]


def test_the_page_is_one_step_list():
    page = _page()
    assert page.count('class="dx-steps"') == 1 and "data-steps" in page
    assert re.findall(r'<li class="dx-step" data-step="([^"]+)"', page) == [s for s, _, _ in STEPS]
    assert "setup-grid" not in page and "setup-card" not in page, "옛 2열 카드 격자가 남아 있다"
    assert '<script src="/static/shared/dx-steps.js"></script>' in HTML


def test_every_step_keeps_its_ids_and_handlers():
    """The tutorial resolves targets by onclick string and id (tests/dx_stream/test_tutorial.py)."""
    page = _page()
    for step, badge, log in STEPS:
        li = page[page.index(f'data-step="{step}"'):]
        li = li[:li.index("</li>")]
        assert f'id="setup-badge-{badge}"' in li and 'class="dx-step-state"' in li, step
        assert f"onclick=\"DXStream.runSetup('{step}')\"" in li, step
        assert f"onclick=\"DXStream.clearLog('{log}')\"" in li, step
        assert f'id="setup-log-{log}"' in li, step
    for kept in ('id="setup-run-all"', 'id="setup-stop-btn"', 'id="setup-info-bar"', 'id="setup-opt-clean"',
                 'id="setup-opt-debug"', 'id="setup-download-progress"', 'id="setup-download-fill"',
                 'id="setup-download-text"', 'id="setup-env-tbody"', 'id="stream-diag-run-btn"'):
        assert kept in page, kept


def test_the_header_counts_and_runs_the_rest():
    page = _page()
    assert "data-steps-count" in page and 'class="dx-steps-bar"' in page
    run = re.search(r'<button[^>]*id="setup-run-all"[^>]*>', page).group(0)
    assert "data-steps-run" in run


def test_logs_start_hidden():
    """The log box appears when a run starts, not as an empty box on every card."""
    for tag in re.findall(r'<pre[^>]*id="setup-log-[^"]+"[^>]*>', _page()):
        assert 'style="display:none"' in tag, tag
    poll = SETUP_JS[SETUP_JS.index("function _startLogPoll("):]
    assert "logEl.style.display = ''" in poll[:600]


def test_no_emoji_left_in_setup():
    assert gate.count(_page()) == 0, sorted({c for c in _page() if gate.count(c)})
    assert gate.count(SETUP_JS) == 0, sorted({c for c in SETUP_JS if gate.count(c)})


def test_setup_js_reports_state_instead_of_painting_badges():
    assert "DXSteps.set(" in SETUP_JS
    assert "cs-ok" not in SETUP_JS and "cs-warn" not in SETUP_JS


def test_run_all_only_runs_what_is_left():
    body = SETUP_JS[SETUP_JS.index("DXStream.setupRunAll = "):]
    body = body[:body.index("\n};")]
    assert "dataset.state !== 'done'" in body
    assert body.index("steps.filter(") < body.index("inputModal("), "끝난 단계만 남았는데 sudo 부터 묻는다"


def test_the_flows_are_untouched():
    for needle in ("_sudoSteps", "result.data.error === 'sudo_auth'", "_appendSetupLog(logEl, r.log);",
                   "if (!_streamSetupVisible()) return;", r"/\[PROGRESS\]\s*(\d+)\/(\d+)/", "_postSetupBody(stepId, body)"):
        assert needle in SETUP_JS, needle


def test_the_setup_tutorial_opens_collapsed_steps_before_pointing_into_them():
    sec = TUTORIAL[re.search(r"id:\s*'setup'", TUTORIAL).start():]
    sec = sec[:sec.index("\n    },", 10)]
    assert "'.setup-grid'" not in sec
    for step, sel in (("stream-deps", 'button[onclick*="stream-deps"]'), ("runtime-deps", 'button[onclick*="runtime-deps"]'),
                      ("driver", 'button[onclick*="driver"]'), ("build", "#setup-opt-clean"),
                      ("build", 'button[onclick*="build"]'), ("download-models", 'button[onclick*="download-models"]'),
                      ("webrtc-deps", 'button[onclick*="webrtc-deps"]')):
        at = sec.index(f"target: '{sel}'")
        nxt = sec.find("{ target:", at + 10)
        body = sec[at:nxt if nxt != -1 else len(sec)]
        assert f"_openSetupStep('{step}')" in body, sel
