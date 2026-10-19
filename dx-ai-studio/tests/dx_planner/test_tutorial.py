"""Tutorial language and selector contracts for DX EdgeGuide (dx_planner).

Follows the `tests/dx_agent_dev/test_tutorial.py` pattern for the dx_planner workspace UI.
Static contract tests: they check source text only, with no browser or JS runtime.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dx_planner"
TEMPLATES = APP / "templates"
JS_DIR = APP / "static" / "js"

RUNTIME_SELECTOR_ALLOWLIST = {
    "#dxToolbar",
    "#langToggle",
    ".rec-card",
    '[data-help-id^="planner-size-"]',
}

EXPECTED_SECTION_IDS = ["overview", "requirements", "recommendations", "details"]

TARGET_LANGS = ("ko", "ja", "zh-CN", "zh-TW", "es")


def rendered_index() -> str:
    """The index.html the server actually sends (after shell injection).

    shared/shell.py injects the rail, header and toolbar at render time.
    """
    from dx_planner.server import DX_PLANNER_SHELL
    from shared.shell import apply as apply_shell

    return apply_shell(
        (TEMPLATES / "index.html").read_text(encoding="utf-8"), DX_PLANNER_SHELL
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
    """Pure helper check: target/targetAll extraction is exact."""
    source = """
    var helpDefs = {
      workspace: [
        { target: '#plannerWorkspace' },
        { targetAll: '.task-btn' },
        { targetAll: '.size-btn' },
      ],
    };
    """
    assert _tutorial_targets(source) == {
        "#plannerWorkspace",
        ".task-btn",
        ".size-btn",
    }


def test_get_lang_uses_dxi18n_and_ko_default():
    source = read_text(JS_DIR / "tutorial.js")
    body = _extract_braced_body(source, "getLang")
    assert "DXI18n" in body
    assert "DXI18n.lang" in body
    assert ": 'ko'" in body or '": "ko"' in body


def test_tutorial_targets_exist_or_are_runtime_injected():
    html = rendered_index()
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


def test_preserves_expected_sections():
    source = read_text(JS_DIR / "tutorial.js")
    for section_id in EXPECTED_SECTION_IDS:
        assert re.search(
            rf"id:\s*['\"]{re.escape(section_id)}['\"]", source
        ), f"section {section_id!r} missing from tutorial.js"


def test_sections_cover_target_languages():
    """Every i18n object covers all TARGET_LANGS (counted against the ko entries)."""
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

