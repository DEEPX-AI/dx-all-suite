/* DX AI Studio — graph canvas core (pure logic, no DOM).

   Geometry, hit testing, history, clipboard, layout and alignment for shared/static/dx-graph-canvas.js. It has no DOM so Node
   can test it (tests/shared/test_graph_core.py). A graph is {nodes: [{id, x, y, ...}], edges: [{id, from, to, ...}]};
   any other field on a node or an edge is carried along unchanged. */
(function (root) {
  'use strict';

  var NODE_W = 160, NODE_H = 56, PORT_R = 6, PORT_HIT = 12, GRID = 20, HISTORY_MAX = 50;
  var MIN_ZOOM = 0.3, MAX_ZOOM = 3, FIT_MAX_ZOOM = 1.25;
  var ID_RE = /^[A-Za-z][A-Za-z0-9_-]{0,31}$/;

  function snap(v) { return Math.round(v / GRID) * GRID; }
  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function clone(v) { return JSON.parse(JSON.stringify(v)); }
  function edgeId(from, to) { return from + '->' + to; }

  function nodeMap(nodes) {
    var m = {};
    for (var i = 0; i < nodes.length; i++) m[nodes[i].id] = nodes[i];
    return m;
  }

  function outPort(n) { return { x: n.x + NODE_W, y: n.y + NODE_H / 2 }; }
  function inPort(n) { return { x: n.x, y: n.y + NODE_H / 2 }; }

  function hitNode(nodes, x, y) {
    for (var i = nodes.length - 1; i >= 0; i--) {
      var n = nodes[i];
      if (x >= n.x && x <= n.x + NODE_W && y >= n.y && y <= n.y + NODE_H) return n;
    }
    return null;
  }

  /* which: 'out' or 'in'. A node with noOutput / noInput has no such port. */
  function hitPort(nodes, x, y, which) {
    for (var i = nodes.length - 1; i >= 0; i--) {
      var n = nodes[i];
      if (which === 'out' && n.noOutput) continue;
      if (which === 'in' && n.noInput) continue;
      var p = which === 'out' ? outPort(n) : inPort(n);
      if (Math.abs(x - p.x) < PORT_HIT && Math.abs(y - p.y) < PORT_HIT) return n;
    }
    return null;
  }

  /* Control-point offset of an edge's cubic bezier: half the horizontal gap, at least 40 so an edge drawn backwards
     still loops instead of folding onto itself, at most 80 (the Pipeline Builder's curve). */
  function controlOffset(x1, x2) { return clamp(Math.abs(x2 - x1) * 0.5, 40, 80); }

  function bezierPoint(x1, y1, x2, y2, t) {
    var c = controlOffset(x1, x2), mt = 1 - t;
    var cx1 = x1 + c, cx2 = x2 - c;
    return {
      x: mt * mt * mt * x1 + 3 * mt * mt * t * cx1 + 3 * mt * t * t * cx2 + t * t * t * x2,
      y: mt * mt * mt * y1 + 3 * mt * mt * t * y1 + 3 * mt * t * t * y2 + t * t * t * y2
    };
  }

  function distToBezierSq(px, py, x1, y1, x2, y2) {
    var best = Infinity;
    for (var i = 0; i <= 20; i++) {
      var b = bezierPoint(x1, y1, x2, y2, i / 20);
      var d = (px - b.x) * (px - b.x) + (py - b.y) * (py - b.y);
      if (d < best) best = d;
    }
    return best;
  }

  /* An edge is drawn as a list of cubic segments {x1, y1, c1x, c1y, c2x, c2y, x2, y2}. A forward edge is one bezier.
     A backward edge (its input port left of its output port) with room between the two nodes runs as a wrapped row
     does: right out of the source, a turn into the lane above the lower node, left along the lane, and a turn into
     the target from the left, so it passes between rows instead of across them. */
  var LANE = 36, TURN = 24, TURN_R = 12, KAPPA = 0.5523;

  function lineSeg(ax, ay, bx, by) {
    return { x1: ax, y1: ay, c1x: ax + (bx - ax) / 3, c1y: ay + (by - ay) / 3,
             c2x: ax + 2 * (bx - ax) / 3, c2y: ay + 2 * (by - ay) / 3, x2: bx, y2: by };
  }

  /* A quarter turn from (ax, ay) to (bx, by) about the corner (kx, ky). */
  function turnSeg(ax, ay, kx, ky, bx, by) {
    return { x1: ax, y1: ay, c1x: ax + KAPPA * (kx - ax), c1y: ay + KAPPA * (ky - ay),
             c2x: bx + KAPPA * (kx - bx), c2y: by + KAPPA * (ky - by), x2: bx, y2: by };
  }

  /* The lane of a backward edge from the output port (x1, y1) to the input port (x2, y2), or null when it is drawn as
     one bezier: in the gap between the two nodes, next to the lower one (the target when the edge goes down). */
  function laneOf(x1, y1, x2, y2) {
    if (x2 >= x1) return null;
    var down = y2 > y1, gap = Math.abs(y2 - y1) - NODE_H;
    if (gap < 24) return null;
    var off = Math.min(LANE, gap / 2);
    return down ? y2 - NODE_H / 2 - off : y1 - NODE_H / 2 - off;
  }

  function edgeRoute(x1, y1, x2, y2) {
    var lane = laneOf(x1, y1, x2, y2);
    if (lane === null) {
      var c = controlOffset(x1, x2);
      return { segs: [{ x1: x1, y1: y1, c1x: x1 + c, c1y: y1, c2x: x2 - c, c2y: y2, x2: x2, y2: y2 }],
               mid: bezierPoint(x1, y1, x2, y2, 0.5) };
    }
    var xa = x1 + TURN, xb = x2 - TURN, s1 = lane > y1 ? 1 : -1, s2 = y2 > lane ? 1 : -1;
    var r = Math.min(TURN_R, Math.abs(lane - y1) / 2, Math.abs(y2 - lane) / 2);
    var segs = [
      lineSeg(x1, y1, xa - r, y1),
      turnSeg(xa - r, y1, xa, y1, xa, y1 + s1 * r),
      lineSeg(xa, y1 + s1 * r, xa, lane - s1 * r),
      turnSeg(xa, lane - s1 * r, xa, lane, xa - r, lane),
      lineSeg(xa - r, lane, xb + r, lane),
      turnSeg(xb + r, lane, xb, lane, xb, lane + s2 * r),
      lineSeg(xb, lane + s2 * r, xb, y2 - s2 * r),
      turnSeg(xb, y2 - s2 * r, xb, y2, xb + r, y2),
      lineSeg(xb + r, y2, x2, y2)
    ];
    return { segs: segs, mid: { x: (x1 + x2) / 2, y: lane } };
  }

  function cubicPoint(s, t) {
    var mt = 1 - t, a = mt * mt * mt, b = 3 * mt * mt * t, c = 3 * mt * t * t, d = t * t * t;
    return { x: a * s.x1 + b * s.c1x + c * s.c2x + d * s.x2, y: a * s.y1 + b * s.c1y + c * s.c2y + d * s.y2 };
  }

  function distToSegmentSq(px, py, a, b) {
    var dx = b.x - a.x, dy = b.y - a.y, l = dx * dx + dy * dy;
    var t = l ? clamp(((px - a.x) * dx + (py - a.y) * dy) / l, 0, 1) : 0;
    var x = a.x + t * dx - px, y = a.y + t * dy - py;
    return x * x + y * y;
  }

  function distToRouteSq(px, py, route) {
    var best = Infinity;
    route.segs.forEach(function (s) {
      var prev = cubicPoint(s, 0);
      for (var i = 1; i <= 16; i++) {
        var p = cubicPoint(s, i / 16);
        best = Math.min(best, distToSegmentSq(px, py, prev, p));
        prev = p;
      }
    });
    return best;
  }

  function edgeEnds(map, e) {
    var f = map[e.from], t = map[e.to];
    if (!f || !t) return null;
    var a = outPort(f), b = inPort(t);
    return { x1: a.x, y1: a.y, x2: b.x, y2: b.y };
  }

  function hitEdge(nodes, edges, x, y, threshold) {
    var th = threshold || 8, map = nodeMap(nodes);
    for (var i = edges.length - 1; i >= 0; i--) {
      var p = edgeEnds(map, edges[i]);
      if (!p) continue;
      if (distToRouteSq(x, y, edgeRoute(p.x1, p.y1, p.x2, p.y2)) < th * th) return edges[i];
    }
    return null;
  }

  function edgeMidpoint(nodes, e) {
    var p = edgeEnds(nodeMap(nodes), e);
    return p ? edgeRoute(p.x1, p.y1, p.x2, p.y2).mid : null;
  }

  /* True when adding from->to would close a cycle: `from` is already reachable from `to`. */
  function wouldCycle(edges, from, to) {
    if (from === to) return true;
    var out = {};
    edges.forEach(function (e) { (out[e.from] = out[e.from] || []).push(e.to); });
    var seen = {}, stack = [to];
    while (stack.length) {
      var n = stack.pop();
      if (n === from) return true;
      if (seen[n]) continue;
      seen[n] = true;
      (out[n] || []).forEach(function (m) { stack.push(m); });
    }
    return false;
  }

  function hasEdge(edges, from, to) {
    return edges.some(function (e) { return e.from === from && e.to === to; });
  }

  function bounds(nodes) {
    if (!nodes.length) return null;
    var b = { minX: Infinity, minY: Infinity, maxX: -Infinity, maxY: -Infinity };
    nodes.forEach(function (n) {
      b.minX = Math.min(b.minX, n.x); b.minY = Math.min(b.minY, n.y);
      b.maxX = Math.max(b.maxX, n.x + NODE_W); b.maxY = Math.max(b.maxY, n.y + NODE_H);
    });
    return b;
  }

  /* bounds() of the nodes widened by the turns of the edges routed through a lane, which reach past the nodes. */
  function graphBounds(nodes, edges) {
    var b = bounds(nodes), map = nodeMap(nodes);
    if (!b) return b;
    (edges || []).forEach(function (e) {
      var p = edgeEnds(map, e);
      if (!p || laneOf(p.x1, p.y1, p.x2, p.y2) === null) return;
      b.maxX = Math.max(b.maxX, p.x1 + TURN); b.minX = Math.min(b.minX, p.x2 - TURN);
    });
    return b;
  }

  /* The view {zoom, offsetX, offsetY} that shows every node inside a w x h viewport, centred in what is left after
     `pad`: px on every side, or {top, right, bottom, left} so overlays (a toolbar, a minimap) stay clear. Fitting never
     zooms past FIT_MAX_ZOOM, so a graph of one or two nodes keeps the size the cards are drawn for. With `edges`, the
     turns of edges routed through a lane count too (graphBounds). */
  function fitTransform(nodes, w, h, pad, edges) {
    var p = pad == null ? 40 : pad, b = edges ? graphBounds(nodes, edges) : bounds(nodes);
    var ins = typeof p === 'number' ? { top: p, right: p, bottom: p, left: p } : p;
    if (!b || w <= 0 || h <= 0) return { zoom: 1, offsetX: 0, offsetY: 0 };
    var bw = b.maxX - b.minX, bh = b.maxY - b.minY;
    var aw = Math.max(1, w - ins.left - ins.right), ah = Math.max(1, h - ins.top - ins.bottom);
    var zoom = clamp(Math.min(aw / bw, ah / bh), MIN_ZOOM, FIT_MAX_ZOOM);
    return {
      zoom: zoom,
      offsetX: ins.left + (aw - bw * zoom) / 2 - b.minX * zoom,
      offsetY: ins.top + (ah - bh * zoom) / 2 - b.minY * zoom
    };
  }

  function screenToWorld(view, sx, sy) {
    return { x: (sx - view.offsetX) / view.zoom, y: (sy - view.offsetY) / view.zoom };
  }

  function worldToScreen(view, wx, wy) {
    return { x: wx * view.zoom + view.offsetX, y: wy * view.zoom + view.offsetY };
  }

  /* Zoom by `factor`, keeping the screen point (sx, sy) where it is. */
  function zoomAt(view, factor, sx, sy) {
    var zoom = clamp(view.zoom * factor, MIN_ZOOM, MAX_ZOOM);
    var w = screenToWorld(view, sx, sy);
    return { zoom: zoom, offsetX: sx - w.x * zoom, offsetY: sy - w.y * zoom };
  }

  function nodesInRect(nodes, r) {
    var x1 = Math.min(r.x1, r.x2), x2 = Math.max(r.x1, r.x2), y1 = Math.min(r.y1, r.y2), y2 = Math.max(r.y1, r.y2);
    return nodes.filter(function (n) {
      return n.x < x2 && n.x + NODE_W > x1 && n.y < y2 && n.y + NODE_H > y1;
    }).map(function (n) { return n.id; });
  }

  /* Keyboard order: left to right, then top to bottom, the direction a pipeline flows. */
  function tabOrder(nodes) {
    return nodes.slice().sort(function (a, b) {
      return (a.x - b.x) || (a.y - b.y) || (a.id < b.id ? -1 : 1);
    }).map(function (n) { return n.id; });
  }

  /* The node after (dir 1) or before (dir -1) `currentId`; null past either end, so Tab can leave the canvas. */
  function nextInOrder(nodes, currentId, dir) {
    var order = tabOrder(nodes);
    if (!order.length) return null;
    var i = order.indexOf(currentId);
    if (i === -1) return dir > 0 ? order[0] : order[order.length - 1];
    var j = i + dir;
    return j >= 0 && j < order.length ? order[j] : null;
  }

  function sanitizeId(s) {
    var v = String(s || '').replace(/[^A-Za-z0-9_-]+/g, '_').replace(/^[^A-Za-z]+/, '');
    return (v || 'node').slice(0, 32);
  }

  function uniqueId(base, taken) {
    var b = sanitizeId(base), set = {};
    (taken || []).forEach(function (t) { set[t] = true; });
    if (!set[b]) return b;
    for (var i = 2; ; i++) {
      var c = b.slice(0, 32 - String(i).length - 1) + '_' + i;
      if (!set[c]) return c;
    }
  }

  function removeNodes(g, ids) {
    var drop = {};
    ids.forEach(function (id) { drop[id] = true; });
    return {
      nodes: g.nodes.filter(function (n) { return !drop[n.id]; }),
      edges: g.edges.filter(function (e) { return !drop[e.from] && !drop[e.to]; })
    };
  }

  function renameNode(g, oldId, newId) {
    var out = clone(g);
    if (oldId === newId) return out;
    out.nodes.forEach(function (n) { if (n.id === oldId) n.id = newId; });
    out.edges.forEach(function (e) {
      if (e.from === oldId) e.from = newId;
      if (e.to === oldId) e.to = newId;
      e.id = edgeId(e.from, e.to);
    });
    return out;
  }

  function copySelection(g, ids) {
    var keep = {};
    ids.forEach(function (id) { keep[id] = true; });
    return {
      nodes: clone(g.nodes.filter(function (n) { return keep[n.id]; })),
      edges: clone(g.edges.filter(function (e) { return keep[e.from] && keep[e.to]; }))
    };
  }

  /* Paste a clipboard into g, `offset` px down and right; nodes get new ids where theirs are taken.
     Returns {graph, ids} (ids of the pasted nodes). */
  function pasteClip(g, clip, offset) {
    var out = clone(g), off = offset == null ? 40 : offset, rename = {}, ids = [];
    var taken = out.nodes.map(function (n) { return n.id; });
    clip.nodes.forEach(function (n) {
      var c = clone(n);
      c.id = uniqueId(n.id, taken);
      taken.push(c.id);
      rename[n.id] = c.id;
      c.x = snap(n.x + off);
      c.y = snap(n.y + off);
      out.nodes.push(c);
      ids.push(c.id);
    });
    clip.edges.forEach(function (e) {
      var c = clone(e);
      c.from = rename[e.from];
      c.to = rename[e.to];
      c.id = edgeId(c.from, c.to);
      out.edges.push(c);
    });
    return { graph: out, ids: ids };
  }

  /* Layered layout: a node's rank is its longest distance from a node without inputs, and each rank is a column.
     With the canvas size (opts.width, opts.height, and opts.insets: the fitTransform paddings the canvas tries), a
     graph with more ranks than fit across is wrapped: the ranks are laid in rows of k columns, read left to right then
     top to bottom, with a lane between rows for the edges that wrap (edgeRoute). k is the widest row count whose fitted
     zoom is close to the best one (at least WRAP_KEEP of it, the best counted up to 100 %), so a graph that already
     fits stays in one row. Without a usable size the ranks stay in one row. g is not changed. */
  var WRAP_KEEP = 0.85, BAND_GAP = 64;

  function autoLayout(g, opts) {
    var o = opts || {}, colW = o.colW || 280, rowH = o.rowH || 100, x0 = o.x0 || 40, y0 = o.y0 || 40;
    var out = clone(g), depth = {}, incoming = {};
    out.nodes.forEach(function (n) { depth[n.id] = 0; incoming[n.id] = 0; });
    out.edges.forEach(function (e) { if (e.to in incoming) incoming[e.to] += 1; });
    var queue = out.nodes.filter(function (n) { return incoming[n.id] === 0; }).map(function (n) { return n.id; });
    var guard = 0;
    while (queue.length && guard++ < 10000) {
      var id = queue.shift();
      out.edges.forEach(function (e) {
        if (e.from !== id || !(e.to in depth)) return;
        depth[e.to] = Math.max(depth[e.to], depth[id] + 1);
        incoming[e.to] -= 1;
        if (incoming[e.to] === 0) queue.push(e.to);
      });
    }
    var cols = {}, ranks = 0;
    out.nodes.forEach(function (n) {
      (cols[depth[n.id]] = cols[depth[n.id]] || []).push(n);
      ranks = Math.max(ranks, depth[n.id] + 1);
    });
    Object.keys(cols).forEach(function (d) {
      cols[d].sort(function (a, b) { return (a.y - b.y) || (a.id < b.id ? -1 : 1); });
    });

    function place(k) {
      var top = y0, bandTop = [];
      for (var b = 0; b * k < ranks; b++) {
        var tall = 1;
        for (var d = b * k; d < Math.min(ranks, (b + 1) * k); d++) tall = Math.max(tall, (cols[d] || []).length);
        bandTop.push(top);
        top += (tall - 1) * rowH + NODE_H + BAND_GAP;
      }
      Object.keys(cols).forEach(function (d) {
        var r = Number(d), band = Math.floor(r / k);
        cols[d].forEach(function (n, i) { n.x = x0 + (r - band * k) * colW; n.y = bandTop[band] + i * rowH; });
      });
    }

    var w = Number(o.width) || 0, h = Number(o.height) || 0, insets = o.insets && o.insets.length ? o.insets : [40];
    if (ranks < 2 || w < NODE_W * 2 || h < NODE_H * 2) { place(Math.max(1, ranks)); return out; }
    var zooms = [], best = 0;
    for (var k = ranks; k >= 1; k--) {
      place(k);
      var z = 0;
      insets.forEach(function (ins) { z = Math.max(z, fitTransform(out.nodes, w, h, ins, out.edges).zoom); });
      zooms[k] = z;
      best = Math.max(best, z);
    }
    var want = Math.min(best, 1) * WRAP_KEEP, pick = 1;
    for (var k2 = ranks; k2 >= 1; k2--) { if (zooms[k2] >= want - 1e-9) { pick = k2; break; } }
    place(pick);
    return out;
  }

  /* Line up the nodes `ids` of g: 'left' and 'top' move them to the selection's first edge, 'center' and 'middle'
     to its centre line (on the grid). Other nodes and every edge stay as they are; g is not changed. */
  function alignNodes(g, ids, how) {
    var out = clone(g), pick = {};
    (ids || []).forEach(function (id) { pick[id] = true; });
    var sel = out.nodes.filter(function (n) { return pick[n.id]; }), b = bounds(sel);
    if (sel.length < 2) return out;
    sel.forEach(function (n) {
      if (how === 'left') n.x = b.minX;
      else if (how === 'center') n.x = snap((b.minX + b.maxX) / 2 - NODE_W / 2);
      else if (how === 'top') n.y = b.minY;
      else if (how === 'middle') n.y = snap((b.minY + b.maxY) / 2 - NODE_H / 2);
    });
    return out;
  }

  /* Space the nodes `ids` of g evenly along `axis` ('x' or 'y'): the two outermost stay, the rest are spread between
     them in their current order (on the grid). Needs three nodes; g is not changed. */
  function distributeNodes(g, ids, axis) {
    var out = clone(g), pick = {}, k = axis === 'y' ? 'y' : 'x';
    (ids || []).forEach(function (id) { pick[id] = true; });
    var sel = out.nodes.filter(function (n) { return pick[n.id]; });
    if (sel.length < 3) return out;
    sel.sort(function (a, b) { return (a[k] - b[k]) || (a.id < b.id ? -1 : 1); });
    var first = sel[0][k], step = (sel[sel.length - 1][k] - first) / (sel.length - 1);
    for (var i = 1; i < sel.length - 1; i++) sel[i][k] = snap(first + i * step);
    return out;
  }

  /* Undo history of graph snapshots (strings), newest `limit` kept. */
  function createHistory(limit) {
    var max = limit || HISTORY_MAX, stack = [], idx = -1;
    return {
      push: function (s) {
        if (idx >= 0 && stack[idx] === s) return false;
        stack = stack.slice(0, idx + 1);
        stack.push(s);
        if (stack.length > max) stack.shift();
        idx = stack.length - 1;
        return true;
      },
      reset: function (s) { stack = [s]; idx = 0; },
      undo: function () { if (idx <= 0) return null; idx -= 1; return stack[idx]; },
      redo: function () { if (idx >= stack.length - 1) return null; idx += 1; return stack[idx]; },
      canUndo: function () { return idx > 0; },
      canRedo: function () { return idx < stack.length - 1; },
      size: function () { return stack.length; }
    };
  }

  root.DXGraphCore = {
    NODE_W: NODE_W, NODE_H: NODE_H, PORT_R: PORT_R, PORT_HIT: PORT_HIT, GRID: GRID, HISTORY_MAX: HISTORY_MAX,
    MIN_ZOOM: MIN_ZOOM, MAX_ZOOM: MAX_ZOOM, FIT_MAX_ZOOM: FIT_MAX_ZOOM, ID_RE: ID_RE,
    snap: snap, clamp: clamp, clone: clone, edgeId: edgeId, nodeMap: nodeMap, outPort: outPort, inPort: inPort,
    hitNode: hitNode, hitPort: hitPort, controlOffset: controlOffset, bezierPoint: bezierPoint,
    edgeRoute: edgeRoute, cubicPoint: cubicPoint, graphBounds: graphBounds,
    distToBezierSq: distToBezierSq, hitEdge: hitEdge, edgeMidpoint: edgeMidpoint, wouldCycle: wouldCycle,
    hasEdge: hasEdge, bounds: bounds, fitTransform: fitTransform, screenToWorld: screenToWorld,
    worldToScreen: worldToScreen, zoomAt: zoomAt, nodesInRect: nodesInRect, tabOrder: tabOrder,
    nextInOrder: nextInOrder, sanitizeId: sanitizeId, uniqueId: uniqueId, removeNodes: removeNodes,
    renameNode: renameNode, copySelection: copySelection, pasteClip: pasteClip, autoLayout: autoLayout,
    alignNodes: alignNodes, distributeNodes: distributeNodes, createHistory: createHistory
  };
})(typeof window !== 'undefined' ? window : this);
