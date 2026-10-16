/* DX App — Graph Composer: take the graph away as a standalone C++ project (the #gc-export-dialog modal).

   Opening the dialog asks the server what an export would hold (POST /api/graph/export/plan: the models and their
   sizes, the User logic stubs to fill in, the inputs copied); **Export** writes the project folder and its zip
   (POST /api/graph/export) and offers the zip. dx_app's scripts/export_graph_project.py does the work
   (dx_app/core/graph_export.py). A source exports the input picked for it in the run panel, else its own.
   Contract: tests/dx_app/test_graph_export_browser.py */
window.GraphExport = (function () {
  'use strict';
  var NAME = /^[A-Za-z][A-Za-z0-9_-]{0,47}$/;
  var c = null;
  var st = { plan: null, seq: 0, busy: false, include: false, name: '', result: null, error: '', failure: null,
    announced: false };

  function $id(i) { return document.getElementById(i); }
  function bytes(b) { return c.D.fmtBytes(b || 0); }

  function defaultName() {
    var n = String(c.state.name || 'graph').replace(/[^A-Za-z0-9_-]+/g, '_').replace(/^[^A-Za-z]+/, '');
    return (n || 'graph').slice(0, 48);
  }

  /* The run panel's sample per source; an upload is not exported (the source keeps its own input). */
  function inputs() {
    var out = {};
    c.canvas().getGraph().nodes.forEach(function (n) {
      var pick = n.kind === 'source' && window.GraphRun && GraphRun.inputFor(n.id);
      if (pick) out[n.id] = pick;
    });
    return out;
  }

  function errorText(r) {
    var key = r && r.error_key;
    if (key === 'export_unsupported') return T('This dx_app build cannot export projects. Update dx_app to use it.');
    if (key === 'export_no_space') {
      return c.fmt(T('Not enough disk space: the export needs {need} and {free} is free.'),
        { need: bytes(r.need_bytes), free: bytes(r.free_bytes) });
    }
    /* The exporter's refusals (user_name_invalid, model_file_missing, ...): the dictionary text of the key. */
    return (typeof translatedError === 'function' ? translatedError(r) : r && r.error) || T('The export failed.');
  }

  /* A new failure: shown, and announced once. */
  function fail(r) { st.failure = r || {}; st.error = errorText(r); st.announced = false; }

  function canInclude() { return !!st.plan && st.plan.models.every(function (m) { return m.present; }); }

  /* A model that is not installed has the download size the exporter knows, else none: bytes null (an older dx_app
     says 0), shown as unknown rather than as 0 B. */
  function sized(m) { return m.present || (typeof m.bytes === 'number' && m.bytes > 0); }

  function modelSize(m) {
    if (m.present) return bytes(m.bytes);
    return sized(m) ? c.fmt(T('not installed ({size})'), { size: bytes(m.bytes) }) : T('not installed, size unknown');
  }

  /* The models' total: exact when every size is known, else the known part as a lower bound. */
  function totalSize() {
    var p = st.plan;
    if (!p) return '…';
    var known = 0, unknown = 0;
    p.models.forEach(function (m) { if (sized(m)) known += m.bytes || 0; else unknown += 1; });
    if (!unknown) return bytes(known);
    return known > 0 ? c.fmt(T('at least {size}'), { size: bytes(known) }) : T('size unknown');
  }

  function planBlock() {
    var h = c.h, p = st.plan, box = h('div', { id: 'gc-export-plan', class: 'gc-export-plan' });
    if (!p) {
      if (!st.error) box.appendChild(h('p', { class: 'gc-help', text: T('Reading what the export will hold…') }));
      return box;
    }
    box.appendChild(h('h3', { class: 'gc-export-head', text: T('Models') }));
    box.appendChild(h('table', { class: 'gc-export-table' }, [h('tbody', null, p.models.map(function (m) {
      return h('tr', null, [h('td', { text: m.model }), h('td', { text: modelSize(m) })]);
    }))]));
    /* The inputs the project carries: a run's upload is never one of them (the source keeps its own input). */
    box.appendChild(h('h3', { class: 'gc-export-head', text: T('Inputs') }));
    box.appendChild(h('ul', { class: 'gc-export-inputs' }, (p.inputs || []).map(function (i) {
      return h('li', null, [h('code', { text: i.uri || T('no input: give one with --input') }), ' ',
        c.fmt(T('for source {source}'), { source: i.source })]);
    })));
    box.appendChild(h('p', { class: 'gc-help',
      text: T('An uploaded image is not exported: a source uses the sample picked for it, else its own input.') }));
    box.appendChild(h('h3', { class: 'gc-export-head', text: T('User logic stubs to fill in') }));
    if (!p.user_logic.length) {
      box.appendChild(h('p', { class: 'gc-help', text: T('No User logic block: the project runs the graph as it is.') }));
    } else {
      box.appendChild(h('ul', { class: 'gc-export-stubs' }, p.user_logic.map(function (u) {
        return h('li', null, [h('code', { text: 'user_logic/' + u.name + '.cpp' }), ' ',
          c.fmt(T('for node {nodes} (input: {kind})'), { nodes: u.nodes.join(', '), kind: u.input })]);
      })));
    }
    (p.warnings || []).forEach(function (w) { box.appendChild(h('p', { class: 'gc-help gc-export-warn', text: w })); });
    return box;
  }

  function resultBlock() {
    var h = c.h, r = st.result;
    if (!r) return null;
    return h('div', { id: 'gc-export-result', class: 'gc-export-result', role: 'status' }, [
      h('p', { text: c.fmt(T('Exported to {folder}'), { folder: r.folder }) }),
      h('a', { id: 'gc-export-zip', class: 'btn btn-primary btn-sm', href: r.zip_url, download: r.name + '.zip' },
        [c.icon('download'), ' ', c.fmt(T('Download .zip ({size})'), { size: bytes(r.zip_bytes) })]),
      h('p', { class: 'gc-help', text: T('Build and run it:') }),
      h('pre', { class: 'gc-export-cmd' }, [h('code', { text: 'unzip ' + r.name + '.zip && cd ' + r.name +
        '\n./setup.sh\n./run.sh' })])
    ]);
  }

  /* The name, the model choice, the size and the Export button follow the state without a re-render (the name
     field keeps its focus while typing). */
  function refreshControls() {
    var ok = NAME.test(st.name), name = $id('gc-export-name'), help = $id('gc-export-name-help');
    var models = $id('gc-export-models'), size = $id('gc-export-size'), go = $id('gc-export-go');
    if (name) name.setAttribute('aria-invalid', String(!ok));
    if (help) help.classList.toggle('is-bad', !ok);
    if (models) {
      if (st.plan && !canInclude()) st.include = false;
      models.disabled = !st.plan || !canInclude() || st.busy;
      models.checked = st.include;
    }
    var why = $id('gc-export-models-why');
    if (why) why.hidden = !(st.plan && !canInclude());
    if (size) size.textContent = c.fmt(T('Include the model files ({size})'), { size: totalSize() });
    if (go) {
      go.disabled = st.busy || !st.plan || !ok;
      go.textContent = st.busy ? T('Exporting…') : T('Export');
    }
  }

  function render() {
    var h = c.h, body = $id('gc-export-body');
    if (!body) return;
    /* A re-render (the plan arriving, a language change) keeps the focus where it was. */
    var active = document.activeElement, focused = active && body.contains(active) ? active.id : '';
    var caret = focused === 'gc-export-name' ? [active.selectionStart, active.selectionEnd] : null;
    body.textContent = '';
    var name = h('input', { type: 'text', id: 'gc-export-name', class: 'input', maxlength: '48', autocomplete: 'off',
      spellcheck: 'false', 'aria-describedby': 'gc-export-name-help' });
    name.value = st.name;
    name.addEventListener('input', function () { st.name = name.value.trim(); refreshControls(); });
    name.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); go(); } });
    body.appendChild(h('label', { class: 'gc-field' }, [h('span', { text: T('Project folder name') }), name]));
    body.appendChild(h('p', { class: 'gc-help', id: 'gc-export-name-help',
      text: T('Letters, digits, _ and -, starting with a letter (at most 48).') }));
    var models = h('input', { type: 'checkbox', id: 'gc-export-models',
      'aria-describedby': 'gc-export-models-help gc-export-models-why' });
    models.addEventListener('change', function () { st.include = models.checked; refreshControls(); });
    body.appendChild(h('label', { class: 'gc-export-check' }, [models, h('span', { id: 'gc-export-size' })]));
    body.appendChild(h('p', { class: 'gc-help', id: 'gc-export-models-help',
      text: T('Without them, setup.sh downloads the models from the DEEPX Model Zoo.') }));
    var why = h('p', { class: 'gc-help gc-export-warn', id: 'gc-export-models-why',
      text: T('Every model must be installed to include the files.') });
    why.hidden = true;
    body.appendChild(why);
    body.appendChild(h('p', { class: 'gc-help', text: T('The project holds the graph, the engine with only these models, a main.cpp, setup.sh, run.sh and a README. It builds and runs anywhere the DEEPX runtime is installed.') }));
    body.appendChild(planBlock());
    /* The failure's text follows the language, but only a new failure is announced: the alert role goes on the
       error's first rendering, so a re-render (a language change) does not read it out again. */
    if (st.failure) st.error = errorText(st.failure);
    var err = h('p', { id: 'gc-export-error', class: 'gc-export-error', text: st.error });
    if (st.error && !st.announced) { err.setAttribute('role', 'alert'); st.announced = true; }
    err.hidden = !st.error;
    body.appendChild(err);
    var res = resultBlock();
    if (res) body.appendChild(res);
    refreshControls();
    if (focused && $id(focused)) $id(focused).focus();
    if (caret && $id('gc-export-name')) $id('gc-export-name').setSelectionRange(caret[0], caret[1]);
  }

  async function open() {
    if (!c) return;
    /* The model files are left out unless the user ticks the box (it can be ticked when every model is installed). */
    st = { plan: null, seq: st.seq + 1, busy: false, include: false, name: defaultName(), result: null, error: '',
      failure: null, announced: false };
    render();
    if (typeof openModal === 'function') openModal('gc-export-dialog'); else $id('gc-export-dialog').showModal();
    var name = $id('gc-export-name');
    if (name) name.focus();
    var mine = st.seq;
    var r = await c.api.exportPlan({ graph: c.engine(), inputs: inputs() });
    if (mine !== st.seq) return;
    if (r && r.ok) st.plan = r; else fail(r);
    render();
  }

  async function go() {
    if (st.busy || !st.plan || !NAME.test(st.name)) return;
    st.busy = true;
    st.error = '';
    st.failure = null;
    st.result = null;
    var mine = st.seq;
    render();
    var r = await c.api.exportProject({ graph: c.engine(), name: st.name, include_models: st.include, inputs: inputs() });
    if (mine !== st.seq) return;
    st.busy = false;
    if (r && r.ok) st.result = r; else fail(r);
    render();
    var focus = $id(st.result ? 'gc-export-zip' : 'gc-export-name');
    if (focus) focus.focus();
  }

  function isOpen() { var d = $id('gc-export-dialog'); return !!d && d.open; }

  function close() { var d = $id('gc-export-dialog'); if (d && d.open) d.close(); }

  function mount(ctx) {
    c = ctx;
    $id('gc-export-go').addEventListener('click', go);
    $id('gc-export-close').addEventListener('click', close);
    /* Closed (Close, Escape, the backdrop): an answer still on its way is dropped. */
    $id('gc-export-dialog').addEventListener('close', function () { st.seq++; st.busy = false; });
  }

  function refreshLanguage() { if (isOpen()) render(); }

  return { mount: mount, open: open, close: close, isOpen: isOpen, refreshLanguage: refreshLanguage,
    state: function () { return st; } };
})();
