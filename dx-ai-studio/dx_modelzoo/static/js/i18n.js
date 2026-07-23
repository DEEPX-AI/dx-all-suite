/* DX Model Zoo — i18n Bootstrap */
'use strict';

/* Ensure dict is initialized (i18n-core.js should have run first) */
window._DX_I18N_DICT = window._DX_I18N_DICT || {};

window._DX_I18N_PLACEHOLDERS = {
  'Search models...': {
    en: 'Search models...',
    ko: '모델 검색...',
    ja: 'モデルを検索...',
    es: 'Buscar modelos...',
    'zh-CN': '搜索模型...',
    'zh-TW': '搜尋模型...',
  },
};

window._DX_I18N_CALLBACKS = [function(lang) {
  document.querySelectorAll('[data-title-ko]').forEach(function(el) {
    el.title = el.getAttribute('data-title-' + lang) || el.title;
  });
  if (typeof filterAndRender === 'function') filterAndRender();
  if (location.hash.startsWith('#model=') && typeof renderDetailPage === 'function') {
    let modelId = location.hash.slice(7);
    if (typeof getModelIdFromHash === 'function') {
      modelId = getModelIdFromHash(location.hash);
    } else {
      try { modelId = decodeURIComponent(modelId); } catch (_) { /* keep raw hash payload */ }
    }
    renderDetailPage(modelId);
  }
  if (window.__modelZooLangRefreshers) {
    window.__modelZooLangRefreshers.forEach(function(fn) {
      try { fn(); } catch (e) { console.error('[modelzoo-lang-refresh]', e); }
    });
  }
}];
window.__modelZooLangRefreshers = window.__modelZooLangRefreshers || [];
window.registerModelZooLangRefresher = function(fn) {
  if (typeof fn === 'function') window.__modelZooLangRefreshers.push(fn);
};

if (typeof DXI18n !== 'undefined' && typeof DXI18n.onLangChange === 'function') {
  DXI18n.onLangChange(function refreshModelZooLanguage(lang) {
    if (typeof filterAndRender === 'function') filterAndRender();
    if (location.hash.startsWith('#model=') && typeof renderDetailPage === 'function') {
      var modelId = location.hash.slice(7);
      if (typeof getModelIdFromHash === 'function') modelId = getModelIdFromHash(location.hash);
      else try { modelId = decodeURIComponent(modelId); } catch (_) {}
      renderDetailPage(modelId);
    }
    if (window.__modelZooLangRefreshers) {
      window.__modelZooLangRefreshers.forEach(function(fn) {
        try { fn(); } catch (e) { console.error('[modelzoo-lang-refresh]', e); }
      });
    }
  });
}
