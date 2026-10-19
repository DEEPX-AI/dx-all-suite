"""dx_stream test fixtures — sys.path isolation."""
import sys
from pathlib import Path

from tests.dx_stream._stream_import import pin_stream_core

_STREAM_ROOT = str(Path(__file__).resolve().parent.parent.parent / "dx_stream")


def pytest_runtest_setup(item):
    """Isolate the core modules before each stream test."""
    pin_stream_core()


def pytest_runtest_teardown(item, nextitem):
    """Clear the core/server module cache after stream tests."""
    for mod_name in list(sys.modules):
        if mod_name in ("core", "server") or mod_name.startswith("core."):
            del sys.modules[mod_name]
