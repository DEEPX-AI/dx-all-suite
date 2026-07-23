"""Static i18n contracts for DX App."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dx_app"
JS_DIR = APP / "static" / "js"
SHARED_CHARTS = ROOT / "shared" / "static" / "dx-charts.js"
TARGET_LANGS = ("ko", "ja", "zh-CN", "zh-TW", "es")

EXCLUDED_T_KEY_FILES = {"i18n.js", "reference.js"}
RUNTIME_JS_FILES = sorted(
    path
    for path in JS_DIR.glob("*.js")
    if path.name not in EXCLUDED_T_KEY_FILES
)

LOCALE_PIN_PATTERNS = (
    "toLocaleString('ko-KR'",
    'toLocaleString("ko-KR"',
    "toLocaleTimeString('ko-KR'",
    'toLocaleTimeString("ko-KR"',
    "toLocaleDateString('ko-KR'",
    'toLocaleDateString("ko-KR"',
)

CHART_HEADER_KEYS = {
    "Class",
    "Detections",
    "Avg Conf",
    "Handedness",
    "Count",
    "Avg Pixel %",
    "Mean Depth",
    "Min Depth",
    "Max Depth",
    "Frames",
    "Total Persons",
    "Total Faces",
    "Avg/Frame",
    "Avg Yaw",
    "Avg Pitch",
    "Avg Roll",
    "No detections recorded.",
    "No results recorded.",
    "No segmentation data.",
    "Waiting for data…",
    "No run data yet",
}

# Unsafe full-initializer calls that must NOT appear in refreshActivePageLanguage()
UNSAFE_REFRESH_CALLS = [
    "initRunPage(",
    "loadRunImages(",
    "initBenchPage(",
    "setABCols(",
    "initABImages(",
    "initModelZoo(",
    "initCompiler(",
    "loadOutputs(",
    "setupInit(",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def i18n_source() -> str:
    return read_text(JS_DIR / "i18n.js")


def dict_keys() -> set[str]:
    return set(re.findall(r"'((?:\\.|[^'\\])+)':\s*\{", i18n_source()))


def dict_entry(key: str) -> str:
    match = re.search(
        rf"'{re.escape(key)}':\s*\{{(.*?)\n\s*\}}\s*(?:,|\n)",
        i18n_source(),
        re.S,
    )
    return match.group(1) if match else ""


def t_keys(path: Path) -> set[str]:
    source = read_text(path)
    single = re.findall(r"\bT\('((?:\\.|[^'\\])+)'", source)
    double = re.findall(r'\bT\("((?:\\.|[^"\\])+)"', source)
    return set(single + double)


def test_app_t_keys_are_in_dictionary():
    keys = dict_keys()
    missing = {}
    for path in RUNTIME_JS_FILES:
        unresolved = sorted(k for k in t_keys(path) if k not in keys)
        if unresolved:
            missing[str(path.relative_to(APP))] = unresolved
    assert not missing, missing


def test_app_dictionary_entries_cover_target_languages():
    incomplete = {}
    required = set(CHART_HEADER_KEYS)
    for path in RUNTIME_JS_FILES:
        required.update(t_keys(path))
    for key in sorted(required):
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


def test_app_global_t5_defaults_to_en_and_keeps_legacy_order():
    source = i18n_source()
    assert "function _T5(ko, en, ja, zhCN, zhTW)" in source
    body = _extract_braced_body(source, "function _T5")
    assert "|| 'en'" in body
    assert "|| 'ko'" not in body
    assert "if (lang === 'ko') return ko || en;" in body
    assert "if (lang === 'ja') return ja || en;" in body


def test_app_no_visible_locale_formatting_is_pinned_to_ko_kr():
    offenders = {}
    for path in RUNTIME_JS_FILES:
        source = read_text(path)
        found = [pattern for pattern in LOCALE_PIN_PATTERNS if pattern in source]
        if found:
            offenders[str(path.relative_to(APP))] = found
    assert not offenders, offenders


def test_app_charts_translate_empty_states_and_summary_headers():
    source = read_text(SHARED_CHARTS)
    assert "ctx.fillText('Waiting for data" not in source
    assert "ctx.fillText('No run data yet" not in source
    assert "opts.emptyText" in source
    missing_usage = sorted(
        key for key in CHART_HEADER_KEYS
        if (
            f"T('{key}'" not in source
            and f'T("{key}"' not in source
            and f"_t('{key}'" not in source
            and f'_t("{key}"' not in source
        )
    )
    assert not missing_usage, missing_usage


def test_app_chart_pose_face_use_separate_labels():
    """POSE must use 'Total Persons', FACE must use 'Total Faces' — never combined."""
    source = read_text(SHARED_CHARTS)
    # Must NOT contain the combined generic label
    assert "Total Persons/Faces" not in source, (
        "charts.js still uses combined 'Total Persons/Faces' label"
    )
    # Must contain separate labels
    assert (
        "T('Total Persons'" in source
        or 'T("Total Persons"' in source
        or "_t('Total Persons'" in source
        or '_t("Total Persons"' in source
    ), (
        "charts.js missing T('Total Persons'...) for POSE tag"
    )
    assert (
        "T('Total Faces'" in source
        or 'T("Total Faces"' in source
        or "_t('Total Faces'" in source
        or '_t("Total Faces"' in source
    ), (
        "charts.js missing T('Total Faces'...) for FACE tag"
    )


def test_app_refresh_language_has_no_unsafe_initializers():
    """refreshActivePageLanguage() must not call full page initializers."""
    source = read_text(JS_DIR / "utils.js")
    body = _extract_braced_body(source, "function refreshActivePageLanguage(")
    found = [call for call in UNSAFE_REFRESH_CALLS if call in body]
    assert not found, (
        f"refreshActivePageLanguage() contains unsafe calls: {found}"
    )


def test_app_dictionary_has_no_duplicate_keys():
    """Every key in _DX_I18N_DICT must appear exactly once."""
    source = i18n_source()
    keys = re.findall(r"'((?:\\.|[^'\\])+)':\s*\{", source)
    from collections import Counter
    counts = Counter(keys)
    dupes = {k: v for k, v in counts.items() if v > 1}
    assert not dupes, f"Duplicate dictionary keys: {dupes}"


def test_app_i18n_callbacks_no_duplicate_side_effects():
    """_DX_I18N_CALLBACKS must NOT call _i18nOptions() or update topbar-title.

    refreshActivePageLanguage() in utils.js is the single dispatcher for both.
    """
    source = i18n_source()
    start = source.find("window._DX_I18N_CALLBACKS")
    assert start != -1, "window._DX_I18N_CALLBACKS not found in i18n.js"
    # Extract everything from assignment to the end of the statement (];)
    end = source.find("];", start)
    assert end != -1, "closing ]; for _DX_I18N_CALLBACKS not found"
    body = source[start:end + 2]
    assert "_i18nOptions()" not in body, (
        "_DX_I18N_CALLBACKS still calls _i18nOptions() — duplicates refreshActivePageLanguage()"
    )
    assert "topbar-title" not in body, (
        "_DX_I18N_CALLBACKS still updates topbar-title — duplicates refreshActivePageLanguage()"
    )


def test_app_utils_bench_running_guarded():
    """_benchRunning must be guarded with typeof check to avoid ReferenceError."""
    source = read_text(JS_DIR / "utils.js")
    assert re.search(r"typeof\s+_benchRunning\s*!==?\s*['\"]undefined['\"]", source), (
        "_benchRunning reference not guarded with typeof check"
    )


def test_app_utils_getlang_uses_window_dxi18n():
    """getLang() must access DXI18n via window.DXI18n for safety."""
    source = read_text(JS_DIR / "utils.js")
    match = re.search(r"function getLang\(\)\{.*?\}", source)
    assert match, "getLang() not found"
    body = match.group(0)
    assert "window.DXI18n" in body, (
        "getLang() should use window.DXI18n consistently"
    )


def test_app_utils_registers_refresh_on_lang_change():
    """lang-refresh.js must register refreshDxAppModuleLanguage via DXI18n.onLangChange."""
    source = read_text(JS_DIR / "lang-refresh.js")
    assert "DXI18n.onLangChange(refreshDxAppModuleLanguage)" in source, (
        "lang-refresh.js missing DXI18n.onLangChange(refreshDxAppModuleLanguage)"
    )
    assert "refreshActivePageLanguage" in source


def test_app_refresh_language_does_not_render_reference():
    """refreshActivePageLanguage() must NOT call DXAppReference.render.

    reference.js owns its own DXI18n.onLangChange callback; dispatching
    from utils.js as well causes a stale first render then correct second
    render (double-render bug).
    """
    source = read_text(JS_DIR / "utils.js")
    body = _extract_braced_body(source, "function refreshActivePageLanguage(")
    assert "DXAppReference.render" not in body, (
        "refreshActivePageLanguage() must not call DXAppReference.render — "
        "reference.js owns its own language-change callback"
    )
    assert "page==='reference'" not in body and 'page==="reference"' not in body, (
        "refreshActivePageLanguage() must not contain a reference page branch"
    )


def test_app_refresh_language_guards_render_models_page():
    """renderModelsPage() call must be guarded with typeof check."""
    source = read_text(JS_DIR / "utils.js")
    body = _extract_braced_body(source, "function refreshActivePageLanguage(")
    assert re.search(
        r"typeof\s+renderModelsPage\s*===?\s*['\"]function['\"]", body
    ), (
        "refreshActivePageLanguage() must guard renderModelsPage with "
        "typeof renderModelsPage === 'function'"
    )


def test_app_refresh_run_language_guards_cat_lookup():
    """refreshRunLanguage() must not access $('r-cat').value before null-check."""
    source = read_text(JS_DIR / "utils.js")
    body = _extract_braced_body(source, "function refreshRunLanguage(")
    # Must NOT contain the unguarded direct property access
    assert "$('r-cat').value" not in body, (
        "refreshRunLanguage() accesses $('r-cat').value before null-check"
    )
    # Must use a guarded pattern: catSel ? catSel.value : ''
    assert re.search(r"catSel\s*\?\s*catSel\.value\s*:\s*''", body), (
        "refreshRunLanguage() must guard catSel.value with ternary null-check"
    )


def test_app_i18n_js_no_missing_commas_before_es():
    """Every property line must end with a comma; catches missing comma before es: entries."""
    source = i18n_source()
    # Match lines ending with a quoted value (no trailing comma) followed by a line with es:
    pattern = re.compile(
        r"^(?P<line>.+?'(?:\\.|[^'\\])*')\s*$\n\s*es:",
        re.MULTILINE,
    )
    violations = pattern.findall(source)
    assert not violations, (
        f"Missing comma before es: on {len(violations)} line(s). "
        f"First: {violations[0]!r}"
    )


def test_app_i18n_js_no_missing_commas_any_lang():
    """General check: no property value line should lack a trailing comma inside an object."""
    source = i18n_source()
    # Match lines like   'zh-TW': '...'  (no comma) followed by   es:  or   'xx':
    pattern = re.compile(
        r"^(\s*'?[\w-]+'?\s*:\s*'(?:\\.|[^'\\])*')\s*$\n\s*'?[\w-]+'?\s*:",
        re.MULTILINE,
    )
    violations = pattern.findall(source)
    assert not violations, (
        f"Missing trailing comma on {len(violations)} property line(s). "
        f"First: {violations[0]!r}"
    )


def test_app_inference_hint_i18n_keys_cover_all_six_languages():
    """New inference error hint T() keys must have ko, ja, zh-CN, zh-TW, es."""
    hint_keys = [
        'Check that dx_engine is running. Real inference is not available in Mock mode.',
        'Check the model file or executable path.',
        'Inference timed out. Try again with a smaller input.',
    ]
    all_langs = ("ko", "ja", "zh-CN", "zh-TW", "es")
    incomplete = {}
    for key in hint_keys:
        entry = dict_entry(key)
        assert entry, f"Key {key!r} not found in i18n dictionary"
        missing = [
            lang for lang in all_langs
            if f"{lang}:" not in entry
            and f"'{lang}':" not in entry
            and f'"{lang}":' not in entry
        ]
        if missing:
            incomplete[key] = missing
    assert not incomplete, incomplete


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


def test_app_html_lang_defaults_to_en():
    """<html lang=...> must default to 'en', not 'ko', to avoid FOUC."""
    html = (ROOT / "dx_app" / "templates" / "index.html").read_text(encoding="utf-8")
    import re
    m = re.search(r'<html\s+lang="([^"]+)"', html)
    assert m, "<html lang=...> not found in index.html"
    assert m.group(1) == "en", (
        f'<html lang="{m.group(1)}"> should be <html lang="en">'
    )
