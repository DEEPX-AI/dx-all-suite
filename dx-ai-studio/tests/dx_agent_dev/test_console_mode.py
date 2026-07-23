"""Mode (Interaction) selector in the Agent Dev console UI."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2] / "dx_agent_dev"


def test_mode_selector_in_template():
    h = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
    assert 'id="mode-select"' in h
    assert 'value="autopilot"' in h and 'value="interactive"' in h
    # 6-lang label present (at least ko/ja/zh-CN/zh-TW/es markers near the picker)
    for lang in ('class="ko"', 'class="ja"', 'class="zh-CN"', 'class="zh-TW"', 'class="es"'):
        assert lang in h


def test_console_sends_mode():
    js = (ROOT / "static" / "js" / "console.js").read_text(encoding="utf-8")
    assert "selectedMode" in js
    assert "mode:" in js
