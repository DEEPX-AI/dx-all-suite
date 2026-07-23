class DXTutorialEngine {
  static _UI = {
    'Tutorial Guide': { ko: '튜토리얼 가이드', ja: 'チュートリアルガイド', 'zh-CN': '教程指南', 'zh-TW': '教學指南',es:'Guía tutorial'},
    'Complete': { ko: '완료', ja: '完了', 'zh-CN': '完成', 'zh-TW': '完成',es:'Completo'},
    'steps': { ko: '단계', ja: 'ステップ', 'zh-CN': '步骤', 'zh-TW': '步驟',es:'pasos'},
    'Start from Beginning': { ko: '처음부터 시작', ja: '最初から開始', 'zh-CN': '从头开始', 'zh-TW': '從頭開始',es:'Iniciar desde el principio'},
    'Reset': { ko: '초기화', ja: 'リセット', 'zh-CN': '重置', 'zh-TW': '重置',es:'Restablecer'},
    'Prerequisites Required': { ko: '선행 학습 필요', ja: '前提条件が必要', 'zh-CN': '需要先修内容', 'zh-TW': '需要先修內容',es:'Requisitos previos necesarios'},
    'Proceed Anyway': { ko: '계속 진행', ja: 'そのまま続行', 'zh-CN': '仍然继续', 'zh-TW': '仍然繼續',es:'Continuar de todos modos'},
    'Cancel': { ko: '취소', ja: 'キャンセル', 'zh-CN': '取消', 'zh-TW': '取消',es:'Cancelar'},
    'Prev': { ko: '이전', ja: '前へ', 'zh-CN': '上一步', 'zh-TW': '上一步',es:'Anterior'},
    'Skip': { ko: '건너뛰기', ja: 'スキップ', 'zh-CN': '跳过', 'zh-TW': '跳過',es:'Omitir'},
    'Next': { ko: '다음', ja: '次へ', 'zh-CN': '下一步', 'zh-TW': '下一步',es:'Siguiente'},
    'Done': { ko: '완료', ja: '完了', 'zh-CN': '完成', 'zh-TW': '完成',es:'Hecho'},
    'Section Complete!': { ko: '섹션 완료!', ja: 'セクション完了！', 'zh-CN': '章节完成！', 'zh-TW': '章節完成！',es:'¡Sección completa!'},
    'Tutorial Complete!': { ko: '튜토리얼 완료!', ja: 'チュートリアル完了！', 'zh-CN': '教程完成！', 'zh-TW': '教學完成！', es: '¡Tutorial completo!' },
    'Continue': { ko: '계속', ja: '続行', 'zh-CN': '继续', 'zh-TW': '繼續',es:'Continuar'},
    'List': { ko: '목록', ja: '一覧', 'zh-CN': '列表', 'zh-TW': '列表',es:'Lista'},
    'Please complete first': { ko: '이 튜토리얼을 시작하기 전에 다음을 먼저 완료하세요:', ja: '始める前に以下を完了してください:', 'zh-CN': '请先完成以下内容:', 'zh-TW': '請先完成以下內容:',es:'Por favor complete primero'},
    'Section done msg': { ko: '이 섹션의 모든 단계를 완료했습니다!', ja: 'このセクションのすべてのステップが完了しました！', 'zh-CN': '已完成本章节的所有步骤！', 'zh-TW': '已完成本章節的所有步驟！',es:'Mensaje de sección completada'},
    'tutorial complete!': { ko: '튜토리얼 완료!', ja: 'チュートリアル完了！', 'zh-CN': '教程完成！', 'zh-TW': '教學完成！',es:'¡tutorial completo!'},
    'Close': { ko: '닫기', ja: '閉じる', 'zh-CN': '关闭', 'zh-TW': '關閉',es:'Cerrar'},
    'Help Mode': { ko: '도움말 모드', ja: 'ヘルプモード', 'zh-CN': '帮助模式', 'zh-TW': '說明模式',es:'Modo de ayuda'},
    'Confirm Reset': { ko: '초기화 확인', ja: 'リセットの確認', 'zh-CN': '确认重置', 'zh-TW': '確認重置',es:'Confirmar restablecimiento'},
    'Reset all progress?': { ko: '진행 상태를 초기화할까요?', ja: 'すべての進捗をリセットしますか？', 'zh-CN': '确定要重置所有进度吗？', 'zh-TW': '確定要重置所有進度嗎？',es:'¿Restablecer todo el progreso?'},
    'Screen Help': { ko: '화면 도움말', ja: '画面ヘルプ', 'zh-CN': '屏幕帮助', 'zh-TW': '畫面說明',es:'Ayuda de pantalla'},
    'No help items': { ko: '이 화면에 등록된 도움말이 없습니다.', ja: 'この画面にはヘルプ項目がありません。', 'zh-CN': '此屏幕没有帮助项目。', 'zh-TW': '此畫面沒有說明項目。',es:'Sin elementos de ayuda'},
    'Not available': { ko: '현재 사용 불가', ja: '現在利用不可', 'zh-CN': '当前不可用', 'zh-TW': '目前不可用',es:'No disponible'},
    'Missing target': { ko: '대상 요소 누락', ja: '対象要素が見つかりません', 'zh-CN': '目标元素缺失', 'zh-TW': '目標元素遺失',es:'Objetivo faltante'},
    'visible': { ko: '표시', ja: '表示', 'zh-CN': '可见', 'zh-TW': '可見',es:'visible'},
    'conditional': { ko: '조건부', ja: '条件付き', 'zh-CN': '条件', 'zh-TW': '條件',es:'condicional'},
    'warning': { ko: '경고', ja: '警告', 'zh-CN': '警告', 'zh-TW': '警告',es:'advertencia'},
  };

  _tl(key) {
    const lang = this.getLang();
    if (lang === 'en') return key;
    const entry = DXTutorialEngine._UI[key];
    return (entry && entry[lang]) || key;
  }

  constructor(opts = {}) {
    this.options      = opts || {};
    this.appId        = opts.appId || 'app';
    this.sections     = opts.sections || [];
    this.getLang      = opts.getLang || (() => localStorage.getItem('dx-lang') || 'en');
    this.onNav        = opts.onNav || (() => {});
    this.onComplete   = opts.onComplete || (() => {});

    this._curSection  = null;
    this._curStep     = 0;
    this._stepToken   = 0;  // race condition 방지용 토큰
    this._spotlight   = null;
    this._overlay     = null;
    this._tooltip     = null;
    this._tocEl       = null;
    this._tocBackdrop = null;
    this._built       = false;

    this._STORAGE_KEY = 'dx-tutorial-progress';
    this._progress    = this._loadProgress();

    this._resizeHandler = () => {
      if (this._rafScrollPending) return;
      this._rafScrollPending = true;
      requestAnimationFrame(() => {
        this._rafScrollPending = false;
        if (this._curSection) this._refreshHighlight();
      });
    };
    this._scrollHandler = () => {
      if (this._rafScrollPending) return;
      this._rafScrollPending = true;
      requestAnimationFrame(() => {
        this._rafScrollPending = false;
        if (this._curSection) this._refreshHighlight();
      });
    };
    this._rafScrollPending = false;
    this._keyHandler = null;
    this._messageHandler = null;
  }

  /** Resolve a step/help target in the current document or an active launcher iframe. */
  _queryTarget(selector) {
    if (!selector) return null;
    var pickVisible = function(root) {
      if (!root) return null;
      var list = root.querySelectorAll(selector);
      for (var i = 0; i < list.length; i++) {
        var node = list[i];
        if (node.tagName === 'DIALOG' && !node.open) continue;
        var style = window.getComputedStyle(node);
        if (style.display === 'none' || style.visibility === 'hidden') continue;
        var r = node.getBoundingClientRect();
        if (r.width > 0 || r.height > 0) return node;
      }
      return null;
    };
    var el = pickVisible(document);
    if (el) return el;
    var pool = document.getElementById('appIframePool');
    if (!pool) return null;
    var iframes = pool.querySelectorAll('iframe');
    for (var i = 0; i < iframes.length; i++) {
      var frame = iframes[i];
      if (!frame || frame.offsetParent === null) continue;
      var doc = null;
      try { doc = frame.contentDocument; } catch (e) { doc = null; }
      if (!doc) continue;
      el = pickVisible(doc);
      if (el) return el;
    }
    return null;
  }

  _t(obj) {
    if (!obj) return '';
    if (typeof obj === 'string') return obj;
    return obj[this.getLang()] || obj.en || obj.ko || '';
  }

  _loadProgress() {
    try {
      const raw = localStorage.getItem(this._STORAGE_KEY);
      const p = raw ? JSON.parse(raw) : {};
      if (!p[this.appId]) p[this.appId] = { completed: [], steps: {} };
      return p;
    } catch (e) { return { [this.appId]: { completed: [], steps: {} } }; }
  }

  _saveProgress() {
    try { localStorage.setItem(this._STORAGE_KEY, JSON.stringify(this._progress)); } catch (e) {}
  }

  _appProgress() { return this._progress[this.appId]; }
  isSectionComplete(id) { return this._appProgress().completed.includes(id); }

  getCompletionPercent() {
    const total = this.sections.filter(s => !s.helpOnly).length;
    if (!total) return 0;
    return Math.round(this._appProgress().completed.length / total * 100);
  }

  resetProgress() {
    this._progress[this.appId] = { completed: [], steps: {} };
    this._saveProgress();
    if (this._tocEl) this._renderTOCContent();
  }

  _markStepDone(sectionId, stepIdx) {
    const ap = this._appProgress();
    if (!ap.steps[sectionId]) ap.steps[sectionId] = [];
    if (!ap.steps[sectionId].includes(stepIdx)) ap.steps[sectionId].push(stepIdx);
    const sec = this.sections.find(s => s.id === sectionId);
    if (sec && ap.steps[sectionId].length >= sec.steps.length) {
      if (!ap.completed.includes(sectionId)) {
        ap.completed.push(sectionId);
        this.onComplete(sectionId);
      }
    }
    this._saveProgress();
  }

  _checkPrereq(section) {
    if (!section.prerequisite) return null;
    const prereqs = Array.isArray(section.prerequisite) ? section.prerequisite : [section.prerequisite];
    const missing = prereqs.filter(pid => !this.isSectionComplete(pid));
    if (!missing.length) return null;
    const names = missing.map(pid => {
      const s = this.sections.find(x => x.id === pid);
      return s ? this._t(s.title) : pid;
    });
    if (section.prerequisiteMessage) return this._t(section.prerequisiteMessage);
    return this._tl('Please complete first') + '\n• ' + names.join('\n• ');
  }

  /** CSS zoom on body (audit + Ctrl+scroll); 1 when unset. */
  _layoutZoom(doc) {
    doc = doc || document;
    if (!doc.body) return 1;
    var z = parseFloat(doc.body.style.zoom);
    return (z > 0 && isFinite(z)) ? z : 1;
  }

  /** Mount tour chrome on <html> — fixed inside zoomed body misaligns at body.style.zoom≠1. */
  _overlayRoot() {
    return document.documentElement;
  }

  /** Map a target element's box to the engine document viewport (handles iframe embeds). */
  _viewportRect(el) {
    if (!el || !el.getBoundingClientRect) return null;
    var rect = el.getBoundingClientRect();
    var doc = el.ownerDocument;
    if (!doc || doc === document) return rect;
    var pool = document.getElementById('appIframePool');
    if (!pool) return rect;
    var frames = pool.querySelectorAll('iframe');
    for (var i = 0; i < frames.length; i++) {
      var frame = frames[i];
      try {
        if (frame.contentDocument === doc) {
          var fr = frame.getBoundingClientRect();
          return {
            top: rect.top + fr.top,
            left: rect.left + fr.left,
            right: rect.right + fr.left,
            bottom: rect.bottom + fr.top,
            width: rect.width,
            height: rect.height,
            x: rect.x + fr.left,
            y: rect.y + fr.top
          };
        }
      } catch (e) { /* cross-origin */ }
    }
    return rect;
  }

  _spotlightPad() { return 8; }

  _applySpotlightBox(el) {
    var rect = this._viewportRect(el);
    if (!rect) return;
    var pad = this._spotlightPad();
    this._spotlight.style.transition = 'none';
    this._spotlight.style.top = (rect.top - pad) + 'px';
    this._spotlight.style.left = (rect.left - pad) + 'px';
    this._spotlight.style.width = (rect.width + pad * 2) + 'px';
    this._spotlight.style.height = (rect.height + pad * 2) + 'px';
    this._spotlight.classList.add('active');
    var self = this;
    requestAnimationFrame(function() {
      if (self._spotlight) self._spotlight.style.transition = '';
    });
  }

  _bindScrollRootsFor(el) {
    if (!el || !el.parentElement) return;
    var seen = this._scrollRootSeen || (this._scrollRootSeen = new WeakSet());
    var node = el;
    while (node && node !== document.documentElement) {
      if (node.nodeType === 1) {
        var style = window.getComputedStyle(node);
        var scrollable = /auto|scroll|overlay/.test(style.overflow + style.overflowY + style.overflowX);
        if (scrollable && !seen.has(node)) {
          seen.add(node);
          node.addEventListener('scroll', this._scrollHandler, { passive: true });
        }
      }
      node = node.parentElement;
    }
  }

  _buildDOM() {
    if (this._built) {
      if (this._overlay && document.documentElement.contains(this._overlay)) return;
      this._detachChromeRefs();
    }
    this._built = true;

    var root = this._overlayRoot();

    this._overlay = document.createElement('div');
    this._overlay.className = 'dxt-overlay';
    this._overlay.addEventListener('click', () => this.stop());
    root.appendChild(this._overlay);

    this._spotlight = document.createElement('div');
    this._spotlight.className = 'dxt-spotlight';
    root.appendChild(this._spotlight);

    this._tooltip = document.createElement('div');
    this._tooltip.className = 'dxt-tooltip';
    root.appendChild(this._tooltip);

    // TOC backdrop (click outside = close TOC) — FIX: was missing
    this._tocBackdrop = document.createElement('div');
    this._tocBackdrop.className = 'dxt-toc-backdrop';
    this._tocBackdrop.addEventListener('click', () => this.hideTOC());
    root.appendChild(this._tocBackdrop);

    this._tocEl = document.createElement('div');
    this._tocEl.className = 'dxt-toc';
    root.appendChild(this._tocEl);

    const _onScroll = () => { if (this._curSection) this._refreshHighlight(); };
    window.addEventListener('scroll', _onScroll, { passive: true });
    ['main-content', 'main-area'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('scroll', _onScroll, { passive: true });
    });
    document.querySelectorAll('[style*="overflow"]').forEach(el => {
      el.addEventListener('scroll', _onScroll, { passive: true });
    });
  }

  showTOC(retryCount) {
    if (retryCount === undefined) retryCount = 0;
    if (window.DXLauncher &&
        typeof window.DXLauncher.isLauncherShellBlocked === 'function' &&
        window.DXLauncher.isLauncherShellBlocked()) {
      if (retryCount < 300) {
        var self = this;
        setTimeout(function() { self.showTOC(retryCount + 1); }, 100);
      }
      return;
    }
    this._buildDOM();
    this._renderTOCContent();
    this._tocEl.classList.add('open');
    this._tocBackdrop.classList.add('open');
  }

  hideTOC() {
    if (this._tocEl) this._tocEl.classList.remove('open');
    if (this._tocBackdrop) this._tocBackdrop.classList.remove('open');
    this._resetToolbarScroll();
  }

  /** scrollIntoView() on a step target inside the (scrollable) shared toolbar can leave the
   *  toolbar horizontally scrolled after the tour/TOC closes. Snap any .dx-toolbar back to 0. */
  _resetToolbarScroll() {
    var bars = document.querySelectorAll('.dx-toolbar');
    for (var i = 0; i < bars.length; i++) bars[i].scrollLeft = 0;
  }

  toggleTOC() {
    if (this._tocEl && this._tocEl.classList.contains('open')) this.hideTOC();
    else this.showTOC();
  }

  _renderTOCContent() {
    const lang = this.getLang();
    const pct = this.getCompletionPercent();
    const tutSecs = this.sections.filter(s => !s.helpOnly);

    let html = '<div class="dxt-toc-header">' +
      '<div class="dxt-toc-title">\uD83C\uDF93 ' + this._tl('Tutorial Guide') + '</div>' +
      '<button class="dxt-toc-close" onclick="window._dxTutorial.hideTOC()">\u2715</button>' +
      '</div>' +
      '<div class="dxt-toc-progress">' +
      '<div class="dxt-toc-pbar"><div class="dxt-toc-pfill" style="width:' + pct + '%"></div></div>' +
      '<span class="dxt-toc-ppct">' + pct + '% ' + this._tl('Complete') + '</span>' +
      '</div><div class="dxt-toc-sections">';

    tutSecs.forEach(function(sec) {
      var done = this.isSectionComplete(sec.id);
      var stepsDone = (this._appProgress().steps[sec.id] || []).length;
      var stepsTotal = sec.steps.length;
      var hasPrereq = !!this._checkPrereq(sec);
      html += '<div class="dxt-toc-item ' + (done ? 'done' : '') + ' ' + (hasPrereq ? 'has-prereq' : '') + '"' +
        ' onclick="window._dxTutorial.startSection(\'' + sec.id + '\')">' +
        '<span class="dxt-toc-icon">' + (sec.icon || '\uD83D\uDCC4') + '</span>' +
        '<div class="dxt-toc-info">' +
        '<div class="dxt-toc-name">' + this._t(sec.title) + '</div>' +
        '<div class="dxt-toc-desc">' + (this._t(sec.description) || '') + '</div>' +
        '<div class="dxt-toc-meta">' + stepsDone + '/' + stepsTotal + ' ' + this._tl('steps') + '</div>' +
        '</div>' +
        '<span class="dxt-toc-check">' + (done ? '\u2705' : hasPrereq ? '\uD83D\uDD12' : '\u25CB') + '</span>' +
        '</div>';
    }.bind(this));

    html += '</div><div class="dxt-toc-footer">' +
      '<button class="dxt-toc-btn dxt-toc-btn-start" onclick="window._dxTutorial.startAll()">\u25B6 ' + this._tl('Start from Beginning') + '</button>' +
      '<button class="dxt-toc-btn dxt-toc-btn-reset" onclick="window._dxTutorial._confirmReset()">\uD83D\uDD04 ' + this._tl('Reset') + '</button>' +
      '</div>';

    this._tocEl.innerHTML = html;
  }

  startAll() {
    this.hideTOC();
    var tutSecs = this.sections.filter(s => !s.helpOnly);
    var first = tutSecs.find(s => !this.isSectionComplete(s.id)) || tutSecs[0];
    if (first) this.startSection(first.id);
  }

  async startSection(sectionId) {
    var sec = this.sections.find(s => s.id === sectionId);
    if (!sec || sec.helpOnly) return;
    // Jumping to another section (e.g. via the TOC) without running the current step's
    // afterStep leaks that step's chrome (pins, mock dialogs, raised z-index). Run it first.
    if (this._curSection && this._curSection !== sec &&
        this._curSection.steps && this._curSection.steps[this._curStep]) {
      this._invokeAfterStep(this._curSection.steps[this._curStep]);
    }
    this._buildDOM();

    var prereqMsg = this._checkPrereq(sec);
    if (prereqMsg) {
      var lang = this.getLang();
      var proceed = await this._showConfirmModal(
        '⚠️ ' + this._tl('Prerequisites Required'),
        prereqMsg,
        [
          { label: this._tl('Proceed Anyway'), value: true },
          { label: this._tl('Cancel'), value: false }
        ]
      );
      if (!proceed) return;
    }

    this.hideTOC();
    this._curSection = sec;
    this._curStep = 0;

    if (sec.beforeStart) {
      var bsResult = sec.beforeStart();
      if (bsResult && typeof bsResult.then === 'function') await bsResult;
    }

    this._overlay.classList.add('active');
    window.addEventListener('resize', this._resizeHandler);
    window.addEventListener('scroll', this._scrollHandler, true);

    setTimeout(() => this._showStep(), 400);
  }

  async _showStep() {
    if (!this._curSection) return;
    var token = ++this._stepToken; // 각 호출마다 고유 토큰 — 이전 폴링 중단용
    var steps = this._curSection.steps;
    var step = steps[this._curStep];
    if (!step) { this.stop(); return; }

    if (step.beforeStep) {
      var beforeResult = step.beforeStep.call(step);
      if (beforeResult && typeof beforeResult.then === 'function') {
        await beforeResult;
      }
    }
    await new Promise(r => setTimeout(r, step.beforeStep ? 150 : 80));

    // 폴링/대기 중에 stop()이나 다른 _showStep이 호출됐으면 중단
    if (this._stepToken !== token || !this._curSection) return;

    this._closeTransientUiChrome();

    var target = step.target ? this._queryTarget(step.target) : null;

    // Poll for target to appear and become visible (max ~2s)
    // <dialog> elements: visible only when open attribute is present
    if (step.target) {
      var _isVisible = function(el) {
        if (!el) return false;
        if (el.tagName === 'DIALOG' && !el.open) return false;
        var r = el.getBoundingClientRect();
        return r.width > 0 || r.height > 0;
      };
      var _vis = _isVisible(target);
      if (!_vis) {
        for (var _pw = 0; _pw < 20; _pw++) {
          await new Promise(function(r) { setTimeout(r, 100); });
          if (this._stepToken !== token || !this._curSection) return; // 중간에 중단됐으면 종료
          target = this._queryTarget(step.target);
          if (_isVisible(target)) { _vis = true; break; }
        }
        if (!_vis) {
          console.warn('[DXTutorial] target not found/visible after polling:', step.target, '→ floating tooltip');
          target = null;
        }
      }
    }

    if (this._stepToken !== token || !this._curSection) return; // 렌더링 전 최종 체크

    if (target) {
      this._bindScrollRootsFor(target);
      var rect = this._viewportRect(target);
      var inView = rect && rect.top >= 60 && rect.bottom <= (window.innerHeight - 20);
      if (!inView && !step.skipScroll) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        await new Promise(r => setTimeout(r, 450));
        if (this._stepToken !== token || !this._curSection) return;
      }
      this._applySpotlightBox(target);
      this._renderTooltip(step, target);
    } else {
      this._spotlight.classList.remove('active');
      this._renderTooltipFloating(step);
    }
    this._markStepDone(this._curSection.id, this._curStep);
  }

  _highlightElement(el) {
    var rect = this._viewportRect(el);
    var needsScroll = rect.top < 60 || rect.bottom > window.innerHeight - 20;

    if (needsScroll) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      var self = this;
      setTimeout(function() {
        if (!self._curSection) return;
        self._applySpotlightBox(el);
        self._positionTooltip(el);
      }, 500);
    } else {
      this._applySpotlightBox(el);
    }
  }

  _refreshHighlight() {
    if (!this._curSection) return;
    var step = this._curSection.steps[this._curStep];
    if (!step) return;
    var target = step.target ? this._queryTarget(step.target) : null;
    if (target) {
      this._applySpotlightBox(target);
      this._positionTooltip(target);
    }
  }

  /** Re-render active tutorial/help copy after locale switch (no beforeStep replay). */
  _refreshActiveStepLocale() {
    if (this._curSection) {
      var step = this._curSection.steps[this._curStep];
      if (!step) return;
      var target = step.target ? this._queryTarget(step.target) : null;
      if (target) {
        this._renderTooltip(step, target);
      } else {
        this._renderTooltipFloating(step);
      }
    }
  }

  _renderTooltip(step, target) {
    var lang = this.getLang();
    var steps = this._curSection.steps;
    var isFirst = this._curStep === 0;
    var isLast = this._curStep === steps.length - 1;

    this._tooltip.innerHTML =
      '<div class="dxt-tip-header">' +
      '<span class="dxt-tip-counter">' + (this._curStep + 1) + ' / ' + steps.length + '</span>' +
      '<span class="dxt-tip-section">' + this._t(this._curSection.title) + '</span>' +
      '<button class="dxt-tip-close" onclick="window._dxTutorial.stop()">\u2715</button>' +
      '</div>' +
      '<div class="dxt-tip-title">' + this._t(step.title) + '</div>' +
      '<div class="dxt-tip-body">' + this._t(step.content) + '</div>' +
      '<div class="dxt-tip-nav">' +
      '<button class="dxt-tip-btn dxt-tip-prev" ' + (isFirst ? 'disabled' : '') + ' onclick="window._dxTutorial.prev()">\u2190 ' + this._tl('Prev') + '</button>' +
      '<button class="dxt-tip-btn dxt-tip-skip" onclick="window._dxTutorial.stop()">' + this._tl('Skip') + '</button>' +
      '<button class="dxt-tip-btn dxt-tip-next" onclick="window._dxTutorial.next()">' + (isLast ? (this._tl('Done') + ' \u2713') : (this._tl('Next') + ' \u2192')) + '</button>' +
      '</div>';
    this._tooltip.classList.add('active');
    this._positionTooltip(target);
  }

  _renderTooltipFloating(step) {
    if (!this._curSection) return; // stop() 이후 호출 방지
    var lang = this.getLang();
    var steps = this._curSection.steps;
    var isFirst = this._curStep === 0;
    var isLast = this._curStep === steps.length - 1;

    this._tooltip.innerHTML =
      '<div class="dxt-tip-header">' +
      '<span class="dxt-tip-counter">' + (this._curStep + 1) + ' / ' + steps.length + '</span>' +
      '<span class="dxt-tip-section">' + this._t(this._curSection.title) + '</span>' +
      '<button class="dxt-tip-close" onclick="window._dxTutorial.stop()">\u2715</button>' +
      '</div>' +
      '<div class="dxt-tip-title">' + this._t(step.title) + '</div>' +
      '<div class="dxt-tip-body">' + this._t(step.content) + '</div>' +
      '<div class="dxt-tip-nav">' +
      '<button class="dxt-tip-btn dxt-tip-prev" ' + (isFirst ? 'disabled' : '') + ' onclick="window._dxTutorial.prev()">\u2190 ' + this._tl('Prev') + '</button>' +
      '<button class="dxt-tip-btn dxt-tip-skip" onclick="window._dxTutorial.stop()">' + this._tl('Skip') + '</button>' +
      '<button class="dxt-tip-btn dxt-tip-next" onclick="window._dxTutorial.next()">' + (isLast ? (this._tl('Done') + ' \u2713') : (this._tl('Next') + ' \u2192')) + '</button>' +
      '</div>';
    this._tooltip.classList.add('active');
    this._tooltip.style.position = 'fixed';
    this._tooltip.style.top = '50%';
    this._tooltip.style.left = '50%';
    this._tooltip.style.transform = 'translate(-50%, -50%)';
    this._tooltip.setAttribute('data-dxt-floating', '1');
    this._tooltip.removeAttribute('data-pos');
  }

  _positionTooltip(target) {
    var tip = this._tooltip;
    tip.removeAttribute('data-dxt-floating');
    var rect = this._viewportRect(target);
    tip.style.position = 'fixed';
    tip.style.transform = 'none';

    // Force layout pass
    tip.style.visibility = 'hidden';
    tip.style.display = 'block';
    var tipRect = tip.getBoundingClientRect();
    tip.style.visibility = '';

    var margin = 16;
    var step = this._curSection.steps[this._curStep];
    var pos = (step && step.position) || 'auto';
    var chosen = pos;

    if (pos === 'auto') {
      var below = window.innerHeight - rect.bottom;
      var above = rect.top;
      var right = window.innerWidth - rect.right;
      var left = rect.left;
      if (below >= tipRect.height + margin) chosen = 'bottom';
      else if (above >= tipRect.height + margin) chosen = 'top';
      else if (right >= tipRect.width + margin) chosen = 'right';
      else if (left >= tipRect.width + margin) chosen = 'left';
      else chosen = 'bottom';
    }

    tip.setAttribute('data-pos', chosen);

    var clampX = function(x) { return Math.max(8, Math.min(x, window.innerWidth - tipRect.width - 8)); };
    var clampY = function(y) { return Math.max(8, Math.min(y, window.innerHeight - tipRect.height - 8)); };

    var place = function(pos) {
      switch (pos) {
        case 'bottom':
          tip.style.top = (rect.bottom + margin) + 'px';
          tip.style.left = (rect.left + rect.width / 2 - tipRect.width / 2) + 'px';
          break;
        case 'top':
          tip.style.top = (rect.top - tipRect.height - margin) + 'px';
          tip.style.left = (rect.left + rect.width / 2 - tipRect.width / 2) + 'px';
          break;
        case 'right':
          tip.style.top = (rect.top + rect.height / 2 - tipRect.height / 2) + 'px';
          tip.style.left = (rect.right + margin) + 'px';
          break;
        case 'left':
          tip.style.top = (rect.top + rect.height / 2 - tipRect.height / 2) + 'px';
          tip.style.left = (rect.left - tipRect.width - margin) + 'px';
          break;
      }
      tip.style.top = clampY(parseFloat(tip.style.top)) + 'px';
      tip.style.left = clampX(parseFloat(tip.style.left)) + 'px';
    };

    place(chosen);

    // Try alternate sides until tooltip fits (explicit position + auto)
    var flip = { bottom: 'top', top: 'bottom', right: 'left', left: 'right' };
    var tryOrder = pos === 'auto'
      ? ['bottom', 'top', 'right', 'left']
      : [pos, flip[pos], flip[flip[pos]], flip[flip[flip[pos]]]].filter(function(v, i, a) {
          return v && a.indexOf(v) === i;
        });
    for (var ti = 0; ti < tryOrder.length; ti++) {
      chosen = tryOrder[ti];
      tip.setAttribute('data-pos', chosen);
      place(chosen);
      var tr2 = tip.getBoundingClientRect();
      var clipped = tr2.top < 4 || tr2.left < 4
        || tr2.bottom > window.innerHeight - 4
        || tr2.right > window.innerWidth - 4;
      if (!clipped) break;
    }
  }

  _hideStepChrome() {
    if (this._spotlight) this._spotlight.classList.remove('active');
    if (this._tooltip) {
      this._tooltip.classList.remove('active');
      this._tooltip.style.top = '';
      this._tooltip.style.left = '';
      this._tooltip.style.transform = '';
      this._tooltip.removeAttribute('data-dxt-floating');
      this._tooltip.removeAttribute('data-pos');
    }
  }

  _invokeAfterStep(step) {
    if (!step || typeof step.afterStep !== 'function') return;
    try {
      step.afterStep.call(step);
    } catch (err) {
      console.warn('[DXTutorial] afterStep failed:', err);
    }
  }

  _closeTransientUiChrome() {
    document.querySelectorAll('.dx-lang-dropdown.open').forEach(function(wrap) {
      wrap.classList.remove('open');
      var menu = wrap.querySelector('.dx-lang-menu');
      if (menu) {
        menu.style.display = '';
        menu.style.position = '';
        menu.style.top = '';
        menu.style.left = '';
        menu.style.right = '';
        menu.style.zIndex = '';
      }
    });
  }

  _activateConfirmPrimary() {
    var primary = document.querySelector('.dxt-confirm-overlay .dxt-confirm-btn.primary') ||
      document.querySelector('.dxt-confirm-overlay .dxt-confirm-btn');
    if (primary) primary.click();
  }

  async next() {
    if (!this._curSection) return;
    if (document.querySelector('.dxt-confirm-overlay')) return;
    var secId = this._curSection.id;
    var steps = this._curSection.steps;
    var currentStep = steps[this._curStep];
    if (this._curStep < steps.length - 1) {
      this._invokeAfterStep(currentStep);
      this._curStep++;
      this._showStep();
    } else {
      this._invokeAfterStep(currentStep);
      var lang = this.getLang();
      var tutSecs = this.sections.filter(s => !s.helpOnly);
      var idx = tutSecs.findIndex(s => s.id === secId);
      var curSec = tutSecs[idx];
      this._hideStepChrome();
      window.removeEventListener('resize', this._resizeHandler);
      window.removeEventListener('scroll', this._scrollHandler, true);

      var action = null;
      if (idx >= 0 && idx < tutSecs.length - 1) {
        var nextSec = tutSecs[idx + 1];
        action = await this._showConfirmModal(
          '✅ ' + this._tl('Section Complete!'),
          '"' + this._t(curSec.title) + '" ' + this._tl('Complete') + '!\n' +
            (lang === 'en' ? 'Next: ' : this._tl('Next') + ': ') + this._t(nextSec.title),
          [
            { label: '▶ ' + this._tl('Continue'), value: 'continue', primary: true },
            { label: '📋 ' + this._tl('List'), value: 'toc' },
            { label: '✕ ' + this._tl('Close'), value: 'close' }
          ]
        );
        this._curSection = null;
        this._curStep = 0;
        if (this._overlay) this._overlay.classList.remove('active');
        if (action === 'continue') this.startSection(nextSec.id);
        else if (action === 'toc') this.showTOC();
        else this.stop();
      } else if (idx >= 0) {
        action = await this._showConfirmModal(
          '✅ ' + this._tl('Tutorial Complete!'),
          '"' + this._t(curSec.title) + '" ' + this._tl('Complete') + '!',
          [
            { label: '📋 ' + this._tl('List'), value: 'toc', primary: true },
            { label: '✕ ' + this._tl('Close'), value: 'close' }
          ]
        );
        this._curSection = null;
        this._curStep = 0;
        if (this._overlay) this._overlay.classList.remove('active');
        if (action === 'toc') this.showTOC();
        else this.stop();
      } else {
        this.stop();
      }
    }
  }

  /** Promise-based custom confirm modal (replaces native confirm()) */
  _showConfirmModal(title, message, buttons) {
    return new Promise(resolve => {
      const overlay = document.createElement('div');
      overlay.className = 'dxt-confirm-overlay';
      overlay.innerHTML =
        '<div class="dxt-confirm-modal">' +
          '<div class="dxt-confirm-title">' + title + '</div>' +
          '<div class="dxt-confirm-msg">' + message + '</div>' +
          '<div class="dxt-confirm-btns"></div>' +
        '</div>';
      const btnWrap = overlay.querySelector('.dxt-confirm-btns');
      var primaryBtn = buttons.find(function(b) { return b.primary; }) || buttons[0];
      var self = this;
      var cleanup = function(value) {
        if (self._pendingConfirmCleanup === cleanup) self._pendingConfirmCleanup = null;
        document.removeEventListener('keydown', onKey, true);
        if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
        resolve(value);
      };
      // Expose to stop()/suspend()/destroy so an aborted tour (nav away, toggle off)
      // tears down this full-screen modal + its capture keydown listener instead of
      // leaving them stuck over the app with an unresolved promise.
      this._pendingConfirmCleanup = cleanup;
      var onKey = function(e) {
        if (e.key === 'Enter' || e.key === 'ArrowRight' || e.key === ' ') {
          e.preventDefault();
          e.stopPropagation();
          cleanup(primaryBtn.value);
        } else if (e.key === 'Escape') {
          e.preventDefault();
          e.stopPropagation();
          cleanup(null);
        }
      };
      buttons.forEach((b, i) => {
        const btn = document.createElement('button');
        btn.className = 'dxt-confirm-btn' + ((b.primary || i === 0) ? ' primary' : '');
        btn.textContent = b.label;
        btn.addEventListener('click', () => { cleanup(b.value); });
        btnWrap.appendChild(btn);
      });
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) cleanup(null);
      });
      document.addEventListener('keydown', onKey, true);
      document.body.appendChild(overlay);
      var focusBtn = btnWrap.querySelector('.dxt-confirm-btn.primary') || btnWrap.firstChild;
      if (focusBtn && typeof focusBtn.focus === 'function') focusBtn.focus();
    });
  }

  async _confirmReset() {
    var ok = await this._showConfirmModal(
      '🔄 ' + this._tl('Confirm Reset'),
      this._tl('Reset all progress?'),
      [
        { label: this._tl('Reset'), value: true },
        { label: this._tl('Cancel'), value: false }
      ]
    );
    if (ok) this.resetProgress();
  }

  prev() {
    if (!this._curSection || this._curStep <= 0) return;
    var steps = this._curSection.steps;
    this._invokeAfterStep(steps[this._curStep]);
    this._curStep--;
    this._showStep();
  }

  stop() {
    if (this._pendingConfirmCleanup) this._pendingConfirmCleanup(null);
    if (this._curSection) {
      var steps = this._curSection.steps;
      this._invokeAfterStep(steps[this._curStep]);
    }
    this._curSection = null;
    this._curStep = 0;
    this._stepToken++;
    this._resetToolbarScroll();
    if (this._overlay) this._overlay.classList.remove('active');
    if (this._spotlight) this._spotlight.classList.remove('active');
    if (this._tooltip) {
      this._tooltip.classList.remove('active');
      this._tooltip.style.top = '';
      this._tooltip.style.left = '';
      this._tooltip.style.transform = '';
      this._tooltip.removeAttribute('data-dxt-floating');
      this._tooltip.removeAttribute('data-pos');
    }
    if (this._tocBackdrop) this._tocBackdrop.classList.remove('open');
    if (this._tocEl) this._tocEl.classList.remove('open');
    window.removeEventListener('resize', this._resizeHandler);
    window.removeEventListener('scroll', this._scrollHandler, true);
  }

  /** Hide tour + help chrome without tearing down DOM (view switches, iframe handoff). */
  suspend() {
    this.hideTOC();
    this.stop();
  }

  static purgeOrphanChrome(doc, activeEngine) {
    doc = doc || document;
    var html = doc.documentElement;
    if (!html) return;
    var keep = new Set();
    if (activeEngine) {
      [activeEngine._overlay, activeEngine._spotlight, activeEngine._tooltip,
        activeEngine._tocBackdrop, activeEngine._tocEl].forEach(function(el) {
        if (el) keep.add(el);
      });
    }
    ['.dxt-overlay', '.dxt-spotlight', '.dxt-tooltip', '.dxt-toc-backdrop', '.dxt-toc',
      '.dxt-confirm-overlay'].forEach(function(sel) {
      html.querySelectorAll(sel).forEach(function(el) {
        if (keep.has(el)) return;
        if (el.parentNode) el.parentNode.removeChild(el);
      });
    });
  }

  _detachChromeRefs() {
    this._overlay = null;
    this._spotlight = null;
    this._tooltip = null;
    this._tocBackdrop = null;
    this._tocEl = null;
    this._built = false;
  }

  refreshLang() {
    if (this._tocEl && this._tocEl.classList.contains('open')) {
      this._renderTOCContent();
    }
    if (this._tooltip && this._tooltip.classList.contains('active') && this._curSection) {
      var step = this._curSection.steps[this._curStep];
      if (step) {
        var target = step.target ? this._queryTarget(step.target) : null;
        this._renderTooltip(step, target);
      }
    }
  }

  enableKeyboard() {
    if (this._keyHandler) return;
    var self = this;
    this._keyHandler = function(e) {
      var confirmEl = document.querySelector('.dxt-confirm-overlay');
      if (confirmEl) {
        if (e.key === 'Enter' || e.key === 'ArrowRight' || e.key === ' ') {
          self._activateConfirmPrimary();
          e.preventDefault();
        } else if (e.key === 'Escape') {
          if (e.target === confirmEl) confirmEl.click();
          else {
            var backdropBtn = confirmEl.querySelector('.dxt-confirm-btn');
            if (backdropBtn) confirmEl.click();
          }
          e.preventDefault();
        }
        return;
      }
      if (e.key === 'Escape') {
        if (self._curSection) { self.stop(); return; }
        if (self._tocEl && self._tocEl.classList.contains('open')) { self.hideTOC(); return; }
        return;
      }
      if (!self._curSection) return;
      if (e.key === 'ArrowRight' || e.key === 'Enter') { self.next(); e.preventDefault(); }
      if (e.key === 'ArrowLeft') { self.prev(); e.preventDefault(); }
    };
    document.addEventListener('keydown', this._keyHandler);
  }

  createToggleBtn(container) {
    if (this._toggleBtnEl) return this._toggleBtnEl;
    var btn = document.createElement('button');
    btn.className = 'dxt-toggle-btn';
    btn.id = 'dxt-toggle';
    btn.title = this._tl('Tutorial Guide');
    btn.innerHTML = '\uD83C\uDF93';
    var self = this;
    btn.addEventListener('click', function() { self.toggleTOC(); });
    if (container) container.appendChild(btn);
    return btn;
  }


  listenForMessages() {
    if (this._messageHandler) return;
    var self = this;
    this._messageHandler = function(e) {
      if (e.data && e.data.type === 'dx-tutorial-start') self.showTOC();
      if (e.data && e.data.type === 'dx-tutorial-stop') {
        if (typeof self.suspend === 'function') self.suspend();
        else {
          self.stop();
          self.hideTOC();
        }
      }
    };
    window.addEventListener('message', this._messageHandler);
  }

  destroy() {
    this.stop();
    if (this._keyHandler) {
      document.removeEventListener('keydown', this._keyHandler);
      this._keyHandler = null;
    }
    if (this._messageHandler) {
      window.removeEventListener('message', this._messageHandler);
      this._messageHandler = null;
    }
    window.removeEventListener('resize', this._resizeHandler);
    window.removeEventListener('scroll', this._scrollHandler, true);
    [this._overlay, this._spotlight, this._tooltip, this._tocBackdrop, this._tocEl].forEach(function(el) {
      if (el && el.parentNode) el.parentNode.removeChild(el);
    });
    document.querySelectorAll('.dxt-confirm-overlay').forEach(function(el) {
      if (el.parentNode) el.parentNode.removeChild(el);
    });
    this._detachChromeRefs();
  }
}

window.DXTutorialEngine = DXTutorialEngine;
if (typeof registerSharedLangRefresher === 'function') {
  registerSharedLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
