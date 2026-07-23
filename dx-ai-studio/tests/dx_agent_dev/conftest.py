"""dx_agent_dev 테스트 픽스처 — sys.path 격리."""
import importlib
import pkgutil
import sys
from pathlib import Path

_AGENT_ROOT = str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev")


def _alias_core_tree():
    """bare `core.*`(테스트 관례 표기)를 설치된 `dx_agent_dev.core.*`의 동일 모듈
    객체로 별칭 처리한다.

    소스가 `dx_agent_dev.core...` 정규화 import로 바뀐 뒤에도 테스트는 여전히 관례적으로
    `from core.x import Y` bare import를 사용한다. 별칭 없이 두면 동일 파일이 서로 다른
    두 개의 모듈 인스턴스(`core.x`와 `dx_agent_dev.core.x`)로 각각 로드되어, 예를 들어
    get_adapter()가 반환하는 클래스와 테스트가 직접 bare-import한 클래스가 `is` 비교에서
    어긋난다. sys.modules에 두 이름을 같은 객체로 등록해 단일 인스턴스를 보장한다.
    """
    import dx_agent_dev.core as _root
    sys.modules["core"] = _root
    for modinfo in pkgutil.walk_packages(_root.__path__, _root.__name__ + "."):
        mod = importlib.import_module(modinfo.name)
        alias = "core" + modinfo.name[len("dx_agent_dev.core"):]
        sys.modules[alias] = mod


def pytest_runtest_setup(item):
    """각 agent_dev 테스트 실행 전에 core 모듈 격리 보장."""
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
    """agent_dev 테스트 후 core/server 모듈 캐시 정리."""
    for mod_name in list(sys.modules):
        if mod_name in ("core", "server") or mod_name.startswith("core."):
            del sys.modules[mod_name]
