/* ── Home prompt → answer ─────────────────────────────────────
 *
 * Wires the hero input to the router and renders what came back. The router is
 * pure and knows nothing about the DOM; this file knows nothing about parsing.
 *
 * The catalogue and the demo list are fetched once, lazily, and cached — never
 * per keystroke. If either is unreachable the router still runs on what it has,
 * which is how a local app should behave when a module has not been started.
 */
(function () {
  'use strict';

  var ns = window.DXLauncher = window.DXLauncher || {};
  var _catalog = null;
  var _demos = null;
  var _loading = null;

  var MODULE_PATH = {
    stream: '/stream/', zoo: '/zoo/', compiler: '/compiler/',
    planner: '/planner/', benchmark: '/benchmark/', monitor: '/dx_monitor/',
    app: '/app/', agent: '/agent/'
  };

  var KIND_LABEL = {
    run: 'Run it now', fit: 'Check it fits', models: 'Pick a model',
    verb: 'Open the tool'
  };

  function $(id) { return document.getElementById(id); }

  function _t(key) {
    return (window.DXI18n && window.DXI18n.T) ? window.DXI18n.T(key) : key;
  }

  function _esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  /* Translate a whole sentence at once — joining fragments breaks sentences in languages with a
     different word order (ko · ja). {x} is a value, **…** is bold. */
  function _tpl(key, vals) {
    var out = _esc(_t(key)).replace(/\{(\w+)\}/g, function (_, k) { return _esc((vals || {})[k]); });
    return out.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
  }

  /* Router task id → display name. Unknown ids get a human-readable form. */
  var TASK_NAME = {
    object_detection: 'Object Detection', pose_estimation: 'Pose Estimation', segmentation: 'Segmentation',
    face_detection: 'Face Detection', classification: 'Classification',
    instance_segmentation: 'Instance Segmentation', semantic_segmentation: 'Semantic Segmentation'
  };
  function _taskName(id) {
    if (!id) return '';
    var key = TASK_NAME[id] || String(id).replace(/_/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
    return _t(key);
  }
  var SOURCE_NAME = { webcam: 'Webcam', video: 'Video file', rtsp: 'RTSP stream' };
  function _sourceName(id) { return id ? _t(SOURCE_NAME[id] || id) : ''; }
  var VERB_NAME = { compile: 'DX Compiler', benchmark: 'DX Benchmark', monitor: 'DX Monitor' };

  /* One fetch per session, not per keystroke. A failure is not fatal: an empty
     catalogue just means the router has fewer terms to match against. */
  function _ensureData() {
    if (_loading) return _loading;
    _loading = Promise.all([
      fetch('/zoo/api/catalog').then(function (r) { return r.json(); })
        .catch(function () { return null; }),
      fetch('/stream/api/demos').then(function (r) { return r.json(); })
        .catch(function () { return null; })
    ]).then(function (both) {
      var cat = both[0];
      _catalog = (cat && (cat.models || cat)) || [];
      if (!Array.isArray(_catalog)) _catalog = [];
      var dem = both[1];
      _demos = (dem && (dem.demos || dem)) || [];
      if (!Array.isArray(_demos)) _demos = [];
    });
    return _loading;
  }

  function _readChips(parsed) {
    var out = [];
    function add(label, value) {
      if (value === null || value === undefined || value === '') return;
      out.push('<span class="read-chip"><b>' + label + '</b>' + value + '</span>');
    }
    add(_t('task'), parsed.task ? _esc(_taskName(parsed.task)) : null);
    add(_t('model'), parsed.model ? _esc(parsed.model) : null);
    add(_t('channels'), parsed.channels);
    add(_t('target'), parsed.fps ? parsed.fps + ' FPS' : null);
    add(_t('input'), parsed.source ? _esc(_sourceName(parsed.source)) : null);
    return out.join('');
  }

  function _routeCard(route, isFirst) {
    var kind = _t(KIND_LABEL[route.kind] || 'Open');
    var name = route.kind === 'verb' ? (VERB_NAME[route.title] || route.title)
      : route.kind === 'models' && route.task ? _taskName(route.task)
      : route.kind === 'run' && route.task ? _taskName(route.task)
      : (route.title ? String(route.title).replace(/_/g, ' ') : route.module);
    var why = route.kind === 'models' && route.count
      ? _t('{n} models').replace('{n}', route.count)
      : route.kind === 'run' && route.channels
      ? _t('{n}-channel').replace('{n}', route.channels)
      : (route.why || route.model || '');
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'route-card' + (isFirst ? ' is-primary' : '');
    btn.dataset.module = route.module;
    if (route.demo !== undefined && route.demo !== null) btn.dataset.demo = route.demo;
    btn.innerHTML =
      '<span class="route-kind">' + _esc(kind) + '</span>' +
      '<span class="route-name">' + _esc(name) + '</span>' +
      '<span class="route-why">' + _esc(why) + '</span>' +
      '<span class="route-go">' + _t('Open') + ' →</span>';
    return btn;
  }

  /* What the agent would do, said before it costs anything. Derived from what
     the router understood, so it is never a generic four lines. */
  function _planSteps(parsed) {
    var steps = [];
    if (parsed.task) steps.push(_tpl('**Pick** a model for {task}', { task: _taskName(parsed.task) }));
    else steps.push(_tpl('**Find** the closest model in the zoo'));
    steps.push(_tpl('**Generate** an app in a new session folder'));
    steps.push(_tpl('**Wire** {input} and the logic you described',
      { input: parsed.source ? _sourceName(parsed.source) : _t('the input') }));
    steps.push(_tpl('**Run** it and show you the output'));
    return steps.map(function (s) { return '<li>' + s + '</li>'; }).join('');
  }

  function _show(el, on) {
    if (!el) return;
    if (on) el.removeAttribute('hidden'); else el.setAttribute('hidden', '');
  }

  function render(text, result) {
    var panel = $('homeAnswer');
    if (!panel) return;
    var routes = result.routes || [];
    var matched = routes.length > 0;

    $('answerRead').innerHTML = _readChips(result.parsed);

    var host = $('answerRoutes');
    host.innerHTML = '';
    routes.slice(0, 3).forEach(function (r, i) { host.appendChild(_routeCard(r, i === 0)); });

    _show(host, matched);
    _show($('answerEscalate'), matched);

    var plan = $('answerAgentPlan');
    if (!matched) {
      $('answerAgentSteps').innerHTML = _planSteps(result.parsed);
      $('answerAgentEta').textContent = _t('about 3–6 min');
    }
    _show(plan, !matched);
    _show(panel, true);
    panel.dataset.ask = text;
    /* Where the request went — home-effects.js flies a light to that module's icon. */
    document.dispatchEvent(new CustomEvent('dx-home-routed', { detail: routes.slice(0, 3) }));
  }

  function ask(text) {
    if (!text || !String(text).trim()) return Promise.resolve(null);
    _saveDraft('');
    return _ensureData().then(function () {
      var result = window.DXHomeRouter.resolve(text, _catalog, _demos);
      render(text, result);
      return result;
    });
  }

  /* Leave home the same way the module cards and icons do: one launch call inside the shell,
     so the document stays and a half-written sentence is not lost. It opens from the card that
     was clicked, and a hash such as #demo=N reaches the module. location.href is used only when
     there is no shell.
     Contract: tests/launcher/test_home_draft_browser.py, test_home_open_browser.py */
  function _leaveHome(path, fromEl) {
    if (!path) return;
    var ns2 = window.DXLauncher;
    var parts = path.split('#');
    var key = (ns2 && typeof ns2.appFromPath === 'function') ? ns2.appFromPath(parts[0]) : null;
    if (key && typeof ns2.launch === 'function') {
      ns2.launch(key, { from: fromEl || null, hash: parts[1] ? '#' + parts[1] : '' });
      return;
    }
    window.location.href = path;
  }

  function _openRoute(btn) {
    var path = MODULE_PATH[btn.dataset.module];
    if (!path) return;
    if (btn.dataset.demo !== undefined) path += '#demo=' + btn.dataset.demo;
    _leaveHome(path, btn);
  }

  /* The handoff carries the sentence. Agent Dev's own input already says
     "Describe what you want to build…" — this is that field, reached from the
     front door instead of one click in. */
  function _handOffToAgent() {
    var panel = $('homeAnswer');
    var text = (panel && panel.dataset.ask) || '';
    if (ns.homeAgentStart) {
      ns.homeAgentStart(text);
      return;
    }
    /* If the work view cannot be used, hand off to the module with the sentence. */
    _leaveHome('/agent/#ask=' + encodeURIComponent(text), $('answerEscalateGo'));
  }

  /* A half-written sentence is work: save it so a trip to a module or a reload does not lose it.
     Clear it once sent (a sent sentence showing up again would be a bug, not a draft).
     sessionStorage, so it goes away with the tab: a draft, not a history. */
  var DRAFT_KEY = 'dxHome.ask.draft';

  function _saveDraft(text) {
    try {
      if (text && text.trim()) sessionStorage.setItem(DRAFT_KEY, text);
      else sessionStorage.removeItem(DRAFT_KEY);
    } catch (e) { /* storage off — nothing is saved, but input still works */ }
  }

  function _restoreDraft() {
    var box = $('homeAsk');
    if (!box) return;
    try {
      var saved = sessionStorage.getItem(DRAFT_KEY);
      if (saved && !box.value) box.value = saved;
    } catch (e) { /* storage off */ }
  }

  function init() {
    var form = $('homeAskForm');
    if (!form) return;
    _restoreDraft();
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      ask($('homeAsk').value);
    });
    /* The input is a textarea so it can hold several lines, which makes Enter a newline. Follow
       the prompt-input convention instead: Enter sends, Shift+Enter starts a new line. */
    var box = $('homeAsk');
    if (box) {
      box.addEventListener('input', function () { _saveDraft(box.value); });
      box.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
          e.preventDefault();
          ask(box.value);
        }
      });
    }
    /* Examples are the original prompts of real showcases (home-prompts.js). Fill and wait —
       running at once would show an answer and switch the stage to the Dock before the long
       prompt could be read or edited. Not translated: the verified text is the English original. */
    var chips = $('homeAskChips');
    if (chips) {
      chips.addEventListener('click', function (e) {
        var more = e.target.closest('#homeAskMore');
        if (more) {
          Array.prototype.forEach.call(chips.querySelectorAll('.ask-chip[hidden]'), function (c) {
            c.hidden = false;
          });
          more.hidden = true;
          return;
        }
        var chip = e.target.closest('.ask-chip');
        if (!chip) return;
        var prompts = window.DXHomePrompts || {};
        var text = prompts[chip.dataset.prompt] || chip.textContent.trim();
        var input = $('homeAsk');
        input.value = text;
        _saveDraft(text);
        input.focus();
        input.setSelectionRange(0, 0);
        input.scrollTop = 0;
      });
    }
    var routes = $('answerRoutes');
    if (routes) {
      routes.addEventListener('click', function (e) {
        var card = e.target.closest('.route-card');
        if (card) _openRoute(card);
      });
    }
    var esc = $('answerEscalateGo');
    if (esc) esc.addEventListener('click', _handOffToAgent);
    var go = $('answerAgentGo');
    if (go) go.addEventListener('click', _handOffToAgent);
    var no = $('answerAgentCancel');
    if (no) no.addEventListener('click', function () { _show($('homeAnswer'), false); });
    var closeBtn = $('answerClose');
    if (closeBtn) closeBtn.addEventListener('click', closeHomeAnswer);

    /* Every label in the panel is built in JS, so data-i18n never reaches it.
       The sentence is kept on the panel, so a language change just answers it
       again — the router is pure and the data is cached, so this is free. */
    if (window.DXI18n && DXI18n.onLangChange) {
      DXI18n.onLangChange(function () {
        var panel = $('homeAnswer');
        if (panel && !panel.hasAttribute('hidden') && panel.dataset.ask) {
          ask(panel.dataset.ask);
        }
      });
    }
  }

  /* Close the answer and restore the stage (close button · Esc). Does nothing if already closed. */
  function closeHomeAnswer() {
    var panel = $('homeAnswer');
    if (!panel || panel.hidden) return false;
    _show(panel, false);
    return true;
  }

  ns.closeHomeAnswer = closeHomeAnswer;
  ns.homeAsk = ask;
  /* The work view leaves the same way — with two ways out, one always goes stale. */
  ns.homeLeaveTo = _leaveHome;
  ns.initHomeAnswer = init;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
