"""Which .dxnn containers this PC's DX-RT can read.

A .dxnn header is 'DXNN' + a little-endian uint32 (the container version). DX-RT 3.4.2 reads 6–8; DX Model Zoo
2_5_0 files are 9 (DX-RT 3.4.2 says: "Model file format version 9 is not supported. Please use model file version
between 6 and 8."). v9 needs DX-RT 3.5.0.

- The version comes from ``dx-runtime/dx_rt/release.ver`` (e.g. ``v3.4.2``). Unknown never blocks.
- Downloads: an older DX-RT gets the same-named 2_4_0 (v8) file. If 2_4_0 lacks it, nothing is downloaded.

Contract: tests/dx_app/test_dxrt_container.py (shared by the studio's dx_app and dx_modelzoo)
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Optional

from shared.paths import DX_RUNTIME_ROOT
from shared.dx_app_layout import container_version

# The dxrt_driver kernel module's version (what Setup shows as "NPU Driver"). `dxrt-cli --version` is the
# DX-RT runtime ("DXRT v3.5.0"), not the driver (v2.7.0) — never use it for this.
_SYS_DRIVER_VERSION = Path("/sys/module/dxrt_driver/version")


def npu_driver_version() -> Optional[str]:
    """'v2.7.0' from the loaded module, else from the installed one (modinfo), else None."""
    try:
        value = _SYS_DRIVER_VERSION.read_text(encoding="utf-8").strip()
    except OSError:
        value = ""
    if not value:
        try:
            r = subprocess.run(["modinfo", "-F", "version", "dxrt_driver"], capture_output=True, text=True, timeout=5)
            value = r.stdout.strip() if r.returncode == 0 else ""
        except (OSError, subprocess.SubprocessError):
            value = ""
    value = value.lstrip("v")
    return f"v{value}" if value else None


# The DX-RT driver's DKMS module (dx_rt_npu_linux_driver/debian/rules: DKMS_MODULE_NAME).
DKMS_MODULE = "dxrt-driver-dkms"


def dkms_dxrt_status() -> tuple:
    """(returncode, output) of `dkms status` for the DX-RT driver: -1 when dkms is missing, -2 on timeout.

    Asks for the driver module only — a bare `dkms status` walks every module on every kernel (6.5 s on a Pi with
    v4l2loopback and seven kernels, 0.8 s for this module). Falls back to the full listing when the module query
    finds nothing, since older packages named the module differently (callers look for "dxrt" / "deepx")."""
    def run(argv):
        r = subprocess.run(argv, capture_output=True, text=True, timeout=15)
        return r.returncode, (r.stdout or "").strip()
    try:
        rc, out = run(["dkms", "status", "-m", DKMS_MODULE])
        if rc == 0 and out:
            return rc, out
        return run(["dkms", "status"])
    except FileNotFoundError:
        return -1, ""
    except subprocess.TimeoutExpired:
        return -2, ""


NEEDS_FOR_V9 = "3.5.0"
_V9_FROM = (3, 5, 0)


def runtime_version() -> Optional[tuple]:
    try:
        text = (Path(DX_RUNTIME_ROOT) / "dx_rt" / "release.ver").read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    return tuple(int(x) for x in m.groups()) if m else None


def max_container() -> Optional[int]:
    v = runtime_version()
    if v is None:
        return None
    return 9 if v >= _V9_FROM else 8


def supports(container: Optional[int]) -> bool:
    top = max_container()
    return container is None or top is None or container <= top


def needs_for(container: Optional[int]) -> Optional[str]:
    """The DX-RT this container needs (None when the installed one runs it)."""
    return None if supports(container) else NEEDS_FOR_V9


def needs_for_file(path) -> Optional[str]:
    return needs_for(container_version(path))


def download_urls(url: str) -> list:
    """URLs to try, in order. If DX-RT cannot read v9, the 2_4_0 copy replaces the 2_5_0 one."""
    if url and "/2_5_0/" in url and not supports(9):
        return [url.replace("/2_5_0/", "/2_4_0/")]
    return [url]


def is_v9_only(url: str) -> bool:
    return bool(url) and "/2_5_0/" in url


def run_env(base: dict) -> dict:
    """Environment for a dx_app run. Models with CPU tasks in their graph (RT-DETR r18 etc.) stall even in async
    when that task has one thread — so set DX-RT's recommended DXRT_DYNAMIC_CPU_THREAD=ON (C++ async 4.2 → 9.3
    FPS). A value already set is kept.
    Qt paths that opencv-python adds on import (cv2/qt/...) are removed — a runner linked against the system Qt5
    aborts loading those plugins (the live view goes black). Qt paths pointing elsewhere are the user's and stay.
    Contract: tests/dx_app/test_dxrt_cpu_thread.py"""
    env = dict(base)
    env.setdefault("DXRT_DYNAMIC_CPU_THREAD", "ON")
    for key in _CV2_QT_VARS:
        if Path(env.get(key) or "/").parent.parent.name == "cv2":
            env.pop(key)
    return env


_CV2_QT_VARS = ("QT_QPA_PLATFORM_PLUGIN_PATH", "QT_QPA_FONTDIR", "QT_PLUGIN_PATH")
