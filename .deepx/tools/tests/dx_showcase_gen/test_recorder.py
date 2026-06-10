"""Pure-function tests for the recorder (no x11grab/ffmpeg side-effects)."""
from dx_showcase_gen import recorder as r


def test_clamp_crop_forces_even_and_clamps():
    rect = r.clamp_crop(1855, 1049, 66, 32, screen_w=1920, screen_h=1080)
    assert rect.w % 2 == 0 and rect.h % 2 == 0
    assert rect.x == 66 and rect.y == 32
    assert rect.x + rect.w <= 1920 and rect.y + rect.h <= 1080


def test_clamp_crop_negative_offset():
    rect = r.clamp_crop(100, 100, -26, -5)
    assert rect.x == 0 and rect.y == 0


def test_speedup_factor():
    assert r.speedup_factor(0) == 1
    assert r.speedup_factor(20, target_secs=20) == 1
    assert r.speedup_factor(600, target_secs=20) == 30
    assert r.speedup_factor(5, target_secs=20) == 1   # never < 1


def test_gif_args_contain_palette_and_setpts():
    pal = r.gif_palette_args("in.mp4", "p.png", spf=30, fps=9, width=760, colors=64)
    enc = r.gif_encode_args("in.mp4", "p.png", "out.gif", spf=30, fps=9, width=760)
    assert "palettegen=max_colors=64" in " ".join(pal)
    assert "setpts=PTS/30" in " ".join(pal)
    assert "paletteuse=dither=none" in " ".join(enc)
    assert enc[-1] == "out.gif"


def test_crop_args():
    rect = r.Rect(w=1266, h=848, x=40, y=9)
    args = r.crop_args("raw.mp4", "crop.mp4", rect)
    assert "crop=1266:848:40:9" in " ".join(args)
