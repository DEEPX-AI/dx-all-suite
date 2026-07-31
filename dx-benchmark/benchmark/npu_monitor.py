"""NPU monitoring via dxtop.

Spawns dxtop in a PTY via `script`, collects samples during a
benchmark run, and parses per-core utilization and memory stats.
"""

from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from typing import Optional

# ANSI escape + bracket-only sequences left by the `script` PTY around dxtop output.
_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\[\??[0-9;]*[A-Za-z]")

# Nominal (rated) NPU clock in MHz. DX-M1 / M1M / H1 all run at 1000 MHz at full
# speed; a min clock below this during a run means DVFS throttled it down.
NOMINAL_CLOCK_MHZ = 1000


@dataclass
class NpuStats:
    """Parsed NPU utilization statistics."""
    core_avg_pct: dict[int, float] = field(default_factory=dict)  # core_id → avg %
    core_max_pct: dict[int, float] = field(default_factory=dict)  # core_id → max %
    core_clock_mhz: dict[int, float] = field(default_factory=dict)  # core_id → avg clock MHz
    core_clock_min_mhz: dict[int, float] = field(default_factory=dict)  # core_id → min clock MHz
    core_clock_max_mhz: dict[int, float] = field(default_factory=dict)  # core_id → max clock MHz
    mem_max_mib: float = 0.0
    temp_min_c: Optional[float] = None   # NPU temperature min °C (across time)
    temp_max_c: Optional[float] = None   # NPU temperature max °C (across time)
    sample_count: int = 0
    raw_log: str = ""

    def as_dict(self, core_ids: list[int],
                nominal_clock_mhz: float = NOMINAL_CLOCK_MHZ) -> dict:
        """Flat dict with explicit core columns."""
        d: dict = {}
        for cid in core_ids:
            d[f"npu_core{cid}_avg_pct"] = round(self.core_avg_pct.get(cid, 0.0), 1)
            d[f"npu_core{cid}_max_pct"] = round(self.core_max_pct.get(cid, 0.0), 1)
        total_avg = sum(self.core_avg_pct.values()) / max(len(self.core_avg_pct), 1)
        d["npu_total_avg_pct"] = round(total_avg, 1)
        total_max = max(self.core_max_pct.values()) if self.core_max_pct else 0.0
        d["npu_total_max_pct"] = round(total_max, 1)
        d["npu_mem_max_mib"] = round(self.mem_max_mib, 1)
        d["npu_temp_min_c"] = round(self.temp_min_c, 1) if self.temp_min_c is not None else None
        d["npu_temp_max_c"] = round(self.temp_max_c, 1) if self.temp_max_c is not None else None
        d["npu_samples"] = self.sample_count
        # NPU clock statistics (time-axis min/max across all cores)
        if self.core_clock_min_mhz and self.core_clock_max_mhz:
            all_mins = list(self.core_clock_min_mhz.values())
            all_maxes = list(self.core_clock_max_mhz.values())
            clock_min = round(min(all_mins), 0)
            d["npu_clock_mhz_min"] = clock_min
            d["npu_clock_mhz_max"] = round(max(all_maxes), 0)
            # Throttled iff the clock dropped below the nominal rated clock at
            # any point — referenced to nominal, not the run's own peak, so a
            # run pinned at a low clock is still flagged. Matches the min-clock
            # value reported above (and the dashboard's clock<nominal badge).
            d["npu_throttled"] = clock_min < nominal_clock_mhz
        else:
            d["npu_clock_mhz_min"] = None
            d["npu_clock_mhz_max"] = None
            d["npu_throttled"] = None
        return d

    @staticmethod
    def empty(core_ids: list[int]) -> "NpuStats":
        """Return an empty stats object (when dxtop is unavailable)."""
        s = NpuStats()
        for cid in core_ids:
            s.core_avg_pct[cid] = 0.0
            s.core_max_pct[cid] = 0.0
            s.core_clock_mhz[cid] = 0.0
            s.core_clock_min_mhz[cid] = 0.0
            s.core_clock_max_mhz[cid] = 0.0
        return s


def parse_npu_log_temp_clock(raw: str) -> dict:
    """Parse raw dxtop log text and return temp/clock min/max.

    Handles both `strings`-processed text and raw `script` PTY output
    (with ANSI escapes and binary control characters).

    Returns dict with keys:
        npu_temp_min_c, npu_temp_max_c,
        npu_clock_mhz_min, npu_clock_mhz_max
    Values are float or None when no data found.
    """
    # Strip ANSI escape codes and bracket-only sequences left by `script` PTY
    clean = _ANSI_RE.sub("", raw)
    # Remove remaining control characters (except newline/tab)
    clean = re.sub(r"[\x00-\x08\x0e-\x1f\x7f]", "", clean)
    clean = re.sub(r"\s+", " ", clean)

    temps = [float(m.group(1))
             for m in re.finditer(r"[Tt]emp(?:erature)?[:\s]+([\d.]+)\s*[°'`]?[Cc]?\b", clean)]
    clocks = [float(m.group(1))
              for m in re.finditer(r"(\d+)\s*MHz", clean)]

    return {
        "npu_temp_min_c": min(temps) if temps else None,
        "npu_temp_max_c": max(temps) if temps else None,
        "npu_clock_mhz_min": min(clocks) if clocks else None,
        "npu_clock_mhz_max": max(clocks) if clocks else None,
    }


def _read_dxrt_cli_status() -> Optional[str]:
    """Run `dxrt-cli -s` once and return the combined output, or None."""
    if not shutil.which("dxrt-cli"):
        return None
    try:
        result = subprocess.run(
            ["dxrt-cli", "-s"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout + result.stderr
    except (subprocess.TimeoutExpired, OSError):
        return None


def read_npu_temp_c() -> Optional[float]:
    """Read NPU temperature from `dxrt-cli -s` output.

    Parses lines like: 'NPU 0: voltage 750 mV, clock 1000 MHz, temperature 42\'C'
    Returns the maximum temperature across all NPU cores, or None if unavailable.
    """
    output = _read_dxrt_cli_status()
    if output is None:
        return None
    temps = re.findall(
        r"temperature\s+(\d+(?:\.\d+)?)'?[Cc]",
        output,
    )
    if temps:
        return max(float(t) for t in temps)
    return None


def read_npu_clock_mhz() -> Optional[float]:
    """Read NPU clock frequency from `dxrt-cli -s` output.

    Parses lines like: 'NPU 0: voltage 750 mV, clock 1000 MHz, temperature 42\'C'
    Returns the average clock across all NPU cores, or None if unavailable.
    """
    output = _read_dxrt_cli_status()
    if output is None:
        return None
    clocks = re.findall(
        r"clock\s+(\d+(?:\.\d+)?)\s*MHz",
        output,
    )
    if clocks:
        vals = [float(c) for c in clocks]
        return sum(vals) / len(vals)
    return None


class NpuMonitor:
    """Manages a dxtop background process and parses its output."""

    def __init__(self, core_ids: list[int], warmup_sec: float = 0.3, drain_sec: float = 0.2):
        self.core_ids = core_ids
        self.warmup_sec = warmup_sec
        self.drain_sec = drain_sec
        self._proc: Optional[subprocess.Popen] = None
        self._log_path: Optional[str] = None
        self._available = bool(shutil.which("dxtop") and shutil.which("script"))

    @property
    def available(self) -> bool:
        return self._available

    def start(self) -> None:
        """Start dxtop in background via script(PTY)."""
        if not self._available:
            return
        fd, self._log_path = tempfile.mkstemp(suffix=".dxtop.log")
        os.close(fd)
        # Force a large PTY size so dxtop renders all rows (Core info, etc.).
        # Without this, the PTY may default to very few rows and dxtop
        # truncates output, losing utilization data.
        self._proc = subprocess.Popen(
            ["script", "-q", "-f", "-c",
             "stty rows 50 cols 200 2>/dev/null; exec dxtop",
             self._log_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid,
        )
        time.sleep(self.warmup_sec)

    def stop(self) -> NpuStats:
        """Stop dxtop and parse collected samples."""
        if not self._available or self._proc is None:
            return NpuStats.empty(self.core_ids)

        time.sleep(self.drain_sec)

        # Terminate the process group
        try:
            os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)
        except (ProcessLookupError, OSError):
            pass
        try:
            self._proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self._proc.pid), signal.SIGKILL)
            except (ProcessLookupError, OSError):
                pass
            self._proc.wait(timeout=3)

        stats = self._parse_log(self._log_path)
        # If dxtop log didn't contain temperature, fall back to dxrt-cli -s
        if stats.temp_max_c is None:
            fallback_temp = read_npu_temp_c()
            if fallback_temp is not None:
                stats.temp_min_c = fallback_temp
                stats.temp_max_c = fallback_temp
        self._proc = None
        return stats

    def _parse_log(self, log_path: str | None) -> NpuStats:
        """Parse dxtop log using strings to strip binary/ANSI."""
        if not log_path or not os.path.exists(log_path):
            return NpuStats.empty(self.core_ids)

        try:
            result = subprocess.run(
                ["strings", log_path],
                capture_output=True, text=True, timeout=10,
            )
            raw = result.stdout
        except (subprocess.TimeoutExpired, OSError):
            return NpuStats.empty(self.core_ids)

        # Strip ANSI escape sequences before parsing
        clean = _ANSI_RE.sub("", raw)
        # Merge into a single stream of tokens by collapsing whitespace
        clean = re.sub(r"\s+", " ", clean)

        stats = NpuStats(raw_log=raw)
        mem_samples: list[float] = []

        # Collect per-core util and clock entries in order of appearance
        core_util_pairs: list[tuple[int, float]] = []
        core_clock_pairs: list[tuple[int, float]] = []
        for m in re.finditer(r"Core\s*:\s*(\d+)\s+.*?Util:\s*([\d.]+)%", clean):
            core_util_pairs.append((int(m.group(1)), float(m.group(2))))
        for m in re.finditer(r"Core\s*:\s*(\d+)\s+.*?Clock:\s*(\d+)\s*MHz", clean):
            core_clock_pairs.append((int(m.group(1)), float(m.group(2))))

        temp_samples: list[float] = []
        for m in re.finditer(r"[Tt]emp(?:erature)?[:\s]+([\d.]+)\s*[°'`]?[Cc]\b", clean):
            temp_samples.append(float(m.group(1)))

        for m in re.finditer(r"([\d.]+)\s*MiB\s*/\s*[\d.]+\s*GiB", clean):
            mem_samples.append(float(m.group(1)))

        # Group into frames (each frame has one entry per core, in ascending order).
        # dxtop renders cores 0,1,2 per refresh; a new frame starts when
        # the core id resets (i.e. is <= the previous core id).
        frames: list[dict[int, float]] = []
        current_frame: dict[int, float] = {}
        last_cid = -1
        for cid, util in core_util_pairs:
            if cid <= last_cid and current_frame:
                frames.append(current_frame)
                current_frame = {}
            if cid in self.core_ids:
                current_frame[cid] = util
            last_cid = cid
        if current_frame:
            frames.append(current_frame)

        # Group clock values into frames (same logic as util frames)
        clock_frames: list[dict[int, float]] = []
        current_clock_frame: dict[int, float] = {}
        last_cid = -1
        for cid, clock in core_clock_pairs:
            if cid <= last_cid and current_clock_frame:
                clock_frames.append(current_clock_frame)
                current_clock_frame = {}
            if cid in self.core_ids:
                current_clock_frame[cid] = clock
            last_cid = cid
        if current_clock_frame:
            clock_frames.append(current_clock_frame)

        # Use all frames — warmup_sec handles pre-workload idle samples.
        # (Previously filtered 0% frames, which inflated NPU Avg% when CPU-bound.)
        active_frames = frames

        # Build per-core statistics from valid frames
        core_samples: dict[int, list[float]] = {cid: [] for cid in self.core_ids}
        for frame in active_frames:
            for cid in self.core_ids:
                if cid in frame:
                    core_samples[cid].append(frame[cid])

        for cid, samples in core_samples.items():
            if samples:
                stats.core_avg_pct[cid] = sum(samples) / len(samples)
                stats.core_max_pct[cid] = max(samples)
                stats.sample_count = max(stats.sample_count, len(samples))
            else:
                stats.core_avg_pct[cid] = 0.0
                stats.core_max_pct[cid] = 0.0

        # Build per-core clock statistics from clock frames
        core_clock_samples: dict[int, list[float]] = {cid: [] for cid in self.core_ids}
        for frame in clock_frames:
            for cid in self.core_ids:
                if cid in frame:
                    core_clock_samples[cid].append(frame[cid])
        for cid, samples in core_clock_samples.items():
            if samples:
                stats.core_clock_mhz[cid] = sum(samples) / len(samples)
                stats.core_clock_min_mhz[cid] = min(samples)
                stats.core_clock_max_mhz[cid] = max(samples)

        stats.mem_max_mib = max(mem_samples) if mem_samples else 0.0
        stats.temp_min_c = min(temp_samples) if temp_samples else None
        stats.temp_max_c = max(temp_samples) if temp_samples else None

        # Cleanup
        try:
            os.unlink(log_path)
        except OSError:
            pass

        return stats
