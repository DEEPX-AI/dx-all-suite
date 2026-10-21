/* ============================================================
   DX AI Studio — Shared i18n Core (Multi-Language)
   Supports N languages: EN, JA, KO, ES, ZH-CN, ZH-TW.

   Usage:
   1. Module sets window._DX_I18N_DICT before loading this script
      Dict format: { 'English key': { ko:'…', ja:'…', es:'…', 'zh-CN':'…', 'zh-TW':'…' } }
      Legacy format { 'English key': '<Korean text>' } is also supported.
   2. <script src="/static/shared/i18n.js"></script>
   3. Use T('key') or T('english', '<Korean text>') for translations
   ============================================================ */
(function () {
  'use strict';

  var STORAGE_KEY = 'dx-lang';
  var DEFAULT_LANG = 'en';
  var SUPPORTED_LANGS = ['en', 'ja', 'ko', 'es', 'zh-CN', 'zh-TW'];
  var LANG_LABELS = {
    'en': 'English', 'ja': '日本語', 'ko': '한국어',
    'es': 'Español', 'zh-CN': '简体中文', 'zh-TW': '繁體中文'
  };
  var LANG_SHORT = { 'en': 'EN', 'ja': 'JA', 'ko': 'KO', 'es': 'ES', 'zh-CN': '简', 'zh-TW': '繁' };

  var _dict = window._DX_I18N_DICT || {};
  var _selectors = window._DX_I18N_SELECTORS || '';
  var _placeholders = window._DX_I18N_PLACEHOLDERS || {};
  var _initCallbacks = window._DX_I18N_CALLBACKS || [];

  // Entries that exist only in the placeholder dictionary are visible to T() and data-i18n too — a module may
  // keep ordinary phrases in _DX_I18N_PLACEHOLDERS. The main dictionary wins (same keys are not overwritten).
  for (var _pk in _placeholders) {
    if (_placeholders.hasOwnProperty(_pk) && !_dict.hasOwnProperty(_pk)) _dict[_pk] = _placeholders[_pk];
  }

  // Text for the chrome every module shares (shell rail, toolbar, chat button), so each module's dictionary
  // need not repeat it. Used only when the module dictionary has no entry for the same key.
  var _SHARED = {
    'Modules': { ko: '모듈', ja: 'モジュール', 'zh-CN': '模块', 'zh-TW': '模組', es: 'Módulos' },
    'Hub': { ko: '홈', ja: 'ホーム', 'zh-CN': '首页', 'zh-TW': '首頁', es: 'Inicio' },
    'Language': { ko: '언어', ja: '言語', 'zh-CN': '语言', 'zh-TW': '語言', es: 'Idioma' },
    'Theme: dark': { ko: '테마: 어둡게', ja: 'テーマ: ダーク', 'zh-CN': '主题：深色', 'zh-TW': '主題：深色', es: 'Tema: oscuro' },
    'Theme: light': { ko: '테마: 밝게', ja: 'テーマ: ライト', 'zh-CN': '主题：浅色', 'zh-TW': '主題：淺色', es: 'Tema: claro' },
    'Theme: system': { ko: '테마: 시스템 설정', ja: 'テーマ: システム設定', 'zh-CN': '主题：跟随系统', 'zh-TW': '主題：跟隨系統', es: 'Tema: del sistema' },
    'Tutorial': { ko: '튜토리얼', ja: 'チュートリアル', 'zh-CN': '教程', 'zh-TW': '教學', es: 'Tutorial' },
    'Tutorial unavailable': { ko: '튜토리얼 없음', ja: 'チュートリアルなし', 'zh-CN': '暂无教程', 'zh-TW': '暫無教學', es: 'Tutorial no disponible' },
    'Settings': { ko: '설정', ja: '設定', 'zh-CN': '设置', 'zh-TW': '設定', es: 'Configuración' },
    'Chat': { ko: '채팅', ja: 'チャット', 'zh-CN': '聊天', 'zh-TW': '聊天', es: 'Chat' },
    'Pages': { ko: '페이지', ja: 'ページ', 'zh-CN': '页面', 'zh-TW': '頁面', es: 'Páginas' },
    'Close': { ko: '닫기', ja: '閉じる', 'zh-CN': '关闭', 'zh-TW': '關閉', es: 'Cerrar' },
    '{n} more pages': { ko: '페이지 {n}개 더 보기', ja: 'ほか {n} ページ', 'zh-CN': '另外 {n} 个页面', 'zh-TW': '另外 {n} 個頁面', es: '{n} páginas más' }
  };
  for (var _sk in _SHARED) {
    if (_SHARED.hasOwnProperty(_sk) && !_dict.hasOwnProperty(_sk)) _dict[_sk] = _SHARED[_sk];
  }

  // Reverse dictionary: any-language-value → English key
  var _rev = {};
  for (var en in _dict) {
    if (!_dict.hasOwnProperty(en)) continue;
    var entry = _dict[en];
    if (typeof entry === 'string') {
      _rev[entry] = en;
    } else if (typeof entry === 'object') {
      for (var l in entry) {
        if (entry.hasOwnProperty(l) && entry[l]) _rev[entry[l]] = en;
      }
    }
  }

  // A first-time visitor gets the browser language. The pick is saved so scripts that read dx-lang directly
  // (brand, toolbar, tutorial …) see the same language. A saved choice always wins.
  // Contract: tests/shared/test_browser_language_default_browser.py
  function _browserLang() {
    var list = (navigator.languages && navigator.languages.length) ? navigator.languages : [navigator.language || ''];
    for (var i = 0; i < list.length; i++) {
      var l = String(list[i] || '').toLowerCase();
      if (/^zh-(tw|hk|mo)\b/.test(l) || l.indexOf('zh-hant') === 0) return 'zh-TW';
      if (l.indexOf('zh') === 0) return 'zh-CN';
      var base = l.split('-')[0];
      if (base === 'en' || base === 'ko' || base === 'ja' || base === 'es') return base;
    }
    return DEFAULT_LANG;
  }
  var _saved = null;
  try { _saved = localStorage.getItem(STORAGE_KEY); } catch (_) { /* storage blocked */ }
  var _lang = _saved || _browserLang();
  if (SUPPORTED_LANGS.indexOf(_lang) === -1) _lang = DEFAULT_LANG;
  if (!_saved) { try { localStorage.setItem(STORAGE_KEY, _lang); } catch (_) { /* storage blocked */ } }
  var _callbacks = [];

  // T(key) or T(en, ko) backward compat
  function T(key, koFallback) {
    var e = _dict[key];
    if (!e) {
      if (_lang === 'ko' && koFallback) return koFallback;
      return key;
    }
    if (typeof e === 'string') return _lang === 'ko' ? e : key;
    if (Object.prototype.hasOwnProperty.call(e, _lang)) return e[_lang];
    return key;
  }

  function _lookup(key) {
    var e = _dict[key];
    if (!e) return null;
    if (typeof e === 'string') return _lang === 'ko' ? e : null;
    if (Object.prototype.hasOwnProperty.call(e, _lang)) return e[_lang];
    return null;
  }

  /* Cross-fade the text, only in documents that opt in with <html data-dx-fade> — modules switch instantly.
     _lang and the saved value change at once; only the screen fades. CSS sets the duration via
     html[data-dx-fading="lang"]. Same rule as _fade in dx-theme.js. */
  function _fade(kind, update) {
    var root = document.documentElement;
    var still = false;
    try { still = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (_) { /* noop */ }
    if (!kind || !root || !('dxFade' in root.dataset) || still || document.readyState !== 'complete'
        || typeof document.startViewTransition !== 'function') {
      update();
      return;
    }
    root.dataset.dxFading = kind;
    var done = function () { if (root.dataset.dxFading === kind) delete root.dataset.dxFading; };
    document.startViewTransition(update).finished.then(done, done);
  }

  function setLang(lang) {
    if (SUPPORTED_LANGS.indexOf(lang) === -1) return;
    var changed = lang !== _lang;
    _lang = lang;
    localStorage.setItem(STORAGE_KEY, lang);
    _fade(changed ? 'lang' : null, function () {
      SUPPORTED_LANGS.forEach(function (l) {
        document.body.classList.remove('lang-' + l);
      });
      document.body.classList.add('lang-' + lang);
      if (document.documentElement) document.documentElement.lang = lang;
      _applyDOM();
      var i;
      for (i = 0; i < _callbacks.length; i++) _callbacks[i](lang);
      for (i = 0; i < _initCallbacks.length; i++) _initCallbacks[i](lang);
      try {
        window.dispatchEvent(new CustomEvent('dx-lang-applied', { detail: { lang: lang } }));
      } catch (_) { /* non-DOM environments */ }
    });
  }

  function toggleLang() {
    // Cycle: en → ja → ko → es → zh-CN → zh-TW → en
    var idx = SUPPORTED_LANGS.indexOf(_lang);
    var next = SUPPORTED_LANGS[(idx + 1) % SUPPORTED_LANGS.length];
    setLang(next);
  }

  function _queryAll(scope, selector) {
    var items = Array.prototype.slice.call(scope.querySelectorAll(selector));
    if (scope.nodeType === 1 && scope.matches && scope.matches(selector)) {
      items.unshift(scope);
    }
    return items;
  }

  function _applyDOM(root) {
    var scope = root || document;
    if (_selectors) {
      _queryAll(scope, _selectors).forEach(function (el) {
        _translateEl(el);
      });
    }

    _queryAll(scope, '[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      var translated = _lookup(key);
      if (_lang === 'en') {
        el.textContent = key;
      } else if (translated !== null) {
        el.textContent = translated;
      }
    });

    _queryAll(scope, '[data-i18n-html]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-html');
      var e = _dict[key];
      if (!e || typeof e !== 'object') return;
      var val = Object.prototype.hasOwnProperty.call(e, _lang) ? e[_lang] : null;
      if (val !== null) el.innerHTML = val;
      else if (_lang === 'en') el.innerHTML = key;
    });

    _queryAll(scope, 'input[placeholder], textarea[placeholder]').forEach(function (el) {
      if (_lang === 'en') {
        var orig = el.getAttribute('data-i18n-ph-orig');
        if (orig) el.setAttribute('placeholder', orig);
        return;
      }
      var origKey = el.getAttribute('data-i18n-ph-orig');
      var ph = el.getAttribute('placeholder');
      var enPh = (origKey && _placeholders.hasOwnProperty(origKey)) ? origKey
               : (ph && _placeholders.hasOwnProperty(ph)) ? ph : null;
      if (enPh === null) return;
      var phEntry = _placeholders[enPh];
      var target;
      if (typeof phEntry === 'string') target = _lang === 'ko' ? phEntry : null;
      else if (typeof phEntry === 'object') target = phEntry[_lang];
      if (target) {
        el.setAttribute('data-i18n-ph-orig', enPh);
        el.setAttribute('placeholder', target);
      }
    });

    _queryAll(scope, '[data-i18n-placeholder]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-placeholder');
      if (!key) return;
      var translated = _lookup(key);
      el.setAttribute('placeholder', translated !== null ? translated : key);
    });

    _queryAll(scope, '[data-i18n-title]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-title');
      if (!key) return;
      var translated = _lookup(key);
      el.setAttribute('title', translated !== null ? translated : key);
    });

    _queryAll(scope, '[data-i18n-aria-label]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-aria-label');
      if (!key) return;
      var translated = _lookup(key);
      el.setAttribute('aria-label', translated !== null ? translated : key);
    });

    SUPPORTED_LANGS.forEach(function (l) {
      _queryAll(scope, 'span.' + l + ', small .' + l).forEach(function (el) {
        el.style.display = l === _lang ? '' : 'none';
      });
    });

    // 5b. Dynamic span injection for languages without HTML spans
    //     When _lang is ja/zh-CN/zh-TW and parent has .en+.ko but no ._lang span:
    //     → create span from dict, or show .en as fallback
    if (_lang !== 'en' && _lang !== 'ko') {
      var _enSpans = _queryAll(scope, 'span.en');
      for (var _si = 0; _si < _enSpans.length; _si++) {
        var _enSp = _enSpans[_si];
        var _par = _enSp.parentNode;
        if (!_par) continue;
        var _koSp = _par.querySelector('span.ko');
        if (!_koSp) continue;
        var _hasTarget = false;
        for (var _ci = 0; _ci < _par.children.length; _ci++) {
          if (_par.children[_ci].classList && _par.children[_ci].classList.contains(_lang)) {
            _hasTarget = true;
            break;
          }
        }
        if (_hasTarget) continue;
        var _enKey = _enSp.textContent.trim();
        var _tr = _lookup(_enKey);
        if (_tr !== null) {
          var _newSp = document.createElement('span');
          _newSp.className = _lang;
          _newSp.textContent = _tr;
          _par.insertBefore(_newSp, _enSp.nextSibling);
        } else {
          // No translation: show English as fallback
          _enSp.style.display = '';
        }
      }
    }

    var langEl = document.querySelector('#langToggle');
    if (langEl) {
      var langCodeEl = langEl.querySelector('.dx-lang-code');
      if (langCodeEl) {
        langCodeEl.textContent = LANG_SHORT[_lang] || _lang.toUpperCase();
      }
      langEl.querySelectorAll('.dx-lang-item').forEach(function (it) {
        it.classList.toggle('active', it.dataset.lang === _lang);
      });
      // Dual-toggle fallback
      var opts = langEl.querySelectorAll('.dx-toggle-opt');
      if (opts.length > 0) {
        for (var oi = 0; oi < opts.length; oi++) {
          if (opts[oi].dataset.val === _lang) opts[oi].classList.add('active');
          else opts[oi].classList.remove('active');
        }
      }
    }
  }

  function _translateEl(el) {
    if (!el.childNodes.length) return;
    // The chat widget translates its own labels (data-chat-t); a key missing here would put them back in English.
    if (el.hasAttribute('data-chat-t')) return;
    if (el.querySelector('.ko, .en, .ja, .es, .zh-CN, .zh-TW')) return;
    // Below, el.textContent is replaced wholesale, which wipes child elements.
    // A child that carries its own key owns the translation.
    // (.legend-item is a colour-dot span + a label span; flattening it here
    //  would drop the dot.)
    if (el.querySelector('[data-i18n], [data-i18n-html]')) return;
    // Icon + text (DXIcon.label): if the only child elements are icons, replace just the text nodes —
    // replacing textContent would drop the icon.
    // Same for elements holding inputs, buttons, links or images (e.g. <label>text <select>…</label>) —
    // replacing textContent would remove that control.
    var kids = el.children;
    if (kids.length && (el.querySelector('input, select, textarea, button, a, img, video, canvas') ||
        Array.prototype.every.call(kids, function (k) {
          return k.tagName && k.tagName.toLowerCase() === 'svg' && k.classList.contains('dx-ico');
        }))) {
      var texts = Array.prototype.filter.call(el.childNodes, function (n) { return n.nodeType === 3; });
      var plain = texts.map(function (n) { return n.nodeValue; }).join('').trim();
      if (!plain) return;
      if (!el.dataset.i18nOrig) el.dataset.i18nOrig = plain;
      var o = el.dataset.i18nOrig;
      var tr = _lang === 'en' ? (_rev[plain] || o) : _lookup(o);
      var out = (tr !== null && tr !== undefined) ? tr : o;
      texts.forEach(function (n, i) { n.nodeValue = i === texts.length - 1 ? ' ' + out : ''; });
      return;
    }
    var text = el.textContent.trim();
    if (!text) return;
    if (!el.dataset.i18nOrig) el.dataset.i18nOrig = text;
    var orig = el.dataset.i18nOrig;
    if (_lang === 'en') {
      el.textContent = _rev[el.textContent.trim()] || el.dataset.i18nOrig || el.textContent;
    } else {
      var translated = _lookup(orig);
      el.textContent = translated !== null ? translated : orig;
    }
  }

  function onLangChange(cb) {
    _callbacks.push(cb);
    return function unsubscribeLangChange() {
      var idx = _callbacks.indexOf(cb);
      if (idx !== -1) _callbacks.splice(idx, 1);
    };
  }

  // postMessage listener (launcher → sub-app sync)
  window.addEventListener('message', function (e) {
    if (e.data && e.data.type === 'dx-lang-change') {
      setLang(e.data.lang);
    }
  });

  function _init() {
    SUPPORTED_LANGS.forEach(function (l) {
      document.body.classList.remove('lang-' + l);
    });
    document.body.classList.add('lang-' + _lang);
    if (document.documentElement) document.documentElement.lang = _lang;
    setTimeout(_applyDOM, 50);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _init);
  } else {
    _init();
  }

  /** Let fragments injected later bring their own translations.
   *
   *  The launcher proxy injects hw_widget into the host page. Dictionaries are
   *  per module, so without this the widget's labels would have to be copied
   *  into every module dictionary.
   *  Existing keys are not overwritten: the module's wording wins. */
  function register(extra) {
    if (!extra) return;
    for (var key in extra) {
      if (!Object.prototype.hasOwnProperty.call(extra, key)) continue;
      if (Object.prototype.hasOwnProperty.call(_dict, key)) continue;
      _dict[key] = extra[key];
      var entry = extra[key];
      if (typeof entry === 'string') _rev[entry] = key;
      else if (typeof entry === 'object') {
        for (var l in entry) {
          if (Object.prototype.hasOwnProperty.call(entry, l) && entry[l]) _rev[entry[l]] = key;
        }
      }
    }
    _applyDOM();
  }

  window.DXI18n = {
    T: T,
    register: register,
    get lang() { return _lang; },
    setLang: setLang,
    toggleLang: toggleLang,
    applyLang: _applyDOM,
    onLangChange: onLangChange,
    dict: _dict,
    rev: _rev,
    SUPPORTED_LANGS: SUPPORTED_LANGS,
    LANG_LABELS: LANG_LABELS,
    LANG_SHORT: LANG_SHORT
  };

  window.T = T;
})();
