/* DX App — Graph Composer page (templates/index.html #page-graph).

   Palette, canvas, inspector, validation pins, the NPU memory bar, the run panel and projects around one dx_app
   graph. The server API is /api/graph/* (dx_app/core/graph_routes.py) with the Lab session token.
   Pieces: graph-doc.js (document model), graph-palette.js, graph-inspector.js, graph-run.js (run once),
   graph-live.js (Live), graph-events.js (event lists), graph-zone.js + graph-zone-editor.js (zones and lines); the
   canvas is shared/static/dx-graph-canvas.js. While a run or a Live goes, its per-node time and event counts tint and
   badge the nodes (observe()). Contract: tests/dx_app/test_graph_composer_page.py,
   tests/dx_app/test_graph_composer_browser.py */
window.GraphComposer = (function () {
  'use strict';
  var D = window.GraphDoc;
  var DRAFT_KEY = 'dx-graph-draft';
  var st = {
    cv: null, catalog: null, models: {}, ops: {}, check: null, memory: null, run: null, observed: null,
    sel: { nodes: [], edge: null }, runTab: 'once',
    projectId: null, version: null, name: '', dirty: false, opened: false, lang: null,
    validateTimer: 0, validateSeq: 0
  };

  /* ── small DOM helpers shared with graph-palette / graph-inspector / graph-run ── */
  function h(tag, attrs, kids) {
    var el = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      var v = attrs[k];
      if (v == null || v === false) return;
      if (k === 'text') el.textContent = v;
      else if (k === 'class') el.className = v;
      else if (k === 'dataset') Object.keys(v).forEach(function (d) { el.dataset[d] = v[d]; });
      else if (k.slice(0, 2) === 'on' && typeof v === 'function') el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? '' : String(v));
    });
    (kids || []).forEach(function (c) {
      if (c != null) el.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    });
    return el;
  }
  function icon(name) { return window.DXIcon && DXIcon.el ? DXIcon.el(name) : document.createTextNode(''); }
  function $id(i) { return document.getElementById(i); }
  function fmt(s, vars) {
    Object.keys(vars || {}).forEach(function (k) { s = s.split('{' + k + '}').join(String(vars[k])); });
    return s;
  }
  function tr(k) { return typeof T === 'function' ? T(k) : k; }
  function curLang() { return (window.DXI18n && DXI18n.lang) || 'en'; }
  function notify(msg, kind) { if (typeof toast === 'function') toast(msg, kind || 'info'); }
  function labToken() { return (typeof S !== 'undefined' && S.labToken) || ''; }

  /* ── API ── */
  async function call(method, path, body) {
    if (typeof labEnsureSession === 'function') await labEnsureSession();
    for (var attempt = 0; attempt < 2; attempt++) {
      var headers = { 'X-Lab-Token': labToken() };
      if (body !== undefined) headers['Content-Type'] = 'application/json';
      var res, data;
      try {
        res = await fetch(path, { method: method, headers: headers, body: body === undefined ? undefined : JSON.stringify(body) });
        data = await res.json().catch(function () { return {}; });
      } catch (e) {
        return { error: (e && e.message) || 'network', error_key: 'network' };
      }
      if (res.status === 403 && data && data.error === 'Lab session required' && attempt === 0 && typeof S !== 'undefined') {
        S.labToken = null;
        if (typeof labEnsureSession === 'function') await labEnsureSession();
        continue;
      }
      if (!res.ok && data && !data.error) data.error = 'HTTP ' + res.status;
      return data || {};
    }
    return { error: 'Lab session required' };
  }

  var api = {
    catalog: function (refresh) { return call('GET', '/api/graph/catalog' + (refresh ? '?refresh=1' : '')); },
    validate: function (g) { return call('POST', '/api/graph/validate', { graph: g }); },
    memory: function (g) { return call('POST', '/api/graph/memory', { graph: g }); },
    run: function (body) { return call('POST', '/api/graph/run', body); },
    poll: function (id, after) {
      return call('GET', '/api/graph/run/poll?id=' + encodeURIComponent(id) + '&events_after=' + encodeURIComponent(after || 0));
    },
    frame: function (uri) { return call('GET', '/api/graph/frame?uri=' + encodeURIComponent(uri)); },
    liveStart: function (body) { return call('POST', '/api/graph/live/start', body); },
    livePoll: function (id, after) {
      return call('GET', '/api/graph/live/poll?id=' + encodeURIComponent(id) + '&events_after=' + encodeURIComponent(after || 0));
    },
    liveStop: function (id) { return call('POST', '/api/graph/live/stop', { id: id }); },
    result: function (id) { return call('GET', '/api/graph/run/result?id=' + encodeURIComponent(id)); },
    stop: function (id) { return call('POST', '/api/graph/run/stop', { id: id }); },
    galleryBuild: function (body) { return call('POST', '/api/graph/gallery/build', body); },
    galleryPoll: function (id) { return call('GET', '/api/graph/gallery/poll?id=' + encodeURIComponent(id)); },
    galleryStop: function (id) { return call('POST', '/api/graph/gallery/stop', { id: id }); },
    projects: function () { return call('GET', '/api/graph/projects'); },
    project: function (id, v) {
      return call('GET', '/api/graph/project?id=' + encodeURIComponent(id) + (v ? '&version=' + encodeURIComponent(v) : ''));
    },
    versions: function (id) { return call('GET', '/api/graph/project/versions?id=' + encodeURIComponent(id)); },
    save: function (id, project) { return call('POST', '/api/graph/project/save', { id: id, project: project }); },
    remove: function (id) { return call('POST', '/api/graph/project/delete', { id: id }); }
  };

  /* ── the graph ── */
  function engineGraph() { return D.toEngine(st.cv.getGraph(), st.name || 'graph'); }

  function nodeOf(id) {
    var found = null;
    st.cv.getGraph().nodes.forEach(function (n) { if (n.id === id) found = n; });
    return found;
  }

  function specFrom(p) {
    var n;
    if (!p) return null;
    if (p.kind === 'source') n = { id: 'cam', kind: 'source', data: { type: 'source', uri: p.uri || 'sample/img/sample_people.jpg' } };
    else if (p.kind === 'cpu') n = { id: p.op, kind: 'cpu', data: { type: 'cpu', op: p.op, params: D.clone(p.params || {}) } };
    else if (p.kind === 'model') n = { id: D.suggestId(p.model, st.models), kind: 'model', data: { model: p.model } };
    else if (p.kind === 'logic') n = { id: p.op, kind: 'logic', data: { type: 'logic', op: p.op, params: D.logicDefaults(st.ops[p.op]) } };
    else return null;
    return D.decorate(n, st.models, tr);
  }

  function addFromPalette(payload) {
    var spec = specFrom(payload);
    if (spec) st.cv.addNode(spec);
  }

  function refreshDisplay() {
    var g = st.cv.getGraph();
    g.nodes.forEach(function (n) {
      D.decorate(n, st.models, tr);
      st.cv.updateNode(n.id, { label: n.label, sub: n.sub, icon: n.icon, category: n.category, noInput: n.noInput, noOutput: n.noOutput }, { commit: false });
    });
    g.edges.forEach(function (e) {
      var l = D.edgeLabel(e, tr);
      if (l !== e.label) st.cv.updateEdge(e.id, { label: l }, { commit: false });
    });
  }

  function onGraphChange() {
    st.dirty = true;
    refreshDisplay();
    saveDraft();
    scheduleValidate();
    renderInspector();
    if (window.GraphRun) GraphRun.renderInputs();
    if (window.GraphLive) GraphLive.renderInputs();
    if (window.GraphZoneEditor) GraphZoneEditor.refresh();
    updateStatus();
  }

  /* The source a node's frames come from (walking its in-edges back), as the run would read it: the input picked in
     the run panel, else the source's uri. Null when no source reaches it. */
  function sourceFor(id) {
    var g = st.cv.getGraph(), seen = {}, queue = [id];
    while (queue.length) {
      var cur = queue.shift(), n = nodeOf(cur);
      if (!n || seen[cur]) continue;
      seen[cur] = true;
      if (n.kind === 'source') return (window.GraphRun && GraphRun.inputFor(n.id)) || (n.data && n.data.uri) || null;
      g.edges.forEach(function (e) { if (e.to === cur) queue.push(e.from); });
    }
    return null;
  }

  /* Per-node time and event counts of a run or a Live while it goes; null when it ends (the result takes over). */
  function observe(x) {
    st.observed = x;
    applyPins();
  }

  function scheduleValidate() {
    clearTimeout(st.validateTimer);
    st.validateTimer = setTimeout(validateNow, 400);
  }

  async function validateNow() {
    clearTimeout(st.validateTimer);
    var seq = ++st.validateSeq, g = engineGraph();
    if (!g.nodes.length) {
      st.check = null;
      st.memory = null;
      applyPins();
      renderMemory();
      updateStatus();
      return;
    }
    setStatus('busy', T('Checking the graph…'));
    var both = await Promise.all([api.validate(g), api.memory(g)]);
    if (seq !== st.validateSeq) return;
    st.check = both[0];
    st.memory = both[1];
    applyPins();
    renderMemory();
    renderInspector();
    updateStatus();
  }

  function applyPins() {
    var p = D.pins(st.check, st.memory, st.observed || st.run, tr);
    st.cv.setBadges(p.badges);
    st.cv.setEdgeStatus(p.edges);
    st.cv.setTints(p.tints);
  }

  function setStatus(kind, text) {
    var el = $id('gc-status');
    if (!el) return;
    el.dataset.kind = kind || '';
    el.textContent = text || '';
  }

  function unusableCount() { return Object.keys((st.check && st.check.unusable) || {}).length; }

  function runnable() {
    return !!(st.check && st.check.ok && !(st.check.missing || []).length && !unusableCount()
      && !(st.memory && st.memory.over_budget));
  }

  function busy() { return !!((window.GraphRun && GraphRun.running()) || (window.GraphLive && GraphLive.running())); }

  function canRun() { return runnable() && !busy(); }

  function updateStatus() {
    var g = st.cv.getGraph(), run = $id('gc-run'), live = $id('gc-live');
    if (run) run.disabled = !canRun();
    if (live) live.disabled = !canRun();
    if (st.catalog && st.catalog.available === false) {
      setStatus('error', T('The graph runner is not built. Build dx_app (./build.sh) to use the Graph Composer.'));
      return;
    }
    if (!g.nodes.length) { setStatus('', T('Empty graph')); return; }
    var c = st.check;
    if (!c) return;
    if (c.error && !c.errors) { setStatus('error', T('Could not check the graph')); return; }
    if ((c.errors || []).length) { setStatus('error', fmt(T('{n} problems to fix'), { n: c.errors.length })); return; }
    if (unusableCount()) { setStatus('error', fmt(T('{n} model files cannot be used'), { n: unusableCount() })); return; }
    if ((c.missing || []).length) { setStatus('warn', fmt(T('{n} models are not installed'), { n: c.missing.length })); return; }
    if (st.memory && st.memory.over_budget) { setStatus('warn', T('Over the NPU memory budget')); return; }
    setStatus('ok', T('Ready to run') + (st.dirty ? ' · ' + T('Unsaved changes') : ''));
  }

  /* ── memory bar ── */
  function suggestionText(s) {
    var saves = D.fmtBytes(s.saves_bytes);
    if (s.kind === 'share') return fmt(T('Share one engine between {nodes} ({model}): saves {saves}'), { nodes: s.nodes.join(', '), model: s.model, saves: saves });
    return fmt(T('Use {n} buffers on {nodes}: saves {saves}'), { n: s.buffers, nodes: s.nodes.join(', '), saves: saves });
  }

  /* A share suggestion carries the server's patch per node (graph_memory._share_patch): dx_app accepts a shared
     engine only when every sharing node has the owner's params and buffers, so engine and params are set as given
     (null removes the key). A buffers suggestion sets the buffer count. One undo step either way. */
  function applySuggestion(s) {
    var ids = s.patch ? Object.keys(s.patch) : s.nodes;
    var todo = ids.map(nodeOf).filter(Boolean);
    todo.forEach(function (n, i) {
      var data;
      if (s.patch) data = D.applyPatch(n.data, s.patch[n.id]);
      else {
        data = D.clone(n.data || {});
        data.engine = data.engine || {};
        if (s.kind === 'share') data.engine.share = true; else data.engine.buffers = s.buffers;
      }
      st.cv.updateNode(n.id, { data: data }, { commit: i === todo.length - 1 });
    });
  }

  function renderMemory() {
    var root = $id('gc-memory');
    if (!root) return;
    root.textContent = '';
    var m = st.memory;
    if (!m || m.error || !(m.engines || []).length) { root.hidden = true; return; }
    root.hidden = false;
    var budget = (m.device || {}).free_bytes, total = m.total_bytes || 0;
    var pct = budget ? Math.min(100, Math.round(total * 100 / budget)) : 0;
    root.classList.toggle('is-over', !!m.over_budget);
    root.appendChild(h('div', { class: 'gc-mem-head' }, [
      h('span', { class: 'gc-mem-title', text: T('NPU memory') }),
      h('span', { class: 'gc-mem-value', text: budget ? fmt(T('{used} of {free} free'), { used: D.fmtBytes(total), free: D.fmtBytes(budget) }) : D.fmtBytes(total) })
    ]));
    if (budget) {
      root.appendChild(h('div', { class: 'gc-mem-bar', role: 'meter', 'aria-valuemin': '0', 'aria-valuemax': '100',
        'aria-valuenow': String(pct), 'aria-label': T('NPU memory') }, [h('span', { class: 'gc-mem-fill', style: 'width:' + pct + '%' })]));
    }
    if ((m.unknown_models || []).length) {
      root.appendChild(h('p', { class: 'gc-mem-note', text: fmt(T('Not counted (model file missing): {models}'), { models: m.unknown_models.join(', ') }) }));
    }
    var caps = (st.catalog && st.catalog.capabilities) || {};
    if (!caps.engine_key) root.appendChild(h('p', { class: 'gc-mem-note', text: T('This dx_app build does not apply engine options yet; the estimate shows what they will save.') }));
    if (m.over_budget && (m.suggestions || []).length) {
      root.appendChild(h('p', { class: 'gc-mem-tips-title', text: T('Ways to fit') }));
      var list = h('ul', { class: 'gc-mem-tips' });
      m.suggestions.slice(0, 4).forEach(function (s) {
        list.appendChild(h('li', {}, [h('span', { text: suggestionText(s) }),
          h('button', { type: 'button', class: 'btn btn-ghost btn-sm', text: T('Apply'), onclick: function () { applySuggestion(s); } })]));
      });
      root.appendChild(list);
    }
  }

  /* ── inspector / palette / run hooks ── */
  function ctx() {
    return {
      h: h, icon: icon, fmt: fmt, api: api, D: D, state: st, canvas: function () { return st.cv; },
      engine: engineGraph, nodeOf: nodeOf, addFromPalette: addFromPalette, loadExample: loadExample,
      reloadCatalog: loadCatalog, applyPins: applyPins, updateStatus: updateStatus, notify: notify,
      sourceFor: sourceFor, observe: observe, canRun: canRun
    };
  }

  function renderInspector() {
    if (window.GraphInspector) GraphInspector.render($id('gc-inspector-body'), ctx(), st.sel);
  }

  function renderPalette() {
    if (window.GraphPalette) GraphPalette.render($id('gc-palette-list'), ctx());
  }

  async function loadCatalog(refresh) {
    // Task group names come from the same labels as the Models page (app.js loadModels); this page may open first.
    if (typeof S !== 'undefined' && !Object.keys(S.catLabels || {}).length && typeof window.api === 'function') {
      var labels = await window.api('/api/category_labels');
      if (labels && typeof labels === 'object' && !Array.isArray(labels) && !labels.error) S.catLabels = labels;
    }
    var r = await api.catalog(refresh);
    st.catalog = r && Array.isArray(r.models) ? r : { available: false, models: [], examples: [], cpu_ops: [], error: (r && r.error) || 'catalog' };
    st.models = {};
    st.catalog.models.forEach(function (m) { st.models[m.name] = m; });
    st.ops = {};
    (st.catalog.logic_ops || []).forEach(function (o) { st.ops[o.op] = o; });
    renderPalette();
    refreshDisplay();
    updateStatus();
    scheduleValidate();
  }

  /* ── projects ── */
  function saveDraft() {
    try {
      localStorage.setItem(DRAFT_KEY, JSON.stringify({
        project: D.makeProject(st.cv.getGraph(), { name: st.name }, st.cv.view()),
        id: st.projectId, version: st.version, dirty: st.dirty
      }));
    } catch (e) { /* storage full or private mode: the draft is a convenience */ }
  }

  function restoreDraft() {
    var raw = null;
    try { raw = JSON.parse(localStorage.getItem(DRAFT_KEY) || 'null'); } catch (e) { raw = null; }
    if (!raw || !raw.project) return false;
    try {
      loadDoc(D.readAny(raw.project), { id: raw.id, version: raw.version, dirty: raw.dirty });
      return true;
    } catch (e) { return false; }
  }

  function loadDoc(doc, info) {
    var g = doc.graph;
    g.nodes.forEach(function (n) { D.decorate(n, st.models, tr); });
    var placed = doc.placed ? g : st.cv.layout(g);   // only a graph without stored positions is laid out
    placed.edges.forEach(function (e) { e.label = D.edgeLabel(e, tr); });
    st.cv.setGraph(placed, { fit: !doc.view });
    if (doc.view) st.cv.setView(doc.view);
    st.name = (doc.meta && doc.meta.name) || g.name || '';
    $id('gc-name').value = st.name;
    st.projectId = (info && info.id) || null;
    st.version = (info && info.version) || null;
    st.dirty = !!(info && info.dirty);
    st.run = null;
    st.observed = null;
    st.check = null;
    st.memory = null;
    st.sel = { nodes: [], edge: null };
    if (window.GraphRun) GraphRun.reset();
    if (window.GraphLive) GraphLive.renderInputs();
    applyPins();
    renderMemory();
    renderInspector();
    saveDraft();
    refreshProjects();
    scheduleValidate();
    updateStatus();
  }

  function confirmLose() {
    return !st.dirty || window.confirm(T('Discard the unsaved changes to this graph?'));
  }

  function loadExample(id) {
    var ex = ((st.catalog && st.catalog.examples) || []).filter(function (e) { return e.id === id; })[0];
    if (!ex || !confirmLose()) return false;
    loadDoc({ graph: D.fromEngine(ex.graph), meta: { name: ex.name }, view: null, placed: false }, null);
    return true;
  }

  function newGraph() {
    if (!confirmLose()) return;
    loadDoc({ graph: { name: '', nodes: [], edges: [] }, meta: { name: '' }, view: null, placed: true }, null);
  }

  async function refreshProjects() {
    var sel = $id('gc-projects');
    if (!sel) return;
    var r = await api.projects();
    sel.textContent = '';
    sel.appendChild(h('option', { value: '', text: T('Open project…') }));
    (r.projects || []).forEach(function (p) {
      sel.appendChild(h('option', { value: p.id, text: p.name + ' (v' + p.version + ')' }));
    });
    sel.value = st.projectId || '';
    await refreshVersions();
  }

  async function refreshVersions() {
    var sel = $id('gc-versions');
    if (!sel) return;
    sel.textContent = '';
    if (!st.projectId) {
      sel.disabled = true;
      sel.appendChild(h('option', { value: '', text: T('No versions') }));
      return;
    }
    var r = await api.versions(st.projectId);
    sel.disabled = false;
    (r.versions || []).forEach(function (v) {
      var when = typeof fmtTime === 'function' && v.saved_at ? ' · ' + fmtTime(v.saved_at) : '';
      sel.appendChild(h('option', { value: String(v.version), text: fmt(T('Version {n}'), { n: v.version }) + when }));
    });
    sel.value = String(st.version || '');
  }

  async function openProject(id, version) {
    if (!id) return;
    if (!confirmLose()) { $id('gc-projects').value = st.projectId || ''; return; }
    var r = await api.project(id, version);
    if (r.error) { notify(r.error, 'err'); return; }
    try {
      loadDoc(D.readAny(r.project), { id: r.id, version: r.version });
    } catch (e) {
      notify(T('This file is not a Graph Composer project.'), 'err');
    }
  }

  async function save() {
    var g = st.cv.getGraph();
    if (!g.nodes.length) { notify(T('Add a node before saving.'), 'warn'); return; }
    st.name = ($id('gc-name').value || '').trim() || st.name || T('Untitled graph');
    $id('gc-name').value = st.name;
    var r = await api.save(st.projectId, D.makeProject(g, { name: st.name }, st.cv.view()));
    if (r.error) { notify(r.error, 'err'); return; }
    st.projectId = r.id;
    st.version = r.version;
    st.dirty = false;
    saveDraft();
    notify(fmt(T('Saved {name}, version {n}'), { name: r.name, n: r.version }), 'ok');
    await refreshProjects();
    updateStatus();
  }

  async function removeProject() {
    if (!st.projectId || !window.confirm(fmt(T('Delete the project {name} and all its versions?'), { name: st.name }))) return;
    var r = await api.remove(st.projectId);
    if (r.error) { notify(r.error, 'err'); return; }
    st.projectId = null;
    st.version = null;
    st.dirty = true;
    saveDraft();
    await refreshProjects();
    updateStatus();
  }

  function exportJson() {
    var project = D.makeProject(st.cv.getGraph(), { name: st.name }, st.cv.view());
    var blob = new Blob([JSON.stringify(project, null, 2)], { type: 'application/json' });
    var a = h('a', { href: URL.createObjectURL(blob), download: (st.name || 'graph').replace(/[^A-Za-z0-9_-]+/g, '_') + '.graph.json' });
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  }

  function importJson(file) {
    if (!file || !confirmLose()) return;
    var reader = new FileReader();
    reader.onload = function () {
      try {
        loadDoc(D.readAny(JSON.parse(String(reader.result))), { dirty: true });
      } catch (e) {
        notify(T('This file is not a Graph Composer project.'), 'err');
      }
    };
    reader.readAsText(file);
  }

  /* ── page wiring ── */
  function bindToolbar() {
    $id('gc-new').addEventListener('click', newGraph);
    $id('gc-save').addEventListener('click', save);
    $id('gc-delete').addEventListener('click', removeProject);
    $id('gc-export').addEventListener('click', exportJson);
    $id('gc-import').addEventListener('click', function () { $id('gc-import-file').click(); });
    $id('gc-import-file').addEventListener('change', function (e) { importJson(e.target.files[0]); e.target.value = ''; });
    $id('gc-projects').addEventListener('change', function (e) { openProject(e.target.value, null); });
    $id('gc-versions').addEventListener('change', function (e) { openProject(st.projectId, e.target.value); });
    $id('gc-validate').addEventListener('click', validateNow);
    $id('gc-run').addEventListener('click', function () { selectRunTab('once'); if (window.GraphRun) GraphRun.start(); });
    $id('gc-live').addEventListener('click', function () { selectRunTab('live'); if (window.GraphLive) GraphLive.start(); });
    ['once', 'live'].forEach(function (name) {
      var tab = $id('gc-tab-' + name);
      tab.addEventListener('click', function () { selectRunTab(name); });
      tab.addEventListener('keydown', function (e) {
        if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight' && e.key !== 'Home' && e.key !== 'End') return;
        e.preventDefault();
        var next = name === 'once' ? 'live' : 'once';
        if (e.key === 'Home') next = 'once';
        if (e.key === 'End') next = 'live';
        selectRunTab(next);
        $id('gc-tab-' + next).focus();
      });
    });
    $id('gc-name').addEventListener('change', function (e) {
      st.name = e.target.value.trim();
      st.dirty = true;
      saveDraft();
      updateStatus();
    });
    document.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S') && document.querySelector('#page-graph.active')) {
        e.preventDefault();
        save();
      }
    });
  }

  /* The run panel's tabs: Run once and Live (ARIA tabs; arrow keys move between them). */
  function selectRunTab(name) {
    st.runTab = name;
    ['once', 'live'].forEach(function (k) {
      var tab = $id('gc-tab-' + k), on = k === name;
      tab.setAttribute('aria-selected', String(on));
      tab.tabIndex = on ? 0 : -1;
    });
    $id('gc-run-body').hidden = name !== 'once';
    $id('gc-live-body').hidden = name !== 'live';
  }

  /* The page is being left (utils.js nav): a Live stops, the zone editor closes. */
  function leave() {
    if (!st.opened) return;
    if (window.GraphLive) GraphLive.leave();
    var dlg = $id('gc-zone-dialog');
    if (dlg && dlg.open) dlg.close();
  }

  async function open() {
    if (!st.opened) {
      st.opened = true;
      st.lang = curLang();
      bindToolbar();
      st.cv = DXGraphCanvas.create($id('gc-canvas-host'), {
        categories: { source: { slot: 1 }, model: { slot: 3 }, cpu: { slot: 2 }, logic: { slot: 5 } },
        t: tr,
        canConnect: function (from, to, graph) {
          var r = D.canConnect(from, to, st.models, st.ops, graph);
          if (!r.ok) return { ok: false, reason: tr(r.reason) };
          return { ok: true, kind: r.kind, data: r.data, label: D.edgeLabel({ kind: r.kind, data: r.data }, tr) };
        },
        onChange: onGraphChange,
        onSelect: function (sel) { st.sel = sel; renderInspector(); },
        onActivate: function () {
          var f = $id('gc-inspector-body') && $id('gc-inspector-body').querySelector('input, select, button');
          if (f) f.focus();
        },
        onDrop: function (payload) { return specFrom(payload); }
      });
      if (window.GraphRun) GraphRun.mount($id('gc-run-body'), ctx());
      if (window.GraphLive) GraphLive.mount($id('gc-live-body'), ctx());
      selectRunTab(st.runTab);
      if (!restoreDraft()) { renderInspector(); updateStatus(); }
      await refreshProjects();
    } else if (st.lang !== curLang()) {
      refreshLanguage();
    }
    await loadCatalog(false);
  }

  function refreshLanguage() {
    if (!st.opened) return;
    st.lang = curLang();
    st.cv.refreshLanguage();
    refreshDisplay();
    applyPins();
    renderPalette();
    renderMemory();
    renderInspector();
    updateStatus();
    refreshProjects();
    if (window.GraphRun) GraphRun.refreshLanguage();
    if (window.GraphLive) GraphLive.refreshLanguage();
  }

  if (typeof registerLangRefresher === 'function') {
    registerLangRefresher(function () { if (document.querySelector('#page-graph.active')) refreshLanguage(); });
  }

  return {
    open: open, refreshLanguage: refreshLanguage, loadExample: loadExample, validate: validateNow,
    applySuggestion: applySuggestion, canRun: canRun, leave: leave, selectRunTab: selectRunTab,
    state: function () { return st; }, canvas: function () { return st.cv; }, ctx: ctx, h: h, fmt: fmt,
    ensureExample: function (id) { if (st.cv && !st.cv.getGraph().nodes.length) loadExample(id); }
  };
})();
