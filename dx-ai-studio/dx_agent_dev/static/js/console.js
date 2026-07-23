/* DX Agent Dev — Agent Console (채팅 UX + Activity 패널 + SSE) */
(function () {
  let _running = false;
  let _agents = [];
  let _showcaseCache = null;
  let _showcasePromise = null;
  let _turn = null;
  let _heartbeatTimer = null;
  let _agentControlsBound = false;
  let _modelHintBound = false;

  const _RECOMMENDED_MODEL = /sonnet-4\.[6-9]|opus-4\.[6-9]|claude-sonnet-4-[6-9]|claude-opus-4-[68]/i;
  let _hasRunOutput = false;

  let _mermaidReady = null;
  let _streamRenderRaf = null;
  /** Server-issued conversation id for multi-turn CLI resume. */
  let _conversationId = null;

  function setConsoleBusy(busy) {
    const form = $('console-form');
    const input = $('console-input');
    const send = $('console-send');
    if (form) form.classList.toggle('console-form--busy', !!busy);
    if (input) input.disabled = !!busy;
    if (send) send.disabled = !!busy;
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

  function fillAgentControls(agents) {
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
    fillModels(_agents[0]);
    if (!_agentControlsBound) {
      _agentControlsBound = true;
      agentSel.addEventListener('change', function () {
        const found = _agents.find(function (x) { return x.name === agentSel.value; });
        fillModels(found);
      });
    }
    if (!_modelHintBound) {
      _modelHintBound = true;
      modelSel.addEventListener('change', updateModelQualityHint);
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
      badge.textContent = '✓';
      badge.className = 'agent-auth-badge ok';
      badge.title = T('Logged in');
    } else {
      badge.textContent = '⚠';
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
        modelSel.innerHTML = '';
        live.forEach(function (m) {
          appendModelOption(modelSel, m, m === prev || (!prev && m === def));
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
        appendError(ev.text);
        setBadge('Failed', 'failed');
        setStatusLine('');
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
        setBadge('Completed', 'ok');
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
    setConsoleBusy(true);
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
      fillAgentControls(st.agents);
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
    else if (bar.getAttribute('data-i18n-prefix') === 'Output saved to') {
      var dir = bar.getAttribute('data-session-dir') || '';
      setStatusLine(T('Output saved to') + (dir ? ' ' + dir : ''), null);
    }
  }

  function applyLang() {
    const input = $('console-input');
    if (input) input.placeholder = T('Describe what you want to build...');
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
    if (agent) fillModels(agent);
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
    applyLang();
    if (typeof DXI18n !== 'undefined' && DXI18n.onLangChange) DXI18n.onLangChange(applyLang);
    checkStatus();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
