"""시스템 상태 감지 — NPU, GStreamer, 모델, 비디오, 빌드 상태를 확인한다.

대시보드 및 설정 페이지에서 사용.
실패 시나리오 #1~#3 완화의 핵심 모듈.
"""
from __future__ import annotations

import json, os, shutil, subprocess, platform, sys
from pathlib import Path
from dx_stream.core.config import DX_STREAM_ROOT, MODELS_DIR, VIDEOS_DIR, MODEL_LIST_JSON


def _all_model_files() -> list[str]:
    from dx_stream.core.models import get_models
    return [m["file"] for m in get_models()]


def _check_npu() -> dict:
    """NPU 디바이스 존재 여부 — /dev/dxrt* 패턴"""
    devices = sorted(str(p) for p in Path("/dev").glob("dxrt*"))
    return {"ok": len(devices) > 0, "devices": devices}


def _check_gst() -> dict:
    """GStreamer 설치 및 dxstream 플러그인 확인"""
    gst_bin = shutil.which("gst-inspect-1.0")
    if not gst_bin:
        return {"ok": False, "installed": False, "plugin": False}
    try:
        r = subprocess.run(
            ["gst-inspect-1.0", "dxstream"],
            capture_output=True, timeout=5
        )
        plugin_ok = r.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        plugin_ok = False
    return {"ok": plugin_ok, "installed": True, "plugin": plugin_ok}


def _check_models() -> dict:
    """모델 다운로드 상태 — 카탈로그 기준 각 .dxnn 존재 여부"""
    from dx_stream.core.models import get_catalog_source
    all_models = _all_model_files()
    installed = []
    missing = []
    if MODELS_DIR.is_dir():
        for m in all_models:
            if (MODELS_DIR / m).exists():
                installed.append(m)
            else:
                missing.append(m)
    else:
        missing = list(all_models)
    return {
        "ok": len(missing) == 0 and len(installed) > 0,
        "total": len(all_models),
        "installed": len(installed),
        "missing": missing,
        "installed_list": installed,
        "catalog_source": get_catalog_source(),
    }


def _check_videos() -> dict:
    """샘플 비디오 존재 여부"""
    if not VIDEOS_DIR.is_dir():
        return {"ok": False, "count": 0, "files": []}
    vids = [f.name for f in VIDEOS_DIR.iterdir()
            if f.suffix.lower() in (".mp4", ".mov", ".avi", ".mkv")]
    return {"ok": len(vids) > 0, "count": len(vids), "files": sorted(vids)}


def _check_webrtc() -> dict:
    """WebRTC 의존성 확인 — nicesrc 플러그인 필요"""
    try:
        r = subprocess.run(
            ["gst-inspect-1.0", "nicesrc"],
            capture_output=True, timeout=5
        )
        nice_ok = r.returncode == 0
    except Exception:
        nice_ok = False
    return {"ok": nice_ok, "nice_plugin": nice_ok}


def _check_build() -> dict:
    """GStreamer 플러그인 빌드 상태 — .so 파일 존재 확인"""
    plugin_paths = [
        Path("/usr/local/lib/gstreamer-1.0/libgstdxstream.so"),
        Path("/usr/lib/gstreamer-1.0/libgstdxstream.so"),
    ]
    for p in plugin_paths:
        if p.exists():
            return {"ok": True, "path": str(p)}
    gst_path = os.environ.get("GST_PLUGIN_PATH", "")
    if gst_path:
        for d in gst_path.split(":"):
            so = Path(d) / "libgstdxstream.so"
            if so.exists():
                return {"ok": True, "path": str(so)}
    return {"ok": False, "path": None}


def _get_gst_version():
    try:
        r = subprocess.run(['gst-inspect-1.0', '--version'], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            for line in r.stdout.split('\n'):
                if 'GStreamer' in line:
                    return line.strip()
        return '--'
    except Exception:
        return '--'


def _get_npu_driver_version():
    try:
        r = subprocess.run(['dxrt-cli', '--version'], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return r.stdout.strip().split('\n')[0]
    except Exception:
        pass
    return '--'


def check_system(pipeline_mgr=None) -> dict:
    """전체 시스템 상태 집계"""
    result = {
        "npu": _check_npu(),
        "gstreamer": _check_gst(),
        "models": _check_models(),
        "videos": _check_videos(),
        "build": _check_build(),
        "webrtc": _check_webrtc(),
        "system_info": {
            "os": f"{platform.system()} {platform.release()}",
            "gstreamer_version": _get_gst_version(),
            "npu_driver_version": _get_npu_driver_version(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }
    }
    result["catalog_source"] = result["models"].get("catalog_source")
    return result
