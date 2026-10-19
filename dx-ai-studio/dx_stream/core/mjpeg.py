"""MJPEG streaming through a subprocess.

gst-launch-1.0 runs as its own process and writes JPEG frames to a stdout pipe,
so a GStreamer crash cannot take the server down.
The browser reads it with <img src="/api/stream/mjpeg"> or fetch.
"""
from __future__ import annotations

import logging
import os
import signal
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional

from dx_stream.core import gst_env

log = logging.getLogger(__name__)

# Shared buffer holding the latest JPEG frame
_frame_lock = threading.Lock()
_latest_frame: Optional[bytes] = None
_frame_event = threading.Event()
_streaming = False
_process: Optional[subprocess.Popen] = None
_reader_thread: Optional[threading.Thread] = None
_pipeline_cmd: Optional[list] = None
_pipeline_env: Optional[dict] = None
_last_error: str = ""
_frame_count = 0


def _drain_dxrt_msgqueues():
    """Best-effort cleanup for stale dxrtd IPC messages before launching GStreamer."""
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


_JPEG_ENCODER = None


def _jpeg_encoder() -> str:
    """Encoder segment for the MJPEG sink (goes after 'videoconvert ! videoscale !').

    Prefer the Rockchip HW JPEG encoder (mppjpegenc) — far cheaper than software jpegenc on
    ARM, which is the bottleneck for remote viewing. The earlier corruption was NOT the HW
    encoder itself but an unconstrained input format: pinning 'video/x-raw,format=NV12' before
    mppjpegenc yields clean, decodable JPEGs (verified via gst-launch + PIL). Fall back to
    software jpegenc where mppjpegenc isn't available. Cached."""
    global _JPEG_ENCODER
    if _JPEG_ENCODER is None:
        try:
            r = subprocess.run(["gst-inspect-1.0", "mppjpegenc"],
                               capture_output=True, timeout=8)
            _JPEG_ENCODER = ("video/x-raw,format=NV12 ! mppjpegenc"
                             if r.returncode == 0 else "jpegenc quality=80")
        except Exception:
            _JPEG_ENCODER = "jpegenc quality=80"
    return _JPEG_ENCODER


def build_mjpeg_pipeline(base_pipeline: str) -> str:
    """Rewrite a pipeline to end in MJPEG output instead of webrtcbin/fpsdisplaysink.

    Multi-stream (compositor) pipeline: replace the sink after the compositor output.
    Single stream: replace everything after the last dxosd.
    Returns the pipeline string to pass to gst-launch-1.0.
    """
    mjpeg_sink = (
        # NOTE: a forced "video/x-raw,width=1280,height=720" caps here segfaults the
        # pipeline (SIGSEGV) on the dxosd→videoscale path; leave videoscale uncapped so
        # the encoder emits at the native frame size (the browser viewer scales it).
        "videoconvert ! videoscale ! "
        f"{_jpeg_encoder()} ! fdsink fd=1"
    )

    # Multi-stream: replace the sink after the compositor
    comp_idx = base_pipeline.find("compositor")
    if comp_idx >= 0:
        # Find where the compositor block ends in "compositor name=comp ... ! videoconvert ! ..."
        after_comp = base_pipeline.find("!", comp_idx)
        if after_comp >= 0:
            # The compositor's properties (sink_0::xpos=... etc.) run up to the next '!'
            # Drop the sink part of the rest and append the MJPEG sink
            comp_block = base_pipeline[:after_comp].rstrip()
            return f"{comp_block} ! {mjpeg_sink}"
        return base_pipeline.rstrip() + f" ! {mjpeg_sink}"

    # Single stream: replace everything after the last dxosd with MJPEG
    idx = base_pipeline.rfind("dxosd")
    if idx >= 0:
        base = base_pipeline[:idx] + "dxosd"
    else:
        markers = ["videoconvert ! vp8enc", "videoconvert ! x264enc",
                   "videoconvert ! fpsdisplaysink", "videoconvert ! vaapih264enc",
                   "webrtcbin"]
        cut_point = -1
        for marker in markers:
            pos = base_pipeline.find(marker)
            if pos >= 0:
                cut_point = pos
                break
        if cut_point > 0:
            base = base_pipeline[:cut_point].rstrip().rstrip("!")
        else:
            base = base_pipeline.rstrip()

    base = base.rstrip().rstrip("!").rstrip()
    return f"{base} ! {mjpeg_sink}"


def get_sink_str() -> str:
    """The MJPEG sink string appended to the pipeline (for gst-launch-1.0)."""
    return (
        # NOTE: a forced "video/x-raw,width=1280,height=720" caps here segfaults the
        # pipeline (SIGSEGV) on the dxosd→videoscale path; leave videoscale uncapped so
        # jpegenc encodes at the native frame size (the browser viewer scales it).
        "videoconvert ! videoscale ! "
        "jpegenc quality=80 ! fdsink fd=1"
    )


def start(pipeline_str: str, extra_env: Optional[dict] = None):
    """Start the pipeline as a gst-launch-1.0 subprocess.

    JPEG frames arrive on stdout; a separate thread reads them into _latest_frame.
    On EOS (end of file) the pipeline restarts, so playback loops forever.
    """
    global _streaming, _process, _reader_thread, _pipeline_cmd, _pipeline_env, _latest_frame, _last_error, _frame_count

    stop()  # stop the previous run
    _drain_dxrt_msgqueues()

    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    env = gst_env.augmented_env(env)

    cmd = ["gst-launch-1.0", "-q"] + _split_pipeline(pipeline_str)
    _pipeline_cmd = cmd
    _pipeline_env = env
    _latest_frame = None
    _last_error = ""
    _frame_count = 0

    log.info("MJPEG subprocess 시작: %s", " ".join(cmd[:5]) + "...")

    _process = _spawn_process(cmd, env)
    _streaming = True
    _reader_thread = threading.Thread(target=_read_frames_loop, daemon=True)
    _reader_thread.start()
    log.info("MJPEG 스트리밍 시작 (PID %d)", _process.pid)


def stop():
    """Stop MJPEG streaming — end the subprocess.

    Always send **SIGINT (graceful)** first. gst-launch-1.0 catches SIGINT, pushes
    EOS and shuts down to the NULL state, so dxinfer releases its NPU inference
    task cleanly. Killing it outright with SIGTERM/SIGKILL makes the process vanish
    while holding the task, which **crashes the dxrtd daemon** (systemd restarts it);
    meanwhile the next pipeline start fails with "dxrt service is not running" /
    "Failed to initialize task on device".
    So escalate step by step: SIGINT → (if still alive) SIGTERM → SIGKILL.
    """
    global _streaming, _process, _latest_frame

    _streaming = False

    if _process is not None:
        try:
            pgid = os.getpgid(_process.pid)
        except (ProcessLookupError, OSError):
            pgid = None

        def _signal(sig):
            if pgid is None:
                return
            try:
                os.killpg(pgid, sig)
            except (ProcessLookupError, OSError):
                pass

        # 1) graceful: SIGINT → gst-launch EOS → dxinfer releases its NPU task
        _signal(signal.SIGINT)
        try:
            _process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # 2) escalation: SIGTERM
            _signal(signal.SIGTERM)
            try:
                _process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                # 3) last resort: SIGKILL (may crash dxrtd)
                _signal(signal.SIGKILL)
        _process = None
        log.info("MJPEG subprocess 종료")

    with _frame_lock:
        _latest_frame = None


def is_streaming() -> bool:
    return _streaming


def get_last_error() -> str:
    return _last_error


def get_frame_count() -> int:
    """Total JPEG frames produced since the current stream started. The client polls this
    to compute a reliable MJPEG FPS (counting <img> 'load' events is flaky for a multipart
    stream — the browser may fire 'load' once, not per frame)."""
    return _frame_count


def wait_until_ready(timeout: float = 2.0, require_frame: bool = False) -> tuple[bool, str]:
    """Return early if the MJPEG subprocess exits before producing frames."""
    global _streaming, _last_error
    deadline = time.time() + timeout
    while time.time() < deadline:
        with _frame_lock:
            if _latest_frame is not None:
                return True, ""
        proc = _process
        if proc is None:
            _last_error = "MJPEG process is not running"
            _streaming = False
            return False, _last_error
        code = proc.poll()
        if code is not None:
            if code == 0 and _frame_count > 0:
                return True, ""
            stderr = _read_stderr(proc)
            _last_error = stderr or f"MJPEG pipeline exited with code {code}"
            _streaming = False
            return False, _last_error
        time.sleep(0.05)
    if require_frame:
        _last_error = f"No MJPEG frame produced within {timeout:.1f}s"
        _streaming = False
        return False, _last_error
    return True, ""


def generate_frames():
    """MJPEG frame generator for the HTTP multipart/x-mixed-replace response.

    Frames are throttled to a minimum gap (33 ms ≈ 30 fps) so the
    single-threaded HTTP server is not overloaded.
    """
    boundary = b"--frame\r\n"
    min_interval = 0.033  # ~30fps cap
    last_send = 0.0

    while is_streaming():
        _frame_event.wait(timeout=2.0)
        _frame_event.clear()

        now = time.time()
        if now - last_send < min_interval:
            continue

        with _frame_lock:
            frame = _latest_frame

        if frame is None:
            continue

        last_send = now
        yield (
            boundary
            + b"Content-Type: image/jpeg\r\n"
            + f"Content-Length: {len(frame)}\r\n".encode()
            + b"\r\n"
            + frame
            + b"\r\n"
        )


def get_latest_frame() -> Optional[bytes]:
    """The latest JPEG frame (for snapshots)."""
    with _frame_lock:
        return _latest_frame


def _spawn_process(cmd, env):
    """Spawn the gst-launch-1.0 subprocess.

    CWD is DX_STREAM_ROOT so relative paths inside the config JSON
    (e.g. ./dx_stream/samples/models/…) resolve correctly.
    """
    from dx_stream.core.config import DX_STREAM_ROOT

    try:
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=str(DX_STREAM_ROOT),
            preexec_fn=os.setsid,
        )
    except FileNotFoundError:
        raise RuntimeError("gst-launch-1.0 not found")


def _read_frames_loop():
    """Thread that reads JPEG frames and restarts the pipeline on EOS."""
    global _process, _latest_frame, _streaming, _last_error

    while _streaming:
        proc = _process
        if proc is None or proc.stdout is None:
            time.sleep(0.5)
            continue

        _read_frames_from(proc)

        # Has the process exited?
        if not _streaming:
            break
        code = proc.poll()
        if code not in (None, 0):
            if not _last_error:
                _last_error = _read_stderr(proc) or f"MJPEG pipeline exited with code {code}"
            _streaming = False
            log.error("MJPEG pipeline failed: %s", _last_error)
            break

        # EOS — restart after 0.5 s
        log.info("MJPEG pipeline EOS — 재시작")
        time.sleep(0.5)
        if not _streaming:
            break
        try:
            _process = _spawn_process(_pipeline_cmd, _pipeline_env)
            log.info("MJPEG subprocess 재시작 (PID %d)", _process.pid)
        except Exception as e:
            log.error("MJPEG 재시작 실패: %s", e)
            break

    log.info("MJPEG reader loop 종료")


def _read_frames_from(proc):
    """Read JPEG frames from one subprocess."""
    global _latest_frame, _frame_count

    buffer = bytearray()
    SOI = b"\xff\xd8"  # Start of Image
    EOI = b"\xff\xd9"  # End of Image

    try:
        while _streaming and proc.poll() is None:
            chunk = proc.stdout.read(65536)
            if not chunk:
                break
            buffer.extend(chunk)

            # Extract JPEG frames (SOI...EOI)
            while True:
                soi_pos = buffer.find(SOI)
                if soi_pos < 0:
                    buffer.clear()
                    break
                eoi_pos = buffer.find(EOI, soi_pos + 2)
                if eoi_pos < 0:
                    if soi_pos > 0:
                        del buffer[:soi_pos]
                    break
                frame = bytes(buffer[soi_pos:eoi_pos + 2])
                del buffer[:eoi_pos + 2]

                with _frame_lock:
                    _latest_frame = frame
                    _frame_count += 1
                _frame_event.set()
    except Exception as e:
        log.error("MJPEG reader 에러: %s", e)


def _read_stderr(proc) -> str:
    stream = getattr(proc, "stderr", None)
    if stream is None:
        return ""
    try:
        data = stream.read()
    except Exception:
        return ""
    if isinstance(data, bytes):
        return data.decode(errors="replace").strip()
    return str(data or "").strip()


def _split_pipeline(pipeline_str: str) -> list:
    """Split a pipeline string into gst-launch-1.0 arguments.

    gst-launch-1.0 needs each '!' as its own argument.
    """
    # shell-like splitting respecting spaces within element properties
    import shlex
    # Make sure '!' has spaces around it
    normalized = pipeline_str.replace("!", " ! ")
    return shlex.split(normalized)
