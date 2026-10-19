"""The glass bar under the stage: hierarchy, offline behaviour, and DEEPX Agent moved into the chat."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "launcher" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
CHAT = (ROOT / "shared" / "chat" / "static" / "chat-widget.js").read_text(encoding="utf-8")
TUTORIAL = (STATIC / "tutorial.js").read_text(encoding="utf-8")

TITLE = ("Go deeper at DEEPX Developers", "https://developer.deepx.ai/")
PRIMARY = [
    ("Get Started", "https://developer.deepx.ai/article/get-started/",
     "Install the SDK and run your first model"),
    ("S/W Download", "https://developer.deepx.ai/sw-download/",
     "DX-RT, DX-COM and drivers for every release"),
]
SECONDARY = [
    ("Tech Docs", "https://developer.deepx.ai/tech-docs/", "API references and guides for the SDK"),
    ("Documents", "https://developer.deepx.ai/document-download/", "Datasheets, manuals and application notes"),
    ("Model Zoo", "https://developer.deepx.ai/modelzoo/", "The full catalogue on developer.deepx.ai"),
    ("GitHub", "https://github.com/DEEPX-AI", "DEEPX-AI source code and examples"),
    ("deepx.ai", "https://deepx.ai", "Company, products and news"),
]
AGENT_URL = "https://deepx.rapidflare.ai/"
AGENT_TITLE = "Open DEEPX Agent on the web"
LANGS = ("ko", "ja", "es", "'zh-CN'", "'zh-TW'")


def _bar() -> str:
    return HTML[HTML.index('id="homeBar"'):HTML.index("</footer>", HTML.index('id="homeBar"'))]


def _links() -> list[tuple[str, str, str]]:
    """Links in the bar: (class, href, inner HTML)."""
    return re.findall(r'<a class="([^"]+)"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', _bar(), re.S)


def _entry(src: str, key: str) -> str:
    m = re.search(r"'" + re.escape(key) + r"':\s*\{([^}]*)\}", src)
    assert m, f"사전에 {key!r} 가 없다"
    return m.group(1)


def _speaks_six(src: str, key: str) -> None:
    entry = _entry(src, key)
    for lang in LANGS:
        assert re.search(r"(?:^|[\s,{])" + re.escape(lang) + r"\s*:", entry), (key, lang)


def test_the_title_names_where_the_bar_goes():
    cls, href, inner = _links()[0]
    assert "bar-title" in cls.split()
    assert href == TITLE[1]
    assert f'data-i18n="{TITLE[0]}"' in inner


def test_two_primary_pills_then_five_links_in_order():
    rest = _links()[1:]
    primary = [(h, i) for c, h, i in rest if "is-primary" in c.split()]
    plain = [(h, i) for c, h, i in rest if "is-primary" not in c.split()]
    assert [h for h, _ in primary] == [p[1] for p in PRIMARY]
    assert [h for h, _ in plain] == [s[1] for s in SECONDARY]
    for (href, inner), (label, _, desc) in zip(primary + plain, PRIMARY + SECONDARY):
        assert f'data-i18n="{label}"' in inner, href
        assert f'data-i18n="{desc}"' in inner, f"{href} 에 한 줄 설명이 없다"
        svg = re.search(r"<svg [^>]*>", inner)
        assert svg and 'aria-hidden="true"' in svg.group(0), f"{href} 에 장식 아이콘이 없다"


def test_every_link_opens_a_new_tab_safely():
    for _, href, _ in _links():
        tag = re.search(r'<a [^>]*href="' + re.escape(href) + r'"[^>]*>', _bar()).group(0)
        assert 'target="_blank"' in tag and 'rel="noopener noreferrer"' in tag, href


def test_the_web_agent_left_the_bar_for_the_chat():
    """The web chatbot lives in "Open web version" inside the chat button."""
    assert AGENT_URL not in _bar()
    assert 'data-i18n="DEEPX Agent"' not in _bar()
    head = CHAT[CHAT.index("'<div class=\"dx-chat-header\">'"):CHAT.index("dx-chat-settings-panel")]
    link = re.search(r'<a [^>]*href="' + re.escape(AGENT_URL) + r'"[^>]*>', head)
    assert link, "챗 머리에 DEEPX Agent 링크가 없다"
    assert 'target="_blank"' in link.group(0) and 'rel="noopener noreferrer"' in link.group(0)
    assert f'data-chat-tip="{AGENT_TITLE}"' in head, "링크 설명은 key 로 달아 언어마다 번역한다"


def test_the_chat_link_speaks_six_languages_and_follows_the_language():
    _speaks_six(CHAT, AGENT_TITLE)
    on_change = CHAT[CHAT.index("DXI18n.onLangChange(function() {"):]
    on_change = on_change[:on_change.index("_renderSource();")]   # the status line
    assert "_relabel()" in on_change, "언어를 바꿔도 링크 설명이 그대로다"
    relabel = CHAT[CHAT.index("function _relabel()"):CHAT.index("function _buildDOM()")]
    assert "[data-chat-tip]" in relabel and "aria-label" in relabel
    # On-screen check: tests/shared/test_chat_widget_lang_browser.py


@pytest.mark.parametrize("key", [TITLE[0], "Documents", "Offline"] + [p[2] for p in PRIMARY + SECONDARY])
def test_new_bar_words_speak_six_languages(key):
    _speaks_six(HTML, key)


def test_the_old_labels_are_gone_from_the_dictionary():
    """Dictionary entries for labels removed from the bar would be counted as unused keys by the i18n audit."""
    for key in ("Document Download", "DEEPX Agent"):
        assert f"data-i18n=\"{key}\"" not in HTML
        assert not re.search(r"^\s*'" + re.escape(key) + r"':", HTML, re.M), key


def test_the_legal_line_is_short_and_carries_the_version():
    legal = re.search(r'<p class="stage-legal">(.*?)</p>', _bar(), re.S).group(1)
    assert legal.startswith("© 2026 DEEPX · ")
    assert 'id="studioVersionFooter"' in legal
    assert "NPU Solutions" not in legal


def test_the_offline_notice_is_there_and_starts_hidden():
    tag = re.search(r'<[a-z]+ [^>]*id="homeBarOffline"[^>]*>', _bar()).group(0)
    assert "hidden" in tag and 'data-i18n="Offline"' in tag


def _bar_js() -> str:
    path = STATIC / "home-bar.js"
    assert path.is_file(), "launcher/static/home-bar.js 가 없다"
    return path.read_text(encoding="utf-8")


def test_the_bar_script_is_served_and_loaded():
    launcher = (ROOT / "launcher" / "launcher.py").read_text(encoding="utf-8")
    assert 'path == "/home-bar.js"' in launcher
    assert 'src="/home-bar.js"' in HTML


def test_the_probe_is_one_no_cors_head_on_first_hover_not_at_load():
    """Going out to the network on load breaks the --offline contract. CORS hides the response, but a network
    failure still shows up as a rejection."""
    js = _bar_js()
    assert "mode: 'no-cors'" in js and "method: 'HEAD'" in js
    assert "https://developer.deepx.ai/" in js
    assert "sessionStorage" in js, "한 세션에 한 번만 묻는다"
    init = js[js.index("function init()"):]
    before_listen = init[:init.index("addEventListener")]
    assert "probe()" not in before_listen, "로드 때 probe 를 보낸다"
    assert re.search(r"\['pointerenter',\s*'focusin'\]", init), "첫 hover · focus 에 묻는다"
    assert "navigator.onLine" in js
    assert "'offline'" in js and "'online'" in js


def test_an_offline_link_is_disabled_not_just_dimmed():
    js = _bar_js()
    assert "aria-disabled" in js
    assert "preventDefault" in js


def test_the_bar_is_glass():
    css = (STATIC / "home-stage.css").read_text(encoding="utf-8")
    body = re.search(r"\n\.stage-bar\s*\{([^}]*)\}", css).group(1)
    assert "backdrop-filter" in body


def test_the_tutorial_no_longer_sends_people_to_the_agent_in_the_bar():
    step = TUTORIAL[TUTORIAL.index("target: '#homeBar'"):]   # the bar step spotlights the whole bar
    step = step[:step.index("target:", 10)]
    assert "DEEPX Agent" not in step
    assert "DEEPX Developers" in step


def test_the_top_bar_carries_no_home_nav():
    """One screen leaves anchors nothing to do. Tabs are filled only inside the app."""
    tabs = re.search(r'<div class="top-bar-center" id="navTabs">(.*?)</div>', HTML, re.S).group(1)
    assert "<a" not in tabs and "<button" not in tabs
