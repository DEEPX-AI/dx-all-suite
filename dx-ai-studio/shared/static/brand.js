(function () {
  'use strict';

  function currentLang() {
    if (typeof DXI18n !== 'undefined' && DXI18n.lang) return DXI18n.lang;
    return localStorage.getItem('dx-lang') || 'en';
  }

  function subtitleFor(subtitle) {
    if (!subtitle) return '';
    if (typeof subtitle === 'string') return subtitle;
    return subtitle[currentLang()] || subtitle.en || '';
  }

  // Rejects unsafe protocols like javascript: or data:
  function isSafeHref(href) {
    if (!href || typeof href !== 'string') return false;
    if (href.charAt(0) === '/') return true;
    if (href.indexOf('https://') === 0 || href.indexOf('http://') === 0) return true;
    return false;
  }

  function mount(opts) {
    opts = opts || {};
    var target = typeof opts.target === 'string' ? document.querySelector(opts.target) : opts.target;
    if (!target) {
      console.warn('[DXBrand] target not found:', opts.target);
      return null;
    }

    var existing = target.querySelector('.dx-brand');
    if (existing) {
      console.warn('[DXBrand] already mounted in target, returning existing element');
      return existing;
    }

    var safeHref = isSafeHref(opts.homeHref) ? opts.homeHref : null;
    if (opts.homeHref && !safeHref) {
      console.warn('[DXBrand] homeHref ignored (unsafe protocol):', opts.homeHref);
    }

    var root = document.createElement(safeHref ? 'a' : 'div');
    root.className = 'dx-brand';
    if (safeHref) {
      root.href = safeHref;
      // The brand links to the launcher home. Modules render inside the launcher's
      // iframe pool, so a default _self navigation would load the launcher shell
      // *inside* the iframe — stacking a second top bar. Force _top to break out
      // and land on the real launcher home (harmless no-op when not framed).
      root.target = '_top';
    }
    root.style.setProperty('--dx-brand-accent', opts.accent || 'var(--accent, #638cff)');
    root.innerHTML = [
      '<span class="dx-brand-prefix">DX</span>',
      '<span class="dx-brand-copy">',
      '  <span class="dx-brand-name"></span>',
      '  <small class="dx-brand-subtitle"></small>',
      '</span>',
    ].join('');

    var nameEl = root.querySelector('.dx-brand-name');
    var subtitleEl = root.querySelector('.dx-brand-subtitle');
    nameEl.textContent = opts.name || '';
    function renderSubtitle() {
      subtitleEl.textContent = subtitleFor(opts.subtitle);
    }
    renderSubtitle();
    target.appendChild(root);

    if (typeof DXI18n !== 'undefined' && typeof DXI18n.onLangChange === 'function') {
      DXI18n.onLangChange(renderSubtitle);
    }
    return root;
  }

  window.DXBrand = { mount: mount };
})();
