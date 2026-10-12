/* ─── intro · Compiler scene — hundreds of nodes become one chip ──────────────

   The real ONNX graph of Ultralytics YOLO26n (384 nodes, 526 edges) lights up left to right, then a
   compile wave pulls the nodes into the center, where they become DX-M1. A glint crosses the chip once.
   scripts/intro/bake_compile.py bakes the graph (layout computed, edges unchanged).

   Stream moves "out", App moves "across", this one moves "in". 384 dots move independently, so the
   graph is drawn on one canvas with rAF — under 1 ms per frame, and drawing stops once all are absorbed.
   The chip is a static SVG animated with transform/opacity only. */
(function () {
  'use strict';

  var SRC = '/static/img/intro/compile/graph.json';
  var LIGHT = 900;        // time for the graph to light up left → right
  var PULL_AT = 1000;     // when the wave starts
  var PULL_SPREAD = 520;  // left nodes first — start delayed by x position
  var PULL_MS = 760;      // travel time of one node to the chip
  var FORGE_AT = 1650;    // the chip appears
  var LIT_AT = 2300;      // the glint crosses the chip
  var CHIP = { x: 800, y: 470, s: 300 };   // stage coordinates (1600×1000) — the prompt sits below

  var _data = null, _ready = false, _started = false, _root = null, _timers = [], _raf = 0;

  function _later(fn, ms) { _timers.push(setTimeout(fn, ms)); }

  function prepare() {
    if (_started) return;
    _started = true;
    fetch(SRC).then(function (r) { if (!r.ok) throw r; return r.json(); })
      .then(function (d) { _data = d; _ready = true; }, function () { _ready = false; });
  }

  /* DX-M1 — package, die, three NPU cores, edge pins. Colors come from CSS (.icp-*). */
  function _chipSvg() {
    var pins = '';
    for (var i = 0; i < 9; i++) {
      var p = 34 + i * 16;
      pins += '<rect class="icp-pin" x="' + p + '" y="4" width="6" height="12" rx="1.5"/>' +
              '<rect class="icp-pin" x="' + p + '" y="184" width="6" height="12" rx="1.5"/>' +
              '<rect class="icp-pin" x="4" y="' + p + '" width="12" height="6" rx="1.5"/>' +
              '<rect class="icp-pin" x="184" y="' + p + '" width="12" height="6" rx="1.5"/>';
    }
    return '<svg viewBox="0 0 200 200" aria-hidden="true">' + pins +
      '<rect class="icp-package" x="16" y="16" width="168" height="168" rx="14"/>' +
      '<rect class="icp-die" x="40" y="40" width="120" height="120" rx="6"/>' +
      '<rect class="icp-core" x="50" y="50" width="30" height="62" rx="3"/>' +
      '<rect class="icp-core" x="85" y="50" width="30" height="62" rx="3"/>' +
      '<rect class="icp-core" x="120" y="50" width="30" height="62" rx="3"/>' +
      '<rect class="icp-mem" x="50" y="120" width="100" height="10" rx="2"/>' +
      '<rect class="icp-mem" x="50" y="136" width="64" height="14" rx="2"/>' +
      '<rect class="icp-mem" x="120" y="136" width="30" height="14" rx="2"/>' +
      '<text class="icp-name" x="100" y="176" text-anchor="middle">DX-M1</text>' +
      '</svg>';
  }

  function _ease(t) { return t <= 0 ? 0 : t >= 1 ? 1 : t * t * (3 - 2 * t); }
  function _in(t) { return t <= 0 ? 0 : t >= 1 ? 1 : t * t * t; }   // accelerate toward the end when absorbed

  function _draw(canvas, t0) {
    var ctx = canvas.getContext('2d');
    var nodes = _data.nodes, edges = _data.edges, W = _data.stage[0];
    var k = canvas.width / W;
    var n = nodes.length, px = new Float32Array(n), py = new Float32Array(n), a = new Float32Array(n);
    var accent = getComputedStyle(canvas).getPropertyValue('--icp-node').trim() || 'white';   // colors live in style.css
    function frame(now) {
      var t = now - t0, done = true;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (var i = 0; i < n; i++) {
        var x = nodes[i][0], y = nodes[i][1];
        var lit = _ease((t - (x / W) * (LIGHT - 200)) / 200);
        var go = _in((t - PULL_AT - (x / W) * PULL_SPREAD) / PULL_MS);
        if (go < 1) done = false;
        px[i] = (x + (CHIP.x - x) * go) * k;
        py[i] = (y + (CHIP.y - y) * go) * k;
        a[i] = lit * (1 - go);
      }
      /* 'lighter' — overlaps get brighter. Each dot gets a faint halo drawn once more to glow
         (shadowBlur runs a blur per dot and is slow). */
      ctx.globalCompositeOperation = 'lighter';
      ctx.lineWidth = Math.max(1, k);
      ctx.strokeStyle = accent;
      for (var e = 0; e < edges.length; e++) {
        var s = edges[e][0], d = edges[e][1], ea = Math.min(a[s], a[d]) * 0.4;
        if (ea < 0.01) continue;
        ctx.globalAlpha = ea;
        ctx.beginPath(); ctx.moveTo(px[s], py[s]); ctx.lineTo(px[d], py[d]); ctx.stroke();
      }
      ctx.fillStyle = accent;
      for (var j = 0; j < n; j++) {
        if (a[j] < 0.01) continue;
        var conv = nodes[j][2] === 'conv', r = (conv ? 4.2 : 2) * k;
        ctx.globalAlpha = a[j] * 0.16;
        ctx.beginPath(); ctx.arc(px[j], py[j], r * 2.8, 0, 6.2832); ctx.fill();
        ctx.globalAlpha = a[j] * (conv ? 1 : 0.75);
        ctx.beginPath(); ctx.arc(px[j], py[j], r, 0, 6.2832); ctx.fill();
      }
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = 'source-over';
      if (!done || t < PULL_AT) _raf = requestAnimationFrame(frame);
      else ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    _raf = requestAnimationFrame(frame);
  }

  function _build(overlay) {
    var root = document.createElement('div');
    root.className = 'intro-compile';
    root.setAttribute('aria-hidden', 'true');
    root.innerHTML =
      '<div class="ist-stage">' +
        '<canvas class="icp-graph"></canvas>' +
        '<div class="icp-chip">' + _chipSvg() + '<div class="icp-sweep"></div></div>' +
      '</div>' +
      '<div class="ist-shade"></div>';
    var S = _data.stage, chip = root.querySelector('.icp-chip');
    chip.style.left = ((CHIP.x - CHIP.s / 2) / S[0] * 100) + '%';
    chip.style.top = ((CHIP.y - CHIP.s / 2) / S[1] * 100) + '%';
    chip.style.width = (CHIP.s / S[0] * 100) + '%';
    chip.style.height = (CHIP.s / S[1] * 100) + '%';
    overlay.insertBefore(root, overlay.firstChild);
    var canvas = root.querySelector('canvas');
    canvas.dataset.nodes = String(_data.nodes.length);
    var box = root.querySelector('.ist-stage').getBoundingClientRect();
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(box.width * dpr);
    canvas.height = Math.round(box.height * dpr);
    return root;
  }

  /* Called when the beat starts. Returns false if not ready — the beat then runs on the prompt alone. */
  function play(overlay, beatMs) {
    if (!_ready || !overlay) return false;
    stop();
    var root = _root = _build(overlay);
    requestAnimationFrame(function (now) {
      if (_root !== root) return;
      root.classList.add('is-on');
      _draw(root.querySelector('canvas'), now);
    });
    _later(function () { root.classList.add('is-forged'); }, FORGE_AT);
    _later(function () { root.classList.add('is-lit'); }, LIT_AT);
    _later(function () { root.classList.add('is-out'); }, beatMs - 250);
    _later(stop, beatMs + 400);
    return true;
  }

  function stop() {
    _timers.forEach(clearTimeout);
    _timers.length = 0;
    if (_raf) { cancelAnimationFrame(_raf); _raf = 0; }
    if (_root && _root.parentNode) _root.parentNode.removeChild(_root);
    _root = null;
  }

  window.DXIntroCompile = { prepare: prepare, play: play, stop: stop };
})();
