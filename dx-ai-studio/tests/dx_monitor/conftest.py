"""dx_monitor test fixtures: sys.path isolation."""
import sys
from pathlib import Path

_MONITOR_ROOT = str(Path(__file__).resolve().parent.parent.parent / "dx_monitor")


def pytest_runtest_setup(item):
    """Isolate the core modules before each monitor test."""
    for mod_name in list(sys.modules):
        if mod_name == "core" or mod_name.startswith("core."):
            del sys.modules[mod_name]
    if _MONITOR_ROOT not in sys.path:
        sys.path.insert(0, _MONITOR_ROOT)
    elif sys.path[0] != _MONITOR_ROOT:
        sys.path.remove(_MONITOR_ROOT)
        sys.path.insert(0, _MONITOR_ROOT)


def pytest_runtest_teardown(item, nextitem):
    """Clear the cached core/server modules after a monitor test."""
    for mod_name in list(sys.modules):
        if mod_name in ("core", "server") or mod_name.startswith("core."):
            del sys.modules[mod_name]
