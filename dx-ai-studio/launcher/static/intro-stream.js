/* ─── intro · Stream scene — 16-channel pull-back ─────────────────────────────

   One intersection channel fills the screen and its boxes appear. The camera pulls back once, the
   view becomes its own cell in a 4×4 wall, and its colors shift to the wall's grade. Then the boxes
   of the other 15 cells appear in a diagonal wave.

   Images and boxes are real: frames of DEEPX's official sample video run through the official Model Zoo
   yolov5-s 320 on DX-M1 (scripts/intro/bake_stream.py). Images are baked; boxes are kept as coordinates
   and drawn here.

   There is one coordinate system — a 16:10 stage (1600×1000) covers the screen, and the wall, boxes and
   start view all live in it. So the pull-back lands exactly in its cell with a single transform on the
   start view. Only transform and opacity animate. */
(function () {
  'use strict';

  var BASE = '/static/img/intro/stream/';
  var PULL_AT = 900;      // after the boxes appear on the start view
  var RIPPLE_AT = 1800;   // when the pull-back ends
  var STEP_TILE = 70;     // per diagonal step
  var STEP_BOX = 18;      // per box within a cell
  var LABELS = 4;         // number of large boxes labelled on the start view

  var _data = null, _ready = false, _root = null, _timers = [];

  function _later(fn, ms) { _timers.push(setTimeout(fn, ms)); }

  function _img(src) {
    return new Promise(function (resolve, reject) {
      var im = new Image();
      im.onload = function () {
        (im.decode ? im.decode() : Promise.resolve()).then(function () { resolve(im); }, function () { resolve(im); });
      };
      im.onerror = reject;
      im.src = src;
    });
  }

  /* Called when the intro starts — preloads during the ~3 s before the beat. If loading fails, the beat shows the prompt only. */
  function prepare() {
    if (_ready || _data) return;
    _data = {};
    Promise.all([
      fetch(BASE + 'detections.json').then(function (r) { if (!r.ok) throw r; return r.json(); }),
      _img(BASE + 'wall.webp'),
      _img(BASE + 'hero.webp'),
    ]).then(function (got) { _data = got[0]; _ready = true; }, function () { _ready = false; });
  }

  function _tileRect(i) {
    var d = _data, cols = d.cols, gap = d.gap;
    var tw = (d.stage[0] - gap * (cols - 1)) / cols, th = (d.stage[1] - gap * (d.rows - 1)) / d.rows;
    var r = Math.floor(i / cols), c = i % cols;
    return { x: c * (tw + gap), y: r * (th + gap), w: tw, h: th, r: r, c: c };
  }

  /* One box = one HTML element, its four corners drawn with CSS gradients (style.css .ist-b).
     In SVG, path transform/opacity cannot reach the compositor, so the whole stage repaints every frame
     during the wave. As elements, each box is its own layer and moves without repainting.
     Coordinates are % of the stage — the same spot whatever size the stage covers. Corner length is 25%
     of a side (at least 6 units), passed as separate horizontal and vertical %. */
  function _box(parent, rect, box, delay, extra) {
    var b = box.b, S = _data.stage;
    var x0 = rect.x + b[0] * rect.w, y0 = rect.y + b[1] * rect.h;
    var w = (b[2] - b[0]) * rect.w, h = (b[3] - b[1]) * rect.h;
    var l = Math.max(6, Math.min(w, h) * 0.25);
    var el = document.createElement('i');
    el.className = extra ? 'ist-b ' + extra : 'ist-b';
    el.style.cssText = 'left:' + (x0 / S[0] * 100) + '%;top:' + (y0 / S[1] * 100) + '%;width:' +
      (w / S[0] * 100) + '%;height:' + (h / S[1] * 100) + '%';
    el.style.setProperty('--lx', (l / w * 100) + '%');
    el.style.setProperty('--ly', (l / h * 100) + '%');
    el.style.setProperty('--d', delay + 'ms');
    parent.appendChild(el);
  }

  function _layer(cls) {
    var el = document.createElement('div');
    el.className = cls;
    return el;
  }

  function _build(overlay) {
    var d = _data, heroI = d.hero, hero = _tileRect(heroI), full = { x: 0, y: 0, w: d.stage[0], h: d.stage[1] };
    var root = document.createElement('div');
    root.className = 'intro-stream';
    root.setAttribute('aria-hidden', 'true');
    root.innerHTML =
      '<div class="ist-stage"><div class="ist-drift">' +
        '<div class="ist-wall"></div>' +
        '<div class="ist-slot"></div>' +
        '<div class="ist-hero"><div class="ist-hero-photo"></div><div class="ist-labels"></div></div>' +
        '<div class="ist-scan"></div>' +
      '</div></div>' +
      '<div class="ist-shade"></div>';
    var drift = root.querySelector('.ist-drift');
    /* the same URL prepare() preloaded — paints straight from cache */
    root.querySelector('.ist-wall').style.backgroundImage = 'url(' + BASE + 'wall.webp)';
    root.querySelector('.ist-hero-photo').style.backgroundImage = 'url(' + BASE + 'hero.webp)';
    var wall = _layer('ist-boxes');
    drift.insertBefore(wall, root.querySelector('.ist-slot'));

    /* Boxes for all 16 cells — the other 15 in the diagonal wave, the start view's cell when the pull-back
       ends (its large boxes fade as they shrink and right-sized boxes take over, so line widths never shrink) */
    d.tiles.forEach(function (tile, i) {
      var rect = _tileRect(i);
      tile.boxes.forEach(function (box, k) {
        if (i === heroI) _box(wall, rect, box, 0, 'is-hero');
        else _box(wall, rect, box, (rect.r + rect.c) * STEP_TILE + k * STEP_BOX);
      });
    });

    /* Start view — drawn over the whole stage, then settles into its cell with a transform */
    var heroEl = root.querySelector('.ist-hero');
    var heroBoxes = _layer('ist-hero-boxes');
    heroEl.appendChild(heroBoxes);
    var byArea = d.tiles[heroI].boxes.slice().sort(function (a, b) {
      return (b.b[2] - b.b[0]) * (b.b[3] - b.b[1]) - (a.b[2] - a.b[0]) * (a.b[3] - a.b[1]);
    });
    /* Class names on a few large boxes — exactly as the model output them (never edited) */
    var labels = root.querySelector('.ist-labels');
    byArea.forEach(function (box, k) {
      _box(heroBoxes, full, box, 120 + k * 40);
      if (k < LABELS) {
        var tag = document.createElement('span');
        tag.className = 'ist-label';
        tag.textContent = box.c;
        tag.style.left = (box.b[0] * 100) + '%';
        tag.style.top = (box.b[1] * 100) + '%';
        tag.style.setProperty('--d', (260 + k * 40) + 'ms');
        labels.appendChild(tag);
      }
    });
    var style = root.style;
    style.setProperty('--hx', (hero.x / d.stage[0] * 100) + '%');
    style.setProperty('--hy', (hero.y / d.stage[1] * 100) + '%');
    style.setProperty('--hsx', String(hero.w / d.stage[0]));
    style.setProperty('--hsy', String(hero.h / d.stage[1]));
    overlay.insertBefore(root, overlay.firstChild);
    return root;
  }

  /* Called when the beat starts. Returns false if not ready — the beat then runs on the prompt alone. */
  function play(overlay, beatMs) {
    if (!_ready || !overlay) return false;
    stop();
    _root = _build(overlay);
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { if (_root) _root.classList.add('is-on'); });
    });
    _later(function () { if (_root) _root.classList.add('is-pulled'); }, PULL_AT);
    _later(function () { if (_root) _root.classList.add('is-rippled'); }, RIPPLE_AT);
    _later(function () { if (_root) _root.classList.add('is-out'); }, beatMs - 250);
    _later(stop, beatMs + 400);
    return true;
  }

  function stop() {
    _timers.forEach(clearTimeout);
    _timers.length = 0;
    if (_root && _root.parentNode) _root.parentNode.removeChild(_root);
    _root = null;
  }

  window.DXIntroStream = { prepare: prepare, play: play, stop: stop };
})();
