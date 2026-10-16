"""SDKREQ-485 [Common] shared toolbar and chat — in every module, inside a real ./launcher.sh studio.

The module list is the launcher's registry, so a new module is checked automatically. The studio here
runs with a PATH that has no coding-agent CLI, which is the "no AI connected" state the chat must
handle; a real LLM answer is a separate AC that runs only when Studio chat settings name an endpoint.
"""
from __future__ import annotations

import json
import os
import shutil

from tests.acceptance.conftest import module_frame, wait_home
from tests.acceptance.hardware import need, real_chat_config_path

LAUNCHER_ENV = {"PATH": "/usr/local/share/gstdxstream/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"}
SETTINGS_MODULES = {"app", "stream"}
# DX Cloud ships the shared toolbar but no chat widget (dx_edge/templates/index.html has no DXChat.init).
NO_CHAT_MODULES = {"edge"}


def _modules(page) -> list[str]:
    return page.evaluate("() => Object.keys(DXLauncher.APP_PATHS)")


def _each_module(pages, lang="en"):
    page = pages.new("/", lang=lang)
    wait_home(page)
    for key in _modules(page):
        page.evaluate("(k) => DXLauncher.launch(k)", key)
        frame = module_frame(page, key, ready="#dxToolbar")
        yield page, key, frame
        page.evaluate("() => DXLauncher.goHome()")
        page.wait_for_function("() => DXLauncher.currentApp === null")


def test_every_module_toolbar_has_language_theme_and_tutorial_and_settings_only_in_app_and_stream(pages):
    seen = []
    for _, key, frame in _each_module(pages):
        seen.append(key)
        tb = frame.locator("#dxToolbar")
        assert tb.locator("#langToggle .dx-lang-btn").count() == 1, key
        assert tb.locator("#dxToolbarTheme").count() == 1, key
        tut = tb.locator("#dxToolbarTutorial")
        tut.wait_for(state="attached", timeout=15000)
        frame.wait_for_function("() => !document.querySelector('#dxToolbarTutorial').disabled", timeout=15000)
        has_settings = tb.locator("#dxToolbarSettings").count() == 1
        assert has_settings == (key in SETTINGS_MODULES), (key, has_settings)
    assert len(seen) >= 9, seen


def test_every_module_language_menu_lists_six_languages_and_its_tutorial_opens_the_guide(pages):
    for _, key, frame in _each_module(pages):
        frame.locator("#dxToolbar .dx-lang-btn").click()
        items = frame.locator(".dx-lang-menu .dx-lang-item")
        items.first.wait_for(state="visible", timeout=10000)
        langs = items.evaluate_all("els => els.map(e => e.dataset.lang)")
        assert langs == ["en", "ja", "ko", "es", "zh-CN", "zh-TW"], (key, langs)
        frame.locator("#dxToolbar .dx-lang-btn").press("Escape")
        frame.locator("#dxToolbarTutorial").click()
        frame.locator(".dxt-toc.open").wait_for(timeout=15000)
        frame.locator(".dxt-toc-backdrop.open").click(position={"x": 5, "y": 5})
        frame.wait_for_function("() => !document.querySelector('.dxt-toc.open')", timeout=10000)


def test_every_module_chat_opens_shows_settings_and_closes(pages):
    for _, key, frame in _each_module(pages):
        fab = frame.locator(".dx-chat-fab")
        if key in NO_CHAT_MODULES:
            assert fab.count() == 0, key
            continue
        fab.wait_for(state="visible", timeout=15000)
        fab.click()
        frame.locator(".dx-chat-window.open").wait_for(timeout=10000)
        frame.locator('.dx-chat-window [data-action="settings"]').click()
        frame.locator(".dx-chat-settings-panel.open").wait_for(timeout=10000)
        frame.locator('.dx-chat-window [data-action="settings-close"]').click()
        frame.wait_for_function("() => !document.querySelector('.dx-chat-settings-panel.open')")
        frame.locator('.dx-chat-window [data-action="close"]').click()
        frame.wait_for_function("() => !document.querySelector('.dx-chat-window.open')")


def test_every_module_chat_sends_and_answers_without_an_ai_connected(pages):
    for _, key, frame in _each_module(pages):
        if key in NO_CHAT_MODULES:
            continue
        frame.locator(".dx-chat-fab").click()
        win = frame.locator(".dx-chat-window.open")
        win.wait_for(timeout=10000)
        frame.wait_for_function(
            "() => (document.querySelector('.dx-chat-source')?.textContent || '').includes('Basic guidance only')",
            timeout=15000)
        frame.locator(".dx-chat-input").fill("How do I compile an ONNX model?")
        frame.locator(".dx-chat-send-btn").click()
        frame.locator(".dx-chat-msg.user").last.wait_for(timeout=10000)
        frame.wait_for_function(
            "() => [...document.querySelectorAll('.dx-chat-msg.ai')].some(m => m.textContent.includes('No AI connected'))",
            timeout=30000)
        frame.locator('.dx-chat-window [data-action="close"]').click()


def test_with_an_llm_configured_the_chat_answers_from_it(pages):
    need("llm")
    cfg_dir = os.environ["DX_CHAT_CONFIG_DIR"]        # the studio under test reads this dir
    shutil.copyfile(real_chat_config_path(), os.path.join(cfg_dir, "chat_config.json"))
    try:
        page = pages.new("/")
        wait_home(page)
        page.evaluate("() => DXLauncher.launch('app')")
        frame = module_frame(page, "app", ready=".dx-chat-fab")
        frame.locator(".dx-chat-fab").click()
        frame.locator(".dx-chat-input").fill("In one sentence, what is DX-M1?")
        frame.locator(".dx-chat-send-btn").click()
        frame.wait_for_function(
            "() => { const m = [...document.querySelectorAll('.dx-chat-msg.ai')].pop();"
            " return m && m.textContent.trim().length > 10 && !m.textContent.includes('No AI connected'); }",
            timeout=180000)
    finally:
        os.remove(os.path.join(cfg_dir, "chat_config.json"))
    assert json.loads(open(real_chat_config_path(), encoding="utf-8").read())
