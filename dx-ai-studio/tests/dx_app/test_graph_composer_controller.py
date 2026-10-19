"""dx_app/static/js/graph-composer.js — the controller's decisions, run in Node with a stub canvas and DOM.

The page is checked end to end in the browser suite; these pin what the server now reports: a memory suggestion's
`patch` (engine and params per node, null removes a key) is applied as given, and model files dx_app cannot use
(`unusable` from --check) keep Run once off and are named in the status line.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tests.browser_support import resolve_node_executable

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [ROOT / "shared/static/dx-graph-core.js", ROOT / "dx_app/static/js/graph-doc.js",
           ROOT / "dx_app/static/js/graph-composer.js"]

_PRELUDE = r"""
const fs = require('fs'), vm = require('vm');
const els = {};
const el = id => els[id] = els[id] || {id: id, dataset: {}, textContent: '', disabled: false, hidden: false, value: ''};
const sandbox = {window: {}, T: k => k, document: {getElementById: el, querySelector: () => null}, setTimeout: () => 0,
                 clearTimeout: () => {}, console: console};
sandbox.window.T = sandbox.T;
const files = JSON.parse(process.argv[1]);
for (const f of files) vm.runInNewContext(fs.readFileSync(f, 'utf8'), sandbox);
const G = sandbox.window.GraphComposer;
const eq = (a, b, m) => { const x = JSON.stringify(a), y = JSON.stringify(b); if (x !== y) throw new Error((m || 'eq') + ': ' + x + ' != ' + y); };
const ok = (c, m) => { if (!c) throw new Error(m || 'assert'); };
function stubCanvas(nodes) {
  const calls = [];
  return {calls: calls, getGraph: () => ({nodes: nodes, edges: []}),
          updateNode: (id, patch, opts) => { calls.push([id, opts && opts.commit]);
                                             nodes.forEach(n => { if (n.id === id) Object.assign(n, JSON.parse(JSON.stringify(patch))); }); }};
}
"""


def _run(body: str) -> None:
    node = resolve_node_executable()
    if not node:
        pytest.skip("node is required for the graph-composer.js tests")
    proc = subprocess.run([node, "-e", _PRELUDE + body + "\nconsole.log('{\"ok\": true}');",
                           json.dumps([str(p) for p in SOURCES])], capture_output=True, text=True, cwd=str(ROOT),
                          check=False)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert json.loads(proc.stdout.strip().splitlines()[-1]) == {"ok": True}


def test_a_share_suggestion_applies_its_patch_to_every_node():
    _run(r"""
const nodes = [{id: 'od', data: {model: 'yolov8-n_640x640', params: {score_threshold: 0.2}, engine: {buffers: 4}}},
               {id: 'od2', data: {model: 'yolov8-n_640x640', params: {score_threshold: 0.5}, track: {algo: 'iou'}}},
               {id: 'od3', data: {model: 'yolov8-n_640x640', params: {score_threshold: 0.6}}}];
const cv = stubCanvas(nodes);
G.state().cv = cv;
G.applySuggestion({kind: 'share', model: 'yolov8-n_640x640', nodes: ['od', 'od2', 'od3'], saves_bytes: 1,
  patch: {od: {engine: {share: true, buffers: 4}, params: {score_threshold: 0.2}},
          od2: {engine: {share: true, buffers: 4}, params: {score_threshold: 0.2}},
          od3: {engine: {share: true, buffers: 4}, params: null}}});
eq(nodes[0].data, {model: 'yolov8-n_640x640', params: {score_threshold: 0.2}, engine: {share: true, buffers: 4}});
eq(nodes[1].data, {model: 'yolov8-n_640x640', params: {score_threshold: 0.2}, track: {algo: 'iou'}, engine: {share: true, buffers: 4}});
eq(nodes[2].data, {model: 'yolov8-n_640x640', engine: {share: true, buffers: 4}}, 'null removes params');
eq(cv.calls, [['od', false], ['od2', false], ['od3', true]], 'one undo step');
""")


def test_a_buffers_suggestion_sets_the_buffer_count_only():
    _run(r"""
const nodes = [{id: 'depth', data: {model: 'fastdepth_224x224', params: {a: 1}, engine: {share: true}}}];
const cv = stubCanvas(nodes);
G.state().cv = cv;
G.applySuggestion({kind: 'buffers', model: 'fastdepth_224x224', nodes: ['depth'], buffers: 2, saves_bytes: 1});
eq(nodes[0].data, {model: 'fastdepth_224x224', params: {a: 1}, engine: {share: true, buffers: 2}});
eq(cv.calls, [['depth', true]]);
""")


def test_unusable_model_files_keep_run_once_off_and_are_named():
    _run(r"""
const st = G.state();
st.cv = stubCanvas([{id: 'cam', data: {type: 'source'}}, {id: 'od', data: {model: 'm'}}]);
st.catalog = {available: true, models: []};
st.check = {ok: true, errors: [], missing: [], unusable: {od: 'invalid'}};
ok(!G.canRun(), 'a broken model file cannot run');
G.ctx().updateStatus();
eq([els['gc-status'].dataset.kind, els['gc-status'].textContent], ['error', '{n} model files cannot be used'.replace('{n}', 1)]);
ok(els['gc-run'].disabled, 'the Run once button is off');
st.check = {ok: true, errors: [], missing: [], unusable: {}};
ok(G.canRun(), 'a clean check can run');
st.check = {ok: true, errors: [], missing: ['od'], unusable: {}};
ok(!G.canRun(), 'a missing model cannot run');
""")


def test_the_canvas_gets_the_page_translator():
    src = (ROOT / "dx_app/static/js/graph-composer.js").read_text(encoding="utf-8")
    create = src[src.index("DXGraphCanvas.create("):]
    assert "t: tr," in create[:create.index("});")]
