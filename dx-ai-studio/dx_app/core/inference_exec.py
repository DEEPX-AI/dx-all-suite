"""DX-APP Inference execution helpers — temp-file plumbing, binary/script
resolution, stdout parsing, and shared constants used by the inference /
camera / live modules.

Bottom layer of the inference.py split (see dx_app/core/inference.py docstring
for the layered DAG): imports only stdlib + dx_app.core.config. No sibling
dx_app.core.{camera,live,inference} imports here — this keeps the DAG acyclic.
"""

import os, re, time, subprocess, shutil, tempfile
from pathlib import Path
from dx_app.core.config import PY_DIR, BUILD_DIR, _RUNTIME_PYTHON

# Honor $TMPDIR (fall back to the system temp dir) instead of a hardcoded "/tmp",
# so the app works where /tmp is unwritable/isolated.
_TMP = tempfile.gettempdir()

def _sweep_stale_temp(max_age_s=6 * 3600):
    """Best-effort janitor for our own leaked temp artifacts (e.g. a SIGKILL mid-run
    leaves /tmp/dxapp_video_* / dxapp_upload_* behind — there is no finally net yet).
    Only touches our own prefixed entries; never raises."""
    import glob
    now = time.time()
    for pat in ("dxapp_video_*", "dxapp_upload_*"):
        for p in glob.glob(os.path.join(_TMP, pat)):
            try:
                if now - os.path.getmtime(p) < max_age_s:
                    continue
                shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else os.unlink(p)
            except OSError:
                pass

_PAIR_COMPARE_CATS = frozenset({"embedding", "reid"})
_STDOUT_TAG_CATS = frozenset({"classification", "attribute_recognition"})
_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".bmp"})


def _count_images_in_dir(path: Path) -> int:
    if not path.is_dir():
        return 0
    return sum(
        1 for f in path.iterdir()
        if f.is_file() and f.suffix.lower() in _IMAGE_EXTENSIONS
    )


def _python_script_path(category, model_name, variant, py_dir=None):
    # py_dir defaults to config.PY_DIR, but callers (inference.run_inference) pass
    # their own current PY_DIR through explicitly — that's the same name tests
    # monkeypatch on the dx_app.core.inference module, so this keeps the lookup
    # observing whatever value the caller's module currently has, not a stale
    # inference_exec-local copy taken at import time.
    py_dir = PY_DIR if py_dir is None else py_dir
    pf = py_dir / category / model_name / f"{model_name}_{variant}.py"
    return pf if pf.exists() else None


def _python_runtime_ready():
    try:
        return subprocess.run(
            [_RUNTIME_PYTHON, "-c", "import numpy,cv2"],
            capture_output=True, timeout=15,
        ).returncode == 0
    except Exception:
        return False


def _effective_run_lang(lang, category, model_name, variant, input_type):
    """Keep user-selected lang; C++ video omits --save to avoid stock VideoWriter SIGABRT."""
    return lang


def _err(error_key, error, **extra):
    payload = {"error": error, "error_key": error_key}
    payload.update(extra)
    return payload


_FALLBACK_BINARIES = {
    "classification":           ["mobilenetv2","resnet50","alexnet","efficientnet_b0","mobilenetv1"],
    "object_detection":         ["yolov5s","yolov8n","yolov7","yolox_s","damoyolo","ssd_mobilenetv1"],
    "face_detection":           ["retinaface_mobilenet0_25_640","blazeface","scrfd_500m"],
    "pose_estimation":          ["hrnet_w32_256x192","centerpose_regnetx_800mf","movenet"],
    "semantic_segmentation":    ["deeplabv3","bisenetv2","deeplabv3plusmobilenet"],
    "instance_segmentation":    ["yolact","mask_rcnn"],
}

def _find_fallback_binary(category, variant="sync", build_dir=None):
    """Find a compatible existing binary for custom models without their own binary.
    build_dir defaults to config.BUILD_DIR — see _python_script_path's py_dir
    param docstring for why callers pass their own current BUILD_DIR through."""
    build_dir = BUILD_DIR if build_dir is None else build_dir
    candidates = _FALLBACK_BINARIES.get(category, _FALLBACK_BINARIES["classification"])
    for name in candidates:
        bp = build_dir / f"{name}_{variant}"
        if bp.exists():
            return bp
    pattern = f"*_{variant}"
    for bp in sorted(build_dir.glob(pattern)):
        if bp.is_file() and os.access(str(bp), os.X_OK):
            return bp
    return None


def _find_saved_video(stdout_text, save_dir=None):
    """Find the video file produced by C++ runners using --save."""
    candidates = []
    for line in (stdout_text or "").splitlines():
        m = re.search(r"Saving output video:\s*(.+?)(?:\s+\([^)]*\))?\s*$", line.strip())
        if m:
            candidates.append(Path(m.group(1).strip()))
    if save_dir:
        root = Path(save_dir)
        if root.exists():
            candidates.extend(
                p for p in root.rglob("output.*")
                if p.suffix.lower() in {".mp4", ".avi", ".mov", ".mkv"}
            )
    for path in candidates:
        if path.exists() and path.stat().st_size > 0:
            return path
    return None


def _drain_dxrt_msgqueues():
    """Best-effort cleanup for stale dxrtd IPC messages before launching DXRT."""
    try:
        import ctypes
        import ctypes.util
        libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
        ipc_nowait = 0x800
        msg_noerror = 0x1000
        buf = ctypes.create_string_buffer(8192)
        for key in (0x2a020467, 0x54020467):
            msqid = libc.msgget(key, 0)
            if msqid < 0:
                continue
            while libc.msgrcv(msqid, buf, 8000, 0, ipc_nowait | msg_noerror) >= 0:
                pass
    except Exception:
        pass
