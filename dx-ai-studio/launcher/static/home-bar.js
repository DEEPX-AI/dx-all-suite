/* ─── Launcher home — the glass bar's links, and when they can't go anywhere ─

   The studio also runs on closed factory and site networks, where the bar's links would only
   open an empty tab. There the links are dimmed, made inert, and labelled "Offline".

   Two ways to find out: navigator.onLine === false settles it at once. Otherwise the first hover
   over the bar sends one HEAD to developer.deepx.ai (no-cors: the response is unreadable, but a
   network failure still rejects). Nothing goes out at load time — the --offline contract. The
   result is kept in sessionStorage for the session.
   Contract: tests/launcher/test_home_bar_contract.py, test_home_bar_browser.py */
(function () {
  'use strict';

  var KEY = 'dx-home-links';
  var PROBE = 'https://developer.deepx.ai/';

  function $(id) { return document.getElementById(id); }
  function _read() {
    try { return sessionStorage.getItem(KEY); } catch (e) { return null; }
  }
  function _write(v) {
    try {
      if (v === null) sessionStorage.removeItem(KEY); else sessionStorage.setItem(KEY, v);
    } catch (e) { /* even if storage is blocked, this page still shows the right state */ }
  }

  var _asked = false;

  function paint() {
    var bar = $('homeBar');
    if (!bar) return;
    var off = navigator.onLine === false || _read() === 'unreachable';
    bar.classList.toggle('is-offline', off);
    var note = $('homeBarOffline');
    if (note) note.hidden = !off;
    Array.prototype.forEach.call(bar.querySelectorAll('a[href^="http"]'), function (a) {
      if (off) a.setAttribute('aria-disabled', 'true');
      else a.removeAttribute('aria-disabled');
    });
  }

  function probe() {
    if (_asked || _read() || navigator.onLine === false) return;
    _asked = true;
    fetch(PROBE, { mode: 'no-cors', method: 'HEAD', cache: 'no-store' })
      .then(function () { _write('reachable'); })
      .catch(function () { _write('unreachable'); paint(); });
  }

  function init() {
    var bar = $('homeBar');
    if (!bar) return;
    paint();
    ['pointerenter', 'focusin'].forEach(function (ev) { bar.addEventListener(ev, probe); });
    bar.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[aria-disabled="true"]');
      if (a) e.preventDefault();
    });
    window.addEventListener('offline', paint);
    /* When the network comes back the old answer is stale — ask again on the next hover. */
    window.addEventListener('online', function () { _write(null); _asked = false; paint(); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
