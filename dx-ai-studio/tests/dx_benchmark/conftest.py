"""tests/dx_benchmark conftest — dx_benchmark 모듈 테스트용 경로 설정."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BENCHMARK_ROOT = _REPO_ROOT / "dx_benchmark"

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_BENCHMARK_ROOT) not in sys.path:
    sys.path.insert(0, str(_BENCHMARK_ROOT))
