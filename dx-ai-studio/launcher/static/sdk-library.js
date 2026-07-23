
(function () {
  'use strict';

  function _sdkDebugLog() { if (window.DX_DEBUG_SDK === true) console.log.apply(console, arguments); }

  function _t(en, ko, ja, zhCN, zhTW, es) {
    if (typeof DXI18n === 'undefined') return en;
    var lang = DXI18n.lang;
    var map = { ko: ko, ja: ja, 'zh-CN': zhCN, 'zh-TW': zhTW, es: es };
    return map[lang] || en;
  }

  function currentLang() {
    if (typeof DXI18n !== 'undefined' && DXI18n.lang) return DXI18n.lang;
    return localStorage.getItem('dx-lang') || 'en';
  }

  function labelText(value) {
    if (!value) return '';
    if (typeof value === 'string') return value;
    return value[currentLang()] || value.en || '';
  }

  let _libData = null;
  let _isSearchActive = false;
  let _sdkInitialized = false;
  let _languageHookRegistered = false;
  let _keydownBound = false;

  var _currentQueryState = { view: 'list', q: '', doc: '' };
  var _pendingQuery = null;
  var _applyingQuery = false;

  function parseSdkQuery(rawQueryString) {
    var result = { view: 'list', q: '', doc: '' };
    if (!rawQueryString) return result;
    var str = rawQueryString.charAt(0) === '?' ? rawQueryString.slice(1) : rawQueryString;
    str.split('&').forEach(function(pair) {
      var parts = pair.split('=');
      var key = parts[0];
      var val = parts.slice(1).join('=');
      if (key === 'view' && (val === 'list' || val === 'cabinet')) result.view = val;
      else if (key === 'q') result.q = decodeURIComponent(val || '');
      else if (key === 'doc') {
        var decoded = decodeDocPath(val || '');
        if (decoded === null) result.doc = '';
        else result.doc = decoded;
        if (decoded === null) result._malformedDoc = true;
      }
    });
    return result;
  }

  function decodeDocPath(value) {
    try {
      return decodeURIComponent(value);
    } catch (e) {
      return null;
    }
  }

  function findBookByPath(path) {
    if (!_libData || !_libData.drawers) return null;
    for (var d = 0; d < _libData.drawers.length; d++) {
      var drawer = _libData.drawers[d];
      var sections = drawer.sections || [];
      for (var s = 0; s < sections.length; s++) {
        var files = sections[s].files || [];
        for (var f = 0; f < files.length; f++) {
          if (files[f].path === path) return files[f];
        }
      }
    }
    return null;
  }

  function requestSdkUrlUpdate(nextPatch, historyMode) {
    if (_applyingQuery) return;
    var next = {
      view: nextPatch.view || _currentQueryState.view,
      q: nextPatch.q !== undefined ? nextPatch.q : _currentQueryState.q,
      doc: nextPatch.doc !== undefined ? nextPatch.doc : _currentQueryState.doc
    };
    if (!next.doc) delete next.doc;
    if (!next.q) delete next.q;
    if (next.view === 'list') delete next.view;
    _currentQueryState = { view: next.view || 'list', q: next.q || '', doc: next.doc || '' };
    if (window.LauncherRouter && window.LauncherRouter.updateSdkLibraryQuery) {
      window.LauncherRouter.updateSdkLibraryQuery(next, { history: historyMode });
    }
  }

  function applyQuery(rawQueryString, options) {
    if (!_libData) {
      _pendingQuery = { raw: rawQueryString, options: options };
      return;
    }
    _applyingQuery = true;
    try {
      var parsed = parseSdkQuery(rawQueryString);
      _currentQueryState = parsed;
      if (parsed.view !== _viewMode) {
        switchView(parsed.view, { silentUrl: true });
      }
      var searchInput = document.getElementById('sdkLibSearch');
      if (searchInput && parsed.q !== undefined) {
        searchInput.value = parsed.q;
        if (parsed.q) {
          if (_viewMode === 'cabinet') searchCabinet(parsed.q.toLowerCase());
          else searchListView(parsed.q.toLowerCase());
        } else {
          clearSearchSummary();
          if (_viewMode === 'cabinet') searchCabinet('');
          else searchListView('');
        }
      }
      if (parsed._malformedDoc) {
        _renderDocNotFound(_t('(malformed path)', '(잘못된 경로)', '(不正なパス)', '(格式错误的路径)', '(格式錯誤的路徑)', '(ruta mal formada)'));
      } else if (parsed.doc) {
        var book = findBookByPath(parsed.doc);
        if (book) {
          openBookViewer(book);
        } else {
          _renderDocNotFound(parsed.doc);
        }
      }
    } finally {
      _applyingQuery = false;
    }
  }

  function _renderDocNotFound(path) {
    var viewer = document.getElementById('sdkBookViewer');
    if (!viewer) return;
    var body = document.getElementById('sdkViewerBody');
    var titleEl = viewer.querySelector('.sdk-viewer-title');
    if (titleEl) titleEl.textContent = _t('Document Not Found', '문서를 찾을 수 없음', 'ドキュメントが見つかりません', '文档未找到', '文件未找到', 'Documento no encontrado');
    if (body) body.innerHTML = '<div class="sdk-not-found"><p>' + _t('Not found: ', '찾을 수 없음: ', '見つかりません: ', '未找到: ', '未找到: ', 'No encontrado: ') + escHtml(path) + '</p></div>';
    viewer.classList.add('open');
  }

  function _renderEmptySearch(kind) {
    var msg = kind === 'no-results'
      ? _t('No results found.', '결과가 없습니다.', '結果が見つかりません。', '未找到结果。', '未找到結果。', 'No se encontraron resultados.')
      : _t('No documents available.', '문서가 없습니다.', 'ドキュメントがありません。', '没有可用文档。', '沒有可用文件。', 'No hay documentos disponibles.');
    return '<div class="sdk-empty-search"><p>' + msg + '</p></div>';
  }

  function _showEmptySearch(container) {
    if (!container) return;
    _clearEmptySearch(container);
    container.insertAdjacentHTML('beforeend', _renderEmptySearch('no-results'));
  }

  function _clearEmptySearch(container) {
    if (!container) return;
    var el = container.querySelector('.sdk-empty-search');
    if (el) el.remove();
  }

  async function loadLibraryData() {
    if (_libData) return _libData;
    try {
      // cache: 'no-cache' → always revalidate with the server (ETag), so catalog
      // updates show up immediately instead of being masked by the max-age cache.
      const res = await fetch('/static/sdk-library-data.json', { cache: 'no-cache' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      _libData = await res.json();
      return _libData;
    } catch (e) {
      console.error('SDK library data load failed:', e);
      return null;
    }
  }

  let _viewMode = 'list'; // 'cabinet' | 'list' — list is default
  let _selectedDrawer = null;
  let _selectedSection = null;

  function buildModuleHeader() {
    const header = document.createElement('header');
    header.className = 'sdk-topbar';
    header.innerHTML = `
      <div class="sdk-topbar-left">
        <span class="dx-brand-slot" id="sdkBrand"></span>
        <span class="sdk-doc-count" id="sdkDocCount"></span>
      </div>
      <div class="sdk-topbar-center">
        <div class="sdk-topbar-search">
          <span class="sdk-topbar-search-icon">🔍</span>
          <input type="text" id="sdkLibSearch" placeholder="${_t('Search documents…', '문서 검색…', 'ドキュメント検색…', '搜索文档…', '搜尋文件…', 'Buscar documentos…')}" autocomplete="off">
        </div>
      </div>
      <div class="sdk-topbar-right">
        <div class="sdk-topbar-toggle">
          <button class="sdk-toggle-btn ${_viewMode === 'list' ? 'active' : ''}" data-mode="list" title="${_t('List View', '목록 보기', 'リストビュー', '列表视图', '列表檢視', 'Vista de lista')}">📋 ${_t('List', '목록', 'リスト', '列表', '列表', 'Lista')}</button>
          <button class="sdk-toggle-btn ${_viewMode === 'cabinet' ? 'active' : ''}" data-mode="cabinet" title="${_t('Cabinet View', '캐비닛 보기', 'キャビネットビュー', '文件柜视图', '文件櫃檢視', 'Vista de archivador')}">🗄️ ${_t('Cabinet', '캐비닛', 'キャビネット', '文件柜', '文件櫃', 'Archivador')}</button>
        </div>
        <button class="sdk-topbar-btn" id="sdkArchBtn" title="${_t('Architecture', '아키텍처', 'アーキテクチャ', '架构', '架構', 'Arquitectura')}">🏗️</button>
      </div>`;
    header.querySelectorAll('.sdk-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;
        if (mode === _viewMode) return;
        switchView(mode);
      });
    });
    return header;
  }

  function mountSdkBrand() {
    if (typeof DXBrand === 'undefined') return;
    DXBrand.mount({
      target: '#sdkBrand',
      name: 'SDK Library',
      subtitle: {
        ko: 'SDK 기술 도서관',
        en: 'SDK Tech Library',
        ja: 'SDK技術ライブラリ',
        'zh-CN': 'SDK技术资料库',
        'zh-TW': 'SDK技術資料庫',
        es: 'Biblioteca técnica del SDK'
      },
      accent: 'var(--accent)'
    });
  }

  function switchView(mode, options) {
    _viewMode = mode;
    _isSearchActive = false;
    if (_libData) renderView(_libData);
    if (!(options && options.silentUrl)) {
      requestSdkUrlUpdate({ view: mode }, 'replace');
    }
  }

  function renderView(data) {
    const container = document.getElementById('sdkCabinet');
    if (!container || !data.drawers) return;
    // The launcher relocates the shared lang+tutorial toolbar (#dxToolbar) into this header. The
    // header is rebuilt on every render (view toggle, lang change, refresh), so preserve the live
    // toolbar node across the innerHTML wipe and re-attach it to the fresh .sdk-topbar-right —
    // otherwise it would be destroyed and lost. The variable keeps the detached node alive.
    //
    // Only re-claim it when SDK is the visible view: onLangChange re-renders regardless of the
    // active view, and grabbing #dxToolbar while another view owns it would steal it away.
    const sdkView = document.getElementById('sdk-library-view');
    const sdkVisible = sdkView && sdkView.classList.contains('visible');
    const toolbar = sdkVisible ? document.getElementById('dxToolbar') : null;
    container.innerHTML = '';
    container.appendChild(buildModuleHeader());
    if (toolbar) {
      const slot = container.querySelector('.sdk-topbar-right');
      if (slot) slot.appendChild(toolbar);
    }
    mountSdkBrand();

    const body = document.createElement('div');
    body.className = 'sdk-body';
    container.appendChild(body);

    if (_viewMode === 'cabinet') {
      renderCabinet(data, body);
    } else {
      renderListView(data, body);
    }
    setupSearch();

    const totalFiles = data.drawers.reduce((t, d) => t + d.sections.reduce((s, sec) => s + sec.files.length, 0), 0);
    const countEl = document.getElementById('sdkDocCount');
    if (countEl) countEl.textContent = totalFiles + _t(' docs', '개 문서', ' ドキュメント', ' 个文档', ' 個文件', ' docs');

    const archBtn = document.getElementById('sdkArchBtn');
    if (archBtn) archBtn.addEventListener('click', toggleArchOverlay);
    const archOverlay = document.getElementById('sdkArchOverlay');
    if (archOverlay && !archOverlay._bound) {
      archOverlay.addEventListener('click', toggleArchOverlay);
      archOverlay._bound = true;
    }

    if (typeof DXChat !== 'undefined') {
      DXChat.init({ appName: 'sdk_library' });
    }

    // Signal tutorial system that SDK Library DOM is ready
    _sdkDebugLog('[SDK Library] dispatching sdk-library-ready event');
    window.dispatchEvent(new CustomEvent('sdk-library-ready'));
  }

  function renderCabinet(data, container) {
    const frame = document.createElement('div');
    frame.className = 'cabinet-frame';
    const drawersEl = document.createElement('div');
    drawersEl.className = 'cabinet-drawers';
    for (const drawer of data.drawers) {
      drawersEl.appendChild(buildDrawer(drawer));
    }
    frame.appendChild(drawersEl);
    container.appendChild(frame);
  }

  function selectListSection(sidebar, data, drawer, section, group, secItem) {
    sidebar.querySelectorAll('.sdk-sidebar-section.selected').forEach(s => s.classList.remove('selected'));
    sidebar.querySelectorAll('.sdk-sidebar-group-head.selected').forEach(h => h.classList.remove('selected'));
    if (secItem) {
      group.classList.add('expanded');
      secItem.classList.add('selected');
    } else {
      const head = group.querySelector('.sdk-sidebar-group-head');
      if (head) head.classList.add('selected');
    }
    _selectedDrawer = drawer.id;
    _selectedSection = section.id;
    renderListContent(data, drawer, section);
  }

  function renderListView(data, container) {
    const layout = document.createElement('div');
    layout.className = 'sdk-list-layout';

    const sidebar = document.createElement('div');
    sidebar.className = 'sdk-list-sidebar';
    for (const drawer of data.drawers) {
      const group = document.createElement('div');
      group.className = `sdk-sidebar-group sidebar-${drawer.color}`;
      group.dataset.drawerId = drawer.id;
      const isFlatDrawer = drawer.sections.length === 1;

      const groupHead = document.createElement('div');
      groupHead.className = 'sdk-sidebar-group-head';
      groupHead.dataset.helpId = 'sidebar-group-' + drawer.id;
      const totalFiles = drawer.sections.reduce((s, sec) => s + sec.files.length, 0);
      groupHead.innerHTML = `
        <span class="sdk-sidebar-icon">${drawer.icon}</span>
        <span class="sdk-sidebar-label">${escHtml(labelText(drawer.label))}</span>
        <span class="sdk-sidebar-count">${totalFiles}</span>`;
      if (isFlatDrawer) {
        group.classList.add('flat');
        groupHead.addEventListener('click', () => {
          selectListSection(sidebar, data, drawer, drawer.sections[0], group, null);
        });
      } else {
        groupHead.addEventListener('click', () => {
          group.classList.toggle('expanded');
          if (!group.querySelector('.sdk-sidebar-section.selected')) {
            const firstSec = group.querySelector('.sdk-sidebar-section');
            if (firstSec) firstSec.click();
          }
        });
      }
      group.appendChild(groupHead);

      if (!isFlatDrawer) {
        for (const section of drawer.sections) {
          const secItem = document.createElement('div');
          secItem.className = 'sdk-sidebar-section';
          secItem.dataset.sectionId = section.id;
          secItem.dataset.drawerId = drawer.id;
          secItem.innerHTML = `
            <span class="sdk-sidebar-sec-icon">${section.icon}</span>
            <span class="sdk-sidebar-sec-label">${escHtml(labelText(section.label))}</span>
            <span class="sdk-sidebar-sec-count">${section.files.length}</span>`;
          secItem.addEventListener('click', (e) => {
            e.stopPropagation();
            selectListSection(sidebar, data, drawer, section, group, secItem);
          });
          group.appendChild(secItem);
        }
      }
      sidebar.appendChild(group);
    }

    const content = document.createElement('div');
    content.className = 'sdk-list-content';
    content.id = 'sdkListContent';
    content.innerHTML = '<div class="sdk-list-empty">' + _t('← Select a category from the left', '← 좌측에서 카테고리를 선택하세요', '← 左側からカテゴリを選択してください', '← 请从左侧选择分类', '← 請從左側選擇分類', '← Seleccione una categoría de la izquierda') + '</div>';

    layout.appendChild(sidebar);
    layout.appendChild(content);
    container.appendChild(layout);
  }

  function renderListContent(data, drawer, section) {
    const content = document.getElementById('sdkListContent');
    if (!content) return;

    content.innerHTML = `
      <div class="sdk-list-content-header">
        <span class="sdk-list-breadcrumb">${drawer.icon} ${escHtml(labelText(drawer.label))} › ${escHtml(labelText(section.label))}</span>
        <span class="sdk-list-file-count">${section.files.length}${_t(' files', '개 파일', ' ファイル', ' 个文件', ' 個檔案', ' archivos')}</span>
      </div>
      <div class="sdk-list-files-grid"></div>`;

    const grid = content.querySelector('.sdk-list-files-grid');
    for (const file of section.files) {
      grid.appendChild(buildFileCard(file, drawer.color));
    }
  }

  function buildDrawer(drawer) {
    const unit = document.createElement('div');
    unit.className = `drawer-unit drawer-${drawer.color}`;
    unit.dataset.drawerId = drawer.id;

    const totalFiles = drawer.sections.reduce((s, sec) => s + sec.files.length, 0);

    const face = document.createElement('div');
    face.className = 'drawer-face';
    face.dataset.helpId = 'drawer-face-' + drawer.id;
    face.innerHTML = `
      <div class="drawer-stripe"></div>
      <div class="drawer-label-plate">
        <span class="drawer-label-icon">${drawer.icon}</span>
        <span class="drawer-label-text">${escHtml(labelText(drawer.label))}</span>
      </div>
      <span class="drawer-label-count">${totalFiles}${_t(' files', '개 파일', ' ファイル', ' 个文件', ' 個檔案', ' archivos')}</span>
      <div class="drawer-handle"></div>`;
    face.addEventListener('click', () => toggleDrawer(unit));
    unit.appendChild(face);

    const body = document.createElement('div');
    body.className = 'drawer-body';

    for (const section of drawer.sections) {
      const secEl = document.createElement('div');
      secEl.className = 'drawer-section';
      secEl.dataset.sectionId = section.id;

      if (drawer.sections.length > 1) {
        const secHeader = document.createElement('div');
        secHeader.className = 'drawer-section-header';
        secHeader.innerHTML = `
          <span class="section-icon">${section.icon}</span>
          <span class="section-label">${escHtml(labelText(section.label))}</span>
          <span class="section-count">${section.files.length}</span>`;
        secEl.appendChild(secHeader);
      }

      const inner = document.createElement('div');
      inner.className = 'drawer-files-inner';
      for (const file of section.files) {
        inner.appendChild(buildFileCard(file, drawer.color));
      }
      secEl.appendChild(inner);
      body.appendChild(secEl);
    }

    unit.appendChild(body);

    body.addEventListener('transitionend', (e) => {
      if (e.propertyName !== 'max-height') return;
      if (unit.classList.contains('open')) {
        body.style.maxHeight = 'none';
        body.style.overflowY = 'auto';
      }
    });

    return unit;
  }

  function buildFileCard(file, drawerColor) {
    const card = document.createElement('div');
    card.className = 'file-card';
    card.dataset.title = file.title.toLowerCase();
    card.dataset.path = (file.path || '').toLowerCase();

    const isPdf = file.type === 'pdf';
    const sizeStr = formatSize(file.size);
    const colorClass = isPdf ? 'pdf' : (drawerColor || 'green');

    card.innerHTML = `
      <div class="file-card-icon ${colorClass}">${isPdf ? '📄' : '📝'}</div>
      <div class="file-card-info">
        <div class="file-card-title">${escHtml(file.title)}</div>
        <div class="file-card-meta">
          <span>${isPdf ? 'PDF' : 'MD'}</span>
          <span>${sizeStr}</span>
        </div>
      </div>
      <span class="file-card-pull">${_t('→ Open', '→ 열기', '→ 開く', '→ 打开', '→ 開啟', '→ Abrir')}</span>`;

    card.addEventListener('click', () => openBookViewer(file, drawerColor));
    return card;
  }

  function formatSize(bytes) {
    if (!bytes || bytes === 0) return '';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
  }

  function toggleDrawer(unit) {
    if (_isSearchActive) return;
    const wasOpen = unit.classList.contains('open');

    document.querySelectorAll('.drawer-unit.open').forEach(d => {
      closeDrawer(d);
    });

    if (!wasOpen) {
      openDrawer(unit);
    }
  }

  function openDrawer(unit) {
    const body = unit.querySelector('.drawer-body');
    if (!body) return;
    body.style.maxHeight = body.scrollHeight + 'px';
    body.style.overflowY = 'hidden';
    unit.classList.add('open');
  }

  function closeDrawer(unit) {
    const body = unit.querySelector('.drawer-body');
    if (!body) return;
    // Set concrete height first for smooth transition
    body.style.maxHeight = body.scrollHeight + 'px';
    body.style.overflowY = 'hidden';
    // Force reflow then set 0
    body.offsetHeight;
    requestAnimationFrame(() => {
      body.style.maxHeight = '0px';
      unit.classList.remove('open');
    });
  }

  var _searchUrlTimeout = null;
  function setupSearch() {
    const input = document.getElementById('sdkLibSearch');
    if (!input) return;
    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();

      if (_viewMode === 'cabinet') {
        searchCabinet(q);
      } else {
        searchListView(q);
      }
      clearTimeout(_searchUrlTimeout);
      _searchUrlTimeout = setTimeout(function() {
        requestSdkUrlUpdate({ q: input.value.trim() }, 'replace');
      }, 250);
    });
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        clearTimeout(_searchUrlTimeout);
        requestSdkUrlUpdate({ q: input.value.trim() }, 'replace');
      }
    });
  }

  function searchCabinet(q) {
    const cabinet = document.getElementById('sdkCabinet');
    const drawers = document.querySelectorAll('.drawer-unit');
    if (!q) {
      _isSearchActive = false;
      _clearEmptySearch(cabinet);
      clearSearchSummary();
      drawers.forEach(d => {
        d.classList.remove('search-hidden');
        d.querySelectorAll('.drawer-section').forEach(s => s.classList.remove('search-hidden'));
        d.querySelectorAll('.file-card').forEach(c => c.classList.remove('search-hidden'));
        closeDrawer(d);
      });
      return;
    }
    _isSearchActive = true;
    let anyMatch = false;
    let matchCount = 0;
    drawers.forEach(d => {
      let drawerHasMatch = false;
      d.querySelectorAll('.drawer-section').forEach(sec => {
        const cards = sec.querySelectorAll('.file-card');
        let sectionHasMatch = false;
        cards.forEach(c => {
          const match = c.dataset.title.includes(q) || c.dataset.path.includes(q);
          c.classList.toggle('search-hidden', !match);
          if (match) { sectionHasMatch = true; matchCount++; }
        });
        sec.classList.toggle('search-hidden', !sectionHasMatch);
        if (sectionHasMatch) drawerHasMatch = true;
      });
      d.classList.toggle('search-hidden', !drawerHasMatch);
      if (drawerHasMatch) { openDrawer(d); anyMatch = true; } else closeDrawer(d);
    });
    renderSearchSummary(q, matchCount);
    if (!anyMatch) _showEmptySearch(cabinet);
    else _clearEmptySearch(cabinet);
  }

  function searchListView(q) {
    const listContent = document.getElementById('sdkListContent');
    const groups = document.querySelectorAll('.sdk-sidebar-group');
    if (!q) {
      _clearEmptySearch(listContent);
      clearSearchSummary();
      groups.forEach(g => {
        g.classList.remove('search-hidden');
        g.querySelectorAll('.sdk-sidebar-section').forEach(s => s.classList.remove('search-hidden'));
        g.classList.remove('expanded');
      });
      document.querySelectorAll('.sdk-list-files-grid .file-card').forEach(c => c.classList.remove('search-hidden'));
      return;
    }
    let matchCount = 0;
    groups.forEach(g => {
      let groupHasMatch = false;
      const sections = g.querySelectorAll('.sdk-sidebar-section');
      if (sections.length) {
        sections.forEach(sec => {
          const label = sec.querySelector('.sdk-sidebar-sec-label').textContent.toLowerCase();
          if (label.includes(q)) { sec.classList.remove('search-hidden'); groupHasMatch = true; }
          else sec.classList.add('search-hidden');
        });
      } else {
        const labelEl = g.querySelector('.sdk-sidebar-label');
        if (labelEl && labelEl.textContent.toLowerCase().includes(q)) groupHasMatch = true;
      }
      g.classList.toggle('search-hidden', !groupHasMatch);
      if (groupHasMatch && sections.length) { g.classList.add('expanded'); }
    });
    // Filter content panel cards — tracked separately for empty state
    let contentCardMatch = false;
    document.querySelectorAll('.sdk-list-files-grid .file-card').forEach(c => {
      const match = c.dataset.title.includes(q) || c.dataset.path.includes(q);
      c.classList.toggle('search-hidden', !match);
      if (match) { contentCardMatch = true; matchCount++; }
    });
    renderSearchSummary(q, matchCount);
    if (!contentCardMatch) _showEmptySearch(listContent);
    else _clearEmptySearch(listContent);
  }

  function escHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  // Resolve a doc-relative path ("img/a.png", "../x.png") against the doc's
  // directory into a suite-root-relative path for /api/sdk-doc-image.
  function _resolveDocRel(docPath, src) {
    const dir = (docPath && docPath.indexOf('/') >= 0)
      ? docPath.slice(0, docPath.lastIndexOf('/')) : '';
    const parts = dir ? dir.split('/') : [];
    src.split('/').forEach((seg) => {
      if (seg === '' || seg === '.') return;
      if (seg === '..') { if (parts.length) parts.pop(); return; }
      parts.push(seg);
    });
    return parts.join('/');
  }

  // Block-based Markdown → HTML. Splits the source into blank-line-separated
  // blocks and classifies each (heading / hr / code / table / blockquote / list /
  // raw-HTML block / paragraph) rather than transforming line-by-line. This keeps
  // paragraphs that start with inline markup (**bold**, `code`) wrapped in <p>,
  // groups list items (incl. tab-indented `-\t`) into a single <ul>, converts
  // trailing hard breaks to <br>, and rewrites BOTH markdown `![](rel)` and raw
  // HTML `<img src="rel">` doc-relative sources through the image endpoint.
  // ── Mermaid diagrams ──────────────────────────────────────────────────────
  // Docs (e.g. Model Zoo architecture) use ```mermaid fences. The parser emits them as
  // <pre class="mermaid-source">; here we turn each into an SVG once the doc mounts, using
  // the offline vendored mermaid.min.js. On failure, the original code block is kept visible.
  let _mermaidReady = null;
  function ensureMermaid() {
    if (typeof mermaid === 'undefined') return null;
    if (!_mermaidReady) {
      try {
        mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'dark', fontFamily: 'inherit' });
      } catch (e) { /* already initialised */ }
      _mermaidReady = Promise.resolve();
    }
    return _mermaidReady;
  }
  function renderMermaidBlocks(root) {
    if (!root) return;
    const blocks = root.querySelectorAll('pre.mermaid-source');
    if (!blocks.length) return;
    const ready = ensureMermaid();
    if (!ready) return;  // mermaid lib absent → leave the code block visible
    ready.then(() => {
      blocks.forEach((pre) => {
        if (pre.dataset.mmDone === '1') return;
        pre.dataset.mmDone = '1';
        const code = pre.querySelector('code');
        const src = ((code && code.textContent) || pre.textContent || '').trim();
        if (!src) return;
        const host = document.createElement('div');
        host.className = 'sdk-mermaid';
        host.textContent = src;
        pre.replaceWith(host);
        try {
          mermaid.run({ nodes: [host], suppressErrors: true }).then(() => {
            if (!host.querySelector('svg')) fallback(host, src);
          }).catch(() => fallback(host, src));
        } catch (e) { fallback(host, src); }
      });
    });
    function fallback(host, src) {
      const pre = document.createElement('pre');
      const c = document.createElement('code');
      c.textContent = src;
      pre.appendChild(c);
      host.replaceWith(pre);
    }
  }

  function mdToHtml(md, docPath) {
    // Protect fenced code blocks from later transforms.
    const codeBlocks = [];
    // Fenced code. Accept a full info string after the opening fence (e.g. ```python
    // title="x", ```py {.highlight}) — capture everything to end-of-line and derive the
    // language token from its first word, so attribute-carrying fences still pair correctly
    // (an unmatched fence used to shift the pairing and leak code as plain text).
    let s = md.replace(/```[ \t]*([^\n]*)\n([\s\S]*?)```/g, (_, info, code) => {
      const idx = codeBlocks.length;
      const lang = ((info || '').trim().match(/^[\w+-]+/) || [''])[0];
      if (lang.toLowerCase() === 'mermaid') {
        // Emit a mermaid source block; renderMermaidBlocks() turns it into an SVG diagram
        // after the doc mounts (falls back to showing the code if rendering fails).
        codeBlocks.push(`<pre class="mermaid-source"><code>${escHtml(code.trimEnd())}</code></pre>`);
      } else {
        codeBlocks.push(`<pre><code class="lang-${lang}">${escHtml(code.trimEnd())}</code></pre>`);
      }
      return `\x00CB${idx}\x00`;
    });
    // Reference-style link definitions: `[label]: url` — collect then blank the line.
    const refs = {};
    s = s.replace(/^[ \t]*\[([^\]]+)\]:\s*(\S+).*$/gm, (_, label, url) => {
      refs[label.toLowerCase()] = url;
      return '\x00REF\x00';
    });

    const rewriteSrc = (x) => {
      x = x.trim();
      // absolute/data/root-anchored/already-rewritten sources pass through
      const abs = /^(https?:|data:|\/|\x00)/i.test(x);
      return (abs || !docPath)
        ? x
        : '/api/sdk-doc-image?path=' + encodeURIComponent(_resolveDocRel(docPath, x));
    };
    const inline = (text) => {
      let t = text;
      t = t.replace(/`([^`]+)`/g, '<code>$1</code>');
      t = t.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
      t = t.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
      t = t.replace(/\*(.+?)\*/g, '<em>$1</em>');
      // Markdown images → rewritten <img>
      t = t.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (m, alt, src) => `<img src="${rewriteSrc(src)}" alt="${alt}">`);
      // Raw HTML <img src="rel"> → rewrite the src attribute (keep other attrs)
      t = t.replace(/(<img\b[^>]*?\bsrc\s*=\s*["'])([^"']+)(["'])/gi, (m, pre, src, post) => `${pre}${rewriteSrc(src)}${post}`);
      // Doc-relative links to another .md open inside the viewer; everything else opens in a
      // new tab. (Cross-doc links used to point at a raw .md path and 404.)
      const mkLink = (txt, url) => {
        const u = (url || '').trim();
        const base = u.split('#')[0].split('?')[0];
        if (docPath && /\.md$/i.test(base) && !/^(https?:|\/|mailto:)/i.test(u)) {
          const anchor = u.includes('#') ? u.slice(u.indexOf('#')) : '';
          return `<a href="#" class="sdk-doclink" data-doc="${escHtml(_resolveDocRel(docPath, base))}" data-anchor="${escHtml(anchor)}">${txt}</a>`;
        }
        return `<a href="${u}" target="_blank">${txt}</a>`;
      };
      t = t.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (m, txt, url) => mkLink(txt, url));
      t = t.replace(/\[([^\]]+)\]\[([^\]]*)\]/g, (m, txt, label) => {
        const url = refs[(label || txt).toLowerCase()];
        return url ? mkLink(txt, url) : m;
      });
      return t;
    };

    const isBlank = (l) => /^\s*$/.test(l) || l.trim() === '\x00REF\x00';
    const listRe = /^(\s*)(?:[*+-]|\d+[.)])[ \t]+(.+)$/;
    const listItemRe = /^(\s*)(?:([*+-])|(\d+)[.)])[ \t]+(.+)$/;
    const headRe = /^(#{1,6})\s+(.+)$/;
    const hrRe = /^\s*(-{3,}|\*{3,}|_{3,})\s*$/;
    const bqRe = /^\s*>\s?/;
    const htmlRe = /^\s*<(\/?)(div|img|table|thead|tbody|tr|td|th|p|ul|ol|li|blockquote|figure|figcaption|h[1-6]|hr|br|section|span|pre|details|summary|iframe|video|source|!--)/i;
    const cbRe = /^\s*\x00CB\d+\x00\s*$/;
    const rowRe = /^\s*\|.*\|\s*$/;
    // GFM tables tolerate rows without outer pipes (e.g. `Type | Format`). Detect a table by
    // a header line containing a pipe immediately followed by a separator row of dashes.
    const hasPipe = (l) => /\|/.test(l) && !cbRe.test(l);
    const sepRowRe = (l) => /-/.test(l) && /\|/.test(l) && /^[\s:|-]+$/.test(l);
    // MkDocs admonitions (`!!! type "Title"`, collapsible `???`/`???+`) and content tabs
    // (`=== "Tab"`) — the source docs use these heavily; without support they'd render as
    // literal `!!! note` text. Body is the following 4-space/tab-indented block.
    const admRe = /^(!!!|\?\?\?\+?)\s+([\w-]+)(?:\s+"([^"]*)")?\s*$/;
    const tabRe = /^===\+?\s+"([^"]*)"\s*$/;
    const indentedRe = /^( {4}|\t)/;
    const ADM_ICONS = {
      note:'📝', abstract:'📄', summary:'📄', tldr:'📄', info:'ℹ️', todo:'☑️',
      tip:'💡', hint:'💡', important:'❗', success:'✅', check:'✅', done:'✅',
      question:'❓', help:'❓', faq:'❓', warning:'⚠️', caution:'⚠️', attention:'⚠️',
      failure:'❌', fail:'❌', missing:'❌', danger:'🛑', error:'🛑', bug:'🐛',
      example:'📋', quote:'❝', cite:'❝',
    };
    const isSpecial = (l) => headRe.test(l) || hrRe.test(l) || listRe.test(l) || bqRe.test(l) || htmlRe.test(l) || cbRe.test(l) || rowRe.test(l) || admRe.test(l) || tabRe.test(l);

    // Collect the indented body under an admonition/tab marker, then dedent one level.
    const takeIndentedBody = (lines, i) => {
      const inner = [];
      while (i < lines.length && (isBlank(lines[i]) || indentedRe.test(lines[i]))) { inner.push(lines[i]); i++; }
      while (inner.length && isBlank(inner[inner.length - 1])) inner.pop();
      return [inner.map((l) => l.replace(indentedRe, '')), i];
    };

    const renderBlocks = (lines) => {
      const out = [];
      let i = 0;
      while (i < lines.length) {
        const line = lines[i];
        if (isBlank(line)) { i++; continue; }
        let m;
        // Admonition / collapsible admonition
        if ((m = line.match(admRe))) {
          const collapsible = m[1][0] === '?';
          const type = m[2].toLowerCase();
          const title = (m[3] != null && m[3] !== '') ? m[3] : (m[2].charAt(0).toUpperCase() + m[2].slice(1));
          let inner; [inner, i] = takeIndentedBody(lines, i + 1);
          const body = renderBlocks(inner);
          const icon = ADM_ICONS[type] || '📌';
          const titleHtml = `<span class="sdk-adm-icon">${icon}</span>${inline(title)}`;
          if (collapsible) {
            const open = m[1] === '???+' ? ' open' : '';
            out.push(`<details class="sdk-adm sdk-adm-${type}"${open}><summary class="sdk-adm-title">${titleHtml}</summary><div class="sdk-adm-body">${body}</div></details>`);
          } else {
            out.push(`<div class="sdk-adm sdk-adm-${type}"><div class="sdk-adm-title">${titleHtml}</div><div class="sdk-adm-body">${body}</div></div>`);
          }
          continue;
        }
        // Content tab → labeled block (stacked; not interactive tabs)
        if ((m = line.match(tabRe))) {
          let inner; [inner, i] = takeIndentedBody(lines, i + 1);
          out.push(`<div class="sdk-tab"><div class="sdk-tab-label">${inline(m[1])}</div><div class="sdk-tab-body">${renderBlocks(inner)}</div></div>`);
          continue;
        }
        if ((m = line.match(headRe))) { out.push(`<h${m[1].length}>${inline(m[2].trim())}</h${m[1].length}>`); i++; continue; }
        if (hrRe.test(line)) { out.push('<hr>'); i++; continue; }
        if (cbRe.test(line)) { out.push(line.trim()); i++; continue; }
        // Table: header row (pipe, outer pipes optional) followed by a dash separator row.
        if (hasPipe(line) && i + 1 < lines.length && sepRowRe(lines[i + 1])) {
          const cell = (r) => r.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
          const ths = cell(line).map(c => `<th>${inline(c)}</th>`).join('');
          i += 2;
          const trs = [];
          while (i < lines.length && hasPipe(lines[i]) && !isBlank(lines[i])) {
            trs.push(`<tr>${cell(lines[i]).map(c => `<td>${inline(c)}</td>`).join('')}</tr>`);
            i++;
          }
          out.push(`<table><thead><tr>${ths}</tr></thead><tbody>${trs.join('')}</tbody></table>`);
          continue;
        }
        if (bqRe.test(line)) {
          const buf = [];
          while (i < lines.length && bqRe.test(lines[i])) { buf.push(lines[i].replace(bqRe, '')); i++; }
          out.push(`<blockquote>${inline(buf.join(' '))}</blockquote>`);
          continue;
        }
        // List — gather consecutive items (blank lines between items still merge), then build
        // a nested tree by indentation with ordered (<ol>) / unordered (<ul>) per level.
        if (listRe.test(line)) {
          const raw = [];
          while (i < lines.length) {
            if (listRe.test(lines[i])) { raw.push(lines[i]); i++; }
            else if (isBlank(lines[i]) && i + 1 < lines.length && listRe.test(lines[i + 1])) { i++; }
            else break;
          }
          const parsed = raw.map((l) => {
            const mm = l.match(listItemRe);
            return { indent: mm[1].replace(/\t/g, '    ').length, ordered: mm[3] !== undefined, content: mm[4].trim() };
          });
          let pos = 0;
          const build = () => {
            const baseIndent = parsed[pos].indent;
            const ordered = parsed[pos].ordered;
            let lis = '';
            while (pos < parsed.length && parsed[pos].indent >= baseIndent) {
              if (parsed[pos].indent > baseIndent) break;  // safety: stray deeper indent
              let li = inline(parsed[pos].content);
              pos++;
              if (pos < parsed.length && parsed[pos].indent > baseIndent) li += build();  // nested child list
              lis += `<li>${li}</li>`;
            }
            return `<${ordered ? 'ol' : 'ul'}>${lis}</${ordered ? 'ol' : 'ul'}>`;
          };
          let listHtml = '';
          while (pos < parsed.length) listHtml += build();
          out.push(listHtml);
          continue;
        }
        // Raw HTML block — pass through (apply inline so <img> src gets rewritten), no <p> wrap.
        if (htmlRe.test(line)) {
          const buf = [];
          while (i < lines.length && !isBlank(lines[i])) { buf.push(lines[i]); i++; }
          out.push(inline(buf.join('\n')));
          continue;
        }
        // Paragraph — always consume the current line (guarantees progress even for
        // a special-looking line no block handler claimed, e.g. a stray `|` row), then
        // gather continuation lines until a blank line or the start of another block.
        const buf = [lines[i]];
        i++;
        while (i < lines.length && !isBlank(lines[i]) && !isSpecial(lines[i]) &&
               !(hasPipe(lines[i]) && i + 1 < lines.length && sepRowRe(lines[i + 1]))) { buf.push(lines[i]); i++; }
        const para = buf.map((l, idx) => {
          const hard = /  +$/.test(l) || /\\$/.test(l);
          return l.replace(/\\$/, '').replace(/\s+$/, '') + (idx < buf.length - 1 ? (hard ? '<br>' : ' ') : '');
        }).join('');
        out.push(`<p>${inline(para)}</p>`);
      }
      return out.join('\n');
    };

    let html = renderBlocks(s.split('\n'));
    html = html.replace(/\x00CB(\d+)\x00/g, (_, idx) => codeBlocks[idx]);
    return html;
  }

  const DRAWER_COLORS = {
    gold:  { accent: '#d4a853', bg: 'rgba(212,168,83,0.06)', border: 'rgba(212,168,83,0.25)' },
    red:   { accent: '#f47067', bg: 'rgba(244,112,103,0.06)', border: 'rgba(244,112,103,0.25)' },
    green: { accent: '#3fb950', bg: 'rgba(63,185,80,0.06)', border: 'rgba(63,185,80,0.25)' },
    blue:  { accent: '#58a6ff', bg: 'rgba(88,166,255,0.06)', border: 'rgba(88,166,255,0.25)' },
    amber: { accent: '#d29922', bg: 'rgba(210,153,34,0.06)', border: 'rgba(210,153,34,0.25)' },
  };

  function buildDocumentTrail(book) {
    if (!_libData || !_libData.drawers) return null;
    for (var d = 0; d < _libData.drawers.length; d++) {
      var drawer = _libData.drawers[d];
      var sections = drawer.sections || [];
      for (var s = 0; s < sections.length; s++) {
        var section = sections[s];
        var files = section.files || [];
        for (var f = 0; f < files.length; f++) {
          if (files[f].path === book.path) {
            return { drawer: drawer, section: section, document: book };
          }
        }
      }
    }
    return null;
  }

  function renderDocumentTrail(book, trailOverride) {
    var trail = trailOverride || buildDocumentTrail(book);
    var container = document.querySelector('.sdk-current-path');
    if (!container) {
      var viewer = document.getElementById('sdkBookViewer');
      if (!viewer) return;
      var viewerContainer = viewer.querySelector('.sdk-viewer-container');
      if (!viewerContainer) return;
      container = document.createElement('div');
      container.className = 'sdk-current-path';
      var header = viewerContainer.querySelector('.sdk-viewer-header');
      if (header) header.parentNode.insertBefore(container, header.nextSibling);
      else viewerContainer.insertBefore(container, viewerContainer.firstChild);
    }
    if (!trail) {
      container.innerHTML = '';
      return;
    }
    var drawerLabel = labelText(trail.drawer.label);
    var sectionLabel = labelText(trail.section.label);
    var docTitle = book.title || '';
    container.innerHTML =
      '<nav class="sdk-breadcrumb">' +
        '<span class="sdk-breadcrumb-item">' + escHtml(drawerLabel) + '</span>' +
        '<span class="sdk-breadcrumb-sep"> › </span>' +
        '<span class="sdk-breadcrumb-item">' + escHtml(sectionLabel) + '</span>' +
        '<span class="sdk-breadcrumb-sep"> › </span>' +
        '<span class="sdk-breadcrumb-item sdk-breadcrumb-current">' + escHtml(docTitle) + '</span>' +
      '</nav>';
  }

  function updateSelectedDocumentState(book, trailOverride) {
    clearSelectedDocumentState();
    if (!book || !_libData) return;
    var trail = trailOverride || buildDocumentTrail(book);
    if (!trail) return;
    var drawerEl = document.querySelector('[data-drawer-id="' + CSS.escape(trail.drawer.id) + '"]');
    if (drawerEl) drawerEl.classList.add('sdk-selected');
    // Select section (or flat drawer head when no nested section UI)
    var sectionEl = null;
    if (drawerEl) sectionEl = drawerEl.querySelector('[data-section-id="' + CSS.escape(trail.section.id) + '"]');
    if (!sectionEl) sectionEl = document.querySelector('[data-section-id="' + CSS.escape(trail.section.id) + '"]');
    if (sectionEl) {
      sectionEl.classList.add('sdk-selected');
    } else if (drawerEl && drawerEl.classList.contains('flat')) {
      var flatHead = drawerEl.querySelector('.sdk-sidebar-group-head');
      if (flatHead) {
        flatHead.classList.add('sdk-selected');
        flatHead.classList.add('selected');
      }
    }
    var cards = document.querySelectorAll('.file-card');
    cards.forEach(function(c) {
      if (c.dataset.path === (book.path || '').toLowerCase()) {
        c.classList.add('sdk-selected');
      }
    });
  }

  function clearSelectedDocumentState() {
    document.querySelectorAll('.sdk-selected').forEach(function(el) {
      el.classList.remove('sdk-selected');
    });
  }

  function renderSearchSummary(query, count) {
    var container = document.querySelector('.sdk-search-summary');
    if (!container) {
      var topbar = document.querySelector('.sdk-topbar-center');
      if (!topbar) return;
      container = document.createElement('div');
      container.className = 'sdk-search-summary';
      topbar.appendChild(container);
    }
    if (!query) {
      container.textContent = '';
      container.style.display = 'none';
      return;
    }
    var text = _t(
      'Showing ' + count + ' result(s) for "' + query + '"',
      '"' + query + '" 검색 결과 ' + count + '개',
      '"' + query + '" の検索結果 ' + count + '件',
      '"' + query + '" 搜索结果 ' + count + '个',
      '"' + query + '" 搜尋結果 ' + count + '個',
      'Mostrando ' + count + ' resultado(s) para "' + query + '"'
    );
    container.textContent = text;
    container.style.display = '';
  }

  function clearSearchSummary() {
    var container = document.querySelector('.sdk-search-summary');
    if (container) {
      container.textContent = '';
      container.style.display = 'none';
    }
  }

  function retryLoadSdkData() {
    _libData = null;
    _sdkInitialized = false;
    initSdkLibrary();
  }

  function retryLoadDocument(book) {
    if (!book) return;
    openBookViewer(book, null, { updateUrl: false });
  }

  function renderSdkRetryAction(container, retryFn) {
    if (!container) return;
    var btn = document.createElement('button');
    btn.className = 'sdk-retry-btn';
    btn.textContent = _t('Retry', '재시도', '再試行', '重试', '重試', 'Reintentar');
    btn.addEventListener('click', retryFn);
    container.appendChild(btn);
  }

  async function checkPdfAvailability(path) {
    const res = await fetch('/api/sdk-pdf-status?path=' + encodeURIComponent(path));
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  }

  function renderPdfUnavailable(body, book, message) {
    if (!body) return;
    body.classList.remove('sdk-pdf-mode');
    var title = book && book.title ? escHtml(book.title) : '';
    var defaultMessage = _t(
      'PDF is not packaged with this release.',
      '이 릴리스에 PDF 파일이 포함되어 있지 않습니다.',
      'このリリースにはPDFファイルが含まれていません。',
      '此版本未包含 PDF 文件。',
      '此版本未包含 PDF 檔案。',
      'El PDF no está incluido en esta versión.'
    );
    body.innerHTML = '<div class="sdk-doc-error"><p>' + (message || defaultMessage) + '</p>' +
      (title ? '<p class="sdk-error-detail">' + title + '</p>' : '') + '</div>';
    renderSdkRetryAction(body.querySelector('.sdk-doc-error'), function() { retryLoadDocument(book); });
  }

  // Find a manifest file entry by its dx-all-suite-relative path (for cross-doc links).
  function findBookByPath(p) {
    if (!_libData || !_libData.drawers || !p) return null;
    for (const dr of _libData.drawers)
      for (const s of (dr.sections || []))
        for (const f of (s.files || []))
          if (f.path === p) return f;
    return null;
  }
  // Delegate clicks on in-doc .md links → open that doc in the viewer if it's in the library;
  // otherwise do nothing (never navigate to a dead raw .md path). Bound once per body.
  function bindDocLinks(body) {
    if (!body || body.dataset.doclinkBound === '1') return;
    body.dataset.doclinkBound = '1';
    body.addEventListener('click', function (e) {
      const a = e.target.closest && e.target.closest('a.sdk-doclink');
      if (!a) return;
      e.preventDefault();
      const book = findBookByPath(a.getAttribute('data-doc'));
      if (book) openBookViewer(book, null, { updateUrl: true });
    });
  }

  async function openBookViewer(book, drawerColor, options) {
    var opts = options || {};
    const viewer = document.getElementById('sdkBookViewer');
    if (!viewer) return;

    const titleEl = viewer.querySelector('.sdk-viewer-title');
    const pathEl = viewer.querySelector('.sdk-viewer-path');
    const body = document.getElementById('sdkViewerBody');
    if (titleEl) titleEl.textContent = '📖 ' + book.title;
    if (pathEl) pathEl.textContent = book.path;
    if (body) body.innerHTML = '<p class="sdk-viewer-loading">' + _t('Loading…', '로딩 중…', '読み込み中…', '加载中…', '載入中…', 'Cargando…') + '</p>';

    const colors = DRAWER_COLORS[drawerColor] || DRAWER_COLORS.blue;
    const container = viewer.querySelector('.sdk-viewer-container');
    if (container) {
      container.style.setProperty('--viewer-accent', colors.accent);
      container.style.setProperty('--viewer-accent-bg', colors.bg);
      container.style.setProperty('--viewer-accent-border', colors.border);
    }

    var trail = buildDocumentTrail(book);
    renderDocumentTrail(book, trail);
    updateSelectedDocumentState(book, trail);

    const searchInput = document.getElementById('sdkViewerSearch');
    const searchInfo = document.getElementById('sdkViewerSearchInfo');
    if (searchInput) searchInput.value = '';
    if (searchInfo) searchInfo.textContent = '';

    viewer.classList.add('open');
    if (opts.updateUrl !== false) {
      requestSdkUrlUpdate({ doc: book.path }, 'push');
    }
    if (book.type === 'pdf') {
      if (body) {
        body.classList.remove('sdk-pdf-mode');
        body.innerHTML = '<div class="sdk-viewer-loading">' +
          _t('Checking PDF availability...', 'PDF 파일 확인 중...', 'PDFを確認中...', '正在检查 PDF...', '正在檢查 PDF...', 'Verificando disponibilidad del PDF...') +
          '</div>';
      }
      try {
        const pdfInfo = await checkPdfAvailability(book.path);
        if (pdfInfo.available && pdfInfo.url) {
          if (body) {
            body.innerHTML = '<iframe src="' + escHtml(pdfInfo.url) + '" class="sdk-pdf-frame"></iframe>';
            body.classList.add('sdk-pdf-mode');
          }
        } else {
          renderPdfUnavailable(body, book);
        }
      } catch (e) {
        renderPdfUnavailable(
          body,
          book,
          _t('Failed to check PDF: ', 'PDF 확인 실패: ', 'PDF確認失敗: ', 'PDF 检查失败: ', 'PDF 檢查失敗: ', 'Error al verificar PDF: ') + escHtml(e.message)
        );
      }
      return;
    }

    try {
      const res = await fetch('/api/sdk-doc?path=' + encodeURIComponent(book.path));
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const md = await res.text();
      const html = mdToHtml(md, book.path);
      if (body) {
        body.classList.remove('sdk-pdf-mode');
        body.innerHTML = html;
        body.scrollTop = 0;
        renderMermaidBlocks(body);
        bindDocLinks(body);
      }
    } catch (e) {
      if (body) {
        body.innerHTML = '<div class="sdk-doc-error"><p>' + _t('Failed to load: ', '로드 실패: ', '読み込み失敗: ', '加载失败: ', '載入失敗: ', 'Error al cargar: ') + escHtml(e.message) + '</p></div>';
        renderSdkRetryAction(body.querySelector('.sdk-doc-error'), function() { retryLoadDocument(book); });
      }
    }
  }

  function closeBookViewer(options) {
    var opts = options || {};
    const viewer = document.getElementById('sdkBookViewer');
    var wasOpen = viewer && viewer.classList.contains('open');
    if (viewer) {
      viewer.classList.remove('open');
      const body = document.getElementById('sdkViewerBody');
      if (body) {
        body.innerHTML = '';
        body.classList.remove('sdk-pdf-mode');
        _clearSearchHighlights();
      }
      clearSelectedDocumentState();
    }
    const searchInput = document.getElementById('sdkViewerSearch');
    if (searchInput) searchInput.value = '';
    const searchInfo = document.getElementById('sdkViewerSearchInfo');
    if (searchInfo) searchInfo.textContent = '';
    if (wasOpen && opts.updateUrl !== false && !_applyingQuery) {
      requestSdkUrlUpdate({ doc: '' }, 'push');
    }
  }

  let _searchMatches = [];
  let _searchIdx = -1;

  function _clearSearchHighlights() {
    const body = document.getElementById('sdkViewerBody');
    if (!body) return;
    body.querySelectorAll('mark.sdk-search-hit').forEach(m => {
      const parent = m.parentNode;
      parent.replaceChild(document.createTextNode(m.textContent), m);
      parent.normalize();
    });
    _searchMatches = [];
    _searchIdx = -1;
  }

  function _doSearch(query) {
    _clearSearchHighlights();
    const body = document.getElementById('sdkViewerBody');
    const info = document.getElementById('sdkViewerSearchInfo');
    if (!body || !query) {
      if (info) info.textContent = '';
      return;
    }

    const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT, null, false);
    const textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);

    const lowerQ = query.toLowerCase();
    const matches = [];

    for (const node of textNodes) {
      const text = node.textContent;
      const lowerText = text.toLowerCase();
      let idx = 0;
      const fragments = [];
      let lastEnd = 0;

      while ((idx = lowerText.indexOf(lowerQ, idx)) !== -1) {
        if (idx > lastEnd) {
          fragments.push({ type: 'text', value: text.slice(lastEnd, idx) });
        }
        fragments.push({ type: 'match', value: text.slice(idx, idx + query.length) });
        lastEnd = idx + query.length;
        idx = lastEnd;
      }

      if (fragments.length > 0) {
        if (lastEnd < text.length) {
          fragments.push({ type: 'text', value: text.slice(lastEnd) });
        }
        const parent = node.parentNode;
        const frag = document.createDocumentFragment();
        for (const f of fragments) {
          if (f.type === 'text') {
            frag.appendChild(document.createTextNode(f.value));
          } else {
            const mark = document.createElement('mark');
            mark.className = 'sdk-search-hit';
            mark.textContent = f.value;
            matches.push(mark);
            frag.appendChild(mark);
          }
        }
        parent.replaceChild(frag, node);
      }
    }

    _searchMatches = matches;
    _searchIdx = matches.length > 0 ? 0 : -1;

    if (info) {
      info.textContent = matches.length > 0
        ? (1) + '/' + matches.length
        : _t('No results', '결과 없음', '結果なし', '无结果', '無結果', 'Sin resultados');
    }

    if (matches.length > 0) {
      matches[0].classList.add('current');
      matches[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  function _searchNext() {
    if (_searchMatches.length === 0) return;
    _searchMatches[_searchIdx].classList.remove('current');
    _searchIdx = (_searchIdx + 1) % _searchMatches.length;
    _searchMatches[_searchIdx].classList.add('current');
    _searchMatches[_searchIdx].scrollIntoView({ behavior: 'smooth', block: 'center' });
    const info = document.getElementById('sdkViewerSearchInfo');
    if (info) info.textContent = (_searchIdx + 1) + '/' + _searchMatches.length;
  }

  function _searchPrev() {
    if (_searchMatches.length === 0) return;
    _searchMatches[_searchIdx].classList.remove('current');
    _searchIdx = (_searchIdx - 1 + _searchMatches.length) % _searchMatches.length;
    _searchMatches[_searchIdx].classList.add('current');
    _searchMatches[_searchIdx].scrollIntoView({ behavior: 'smooth', block: 'center' });
    const info = document.getElementById('sdkViewerSearchInfo');
    if (info) info.textContent = (_searchIdx + 1) + '/' + _searchMatches.length;
  }

  function toggleArchOverlay() {
    const overlay = document.getElementById('sdkArchOverlay');
    if (overlay) overlay.classList.toggle('open');
  }

  function handleKeydown(e) {
    const viewer = document.getElementById('sdkBookViewer');
    if (viewer && viewer.classList.contains('open')) {
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.getElementById('sdkViewerSearch');
        if (searchInput) searchInput.focus();
        return;
      }
      if (e.key === 'Escape') {
        closeBookViewer();
        e.preventDefault();
        if (e.stopImmediatePropagation) e.stopImmediatePropagation();
        else e.stopPropagation();
      }
      return;
    }
    const archOverlay = document.getElementById('sdkArchOverlay');
    if (archOverlay && archOverlay.classList.contains('open')) {
      if (e.key === 'Escape') {
        toggleArchOverlay();
        e.preventDefault();
        if (e.stopImmediatePropagation) e.stopImmediatePropagation();
        else e.stopPropagation();
      }
      return;
    }
    // Defensive symmetry: launcher.js fires first for SDK root Escape (its
    // hardcoded guards return early), so stopImmediatePropagation below is a
    // no-op in current listener order.  Kept for consistency with the viewer
    // and overlay branches, and as a safety net if registration order changes.
    const libView = document.getElementById('sdk-library-view');
    if (libView && libView.classList.contains('visible')) {
      if (e.key === 'Escape') {
        hideSdkLibraryView();
        e.preventDefault();
        if (e.stopImmediatePropagation) e.stopImmediatePropagation();
        else e.stopPropagation();
      }
    }
  }

  function _refreshViewerChrome() {
    var closeBtn = document.querySelector('.sdk-viewer-close');
    if (closeBtn) closeBtn.title = _t('Close', '닫기', '閉じる', '关闭', '關閉', 'Cerrar');
  }

  function renderSdkError(error) {
    var container = document.getElementById('sdkCabinet');
    if (!container) return;
    container.innerHTML = '<div class="sdk-error">' +
      '<p class="sdk-error-message">' +
      _t('Failed to load SDK Library data.', 'SDK 라이브러리 데이터 로드 실패.', 'SDKライブラリデータの読み込みに失敗しました。', 'SDK资料加载失败。', 'SDK資料載入失敗。', 'Error al cargar datos de la biblioteca SDK.') +
      '</p>' +
      '<p class="sdk-error-detail">' + (error || '') + '</p>' +
      '</div>';
    var errEl = container.querySelector('.sdk-error');
    // sdk-retry-btn appended by renderSdkRetryAction
    renderSdkRetryAction(errEl, retryLoadSdkData);
  }

  function registerLanguageHook() {
    if (_languageHookRegistered) return;
    if (typeof DXI18n !== 'undefined' && typeof DXI18n.onLangChange === 'function') {
      DXI18n.onLangChange(function () {
        _refreshViewerChrome();
        var viewer = document.getElementById('sdkBookViewer');
        if (viewer && viewer.classList.contains('open') && _currentQueryState.doc) {
          var book = findBookByPath(_currentQueryState.doc);
          if (book) renderDocumentTrail(book);
        }

        if (_libData) renderView(_libData);
      });
      _languageHookRegistered = true;
    }
  }

  function restoreLauncherToolbarOwner(options) {
    var opts = options || {};
    if (window.SDKTutorial && typeof window.SDKTutorial.beforeLeave === 'function') {
      window.SDKTutorial.beforeLeave();
    }
    if (typeof DXToolbar !== 'undefined' && typeof DXToolbar.disconnectTutorial === 'function') {
      DXToolbar.disconnectTutorial('sdk_library');
    }
    if (window._dxTutorialSuspended &&
        window._dxTutorialSuspended.appId === 'launcher') {
      window._dxTutorial = window._dxTutorialSuspended;
      window._dxTutorialSuspended = null;
    } else if (window._dxTutorial &&
               window._dxTutorial.appId === 'sdk_library') {
      window._dxTutorial = null;
    }
    if (typeof DXTutorialEngine !== 'undefined' &&
        typeof DXTutorialEngine.purgeOrphanChrome === 'function') {
      DXTutorialEngine.purgeOrphanChrome(document, window._dxTutorial || null);
    }
    if (opts.restoreToolbar === false) return;
    if (typeof DXToolbar === 'undefined' || typeof DXToolbar.connectTutorial !== 'function') return;
    if (window.LauncherTutorial && typeof window.LauncherTutorial.connectToolbar === 'function') {
      window.LauncherTutorial.connectToolbar();
      return;
    }
    // Launcher tutorial engine이 없을 때만 튜토리얼 토글을 복구한다.
    DXToolbar.connectTutorial({
      toggleTOC: function() { if (window._dxTutorialMode) window._dxTutorialMode.toggle(); },
      _toggleBtnEl: null
    }, { owner: 'launcher' });
  }

  async function initSdkLibrary() {
    if (_sdkInitialized) return;
    try {
      var data = await loadLibraryData();
      if (!data) throw new Error('No data returned');
      renderView(data);

      var viewerClose = document.querySelector('.sdk-viewer-close');
      if (viewerClose) {
        viewerClose.addEventListener('click', closeBookViewer);
      }
      _refreshViewerChrome();

      var searchInput = document.getElementById('sdkViewerSearch');
      if (searchInput) {
        var _searchTimeout = null;
        searchInput.addEventListener('input', function() {
          clearTimeout(_searchTimeout);
          _searchTimeout = setTimeout(function() { _doSearch(searchInput.value.trim()); }, 250);
        });
        searchInput.addEventListener('keydown', function(e) {
          if (e.key === 'Enter') {
            e.preventDefault();
            if (e.shiftKey) _searchPrev();
            else _searchNext();
          }
          if (e.key === 'Escape') {
            searchInput.value = '';
            _clearSearchHighlights();
            var info = document.getElementById('sdkViewerSearchInfo');
            if (info) info.textContent = '';
          }
        });
      }

      if (!_keydownBound) {
        document.addEventListener('keydown', handleKeydown);
        _keydownBound = true;
      }
      _sdkInitialized = true;
      registerLanguageHook();
      // Flush pending query from applyQuery called before data was loaded
      if (_pendingQuery) {
        var pq = _pendingQuery;
        _pendingQuery = null;
        applyQuery(pq.raw, pq.options);
      }
    } catch (e) {
      renderSdkError(e.message || String(e));
    }
  }

  function showSdkLibrary() {
    var view = document.getElementById('sdk-library-view');
    if (view) {
      view.classList.add('visible');
      if (!_sdkInitialized) initSdkLibrary();
      if (window.SDKTutorial && typeof window.SDKTutorial.connectToolbar === 'function') {
        window.SDKTutorial.connectToolbar();
      }
    }
  }

  function hideSdkLibraryView(options) {
    var opts = options || {};
    var view = document.getElementById('sdk-library-view');
    if (view) view.classList.remove('visible');
    if (opts.restoreToolbar !== false) restoreLauncherToolbarOwner();
  }

  function closeSdkLibrary() {
    hideSdkLibraryView();
  }

  window.SDKLibrary = {
    init: initSdkLibrary,
    refresh: function () { if (_libData) renderView(_libData); },
    reset: function () { _sdkInitialized = false; _libData = null; },
    applyQuery: applyQuery
  };
  window.showSdkLibrary = function () {
    if (window.LauncherRouter) window.LauncherRouter.navigate('sdk-library');
    else showSdkLibrary();
  };
  window.hideSdkLibraryView = hideSdkLibraryView;
  window.closeSdkLibrary = closeSdkLibrary;
  window._sdkLibHasViewer = function () {
    var v = document.getElementById('sdkBookViewer');
    return v && v.classList.contains('open');
  };
  window._sdkLibHasOverlay = function () {
    var o = document.getElementById('sdkArchOverlay');
    return o && o.classList.contains('open');
  };
  window._sdkLib = {
    switchView: switchView,
    openDrawer: openDrawer,
    closeDrawer: closeDrawer,
    openBookViewer: openBookViewer,
    getLibData: function () { return _libData; }
  };
})();
