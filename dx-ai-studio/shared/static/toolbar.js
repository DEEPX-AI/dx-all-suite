/* ═══════════════════════════════════════════════════════════════
   DX AI Studio — Unified Toolbar
   Provides dropdown language selector and tutorial button.

   Usage:
     <link rel="stylesheet" href="/static/shared/toolbar.css">
     <script src="/static/shared/i18n.js"></script>
     <script src="/static/shared/toolbar.js"></script>
     <script>DXToolbar.init({ container: '.topbar-right' });</script>

   Prerequisites: shared/i18n.js must be loaded first (provides DXI18n).
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var _opts = {};
  var _tutorialOwner = null;
  var _tutorialInstance = null;
  var _tutorialClickHandler = null;

  function _getLang() {
    return (typeof DXI18n !== 'undefined') ? DXI18n.lang : (localStorage.getItem('dx-lang') || 'en');
  }

  function _setLang(code) {
    if (typeof DXI18n !== 'undefined') {
      DXI18n.setLang(code);
    } else {
      _updateLangUI();
    }
    try {
      if (window.parent !== window) {
        window.parent.postMessage({ type: 'dx-lang-change', lang: code }, '*');
      }
    } catch (e) {}
  }

  function _updateLangUI() {
    var langEl = document.getElementById('langToggle');
    if (!langEl) return;
    var lang = _getLang();
    var codeEl = langEl.querySelector('.dx-lang-code');
    if (codeEl) {
      var SHORT = (typeof DXI18n !== 'undefined') ? DXI18n.LANG_SHORT : { en: 'EN', ja: 'JA', ko: 'KO', es: 'ES', 'zh-CN': '简', 'zh-TW': '繁' };
      codeEl.textContent = SHORT[lang] || lang.toUpperCase();
    }
    // Query document-wide: the menu is re-parented to <body> while open (see _positionLangMenu),
    // so it is not always a descendant of #langToggle.
    document.querySelectorAll('.dx-lang-item').forEach(function (it) {
      it.classList.toggle('active', it.dataset.lang === lang);
    });
  }

  function _makeLangDropdown() {
    var LABELS = (typeof DXI18n !== 'undefined') ? DXI18n.LANG_LABELS :
      { en: 'English', ja: '日本語', ko: '한국어', es: 'Español', 'zh-CN': '简体中文', 'zh-TW': '繁體中文' };
    var SHORT = (typeof DXI18n !== 'undefined') ? DXI18n.LANG_SHORT :
      { en: 'EN', ja: 'JA', ko: 'KO', es: 'ES', 'zh-CN': '简', 'zh-TW': '繁' };
    var LANGS = (typeof DXI18n !== 'undefined') ? DXI18n.SUPPORTED_LANGS :
      ['en', 'ja', 'ko', 'es', 'zh-CN', 'zh-TW'];

    var wrap = document.createElement('div');
    wrap.className = 'dx-lang-dropdown';
    wrap.id = 'langToggle';

    var btn = document.createElement('button');
    btn.className = 'dx-toolbar-btn dx-lang-btn';
    btn.title = 'Language';

    var iconSpan = document.createElement('span');
    iconSpan.className = 'dx-lang-icon';
    iconSpan.textContent = '🌏';

    var codeSpan = document.createElement('span');
    codeSpan.className = 'dx-lang-code';
    codeSpan.textContent = SHORT[_getLang()] || 'EN';

    var arrowSpan = document.createElement('span');
    arrowSpan.className = 'dx-lang-arrow';
    arrowSpan.textContent = '▾';

    btn.appendChild(iconSpan);
    btn.appendChild(codeSpan);
    btn.appendChild(arrowSpan);

    var menu = document.createElement('div');
    menu.className = 'dx-lang-menu';
    LANGS.forEach(function (code) {
      var item = document.createElement('div');
      item.className = 'dx-lang-item';
      item.dataset.lang = code;
      item.textContent = LABELS[code] || code;
      if (code === _getLang()) item.classList.add('active');
      item.addEventListener('click', function (e) {
        e.stopPropagation();
        _setLang(code);
        _closeLangMenu();
      });
      menu.appendChild(item);
    });

    function _positionLangMenu() {
      if (!wrap.classList.contains('open')) return;
      // Re-parent to <body> so position:fixed is resolved against the viewport. Inside a header
      // with backdrop-filter/transform (module chrome, about-topbar, sdk-topbar) that ancestor
      // becomes the containing block for fixed descendants, which would offset the menu downward
      // (the "menu appears far below the button" bug in About). <body> has no such ancestor.
      if (menu.parentNode !== document.body) document.body.appendChild(menu);
      var rect = btn.getBoundingClientRect();
      menu.style.display = 'block';
      menu.style.position = 'fixed';
      menu.style.top = (rect.bottom + 4) + 'px';
      var menuWidth = menu.offsetWidth || 140;
      var left = rect.right - menuWidth;
      if (left < 8) left = 8;
      if (left + menuWidth > window.innerWidth - 8) {
        left = Math.max(8, window.innerWidth - menuWidth - 8);
      }
      menu.style.left = left + 'px';
      menu.style.right = 'auto';
      menu.style.zIndex = '10050';
    }

    function _closeLangMenu() {
      wrap.classList.remove('open');
      // _positionLangMenu set display:block + position:fixed on open. Reset BOTH — clearing only
      // position leaves display:block inline, which overrides the CSS `display:none` and keeps the
      // 140px menu rendered as position:absolute (CSS fallback). That stray absolute box overflows
      // the toolbar's overflow-x:auto and leaves it stuck with a horizontal scrollbar after close.
      menu.style.display = '';
      menu.style.position = '';
      menu.style.top = '';
      menu.style.left = '';
      menu.style.right = '';
      menu.style.zIndex = '';
      // Return the menu under its dropdown when idle (keeps the DOM tidy and CSS base state).
      if (menu.parentNode !== wrap) wrap.appendChild(menu);
    }

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      if (wrap.classList.contains('open')) {
        _closeLangMenu();
      } else {
        wrap.classList.add('open');
        _positionLangMenu();
      }
    });

    wrap.appendChild(btn);
    wrap.appendChild(menu);

    window.addEventListener('resize', _positionLangMenu);
    window.addEventListener('scroll', _positionLangMenu, true);

    document.addEventListener('click', function (e) {
      if (wrap.contains(e.target)) return;
      _closeLangMenu();
    });

    if (typeof DXI18n !== 'undefined') {
      DXI18n.onLangChange(function () { _updateLangUI(); });
    }

    return wrap;
  }

  function _makeIconBtn(emoji, title, onClick) {
    var btn = document.createElement('button');
    btn.className = 'dx-toolbar-btn';
    btn.title = title;
    btn.textContent = emoji;
    btn.addEventListener('click', onClick);
    return btn;
  }

  function buildToolbar(containerSelector) {
    var container = document.querySelector(containerSelector);
    if (!container) {
      console.warn('[DXToolbar] Container not found:', containerSelector);
      return;
    }
    if (document.getElementById('dxToolbar')) return;

    var toolbar = document.createElement('div');
    toolbar.className = 'dx-toolbar';
    toolbar.id = 'dxToolbar';

    toolbar.appendChild(_makeLangDropdown());

    if (_opts.tutorial) {
      _tutorialClickHandler = function () {
        if (_opts.tutorial && typeof _opts.tutorial.toggleTOC === 'function') {
          _opts.tutorial.toggleTOC();
        }
      };
      var tutBtn = _makeIconBtn('🎓', 'Tutorial', _tutorialClickHandler);
      tutBtn.id = 'dxToolbarTutorial';
      toolbar.appendChild(tutBtn);
      if (_opts.tutorial._toggleBtnEl !== undefined) {
        _opts.tutorial._toggleBtnEl = tutBtn;
      }
    }

    if (typeof _opts.onSettings === 'function') {
      var settingsBtn = _makeIconBtn('⚙️', 'Settings', _opts.onSettings);
      settingsBtn.id = 'dxToolbarSettings';
      toolbar.appendChild(settingsBtn);
    }

    container.appendChild(toolbar);
  }

  window.addEventListener('message', function (e) {
    if (!e.data || !e.data.type) return;
    if (e.data.type === 'dx-lang-change' && e.data.lang) {
      if (typeof DXI18n !== 'undefined' && DXI18n.lang !== e.data.lang) {
        DXI18n.setLang(e.data.lang);
      } else {
        _updateLangUI();
      }
    }
  });

  function init(opts) {
    opts = opts || {};
    _opts = opts;
    var containerSel = opts.container || '.topbar-right';

    function _doInit() {
      buildToolbar(containerSel);
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', _doInit);
    } else {
      _doInit();
    }
  }

  window.DXToolbar = {
    init: init,
    toggleLang: function () {
      if (typeof DXI18n !== 'undefined') {
        DXI18n.toggleLang();
      } else {
        _updateLangUI();
      }
    },
    connectTutorial: function (tutorialInstance, opts) {
      opts = opts || {};
      var owner = opts.owner || null;
      _opts.tutorial = tutorialInstance;
      _tutorialInstance = tutorialInstance;
      _tutorialOwner = owner;

      var toolbar = document.getElementById('dxToolbar');
      if (!toolbar) return;

      var tutBtn = document.getElementById('dxToolbarTutorial');
      var newTutHandler = function () {
        if (_tutorialInstance && typeof _tutorialInstance.toggleTOC === 'function') {
          _tutorialInstance.toggleTOC();
        }
      };

      if (tutBtn) {
        if (_tutorialClickHandler) {
          tutBtn.removeEventListener('click', _tutorialClickHandler);
        }
        tutBtn.addEventListener('click', newTutHandler);
      } else {
        var langDrop = document.getElementById('langToggle');
        var insertRef = langDrop ? langDrop.nextSibling : null;
        tutBtn = _makeIconBtn('🎓', 'Tutorial', newTutHandler);
        tutBtn.id = 'dxToolbarTutorial';
        if (insertRef) toolbar.insertBefore(tutBtn, insertRef);
        else toolbar.appendChild(tutBtn);
      }
      tutBtn.disabled = false;
      tutBtn.removeAttribute('aria-disabled');
      tutBtn.title = 'Tutorial';
      _tutorialClickHandler = newTutHandler;
      if (tutorialInstance._toggleBtnEl !== undefined) {
        tutorialInstance._toggleBtnEl = tutBtn;
      }

      var helpBtn = document.getElementById('dxToolbarHelp');
      if (helpBtn && helpBtn.parentNode) {
        helpBtn.parentNode.removeChild(helpBtn);
      }
    },
    disconnectTutorial: function (owner) {
      if (_tutorialOwner !== owner) return;
      var tutBtn = document.getElementById('dxToolbarTutorial');
      if (tutBtn && _tutorialClickHandler) {
        tutBtn.removeEventListener('click', _tutorialClickHandler);
        _tutorialClickHandler = null;
      }
      if (tutBtn) {
        tutBtn.disabled = true;
        tutBtn.setAttribute('aria-disabled', 'true');
        tutBtn.title = 'Tutorial unavailable';
      }
      _tutorialInstance = null;
      _tutorialOwner = null;
      _opts.tutorial = null;
    }
  };

  window.toggleLang = function () {
    if (typeof DXI18n !== 'undefined') {
      DXI18n.toggleLang();
    } else {
      _updateLangUI();
    }
  };
})();
