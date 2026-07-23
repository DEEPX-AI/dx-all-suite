"""__main__.py CLI 인자 파싱 테스트"""
import warnings
from pathlib import Path

import pytest

BENCHMARK_DIR = Path(__file__).resolve().parents[4] / "dx-runtime" / "dx_stream" / "dx_stream" / "apps" / "benchmark"
# Guard on the actual source file, not the directory: a stale __pycache__ leftover
# can keep the dir present after staging dx_stream removed the benchmark app.
_BENCHMARK_APP = BENCHMARK_DIR / "__main__.py"
pytestmark = [
    pytest.mark.requires_dx_runtime,
    pytest.mark.skipif(
        not _BENCHMARK_APP.is_file(),
        reason="dx-runtime benchmark app is not available",
    ),
]

# benchmark import는 각 테스트에서 지연 수행하므로 모듈 레벨 guard가 필요 없다.
class TestGetStages:
    def test_stage_model(self):
        from benchmark.__main__ import _get_stages
        import argparse
        args = argparse.Namespace(stage="model", family=None)
        assert _get_stages(args) == ["model"]

    def test_stage_pipeline(self):
        from benchmark.__main__ import _get_stages
        import argparse
        args = argparse.Namespace(stage="pipeline", family=None)
        assert _get_stages(args) == ["pipeline"]

    def test_stage_multistream(self):
        from benchmark.__main__ import _get_stages
        import argparse
        args = argparse.Namespace(stage="multistream", family=None)
        assert _get_stages(args) == ["multistream"]

    def test_no_stage_default(self):
        from benchmark.__main__ import _get_stages
        import argparse
        args = argparse.Namespace(stage=None, family=None)
        assert _get_stages(args) == ["model", "pipeline", "multistream"]

    def test_deprecated_family_e2e(self):
        from benchmark.__main__ import _get_stages
        import argparse
        args = argparse.Namespace(stage=None, family="e2e")
        with pytest.warns(DeprecationWarning):
            result = _get_stages(args)
        assert result == ["pipeline"]

    def test_deprecated_family_model(self):
        from benchmark.__main__ import _get_stages
        import argparse
        args = argparse.Namespace(stage=None, family="model")
        with pytest.warns(DeprecationWarning):
            result = _get_stages(args)
        assert result == ["model"]

    def test_deprecated_family_multi(self):
        from benchmark.__main__ import _get_stages
        import argparse
        args = argparse.Namespace(stage=None, family="multi")
        with pytest.warns(DeprecationWarning):
            result = _get_stages(args)
        assert result == ["multistream"]

    def test_deprecated_family_all(self):
        from benchmark.__main__ import _get_stages
        import argparse
        args = argparse.Namespace(stage=None, family="all")
        assert _get_stages(args) == ["model", "pipeline", "multistream"]
