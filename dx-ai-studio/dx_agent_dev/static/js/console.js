/* DX Agent Dev — Agent Console (chat UX + Activity panel + SSE) */
(function () {
  let _running = false;
  let _agents = [];
  let _showcaseCache = null;
  let _showcasePromise = null;
  let _turn = null;
  /* After an error the server still ends with done, so remember until done whether this run failed. */
  let _runFailed = false;
  let _heartbeatTimer = null;
  let _agentControlsBound = false;
  let _modelHintBound = false;

  // Recommended = harness-following-capable families: Sonnet/Opus 4.6+, any Sonnet/Opus 5+,
  // and GPT 5.4+ (covers gpt-5.6-*). Accepts dot or dash forms (4.8 / 4-8, 5.6 / 5-6).
  const _RECOMMENDED_MODEL = /(sonnet|opus)[ -]?4[.-][6-9]|(sonnet|opus)[ -]?[5-9]|gpt[ -]?5[.-][4-9]|gpt[ -]?[6-9]/i;
  let _hasRunOutput = false;

  let _mermaidReady = null;
  let _streamRenderRaf = null;
  /** Server-issued conversation id for multi-turn CLI resume. */
  let _conversationId = null;
  /** The user pressed Stop — the "exit -15" the CLI reports is then expected, not a failure. */
  let _stopRequested = false;

  function setConsoleBusy(busy) {
    const form = $('console-form');
    const input = $('console-input');
    const send = $('console-send');
    if (form) form.classList.toggle('console-form--busy', !!busy);
    if (input) input.disabled = !!busy;
    if (send) send.disabled = !!busy;
    const stop = $('console-stop');
    if (stop) { stop.hidden = !busy; stop.disabled = false; }
  }

  /* Stop a run: a minutes-long build sent by mistake should not have to run to the end. */
  function stopRun() {
    if (!_running || _stopRequested) return;
    _stopRequested = true;
    const stop = $('console-stop');
    if (stop) stop.disabled = true;
    setStatusLine(T('Stopping...'), 'Stopping...');
    fetch('/api/agent/cancel', { method: 'POST' }).catch(function () {});
  }

  /* The stream ended without done: the server died or the connection dropped. Do not leave "Running..." on screen. */
  function finishWithoutDone() {
    if (!_turn) return;
    if (_stopRequested) {
      setBadge('Stopped', 'failed');
      setStatusLine(T('Stopped.'), 'Stopped.');
    } else {
      if (!_runFailed) appendError(T('The connection to the agent ended before it finished.'));
      setBadge('Failed', 'failed');
    }
    if (_turn) updateAssistantView(true);
    _turn = null;
  }

  function releaseRunLock() {
    _running = false;
    setConsoleBusy(false);
  }

  function cancelStreamingRender() {
    if (_streamRenderRaf) {
      cancelAnimationFrame(_streamRenderRaf);
      _streamRenderRaf = null;
    }
  }

  function scheduleStreamingRender() {
    if (_streamRenderRaf) return;
    _streamRenderRaf = requestAnimationFrame(function () {
      _streamRenderRaf = null;
      paintStreamingAssistant();
    });
  }

  /** Stream preview — server already strips harness noise; light client pass only. */
  function paintStreamingAssistant() {
    if (!_turn || !_turn.assistantText) return;
    _turn.typing = false;
    _turn.assistantBody.classList.add('assistant-body--streaming');
    _turn.assistantBody.textContent = _turn.assistantText;
    scrollOut();
  }

  function ensureMermaid() {
    if (typeof mermaid !== 'undefined') {
      if (!_mermaidReady) {
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: 'strict',
          theme: 'neutral',
          fontFamily: 'inherit',
        });
        _mermaidReady = Promise.resolve();
      }
      return _mermaidReady;
    }
    return null;
  }

  function renderMermaidBlocks(root) {
    if (!root) return;
    const blocks = root.querySelectorAll('pre.mermaid-source');
    if (!blocks.length) return;
    const ready = ensureMermaid();
    if (!ready) return;
    ready.then(function () {
      blocks.forEach(function (pre) {
        if (pre.dataset.mermaidDone === '1') return;
        pre.dataset.mermaidDone = '1';
        const code = pre.querySelector('code');
        const src = (code && code.textContent) || pre.textContent || '';
        if (!src.trim()) return;
        const host = document.createElement('div');
        host.className = 'mermaid-diagram';
        host.textContent = src.trim();
        pre.replaceWith(host);
        mermaid.run({ nodes: [host], suppressErrors: true }).then(function () {
          if (!host.querySelector('svg')) {
            throw new Error('empty svg');
          }
        }).catch(function () {
          const fallback = document.createElement('pre');
          fallback.className = 'mermaid-error';
          fallback.textContent = T('Diagram could not be rendered.') + '\n' + src.trim();
          host.replaceWith(fallback);
        });
      });
    });
  }

  function clearHeartbeat() {
    if (_heartbeatTimer) {
      clearInterval(_heartbeatTimer);
      _heartbeatTimer = null;
    }
  }

  function startHeartbeat() {
    clearHeartbeat();
    _hasRunOutput = false;
    setStatusLine(T('Agent running...'), 'Agent running...');
    _heartbeatTimer = setInterval(function () {
      if (!_running || _hasRunOutput) return;
      setStatusLine(T('Agent running...'), 'Agent running...');
    }, 4000);
  }

  function noteRunOutput() {
    _hasRunOutput = true;
    clearHeartbeat();
    const bar = $('console-status-bar');
    if (bar && bar.getAttribute('data-i18n-key') === 'Agent running...') {
      setStatusLine('');
    }
  }

  function formatModelLabel(model) {
    if (!model) return '—';
    var s = String(model);
    var slash = s.lastIndexOf('/');
    if (slash >= 0 && slash < s.length - 1) return s.slice(slash + 1);
    return s;
  }

  function appendModelOption(select, model, selected) {
    var opt = document.createElement('option');
    opt.value = model;
    opt.textContent = formatModelLabel(model);
    opt.title = model;
    if (selected) opt.selected = true;
    select.appendChild(opt);
  }

  function updateAgentPickerLayout() {
    var row = document.querySelector('.agent-toolbar-row');
    var picker = $('agent-picker');
    if (!row || !picker) return;
    if (_agents.length <= 1) {
      row.classList.add('agent-toolbar-row--single');
      picker.setAttribute('hidden', '');
    } else {
      row.classList.remove('agent-toolbar-row--single');
      picker.removeAttribute('hidden');
    }
  }

  var _STUDIO_ORDER = ['claude', 'copilot', 'cursor', 'codex', 'opencode'];
  /* Start with the same agent as Home: the picked one (studio_agent) -> first logged-in agent (Studio order) -> first agent.
     Contract: tests/dx_agent_dev/test_studio_agent_console_browser.py */
  function initialAgent(agents, studio) {
    const names = agents.map(function (a) { return a.name; });
    if (studio && names.indexOf(studio.agent) !== -1) return studio.agent;
    for (let i = 0; i < _STUDIO_ORDER.length; i++) {
      const a = agents.find(function (x) { return x.name === _STUDIO_ORDER[i]; });
      if (a && a.authenticated === true) return a.name;
    }
    return names[0];
  }

  function saveStudioAgent() {
    const agentSel = $('agent-select');
    const modelSel = $('model-select');
    if (!agentSel || !agentSel.value) return;
    fetch('api/studio/agent', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent: agentSel.value, model: (modelSel && modelSel.value) || null })
    }).catch(function () { /* the pick still applies to this page */ });
  }

  function fillAgentControls(agents, studio) {
    _agents = agents || [];
    const controls = $('agent-controls');
    const agentSel = $('agent-select');
    const modelSel = $('model-select');
    if (!controls || !agentSel || !modelSel) return;
    if (_agents.length === 0) { controls.setAttribute('hidden', ''); return; }
    agentSel.innerHTML = '';
    _agents.forEach(function (a) {
      const opt = document.createElement('option');
      opt.value = a.name;
      opt.textContent = a.name;
      agentSel.appendChild(opt);
    });
    updateAgentPickerLayout();
    const first = initialAgent(_agents, studio);
    agentSel.value = first;
    fillModels(_agents.find(function (x) { return x.name === first; }));
    if (!_agentControlsBound) {
      _agentControlsBound = true;
      agentSel.addEventListener('change', function () {
        const found = _agents.find(function (x) { return x.name === agentSel.value; });
        if (modelSel) delete modelSel.dataset.userPicked;  // another agent: start from that agent's default model
        fillModels(found);
        saveStudioAgent();
      });
    }
    if (!_modelHintBound) {
      _modelHintBound = true;
      modelSel.addEventListener('change', function () {
        // Keep the user's model pick when the CLI list is refetched or the language changes.
        modelSel.dataset.userPicked = '1';
        updateModelQualityHint();
        saveStudioAgent();
      });
    }
    updateModelQualityHint();
    controls.removeAttribute('hidden');
  }

  function updateAuthBadge(agent) {
    const badge = $('agent-auth-badge');
    if (!badge) return;
    if (!agent || agent.authenticated == null) {
      badge.setAttribute('hidden', '');
      badge.textContent = '';
      badge.className = 'agent-auth-badge';
      return;
    }
    badge.removeAttribute('hidden');
    if (agent.authenticated === true) {
      badge.innerHTML = (typeof DXIcon === 'function') ? DXIcon('check') : '';
      badge.className = 'agent-auth-badge ok';
      badge.title = T('Logged in');
    } else {
      badge.innerHTML = (typeof DXIcon === 'function') ? DXIcon('alert') : '';
      badge.className = 'agent-auth-badge warn';
      badge.title = T('Login required');
    }
  }

  function fillEfforts(agent) {
    const ctrl = $('effort-control');
    const sel = $('effort-select');
    if (!ctrl || !sel) return;
    const efforts = (agent && agent.reasoning_efforts) || [];
    sel.innerHTML = '';
    if (efforts.length === 0) { ctrl.setAttribute('hidden', ''); return; }
    efforts.forEach(function (e) {
      const opt = document.createElement('option');
      opt.value = e;
      opt.textContent = e;
      if (agent.default_effort === e) opt.selected = true;
      sel.appendChild(opt);
    });
    ctrl.removeAttribute('hidden');
  }

  function showLoginHint(agent) {
    const box = $('agent-login-hint');
    if (!box) return;
    if (!agent || agent.authenticated !== false) { box.setAttribute('hidden', ''); box.innerHTML = ''; return; }
    fetch('/api/agent/login/status?agent=' + encodeURIComponent(agent.name))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        const hint = (d && d.hint) || (agent.name + ' login');
        box.innerHTML = '';
        const span = document.createElement('span');
        span.textContent = T('Login required') + ': ';
        const code = document.createElement('code');
        code.textContent = hint;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = T('Re-check');
        btn.addEventListener('click', checkStatus);
        box.appendChild(span); box.appendChild(code); box.appendChild(document.createTextNode(' ')); box.appendChild(btn);
        box.removeAttribute('hidden');
      })
      .catch(function () {});
  }

  function fillModels(agent) {
    fillEfforts(agent);
    showLoginHint(agent);
    updateAuthBadge(agent);
    const modelSel = $('model-select');
    if (!modelSel) return;
    modelSel.innerHTML = '';
    const models = (agent && agent.models) || [];
    if (models.length === 0) {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = T('Default (no model picker)');
      modelSel.appendChild(opt);
      modelSel.disabled = true;
      return;
    }
    modelSel.disabled = false;
    models.forEach(function (m) {
      appendModelOption(modelSel, m, agent.default_model === m);
    });
    refreshModelsFromCli(agent);
    updateModelQualityHint();
  }

  function refreshModelsFromCli(agent) {
    if (!agent || !agent.name) return;
    const modelSel = $('model-select');
    if (!modelSel) return;
    fetch('/api/agent/models?agent=' + encodeURIComponent(agent.name))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        const live = (d && d.models) || [];
        const sel = $('agent-select');
        if (!live.length || !sel || sel.value !== agent.name) return;
        const prev = modelSel.value;
        const def = d.default_model;
        // The static default (prev) must not win over the CLI's real default model (e.g. copilot's claude-sonnet-5).
        const picked = modelSel.dataset.userPicked === '1' && live.indexOf(prev) !== -1;
        const keep = picked ? prev : (def && live.indexOf(def) !== -1 ? def : prev);
        modelSel.innerHTML = '';
        live.forEach(function (m) {
          appendModelOption(modelSel, m, m === keep);
        });
        modelSel.disabled = false;
        updateModelQualityHint();
      })
      .catch(function () {});
  }

  function isRecommendedModel(model) {
    if (!model) return true;
    const m = String(model).trim().toLowerCase();
    if (!m || m === '—') return true;
    if (m === 'auto' || m.includes('auto')) return false;
    // An alias without a version points at the newest of that family
    if (m === 'opus' || m === 'sonnet') return true;
    return _RECOMMENDED_MODEL.test(m);
  }

  function updateModelQualityHint() {
    const box = $('model-quality-hint');
    const modelSel = $('model-select');
    if (!box || !modelSel) return;
    const model = modelSel.value;
    if (!model || isRecommendedModel(model)) {
      box.setAttribute('hidden', '');
      box.textContent = '';
      return;
    }
    box.textContent = T('Current model may reduce instruction following quality.') + ' '
      + T('Recommended: Claude Sonnet 4.6+ or Opus 4.6+ for best harness following.');
    box.removeAttribute('hidden');
  }

  function selectedAgent() {
    const s = $('agent-select');
    return (s && s.value) || null;
  }
  function selectedModel() {
    const s = $('model-select');
    return (s && s.value) || null;
  }
  function selectedEffort() {
    const c = $('effort-control');
    const s = $('effort-select');
    if (!c || c.hasAttribute('hidden') || !s) return null;
    return s.value || null;
  }

  /** Target workdir the agent runs in (cwd) — mirrors the original SCENARIO_WORKDIRS. */
  function selectedTarget() {
    const s = $('target-select');
    return (s && s.value) || 'suite';
  }

  /** Interaction mode for the run — "interactive" (default) or "autopilot". */
  function selectedMode() {
    const s = $('mode-select');
    return (s && s.value) || 'interactive';
  }

  function out() { return $('console-output'); }

  function scrollOut() {
    const o = out();
    if (o) o.scrollTop = o.scrollHeight;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function extractModelNotice(text) {
    const patterns = [
      /(?:^|\n)[═=]{3,}\s*\r?\n⚠\s*DX-AGENT-DEV:\s*MODEL NOTICE([\s\S]*?)(?:[═=]{3,}\s*\r?\n|$)/gi,
      /(?:^|\n)⚠\s*DX-AGENT-DEV:\s*MODEL NOTICE([\s\S]*?)(?=\n\n|\r?\n(?=[A-Za-z0-9\u0080-\uFFFF*#]))/gi,
    ];
    let notice = '';
    let body = text || '';
    patterns.forEach(function (pat) {
      body = body.replace(pat, function (_full, inner) {
        notice = (inner || '').replace(/^[═=\s⚠]+/, '').replace(/[═=]{3,}\s*$/, '').trim();
        return '\n';
      });
    });
    return { body: body, notice: notice };
  }

  function buildModelNoticeHtml(notice) {
    if (!notice) return '';
    return '<details class="agent-model-notice" open>'
      + '<summary>' + escapeHtml(T('Model quality notice')) + '</summary>'
      + '<div class="notice-body">' + escapeHtml(notice) + '</div>'
      + '</details>';
  }

  function sanitizeAssistantText(text) {
    if (!text) return { body: '', notice: '' };
    let parsed = extractModelNotice(text);
    let s = parsed.body;
    s = s.replace(/\[DX-AGENT-DEV:\s*START\][^\n]*on-device NPU[^\n]*/gi, '');
    s = s.replace(/\[DX-AGENT-DEV:\s*START\]/gi, '');
    s = s.replace(/\[DX-AGENT-DEV:\s*DONE[^\]]*\]/gi, '');
    s = s.replace(/^\[DX-AGENT-DEV:\s*START\]\s*\r?\n?/gim, '');
    s = s.replace(/^\[DX-AGENT-DEV:\s*DONE[^\]]*\]\s*\r?\n?/gim, '');
    s = s.replace(/```[\s\S]*?████████[\s\S]*?on-device NPU[\s\S]*?```/gi, '');
    s = s.replace(/```[^`\n]*[█░][^`]*on-device NPU[^`]*```/gi, '');
    s = s.replace(/(?:^|\n)(?:[^\n]*[█░][^\n]*\n)+[^\n]*on-device NPU[^\n]*\n?/gi, '\n');
    s = s.replace(/(?:^|\n)Syntax error in text\s*(?:\n(?:mermaid version[^\n]*)?)?/gi, '\n');
    s = s.replace(/^\s*\n{2,}/, '').trim();
    return { body: s, notice: parsed.notice };
  }

  function renderMarkdown(text) {
    if (!text) return '';
    const parsed = sanitizeAssistantText(text);
    let body = parsed.body;
    var notice = parsed.notice || (_turn && _turn.modelNotice) || '';
    if (typeof DXMarkdownRender !== 'undefined') {
      body = DXMarkdownRender.repairCodeFences(body);
      body = DXMarkdownRender.normalizeBareMermaid(body);
    }
    const mermaidErr = typeof T === 'function' ? T('Diagram could not be rendered.') : 'Diagram could not be rendered.';
    let html = typeof DXMarkdownRender !== 'undefined'
      ? DXMarkdownRender.render(body, { mermaidErrorLabel: mermaidErr })
      : escapeHtml(body);
    if (parsed.notice) {
      html = buildModelNoticeHtml(parsed.notice) + html;
    } else if (notice) {
      html = buildModelNoticeHtml(notice) + html;
    }
    return html;
  }

  function applySpecLayout() {
    if (!_turn || !_turn.assistantWrap) return;
    const spec = typeof DXMarkdownRender !== 'undefined'
      && DXMarkdownRender.isSpecContent(_turn.assistantText);
    _turn.assistantWrap.classList.toggle('assistant-line--spec', !!spec);
  }

  function setStatusLine(text, i18nKey) {
    const bar = $('console-status-bar');
    if (!bar) return;
    bar.textContent = text || '';
    bar.hidden = !text;
    if (i18nKey) bar.setAttribute('data-i18n-key', i18nKey);
    else bar.removeAttribute('data-i18n-key');
  }

  function setBadge(key, cls) {
    const b = $('status-badge');
    if (!b) return;
    b.textContent = T(key);
    b.dataset.i18nKey = key;
    b.className = 'status-badge ' + (cls || '');
  }

  function beginTurn(userText) {
    const root = out();
    if (!root) return;

    const block = document.createElement('div');
    block.className = 'chat-turn';

    const userEl = document.createElement('div');
    userEl.className = 'user-line';
    userEl.textContent = userText;
    block.appendChild(userEl);

    const assistantWrap = document.createElement('div');
    assistantWrap.className = 'assistant-line';
    const assistantBody = document.createElement('div');
    assistantBody.className = 'assistant-body';
    assistantBody.innerHTML = '<div class="console-typing"><span></span><span></span><span></span></div>';
    assistantWrap.appendChild(assistantBody);
    block.appendChild(assistantWrap);

    const activity = document.createElement('details');
    activity.className = 'activity-panel';
    activity.hidden = true;
    const summary = document.createElement('summary');
    summary.className = 'activity-summary';
    summary.textContent = T('Agent activity') + ' (0)';
    activity.appendChild(summary);
    const activityBody = document.createElement('div');
    activityBody.className = 'activity-body';
    activity.appendChild(activityBody);
    block.appendChild(activity);

    root.appendChild(block);
    scrollOut();

    _turn = {
      block: block,
      assistantWrap: assistantWrap,
      assistantBody: assistantBody,
      activity: activity,
      activitySummary: summary,
      activityBody: activityBody,
      activityCount: 0,
      assistantText: '',
      typing: true,
    };
  }

  function updateAssistantView(fullRender) {
    if (!_turn) return;
    if (_turn.typing && !_turn.assistantText) return;
    _turn.typing = false;
    if (_turn.assistantText) {
      if (fullRender) {
        cancelStreamingRender();
        _turn.assistantBody.classList.remove('assistant-body--streaming');
        _turn.assistantBody.innerHTML = renderMarkdown(_turn.assistantText);
        renderMermaidBlocks(_turn.assistantBody);
        applySpecLayout();
      } else {
        scheduleStreamingRender();
        return;
      }
    } else {
      cancelStreamingRender();
      _turn.assistantBody.classList.remove('assistant-body--streaming');
      _turn.assistantBody.innerHTML = '<span class="assistant-empty">' + escapeHtml(T('(No response)')) + '</span>';
    }
    scrollOut();
  }

  function applyAssistantText(text, opts) {
    if (!_turn || !text) return;
    if (opts && opts.final) {
      _turn.assistantText = text;
    } else if (opts && opts.delta) {
      _turn.assistantText += text;
    } else if (!_turn.assistantText || text.length >= _turn.assistantText.length) {
      _turn.assistantText = text;
    } else {
      _turn.assistantText += text;
    }
    updateAssistantView(!!(opts && opts.final));
  }

  function appendActivity(text, cls) {
    if (!_turn || !text) return;
    _turn.activity.hidden = false;
    _turn.activityCount += 1;
    _turn.activitySummary.textContent = T('Agent activity') + ' (' + _turn.activityCount + ')';
    const line = document.createElement('div');
    line.className = 'activity-item ' + (cls || 'log');
    line.textContent = text;
    _turn.activityBody.appendChild(line);
    scrollOut();
  }

  function appendError(text) {
    const root = out();
    if (!root) return;
    const el = document.createElement('div');
    el.className = 'error-line';
    el.textContent = text;
    root.appendChild(el);
    scrollOut();
  }

  function renderEvent(ev) {
    if (!ev || ev.type === 'ping' || ev.hidden) return;
    switch (ev.type) {
      case 'degraded':
        showDegradedGallery(ev);
        break;
      case 'message':
        noteRunOutput();
        if (ev.model_notice && _turn) _turn.modelNotice = ev.model_notice;
        applyAssistantText(ev.text || '', { delta: ev.delta, final: ev.final });
        break;
      case 'command':
        noteRunOutput();
        appendActivity(ev.text, 'command');
        break;
      case 'log':
        noteRunOutput();
        appendActivity(ev.text, 'log');
        break;
      case 'error':
        noteRunOutput();
        if (_stopRequested && /^exit -?\d+$/.test(String(ev.text || '').trim())) break;
        appendError(ev.text);
        _runFailed = true;
        setBadge('Failed', 'failed');
        setStatusLine('');
        break;
      case 'artifacts':
        // Where the agent built the app (the target project's dx-agent-dev/<session>/); preferred over done's Studio tracking folder
        if (Array.isArray(ev.dirs) && ev.dirs.length) {
          const where = ev.dirs.join(', ');
          setStatusLine(T('App written to') + ' ' + where, null);
          const bar = $('console-status-bar');
          if (bar) {
            bar.setAttribute('data-i18n-prefix', 'App written to');
            bar.setAttribute('data-session-dir', where);
          }
        }
        break;
      case 'status':
        if (ev.text) {
          noteRunOutput();
          setStatusLine(ev.text);
        }
        break;
      case 'done':
        clearHeartbeat();
        cancelStreamingRender();
        if (ev.conversation_id) _conversationId = ev.conversation_id;
        if (_turn) updateAssistantView(true);
        if (_stopRequested) setBadge('Stopped', 'failed');
        else if (_runFailed) setBadge('Failed', 'failed');
        else setBadge('Completed', 'ok');
        if (ev.session_dir) {
          var statusBar = $('console-status-bar');
          setStatusLine(T('Output saved to') + ' ' + ev.session_dir, null);
          if (statusBar) {
            statusBar.setAttribute('data-i18n-prefix', 'Output saved to');
            statusBar.setAttribute('data-session-dir', ev.session_dir);
          }
        } else {
          setStatusLine('');
        }
        _turn = null;
        releaseRunLock();
        break;
      default:
        break;
    }
  }

  async function runPrompt(rawPrompt) {
    if (_running) {
      setStatusLine(T('Agent is still running. Please wait for the current reply to finish.'));
      return;
    }
    _running = true;
    _stopRequested = false;
    setConsoleBusy(true);
    _runFailed = false;
    setBadge('Running...', 'running');
    startHeartbeat();
    beginTurn(rawPrompt);
    try {
      const resp = await fetch('/api/agent/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: rawPrompt,
          conversation_id: _conversationId,
          lang: getLang(),
          agent: selectedAgent(),
          model: selectedModel(),
          effort: selectedEffort(),
          target: selectedTarget(),
          mode: selectedMode(),
        }),
      });
      if (!resp.ok) {
        if (resp.status === 409) appendError(T('Agent is busy, please wait.'));
        else appendError('HTTP ' + resp.status);
        setBadge('Failed', 'failed');
        _turn = null;
        releaseRunLock();
        return;
      }
      await _consumeStream(resp);
      finishWithoutDone();
    } catch (e) {
      clearHeartbeat();
      appendError(String((e && e.message) || e));
      setBadge('Failed', 'failed');
      _turn = null;
    } finally {
      clearHeartbeat();
      releaseRunLock();
    }
  }

  /* Read the SSE body and render it. Starting a run and attaching to a running one share this code;
     if attaching drew differently, "picked up" would be a lie. */
  async function _consumeStream(resp) {
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const frag = line.slice(6);
        if (frag === '[DONE]') continue;
        let evt;
        try { evt = JSON.parse(frag); } catch (e) { continue; }
        renderEvent(evt);
      }
    }
  }

  /* Picks up here a run started from home, so a user who navigates over sees it continue. */
  /* The request home hands over (/agent/#ask=…): the first line when status does not know it */
  function _askFromHash() {
    const m = /(?:^#|&)ask=([^&]*)/.exec(window.location.hash || '');
    if (!m) return '';
    try { return decodeURIComponent(m[1].replace(/\+/g, ' ')); } catch (e) { return ''; }
  }

  async function attachIfRunning(st) {
    if (!st || !st.run_id || st.run_done || _running) return false;
    _running = true;
    _stopRequested = false;
    setConsoleBusy(true);
    _runFailed = false;
    setBadge('Running...', 'running');
    startHeartbeat();
    /* The conversation cell comes first: without it the message and command renderers drop everything
       (`if (!_turn) return`), and a user arriving from home would see no live output. The first line is the
       run's request (status), else the #ask home handed over. Replying here continues the same conversation
       (conversation, mode). */
    beginTurn(st.run_prompt || _askFromHash() || T('Resumed run'));
    if (st.run_conversation_id) _conversationId = st.run_conversation_id;
    const modeSel = $('mode-select');
    if (modeSel && st.run_mode) modeSel.value = st.run_mode;
    try {
      const resp = await fetch('/api/agent/run/events?from=0');
      if (!resp.ok || !resp.body) return false;
      await _consumeStream(resp);
      finishWithoutDone();
      return true;
    } catch (e) {
      return false;
    } finally {
      clearHeartbeat();
      releaseRunLock();
    }
  }

  function _localized(obj, fallback) {
    if (!obj) return fallback || '';
    const lang = getLang();
    return obj[lang] || obj.en || fallback || '';
  }

  /** Render `` `code` `` spans as <code> after escaping the rest — no full markdown needed here. */
  function _renderInlineCode(text) {
    const parts = String(text || '').split(/(`[^`]+`)/g);
    return parts.map(function (p) {
      if (p.length >= 2 && p[0] === '`' && p[p.length - 1] === '`') {
        return '<code>' + esc(p.slice(1, -1)) + '</code>';
      }
      return esc(p);
    }).join('');
  }

  function _buildInstallOptionsList(options) {
    const ul = document.createElement('ul');
    ul.className = 'gallery-install-options';
    options.forEach(function (opt) {
      const li = document.createElement('li');
      let statusText;
      if (!opt.installed) {
        statusText = T('Not installed') + ' — ' + T('Install, then log in');
      } else if (opt.authenticated === false) {
        statusText = T('Login required');
      } else if (opt.authenticated === true) {
        statusText = T('Logged in');
      } else {
        statusText = T('Installed');
      }
      let html = '<b>' + esc(opt.displayName || opt.agent) + '</b> — ' + esc(statusText);
      if (opt.loginHint) html += ' (<code>' + esc(opt.loginHint) + '</code>)';
      li.innerHTML = html;
      ul.appendChild(li);
    });
    return ul;
  }

  /**
   * ev: optional degraded payload (SSE 'degraded' event or /api/agent/status response) with
   * localized `title`/`detail` objects and (cli_missing only) an `installOptions` list. Falls
   * back to a generic message when no payload is given (defensive — keeps old callers working).
   */
  function showDegradedGallery(ev) {
    const form = $('console-form');
    if (form) form.setAttribute('hidden', '');
    const gallery = $('showcase-gallery');
    if (!gallery) return;
    gallery.innerHTML = '';
    if (ev && ev.title && ev.detail) {
      const title = document.createElement('p');
      title.className = 'gallery-note gallery-note--title';
      title.innerHTML = '<b>' + esc(_localized(ev.title)) + '</b>';
      gallery.appendChild(title);
      const detail = document.createElement('p');
      detail.className = 'gallery-note';
      detail.innerHTML = _renderInlineCode(_localized(ev.detail));
      gallery.appendChild(detail);
      if (Array.isArray(ev.installOptions) && ev.installOptions.length) {
        gallery.appendChild(_buildInstallOptionsList(ev.installOptions));
      }
    } else {
      const note = document.createElement('p');
      note.className = 'gallery-note';
      note.textContent = T('The agent is unavailable in this environment. Browse the showcases.');
      gallery.appendChild(note);
    }
    gallery.removeAttribute('hidden');
  }

  async function renderExamplePanels() {
    const left = $('examples-left');
    const right = $('examples-right');
    if (!left || !right) return;
    if (_showcaseCache === null) {
      if (!_showcasePromise) _showcasePromise = api('/api/agent/showcases');
      let data;
      try { data = await _showcasePromise; } catch (e) { data = {}; }
      _showcaseCache = (data && data.showcases) || [];
    }
    const lang = getLang();
    const items = _showcaseCache;
    const half = Math.ceil(items.length / 2);

    function buildCard(sc) {
      const a = document.createElement('a');
      a.className = 'example-card';
      a.href = sc.url || '#';
      a.target = '_blank';
      a.rel = 'noopener';
      const titleText = (sc.title && (sc.title[lang] || sc.title.en)) || sc.id;
      if (sc.media) {
        const img = document.createElement('img');
        img.className = 'example-thumb';
        img.loading = 'lazy';
        img.decoding = 'async';
        img.src = '/static/' + sc.media;
        img.alt = titleText;
        a.appendChild(img);
      }
      const t = document.createElement('b');
      t.className = 'example-title';
      t.textContent = titleText;
      const tag = document.createElement('span');
      tag.className = 'example-tag';
      tag.textContent = (sc.tagline && (sc.tagline[lang] || sc.tagline.en)) || '';
      a.appendChild(t);
      a.appendChild(tag);
      return a;
    }

    function fill(panel, slice) {
      panel.innerHTML = '';
      slice.forEach(function (sc) { panel.appendChild(buildCard(sc)); });
    }

    fill(left, items.slice(0, half));
    fill(right, items.slice(half));
  }

  async function checkStatus() {
    let st;
    try { st = await api('/api/agent/status'); } catch (e) { st = {}; }
    if (st && st.available) {
      setBadge('Ready', 'ok');
      fillAgentControls(st.agents, st.studio_agent);
      /* Attach to a run already in progress (the case when arriving from home). */
      if (st.run_id && !st.run_done) attachIfRunning(st);
    } else {
      showDegradedGallery(st);
    }
  }

  function relocalizeOpenTurns() {
    const root = out();
    if (!root) return;
    root.querySelectorAll('.activity-summary').forEach(function (summary) {
      var m = summary.textContent.match(/\((\d+)\)\s*$/);
      var n = m ? m[1] : '0';
      summary.textContent = T('Agent activity') + ' (' + n + ')';
    });
    root.querySelectorAll('.assistant-empty').forEach(function (el) {
      el.textContent = T('(No response)');
    });
    if (_turn && _turn.assistantBody && _turn.assistantText) {
      _turn.assistantBody.innerHTML = renderMarkdown(_turn.assistantText);
      renderMermaidBlocks(_turn.assistantBody);
    }
  }

  function relocalizeStatusBar() {
    var bar = $('console-status-bar');
    if (!bar || bar.hidden) return;
    var key = bar.getAttribute('data-i18n-key');
    if (key) setStatusLine(T(key), key);
    else if (bar.getAttribute('data-i18n-prefix')) {
      var prefix = bar.getAttribute('data-i18n-prefix');
      var dir = bar.getAttribute('data-session-dir') || '';
      setStatusLine(T(prefix) + (dir ? ' ' + dir : ''), null);
    }
  }

  function applyLang() {
    const input = $('console-input');
    if (input) input.placeholder = T('Describe what you want to build...');
    const outEl = $('console-output');
    if (outEl) outEl.dataset.emptyHint = T('Plans, commands and results from the agent appear here. Describe an app below, or start from a showcase.');
    const b = $('status-badge');
    if (b && b.dataset.i18nKey) b.textContent = T(b.dataset.i18nKey);
    const note = document.querySelector('.gallery-note');
    if (note) note.textContent = T('The agent is unavailable in this environment. Browse the showcases.');
    const modeSel = $('mode-select');
    if (modeSel) {
      Array.prototype.forEach.call(modeSel.options, function (opt) {
        if (opt.dataset.i18n) opt.textContent = T(opt.dataset.i18n);
      });
    }
    const agentSel = $('agent-select');
    const agent = _agents.find(function (x) { return x.name === (agentSel && agentSel.value); }) || _agents[0];
    if (agent) {
      // Only the language changed: keep the picked model and effort level (do not reset to defaults)
      const modelSel = $('model-select'), effortSel = $('effort-select');
      const keepModel = modelSel ? modelSel.value : '', picked = modelSel ? modelSel.dataset.userPicked : '';
      const keepEffort = effortSel ? effortSel.value : '';
      fillModels(agent);
      if (modelSel && keepModel && Array.prototype.some.call(modelSel.options, function (o) { return o.value === keepModel; })) {
        modelSel.value = keepModel;
        if (picked) modelSel.dataset.userPicked = picked;
      }
      if (effortSel && keepEffort && Array.prototype.some.call(effortSel.options, function (o) { return o.value === keepEffort; })) {
        effortSel.value = keepEffort;
      }
    }
    updateModelQualityHint();
    renderExamplePanels();
    relocalizeOpenTurns();
    relocalizeStatusBar();
  }

  function init() {
    const form = $('console-form');
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        const input = $('console-input');
        const prompt = (input.value || '').trim();
        if (!prompt) return;
        if (_running) {
          setStatusLine(T('Agent is still running. Please wait for the current reply to finish.'));
          return;
        }
        input.value = '';
        runPrompt(prompt);
      });
    }
    const stopBtn = $('console-stop');
    if (stopBtn) stopBtn.addEventListener('click', stopRun);
    applyLang();
    if (typeof DXI18n !== 'undefined' && DXI18n.onLangChange) DXI18n.onLangChange(applyLang);
    checkStatus();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
