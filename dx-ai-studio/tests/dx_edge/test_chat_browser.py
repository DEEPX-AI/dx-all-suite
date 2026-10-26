"""DX Cloud has the SDK chat widget, like the other modules — opened at /cloud inside the launcher.

The button opens the chat, the chat takes a question and answers it from DX Cloud's own offline answers (the
launcher sends /api/chat from the /cloud iframe to the dx_edge server), and it closes. It speaks all six languages,
and the floating button covers none of DX Cloud's own controls at the top or the bottom of the page.

The launcher and its module servers run with a PATH that has no coding-agent CLI, so nothing real answers: the
"no AI connected" state, which must still give the module's basic answer.
"""
from __future__ import annotations

import os
import sys

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

NO_AGENT_PATH = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Panel title, and a word of DX Cloud's offline answer to "how do I compile on a stack" in that language.
LANGS = {
    "en": ("DX Cloud Help", "Upload and compile"),
    "ko": ("DX Cloud 도움말", "스택"),
    "ja": ("DX Cloudヘルプ", "スタック"),
    "es": ("Ayuda DX Cloud", "pila"),
    "zh-CN": ("DX Cloud 帮助", "堆栈"),
    "zh-TW": ("DX Cloud 說明", "堆疊"),
}
QUESTION = {
    "en": "How do I compile an ONNX model on my stack?",
    "ko": "스택에서 ONNX 모델을 어떻게 컴파일하나요?",
    "ja": "スタックで ONNX モデルをコンパイルするには?",
    "es": "¿Cómo compilo un modelo ONNX en mi pila?",
    "zh-CN": "如何在堆栈上编译 ONNX 模型?",
    "zh-TW": "如何在堆疊上編譯 ONNX 模型?",
}


def _purge_launcher_modules() -> None:
    for name in list(sys.modules):
        if name == "launcher" or name.startswith("launcher."):
            del sys.modules[name]


@pytest.fixture(scope="module")
def port():
    # The launcher here proxies /cloud to an in-process dx_edge server; both see PATH without an agent CLI.
    saved = {k: os.environ.get(k) for k in ("PATH", "DX_EDGE_PORT")}
    os.environ["PATH"] = NO_AGENT_PATH
    # PATH alone is not enough where an agent CLI sits in /usr/local/bin (copilot on the QA board): Studio then
    # connects Chat to it. Both servers run in this process, so its CLI lookup finds none.
    no_agent = pytest.MonkeyPatch()
    no_agent.setattr("shared.agent_cli.find_cli", lambda binary: None)
    edge, edge_port = start_module_server("dx_edge")
    os.environ["DX_EDGE_PORT"] = str(edge_port)
    _purge_launcher_modules()
    launcher, port = start_module_server("launcher")
    try:
        yield port
    finally:
        launcher.shutdown()
        edge.shutdown()
        no_agent.undo()
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        _purge_launcher_modules()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright
    from tests.browser_support import resolve_chromium_executable

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True, executable_path=resolve_chromium_executable())
    yield br
    br.close()
    pw.stop()


def _cloud(browser, port, lang="en", viewport=(1440, 900)):
    ctx = browser.new_context(viewport={"width": viewport[0], "height": viewport[1]}, reduced_motion="reduce")
    ctx.add_init_script(
        "try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
        "localStorage.setItem('dx-tutorial-launcher-autostarted','1');localStorage.setItem('dx-tutorial-mode','off');"
        f"localStorage.setItem('dx-lang','{lang}');}}catch(e){{}}")
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{port}/cloud", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_function("!!(window.DXLauncher && DXLauncher.currentApp === 'edge')", timeout=30000)
    sel = 'iframe.module-iframe[data-app="edge"]'
    page.wait_for_function(
        "(s) => { const f = document.querySelector(s); return f && f.contentDocument && "
        "f.contentDocument.readyState === 'complete' && f.contentWindow.location.pathname.startsWith('/cloud'); }",
        arg=sel, timeout=60000)
    frame = page.locator(sel).element_handle().content_frame()
    frame.wait_for_selector(".dx-chat-fab", state="visible", timeout=30000)
    return ctx, page, frame


def test_the_chat_opens_takes_a_question_answers_and_closes_on_cloud(port, browser):
    ctx, page, frame = _cloud(browser, port)
    try:
        frame.locator(".dx-chat-fab").click()
        frame.locator(".dx-chat-window.open").wait_for(timeout=10000)
        assert frame.locator(".dx-chat-header-title").inner_text().strip() == "DX Cloud Help"
        frame.wait_for_function(
            "() => (document.querySelector('.dx-chat-source')?.textContent || '').includes('Basic guidance only')",
            timeout=15000)
        frame.locator(".dx-chat-input").fill(QUESTION["en"])
        frame.locator(".dx-chat-send-btn").click()
        frame.locator(".dx-chat-msg.user").last.wait_for(timeout=10000)
        assert QUESTION["en"] in frame.locator(".dx-chat-msg.user").last.inner_text()
        frame.wait_for_function(
            "() => { const m = [...document.querySelectorAll('.dx-chat-msg.ai')].pop();"
            " return m && m.textContent.includes('No AI connected') && m.textContent.includes('Upload and compile'); }",
            timeout=30000)
        frame.locator('.dx-chat-window [data-action="close"]').click()
        frame.wait_for_function("() => !document.querySelector('.dx-chat-window.open')", timeout=10000)
        # Only the module's own button: the launcher's chat hides while a module is open.
        assert not page.locator("body > .dx-chat-fab").first.is_visible()
    finally:
        ctx.close()


@pytest.mark.parametrize("lang", [l for l in LANGS if l != "en"])
def test_the_chat_speaks_every_language(port, browser, lang):
    title, word = LANGS[lang]
    ctx, _, frame = _cloud(browser, port, lang)
    try:
        frame.locator(".dx-chat-fab").click()
        frame.locator(".dx-chat-window.open").wait_for(timeout=10000)
        assert frame.locator(".dx-chat-header-title").inner_text().strip() == title
        assert frame.locator(".dx-chat-fab").get_attribute("aria-label") != "Chat"
        frame.locator(".dx-chat-input").fill(QUESTION[lang])
        frame.locator(".dx-chat-send-btn").click()
        frame.wait_for_function(
            "(w) => { const m = [...document.querySelectorAll('.dx-chat-msg.ai')].pop();"
            " return m && !m.querySelector('.dx-chat-typing') && m.textContent.includes(w); }",
            arg=word, timeout=30000)
    finally:
        ctx.close()


# DX Cloud controls under the button. While the page scrolls, a floating button passes over content in every
# module; what must hold is that nothing stays under it: at the end of the page (the shell leaves room below the last
# control) and for anything DX Cloud pins to the screen (position fixed or sticky).
_COVERED = """(pinnedOnly) => {
  const fab = document.querySelector('.dx-chat-fab').getBoundingClientRect();
  const hit = r => r.width && r.height && r.left < fab.right && r.right > fab.left && r.top < fab.bottom && r.bottom > fab.top;
  const pinned = e => { for (let n = e; n && n !== document.body; n = n.parentElement) {
    const p = getComputedStyle(n).position; if (p === 'fixed' || p === 'sticky') return true; } return false; };
  return [...document.querySelectorAll('.dx-shell-main button, .dx-shell-main a, .dx-shell-main input, '
      + '.dx-shell-main select, .dx-shell-main summary, .dx-shell-main label, .dx-shell-main .edge-chip, '
      + '.dx-shell-main .edge-badge-art, .dx-shell-main code, .dx-shell-main td, .toast-wrap')]
    .filter(e => e.offsetParent && hit(e.getBoundingClientRect()) && (!pinnedOnly || pinned(e)))
    .map(e => e.id || e.className || e.tagName);
}"""

_TO_END = ("() => { const m = document.querySelector('.dx-shell-main'); m.style.scrollBehavior = 'auto';"
           " m.scrollTop = m.scrollHeight; }")


@pytest.mark.parametrize("viewport", [(1440, 900), (390, 844)])
def test_the_chat_button_leaves_dx_clouds_controls_reachable(port, browser, viewport):
    ctx, _, frame = _cloud(browser, port, viewport=viewport)
    try:
        frame.wait_for_timeout(500)
        assert frame.evaluate(_COVERED, True) == []
        frame.evaluate(_TO_END)
        frame.wait_for_timeout(300)
        assert frame.evaluate(_COVERED, False) == []
        # The AWS Console guide page has the chat too, with the same room at its end.
        frame.evaluate("() => { location.href = 'guide'; }")
        frame.wait_for_function("() => location.pathname.endsWith('/guide') && !!document.querySelector('.dx-chat-fab')"
                                " && !!document.querySelector('#guideBody h2, #guideBody h3')", timeout=30000)
        frame.evaluate(_TO_END)
        frame.wait_for_timeout(300)
        assert frame.evaluate(_COVERED, False) == []
    finally:
        ctx.close()
