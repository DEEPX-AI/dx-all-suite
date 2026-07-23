"""dx-runtime benchmark 테스트 픽스처 — sibling 앱 경로 격리."""
import sys
from pathlib import Path


_BENCHMARK_DIR = (
    Path(__file__).resolve().parents[4]
    / "dx-runtime"
    / "dx_stream"
    / "dx_stream"
    / "apps"
    / "benchmark"
)
_APPS_DIR = str(_BENCHMARK_DIR.parent)


def _clear_benchmark_modules():
    for mod_name in list(sys.modules):
        if mod_name == "benchmark" or mod_name.startswith("benchmark."):
            del sys.modules[mod_name]


def _ensure_benchmark_path():
    # Require a real source file, not just the dir: a stale __pycache__ leftover
    # can keep the dir present after staging dx_stream removed the benchmark app.
    if not (_BENCHMARK_DIR / "__main__.py").is_file():
        return
    while _APPS_DIR in sys.path:
        sys.path.remove(_APPS_DIR)
    sys.path.insert(0, _APPS_DIR)


_ensure_benchmark_path()


def pytest_runtest_setup(item):
    """각 benchmark 테스트 실행 전에 dx-runtime benchmark 모듈 격리 보장."""
    _clear_benchmark_modules()
    _ensure_benchmark_path()


def pytest_runtest_teardown(item, nextitem):
    """benchmark 테스트 후 모듈 캐시 정리."""
    _clear_benchmark_modules()
