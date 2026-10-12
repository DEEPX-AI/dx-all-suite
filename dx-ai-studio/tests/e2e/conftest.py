"""Fixtures for the inference E2E triple gate.

``DX_APP_ROOT`` is read at *import* time by ``shared.paths`` -> ``dx_app.core.config``
(which also freezes ``BUILD_DIR`` and ``CATEGORIES``). It therefore has to be set
before anything imports ``dx_app`` — module level here, not inside a fixture.

Because of that import-time freeze this package must run in its OWN pytest
process (``scripts/run_ci.sh`` runs it isolated, exactly like the Playwright
browser suites). Any module already imported with the real root is purged below
so a stray import order cannot silently pin the wrong tree.
"""
from __future__ import annotations

import atexit
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

from tests.browser_support import launch_browser, selected_engines
from tests.e2e import fake_app_root, npu_app_root

# --- import-time activation (order matters) ---------------------------------
# Failure traces land in the repo (gitignored) so CI can upload them as artifacts.
TRACE_DIR = Path(__file__).resolve().parents[2] / "var" / "e2e-traces"

# Which DX_APP_ROOT this process gets is decided ONCE, here, because
# dx_app.core.config freezes BUILD_DIR/CATEGORIES on first import. The two tiers
# therefore cannot share a pytest process — run them as separate invocations
# (run_ci.sh already does: stage 6 is `-m e2e_mock`).
NPU_TARGET = npu_app_root.resolve()

if NPU_TARGET is not None:
    _FIXTURE_ROOT, NPU_MODEL_NAME, NPU_MODEL_FILE = NPU_TARGET
    atexit.register(npu_app_root.cleanup)
else:
    NPU_MODEL_NAME = NPU_MODEL_FILE = None
    _FIXTURE_ROOT = Path(tempfile.mkdtemp(prefix="dx-e2e-approot-"))
    atexit.register(shutil.rmtree, _FIXTURE_ROOT, True)
    fake_app_root.build(_FIXTURE_ROOT)

fake_app_root.activate(_FIXTURE_ROOT)

# Result images go to a temp dir so test runs do not pile files into the user's DX App Outputs.
_OUTPUTS = Path(tempfile.mkdtemp(prefix="dx-e2e-outputs-"))
atexit.register(shutil.rmtree, _OUTPUTS, True)
os.environ["DX_STUDIO_OUTPUTS"] = str(_OUTPUTS)

for _name in [n for n in sys.modules
              if n == "dx_app" or n.startswith("dx_app.")
              or n in ("shared.paths", "shared.catalog_sources")]:
    del sys.modules[_name]
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def fixture_app_root() -> Path:
    return _FIXTURE_ROOT


@pytest.fixture(scope="session")
def npu_model() -> str:
    """The registry model name the NPU tier will drive, or skip with the reason.

    Resolution happened at import time (DX_APP_ROOT must be bound before dx_app
    is imported), so this only reports the outcome.
    """
    if NPU_TARGET is None:
        reason = npu_app_root.unavailable_reason()
        # A scheduled NPU job that SKIPS reports green while proving nothing — the
        # exact failure mode this tier exists to close. When the caller explicitly
        # asked for real hardware (run_ci.sh --npu sets this), an unavailable NPU
        # is a failure, not a skip.
        if os.environ.get("DX_E2E_NPU_STRICT") == "1":
            pytest.fail(
                f"DX_E2E_NPU_STRICT=1 but the real-NPU tier cannot run: {reason}"
            )
        pytest.skip(reason)
    return NPU_MODEL_NAME


@pytest.fixture(scope="session")
def dx_app_server():
    """Live dx_app HTTP server bound to the fixture root, on an ephemeral port."""
    from tests.server_helpers import start_module_server

    server, port = start_module_server("dx_app")
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()


@pytest.fixture(scope="session", params=selected_engines())
def browser(request):
    """One session browser per selected engine.

    Defaults to chromium alone (fast, single-engine blocking gate). The
    cross-browser job opts in via DX_BROWSER_ENGINES=chromium,firefox[,webkit].
    An engine that is downloaded but cannot launch (WebKit needs distro packages
    Playwright cannot install itself) SKIPS with the driver's own message rather
    than failing the suite — a missing system library is not a product defect.
    """
    sync_api = pytest.importorskip("playwright.sync_api")

    engine = request.param
    pw = sync_api.sync_playwright().start()
    try:
        browser_ = launch_browser(pw, engine)
    except Exception as exc:
        pw.stop()
        pytest.skip(f"{engine} unavailable on this host: {str(exc).splitlines()[0][:200]}")
    browser_.dx_engine_name = engine
    try:
        yield browser_
    finally:
        browser_.close()
        pw.stop()


@pytest.fixture()
def page(browser, request):
    """Page with Playwright tracing armed; the trace is kept only on failure.

    Keeping traces for passing runs would bury the one that matters under
    hundreds of green artifacts, so the trace is written out in teardown only
    when the test actually failed (see pytest_runtest_makereport below).
    """
    engine = getattr(browser, "dx_engine_name", "chromium")
    ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
    ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    pg = ctx.new_page()
    try:
        yield pg
    finally:
        failed = getattr(request.node, "dx_failed", False)
        if failed:
            TRACE_DIR.mkdir(parents=True, exist_ok=True)
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", request.node.name)
            target = TRACE_DIR / f"{safe}.{engine}.trace.zip"
            ctx.tracing.stop(path=str(target))
            print(f"\n[trace] failure trace written: {target}")
            print(f"[trace] open with: playwright show-trace {target}")
        else:
            ctx.tracing.stop()
        pg.close()
        ctx.close()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Expose per-phase outcome so the page fixture knows whether to keep the trace."""
    outcome = yield
    report = outcome.get_result()
    if report.when in ("setup", "call") and report.failed:
        item.dx_failed = True
