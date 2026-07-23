'use strict';

var Dashboard = (function() {

/* Dark-only color palette for Canvas charts */
function _cc() {
  return {
    text:    '#B0BDD0',
    dim:     '#8892A8',
    strong:  '#E2E8F0',
    emph:    '#E2E8F0',
    noData:  '#8892A8',
    grid:    'rgba(255,255,255,0.06)',
    axes:    'rgba(255,255,255,0.15)',
    outline: 'rgba(0,0,0,0.7)',
    sel:     'rgba(99,140,255,0.12)',
    selBdr:  'rgba(99,140,255,0.7)'
  };
}

function dispatchBenchmarkHelpSync() {
  requestAnimationFrame(function() {
  });
}

function scheduleBenchmarkHover(chart, event) {
  chart._pendingHoverEvent = {
    clientX: event.clientX,
    clientY: event.clientY
  };
  if (chart._hoverRaf) return;
  chart._hoverRaf = requestAnimationFrame(function() {
    chart._hoverRaf = null;
    var e = chart._pendingHoverEvent;
    chart._pendingHoverEvent = null;
    if (!e) return;
    var i = chart._hitTest(e);
    if (i !== chart._hoverIdx) {
      chart._hoverIdx = i;
      chart._canvas.style.cursor = i >= 0 ? 'pointer' : 'default';
      chart._scheduleDraw();
    }
  });
}

function setBenchmarkCanvasSize(canvas, width, height, dpr) {
  var nextW = width * dpr;
  var nextH = height * dpr;
  var changed = canvas.width !== nextW || canvas.height !== nextH;
  if (canvas.width !== nextW) canvas.width = nextW;
  if (canvas.height !== nextH) canvas.height = nextH;
  if (canvas.style.width !== width + 'px') canvas.style.width = width + 'px';
  if (canvas.style.height !== height + 'px') canvas.style.height = height + 'px';
  return changed;
}

function _withTrailingSlash(url) {
  url = String(url || '');
  return url.endsWith('/') ? url : url + '/';
}

function _edgeGuideBase() {
  if (window.location.pathname.startsWith('/benchmark')) return '/planner/';
  var cfg = window.DX_BENCHMARK_CONFIG || window.DXBenchmarkConfig || {};
  if (cfg.plannerBaseUrl) return _withTrailingSlash(cfg.plannerBaseUrl);
  if (cfg.planner_url) return _withTrailingSlash(cfg.planner_url);
  var launchFn = _launcherLaunch();
  if (launchFn) return '/planner/';
  var currentPort = Number(window.location.port);
  if (Number.isInteger(currentPort) && currentPort > 1024) {
    return window.location.protocol + '//' + window.location.hostname + ':' + String(currentPort - 1) + '/';
  }
  return _withTrailingSlash(window.location.origin + '/planner');
}

function _launcherLaunch() {
  var candidates = [window.parent, window.top];
  for (var i = 0; i < candidates.length; i++) {
    var w = candidates[i];
    if (w && w !== window && typeof w.launch === 'function') return w.launch.bind(w);
  }
  return null;
}

function _buildEdgeGuideQuery(overrides) {
  var o = overrides || {};
  var task = o.task !== undefined ? o.task : (state.fpsTask || state.task || 'object_detection');
  var size = o.size !== undefined ? o.size : (state.size || 'n');
  var ortVal = o.ort;
  if (ortVal === undefined) {
    if (state.fpsOrt !== undefined) ortVal = state.fpsOrt;
    else if (state.ort !== undefined) ortVal = state.ort;
    else ortVal = true;
  }
  return new URLSearchParams({ task: task, size: size, ort: ortVal }).toString();
}

function _edgeGuideUrl(overrides) {
  return _edgeGuideBase() + '?' + _buildEdgeGuideQuery(overrides);
}

function _navigateToEdgeGuide(overrides) {
  var query = _buildEdgeGuideQuery(overrides);
  var launchFn = _launcherLaunch();
  if (launchFn) {
    launchFn('planner', query);
    return;
  }
  window.location.assign(_edgeGuideUrl(overrides));
}

function _appendEdgeGuideLink(parentEl, overrides) {
  if (!parentEl) return;
  var old = parentEl.querySelector('.edgeguide-link');
  if (old) old.remove();
  var el = document.createElement('a');
  el.className = 'edgeguide-link';
  el.href = _edgeGuideUrl(overrides);
  el.textContent = '💰 ' + _t('Find optimal product in EdgeGuide →');
  el.addEventListener('click', function(e) {
    e.preventDefault();
    _navigateToEdgeGuide(overrides);
  });
  parentEl.appendChild(el);
}

function _buildDashboardHTML() {
  return '<div class="page benchmark-workspace dashboard-workspace">' +
    '<header class="hero benchmark-workspace-hero">' +
      '<div>' +
        '<p class="eyebrow">YOLO26 Benchmark</p>' +
        '<h1 data-i18n="Performance Dashboard">' + _t('Performance Dashboard') + '</h1>' +
        '<p class="lede" data-i18n="Compare model performance across environments at a glance.">' + _t('Compare model performance across environments at a glance.') + '</p>' +
      '</div>' +
      '<div id="meta" class="meta-card"></div>' +
    '</header>' +
    '<nav class="tabs benchmark-segment-tabs">' +
      '<button class="dashboard-tab active" data-tab="fps-compare" data-i18n="E2E FPS Overview">' + _t('E2E FPS Overview') + '</button>' +
      '<button class="dashboard-tab" data-tab="overview" data-i18n="Full Metrics">' + _t('Full Metrics') + '</button>' +
      '<button class="dashboard-tab" data-tab="detail" data-i18n="Detailed Data">' + _t('Detailed Data') + '</button>' +
      '<button class="dashboard-tab" data-tab="version-trend" data-i18n="Version Trend">' + _t('Version Trend') + '</button>' +
      '<button class="dashboard-tab" data-tab="ort-compare" data-i18n="ORT ON/OFF">' + _t('ORT ON/OFF') + '</button>' +
    '</nav>' +
    '<div id="tab-fps-compare" class="tab-content active dashboard-panel-stack">' +
      '<div class="dashboard-filter-grid">' +
        '<section class="controls run-selector-panel">' +
          '<div class="control-heading" data-i18n="Run Selection by Environment">' + _t('Run Selection by Environment') + '</div>' +
          '<div id="fpsRunSelectors" class="run-selector-grid"></div>' +
        '</section>' +
        '<section class="controls controls--compact">' +
          '<label>' + _t('Task') + ' <select id="fpsTaskFilter">' +
            '<option value="object_detection">OD (' + _t('Object Detection') + ')</option>' +
            '<option value="pose_estimation">Pose (' + _t('Pose Estimation') + ')</option>' +
            '<option value="segmentation">Seg (' + _t('Segmentation') + ')</option>' +
            '<option value="oriented_bbox">OBB (' + _t('Oriented BBox (OBB)') + ')</option>' +
            '<option value="classification">Cls (' + _t('Classification') + ')</option>' +
          '</select></label>' +
          '<label>ORT <select id="fpsOrtFilter">' +
            '<option value="on">ON</option>' +
            '<option value="off">OFF</option>' +
          '</select></label>' +
        '</section>' +
      '</div>' +
      '<section class="panel chart-panel dashboard-primary">' +
        '<div class="chart-header">' +
          '<h2 id="fpsChartTitle" data-i18n="E2E FPS by Model Size">' + _t('E2E FPS by Model Size') + '</h2>' +
          '<p class="chart-subtitle" id="fpsChartSubtitle"></p>' +
        '</div>' +
        '<div class="chart-container"><canvas id="fpsCompareChart"></canvas></div>' +
        '<p class="chart-hint" id="fpsChartHint" data-i18n="Click on a bar group to view environment details">' + _t('Click on a bar group to view environment details') + '</p>' +
      '</section>' +
      '<div class="dashboard-detail-grid">' +
        '<section class="panel env-detail" id="fpsEnvDetail" data-help-id="bench-fps-env-detail" style="display:none">' +
          '<h2 id="fpsEnvDetailTitle" data-i18n="Environment Details">' + _t('Environment Details') + '</h2>' +
          '<div class="env-detail-grid env-detail-grid--3">' +
            '<div class="env-detail-col"><h3 data-i18n="Host PC">' + _t('Host PC') + '</h3><div id="fpsEnvHostInfo"></div></div>' +
            '<div class="env-detail-col"><h3>NPU</h3><div id="fpsEnvNpuInfo"></div></div>' +
            '<div class="env-detail-col"><h3 data-i18n="Tools">' + _t('Tools') + '</h3><div id="fpsEnvToolsInfo"></div></div>' +
          '</div>' +
        '</section>' +
        '<section class="panel" id="fpsModelMetaPanel" data-help-id="bench-fps-model-meta" style="display:none">' +
          '<h2 id="fpsModelMetaTitle" data-i18n="Benchmarked Models">' + _t('Benchmarked Models') + '</h2>' +
          '<div id="fpsModelMetaSection"></div>' +
        '</section>' +
        '<section class="panel dashboard-detail-wide" id="fpsE2eTableSection" data-help-id="bench-fps-e2e-table" style="display:none">' +
          '<h2 id="fpsE2eTableTitle" data-i18n="E2E Pipeline (Single-Stream)">' + _t('E2E Pipeline (Single-Stream)') + '</h2>' +
          '<div id="fpsE2eTableContent"></div>' +
        '</section>' +
      '</div>' +
    '</div>' +
    '<div id="tab-overview" class="tab-content dashboard-panel-stack">' +
      '<div class="dashboard-filter-grid">' +
        '<section class="controls run-selector-panel">' +
          '<div class="control-heading" data-i18n="Run Selection by Environment">' + _t('Run Selection by Environment') + '</div>' +
          '<div id="overviewRunSelectors" class="run-selector-grid"></div>' +
        '</section>' +
        '<section class="controls controls--compact">' +
          '<label>' + _t('Task') + ' <select id="taskFilter">' +
            '<option value="object_detection">OD (' + _t('Object Detection') + ')</option>' +
            '<option value="pose_estimation">Pose (' + _t('Pose Estimation') + ')</option>' +
            '<option value="segmentation">Seg (' + _t('Segmentation') + ')</option>' +
            '<option value="oriented_bbox">OBB (' + _t('Oriented BBox (OBB)') + ')</option>' +
            '<option value="classification">Cls (' + _t('Classification') + ')</option>' +
          '</select></label>' +
          '<label>' + _t('Size') + ' <select id="sizeFilter">' +
            '<option value="n">N (Nano)</option>' +
            '<option value="s">S (Small)</option>' +
            '<option value="m">M (Medium)</option>' +
            '<option value="l">L (Large)</option>' +
            '<option value="x">X (Extra-Large)</option>' +
          '</select></label>' +
          '<label>ORT <select id="ortFilter">' +
            '<option value="on">ON</option>' +
            '<option value="off">OFF</option>' +
          '</select></label>' +
        '</section>' +
      '</div>' +
      '<section class="panel chart-panel dashboard-primary">' +
        '<div class="chart-header">' +
          '<h2 id="chartTitle" data-i18n="Environment Performance Comparison">' + _t('Environment Performance Comparison') + '</h2>' +
          '<p class="chart-subtitle" id="chartSubtitle"></p>' +
        '</div>' +
        '<div class="chart-container"><canvas id="mainChart"></canvas></div>' +
        '<p class="chart-hint" id="chartHint" data-i18n="Click on a bar to view environment details">' + _t('Click on a bar to view environment details') + '</p>' +
      '</section>' +
      '<div class="dashboard-detail-grid">' +
        '<section class="panel env-detail" id="envDetail" data-help-id="bench-overview-env-detail" style="display:none">' +
          '<h2 id="envDetailTitle" data-i18n="Environment Details">' + _t('Environment Details') + '</h2>' +
          '<div class="env-detail-grid env-detail-grid--3">' +
            '<div class="env-detail-col"><h3 data-i18n="Host PC">' + _t('Host PC') + '</h3><div id="envHostInfo"></div></div>' +
            '<div class="env-detail-col"><h3>NPU</h3><div id="envNpuInfo"></div></div>' +
            '<div class="env-detail-col"><h3 data-i18n="Tools">' + _t('Tools') + '</h3><div id="envToolsInfo"></div></div>' +
          '</div>' +
        '</section>' +
        '<section class="panel" id="overviewModelMetaPanel" data-help-id="bench-overview-model-meta" style="display:none">' +
          '<h2 id="overviewModelMetaTitle" data-i18n="Benchmarked Models">' + _t('Benchmarked Models') + '</h2>' +
          '<div id="overviewModelMetaSection"></div>' +
        '</section>' +
      '</div>' +
    '</div>' +
    '<div id="tab-detail" class="tab-content dashboard-panel-stack">' +
      '<section class="controls">' +
        '<label>' + _t('Environment') + ' <select id="detailEnvFilter"></select></label>' +
        '<label>' + _t('Run ID') + ' <select id="detailRunFilter"></select></label>' +
        '<label>' + _t('Task') + ' <select id="detailTaskFilter">' +
          '<option value="all">' + _t('All Tasks') + '</option>' +
          '<option value="object_detection">OD (' + _t('Object Detection') + ')</option>' +
          '<option value="pose_estimation">Pose (' + _t('Pose Estimation') + ')</option>' +
          '<option value="segmentation">Seg (' + _t('Segmentation') + ')</option>' +
          '<option value="oriented_bbox">OBB (' + _t('Oriented BBox (OBB)') + ')</option>' +
          '<option value="classification">Cls (' + _t('Classification') + ')</option>' +
        '</select></label>' +
        '<label>ORT <select id="detailOrtFilter">' +
          '<option value="all">' + _t('All') + '</option>' +
          '<option value="on">ON</option>' +
          '<option value="off">OFF</option>' +
        '</select></label>' +
      '</section>' +
      '<section class="panel"><div id="detailTables"></div></section>' +
    '</div>' +
    '<div id="tab-version-trend" class="tab-content dashboard-panel-stack">' +
      '<section class="controls">' +
        '<label>' + _t('Environment') + ' <select id="trendEnvFilter"></select></label>' +
        '<label>' + _t('Task') + ' <select id="trendTaskFilter">' +
          '<option value="object_detection">OD (' + _t('Object Detection') + ')</option>' +
          '<option value="pose_estimation">Pose (' + _t('Pose Estimation') + ')</option>' +
          '<option value="segmentation">Seg (' + _t('Segmentation') + ')</option>' +
          '<option value="oriented_bbox">OBB (' + _t('Oriented BBox (OBB)') + ')</option>' +
          '<option value="classification">Cls (' + _t('Classification') + ')</option>' +
        '</select></label>' +
        '<label>ORT <select id="trendOrtFilter">' +
          '<option value="on">ON</option>' +
          '<option value="off">OFF</option>' +
        '</select></label>' +
      '</section>' +
      '<section class="controls trend-version-filter-panel">' +
        '<div class="trend-version-filter-heading-row">' +
          '<span class="control-heading" data-i18n="dx-all-suite Version">' + _t('dx-all-suite Version') + '</span>' +
          '<span class="version-filter-actions">' +
            '<button type="button" class="version-filter-btn" id="trendVersionAll" data-i18n="All">' + _t('All') + '</button>' +
            '<button type="button" class="version-filter-btn" id="trendVersionNone" data-i18n="None">' + _t('None') + '</button>' +
          '</span>' +
        '</div>' +
        '<div id="trendVersionFilter" class="version-filter-chips"></div>' +
      '</section>' +
      '<p class="chart-hint" data-i18n="Compare key metrics across dx-all-suite versions for the same hardware">' + _t('Compare key metrics across dx-all-suite versions for the same hardware') + '</p>' +
      '<div class="trend-charts-grid" id="trendChartsGrid"></div>' +
      '<p class="chart-hint" data-i18n="Click on a data point group to view snapshot environment details">' + _t('Click on a data point group to view snapshot environment details') + '</p>' +
      '<div class="dashboard-detail-grid">' +
        '<section class="panel env-detail" id="trendEnvDetail" data-help-id="bench-trend-env-detail" style="display:none">' +
          '<h2 id="trendEnvDetailTitle" data-i18n="Environment Details">' + _t('Environment Details') + '</h2>' +
          '<div class="env-detail-grid env-detail-grid--3">' +
            '<div class="env-detail-col"><h3 data-i18n="Host PC">' + _t('Host PC') + '</h3><div id="trendEnvHostInfo"></div></div>' +
            '<div class="env-detail-col"><h3>NPU</h3><div id="trendEnvNpuInfo"></div></div>' +
            '<div class="env-detail-col"><h3 data-i18n="Tools">' + _t('Tools') + '</h3><div id="trendEnvToolsInfo"></div></div>' +
          '</div>' +
        '</section>' +
        '<section class="panel" id="trendModelMetaPanel" data-help-id="bench-trend-model-meta" style="display:none">' +
          '<h2 id="trendModelMetaTitle" data-i18n="Benchmarked Models">' + _t('Benchmarked Models') + '</h2>' +
          '<div id="trendModelMetaSection"></div>' +
        '</section>' +
      '</div>' +
    '</div>' +
    '<div id="tab-ort-compare" class="tab-content dashboard-panel-stack">' +
      '<section class="controls">' +
        '<label>' + _t('Environment') + ' <select id="ortEnvFilter"></select></label>' +
        '<label>' + _t('Task') + ' <select id="ortTaskFilter">' +
          '<option value="object_detection">OD (' + _t('Object Detection') + ')</option>' +
          '<option value="pose_estimation">Pose (' + _t('Pose Estimation') + ')</option>' +
          '<option value="segmentation">Seg (' + _t('Segmentation') + ')</option>' +
          '<option value="oriented_bbox">OBB (' + _t('Oriented BBox (OBB)') + ')</option>' +
          '<option value="classification">Cls (' + _t('Classification') + ')</option>' +
        '</select></label>' +
        '<label>' + _t('Metric') + ' <select id="ortMetricFilter">' +
          '<option value="throughput_fps" data-i18n="Throughput (FPS)">' + _t('Throughput (FPS)') + '</option>' +
          '<option value="e2e_fps" data-i18n="E2E FPS (Single-Stream)">' + _t('E2E FPS (Single-Stream)') + '</option>' +
          '<option value="latency_ms" data-i18n="Latency (ms)">' + _t('Latency (ms)') + '</option>' +
          '<option value="capacity_streams" data-i18n="Max Channels">' + _t('Max Channels') + '</option>' +
        '</select></label>' +
      '</section>' +
      '<section class="panel chart-panel dashboard-primary">' +
        '<div class="chart-header">' +
          '<h2 id="ortChartTitle" data-i18n="ORT ON/OFF Comparison">' + _t('ORT ON/OFF Comparison') + '</h2>' +
          '<p class="chart-subtitle" id="ortChartSubtitle"></p>' +
        '</div>' +
        '<div class="chart-container"><canvas id="ortCompareChart"></canvas></div>' +
        '<p class="chart-hint" data-i18n="ORT changes the CPU/NPU balance — compare ON vs OFF for the same model and environment.">' + _t('ORT changes the CPU/NPU balance — compare ON vs OFF for the same model and environment.') + '</p>' +
      '</section>' +
      '<section class="panel" id="ortCompareTableSection">' +
        '<h2 data-i18n="ORT ON/OFF Detail">' + _t('ORT ON/OFF Detail') + '</h2>' +
        '<div id="ortCompareTableContent"></div>' +
      '</section>' +
    '</div>' +
  '</div>';
}

var TASK_MAP = {
  object_detection:  { label: 'Object Detection',    suffix: '1',    short: 'OD'   },
  pose_estimation:   { label: 'Pose Estimation',     suffix: 'pose', short: 'Pose' },
  segmentation:      { label: 'Segmentation',        suffix: 'seg',  short: 'Seg'  },
  oriented_bbox:     { label: 'Oriented BBox (OBB)', suffix: 'obb',  short: 'OBB'  },
  classification:    { label: 'Classification',      suffix: 'cls',  short: 'Cls'  },
};
var TASK_KEYS  = ['object_detection','pose_estimation','segmentation','oriented_bbox','classification'];
var TASK_ORDER = { object_detection: 0, pose_estimation: 1, segmentation: 2, oriented_bbox: 3, classification: 4 };
var SIZE_ORDER  = { n: 0, s: 1, m: 2, l: 3, x: 4 };
var SIZE_KEYS   = ['n', 's', 'm', 'l', 'x'];
var SIZE_LABELS = { n: 'Nano', s: 'Small', m: 'Medium', l: 'Large', x: 'X-Large' };
var SIZE_COLORS = {
  n: { fill: 'rgba(59,130,246,0.70)',  hi: 'rgba(59,130,246,0.95)',  line: 'rgb(59,130,246)',  dim: 'rgba(59,130,246,0.25)' },
  s: { fill: 'rgba(16,185,129,0.70)',  hi: 'rgba(16,185,129,0.95)',  line: 'rgb(16,185,129)',  dim: 'rgba(16,185,129,0.25)' },
  m: { fill: 'rgba(245,158,11,0.70)',  hi: 'rgba(245,158,11,0.95)',  line: 'rgb(245,158,11)',  dim: 'rgba(245,158,11,0.25)' },
  l: { fill: 'rgba(239,68,68,0.70)',   hi: 'rgba(239,68,68,0.95)',   line: 'rgb(239,68,68)',   dim: 'rgba(239,68,68,0.25)' },
  x: { fill: 'rgba(139,92,246,0.70)',  hi: 'rgba(139,92,246,0.95)',  line: 'rgb(139,92,246)',  dim: 'rgba(139,92,246,0.25)' },
};
var TREND_METRICS = [
  { key: 'latency', title: 'Model Latency Trend', metricLabel: 'Model Latency', axisLabel: 'Latency (ms)', resultKind: 'model', family: 'latency', valueKey: 'latency_ms', precision: 2 },
  { key: 'throughput', title: 'Model Throughput Trend', metricLabel: 'Model Throughput', axisLabel: 'Throughput (FPS)', resultKind: 'model', family: 'throughput', valueKey: 'fps', precision: 1 },
  { key: 'e2e', title: 'E2E FPS (Single-Channel) Trend', metricLabel: 'E2E FPS (Single-Channel)', axisLabel: 'E2E FPS', resultKind: 'e2e_single', valueKey: 'avg_e2e_fps', precision: 1 },
  { key: 'capacity', title: 'Max Channel Trend', metricLabel: 'Max Channels', axisLabel: 'Max Channels', resultKind: 'e2e_multi_capacity', valueKey: 'capacity_streams', precision: 0 },
];
/* ORT ON/OFF comparison: keys/labels mirror summaries.ort_delta's `metric` values 1:1. */
var ORT_METRICS = [
  { key: 'throughput_fps',   label: 'Throughput (FPS)',            axisLabel: 'Throughput (FPS)', precision: 1, higherBetter: true  },
  { key: 'e2e_fps',          label: 'E2E FPS (Single-Stream)',      axisLabel: 'E2E FPS',          precision: 1, higherBetter: true  },
  { key: 'latency_ms',       label: 'Latency (ms)',                 axisLabel: 'Latency (ms)',     precision: 2, higherBetter: false },
  { key: 'capacity_streams', label: 'Max Channels',                 axisLabel: 'Max Channels',     precision: 0, higherBetter: true  },
];
var ORT_ON_COLOR  = { fill: 'rgba(91,141,239,0.70)',  line: 'rgb(91,141,239)'  };
var ORT_OFF_COLOR = { fill: 'rgba(245,158,11,0.70)',  line: 'rgb(245,158,11)' };

function sizeOrd(key) { var v = SIZE_ORDER[key]; return v !== undefined ? v : 99; }

var state = {
  dataset: null,
  task: 'object_detection', size: 'n', ort: true,
  selectedEnvId: null, chartData: [],
  fpsTask: 'object_detection', fpsOrt: true,
  fpsSelectedEnvId: null, fpsChartData: [],
  selectedRunIds: {},
  detailEnvId: null, detailTask: 'all', detailOrt: 'all',
  trendHwId: null, trendTask: 'object_detection', trendOrt: true,
  trendDataByMetric: {}, trendSelectedIdx: -1, trendCharts: {},
  trendVersions: [], trendVersionFilter: {},
  ortEnvId: null, ortTask: 'object_detection', ortMetric: 'throughput_fps', ortChartData: [],
};

function getModelName(task, size) { return 'yolo26' + size + '-' + TASK_MAP[task].suffix + '.dxnn'; }
/* Tolerant NPU product-label reader: prefers npu_sku, then npu_product, then the
   first entry of the npu_modules block (new-tool shapes); null if none present. */
function _envProductLabel(env) {
  env = env || {};
  if (env.npu_sku) return env.npu_sku;
  if (env.npu_product) return env.npu_product;
  if (Array.isArray(env.npu_modules) && env.npu_modules.length) {
    var m = env.npu_modules[0];
    if (m && m.product) return (m.count && m.count > 1) ? (m.product + ' ×' + m.count) : m.product;
  }
  return null;
}
function envLabel(env) { env = env || {}; return (env.hw_id || env.hostname || 'unknown') + '\n(' + (_envProductLabel(env) || '?') + ')'; }
/* Tolerant suite-version reader: new dataset carries dx_all_suite_version on
   both env and run objects; falls back to 'unknown' if absent (older shape). */
function envVersion(env) { env = env || {}; return env.dx_all_suite_version || env.suite_version || env.version || 'unknown'; }
function fmt(v, d) { if (v === null || v === undefined) return '-'; var n = Number(v); return Number.isNaN(n) ? '-' : n.toFixed(d === undefined ? 1 : d); }
function modelSizeChar(name) { var m = String(name||'').match(/yolo26([nslmx])/i); return m ? m[1].toLowerCase() : ''; }
function formatInputShape(shape) {
  if (!shape || !Array.isArray(shape)) return '-';
  if (shape.length === 4) return shape[1] + '\u00d7' + shape[2];
  return shape.join('\u00d7');
}
function formatMemMB(mb) { if (mb == null) return '-'; return Number(mb).toFixed(1); }
function escHtml(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
function _fmtTemp(lo,hi){if(lo==null&&hi==null)return'-';var a=lo!=null?Math.round(lo):'?';var b=hi!=null?Math.round(hi):'?';return a===b?String(a):a+'~'+b;}
function _fmtClock(lo,hi){if(lo==null&&hi==null)return'\u2014';var a=lo!=null?Math.round(lo):'?';var b=hi!=null?Math.round(hi):'?';return a===b?String(a):a+'~'+b;}
/* Resume/retry status badges: dataset carries per-condition `status` in
   summaries.model / e2e_single / e2e_multi_capacity (observed values: ok,
   partial, timeout, error). No `reason` field exists in the dataset \u2014 for
   e2e_single 'partial' the closest available detail is runs/requested_runs. */
var STATUS_SEVERITY = { ok: 0, partial: 1, timeout: 2, error: 2 };
var STATUS_BADGE_CLASS = { partial: 'tag--warn', timeout: 'tag--err', error: 'tag--err' };
var STATUS_LABEL_KEY = { ok: 'OK', partial: 'Partial', timeout: 'Timeout', error: 'Error' };
function _statusLabel(status) { return STATUS_LABEL_KEY[status] || status; }
function _statusSeverity(status) { var v = STATUS_SEVERITY[status]; return v === undefined ? 1 : v; }
function _statusBadge(status, detail) {
  if (!status || status === 'ok') return '-';
  var cls = STATUS_BADGE_CLASS[status] || 'tag--warn';
  var titleAttr = detail ? ' title="' + escHtml(detail) + '"' : '';
  return '<span class="tag ' + cls + '"' + titleAttr + '>' + _t(_statusLabel(status)) + '</span>';
}
function stripAnsi(s) { return typeof s === 'string' ? s.replace(/\x1b\[[0-9;]*m/g, '') : s; }
function _history(kind){return ((state.dataset.history||{})[kind])||((state.dataset.summaries||{})[kind])||[];}
/* Selected-run comparisons are driven from state.dataset.history.e2e_single and friends. */
function _envById(envId){return (state.dataset.environments||[]).find(function(env){return env.env_id===envId;})||null;}
function _getRunOptions(envId){var rows=(state.dataset.runs||[]).filter(function(r){return r.env_id===envId;});rows.sort(function(a,b){return (b.run_id||'').localeCompare(a.run_id||'');});return rows;}
function _getSelectedRunId(envId){var env=_envById(envId);return state.selectedRunIds[envId]||(env?env.latest_run_id:null);}
function _initSelectedRunIds(){(state.dataset.environments||[]).forEach(function(env){state.selectedRunIds[env.env_id]=env.latest_run_id;});}
function _syncRunSelectors(envId,runId){document.querySelectorAll('select[data-run-env]').forEach(function(sel){if(sel.dataset.runEnv===envId)sel.value=runId;});}
function syncDetailRunFilter(){
  var sel=document.getElementById('detailRunFilter');if(!sel)return;
  var envId=state.detailEnvId;var runs=envId?_getRunOptions(envId):[];
  sel.innerHTML=runs.map(function(run){return '<option value="'+escHtml(run.run_id)+'">'+escHtml(run.run_id)+'</option>';}).join('');
  sel.disabled=!runs.length;
  if(runs.length){sel.value=_getSelectedRunId(envId)||runs[0].run_id;}
}
function _handleRunSelectionChange(envId,runId){state.selectedRunIds[envId]=runId;_syncRunSelectors(envId,runId);refreshFpsCompare(envId);refreshChart(envId);if(state.detailEnvId===envId){syncDetailRunFilter();renderDetailTables();}}
function renderRunSelectors(targetId){
  var target=document.getElementById(targetId);if(!target)return;
  var envs=state.dataset.environments||[];
  if(!envs.length){target.innerHTML='<p class="empty-state small">' + _t('No environments available.') + '</p>';return;}
  target.innerHTML=envs.map(function(env){
    var runs=_getRunOptions(env.env_id);if(!runs.length)return '';
    var options=runs.map(function(run){return '<option value="'+escHtml(run.run_id)+'">'+escHtml(run.run_id)+'</option>';}).join('');
    return '<label><span>'+escHtml(env.hostname)+' ('+escHtml(_envProductLabel(env)||'?')+')</span><select data-run-env="'+escHtml(env.env_id)+'">'+options+'</select></label>';
  }).join('');
  target.querySelectorAll('select[data-run-env]').forEach(function(sel){
    var envId=sel.dataset.runEnv;sel.value=_getSelectedRunId(envId)||sel.value;
    sel.addEventListener('change',function(){_handleRunSelectionChange(envId,this.value);});
  });
}


function _infoRows(r) { return r.map(function(row) { return '<div class="info-row"><span class="info-key">'+escHtml(row[0])+'</span><span class="info-val">'+escHtml(row[1]!=null?String(row[1]):'-')+'</span></div>'; }).join(''); }
function cleanVer(v) { if (typeof v !== 'string') return v; return v.replace(/^DXRT\s+/i,'').replace(/^v(?=\d)/i,''); }
/* Formats the npu_modules block (new-tool shape: [{product,count},...]) into a
   single readable string, e.g. "H1-Quattro ×1" or "M1 ×2, M1M ×1". */
function _fmtNpuModules(env) {
  var mods = (env && Array.isArray(env.npu_modules)) ? env.npu_modules : [];
  if (!mods.length) return '-';
  return mods.map(function(m) {
    if (!m) return '?';
    var p = m.product || '?';
    return (m.count != null) ? (p + ' ×' + m.count) : p;
  }).join(', ');
}
function renderHostInfo(el, env) {
  var rows = [[_t('Product Name'),env.product_name||'-'],['Hostname',env.hostname],['OS',env.os],['Kernel',env.kernel],['Architecture',env.arch],['CPU',env.cpu],['CPU Cores',env.cpu_count],['RAM',env.ram_gb?env.ram_gb+' GB':'-']];
  el.innerHTML = _infoRows(rows);
}
function renderToolsInfo(el, env) {
  var rows = [['dx_stream',cleanVer(env.dx_stream_version)||'-'],['GStreamer',cleanVer(env.gstreamer_version)||'-']];
  el.innerHTML = _infoRows(rows);
}
function renderNpuInfo(el, env) {
  var rows = [['Product',env.npu_product||_envProductLabel(env)||'-'],[_t('SKU'),env.npu_sku||'-'],[_t('Modules'),_fmtNpuModules(env)],[_t('Device Count'),(env.npu_device_count!=null)?env.npu_device_count:'-'],['DXRT',cleanVer(env.rt_version)],['RT Driver',cleanVer(env.rt_driver)],['PCIe Driver',cleanVer(env.pcie_driver)],['Firmware',cleanVer(env.firmware)],['Clock',env.npu_clock_mhz?env.npu_clock_mhz+' MHz':'-'],['Memory',env.memory],['Board',(env.board && env.board !== 'unknown') ? env.board : '-'],['PCIe',env.pcie]];
  el.innerHTML = _infoRows(rows);
}

function renderModelMetaForTask(container, env, task) {
  var models = (env.benchmarked_models || []).filter(function(m) { return m.task === task; });
  if (!models.length) { container.innerHTML = '<p class="empty-state small">' + _t('No data for this task.') + '</p>'; return; }
  models.sort(function(a,b) { return sizeOrd(a.size) - sizeOrd(b.size); });
  var html = '<table class="summary-table bench-table"><colgroup><col style="width:34%"><col style="width:8%"><col style="width:14%"><col style="width:14%"><col style="width:15%"><col style="width:15%"></colgroup><thead><tr><th>' + _t('Model') + '</th><th>' + _t('Size') + '</th><th>' + _t('Input') + '</th><th>' + _t('NPU Mem (MB)') + '</th><th>' + _t('DXNN Format') + '</th><th>DX-COM</th></tr></thead><tbody>';
  models.forEach(function(m) {
    var input = formatInputShape(m.input_tensor_shape || m.input_size);
    var mem = formatMemMB(m.total_memory_mb);
    html += '<tr><td>' + escHtml(m.name||'-') + '</td><td>' + (m.size||'-').toUpperCase() + '</td><td>' + input + '</td><td>' + mem + '</td><td>' + escHtml(stripAnsi(m.format_version)||'-') + '</td><td>' + escHtml(stripAnsi(m.dxcom_version)||'-') + '</td></tr>';
  });
  html += '</tbody></table>';
  container.innerHTML = html;
}

function renderE2eTable(container, envId, task, useOrt, runId) {
  var rows = _history('e2e_single').filter(function(r) {
    return r.env_id === envId && r.run_id===runId && r.task === task && r.use_ort === useOrt;
  });
  rows.sort(function(a,b) { return sizeOrd(modelSizeChar(a.model)) - sizeOrd(modelSizeChar(b.model)); });
  if (!rows.length) { container.innerHTML = '<p class="empty-state">' + _t('No E2E data for this selection.') + '</p>'; return; }

  var html = '';
  /* Decode path summary from first row with pipeline_caps */
  var caps = null;
  for (var ci=0;ci<rows.length;ci++){if(rows[ci].pipeline_caps){caps=rows[ci].pipeline_caps;break;}}
  if (caps) {
    var parts = [];
    if (caps.video_codec) parts.push('<b>Codec:</b> '+escHtml(caps.video_codec));
    /* Decoder element name (same for all rows in this env) */
    var decName = null;
    for (var di=0;di<rows.length;di++){if(rows[di].decoder && rows[di].decoder!=='unknown'){decName=rows[di].decoder;break;}}
    if (decName) parts.push('<b>Decoder:</b> '+escHtml(decName));
    var decFmt = caps.decoder_src_format||'?';
    var decMem = caps.decoder_src_memory;
    parts.push('<b>Decoder Out:</b> '+escHtml(decFmt)+(decMem?' <span class="tag tag--warn">'+escHtml(decMem)+'</span>':''));
    var ppFmt = caps.dxpreprocess_sink_format||'?';
    var ppMem = caps.dxpreprocess_sink_memory;
    parts.push('<b>Preprocess In:</b> '+escHtml(ppFmt)+(ppMem?' <span class="tag tag--warn">'+escHtml(ppMem)+'</span>':''));
    if (caps.dxpreprocess_backend) parts.push('<b>Preprocess Backend:</b> '+escHtml(caps.dxpreprocess_backend));
    html += '<p class="decode-path-summary">'+parts.join(' &nbsp;|&nbsp; ')+'</p>';
  }

  html += '<table class="summary-table"><thead><tr><th>Model</th><th>E2E FPS</th><th>CPU%</th><th>NPU Avg%</th><th>NPU Max%</th><th>NPU Temp \u00b0C</th><th>NPU MHz</th><th>Host RSS (MiB)</th><th>Runs</th><th>Status</th></tr></thead><tbody>';
  rows.forEach(function(r) {
    var fpsS=fmt(r.avg_e2e_fps,1);if(r.fps_std!=null)fpsS+=' \u00b1'+fmt(r.fps_std,1);
    var tempS=_fmtTemp(r.npu_temp_min_c,r.npu_temp_max_c);
    var clkS=_fmtClock(r.npu_clock_mhz_min,r.npu_clock_mhz_max);
    var statusDetail=(r.status&&r.status!=='ok'&&r.runs!=null&&r.requested_runs!=null)?((r.runs)+'/'+(r.requested_runs)+' '+_t('runs completed')):null;
    html += '<tr><td>'+escHtml(r.model)+'</td><td>'+fpsS+'</td><td>'+fmt(r.avg_cpu_pct,0)+'</td><td>'+fmt(r.npu_total_avg_pct,1)+'</td><td>'+fmt(r.npu_total_max_pct,1)+'</td><td>'+tempS+'</td><td>'+clkS+'</td><td>'+fmt(r.max_rss_mib,0)+'</td><td>'+(r.runs||'-')+'/'+(r.requested_runs||'-')+'</td><td>'+_statusBadge(r.status,statusDetail)+'</td></tr>';
  });
  html += '</tbody></table>';
  container.innerHTML = html;
}

var Chart = {
  _canvas: null, _onClick: null, _hoverIdx: -1, _data: [], _selectedId: null, _raf: null, _ro: null,
  init: function(canvas, onClick) {
    this._canvas = canvas; this._onClick = onClick;
    this._ro = new ResizeObserver(this._resize.bind(this));
    this._ro.observe(canvas.parentElement); this._resize();
    canvas.addEventListener('click', this._handleClick.bind(this));
    canvas.addEventListener('mousemove', this._handleHover.bind(this));
    canvas.addEventListener('mouseleave', this._handleLeave.bind(this));
  },
  update: function(data, selectedId) { this._data = data; this._selectedId = selectedId; this._scheduleDraw(); },
  _resize: function() {
    var el=this._canvas.parentElement, dpr=window.devicePixelRatio||1;
    var w=el.clientWidth, h=el.clientHeight;
    setBenchmarkCanvasSize(this._canvas,w,h,dpr);
    this._canvas.getContext('2d').setTransform(dpr,0,0,dpr,0,0); this._scheduleDraw();
  },
  _scheduleDraw: function() { var s=this; if(s._raf) cancelAnimationFrame(s._raf); s._raf=requestAnimationFrame(function(){s._draw();}); },
  _layout: function() { var dpr=window.devicePixelRatio||1; var W=this._canvas.width/dpr,H=this._canvas.height/dpr; var P={top:65,right:90,bottom:90,left:72}; return {W:W,H:H,P:P,CW:W-P.left-P.right,CH:H-P.top-P.bottom}; },
  _niceMax: function(v) { if(v<=0)return 10; var e=Math.pow(10,Math.floor(Math.log10(v))); var f=v/e; return (f<=2?2:f<=5?5:10)*e; },
  _scales: function(data) {
    var maxFps=0,maxLat=0;
    data.forEach(function(d){if(d.throughput)maxFps=Math.max(maxFps,d.throughput);if(d.e2eFps)maxFps=Math.max(maxFps,d.e2eFps);if(d.latency)maxLat=Math.max(maxLat,d.latency);});
    return {fpsCeil:this._niceMax(maxFps*1.3),latCeil:this._niceMax(maxLat*1.35)};
  },
  _draw: function() {
    var data=this._data,cv=this._canvas,ctx=cv.getContext('2d');var lay=this._layout();var W=lay.W,H=lay.H,P=lay.P,CW=lay.CW,CH=lay.CH;var cc=_cc();ctx.clearRect(0,0,W,H);
    if(!data.length){ctx.fillStyle=cc.noData;ctx.font='14px sans-serif';ctx.textAlign='center';ctx.fillText(_t('No data for this selection'),W/2,H/2);return;}
    var sc=this._scales(data);var fpsCeil=sc.fpsCeil,latCeil=sc.latCeil;
    var n=data.length,gW=CW/n,bW=gW*0.34;
    var fpsY=function(v){return P.top+CH-(v/fpsCeil)*CH;};var latY=function(v){return P.top+CH-(v/latCeil)*CH;};
    var gX=function(i){return P.left+i*gW+gW*0.1;};var midX=function(i){return P.left+i*gW+gW*0.5;};
    var C_TP={fill:'rgba(91,141,239,0.60)',hi:'rgba(91,141,239,0.90)',line:'rgb(91,141,239)',dim:'rgba(91,141,239,0.25)'};
    var C_E2E={fill:'rgba(46,204,113,0.60)',hi:'rgba(46,204,113,0.90)',line:'rgb(46,204,113)',dim:'rgba(46,204,113,0.25)'};
    var C_LAT='rgb(231,76,60)';var C_MAX='rgb(136,84,208)';var self=this;
    /* Grid */ctx.strokeStyle=cc.grid;ctx.lineWidth=1;for(var g=0;g<=5;g++){var gy=P.top+CH*g/5;ctx.beginPath();ctx.moveTo(P.left,gy);ctx.lineTo(P.left+CW,gy);ctx.stroke();}
    /* Axes */ctx.strokeStyle=cc.axes;ctx.lineWidth=1.5;[[P.left,P.top,P.left,P.top+CH],[P.left,P.top+CH,P.left+CW,P.top+CH],[P.left+CW,P.top,P.left+CW,P.top+CH]].forEach(function(l){ctx.beginPath();ctx.moveTo(l[0],l[1]);ctx.lineTo(l[2],l[3]);ctx.stroke();});
    /* Y left */ctx.textAlign='right';for(var t=0;t<=5;t++){var tv=fpsCeil*(5-t)/5,ty=P.top+CH*t/5;ctx.fillStyle=cc.dim;ctx.font='11px sans-serif';ctx.fillText(Math.round(tv),P.left-6,ty+4);}
    /* Y right */ctx.textAlign='left';for(var t2=0;t2<=5;t2++){var tv2=latCeil*(5-t2)/5,ty2=P.top+CH*t2/5;ctx.fillStyle=C_LAT;ctx.font='11px sans-serif';ctx.fillText(Math.round(tv2),P.left+CW+8,ty2+4);}
    ctx.save();ctx.fillStyle=cc.text;ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.translate(14,P.top+CH/2);ctx.rotate(-Math.PI/2);ctx.fillText('FPS',0,0);ctx.restore();
    ctx.save();ctx.fillStyle=C_LAT;ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.translate(W-14,P.top+CH/2);ctx.rotate(Math.PI/2);ctx.fillText('Latency (ms)',0,0);ctx.restore();
    data.forEach(function(d,i){
      var sel=d.envId===self._selectedId;var hi=sel||i===self._hoverIdx;
      if(d.throughput!=null){var bx=gX(i),by=fpsY(d.throughput),bh=P.top+CH-by;ctx.fillStyle=sel?C_TP.hi:(self._selectedId&&!sel?C_TP.dim:(hi?C_TP.hi:C_TP.fill));ctx.fillRect(bx,by,bW-2,bh);ctx.strokeStyle=C_TP.line;ctx.lineWidth=sel?2:1;ctx.strokeRect(bx,by,bW-2,bh);ctx.fillStyle=C_TP.line;ctx.font='bold 10px sans-serif';ctx.textAlign='center';ctx.fillText(Math.round(d.throughput),bx+(bW-2)/2,by-4);}
      if(d.e2eFps!=null){var bx2=gX(i)+bW,by2=fpsY(d.e2eFps),bh2=P.top+CH-by2;ctx.fillStyle=sel?C_E2E.hi:(self._selectedId&&!sel?C_E2E.dim:(hi?C_E2E.hi:C_E2E.fill));ctx.fillRect(bx2+1,by2,bW-2,bh2);ctx.strokeStyle=C_E2E.line;ctx.lineWidth=sel?2:1;ctx.strokeRect(bx2+1,by2,bW-2,bh2);ctx.fillStyle=cc.strong;ctx.font='bold 10px sans-serif';ctx.textAlign='center';ctx.fillText(Math.round(d.e2eFps),bx2+1+(bW-2)/2,by2-4);}
      if(d.maxChannels!=null&&d.e2eFps!=null){var badgeX=gX(i)+bW+(bW-2)/2;var badgeY=fpsY(d.e2eFps)-20;var txt='Max '+d.maxChannels+'ch';ctx.font='bold 9px sans-serif';var tw=ctx.measureText(txt).width;var px=4,py=2,rr=4;var rx=badgeX-tw/2-px,ry=badgeY-8-py;var rw=tw+px*2,rh=12+py*2;ctx.fillStyle='rgba(136,84,208,0.15)';ctx.beginPath();ctx.moveTo(rx+rr,ry);ctx.lineTo(rx+rw-rr,ry);ctx.quadraticCurveTo(rx+rw,ry,rx+rw,ry+rr);ctx.lineTo(rx+rw,ry+rh-rr);ctx.quadraticCurveTo(rx+rw,ry+rh,rx+rw-rr,ry+rh);ctx.lineTo(rx+rr,ry+rh);ctx.quadraticCurveTo(rx,ry+rh,rx,ry+rh-rr);ctx.lineTo(rx,ry+rr);ctx.quadraticCurveTo(rx,ry,rx+rr,ry);ctx.closePath();ctx.fill();ctx.strokeStyle=C_MAX;ctx.lineWidth=1;ctx.stroke();ctx.fillStyle=C_MAX;ctx.textAlign='center';ctx.fillText(txt,badgeX,badgeY);}
      if(sel){ctx.save();ctx.strokeStyle=cc.selBdr;ctx.lineWidth=3;ctx.setLineDash([6,3]);var sx=gX(i)-4,sw=bW*2+6;ctx.strokeRect(sx,P.top,sw,CH);ctx.setLineDash([]);ctx.restore();}
    });
    var pts=data.map(function(d,i){return{x:midX(i),y:d.latency!=null?latY(d.latency):null,v:d.latency};});
    ctx.strokeStyle=C_LAT;ctx.lineWidth=2;ctx.setLineDash([8,5]);ctx.beginPath();var started=false;
    pts.forEach(function(p){if(p.y==null)return;if(!started){ctx.moveTo(p.x,p.y);started=true;}else{ctx.lineTo(p.x,p.y);}});ctx.stroke();ctx.setLineDash([]);
    pts.forEach(function(p){if(p.y==null)return;ctx.save();ctx.translate(p.x,p.y);ctx.rotate(Math.PI/4);ctx.fillStyle=C_LAT;ctx.fillRect(-5,-5,10,10);ctx.strokeStyle=cc.outline;ctx.lineWidth=2;ctx.strokeRect(-5,-5,10,10);ctx.restore();ctx.fillStyle=C_LAT;ctx.font='bold 10px sans-serif';ctx.textAlign='center';ctx.fillText(p.v.toFixed(1)+' ms',p.x,p.y-14);});
    /* X labels */ctx.fillStyle=cc.text;data.forEach(function(d,i){var parts=d.label.split('\n'),lx=midX(i);parts.forEach(function(part,pi){ctx.font=pi===0?'600 11px sans-serif':'11px sans-serif';ctx.textAlign='center';ctx.fillText(part,lx,P.top+CH+16+pi*14);});});
    var items=[{c:C_LAT,bc:C_LAT,label:'NPU Latency (Single-Core)',line:true},{c:C_TP.fill,bc:C_TP.line,label:'NPU Throughput (Multi-Core)',line:false},{c:C_E2E.fill,bc:C_E2E.line,label:'E2E FPS (Single-Stream)',line:false},{c:C_MAX,bc:C_MAX,label:'Max Channels (\u2265 30fps)',line:false,badge:true}];
    var lx=P.left,ly=22;items.forEach(function(it){if(it.line){ctx.strokeStyle=it.c;ctx.lineWidth=2;ctx.setLineDash([6,4]);ctx.beginPath();ctx.moveTo(lx,ly);ctx.lineTo(lx+20,ly);ctx.stroke();ctx.setLineDash([]);ctx.save();ctx.translate(lx+10,ly);ctx.rotate(Math.PI/4);ctx.fillStyle=it.c;ctx.fillRect(-4,-4,8,8);ctx.restore();}else if(it.badge){ctx.fillStyle='rgba(136,84,208,0.15)';ctx.fillRect(lx,ly-7,18,14);ctx.strokeStyle=it.bc;ctx.lineWidth=1;ctx.strokeRect(lx,ly-7,18,14);ctx.fillStyle=it.c;ctx.font='bold 8px sans-serif';ctx.textAlign='center';ctx.fillText('ch',lx+9,ly+3);}else{ctx.fillStyle=it.c;ctx.fillRect(lx,ly-7,18,14);ctx.strokeStyle=it.bc;ctx.lineWidth=1;ctx.strokeRect(lx,ly-7,18,14);}ctx.fillStyle=cc.text;ctx.font='12px sans-serif';ctx.textAlign='left';ctx.fillText(it.label,lx+24,ly+4);lx+=ctx.measureText(it.label).width+44;});
  },
  _hitTest: function(e){var rect=this._canvas.getBoundingClientRect();var x=e.clientX-rect.left;var lay=this._layout();if(x<lay.P.left||x>lay.P.left+lay.CW||!this._data.length)return -1;return Math.min(Math.floor((x-lay.P.left)/(lay.CW/this._data.length)),this._data.length-1);},
  _handleClick: function(e){var i=this._hitTest(e);if(i>=0&&this._onClick)this._onClick(i,this._data[i]);},
  _handleHover: function(e){scheduleBenchmarkHover(this,e);},
  _handleLeave: function(){this._pendingHoverEvent=null;if(this._hoverRaf){cancelAnimationFrame(this._hoverRaf);this._hoverRaf=null;}this._hoverIdx=-1;this._canvas.style.cursor='default';this._scheduleDraw();},
};

var FpsChart = {
  _canvas: null, _onClick: null, _hoverIdx: -1, _data: [], _selectedId: null, _raf: null, _ro: null,
  init: function(canvas, onClick) {
    this._canvas=canvas; this._onClick=onClick;
    this._ro=new ResizeObserver(this._resize.bind(this));
    this._ro.observe(canvas.parentElement); this._resize();
    canvas.addEventListener('click',this._handleClick.bind(this));
    canvas.addEventListener('mousemove',this._handleHover.bind(this));
    canvas.addEventListener('mouseleave',this._handleLeave.bind(this));
  },
  update: function(data,selectedId){this._data=data;this._selectedId=selectedId;this._scheduleDraw();},
  _resize: function(){var el=this._canvas.parentElement,dpr=window.devicePixelRatio||1;var w=el.clientWidth,h=el.clientHeight;setBenchmarkCanvasSize(this._canvas,w,h,dpr);this._canvas.getContext('2d').setTransform(dpr,0,0,dpr,0,0);this._scheduleDraw();},
  _scheduleDraw: function(){var s=this;if(s._raf)cancelAnimationFrame(s._raf);s._raf=requestAnimationFrame(function(){s._draw();});},
  _layout: function(){var dpr=window.devicePixelRatio||1;var W=this._canvas.width/dpr,H=this._canvas.height/dpr;var P={top:55,right:30,bottom:90,left:72};return {W:W,H:H,P:P,CW:W-P.left-P.right,CH:H-P.top-P.bottom};},
  _niceMax: function(v){if(v<=0)return 10;var e=Math.pow(10,Math.floor(Math.log10(v)));var f=v/e;return (f<=1.5?2:f<=3?4:f<=6?8:10)*e;},
  _draw: function() {
    var data=this._data,cv=this._canvas,ctx=cv.getContext('2d');var lay=this._layout();
    var W=lay.W,H=lay.H,P=lay.P,CW=lay.CW,CH=lay.CH;var cc=_cc();ctx.clearRect(0,0,W,H);
    if(!data.length){ctx.fillStyle=cc.noData;ctx.font='14px sans-serif';ctx.textAlign='center';ctx.fillText(_t('No data for this selection'),W/2,H/2);return;}
    var maxFps=0,minFps=Infinity;
    data.forEach(function(d){SIZE_KEYS.forEach(function(sz){if(d.sizes[sz]!=null){maxFps=Math.max(maxFps,d.sizes[sz]);minFps=Math.min(minFps,d.sizes[sz]);}});});
    if(minFps===Infinity)minFps=0;
    var range=maxFps-minFps;
    var floor=Math.max(0,Math.floor((minFps-range*0.3)/10)*10);
    if(range<maxFps*0.15)floor=Math.max(0,Math.floor(minFps*0.7/10)*10);
    var fpsCeil=this._niceMax((maxFps-floor)*1.2)+floor;
    var n=data.length;var gW=CW/n;var barAreaW=gW*0.82;var subW=barAreaW/SIZE_KEYS.length;var padLeft=(gW-barAreaW)/2;var self=this;
    var fpsY=function(v){return P.top+CH-((v-floor)/(fpsCeil-floor))*CH;};
    var gX=function(i,si){return P.left+i*gW+padLeft+si*subW;};
    var midX=function(i){return P.left+i*gW+gW/2;};
    var capMap={};
    _history('e2e_multi_capacity').forEach(function(r){
      if(r.use_ort!==state.fpsOrt)return;if((r.task||'')!==state.fpsTask)return;
      if(r.run_id!==_getSelectedRunId(r.env_id))return;
      var sz=r.size||modelSizeChar(r.model);
      var k=r.env_id+'|'+sz;
      if(!capMap[k]||r.capacity_streams>capMap[k])capMap[k]=r.capacity_streams;
    });
    /* Grid */ctx.strokeStyle=cc.grid;ctx.lineWidth=1;for(var g=0;g<=5;g++){var gy=P.top+CH*g/5;ctx.beginPath();ctx.moveTo(P.left,gy);ctx.lineTo(P.left+CW,gy);ctx.stroke();}
    /* Axes */ctx.strokeStyle=cc.axes;ctx.lineWidth=1.5;[[P.left,P.top,P.left,P.top+CH],[P.left,P.top+CH,P.left+CW,P.top+CH]].forEach(function(l){ctx.beginPath();ctx.moveTo(l[0],l[1]);ctx.lineTo(l[2],l[3]);ctx.stroke();});
    /* Y ticks */ctx.textAlign='right';ctx.fillStyle=cc.dim;ctx.font='11px sans-serif';
    for(var t=0;t<=5;t++){var tv=fpsCeil-(fpsCeil-floor)*t/5,ty=P.top+CH*t/5;ctx.fillText(Math.round(tv),P.left-6,ty+4);}
    /* Y title */ctx.save();ctx.fillStyle=cc.text;ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.translate(14,P.top+CH/2);ctx.rotate(-Math.PI/2);ctx.fillText('E2E FPS',0,0);ctx.restore();
    data.forEach(function(d,i){
      var sel=d.envId===self._selectedId;var hi=sel||i===self._hoverIdx;
      SIZE_KEYS.forEach(function(sz,si){
        var v=d.sizes[sz];if(v==null)return;
        var bx=gX(i,si),by=fpsY(v),bh=P.top+CH-by;var sc=SIZE_COLORS[sz];
        var barFill=sel?sc.hi:(self._selectedId&&!sel?sc.dim:(hi?sc.hi:sc.fill));
        ctx.fillStyle=barFill;ctx.fillRect(bx+1,by,subW-2,bh);
        ctx.strokeStyle=sc.line;ctx.lineWidth=sel?2:1;ctx.strokeRect(bx+1,by,subW-2,bh);
        ctx.fillStyle=sc.line;ctx.font='bold 9px sans-serif';ctx.textAlign='center';ctx.fillText(Math.round(v),bx+subW/2,by-4);
        var capKey=d.envId+'|'+sz;var cap=capMap[capKey];
        if(cap!=null){
          var bt=cap+'ch';ctx.font='bold 8px sans-serif';var btw=ctx.measureText(bt).width;
          var bcx=bx+subW/2,bcy=by-18;var bpx=3,bpy=1,brr=3;
          var brx=bcx-btw/2-bpx,bry=bcy-6-bpy;var brw=btw+bpx*2,brh=10+bpy*2;
          ctx.fillStyle='rgba(136,84,208,0.12)';ctx.beginPath();
          ctx.moveTo(brx+brr,bry);ctx.lineTo(brx+brw-brr,bry);ctx.quadraticCurveTo(brx+brw,bry,brx+brw,bry+brr);ctx.lineTo(brx+brw,bry+brh-brr);ctx.quadraticCurveTo(brx+brw,bry+brh,brx+brw-brr,bry+brh);ctx.lineTo(brx+brr,bry+brh);ctx.quadraticCurveTo(brx,bry+brh,brx,bry+brh-brr);ctx.lineTo(brx,bry+brr);ctx.quadraticCurveTo(brx,bry,brx+brr,bry);ctx.closePath();ctx.fill();
          ctx.strokeStyle='rgb(136,84,208)';ctx.lineWidth=0.8;ctx.stroke();
          ctx.fillStyle='rgb(136,84,208)';ctx.textAlign='center';ctx.fillText(bt,bcx,bcy);
        }
      });
      if(sel){ctx.save();ctx.strokeStyle=cc.selBdr;ctx.lineWidth=3;ctx.setLineDash([6,3]);var sx=P.left+i*gW+2;ctx.strokeRect(sx,P.top-2,gW-4,CH+4);ctx.setLineDash([]);ctx.restore();}
    });
    /* X labels */ctx.fillStyle=cc.text;data.forEach(function(d,i){var parts=d.label.split('\n'),lx=midX(i);parts.forEach(function(part,pi){ctx.font=pi===0?'600 11px sans-serif':'11px sans-serif';ctx.textAlign='center';ctx.fillText(part,lx,P.top+CH+16+pi*14);});});
    var lx=P.left,ly=22;
    SIZE_KEYS.forEach(function(sz){var sc=SIZE_COLORS[sz];ctx.fillStyle=sc.fill;ctx.fillRect(lx,ly-7,18,14);ctx.strokeStyle=sc.line;ctx.lineWidth=1;ctx.strokeRect(lx,ly-7,18,14);var label=sz.toUpperCase()+' ('+SIZE_LABELS[sz]+')';ctx.fillStyle=cc.text;ctx.font='12px sans-serif';ctx.textAlign='left';ctx.fillText(label,lx+22,ly+4);lx+=ctx.measureText(label).width+40;});
    ctx.fillStyle='rgba(136,84,208,0.12)';ctx.fillRect(lx,ly-7,18,14);ctx.strokeStyle='rgb(136,84,208)';ctx.lineWidth=1;ctx.strokeRect(lx,ly-7,18,14);ctx.fillStyle='rgb(136,84,208)';ctx.font='bold 8px sans-serif';ctx.textAlign='center';ctx.fillText('ch',lx+9,ly+3);ctx.fillStyle=cc.text;ctx.font='12px sans-serif';ctx.textAlign='left';ctx.fillText('Max Ch (\u2265 30fps)',lx+22,ly+4);
  },
  _hitTest: function(e){var rect=this._canvas.getBoundingClientRect();var x=e.clientX-rect.left;var lay=this._layout();if(x<lay.P.left||x>lay.P.left+lay.CW||!this._data.length)return -1;return Math.min(Math.floor((x-lay.P.left)/(lay.CW/this._data.length)),this._data.length-1);},
  _handleClick: function(e){var i=this._hitTest(e);if(i>=0&&this._onClick)this._onClick(i,this._data[i]);},
  _handleHover: function(e){scheduleBenchmarkHover(this,e);},
  _handleLeave: function(){this._pendingHoverEvent=null;if(this._hoverRaf){cancelAnimationFrame(this._hoverRaf);this._hoverRaf=null;}this._hoverIdx=-1;this._canvas.style.cursor='default';this._scheduleDraw();},
};

function getChartData() {
  var sz=state.size;var task=state.task;var useOrt=state.ort;var results=[];
  var modelRows=_history('model');var e2eRows=_history('e2e_single');var capRows=_history('e2e_multi_capacity');
  (state.dataset.environments||[]).forEach(function(env){
    var eid=env.env_id;var runId=_getSelectedRunId(eid);
    var tRow=modelRows.find(function(r){return r.env_id===eid&&r.run_id===runId&&r.size===sz&&r.task===task&&r.use_ort===useOrt&&r.family==='throughput';});
    var lRow=modelRows.find(function(r){return r.env_id===eid&&r.run_id===runId&&r.size===sz&&r.task===task&&r.use_ort===useOrt&&r.family==='latency';});
    var eRow=e2eRows.find(function(r){return r.env_id===eid&&r.run_id===runId&&r.size===sz&&r.task===task&&r.use_ort===useOrt;});
    var cRow=capRows.find(function(r){return r.env_id===eid&&r.run_id===runId&&r.size===sz&&r.task===task&&r.use_ort===useOrt;});
    if(tRow||eRow){results.push({env:env,envId:eid,label:envLabel(env),throughput:tRow?tRow.fps:null,e2eFps:eRow?eRow.avg_e2e_fps:null,latency:lRow?lRow.latency_ms:null,maxChannels:cRow?cRow.capacity_streams:null});}
  });
  results.sort(function(a,b){return(a.e2eFps||0)-(b.e2eFps||0);});return results;
}
function refreshChart(preferredEnvId) {
  var data=getChartData();state.chartData=data;
  var model=getModelName(state.task,state.size);
  document.getElementById('chartSubtitle').textContent=TASK_MAP[state.task].label+'  \u00b7  '+model+'  \u00b7  ORT '+(state.ort?'ON':'OFF');
  if(!data.length){
    state.selectedEnvId=null;
    document.getElementById('envDetail').style.display='none';
    document.getElementById('overviewModelMetaPanel').style.display='none';
    Chart.update(data,null);
    dispatchBenchmarkHelpSync();
    return;
  }
  var selected=data[0];
  if(preferredEnvId){for(var i=0;i<data.length;i++){if(data[i].envId===preferredEnvId){selected=data[i];break;}}}
  state.selectedEnvId=selected.envId;renderEnvDetail(selected.env,{scroll:false});
  Chart.update(data,state.selectedEnvId);
}
function getFpsCompareData() {
  var useOrt=state.fpsOrt;var task=state.fpsTask;var results=[];var e2eRows=_history('e2e_single');
  (state.dataset.environments||[]).forEach(function(env){
    var eid=env.env_id;var runId=_getSelectedRunId(eid);var sizes={};var hasAny=false;
    SIZE_KEYS.forEach(function(sz){var eRow=e2eRows.find(function(r){return r.env_id===eid&&r.run_id===runId&&r.size===sz&&r.task===task&&r.use_ort===useOrt;});if(eRow){sizes[sz]=eRow.avg_e2e_fps;hasAny=true;}else{sizes[sz]=null;}});
    if(hasAny){results.push({env:env,envId:eid,label:envLabel(env),sizes:sizes});}
  });
  results.sort(function(a,b){var sum=function(d){var s=0;SIZE_KEYS.forEach(function(sz){if(d.sizes[sz]!=null)s+=d.sizes[sz];});return s;};return sum(a)-sum(b);});return results;
}
function refreshFpsCompare(preferredEnvId) {
  var data=getFpsCompareData();state.fpsChartData=data;
  document.getElementById('fpsChartSubtitle').textContent=TASK_MAP[state.fpsTask].label+'  \u00b7  ORT '+(state.fpsOrt?'ON':'OFF')+'  \u00b7  All Sizes (N / S / M / L / X)';
  if(!data.length){
    state.fpsSelectedEnvId=null;
    document.getElementById('fpsEnvDetail').style.display='none';
    document.getElementById('fpsModelMetaPanel').style.display='none';
    document.getElementById('fpsE2eTableSection').style.display='none';
    FpsChart.update(data,null);
    dispatchBenchmarkHelpSync();
    return;
  }
  var selected=data[0];var idx=0;
  if(preferredEnvId){for(var i=0;i<data.length;i++){if(data[i].envId===preferredEnvId){selected=data[i];idx=i;break;}}}
  handleFpsEnvClick(idx,selected,{scroll:false});
}

function handleFpsEnvClick(idx,d,options) {
  options=options||{};
  state.fpsSelectedEnvId=d.envId;
  var panel=document.getElementById('fpsEnvDetail');panel.style.display='';
  document.getElementById('fpsEnvDetailTitle').textContent=d.env.hostname+' ('+(_envProductLabel(d.env)||'?')+')';
  renderHostInfo(document.getElementById('fpsEnvHostInfo'),d.env);
  renderNpuInfo(document.getElementById('fpsEnvNpuInfo'),d.env);
  renderToolsInfo(document.getElementById('fpsEnvToolsInfo'),d.env);
  var metaPanel=document.getElementById('fpsModelMetaPanel');metaPanel.style.display='';
  document.getElementById('fpsModelMetaTitle').textContent='Benchmarked Models – '+TASK_MAP[state.fpsTask].label;
  renderModelMetaForTask(document.getElementById('fpsModelMetaSection'),d.env,state.fpsTask);
  var e2eSection=document.getElementById('fpsE2eTableSection');e2eSection.style.display='';
  var runId=_getSelectedRunId(d.envId);
  document.getElementById('fpsE2eTableTitle').textContent=_t('E2E Pipeline (Single-Stream)') +' \u2013 '+TASK_MAP[state.fpsTask].label+' \u00b7 ORT '+(state.fpsOrt?'ON':'OFF')+' \u00b7 '+runId;
  renderE2eTable(document.getElementById('fpsE2eTableContent'),d.envId,state.fpsTask,state.fpsOrt,runId);
  /* View trend link */
  var hwId=_envToHwId(d.env);
  if(hwId&&_hwIdHasSnapshots(hwId)){
    var link=document.createElement('p');link.className='trend-link';link.innerHTML='<a href="#" id="fpsTrendLink">\u2192 ' + _t('View version trend for this environment') + '</a>';
    document.getElementById('fpsE2eTableContent').appendChild(link);
    document.getElementById('fpsTrendLink').addEventListener('click',function(e){e.preventDefault();_switchToTrend(hwId);});
  }
  if(options.scroll!==false){panel.scrollIntoView({behavior:'smooth',block:'nearest'});}
  FpsChart.update(state.fpsChartData,state.fpsSelectedEnvId);
  var fpsPanel = document.getElementById('fpsEnvDetail');
  var fpsEgOrt = state.fpsOrt !== undefined ? state.fpsOrt : true;
  _appendEdgeGuideLink(fpsPanel, { task: state.fpsTask, size: state.size || 'n', ort: fpsEgOrt });
  dispatchBenchmarkHelpSync();
}

function initFpsFilters() {
  document.getElementById('fpsTaskFilter').value=state.fpsTask;
  document.getElementById('fpsOrtFilter').value=state.fpsOrt?'on':'off';
  document.getElementById('fpsTaskFilter').addEventListener('change',function(){state.fpsTask=this.value;refreshFpsCompare();});
  document.getElementById('fpsOrtFilter').addEventListener('change',function(){state.fpsOrt=this.value==='on';refreshFpsCompare();});
}

function renderEnvDetail(env,options) {
  options=options||{};
  var panel=document.getElementById('envDetail');panel.style.display='';
  document.getElementById('envDetailTitle').textContent=env.hostname+' ('+(_envProductLabel(env)||'?')+')';
  renderHostInfo(document.getElementById('envHostInfo'),env);
  renderNpuInfo(document.getElementById('envNpuInfo'),env);
  renderToolsInfo(document.getElementById('envToolsInfo'),env);
  var metaPanel=document.getElementById('overviewModelMetaPanel');metaPanel.style.display='';
  document.getElementById('overviewModelMetaTitle').textContent='Benchmarked Models – '+TASK_MAP[state.task].label;
  renderModelMetaForTask(document.getElementById('overviewModelMetaSection'),env,state.task);
  /* View trend link */
  var hwId=_envToHwId(env);
  if(hwId&&_hwIdHasSnapshots(hwId)){
    var link=document.createElement('p');link.className='trend-link';link.innerHTML='<a href="#" id="overviewTrendLink">\u2192 ' + _t('View version trend for this environment') + '</a>';
    document.getElementById('overviewModelMetaSection').appendChild(link);
    document.getElementById('overviewTrendLink').addEventListener('click',function(e){e.preventDefault();_switchToTrend(hwId);});
  }
  if(options.scroll!==false)panel.scrollIntoView({behavior:'smooth',block:'nearest'});
  var egOrt = state.ort !== undefined ? state.ort : true;
  _appendEdgeGuideLink(panel, { task: state.task, size: state.size, ort: egOrt });
  dispatchBenchmarkHelpSync();
}

function initTabs() {
  document.querySelectorAll('.dashboard-tab').forEach(function(btn){
    btn.addEventListener('click',function(){
      var target=this.dataset.tab;
      document.querySelectorAll('.dashboard-tab').forEach(function(b){b.classList.remove('active');});
      document.querySelectorAll('.tab-content').forEach(function(c){c.classList.remove('active');});
      this.classList.add('active');document.getElementById('tab-'+target).classList.add('active');
      if(target==='fps-compare')FpsChart._resize();
      if(target==='overview')Chart._resize();
      if(target==='detail')renderDetailTables();
      if(target==='version-trend')resizeTrendChart();
      if(target==='ort-compare')OrtChart._resize();
      dispatchBenchmarkHelpSync();
    });
  });
}

function initOverviewFilters() {
  document.getElementById('taskFilter').value=state.task;
  document.getElementById('sizeFilter').value=state.size;
  document.getElementById('ortFilter').value=state.ort?'on':'off';
  document.getElementById('taskFilter').addEventListener('change',function(){state.task=this.value;refreshChart();});
  document.getElementById('sizeFilter').addEventListener('change',function(){state.size=this.value;refreshChart();});
  document.getElementById('ortFilter').addEventListener('change',function(){state.ort=this.value==='on';refreshChart();});
}

function initDetailTab() {
  var sel=document.getElementById('detailEnvFilter');
  var runSel=document.getElementById('detailRunFilter');
  sel.innerHTML=(state.dataset.environments||[]).map(function(e){return '<option value="'+e.env_id+'">'+escHtml(e.hostname)+' ('+escHtml(_envProductLabel(e)||'?')+')</option>';}).join('');
  if(state.dataset.environments.length){state.detailEnvId=state.dataset.environments[0].env_id;sel.value=state.detailEnvId;}
  syncDetailRunFilter();
  sel.addEventListener('change',function(){state.detailEnvId=this.value;syncDetailRunFilter();renderDetailTables();});
  runSel.addEventListener('change',function(){if(state.detailEnvId)_handleRunSelectionChange(state.detailEnvId,this.value);});
  document.getElementById('detailTaskFilter').addEventListener('change',function(){state.detailTask=this.value;renderDetailTables();});
  document.getElementById('detailOrtFilter').addEventListener('change',function(){state.detailOrt=this.value;renderDetailTables();});
}

function renderDetailTables() {
  var target=document.getElementById('detailTables');var envId=state.detailEnvId;
  if(!envId){target.innerHTML='<div class="empty-state">' + _t('No environment selected.') + '</div>';dispatchBenchmarkHelpSync();return;}
  var runId=_getSelectedRunId(envId);
  var latMap={},tpMap={},e2eMap={},capMap={},taskModels={},thermMap={},statusMap={},capStatusMap={};
  _history('model').forEach(function(r){if(r.env_id!==envId||r.run_id!==runId)return;var k=r.model+'|'+(r.use_ort?'on':'off');if(r.family==='latency')latMap[k]=r.latency_ms;if(r.family==='throughput')tpMap[k]=r.fps;if(!taskModels[r.task])taskModels[r.task]={};taskModels[r.task][r.model]=true;var th=thermMap[k]||{tMin:null,tMax:null,cMin:null,cMax:null,throttled:false};if(r.npu_temp_min_c!=null)th.tMin=(th.tMin==null)?r.npu_temp_min_c:Math.min(th.tMin,r.npu_temp_min_c);if(r.npu_temp_max_c!=null)th.tMax=(th.tMax==null)?r.npu_temp_max_c:Math.max(th.tMax,r.npu_temp_max_c);if(r.npu_clock_mhz_min!=null)th.cMin=(th.cMin==null)?r.npu_clock_mhz_min:Math.min(th.cMin,r.npu_clock_mhz_min);if(r.npu_clock_mhz_max!=null)th.cMax=(th.cMax==null)?r.npu_clock_mhz_max:Math.max(th.cMax,r.npu_clock_mhz_max);if(r.npu_throttled)th.throttled=true;thermMap[k]=th;var stm=statusMap[k]||{};if(r.family==='latency')stm.lat=r.status;if(r.family==='throughput')stm.tp=r.status;statusMap[k]=stm;});
  _history('e2e_single').forEach(function(r){if(r.env_id!==envId||r.run_id!==runId)return;e2eMap[r.model+'|'+(r.use_ort?'on':'off')]=r;if(!taskModels[r.task])taskModels[r.task]={};taskModels[r.task][r.model]=true;});
  _history('e2e_multi_capacity').forEach(function(r){if(r.env_id!==envId||r.run_id!==runId)return;var k=r.model+'|'+(r.use_ort?'on':'off');capMap[k]=r.capacity_streams;capStatusMap[k]=r.status;if(!taskModels[r.task])taskModels[r.task]={};taskModels[r.task][r.model]=true;});
  var tasks=Object.keys(taskModels).sort(function(a,b){var oa=TASK_ORDER[a],ob=TASK_ORDER[b];return(oa!==undefined?oa:99)-(ob!==undefined?ob:99);});
  if(state.detailTask!=='all')tasks=tasks.filter(function(t){return t===state.detailTask;});
  if(!tasks.length){target.innerHTML='<div class="empty-state">' + _t('No data.') + '</div>';dispatchBenchmarkHelpSync();return;}
  target.innerHTML=tasks.map(function(task){
    var models=Object.keys(taskModels[task]).sort(function(a,b){var d=sizeOrd(modelSizeChar(a))-sizeOrd(modelSizeChar(b));return d!==0?d:a.localeCompare(b);});
    var body=models.map(function(model){var ortRows=[true,false].filter(function(useOrt){return state.detailOrt==='all'||state.detailOrt===(useOrt?'on':'off');});var fpsOn=null,fpsOff=null,capOn=null,capOff=null;ortRows.forEach(function(useOrt){var k=model+'|'+(useOrt?'on':'off');var e2e=e2eMap[k]||{};if(useOrt){fpsOn=e2e.avg_e2e_fps!=null?Number(e2e.avg_e2e_fps):null;capOn=capMap[k]!=null?Number(capMap[k]):null;}else{fpsOff=e2e.avg_e2e_fps!=null?Number(e2e.avg_e2e_fps):null;capOff=capMap[k]!=null?Number(capMap[k]):null;}});var bestFpsOrt=null,bestCapOrt=null;if(fpsOn!=null&&fpsOff!=null){bestFpsOrt=fpsOn>=fpsOff?'on':'off';}else if(fpsOn!=null){bestFpsOrt='on';}else if(fpsOff!=null){bestFpsOrt='off';}if(capOn!=null&&capOff!=null){bestCapOrt=capOn>=capOff?'on':'off';}else if(capOn!=null){bestCapOrt='on';}else if(capOff!=null){bestCapOrt='off';}var sz=modelSizeChar(model);var szLabel=sz?sz.toUpperCase():'-';return ortRows.map(function(useOrt){var k=model+'|'+(useOrt?'on':'off');var e2e=e2eMap[k]||{};var ortKey=useOrt?'on':'off';var fpsVal=fmt(e2e.avg_e2e_fps,1);var capVal=capMap[k]!=null?capMap[k]:null;var fpsTd=bestFpsOrt===ortKey?'<td class="cell-best">'+fpsVal+'</td>':'<td>'+fpsVal+'</td>';var capTd=bestCapOrt===ortKey?'<td class="cell-best">'+(capVal!=null?capVal:'-')+'</td>':'<td>'+(capVal!=null?capVal:'-')+'</td>';var th=thermMap[k]||{};var tempS=_fmtTemp(th.tMin,th.tMax);var clkS=_fmtClock(th.cMin,th.cMax);var tempTd='<td>'+tempS+(th.throttled?' <span class="tag tag--warn" title="'+_t('NPU thermal throttling detected')+'">'+_t('Throttled')+'</span>':'')+'</td>';var conds=[];var stm=statusMap[k]||{};if(stm.lat&&stm.lat!=='ok')conds.push({metric:_t('Latency (ms)'),status:stm.lat});if(stm.tp&&stm.tp!=='ok')conds.push({metric:_t('Throughput'),status:stm.tp});var e2eRow=e2eMap[k];if(e2eRow&&e2eRow.status&&e2eRow.status!=='ok')conds.push({metric:_t('E2E FPS'),status:e2eRow.status,extra:(e2eRow.runs!=null&&e2eRow.requested_runs!=null)?(e2eRow.runs+'/'+e2eRow.requested_runs+' '+_t('runs completed')):null});var capSt=capStatusMap[k];if(capSt&&capSt!=='ok')conds.push({metric:_t('Max Channels'),status:capSt});var statusTd='<td>-</td>';if(conds.length){var worst=conds[0];conds.forEach(function(c){if(_statusSeverity(c.status)>_statusSeverity(worst.status))worst=c;});var title=conds.map(function(c){return c.metric+': '+_t(_statusLabel(c.status))+(c.extra?' ('+c.extra+')':'');}).join('; ');statusTd='<td>'+_statusBadge(worst.status,title)+'</td>';}return '<tr><td>'+escHtml(model)+'</td><td>'+szLabel+'</td><td>'+(useOrt?'ON':'OFF')+'</td><td>'+fmt(latMap[k],2)+'</td><td>'+fmt(tpMap[k],1)+'</td>'+fpsTd+capTd+tempTd+'<td>'+clkS+'</td>'+statusTd+'</tr>';}).join('');}).join('');
    return '<section class="task-section"><h3>'+(TASK_MAP[task]?TASK_MAP[task].label:task)+'</h3><table class="summary-table detail-table"><colgroup><col style="width:20%"><col style="width:5%"><col style="width:5%"><col style="width:11%"><col style="width:12%"><col style="width:10%"><col style="width:11%"><col style="width:9%"><col style="width:9%"><col style="width:8%"></colgroup><thead><tr><th>' + _t('Model') + '</th><th>' + _t('Size') + '</th><th>ORT</th><th>' + _t('Latency (ms)') + '</th><th>' + _t('Throughput') + ' (FPS)</th><th>' + _t('E2E FPS') + '</th><th>' + _t('Max Channels') + '</th><th>' + _t('NPU Temp (°C)') + '</th><th>' + _t('NPU Clock (MHz)') + '</th><th>' + _t('Status') + '</th></tr></thead><tbody>'+body+'</tbody></table></section>';
  }).join('');
  dispatchBenchmarkHelpSync();
}

function renderMeta() {
  var m=state.dataset.meta||{};
  document.getElementById('meta').innerHTML=
    '<div><strong>' + _t('Environments') + '</strong><span>'+(m.environment_count||0)+'</span></div>'+
    '<div><strong>' + _t('Generated') + '</strong><span>'+(m.generated_at?new Date(m.generated_at).toLocaleDateString():'-')+'</span></div>';
}

function _envToHwId(env){
  if(!env)return null;
  if(env.hw_id)return env.hw_id;
  var h=env.hostname||'unknown',s=_envProductLabel(env)||'unknown';
  return (h+'_'+s).replace(/[^A-Za-z0-9_.\-]/g,'_').replace(/_+/g,'_').replace(/^_|_$/g,'');
}
function _hwIdHasSnapshots(hwId){
  var snaps=state.dataset.snapshots||[];
  for(var i=0;i<snaps.length;i++){if(snaps[i].hw_id===hwId)return true;}
  return false;
}
function _getUniqueHwIds(){
  var snaps=state.dataset.snapshots||[];
  var seen={},ids=[];
  snaps.forEach(function(s){if(!seen[s.hw_id]){seen[s.hw_id]=true;ids.push(s.hw_id);}});
  return ids;
}
/* dx-all-suite version ordering: numeric-ish (v2.3.3 < v2.4.0), 'unknown' bucket always sorts last. */
function _compareVersions(a,b){
  a=a==null?'unknown':String(a);b=b==null?'unknown':String(b);
  if(a==='unknown'&&b==='unknown')return 0;
  if(a==='unknown')return 1;
  if(b==='unknown')return -1;
  var pa=a.replace(/^v/i,'').split('.').map(Number);
  var pb=b.replace(/^v/i,'').split('.').map(Number);
  for(var i=0;i<Math.max(pa.length,pb.length);i++){
    var xa=pa[i]||0,xb=pb[i]||0;
    if(xa!==xb)return xa-xb;
  }
  return 0;
}
/* Distinct dx_all_suite_version values across this HW's snapshots, oldest-to-newest ('unknown' last). */
function _getAvailableVersions(hwId){
  var snaps=(state.dataset.snapshots||[]).filter(function(s){return s.hw_id===hwId;});
  var seen={},vers=[];
  snaps.forEach(function(s){var v=envVersion(s.environment);if(!seen[v]){seen[v]=true;vers.push(v);}});
  vers.sort(_compareVersions);
  return vers;
}
function _resetTrendVersionFilter(hwId){
  var vers=_getAvailableVersions(hwId);
  var filter={};
  vers.forEach(function(v){filter[v]=true;});
  state.trendVersions=vers;
  state.trendVersionFilter=filter;
}
function renderTrendVersionFilter(){
  var container=document.getElementById('trendVersionFilter');if(!container)return;
  var vers=state.trendVersions||[];
  if(!vers.length){container.innerHTML='<p class="empty-state small">' + _t('No version data available.') + '</p>';return;}
  container.innerHTML=vers.map(function(v){
    var checked=state.trendVersionFilter[v]?' checked':'';
    var label=v==='unknown'?_t('unknown'):v;
    return '<label class="version-chip"><input type="checkbox" data-version="'+escHtml(v)+'"'+checked+'> '+escHtml(label)+'</label>';
  }).join('');
  container.querySelectorAll('input[data-version]').forEach(function(cb){
    cb.addEventListener('change',function(){
      state.trendVersionFilter[this.dataset.version]=this.checked;
      refreshTrend();
    });
  });
}
function _switchToTrend(hwId){
  document.querySelectorAll('.dashboard-tab').forEach(function(b){b.classList.remove('active');});
  document.querySelectorAll('.tab-content').forEach(function(c){c.classList.remove('active');});
  document.querySelector('[data-tab="version-trend"]').classList.add('active');
  document.getElementById('tab-version-trend').classList.add('active');
  var sel=document.getElementById('trendEnvFilter');
  sel.value=hwId;state.trendHwId=hwId;
  _resetTrendVersionFilter(hwId);renderTrendVersionFilter();
  refreshTrend();resizeTrendChart();
  dispatchBenchmarkHelpSync();
}

function _trendMetricByKey(metricKey){return TREND_METRICS.find(function(metric){return metric.key===metricKey;})||TREND_METRICS[0];}
function _formatTrendValue(metric,value){
  if(value==null)return '-';
  if(metric.precision===0)return String(Math.round(Number(value)));
  return Number(value).toFixed(metric.precision);
}
function _latestTrendPointIndex(data){
  return (data.length&&data[0].points&&data[0].points.length)?(data[0].points.length-1):-1;
}
function _snapshotMetricValue(snap,task,useOrt,metric,sizeKey){
  var rows=(snap.results&&snap.results[metric.resultKind])||[];
  var row=rows.find(function(candidate){
    if(candidate.size!==sizeKey||candidate.use_ort!==useOrt)return false;
    if(candidate.task!==task)return false;
    if(metric.family)return candidate.family===metric.family;
    return true;
  });
  if(!row)return null;
  return row[metric.valueKey];
}
function createTrendChart(canvas,onClick){
  var chart={_canvas:canvas,_metric:TREND_METRICS[0],_onClick:onClick,_hoverIdx:-1,_data:[],_selectedIdx:-1,_raf:null,_ro:null};
  chart.setMetric=function(metric){this._metric=metric||TREND_METRICS[0];this._scheduleDraw();};
  chart.update=function(data,selectedIdx){this._data=data;this._selectedIdx=selectedIdx;this._scheduleDraw();};
  chart._resize=function(){var el=this._canvas.parentElement,dpr=window.devicePixelRatio||1;var w=el.clientWidth,h=el.clientHeight;setBenchmarkCanvasSize(this._canvas,w,h,dpr);this._canvas.getContext('2d').setTransform(dpr,0,0,dpr,0,0);this._scheduleDraw();};
  chart._scheduleDraw=function(){var s=this;if(s._raf)cancelAnimationFrame(s._raf);s._raf=requestAnimationFrame(function(){s._draw();});};
  chart._layout=function(){var dpr=window.devicePixelRatio||1;var W=this._canvas.width/dpr,H=this._canvas.height/dpr;var P={top:55,right:30,bottom:80,left:72};return{W:W,H:H,P:P,CW:W-P.left-P.right,CH:H-P.top-P.bottom};};
  chart._niceMax=function(v){if(v<=0)return 10;var e=Math.pow(10,Math.floor(Math.log10(v)));var f=v/e;return(f<=2?2:f<=5?5:10)*e;};
  chart._draw=function(){
    var data=this._data,cv=this._canvas,ctx=cv.getContext('2d');
    var lay=this._layout();var W=lay.W,H=lay.H,P=lay.P,CW=lay.CW,CH=lay.CH;var cc=_cc();
    ctx.clearRect(0,0,W,H);
    if(!data.length||!data[0].points||!data[0].points.length){ctx.fillStyle=cc.noData;ctx.font='14px sans-serif';ctx.textAlign='center';ctx.fillText((state.dataset.snapshots||[]).length?('No trend data for '+this._metric.metricLabel.toLowerCase()+' with this selection'):'No snapshot history available. Build the dashboard from nested results/{hw_id}/{run_id} data to see version trend.',W/2,H/2);return;}
    var nPts=data[0].points.length;var maxVal=0,minVal=Infinity;
    data.forEach(function(line){line.points.forEach(function(point){if(point.value!=null){maxVal=Math.max(maxVal,point.value);minVal=Math.min(minVal,point.value);}});});
    if(minVal===Infinity)minVal=0;
    var range=maxVal-minVal;var pad=Math.max(range*0.2,maxVal*0.02,1);var rawFloor=minVal-pad;var rawCeil=maxVal+pad;var ystep=(rawCeil-rawFloor)/5;var ymag=Math.pow(10,Math.floor(Math.log10(Math.max(ystep,1e-9))));var ynorm=ystep/ymag;var niceStep=(ynorm<=1?1:ynorm<=2?2:ynorm<=5?5:10)*ymag;var floor=Math.max(0,Math.floor(rawFloor/niceStep)*niceStep);var ceil=Math.ceil(rawCeil/niceStep)*niceStep;if(ceil<=floor)ceil=floor+niceStep*5;
    var xMargin=nPts<=1?0:Math.max(40,Math.min(CW*0.08,80));var xSpan=CW-2*xMargin;var self=this;var xPos=function(i){return P.left+xMargin+(nPts===1?xSpan/2:i*(xSpan/Math.max(nPts-1,1)));};var yPos=function(v){return P.top+CH-((v-floor)/(ceil-floor||1))*CH;};var hasSelection=self._selectedIdx>=0&&self._selectedIdx<nPts;var groupWidth=nPts===1?Math.min(xSpan*0.6,96):Math.max(36,Math.min(90,(xSpan/Math.max(nPts-1,1))-14));
    ctx.strokeStyle=cc.grid;ctx.lineWidth=1;for(var g=0;g<=5;g++){var gy=P.top+CH*g/5;ctx.beginPath();ctx.moveTo(P.left,gy);ctx.lineTo(P.left+CW,gy);ctx.stroke();}
    ctx.strokeStyle=cc.axes;ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(P.left,P.top);ctx.lineTo(P.left,P.top+CH);ctx.stroke();ctx.beginPath();ctx.moveTo(P.left,P.top+CH);ctx.lineTo(P.left+CW,P.top+CH);ctx.stroke();
    ctx.textAlign='right';ctx.fillStyle=cc.dim;ctx.font='11px sans-serif';for(var t=0;t<=5;t++){var tv=ceil-(ceil-floor)*t/5;ctx.fillText(Math.round(tv),P.left-6,P.top+CH*t/5+4);}ctx.save();ctx.fillStyle=cc.text;ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.translate(14,P.top+CH/2);ctx.rotate(-Math.PI/2);ctx.fillText(this._metric.axisLabel,0,0);ctx.restore();
    if(hasSelection){var selectedX=xPos(self._selectedIdx);var groupLeft=Math.max(P.left,Math.min(selectedX-groupWidth/2,P.left+CW-groupWidth));ctx.save();ctx.fillStyle=cc.sel;ctx.fillRect(groupLeft,P.top-2,groupWidth,CH+4);ctx.strokeStyle=cc.selBdr;ctx.lineWidth=3;ctx.setLineDash([6,3]);ctx.strokeRect(groupLeft,P.top-2,groupWidth,CH+4);ctx.setLineDash([]);ctx.restore();}
    var _labelGap=13;function _spreadLabels(items){items.sort(function(a,b){return a.baseY-b.baseY;});for(var pass=0;pass<4;pass++){for(var j=1;j<items.length;j++){var gap=items[j].y-items[j-1].y;if(gap<_labelGap){var shift=(_labelGap-gap)/2;items[j-1].y-=Math.ceil(shift);items[j].y+=Math.ceil(shift);}}items.sort(function(a,b){return a.y-b.y;});}return items;}
    var colLabels={};data.forEach(function(line,li){line.points.forEach(function(point,i){if(point.value==null)return;if(!colLabels[i])colLabels[i]=[];colLabels[i].push({lineIdx:li,baseY:yPos(point.value)-10,y:yPos(point.value)-10,value:point.value});});});Object.keys(colLabels).forEach(function(k){_spreadLabels(colLabels[k]);});
    data.forEach(function(line,li){var sc=SIZE_COLORS[line.size]||SIZE_COLORS.n;ctx.save();ctx.globalAlpha=hasSelection?0.72:1;ctx.strokeStyle=sc.line;ctx.lineWidth=2.5;ctx.beginPath();var started=false;line.points.forEach(function(point,i){if(point.value==null)return;var x=xPos(i),y=yPos(point.value);if(!started){ctx.moveTo(x,y);started=true;}else{ctx.lineTo(x,y);}});ctx.stroke();ctx.restore();line.points.forEach(function(point,i){if(point.value==null)return;var x=xPos(i),y=yPos(point.value);var isSelectedColumn=i===self._selectedIdx;var isHoveredColumn=i===self._hoverIdx;var r=isSelectedColumn?7:(isHoveredColumn?6:5);ctx.fillStyle=hasSelection?(isSelectedColumn?sc.hi:(isHoveredColumn?sc.fill:sc.dim)):(isHoveredColumn?sc.hi:sc.fill);ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.strokeStyle=sc.line;ctx.lineWidth=isSelectedColumn?3:1.5;ctx.stroke();});});
    /* value labels in a final pass so no other series' line/marker occludes them */
    data.forEach(function(line,li){line.points.forEach(function(point,i){if(point.value==null)return;var x=xPos(i),y=yPos(point.value);var isSelectedColumn=i===self._selectedIdx;var isHoveredColumn=i===self._hoverIdx;var labelY=y-10;var cl=colLabels[i];if(cl){for(var ci=0;ci<cl.length;ci++){if(cl[ci].lineIdx===li){labelY=cl[ci].y;break;}}}var isEmphasized=isSelectedColumn||isHoveredColumn;var labelText=_formatTrendValue(self._metric,point.value);ctx.font=isEmphasized?'bold 11px sans-serif':'10px sans-serif';ctx.textAlign='center';ctx.globalAlpha=hasSelection?(isEmphasized?1:0.7):1;ctx.strokeStyle=cc.outline;ctx.lineWidth=3;ctx.lineJoin='round';ctx.strokeText(labelText,x,labelY);ctx.fillStyle=cc.emph;ctx.fillText(labelText,x,labelY);ctx.globalAlpha=1;});});
    if(data[0]&&data[0].points){data[0].points.forEach(function(point,i){var x=xPos(i);var isSelectedColumn=i===self._selectedIdx;var isHoveredColumn=i===self._hoverIdx;ctx.fillStyle=hasSelection?(isSelectedColumn?cc.text:(isHoveredColumn?cc.dim:'rgba(93,101,114,0.55)')):cc.text;ctx.font=isSelectedColumn?'600 11px sans-serif':'11px sans-serif';ctx.textAlign='center';ctx.fillText(point.dateLabel||'',x,P.top+CH+16);if(point.swLabel){ctx.fillStyle=hasSelection?(isSelectedColumn?cc.noData:'rgba(93,101,114,0.45)'):cc.noData;ctx.font='10px sans-serif';ctx.fillText(point.swLabel,x,P.top+CH+30);}});}
    var lx=P.left,ly=22;SIZE_KEYS.forEach(function(sz){var sc=SIZE_COLORS[sz];ctx.fillStyle=sc.fill;ctx.beginPath();ctx.arc(lx+6,ly,5,0,Math.PI*2);ctx.fill();ctx.strokeStyle=sc.line;ctx.lineWidth=1.5;ctx.stroke();var label=sz.toUpperCase()+' ('+SIZE_LABELS[sz]+')';ctx.fillStyle=cc.text;ctx.font='12px sans-serif';ctx.textAlign='left';ctx.fillText(label,lx+16,ly+4);lx+=ctx.measureText(label).width+35;});
  };
  chart._hitTest=function(e){var rect=this._canvas.getBoundingClientRect();var x=e.clientX-rect.left;var lay=this._layout();var data=this._data;if(!data.length||!data[0].points||!data[0].points.length)return -1;var nPts=data[0].points.length;var xM=nPts<=1?0:Math.max(40,Math.min(lay.CW*0.08,80));var xS=lay.CW-2*xM;if(nPts===1)return Math.abs(x-(lay.P.left+xM+xS/2))<30?0:-1;var step=xS/Math.max(nPts-1,1);var idx=Math.round((x-lay.P.left-xM)/step);if(idx<0||idx>=nPts)return -1;var hitX=lay.P.left+xM+idx*step;return Math.abs(x-hitX)<Math.max(20,step*0.4)?idx:-1;};
  chart._handleClick=function(e){var i=this._hitTest(e);if(i>=0&&this._onClick)this._onClick(i);};
  chart._handleHover=function(e){scheduleBenchmarkHover(this,e);};
  chart._handleLeave=function(){this._pendingHoverEvent=null;if(this._hoverRaf){cancelAnimationFrame(this._hoverRaf);this._hoverRaf=null;}this._hoverIdx=-1;this._canvas.style.cursor='default';this._scheduleDraw();};
  chart._ro=new ResizeObserver(chart._resize.bind(chart));chart._ro.observe(canvas.parentElement);canvas.addEventListener('click',chart._handleClick.bind(chart));canvas.addEventListener('mousemove',chart._handleHover.bind(chart));canvas.addEventListener('mouseleave',chart._handleLeave.bind(chart));chart._resize();
  return chart;
}
function resizeTrendChart(){Object.keys(state.trendCharts).forEach(function(k){state.trendCharts[k]._resize();});}
/* Small-multiples: same x-axis (dx_all_suite_version, oldest\u2192newest) and same run-set for every
   metric panel, so a point index selected on one chart lines up with the same run on all others. */
function getTrendData(hwId,task,useOrt,metricKey){
  var metric=_trendMetricByKey(metricKey);
  var snaps=(state.dataset.snapshots||[]).filter(function(s){
    if(s.hw_id!==hwId)return false;
    var v=envVersion(s.environment);
    if(state.trendVersionFilter&&state.trendVersionFilter[v]===false)return false;
    return true;
  });
  snaps.sort(function(a,b){return _compareVersions(envVersion(a.environment),envVersion(b.environment));});
  if(!snaps.length)return[];
  var lines=SIZE_KEYS.map(function(sz){return{size:sz,points:[]};});
  snaps.forEach(function(snap){
    var ver=envVersion(snap.environment);
    var ts=snap.timestamp?snap.timestamp.substring(0,10):(snap.run_id||'').replace(/(\d{4})(\d{2})(\d{2}).*/,'$1-$2-$3');
    SIZE_KEYS.forEach(function(sz,si){
      var value=_snapshotMetricValue(snap,task,useOrt,metric,sz);
      lines[si].points.push({value:value!=null?Number(value):null,dateLabel:ver,swLabel:ts,run_id:snap.run_id,snap:snap});
    });
  });
  return lines;
}
function hideTrendEnvDetail(){var panel=document.getElementById('trendEnvDetail');if(panel)panel.style.display='none';var metaPanel=document.getElementById('trendModelMetaPanel');if(metaPanel)metaPanel.style.display='none';dispatchBenchmarkHelpSync();}
function renderTrendEnvDetail(snap,options){
  options=options||{};var panel=document.getElementById('trendEnvDetail');if(!panel)return;var env=snap&&snap.environment;if(!env){panel.style.display='none';document.getElementById('trendModelMetaPanel').style.display='none';dispatchBenchmarkHelpSync();return;}panel.style.display='';var dateStr=snap.timestamp?snap.timestamp.substring(0,10):snap.run_id;var ver=envVersion(env);document.getElementById('trendEnvDetailTitle').textContent=(env.hostname||'Environment')+' ('+(_envProductLabel(env)||'?')+') \u00b7 '+ver+' \u00b7 '+dateStr+' \u00b7 '+snap.run_id;renderHostInfo(document.getElementById('trendEnvHostInfo'),env);renderNpuInfo(document.getElementById('trendEnvNpuInfo'),env);renderToolsInfo(document.getElementById('trendEnvToolsInfo'),env);
  var metaPanel=document.getElementById('trendModelMetaPanel');metaPanel.style.display='';document.getElementById('trendModelMetaTitle').textContent='Benchmarked Models \u2013 '+TASK_MAP[state.trendTask].label+' \u00b7 '+snap.run_id;renderModelMetaForTask(document.getElementById('trendModelMetaSection'),env,state.trendTask);
  if(options.scroll!==false)panel.scrollIntoView({behavior:'smooth',block:'nearest'});
  dispatchBenchmarkHelpSync();
}
function refreshTrend(){
  var hwId=state.trendHwId;var task=state.trendTask;var useOrt=state.trendOrt;
  var firstData=null;
  TREND_METRICS.forEach(function(metric){
    var data=getTrendData(hwId,task,useOrt,metric.key);
    state.trendDataByMetric[metric.key]=data;
    if(!firstData&&data.length&&data[0].points.length)firstData=data;
    var ids=_trendPanelIds(metric.key);
    var subtitleEl=document.getElementById(ids.subtitle);
    if(subtitleEl)subtitleEl.textContent=(TASK_MAP[task]?TASK_MAP[task].label:task)+'  \u00b7  ORT '+(useOrt?'ON':'OFF')+'  \u00b7  '+_t('All Sizes (N / S / M / L / X)');
  });
  var selectedIdx=firstData?_latestTrendPointIndex(firstData):-1;
  state.trendSelectedIdx=selectedIdx;
  TREND_METRICS.forEach(function(metric){
    var chart=state.trendCharts[metric.key];if(!chart)return;
    chart.update(state.trendDataByMetric[metric.key]||[],selectedIdx);
  });
  if(selectedIdx>=0){handleTrendPointClick(selectedIdx,{scroll:false});}else{hideTrendEnvDetail();}
}
function handleTrendPointClick(idx,options){
  options=options||{};state.trendSelectedIdx=idx;
  var snap=null;
  TREND_METRICS.some(function(metric){
    var data=state.trendDataByMetric[metric.key];
    if(data&&data.length&&data[0].points[idx]&&data[0].points[idx].snap){snap=data[0].points[idx].snap;return true;}
    return false;
  });
  TREND_METRICS.forEach(function(metric){
    var chart=state.trendCharts[metric.key];if(!chart)return;
    chart.update(state.trendDataByMetric[metric.key]||[],idx);
  });
  if(!snap){hideTrendEnvDetail();return;}
  renderTrendEnvDetail(snap,options);
}
function _trendPanelIds(key){return {canvas:'trendChart_'+key,title:'trendChartTitle_'+key,subtitle:'trendChartSubtitle_'+key};}
function _buildTrendMetricPanelHTML(metric){
  var ids=_trendPanelIds(metric.key);
  return '<section class="panel chart-panel trend-metric-panel" data-metric="'+metric.key+'">'+
      '<div class="chart-header">'+
        '<h2 id="'+ids.title+'">'+escHtml(_t(metric.title))+'</h2>'+
        '<p class="chart-subtitle" id="'+ids.subtitle+'"></p>'+
      '</div>'+
      '<div class="chart-container"><canvas id="'+ids.canvas+'"></canvas></div>'+
    '</section>';
}
function initTrendChart(){
  var grid=document.getElementById('trendChartsGrid');if(!grid)return;
  grid.innerHTML=TREND_METRICS.map(_buildTrendMetricPanelHTML).join('');
  state.trendCharts={};
  TREND_METRICS.forEach(function(metric){
    var ids=_trendPanelIds(metric.key);
    var canvas=document.getElementById(ids.canvas);if(!canvas)return;
    var chart=createTrendChart(canvas,function(idx){handleTrendPointClick(idx);});
    chart.setMetric(metric);
    state.trendCharts[metric.key]=chart;
  });
}
function initTrendTab(){
  var sel=document.getElementById('trendEnvFilter');var hwIds=_getUniqueHwIds();sel.innerHTML=hwIds.map(function(id){return '<option value="'+escHtml(id)+'">'+escHtml(id)+'</option>';}).join('');if(hwIds.length){state.trendHwId=hwIds[0];sel.value=hwIds[0];}state.trendTask='object_detection';state.trendOrt=true;document.getElementById('trendTaskFilter').value=state.trendTask;document.getElementById('trendOrtFilter').value=state.trendOrt?'on':'off';
  _resetTrendVersionFilter(state.trendHwId);renderTrendVersionFilter();
  sel.addEventListener('change',function(){state.trendHwId=this.value;_resetTrendVersionFilter(state.trendHwId);renderTrendVersionFilter();refreshTrend();});
  document.getElementById('trendTaskFilter').addEventListener('change',function(){state.trendTask=this.value;refreshTrend();});
  document.getElementById('trendOrtFilter').addEventListener('change',function(){state.trendOrt=this.value==='on';refreshTrend();});
  document.getElementById('trendVersionAll').addEventListener('click',function(){Object.keys(state.trendVersionFilter).forEach(function(v){state.trendVersionFilter[v]=true;});renderTrendVersionFilter();refreshTrend();});
  document.getElementById('trendVersionNone').addEventListener('click',function(){Object.keys(state.trendVersionFilter).forEach(function(v){state.trendVersionFilter[v]=false;});renderTrendVersionFilter();refreshTrend();});
  refreshTrend();
}

/* ═══ ORT ON/OFF comparison (5b) ═══
   Reads state.dataset.summaries.ort_delta (one row per env_id/task/size/metric,
   already precomputed ON vs OFF for the latest run) — no extra aggregation needed. */
function _ortMetricByKey(key) { return ORT_METRICS.find(function(m) { return m.key === key; }) || ORT_METRICS[0]; }
function _formatOrtValue(metric, v) { if (v == null) return '-'; return metric.precision === 0 ? String(Math.round(v)) : Number(v).toFixed(metric.precision); }
/* true = ORT ON wins this metric, false = OFF wins, null = no meaningful delta */
function _ortOnIsBetter(metric, delta) { if (delta == null || delta === 0) return null; return metric.higherBetter ? delta > 0 : delta < 0; }
function getOrtCompareData(envId, task, metricKey) {
  var rows = _history('ort_delta').filter(function(r) { return r.env_id === envId && r.task === task && r.metric === metricKey; });
  var bySize = {}; rows.forEach(function(r) { bySize[r.size] = r; });
  return SIZE_KEYS.filter(function(sz) { return bySize[sz]; }).map(function(sz) {
    var r = bySize[sz];
    return { size: sz, label: sz.toUpperCase(), on: r.ort_on, off: r.ort_off, delta: r.delta, deltaPct: r.delta_pct };
  });
}

var OrtChart = {
  _canvas: null, _metric: null, _data: [], _raf: null, _ro: null,
  init: function(canvas) {
    this._canvas = canvas;
    this._ro = new ResizeObserver(this._resize.bind(this));
    this._ro.observe(canvas.parentElement); this._resize();
  },
  setMetric: function(metric) { this._metric = metric; this._scheduleDraw(); },
  update: function(data) { this._data = data; this._scheduleDraw(); },
  _resize: function() { var el=this._canvas.parentElement,dpr=window.devicePixelRatio||1;var w=el.clientWidth,h=el.clientHeight;setBenchmarkCanvasSize(this._canvas,w,h,dpr);this._canvas.getContext('2d').setTransform(dpr,0,0,dpr,0,0);this._scheduleDraw(); },
  _scheduleDraw: function() { var s=this;if(s._raf)cancelAnimationFrame(s._raf);s._raf=requestAnimationFrame(function(){s._draw();}); },
  _layout: function() { var dpr=window.devicePixelRatio||1;var W=this._canvas.width/dpr,H=this._canvas.height/dpr;var P={top:60,right:30,bottom:60,left:72};return {W:W,H:H,P:P,CW:W-P.left-P.right,CH:H-P.top-P.bottom}; },
  _niceMax: function(v) { if(v<=0)return 10;var e=Math.pow(10,Math.floor(Math.log10(v)));var f=v/e;return (f<=2?2:f<=5?5:10)*e; },
  _draw: function() {
    var data=this._data,metric=this._metric||ORT_METRICS[0],cv=this._canvas,ctx=cv.getContext('2d');
    var lay=this._layout();var W=lay.W,H=lay.H,P=lay.P,CW=lay.CW,CH=lay.CH;var cc=_cc();
    ctx.clearRect(0,0,W,H);
    if(!data.length){ctx.fillStyle=cc.noData;ctx.font='14px sans-serif';ctx.textAlign='center';ctx.fillText(_t('No data for this selection'),W/2,H/2);return;}
    var maxV=0;data.forEach(function(d){if(d.on!=null)maxV=Math.max(maxV,d.on);if(d.off!=null)maxV=Math.max(maxV,d.off);});
    var ceilV=this._niceMax(maxV*1.25);
    var n=data.length,gW=CW/n,barAreaW=gW*0.6,subW=barAreaW/2,padLeft=(gW-barAreaW)/2;
    var yPos=function(v){return P.top+CH-(v/ceilV)*CH;};
    var gX=function(i,si){return P.left+i*gW+padLeft+si*subW;};
    var midX=function(i){return P.left+i*gW+gW/2;};
    ctx.strokeStyle=cc.grid;ctx.lineWidth=1;for(var g=0;g<=5;g++){var gy=P.top+CH*g/5;ctx.beginPath();ctx.moveTo(P.left,gy);ctx.lineTo(P.left+CW,gy);ctx.stroke();}
    ctx.strokeStyle=cc.axes;ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(P.left,P.top);ctx.lineTo(P.left,P.top+CH);ctx.stroke();ctx.beginPath();ctx.moveTo(P.left,P.top+CH);ctx.lineTo(P.left+CW,P.top+CH);ctx.stroke();
    ctx.textAlign='right';ctx.fillStyle=cc.dim;ctx.font='11px sans-serif';
    for(var t=0;t<=5;t++){var tv=ceilV*(5-t)/5;ctx.fillText(_formatOrtValue(metric,tv),P.left-6,P.top+CH*t/5+4);}
    ctx.save();ctx.fillStyle=cc.text;ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.translate(14,P.top+CH/2);ctx.rotate(-Math.PI/2);ctx.fillText(_t(metric.axisLabel),0,0);ctx.restore();
    data.forEach(function(d,i){
      if(d.on!=null){var bx=gX(i,0),by=yPos(d.on),bh=P.top+CH-by;ctx.fillStyle=ORT_ON_COLOR.fill;ctx.fillRect(bx+1,by,subW-2,bh);ctx.strokeStyle=ORT_ON_COLOR.line;ctx.lineWidth=1;ctx.strokeRect(bx+1,by,subW-2,bh);ctx.fillStyle=ORT_ON_COLOR.line;ctx.font='bold 10px sans-serif';ctx.textAlign='center';ctx.fillText(_formatOrtValue(metric,d.on),bx+1+(subW-2)/2,by-4);}
      if(d.off!=null){var bx2=gX(i,1),by2=yPos(d.off),bh2=P.top+CH-by2;ctx.fillStyle=ORT_OFF_COLOR.fill;ctx.fillRect(bx2+1,by2,subW-2,bh2);ctx.strokeStyle=ORT_OFF_COLOR.line;ctx.lineWidth=1;ctx.strokeRect(bx2+1,by2,subW-2,bh2);ctx.fillStyle=ORT_OFF_COLOR.line;ctx.font='bold 10px sans-serif';ctx.textAlign='center';ctx.fillText(_formatOrtValue(metric,d.off),bx2+1+(subW-2)/2,by2-4);}
      if(d.deltaPct!=null){
        var onBetter=_ortOnIsBetter(metric,d.delta);
        var color=onBetter===true?'rgb(46,204,113)':(onBetter===false?'rgb(231,76,60)':cc.text);
        var topY=Math.min(d.on!=null?yPos(d.on):P.top+CH,d.off!=null?yPos(d.off):P.top+CH)-18;
        ctx.fillStyle=color;ctx.font='bold 10px sans-serif';ctx.textAlign='center';
        var sign=d.deltaPct>0?'+':'';
        ctx.fillText(sign+d.deltaPct.toFixed(1)+'%',midX(i),topY);
      }
    });
    ctx.fillStyle=cc.text;ctx.font='600 11px sans-serif';ctx.textAlign='center';
    data.forEach(function(d,i){ctx.fillText(d.label,midX(i),P.top+CH+18);});
    var lx=P.left,ly=22;
    [{c:ORT_ON_COLOR,label:_t('ORT ON')},{c:ORT_OFF_COLOR,label:_t('ORT OFF')}].forEach(function(it){
      ctx.fillStyle=it.c.fill;ctx.fillRect(lx,ly-7,18,14);ctx.strokeStyle=it.c.line;ctx.lineWidth=1;ctx.strokeRect(lx,ly-7,18,14);
      ctx.fillStyle=cc.text;ctx.font='12px sans-serif';ctx.textAlign='left';ctx.fillText(it.label,lx+24,ly+4);
      lx+=ctx.measureText(it.label).width+44;
    });
  }
};

function renderOrtCompareTable(container,data,metric) {
  if(!container) return;
  if(!data.length){container.innerHTML='<p class="empty-state small">' + _t('No data for this selection') + '</p>';return;}
  var html='<table class="summary-table"><thead><tr><th>' + _t('Size') + '</th><th>' + _t('ORT ON') + '</th><th>' + _t('ORT OFF') + '</th><th>' + _t('Delta') + '</th><th>' + _t('Delta %') + '</th></tr></thead><tbody>';
  data.forEach(function(d){
    var onBetter=_ortOnIsBetter(metric,d.delta);
    var deltaCls=onBetter===true?'ort-delta-pos':(onBetter===false?'ort-delta-neg':'');
    var sign=(d.delta!=null&&d.delta>0)?'+':'';
    var pctSign=(d.deltaPct!=null&&d.deltaPct>0)?'+':'';
    html+='<tr><td>'+escHtml(d.label)+'</td><td>'+_formatOrtValue(metric,d.on)+'</td><td>'+_formatOrtValue(metric,d.off)+'</td>'+
      '<td class="'+deltaCls+'">'+(d.delta!=null?sign+_formatOrtValue(metric,d.delta):'-')+'</td>'+
      '<td class="'+deltaCls+'">'+(d.deltaPct!=null?pctSign+d.deltaPct.toFixed(1)+'%':'-')+'</td></tr>';
  });
  html+='</tbody></table>';
  container.innerHTML=html;
}

function refreshOrtCompare() {
  if(!document.getElementById('ortCompareChart')) return;
  var metric=_ortMetricByKey(state.ortMetric);
  var data=getOrtCompareData(state.ortEnvId,state.ortTask,metric.key);
  state.ortChartData=data;
  var env=_envById(state.ortEnvId);
  var subtitleEl=document.getElementById('ortChartSubtitle');
  if(subtitleEl){
    var envLbl=env?(env.hostname+' ('+(_envProductLabel(env)||'?')+')'):'';
    subtitleEl.textContent=envLbl+'  ·  '+(TASK_MAP[state.ortTask]?TASK_MAP[state.ortTask].label:state.ortTask)+'  ·  '+_t(metric.label);
  }
  OrtChart.setMetric(metric);
  OrtChart.update(data);
  renderOrtCompareTable(document.getElementById('ortCompareTableContent'),data,metric);
  dispatchBenchmarkHelpSync();
}

function initOrtCompareTab() {
  var sel=document.getElementById('ortEnvFilter');if(!sel)return;
  var envs=state.dataset.environments||[];
  sel.innerHTML=envs.map(function(e){return '<option value="'+escHtml(e.env_id)+'">'+escHtml(e.hostname)+' ('+escHtml(_envProductLabel(e)||'?')+')</option>';}).join('');
  if(envs.length){state.ortEnvId=envs[0].env_id;sel.value=state.ortEnvId;}
  document.getElementById('ortTaskFilter').value=state.ortTask;
  document.getElementById('ortMetricFilter').value=state.ortMetric;
  sel.addEventListener('change',function(){state.ortEnvId=this.value;refreshOrtCompare();});
  document.getElementById('ortTaskFilter').addEventListener('change',function(){state.ortTask=this.value;refreshOrtCompare();});
  document.getElementById('ortMetricFilter').addEventListener('change',function(){state.ortMetric=this.value;refreshOrtCompare();});
  OrtChart.init(document.getElementById('ortCompareChart'));
  refreshOrtCompare();
}

  return {
    init: function(dataset) {
      if (!dataset) return;
      var container = document.getElementById('tab-dashboard');
      if (container && !container.hasChildNodes()) {
        container.innerHTML = _buildDashboardHTML();
      }
      state.dataset = dataset;
      _initSelectedRunIds();
      renderMeta();
      initTabs();
      renderRunSelectors('fpsRunSelectors');
      renderRunSelectors('overviewRunSelectors');
      initFpsFilters();
      initOverviewFilters();
      FpsChart.init(document.getElementById('fpsCompareChart'), handleFpsEnvClick);
      Chart.init(document.getElementById('mainChart'), function(idx, d) {
        state.selectedEnvId = d.envId;
        renderEnvDetail(d.env, {scroll: true});
        Chart.update(state.chartData, state.selectedEnvId);
      });
      refreshFpsCompare();
      refreshChart();
      initDetailTab();
      if ((state.dataset.snapshots || []).length) {
        initTrendChart();
        initTrendTab();
      }
      initOrtCompareTab();
      dispatchBenchmarkHelpSync();
    },
    refresh: function() {
      if (!state.dataset) return;
      refreshFpsCompare();
      refreshChart();
      dispatchBenchmarkHelpSync();
    },
    refreshAllCharts: function() {
      if (!state.dataset) return;
      refreshFpsCompare();
      refreshChart();
      if (Object.keys(state.trendCharts).length) refreshTrend();
      refreshOrtCompare();
    },
    openEdgeGuide: function() {
      _navigateToEdgeGuide();
    },
  };

})();
if (typeof registerBenchmarkLangRefresher === 'function') {
  registerBenchmarkLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof Dashboard !== 'undefined' && typeof Dashboard.refreshAllCharts === 'function') Dashboard.refreshAllCharts();
  });
}
