"""Root conftest — keep the repo root first on the import path."""
from pathlib import Path
import os
import sys

from tests.browser_support import resolve_chromium_executable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) in sys.path:
    sys.path.remove(str(ROOT))
sys.path.insert(0, str(ROOT))

# Tests never run a real agent CLI (copilot · claude · cursor …). With this set, the adapter refuses to
# run a real CLI from PATH (fake scripts still run); module server child processes inherit it. Without it,
# a run that names no agent falls back to copilot and, on a machine where that CLI is installed and logged
# in, really runs it. Contract: tests/dx_agent_dev/test_no_real_runs_in_tests.py
os.environ["DX_AGENT_NO_REAL_RUN"] = "1"

# Tests never touch the user's Studio settings (~/.dx-ai-studio: chat_config.json · agent.json); otherwise a
# browser test that switches the agent in Home would overwrite the agent.json of whoever runs the suite.
# The whole session points at a temp dir, inherited by module server child processes. A test that sets its own
# value with monkeypatch wins. Contract: tests/shared/test_tests_keep_user_settings.py
if not os.environ.get("DX_CHAT_CONFIG_DIR"):
    import atexit as _atexit
    import shutil as _shutil
    import tempfile as _tempfile
    os.environ["DX_CHAT_CONFIG_DIR"] = _tempfile.mkdtemp(prefix="dx-studio-cfg-")
    _atexit.register(_shutil.rmtree, os.environ["DX_CHAT_CONFIG_DIR"], True)

# Pin the root namespace first, so module tests that prepend their own top-level package paths
# cannot shadow the audit tool import.
import tools.i18n_audit  # noqa: E402,F401


def pytest_configure(config):
    """Let browser tests reuse a host Chromium when Playwright has no cache."""
    del config

    # With DX_OFFLINE_GUARD=1 the suite runs with external sockets blocked; run_ci.sh --offline
    # sets it. localhost stays open: tests start module servers and talk to them on 127.0.0.1.
    # Tiers and exceptions: docs/offline-contract.md.
    if os.environ.get("DX_OFFLINE_GUARD") == "1":
        from tests.offline_guard import install as install_offline_guard

        install_offline_guard()
    executable = resolve_chromium_executable()
    if executable is None:
        return

    try:
        from playwright.sync_api import BrowserType
    except ModuleNotFoundError:
        return

    original_launch = BrowserType.launch
    if getattr(original_launch, "_dx_system_chromium_fallback", False):
        return

    def launch_with_system_chromium(self, *args, **kwargs):
        browser_name = getattr(self, "name", None)
        if browser_name is None:
            browser_name = getattr(getattr(self, "_impl_obj", None), "name", None)
        if browser_name == "chromium":
            kwargs.setdefault("executable_path", executable)
        return original_launch(self, *args, **kwargs)

    launch_with_system_chromium._dx_system_chromium_fallback = True
    BrowserType.launch = launch_with_system_chromium


def _ensure_launcher_package():
    """Restore launcher package if a test imported launcher/launcher.py as top-level 'launcher'."""
    mod = sys.modules.get("launcher")
    if mod is not None and not hasattr(mod, "__path__"):
        for name in list(sys.modules):
            if name == "launcher" or name.startswith("launcher."):
                del sys.modules[name]


def pytest_runtest_setup(item):
    nodeid = item.nodeid
    if (
        nodeid.startswith("tests/launcher/")
        or "test_boot_animation.py" in nodeid
        or "test_dx_server_body_parsing.py" in nodeid
        or "test_launcher_wiring.py" in nodeid
    ):
        _ensure_launcher_package()
