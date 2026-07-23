
(function() {
  var ns = window.DXLauncher;

  var BOOT_GATE_POLL_MS = 250;
  var BOOT_GATE_MAX_WAIT_MS = 120000;
  var _pendingRouteRestore = null;
  var _shellRevealInFlight = false;

  function hideStudioBootGate(options) {
    options = options || {};
    var gate = document.getElementById('studioBootGate');
    if (!gate) return;
    gate.setAttribute('aria-busy', 'false');
    if (options.conceal) {
      // Keep the gate in the DOM but hidden behind the full-screen splash, so an
      // early skip can re-show it while the studio is still booting (see skipSplash).
      gate.style.display = 'none';
      return;
    }
    if (options.instant) {
      if (gate.parentNode) gate.parentNode.removeChild(gate);
      return;
    }
    gate.classList.add('fade-out');
    setTimeout(function() {
      if (gate.parentNode) gate.parentNode.removeChild(gate);
    }, 400);
  }

  function showStudioBootGate() {
    var gate = document.getElementById('studioBootGate');
    if (!gate) return;
    gate.style.display = '';
    gate.classList.remove('fade-out');
    gate.setAttribute('aria-busy', 'true');
  }

  function isLauncherShellPending() {
    return document.documentElement &&
      document.documentElement.classList.contains('launcher-boot-pending');
  }

  function splashBlocksShellReveal() {
    var splashOverlay = document.getElementById('splashOverlay');
    if (!splashOverlay) return false;
    if (splashOverlay.classList.contains('fade-out') ||
        splashOverlay.classList.contains('dissolve-out')) {
      return false;
    }
    return true;
  }

  function _applyMainRevealAnimation(mode) {
    var main = document.querySelector('.landing-container') ||
      document.querySelector('.top-bar') ||
      document.getElementById('landing');
    if (!main) return;
    if (mode === 'skip') {
      main.classList.add('main-content-reveal-skip');
      return;
    }
    if (mode === 'normal') {
      main.classList.add('main-content-reveal');
      return;
    }
    if (typeof ns.revealMainContent === 'function') ns.revealMainContent();
  }

  function flushPendingRouteRestore() {
    if (!_pendingRouteRestore) return;
    var pending = _pendingRouteRestore;
    _pendingRouteRestore = null;
    LauncherRouter.restoreFromLocation(pending.loc, pending.opts);
  }

  function completeLauncherBoot(revealOpts) {
    revealOpts = revealOpts || {};
    if (!ns._studioReadyResolved) return;

    flushPendingRouteRestore();

    if (!isLauncherShellPending()) {
      if (revealOpts.revealAnimation) _applyMainRevealAnimation(revealOpts.revealAnimation);
      return;
    }
    if (_shellRevealInFlight) return;
    _shellRevealInFlight = true;

    if (typeof ns.scheduleOrbitalLayout === 'function') ns.scheduleOrbitalLayout();

    requestAnimationFrame(function() {
      requestAnimationFrame(function() {
        document.documentElement.classList.remove('launcher-boot-pending');
        if (revealOpts.revealAnimation) _applyMainRevealAnimation(revealOpts.revealAnimation);
        _shellRevealInFlight = false;
      });
    });
  }

  function tryCompleteLauncherBoot(revealOpts) {
    if (!ns._studioReadyResolved) return;
    if (splashBlocksShellReveal()) return;
    completeLauncherBoot(revealOpts);
  }

  function queueRouteRestore(loc, opts) {
    _pendingRouteRestore = { loc: loc || window.location, opts: opts || {} };
    tryCompleteLauncherBoot();
  }

  function shouldPlayIntroSplash() {
    return !sessionStorage.getItem('dx-splash-seen');
  }

  function isStudioReadyPayload(data) {
    if (!data || typeof data !== 'object') return false;
    if (data.studio_ready === true) return true;
    if (data.studio_ready === false) return false;
    // Handler-only tests / legacy health without the flag.
    return !!data.launcher_boot;
  }

  function _refreshViewAfterStudioReady() {
    if (!ns.currentApp) return;
    if (ns.currentApp === 'about') {
      LauncherRouter._showAbout({ skipHistory: true });
      return;
    }
    if (ns.currentApp === 'sdk-library') {
      LauncherRouter._showSdk({ source: 'boot-ready', skipHistory: true });
      return;
    }
    LauncherRouter._showApp(ns.currentApp, {
      forceReload: true,
      skipHistory: true,
      source: 'boot-ready',
    });
  }

  function ensureStudioReady(options) {
    options = options || {};
    if (ns._studioReadyResolved) {
      return Promise.resolve(ns._healthStatus || {});
    }
    if (ns._studioReadyPromise) return ns._studioReadyPromise;

    var showBootGate = options.showBootGate !== false;
    if (options.showBootGate === false) {
      showBootGate = false;
      hideStudioBootGate({ instant: true });
    } else if (shouldPlayIntroSplash()) {
      // Intro splash is full-screen and sits above the gate — conceal the gate (keep it
      // in the DOM) rather than removing it, so an early skip can re-show it while the
      // studio is still booting instead of leaving a blank screen (see skipSplash).
      showBootGate = true;
      hideStudioBootGate({ conceal: true });
    }

    ns._studioReadyPromise = new Promise(function(resolve) {
      var startedAt = Date.now();

      function finish(data) {
        ns._studioReadyResolved = true;
        if (showBootGate) hideStudioBootGate();
        if (!ns._launcherCoreStarted) ns._initLauncherCore();
        resolve(data || {});
        // Run after queued navigate()/restoreFromLocation handlers so early clicks win.
        queueMicrotask(function() {
          tryCompleteLauncherBoot();
          _refreshViewAfterStudioReady();
        });
      }

      function poll() {
        fetch('/api/health', { cache: 'no-store' })
          .then(function(res) { return res.json(); })
          .then(function(data) {
            if (_maybeReloadForLauncherBoot(data)) return;
            ns._healthStatus = data;
            ns._healthCheckedAt = Date.now();
            if (isStudioReadyPayload(data)) {
              finish(data);
              return;
            }
            if (Date.now() - startedAt >= BOOT_GATE_MAX_WAIT_MS) {
              finish(data);
              return;
            }
            setTimeout(poll, BOOT_GATE_POLL_MS);
          })
          .catch(function() {
            if (Date.now() - startedAt >= BOOT_GATE_MAX_WAIT_MS) {
              finish({});
              return;
            }
            setTimeout(poll, BOOT_GATE_POLL_MS);
          });
      }

      poll();
    });

    return ns._studioReadyPromise;
  }

  function appFromPath(pathname) {
    for (var key in ns.APP_PATHS) {
      var prefix = ns.APP_PATHS[key].replace(/\/$/, '');
      if (pathname === prefix || pathname.indexOf(prefix + '/') === 0) return key;
    }
    return null;
  }

  var _moduleIframes = {};

  function getIframePool() {
    var pool = document.getElementById('appIframePool');
    if (!pool) {
      var frame = document.getElementById('appFrame');
      pool = document.createElement('div');
      pool.id = 'appIframePool';
      pool.className = 'app-iframe-pool';
      if (frame) frame.appendChild(pool);
    }
    return pool;
  }

  function hideAllModuleIframes() {
    Object.keys(_moduleIframes).forEach(function (key) {
      var frame = _moduleIframes[key];
      if (!frame) return;
      frame.classList.remove('active');
      frame.removeAttribute('id');
      frame.hidden = true;
    });
  }

  function activateModuleIframe(iframe) {
    hideAllModuleIframes();
    if (!iframe) return;
    iframe.classList.add('active');
    iframe.id = 'appIframe';
    iframe.hidden = false;
  }

  function getOrCreateModuleIframe(appKey) {
    if (_moduleIframes[appKey]) return _moduleIframes[appKey];
    var iframe = document.createElement('iframe');
    iframe.className = 'module-iframe';
    iframe.dataset.app = appKey;
    iframe.setAttribute('frameborder', '0');
    iframe.title = moduleDisplayName(appKey);
    getIframePool().appendChild(iframe);
    _moduleIframes[appKey] = iframe;
    return iframe;
  }

  function broadcastToModuleIframes(msg) {
    Object.keys(_moduleIframes).forEach(function (key) {
      var frame = _moduleIframes[key];
      if (!frame || frame.dataset.loadState !== 'loaded') return;
      try {
        if (frame.contentWindow) frame.contentWindow.postMessage(msg, '*');
      } catch (e) { /* ignore */ }
    });
  }

  function getActiveAppIframe() {
    return document.getElementById('appIframe');
  }

  function loadAppIframe(iframe, iframePath) {
    if (!iframe) return;
    iframe.dataset.currentSrc = iframePath;
    try {
      if (iframe.contentWindow && iframe.contentWindow.location) {
        iframe.contentWindow.location.replace(iframePath);
        return;
      }
    } catch (e) {
      // Fall back below if a browser denies access to the frame location.
    }
    iframe.src = iframePath;
  }

  function loadAppIframeIfNeeded(iframe, iframePath, opts) {
    opts = opts || {};
    var loaded = iframe.dataset.loadedSrc || '';
    var ready = iframe.dataset.loadState === 'loaded';
    if (!opts.forceReload && ready && loaded === iframePath) return false;
    iframe.dataset.loadState = 'loading';
    iframe.dataset.loadedSrc = iframePath;
    loadAppIframe(iframe, iframePath);
    return true;
  }

  function disarmModuleIframeLoads(exceptIframe) {
    Object.keys(_moduleIframes).forEach(function (key) {
      var frame = _moduleIframes[key];
      if (!frame || frame === exceptIframe) return;
      frame.onload = null;
    });
  }

  function finishModuleEntry(appKey, iframe) {
    if (iframe) iframe.dataset.loadState = 'loaded';
    if (ns.currentApp !== appKey) return;
    if (_moduleLoadTimer) { clearTimeout(_moduleLoadTimer); _moduleLoadTimer = null; }
    if (ns._moduleRetryStart) ns._moduleRetryStart[appKey] = 0;  // success clears the self-heal window
    clearModuleEntryState();
    var overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.remove();
  }

  function animateIn(el) {
    if (!el) return;
    el.classList.remove('view-slide-in');
    void el.offsetWidth; // force reflow so animation re-triggers
    el.classList.add('view-slide-in');
  }

  function isIntroSplashPlaying() {
    return !!document.getElementById('splashOverlay');
  }

  function isLauncherShellBlocked() {
    if (isLauncherShellPending()) return true;
    if (isIntroSplashPlaying()) return true;
    // The boot gate is concealed (display:none), not removed, so gate on VISIBLE — a
    // mere existence check would report "blocked" forever after a conceal.
    var gate = document.getElementById('studioBootGate');
    if (gate && getComputedStyle(gate).display !== 'none') return true;
    if (!ns._studioReadyResolved) return true;
    return false;
  }

  function resetLauncherUiBlockers() {
    if (typeof ns.closePlatformInfo === 'function') ns.closePlatformInfo();
    else {
      var platformOverlay = document.getElementById('platformInfoOverlay');
      if (platformOverlay) platformOverlay.classList.remove('open');
    }
    clearModuleEntryState();
    var loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) loadingOverlay.remove();
    if (_moduleLoadTimer) { clearTimeout(_moduleLoadTimer); _moduleLoadTimer = null; }
    var splashOverlay = document.getElementById('splashOverlay');
    // Do not cut intro splash short when studio_ready fires during VS Code early entry.
    if (splashOverlay && splashOverlay.style.display !== 'none' && !isIntroSplashPlaying()) {
      splashOverlay.classList.add('fade-out');
      splashOverlay.style.pointerEvents = 'none';
    }
    var heroSplash = document.getElementById('heroSplash');
    if (heroSplash) {
      heroSplash.classList.add('hidden');
      heroSplash.style.pointerEvents = 'none';
    }
    document.body.style.overflow = '';
    document.documentElement.style.overflow = '';
  }

  function suspendAllTutorialChrome() {
    // A tutorial-driven navigation (e.g. home tour's beforeStart calling goHome from
    // inside a module) must NOT stop the tour it is starting. The step engine sets this
    // flag around its own navigation so the view switches without killing _curSection.
    if (ns && ns._tutorialDrivenNav) return;
    var sdkView = document.getElementById('sdk-library-view');
    var leavingSdk = sdkView && sdkView.classList.contains('visible');
    if (leavingSdk && window.SDKTutorial && typeof window.SDKTutorial.beforeLeave === 'function') {
      window.SDKTutorial.beforeLeave();
    }
    if (window._dxTutorial) {
      if (typeof window._dxTutorial.suspend === 'function') {
        window._dxTutorial.suspend();
      } else {
        if (typeof window._dxTutorial.hideTOC === 'function') window._dxTutorial.hideTOC();
        if (typeof window._dxTutorial.stop === 'function') window._dxTutorial.stop();
      }
    }
    if (typeof DXTutorialEngine !== 'undefined' &&
        typeof DXTutorialEngine.purgeOrphanChrome === 'function') {
      DXTutorialEngine.purgeOrphanChrome(document, window._dxTutorial);
    }
  }

  function stopEmbeddedModuleTutorial() {
    var iframe = document.getElementById('appIframe');
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.postMessage({ type: 'dx-tutorial-stop' }, '*');
    }
  }

  function setVisibleView(viewName) {
    suspendAllTutorialChrome();
    resetLauncherUiBlockers();
    _hideOrbitalTooltip();
    var landing   = document.getElementById('landing');
    var appFrame  = document.getElementById('appFrame');
    var aboutView = document.getElementById('about-view');
    var sdkView   = document.getElementById('sdk-library-view');
    var tutCard   = document.getElementById('dxt-tutorial-card');
    var rb        = document.getElementById('replayBtn');
    var footer    = document.getElementById('deepxFooter');

    document.body.classList.toggle('app-frame-visible', viewName === 'app');
    // The shared NPU Monitor float is injected into the launcher shell but should only show
    // on the launcher-native views (About, SDK Library) — module iframes carry their own, and
    // the home splash stays uncluttered.
    document.body.classList.toggle('hw-native-visible', viewName === 'about' || viewName === 'sdk-library');

    if (landing)   landing.style.display = 'none';
    if (footer)    footer.style.display = 'none';   // resource bar is home-shell chrome
    if (appFrame)  appFrame.style.display = 'none';
    if (aboutView) aboutView.classList.remove('visible');
    // Hide SDK shell without tearing down viewer/search — state survives module switches.
    if (window.hideSdkLibraryView) {
      window.hideSdkLibraryView({
        restoreToolbar: viewName === 'home' || viewName === 'about'
      });
    } else if (sdkView) sdkView.classList.remove('visible');
    if (tutCard)   tutCard.style.display = 'none';
    if (rb)        rb.style.display = 'none';

    // Keep module iframes alive in the pool — only hide the shell when leaving app view.

    if (viewName === 'home') {
      if (landing) { landing.style.display = ''; animateIn(landing); }
      if (footer)  footer.style.display = '';
      if (tutCard) tutCard.style.display = '';
      if (rb)      rb.style.display = '';
    } else if (viewName === 'about') {
      if (aboutView) aboutView.classList.add('visible');
    } else if (viewName === 'sdk-library') {
      if (sdkView) sdkView.classList.add('visible');
    } else if (viewName === 'app') {
      if (appFrame) { appFrame.style.display = 'block'; animateIn(appFrame); }
    }

    if (viewName !== 'app') {
      stopEmbeddedModuleTutorial();
    }
    if (viewName === 'home' || viewName === 'about') {
      if (window.LauncherTutorial && typeof window.LauncherTutorial.connectToolbar === 'function') {
        window.LauncherTutorial.connectToolbar();
      }
    }
  }

  var LauncherRouter = (function() {

    function _commitHistory(method, state, url) {
      if (method === 'push') history.pushState(state, '', url);
      else history.replaceState(state, '', url);
    }

    // The launcher builds one shared toolbar (#dxToolbar: language + tutorial) inside
    // #launcherToolbar in the global top bar. Every module carries these controls in its own
    // chrome, so on the launcher-native views (SDK Library, About DEEPX) we RELOCATE the same
    // element into that view's own header — unifying "each view owns its lang+tutorial" and
    // leaving the global bar's slot empty, just like it is hidden in module views. Moving (not
    // cloning) preserves every binding; tutorial spotlights targeting #dxToolbar follow it.
    function _relocateToolbar(target) {
      var toolbar = document.getElementById('dxToolbar');
      var dest = typeof target === 'string' ? document.querySelector(target) : target;
      if (!toolbar || !dest || toolbar.parentNode === dest) return;
      dest.appendChild(toolbar);
    }

    function _showHome(opts) {
      ns.currentApp = null;
      if (typeof ns.syncLangFromStorage === 'function') ns.syncLangFromStorage();
      setVisibleView('home');
      _relocateToolbar('#launcherToolbar');
      updateNavTabs();
      _commitHistory(opts && opts.push ? 'push' : 'replace', {}, '/');
    }

    function _showAbout(opts) {
      opts = opts || {};
      ns.currentApp = 'about';
      setVisibleView('about');
      _relocateToolbar('#aboutTopbarSlot');
      updateNavTabs();
      if (!opts.skipHistory) {
        _commitHistory(opts.push ? 'push' : 'replace', { app: 'about' }, '/about');
      }
      if (window.AboutDeepX && typeof window.AboutDeepX.onShown === 'function') {
        window.AboutDeepX.onShown();
      } else if (window.initAboutView) {
        window.initAboutView();
      }
    }

    function _showSdk(opts) {
      opts = opts || {};
      ns.currentApp = 'sdk-library';
      setVisibleView('sdk-library');
      if (window.SDKLibrary) window.SDKLibrary.init();
      // init() builds .sdk-topbar, so relocate the toolbar after it exists.
      _relocateToolbar('.sdk-topbar-right');
      updateNavTabs();
      var source = opts.source || 'restore';
      var url = '/sdk-library';
      if (opts.query) url += '?' + opts.query;
      if (!opts.skipHistory) {
        if (source !== 'popstate') {
          _commitHistory(opts.push ? 'push' : 'replace', { app: 'sdk-library' }, url);
        }
      }
      var queryStr = (opts && opts.query) || '';
      if (window.SDKLibrary && window.SDKLibrary.applyQuery) {
        if (source === 'popstate') {
          window.SDKLibrary.applyQuery(queryStr, { source: 'popstate' });
        } else {
          window.SDKLibrary.applyQuery(queryStr, { source: 'restore' });
        }
      }
    }

    function updateSdkLibraryQuery(nextQuery, options) {
      var opts = options || {};
      var method = opts.history === 'push' ? 'push' : 'replace';
      var url = '/sdk-library';
      var qs = _serializeSdkQuery(nextQuery);
      if (qs) url += '?' + qs;
      _commitHistory(method, { app: 'sdk-library' }, url);
    }

    function _serializeSdkQuery(queryObj) {
      if (!queryObj) return '';
      var doc, q, view;
      if (typeof queryObj.get === 'function') {
        doc = queryObj.get('doc') || '';
        q = queryObj.get('q') || '';
        view = queryObj.get('view') || '';
      } else {
        doc = queryObj.doc || '';
        q = queryObj.q || '';
        view = queryObj.view || '';
      }
      var parts = [];
      if (doc) parts.push('doc=' + encodeURIComponent(doc));
      if (q) parts.push('q=' + encodeURIComponent(q));
      if (view && view !== 'list') parts.push('view=' + encodeURIComponent(view));
      return parts.join('&');
    }

    function _showApp(appKey, opts) {
      opts = opts || {};
      ns.currentApp = appKey;
      clearModuleEntryState();
      var staleOverlay = document.getElementById('loadingOverlay');
      if (staleOverlay) staleOverlay.remove();

      if (_moduleLoadTimer) { clearTimeout(_moduleLoadTimer); _moduleLoadTimer = null; }

      var iframe = getOrCreateModuleIframe(appKey);
      iframe.onload = null;
      disarmModuleIframeLoads(iframe);
      activateModuleIframe(iframe);

      setVisibleView('app');
      // Return the shared toolbar to the (CSS-hidden) global slot so it isn't stranded inside a
      // now-hidden SDK/About header; the module supplies its own lang+tutorial inside its iframe.
      _relocateToolbar('#launcherToolbar');
      updateNavTabs();

      var iframePath = ns.APP_PATHS[appKey] || ('/' + appKey + '/');
      if (opts.suffix) iframePath += opts.suffix;
      if (opts.query) iframePath += '?' + opts.query;
      else if (opts.rawQuery) iframePath += opts.rawQuery;

      var historyUrl = '/' + appKey;
      if (opts.suffix) historyUrl += '/' + opts.suffix;
      if (opts.query) historyUrl += '?' + opts.query;
      else if (opts.rawQuery) historyUrl += opts.rawQuery;

      if (!opts.skipHistory && opts.source !== 'popstate') {
        _commitHistory(opts.push ? 'push' : 'replace', { app: appKey }, historyUrl);
      }

      var healthOpts = Object.assign({}, opts);
      if (healthOpts.push && !healthOpts.skipHistory && healthOpts.source !== 'popstate') {
        healthOpts.forceHealth = true;
      }

      resolveModuleHealth(appKey, healthOpts).then(function(status) {
        if (ns.currentApp !== appKey) return;

        if (!status || !status.alive) {
          var reason = (status && status.watchdogUnavailable) ? 'watchdog-unavailable' : 'unavailable';
          handleModuleEntryFailure(appKey, opts, reason, function() {
            retryModuleLaunch(appKey, opts, reason);
          });
          return;
        }

        var forceReload = !!opts.forceReload;
        var needsLoad = loadAppIframeIfNeeded(iframe, iframePath, { forceReload: forceReload });

        if (!needsLoad) {
          finishModuleEntry(appKey, iframe);
          return;
        }

        if (_moduleLoadTimer) { clearTimeout(_moduleLoadTimer); _moduleLoadTimer = null; }

        renderModuleLoading(appKey);
        _moduleLoadTimer = setTimeout(function() {
          _moduleLoadTimer = null;
          if (ns.currentApp !== appKey) return;
          iframe.onload = null;
          handleModuleEntryFailure(appKey, opts, 'load-timeout', function() {
            retryModuleLaunch(appKey, opts, 'load-timeout');
          });
        }, MODULE_LOAD_TIMEOUT_MS);

        iframe.onload = function() {
          finishModuleEntry(appKey, iframe);
        };
      }).catch(function(err) {
        console.error('[launcher] module health callback error for ' + appKey + ':', err);
        if (ns.currentApp !== appKey) return;
        if (_moduleLoadTimer) { clearTimeout(_moduleLoadTimer); _moduleLoadTimer = null; }
        iframe.onload = null;
        handleModuleEntryFailure(appKey, opts, 'error', function() {
          retryModuleLaunch(appKey, opts, 'error');
        });
      });
    }

    function navigate(target, opts) {
      ensureStudioReady().then(function() {
        navigateNow(target, opts);
      });
    }

    function navigateNow(target, opts) {
      opts = opts || {};
      opts.push = true;
      if (target === 'home') return _showHome(opts);
      if (target === 'about') return _showAbout(opts);
      if (target === 'sdk-library') return _showSdk(opts);
      if (target === 'app' && opts.app) {
        return _showApp(opts.app, { push: true, query: opts.query });
      }
      _showApp(target, { push: true, query: opts.query });
    }

    function restoreFromLocation(loc, opts) {
      var pathname = loc.pathname || '/';
      var search = loc.search || '';
      var source = (opts && opts.source) || 'restore';

      if (pathname === '/about') return _showAbout();
      if (pathname === '/sdk-library') return _showSdk({ query: search ? search.slice(1) : '', source: source });

      var appKey = appFromPath(pathname);
      if (appKey) {
        var basePath = ns.APP_PATHS[appKey].replace(/\/$/, '');
        var suffix = pathname.length > basePath.length ? pathname.slice(basePath.length + 1) : '';
        return _showApp(appKey, { suffix: suffix, rawQuery: search, source: source });
      }
      if (pathname !== '/') renderRouteRecoveryNotice(pathname);
      _showHome();
    }

    return {
      navigate: navigate,
      navigateNow: navigateNow,
      restoreFromLocation: restoreFromLocation,
      updateSdkLibraryQuery: updateSdkLibraryQuery,
      _commitHistory: _commitHistory,
      _showHome: _showHome,
      _showAbout: _showAbout,
      _showSdk: _showSdk,
      _showApp: _showApp
    };
  })();

  function goHome() { LauncherRouter.navigate('home'); }
  function showAboutView() { LauncherRouter.navigate('about'); }
  function showSdkLibrary() { LauncherRouter.navigate('sdk-library'); }
  function launch(app, query) { LauncherRouter.navigate('app', { app: app, query: query }); }

  var NAV_TAB_LABELS = {
    app: '📱 DX App',
    stream: '🎬 DX Stream',
    zoo: '🦁 Model Zoo',
    compiler: '⚙️ Compiler',
    planner: '🗺️ EdgeGuide',
    benchmark: '📊 Benchmark',
    dx_monitor: '📡 Monitor',
    agent: '🤖 Agent Dev',
    'sdk-library': '📚 SDK Library',
    about: '🔬 About DEEPX',
  };
  var NAV_TAB_CONFIG = [
    { app: 'app', label: NAV_TAB_LABELS.app, action: function() { launch('app'); }, activeClass: 'active' },
    { app: 'stream', label: NAV_TAB_LABELS.stream, action: function() { launch('stream'); }, activeClass: 'active-stream' },
    { app: 'zoo', label: NAV_TAB_LABELS.zoo, action: function() { launch('zoo'); }, activeClass: 'active-zoo' },
    { app: 'compiler', label: NAV_TAB_LABELS.compiler, action: function() { launch('compiler'); }, activeClass: 'active' },
    { app: 'planner', label: NAV_TAB_LABELS.planner, action: function() { launch('planner'); }, activeClass: 'active' },
    { app: 'benchmark', label: NAV_TAB_LABELS.benchmark, action: function() { launch('benchmark'); }, activeClass: 'active' },
    { app: 'dx_monitor', label: NAV_TAB_LABELS.dx_monitor, action: function() { launch('dx_monitor'); }, activeClass: 'active' },
    { app: 'agent', label: NAV_TAB_LABELS.agent, action: function() { launch('agent'); }, activeClass: 'active' },
    { app: 'sdk-library', label: NAV_TAB_LABELS['sdk-library'], action: showSdkLibrary, activeClass: 'active' },
    { app: 'about', label: NAV_TAB_LABELS.about, action: showAboutView, activeClass: 'active' },
  ];
  var MODULE_LABEL_LANGS = ['en', 'ko', 'ja', 'zh-CN', 'zh-TW', 'es'];
  var MODULE_LABEL_MATRIX = {
    app: { en: 'DX App', ko: 'DX App', ja: 'DX App', 'zh-CN': 'DX App', 'zh-TW': 'DX App', es: 'DX App' },
    stream: { en: 'DX Stream', ko: 'DX Stream', ja: 'DX Stream', 'zh-CN': 'DX Stream', 'zh-TW': 'DX Stream', es: 'DX Stream' },
    zoo: { en: 'Model Zoo', ko: 'Model Zoo', ja: 'Model Zoo', 'zh-CN': 'Model Zoo', 'zh-TW': 'Model Zoo', es: 'Model Zoo' },
    compiler: { en: 'Compiler', ko: 'Compiler', ja: 'コンパイラ', 'zh-CN': '编译器', 'zh-TW': '編譯器', es: 'Compilador' },
    planner: { en: 'EdgeGuide', ko: 'EdgeGuide', ja: 'EdgeGuide', 'zh-CN': 'EdgeGuide', 'zh-TW': 'EdgeGuide', es: 'EdgeGuide' },
    benchmark: { en: 'Benchmark', ko: 'Benchmark', ja: 'ベンチマーク', 'zh-CN': 'Benchmark', 'zh-TW': 'Benchmark', es: 'Benchmark' },
    dx_monitor: { en: 'Monitor', ko: 'Monitor', ja: 'モニター', 'zh-CN': '监控', 'zh-TW': '監控', es: 'Monitor' },
    agent: { en: 'Agent Dev', ko: 'Agent Dev', ja: 'Agent Dev', 'zh-CN': 'Agent Dev', 'zh-TW': 'Agent Dev', es: 'Agent Dev' },
    'sdk-library': { en: 'SDK Library', ko: 'SDK 라이브러리', ja: 'SDK ライブラリ', 'zh-CN': 'SDK 库', 'zh-TW': 'SDK 庫', es: 'Biblioteca SDK' },
    about: { en: 'About DEEPX', ko: 'DEEPX 소개', ja: 'DEEPXについて', 'zh-CN': '关于 DEEPX', 'zh-TW': '關於 DEEPX', es: 'Acerca de DEEPX' },
  };
  var MODULE_ORBITAL_MATRIX = {
    app: { en: 'DX App', ko: 'DX App', ja: 'DX App', 'zh-CN': 'DX App', 'zh-TW': 'DX App', es: 'DX App' },
    stream: { en: 'DX Stream', ko: 'DX Stream', ja: 'DX Stream', 'zh-CN': 'DX Stream', 'zh-TW': 'DX Stream', es: 'DX Stream' },
    zoo: { en: 'DX Model Zoo', ko: 'DX Model Zoo', ja: 'DX Model Zoo', 'zh-CN': 'DX Model Zoo', 'zh-TW': 'DX Model Zoo', es: 'DX Model Zoo' },
    compiler: { en: 'DX Compiler', ko: 'DX Compiler', ja: 'DX Compiler', 'zh-CN': 'DX Compiler', 'zh-TW': 'DX Compiler', es: 'DX Compiler' },
    planner: { en: 'DX EdgeGuide', ko: 'DX EdgeGuide', ja: 'DX EdgeGuide', 'zh-CN': 'DX EdgeGuide', 'zh-TW': 'DX EdgeGuide', es: 'DX EdgeGuide' },
    benchmark: { en: 'DX Benchmark', ko: 'DX Benchmark', ja: 'DX Benchmark', 'zh-CN': 'DX Benchmark', 'zh-TW': 'DX Benchmark', es: 'DX Benchmark' },
    dx_monitor: { en: 'DX Monitor', ko: 'DX Monitor', ja: 'DX Monitor', 'zh-CN': 'DX Monitor', 'zh-TW': 'DX Monitor', es: 'DX Monitor' },
    agent: { en: 'DX Agent Dev', ko: 'DX Agent Dev', ja: 'DX Agent Dev', 'zh-CN': 'DX Agent Dev', 'zh-TW': 'DX Agent Dev', es: 'DX Agent Dev' },
    'sdk-library': MODULE_LABEL_MATRIX['sdk-library'],
    about: MODULE_LABEL_MATRIX.about,
  };
  var PM_HELP_ID_TO_MODULE = {
    'pm-dx-app': 'app',
    'pm-dx-stream': 'stream',
    'pm-model-zoo': 'zoo',
    'pm-compiler': 'compiler',
    'pm-edgeguide': 'planner',
    'pm-benchmark': 'benchmark',
    'pm-monitor': 'dx_monitor',
    'pm-agent-dev': 'agent',
    'pm-sdk-library': 'sdk-library',
    'pm-about-deepx': 'about',
  };

  function _moduleLabelSpanHtml(map) {
    return MODULE_LABEL_LANGS.map(function(lang) {
      return '<span class="' + lang + '">' + (map[lang] || map.en || '') + '</span>';
    }).join('');
  }

  function _refreshModuleLabelElements() {
    document.querySelectorAll('[data-i18n-module]').forEach(function(el) {
      var key = el.getAttribute('data-i18n-module');
      var variant = el.getAttribute('data-i18n-variant') || 'poster';
      var map = variant === 'orbital' ? MODULE_ORBITAL_MATRIX[key] : MODULE_LABEL_MATRIX[key];
      if (map) el.innerHTML = _moduleLabelSpanHtml(map);
    });
    document.querySelectorAll('.pm-item[data-help-id]').forEach(function(item) {
      var key = PM_HELP_ID_TO_MODULE[item.getAttribute('data-help-id')];
      var nameEl = item.querySelector('.pm-name');
      if (key && nameEl && MODULE_LABEL_MATRIX[key]) {
        nameEl.innerHTML = _moduleLabelSpanHtml(MODULE_LABEL_MATRIX[key]);
      }
    });
    // About header now uses the shared DXBrand component (mounted in about-deepx.js), so the old
    // #aboutLogoTitle hook is gone.
  }

  var STATUS_DOT_LABELS = {
    statusLabelApp: 'App',
    statusLabelStream: 'Stream',
    statusLabelZoo: 'Zoo',
    statusLabelCompiler: 'Compiler',
    statusLabelPlanner: 'EdgeGuide',
    statusLabelBenchmark: 'Benchmark',
    statusLabelMonitor: 'Monitor',
    statusLabelAgent: 'Agent',
  };
  var STATUS_DOT_CONFIG = [
    { labelId: 'statusLabelApp', label: STATUS_DOT_LABELS.statusLabelApp },
    { labelId: 'statusLabelStream', label: STATUS_DOT_LABELS.statusLabelStream },
    { labelId: 'statusLabelZoo', label: STATUS_DOT_LABELS.statusLabelZoo },
    { labelId: 'statusLabelCompiler', label: STATUS_DOT_LABELS.statusLabelCompiler },
    { labelId: 'statusLabelPlanner', label: STATUS_DOT_LABELS.statusLabelPlanner },
    { labelId: 'statusLabelBenchmark', label: STATUS_DOT_LABELS.statusLabelBenchmark },
    { labelId: 'statusLabelMonitor', label: STATUS_DOT_LABELS.statusLabelMonitor },
    { labelId: 'statusLabelAgent', label: STATUS_DOT_LABELS.statusLabelAgent },
  ];
  var NAV_ACTIVE_CLASSES = ['active', 'active-stream', 'active-zoo'];

  function _buildNavTabs(container) {
    var home = document.createElement('div');
    home.className = 'nav-tab home-btn';
    home.dataset.home = '1';
    home.textContent = '🏠';
    home.setAttribute('tabindex', '0');
    home.setAttribute('role', 'button');
    home.addEventListener('click', goHome);
    home.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); goHome(); }
    });
    container.appendChild(home);

    NAV_TAB_CONFIG.forEach(function(item) {
      var tab = document.createElement('div');
      tab.className = 'nav-tab';
      tab.dataset.app = item.app;
      tab.dataset.activeClass = item.activeClass;
      tab.textContent = item.label || '';
      tab.setAttribute('tabindex', '0');
      tab.setAttribute('role', 'button');
      tab.addEventListener('click', item.action);
      tab.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); item.action(); }
      });
      container.appendChild(tab);
    });
    container.dataset.built = '1';
  }

  function _refreshNavTabLabels() {
    var container = document.getElementById('navTabs');
    if (!container || !container.dataset.built) return;
    var home = container.querySelector('.nav-tab[data-home]');
    if (home) home.title = ns._lt('Home', '홈으로', 'ホーム', '首页', '首頁', 'Inicio');
    // Module tab names stay English regardless of UI language.
  }

  function _refreshStatusDotLabels() {
    STATUS_DOT_CONFIG.forEach(function(item) {
      var label = document.getElementById(item.labelId);
      if (label && item.label) label.textContent = item.label;
    });
  }

  ns._moduleEntryState = null;

  function refreshModuleEntryChrome() {
    var st = ns._moduleEntryState;
    if (!st || !st.appKey) return;
    if (st.kind === 'loading') renderModuleLoading(st.appKey);
    else if (st.kind === 'error') renderModuleUnavailable(st.appKey, st.reason, st.retryFn);
  }

  function refreshLauncherChrome() {
    _refreshNavTabLabels();
    _refreshStatusDotLabels();
    _refreshModuleLabelElements();
    refreshModuleEntryChrome();
    if (typeof updateHubLauncherPort === 'function' && ns._healthStatus) {
      updateHubLauncherPort(ns._healthStatus);
    }
    if (typeof updateModulePortLabels === 'function' && ns._healthStatus) {
      updateModulePortLabels(ns._healthStatus);
    }
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  }

  function updateNavTabs() {
    var container = document.getElementById('navTabs');
    if (!container) return;
    if (!ns.currentApp) {
      // Home: clear any lingering active class off the module tabs before hiding, so the
      // last-entered module's highlight doesn't survive and reappear next time the bar shows.
      container.querySelectorAll('.nav-tab[data-app]').forEach(function(tab) {
        NAV_ACTIVE_CLASSES.forEach(function(className) { tab.classList.remove(className); });
      });
      container.hidden = true;
      updateActiveModuleCards();
      return;
    }
    container.hidden = false;
    if (!container.dataset.built) _buildNavTabs(container);

    var home = container.querySelector('.nav-tab[data-home]');
    if (home) home.title = ns._lt('Home', '홈으로', 'ホーム', '首页', '首頁', 'Inicio');

    container.querySelectorAll('.nav-tab[data-app]').forEach(function(tab) {
      var isActive = tab.dataset.app === ns.currentApp;
      NAV_ACTIVE_CLASSES.forEach(function(className) {
        tab.classList.toggle(className, isActive && tab.dataset.activeClass === className);
      });
      if (isActive && typeof tab.scrollIntoView === 'function') {
        tab.scrollIntoView({ block: 'nearest', inline: 'nearest' });
      }
    });
    updateActiveModuleCards();
  }

  // 8s was too tight for remote access (many head resources over a higher-latency link
  // proxied through the launcher) → spurious "Load timeout". 20s gives headroom; the
  // Retry button still covers genuine transients.
  var MODULE_LOAD_TIMEOUT_MS = 20000;
  var MODULE_HEALTH_STALE_MS = 6000;
  var _moduleLoadTimer = null;

  // When the studio is opened the instant the launcher port starts listening (e.g. VS
  // Code "open in browser"), a module server may still be spawning — its first health
  // probe / iframe load fails. Rather than dropping the user on a manual "unavailable"
  // screen, silently retry within a bounded window so the module fills in once it is up.
  var MODULE_AUTO_RETRY_WINDOW_MS = 30000;
  var MODULE_AUTO_RETRY_DELAY_MS = 1500;
  ns._moduleRetryStart = ns._moduleRetryStart || {};

  function handleModuleEntryFailure(appKey, opts, reason, manualRetryFn) {
    // A crashed-and-unrecoverable backend is not transient — go straight to manual.
    if (reason === 'watchdog-unavailable') {
      renderModuleUnavailable(appKey, reason, manualRetryFn);
      return;
    }
    var now = Date.now();
    if (!ns._moduleRetryStart[appKey]) ns._moduleRetryStart[appKey] = now;
    if (now - ns._moduleRetryStart[appKey] < MODULE_AUTO_RETRY_WINDOW_MS) {
      renderModuleLoading(appKey);
      setTimeout(function() {
        if (ns.currentApp !== appKey) return;
        retryModuleLaunch(appKey, opts, reason);
      }, MODULE_AUTO_RETRY_DELAY_MS);
      return;
    }
    ns._moduleRetryStart[appKey] = 0;  // window exhausted — reset for a future manual retry
    renderModuleUnavailable(appKey, reason, manualRetryFn);
  }

  function _maybeReloadForLauncherBoot(data) {
    if (!data || !data.launcher_boot) return false;
    // Never reload mid-navigation — that aborts About / iframe module entry.
    if (ns.currentApp) {
      sessionStorage.setItem('dx-launcher-boot', data.launcher_boot);
      return false;
    }
    var prev = sessionStorage.getItem('dx-launcher-boot');
    if (prev && prev !== data.launcher_boot) {
      // A changed boot id is a genuine launcher restart ONLY after we have already
      // reached studio-ready once. Before first-ready — e.g. VS Code "open in browser"
      // fires the instant the port starts listening, while the boot id is still
      // settling — a reload here would abort a top-bar navigation that is queued behind
      // ensureStudioReady() (currentApp is not set yet), making the click look ignored.
      // That was a chronic early-open bug. Pre-ready: just adopt the new id, never reload.
      sessionStorage.setItem('dx-launcher-boot', data.launcher_boot);
      if (ns._studioReadyResolved) {
        location.reload();
        return true;
      }
      return false;
    }
    if (!prev) sessionStorage.setItem('dx-launcher-boot', data.launcher_boot);
    return false;
  }

  var MODULE_PORT_HEALTH_KEYS = {
    app: 'app',
    stream: 'stream',
    zoo: 'zoo',
    compiler: 'compiler',
    planner: 'planner',
    benchmark: 'benchmark',
    dx_monitor: 'monitor',
    agent: 'agent'
  };

  function _resolveLauncherPort(data) {
    var port = window.location.port;
    if (!port && window.location.protocol !== 'file:') port = '80';
    if (data && data.launcher_boot) {
      var bootPort = String(data.launcher_boot).split('-')[0];
      if (bootPort) port = bootPort;
    }
    return port;
  }

  function _setPortLabel(el, label, url, title) {
    el.textContent = '';
    if (url) {
      var a = document.createElement('a');
      a.className = 'port-link';
      a.href = url;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.textContent = label;
      if (title) a.title = title;
      el.appendChild(a);
    } else {
      el.textContent = label;
    }
  }

  function updateHubLauncherPort(data) {
    var el = document.getElementById('hubLauncherPort');
    if (!el) return;
    var port = _resolveLauncherPort(data);
    var label = port ? (':' + port) : ':—';
    var url = port ? (window.location.protocol + '//' + window.location.hostname + ':' + port + '/') : null;
    var title = ns._lt(
      'Launcher gateway (integrated UI)',
      'Launcher gateway (통합 UI)',
      'Launcher gateway (統合 UI)',
      'Launcher 网关（集成 UI）',
      'Launcher 閘道（整合 UI）',
      'Launcher gateway (Puerta de enlace integrada)'
    );
    _setPortLabel(el, label, url, title);
  }

  function updateModulePortLabels(data) {
    document.querySelectorAll('.orbital-card[data-app]').forEach(function(card) {
      var appKey = card.getAttribute('data-app');
      var healthKey = MODULE_PORT_HEALTH_KEYS[appKey];
      if (!healthKey) return;
      var el = card.querySelector('.orbital-port');
      if (!el) return;
      var entry = data && data[healthKey];
      var port = entry && entry.port;
      var alive = entry && entry.alive;
      var label = (alive && port) ? (':' + port) : ':—';
      var url = (alive && port) ? ('http://127.0.0.1:' + port + '/') : null;
      var title = url ? ns._lt(
        'Open module directly (localhost)',
        '모듈 직접 열기 (localhost)',
        'モジュールを直接開く (localhost)',
        '直接打开模块 (localhost)',
        '直接開啟模組 (localhost)',
        'Abrir módulo directamente (localhost)'
      ) : null;
      _setPortLabel(el, label, url, title);
    });
  }

  function checkHealth() {
    return fetch('/api/health').then(function(res) { return res.json(); }).then(function(data) {
      if (_maybeReloadForLauncherBoot(data)) return data;
      ns._healthStatus = data;
      ns._healthCheckedAt = Date.now();
      setDot('dotApp',    data.app.alive);
      setDot('dotStream', data.stream ? data.stream.alive : false);
      setDot('dotZoo',    data.zoo ? data.zoo.alive : false);
      setDot('dotCompiler', data.compiler ? data.compiler.alive : false);
      setDot('dotPlanner',  data.planner ? data.planner.alive : false);
      setDot('dotBenchmark', data.benchmark ? data.benchmark.alive : false);
      setDot('dotMonitor',  data.monitor ? data.monitor.alive : false);
      setDot('dotAgent',    data.agent ? data.agent.alive : false);
      setStatus('statusApp',      data.app.alive);
      setStatus('statusStream',   data.stream ? data.stream.alive : false);
      setStatus('statusZoo',      data.zoo ? data.zoo.alive : false);
      setStatus('statusCompiler', data.compiler ? data.compiler.alive : false);
      setStatus('statusPlanner',  data.planner ? data.planner.alive : false);
      setStatus('statusBenchmark', data.benchmark ? data.benchmark.alive : false);
      _setOrbStatus('orbStatusApp', data.app.alive);
      _setOrbStatus('orbStatusStream', data.stream ? data.stream.alive : false);
      _setOrbStatus('orbStatusZoo', data.zoo ? data.zoo.alive : false);
      _setOrbStatus('orbStatusCompiler', data.compiler ? data.compiler.alive : false);
      _setOrbStatus('orbStatusPlanner', data.planner ? data.planner.alive : false);
      _setOrbStatus('orbStatusBenchmark', data.benchmark ? data.benchmark.alive : false);
      _setOrbStatus('orbStatusMonitor', data.monitor ? data.monitor.alive : false);
      _setOrbStatus('orbStatusAgent', data.agent ? data.agent.alive : false);
      updateHubLauncherPort(data);
      updateModulePortLabels(data);
      return data;
    }).catch(function() {
      setDot('dotApp', false);
      setDot('dotStream', false);
      setDot('dotZoo', false);
      setDot('dotCompiler', false);
      setDot('dotPlanner', false);
      setDot('dotBenchmark', false);
      setDot('dotMonitor', false);
      setDot('dotAgent', false);
      setStatus('statusApp', false);
      setStatus('statusStream', false);
      setStatus('statusZoo', false);
      setStatus('statusCompiler', false);
      setStatus('statusPlanner', false);
      setStatus('statusBenchmark', false);
      setStatus('statusMonitor', false);
      _setOrbStatus('orbStatusApp', false);
      _setOrbStatus('orbStatusStream', false);
      _setOrbStatus('orbStatusZoo', false);
      _setOrbStatus('orbStatusCompiler', false);
      _setOrbStatus('orbStatusPlanner', false);
      _setOrbStatus('orbStatusBenchmark', false);
      _setOrbStatus('orbStatusMonitor', false);
      _setOrbStatus('orbStatusAgent', false);
      updateHubLauncherPort({});
      updateModulePortLabels({});
      return {};
    });
  }

  function resolveModuleHealth(appKey, opts) {
    var force = opts && opts.forceHealth;
    var healthKey = appKey === 'dx_monitor' ? 'monitor' : appKey;
    var status = ns._healthStatus && ns._healthStatus[healthKey];
    var stale = !ns._healthCheckedAt || Date.now() - ns._healthCheckedAt > MODULE_HEALTH_STALE_MS;

    var healthPromise = (status && !stale && !force)
      ? Promise.resolve(status)
      : checkHealth().then(function(data) {
          var entry = data && data[healthKey];
          // entry present  → /api/health ran; trust it (alive true OR a real down).
          // entry absent   → the probe itself couldn't run (launcher busy under a request
          //   burst). Do NOT block entry on that — load the iframe optimistically; its own
          //   20s load-timeout is the real availability gate. This removes the false
          //   "unavailable" that previously forced a manual retry / refresh.
          return entry || { alive: true, optimistic: true };
        }).catch(function() {
          return { alive: true, optimistic: true };
        });

    // Also check watchdog status for richer failure info
    return healthPromise.then(function(healthResult) {
      if (healthResult && healthResult.alive) return healthResult;
      return fetch('/api/modules/' + encodeURIComponent(appKey) + '/status', {
        credentials: 'same-origin'
      }).then(function(r) { return r.json(); }).then(function(wd) {
        if (wd && wd.status === 'unavailable') {
          ns._lastWatchdogDetail = wd;
          return { alive: false, watchdogUnavailable: true };
        }
        return healthResult;
      }).catch(function() {
        return healthResult;
      });
    });
  }

  function moduleDisplayName(appKey) {
    var names = {
      app: 'DX App', stream: 'DX Stream',
      zoo: 'DX Model Zoo', compiler: 'DX Compiler', planner: 'DX EdgeGuide',
      benchmark: 'DX Benchmark', dx_monitor: 'DX Monitor',
      agent: 'DX Agent Dev'
    };
    return names[appKey] || appKey;
  }

  function renderModuleLoading(appKey) {
    clearModuleEntryState();
    ns._moduleEntryState = { appKey: appKey, kind: 'loading' };
    var panel = document.createElement('div');
    panel.className = 'module-entry-state module-entry-loading';
    var spinner = document.createElement('div');
    spinner.className = 'spinner';
    var title = document.createElement('div');
    title.className = 'module-entry-title';
    title.textContent = moduleDisplayName(appKey);
    var message = document.createElement('div');
    message.className = 'module-entry-message';
    message.textContent = ns._lt('Loading...', '로딩 중...', '読み込み中...', '加载中...', '載入中...', 'Cargando...');
    panel.appendChild(spinner);
    panel.appendChild(title);
    panel.appendChild(message);
    var appFrame = document.getElementById('appFrame');
    if (appFrame) appFrame.appendChild(panel);
  }

  function renderModuleUnavailable(appKey, reason, retryFn) {
    clearModuleEntryState();
    ns._moduleEntryState = { appKey: appKey, kind: 'error', reason: reason, retryFn: retryFn };
    var panel = document.createElement('div');
    panel.className = 'module-entry-state module-entry-error';
    var msg;
    if (reason === 'load-timeout') {
      msg = ns._lt('Load timeout', '로딩 시간 초과', '読み込みタイムアウト', '加载超时', '載入逾時', 'Tiempo de carga agotado');
    } else if (reason === 'watchdog-unavailable') {
      msg = ns._lt('Module crashed and could not be recovered', '모듈이 중단되어 복구할 수 없습니다', 'モジュールがクラッシュし復旧できませんでした', '模块崩溃且无法恢复', '模組崩潰且無法恢復', 'El módulo falló y no pudo recuperarse');
    } else {
      msg = ns._lt('Module unavailable', '모듈 사용 불가', 'モジュール利用不可', '模块不可用', '模組不可用', 'Módulo no disponible');
    }
    var title = document.createElement('div');
    title.className = 'module-entry-title';
    title.textContent = moduleDisplayName(appKey);
    var message = document.createElement('div');
    message.className = 'module-entry-message';
    message.textContent = msg;
    panel.appendChild(title);
    panel.appendChild(message);

    // Show extra detail for watchdog failures
    if (reason === 'watchdog-unavailable' && ns._lastWatchdogDetail) {
      var detail = document.createElement('div');
      detail.className = 'module-entry-detail';
      var parts = [];
      if (ns._lastWatchdogDetail.path) parts.push('Path: ' + ns._lastWatchdogDetail.path);
      if (ns._lastWatchdogDetail.port) parts.push('Port: ' + ns._lastWatchdogDetail.port);
      if (ns._lastWatchdogDetail.last_error) parts.push(ns._lastWatchdogDetail.last_error);
      detail.textContent = parts.join(' · ');
      panel.appendChild(detail);
    }

    if (retryFn) {
      var btn = document.createElement('button');
      btn.className = 'module-retry-btn';
      btn.textContent = ns._lt('Retry', '재시도', '再試行', '重试', '重試', 'Reintentar');
      btn.addEventListener('click', retryFn);
      panel.appendChild(btn);
    }
    var appFrame = document.getElementById('appFrame');
    if (appFrame) appFrame.appendChild(panel);
  }

  function clearModuleEntryState() {
    var existing = document.querySelectorAll('.module-entry-state');
    existing.forEach(function(el) { el.remove(); });
    ns._moduleEntryState = null;
  }

  function restartModule(moduleKey) {
    var url = '/api/modules/' + encodeURIComponent(moduleKey) + '/restart';
    return fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' }
    }).then(function(r) { return r.json(); });
  }

  function retryModuleLaunch(appKey, opts, reason) {
    var relaunchOpts = Object.assign({}, opts, { skipHistory: true, forceHealth: true, forceReload: true });
    if (reason === 'watchdog-unavailable') {
      // Server is down — restart the backend module first, then re-launch iframe
      restartModule(appKey).then(function() {
        LauncherRouter._showApp(appKey, relaunchOpts);
      }).catch(function() {
        LauncherRouter._showApp(appKey, relaunchOpts);
      });
    } else {
      // load-timeout or transient error — just re-launch iframe without server restart
      LauncherRouter._showApp(appKey, relaunchOpts);
    }
  }

  function updateActiveModuleCards() {
    document.querySelectorAll('.orbital-card[data-app]').forEach(function(card) {
      card.classList.toggle('active-module-card', card.dataset.app === ns.currentApp);
    });
  }

  function renderRouteRecoveryNotice(pathname) {
    var notice = document.createElement('div');
    notice.className = 'route-recovery-notice';
    notice.textContent = ns._lt(
      'Unknown route: ' + pathname + ' — redirected home.',
      '알 수 없는 경로: ' + pathname + ' — 홈으로 이동했습니다.',
      '不明なルート: ' + pathname + ' — ホームへ移動しました。',
      '未知路由: ' + pathname + ' — 已跳转至首页。',
      '未知路由: ' + pathname + ' — 已跳轉至首頁。',
      'Ruta desconocida: ' + pathname + ' — redirigido al inicio.'
    );
    var landing = document.getElementById('landing');
    if (landing) {
      landing.insertBefore(notice, landing.firstChild);
      setTimeout(function() { if (notice.parentNode) notice.remove(); }, 5000);
    }
  }

  function setDot(id, alive) {
    var el = document.getElementById(id);
    var targetClass = alive ? 'dot alive' : 'dot';
    if (el && el.className !== targetClass) el.className = targetClass;
  }

  function setStatus(id, alive) {
    var el = document.getElementById(id);
    var targetClass = alive ? 'status-indicator alive' : 'status-indicator dead';
    if (el && el.className !== targetClass) el.className = targetClass;
  }

  function _setOrbStatus(id, alive) {
    var el = document.getElementById(id);
    var targetClass = alive ? 'orbital-status alive' : 'orbital-status dead';
    if (el && el.className !== targetClass) el.className = targetClass;
  }


  function scheduleOrbitalLayout() {
    if (ns._orbitalResizeTimer) clearTimeout(ns._orbitalResizeTimer);
    ns._orbitalResizeTimer = setTimeout(initOrbital, 120);
  }

  function activateOnEnterOrSpace(el, action) {
    if (el.dataset.keyboardBound === '1') return;
    el.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        action.call(el, e);
      }
    });
    el.dataset.keyboardBound = '1';
  }

  function initOrbitalAccessibility() {
    document.querySelectorAll('.orbital-card[data-app]').forEach(function(card) {
      if (!card.getAttribute('role')) {
        card.setAttribute('role', 'button');
      }
      activateOnEnterOrSpace(card, function() { card.click(); });
    });

    document.querySelectorAll('.about-book-card').forEach(function(card) {
      activateOnEnterOrSpace(card, function() { card.click(); });
    });

    // landingPoster: only image + hint are clickable (container passes clicks through)
    var posterImg = document.querySelector('#landingPoster img');
    var posterHint = document.querySelector('#landingPoster .poster-hint');
    if (posterImg && typeof ns.openPlatformInfo === 'function') {
      activateOnEnterOrSpace(posterImg, function() { ns.openPlatformInfo(); });
    }
    if (posterHint && typeof ns.openPlatformInfo === 'function') {
      activateOnEnterOrSpace(posterHint, function() { ns.openPlatformInfo(); });
    }
  }

  function initOrbital() {
    var container = document.getElementById('orbitalContainer');
    if (!container) return;
    var cards = container.querySelectorAll('.orbital-card');
    var svg = document.getElementById('orbitalSvg');
    if (!svg) return;

    var rect = container.getBoundingClientRect();
    if (rect.width < 80 || rect.height < 80) {
      container.classList.remove('orbital-ready');
      scheduleOrbitalLayout();
      return;
    }

    var cx = rect.width / 2;
    var cy = rect.height / 2;
    var radius = Math.min(cx, cy) * 0.72;

    svg.innerHTML = '';
    svg.setAttribute('viewBox', '0 0 ' + rect.width + ' ' + rect.height);

    cards.forEach(function(card, i) {
      var angle = parseFloat(card.dataset.angle);
      var rad = (angle - 90) * Math.PI / 180;
      var x = cx + radius * Math.cos(rad);
      var y = cy + radius * Math.sin(rad);

      card.style.setProperty('--orbit-x', x + 'px');
      card.style.setProperty('--orbit-y', y + 'px');

      var pos = _getDetailPosition(angle);
      card.dataset.position = pos;

      var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', cx);
      line.setAttribute('y1', cy);
      line.setAttribute('x2', x);
      line.setAttribute('y2', y);
      line.dataset.index = i;
      line.id = 'orbital-line-' + i;
      svg.appendChild(line);
      card.dataset.lineId = line.id;

      _bindOrbitalCardHover(card);
    });
    container.classList.add('orbital-ready');
  }

  function _ensureOrbitalResizeObserver() {
    if (ns._orbitalResizeObs) return;
    var container = document.getElementById('orbitalContainer');
    if (!container || typeof ResizeObserver === 'undefined') return;
    ns._orbitalResizeObs = new ResizeObserver(function() {
      scheduleOrbitalLayout();
    });
    ns._orbitalResizeObs.observe(container);
  }

  function _clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  var _orbitalTooltipEl = null;

  function _ensureOrbitalTooltipLayer() {
    if (_orbitalTooltipEl) return _orbitalTooltipEl;
    var layer = document.getElementById('orbitalTooltipLayer');
    if (!layer) {
      layer = document.createElement('div');
      layer.id = 'orbitalTooltipLayer';
      layer.className = 'orbital-tooltip-layer';
      layer.setAttribute('aria-hidden', 'true');
      document.body.appendChild(layer);
    }
    _orbitalTooltipEl = document.createElement('div');
    _orbitalTooltipEl.className = 'orbital-detail orbital-detail-flyout';
    _orbitalTooltipEl.setAttribute('role', 'tooltip');
    layer.appendChild(_orbitalTooltipEl);
    return _orbitalTooltipEl;
  }

  function _hideOrbitalTooltip() {
    if (!_orbitalTooltipEl) return;
    _orbitalTooltipEl.classList.remove('visible');
    _orbitalTooltipEl.innerHTML = '';
    _orbitalTooltipEl.style.left = '';
    _orbitalTooltipEl.style.top = '';
    var layer = document.getElementById('orbitalTooltipLayer');
    if (layer) layer.setAttribute('aria-hidden', 'true');
  }

  function _orbitalTopbarOffset() {
    var raw = getComputedStyle(document.documentElement).getPropertyValue('--launcher-topbar-h');
    var parsed = parseInt(raw, 10);
    return isNaN(parsed) ? 48 : parsed;
  }

  function _positionOrbitalTooltip(card, tip) {
    var rect = card.getBoundingClientRect();
    var pos = card.dataset.position || 'bottom';
    var gap = 10;
    var pad = 8;
    var topbar = _orbitalTopbarOffset();
    var vw = window.innerWidth;
    var vh = window.innerHeight;

    tip.classList.remove('visible');
    var tw = tip.offsetWidth;
    var th = tip.offsetHeight;

    var left = 0;
    var top = 0;

    if (pos === 'top') {
      left = rect.left + rect.width / 2 - tw / 2;
      top = rect.top - gap - th;
    } else if (pos === 'bottom') {
      left = rect.left + rect.width / 2 - tw / 2;
      top = rect.bottom + gap;
    } else if (pos === 'right') {
      left = rect.right + gap;
      top = rect.top + rect.height / 2 - th / 2;
    } else {
      left = rect.left - gap - tw;
      top = rect.top + rect.height / 2 - th / 2;
    }

    left = _clamp(left, pad, Math.max(pad, vw - tw - pad));
    top = _clamp(top, topbar + pad, Math.max(topbar + pad, vh - th - pad));

    tip.style.left = left + 'px';
    tip.style.top = top + 'px';
    tip.classList.add('visible');
  }

  function _showOrbitalTooltip(card) {
    if (window.matchMedia('(max-width: 768px)').matches) return;
    var source = card.querySelector('.orbital-detail');
    if (!source) return;
    var tip = _ensureOrbitalTooltipLayer();
    tip.innerHTML = source.innerHTML;
    var layer = document.getElementById('orbitalTooltipLayer');
    if (layer) layer.setAttribute('aria-hidden', 'false');
    _positionOrbitalTooltip(card, tip);
  }

  function _bindOrbitalCardHover(card) {
    if (card.dataset.hoverBound === '1') return;
    card.addEventListener('mouseenter', _handleOrbitalCardMouseEnter);
    card.addEventListener('mouseleave', _handleOrbitalCardMouseLeave);
    card.dataset.hoverBound = '1';
  }

  function _handleOrbitalCardMouseEnter(e) {
    var card = e.currentTarget;
    var line = document.getElementById(card.dataset.lineId);
    if (line) line.classList.add('highlight');
    _showOrbitalTooltip(card);
  }

  function _handleOrbitalCardMouseLeave(e) {
    var card = e.currentTarget;
    var line = document.getElementById(card.dataset.lineId);
    if (line) line.classList.remove('highlight');
    _hideOrbitalTooltip();
  }

  function _getDetailPosition(angle) {
    var a = ((angle % 360) + 360) % 360;
    if (a >= 337 || a < 23) return 'bottom';
    if (a >= 23 && a < 157) return 'right';
    if (a >= 157 && a < 203) return 'bottom';
    return 'left';
  }

  function _updateToggleActive(groupId, activeVal) {
    var grp = document.getElementById(groupId);
    if (!grp) return;
    var opts = grp.querySelectorAll('.dx-toggle-opt');
    for (var i = 0; i < opts.length; i++) {
      if (opts[i].dataset.val === activeVal) opts[i].classList.add('active');
      else opts[i].classList.remove('active');
    }
  }

  function handleDocumentClick(e) {
    var dd = document.getElementById('langToggle');
    if (dd && (!e.target || !dd.contains(e.target))) dd.classList.remove('open');

    var ov = document.getElementById('platformInfoOverlay');
    if (ov && ov.classList.contains('open') && e.target === ov) {
      ns.closePlatformInfo();
    }
  }
  document.addEventListener('click', handleDocumentClick);

  function initHomeClickRouting() {
    var landing = document.getElementById('landing');
    if (!landing || landing.dataset.clickRoutingBound === '1') return;
    landing.addEventListener('click', function(e) {
      var card = e.target.closest('.orbital-card[data-app]');
      if (card && card.dataset.app) {
        e.preventDefault();
        launch(card.dataset.app);
        return;
      }
      var aboutCard = e.target.closest('.about-book-card');
      if (aboutCard) {
        e.preventDefault();
        if (aboutCard.classList.contains('sdk-card')) showSdkLibrary();
        else showAboutView();
      }
    });
    landing.dataset.clickRoutingBound = '1';
  }

  // Core launcher init — must not wait for splash (orbital + routing + health).
  function _initLauncherCore() {
    if (ns._launcherCoreStarted) return;
    ns._launcherCoreStarted = true;
    ns._deferredLauncherWorkStarted = true;
    checkHealth();
    setInterval(checkHealth, 5000);
    initOrbital();
    initOrbitalAccessibility();
    initHomeClickRouting();
    _ensureOrbitalResizeObserver();
    window.addEventListener('resize', scheduleOrbitalLayout);
    window.addEventListener('scroll', _hideOrbitalTooltip, true);
    if (document.readyState === 'complete') {
      scheduleOrbitalLayout();
    } else {
      window.addEventListener('load', scheduleOrbitalLayout, { once: true });
    }
    refreshLauncherChrome();
  }

  ns._initLauncherCore = _initLauncherCore;
  ns._initDeferredLauncherWork = _initLauncherCore;
  ns.ensureStudioReady = ensureStudioReady;
  ns.hideStudioBootGate = hideStudioBootGate;
  ns.showStudioBootGate = showStudioBootGate;
  ns.shouldPlayIntroSplash = shouldPlayIntroSplash;
  ns.isIntroSplashPlaying = isIntroSplashPlaying;
  ns.isLauncherShellPending = isLauncherShellPending;
  ns.isLauncherShellBlocked = isLauncherShellBlocked;
  ns.queueRouteRestore = queueRouteRestore;
  ns.tryCompleteLauncherBoot = tryCompleteLauncherBoot;
  ns.completeLauncherBoot = completeLauncherBoot;

  ns.LauncherRouter = LauncherRouter;
  ns.goHome = goHome;
  ns.showAboutView = showAboutView;
  ns.showSdkLibrary = showSdkLibrary;
  ns.launch = launch;
  ns.updateNavTabs = updateNavTabs;
  ns.checkHealth = checkHealth;
  ns.initOrbital = initOrbital;
  ns.scheduleOrbitalLayout = scheduleOrbitalLayout;
  ns.appFromPath = appFromPath;
  ns.setVisibleView = setVisibleView;
  ns._updateToggleActive = _updateToggleActive;
  ns.resolveModuleHealth = resolveModuleHealth;
  ns.renderModuleLoading = renderModuleLoading;
  ns.renderModuleUnavailable = renderModuleUnavailable;
  ns.clearModuleEntryState = clearModuleEntryState;
  ns.retryModuleLaunch = retryModuleLaunch;
  ns.restartModule = restartModule;
  ns.updateActiveModuleCards = updateActiveModuleCards;
  ns.renderRouteRecoveryNotice = renderRouteRecoveryNotice;
  ns.getActiveAppIframe = getActiveAppIframe;
  ns.broadcastToModuleIframes = broadcastToModuleIframes;
  ns.getOrCreateModuleIframe = getOrCreateModuleIframe;
  ns.loadAppIframeIfNeeded = loadAppIframeIfNeeded;
  ns.refreshLauncherChrome = refreshLauncherChrome;
  ns.resetLauncherUiBlockers = resetLauncherUiBlockers;

  if (typeof DXI18n !== 'undefined' && typeof DXI18n.onLangChange === 'function') {
    DXI18n.onLangChange(function() { refreshLauncherChrome(); });
  }
})();
