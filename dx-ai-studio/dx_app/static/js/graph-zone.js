/* DX App — Graph Composer zone and line editor.

   GraphZoneGeom (pure, Node-tested in tests/dx_app/test_graph_zone.py) turns a logic node's drawn param into a shape
   and back, in dx_app's coordinates: fractions 0..1 of the source frame, a "polygon" param a flat
   [x0, y0, x1, y1, ...] of at least 3 points, a "line" param [x0, y0, x1, y1] from A to B. A line counts "in" for a
   crossing from the left of A->B to its right, which is where its arrow points; flipping swaps A and B.
   The editor that uses it is graph-zone-editor.js. */
(function (root) {
  'use strict';

  var MAX_POINTS = 64;

  function clamp01(v) { return Math.min(1, Math.max(0, v)); }
  function round(v) { return Math.round(v * 10000) / 10000; }
  function num(v) { return typeof v === 'number' && isFinite(v); }

  function pairs(flat) {
    var out = [];
    for (var i = 0; i + 1 < flat.length; i += 2) out.push([flat[i], flat[i + 1]]);
    return out;
  }

  /* The shape {points: [[x, y], ...]} of a polygon or line param, or null when the value is not one (too short,
     not numbers). Points outside the frame are clamped. */
  function shapeFrom(value) {
    if (!Array.isArray(value) || value.length < 4 || value.length % 2 || !value.every(num)) return null;
    return { points: pairs(value).slice(0, MAX_POINTS).map(function (p) { return [clamp01(p[0]), clamp01(p[1])]; }) };
  }

  /* The param value of a shape: the flat list dx_app reads, 4 decimals. */
  function paramFrom(shape) {
    var out = [];
    ((shape && shape.points) || []).forEach(function (p) { out.push(round(p[0]), round(p[1])); });
    return out;
  }

  /* Letterbox a frame of w x h in a box of bw x bh. */
  function fit(w, h, bw, bh) {
    var s = Math.min(bw / w, bh / h);
    return { scale: s, ox: (bw - w * s) / 2, oy: (bh - h * s) / 2, w: w * s, h: h * s };
  }
  function toScreen(f, p) { return [f.ox + p[0] * f.w, f.oy + p[1] * f.h]; }
  function toNorm(f, x, y) { return [clamp01((x - f.ox) / f.w), clamp01((y - f.oy) / f.h)]; }

  function dist2(ax, ay, bx, by) { return (ax - bx) * (ax - bx) + (ay - by) * (ay - by); }

  /* The point under (x, y) within r px: {shape, index}, nearest first; null when none. */
  function hitPoint(shapes, f, x, y, r) {
    var best = null, bd = r * r;
    shapes.forEach(function (s, si) {
      s.points.forEach(function (p, pi) {
        var q = toScreen(f, p), d = dist2(q[0], q[1], x, y);
        if (d <= bd) { bd = d; best = { shape: si, index: pi }; }
      });
    });
    return best;
  }

  function edges(s, closed) {
    var out = [], n = s.points.length;
    for (var i = 0; i < n - 1; i++) out.push([i, i + 1]);
    if (closed && n > 2) out.push([n - 1, 0]);
    return out;
  }

  /* The handle in the middle of an edge under (x, y): {shape, index} to insert after `index`; null when none. */
  function hitMidpoint(shapes, f, x, y, r, closed) {
    var best = null, bd = r * r;
    shapes.forEach(function (s, si) {
      if (s.points.length >= MAX_POINTS) return;
      edges(s, closed).forEach(function (e) {
        var a = toScreen(f, s.points[e[0]]), b = toScreen(f, s.points[e[1]]);
        var d = dist2((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, x, y);
        if (d <= bd) { bd = d; best = { shape: si, index: e[0] }; }
      });
    });
    return best;
  }

  function inside(points, x, y) {
    var c = false;
    for (var i = 0, j = points.length - 1; i < points.length; j = i++) {
      var a = points[i], b = points[j];
      if ((a[1] > y) !== (b[1] > y) && x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]) c = !c;
    }
    return c;
  }

  function segDist2(px, py, a, b) {
    var dx = b[0] - a[0], dy = b[1] - a[1], l = dx * dx + dy * dy;
    var t = l ? Math.max(0, Math.min(1, ((px - a[0]) * dx + (py - a[1]) * dy) / l)) : 0;
    return dist2(px, py, a[0] + t * dx, a[1] + t * dy);
  }

  /* The shape under (x, y): inside a polygon, or within r px of a line; the last drawn wins. -1 when none. */
  function hitShape(shapes, f, x, y, r, closed) {
    for (var si = shapes.length - 1; si >= 0; si--) {
      var pts = shapes[si].points.map(function (p) { return toScreen(f, p); });
      if (closed && pts.length > 2 && inside(pts, x, y)) return si;
      for (var i = 0; i < pts.length - 1; i++) if (segDist2(x, y, pts[i], pts[i + 1]) <= r * r) return si;
    }
    return -1;
  }

  function insertAfter(s, i, closed) {
    if (s.points.length >= MAX_POINTS) return -1;
    var j = i + 1 < s.points.length ? i + 1 : (closed ? 0 : -1);
    if (j < 0) return -1;
    var a = s.points[i], b = s.points[j];
    s.points.splice(i + 1, 0, [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]);
    return i + 1;
  }

  function removePoint(s, i, min) {
    if (s.points.length <= min || i < 0 || i >= s.points.length) return false;
    s.points.splice(i, 1);
    return true;
  }

  function nudge(s, i, dx, dy) {
    var p = s.points[i];
    if (p) s.points[i] = [clamp01(p[0] + dx), clamp01(p[1] + dy)];
  }

  /* The "in" arrow of a line A->B in screen space (y down): its middle and the unit normal pointing from the left
     of A->B to its right. */
  function arrow(a, b) {
    var dx = b[0] - a[0], dy = b[1] - a[1], l = Math.sqrt(dx * dx + dy * dy) || 1;
    return { mid: [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], normal: [-dy / l, dx / l] };
  }

  function cross(o, a, b) { return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]); }
  function segsCross(p1, p2, p3, p4) {
    var d1 = cross(p3, p4, p1), d2 = cross(p3, p4, p2), d3 = cross(p1, p2, p3), d4 = cross(p1, p2, p4);
    return ((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) && ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0));
  }

  /* True when two edges of a closed polygon cross (the zone's inside is then ambiguous). */
  function selfIntersects(points) {
    var n = points.length;
    if (n < 4) return false;
    for (var i = 0; i < n; i++) {
      for (var j = i + 1; j < n; j++) {
        if (Math.abs(i - j) <= 1 || (i === 0 && j === n - 1)) continue;
        if (segsCross(points[i], points[(i + 1) % n], points[j], points[(j + 1) % n])) return true;
      }
    }
    return false;
  }

  function rect(cx, cy, w, h) {
    return { points: [[cx - w / 2, cy - h / 2], [cx + w / 2, cy - h / 2], [cx + w / 2, cy + h / 2], [cx - w / 2, cy + h / 2]]
      .map(function (p) { return [clamp01(p[0]), clamp01(p[1])]; }) };
  }

  root.GraphZoneGeom = {
    MAX_POINTS: MAX_POINTS, shapeFrom: shapeFrom, paramFrom: paramFrom, fit: fit, toScreen: toScreen,
    toNorm: toNorm, hitPoint: hitPoint, hitMidpoint: hitMidpoint, hitShape: hitShape, insertAfter: insertAfter,
    removePoint: removePoint, nudge: nudge, arrow: arrow, selfIntersects: selfIntersects, rect: rect,
    clone: function (shapes) { return JSON.parse(JSON.stringify(shapes)); }
  };
})(typeof window !== 'undefined' ? window : this);
