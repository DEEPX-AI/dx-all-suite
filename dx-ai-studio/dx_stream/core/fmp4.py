"""Fragmented-MP4 (H264) streaming over HTTP — for remote viewers behind an SSH tunnel/NAT.

WebRTC's media is peer-to-peer UDP and can't cross a VSCode/SSH port-forward (only the HTTP
port is tunneled). MJPEG *does* ride the HTTP port but has no inter-frame compression, so 1080p
MJPEG is ~60 Mbps and saturates the tunnel (torn pixels, stalls). Fragmented MP4 carries HW-
encoded H264 (mpph264enc) over the same HTTP port at ~2-4 Mbps, which fits the tunnel and plays
in the browser via Media Source Extensions (MSE).

Architecture mirrors mjpeg.py: a gst-launch subprocess muxes
    ... ! mpph264enc ! h264parse ! mp4mux fragment-duration=N streamable=true ! fdsink fd=1
and this module parses the byte stream into MP4 boxes, caching the init segment (ftyp+moov) and
broadcasting each media fragment (moof+mdat) to connected HTTP clients. A late-joining client
gets the cached init first, then live fragments.
"""
from __future__ import annotations

import logging
import os
import queue
import signal
import struct
import subprocess
import threading
import time
from typing import Optional

from dx_stream.core import gst_env

log = logging.getLogger(__name__)

_streaming = False
_process: Optional[subprocess.Popen] = None
_reader_thread: Optional[threading.Thread] = None
_pipeline_cmd: Optional[list] = None
_pipeline_env: Optional[dict] = None
_last_error: str = ""

_state_lock = threading.Lock()
_init_segment: Optional[bytes] = None          # ftyp + moov (required by MSE before any fragment)
_subscribers: "list[queue.Queue]" = []         # one bounded queue per connected HTTP client
_fragment_count = 0

_MAX_QUEUE = 120  # per-client fragment backlog; drop oldest when a slow client falls behind


# ── HW encoder detection ─────────────────────────────────────────────────────
_H264_ENCODER = None


def _h264_encoder() -> str:
    """Prefer Rockchip HW H264 (mpph264enc, profile=baseline for broad browser decode), else
    software x264enc. Cached."""
    global _H264_ENCODER
    if _H264_ENCODER is None:
        try:
            r = subprocess.run(["gst-inspect-1.0", "mpph264enc"], capture_output=True, timeout=8)
            # bps caps the bitrate (~3 Mbps) so the stream comfortably fits an SSH tunnel — the
            # whole point of this path. gop=30 keeps keyframes frequent enough for a fast MSE start.
            _H264_ENCODER = ("mpph264enc profile=baseline bps=3000000 gop=30" if r.returncode == 0
                             else "x264enc tune=zerolatency speed-preset=ultrafast bitrate=3000 key-int-max=30")
        except Exception:
            _H264_ENCODER = "x264enc tune=zerolatency speed-preset=ultrafast bitrate=3000 key-int-max=30"
    return _H264_ENCODER


def get_sink_str() -> str:
    """fMP4 sink appended to a pipeline (H264 → fragmented MP4 on stdout).

    fragment-duration keeps fragments short (~200ms) for low latency; streamable=true emits a
    moov suitable for progressive/streaming consumption. h264parse with config-interval feeds
    SPS/PPS into the moov. No width/height caps here — that SIGSEGVs the dxosd→videoscale path
    (see mjpeg.get_sink_str); H264 inter-frame compression keeps the native size cheap anyway."""
    return (
        f"videoconvert ! {_h264_encoder()} ! h264parse config-interval=-1 ! "
        "mp4mux fragment-duration=200 streamable=true ! fdsink fd=1"
    )


def build_fmp4_pipeline(base_pipeline: str) -> str:
    """Replace a demo pipeline's webrtcbin/fpsdisplaysink sink with the fMP4 sink.

    Mirrors mjpeg.build_mjpeg_pipeline: for multi-stream (compositor) pipelines cut after the
    compositor block; for single-stream cut after the last dxosd.
    """
    sink = get_sink_str()

    comp_idx = base_pipeline.find("compositor")
    if comp_idx >= 0:
        after_comp = base_pipeline.find("!", comp_idx)
        if after_comp >= 0:
            comp_block = base_pipeline[:after_comp].rstrip()
            return f"{comp_block} ! {sink}"

    # single stream: keep everything up to and including the last dxosd, replace the rest
    cut_point = -1
    for marker in ("dxosd", "dxpostprocess"):
        pos = base_pipeline.rfind(marker)
        if pos >= 0:
            nxt = base_pipeline.find("!", pos)
            if nxt >= 0:
                cut_point = max(cut_point, nxt)
    if cut_point > 0:
        base = base_pipeline[:cut_point].rstrip().rstrip("!")
    else:
        base = base_pipeline.rstrip()
    base = base.rstrip().rstrip("!").rstrip()
    return f"{base} ! {sink}"


# ── lifecycle ────────────────────────────────────────────────────────────────
def start(pipeline_str: str, extra_env: Optional[dict] = None):
    """Start the fMP4 subprocess. H264 fragments stream to stdout; a reader thread parses boxes."""
    global _streaming, _process, _reader_thread, _pipeline_cmd, _pipeline_env
    global _init_segment, _last_error, _fragment_count

    stop()

    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    env = gst_env.augmented_env(env)

    cmd = ["gst-launch-1.0", "-q"] + _split_pipeline(pipeline_str)
    _pipeline_cmd = cmd
    _pipeline_env = env
    with _state_lock:
        _init_segment = None
    _last_error = ""
    _fragment_count = 0

    log.info("fMP4 subprocess 시작: %s", " ".join(cmd[:5]) + "...")
    _process = _spawn_process(cmd, env)
    _streaming = True
    _reader_thread = threading.Thread(target=_read_loop, daemon=True)
    _reader_thread.start()
    log.info("fMP4 스트리밍 시작 (PID %d)", _process.pid)


def stop():
    """Stop the subprocess. SIGINT first (graceful EOS → dxinfer returns its NPU task, avoiding a
    dxrtd crash), escalating to SIGTERM/SIGKILL — identical rationale to mjpeg.stop()."""
    global _streaming, _process, _init_segment

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

        _signal(signal.SIGINT)
        try:
            _process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _signal(signal.SIGTERM)
            try:
                _process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                _signal(signal.SIGKILL)
        _process = None
        log.info("fMP4 subprocess 종료")

    # wake any blocked subscribers so their generators can exit
    with _state_lock:
        _init_segment = None
        subs = list(_subscribers)
    for q in subs:
        try:
            q.put_nowait(None)
        except queue.Full:
            pass


def is_streaming() -> bool:
    return _streaming


def get_last_error() -> str:
    return _last_error


def get_fragment_count() -> int:
    """Total media fragments emitted since start (client polls /api/stream/stats for FPS-ish
    liveness; fragments are ~fragment-duration apart, not per-frame)."""
    return _fragment_count


def has_init() -> bool:
    with _state_lock:
        return _init_segment is not None


def wait_until_ready(timeout: float = 15.0) -> tuple[bool, str]:
    """Ready once the init segment is captured and at least one fragment has been emitted."""
    global _streaming, _last_error
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _init_segment is not None and _fragment_count > 0:
            return True, ""
        proc = _process
        if proc is None:
            _last_error = "fMP4 process is not running"
            _streaming = False
            return False, _last_error
        code = proc.poll()
        if code is not None and not (code == 0 and _fragment_count > 0):
            _last_error = _read_stderr(proc) or f"fMP4 pipeline exited with code {code}"
            _streaming = False
            return False, _last_error
        time.sleep(0.05)
    _last_error = f"No fMP4 fragment produced within {timeout:.1f}s"
    _streaming = False
    return False, _last_error


def generate():
    """Byte generator for an HTTP client: emit the init segment, then live fragments as they
    arrive. Registers a per-client queue so slow clients can't block the reader (oldest
    fragments are dropped for them instead)."""
    q: "queue.Queue" = queue.Queue(maxsize=_MAX_QUEUE)
    with _state_lock:
        init = _init_segment
        _subscribers.append(q)
    try:
        if init:
            yield init
        while is_streaming():
            try:
                frag = q.get(timeout=2.0)
            except queue.Empty:
                continue
            if frag is None:  # stop() sentinel
                break
            yield frag
    finally:
        with _state_lock:
            if q in _subscribers:
                _subscribers.remove(q)


# ── reader / box parser ──────────────────────────────────────────────────────
def _broadcast_fragment(frag: bytes):
    global _fragment_count
    with _state_lock:
        _fragment_count += 1
        subs = list(_subscribers)
    for q in subs:
        try:
            q.put_nowait(frag)
        except queue.Full:
            # slow client: drop its oldest fragment to make room (keep the stream live)
            try:
                q.get_nowait()
                q.put_nowait(frag)
            except (queue.Empty, queue.Full):
                pass


def _iter_boxes(buffer: bytearray):
    """Yield complete top-level MP4 boxes (type, raw_bytes) from the front of buffer, consuming
    them. Handles 32-bit and 64-bit (size==1) box sizes. Leaves incomplete tail in buffer."""
    while len(buffer) >= 8:
        size = struct.unpack(">I", buffer[0:4])[0]
        btype = bytes(buffer[4:8])
        header = 8
        if size == 1:
            if len(buffer) < 16:
                break
            size = struct.unpack(">Q", buffer[8:16])[0]
            header = 16
        elif size == 0:
            # box extends to EOF — can't happen mid-stream for streamable mp4mux; wait for more
            break
        if size < header or len(buffer) < size:
            break
        raw = bytes(buffer[:size])
        del buffer[:size]
        yield btype, raw


def _read_from(proc):
    """Parse the fMP4 byte stream from one subprocess: capture init (ftyp+moov), broadcast each
    fragment (…+moof+mdat). Re-captures init if the pipeline restarts (new ftyp)."""
    global _init_segment

    buffer = bytearray()
    building_init = True
    init_parts: "list[bytes]" = []
    frag_parts: "list[bytes]" = []

    while _streaming and proc.poll() is None:
        chunk = proc.stdout.read(65536)
        if not chunk:
            break
        buffer.extend(chunk)
        for btype, raw in _iter_boxes(buffer):
            if btype == b"ftyp":
                # (re)start of an init segment — flush any partial fragment, begin collecting init
                building_init = True
                init_parts = [raw]
                frag_parts = []
                continue
            if building_init and btype == b"moov":
                init_parts.append(raw)
                with _state_lock:
                    _init_segment = b"".join(init_parts)
                building_init = False
                continue
            if building_init:
                # unexpected box before moov (e.g. free) — keep it with init
                init_parts.append(raw)
                continue
            # fragment stream: styp?/moof/mdat …; a fragment completes at its mdat
            frag_parts.append(raw)
            if btype == b"mdat":
                _broadcast_fragment(b"".join(frag_parts))
                frag_parts = []


def _read_loop():
    """Reader thread: parse fragments; auto-restart on EOS (loop the sample video)."""
    global _process, _streaming, _last_error

    while _streaming:
        proc = _process
        if proc is None or proc.stdout is None:
            time.sleep(0.5)
            continue

        _read_from(proc)

        if not _streaming:
            break
        code = proc.poll()
        if code not in (None, 0):
            if not _last_error:
                _last_error = _read_stderr(proc) or f"fMP4 pipeline exited with code {code}"
            _streaming = False
            log.error("fMP4 pipeline failed: %s", _last_error)
            break

        log.info("fMP4 pipeline EOS — 재시작")
        time.sleep(0.5)
        if not _streaming:
            break
        try:
            _process = _spawn_process(_pipeline_cmd, _pipeline_env)
            log.info("fMP4 subprocess 재시작 (PID %d)", _process.pid)
        except Exception as e:
            log.error("fMP4 재시작 실패: %s", e)
            break

    log.info("fMP4 reader loop 종료")


# ── subprocess helpers (mirror mjpeg.py) ─────────────────────────────────────
def _spawn_process(cmd, env):
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


def _read_stderr(proc) -> str:
    try:
        if proc.stderr is not None:
            return proc.stderr.read(4096).decode("utf-8", "replace").strip()
    except Exception:
        pass
    return ""


def _split_pipeline(pipeline_str: str) -> list:
    import shlex
    normalized = pipeline_str.replace("!", " ! ")
    return shlex.split(normalized)
