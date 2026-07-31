"""Model-level benchmark runners.

Two benchmark families:
  - throughput: async (multi-core), high loop count → measures FPS
  - latency:   sync  (single-core) with profiler → measures ms per frame
"""

from __future__ import annotations

import json
import re
import shutil
import statistics
import subprocess
import tempfile
import time
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .config import BenchmarkConfig
from .model_catalog import ModelEntry
from .npu_monitor import NpuMonitor, NpuStats
from .npu_stats_util import merge_npu_stats as _merge_npu_stats
from .runner_pipeline import cleanup_after_timeout as _cleanup_after_timeout
from .runner_pipeline import collect_timeout_incident as _collect_timeout_incident
from .runner_pipeline import maybe_collect_dxrt_incident as _maybe_collect_dxrt_incident


def _stdev(values: list[float]) -> Optional[float]:
    """Return sample stdev if ≥2 values, else None."""
    return statistics.stdev(values) if len(values) >= 2 else None


def select_buffer_count(probe, start=3, floor_max=8, improve_eps=0.01,
                        decline_eps=0.02, max_probe=16, zero_retries=1):
    """Adaptive sweep over run_model ``--buffer-count``.

    ``probe(c)`` runs a short throughput probe at buffer-count ``c`` and returns FPS.
    Throughput vs buffer-count is a unimodal saturation curve (rise -> knee -> slight
    decline).

    Phase 1 — always probe the floor range ``start..floor_max`` (default 3..8) so the
    default buffer-count (6) and its neighborhood are ALWAYS measured, even if an early
    knee would otherwise have stopped sooner.
    Phase 2 — only if throughput is still highest at ``floor_max`` (still rising), keep
    incrementing by 1, stopping at the knee: a decline >= decline_eps past the running
    peak, a confirmed plateau (< improve_eps gain twice), or ``max_probe``.

    Winner = the buffer-count with the HIGHEST measured throughput (the device ceiling);
    a smaller buffer-count wins only on an exact tie. If the winner is the start floor,
    probe one below in case the true peak is lower.

    A probe that reads 0 fps is retried up to ``zero_retries`` times (a transient NPU
    stall, not a real ceiling). If EVERY probe still reads 0 (device unresponsive), the
    winner is ``None`` so the caller can short-circuit instead of "picking" the smallest
    buffer-count off a meaningless all-zero curve.

    Returns ``(winner, curve{c: fps}, edge_hit)`` — ``winner`` is ``None`` when all-zero.
    """
    floor_max = max(floor_max, start)
    curve: dict[int, float] = {}
    edge = False

    def _probe(c: int) -> float:
        """Probe once, retrying up to *zero_retries* times on a 0-fps (transient) read."""
        v = float(probe(c))
        tries = 0
        while v <= 0.0 and tries < zero_retries:
            tries += 1
            v = float(probe(c))
        return v

    # Phase 1: unconditional floor sweep (covers the default buffer-count + margin).
    for c in range(start, floor_max + 1):
        curve[c] = _probe(c)

    # All-zero after retries → device unresponsive; no winner (caller short-circuits).
    if max(curve.values(), default=0.0) <= 0.0:
        return None, curve, edge

    # Phase 2: continue only while the top of the floor is still the max (rising).
    if curve.get(floor_max, -1.0) >= max(curve.values()):
        best = max(curve.values())
        plateau = 0
        c = floor_max + 1
        while c <= max_probe:
            fps = _probe(c)
            curve[c] = fps
            if fps <= best * (1 - decline_eps):
                break                                      # declined past the peak
            gain = (fps - best) / best if best > 0 else 1.0
            best = max(best, fps)
            plateau = plateau + 1 if gain < improve_eps else 0
            if plateau >= 2:
                break                                      # plateau confirmed
            c += 1
        else:
            edge = True                                    # hit max_probe still rising

    def _winner(cv: dict[int, float]) -> int:
        # Highest measured throughput wins (this benchmark reports the ceiling); a
        # smaller buffer-count only wins on an EXACT tie.
        return min(cv, key=lambda k: (-cv[k], k))

    win = _winner(curve)
    if win == start and start > 1:                          # peak may be below the floor
        below = start - 1
        curve[below] = _probe(below)
        win = _winner(curve)
    return win, curve, edge


def _cleanup_run_model(incident_context: str = "") -> None:
    """Kill any lingering run_model processes and recover NPU after timeout.

    Uses a host-wide `pkill -f run_model` on purpose: a benchmark run assumes it
    is the ONLY NPU workload on the machine (any concurrent load would invalidate
    the measurement), so there is no other run_model to protect.
    """
    try:
        subprocess.run(
            ["pkill", "-9", "-f", "run_model"],
            timeout=5, capture_output=True,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass
    time.sleep(0.5)
    _collect_timeout_incident(incident_context or "run_model")
    _cleanup_after_timeout()


def _warmup_with_retries(
    cmd: list[str],
    cfg: BenchmarkConfig,
    incident_context: str,
    work_dir_root: Optional[Path] = None,
) -> bool:
    """Run the warmup command, retrying on timeout.

    A single warmup timeout is usually a transient NPU stall; ``_cleanup_run_model``
    kills the lingering process and recovers the device, so a retry typically
    succeeds. Returns True once any attempt completes, False if every attempt
    (1 + ``cfg.model_warmup_retries``) times out.
    """
    attempts = 1 + max(0, cfg.model_warmup_retries)
    for attempt in range(attempts):
        try:
            if work_dir_root is not None:
                with tempfile.TemporaryDirectory(prefix="bench_warmup_", dir=work_dir_root) as wd:
                    subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=wd)
            else:
                subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            return True
        except subprocess.TimeoutExpired:
            tag = incident_context if attempt == 0 else f"{incident_context}.retry{attempt}"
            _cleanup_run_model(tag)
            if attempt + 1 < attempts:
                print(f"    [warmup timeout] retrying ({attempt + 1}/{attempts - 1})", flush=True)
    return False


@dataclass
class ModelResult:
    """Result of a single model-level benchmark run."""
    model: str
    task: str
    size: str
    use_ort: bool
    family: str          # "throughput" or "latency"
    fps: Optional[float] = None
    total_ms: Optional[float] = None
    npu_task_ms: Optional[float] = None
    cpu_0_ms: Optional[float] = None
    cpu_pct: Optional[float] = None
    fps_std: Optional[float] = None
    buffer_count: Optional[int] = None   # run_model --buffer-count chosen by the probe (throughput)
    buffer_count_curve: Optional[str] = None  # "bc:fps bc:fps …" probe curve (throughput)
    npu_stats: Optional[dict] = None
    input_tensor: Optional[dict] = None
    status: str = "ok"
    reason: str = ""

    def as_dict(self) -> dict:
        d = {
            "model": self.model,
            "task": self.task,
            "size": self.size,
            "use_ort": self.use_ort,
            "family": self.family,
            "fps": self.fps,
            "fps_std": self.fps_std,
            "total_ms": self.total_ms,
            "npu_task_ms": self.npu_task_ms,
            "cpu_0_ms": self.cpu_0_ms,
            "cpu_pct": self.cpu_pct,
            "buffer_count": self.buffer_count,
            "buffer_count_curve": self.buffer_count_curve,
            "status": self.status,
            "reason": self.reason,
        }
        if self.npu_stats:
            d.update(self.npu_stats)
        if self.input_tensor:
            d["input_tensor"] = self.input_tensor
        return d


def _parse_input_tensor_shape(log: str) -> Optional[dict]:
    """Extract the first input tensor info from run_model output.

    Matches lines like:  ``  -  images, UINT8, [1, 640, 640, 3 ]``
    Returns e.g. ``{"name": "images", "dtype": "UINT8", "shape": [1, 640, 640, 3]}``.
    """
    m = re.search(
        r"-\s+(\w+),\s+(\w+),\s*\[([\d,\s]+)\]",
        log,
    )
    if not m:
        return None
    name = m.group(1)
    dtype = m.group(2)
    shape = [int(x.strip()) for x in m.group(3).split(",") if x.strip()]
    return {"name": name, "dtype": dtype, "shape": shape}


def _parse_fps_from_log(log: str) -> Optional[float]:
    """Extract average FPS from run_model output."""
    fps_values = []
    for m in re.finditer(r"FPS\s*:\s*([\d.]+)", log):
        fps_values.append(float(m.group(1)))
    return sum(fps_values) / len(fps_values) if fps_values else None


def _parse_npu_memory_bytes(log: str) -> Optional[int]:
    """Extract NPU memory usage in bytes from run_model output.

    Matches lines like: 'NPU memory usage 124,731,520 bytes'
    """
    m = re.search(r"NPU memory usage\s+([\d,]+)\s+bytes", log)
    if m:
        return int(m.group(1).replace(",", ""))
    return None


def _parse_cpu_pct(stderr: str) -> Optional[float]:
    """Extract CPU% from GNU time output."""
    m = re.search(r"__CPU_PERCENT__=([\d]+)%", stderr)
    if m:
        return float(m.group(1))
    return None


def _parse_profiler_metric(profiler_path: Path, metric_name: str) -> Optional[float]:
    """Extract a metric's average duration (ms) from profiler.json.

    Searches JSON keys case-insensitively for *metric_name* and averages
    durations across ALL matching keys (one event per job/key).
    """
    if not profiler_path.exists():
        return None
    try:
        with open(profiler_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    target_key = metric_name.lower()
    all_durations: list[float] = []
    for key, events in data.items():
        if target_key not in key.lower():
            continue
        if not isinstance(events, list) or not events:
            continue
        for ev in events:
            if "start" in ev and "end" in ev:
                all_durations.append(ev["end"] - ev["start"])
    if all_durations:
        avg_ns = sum(all_durations) / len(all_durations)
        return avg_ns / 1_000_000  # ns → ms
    return None


def run_throughput(
    model: ModelEntry,
    use_ort: bool,
    cfg: BenchmarkConfig,
    save_dir: Optional[Path] = None,
) -> ModelResult:
    """Run async (multi-core) throughput benchmark for one model.

    Performs one warmup run followed by *cfg.model_runs* measured runs and
    reports the average FPS, matching the E2E pipeline measurement approach.
    """
    cmd = [
        "/usr/bin/time", "-f", "__CPU_PERCENT__=%P",
        "run_model", "-m", str(model.path),
        "-t", str(cfg.model_time_sec),
        "--warmup-runs", str(cfg.model_warmup),
    ]
    if use_ort:
        cmd.append("--use-ort")

    num_runs = max(1, cfg.model_throughput_runs)
    ort_tag = "ort_on" if use_ort else "ort_off"

    # ── buffer-count probe: find the knee for THIS model×HW, then measure there ──
    def _bc_probe(c: int) -> float:
        pcmd = ["run_model", "-m", str(model.path),
                "-t", str(cfg.buffer_count_probe_sec), "--buffer-count", str(c)]
        if use_ort:
            pcmd.append("--use-ort")
        try:
            p = subprocess.run(pcmd, capture_output=True, text=True,
                               timeout=cfg.buffer_count_probe_sec + 120)
        except subprocess.TimeoutExpired:
            _cleanup_run_model(f"{model.name}.{ort_tag}.bufprobe.c{c}")
            return 0.0
        fps = _parse_fps_from_log(p.stdout + "\n" + p.stderr)
        return fps if fps is not None else 0.0

    buffer_count, bc_curve, bc_edge = select_buffer_count(
        _bc_probe,
        start=cfg.buffer_count_probe_start,
        floor_max=cfg.buffer_count_probe_floor_max,
        improve_eps=cfg.buffer_count_improve_eps,
        decline_eps=cfg.buffer_count_decline_eps,
        max_probe=cfg.buffer_count_max_probe,
        zero_retries=cfg.buffer_count_probe_retries,
    )
    bc_curve_str = " ".join(f"{k}:{v:.1f}" for k, v in sorted(bc_curve.items()))
    # All probes read 0 fps even after retries → device unresponsive. Don't "pick" a
    # meaningless winner or waste warmup+measured runs; fail fast so the circuit breaker
    # (which treats no_fps as fatal) can decide whether the device is truly dead.
    if buffer_count is None:
        print(f"    [buffer-count] all probes 0 fps → device unresponsive; skipping throughput "
              f"(probe {cfg.buffer_count_probe_sec}s: {bc_curve_str})", flush=True)
        return ModelResult(
            model=model.name, task=model.task, size=model.size,
            use_ort=use_ort, family="throughput",
            status="no_fps", buffer_count=None, buffer_count_curve=bc_curve_str,
            reason="all buffer-count probes returned 0 fps (device unresponsive)",
        )
    print(f"    [buffer-count] winner={buffer_count} "
          f"(probe {cfg.buffer_count_probe_sec}s: "
          + ", ".join(f"{k}:{v:.1f}" for k, v in sorted(bc_curve.items())) + ")", flush=True)
    if bc_edge:
        print(f"    [WARN] buffer-count still rising at probe cap {cfg.buffer_count_max_probe} "
              f"(winner={buffer_count}); consider raising buffer_count_max_probe", flush=True)
    cmd += ["--buffer-count", str(buffer_count)]

    # Warmup run (discard result); retry on transient timeout before giving up the cell
    print(f"    [throughput warmup] (-t {cfg.model_time_sec}s)", flush=True)
    if not _warmup_with_retries(cmd, cfg, f"{model.name}.{ort_tag}.throughput.warmup"):
        return ModelResult(
            model=model.name, task=model.task, size=model.size,
            use_ort=use_ort, family="throughput",
            status="timeout", buffer_count=buffer_count, buffer_count_curve=bc_curve_str,
            reason=f"warmup exceeded 600s on all {1 + max(0, cfg.model_warmup_retries)} attempt(s)",
        )

    # Measured runs
    fps_values = []
    cpu_pcts = []
    last_combined = ""
    npu_stats_accum: list[NpuStats] = []
    last_npu_mem = None

    # Backfill: keep attempting until *num_runs* successful runs or the attempt
    # budget (num_runs + model_run_retries) is exhausted. Transient timeouts/parse
    # failures no longer leave a permanent partial when retries can fill the gap.
    target = num_runs
    max_attempts = target + max(0, cfg.model_run_retries)
    attempt = 0
    timeout_runs = 0
    parse_fail_runs = 0
    while len(fps_values) < target and attempt < max_attempts:
        attempt += 1
        slot = len(fps_values) + 1
        label = f"run{slot}" if attempt <= target else f"run{slot}.retry{attempt - target}"
        print(f"    [throughput {label} ({len(fps_values)}/{target} ok, attempt {attempt}/{max_attempts})]", end=" ", flush=True)
        t0_run = time.monotonic()
        npu = NpuMonitor(cfg.npu_core_ids, cfg.npu_warmup_sec, cfg.npu_drain_sec)
        npu.start()

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=600,
            )
            combined = proc.stdout + "\n" + proc.stderr
        except subprocess.TimeoutExpired:
            npu.stop()
            _cleanup_run_model(f"{model.name}.{ort_tag}.throughput.{label}")
            timeout_runs += 1
            print("TIMEOUT", flush=True)
            continue

        npu_stats = npu.stop()

        if save_dir:
            _save_raw(save_dir, model.name, f"throughput.{label}", use_ort, combined, npu_stats.raw_log)

        fps = _parse_fps_from_log(combined)
        if not fps or proc.returncode != 0:
            _maybe_collect_dxrt_incident(combined, f"{model.name}.{ort_tag}.throughput.{label}")
        if not fps:
            parse_fail_runs += 1
            print("no fps parsed", flush=True)
            continue

        fps_values.append(fps)
        last_combined = combined
        npu_stats_accum.append(npu_stats)
        print(f"{fps:.1f} fps ({time.monotonic() - t0_run:.1f}s)", flush=True)

        cpu_pct = _parse_cpu_pct(proc.stderr)
        if cpu_pct is not None:
            cpu_pcts.append(cpu_pct)

        mem = _parse_npu_memory_bytes(combined)
        if mem is not None:
            last_npu_mem = mem

    if not fps_values:
        return ModelResult(
            model=model.name, task=model.task, size=model.size,
            use_ort=use_ort, family="throughput",
            status="no_fps", buffer_count=buffer_count, buffer_count_curve=bc_curve_str,
            reason="Could not parse FPS from any run",
        )

    avg_fps = sum(fps_values) / len(fps_values)
    fps_std = _stdev(fps_values)
    avg_cpu = sum(cpu_pcts) / len(cpu_pcts) if cpu_pcts else None

    # Merge NpuStats across all measured runs
    merged_npu = _merge_npu_stats(npu_stats_accum, cfg.npu_core_ids)
    npu_dict = merged_npu.as_dict(cfg.npu_core_ids)
    if last_npu_mem is not None:
        npu_dict["npu_model_mem_bytes"] = last_npu_mem

    input_tensor = _parse_input_tensor_shape(last_combined)

    status = "ok" if len(fps_values) >= target else "partial"
    reason = f"avg of {len(fps_values)}/{target} runs"
    if status == "partial":
        reason += f" (backfill exhausted after {attempt} attempts: {timeout_runs} timeout, {parse_fail_runs} unparsable)"

    result = ModelResult(
        model=model.name, task=model.task, size=model.size,
        use_ort=use_ort, family="throughput",
        fps=avg_fps,
        fps_std=fps_std,
        cpu_pct=avg_cpu,
        buffer_count=buffer_count,
        buffer_count_curve=bc_curve_str,
        npu_stats=npu_dict,
        input_tensor=input_tensor,
        status=status,
        reason=reason,
    )

    return result


def run_latency(
    model: ModelEntry,
    use_ort: bool,
    cfg: BenchmarkConfig,
    save_dir: Optional[Path] = None,
) -> ModelResult:
    """Run sync (single-core) latency benchmark with profiler for one model.

    Performs one warmup run followed by *cfg.model_runs* measured runs and
    reports the average latency, matching the E2E pipeline measurement approach.
    """
    work_dir_root = None
    if save_dir is not None:
        work_dir_root = save_dir / ".tmp"
        work_dir_root.mkdir(parents=True, exist_ok=True)

    cmd = [
        "/usr/bin/time", "-f", "__CPU_PERCENT__=%P",
        "run_model", "-m", str(model.path),
        "-s", "--profiler",
        "-l", str(cfg.model_latency_loops),
        "--warmup-runs", str(cfg.model_warmup),
    ]
    if use_ort:
        cmd.append("--use-ort")

    num_runs = max(1, cfg.model_latency_runs)
    ort_tag = "ort_on" if use_ort else "ort_off"

    # Warmup run (discard result); retry on transient timeout before giving up the cell
    print(f"    [latency warmup] (-l {cfg.model_latency_loops}, profiler)", flush=True)
    if not _warmup_with_retries(cmd, cfg, f"{model.name}.{ort_tag}.latency.warmup", work_dir_root=work_dir_root):
        return ModelResult(
            model=model.name, task=model.task, size=model.size,
            use_ort=use_ort, family="latency",
            status="timeout",
            reason=f"warmup exceeded 600s on all {1 + max(0, cfg.model_warmup_retries)} attempt(s)",
        )

    # Measured runs
    total_ms_values = []
    npu_task_ms_values = []
    cpu_0_ms_values = []
    fps_values = []
    cpu_pcts = []
    npu_stats_accum: list[NpuStats] = []
    last_npu_mem = None

    # Backfill: keep attempting until *num_runs* successful runs or the attempt
    # budget (num_runs + model_run_retries) is exhausted. A run counts as successful
    # when profiler metrics OR an FPS fallback parse.
    target = num_runs
    max_attempts = target + max(0, cfg.model_run_retries)
    attempt = 0
    timeout_runs = 0
    parse_fail_runs = 0
    try:
        while (len(total_ms_values) + len(fps_values)) < target and attempt < max_attempts:
            attempt += 1
            slot = len(total_ms_values) + len(fps_values) + 1
            label = f"run{slot}" if attempt <= target else f"run{slot}.retry{attempt - target}"
            print(f"    [latency {label} ({len(total_ms_values) + len(fps_values)}/{target} ok, attempt {attempt}/{max_attempts})]", end=" ", flush=True)
            t0_run = time.monotonic()
            with tempfile.TemporaryDirectory(prefix="bench_latency_", dir=work_dir_root) as work_dir:
                profiler_path = Path(work_dir) / "profiler.json"

                npu = NpuMonitor(cfg.npu_core_ids, cfg.npu_warmup_sec, cfg.npu_drain_sec)
                npu.start()

                try:
                    proc = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=600,
                        cwd=work_dir,
                    )
                    combined = proc.stdout + "\n" + proc.stderr
                except subprocess.TimeoutExpired:
                    npu.stop()
                    _cleanup_run_model(f"{model.name}.{ort_tag}.latency.{label}")
                    timeout_runs += 1
                    print("TIMEOUT", flush=True)
                    continue

                npu_stats = npu.stop()

                npu_task_ms = _parse_profiler_metric(profiler_path, "npu task")
                cpu_0_ms = _parse_profiler_metric(profiler_path, "cpu_0")

                run_ok = True
                if npu_task_ms is not None and cpu_0_ms is not None:
                    elapsed_run = time.monotonic() - t0_run
                    print(f"{npu_task_ms + cpu_0_ms:.1f}ms  (npu={npu_task_ms:.1f} cpu0={cpu_0_ms:.1f}, {elapsed_run:.1f}s)", flush=True)
                    total_ms_values.append(npu_task_ms + cpu_0_ms)
                    npu_task_ms_values.append(npu_task_ms)
                    cpu_0_ms_values.append(cpu_0_ms)
                elif npu_task_ms is not None:
                    elapsed_run = time.monotonic() - t0_run
                    print(f"{npu_task_ms:.1f}ms  (npu only, {elapsed_run:.1f}s)", flush=True)
                    total_ms_values.append(npu_task_ms)
                    npu_task_ms_values.append(npu_task_ms)
                else:
                    fps_fallback = _parse_fps_from_log(combined)
                    if fps_fallback:
                        elapsed_run = time.monotonic() - t0_run
                        print(f"{fps_fallback:.1f} fps (profiler fallback, {elapsed_run:.1f}s)", flush=True)
                        fps_values.append(fps_fallback)
                    else:
                        run_ok = False
                        parse_fail_runs += 1
                        print("parse failed", flush=True)

                if not run_ok or proc.returncode != 0:
                    _maybe_collect_dxrt_incident(
                        combined, f"{model.name}.{ort_tag}.latency.{label}")

                if run_ok:
                    npu_stats_accum.append(npu_stats)
                    cpu_pct = _parse_cpu_pct(proc.stderr)
                    if cpu_pct is not None:
                        cpu_pcts.append(cpu_pct)
                    mem = _parse_npu_memory_bytes(combined)
                    if mem is not None:
                        last_npu_mem = mem

                # Save last profiler for archival
                if profiler_path.exists() and save_dir:
                    dest = save_dir / f"{model.name}.ort_{'on' if use_ort else 'off'}.profiler.json"
                    shutil.copy2(profiler_path, dest)

                if save_dir:
                    _save_raw(save_dir, model.name, f"latency.{label}", use_ort, combined, npu_stats.raw_log)

        # Compute averages
        _lat_partial_note = ""
        if (len(total_ms_values) + len(fps_values)) < target:
            _lat_partial_note = f" (backfill exhausted after {attempt} attempts: {timeout_runs} timeout, {parse_fail_runs} unparsable)"
        if total_ms_values:
            total_ms = sum(total_ms_values) / len(total_ms_values)
            npu_task_ms = sum(npu_task_ms_values) / len(npu_task_ms_values) if npu_task_ms_values else None
            cpu_0_ms = sum(cpu_0_ms_values) / len(cpu_0_ms_values) if cpu_0_ms_values else None
            fps = 1000.0 / total_ms if total_ms > 0 else None
            status = "ok" if len(total_ms_values) >= target else "partial"
            reason = f"avg of {len(total_ms_values)}/{target} runs{_lat_partial_note}"
        elif fps_values:
            fps = sum(fps_values) / len(fps_values)
            total_ms = 1000.0 / fps if fps > 0 else None
            npu_task_ms = None
            cpu_0_ms = None
            status = "partial"
            reason = f"Profiler keys not found; FPS from stdout ({len(fps_values)}/{target} runs){_lat_partial_note}"
        else:
            return ModelResult(
                model=model.name, task=model.task, size=model.size,
                use_ort=use_ort, family="latency",
                status="error", reason="Could not parse metrics from any run",
            )

        npu_dict = _merge_npu_stats(npu_stats_accum, cfg.npu_core_ids).as_dict(cfg.npu_core_ids)
        if last_npu_mem is not None:
            npu_dict["npu_model_mem_bytes"] = last_npu_mem

        return ModelResult(
            model=model.name, task=model.task, size=model.size,
            use_ort=use_ort, family="latency",
            fps=fps, total_ms=total_ms,
            npu_task_ms=npu_task_ms, cpu_0_ms=cpu_0_ms,
            cpu_pct=sum(cpu_pcts) / len(cpu_pcts) if cpu_pcts else None,
            npu_stats=npu_dict,
            status=status, reason=reason,
        )
    finally:
        if work_dir_root is not None and work_dir_root.exists():
            with suppress(OSError):
                work_dir_root.rmdir()


def _save_raw(save_dir: Path, model_name: str, family: str, use_ort: bool, log: str, npu_log: str) -> None:
    """Save raw logs to disk."""
    save_dir.mkdir(parents=True, exist_ok=True)
    ort_tag = "ort_on" if use_ort else "ort_off"
    prefix = f"{model_name}.{family}.{ort_tag}"
    with open(save_dir / f"{prefix}.log", "w") as f:
        f.write(log)
    if npu_log:
        with open(save_dir / f"{prefix}.npu.log", "w") as f:
            f.write(npu_log)
