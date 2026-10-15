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
    assert re.search(r"render\(\w+, lastStatus\)", hook)
    assert "renderDevices(lastDevices)" in hook
    assert "Default credentials" in hook


def test_api_calls_are_relative_so_they_work_behind_the_launcher_proxy():
    js = (APP / "static/js/edge.js").read_text(encoding="utf-8")
    assert re.findall(r"api\('api/", js)
    assert "'/api/" not in js


def test_no_access_key_field_on_the_page():
    html = (APP / "templates/index.html").read_text(encoding="utf-8").lower()
    for word in ("access key id", "secret", 'type="password"'):
        assert word not in html


def test_stack_setup_card_sits_above_the_compile_form():
    html = (APP / "templates/index.html").read_text(encoding="utf-8")
    assert 'id="edgeSetup"' in html
    for kind in KINDS:
        assert html.index('id="edgeSetup"') < html.index(f'id="edgeStackList-{kind}"') \
            < html.index(f'id="edgeCompileForm-{kind}"')
    assert html.count("<dialog") == 1 and 'id="edgeDeleteDialog"' in html


KINDS = ("compiler", "greengrass")


def _panel(html: str, kind: str) -> str:
    start = html.index(f'id="edgePanel-{kind}"')
    end = html.find('id="edgePanel-', start + 1)
    return html[start:end if end > 0 else len(html)]


def test_tabs_are_an_accessible_tablist():
    html = (APP / "templates/index.html").read_text(encoding="utf-8")
    assert html.count('role="tablist"') == 1
    tabs = re.findall(r'<button[^>]*role="tab"[^>]*>', html)
    assert len(tabs) == 2
    for kind, tab in zip(KINDS, tabs):
        assert f'aria-controls="edgePanel-{kind}"' in tab and "aria-selected=" in tab
        assert f'id="edgeTab-{kind}"' in tab
        assert re.search(rf'id="edgePanel-{kind}"[^>]*role="tabpanel"|role="tabpanel"[^>]*id="edgePanel-{kind}"',
                         html)
    js = (APP / "static/js/edge.js").read_text(encoding="utf-8")
    assert "ArrowLeft" in js and "ArrowRight" in js
    assert re.search(r"try\s*\{[^}]*localStorage", js)


def test_each_tab_has_its_own_subscription_stacks_deploy_and_compile():
    html = (APP / "templates/index.html").read_text(encoding="utf-8")
    assert 'id="edgeTemplate"' not in html  # the tab fixes the template
    for kind in KINDS:
        panel = _panel(html, kind)
        for part in ("edgeSubs", "edgeStackList", "edgeDeployForm", "edgeCompileForm", "edgeStack"):
            assert f'id="{part}-{kind}"' in panel, (kind, part)


def test_greengrass_tab_has_devices_and_registration():
    html = (APP / "templates/index.html").read_text(encoding="utf-8")
    gg, comp = _panel(html, "greengrass"), _panel(html, "compiler")
    for part in ("edgeDevRows", "edgeRegForm", "edgeThing", "edgeScript", "edgeCopy", "edgeScriptDownload"):
        assert f'id="{part}"' in gg, part
        assert f'id="{part}"' not in comp, part
    js = (APP / "static/js/edge.js").read_text(encoding="utf-8")
    for api in ("api/aws/greengrass/devices", "api/aws/greengrass/components",
                "api/aws/greengrass/install-script", "navigator.clipboard", "new Blob"):
        assert api in js, api


def test_no_native_browser_dialogs():
    js = (APP / "static/js/edge.js").read_text(encoding="utf-8")
    for fn in ("confirm(", "alert(", "prompt("):
        assert not re.search(r"(?<![\w.])" + re.escape(fn), js), fn
        assert "window." + fn not in js
