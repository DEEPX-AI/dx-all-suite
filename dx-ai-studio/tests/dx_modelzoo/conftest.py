"""dx_modelzoo 테스트 픽스처 — sys.path 격리 + generated catalog bootstrap."""
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
    """core/server 모듈 캐시 제거 + zoo 경로를 sys.path 최상위로."""
    for mod_name in list(sys.modules):
        if mod_name in ("core", "server") or mod_name.startswith("core."):
            del sys.modules[mod_name]
    # stream 경로를 임시 제거하고 zoo를 맨 앞으로
    while _STREAM_ROOT in sys.path:
        sys.path.remove(_STREAM_ROOT)
    if _ZOO_ROOT in sys.path:
        sys.path.remove(_ZOO_ROOT)
    sys.path.insert(0, _ZOO_ROOT)


def pytest_sessionstart(session):
    _ensure_generated_catalog()


def pytest_runtest_setup(item):
    """각 modelzoo 테스트 실행 전 격리."""
    _isolate_zoo()


def pytest_runtest_teardown(item, nextitem):
    """modelzoo 테스트 후 정리 — stream 경로 복원."""
    for mod_name in list(sys.modules):
        if mod_name in ("core", "server") or mod_name.startswith("core."):
            del sys.modules[mod_name]
    # stream 경로 복원 (stream 테스트가 나중에 실행될 수 있음)
    if _STREAM_ROOT not in sys.path:
        sys.path.append(_STREAM_ROOT)
