/* ============================================================
   DX AI Studio — 탭 행 오버플로

   라벨을 자르지 않는다. 넘치는 탭을 뒤에서부터 +N 드롭다운으로 옮긴다.
   오버플로는 창 폭이 아니라 번역 길이의 함수다 —
   Benchmark(9자)가 es에서 Evaluación de rendimiento(25자)가 된다.
   그래서 폭 변화(ResizeObserver)와 언어 변화(dx-lang-applied) 양쪽을 듣는다.
   활성 탭은 언제나 행에 남는다.
   ============================================================ */
(function () {
  'use strict';

  var _instances = [];

  function _measure(el) {
    // hidden이면 offsetWidth가 0이므로, 재는 동안만 잠시 되돌린다.
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

    // 1) 전부 행으로 되돌리고 자연 폭을 잰다.
    for (i = 0; i < tabs.length; i++) {
      if (tabs[i].parentNode !== row) row.insertBefore(tabs[i], inst.moreBtn);
      tabs[i].hidden = false;
    }
    inst.moreBtn.hidden = true;

    var style = window.getComputedStyle(row);
    var avail = row.clientWidth
      - parseFloat(style.paddingLeft || 0)
      - parseFloat(style.paddingRight || 0);
    if (!avail) return;   // 아직 레이아웃 전

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

    // 2) 넘친다 — +N 버튼 자리를 확보하고 뒤에서부터 밀어낸다.
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

    /* i18n이 DOM 텍스트를 다시 쓴 뒤 한 프레임 기다렸다가 재계산한다. */
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
