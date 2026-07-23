"""AdapterResult 프로토콜 계약 테스트.

각 어댑터 반환값이 AdapterResult 필수 키와 타입을 준수하는지 검증한다.
"""

import json
import tempfile
from pathlib import Path

import pytest

from dx_modelzoo.metadata._protocol import AdapterResult, ADAPTER_RESULT_REQUIRED_KEYS
from dx_modelzoo.metadata.adapters import (
    benchmark_cache_adapter,
    local_runtime_adapter,
    local_modelzoo_repo_adapter,
    internal_modelzoo_adapter,
    _adapter_result,
)


_EXPECTED_TYPES = {
    "adapter": str,
    "profile": str,
    "fetched_at": str,
    "ok": bool,
    "models": dict,
    "errors": list,
    "warnings": list,
}




def _assert_adapter_result_shape(result: dict, *, label: str = ""):
    """result 가 AdapterResult 필수 키·타입을 모두 갖추었는지 검증."""
    prefix = f"[{label}] " if label else ""
    for key in ADAPTER_RESULT_REQUIRED_KEYS:
        assert key in result, f"{prefix}missing required key: {key}"
    for key, expected_type in _EXPECTED_TYPES.items():
        assert isinstance(result[key], expected_type), (
            f"{prefix}key '{key}' expected {expected_type.__name__}, "
            f"got {type(result[key]).__name__}"
        )




class TestAdapterResultDefinition:
    """AdapterResult TypedDict 가 올바르게 정의되었는지 확인."""

    def test_required_keys_constant_matches_spec(self):
        assert ADAPTER_RESULT_REQUIRED_KEYS == {
            "adapter", "profile", "fetched_at", "ok", "models", "errors", "warnings",
        }

    def test_typed_dict_has_all_required_annotations(self):
        annotations = AdapterResult.__annotations__
        for key in ADAPTER_RESULT_REQUIRED_KEYS:
            assert key in annotations, f"AdapterResult missing annotation for '{key}'"




class TestAdapterResultHelper:
    """adapters._adapter_result() 헬퍼가 계약을 준수하는지 확인."""

    def test_default_result_shape(self):
        r = _adapter_result("test_adapter")
        _assert_adapter_result_shape(r, label="_adapter_result default")

    def test_default_ok_is_true(self):
        r = _adapter_result("test_adapter")
        assert r["ok"] is True

    def test_default_models_empty(self):
        r = _adapter_result("test_adapter")
        assert r["models"] == {}

    def test_default_errors_empty(self):
        r = _adapter_result("test_adapter")
        assert r["errors"] == []

    def test_custom_profile(self):
        r = _adapter_result("x", profile="internal")
        assert r["profile"] == "internal"




class TestLocalRuntimeAdapterContract:
    """local_runtime_adapter 가 외부 파일 없이도 계약을 준수하는지 확인."""

    def test_missing_runtime_returns_ok_false_with_error(self, tmp_path):
        """dx-runtime 디렉토리가 없으면 ok=False, errors 비어있지 않아야 한다."""
        result = local_runtime_adapter(tmp_path)
        _assert_adapter_result_shape(result, label="local_runtime missing")
        assert result["ok"] is False
        assert len(result["errors"]) > 0

    def test_adapter_name_is_local_runtime(self, tmp_path):
        result = local_runtime_adapter(tmp_path)
        assert result["adapter"] == "local_runtime"




class TestBenchmarkCacheAdapterContract:
    """benchmark_cache_adapter 계약 검증."""

    def test_missing_cache_file_returns_ok_true_with_warning(self, tmp_path):
        """캐시 파일이 없으면 ok=True + warning (기존 동작 문서화)."""
        result = benchmark_cache_adapter(tmp_path / "nonexistent.json")
        _assert_adapter_result_shape(result, label="benchmark_cache missing")
        # 기존 동작: 파일 없으면 ok=True, warnings에 항목 추가
        assert result["ok"] is True
        assert any("not found" in w for w in result["warnings"])

    def test_invalid_json_returns_ok_false(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not-json", encoding="utf-8")
        result = benchmark_cache_adapter(bad_file)
        _assert_adapter_result_shape(result, label="benchmark_cache bad json")
        assert result["ok"] is False
        assert len(result["errors"]) > 0

    def test_valid_cache_returns_ok_true(self, tmp_path):
        cache_file = tmp_path / "bench.json"
        cache_file.write_text(json.dumps({
            "device": "test-device",
            "models": {
                "TestModel": {"fps": 30.0, "fps_per_watt": 5.0},
            },
        }), encoding="utf-8")
        result = benchmark_cache_adapter(cache_file)
        _assert_adapter_result_shape(result, label="benchmark_cache valid")
        assert result["ok"] is True
        assert len(result["models"]) > 0

    def test_adapter_name_is_benchmark_cache(self, tmp_path):
        result = benchmark_cache_adapter(tmp_path / "x.json")
        assert result["adapter"] == "benchmark_cache"




class TestLocalModelzooRepoAdapterContract:
    """local_modelzoo_repo_adapter 계약 검증."""

    def test_missing_models_dir_returns_ok_false(self, tmp_path):
        result = local_modelzoo_repo_adapter(tmp_path)
        _assert_adapter_result_shape(result, label="local_modelzoo_repo missing")
        assert result["ok"] is False
        assert len(result["errors"]) > 0

    def test_adapter_name(self, tmp_path):
        result = local_modelzoo_repo_adapter(tmp_path)
        assert result["adapter"] == "local_modelzoo_repo"




class TestInternalModelzooAdapterContract:
    """internal_modelzoo_adapter 계약 검증 (네트워크 모킹)."""

    def test_fetch_failure_returns_ok_false(self, tmp_path):
        def _fail(url):
            raise ConnectionError("mocked network error")
        result = internal_modelzoo_adapter(tmp_path, fetch_text=_fail)
        _assert_adapter_result_shape(result, label="internal_modelzoo fail")
        assert result["ok"] is False
        assert len(result["errors"]) > 0

    def test_empty_html_returns_ok_true_with_warning(self, tmp_path):
        result = internal_modelzoo_adapter(tmp_path, fetch_text=lambda url: "<html></html>")
        _assert_adapter_result_shape(result, label="internal_modelzoo empty")
        assert result["ok"] is True
        assert any("zero models" in w for w in result["warnings"])

    def test_adapter_name(self, tmp_path):
        result = internal_modelzoo_adapter(tmp_path, fetch_text=lambda url: "<html></html>")
        assert result["adapter"] == "internal_modelzoo"




class TestStubNetworkAdapterContract:
    """sync.py 의 _stub_network_adapter 결과가 계약을 준수하는지 확인."""

    def test_stub_result_shape(self):
        from dx_modelzoo.metadata.sync import _stub_network_adapter
        stub = _stub_network_adapter("public_modelzoo")
        result = stub()
        _assert_adapter_result_shape(result, label="public_modelzoo stub")




class TestSyncAggregationContract:
    """run_sync 가 어댑터 결과를 올바르게 집계하는지 확인."""

    def test_all_adapters_fail_produces_empty_catalog(self, tmp_path):
        from dx_modelzoo.metadata.sync import run_sync

        output = tmp_path / "catalog.json"
        result = run_sync(
            source_profile="local",
            suite_root=tmp_path,
            output_path=str(output),
        )
        assert "catalog" in result
        assert "report" in result
        catalog = result["catalog"]
        assert "models" in catalog
        report = result["report"]
        assert isinstance(report["adapter_errors"], list)
        assert isinstance(report["adapter_warnings"], list)

    def test_adapter_exception_result_keeps_required_shape(self, tmp_path, monkeypatch):
        from dx_modelzoo.metadata import sync as sync_module

        captured_results = []

        def _raise_adapter(_suite_root):
            raise RuntimeError("boom")

        def _ok_adapter(_suite_root):
            return _adapter_result("benchmark_cache")

        def _capture_merge(adapter_results, *, source_profile):
            captured_results.extend(adapter_results)
            return {
                "schema_version": "2.0",
                "source_profile": source_profile,
                "generated_at": "2026-01-01T00:00:00+00:00",
                "models": [],
            }

        monkeypatch.setattr(sync_module, "merge_adapter_results", _capture_merge)

        sync_module.run_sync(
            source_profile="local",
            suite_root=tmp_path,
            output_path=tmp_path / "catalog.json",
            adapter_overrides={
                "local_runtime": _raise_adapter,
                "benchmark_cache": _ok_adapter,
            },
        )

        failed_result = next(
            (r for r in captured_results if r["adapter"] == "local_runtime"),
            None,
        )
        assert failed_result is not None
        _assert_adapter_result_shape(failed_result, label="run_sync exception")
        assert failed_result["ok"] is False
        assert failed_result["errors"] == ["boom"]
