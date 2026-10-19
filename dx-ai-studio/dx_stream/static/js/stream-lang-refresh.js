/* DX Stream — language refresh registry */
(function () {
  'use strict';
  window.__streamLangRefreshers = window.__streamLangRefreshers || [];
  window.registerStreamLangRefresher = function (fn) {
    if (typeof fn === 'function') window.__streamLangRefreshers.push(fn);
  };

  // Each registered refresher (and stream-app.js) asks for a reload on a language change;
  // coalesce them into one, since every reload re-runs the page's fetches and stops any
  // running setup log poll.
  function refreshStreamModuleLanguage(lang) {
    if (typeof DXI18n !== 'undefined' && typeof DXI18n.applyLang === 'function') DXI18n.applyLang(document);
    var hasStream = typeof DXStream !== 'undefined' && typeof DXStream.nav === 'function';
    var realNav = hasStream ? DXStream.nav : null;
    if (hasStream) {
      DXStream.S.lang = lang || (DXI18n && DXI18n.lang) || 'en';
      DXStream.nav = function () { /* coalesced — one reload below */ };
    }
    try {
      window.__streamLangRefreshers.forEach(function (fn) {
        try { fn(); } catch (e) { console.error('[stream-lang-refresh]', e); }
      });
    } finally {
      if (hasStream) {
        DXStream.nav = realNav;
        if (DXStream.S.currentPage) realNav(DXStream.S.currentPage);
      }
    }
  }

  if (typeof DXI18n !== 'undefined' && typeof DXI18n.onLangChange === 'function') {
    DXI18n.onLangChange(refreshStreamModuleLanguage);
  }
  window.refreshStreamLanguage = refreshStreamModuleLanguage;
})();
