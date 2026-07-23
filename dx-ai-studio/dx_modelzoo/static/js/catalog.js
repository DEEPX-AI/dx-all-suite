'use strict';

// 전역 상태 (기존 app/message handler가 참조)
let _viewMode = 'card';
let _selectedCategories = [];
let _allModels = [];
let _allCategories = {};
let _sortField = 'name';
let _sortDir = 'asc';

const PAGE_SIZE = 60;
const MAX_CACHED_PAGES = 20;
const CARD_ESTIMATED_HEIGHT = 300;
const LIST_ROW_HEIGHT = 48;
const OVERSCAN_ROWS = 3;
const CARD_DOM_LIMIT = 50;
const LIST_ROW_DOM_LIMIT = 100;

// 최적화 이미지 헬퍼 (Task 9) — window에 노출하여 detail.js와 공유

function optimizedImageCandidates(originalPath) {
  if (!originalPath) return [];
  const clean = originalPath.replace(/^\/?data\//, '');
  const dot = clean.lastIndexOf('.');
  const stem = dot >= 0 ? clean.slice(0, dot) : clean;
  const ext = dot >= 0 ? clean.slice(dot + 1).toLowerCase() : 'img';
  const safeStem = `${stem}-${ext}`;
  return [
    `/data/optimized/${safeStem}.webp`,
    `/data/optimized/${safeStem}.jpg`,
    `/data/${clean}`,
  ];
}

function imageTagWithFallback(originalPath, alt, className) {
  const candidates = optimizedImageCandidates(originalPath);
  const first = candidates.shift() || '';
  const encoded = JSON.stringify(candidates);
  const cls = className || '';
  return `<img src="${_escapeAttr(first)}" alt="${_escapeAttr(alt)}" class="${_escapeAttr(cls)}" loading="lazy" decoding="async" data-fallbacks='${_escapeAttr(encoded)}' onerror="handleImageFallback(this)">`;
}

function handleImageFallback(img) {
  const fallbacks = JSON.parse(img.dataset.fallbacks || '[]');
  const next = fallbacks.shift();
  if (next) {
    img.dataset.fallbacks = JSON.stringify(fallbacks);
    img.src = next;
    return;
  }
  img.onerror = null;
  const cardThumb = img.closest('.mz-card-thumb');
  if (cardThumb) {
    // Grid card: the category icon glyph is already rendered as a sibling of the
    // <img> — just drop the broken image and let CSS (.mz-card-thumb.no-thumb)
    // center the existing icon in its place.
    cardThumb.classList.add('no-thumb');
    img.remove();
    return;
  }
  // Detail-page example/thumbnail images have no such sibling icon to fall back
  // on, so swap the broken <img> for an explicit placeholder box (icon + label)
  // instead of just removing it — a missing asset should look intentional, not
  // like a layout hole or a broken-image icon.
  const placeholder = document.createElement('div');
  placeholder.className = 'mz-img-placeholder' + (img.className ? ' ' + img.className : '');
  const icon = document.createElement('span');
  icon.className = 'mz-img-placeholder-icon';
  icon.textContent = '🖼️';
  placeholder.appendChild(icon);
  if (img.alt) {
    const label = document.createElement('span');
    label.className = 'mz-img-placeholder-label';
    label.textContent = img.alt;
    placeholder.appendChild(label);
  }
  img.replaceWith(placeholder);
}

function _escapeAttr(s) {
  if (s == null) return '';
  return String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

window.handleImageFallback = handleImageFallback;
window.ModelZooImages = { optimizedImageCandidates, imageTagWithFallback, handleImageFallback };


function _localLabel(obj, prefix) {
  const lang = DXI18n.lang;
  const direct = obj[prefix + '_' + lang] || obj[prefix + '_' + lang.split('-')[0]];
  if (direct) return direct;
  // The category data only ships label_en + label_ko. For ja/zh-CN/zh-TW/es fall back to
  // the shared i18n dict (which has all 6 languages for the category names) keyed by the
  // English label — otherwise the category column/chips stay English in those languages.
  const en = obj[prefix + '_en'] || '';
  return en ? T(en) : '';
}

function _localText(obj) {
  if (!obj) return '';
  const lang = DXI18n.lang;
  return obj[lang] || obj[lang.split('-')[0]] || obj.en || '';
}

function _missingLabel(label) {
  return `<span class="mz-field-empty">${_escapeAttr(T(label))}</span>`;
}

function _modelInputResolution(m) {
  const spec = m.specification || {};
  if (spec.input_resolution) return spec.input_resolution;
  if (spec.input_width && spec.input_height) return `${spec.input_width}x${spec.input_height}`;
  if (Array.isArray(spec.input_shape)) return spec.input_shape.join('x');
  return '';
}

function _modelMetricText(metric) {
  if (!metric) return '';
  if (typeof metric === 'object') {
    if (metric.name) return metric.name;
    return Object.entries(metric).map(([k, v]) => `${k}: ${v}`).join(', ');
  }
  return metric;
}

function _bestAccuracyValue(m) {
  const evaluation = m.evaluation || {};
  const legacyMetric = m.specification?.metric;
  for (const key of ['raw', 'onnx', 'qlite', 'qpro']) {
    if (evaluation[key]?.source_status === 'suspect') continue;
    const value = evaluation[key]?.accuracy;
    if (value != null && value !== '') return value;
  }
  if (legacyMetric && typeof legacyMetric === 'object') {
    return legacyMetric.mAP ?? legacyMetric['Top-1'] ?? Object.values(legacyMetric)[0] ?? '';
  }
  return legacyMetric || '';
}

function _modelFpsText(m) {
  const performance = m.performance || {};
  const fps = performance.fps ?? m.specification?.fps;
  if (fps != null && fps !== '') return `${fps} FPS`;
  return T('Benchmark required');
}

function _modelFpsClass(m) {
  const performance = m.performance || {};
  const fps = performance.fps ?? m.specification?.fps;
  return fps != null && fps !== '' ? 'mz-card-fps' : 'mz-card-status missing';
}

function _variantRootId(modelId) {
  const value = String(modelId || '').trim();
  if (!value) return '';
  const matched = value.match(/^(.*)-(\d+)$/);
  if (matched && matched[1]) return matched[1];
  return value;
}

function _computeUniqueModelCount(models) {
  const unique = new Set();
  (models || []).forEach(model => {
    if (!model || !model.id) return;
    unique.add(_variantRootId(model.id));
  });
  return unique.size || (models || []).length;
}

function _artifactAvailable(m, artifactId) {
  const artifact = (m.artifacts || {})[artifactId] || {};
  if (artifact.available === false) return false;
  return artifact.available === true ||
    Boolean(artifact.download_endpoint || artifact.local_path || artifact.remote_url);
}

function _artifactBadge(m, artifactId, label) {
  const available = _artifactAvailable(m, artifactId);
  const status = available ? 'ready' : 'not-ready';
  const icon = available ? '✅' : '⏳';
  const title = available ? label : T('Artifact unavailable');
  return `<span class="mz-download-badge ${status}" title="${_escapeAttr(title)}">${icon} ${_escapeAttr(label)}</span>`;
}

function _artifactBadges(m) {
  const qlite = _artifactAvailable(m, 'qlite_dxnn') || _artifactAvailable(m, 'qlite_json') ||
    m.downloaded_qlite || m.downloaded;
  const qpro = _artifactAvailable(m, 'qpro_dxnn') || _artifactAvailable(m, 'qpro_json') ||
    m.downloaded_qpro;
  const artifacts = {
    qlite_dxnn: qlite ? { available: true } : (m.artifacts || {}).qlite_dxnn,
    qpro_dxnn: qpro ? { available: true } : (m.artifacts || {}).qpro_dxnn,
  };
  return [
    _artifactBadge({ artifacts }, 'qlite_dxnn', 'Q-Lite'),
    _artifactBadge({ artifacts }, 'qpro_dxnn', 'Q-Pro'),
  ].join(' ');
}

function _licenseBadge(m) {
  const cu = m.legal && m.legal.commercial_use;
  if (cu !== 'non-commercial' && cu !== 'restricted') return '';
  const label = cu === 'non-commercial' ? T('Non-commercial') : T('License: review');
  const title = cu === 'non-commercial'
    ? T('Commercial use prohibited')
    : T('Commercial use requires license review');
  return `<span class="mz-license-badge ${cu}" title="${_escapeAttr(title)}">⚠ ${_escapeAttr(label)}</span>`;
}

function _commitCatalogStateSave(state) {
  sessionStorage.setItem('modelzooCatalogState', JSON.stringify(state));
}

const ModelZooVirtualCatalog = {
  pageCache: new Map(),
  lru: [],
  total: 0,
  pageSize: PAGE_SIZE,
  queryKey: '',
  scrollTop: 0,
  _viewMode: 'card',
  _container: null,
  _filteredModels: [],
  _pendingPages: new Set(),

  _scrollBound: false,
  _modelNavigationBound: false,
  _listSortBound: false,
  _rafTicking: false,
  _lastViewportSignature: '',
  _lastViewportHtml: '',
  _stateSaveTimer: null,
  _measuredCardHeight: null,

  init(dataOrMeta) {
    try {
      if (dataOrMeta) {
        _allModels = dataOrMeta.models || _allModels;
        _allCategories = dataOrMeta.categories || _allCategories;
      }
      this._container = document.getElementById('catalogContainer');
      this._viewMode = _viewMode;
      this._bindScroll();
      this._bindModelNavigation();
      this._bindListSortEvents();
      this._restoreState();
      syncCatalogControls();
      renderCategoryChips();
      this.resetAndRender();
      updateActiveFilterSummary();
    } catch (e) {
      console.warn('[ModelZoo] init 오류:', e);
      this._showError();
    }
  },

  _bindScroll() {
    const container = this._container;
    if (!container || this._scrollBound) return;
    const self = this;
    const onScroll = function() {
      if (!self._rafTicking) {
        self._rafTicking = true;
        requestAnimationFrame(() => {
          self.renderViewport();
          self._rafTicking = false;
        });
      }
    };
    container.addEventListener('scroll', onScroll);
    window.addEventListener('scroll', onScroll);
    window.addEventListener('resize', () => {
      this._measuredCardHeight = null;
      onScroll();
    });
    this._scrollBound = true;
  },

  _bindModelNavigation() {
    const container = this._container;
    if (!container || this._modelNavigationBound) return;
    container.addEventListener('click', event => {
      if (!event.target || typeof event.target.closest !== 'function') return;
      const target = event.target.closest('[data-model-id]');
      if (!target || !container.contains(target)) return;
      const modelId = target.dataset.modelId || '';
      if (!modelId) return;
      location.hash = 'model=' + encodeURIComponent(modelId);
    });
    this._modelNavigationBound = true;
  },

  _bindListSortEvents() {
    const container = this._container;
    if (!container || this._listSortBound) return;
    container.addEventListener('click', event => {
      if (!event.target || typeof event.target.closest !== 'function') return;
      const target = event.target.closest('[data-sort-key]');
      if (!target || !container.contains(target)) return;
      onListHeaderClick(target.dataset.sortKey || '');
    });
    this._listSortBound = true;
  },

  _getEffectiveScrollTop() {
    const container = this._container;
    if (!container) return 0;
    // container가 자체 스크롤 컨테이너인 경우
    const style = window.getComputedStyle ? window.getComputedStyle(container) : {};
    const overflowY = style.overflowY || '';
    if (container.scrollHeight > container.clientHeight &&
        (overflowY === 'auto' || overflowY === 'scroll')) {
      return container.scrollTop || 0;
    }
    // window 스크롤 모드: container의 문서 내 위치를 기준으로 계산
    const rect = container.getBoundingClientRect();
    const containerDocTop = rect.top + window.scrollY;
    return Math.max(0, window.scrollY - containerDocTop);
  },

  setViewMode(mode) {
    this._measuredCardHeight = null;
    this._viewMode = mode;
    _viewMode = mode;
    this.pageCache.clear();
    this.lru.length = 0;
    this.renderViewport();
  },

  setQuery(query) {
    const newKey = query || '';
    if (this.queryKey !== newKey) {
      this.queryKey = newKey;
      this.pageCache.clear();
      this.lru.length = 0;
    }
  },

  resetAndRender() {
    this._measuredCardHeight = null;
    this._filteredModels = this._applyFilters();
    this.total = this._filteredModels.length;
    if (!this._container) return;
    if (this.total === 0) {
      this._container.innerHTML = `<div class="mz-placeholder">${T('No models found')}</div>`;
      return;
    }
    this.renderViewport();
  },

  _applyFilters() {
    let models = _allModels;
    if (_selectedCategories.length > 0) {
      models = models.filter(m => _selectedCategories.includes(m.category) ||
        (_selectedCategories.includes('__unknown__') && !hasCategory(m.category)));
    }
    const q = (document.getElementById('searchInput')?.value || '').toLowerCase();
    if (q) {
      models = models.filter(m =>
        m.id.toLowerCase().includes(q) ||
        m.name.toLowerCase().includes(q) ||
        (m.class_name || '').toLowerCase().includes(q)
      );
    }
    return sortModels(models);
  },

  // loadPage: 서버 페이지 fetch 경로 — API 기반 가상화/향후 점진적 로딩용으로 유지
  async loadPage(page) {
    const cacheKey = this._cacheKey(page);
    if (this.pageCache.has(cacheKey)) {
      this._touchLru(cacheKey);
      return this.pageCache.get(cacheKey);
    }
    if (this._pendingPages.has(cacheKey)) return null;
    this._pendingPages.add(cacheKey);
    try {
      const q = (document.getElementById('searchInput')?.value || '').trim();
      const cats = [..._selectedCategories].sort().join(',');
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(this.pageSize),
        search: q,
        category: cats,
        sort: _sortField,
        dir: _sortDir,
      });
      const resp = await fetch(modelzooApiUrl(`/api/catalog/page?${params.toString()}`));
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      if (!data.ok) throw new Error(data.error || 'API error');
      const models = data.models || [];
      this.pageCache.set(cacheKey, models);
      this._touchLru(cacheKey);
      this._evictLru();
      this.total = data.total ?? this.total;
      return models;
    } catch (e) {
      console.warn(`[ModelZoo] loadPage(${page}) 실패:`, e);
      return null;
    } finally {
      this._pendingPages.delete(cacheKey);
    }
  },

  _cacheKey(page) {
    const q = (document.getElementById('searchInput')?.value || '').trim();
    const cats = [..._selectedCategories].sort().join(',');
    return `${q}|${cats}|${_sortField}|${_sortDir}|${page}`;
  },

  _touchLru(key) {
    const idx = this.lru.indexOf(key);
    if (idx >= 0) this.lru.splice(idx, 1);
    this.lru.push(key);
  },

  _evictLru() {
    while (this.lru.length > MAX_CACHED_PAGES) {
      const old = this.lru.shift();
      this.pageCache.delete(old);
    }
  },

  getVisibleRange(scrollTop, viewportHeight) {
    const models = this._filteredModels;
    if (!models.length) return { start: 0, end: 0 };
    if (this._viewMode === 'list') {
      const rawStartRow = Math.max(0, Math.floor(scrollTop / LIST_ROW_HEIGHT) - OVERSCAN_ROWS);
      const visibleRows = Math.ceil(viewportHeight / LIST_ROW_HEIGHT) + 2 * OVERSCAN_ROWS;
      const boundedRows = Math.min(visibleRows, LIST_ROW_DOM_LIMIT);
      const maxStartRow = Math.max(0, models.length - boundedRows);
      const startRow = Math.min(rawStartRow, maxStartRow);
      const endRow = Math.min(models.length, startRow + boundedRows);
      return { start: startRow, end: endRow };
    }
    const container = this._container;
    const containerWidth = container ? container.clientWidth : 960;
    const minCardWidth = 260;
    const cols = Math.max(1, Math.floor(containerWidth / minCardWidth));
    const cardH = this._getCardHeight();
    const rawStartRow = Math.max(0, Math.floor(scrollTop / cardH) - OVERSCAN_ROWS);
    const visibleRows = Math.ceil(viewportHeight / cardH) + 2 * OVERSCAN_ROWS;
    const totalRows = Math.ceil(models.length / cols);
    const rowsByLimit = Math.max(1, Math.floor(CARD_DOM_LIMIT / cols));
    const windowRows = Math.min(visibleRows, rowsByLimit);
    const maxStartRow = Math.max(0, totalRows - windowRows);
    const startRow = Math.min(rawStartRow, maxStartRow);
    const startIdx = startRow * cols;
    const endIdx = Math.min(models.length, startIdx + windowRows * cols, startIdx + CARD_DOM_LIMIT);
    return { start: startIdx, end: endIdx };
  },

  renderViewport() {
    const container = this._container;
    if (!container) return;
    const models = this._filteredModels;
    if (!models.length) {
      container.innerHTML = `<div class="mz-placeholder">${T('No models found')}</div>`;
      return;
    }

    try {
      const scrollTop = this._getEffectiveScrollTop();
      const viewportHeight = container.clientHeight || window.innerHeight || 800;
      const { start, end } = this.getVisibleRange(scrollTop, viewportHeight);

      if (this._viewMode === 'card') {
        this._renderCardViewport(container, models, start, end);
      } else {
        this._renderListViewport(container, models, start, end);
      }
      this._saveState();
    } catch (e) {
      console.warn('[ModelZoo] renderViewport 오류:', e);
      this._showError();
    }
  },

  _commitViewportHtml(container, html, savedScrollTop, signature) {
    if (this._lastViewportSignature === signature &&
        this._lastViewportHtml === html &&
        container.dataset.viewportSignature === signature) {
      if (this._isContainerScrollable() && container.scrollTop !== savedScrollTop) {
        container.scrollTop = savedScrollTop;
      }
      return;
    }
    container.innerHTML = html;
    container.dataset.viewportSignature = signature;
    this._lastViewportSignature = signature;
    this._lastViewportHtml = html;
    if (this._isContainerScrollable() && container.scrollTop !== savedScrollTop) {
      container.scrollTop = savedScrollTop;
    }
  },

  _getCardHeight() {
    return this._measuredCardHeight || CARD_ESTIMATED_HEIGHT;
  },

  _measureCardHeight(container) {
    if (this._measuredCardHeight) return;
    if (!container || !container.isConnected) return;
    const cards = container.querySelectorAll('.mz-card-item');
    if (cards.length === 0) return;
    let total = 0;
    let count = 0;
    const limit = Math.min(cards.length, 6);
    for (let i = 0; i < limit; i++) {
      const h = cards[i].offsetHeight;
      if (h > 0) { total += h; count++; }
    }
    if (count > 0) {
      this._measuredCardHeight = Math.round(total / count);
      this.renderViewport();
    }
  },

  _renderCardViewport(container, models, start, end) {
    container.className = 'mz-card-grid';
    const visible = models.slice(start, end);
    const beforeCount = start;
    const afterCount = Math.max(0, models.length - end);

    const containerWidth = container.clientWidth || 960;
    const minCardWidth = 260;
    const cols = Math.max(1, Math.floor(containerWidth / minCardWidth));
    const beforeRows = Math.ceil(beforeCount / cols);
    const afterRows = Math.ceil(afterCount / cols);
    const cardH = this._getCardHeight();

    let html = '';
    if (beforeRows > 0) {
      html += `<div class="mz-spacer" style="height:${beforeRows * cardH}px;grid-column:1/-1"></div>`;
    }
    visible.forEach(m => { html += this.renderCardItem(m); });
    if (afterRows > 0) {
      html += `<div class="mz-spacer" style="height:${afterRows * cardH}px;grid-column:1/-1"></div>`;
    }
    const savedScrollTop = container.scrollTop || 0;
    const signature = ['card', start, end, models.length, beforeRows, afterRows].join(':');
    this._commitViewportHtml(container, html, savedScrollTop, signature);
    // Measure actual card heights after first render to reduce scroll jumps
    if (!this._measuredCardHeight) {
      requestAnimationFrame(() => this._measureCardHeight(container));
    }
  },

  _renderListViewport(container, models, start, end) {
    container.className = '';
    const visible = models.slice(start, end);
    const headers = [
      { key: 'name', label: T('Name') },
      { key: 'category', label: T('Category') },
      { key: 'fps', label: 'FPS' },
      { key: 'resolution', label: T('Input Resolution') },
      { key: 'accuracy', label: T('Accuracy') },
      { key: 'status', label: T('Status') },
    ];
    let html = '<table class="mz-list-table"><thead><tr>';
    headers.forEach(h => {
      const arrow = _sortField === h.key ? (_sortDir === 'asc' ? ' ▲' : ' ▼') : '';
      html += `<th data-sort-key="${_escapeAttr(h.key)}">${_escapeAttr(h.label)}${arrow}</th>`;
    });
    html += '</tr></thead><tbody>';

    const beforeHeight = start * LIST_ROW_HEIGHT;
    const afterHeight = Math.max(0, models.length - end) * LIST_ROW_HEIGHT;

    if (beforeHeight > 0) {
      html += `<tr class="mz-spacer"><td colspan="6" style="height:${beforeHeight}px;padding:0;border:none"></td></tr>`;
    }
    visible.forEach(m => { html += this.renderListRow(m); });
    if (afterHeight > 0) {
      html += `<tr class="mz-spacer"><td colspan="6" style="height:${afterHeight}px;padding:0;border:none"></td></tr>`;
    }
    html += '</tbody></table>';
    const savedScrollTop = container.scrollTop || 0;
    const signature = ['list', start, end, models.length, beforeHeight, afterHeight, _sortField, _sortDir].join(':');
    this._commitViewportHtml(container, html, savedScrollTop, signature);
  },

  _isContainerScrollable() {
    const container = this._container;
    if (!container) return false;
    const style = window.getComputedStyle ? window.getComputedStyle(container) : {};
    const overflowY = style.overflowY || '';
    return container.scrollHeight > container.clientHeight &&
           (overflowY === 'auto' || overflowY === 'scroll');
  },

  renderCardItem(m) {
    const catInfo = _allCategories[m.category] || {};
    const catLabel = _localLabel(catInfo, 'label') || m.category;
    const icon = _escapeAttr(catInfo.icon || '🤖');
    const categoryIcon = _escapeAttr(catInfo.icon || '');
    const legacyFps = m.specification?.fps ? `<span class="mz-card-fps">${_escapeAttr(m.specification.fps)} FPS</span>` : '';
    const fps = `<span class="${_escapeAttr(_modelFpsClass(m))}">${_escapeAttr(_modelFpsText(m))}</span>` || legacyFps;
    const resolution = _modelInputResolution(m);
    const missing = Array.isArray(m.missing) ? m.missing : [];
    const missingCount = missing.length;
    const summary = _localText(m.display?.summary) || _localText(m.content?.use_case) || '';
    const thumbImg = m.thumbnail
      ? imageTagWithFallback(m.thumbnail, m.name)
      : '';
    return `
    <div class="mz-card" data-model-id="${_escapeAttr(m.id)}" data-help-id="model-card-${_escapeAttr(m.id)}">
      <div class="mz-card-thumb">${icon}${thumbImg}</div>
      <div class="mz-card-body">
        <div class="mz-card-name" title="${_escapeAttr(m.id)}">${_escapeAttr(m.name)}</div>
        <div class="mz-card-cat">${categoryIcon} ${_escapeAttr(catLabel)}</div>
        ${_licenseBadge(m)}
        ${summary ? `<div class="mz-card-summary">${_escapeAttr(summary)}</div>` : ''}
        <div class="mz-card-meta">
          ${fps}
          <span>${resolution ? _escapeAttr(resolution) : _missingLabel('Not provided by source')}</span>
        </div>
        <div class="mz-card-artifacts">${_artifactBadges(m)}</div>
        ${missingCount ? `<div class="mz-card-missing">${_escapeAttr(missingCount)} ${_escapeAttr(T('Not provided by source'))}</div>` : ''}
      </div>
    </div>`;
  },

  renderListRow(m) {
    const catInfo = _allCategories[m.category] || {};
    const catLabel = _localLabel(catInfo, 'label') || m.category;
    const categoryIcon = _escapeAttr(catInfo.icon || '');
    const metric = m.specification?.metric;
    let accuracy = '';
    if (metric) {
      if (typeof metric === 'object') {
        const firstVal = metric.mAP ?? metric['Top-1'] ?? Object.values(metric)[0];
        if (firstVal != null) accuracy = firstVal;
      } else accuracy = metric;
    }
    const legacyFps = _escapeAttr(m.specification?.fps || '-');
    const fpsText = _modelFpsText(m) || legacyFps;
    const resolution = _modelInputResolution(m);
    const accuracyText = _bestAccuracyValue(m) || accuracy;
    let statusBadges = '—';
    if (m.artifacts || m.downloaded_qlite || m.downloaded_qpro || m.downloaded) {
      statusBadges = _artifactBadges(m);
    } else if ((m.missing || []).length) {
      statusBadges = `<span class="mz-card-status missing">${_escapeAttr(T('Not provided by source'))}</span>`;
    }
    return `<tr class="mz-list-row" data-model-id="${_escapeAttr(m.id)}" data-help-id="model-row-${_escapeAttr(m.id)}">
      <td>${_escapeAttr(m.name)}</td>
      <td><span class="mz-card-cat">${categoryIcon} ${_escapeAttr(catLabel)}</span></td>
      <td>${_escapeAttr(fpsText)}</td>
      <td>${resolution ? _escapeAttr(resolution) : _missingLabel('Not provided by source')}</td>
      <td>${accuracyText ? _escapeAttr(String(accuracyText)) : _missingLabel('Not provided by source')}</td>
      <td>${statusBadges}${_licenseBadge(m)}</td>
    </tr>`;
  },

  _showError() {
    const container = this._container;
    if (!container) return;
    container.innerHTML = `<div class="mz-catalog-error">
      <p>${T('Failed to load catalog')}</p>
      <button class="mz-btn mz-btn-outline" onclick="ModelZooVirtualCatalog.resetAndRender()">↻ ${T('Retry')}</button>
    </div>`;
  },

  _saveState() {
    try {
      const state = {
        search: (document.getElementById('searchInput')?.value || ''),
        categories: _selectedCategories,
        sort: _sortField,
        dir: _sortDir,
        viewMode: _viewMode,
        scrollTop: this._container?.scrollTop || 0,
      };
      if (this._stateSaveTimer) clearTimeout(this._stateSaveTimer);
      this._stateSaveTimer = setTimeout(() => {
        this._stateSaveTimer = null;
        _commitCatalogStateSave(state);
      }, 150);
    } catch (_) { /* sessionStorage 접근 불가 시 무시 */ }
  },

  _restoreState() {
    try {
      const raw = sessionStorage.getItem('modelzooCatalogState');
      if (!raw) return;
      const state = JSON.parse(raw);
      if (state.search) {
        const input = document.getElementById('searchInput');
        if (input) input.value = state.search;
      }
      if (Array.isArray(state.categories)) {
        const valid = state.categories.filter(c => isValidCategoryFilter(c, { requireUnknownModels: true }));
        const dropped = state.categories.length - valid.length;
        if (dropped > 0) {
          console.warn(`[ModelZoo] restoreState: dropped ${dropped} invalid category filter(s)`);
        }
        _selectedCategories = valid;
      }
      if (state.sort) _sortField = state.sort;
      if (state.dir) _sortDir = state.dir;
      if (state.viewMode) {
        _viewMode = state.viewMode;
        this._viewMode = state.viewMode;
      }
      if (state.scrollTop && this._container) {
        requestAnimationFrame(() => {
          if (this._container) this._container.scrollTop = state.scrollTop;
        });
      }
    } catch (_) { /* 파싱 실패 시 무시 */ }
  },
};


function updateCatalogHeading() {
  const titleEl = document.getElementById('catalogTitle');
  const subtitleEl = document.getElementById('catalogSubtitle');
  const countEl = document.getElementById('modelCount');
  const filteredModels = ModelZooVirtualCatalog._filteredModels || [];
  const variantCount = ModelZooVirtualCatalog.total ?? filteredModels.length;
  const uniqueModelCount = _computeUniqueModelCount(filteredModels);
  const hasSearch = Boolean((document.getElementById('searchInput')?.value || '').trim());

  if (titleEl) {
    if (hasSearch) {
      titleEl.textContent = T('Search results');
    } else if (_selectedCategories.length > 0) {
      titleEl.textContent = `${T('Selected categories')} (${_selectedCategories.length})`;
    } else {
      titleEl.textContent = T('All Models');
    }
  }
  if (subtitleEl) {
    subtitleEl.textContent = `${variantCount} ${T('model variants')} · ${uniqueModelCount} ${T('unique models')}`;
  }
  if (countEl) {
    countEl.textContent = `${variantCount} ${T('models found')}`;
  }
}

function updateActiveFilterSummary() {
  const el = document.getElementById('activeFilterSummary');
  const categoryText = _selectedCategories.length ? `${T('Active filters')}: ${_selectedCategories.length}` : T('All');
  if (el) el.textContent = `${categoryText}`;
  updateCatalogHeading();
}

function syncCatalogControls() {
  const sortSelect = document.getElementById('sortSelect');
  if (sortSelect) sortSelect.value = _sortField;
  document.getElementById('btnCardView')?.classList.toggle('active', _viewMode === 'card');
  document.getElementById('btnListView')?.classList.toggle('active', _viewMode === 'list');
}

// 공개 API — 기존 호환 래퍼

function initCatalog(data) {
  if (!data) return;
  ModelZooVirtualCatalog.init(data);
}

function renderCategoryChips() {
  const container = document.getElementById('categoryChips');
  if (!container) return;

  const counts = {};
  _allModels.forEach(m => { counts[m.category] = (counts[m.category] || 0) + 1; });

  const allActive = _selectedCategories.length === 0;
  let html = `<div class="mz-category-list">`;
  html += `<label class="mz-category-option${allActive ? ' active' : ''}">
    <input type="checkbox" data-cat="all" ${allActive ? 'checked' : ''}>
    <span class="mz-category-label">${_escapeAttr(T('All'))}</span>
    <span class="chip-count">${_escapeAttr(_allModels.length)}</span>
  </label>`;
  for (const [id, info] of Object.entries(_allCategories)) {
    const count = counts[id] || 0;
    if (count === 0) continue;
    const label = _localLabel(info, 'label') || id;
    const catActive = _selectedCategories.includes(id);
    html += `<label class="mz-category-option${catActive ? ' active' : ''}">
      <input type="checkbox" data-cat="${_escapeAttr(id)}" ${catActive ? 'checked' : ''}>
      <span class="mz-category-label">${_escapeAttr(info.icon || '')} ${_escapeAttr(label)}</span>
      <span class="chip-count">${_escapeAttr(count)}</span>
    </label>`;
  }
  const unknownCount = _allModels.filter(m => !hasCategory(m.category)).length;
  if (unknownCount > 0) {
    const unknownLabel = T('Unknown');
    const unkActive = _selectedCategories.includes('__unknown__');
    html += `<label class="mz-category-option${unkActive ? ' active' : ''}">
      <input type="checkbox" data-cat="__unknown__" ${unkActive ? 'checked' : ''}>
      <span class="mz-category-label">❓ ${_escapeAttr(unknownLabel)}</span>
      <span class="chip-count">${_escapeAttr(unknownCount)}</span>
    </label>`;
  }
  html += `</div>`;
  container.innerHTML = html;
  _bindCategoryChipEvents(container);
}

function _bindCategoryChipEvents(container) {
  container.querySelectorAll('input[data-cat]').forEach(input => {
    input.addEventListener('change', () => toggleCategory(input.dataset.cat || 'all'));
  });
}

function hasCategory(cat) {
  return Object.prototype.hasOwnProperty.call(_allCategories, cat);
}

function hasUnknownCategoryModels() {
  return _allModels.some(m => !hasCategory(m.category));
}

function isValidCategoryFilter(cat, options) {
  if (cat === '__unknown__') {
    return !(options && options.requireUnknownModels) || hasUnknownCategoryModels();
  }
  return hasCategory(cat);
}

function resetCatalogViewport() {
  ModelZooVirtualCatalog.scrollTop = 0;
  const container = ModelZooVirtualCatalog._container;
  if (container && container.scrollTop !== 0) container.scrollTop = 0;
  if (typeof window === 'undefined' || typeof window.scrollTo !== 'function') return;
  const anchor = document.getElementById('catalogView') || container;
  if (!anchor || typeof anchor.getBoundingClientRect !== 'function') return;
  const top = Math.max(0, anchor.getBoundingClientRect().top + window.scrollY - 72);
  if (window.scrollY <= top) return;
  try {
    window.scrollTo({ top, behavior: 'auto' });
  } catch (_) {
    window.scrollTo(0, top);
  }
}

function toggleCategory(cat) {
  if (cat === 'all') {
    _selectedCategories = [];
  } else if (!isValidCategoryFilter(cat)) {
    console.warn(`[ModelZoo] toggleCategory: invalid category "${cat}"`);
    return;
  } else {
    const idx = _selectedCategories.indexOf(cat);
    if (idx >= 0) _selectedCategories.splice(idx, 1);
    else _selectedCategories.push(cat);
  }
  document.querySelectorAll('#categoryChips input[data-cat]').forEach(input => {
    const c = input.dataset.cat;
    const checked = c === 'all' ? _selectedCategories.length === 0 : _selectedCategories.includes(c);
    input.checked = checked;
    input.closest('.mz-category-option')?.classList.toggle('active', checked);
  });
  resetCatalogViewport();
  filterAndRender();
}

function onSearchInput() {
  resetCatalogViewport();
  filterAndRender();
}

function onSortChange() {
  const sel = document.getElementById('sortSelect');
  if (sel) _sortField = sel.value;
  resetCatalogViewport();
  filterAndRender();
}

function onListHeaderClick(key) {
  if (_sortField === key) {
    _sortDir = _sortDir === 'asc' ? 'desc' : 'asc';
  } else {
    _sortField = key;
    _sortDir = 'asc';
  }
  resetCatalogViewport();
  filterAndRender();
}

function sortModels(models) {
  const dir = _sortDir === 'desc' ? -1 : 1;
  return [...models].sort((a, b) => {
    let va = a[_sortField] || a.id || '';
    let vb = b[_sortField] || b.id || '';
    if (_sortField === 'fps') {
      va = parseFloat(a.performance?.fps ?? a.specification?.fps) || 0;
      vb = parseFloat(b.performance?.fps ?? b.specification?.fps) || 0;
      return (vb - va) * dir;
    }
    return String(va).localeCompare(String(vb)) * dir;
  });
}

function filterAndRender() {
  renderCategoryChips();
  const sortSel = document.getElementById('sortSelect');
  if (sortSel) {
    sortSel.options[0].text = T('Name');
    sortSel.options[1].text = T('Category');
    sortSel.options[2].text = 'FPS';
  }
  const q = (document.getElementById('searchInput')?.value || '').trim();
  ModelZooVirtualCatalog.setQuery(q);
  ModelZooVirtualCatalog.resetAndRender();
  updateActiveFilterSummary();
}

function renderCardView(container, models) {
  // 가상화 위임 — 내부 상태 사용, 레거시 인자는 호환성을 위해 유지
  ModelZooVirtualCatalog._viewMode = 'card';
  ModelZooVirtualCatalog.renderViewport();
}

function renderListView(container, models) {
  // 가상화 위임 — 내부 상태 사용, 레거시 인자는 호환성을 위해 유지
  ModelZooVirtualCatalog._viewMode = 'list';
  ModelZooVirtualCatalog.renderViewport();
}

function setViewMode(mode) {
  _viewMode = mode;
  syncCatalogControls();
  resetCatalogViewport();
  ModelZooVirtualCatalog.setViewMode(mode);
}

function resetFilters() {
  _selectedCategories = [];
  const searchInput = document.getElementById('searchInput');
  if (searchInput) searchInput.value = '';
  _sortField = 'name';
  _sortDir = 'asc';
  const sortSelect = document.getElementById('sortSelect');
  if (sortSelect) sortSelect.value = 'name';
  resetCatalogViewport();
  filterAndRender();
}

// Expose UI-bound functions to global scope for inline event handlers
window.resetFilters = resetFilters;
window.setViewMode = setViewMode;
window.onSearchInput = onSearchInput;
window.onSortChange = onSortChange;
if (typeof registerModelZooLangRefresher === 'function') {
  registerModelZooLangRefresher(function() {
    if (typeof filterAndRender === 'function') filterAndRender();
    if (location.hash.startsWith('#model=') && typeof renderDetailPage === 'function') {
      var modelId = location.hash.slice(7);
      try { modelId = decodeURIComponent(modelId); } catch (_) {}
      renderDetailPage(modelId);
    }
  });
}
