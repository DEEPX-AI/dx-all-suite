"""Target-workdir selector in the Agent Dev console UI."""
from pathlib import Path

AD = Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"


def test_template_has_target_select():
    html = (AD / "templates" / "index.html").read_text(encoding="utf-8")
    assert 'id="target-select"' in html
    for v in ("suite", "dx-runtime", "dx_app", "dx_stream", "dx-compiler"):
        assert 'value="%s"' % v in html


def test_console_js_sends_target():
    js = (AD / "static" / "js" / "console.js").read_text(encoding="utf-8")
    assert "selectedTarget" in js
    assert "target:" in js  # included in the /api/agent/run POST body
