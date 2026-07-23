"""dx_app tests import isolation.

Since Task 4b, dx_app's own source (server.py + dx_app/core/*.py) imports its
siblings via the qualified `dx_app.core.*` name instead of bare `import
config` / `from developer import ...`. Some tests here still bare-import a
dx_app.core submodule directly (`from lab_portal import create_manifest`,
`import developer`, ...) — same as before Task 4b, these bare submodule
imports are process-persistent (first-import-wins; never cleared per test,
same as pre-4b). Left un-aliased, such a bare import would now execute a
SECOND, disconnected copy of the module (`sys.modules["lab_portal"]` distinct
from `sys.modules["dx_app.core.lab_portal"]`), so state such as the manifest
store or lab sessions would silently fork between what the test sets up and
what `dx_app.server`'s routes (which import the qualified name) observe — a
pure test-harness binding concern, not a source behavior change (see Task 4b
brief's "NOTE binding subtlety"). We alias each bare submodule name to the
same persistent `dx_app.core.<name>` singleton the source now uses, once per
process (`setdefault`, never overwritten), so both spellings share identity.

`server` and `config` keep their original per-test-fresh bare reimport
(via sys.path pinning) unchanged — that predates Task 4b and is unrelated to
this fix.
"""
import importlib
import sys
from pathlib import Path

_APP_ROOT = str(Path(__file__).resolve().parent.parent.parent / "dx_app")
_APP_CORE = str(Path(__file__).resolve().parent.parent.parent / "dx_app/core")

# Every dx_app/core/*.py submodule name a test might bare-import. Aliased
# (setdefault, once) to the persistent dx_app.core.<name> singleton so it
# shares identity/state with what dx_app's qualified source sees.
_CORE_MODULES = (
    "dx_app_security", "filesystem", "assets",
    "performance", "run_config", "models", "modelzoo", "modelzoo_gateway",
    "forum", "developer", "lab_portal", "setup_steps", "inference",
    "inference_exec", "camera", "live",
)


def _clear_bare_modules():
    for mod_name in list(sys.modules):
        if mod_name in ("core", "server", "config") or mod_name.startswith(("core.", "server.")):
            del sys.modules[mod_name]


def _remove_paths(paths):
    for path in paths:
        while path in sys.path:
            sys.path.remove(path)


def _pin_paths():
    for path in (_APP_CORE, _APP_ROOT):
        if path not in sys.path:
            sys.path.insert(0, path)
        elif sys.path[0] != path:
            sys.path.remove(path)
            sys.path.insert(0, path)


def _bind_bare_core_aliases():
    """setdefault bare submodule names to their persistent dx_app.core.<name>
    singleton. Idempotent — only actually imports/binds once per process."""
    for name in _CORE_MODULES:
        if name in sys.modules:
            continue
        mod = importlib.import_module(f"dx_app.core.{name}")
        sys.modules.setdefault(name, mod)


def pytest_runtest_setup(item):
    _clear_bare_modules()
    _pin_paths()
    _bind_bare_core_aliases()


def pytest_runtest_teardown(item, nextitem):
    _clear_bare_modules()
    _remove_paths([_APP_ROOT, _APP_CORE])
