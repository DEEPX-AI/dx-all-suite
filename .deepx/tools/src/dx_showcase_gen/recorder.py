"""Screen recording → timelapse GIF.

Records the REAL on-screen window (e.g. the claude TUI / build terminal) via
x11grab over the FULL screen, then post-crops to the window rect — this is robust
to gnome-terminal mapping off-screen, which broke direct cropped capture. The pure
helpers (crop clamping, speedup, ffmpeg arg builders) are unit-tested; the x11grab
side-effects are thin wrappers.

Hard-won gotchas baked in:
- keep the display awake (GNOME blanks :1 → black frames) via dbus + xset loop
- FULL-screen capture + post-crop (never a negative-offset direct crop)
- even crop dimensions (h264/gif require even W/H), clamped to the screen
- timelapse speedup so a ~10-20 min build becomes a ~20s GIF, kept < 10 MB
"""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from . import constants as C


# ----------------------------- pure helpers ------------------------------- #

@dataclass(frozen=True)
class Rect:
    w: int
    h: int
    x: int
    y: int


def clamp_crop(w: int, h: int, x: int, y: int,
               screen_w: int = C.SCREEN_W, screen_h: int = C.SCREEN_H) -> Rect:
    """Clamp a window rect to the screen and force even dimensions.

    x11grab/x264/gif require even width & height; negative offsets and
    out-of-screen extents must be trimmed or ffmpeg's crop filter fails.
    """
    x = max(0, int(x))
    y = max(0, int(y))
    w = max(2, int(w))
    h = max(2, int(h))
    if x + w > screen_w:
        w = screen_w - x
    if y + h > screen_h:
        h = screen_h - y
    w -= w % 2
    h -= h % 2
    return Rect(w=w, h=h, x=x, y=y)


def speedup_factor(duration_secs: float, target_secs: int = C.GIF_TARGET_SECS) -> int:
    """Integer setpts divisor so ``duration_secs`` compresses to ~target_secs."""
    if not duration_secs or duration_secs <= 0:
        return 1
    return max(1, int(duration_secs // max(1, target_secs)))


def gif_palette_args(src: str, palette: str, *, spf: int, fps: int,
                     width: int, colors: int) -> List[str]:
    """ffmpeg args to generate an optimal palette for the timelapse GIF."""
    vf = (f"setpts=PTS/{spf},fps={fps},scale={width}:-1:flags=lanczos,"
          f"palettegen=max_colors={colors}:stats_mode=full")
    return ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", src, "-vf", vf, palette]


def gif_encode_args(src: str, palette: str, out: str, *, spf: int, fps: int,
                    width: int) -> List[str]:
    """ffmpeg args to encode the timelapse GIF using the palette."""
    lavfi = (f"setpts=PTS/{spf},fps={fps},scale={width}:-1:flags=lanczos[x];"
             f"[x][1:v]paletteuse=dither=none")
    return ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", src, "-i", palette, "-lavfi", lavfi, out]


def crop_args(src: str, out: str, rect: Rect) -> List[str]:
    """ffmpeg args to post-crop a full-screen capture to the window rect."""
    return ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", src, "-vf", f"crop={rect.w}:{rect.h}:{rect.x}:{rect.y}",
            "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", out]


# --------------------------- shell side-effects --------------------------- #

def _run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def have(tool: str) -> bool:
    return shutil.which(tool) is not None


def window_rect(title: str, display: str = ":1") -> Optional[Rect]:
    """Resolve a window's absolute rect via ``xwininfo -name``."""
    if not have("xwininfo"):
        return None
    cp = _run(["xwininfo", "-display", display, "-name", title])
    if cp.returncode != 0:
        return None
    vals = {}
    for line in cp.stdout.splitlines():
        line = line.strip()
        for key, k in (("Absolute upper-left X:", "x"),
                       ("Absolute upper-left Y:", "y"),
                       ("Width:", "w"), ("Height:", "h")):
            if line.startswith(key):
                try:
                    vals[k] = int(line.split()[-1])
                except ValueError:
                    pass
    if {"w", "h", "x", "y"} <= set(vals):
        return clamp_crop(vals["w"], vals["h"], vals["x"], vals["y"])
    return None


def make_gif(src_mp4: str, out_gif: str, *, duration_secs: float,
             target_secs: int = C.GIF_TARGET_SECS, width: int = C.GIF_WIDTH,
             workdir: Optional[str] = None) -> int:
    """Encode a timelapse GIF, auto-reducing once if it exceeds GIF_MAX_BYTES.

    Returns the final GIF size in bytes (0 if ffmpeg is unavailable / failed).
    """
    if not have("ffmpeg"):
        return 0
    work = Path(workdir or Path(out_gif).parent)
    palette = str(work / "_palette.png")
    spf = speedup_factor(duration_secs, target_secs)
    _run(gif_palette_args(src_mp4, palette, spf=spf, fps=C.GIF_FPS,
                          width=width, colors=C.GIF_MAX_COLORS))
    _run(gif_encode_args(src_mp4, palette, out_gif, spf=spf, fps=C.GIF_FPS, width=width))
    size = Path(out_gif).stat().st_size if Path(out_gif).exists() else 0
    if size > C.GIF_MAX_BYTES:
        _run(gif_palette_args(src_mp4, palette, spf=spf, fps=C.GIF_REDUCE_FPS,
                              width=C.GIF_REDUCE_WIDTH, colors=C.GIF_REDUCE_COLORS))
        _run(gif_encode_args(src_mp4, palette, out_gif, spf=spf,
                             fps=C.GIF_REDUCE_FPS, width=C.GIF_REDUCE_WIDTH))
        size = Path(out_gif).stat().st_size if Path(out_gif).exists() else 0
    if Path(palette).exists():
        Path(palette).unlink()
    return size


def crop_capture(raw_mp4: str, out_mp4: str, rect: Rect) -> bool:
    """Post-crop a full-screen capture to the window rect."""
    if not have("ffmpeg"):
        return False
    cp = _run(crop_args(raw_mp4, out_mp4, rect))
    return cp.returncode == 0 and Path(out_mp4).exists()


def gif_first_frame_nonblack(gif_or_mp4: str, at_secs: float = 1.0) -> Optional[bool]:
    """Best-effort: sample a frame and report whether it has visible content.

    Returns None when ffmpeg/PIL is unavailable (check is skipped, not failed).
    """
    if not have("ffmpeg"):
        return None
    try:
        from PIL import Image  # noqa
    except Exception:
        return None
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        frame = str(Path(td) / "f.png")
        _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
              "-ss", str(at_secs), "-i", gif_or_mp4, "-frames:v", "1", frame])
        if not Path(frame).exists():
            return None
        from PIL import Image
        im = Image.open(frame).convert("RGB")
        ex = im.getextrema()
        return max(c[1] for c in ex) > 40


def gif_is_static(gif_or_mp4: str, a_secs: float = 0.5, b_secs: float = 2.5,
                  thresh: float = 2.0) -> Optional[bool]:
    """Best-effort: sample two frames at different times and report whether the GIF is
    STATIC (no motion) — catches the "redirect stream to file, render at end" recording
    bug that leaves the build screen frozen. Returns True if static (frames ~identical),
    False if there is motion, None when ffmpeg/PIL is unavailable (check skipped)."""
    if not have("ffmpeg"):
        return None
    try:
        from PIL import Image, ImageChops  # noqa
    except Exception:
        return None
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        fa, fb = str(Path(td) / "a.png"), str(Path(td) / "b.png")
        for ss, out in ((a_secs, fa), (b_secs, fb)):
            _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                  "-ss", str(ss), "-i", gif_or_mp4, "-frames:v", "1", out])
        if not (Path(fa).exists() and Path(fb).exists()):
            return None
        from PIL import Image, ImageChops
        a = Image.open(fa).convert("RGB"); b = Image.open(fb).convert("RGB")
        if a.size != b.size:
            return False
        hist = ImageChops.difference(a, b).convert("L").histogram()  # 256 bins
        total = sum(hist) or 1
        mean_abs = sum(i * hist[i] for i in range(256)) / total
        return mean_abs < thresh
