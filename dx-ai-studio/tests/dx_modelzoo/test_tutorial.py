"""Tutorial language and selector contracts for DX Model Zoo.

`tests/dx_planner/test_tutorial.py` 패턴을 dx_modelzoo(카탈로그/상세 UI)에 맞게 복제.
정적 계약 테스트 — 브라우저/JS 런타임 없이 소스 텍스트만 검증.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dx_modelzoo"
TEMPLATES = APP / "templates"
JS_DIR = APP / "static" / "js"

RUNTIME_SELECTOR_ALLOWLIST = {
    "#btnDxtronCompiler",
    "#btnOnnxLink",
    "#btnRunDefault",
    "#btnRunSample",
    "#demoSection",
    "#dxToolbar",
    "#dxt-mock-dl",
    "#dxt-mock-example",
    "#dxt-mock-inf",
    "#inferencePanel",
    "#inferenceResultUpload",
    "#inferenceUploadTrigger",
    "#langToggle",
    "#sampleImageGrid",
    "#sectionCompile",
    "#sectionExample",
    "#sectionLegal",
    "#sectionQuickFacts",
    "#sectionSpec",
    "#sectionUseCase",
    "#tabSample",
    "#tabUpload",
    ".mz-back-btn",
    ".mz-card",
    ".mz-category-option",
    ".mz-code-copy",
    ".mz-code-tab",
    ".mz-code-tabs",
    ".mz-detail-action-bar",
    ".mz-detail-header",
    ".mz-detail-hero-badges",
    "#detailView",
    ".mz-detail-title",
    ".mz-download-badge",
    ".mz-example-gallery",
    ".mz-example-image",
    ".mz-list-row",
    ".mz-list-table",
    ".mz-placeholder",
    ".mz-spec-table",
    "[data-model-id][data-quant]",
}

EXPECTED_SECTION_IDS = [
    "topbar",
    "catalog",
    "detail",
    "examples",
    "download",
    "inference",
]

TARGET_LANGS = ("ko", "ja", "zh-CN", "zh-TW", "es")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_braced_body(source: str, anchor: str) -> str:
    start = source.find(anchor)
    assert start != -1, f"anchor {anchor!r} not found"
    open_pos = source.find("{", start)
    assert open_pos != -1, f"no opening brace after {anchor!r}"
    depth = 0
    for i in range(open_pos, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[open_pos + 1 : i]
    raise AssertionError(f"unmatched braces after {anchor!r}")


def _template_ids_and_classes(html: str) -> set:
    ids = set(re.findall(r'id="([^"]+)"', html))
    classes = set()
    for match in re.findall(r'class="([^"]+)"', html):
        for cls in match.split():
            classes.add(f".{cls}")
    return {f"#{i}" for i in ids} | classes


def _js_rendered_selectors() -> set:
    tokens: set[str] = set()
    for js_path in JS_DIR.glob("*.js"):
        if js_path.name == "tutorial.js":
            continue
        text = js_path.read_text(encoding="utf-8")
        tokens.update(f"#{i}" for i in re.findall(r'id="([^"]+)"', text))
        tokens.update(f"#{i}" for i in re.findall(r"id='([^']+)'", text))
        for match in re.findall(r'class="([^"]+)"', text):
            for cls in match.split():
                tokens.add(f".{cls}")
        for match in re.findall(r"class='([^']+)'", text):
            for cls in match.split():
                tokens.add(f".{cls}")
    return tokens


def _tutorial_targets(source: str) -> set:
    single = re.findall(r"target(?:All)?:\s*'([^']+)'", source)
    double = re.findall(r'target(?:All)?:\s*"([^"]+)"', source)
    return set(single + double)


def _unresolved_target_tokens(target: str, selectors: set) -> list:
    if target in selectors:
        return []
    tokens = re.findall(r"#[A-Za-z0-9_-]+|\.[A-Za-z0-9_-]+", target)
    if not tokens:
        return [target]
    return [token for token in tokens if token not in selectors]


def test_tutorial_targets_extract():
    """헬퍼 단위(순수) — target/targetAll 추출 정확성."""
    source = """
    var helpDefs = {
      catalog: [
        { target: '#catalogContainer' },
        { targetAll: '.mz-card' },
        { targetAll: '.mz-list-row' },
      ],
    };
    """
    assert _tutorial_targets(source) == {
        "#catalogContainer",
        ".mz-card",
        ".mz-list-row",
    }


def test_get_lang_uses_local_storage_and_en_default():
    source = read_text(JS_DIR / "tutorial.js")
    body = _extract_braced_body(source, "getLang")
    assert (
        "localStorage.getItem('dx-lang')" in body
        or 'localStorage.getItem("dx-lang")' in body
    )
    assert "|| 'en'" in body
    assert "|| 'ko'" not in body


def test_tutorial_targets_exist_or_are_runtime_injected():
    html = read_text(TEMPLATES / "index.html")
    source = read_text(JS_DIR / "tutorial.js")
    template_tokens = _template_ids_and_classes(html)
    all_known = template_tokens | _js_rendered_selectors() | RUNTIME_SELECTOR_ALLOWLIST
    targets = _tutorial_targets(source)
    unresolved = {
        target: tokens
        for target in sorted(targets)
        if (tokens := _unresolved_target_tokens(target, all_known))
    }
    assert not unresolved, f"targets with missing tokens: {unresolved}"


def test_preserves_expected_sections():
    source = read_text(JS_DIR / "tutorial.js")
    for section_id in EXPECTED_SECTION_IDS:
        assert re.search(
            rf"id:\s*['\"]{re.escape(section_id)}['\"]", source
        ), f"section {section_id!r} missing from tutorial.js"


def test_sections_cover_target_languages():
    """모든 i18n 객체가 TARGET_LANGS를 빠짐없이 커버(ko 출현수 기준)."""
    source = read_text(JS_DIR / "tutorial.js")
    ko_count = len(re.findall(r"(?<![A-Za-z0-9_'\"-])ko\s*:", source))
    assert ko_count >= 8, f"expected several i18n objects, ko-keys={ko_count}"
    deficits = {}
    for lang in TARGET_LANGS:
        if lang == "ko":
            continue
        count = len(re.findall(rf"['\"]?{re.escape(lang)}['\"]?\s*:", source))
        if count < ko_count:
            deficits[lang] = (count, ko_count)
    assert not deficits, f"language coverage deficits (count < ko): {deficits}"


def test_index_html_loads_tutorial_assets():
    html = read_text(TEMPLATES / "index.html")
    for asset in (
        "/static/shared/tutorial.css",
        "/static/shared/tutorial-engine.js",
        "/static/shared/tutorial-init.js",
        "/static/js/tutorial.js",
    ):
        assert asset in html, f"{asset} not loaded in index.html"
    e = html.find("tutorial-engine.js")
    i = html.find("tutorial-init.js")
    t = html.find("/static/js/tutorial.js")
    assert -1 < e < i < t, "script order must be engine -> init -> tutorial.js"


def test_tutorial_header_declares_six_language_support():
    source = read_text(JS_DIR / "tutorial.js")
    assert "6-language support" in source
