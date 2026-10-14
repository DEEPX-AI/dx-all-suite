/* DX AI Studio — graph canvas (shared component).

   The look and mouse handling of dx_stream's Pipeline Builder (160x56 node cards with a category gradient and a left
   stripe, a sprite icon, 6 px ports, gradient bezier edges with arrowheads, a 20 px grid, a minimap, a context menu,
   touch) as a component any page can mount, plus what the Pipeline Builder lacks: keyboard control, an accessible
   canvas, edge labels, node badges and tints, marquee selection and auto layout.

     var cv = DXGraphCanvas.create(hostElement, {
       categories: { source: { slot: 1 }, model: { slot: 3 }, cpu: { slot: 2 } },   // colour = --cat-<slot>
       canConnect: function (fromNode, toNode, graph) { return { ok: true, kind: 'frame', label: '', data: {} }; },
       onChange: function (graph, info) {},   // after every committed change (info.reason)
       onSelect: function (selection) {},     // {nodes: [ids], edge: id or null}
       onActivate: function (item) {},       // Enter or double-click: {type: 'node' or 'edge', id}
       onDrop: function (payload, worldPoint) { return nodeSpec; },   // a palette item dropped on the canvas
       t: function (key) { return key; }     // translator; the keys are DXGraphCanvas.STRINGS
     });

   A node is {id, x, y, label, sub, category, icon, noInput, noOutput, ...}; an edge is {id, from, to, kind, label, ...}.
   Other fields ride along untouched. Colours come only from tokens (dx-tokens.css, dx-semantic.css) and are read on
   every paint, so a theme change repaints with the new ones. Needs dx-graph-core.js; draws icons with DXIcon.draw.
   Contract: tests/shared/test_graph_canvas_browser.py */
(function () {
  'use strict';
  var C = window.DXGraphCore;
  var W = C.NODE_W, H = C.NODE_H, PR = C.PORT_R;
  var DND_TYPE = 'application/x-dx-graph-node';

  /* Every string the canvas shows. The page passes its translator; the dx_app dictionary carries these keys
     (tests/dx_app/test_graph_composer_i18n.py). */
  var STRINGS = [
    'Graph canvas. Tab moves between nodes, arrow keys move the selection, Delete removes it, Ctrl+Z undoes.',
    'Graph canvas tools', 'Zoom in', 'Zoom out', 'Fit view', 'Auto layout', 'Undo', 'Redo', 'Minimap',
    'Delete', 'Copy', 'Paste', 'Duplicate', 'Select all',
    'Drag items from the palette, or select one and press Enter',
    'Selected {label}', '{n} nodes selected', 'Connected {from} to {to}', 'Cannot connect: {reason}',
    'This would create a cycle', 'These nodes are already connected', 'Deleted {n}'
  ];

  var _rootStyle = null;
  function css(name) {
    _rootStyle = _rootStyle || getComputedStyle(document.documentElement);
    return _rootStyle.getPropertyValue(name).trim();
  }

  /* 'r,g,b' of a colour token: its --name-rgb companion when there is one, else parsed from the token's value. */
  function rgbOf(name) {
    var direct = css(name + '-rgb');
    if (direct) return direct.replace(/\s+/g, '');
    var c = css(name), m = c.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i);
    if (m) {
      var h = m[1].length === 3 ? m[1].replace(/./g, function (x) { return x + x; }) : m[1];
      return parseInt(h.slice(0, 2), 16) + ',' + parseInt(h.slice(2, 4), 16) + ',' + parseInt(h.slice(4, 6), 16);
    }
    m = c.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/i);
    return m ? m[1] + ',' + m[2] + ',' + m[3] : '128,128,128';
  }

  function rgba(rgb, a) { return 'rgba(' + rgb + ',' + a + ')'; }

  function readTheme(cats) {
    var th = {
      page: css('--surface-page'), panel: css('--surface-panel'),
      text: css('--text-primary'), textRgb: rgbOf('--text-primary'), muted: css('--text-muted'),
      ok: css('--status-ok'), warn: css('--status-warn'), warnRgb: rgbOf('--status-warn'),
      error: css('--status-error'), info: css('--status-info'),
      accent: css('--accent'), accentRgb: rgbOf('--accent'),
      font: css('--font') || 'sans-serif', cats: {}
    };
    Object.keys(cats).forEach(function (k) {
      var slot = cats[k].slot || 6;
      th.cats[k] = { color: css('--cat-' + slot), rgb: rgbOf('--cat-' + slot) };
    });
    th.cats._ = { color: th.muted, rgb: rgbOf('--text-muted') };
    return th;
  }

  function el(tag, cls) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    return e;
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.arcTo(x + w, y, x + w, y + r, r);
    ctx.lineTo(x + w, y + h - r);
    ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
    ctx.lineTo(x + r, y + h);
    ctx.arcTo(x, y + h, x, y + h - r, r);
    ctx.lineTo(x, y + r);
    ctx.arcTo(x, y, x + r, y, r);
    ctx.closePath();
  }

  /* `s` cut with an ellipsis to fit `maxW` px in the current font. */
  function fit(ctx, s, maxW) {
    s = String(s == null ? '' : s);
    if (ctx.measureText(s).width <= maxW) return s;
    while (s.length > 1 && ctx.measureText(s + '…').width > maxW) s = s.slice(0, -1);
    return s + '…';
  }

  function create(host, options) {
    var o = options || {};
    var t = typeof o.t === 'function' ? o.t : function (k) { return k; };
    var cats = o.categories || {};
    var g = { nodes: [], edges: [] };
    var view = { zoom: 1, offsetX: 0, offsetY: 0 };
    var sel = { nodes: [], edge: null };
    var focusId = null, badges = {}, tints = {}, edgeStatus = {}, clip = null;
    var hist = C.createHistory(C.HISTORY_MAX);
    var mode = null, drag = null, pending = null, marquee = null, panStart = null, connectable = null;
    var raf = 0, destroyed = false, theme = null, dpr = 1, cssW = 1, cssH = 1, menu = null, longPress = 0;

    host.classList.add('dxg-host');
    var canvas = el('canvas', 'dxg-canvas');
    canvas.tabIndex = 0;
    canvas.setAttribute('role', 'application');
    var toolbar = buildToolbar();
    var mini = el('div', 'dxg-minimap');
    mini.setAttribute('role', 'img');
    var miniCanvas = el('canvas');
    mini.appendChild(miniCanvas);
    var tip = el('div', 'dxg-tip');
    var live = el('div', 'dxg-live');
    live.setAttribute('aria-live', 'polite');
    [canvas, toolbar, mini, tip, live].forEach(function (x) { host.appendChild(x); });

    function tbtn(icon, key, fn) {
      var b = el('button', 'dxg-tbtn');
      b.type = 'button';
      b.dataset.key = key;
      if (window.DXIcon && DXIcon.el) b.appendChild(DXIcon.el(icon));
      b.addEventListener('click', function () { fn(); canvas.focus(); });
      return b;
    }

    function buildToolbar() {
      var bar = el('div', 'dxg-toolbar');
      bar.setAttribute('role', 'toolbar');
      bar._zoom = el('span', 'dxg-zoom');
      bar._zoom.setAttribute('aria-hidden', 'true');
      bar.appendChild(tbtn('minus', 'Zoom out', function () { zoomBy(1 / 1.2); }));
      bar.appendChild(bar._zoom);
      bar.appendChild(tbtn('plus', 'Zoom in', function () { zoomBy(1.2); }));
      bar.appendChild(el('span', 'dxg-sep'));
      bar.appendChild(tbtn('fit', 'Fit view', function () { fitView(); }));
      bar.appendChild(tbtn('graph', 'Auto layout', function () { autoLayout(); }));
      bar.appendChild(el('span', 'dxg-sep'));
      bar._undo = tbtn('undo', 'Undo', function () { undo(); });
      bar._redo = tbtn('redo', 'Redo', function () { redo(); });
      bar.appendChild(bar._undo);
      bar.appendChild(bar._redo);
      return bar;
    }

    function refreshLanguage() {
      canvas.setAttribute('aria-label', t(STRINGS[0]));
      toolbar.setAttribute('aria-label', t('Graph canvas tools'));
      mini.setAttribute('aria-label', t('Minimap'));
      Array.prototype.forEach.call(toolbar.querySelectorAll('.dxg-tbtn'), function (b) {
        b.setAttribute('aria-label', t(b.dataset.key));
        b.title = t(b.dataset.key);
      });
      paint();
    }

    function announce(msg) { live.textContent = msg; }
    function emitSelect() { if (typeof o.onSelect === 'function') o.onSelect(selection()); }
    function selection() { return { nodes: sel.nodes.slice(), edge: sel.edge }; }
    function getGraph() { return C.clone(g); }
    function snapshot() { return JSON.stringify(g); }

    function commit(reason) {
      hist.push(snapshot());
      paint();
      if (typeof o.onChange === 'function') o.onChange(getGraph(), { reason: reason });
    }

    function restore(s) {
      g = JSON.parse(s);
      var ids = C.nodeMap(g.nodes);
      sel = {
        nodes: sel.nodes.filter(function (id) { return ids[id]; }),
        edge: g.edges.some(function (e) { return e.id === sel.edge; }) ? sel.edge : null
      };
      if (focusId && !ids[focusId]) focusId = null;
      paint();
      emitSelect();
      if (typeof o.onChange === 'function') o.onChange(getGraph(), { reason: 'history' });
    }

    function undo() { var s = hist.undo(); if (s !== null) restore(s); }
    function redo() { var s = hist.redo(); if (s !== null) restore(s); }

    function setGraph(graph, opts) {
      var src = graph || { nodes: [], edges: [] };
      g = { nodes: C.clone(src.nodes || []), edges: C.clone(src.edges || []) };
      g.edges.forEach(function (e) { e.id = e.id || C.edgeId(e.from, e.to); });
      sel = { nodes: [], edge: null };
      focusId = null;
      hist.reset(snapshot());
      if (!opts || opts.fit !== false) fitView(); else paint();
      emitSelect();
    }

    function addNode(spec, at) {
      var p = at || C.screenToWorld(view, cssW / 2, cssH / 2);
      var n = C.clone(spec || {});
      n.id = C.uniqueId(n.id || n.label || 'node', g.nodes.map(function (x) { return x.id; }));
      n.x = C.snap(p.x - W / 2);
      n.y = C.snap(p.y - H / 2);
      while (g.nodes.some(function (m) { return m.x === n.x && m.y === n.y; })) { n.x += 2 * C.GRID; n.y += 2 * C.GRID; }
      g.nodes.push(n);
      sel = { nodes: [n.id], edge: null };
      focusId = n.id;
      commit('add');
      emitSelect();
      announceSelection();
      return n.id;
    }

    function updateNode(id, patch, opts) {
      var n = C.nodeMap(g.nodes)[id];
      if (!n) return false;
      Object.keys(patch || {}).forEach(function (k) { if (k !== 'id') n[k] = C.clone(patch[k]); });
      if (opts && opts.commit === false) paint(); else commit('edit');
      return true;
    }

    function updateEdge(id, patch, opts) {
      var e = null;
      g.edges.forEach(function (x) { if (x.id === id) e = x; });
      if (!e) return false;
      Object.keys(patch || {}).forEach(function (k) { if (k !== 'id' && k !== 'from' && k !== 'to') e[k] = C.clone(patch[k]); });
      if (opts && opts.commit === false) paint(); else commit('edit');
      return true;
    }

    function renameNode(oldId, newId) {
      if (!C.ID_RE.test(newId) || C.nodeMap(g.nodes)[newId] || !C.nodeMap(g.nodes)[oldId]) return false;
      g = C.renameNode(g, oldId, newId);
      sel.nodes = sel.nodes.map(function (id) { return id === oldId ? newId : id; });
      if (focusId === oldId) focusId = newId;
      var n = C.nodeMap(g.nodes)[newId];
      if (n.label === oldId) n.label = newId;
      commit('rename');
      emitSelect();
      return true;
    }

    function check(from, to) {
      if (!from || !to || from.id === to.id) return { ok: false, reason: '' };
      if (C.hasEdge(g.edges, from.id, to.id)) return { ok: false, reason: t('These nodes are already connected') };
      if (C.wouldCycle(g.edges, from.id, to.id)) return { ok: false, reason: t('This would create a cycle') };
      var r = typeof o.canConnect === 'function' ? o.canConnect(C.clone(from), C.clone(to), getGraph()) : { ok: true };
      return r || { ok: false, reason: '' };
    }

    function connect(fromId, toId) {
      var map = C.nodeMap(g.nodes), r = check(map[fromId], map[toId]);
      if (!r.ok) {
        if (r.reason) announce(t('Cannot connect: {reason}').replace('{reason}', r.reason));
        return r;
      }
      var id = C.edgeId(fromId, toId);
      g.edges.push({ id: id, from: fromId, to: toId, kind: r.kind || '', label: r.label || '', data: C.clone(r.data || {}) });
      sel = { nodes: [], edge: id };
      commit('connect');
      emitSelect();
      announce(t('Connected {from} to {to}').replace('{from}', fromId).replace('{to}', toId));
      return r;
    }

    function removeSelection() {
      var n = 0;
      if (sel.nodes.length) {
        n = sel.nodes.length;
        g = C.removeNodes(g, sel.nodes);
        focusId = null;
      } else if (sel.edge) {
        n = 1;
        g.edges = g.edges.filter(function (e) { return e.id !== sel.edge; });
      } else return;
      sel = { nodes: [], edge: null };
      commit('delete');
      emitSelect();
      announce(t('Deleted {n}').replace('{n}', n));
    }

    function copy() { if (sel.nodes.length) clip = C.copySelection(g, sel.nodes); }

    function paste() {
      if (!clip || !clip.nodes.length) return;
      var r = C.pasteClip(g, clip, 2 * C.GRID);
      g = r.graph;
      sel = { nodes: r.ids, edge: null };
      focusId = r.ids[0];
      clip = C.copySelection(g, r.ids);
      commit('paste');
      emitSelect();
      announceSelection();
    }

    function duplicate() { copy(); paste(); }

    function selectAll() {
      sel = { nodes: g.nodes.map(function (n) { return n.id; }), edge: null };
      paint();
      emitSelect();
      announceSelection();
    }

    function select(s) {
      var ids = C.nodeMap(g.nodes);
      sel = {
        nodes: ((s && s.nodes) || []).filter(function (id) { return ids[id]; }),
        edge: s && s.edge && g.edges.some(function (e) { return e.id === s.edge; }) ? s.edge : null
      };
      if (sel.nodes.length) { focusId = sel.nodes[0]; ensureVisible(focusId); }
      paint();
      emitSelect();
    }

    function announceSelection() {
      if (sel.nodes.length === 1) {
        var n = C.nodeMap(g.nodes)[sel.nodes[0]];
        announce(t('Selected {label}').replace('{label}', (n.label || n.id) + (n.sub ? ', ' + n.sub : '')));
      } else if (sel.nodes.length > 1) {
        announce(t('{n} nodes selected').replace('{n}', sel.nodes.length));
      }
    }

    function ensureVisible(id) {
      var n = C.nodeMap(g.nodes)[id];
      if (!n) return;
      var a = C.worldToScreen(view, n.x, n.y), b = C.worldToScreen(view, n.x + W, n.y + H), pad = 24;
      if (a.x < pad) view.offsetX += pad - a.x;
      if (b.x > cssW - pad) view.offsetX -= b.x - (cssW - pad);
      if (a.y < pad) view.offsetY += pad - a.y;
      if (b.y > cssH - pad) view.offsetY -= b.y - (cssH - pad);
    }

    function fitView() { view = C.fitTransform(g.nodes, cssW, cssH, 60); paint(); }
    function zoomBy(f) { view = C.zoomAt(view, f, cssW / 2, cssH / 2); paint(); }
    function autoLayout() { if (!g.nodes.length) return; g = C.autoLayout(g); commit('layout'); fitView(); }

    function nodeRect(id) {
      var n = C.nodeMap(g.nodes)[id];
      if (!n) return null;
      var r = canvas.getBoundingClientRect(), a = C.worldToScreen(view, n.x, n.y);
      return { left: r.left + a.x, top: r.top + a.y, width: W * view.zoom, height: H * view.zoom };
    }

    /* ── painting ─────────────────────────────────────────────── */

    function resize() {
      var r = host.getBoundingClientRect();
      cssW = Math.max(1, Math.round(r.width));
      cssH = Math.max(1, Math.round(r.height));
      dpr = window.devicePixelRatio || 1;
      canvas.width = Math.round(cssW * dpr);
      canvas.height = Math.round(cssH * dpr);
      paintNow();
    }

    function paint() {
      if (raf || destroyed) return;
      raf = requestAnimationFrame(function () { raf = 0; paintNow(); });
    }

    function catOf(n) { return theme.cats[n.category] || theme.cats._; }

    function paintNow() {
      if (destroyed) return;
      theme = readTheme(cats);
      var ctx = canvas.getContext('2d');
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.fillStyle = theme.page;
      ctx.fillRect(0, 0, cssW, cssH);
      drawGrid(ctx);
      if (!g.nodes.length) {
        ctx.fillStyle = rgba(theme.textRgb, 0.55);
        ctx.font = '13px ' + theme.font;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(t('Drag items from the palette, or select one and press Enter'), cssW / 2, cssH / 2);
      }
      ctx.save();
      ctx.translate(view.offsetX, view.offsetY);
      ctx.scale(view.zoom, view.zoom);
      var map = C.nodeMap(g.nodes);
      g.edges.forEach(function (e) { drawEdge(ctx, map, e); });
      if (mode === 'edge' && pending) drawPending(ctx, map);
      g.nodes.forEach(function (n) { drawNode(ctx, n); });
      if (mode === 'marquee' && marquee) drawMarquee(ctx);
      ctx.restore();
      drawMinimap();
      toolbar._zoom.textContent = Math.round(view.zoom * 100) + '%';
      toolbar._undo.disabled = !hist.canUndo();
      toolbar._redo.disabled = !hist.canRedo();
    }

    function drawGrid(ctx) {
      var step = C.GRID * view.zoom;
      if (step < 6) return;
      ctx.strokeStyle = rgba(theme.textRgb, 0.06);
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (var x = ((view.offsetX % step) + step) % step; x < cssW; x += step) { ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, cssH); }
      for (var y = ((view.offsetY % step) + step) % step; y < cssH; y += step) { ctx.moveTo(0, y + 0.5); ctx.lineTo(cssW, y + 0.5); }
      ctx.stroke();
    }

    function connectStatus(n) {
      if (mode !== 'edge' || !connectable || !pending || n.id === pending.from) return null;
      var r = connectable[n.id];
      return r && r.ok ? 'allow' : 'block';
    }

    function port(ctx, px, py, c) {
      ctx.beginPath();
      ctx.arc(px, py, PR + 1, 0, Math.PI * 2);
      ctx.fillStyle = rgba(c.rgb, 0.15);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(px, py, PR, 0, Math.PI * 2);
      ctx.fillStyle = theme.page;
      ctx.fill();
      ctx.strokeStyle = c.color;
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    function drawNode(ctx, n) {
      var c = catOf(n), x = n.x, y = n.y, selected = sel.nodes.indexOf(n.id) !== -1, status = connectStatus(n);
      ctx.save();
      if (status === 'block') ctx.globalAlpha = 0.3;
      ctx.save();
      ctx.shadowColor = status === 'allow' ? theme.ok : rgba(c.rgb, 0.25);
      ctx.shadowBlur = status === 'allow' || selected ? 16 : 10;
      ctx.shadowOffsetY = status ? 0 : 4;
      roundRect(ctx, x, y, W, H, 10);
      ctx.fillStyle = theme.page;
      ctx.fill();
      ctx.restore();
      var body = ctx.createLinearGradient(x, y, x + W, y + H);
      body.addColorStop(0, rgba(c.rgb, selected ? 0.20 : 0.10));
      body.addColorStop(1, rgba(c.rgb, selected ? 0.08 : 0.03));
      roundRect(ctx, x, y, W, H, 10);
      ctx.fillStyle = body;
      ctx.fill();
      if (tints[n.id] > 0) {
        roundRect(ctx, x, y, W, H, 10);
        ctx.fillStyle = rgba(theme.warnRgb, 0.08 + 0.32 * Math.min(1, tints[n.id]));
        ctx.fill();
      }
      ctx.strokeStyle = selected ? theme.text : rgba(c.rgb, 0.6);
      ctx.lineWidth = selected ? 2 : 1;
      roundRect(ctx, x, y, W, H, 10);
      ctx.stroke();
      if ((badges[n.id] || []).some(function (b) { return b.kind === 'error'; })) {
        ctx.strokeStyle = theme.error;
        ctx.lineWidth = 2;
        roundRect(ctx, x - 2, y - 2, W + 4, H + 4, 12);
        ctx.stroke();
      }
      ctx.save();
      ctx.shadowColor = rgba(c.rgb, 0.5);
      ctx.shadowBlur = 6;
      ctx.fillStyle = c.color;
      ctx.beginPath();
      ctx.moveTo(x + 10, y);
      ctx.lineTo(x + 5, y);
      ctx.arcTo(x, y, x, y + 10, 10);
      ctx.lineTo(x, y + H - 10);
      ctx.arcTo(x, y + H, x + 10, y + H, 10);
      ctx.lineTo(x + 5, y + H);
      ctx.lineTo(x + 5, y);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
      if (window.DXIcon && DXIcon.draw) DXIcon.draw(ctx, n.icon || 'circle', x + 11, y + H / 2 - 7, 14, c.color);
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = theme.text;
      ctx.font = '600 11px ' + theme.font;
      ctx.fillText(fit(ctx, n.label || n.id, W - 40), x + 31, y + H / 2 - 8);
      ctx.fillStyle = rgba(c.rgb, 0.9);
      ctx.font = '10px ' + theme.font;
      ctx.fillText(fit(ctx, n.sub || '', W - 40), x + 31, y + H / 2 + 8);
      if (!n.noInput && status !== 'block') port(ctx, x, y + H / 2, c);
      if (!n.noOutput) port(ctx, x + W, y + H / 2, c);
      if (focusId === n.id && document.activeElement === canvas) {
        ctx.setLineDash([4, 3]);
        ctx.strokeStyle = theme.accent;
        ctx.lineWidth = 2;
        roundRect(ctx, x - 6, y - 6, W + 12, H + 12, 14);
        ctx.stroke();
        ctx.setLineDash([]);
      }
      if (status === 'block') {
        ctx.globalAlpha = 1;
        if (window.DXIcon && DXIcon.draw) DXIcon.draw(ctx, 'x', x + W / 2 - 10, y + H / 2 - 10, 20, theme.error);
      }
      drawBadges(ctx, n);
      ctx.restore();
    }

    /* Badges sit on the node's top edge, right-aligned: error, missing (not installed), mem (MB), ms (time). */
    function drawBadges(ctx, n) {
      var list = badges[n.id];
      if (!list || !list.length) return;
      ctx.font = '600 9px ' + theme.font;
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      var right = n.x + W - 8;
      for (var i = list.length - 1; i >= 0; i--) {
        var b = list[i], w = ctx.measureText(b.text).width + 12, bx = right - w, by = n.y - 8;
        var color = b.kind === 'error' ? theme.error : b.kind === 'missing' ? theme.warn : b.kind === 'ms' ? theme.info : theme.muted;
        roundRect(ctx, bx, by, w, 16, 8);
        ctx.fillStyle = theme.panel;
        ctx.fill();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.fillStyle = color;
        ctx.fillText(b.text, bx + 6, by + 8);
        right = bx - 4;
      }
    }

    function curve(ctx, x1, y1, x2, y2) {
      var c = C.controlOffset(x1, x2);
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.bezierCurveTo(x1 + c, y1, x2 - c, y2, x2, y2);
    }

    function arrow(ctx, x, y, color) {
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x - 8, y - 4);
      ctx.lineTo(x - 8, y + 4);
      ctx.closePath();
      ctx.fillStyle = color;
      ctx.fill();
    }

    function drawEdgeLabel(ctx, p, text, color) {
      ctx.font = '10px ' + theme.font;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      var s = fit(ctx, text, 140), w = ctx.measureText(s).width + 12;
      roundRect(ctx, p.x - w / 2, p.y - 9, w, 18, 9);
      ctx.fillStyle = theme.panel;
      ctx.fill();
      ctx.strokeStyle = rgba(theme.textRgb, 0.2);
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.fillStyle = color;
      ctx.fillText(s, p.x, p.y);
    }

    function drawEdge(ctx, map, e) {
      var f = map[e.from], to = map[e.to];
      if (!f || !to) return;
      var a = C.outPort(f), b = C.inPort(to), cf = catOf(f), ct = catOf(to);
      var selected = sel.edge === e.id, bad = edgeStatus[e.id] === 'error';
      curve(ctx, a.x, a.y, b.x, b.y);
      if (selected) ctx.strokeStyle = theme.accent;
      else if (bad) ctx.strokeStyle = theme.error;
      else {
        var gr = ctx.createLinearGradient(a.x, a.y, b.x, b.y);
        gr.addColorStop(0, cf.color);
        gr.addColorStop(1, ct.color);
        ctx.strokeStyle = gr;
      }
      ctx.lineWidth = selected ? 3 : 2;
      ctx.setLineDash(bad ? [8, 4] : e.kind === 'roi' ? [6, 3] : []);
      ctx.stroke();
      ctx.setLineDash([]);
      arrow(ctx, b.x, b.y, selected ? theme.accent : bad ? theme.error : ct.color);
      var mid = C.bezierPoint(a.x, a.y, b.x, b.y, 0.5);
      if (e.label) drawEdgeLabel(ctx, mid, e.label, bad ? theme.error : theme.muted);
      if (bad && window.DXIcon && DXIcon.draw) DXIcon.draw(ctx, 'alert', mid.x - 8, mid.y - (e.label ? 30 : 18), 16, theme.error);
    }

    function drawPending(ctx, map) {
      var f = map[pending.from];
      if (!f) return;
      var a = C.outPort(f);
      curve(ctx, a.x, a.y, pending.x, pending.y);
      ctx.strokeStyle = rgba(theme.textRgb, 0.35);
      ctx.lineWidth = 2;
      ctx.setLineDash([6, 4]);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    function drawMarquee(ctx) {
      var x = Math.min(marquee.x1, marquee.x2), y = Math.min(marquee.y1, marquee.y2);
      var w = Math.abs(marquee.x2 - marquee.x1), h = Math.abs(marquee.y2 - marquee.y1);
      ctx.fillStyle = rgba(theme.accentRgb, 0.08);
      ctx.fillRect(x, y, w, h);
      ctx.strokeStyle = theme.accent;
      ctx.lineWidth = 1 / view.zoom;
      ctx.strokeRect(x, y, w, h);
    }

    function drawMinimap() {
      if (!g.nodes.length) { mini.style.display = 'none'; mini._map = null; return; }
      mini.style.display = '';
      var mw = mini.clientWidth || 160, mh = mini.clientHeight || 120;
      if (miniCanvas.width !== Math.round(mw * dpr)) { miniCanvas.width = Math.round(mw * dpr); miniCanvas.height = Math.round(mh * dpr); }
      var m = miniCanvas.getContext('2d');
      m.setTransform(dpr, 0, 0, dpr, 0, 0);
      var b = C.bounds(g.nodes), pad = 40;
      var bw = b.maxX - b.minX + pad * 2, bh = b.maxY - b.minY + pad * 2, s = Math.min(mw / bw, mh / bh);
      var ox = b.minX - pad, oy = b.minY - pad;
      mini._map = { ox: ox, oy: oy, s: s };
      m.fillStyle = theme.panel;
      m.fillRect(0, 0, mw, mh);
      var map = C.nodeMap(g.nodes);
      m.strokeStyle = rgba(theme.textRgb, 0.25);
      m.lineWidth = 1;
      g.edges.forEach(function (e) {
        var f = map[e.from], to = map[e.to];
        if (!f || !to) return;
        m.beginPath();
        m.moveTo((f.x + W - ox) * s, (f.y + H / 2 - oy) * s);
        m.lineTo((to.x - ox) * s, (to.y + H / 2 - oy) * s);
        m.stroke();
      });
      g.nodes.forEach(function (n) {
        m.globalAlpha = 0.75;
        m.fillStyle = catOf(n).color;
        m.fillRect((n.x - ox) * s, (n.y - oy) * s, W * s, H * s);
        m.globalAlpha = 1;
      });
      var tl = C.screenToWorld(view, 0, 0);
      m.strokeStyle = theme.accent;
      m.lineWidth = 1.5;
      m.strokeRect((tl.x - ox) * s, (tl.y - oy) * s, cssW / view.zoom * s, cssH / view.zoom * s);
    }

    /* ── input ────────────────────────────────────────────────── */

    function local(e) {
      var r = canvas.getBoundingClientRect();
      return { x: e.clientX - r.left, y: e.clientY - r.top };
    }

    function world(e) { var p = local(e); return C.screenToWorld(view, p.x, p.y); }

    function showTip(p, text) {
      tip.textContent = text;
      tip.style.left = (p.x + 12) + 'px';
      tip.style.top = (p.y - 30) + 'px';
      tip.classList.add('is-on');
    }

    function hideTip() { tip.classList.remove('is-on'); }

    function startPan(e) {
      mode = 'pan';
      panStart = { x: e.clientX, y: e.clientY, ox: view.offsetX, oy: view.offsetY };
      canvas.style.cursor = 'grabbing';
    }

    function onDown(e) {
      hideMenu();
      canvas.focus();
      if (e.button === 1 || e.button === 2) { startPan(e); return; }
      var w = world(e);
      var outN = C.hitPort(g.nodes, w.x, w.y, 'out');
      if (outN) {
        mode = 'edge';
        pending = { from: outN.id, x: w.x, y: w.y };
        connectable = {};
        g.nodes.forEach(function (n) { if (n.id !== outN.id) connectable[n.id] = check(outN, n); });
        paint();
        return;
      }
      var n = C.hitNode(g.nodes, w.x, w.y);
      if (n) {
        if (e.shiftKey || e.ctrlKey || e.metaKey) {
          var i = sel.nodes.indexOf(n.id);
          if (i === -1) sel.nodes.push(n.id); else sel.nodes.splice(i, 1);
        } else if (sel.nodes.indexOf(n.id) === -1) sel.nodes = [n.id];
        sel.edge = null;
        focusId = n.id;
        var map = C.nodeMap(g.nodes);
        mode = 'drag';
        drag = { x: w.x, y: w.y, moved: false, orig: sel.nodes.map(function (id) { return { id: id, x: map[id].x, y: map[id].y }; }) };
        emitSelect();
        announceSelection();
        paint();
        return;
      }
      var ed = C.hitEdge(g.nodes, g.edges, w.x, w.y);
      if (ed) { sel = { nodes: [], edge: ed.id }; emitSelect(); paint(); return; }
      if (e.shiftKey) { mode = 'marquee'; marquee = { x1: w.x, y1: w.y, x2: w.x, y2: w.y }; return; }
      if (sel.nodes.length || sel.edge) { sel = { nodes: [], edge: null }; emitSelect(); paint(); }
      startPan(e);
    }

    function onMove(e) {
      if (mode === 'pan') {
        view.offsetX = panStart.ox + e.clientX - panStart.x;
        view.offsetY = panStart.oy + e.clientY - panStart.y;
        paint();
        return;
      }
      if (!mode && e.target !== canvas) return;
      var w = world(e);
      if (mode === 'drag') {
        var dx = w.x - drag.x, dy = w.y - drag.y, map = C.nodeMap(g.nodes);
        if (Math.abs(dx) + Math.abs(dy) > 2) drag.moved = true;
        drag.orig.forEach(function (p) { var m = map[p.id]; if (m) { m.x = p.x + dx; m.y = p.y + dy; } });
        paint();
        return;
      }
      if (mode === 'edge') {
        pending.x = w.x;
        pending.y = w.y;
        var over = C.hitNode(g.nodes, w.x, w.y), r = over && connectable[over.id];
        if (r && !r.ok && r.reason) showTip(local(e), r.reason); else hideTip();
        paint();
        return;
      }
      if (mode === 'marquee') { marquee.x2 = w.x; marquee.y2 = w.y; paint(); return; }
      canvas.style.cursor = C.hitPort(g.nodes, w.x, w.y, 'out') || C.hitPort(g.nodes, w.x, w.y, 'in') ? 'crosshair'
        : C.hitNode(g.nodes, w.x, w.y) ? 'grab' : C.hitEdge(g.nodes, g.edges, w.x, w.y) ? 'pointer' : 'default';
    }

    function onUp(e) {
      var m = mode;
      if (!m) return;
      mode = null;
      canvas.style.cursor = 'default';
      if (m === 'drag') {
        if (drag.moved) {
          var map = C.nodeMap(g.nodes);
          drag.orig.forEach(function (p) { var n = map[p.id]; if (n) { n.x = C.snap(n.x); n.y = C.snap(n.y); } });
          commit('move');
        }
        drag = null;
        paint();
        return;
      }
      if (m === 'edge') {
        var w = world(e), target = C.hitPort(g.nodes, w.x, w.y, 'in') || C.hitNode(g.nodes, w.x, w.y);
        var from = pending.from;
        pending = null;
        connectable = null;
        hideTip();
        if (target && target.id !== from) connect(from, target.id); else paint();
        return;
      }
      if (m === 'marquee') {
        sel = { nodes: C.nodesInRect(g.nodes, marquee), edge: null };
        marquee = null;
        if (sel.nodes.length) focusId = sel.nodes[0];
        emitSelect();
        announceSelection();
        paint();
      }
    }

    function onDblClick(e) {
      if (typeof o.onActivate !== 'function') return;
      var w = world(e), n = C.hitNode(g.nodes, w.x, w.y);
      if (n) { o.onActivate({ type: 'node', id: n.id }); return; }
      var ed = C.hitEdge(g.nodes, g.edges, w.x, w.y);
      if (ed) o.onActivate({ type: 'edge', id: ed.id });
    }

    function onWheel(e) {
      e.preventDefault();
      var p = local(e);
      view = C.zoomAt(view, e.deltaY > 0 ? 1 / 1.1 : 1.1, p.x, p.y);
      paint();
    }

    function focusNode(id) {
      focusId = id;
      sel = { nodes: [id], edge: null };
      ensureVisible(id);
      emitSelect();
      announceSelection();
      paint();
    }

    function moveSelection(dx, dy) {
      var map = C.nodeMap(g.nodes);
      sel.nodes.forEach(function (id) { var n = map[id]; n.x += dx * C.GRID; n.y += dy * C.GRID; });
      commit('move');
    }

    function onKey(e) {
      var mod = e.ctrlKey || e.metaKey, k = e.key;
      if (k === 'Tab') {
        var next = C.nextInOrder(g.nodes, focusId, e.shiftKey ? -1 : 1);
        if (next === null) return;   // let focus leave the canvas
        e.preventDefault();
        focusNode(next);
        return;
      }
      if (mod) {
        var lk = k.toLowerCase(), act = { z: e.shiftKey ? redo : undo, y: redo, c: copy, v: paste, a: selectAll, d: duplicate }[lk];
        if (act) { e.preventDefault(); act(); }
        return;
      }
      if (k === 'Delete' || k === 'Backspace') { e.preventDefault(); removeSelection(); return; }
      if (k === 'Escape') {
        if (mode === 'edge') { mode = null; pending = null; connectable = null; hideTip(); }
        sel = { nodes: [], edge: null };
        emitSelect();
        paint();
        return;
      }
      if (k === 'Enter') {
        if (focusId && typeof o.onActivate === 'function') { e.preventDefault(); o.onActivate({ type: 'node', id: focusId }); }
        return;
      }
      if (k === 'ContextMenu' || (e.shiftKey && k === 'F10')) {
        e.preventDefault();
        var fn = focusId && C.nodeMap(g.nodes)[focusId], r = canvas.getBoundingClientRect();
        var p = fn ? C.worldToScreen(view, fn.x + W / 2, fn.y + H / 2) : { x: cssW / 2, y: cssH / 2 };
        showMenu(r.left + p.x, r.top + p.y, fn ? { x: fn.x + 1, y: fn.y + 1 } : C.screenToWorld(view, p.x, p.y));
        return;
      }
      if (k === '+' || k === '=') { e.preventDefault(); zoomBy(1.2); return; }
      if (k === '-') { e.preventDefault(); zoomBy(1 / 1.2); return; }
      if (k === '0') { e.preventDefault(); fitView(); return; }
      var d = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[k];
      if (!d) return;
      e.preventDefault();
      if (sel.nodes.length) moveSelection(d[0], d[1]);
      else { view.offsetX -= d[0] * 40; view.offsetY -= d[1] * 40; paint(); }
    }

    /* ── context menu ─────────────────────────────────────────── */

    function showMenu(cx, cy, w) {
      hideMenu();
      var n = C.hitNode(g.nodes, w.x, w.y), ed = n ? null : C.hitEdge(g.nodes, g.edges, w.x, w.y);
      if (n && sel.nodes.indexOf(n.id) === -1) { sel = { nodes: [n.id], edge: null }; focusId = n.id; emitSelect(); }
      if (ed) { sel = { nodes: [], edge: ed.id }; emitSelect(); }
      paint();
      menu = el('div', 'dxg-menu');
      menu.setAttribute('role', 'menu');
      function item(key, keys, fn, disabled) {
        var b = el('button');
        b.type = 'button';
        b.setAttribute('role', 'menuitem');
        var s = el('span');
        s.textContent = t(key);
        b.appendChild(s);
        if (keys) { var kk = el('span', 'dxg-key'); kk.textContent = keys; b.appendChild(kk); }
        b.disabled = !!disabled;
        b.addEventListener('click', function () { hideMenu(); fn(); canvas.focus(); });
        menu.appendChild(b);
      }
      if (n || ed) {
        item('Delete', 'Del', removeSelection);
        if (n) { item('Copy', 'Ctrl+C', copy); item('Duplicate', 'Ctrl+D', duplicate); }
      } else {
        item('Paste', 'Ctrl+V', paste, !clip);
        item('Select all', 'Ctrl+A', selectAll, !g.nodes.length);
        menu.appendChild(el('hr'));
        item('Undo', 'Ctrl+Z', undo, !hist.canUndo());
        item('Redo', 'Ctrl+Y', redo, !hist.canRedo());
        menu.appendChild(el('hr'));
        item('Fit view', '0', fitView);
        item('Auto layout', '', autoLayout, !g.nodes.length);
      }
      menu.style.left = cx + 'px';
      menu.style.top = cy + 'px';
      document.body.appendChild(menu);
      var r = menu.getBoundingClientRect();
      if (r.right > window.innerWidth) menu.style.left = Math.max(0, cx - r.width) + 'px';
      if (r.bottom > window.innerHeight) menu.style.top = Math.max(0, cy - r.height) + 'px';
      menu.addEventListener('keydown', menuKeys);
      var first = menu.querySelector('button:not([disabled])');
      if (first) first.focus();
      setTimeout(function () { document.addEventListener('mousedown', outside, true); }, 0);
    }

    function outside(e) { if (menu && !menu.contains(e.target)) hideMenu(); }

    function hideMenu() {
      if (!menu) return;
      menu.remove();
      menu = null;
      document.removeEventListener('mousedown', outside, true);
    }

    function menuKeys(e) {
      var items = Array.prototype.slice.call(menu.querySelectorAll('button:not([disabled])'));
      var i = items.indexOf(document.activeElement);
      if (e.key === 'Escape') { e.preventDefault(); hideMenu(); canvas.focus(); }
      else if (e.key === 'ArrowDown' && items.length) { e.preventDefault(); items[(i + 1) % items.length].focus(); }
      else if (e.key === 'ArrowUp' && items.length) { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); }
    }

    /* ── touch, drop, minimap ─────────────────────────────────── */

    function touchToMouse(type, e) {
      if (e.touches.length > 1) return;
      var tch = e.touches[0] || e.changedTouches[0];
      canvas.dispatchEvent(new MouseEvent(type, { clientX: tch.clientX, clientY: tch.clientY, button: 0, bubbles: true }));
      e.preventDefault();
    }

    function onTouchStart(e) {
      touchToMouse('mousedown', e);
      var tch = e.touches[0];
      clearTimeout(longPress);
      longPress = setTimeout(function () {
        if (drag && drag.moved) return;
        mode = null;
        var r = canvas.getBoundingClientRect();
        showMenu(tch.clientX, tch.clientY, C.screenToWorld(view, tch.clientX - r.left, tch.clientY - r.top));
      }, 600);
    }

    function onTouchMove(e) { clearTimeout(longPress); touchToMouse('mousemove', e); }
    function onTouchEnd(e) { clearTimeout(longPress); touchToMouse('mouseup', e); }

    function hasDnd(e) { return Array.prototype.indexOf.call((e.dataTransfer && e.dataTransfer.types) || [], DND_TYPE) !== -1; }

    function onDragOver(e) {
      if (!hasDnd(e)) return;
      e.preventDefault();
      e.dataTransfer.dropEffect = 'copy';
      host.classList.add('is-drop');
    }

    function onDragLeave(e) { if (!host.contains(e.relatedTarget)) host.classList.remove('is-drop'); }

    function onDrop(e) {
      host.classList.remove('is-drop');
      var raw = e.dataTransfer && e.dataTransfer.getData(DND_TYPE);
      if (!raw) return;
      e.preventDefault();
      var payload;
      try { payload = JSON.parse(raw); } catch (err) { return; }
      var w = world(e), spec = typeof o.onDrop === 'function' ? o.onDrop(payload, w) : payload;
      if (spec) addNode(spec, w);
    }

    function onMiniDown(e) {
      e.preventDefault();
      e.stopPropagation();
      if (!mini._map) return;
      var r = mini.getBoundingClientRect(), mm = mini._map;
      var wx = (e.clientX - r.left) / mm.s + mm.ox, wy = (e.clientY - r.top) / mm.s + mm.oy;
      view.offsetX = cssW / 2 - wx * view.zoom;
      view.offsetY = cssH / 2 - wy * view.zoom;
      paint();
    }

    function onTheme() { requestAnimationFrame(function () { paint(); }); }

    canvas.addEventListener('mousedown', onDown);
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    canvas.addEventListener('dblclick', onDblClick);
    canvas.addEventListener('wheel', onWheel, { passive: false });
    canvas.addEventListener('contextmenu', function (e) { e.preventDefault(); showMenu(e.clientX, e.clientY, world(e)); });
    canvas.addEventListener('keydown', onKey);
    canvas.addEventListener('focus', paint);
    canvas.addEventListener('blur', paint);
    canvas.addEventListener('touchstart', onTouchStart, { passive: false });
    canvas.addEventListener('touchmove', onTouchMove, { passive: false });
    canvas.addEventListener('touchend', onTouchEnd, { passive: false });
    host.addEventListener('dragover', onDragOver);
    host.addEventListener('dragleave', onDragLeave);
    host.addEventListener('drop', onDrop);
    mini.addEventListener('mousedown', onMiniDown);
    window.addEventListener('dx-icons-ready', paint);
    if (window.DXTheme && typeof DXTheme.onThemeChange === 'function') DXTheme.onThemeChange(onTheme);
    var ro = typeof ResizeObserver === 'function' ? new ResizeObserver(function () { resize(); }) : null;
    if (ro) ro.observe(host); else window.addEventListener('resize', resize);

    function destroy() {
      destroyed = true;
      hideMenu();
      if (ro) ro.disconnect(); else window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
      window.removeEventListener('dx-icons-ready', paint);
      [canvas, toolbar, mini, tip, live].forEach(function (x) { x.remove(); });
      host.classList.remove('dxg-host', 'is-drop');
    }

    refreshLanguage();
    resize();

    return {
      setGraph: setGraph, getGraph: getGraph, addNode: addNode, updateNode: updateNode, updateEdge: updateEdge,
      renameNode: renameNode, connect: connect, remove: removeSelection, select: select, selection: selection,
      selectAll: selectAll, copy: copy, paste: paste, duplicate: duplicate, undo: undo, redo: redo,
      canUndo: function () { return hist.canUndo(); }, canRedo: function () { return hist.canRedo(); },
      fitView: fitView, zoomBy: zoomBy, autoLayout: autoLayout, nodeRect: nodeRect,
      view: function () { return C.clone(view); },
      setView: function (v) {
        view = { zoom: C.clamp(Number(v && v.zoom) || 1, C.MIN_ZOOM, C.MAX_ZOOM), offsetX: Number(v && v.offsetX) || 0, offsetY: Number(v && v.offsetY) || 0 };
        paint();
      },
      setBadges: function (m) { badges = m || {}; paint(); },
      setTints: function (m) { tints = m || {}; paint(); },
      setEdgeStatus: function (m) { edgeStatus = m || {}; paint(); },
      focus: function () { canvas.focus(); },
      refreshLanguage: refreshLanguage, repaint: paint, destroy: destroy, element: canvas
    };
  }

  window.DXGraphCanvas = { create: create, STRINGS: STRINGS, DND_TYPE: DND_TYPE };
})();
