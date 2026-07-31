"""Environment fingerprinting – capture host, NPU, and tool versions.

Produces a dict that uniquely identifies the measurement environment
so results from different machines are traceable and comparable.
"""

from __future__ import annotations

import glob
import json
import os
import platform
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from . import __version__ as BENCHMARK_TOOL_VERSION
from .npu_catalog import classify_devices, format_badge, format_sku


def _normalize_version(raw: str) -> str:
    """Normalize a git-describe-style version to a clean semver string.

    Tools may report a build-stamped version such as
    ``v3.4.0+9ef3f4c-dirty`` (git ``describe`` with commit hash / dirty flag)
    instead of a clean ``v3.4.0``. Per semver, everything after ``+`` is build
    metadata and is irrelevant to precedence, so it is dropped; git-describe
    commit suffixes (``-<n>-g<hash>``) and the ``-dirty`` marker are stripped
    too. Genuine pre-release tags (``-rc.4``) are preserved. The full,
    unmodified ``dxrt-cli`` output is still kept in the fingerprint's ``raw``
    field, so a dirty build remains auditable. Empty / ``unknown`` unchanged.
    """
    if not raw:
        return raw
    v = raw.strip()
    if v.lower() == "unknown":
        return v
    v = v.split("+", 1)[0]                       # drop semver build metadata
    v = re.sub(r"-dirty$", "", v)                # drop dirty marker
    v = re.sub(r"-\d+-g[0-9a-f]+$", "", v)       # drop git-describe '-<n>-g<hash>'
    return v.strip()


def _run(cmd: list[str], default: str = "unknown") -> str:
    """Run a command and return stripped stdout, or *default* on failure."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or default
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return default


def _read_release_ver(start: Path) -> str | None:
    """Walk up from *start* until a ``release.ver`` file is found; return its
    stripped contents, or None if none exists up to the filesystem root."""
    p = Path(start).resolve()
    for d in [p, *p.parents]:
        f = d / "release.ver"
        if f.is_file():
            v = f.read_text().strip()
            if v:
                return v
    return None


def resolve_dx_all_suite_version(explicit: str | None, start: Path | None = None) -> str | None:
    """Resolve the dx-all-suite version: explicit flag wins, else walk up from
    *start* (default: package dir) for ``release.ver``, else None."""
    explicit = (explicit or "").strip()
    if explicit:
        return _normalize_version(explicit)
    if start is None:
        from .config import APP_DIR
        # Search for the SUITE-root release.ver ABOVE the dx-benchmark component, so
        # dx-benchmark's OWN release.ver (its tool version, e.g. v0.1.0) is never
        # mistaken for the measured dx-all-suite version. Layout:
        #   <suite-root>/dx-benchmark/benchmark  == APP_DIR
        #   APP_DIR.parent        == dx-benchmark  (has its own release.ver → skip)
        #   APP_DIR.parent.parent == suite root    (the release.ver we want)
        start = APP_DIR.parent.parent
    resolved = _read_release_ver(start)
    return _normalize_version(resolved) if resolved else resolved


def _tool_version(name: str) -> dict[str, Any]:
    """Return {'path': ..., 'version': ...} for a CLI tool."""
    path = shutil.which(name)
    if not path:
        return {"path": None, "version": None, "available": False}
    ver = "unknown"
    if name == "ffprobe":
        ver = _run([name, "-version"]).split("\n")[0]
    elif name in ("gst-launch-1.0", "gst-inspect-1.0"):
        ver = _run([name, "--version"]).split("\n")[0]
    elif name == "dxtop":
        # dxtop has no --version; extract from runtime header instead
        ver = _run([name, "--help"]).split("\n")[0]
    elif name == "run_model":
        # Extract only the first line (version string)
        ver = _run([name, "--help"]).split("\n")[0]
    return {"path": path, "version": ver, "available": True}


# Always required — every benchmark family (model / E2E / multi) needs these.
# `time` is GNU /usr/bin/time, used for CPU%/RSS in every run_model & gst run.
REQUIRED_TOOLS = ["run_model", "dxrt-cli", "gst-launch-1.0", "gst-inspect-1.0", "time"]
# Required only for the E2E / multi-stream (GStreamer pipeline) families.
E2E_REQUIRED_TOOLS = ["ffprobe"]
OPTIONAL_TOOLS = ["dxtop"]

# Actionable install hints surfaced next to a missing tool in preflight output.
_REMEDIATION = {
    "run_model": "DEEPX runtime — run: dx-runtime/install.sh --all",
    "dxrt-cli": "DEEPX runtime — run: dx-runtime/install.sh --all",
    "gst-launch-1.0": "GStreamer tools — sudo apt-get install -y gstreamer1.0-tools",
    "gst-inspect-1.0": "GStreamer tools — sudo apt-get install -y gstreamer1.0-tools",
    "time": "GNU time — sudo apt-get install -y time",
    "ffprobe": "ffmpeg — sudo apt-get install -y ffmpeg",
}


def _remediation(tool: str) -> str:
    """Return an install hint for a tool name, or '' when none is known."""
    for key, hint in _REMEDIATION.items():
        if key in tool:
            return hint
    return ""


def _repo_relative_path(p: str | Path) -> str:
    """Return a repo-relative path string (no username/absolute-path leak).

    Falls back to the bare filename when the target is outside the repo, so a
    user-supplied ``--video`` path never leaks a home directory into results.
    """
    from .config import APP_DIR

    path = Path(p)
    repo_root = APP_DIR.parent  # dx-benchmark/
    try:
        return str(path.resolve().relative_to(repo_root))
    except (ValueError, OSError):
        return path.name


def _get_dx_stream_version() -> str:
    """Get installed dxstream plugin version via gst-inspect-1.0."""
    if not shutil.which("gst-inspect-1.0"):
        return "unknown"
    raw = _run(["gst-inspect-1.0", "dxstream"])
    m = re.search(r"Version\s+(\S+)", raw)
    return m.group(1) if m else "unknown"


def _stamp_npu_products(info: dict, device_signals: list[tuple[str | None, str | None]]) -> None:
    """Classify per-device (board, memory) signals and stamp product fields."""
    modules = classify_devices(device_signals)
    info["modules"] = modules
    info["product"] = format_badge(modules)
    info["sku"] = format_sku(modules)


def collect_fingerprint() -> dict[str, Any]:
    """Collect full environment fingerprint."""
    uname = platform.uname()
    fp: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "benchmark_tool_version": BENCHMARK_TOOL_VERSION,
        "host": {
            "hostname": uname.node,
            "os": _get_os_pretty_name(),
            "kernel": uname.release,
            "arch": uname.machine,
            "cpu": _get_cpu_model(),
            "cpu_count": platform.os.cpu_count(),  # type: ignore[attr-defined]
            "ram_gb": _get_ram_gb(),
            "cpu_governors": _get_cpu_governors(),
        },
        "host_health": collect_host_health(),
        "npu": _get_npu_info(),
        "software": {
            "dx_stream": _get_dx_stream_version(),
        },
        "tools": {},
    }

    # Always-required tools
    missing = []
    for tool in REQUIRED_TOOLS:
        info = _tool_version(tool)
        fp["tools"][tool] = info
        if not info["available"]:
            missing.append(tool)

    # E2E-tier tools (record availability; gate only the E2E/multi families)
    for tool in E2E_REQUIRED_TOOLS:
        fp["tools"][tool] = _tool_version(tool)

    # Optional tools
    for tool in OPTIONAL_TOOLS:
        fp["tools"][tool] = _tool_version(tool)

    fp["missing_required"] = missing
    fp["missing_e2e"] = collect_e2e_missing()
    return fp


def collect_e2e_missing() -> list[str]:
    """Return E2E/multi-stream prerequisites that are absent.

    Beyond ``E2E_REQUIRED_TOOLS`` (CLIs on PATH) this also checks the GStreamer
    ``dxstream`` plugin and the task postprocess libraries — presence of
    ``gst-inspect-1.0`` alone does NOT imply the DEEPX plugin is installed.
    """
    from .config import POSTPROCESS_LIB_DIR

    missing: list[str] = []
    if _get_dx_stream_version() == "unknown":
        missing.append("dxstream (GStreamer plugin — gst-inspect-1.0 dxstream)")
    if not POSTPROCESS_LIB_DIR.exists() or not list(POSTPROCESS_LIB_DIR.glob("libpostprocess_yolo26*.so")):
        missing.append(f"postprocess libs ({POSTPROCESS_LIB_DIR}/libpostprocess_yolo26*.so)")
    for tool in E2E_REQUIRED_TOOLS:
        if not shutil.which(tool):
            missing.append(tool)
    return missing


def _get_os_pretty_name() -> str:
    """Get distro name from /etc/os-release (e.g. 'Ubuntu 24.04.2 LTS')."""
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return f"{platform.system()} {platform.release()}"


def _get_dxrt_version() -> str:
    """Get DXRT runtime version from dxrt-cli --version."""
    if not shutil.which("dxrt-cli"):
        return "unknown"
    ver = _run(["dxrt-cli", "--version"])
    if ver and ver != "unknown":
        first_line = ver.split("\n")[0].strip()
        # Strip "DXRT " prefix: "DXRT v3.2.0" -> "v3.2.0"
        if first_line.upper().startswith("DXRT "):
            first_line = first_line[5:].strip()
        return first_line
    return "unknown"


def _get_ram_gb() -> float:
    """Get total RAM in GB from /proc/meminfo."""
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return round(kb / 1024 / 1024, 1)
    except OSError:
        pass
    return 0.0


def _get_cpu_model() -> str:
    """Get CPU model name from lscpu."""
    if not shutil.which("lscpu"):
        return platform.processor() or "unknown"
    raw = _run(["lscpu"])
    for line in raw.split("\n"):
        if "Model name" in line:
            m = re.search(r":\s*(.+)", line)
            if m:
                return m.group(1).strip()
    return raw.split("\n")[0] if raw else "unknown"


CPU_SYSFS_BASE = "/sys/devices/system/cpu"


def _get_cpu_governors(cpu_base: str = CPU_SYSFS_BASE) -> dict[str, int]:
    """Summarize CPU frequency governors across cores → {governor: cpu_count}.

    Reads ``{cpu_base}/cpu*/cpufreq/scaling_governor``. Returns an empty dict when
    cpufreq is unavailable (no scaling driver / restricted sysfs). Recorded in the
    fingerprint so a slow or noisy run can be checked against the CPU power policy:
    a non-'performance' governor depresses and adds variance to host-bound metrics
    (latency, small-model throughput, E2E).
    """
    govs: dict[str, int] = {}
    for path in glob.glob(os.path.join(cpu_base, "cpu[0-9]*", "cpufreq", "scaling_governor")):
        try:
            with open(path) as f:
                g = f.read().strip()
        except OSError:
            continue
        if g:
            govs[g] = govs.get(g, 0) + 1
    return govs


def check_cpu_governor(fingerprint: dict) -> Optional[str]:
    """Return a neutral informational note about the CPU governor, else None.

    The governor is recorded in the fingerprint for reproducibility. We do NOT
    prescribe a specific governor — the benchmark measures whatever governor the
    host actually uses (that is the representative, as-deployed number). Empty/
    unknown governors return None (nothing to say); a uniform governor also
    returns None (no cross-core inconsistency worth flagging).
    """
    govs = (fingerprint.get("host") or {}).get("cpu_governors") or {}
    if not govs:
        return None
    summary = ", ".join(f"{g}×{n}" for g, n in sorted(govs.items()))
    return (f"CPU governor: {summary}. Recorded in the fingerprint for "
            f"reproducibility. No action needed — just keep the governor "
            f"consistent across runs you compare.")


# ── Host power / PCIe link health (G5) ─────────────────────────────────────

# `vcgencmd get_throttled` bit map (Raspberry Pi firmware): bits 0-3 report the
# current state, bits 16-19 whether the condition occurred since boot.
_THROTTLED_BITS = {
    0: "under_voltage_now",
    1: "freq_capped_now",
    2: "throttled_now",
    3: "soft_temp_limit_now",
    16: "under_voltage_occurred",
    17: "freq_capped_occurred",
    18: "throttled_occurred",
    19: "soft_temp_limit_occurred",
}


def _decode_throttled(raw: str) -> Optional[dict]:
    """Decode `vcgencmd get_throttled` output into named boolean flags."""
    m = re.search(r"throttled=0x([0-9a-fA-F]+)", raw or "")
    if not m:
        return None
    val = int(m.group(1), 16)
    return {name: bool(val >> bit & 1) for bit, name in _THROTTLED_BITS.items()}


def _parse_pmic_volts(raw: str, channel: str = "EXT5V_V") -> Optional[float]:
    """Parse one channel's voltage from `vcgencmd pmic_read_adc` output.

    Matches lines like ``EXT5V_V volt(24)=5.10370000V`` (RPi5 PMIC supply rail).
    """
    m = re.search(rf"{re.escape(channel)}\s+volt\([^)]*\)=([\d.]+)V", raw or "")
    return float(m.group(1)) if m else None


def _get_pcie_links() -> list[dict]:
    """LnkCap/LnkSta of NPU-looking PCI devices (DEEPX / accelerator class).

    Kernel-side view of the negotiated link, independent of dxrt-cli's report —
    lets a downgraded or retrained link be spotted after the fact.
    """
    if not shutil.which("lspci"):
        return []
    links: list[dict] = []
    for line in _run(["lspci", "-D"], default="").splitlines():
        if not re.search(r"deepx|accelerat", line, re.IGNORECASE):
            continue
        bdf = line.split()[0]
        # PCIe capability registers (LnkCap/LnkSta) need root; try passwordless
        # sudo first (same convention as incident diagnostics), fall back to bare.
        detail = _run(["sudo", "-n", "lspci", "-vv", "-s", bdf], default="")
        if "LnkSta" not in detail:
            detail = _run(["lspci", "-vv", "-s", bdf], default="")
        entry: dict[str, Any] = {"bdf": bdf, "device": line.strip()}
        for field in ("LnkCap", "LnkSta"):
            m = re.search(rf"{field}:\s*(.+)", detail)
            entry[field.lower()] = m.group(1).strip() if m else None
        links.append(entry)
    return links


def collect_host_health() -> dict[str, Any]:
    """Host power / PCIe link health snapshot (G5).

    Best-effort: every probe degrades to None/empty on non-RPi hosts or
    missing tools; never raises. Recorded at run start (``host_health``),
    run end (``host_health_end``), and in incident bundles.
    """
    health: dict[str, Any] = {
        "throttled": None,
        "throttled_flags": None,
        "pmic_ext5v_v": None,
        "pcie_links": [],
    }
    if shutil.which("vcgencmd"):
        raw = _run(["vcgencmd", "get_throttled"], default="")
        if "throttled=" in raw:
            health["throttled"] = raw.strip()
            health["throttled_flags"] = _decode_throttled(raw)
        health["pmic_ext5v_v"] = _parse_pmic_volts(
            _run(["vcgencmd", "pmic_read_adc"], default=""))
    health["pcie_links"] = _get_pcie_links()
    health["available"] = bool(
        health["throttled"] or health["pmic_ext5v_v"] is not None
        or health["pcie_links"])
    return health


def _get_npu_info() -> dict[str, Any]:
    """Parse NPU information from dxrt-cli -s output."""
    rt_raw = _get_dxrt_version()
    rt_clean = _normalize_version(rt_raw)
    info: dict[str, Any] = {
        "sku": "unknown",
        "rt_version": rt_clean,
        "driver": "unknown",
        "pcie_driver": "unknown",
        "firmware": "unknown",
        "memory": "unknown",
        "board": "unknown",
        "pcie": "unknown",
        "cores": [],
    }
    # Preserve the build-stamped string (e.g. "v3.4.0+9ef3f4c-dirty") only when
    # normalization actually changed it, so a dirty/non-release runtime stays
    # visible for auditing without cluttering clean-release fingerprints.
    if rt_raw != rt_clean:
        info["rt_version_raw"] = rt_raw
    if not shutil.which("dxrt-cli"):
        return info

    raw = _run(["dxrt-cli", "-s"])
    if raw == "unknown":
        return info
    info["raw"] = raw

    # Parse structured fields from dxrt-cli -s output
    device_count = 0
    device_signals: list[tuple[str | None, str | None]] = []
    current_board: str | None = None
    current_memory: str | None = None
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("* Device"):
            if device_count > 0:
                device_signals.append((current_board, current_memory))
            current_board = None
            current_memory = None
            device_count += 1
        elif "Board" in line and ":" in line and "Chip" not in line:
            m = re.search(r":\s*(.+)", line)
            if m:
                val = m.group(1).strip()
                current_board = val.split(",")[0].strip()  # e.g. "M.2" / "H1"
                info["board"] = val
        elif "RT Driver version" in line:
            m = re.search(r":\s*(.+)", line)
            if m:
                info["driver"] = m.group(1).strip()
        elif "PCIe Driver version" in line:
            m = re.search(r":\s*(.+)", line)
            if m:
                info["pcie_driver"] = m.group(1).strip()
        elif "FW version" in line:
            m = re.search(r":\s*(.+)", line)
            if m:
                info["firmware"] = m.group(1).strip()
        elif "Memory" in line and ":" in line:
            m = re.search(r":\s*(.+)", line)
            if m:
                current_memory = m.group(1).strip()
                info["memory"] = current_memory
        elif "PCIe" in line and "Gen" in line:
            m = re.search(r":\s*(.+)", line)
            if m:
                info["pcie"] = m.group(1).strip()
        elif line.startswith("NPU"):
            info["cores"].append(line)
    if device_count > 0:
        device_signals.append((current_board, current_memory))

    info["device_count"] = device_count
    _stamp_npu_products(info, device_signals)

    # Extract max NPU clock from core info
    clock_mhz: int | None = None
    for core_line in info["cores"]:
        cm = re.search(r"clock\s+(\d+)\s*MHz", core_line)
        if cm:
            val = int(cm.group(1))
            if clock_mhz is None or val > clock_mhz:
                clock_mhz = val
    info["clock_mhz"] = clock_mhz

    return info


def check_preflight(fingerprint: dict) -> tuple[bool, list[str]]:
    """Validate that all always-required tools are present.

    Returns (ok, list_of_error_messages). Each message carries an install hint.
    """
    errors = []
    for tool in fingerprint.get("missing_required", []):
        hint = _remediation(tool)
        errors.append(f"Required tool not found: {tool}" + (f"  → {hint}" if hint else ""))
    return len(errors) == 0, errors


def check_e2e_readiness(fingerprint: dict) -> tuple[bool, list[str]]:
    """Validate E2E/multi-stream prerequisites (dxstream plugin, postprocess libs, ffprobe).

    Returns (ok, list_of_warning_messages). Model-only runs do not need these,
    so this is separate from ``check_preflight`` and only gates E2E/multi families.
    """
    warnings = []
    for item in fingerprint.get("missing_e2e", []):
        hint = _remediation(item)
        warnings.append(f"E2E prerequisite missing: {item}" + (f"  → {hint}" if hint else ""))
    return len(warnings) == 0, warnings


def get_video_info(video_path: str | Path) -> dict[str, Any]:
    """Get video metadata using ffprobe."""
    info: dict[str, Any] = {
        "path": _repo_relative_path(video_path),
        "filename": Path(video_path).name,
    }
    if not shutil.which("ffprobe") or not Path(video_path).exists():
        return info
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_streams", "-show_format", str(video_path)],
            capture_output=True, text=True, timeout=10,
        )
        data = json.loads(r.stdout)
        for s in data.get("streams", []):
            if s.get("codec_type") == "video":
                info["codec"] = s.get("codec_name", "unknown")
                info["width"] = s.get("width", 0)
                info["height"] = s.get("height", 0)
                info["pix_fmt"] = s.get("pix_fmt", "unknown")
                fps_str = s.get("r_frame_rate", "0/1")
                try:
                    num, den = fps_str.split("/")
                    info["fps"] = round(int(num) / int(den), 1)
                except (ValueError, ZeroDivisionError):
                    info["fps"] = fps_str
                info["nb_frames"] = int(s.get("nb_frames", 0))
                info["duration_sec"] = float(s.get("duration", 0))
                break
        fmt = data.get("format", {})
        info["format"] = fmt.get("format_long_name", "unknown")
        bitrate = fmt.get("bit_rate")
        if bitrate:
            info["bitrate_mbps"] = round(int(bitrate) / 1_000_000, 2)
    except (subprocess.TimeoutExpired, OSError, ValueError):
        pass
    return info


def save_fingerprint(fingerprint: dict, output_dir: Path) -> Path:
    """Save fingerprint as JSON and return the path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "environment.json"
    with open(path, "w") as f:
        json.dump(fingerprint, f, indent=2)
    return path


def _strip_ansi(text: str) -> str:
    """Remove ANSI/VT100 escape sequences from *text*."""
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", text)


def collect_model_metadata(model_path: str | Path) -> dict[str, Any]:
    """Run ``parse_model -m <model_path>`` and extract key metadata.

    Returns a dict with ``format_version``, ``dxcom_version``, and
    ``total_memory_mb`` (or empty dict on failure).
    """
    raw = _run(["parse_model", "-m", str(model_path)], default="")
    if not raw:
        return {}

    # parse_model always emits ANSI colour codes regardless of TTY; strip them
    # before applying regex patterns so captured values are clean strings.
    raw = _strip_ansi(raw)

    result: dict[str, Any] = {}

    # .dxnn Format Version
    m = re.search(r"\.dxnn Format Version\s*:\s*(\S+)", raw)
    if m:
        result["format_version"] = m.group(1)

    # DX-COM Version
    m = re.search(r"DX-COM Version\s*:\s*(\S+)", raw)
    if m:
        result["dxcom_version"] = m.group(1)

    # Total memory MB from "102.49 MB (107,468,288 bytes)"
    m = re.search(r"Total\s*:\s*[\d.]+ \S+\s*\(([\d,]+)\s*bytes\)", raw)
    if m:
        result["total_memory_mb"] = round(int(m.group(1).replace(",", "")) / (1024 * 1024), 2)

    return result
