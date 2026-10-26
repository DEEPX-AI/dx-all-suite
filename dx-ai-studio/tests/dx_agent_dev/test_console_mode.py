"""Mode (Interaction) selector in the Agent Dev console UI."""
import pathlib
from tests.i18n_markup import assert_translatable

ROOT = pathlib.Path(__file__).resolve().parents[2] / "dx_agent_dev"


def test_mode_selector_in_template():
    h = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert 'id="mode-select"' in h
    assert 'value="autopilot"' in h and 'value="interactive"' in h
    picker = h[h.index('id="mode-select"'):h.index("</select>", h.index('id="mode-select"'))]
    assert_translatable(picker, "dx_agent_dev/static/js/i18n.js", "mode-select")


def test_console_sends_mode():
    js = (ROOT / "static" / "js" / "console.js").read_text(encoding="utf-8")
    assert "selectedMode" in js
    assert "mode:" in js
