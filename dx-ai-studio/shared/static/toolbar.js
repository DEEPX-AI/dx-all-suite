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

  /* Button names (title · aria-label) keep their key so a language change translates them again. The text
     lives in the shared chrome dictionary in shared/static/i18n.js. */
  function _tr(key) {
    return (typeof window.T === 'function') ? window.T(key) : key;
  }

  function _label(el, key) {
    el.dataset.dxTip = key;
    el.title = _tr(key);
    el.setAttribute('aria-label', _tr(key));
  }

  function _relabelAll() {
    document.querySelectorAll('#dxToolbar [data-dx-tip]').forEach(function (el) {
      el.title = _tr(el.dataset.dxTip);
      el.setAttribute('aria-label', _tr(el.dataset.dxTip));
    });
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
      it.setAttribute('aria-checked', String(it.dataset.lang === lang));
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
    btn.type = 'button';
    btn.className = 'dx-toolbar-btn dx-lang-btn';
    _label(btn, 'Language');
    btn.setAttribute('aria-haspopup', 'menu');
    btn.setAttribute('aria-expanded', 'false');

    var iconSpan = document.createElement('span');
    iconSpan.className = 'dx-lang-icon';
    iconSpan.appendChild(_icon('globe'));

    var codeSpan = document.createElement('span');
    codeSpan.className = 'dx-lang-code';
    codeSpan.textContent = SHORT[_getLang()] || 'EN';

    var arrowSpan = document.createElement('span');
    arrowSpan.className = 'dx-lang-arrow';
    arrowSpan.appendChild(_icon('chevd'));

    btn.appendChild(iconSpan);
    btn.appendChild(codeSpan);
    btn.appendChild(arrowSpan);

    var menu = document.createElement('div');
    menu.className = 'dx-lang-menu';
    menu.setAttribute('role', 'menu');
    LANGS.forEach(function (code) {
      /* A button, so the keyboard can reach it with Tab and pick with Enter · Space */
      var item = document.createElement('button');
      item.type = 'button';
      item.className = 'dx-lang-item';
      item.dataset.lang = code;
      item.lang = code;
      item.setAttribute('role', 'menuitemradio');
      item.setAttribute('aria-checked', String(code === _getLang()));
      item.tabIndex = -1;
      item.textContent = LABELS[code] || code;
      if (code === _getLang()) item.classList.add('active');
      item.addEventListener('click', function (e) {
        e.stopPropagation();
        var fromKey = e.detail === 0;          // picked with Enter · Space: return focus to the button
        _setLang(code);
        _closeLangMenu();
        if (fromKey) btn.focus();
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

    function _items() { return Array.prototype.slice.call(menu.querySelectorAll('.dx-lang-item')); }

    function _openLangMenu(focusItem) {
      wrap.classList.add('open');
      btn.setAttribute('aria-expanded', 'true');
      _positionLangMenu();
      if (focusItem) {
        var list = _items();
        var cur = menu.querySelector('.dx-lang-item.active') || list[0];
        if (cur) cur.focus();
      }
    }

    function _closeLangMenu() {
      wrap.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
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
        _openLangMenu(e.detail === 0);       // opened from the keyboard: focus the current language
      }
    });
    btn.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        _openLangMenu(true);
      }
    });
    menu.addEventListener('keydown', function (e) {
      var list = _items();
      var i = list.indexOf(document.activeElement);
      var next = null;
      if (e.key === 'ArrowDown') next = list[(i + 1) % list.length];
      else if (e.key === 'ArrowUp') next = list[(i - 1 + list.length) % list.length];
      else if (e.key === 'Home') next = list[0];
      else if (e.key === 'End') next = list[list.length - 1];
      else if (e.key === 'Escape') {
        e.preventDefault();                  // keep this Escape from also closing an outer dialog or screen
        e.stopPropagation();
        _closeLangMenu();
        btn.focus();
        return;
      } else if (e.key === 'Tab') {
        _closeLangMenu();
        return;
      }
      if (next) { e.preventDefault(); next.focus(); }
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
      DXI18n.onLangChange(function () { _updateLangUI(); _relabelAll(); });
    }

    return wrap;
  }

  /* Icons come from the shared sprite — emoji render differently per OS and font. Without DXIcon
     (a document that did not load dx-icon.js) the spot stays empty. */
  function _icon(name) {
    if (window.DXIcon && window.DXIcon.el) return window.DXIcon.el(name);
    return document.createTextNode('');
  }

  function _setIcon(btn, name) {
    btn.textContent = '';
    btn.appendChild(_icon(name));
    btn.dataset.icon = name;
  }

  function _makeIconBtn(iconName, title, onClick) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'dx-toolbar-btn';
    _label(btn, title);
    _setIcon(btn, iconName);
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

    if (typeof DXTheme !== 'undefined') {
      /* Each of the three states has its own icon: dark · light · system (half circle). The title names the current state too. */
      var THEME_ICON = { dark: 'moon', light: 'sun', system: 'theme' };
      var THEME_TITLE = { dark: 'Theme: dark', light: 'Theme: light', system: 'Theme: system' };
      var themeBtn = _makeIconBtn(THEME_ICON[DXTheme.getTheme()], THEME_TITLE[DXTheme.getTheme()], function () {
        DXTheme.cycle();
      });
      themeBtn.id = 'dxToolbarTheme';
      DXTheme.onThemeChange(function (t) {
        _setIcon(themeBtn, THEME_ICON[t]);
        _label(themeBtn, THEME_TITLE[t]);
      });
      toolbar.appendChild(themeBtn);
    }

    if (_opts.tutorial) {
      _tutorialClickHandler = function () {
        if (_opts.tutorial && typeof _opts.tutorial.toggleTOC === 'function') {
          _opts.tutorial.toggleTOC();
        }
      };
      var tutBtn = _makeIconBtn('graduation', 'Tutorial', _tutorialClickHandler);
      tutBtn.id = 'dxToolbarTutorial';
      toolbar.appendChild(tutBtn);
      if (_opts.tutorial._toggleBtnEl !== undefined) {
        _opts.tutorial._toggleBtnEl = tutBtn;
      }
    }

    if (typeof _opts.onSettings === 'function') {
      var settingsBtn = _makeIconBtn('gear', 'Settings', _opts.onSettings);
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
        // Same order as the launcher — language · theme · tutorial · (settings).
        var settingsRef = document.getElementById('dxToolbarSettings');
        var insertRef = settingsRef && settingsRef.parentNode === toolbar ? settingsRef : null;
        tutBtn = _makeIconBtn('graduation', 'Tutorial', newTutHandler);
        tutBtn.id = 'dxToolbarTutorial';
        if (insertRef) toolbar.insertBefore(tutBtn, insertRef);
        else toolbar.appendChild(tutBtn);
      }
      tutBtn.disabled = false;
      tutBtn.removeAttribute('aria-disabled');
      _label(tutBtn, 'Tutorial');
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
        _label(tutBtn, 'Tutorial unavailable');
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
