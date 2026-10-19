"""dx_app/static/js/graph-zone.js — zone and line geometry of the Graph Composer's editor, run in Node.

The editor itself is checked in a browser (tests/dx_app/test_graph_logic_browser.py); what is checked here is that a
drawn shape becomes exactly the parameter dx_app reads (fractions 0..1 of the frame) and back, the direction of a
line's arrow, and the hit tests and edits the mouse and keyboard use.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tests.browser_support import resolve_node_executable

ROOT = Path(__file__).resolve().parents[2]
ZONE = ROOT / "dx_app" / "static" / "js" / "graph-zone.js"

_PRELUDE = r"""
const fs = require('fs');
const vm = require('vm');
const sandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), sandbox);
const Z = sandbox.window.GraphZoneGeom;
const eq = (a, b, m) => { const x = JSON.stringify(a), y = JSON.stringify(b); if (x !== y) throw new Error((m || 'eq') + ': ' + x + ' != ' + y); };
const ok = (c, m) => { if (!c) throw new Error(m || 'assert'); };
"""


def _run(body: str) -> None:
    node = resolve_node_executable()
    if not node:
        pytest.skip("node is required for the graph-zone.js tests")
    proc = subprocess.run([node, "-e", _PRELUDE + body + "\nconsole.log('{\"ok\": true}');", str(ZONE)],
                          capture_output=True, text=True, cwd=str(ROOT), check=False)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert json.loads(proc.stdout.strip().splitlines()[-1]) == {"ok": True}


def test_params_become_shapes_and_back_in_dx_app_coordinates():
    _run(r"""
const zone = [0.45, 0.35, 1.0, 0.35, 1.0, 1.0, 0.45, 1.0];
const s = Z.shapeFrom(zone);
eq(s.points, [[0.45, 0.35], [1, 0.35], [1, 1], [0.45, 1]]);
eq(Z.paramFrom(s), zone);
eq(Z.shapeFrom([0.3, 1.0, 0.3, 0.0]).points, [[0.3, 1], [0.3, 0]], 'a line is two points');
eq(Z.shapeFrom([0.1, 'x', 0.2, 0.3]), null);
eq(Z.shapeFrom([0.1, 0.2, 0.3]), null, 'x, y pairs');
eq(Z.shapeFrom([0.1, 0.2]), null, 'at least two points');
eq(Z.shapeFrom('nope'), null);
eq(Z.shapeFrom([0.2, 0.2, 2, -1]).points, [[0.2, 0.2], [1, 0]], 'points outside the frame are clamped');
eq(Z.paramFrom({points: [[0.123456, 0.5]]}), [0.1235, 0.5], '4 decimals');
eq(Z.paramFrom(null), []);
""")


def test_the_frame_is_letterboxed_and_points_map_both_ways():
    _run(r"""
const f = Z.fit(1920, 1080, 800, 600);
eq([f.scale, f.ox, Math.round(f.oy), f.w, f.h], [800 / 1920, 0, 75, 800, 450]);
eq(Z.toScreen(f, [0.5, 0.5]), [400, 300]);
eq(Z.toNorm(f, 400, 300), [0.5, 0.5]);
eq(Z.toNorm(f, -50, 900), [0, 1], 'clamped to the frame');
""")


def test_hit_tests_find_points_edge_handles_and_shapes():
    _run(r"""
const f = Z.fit(100, 100, 100, 100);
const shapes = [{points: [[0.1, 0.1], [0.5, 0.1], [0.5, 0.5], [0.1, 0.5]]}, {points: [[0.7, 0.7], [0.9, 0.9]]}];
eq(Z.hitPoint(shapes, f, 51, 11, 6), {shape: 0, index: 1});
eq(Z.hitPoint(shapes, f, 30, 30, 6), null);
eq(Z.hitMidpoint(shapes, f, 30, 10, 6, true), {shape: 0, index: 0});
eq(Z.hitMidpoint(shapes, f, 10, 30, 6, true), {shape: 0, index: 3}, 'the closing edge of a polygon');
eq(Z.hitMidpoint([shapes[1]], f, 80, 80, 6, false), {shape: 0, index: 0});
eq(Z.hitShape(shapes, f, 30, 30, 6, true), 0, 'inside the zone');
eq(Z.hitShape(shapes, f, 80, 81, 6, true), 1, 'near the line');
eq(Z.hitShape(shapes, f, 95, 20, 6, true), -1);
""")


def test_points_are_added_removed_and_moved_within_limits():
    _run(r"""
const s = {points: [[0, 0], [1, 0], [1, 1]]};
eq(Z.insertAfter(s, 2, true), 3); eq(s.points[3], [0.5, 0.5], 'between the last and the first');
eq(Z.insertAfter({points: [[0, 0], [1, 1]]}, 1, false), -1, 'an open line has no edge after its end');
ok(Z.removePoint(s, 3, 3) && s.points.length === 3);
ok(!Z.removePoint(s, 0, 3), 'a zone keeps 3 points');
Z.nudge(s, 1, 0.5, -0.5); eq(s.points[1], [1, 0], 'clamped');
const many = {points: []}; for (let i = 0; i < Z.MAX_POINTS; i++) many.points.push([i / 100, 0]);
eq(Z.insertAfter(many, 0, true), -1, 'at most MAX_POINTS');
eq(Z.rect(0.9, 0.5, 0.4, 0.4).points[1], [1, 0.3], 'a new zone stays in the frame');
""")


def test_the_line_arrow_and_crossed_zones():
    _run(r"""
const a = Z.arrow([0, 0], [10, 0]);
eq(a.mid, [5, 0]); eq(a.normal, [0, 1], 'A->B to the right: "in" points down the screen, from its left to its right');
eq(Z.arrow([10, 0], [0, 0]).normal, [0, -1], 'flipping A and B turns the arrow round');
eq(Z.arrow([0.3, 1], [0.3, 0]).normal, [1, 0], "line_counting.json's line: in is a crossing to the right");
ok(Z.selfIntersects([[0, 0], [1, 1], [1, 0], [0, 1]]), 'a bow tie');
ok(!Z.selfIntersects([[0, 0], [1, 0], [1, 1], [0, 1]]));
ok(!Z.selfIntersects([[0, 0], [1, 0], [0.5, 1]]), 'a triangle never crosses itself');
""")
