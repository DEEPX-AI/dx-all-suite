"""dx_monitor 테스트 픽스처 — sys.path 격리."""
import sys
from pathlib import Path

_MONITOR_ROOT = str(Path(__file__).resolve().parent.parent.parent / "dx_monitor")


def pytest_runtest_setup(item):
    """각 monitor 테스트 실행 전에 core 모듈 격리 보장."""
    for mod_name in list(sys.modules):
        if mod_name == "core" or mod_name.startswith("core."):
            del sys.modules[mod_name]
    if _MONITOR_ROOT not in sys.path:
        sys.path.insert(0, _MONITOR_ROOT)
    elif sys.path[0] != _MONITOR_ROOT:
        sys.path.remove(_MONITOR_ROOT)
        sys.path.insert(0, _MONITOR_ROOT)


def pytest_runtest_teardown(item, nextitem):
    """monitor 테스트 후 core/server 모듈 캐시 정리."""
    for mod_name in list(sys.modules):
        if mod_name in ("core", "server") or mod_name.startswith("core."):
            del sys.modules[mod_name]
