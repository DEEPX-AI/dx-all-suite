"""Static i18n contracts for DX ModelZoo."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODELZOO = ROOT / "dx_modelzoo"
I18N = MODELZOO / "static" / "js" / "i18n.js"
I18N_JS_DIR = MODELZOO / "static" / "js"
TEMPLATE = MODELZOO / "templates" / "index.html"
TARGET_LANGS = ("en", "ko", "ja", "zh-CN", "zh-TW", "es")
I18N_SOURCE_FILES = [
    MODELZOO / "templates" / "index.html",
    MODELZOO / "static" / "js" / "app.js",
    MODELZOO / "static" / "js" / "catalog.js",
    MODELZOO / "static" / "js" / "detail.js",
    MODELZOO / "static" / "js" / "inference.js",
    MODELZOO / "static" / "js" / "tutorial.js",
]
TECH_TOKEN_KEYS = {
    "DX App",
    "DX Model Zoo",
    "DXNN",
    "Q-Lite",
    "Q-Pro",
    "ONNX",
    "PPU",
    "FPS",
    "FPS (DX-M1)",
    "FPS/Watt",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def i18n_fragment_files() -> list[Path]:
    """Return all i18n-dict-*.js fragment files sorted by name."""
    return sorted(I18N_JS_DIR.glob("i18n-dict-*.js"))


def i18n_all_sources() -> str:
    """Return concatenated source of i18n.js + all i18n-dict-*.js fragments."""
    parts = [read_text(I18N)]
    for frag in i18n_fragment_files():
        parts.append(read_text(frag))
    return "\n".join(parts)


def i18n_source() -> str:
    return read_text(I18N)


def _extract_dict_keys_from_source(source: str) -> list[str]:
    """Extract all dictionary keys from Object.assign or direct dict blocks."""
    return re.findall(r"'((?:\\.|[^'\\])+)':\s*\{", source)


def _extract_dict_entry_from_source(source: str, key: str) -> str:
    """Extract a single entry block for a key from source text."""
    pattern = rf"'{re.escape(key)}':\s*\{{"
    match = re.search(pattern, source)
    if not match:
        return ""
    brace = source.index("{", match.start())
    depth = 0
    for i in range(brace, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[brace + 1 : i]
    return ""


def dict_section() -> str:
    """Legacy: extract dict section from the union of all i18n sources."""
    source = i18n_all_sources()
    # Collect all dict entries from all sources
    entries = []
    for m in re.finditer(r"'((?:\\.|[^'\\])+)':\s*\{", source):
        key = m.group(1)
        # Skip language keys (en, ko, ja, zh-CN, zh-TW)
        if key in TARGET_LANGS:
            continue
        entry_text = _extract_dict_entry_from_source(source[m.start():], m.group(1))
        if entry_text:
            entries.append(f"'{key}': {{{entry_text}}}")
    return "\n".join(entries)


def _dict_source_sections() -> str:
    """Return concatenated source of dict-only sections (fragments + core dict)."""
    parts = []
    # From each fragment file, extract the register call body
    for frag in i18n_fragment_files():
        parts.append(read_text(frag))
    # Also check i18n.js for any direct _DX_I18N_DICT assignment (backward compat)
    src = read_text(I18N)
    if "window._DX_I18N_DICT = {" in src:
        parts.append(src)
    return "\n".join(parts)


def dict_keys_list() -> list[str]:
    source = _dict_source_sections()
    keys = []
    for m in re.finditer(r"'((?:\\.|[^'\\])+)':\s*\{", source):
        key = m.group(1)
        if key in TARGET_LANGS:
            continue
        entry = _extract_dict_entry_from_source(source[m.start():], key)
        if any(f"{lang}:" in entry or f"'{lang}':" in entry for lang in TARGET_LANGS):
            keys.append(key)
    return keys


def dict_keys() -> set[str]:
    return set(dict_keys_list())


def dict_entry(key: str) -> str:
    source = i18n_all_sources()
    return _extract_dict_entry_from_source(source, key)


def t_keys(path: Path) -> set[str]:
    source = read_text(path)
    single = re.findall(r"\bT\('\s*((?:\\.|[^'\\])+)\s*'\)", source)
    double = re.findall(r'\bT\("\s*((?:\\.|[^"\\])+)\s*"\)', source)
    return set(single + double)


def data_i18n_keys(path: Path) -> set[str]:
    source = read_text(path)
    return set(re.findall(r'data-i18n(?:-[a-z]+)?="([^"]+)"', source))


def used_i18n_keys() -> dict[str, set[str]]:
    result = {}
    for path in I18N_SOURCE_FILES:
        keys = t_keys(path) | data_i18n_keys(path)
        if keys:
            result[str(path.relative_to(MODELZOO))] = keys
    return result




def test_modelzoo_dict_entry_parser_handles_compact_entries():
    entry = dict_entry("AI Model Hub")
    assert "AI Model Hub" in entry
    assert re.search(r"\n\s*'[^']+':\s*\{", entry) is None
    assert "{" not in entry
    assert "}" not in entry


def test_modelzoo_i18n_has_no_duplicate_keys():
    assert dict_keys_list(), "No dictionary keys parsed"
    counts = Counter(dict_keys_list())
    dupes = {key: count for key, count in counts.items() if count > 1}
    assert not dupes, dupes


def test_modelzoo_used_i18n_keys_are_in_dictionary():
    keys = dict_keys()
    assert keys, "No dictionary keys parsed"
    missing = {}
    for rel_path, used in used_i18n_keys().items():
        unresolved = sorted(key for key in used if key not in keys)
        if unresolved:
            missing[rel_path] = unresolved
    assert not missing, missing


def test_modelzoo_dictionary_entries_cover_all_five_languages():
    keys = dict_keys()
    assert keys, "No dictionary keys parsed"
    incomplete = {}
    for key in sorted(keys):
        entry = dict_entry(key)
        missing_langs = [
            lang
            for lang in TARGET_LANGS
            if f"{lang}:" not in entry
            and f"'{lang}':" not in entry
            and f'"{lang}":' not in entry
        ]
        if missing_langs:
            incomplete[key] = missing_langs
    assert not incomplete, incomplete


def test_modelzoo_technical_token_keys_keep_identity_when_present():
    identity_langs = [lang for lang in TARGET_LANGS if lang != "es"]
    for key in sorted(TECH_TOKEN_KEYS & dict_keys()):
        entry = dict_entry(key)
        for lang in identity_langs:
            pattern = rf"(?:{re.escape(lang)}|'?{re.escape(lang)}'?):\s*'({re.escape(key)})'"
            assert re.search(pattern, entry), (key, lang)




def test_i18n_fragment_files_exist():
    """At least one i18n-dict-*.js fragment must exist."""
    frags = i18n_fragment_files()
    assert len(frags) >= 1, "No i18n-dict-*.js fragment files found"


def test_i18n_core_exists():
    """i18n-core.js must exist as the bootstrap/initializer."""
    core = I18N_JS_DIR / "i18n-core.js"
    assert core.exists(), "i18n-core.js not found"


def test_i18n_core_initializes_globals():
    """i18n-core.js must initialize window._DX_I18N_DICT and provide register helper."""
    core_src = read_text(I18N_JS_DIR / "i18n-core.js")
    assert "window._DX_I18N_DICT" in core_src, "core must init _DX_I18N_DICT"
    assert "_DX_MODELZOO_I18N_REGISTER" in core_src, "core must provide register helper"


def test_i18n_js_is_small_bootstrap():
    """i18n.js must be a small compatibility/bootstrap file, not the full dictionary."""
    src = i18n_source()
    # The original i18n.js was ~980 lines. After split it should be much smaller.
    line_count = len(src.strip().splitlines())
    assert line_count < 80, (
        f"i18n.js should be a small bootstrap file but has {line_count} lines"
    )


def test_i18n_js_sets_placeholders_and_callbacks():
    """i18n.js must still define _DX_I18N_PLACEHOLDERS and _DX_I18N_CALLBACKS."""
    src = i18n_source()
    assert "window._DX_I18N_PLACEHOLDERS" in src, "i18n.js must set placeholders"
    assert "window._DX_I18N_CALLBACKS" in src, "i18n.js must set callbacks"


def test_i18n_js_callback_preserves_behavior():
    """i18n.js callback must update data-title-*, call filterAndRender, handle #model= hash."""
    src = i18n_source()
    assert "data-title-" in src, "callback must update data-title attributes"
    assert "filterAndRender" in src, "callback must call filterAndRender"
    assert "getModelIdFromHash" in src, "callback must use getModelIdFromHash"
    assert "renderDetailPage" in src, "callback must call renderDetailPage"


def test_fragments_use_register_or_object_assign():
    """Each fragment must register entries via helper or Object.assign."""
    for frag in i18n_fragment_files():
        src = read_text(frag)
        uses_register = "_DX_MODELZOO_I18N_REGISTER" in src
        uses_assign = "Object.assign" in src
        assert uses_register or uses_assign, (
            f"{frag.name} must use register helper or Object.assign"
        )


def test_fragments_no_async_fetch():
    """No fragment may use async fetch or dynamic import for dictionary loading."""
    all_i18n_files = [I18N_JS_DIR / "i18n-core.js", I18N] + i18n_fragment_files()
    for f in all_i18n_files:
        src = read_text(f)
        assert "fetch(" not in src, f"{f.name} must not use fetch()"
        assert "import(" not in src, f"{f.name} must not use dynamic import()"
        assert "XMLHttpRequest" not in src, f"{f.name} must not use XMLHttpRequest"
        assert "require(" not in src, f"{f.name} must not use require()"


def test_union_of_fragments_covers_all_keys():
    """Union of i18n.js + all fragments must have same keys as original dict."""
    keys = dict_keys()
    assert len(keys) >= 130, (
        f"Expected ~136 keys total but found {len(keys)}"
    )


def test_every_key_has_all_five_languages_in_fragments():
    """Every key across all fragments must have all five target languages."""
    keys = dict_keys()
    incomplete = {}
    for key in sorted(keys):
        entry = dict_entry(key)
        missing_langs = [
            lang
            for lang in TARGET_LANGS
            if f"{lang}:" not in entry
            and f"'{lang}':" not in entry
            and f'"{lang}":' not in entry
        ]
        if missing_langs:
            incomplete[key] = missing_langs
    assert not incomplete, incomplete


def test_template_loads_fragments_before_shared_i18n():
    """Template must load i18n-core, fragments, then i18n.js all before shared/i18n.js."""
    html = read_text(TEMPLATE)
    shared_pos = html.index("/static/shared/i18n.js")

    # i18n-core.js must appear before shared i18n
    assert "i18n-core.js" in html, "Template must load i18n-core.js"
    core_pos = html.index("i18n-core.js")
    assert core_pos < shared_pos, "i18n-core.js must load before shared/i18n.js"

    # All fragment script tags must appear before shared i18n
    for frag in i18n_fragment_files():
        assert frag.name in html, f"Template must load {frag.name}"
        frag_pos = html.index(frag.name)
        assert frag_pos < shared_pos, (
            f"{frag.name} must load before shared/i18n.js"
        )

    # i18n.js must load before shared/i18n.js (sets placeholders/callbacks)
    i18n_pos = html.index("i18n.js?m=dx_modelzoo")
    assert i18n_pos < shared_pos, "i18n.js must load before shared/i18n.js"


def test_template_loads_fragments_before_app_modules():
    """All dictionary fragments must load before app.js, catalog.js, detail.js, etc."""
    html = read_text(TEMPLATE)
    app_modules = ["app.js", "catalog.js", "detail.js", "inference.js", "tutorial.js"]
    # Find earliest app module script tag position
    app_positions = []
    for mod in app_modules:
        tag = f'src="/static/js/{mod}?m=dx_modelzoo"'
        if tag in html:
            app_positions.append(html.index(tag))
    earliest_app = min(app_positions)

    # All fragment script tags must load before earliest app module
    for frag in i18n_fragment_files():
        frag_tag = f'src="/static/js/{frag.name}'
        assert frag_tag in html, f"Template must load {frag.name}"
        frag_pos = html.index(frag_tag)
        assert frag_pos < earliest_app, (
            f"{frag.name} must load before app modules"
        )


def test_globals_available_after_i18n_js():
    """After i18n.js loads, _DX_I18N_DICT, _DX_I18N_PLACEHOLDERS, _DX_I18N_CALLBACKS must be set."""
    src = i18n_source()
    assert "window._DX_I18N_PLACEHOLDERS" in src
    assert "window._DX_I18N_CALLBACKS" in src
    # _DX_I18N_DICT is initialized in i18n-core.js; i18n.js must not wipe it.
    assert "window._DX_I18N_DICT = {}" not in src
