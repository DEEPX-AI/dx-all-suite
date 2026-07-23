/**
 * DXTutorial.create() — Tutorial 공통 초기화 헬퍼
 *
 * Usage:
 *   window.DXTutorial.create({
 *     appId:           'xxx',
 *     sections:        sections,
 *     referenceDocs:   [...],
 *     toolbarSelector: '.toolbar',
 *     toolbarWrapper:  false,
 *     toolbarInsertBefore: '#id',
 *     getLang:         function(){},
 *     onNav:           function(){},
 *     patchNav:        function(engine){},
 *     setupButtons:    function(engine){},
 *     onComplete:      function(sectionId){}
 *   });
 */
(function () {
  'use strict';

  window.__sharedLangRefreshers = window.__sharedLangRefreshers || [];
  window.registerSharedLangRefresher = function (fn) {
    if (typeof fn === 'function') window.__sharedLangRefreshers.push(fn);
  };
  if (typeof DXI18n !== 'undefined' && typeof DXI18n.onLangChange === 'function') {
    DXI18n.onLangChange(function () {
      window.__sharedLangRefreshers.forEach(function (fn) {
        try { fn(); } catch (e) { console.error('[shared-lang-refresh]', e); }
      });
    });
  }

  window.DXTutorial = {
    create: function (opts) {
      var tutorials = opts.tutorials || null;
      var activeSections = opts.sections || null;

      function _destroyActiveTutorialEngine(keepPrevious) {
        if (window._dxTutorial) {
          if (keepPrevious && window._dxTutorial.appId === 'launcher') {
            if (typeof window._dxTutorial.suspend === 'function') {
              window._dxTutorial.suspend();
            } else if (typeof window._dxTutorial.stop === 'function') {
              window._dxTutorial.stop();
            }
            window._dxTutorialSuspended = window._dxTutorial;
            window._dxTutorial = null;
          } else {
            if (typeof window._dxTutorial.destroy === 'function') {
              window._dxTutorial.destroy();
            } else if (typeof window._dxTutorial.suspend === 'function') {
              window._dxTutorial.suspend();
            } else if (typeof window._dxTutorial.stop === 'function') {
              window._dxTutorial.stop();
            }
            window._dxTutorial = null;
          }
        }
        if (typeof DXTutorialEngine !== 'undefined' &&
            typeof DXTutorialEngine.purgeOrphanChrome === 'function') {
          DXTutorialEngine.purgeOrphanChrome(document, window._dxTutorial || null);
        }
      }

      function _isLauncherShellBlocked() {
        if (document.documentElement.classList.contains('launcher-boot-pending')) return true;
        if (document.getElementById('splashOverlay')) return true;
        // Gate on VISIBLE, not merely present: the gate is concealed (display:none) not
        // removed, so an existence check would block the tutorial forever after conceal.
        var _gate = document.getElementById('studioBootGate');
        if (_gate && getComputedStyle(_gate).display !== 'none') return true;
        if (window.DXLauncher) {
          if (typeof window.DXLauncher.isLauncherShellBlocked === 'function' &&
              window.DXLauncher.isLauncherShellBlocked()) {
            return true;
          }
          if (!window.DXLauncher._studioReadyResolved) return true;
        }
        return false;
      }

      function _scheduleAutoToc(engine) {
        var tutMode = localStorage.getItem('dx-tutorial-mode');
        if (tutMode === 'off') return;  // ON by default — only an explicit "off" opts out
        function openWhenReady(attempts) {
          if (_isLauncherShellBlocked()) {
            if (attempts < 300) {
              setTimeout(function () { openWhenReady(attempts + 1); }, 100);
            }
            return;
          }
          // Launcher, first load with the tutorial on → auto-run the walkthrough so it opens
          // on the "you can turn this off" toggle step. Afterwards (and for module tutorials)
          // just open the table of contents.
          if (engine.appId === 'launcher' &&
              !localStorage.getItem('dx-tutorial-launcher-autostarted')) {
            try { localStorage.setItem('dx-tutorial-launcher-autostarted', '1'); } catch (e) {}
            if (typeof engine.startAll === 'function') { engine.startAll(); return; }
          }
          engine.showTOC();
        }
        setTimeout(function () { openWhenReady(0); }, 500);
      }

      function _orderGlobalFirst(sections) {
        if (!Array.isArray(sections)) return sections;
        var primaryIds = ['global', 'home'];
        for (var pi = 0; pi < primaryIds.length; pi++) {
          var idx = sections.findIndex(function (s) { return s && s.id === primaryIds[pi]; });
          if (idx > 0) {
            var primarySec = sections.splice(idx, 1)[0];
            sections.unshift(primarySec);
            break;
          }
        }
        return sections;
      }

      function _initSingleTutorial(sections, opts) {
        _destroyActiveTutorialEngine(!!opts.keepPreviousEngine);
        var orderedSections = _orderGlobalFirst((sections || []).slice());
        var engine = new DXTutorialEngine({
          appId:    opts.appId,
          sections: orderedSections,
          getLang:  opts.getLang || function () {
            return localStorage.getItem('dx-lang') || 'en';
          },
          onNav:      opts.onNav || function () {},
          onComplete: opts.onComplete || function (sectionId) {
            console.info('[DXTutorial] section complete:', sectionId);
          }
        });

        window._dxTutorial = engine;

        if (typeof opts.setupButtons === 'function') {
          opts.setupButtons(engine);
        } else if (opts.skipButtons) {
          if (typeof DXToolbar !== 'undefined' && typeof DXToolbar.connectTutorial === 'function') {
            DXToolbar.connectTutorial(engine);
          }
        } else {
          var sel = opts.toolbarSelector || '.toolbar';
          var toolbar = typeof sel === 'string' ? document.querySelector(sel) : sel;
          if (toolbar) {
            if (opts.toolbarWrapper) {
              var wrap = document.createElement('div');
              wrap.style.cssText = 'display:flex;gap:8px;align-items:center;margin-left:8px;';
              engine.createToggleBtn(wrap);
              var insertBefore = opts.toolbarInsertBefore
                ? (toolbar.querySelector(opts.toolbarInsertBefore) ||
                   document.querySelector(opts.toolbarInsertBefore))
                : null;
              if (insertBefore) toolbar.insertBefore(wrap, insertBefore);
              else toolbar.appendChild(wrap);
            } else {
              engine.createToggleBtn(toolbar);
            }
          }
        }

        if (typeof opts.patchNav === 'function') {
          opts.patchNav(engine);
        }

        engine.enableKeyboard();
        engine.listenForMessages();

        registerSharedLangRefresher(function () {
          if (engine._tocEl && engine._tocEl.classList.contains('open')) {
            engine._renderTOCContent();
          }
          if (typeof engine._refreshActiveStepLocale === 'function') {
            engine._refreshActiveStepLocale();
          }
        });

        _scheduleAutoToc(engine);

        if (opts.referenceDocs) {
          window._dxRefDocs = opts.referenceDocs;
        }
      }

      function _initMultiTutorial(tutorials, opts) {
        var toolbar = document.querySelector(opts.toolbarSelector || '.toolbar');
        if (!toolbar) return;

        var menuContainer = document.createElement('div');
        menuContainer.className = 'tutorial-menu-container';
        menuContainer.style.position = 'relative';
        menuContainer.style.display = 'inline-block';

        var menuBtn = document.createElement('button');
        menuBtn.className = 'btn-small tutorial-menu-btn';
        menuBtn.innerHTML = '📖 Tutorial ▼';

        var menuDropdown = document.createElement('div');
        menuDropdown.className = 'tutorial-menu-dropdown';
        menuDropdown.style.display = 'none';

        tutorials.forEach(function(tut) {
          var item = document.createElement('div');
          item.className = 'tutorial-menu-item';
          item.textContent = (tut.icon || '') + ' ' + tut.name;
          item.addEventListener('click', function() {
            menuDropdown.style.display = 'none';
            _startTutorial(tut, opts);
          });
          menuDropdown.appendChild(item);
        });

        menuBtn.addEventListener('click', function(e) {
          e.stopPropagation();
          var isOpen = menuDropdown.style.display !== 'none';
          menuDropdown.style.display = isOpen ? 'none' : 'block';
        });
        document.addEventListener('click', function() {
          menuDropdown.style.display = 'none';
        });

        menuContainer.appendChild(menuBtn);
        menuContainer.appendChild(menuDropdown);
        toolbar.appendChild(menuContainer);
      }

      function _startTutorial(tut, opts) {
        _destroyActiveTutorialEngine();
        var engine = new DXTutorialEngine({
          appId: opts.appId,
          sections: _orderGlobalFirst((tut.sections || []).slice()),
          getLang: opts.getLang,
          onNav: opts.onNav,
          onComplete: opts.onComplete,
        });
        window._dxTutorial = engine;

        if (typeof opts.patchNav === 'function') {
          opts.patchNav(engine);
        }

        engine.enableKeyboard();
        engine.listenForMessages();
        engine.showTOC();
      }

      function _doInit() {
        setTimeout(function () {
          if (typeof DXTutorialEngine === 'undefined') {
            console.error('[DXTutorial] DXTutorialEngine not loaded');
            return;
          }

          if (tutorials) {
            _initMultiTutorial(tutorials, opts);
          } else if (activeSections) {
            _initSingleTutorial(activeSections, opts);
          }
        }, 200);
      }

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', _doInit);
      } else {
        _doInit();
      }
    }
  };
})();
