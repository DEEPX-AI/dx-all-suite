'use strict';

let _catalogData = null;
let _dxAppAlive = false;
let _catalogLoadFailed = false;

function modelzooApiUrl(path) {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  const prefix = location.pathname.startsWith('/zoo/') || location.pathname === '/zoo' ? '/zoo' : '';
  return `${prefix}${cleanPath}`;
}

function getModelIdFromHash(hash) {
  if (!hash || !hash.startsWith('#model=')) return '';
  const raw = hash.slice(7);
  try {
    return decodeURIComponent(raw);
  } catch (_) {
    return raw;
  }
}

window.getModelIdFromHash = getModelIdFromHash;

async function fetchCatalog() {
  try {
    const resp = await fetch(modelzooApiUrl('/api/catalog'));
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    _catalogData = await resp.json();
    _catalogLoadFailed = false;
    return _catalogData;
  } catch (e) {
    console.error('Failed to fetch catalog:', e);
    // Distinguish a load failure from a genuinely empty catalog (F-21): keep an
    // empty shape for callers but flag the failure so the UI shows an error+retry
    // instead of a misleading "No models found" placeholder.
    _catalogLoadFailed = true;
    _catalogData = { models: [], categories: {}, count: 0 };
    return _catalogData;
  }
}

function _showCatalogLoadError() {
  const container = document.getElementById('catalogContainer');
  if (!container) return;
  const retry = (typeof T === 'function') ? T('Retry') : 'Retry';
  const msg = (typeof T === 'function') ? T('Failed to load catalog') : 'Failed to load catalog';
  container.innerHTML = `<div class="mz-catalog-error">
      <p>${msg}</p>
      <button class="mz-btn mz-btn-outline" onclick="reloadCatalog()">↻ ${retry}</button>
    </div>`;
}

// Fetch + populate the catalog. Does NOT call route() — the initial page load must
// run checkDxAppHealth() before route() (see _boot) so the detail view never flashes
// a stale "DX App inactive" state.
async function loadAndInitCatalog() {
  await fetchCatalog();
  if (_catalogLoadFailed) {
    _showCatalogLoadError();
    return false;
  }
  const countEl = document.getElementById('modelCount');
  if (countEl && _catalogData) {
    const variantCount = Number.isFinite(_catalogData.variant_count) ? _catalogData.variant_count : _catalogData.count;
    countEl.textContent = `${variantCount} ${T('models found')}`;
  }
  if (typeof initCatalog === 'function') {
    initCatalog(_catalogData);
  }
  return true;
}

// Retry entry point (error-state button): reload, refresh health, then render route.
window.reloadCatalog = async function reloadCatalog() {
  const ok = await loadAndInitCatalog();
  if (!ok) return;
  await checkDxAppHealth();
  route();
};

async function checkDxAppHealth() {
  const previousAlive = _dxAppAlive;
  try {
    const resp = await fetch(modelzooApiUrl('/api/health'));
    const data = await resp.json();
    _dxAppAlive = data.dx_app_alive === true;
  } catch {
    _dxAppAlive = false;
  }
  const dot = document.getElementById('dxAppStatus');
  if (dot) dot.classList.toggle('alive', _dxAppAlive);

  const changed = previousAlive !== _dxAppAlive;
  if (changed && location.hash.startsWith('#model=')) {
    if (typeof refreshDetailActionBarsForHealth === 'function') {
      refreshDetailActionBarsForHealth();
    }
  }
}

function route() {
  const hash = location.hash;
  const catalogView = document.getElementById('catalogView');
  const detailView = document.getElementById('detailView');

  if (!catalogView || !detailView) return;

  const shell = document.querySelector('.mz-explorer-shell');

  if (hash.startsWith('#model=')) {
    const modelId = getModelIdFromHash(location.hash);
    catalogView.style.display = 'none';
    detailView.style.display = '';
    if (shell) shell.classList.add('is-detail');
    if (typeof renderDetailPage === 'function') {
      renderDetailPage(modelId);
    }
  } else {
    catalogView.style.display = '';
    detailView.style.display = 'none';
    if (shell) shell.classList.remove('is-detail');
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  DXI18n.setLang(DXI18n.lang);

  await loadAndInitCatalog();
  await checkDxAppHealth();
  route();
  setInterval(() => { checkDxAppHealth(); }, 10000);

  window.addEventListener('hashchange', route);
});

// Listen for theme/language changes from parent launcher (postMessage)
// toolbar.js + i18n.js가 theme/lang 동기화 처리
window.addEventListener('message', function(e) {
  if (!e.data) return;
  if (e.data.type === 'dx-lang-change' && e.data.lang) {
    if (typeof filterAndRender === 'function') filterAndRender();
    if (location.hash.startsWith('#model=') && typeof renderDetailPage === 'function') {
      renderDetailPage(getModelIdFromHash(location.hash));
    }
  }
});
