"""Static i18n and tutorial contracts for DX Monitor."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MONITOR = ROOT / "dx_monitor"
SHARED_CHARTS = ROOT / "shared" / "static" / "dx-charts.js"
TARGET_LANGS = ("ko", "ja", "zh-CN", "zh-TW", "es")

REQUIRED_DYNAMIC_KEYS = {
    "Mock",
    "Memory",
    "Util",
    "Voltage",
    "Clock",
    "DRAM",
    "NPU Temp (C)",
    "Voltage (mV)",
    "Clock (MHz)",
    "NPU DRAM (%)",
    "NPU Util (%)",
    "Core Temp (C)",
    "CPU Load",
    "Memory (%)",
    "CPU Cores (%)",
    "Waiting for data...",
    "No data available",
    "System",
    "NPU {id}",
    "Avg Temp",
    "Cores",
    "Firmware",
    "Chip",
    "Board",
    "DDR Type",
    "DDR Errors",
    "DDR Channel Temp",
    "Available",
    "Unavailable",
    "N/A",
    "No events recorded",
    "{count} events",
}

SOURCE_FILES = [
    MONITOR / "static" / "js" / "dashboard.js",
    MONITOR / "static" / "js" / "charts.js",
    MONITOR / "static" / "js" / "utils.js",
    MONITOR / "static" / "js" / "tutorial.js",
]

VALID_DYNAMIC_TUTORIAL_TARGETS = {
    "#langToggle",
    "#dxToolbar",
    ".dx-chat-fab",
    ".dx-chat-input-area",
    ".dx-chat-window",
}

STALE_TUTORIAL_TARGETS = {
    "#rt-mode-btns",
    "#rt-view-btns",
    "#rt-hist-range-wrap",
    "#rt-chart-box",
    "#cpu-gauge",
    "#mem-gauge",
    "#nputemp-gauge",
    "#disk-gauge",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def monitor_i18n_source() -> str:
    return read_text(MONITOR / "static" / "js" / "i18n.js")


def dict_section() -> str:
    return monitor_i18n_source()


def dict_keys() -> set[str]:
    return set(re.findall(r"'((?:\\.|[^'\\])+)':\s*\{", dict_section()))


def dict_entry(key: str) -> str:
    match = re.search(rf"'{re.escape(key)}':\s*\{{(.*?)\n\s*\}}\s*(?:,|\n)", dict_section(), re.S)
    return match.group(1) if match else ""


def t_keys(path: Path) -> set[str]:
    source = read_text(path)
    single = re.findall(r"\bT\('((?:\\.|[^'\\])+)'", source)
    double = re.findall(r'\bT\("((?:\\.|[^"\\])+)"', source)
    return set(single + double)


def monitor_t_keys() -> set[str]:
    keys = set()
    for path in SOURCE_FILES:
        keys.update(t_keys(path))
    return keys


def test_monitor_required_dynamic_keys_exist_in_dictionary():
    keys = dict_keys()
    missing = sorted(REQUIRED_DYNAMIC_KEYS - keys)
    assert not missing, missing


def test_monitor_dictionary_entries_cover_target_languages():
    incomplete = {}
    for key in REQUIRED_DYNAMIC_KEYS | monitor_t_keys():
        entry = dict_entry(key)
        missing_langs = [
            lang
            for lang in TARGET_LANGS
            if f"{lang}:" not in entry and f"'{lang}':" not in entry and f'"{lang}":' not in entry
        ]
        if missing_langs:
            incomplete[key] = missing_langs
    assert not incomplete, incomplete


def test_monitor_t_keys_are_in_dictionary():
    keys = dict_keys()
    missing = {}
    for path in SOURCE_FILES:
        unresolved = sorted(k for k in t_keys(path) if k not in keys)
        if unresolved:
            missing[str(path.relative_to(MONITOR))] = unresolved
    assert not missing, missing


def test_monitor_dashboard_registers_language_refresh_without_refetch_hook():
    source = read_text(MONITOR / "static" / "js" / "dashboard.js")
    template = read_text(MONITOR / "templates" / "index.html")
    assert "function refreshLanguage()" in source
    assert source.count("DXI18n.onLangChange(refreshLanguage)") == 1
    refresh_body = _extract_braced_body(source, "function refreshLanguage()")
    assert "refreshDash()" not in refresh_body
    assert "DXI18n.onLangChange(function(){refreshDash();})" not in template


def test_monitor_browser_state_caches_latest_payloads_for_repaint():
    utils = read_text(MONITOR / "static" / "js" / "utils.js")
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    for token in ("lastHW", "lastSystemInfo", "lastEvents", "lastEventCount"):
        assert token in utils
    assert re.search(r"S\.lastHW\s*=\s*hw;", dashboard)
    assert re.search(r"S\.lastSystemInfo\s*=\s*si;", dashboard)
    assert "S.lastEvents" in dashboard
    assert re.search(r"S\.lastEventCount\s*=", dashboard)


def test_monitor_charts_receive_translated_empty_state_text():
    charts = read_text(SHARED_CHARTS)
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    assert "ctx.fillText('Waiting for data" not in charts
    assert "ctx.fillText('No data available" not in charts
    assert "opts.emptyText" in charts
    assert "emptyText:T('Waiting for data...')" in dashboard


def _template_selectors() -> set[str]:
    html = read_text(MONITOR / "templates" / "index.html")
    ids = {"#" + value for value in re.findall(r'id="([^"]+)"', html)}
    classes = {"." + value for cls in re.findall(r'class="([^"]+)"', html) for value in cls.split()}
    return ids | classes | VALID_DYNAMIC_TUTORIAL_TARGETS


def _tutorial_targets() -> set[str]:
    source = read_text(MONITOR / "static" / "js" / "tutorial.js")
    single = re.findall(r"target:\s*'([^']+)'", source)
    double = re.findall(r'target:\s*"([^"]+)"', source)
    return {target for target in single + double if target and target != "null"}


def test_monitor_tutorial_targets_current_dom_only():
    selectors = _template_selectors()
    targets = _tutorial_targets()
    stale = sorted(targets & STALE_TUTORIAL_TARGETS)
    missing = sorted(target for target in targets if target not in selectors)
    assert not stale, stale
    assert not missing, missing


def _extract_braced_body(source: str, anchor: str) -> str:
    """Find *anchor* in *source*, locate the next ``{``, then walk characters
    counting braces until the matching ``}`` is found.  Returns the body
    between (exclusive of) the outermost braces.

    Raises ``AssertionError`` with a clear message when the anchor or its
    opening/closing brace cannot be located.
    """
    start = source.find(anchor)
    assert start != -1, f"anchor {anchor!r} not found in source"
    open_pos = source.find("{", start)
    assert open_pos != -1, f"no opening brace after {anchor!r}"
    depth = 0
    for i in range(open_pos, len(source)):
        ch = source[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[open_pos + 1 : i]
    raise AssertionError(f"unmatched braces after {anchor!r}")


def test_monitor_tutorial_prefers_dxi18n_lang():
    source = read_text(MONITOR / "static" / "js" / "tutorial.js")
    # Anchor to a definition context—never a bare call or reference.
    m = re.search(
        r"function\s+getLang\s*\("
        r"|getLang\s*:\s*function\s*\("
        r"|getLang\s*\([^)]*\)\s*\{",
        source,
    )
    assert m is not None, "no getLang definition found in tutorial.js"
    get_lang_body = _extract_braced_body(source, m.group())
    assert "DXI18n.lang" in get_lang_body
    assert "localStorage.getItem('dx-lang')" in get_lang_body
