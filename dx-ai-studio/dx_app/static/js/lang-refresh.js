/* DX App — language refresh registry (load after page scripts, before app.js) */
(function () {
  'use strict';
  window.__dxAppLangRefreshers = window.__dxAppLangRefreshers || [];
  window.registerLangRefresher = function (fn) {
    if (typeof fn === 'function') window.__dxAppLangRefreshers.push(fn);
  };

  function refreshDxAppModuleLanguage() {
    if (typeof refreshActivePageLanguage === 'function') refreshActivePageLanguage();
    window.__dxAppLangRefreshers.forEach(function (fn) {
      try { fn(); } catch (e) { console.error('[lang-refresh]', e); }
    });
    if (typeof DXI18n !== 'undefined' && typeof DXI18n.applyLang === 'function') {
      DXI18n.applyLang(document);
    }
  }

  if (typeof DXI18n !== 'undefined' && typeof DXI18n.onLangChange === 'function') {
    DXI18n.onLangChange(refreshDxAppModuleLanguage);
  }
})();
