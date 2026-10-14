"""dx_app/static/js/graph-doc.js — the Graph Composer's document model, run in Node.

The conversions are what keeps a graph the user draws identical to the dx_app graph JSON that runs, so they are
tested on the shipped samples' shapes: round trips, edge kinds, connection rules, projects and canvas pins.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tests.browser_support import resolve_node_executable

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "dx_app" / "static" / "js" / "graph-doc.js"

# Two shipped samples (dx_app src/cpp_example/multi_model_graph): a ROI cascade with tracking, and a CPU op fed by
# three result edges.
CASCADE = {"version": 1, "name": "person-attributes", "nodes": [
    {"id": "cam", "type": "source", "uri": "sample/img/sample_people.jpg"},
    {"id": "od", "model": "yolov8-n_640x640", "params": {"score_threshold": 0.35},
     "track": {"algo": "iou", "iou": 0.3, "max_age": 30}},
    {"id": "attr", "model": "deepmar_resnet50_224x224"}],
    "edges": [{"from": "cam", "to": "od"}, {"from": "od", "to": "attr", "roi": {"classes": ["person"], "pad": 0.05}}]}
VOLUME = {"version": 1, "name": "logistics_volume", "nodes": [
    {"id": "cam", "type": "source", "uri": "sample/img/sample_baggage_cart_airport.jpg"},
    {"id": "det", "model": "yolo26-n_640x640"}, {"id": "seg", "model": "yolo26-n-seg_640x640"},
    {"id": "depth", "model": "yolo26-depth-n_768x768"},
    {"id": "volume", "type": "cpu", "op": "volume", "params": {"scale_factor": 1.0}}],
    "edges": [{"from": "cam", "to": "det"}, {"from": "cam", "to": "seg"}, {"from": "cam", "to": "depth"},
              {"from": "det", "to": "volume", "carry": "result"}, {"from": "seg", "to": "volume", "carry": "result"},
              {"from": "depth", "to": "volume", "carry": "result"}]}
MODELS = {
    "yolov8-n_640x640": {"task": "object_detection", "produces": "boxes", "consumes": "full_frame"},
    "deepmar_resnet50_224x224": {"task": "person_attribute", "produces": "scores", "consumes": "either"},
    "fastdepth_224x224": {"task": "depth_estimation", "produces": "densemap", "consumes": "full_frame"},
    "realesrgan-x2_192x192": {"task": "super_resolution", "produces": "image", "consumes": "either"},
}

_PRELUDE = r"""
const fs = require('fs');
const vm = require('vm');
const sandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), sandbox);
const D = sandbox.window.GraphDoc;
const DATA = JSON.parse(process.argv[2]);
const eq = (a, b, m) => { const x = JSON.stringify(a), y = JSON.stringify(b); if (x !== y) throw new Error((m || 'eq') + ': ' + x + ' != ' + y); };
const ok = (c, m) => { if (!c) throw new Error(m || 'assert'); };
"""


def _run(body: str) -> None:
    node = resolve_node_executable()
    if not node:
        pytest.skip("node is required for the graph-doc.js tests")
    data = json.dumps({"cascade": CASCADE, "volume": VOLUME, "models": MODELS})
    proc = subprocess.run([node, "-e", _PRELUDE + body + "\nconsole.log('{\"ok\": true}');", str(DOC), data],
                          capture_output=True, text=True, cwd=str(ROOT), check=False)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert json.loads(proc.stdout.strip().splitlines()[-1]) == {"ok": True}


def test_the_shipped_samples_round_trip_unchanged():
    _run(r"""
for (const k of ['cascade', 'volume']) {
  const g = D.fromEngine(DATA[k]);
  eq(D.toEngine(g, DATA[k].name), DATA[k], k);
}
const g = D.fromEngine(DATA.cascade);
eq(g.edges.map(e => [e.id, e.kind]), [['cam->od', 'frame'], ['od->attr', 'roi']]);
eq(D.fromEngine(DATA.volume).edges[3].kind, 'result');
eq(g.nodes.map(n => n.kind), ['source', 'model', 'model']);
""")


def test_engine_options_are_written_only_for_models():
    _run(r"""
const g = D.fromEngine(DATA.cascade);
g.nodes[1].data.engine = {buffers: 2, share: true};
g.nodes[0].data.engine = {buffers: 2};
const e = D.toEngine(g);
eq(e.nodes[1].engine, {buffers: 2, share: true});
ok(!('engine' in e.nodes[0]), 'a source has no engine');
g.nodes[1].data.engine = {};
ok(!('engine' in D.toEngine(g).nodes[1]), 'an empty engine object is left out');
""")


def test_connection_rules_follow_produces_and_consumes():
    _run(r"""
const M = DATA.models;
const src = {kind: 'source', data: {}}, od = {kind: 'model', data: {model: 'yolov8-n_640x640'}};
const attr = {kind: 'model', data: {model: 'deepmar_resnet50_224x224'}};
const depth = {kind: 'model', data: {model: 'fastdepth_224x224'}};
const sr = {kind: 'model', data: {model: 'realesrgan-x2_192x192'}}, cpu = {kind: 'cpu', data: {op: 'headpose'}};
eq(D.canConnect(src, od, M), {ok: true, kind: 'frame', data: {}});
eq(D.canConnect(od, attr, M), {ok: true, kind: 'roi', data: {roi: {}}}, 'boxes feed crops');
eq(D.canConnect(od, cpu, M), {ok: true, kind: 'result', data: {carry: 'result'}});
eq(D.canConnect(sr, od, M).kind, 'frame', 'an image is handed off on a plain edge');
eq(D.canConnect(od, depth, M).reason, 'This model needs a full frame; boxes can only feed a model that takes crops');
eq(D.canConnect(depth, od, M).reason, 'Only boxes (as crops) or an image can feed another model');
eq(D.canConnect(od, src, M).reason, 'A source has no input');
eq(D.canConnect(cpu, od, M).reason, 'A CPU op ends a branch');
eq(D.canConnect(src, cpu, M).reason, 'A CPU op takes results from models');
eq(D.canConnect(od, {kind: 'model', data: {model: 'unknown_model'}}, M).kind, 'frame', 'unknown: --check decides');
for (const r of [D.canConnect(od, depth, M), D.canConnect(od, src, M), D.canConnect(cpu, od, M)])
  ok(D.STRINGS.indexOf(r.reason) !== -1, 'every reason is a dictionary key: ' + r.reason);
""")


def test_edge_labels_and_display_fields():
    _run(r"""
const g = D.fromEngine(DATA.cascade);
eq(D.edgeLabel(g.edges[1]), 'ROI · person');
eq(D.edgeLabel(g.edges[0]), '');
eq(D.edgeLabel({kind: 'result', data: {carry: 'result'}}, k => '<' + k + '>'), '<result>');
eq(D.edgeLabel({kind: 'roi', data: {roi: {classes: ['face'], align: 'face5', max: 4}}}), 'ROI · face · face5 · ≤4');
const n = D.decorate(g.nodes[1], DATA.models);
eq([n.label, n.sub, n.icon, n.category, n.noInput, n.noOutput], ['od', 'yolov8-n_640x640', 'task-object_detection', 'model', false, false]);
eq(D.decorate(g.nodes[0], {}).noInput, true);
eq(D.suggestId('yolov8-n_640x640', DATA.models), 'od'); eq(D.suggestId('mystery_1x1', {}), 'mystery');
""")


def test_projects_keep_layout_outside_the_graph():
    _run(r"""
const g = D.fromEngine(DATA.cascade);
g.nodes.forEach((n, i) => { n.x = 40 + 220 * i; n.y = 40; });
const p = D.makeProject(g, {name: 'person-attributes'}, {zoom: 1, offsetX: 0, offsetY: 0});
eq(p.schema, 1); eq(p.graph, DATA.cascade, 'graph is exactly what dx_app runs');
eq(p.layout.nodes.attr, {x: 480, y: 40});
const back = D.readAny(JSON.parse(JSON.stringify(p)));
ok(back.placed); eq(back.graph.nodes[2].x, 480); eq(back.view.zoom, 1); eq(back.meta.name, 'person-attributes');
const bare = D.readAny(DATA.volume);
ok(!bare.placed, 'a bare dx_app graph needs a layout'); eq(bare.meta.name, 'logistics_volume');
let threw = false; try { D.readAny({hello: 1}); } catch (e) { threw = true; } ok(threw);
""")


def test_pins_turn_results_into_badges_and_tints():
    _run(r"""
const check = {errors: [{node: 'od', edge: null}, {node: 'od', edge: null}, {node: null, edge: 'od->attr'},
                        {node: null, edge: null, code: 'GRAPH_CYCLE'}], missing: ['attr']};
const memory = {nodes: {od: {bytes: 123528064, shared_with: []}, od2: {bytes: 0, shared_with: ['od']}}};
const run = {node_ms: {od: 9, attr: 3}};
const p = D.pins(check, memory, run);
eq(p.badges.od.map(b => b.kind), ['error', 'mem', 'ms'], 'one badge per kind');
eq(p.badges.od[1].text, '118 MB'); eq(p.badges.od2[0].text, 'shared'); eq(p.badges.attr[0].kind, 'missing');
eq(p.edges, {'od->attr': 'error'}); eq(p.general.length, 1);
eq(p.tints, {od: 0.75, attr: 0.25});
eq(D.fmtBytes(4209067950), '3.92 GiB');
""")


def test_unusable_model_files_get_their_own_badge_and_edges_carry_the_message():
    """--check reports a model file that is there but cannot be used (`unusable`: invalid, unloadable, unknown); the
    node says which, and an edge error carries dx_app's message so the canvas announces it."""
    _run(r"""
const check = {errors: [{node: 'od', edge: null, what: 'cannot load'}, {node: null, edge: 'od->attr', what: 'needs boxes'},
                        {node: null, edge: 'od->attr', what: 'bad pad'}],
               missing: [], unusable: {od: 'invalid', attr: 'unloadable', x: 'unknown'}};
const p = D.pins(check, null, null, k => '<' + k + '>');
eq(p.badges.od.map(b => [b.kind, b.text]), [['missing', '<Broken file>'], ['error', '<error>']], 'the specific text comes first');
eq(p.badges.attr.map(b => [b.kind, b.text]), [['missing', '<Needs a newer DX-RT>']]);
eq(p.badges.x.map(b => [b.kind, b.text]), [['error', '<Unknown model>']]);
eq(p.edges, {'od->attr': {status: 'error', message: 'needs boxes; bad pad'}});
for (const k of ['Broken file', 'Needs a newer DX-RT', 'Unknown model']) ok(D.STRINGS.indexOf(k) !== -1, k);
""")


def test_a_memory_suggestion_patch_sets_and_removes_keys():
    """graph_memory's share suggestion carries {node: {"engine": {...}, "params": {...} | null}}; null removes the key."""
    _run(r"""
const data = {model: 'yolov8-n_640x640', params: {score_threshold: 0.2}, engine: {buffers: 4}, track: {algo: 'iou'}};
const out = D.applyPatch(data, {engine: {share: true, buffers: 2}, params: null});
eq(out, {model: 'yolov8-n_640x640', engine: {share: true, buffers: 2}, track: {algo: 'iou'}});
eq(data.params, {score_threshold: 0.2}, 'the input is not changed');
eq(D.applyPatch({model: 'm'}, {params: {a: 1}}), {model: 'm', params: {a: 1}});
eq(D.applyPatch({model: 'm'}, null), {model: 'm'});
""")
