"""메타데이터 동기화 오케스트레이터."""

import json
from datetime import datetime, timezone
from pathlib import Path

from dx_modelzoo.metadata.adapters import (
    benchmark_cache_adapter,
    internal_modelzoo_adapter,
    public_modelzoo_adapter,
    local_modelzoo_repo_adapter,
    local_runtime_adapter,
)
from dx_modelzoo.metadata._protocol import AdapterResult
from dx_modelzoo.metadata.cache import atomic_write_json, load_catalog_cache
from dx_modelzoo.metadata.merge import merge_adapter_results


_PROFILE_ADAPTERS = {
    "local": ["local_runtime", "local_modelzoo_repo", "benchmark_cache"],
    "internal": ["local_runtime", "local_modelzoo_repo", "internal_modelzoo", "benchmark_cache"],
    "public": ["local_runtime", "local_modelzoo_repo", "public_modelzoo", "benchmark_cache"],
}

# 네트워크 어댑터 (offline 모드에서 제외)
_NETWORK_ADAPTERS = {"internal_modelzoo", "public_modelzoo"}


def _empty_adapter_result(adapter, profile="default") -> AdapterResult:
    return {
        "adapter": adapter,
        "profile": profile,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "ok": True,
        "models": {},
        "errors": [],
        "warnings": [],
    }


def adapter_names_for_profile(profile, offline=False):
    """프로필에 해당하는 어댑터 이름 목록 반환."""
    adapters = list(_PROFILE_ADAPTERS.get(profile, _PROFILE_ADAPTERS["local"]))
    if offline:
        adapters = [a for a in adapters if a not in _NETWORK_ADAPTERS]
    return adapters


def resolve_source_profile(cli_source=None, env=None, config_path=None):
    """소스 프로필 결정: CLI → env → config → 'local'."""
    if cli_source:
        return cli_source
    if env and env.get("DX_MODELZOO_METADATA_SOURCE"):
        return env["DX_MODELZOO_METADATA_SOURCE"]
    if config_path:
        config_path = Path(config_path)
        if config_path.exists():
            try:
                cfg = json.loads(config_path.read_text(encoding="utf-8"))
                if cfg.get("source_profile"):
                    return cfg["source_profile"]
            except (json.JSONDecodeError, OSError):
                pass
    return "local"


def _get_adapter_func(name):
    """어댑터 이름 → 실행 함수 매핑."""
    mapping = {
        "local_runtime": local_runtime_adapter,
        "local_modelzoo_repo": local_modelzoo_repo_adapter,
        "benchmark_cache": benchmark_cache_adapter,
        "internal_modelzoo": internal_modelzoo_adapter,
        "public_modelzoo": public_modelzoo_adapter,
    }
    return mapping.get(name)


def _stub_network_adapter(adapter_name):
    """네트워크 어댑터 스텁 – 빈 결과 반환."""
    def _adapter(*args, **kwargs):
        result = _empty_adapter_result(adapter_name, profile="public")
        result["warnings"].append(f"{adapter_name}: stub adapter, no data fetched")
        return result
    return _adapter


def run_sync(
    source_profile,
    suite_root,
    output_path,
    cache_path=None,
    report_path=None,
    offline=False,
    adapter_overrides=None,
    benchmark_cache_path=None,
    adapter_kwargs=None,
):
    """동기화 실행: 어댑터 실행 → 병합 → 출력/캐시 작성.

    Returns:
        {"catalog": {...}, "report": {...}}
    """
    suite_root = Path(suite_root)
    adapter_overrides = adapter_overrides or {}
    adapter_kwargs = adapter_kwargs or {}

    adapter_names = adapter_names_for_profile(source_profile, offline=offline)

    adapter_results = []
    adapter_errors = []
    adapter_warnings = []

    for name in adapter_names:
        func = adapter_overrides.get(name, _get_adapter_func(name))
        if func is None:
            adapter_warnings.append(f"unknown adapter: {name}")
            continue
        try:
            if name == "benchmark_cache":
                bench_path = benchmark_cache_path or (
                    suite_root / "dx-ai-studio" / "dx_modelzoo" / "data" / "benchmark_cache.json"
                )
                r = func(bench_path)
            elif name in ("local_runtime", "local_modelzoo_repo"):
                r = func(suite_root)
            else:
                r = func(suite_root, **adapter_kwargs.get(name, {}))
        except Exception as exc:
            r = _empty_adapter_result(name, profile=source_profile)
            r["ok"] = False
            r["errors"].append(str(exc))

        adapter_results.append(r)
        if not r.get("ok"):
            adapter_errors.extend(
                [f"{name}: {e}" for e in r.get("errors", [])]
            )
        adapter_warnings.extend(
            [f"{name}: {w}" for w in r.get("warnings", [])]
        )

    ok_results = [r for r in adapter_results if r.get("ok")]
    if ok_results:
        catalog = merge_adapter_results(adapter_results, source_profile=source_profile)
        # An ok-but-empty merge (e.g. run from the wrong location so the sibling
        # dx-runtime/dx-modelzoo repos are absent, leaving only an empty
        # benchmark_cache) must NOT count as a valid catalog — otherwise it
        # silently clobbers a good one with 0 models. Treat as failure.
        if not catalog.get("models"):
            catalog = None
    else:
        catalog = None

    # 캐시 fallback: fresh 카탈로그가 없을 때만 이전 캐시 사용
    if catalog is None and cache_path:
        prior = load_catalog_cache(cache_path)
        if prior is not None and prior.get("models"):
            for model in prior.get("models", []):
                if isinstance(model.get("performance"), dict):
                    model["performance"]["source_status"] = "stale_cache"
            catalog = prior

    # Last resort: keep whatever populated catalog is already on disk rather than
    # overwriting it with an empty one.
    if catalog is None or not catalog.get("models"):
        existing = load_catalog_cache(Path(output_path))
        if existing is not None and existing.get("models"):
            return {
                "catalog": existing,
                "report": {
                    "source_profile": source_profile,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "model_count": len(existing.get("models", [])),
                    "adapter_errors": adapter_errors,
                    "adapter_warnings": adapter_warnings,
                    "skipped_write": "all adapters empty — kept existing catalog",
                    "coverage": _build_coverage_report(existing),
                },
            }

    if catalog is None:
        catalog = {
            "schema_version": "2.0",
            "source_profile": source_profile,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "models": [],
        }

    output_path = Path(output_path)
    atomic_write_json(output_path, catalog)

    if cache_path:
        atomic_write_json(cache_path, catalog)

    report = {
        "source_profile": source_profile,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_count": len(catalog.get("models", [])),
        "adapter_errors": adapter_errors,
        "adapter_warnings": adapter_warnings,
        "coverage": _build_coverage_report(catalog),
    }

    if report_path:
        atomic_write_json(Path(report_path), report)

    return {"catalog": catalog, "report": report}


def _build_coverage_report(catalog):
    """카탈로그 모델의 missing/suspect 필드를 집계하여 커버리지 리포트 생성."""
    missing_by_field = {}
    suspect_by_field = {}

    for model in catalog.get("models", []):
        for field in model.get("missing", []):
            missing_by_field[field] = missing_by_field.get(field, 0) + 1

        # suspect 필드 집계: evaluation 하위의 source_status == "suspect"
        evaluation = model.get("evaluation", {})
        for bench_name, bench_data in evaluation.items():
            if isinstance(bench_data, dict) and bench_data.get("source_status") == "suspect":
                key = f"evaluation.{bench_name}.accuracy"
                suspect_by_field[key] = suspect_by_field.get(key, 0) + 1

    return {
        "missing_by_field": missing_by_field,
        "suspect_by_field": suspect_by_field,
    }
