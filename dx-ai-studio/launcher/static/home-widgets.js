/* ─── Launcher home — the two widgets beside the grid ─────────────────────

   Left: what is true right now (this PC's DX-M1). Right: what was measured on that device.

   This file alone owns the device values. startSharedHwStream already broadcasts the device over
   SSE (or a 3 s poll), so a second poller would overwrite the same slots in turn. The stream
   starts once the studio is ready; before that, hw_status is read once.

   Count-up lives here (_countTo); bar transitions and the pulse are CSS (is-idle).
   Contract: tests/launcher/test_home_widgets_contract.py, test_home_widgets_browser.py */
(function () {
  'use strict';

  var ns = window.DXLauncher = window.DXLauncher || {};

  function $(id) { return document.getElementById(id); }
  function _t(key) {
    return (window.DXI18n && window.DXI18n.T) ? window.DXI18n.T(key) : key;
  }
  function _fmt(n) {
    return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
  function _open(app) {
    if (ns.launch) ns.launch(app);
  }
  function _bindOpen(el, app) {
    if (!el) return;
    el.addEventListener('click', function (e) { e.preventDefault(); _open(app); });
    el.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); _open(app); }
    });
  }

  /* ── Status: DX-M1 ─────────────────────────────────────────── */

  var _hw = null;

  function _line(npu) {
    var parts = [];
    var temps = npu.temperatures || [];
    var temp = typeof npu.temp_avg === 'number' ? npu.temp_avg
      : (temps.length ? Math.max.apply(null, temps) : null);
    if (typeof temp === 'number') parts.push(Math.round(temp) + '°C');
    if (typeof npu.clock_avg === 'number') parts.push(_fmt(npu.clock_avg) + ' MHz');
    if (typeof npu.power_est_mW === 'number') parts.push(_fmt(npu.power_est_mW) + ' mW');
    return parts.join(' · ');
  }

  function _paintCores(box, npu) {
    var n = (npu && npu.cores) || 0;
    var util = (npu && npu.utilization) || [];
    if (box.children.length !== n) {
      box.innerHTML = '';
      for (var i = 0; i < n; i++) {
        var core = document.createElement('span');
        core.className = 'dev-core';
        core.appendChild(document.createElement('i'));
        var label = document.createElement('b');
        label.textContent = String(i);
        core.appendChild(label);
        box.appendChild(core);
      }
    }
    for (var j = 0; j < n; j++) {
      var u = Math.max(0, Math.min(100, Number(util[j]) || 0));
      box.children[j].style.setProperty('--u', String(u));
    }
  }

  function paintDevice(hw) {
    _hw = hw;
    var box = $('homeDevice');
    var chip = $('heroDeviceChip');
    var cores = $('homeCores');
    var line = $('homeDeviceLine');
    if (!box || !chip || !cores || !line) return;
    chip.removeAttribute('data-i18n');   // live values are not dictionary keys

    var npu = hw && hw.npus && hw.npus[0];
    var live = !!(hw && hw.available && hw.count > 0 && npu);
    var mock = !!(hw && hw.mock && npu);
    /* Absent is shown by dimming, not by shouting in color. */
    box.classList.toggle('is-off', !live && !mock);
    /* All cores under 5% means idle — the bars breathe every 4 s (CSS). */
    var util = (npu && npu.utilization) || [];
    box.classList.toggle('is-idle', (live || mock) && Math.max.apply(null, util.concat([0])) < 5);

    if (live || mock) {
      chip.className = 'ws-device' + (live ? ' is-live' : '');
      chip.textContent = mock ? _t('Mock data') : '';
      chip.hidden = !mock;
      _paintCores(cores, npu);
      line.textContent = _line(npu);
    } else {
      chip.className = 'ws-device is-missing';
      chip.textContent = _t('No DX-M1 connected');
      chip.hidden = false;
      cores.innerHTML = '';
      line.textContent = '';
    }
  }

  /* ── Evidence: measured on this device ─────────────────────── */

  /* One model per task, at the size people actually run (nano). Picking the fastest would mix tasks
     into numbers that cannot be compared — classification's 3,695 next to detection's 1,847 says
     nothing. Listed by id rather than guessed from name patterns, so what gets picked is readable here. */
  var HEADLINE = [
    ['object_detection', 'yolo26n'],
    ['instance_segmentation', 'yolo26n_seg'],
    ['pose_estimation', 'yolo26n_pose'],
    ['classification', 'yolo26n_cls'],
    ['obb_detection', 'yolo26n_obb'],
    ['depth_estimation', 'yolo26_depth_n'],
  ];
  /* Same keys as the Model Zoo dictionary (i18n-dict-shared.js), so terms stay the same across modules. */
  var TASK_LABEL = {
    object_detection: 'Object Detection',
    instance_segmentation: 'Instance Segmentation',
    pose_estimation: 'Pose Estimation',
    classification: 'Classification',
    obb_detection: 'OBB Detection',
    depth_estimation: 'Depth Estimation',
  };
  var ROTATE_MS = 5000;

  var _rows = [];
  var _at = 0;
  var _timer = null;
  var _held = false;

  function pickHeadline(models) {
    var byId = {};
    (models || []).forEach(function (m) { if (m && m.id) byId[m.id] = m; });
    return HEADLINE.map(function (pair) {
      var m = byId[pair[1]];
      var fps = m && m.performance && m.performance.fps;
      return fps ? { task: pair[0], fps: fps } : null;
    }).filter(Boolean);
  }

  function _paintDots(host) {
    if (host.children.length !== _rows.length) {
      host.innerHTML = '';
      _rows.forEach(function (row, i) {
        var dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'proof-dot';
        dot.setAttribute('aria-label', _t(TASK_LABEL[row.task]));
        dot.addEventListener('click', function (e) { e.stopPropagation(); _at = i; paintProof(); });
        host.appendChild(dot);
      });
    }
    Array.prototype.forEach.call(host.children, function (dot, i) {
      dot.classList.toggle('is-on', i === _at);
    });
  }

  /* Numbers count from the shown value to the new one over 700 ms. Instant under reduced motion
     or in a hidden tab. */
  var COUNT_MS = 700;
  var _shownFps = 0;
  var _countRaf = 0;

  function _countTo(el, to) {
    cancelAnimationFrame(_countRaf);
    var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (still || document.hidden || _shownFps === to) {
      _shownFps = to;
      el.textContent = _fmt(to);
      return;
    }
    var from = _shownFps;
    var t0 = null;
    function step(t) {
      if (t0 === null) t0 = t;
      var k = Math.min(1, (t - t0) / COUNT_MS);
      _shownFps = from + (to - from) * (1 - Math.pow(1 - k, 3));
      if (k === 1) _shownFps = to;
      el.textContent = _fmt(_shownFps);
      if (k < 1) _countRaf = requestAnimationFrame(step);
    }
    _countRaf = requestAnimationFrame(step);
  }

  function paintProof() {
    var body = $('homeProof');
    if (!body) return;
    if (!_rows.length) { body.hidden = true; return; }
    var row = _rows[_at % _rows.length];
    _countTo($('homeProofFps'), row.fps);
    $('homeProofModel').textContent = 'YOLO26n · ' + _t(TASK_LABEL[row.task]);
    _paintDots($('homeProofDots'));
    body.hidden = false;
  }

  function rotate() {
    if (!_rows.length) return;
    _at = (_at + 1) % _rows.length;
    paintProof();
  }

  /* Auto-advancing is motion too: under reduced motion it stays on the first task and the dots
     pick. It does not advance while hovered or while the tab is hidden. */
  function _startRotation() {
    if (_timer || _rows.length < 2) return;
    var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (still) return;
    _timer = setInterval(function () {
      if (!_held && !document.hidden) rotate();
    }, ROTATE_MS);
  }

  function takeCatalogue(models) {
    _rows = pickHeadline(models);
    _at = 0;
    paintProof();
    _startRotation();
  }

  /* ── wiring ────────────────────────────────────────────── */

  function init() {
    _bindOpen($('homeDevice'), 'dx_monitor');
    var count = $('measuredCount');
    if (count) {
      count.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); _open('benchmark'); });
    }
    var proof = $('homeMeasured');
    if (proof) {
      ['mouseenter', 'focusin'].forEach(function (ev) { proof.addEventListener(ev, function () { _held = true; }); });
      ['mouseleave', 'focusout'].forEach(function (ev) { proof.addEventListener(ev, function () { _held = false; }); });
    }

    window.addEventListener('message', function (e) {
      if (e.data && e.data.type === 'dx-hw-data') paintDevice(e.data.payload);
    });
    fetch('/dx_monitor/api/hw_status', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (hw) { if (_hw === null) paintDevice(hw); })
      .catch(function () { if (_hw === null) paintDevice(null); });

    document.addEventListener('dx-home-catalog', function (e) { takeCatalogue(e.detail); });
    if (ns._homeCatalog) takeCatalogue(ns._homeCatalog);

    if (window.DXI18n && window.DXI18n.onLangChange) {
      window.DXI18n.onLangChange(function () {
        if (_hw !== null) paintDevice(_hw);
        var dots = $('homeProofDots');
        if (dots) dots.innerHTML = '';   // dot labels follow the language too
        paintProof();
      });
    }
  }

  ns._pickHeadline = pickHeadline;   // lets tests check the pick rule directly
  ns._rotateHeadline = rotate;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
