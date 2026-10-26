/* DX App — Graph Composer inspector: the settings of the selected node or edge, its --check errors, its NPU memory
   and its last run result. A change commits to the canvas on `change` (one undo step per edit).
   A logic block's form is built from its --list-ops schema (type, range, default per param); zones and lines open
   the zone editor (graph-zone-editor.js) on a frame of the block's input.
   Contract: tests/dx_app/test_graph_composer_browser.py */
window.GraphInspector = (function () {
  'use strict';
  var uid = 0;
  var lastRoot = null, lastCtx = null, lastSel = null;
  var samples = null;

  function nextId() { uid += 1; return 'gc-f' + uid; }

  /* dx_app gives a logic op's summary and its params' help in English only; Studio's translations
     (window._DX_GRAPH_OPS_I18N in i18n.js) stand in for them in the page language. `given` is dx_app's text: an entry
     is used only while its English matches it, so a reworded text or an unknown op or param shows dx_app's words. */
  function opText(op, param, what, given) {
    var all = window._DX_GRAPH_OPS_I18N || {}, e = all[op];
    e = e && (param ? e.params && e.params[param] && e.params[param][what] : e.summary);
    if (!e || (given && e.en !== given)) return given;
    var lang = (window.DXI18n && DXI18n.lang) || 'en';
    return e[lang] || e.en || given;
  }

  /* The label of a logic param: Studio's name for it, or dx_app's param name. */
  function paramLabel(n, p) { return (opText((n.data || {}).op, p.name, 'label', null) || p.name) + (p.required ? ' *' : ''); }

  function paramHelp(n, p) { return p.help ? opText((n.data || {}).op, p.name, 'help', p.help) : p.help; }

  function field(c, label, input, help) {
    if (!input.id) input.id = nextId();
    return c.h('div', { class: 'fg gc-fg' }, [c.h('label', { for: input.id, text: label }), input,
      help ? c.h('p', { class: 'gc-help', text: help }) : null]);
  }

  function textInput(c, value, onCommit, attrs) {
    var el = c.h('input', Object.assign({ type: 'text', class: 'input', value: value == null ? '' : String(value) }, attrs || {}));
    el.addEventListener('change', function () { onCommit(el.value.trim(), el); });
    return el;
  }

  function numberInput(c, value, onCommit, attrs) {
    var el = c.h('input', Object.assign({ type: 'number', class: 'input', value: value == null ? '' : String(value) }, attrs || {}));
    el.addEventListener('change', function () {
      if (el.value === '') { onCommit(null); return; }
      var v = Number(el.value);
      if (!isNaN(v)) onCommit(v);
    });
    return el;
  }

  function selectInput(c, options, value, onChange) {
    var el = c.h('select', { class: 'input' }, options.map(function (o) {
      return c.h('option', { value: o.value, text: o.label });
    }));
    el.value = value == null ? '' : String(value);
    el.addEventListener('change', function () { onChange(el.value); });
    return el;
  }

  function checkbox(c, label, checked, onChange) {
    var box = c.h('input', { type: 'checkbox', id: nextId() });
    box.checked = !!checked;
    box.addEventListener('change', function () { onChange(box.checked); });
    return c.h('div', { class: 'gc-check' }, [box, c.h('label', { for: box.id, text: label })]);
  }

  function section(c, title, kids) {
    return c.h('section', { class: 'gc-section' }, [c.h('h3', { class: 'gc-section-title', text: title })].concat(kids));
  }

  function setData(c, id, mutate) {
    var n = c.nodeOf(id);
    if (!n) return;
    var d = c.D.clone(n.data || {});
    mutate(d);
    var shown = c.D.decorate({ id: id, kind: n.kind, data: d }, c.state.models, T);
    c.canvas().updateNode(id, { data: d, sub: shown.sub, icon: shown.icon });
  }

  function edgeOf(c, id) {
    var found = null;
    c.canvas().getGraph().edges.forEach(function (e) { if (e.id === id) found = e; });
    return found;
  }

  function setEdge(c, id, kind, mutate) {
    var e = edgeOf(c, id);
    if (!e) return;
    var d = c.D.clone(e.data || {});
    if (mutate) mutate(d);
    if (kind === 'roi') { d.roi = d.roi || {}; delete d.carry; }
    else if (kind === 'result') { d.carry = 'result'; delete d.roi; delete d.port; }
    else { delete d.roi; delete d.carry; }
    c.canvas().updateEdge(id, { kind: kind, data: d, label: c.D.edgeLabel({ kind: kind, data: d }, T) });
  }

  function list(v) {
    return String(v || '').split(',').map(function (s) { return s.trim(); }).filter(Boolean);
  }

  function parseParam(key, raw) {
    if (key === 'class_names' || key === 'classes' || key === 'class_ids') return list(raw);
    if (raw !== '' && !isNaN(Number(raw))) return Number(raw);
    return raw;
  }

  function errorsFor(c, pred) {
    var errs = ((c.state.check && c.state.check.errors) || []).filter(pred);
    if (!errs.length) return null;
    return section(c, T('Problems'), errs.map(function (e) {
      return c.h('div', { class: 'gc-error', role: 'alert' }, [
        c.h('strong', { text: e.code }), c.h('span', { text: ' ' + e.what }),
        e.how ? c.h('p', { class: 'gc-help', text: '→ ' + e.how }) : null]);
    }));
  }

  function paramsEditor(c, n) {
    var params = (n.data && n.data.params) || {}, rows = [];
    Object.keys(params).forEach(function (k) {
      var v = Array.isArray(params[k]) ? params[k].join(', ') : params[k];
      var input = textInput(c, v, function (raw) {
        setData(c, n.id, function (d) { d.params = d.params || {}; d.params[k] = parseParam(k, raw); });
      }, { 'aria-label': k });
      var rm = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm', 'aria-label': c.fmt(T('Remove {name}'), { name: k }) }, [c.icon('x')]);
      rm.addEventListener('click', function () { setData(c, n.id, function (d) { delete d.params[k]; }); });
      rows.push(c.h('div', { class: 'gc-param' }, [c.h('code', { text: k }), input, rm]));
    });
    var key = c.h('input', { type: 'text', class: 'input', placeholder: T('name, e.g. score_threshold'), 'aria-label': T('Parameter name') });
    var val = c.h('input', { type: 'text', class: 'input', placeholder: T('value'), 'aria-label': T('Parameter value') });
    var add = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm', text: T('Add') });
    add.addEventListener('click', function () {
      var k = key.value.trim();
      if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(k) || val.value.trim() === '') return;
      setData(c, n.id, function (d) { d.params = d.params || {}; d.params[k] = parseParam(k, val.value.trim()); });
    });
    rows.push(c.h('div', { class: 'gc-param gc-param-new' }, [key, val, add]));
    return section(c, T('Parameters'), rows.concat([c.h('p', { class: 'gc-help',
      text: T('Overrides the model config.json for this node. Lists such as class_names are comma separated.') })]));
  }

  function renameField(c, n) {
    var input = textInput(c, n.id, function (v, el) {
      if (v === n.id) return;
      if (!DXGraphCore.ID_RE.test(v)) { c.notify(T('Use letters, digits, _ or -, starting with a letter.'), 'warn'); el.value = n.id; return; }
      if (!DXGraphCore.validId(v)) { c.notify(T('"base" and "events" are reserved: dx_app names its layer files after them. Pick another name.'), 'warn'); el.value = n.id; return; }
      if (!c.canvas().renameNode(n.id, v)) { c.notify(T('Another node already has this name.'), 'warn'); el.value = n.id; }
    }, { maxlength: '32' });
    return field(c, T('Node name'), input);
  }

  function connectField(c, n) {
    if (n.noOutput) return null;
    var g = c.canvas().getGraph();
    var targets = g.nodes.filter(function (m) {
      return m.id !== n.id && !g.edges.some(function (e) { return e.from === n.id && e.to === m.id; });
    });
    if (!targets.length) return null;
    var sel = selectInput(c, [{ value: '', label: T('Connect to…') }].concat(targets.map(function (m) { return { value: m.id, label: m.id }; })), '', function (v) {
      if (!v) return;
      var r = c.canvas().connect(n.id, v);
      if (!r.ok && r.reason) c.notify(r.reason, 'warn');
    });
    return field(c, T('Connect to'), sel, T('The keyboard way to draw an edge from this node.'));
  }

  function memoryLine(c, n) {
    var m = c.state.memory && c.state.memory.nodes && c.state.memory.nodes[n.id];
    if (!m) return null;
    var text = m.bytes ? c.fmt(T('{mb} on the NPU'), { mb: c.D.fmtBytes(m.bytes) })
      : c.fmt(T('Uses the engine of {nodes}'), { nodes: m.shared_with.join(', ') });
    return c.h('p', { class: 'gc-help', text: text });
  }

  function resultSection(c, id) {
    var run = c.state.run, r = run && run.nodes && run.nodes[id];
    var ev = run && run.event_counts && run.event_counts[id];
    if (!r && !ev) return null;
    var lines = [];
    if (r) lines.push(c.h('p', { class: 'gc-help', text: c.fmt(T('{shape} · {frames} frames · {items} results · {crops} crops'),
      { shape: r.shape || '-', frames: r.frames, items: r.items_total, crops: r.crops_total }) }));
    ((r && r.last_records) || []).slice(0, 4).forEach(function (rec) {
      var nums = rec.numbers || {};
      lines.push(c.h('p', { class: 'gc-help', text: c.fmt(T('Last values: {values}'), {
        values: Object.keys(nums).map(function (k) { return k + ' ' + nums[k]; }).join(', ') }) }));
    });
    if (ev) lines.push(c.h('p', { class: 'gc-help', text: c.fmt(T('Events: {events}'), {
      events: Object.keys(ev).map(function (k) { return k + ' ' + ev[k]; }).join(', ') }) }));
    if (!r) return section(c, T('Last run'), lines);
    if (run.node_ms && run.node_ms[id] != null) lines.push(c.h('p', { class: 'gc-help', text: c.fmt(T('{ms} ms per frame'), { ms: run.node_ms[id].toFixed(1) }) }));
    if ((r.last_items || []).length) lines.push(c.h('pre', { class: 'gc-result', text: JSON.stringify(r.last_items, null, 1) }));
    return section(c, T('Last run'), lines);
  }

  function sourceForm(c, n) {
    var d = n.data || {};
    var input = textInput(c, d.uri, function (v) { setData(c, n.id, function (x) { x.uri = v; }); }, { list: 'gc-samples' });
    return [field(c, T('Input'), input, T('An image or video under the dx_app folder, camera:0 or rtsp://… (Run once takes images and videos).'))];
  }

  function modelForm(c, n) {
    var d = n.data || {}, m = c.state.models[d.model] || {};
    var names = Object.keys(c.state.models).sort().filter(function (k) { return c.state.models[k].ready; });
    if (d.model && names.indexOf(d.model) === -1) names.unshift(d.model);
    var model = selectInput(c, names.map(function (k) { return { value: k, label: k }; }), d.model, function (v) {
      setData(c, n.id, function (x) { x.model = v; });
    });
    var out = [field(c, T('Model'), model, m.task ? c.fmt(T('{task} · produces {produces} · takes {consumes}'),
      { task: typeof catText === 'function' ? catText(m.task) : m.task, produces: m.produces,
        consumes: m.consumes === 'either' ? T('frame or crop') : T('full frame') }) : '')];
    var line = memoryLine(c, n);
    if (line) out.push(line);
    out.push(paramsEditor(c, n));
    var track = d.track || null;
    var trackKids = [checkbox(c, T('Track objects across frames (IoU tracker)'), !!track, function (on) {
      setData(c, n.id, function (x) { if (on) x.track = { algo: 'iou', iou: 0.3, max_age: 30 }; else delete x.track; });
    })];
    if (track) {
      trackKids.push(field(c, T('Overlap to keep a track (IoU)'), numberInput(c, track.iou, function (v) {
        setData(c, n.id, function (x) { x.track.iou = v == null ? 0.3 : v; });
      }, { min: '0.01', max: '1', step: '0.05' })));
      trackKids.push(field(c, T('Frames a lost track survives'), numberInput(c, track.max_age, function (v) {
        setData(c, n.id, function (x) { x.track.max_age = v == null ? 30 : Math.max(0, Math.round(v)); });
      }, { min: '0', step: '1' })));
    }
    out.push(section(c, T('Tracking'), trackKids));
    var eng = d.engine || {};
    var buffers = selectInput(c, [{ value: '', label: T('Default (6)') }, { value: '1', label: '1' }, { value: '2', label: '2' },
      { value: '3', label: '3' }, { value: '4', label: '4' }], eng.buffers == null ? '' : String(eng.buffers), function (v) {
      setData(c, n.id, function (x) { x.engine = x.engine || {}; if (v) x.engine.buffers = Number(v); else delete x.engine.buffers; });
    });
    out.push(section(c, T('NPU engine'), [
      field(c, T('Buffers'), buffers, T('Fewer buffers use less NPU memory and may lower throughput.')),
      checkbox(c, T('Share one engine with other nodes of this model'), !!eng.share, function (on) {
        setData(c, n.id, function (x) { x.engine = x.engine || {}; if (on) x.engine.share = true; else delete x.engine.share; });
      })]));
    return out;
  }

  function cpuForm(c, n) {
    var d = n.data || {}, out = [c.h('p', { class: 'gc-help', text: c.fmt(T('Takes the results of: {inputs}'), {
      inputs: (((c.state.catalog && c.state.catalog.cpu_ops) || []).filter(function (o) { return o.op === d.op; })[0] || { inputs: [] }).inputs.join(' + ') }) })];
    if (d.op === 'volume') out.push(paramsEditor(c, n));
    return out;
  }

  /* ── logic blocks: the form comes from the op's --list-ops params ── */
  function setParam(c, id, name, value) {
    setData(c, id, function (d) {
      d.params = d.params || {};
      if (value == null || value === '') delete d.params[name];
      else d.params[name] = value;
    });
  }

  /* The values a text param can take, from its inputs: dx_app's values_by_input names them per input shape
     ("values", or "values_from": "numbers" for the numbers a logic block writes); without it, "count" and those
     numbers. */
  function valueSuggestions(c, n, p) {
    var out = [], g = c.canvas().getGraph(), rows = (p && p.values_by_input) || null;
    function add(k) { if (out.indexOf(k) === -1) out.push(k); }
    if (!rows) add('count');
    g.edges.forEach(function (e) {
      if (e.to !== n.id) return;
      var from = c.nodeOf(e.from), spec = from && from.kind === 'logic' && (c.state.ops || {})[(from.data || {}).op];
      var numbers = (spec && spec.numbers) || [];
      if (!rows) { numbers.forEach(add); return; }
      var shape = from ? c.D.outputOf(from, c.state.models, c.state.ops, g) : '';
      var hit = rows.filter(function (r) { return r.shape === shape; });
      if (!hit.length) { add('count'); return; }
      hit.forEach(function (r) {
        (r.values || []).forEach(add);
        if (r.values_from === 'numbers') numbers.forEach(add);
      });
    });
    if (!out.length) add('count');
    return out;
  }

  function rangeText(c, p) {
    if (p.min != null && p.max != null) return c.fmt(T('{min} to {max}'), { min: p.min, max: p.max });
    if (p.min != null) return c.fmt(p.min_exclusive ? T('more than {min}') : T('at least {min}'), { min: p.min });
    if (p.max != null) return c.fmt(T('at most {max}'), { max: p.max });
    return '';
  }

  function paramField(c, n, p) {
    var params = (n.data && n.data.params) || {}, v = params[p.name], label = paramLabel(n, p), help = paramHelp(n, p);
    if (p.type === 'polygon' || p.type === 'line') return drawnField(c, n, p, v);
    var wrap = paramInput(c, n, p, v, label, help);
    wrap.setAttribute('data-param', p.name);
    return wrap;
  }

  function paramInput(c, n, p, v, label, help) {
    if (p.type === 'choice') {
      var opts = (p.required ? [] : [{ value: '', label: p.default !== undefined && p.default !== ''
        ? c.fmt(T('Default ({value})'), { value: p.default }) : T('Default') }])
        .concat((p.choices || []).map(function (x) { return { value: x, label: x }; }));
      /* A param that "equals" this one (the user op's output equals its input) follows it in the same step. */
      var followers = (((c.state.ops || {})[(n.data || {}).op] || {}).params || [])
        .filter(function (q) { return q.equals === p.name; }).map(function (q) { return q.name; });
      return field(c, label, selectInput(c, opts, v == null ? '' : v, function (x) {
        setData(c, n.id, function (d) {
          d.params = d.params || {};
          [p.name].concat(followers).forEach(function (k) { if (x) d.params[k] = x; else delete d.params[k]; });
        });
      }), help);
    }
    if (p.type === 'number') {
      var attrs = { step: p.step != null ? String(p.step) : 'any' };
      if (p.min != null) attrs.min = String(p.min);
      if (p.max != null) attrs.max = String(p.max);
      if (p.default !== undefined) attrs.placeholder = String(p.default);
      return field(c, label, numberInput(c, v, function (x) {
        if (x != null && p.min != null && x < p.min) x = p.min;
        if (x != null && p.max != null && x > p.max) x = p.max;
        setParam(c, n.id, p.name, x);
      }, attrs), [rangeText(c, p), help].filter(Boolean).join(' · '));
    }
    if (p.type === 'text_list') {
      return field(c, label, textInput(c, Array.isArray(v) ? v.join(', ') : '', function (raw) {
        var items = list(raw);
        setParam(c, n.id, p.name, items.length ? items : null);
      }), help || T('Comma separated. Empty: all.'));
    }
    var attrs2 = p.default !== undefined && p.default !== '' ? { placeholder: String(p.default) } : {};
    if (n.data.op === 'condition' && p.name === 'value') {
      attrs2.list = 'gc-value-suggest-' + n.id;
    }
    var input = textInput(c, v == null ? '' : v, function (raw) { setParam(c, n.id, p.name, raw || null); }, attrs2);
    var wrap = field(c, label, input, help);
    if (attrs2.list) {
      wrap.appendChild(c.h('datalist', { id: attrs2.list }, valueSuggestions(c, n, p).map(function (k) { return c.h('option', { value: k }); })));
    }
    return wrap;
  }

  function drawnField(c, n, p, v) {
    var cv = c.h('canvas', { class: 'gc-zone-preview', 'aria-hidden': 'true' });
    var s = window.GraphZoneGeom ? GraphZoneGeom.shapeFrom(v) : null;
    var dir = ((n.data && n.data.params) || {}).direction;
    var edit = c.h('button', { type: 'button', class: 'btn btn-neutral btn-sm gc-zone-edit',
      'aria-label': c.fmt(T('Edit {param} on the frame'), { param: paramLabel(n, p).replace(/ \*$/, '') }) }, [c.icon('image'), c.h('span', { text: ' ' + T('Edit on the frame…') })]);
    edit.addEventListener('click', function () {
      GraphZoneEditor.open({ nodeId: n.id, param: p, frameUri: c.sourceFor(n.id), ctx: c });
    });
    setTimeout(function () { if (window.GraphZoneEditor && cv.isConnected) GraphZoneEditor.preview(cv, p, v, dir); }, 0);
    return c.h('div', { class: 'fg gc-fg gc-drawn', 'data-param': p.name }, [c.h('span', { class: 'gc-drawn-label', text: paramLabel(n, p) }),
      cv, c.h('p', { class: 'gc-help', text: s ? c.fmt(T('{n} points'), { n: s.points.length }) : T('Not drawn yet') }), edit]);
  }

  function acceptsText(spec) {
    var seen = [];
    (spec.inputs.accepts || []).forEach(function (a) {
      var t = a.shape + (a.per_crop ? ' ' + T('per crop') : '');
      if (seen.indexOf(t) === -1) seen.push(t);
    });
    return seen.join(', ');
  }

  /* ── a gallery block: build its gallery .bin from an image folder (POST /api/graph/gallery/build, polled) ──
     One build at a time (the server holds the NPU for it). The form keeps what was typed across re-renders; a finished
     build sets the block's gallery param to the file it wrote (one undo step). */
  var GALLERY_POLL_MS = 1000, GALLERY_POLL_FAILURES = 3;
  var gallery = null;               // {nodeId, jobId, state: running|done|failed, elapsed, result, response, failures}
  var galleryForm = {};             // nodeId -> {folder, model, name}

  function errText(r) {
    return (typeof translatedError === 'function' ? translatedError(r) : (r && r.error)) || T('The gallery build failed.');
  }

  /* The model of the block feeding the gallery block: the embedding its vectors come from. */
  function feedingModel(c, n) {
    var model = '';
    c.canvas().getGraph().edges.forEach(function (e) {
      var from = e.to === n.id && c.nodeOf(e.from);
      if (!model && from && from.kind === 'model') model = (from.data && from.data.model) || '';
    });
    return model;
  }

  function galleryStatus(c) {
    if (!gallery) return null;
    if (gallery.state === 'running') {
      return c.h('p', { class: 'gc-help gc-gallery-status', role: 'status' }, [c.h('span', { class: 'spin', 'aria-hidden': 'true' }),
        c.h('span', { text: ' ' + T('Building the gallery…') + (gallery.elapsed != null ? ' ' + c.fmt(T('{s} s'), { s: gallery.elapsed }) : '') })]);
    }
    if (gallery.state === 'done') {
      return c.h('p', { class: 'gc-help gc-gallery-status', role: 'status', text: c.fmt(T('Gallery built: {people} people, {images} images'),
        { people: gallery.result.people, images: gallery.result.images }) });
    }
    return c.h('p', { class: 'gc-error gc-gallery-status', role: 'alert', text: errText(gallery.response) });
  }

  function rerender() {
    if (lastRoot && lastCtx) render(lastRoot, lastCtx, lastSel);
  }

  function pollGallery(c, job) {
    setTimeout(function () {
      if (gallery !== job) return;
      c.api.galleryPoll(job.jobId).then(function (r) {
        if (gallery !== job) return;
        if (r && r.state === 'running') {
          job.failures = 0;
          job.elapsed = r.elapsed;
        } else if (r && r.state === 'done') {
          job.state = 'done';
          job.result = r;
          var n = c.nodeOf(job.nodeId);
          if (n && n.kind === 'logic' && (n.data || {}).op === 'gallery') { setParam(c, job.nodeId, 'gallery', r.gallery); return; }
        } else if (r && (r.state === 'failed' || r.error_key === 'unknown_job' || ++job.failures >= GALLERY_POLL_FAILURES)) {
          job.state = 'failed';
          job.response = r;
        }
        rerender();
        if (job.state === 'running') pollGallery(c, job);
      });
    }, GALLERY_POLL_MS);
  }

  function gallerySection(c, n) {
    var form = galleryForm[n.id] = galleryForm[n.id] || { folder: '', model: feedingModel(c, n), name: '' };
    function input(key, attrs) {
      var el = c.h('input', Object.assign({ type: 'text', class: 'input', value: form[key] }, attrs || {}));
      el.addEventListener('input', function () { form[key] = el.value; });
      return el;
    }
    var mine = gallery && gallery.nodeId === n.id, running = !!(gallery && gallery.state === 'running');
    var build = c.h('button', { type: 'button', class: 'btn btn-neutral btn-sm', text: T('Build gallery') });
    build.disabled = running;
    build.addEventListener('click', function () {
      var body = { folder: form.folder.trim(), model: form.model.trim() };
      if (form.name.trim()) body.name = form.name.trim();
      var job = gallery = { nodeId: n.id, jobId: null, state: 'running', elapsed: null, failures: 0 };
      rerender();
      c.api.galleryBuild(body).then(function (r) {
        if (gallery !== job) return;
        if (!r || r.error || !r.job_id) { job.state = 'failed'; job.response = r; rerender(); return; }
        job.jobId = r.job_id;
        pollGallery(c, job);
      });
    });
    var row = [build];
    if (mine && running) {
      var stop = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm', text: T('Stop') });
      stop.disabled = !gallery.jobId;
      stop.addEventListener('click', function () { if (gallery && gallery.jobId) c.api.galleryStop(gallery.jobId); stop.disabled = true; });
      row.push(stop);
    }
    var kids = [
      field(c, T('Image folder'), input('folder'),
        T('A folder under the dx_app, sample or outputs folders. One subfolder per person names its images after the subfolder; images directly in the folder are named after their files.')),
      field(c, T('Embedding model'), input('model')),
      field(c, T('Gallery name (optional)'), input('name')),
      c.h('div', { class: 'gc-gallery-actions' }, row)
    ];
    if (mine) kids.push(galleryStatus(c));
    var sec = section(c, T('Build a gallery from an image folder'), kids);
    sec.classList.add('gc-gallery-build');
    return sec;
  }

  function logicForm(c, n) {
    var d = n.data || {}, spec = (c.state.ops || {})[d.op], out = [];
    if (!spec) {
      out.push(c.h('p', { class: 'gc-help', text: T('This dx_app build does not list this block; its params are edited as text.') }));
      out.push(paramsEditor(c, n));
      return out;
    }
    if (spec.summary) out.push(c.h('p', { class: 'gc-help', text: opText(d.op, null, 'summary', spec.summary) }));
    out.push(c.h('p', { class: 'gc-help', text: c.fmt(T('Takes {inputs} · hands on {output}'), {
      inputs: acceptsText(spec), output: spec.output === 'same' ? (c.D.outputOf(n, c.state.models, c.state.ops, c.canvas().getGraph()) || T('what it takes'))
        : 'records' }) }));
    if (spec.events && spec.events.length) {
      out.push(c.h('p', { class: 'gc-help', text: c.fmt(T('Fires: {events}'), {
        events: spec.events.map(function (e) { return e === '<event>' ? ((d.params || {}).event || n.id) : e; }).join(', ') }) }));
    }
    var untracked = c.D.untrackedFeeds(c.canvas().getGraph(), n.id, c.state.ops);
    if (untracked.length) {
      var fix = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm', text: c.fmt(T('Track objects on {nodes}'), { nodes: untracked.join(', ') }) });
      fix.addEventListener('click', function () {
        untracked.forEach(function (id, i) {
          var m = c.nodeOf(id);
          if (!m) return;
          var data = c.D.clone(m.data || {});
          data.track = { algo: 'iou', iou: 0.3, max_age: 30 };
          c.canvas().updateNode(id, { data: data }, { commit: i === untracked.length - 1 });
        });
      });
      out.push(c.h('div', { class: 'gc-warn', role: 'note' }, [c.h('p', { text: T('This block needs track ids; the detector feeding it does not track.') }), fix]));
    }
    if (d.op === 'user') {
      out.push(c.h('p', { class: 'gc-help gc-user-logic', text: c.fmt(T('Studio runs this block as a pass-through. An exported project gets a function stub named {name} where you write the logic.'),
        { name: (d.params && d.params.name) || 'my_logic' }) }));
    }
    var fields = spec.params.map(function (p) { return paramField(c, n, p); });
    if (fields.length) out.push(section(c, T('Settings'), fields));
    if (d.op === 'gallery') out.push(gallerySection(c, n));
    return out;
  }

  function nodeView(c, n) {
    var kinds = { source: T('Source'), cpu: T('CPU op'), model: T('Model'), logic: T('Logic block') };
    var kids = [c.h('div', { class: 'gc-insp-head' }, [c.icon(n.icon || 'circle'),
      c.h('strong', { text: n.id }), c.h('span', { class: 'gc-help', text: kinds[n.kind] || '' })]), renameField(c, n)];
    kids = kids.concat(n.kind === 'source' ? sourceForm(c, n) : n.kind === 'cpu' ? cpuForm(c, n)
      : n.kind === 'logic' ? logicForm(c, n) : modelForm(c, n));
    kids.push(connectField(c, n));
    kids.push(errorsFor(c, function (e) { return e.node === n.id; }));
    kids.push(resultSection(c, n.id));
    var del = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm gc-danger', text: T('Delete node') });
    del.addEventListener('click', function () { c.canvas().select({ nodes: [n.id] }); c.canvas().remove(); });
    kids.push(del);
    return kids;
  }

  function edgeView(c, e) {
    var g = c.canvas().getGraph(), map = {};
    g.nodes.forEach(function (n) { map[n.id] = n; });
    var kinds = c.D.edgeKinds(map[e.from], map[e.to], c.state.models, c.state.ops);
    if (kinds.indexOf(e.kind) === -1) kinds.unshift(e.kind);
    var names = { frame: T('Whole frame'), roi: T('One run per box (ROI crop)'),
      result: (map[e.to] || {}).kind === 'logic' ? T('Results to a logic block') : T('Results to a CPU op') };
    var kids = [c.h('div', { class: 'gc-insp-head' }, [c.icon('graph'), c.h('strong', { text: e.from + ' → ' + e.to })]),
      field(c, T('Connection'), selectInput(c, kinds.map(function (k) { return { value: k, label: names[k] || k }; }), e.kind,
        function (k) { setEdge(c, e.id, k); }))];
    if (e.kind === 'roi') {
      var r = (e.data && e.data.roi) || {};
      var set = function (key, v) {
        setEdge(c, e.id, 'roi', function (d) {
          d.roi = d.roi || {};
          if (v == null || v === '' || (Array.isArray(v) && !v.length)) delete d.roi[key]; else d.roi[key] = v;
        });
      };
      kids.push(section(c, T('Crops'), [
        field(c, T('Classes'), textInput(c, (r.classes || []).join(', '), function (v) { set('classes', list(v)); }), T('Comma separated, e.g. person, car. Empty: every box.')),
        field(c, T('Minimum score'), numberInput(c, r.min_score, function (v) { set('min_score', v); }, { min: '0', max: '1', step: '0.05' })),
        field(c, T('Minimum area (px²)'), numberInput(c, r.min_area, function (v) { set('min_area', v); }, { min: '0', step: '1' })),
        field(c, T('Padding (share of the box per side)'), numberInput(c, r.pad, function (v) { set('pad', v); }, { min: '0', max: '1', step: '0.05' })),
        field(c, T('At most this many boxes'), numberInput(c, r.max, function (v) { set('max', v == null ? null : Math.max(1, Math.round(v))); }, { min: '1', step: '1' })),
        field(c, T('Alignment'), selectInput(c, [{ value: '', label: T('None') }, { value: 'face5', label: T('Five face landmarks (face5)') }],
          r.align || '', function (v) { set('align', v); }))]));
    }
    var fm = c.state.models[((map[e.from] || {}).data || {}).model] || {};
    var ports = Object.keys(fm.ports || {});
    if (ports.length && e.kind !== 'result') {
      kids.push(field(c, T('Output'), selectInput(c, [{ value: '', label: T('Primary output') }].concat(ports.map(function (p) {
        return { value: p, label: p + ' (' + fm.ports[p] + ')' };
      })), (e.data && e.data.port) || '', function (v) {
        setEdge(c, e.id, e.kind, function (d) { if (v) d.port = v; else delete d.port; });
      })));
    }
    kids.push(errorsFor(c, function (x) { return x.edge === e.id; }));
    var del = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm gc-danger', text: T('Delete connection') });
    del.addEventListener('click', function () { c.canvas().select({ edge: e.id }); c.canvas().remove(); });
    kids.push(del);
    return kids;
  }

  function emptyView(c) {
    var g = c.canvas().getGraph();
    var kids = [c.h('p', { class: 'gc-help', text: g.nodes.length ? T('Select a node or a connection to edit it.')
      : T('Start from an example in the palette, or add a source and a model.') })];
    var general = c.D.pins(c.state.check, null, null, T).general;
    if (general.length) kids.push(errorsFor(c, function (e) { return !e.node && !e.edge; }));
    return kids;
  }

  function ensureSamples() {
    if (samples || typeof api !== 'function') return;
    samples = [];
    Promise.all([api('/api/images'), api('/api/videos')]).then(function (r) {
      samples = [].concat(Array.isArray(r[0]) ? r[0] : [], Array.isArray(r[1]) ? r[1] : []);
      var dl = document.getElementById('gc-samples');
      if (!dl) return;
      dl.textContent = '';
      samples.forEach(function (s) { var o = document.createElement('option'); o.value = s; dl.appendChild(o); });
    });
  }

  function render(root, c, sel) {
    if (!root) return;
    lastRoot = root;
    lastCtx = c;
    lastSel = sel;
    uid = 0;          // the same form gets the same ids, so focus survives a re-render
    ensureSamples();
    var focusedId = document.activeElement && root.contains(document.activeElement) ? document.activeElement.id : null;
    root.textContent = '';
    var kids;
    if (sel && sel.nodes && sel.nodes.length === 1 && c.nodeOf(sel.nodes[0])) kids = nodeView(c, c.nodeOf(sel.nodes[0]));
    else if (sel && sel.nodes && sel.nodes.length > 1) kids = [c.h('p', { class: 'gc-help', text: c.fmt(T('{n} nodes selected'), { n: sel.nodes.length }) })];
    else if (sel && sel.edge && edgeOf(c, sel.edge)) kids = edgeView(c, edgeOf(c, sel.edge));
    else kids = emptyView(c);
    kids.forEach(function (k) { if (k) root.appendChild(k); });
    if (focusedId && document.getElementById(focusedId)) document.getElementById(focusedId).focus();
  }

  if (typeof registerLangRefresher === 'function') {
    registerLangRefresher(function () {
      if (lastRoot && lastCtx && document.querySelector('#page-graph.active')) render(lastRoot, lastCtx, lastSel);
    });
  }

  return { render: render };
})();
