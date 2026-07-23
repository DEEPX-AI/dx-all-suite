/**
 * DX Stream — GStreamer 요소 레퍼런스
 * 카드 기반 렌더링 + 검색/필터
 */
DXStream.elementsInit = async function () {
    const grid = DXStream.$('elements-grid');
    if (!grid) return;
    grid.innerHTML = '<div style="text-align:center;padding:40px;grid-column:1/-1" class="txt-dim"><span class="spin"></span></div>';

    const elements = await DXStream.api('/api/elements');
    if (!elements || elements.error) {
        grid.innerHTML = '<div style="text-align:center;padding:40px;grid-column:1/-1" class="txt-dim">' +
            T('Failed to load elements') + '</div>';
        return;
    }
    DXStream._allElements = Array.isArray(elements) ? elements : [];
    _renderElementCards(DXStream._allElements);

    const search = DXStream.$('elements-search');
    if (search) {
        search.oninput = function () {
            var q = this.value.toLowerCase();
            var filtered = DXStream._allElements.filter(function (e) {
                return e.name.toLowerCase().indexOf(q) !== -1 || (e.category || '').toLowerCase().indexOf(q) !== -1;
            });
            _renderElementCards(filtered);
        };
    }
};

DXStream.filterElements = function (cat, btn) {
    document.querySelectorAll('#elements-filter-bar .btn').forEach(function (b) { b.classList.remove('active'); });
    if (btn) btn.classList.add('active');
    if (cat === 'all') {
        _renderElementCards(DXStream._allElements);
    } else {
        _renderElementCards(DXStream._allElements.filter(function (e) { return e.category === cat; }));
    }
};

var _elemCatCssClasses = {
    preprocess: 'b-ok', inference: 'b-cat', postprocess: 'b-warn',
    visualization: 'b-blue', tracking: 'b-blue', messaging: 'b-red',
    source: 'b-ok', output: 'b-ok', utility: 'b-warn'
};
var _elemCatI18n = {
    preprocess:    { ko: '전처리',   ja: '前処理',         'zh-CN': '预处理',   'zh-TW': '前處理' },
    inference:     { ko: '추론',     ja: '推論',           'zh-CN': '推理',     'zh-TW': '推論' },
    postprocess:   { ko: '후처리',   ja: '後処理',         'zh-CN': '后处理',   'zh-TW': '後處理' },
    visualization: { ko: '시각화',   ja: '可視化',         'zh-CN': '可视化',   'zh-TW': '視覺化' },
    tracking:      { ko: '추적',     ja: '追跡',           'zh-CN': '追踪',     'zh-TW': '追蹤' },
    messaging:     { ko: '메시징',   ja: 'メッセージング', 'zh-CN': '消息传递', 'zh-TW': '訊息傳遞' },
    source:        { ko: '소스',     ja: 'ソース',         'zh-CN': '源',       'zh-TW': '來源' },
    output:        { ko: '출력',     ja: '出力',           'zh-CN': '输出',     'zh-TW': '輸出' },
    utility:       { ko: '유틸리티', ja: 'ユーティリティ', 'zh-CN': '实用工具', 'zh-TW': '實用工具' }
};
function _elemCatLabel(cat) {
    var t = _elemCatI18n[cat];
    if (!t) return cat || '';
    return t[DXStream.S.lang] || t.en || cat || '';
}

function _escElementHtml(value) {
    if (DXStream.escHtml) return DXStream.escHtml(value || '');
    return String(value || '').replace(/[&<>"]/g, function (m) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m];
    });
}

function _renderBilingualText(ko, en) {
    return '<span class="ko">' + _escElementHtml(ko || en || '') + '</span>' +
        '<span class="en">' + _escElementHtml(en || ko || '') + '</span>';
}

function _renderElementExtra(el) {
    var html = '';
    if (el.long_description_ko || el.long_description_en) {
        html += '<div class="element-detail-section element-detail-callout">' +
            '<p>' + _renderBilingualText(el.long_description_ko, el.long_description_en) + '</p>' +
            '</div>';
    }
    if (el.key_features && el.key_features.length) {
        html += '<div class="element-detail-section"><h4>' +
            '<span class="ko">핵심 기능</span><span class="en">Key Features</span>' +
            '</h4><ul class="element-feature-list">';
        for (var i = 0; i < el.key_features.length; i++) {
            var feature = el.key_features[i] || {};
            html += '<li>' + _renderBilingualText(feature.ko, feature.en) + '</li>';
        }
        html += '</ul></div>';
    }
    if (el.pipeline_hint_ko || el.pipeline_hint_en) {
        html += '<div class="element-detail-section"><h4>' +
            '<span class="ko">파이프라인 힌트</span><span class="en">Pipeline Hint</span>' +
            '</h4><p>' + _renderBilingualText(el.pipeline_hint_ko, el.pipeline_hint_en) + '</p></div>';
    }
    if (el.example_config) {
        html += '<div class="element-detail-section"><h4>' +
            '<span class="ko">예시 설정</span><span class="en">Example Config</span>' +
            '</h4><pre class="element-code-snippet">' + _escElementHtml(el.example_config) + '</pre></div>';
    }
    if (el.related_elements && el.related_elements.length) {
        html += '<div class="element-detail-section element-related"><h4>' +
            '<span class="ko">관련 요소</span><span class="en">Related Elements</span>' +
            '</h4>';
        for (var j = 0; j < el.related_elements.length; j++) {
            html += '<span class="badge b-cat">' + _escElementHtml(el.related_elements[j]) + '</span>';
        }
        html += '</div>';
    }
    if (el.doc_path) {
        html += '<div class="element-detail-section"><h4>' +
            '<span class="ko">SDK 문서</span><span class="en">SDK Docs</span>' +
            '</h4><code class="element-doc-path">' + _escElementHtml(el.doc_path) + '</code></div>';
    }
    return html;
}

function _renderElementCards(elements) {
    var grid = DXStream.$('elements-grid');
    if (!grid) return;
    if (!elements || elements.length === 0) {
        grid.innerHTML = '<div class="txt-dim" style="text-align:center;padding:40px;grid-column:1/-1">' +
            T('No matching elements') + '</div>';
        return;
    }
    var html = '';
    for (var i = 0; i < elements.length; i++) {
        var e = elements[i];
        var catClass = _elemCatCssClasses[e.category] || 'b-cat';
        var propCount = e.properties ? e.properties.length : 0;
        html += '<div class="element-card" onclick="DXStream.showElementDetail(\'' + e.name.replace(/'/g, "\\'") + '\')">' +
            '<div><span class="element-card-name">' + e.name + '</span>' +
            '<span class="badge ' + catClass + ' element-card-cat">' + _elemCatLabel(e.category) + '</span></div>' +
            '<div class="element-card-desc"><span class="ko">' + (e.description_ko || '') + '</span><span class="en">' + (e.description_en || '') + '</span></div>' +
            '<div class="element-card-props">' + propCount + ' ' + T('properties') + '</div>' +
            '</div>';
    }
    grid.innerHTML = html;
}

DXStream.showElementDetail = function (name) {
    var el = null;
    for (var i = 0; i < DXStream._allElements.length; i++) {
        if (DXStream._allElements[i].name === name) { el = DXStream._allElements[i]; break; }
    }
    if (!el) return;
    var detail = DXStream.$('element-detail');
    if (detail) detail.style.display = '';
    DXStream.$('element-detail-name').textContent = el.name;
    DXStream.$('element-detail-desc').innerHTML = _renderBilingualText(el.description_ko, el.description_en);
    var extra = DXStream.$('element-detail-extra');
    if (extra) extra.innerHTML = _renderElementExtra(el);
    var tbody = DXStream.$('element-detail-props-tbody');
    if (tbody && el.properties) {
        var rows = '';
        for (var i = 0; i < el.properties.length; i++) {
            var p = el.properties[i];
            var desc = _renderBilingualText(p.description_ko || p.description, p.description_en || p.description);
            rows += '<tr><td><code>' + _escElementHtml(p.name) + '</code></td><td>' + _escElementHtml(p.type || '--') + '</td>' +
                '<td>' + _escElementHtml(p['default'] || '--') + '</td><td>' + desc + '</td></tr>';
        }
        tbody.innerHTML = rows;
    }
    var padsEl = DXStream.$('element-detail-pads');
    if (padsEl && el.pads) {
        var phtml = '';
        for (var i = 0; i < el.pads.length; i++) {
            var pad = el.pads[i];
            phtml += '<span class="badge b-cat" style="margin:2px">' + pad.name + ' (' + pad.direction + ')</span>';
        }
        padsEl.innerHTML = phtml || '<span class="txt-dim">--</span>';
    } else if (padsEl) {
        padsEl.innerHTML = '<span class="txt-dim">sink → src</span>';
    }
    detail.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
};

DXStream.closeElementDetail = function () {
    var detail = DXStream.$('element-detail');
    if (detail) detail.style.display = 'none';
};
if (typeof registerStreamLangRefresher === 'function') {
  registerStreamLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined' && DXStream.S && DXStream.S.currentPage && typeof DXStream.nav === 'function') {
      DXStream.nav(DXStream.S.currentPage);
    }
  });
}
