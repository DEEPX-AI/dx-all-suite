"""Video previews in the Outputs gallery load only when they come near the viewport.

If every card fetched its src up front (preload="metadata"), opening a gallery of hundreds of results would fire
hundreds of requests at once.
"""
from pathlib import Path

JS = Path(__file__).resolve().parents[2] / "dx_app/static/js/outputs.js"


def test_video_thumbs_start_without_src():
    src = JS.read_text(encoding="utf-8")
    assert "<video class=\"gal-thumb\" data-src=\"'+f.url+'\" muted preload=\"none\"" in src
    assert "muted preload=\"metadata\"" not in src


def test_video_thumbs_load_through_an_intersection_observer():
    src = JS.read_text(encoding="utf-8")
    body = src[src.index("function _lazyVideoThumbs"):]
    assert "new IntersectionObserver" in body and "v.src=v.dataset.src" in body
    assert "_lazyVideoThumbs(grid);" in src
