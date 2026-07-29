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
  var _abort = null;           // AbortController for the in-flight /agent/api/agent/run
  var _agents = [];            // live agent metadata from /agent/api/agent/status

  // Recommended = harness-following-capable families: Sonnet/Opus 4.6+, any Sonnet/Opus 5+,
  // and GPT 5.4+ (covers gpt-5.6-*). Accepts dot or dash forms (4.8 / 4-8, 5.6 / 5-6).
  var _RECOMMENDED_MODEL = /(sonnet|opus)[ -]?4[.-][6-9]|(sonnet|opus)[ -]?[5-9]|gpt[ -]?5[.-][4-9]|gpt[ -]?[6-9]/i;

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

  var _lastLoggedText = null;
  function appendLog(text) {
    ensureLogVisible();
    var el = getLogContent();
    if (!el) return;
    // Collapse consecutive duplicates: the agent stream emits a turn's text as an
    // `assistant` block AND again as the final `result`, so the last message would print
    // twice (three times with the old partial-delta stream). Skip identical repeats.
    var norm = (text == null ? '' : String(text)).trim();
    if (norm && norm === _lastLoggedText) return;
    _lastLoggedText = norm;
    el.textContent += text + '\n';
    el.scrollTop = el.scrollHeight;
  }

  function setButtonsDisabled(disabled) {
    var b1 = document.getElementById('auto-compile-noninteractive');
    var b2 = document.getElementById('auto-compile-interactive');
    if (b1) b1.disabled = disabled;
    if (b2) b2.disabled = disabled;
  }

  // ── Persistent interactive chat input (under the Compiler Log) ─────────────────────
  // Mirrors the dx_agent_dev console: one always-present box that sends each line as a turn
  // in the SAME agent conversation. Shown when an interactive agentic run starts; disabled
  // while the agent is running, re-enabled when its turn ends (so the user can reply).
  function getChatRow()   { return document.getElementById('agentic-chat-row'); }
  function getChatInput() { return document.getElementById('agentic-chat-input'); }

  // The input stays ALWAYS typeable while the chat row is visible. It is NEVER disabled:
  // the agent (claude -p) is one-shot per turn, and a run can sit "running" for a long time
  // (rate limits, long tool calls) after it has already printed its question — greying the
  // box out in that window left the user unable to click or type their answer. Instead, the
  // box is always editable and sendChatReply() soft-guards on _running.
  function showAgenticChat(focusIt) {
    var row = getChatRow();
    if (row) row.style.display = '';
    var inp = getChatInput();
    var btn = document.getElementById('agentic-chat-send');
    if (inp) inp.disabled = false;
    if (btn) btn.disabled = false;
    if (focusIt && inp) {
      ensureLogVisible();
      setTimeout(function () {
        inp.focus();
        if (row) row.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 50);
    }
  }
  function hideAgenticChat() {
    var row = getChatRow();
    if (row) row.style.display = 'none';
  }

  // Send the current chat line as an interactive follow-up turn (same conversation).
  var _lastAgenticPayload = null;   // remembers agent/model/effort/target for follow-ups

  // Abort the in-flight run and tell the backend to kill the agent process, so a reply can
  // start a fresh resume turn without a 409 "agent busy".
  function cancelCurrentRun() {
    if (_abort) { try { _abort.abort(); } catch (e) { /* ignore */ } _abort = null; }
    try { fetch('/agent/api/agent/cancel', { method: 'POST' }); } catch (e) { /* best effort */ }
    _running = false;
  }

  // Poll /agent/api/agent/status until the runner reports not-busy (or a timeout), then cb().
  function _whenAgentFree(cb, tries) {
    tries = tries || 0;
    fetch('/agent/api/agent/status')
      .then(function (r) { return r.json(); })
      .then(function (s) {
        if (!s || !s.busy || tries >= 25) cb();          // ~5s max
        else setTimeout(function () { _whenAgentFree(cb, tries + 1); }, 200);
      })
      .catch(function () { cb(); });
  }

  function sendChatReply() {
    var inp = getChatInput();
    if (!inp) return;
    var val = inp.value.trim();
    if (!val) return;
    inp.value = '';
    var base = _lastAgenticPayload || {};
    var followUp = {
      prompt: val,
      agent: base.agent,
      model: base.model,
      effort: base.effort,
      target: base.target || 'dx-compiler',
      mode: 'interactive',
      conversation_id: conversationId,
    };
    // If a turn is still streaming (interactive agent asked a question but hasn't exited —
    // rate-limited or otherwise), interrupt it and resume with the user's answer. Never block
    // the user behind a stream that may never close on its own.
    if (_running) {
      appendLog('[' + tr('Agentic Auto Compile') + '] ' +
                tr('Sending your answer (interrupting the current step)…'));
      cancelCurrentRun();
      _whenAgentFree(function () { runStream(followUp, 'interactive'); });
      return;
    }
    runStream(followUp, 'interactive');
  }

  /**
   * POST to /agent/api/agent/run and consume the SSE stream.
   * @param {object} payload  - request body
   * @param {string} mode     - "autopilot" | "interactive"
   */
  function runStream(payload, mode) {
    _running = true;
    setButtonsDisabled(true);
    if (mode === 'interactive') {
      // Keep the chat row visible AND typeable while the agent's turn runs (the user may
      // answer at any time — sendChatReply() will interrupt this run and resume).
      showAgenticChat(false);
    }

    appendLog('[' + tr('Agentic Auto Compile') + '] ' +
              tr('Starting') + ' (' + mode + ')...');

    // AbortController so a reply can interrupt a still-open stream (an interactive agent that
    // asked a question but hasn't exited — e.g. rate-limited mid-turn — would otherwise keep
    // the stream open forever, leaving the user unable to answer).
    _abort = (typeof AbortController !== 'undefined') ? new AbortController() : null;
    fetch('/agent/api/agent/run', {
      signal: _abort ? _abort.signal : undefined,
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
      var sessionDir = null;

      // Accumulate SSE chunks; emit on blank-line delimiters
      function processChunk(done, value) {
        if (done) {
          if (buffer.trim()) {
            var tail = processSSEBlock(buffer);
            if (tail && tail.sessionDir) sessionDir = tail.sessionDir;
            if (tail && tail.conversationId) conversationId = tail.conversationId;
          }
          onStreamEnd(sessionDir, mode, payload);
          return;
        }

        buffer += decoder.decode(value, { stream: true });
        var blocks = buffer.split('\n\n');
        buffer = blocks.pop(); // keep incomplete tail

        for (var i = 0; i < blocks.length; i++) {
          var result = processSSEBlock(blocks[i]);
          if (result && result.sessionDir) sessionDir = result.sessionDir;
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
      // A deliberate interrupt (user sent a reply mid-stream) aborts the fetch — not an error.
      if (err && err.name === 'AbortError') return;
      appendLog('[' + tr('Error') + '] ' + String(err));
      _running = false;
      setButtonsDisabled(false);
      if (mode === 'interactive') showAgenticChat(true);   // let the user retry
    });
  }

  /**
   * Parse one SSE block (lines separated by \n) and handle it.
   * Returns { dxnn: bool, conversationId: string|null }.
   */
  function processSSEBlock(block) {
    var ret = { sessionDir: null, conversationId: null };
    var lines = block.split('\n');
    var dataStr = '';

    // The dx_agent_dev runner sends data-only SSE frames (no `event:` line); the real
    // event kind lives in the JSON `type` field — exactly what its own console.js keys off.
    // (The old code switched on the never-present SSE event name, so every frame fell into
    // one branch and printed as a raw `[agent] …` blob.) Mirror console.js: dispatch on
    // data.type.
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      if (line.startsWith('data:')) {
        dataStr += line.slice(5).trim();
      }
    }

    if (!dataStr) return ret;

    var data;
    try {
      data = JSON.parse(dataStr);
    } catch (e) {
      data = { text: dataStr };
    }

    // Track conversation_id from any event (the done frame carries it).
    if (data && data.conversation_id) {
      ret.conversationId = data.conversation_id;
    }

    // Hidden/heartbeat frames carry no user-facing content — drop them silently.
    if (!data || data.hidden || data.type === 'ping') return ret;

    var type = data.type || 'message';
    switch (type) {
      case 'session':
        // system:init — "Session started (model)"
        if (data.status_text) appendLog('[agent] ' + data.status_text);
        break;

      case 'status':
        if (data.text || data.message) appendLog('· ' + (data.text || data.message));
        break;

      case 'message':
        if (data.text) appendLog(data.text);
        break;

      case 'command':
        // Compact tool/shell activity (→ Read: SKILL.md, ✓ Bash: …) formatted server-side.
        if (data.text) appendLog(data.text);
        break;

      case 'log':
        if (data.lines && data.lines.length) {
          appendLog(data.lines.join('\n'));
        } else if (data.text) {
          appendLog(data.text);
        }
        break;

      case 'error':
        appendLog('[' + tr('Error') + '] ' + (data.text || data.error || data.message || ''));
        break;

      case 'done':
        var doneDir = data.session_dir || (data.data && data.data.session_dir);
        if (doneDir) {
          // Defer the actual .dxnn check to stream end — session_dir always exists even
          // when the agent only asked a question, so presence != a produced .dxnn.
          ret.sessionDir = doneDir;
        }
        break;

      default:
        if (data.text) appendLog(data.text);
    }

    return ret;
  }

  /**
   * The agent's turn ended. In interactive mode, re-enable the persistent chat input so the
   * user can type the next reply into the SAME conversation.
   */
  function onStreamEnd(sessionDir, mode, originalPayload) {
    _running = false;
    setButtonsDisabled(false);
    // Best-effort: if the agent produced a .dxnn, surface it in the viewer. Fire-and-forget.
    if (sessionDir) loadDxnnFromSession(sessionDir);
    // claude -p is one-shot per turn, so the stream ending == "the agent's turn is over" — it
    // asked a question or finished a step. Re-enable the always-present chat box so the user
    // can answer / give the next instruction. conversationId (captured from the done frame) is
    // threaded into the next send for continuity.
    if (mode === 'interactive') {
      appendLog('[' + tr('Agentic Auto Compile') + '] ' +
                tr('Agent is waiting for your reply.'));
      showAgenticChat(true);   // focus the (already-typeable) box for the reply
    }
  }

  function handleStreamError(err) {
    // A deliberate interrupt (user sent a reply mid-stream) aborts the reader — not an error.
    if (err && err.name === 'AbortError') return;
    appendLog('[' + tr('Error') + '] ' + tr('Stream error: ') + String(err));
    _running = false;
    setButtonsDisabled(false);
    // Keep the chat input focused/typeable if an interactive session is active (retry).
    var row = getChatRow();
    if (row && row.style.display !== 'none') showAgenticChat(true);
  }

  // Returns a Promise<boolean> — true iff a real .dxnn artifact exists in the session dir.
  // onStreamEnd relies on this to distinguish "agent produced output" from "agent asked a
  // question": interactive runs with no .dxnn ⇒ show the reply box.
  function loadDxnnFromSession(sessionDir) {
    return fetch('/agentic/session-dxnn?dir=' + encodeURIComponent(sessionDir))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.ok && data.dxnn_path) {
          appendLog('[viewer] ' + tr('Loading DXNN:') + ' ' + data.dxnn_path);
          if (window.ViewerPanel && typeof ViewerPanel.loadModel === 'function') {
            ViewerPanel.loadModel('dxnn', data.dxnn_path);
          }
          return true;
        }
        appendLog('[viewer] ' + tr('No .dxnn found in session dir yet.'));
        return false;
      })
      .catch(function (err) {
        appendLog('[viewer] ' + tr('Could not load DXNN:') + ' ' + String(err));
        return false;
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

    var payload = {
      prompt: buildPrompt(model),
      agent: agent,
      model: selectedModel(),
      effort: selectedEffort(),
      target: 'dx-compiler',
      mode: mode,       // "autopilot" or "interactive"
    };
    // Remember agent/model/effort/target so chat follow-ups reuse them.
    _lastAgenticPayload = payload;

    if (mode === 'interactive') {
      showAgenticChat();
    } else {
      hideAgenticChat();   // autopilot = no interaction, no chat box
    }

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

    // Persistent chat input under the Compiler Log: Enter or Send → next interactive turn.
    var chatSend = document.getElementById('agentic-chat-send');
    var chatInput = getChatInput();
    if (chatSend) chatSend.addEventListener('click', sendChatReply);
    if (chatInput) {
      chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); sendChatReply(); }
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
