/* ─── DX AI Studio — shared demo stage · cards · filter ─────────────────────

   App Run Demo and Stream Demo Launcher share one layout:
     · at the top, the **result stage** — media on the left (16:9), panel on the right (title · options · Run · metrics)
     · below it, the **filter** and **cards to pick from** — clicking a card opens that demo on the stage
     · at first the first ready demo opens. With none ready, the stage points the way to Setup
     · a card that is not ready shows a one-line reason + Set up (file name in the title)

   This file owns layout and state only. Options, running and results are filled in by the module:

     var ctl = DXDemoStage.mount(root, {
       items: [{id, title, category, task: {icon, label}, thumb, ready, reason, reasonTitle, sub}],
       filters: [{key, label}],           // optional. key 'all' means everything
       labels: {setup, none, ready, running, unready},
       onSelect: function (item, stage) { stage.opts.innerHTML = …; stage.actions.innerHTML = …; },
       onSetup: function (item) { … },    // item is null when nothing is ready
       onRender: function (el) { … },     // optional. Called per freshly drawn fragment (to attach i18n attributes)
     });
     ctl.stage.setMedia(nodeOrHtml) · setMetrics([{value, label, accent, id}]) · setBars([{label, ms}])
     ctl.stage.setState(kind, label)      // kind: ready · running · done · failed · unready
     ctl.setRunning(id | null) · ctl.select(id) · ctl.current() · ctl.relabel({labels, items})   // language switch

   Contract: tests/shared/test_demo_stage_browser.py */
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

  /* Stage bar colours, in bar order (Read · Pre · Infer · Post). Tokens only. */
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
      /* Every card has exactly one third line — the model file when ready, otherwise reason + Set up. Equal line
         counts keep ready cards from stretching with empty space when the grid equalises heights. */
      var foot = '<span class="dds-cfoot">' + (it.ready
        ? '<span class="dds-cmeta" title="' + _esc(it.sub || '') + '">' + _esc(it.sub || '') + '</span>'
        : '<span class="dds-reason" title="' + _esc(it.reasonTitle || it.reason || '') + '">' + _esc(it.reason || '') + '</span>' +
          '<button type="button" class="dds-setup">' + _esc(L.setup || 'Set up') + _ico('chev') + '</button>') + '</span>';
      /* With a mouse, a click anywhere on the card picks it (grid click). Keyboard and screen readers pick via the
         hidden .dds-cpick button — a role=button card would nest the Set up button inside a button. */
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

    /* Update in place — redrawing the cards would drop the translations (data-i18n) the module attached */
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

    /* On a language change, update only the text in place — redrawing the cards would drop the chosen options,
       results and i18n attributes. next: {labels, items} (items: new text for the same ids). The module refills
       the panel of an open ready demo. */
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
      else if (!cur.ready) select(cur.id);       // a demo that is not ready has no result on the stage
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
      if (e.target.closest('.dds-setup')) {       // Set up does not pick the card
        e.stopPropagation();
        if (opts.onSetup) opts.onSetup(_find(card.dataset.id));
        return;
      }
      select(card.dataset.id);
      /* If the stage has scrolled off the top (a card in a lower row was clicked), scroll back to it */
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
