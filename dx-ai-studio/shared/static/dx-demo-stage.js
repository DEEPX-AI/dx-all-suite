/* ─── DX AI Studio — demo 화면 공통 무대 · card · filter ─────────────────────
   spec: docs/superpowers/specs/2026-10-01-demo-stage-design.md

   App Run Demo 와 Stream Demo Launcher 가 같은 모양을 쓴다 (사용자 결정 2026-10-01):
     · page 위쪽 **결과 무대** — 왼쪽 media (16:9), 오른쪽 panel (제목 · 옵션 · Run · 수치)
     · 그 아래 **filter** 와 **고르기용 card** — card 를 누르면 무대에 그 demo 가 열린다
     · 처음에는 첫 준비된 demo 를 연다. 준비된 것이 없으면 무대가 Setup 으로 가는 길을 말한다
     · 준비 안 된 card 는 짧은 이유 한 줄 + Set up (파일 이름은 title)
   예전에는 App 은 결과를 폭 321px card 안에, Stream 은 grid 아래 (화면 밖) 에 그렸다.

   이 파일은 모양과 상태만 갖는다. 옵션 · 실행 · 결과는 module 이 채운다:

     var ctl = DXDemoStage.mount(root, {
       items: [{id, title, category, task: {icon, label}, thumb, ready, reason, reasonTitle, sub}],
       filters: [{key, label}],           // 선택. key 'all' 은 전부
       labels: {setup, none, ready, running, unready},
       onSelect: function (item, stage) { stage.opts.innerHTML = …; stage.actions.innerHTML = …; },
       onSetup: function (item) { … },    // item 은 준비된 것이 없을 때 null
       onRender: function (el) { … },     // 선택. 새로 그린 조각마다 (번역 속성을 붙이는 자리)
     });
     ctl.stage.setMedia(nodeOrHtml) · setMetrics([{value, label, accent, id}]) · setBars([{label, ms}])
     ctl.stage.setState(kind, label)      // kind: ready · running · done · failed · unready
     ctl.setRunning(id | null) · ctl.select(id) · ctl.current() · ctl.relabel({labels, items})   // 언어 전환

   계약: tests/shared/test_demo_stage_browser.py */
(function () {
  'use strict';

  function _esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function _ico(name, cls) {
    return (name && typeof window.DXIcon === 'function') ? window.DXIcon(name, { cls: 'dds-ico' + (cls ? ' ' + cls : '') }) : '';
  }
  function _task(t) {
    if (!t || !t.label) return '';
    return '<span class="dds-task">' + _ico(t.icon) + '<span>' + _esc(t.label) + '</span></span>';
  }
  function _thumb(src) {
    return src ? '<img src="' + _esc(src) + '" alt="" loading="lazy" onerror="this.remove()">' : '';
  }

  /* 단계 막대의 색 — 앞에서부터 같은 순서 (Read · Pre · Infer · Post). tokens 에서만. */
  var BAR_COLORS = ['var(--accent)', 'var(--status-info)', 'var(--status-warn)', 'var(--status-error)', 'var(--status-ok)'];

  function mount(root, opts) {
    opts = opts || {};
    var L = opts.labels || {};
    var items = (opts.items || []).slice();
    var selected = null;
    var running = null;
    var filterKey = 'all';

    root.classList.add('dds');
    root.innerHTML =
      '<section class="dds-stage" aria-live="polite">' +
        '<div class="dds-media"></div>' +
        '<aside class="dds-side">' +
          '<div class="dds-head"></div>' +
          '<div class="dds-opts"></div>' +
          '<div class="dds-actions"></div>' +
          '<div class="dds-metrics"></div>' +
          '<div class="dds-bars"></div>' +
          '<div class="dds-extra"></div>' +
        '</aside>' +
      '</section>' +
      (opts.filters && opts.filters.length ? '<div class="dds-filter" role="toolbar"></div>' : '') +
      '<div class="dds-grid"></div>';

    var el = {
      stage: root.querySelector('.dds-stage'),
      media: root.querySelector('.dds-media'),
      side: root.querySelector('.dds-side'),
      head: root.querySelector('.dds-head'),
      opts: root.querySelector('.dds-opts'),
      actions: root.querySelector('.dds-actions'),
      metrics: root.querySelector('.dds-metrics'),
      bars: root.querySelector('.dds-bars'),
      extra: root.querySelector('.dds-extra'),
      filter: root.querySelector('.dds-filter'),
      grid: root.querySelector('.dds-grid'),
    };

    var stage = {
      root: el.stage, media: el.media, side: el.side, opts: el.opts, actions: el.actions,
      metrics: el.metrics, bars: el.bars, extra: el.extra,
      setMedia: function (content) {
        el.media.innerHTML = '';
        if (content == null) return;
        if (typeof content === 'string') el.media.innerHTML = content;
        else el.media.appendChild(content);
      },
      setMetrics: function (list) {
        el.metrics.innerHTML = (list || []).map(function (m) {
          return '<div class="dds-metric' + (m.accent ? ' is-accent' : '') + '"><b' + (m.id ? ' id="' + _esc(m.id) + '"' : '') + '>' + _esc(m.value) +
            '</b><span>' + _esc(m.label) + '</span></div>';
        }).join('');
      },
      setBars: function (parts) {
        parts = (parts || []).filter(function (p) { return p && p.ms != null; });
        var total = parts.reduce(function (s, p) { return s + Math.max(0, +p.ms || 0); }, 0);
        if (!parts.length || !total) { el.bars.innerHTML = ''; return; }
        el.bars.innerHTML = '<div class="dds-bar">' + parts.map(function (p, i) {
          return '<i style="flex:' + Math.max(0.5, +p.ms || 0) + ';background:' + (p.color || BAR_COLORS[i % BAR_COLORS.length]) + '"></i>';
        }).join('') + '</div><div class="dds-legend">' + parts.map(function (p, i) {
          return '<span style="--c:' + (p.color || BAR_COLORS[i % BAR_COLORS.length]) + '">' + _esc(p.label) + ' ' +
            _esc(Math.round((+p.ms || 0) * 10) / 10) + ' ms</span>';
        }).join('') + '</div>';
      },
      setState: function (kind, label) {
        var s = el.head.querySelector('.dds-state');
        if (!s) return;
        s.dataset.kind = kind || '';
        s.innerHTML = (kind === 'running' ? _ico('spinner', 'dx-ico--spin') : '') + '<span>' + _esc(label || '') + '</span>';
      },
      clear: function () {
        el.opts.innerHTML = ''; el.actions.innerHTML = ''; el.metrics.innerHTML = '';
        el.bars.innerHTML = ''; el.extra.innerHTML = '';
      },
    };

    function _card(it) {
      var cls = 'dds-card' + (it.ready ? '' : ' is-unready') + (it.id === selected ? ' is-selected' : '') +
        (it.id === running ? ' is-running' : '');
      var state = it.ready
        ? (it.id === running ? '<span class="dds-cstate is-running">' + _esc(L.running || 'Running') + '</span>' : '')
        : '<span class="dds-cstate is-todo">' + _ico('alert') + '<span>' + _esc(L.unready || 'Needs setup') + '</span></span>';
      /* 셋째 줄은 모든 card 가 한 줄 — 준비된 card 는 model 파일, 안 된 card 는 이유 + Set up. 줄 수가 같아야
         grid 가 같은 높이로 맞출 때 준비된 card 가 빈 자리로 늘어나지 않는다. */
      var foot = '<span class="dds-cfoot">' + (it.ready
        ? '<span class="dds-cmeta" title="' + _esc(it.sub || '') + '">' + _esc(it.sub || '') + '</span>'
        : '<span class="dds-reason" title="' + _esc(it.reasonTitle || it.reason || '') + '">' + _esc(it.reason || '') + '</span>' +
          '<button type="button" class="dds-setup">' + _esc(L.setup || 'Set up') + _ico('chev') + '</button>') + '</span>';
      /* card 는 마우스로는 어디를 눌러도 고른다 (grid 의 click). 키보드 · screen reader 에서 고르는 것은 보이지 않는
         .dds-cpick 버튼이다 — card 자체가 role=button 이면 안의 Set up 이 버튼 속 버튼이 됐다 (axe 2026-10-11). */
      return '<div class="' + cls + '" data-id="' + _esc(it.id) + '" data-category="' + _esc(it.category || '') + '">' +
        '<button type="button" class="dds-cpick" aria-pressed="' + (it.id === selected) + '">' + _esc(it.title) + '</button>' +
        (it.thumb ? '<span class="dds-thumb">' + _thumb(it.thumb) + '</span>'
          : '<span class="dds-thumb is-blank">' + _ico(it.task && it.task.icon) + '</span>') +
        '<span class="dds-cbody">' +
          '<span class="dds-crow">' + _task(it.task) + state + '</span>' +
          '<span class="dds-ctitle" title="' + _esc(it.title) + '">' + _esc(it.title) + '</span>' + foot +
        '</span></div>';
    }

    function _applyFilter() {
      Array.prototype.forEach.call(el.grid.children, function (c) {
        c.hidden = !(filterKey === 'all' || c.dataset.category === filterKey);
      });
      if (el.filter) {
        Array.prototype.forEach.call(el.filter.children, function (b) {
          b.classList.toggle('is-on', b.dataset.key === filterKey);
          b.setAttribute('aria-pressed', String(b.dataset.key === filterKey));
        });
      }
    }

    function _renderGrid() {
      el.grid.innerHTML = items.map(_card).join('');
      _applyFilter();
      if (opts.onRender) opts.onRender(el.grid);
    }

    function _find(id) {
      for (var i = 0; i < items.length; i++) if (String(items[i].id) === String(id)) return items[i];
      return null;
    }

    function _openNone() {
      selected = null;
      stage.clear();
      el.media.innerHTML = '';
      el.stage.classList.add('is-empty');
      el.head.innerHTML = '<div class="dds-none"><p>' + _esc(L.none || '') + '</p>' +
        '<button type="button" class="dds-setup">' + _esc(L.setup || 'Set up') + _ico('chev') + '</button></div>';
      el.head.querySelector('button').addEventListener('click', function () {
        if (opts.onSetup) opts.onSetup(null);
      });
      if (opts.onRender) opts.onRender(el.head);
    }

    function select(id) {
      var it = _find(id);
      if (!it) return;
      selected = it.id;
      el.stage.classList.remove('is-empty');
      el.stage.classList.toggle('is-unready', !it.ready);
      stage.clear();
      el.media.innerHTML = it.thumb ? '<img class="dds-preview" src="' + _esc(it.thumb) + '" alt="">'
        : '<div class="dds-blank">' + _ico(it.task && it.task.icon) + '</div>';
      el.head.innerHTML = _task(it.task) + '<h2 class="dds-title">' + _esc(it.title) + '</h2>' +
        '<div class="dds-sub">' + (it.sub ? '<span class="dds-model" title="' + _esc(it.sub) + '">' + _esc(it.sub) + '</span>' : '') +
        '<span class="dds-state"></span></div>';
      if (it.ready) {
        var on = it.id === running;
        stage.setState(on ? 'running' : 'ready', on ? (L.running || 'Running') : (L.ready || 'Ready'));
      } else {
        stage.setState('unready', L.unready || 'Needs setup');
        el.opts.innerHTML = '<p class="dds-why" title="' + _esc(it.reasonTitle || '') + '">' + _esc(it.reason || '') + '</p>';
        el.actions.innerHTML = '<button type="button" class="dds-setup">' + _esc(L.setup || 'Set up') + _ico('chev') + '</button>';
        el.actions.querySelector('button').addEventListener('click', function () { if (opts.onSetup) opts.onSetup(it); });
      }
      Array.prototype.forEach.call(el.grid.children, function (c) {
        var sel = String(c.dataset.id) === String(it.id);
        c.classList.toggle('is-selected', sel);
        var pick = c.querySelector('.dds-cpick');
        if (pick) pick.setAttribute('aria-pressed', String(sel));
      });
      if (opts.onRender) opts.onRender(el.head);
      if (it.ready && opts.onSelect) opts.onSelect(it, stage);
    }

    /* 그 자리에서 바꾼다 — card 를 다시 그리면 module 이 붙인 번역 (data-i18n) 이 사라진다 */
    function setRunning(id) {
      var it = id == null ? null : _find(id);
      running = it ? it.id : null;
      Array.prototype.forEach.call(el.grid.children, function (c) {
        var on = running != null && String(c.dataset.id) === String(running);
        c.classList.toggle('is-running', on);
        var row = c.querySelector('.dds-crow');
        var old = row && row.querySelector('.dds-cstate.is-running');
        if (old && !on) old.remove();
        if (row && on && !old) row.insertAdjacentHTML('beforeend',
          '<span class="dds-cstate is-running">' + _esc(L.running || 'Running') + '</span>');
      });
    }

    /* 언어가 바뀌면 글자만 그 자리에서 — card 를 다시 그리면 고른 설정 · 결과 · 번역 속성이 사라진다.
       next: {labels, items} (items 는 같은 id 의 새 글자). 열린 준비된 demo 의 panel 은 module 이 다시 채운다. */
    function relabel(next) {
      next = next || {};
      if (next.labels) L = next.labels;
      (next.items || []).forEach(function (n) {
        var it = _find(n.id);
        if (it) { it.reason = n.reason; it.reasonTitle = n.reasonTitle; }
      });
      Array.prototype.forEach.call(el.grid.children, function (c) {
        var it = _find(c.dataset.id);
        if (!it) return;
        var r = c.querySelector('.dds-reason');
        if (r) { r.textContent = it.reason || ''; r.title = it.reasonTitle || it.reason || ''; }
        var todo = c.querySelector('.dds-cstate.is-todo > span');
        if (todo) todo.textContent = L.unready || 'Needs setup';
        var run = c.querySelector('.dds-cstate.is-running');
        if (run) run.textContent = L.running || 'Running';
        var b = c.querySelector('.dds-setup');
        if (b) b.innerHTML = _esc(L.setup || 'Set up') + _ico('chev');
      });
      var cur = _find(selected);
      if (!cur) { if (selected == null) _openNone(); }
      else if (!cur.ready) select(cur.id);       // 준비 안 된 demo 는 무대에 결과가 없다
    }

    if (el.filter) {
      el.filter.innerHTML = opts.filters.map(function (f) {
        return '<button type="button" class="dds-fbtn" data-key="' + _esc(f.key) + '">' + _esc(f.label) + '</button>';
      }).join('');
      el.filter.addEventListener('click', function (e) {
        var b = e.target.closest('button[data-key]');
        if (!b) return;
        filterKey = b.dataset.key;
        _applyFilter();
      });
      if (opts.onRender) opts.onRender(el.filter);
    }

    el.grid.addEventListener('click', function (e) {
      var card = e.target.closest('.dds-card');
      if (!card) return;
      if (e.target.closest('.dds-setup')) {       // Set up 은 card 를 고르지 않는다
        e.stopPropagation();
        if (opts.onSetup) opts.onSetup(_find(card.dataset.id));
        return;
      }
      select(card.dataset.id);
      /* 무대가 화면 위로 지나가 있으면 (아래 줄의 card 를 누른 경우) 무대로 올린다 */
      if (el.stage.getBoundingClientRect().top < 0) {
        try { el.stage.scrollIntoView({ block: 'start', behavior: 'smooth' }); } catch (err) {}
      }
    });

    _renderGrid();
    var first = null;
    for (var i = 0; i < items.length; i++) if (items[i].ready) { first = items[i]; break; }
    if (first) select(first.id); else _openNone();

    return {
      stage: stage,
      select: select,
      setRunning: setRunning,
      relabel: relabel,
      current: function () { return _find(selected); },
      setFilter: function (key) { filterKey = key || 'all'; _applyFilter(); },
    };
  }

  window.DXDemoStage = { mount: mount };
})();
