"""DX Chat per-module header titles must cover all six locales."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHAT_WIDGET = ROOT / "shared" / "chat" / "static" / "chat-widget.js"
LANGS = ("en", "ja", "ko", "es", "zh-CN", "zh-TW")

REQUIRED_APPS = (
    "launcher",
    "dx_app",
    "dx_stream",
    "dx_compiler",
    "dx_planner",
    "dx_benchmark",
    "dx_monitor",
    "dx_modelzoo",
    "dx_agent_dev",
    "sdk_library",
)


def _header_titles_block() -> str:
    text = CHAT_WIDGET.read_text(encoding="utf-8")
    match = re.search(
        r"window\._DX_CHAT_HEADER_TITLES\s*=\s*window\._DX_CHAT_HEADER_TITLES\s*\|\|\s*\{",
        text,
    )
    assert match, "_DX_CHAT_HEADER_TITLES map missing from chat-widget.js"
    start = match.end() - 1
    depth = 0
    for idx in range(start, len(text)):
        ch = text[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    raise AssertionError("Unclosed _DX_CHAT_HEADER_TITLES object")


def _app_block(app_name: str, block: str) -> str:
    pattern = rf"{re.escape(app_name)}:\s*\{{"
    match = re.search(pattern, block)
    assert match, f"Missing header title entry for {app_name!r}"
    start = match.end() - 1
    depth = 0
    for idx in range(start, len(block)):
        ch = block[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return block[start : idx + 1]
    raise AssertionError(f"Unclosed header title block for {app_name!r}")


def test_chat_header_titles_cover_all_modules_and_languages():
    block = _header_titles_block()
    missing = []
    for app in REQUIRED_APPS:
        app_block = _app_block(app, block)
        for lang in LANGS:
            key = re.escape(lang)
            if not re.search(rf"(?:{key}|'{key}'|\"{key}\")\s*:\s*['\"]", app_block):
                missing.append(f"{app}.{lang}")
    assert not missing, f"Missing chat header locales: {missing[:20]}"
