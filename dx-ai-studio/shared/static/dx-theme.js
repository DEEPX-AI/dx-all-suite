/* ============================================================
   DX AI Studio — shared theme state
   Three states: 'dark' | 'light' | 'system'
   Storage key 'dx-theme' (same convention as 'dx-lang' for language).
   ============================================================ */
(function () {
  'use strict';

  var STORAGE_KEY = 'dx-theme';
  var DEFAULT_THEME = 'system';
  var SUPPORTED = ['dark', 'light', 'system'];
  var _callbacks = [];

  var _theme = DEFAULT_THEME;
  try {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (SUPPORTED.indexOf(stored) !== -1) _theme = stored;
  } catch (e) { /* private mode — fall back to the default */ }

  function _apply(theme) {
    var root = document.documentElement;
    if (!root) return;
    if (theme === 'system') root.removeAttribute('data-theme');
    else root.setAttribute('data-theme', theme);
  }

  // Applied before first paint so the first frame does not flash the wrong theme.
  // That is why this script comes after the CSS links in <head> and before the body scripts.
  _apply(_theme);

  function getTheme() { return _theme; }

  function resolved() {
    if (_theme !== 'system') return _theme;
    try {
      return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    } catch (e) { return 'dark'; }
  }

  /* Dark ↔ light cross-fade, only in documents that opt in with <html data-dx-fade>
     — modules switch instantly. State (_theme and the saved value) changes at once; only the screen fades.
     CSS sets the duration via html[data-dx-fading="theme"]. */
  function _fade(kind, update) {
    var root = document.documentElement;
    var still = false;
    try { still = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { /* noop */ }
    if (!kind || !root || !('dxFade' in root.dataset) || still || document.readyState !== 'complete'
        || typeof document.startViewTransition !== 'function') {
      update();
      return;
    }
    root.dataset.dxFading = kind;
    var done = function () { if (root.dataset.dxFading === kind) delete root.dataset.dxFading; };
    document.startViewTransition(update).finished.then(done, done);
  }

  function setTheme(theme, opts) {
    if (SUPPORTED.indexOf(theme) === -1) return;
    var changed = theme !== _theme;
    _theme = theme;
    try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) { /* noop */ }
    _fade(changed ? 'theme' : null, function () {
      _apply(theme);
      for (var i = 0; i < _callbacks.length; i++) _callbacks[i](theme);
      try {
        window.dispatchEvent(new CustomEvent('dx-theme-applied', { detail: { theme: theme } }));
      } catch (e) { /* non-DOM environment */ }
    });

    if (!(opts && opts.silent)) _broadcast(theme);
  }

  function cycle() {
    var next = SUPPORTED[(SUPPORTED.indexOf(_theme) + 1) % SUPPORTED.length];
    setTheme(next);
    return next;
  }

  function onThemeChange(fn) { if (typeof fn === 'function') _callbacks.push(fn); }

  /* The launcher shows modules in an iframe. Post the change both ways (parent ↔ child)
     so the hub and the module never disagree on the theme. Without an iframe both
     calls are no-ops. */
  function _broadcast(theme) {
    var msg = { type: 'dx-theme-change', theme: theme };
    try {
      if (window.parent && window.parent !== window) window.parent.postMessage(msg, '*');
    } catch (e) { /* cross-origin */ }
    try {
      var frames = document.querySelectorAll('iframe');
      for (var i = 0; i < frames.length; i++) {
        if (frames[i].contentWindow) frames[i].contentWindow.postMessage(msg, '*');
      }
    } catch (e) { /* noop */ }
  }

  window.addEventListener('message', function (e) {
    if (!e.data || e.data.type !== 'dx-theme-change') return;
    if (e.data.theme === _theme) return;
    // silent: re-posting what we received would echo between parent and child.
    setTheme(e.data.theme, { silent: true });
  });

  /* In the system state CSS follows an OS theme change on its own,
     but readers of resolved() (chart colours etc.) need to hear about it. */
  try {
    var mq = window.matchMedia('(prefers-color-scheme: light)');
    var onSystemChange = function () {
      if (_theme !== 'system') return;
      for (var i = 0; i < _callbacks.length; i++) _callbacks[i](_theme);
    };
    if (mq.addEventListener) mq.addEventListener('change', onSystemChange);
    else if (mq.addListener) mq.addListener(onSystemChange);
  } catch (e) { /* matchMedia not supported */ }

  window.DXTheme = {
    getTheme: getTheme,
    setTheme: setTheme,
    resolved: resolved,
    cycle: cycle,
    onThemeChange: onThemeChange,
    SUPPORTED: SUPPORTED
  };
})();
