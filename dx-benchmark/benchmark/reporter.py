"""Report generator – produces Markdown and CSV from benchmark results.

Collects results from all benchmark families and generates:
  1. CSV files for programmatic analysis
  2. A comprehensive Markdown report with comparison tables

Report table structure (per section):
  1. ORT=ON results table
  2. ORT=OFF results table
  3. ORT ON vs OFF comparison table
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import TASK_MODEL_META, MULTI_STREAM_SUPPORTED_TASKS
from .runner_pipeline import is_capacity_pass


def _get_fps_threshold(fingerprint: dict) -> float:
    """Resolve the run's per-channel FPS threshold (protocol → params → 30.0)."""
    protocol = fingerprint.get("protocol") or {}
    params = fingerprint.get("benchmark_params") or {}
    val = protocol.get("fps_threshold", params.get("fps_threshold", 30.0))
    try:
        return float(val)
    except (TypeError, ValueError):
        return 30.0


def _status_cell(r: dict) -> str:
    """Status cell text; appends the reason for any non-ok row so degraded
    results are never shown as a bare word with no cause."""
    status = r.get("status", "")
    reason = r.get("reason", "")
    if status and status != "ok" and reason:
        return f"{status} — {reason}"
    return status


def save_results_csv(results: list[dict], path: Path, fieldnames: list[str] | None = None) -> None:
    """Write results to a CSV file."""
    if not results:
        return
    if fieldnames is None:
        # Collect the superset of all keys (preserving insertion order from
        # the first record, then appending any extra keys from later records).
        seen: set[str] = set()
        fieldnames = []
        for r in results:
            for k in r.keys():
                if k not in seen:
                    seen.add(k)
                    fieldnames.append(k)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)


def save_results_json(results: list[dict], path: Path) -> None:
    """Write results to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)


# ── Ordering helpers ──────────────────────────────────────────────────────

_SIZE_ORDER = {"n": 0, "s": 1, "m": 2, "l": 3, "x": 4}

# Canonical task display order
_TASK_DISPLAY_ORDER = {
    "object_detection": 0,
    "pose_estimation": 1,
    "segmentation": 2,
    "oriented_bbox": 3,
    "classification": 4,
}

# Friendly names for display
_TASK_DISPLAY_NAMES = {
    "object_detection": "Object Detection",
    "pose_estimation": "Pose Estimation",
    "segmentation": "Segmentation",
    "oriented_bbox": "Oriented BBox (OBB)",
    "classification": "Classification",
}

# Video group friendly names
_GROUP_DISPLAY_NAMES = {
    "cls": "Classification",
    "od_pose_seg": "Object Detection / Pose / Segmentation",
    "obb": "Oriented BBox (OBB)",
}

# Group display order
_GROUP_ORDER = {"od_pose_seg": 0, "obb": 1, "cls": 2}


def _sort_by_size(results: list[dict]) -> list[dict]:
    return sorted(results, key=lambda r: _SIZE_ORDER.get(r.get("size", ""), 99))


def _size_char_from_name(name: str) -> str:
    """Best-effort size char from a model file name (tolerant fallback only).

    Handles both the legacy glued form ("yolo26n", "yolo26n-cls") and the newer
    hyphenated form ("yolo26-n_640x640", "yolo26-l-pose_640x640"). This is a
    LAST RESORT — callers should prefer the stamped ``size`` field, which is
    version-proof; naming rules keep changing and must not drive ordering.
    """
    m = re.search(r"yolo26-?([nslmx])(?:[-_.]|$)", name or "")
    return m.group(1).lower() if m else ""


def _sort_models_by_size(models: list[str], size_of: dict[str, str] | None = None) -> list[str]:
    """Sort model names by size (n<s<m<l<x). Prefers the stamped size from
    *size_of* (model name → size char); falls back to tolerant name parsing."""
    def _size_key(name: str) -> int:
        size = (size_of or {}).get(name) or _size_char_from_name(name)
        return _SIZE_ORDER.get(size, 99)
    return sorted(models, key=_size_key)


def _is_usable_result(result: dict) -> bool:
    return result.get("status", "ok") in {"ok", "partial"}


def _format_runs(result: dict) -> str:
    completed = int(result.get("runs", 0) or 0)
    requested = int(result.get("requested_runs", completed) or completed)
    if requested > 0 and requested != completed:
        return f"{completed}/{requested}"
    return str(completed)


def _group_by_task(results: list[dict]) -> dict[str, list[dict]]:
    """Group results by task name, in canonical order."""
    groups: dict[str, list[dict]] = {}
    for r in results:
        task = r.get("task", "unknown")
        groups.setdefault(task, []).append(r)
    return dict(sorted(groups.items(), key=lambda kv: _TASK_DISPLAY_ORDER.get(kv[0], 99)))


# ── Main report generator ────────────────────────────────────────────────

def generate_markdown_report(
    fingerprint: dict,
    model_results: list[dict],
    pipeline_results: list[dict],
    multi_stream_results: list[dict],
    output_path: Path,
    video_infos: dict[str, dict] | None = None,
) -> Path:
    """Generate a comprehensive Markdown benchmark report."""
    lines: list[str] = []

    lines.append("# YOLO26 Benchmark Report")
    lines.append("")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S (Local)")
    lines.append(f"**Generated:** {ts}")
    lines.append("")

    fps_threshold = _get_fps_threshold(fingerprint)

    # ── Test Timing ───────────────────────────────────────────────────
    _add_timing_section(lines, fingerprint)

    # ── Executive Summary ─────────────────────────────────────────────
    _add_executive_summary(lines, model_results, pipeline_results, multi_stream_results, fps_threshold)

    # ── Environment ───────────────────────────────────────────────────
    _add_environment_section(lines, fingerprint)

    # ── Benchmark Parameters ──────────────────────────────────────────
    _add_benchmark_params_section(lines, fingerprint)

    # ── Measurement Protocol ──────────────────────────────────────────
    _add_protocol_section(lines, fingerprint)

    # ── Benchmarked Models ────────────────────────────────────────────
    _add_model_info_section(lines, fingerprint, model_results)

    # ── Input Videos ──────────────────────────────────────────────────
    # Only meaningful when a video-based family (e2e / multi) actually ran.
    if pipeline_results or multi_stream_results:
        _add_video_section(lines, video_infos)

    # ── Model-level results ───────────────────────────────────────────
    if model_results:
        lines.append("## Model-Level Benchmarks")
        lines.append("")

        throughput = [r for r in model_results if r.get("family") == "throughput"]
        latency = [r for r in model_results if r.get("family") == "latency"]

        if throughput:
            _add_model_throughput_section(lines, throughput)
        if latency:
            _add_model_latency_section(lines, latency)

    # ── E2E single-stream results ─────────────────────────────────────
    if pipeline_results:
        _add_pipeline_section(lines, pipeline_results)

    # ── Multi-stream results ──────────────────────────────────────────
    if multi_stream_results:
        _add_multi_stream_section(lines, multi_stream_results, fps_threshold)

    # ── Footer ────────────────────────────────────────────────────────
    lines.append("---")
    lines.append("*Report generated by dx-benchmark tool*")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return output_path


# ── Test Timing section ──────────────────────────────────────────────────

def _add_timing_section(lines: list[str], fingerprint: dict) -> None:
    timing = fingerprint.get("timing")
    history = fingerprint.get("timing_history") or _build_legacy_timing_history(fingerprint)
    if not timing and not history:
        return

    lines.append("## Test Timing")
    lines.append("")
    if history:
        show_families = _history_column_needed(history, "families")
        show_task = _history_column_needed(history, "task")
        show_sizes = _history_column_needed(history, "sizes")
        show_outcome = _history_column_needed(history, "outcome") or any(
            item.get("outcome", "completed") != "completed" for item in history
        )
        show_details = any(_format_history_details(item) != "—" for item in history)

        headers = ["#", "Type"]
        separators = ["---", "------"]
        if show_families:
            headers.append("Families")
            separators.append("----------")
        if show_task:
            headers.append("Task")
            separators.append("------")
        if show_sizes:
            headers.append("Sizes")
            separators.append("-------")
        if show_outcome:
            headers.append("Outcome")
            separators.append("--------")
        if show_details:
            headers.append("Details")
            separators.append("---------")
        headers.extend(["Start", "End", "Duration"])
        separators.extend(["-------", "-----", "----------"])

        lines.append("| " + " | ".join(headers) + " |")
        lines.append("|" + "|".join(separators) + "|")
        for idx, item in enumerate(history, start=1):
            row = [str(idx), _format_execution_type(item)]
            families = item.get("families", [])
            families_s = "all" if "all" in families else ", ".join(families) if families else "N/A"
            sizes = item.get("sizes", [])
            sizes_s = ",".join(sizes) if sizes else "N/A"
            if show_families:
                row.append(families_s)
            if show_task:
                row.append(item.get("task", "N/A"))
            if show_sizes:
                row.append(sizes_s)
            if show_outcome:
                row.append(item.get("outcome", "completed"))
            if show_details:
                row.append(_format_history_details(item))
            row.extend([
                item.get("start", "N/A"),
                item.get("end", "N/A"),
                _format_duration(item.get("duration_sec", 0)),
            ])
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")


def _build_legacy_timing_history(fingerprint: dict) -> list[dict]:
    timing = fingerprint.get("timing")
    if not timing:
        return []
    params = fingerprint.get("benchmark_params", {})
    benchmarked_models = fingerprint.get("benchmarked_models", [])
    sizes = sorted({m.get("size") for m in benchmarked_models if m.get("size")})
    return [{
        "mode": "run",
        "start": timing.get("start"),
        "end": timing.get("end"),
        "duration_sec": timing.get("duration_sec", 0),
        "families": params.get("families", []),
        "task": "mixed",
        "sizes": sizes,
        "retry_failed": bool(params.get("retry_failed", False)),
        "outcome": "completed",
    }]


def _format_duration(duration_sec: float | int | None) -> str:
    if not duration_sec:
        return "N/A"
    dur_sec = float(duration_sec)
    mins, secs = divmod(int(dur_sec), 60)
    hours, mins = divmod(mins, 60)
    if hours:
        return f"{hours}h {mins}m {secs}s"
    if mins:
        return f"{mins}m {secs}s"
    return f"{dur_sec:.1f}s"


def _format_execution_type(item: dict) -> str:
    mode = item.get("mode")
    if mode == "retry-failed":
        return "retry-failed"
    if mode == "resume":
        return "resume"
    return "run"


def _format_history_details(item: dict) -> str:
    failure_stage = item.get("failure_stage")
    failure_model = item.get("failure_model")
    failure_ort = item.get("failure_ort")
    failure_reason = item.get("failure_reason")

    details: list[str] = []
    if failure_stage:
        details.append(str(failure_stage))
    if failure_model:
        details.append(str(failure_model))
    if failure_ort:
        details.append(f"ORT={failure_ort}")
    if failure_reason:
        details.append(str(failure_reason))

    return " / ".join(details) if details else "—"


def _history_column_needed(history: list[dict], key: str) -> bool:
    normalized_values = {_normalize_history_value(item.get(key)) for item in history}
    return len(normalized_values) > 1


def _normalize_history_value(value: Any) -> tuple:
    if isinstance(value, list):
        return tuple(value)
    if value is None:
        return ("N/A",)
    return (str(value),)


# ── Executive Summary section ────────────────────────────────────────────

def _add_executive_summary(
    lines: list[str],
    model_results: list[dict],
    pipeline_results: list[dict],
    multi_stream_results: list[dict],
    fps_threshold: float = 30.0,
) -> None:
    """Add a top-level summary table with key metrics per model."""
    if not model_results and not pipeline_results:
        return

    # Gather per-model metrics keyed by (model, use_ort)
    latency_map: dict[tuple[str, bool], dict] = {}   # model,ort -> latency result
    throughput_map: dict[tuple[str, bool], dict] = {} # model,ort -> throughput result
    e2e_map: dict[tuple[str, bool], dict] = {}        # model,ort -> e2e result
    capacity_map: dict[tuple[str, bool], int] = {}    # model,ort -> max channel capacity

    for r in model_results:
        key = (r.get("model", "?"), r.get("use_ort", False))
        if r.get("family") == "latency":
            latency_map[key] = r
        elif r.get("family") == "throughput":
            throughput_map[key] = r

    for r in pipeline_results:
        key = (r.get("model", "?"), r.get("use_ort", False))
        e2e_map[key] = r

    # Build capacity from multi-stream using the single shared capacity rule
    # (status ok + all runs completed + per-ch FPS >= threshold).
    for r in multi_stream_results:
        sc = r.get("stream_count", 0)
        if sc < 1 or not is_capacity_pass(r, fps_threshold):
            continue
        key = (r.get("model", "?"), r.get("use_ort", False))
        if sc > capacity_map.get(key, 0):
            capacity_map[key] = sc

    # Collect unique models grouped by task, in canonical task + size order
    all_results = list(model_results) + list(pipeline_results)
    task_model_map: dict[str, set[str]] = {}
    model_size: dict[str, str] = {}  # stamped size per model (version-proof ordering)
    for r in all_results:
        task = r.get("task", "unknown")
        model = r.get("model", "?")
        task_model_map.setdefault(task, set()).add(model)
        if r.get("size"):
            model_size[model] = r["size"]

    # Sort tasks in canonical order
    sorted_tasks = sorted(task_model_map.items(),
                          key=lambda kv: _TASK_DISPLAY_ORDER.get(kv[0], 99))

    if not sorted_tasks:
        return

    lines.append("## Executive Summary")
    lines.append("")

    _HDR = "| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |"
    _SEP = "|-------|-----|:------------:|:----------------:|:-------:|:------------:|"

    degraded = False  # any cell backed by a non-ok result → footnote

    def _cell(result: dict | None, value_key: str, fmt: str) -> str:
        nonlocal degraded
        if not result or result.get(value_key) is None:
            return "—"
        s = format(result[value_key], fmt)
        if result.get("status", "ok") != "ok":
            degraded = True
            s += "*"
        return s

    for task, task_models in sorted_tasks:
        task_name = _TASK_DISPLAY_NAMES.get(task, task)
        lines.append(f"### {task_name}")
        lines.append("")
        lines.append(_HDR)
        lines.append(_SEP)

        for model in _sort_models_by_size(list(task_models), model_size):
            for use_ort in [True, False]:
                key = (model, use_ort)
                ort_s = "ON" if use_ort else "OFF"

                lat_s = _cell(latency_map.get(key), "total_ms", ".2f")
                thr_s = _cell(throughput_map.get(key), "fps", ".1f")
                e2e_s = _cell(e2e_map.get(key), "avg_e2e_fps", ".1f")

                cap = capacity_map.get(key)
                cap_s = str(cap) if cap else "—"

                lines.append(f"| {model} | {ort_s} | {lat_s} | {thr_s} | {e2e_s} | {cap_s} |")

        lines.append("")

    if degraded:
        lines.append("> **\\***: value came from a degraded (partial/failed) run — "
                     "see the per-family tables below for the status and reason.")
        lines.append("")


def _add_protocol_section(lines: list[str], fingerprint: dict) -> None:
    protocol = fingerprint.get("protocol") or {}
    if not protocol:
        return

    lines.append("## Measurement Protocol")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("|------|-------|")
    lines.append(f"| Version | {protocol.get('version', 'N/A')} |")
    lines.append(f"| Thermal Mode | {protocol.get('thermal_mode', 'N/A')} |")
    lines.append(f"| Throughput Time | {protocol.get('model_time_sec', 'N/A')} s |")
    lines.append(f"| Latency Loops | {protocol.get('model_latency_loops', protocol.get('model_time_sec', 'N/A'))} |")
    lines.append(f"| Model Warmup | {protocol.get('model_warmup_runs', 'N/A')} |")
    # v2: split latency/throughput runs
    if 'model_latency_runs' in protocol:
        lines.append(f"| Model Latency Runs | {protocol.get('model_latency_runs', 'N/A')} |")
        lines.append(f"| Model Throughput Runs | {protocol.get('model_throughput_runs', 'N/A')} |")
    elif 'model_runs' in protocol:
        lines.append(f"| Model Runs | {protocol.get('model_runs', 'N/A')} |")
    lines.append(f"| E2E Runs | {protocol.get('e2e_runs', 'N/A')} |")
    lines.append(f"| FPS Threshold | {protocol.get('fps_threshold', 'N/A')} |")
    lines.append(f"| Multi-Stream Search | {protocol.get('multi_stream_search', 'N/A')} |")
    lines.append(f"| Stable Capacity Rule | {protocol.get('stable_capacity_rule', 'N/A')} |")
    # v2 thermal params (conditionally)
    if protocol.get('thermal_mode') == 'steady':
        lines.append(f"| Cooldown Target ΔT | {protocol.get('thermal_cooldown_target_delta_c', 'N/A')} °C |")
        lines.append(f"| Cooldown Absolute Cap | {protocol.get('thermal_cooldown_abs_cap_c', 'N/A')} °C |")
        lines.append(f"| Hot-Start Block | {protocol.get('thermal_hot_start_block_c', 'N/A')} °C |")
        lines.append(f"| Cooldown Max Time | {protocol.get('thermal_cooldown_max_sec', 'N/A')} s |")
    lines.append(f"| NPU Warmup | {protocol.get('npu_warmup_sec', 'N/A')} s |")
    lines.append(f"| NPU Drain | {protocol.get('npu_drain_sec', 'N/A')} s |")
    lines.append("")


# ── Benchmark Parameters section ─────────────────────────────────────────

def _add_benchmark_params_section(lines: list[str], fingerprint: dict) -> None:
    params = fingerprint.get("benchmark_params")
    if not params:
        return
    lines.append("## Benchmark Parameters")
    lines.append("")
    lines.append("| Parameter | Value |")
    lines.append("|-----------|-------|")
    lines.append(f"| Throughput duration (-t) | {params.get('model_time_sec', 'N/A')} sec |")
    lines.append(f"| Latency loops (-l) | {params.get('model_latency_loops', 'N/A')} |")
    lines.append(f"| Model warmup runs | {params.get('model_warmup', 'N/A')} |")
    # v2: split latency/throughput runs
    if 'model_latency_runs' in params:
        lines.append(f"| Model latency runs | {params.get('model_latency_runs', 'N/A')} |")
        lines.append(f"| Model throughput runs | {params.get('model_throughput_runs', 'N/A')} |")
    elif 'model_runs' in params:
        lines.append(f"| Model runs | {params.get('model_runs', 'N/A')} |")
    lines.append(f"| E2E pipeline runs | {params.get('e2e_runs', 'N/A')} |")
    lines.append(f"| Multi-stream FPS threshold | {params.get('fps_threshold', 'N/A')} fps |")
    lines.append(f"| ORT modes | {', '.join(params.get('ort_modes', []))} |")
    families = params.get("families", [])
    families_s = "all" if "all" in families else ", ".join(families)
    lines.append(f"| Benchmark families | {families_s} |")
    lines.append("")


# ── Model Info section ───────────────────────────────────────────────────

def _add_model_info_section(lines: list[str], fingerprint: dict, model_results: list[dict] | None = None) -> None:
    models = fingerprint.get("benchmarked_models")
    if not models:
        return

    # Build NPU memory lookup from model results (first occurrence per model)
    npu_mem_map: dict[str, int | None] = {}
    for r in (model_results or []):
        name = r.get("model", "")
        if name and name not in npu_mem_map:
            npu_mem_map[name] = r.get("npu_model_mem_bytes")

    lines.append("## Benchmarked Models")
    lines.append("")

    # Group by task in canonical order
    by_task: dict[str, list[dict]] = {}
    for m in models:
        by_task.setdefault(m["task"], []).append(m)
    by_task = dict(sorted(by_task.items(), key=lambda kv: _TASK_DISPLAY_ORDER.get(kv[0], 99)))

    lines.append("| Model | Task | Input Size | NPU Memory (MB) | ORT CPU Offload | Multi-Stream Sweep |")
    lines.append("|-------|------|------------|:----------------:|:---------------:|:------------------:|")

    for task, task_models in by_task.items():
        task_name = _TASK_DISPLAY_NAMES.get(task, task)
        meta = TASK_MODEL_META.get(task, {})
        ort_s = "Yes" if meta.get("ort_offload", "").lower().startswith("yes") else "No"
        multi_s = "✅" if task in MULTI_STREAM_SUPPORTED_TASKS else "—"
        input_size = meta.get("input_size", "N/A")
        if isinstance(input_size, (list, tuple)) and len(input_size) == 2:
            input_size_s = f"{input_size[0]}×{input_size[1]}"
        else:
            input_size_s = str(input_size)
        for m in sorted(task_models, key=lambda x: _SIZE_ORDER.get(x.get("size", ""), 99)):
            mem_bytes = npu_mem_map.get(m["name"])
            if mem_bytes is not None:
                mem_mb_s = f"{mem_bytes / (1024 * 1024):.1f}"
            else:
                mem_mb_s = "—"
            lines.append(f"| {m['name']} | {task_name} | {input_size_s} | {mem_mb_s} | {ort_s} | {multi_s} |")
    lines.append("")


# ── Environment section ──────────────────────────────────────────────────

def _add_environment_section(lines: list[str], fingerprint: dict) -> None:
    lines.append("## Environment")
    lines.append("")
    host = fingerprint.get("host", {})
    npu = fingerprint.get("npu", {})
    product_name = fingerprint.get("product_name")
    lines.append("| Item | Value |")
    lines.append("|------|-------|")
    if product_name:
        lines.append(f"| Product | {product_name} |")
    lines.append(f"| Hostname | {host.get('hostname', 'N/A')} |")
    lines.append(f"| OS | {host.get('os', 'N/A')} |")
    lines.append(f"| Kernel | {host.get('kernel', 'N/A')} |")
    lines.append(f"| CPU | {host.get('cpu', 'N/A')} |")
    lines.append(f"| CPU Cores | {host.get('cpu_count', 'N/A')} |")
    lines.append(f"| RAM | {host.get('ram_gb', 'N/A')} GB |")
    lines.append(f"| NPU SKU | {npu.get('sku', 'N/A')} |")
    lines.append(f"| DX-AllSuite | {fingerprint.get('dx_all_suite_version') or 'N/A'} |")
    lines.append(f"| Benchmark Tool | {fingerprint.get('benchmark_tool_version') or 'N/A'} |")
    lines.append(f"| NPU RT | {npu.get('rt_version', 'N/A')} |")
    if npu.get("rt_version_raw") and npu.get("rt_version_raw") != npu.get("rt_version"):
        lines.append(f"| NPU RT (commit) | {npu.get('rt_version_raw')} |")
    lines.append(f"| NPU Driver (RT) | {npu.get('driver', 'N/A')} |")
    lines.append(f"| NPU Driver (PCIe) | {npu.get('pcie_driver', 'N/A')} |")
    lines.append(f"| NPU Firmware | {npu.get('firmware', 'N/A')} |")
    lines.append(f"| NPU Memory | {npu.get('memory', 'N/A')} |")
    lines.append(f"| NPU Board | {npu.get('board', 'N/A')} |")
    lines.append(f"| NPU PCIe | {npu.get('pcie', 'N/A')} |")
    lines.append("")

    tools = fingerprint.get("tools", {})
    lines.append("### Tools")
    lines.append("")
    lines.append("| Tool | Available | Version |")
    lines.append("|------|-----------|---------|")
    for name, info in tools.items():
        avail = "Yes" if info.get("available") else "**No**"
        ver = info.get("version", "N/A") or "N/A"
        if len(str(ver)) > 60:
            ver = str(ver)[:60] + "..."
        lines.append(f"| {name} | {avail} | {ver} |")
    lines.append("")


# ── Input Video section ──────────────────────────────────────────────────

def _add_video_section(lines: list[str], video_infos: dict[str, dict] | None) -> None:
    if not video_infos:
        return

    lines.append("## Input Videos")
    lines.append("")

    sorted_groups = sorted(video_infos.items(), key=lambda kv: _GROUP_ORDER.get(kv[0], 99))
    for group, info in sorted_groups:
        group_name = _GROUP_DISPLAY_NAMES.get(group, group)
        lines.append(f"### {group_name}")
        lines.append("")
        lines.append("| Item | Value |")
        lines.append("|------|-------|")
        lines.append(f"| File | {info.get('filename', 'N/A')} |")
        w = info.get("width", 0)
        h = info.get("height", 0)
        if w and h:
            lines.append(f"| Resolution | {w} x {h} |")
        lines.append(f"| Codec | {info.get('codec', 'N/A')} |")
        lines.append(f"| FPS | {info.get('fps', 'N/A')} |")
        lines.append(f"| Frames | {info.get('nb_frames', 'N/A')} |")
        dur = info.get("duration_sec", 0)
        if dur:
            lines.append(f"| Duration | {dur:.1f} sec |")
        bitrate = info.get("bitrate_mbps")
        if bitrate:
            lines.append(f"| Bitrate | {bitrate} Mbps |")
        lines.append(f"| Format | {info.get('format', 'N/A')} |")
        lines.append(f"| Pixel Format | {info.get('pix_fmt', 'N/A')} |")
        lines.append("")


# ── Clock formatting helper ──────────────────────────────────────────────

def _format_clock(clk_min: float | None, clk_max: float | None) -> str:
    """Format min~max clock MHz.  Returns '—' when no data."""
    if clk_min is None and clk_max is None:
        return "—"
    lo = f"{clk_min:.0f}" if clk_min is not None else "?"
    hi = f"{clk_max:.0f}" if clk_max is not None else "?"
    if clk_min is not None and clk_max is not None and clk_min == clk_max:
        return lo  # no throttling → single value
    return f"{lo}~{hi}"


def _format_temp(temp_min: float | None, temp_max: float | None) -> str:
    """Format min~max temperature °C.  Returns 'N/A' when no data."""
    if temp_min is None and temp_max is None:
        return "N/A"
    lo = f"{temp_min:.0f}" if temp_min is not None else "?"
    hi = f"{temp_max:.0f}" if temp_max is not None else "?"
    if temp_min is not None and temp_max is not None and temp_min == temp_max:
        return lo
    return f"{lo}~{hi}"


# ── Model Throughput section ─────────────────────────────────────────────

def _bc_sweep_cell(curve_str: str, winner) -> str:
    """Format a stored "bc:fps bc:fps …" curve as "bc:fps · bc:fps …" with the
    winner bolded + ★. Handles any probe range (2..N) — it's a single string cell."""
    parts = []
    for tok in str(curve_str).split():
        if ":" not in tok:
            continue
        bc_s, fps_s = tok.split(":", 1)
        try:
            bc, fps = int(bc_s), float(fps_s)
        except ValueError:
            continue
        cell = f"[{bc}]:{fps:.1f}"
        if winner is not None and bc == int(winner):
            cell = f"**{cell} ★**"
        parts.append(cell)
    return " · ".join(parts)


def _add_bc_sweep_subtable(lines: list[str], results: list[dict]) -> None:
    """Below a throughput table: per-model buffer-count sweep curve (bc:fps), winner
    bolded. One string cell per model absorbs any probe range without widening the table."""
    sweeps = [r for r in results if r.get("buffer_count_curve")]
    if not sweeps:
        return
    lines.append("")
    lines.append("_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):")
    lines.append("")
    lines.append("| Model | BC ★ | Sweep ([bc]:fps) |")
    lines.append("|-------|------|----------------|")
    for r in sweeps:
        bc = r.get("buffer_count")
        lines.append(f"| {r.get('model', '?')} | {bc if bc is not None else '—'} | "
                     f"{_bc_sweep_cell(r.get('buffer_count_curve', ''), bc)} |")
    lines.append("")


def _add_model_throughput_section(lines: list[str], throughput: list[dict]) -> None:
    lines.append("### Throughput (Multi-Core, Async)")
    lines.append("")

    task_groups = _group_by_task(throughput)

    # Check if clock data is available in any result
    has_npu_clock = any(r.get("npu_clock_mhz_min") is not None or r.get("npu_clock_mhz_max") is not None for r in throughput)
    has_bc = any(r.get("buffer_count") is not None for r in throughput)

    if has_bc:
        # Legend once per report; the per-table sweep captions below just mark ★.
        lines.append(
            "> **Buffer-count sweep (★)** — the _Buffer-count sweep_ tables below list "
            "throughput fps per `--buffer-count`; ★ marks the winner (highest measured "
            "throughput, at full probe precision; fps rounded to 1 decimal). A smaller "
            "buffer-count wins only on an exact tie. The sweep's goal is the throughput "
            "ceiling — the winning buffer-count value itself is secondary, since tied "
            "buffer-counts deliver effectively equal throughput."
        )
        lines.append("")

    for task, task_results in task_groups.items():
        task_name = _TASK_DISPLAY_NAMES.get(task, task)
        sorted_results = _sort_by_size(task_results)
        ort_on = _sort_by_size([r for r in sorted_results if r.get("use_ort")])
        ort_off = _sort_by_size([r for r in sorted_results if not r.get("use_ort")])

        if len(task_groups) > 1:
            lines.append(f"#### {task_name}")
            lines.append("")

        # Build dynamic header
        hdr_cols = ["Model", "FPS"]
        sep_cols = ["-------", "-----"]
        if has_bc:
            hdr_cols.append("BC")
            sep_cols.append("---")
        hdr_cols += ["CPU%", "NPU Avg%", "NPU Max%", "NPU Temp °C"]
        sep_cols += ["------", "----------", "----------", "-------------"]
        if has_npu_clock:
            hdr_cols.append("NPU MHz")
            sep_cols.append("---------")
        hdr_cols.append("Status")
        sep_cols.append("--------")
        hdr_line = "| " + " | ".join(hdr_cols) + " |"
        sep_line = "|" + "|".join(sep_cols) + "|"

        for ort_label, ort_results in [("ORT = ON", ort_on), ("ORT = OFF", ort_off)]:
            if not ort_results:
                continue
            lines.append(f"**{ort_label}**")
            lines.append("")
            lines.append(hdr_line)
            lines.append(sep_line)
            for r in ort_results:
                fps_val = r.get("fps")
                fps_std = r.get("fps_std")
                if fps_val is not None:
                    fps = f'{fps_val:.1f}'
                    if fps_std is not None:
                        fps += f' ±{fps_std:.1f}'
                else:
                    fps = "N/A"
                cpu = f'{r["cpu_pct"]:.0f}' if r.get("cpu_pct") is not None else "N/A"
                npu_avg = f'{(r.get("npu_total_avg_pct") or 0):.1f}'
                npu_max_val = r.get("npu_total_max_pct")
                npu_max = f'{npu_max_val:.1f}' if npu_max_val is not None else "—"
                temp_s = _format_temp(r.get("npu_temp_min_c"), r.get("npu_temp_max_c"))
                row = f"| {r.get('model', '?')} | {fps}"
                if has_bc:
                    bc = r.get("buffer_count")
                    row += f" | {bc if bc is not None else '—'}"
                row += f" | {cpu} | {npu_avg} | {npu_max} | {temp_s}"
                if has_npu_clock:
                    row += f" | {_format_clock(r.get('npu_clock_mhz_min'), r.get('npu_clock_mhz_max'))}"
                row += f" | {_status_cell(r)} |"
                lines.append(row)
            _add_bc_sweep_subtable(lines, ort_results)
            lines.append("")


# ── Model Latency section ───────────────────────────────────────────────

def _add_model_latency_section(lines: list[str], latency: list[dict]) -> None:
    lines.append("### Latency (Single-Core, Sync)")
    lines.append("")

    task_groups = _group_by_task(latency)

    for task, task_results in task_groups.items():
        task_name = _TASK_DISPLAY_NAMES.get(task, task)
        sorted_results = _sort_by_size(task_results)
        ort_on = _sort_by_size([r for r in sorted_results if r.get("use_ort")])
        ort_off = _sort_by_size([r for r in sorted_results if not r.get("use_ort")])

        if len(task_groups) > 1:
            lines.append(f"#### {task_name}")
            lines.append("")

        # ORT=ON and ORT=OFF tables share one column schema for comparability.
        for ort_label, ort_results in [("ORT = ON", ort_on), ("ORT = OFF", ort_off)]:
            if not ort_results:
                continue
            lines.append(f"**{ort_label}**")
            lines.append("")
            lines.append("| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |")
            lines.append("|-------|-----|----------|--------|--------|-------------|--------|")
            for r in ort_results:
                fps = f'{r["fps"]:.1f}' if r.get("fps") is not None else "N/A"
                if r.get("fps") is not None and r.get("fps_std") is not None:
                    fps += f' ±{r["fps_std"]:.1f}'
                total = f'{r["total_ms"]:.2f}' if r.get("total_ms") is not None else "N/A"
                npu_ms = f'{r["npu_task_ms"]:.2f}' if r.get("npu_task_ms") is not None else "N/A"
                cpu_0 = r.get("cpu_0_ms")
                cpu_ms = f'{cpu_0:.2f}' if cpu_0 is not None else "N/A"
                temp_s = _format_temp(r.get("npu_temp_min_c"), r.get("npu_temp_max_c"))
                lines.append(f"| {r.get('model', '?')} | {fps} | {total} | {npu_ms} | {cpu_ms} | {temp_s} | {_status_cell(r)} |")
            lines.append("")


# ── E2E Pipeline section ────────────────────────────────────────────────

def _add_pipeline_section(lines: list[str], pipeline_results: list[dict]) -> None:
    lines.append("## E2E Pipeline (Single-Stream)")
    lines.append("")

    task_groups = _group_by_task(pipeline_results)

    # Check if clock data is available
    has_npu_clock = any(r.get("npu_clock_mhz_min") is not None or r.get("npu_clock_mhz_max") is not None for r in pipeline_results)

    for task, task_results in task_groups.items():
        task_name = _TASK_DISPLAY_NAMES.get(task, task)
        sorted_results = _sort_by_size(task_results)
        ort_on = _sort_by_size([r for r in sorted_results if r.get("use_ort")])
        ort_off = _sort_by_size([r for r in sorted_results if not r.get("use_ort")])

        if len(task_groups) > 1:
            lines.append(f"### {task_name}")
            lines.append("")

        # Build dynamic header/separator
        hdr_cols = ["Model", "Decoder", "Frames", "Runs", "Avg FPS", "Avg Duration (s)",
                     "CPU%", "NPU Avg%", "NPU Max%", "NPU Temp °C"]
        sep_cols = ["-------", "---------", "--------", "------", "---------",
                     "------------------", "------", "----------", "----------",
                     "-------------"]
        if has_npu_clock:
            hdr_cols.append("NPU MHz")
            sep_cols.append("---------")
        hdr_cols.append("RSS MiB")
        sep_cols.append("---------")
        hdr_cols.append("Status")
        sep_cols.append("--------")
        hdr_line = "| " + " | ".join(hdr_cols) + " |"
        sep_line = "|" + "|".join(sep_cols) + "|"

        for ort_label, ort_results in [("ORT = ON", ort_on), ("ORT = OFF", ort_off)]:
            if not ort_results:
                continue
            lines.append(f"**{ort_label}**")
            lines.append("")
            lines.append(hdr_line)
            lines.append(sep_line)
            for r in ort_results:
                temp_s = _format_temp(r.get('npu_temp_min_c'), r.get('npu_temp_max_c'))
                avg_dur = r.get('avg_time_sec')
                avg_dur_s = f"{avg_dur:.2f}" if avg_dur else "N/A"
                fps_s = f"{(r.get('avg_e2e_fps') or 0):.1f}"
                fps_std = r.get('fps_std')
                if fps_std is not None:
                    fps_s += f" ±{fps_std:.1f}"
                row_parts = [
                    r.get('model', '?'),
                    r.get('decoder', 'N/A'),
                    str(r.get('frame_count', 0)),
                    _format_runs(r),
                    fps_s,
                    avg_dur_s,
                    f"{(r.get('avg_cpu_pct') or 0):.0f}",
                    f"{(r.get('npu_total_avg_pct') or 0):.1f}",
                    f"{(r.get('npu_total_max_pct') or 0):.1f}",
                    temp_s,
                ]
                if has_npu_clock:
                    row_parts.append(_format_clock(r.get('npu_clock_mhz_min'), r.get('npu_clock_mhz_max')))
                row_parts.append(f"{(r.get('max_rss_mib') or 0):.0f}")
                row_parts.append(_status_cell(r))
                lines.append("| " + " | ".join(row_parts) + " |")
            lines.append("")

        _add_ort_comparison_table(lines, sorted_results, "avg_e2e_fps", "E2E FPS")


# ── Multi-stream section ────────────────────────────────────────────────

def _add_multi_stream_section(lines: list[str], multi_stream_results: list[dict],
                              fps_threshold: float = 30.0) -> None:
    lines.append("## E2E Pipeline (Multi-Stream)")
    lines.append("")

    task_groups = _group_by_task(multi_stream_results)

    # Check if clock data is available
    has_npu_clock = any(r.get("npu_clock_mhz_min") is not None or r.get("npu_clock_mhz_max") is not None for r in multi_stream_results)

    for task, task_results in task_groups.items():
        task_name = _TASK_DISPLAY_NAMES.get(task, task)
        # Include sc=1 only when it's boundary-relevant: no sc>1 passes
        # for the same model+ORT (meaning capacity is at most 1)
        _pass_above_1 = set()
        for r in task_results:
            if r.get("stream_count", 0) > 1 and is_capacity_pass(r, fps_threshold):
                _pass_above_1.add((r.get("model", "?"), r.get("use_ort")))
        multi_relevant = [
            r for r in task_results
            if r.get("stream_count", 0) > 1
            or (r.get("stream_count", 0) == 1
                and (r.get("model", "?"), r.get("use_ort")) not in _pass_above_1)
        ]
        sorted_results = _sort_by_size(multi_relevant)
        ort_on = _sort_by_size([r for r in sorted_results if r.get("use_ort")])
        ort_off = _sort_by_size([r for r in sorted_results if not r.get("use_ort")])

        if len(task_groups) > 1:
            lines.append(f"### {task_name}")
            lines.append("")

        # Build dynamic header
        hdr_cols = ["Model", "Streams", "Runs", "E2E FPS", "Per-Ch FPS",
                     "CPU%", "NPU Avg%", "NPU Max%", "NPU Temp °C"]
        sep_cols = ["-------", "---------", "------", "---------", "------------",
                     "------", "----------", "----------", "-------------"]
        if has_npu_clock:
            hdr_cols.append("NPU MHz")
            sep_cols.append("---------")
        hdr_cols.append("RSS MiB")
        sep_cols.append("---------")
        hdr_cols.append("Status")
        sep_cols.append("--------")
        hdr_line = "| " + " | ".join(hdr_cols) + " |"
        sep_line = "|" + "|".join(sep_cols) + "|"

        for ort_label, ort_results in [("ORT = ON", ort_on), ("ORT = OFF", ort_off)]:
            if not ort_results:
                continue
            lines.append(f"**{ort_label}**")
            lines.append("")
            lines.append(hdr_line)
            lines.append(sep_line)
            for r in ort_results:
                temp_s = _format_temp(r.get('npu_temp_min_c'), r.get('npu_temp_max_c'))
                fps_s = f"{(r.get('avg_e2e_fps') or 0):.1f}"
                fps_std = r.get('fps_std')
                if fps_std is not None:
                    fps_s += f" ±{fps_std:.1f}"
                row_parts = [
                    r.get('model', '?'),
                    str(r.get('stream_count', 0)),
                    _format_runs(r),
                    fps_s,
                    f"{(r.get('avg_per_channel_fps') or 0):.1f}",
                    f"{(r.get('avg_cpu_pct') or 0):.0f}",
                    f"{(r.get('npu_total_avg_pct') or 0):.1f}",
                    f"{(r.get('npu_total_max_pct') or 0):.1f}",
                    temp_s,
                ]
                if has_npu_clock:
                    row_parts.append(_format_clock(r.get('npu_clock_mhz_min'), r.get('npu_clock_mhz_max')))
                row_parts.append(f"{(r.get('max_rss_mib') or 0):.0f}")
                row_parts.append(_status_cell(r))
                lines.append("| " + " | ".join(row_parts) + " |")
            lines.append("")

        # Channel capacity summary for this task
        _add_capacity_summary(lines, multi_relevant, fps_threshold)

        # Footnote: surface rows hidden from the tables above (sc=1 dropped when a
        # higher sc passes) that are non-ok, so a hidden failure stays discoverable
        # instead of vanishing behind a clean capacity number.
        hidden_non_ok = [
            r for r in task_results
            if r.get("stream_count", 0) == 1
            and (r.get("model", "?"), r.get("use_ort")) in _pass_above_1
            and (r.get("status") or "ok") != "ok"
        ]
        if hidden_non_ok:
            lines.append("> **Note — hidden non-ok measurements** (not shown above; capacity is "
                         "taken from passing rows, so these did not affect the numbers):")
            for r in sorted(hidden_non_ok,
                            key=lambda r: (r.get("model", ""), not r.get("use_ort"))):
                ort_s = "ON" if r.get("use_ort") else "OFF"
                reason = (r.get("reason") or "").strip()
                reason_s = f" — {reason}" if reason else ""
                lines.append(f"> - {r.get('model', '?')} (ORT {ort_s}, sc="
                             f"{r.get('stream_count', '?')}): {r.get('status')}{reason_s}")
            lines.append("")


# ── ORT comparison table ────────────────────────────────────────────────

def _add_ort_comparison_table(lines: list[str], results: list[dict],
                               metric_key: str, metric_label: str) -> None:
    """Add an ORT ON vs OFF comparison table."""
    ort_on = {r.get("model", "?"): r for r in results if r.get("use_ort")}
    ort_off = {r.get("model", "?"): r for r in results if not r.get("use_ort")}
    models = _sort_models_by_size(list(set(ort_on.keys()) | set(ort_off.keys())))

    if not models:
        return

    lines.append(f"**ORT Comparison – {metric_label}**")
    lines.append("")
    lines.append("| Model | ORT ON | ORT OFF | Delta | Delta % |")
    lines.append("|-------|--------|---------|-------|---------|")
    for m in models:
        on_val = ort_on.get(m, {}).get(metric_key)
        off_val = ort_off.get(m, {}).get(metric_key)
        on_s = f"{on_val:.1f}" if on_val is not None else "N/A"
        off_s = f"{off_val:.1f}" if off_val is not None else "N/A"
        if on_val is not None and off_val:
            delta = on_val - off_val
            pct = (delta / off_val * 100) if off_val else 0
            sign = "+" if delta >= 0 else ""
            lines.append(f"| {m} | {on_s} | {off_s} | {sign}{delta:.1f} | {sign}{pct:.1f}% |")
        else:
            lines.append(f"| {m} | {on_s} | {off_s} | N/A | N/A |")
    lines.append("")


# ── Capacity summary ────────────────────────────────────────────────────

def _add_capacity_summary(lines: list[str], results: list[dict],
                          fps_threshold: float = 30.0) -> None:
    """Add max capacity summary from multi-stream results with per-ch FPS."""
    # Per model+ORT: track best SC meeting threshold and whether we hit max tested SC
    capacity: dict[str, dict[str, tuple[int, float]]] = {}
    max_tested: dict[str, dict[str, tuple[int, float]]] = {}  # highest SC tested (regardless of FPS)
    for r in results:
        if not _is_usable_result(r):
            continue
        model = r.get("model", "?")
        ort_key = "on" if r.get("use_ort") else "off"
        per_ch = r.get("avg_per_channel_fps") or 0
        sc = r.get("stream_count", 0)
        # Track capacity (highest SC passing the shared capacity rule)
        if is_capacity_pass(r, fps_threshold):
            if model not in capacity:
                capacity[model] = {}
            current_sc = capacity[model].get(ort_key, (0, 0))[0]
            if sc > current_sc:
                capacity[model][ort_key] = (sc, round(per_ch, 1))
        # Track max tested SC
        if model not in max_tested:
            max_tested[model] = {}
        current_max = max_tested[model].get(ort_key, (0, 0))[0]
        if sc > current_max:
            max_tested[model][ort_key] = (sc, round(per_ch, 1))

    if not capacity:
        return

    lines.append(f"**Channel Capacity Summary** (max streams where per-channel FPS ≥ {fps_threshold:.0f})")
    lines.append("")
    lines.append("| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |")
    lines.append("|-------|-----------------|------------|------------------|------------|")
    for model in _sort_models_by_size(list(capacity.keys())):
        on_cap, on_fps = capacity[model].get("on", (0, 0))
        off_cap, off_fps = capacity[model].get("off", (0, 0))
        # Add "+" suffix if capacity equals the last tested SC and last SC had FPS >= threshold
        # (meaning true capacity could be higher, limited by max_streams setting)
        on_max_sc, on_max_fps = max_tested.get(model, {}).get("on", (0, 0))
        off_max_sc, off_max_fps = max_tested.get(model, {}).get("off", (0, 0))
        on_plus = "+" if on_cap > 0 and on_cap == on_max_sc and on_max_fps >= fps_threshold else ""
        off_plus = "+" if off_cap > 0 and off_cap == off_max_sc and off_max_fps >= fps_threshold else ""
        on_s = f"{on_cap}{on_plus}" if on_cap else "< 1"
        on_fps_s = f"{on_fps:.1f}" if on_fps else "—"
        off_s = f"{off_cap}{off_plus}" if off_cap else "< 1"
        off_fps_s = f"{off_fps:.1f}" if off_fps else "—"
        lines.append(f"| {model} | {on_s} | {on_fps_s} | {off_s} | {off_fps_s} |")
    lines.append("")
    # Add footnote if any "+" entries exist
    has_plus = any(
        (cap_data.get("on", (0,0))[0] > 0 and
         cap_data.get("on", (0,0))[0] == max_tested.get(model, {}).get("on", (0,0))[0] and
         max_tested.get(model, {}).get("on", (0,0))[1] >= fps_threshold) or
        (cap_data.get("off", (0,0))[0] > 0 and
         cap_data.get("off", (0,0))[0] == max_tested.get(model, {}).get("off", (0,0))[0] and
         max_tested.get(model, {}).get("off", (0,0))[1] >= fps_threshold)
        for model, cap_data in capacity.items()
    )
    if has_plus:
        lines.append("> **+**: the last tested stream count still met the FPS threshold. "
                     "The sweep stopped before crossing the threshold, so the true maximum "
                     "sustainable stream count may be higher.")
        lines.append("")
