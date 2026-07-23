"""DX Monitor — 하드웨어 SDK 초기화.

기존 dx_monitor/config.py의 SDK 초기화 로직을 분리.
import 시 자동으로 DX Engine SDK를 로드하고 hardware.py를 초기화한다.
"""
import sys
from pathlib import Path

from dx_monitor.core.config import STUDIO_DIR, SCRIPT_DIR, DX_APP_ROOT
from shared import runtime as _runtime

_DS = None
_dx_ok = False
_NPU_STATS_BIN = SCRIPT_DIR / "dx_npu_stats"

if not _NPU_STATS_BIN.exists():
    _alt = DX_APP_ROOT / "core" / "dx_npu_stats"
    if _alt.exists():
        _NPU_STATS_BIN = _alt


def _try_import_dx():
    from dx_engine.device_status import DeviceStatus
    return DeviceStatus


def _load_dx():
    global _DS, _dx_ok
    # 1) Prefer an already-importable dx_engine (e.g. the studio venv's fully-built
    #    package). Do this BEFORE any sys.path injection so an *uncompiled* source tree
    #    on a fallback path (dx_rt/python_package/src has no compiled _pydxrt.so) cannot
    #    shadow a working install and force mock NPU data.
    try:
        _DS = _try_import_dx()
        _dx_ok = True
        print("[DX Monitor] dx_engine loaded")
        return
    except Exception:
        pass
    # 2) Fallback for environments where dx_engine is not on the path yet: inject known
    #    SDK locations, then retry. Only reached when the direct import above failed.
    for sp in _runtime.dx_engine_search_paths():
        if str(sp) not in sys.path:
            sys.path.insert(0, str(sp))
    try:
        _DS = _try_import_dx()
        _dx_ok = True
        print("[DX Monitor] dx_engine loaded (via fallback path)")
    except Exception:
        _dx_ok = False
        print("[DX Monitor] dx_engine unavailable — mock NPU data")


def init():
    """SDK 로드 + hardware.py 초기화. 서버 시작 시 1회 호출."""
    _load_dx()
    from shared.hardware import init_hw
    init_hw(ds=_DS, dx_ok=_dx_ok, npu_stats_bin=_NPU_STATS_BIN,
            app_root=DX_APP_ROOT)
