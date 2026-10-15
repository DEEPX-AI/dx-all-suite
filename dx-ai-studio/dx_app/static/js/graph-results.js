/* DX App — Graph Composer results view: the rendered results of a run once (graph-run.js).
   One cell per output, labelled with its stream (source id): one source is one cell, two sit side by side, three
   or four make a 2x2 grid. Each cell can be enlarged into a dialog (Esc closes it, Tab stays inside it); the cell's
   media moves into the dialog and back, so a video keeps its time and a layer stack its toggles.
   An image output with layers (dx_app --output-layers: the clean frame and each node's drawing on its own RGBA PNG
   of the same size) is a stack of <img>s in a box of the frame's aspect ratio, each filling it, so they align
   pixel for pixel; the layer toggles (one per node, in its category colour, with All / None) show and hide them in
   every cell at once. A paused result video offers "Layers for this frame": the run's graph runs again on that
   frame (POST /api/graph/run/frame, the NPU) and the cell shows that frame's stack until the video plays again.
   A component: its owner calls render() after a language change. Contract: tests/dx_app/test_graph_logic_browser.py */
window.GraphResults = (function () {
  'use strict';
  var seq = 0;

  /* A list of checkboxes, one per node, with its category colour and All / None: the layer toggles here and the
     Live tab's "Draw" picker. items: [{key, label, cat}]; isOn(key); onChange(key, on) (key null: All / None). */
  function nodeChecks(c, opts) {
    var o = opts || {}, items = o.items || [], boxes = [];
    var legend = c.h('legend', { class: 'gc-checks-title', text: o.title });
    function setAll(on) {
      boxes.forEach(function (b) { b.checked = on; });
      if (o.onAll) o.onAll(on);
    }
    var all = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm', text: T('All'), disabled: o.disabled });
    var none = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm', text: T('None'), disabled: o.disabled });
    all.addEventListener('click', function () { setAll(true); });
    none.addEventListener('click', function () { setAll(false); });
    var list = c.h('div', { class: 'gc-checks-list' }, items.map(function (it, i) {
      var id = (o.idPrefix || 'gc-check') + '-' + i;
      var box = c.h('input', { type: 'checkbox', id: id, checked: o.isOn(it.key), disabled: o.disabled,
        dataset: { key: it.key } });
      boxes.push(box);
      box.addEventListener('change', function () { o.onChange(it.key, box.checked); });
      return c.h('label', { class: 'gc-check', for: id }, [box,
        c.h('span', { class: 'gc-swatch', dataset: { cat: it.cat || 'model' }, 'aria-hidden': 'true' }),
        c.h('span', { class: 'gc-check-name', text: it.label })]);
    }));
    return c.h('fieldset', { class: 'gc-checks', id: o.id }, [legend,
      c.h('div', { class: 'gc-checks-row' }, [list, c.h('div', { class: 'gc-checks-all' }, [all, none])])]);
  }

  /* The stream of an output: its "stream", else read from dx_app's name (result_<source>[_<frame6>].<ext>). */
  function streamOf(out1) {
    if (out1.stream) return out1.stream;
    var m = /^result_(.+?)(?:_\d{6})?\.[^.]+$/.exec(out1.name || '');
    return m ? m[1] : null;
  }

  /* The toggle of one layer: a node's id, or "panel:<name>" for dx_app's event panel. */
  function layerKey(l) { return l.node != null ? l.node : 'panel:' + (l.panel || ''); }

  function create(host, c, opts) {
    var o = opts || {}, scope = 'r' + (++seq);
    var st = { outputs: [], runId: null, hidden: {}, frames: {}, busy: {}, notes: {}, cells: {}, open: null };
    var dlg = null;

    function category(l) {
      var n = l.node != null && c.nodeOf(l.node);
      if (n && n.category) return n.category;
      if (l.panel) return 'panel';
      return l.op ? 'logic' : 'model';
    }

    function layerLabel(l) {
      if (l.panel === 'events') return T('Event panel');
      if (l.panel) return l.panel;
      return l.node + (l.model ? ' · ' + l.model : l.op ? ' · ' + l.op : '');
    }

    /* Every layer of the results and of the frames taken from videos, once each, in stacking order. */
    function layerItems() {
      var seen = {}, out = [];
      function add(set) {
        ((set && set.layers) || []).forEach(function (l) {
          var k = layerKey(l);
          if (seen[k]) return;
          seen[k] = true;
          out.push({ key: k, label: layerLabel(l), cat: category(l) });
        });
      }
      st.outputs.forEach(function (out1) { add(out1.layers); });
      Object.keys(st.frames).forEach(function (s) { add(st.frames[s].layers); });
      return out;
    }

    function applyToggles() {
      var sel = '.gc-res-layer[data-scope="' + scope + '"]';
      [host, dlg].forEach(function (root) {
        if (!root) return;
        root.querySelectorAll(sel).forEach(function (img) { img.hidden = !!st.hidden[img.dataset.layer]; });
      });
    }

    /* A stack of the clean frame and its layers, each <img> filling a box of the frame's aspect ratio. */
    function stack(set, name) {
      var box = c.h('div', { class: 'gc-res-stack' });
      function ratio(w, h) {
        if (!w || !h) return;
        box.style.setProperty('--ar', String(w / h));
        box.style.aspectRatio = w + ' / ' + h;
      }
      ratio(set.width, set.height);
      var base = c.h('img', { class: 'gc-res-base', src: set.base, alt: c.fmt(T('Result of {name}'), { name: name }) });
      if (!set.width || !set.height) base.addEventListener('load', function () { ratio(base.naturalWidth, base.naturalHeight); });
      box.appendChild(base);
      (set.layers || []).forEach(function (l) {
        box.appendChild(c.h('img', { class: 'gc-res-layer', src: l.url, alt: '', 'aria-hidden': 'true',
          hidden: !!st.hidden[layerKey(l)], dataset: { layer: layerKey(l), scope: scope } }));
      });
      return box;
    }

    function renderToggles() {
      var items = layerItems();
      if (!els.toggles) return;
      els.toggles.textContent = '';
      if (!items.length) return;
      els.toggles.appendChild(nodeChecks(c, { id: 'gc-res-layers-' + scope, idPrefix: 'gc-res-layer-' + scope,
        title: T('Layers'), items: items, isOn: function (k) { return !st.hidden[k]; },
        onChange: function (k, on) { if (on) delete st.hidden[k]; else st.hidden[k] = true; applyToggles(); },
        onAll: function (on) {
          items.forEach(function (it) { if (on) delete st.hidden[it.key]; else st.hidden[it.key] = true; });
          applyToggles();
        } }));
    }

    function frameLabel(f) {
      return c.fmt(T('Frame at {t} s'), { t: Number(f.time_s || 0).toFixed(2) });
    }

    /* The media of one cell: a layer stack, an image, a video (with its frame tools), or a frame of the video. */
    function media(out1) {
      var s = keyOf(out1), cell = st.cells[s];
      var wrap = c.h('div', { class: 'gc-res-media' });
      if (out1.kind !== 'video') {
        wrap.appendChild(out1.layers ? stack(out1.layers, out1.name)
          : c.h('img', { class: 'gc-res-img', src: out1.url, alt: c.fmt(T('Result of {name}'), { name: out1.name }) }));
        return wrap;
      }
      var video = cell && cell.video;
      if (!video) {
        video = c.h('video', { src: out1.url, controls: true, class: 'gc-res-video', tabindex: '0', preload: 'metadata' });
        video.addEventListener('play', function () { if (st.frames[s]) { delete st.frames[s]; renderCell(s); renderToggles(); } else syncTools(s); });
        video.addEventListener('pause', function () { syncTools(s); });
      }
      var f = st.frames[s];
      if (f) {
        video.hidden = true;
        wrap.appendChild(video);
        var back = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm gc-res-back' }, [c.icon('play'),
          c.h('span', { text: ' ' + T('Back to the video') })]);
        back.addEventListener('click', function () { delete st.frames[s]; renderCell(s); renderToggles(); video.focus(); });
        wrap.appendChild(stack(f.layers, frameLabel(f)));
        wrap.appendChild(c.h('div', { class: 'gc-res-frame-tools' }, [c.h('span', { class: 'gc-help', text: frameLabel(f) }), back]));
        return wrap;
      }
      video.hidden = false;
      wrap.appendChild(video);
      if (o.canInspect && o.canInspect()) {
        var btn = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm gc-res-inspect' }, [c.icon('image'),
          c.h('span', { text: ' ' + T('Layers for this frame') })]);
        btn.addEventListener('click', function () { inspect(s); });
        var note = c.h('span', { class: 'gc-help gc-res-note', role: 'status' });
        wrap.appendChild(c.h('div', { class: 'gc-res-frame-tools' }, [btn, note]));
      }
      return wrap;
    }

    /* "Layers for this frame" shows while the video is paused, a spinner while that frame runs. */
    function syncTools(s) {
      var cell = st.cells[s];
      if (!cell) return;
      var root = cell.media, btn = root.querySelector('.gc-res-inspect'), note = root.querySelector('.gc-res-note');
      if (!btn) return;
      btn.hidden = !cell.video.paused && !st.busy[s];
      btn.disabled = !!st.busy[s];
      note.textContent = '';
      if (st.busy[s]) {
        note.appendChild(c.h('span', { class: 'spin', 'aria-hidden': 'true' }));
        note.appendChild(document.createTextNode(' ' + T('Running the graph on this frame…')));
      } else if (st.notes[s]) {
        note.textContent = st.notes[s];
      }
    }

    async function inspect(s) {
      var cell = st.cells[s];
      if (!cell || st.busy[s] || !o.inspect) return;
      var v = cell.video, out1 = cell.output, body = { stream: s };
      v.pause();
      if (out1.fps) body.frame = Math.max(0, Math.floor(v.currentTime * out1.fps + 1e-6));
      else body.time_s = Math.max(0, v.currentTime);
      st.busy[s] = true;
      delete st.notes[s];
      syncTools(s);
      var r = await o.inspect(body);
      st.busy[s] = false;
      if (r && r.ok && r.output && r.output.layers) {
        st.frames[s] = { layers: r.output.layers, time_s: r.time_s };
        renderCell(s);
        renderToggles();
        var stackEl = st.cells[s] && st.cells[s].media.querySelector('.gc-res-back');
        if (stackEl) stackEl.focus();
        return;
      }
      st.notes[s] = o.errorText ? o.errorText(r) : T('The run failed.');
      syncTools(s);
    }

    /* Rebuild one cell's media in place (in the dialog when it is enlarged there). */
    function renderCell(s) {
      var cell = st.cells[s];
      if (!cell) return;
      var fresh = media(cell.output);
      cell.media.replaceWith(fresh);
      cell.media = fresh;
      syncTools(s);
    }

    function keyOf(out1) { return streamOf(out1) || out1.name || ''; }

    function cellOf(out1) {
      var s = keyOf(out1);
      var cell = { output: out1, video: null };
      st.cells[s] = cell;
      cell.media = media(out1);
      cell.video = cell.media.querySelector('video');
      var label = streamOf(out1) || out1.name;
      var grow = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm gc-res-grow',
        'aria-label': c.fmt(T('Enlarge {source}'), { source: label }), title: c.fmt(T('Enlarge {source}'), { source: label }) },
        [c.icon('fit')]);
      grow.addEventListener('click', function () { enlarge(s, grow); });
      cell.slot = c.h('div', { class: 'gc-res-slot' }, [cell.media]);
      cell.el = c.h('figure', { class: 'gc-res-cell', dataset: { stream: s } }, [
        c.h('figcaption', { class: 'gc-res-cap' }, [c.h('span', { class: 'gc-res-label', text: label }), grow]),
        cell.slot]);
      /* A click on an image (not on a video, whose controls take clicks) enlarges it too. */
      cell.slot.addEventListener('click', function (e) {
        if (e.target && e.target.tagName === 'IMG') enlarge(s, grow);
      });
      syncTools(s);
      return cell.el;
    }

    /* ── the enlarge dialog ── */
    function dialog() {
      if (dlg) return dlg;
      var close = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm gc-res-close', 'aria-label': T('Close') }, [c.icon('x')]);
      close.addEventListener('click', function () { dlg.close(); });
      dlg = c.h('dialog', { class: 'modal-overlay gc-res-dialog', id: 'gc-res-dialog-' + scope, 'aria-labelledby': 'gc-res-dialog-title-' + scope }, [
        c.h('div', { class: 'modal modal-lg gc-res-modal' }, [
          c.h('div', { class: 'gc-res-dialog-head' }, [c.h('h2', { id: 'gc-res-dialog-title-' + scope }), close]),
          c.h('div', { class: 'gc-res-dialog-body' })])]);
      dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
      dlg.addEventListener('close', restore);
      /* Tab and Shift+Tab go round the dialog's own controls. */
      dlg.addEventListener('keydown', function (e) {
        if (e.key !== 'Tab') return;
        var f = Array.prototype.filter.call(dlg.querySelectorAll('button, [href], input, select, video[controls], [tabindex]:not([tabindex="-1"])'),
          function (el) { return !(el instanceof SVGElement) && !el.disabled && !el.hidden && el.getClientRects().length > 0; });
        if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      });
      (document.getElementById('page-graph') || document.body).appendChild(dlg);
      return dlg;
    }

    function enlarge(s, opener) {
      var cell = st.cells[s];
      if (!cell) return;
      var d = dialog();
      if (d.open) d.close();
      st.open = { stream: s, opener: opener };
      /* The modal's h2 is upper case; the source id keeps its letter case. */
      var title = d.querySelector('h2'), parts = T('Result of {name}').split('{name}');
      title.textContent = '';
      title.appendChild(document.createTextNode(parts[0]));
      title.appendChild(c.h('span', { class: 'gc-res-src', text: streamOf(cell.output) || cell.output.name }));
      title.appendChild(document.createTextNode(parts.slice(1).join('')));
      var body = d.querySelector('.gc-res-dialog-body'), playing = cell.video && !cell.video.paused;
      body.textContent = '';
      body.appendChild(cell.media);           // moving a video pauses it; it goes on where it was
      if (playing) cell.video.play().catch(function () {});
      d.showModal();
      d.querySelector('.gc-res-close').focus();
    }

    function restore() {
      var open = st.open;
      st.open = null;
      if (!open) return;
      var cell = st.cells[open.stream];
      if (cell && cell.slot && cell.slot.isConnected) {
        var playing = cell.video && !cell.video.paused;
        cell.slot.appendChild(cell.media);
        if (playing) cell.video.play().catch(function () {});
      }
      if (open.opener && open.opener.isConnected) open.opener.focus();
    }

    var els = {};
    function render() {
      if (dlg && dlg.open) dlg.close();
      host.textContent = '';
      st.cells = {};
      if (!st.outputs.length) return;
      els.toggles = c.h('div', { class: 'gc-res-toggles' });
      var n = st.outputs.length;
      els.grid = c.h('div', { class: 'gc-res-grid', dataset: { n: String(n > 4 ? 'many' : n) } },
        st.outputs.map(cellOf));
      host.appendChild(els.toggles);
      host.appendChild(els.grid);
      renderToggles();
    }

    var api = {
      /* A finished run's outputs: [{url, kind, name, stream, fps?, layers?}]. */
      set: function (outputs, meta) {
        st.outputs = (outputs || []).slice();
        st.runId = (meta && meta.runId) || null;
        st.frames = {};
        st.busy = {};
        st.notes = {};
        render();
      },
      clear: function () { st.outputs = []; st.frames = {}; st.hidden = {}; render(); },
      /* Draw into another element (the owner rebuilt its panel); render() then draws the same results again. */
      attach: function (el) { if (dlg && dlg.open) dlg.close(); host = el; },
      /* The result videos, for the event list: [{video, fps, stream}]. */
      videos: function () {
        return st.outputs.filter(function (x) { return x.kind === 'video'; }).map(function (x) {
          var cell = st.cells[keyOf(x)];
          return { video: cell && cell.video, fps: x.fps || null, stream: streamOf(x) };
        }).filter(function (v) { return v.video; });
      },
      /* An event was sought in a stream's video: bring its cell into view (back from a frame, out of the dialog). */
      reveal: function (stream) {
        var s = stream != null && st.cells[stream] ? stream : Object.keys(st.cells)[0];
        var cell = st.cells[s];
        if (!cell) return;
        if (dlg && dlg.open && (!st.open || st.open.stream !== s)) dlg.close();
        if (st.frames[s]) { delete st.frames[s]; renderCell(s); renderToggles(); }
        if (!(dlg && dlg.open)) {
          if (cell.el.scrollIntoView) cell.el.scrollIntoView({ block: 'nearest' });
          cell.el.classList.remove('is-sought');
          void cell.el.offsetWidth;
          cell.el.classList.add('is-sought');
        }
      },
      runId: function () { return st.runId; },
      state: function () { return st; },
      render: render
    };
    return api;
  }

  return { create: create, nodeChecks: nodeChecks, layerKey: layerKey };
})();
