/* DX App — Graph Composer zone and line editor (the #gc-zone-dialog modal). Geometry: graph-zone.js.

   open({nodeId, param, frameUri, ctx}) shows a frame of the block's input (/api/graph/frame) with every polygon and
   line of the logic blocks that read the same input, and edits one of them at a time: a dx_app zone or line node
   holds one shape, so several zones are several nodes. "Add zone" adds a zone node beside the edited one, fed by the
   same input; clicking another shape (or PageUp / PageDown) edits that node instead.
   Mouse: drag a point; drag the dot in the middle of a zone's edge to add a point; "Redraw zone" replaces the zone
   with points clicked one by one (Enter, a double click or a click on the first point ends; Escape keeps the old
   one). Keyboard on the drawing: [ and ] pick a point, arrows move it (Shift: further), Insert adds a point after
   it, Delete removes it, N adds a zone, F flips a line, Ctrl+Z / Ctrl+Y undo and redo. Points can also be typed in
   the table. Every finished edit writes the param with ctx.canvas().updateNode (one step of the graph canvas
   history), so undo here and on the canvas is the same; refresh() redraws from the graph after a change.
   Contract: tests/dx_app/test_graph_logic_browser.py */
window.GraphZoneEditor = (function () {
  'use strict';
  var Z = window.GraphZoneGeom;
  var HIT = 9, NUDGE = 0.005, NUDGE_FAR = 0.05, COMMIT_IDLE_MS = 500, FRAME = { width: 1280, height: 720 };
  var st = null;          // the open editor
  var els = {};

  function $id(i) { return document.getElementById(i); }
  function cur() { return st.targets[st.cur]; }
  function closed() { return !!cur() && cur().param.type === 'polygon'; }
  function minPoints() { return closed() ? Math.max(3, cur().param.min_points || 3) : 2; }
  function shape() { return st.shapes[st.cur]; }

  /* Every polygon or line param of the logic nodes whose frames come from this editor's input. */
  function collectTargets() {
    var c = st.ctx, out = [];
    c.canvas().getGraph().nodes.forEach(function (n) {
      if (n.kind !== 'logic') return;
      var spec = (c.state.ops || {})[(n.data || {}).op];
      if (!spec || c.sourceFor(n.id) !== st.frameUri) return;
      spec.params.forEach(function (p) {
        if (p.type === 'polygon' || p.type === 'line') out.push({ nodeId: n.id, param: p });
      });
    });
    return out;
  }

  function dirOf(t) {
    var n = st.ctx.nodeOf(t.nodeId);
    return n && n.data && n.data.params ? n.data.params.direction : undefined;
  }

  function valueOf(t) {
    var n = st.ctx.nodeOf(t.nodeId);
    return n && n.data && n.data.params ? n.data.params[t.param.name] : undefined;
  }

  function load(want) {
    var keep = want || (cur() ? { nodeId: cur().nodeId, name: cur().param.name } : null);
    st.targets = collectTargets();
    st.shapes = st.targets.map(function (t) { return Z.shapeFrom(valueOf(t)) || { points: [] }; });
    st.cur = 0;
    st.targets.forEach(function (t, i) { if (keep && t.nodeId === keep.nodeId && t.param.name === keep.name) st.cur = i; });
    var s = shape();
    if (!s || st.pt >= s.points.length || st.pt < 0) st.pt = s && s.points.length ? 0 : -1;
  }

  function commit() {
    clearTimeout(st.idle);
    st.idle = 0;
    var t = cur(), n = t && st.ctx.nodeOf(t.nodeId);
    if (!n) return;
    var data = st.ctx.D.clone(n.data || {});
    data.params = data.params || {};
    data.params[t.param.name] = Z.paramFrom(shape());
    st.committing = true;
    st.ctx.canvas().updateNode(t.nodeId, { data: data });
    st.committing = false;
    renderSide();
  }

  function commitLater() {
    clearTimeout(st.idle);
    st.idle = setTimeout(commit, COMMIT_IDLE_MS);
  }

  /* ── drawing ── */
  function cssVar(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }

  function layout() {
    var c = els.canvas, r = c.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
    c.width = Math.max(1, Math.round(r.width * dpr));
    c.height = Math.max(1, Math.round(r.height * dpr));
    st.dpr = dpr;
    st.box = { w: r.width, h: r.height };
    st.fit = Z.fit(st.frame.width, st.frame.height, r.width, r.height);
  }

  /* The "in" arrow ("in" along it, "out" against it, both by default: the line node's direction param). */
  function drawArrow(ctx, a, b, color, dir) {
    var ar = Z.arrow(a, b), len = 28;
    function one(sign) {
      var nx = sign * ar.normal[0], ny = sign * ar.normal[1], tip = [ar.mid[0] + nx * len, ar.mid[1] + ny * len];
      ctx.beginPath(); ctx.moveTo(ar.mid[0], ar.mid[1]); ctx.lineTo(tip[0], tip[1]);
      ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.stroke();
      ctx.beginPath(); ctx.moveTo(tip[0] + nx * 8, tip[1] + ny * 8);
      ctx.lineTo(tip[0] - ny * 6, tip[1] + nx * 6); ctx.lineTo(tip[0] + ny * 6, tip[1] - nx * 6); ctx.closePath();
      ctx.fillStyle = color; ctx.fill();
    }
    one(dir === 'out' ? -1 : 1);
    if (!dir || dir === 'both') one(-1);
  }

  function paint() {
    if (!st) return;
    layout();
    var ctx = els.canvas.getContext('2d'), f = st.fit;
    ctx.setTransform(st.dpr, 0, 0, st.dpr, 0, 0);
    ctx.clearRect(0, 0, st.box.w, st.box.h);
    ctx.fillStyle = cssVar('--surface-sunken');
    ctx.fillRect(0, 0, st.box.w, st.box.h);
    if (st.img) ctx.drawImage(st.img, f.ox, f.oy, f.w, f.h);
    else {
      ctx.fillStyle = cssVar('--surface-panel');
      ctx.fillRect(f.ox, f.oy, f.w, f.h);
      ctx.strokeStyle = cssVar('--border-subtle');
      ctx.lineWidth = 1;
      for (var g = 1; g < 10; g++) {
        ctx.beginPath(); ctx.moveTo(f.ox + f.w * g / 10, f.oy); ctx.lineTo(f.ox + f.w * g / 10, f.oy + f.h); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(f.ox, f.oy + f.h * g / 10); ctx.lineTo(f.ox + f.w, f.oy + f.h * g / 10); ctx.stroke();
      }
    }
    var accent = cssVar('--accent'), other = cssVar('--status-warn'), text = cssVar('--text-primary'), panel = cssVar('--surface-panel');
    var font = '600 12px ' + (cssVar('--font') || 'sans-serif');
    st.shapes.forEach(function (s, si) {
      var t = st.targets[si], active = si === st.cur, poly = t.param.type === 'polygon';
      var pts = s.points.map(function (p) { return Z.toScreen(f, p); });
      if (!pts.length) return;
      ctx.beginPath();
      pts.forEach(function (p, i) { if (i) ctx.lineTo(p[0], p[1]); else ctx.moveTo(p[0], p[1]); });
      if (poly && !(st.drawing && active)) ctx.closePath();
      ctx.setLineDash(active ? [] : [6, 4]);
      ctx.lineWidth = active ? 3 : 2;
      ctx.strokeStyle = active ? accent : other;
      if (poly) {
        ctx.globalAlpha = active ? 0.22 : 0.1;
        ctx.fillStyle = active ? accent : other;
        ctx.fill();
        ctx.globalAlpha = 1;
      }
      ctx.stroke();
      ctx.setLineDash([]);
      if (!poly && pts.length === 2) drawArrow(ctx, pts[0], pts[1], active ? accent : other, dirOf(t));
      ctx.font = font;                              // the name on a chip of the panel colour: any frame behind it
      var lw = ctx.measureText(t.nodeId).width, lx = pts[0][0] + 8, ly = pts[0][1] - 8;
      ctx.globalAlpha = 0.85;
      ctx.fillStyle = panel;
      ctx.fillRect(lx - 4, ly - 13, lw + 8, 18);
      ctx.globalAlpha = 1;
      ctx.fillStyle = text;
      ctx.fillText(t.nodeId, lx, ly);
      if (!active) return;
      if (poly && !st.drawing) {                    // the dots that add a point; a line keeps its two ends
        for (var i = 0; i < pts.length && pts.length < Z.MAX_POINTS; i++) {
          var a = pts[i], b = pts[(i + 1) % pts.length];
          ctx.beginPath(); ctx.arc((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 3.5, 0, Math.PI * 2);
          ctx.fillStyle = panel; ctx.fill(); ctx.strokeStyle = accent; ctx.lineWidth = 1.5; ctx.stroke();
        }
      }
      pts.forEach(function (p, i) {
        ctx.beginPath(); ctx.arc(p[0], p[1], i === st.pt ? 7 : 5, 0, Math.PI * 2);
        ctx.fillStyle = i === st.pt ? accent : panel; ctx.fill();
        ctx.strokeStyle = accent; ctx.lineWidth = 2; ctx.stroke();
      });
    });
  }

  /* ── side panel: the shapes on this frame, the points, warnings ── */
  function fmtCoord(v) { return String(Math.round(v * 1000) / 1000); }

  function renderSide() {
    var c = st.ctx, h = c.h;
    els.list.textContent = '';
    st.targets.forEach(function (t, si) {
      var b = h('button', { type: 'button', class: 'btn btn-ghost btn-sm' + (si === st.cur ? ' is-active' : ''),
        'aria-pressed': String(si === st.cur), text: t.nodeId + (st.targets.filter(function (x) { return x.nodeId === t.nodeId; }).length > 1 ? ' · ' + t.param.name : '') });
      b.addEventListener('click', function () { select(si, 0); els.canvas.focus(); });
      els.list.appendChild(b);
    });
    els.points.textContent = '';
    var s = shape();
    if (s) {
      var rows = s.points.map(function (p, i) {
        function input(axis) {
          var el = h('input', { type: 'number', class: 'input', min: '0', max: '1', step: '0.01', value: fmtCoord(p[axis]),
            'aria-label': c.fmt(T('Point {n} {axis}'), { n: i + 1, axis: axis ? 'y' : 'x' }) });
          el.addEventListener('change', function () {
            var nv = Number(el.value);
            if (!isFinite(nv)) return;
            shape().points[i][axis] = Math.min(1, Math.max(0, nv));
            st.pt = i;
            commit();
            paint();
          });
          return el;
        }
        return h('tr', { class: i === st.pt ? 'is-active' : '' }, [h('th', { scope: 'row', text: String(i + 1) }),
          h('td', {}, [input(0)]), h('td', {}, [input(1)])]);
      });
      els.points.appendChild(h('table', { class: 'gc-zone-points' }, [
        h('caption', { class: 'dx-sr-only', text: T('Points') }),
        h('thead', {}, [h('tr', {}, [h('th', { text: '#' }), h('th', { text: 'x' }), h('th', { text: 'y' })])]),
        h('tbody', {}, rows)]));
    }
    var warns = [];
    if (closed() && s && Z.selfIntersects(s.points)) warns.push(T('A zone crosses itself; dx_app may read its inside differently.'));
    if (!st.img && st.frameError) warns.push(st.frameError);
    els.warn.textContent = warns.join(' ');
    els.warn.hidden = !warns.length;
    renderTools();
  }

  function renderTools() {
    var c = st.ctx, h = c.h;
    function btn(icon, label, fn, disabled) {
      var b = h('button', { type: 'button', class: 'btn btn-ghost btn-sm', disabled: !!disabled }, [c.icon(icon), h('span', { text: ' ' + label })]);
      b.addEventListener('click', function () { fn(); if (!st.drawing) els.canvas.focus(); });
      return b;
    }
    var s = shape(), kids = [];
    if (closed()) {
      kids.push(btn('plus', T('Add zone'), addZone));
      kids.push(btn('logic-zone', T('Redraw zone'), startDraw));
      kids.push(btn('x', T('Delete point'), deletePoint, !s || s.points.length <= minPoints() || st.pt < 0));
    } else if (cur()) {
      kids.push(btn('refresh', T('Flip direction'), flip, !s || s.points.length !== 2));
    }
    kids.push(btn('undo', T('Undo'), undo, !st.ctx.canvas().canUndo()));
    kids.push(btn('redo', T('Redo'), redo, !st.ctx.canvas().canRedo()));
    els.tools.textContent = '';
    kids.forEach(function (k) { els.tools.appendChild(k); });
  }

  function announce(msg) { els.live.textContent = msg; }

  function describePoint() {
    var s = shape(), p = s && s.points[st.pt];
    if (!p) return;
    announce(st.ctx.fmt(T('Point {n} of {total}: x {x}, y {y}'), { n: st.pt + 1, total: s.points.length,
      x: fmtCoord(p[0]), y: fmtCoord(p[1]) }));
  }

  function select(si, pi) {
    if (st.idle) commit();
    st.cur = si;
    st.pt = pi;
    renderSide();
    paint();
    describePoint();
  }

  /* ── edits ── */
  /* A zone node beside the edited one, with its params and a new rectangle, fed by the same input. */
  function addZone() {
    var c = st.ctx, t = cur(), n = c.nodeOf(t.nodeId);
    if (!n) return;
    var data = c.D.clone(n.data || {});
    data.params = data.params || {};
    data.params[t.param.name] = Z.paramFrom(Z.rect(0.5, 0.5, 0.4, 0.4));
    var spec = c.D.decorate({ id: t.nodeId, kind: 'logic', data: data }, c.state.models, T);
    var id = c.canvas().addNode(spec, { x: n.x + 80, y: n.y + 28 + 2 * 56 });
    var src = c.canvas().getGraph().edges.filter(function (e) { return e.to === t.nodeId; })[0];
    if (src) c.canvas().connect(src.from, id);
    load({ nodeId: id, name: t.param.name });
    st.pt = 0;
    renderSide();
    paint();
    announce(c.fmt(T('Zone {node} added'), { node: id }));
  }

  function startDraw() {
    st.backup = st.shapes[st.cur];
    st.shapes[st.cur] = { points: [] };
    st.pt = -1;
    st.drawing = true;
    els.canvas.classList.add('is-drawing');
    announce(T('Click to add points; Enter, a double click or a click on the first point finishes; Escape cancels.'));
    paint();
    els.canvas.focus();
  }

  function finishDraw(keep) {
    if (!st.drawing) return;
    st.drawing = false;
    els.canvas.classList.remove('is-drawing');
    if (!keep || shape().points.length < minPoints()) {
      st.shapes[st.cur] = st.backup;
      st.pt = 0;
      renderSide();
      paint();
      announce(T('Drawing cancelled'));
      return;
    }
    st.pt = 0;
    commit();
    paint();
    describePoint();
  }

  function deletePoint() {
    var s = shape();
    if (!s || !Z.removePoint(s, st.pt, minPoints())) return;
    st.pt = Math.min(st.pt, s.points.length - 1);
    commit();
    paint();
    describePoint();
  }

  function insertPoint() {
    var s = shape();
    if (!s || !closed()) return;
    var i = Z.insertAfter(s, Math.max(0, st.pt), true);
    if (i < 0) return;
    st.pt = i;
    commit();
    paint();
    describePoint();
  }

  function flip() {
    var s = shape();
    if (!s || closed() || s.points.length !== 2) return;
    s.points.reverse();
    commit();
    paint();
    announce(T('Direction flipped'));
  }

  /* ── pointer ── */
  function pos(e) {
    var r = els.canvas.getBoundingClientRect();
    return [e.clientX - r.left, e.clientY - r.top];
  }

  function onDown(e) {
    if (e.button !== 0 || !cur()) return;
    layout();                                     // the side panel may have changed the drawing's width
    var p = pos(e), f = st.fit;
    els.canvas.focus();
    if (st.drawing) {
      var s = shape(), first = s.points[0] && Z.toScreen(f, s.points[0]);
      if (first && s.points.length >= minPoints() && Math.abs(first[0] - p[0]) <= HIT && Math.abs(first[1] - p[1]) <= HIT) {
        finishDraw(true);
        return;
      }
      if (s.points.length < Z.MAX_POINTS) s.points.push(Z.toNorm(f, p[0], p[1]));
      st.pt = s.points.length - 1;
      paint();
      return;
    }
    var hit = Z.hitPoint([shape()], f, p[0], p[1], HIT);
    if (!hit && closed()) {
      var mid = Z.hitMidpoint([shape()], f, p[0], p[1], HIT, true);
      if (mid) {
        var at = Z.insertAfter(shape(), mid.index, true);
        if (at >= 0) hit = { shape: 0, index: at };
      }
    }
    if (hit) {
      st.pt = hit.index;
      st.drag = true;
      renderSide();
      paint();
      e.preventDefault();
      return;
    }
    var si = -1;
    st.shapes.forEach(function (s2, i) {
      if (si < 0 && i !== st.cur && Z.hitShape([s2], f, p[0], p[1], HIT, st.targets[i].param.type === 'polygon') === 0) si = i;
    });
    if (si >= 0) select(si, 0);
  }

  function onMove(e) {
    if (!st || !st.drag) return;
    var p = pos(e);
    shape().points[st.pt] = Z.toNorm(st.fit, p[0], p[1]);
    paint();
  }

  function onUp() {
    if (!st || !st.drag) return;
    st.drag = false;
    commit();
    describePoint();
  }

  function onDbl(e) {
    if (st.drawing) { e.preventDefault(); finishDraw(true); }
  }

  /* ── keyboard ── */
  function onKey(e) {
    var s = shape(), k = e.key, mod = e.ctrlKey || e.metaKey;
    if (mod && (k === 'z' || k === 'Z') && !e.shiftKey) { e.preventDefault(); undo(); return; }
    if (mod && (k === 'y' || k === 'Y' || ((k === 'z' || k === 'Z') && e.shiftKey))) { e.preventDefault(); redo(); return; }
    if (st.drawing) {
      if (k === 'Enter') { e.preventDefault(); finishDraw(true); }
      else if (k === 'Escape') { e.preventDefault(); e.stopPropagation(); finishDraw(false); }
      return;
    }
    if ((k === '[' || k === ']') && s && s.points.length) {
      e.preventDefault();
      st.pt = (Math.max(0, st.pt) + (k === ']' ? 1 : -1) + s.points.length) % s.points.length;
      paint(); renderSide(); describePoint();
      return;
    }
    if ((k === 'PageDown' || k === 'PageUp') && st.targets.length > 1) {
      e.preventDefault();
      select((st.cur + (k === 'PageDown' ? 1 : -1) + st.targets.length) % st.targets.length, 0);
      return;
    }
    if (k.indexOf('Arrow') === 0 && s && st.pt >= 0) {
      e.preventDefault();
      var step = e.shiftKey ? NUDGE_FAR : NUDGE;
      Z.nudge(s, st.pt, k === 'ArrowLeft' ? -step : k === 'ArrowRight' ? step : 0, k === 'ArrowUp' ? -step : k === 'ArrowDown' ? step : 0);
      paint();
      describePoint();
      commitLater();
      return;
    }
    if (k === 'Insert' || k === '+') { e.preventDefault(); insertPoint(); return; }
    if (k === 'Delete' || k === 'Backspace') { e.preventDefault(); deletePoint(); return; }
    if ((k === 'n' || k === 'N') && closed()) { e.preventDefault(); addZone(); return; }
    if ((k === 'f' || k === 'F') && !closed()) { e.preventDefault(); flip(); }
  }

  function undo() {
    if (st.idle) commit();
    st.ctx.canvas().undo();
  }

  function redo() { st.ctx.canvas().redo(); }

  /* ── open / close ── */
  function build() {
    var h = st.ctx.h, dlg = $id('gc-zone-dialog');
    els.body = $id('gc-zone-body');
    els.body.textContent = '';
    els.tools = h('div', { class: 'gc-zone-tools', role: 'toolbar', 'aria-label': T('Zone tools') });
    els.canvas = h('canvas', { class: 'gc-zone-canvas', tabindex: '0', role: 'application',
      'aria-label': T('Zone drawing. [ and ] pick a point, arrow keys move it, Insert adds a point, Delete removes it, PageUp and PageDown pick another shape, N adds a zone, F flips a line, Ctrl+Z undoes.') });
    els.list = h('div', { class: 'gc-zone-list', role: 'group', 'aria-label': T('Shapes on this frame') });
    els.points = h('div', { class: 'gc-zone-points-wrap' });
    els.warn = h('p', { class: 'gc-help gc-zone-warn', role: 'status' });
    els.live = h('div', { class: 'dx-sr-only', id: 'gc-zone-live', 'aria-live': 'polite' });
    els.body.appendChild(els.tools);
    els.body.appendChild(h('div', { class: 'gc-zone-main' }, [els.canvas,
      h('div', { class: 'gc-zone-side' }, [h('p', { class: 'gc-drawn-label', text: T('Shapes on this frame') }), els.list, els.points, els.warn])]));
    els.body.appendChild(els.live);
    els.canvas.addEventListener('mousedown', onDown);
    els.canvas.addEventListener('dblclick', onDbl);
    els.canvas.addEventListener('keydown', onKey);
    if (typeof ResizeObserver === 'function') new ResizeObserver(function () { if (st) paint(); }).observe(els.canvas);
    if (!dlg.dataset.bound) {
      dlg.dataset.bound = '1';
      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onUp);
      dlg.addEventListener('close', function () {
        if (st) { if (st.drawing) finishDraw(false); if (st.idle) commit(); }
        st = null;
      });
      $id('gc-zone-done').addEventListener('click', function () { dlg.close(); });
      window.addEventListener('resize', function () { if (st) paint(); });
    }
  }

  /* The dialog title; the input's path keeps its letter case (dx_app's h2 is upper case). */
  function setTitle() {
    var el = $id('gc-zone-title-text');
    el.textContent = T('Draw on the frame');
    if (!st.frameUri) return;
    el.appendChild(document.createTextNode(' · '));
    var uri = document.createElement('span');
    uri.className = 'gc-zone-uri';
    uri.textContent = st.frameUri;
    el.appendChild(uri);
  }

  async function open(opts) {
    var c = opts.ctx, dlg = $id('gc-zone-dialog');
    st = { ctx: c, frameUri: opts.frameUri || null, frame: FRAME, img: null, targets: [], shapes: [], cur: 0, pt: 0,
      drag: false, drawing: false, idle: 0, frameError: '' };
    load({ nodeId: opts.nodeId, name: opts.param.name });
    setTitle();
    build();
    if (typeof openModal === 'function') openModal('gc-zone-dialog'); else dlg.showModal();
    renderSide();
    paint();
    els.canvas.focus();
    var mine = st;
    var r = st.frameUri ? await c.api.frame(st.frameUri) : { error_key: 'no_input' };
    if (st !== mine) return;
    if (r && r.image) {
      var img = new Image();
      img.onload = function () {
        if (st !== mine) return;
        st.img = img;
        st.frame = { width: r.width, height: r.height };
        renderSide();
        paint();
      };
      img.src = r.image;
    } else {
      st.frameError = r && r.error_key === 'live_source'
        ? T('A camera or RTSP source has no still frame here; shapes are drawn on an empty 16:9 frame.')
        : T('The input frame could not be read; shapes are drawn on an empty 16:9 frame.');
      /* Why it could not be read (too large to show, outside the input folders), translated by its error key. */
      var why = r && r.error_key && r.error_key !== 'live_source' && r.error_key !== 'no_input' && typeof translatedError === 'function'
        ? translatedError(r) : '';
      if (why) st.frameError += ' (' + why + ')';
      renderSide();
    }
  }

  /* The graph changed (an undo on the canvas, an edit elsewhere): redraw from it, unless this editor wrote it. */
  function refresh() {
    if (!st || st.committing || st.drag || st.drawing) return;
    load();
    if (!st.targets.length) { $id('gc-zone-dialog').close(); return; }
    renderSide();
    paint();
  }

  function isOpen() { var d = $id('gc-zone-dialog'); return !!st && !!d && d.open; }

  /* A small drawing of a polygon or line param for the inspector, on a 16:9 frame (`dir`: a line's direction). */
  function preview(canvasEl, param, value, dir) {
    var rect = canvasEl.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
    var w = rect.width || 240, hgt = rect.height || 135;
    canvasEl.width = Math.round(w * dpr);
    canvasEl.height = Math.round(hgt * dpr);
    var ctx = canvasEl.getContext('2d'), f = Z.fit(16, 9, w, hgt), s = Z.shapeFrom(value);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = cssVar('--surface-sunken');
    ctx.fillRect(0, 0, w, hgt);
    ctx.fillStyle = cssVar('--surface-panel');
    ctx.fillRect(f.ox, f.oy, f.w, f.h);
    ctx.strokeStyle = cssVar('--border-subtle');
    ctx.strokeRect(f.ox + 0.5, f.oy + 0.5, f.w - 1, f.h - 1);
    if (!s) return 0;
    ctx.strokeStyle = cssVar('--accent');
    ctx.fillStyle = cssVar('--accent');
    ctx.lineWidth = 2;
    ctx.beginPath();
    s.points.forEach(function (pt, i) { var q = Z.toScreen(f, pt); if (i) ctx.lineTo(q[0], q[1]); else ctx.moveTo(q[0], q[1]); });
    if (param.type === 'polygon') {
      ctx.closePath();
      ctx.globalAlpha = 0.2; ctx.fill(); ctx.globalAlpha = 1;
    }
    ctx.stroke();
    if (param.type === 'line' && s.points.length === 2) {
      drawArrow(ctx, Z.toScreen(f, s.points[0]), Z.toScreen(f, s.points[1]), cssVar('--accent'), dir);
    }
    return s.points.length;
  }

  if (typeof registerLangRefresher === 'function') {
    registerLangRefresher(function () {
      if (!st) return;
      setTitle();
      build();
      renderSide();
      paint();
    });
  }

  return { open: open, refresh: refresh, isOpen: isOpen, preview: preview, state: function () { return st; } };
})();
