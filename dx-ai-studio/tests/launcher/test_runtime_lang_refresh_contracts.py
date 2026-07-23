"""Launcher runtime language refresh contracts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRAME = ROOT / "launcher/static/launcher-app-frame.js"


def test_refresh_launcher_chrome_updates_nav_and_ports():
    src = FRAME.read_text(encoding="utf-8")
    body_start = src.index("function refreshLauncherChrome")
    body = src[body_start:body_start + 600]
    assert "_refreshNavTabLabels()" in body
    assert "refreshModuleEntryChrome()" in body
    assert "updateModulePortLabels" in body


def test_platform_info_registers_lang_refresh():
    src = (ROOT / "launcher/static/platform-info.js").read_text(encoding="utf-8")
    assert "refreshPlatformInfoLanguage" in src
    assert "DXI18n.onLangChange" in src


def test_sdk_library_registers_language_hook():
    src = (ROOT / "launcher/static/sdk-library.js").read_text(encoding="utf-8")
    assert "registerLanguageHook" in src
    assert "DXI18n.onLangChange" in src
    assert "_refreshViewerChrome" in src
