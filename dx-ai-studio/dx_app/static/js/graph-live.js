/* DX App — Graph Composer Live tab: run the graph on a camera, an RTSP stream or a looping video until stopped, and
   watch it — the rendered frames (an MJPEG stream of the runner's window, /api/graph/live/frame), FPS, time per node
   and the events as they fire. One Live at a time; it does not run beside a run once or the Run page's Live
   (dx_app/core/graph_live.py). Leaving the page stops it, like the Run page's continuous mode. Before start, "Draw"
   picks the nodes the picture shows (dx_app --draw; every node still runs); with several sources the picture is
   dx_app's grid of the streams, each labelled with its source id.
   Contract: tests/dx_app/test_graph_logic_browser.py */
window.GraphLive = (function () {
  'use strict';
  var c = null, root = null, job = null, timer = 0, picks = {}, rtsp = {}, cameras = [], videos = [], events = null;
  var drawOff = {};
  var els = {};

  function running() { return !!job; }

  function sources() {
    return c.canvas().getGraph().nodes.filter(function (n) { return n.kind === 'source'; });
  }

  function errorText(r) {
    var key = r && r.error_key;
    if (key === 'live_deps_missing') return c.fmt(T('Live needs these on this computer: {what}'), { what: (r.error || '').replace(/^Live needs: /, '') });
    if (key === 'loop_unsupported') return T('This dx_app build cannot loop a video yet. Use a camera or an RTSP stream.');
    if (key === 'graph_live_busy') return T('A graph Live is already running.');
    if (key === 'graph_run_busy') return T('A graph run is running. Wait for it or stop it first.');
    if (key === 'live_busy') return T('The Run page has a Live run. Stop it there first.');
    if (key === 'invalid_live_input') return c.fmt(T('This input cannot stream: {why}'), { why: r.error || '' });
    if (key === 'graph_binary_missing') return T('The graph runner is not built. Build dx_app (./build.sh) to use the Graph Composer.');
    if (key === 'invalid_draw') return c.fmt(T('The nodes to draw do not match the graph: {why}'), { why: r.error || '' });
    if (key === 'draw_unsupported') return T('This dx_app build draws every node. Update dx_app to pick the nodes to draw.');
    /* Other refusals (npu_hold_lost, gallery_busy, unknown_job, ...): the dictionary text of the error key. */
    return (typeof translatedError === 'function' ? translatedError(r) : r && r.error) || T('Live failed to start.');
  }

  function inputOptions(s) {
    var uri = (s.data && s.data.uri) || '';
    var opts = [{ value: '', label: c.fmt(T('As in the graph: {uri}'), { uri: uri }) }];
    cameras.forEach(function (cam) {
      opts.push({ value: 'camera:' + cam.index, label: c.fmt(T('Camera {n}'), { n: cam.index }) + (cam.device ? ' (' + cam.device + ')' : '') });
    });
    opts.push({ value: '__rtsp__', label: T('RTSP stream…') });
    videos.forEach(function (v) { opts.push({ value: v, label: c.fmt(T('{video} (looping)'), { video: v }) }); });
    return opts;
  }

  /* The nodes that draw (every node but the sources), for the "Draw" picker. */
  function drawable() {
    return c.canvas().getGraph().nodes.filter(function (n) { return n.kind !== 'source'; });
  }

  function canDraw() {
    var caps = c.state.catalog && c.state.catalog.capabilities;
    return !!(caps && caps.draw);
  }

  function renderDraw() {
    els.draw.textContent = '';
    var nodes = drawable();
    els.draw.hidden = !canDraw() || !nodes.length;
    if (els.draw.hidden) return;
    var items = nodes.map(function (n) {
      var d = n.data || {};
      return { key: n.id, label: n.id + (d.model ? ' · ' + d.model : d.op ? ' · ' + d.op : ''), cat: n.category };
    });
    els.draw.appendChild(GraphResults.nodeChecks(c, { id: 'gc-live-draw-list', idPrefix: 'gc-live-draw', title: T('Draw'),
      items: items, disabled: !!job, isOn: function (k) { return !drawOff[k]; },
      onChange: function (k, on) { if (on) delete drawOff[k]; else drawOff[k] = true; },
      onAll: function (on) { items.forEach(function (it) { if (on) delete drawOff[it.key]; else drawOff[it.key] = true; }); } }));
    els.draw.appendChild(c.h('p', { class: 'gc-help', text: T('Only the checked nodes draw on the picture; every node still runs and raises its events.') }));
  }

  /* The ids to send as `draw`: null when every node draws (no --draw), [] when none is checked. */
  function drawPick() {
    var nodes = drawable();
    if (!canDraw() || !nodes.some(function (n) { return drawOff[n.id]; })) return null;
    return nodes.filter(function (n) { return !drawOff[n.id]; }).map(function (n) { return n.id; });
  }

  function renderInputs() {
    if (els.draw) renderDraw();
    els.inputs.textContent = '';
    var srcs = sources();
    if (!srcs.length) { els.inputs.appendChild(c.h('p', { class: 'gc-help', text: T('Add a source to run the graph.') })); return; }
    srcs.forEach(function (s) {
      var sel = c.h('select', { class: 'input', id: 'gc-live-input-' + s.id }, inputOptions(s).map(function (o) {
        return c.h('option', { value: o.value, text: o.label });
      }));
      var url = c.h('input', { type: 'text', class: 'input', id: 'gc-live-rtsp-' + s.id, placeholder: 'rtsp://192.168.0.10/stream1',
        value: rtsp[s.id] || '', 'aria-label': c.fmt(T('RTSP address for {source}'), { source: s.id }) });
      sel.value = picks[s.id] || '';
      url.hidden = sel.value !== '__rtsp__';
      sel.addEventListener('change', function () { picks[s.id] = sel.value; url.hidden = sel.value !== '__rtsp__'; if (!url.hidden) url.focus(); });
      url.addEventListener('change', function () { rtsp[s.id] = url.value.trim(); });
      els.inputs.appendChild(c.h('div', { class: 'fg gc-fg' }, [
        c.h('label', { for: sel.id, text: c.fmt(T('Live input for {source}'), { source: s.id }) }), sel, url]));
    });
  }

  function loadChoices() {
    if (typeof api !== 'function') return;
    Promise.all([api('/api/cameras'), api('/api/videos')]).then(function (r) {
      cameras = (Array.isArray(r[0]) ? r[0] : []).filter(function (x) { return x && x.available; });
      videos = Array.isArray(r[1]) ? r[1] : [];
      if (root) renderInputs();
    });
  }

  function mount(el, ctx) {
    c = ctx;
    root = el;
    root.textContent = '';
    els.inputs = c.h('div', { class: 'gc-run-inputs' });
    els.mode = c.h('select', { class: 'input', id: 'gc-live-mode' }, [
      c.h('option', { value: 'sync', text: T('Sync (one stage at a time)') }),
      c.h('option', { value: 'async', text: T('Async (stages overlap)') })]);
    els.start = c.h('button', { type: 'button', class: 'btn btn-primary btn-sm', id: 'gc-live-start' }, [c.icon('play'), c.h('span', { text: ' ' + T('Start Live') })]);
    els.stop = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm', id: 'gc-live-stop', disabled: true }, [c.icon('stop'), c.h('span', { text: ' ' + T('Stop') })]);
    els.status = c.h('div', { class: 'gc-run-progress', role: 'status', 'aria-live': 'polite' });
    els.draw = c.h('div', { class: 'gc-live-draw', id: 'gc-live-draw' });
    els.view = c.h('img', { class: 'gc-live-view', id: 'gc-live-view', alt: T('Live view of the graph'), hidden: true });
    els.errors = c.h('div', { class: 'gc-run-result' });
    els.events = c.h('div', { class: 'gc-events', id: 'gc-live-events' });
    els.start.addEventListener('click', start);
    els.stop.addEventListener('click', stop);
    root.appendChild(c.h('div', { class: 'gc-run-form' }, [els.inputs,
      c.h('div', { class: 'fg gc-fg' }, [c.h('label', { for: 'gc-live-mode', text: T('Mode') }), els.mode]),
      c.h('div', { class: 'gc-run-actions' }, [els.start, els.stop])]));
    root.appendChild(els.draw);
    root.appendChild(c.h('p', { class: 'gc-help', text: T('A video loops until you stop. One Live runs at a time; leaving this page stops it.') }));
    root.appendChild(els.status);
    root.appendChild(els.view);
    root.appendChild(els.errors);
    root.appendChild(els.events);
    if (!events) events = GraphEvents.create(els.events, c, { idPrefix: 'gc-live-ev', onSelectNode: function (id) { if (c.nodeOf(id)) c.canvas().select({ nodes: [id] }); } });
    else events.attach(els.events);
    renderInputs();
    loadChoices();
    setRunning(!!job);
  }

  function setRunning(on) {
    els.start.disabled = on;
    els.stop.disabled = !on;
    els.draw.querySelectorAll('input, button').forEach(function (el) { el.disabled = on; });
    c.updateStatus();
  }

  function inputsBody() {
    var out = {};
    sources().forEach(function (s) {
      var v = picks[s.id] || '';
      if (v === '__rtsp__') { if (rtsp[s.id]) out[s.id] = rtsp[s.id]; }
      else if (v) out[s.id] = v;
    });
    return out;
  }

  async function start() {
    if (job) return;
    var g = c.engine();
    if (!g.nodes.length) return;
    var body = { graph: g, variant: els.mode.value, inputs: inputsBody() }, draw = drawPick();
    if (draw && !draw.length) { els.status.textContent = T('Check at least one node to draw.'); return; }
    if (draw) body.draw = draw;
    els.errors.textContent = '';
    events.clear();
    els.status.textContent = T('Starting Live…');
    job = { id: null };
    setRunning(true);
    var r = await c.api.liveStart(body), leaving = job && job.leaving;
    if (r.job_id && leaving) {                 // the page was left while Live was starting
      c.api.liveStop(r.job_id);
      job = null;
      setRunning(false);
      return;
    }
    if (!r.job_id) {
      job = null;
      setRunning(false);
      els.status.textContent = errorText(r);
      return;
    }
    job = { id: r.job_id, frame: r.frame_url };
    showView();
    poll();
  }

  function showView() {
    els.view.hidden = false;
    els.view.src = job.frame + '&t=' + Date.now();
  }

  async function stop() {
    if (job && job.id) {
      els.status.textContent = T('Stopping…');
      await c.api.liveStop(job.id);
    }
  }

  function renderStats(p) {
    els.status.textContent = '';
    var parts = [c.fmt(T('{frames} frames'), { frames: p.frames || 0 })];
    if (p.fps != null) parts.push(c.fmt(T('{fps} FPS (average {avg})'), { fps: p.fps.toFixed(1), avg: (p.avg_fps || 0).toFixed(1) }));
    parts.push(c.fmt(T('{s} s'), { s: p.elapsed }));
    els.status.appendChild(c.h('p', { text: parts.join(' · ') }));
    var ms = p.node_ms || {}, ids = Object.keys(ms).sort(function (a, b) { return ms[b] - ms[a]; }), total = 0;
    ids.forEach(function (k) { total += ms[k]; });
    if (!ids.length) return;
    els.status.appendChild(c.h('ul', { class: 'gc-ms' }, ids.map(function (k) {
      var pct = total ? Math.round(ms[k] * 100 / total) : 0;
      return c.h('li', {}, [c.h('span', { class: 'gc-ms-name', text: k }),
        c.h('span', { class: 'gc-ms-bar' }, [c.h('span', { class: 'gc-ms-fill', style: 'width:' + pct + '%' })]),
        c.h('span', { class: 'gc-ms-value', text: ms[k].toFixed(1) + ' ms' })]);
    })));
  }

  function poll() {
    clearTimeout(timer);
    timer = setTimeout(async function () {
      if (!job || !job.id) return;
      var p = await c.api.livePoll(job.id, events.lastSeq());
      if (p.error) { finish({ errors: [], exit_code: null, error: p.error, error_key: p.error_key }); return; }
      renderStats(p);
      events.append(p.events, p.event_total);
      c.observe({ node_ms: p.node_ms, event_counts: p.event_counts });
      if (p.running) { poll(); return; }
      finish(p);
    }, 1000);
  }

  function finish(p) {
    clearTimeout(timer);
    job = null;
    els.view.removeAttribute('src');
    els.view.hidden = true;
    setRunning(false);
    c.state.run = Object.assign({}, c.state.run || {}, { event_counts: p.event_counts || {}, node_ms: p.node_ms || {} });
    c.observe(null);
    c.applyPins();
    els.errors.textContent = '';
    els.errors.appendChild(c.h('p', { class: (p.errors && p.errors.length) || p.error ? 'gc-error' : 'gc-ok',
      text: p.stopped_by === 'user' ? T('Live stopped.') : p.stopped_by === 'unwatched' ? T('Live stopped: the page stopped asking for it.')
        : c.fmt(T('Live ended (exit code {code}).'), { code: p.exit_code == null ? '-' : p.exit_code }) }));
    if (p.error) els.errors.appendChild(c.h('p', { class: 'gc-error', role: 'alert', text: errorText(p) }));
    (p.errors || []).forEach(function (e) {
      els.errors.appendChild(c.h('div', { class: 'gc-error', role: 'alert' }, [c.h('strong', { text: e.code }),
        c.h('span', { text: ' ' + (e.node ? e.node + ': ' : '') + e.what }), e.how ? c.h('p', { class: 'gc-help', text: '→ ' + e.how }) : null]));
    });
    var st = events.state();
    events.set(st.events, { total: p.event_total != null ? p.event_total : st.total, url: p.events_url || null });
  }

  /* The page is left (utils.js nav): stop, as the Run page stops its continuous mode. */
  function leave() {
    if (!job) return;
    if (job.id) c.api.liveStop(job.id);
    else job.leaving = true;
  }

  function refreshLanguage() {
    if (!root) return;
    var mode = els.mode.value, status = els.status.textContent;
    mount(root, c);
    els.mode.value = mode;
    if (job) { els.status.textContent = status; if (job.frame) showView(); }
    events.render();
  }

  if (typeof registerLangRefresher === 'function') {
    registerLangRefresher(function () { if (root && document.querySelector('#page-graph.active')) refreshLanguage(); });
  }

  return { mount: mount, start: start, stop: stop, running: running, leave: leave, refreshLanguage: refreshLanguage,
    renderInputs: function () { if (root) renderInputs(); } };
})();
