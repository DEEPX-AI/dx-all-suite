"""tests/dx_planner conftest — dx_planner 모듈 테스트용 경로 설정."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
