"""Tutorial language and selector contracts for DX App."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dx_app"
TEMPLATES = APP / "templates"
JS_DIR = APP / "static" / "js"

RUNTIME_SELECTOR_ALLOWLIST = {
    "#dxToolbar",
    '[data-page="lab"]',
    '[id^="b-input-"]',
    '[id^="lab-card-"]',
    '[id^="ref-cat-"]',
    '[id^="ref-sec-"]',
    '[id^="setup-badge-"]',
    '[id^="setup-detail-"]',
    '[id^="setup-version-"]',
    ".ref-topic-card",
    "#ref-expand",
    "#ref-detail",
    "#lb-header",
    "#dxt-mock-toast",
    "#gallery-lightbox",
    ".dxt-tutorial-pin",
}

EXPECTED_SECTION_IDS = [
    "setup",
    "models",
    "run-single",
    "run-cont",
    "bench",
    "compare",
    "modelzoo",
    "compiler",
    "outputs",
    "global",
    "developer",
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


def _template_ids_and_classes(html: str) -> set[str]:
    ids = set(re.findall(r'id="([^"]+)"', html))
    classes = set()
    for match in re.findall(r'class="([^"]+)"', html):
        for cls in match.split():
            classes.add(f".{cls}")
    return {f"#{i}" for i in ids} | classes


def _tutorial_targets(source: str) -> set[str]:
    """Extract target and targetAll values from tutorial step definitions."""
    single = re.findall(r"target(?:All)?:\s*'([^']+)'", source)
    double = re.findall(r'target(?:All)?:\s*"([^"]+)"', source)
    return set(single + double)


def test_tutorial_targets_include_target_all_selectors():
    source = """
    const helpDefs = {
      reference: [
        { target: '#ref-search' },
        { targetAll: '.ref-topic-card' },
        { targetAll: "[id^='ref-cat-']" },
      ],
    };
    """
    assert _tutorial_targets(source) == {
        "#ref-search",
        ".ref-topic-card",
        "[id^='ref-cat-']",
    }


def _unresolved_target_tokens(target: str, selectors: set[str]) -> list[str]:
    """Return unresolvable tokens from a CSS selector target."""
    if target in selectors:
        return []
    tokens = re.findall(r"#[A-Za-z0-9_-]+|\.[A-Za-z0-9_-]+", target)
    if not tokens:
        return [target]
    return [token for token in tokens if token not in selectors]


def test_app_tutorial_get_lang_uses_dxi18n_and_en_default():
    source = read_text(JS_DIR / "tutorial.js")
    body = _extract_braced_body(source, "getLang")
    assert "window.DXI18n" in body
    assert "window.DXI18n.lang" in body, (
        "getLang must use fully-qualified window.DXI18n.lang"
    )
    assert "localStorage.getItem('dx-lang')" in body or 'localStorage.getItem("dx-lang")' in body
    assert "|| 'en'" in body
    assert "typeof _lang" not in body
    assert "|| 'ko'" not in body


def test_app_tutorial_targets_exist_or_are_runtime_injected():
    html = read_text(TEMPLATES / "index.html")
    source = read_text(JS_DIR / "tutorial.js")
    template_tokens = _template_ids_and_classes(html)
    all_known = template_tokens | RUNTIME_SELECTOR_ALLOWLIST
    targets = _tutorial_targets(source)
    unresolved = {
        target: tokens
        for target in sorted(targets)
        if (tokens := _unresolved_target_tokens(target, all_known))
    }
    assert not unresolved, f"targets with missing tokens: {unresolved}"


def test_app_tutorial_preserves_expected_sections():
    source = read_text(JS_DIR / "tutorial.js")
    for section_id in EXPECTED_SECTION_IDS:
        assert re.search(rf"\{{\s*id\s*:\s*['\"]{re.escape(section_id)}['\"]", source), (
            f"section {section_id!r} missing from tutorial.js"
        )


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
