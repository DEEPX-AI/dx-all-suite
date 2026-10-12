/* ============================================================
   DX AI Studio — tab row overflow

   Labels are never truncated. Tabs that do not fit move, from the end, into a +N dropdown.
   Overflow depends on translation length as much as window width —
   Benchmark (9 chars) becomes Evaluación de rendimiento (25 chars) in es.
   So it listens to both width changes (ResizeObserver) and language changes (dx-lang-applied).
   The active tab always stays in the row.
   ============================================================ */
(function () {
  'use strict';

  var _instances = [];

  function _measure(el) {
    // A hidden element has offsetWidth 0, so unhide it just while measuring.
    var wasHidden = el.hidden;
    if (wasHidden) el.hidden = false;
    var w = el.offsetWidth;
    if (wasHidden) el.hidden = true;
    return w;
  }

  function _reflow(inst) {
    var row = inst.row;
    var tabs = inst.tabs;
    var i;

    // 1) Move everything back into the row and measure the natural width.
    for (i = 0; i < tabs.length; i++) {
      if (tabs[i].parentNode !== row) row.insertBefore(tabs[i], inst.moreBtn);
      tabs[i].hidden = false;
    }
    inst.moreBtn.hidden = true;

    var style = window.getComputedStyle(row);
    var avail = row.clientWidth
      - parseFloat(style.paddingLeft || 0)
      - parseFloat(style.paddingRight || 0);
    if (!avail) return;   // not laid out yet

    var widths = [];
    var total = 0;
    for (i = 0; i < tabs.length; i++) {
      widths[i] = _measure(tabs[i]) + 2;   /* gap */
      total += widths[i];
    }
    if (total <= avail) {
      inst.menu.classList.remove('open');
      return;
    }

    // 2) It overflows — reserve room for the +N button and push tabs out from the end.
    inst.moreBtn.hidden = false;
    var budget = avail - _measure(inst.moreBtn) - 8;

    var activeIdx = -1;
    for (i = 0; i < tabs.length; i++) {
      if (tabs[i].getAttribute('aria-current') === 'page') { activeIdx = i; break; }
    }

    var used = activeIdx >= 0 ? widths[activeIdx] : 0;
    var keep = {};
    if (activeIdx >= 0) keep[activeIdx] = true;
    for (i = 0; i < tabs.length; i++) {
      if (i === activeIdx) continue;
      if (used + widths[i] > budget) break;
      used += widths[i];
      keep[i] = true;
    }

    var overflowed = 0;
    for (i = 0; i < tabs.length; i++) {
      if (keep[i]) continue;
      inst.menu.appendChild(tabs[i]);
      tabs[i].hidden = false;
      overflowed++;
    }
    inst.moreLabel.textContent = '+' + overflowed;
    var moreTpl = typeof T === 'function' ? T('{n} more pages') : '{n} more pages';
    inst.moreBtn.setAttribute('aria-label', moreTpl.replace('{n}', overflowed));
  }

  function init(opts) {
    var row = document.querySelector((opts && opts.row) || '.dx-shell-tabs');
    if (!row) return null;

    var tabs = Array.prototype.slice.call(row.querySelectorAll('.dx-tab'));
    if (!tabs.length) return null;

    var moreBtn = document.createElement('button');
    moreBtn.className = 'dx-tab-overflow';
    moreBtn.type = 'button';
    moreBtn.hidden = true;
    var moreLabel = document.createElement('span');
    moreLabel.textContent = '+0';
    moreBtn.appendChild(moreLabel);
    moreBtn.insertAdjacentHTML(
      'beforeend',
      '<svg aria-hidden="true"><use href="' +
        (window.DXIcon ? window.DXIcon.url('dots') : '/static/shared/dx-icons.svg' + '#dots') + '"></use></svg>'
    );
    row.appendChild(moreBtn);

    var menu = document.createElement('div');
    menu.className = 'dx-tab-menu';
    row.appendChild(menu);

    moreBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      menu.classList.toggle('open');
    });
    document.addEventListener('click', function () { menu.classList.remove('open'); });

    var inst = {
      row: row, tabs: tabs, moreBtn: moreBtn, moreLabel: moreLabel, menu: menu
    };
    _instances.push(inst);

    if (typeof ResizeObserver !== 'undefined') {
      new ResizeObserver(function () { _reflow(inst); }).observe(row);
    } else {
      window.addEventListener('resize', function () { _reflow(inst); });
    }

    /* After i18n rewrites the DOM text, wait one frame and recompute. */
    window.addEventListener('dx-lang-applied', function () {
      window.requestAnimationFrame(function () { _reflow(inst); });
    });

    _reflow(inst);
    return inst;
  }

  function reflowAll() {
    for (var i = 0; i < _instances.length; i++) _reflow(_instances[i]);
  }

  window.DXTabs = { init: init, reflowAll: reflowAll };
})();
