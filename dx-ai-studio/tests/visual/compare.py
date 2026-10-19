"""Pixel comparison for the visual-regression suite.

Deliberately simple: no perceptual metric, no anti-alias heuristics. A screenshot
gate earns its keep by being predictable, and "N pixels differ by more than T"
is something a reviewer can reason about from the diff image alone.
"""
from __future__ import annotations

from pathlib import Path

# Per-channel difference below this is treated as encoder/AA noise, not a change.
CHANNEL_TOLERANCE = 8


def _load(path: Path):
    from PIL import Image

    with Image.open(path) as im:
        return im.convert("RGB").copy()


def compare(baseline: Path, candidate: Path, diff_out: Path | None = None) -> dict:
    """Compare two PNGs.

    Returns {"same_size", "changed_ratio", "changed_pixels", "total_pixels",
    "baseline_size", "candidate_size"}. When they differ and ``diff_out`` is given,
    writes a red-highlight overlay so the failure is inspectable in CI artifacts.
    """
    from PIL import Image, ImageChops

    base = _load(baseline)
    cand = _load(candidate)

    if base.size != cand.size:
        # A size change is a layout change; reporting a ratio would be meaningless.
        return {
            "same_size": False,
            "changed_ratio": 1.0,
            "changed_pixels": -1,
            "total_pixels": base.size[0] * base.size[1],
            "baseline_size": base.size,
            "candidate_size": cand.size,
        }

    diff = ImageChops.difference(base, cand)
    # Collapse RGB to the worst channel, then threshold.
    mono = diff.convert("L").point(lambda v: 255 if v > CHANNEL_TOLERANCE else 0)
    changed = sum(mono.histogram()[255:])
    total = base.size[0] * base.size[1]

    if changed and diff_out is not None:
        diff_out.parent.mkdir(parents=True, exist_ok=True)
        overlay = cand.copy()
        red = Image.new("RGB", cand.size, (255, 0, 0))
        overlay.paste(red, mask=mono)
        Image.blend(cand, overlay, 0.55).save(diff_out, "PNG")

    return {
        "same_size": True,
        "changed_ratio": changed / total if total else 0.0,
        "changed_pixels": changed,
        "total_pixels": total,
        "baseline_size": base.size,
        "candidate_size": cand.size,
    }
