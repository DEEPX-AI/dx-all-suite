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
