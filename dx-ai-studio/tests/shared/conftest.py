"""tests/shared conftest — shared 모듈 테스트용 경로 설정."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SHARED_DIR = _REPO_ROOT / "shared"

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))
