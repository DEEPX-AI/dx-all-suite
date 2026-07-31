"""Shared NPU stats merge utility.

Extracted from runner_pipeline.py so both runner_model.py and
runner_pipeline.py can share the same merge logic.
"""

from __future__ import annotations

from .npu_monitor import NpuStats


def merge_npu_stats(stats_list: list[NpuStats], core_ids: list[int]) -> NpuStats:
    """Average NPU stats across multiple runs."""
    if not stats_list:
        return NpuStats.empty(core_ids)

    merged = NpuStats()
    for cid in core_ids:
        avgs = [s.core_avg_pct.get(cid, 0.0) for s in stats_list if s.core_avg_pct]
        maxes = [s.core_max_pct.get(cid, 0.0) for s in stats_list if s.core_max_pct]
        merged.core_avg_pct[cid] = sum(avgs) / len(avgs) if avgs else 0.0
        merged.core_max_pct[cid] = max(maxes) if maxes else 0.0
    merged.mem_max_mib = max((s.mem_max_mib for s in stats_list), default=0.0)
    merged.sample_count = sum(s.sample_count for s in stats_list)
    # Temperature: min of mins, max of maxes across runs
    temp_mins = [s.temp_min_c for s in stats_list if s.temp_min_c is not None]
    temp_maxes = [s.temp_max_c for s in stats_list if s.temp_max_c is not None]
    merged.temp_min_c = min(temp_mins) if temp_mins else None
    merged.temp_max_c = max(temp_maxes) if temp_maxes else None
    # Clock: min of mins, max of maxes, avg of avgs per core
    clock_avg_by_core: dict[int, list[float]] = {cid: [] for cid in core_ids}
    clock_min_by_core: dict[int, list[float]] = {cid: [] for cid in core_ids}
    clock_max_by_core: dict[int, list[float]] = {cid: [] for cid in core_ids}
    for s in stats_list:
        for cid in core_ids:
            if cid in s.core_clock_mhz and s.core_clock_mhz[cid] > 0:
                clock_avg_by_core[cid].append(s.core_clock_mhz[cid])
            if cid in s.core_clock_min_mhz and s.core_clock_min_mhz[cid] > 0:
                clock_min_by_core[cid].append(s.core_clock_min_mhz[cid])
            if cid in s.core_clock_max_mhz and s.core_clock_max_mhz[cid] > 0:
                clock_max_by_core[cid].append(s.core_clock_max_mhz[cid])
    for cid in core_ids:
        if clock_avg_by_core[cid]:
            merged.core_clock_mhz[cid] = sum(clock_avg_by_core[cid]) / len(clock_avg_by_core[cid])
        if clock_min_by_core[cid]:
            merged.core_clock_min_mhz[cid] = min(clock_min_by_core[cid])
        if clock_max_by_core[cid]:
            merged.core_clock_max_mhz[cid] = max(clock_max_by_core[cid])
    return merged
