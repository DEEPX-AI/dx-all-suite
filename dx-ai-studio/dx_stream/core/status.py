"""System status — NPU, GStreamer, models, videos and build state.

Used by the dashboard and the setup page to show what is missing before a pipeline fails.
"""
from __future__ import annotations

import json, os, shutil, subprocess, platform, sys
from pathlib import Path
from dx_stream.core.config import DX_STREAM_ROOT, MODELS_DIR, VIDEOS_DIR, MODEL_LIST_JSON


def _all_model_files() -> list[str]:
    from dx_stream.core.models import get_models
    return [m["file"] for m in get_models()]


def _check_npu() -> dict:
    """Whether an NPU device exists (/dev/dxrt*)."""
    devices = sorted(str(p) for p in Path("/dev").glob("dxrt*"))
    return {"ok": len(devices) > 0, "devices": devices}


def _check_gst() -> dict:
    """GStreamer installed and the dxstream plugins present."""
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
    """Model download state — whether each catalog .dxnn exists."""
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
    """Whether the sample videos exist."""
    if not VIDEOS_DIR.is_dir():
        return {"ok": False, "count": 0, "files": []}
    # setup.sh extracts the tarball into a sample_videos/ subfolder — count what the demos find
    # (core.demos._video_path also searches below VIDEOS_DIR).
    vids = [f.name for f in VIDEOS_DIR.rglob("*")
            if f.is_file() and f.suffix.lower() in (".mp4", ".mov", ".avi", ".mkv")]
    return {"ok": len(vids) > 0, "count": len(vids), "files": sorted(vids)}


def _nice_plugin_ok() -> bool:
    try:
        return subprocess.run(["gst-inspect-1.0", "nicesrc"], capture_output=True, timeout=5).returncode == 0
    except Exception:
        return False


def _gi_webrtc_ok() -> bool:
    """Whether this server's Python can load the GstWebRTC binding (it drives webrtcbin)."""
    try:
        import gi
        gi.require_version("GstWebRTC", "1.0")
        from gi.repository import GstWebRTC  # noqa: F401
        return True
    except Exception:
        return False


def _check_webrtc() -> dict:
    """WebRTC dependencies — both nicesrc and the GstWebRTC binding. With nicesrc alone Setup says "OK" while
    Local (WebRTC) still falls back to MJPEG (gir1.2-gst-plugins-bad-1.0 missing)."""
    nice_ok = _nice_plugin_ok()
    gi_ok = _gi_webrtc_ok()
    missing = ([] if nice_ok else ["gstreamer1.0-nice"]) + ([] if gi_ok else ["gir1.2-gst-plugins-bad-1.0"])
    return {"ok": nice_ok and gi_ok, "nice_plugin": nice_ok, "gi_webrtc": gi_ok, "missing": missing}


def _check_build() -> dict:
    """GStreamer plugin build state — whether the .so files exist (via the shared finder)."""
    from dx_stream.core import gst_env

    so = gst_env.find_dxstream_plugin()
    return {"ok": bool(so), "path": str(so) if so else None}


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
    """All system status in one dict."""
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
