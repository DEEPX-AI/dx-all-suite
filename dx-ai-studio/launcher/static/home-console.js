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
  /* 한 대화 — Interactive 면 답장이 같은 conversation 으로 이어진다. 닫으면 버린다. */
  var _conversationId = null;
  var _mode = 'interactive';
  var _setup = {};           // 대화를 시작할 때 고른 agent · model · effort (답장도 같은 것으로)

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

  /* 한 턴의 글은 한 덩어리 — Agent Dev (console.js applyAssistantText) 와 같은 규칙으로 합친다: final 은
     바꾸고, delta 는 잇고, 그 밖에는 더 길면 바꾸고 (누적 snapshot) 짧으면 잇는다. 예전에는 message 마다
     새 문단을 만들고 textContent 로 넣어서, 조각이 흩어지고 줄바꿈 · 목록 · 제목이 뭉개졌다.
     그리기는 Agent Dev 와 같은 renderer (shared/static/markdown_render.js) 로, frame 당 한 번. */
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
      case 'done':
        if (ev.session_dir) _sessionDir = ev.session_dir;
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
    /* 도는 동안에는 닫을 수 없다 — 먼저 Stop. 작업 화면을 실수로 잃지 않게.
       무대를 Dock 으로 바꾸는 것은 CSS 가 #homeWork 가 보이는지에서 계산한다
       (home-stage.css, spec 2026-09-23 §5.7b). */
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
    if (!_running && _ended) return;       // done 과 stream 끝이 둘 다 부른다
    _setBusy(false);
    if (_turn && _turn.paint) { cancelAnimationFrame(_turn.paint); _turn.paint = 0; _paintTurn(_turn); }
    _turn = null;                          // 다음 답장은 새 턴
    _ended = !ok ? 'Stopped' : (_failed ? 'Failed' : 'Completed');
    /* Interactive 면 agent 가 묻고 멈춘 자리다 — 답장 칸을 연다 (같은 대화로 이어 간다). 실패한 실행에는 열지 않는다. */
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

  /* 새 대화. 설정 (agent · model · effort · mode) 은 여기서 한 번 읽고, 답장도 같은 것으로 간다. */
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

  /* 같은 대화로 한 턴 더 — Interactive 에서 agent 가 묻고 멈춘 뒤. */
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
           which reads it from the module. This used to read three selects in
           the console header that were never populated: the loader asked
           /api/agent/models for a key (`agents`) that endpoint does not
           return, so all three posted empty. */
        agent: _setup.agent,
        model: _setup.model,
        effort: _setup.effort,
        /* mode 를 보내지 않으면 server 는 interactive 로 돌리는데, 예전 home 에는 답할 곳이 없어서
           agent 가 "진행할까요?" 하고 멈추면 거기서 끝이었다. */
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


  /* SSE 본문을 읽어 화면에 흘린다. 시작할 때와 이미 도는 실행에 붙을 때가 같은
     코드를 쓴다 — 붙는 쪽이 다르게 그리면 "이어받았다" 가 거짓말이 된다. */
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

  /* 열릴 때 이미 도는 실행이 있으면 붙는다. 이것이 없으면 서버가 실행을 들고 있어도
     사용자에게는 여전히 "작업이 사라진" 것이다 — home 을 떠났다 돌아온 경우가
     정확히 그랬다. */
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
        /* 무엇을 이어받는지 — status 가 도는 실행의 요청 · 대화 · mode 를 준다 */
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
        /* Enter 로 보내고 Shift+Enter 는 줄바꿈 (한글 조합 중에는 보내지 않는다) */
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
        /* 전체 이동이면 스트림이 끊긴다. 예전에는 그것이 곧 실행의 종료였고
           (agent_runner 의 finally 가 GeneratorExit 에서 subprocess 를 죽였다),
           그래서 이 버튼은 이름과 달리 "중단하고 이동" 이었다. 이제 실행은 서버가
           들고 있지만, 셸 안에서 움직이면 화면 전환도 즉시다. */
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

  /* 끝난 (또는 멈춘) 작업을 닫고 무대를 되돌린다. 도는 중이면 닫지 않는다. */
  function closeHomeWork() {
    if (_running) return false;
    var view = $('homeWork');
    if (!view || view.hidden) return false;
    _show(view, false);
    _conversationId = null;      // 닫으면 대화를 버린다 — 다음 시작은 새 대화
    _showReply(false);
    return true;
  }

  ns.closeHomeWork = closeHomeWork;
  ns._homeWorkSetBusy = _setBusy;   // test_home_stage_browser.py 가 도는 상태를 만든다
  ns.homeAgentStart = start;
  ns.homeAgentReply = reply;
  ns.initHomeConsole = init;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
