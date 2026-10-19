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

# Logic blocks as dx_app's --list-ops --json describes them (fixture recorded from the dx_app Phase 2 plan's catalog)
# and two of its six samples.
_FIX = ROOT / "tests" / "dx_app" / "fixtures" / "graph"
OPS = {o["op"]: o for o in json.loads((_FIX / "list_ops.json").read_text(encoding="utf-8")) if o["type"] == "logic"}
ZONE = json.loads((_FIX / "examples" / "zone_intrusion.json").read_text(encoding="utf-8"))
PPE = json.loads((_FIX / "examples" / "ppe_zone_check.json").read_text(encoding="utf-8"))

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
    data = json.dumps({"cascade": CASCADE, "volume": VOLUME, "models": MODELS, "ops": OPS, "zone": ZONE,
                       "ppe": PPE})
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


# Phase 2: logic blocks.

def test_logic_graphs_round_trip_with_their_drawn_params():
    _run(r"""
for (const k of ['zone', 'ppe']) eq(D.toEngine(D.fromEngine(DATA[k]), DATA[k].name), DATA[k], k);
const g = D.fromEngine(DATA.zone);
eq(g.nodes.map(n => n.kind), ['source', 'model', 'logic', 'logic', 'logic']);
eq(g.edges.map(e => e.kind), ['frame', 'result', 'result', 'result']);
eq(D.fromEngine(DATA.ppe).edges[3].kind, 'roi', 'zone -> ROI -> classifier');
""")


def test_logic_connection_rules_follow_list_ops():
    _run(r"""
const M = Object.assign({}, DATA.models, {'deepmar_resnet18_224x224': {task: 'person_attribute', produces: 'scores', consumes: 'either'},
  'repvgg-a0-reid_256x128': {task: 'person_reid', produces: 'vector', consumes: 'either'}}), O = DATA.ops;
const src = {id: 'cam', kind: 'source', data: {}}, od = {id: 'od', kind: 'model', data: {model: 'yolov8-n_640x640'}};
const depth = {id: 'depth', kind: 'model', data: {model: 'fastdepth_224x224'}};
const attr = {id: 'attr', kind: 'model', data: {model: 'deepmar_resnet18_224x224'}};
const reid = {id: 'reid', kind: 'model', data: {model: 'repvgg-a0-reid_256x128'}};
const L = (id, op, params) => ({id: id, kind: 'logic', data: {type: 'logic', op: op, params: params || {}}});
const person = L('person', 'filter'), zone = L('zone', 'zone'), line = L('line', 'line'), alarm = L('alarm', 'condition');
const known = L('known', 'gallery'), count = L('count', 'count');
const g = {nodes: [src, od, person, zone, line, alarm, attr, reid, depth, known, count],
           edges: [{from: 'cam', to: 'od', kind: 'frame'}, {from: 'od', to: 'person', kind: 'result'},
                   {from: 'person', to: 'zone', kind: 'result'}, {from: 'zone', to: 'attr', kind: 'roi', data: {roi: {}}},
                   {from: 'od', to: 'reid', kind: 'roi', data: {roi: {}}}]};
eq(D.canConnect(od, person, M, O, {nodes: g.nodes, edges: []}), {ok: true, kind: 'result', data: {carry: 'result'}}, 'boxes into a filter');
eq(D.canConnect(src, line, M, O, g).reason, 'A logic block takes results, not frames');
eq(D.canConnect(depth, line, M, O, g).reason, 'This logic block does not take this kind of result', 'a densemap is no boxes');
eq(D.outputOf(zone, M, O, g), 'boxes', 'a zone hands on what reaches it');
eq(D.canConnect(zone, line, M, O, g).kind, 'result', 'the zone boxes into a line');
eq(D.canConnect(zone, alarm, M, O, g).kind, 'result', 'boxes into a condition');
eq(D.canConnect(attr, alarm, M, O, g).kind, 'result', 'scores per crop into a condition');
eq(D.canConnect(attr, line, M, O, g).reason, 'This logic block does not take this kind of result');
eq(D.canConnect(reid, known, M, O, g).kind, 'result', 'vectors per crop into a gallery');
eq(D.canConnect(line, alarm, M, O, g).kind, 'result', 'records into a condition');
eq(D.canConnect(line, count, M, O, g).reason, 'This logic block does not take this kind of result', 'records are not boxes');
eq(D.canConnect(zone, depth, M, O, g).reason, 'Only a block that hands on boxes can feed a model, as crops');
eq(D.canConnect(line, attr, M, O, g).reason, 'Only a block that hands on boxes can feed a model, as crops');
eq(D.canConnect(zone, {id: 'v', kind: 'cpu', data: {op: 'volume'}}, M, O, g).reason, 'A CPU op takes results from models');
eq(D.canConnect(od, zone, M, O, g).reason, 'This logic block takes no more inputs', 'a zone takes one input');
ok(D.canConnect(od, count, M, O, {nodes: g.nodes, edges: [1, 2, 3, 4, 5, 6, 7].map(i => ({from: 'x' + i, to: 'count'}))}).ok, 'count takes eight');
eq(D.canConnect(od, L('mine', 'user', {input: 'boxes', output: 'boxes'}), M, O, g).kind, 'result');
eq(D.canConnect(od, L('x', 'brand_new_op'), M, O, g).kind, 'result', 'an op this page does not know is left to --check');
eq(D.edgeKinds(od, zone, M, undefined, g), ['result'], 'no op list yet: --check decides');
""")


def test_logic_nodes_look_like_logic_and_start_with_what_they_require():
    _run(r"""
const n = D.decorate({id: 'zone', kind: 'logic', data: {op: 'zone'}}, DATA.models);
eq([n.category, n.icon, n.sub, n.noInput, n.noOutput], ['logic', 'logic-zone', 'Logic · zone', false, false]);
eq(D.decorate({id: 'x', kind: 'logic', data: {op: 'new_op'}}, {}).icon, 'puzzle');
eq(D.decorate({id: 'u', kind: 'logic', data: {op: 'user', params: {name: 'ppe_rule'}}}, {}).sub, 'Logic · ppe_rule');
eq(D.logicDefaults(DATA.ops.zone), {polygon: [0.25, 0.25, 0.75, 0.25, 0.75, 0.75, 0.25, 0.75]});
eq(D.logicDefaults(DATA.ops.line), {line: [0.1, 0.5, 0.9, 0.5]});
eq(D.logicDefaults(DATA.ops.user), {name: 'my_logic', input: 'boxes', output: 'boxes'});
eq(D.logicDefaults(DATA.ops.condition), {}, 'optional params keep dx_app defaults');
const d = D.logicDefaults(DATA.ops.zone); d.polygon[0] = 9;
eq(D.logicDefaults(DATA.ops.zone).polygon[0], 0.25, 'each node gets its own copy');
""")


def test_a_block_that_needs_tracking_names_the_untracked_detector():
    _run(r"""
const O = DATA.ops;
const g = {nodes: [{id: 'od', kind: 'model', data: {model: 'm'}}, {id: 'zone', kind: 'logic', data: {op: 'zone'}},
                   {id: 'line', kind: 'logic', data: {op: 'line'}}, {id: 'od2', kind: 'model', data: {model: 'm', track: {}}},
                   {id: 'line2', kind: 'logic', data: {op: 'line'}}],
           edges: [{from: 'od', to: 'zone'}, {from: 'zone', to: 'line'}, {from: 'od2', to: 'line2'}]};
eq(D.untrackedFeeds(g, 'line', O), ['od'], 'through the zone to its detector');
eq(D.untrackedFeeds(g, 'line2', O), [], 'tracked');
eq(D.untrackedFeeds(g, 'zone', O), [], 'a zone does not need tracking');
""")


def test_event_counts_become_badges():
    _run(r"""
const p = D.pins(null, null, {event_counts: {zone: {enter: 2, exit: 1}, alarm: {intrusion: 1}, quiet: {}}}, k => k);
eq(p.badges.zone, [{kind: 'events', text: 'Events: 3'}]);
eq(p.badges.alarm, [{kind: 'events', text: 'Events: 1'}]);
ok(!p.badges.quiet, 'no badge without events');
""")
