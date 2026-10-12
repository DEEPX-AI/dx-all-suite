"""Tutorial language and selector contracts for DX Stream.

Mirrors the `tests/dx_benchmark/test_tutorial.py` pattern for dx_stream.
Static contract tests — check source text only, without a browser/JS runtime.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dx_stream"
TEMPLATES = APP / "templates"
JS_DIR = APP / "static" / "js"

RUNTIME_SELECTOR_ALLOWLIST = {
    "#langToggle",
    "#dxToolbar",
    "button[onclick*=\"custom.upload\"]",
    'button[onclick*="build"]',
    'button[onclick*="stream-deps"]',
    'button[onclick*="runtime-deps"]',
    'button[onclick*="driver"]',
    'button[onclick*="download-models"]',
    'button[onclick*="webrtc-deps"]',
    '#demo-root .dds-stage [data-axis-row="playback"]',
    "#demo-root .dds-filter",
    "#demo-root .dds-grid",
    "#demo-root .dds-stage .dds-actions",
    "#demo-root .dds-stage .dds-media",
    "#demo-root .dds-stage .dds-metrics",
    "#demo-root .dds-stage #btn-demo-stop",
    "#demo-root .dds-stage .dds-extra",
    ".download-model-btn",
    ".modal-tab[data-tab=\"metadata\"]",
    "#model-tab-metadata",
    "#model-detail-modal",
    "#model-detail-modal .modal",
    "#dxt-mock-stream-toast",
    "#dxt-stream-mock-download-btn",
    ".palette-item",
    "#setup-badge-webrtc-deps",
    "#btn-demo-fullscreen",
    "#custom-build-log-card",
    '[id^="start-demo-"]',
}

EXPECTED_SECTION_IDS = [
    "global",
    "dashboard",
    "demo",
    "pipeline",
    "models",
    "elements",
    "setup",
    "custom",
]

TARGET_LANGS = ("ko", "ja", "zh-CN", "zh-TW", "es")


def rendered_index() -> str:
    """The index.html the server actually serves.

    shared/shell.py injects the rail, header, tabs and toolbar badges at render time, so
    reading only the template file misses the shell selectors the tutorial points at.
    """
    from dx_stream.server import DX_STREAM_SHELL
    from shared.shell import apply as apply_shell

    return apply_shell(
        (TEMPLATES / "index.html").read_text(encoding="utf-8"), DX_STREAM_SHELL
    )


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
    tokens: set = set()
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
    """Pure helper unit — target/targetAll extraction."""
    source = """
    var helpDefs = {
      dashboard: [
        { target: '#stat-npu' },
        { targetAll: '.chart-row' },
        { targetAll: "[id^='ref-cat-']" },
      ],
    };
    """
    assert _tutorial_targets(source) == {
        "#stat-npu",
        ".chart-row",
        "[id^='ref-cat-']",
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
    html = rendered_index()
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
    """Every i18n object covers all TARGET_LANGS (counted against ko occurrences)."""
    source = read_text(JS_DIR / "tutorial.js")
    ko_count = len(re.findall(r"\bko\s*:", source))
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
    """The tutorial ships all six languages (ko/en/ja/zh-CN/zh-TW/es) with real
    per-section coverage, not just a '6-language support' header string."""
    source = read_text(JS_DIR / "tutorial.js")
    langs = ("ko", "en", "ja", "zh-CN", "zh-TW", "es")
    counts = {
        lang: source.count(f"'{lang}':" if "-" in lang else f"{lang}:")
        for lang in langs
    }
    insufficient = {lang: c for lang, c in counts.items() if c < 8}
    assert not insufficient, f"languages with insufficient coverage: {counts}"


def test_zh_tw_gstreamer_command_not_calqued_from_zh_cn():
    """zh-TW should use 指令 (not mainland 命令) for GStreamer command labels."""
    source = read_text(JS_DIR / "tutorial.js")
    assert "'zh-TW': 'GStreamer指令'" in source
    assert "gst-launch指令" in source
    assert re.search(
        r"title: \{ ko: 'GStreamer 명령어'.*'zh-TW': 'GStreamer指令'",
        source,
    )
    assert "'zh-TW': 'GStreamer命令'" not in source
