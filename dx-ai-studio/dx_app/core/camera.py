"""DX-APP camera & display helpers — device listing, per-slot Xvfb lifecycle,
ffmpeg camera multiplexing (single real camera fanned out to N UDP streams),
ROI cropping, and live-frame capture.

Layer 2 of the inference.py split (see dx_app/core/inference.py docstring for
the layered DAG): imports inference_exec only. No dependency on live.py or
inference.py — this keeps the DAG acyclic.
"""

import os, time, threading, tempfile, subprocess, io
from pathlib import Path
from dx_app.core.inference_exec import _TMP

_xvfb_procs = {}             # slot_idx -> Xvfb proc
_xvfb_lock = threading.Lock()
_capture_locks = {}          # slot_idx -> Lock (lazy)
_capture_locks_meta = threading.Lock()
_XVFB_BASE = 99
_XVFB_RES = "1280x720x24"

_UDP_BASE_PORT = 9100        # UDP ports 9100, 9101, 9102 ...
_cam_mux_proc = None         # ffmpeg tee process
_cam_mux_lock = threading.Lock()
_cam_mux_count = 0           # how many UDP streams are active


def _start_cam_mux(real_cam_idx, n_slots):
    """Start ffmpeg to fan out real camera to N local UDP streams (no sudo)."""
    global _cam_mux_proc, _cam_mux_count
    with _cam_mux_lock:
        if _cam_mux_proc and _cam_mux_proc.poll() is None:
            _cam_mux_proc.terminate()
            try: _cam_mux_proc.wait(timeout=3)
            except: _cam_mux_proc.kill()
            _cam_mux_proc = None

        real_dev = f"/dev/video{real_cam_idx}"
        if not Path(real_dev).exists():
            print(f"[CAM-MUX] Real camera not found: {real_dev}")
            return False

        # Build ffmpeg command: read from real camera, encode once to H.264,
        # then fan-out to N UDP mpegts streams using tee muxer (single encode)
        tee_parts = []
        for i in range(n_slots):
            port = _UDP_BASE_PORT + i
            tee_parts.append(f"[f=mpegts]udp://127.0.0.1:{port}?pkt_size=1316")
        tee_output = "|".join(tee_parts)

        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning",
               "-f", "v4l2", "-input_format", "mjpeg",
               "-video_size", "640x480", "-framerate", "30",
               "-i", real_dev,
               "-map", "0:v",
               "-c:v", "libx264", "-preset", "ultrafast",
               "-tune", "zerolatency", "-g", "30",
               "-f", "tee", tee_output]

        print(f"[CAM-MUX] Starting ffmpeg: {' '.join(cmd)}")
        _cam_mux_proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            close_fds=True)
        _cam_mux_count = n_slots
        time.sleep(1.5)  # let UDP streams initialize
        if _cam_mux_proc.poll() is not None:
            stderr = _cam_mux_proc.stderr.read().decode(errors="replace")
            print(f"[CAM-MUX] ffmpeg exited immediately: {stderr[:500]}")
            _cam_mux_proc = None
            return False
        print(f"[CAM-MUX] ffmpeg running PID={_cam_mux_proc.pid}, {n_slots} UDP streams")
        return True


def _stop_cam_mux():
    """Stop ffmpeg camera multiplexer."""
    global _cam_mux_proc, _cam_mux_count
    with _cam_mux_lock:
        if _cam_mux_proc and _cam_mux_proc.poll() is None:
            _cam_mux_proc.terminate()
            try: _cam_mux_proc.wait(timeout=3)
            except: _cam_mux_proc.kill()
            print("[CAM-MUX] ffmpeg stopped")
        _cam_mux_proc = None
        _cam_mux_count = 0

def _get_capture_lock(slot_idx):
    with _capture_locks_meta:
        if slot_idx not in _capture_locks:
            _capture_locks[slot_idx] = threading.Lock()
        return _capture_locks[slot_idx]


def _crop_roi(imgp, roi):
    try:
        import cv2; img = cv2.imread(str(imgp))
        if img is None:
            print(f"[ROI] Failed to read image: {imgp}")
            return None
        ih, iw = img.shape[:2]
        x = max(0, min(int(roi["x"]), iw - 1))
        y = max(0, min(int(roi["y"]), ih - 1))
        w = max(1, min(int(roi["w"]), iw - x))
        h = max(1, min(int(roi["h"]), ih - y))
        print(f"[ROI] Crop: x={x},y={y},w={w},h={h} from image {iw}x{ih}")
        cropped = img[y:y+h, x:x+w]
        if cropped.size == 0:
            print("[ROI] Empty crop result")
            return None
        tmp = tempfile.mktemp(suffix=".jpg", dir=_TMP)
        cv2.imwrite(tmp, cropped)
        print(f"[ROI] Saved crop to {tmp} ({w}x{h})")
        return tmp
    except Exception as e:
        print(f"[ROI] Error: {e}")
        return None


def list_cameras():
    """Scan /dev/video* and return available camera devices."""
    cams = []
    import glob
    for dev in sorted(glob.glob("/dev/video*")):
        idx = dev.replace("/dev/video", "")
        try:
            idx_int = int(idx)
        except ValueError:
            continue
        try:
            import cv2
            cap = cv2.VideoCapture(idx_int)
            ok = cap.isOpened()
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) if ok else 0
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) if ok else 0
            cap.release()
            cams.append({"index": idx_int, "device": dev, "available": ok, "width": w, "height": h})
        except Exception:
            cams.append({"index": idx_int, "device": dev, "available": False, "width": 0, "height": 0})
    return cams


def _ensure_xvfb(slot_idx=0):
    """Start per-slot Xvfb if not already running."""
    global _xvfb_procs
    display = f":{_XVFB_BASE + slot_idx}"
    with _xvfb_lock:
        proc = _xvfb_procs.get(slot_idx)
        if proc and proc.poll() is None:
            return
        os.system(f"pkill -f 'Xvfb {display}' 2>/dev/null")
        time.sleep(0.3)
        p = subprocess.Popen(
            ["Xvfb", display, "-screen", "0", _XVFB_RES, "-ac"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        _xvfb_procs[slot_idx] = p
        print(f"[LIVE] Xvfb started on {display} PID={p.pid}")


_display_env_lock = threading.Lock()   # global lock for DISPLAY env changes

def capture_live_frame(slot_idx=0):
    """Capture per-slot Xvfb screen as JPEG bytes (thread-safe)."""
    display = f":{_XVFB_BASE + slot_idx}"
    with _display_env_lock:
        old_display = os.environ.get("DISPLAY")
        os.environ["DISPLAY"] = display
        try:
            import mss
            from PIL import Image
            with mss.mss() as sct:
                mon = sct.monitors[0]
                img = sct.grab(mon)
                pil = Image.frombytes("RGB", (img.width, img.height), img.rgb)
                pil = pil.resize((960, 540), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                pil.save(buf, format="JPEG", quality=70)
                return buf.getvalue()
        except Exception as e:
            print(f"[LIVE] Capture error slot={slot_idx}: {e}")
            return None
        finally:
            if old_display is not None:
                os.environ["DISPLAY"] = old_display
            else:
                os.environ.pop("DISPLAY", None)
