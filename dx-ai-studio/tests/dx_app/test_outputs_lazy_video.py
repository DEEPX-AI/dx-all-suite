"""Outputs 갤러리의 영상 미리보기는 화면 가까이 올 때만 받는다 (release audit A-23).

예전에는 모든 카드가 preload="metadata" 로 src 를 바로 가져, 결과가 수백 개면 갤러리를 열 때 수백 개 요청이 몰렸다.
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
