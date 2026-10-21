"""Post-run audit: did every measured row keep its NPU telemetry?

dxtop is the only source of per-cell NPU clock, utilization and memory. If it
cannot start the run still succeeds and `npu_throttled` reads False, which looks
like "not throttled". This audit turns that into a warning at the end of the run.
"""
from __future__ import annotations

# Fields that dxtop (not the benchmark process) is responsible for.
NPU_TELEMETRY_FIELDS = ("npu_clock_mhz_min", "npu_clock_mhz_max", "npu_total_avg_pct")

_HINT = ("dxtop produced no data: check that dxtop starts (a detached run needs TERM set) "
         "and re-run -- throttling is invisible without NPU clock samples")


def _measured(row: dict) -> bool:
    return (row.get("status") or "ok") == "ok"


def audit_results(model_results: list[dict], pipeline_results: list[dict],
                  multi_results: list[dict]) -> list[str]:
    """Return one warning per result set whose measured rows lack NPU telemetry."""
    warnings: list[str] = []
    for label, rows in (("model_results", model_results),
                        ("pipeline_results", pipeline_results),
                        ("multi_stream_results", multi_results)):
        measured = [r for r in rows if _measured(r)]
        bad = [r for r in measured
               if any(r.get(f) is None for f in NPU_TELEMETRY_FIELDS)]
        if bad:
            warnings.append(
                f"{label}: {len(bad)}/{len(measured)} measured row(s) lack NPU "
                f"clock/utilization data ({', '.join(NPU_TELEMETRY_FIELDS)}). {_HINT}")
    return warnings
