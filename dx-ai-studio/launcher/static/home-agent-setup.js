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

  /* copilot 은 `catalog` 를 준다 — 전체 model 과, 이 계정이 쓸 수 있는지 (요금제 · 회사 정책) 와 요금
     배수. 전부 보이되 계정 것만 고르게 한다 (사용자 결정 2026-09-30): 못 쓰는 것은 disabled, 쓸 수
     있는 것은 배수를 붙인다. catalog 가 없으면 (다른 agent · 조회 실패) 목록 전체가 고를 수 있는 것이다. */
  function _paintModels(name, d, fallbackDefault) {
    var sel = $('setupModel');
    var chosen = d.default_model || fallbackDefault;
    /* CLI 목록은 몇 초 걸린다 (cursor 는 200 개 넘게) — 그 사이 사람이 고른 model 은 지킨다. 예전에는 기본값으로
       바꿔 놓고 접힌 요약은 고른 이름을 그대로 보였다 (2026-10-11 실사용 감사). */
    var picked = sel && sel.dataset.userPicked === name ? sel.value : '';
    if (picked && (d.models || []).indexOf(picked) !== -1) chosen = picked;
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
    /* 목록이 select 를 바꿔도 change 가 나지 않는다 — 요약을 여기서 다시 쓴다 ("copilot · auto" 로 남아 실제로
       돌 model 과 달랐다). */
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

  /* 한 번 묻고 끝내면 안 된다. home 은 launcher 가 module 들을 띄우는 동안 열릴 수 있고, 그때
     agent dev 는 아직 없어 proxy 가 502 를 준다 — 예전에는 그 한 번으로 form 을 숨긴 채 다시 묻지
     않아서, 새로고침 시점에 따라 model 선택이 떴다 안 떴다 했다. 준비될 때까지 (최대 ~30s) 다시
     묻고, studio 가 준비됐다는 신호 (dx-studio-ready) 에도 한 번 더 묻는다. */
  var _RETRY_MS = [500, 1000, 2000, 4000, 4000, 4000, 4000, 4000, 4000, 4000];
  var _retry = null;

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
        _fill($('setupAgent'), _agents.map(function (a) { return a.name; }), _agents[0].name);
        _selectAgent(_agents[0].name);
        _paintFoldSummary();
      })
      .catch(function () {
        /* The module is not running (yet). The Build section still explains itself;
           it just cannot say who would do the building. 다시 묻는 동안에도 숨겨 둔다 — 값이 빈
           "Agent ›" 가 떠 있으면 고장 난 control 로 보인다. 받아지면 위의 성공 경로가 보인다. */
        _show($('setupForm'), false);
        _show($('setupFold'), false);
        _show($('setupDegraded'), false);
        if (attempt < _RETRY_MS.length) {
          _retry = setTimeout(function () { load(attempt + 1); }, _RETRY_MS[attempt]);
        }
      });
  }

  /* 접힌 채로도 무엇이 골라져 있는지는 보여야 한다 — 접는 것과 숨기는 것은 다르다. */
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

  /* What the console posts to /api/agent/run. mode 는 Agent Dev 와 같은 두 값 — Interactive (묻고 멈춘다,
     답장으로 이어진다) 와 Autopilot (묻지 않고 끝까지). */
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
    } catch (e) { /* storage 없음 — 기본 Interactive */ }
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
      });
    }
    var model = $('setupModel');
    if (model) {
      model.addEventListener('change', function () {
        model.dataset.userPicked = _current ? _current.name : '';
        _paintFoldSummary();
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
