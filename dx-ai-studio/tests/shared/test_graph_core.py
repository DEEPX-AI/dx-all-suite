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
eq(v.zoom, 1.5, 'fit never zooms past 150 %');
const v2 = C.zoomAt({zoom: 1, offsetX: 0, offsetY: 0}, 2, 100, 50);
const w2 = C.screenToWorld(v2, 100, 50); eq([w2.x, w2.y], [100, 50], 'zoom keeps the point under the cursor');
eq(C.zoomAt({zoom: 3, offsetX: 0, offsetY: 0}, 2, 0, 0).zoom, 3, 'zoom is clamped');
eq(C.fitTransform([], 800, 600), {zoom: 1, offsetX: 0, offsetY: 0});
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
