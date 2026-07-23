"""Chat-render robustness: wide content (code/tables/long tokens) must stay contained in
the center column instead of blowing out the 3-column grid; markdown stays complete."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

AD = Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"
CSS = (AD / "static" / "css" / "console.css").read_text(encoding="utf-8")


def _rule(selector):
    m = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", CSS)
    return m.group(1) if m else None


def test_assistant_body_is_contained():
    body = _rule(".assistant-body")
    assert body is not None
    assert "min-width: 0" in body
    assert "max-width: 100%" in body
    assert "overflow-wrap" in body  # long unbroken tokens wrap instead of stretching the cell


def test_pre_blocks_capped_and_scroll():
    pre = _rule(".assistant-body pre")
    assert pre is not None
    assert "max-width: 100%" in pre
    assert "overflow-x: auto" in pre


def test_table_wrap_scrolls():
    wrap = _rule(".assistant-body .md-table-wrap")
    assert wrap is not None and "overflow-x: auto" in wrap


@pytest.mark.skipif(not shutil.which("node"), reason="node not available")
def test_markdown_render_completeness():
    """Lock the verified-good renderer: unclosed fences repaired, tables wrapped, no raw fence."""
    js = AD / "static" / "js" / "markdown_render.js"
    script = (
        "const fs=require('fs'),vm=require('vm');"
        "const g={};const ctx=vm.createContext({window:g,globalThis:g,console});"
        "vm.runInContext(fs.readFileSync(%r,'utf8'),ctx);const R=g.DXMarkdownRender;"
        "const a=R.render(R.repairCodeFences('x:\\n```python\\nprint(1)\\n'),{});"
        "const b=R.render('| A | B |\\n|---|---|\\n| 1 | 2 |',{});"
        "if(!a.includes('<pre')||!a.includes('<code')||a.includes('```'))throw new Error('fence');"
        "if(!b.includes('md-table-wrap')||!b.includes('<table'))throw new Error('table');"
        "console.log('OK');"
    ) % str(js)
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "OK" in out.stdout
