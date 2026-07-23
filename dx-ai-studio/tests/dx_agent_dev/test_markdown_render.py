"""markdown_render.js unit tests (Node.js)."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = ROOT / "dx_agent_dev" / "static" / "js" / "markdown_render.js"

NODE_TEST = r"""
const fs = require('fs');
const vm = require('vm');
const src = fs.readFileSync(process.argv[1], 'utf8');
const sandbox = { window: {}, console };
vm.runInNewContext(src, sandbox);
const R = sandbox.window.DXMarkdownRender;
const assert = (cond, msg) => { if (!cond) throw new Error(msg || 'assert failed'); };

// repairCodeFences
assert(R.repairCodeFences('a ``` b').endsWith('\n```'));

// bare mermaid (single newline after heading)
const m2 = R.normalizeBareMermaid('## arch\nmermaid\nflowchart LR\nA-->B\n\n## next');
assert(m2.includes('```mermaid'));

// pipe table after unclosed fence (screenshot regression)
const raw = [
  '```',
  '43:49:dx-runtime/foo.sh',
  'gst-launch-1.0 ...',
  '- **Person detection**: YOLO',
  '',
  '| 장점 | 단점 |',
  '|------|------|',
  '| NPU | manual |',
].join('\n');
const fixed = R.repairCodeFences(raw);
const html = R.render(fixed);
assert(html.includes('md-table'), 'table should render');
assert(html.includes('code-citation') || html.includes('code-block'), 'code block');
assert(!html.includes('| 장점 |'), 'raw pipe row should not remain');

// horizontal rule
assert(R.render('a\n---\nb').includes('md-hr'));

// spec mode
assert(R.isSpecContent('## a\n## b\nlong '.repeat(200)));

console.log(JSON.stringify({ ok: true, tests: 5 }));
"""


def test_markdown_render_node():
    proc = subprocess.run(
        ["node", "-e", NODE_TEST, str(JS)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    data = json.loads(proc.stdout.strip().splitlines()[-1])
    assert data.get("ok") is True


def test_index_loads_markdown_render():
    html = (ROOT / "dx_agent_dev" / "templates" / "index.html").read_text(encoding="utf-8")
    assert "markdown_render.js" in html
    assert html.index("markdown_render.js") < html.index("console.js")
