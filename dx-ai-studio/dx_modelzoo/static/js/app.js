'use strict';

let _catalogData = null;
let _dxAppAlive = false;
let _catalogLoadFailed = false;

/* ── 지표의 방향 ──────────────────────────────────────────────
   지표마다 좋은 쪽이 다르다 — Top1 은 클수록, RMSE 는 작을수록 좋다. 정렬과
   델타 색칠이 모두 이 방향에 의존하므로, 카탈로그(catalog.js)와 상세(detail.js)
   가 같은 표를 본다. 두 파일이 각자 선언하면 같은 전역 스코프에서 재선언이 되어
   나중에 로드되는 쪽이 통째로 파싱에 실패한다 — 그래서 여기 한 벌만 둔다.
   (서버 쪽 같은 표: dx_modelzoo/core/metrics.py) */
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

/* ── 카탈로그와 상세가 함께 쓰는 헬퍼 ────────────────────────
   catalog.js 와 detail.js 는 같은 전역 스코프를 공유한다. 같은 이름을 양쪽에서
   선언하면 나중에 로드되는 쪽이 조용히 이긴다 — 실제로 _localLabel 의 다국어
   폴백이 그렇게 사라져 있었다. 그래서 공유 헬퍼는 여기 한 벌만 둔다. */
function _escapeAttr(s) {
  if (s == null) return '';
  return String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

/* 화면의 표시 아이콘 (sprite, 아이콘 체계 단계 5) — HTML 문자열 안에서 쓴다. */
function _mzIco(name) {
  return (typeof window.DXIcon === 'function') ? window.DXIcon(name) : '';
}

/* task 아이콘 — sprite 의 task-<key> (dx_modelzoo/core/config.py CATEGORIES 의 icon, 아이콘 체계 단계 3).
   모르는 이름이면 모델 일반 표시 (models) 로. 옆에 task 이름이 적혀 있으므로 장식이다 (label 없음). */
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

/* 카드 · 상세의 요약. 생성기 (metadata/merge.py) 가 task 마다 영어 한 문장으로 채우므로, 고른 언어가 없으면 그
   문장을 사전으로 번역하고, "AI model for <task> tasks." 꼴은 번역한 task 이름으로 말한다 (release audit Z-6:
   요약이 모든 언어에서 영어였고, 일부는 "image_retrieval" 같은 slug 가 보였다). */
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
    // 수량사 (개 · 件 · 个 · 個) 는 숫자에 붙인다 — "499개 모델" (release audit)
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
