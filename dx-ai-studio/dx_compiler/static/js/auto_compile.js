/* auto_compile.js — Agentic Auto Compile wiring for DX Compiler GUI
 *
 * Binds #auto-compile-noninteractive (mode=autopilot) and
 * #auto-compile-interactive (mode=interactive) to the dx_agent_dev runner
 * via POST /agent/api/agent/run (SSE stream).
 *
 * On `done` with a session_dir, fetches /agentic/session-dxnn?dir=<session_dir>
 * and loads the .dxnn into the viewer via ViewerPanel.loadModel('dxnn', path).
 *
 * Interactive mode keeps a conversationId and shows a follow-up reply input
 * when the agent asks a question without producing a .dxnn.
 */
(function () {
  'use strict';

  function tr(key) {
    return (typeof T === 'function') ? T(key) : key;
  }

  var conversationId = null;   // tracked across interactive follow-ups
  var _running = false;
  var _agents = [];            // live agent metadata from /agent/api/agent/status

  var _RECOMMENDED_MODEL = /(sonnet|opus)[ -]?4\.(6|7|8|9)|(sonnet|opus)[ -]?[5-9]/i;

  function buildPrompt(model) {
    return (
      "Compile the model '" + model + "' to a DXNN for the DEEPX DX-M1 NPU. " +
      "If it is a name/ID/URL and no local ONNX exists, download it, convert to ONNX if needed, " +
      "then compile, verify (ONNX vs DXNN), and report the .dxnn path."
    );
  }

  function getLogPanel() { return document.getElementById('log-panel'); }
  function getLogContent() { return document.getElementById('log-content'); }

  function ensureLogVisible() {
    var panel = getLogPanel();
    if (panel) panel.style.display = '';
  }

  function appendLog(text) {
    ensureLogVisible();
    var el = getLogContent();
    if (!el) return;
    el.textContent += text + '\n';
    el.scrollTop = el.scrollHeight;
  }

  function setButtonsDisabled(disabled) {
    var b1 = document.getElementById('auto-compile-noninteractive');
    var b2 = document.getElementById('auto-compile-interactive');
    if (b1) b1.disabled = disabled;
    if (b2) b2.disabled = disabled;
  }

  function _removeReplyUI() {
    var existing = document.getElementById('agentic-reply-row');
    if (existing) existing.remove();
  }

  function showReplyUI(onSend) {
    _removeReplyUI();
    var container = document.getElementById('agentic-compile');
    if (!container) return;

    var row = document.createElement('div');
    row.id = 'agentic-reply-row';
    row.style.cssText = 'display:flex;gap:8px;margin-top:10px;align-items:center;';

    var inp = document.createElement('input');
    inp.type = 'text';
    inp.id = 'agentic-reply-input';
    inp.placeholder = tr('Reply to agent...');
    inp.style.cssText = 'flex:1;padding:6px 10px;border:1px solid var(--border,#ccc);border-radius:4px;font-size:0.9rem;';

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = tr('Send');
    btn.className = 'compile-btn';
    btn.style.cssText = 'padding:6px 14px;';

    function doSend() {
      var val = inp.value.trim();
      if (!val) return;
      _removeReplyUI();
      onSend(val);
    }

    btn.addEventListener('click', doSend);
    inp.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') doSend();
    });

    row.appendChild(inp);
    row.appendChild(btn);
    container.appendChild(row);

    setTimeout(function () { inp.focus(); }, 50);
  }

  /**
   * POST to /agent/api/agent/run and consume the SSE stream.
   * @param {object} payload  - request body
   * @param {string} mode     - "autopilot" | "interactive"
   */
  function runStream(payload, mode) {
    _running = true;
    setButtonsDisabled(true);
    _removeReplyUI();

    appendLog('[' + tr('Agentic Auto Compile') + '] ' +
              tr('Starting') + ' (' + mode + ')...');

    fetch('/agent/api/agent/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    .then(function (response) {
      if (!response.ok || !response.body) {
        return response.text().then(function (txt) {
          throw new Error(txt || ('HTTP ' + response.status));
        });
      }

      var reader = response.body.getReader();
      var decoder = new TextDecoder('utf-8');
      var buffer = '';
      var gotDxnn = false;

      // Accumulate SSE chunks; emit on blank-line delimiters
      function processChunk(done, value) {
        if (done) {
          if (buffer.trim()) processSSEBlock(buffer);
          onStreamEnd(gotDxnn, mode, payload);
          return;
        }

        buffer += decoder.decode(value, { stream: true });
        var blocks = buffer.split('\n\n');
        buffer = blocks.pop(); // keep incomplete tail

        for (var i = 0; i < blocks.length; i++) {
          var result = processSSEBlock(blocks[i]);
          if (result && result.dxnn) gotDxnn = true;
          if (result && result.conversationId) {
            conversationId = result.conversationId;
          }
        }

        reader.read().then(function (chunk) {
          processChunk(chunk.done, chunk.value);
        }).catch(handleStreamError);
      }

      reader.read().then(function (chunk) {
        processChunk(chunk.done, chunk.value);
      }).catch(handleStreamError);

      return null; // stream handled via reader
    })
    .catch(function (err) {
      appendLog('[' + tr('Error') + '] ' + String(err));
      _running = false;
      setButtonsDisabled(false);
    });
  }

  /**
   * Parse one SSE block (lines separated by \n) and handle it.
   * Returns { dxnn: bool, conversationId: string|null }.
   */
  function processSSEBlock(block) {
    var ret = { dxnn: false, conversationId: null };
    var lines = block.split('\n');
    var eventType = 'message';
    var dataStr = '';

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      if (line.startsWith('event:')) {
        eventType = line.slice(6).trim();
      } else if (line.startsWith('data:')) {
        dataStr = line.slice(5).trim();
      }
    }

    if (!dataStr) return ret;

    var data;
    try {
      data = JSON.parse(dataStr);
    } catch (e) {
      data = { text: dataStr };
    }

    // Track conversation_id from any event
    if (data && data.conversation_id) {
      ret.conversationId = data.conversation_id;
    }

    switch (eventType) {
      case 'status':
        appendLog('[status] ' + (data.message || dataStr));
        break;

      case 'message':
        appendLog('[agent] ' + (data.text || data.message || dataStr));
        break;

      case 'command':
        appendLog('[cmd] ' + (data.command || dataStr));
        break;

      case 'log':
        if (data.lines && data.lines.length) {
          appendLog(data.lines.join('\n'));
        } else {
          appendLog('[log] ' + (data.text || dataStr));
        }
        break;

      case 'error':
        appendLog('[' + tr('Error') + '] ' + (data.error || data.message || dataStr));
        break;

      case 'done':
        var sessionDir = data.session_dir || (data.data && data.data.session_dir);
        if (sessionDir) {
          appendLog('[done] session_dir: ' + sessionDir);
          loadDxnnFromSession(sessionDir);
          ret.dxnn = true;
        } else {
          appendLog('[done] ' + tr('Agentic run complete.'));
        }
        break;

      default:
        if (dataStr) {
          appendLog('[' + eventType + '] ' + dataStr);
        }
    }

    return ret;
  }

  /**
   * After the stream ends, decide whether to show a reply UI (interactive mode
   * when no .dxnn was produced — the agent likely asked a question).
   */
  function onStreamEnd(gotDxnn, mode, originalPayload) {
    _running = false;
    setButtonsDisabled(false);

    if (mode === 'interactive' && !gotDxnn && conversationId) {
      // Agent asked a question — show follow-up reply input
      appendLog('[' + tr('Agentic Auto Compile') + '] ' +
                tr('Agent is waiting for your reply.'));
      showReplyUI(function (replyText) {
        var followUp = {
          prompt: replyText,
          agent: originalPayload.agent,
          model: originalPayload.model,
          effort: originalPayload.effort,
          target: originalPayload.target,
          mode: 'interactive',
          conversation_id: conversationId,
        };
        runStream(followUp, 'interactive');
      });
    }
  }

  function handleStreamError(err) {
    appendLog('[' + tr('Error') + '] ' + tr('Stream error: ') + String(err));
    _running = false;
    setButtonsDisabled(false);
  }

  function loadDxnnFromSession(sessionDir) {
    fetch('/agentic/session-dxnn?dir=' + encodeURIComponent(sessionDir))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.ok && data.dxnn_path) {
          appendLog('[viewer] ' + tr('Loading DXNN:') + ' ' + data.dxnn_path);
          if (window.ViewerPanel && typeof ViewerPanel.loadModel === 'function') {
            ViewerPanel.loadModel('dxnn', data.dxnn_path);
          }
        } else {
          appendLog('[viewer] ' +
            tr('No .dxnn found in session dir yet.'));
        }
      })
      .catch(function (err) {
        appendLog('[viewer] ' + tr('Could not load DXNN:') + ' ' + String(err));
      });
  }

  /* ── LLM model / effort pickers (mirror dx_agent_dev console) ─ */
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

  function fillEfforts(agent) {
    var ctrl = document.getElementById('agentic-effort-control');
    var sel = document.getElementById('agentic-effort-select');
    if (!ctrl || !sel) return;
    var efforts = (agent && agent.reasoning_efforts) || [];
    sel.innerHTML = '';
    if (efforts.length === 0) { ctrl.setAttribute('hidden', ''); return; }
    efforts.forEach(function (e) {
      var opt = document.createElement('option');
      opt.value = e;
      opt.textContent = e;
      if (agent.default_effort === e) opt.selected = true;
      sel.appendChild(opt);
    });
    ctrl.removeAttribute('hidden');
  }

  function fillModels(agent) {
    fillEfforts(agent);
    var modelSel = document.getElementById('agentic-model-select');
    if (!modelSel) return;
    modelSel.innerHTML = '';
    var models = (agent && agent.models) || [];
    if (models.length === 0) {
      var opt = document.createElement('option');
      opt.value = '';
      opt.textContent = tr('Default (no model picker)');
      modelSel.appendChild(opt);
      modelSel.disabled = true;
      updateModelQualityHint();
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
    var modelSel = document.getElementById('agentic-model-select');
    var agentSel = document.getElementById('agentic-agent-select');
    if (!modelSel) return;
    fetch('/agent/api/agent/models?agent=' + encodeURIComponent(agent.name))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var live = (d && d.models) || [];
        if (!live.length || !agentSel || agentSel.value !== agent.name) return;
        var prev = modelSel.value;
        var def = d.default_model;
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
    var m = String(model).trim().toLowerCase();
    if (!m || m === '—') return true;
    if (m.indexOf('auto') >= 0) return false;
    return _RECOMMENDED_MODEL.test(m);
  }

  function updateModelQualityHint() {
    var box = document.getElementById('agentic-model-quality-hint');
    var modelSel = document.getElementById('agentic-model-select');
    if (!box || !modelSel) return;
    var model = modelSel.value;
    if (!model || isRecommendedModel(model)) {
      box.setAttribute('hidden', '');
      box.textContent = '';
      return;
    }
    box.textContent = tr('Current model may reduce instruction following quality.') + ' '
      + tr('Recommended: Claude Sonnet 4.6+ or Opus 4.6+ for best harness following.');
    box.removeAttribute('hidden');
  }

  function selectedModel() {
    var s = document.getElementById('agentic-model-select');
    return (s && !s.disabled && s.value) || null;
  }

  function selectedEffort() {
    var ctrl = document.getElementById('agentic-effort-control');
    var s = document.getElementById('agentic-effort-select');
    if (!ctrl || ctrl.hasAttribute('hidden') || !s) return null;
    return s.value || null;
  }

  function runAgentic(mode) {
    if (_running) return;

    var modelInput = document.getElementById('agentic-model-input');
    var agentSelect = document.getElementById('agentic-agent-select');

    var model = modelInput ? modelInput.value.trim() : '';
    if (!model) {
      appendLog(tr('Please enter a model name, path, or URL.'));
      return;
    }

    var agent = agentSelect ? agentSelect.value : '';

    // Reset conversation for new runs (non-follow-up)
    conversationId = null;
    _removeReplyUI();

    var payload = {
      prompt: buildPrompt(model),
      agent: agent,
      model: selectedModel(),
      effort: selectedEffort(),
      target: 'dx-compiler',
      mode: mode,       // "autopilot" or "interactive"
    };

    runStream(payload, mode);
  }

  /**
   * Fetches the live agent status and populates #agentic-agent-select.
   * - Agents where authenticated !== true are added as disabled options
   *   with a localized "(login required)" suffix.
   * - If no authenticated agents exist (or `available` is false), both
   *   compile buttons are disabled and a hint is shown in the log panel.
   * - Network / parse errors are caught; the picker is left empty and
   *   the buttons are disabled with a hint.
   */
  function populateAgenticAgents() {
    var select = document.getElementById('agentic-agent-select');
    if (!select) return;

    // Clear existing options and start with a disabled placeholder
    select.innerHTML = '';

    function showNoAgentHint() {
      setButtonsDisabled(true);
      ensureLogVisible();
      appendLog('[agent] ' + tr('No installed & authenticated agent'));
    }

    fetch('/agent/api/agent/status')
      .then(function (response) {
        if (!response.ok) {
          throw new Error('HTTP ' + response.status);
        }
        return response.json();
      })
      .then(function (data) {
        var agents = (data && Array.isArray(data.agents)) ? data.agents : [];
        var available = data && data.available;
        _agents = agents;

        // Build option list
        var firstAuthenticated = null;
        agents.forEach(function (agent) {
          var opt = document.createElement('option');
          var name = agent.name || '';
          opt.value = name;
          if (agent.authenticated === true) {
            opt.textContent = name;
            if (!firstAuthenticated) firstAuthenticated = opt;
          } else {
            opt.textContent = name + tr(' (login required)');
            opt.disabled = true;
          }
          select.appendChild(opt);
        });

        // Select the first authenticated agent
        if (firstAuthenticated) {
          firstAuthenticated.selected = true;
        }

        // Populate model / effort pickers for the selected agent
        var selName = select.value;
        var selAgent = agents.find(function (a) { return a.name === selName; });
        fillModels(selAgent);

        // Repopulate model / effort when the agent changes
        if (!select._agenticBound) {
          select._agenticBound = true;
          select.addEventListener('change', function () {
            var found = _agents.find(function (a) { return a.name === select.value; });
            fillModels(found);
          });
        }

        // Disable buttons when no authenticated agents or service unavailable
        var hasAuthenticated = !!firstAuthenticated;
        if (!available || !hasAuthenticated) {
          showNoAgentHint();
        }
      })
      .catch(function (err) {
        // Network error — leave picker empty, disable buttons, show hint
        appendLog('[agent] ' + tr('No installed & authenticated agent') +
                  ' (' + String(err) + ')');
        setButtonsDisabled(true);
      });
  }

  function bindButtons() {
    var btnNonInteractive = document.getElementById('auto-compile-noninteractive');
    var btnInteractive    = document.getElementById('auto-compile-interactive');

    if (btnNonInteractive) {
      btnNonInteractive.addEventListener('click', function () {
        runAgentic('autopilot');
      });
    }

    if (btnInteractive) {
      btnInteractive.addEventListener('click', function () {
        runAgentic('interactive');
      });
    }
  }

  function init() {
    bindButtons();
    populateAgenticAgents();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose for testing / external use
  window.AutoCompile = {
    buildPrompt: buildPrompt,
    runAgentic: runAgentic,
    populateAgenticAgents: populateAgenticAgents,
  };

})();
if (typeof registerCompilerLangRefresher === 'function') {
  registerCompilerLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
