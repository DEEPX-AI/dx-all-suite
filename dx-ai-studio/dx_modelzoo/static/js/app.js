'use strict';

let _catalogData = null;
let _dxAppAlive = false;
let _catalogLoadFailed = false;

/* ── Metric direction ──────────────────────────────────────────
   Each metric has its own good direction — Top1 is better higher, RMSE lower. Sorting
   and delta coloring both depend on it, so the catalog (catalog.js) and the detail page
   (detail.js) read the same table. Declaring it in both files would be a redeclaration in
   the shared global scope and the later file would fail to parse — so it lives only here.
   (Server-side counterpart: dx_modelzoo/core/metrics.py) */
const METRIC_HIGHER_IS_BETTER = new Set([
  'Top1', 'Top5', 'Accuracy', 'Average Accuracy',
  'mAP', 'mAP50', 'mAP_BEV@0.5', 'det_mAP50',
  'AP', 'AP(Easy)', 'AP(Medium)', 'AP(Hard)', 'AP@0.5', 'AR10',
  'mIoU', 'PSNR', 'Recall@1', 'HEA',
]);
const METRIC_LOWER_IS_BETTER = new Set(['RMSE', 'NME', 'MNAE', 'ADD']);

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

/* ── Helpers shared by the catalog and the detail page ─────────────
   catalog.js and detail.js share one global scope. A name declared in both is silently
   won by whichever loads later (e.g. a localized fallback in _localLabel could be lost),
   so shared helpers live only here. */
function _escapeAttr(s) {
  if (s == null) return '';
  return String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/* Status icons from the sprite — used inside HTML strings. */
function _mzIco(name) {
  return (typeof window.DXIcon === 'function') ? window.DXIcon(name) : '';
}

/* Task icon — task-<key> in the sprite (the icon of CATEGORIES in dx_modelzoo/core/config.py).
   Unknown names fall back to the generic model icon (models). Decorative: the task name is written next to it (no label). */
function _taskIcon(catInfo, cls) {
  if (typeof window.DXIcon !== 'function') return '';
  const name = catInfo && /^task-[a-z0-9_]+$/.test(catInfo.icon || '') ? catInfo.icon : 'models';
  return window.DXIcon(name, { cls: cls || 'mz-task-ico' });
}

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

/* Card and detail summary. The generator (metadata/merge.py) fills one English sentence per task, so when the
   chosen language is missing, translate that sentence through the dictionary, and say "AI model for <task> tasks."
   with the translated task name rather than a slug such as "image_retrieval". */
function _summaryText(m) {
  const s = (m && ((m.display && m.display.summary) || (m.content && m.content.use_case))) || null;
  if (!s) return '';
  const lang = DXI18n.lang;
  if (lang === 'en' || s[lang] || s[lang.split('-')[0]]) return _localText(s);
  const en = s.en || '';
  const tr = T(en);
  if (tr !== en) return tr;
  const g = en.match(/^AI model for (\w+) tasks\.$/);
  if (g) {
    const cats = (typeof _allCategories === 'object' && _allCategories) || {};
    const label = (m.category && cats[m.category] && _localLabel(cats[m.category], 'label')) || g[1].replace(/_/g, ' ');
    return T('%s model.').replace('%s', label);
  }
  return en;
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
  const icon = available ? _mzIco('check') : _mzIco('spinner');
  const title = available ? label : T('Artifact unavailable');
  return `<span class="mz-download-badge ${status}" title="${_escapeAttr(title)}">${icon} ${_escapeAttr(label)}</span>`;
}

async function fetchCatalog() {
  try {
    const resp = await fetch(modelzooApiUrl('/api/catalog'));
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    _catalogData = await resp.json();
    _catalogLoadFailed = false;
    return _catalogData;
  } catch (e) {
    console.error('Failed to fetch catalog:', e);
    // Distinguish a load failure from a genuinely empty catalog: keep an
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
    // CJK counter words (Korean, Japanese, Chinese) attach to the number with no space
    const found = T('models found');
    countEl.textContent = /^[개件個个]/.test(found) ? `${variantCount}${found}` : `${variantCount} ${found}`;
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
  const indicator = document.getElementById('dxAppIndicator');
  if (indicator) {
    const state = T(_dxAppAlive ? 'DX App connected' : 'DX App offline');
    indicator.title = state;
    indicator.setAttribute('aria-label', state);
  }

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
// toolbar.js + i18n.js handle theme/lang sync
window.addEventListener('message', function(e) {
  if (!e.data) return;
  if (e.data.type === 'dx-lang-change' && e.data.lang) {
    if (typeof filterAndRender === 'function') filterAndRender();
    if (location.hash.startsWith('#model=') && typeof renderDetailPage === 'function') {
      renderDetailPage(getModelIdFromHash(location.hash));
    }
  }
});
