/* ─── Launcher home — the effects ───────────────────────────────────────

   Rule: move only transform and opacity. What JS animates goes through the Web
   Animations API — removing a class and re-adding it after a reflow forces layout
   on every keystroke. Nothing starts for people with reduced motion on (the CSS
   side is the global rule in dx-base.css).

   Static effects (stage lighting, book, poster pills) live in home-stage.css alone.
   Only what needs JS is here.
   Contract: tests/launcher/test_home_effects_contract.py, test_home_effects_browser.py */
(function () {
  'use strict';

  var EASE = 'cubic-bezier(.2, .8, .2, 1)';   // no overshoot

  function still() {
    try { return window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; }
  }

  /* #3 Input box — each keystroke swells the edge glow, which settles back to the focus
     brightness over 240ms. Resting and focus brightness come from CSS (.ask-box::after,
     :focus-within); this adds one ripple on top, and the CSS value returns when it ends. */
  function inputRipple() {
    var input = document.getElementById('homeAsk');
    var box = input && input.closest('.ask-box');
    if (!box || typeof box.animate !== 'function') return;
    var wave = null;
    input.addEventListener('input', function () {
      if (still()) return;
      if (wave) wave.cancel();
      var rest = parseFloat(getComputedStyle(box, '::after').opacity) || 0;
      wave = box.animate([{ opacity: 1 }, { opacity: rest }],
        { duration: 240, easing: EASE, pseudoElement: '::after' });
      wave.onfinish = function () { wave = null; };
    });
  }

  /* #4 Placeholder — cycles through proven requests and requests that go straight to a module
     (home-prompts.js DXHomePlaceholders): fully shown for 1.8s → erased at 20ms/char → the next
     line typed at 45ms/char. Focus stops and clears it (text should not move in front of someone
     typing); blur resumes. While it runs, data-i18n-placeholder is removed so i18n cannot restore
     the placeholder, and the language is followed here. */
  var TYPE_MS = 45, HOLD_MS = 1800, ERASE_MS = 20;

  function placeholderCycle() {
    var input = document.getElementById('homeAsk');
    var cycle = window.DXHomePlaceholders;
    if (!input || !cycle || !cycle.length || still()) return;
    input.removeAttribute('data-i18n-placeholder');

    var at = 0, chars = [], n = 0, phase = 'hold', timer = null;
    function say(i) {
      var key = cycle[i];
      return Array.from((window.DXI18n && window.DXI18n.T) ? window.DXI18n.T(key) : key);
    }
    function show() { input.placeholder = chars.slice(0, n).join(''); }
    function busy() { return document.activeElement === input || input.value !== ''; }
    function later(ms) { clearTimeout(timer); timer = setTimeout(step, ms); }

    function step() {
      if (document.hidden || busy()) return;
      if (phase === 'hold') { phase = 'erase'; return later(ERASE_MS); }
      if (phase === 'erase') {
        if (n > 0) { n -= 1; show(); return later(ERASE_MS); }
        at = (at + 1) % cycle.length;
        chars = say(at);
        phase = 'type';
        return later(TYPE_MS);
      }
      n += 1;
      show();
      if (n >= chars.length) { phase = 'hold'; return later(HOLD_MS); }
      later(TYPE_MS);
    }

    /* Restart with the current line fully shown. */
    function restart() {
      chars = say(at);
      n = chars.length;
      phase = 'hold';
      show();
      later(HOLD_MS);
    }

    input.addEventListener('focus', function () { clearTimeout(timer); input.placeholder = ''; });
    input.addEventListener('blur', function () { if (!busy()) restart(); });
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) clearTimeout(timer);
      else if (!busy()) later(phase === 'type' ? TYPE_MS : HOLD_MS);
    });
    if (window.DXI18n && window.DXI18n.onLangChange) {
      window.DXI18n.onLangChange(function () { if (!busy()) restart(); });
    }
    restart();
  }

  /* Effect tier. The cursor light passes under glass (backdrop-filter on the input and bar), so
     every move re-blurs the glass — cheap on a GPU, but with software raster (no acceleration,
     remote desktop, headless) frames stalled at 50-85ms, and 0 with the light off. On such
     machines only the cursor light is turned off. failIfMajorPerformanceCaveat withholds a
     context when WebGL is software-only, but SwiftShader on ANGLE passes (headless Chrome), so
     the renderer name is checked too. localStorage['dx-fx'] = 'full' | 'lite' forces a tier
     (tests, settings). */
  var SOFTWARE_GL = /swiftshader|llvmpipe|softpipe|software|basic render/i;
  var _lite = null;
  function lite() {
    if (_lite !== null) return _lite;
    var pick = null;
    try { pick = localStorage.getItem('dx-fx'); } catch (e) { /* noop */ }
    if (pick === 'full' || pick === 'lite') return (_lite = pick === 'lite');
    try {
      var c = document.createElement('canvas');
      var gl = c.getContext('webgl', { failIfMajorPerformanceCaveat: true });
      var info = gl && gl.getExtension('WEBGL_debug_renderer_info');
      var renderer = gl ? String(gl.getParameter(info ? info.UNMASKED_RENDERER_WEBGL : gl.RENDERER)) : '';
      _lite = !gl || SOFTWARE_GL.test(renderer);
      var lose = gl && gl.getExtension('WEBGL_lose_context');
      if (lose) lose.loseContext();   // release the context as soon as it has been measured
    } catch (e) {
      _lite = true;
    }
    return _lite;
  }

  /* #16 Cursor light — moves the light under the stage (.stage-light > i) to the cursor. Only a
     transform changes, once per frame (rAF). It turns on with the first move and off when the
     pointer leaves the window. Not used on the lite tier (above). */
  function cursorLight() {
    var wrap = document.querySelector('#landing .stage-light');
    var dot = wrap && wrap.firstElementChild;
    if (!dot || lite()) return;
    var x = 0, y = 0, queued = false, half = 0;

    function paint() {
      queued = false;
      if (!document.body.classList.contains('home-visible')) return;
      var r = wrap.getBoundingClientRect();
      if (!half) half = dot.getBoundingClientRect().width / 2;
      dot.style.transform = 'translate3d(' + (x - r.left - half) + 'px, ' + (y - r.top - half) + 'px, 0)';
      wrap.classList.add('is-on');   // turn on after it is in place, so it does not float in from the corner
    }
    document.addEventListener('pointermove', function (e) {
      if (e.pointerType === 'touch' || still()) return;
      x = e.clientX;
      y = e.clientY;
      if (!queued) { queued = true; requestAnimationFrame(paint); }
    }, { passive: true });
    document.addEventListener('pointerout', function (e) {
      if (!e.relatedTarget) wrap.classList.remove('is-on');
    });
  }

  /* ── Motion ─────────────────────────────────────────────────────────── */

  var STAGGER_MS = 60, ENTRY_MS = 500, TILE_STAGGER_MS = 16, SWEEP_MS = 900, FLY_MS = 600;
  var NEAR_PX = 120, MAX_SCALE = 1.18, PRESS_SCALE = .96;

  function lightLayer() { return document.querySelector('#landing .stage-light'); }

  /* The transform that puts the centre of light-layer element el at screen point (x, y). */
  function at(el, x, y) {
    var r = lightLayer().getBoundingClientRect();
    return 'translate3d(' + (x - r.left - el._dxW / 2) + 'px, ' + (y - r.top - el._dxH / 2) + 'px, 0)';
  }
  /* CSS fixes the size of light elements, so measure once. */
  function sized(el) {
    if (!el._dxW) {
      var b = el.getBoundingClientRect();
      el._dxW = b.width;
      el._dxH = b.height;
    }
    return el;
  }
  function centre(el) {
    var r = el.getBoundingClientRect();
    return [r.left + r.width / 2, r.top + r.height / 2];
  }

  /* #1 First entry — once per session. Elements rise in screen order (60ms apart, 16ms between
     tiles), a light sweeps left to right behind the title, then grazes the bar once. Starts when
     the shell is revealed (launcher-boot-pending removed and home visible), so it does not finish
     before the intro ends. */
  var ENTERED = 'dx-home-entered';

  function firstEntry() {
    try { if (sessionStorage.getItem(ENTERED)) return; } catch (e) { return; }
    function ready() {
      return !document.documentElement.classList.contains('launcher-boot-pending')
        && document.body.classList.contains('home-visible');
    }
    function play() {
      try { sessionStorage.setItem(ENTERED, '1'); } catch (e) { /* noop */ }
      if (still()) return;
      var order = ['#homeTour', '#homeStage .stage-title', '#homeStage .stage-sub', '#homeStage .stage-films',
        '#homeAskForm .ask-box', '#homeAskChips', '#homeDevice'];
      var delay = 0;
      function rise(el, d) {
        var a = el.animate([{ opacity: 0, transform: 'translateY(12px)' }, { opacity: 1, transform: 'none' }],
          { duration: ENTRY_MS, delay: d, easing: EASE, fill: 'backwards' });
        a.id = 'entry';
      }
      order.forEach(function (sel, i) {
        var el = document.querySelector(sel);
        delay = i * STAGGER_MS;
        if (el) rise(el, delay);
      });
      var tiles = document.querySelectorAll('#studioGrid > *');
      Array.prototype.forEach.call(tiles, function (el, j) { rise(el, (order.length) * STAGGER_MS + j * TILE_STAGGER_MS); });
      delay = order.length * STAGGER_MS + Math.max(0, tiles.length - 1) * TILE_STAGGER_MS;
      ['#homeMeasured', '#homeBar'].forEach(function (sel, i) {
        var el = document.querySelector(sel);
        if (el) rise(el, delay + (i + 1) * STAGGER_MS);
      });
      sweep();
    }
    if (ready()) { play(); return; }
    var watch = new MutationObserver(function () {
      if (!ready()) return;
      watch.disconnect();
      play();
    });
    watch.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
    watch.observe(document.body, { attributes: true, attributeFilter: ['class'] });
  }

  function sweep() {
    var band = document.querySelector('#landing .stage-sweep');
    var title = document.querySelector('#homeStage .stage-title');
    var bar = document.getElementById('homeBar');
    if (!band || !title) return;
    sized(band);
    var t = title.getBoundingClientRect();
    var ty = t.top + t.height / 2;
    var a = band.animate([
      { transform: at(band, t.left, ty), opacity: 0 },
      { opacity: 1, offset: .2 },
      { opacity: 1, offset: .75 },
      { transform: at(band, t.right, ty), opacity: 0 }
    ], { duration: SWEEP_MS, delay: 150, easing: EASE });
    a.id = 'sweep';
    if (!bar) return;
    var b = bar.getBoundingClientRect();
    var by = b.top + b.height / 2;
    var g = band.animate([
      { transform: at(band, b.left, by) + ' scaleY(.5)', opacity: 0 },
      { opacity: .7, offset: .3 },
      { transform: at(band, b.right, by) + ' scaleY(.5)', opacity: 0 }
    ], { duration: 500, delay: 150 + SWEEP_MS, easing: EASE });
    g.id = 'sweep';
  }

  /* #5 Send — a light drops from the input box onto the routed module icon, which lights up;
     several in order when there are several. Once render() opens the answer the stage becomes the
     Dock, so measure on the frame after that layout settles. */
  var TILE_OF = { monitor: 'dx_monitor' };

  function routedLight() {
    document.addEventListener('dx-home-routed', function (e) {
      if (still()) return;
      var routes = (e.detail || []).map(function (r) { return r && r.module; }).filter(Boolean);
      var seen = {};
      routes = routes.filter(function (m) { return seen[m] ? false : (seen[m] = true); });
      if (!routes.length) return;
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { fly(routes); });
      });
    });
  }

  function fly(modules) {
    var orb = document.querySelector('#landing .stage-orb');
    var box = document.querySelector('#homeAskForm .ask-box');
    if (!orb || !box) return;
    sized(orb);
    var from = centre(box);
    modules.forEach(function (m, i) {
      var tile = document.querySelector('.orbital-card[data-app="' + (TILE_OF[m] || m) + '"] .mod-tile');
      if (!tile) return;
      var to = centre(tile);
      var start = i * (FLY_MS + 120);
      var a = orb.animate([
        { transform: at(orb, from[0], from[1]) + ' scale(.6)', opacity: 0 },
        { opacity: 1, offset: .15 },
        { transform: at(orb, to[0], to[1]) + ' scale(1)', opacity: .9 }
      ], { duration: FLY_MS, delay: start, easing: EASE });
      a.id = 'orb';
      var lit = tile.animate([{ opacity: 0 }, { opacity: 1, offset: .3 }, { opacity: 0 }],
        { duration: 700, delay: start + FLY_MS - 60, easing: EASE, pseudoElement: '::after' });
      lit.id = 'lit';
    });
  }

  /* #6 Dock magnification — module icons within 120px of the cursor grow with proximity (up to
     1.18, .96 when pressed). The edge specular lights from the cursor side (CSS variables →
     ::before). All reads happen before all writes, so layout runs once per frame. */
  function dockMagnify() {
    var tiles = Array.prototype.slice.call(document.querySelectorAll('#studioGrid .orbital-card .mod-tile'));
    if (!tiles.length) return;
    var x = -1e4, y = -1e4, queued = false, pressed = null, dirty = false;

    function paint() {
      queued = false;
      var rects = tiles.map(function (t) { return t.getBoundingClientRect(); });
      var any = false;
      tiles.forEach(function (t, i) {
        var r = rects[i];
        var d = Math.sqrt(Math.pow(x - (r.left + r.width / 2), 2) + Math.pow(y - (r.top + r.height / 2), 2));
        var k = d < NEAR_PX ? Math.pow(1 - d / NEAR_PX, 2) : 0;
        var s = 1 + (MAX_SCALE - 1) * k;
        if (pressed === t) s *= PRESS_SCALE;
        if (k > 0 || pressed === t) any = true;
        t.style.transform = s === 1 ? '' : 'scale(' + s.toFixed(4) + ')';
        t.style.setProperty('--near', k.toFixed(3));
        if (k > 0) {
          t.style.setProperty('--sx', ((x - r.left) / r.width * 100).toFixed(1) + '%');
          t.style.setProperty('--sy', ((y - r.top) / r.height * 100).toFixed(1) + '%');
        }
      });
      dirty = any;
    }
    function ask() { if (!queued) { queued = true; requestAnimationFrame(paint); } }

    document.addEventListener('pointermove', function (e) {
      if (e.pointerType === 'touch' || still()) return;
      if (!document.body.classList.contains('home-visible')) return;
      x = e.clientX;
      y = e.clientY;
      ask();
    }, { passive: true });
    document.addEventListener('pointerdown', function (e) {
      if (still()) return;
      var card = e.target.closest && e.target.closest('#studioGrid .orbital-card');
      pressed = card ? card.querySelector('.mod-tile') : null;
      if (pressed) ask();
    });
    ['pointerup', 'pointercancel'].forEach(function (ev) {
      document.addEventListener(ev, function () { if (pressed) { pressed = null; ask(); } });
    });
    document.addEventListener('pointerout', function (e) {
      if (!e.relatedTarget && dirty) { x = y = -1e4; ask(); }
    });
  }

  function init() {
    inputRipple();
    placeholderCycle();
    cursorLight();
    firstEntry();
    routedLight();
    dockMagnify();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
