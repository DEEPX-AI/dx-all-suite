/* DX App — Graph Composer run panel: run the graph once on an image or a video (per source: the graph's own input,
   a sample, or an uploaded image), sync or async, then show progress, FPS, per-node time, the rendered result and
   per-node results. Camera and RTSP come with Live (a later phase). Uploads of one run together stay under the
   server's limit (catalog `limits`). Contract: tests/dx_app/test_graph_composer_browser.py */
window.GraphRun = (function () {
  'use strict';
  var c = null, root = null, job = null, timer = 0, picks = {}, uploads = {}, samples = [];
  var els = {};
  var DEFAULT_UPLOAD_LIMIT = 20 * 1024 * 1024;

  function uploadLimit() {
    var l = c && c.state.catalog && c.state.catalog.limits;
    return (l && l.uploads_total_b64) || DEFAULT_UPLOAD_LIMIT;
  }

  function uploadBytes(extra) {
    var n = 0;
    Object.keys(uploads).forEach(function (k) { n += uploads[k].length; });
    return n + (extra || 0);
  }

  function tooLargeText(bytes) {
    return c.fmt(T('The uploaded images add up to {mb} MB; one run takes at most {max} MB. Use smaller images or a sample.'),
      { mb: (bytes / 1048576).toFixed(1), max: Math.round(uploadLimit() / 1048576) });
  }

  function running() { return !!job; }

  function sources() {
    return c.canvas().getGraph().nodes.filter(function (n) { return n.kind === 'source'; });
  }

  function errorText(r) {
    var key = r && r.error_key;
    if (key === 'live_source') return T('Run once takes images and videos. Camera and RTSP sources come with Live.');
    if (key === 'invalid_input') return T('This input does not exist or is outside the dx_app, sample and outputs folders.');
    if (key === 'graph_run_busy') return T('A graph run is already running.');
    if (key === 'graph_binary_missing') return T('The graph runner is not built. Build dx_app (./build.sh) to use the Graph Composer.');
    if (key === 'uploads_too_large' || /^JSON body too large/.test((r && r.error) || '')) return tooLargeText(uploadBytes());
    return (r && r.error) || T('The run failed.');
  }

  function renderInputs() {
    els.inputs.textContent = '';
    var srcs = sources();
    if (!srcs.length) { els.inputs.appendChild(c.h('p', { class: 'gc-help', text: T('Add a source to run the graph.') })); return; }
    srcs.forEach(function (s) {
      var uri = (s.data && s.data.uri) || '';
      var opts = [{ value: '', label: c.fmt(T('As in the graph: {uri}'), { uri: uri }) }]
        .concat(samples.map(function (p) { return { value: p, label: p }; }))
        .concat([{ value: '__upload__', label: T('Upload an image…') }]);
      var sel = c.h('select', { class: 'input', id: 'gc-run-input-' + s.id }, opts.map(function (o) { return c.h('option', { value: o.value, text: o.label }); }));
      sel.value = uploads[s.id] ? '__upload__' : (picks[s.id] || '');
      var file = c.h('input', { type: 'file', accept: 'image/jpeg,image/png', hidden: true });
      sel.addEventListener('change', function () {
        if (sel.value === '__upload__') { file.click(); return; }
        picks[s.id] = sel.value;
        delete uploads[s.id];
      });
      file.addEventListener('change', function () {
        var f = file.files[0];
        if (!f) { sel.value = picks[s.id] || ''; return; }
        var reader = new FileReader();
        reader.onload = function () {
          var data = String(reader.result), others = uploadBytes() - (uploads[s.id] ? uploads[s.id].length : 0);
          if (others + data.length > uploadLimit()) {
            c.notify(tooLargeText(others + data.length), 'warn');
            sel.value = picks[s.id] || '';
            return;
          }
          uploads[s.id] = data;
          delete picks[s.id];
        };
        reader.readAsDataURL(f);
      });
      els.inputs.appendChild(c.h('div', { class: 'fg gc-fg' }, [
        c.h('label', { for: sel.id, text: c.fmt(T('Input for {source}'), { source: s.id }) }), sel, file]));
    });
  }

  function loadSamples() {
    if (typeof api !== 'function') return;
    Promise.all([api('/api/images'), api('/api/videos')]).then(function (r) {
      samples = [].concat(Array.isArray(r[0]) ? r[0] : [], Array.isArray(r[1]) ? r[1] : []);
      renderInputs();
    });
  }

  function mount(el, ctx) {
    c = ctx;
    root = el;
    root.textContent = '';
    els.inputs = c.h('div', { class: 'gc-run-inputs' });
    els.mode = c.h('select', { class: 'input', id: 'gc-run-mode' }, [
      c.h('option', { value: 'sync', text: T('Sync (one stage at a time)') }),
      c.h('option', { value: 'async', text: T('Async (stages overlap)') })]);
    els.inflight = c.h('input', { type: 'number', class: 'input', id: 'gc-run-inflight', min: '1', max: '64', value: '4' });
    els.frames = c.h('input', { type: 'number', class: 'input', id: 'gc-run-frames', min: '1', placeholder: T('all') });
    els.start = c.h('button', { type: 'button', class: 'btn btn-primary btn-sm', id: 'gc-run-start' }, [c.icon('play'), c.h('span', { text: ' ' + T('Run once') })]);
    els.stop = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm', id: 'gc-run-stop', disabled: true }, [c.icon('stop'), c.h('span', { text: ' ' + T('Stop') })]);
    els.progress = c.h('div', { class: 'gc-run-progress', role: 'status', 'aria-live': 'polite' });
    els.result = c.h('div', { class: 'gc-run-result' });
    els.start.addEventListener('click', start);
    els.stop.addEventListener('click', stop);
    els.mode.addEventListener('change', function () { els.inflightRow.hidden = els.mode.value !== 'async'; });
    els.inflightRow = c.h('div', { class: 'fg gc-fg', hidden: true }, [c.h('label', { for: 'gc-run-inflight', text: T('Frames in flight') }), els.inflight]);
    root.appendChild(c.h('div', { class: 'gc-run-form' }, [els.inputs,
      c.h('div', { class: 'fg gc-fg' }, [c.h('label', { for: 'gc-run-mode', text: T('Mode') }), els.mode]),
      els.inflightRow,
      c.h('div', { class: 'fg gc-fg' }, [c.h('label', { for: 'gc-run-frames', text: T('Stop after frames') }), els.frames]),
      c.h('div', { class: 'gc-run-actions' }, [els.start, els.stop])]));
    root.appendChild(els.progress);
    root.appendChild(els.result);
    renderInputs();
    loadSamples();
  }

  function setRunning(on) {
    els.start.disabled = on;
    els.stop.disabled = !on;
    c.updateStatus();
  }

  async function start() {
    if (job) return;
    var g = c.engine();
    if (!g.nodes.length) return;
    if (uploadBytes() > uploadLimit()) { els.progress.textContent = tooLargeText(uploadBytes()); return; }
    var body = { graph: g, variant: els.mode.value, inputs: {}, uploads: {} };
    sources().forEach(function (s) {
      if (uploads[s.id]) body.uploads[s.id] = uploads[s.id];
      else if (picks[s.id]) body.inputs[s.id] = picks[s.id];
    });
    if (els.mode.value === 'async') body.max_inflight = Number(els.inflight.value) || 4;
    if (els.frames.value) body.frames = Number(els.frames.value);
    els.result.textContent = '';
    els.progress.textContent = T('Starting…');
    job = 'starting';
    setRunning(true);
    var r = await c.api.run(body);
    if (!r.job_id) {
      job = null;
      setRunning(false);
      els.progress.textContent = errorText(r);
      return;
    }
    job = r.job_id;
    poll();
  }

  async function stop() {
    if (job && job !== 'starting') await c.api.stop(job);
  }

  function renderProgress(p) {
    els.progress.textContent = '';
    var parts = [c.fmt(T('{frames} frames'), { frames: p.frames || 0 })];
    if (p.fps != null) parts.push(c.fmt(T('{fps} FPS (average {avg})'), { fps: p.fps.toFixed(1), avg: (p.avg_fps || 0).toFixed(1) }));
    parts.push(c.fmt(T('{s} s'), { s: p.elapsed }));
    els.progress.appendChild(c.h('p', { text: parts.join(' · ') }));
    var ms = p.node_ms || {}, ids = Object.keys(ms).sort(function (a, b) { return ms[b] - ms[a]; }), total = 0;
    ids.forEach(function (k) { total += ms[k]; });
    if (!ids.length) return;
    els.progress.appendChild(c.h('ul', { class: 'gc-ms' }, ids.map(function (k) {
      var pct = total ? Math.round(ms[k] * 100 / total) : 0;
      return c.h('li', {}, [c.h('span', { class: 'gc-ms-name', text: k }),
        c.h('span', { class: 'gc-ms-bar' }, [c.h('span', { class: 'gc-ms-fill', style: 'width:' + pct + '%' })]),
        c.h('span', { class: 'gc-ms-value', text: ms[k].toFixed(1) + ' ms' })]);
    })));
  }

  function poll() {
    clearTimeout(timer);
    timer = setTimeout(async function () {
      var p = await c.api.poll(job);
      if (p.error) { finish({ ok: false, error: p.error }); return; }
      renderProgress(p);
      if (!p.has_result) { poll(); return; }
      var r = await c.api.result(job);
      if (r.running) { poll(); return; }
      finish(r);
    }, 500);
  }

  function finish(r) {
    job = null;
    c.state.run = r.error && !r.nodes ? null : r;
    setRunning(false);
    c.applyPins();
    renderResult(r);
    if (window.GraphInspector) GraphInspector.render(document.getElementById('gc-inspector-body'), c, c.state.sel);
  }

  function renderResult(r) {
    els.result.textContent = '';
    if (!r || r.error && !r.nodes) { els.result.appendChild(c.h('p', { class: 'gc-error', text: errorText(r) })); return; }
    els.result.appendChild(c.h('p', { class: r.ok ? 'gc-ok' : 'gc-error', text: r.ok
      ? c.fmt(T('Done: {frames} frames in {s} s'), { frames: r.frames, s: r.elapsed })
      : c.fmt(T('The run stopped with exit code {code}'), { code: r.exit_code }) }));
    (r.errors || []).forEach(function (e) {
      els.result.appendChild(c.h('div', { class: 'gc-error', role: 'alert' }, [c.h('strong', { text: e.code }),
        c.h('span', { text: ' ' + (e.node ? e.node + ': ' : '') + e.what }), e.how ? c.h('p', { class: 'gc-help', text: '→ ' + e.how }) : null]));
    });
    (r.outputs || []).forEach(function (o) {
      els.result.appendChild(o.kind === 'video'
        ? c.h('video', { src: o.url, controls: true, class: 'gc-run-media' })
        : c.h('img', { src: o.url, alt: c.fmt(T('Result of {name}'), { name: o.name }), class: 'gc-run-media' }));
    });
    var ids = Object.keys(r.nodes || {});
    if (!ids.length) return;
    var rows = ids.map(function (id) {
      var n = r.nodes[id];
      var btn = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm', text: id });
      btn.addEventListener('click', function () { c.canvas().select({ nodes: [id] }); c.canvas().focus(); });
      return c.h('tr', {}, [c.h('td', {}, [btn]), c.h('td', { text: n.shape || '-' }), c.h('td', { text: String(n.items_total) }),
        c.h('td', { text: String(n.crops_total) }), c.h('td', { text: r.node_ms && r.node_ms[id] != null ? r.node_ms[id].toFixed(1) : '-' })]);
    });
    els.result.appendChild(c.h('table', { class: 'gc-run-table' }, [
      c.h('thead', {}, [c.h('tr', {}, [c.h('th', { text: T('Node') }), c.h('th', { text: T('Output') }), c.h('th', { text: T('Results') }),
        c.h('th', { text: T('Crops') }), c.h('th', { text: T('ms per frame') })])]),
      c.h('tbody', {}, rows)]));
  }

  function reset() {
    clearTimeout(timer);
    picks = {};
    uploads = {};
    if (!root) return;
    els.progress.textContent = '';
    els.result.textContent = '';
    renderInputs();
  }

  function refreshLanguage() {
    if (!root) return;
    var mode = els.mode.value;
    mount(root, c);
    els.mode.value = mode;
    els.inflightRow.hidden = mode !== 'async';
    els.start.disabled = !!job;
    els.stop.disabled = !job;
    if (c.state.run) renderResult(c.state.run);
  }

  if (typeof registerLangRefresher === 'function') {
    registerLangRefresher(function () { if (root && document.querySelector('#page-graph.active')) refreshLanguage(); });
  }

  return { mount: mount, start: start, stop: stop, reset: reset, running: running, refreshLanguage: refreshLanguage,
    renderInputs: function () { if (root) renderInputs(); },
    /* The input picked for a source here (a sample path), else null: the zone editor draws on that frame. */
    inputFor: function (sid) { return picks[sid] || null; } };
})();
