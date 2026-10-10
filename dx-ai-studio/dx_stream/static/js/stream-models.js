/**
 * DX Stream — 모델 카탈로그
 * 카드 렌더링, 카테고리 필터, 검색, 상세 모달
 */
var _modelCatI18n = {
    'object detection': { ko: '객체 탐지',  ja: '物体検出',   'zh-CN': '目标检测',  'zh-TW': '物件偵測',es:'detección de objetos'},
    'classification': { ko: '분류',       ja: '分類',       'zh-CN': '分类',      'zh-TW': '分類',es:'clasificación'},
    'segmentation': { ko: '분할',       ja: 'セグメンテーション', 'zh-CN': '分割', 'zh-TW': '分割',es:'segmentación'},
    'pose estimation': { ko: '자세 추정',  ja: '姿勢推定',   'zh-CN': '姿态估计',  'zh-TW': '姿勢估計',es:'estimación de pose'},
    'face detection': { ko: '얼굴 탐지',  ja: '顔検出',     'zh-CN': '人脸检测',  'zh-TW': '人臉偵測',es:'detección facial'},
    'tracking': { ko: '추적',       ja: '追跡',       'zh-CN': '追踪',      'zh-TW': '追蹤',es:'seguimiento'},
    'super resolution': { ko: '초해상도',   ja: '超解像',     'zh-CN': '超分辨率',  'zh-TW': '超解析度',es:'súper resolución'},
    'depth estimation': { ko: '깊이 추정',  ja: '深度推定',   'zh-CN': '深度估计',  'zh-TW': '深度估計',es:'estimación de profundidad'}
};
function _modelCatLabel(rawCat) {
    var t = _modelCatI18n[rawCat];
    if (!t) return rawCat;
    return t[DXStream.S.lang] || t.en || rawCat;
}
DXStream.modelsInit = async function () {
    var payload = await DXStream.api('/api/models');
    if (payload.error) {
        DXStream.toast(T('Error: ') + payload.error, 'error');
        return;
    }
    var models = Array.isArray(payload) ? payload : (payload.models || []);
    DXStream._modelCatalogSource = Array.isArray(payload) ? 'fallback' : (payload.catalog_source || 'fallback');
    DXStream._allModels = models;
    DXStream._filteredModels = DXStream._allModels;
    _renderModelCards(DXStream._allModels);
    _renderModelFilters(DXStream._allModels);

    // 검색
    var search = DXStream.$('models-search');
    if (search) {
        search.oninput = function () {
            var q = this.value.toLowerCase();
            var filtered = (DXStream._filteredModels || DXStream._allModels).filter(function (m) {
                return m.name.toLowerCase().indexOf(q) !== -1 ||
                       (m.category || '').toLowerCase().indexOf(q) !== -1;
            });
            _renderModelCards(filtered);
        };
    }
};

/* 분류 버튼은 받은 목록에 있는 분류로 만든다. 목록은 manifest 에서 오고 (깊이 추정은 있고 OBB 는 없다) 매니페스트가
   없으면 내장 목록이라, 고정 버튼은 있는 model 을 못 고르거나 빈 분류를 보여줬다 (release audit S-16). */
function _renderModelFilters(models) {
    var bar = DXStream.$('models-filter-bar');
    if (!bar) return;
    var cats = [];
    (models || []).forEach(function (m) {
        if (m.category && cats.indexOf(m.category) === -1) cats.push(m.category);
    });
    var order = ['object_detection', 'classification', 'segmentation', 'pose_estimation', 'face_detection',
        'depth_estimation', 'obb_detection'];
    cats.sort(function (x, y) {
        var a = order.indexOf(x), b = order.indexOf(y);
        return (a === -1 ? 99 : a) - (b === -1 ? 99 : b);
    });
    var cur = DXStream._modelFilterCat || 'all';
    if (cats.indexOf(cur) === -1) cur = 'all';
    DXStream._modelFilterCat = cur;
    bar.innerHTML = ['all'].concat(cats).map(function (c) {
        return '<button type="button" class="btn btn-ghost btn-sm' + (c === cur ? ' active' : '') + '" data-cat="'
            + DXStream.escHtml(c) + '">' + DXStream.escHtml(c === 'all' ? T('All') : _modelCat(c)) + '</button>';
    }).join('');
    bar.onclick = function (e) {
        var b = e.target.closest('[data-cat]');
        if (b) DXStream.filterModels(b.getAttribute('data-cat'), b);
    };
    if (cur !== 'all') DXStream.filterModels(cur);
}

DXStream.filterModels = function (cat, btn) {
    DXStream._modelFilterCat = cat;
    var bar = DXStream.$('models-filter-bar');
    if (bar) {
        bar.querySelectorAll('.btn').forEach(function (b) { b.classList.remove('active'); });
        // onclick 은 버튼을 넘기지 않는다 — 분류로 찾아야 첫 클릭 뒤에도 고른 버튼이 강조된다 (release audit S-16).
        btn = btn || bar.querySelector('[data-cat="' + cat + '"]');
        if (btn) btn.classList.add('active');
    }
    if (!DXStream._allModels) return;
    if (cat === 'all') {
        DXStream._filteredModels = DXStream._allModels;
    } else {
        DXStream._filteredModels = DXStream._allModels.filter(function (m) {
            return m.category === cat;
        });
    }
    // 검색어는 지우지 않고 새 분류에 다시 적용한다 (S-16).
    var search = DXStream.$('models-search');
    if (search && search.value && search.oninput) search.oninput.call(search);
    else _renderModelCards(DXStream._filteredModels);
};

/* 설명은 고른 언어로 (서버는 ko · en 만 준다 — 다른 언어는 en), 분류는 번역한 이름으로. 예전에는 ko · en <span> 만 있어
   ja · zh · es 에서는 설명이 비었고, 분류는 "object detection" 같은 slug 였다 (release audit S-10). */
function _modelDesc(m) {
    var lang = (window.DXI18n && DXI18n.lang) || 'en';
    if (m['description_' + lang]) return m['description_' + lang];
    if (lang === 'ko' && m.description_ko) return m.description_ko;
    return m.description_en ? T(m.description_en) : '';
}
function _modelCat(c) {
    var label = String(c || '').replace(/_/g, ' ').replace(/\b\w/g, function (x) { return x.toUpperCase(); })
        .replace(/^Obb /, 'OBB ');
    return label ? T(label) : '';
}

function _renderModelCards(models) {
    var grid = DXStream.$('models-grid');
    if (!grid) return;
    if (!models || models.length === 0) {
        grid.innerHTML = '<p class="txt-dim" style="grid-column:1/-1;text-align:center">'
            + T('No models found') + '</p>';
        return;
    }
    grid.innerHTML = models.map(function (m) {
        return '<div class="card" style="cursor:pointer" onclick="DXStream.showModelDetail(\'' + m.name.replace(/'/g, "\\'") + '\')">' +
            '<h3>' + DXStream.escHtml(m.name) + '</h3>' +
            '<p class="txt-dim txt-sm">' + DXStream.escHtml(_modelDesc(m)) + '</p>' +
            '<div class="demo-card-meta">' +
            '<span>' + ((typeof DXIcon === 'function') ? DXIcon('file') : '') + ' ' + DXStream.escHtml(m.file || '--') + '</span>' +
            '<span class="demo-card-cat">' + DXStream.escHtml(_modelCat(m.category)) + '</span>' +
            '</div>' +
            (m.installed
                ? '<span class="card-badge" style="background:var(--surface-raised);color:var(--status-ok)">' + ((typeof DXIcon === 'function') ? DXIcon('check') : '') + ' ' + T('Installed') + '</span>'
                : '<button class="btn btn-sm btn-accent download-model-btn" data-model="' + DXStream.escHtml(m.file) + '" onclick="event.stopPropagation(); DXStream.downloadModelFile(this.dataset.model, this)">' + ((typeof DXIcon === 'function') ? DXIcon('download') : '') + ' ' + T('Download') + '</button>') +
            '</div>';
    }).join('');
}

document.addEventListener('click', function(e) {
    var tab = e.target.closest('.modal-tab');
    if (!tab) return;
    var tabName = tab.dataset.tab;
    document.querySelectorAll('.modal-tab').forEach(function(t) { t.classList.remove('active'); });
    tab.classList.add('active');
    document.getElementById('model-tab-detail').style.display = tabName === 'detail' ? '' : 'none';
    document.getElementById('model-tab-metadata').style.display = tabName === 'metadata' ? '' : 'none';

    if (tabName === 'metadata') {
        var modelFile = document.getElementById('model-detail-tabs').dataset.modelFile;
        if (modelFile) DXStream.loadModelMetadata(modelFile);
    }
});

DXStream.loadModelMetadata = function(modelFile) {
    var container = document.getElementById('model-metadata-content');
    container.innerHTML = '<div class="loading-placeholder"><span class="spin"></span></div>';
    DXStream.api('/api/models/' + encodeURIComponent(modelFile) + '/metadata')
        .then(function(data) {
            if (!data || data.error) {
                /* 서버의 오류 코드 ('not_found') 를 그대로 보이지 않는다 — 모델 파일이 없을 때가 대부분이다 */
                var msg = (data && (data.error_code === 'not_found' || data.status === 404))
                    ? T('Download this model to see its metadata.')
                    : _srvMsg((data && data.error) || '');
                container.innerHTML = '<p class="metadata-error txt-dim">' + DXStream.escHtml(msg) + '</p>';
                return;
            }
            var html = '<pre class="metadata-raw">' + DXStream.escHtml(data.raw_output || T('No output')) + '</pre>';
            if (data.graph_info) {
                html += '<h4>' + T('Graph Info') + '</h4>';
                html += '<pre>' + DXStream.escHtml(JSON.stringify(data.graph_info, null, 2)) + '</pre>';
            }
            container.innerHTML = html;
        })
        .catch(function() {
            container.innerHTML = '<p class="txt-dim">' + T('Failed to load metadata') + '</p>';
        });
};

function _srvMsg(m) { return (typeof window.translateServerError === 'function') ? window.translateServerError(m) : m; }

// One download path for the card button and the detail dialog. It used to (card) poll the latest
// log of ANY step, never report a failed download, and keep a disabled spinner forever when the
// server said another process was running; the dialog started a download and showed nothing more.
function _downloadModelFile(file, btn) {
    function restore() {
        if (!btn) return;
        btn.disabled = false;
        if (typeof DXIcon === 'function' && DXIcon.label) DXIcon.label(btn, 'download', T('Download'));
    }
    if (btn) {
        btn.disabled = true;
        if (typeof DXIcon === 'function' && DXIcon.label) DXIcon.label(btn, 'spinner', T('Downloading...'), { cls: 'dx-ico--spin' });
    }
    return DXStream.postJ('/api/setup/download-model', { model: file }).then(function (resp) {
        if (!resp || resp.error) {
            restore();
            DXStream.toast(T('Download failed: ') + _srvMsg((resp && resp.error) || ''), 'error');
            return;
        }
        DXStream.toast(file + ' ' + T('download started'), 'info');
        var step = 'model-' + file;
        var pollId = setInterval(function () {
            DXStream.api('/api/setup/log?step=' + encodeURIComponent(step)).then(function (l) {
                if (!l || l.error || !l.done) return;
                clearInterval(pollId);
                if (l.exit_code === 0) DXStream.toast(file + ' ' + T('completed'), 'success');
                else { restore(); DXStream.toast(T('Download failed: ') + 'exit ' + l.exit_code, 'error'); }
                if (DXStream.S.currentPage === 'models' && typeof DXStream.modelsInit === 'function') DXStream.modelsInit();
            });
        }, 2000);
    });
}

// The card button stops propagation (the card itself opens the detail dialog), so a document-level
// click listener never saw it — the card Download button did nothing. It calls this directly now.
DXStream.downloadModelFile = _downloadModelFile;

DXStream.showModelDetail = function (name) {
    var model = null;
    for (var i = 0; i < DXStream._allModels.length; i++) {
        if (DXStream._allModels[i].name === name) { model = DXStream._allModels[i]; break; }
    }
    if (!model) return;

    var modal = DXStream.$('model-detail-modal');
    if (!modal) return;
    modal.showModal();
    var titleEl = DXStream.$('model-detail-title');
    if (titleEl) titleEl.textContent = model.name;

    var catEl = DXStream.$('model-detail-category');
    if (catEl) {
        var rawCat = (model.category || '').replace(/_/g, ' ');
        catEl.textContent = _modelCatLabel(rawCat);
    }

    var inputEl = DXStream.$('model-detail-input');
    if (inputEl) inputEl.textContent = model.input_size || '--';

    var sizeEl = DXStream.$('model-detail-size');
    if (sizeEl) sizeEl.textContent = model.file_size || '--';

    var statusEl = DXStream.$('model-detail-status');
    if (statusEl) {
        DXIcon.label(statusEl, model.installed ? 'check' : 'alert', model.installed ? T('OK') : T('Not installed'));
    }

    var infoEl = DXStream.$('model-detail-info');
    if (infoEl) infoEl.textContent = model.file || '';

    DXStream._selectedModel = model;

    var tabs = document.getElementById('model-detail-tabs');
    if (tabs) tabs.dataset.modelFile = model.file || '';

    // 탭 초기화: detail 탭으로 리셋
    document.querySelectorAll('.modal-tab').forEach(function(t) { t.classList.remove('active'); });
    var detailTab = document.querySelector('.modal-tab[data-tab="detail"]');
    if (detailTab) detailTab.classList.add('active');
    var detailPane = document.getElementById('model-tab-detail');
    var metaPane = document.getElementById('model-tab-metadata');
    if (detailPane) detailPane.style.display = '';
    if (metaPane) metaPane.style.display = 'none';
};

DXStream.closeModelDetail = function () {
    var modal = DXStream.$('model-detail-modal');
    if (modal) modal.close();
};

DXStream.downloadModel = function () {
    if (!DXStream._selectedModel) return;
    _downloadModelFile(DXStream._selectedModel.file, DXStream.$('model-detail-download-btn'));
};
if (typeof registerStreamLangRefresher === 'function') {
  registerStreamLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined' && DXStream.S && DXStream.S.currentPage && typeof DXStream.nav === 'function') {
      DXStream.nav(DXStream.S.currentPage);
    }
  });
}
