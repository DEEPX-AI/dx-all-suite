"""DX Cloud page — every visible string is translated, and JS-written text repaints on a language change.

Static contracts (source text only, no browser).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dx_edge"
TARGET_LANGS = ("ko", "ja", "zh-CN", "zh-TW", "es")


def _dict() -> dict:
    src = (APP / "static/js/i18n.js").read_text(encoding="utf-8")
    body = src[src.index("{"):src.rindex("}") + 1]
    body = re.sub(r"^\s*//.*$", "", body, flags=re.M)
    body = re.sub(r"(\s)(ko|ja|es):", r'\1"\2":', body)
    body = re.sub(r",(\s*[}\]])", r"\1", body.replace("'", '"'))
    return json.loads(body)


def test_every_template_key_is_in_the_dictionary_in_every_language():
    html = (APP / "templates/index.html").read_text(encoding="utf-8")
    d = _dict()
    keys = set(re.findall(r'data-i18n="([^"]+)"', html))
    assert keys
    for key in keys:
        assert key in d, key
        assert all(d[key].get(lang) for lang in TARGET_LANGS), key


def test_every_runtime_key_is_in_the_dictionary():
    js = (APP / "static/js/edge.js").read_text(encoding="utf-8")
    d = _dict()
    state_msgs = js[js.index("var STATE_MSG"):js.index("};", js.index("var STATE_MSG"))]
    keys = set(re.findall(r"T\('([^']+)'\)", js)) | set(re.findall(r": '([^']+)'", state_msgs))
    keys |= {"pending", "running", "succeeded", "failed"}  # T(st.state)
    for key in keys:
        assert key in d, key


def test_runtime_text_repaints_on_language_change():
    js = (APP / "static/js/edge.js").read_text(encoding="utf-8")
    hook = js[js.index("DXI18n.onLangChange"):]
    assert "render(lastStatus)" in hook
    assert "Default credentials" in hook


def test_api_calls_are_relative_so_they_work_behind_the_launcher_proxy():
    js = (APP / "static/js/edge.js").read_text(encoding="utf-8")
    assert re.findall(r"api\('api/", js)
    assert "'/api/" not in js


def test_no_access_key_field_on_the_page():
    html = (APP / "templates/index.html").read_text(encoding="utf-8").lower()
    for word in ("access key id", "secret", 'type="password"'):
        assert word not in html
