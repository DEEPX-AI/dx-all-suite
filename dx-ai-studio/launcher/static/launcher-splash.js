
(function() {
  var ns = window.DXLauncher;

  /* Intro.
   *
   * The intro follows the grammar of Apple and Google product ads rather than
   * borrowing a genre look (neon circuits, black holes): sell the product, not
   * the ad.
   *
   * Apple: hero reveal -> detail -> context shot (the product in use) -> one
   * claim. And:
   *
   *   · one subject on a black stage (at least 20% empty space around it)
   *   · the camera moves once, and the move reveals something
   *   · animate transform and opacity only (compositor-friendly)
   *   · springs: damping 1.0, response 0.3-0.4s; no abrupt starts or stops
   *   · tighten tracking on large type (-0.02em); type comes last
   *   · the signature is a hard specular sweeping across the surface
   *   · reduced motion falls back to an opacity crossfade
   *
   * Google "Parisian Love": no actors, no dialogue, only sentences typed into
   * the product's input box. The viewer's inference does the work.
   *
   * Both point to the same scene: the product at work. This product's premise
   * is "say what you want and it builds it", so the intro has three beats:
   *
   *   1. hero    the logotype arrives as a machined object; light sweeps it
   *   2. work    three prompts are typed; the studio answers with a module
   *   3. close   the prompts clear and the mark stays with the name
   *
   * The beat-2 prompts are not invented copy: they are the real prompts from
   * the home Build example chips, already translated into six languages. Each
   * answer is the module that handles that request; module names are proper
   * nouns and are not translated. */

  /* Typing runs on setTimeout, not a frame loop. Text length differs per
     language, so the total time is fixed rather than the per-character speed:
     every language must finish on the same beat or the sequence drifts. */
  var _TYPE_MS = 900;
  var _BEAT = 1950;
  /* Beats can differ in length: Stream is longer because its scene moves three
     times (box · pull-back · ripple; intro-stream.js). answerAt is when the answer
     appears: after the scene has made its point, leaving time to read it (about
     1.7-1.8s). note is a measured line attached to the answer
     (img/intro/stream/MEASURED.md). The 16 x 30 fps figure is an NPU number: this
     host's (N97) end-to-end rate is about 18 fps per channel, so the note quotes
     the NPU figure, which is true. */
  var _WORK = [
    { ask: '16-channel CCTV object detection', by: 'Stream', note: '16 channels on one DX-M1 · 495 fps NPU',
      ms: 4700, answerAt: 2600, scene: 'stream' },
    { ask: 'segment a video file', by: 'App', note: 'segformer · 200 fps on one DX-M1',
      ms: 4600, answerAt: 2650, scene: 'app' },
    { ask: 'compile yolo26n to DXNN', by: 'Compiler', note: 'yolo26n → DXNN · 212 fps on DX-M1',
      ms: 4600, answerAt: 2650, scene: 'compile' }
  ];
  /* The scene that fills the screen on each beat; each one has prepare / play / stop.
     If a scene is not ready (slow tunnel, missing images) the beat runs on the prompt alone. */
  function _scene(name) {
    return { stream: window.DXIntroStream, app: window.DXIntroApp, compile: window.DXIntroCompile }[name];
  }
  var _SCENES = ['stream', 'app', 'compile'];
  function _ms(item) { return item.ms || _BEAT; }
  var _WORK_MS = _WORK.reduce(function (sum, item) { return sum + _ms(item); }, 0);
  /* CSS shows the hero subtitle ("AI Studio") at 1.9s. work must start one
     beat after it settles, or the subtitle is pushed away before anyone sees it. */
  var _WORK_IN  = 3400;
  var _CLOSE    = _WORK_IN + _WORK_MS;         /* 17300 */
  /* close ends on a single claim. It needs reading time, so it runs longer
     than the return to hero would. */
  var _INTRO    = _CLOSE + 2600;              /* 19900 */

  function _t(key) {
    return (window.DXI18n && window.DXI18n.T) ? window.DXI18n.T(key) : key;
  }

  function _later(fn, ms) { ns._splashTimers.push(setTimeout(fn, ms)); }

  function _type(el, text) {
    var i = 0;
    var step = Math.max(18, Math.round(_TYPE_MS / Math.max(text.length, 1)));
    el.textContent = '';
    (function tick() {
      if (i >= text.length) return;
      i += 1;
      el.textContent = text.slice(0, i);
      _later(tick, step);
    })();
  }

  /* One beat: the request is typed, the studio answers, both step back. */
  function _beat(item, index, at) {
    var cue = document.getElementById('splashCue');
    var text = document.getElementById('splashCueText');
    var answer = document.getElementById('splashCueAnswer');
    if (!cue || !text || !answer) return;
    _later(function () {
      cue.classList.remove('is-answered', 'is-out');
      cue.setAttribute('data-beat', String(index));
      answer.textContent = item.note ? item.by + ' \u00b7 ' + _t(item.note) : item.by;
      /* is-scene (prompt moves down, logo steps aside) is set here, once per beat. When each
         scene cleared it itself, a late-starting scene's timer could fire after the next scene
         had set it, and the prompt jumped to the centre over the chips. */
      var ov = document.getElementById('splashOverlay');
      var scene = item.scene && _scene(item.scene);
      var played = !!(scene && scene.play(ov, _ms(item)));
      if (ov) ov.classList.toggle('is-scene', played);
      _type(text, _t(item.ask));
    }, at);
    _later(function () { cue.classList.add('is-answered'); }, at + (item.answerAt || _TYPE_MS + 260));
    _later(function () { cue.classList.add('is-out'); }, at + _ms(item) - 260);
  }

  function initSplashV2() {
    if (sessionStorage.getItem('dx-splash-seen')) {
      var ov0 = document.getElementById('splashOverlay');
      if (ov0) ov0.remove();
      revealMainContent();
      return false;
    }
    sessionStorage.setItem('dx-splash-seen', '1');
    ns._splashActive = true;
    if (typeof ns.hideStudioBootGate === 'function') ns.hideStudioBootGate({ conceal: true });

    var overlay = document.getElementById('splashOverlay');

    /* Crossfade for people who asked for reduced motion. */
    var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!still) _SCENES.forEach(function (name) { var s = _scene(name); if (s) s.prepare(); });
    if (still) {
      if (overlay) overlay.classList.add('is-still');
      ns._splashTimers.push(setTimeout(skipSplash, 700));
      return true;
    }

    /* Start one frame later so the initial state is painted before the transition.

       The cut's clock also starts here, on the frame the sequence actually starts.
       Measuring from the initSplashV2 call lets boot work on the main thread eat the
       budget (first frame can take over a second), and the intro gets cut short,
       more so on slower devices. */
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        if (overlay) overlay.classList.add('is-running');

        /* 2. work — the name steps back and the product works in its place. */
        _later(function () { if (overlay) overlay.classList.add('is-working'); }, _WORK_IN - 400);
        for (var i = 0, at = _WORK_IN; i < _WORK.length; at += _ms(_WORK[i]), i++) {
          _beat(_WORK[i], i, at);
        }

        /* 3. close — the prompts clear and the mark stays with the name. */
        _later(function () {
          if (!overlay) return;
          overlay.classList.remove('is-working', 'is-scene');
          overlay.classList.add('is-closed');
        }, _CLOSE);

        /* Last: start the app and leave on the mark — a cut, not a fade. */
        _later(function () {
          if (typeof ns.completeLauncherBoot === 'function') {
            ns.completeLauncherBoot({ revealAnimation: 'skip' });
          }
          if (overlay) overlay.classList.add('is-through');
          _later(function () { skipSplash(); }, 300);
        }, _INTRO);
      });
    });

    return true;
  }

  function skipSplash(manual) {
    if (manual === undefined) manual = false;
    var ov = document.getElementById('splashOverlay');
    if (!ov || ov.classList.contains('fade-out')) return;

    ns._splashTimers.forEach(function(id) { clearTimeout(id); });
    ns._splashTimers.length = 0;
    ns._splashActive = false;
    _SCENES.forEach(function (name) { var s = _scene(name); if (s) s.stop(); });
    if (ns._decodeRAF) { cancelAnimationFrame(ns._decodeRAF); ns._decodeRAF = null; }
    if (window._splashParticleCleanup) window._splashParticleCleanup();

    ov.classList.add('fade-out');
    sessionStorage.setItem('dx-splash-seen', '1');
    ns._splashActive = false;

    if (window._dxTutorial && typeof window._dxTutorial.hideTOC === 'function') {
      window._dxTutorial.hideTOC();
    }

    if (typeof ns.completeLauncherBoot === 'function') {
      ns.completeLauncherBoot({ revealAnimation: manual ? 'skip' : 'normal' });
    }

    // If the 8 module servers aren't ready yet, completeLauncherBoot is a no-op and the
    // shell stays boot-pending. Re-show the boot gate (concealed behind the splash until
    // now) so the user sees a "starting up" spinner instead of a blank screen until ready.
    if (!ns._studioReadyResolved && typeof ns.showStudioBootGate === 'function') {
      ns.showStudioBootGate();
    }

    setTimeout(function() {
      ov.remove();
      if (typeof ns.tryCompleteLauncherBoot === 'function') ns.tryCompleteLauncherBoot();
    }, 800);
  }

  function replaySplash() {
    var existing = document.getElementById('splashOverlay');
    if (existing) existing.remove();

    sessionStorage.removeItem('dx-splash-seen');

    var ov = document.createElement('div');
    ov.className = 'splash-overlay';
    ov.id = 'splashOverlay';
    ov.setAttribute('onclick', 'skipSplash(true)');
    ov.innerHTML =
      '<div class="mark" id="splashMark">' +
        '<span class="mark-face" aria-hidden="true"></span>' +
        '<span class="mark-sweep" aria-hidden="true">' +
          '<span class="mark-shine"></span>' +
        '</span>' +
        '<span class="mark-floor" aria-hidden="true">' +
          '<span class="mark-face"></span>' +
        '</span>' +
        '<span class="mark-a11y">DEEPX</span>' +
      '</div>' +
      '<div class="mark-slot">' +
        '<p class="mark-sub" id="splashSubtitle">AI Studio</p>' +
        '<blockquote class="mark-claim">' +
          '<p class="claim-line">' +
            '<span class="claim-a">\u201cThe center of gravity in AI is shifting</span> ' +
            '<span class="claim-b">from the cloud to <em>the physical world</em>.\u201d</span>' +
          '</p>' +
          '<footer class="claim-by">Lokwon Kim \u00b7 Founder &amp; CEO, DEEPX \u00b7 CES 2026</footer>' +
        '</blockquote>' +
      '<div class="mark-cue" id="splashCue" aria-hidden="true">' +
        '<span class="cue-line"><span class="cue-text" id="splashCueText"></span>' +
        '<i class="cue-caret"></i></span>' +
        '<span class="cue-answer" id="splashCueAnswer"></span>' +
      '</div>' +
      '</div>' +
      '<div class="splash-skip" data-i18n="Click to skip">Click to skip</div>';
    document.body.insertBefore(ov, document.body.firstChild);
    initSplashV2();
  }

  function showHeroSplash() {
    var hero = document.getElementById('heroSplash');
    if (!hero) { revealMainContent(); return; }

    window._heroTimer = setTimeout(dismissHeroSplash, 4000);
    setTimeout(function() { var h = document.getElementById('heroSplash'); if (h) { h.remove(); revealMainContent(); } }, 5000);
  }

  function dismissHeroSplash() {
    var hero = document.getElementById('heroSplash');
    if (!hero || hero.classList.contains('hidden')) return;
    clearTimeout(window._heroTimer);
    hero.classList.add('hidden');
    revealMainContent();
    setTimeout(function() { hero.remove(); }, 700);
  }

  function revealMainContent() {
    var main = document.querySelector('.landing-container') || document.querySelector('.top-bar') || document.getElementById('landing');
    if (main && !main.classList.contains('main-content-reveal') && !main.classList.contains('main-content-reveal-skip')) {
      main.classList.add(sessionStorage.getItem('dx-splash-seen') ? 'main-content-reveal-skip' : 'main-content-reveal');
    }
  }

  ns.initSplashV2 = initSplashV2;
  ns.skipSplash = skipSplash;
  ns.replaySplash = replaySplash;
  ns.showHeroSplash = showHeroSplash;
  ns.dismissHeroSplash = dismissHeroSplash;
  ns.revealMainContent = revealMainContent;
})();
if (typeof DXI18n !== 'undefined' && typeof DXI18n.onLangChange === 'function') {
  DXI18n.onLangChange(function() {
    if (typeof DXLauncher !== 'undefined' && typeof DXLauncher.refreshLauncherChrome === 'function') DXLauncher.refreshLauncherChrome();
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
