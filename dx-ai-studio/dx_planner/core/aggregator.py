"""벤치마크 결과 집계 모듈.

dx_benchmark/results 디렉터리를 스캔하여 플랫폼별 벤치마크를
단일 JSON 구조로 병합한다.
"""
from __future__ import annotations

import json
import re
import warnings
from datetime import datetime, timezone
from pathlib import Path

_REQUIRED_FILES = ["environment.json", "model_results.json", "multi_stream_results.json"]
_IGNORED_PLATFORM_NAMES = {"tmp", "temp", "__pycache__"}
_SUFFIX_RE = re.compile(r"-(cls|seg|pose|obb)$")
_NPU_NAME_RE = re.compile(r" (V-NPU|Quattro)$")
_RUN_DATE_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})")


def _without_meta_field(data: dict, field: str) -> dict:
    cloned = json.loads(json.dumps(data, ensure_ascii=False))
    if isinstance(cloned.get("meta"), dict):
        cloned["meta"].pop(field, None)
    return cloned


def _load_existing_if_only_generated_changed(out_path: Path, output: dict) -> dict | None:
    if not out_path.exists():
        return None
    try:
        existing = json.loads(out_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if _without_meta_field(existing, "generated") == _without_meta_field(output, "generated"):
        return existing
    return None


def _is_ignored_platform_dir(path: Path) -> bool:
    name = path.name
    return name.startswith((".", "_")) or name.lower() in _IGNORED_PLATFORM_NAMES


def _iter_platform_dirs(results_dir: Path) -> list[Path]:
    if not results_dir.exists():
        return []
    try:
        entries = list(results_dir.iterdir())
    except OSError as exc:
        warnings.warn(
            f"결과 디렉터리 읽기 실패: {results_dir} — {exc}",
            UserWarning,
            stacklevel=2,
        )
        return []
    return sorted(
        (path for path in entries if path.is_dir() and not _is_ignored_platform_dir(path)),
        key=lambda path: path.name,
    )


def _billing_units(npu_env: dict) -> int:
    """Catalog SKU count for this benchmark system (cards/modules), not DXRT device_count."""
    h1_cards = npu_env.get("h1_cards")
    if isinstance(h1_cards, int) and h1_cards > 0:
        return h1_cards
    m1_modules = npu_env.get("m1_modules")
    if isinstance(m1_modules, int) and m1_modules > 0:
        return m1_modules
    return 1


def _system_price_usd(unit_price: float | int | None, npu_env: dict) -> float | int | None:
    if unit_price is None:
        return None
    try:
        unit = float(unit_price)
    except (TypeError, ValueError):
        return None
    return round(unit * _billing_units(npu_env), 2)


def _topology_from_env(npu_env: dict) -> dict:
    return {
        "device_count": npu_env.get("device_count"),
        "hw_config": npu_env.get("hw_config"),
        "h1_cards": npu_env.get("h1_cards"),
        "m1_modules": npu_env.get("m1_modules"),
        "board": npu_env.get("board"),
        "pcie": npu_env.get("pcie"),
    }


def _format_dram(npu_info: dict) -> str:
    dram_mb = npu_info.get("dram_mb")
    if dram_mb is None:
        return "N/A"
    try:
        dram_gb = float(dram_mb) / 1024
    except (TypeError, ValueError):
        return "N/A"
    dram_value = f"{int(dram_gb)}GB" if dram_gb == int(dram_gb) else f"{dram_gb:.1f}GB"
    dram_type = npu_info.get("dram_type") or ""
    return f"{dram_value} {dram_type}".strip()


def _warn_skip(folder_name: str, run_name: str, reason: str) -> None:
    warnings.warn(
        f"불완전한 run 건너뜀: {folder_name}/{run_name} — {reason}",
        UserWarning,
        stacklevel=2,
    )


def _load_run_json(path: Path, folder_name: str, run_name: str):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        _warn_skip(folder_name, run_name, f"{path.name} JSON 파싱 오류: {exc}")
        return None


def _load_run_json_list(path: Path, folder_name: str, run_name: str):
    data = _load_run_json(path, folder_name, run_name)
    if data is None:
        return None
    if not isinstance(data, list):
        _warn_skip(folder_name, run_name, f"{path.name} 타입 오류: list 기대")
        return None
    return data


def _load_run_json_dict(path: Path, folder_name: str, run_name: str):
    data = _load_run_json(path, folder_name, run_name)
    if data is None:
        return None
    if not isinstance(data, dict):
        _warn_skip(folder_name, run_name, f"{path.name} 타입 오류: dict 기대")
        return None
    return data


def _parse_run_date(run_name: str) -> str | None:
    match = _RUN_DATE_RE.match(run_name)
    if not match:
        return None
    date_text = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return None
    return date_text


def _safe_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _iter_run_dirs(platform_dir: Path) -> list[Path]:
    try:
        entries = list(platform_dir.iterdir())
    except OSError as exc:
        warnings.warn(
            f"플랫폼 디렉터리 읽기 실패: {platform_dir} — {exc}",
            UserWarning,
            stacklevel=2,
        )
        return []
    run_dirs = [d for d in entries if d.is_dir() and not _is_ignored_platform_dir(d)]
    dated = sorted((d for d in run_dirs if _RUN_DATE_RE.match(d.name)), key=lambda d: d.name, reverse=True)
    undated = sorted(
        (d for d in run_dirs if not _RUN_DATE_RE.match(d.name)),
        key=lambda d: (_safe_mtime(d), d.name),
        reverse=True,
    )
    return dated + undated


def aggregate_benchmarks(
    results_dir: Path,
    npu_catalog_path: Path | None = None,
    out_path: Path | None = None,
) -> dict:
    """벤치마크 결과를 집계하여 dict 를 반환하고, out_path 가 있으면 JSON 파일도 생성."""
    results_dir = Path(results_dir)

    # NPU 카탈로그 로드
    npu_catalog: dict = {}
    if npu_catalog_path is not None:
        npu_catalog_path = Path(npu_catalog_path)
        if npu_catalog_path.exists():
            with open(npu_catalog_path, encoding="utf-8") as f:
                npu_catalog = {item["id"]: item for item in json.load(f)}
        else:
            warnings.warn(
                f"npu_catalog_path 가 제공되었지만 존재하지 않습니다: {npu_catalog_path}",
                UserWarning,
                stacklevel=2,
            )

    platforms = []
    benchmark_dates: dict = {}
    all_model_keys: set = set()
    seen_platform_ids: set = set()
    skipped_incomplete_runs = 0

    for platform_dir in _iter_platform_dirs(results_dir):
        folder_name = platform_dir.name

        run_folders = _iter_run_dirs(platform_dir)
        if not run_folders:
            continue

        selected_run = None
        selected_env = None
        selected_sku = None
        selected_model_results = None
        selected_multi_stream_results = None
        for candidate in run_folders:
            missing = [name for name in _REQUIRED_FILES if not (candidate / name).exists()]
            if missing:
                skipped_incomplete_runs += 1
                _warn_skip(folder_name, candidate.name, f"누락 파일: {', '.join(missing)}")
                continue

            env = _load_run_json_dict(candidate / "environment.json", folder_name, candidate.name)
            if env is None:
                skipped_incomplete_runs += 1
                continue

            npu_section = env.get("npu")
            sku = npu_section.get("sku") if isinstance(npu_section, dict) else None
            if not sku:
                skipped_incomplete_runs += 1
                _warn_skip(folder_name, candidate.name, "npu.sku 누락")
                continue

            model_results = _load_run_json_list(candidate / "model_results.json", folder_name, candidate.name)
            if model_results is None:
                skipped_incomplete_runs += 1
                continue

            multi_stream_results = _load_run_json_list(candidate / "multi_stream_results.json", folder_name, candidate.name)
            if multi_stream_results is None:
                skipped_incomplete_runs += 1
                continue

            selected_run = candidate
            selected_env = env
            selected_sku = sku
            selected_model_results = model_results
            selected_multi_stream_results = multi_stream_results
            break

        if selected_run is None:
            continue

        latest_run = selected_run
        env = selected_env
        sku = selected_sku
        model_results = selected_model_results or []
        multi_stream_results = selected_multi_stream_results or []
        platform_id = folder_name.lower().replace("_", "-")
        if platform_id in seen_platform_ids:
            warnings.warn(
                f"platform_id 충돌 건너뜀: {folder_name} → '{platform_id}' (이미 등록됨)",
                UserWarning,
                stacklevel=2,
            )
            continue
        seen_platform_ids.add(platform_id)
        npu_id = "dx-" + sku.lower()
        npu_info = npu_catalog.get(npu_id, {})
        npu_env = env.get("npu")
        if not isinstance(npu_env, dict):
            npu_env = {}

        raw_name = npu_info.get("name", npu_id)
        npu_display_name = _NPU_NAME_RE.sub("", raw_name)

        dram_str = _format_dram(npu_info)
        unit_price_usd = npu_info.get("price_usd")
        system_price_usd = _system_price_usd(unit_price_usd, npu_env)
        topology_out = _topology_from_env(npu_env)

        npu_out = {
            "model": npu_display_name,
            "tops": npu_info.get("tops"),
            "tdp_w": npu_info.get("tdp_w"),
            "unit_price_usd": unit_price_usd,
            "price_usd": unit_price_usd,
            "system_price_usd": system_price_usd,
            "form_factor": npu_info.get("form_factor"),
            "dram": dram_str,
        }

        host = env.get("host")
        if not isinstance(host, dict):
            host = {}
        host_out = {
            "name": host.get("hostname", ""),
            "cpu": host.get("cpu", ""),
            "ram_gb": host.get("ram_gb"),
            "os": host.get("os", ""),
        }

        benchmark_date = _parse_run_date(latest_run.name)
        if benchmark_date is None:
            warnings.warn(
                f"run 폴더 날짜 형식 불인식: {folder_name}/{latest_run.name}",
                UserWarning,
                stacklevel=2,
            )

        latency_map: dict = {}
        throughput_map: dict = {}

        for entry in model_results:
            fps = entry.get("fps")
            if fps is None:
                continue

            use_ort = bool(entry.get("use_ort"))
            model_base = _SUFFIX_RE.sub("", (entry["model"][:-5] if entry["model"].endswith(".dxnn") else entry["model"]))
            key = (model_base, entry["task"], entry["size"], use_ort)
            all_model_keys.add((model_base, entry["task"], entry["size"]))

            if entry.get("family") == "latency":
                total_ms = entry.get("total_ms")
                if total_ms is None:
                    continue
                latency_map[key] = {"fps": fps, "ms": total_ms}
            elif entry.get("family") == "throughput":
                throughput_map[key] = {"fps": fps, "ms": round(1000.0 / fps, 2)}

        benchmarks = []
        for key in sorted(set(latency_map) | set(throughput_map)):
            model_base, task, size, use_ort = key
            lat = latency_map.get(key, {})
            thr = throughput_map.get(key, {})
            benchmarks.append({
                "model": model_base,
                "task": task,
                "size": size,
                "ort": use_ort,
                "latency_fps": round(lat["fps"], 1) if "fps" in lat else None,
                "latency_ms": round(lat["ms"], 2) if "ms" in lat else None,
                "throughput_fps": round(thr["fps"], 1) if "fps" in thr else None,
                "throughput_ms": round(thr["ms"], 2) if "ms" in thr else None,
            })

        multi_stream = []
        for entry in multi_stream_results:
            total_fps = entry.get("avg_e2e_fps")
            per_channel_fps = entry.get("avg_per_channel_fps")
            if total_fps is None or per_channel_fps is None:
                continue

            model_base = _SUFFIX_RE.sub("", (entry["model"][:-5] if entry["model"].endswith(".dxnn") else entry["model"]))
            multi_stream.append({
                "model": model_base,
                "task": entry["task"],
                "size": entry["size"],
                "ort": bool(entry.get("use_ort")),
                "stream_count": entry.get("stream_count"),
                "total_fps": round(total_fps, 1),
                "per_channel_fps": round(per_channel_fps, 1),
                "fps_std": round(entry["fps_std"], 2) if entry.get("fps_std") is not None else None,
                "avg_cpu_pct": round(entry["avg_cpu_pct"], 1) if entry.get("avg_cpu_pct") is not None else None,
                "npu_throttled": bool(entry.get("npu_throttled")),
                "npu_total_avg_pct": round(entry["npu_total_avg_pct"], 1)
                if entry.get("npu_total_avg_pct") is not None
                else None,
                "max_rss_mib": round(entry["max_rss_mib"], 1) if entry.get("max_rss_mib") is not None else None,
            })
        multi_stream.sort(
            key=lambda m: (m["model"], m["task"], m["size"], m["ort"], m["stream_count"] or 0)
        )

        benchmark_dates[platform_id] = benchmark_date

        platforms.append({
            "id": platform_id,
            "npu": npu_out,
            "host": host_out,
            "topology": topology_out,
            "benchmarks": benchmarks,
            "multi_stream": multi_stream,
        })

    output = {
        "meta": {
            "generated": datetime.now(timezone.utc).isoformat(),
            "benchmark_dates": benchmark_dates,
            "platform_count": len(platforms),
            "model_count": len(all_model_keys),
            "skipped_incomplete_runs": skipped_incomplete_runs,
        },
        "platforms": platforms,
    }

    if out_path is not None:
        out_path = Path(out_path)
        existing = _load_existing_if_only_generated_changed(out_path, output)
        if existing is not None:
            return existing
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    return output
