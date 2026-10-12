"""DX Monitor release-medium UI contract tests."""

from pathlib import Path
import re
from tests.css_rules import css_rule


ROOT = Path(__file__).resolve().parents[2]
MONITOR = ROOT / "dx_monitor"
CHAT_WIDGET_CSS = ROOT / "shared" / "chat" / "static" / "chat-widget.css"
HW_WIDGET_HTML = ROOT / "shared" / "hw_widget" / "widget.html"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def z_index(rule: str, selector: str) -> int:
    match = re.search(r"z-index\s*:\s*(\d+)\s*;", rule)
    assert match, f"{selector} must declare a numeric z-index"
    return int(match.group(1))


def test_chat_panel_stacks_above_monitor_topbar():
    monitor_css = read_text(MONITOR / "static" / "css" / "style.css")
    chat_css = read_text(CHAT_WIDGET_CSS)

    # The header belongs to the shared shell (dx-shell.css).
    shell_css = read_text(MONITOR.parent / "shared" / "static" / "dx-shell.css")
    topbar_z = z_index(css_rule(shell_css, ".dx-shell-header"), ".dx-shell-header")
    chat_z = z_index(css_rule(chat_css, ".dx-chat-window"), ".dx-chat-window")

    assert chat_z > topbar_z, (
        "Monitor chat panel must stack above the fixed topbar so controls remain clickable"
    )


def test_monitor_topbar_stacks_below_hw_float_widget():
    monitor_css = read_text(MONITOR / "static" / "css" / "style.css")
    hw_widget = read_text(HW_WIDGET_HTML)

    shell_css = read_text(MONITOR.parent / "shared" / "static" / "dx-shell.css")
    topbar_z = z_index(css_rule(shell_css, ".dx-shell-header"), ".dx-shell-header")
    hw_float_z = z_index(css_rule(hw_widget, ".hw-float"), ".hw-float")

    assert topbar_z < hw_float_z, (
        "Monitor topbar must not tie the shared hardware floating widget layer"
    )


def test_mock_banner_is_in_topbar_template():
    """The banner is server-rendered into the .toolbar slot of the shell header."""
    from dx_monitor.server import DX_MONITOR_SHELL
    from shared.shell import apply as apply_shell

    template = read_text(MONITOR / "templates" / "index.html")
    assert 'id="mock-banner"' not in template, "배너는 이제 shell 슬롯이 그린다"

    html = apply_shell(template, DX_MONITOR_SHELL)
    header = html.split('<header class="dx-shell-header">', 1)[1].split("</header>", 1)[0]
    main = html.split('<main class="dx-shell-main monitor-main">', 1)[1]

    assert 'id="mock-banner"' in header
    assert 'id="mock-banner"' not in main


def test_mock_banner_is_topbar_visible_when_displayed():
    css = read_text(MONITOR / "static" / "css" / "style.css")
    rule = css_rule(css, ".mock-banner")

    assert "display:none" in rule.replace(" ", "")
    assert "position: sticky" not in rule and "position: fixed" not in rule
    assert "flex-shrink: 0" in rule
