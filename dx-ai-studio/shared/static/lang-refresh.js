(function () {
  'use strict';

  function translateKey(key) {
    if (typeof window.T === 'function') return window.T(key);
    return key;
  }

  function relocalizeByKey(root, selector) {
    var scope = root || document;
    var sel = selector || '[data-i18n-key]';
    scope.querySelectorAll(sel).forEach(function (el) {
      var key = el.getAttribute('data-i18n-key');
      if (!key) return;
      el.textContent = translateKey(key);
    });
  }

  function relocalizeSelectOptions(selectEl, keyAttr) {
    if (!selectEl) return;
    var attr = keyAttr || 'data-i18n';
    Array.prototype.forEach.call(selectEl.options, function (opt) {
      var key = opt.getAttribute(attr);
      if (key) opt.textContent = translateKey(key);
    });
  }

  function snapshotSelect(selectEl) {
    if (!selectEl) return null;
    return { value: selectEl.value, index: selectEl.selectedIndex };
  }

  function restoreSelect(selectEl, snap) {
    if (!selectEl || !snap) return;
    if (snap.value && Array.prototype.some.call(selectEl.options, function (o) { return o.value === snap.value; })) {
      selectEl.value = snap.value;
    } else if (snap.index >= 0 && snap.index < selectEl.options.length) {
      selectEl.selectedIndex = snap.index;
    }
  }

  function relocalizePlaceholders(root) {
    if (typeof window.DXI18n !== 'undefined' && typeof DXI18n.applyLang === 'function') {
      DXI18n.applyLang(root || document);
    }
  }

  window.LangRefresh = {
    translateKey: translateKey,
    relocalizeByKey: relocalizeByKey,
    relocalizeSelectOptions: relocalizeSelectOptions,
    snapshotSelect: snapshotSelect,
    restoreSelect: restoreSelect,
    relocalizePlaceholders: relocalizePlaceholders,
  };
})();
