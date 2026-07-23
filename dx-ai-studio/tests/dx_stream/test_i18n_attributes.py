"""Static contracts for DX Stream attribute-based i18n completion."""

import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STREAM = ROOT / "dx_stream"
SHARED = ROOT / "shared"

SUPPORTED_LANG_TOKENS = ("ko:", "ja:", "'zh-CN':", "'zh-TW':")

PRESET_OPTION_KEYS = (
    "📋 Preset",
    "Demo 0 — Object Detection",
    "Demo 1 — OD (PPU)",
    "Demo 2 — Face Detection",
    "Demo 3 — Face (PPU)",
    "Demo 4 — Pose Estimation",
    "Demo 5 — Pose (PPU)",
    "Demo 6 — Segmentation",
    "Demo 7 — Multi-Object Tracking",
    "Demo 8 — Multi-Stream",
    "Demo 9 — RTSP Stream",
    "Demo 10 — Secondary Inference",
)

PLACEHOLDER_KEYS = ("Search...", "Search models...", "Search documentation...")
TITLE_KEYS = ("Zoom In", "Zoom Out", "Fit View", "Reset")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def stream_template() -> str:
    return read_text(STREAM / "templates" / "index.html")


def stream_app_js() -> str:
    return read_text(STREAM / "static" / "js" / "stream-app.js")


def stream_i18n_js() -> str:
    return read_text(STREAM / "static" / "js" / "stream-i18n.js")


def shared_i18n_js() -> str:
    return read_text(SHARED / "static" / "i18n.js")


def test_stream_i18n_js_has_commas_before_spanish_entries():
    src = stream_i18n_js()
    missing = re.findall(r"'zh-TW':\s*'(?:\\.|[^'\\])*'\s*\n\s*es:", src)
    assert not missing, missing[:5]


def _entry_for(js: str, key: str) -> str:
    marker = f"'{key}':"
    start = js.find(marker)
    assert start != -1, f"missing i18n key: {key}"
    end = js.find("},", start)
    assert end != -1, f"unterminated i18n entry: {key}"
    return js[start:end]


def _extract_braced_body(source: str, anchor: str) -> str:
    start = source.find(anchor)
    assert start != -1, f"anchor {anchor!r} not found"
    brace_start = source.find("{", start)
    assert brace_start != -1, f"opening brace for {anchor!r} not found"
    depth = 0
    for index in range(brace_start, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace_start + 1 : index]
    raise AssertionError(f"closing brace for {anchor!r} not found")


def test_stream_template_uses_shared_i18n_attributes_for_attribute_text():
    html = stream_template()
    for legacy in (
        "data-ko=",
        "data-en=",
        "data-placeholder-ko=",
        "data-placeholder-en=",
        "data-title-ko=",
        "data-title-en=",
    ):
        assert legacy not in html

    for key in PRESET_OPTION_KEYS:
        assert f'data-i18n="{key}"' in html

    assert html.count('data-i18n-placeholder="Search..."') == 2
    assert 'data-i18n-placeholder="Search models..."' in html
    assert 'id="ref-search" type="text" data-i18n-placeholder="Search documentation..."' in html

    for key in TITLE_KEYS:
        assert f'data-i18n-title="{key}"' in html


def test_stream_template_starts_in_release_neutral_english_language():
    html = stream_template()
    assert '<html lang="en">' in html
    assert 'class="lang-ko"' not in html


def test_stream_app_removes_legacy_attribute_language_loop():
    js = stream_app_js()
    for forbidden in (
        "[data-placeholder-ko]",
        "option[data-ko]",
        "[data-title-ko]",
        "data-placeholder-",
        "data-title-",
        "getAttribute('data-' + lang)",
        'getAttribute("data-" + lang)',
    ):
        assert forbidden not in js
    assert "DXI18n.onLangChange" in js
    assert "DXStream.nav(DXStream.S.currentPage)" in js


def test_stream_reference_search_uses_shared_placeholder_i18n():
    js = read_text(STREAM / "static" / "js" / "stream-reference.js")
    assert "searchEl.placeholder =" not in js


def test_stream_demo_cards_render_language_specific_metadata_dynamically():
    js = read_text(STREAM / "static" / "js" / "stream-demo.js")
    assert "function _demoText(d, field)" in js
    assert "_demoText(d, 'name')" in js
    assert "_demoText(d, 'description')" in js
    assert "d.name_ko" not in js
    assert "d.description_ko" not in js


def test_stream_demo_duplicate_start_shows_translated_toast():
    js = read_text(STREAM / "static" / "js" / "stream-demo.js")
    assert "if (DXStream._startingDemo)" in js
    assert "T('Demo start already in progress')" in js


def test_stream_demo_start_uses_status_polling_with_backoff():
    js = read_text(STREAM / "static" / "js" / "stream-demo.js")
    assert "function _demoStatusDelay" in js
    assert "async function _waitDemoStarted" in js
    assert "/api/pipeline/status" in js
    assert "_waitDemoStarted(id" in js


def test_stream_demo_start_polling_requires_matching_pipeline_id():
    js = read_text(STREAM / "static" / "js" / "stream-demo.js")
    body = _extract_braced_body(js, "async function _waitDemoStarted")
    assert "status.pipeline_id === pipelineId" in body
    assert re.search(r"status\.running\s*&&\s*pipelineMatch", body)


def test_stream_demo_text_falls_back_to_english_not_korean():
    js = read_text(STREAM / "static" / "js" / "stream-demo.js")
    body = _extract_braced_body(js, "function _demoText")
    assert "d[field + '_en']" in body
    assert "d[field + '_ko']" not in body


def test_stream_i18n_dictionary_covers_attribute_keys():
    js = stream_i18n_js()
    for key in PRESET_OPTION_KEYS + PLACEHOLDER_KEYS + TITLE_KEYS:
        entry = _entry_for(js, key)
        missing = [token for token in SUPPORTED_LANG_TOKENS if token not in entry]
        assert not missing, f"{key} missing {missing}"


def test_stream_i18n_dictionary_removes_stale_demo_preset_keys():
    js = stream_i18n_js()
    for key in (
        "Demo 10 — Classification",
        "Demo 11 — OBB Detection",
        "Demo 12 — Secondary Inference",
    ):
        assert f"'{key}':" not in js


def test_shared_i18n_supports_explicit_placeholder_and_title_attributes():
    js = shared_i18n_js()
    assert "data-i18n-placeholder" in js
    assert "data-i18n-title" in js
    assert re.search(r"setAttribute\(['\"]placeholder['\"],\s*translated\s*!==\s*null\s*\?\s*translated\s*:\s*key\)", js)
    assert re.search(r"setAttribute\(['\"]title['\"],\s*translated\s*!==\s*null\s*\?\s*translated\s*:\s*key\)", js)


# Behavior-level test: runs shared/static/i18n.js in Node.js

_JS_HARNESS = r"""
'use strict';
const fs = require('fs');
const assert = require('assert');

// --- Minimal DOM stub ---------------------------------------------------
const _allElements = [];

function _matchesSelector(el, selector) {
  return selector.split(',').some(s => _matchesSingle(el, s.trim()));
}

function _matchesSingle(el, sel) {
  // [attr]
  let m = sel.match(/^\[([^\]=]+)\]$/);
  if (m) return el._attrs.hasOwnProperty(m[1]);
  // tag[attr]
  m = sel.match(/^(\w+)\[([^\]]+)\]$/);
  if (m) return el._tag === m[1].toLowerCase() && el._attrs.hasOwnProperty(m[2]);
  // span.class  /  tag.class
  m = sel.match(/^(\w+)\.(.+)$/);
  if (m) return el._tag === m[1].toLowerCase() && el._classes.has(m[2]);
  // #id
  m = sel.match(/^#(.+)$/);
  if (m) return el._attrs.id === m[1];
  // descendant selectors (small .xx) — not tested, return false
  return false;
}

function _qsa(sel) {
  return _allElements.filter(e => _matchesSelector(e, sel));
}
function _qs(sel) { return _qsa(sel)[0] || null; }

function makeElement(tag, attrs) {
  const el = {
    _tag: tag.toLowerCase(),
    _attrs: Object.assign({}, attrs || {}),
    _classes: new Set(),
    childNodes: [1],          // non-empty so _translateEl doesn't bail
    children: [],
    style: {},
    textContent: '',
    innerHTML: '',
    dataset: {},
    parentNode: null,
    classList: {
      _ref: null,
      add(c) { this._ref._classes.add(c); },
      remove(c) { this._ref._classes.delete(c); },
      contains(c) { return this._ref._classes.has(c); },
      toggle(c, force) { if (force) this._ref._classes.add(c); else this._ref._classes.delete(c); },
    },
    getAttribute(n) { return this._attrs[n] !== undefined ? this._attrs[n] : null; },
    setAttribute(n, v) { this._attrs[n] = v; },
    querySelector: _qs,
    querySelectorAll: _qsa,
    addEventListener() {},
    insertBefore() {},
  };
  el.classList._ref = el;
  // populate dataset from data- attrs
  for (const [k, v] of Object.entries(el._attrs)) {
    if (k.startsWith('data-')) {
      const camel = k.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      el.dataset[camel] = v;
    }
  }
  _allElements.push(el);
  return el;
}

// --- Global stubs -------------------------------------------------------
const _storage = {};
global.localStorage = {
  getItem(k) { return _storage[k] || null; },
  setItem(k, v) { _storage[k] = v; },
};

const body = makeElement('body', {});
_allElements.pop(); // body is not a regular element

global.document = {
  readyState: 'complete',
  body: body,
  documentElement: { lang: 'en' },
  querySelectorAll: _qsa,
  querySelector: _qs,
  addEventListener() {},
  createElement(tag) { return makeElement(tag, {}); },
};

global.window = global;
global.window.addEventListener = function() {};

// --- i18n dictionary & placeholders for test ----------------------------
global.window._DX_I18N_DICT = DICT_PLACEHOLDER;
global.window._DX_I18N_PLACEHOLDERS = PH_PLACEHOLDER;
global.window._DX_I18N_SELECTORS = '';
global.window._DX_I18N_CALLBACKS = [];

// --- Create test DOM elements -------------------------------------------
const elI18n = makeElement('span', {'data-i18n': 'Hello'});
elI18n.textContent = 'Hello';

const elI18nHtml = makeElement('div', {'data-i18n-html': '<b>Bold</b>'});
elI18nHtml.innerHTML = '<b>Bold</b>';

const elPlaceholder = makeElement('input', {'data-i18n-placeholder': 'Search...'});
elPlaceholder._attrs['placeholder'] = 'Search...';

const elTitle = makeElement('button', {'data-i18n-title': 'Zoom In'});
elTitle._attrs['title'] = 'Zoom In';

// Legacy _DX_I18N_PLACEHOLDERS element
const elLegacyPh = makeElement('input', {'placeholder': 'Legacy placeholder'});

// --- Load and eval i18n.js (suppress setTimeout to run synchronously) ---
const _origTimeout = global.setTimeout;
global.setTimeout = function(fn) { fn(); };

const src = fs.readFileSync(I18N_JS_PATH, 'utf-8');
eval(src);

global.setTimeout = _origTimeout;

// --- Assertions ---------------------------------------------------------
const LANGS = ['ko', 'ja', 'zh-CN', 'zh-TW'];
const dict = global.window._DX_I18N_DICT;

for (const lang of LANGS) {
  DXI18n.setLang(lang);
  assert.strictEqual(DXI18n.lang, lang, 'lang getter for ' + lang);

  // [data-i18n] textContent
  const expectText = dict['Hello'][lang];
  assert.strictEqual(elI18n.textContent, expectText,
    `[data-i18n] text for ${lang}: got "${elI18n.textContent}", expected "${expectText}"`);

  // [data-i18n-html] innerHTML
  const expectHtml = dict['<b>Bold</b>'][lang];
  assert.strictEqual(elI18nHtml.innerHTML, expectHtml,
    `[data-i18n-html] html for ${lang}: got "${elI18nHtml.innerHTML}", expected "${expectHtml}"`);

  // [data-i18n-placeholder]
  const expectPh = dict['Search...'][lang];
  assert.strictEqual(elPlaceholder.getAttribute('placeholder'), expectPh,
    `[data-i18n-placeholder] for ${lang}: got "${elPlaceholder.getAttribute('placeholder')}", expected "${expectPh}"`);

  // [data-i18n-title]
  const expectTitle = dict['Zoom In'][lang];
  assert.strictEqual(elTitle.getAttribute('title'), expectTitle,
    `[data-i18n-title] for ${lang}: got "${elTitle.getAttribute('title')}", expected "${expectTitle}"`);

  // _DX_I18N_PLACEHOLDERS legacy
  const legacyEntry = global.window._DX_I18N_PLACEHOLDERS['Legacy placeholder'];
  const expectLegacy = (typeof legacyEntry === 'object') ? legacyEntry[lang] : null;
  if (expectLegacy) {
    assert.strictEqual(elLegacyPh.getAttribute('placeholder'), expectLegacy,
      `_DX_I18N_PLACEHOLDERS for ${lang}: got "${elLegacyPh.getAttribute('placeholder')}", expected "${expectLegacy}"`);
  }
}

// --- Restore to English -------------------------------------------------
DXI18n.setLang('en');
assert.strictEqual(DXI18n.lang, 'en', 'lang restored to en');

// [data-i18n] should show English key
assert.strictEqual(elI18n.textContent, 'Hello',
  `[data-i18n] en restore: got "${elI18n.textContent}"`);

// [data-i18n-html] should show English key
assert.strictEqual(elI18nHtml.innerHTML, '<b>Bold</b>',
  `[data-i18n-html] en restore: got "${elI18nHtml.innerHTML}"`);

// [data-i18n-placeholder] should fall back to English key
assert.strictEqual(elPlaceholder.getAttribute('placeholder'), 'Search...',
  `[data-i18n-placeholder] en restore: got "${elPlaceholder.getAttribute('placeholder')}"`);

// [data-i18n-title] should fall back to English key
assert.strictEqual(elTitle.getAttribute('title'), 'Zoom In',
  `[data-i18n-title] en restore: got "${elTitle.getAttribute('title')}"`);

// Legacy placeholder should restore
const origPh = elLegacyPh.getAttribute('data-i18n-ph-orig');
if (origPh) {
  assert.strictEqual(elLegacyPh.getAttribute('placeholder'), origPh,
    `_DX_I18N_PLACEHOLDERS en restore: got "${elLegacyPh.getAttribute('placeholder')}"`);
}

console.log('ALL ASSERTIONS PASSED');
"""


import pytest


def _load_stream_server():
    import importlib.util
    import sys

    module_name = "dx_stream_server_i18n_test"
    spec = importlib.util.spec_from_file_location(
        module_name, str(STREAM / "server.py"),
    )
    assert spec and spec.loader
    stream_server = importlib.util.module_from_spec(spec)

    old_path = sys.path[:]
    sys.path.insert(0, str(STREAM))
    sys.path.insert(0, str(ROOT))
    try:
        sys.modules[module_name] = stream_server
        spec.loader.exec_module(stream_server)
        return stream_server
    finally:
        sys.path[:] = old_path
        sys.modules.pop(module_name, None)


@pytest.mark.parametrize(
    ("message", "lang", "expected", "forbidden"),
    [
        ("GStreamer elements", "en", "Elements tab", "Pipeline Builder"),
        ("GStreamer エレメント", "ja", "Elements タブ", "Pipeline Builder"),
        ("GStreamer 元素", "zh-CN", "Elements 选项卡", "Pipeline Builder"),
        ("GStreamer 元素", "zh-TW", "Elements 分頁", "Pipeline Builder"),
    ],
)
def test_stream_fallback_routes_element_queries_to_elements_response(message, lang, expected, forbidden):
    """Element-related queries should route to Elements rule, not broad Pipeline."""
    stream_server = _load_stream_server()
    result = stream_server._chat_engine.fallback.respond(message, lang=lang)
    assert expected in result["reply"], f"Expected Elements response: {result['reply']}"
    assert forbidden not in result["reply"], f"Should not route to Pipeline: {result['reply']}"


@pytest.mark.parametrize(
    ("message", "lang", "expected"),
    [
        ("パイプライン", "ja", "Pipeline Builder タブ"),
        ("管道", "zh-CN", "Pipeline Builder 选项卡"),
        ("管線", "zh-TW", "Pipeline Builder 分頁"),
        ("ストリーミング", "ja", "WebRTC ストリーミング"),
        ("流媒体", "zh-CN", "WebRTC 流媒体"),
        ("串流", "zh-TW", "WebRTC 串流"),
    ],
)
def test_stream_fallback_routes_localized_app_keywords(message, lang, expected):
    stream_server = _load_stream_server()
    result = stream_server._chat_engine.fallback.respond(message, lang=lang)
    assert expected in result["reply"], f"message={message!r}, reply={result['reply']}"


def test_stream_server_app_fallback_rules_cover_all_supported_languages():
    source = read_text(STREAM / "server.py")
    fallback_block = source[source.index("fallback_rules=["):source.index("class DXStreamHandler")]
    for marker in ('"ko":', '"en":', '"ja":', '"zh-CN":', '"zh-TW":'):
        assert fallback_block.count(marker) >= 3, marker
    shared_fallback = read_text(ROOT / "shared" / "chat" / "fallback.py")
    assert 'response.get(lang, response["en"])' not in shared_fallback


@pytest.mark.requires_node
def test_shared_i18n_behavior_runtime(tmp_path):
    """Run shared/static/i18n.js in Node.js and verify DOM-level behavior."""
    node = shutil.which("node")
    if not node:
        pytest.skip("node is required for shared i18n behavior test")

    i18n_path = SHARED / "static" / "i18n.js"
    assert i18n_path.exists(), f"{i18n_path} not found"

    test_dict = {
        "Hello": {
            "ko": "안녕하세요",
            "ja": "こんにちは",
            "zh-CN": "你好",
            "zh-TW": "你好",
        },
        "<b>Bold</b>": {
            "ko": "<b>굵게</b>",
            "ja": "<b>太字</b>",
            "zh-CN": "<b>粗体</b>",
            "zh-TW": "<b>粗體</b>",
        },
        "Search...": {
            "ko": "검색...",
            "ja": "検索...",
            "zh-CN": "搜索...",
            "zh-TW": "搜尋...",
        },
        "Zoom In": {
            "ko": "확대",
            "ja": "ズームイン",
            "zh-CN": "放大",
            "zh-TW": "放大",
        },
    }
    test_placeholders = {
        "Legacy placeholder": {
            "ko": "레거시",
            "ja": "レガシー",
            "zh-CN": "旧版",
            "zh-TW": "舊版",
        },
    }

    harness = _JS_HARNESS.replace(
        "DICT_PLACEHOLDER", json.dumps(test_dict, ensure_ascii=False)
    ).replace(
        "PH_PLACEHOLDER", json.dumps(test_placeholders, ensure_ascii=False)
    ).replace(
        "I18N_JS_PATH", json.dumps(str(i18n_path))
    )

    harness_path = tmp_path / "test_i18n_behavior.js"
    harness_path.write_text(harness, encoding="utf-8")
    result = subprocess.run(
        [node, str(harness_path)],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        pytest.fail(
            f"Node.js harness failed (rc={result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    assert "ALL ASSERTIONS PASSED" in result.stdout
