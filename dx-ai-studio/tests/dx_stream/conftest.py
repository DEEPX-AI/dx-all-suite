"""dx_stream 테스트 픽스처 — sys.path 격리."""
import sys
from pathlib import Path

from tests.dx_stream._stream_import import pin_stream_core

_STREAM_ROOT = str(Path(__file__).resolve().parent.parent.parent / "dx_stream")


def pytest_runtest_setup(item):
    """각 stream 테스트 실행 전에 core 모듈 격리 보장."""
    pin_stream_core()


def pytest_runtest_teardown(item, nextitem):
    """stream 테스트 후 core/server 모듈 캐시 정리."""
    for mod_name in list(sys.modules):
        if mod_name in ("core", "server") or mod_name.startswith("core."):
            del sys.modules[mod_name]
