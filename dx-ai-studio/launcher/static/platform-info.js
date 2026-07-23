
(function() {
  var ns = window.DXLauncher;

  var PM_LAUNCH_MAP = {
    'pm-dx-app': 'app',
    'pm-dx-stream': 'stream',
    'pm-model-zoo': 'zoo',
    'pm-compiler': 'compiler',
    'pm-edgeguide': 'planner',
    'pm-benchmark': 'benchmark',
    'pm-monitor': 'dx_monitor',
    'pm-agent-dev': 'agent',
    'pm-sdk-library': 'sdk-library',
    'pm-about-deepx': 'about'
  };

  function launchFromPlatformItem(helpId) {
    var target = PM_LAUNCH_MAP[helpId];
    if (!target) return;
    closePlatformInfo();
    if (target === 'about') {
      if (typeof ns.showAboutView === 'function') ns.showAboutView();
      else if (typeof showAboutView === 'function') showAboutView();
      return;
    }
    if (target === 'sdk-library') {
      if (typeof ns.showSdkLibrary === 'function') ns.showSdkLibrary();
      else if (typeof showSdkLibrary === 'function') showSdkLibrary();
      return;
    }
    if (typeof ns.launch === 'function') ns.launch(target);
    else if (typeof launch === 'function') launch(target);
  }

  function initPlatformModuleClicks() {
    document.querySelectorAll('.platform-modules .pm-item[data-help-id]').forEach(function(item) {
      if (item.dataset.pmLaunchBound === '1') return;
      var helpId = item.getAttribute('data-help-id');
      if (!PM_LAUNCH_MAP[helpId]) return;
      if (!item.getAttribute('tabindex')) item.setAttribute('tabindex', '0');
      if (!item.getAttribute('role')) item.setAttribute('role', 'button');
      item.addEventListener('click', function() {
        launchFromPlatformItem(helpId);
      });
      item.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          launchFromPlatformItem(helpId);
        }
      });
      item.dataset.pmLaunchBound = '1';
    });
  }

  var _platformBodyOverflow = null;

  function _lockPlatformBodyScroll() {
    if (_platformBodyOverflow !== null) return;
    _platformBodyOverflow = document.body.style.overflow || '';
    document.body.style.overflow = 'hidden';
  }

  function _unlockPlatformBodyScroll() {
    if (_platformBodyOverflow === null) return;
    document.body.style.overflow = _platformBodyOverflow;
    _platformBodyOverflow = null;
  }

  function openPlatformInfo() {
    var ov = document.getElementById('platformInfoOverlay');
    if (ov) ov.classList.add('open');
    _lockPlatformBodyScroll();
    initPlatformModuleClicks();
  }

  function closePlatformInfo() {
    var ov = document.getElementById('platformInfoOverlay');
    if (ov) ov.classList.remove('open');
    _unlockPlatformBodyScroll();
  }

  function openEcosystemInfo() {
    var ov = document.getElementById('ecosystemOverlay');
    if (ov) ov.classList.add('open');
    _lockPlatformBodyScroll();
  }

  function closeEcosystemInfo() {
    var ov = document.getElementById('ecosystemOverlay');
    if (ov) ov.classList.remove('open');
    _unlockPlatformBodyScroll();
  }

  document.addEventListener('keydown', function(e) {
    if (e.key !== 'Escape') return;
    var pi = document.getElementById('platformInfoOverlay');
    if (pi && pi.classList.contains('open')) {
      closePlatformInfo();
      e.stopPropagation();
      return;
    }
    var eco = document.getElementById('ecosystemOverlay');
    if (eco && eco.classList.contains('open')) {
      closeEcosystemInfo();
      e.stopPropagation();
    }
  });

  // Backdrop click closes the overlay — only when the click lands on the overlay
  // itself (outside the panel), so clicks inside the panel don't dismiss it.
  [['platformInfoOverlay', closePlatformInfo],
   ['ecosystemOverlay', closeEcosystemInfo]].forEach(function(pair) {
    var ov = document.getElementById(pair[0]);
    if (!ov) return;
    ov.addEventListener('click', function(e) {
      if (e.target === ov) pair[1]();
    });
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPlatformModuleClicks);
  } else {
    initPlatformModuleClicks();
  }

  function refreshPlatformInfoLanguage() {
    if (typeof DXI18n !== 'undefined' && typeof DXI18n.applyLang === 'function') {
      var ov = document.getElementById('platformInfoOverlay');
      DXI18n.applyLang(ov || document);
    }
  }

  if (typeof DXI18n !== 'undefined' && typeof DXI18n.onLangChange === 'function') {
    DXI18n.onLangChange(refreshPlatformInfoLanguage);
  }

  ns.openPlatformInfo = openPlatformInfo;
  ns.closePlatformInfo = closePlatformInfo;
  ns.openEcosystemInfo = openEcosystemInfo;
  ns.closeEcosystemInfo = closeEcosystemInfo;
})();
