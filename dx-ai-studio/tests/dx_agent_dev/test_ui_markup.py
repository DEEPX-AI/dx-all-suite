"""콘솔 드롭다운 마크업 계약."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "dx_agent_dev" / "templates" / "index.html"


def test_agent_controls_present():
    html = INDEX.read_text(encoding="utf-8")
    assert 'id="agent-controls"' in html
    assert 'id="agent-select"' in html
    assert 'id="model-select"' in html


def test_agent_controls_before_form():
    html = INDEX.read_text(encoding="utf-8")
    assert html.index('id="agent-controls"') < html.index('id="console-form"')


def test_console_chat_markup_and_six_lang_hints():
    html = INDEX.read_text(encoding="utf-8")
    for el in ('id="console-status-bar"', 'class="console-role-hint"', 'class="console-session-hint"'):
        assert el in html
    langs = ('class="en"', 'class="ko"', 'class="ja"', 'class="es"', 'class="zh-CN"', 'class="zh-TW"')
    role = html.split('console-role-hint', 1)[1].split('</p>', 1)[0]
    for lang in langs:
        assert lang in role, f"missing {lang} in console-role-hint"
