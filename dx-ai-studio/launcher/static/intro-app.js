/* ─── intro · App scene — a line of light leaves segmentation behind ─────────

   The first frame of a real driving video. A thin line of light sweeps top to bottom, and what it
   passes turns into the real segmentation DX-M1 produced. Once fully revealed it plays on — the mask
   follows the moving cars (a video file). scripts/intro/bake_app.py bakes the images and the clip.

   Stream moves "out" (pull-back), so this one moves "across"; the camera creeps slightly forward in
   the driving direction. The stage (.ist-stage) and edge shade (.ist-shade) are shared with Stream.

   The reveal runs on the compositor only: the frame around the mask layer slides down (translateY
   -100% → 0) while its inside moves the other way (100% → 0), so the image stays put — the frame's
   bottom edge is the line of light. Animating clip-path would repaint every frame. */
(function () {
  'use strict';

  var BASE = '/static/img/intro/app/';
  var REVEAL_AT = 300;
  var PLAY_AT = 1450;     // after the reveal (1.1 s) ends

  var _ready = false, _started = false, _root = null, _timers = [];

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

  /* Wait for the two images only — the clip plays if ready by then, otherwise the still mask image stays. */
  function prepare() {
    if (_started) return;
    _started = true;
    Promise.all([_img(BASE + 'first.webp'), _img(BASE + 'seg-first.webp')])
      .then(function () { _ready = true; }, function () { _ready = false; });
  }

  function _build(overlay) {
    var root = document.createElement('div');
    root.className = 'intro-app';
    root.setAttribute('aria-hidden', 'true');
    root.innerHTML =
      '<div class="ist-stage"><div class="iap-drift">' +
        '<div class="iap-photo"></div>' +
        '<div class="iap-reveal"><div class="iap-reveal-in"><div class="iap-seg">' +
          '<video class="iap-video" muted playsinline preload="auto"></video>' +
        '</div></div></div>' +
        '<div class="iap-line"></div>' +
      '</div></div>' +
      '<div class="ist-shade"></div>';
    root.querySelector('.iap-photo').style.backgroundImage = 'url(' + BASE + 'first.webp)';
    root.querySelector('.iap-seg').style.backgroundImage = 'url(' + BASE + 'seg-first.webp)';
    /* Show the video only once its first frame is really on screen (is-playing). On some GPU paths decode
       fails, and a stalled video would cover the still mask image with a white or black box. On failure it stays hidden. */
    var video = root.querySelector('video');
    video.muted = true;
    function shown() { if (!video.error) root.classList.add('is-playing'); }
    video.addEventListener('playing', function () {
      if (video.requestVideoFrameCallback) video.requestVideoFrameCallback(shown);
      else shown();
    });
    video.addEventListener('error', function () { root.classList.remove('is-playing'); });
    video.src = BASE + 'seg.mp4';
    overlay.insertBefore(root, overlay.firstChild);
    return root;
  }

  /* Called when the beat starts. Returns false if not ready — the beat then runs on the prompt alone. */
  function play(overlay, beatMs) {
    if (!_ready || !overlay) return false;
    stop();
    var root = _root = _build(overlay);
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { if (_root === root) root.classList.add('is-on'); });
    });
    _later(function () { root.classList.add('is-revealing'); }, REVEAL_AT);
    _later(function () {
      root.classList.add('is-revealed');
      var v = root.querySelector('video');
      try {
        v.currentTime = 0;
        var p = v.play();
        if (p && p.catch) p.catch(function () {});
      } catch (e) {}
    }, PLAY_AT);
    _later(function () { root.classList.add('is-out'); }, beatMs - 250);
    _later(stop, beatMs + 400);
    return true;
  }

  function stop() {
    _timers.forEach(clearTimeout);
    _timers.length = 0;
    if (_root) {
      var v = _root.querySelector('video');
      if (v) { try { v.pause(); v.removeAttribute('src'); v.load(); } catch (e) {} }
      if (_root.parentNode) _root.parentNode.removeChild(_root);
    }
    _root = null;
  }

  window.DXIntroApp = { prepare: prepare, play: play, stop: stop };
})();
