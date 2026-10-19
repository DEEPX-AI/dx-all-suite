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
    # Run Demo (Task 11) — rendered by rundemo.js / dx-demo-stage.js at runtime, not present in
    # the static index.html template.
    "#rundemo-root .dds-filter",
    "#rundemo-root .dds-stage",
    '#rundemo-root .dds-stage [data-axis-row="post"]',
    "#rundemo-root .dds-stage .dds-run",
    # Graph Composer: drawn by graph-palette.js, graph-inspector.js and graph-run.js once the page opens.
    ".gc-group",
    ".gc-zone-edit",
    "#gc-run-results",
    "#gc-run-events",
}

# The graph tour, in order: one step per part of the composer (Phase 4).
GRAPH_STEP_TARGETS = [
    "#gc-palette",
    '.gc-group[data-group="templates"]',
    "#gc-canvas-host",
    "#gc-inspector",
    '.gc-group[data-group="logic"]',
    "#gc-inspector .gc-zone-edit",
    "#gc-validate",
    "#gc-run-panel",
    "#gc-run-results",
    "#gc-run-events",
    "#gc-live-body",
    "#gc-export-cpp",
    "#gc-toolbar",
]

EXPECTED_SECTION_IDS = [
    "setup",
    "models",
    "run-single",
    "run-cont",
    "rundemo",
    "bench",
    "compare",
    "modelzoo",
    "graph",
    "compiler",
    "outputs",
    "global",
    "developer",
]

TARGET_LANGS = ("ko", "ja", "zh-CN", "zh-TW", "es")


def rendered_index() -> str:
    """The index.html the server actually serves.

    shared/shell.py injects the rail, header and tabs at render time, so reading the template file alone would miss
    the shell selectors the tutorial points at.
    """
    from shared.shell import apply as apply_shell
    from dx_app.server import DX_APP_SHELL

    return apply_shell(
        (TEMPLATES / "index.html").read_text(encoding="utf-8"), DX_APP_SHELL
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


def _template_ids_and_classes(html: str) -> set[str]:
    ids = set(re.findall(r'id="([^"]+)"', html))
    classes = set()
    for match in re.findall(r'class="([^"]+)"', html):
        for cls in match.split():
            classes.add(f".{cls}")
    return {f"#{i}" for i in ids} | classes


def _template_onclick_values(html: str) -> set[str]:
    """All onclick attribute strings in the template — lets attribute-substring
    selectors like button[onclick*="dx-app-deps"] resolve against real handlers."""
    return set(re.findall(r'onclick="([^"]+)"', html))


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


def _unresolved_target_tokens(target: str, selectors: set[str], onclicks=frozenset()) -> list[str]:
    """Return unresolvable tokens from a CSS selector target."""
    if target in selectors:
        return []
    # Attribute-substring selector, e.g. button[onclick*="dx-app-deps"] — robust,
    # order-independent targeting of a handler button. Resolves if the substring
    # appears in some onclick attribute in the template.
    attr = re.search(r'\[onclick\*=["\']([^"\']+)["\']\]', target)
    if attr:
        needle = attr.group(1)
        return [] if any(needle in oc for oc in onclicks) else [target]
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
    html = rendered_index()
    source = read_text(JS_DIR / "tutorial.js")
    template_tokens = _template_ids_and_classes(html)
    all_known = template_tokens | RUNTIME_SELECTOR_ALLOWLIST
    onclicks = _template_onclick_values(html)
    targets = _tutorial_targets(source)
    unresolved = {
        target: tokens
        for target in sorted(targets)
        if (tokens := _unresolved_target_tokens(target, all_known, onclicks))
    }
    assert not unresolved, f"targets with missing tokens: {unresolved}"


def test_app_tutorial_preserves_expected_sections():
    source = read_text(JS_DIR / "tutorial.js")
    for section_id in EXPECTED_SECTION_IDS:
        assert re.search(rf"\{{\s*id\s*:\s*['\"]{re.escape(section_id)}['\"]", source), (
            f"section {section_id!r} missing from tutorial.js"
        )


def test_sections_cover_target_languages():
    """Every i18n object covers all TARGET_LANGS (objects counted by their ko keys)."""
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


def _graph_section(source: str) -> str:
    return source[source.index("{ id:'graph'"):source.index("{ id:'lab'")]


def test_graph_tour_covers_the_composer_in_order():
    section = _graph_section(read_text(JS_DIR / "tutorial.js"))
    assert re.findall(r"target:'([^']+)'", section) == GRAPH_STEP_TARGETS


def test_graph_tour_undoes_what_it_shows():
    steps = re.split(r"\n        \{ target:", _graph_section(read_text(JS_DIR / "tutorial.js")))[1:]
    for step in steps:
        if "_gcShowResults" in step:
            assert "_gcHideResults" in step, step[:60]
        if "_gcTab('live')" in step:
            assert "_gcRestoreTab" in step, step[:60]
    assert "ensureExample" not in read_text(JS_DIR / "tutorial.js")


def test_graph_steps_that_need_a_template_are_optional():
    """With unsaved work on the canvas the tour shows no template, so these targets may be absent."""
    steps = re.split(r"\n        \{ target:", _graph_section(read_text(JS_DIR / "tutorial.js")))[1:]
    optional = {re.match(r"'([^']+)'", s).group(1) for s in steps if "optionalTarget:true" in s}
    assert optional == {'.gc-group[data-group="templates"]', '.gc-group[data-group="logic"]',
                        "#gc-inspector .gc-zone-edit", "#gc-run-results", "#gc-run-events"}


def test_the_graph_composer_has_a_reference_doc():
    source = read_text(JS_DIR / "tutorial.js")
    assert re.search(r"\{ id:'ref-graph', icon:'graph'", source)
