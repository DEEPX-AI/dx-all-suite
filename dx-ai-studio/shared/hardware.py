"""Shared hardware monitoring — NPU, CPU, memory, disk status."""
import os, sys, re, json, time, subprocess, platform, threading, math, shutil
from pathlib import Path

_DS = None
_dx_ok = False
_NPU_STATS_BIN = Path("/dev/null")
_APP_ROOT = Path(".")
_hw_cache = {"d": None, "t": 0.0}
_hw_lock = threading.Lock()
_prev_cpu = None

def init_hw(ds=None, dx_ok=False, npu_stats_bin=None, app_root=None):
    """Initialize hardware module. Call once at server startup."""
    global _DS, _dx_ok, _NPU_STATS_BIN, _APP_ROOT
    _DS = ds
    _dx_ok = dx_ok
    if npu_stats_bin:
        _NPU_STATS_BIN = Path(npu_stats_bin)
    if app_root:
        _APP_ROOT = Path(app_root)

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

_DEVICE_INFO_FIELDS = (
    "firmware_version", "device_type", "device_variant", "board_type",
    "memory_type", "memory_size_bytes", "memory_freq_mhz",
    "ddr_status", "ddr_sbe_cnt", "ddr_dbe_cnt",
)
_DXRT_INVALID_TEMPERATURE = -32768

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

def get_hw():
    now = time.time()
    with _hw_lock:
        if _hw_cache["d"] and now - _hw_cache["t"] < 1.5:
            return _hw_cache["d"]
    d = {"available": _dx_ok, "npus": [], "ts": now}
    if _dx_ok and _DS:
        try:
            cnt = _DS.get_device_count(); d["count"] = cnt
            for did in range(cnt):
                dev = _DS.get_current_status(did); T, V, C = [], [], []
                for ch in range(4):
                    try:
                        temp = dev.get_temperature(ch)
                        if temp == _DXRT_INVALID_TEMPERATURE:
                            break
                        T.append(temp)
                        V.append(dev.get_npu_voltage(ch))
                        C.append(dev.get_npu_clock(ch))
                    except: break
                npu_entry = {
                    "id": did,
                    "device_id": dev.get_id() if hasattr(dev, 'get_id') else did,
                    "cores": len(T), "temperatures": T, "voltages_mV": V, "clocks_MHz": C,
                    "temp_avg": sum(T)/len(T) if T else 0,
                    "voltage_avg": sum(V)/len(V) if V else 0,
                    "clock_avg": sum(C)/len(C) if C else 0,
                    "power_est_mW": (sum(V)/len(V))*0.5 if V else 0,
                    "dram_used_mb": -1, "dram_total_mb": -1, "dram_pct": -1,
                    "utilization": []
                }
                if _NPU_STATS_BIN.exists():
                    try:
                        raw = subprocess.check_output(
                            [str(_NPU_STATS_BIN), str(did), str(len(T))],
                            timeout=2, stderr=subprocess.DEVNULL)
                        ns = json.loads(raw)
                        npu_entry.update({k: ns[k] for k in ns
                            if k in ("dram_used_mb","dram_free_mb","dram_total_mb","dram_pct","utilization")})
                        for f in _DEVICE_INFO_FIELDS:
                            if f in ns:
                                npu_entry[f] = ns[f]
                    except: pass
                d["npus"].append(npu_entry)
        except Exception as e:
            d["error"] = str(e); d["npus"] = _mock_npu()
    else:
        d["npus"] = _mock_npu(); d["mock"] = True
    try:
        m = open("/proc/meminfo").read()
        tot = int(re.search(r'MemTotal:\s+(\d+)', m).group(1))
        av = int(re.search(r'MemAvailable:\s+(\d+)', m).group(1))
        d.update({"mem_total_mb": tot//1024, "mem_used_mb": (tot-av)//1024,
                  "mem_pct": round((tot-av)/tot*100, 1)})
        st = re.search(r'SwapTotal:\s+(\d+)', m)
        sf = re.search(r'SwapFree:\s+(\d+)', m)
        if st and sf:
            swap_total = int(st.group(1))
            swap_free = int(sf.group(1))
            swap_used = swap_total - swap_free
            d.update({"swap_total_mb": swap_total // 1024,
                      "swap_used_mb": swap_used // 1024,
                      "swap_pct": round(swap_used / swap_total * 100, 1) if swap_total > 0 else 0.0})
        else:
            d.update({"swap_total_mb": 0, "swap_used_mb": 0, "swap_pct": 0.0})
    except: d.update({"mem_total_mb": 0, "mem_used_mb": 0, "mem_pct": 0,
                      "swap_total_mb": 0, "swap_used_mb": 0, "swap_pct": 0.0})
    try: d["cpu_load"] = float(open("/proc/loadavg").read().split()[0])
    except: d["cpu_load"] = 0.0
    d["cpu_cores_pct"] = _read_cpu_per_core()
    try:
        du = shutil.disk_usage('/')
        d.update({"disk_total_gb": round(du.total/1e9, 1),
                  "disk_used_gb": round(du.used/1e9, 1),
                  "disk_pct": round(du.used/du.total*100, 1)})
    except: d.update({"disk_total_gb": 0, "disk_used_gb": 0, "disk_pct": 0})
    with _hw_lock:
        _hw_cache.update({"d": d, "t": now})
    return d

def get_sysinfo():
    i = {"os": platform.platform(), "hostname": platform.node(),
         "arch": platform.machine(), "python": sys.version.split()[0],
         "dx_engine_available": _dx_ok}
    try: import cv2; i["opencv"] = cv2.__version__
    except: i["opencv"] = "N/A"
    # F-16: release.ver lives in the runtime repo, not the studio tree. _APP_ROOT is
    # <suite>/dx-ai-studio/dx_app, so the suite root is two levels up and the real files
    # are <suite>/dx-runtime/{dx_rt,dx_app}/release.ver.
    _runtime = _APP_ROOT.parent.parent / "dx-runtime"
    for lbl, p in [("dx_rt_version", _runtime / "dx_rt" / "release.ver"),
                    ("dx_app_version", _runtime / "dx_app" / "release.ver")]:
        i[lbl] = p.read_text().strip() if p.exists() else "N/A"
    try:
        from dx_engine.configuration import Configuration
        # dx_engine's Configuration has no get_instance(); it's instantiated directly
        # (it manages its own internal singleton). The old get_instance() call raised
        # AttributeError, silently falling through to the N/A branch on real boards.
        cfg = Configuration()
        i["sdk_version"] = cfg.get_version()
        i["driver_version"] = cfg.get_driver_version()
        i["pcie_driver_version"] = cfg.get_pcie_driver_version()
    except Exception:
        i.update({"sdk_version": "N/A", "driver_version": "N/A",
                  "pcie_driver_version": "N/A"})
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
        i["npu_pci"] = [l for l in out.splitlines() if "deepx" in l.lower()] or ["Not detected"]
    except: i["npu_pci"] = ["N/A"]
    try:
        m = open("/proc/meminfo").read()
        i["mem_total_gb"] = round(int(re.search(r'MemTotal:\s+(\d+)', m).group(1))/1024/1024, 1)
    except: i["mem_total_gb"] = 0
    try:
        ci = open("/proc/cpuinfo").read()
        ms = re.findall(r'model name\s*:\s*(.+)', ci)
        i["cpu_model"] = ms[0].strip() if ms else "N/A"
        i["cpu_cores"] = len(re.findall(r'^processor', ci, re.M))
    except: i.update({"cpu_model": "N/A", "cpu_cores": 0})
    i["npu_count"] = _DS.get_device_count() if _dx_ok and _DS else 0
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
    return i
