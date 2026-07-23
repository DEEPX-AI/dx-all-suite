
(function() {
  var ns = window.DXLauncher;

  ns._lang = (typeof DXI18n !== 'undefined') ? DXI18n.lang : (localStorage.getItem('dx-lang') || 'en');

  function _lt(en, ko, ja, zhCN, zhTW, es) {
    var translations = { ko: ko, ja: ja, es: es, 'zh-CN': zhCN, 'zh-TW': zhTW };
    return translations[ns._lang] || en;
  }

  function selectLang(lang) {
    // Supported body classes: lang-en, lang-ja, lang-ko, lang-es, lang-zh-CN, lang-zh-TW
    var VALID_LANGS = ['en', 'ja', 'ko', 'es', 'zh-CN', 'zh-TW'];
    if (VALID_LANGS.indexOf(lang) === -1) return;
    if (ns._lang === lang && document.body.classList.contains('lang-' + lang)) return;
    ns._lang = lang;
    localStorage.setItem('dx-lang', lang);
    ns.SUPPORTED_LANGS.forEach(function(l) { document.body.classList.remove('lang-' + l); });
    document.body.classList.add('lang-' + lang);
    if (document.documentElement) document.documentElement.lang = lang;
    if (typeof DXI18n !== 'undefined' && DXI18n.lang !== lang) {
      DXI18n.setLang(lang);
    }
    _updateLangUI();
    if (typeof ns.refreshLauncherChrome === 'function') ns.refreshLauncherChrome();
    ns._sendToIframe({ type: 'dx-lang-change', lang: lang });
    var dd = document.getElementById('langToggle');
    if (dd) dd.classList.remove('open');
  }

  function toggleLang() {
    var idx = ns.SUPPORTED_LANGS.indexOf(ns._lang);
    selectLang(ns.SUPPORTED_LANGS[(idx + 1) % ns.SUPPORTED_LANGS.length]);
  }

  function _updateLangUI() {
    var codeEl = document.querySelector('#langToggle .dx-lang-code');
    if (codeEl) codeEl.textContent = ns.LANG_SHORT[ns._lang] || ns._lang.toUpperCase();
    document.querySelectorAll('#langToggle .dx-lang-item').forEach(function(it) {
      it.classList.toggle('active', it.dataset.lang === ns._lang);
    });
  }

  // Sync launcher _lang with DXI18n
  if (typeof DXI18n !== 'undefined') {
    DXI18n.onLangChange(function(lang) {
      ns._lang = lang;
    });
  }

  // Iframe message helper — sync all loaded modules (including hidden) until launcher closes
  function _sendToIframe(msg) {
    if (typeof ns.broadcastToModuleIframes === 'function') {
      ns.broadcastToModuleIframes(msg);
      return;
    }
    var iframe = document.getElementById('appIframe');
    if (iframe && iframe.contentWindow) {
      try { iframe.contentWindow.postMessage(msg, '*'); } catch(e) {}
    }
  }

  function syncLangFromStorage() {
    var stored = localStorage.getItem('dx-lang') || 'en';
    selectLang(stored);
  }

  // Child module iframe → launcher chrome sync (shared localStorage + body class)
  window.addEventListener('message', function(e) {
    if (!e.data || e.data.type !== 'dx-lang-change' || !e.data.lang) return;
    if (e.source === window) return;
    selectLang(e.data.lang);
  });

  ns._lt = _lt;
  ns.selectLang = selectLang;
  ns.syncLangFromStorage = syncLangFromStorage;
  ns.toggleLang = toggleLang;
  ns._updateLangUI = _updateLangUI;
  ns._sendToIframe = _sendToIframe;
})();
