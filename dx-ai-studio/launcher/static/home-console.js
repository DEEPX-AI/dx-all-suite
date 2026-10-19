/* ── Home working view ────────────────────────────────────────
 *
 * Runs an agent from the front door without leaving the page.
 *
 * It adds no way to run an agent. The launcher already reverse proxies
 * dx_agent_dev at /agent/, so this calls the endpoints the module itself calls
 * — same adapters, same effort levels, same targets. If the module's API moves,
 * this follows for free. What is new is only the layout.
 *
 * The stream is already typed, and the types say where each event belongs:
 *
 *   message  → left, as prose
 *   status   → left, as a status line
 *   command  → right as the line, left as a +1 on the activity summary
 *   log      → right
 *   session  → left footer (the artefact)
 *   done     → both settle
 *   error    → left, with the raw text kept in the terminal
 *   ping     → nowhere; it is a keepalive
 */
(function () {
  'use strict';

  var ns = window.DXLauncher = window.DXLauncher || {};

  var _running = false;
  var _follow = true;
  var _started = 0;
  var _tick = null;
  var _turn = null;          // { block, summary, commands, files, other }
  var _turns = [];           // every turn, so a language change can relabel them
  var _ended = '';           // 'Completed' | 'Failed' | 'Stopped' — the badge's resting text
  var _failed = false;       // an `error` came — the closing `done` must not read as success
  var _sessionDir = '';
  /* One conversation — in Interactive mode replies continue the same conversation. Dropped on close. */
  var _conversationId = null;
  var _mode = 'interactive';
  var _setup = {};           // agent · model · effort chosen when the conversation started (replies reuse them)

  function $(id) { return document.getElementById(id); }
  function _t(key) {
    return (window.DXI18n && window.DXI18n.T) ? window.DXI18n.T(key) : key;
  }
  function _show(el, on) {
    if (!el) return;
    if (on) el.removeAttribute('hidden'); else el.setAttribute('hidden', '');
  }

  /* ── left: narration ─────────────────────────────────────── */

  function _newTurn() {
    var host = $('workNarration');
    if (!host) return null;
    var block = document.createElement('div');
    block.className = 'work-turn';
    var body = document.createElement('div');
    body.className = 'turn-text';
    var summary = document.createElement('p');
    summary.className = 'turn-activity';
    summary.hidden = true;
    block.appendChild(body);
    block.appendChild(summary);
    host.appendChild(block);
    var turn = {
      block: block, body: body, summary: summary, commands: 0, files: 0, other: 0, text: '', paint: 0
    };
    _turns.push(turn);
    return turn;
  }

  /* One turn's text is one block, merged by the same rule as Agent Dev (console.js applyAssistantText):
     final replaces, delta appends, otherwise a longer text replaces (cumulative snapshot) and a shorter
     one appends. A paragraph per message scattered the pieces and broke line breaks, lists and headings.
     Rendered with the same renderer as Agent Dev (shared/static/markdown_render.js), once per frame. */
  function _say(text, ev) {
    if (!text) return;
    if (!_turn) _turn = _newTurn();
    if (!_turn) return;
    var turn = _turn;
    if (ev && ev.final) turn.text = text;
    else if (ev && ev.delta) turn.text += text;
    else if (!turn.text || text.length >= turn.text.length) turn.text = text;
    else turn.text += text;
    if (turn.paint) return;
    turn.paint = requestAnimationFrame(function () {
      turn.paint = 0;
      _paintTurn(turn);
    });
  }

  function _paintTurn(turn) {
    var R = window.DXMarkdownRender;
    if (R && R.render) turn.body.innerHTML = R.render(R.repairCodeFences(turn.text), {});
    else turn.body.textContent = turn.text;
  }

  function _youSaid(text) {
    var host = $('workNarration');
    if (!host) return;
    var el = document.createElement('p');
    el.className = 'work-you';
    el.textContent = text;
    host.appendChild(el);
  }

  /* The adapter formats shell lines as `$ cmd` and file tools as `✓ action: path`.
     We own both ends, so counting by prefix is a contract, not a heuristic — and
     anything unrecognised falls back to a plain total rather than a wrong label. */
  function _relabel(turn) {
    var parts = [];
    if (turn.files) parts.push(turn.files + ' ' + _t('files'));
    if (turn.commands) parts.push(turn.commands + ' ' + _t('commands'));
    if (!parts.length) parts.push(turn.other + ' ' + _t('activity'));
    turn.summary.hidden = false;
    turn.summary.textContent = '⤷ ' + parts.join(' · ');
  }

  function _countActivity(text) {
    if (!_turn) _turn = _newTurn();
    if (!_turn) return;
    var line = String(text || '');
    if (line.indexOf('$ ') === 0) _turn.commands += 1;
    else if (line.indexOf('✓') === 0) _turn.files += 1;
    else _turn.other += 1;
    _relabel(_turn);
  }

  function _status(text) {
    var el = $('workStatus');
    if (el) el.textContent = text || '';
  }

  function _error(text) {
    var host = $('workNarration');
    if (!host) return;
    var el = document.createElement('p');
    el.className = 'turn-error';
    el.textContent = text;
    host.appendChild(el);
  }

  /* ── right: terminal ─────────────────────────────────────── */

  function _termLine(text, kind) {
    var out = $('workTerminalOut');
    if (!out) return;
    _show($('workTerminal'), true);
    var line = document.createElement('div');
    line.className = 'term-line' + (kind ? ' is-' + kind : '');
    line.textContent = text;
    out.appendChild(line);
    if (_follow) out.scrollTop = out.scrollHeight;
  }

  /* ── the stream ──────────────────────────────────────────── */

  function _artifactSeen() { return _sessionDir.indexOf('dx-agent-dev') >= 0; }

  function renderEvent(ev) {
    if (!ev || ev.type === 'ping' || ev.hidden) return;
    switch (ev.type) {
      case 'message':
        _say(ev.text || '', ev);
        break;
      case 'status':
        if (ev.text) _status(ev.text);
        break;
      case 'command':
        _termLine(ev.text || '', 'cmd');
        _countActivity(ev.text || '');
        break;
      case 'log':
        _termLine(ev.text || '', 'log');
        _countActivity(ev.text || '');
        break;
      case 'session':
        if (ev.session_dir) _sessionDir = ev.session_dir;
        break;
      case 'error':
        _failed = true;
        _error(ev.text || '');
        _termLine(ev.text || '', 'err');
        break;
      case 'artifacts':
        /* Where the agent built the app (the target project's dx-agent-dev/<session>/), rather than the Studio tracking folder from done */
        if (ev.dirs && ev.dirs.length) {
          _sessionDir = ev.dirs.join(', ');
          var pathEl = $('workSessionPath');
          if (pathEl && pathEl.textContent) pathEl.textContent = _sessionDir;
        }
        break;
      case 'done':
        if (ev.session_dir && !_artifactSeen()) _sessionDir = ev.session_dir;
        if (ev.conversation_id) _conversationId = ev.conversation_id;
        _finish(true);
        break;
      default:
        break;
    }
  }

  /* ── run ─────────────────────────────────────────────────── */

  function _elapsed() {
    var s = Math.floor((Date.now() - _started) / 1000);
    return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2);
  }

  function _setBusy(on) {
    _running = on;
    var view = $('homeWork');
    if (view) view.classList.toggle('is-running', on);
    /* Cannot be closed while running — Stop first, so the work view is not lost by accident.
       Switching the stage to the Dock is computed in CSS from whether #homeWork is visible
       (home-stage.css). */
    var close = $('workClose');
    if (close) close.hidden = on;
    var badge = $('workBadge');
    if (badge) badge.classList.toggle('is-running', on);
    if (on) {
      _started = Date.now();
      _tick = setInterval(function () {
        if (badge) badge.textContent = _t('Working') + ' · ' + _elapsed();
      }, 1000);
    } else if (_tick) {
      clearInterval(_tick);
      _tick = null;
    }
  }

  /* The last thing on the left is the thing you can execute. "Done" is not a
     result; a session folder with a Run control is. */
  function _finish(ok) {
    if (!_running && _ended) return;       // called by both done and the end of the stream
    _setBusy(false);
    if (_turn && _turn.paint) { cancelAnimationFrame(_turn.paint); _turn.paint = 0; _paintTurn(_turn); }
    _turn = null;                          // the next reply is a new turn
    _ended = !ok ? 'Stopped' : (_failed ? 'Failed' : 'Completed');
    /* In Interactive mode the agent has asked a question and stopped — open the reply box (same conversation). Not for failed runs. */
    _showReply(ok && !_failed && _mode === 'interactive' && !!_conversationId);
    var badge = $('workBadge');
    if (badge) badge.textContent = _t(_ended);
    var foot = $('workArtefact');
    if (foot && _sessionDir) {
      $('workSessionPath').textContent = _sessionDir;
      _show(foot, true);
    }
  }

  function _showReply(on) {
    var box = $('workReply');
    if (!box) return;
    _show(box, on);
    if (on) {
      var input = $('workReplyInput');
      if (input) { input.value = ''; try { input.focus({ preventScroll: true }); } catch (e) {} }
    }
  }

  /* New conversation. Settings (agent · model · effort · mode) are read once here; replies reuse them. */
  function start(prompt) {
    if (_running || !prompt) return;
    var view = $('homeWork');
    if (!view) return;
    _show($('homeAnswer'), false);
    _show(view, true);
    $('workAsk').textContent = prompt;
    $('workNarration').innerHTML = '';
    $('workTerminalOut').innerHTML = '';
    _show($('workArtefact'), false);
    _showReply(false);
    _turns = [];
    _sessionDir = '';
    _follow = true;
    _conversationId = null;
    _setup = (ns.agentChoice && ns.agentChoice()) || {};
    _mode = _setup.mode === 'autopilot' ? 'autopilot' : 'interactive';
    _run(prompt);
  }

  /* One more turn in the same conversation — after the agent asked and stopped in Interactive mode. */
  function reply(text) {
    text = String(text || '').trim();
    if (_running || !text || !_conversationId) return;
    _showReply(false);
    _youSaid(text);
    _run(text);
  }

  function _run(prompt) {
    _turn = null;
    _ended = '';
    _failed = false;
    _setBusy(true);
    fetch('/agent/api/agent/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: prompt,
        lang: (window.DXI18n && window.DXI18n.lang) || 'en',
        /* One place owns who is building and how — the setup row in Build,
           which reads it from the module. */
        agent: _setup.agent,
        model: _setup.model,
        effort: _setup.effort,
        /* Without mode the server runs interactive; home must send it so the agent's questions
           have somewhere to be answered. */
        mode: _mode,
        conversation_id: _conversationId || undefined
      })
    }).then(function (resp) {
      if (!resp.ok || !resp.body) {
        _error(_t('Could not reach DX Agent Dev') + ' (HTTP ' + resp.status + ')');
        _finish(false);
        return;
      }
      _consume(resp);
    }).catch(function () {
      _error(_t('Could not reach DX Agent Dev'));
      _finish(false);
    });
  }

  function stop() {
    fetch('/agent/api/agent/cancel', { method: 'POST' }).catch(function () {});
    _finish(false);
  }

  /* ── setup chips ─────────────────────────────────────────── */


  /* Reads the SSE body and streams it to the screen. Starting a run and attaching to a
     running one share this code, so a resumed run looks exactly like the original. */
  function _consume(resp) {
    var reader = resp.body.getReader();
    var decoder = new TextDecoder();
    var buffer = '';
    (function pump() {
      reader.read().then(function (chunk) {
        if (chunk.done) { _finish(true); return; }
        buffer += decoder.decode(chunk.value, { stream: true });
        var lines = buffer.split('\n');
        buffer = lines.pop() || '';
        lines.forEach(function (line) {
          if (line.indexOf('data: ') !== 0) return;
          var frag = line.slice(6);
          if (frag === '[DONE]') return;
          try { renderEvent(JSON.parse(frag)); } catch (e) { /* partial frame */ }
        });
        pump();
      }).catch(function () { _finish(false); });
    })();
  }

  /* On open, attach to a run that is already going. Otherwise, after leaving home and
     coming back, the work would look lost even though the server still holds the run. */
  function attachIfRunning() {
    return fetch('/agent/api/agent/status').then(function (r) { return r.json(); })
      .then(function (st) {
        if (!st || !st.run_id || st.run_done) return false;
        var view = $('homeWork');
        if (!view) return false;
        _show($('homeAnswer'), false);
        _show(view, true);
        $('workNarration').innerHTML = '';
        $('workTerminalOut').innerHTML = '';
        /* What is being resumed — status gives the running run's request · conversation · mode */
        if (st.run_prompt) $('workAsk').textContent = st.run_prompt;
        _conversationId = st.run_conversation_id || null;
        _mode = st.run_mode === 'autopilot' ? 'autopilot' : 'interactive';
        _setup = (ns.agentChoice && ns.agentChoice()) || {};
        _showReply(false);
        _turn = null; _turns = []; _ended = ''; _failed = false; _follow = true;
        _setBusy(true);
        return fetch('/agent/api/agent/run/events?from=0').then(function (resp) {
          if (!resp.ok || !resp.body) { _finish(false); return false; }
          _consume(resp);
          return true;
        });
      })
      .catch(function () { return false; });
  }

  function init() {
    var view = $('homeWork');
    if (!view) return;

    attachIfRunning();

    var out = $('workTerminalOut');
    if (out) {
      /* Auto-follow, but scrolling up pins it. A log that yanks itself to the
         bottom while you are reading is a log nobody reads. */
      out.addEventListener('scroll', function () {
        var atBottom = out.scrollHeight - out.scrollTop - out.clientHeight < 40;
        _follow = atBottom;
        var btn = $('workFollow');
        if (btn) btn.classList.toggle('is-on', _follow);
      });
    }
    var follow = $('workFollow');
    if (follow) {
      follow.addEventListener('click', function () {
        _follow = true;
        follow.classList.add('is-on');
        if (out) out.scrollTop = out.scrollHeight;
      });
    }
    var collapse = $('workCollapse');
    if (collapse) {
      collapse.addEventListener('click', function () {
        var split = $('workSplit');
        if (split) split.classList.toggle('is-collapsed');
      });
    }
    var edit = $('workSetupEdit');
    if (edit) {
      edit.addEventListener('click', function () {
        view.classList.toggle('setup-open');
      });
    }
    var stopBtn = $('workStop');
    if (stopBtn) stopBtn.addEventListener('click', stop);
    var replyBox = $('workReply');
    if (replyBox) {
      replyBox.addEventListener('submit', function (e) {
        e.preventDefault();
        reply(($('workReplyInput') || {}).value);
      });
      var replyInput = $('workReplyInput');
      if (replyInput) {
        /* Enter sends, Shift+Enter inserts a newline (never sends during IME composition) */
        replyInput.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
            e.preventDefault();
            reply(replyInput.value);
          }
        });
      }
    }
    var closeBtn = $('workClose');
    if (closeBtn) closeBtn.addEventListener('click', closeHomeWork);
    var openModule = $('workOpenModule');
    if (openModule) {
      openModule.addEventListener('click', function () {
        /* A full navigation drops the stream; the run itself is held by the server.
           Moving inside the shell switches the view instantly. */
        var path = '/agent/#ask=' + encodeURIComponent($('workAsk').textContent || '');
        if (ns.homeLeaveTo) { ns.homeLeaveTo(path); return; }
        window.location.assign(path);
      });
    }

    /* What we wrote, we relabel: the badge and each turn's activity count. The
       agent's own prose is not ours to translate — it answered in the language
       the run was started in, and rewriting it would be a claim we cannot make.
       The terminal is verbatim output and stays verbatim. */
    if (window.DXI18n && DXI18n.onLangChange) {
      DXI18n.onLangChange(function () {
        var badge = $('workBadge');
        if (badge && !_running && _ended) badge.textContent = _t(_ended);
        _turns.forEach(function (turn) {
          if (turn.commands || turn.files || turn.other) _relabel(turn);
        });
      });
    }
  }

  /* Close a finished (or stopped) work view and restore the stage. Does nothing while running. */
  function closeHomeWork() {
    if (_running) return false;
    var view = $('homeWork');
    if (!view || view.hidden) return false;
    _show(view, false);
    _conversationId = null;      // closing drops the conversation — the next start is a new one
    _showReply(false);
    return true;
  }

  ns.closeHomeWork = closeHomeWork;
  ns._homeWorkSetBusy = _setBusy;   // lets test_home_stage_browser.py put the view in the running state
  ns.homeAgentStart = start;
  ns.homeAgentReply = reply;
  ns.initHomeConsole = init;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
