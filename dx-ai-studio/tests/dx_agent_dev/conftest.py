"""dx_agent_dev test fixtures: sys.path isolation."""
import importlib
import pkgutil
import sys
from pathlib import Path

_AGENT_ROOT = str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev")


def _alias_core_tree():
    """Alias bare `core.*` (the tests' import convention) to the same module objects as `dx_agent_dev.core.*`.

    The source imports `dx_agent_dev.core...`, while tests use `from core.x import Y`. Without the alias one
    file loads as two module instances (`core.x` and `dx_agent_dev.core.x`), so e.g. the class get_adapter()
    returns and the class a test imported fail an `is` check. Registering both names to one object in
    sys.modules keeps a single instance.
    """
    import dx_agent_dev.core as _root
    sys.modules["core"] = _root
    for modinfo in pkgutil.walk_packages(_root.__path__, _root.__name__ + "."):
        mod = importlib.import_module(modinfo.name)
        alias = "core" + modinfo.name[len("dx_agent_dev.core"):]
        sys.modules[alias] = mod


def pytest_runtest_setup(item):
    """Isolate the core modules before each agent_dev test."""
    for mod_name in list(sys.modules):
        if mod_name == "core" or mod_name.startswith("core."):
            del sys.modules[mod_name]
    if _AGENT_ROOT not in sys.path:
        sys.path.insert(0, _AGENT_ROOT)
    elif sys.path[0] != _AGENT_ROOT:
        sys.path.remove(_AGENT_ROOT)
        sys.path.insert(0, _AGENT_ROOT)
    _alias_core_tree()


def pytest_runtest_teardown(item, nextitem):
    """Clear the cached core/server modules after each agent_dev test."""
    for mod_name in list(sys.modules):
        if mod_name in ("core", "server") or mod_name.startswith("core."):
            del sys.modules[mod_name]
