/* DX App — Graph Composer palette: scenario templates (examples with logic blocks, with a result thumbnail), example
   graphs, a source, the models dx_app can put in a graph (by task, with their install state and a Download button),
   the logic blocks dx_app lists (--list-ops) and the CPU ops. Items drag onto the canvas; the + button (or Enter on
   it) adds one in the middle of the view. A model download is followed until it ends, the status stops answering
   STATUS_FAILURES times in a row, or the page is left (it is picked up again when the page opens).
   Contract: tests/dx_app/test_graph_composer_browser.py, tests/dx_app/test_graph_logic_browser.py */
window.GraphPalette = (function () {
  'use strict';
  var expanded = { templates: true, examples: true, sources: true, logic: true, cpu: true };   // task groups start closed: 497 models
  var query = '';
  var downloading = null;          // {name, btn} while a download runs
  var lastRoot = null, lastCtx = null;
  var STATUS_EVERY_MS = 1500, STATUS_FAILURES = 5;
  var statusTimer = 0, failures = 0, resumeOnOpen = false;
  /* Labels of the logic blocks of the spec (section 6); a block dx_app adds later shows its op name. */
  var LOGIC_LABELS = { filter: 'Filter', zone: 'Zone', line: 'Line crossing', count: 'Count', dwell: 'Dwell',
    condition: 'Condition → Event', gallery: 'Gallery match', user: 'User logic' };

  /* dx_app's example graphs by example id (the templates, with logic blocks, then the engine examples): a name and
     what it does, both dictionary keys. An example dx_app adds later shows its graph name and its blocks or models.
     tests/dx_app/test_graph_composer_i18n.py keeps this list equal to dx_app's samples. */
  var TEMPLATE_TEXT = {
    zone_intrusion: ['Restricted-zone intrusion', 'An event when a person enters the zone'],
    line_counting: ['Line counting', 'People crossing a line, counted per direction'],
    ppe_zone_check: ['PPE check', 'An event for a person in the zone without a hat'],
    loitering_dwell: ['Loitering', 'An event when a person stays in the zone over 5 s'],
    zone_people_count: ['People count per zone', 'People counted in two zones'],
    gallery_known_person: ['Known person', 'Each person named after the closest Gallery entry, or unknown'],
    driver_attention: ['Driver attention', 'Events when the driver turns the head away or down'],
    multistream_people_count: ['Multi-camera people count', 'People counted per camera; an event when one is crowded'],
    logistics_volume_alert: ['Logistics volume alert', 'An event when the estimated volume of packages passes a limit'],
    fanout_od_seg_pose: ['Detection, segmentation and pose', 'Three models on one frame, drawn together'],
    fanout_od_seg_depth: ['Detection, segmentation and depth', 'Three models on one frame, with depth instead of pose'],
    cascade_od_reid_track: ['Person re-identification', 'Each tracked person cropped for a ReID embedding'],
    cascade_od_attr: ['Person attributes', 'Each person cropped for attribute recognition'],
    cascade_obb_cls: ['Rotated objects classified', 'Oriented boxes straightened, then classified'],
    handoff_denoise_od: ['Denoise, then detect', 'Detection on the denoised image'],
    handoff_sr_od_cls: ['Super-resolution, detect, classify', 'Detection and classification on a 2x image; too large for DX-M1'],
    multistream_od_two_sources: ['Two cameras, one ReID', 'Two sources share one tracked detector and one ReID model'],
    chain_sr_od_pose: ['Super-resolution, detect, pose', 'Top-down pose on a 2x image; too large for DX-M1'],
    chain_zerodce_od_pose_emb: ['Low-light detection, pose and ReID', 'Low-light enhancement, then a pose and an embedding per person'],
    hand_cascade: ['Hand landmarks', 'Palm detection, then 21 landmarks per hand'],
    dms_headpose: ['Driver head pose', 'Face detection, then pitch, yaw and roll'],
    logistics_volume: ['Package volume', 'Detection, masks and depth give a volume estimate per package']
  };

  function opLabel(op) { return LOGIC_LABELS[op] ? T(LOGIC_LABELS[op]) : op; }
  function templateName(ex) { return TEMPLATE_TEXT[ex.id] ? T(TEMPLATE_TEXT[ex.id][0]) : ex.name; }

  /* The search box finds an example by its graph name, its id or its name in this language. */
  function exampleMatches(ex) {
    if (!query) return true;
    return [ex.name, ex.id, templateName(ex)].some(function (s) {
      return String(s || '').toLowerCase().indexOf(query) !== -1;
    });
  }

  function stateLabel(m) {
    if (m.state === 'installed') return T('Installed');
    if (m.state === 'missing') return T('Not installed');
    if (m.state === 'invalid') return T('Broken file');
    if (m.state === 'needs_runtime') return T('Needs a newer DX-RT');
    return T('Not graph-ready');
  }

  function stateBadge(m) {
    return { installed: 'b-ok', missing: 'b-warn', invalid: 'b-red', needs_runtime: 'b-warn', not_ready: 'b-no' }[m.state] || 'b-no';
  }

  function matches(keys) {
    return function (o) {
      return !query || keys.some(function (k) { return String(o[k] || '').toLowerCase().indexOf(query) !== -1; });
    };
  }

  function group(c, key, title, items, count) {
    var isOpen = query ? true : !!expanded[key];
    var body = c.h('div', { class: 'gc-group-body', role: 'list' }, items);
    body.hidden = !isOpen;
    var head = c.h('button', { type: 'button', class: 'gc-group-head', 'aria-expanded': String(isOpen) },
      [c.icon('chevd'), c.h('span', { class: 'gc-group-title', text: title }),
       c.h('span', { class: 'gc-count', text: String(count == null ? items.length : count) })]);
    head.addEventListener('click', function () {
      expanded[key] = !(head.getAttribute('aria-expanded') === 'true');
      head.setAttribute('aria-expanded', String(expanded[key]));
      body.hidden = !expanded[key];
    });
    return c.h('div', { class: 'gc-group' + (items.length ? '' : ' is-empty'), dataset: { group: key } }, [head, body]);
  }

  function item(c, payload, name, sub, iconName, cat, extra) {
    var add = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm gc-add', title: T('Add to the graph'),
      'aria-label': c.fmt(T('Add {name} to the graph'), { name: name }) }, [c.icon('plus')]);
    add.addEventListener('click', function () { c.addFromPalette(payload); });
    var el = c.h('div', { class: 'gc-item', role: 'listitem', draggable: 'true', dataset: { cat: cat } }, [
      c.icon(iconName),
      c.h('span', { class: 'gc-item-text' }, [c.h('span', { class: 'gc-item-name', text: name, title: name }),
                                              c.h('span', { class: 'gc-item-sub', text: sub })]),
      extra || null,
      add
    ]);
    el.addEventListener('dragstart', function (e) {
      e.dataTransfer.setData(DXGraphCanvas.DND_TYPE, JSON.stringify(payload));
      e.dataTransfer.effectAllowed = 'copy';
    });
    return el;
  }

  function modelItem(c, m) {
    var extra = c.h('span', { class: 'gc-item-extra' }, [
      c.h('span', { class: 'badge ' + stateBadge(m), text: stateLabel(m),
        title: m.reason || (m.needs_dxrt ? c.fmt(T('Needs DX-RT {version} or later'), { version: m.needs_dxrt }) : '') })]);
    if ((m.state === 'missing' || m.state === 'invalid') && m.download) {
      var dl = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm', text: T('Download') });
      dl.addEventListener('click', function (e) { e.stopPropagation(); download(c, m, dl); });
      extra.appendChild(dl);
    }
    var takes = m.consumes === 'either' ? T('frame or crop') : T('full frame');
    var el = item(c, { kind: 'model', model: m.name }, m.name, m.produces + ' · ' + takes, 'task-' + m.task, 'model', extra);
    if (m.state === 'not_ready') {
      el.classList.add('is-disabled');
      el.draggable = false;
      el.querySelector('.gc-add').disabled = true;
    }
    return el;
  }

  function templateItem(c, ex) {
    var name = templateName(ex), text = TEMPLATE_TEXT[ex.id];
    var blocks = (ex.ops || []).map(opLabel).join(' · ');
    var about = text ? T(text[1]) : blocks;
    var open = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm', text: T('Open'),
      'aria-label': c.fmt(T('Open the template {name}'), { name: name }) });
    open.addEventListener('click', function () { c.loadExample(ex.id); });
    var thumb = ex.thumb ? c.h('img', { class: 'gc-thumb', src: ex.thumb, alt: c.fmt(T('Result of {name}'), { name: name }), loading: 'lazy' })
      : c.icon('graph');
    return c.h('div', { class: 'gc-item gc-template', role: 'listitem', dataset: { cat: 'example', id: ex.id } }, [
      thumb,
      c.h('span', { class: 'gc-item-text' }, [c.h('span', { class: 'gc-item-name', text: name, title: name }),
                                              c.h('span', { class: 'gc-item-sub', text: about, title: text ? about + ' (' + blocks + ')' : blocks })]),
      open
    ]);
  }

  function logicItem(c, op) {
    var shapes = [];
    (op.inputs.accepts || []).forEach(function (a) { if (shapes.indexOf(a.shape) === -1) shapes.push(a.shape); });
    var takes = shapes.length > 4 ? T('any result') : shapes.join(' / ');
    return item(c, { kind: 'logic', op: op.op }, opLabel(op.op), c.fmt(T('takes {inputs}'), { inputs: takes }),
      { filter: 1, zone: 1, line: 1, count: 1, dwell: 1, condition: 1, gallery: 1, user: 1 }[op.op] ? 'logic-' + op.op : 'puzzle', 'logic');
  }

  function exampleItem(c, ex) {
    var name = templateName(ex), text = TEMPLATE_TEXT[ex.id];
    var models = ex.models.join(' + ');
    var about = text ? T(text[1]) : models;
    var open = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm', text: T('Open'),
      'aria-label': c.fmt(T('Open the example {name}'), { name: name }) });
    open.addEventListener('click', function () { c.loadExample(ex.id); });
    var thumb = ex.thumb ? c.h('img', { class: 'gc-thumb', src: ex.thumb, alt: c.fmt(T('Result of {name}'), { name: name }), loading: 'lazy' })
      : c.icon('graph');
    return c.h('div', { class: 'gc-item gc-example', role: 'listitem', dataset: { cat: 'example', id: ex.id } }, [
      thumb,
      c.h('span', { class: 'gc-item-text' }, [c.h('span', { class: 'gc-item-name', text: name, title: name }),
                                              c.h('span', { class: 'gc-item-sub', text: about, title: text ? about + ' (' + models + ')' : models })]),
      open
    ]);
  }

  function pageOpen() { return !!document.querySelector('#page-graph.active'); }

  function stopFollowing() {
    clearTimeout(statusTimer);
    statusTimer = 0;
  }

  /* One status check; the next is scheduled only while the page is open and the status answers. */
  function follow(c) {
    stopFollowing();
    statusTimer = setTimeout(async function () {
      statusTimer = 0;
      if (!downloading) return;
      if (!pageOpen()) { resumeOnOpen = true; return; }
      var s = await api('/api/modelzoo/status');
      if (!downloading) return;
      if (!s || s.error || typeof s !== 'object') {
        failures += 1;
        if (failures >= STATUS_FAILURES) {
          var btn = downloading.btn;
          downloading = null;
          failures = 0;
          if (btn) { btn.disabled = false; btn.textContent = T('Download'); }
          c.notify(T('The download status stopped answering. Check Model Zoo, then refresh the palette.'), 'warn');
          return;
        }
        follow(c);
        return;
      }
      failures = 0;
      if (!s.finished) {
        if (s.total && downloading.btn) downloading.btn.textContent = T('Downloading') + ' ' + Math.round(s.done * 100 / s.total) + '%';
        follow(c);
        return;
      }
      downloading = null;
      var ok = !(s.results || []).some(function (x) { return x && x.ok === false; });
      c.notify(ok ? T('Download complete') : T('Download finished with errors'), ok ? 'ok' : 'warn');
      c.reloadCatalog(true);
    }, STATUS_EVERY_MS);
  }

  async function download(c, m, btn) {
    if (downloading) { c.notify(T('A model download is already in progress.'), 'warn'); return; }
    downloading = { name: m.name, btn: btn };
    failures = 0;
    btn.disabled = true;
    btn.textContent = T('Starting…');
    var r = await postJ('/api/modelzoo/download', { items: [{ name: m.download.name, chip: 'qlite',
      dxnn_url: m.download.dxnn_url, json_url: m.download.json_url }], source: 'public' });
    if (!r || !r.ok) {
      downloading = null;
      btn.disabled = false;
      btn.textContent = T('Download');
      c.notify((r && r.error) || T('Download failed to start'), 'err');
      return;
    }
    follow(c);
  }

  function render(root, c) {
    if (!root) return;
    lastRoot = root;
    lastCtx = c;
    var cat = c.state.catalog || { models: [], examples: [], cpu_ops: [] };
    var search = document.getElementById('gc-search');
    if (search && !search.dataset.bound) {
      search.dataset.bound = '1';
      search.addEventListener('input', function () { query = search.value.trim().toLowerCase(); render(lastRoot, lastCtx); });
    }
    root.textContent = '';
    if (resumeOnOpen && downloading) { resumeOnOpen = false; follow(c); }
    if (cat.available === false) {
      root.appendChild(c.h('p', { class: 'gc-empty', text: T('The graph runner is not built. Build dx_app (./build.sh) to use the Graph Composer.') }));
    }
    var exs = (cat.examples || []).filter(exampleMatches);
    var templates = exs.filter(function (ex) { return ex.logic; });
    if (templates.length) root.appendChild(group(c, 'templates', T('Templates'), templates.map(function (ex) { return templateItem(c, ex); })));
    root.appendChild(group(c, 'examples', T('Examples'), exs.filter(function (ex) { return !ex.logic; })
      .map(function (ex) { return exampleItem(c, ex); })));
    root.appendChild(group(c, 'sources', T('Sources'), [item(c, { kind: 'source' }, T('Image or video'), T('Source'), 'camera', 'source')]));
    var byTask = {};
    (cat.models || []).filter(matches(['name', 'task'])).forEach(function (m) { (byTask[m.task] = byTask[m.task] || []).push(m); });
    Object.keys(byTask).sort().forEach(function (task) {
      var label = typeof catText === 'function' ? catText(task) : task.replace(/_/g, ' ');
      root.appendChild(group(c, 'task:' + task, label, byTask[task].map(function (m) { return modelItem(c, m); })));
    });
    var ops = (cat.logic_ops || []).filter(function (op) {
      return !query || op.op.indexOf(query) !== -1 || opLabel(op.op).toLowerCase().indexOf(query) !== -1;
    });
    if (ops.length) root.appendChild(group(c, 'logic', T('Logic'), ops.map(function (op) { return logicItem(c, op); })));
    else if (cat.available !== false && cat.logic_error === 'list_ops_unsupported' && !query) {
      var none = group(c, 'logic', T('Logic'), []);
      none.classList.remove('is-empty');
      none.querySelector('.gc-group-body').appendChild(c.h('p', { class: 'gc-help', text: T('This dx_app build has no logic blocks yet.') }));
      root.appendChild(none);
    }
    root.appendChild(group(c, 'cpu', T('CPU ops'), (cat.cpu_ops || []).filter(matches(['op'])).map(function (op) {
      return item(c, { kind: 'cpu', op: op.op, params: op.params }, op.op, c.fmt(T('takes {inputs}'), { inputs: op.inputs.join(' + ') }), 'cpu', 'cpu');
    })));
  }

  if (typeof registerLangRefresher === 'function') {
    registerLangRefresher(function () {
      if (lastRoot && lastCtx && document.querySelector('#page-graph.active')) render(lastRoot, lastCtx);
    });
  }

  return { render: render, following: function () { return !!statusTimer; },
    downloading: function () { return downloading ? downloading.name : null; } };
})();
