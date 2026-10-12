/* ── Agent setup ──────────────────────────────────────────────
 *
 * Who is going to build it, with which model, at what effort — and whether it
 * is signed in. Visible before you run, because a control you can only reach
 * after starting is a control you cannot use to decide whether to start.
 *
 * Every value here comes from dx_agent_dev. `GET /api/agent/status` already
 * returns, per detected agent: name, models, default_model, reasoning_efforts,
 * default_effort and authenticated. That is the whole form. Nothing is
 * hard-coded on this side — the effort levels in particular differ per agent
 * (copilot has `none`, codex has `minimal` and no `max`, claude has neither),
 * so a fixed list here would be wrong for two of the five.
 *
 * When no CLI is present the same endpoint returns localized `title`/`detail`
 * and an `installOptions` list. An empty set of dropdowns explains nothing;
 * that guidance does.
 */
(function () {
  'use strict';

  var ns = window.DXLauncher = window.DXLauncher || {};

  var API = '/agent/api/agent';
  var _agents = [];          // [{name, models, default_model, reasoning_efforts, default_effort, authenticated}]
  var _current = null;

  function $(id) { return document.getElementById(id); }
  function _t(key) {
    return (window.DXI18n && window.DXI18n.T) ? window.DXI18n.T(key) : key;
  }
  function _show(el, on) {
    if (!el) return;
    if (on) el.removeAttribute('hidden'); else el.setAttribute('hidden', '');
  }

  function _esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function _fill(sel, values, chosen) {
    if (!sel) return;
    sel.innerHTML = values.map(function (v) {
      return '<option value="' + _esc(v) + '"' + (v === chosen ? ' selected' : '') + '>' + _esc(v) + '</option>';
    }).join('');
  }

  /* ── the form ────────────────────────────────────────────── */

  function _byName(name) {
    for (var i = 0; i < _agents.length; i++) {
      if (_agents[i].name === name) return _agents[i];
    }
    return null;
  }

  /* Model and effort belong to the agent, so both are rebuilt whenever the
     agent changes. Keeping the old model selected across a change would post
     a model the new CLI has never heard of.

     The two lists come from different places on purpose. Effort levels are
     configuration and /status carries them. The model list is NOT — /status
     reports the static table in agents_config, while /models?agent=X asks the
     CLI itself. For cursor that is the difference between 4 models and 223.
     So the static list paints immediately and the real one replaces it. */
  function _selectAgent(name) {
    var a = _byName(name);
    if (!a) return;
    _current = a;
    _fill($('setupModel'), a.models || [], a.default_model);
    _fill($('setupEffort'), a.reasoning_efforts || [], a.default_effort);
    _paintAuth(a);
    _loadModels(name, a.default_model);
  }

  var _modelCache = {};

  function _loadModels(name, fallbackDefault) {
    if (_modelCache[name]) { _paintModels(name, _modelCache[name], fallbackDefault); return; }
    fetch(API + '/models?agent=' + encodeURIComponent(name))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d || !d.models || !d.models.length) return;
        _modelCache[name] = d;
        /* The agent may have changed while the CLI was being asked. */
        if (_current && _current.name === name) {
          _paintModels(name, d, fallbackDefault);
        }
      })
      .catch(function () { /* the static list is already on screen */ });
  }

  /* copilot gives a `catalog`: every model, whether this account may use it (plan, org policy), and its
     cost multiplier. All are shown but only the account's are selectable: unusable ones are disabled,
     usable ones carry the multiplier. Without a catalog (other agents, lookup failed) the whole list is selectable. */
  function _paintModels(name, d, fallbackDefault) {
    var sel = $('setupModel');
    var chosen = d.default_model || fallbackDefault;
    /* The CLI list takes seconds (cursor has 200+) — keep a model the user picked meanwhile, rather than
       resetting it to the default while the collapsed summary still shows the pick. */
    var picked = sel && sel.dataset.userPicked === name ? (sel.dataset.wanted || sel.value) : '';
    if (picked && (d.models || []).indexOf(picked) !== -1) chosen = picked;
    if (sel) delete sel.dataset.wanted;
    if (d.catalog && d.catalog.length && sel) {
      var off = _t('not available on this account');
      sel.innerHTML = d.catalog.map(function (m) {
        var label = m.id + (m.enabled ? (m.usage ? ' \u00B7 ' + m.usage : '') : ' \u2014 ' + off);
        return '<option value="' + _esc(m.id) + '"' + (m.enabled ? '' : ' disabled') +
          (m.enabled && m.id === chosen ? ' selected' : '') + '>' + _esc(label) + '</option>';
      }).join('');
    } else {
      _fill(sel, d.models, chosen);
    }
    var note = $('setupModelCount');
    if (note) note.textContent = d.models.length + ' ' + _t('models');
    /* Changing the select from code fires no change event — rewrite the summary here so it names the model
       that will actually run. */
    _paintFoldSummary();
  }

  function _paintAuth(a) {
    var badge = $('setupAuth');
    var hint = $('setupHint');
    if (!badge) return;
    if (a.authenticated === true) {
      badge.textContent = _t('signed in');
      badge.className = 'setup-auth is-ok';
      _show(hint, false);
      return;
    }
    /* authenticated === null means the adapter could not tell. Saying "signed
       out" then would be a guess, and a wrong one sends people to re-run a
       login they already did. */
    badge.textContent = a.authenticated === false ? _t('not signed in') : _t('sign-in unknown');
    badge.className = 'setup-auth' + (a.authenticated === false ? ' is-off' : '');
    _loadHint(a.name);
  }

  /* The exact command, from the adapter that owns it. Interactive OAuth needs a
     terminal, so the honest help is the command rather than a button that
     cannot finish the job. */
  function _loadHint(name) {
    var hint = $('setupHint');
    if (!hint) return;
    fetch(API + '/login/status?agent=' + encodeURIComponent(name))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d || !d.hint || d.authenticated === true) { _show(hint, false); return; }
        hint.querySelector('code').textContent = d.hint;
        _show(hint, true);
      })
      .catch(function () { _show(hint, false); });
  }

  /* ── no CLI at all ───────────────────────────────────────── */

  function _degraded(status) {
    var box = $('setupDegraded');
    var form = $('setupForm');
    _show(form, false);
    if (!box) return;
    box.querySelector('[data-role="title"]').textContent =
      status.title || _t('No coding agent found');
    box.querySelector('[data-role="detail"]').textContent = status.detail || '';
    var list = box.querySelector('[data-role="options"]');
    list.innerHTML = '';
    (status.installOptions || []).forEach(function (o) {
      var li = document.createElement('li');
      var state = o.installed
        ? (o.authenticated === true ? _t('signed in') : _t('not signed in'))
        : _t('not installed');
      li.innerHTML = '<b>' + (o.displayName || o.agent) + '</b><span>' + state + '</span>' +
        (o.loginHint ? '<code>' + o.loginHint + '</code>' : '');
      list.appendChild(li);
    });
    _show(box, true);
  }

  /* ── load ────────────────────────────────────────────────── */

  /* One request is not enough. Home can open while the launcher is still starting modules; Agent Dev
     is not up yet and the proxy answers 502, and giving up there would hide the model picker depending
     on when the page loaded. Retry until it is ready (up to ~30 s), and ask once more on the
     studio-ready signal (dx-studio-ready). */
  var _RETRY_MS = [500, 1000, 2000, 4000, 4000, 4000, 4000, 4000, 4000, 4000];
  var _retry = null;

  var _STUDIO_ORDER = ['claude', 'copilot', 'cursor', 'codex', 'opencode'];
  /* The whole studio uses one agent: the picked one (studio_agent) → else the first signed-in agent (studio
     order) → else the first agent. Chat answers with the same one. Contract: tests/launcher/test_home_studio_agent_browser.py */
  function _initialAgent(status) {
    var names = _agents.map(function (a) { return a.name; });
    var pick = status.studio_agent && status.studio_agent.agent;
    if (pick && names.indexOf(pick) !== -1) return pick;
    for (var i = 0; i < _STUDIO_ORDER.length; i++) {
      var a = _byName(_STUDIO_ORDER[i]);
      if (a && a.authenticated === true) return a.name;
    }
    return names[0];
  }

  function _saveStudioAgent() {
    var agent = $('setupAgent'), model = $('setupModel');
    if (!agent || !agent.value) return;
    fetch('/api/studio/agent', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent: agent.value, model: (model && model.value) || null })
    }).catch(function () { /* the pick still applies to this page */ });
  }

  function load(attempt) {
    attempt = attempt || 0;
    if (_retry) { clearTimeout(_retry); _retry = null; }
    return fetch(API + '/status')
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (status) {
        if (!status || !status.available) { _degraded(status || {}); return; }
        _agents = status.agents || [];
        if (!_agents.length) { _degraded(status); return; }
        _show($('setupDegraded'), false);
        _show($('setupForm'), true);
        _show($('setupFold'), true);
        var first = _initialAgent(status);
        _fill($('setupAgent'), _agents.map(function (a) { return a.name; }), first);
        _selectAgent(first);
        var savedModel = status.studio_agent && status.studio_agent.agent === first && status.studio_agent.model;
        var modelSel = $('setupModel');
        if (savedModel && modelSel) {
          modelSel.dataset.userPicked = first;          // the CLI list that arrives later keeps it
          modelSel.dataset.wanted = savedModel;          // may exist only in that later list (cursor: 200+)
          if ([].some.call(modelSel.options, function (o) { return o.value === savedModel; })) modelSel.value = savedModel;
        }
        _paintFoldSummary();
      })
      .catch(function () {
        /* The module is not running (yet). The Build section still explains itself;
           it just cannot say who would do the building. Stay hidden while retrying — an empty
           "Agent ›" looks like a broken control. Once an answer arrives, the success path above shows it. */
        _show($('setupForm'), false);
        _show($('setupFold'), false);
        _show($('setupDegraded'), false);
        if (attempt < _RETRY_MS.length) {
          _retry = setTimeout(function () { load(attempt + 1); }, _RETRY_MS[attempt]);
        }
      });
  }

  /* Collapsed, it still shows what is picked — collapsing is not hiding. */
  function _paintFoldSummary() {
    var out = $('setupFoldValue');
    if (!out) return;
    var agent = $('setupAgent');
    var model = $('setupModel');
    var parts = [];
    if (agent && agent.value) parts.push(agent.value);
    if (model && model.value) parts.push(model.value);
    out.textContent = parts.join(' \u00B7 ');
  }

  /* What the console posts to /api/agent/run. mode takes Agent Dev's two values — Interactive (asks and
     stops, continues on a reply) and Autopilot (runs to the end without asking). */
  function choice() {
    return {
      agent: $('setupAgent') ? $('setupAgent').value : undefined,
      model: $('setupModel') ? $('setupModel').value : undefined,
      effort: $('setupEffort') ? $('setupEffort').value : undefined,
      mode: $('setupMode') ? $('setupMode').value : 'interactive'
    };
  }

  var _MODE_KEY = 'dx-home-agent-mode';
  function _restoreMode() {
    var sel = $('setupMode');
    if (!sel) return;
    try {
      var saved = localStorage.getItem(_MODE_KEY);
      if (saved === 'interactive' || saved === 'autopilot') sel.value = saved;
    } catch (e) { /* no storage — default to Interactive */ }
    sel.addEventListener('change', function () {
      try { localStorage.setItem(_MODE_KEY, sel.value); } catch (e) {}
    });
  }

  function init() {
    if (!$('setupForm')) return;
    var agent = $('setupAgent');
    if (agent) {
      agent.addEventListener('change', function () {
        _selectAgent(agent.value);
        _paintFoldSummary();
        _saveStudioAgent();
      });
    }
    var model = $('setupModel');
    if (model) {
      model.addEventListener('change', function () {
        model.dataset.userPicked = _current ? _current.name : '';
        delete model.dataset.wanted;      // the user's own pick beats the saved Studio model
        _paintFoldSummary();
        _saveStudioAgent();
      });
    }
    _restoreMode();
    load();
    window.addEventListener('dx-studio-ready', function () { if (!_agents.length) load(); });
    if (window.DXI18n && DXI18n.onLangChange) {
      DXI18n.onLangChange(function () { if (_current) _paintAuth(_current); });
    }
  }

  ns.agentChoice = choice;
  ns.reloadAgentSetup = load;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
