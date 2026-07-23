"""dx_agent_dev 쇼케이스 양옆 패널 정적 계약 테스트."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENT = ROOT / "dx_agent_dev"
INDEX = AGENT / "templates" / "index.html"
CONSOLE = AGENT / "static" / "js" / "console.js"
MEDIA = AGENT / "static" / "media"

EXPECTED_MEDIA = (
    "dx-agent-dev-squat-gameplay.gif",
    "dx-agent-dev-stretch-gameplay.gif",
    "dx-agent-dev-ultralytics-yolo.gif",
    "dx-agent-dev-ultralytics-wildlife-sample.jpg",
    "dx-agent-dev-ultralytics-ppe-sample.jpg",
    "dx-agent-dev-ultralytics-braintumor-sample.jpg",
    "dx-agent-dev-ultralytics-pills-sample.jpg",
    "dx-agent-dev-paddleocr-gameplay.gif",
    "dx-agent-dev-rapiddoc-pdf2md-sample.png",
)


def _read(p):
    return p.read_text(encoding="utf-8")


def _func_body(js, name):
    """IIFE 내 함수 본문을 다음 함수 선언 직전까지 추출."""
    marker = "function " + name + "("
    start = js.index(marker)
    rest = js[start + len(marker):]
    nxt = re.search(r"\n  (?:async )?function ", rest)
    return rest[:nxt.start()] if nxt else rest


def test_index_has_side_panels():
    html = _read(INDEX)
    assert 'class="agent-layout"' in html
    assert 'id="examples-left"' in html
    assert 'id="examples-right"' in html


def test_console_defines_render_panels_with_cache():
    js = _read(CONSOLE)
    assert "renderExamplePanels" in js
    assert "_showcaseCache" in js


def test_applylang_calls_render_panels():
    body = _func_body(_read(CONSOLE), "applyLang")
    assert "renderExamplePanels" in body


def test_cards_use_blank_and_lazy():
    body = _func_body(_read(CONSOLE), "renderExamplePanels")
    assert "_blank" in body
    assert "loading" in body and "lazy" in body


def test_degraded_gallery_has_no_fetch_or_grid():
    body = _func_body(_read(CONSOLE), "showDegradedGallery")
    assert "showcase-grid" not in body
    assert "/api/agent/showcases" not in body


def test_media_files_exist():
    for f in EXPECTED_MEDIA:
        assert (MEDIA / f).exists(), f
