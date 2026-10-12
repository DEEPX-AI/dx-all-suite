/* ─── DX AI Studio — Setup step list (shared) ──────────────────────────────

   The app and stream Setup pages and the compiler's Setup panel share this component.
   - Top: "N of M ready" · a bar with one segment per step · one button that does the remaining work.
   - List: a vertical sequence of numbered circles joined by a line. Finished steps collapse to one line;
     only the first unfinished step ("next") expands — the blue button lives only there. Clicking a
     collapsed row opens its details.
   - State (data-state): done · todo · running · failed · blocked. Shown by shape + colour + words (never
     colour alone).
   - compact (compiler): when everything is done the whole card collapses to one line ("Setup ready").

   Module JS only reports state — DXSteps.set(root, id, state, { facts, detail }). Everything else (next step,
   bar, button text, collapsing) is computed here.

     <section class="dx-steps" data-steps>
       <header class="dx-steps-head">…<b data-steps-count></b>…<div class="dx-steps-bar"></div>
         <button data-steps-run>Set up the rest</button></header>
       <ol class="dx-steps-list">
         <li class="dx-step" data-step="deps" data-state="todo">
           <span class="dx-step-dot"></span>
           <div class="dx-step-body">
             <div class="dx-step-row"><h3 class="dx-step-title">…</h3><span class="dx-step-facts"></span>
               <span class="dx-step-state"></span></div>
             <div class="dx-step-more">description · command · buttons · log (only when expanded)</div>
           </div>
         </li>
       </ol>
     </section>

   Contract: tests/shared/test_setup_steps.py, test_setup_steps_browser.py */
(function () {
  'use strict';

  var STATES = ['done', 'todo', 'running', 'failed', 'blocked'];

  /* This component's own text (as in hw_widget — not copied into every module dictionary). */
  var DICT = {
    'Ready': { ko: '준비됨', ja: '準備完了', 'zh-CN': '就绪', 'zh-TW': '就緒', es: 'Listo' },
    'Needs setup': { ko: '설치 필요', ja: 'セットアップが必要', 'zh-CN': '需要安装', 'zh-TW': '需要安裝', es: 'Requiere instalación' },
    'Running': { ko: '진행 중', ja: '実行中', 'zh-CN': '进行中', 'zh-TW': '進行中', es: 'En curso' },
    'Failed': { ko: '실패', ja: '失敗', 'zh-CN': '失败', 'zh-TW': '失敗', es: 'Falló' },
    'After step {n}': { ko: '{n}단계 다음', ja: 'ステップ {n} の後', 'zh-CN': '第 {n} 步之后', 'zh-TW': '第 {n} 步之後', es: 'Tras el paso {n}' },
    '{n} of {m} ready': { ko: '{m}개 중 {n}개 준비됨', ja: '{m} 件中 {n} 件準備完了', 'zh-CN': '{m} 项中 {n} 项就绪', 'zh-TW': '{m} 項中 {n} 項就緒', es: '{n} de {m} listos' },
    'Set up the rest ({n})': { ko: '나머지 설치 ({n})', ja: '残りをセットアップ ({n})', 'zh-CN': '安装其余项 ({n})', 'zh-TW': '安裝其餘項目 ({n})', es: 'Instalar el resto ({n})' },
    'All set': { ko: '모두 준비됨', ja: 'すべて準備完了', 'zh-CN': '全部就绪', 'zh-TW': '全部就緒', es: 'Todo listo' },
    'Setup ready': { ko: '설치 완료', ja: 'セットアップ完了', 'zh-CN': '安装完成', 'zh-TW': '安裝完成', es: 'Instalación lista' },
    'Show details': { ko: '자세히 보기', ja: '詳細を表示', 'zh-CN': '显示详情', 'zh-TW': '顯示詳情', es: 'Ver detalles' }
  };
  if (window.DXI18n && window.DXI18n.register) window.DXI18n.register(DICT);

  function _t(key, vars) {
    var s = (window.DXI18n && window.DXI18n.T) ? window.DXI18n.T(key) : key;
    if (vars) Object.keys(vars).forEach(function (k) { s = s.split('{' + k + '}').join(vars[k]); });
    return s;
  }
  function _ico(name) {
    return (typeof window.DXIcon === 'function') ? window.DXIcon(name) : '';
  }

  var STATE_ICON = { done: 'check', todo: 'alert', running: 'spinner', failed: 'x', blocked: 'circle' };
  var STATE_LABEL = { done: 'Ready', todo: 'Needs setup', running: 'Running', failed: 'Failed' };

  function _steps(root) { return Array.prototype.slice.call(root.querySelectorAll('.dx-step[data-step]')); }

  function _paintStep(li, index, blockedBy) {
    var state = li.dataset.state;
    var dot = li.querySelector('.dx-step-dot');
    if (dot) dot.innerHTML = (state === 'done' || state === 'failed' || state === 'running') ? _ico(STATE_ICON[state]) : String(index + 1);
    var badge = li.querySelector('.dx-step-state');
    if (badge) {
      var label = state === 'blocked' ? _t('After step {n}', { n: blockedBy }) : _t(STATE_LABEL[state]);
      badge.className = 'dx-step-state is-' + state;
      badge.innerHTML = _ico(STATE_ICON[state]) + '<span>' + label + '</span>';
    }
  }

  /* Recompute everything from state — whoever called set, the screen follows one rule. */
  function refresh(root) {
    if (!root) return;
    var steps = _steps(root);
    var ready = 0, next = null, lastDone = 0;
    steps.forEach(function (li, i) {
      if (li.dataset.state === 'done') { ready += 1; lastDone = i + 1; }
      else if (!next && li.dataset.state !== 'blocked') next = li;
    });
    steps.forEach(function (li, i) {
      _paintStep(li, i, lastDone + 1);
      li.classList.toggle('is-next', li === next);
      /* Expanded: the next step, running, failed, or a row the user opened. */
      var open = li === next || li.dataset.state === 'running' || li.dataset.state === 'failed' || li.dataset.pinned === '1';
      li.classList.toggle('is-open', open);
      var row = li.querySelector('.dx-step-row');
      if (row) row.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    var count = root.querySelector('[data-steps-count]');
    if (count) count.textContent = _t('{n} of {m} ready', { n: ready, m: steps.length });
    var bar = root.querySelector('.dx-steps-bar');
    if (bar) {
      if (bar.children.length !== steps.length) {
        bar.innerHTML = '';
        steps.forEach(function () { bar.appendChild(document.createElement('i')); });
      }
      steps.forEach(function (li, i) {
        bar.children[i].className = li.dataset.state === 'done' ? 'is-done' : li === next ? 'is-next' : li.dataset.state === 'failed' ? 'is-failed' : '';
      });
    }
    var run = root.querySelector('[data-steps-run]');
    var left = steps.length - ready;
    if (run) {
      run.hidden = left === 0;
      /* Two ways to label: a sentence this component writes ([data-steps-run-label]), or a label from the
         module dictionary plus just the count ([data-steps-left] — the module's data-i18n translates the label). */
      var label = run.querySelector('[data-steps-run-label]');
      if (label) label.textContent = _t('Set up the rest ({n})', { n: left });
      var leftEl = run.querySelector('[data-steps-left]');
      if (leftEl) leftEl.textContent = '(' + left + ')';
    }
    root.classList.toggle('is-complete', left === 0);
    root.dataset.ready = String(ready);
    root.dispatchEvent(new CustomEvent('dx-steps-change', { detail: { ready: ready, total: steps.length } }));
  }

  /* Report one step's state. facts: short facts kept on the collapsed line (version · component). */
  function set(root, id, state, opts) {
    if (!root || STATES.indexOf(state) === -1) return;
    var li = root.querySelector('.dx-step[data-step="' + id + '"]');
    if (!li) return;
    li.dataset.state = state;
    opts = opts || {};
    if (opts.facts) {
      var facts = li.querySelector('.dx-step-facts');
      if (facts) {
        facts.innerHTML = '';
        opts.facts.filter(Boolean).forEach(function (f) {
          var s = document.createElement('span');
          s.textContent = f;
          facts.appendChild(s);
        });
      }
    }
    if (opts.detail !== undefined) {
      var detail = li.querySelector('.dx-step-detail');
      if (detail) detail.textContent = opts.detail;
    }
    refresh(root);
  }

  /* Open a collapsed step (before the tutorial points at a button inside it). Only the user closes it, by clicking the row. */
  function open(root, id) {
    var li = root && root.querySelector('.dx-step[data-step="' + id + '"]');
    if (!li) return;
    li.dataset.pinned = '1';
    refresh(root);
  }

  function mount(root) {
    if (!root || root.dataset.stepsMounted === '1') return;
    root.dataset.stepsMounted = '1';
    root.addEventListener('click', function (e) {
      /* Clicking a collapsed row opens its details (clicks on buttons and links excepted). */
      if (e.target.closest('button, a, input, select, textarea, label')) return;
      var row = e.target.closest('.dx-step-row');
      if (!row) return;
      var li = row.closest('.dx-step');
      if (!li || li.classList.contains('is-next')) return;
      li.dataset.pinned = li.dataset.pinned === '1' ? '0' : '1';
      refresh(root);
    });
    root.addEventListener('keydown', function (e) {
      if ((e.key === 'Enter' || e.key === ' ') && e.target.classList && e.target.classList.contains('dx-step-row')) {
        e.preventDefault();
        e.target.click();
      }
    });
    _steps(root).forEach(function (li) {
      var row = li.querySelector('.dx-step-row');
      if (row) { row.setAttribute('tabindex', '0'); row.setAttribute('role', 'button'); }
    });
    var summary = root.querySelector('[data-steps-summary]');
    if (summary) {
      summary.addEventListener('click', function () { root.classList.toggle('is-expanded'); });
    }
    if (window.DXI18n && window.DXI18n.onLangChange) window.DXI18n.onLangChange(function () { refresh(root); });
    refresh(root);
  }

  function mountAll() {
    Array.prototype.forEach.call(document.querySelectorAll('.dx-steps[data-steps]'), mount);
  }

  window.DXSteps = { mount: mount, mountAll: mountAll, set: set, open: open, refresh: refresh, STATES: STATES };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mountAll);
  else mountAll();
})();
