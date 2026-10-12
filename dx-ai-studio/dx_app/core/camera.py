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
_cam_mux_last_error = ""


def _start_cam_mux(real_cam_idx, n_slots):
    """Start ffmpeg to fan out real camera to N local UDP streams (no sudo)."""
    global _cam_mux_proc, _cam_mux_count
    with _cam_mux_lock:
        if _cam_mux_proc and _cam_mux_proc.poll() is None:
            _cam_mux_proc.terminate()
            try: _cam_mux_proc.wait(timeout=3)
            except Exception: _cam_mux_proc.kill()
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

        # MJPEG 640x480 first (cheap to decode on most USB webcams); a camera without that mode (YUYV-only webcams,
        # capture cards) would make ffmpeg exit at once and fail every multi-slot run — then take the camera's own
        # format and scale to the same 640x480.
        attempts = [
            (["-input_format", "mjpeg", "-video_size", "640x480", "-framerate", "30"], []),
            ([], ["-vf", "scale=640:480"]),
        ]
        global _cam_mux_last_error
        _cam_mux_last_error = ""
        for in_opts, filt in attempts:
            cmd = (["ffmpeg", "-hide_banner", "-loglevel", "warning", "-f", "v4l2"] + in_opts + ["-i", real_dev,
                   "-map", "0:v"] + filt + ["-c:v", "libx264", "-preset", "ultrafast",
                   "-tune", "zerolatency", "-g", "30", "-f", "tee", tee_output])
            print(f"[CAM-MUX] Starting ffmpeg: {' '.join(cmd)}")
            _cam_mux_proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                close_fds=True)
            _cam_mux_count = n_slots
            time.sleep(1.5)  # let UDP streams initialize
            if _cam_mux_proc.poll() is None:
                print(f"[CAM-MUX] ffmpeg running PID={_cam_mux_proc.pid}, {n_slots} UDP streams")
                return True
            stderr = _cam_mux_proc.stderr.read().decode(errors="replace")
            print(f"[CAM-MUX] ffmpeg exited immediately: {stderr[:500]}")
            _cam_mux_last_error = stderr.strip().splitlines()[-1][:300] if stderr.strip() else "ffmpeg exited"
            _cam_mux_proc = None
        return False


def cam_mux_last_error():
    """Why the last _start_cam_mux failed (ffmpeg's last stderr line)."""
    return _cam_mux_last_error


def _stop_cam_mux():
    """Stop ffmpeg camera multiplexer."""
    global _cam_mux_proc, _cam_mux_count
    with _cam_mux_lock:
        if _cam_mux_proc and _cam_mux_proc.poll() is None:
            _cam_mux_proc.terminate()
            try: _cam_mux_proc.wait(timeout=3)
            except Exception: _cam_mux_proc.kill()
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
        # If that display already has an X server (left by an earlier run, or another studio), use it rather than
        # kill it: a `pkill -f 'Xvfb :99'` would also kill ':990' or someone else's Xvfb. It runs with -ac, so drawing works.
        if _xcb_conn(display) is not None:
            _xvfb_procs.pop(slot_idx, None)
            return
        p = subprocess.Popen(
            ["Xvfb", display, "-screen", "0", _XVFB_RES, "-ac"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        _xvfb_procs[slot_idx] = p
        print(f"[LIVE] Xvfb started on {display} PID={p.pid}")


def stop_xvfb(slot_idx):
    """Stop only the Xvfb of a slot this server started (displays started by others are left alone). The next run restarts it (about 1 s)."""
    with _xvfb_lock:
        p = _xvfb_procs.pop(slot_idx, None)
    conn = _xcb_conns.pop(f":{_XVFB_BASE + slot_idx}", None)
    if conn is not None and _XCB:
        try:
            _XCB.xcb_disconnect(conn[0])
        except Exception:
            pass
    if p is not None and p.poll() is None:
        p.terminate()
        try:
            p.wait(timeout=3)
        except Exception:
            p.kill()


# ── Live view: fit the window, crop the Qt frame (contract: tests/dx_app/test_live_display.py) ──────────────
# dx_app's C++ runner opens an OpenCV (Qt) window at its default size (400x300). Xvfb has no window manager, so it
# stays small in the top-left corner and a full-screen grab is mostly black. The window is stretched to the screen,
# and the Qt toolbar, status bar and aspect padding (gray) are cut from the grab. libX11 via ctypes, no new dependency (the screen is grabbed with libxcb, `_grab_screen`).
_LIVE_FRAME_MAX = (960, 540)
_QT_CHROME = (239, 239, 239)
_FIT_EVERY_S = 1.0
_BOX_EVERY_S = 2.0
_live_view = {}              # slot_idx -> {"fit_at": t, "box": (..)|None, "box_at": t}
_XLIB = None


def _load_lib(soname, short):
    """Open by soname first, since find_library spawns ldconfig and gcc. Fall back to find_library."""
    import ctypes
    try:
        return ctypes.cdll.LoadLibrary(soname)
    except OSError:
        pass
    import ctypes.util
    name = ctypes.util.find_library(short)
    try:
        return ctypes.cdll.LoadLibrary(name) if name else None
    except OSError:
        return None


def _xlib():
    """libX11 (ctypes), or None."""
    global _XLIB
    if _XLIB is not None:
        return _XLIB or None
    import ctypes
    x = _load_lib("libX11.so.6", "X11")
    if x is None:
        _XLIB = False
        return None
    P, W, I, U = ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_uint
    x.XOpenDisplay.restype, x.XOpenDisplay.argtypes = P, [ctypes.c_char_p]
    x.XCloseDisplay.argtypes = [P]
    x.XDefaultRootWindow.restype, x.XDefaultRootWindow.argtypes = W, [P]
    x.XQueryTree.argtypes = [P, W, ctypes.POINTER(W), ctypes.POINTER(W), ctypes.POINTER(ctypes.POINTER(W)), ctypes.POINTER(U)]
    x.XGetGeometry.argtypes = [P, W, ctypes.POINTER(W), ctypes.POINTER(I), ctypes.POINTER(I),
                               ctypes.POINTER(U), ctypes.POINTER(U), ctypes.POINTER(U), ctypes.POINTER(U)]
    x.XMoveResizeWindow.argtypes = [P, W, I, I, U, U]
    x.XCreateSimpleWindow.restype = W
    x.XCreateSimpleWindow.argtypes = [P, W, I, I, U, U, U, W, W]
    x.XMapWindow.argtypes = [P, W]
    x.XSync.argtypes = [P, I]
    x.XFlush.argtypes = [P]
    x.XFree.argtypes = [P]
    _XLIB = x
    return x


_ZPIXMAP = 2
_ALL_PLANES = 0xFFFFFFFF


_XCB = None
_xcb_conns = {}              # display -> (conn, root, width, height)


def _xcb():
    """libxcb + libc (ctypes), or None. Why xcb rather than Xlib: when the X server connection drops (Xvfb dies), Xlib's
    default IO error handler exits the process, taking the whole dx_app server down. xcb just returns an error."""
    global _XCB
    if _XCB is not None:
        return _XCB or None
    import ctypes
    x, libc = _load_lib("libxcb.so.1", "xcb"), _load_lib("libc.so.6", "c")
    if x is None or libc is None:
        _XCB = False
        return None
    P, I, U8, U16, U32 = ctypes.c_void_p, ctypes.c_int, ctypes.c_uint8, ctypes.c_uint16, ctypes.c_uint32

    class Cookie(ctypes.Structure):
        _fields_ = [("sequence", ctypes.c_uint)]

    class ScreenIter(ctypes.Structure):
        _fields_ = [("data", P), ("rem", I), ("index", I)]

    x.xcb_connect.restype, x.xcb_connect.argtypes = P, [ctypes.c_char_p, ctypes.POINTER(I)]
    x.xcb_connection_has_error.restype, x.xcb_connection_has_error.argtypes = I, [P]
    x.xcb_disconnect.argtypes = [P]
    x.xcb_get_setup.restype, x.xcb_get_setup.argtypes = P, [P]
    x.xcb_setup_roots_iterator.restype, x.xcb_setup_roots_iterator.argtypes = ScreenIter, [P]
    x.xcb_screen_next.argtypes = [ctypes.POINTER(ScreenIter)]
    x.xcb_get_image.restype = Cookie
    x.xcb_get_image.argtypes = [P, U8, U32, ctypes.c_int16, ctypes.c_int16, U16, U16, U32]
    x.xcb_get_image_reply.restype = P
    x.xcb_get_image_reply.argtypes = [P, Cookie, ctypes.POINTER(P)]
    x.xcb_get_image_data.restype, x.xcb_get_image_data.argtypes = ctypes.POINTER(ctypes.c_ubyte), [P]
    x.xcb_get_image_data_length.restype, x.xcb_get_image_data_length.argtypes = I, [P]
    libc.free.argtypes = [P]
    x._libc = libc
    _XCB = x
    return x


def _xcb_conn(display):
    """(conn, root, width, height) for the display. Reuses the connection and reconnects if it dropped."""
    import ctypes
    x = _xcb()
    if x is None:
        return None
    cached = _xcb_conns.get(display)
    if cached and not x.xcb_connection_has_error(cached[0]):
        return cached
    if cached:
        x.xcb_disconnect(cached[0])
        _xcb_conns.pop(display, None)
    num = ctypes.c_int(0)
    conn = x.xcb_connect(display.encode(), ctypes.byref(num))
    if not conn or x.xcb_connection_has_error(conn):
        if conn:
            x.xcb_disconnect(conn)
        return None
    it = x.xcb_setup_roots_iterator(x.xcb_get_setup(conn))
    for _ in range(num.value):
        x.xcb_screen_next(ctypes.byref(it))
    if not it.data:
        x.xcb_disconnect(conn)
        return None
    # xcb_screen_t: root (u32) · colormap · white · black · input masks (u32 ×4) · width (u16) · height (u16)
    root = ctypes.c_uint32.from_address(it.data).value
    width = ctypes.c_uint16.from_address(it.data + 20).value
    height = ctypes.c_uint16.from_address(it.data + 22).value
    _xcb_conns[display] = (conn, root, width, height)
    return _xcb_conns[display]


def _grab_screen(display):
    """Grab the display's whole root window as a PIL RGB image (xcb_get_image). None on failure.

    Not mss: mss is not a declared dependency, so live view would fail on a freshly installed board
    (contract: tests/dx_app/test_live_grab.py). Xvfb is 24-bit TrueColor, 32bpp, little-endian, so BGRX is read as is.
    The caller (capture_live_frame) holds _display_env_lock, so the connection is never used concurrently."""
    import ctypes
    from PIL import Image
    x = _xcb()
    c = _xcb_conn(display) if x is not None else None
    if c is None:
        return None
    conn, root, w, h = c
    err = ctypes.c_void_p()
    reply = x.xcb_get_image_reply(conn, x.xcb_get_image(conn, _ZPIXMAP, root, 0, 0, w, h, _ALL_PLANES),
                                  ctypes.byref(err))
    if err.value:
        x._libc.free(err)
    if not reply:
        return None
    try:
        n = x.xcb_get_image_data_length(reply)
        if n != w * h * 4:
            return None
        raw = ctypes.string_at(x.xcb_get_image_data(reply), n)
    finally:
        x._libc.free(reply)
    return Image.frombuffer("RGB", (w, h), raw, "raw", "BGRX", w * 4, 1)


def _fit_windows(display, width, height):
    """Move the display's top-level windows to (0, 0, width, height). Returns how many windows have that size."""
    import ctypes
    x = _xlib()
    if x is None:
        return 0
    d = x.XOpenDisplay(display.encode())
    if not d:
        return 0
    fitted = 0
    try:
        root, parent = ctypes.c_ulong(), ctypes.c_ulong()
        children, n = ctypes.POINTER(ctypes.c_ulong)(), ctypes.c_uint()
        if not x.XQueryTree(d, x.XDefaultRootWindow(d), ctypes.byref(root), ctypes.byref(parent),
                            ctypes.byref(children), ctypes.byref(n)):
            return 0
        wins = [children[i] for i in range(n.value)]
        if n.value:
            x.XFree(children)
        gx, gy = ctypes.c_int(), ctypes.c_int()
        gw, gh, bw, depth = ctypes.c_uint(), ctypes.c_uint(), ctypes.c_uint(), ctypes.c_uint()
        for w in wins:
            if not x.XGetGeometry(d, w, ctypes.byref(root), ctypes.byref(gx), ctypes.byref(gy),
                                  ctypes.byref(gw), ctypes.byref(gh), ctypes.byref(bw), ctypes.byref(depth)):
                continue
            if (gx.value, gy.value, gw.value, gh.value) != (0, 0, width, height):
                x.XMoveResizeWindow(d, w, 0, 0, width, height)
            fitted += 1
        x.XFlush(d)
    finally:
        x.XCloseDisplay(d)
    return fitted


def _is_chrome(px):
    return all(abs(c - q) <= 3 for c, q in zip(px, _QT_CHROME))


def _content_box(img):
    """Video area (x0, y0, x1, y1) without the Qt window's gray frame (toolbar, status bar, aspect padding). None if no frame.
    Trims inward from the edges only, so a light gray line in the middle of the video is left alone."""
    W, H = img.size
    step = max(1, min(W, H) // 180)
    from PIL import Image
    # nearest: blending would make the column between frame and video neither gray nor video
    small = img.convert("RGB").resize((max(1, W // step), max(1, H // step)), Image.Resampling.NEAREST)
    sw, sh = small.size
    px = small.load()

    # Side padding first (whole column nearly gray): for portrait video the padding exceeds half the screen, so rows cannot split it.
    # Then the top and bottom rows inside the video columns (toolbar text rows are close to half gray, video rows near 0).
    def chrome_col(x):
        return sum(_is_chrome(px[x, y]) for y in range(sh)) > 0.6 * sh

    x0 = 0
    while x0 < sw and chrome_col(x0):
        x0 += 1
    x1 = sw
    while x1 > x0 and chrome_col(x1 - 1):
        x1 -= 1
    if x1 - x0 < sw * 0.1:
        return None

    def chrome_row(y):
        return sum(_is_chrome(px[x, y]) for x in range(x0, x1)) > 0.2 * (x1 - x0)

    y0 = 0
    while y0 < sh and chrome_row(y0):
        y0 += 1
    y1 = sh
    while y1 > y0 and chrome_row(y1 - 1):
        y1 -= 1
    if y1 - y0 < sh * 0.1:
        return None
    if (x0, y0, x1, y1) == (0, 0, sw, sh):
        return None
    return (x0 * step, y0 * step, min(W, x1 * step), min(H, y1 * step))


def _frame_jpeg(img, box=None):
    """Grabbed screen -> video area only, scaled with aspect ratio to fit _LIVE_FRAME_MAX, as JPEG."""
    from PIL import Image
    if box is None:
        box = _content_box(img)
    if box:
        img = img.crop(box)
    img = img.convert("RGB")
    img.thumbnail(_LIVE_FRAME_MAX, Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    return buf.getvalue()


_display_env_lock = threading.Lock()   # global lock for DISPLAY env changes

def capture_live_frame(slot_idx=0):
    """Capture per-slot Xvfb screen as JPEG bytes (thread-safe)."""
    display = f":{_XVFB_BASE + slot_idx}"
    with _display_env_lock:
        old_display = os.environ.get("DISPLAY")
        os.environ["DISPLAY"] = display
        try:
            view = _live_view.setdefault(slot_idx, {"fit_at": 0.0, "box": None, "box_at": 0.0})
            now = time.time()
            if now - view["fit_at"] >= _FIT_EVERY_S:
                view["fit_at"] = now
                w, h = (int(v) for v in _XVFB_RES.split("x")[:2])
                _fit_windows(display, w, h)
            pil = _grab_screen(display)
            if pil is None:
                return None
            # The first grab right after stretching still shows the small window; if no video area was found, look again soon
            if now - view["box_at"] >= (_BOX_EVERY_S if view["box"] else 0.5):
                view["box_at"] = now
                view["box"] = _content_box(pil)
            return _frame_jpeg(pil, view["box"] or (0, 0, pil.width, pil.height))
        except Exception as e:
            print(f"[LIVE] Capture error slot={slot_idx}: {e}")
            return None
        finally:
            if old_display is not None:
                os.environ["DISPLAY"] = old_display
            else:
                os.environ.pop("DISPLAY", None)
