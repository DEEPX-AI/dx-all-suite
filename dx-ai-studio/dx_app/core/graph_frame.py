"""One frame of a graph input, for drawing zones and lines on it: the image itself, or a video's first frame.

The page asks with the source's uri (or the input picked for the run) and gets a JPEG data URL no wider than
MAX_WIDTH plus the frame's real size, which pixel coordinates are measured in. Inputs resolve under the same roots
as a run (graph_run.input_roots); a camera or RTSP source has no file to read and says so (`live_source`).
A video frame needs ffmpeg. An input larger than MAX_IMAGE_BYTES / MAX_VIDEO_BYTES, or an image declaring more than
MAX_PIXELS pixels (checked from its header, before it is decoded), is refused (`frame_too_large`).

inspect() is the results view's "Layers for this frame": a paused result video's frame is taken from the run's own
input (ffmpeg, at that time; every other video source at the same time, an image as it is) and the run's graph runs
once on it with --output-layers, through graph_run.start (so it takes the NPU like any run, or is refused while
another job holds it), and the stream's output comes back with its base and per-node layer URLs.
Contract: tests/dx_app/test_graph_frame.py
"""
from __future__ import annotations

import base64
import io
import json
import re
import shutil
import subprocess

from dx_app.core import graph_cli, graph_run

MAX_WIDTH = 1280
MAX_IMAGE_BYTES = 40 * 1024 * 1024
MAX_VIDEO_BYTES = 200 * 1024 * 1024
# Below Pillow's own decompression-bomb limit (~89 MP, process-wide); checked here so that limit is left alone
MAX_PIXELS = 50_000_000
_JPEG_QUALITY = 85
# How long a "Layers for this frame" run may take before it is stopped (models load before the one frame runs)
INSPECT_TIMEOUT = 180.0
_RUN_ID = re.compile(r"^[0-9a-f]{32}$")


class _TooLarge(Exception):
    pass


def _decode(data: bytes):
    from PIL import Image
    img = Image.open(io.BytesIO(data))
    width, height = img.size
    if width * height > MAX_PIXELS:
        raise _TooLarge(f"the image is {width}x{height}; at most {MAX_PIXELS // 1_000_000} million pixels are shown")
    img.load()
    return img


def _video_frame(path) -> bytes:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is needed to read a video frame")
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(path), "-frames:v", "1", "-f", "image2pipe",
                        "-vcodec", "png", "-"], stdin=subprocess.DEVNULL, capture_output=True, timeout=30)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError((r.stderr or b"").decode("utf-8", "replace").strip()[-300:] or "no frame")
    return r.stdout


def first_frame(uri) -> tuple:
    """({"image": data URL, "width", "height", "uri"}, 200) or ({"error", "error_key"}, status)."""
    try:
        path = graph_run._resolve_uri(uri)
    except ValueError as e:
        if str(e) == "live_source":
            return {"error": "a camera or RTSP source has no file to show", "error_key": "live_source"}, 409
        return {"error": str(e), "error_key": "invalid_input"}, 400
    video = path.suffix.lower() in graph_run._VIDEO_EXT
    limit = MAX_VIDEO_BYTES if video else MAX_IMAGE_BYTES
    try:
        size = path.stat().st_size
        if size > limit:
            return {"error": f"the file is {size / 1048576:.0f} MB; a {'video' if video else 'image'} up to "
                             f"{limit // 1048576} MB is shown", "error_key": "frame_too_large"}, 413
        img = _decode(_video_frame(path) if video else path.read_bytes())
    except _TooLarge as e:
        return {"error": str(e), "error_key": "frame_too_large"}, 413
    except (OSError, RuntimeError, subprocess.SubprocessError) as e:
        return {"error": str(e), "error_key": "frame_unreadable"}, 422
    except Exception as e:                      # PIL raises its own types for a file that is not an image
        return {"error": f"not an image: {e}", "error_key": "frame_unreadable"}, 422
    width, height = img.size
    img = img.convert("RGB")
    if width > MAX_WIDTH:
        img = img.resize((MAX_WIDTH, max(1, round(height * MAX_WIDTH / width))))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=_JPEG_QUALITY)
    return {"image": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii"),
            "width": width, "height": height, "uri": uri}, 200


def _frame_png(path, t: float) -> bytes:
    """The frame of a video shown at `t` seconds, as PNG bytes (ffmpeg seeks, then decodes to that frame)."""
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is needed to read a video frame")
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1",
                        "-f", "image2pipe", "-vcodec", "png", "-"], stdin=subprocess.DEVNULL, capture_output=True,
                       timeout=60)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError((r.stderr or b"").decode("utf-8", "replace").strip()[-300:] or f"no frame at {t:g} s")
    return r.stdout


def _bad(what, key="invalid_payload", code=400) -> tuple:
    return {"error": what, "error_key": key}, code


def _at(data) -> tuple:
    """(time_s, frame) of a frame request, one of them None; ValueError when neither is a number >= 0."""
    t, fr = data.get("time_s"), data.get("frame")
    if t is not None:
        if isinstance(t, bool) or not isinstance(t, (int, float)) or not 0 <= t < 1e7:
            raise ValueError("time_s must be a number of seconds, 0 or more")
        return float(t), None
    if fr is not None:
        if isinstance(fr, bool) or not isinstance(fr, int) or not 0 <= fr < 10 ** 9:
            raise ValueError("frame must be a whole number, 0 or more")
        return None, fr
    raise ValueError("time_s or frame is required")


def inspect(data) -> tuple:
    """Run a graph once on one frame with its layers. `data`: {"run_id"} (a run once; its run.json gives the graph
    and the inputs) or {"graph", "inputs", "variant"}, plus "stream" (a source id) and "time_s" or "frame" (an
    index, taken at the middle of that frame of the stream's video). Returns ({"ok", "run_id", "stream", "time_s",
    "output": {url, kind, name, stream, layers}, "errors", "exit_code"}, 200) or ({"error", "error_key"}, status)."""
    if not isinstance(data, dict):
        return _bad("the request must be an object")
    run_id = data.get("run_id")
    if run_id is not None:
        if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
            return _bad("run_id must be a run's id")
        try:
            saved = json.loads((graph_run.runs_dir() / run_id / "run.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return _bad("that run's folder is gone; run the graph again", "run_gone", 404)
        graph, inputs, variant = saved.get("graph"), saved.get("inputs"), saved.get("variant") or "sync"
    else:
        graph, inputs, variant = data.get("graph"), data.get("inputs"), data.get("variant") or "sync"
    if not isinstance(graph, dict) or not isinstance(graph.get("nodes"), list):
        return _bad("run_id or a graph is required")
    if inputs is not None and not isinstance(inputs, dict):
        return _bad("inputs must be an object")
    inputs = inputs or {}
    sources = [n for n in graph["nodes"] if isinstance(n, dict) and n.get("type") == "source"]
    stream = data.get("stream")
    if not isinstance(stream, str) or stream not in [s.get("id") for s in sources]:
        return _bad(f"stream must be one of the graph's sources, not {stream!r}", "invalid_stream")
    try:
        t, fr = _at(data)
    except ValueError as e:
        return _bad(str(e))
    if not graph_cli.capabilities().get("output_layers"):
        return _bad("this dx_app build cannot write layers (no --output-layers)", "layers_unsupported", 409)
    paths = {}
    for s in sources:
        try:
            paths[s["id"]] = graph_run._resolve_uri(inputs.get(s["id"]) or s.get("uri"))
        except ValueError as e:
            if str(e) == "live_source":
                return _bad("a camera or RTSP source has no frame to take again", "live_source")
            return _bad(str(e), "invalid_input")
    videos = [sid for sid, p in paths.items() if p.suffix.lower() in graph_run._VIDEO_EXT]
    if t is None:
        vid = stream if stream in videos else (videos[0] if videos else None)
        fps = graph_run.video_fps(paths[vid]) if vid else None
        if not fps:
            return _bad("the video's frame rate is unknown; ask by time_s", "frame_unreadable", 422)
        t = round((fr + 0.5) / fps, 3)
    files = {}
    try:
        for sid in videos:
            files[sid] = _frame_png(paths[sid], t)
    except (OSError, RuntimeError, subprocess.SubprocessError) as e:
        return _bad(str(e), "frame_unreadable", 422)
    body, code = graph_run.start(graph, variant=variant, frame_files=files,
                                 inputs={sid: str(p) for sid, p in paths.items() if sid not in files})
    if code != 200:
        return body, code
    r = graph_run.wait(body["job_id"], INSPECT_TIMEOUT)
    out = next((o for o in r.get("outputs") or [] if o.get("stream") == stream), None)
    return {"ok": bool(r.get("ok")) and out is not None and "layers" in out, "run_id": body["job_id"],
            "stream": stream, "time_s": t, "output": out, "errors": r.get("errors") or [],
            "exit_code": r.get("exit_code"), "log_tail": (r.get("log_tail") or "")[-2000:]}, 200
