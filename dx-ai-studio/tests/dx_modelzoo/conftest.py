"""dx_modelzoo test fixtures: sys.path isolation and generated catalog bootstrap."""
import subprocess
import sys
from pathlib import Path

_STUDIO_ROOT = Path(__file__).resolve().parent.parent.parent
_ZOO_ROOT = str(_STUDIO_ROOT / "dx_modelzoo")
_STREAM_ROOT = str(_STUDIO_ROOT / "dx_stream")
_GENERATED_CATALOG = _STUDIO_ROOT / "dx_modelzoo" / "data" / "generated_catalog.json"
_SYNC_SCRIPT = _STUDIO_ROOT / "dx_modelzoo" / "tools" / "sync_metadata.py"


def _ensure_generated_catalog():
    """generated_catalog.json is gitignored; create offline when missing."""
    if _GENERATED_CATALOG.is_file():
        return
    if not _SYNC_SCRIPT.is_file():
        return
    bootstrap_cache = _STUDIO_ROOT / "dx_modelzoo" / "data" / ".pytest_bootstrap.cache.json"
    subprocess.run(
        [
            sys.executable,
            str(_SYNC_SCRIPT),
            "--offline",
            "--cache",
            str(bootstrap_cache),
        ],
        cwd=str(_STUDIO_ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    bootstrap_cache.unlink(missing_ok=True)


def _isolate_zoo():
    """Drop the cached core/server modules and put the zoo path first on sys.path."""
    for mod_name in list(sys.modules):
        if mod_name in ("core", "server") or mod_name.startswith("core."):
            del sys.modules[mod_name]
    # Remove the stream path for now and put the zoo first
    while _STREAM_ROOT in sys.path:
        sys.path.remove(_STREAM_ROOT)
    if _ZOO_ROOT in sys.path:
        sys.path.remove(_ZOO_ROOT)
    sys.path.insert(0, _ZOO_ROOT)


def pytest_sessionstart(session):
    _ensure_generated_catalog()


def pytest_runtest_setup(item):
    """Isolate before each modelzoo test."""
    _isolate_zoo()


def pytest_runtest_teardown(item, nextitem):
    """Clean up after a modelzoo test: restore the stream path."""
    for mod_name in list(sys.modules):
        if mod_name in ("core", "server") or mod_name.startswith("core."):
            del sys.modules[mod_name]
    # Restore the stream path (stream tests may run later)
    if _STREAM_ROOT not in sys.path:
        sys.path.append(_STREAM_ROOT)
