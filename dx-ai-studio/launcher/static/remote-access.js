/* ── Connected browsers ──────────────────────────────────────
 *
 * The launcher answers other computers on the network, and each of their browsers pairs
 * once with the 6-digit code on the launcher's console. This is where the
 * board's owner sees which browsers are paired and disconnects one, and where a remote
 * browser disconnects itself.
 *
 * The button exists only while pairing does (`/api/auth/status` → pairing). A launcher
 * bound to loopback has nothing to show, so it shows nothing. The code is never put on
 * this screen — it stays on the console, where only someone at the board can read it.
 *
 * Contract: tests/shared/test_remote_access.py, tests/launcher/test_connected_browsers_browser.py
 */
(function () {
  'use strict';

  var ns = window.DXLauncher = window.DXLauncher || {};
  var _status = null;
  var _dialog = null;
  var _focusKey = null;

  function _t(key) {
    return (window.DXI18n && window.DXI18n.T) ? window.DXI18n.T(key) : key;
  }
  function _lang() {
    return (window.DXI18n && window.DXI18n.lang) || document.documentElement.lang || 'en';
  }
  function _el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function _json(url, opts) {
    return fetch(url, Object.assign({ credentials: 'same-origin', cache: 'no-store' }, opts || {}))
      .then(function (r) {
        if (!r.ok) throw new Error(String(r.status));
        return r.status === 204 ? {} : r.json();
      });
  }
  function _post(url, body) {
    return _json(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body || {})
    });
  }

  /* "Chrome · Windows" — names of products, so they stay as they are in every language */
  function _device(ua) {
    ua = ua || '';
    var browser = /Edg\//.test(ua) ? 'Edge'
      : /OPR\//.test(ua) ? 'Opera'
      : /Firefox\//.test(ua) ? 'Firefox'
      : /Chrome\//.test(ua) ? 'Chrome'
      : /Safari\//.test(ua) ? 'Safari' : '';
    var os = /Windows/.test(ua) ? 'Windows'
      : /Android/.test(ua) ? 'Android'
      : /iPhone|iPad|iOS/.test(ua) ? 'iOS'
      : /Mac OS X|Macintosh/.test(ua) ? 'macOS'
      : /CrOS/.test(ua) ? 'ChromeOS'
      : /Linux/.test(ua) ? 'Linux' : '';
    if (!browser && !os) return _t('Unknown browser');
    return [browser, os].filter(Boolean).join(' · ');
  }

  function _ago(sec) {
    var diff = Math.round((sec * 1000 - Date.now()) / 1000);
    var units = [['day', 86400], ['hour', 3600], ['minute', 60], ['second', 1]];
    try {
      var rtf = new Intl.RelativeTimeFormat(_lang(), { numeric: 'auto' });
      for (var i = 0; i < units.length; i++) {
        if (Math.abs(diff) >= units[i][1] || units[i][0] === 'second') {
          var n = Math.round(diff / units[i][1]);
          return rtf.format(units[i][0] === 'second' && Math.abs(n) < 30 ? 0 : n, units[i][0]);
        }
      }
    } catch (e) { /* fall back below */ }
    return new Date(sec * 1000).toLocaleString();
  }
  function _date(sec) {
    try {
      return new Intl.DateTimeFormat(_lang(), { dateStyle: 'medium' }).format(new Date(sec * 1000));
    } catch (e) {
      return new Date(sec * 1000).toLocaleDateString();
    }
  }

  /* ── dialog ─────────────────────────────────────────────── */

  function _ensureDialog() {
    if (_dialog) return _dialog;
    _dialog = document.createElement('dialog');
    _dialog.className = 'modal-overlay';
    _dialog.id = 'remoteAccessDialog';
    _dialog.setAttribute('aria-labelledby', 'remoteAccessTitle');
    _dialog.addEventListener('click', function (ev) { if (ev.target === _dialog) _dialog.close(); });
    /* Remember where focus was — after the list is redrawn (refresh, disconnect) it goes back there,
       instead of dropping to body and losing keyboard users */
    _dialog.addEventListener('focusin', function (ev) {
      var row = ev.target.closest && ev.target.closest('.ra-row');
      _focusKey = row ? 'row:' + row.dataset.session : 'close';
    });
    document.body.appendChild(_dialog);
    return _dialog;
  }

  function _restoreFocus(d) {
    if (!d.open) return;
    var key = _focusKey || 'close';
    var target = null;
    if (key.indexOf('row:') === 0) {
      var id = key.slice(4);
      Array.prototype.forEach.call(d.querySelectorAll('.ra-row'), function (r) {
        if (r.dataset.session === id) target = r.querySelector('button');
      });
      if (!target) target = d.querySelector('.ra-row button');   // the disconnected row is gone — go to the next one
    }
    (target || d.querySelector('.modal-x')).focus();
  }

  function _render(sessions, error) {
    var d = _ensureDialog();
    d.textContent = '';
    var box = _el('div', 'modal ra-modal');
    var close = _el('button', 'modal-x');
    close.type = 'button';
    close.innerHTML = (typeof window.DXIcon === 'function') ? window.DXIcon('x') : '&times;';
    close.setAttribute('aria-label', _t('Close'));
    close.addEventListener('click', function () { d.close(); });
    box.appendChild(close);
    var h = _el('h2', null, _t('Connected browsers'));
    h.id = 'remoteAccessTitle';
    box.appendChild(h);

    var st = _status || {};
    if (st.local) {
      var addrs = st.addresses || [];
      if (addrs.length) {
        box.appendChild(_el('p', 'ra-lead', _t('Other computers on this network can open DX AI Studio at:')));
        var ul = _el('ul', 'ra-addrs');
        addrs.forEach(function (a) { ul.appendChild(_el('li', null, a)).classList.add('ra-addr'); });
        box.appendChild(ul);
      }
      box.appendChild(_el('p', 'ra-lead',
        _t('Each browser asks once for the 6-digit code shown in the terminal where ./launcher.sh is running.')));
    } else {
      box.appendChild(_el('p', 'ra-lead', _t('This browser is connected to DX AI Studio from another computer.')));
    }

    var list = _el('div', 'ra-list');
    list.setAttribute('role', 'list');
    if (error) {
      list.appendChild(_el('p', 'ra-empty ra-error', _t('Could not load the list. Try again.')));
    } else if (!sessions.length) {
      list.appendChild(_el('p', 'ra-empty', _t('No other computer is connected.')));
    }
    sessions.forEach(function (s) {
      var row = _el('div', 'ra-row');
      row.setAttribute('role', 'listitem');
      row.dataset.session = s.id;
      var info = _el('div', 'ra-info');
      var name = _el('div', 'ra-name', _device(s.user_agent));
      if (s.current) name.appendChild(_el('span', 'ra-tag', _t('This browser')));
      info.appendChild(name);
      var meta = [s.ip, _t('Last active {when}').replace('{when}', _ago(s.last_seen)),
                  _t('Paired {date}').replace('{date}', _date(s.created))].filter(Boolean);
      info.appendChild(_el('div', 'ra-meta', meta.join(' · ')));
      row.appendChild(info);
      var btn = _el('button', 'btn btn-sm ' + (s.current ? 'btn-ghost' : 'btn-danger'),
                    s.current ? _t('Disconnect this browser') : _t('Disconnect'));
      btn.type = 'button';
      btn.addEventListener('click', function () { _disconnect(s, btn); });
      row.appendChild(btn);
      list.appendChild(row);
    });
    box.appendChild(list);
    d.appendChild(box);
    _restoreFocus(d);
  }

  function _disconnect(s, btn) {
    btn.disabled = true;
    var req = s.current ? _post('/api/auth/logout') : _post('/api/auth/sessions/revoke', { id: s.id });
    req.then(function () {
      /* Disconnecting yourself ends access to this screen too — reload into the pairing page */
      if (s.current) { location.reload(); return; }
      _refresh();
    }).catch(function () { btn.disabled = false; _render([], true); });
  }

  function _refresh() {
    return _json('/api/auth/sessions')
      .then(function (d) { _render((d && d.sessions) || [], false); })
      .catch(function () { _render([], true); });
  }

  function open() {
    var d = _ensureDialog();
    _focusKey = 'close';
    _render([], false);
    if (!d.open) d.showModal();
    /* Re-read the addresses (board IPs) on every open — the network may have changed */
    return _json('/api/auth/status').then(function (st) { _status = st; }, function () {}).then(_refresh);
  }

  /* ── toolbar button ─────────────────────────────────────── */

  function _addButton() {
    var toolbar = document.getElementById('dxToolbar');
    if (!toolbar || document.getElementById('dxToolbarRemote')) return !!toolbar;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'dxToolbarRemote';
    btn.className = 'dx-toolbar-btn';
    btn.appendChild(window.DXIcon.el('users'));
    var label = function () {
      btn.title = _t('Connected browsers');
      btn.setAttribute('aria-label', btn.title);
    };
    label();
    if (window.DXI18n && window.DXI18n.onLangChange) {
      window.DXI18n.onLangChange(function () {
        label();
        if (_dialog && _dialog.open) _refresh();
      });
    }
    btn.addEventListener('click', open);
    var tut = document.getElementById('dxToolbarTutorial');
    toolbar.insertBefore(btn, tut && tut.parentNode === toolbar ? tut : null);
    return true;
  }

  function _init() {
    _json('/api/auth/status').then(function (st) {
      _status = st;
      if (!st || !st.pairing) return;
      /* toolbar.js builds #dxToolbar on DOMContentLoaded — if it is not there yet, try once more */
      if (!_addButton()) requestAnimationFrame(_addButton);
    }).catch(function () { /* no button when the status is unknown */ });
  }

  ns.remoteAccess = { open: open };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', _init);
  } else {
    _init();
  }
})();
