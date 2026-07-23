"""DX Agent Dev 서버 경로 상수 및 기본 설정.

dx_monitor/core/config.py 패턴을 따른다.
경로 계산: SCRIPT_DIR(dx_agent_dev/) → STUDIO_DIR(dx-ai-studio/) → SUITE_ROOT(dx-all-suite/)
"""
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent     # dx_agent_dev/
STUDIO_DIR = SCRIPT_DIR.parent                          # dx-ai-studio/

from shared.paths import SUITE_ROOT, var_dir

# 서버 디렉토리
STATIC_DIR = SCRIPT_DIR / "static"
TEMPLATES_DIR = SCRIPT_DIR / "templates"

DEFAULT_PORT = 8099
SERVER_NAME = "DX Agent Dev"

# 에이전트 세션 작업 디렉토리 (.gitignore 대상)
WORKSPACE_ROOT = var_dir("dx_agent_dev", "sessions")

# 입력/스트림 한계
PROMPT_MAX_LEN = 8000
KEEPALIVE_SEC = 15   # 일반망 keepalive ping 주기. 유휴(이벤트 없음) 시 ping으로 SSE 연결 유지.
# 단일 생성(generation)에 대한 wall-clock 상한(초). 멈춘/행(hang)한 실행이 단일 동시성
# 슬롯을 영구 점유하는 것을 방지한다(F-19). 환경변수로 조정 가능.
GENERATION_TIMEOUT_SEC = int(os.environ.get("DX_AGENT_GENERATION_TIMEOUT", "900"))


# Target workdirs the agent can run in — mirrors the original SCENARIO_WORKDIRS
# (.deepx/e2e/test.sh). The agent's cwd becomes one of these so it discovers that
# project's CLAUDE.md + .claude/skills.
TARGET_WORKDIRS = {
    "suite": SUITE_ROOT,
    "dx-runtime": SUITE_ROOT / "dx-runtime",
    "dx_app": SUITE_ROOT / "dx-runtime" / "dx_app",
    "dx_stream": SUITE_ROOT / "dx-runtime" / "dx_stream",
    "dx-compiler": SUITE_ROOT / "dx-compiler",
}


def resolve_target(name):
    """Map a target name to an absolute workdir under the suite root.

    Whitelist-based: unknown names, empty, or traversal attempts fall back to the
    suite root and can never escape it.
    """
    root = SUITE_ROOT.resolve()
    path = TARGET_WORKDIRS.get((name or "").strip())
    if path is None:
        return root
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return root
    return resolved


def harness_search_paths():
    """하니스 디렉토리 후보: env override → dx-all-suite 루트 → dx-agent-dev."""
    candidates = []
    env = os.environ.get("DX_HARNESS_ROOT")
    if env:
        candidates.append(Path(env))
    candidates.append(SUITE_ROOT)
    candidates.append(SUITE_ROOT / "dx-agent-dev")
    return candidates
