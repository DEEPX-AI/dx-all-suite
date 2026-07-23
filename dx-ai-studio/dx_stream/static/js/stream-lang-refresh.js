/* DX Stream — language refresh registry */
(function () {
  'use strict';
  window.__streamLangRefreshers = window.__streamLangRefreshers || [];
  window.registerStreamLangRefresher = function (fn) {
    if (typeof fn === 'function') window.__streamLangRefreshers.push(fn);
  };

  function refreshStreamModuleLanguage(lang) {
    if (typeof DXI18n !== 'undefined' && typeof DXI18n.applyLang === 'function') DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined') {
      DXStream.S.lang = lang || (DXI18n && DXI18n.lang) || 'en';
      if (DXStream.S.currentPage && typeof DXStream.nav === 'function') DXStream.nav(DXStream.S.currentPage);
    }
    window.__streamLangRefreshers.forEach(function (fn) {
      try { fn(); } catch (e) { console.error('[stream-lang-refresh]', e); }
    });
  }

  if (typeof DXI18n !== 'undefined' && typeof DXI18n.onLangChange === 'function') {
    DXI18n.onLangChange(refreshStreamModuleLanguage);
  }
  window.refreshStreamLanguage = refreshStreamModuleLanguage;
})();
