"""Shared hardware monitoring — cache-backed NPU plus local host metrics."""
import copy
import os, sys, re, json, time, subprocess, platform, threading, math, shutil
from pathlib import Path

_DS = None
_dx_ok = False
_NPU_STATS_BIN = Path("/dev/null")
_APP_ROOT = Path(".")
_TELEMETRY = None
_TELEMETRY_EPOCH = 0
_TELEMETRY_ACTIVE = False
_EXPLICIT_MOCK = False
_hw_cache = {"d": None, "t": 0.0}
_hw_lock = threading.Lock()
_prev_cpu = None

def init_hw(
    ds=None,
    dx_ok=False,
    npu_stats_bin=None,
    app_root=None,
    telemetry=None,
    explicit_mock=False,
):
    """Initialize cache-backed Monitor telemetry and safe legacy test support.

    ``ds`` is accepted only for pre-existing unit-test and non-Monitor callers.
    It is never constructed or imported by this module; Monitor passes a
    ``TelemetrySupervisor`` through ``telemetry`` instead.
    """
    global _DS, _dx_ok, _NPU_STATS_BIN, _APP_ROOT, _TELEMETRY, _TELEMETRY_EPOCH, _TELEMETRY_ACTIVE, _EXPLICIT_MOCK
    with _hw_lock:
        _DS = ds
        _dx_ok = dx_ok
        _TELEMETRY = telemetry
        _TELEMETRY_EPOCH += 1
        _TELEMETRY_ACTIVE = telemetry is not None
        _EXPLICIT_MOCK = bool(explicit_mock)
        if npu_stats_bin:
            _NPU_STATS_BIN = Path(npu_stats_bin)
        if app_root:
            _APP_ROOT = Path(app_root)
        _hw_cache.update({"d": None, "t": 0.0})


def detach_telemetry_if(telemetry):
    """Detach ``telemetry`` only when it remains the active supervisor.

    The identity check keeps a newly bound supervisor intact when an older
    supervisor is stopping.  A successful detach also disables the legacy and
    explicit-mock paths so subsequent hardware reads are unavailable rather
    than querying a stopped worker or fabricating NPU metrics.
    """
    global _DS, _dx_ok, _TELEMETRY, _TELEMETRY_EPOCH, _TELEMETRY_ACTIVE, _EXPLICIT_MOCK
    with _hw_lock:
        if _TELEMETRY is not telemetry:
            return False
        _DS = None
        _dx_ok = False
        _TELEMETRY = None
        _TELEMETRY_EPOCH += 1
        _TELEMETRY_ACTIVE = False
        _EXPLICIT_MOCK = False
        _hw_cache.update({"d": None, "t": 0.0, "e": _TELEMETRY_EPOCH})
        return True


def invalidate_telemetry_if(telemetry):
    """Invalidate one active telemetry binding without detaching it.

    Shutdown uses this before a potentially blocking ``stop()`` call.  The
    identity check prevents an older shutdown from invalidating a replacement
    supervisor that bound concurrently.
    """
    global _TELEMETRY_EPOCH, _TELEMETRY_ACTIVE
    with _hw_lock:
        if _TELEMETRY is not telemetry:
            return False
        _TELEMETRY_EPOCH += 1
        _TELEMETRY_ACTIVE = False
        _hw_cache.update({"d": None, "t": 0.0, "e": _TELEMETRY_EPOCH})
        return True

def _read_cpu_per_core():
    """Read per-core CPU utilization from /proc/stat. Returns list of percentages."""
    global _prev_cpu
    try:
        lines = open("/proc/stat").readlines()
        cur = {}
        for line in lines:
            if line.startswith("cpu") and not line.startswith("cpu "):
                parts = line.split()
                name = parts[0]
                vals = list(map(int, parts[1:8]))
                total = sum(vals)
                idle = vals[3] + vals[4]
                cur[name] = (total, idle)
        if _prev_cpu is None:
            _prev_cpu = cur
            return []
        result = []
        for name in sorted(cur.keys()):
            if name in _prev_cpu:
                dt = cur[name][0] - _prev_cpu[name][0]
                di = cur[name][1] - _prev_cpu[name][1]
                pct = round((1.0 - di / dt) * 100, 1) if dt > 0 else 0.0
                result.append(max(0.0, pct))
        _prev_cpu = cur
        return result
    except Exception:
        return []

_DXRT_INVALID_TEMPERATURE = -32768
_DEVICE_INFO_FIELDS = (
    "firmware_version", "device_type", "device_variant", "board_type",
    "memory_type", "memory_size_bytes", "memory_freq_mhz",
    "ddr_status", "ddr_sbe_cnt", "ddr_dbe_cnt",
)

def _mock_npu():
    t = time.time()
    return [{"id": i, "device_id": i, "cores": 1, "mock": True,
        "temperatures": [38 + 5 * math.sin(t/10+i)],
        "voltages_mV": [750 + 20 * math.sin(t/7+i)],
        "clocks_MHz": [1000 + 50 * math.sin(t/5+i)],
        "temp_avg": 38 + 5 * math.sin(t/10+i),
        "voltage_avg": 750 + 20 * math.sin(t/7+i),
        "clock_avg": 1000 + 50 * math.sin(t/5+i),
        "power_est_mW": 375 + 25 * math.sin(t/8+i),
        "dram_used_mb": int(256 + 128 * math.sin(t/12+i)),
        "dram_total_mb": 4096,
        "dram_pct": round((256 + 128 * math.sin(t/12+i)) / 4096 * 100, 1),
        "utilization": [int(30 + 20 * math.sin(t/3+i+j*0.5)) for j in range(1)]
    } for i in range(1)]

def _telemetry_cache(telemetry=None):
    """Read a bounded, defensive cache snapshot without native runtime access."""
    unavailable = {
        "available": False,
        "source_mode": "unavailable",
        "npus": [],
        "diagnostics": [],
    }
    if telemetry is None:
        with _hw_lock:
            telemetry = _TELEMETRY
    if telemetry is None:
        unavailable["diagnostics"] = ["Telemetry supervisor is not initialized"]
        return unavailable
    try:
        snapshot = telemetry.snapshot()
    except Exception as error:
        unavailable["error"] = "Telemetry snapshot failed: {0}".format(error)
        return unavailable
    if not isinstance(snapshot, dict):
        unavailable["error"] = "Telemetry snapshot is invalid"
        return unavailable

    mode = snapshot.get("source_mode", "unavailable")
    if mode not in ("real", "stale", "unavailable"):
        mode = "unavailable"
    if mode == "unavailable":
        available = False
        npus = []
    else:
        available = bool(snapshot.get("available", False))
        npus = snapshot.get("npus", [])
    diagnostics = snapshot.get("diagnostics", [])
    cache = {
        "available": available,
        "source_mode": mode,
        "npus": copy.deepcopy(npus) if isinstance(npus, list) else [],
        "diagnostics": copy.deepcopy(diagnostics) if isinstance(diagnostics, list) else [],
    }
    if snapshot.get("error") is not None:
        cache["error"] = str(snapshot["error"])
    return cache


def _legacy_npus():
    """Return supplied status-object data for legacy tests without SDK imports."""
    npus = []
    if not (_dx_ok and _DS):
        return npus
    try:
        count = max(0, int(_DS.get_device_count()))
        for did in range(count):
            dev = _DS.get_current_status(did)
            temperatures, voltages, clocks, utilization = [], [], [], []
            for channel in range(4):
                try:
                    temperature = dev.get_temperature(channel)
                    if temperature == _DXRT_INVALID_TEMPERATURE:
                        break
                    temperatures.append(temperature)
                    voltages.append(dev.get_npu_voltage(channel))
                    clocks.append(dev.get_npu_clock(channel))
                    try:
                        value = dev.get_core_utilization(channel)
                        utilization.append(
                            round(float(value), 1)
                            if value is not None and value >= 0 else 0.0
                        )
                    except Exception:
                        pass
                except Exception:
                    break
            dram_used = dram_total = -1
            try:
                used, free = int(dev.get_memory_used()), int(dev.get_memory_free())
                if used >= 0 and free >= 0:
                    dram_used, dram_total = used, used + free
            except Exception:
                pass
            entry = {
                "id": did,
                "device_id": dev.get_id() if hasattr(dev, "get_id") else did,
                "cores": len(temperatures),
                "temperatures": temperatures,
                "voltages_mV": voltages,
                "clocks_MHz": clocks,
                "temp_avg": sum(temperatures) / len(temperatures) if temperatures else 0,
                "voltage_avg": sum(voltages) / len(voltages) if voltages else 0,
                "clock_avg": sum(clocks) / len(clocks) if clocks else 0,
                "power_est_mW": (sum(voltages) / len(voltages)) * 0.5 if voltages else 0,
                "dram_used_mb": round(dram_used / 1048576, 1) if dram_used >= 0 else -1,
                "dram_total_mb": round(dram_total / 1048576, 1) if dram_total > 0 else -1,
                "dram_pct": round(100.0 * dram_used / dram_total, 1) if dram_total > 0 else -1,
                "utilization": utilization,
            }
            if _NPU_STATS_BIN.exists():
                try:
                    raw = subprocess.check_output(
                        [str(_NPU_STATS_BIN), str(did), str(len(temperatures))],
                        timeout=2,
                        stderr=subprocess.DEVNULL,
                    )
                    stats = json.loads(raw)
                    for field in _DEVICE_INFO_FIELDS:
                        if field in stats:
                            entry[field] = stats[field]
                except Exception:
                    pass
            npus.append(entry)
    except Exception:
        return []
    return npus


def _add_host_metrics(data):
    """Populate local host metrics independently of NPU telemetry state."""
    try:
        m = open("/proc/meminfo").read()
        tot = int(re.search(r'MemTotal:\s+(\d+)', m).group(1))
        av = int(re.search(r'MemAvailable:\s+(\d+)', m).group(1))
        data.update({"mem_total_mb": tot//1024, "mem_used_mb": (tot-av)//1024,
                     "mem_pct": round((tot-av)/tot*100, 1)})
        st = re.search(r'SwapTotal:\s+(\d+)', m)
        sf = re.search(r'SwapFree:\s+(\d+)', m)
        if st and sf:
            swap_total = int(st.group(1))
            swap_free = int(sf.group(1))
            swap_used = swap_total - swap_free
            data.update({"swap_total_mb": swap_total // 1024,
                         "swap_used_mb": swap_used // 1024,
                         "swap_pct": round(swap_used / swap_total * 100, 1) if swap_total > 0 else 0.0})
        else:
            data.update({"swap_total_mb": 0, "swap_used_mb": 0, "swap_pct": 0.0})
    except Exception:
        data.update({"mem_total_mb": 0, "mem_used_mb": 0, "mem_pct": 0,
                     "swap_total_mb": 0, "swap_used_mb": 0, "swap_pct": 0.0})
    try:
        data["cpu_load"] = float(open("/proc/loadavg").read().split()[0])
    except Exception:
        data["cpu_load"] = 0.0
    data["cpu_cores_pct"] = _read_cpu_per_core()
    try:
        du = shutil.disk_usage('/')
        data.update({"disk_total_gb": round(du.total/1e9, 1),
                     "disk_used_gb": round(du.used/1e9, 1),
                     "disk_pct": round(du.used/du.total*100, 1)})
    except Exception:
        data.update({"disk_total_gb": 0, "disk_used_gb": 0, "disk_pct": 0})


def _refresh_after_telemetry_rebind(data):
    """Refresh one completed host snapshot against the current binding once.

    This runs only after the binding captured by ``get_hw()`` changed during
    host probes.  Snapshot reads run outside the lifecycle lock because a
    supervisor may acquire that lock while serving its cache.  The captured
    binding is revalidated before its result can update the hardware cache.
    """
    with _hw_lock:
        telemetry = _TELEMETRY
        telemetry_epoch = _TELEMETRY_EPOCH
        telemetry_active = _TELEMETRY_ACTIVE
        explicit_mock = _EXPLICIT_MOCK
    data["ts"] = time.time()
    cache = (
        _telemetry_cache(telemetry)
        if telemetry is not None and telemetry_active else None
    )

    with _hw_lock:
        telemetry_is_current = (
            _TELEMETRY is telemetry
            and _TELEMETRY_EPOCH == telemetry_epoch
            and _TELEMETRY_ACTIVE == telemetry_active
        )
        if not telemetry_is_current:
            data.update({
                "available": False,
                "source_mode": "unavailable",
                "npus": [],
                "count": 0,
                "mock": False,
                "telemetry": {
                    "available": False,
                    "source_mode": "unavailable",
                    "diagnostics": [
                        "Telemetry supervisor changed during refresh"
                    ],
                },
            })
            return copy.deepcopy(data)

        if cache is None:
            diagnostics = [
                "Telemetry supervisor is not initialized"
                if telemetry is None else "Telemetry supervisor is stopping"
            ]
            data.update({
                "available": False,
                "source_mode": "unavailable",
                "npus": [],
                "count": 0,
                "mock": False,
                "telemetry": {
                    "available": False,
                    "source_mode": "unavailable",
                    "diagnostics": diagnostics,
                },
            })
            if telemetry is None and explicit_mock:
                data["npus"] = _mock_npu()
                data["count"] = len(data["npus"])
                data["mock"] = True
                data["source_mode"] = "mock"
            if telemetry is None:
                _hw_cache.update({
                    "d": copy.deepcopy(data),
                    "t": data["ts"],
                    "e": telemetry_epoch,
                })
            return copy.deepcopy(data)

        data.update({
            "available": cache["available"],
            "source_mode": cache["source_mode"],
            "npus": cache["npus"] if (
                cache["available"] or cache["source_mode"] == "stale"
            ) else [],
            "mock": False,
            "telemetry": {
                "available": cache["available"],
                "source_mode": cache["source_mode"],
                "diagnostics": cache["diagnostics"],
            },
        })
        if "error" in cache:
            data["telemetry"]["error"] = cache["error"]
        if cache["source_mode"] == "unavailable" and explicit_mock:
            data["npus"] = _mock_npu()
            data["mock"] = True
            data["source_mode"] = "mock"
            data["telemetry"]["source_mode"] = "mock"
        data["count"] = len(data["npus"])
        _hw_cache.update({
            "d": copy.deepcopy(data),
            "t": data["ts"],
            "e": telemetry_epoch,
        })
        return copy.deepcopy(data)


def get_hw():
    """Merge supervisor telemetry cache with local CPU, memory, and disk metrics."""
    now = time.time()
    with _hw_lock:
        telemetry = _TELEMETRY
        telemetry_epoch = _TELEMETRY_EPOCH
        telemetry_active = _TELEMETRY_ACTIVE
        if (
            _hw_cache["d"]
            and _hw_cache.get("e") == telemetry_epoch
            and (telemetry is None or telemetry_active)
            and now - _hw_cache["t"] < 1.5
        ):
            return copy.deepcopy(_hw_cache["d"])
        explicit_mock = _EXPLICIT_MOCK
        ds = _DS
        dx_ok = _dx_ok

    if telemetry is not None:
        if not telemetry_active:
            data = {
                "available": False,
                "source_mode": "unavailable",
                "npus": [],
                "count": 0,
                "ts": now,
                "mock": False,
                "telemetry": {
                    "available": False,
                    "source_mode": "unavailable",
                    "diagnostics": ["Telemetry supervisor is stopping"],
                },
            }
            _add_host_metrics(data)
            return data
        cache = _telemetry_cache(telemetry)
        with _hw_lock:
            telemetry_is_current = (
                _TELEMETRY is telemetry
                and _TELEMETRY_EPOCH == telemetry_epoch
                and _TELEMETRY_ACTIVE
            )
        if not telemetry_is_current:
            cache = _telemetry_cache(None)
            explicit_mock = False
        data = {
            "available": cache["available"],
            "source_mode": cache["source_mode"],
            "npus": cache["npus"] if (
                cache["available"] or cache["source_mode"] == "stale"
            ) else [],
            "ts": now,
            "mock": False,
            "telemetry": {
                "available": cache["available"],
                "source_mode": cache["source_mode"],
                "diagnostics": cache["diagnostics"],
            },
        }
        if "error" in cache:
            data["telemetry"]["error"] = cache["error"]
        if cache["source_mode"] == "unavailable" and explicit_mock:
            data["npus"] = _mock_npu()
            data["mock"] = True
            data["source_mode"] = "mock"
            data["telemetry"]["source_mode"] = "mock"
        data["count"] = len(data["npus"])
    else:
        # Compatibility only: no normal Monitor startup reaches this branch.
        npus = _legacy_npus() if dx_ok and ds else []
        data = {
            "available": bool(dx_ok and ds),
            "source_mode": "real" if dx_ok and ds else "unavailable",
            "npus": npus,
            "count": len(npus),
            "ts": now,
            "mock": False,
            "telemetry": {
                "available": bool(dx_ok and ds),
                "source_mode": "real" if dx_ok and ds else "unavailable",
                "diagnostics": [],
            },
        }
        if not data["available"] and explicit_mock:
            data["npus"] = _mock_npu()
            data["count"] = len(data["npus"])
            data["mock"] = True
            data["source_mode"] = "mock"
            data["telemetry"]["source_mode"] = "mock"

    _add_host_metrics(data)
    with _hw_lock:
        telemetry_is_current = (
            _TELEMETRY is telemetry
            and _TELEMETRY_EPOCH == telemetry_epoch
            and (telemetry is None or _TELEMETRY_ACTIVE)
        )
        if telemetry_is_current:
            _hw_cache.update({
                "d": copy.deepcopy(data),
                "t": now,
                "e": telemetry_epoch,
            })
    if not telemetry_is_current:
        # A concurrent bind, shutdown, or replacement invalidated this
        # snapshot. Refresh exactly once against the current lifecycle state;
        # this avoids returning a legacy unavailable payload after a provider
        # starts and cannot spin indefinitely during repeated rebinds.
        return _refresh_after_telemetry_rebind(data)
    return copy.deepcopy(data)

def get_sysinfo():
    i = {"os": platform.platform(), "hostname": platform.node(),
         "arch": platform.machine(), "python": sys.version.split()[0],
         "dx_engine_available": False}
    try: import cv2; i["opencv"] = cv2.__version__
    except Exception: i["opencv"] = "N/A"
    # F-16: release.ver lives in the runtime repo, not the studio tree. _APP_ROOT is
    # <suite>/dx-ai-studio/dx_app, so the suite root is two levels up and the real files
    # are <suite>/dx-runtime/{dx_rt,dx_app}/release.ver.
    _runtime = _APP_ROOT.parent.parent / "dx-runtime"
    for lbl, p in [("dx_rt_version", _runtime / "dx_rt" / "release.ver"),
                    ("dx_app_version", _runtime / "dx_app" / "release.ver")]:
        i[lbl] = p.read_text().strip() if p.exists() else "N/A"
    with _hw_lock:
        telemetry = _TELEMETRY
        telemetry_epoch = _TELEMETRY_EPOCH
        telemetry_active = _TELEMETRY_ACTIVE
    telemetry_binding = telemetry
    telemetry_info = {}
    telemetry_snapshot = {
        "available": False,
        "source_mode": "unavailable",
        "npus": [],
        "diagnostics": ["Telemetry supervisor is stopping"],
    }
    if telemetry is not None and telemetry_active:
        telemetry_snapshot = _telemetry_cache(telemetry)
        with _hw_lock:
            telemetry_is_current = (
                _TELEMETRY is telemetry
                and _TELEMETRY_EPOCH == telemetry_epoch
                and _TELEMETRY_ACTIVE
            )
        if telemetry_is_current:
            try:
                candidate = telemetry.system_info()
                telemetry_info = candidate if isinstance(candidate, dict) else {}
            except Exception:
                telemetry_info = {}
        with _hw_lock:
            telemetry_is_current = (
                _TELEMETRY is telemetry
                and _TELEMETRY_EPOCH == telemetry_epoch
                and _TELEMETRY_ACTIVE
            )
        if not telemetry_is_current:
            telemetry = None
            telemetry_info = {}
            telemetry_snapshot = {
                "available": False,
                "source_mode": "unavailable",
                "npus": [],
                "diagnostics": ["Telemetry supervisor is stopping"],
            }
    try:
        npu_count = int(telemetry_info.get("npu_count", len(telemetry_snapshot["npus"])))
        npu_count = max(0, npu_count)
    except (TypeError, ValueError):
        npu_count = len(telemetry_snapshot["npus"])
    telemetry_fields = {
        "dx_engine_available": bool(
            telemetry_info.get("available", telemetry_snapshot["available"])
        ) if telemetry is not None else False,
        "npu_count": npu_count,
        "sdk_version": telemetry_info.get("sdk_version", "N/A"),
        "driver_version": telemetry_info.get("driver_version", "N/A"),
        "pcie_driver_version": telemetry_info.get("pcie_driver_version", "N/A"),
    }
    i.update(telemetry_fields)
    try:
        raw = open("/proc/uptime").read().split()[0]
        uptime_sec = int(float(raw))
        days, rem = divmod(uptime_sec, 86400)
        hours, rem = divmod(rem, 3600)
        mins, secs = divmod(rem, 60)
        parts = []
        if days: parts.append(f"{days}d")
        if hours: parts.append(f"{hours}h")
        parts.append(f"{mins}m")
        i["uptime"] = " ".join(parts)
        i["uptime_seconds"] = uptime_sec
    except Exception:
        i["uptime"] = "N/A"
        i["uptime_seconds"] = 0
    try:
        out = subprocess.check_output(["lspci"], text=True, timeout=5,
                                       stderr=subprocess.DEVNULL)
        i["npu_pci"] = [
            line for line in out.splitlines()
            if "deepx" in line.lower() or "1ff4:0000" in line.lower()
        ] or ["Not detected"]
    except Exception: i["npu_pci"] = ["N/A"]
    try:
        m = open("/proc/meminfo").read()
        i["mem_total_gb"] = round(int(re.search(r'MemTotal:\s+(\d+)', m).group(1))/1024/1024, 1)
    except Exception: i["mem_total_gb"] = 0
    try:
        ci = open("/proc/cpuinfo").read()
        ms = re.findall(r'model name\s*:\s*(.+)', ci)
        i["cpu_model"] = ms[0].strip() if ms else "N/A"
        i["cpu_cores"] = len(re.findall(r'^processor', ci, re.M))
    except Exception: i.update({"cpu_model": "N/A", "cpu_cores": 0})
    # 임계치 (프론트엔드 전달용)
    try:
        from dx_monitor.core.config import THRESHOLDS
        cpu_cores = i.get("cpu_cores", 4) or 4
        th = {}
        for k, v in THRESHOLDS.items():
            if k == "cpu_load":
                th[k] = {
                    "warn": round(v["warn_factor"] * cpu_cores, 1),
                    "crit": round(v["crit_factor"] * cpu_cores, 1),
                    "unit": "",
                }
            else:
                th[k] = dict(v)
        i["thresholds"] = th
    except ImportError:
        i["thresholds"] = {}
    with _hw_lock:
        telemetry_is_current = (
            telemetry_binding is not None
            and _TELEMETRY is telemetry_binding
            and _TELEMETRY_EPOCH == telemetry_epoch
            and _TELEMETRY_ACTIVE
        )
    if not telemetry_is_current:
        # Host probes remain valid, but no telemetry-derived value can outlive
        # the exact supervisor binding from which it was captured.
        i.update({
            "dx_engine_available": False,
            "npu_count": 0,
            "sdk_version": "N/A",
            "driver_version": "N/A",
            "pcie_driver_version": "N/A",
        })
    return i
