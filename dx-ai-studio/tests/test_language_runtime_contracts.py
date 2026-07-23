from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGS = ("en", "ja", "ko", "es", "zh-CN", "zh-TW")


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def _extract_js_call_args(source: str, call: str) -> list[str]:
    results = []
    marker = f"{call}("
    index = 0
    while True:
        start = source.find(marker, index)
        if start == -1:
            return results
        cursor = start + len(marker)
        depth = 1
        quote = None
        escaped = False
        while cursor < len(source) and depth:
            char = source[cursor]
            if quote:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote:
                    quote = None
            elif char in ("'", '"', "`"):
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            cursor += 1
        results.append(source[start + len(marker) : cursor - 1])
        index = cursor


def _split_js_args(args: str) -> list[str]:
    parts = []
    start = 0
    depth = 0
    quote = None
    escaped = False
    for index, char in enumerate(args):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in ("'", '"', "`"):
            quote = char
        elif char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(args[start:index].strip())
            start = index + 1
    parts.append(args[start:].strip())
    return parts


def test_shared_i18n_supports_six_language_runtime():
    source = read("shared/static/i18n.js")
    assert re.search(
        r"SUPPORTED_LANGS\s*=\s*\[\s*['\"]en['\"]\s*,\s*['\"]ja['\"]\s*,\s*['\"]ko['\"]\s*,\s*['\"]es['\"]\s*,\s*['\"]zh-CN['\"]\s*,\s*['\"]zh-TW['\"]\s*\]",
        source,
    )
    assert "'es': 'Español'" in source
    assert "'es': 'ES'" in source
    assert ".es" in source
    assert "dx-lang-change" in source


def test_shared_i18n_honors_empty_string_dictionary_values():
    source = read("shared/static/i18n.js")
    assert "Object.prototype.hasOwnProperty.call(e, _lang)" in source
    assert "return e[_lang];" in source
    assert "translated !== null" in source


def test_toolbar_and_launcher_language_pipeline_support_es():
    toolbar = read("shared/static/toolbar.js")
    assert "SUPPORTED_LANGS" in toolbar or "getSupportedLanguages" in toolbar
    assert "LANG_LABELS" in toolbar or "getLanguageLabel" in toolbar
    launcher_language = read("launcher/static/launcher-language.js")
    assert "postMessage" in launcher_language
    assert "lang-es" in launcher_language
    assert "'es'" in launcher_language or '"es"' in launcher_language


def test_launcher_language_state_supports_es():
    for rel_path in (
        "launcher/static/launcher-state.js",
        "launcher/static/about-deepx.js",
    ):
        source = read(rel_path)
        assert "'es'" in source


def test_launcher_frame_dynamic_copy_supplies_spanish_argument():
    source = read("launcher/static/launcher-app-frame.js")
    calls = _extract_js_call_args(source, "ns._lt")
    assert calls
    for args in calls:
        assert len(_split_js_args(args)) == len(LANGS), args


def test_locale_visibility_css_hides_spanish_in_other_languages():
    for rel_path in (
        "launcher/static/style.css",
        "dx_app/static/css/style.css",
        "dx_modelzoo/static/css/style.css",
        "dx_compiler/static/css/style.css",
        "dx_monitor/static/css/style.css",
        "dx_stream/static/css/stream.css",
        "dx_benchmark/static/css/style.css",
        "dx_planner/static/css/style.css",
    ):
        source = read(rel_path)
        assert ".es" in source, f"{rel_path} missing .es selector"
        assert (
            "lang-es" in source or 'lang="es"' in source
        ), f"{rel_path} missing Spanish language selector"
