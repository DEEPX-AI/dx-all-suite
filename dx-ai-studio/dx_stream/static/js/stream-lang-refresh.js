/* DX Stream — language refresh registry */
(function () {
  'use strict';
  window.__streamLangRefreshers = window.__streamLangRefreshers || [];
  window.registerStreamLangRefresher = function (fn) {
    if (typeof fn === 'function') window.__streamLangRefreshers.push(fn);
  };

  // One language change used to reload the page twelve times: here, in each of the ten
  // registered refreshers and in stream-app.js — every reload re-ran the page's fetches and
  // stopped any running setup log poll. Refreshers still ask for a reload; it happens once.
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
