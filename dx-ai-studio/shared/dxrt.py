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
from pathlib import Path
from typing import Optional

from shared.paths import DX_RUNTIME_ROOT
from shared.dx_app_layout import container_version

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
