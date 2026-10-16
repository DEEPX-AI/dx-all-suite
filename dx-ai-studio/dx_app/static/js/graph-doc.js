/* DX App — Graph Composer document model (pure, no DOM).

   Converts between dx_app's graph JSON (dx_app src/cpp_example/multi_model_graph/README.md) and the canvas graph of
   shared/static/dx-graph-canvas.js, gives a first answer on which connections make sense (dx_app's --check has the
   last word), and reads/writes the Studio project file {schema: 1, graph, layout, meta}.
   Logic blocks are {"type": "logic", "op", "params"} nodes; what each op takes and hands on comes from dx_app's
   --list-ops --json (`ops`: op name -> {inputs: {min, max, accepts: [{shape, per_crop}]}, output: same|records,
   tracking, events, numbers, params}; dx_app/core/graph_ops.py).
   Strings it returns are English dictionary keys listed in STRINGS; the page translates them.
   Node-tested: tests/dx_app/test_graph_doc.py */
(function (root) {
  'use strict';
  var SCHEMA = 1;
  var CROPPABLE = { boxes: true, obboxes: true, instances: true };
  var TASK_IDS = {
    object_detection: 'od', mainbody_detection: 'mainbody', oriented_object_detection: 'obb', instance_segmentation: 'iseg',
    semantic_segmentation: 'seg', depth_estimation: 'depth', pose_estimation: 'pose',
    image_classification: 'cls', face_detection: 'face', face_landmark: 'landmark', face_recognition: 'face_id',
    person_attribute: 'attr', person_reid: 'reid', super_resolution: 'sr', image_denoising: 'denoise',
    low_light_enhancement: 'enhance', hand_detection: 'palm', hand_landmark: 'hand'
  };
  var STRINGS = [
    'A source has no input', 'A CPU op ends a branch', 'A CPU op takes results from models',
    'This model does not take a full frame',
    'This model needs a full frame; boxes can only feed a model that takes crops',
    'This model takes crops, and an image is a full frame',
    'Only boxes (as crops) or an image can feed another model',
    'Source', 'CPU op', 'ROI', 'result', 'port', 'error', 'not installed', 'shared',
    'Broken file', 'Needs a newer DX-RT', 'Unknown model',
    'A logic block takes results, not frames', 'This logic block does not take this kind of result',
    'This logic block takes no more inputs', 'Only a block that hands on boxes can feed a model, as crops',
    'Logic', 'Events: {n}'
  ];
  /* A new block's drawn params, as fractions 0..1 of the frame (dx_app's coordinates): a centred rectangle, a line
     across the middle. */
  var DEFAULT_ZONE = [0.25, 0.25, 0.75, 0.25, 0.75, 0.75, 0.25, 0.75];
  var DEFAULT_LINE = [0.1, 0.5, 0.9, 0.5];
  var LOGIC_ICONS = { filter: 1, zone: 1, line: 1, count: 1, dwell: 1, condition: 1, gallery: 1, user: 1 };
  /* --check's `unusable` states: the model file is there (or the name is not) but dx_app cannot use it. */
  var UNUSABLE = {
    invalid: { kind: 'missing', text: 'Broken file' },
    unloadable: { kind: 'missing', text: 'Needs a newer DX-RT' },
    unknown: { kind: 'error', text: 'Unknown model' }
  };

  function clone(v) { return JSON.parse(JSON.stringify(v)); }
  function edgeId(from, to) { return from + '->' + to; }
  function id(k) { return k; }

  function kindOf(n) { return n.type === 'source' ? 'source' : n.type === 'cpu' ? 'cpu' : n.type === 'logic' ? 'logic' : 'model'; }
  function edgeKind(d) { return d && d.roi ? 'roi' : d && d.carry === 'result' ? 'result' : 'frame'; }

  function fromEngine(engine, layout) {
    var pos = (layout && layout.nodes) || {};
    return {
      name: engine.name || '',
      nodes: (engine.nodes || []).map(function (n) {
        var data = clone(n), p = pos[n.id];
        delete data.id;
        return { id: n.id, kind: kindOf(n), x: p ? p.x : 0, y: p ? p.y : 0, data: data };
      }),
      edges: (engine.edges || []).map(function (e) {
        var data = clone(e);
        delete data.from;
        delete data.to;
        return { id: edgeId(e.from, e.to), from: e.from, to: e.to, kind: edgeKind(data), data: data };
      })
    };
  }

  /* dx_app graph JSON. Node keys keep dx_app's order: id, type, uri, model, op, params, track, engine. */
  function toEngine(graph, name) {
    var nodes = graph.nodes.map(function (n) {
      var d = n.data || {}, out = { id: n.id };
      if (n.kind === 'source') { out.type = 'source'; out.uri = d.uri || ''; }
      else if (n.kind === 'cpu') { out.type = 'cpu'; out.op = d.op; }
      else if (n.kind === 'logic') { out.type = 'logic'; out.op = d.op; }
      else out.model = d.model;
      if (d.params && Object.keys(d.params).length) out.params = clone(d.params);
      if (n.kind === 'model' && d.track) out.track = clone(d.track);
      if (n.kind === 'model' && d.engine && Object.keys(d.engine).length) out.engine = clone(d.engine);
      return out;
    });
    var edges = graph.edges.map(function (e) {
      var d = e.data || {}, out = { from: e.from, to: e.to };
      if (e.kind === 'roi') out.roi = clone(d.roi || {});
      if (e.kind === 'result') out.carry = 'result';
      if (d.port && e.kind !== 'result') out.port = d.port;
      return out;
    });
    return { version: 1, name: name || graph.name || 'graph', nodes: nodes, edges: edges };
  }

  function nodeIn(graph, id) {
    var found = null;
    ((graph && graph.nodes) || []).forEach(function (n) { if (n.id === id) found = n; });
    return found;
  }

  function inEdges(graph, id) {
    return ((graph && graph.edges) || []).filter(function (e) { return e.to === id; });
  }

  /* What node `n` hands on over a result or ROI edge, and whether once per crop: {shape, perCrop}. A model hands on
     its `produces`, per crop when an ROI edge feeds it; a logic op its input's shape ("same") or "records", always
     for the whole frame; a cpu op records. shape '' means unknown here (--check decides). */
  function handsOn(n, models, ops, graph, depth) {
    var d = n.data || {};
    if (n.kind === 'source') return { shape: 'frame', perCrop: false };
    if (n.kind === 'cpu') return { shape: 'records', perCrop: false };
    if (n.kind === 'model') {
      return { shape: ((models || {})[d.model] || {}).produces || '',
        perCrop: inEdges(graph, n.id).some(function (e) { return e.kind === 'roi' || !!(e.data && e.data.roi); }) };
    }
    var spec = (ops || {})[d.op];
    if (!spec) return { shape: '', perCrop: false };
    if (spec.output !== 'same') return { shape: 'records', perCrop: false };
    var src = inEdges(graph, n.id)[0], from = src && nodeIn(graph, src.from);
    if (!from || (depth || 0) > 64) return { shape: '', perCrop: false };
    return { shape: handsOn(from, models, ops, graph, (depth || 0) + 1).shape, perCrop: false };
  }

  function outputOf(n, models, ops, graph) { return handsOn(n, models, ops, graph).shape; }

  function takes(spec, h) {
    return (spec.inputs.accepts || []).some(function (a) { return a.shape === h.shape && !!a.per_crop === !!h.perCrop; });
  }

  /* Edge kinds into a logic node: a result edge when the op accepts what `from` hands on. */
  function logicKinds(from, to, models, ops, graph) {
    if (from.kind === 'source') return [];
    var spec = (ops || {})[(to.data || {}).op];
    if (!spec) return ['result'];
    if (graph && inEdges(graph, to.id).length >= ((spec.inputs && spec.inputs.max) || 1)) return [];
    var h = handsOn(from, models, ops, graph);
    return h.shape === '' || takes(spec, h) ? ['result'] : [];
  }

  /* Edge kinds dx_app allows between two nodes, best first: [] when none. `models` maps a model name to its
     --list-models entry and `ops` a logic op to its --list-ops entry; an unknown model allows a plain edge and an
     unknown op a result edge, leaving the verdict to --check. `graph` (the canvas graph) tells what reaches a node
     and counts a logic node's inputs. */
  function edgeKinds(from, to, models, ops, graph) {
    models = models || {};
    if (to.kind === 'source' || from.kind === 'cpu') return [];
    if (to.kind === 'logic') return logicKinds(from, to, models, ops, graph);
    if (to.kind === 'cpu') return from.kind === 'model' ? ['result'] : [];
    var tm = models[(to.data || {}).model] || {};
    var crops = tm.consumes === 'either' || tm.consumes === 'roi', frames = tm.consumes !== 'roi';
    if (from.kind === 'logic') {
      var out = outputOf(from, models, ops, graph);
      return out === '' || CROPPABLE[out] ? (tm.consumes ? (crops ? ['roi'] : []) : ['roi']) : [];
    }
    if (from.kind === 'source') return frames ? ['frame'] : [];
    var fm = models[(from.data || {}).model] || {};
    if (!fm.produces || !tm.consumes) return ['frame'];
    if (CROPPABLE[fm.produces]) return crops ? ['roi'] : [];
    if (fm.produces === 'image') return frames ? ['frame'] : [];
    return [];
  }

  function canConnect(from, to, models, ops, graph) {
    var kinds = edgeKinds(from, to, models || {}, ops, graph);
    if (kinds.length) {
      var kind = kinds[0];
      return { ok: true, kind: kind, data: kind === 'roi' ? { roi: {} } : kind === 'result' ? { carry: 'result' } : {} };
    }
    if (to.kind === 'source') return { ok: false, reason: 'A source has no input' };
    if (from.kind === 'cpu') return { ok: false, reason: 'A CPU op ends a branch' };
    if (to.kind === 'logic') {
      if (from.kind === 'source') return { ok: false, reason: 'A logic block takes results, not frames' };
      var spec = (ops || {})[(to.data || {}).op];
      if (spec && graph && inEdges(graph, to.id).length >= ((spec.inputs && spec.inputs.max) || 1)) {
        return { ok: false, reason: 'This logic block takes no more inputs' };
      }
      return { ok: false, reason: 'This logic block does not take this kind of result' };
    }
    if (from.kind === 'logic') {
      if (to.kind === 'cpu') return { ok: false, reason: 'A CPU op takes results from models' };
      return { ok: false, reason: 'Only a block that hands on boxes can feed a model, as crops' };
    }
    if (to.kind === 'cpu') return { ok: false, reason: 'A CPU op takes results from models' };
    if (from.kind === 'source') return { ok: false, reason: 'This model does not take a full frame' };
    var fm = (models || {})[(from.data || {}).model] || {};
    if (CROPPABLE[fm.produces]) return { ok: false, reason: 'This model needs a full frame; boxes can only feed a model that takes crops' };
    if (fm.produces === 'image') return { ok: false, reason: 'This model takes crops, and an image is a full frame' };
    return { ok: false, reason: 'Only boxes (as crops) or an image can feed another model' };
  }

  function edgeLabel(edge, t) {
    var tr = t || id, d = edge.data || {};
    if (edge.kind === 'result') return tr('result');
    if (edge.kind === 'roi') {
      var r = d.roi || {}, parts = [];
      if (r.classes && r.classes.length) parts.push(r.classes.join(', '));
      if (r.align) parts.push(r.align);
      if (r.max) parts.push('≤' + r.max);
      return tr('ROI') + (parts.length ? ' · ' + parts.join(' · ') : '');
    }
    return d.port ? tr('port') + ' ' + d.port : '';
  }

  /* Display fields the canvas draws: label, sub, category (colour), icon, ports. */
  function decorate(n, models, t) {
    var tr = t || id, d = n.data || {};
    n.label = n.id;
    n.noInput = n.kind === 'source';
    n.noOutput = n.kind === 'cpu';
    if (n.kind === 'source') { n.category = 'source'; n.icon = 'camera'; n.sub = tr('Source'); }
    else if (n.kind === 'cpu') { n.category = 'cpu'; n.icon = 'cpu'; n.sub = tr('CPU op') + ' · ' + (d.op || ''); }
    else if (n.kind === 'logic') {
      n.category = 'logic';
      n.icon = LOGIC_ICONS[d.op] ? 'logic-' + d.op : 'puzzle';
      n.sub = tr('Logic') + ' · ' + (d.op === 'user' && d.params && d.params.name ? d.params.name : d.op || '');
    }
    else {
      var m = (models || {})[d.model] || {};
      n.category = 'model';
      n.icon = m.task ? 'task-' + m.task : 'cpu';
      n.sub = d.model || '';
    }
    return n;
  }

  /* A new logic node's params: what the op requires — a starting shape for a polygon or a line, the first choice of
     a required choice, "my_logic" as a required name. Optional params stay out (dx_app's defaults apply, and the
     inspector shows them). */
  function logicDefaults(spec) {
    var out = {};
    ((spec && spec.params) || []).forEach(function (p) {
      if (p.type === 'polygon') out[p.name] = DEFAULT_ZONE.slice();
      else if (p.type === 'line') out[p.name] = DEFAULT_LINE.slice();
      else if (p.required && p.type === 'choice' && (p.choices || []).length) out[p.name] = p.choices[0];
      else if (p.required && p.type === 'text' && p.name === 'name') out[p.name] = 'my_logic';
    });
    return out;
  }

  /* Model nodes that feed boxes to logic node `id` (directly or through other logic nodes) without tracking; empty
     when the op does not need track ids. */
  function untrackedFeeds(graph, id, ops) {
    var seen = {}, out = [];
    var spec = (ops || {})[((nodeIn(graph, id) || {}).data || {}).op];
    if (!spec || !spec.tracking) return out;
    (function walk(nid) {
      inEdges(graph, nid).forEach(function (e) {
        if (seen[e.from]) return;
        seen[e.from] = true;
        var f = nodeIn(graph, e.from);
        if (!f) return;
        if (f.kind === 'logic') walk(f.id);
        else if (f.kind === 'model' && !(f.data || {}).track) out.push(f.id);
      });
    })(id);
    return out;
  }

  function suggestId(model, models) {
    var m = (models || {})[model] || {};
    return TASK_IDS[m.task] || String(model || 'node').split(/[_-]/)[0];
  }

  function makeProject(graph, meta, view) {
    var layout = { nodes: {}, view: view || null };
    graph.nodes.forEach(function (n) { layout.nodes[n.id] = { x: n.x, y: n.y }; });
    var m = clone(meta || {});
    return { schema: SCHEMA, graph: toEngine(graph, m.name), layout: layout, meta: m };
  }

  /* A Studio project, or a bare dx_app graph (an example file, a graph written by hand). */
  function readAny(json) {
    if (json && json.schema === SCHEMA && json.graph && Array.isArray(json.graph.nodes)) {
      var layout = json.layout || {};
      var g = fromEngine(json.graph, layout);
      var placed = g.nodes.every(function (n) { return layout.nodes && layout.nodes[n.id]; });
      return { graph: g, meta: clone(json.meta || {}), view: layout.view || null, placed: placed && g.nodes.length > 0 };
    }
    if (json && Array.isArray(json.nodes)) {
      return { graph: fromEngine(json), meta: { name: json.name || '' }, view: null, placed: false };
    }
    throw new Error('Not a Graph Composer project or a dx_app graph');
  }

  function fmtBytes(b) {
    if (b == null) return '';
    var mb = b / 1048576;
    return mb >= 1024 ? (mb / 1024).toFixed(2) + ' GiB' : Math.round(mb) + ' MB';
  }

  function addBadge(map, nodeId, badge) {
    var list = map[nodeId] = map[nodeId] || [];
    if (!list.some(function (b) { return b.kind === badge.kind; })) list.push(badge);
  }

  /* A node's data with a memory suggestion's patch applied ({engine, params}: a value sets the key, null removes it).
     The input is not changed. */
  function applyPatch(data, patch) {
    var out = clone(data || {});
    Object.keys(patch || {}).forEach(function (k) {
      if (patch[k] === null) delete out[k];
      else out[k] = clone(patch[k]);
    });
    return out;
  }

  /* Canvas pins from a --check result, memory estimate and run result. An edge error is 'error', or
     {status: 'error', message} when dx_app said what is wrong (the canvas announces the message). */
  function pins(check, memory, run, t) {
    var tr = t || id, badges = {}, edges = {}, general = [], tints = {}, edgeMsgs = {};
    var unusable = (check && check.unusable) || {};
    Object.keys(unusable).forEach(function (nid) {
      var u = UNUSABLE[unusable[nid]];
      if (u) addBadge(badges, nid, { kind: u.kind, text: tr(u.text) });
    });
    ((check && check.errors) || []).forEach(function (e) {
      if (e.node) addBadge(badges, e.node, { kind: 'error', text: tr('error') });
      else if (e.edge) {
        if (e.what) (edgeMsgs[e.edge] = edgeMsgs[e.edge] || []).push(String(e.what));
        else edgeMsgs[e.edge] = edgeMsgs[e.edge] || [];
      } else general.push(e);
    });
    Object.keys(edgeMsgs).forEach(function (eid) {
      edges[eid] = edgeMsgs[eid].length ? { status: 'error', message: edgeMsgs[eid].join('; ') } : 'error';
    });
    ((check && check.missing) || []).forEach(function (nid) { addBadge(badges, nid, { kind: 'missing', text: tr('not installed') }); });
    var mem = (memory && memory.nodes) || {};
    Object.keys(mem).forEach(function (nid) {
      var m = mem[nid];
      if (m.bytes) addBadge(badges, nid, { kind: 'mem', text: fmtBytes(m.bytes) });
      else if (m.shared_with && m.shared_with.length) addBadge(badges, nid, { kind: 'mem', text: tr('shared') });
    });
    var ev = (run && run.event_counts) || {};
    Object.keys(ev).forEach(function (nid) {
      var n = 0;
      Object.keys(ev[nid] || {}).forEach(function (k) { n += Number(ev[nid][k]) || 0; });
      if (n > 0) addBadge(badges, nid, { kind: 'events', text: tr('Events: {n}').replace('{n}', n) });
    });
    var ms = (run && run.node_ms) || {}, total = 0;
    Object.keys(ms).forEach(function (nid) { total += ms[nid]; });
    Object.keys(ms).forEach(function (nid) {
      addBadge(badges, nid, { kind: 'ms', text: ms[nid].toFixed(1) + ' ms' });
      if (total > 0) tints[nid] = ms[nid] / total;
    });
    return { badges: badges, edges: edges, general: general, tints: tints };
  }

  root.GraphDoc = {
    SCHEMA: SCHEMA, STRINGS: STRINGS, clone: clone, edgeId: edgeId, fromEngine: fromEngine, toEngine: toEngine,
    edgeKind: edgeKind, edgeKinds: edgeKinds, canConnect: canConnect, edgeLabel: edgeLabel, decorate: decorate,
    suggestId: suggestId, makeProject: makeProject, readAny: readAny, fmtBytes: fmtBytes, applyPatch: applyPatch,
    pins: pins, outputOf: outputOf, logicDefaults: logicDefaults, untrackedFeeds: untrackedFeeds
  };
})(typeof window !== 'undefined' ? window : this);
