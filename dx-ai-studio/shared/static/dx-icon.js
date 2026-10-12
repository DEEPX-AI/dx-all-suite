/* ─── DX AI Studio — icon helper ───────────────────────────────────────────

   The studio's icons are one set: shared/static/dx-icons.svg. Use this to insert SVG icons instead of
   emoji in textContent — the colour is currentColor, so it follows text colour, theme and state.

     DXIcon('check')                       → '<svg class="dx-ico" aria-hidden="true">…</svg>' (string)
     DXIcon('alert', { label: 'Warning' }) → a meaningful icon: role="img" + aria-label
     DXIcon.el('globe', { cls: 'dx-ico--lg' }) → element

   Decorative icons (with text of the same meaning beside them) get no label — screen readers would read it twice.
   Contract: tests/shared/test_icon_system.py */
(function () {
  'use strict';

  var NS = 'http://www.w3.org/2000/svg';

  /* Sprite URL — the server writes a content-hashed URL into <meta name="dx-icons"> (dx_server
     _render_sprite_refs). Hashed URLs are cached as immutable, so revisits cost no round trip. <use> and load()
     must use the same URL to share one cache entry. Documents without the meta (static previews etc.) use the
     unhashed path. */
  var _sprite = null;
  function _spriteUrl() {
    if (_sprite) return _sprite;
    var meta = document.querySelector('meta[name="dx-icons"]');
    _sprite = (meta && meta.getAttribute('content')) || '/static/shared/dx-icons.svg';
    return _sprite;
  }

  function _esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function DXIcon(name, opts) {
    opts = opts || {};
    var cls = 'dx-ico' + (opts.cls ? ' ' + opts.cls : '');
    var a11y = opts.label
      ? ' role="img" aria-label="' + _esc(opts.label) + '"'
      : ' aria-hidden="true" focusable="false"';
    return '<svg class="' + _esc(cls) + '"' + a11y + '><use href="' + _esc(DXIcon.url(name)) + '"></use></svg>';
  }

  /* The <use href> value — code that builds <svg> by hand (dx-tabs etc.) uses this too */
  DXIcon.url = function (name) {
    return _spriteUrl() + '#' + name;
  };

  DXIcon.el = function (name, opts) {
    opts = opts || {};
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('class', 'dx-ico' + (opts.cls ? ' ' + opts.cls : ''));
    if (opts.label) {
      svg.setAttribute('role', 'img');
      svg.setAttribute('aria-label', opts.label);
    } else {
      svg.setAttribute('aria-hidden', 'true');
      svg.setAttribute('focusable', 'false');
    }
    var use = document.createElementNS(NS, 'use');
    use.setAttribute('href', DXIcon.url(name));
    svg.appendChild(use);
    return svg;
  };

  /* Icon + text in one call.
     Text goes in as a text node (translations and server messages are never parsed as HTML).
       DXIcon.label(btn, 'check', T('Use This Config'))
       DXIcon.label(h3, 'spinner', T('Compiling...'), { cls: 'dx-ico--spin' }) */
  DXIcon.label = function (el, name, text, opts) {
    if (!el) return el;
    el.textContent = '';
    if (name) {
      el.appendChild(DXIcon.el(name, opts));
      el.appendChild(document.createTextNode(' '));
    }
    el.appendChild(document.createTextNode(text == null ? '' : String(text)));
    return el;
  };

  /* Draw on a canvas — for places <use> cannot reach (pipeline nodes etc.).
     The sprite is read once and each symbol turned into a Path2D. If it is not loaded yet, this returns false and
     starts loading — when done, 'dx-icons-ready' fires on window (the caller redraws).
       DXIcon.draw(ctx, 'play', x, y, 16, color)  // x, y is the top-left corner, color is a CSS colour */
  var _shapes = null, _loading = null;
  function _toPath(node) {
    var tag = node.tagName.toLowerCase(), p = new Path2D();
    if (tag === 'path') p = new Path2D(node.getAttribute('d') || '');
    else if (tag === 'circle') {
      var cx = +node.getAttribute('cx'), cy = +node.getAttribute('cy'), r = +node.getAttribute('r');
      p.arc(cx, cy, r, 0, Math.PI * 2);
    } else if (tag === 'rect') {
      var x = +node.getAttribute('x'), y = +node.getAttribute('y'), w = +node.getAttribute('width'),
          h = +node.getAttribute('height'), rx = +(node.getAttribute('rx') || 0);
      if (p.roundRect) p.roundRect(x, y, w, h, rx); else p.rect(x, y, w, h);
    } else return null;
    var t = node.getAttribute('transform');
    if (t && typeof DOMMatrix === 'function') {
      var out = new Path2D();
      out.addPath(p, new DOMMatrix(t.replace(/scale\(([^)]+)\)/, function (m, a) { return 'scale(' + a.trim().replace(/\s+/g, ',') + ')'; })
        .replace(/translate\(([^)]+)\)/, function (m, a) { return 'translate(' + a.trim().replace(/\s+/g, 'px,') + 'px)'; })));
      return out;
    }
    return p;
  }
  DXIcon.load = function () {
    if (_loading) return _loading;
    _loading = fetch(_spriteUrl()).then(function (r) { return r.text(); }).then(function (text) {
      var doc = new DOMParser().parseFromString(text, 'image/svg+xml'), map = {};
      Array.prototype.forEach.call(doc.querySelectorAll('symbol'), function (sym) {
        var one = { fill: [], line: [] };
        ['f', 'l'].forEach(function (cls) {
          var g = sym.querySelector('g.' + cls);
          if (!g) return;
          Array.prototype.forEach.call(g.children, function (n) {
            var path = _toPath(n);
            if (path) one[cls === 'f' ? 'fill' : 'line'].push(path);
          });
        });
        map[sym.id] = one;
      });
      _shapes = map;
      try { window.dispatchEvent(new Event('dx-icons-ready')); } catch (e) {}
      return map;
    }).catch(function () { _loading = null; return null; });
    return _loading;
  };
  DXIcon.draw = function (ctx, name, x, y, size, color) {
    if (!_shapes) { DXIcon.load(); return false; }
    var shape = _shapes[name];
    if (!shape) return false;
    ctx.save();
    ctx.translate(x, y);
    ctx.scale(size / 24, size / 24);
    ctx.fillStyle = color; ctx.strokeStyle = color;
    var a = ctx.globalAlpha;
    ctx.globalAlpha = a * 0.24;
    shape.fill.forEach(function (p) { ctx.fill(p); });
    ctx.globalAlpha = a;
    ctx.lineWidth = 2; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    shape.line.forEach(function (p) { ctx.stroke(p); });
    ctx.restore();
    return true;
  };

  window.DXIcon = DXIcon;
})();
