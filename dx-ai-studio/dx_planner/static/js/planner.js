/**
 * DX EdgeGuide — Main Entry Point
 * 모듈 와이어링: DataLoader, I18n, WizardController, RecommendEngine,
 *               CardRenderer, BarChart, GaugeChart, ExplorerView, PlannerWorkspace
 */

/* global DataLoader, I18n, WizardController, RecommendEngine,
          CardRenderer, BarChart, ExplorerView, RadarChart, GroupBarChart, GaugeChart, DXChat, PlannerWorkspace, MethodologyDialog */

window.PlannerRuntime = {
  getLastResults() { return _lastResults; },
  getLastInputs() { return _lastInputs; },
  buildShareUrl(inputs) { return buildShareUrl(inputs || _lastInputs); },
};

const PLANNER_STORAGE_KEY = 'dxPlanner.state.v1';

let _lastResults = null;
let _lastInputs = null;
let _suspendAutoRefresh = false;
let _overviewRedrawFrame = null;
let _overviewResizeTimer = null;
let _overviewResizeObserver = null;
let _recommendationDebounceTimer = null;
let _lastRecommendationSignature = null;

function recommendationSignature(inputs, compareId) {
  return JSON.stringify({ inputs, compareId });
}

// ── Share link: build a URL that fully reproduces the current inputs ──
// (task/size/cameras/fps/ort plus priority + latency, which were previously dropped).
function buildShareParams(inputs) {
  const params = new URLSearchParams();
  if (!inputs) return params;
  if (inputs.task) params.set('task', inputs.task);
  if (inputs.size) params.set('size', inputs.size);
  if (inputs.cameras != null) params.set('cameras', String(inputs.cameras));
  if (inputs.targetFps != null) params.set('fps', String(inputs.targetFps));
  if (inputs.ort != null) params.set('ort', String(inputs.ort));
  if (inputs.priority) params.set('priority', inputs.priority);
  if (inputs.maxLatencyMs != null) params.set('latency', String(inputs.maxLatencyMs));
  return params;
}

function buildShareUrl(inputs) {
  const params = buildShareParams(inputs);
  const loc = (typeof window !== 'undefined' && window.location) ? window.location : null;
  const base = loc ? loc.origin + loc.pathname : '';
  const qs = params.toString();
  return qs ? base + '?' + qs : base;
}

// Keep the address bar in sync so the current URL is always a shareable link.
function updateShareUrl(inputs) {
  if (typeof window === 'undefined' || !window.history || !window.history.replaceState) return;
  try {
    window.history.replaceState(null, '', buildShareUrl(inputs));
  } catch (e) { /* replaceState can throw in sandboxed contexts */ }
}

// ── localStorage persistence: survive page refresh ──
function persistPlannerState() {
  try {
    if (typeof localStorage === 'undefined' || !localStorage) return;
    if (!_lastInputs) return;
    const started = typeof PlannerWorkspace !== 'undefined' && PlannerWorkspace.hasStarted();
    const payload = {
      inputs: _lastInputs,
      results: _lastResults,
      view: {
        started,
        selectedPlatformId: typeof PlannerWorkspace !== 'undefined'
          ? PlannerWorkspace.getSelectedPlatformId() : null,
        compareId: typeof PlannerWorkspace !== 'undefined'
          ? PlannerWorkspace.getComparePlatformId() : null,
      },
    };
    localStorage.setItem(PLANNER_STORAGE_KEY, JSON.stringify(payload));
  } catch (e) { /* storage unavailable / quota exceeded — non-fatal */ }
}

function loadPersistedState() {
  try {
    if (typeof localStorage === 'undefined' || !localStorage) return null;
    const raw = localStorage.getItem(PLANNER_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

function drawOverviewChart() {
  const barCanvas = document.getElementById('overviewChart');
  if (barCanvas && _lastResults) BarChart.draw(barCanvas, _lastResults, openDetail);
}

function scheduleOverviewChartRedraw() {
  const opts = arguments[0] || {};
  if (opts.debounce) {
    if (_overviewResizeTimer) clearTimeout(_overviewResizeTimer);
    _overviewResizeTimer = setTimeout(() => {
      _overviewResizeTimer = null;
      scheduleOverviewChartRedraw();
    }, 150);
    return;
  }
  if (_overviewRedrawFrame) cancelAnimationFrame(_overviewRedrawFrame);
  _overviewRedrawFrame = requestAnimationFrame(() => {
    _overviewRedrawFrame = null;
    drawOverviewChart();
  });
}

function dispatchPlannerHelpSync() {
  requestAnimationFrame(() => {
  });
}

function scheduleRecommendation(options) {
  const opts = options || {};
  if (_recommendationDebounceTimer) clearTimeout(_recommendationDebounceTimer);
  _recommendationDebounceTimer = setTimeout(() => {
    _recommendationDebounceTimer = null;
    runRecommendation(opts);
    scheduleOverviewChartRedraw();
    dispatchPlannerHelpSync();
  }, 150);
}

function observeOverviewChartResize() {
  const container = document.getElementById('overview-chart-container');
  if (!container) return;
  const scheduleResizeRedraw = () => {
    scheduleOverviewChartRedraw({ debounce: true });
  };
  if (typeof ResizeObserver !== 'undefined') {
    _overviewResizeObserver = new ResizeObserver(scheduleResizeRedraw);
    _overviewResizeObserver.observe(container);
  } else {
    window.addEventListener('resize', scheduleResizeRedraw);
  }
}

function runRecommendation(options) {
  const opts = options || {};
  const inputs = WizardController.getInputs();
  const compareId = PlannerWorkspace.getComparePlatformId();
  const signature = recommendationSignature(inputs, compareId);
  let results = _lastResults;

  if (signature !== _lastRecommendationSignature || !_lastResults) {
    const platforms = DataLoader.getPlatforms();
    results = RecommendEngine.recommend(inputs, platforms);
    _lastRecommendationSignature = signature;
    _lastResults = results;
    _lastInputs = inputs;

    CardRenderer.render(results, inputs);
    PlannerWorkspace.renderRecommendationSummary(inputs, results);
    dispatchPlannerHelpSync();
  } else {
    _lastInputs = inputs;
  }

  if (compareId && !results.some(r => r.platform.id === compareId)) {
    PlannerWorkspace.clearCompareSelection();
  }

  drawOverviewChart();

  if (opts.preserveSelection && PlannerWorkspace.getSelectedPlatformId()) {
    const selectedId = PlannerWorkspace.getSelectedPlatformId();
    if (results.some(r => r.platform.id === selectedId)) {
      openDetail(selectedId);
    } else {
      PlannerWorkspace.showDetailEmpty();
      dispatchPlannerHelpSync();
    }
  }

  updateShareUrl(_lastInputs);
  persistPlannerState();
}

function openDetail(platformId) {
  PlannerWorkspace.showDetail(platformId);
  ExplorerView.open(platformId, _lastInputs, _lastResults);
  PlannerWorkspace.markCommerceStepActive(true);
  scheduleOverviewChartRedraw();
  dispatchPlannerHelpSync();
  persistPlannerState();
}

const SCENARIO_PRESETS = {
  cctv: { task: 'object_detection', size: 'n', cameras: 4, targetFps: 30, ort: true },
  retail: { task: 'classification', size: 's', cameras: 8, targetFps: 15, ort: true },
  pose: { task: 'pose_estimation', size: 'm', cameras: 2, targetFps: 30, ort: false },
};

function bindScenarioChips() {
  document.querySelectorAll('.scenario-chip[data-preset]').forEach(chip => {
    chip.addEventListener('click', () => {
      const preset = SCENARIO_PRESETS[chip.dataset.preset];
      if (!preset) return;
      _suspendAutoRefresh = true;
      WizardController.setInputs(preset);
      _suspendAutoRefresh = false;
      if (PlannerWorkspace.hasStarted()) {
        scheduleRecommendation({ preserveSelection: false });
      } else {
        WizardController.goToSetupStep(2);
      }
    });
  });
}

function triggerInitialRecommendationFromUrl(hasPrefill) {
  if (!hasPrefill) return;
  WizardController.goToSetupStep(2);
  WizardController.unlockSetupSteps();
  PlannerWorkspace.showRecommendations();
  runRecommendation();
  scheduleOverviewChartRedraw();
}

async function initConfigurator() {
  // Init i18n (handled by shared/i18n.js on DOMContentLoaded)

  try {
    await DataLoader.load();
  } catch (e) {
    const panel = document.getElementById('requirementsPanel');
    if (panel) panel.innerHTML = '<p style="color:var(--error);padding:2rem;">⚠️ 벤치마크 데이터를 로드할 수 없습니다.</p>';
    return;
  }

  WizardController.init();
  PlannerWorkspace.init();
  MethodologyDialog.init();
  PlannerWorkspace.renderScopeBannerMeta();
  bindScenarioChips();

  const urlParams = new URLSearchParams(window.location.search);
  const preTask = urlParams.get('task');
  const preSize = urlParams.get('size');
  const preCameras = parseInt(urlParams.get('cameras'), 10);
  const preFps = parseInt(urlParams.get('fps'), 10);
  const preOrt = urlParams.get('ort');
  const prePriority = urlParams.get('priority');
  const preLatency = parseInt(urlParams.get('latency'), 10);
  const hasLatency = !isNaN(preLatency) && preLatency > 0;
  const hasPrefill = preTask !== null || preSize !== null ||
    !isNaN(preCameras) || !isNaN(preFps) || preOrt !== null ||
    prePriority !== null || hasLatency;

  // A share link (URL params) takes precedence; otherwise restore the last session.
  const persisted = hasPrefill ? null : loadPersistedState();

  if (hasPrefill) {
    WizardController.setInputs({
      task: preTask || undefined,
      size: preSize || undefined,
      cameras: isNaN(preCameras) ? undefined : preCameras,
      targetFps: isNaN(preFps) ? undefined : preFps,
      ort: preOrt !== null ? preOrt === 'true' : undefined,
      priority: prePriority || undefined,
      maxLatencyMs: hasLatency ? preLatency : undefined,
    });
  } else if (persisted && persisted.inputs) {
    const pi = persisted.inputs;
    WizardController.setInputs({
      task: pi.task,
      size: pi.size,
      cameras: pi.cameras,
      targetFps: pi.targetFps,
      ort: pi.ort,
      priority: pi.priority,
      fpsHeadroom: pi.fpsHeadroom,
      maxLatencyMs: pi.maxLatencyMs != null ? pi.maxLatencyMs : undefined,
    });
  }

  const shouldRestoreView = !hasPrefill && persisted && persisted.view && persisted.view.started;
  triggerInitialRecommendationFromUrl(hasPrefill || shouldRestoreView);

  // Re-open the previously selected platform / comparison after results render.
  if (shouldRestoreView) {
    const view = persisted.view;
    if (view.compareId) {
      const dropdown = document.getElementById('compare-dropdown');
      if (dropdown) dropdown.value = view.compareId;
    }
    if (view.selectedPlatformId && _lastResults &&
        _lastResults.some(r => r.platform.id === view.selectedPlatformId)) {
      openDetail(view.selectedPlatformId);
    }
  }

  observeOverviewChartResize();

  WizardController.onRecommend(() => {
    WizardController.unlockSetupSteps();
    PlannerWorkspace.showRecommendations();
    runRecommendation();
    scheduleOverviewChartRedraw();
    dispatchPlannerHelpSync();
  });

  WizardController.onChange(() => {
    if (!_suspendAutoRefresh && PlannerWorkspace.hasStarted()) {
      scheduleRecommendation({ preserveSelection: true });
    }
  });

  CardRenderer.onDetailClick(openDetail);

  ExplorerView.setOnModelClick(({ task, size, ort }) => {
    _suspendAutoRefresh = true;
    WizardController.setInputs({ task, size, ort });
    _suspendAutoRefresh = false;
    scheduleRecommendation({ preserveSelection: true });
  });
}

document.addEventListener('DOMContentLoaded', initConfigurator);
