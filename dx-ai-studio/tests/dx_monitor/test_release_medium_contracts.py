"""DX Monitor release-medium UI contract tests."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
MONITOR = ROOT / "dx_monitor"
CHAT_WIDGET_CSS = ROOT / "shared" / "chat" / "static" / "chat-widget.css"
HW_WIDGET_HTML = ROOT / "shared" / "hw_widget" / "widget.html"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def css_rule(css: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{([^}}]+)\}}", css)
    assert match, f"{selector} rule not found"
    return match.group(1)


def z_index(rule: str, selector: str) -> int:
    match = re.search(r"z-index\s*:\s*(\d+)\s*;", rule)
    assert match, f"{selector} must declare a numeric z-index"
    return int(match.group(1))


def test_chat_panel_stacks_above_monitor_topbar():
    monitor_css = read_text(MONITOR / "static" / "css" / "style.css")
    chat_css = read_text(CHAT_WIDGET_CSS)

    topbar_z = z_index(css_rule(monitor_css, ".top-bar"), ".top-bar")
    chat_z = z_index(css_rule(chat_css, ".dx-chat-window"), ".dx-chat-window")

    assert chat_z > topbar_z, (
        "Monitor chat panel must stack above the fixed topbar so controls remain clickable"
    )


def test_monitor_topbar_stacks_below_hw_float_widget():
    monitor_css = read_text(MONITOR / "static" / "css" / "style.css")
    hw_widget = read_text(HW_WIDGET_HTML)

    topbar_z = z_index(css_rule(monitor_css, ".top-bar"), ".top-bar")
    hw_float_z = z_index(css_rule(hw_widget, ".hw-float"), ".hw-float")

    assert topbar_z < hw_float_z, (
        "Monitor topbar must not tie the shared hardware floating widget layer"
    )


def test_mock_banner_is_in_topbar_template():
    template = read_text(MONITOR / "templates" / "index.html")
    header = template.split('<header class="top-bar">', 1)[1].split("</header>", 1)[0]
    main = template.split('<main class="monitor-main">', 1)[1].split("</main>", 1)[0]

    assert 'id="mock-banner"' in header
    assert 'id="mock-banner"' not in main


def test_mock_banner_is_topbar_visible_when_displayed():
    css = read_text(MONITOR / "static" / "css" / "style.css")
    rule = css_rule(css, ".mock-banner")

    assert "display:none" in rule.replace(" ", "")
    assert "position: sticky" not in rule and "position: fixed" not in rule
    assert "flex-shrink: 0" in rule
