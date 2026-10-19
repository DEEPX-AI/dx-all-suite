/**
 * DX Stream Pipeline — state & constants module
 * Namespace, shared state, theme helpers, scheduling utilities, category info
 */

window.DXStreamPipeline = window.DXStreamPipeline || {};
window.DXStreamPipeline.publicApi = DXStream;

var _pipelineThemeColors = null;
var _canvasRefreshRaf = null;
var _commandPreviewRaf = null;
var _lastCommandPreviewText = null;
var _draftSaveTimer = null;

function _cachePipelineThemeColors() {
    var cs = getComputedStyle(document.documentElement);
    _pipelineThemeColors = {
        bg0: cs.getPropertyValue('--surface-page').trim() || '#0f0f1a',
        success: cs.getPropertyValue('--status-ok').trim(),
        warning: cs.getPropertyValue('--status-warn').trim(),
        raw: {},
    };
    return _pipelineThemeColors;
}

function _themeColor(name) {
    return (_pipelineThemeColors || _cachePipelineThemeColors())[name];
}

function _cv(k) {
    var colors = _pipelineThemeColors || _cachePipelineThemeColors();
    if (k === '--surface-page') return colors.bg0;
    if (k === '--status-ok') return colors.success;
    if (k === '--status-warn') return colors.warning;
    if (!colors.raw[k]) {
        colors.raw[k] = getComputedStyle(document.documentElement).getPropertyValue(k).trim();
    }
    return colors.raw[k];
}

/* Canvas color from a color token with alpha (hex · rgb() → rgba(…, a)). Unknown formats pass through. */
function _cvAlpha(k, a) {
    var c = _cv(k) || '';
    var m = c.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i);
    if (m) {
        var h = m[1].length === 3 ? m[1].replace(/./g, function (x) { return x + x; }) : m[1];
        return 'rgba(' + parseInt(h.slice(0, 2), 16) + ',' + parseInt(h.slice(2, 4), 16) + ',' +
            parseInt(h.slice(4, 6), 16) + ',' + a + ')';
    }
    m = c.match(/^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/i);
    return m ? 'rgba(' + m[1] + ',' + m[2] + ',' + m[3] + ',' + a + ')' : c;
}

/* When the theme changes (user or system), re-read the colors and redraw; otherwise the canvas keeps the colors
   it read first. */
if (window.DXTheme && typeof DXTheme.onThemeChange === 'function') {
    DXTheme.onThemeChange(function () {
        _pipelineThemeColors = null;
        requestAnimationFrame(function () {   // let CSS apply the new theme first
            _pipelineThemeColors = null;
            if (typeof _refreshCanvas === 'function') { try { _refreshCanvas(); } catch (e) { /* no canvas */ } }
        });
    });
}

function _scheduleCanvasRefresh() {
    if (_canvasRefreshRaf) return;
    _canvasRefreshRaf = requestAnimationFrame(function () {
        _canvasRefreshRaf = null;
        _refreshCanvas();
    });
}

function _scheduleCommandPreview() {
    if (_commandPreviewRaf) return;
    _commandPreviewRaf = requestAnimationFrame(function () {
        _commandPreviewRaf = null;
        _updateCommandPreview();
    });
}

function _setCommandPreviewText(el, text, muted) {
    var signature = (muted ? 'muted:' : 'plain:') + text;
    if (_lastCommandPreviewText === signature) return;
    _lastCommandPreviewText = signature;
    if (muted) {
        el.innerHTML = '<span class="txt-dim">' + DXStream.escHtml(text) + '</span>';
    } else {
        el.textContent = text;
    }
}

function _scheduleDraftSave(snap) {
    if (_draftSaveTimer) clearTimeout(_draftSaveTimer);
    _draftSaveTimer = setTimeout(function () {
        _draftSaveTimer = null;
        try { localStorage.setItem('dx-pipeline-draft', snap); } catch(_) {}
    }, 250);
}


var _NODE_W = 160, _NODE_H = 56, _PORT_R = 6, _PORT_HIT = 12;

DXStream._pipeState = {
    zoom: 1.0,
    offsetX: 0,
    offsetY: 0,
    elements: [],       // raw API response (grouped dict)
    elementFlat: [],     // flat array of all elements
    nodes: [],           // [{id, type, name, category, x, y, properties:{}}]
    edges: [],           // [{id, from, to}]  (node id → node id)
    selectedNode: null,  // node id (single-selection compatibility)
    selectedNodes: [],   // [node id, ...] (multi-selection)
    selectedEdge: null,   // edge id
    _nextId: 1,
    _clipboard: [],      // copied nodes

    _drag: null,         // {nodeId, startX, startY, origX, origY} or {multi: true, startX, startY, origPositions: [{id, x, y}]}
    _pan: null,          // {startX, startY, origOX, origOY}
    _edge: null,         // {fromId, mx, my}  — drawing edge
    _connectable: null,  // {allow: [id], warn: [{id,reason}], block: [{id,reason}]}

    _history: [],
    _historyIdx: -1,
};
DXStream._pipeRunning = false;

/* ── Category colors (kept in sync with the server's CATEGORY_COLORS) ── */
var _elemCatColors = {
    source:        '#3B82F6',
    preprocess:    '#F59E0B',
    inference:     '#8B5CF6',
    postprocess:   '#F97316',
    visualization: '#10B981',
    tracking:      '#EC4899',
    messaging:     '#06B6D4',
    output:        '#6366F1',
    utility:       '#94A3B8',
    default:       '#78909c',
};
var _elemCatIcons = {
    source:        'camera',
    preprocess:    'setup',
    inference:     'cpu',
    postprocess:   'models',
    visualization: 'eye',
    tracking:      'task-object_detection',
    messaging:     'send',
    output:        'external',
    utility:       'wrench',
};
function _catColor(cat) { return _elemCatColors[cat] || _elemCatColors.default; }
// Category icons are sprite names — lists draw them with DXIcon, the canvas with DXIcon.draw.
function _catIcon(cat) { return _elemCatIcons[cat] || 'circle'; }
var _catNameI18n = {
    source:        { ko: '소스',     ja: 'ソース',         'zh-CN': '源',      'zh-TW': '來源' },
    preprocess:    { ko: '전처리',   ja: '前処理',         'zh-CN': '预处理',  'zh-TW': '前處理' },
    inference:     { ko: '추론',     ja: '推論',           'zh-CN': '推理',    'zh-TW': '推論' },
    postprocess:   { ko: '후처리',   ja: '後処理',         'zh-CN': '后处理',  'zh-TW': '後處理' },
    visualization: { ko: '시각화',   ja: '可視化',         'zh-CN': '可视化',  'zh-TW': '視覺化' },
    tracking:      { ko: '추적',     ja: '追跡',           'zh-CN': '追踪',    'zh-TW': '追蹤' },
    messaging:     { ko: '메시징',   ja: 'メッセージング', 'zh-CN': '消息传递','zh-TW': '訊息傳遞' },
    output:        { ko: '출력',     ja: '出力',           'zh-CN': '输出',    'zh-TW': '輸出' },
    utility:       { ko: '유틸리티', ja: 'ユーティリティ', 'zh-CN': '实用工具','zh-TW': '實用工具' }
};
function _catLabel(cat) {
    var t = _catNameI18n[cat];
    if (!t) return cat;
    return t[DXStream.S.lang] || t.en || cat;
}
