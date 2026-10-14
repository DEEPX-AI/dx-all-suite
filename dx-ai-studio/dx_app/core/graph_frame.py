"""One frame of a graph input, for drawing zones and lines on it: the image itself, or a video's first frame.

The page asks with the source's uri (or the input picked for the run) and gets a JPEG data URL no wider than
MAX_WIDTH plus the frame's real size, which pixel coordinates are measured in. Inputs resolve under the same roots
as a run (graph_run.input_roots); a camera or RTSP source has no file to read and says so (`live_source`).
A video frame needs ffmpeg. Contract: tests/dx_app/test_graph_frame.py
"""
from __future__ import annotations

import base64
import io
import shutil
import subprocess

from dx_app.core import graph_run

MAX_WIDTH = 1280
_JPEG_QUALITY = 85


def _decode(data: bytes):
    from PIL import Image
    img = Image.open(io.BytesIO(data))
    img.load()
    return img


def _video_frame(path) -> bytes:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is needed to read a video frame")
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-frames:v", "1", "-f", "image2pipe",
                        "-vcodec", "png", "-"], capture_output=True, timeout=30)
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
    try:
        raw = _video_frame(path) if path.suffix.lower() in graph_run._VIDEO_EXT else path.read_bytes()
        img = _decode(raw)
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
