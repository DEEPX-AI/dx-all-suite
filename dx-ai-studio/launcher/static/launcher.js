/* Split modules loaded before this file:
 *   launcher-state.js    → window.DXLauncher namespace + shared state
 *   launcher-language.js → language selection, _lt, i18n sync
 *   launcher-splash.js   → splash intro, hero splash, replay
 *   platform-info.js     → platform info overlay open/close
 *   launcher-app-frame.js → router, navigation, health, orbital, app frame
 */

(function() {
  var ns = window.DXLauncher;

  window.initSplashV2 = ns.initSplashV2;
  window.skipSplash = ns.skipSplash;
  window.replaySplash = ns.replaySplash;
  window.showHeroSplash = ns.showHeroSplash;
  window.dismissHeroSplash = ns.dismissHeroSplash;
  window.revealMainContent = ns.revealMainContent;
  window.goHome = ns.goHome;
  window.launch = ns.launch;
  window.showAboutView = ns.showAboutView;
  window.showSdkLibrary = ns.showSdkLibrary;
  window.openPlatformInfo = ns.openPlatformInfo;
  window.closePlatformInfo = ns.closePlatformInfo;
  window.openEcosystemInfo = ns.openEcosystemInfo;
  window.closeEcosystemInfo = ns.closeEcosystemInfo;
  window._lt = ns._lt;
  window.selectLang = ns.selectLang;
  window.toggleLang = ns.toggleLang;
  window._updateLangUI = ns._updateLangUI;
  window._sendToIframe = ns._sendToIframe;
  window.LauncherRouter = ns.LauncherRouter;
  window.updateNavTabs = ns.updateNavTabs;
  window.checkHealth = ns.checkHealth;
  window.initOrbital = ns.initOrbital;
  window.scheduleOrbitalLayout = ns.scheduleOrbitalLayout;
  window.appFromPath = ns.appFromPath;
  window.setVisibleView = ns.setVisibleView;
  window._updateToggleActive = ns._updateToggleActive;

  window.addEventListener('popstate', function() {
    ns.ensureStudioReady().then(function() {
      ns.queueRouteRestore(window.location, { source: 'popstate' });
    });
  });

  document.addEventListener('keydown', function(e) {
    var ov = document.getElementById('splashOverlay');
    if (ov) {
      var isReady = ov.querySelector('.splash-skip.ready');
      if (e.key === 'Enter' || e.key === ' ') {
        ns.skipSplash(isReady ? false : true);
        e.preventDefault();
        return;
      }
      if (e.key === 'Escape') {
        ns.skipSplash(true);
        e.preventDefault();
        return;
      }
    }
    if (e.key === 'Escape') {
      if (ns.currentApp === 'about' && window._aboutHasActivePanel) {
        if (window.closeAboutPanel) window.closeAboutPanel();
      } else if (ns.currentApp === 'about') {
        ns.goHome();
      } else if (ns.currentApp === 'sdk-library' &&
                 ((window._sdkLibHasViewer && window._sdkLibHasViewer()) ||
                  (window._sdkLibHasOverlay && window._sdkLibHasOverlay()))) {
        // SDK handler will close the topmost viewer/overlay via stopImmediatePropagation;
        // do not call goHome so the user stays in SDK Library.
        return;
      } else if (ns.currentApp) {
        ns.goHome();
      }
    }
    if (e.altKey && e.key === '1') { ns.launch('app');    e.preventDefault(); }
    if (e.altKey && e.key === '2') { ns.launch('stream'); e.preventDefault(); }
    if (e.altKey && e.key === '3') { ns.launch('zoo');    e.preventDefault(); }
    if (e.altKey && e.key === '4') { ns.launch('compiler'); e.preventDefault(); }
    if (e.altKey && e.key === '5') { ns.launch('planner');  e.preventDefault(); }
    if (e.altKey && e.key === '6') { ns.launch('benchmark'); e.preventDefault(); }
    if (e.altKey && e.key === '7') { ns.launch('dx_monitor'); e.preventDefault(); }
    if (e.altKey && e.key === '8') { ns.launch('agent'); e.preventDefault(); }
  });

  document.addEventListener('DOMContentLoaded', function() {
    ns.SUPPORTED_LANGS.forEach(function(l) { document.body.classList.remove('lang-' + l); });
    document.body.classList.add('lang-' + ns._lang);
    if (document.documentElement) document.documentElement.lang = ns._lang;
    ns._updateLangUI();

    var playSplash = ns.shouldPlayIntroSplash();
    // #splashOverlay is a static element in index.html. initSplashV2() either plays it
    // (first visit) or removes it (already seen). It MUST run in both cases — otherwise on
    // a return visit the static overlay is never removed, covers the shell, and blocks
    // startWhenShellReady() so the launcher tutorial engine is never created.
    ns.initSplashV2();
    if (playSplash) {
      // No explicit showBootGate: let ensureStudioReady take its splash branch, which
      // conceals the gate under the splash and keeps it for an early skip to re-show.
      ns.ensureStudioReady().then(function() {
        ns.queueRouteRestore(window.location);
      });
      return;
    }

    ns.ensureStudioReady({ showBootGate: true }).then(function() {
      ns.queueRouteRestore(window.location);
    });
  });

  // Restore shell view after bfcache back-navigation (stale JS vs fresh DOM).
  window.addEventListener('pageshow', function(ev) {
    if (!ev.persisted) return;
    ns.ensureStudioReady().then(function() {
      ns.queueRouteRestore(window.location, { source: 'pageshow' });
    });
  });
})();
