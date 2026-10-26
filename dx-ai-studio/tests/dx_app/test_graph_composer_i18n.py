"""Strings the Graph Composer shows without a literal T('...') call are in the dx_app dictionary, in six languages.

tests/dx_app/test_i18n.py checks every T('literal') in dx_app/static/js. The shared canvas (shared/static/
dx-graph-canvas.js) and the document model (graph-doc.js) take a translator instead and list their keys in STRINGS;
this extends the same gate to those lists.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tests.browser_support import resolve_node_executable
from tests.dx_app.test_i18n import TARGET_LANGS, dict_entry, dict_keys
from tests.installed_sdk import require_graph_examples

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [ROOT / "shared/static/dx-graph-core.js", ROOT / "shared/static/dx-graph-canvas.js",
           ROOT / "dx_app/static/js/graph-doc.js"]

_JS = """
const fs = require('fs'), vm = require('vm');
const sandbox = {window: {}};
for (const f of process.argv.slice(1)) vm.runInNewContext(fs.readFileSync(f, 'utf8'), sandbox);
console.log(JSON.stringify({canvas: sandbox.window.DXGraphCanvas.STRINGS, doc: sandbox.window.GraphDoc.STRINGS}));
"""


@pytest.fixture(scope="module")
def strings():
    node = resolve_node_executable()
    if not node:
        pytest.skip("node is required to read the STRINGS lists")
    proc = subprocess.run([node, "-e", _JS, *map(str, SOURCES)], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_canvas_and_document_strings_are_dictionary_keys(strings):
    keys = dict_keys()
    missing = sorted(k for k in strings["canvas"] + strings["doc"] if k not in keys)
    assert not missing, missing


def test_canvas_and_document_strings_cover_every_language(strings):
    incomplete = {}
    for key in strings["canvas"] + strings["doc"]:
        entry = dict_entry(key)
        lacking = [lang for lang in TARGET_LANGS if f"{lang}:" not in entry and f"'{lang}':" not in entry]
        if lacking:
            incomplete[key] = lacking
    assert not incomplete, incomplete


def test_the_canvas_draws_no_literal_english_outside_strings():
    """Every t('...') the canvas calls is in its STRINGS list, so this gate sees all of them."""
    import re
    src = (ROOT / "shared/static/dx-graph-canvas.js").read_text(encoding="utf-8")
    listed = set(re.findall(r"'([^']+)'", src[src.index("var STRINGS = ["):src.index("];", src.index("var STRINGS = ["))]))
    used = set(re.findall(r"\bt\('([^']+)'\)", src))
    assert used <= listed, sorted(used - listed)


# Korean keeps English technical terms as written instead of spelling them out in Hangul (suite language rule).
_HANGUL_SPELLINGS = ("컴포저", "인스펙터")


def test_korean_keeps_composer_and_inspector_in_english():
    sources = {p: p.read_text(encoding="utf-8") for p in (ROOT / "dx_app/static/js/i18n.js",
                                                          ROOT / "dx_app/static/js/tutorial.js")}
    found = [(p.name, w) for p, text in sources.items() for w in _HANGUL_SPELLINGS if w in text]
    assert not found, found
    assert "ko: '그래프 Composer'" in dict_entry("Graph Composer"), "graph keeps its established Korean loanword; Composer stays English"


# Phase 2: every string of the composer's scripts in six languages, and Korean keeps English technical terms there
# instead of spelling them in Hangul (the older Run page entries, such as its Live display, are not the composer's).
GRAPH_SCRIPTS = sorted((ROOT / "dx_app/static/js").glob("graph-*.js"))
_P2_HANGUL_SPELLINGS = _HANGUL_SPELLINGS + ("라이브", "로직", "갤러리", "템플릿", "스트리밍", "트래킹", "폴리곤")


def _graph_keys(strings) -> list[str]:
    import re
    keys = set(strings["canvas"] + strings["doc"])
    for p in GRAPH_SCRIPTS:
        src = p.read_text(encoding="utf-8")
        keys |= {k.replace("\\'", "'") for k in re.findall(r"\bT\('((?:[^'\\]|\\.)*)'\)", src)}
        if p.name == "graph-palette.js" and "var LOGIC_LABELS" in src:
            block = src[src.index("var LOGIC_LABELS"):src.index("};", src.index("var LOGIC_LABELS"))]
            keys |= set(re.findall(r": '([^']+)'", block))
        if p.name == "graph-palette.js" and "var TEMPLATE_TEXT" in src:
            block = src[src.index("var TEMPLATE_TEXT"):src.index("};", src.index("var TEMPLATE_TEXT"))]
            keys |= set(re.findall(r"'([^']+)'", block))
    return sorted(keys)


def _ko(entry: str) -> str:
    import re
    m = re.search(r"\bko:\s*'((?:[^'\\]|\\.)*)'", entry)
    return m.group(1) if m else ""


def test_every_composer_string_covers_every_language(strings):
    incomplete = {}
    for key in _graph_keys(strings):
        entry = dict_entry(key)
        lacking = [lang for lang in TARGET_LANGS if f"{lang}:" not in entry and f"'{lang}':" not in entry]
        if lacking:
            incomplete[key] = lacking
    assert not incomplete, incomplete


def test_korean_composer_strings_keep_english_technical_terms(strings):
    import re
    found = {k: w for k in _graph_keys(strings) for w in _P2_HANGUL_SPELLINGS if w in _ko(dict_entry(k))}
    assert not found, found
    tut = (ROOT / "dx_app/static/js/tutorial.js").read_text(encoding="utf-8")
    section = tut[tut.index("{ id:'graph'"):tut.index("{ id:'lab'")]
    ko = re.findall(r"\bko:\s*'((?:[^'\\]|\\.)*)'", section)
    assert ko and not [(s, w) for s in ko for w in _P2_HANGUL_SPELLINGS if w in s]


# The logic blocks' texts come from dx_app's --list-ops in English only; Studio translates each op's summary and each
# param's label and help in dx_app/static/js/i18n.js (window._DX_GRAPH_OPS_I18N). `en` is dx_app's own text, which
# the inspector compares before using a translation, so it has to match the recorded --list-ops output exactly.
_OPS_JS = """
const fs = require('fs'), vm = require('vm');
const sandbox = {window: {}};
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), sandbox);
console.log(JSON.stringify(sandbox.window._DX_GRAPH_OPS_I18N || null));
"""
ALL_LANGS = ("en",) + TARGET_LANGS


@pytest.fixture(scope="module")
def op_texts():
    node = resolve_node_executable()
    if not node:
        pytest.skip("node is required to read the logic block translations")
    proc = subprocess.run([node, "-e", _OPS_JS, str(ROOT / "dx_app/static/js/i18n.js")], capture_output=True,
                          text=True, check=False)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def _logic_ops():
    ops = json.loads((ROOT / "tests/dx_app/fixtures/graph/list_ops.json").read_text(encoding="utf-8"))
    return [o for o in ops if o.get("type") == "logic"]


def test_every_logic_op_and_param_is_translated_into_six_languages(op_texts):
    assert op_texts, "window._DX_GRAPH_OPS_I18N is missing"
    lacking = {}
    for op in _logic_ops():
        entry = op_texts.get(op["op"]) or {}
        texts = {"summary": entry.get("summary")}
        for p in op["params"]:
            spec = ((entry.get("params") or {}).get(p["name"])) or {}
            texts[p["name"] + ".label"] = spec.get("label")
            texts[p["name"] + ".help"] = spec.get("help")
        for where, t in texts.items():
            miss = [lang for lang in ALL_LANGS if not (t or {}).get(lang)]
            if miss:
                lacking[op["op"] + ":" + where] = miss
    assert not lacking, lacking
    assert sorted(op_texts) == sorted(o["op"] for o in _logic_ops()), "one entry per logic op of --list-ops"


def test_the_english_of_each_translation_is_dx_apps_text(op_texts):
    stale = {}
    for op in _logic_ops():
        entry = op_texts.get(op["op"]) or {}
        if (entry.get("summary") or {}).get("en") != op["summary"]:
            stale[op["op"] + ":summary"] = op["summary"]
        for p in op["params"]:
            got = (((entry.get("params") or {}).get(p["name"]) or {}).get("help") or {}).get("en")
            if p.get("help") and got != p["help"]:
                stale[op["op"] + ":" + p["name"]] = p["help"]
    assert not stale, stale


def test_korean_logic_texts_keep_english_technical_terms(op_texts):
    def strings(v):
        if isinstance(v, dict):
            return [s for k, x in v.items() for s in ([x] if k == "ko" and isinstance(x, str) else strings(x))]
        return []
    ko = strings(op_texts)
    assert len(ko) > 40
    found = [(s, w) for s in ko for w in _P2_HANGUL_SPELLINGS + ("트랙", "레코드", "스텁", "임베딩", "갤러리") if w in s]
    assert not found, found


def test_the_font_subsets_draw_every_glyph_of_the_logic_texts(op_texts):
    """scripts/font_coverage_gate.py reads the dictionaries; these translations sit beside them, so they are checked
    here against the same font chain (rebuild with `python -m scripts.build_font_subsets` when this fails)."""
    from fontTools.ttLib import TTFont

    from scripts.font_coverage_gate import CHAIN, FONTS, SOURCES
    from scripts.font_glyphs import is_cjk
    specs = json.loads(SOURCES.read_text(encoding="utf-8"))
    cmaps = {s["lang"]: TTFont(FONTS / s["output"]).getBestCmap() for s in specs.values() if s["lang"] != "latin"}
    missing: dict[str, set[str]] = {}

    def walk(v):
        for k, x in v.items():
            if isinstance(x, dict):
                walk(x)
            elif k in CHAIN:
                missing.setdefault(k, set()).update(
                    ch for ch in x if is_cjk(ord(ch)) and not any(ord(ch) in cmaps[f] for f in CHAIN[k]))
    walk(op_texts)
    assert not {k: v for k, v in missing.items() if v}, missing


# Error keys of the graph routes that the page shows through the dictionary (translatedError: the key's text, then the
# server's English message), not through a sentence of its own in graph-run.js / graph-live.js / graph-inspector.js.
DICTIONARY_ERROR_KEYS = ("invalid_stream", "gallery_exists", "gallery_outside_roots", "frame_too_large",
                         "gallery_busy", "invalid_folder", "invalid_slot",
                         # Phase 3: the export's refusals (graph_export.py and dx_app's exporter)
                         "export_busy", "export_name_invalid", "export_failed", "model_file_missing",
                         "model_unknown", "model_not_ready", "user_name_invalid", "user_kind_invalid",
                         "user_kind_conflict", "input_missing", "gallery_missing", "graph_unreadable",
                         "invalid_input", "path_leak")

# Phase 3: the strings graph-export.js and the export button show (graph-export.js is checked by
# test_every_composer_string_covers_every_language as soon as it exists, Task 7).
EXPORT_STRINGS = ("Export C++ project", "Project folder name",
                  "Letters, digits, _ and -, starting with a letter (at most 48).",
                  "Include the model files ({size})",
                  "Without them, setup.sh downloads the models from the DEEPX Model Zoo.",
                  "User logic stubs to fill in", "for node {nodes} (input: {kind})",
                  "The project holds the graph, the engine with only these models, a main.cpp, setup.sh, run.sh and a "
                  "README. It builds and runs anywhere the DEEPX runtime is installed.",
                  "Exporting…", "Exported to {folder}", "Download .zip ({size})", "Build and run it:",
                  "This dx_app build cannot export projects. Update dx_app to use it.",
                  "Not enough disk space: the export needs {need} and {free} is free.", "The export failed.",
                  "Reading what the export will hold…", "No User logic block: the project runs the graph as it is.",
                  "Export needs a graph without problems and a dx_app that can export projects.", "Close",
                  "Inputs", "for source {source}", "no input: give one with --input",
                  "An uploaded image is not exported: a source uses the sample picked for it, else its own input.",
                  "Every model must be installed to include the files.",
                  "not installed ({size})", "not installed, size unknown", "at least {size}", "size unknown")


@pytest.mark.parametrize("key", EXPORT_STRINGS)
def test_the_export_strings_read_in_every_language(key):
    entry = dict_entry(key)
    lacking = [lang for lang in TARGET_LANGS if f"{lang}:" not in entry and f"'{lang}':" not in entry]
    assert entry and not lacking, (key, lacking)
    assert not [w for w in _P2_HANGUL_SPELLINGS if w in _ko(entry)], _ko(entry)


@pytest.mark.parametrize("key", DICTIONARY_ERROR_KEYS)
def test_graph_error_keys_read_in_every_language(key):
    entry = dict_entry(key)
    lacking = [lang for lang in TARGET_LANGS if f"{lang}:" not in entry and f"'{lang}':" not in entry]
    assert entry and not lacking, (key, lacking)
    assert not [w for w in _P2_HANGUL_SPELLINGS if w in _ko(entry)], _ko(entry)


def test_every_dx_app_example_has_a_name_in_the_palette():
    """TEMPLATE_TEXT (graph-palette.js) names exactly the sample graphs dx_app ships."""
    import re
    from dx_app.core import config
    d = require_graph_examples()
    src = (ROOT / "dx_app/static/js/graph-palette.js").read_text(encoding="utf-8")
    block = src[src.index("var TEMPLATE_TEXT"):src.index("};", src.index("var TEMPLATE_TEXT"))]
    assert set(re.findall(r"^\s+(\w+): \[", block, re.M)) == {p.stem for p in d.glob("*.json")}
