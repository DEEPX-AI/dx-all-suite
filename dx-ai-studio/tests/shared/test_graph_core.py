"""shared/static/dx-graph-core.js — the graph canvas's pure logic, run in Node.

Geometry, hit testing, history, clipboard and layout have no DOM, so they are tested here directly; drawing and
input are tested in a browser (tests/shared/test_graph_canvas_browser.py).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tests.browser_support import resolve_node_executable

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "shared" / "static" / "dx-graph-core.js"

_PRELUDE = r"""
const fs = require('fs');
const vm = require('vm');
const sandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), sandbox);
const C = sandbox.window.DXGraphCore;
const eq = (a, b, m) => { const x = JSON.stringify(a), y = JSON.stringify(b); if (x !== y) throw new Error((m || 'eq') + ': ' + x + ' != ' + y); };
const ok = (c, m) => { if (!c) throw new Error(m || 'assert'); };
"""


def _run(body: str) -> None:
    node = resolve_node_executable()
    if not node:
        pytest.skip("node is required for the dx-graph-core.js tests")
    proc = subprocess.run([node, "-e", _PRELUDE + body + "\nconsole.log(JSON.stringify({ok: true}));", str(CORE)],
                          capture_output=True, text=True, cwd=str(ROOT), check=False)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert json.loads(proc.stdout.strip().splitlines()[-1]) == {"ok": True}


def test_grid_and_hit_testing():
    _run(r"""
eq(C.snap(29), 20, 'snap down'); eq(C.snap(31), 40, 'snap up');
const nodes = [{id: 'a', x: 0, y: 0}, {id: 'b', x: 300, y: 0}, {id: 's', x: 0, y: 200, noInput: true}];
eq(C.hitNode(nodes, 10, 10).id, 'a'); eq(C.hitNode(nodes, 200, 10), null);
eq(C.hitPort(nodes, 160, 28, 'out').id, 'a', 'output port on the right edge');
eq(C.hitPort(nodes, 300, 28, 'in').id, 'b', 'input port on the left edge');
eq(C.hitPort(nodes, 0, 228, 'in'), null, 'a source has no input port');
const edges = [{id: 'a->b', from: 'a', to: 'b'}];
eq(C.hitEdge(nodes, edges, 230, 28).id, 'a->b'); eq(C.hitEdge(nodes, edges, 230, 120), null);
const mid = C.edgeMidpoint(nodes, edges[0]); eq([mid.x, mid.y], [230, 28]);
""")


def test_cycles_and_duplicates_are_detected():
    _run(r"""
ok(C.wouldCycle([{from: 'a', to: 'b'}, {from: 'b', to: 'c'}], 'c', 'a'), 'c->a closes a cycle');
ok(!C.wouldCycle([{from: 'a', to: 'b'}], 'a', 'c'), 'a->c is fine');
ok(C.wouldCycle([], 'a', 'a'), 'a self loop is a cycle');
ok(C.hasEdge([{from: 'a', to: 'b'}], 'a', 'b')); ok(!C.hasEdge([{from: 'a', to: 'b'}], 'b', 'a'));
""")


def test_view_transforms():
    _run(r"""
const v = C.fitTransform([{id: 'a', x: 0, y: 0}, {id: 'b', x: 340, y: 0}], 1000, 600, 40);
const s = C.worldToScreen(v, 250, 28);
ok(Math.abs(s.x - 500) < 1 && Math.abs(s.y - 300) < 1, 'the middle of the graph lands in the middle ' + JSON.stringify(s));
eq(v.zoom, 1.25, 'fit never zooms past 125 %: a small graph stays the size the cards are drawn for');
const v2 = C.zoomAt({zoom: 1, offsetX: 0, offsetY: 0}, 2, 100, 50);
const w2 = C.screenToWorld(v2, 100, 50); eq([w2.x, w2.y], [100, 50], 'zoom keeps the point under the cursor');
eq(C.zoomAt({zoom: 3, offsetX: 0, offsetY: 0}, 2, 0, 0).zoom, 3, 'zoom is clamped');
eq(C.fitTransform([], 800, 600), {zoom: 1, offsetX: 0, offsetY: 0});
""")


def test_fit_leaves_room_for_overlays_per_side():
    """The canvas passes the toolbar and minimap as insets; the graph is fitted and centred in what is left."""
    _run(r"""
eq(C.FIT_MAX_ZOOM, 1.25);
eq(C.fitTransform([{id: 'a', x: 0, y: 0}], 1000, 600, 24).zoom, 1.25, 'one node stops at 125 %');
const ins = {top: 60, right: 24, bottom: 140, left: 24};
const v = C.fitTransform([{id: 'a', x: 0, y: 0}, {id: 'b', x: 600, y: 0}], 700, 600, ins);
eq(Math.round(v.zoom * 1000), Math.round((700 - 48) / 760 * 1000), 'a wide graph uses the width less the side insets');
const tl = C.worldToScreen(v, 0, 0), br = C.worldToScreen(v, 760, 56);
ok(tl.x >= 24 - 0.5 && br.x <= 700 - 24 + 0.5, 'inside the side insets ' + JSON.stringify([tl, br]));
ok(tl.y >= 60 - 0.5 && br.y <= 600 - 140 + 0.5, 'below the toolbar and above the minimap');
ok(Math.abs((tl.y + br.y) / 2 - (60 + 460) / 2) < 1, 'centred in the free band');
const tall = C.fitTransform([{id: 'a', x: 0, y: 0}, {id: 'b', x: 0, y: 400}], 700, 600, ins);
eq(Math.round(tall.zoom * 1000), Math.round((600 - 200) / 456 * 1000), 'a tall graph uses the height less top and bottom');
eq(C.fitTransform([{id: 'a', x: 0, y: 0}], 100, 100, {top: 80, right: 0, bottom: 80, left: 0}).zoom, C.MIN_ZOOM,
   'no room left: the smallest zoom, not a negative one');
""")

def test_selection_order_and_ids():
    _run(r"""
const nodes = [{id: 'a', x: 0, y: 0}, {id: 'b', x: 300, y: 0}, {id: 's', x: 0, y: 200}];
eq(C.nodesInRect(nodes, {x1: -10, y1: -10, x2: 170, y2: 60}), ['a'], 'marquee');
eq(C.tabOrder(nodes), ['a', 's', 'b'], 'left to right, then top to bottom');
eq(C.nextInOrder(nodes, 'a', 1), 's'); eq(C.nextInOrder(nodes, 'b', 1), null, 'Tab leaves after the last node');
eq(C.nextInOrder(nodes, null, -1), 'b');
eq(C.uniqueId('od', ['od', 'od_2']), 'od_3'); eq(C.sanitizeId('9 bad id!'), 'bad_id_'); eq(C.sanitizeId(''), 'node');
ok(C.ID_RE.test('od_2') && !C.ID_RE.test('2od') && !C.ID_RE.test('a b'));
""")


def test_edit_operations_keep_edges_consistent():
    _run(r"""
const g = {nodes: [{id: 'a', x: 0, y: 0}, {id: 'b', x: 200, y: 0}, {id: 'c', x: 400, y: 0}],
           edges: [{id: 'a->b', from: 'a', to: 'b'}, {id: 'b->c', from: 'b', to: 'c'}]};
eq(C.removeNodes(g, ['b']).edges, [], 'edges of a removed node go with it');
eq(C.renameNode(g, 'b', 'x').edges.map(e => e.id), ['a->x', 'x->c']);
const clip = C.copySelection(g, ['a', 'b']); eq(clip.edges.length, 1, 'only edges inside the selection are copied');
const p = C.pasteClip(g, clip, 40);
eq(p.ids, ['a_2', 'b_2']); eq(p.graph.edges[2], {id: 'a_2->b_2', from: 'a_2', to: 'b_2'});
eq([p.graph.nodes[3].x, p.graph.nodes[3].y], [40, 40], 'pasted 40 px down and right, on the grid');
eq(g.nodes.length, 3, 'the input graph is not changed');
""")


def test_auto_layout_columns_follow_the_longest_path():
    _run(r"""
const L = C.autoLayout({nodes: [{id: 'c', x: 0, y: 0}, {id: 'a', x: 0, y: 0}, {id: 'b', x: 0, y: 0}],
                        edges: [{from: 'a', to: 'b'}, {from: 'b', to: 'c'}, {from: 'a', to: 'c'}]});
const pos = {}; L.nodes.forEach(n => { pos[n.id] = [n.x, n.y]; });
eq(pos, {c: [600, 40], a: [40, 40], b: [320, 40]});
""")


def test_history_keeps_fifty_snapshots_and_drops_the_redo_branch():
    _run(r"""
const h = C.createHistory(50);
for (let i = 0; i < 60; i++) h.push('s' + i);
eq(h.size(), 50);
let undos = 0; while (h.undo() !== null) undos++;
eq(undos, 49, 'the oldest kept snapshot is the floor');
eq(h.redo(), 's11'); ok(h.canRedo());
h.push('new'); ok(!h.canRedo(), 'a new change drops the redo branch');
ok(!h.push('new'), 'the same snapshot twice is one step');
eq(C.HISTORY_MAX, 50);
""")


def test_align_lines_up_the_selection_and_leaves_the_rest():
    _run(r"""
const g = {nodes: [{id: 'a', x: 40, y: 20}, {id: 'b', x: 300, y: 140}, {id: 'c', x: 120, y: 300}, {id: 'z', x: 900, y: 900}],
           edges: [{id: 'a->b', from: 'a', to: 'b'}]};
const pos = (h) => { const m = {}; h.nodes.forEach(n => { m[n.id] = [n.x, n.y]; }); return m; };
eq(pos(C.alignNodes(g, ['a', 'b', 'c'], 'left')), {a: [40, 20], b: [40, 140], c: [40, 300], z: [900, 900]}, 'left');
eq(pos(C.alignNodes(g, ['a', 'b', 'c'], 'top')), {a: [40, 20], b: [300, 20], c: [120, 20], z: [900, 900]}, 'top');
// The selection spans x 40..460: centre 250, so each card's left edge goes to 250 - 80 = 170, on the grid 180.
eq(pos(C.alignNodes(g, ['a', 'b', 'c'], 'center')), {a: [180, 20], b: [180, 140], c: [180, 300], z: [900, 900]}, 'center');
// y 20..356: middle 188, card top 188 - 28 = 160.
eq(pos(C.alignNodes(g, ['a', 'b', 'c'], 'middle')), {a: [40, 160], b: [300, 160], c: [120, 160], z: [900, 900]}, 'middle');
eq(pos(C.alignNodes(g, ['a'], 'left')), pos(g), 'one node has nothing to align with');
eq(C.alignNodes(g, ['a', 'b'], 'left').edges, g.edges, 'edges ride along');
eq(g.nodes[1].x, 300, 'the input graph is not changed');
""")


def test_distribute_spaces_the_selection_evenly_between_its_ends():
    _run(r"""
const g = {nodes: [{id: 'a', x: 0, y: 0}, {id: 'b', x: 100, y: 40}, {id: 'c', x: 600, y: 400}, {id: 'd', x: 200, y: 100}],
           edges: []};
const pos = (h) => { const m = {}; h.nodes.forEach(n => { m[n.id] = [n.x, n.y]; }); return m; };
// x order a(0) b(100) d(200) c(600): the ends stay, the middle two go to 200 and 400.
eq(pos(C.distributeNodes(g, ['a', 'b', 'c', 'd'], 'x')), {a: [0, 0], b: [200, 40], c: [600, 400], d: [400, 100]}, 'x');
// y order a(0) b(40) d(100) c(400): 0, 133.3 -> 140 on the grid, 266.7 -> 260, 400.
eq(pos(C.distributeNodes(g, ['a', 'b', 'c', 'd'], 'y')), {a: [0, 0], b: [100, 140], c: [600, 400], d: [200, 260]}, 'y');
eq(pos(C.distributeNodes(g, ['a', 'b'], 'x')), pos(g), 'two nodes have nothing to distribute');
""")


_CHAIN = r"""
const chain = ids => ({nodes: ids.map(id => ({id: id, x: 0, y: 0})),
                       edges: ids.slice(1).map((id, i) => ({id: ids[i] + '->' + id, from: ids[i], to: id}))});
const INSETS = [{top: 60, right: 24, bottom: 140, left: 24}, {top: 60, right: 180, bottom: 24, left: 24}];
const fitZoom = (L, w, h) => Math.max.apply(null, INSETS.map(i => C.fitTransform(L.nodes, w, h, i, L.edges).zoom));
const inside = (n, p) => p.x > n.x + 2 && p.x < n.x + C.NODE_W - 2 && p.y > n.y + 2 && p.y < n.y + C.NODE_H - 2;
const samples = (L, e) => {
  const m = C.nodeMap(L.nodes), a = C.outPort(m[e.from]), b = C.inPort(m[e.to]), out = [];
  C.edgeRoute(a.x, a.y, b.x, b.y).segs.forEach(s => { for (let i = 0; i <= 20; i++) out.push(C.cubicPoint(s, i / 20)); });
  return out;
};
const noEdgeCrossesANode = L => L.edges.forEach(e => samples(L, e).forEach(p => L.nodes.forEach(n =>
  ok(!inside(n, p), e.id + ' crosses ' + n.id + ' at ' + JSON.stringify(p)))));
"""


def test_auto_layout_wraps_a_long_chain_into_rows_that_fit_the_canvas():
    """A chain of five laid in one row is wider than a 714 x 558 canvas (about half size); given the canvas, the
    layout wraps the ranks into rows, read left to right then top to bottom, and the wrapping edge runs in the lane
    between the rows."""
    _run(_CHAIN + r"""
const g = chain(['cam', 'od', 'person', 'zone', 'alarm']);
const flat = C.autoLayout(g);
ok(fitZoom(flat, 714, 558) < 0.6, 'one row: ' + fitZoom(flat, 714, 558));
for (const [w, h, least] of [[714, 558, 0.8], [678, 558, 0.8], [480, 558, 0.7]]) {
  const L = C.autoLayout(g, {width: w, height: h, insets: INSETS});
  const z = fitZoom(L, w, h);
  ok(z >= least, w + 'x' + h + ': zoom ' + z);
  const rows = {}; L.nodes.forEach(n => { rows[n.y] = true; });
  ok(Object.keys(rows).length >= 2, 'wrapped into rows');
  eq(L.nodes.slice().sort((a, b) => (a.y - b.y) || (a.x - b.x)).map(n => n.id), ['cam', 'od', 'person', 'zone', 'alarm']);
  noEdgeCrossesANode(L);
  const m = C.nodeMap(L.nodes);
  L.edges.forEach(e => { const a = C.outPort(m[e.from]), b = C.inPort(m[e.to]);
    if (b.x < a.x) ok(C.edgeRoute(a.x, a.y, b.x, b.y).segs.length > 1, e.id + ' wraps through the lane'); });
}
""")


def test_auto_layout_keeps_a_chain_that_fits_in_one_row():
    _run(_CHAIN + r"""
const L = C.autoLayout(chain(['a', 'b', 'c']), {width: 714, height: 558, insets: INSETS});
eq(L.nodes.map(n => [n.x, n.y]), [[40, 40], [320, 40], [600, 40]], 'three fit at full size: one row, as before');
const tiny = C.autoLayout(chain(['a', 'b', 'c', 'd', 'e']), {width: 1, height: 1, insets: INSETS});
eq(tiny.nodes.map(n => n.y), [40, 40, 40, 40, 40], 'a canvas not laid out yet (1 x 1) gives the plain layout');
""")


def test_auto_layout_keeps_a_short_chain_in_one_row_even_at_a_lower_zoom():
    """Three ranks or fewer (cascade_od_attr: cam -> od -> attr) read best in one row: on a canvas narrower than the
    row they are not wrapped 2 + 1, the view zooms out instead."""
    _run(_CHAIN + r"""
for (const [w, h] of [[480, 558], [360, 700], [714, 558]]) {
  const L = C.autoLayout(chain(['cam', 'od', 'attr']), {width: w, height: h, insets: INSETS});
  eq(L.nodes.map(n => [n.x, n.y]), [[40, 40], [320, 40], [600, 40]], w + 'x' + h + ': one row');
}
const fan = C.autoLayout({nodes: ['cam', 'od', 'seg', 'depth'].map(id => ({id, x: 0, y: 0})),
  edges: ['od', 'seg', 'depth'].map(to => ({id: 'cam->' + to, from: 'cam', to}))}, {width: 360, height: 700, insets: INSETS});
eq(new Set(fan.nodes.map(n => n.x)).size, 2, 'a fan-out keeps its two columns');
const four = C.autoLayout(chain(['a', 'b', 'c', 'd']), {width: 360, height: 900, insets: INSETS});
ok(new Set(four.nodes.map(n => n.y)).size >= 2, 'four ranks still wrap when that reads better');
""")


def test_a_backward_edge_between_rows_runs_through_the_lane():
    """An edge whose input port is left of its output port, a row lower, leaves right, turns down into the lane above
    the target, runs left and enters the target from the left; it is hit and labelled on the lane."""
    _run(r"""
const nodes = [{id: 'a', x: 400, y: 0}, {id: 'b', x: 0, y: 128}], edges = [{id: 'a->b', from: 'a', to: 'b'}];
const r = C.edgeRoute(560, 28, 0, 156);
ok(r.segs.length > 1, 'routed');
const ys = []; r.segs.forEach(s => { for (let i = 0; i <= 10; i++) ys.push(C.cubicPoint(s, i / 10).y); });
ok(Math.min.apply(null, ys) >= 28 - 0.01 && Math.max.apply(null, ys) <= 156 + 0.01, 'stays between the ports');
eq(C.edgeMidpoint(nodes, edges[0]), {x: 280, y: 92}, 'the label sits in the middle of the lane');
eq(C.hitEdge(nodes, edges, 280, 92).id, 'a->b'); eq(C.hitEdge(nodes, edges, 280, 40), null);
eq(C.edgeRoute(160, 28, 300, 28).segs.length, 1, 'a forward edge is one curve');
eq(C.edgeRoute(560, 28, 0, 60).segs.length, 1, 'no room between the nodes: the loop as before');
const b = C.graphBounds(nodes, edges);
ok(b.maxX > 560 && b.minX < 0, 'the turns count in the bounds a fit uses ' + JSON.stringify(b));
""")
