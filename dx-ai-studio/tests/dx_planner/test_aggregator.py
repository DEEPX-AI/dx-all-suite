"""dx_planner.core.aggregator 단위 테스트."""
from __future__ import annotations

import json
import os
import sys
import warnings
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

from dx_planner.core.aggregator import aggregate_benchmarks



def _make_environment(d: Path, npu_sku: str = "M1A", hostname: str = "test-host", npu_extra: dict | None = None):
    """환경 JSON 파일 생성."""
    npu = {"sku": npu_sku}
    if npu_extra:
        npu.update(npu_extra)
    env = {
        "npu": npu,
        "host": {"hostname": hostname, "cpu": "test-cpu", "ram_gb": 8, "os": "Linux"},
    }
    d.mkdir(parents=True, exist_ok=True)
    (d / "environment.json").write_text(json.dumps(env), encoding="utf-8")
    return env


def _make_model_results(d: Path, entries=None):
    if entries is None:
        entries = [
            {
                "model": "yolo11n-cls.dxnn",
                "task": "classification",
                "size": "n",
                "family": "latency",
                "fps": 100.0,
                "total_ms": 10.0,
                "use_ort": False,
            },
            {
                "model": "yolo11n-cls.dxnn",
                "task": "classification",
                "size": "n",
                "family": "throughput",
                "fps": 120.0,
                "total_ms": None,
                "use_ort": False,
            },
        ]
    (d / "model_results.json").write_text(json.dumps(entries), encoding="utf-8")


def _make_multi_stream(d: Path, entries=None):
    if entries is None:
        entries = []
    (d / "multi_stream_results.json").write_text(json.dumps(entries), encoding="utf-8")


def _make_npu_catalog(path: Path, items=None):
    if items is None:
        items = [
            {
                "id": "dx-m1a",
                "name": "DX-M1 V-NPU",
                "tops": 25,
                "tdp_w": 3,
                "price_usd": 99,
                "form_factor": "M.2",
                "dram_mb": 2048,
                "dram_type": "LPDDR4",
            }
        ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")


def _setup_platform(results_dir: Path, folder: str, run_name: str = "20250101_run"):
    """results_dir/<folder>/<run_name> 에 최소 벤치마크 데이터를 생성."""
    run_dir = results_dir / folder / run_name
    _make_environment(run_dir)
    _make_model_results(run_dir)
    _make_multi_stream(run_dir)
    return run_dir




class TestAggregatorMissingDir:
    """results_dir 가 없거나 비어 있으면 빈 플랫폼 목록을 반환해야 한다."""

    def test_missing_results_dir_returns_empty_platforms(self, tmp_path):
        result = aggregate_benchmarks(results_dir=tmp_path / "no-such-dir")
        assert result["platforms"] == []
        assert result["meta"]["platform_count"] == 0

    def test_empty_results_dir_returns_empty_platforms(self, tmp_path):
        results_dir = tmp_path / "results"
        results_dir.mkdir()
        result = aggregate_benchmarks(results_dir=results_dir)
        assert result["platforms"] == []


class TestAggregatorKnownPlatform:
    """알려진 플랫폼 폴더가 포함되어야 한다."""

    def test_known_platform_included(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)
        ids = [p["id"] for p in result["platforms"]]
        assert "rpi-m1" in ids

    def test_unknown_platform_folder_with_complete_run_is_included(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "UnknownBoard_X99")
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)
        ids = [p["id"] for p in result["platforms"]]
        assert "unknownboard-x99" in ids

    def test_hidden_and_temp_platform_folders_are_skipped(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, ".hidden_M1")
        _setup_platform(results_dir, "_scratch_M1")
        _setup_platform(results_dir, "tmp")
        _setup_platform(results_dir, "NewBoard_M1")
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)
        ids = [p["id"] for p in result["platforms"]]
        assert ids == ["newboard-m1"]

    def test_duplicate_normalized_platform_id_is_skipped_with_warning(self, tmp_path):
        """동적 스캔에서 정규화된 platform_id가 충돌하면 후행 폴더를 건너뛰어야 한다."""
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1", run_name="20250101_run")
        _setup_platform(results_dir, "rpi-m1", run_name="20260101_run")

        with pytest.warns(UserWarning, match="platform_id 충돌"):
            result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        ids = [p["id"] for p in result["platforms"]]
        assert ids == ["rpi-m1"]
        assert result["meta"]["platform_count"] == 1
        assert result["meta"]["benchmark_dates"] == {"rpi-m1": "2025-01-01"}


class TestAggregatorNpuCatalogMissing:
    """NPU 카탈로그가 없어도 크래시하지 않아야 한다."""

    def test_npu_catalog_missing_does_not_crash(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")

        result = aggregate_benchmarks(
            results_dir=results_dir,
            npu_catalog_path=tmp_path / "nonexistent.json",
        )
        assert isinstance(result["platforms"], list)
        assert len(result["platforms"]) == 1

    def test_npu_catalog_none_does_not_crash(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)
        assert len(result["platforms"]) == 1

    def test_missing_catalog_uses_unknown_dram_sentinel(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        assert result["platforms"][0]["npu"]["dram"] == "N/A"

    def test_catalog_entry_missing_dram_uses_unknown_sentinel(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path, items=[{
            "id": "dx-m1a",
            "name": "DX-M1 V-NPU",
            "tops": 25,
            "tdp_w": 3,
            "price_usd": None,
            "form_factor": "M.2",
        }])

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)

        npu = result["platforms"][0]["npu"]
        assert npu["dram"] == "N/A"
        assert npu["price_usd"] is None


class TestAggregatorOutputShape:
    """출력이 /api/benchmarks 기대 형태와 일치해야 한다."""

    def test_output_shape(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)

        # top-level keys
        assert "meta" in result
        assert "platforms" in result

        meta = result["meta"]
        assert "generated" in meta
        assert "benchmark_dates" in meta
        assert "platform_count" in meta
        assert "model_count" in meta

        platform = result["platforms"][0]
        assert "id" in platform
        assert "npu" in platform
        assert "host" in platform
        assert "benchmarks" in platform
        assert "multi_stream" in platform

        npu = platform["npu"]
        for key in ("model", "tops", "tdp_w", "price_usd", "unit_price_usd", "system_price_usd", "form_factor", "dram"):
            assert key in npu

        assert "topology" in platform
        topo = platform["topology"]
        for key in ("device_count", "hw_config", "h1_cards", "m1_modules", "board", "pcie"):
            assert key in topo

        host = platform["host"]
        for key in ("name", "cpu", "ram_gb", "os"):
            assert key in host

    def test_benchmark_entry_fields(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)
        bm = result["platforms"][0]["benchmarks"][0]
        for key in ("model", "task", "size", "ort", "latency_fps", "latency_ms",
                     "throughput_fps", "throughput_ms"):
            assert key in bm

    def test_out_path_writes_json(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)
        out = tmp_path / "output" / "benchmarks.json"

        result = aggregate_benchmarks(
            results_dir=results_dir,
            npu_catalog_path=npu_path,
            out_path=out,
        )
        assert out.exists()
        saved = json.loads(out.read_text(encoding="utf-8"))
        assert saved["meta"]["platform_count"] == result["meta"]["platform_count"]

    def test_out_path_does_not_rewrite_when_only_generated_changes(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)
        out = tmp_path / "output" / "benchmarks.json"

        first = aggregate_benchmarks(
            results_dir=results_dir,
            npu_catalog_path=npu_path,
            out_path=out,
        )
        first["meta"]["generated"] = "2026-01-01T00:00:00+00:00"
        out.write_text(json.dumps(first, indent=2, ensure_ascii=False), encoding="utf-8")

        aggregate_benchmarks(
            results_dir=results_dir,
            npu_catalog_path=npu_path,
            out_path=out,
        )

        saved = json.loads(out.read_text(encoding="utf-8"))
        assert saved["meta"]["generated"] == "2026-01-01T00:00:00+00:00"


class TestAggregatorCatalogWarnings:
    """제공된 npu_catalog_path 가 없으면 경고를 발행해야 한다."""

    def test_npu_catalog_missing_warns_when_path_provided(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")
        missing_path = tmp_path / "nonexistent_catalog.json"

        with pytest.warns(UserWarning, match="npu_catalog_path"):
            aggregate_benchmarks(
                results_dir=results_dir,
                npu_catalog_path=missing_path,
            )

    def test_npu_catalog_none_does_not_warn(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        user_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
        assert user_warnings == [], f"Unexpected warnings: {user_warnings}"


class TestAggregatorIncompleteRun:
    """불완전한 벤치마크 run 폴더는 건너뛰고 meta 에 skipped_incomplete_runs 를 기록해야 한다."""

    def test_aggregate_skips_incomplete_platform_run(self, tmp_path):
        """environment.json 만 있고 나머지 파일이 없는 run 은 건너뛰어야 한다."""
        results_dir = tmp_path / "results"
        run_dir = results_dir / "RPi_M1" / "20260608_run"
        run_dir.mkdir(parents=True, exist_ok=True)
        _make_environment(run_dir)
        # model_results.json, multi_stream_results.json 은 의도적으로 생성하지 않음

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)
        assert result["platforms"] == []
        assert result["meta"]["platform_count"] == 0
        assert result["meta"].get("skipped_incomplete_runs", 0) >= 1

    def test_aggregate_skips_run_missing_model_results(self, tmp_path):
        """model_results.json 만 없어도 건너뛰어야 한다."""
        results_dir = tmp_path / "results"
        run_dir = results_dir / "RPi_M1" / "20260608_run"
        run_dir.mkdir(parents=True, exist_ok=True)
        _make_environment(run_dir)
        _make_multi_stream(run_dir)
        # model_results.json 없음

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)
        assert result["platforms"] == []
        assert result["meta"]["skipped_incomplete_runs"] >= 1

    def test_aggregate_skips_run_missing_npu_sku(self, tmp_path):
        """environment.json 에 npu.sku 가 없으면 건너뛰어야 한다."""
        results_dir = tmp_path / "results"
        run_dir = results_dir / "RPi_M1" / "20260608_run"
        run_dir.mkdir(parents=True, exist_ok=True)
        env = {"host": {"hostname": "h", "cpu": "c", "ram_gb": 4, "os": "L"}}
        (run_dir / "environment.json").write_text(json.dumps(env), encoding="utf-8")
        _make_model_results(run_dir)
        _make_multi_stream(run_dir)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)
        assert result["platforms"] == []
        assert result["meta"]["skipped_incomplete_runs"] >= 1

    def test_complete_run_unaffected(self, tmp_path):
        """완전한 run 폴더는 기존처럼 정상 집계되어야 한다."""
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)
        assert len(result["platforms"]) == 1
        assert result["meta"]["skipped_incomplete_runs"] == 0


class TestAggregatorFallbackToOlderCompleteRun:
    """최신 run이 불완전하면 이전 완전한 run을 사용해야 한다."""

    def test_older_complete_run_used_when_newest_incomplete(self, tmp_path):
        """최신 run에 파일이 없어도, 이전 완전한 run이 있으면 플랫폼이 포함되어야 한다."""
        results_dir = tmp_path / "results"
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)

        # 완전한 이전 run
        _setup_platform(results_dir, "RPi_M1", run_name="20250101_run")

        # 불완전한 최신 run (environment.json만 존재)
        incomplete_run = results_dir / "RPi_M1" / "20250602_run"
        incomplete_run.mkdir(parents=True, exist_ok=True)
        _make_environment(incomplete_run)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)

        ids = [p["id"] for p in result["platforms"]]
        assert "rpi-m1" in ids, "이전 완전한 run이 있으므로 플랫폼이 포함되어야 한다"
        assert result["meta"]["skipped_incomplete_runs"] == 1

    def test_all_runs_incomplete_skips_platform(self, tmp_path):
        """모든 run이 불완전하면 플랫폼이 건너뛰어져야 한다."""
        results_dir = tmp_path / "results"
        for run_name in ["20250101_run", "20250602_run"]:
            run_dir = results_dir / "RPi_M1" / run_name
            run_dir.mkdir(parents=True, exist_ok=True)
            _make_environment(run_dir)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)
        assert result["platforms"] == []
        assert result["meta"]["skipped_incomplete_runs"] == 2

    def test_benchmark_date_uses_selected_run(self, tmp_path):
        """선택된 run의 날짜가 benchmark_dates에 반영되어야 한다."""
        results_dir = tmp_path / "results"
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)

        _setup_platform(results_dir, "RPi_M1", run_name="20250101_run")
        incomplete_run = results_dir / "RPi_M1" / "20250602_run"
        incomplete_run.mkdir(parents=True, exist_ok=True)
        _make_environment(incomplete_run)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)
        assert result["meta"]["benchmark_dates"]["rpi-m1"] == "2025-01-01"

    def test_dated_runs_are_preferred_over_non_date_aliases(self, tmp_path):
        """latest/current 같은 alias 폴더보다 YYYYMMDD run을 최신순으로 우선 선택해야 한다."""
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1", run_name="20250101_run")
        _setup_platform(results_dir, "RPi_M1", run_name="latest")

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        assert result["meta"]["benchmark_dates"]["rpi-m1"] == "2025-01-01"


class TestAggregatorSkipWarnings:
    """불완전하거나 malformed된 run을 건너뛸 때 경고가 발행되어야 한다."""

    def test_warns_on_missing_required_files(self, tmp_path):
        """필수 파일이 없는 run에 대해 UserWarning이 발행되어야 한다."""
        results_dir = tmp_path / "results"
        run_dir = results_dir / "RPi_M1" / "20260608_run"
        run_dir.mkdir(parents=True, exist_ok=True)
        _make_environment(run_dir)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        user_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
        warn_msgs = [str(w.message) for w in user_warnings]
        assert any("RPi_M1" in m and "20260608_run" in m for m in warn_msgs), \
            f"플랫폼/run 폴더를 포함한 경고가 필요합니다. 발행된 경고: {warn_msgs}"
        assert any("model_results.json" in m or "multi_stream_results.json" in m for m in warn_msgs), \
            f"누락된 파일명을 포함한 경고가 필요합니다. 발행된 경고: {warn_msgs}"

    def test_warns_on_missing_npu_sku(self, tmp_path):
        """npu.sku가 없는 run에 대해 UserWarning이 발행되어야 한다."""
        results_dir = tmp_path / "results"
        run_dir = results_dir / "RPi_M1" / "20260608_run"
        run_dir.mkdir(parents=True, exist_ok=True)
        env = {"host": {"hostname": "h", "cpu": "c", "ram_gb": 4, "os": "L"}}
        (run_dir / "environment.json").write_text(json.dumps(env), encoding="utf-8")
        _make_model_results(run_dir)
        _make_multi_stream(run_dir)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        user_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
        warn_msgs = [str(w.message) for w in user_warnings]
        assert any("npu.sku" in m for m in warn_msgs), \
            f"npu.sku 누락 경고가 필요합니다. 발행된 경고: {warn_msgs}"
        assert any("RPi_M1" in m for m in warn_msgs), \
            f"플랫폼 폴더를 포함한 경고가 필요합니다. 발행된 경고: {warn_msgs}"

    def test_malformed_environment_falls_back_to_older_complete_run(self, tmp_path):
        """최신 environment.json이 깨졌으면 크래시하지 않고 이전 complete run을 사용해야 한다."""
        results_dir = tmp_path / "results"
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)
        _setup_platform(results_dir, "RPi_M1", run_name="20250101_run")
        broken = results_dir / "RPi_M1" / "20250602_run"
        broken.mkdir(parents=True, exist_ok=True)
        (broken / "environment.json").write_text("{bad json", encoding="utf-8")
        _make_model_results(broken)
        _make_multi_stream(broken)

        with pytest.warns(UserWarning, match="environment.json"):
            result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)

        assert result["meta"]["benchmark_dates"]["rpi-m1"] == "2025-01-01"
        assert result["meta"]["skipped_incomplete_runs"] == 1

    def test_non_dict_environment_falls_back_to_older_complete_run(self, tmp_path):
        """environment.json이 dict가 아니면 크래시하지 않고 이전 complete run으로 fallback해야 한다."""
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1", run_name="20250101_run")
        broken = results_dir / "RPi_M1" / "20250602_run"
        broken.mkdir(parents=True, exist_ok=True)
        (broken / "environment.json").write_text(json.dumps([{"npu": {"sku": "M1A"}}]), encoding="utf-8")
        _make_model_results(broken)
        _make_multi_stream(broken)

        with pytest.warns(UserWarning, match="environment.json"):
            result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        assert [p["id"] for p in result["platforms"]] == ["rpi-m1"]
        assert result["meta"]["benchmark_dates"]["rpi-m1"] == "2025-01-01"
        assert result["meta"]["skipped_incomplete_runs"] == 1

    def test_null_npu_section_falls_back_to_older_complete_run(self, tmp_path):
        """environment.json의 npu가 null이면 크래시하지 않고 이전 complete run으로 fallback해야 한다."""
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1", run_name="20250101_run")
        broken = results_dir / "RPi_M1" / "20250602_run"
        broken.mkdir(parents=True, exist_ok=True)
        env = {"npu": None, "host": {"hostname": "h", "cpu": "c", "ram_gb": 4, "os": "L"}}
        (broken / "environment.json").write_text(json.dumps(env), encoding="utf-8")
        _make_model_results(broken)
        _make_multi_stream(broken)

        with pytest.warns(UserWarning, match="npu.sku"):
            result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        assert [p["id"] for p in result["platforms"]] == ["rpi-m1"]
        assert result["meta"]["benchmark_dates"]["rpi-m1"] == "2025-01-01"
        assert result["meta"]["skipped_incomplete_runs"] == 1

    def test_null_host_section_uses_empty_host_fields(self, tmp_path):
        """environment.json의 host가 null이어도 플랫폼 집계가 크래시하지 않아야 한다."""
        results_dir = tmp_path / "results"
        run_dir = results_dir / "RPi_M1" / "20250101_run"
        run_dir.mkdir(parents=True, exist_ok=True)
        env = {"npu": {"sku": "M1A"}, "host": None}
        (run_dir / "environment.json").write_text(json.dumps(env), encoding="utf-8")
        _make_model_results(run_dir)
        _make_multi_stream(run_dir)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        assert result["platforms"][0]["host"] == {
            "name": "",
            "cpu": "",
            "ram_gb": None,
            "os": "",
        }

    def test_malformed_model_results_skips_platform_without_crash(self, tmp_path):
        """model_results.json이 깨진 최신 run은 크래시 대신 이전 complete run으로 fallback해야 한다."""
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1", run_name="20250101_run")
        run_dir = results_dir / "RPi_M1" / "20250602_run"
        _make_environment(run_dir)
        (run_dir / "model_results.json").write_text("{bad json", encoding="utf-8")
        _make_multi_stream(run_dir)
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)

        with pytest.warns(UserWarning, match="model_results.json"):
            result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)

        assert [p["id"] for p in result["platforms"]] == ["rpi-m1"]
        assert result["meta"]["benchmark_dates"]["rpi-m1"] == "2025-01-01"
        assert result["meta"]["skipped_incomplete_runs"] == 1

    def test_malformed_multi_stream_falls_back_to_older_complete_run(self, tmp_path):
        """multi_stream_results.json이 깨진 최신 run도 이전 complete run으로 fallback해야 한다."""
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1", run_name="20250101_run")
        run_dir = results_dir / "RPi_M1" / "20250602_run"
        _make_environment(run_dir)
        _make_model_results(run_dir)
        (run_dir / "multi_stream_results.json").write_text("{bad json", encoding="utf-8")

        with pytest.warns(UserWarning, match="multi_stream_results.json"):
            result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        assert [p["id"] for p in result["platforms"]] == ["rpi-m1"]
        assert result["meta"]["benchmark_dates"]["rpi-m1"] == "2025-01-01"
        assert result["meta"]["skipped_incomplete_runs"] == 1

    def test_non_list_model_results_falls_back_to_older_complete_run(self, tmp_path):
        """model_results.json이 list가 아니면 크래시하지 않고 이전 complete run으로 fallback해야 한다."""
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1", run_name="20250101_run")
        run_dir = results_dir / "RPi_M1" / "20250602_run"
        _make_environment(run_dir)
        (run_dir / "model_results.json").write_text(json.dumps({"error": "timeout"}), encoding="utf-8")
        _make_multi_stream(run_dir)

        with pytest.warns(UserWarning, match="model_results.json"):
            result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        assert [p["id"] for p in result["platforms"]] == ["rpi-m1"]
        assert result["meta"]["benchmark_dates"]["rpi-m1"] == "2025-01-01"
        assert result["meta"]["skipped_incomplete_runs"] == 1

    def test_non_list_multi_stream_falls_back_to_older_complete_run(self, tmp_path):
        """multi_stream_results.json이 list가 아니면 크래시하지 않고 이전 complete run으로 fallback해야 한다."""
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1", run_name="20250101_run")
        run_dir = results_dir / "RPi_M1" / "20250602_run"
        _make_environment(run_dir)
        _make_model_results(run_dir)
        (run_dir / "multi_stream_results.json").write_text(json.dumps({"error": "timeout"}), encoding="utf-8")

        with pytest.warns(UserWarning, match="multi_stream_results.json"):
            result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        assert [p["id"] for p in result["platforms"]] == ["rpi-m1"]
        assert result["meta"]["benchmark_dates"]["rpi-m1"] == "2025-01-01"
        assert result["meta"]["skipped_incomplete_runs"] == 1

    def test_hidden_run_dirs_do_not_pollute_skip_count_or_warnings(self, tmp_path):
        """플랫폼 내부 hidden/temp 디렉터리는 run 후보가 아니므로 skip count와 warning에 포함되면 안 된다."""
        results_dir = tmp_path / "results"
        hidden = results_dir / "RPi_M1" / ".cache"
        hidden.mkdir(parents=True)
        incomplete = results_dir / "RPi_M1" / "20250602_run"
        incomplete.mkdir(parents=True)
        _make_environment(incomplete)

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        warn_msgs = [str(w.message) for w in caught if issubclass(w.category, UserWarning)]
        assert result["meta"]["skipped_incomplete_runs"] == 1
        assert not any(".cache" in message for message in warn_msgs)

    def test_invalid_run_date_uses_unknown_benchmark_date_sentinel(self, tmp_path):
        """run 폴더명이 YYYYMMDD로 시작하지 않으면 garbage 날짜 대신 null sentinel을 노출해야 한다."""
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1", run_name="latest")

        with pytest.warns(UserWarning, match="날짜 형식"):
            result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        assert result["meta"]["benchmark_dates"]["rpi-m1"] is None

    def test_impossible_run_date_uses_unknown_benchmark_date_sentinel(self, tmp_path):
        """YYYYMMDD 형태여도 달력상 불가능한 날짜는 null sentinel이어야 한다."""
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1", run_name="20261399_run")

        with pytest.warns(UserWarning, match="날짜 형식"):
            result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        assert result["meta"]["benchmark_dates"]["rpi-m1"] is None

    def test_undated_runs_fallback_by_mtime(self, tmp_path):
        """dated run이 없으면 undated alias는 알파벳 역순이 아니라 수정 시각 최신순으로 선택해야 한다."""
        results_dir = tmp_path / "results"
        stable = _setup_platform(results_dir, "RPi_M1", run_name="stable")
        latest = _setup_platform(results_dir, "RPi_M1", run_name="latest")
        _make_environment(stable, hostname="stable-host")
        _make_environment(latest, hostname="latest-host")
        os.utime(stable, (1000, 1000))
        os.utime(latest, (2000, 2000))

        with pytest.warns(UserWarning, match="날짜 형식"):
            result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=None)

        assert result["platforms"][0]["host"]["name"] == "latest-host"
        assert result["meta"]["benchmark_dates"]["rpi-m1"] is None

    def test_undated_run_stat_failure_does_not_crash_sort(self):
        """undated run mtime 조회가 실패해도 run 정렬은 전체 집계를 크래시시키면 안 된다."""
        from dx_planner.core.aggregator import _iter_run_dirs

        class FakeStat:
            def __init__(self, mtime):
                self.st_mtime = mtime

        class FakeRun:
            def __init__(self, name, mtime=None, fail_stat=False):
                self.name = name
                self._mtime = mtime
                self._fail_stat = fail_stat

            def is_dir(self):
                return True

            def stat(self):
                if self._fail_stat:
                    raise OSError("race")
                return FakeStat(self._mtime)

        class FakePlatformDir:
            def iterdir(self):
                return [
                    FakeRun("latest", fail_stat=True),
                    FakeRun("stable", mtime=1000),
                ]

        assert [run.name for run in _iter_run_dirs(FakePlatformDir())] == ["stable", "latest"]

    def test_platform_dir_iter_failure_returns_empty_with_warning(self):
        """results_dir.iterdir() 실패는 집계 전체 크래시가 아니라 경고+빈 목록이어야 한다."""
        from dx_planner.core.aggregator import _iter_platform_dirs

        class UnreadableResultsDir:
            def exists(self):
                return True

            def iterdir(self):
                raise PermissionError("denied")

            def __str__(self):
                return "/unreadable/results"

        with pytest.warns(UserWarning, match="결과 디렉터리 읽기 실패"):
            assert _iter_platform_dirs(UnreadableResultsDir()) == []

    def test_run_dir_iter_failure_returns_empty_with_warning(self):
        """platform_dir.iterdir() 실패는 집계 전체 크래시가 아니라 경고+빈 목록이어야 한다."""
        from dx_planner.core.aggregator import _iter_run_dirs

        class UnreadablePlatformDir:
            def iterdir(self):
                raise PermissionError("denied")

            def __str__(self):
                return "/unreadable/platform"

        with pytest.warns(UserWarning, match="플랫폼 디렉터리 읽기 실패"):
            assert _iter_run_dirs(UnreadablePlatformDir()) == []


class TestAggregatorMetaOutputShape:
    """meta에 skipped_incomplete_runs가 항상 포함되어야 한다."""

    def test_meta_includes_skipped_incomplete_runs_key(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)
        assert "skipped_incomplete_runs" in result["meta"]
        assert isinstance(result["meta"]["skipped_incomplete_runs"], int)

    def test_meta_skipped_count_zero_when_all_complete(self, tmp_path):
        results_dir = tmp_path / "results"
        _setup_platform(results_dir, "RPi_M1")
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)
        assert result["meta"]["skipped_incomplete_runs"] == 0

    def test_meta_skipped_count_empty_results(self, tmp_path):
        result = aggregate_benchmarks(results_dir=tmp_path / "no-dir")
        assert "skipped_incomplete_runs" in result["meta"]
        assert result["meta"]["skipped_incomplete_runs"] == 0


class TestAggregatorMultiStreamNoneStreamCount:
    """stream_count가 None/누락된 항목과 int가 섞여도 정렬이 크래시하지 않아야 한다."""

    def test_sort_with_none_stream_count(self, tmp_path):
        results_dir = tmp_path / "results"
        run_dir = results_dir / "RPi_M1" / "20250101_run"
        _make_environment(run_dir)
        _make_model_results(run_dir)
        _make_multi_stream(run_dir, entries=[
            {
                "model": "yolo11n-det.dxnn",
                "task": "detection",
                "size": "n",
                "avg_e2e_fps": 50.0,
                "avg_per_channel_fps": 12.5,
                "use_ort": False,
                # stream_count 의도적으로 누락
            },
            {
                "model": "yolo11n-det.dxnn",
                "task": "detection",
                "size": "n",
                "stream_count": 4,
                "avg_e2e_fps": 180.0,
                "avg_per_channel_fps": 45.0,
                "use_ort": False,
            },
        ])
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path)

        result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)
        ms = result["platforms"][0]["multi_stream"]
        assert len(ms) == 2
        # None/누락 stream_count가 int보다 앞에 정렬되어야 한다 (0으로 취급)
        assert ms[0]["stream_count"] is None or ms[0]["stream_count"] == 0
        assert ms[1]["stream_count"] == 4


class TestAggregatorUnicodeRoundtrip:
    """비-ASCII 데이터가 올바르게 읽히고 출력 JSON 으로 왕복해야 한다."""

    def test_unicode_catalog_and_host_roundtrip(self, tmp_path):
        results_dir = tmp_path / "results"
        run_dir = results_dir / "RPi_M1" / "20250101_run"
        run_dir.mkdir(parents=True, exist_ok=True)

        env = {
            "npu": {"sku": "M1A"},
            "host": {"hostname": "テスト호스트", "cpu": "ARM Córtex", "ram_gb": 4, "os": "리눅스"},
        }
        (run_dir / "environment.json").write_text(json.dumps(env, ensure_ascii=False), encoding="utf-8")
        _make_model_results(run_dir)
        _make_multi_stream(run_dir)

        catalog_items = [
            {
                "id": "dx-m1a",
                "name": "DX-M1 Quattro",
                "tops": 25,
                "tdp_w": 3,
                "price_usd": 99,
                "form_factor": "M.2 키ー",
                "dram_mb": 2048,
                "dram_type": "LPDDR4",
            }
        ]
        npu_path = tmp_path / "npu_unicode.json"
        _make_npu_catalog(npu_path, items=catalog_items)

        out = tmp_path / "output" / "unicode_result.json"
        result = aggregate_benchmarks(
            results_dir=results_dir,
            npu_catalog_path=npu_path,
            out_path=out,
        )

        assert out.exists()
        saved = json.loads(out.read_text(encoding="utf-8"))

        platform = saved["platforms"][0]
        assert platform["host"]["name"] == "テスト호스트"
        assert platform["host"]["cpu"] == "ARM Córtex"
        assert platform["npu"]["form_factor"] == "M.2 키ー"
        assert saved["meta"]["platform_count"] == result["meta"]["platform_count"]


class TestAggregatorTopology:
    """benchmark environment topology and system price aggregation."""

    def test_m1_dual_module_system_price(self, tmp_path):
        results_dir = tmp_path / "results"
        run_dir = results_dir / "DualM1_M1" / "20250101_run"
        _make_environment(
            run_dir,
            npu_sku="M1",
            hostname="dual-m1",
            npu_extra={
                "device_count": 2,
                "m1_modules": 2,
                "h1_cards": 0,
                "hw_config": "M1",
                "board": "M.2, Rev 1.0",
                "pcie": "Gen3 X4",
            },
        )
        _make_model_results(run_dir)
        _make_multi_stream(run_dir)
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path, items=[{
            "id": "dx-m1",
            "name": "DX-M1 V-NPU",
            "tops": 25,
            "tdp_w": 5,
            "price_usd": 99,
            "form_factor": "M.2",
            "dram_mb": 2048,
            "dram_type": "LPDDR4",
        }])

        platform = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)["platforms"][0]
        assert platform["topology"]["m1_modules"] == 2
        assert platform["npu"]["unit_price_usd"] == 99
        assert platform["npu"]["system_price_usd"] == 198

    def test_h1_card_price_uses_cards_not_device_count(self, tmp_path):
        results_dir = tmp_path / "results"
        run_dir = results_dir / "BIOSTAR_H1" / "20250101_run"
        _make_environment(
            run_dir,
            npu_sku="H1",
            hostname="BIOSTAR",
            npu_extra={
                "device_count": 4,
                "h1_cards": 1,
                "m1_modules": 0,
                "hw_config": "H1",
                "board": "H1, Rev 0.0",
                "pcie": "Gen3 X4",
            },
        )
        _make_model_results(run_dir)
        _make_multi_stream(run_dir)
        npu_path = tmp_path / "npu.json"
        _make_npu_catalog(npu_path, items=[{
            "id": "dx-h1",
            "name": "DX-H1 V-NPU",
            "tops": 50,
            "tdp_w": 40,
            "price_usd": 499,
            "form_factor": "PCIe Card",
            "dram_mb": 24576,
            "dram_type": "LPDDR5",
        }])

        platform = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)["platforms"][0]
        assert platform["topology"]["device_count"] == 4
        assert platform["topology"]["h1_cards"] == 1
        assert platform["npu"]["system_price_usd"] == 499
