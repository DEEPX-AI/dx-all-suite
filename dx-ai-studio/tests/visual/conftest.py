"""Fixtures for the pixel visual-regression suite.

Every screenshot gets a FRESH browser context. That is not hygiene — it is what
makes the suite deterministic: reusing a context makes the second page render a
"return visit" (splash already seen, panels remembered), which on the launcher hub
alone moved 48.8% of the pixels between two captures of the same commit.
"""
from __future__ import annotations

import atexit
import os
import shutil
import tempfile

import pytest

from tests.browser_support import launch_browser, selected_engines

# dx_app's model table renders differently depending on **what is installed locally**:
# models.js's `dl = !!runnable` turns on the C++/PYTHON/MODE columns and adds a Graph
# button under ACTIONS only for installed models. Five column widths change and the whole
# table reflows, moving the baseline by up to 22% — the capture would photograph the
# developer's filesystem.
#
# Pointing at an empty directory pins "nothing installed", for the same reason
# DX_MONITOR_SKIP_HARDWARE_INIT turns off real hardware reads in dx_monitor.
# This suite runs as `pytest tests/visual/` in a **separate process** (run_ci.sh), so
# setting the environment here does not leak into other suites.
# Contract: tests/dx_app/test_models_dir_is_configurable.py
_EMPTY_MODELS_DIR = tempfile.mkdtemp(prefix="dx-visual-empty-models-")
atexit.register(shutil.rmtree, _EMPTY_MODELS_DIR, True)
os.environ.setdefault("DX_APP_MODELS_DIR", _EMPTY_MODELS_DIR)

# For the same reason the dx_agent_dev console's agent dropdown is pinned. Otherwise the
# capture shows what is on PATH and which CLIs are logged in (a VS Code session putting
# copilot on PATH would break 8 shots with no code change).
# Contract: tests/dx_agent_dev/test_agents_can_be_pinned.py
# Two agents, so the multi-agent layout with the picker visible is captured
# (console.js updateAgentPickerLayout).
os.environ.setdefault("DX_AGENT_DEV_PIN_AGENTS", "claude,cursor")

# Applied before any page script runs, so neither the splash nor the tutorial
# walkthrough enters the capture.
STABILISE_INIT = """
() => {
  try {
    sessionStorage.setItem('dx-splash-seen', '1');
    localStorage.setItem('dx-splash-seen', '1');
    // The launcher — and only the launcher — auto-RUNS the walkthrough on a first
    // visit (tutorial-init.js), which scrolls the page to the toggle step and
    // opens a popover over a dimmed backdrop. hideTOC() closes the table of
    // contents, not a running tour, so eight launcher baselines were photographs
    // of a dimmed footer: the hub's actual landing layout was never in frame.
    // Marking the walkthrough as already run drops the launcher onto the same
    // showTOC() path as every module, which hideTOC() does handle.
    localStorage.setItem('dx-tutorial-launcher-autostarted', '1');
  } catch (e) { /* private mode — the settle wait still covers it */ }
}
"""


@pytest.fixture(scope="session", params=selected_engines())
def visual_browser(request):
    sync_api = pytest.importorskip("playwright.sync_api")

    pw = sync_api.sync_playwright().start()
    try:
        browser = launch_browser(pw, request.param)
    except Exception as exc:  # engine not installed on this host
        pw.stop()
        pytest.skip(f"{request.param} unavailable: {type(exc).__name__}: {exc}")
    try:
        yield request.param, browser
    finally:
        browser.close()
        pw.stop()
