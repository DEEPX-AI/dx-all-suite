"""Home starts on the Studio agent and saves a change, so Chat follows it."""
from __future__ import annotations

import json

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

_QUIET = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
          "localStorage.setItem('dx-tutorial-launcher-autostarted','1');localStorage.setItem('dx-tutorial-mode','off');"
          "localStorage.setItem('dx-lang','en')}catch(e){}")
AGENTS = [{"name": n, "models": ["auto", "m1"], "default_model": "auto", "authenticated": a,
           "reasoning_efforts": [], "default_effort": None}
          for n, a in (("copilot", True), ("claude", True), ("cursor", False))]


@pytest.fixture(scope="module")
def port():
    srv, port = start_module_server("launcher")
    yield port
    srv.shutdown()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


def _home(browser, port, studio):
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script(_QUIET)
    saved = []
    status = {"available": True, "agents": AGENTS, "studio_agent": studio, "busy": False, "showcase_count": 0}
    ctx.route("**/agent/api/agent/status", lambda r: r.fulfill(status=200, content_type="application/json",
                                                               body=json.dumps(status)))
    ctx.route("**/agent/api/agent/models*", lambda r: r.fulfill(status=200, content_type="application/json",
                                                                body='{"models": ["auto", "m1", "m2"], "default_model": "auto"}'))
    ctx.route("**/api/studio/agent", lambda r: (saved.append(json.loads(r.request.post_data)),
                                                r.fulfill(status=200, content_type="application/json", body='{"ok":true}')))
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
    page.wait_for_selector("#setupForm:not([hidden])", state="attached", timeout=20000)
    return ctx, page, saved


def test_home_starts_on_the_studio_agent(browser, port):
    ctx, page, _ = _home(browser, port, {"agent": "claude", "model": "m1"})
    try:
        assert page.evaluate("document.getElementById('setupAgent').value") == "claude"
    finally:
        ctx.close()


def test_without_a_choice_home_starts_on_the_first_signed_in_in_studio_order(browser, port):
    ctx, page, _ = _home(browser, port, None)
    try:
        assert page.evaluate("document.getElementById('setupAgent').value") == "claude"   # claude before copilot
    finally:
        ctx.close()


def test_changing_the_agent_saves_it(browser, port):
    ctx, page, saved = _home(browser, port, None)
    try:
        page.click("#setupFold > summary")
        page.select_option("#setupAgent", "copilot")
        page.wait_for_function("1", timeout=1000)
        page.wait_for_timeout(300)
        assert saved and saved[-1]["agent"] == "copilot"
    finally:
        ctx.close()


def test_a_saved_model_only_the_cli_lists_is_kept(browser, port):
    """The static table has auto/m1; m2 comes from the CLI later (cursor lists 200+). The saved m2 must win then."""
    ctx, page, _ = _home(browser, port, {"agent": "claude", "model": "m2"})
    try:
        page.wait_for_function("document.getElementById('setupModel').value === 'm2'", timeout=10000)
    finally:
        ctx.close()


def test_a_model_the_user_picks_beats_the_saved_one(browser, port):
    """With a saved Studio model, a model the user picked before the CLI's list arrived must not be replaced by
    the saved one when the list comes. The user's own pick wins."""
    import json as _json
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script(_QUIET)
    held = []
    status = {"available": True, "agents": AGENTS, "studio_agent": {"agent": "claude", "model": "m2"},
              "busy": False, "showcase_count": 0}
    ctx.route("**/agent/api/agent/status", lambda r: r.fulfill(status=200, content_type="application/json",
                                                               body=_json.dumps(status)))
    ctx.route("**/agent/api/agent/models*", lambda r: held.append(r))
    ctx.route("**/api/studio/agent", lambda r: r.fulfill(status=200, content_type="application/json", body='{"ok":true}'))
    page = ctx.new_page()
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
        page.wait_for_selector("#setupForm:not([hidden])", state="attached", timeout=20000)
        page.click("#setupFold > summary")
        page.select_option("#setupModel", "m1")              # picked while the CLI list is still on its way
        page.wait_for_function("document.querySelectorAll('#setupModel option').length > 0")
        for r in held:
            r.fulfill(status=200, content_type="application/json",
                      body='{"models": ["auto", "m1", "m2"], "default_model": "auto"}')
        page.wait_for_timeout(500)
        assert page.evaluate("document.getElementById('setupModel').value") == "m1"
    finally:
        ctx.close()
