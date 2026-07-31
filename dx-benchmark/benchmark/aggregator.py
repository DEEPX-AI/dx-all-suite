"""Aggregate multiple benchmark result directories into a comparison dataset."""

from __future__ import annotations

import json
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

from .npu_catalog import UNKNOWN_PRODUCT, classify_from_raw, format_badge, format_sku
from .result_layout import iter_result_dirs
from .runner_pipeline import _extract_pipeline_caps


def _load_json_object(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _load_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _extract_gstreamer_version(tools: dict) -> str | None:
    """Extract short GStreamer version from tools fingerprint."""
    raw = (tools.get("gst-launch-1.0") or {}).get("version")
    if not raw:
        return None
    # e.g. "gst-launch-1.0 version 1.20.3" -> "1.20.3"
    m = re.search(r"(\d+\.\d+\.\d+)", raw)
    return m.group(1) if m else raw.split()[-1]


def _parse_board_from_raw(raw: str) -> str | None:
    """Re-parse board value from dxrt-cli -s raw output.

    Used as a fallback when the stored ``board`` field is ``"unknown"`` because
    the field was collected before the board-parsing logic was added.
    Returns the first Board value found, or None.
    """
    for line in raw.splitlines():
        stripped = line.strip()
        if "Board" in stripped and ":" in stripped and "Chip" not in stripped:
            m = re.search(r":\s*(.+)", stripped)
            if m:
                return m.group(1).strip()
    return None


# NOTE: unlike result_layout._get_sku (fresh-fingerprint path, trusts stamped `sku`),
# this backfill path IGNORES a possibly-stale on-disk `sku` and re-derives from
# `modules`/`raw` so legacy data reclassifies under the current catalog.
def _resolve_modules(npu: dict) -> list[dict]:
    modules = npu.get("modules")
    if modules:
        return modules
    raw = npu.get("raw")
    if isinstance(raw, str) and raw:
        return classify_from_raw(raw)
    return []


def _build_environment_summary(env_id: str, run_id: str, fingerprint: dict) -> dict:
    host = fingerprint.get("host", {})
    npu = fingerprint.get("npu", {})
    software = fingerprint.get("software", {})
    modules = _resolve_modules(npu)

    board = npu.get("board")
    if (not board or board == "unknown") and npu.get("raw"):
        board = _parse_board_from_raw(npu["raw"]) or board

    return {
        "env_id": env_id,
        "dx_all_suite_version": fingerprint.get("dx_all_suite_version"),
        "benchmark_tool_version": fingerprint.get("benchmark_tool_version"),
        "hw_id": env_id,                     # legacy alias == env_id (folder)
        "latest_run_id": run_id,
        "product_name": fingerprint.get("product_name"),
        "hostname": host.get("hostname"),
        "os": host.get("os"),
        "kernel": host.get("kernel"),
        "arch": host.get("arch"),
        "cpu": host.get("cpu"),
        "cpu_count": host.get("cpu_count"),
        "ram_gb": host.get("ram_gb"),
        "npu_product": format_badge(modules),
        "npu_sku": format_sku(modules),
        "npu_modules": modules,
        "npu_device_count": npu.get("device_count"),
        "npu_clock_mhz": npu.get("clock_mhz"),
        "rt_driver": npu.get("driver"),
        "rt_version": npu.get("rt_version"),
        "pcie_driver": npu.get("pcie_driver"),
        "firmware": npu.get("firmware"),
        "memory": npu.get("memory"),
        "board": board,
        "pcie": npu.get("pcie"),
        "dx_stream_version": software.get("dx_stream"),
        "gstreamer_version": _extract_gstreamer_version(fingerprint.get("tools", {})),
        "benchmarked_models": fingerprint.get("benchmarked_models", []),
    }


def _normalize_run(run_id: str, env_id: str, result_dir: Path, fingerprint: dict) -> dict:
    npu = fingerprint.get("npu", {})
    software = fingerprint.get("software", {})
    return {
        "run_id": run_id,
        "env_id": env_id,
        "dx_all_suite_version": fingerprint.get("dx_all_suite_version"),
        "benchmark_tool_version": fingerprint.get("benchmark_tool_version"),
        # Relative "<env_id>/<run_id>" — never an absolute path (no username /
        # internal-repo leak in the published dataset.json; unused by the dashboard).
        "path": f"{env_id}/{run_id}",
        "timestamp": fingerprint.get("timestamp"),
        # Per-run SDK stack (this run's environment.json) — powers the Version Trend
        # tooltip so each point shows what actually changed at that suite version.
        "rt_version": npu.get("rt_version"),
        "rt_driver": npu.get("driver"),
        "pcie_driver": npu.get("pcie_driver"),
        "firmware": npu.get("firmware"),
        "dx_stream_version": software.get("dx_stream"),
        "protocol": fingerprint.get("protocol", {}),
        "benchmark_params": fingerprint.get("benchmark_params", {}),
    }


def _flatten_model_results(run_id: str, env_id: str, rows: list[dict]) -> list[dict]:
    flattened = []
    for row in rows:
        # Latency is a single-core sync burst measured via the profiler. dxtop's
        # ~1 Hz sampler undersamples such sub-second runs (util reads ~0%, and the
        # clock catches the idle DVFS downclock, e.g. 700 MHz, which then trips a
        # false throttle flag). So for latency we derive NPU occupancy from the
        # profiler timing (npu_task_ms / total_ms) and drop the sampled clock/throttle;
        # the sustained families (throughput/e2e/multi) keep the dxtop-sampled values.
        is_latency = row.get("family") == "latency"
        total_ms = row.get("total_ms")
        npu_task_ms = row.get("npu_task_ms")
        occupancy = None
        latency_ms_std = None
        if is_latency and total_ms:
            if npu_task_ms is not None:
                occupancy = round(min(100.0, npu_task_ms / total_ms * 100.0), 1)
            fps = row.get("fps")
            fps_std = row.get("fps_std")
            if fps and fps_std is not None:
                # delta method: latency = 1000/fps  ->  σ_ms = latency_ms * σ_fps / fps
                latency_ms_std = round(total_ms * fps_std / fps, 3)
        flattened.append({
            "run_id": run_id,
            "env_id": env_id,
            "task": row.get("task"),
            "size": row.get("size"),
            "model": row.get("model"),
            "use_ort": bool(row.get("use_ort")),
            "family": row.get("family"),
            "fps": row.get("fps"),
            "fps_std": row.get("fps_std"),
            "buffer_count": row.get("buffer_count"),
            "latency_ms": row.get("total_ms"),
            "latency_ms_std": latency_ms_std,
            "npu_occupancy_pct": occupancy,
            "cpu_pct": row.get("cpu_pct"),
            "npu_total_avg_pct": row.get("npu_total_avg_pct"),
            "npu_total_max_pct": row.get("npu_total_max_pct"),
            "npu_temp_min_c": row.get("npu_temp_min_c"),
            "npu_temp_max_c": row.get("npu_temp_max_c"),
            "npu_clock_mhz_min": None if is_latency else row.get("npu_clock_mhz_min"),
            "npu_clock_mhz_max": None if is_latency else row.get("npu_clock_mhz_max"),
            "npu_throttled": None if is_latency else row.get("npu_throttled"),
            "status": row.get("status"),
        })
    return flattened


_EXECUTION_ENDED_RE = re.compile(r"Execution ended after (\d+):(\d+):(\d+(?:\.\d+)?)")


def _parse_elapsed_seconds(log_text: str) -> float | None:
    match = _EXECUTION_ENDED_RE.search(log_text)
    if not match:
        return None
    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = float(match.group(3))
    return hours * 3600 + minutes * 60 + seconds


def _backfill_pipeline_fps_std(result_dir: Path, row: dict) -> float | None:
    if row.get("fps_std") is not None:
        return row.get("fps_std")

    model = row.get("model")
    frame_count = int(row.get("frame_count", 0) or 0)
    if not model or frame_count <= 0:
        return None

    raw_dir = result_dir / "raw"
    if not raw_dir.exists():
        return None

    ort_suffix = "on" if bool(row.get("use_ort")) else "off"
    fps_values: list[float] = []
    for log_path in sorted(raw_dir.glob(f"{model}.e2e.single.ort_{ort_suffix}.run*.log")):
        if log_path.name.endswith(".npu.log") or ".warmup." in log_path.name:
            continue
        elapsed = _parse_elapsed_seconds(log_path.read_text(errors="ignore"))
        if elapsed and elapsed > 0:
            fps_values.append(frame_count / elapsed)

    if len(fps_values) < 2:
        return None
    return round(statistics.stdev(fps_values), 2)


def _backfill_pipeline_caps(result_dir: Path, row: dict) -> dict | None:
    caps = dict(row.get("pipeline_caps") or {})
    if caps.get("decoder_src_format") is not None or caps.get("decoder_src_memory") is not None:
        return caps or None

    model = row.get("model")
    if not model:
        return caps or None

    raw_dir = result_dir / "raw"
    if not raw_dir.exists():
        return caps or None

    ort_suffix = "on" if bool(row.get("use_ort")) else "off"
    for log_path in sorted(raw_dir.glob(f"{model}.e2e.single.ort_{ort_suffix}.run*.log")):
        if log_path.name.endswith(".npu.log") or ".warmup." in log_path.name:
            continue
        parsed_caps = _extract_pipeline_caps(log_path.read_text(errors="ignore"))
        if not parsed_caps:
            continue
        for key, value in parsed_caps.items():
            if key not in caps or caps.get(key) is None:
                caps[key] = value
        if caps.get("decoder_src_format") is not None or caps.get("decoder_src_memory") is not None:
            break

    return caps or None


def _flatten_pipeline_results(run_id: str, env_id: str, result_dir: Path, rows: list[dict]) -> list[dict]:
    flattened = []
    for row in rows:
        entry = {
            "run_id": run_id,
            "env_id": env_id,
            "task": row.get("task"),
            "size": row.get("size"),
            "model": row.get("model"),
            "use_ort": bool(row.get("use_ort")),
            "avg_e2e_fps": row.get("avg_e2e_fps"),
            "decoder": row.get("decoder"),
            "status": row.get("status"),
            "video": row.get("video"),
            "avg_cpu_pct": row.get("avg_cpu_pct"),
            "npu_total_avg_pct": row.get("npu_total_avg_pct"),
            "npu_total_max_pct": row.get("npu_total_max_pct"),
            "max_rss_mib": row.get("max_rss_mib"),
            "avg_time_sec": row.get("avg_time_sec"),
            "frame_count": row.get("frame_count"),
            "runs": row.get("runs"),
            "requested_runs": row.get("requested_runs"),
            "fps_std": _backfill_pipeline_fps_std(result_dir, row),
            "npu_temp_min_c": row.get("npu_temp_min_c"),
            "npu_temp_max_c": row.get("npu_temp_max_c"),
            "npu_clock_mhz_min": row.get("npu_clock_mhz_min"),
            "npu_clock_mhz_max": row.get("npu_clock_mhz_max"),
        }
        caps = _backfill_pipeline_caps(result_dir, row)
        if caps:
            entry["pipeline_caps"] = caps
        flattened.append(entry)
    return flattened


_STATUS_RANK = {"ok": 0, "partial": 1, "timeout": 2, "error": 3, "fail": 4}


def _worst_status(rows: list[dict]) -> str:
    """Worst status across a model's multi-stream rows (ok < partial < timeout < error < fail).

    Capacity is taken from the best *ok* stream count, so a valid channel number
    can hide failed rows (e.g. an unparsable sc=1 baseline). Surfacing the worst
    status lets the dashboard flag such runs instead of showing a clean number.
    """
    worst, worst_rank = "ok", 0
    for row in rows:
        s = (row.get("status") or "ok")
        rank = _STATUS_RANK.get(s, _STATUS_RANK["error"])  # unknown → treat as error
        if rank > worst_rank:
            worst, worst_rank = s, rank
    return worst


def _status_detail(rows: list[dict]) -> tuple[str | None, list[int]]:
    """Explain a non-ok capacity status: (reason, sorted failed stream counts).

    Pairs with ``_worst_status`` so the dashboard/report can show WHY a capacity
    row is flagged (e.g. "error @ sc=[1]: <reason>") instead of an unexplained
    badge. Returns (None, []) when every row is ok.
    """
    failed = [r for r in rows if (r.get("status") or "ok") != "ok"]
    if not failed:
        return None, []
    failed_scs = sorted({int(r.get("stream_count", 0) or 0) for r in failed})
    worst = max(failed, key=lambda r: _STATUS_RANK.get(r.get("status") or "ok", _STATUS_RANK["error"]))
    return (worst.get("reason") or None), failed_scs


def _build_capacity_summary(run_id: str, env_id: str, rows: list[dict], fps_threshold: float) -> list[dict]:
    grouped: dict[tuple[str, bool], list[dict]] = {}
    for row in rows:
        key = (row.get("model"), bool(row.get("use_ort")))
        grouped.setdefault(key, []).append(row)

    summaries = []
    for (_, use_ort), group in grouped.items():
        stable = [
            row for row in group
            if row.get("status") == "ok"
            and int(row.get("runs", 0) or 0) == int(row.get("requested_runs", row.get("runs", 0)) or 0)
            and float(row.get("avg_per_channel_fps", 0.0) or 0.0) >= fps_threshold
        ]
        status_reason, failed_stream_counts = _status_detail(group)
        if stable:
            best = max(stable, key=lambda row: int(row.get("stream_count", 0) or 0))
            summaries.append({
                "run_id": run_id,
                "env_id": env_id,
                "task": best.get("task"),
                "size": best.get("size"),
                "model": best.get("model"),
                "use_ort": use_ort,
                "capacity_streams": best.get("stream_count"),
                "capacity_per_channel_fps": best.get("avg_per_channel_fps"),
                "fps_threshold": fps_threshold,
                "status": _worst_status(group),
                "status_reason": status_reason,
                "failed_stream_counts": failed_stream_counts,
            })
        elif group:
            # No stream count met the threshold (or all multi runs failed) —
            # emit a 0-capacity sentinel so the model stays visible instead of
            # silently vanishing from the capacity table.
            rep = group[0]
            summaries.append({
                "run_id": run_id,
                "env_id": env_id,
                "task": rep.get("task"),
                "size": rep.get("size"),
                "model": rep.get("model"),
                "use_ort": use_ort,
                "capacity_streams": 0,
                "capacity_per_channel_fps": None,
                "fps_threshold": fps_threshold,
                "status": _worst_status(group),
                "status_reason": status_reason,
                "failed_stream_counts": failed_stream_counts,
            })
    return summaries


def _build_ort_delta_summary(model_rows: list[dict], e2e_rows: list[dict], capacity_rows: list[dict]) -> list[dict]:
    deltas = []

    def _pair_by_key(rows: list[dict], metric_key: str, label: str) -> None:
        grouped: dict[tuple[str, str, str], dict[bool, dict]] = {}
        for row in rows:
            key = (row.get("env_id"), row.get("task"), row.get("size"))
            grouped.setdefault(key, {})[bool(row.get("use_ort"))] = row
        for (env_id, task, size), pair in grouped.items():
            if True not in pair or False not in pair:
                continue
            on = pair[True]
            off = pair[False]
            # Skip pairs where either side has no real metric (None/missing) —
            # coercing to 0.0 would fabricate a bogus (e.g. -100%) delta.
            if on.get(metric_key) is None or off.get(metric_key) is None:
                continue
            on_val = float(on[metric_key])
            off_val = float(off[metric_key])
            delta = on_val - off_val
            delta_pct = (delta / off_val * 100.0) if off_val else None
            deltas.append({
                "env_id": env_id,
                "task": task,
                "size": size,
                "metric": label,
                "ort_on": on_val,
                "ort_off": off_val,
                "delta": round(delta, 3),
                "delta_pct": round(delta_pct, 2) if delta_pct is not None else None,
            })

    _pair_by_key([row for row in model_rows if row.get("family") == "throughput"], "fps", "throughput_fps")
    _pair_by_key([row for row in model_rows if row.get("family") == "latency"], "latency_ms", "latency_ms")
    _pair_by_key(e2e_rows, "avg_e2e_fps", "e2e_fps")
    _pair_by_key(capacity_rows, "capacity_streams", "capacity_streams")
    return deltas


def _build_snapshot(hw_id: str, run_id: str, fingerprint: dict,
                    model_rows: list[dict], pipeline_rows: list[dict],
                    multi_rows: list[dict], fps_threshold: float,
                    result_dir: Path) -> dict:
    """Build a snapshot entry for the Version Trend tab."""
    npu = fingerprint.get("npu", {})
    software = fingerprint.get("software", {})
    return {
        "run_id": run_id,
        "dx_all_suite_version": fingerprint.get("dx_all_suite_version"),
        "hw_id": hw_id,
        "env_id": hw_id,
        "timestamp": fingerprint.get("timestamp"),
        "environment": _build_environment_summary(hw_id, run_id, fingerprint),
        "sw_versions": {
            "dx_stream": software.get("dx_stream"),
            "rt_version": npu.get("rt_version"),
            "rt_driver": npu.get("driver"),
            "firmware": npu.get("firmware"),
        },
        "results": {
            "model": _flatten_model_results(run_id, hw_id, model_rows),
            "e2e_single": _flatten_pipeline_results(run_id, hw_id, result_dir, pipeline_rows),
            "e2e_multi_capacity": _build_capacity_summary(run_id, hw_id, multi_rows, fps_threshold),
        },
    }


def aggregate_result_directories(results_root: Path) -> dict:
    result_dirs = iter_result_dirs(results_root)

    environments: dict[str, dict] = {}
    warnings: list[str] = []
    env_products: dict[str, set] = {}
    env_hostnames: dict[str, set] = {}
    runs: list[dict] = []
    model_summary: list[dict] = []
    e2e_single_summary: list[dict] = []
    e2e_multi_capacity_summary: list[dict] = []
    snapshots: list[dict] = []

    for result_dir in result_dirs:
        run_id = result_dir.name
        env_id = result_dir.parent.name          # folder directly under results/
        fingerprint = _load_json_object(result_dir / "environment.json")
        modules = _resolve_modules(fingerprint.get("npu", {}))
        sku = format_sku(modules)
        if sku != UNKNOWN_PRODUCT:
            env_products.setdefault(env_id, set()).add(sku)
        host = fingerprint.get("host", {}).get("hostname")
        if host:
            env_hostnames.setdefault(env_id, set()).add(host)
        # Use env_id (results folder name) as the environment key across all tabs.
        # SW version changes (driver/firmware) are tracked via history/snapshots.
        environments[env_id] = _build_environment_summary(env_id, run_id, fingerprint)
        runs.append(_normalize_run(run_id, env_id, result_dir, fingerprint))

        model_rows = _load_json_list(result_dir / "model_results.json")
        pipeline_rows = _load_json_list(result_dir / "pipeline_results.json")
        multi_rows = _load_json_list(result_dir / "multi_stream_results.json")
        fps_threshold = float(fingerprint.get("protocol", {}).get("fps_threshold", fingerprint.get("benchmark_params", {}).get("fps_threshold", 30.0)) or 30.0)

        model_summary.extend(_flatten_model_results(run_id, env_id, model_rows))
        e2e_single_summary.extend(_flatten_pipeline_results(run_id, env_id, result_dir, pipeline_rows))
        e2e_multi_capacity_summary.extend(_build_capacity_summary(run_id, env_id, multi_rows, fps_threshold))

        snapshots.append(_build_snapshot(
            env_id, run_id, fingerprint,
            model_rows, pipeline_rows, multi_rows, fps_threshold, result_dir,
        ))

    for env_id, products in env_products.items():
        if len(products) > 1:
            warnings.append(
                f"Folder '{env_id}' contains runs classified as different NPU "
                f"products: {sorted(products)}. Check the folder name / hardware.")

    for env_id, hosts in env_hostnames.items():
        if len(hosts) > 1:
            warnings.append(
                f"Folder '{env_id}' contains runs from different hostnames: "
                f"{sorted(hosts)}. Check the folder name / hardware.")

    # hw_id == env_id here; kept for the JS frontend
    snapshots.sort(key=lambda s: (s.get("hw_id", ""), s.get("run_id", "")))

    # Keep only the latest run per (env_id, model, use_ort) for display summaries.
    # Since result_dirs are sorted chronologically, later entries overwrite earlier ones.
    def _dedup_latest(rows: list[dict], key_fields: list[str]) -> list[dict]:
        seen: dict[tuple, dict] = {}
        for row in rows:
            k = tuple(row.get(f) for f in key_fields)
            seen[k] = row  # last write wins (latest run)
        return list(seen.values())

    model_latest = _dedup_latest(model_summary, ["env_id", "model", "use_ort", "family"])
    e2e_latest = _dedup_latest(e2e_single_summary, ["env_id", "model", "use_ort"])
    cap_latest = _dedup_latest(e2e_multi_capacity_summary, ["env_id", "model", "use_ort"])

    ort_delta = _build_ort_delta_summary(model_latest, e2e_latest, cap_latest)
    return {
        "meta": {
            "dataset_version": "v2",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "run_count": len(runs),
            "environment_count": len(environments),
            "warnings": warnings,
        },
        "environments": sorted(environments.values(), key=lambda item: item["env_id"]),
        "runs": sorted(runs, key=lambda item: item["run_id"]),
        "summaries": {
            "model": model_latest,
            "e2e_single": e2e_latest,
            "e2e_multi_capacity": cap_latest,
            "ort_delta": ort_delta,
        },
        "history": {
            "model": model_summary,
            "e2e_single": e2e_single_summary,
            "e2e_multi_capacity": e2e_multi_capacity_summary,
        },
        "snapshots": snapshots,
    }


def save_dataset_json(dataset: dict, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
    return output_path