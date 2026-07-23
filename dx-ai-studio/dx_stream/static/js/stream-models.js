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

DXStream.filterModels = function (cat, btn) {
    var bar = DXStream.$('models-filter-bar');
    if (bar) {
        bar.querySelectorAll('.btn').forEach(function (b) { b.classList.remove('active'); });
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
    _renderModelCards(DXStream._filteredModels);

    // 검색 입력 리셋
    var search = DXStream.$('models-search');
    if (search) search.value = '';
};

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
            '<p class="txt-dim txt-sm">' +
            '<span class="ko">' + DXStream.escHtml(m.description_ko || '') + '</span>' +
            '<span class="en">' + DXStream.escHtml(m.description_en || '') + '</span>' +
            '</p>' +
            '<div class="demo-card-meta">' +
            '<span>📁 ' + DXStream.escHtml(m.file || '--') + '</span>' +
            '<span class="demo-card-cat">' + DXStream.escHtml((m.category || '').replace(/_/g, ' ')) + '</span>' +
            '</div>' +
            (m.installed
                ? '<span class="card-badge" style="background:var(--success-dim);color:var(--success)">✅ ' + T('Installed') + '</span>'
                : '<button class="btn btn-sm btn-accent download-model-btn" data-model="' + DXStream.escHtml(m.file) + '" onclick="event.stopPropagation()">⬇️ ' + T('Download') + '</button>') +
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
    fetch('/api/models/' + modelFile + '/metadata')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.error) {
                container.innerHTML = '<pre class="metadata-error">' + data.error + '</pre>';
                return;
            }
            var html = '<pre class="metadata-raw">' + (data.raw_output || 'No output') + '</pre>';
            if (data.graph_info) {
                html += '<h4>' + T('Graph Info') + '</h4>';
                html += '<pre>' + JSON.stringify(data.graph_info, null, 2) + '</pre>';
            }
            container.innerHTML = html;
        })
        .catch(function() {
            container.innerHTML = '<p class="txt-dim">' + T('Failed to load metadata') + '</p>';
        });
};

document.addEventListener('click', function(e) {
    var btn = e.target.closest('.download-model-btn');
    if (!btn) return;
    var model = btn.dataset.model;
    btn.disabled = true;
    btn.textContent = '⏳ ' + T('Downloading...');
    fetch('/api/setup/download-model', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({model: model})
    }).then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.started) {
            var pollId = setInterval(function() {
                fetch('/api/setup/log').then(function(r2) { return r2.json(); })
                .then(function(logData) {
                    if (logData.done) {
                        clearInterval(pollId);
                        DXStream.modelsInit();
                    }
                });
            }, 2000);
        }
    }).catch(function() {
        btn.disabled = false;
        btn.textContent = '⬇️ ' + T('Download');
    });
});

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
        statusEl.textContent = model.installed ? '✅ ' + T('OK') : '⚠️ ' + T('Not installed');
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
    var model = DXStream._selectedModel;
    DXStream.toast(T('Downloading models…'), 'info');
    DXStream.postJ('/api/setup/download-model', { model: model.file }).then(function (resp) {
        if (resp.error) {
            DXStream.toast(T('Download failed: ') + resp.error, 'error');
            return;
        }
        DXStream.toast(model.name + ' ' + T('download started'), 'success');
    });
};
if (typeof registerStreamLangRefresher === 'function') {
  registerStreamLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined' && DXStream.S && DXStream.S.currentPage && typeof DXStream.nav === 'function') {
      DXStream.nav(DXStream.S.currentPage);
    }
  });
}
