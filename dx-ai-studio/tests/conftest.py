"""Root conftest — repo root import 우선순위를 안정화한다."""
from pathlib import Path
import os
import sys

from tests.browser_support import resolve_chromium_executable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) in sys.path:
    sys.path.remove(str(ROOT))
sys.path.insert(0, str(ROOT))

# test 는 진짜 agent CLI (copilot · claude · cursor …) 를 돌리지 않는다. adapter 가 이 값을 보고
# PATH 의 진짜 CLI 실행을 거절한다 (가짜 script 는 그대로). module server 하위 process 도 물려받는다.
# agent 를 지정하지 않은 실행이 기본 copilot 으로 가서, CLI 를 설치 · 로그인하자 test 한 번에 실제
# 실행이 12번 돌았다 (2026-09-30). 계약: tests/dx_agent_dev/test_no_real_runs_in_tests.py
os.environ["DX_AGENT_NO_REAL_RUN"] = "1"

# test 는 사용자의 Studio 설정 (~/.dx-ai-studio: chat_config.json · agent.json) 을 건드리지 않는다. Home 이 고른 agent 를
# 저장하게 되자 (2026-10-11 chat settings) agent 를 바꾸는 browser test 가 실행한 사람의 agent.json 을 썼다.
# 세션 전체를 임시 폴더로 돌린다 — module server 하위 process 도 물려받는다. test 가 monkeypatch 로 따로 정하면 그것이 이긴다.
# 계약: tests/shared/test_tests_keep_user_settings.py
if not os.environ.get("DX_CHAT_CONFIG_DIR"):
    import tempfile as _tempfile
    os.environ["DX_CHAT_CONFIG_DIR"] = _tempfile.mkdtemp(prefix="dx-studio-cfg-")

# 일부 모듈 테스트가 자체 top-level package 경로를 앞에 추가해도 감사 도구 import가
# 흔들리지 않도록 root namespace를 먼저 고정한다.
import tools.i18n_audit  # noqa: E402,F401


def pytest_configure(config):
    """Let browser tests reuse a host Chromium when Playwright has no cache."""
    del config

    # DX_OFFLINE_GUARD=1 이면 외부 소켓을 막은 채로 돈다. run_ci.sh --offline 이
    # 이것을 켠다 — 폐쇄망에서 개발하던 시절에는 환경이 해주던 일이다.
    # localhost 는 막지 않는다: 테스트가 모듈 서버를 띄워 127.0.0.1 로 말한다.
    # 등급과 예외는 docs/offline-contract.md.
    if os.environ.get("DX_OFFLINE_GUARD") == "1":
        from tests.offline_guard import install as install_offline_guard

        install_offline_guard()
    executable = resolve_chromium_executable()
    if executable is None:
        return

    try:
        from playwright.sync_api import BrowserType
    except ModuleNotFoundError:
        return

    original_launch = BrowserType.launch
    if getattr(original_launch, "_dx_system_chromium_fallback", False):
        return

    def launch_with_system_chromium(self, *args, **kwargs):
        browser_name = getattr(self, "name", None)
        if browser_name is None:
            browser_name = getattr(getattr(self, "_impl_obj", None), "name", None)
        if browser_name == "chromium":
            kwargs.setdefault("executable_path", executable)
        return original_launch(self, *args, **kwargs)

    launch_with_system_chromium._dx_system_chromium_fallback = True
    BrowserType.launch = launch_with_system_chromium


def _ensure_launcher_package():
    """Restore launcher package if a test imported launcher/launcher.py as top-level 'launcher'."""
    mod = sys.modules.get("launcher")
    if mod is not None and not hasattr(mod, "__path__"):
        for name in list(sys.modules):
            if name == "launcher" or name.startswith("launcher."):
                del sys.modules[name]


def pytest_runtest_setup(item):
    nodeid = item.nodeid
    if (
        nodeid.startswith("tests/launcher/")
        or "test_boot_animation.py" in nodeid
        or "test_dx_server_body_parsing.py" in nodeid
        or "test_launcher_wiring.py" in nodeid
    ):
        _ensure_launcher_package()
