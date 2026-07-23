'use strict';

let _currentDetailModel = null;

function setModelZooStatusHtml(el, html) {
  if (!el) return;
  if (el._lastModelZooStatusHtml === html) return;
  el._lastModelZooStatusHtml = html;
  el.innerHTML = html;
}

// 최적화 이미지 헬퍼 (catalog.js의 ModelZooImages와 동일 정책)

function _detailOptimizedCandidates(originalPath) {
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

function _detailImageTag(originalPath, alt, extraAttrs) {
  const candidates = _detailOptimizedCandidates(originalPath);
  const first = candidates.shift() || '';
  const encoded = JSON.stringify(candidates);
  const attrs = extraAttrs || '';
  return `<img src="${escapeHtml(first)}" alt="${escapeHtml(alt || '')}" loading="lazy" decoding="async" data-fallbacks='${escapeHtml(encoded)}' onerror="handleImageFallback(this)" ${attrs}>`;
}

function _detailHandleImageFallback(img) {
  const fallbacks = JSON.parse(img.dataset.fallbacks || '[]');
  const next = fallbacks.shift();
  if (next) {
    img.dataset.fallbacks = JSON.stringify(fallbacks);
    img.src = next;
    return;
  }
  img.onerror = null;
  img.parentElement?.classList.add('no-thumb');
  img.remove();
}

// catalog.js가 먼저 로드되면 window.handleImageFallback이 이미 존재함.
// 독립 로드 시에도 동작하도록 fallback 등록
if (typeof window.handleImageFallback !== 'function') {
  window.handleImageFallback = _detailHandleImageFallback;
}

function _localLabel(obj, prefix) {
  const lang = DXI18n.lang;
  return obj[prefix + '_' + lang] || obj[prefix + '_' + lang.split('-')[0]] || obj[prefix + '_en'] || '';
}

function _localText(obj) {
  if (!obj) return '';
  const lang = DXI18n.lang;
  return obj[lang] || obj[lang.split('-')[0]] || obj.en || '';
}

const DETAIL_ARTIFACTS = [
  { id: 'onnx', label: 'ONNX' },
  { id: 'qlite_dxnn', label: 'Q-Lite DXNN' },
  { id: 'qlite_json', label: 'Q-Lite JSON' },
  { id: 'qpro_dxnn', label: 'Q-Pro DXNN' },
  { id: 'qpro_json', label: 'Q-Pro JSON' },
];

function _hasValue(value) {
  return value !== null && value !== undefined && value !== '';
}

function _detailStatus(label) {
  return `<span class="mz-field-empty">${escapeHtml(T(label))}</span>`;
}

function _detailValue(v, fallbackLabel) {
  if (!_hasValue(v)) return _detailStatus(fallbackLabel || 'Not provided by source');
  if (Array.isArray(v)) return escapeHtml(v.join(', '));
  if (typeof v === 'object') return escapeHtml(Object.entries(v).map(([k, value]) => `${k}: ${value}`).join(', '));
  return escapeHtml(String(v));
}

function _commercialUseLabel(cu) {
  switch (cu) {
    case 'allowed': return T('Allowed — commercial use permitted');
    case 'copyleft': return T('Copyleft — commercial use OK, share-alike required');
    case 'non-commercial': return T('Non-commercial — commercial use prohibited');
    default: return T('Restricted — license review required');
  }
}

function _commercialUseValue(cu) {
  const key = ['allowed', 'copyleft', 'non-commercial', 'restricted'].indexOf(cu) >= 0 ? cu : 'restricted';
  return `<span class="mz-commercial mz-commercial-${key}"><span class="mz-commercial-dot"></span>${escapeHtml(_commercialUseLabel(key))}</span>`;
}

function _commercialUseWarning(cu) {
  if (cu === 'non-commercial') {
    return `<div class="mz-commercial-warn non-commercial">⚠ ${escapeHtml(T('This model is licensed for non-commercial use only — review the source license before deploying commercially.'))}</div>`;
  }
  if (cu === 'restricted') {
    return `<div class="mz-commercial-warn restricted">⚠ ${escapeHtml(T('This model has no clear commercial-use license — review the source license before deploying commercially.'))}</div>`;
  }
  return '';
}

function _sourceStatusText(status) {
  const labels = {
    provided: 'Available',
    not_provided: 'Not provided by source',
    benchmark_required: 'Benchmark required',
    metadata_pending: 'Metadata pending',
    artifact_unavailable: 'Artifact unavailable',
    source_error: 'Source refresh failed',
    stale_cache: 'Using cached data after refresh failed',
    suspect: 'Suspect value: source verification required',
  };
  return T(labels[status] || 'Metadata pending');
}

function _artifactSourceCell(data) {
  if (_hasValue(data.remote_url)) {
    const url = String(data.remote_url);
    if (/^https:\/\//i.test(url)) {
      return `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(url)}</a>`;
    }
    return escapeHtml(url);
  }
  if (_hasValue(data.source)) return escapeHtml(String(data.source));
  if (_hasValue(data.source_status)) return escapeHtml(_sourceStatusText(data.source_status));
  return _detailStatus('Not provided by source');
}

function _metricText(metric) {
  if (!metric) return '';
  if (typeof metric === 'object') {
    if (metric.name) return metric.name;
    return Object.entries(metric).map(([k, v]) => `${k}: ${v}`).join(', ');
  }
  return metric;
}

function _bestAccuracy(model) {
  const evaluation = model.evaluation || {};
  for (const id of ['raw', 'onnx', 'qlite', 'qpro']) {
    const accuracy = evaluation[id]?.accuracy;
    if (_hasValue(accuracy)) return accuracy;
  }
  // No accuracy in evaluation → leave empty ("Not provided by source"). Do NOT fall back to
  // the metric spec: metric is the metric *name* (e.g. {name:"TopK1, TopK5"}), not an
  // accuracy value, so the fallback made Accuracy mirror Metric.
  return '';
}

function _inputResolution(model) {
  const spec = model.specification || {};
  if (spec.input_resolution) return spec.input_resolution;
  if (spec.input_width && spec.input_height) return `${spec.input_width}x${spec.input_height}`;
  if (Array.isArray(spec.input_shape)) return spec.input_shape.join('x');
  return '';
}

function _performanceFps(model) {
  const performance = model.performance || {};
  const fps = performance.fps ?? model.specification?.fps;
  return _hasValue(fps) ? `${fps} FPS` : T('Benchmark required');
}

function _artifactEndpoint(modelId, artifactId) {
  return `/api/catalog/${encodeURIComponent(modelId)}/artifacts/${artifactId}`;
}

function _artifactAvailable(model, artifactId) {
  const artifact = (model.artifacts || {})[artifactId] || {};
  if (artifact.available === false) return false;
  return artifact.available === true ||
    Boolean(artifact.download_endpoint || artifact.local_path || artifact.remote_url);
}

function _artifactBadge(model, artifactId, label) {
  const available = _artifactAvailable(model, artifactId);
  const status = available ? 'ready' : 'not-ready';
  const icon = available ? '✅' : '⏳';
  const title = available ? label : T('Artifact unavailable');
  return `<span class="mz-download-badge ${status}" title="${escapeHtml(title)}">${icon} ${escapeHtml(label)}</span>`;
}

function _artifactAction(model, artifactId) {
  if (!_artifactAvailable(model, artifactId)) return _detailStatus('Artifact unavailable');
  const href = _artifactEndpoint(model.id, artifactId);
  return `<a class="mz-artifact-link" href="${escapeHtml(href)}" target="_blank" rel="noopener">${escapeHtml(T('Download'))}</a>`;
}

function _metadataSource(model) {
  return model.metadata_source || model.metadata || {};
}

function _lastMetadataSync(model) {
  const source = _metadataSource(model);
  return source.generated_at || source.last_sync || source.last_metadata_sync || model.generated_at || '';
}

function _artifactLastChecked(model, artifact) {
  return artifact.last_checked || artifact.checked_at || artifact.fetched_at ||
    artifact.generated_at || _lastMetadataSync(model);
}

async function renderDetailPage(modelId) {
  const container = document.getElementById('detailView');
  if (!container) return;
  container.innerHTML = '<div class="mz-placeholder"><div class="mz-spinner"></div></div>';

  try {
    const resp = await fetch(modelzooApiUrl(`/api/catalog/${encodeURIComponent(modelId)}`));
    if (!resp.ok) throw new Error(`${resp.status}`);
    const data = await resp.json();
    if (!data.ok || !data.model) throw new Error(data.error || 'Not found');
    renderDetail(container, data.model);
  } catch (e) {
    container.innerHTML = `<div class="mz-placeholder">${T('Model not found')}: ${escapeHtml(modelId)}</div>`;
  }
}

function renderDetailActionBar(model) {
  // Downloads live in the header (next to artifact badges) — do NOT duplicate them here.
  // Compile/Demo use scrollToDetailSection (NOT href="#...") because the modelzoo SPA routes
  // on location.hash: any hash that is not "#model=..." makes route() hide the detail view.
  return `<div class="mz-detail-action-bar" data-detail-action-bar>
    <button class="mz-btn mz-btn-outline" onclick="location.hash=''">← ${T('Back to Catalog')}</button>
    <button class="mz-btn mz-btn-outline" onclick="scrollToDetailSection('sectionCompile')">🔧 ${T('How to Compile DXNN')}</button>
    <button class="mz-btn mz-btn-primary" onclick="scrollToDetailSection('demoSection')">▶ ${T('Demo Usage')}</button>
    <button class="mz-btn mz-btn-outline" onclick="exportModelCardHtml()">💾 ${T('Save as HTML')}</button>
  </div>`;
}

function scrollToDetailSection(id) {
  const el = document.getElementById(id);
  if (el) { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
}

function renderDetail(container, model) {
  _currentDetailModel = model;
  const catInfo = (_catalogData?.categories || {})[model.category] || {};
  const catLabel = _localLabel(catInfo, 'label') || model.category;
  const summary = _localText(model.display?.summary) || _localText(model.content?.use_case) || T('Metadata pending');

  container.innerHTML = `
    <button class="mz-back-btn" onclick="location.hash=''">← ${T('Back to Catalog')}</button>
    <article class="mz-detail-document">
      <header class="mz-detail-header">
        <div class="mz-detail-hero">
          <h1 class="mz-detail-title">${escapeHtml(model.name)}</h1>
          <span class="mz-card-cat">${escapeHtml(catInfo.icon || '')} ${escapeHtml(catLabel)}</span>
          <p class="mz-detail-summary">${escapeHtml(summary)}</p>
          <div class="mz-detail-hero-badges">
            ${_artifactBadge(model, 'onnx', 'ONNX')}
            ${_artifactBadge(model, 'qlite_dxnn', 'Q-Lite')}
            ${_artifactBadge(model, 'qpro_dxnn', 'Q-Pro')}
          </div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap" data-detail-downloads>
          ${renderDownloadButtons(model, 'summary')}
        </div>
      </header>
      <div class="mz-detail-two-by-two">
        <div class="mz-detail-col mz-detail-col-right">
          <aside class="mz-detail-panel mz-detail-panel-b">
            <div class="mz-detail-side-sticky">
              ${renderDetailActionBar(model)}
              <section class="mz-detail-section mz-detail-side-section" id="sectionQuickFacts">
                <h3>📌 ${T('Key Facts')}</h3>
                ${renderKeyFacts(model)}
              </section>
            </div>
          </aside>

          <div class="mz-detail-panel mz-detail-panel-d">
            <section class="mz-detail-section" id="sectionSpec">
              <h3>📊 ${T('Specification')}</h3>
              <div class="mz-spec-metrics-grid">
                ${renderAccuracyMatrix(model)}
                ${renderRuntimePerformance(model)}
              </div>
              ${renderSpecification(model)}
              ${renderArtifactTable(model)}
            </section>

            <section class="mz-detail-section" id="sectionCompile">
              <h3>🔧 ${T('How to Compile DXNN')}</h3>
              ${renderCompileGuide(model)}
            </section>
          </div>
        </div>

        <div class="mz-detail-col mz-detail-col-left">
          <div class="mz-detail-panel mz-detail-panel-a">
            <section class="mz-detail-section" id="sectionUseCase">
              <h3>📝 ${T('Use Case & Description')}</h3>
              ${renderDescription(model)}
            </section>

            <section class="mz-detail-section" id="sectionExample">
              <h3>🖼️ ${T('Example')}</h3>
              ${renderExampleText(model)}
              ${renderExampleImages(model)}
              <details style="margin-top:24px">
                <summary style="cursor:pointer;font-weight:600">🔬 ${T('Run Inference')}</summary>
                <div id="inferencePanel"></div>
              </details>
            </section>
          </div>

          <div class="mz-detail-panel mz-detail-panel-c">
            <section class="mz-detail-section" id="demoSection">
              <h3>💻 ${T('Demo Usage')}</h3>
              <div id="demoContent"><div class="mz-placeholder"><div class="mz-spinner"></div></div></div>
            </section>
          </div>
        </div>
      </div>

      <section class="mz-detail-section" id="sectionLegal">
        <h3>⚖️ ${T('Legal Information')}</h3>
        ${renderLegal(model)}
      </section>
    </article>
  `;

  initDownloadButtons(container);
  loadDemoCode(model);
  if (typeof renderInferencePanel === 'function') {
    renderInferencePanel(model);
  }
  initBeforeAfterSliders();
  initOverlayOpacitySliders(container);
}

function refreshDetailActionBarsForHealth() {
  if (!_currentDetailModel) return false;
  const container = document.getElementById('detailView');
  if (!container) return false;
  container.querySelectorAll('[data-detail-downloads]').forEach(el => {
    el.innerHTML = renderDownloadButtons(_currentDetailModel, 'summary');
  });
  const actionBar = container.querySelector('[data-detail-action-bar]');
  if (actionBar) {
    actionBar.outerHTML = renderDetailActionBar(_currentDetailModel);
  }
  initDownloadButtons(container);
  return true;
}

function renderDescription(model) {
  const desc = model.description || {};
  const text = _localText(desc) || _localText(model.content?.use_case);
  if (!text) return `<p style="color:var(--text-3)">${T('Description coming soon')}</p>`;
  return `<p>${escapeHtml(text)}</p>`;
}

function renderExampleText(model) {
  const text = _localText(model.content?.example);
  if (!text) return `<p class="mz-muted">${escapeHtml(T('Metadata pending'))}</p>`;
  return `<p>${escapeHtml(text)}</p>`;
}

function renderKeyFacts(model) {
  const spec = model.specification || {};
  const legal = model.legal || {};
  const rows = [
    ['Dataset', spec.dataset],
    ['Input Resolution', _inputResolution(model)],
    ['Metric', _metricText(spec.metric)],
    ['Accuracy', _bestAccuracy(model)],
    ['FPS', _performanceFps(model)],
    ['License', legal.license],
  ];
  return `<div class="mz-key-facts" aria-label="${escapeHtml(T('Key Facts'))}">
    ${rows.map(([k, v]) => `<div class="mz-key-fact"><span>${escapeHtml(T(k))}</span><strong>${_detailValue(v, k === 'FPS' ? 'Benchmark required' : 'Not provided by source')}</strong></div>`).join('')}
  </div>`;
}

function renderArtifactTable(model) {
  return `<div class="mz-datasheet-block">
    <h4>${escapeHtml(T('Artifacts & Downloads'))}</h4>
    <table class="mz-artifact-table"><thead><tr>
      <th>${escapeHtml(T('Artifact'))}</th>
      <th>${escapeHtml(T('Status'))}</th>
      <th>${escapeHtml(T('Source'))}</th>
      <th>${escapeHtml(T('Last metadata sync'))}</th>
      <th>${escapeHtml(T('Download'))}</th>
    </tr></thead><tbody>
      ${DETAIL_ARTIFACTS.map(artifact => {
        const data = (model.artifacts || {})[artifact.id] || {};
        const status = _artifactAvailable(model, artifact.id)
          ? T('Available')
          : T('Artifact unavailable');
        const lastChecked = _artifactLastChecked(model, data);
        return `<tr>
          <th>${escapeHtml(artifact.label)}</th>
          <td>${escapeHtml(status)}</td>
          <td>${_artifactSourceCell(data)}</td>
          <td>${lastChecked ? escapeHtml(lastChecked) : _detailStatus('Metadata pending')}</td>
          <td>${_artifactAction(model, artifact.id)}</td>
        </tr>`;
      }).join('')}
    </tbody></table>
  </div>`;
}

function renderAccuracyMatrix(model) {
  const evaluation = model.evaluation || {};
  const rows = [
    ['Raw', evaluation.raw],
    ['Q-Lite', evaluation.qlite],
    ['Q-Pro', evaluation.qpro],
  ].filter(([, evalEntry]) => _hasValue(evalEntry?.accuracy) || evalEntry?.source_status === 'suspect');
  return `<div class="mz-datasheet-block">
    <h4>${escapeHtml(T('Accuracy Matrix'))}</h4>
    <table class="mz-accuracy-matrix"><tbody>
      ${rows.length ? rows.map(([label, evalEntry]) => {
        if (evalEntry?.source_status === 'suspect') {
          return `<tr><th>${escapeHtml(T(label))}</th><td class="mz-suspect">${escapeHtml(T('Suspect value: source verification required'))}</td></tr>`;
        }
        return `<tr><th>${escapeHtml(T(label))}</th><td>${_detailValue(evalEntry?.accuracy, 'Not provided by source')}</td></tr>`;
      }).join('') : `<tr><td>${_detailStatus('Metadata pending')}</td></tr>`}
    </tbody></table>
  </div>`;
}

function renderRuntimePerformance(model) {
  const performance = model.performance || {};
  const rows = [
    ['FPS', performance.fps ?? model.specification?.fps, 'Benchmark required'],
    ['FPS/Watt', performance.fps_per_watt, 'Benchmark required'],
    ['Status', performance.source_status ? _sourceStatusText(performance.source_status) : T('Benchmark required'), 'Benchmark required'],
  ];
  return `<div class="mz-datasheet-block">
    <h4>${escapeHtml(T('Runtime Performance'))}</h4>
    <table class="mz-runtime-performance"><tbody>
      ${rows.map(([label, value, fallback]) => `<tr><th>${escapeHtml(T(label))}</th><td>${_detailValue(value, fallback)}</td></tr>`).join('')}
    </tbody></table>
  </div>`;
}

function renderExampleImages(model) {
  const ex = model.example_images || {};
  const type = ex.type || 'single';
  const resultPath = ex.result || '';
  const originalPath = ex.original || '';

  if (!resultPath) {
    return `<p style="color:var(--text-3)">${T('Run inference to generate example images.')}</p>`;
  }

  switch (type) {
    case 'before_after':
      return `<div class="mz-ba-container">
        ${_detailImageTag(originalPath, T('Before'), 'class="mz-example-image"')}
        <div class="mz-ba-after" id="baAfter">
          ${_detailImageTag(resultPath, T('After'), 'class="mz-example-image"')}
        </div>
        <div class="mz-ba-slider" id="baSlider" style="left:50%"></div>
        <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:12px;color:var(--text-3)">
          <span>${T('Before')}</span><span>${T('After')}</span>
        </div>
      </div>`;

    case 'overlay':
      return `<div class="mz-example-overlay">
        ${_detailImageTag(originalPath, T('Before'), 'class="mz-example-image"')}
        ${_detailImageTag(resultPath, T('Overlay'), 'id="overlayImg" class="mz-example-overlay-result"')}
        <label style="display:flex;align-items:center;gap:8px;margin-top:8px;font-size:14px;cursor:pointer">
          <input type="range" min="0" max="100" value="60"
            data-overlay-opacity-target="overlayImg">
          ${T('Overlay')}
        </label>
      </div>`;

    case 'classified':
      return `<div class="mz-classified-example">
        ${_detailImageTag(resultPath, T('After'), 'class="mz-example-image"')}
        <div id="classificationResults" class="mz-classified-results">
          <p style="color:var(--text-3)">${T('Run inference to see classification results.')}</p>
        </div>
      </div>`;

    case 'gallery':
      return `<div class="mz-example-gallery">
        ${_detailImageTag(resultPath, 'Query', 'class="mz-example-image mz-example-gallery-image"')}
      </div>`;

    default:
      return _detailImageTag(resultPath, model.name, 'class="mz-example-image"');
  }
}

function renderSpecification(model) {
  const spec = model.specification || {};
  const technical = model.technical || {};
  const performance = model.performance || {};
  const rows = [
    ['Input Resolution', _inputResolution(model)],
    ['FPS (DX-M1)', performance.fps ?? spec.fps],
    ['FPS/Watt', performance.fps_per_watt ?? spec.fps_per_watt],
    ['Parameters', spec.params || spec.parameters],
    ['Operations', spec.ops || spec.operations],
    ['Dataset', spec.dataset],
    ['Metric', _metricText(spec.metric)],
    ['Quantization', Array.isArray(spec.quantization) ? spec.quantization.join(', ') : spec.quantization],
    ['Postprocessor', technical.postprocessor],
    ['Input Shape', technical.input_shape],
  ];
  const leftRows = rows.slice(0, 5);
  const rightRows = rows.slice(5);
  const renderRows = (entries) => `<table class="mz-spec-table"><tbody>
    ${entries.map(([k, v]) => `<tr><th>${T(k)}</th><td>${_detailValue(v, 'Not provided by source')}</td></tr>`).join('')}
  </tbody></table>`;

  return `<div class="mz-spec-columns">
    <div class="mz-spec-group">
      <h4>${escapeHtml(T('Model Inputs & Core Metrics'))}</h4>
      ${renderRows(leftRows)}
    </div>
    <div class="mz-spec-group">
      <h4>${escapeHtml(T('Runtime & Deployment Metadata'))}</h4>
      ${renderRows(rightRows)}
    </div>
  </div>`;
}

function renderCompileGuide(model) {
  const guide = model.compile_guide || {};
  const notes = guide.notes || {};
  const text = _localText(notes) || _localText(model.content?.compile_guide);
  const quantization = Array.isArray(model?.specification?.quantization)
    ? model.specification.quantization.join(', ')
    : model?.specification?.quantization;
  const checklist = [
    { label: T('Input Resolution'), value: _detailValue(_inputResolution(model), 'Not provided by source') },
    { label: T('Quantization'), value: _detailValue(quantization, 'Not provided by source') },
    {
      label: T('ONNX Model Link'),
      value: _artifactAvailable(model, 'onnx') ? escapeHtml(T('Available')) : _detailStatus('Not provided by source')
    },
    { label: T('Class Name'), value: _detailValue(model.display?.class_name || model.class_name, 'Not provided by source') }
  ];
  const outputs = [
    { label: 'Q-Lite DXNN', ready: _artifactAvailable(model, 'qlite_dxnn') },
    { label: 'Q-Lite JSON', ready: _artifactAvailable(model, 'qlite_json') },
    { label: 'Q-Pro DXNN', ready: _artifactAvailable(model, 'qpro_dxnn') },
    { label: 'Q-Pro JSON', ready: _artifactAvailable(model, 'qpro_json') },
  ];
  const steps = [T('View Model Graph'), T('ONNX Model Link'), T('Run Demo')];

  let html = text ? `<p>${escapeHtml(text)}</p>` : `<p style="color:var(--text-3)">${T('Use dxcom default settings.')}</p>`;
  html += `
    <div class="mz-compile-grid">
      <section class="mz-compile-block">
        <h4>${escapeHtml(T('Compile Checklist'))}</h4>
        <ul class="mz-compile-checklist">
          ${checklist.map((item) => `
            <li>
              <span>${escapeHtml(item.label)}</span>
              <strong>${item.value}</strong>
            </li>
          `).join('')}
        </ul>
      </section>
      <section class="mz-compile-block">
        <h4>${escapeHtml(T('Expected Outputs'))}</h4>
        <div class="mz-compile-outputs">
          ${outputs.map((item) => `
            <span class="mz-compile-output ${item.ready ? 'ready' : 'pending'}">
              ${item.ready ? '✅' : '⏳'} ${escapeHtml(item.label)}
            </span>
          `).join('')}
        </div>
      </section>
      <section class="mz-compile-block">
        <h4>${escapeHtml(T('Quick Compile Steps'))}</h4>
        <ol class="mz-compile-steps">
          ${steps.map((step) => `<li>${escapeHtml(step)}</li>`).join('')}
        </ol>
      </section>
    </div>
  `;
  html += `<div class="mz-action-buttons">`;
  const isValidOnnxUrl = /^https?:\/\//i.test(guide.onnx_url || '');
  if (_artifactAvailable(model, 'onnx') || isValidOnnxUrl) {
    const href = _artifactEndpoint(model.id, 'onnx');
    html += `<a href="${escapeHtml(href)}" target="_blank" rel="noopener" class="mz-btn mz-btn-outline" id="btnOnnxLink">📦 ${T('ONNX Model Link')}</a>`;
  }
  html += `<button class="mz-btn mz-btn-primary" id="btnDxtronCompiler" onclick="openModelzooGraph('${escapeHtml(model.id)}')">📊 ${T('View Model Graph')}</button>`;
  html += `</div>`;
  return html;
}

function _modelzooLauncherLaunch() {
  // Mirrors dx_benchmark/static/js/dashboard.js:_launcherLaunch() — when running
  // inside the launcher iframe, the parent frame exposes a global `launch(app, query)`
  // that switches the launcher shell to another module without leaving the page.
  const candidates = [window.parent, window.top];
  for (let i = 0; i < candidates.length; i++) {
    const w = candidates[i];
    if (w && w !== window && typeof w.launch === 'function') return w.launch.bind(w);
  }
  return null;
}

function _navigateToCompilerGraph(viewerPath, notice) {
  // notice: optional reason code shown by the compiler's empty-viewer state when
  // there is no viewerPath to render (e.g. 'onnx_missing' — see openModelzooGraph).
  const launchFn = _modelzooLauncherLaunch();
  if (viewerPath) {
    const query = new URLSearchParams({ viewer_path: viewerPath }).toString();
    if (launchFn) {
      launchFn('compiler', query);
      return;
    }
    // Standalone (no parent launcher): fall back to the previous new-tab behavior.
    window.open('/compiler/?viewer_path=' + encodeURIComponent(viewerPath), '_blank', 'noopener');
    return;
  }
  if (notice) {
    const query = new URLSearchParams({ viewer_notice: notice }).toString();
    if (launchFn) {
      launchFn('compiler', query);
      return;
    }
    window.open('/compiler/?viewer_notice=' + encodeURIComponent(notice), '_blank', 'noopener');
    return;
  }
  if (launchFn) {
    launchFn('compiler', '');
    return;
  }
  window.open('/compiler/', '_blank', 'noopener');
}

function openModelzooGraph(modelId) {
  // DX-TRON removed this release → open the model's ONNX graph in the dx-compiler viewer.
  // Resolve the absolute local ONNX path first; if it isn't downloaded, fall back to opening
  // the compiler so the user can fetch/compile it there.
  //
  // NOTE: the compiler's graph viewer (dx_compiler/static/js/viewer_panel.js loadModel() ->
  // POST /viewer/parse -> dx_compiler/core/onnx_parser.py:parse_onnx_model()) parses ONNX
  // protobuf via `onnx.load()` exclusively. Model Zoo's compiled artifacts (qlite_dxnn /
  // qpro_dxnn, the *.dxnn files) use a distinct DEEPX binary container (magic header
  // b"DXNN...") that is not valid ONNX wire format — onnx.load() raises DecodeError on it
  // (verified empirically). There is no dxnn parser anywhere in dx_compiler; the compiler's
  // "DXNN" tab is only ever populated from a live compile job's SSE progress
  // (handleModelReady), never by pointing loadModel() at an arbitrary .dxnn file on disk.
  // So a dxnn artifact can NOT be handed to this viewer as a substitute for onnx — doing so
  // would surface a parse error instead of a graph. When onnx isn't downloaded locally we
  // land on the compiler with an explicit "download/compile to view the graph" notice
  // instead of silently showing nothing.
  fetch(modelzooApiUrl(`/api/catalog/${encodeURIComponent(modelId)}/artifacts/onnx/localpath`))
    .then((r) => r.json())
    .then((j) => {
      if (j && j.ok && j.path) {
        _navigateToCompilerGraph(j.path);
      } else {
        _navigateToCompilerGraph(null, 'onnx_missing');
      }
    })
    .catch(() => _navigateToCompilerGraph(null, 'onnx_missing'));
}

function openInferencePanelFromDemo() {
  const panel = document.getElementById('inferencePanel');
  if (!panel) return;
  const details = panel.closest('details');
  if (details && !details.open) details.open = true;
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function loadDemoCode(model) {
  const container = document.getElementById('demoContent');
  if (!container) return;

  try {
    const resp = await fetch(modelzooApiUrl(`/api/demo/code/${encodeURIComponent(model.id)}`));
    const data = await resp.json();
    if (!data.ok) throw new Error(data.error);

    let html = '';
    const tabs = [];
    if (data.cpp) tabs.push({ id: 'cpp', label: T('C++ Example') });
    if (data.python) tabs.push({ id: 'python', label: T('Python Example') });
    if (data.cli_command) tabs.push({ id: 'cli', label: T('CLI Command') });

    if (tabs.length === 0) {
      container.innerHTML = `<p style="color:var(--text-3)">${T('No demo code available.')}</p>`;
      return;
    }

    html += `<div class="mz-code-tabs">`;
    tabs.forEach((t, i) => {
      html += `<button class="mz-code-tab ${i === 0 ? 'active' : ''}" onclick="switchDemoTab('${t.id}')">${t.label}</button>`;
    });
    html += `</div>`;

    if (data.cpp) {
      html += `<div class="mz-code-panel" id="panel-cpp" style="${tabs[0].id !== 'cpp' ? 'display:none' : ''}">
        <div class="mz-code-block"><button class="mz-code-copy" onclick="copyCode(this)">📋 ${T('Copy')}</button><pre><code>${escapeHtml(data.cpp)}</code></pre></div></div>`;
    }
    if (data.python) {
      html += `<div class="mz-code-panel" id="panel-python" style="${tabs[0].id !== 'python' ? 'display:none' : ''}">
        <div class="mz-code-block"><button class="mz-code-copy" onclick="copyCode(this)">📋 ${T('Copy')}</button><pre><code>${escapeHtml(data.python)}</code></pre></div></div>`;
    }
    if (data.cli_command) {
      html += `<div class="mz-code-panel" id="panel-cli" style="${tabs[0].id !== 'cli' ? 'display:none' : ''}">
        <div class="mz-code-block"><button class="mz-code-copy" onclick="copyCode(this)">📋 ${T('Copy')}</button><pre><code>${escapeHtml(data.cli_command)}</code></pre></div></div>`;
    }

    html += `<div style="margin-top:16px">
      <button class="mz-btn mz-btn-primary" onclick="openInferencePanelFromDemo()">
        ▶ ${T('Run Demo')}
      </button>
    </div>`;

    container.innerHTML = html;
  } catch (e) {
    container.innerHTML = `<p style="color:var(--text-3)">${T('Failed to load demo')}: ${escapeHtml(e.message)}</p>`;
  }
}

function switchDemoTab(tabId) {
  document.querySelectorAll('.mz-code-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.mz-code-panel').forEach(p => p.style.display = 'none');
  const tab = document.querySelector(`.mz-code-tab[onclick*="${tabId}"]`);
  const panel = document.getElementById(`panel-${tabId}`);
  if (tab) tab.classList.add('active');
  if (panel) panel.style.display = '';
}

function copyCode(btn) {
  const code = btn.parentElement.querySelector('code');
  if (code) {
    navigator.clipboard.writeText(code.textContent).then(() => {
      const orig = btn.textContent;
      btn.textContent = `✓ ${T('Copied!')}`;
      setTimeout(() => { btn.textContent = orig; }, 2000);
    });
  }
}

async function _imageToDataUrl(url) {
  try {
    const resp = await fetch(url);
    if (!resp.ok) { return ''; }
    const blob = await resp.blob();
    return await new Promise(function (resolve) {
      const r = new FileReader();
      r.onloadend = function () { resolve(typeof r.result === 'string' ? r.result : ''); };
      r.onerror = function () { resolve(''); };
      r.readAsDataURL(blob);
    });
  } catch (e) { return ''; }
}

async function exportModelCardHtml() {
  const m = _currentDetailModel;
  if (!m) { return; }
  // embed the model thumbnail (self-contained: base64 data URI). Best-effort.
  let img = '';
  try {
    const thumbUrl = (typeof modelzooApiUrl === 'function')
      ? modelzooApiUrl('/data/thumbnails/' + encodeURIComponent(m.id) + '.jpg')
      : '/data/thumbnails/' + encodeURIComponent(m.id) + '.jpg';
    img = await _imageToDataUrl(thumbUrl);
  } catch (e) { img = ''; }
  const html = _buildModelCardHtml(m, img);
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = (((m.display && m.display.class_name) || m.id || 'model') + '_modelcard.html');
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(function () { URL.revokeObjectURL(url); }, 1500);
}

function _buildModelCardHtml(m, imgDataUrl) {
  const e = escapeHtml;
  const v = function (x) { return _hasValue(x) ? e(String(x)) : '—'; };
  const spec = m.specification || {};
  const perf = m.performance || {};
  const evalm = m.evaluation || {};
  const legal = m.legal || {};
  const demo = m.demo || {};
  const arts = m.artifacts || {};
  const tech = m.technical || {};
  const title = (m.display && m.display.name) || m.name || (m.display && m.display.class_name) || m.id || 'Model';
  const task = (m.display && m.display.category_label) || m.category || '';
  const summary = _localText(m.display && m.display.summary) || _localText(m.content && m.content.use_case) || '';

  // Description (full use-case text) — model.description is curated in all 6 languages.
  const description = _localText(m.description) || _localText(m.content && m.content.use_case) || '';
  const lang = (typeof DXI18n !== 'undefined' && DXI18n.lang) || 'en';
  const gflops = T('Operations') + ' (GFLOPs)';
  const paramsM = T('Parameters') + ' (M)';

  const facts = [
    [T('Class Name'), (m.display && m.display.class_name) || m.id],
    [T('Task'), task],
    [T('Dataset'), spec.dataset],
    [T('Input Resolution'), spec.input_resolution],
    [gflops, spec.operations],
    [paramsM, spec.parameters],
    [T('Metric'), spec.metric && spec.metric.name],
    [T('FPS (DX-M1)'), perf.fps],
    [T('FPS/Watt'), perf.fps_per_watt],
    [T('Quantization'), Array.isArray(spec.quantization) ? spec.quantization.join(', ') : spec.quantization],
  ];
  const factRows = facts.map(function (r) { return '<tr><th>' + e(r[0]) + '</th><td>' + v(r[1]) + '</td></tr>'; }).join('');
  const accRows = [[T('Raw') + ' (FP32)', evalm.raw], ['Q-Lite', evalm.qlite], ['Q-Pro', evalm.qpro]]
    .filter(function (r) { return r[1] && _hasValue(r[1].accuracy); })
    .map(function (r) { return '<tr><th>' + e(r[0]) + '</th><td>' + v(r[1].accuracy) + '</td></tr>'; }).join('') || '<tr><td colspan="2">—</td></tr>';
  const artRows = DETAIL_ARTIFACTS.map(function (art) {
    const d = arts[art.id] || {};
    const link = d.remote_url ? '<a href="' + e(d.remote_url) + '">' + e(d.remote_url) + '</a>' : '—';
    return '<tr><th>' + e(T(art.label)) + '</th><td>' + link + '</td></tr>';
  }).join('');
  const cli = demo.cli_command ? '<pre>' + e(demo.cli_command) + '</pre>' : '';
  const exP = [demo.python_example && ('Python: ' + demo.python_example), demo.cpp_example && ('C++: ' + demo.cpp_example)]
    .filter(Boolean).map(function (s) { return '<div>' + e(s) + '</div>'; }).join('');
  const src = legal.source_url ? '<a href="' + e(legal.source_url) + '">' + e(legal.source_url) + '</a>' : '—';

  const techRows = [
    [T('Postprocessor'), tech.postprocessor],
    [T('Config'), (tech.config && Object.keys(tech.config).length) ? JSON.stringify(tech.config) : ''],
    [T('Input Shape'), Array.isArray(tech.input_shape) ? tech.input_shape.join('x')
      : ((_hasValue(spec.input_width) && _hasValue(spec.input_height) && spec.input_width) ? (spec.input_width + 'x' + spec.input_height) : '')],
  ].filter(function (r) { return _hasValue(r[1]); })
    .map(function (r) { return '<tr><th>' + e(r[0]) + '</th><td>' + v(r[1]) + '</td></tr>'; }).join('');

  const cg = m.compile_guide || {};
  const cgNote = _localText(cg.notes);
  const cgRows = [
    [T('Input Resolution'), spec.input_resolution],
    [T('Quantization'), cg.recommended_quant || (Array.isArray(spec.quantization) ? spec.quantization.join(', ') : spec.quantization)],
    [T('Class Name'), (m.display && m.display.class_name) || m.id],
    ['ONNX', (arts.onnx && arts.onnx.remote_url) ? ('<a href="' + e(arts.onnx.remote_url) + '">' + e(arts.onnx.remote_url) + '</a>') : '—'],
  ].map(function (r) { return '<tr><th>' + e(r[0]) + '</th><td>' + (r[0] === 'ONNX' ? r[1] : v(r[1])) + '</td></tr>'; }).join('');

  const metaSrc = (typeof _metadataSource === 'function') ? _metadataSource(m) : {};
  const lastSync = (typeof _lastMetadataSync === 'function') ? _lastMetadataSync(m) : '';
  const legalRows = [
    [T('License'), v(legal.license)],
    [T('Commercial use'), e(_commercialUseLabel(legal.commercial_use))],
    [T('License text'), v(legal.license_text)],
    [T('Copyright'), v(legal.copyright)],
    [T('Source'), src],
    [T('Source profile'), v(metaSrc.source_profile)],
    [T('Last metadata sync'), v(lastSync)],
  ].map(function (r) { return '<tr><th>' + e(r[0]) + '</th><td>' + (r[0] === T('Source') ? r[1] : r[1]) + '</td></tr>'; }).join('');
  const legalWarn = (legal.commercial_use === 'non-commercial')
    ? ('<p class="sum">⚠ ' + e(T('This model is licensed for non-commercial use only — review the source license before deploying commercially.')) + '</p>')
    : (legal.commercial_use === 'restricted')
      ? ('<p class="sum">⚠ ' + e(T('This model has no clear commercial-use license — review the source license before deploying commercially.')) + '</p>')
      : '';

  const preview = imgDataUrl
    ? '<h2>' + e(T('Preview')) + '</h2><img src="' + imgDataUrl + '" alt="' + e(title) + '" style="display:block;max-width:100%;margin:0 auto 8px;border-radius:10px;border:1px solid rgba(99,140,255,.18)">'
    : '';
  let exportedAt = '';
  try { exportedAt = new Date().toLocaleString(lang); } catch (_) { exportedAt = ''; }

  return '<!doctype html><html lang="' + e(lang) + '"><head><meta charset="utf-8">'
    + '<meta name="viewport" content="width=device-width,initial-scale=1">'
    + '<title>' + e(title) + ' — DEEPX Model Card</title><style>'
    + 'body{margin:0;background:#080c16;color:#E2E8F0;font:14px/1.6 Inter,system-ui,-apple-system,sans-serif;padding:32px}'
    + '.wrap{max-width:860px;margin:0 auto}h1{font-size:28px;margin:0 0 4px}'
    + '.cat{color:#8AACFF;font-size:13px}.sum{color:#B0BDD0;margin:12px 0 24px}'
    + 'h2{font-size:16px;color:#8AACFF;border-bottom:1px solid rgba(99,140,255,.18);padding-bottom:6px;margin:28px 0 12px}'
    + 'table{width:100%;border-collapse:collapse;margin:0 0 8px}'
    + 'th,td{text-align:left;padding:7px 10px;border-bottom:1px solid rgba(99,140,255,.1);vertical-align:top}'
    + 'th{color:#8892A8;font-weight:600;width:38%}td{word-break:break-word}a{color:#8AACFF}'
    + 'pre{background:#0e1525;border:1px solid rgba(99,140,255,.1);border-radius:8px;padding:12px;overflow-x:auto;font:12px/1.5 ui-monospace,monospace}'
    + 'footer{margin-top:28px;color:#5E6B80;font-size:12px}</style></head><body><div class="wrap">'
    + '<h1>' + e(title) + '</h1><div class="cat">' + e(task) + '</div>'
    + (summary ? '<p class="sum">' + e(summary) + '</p>' : '')
    + preview
    + ((description && description !== summary) ? ('<h2>' + e(T('Use Case & Description')) + '</h2><p class="sum">' + e(description) + '</p>') : '')
    + '<h2>' + e(T('Key Facts')) + '</h2><table>' + factRows + '</table>'
    + (techRows ? ('<h2>' + e(T('Technical')) + '</h2><table>' + techRows + '</table>') : '')
    + '<h2>' + e(T('Accuracy Matrix')) + '</h2><table>' + accRows + '</table>'
    + '<h2>' + e(T('Compile Guide')) + '</h2><table>' + cgRows + '</table>'
    + (cgNote ? '<p class="sum">' + e(cgNote) + '</p>' : '')
    + '<h2>' + e(T('Artifacts & Downloads')) + '</h2><table>' + artRows + '</table>'
    + ((cli || exP) ? ('<h2>' + e(T('Demo')) + '</h2>' + cli + exP) : '')
    + '<h2>' + e(T('Source & License')) + '</h2><table>' + legalRows + '</table>' + legalWarn
    + '<footer>Generated from DEEPX Model Zoo · ' + e(title)
    + (exportedAt ? (' · ' + e(T('Exported')) + ': ' + e(exportedAt)) : '') + '</footer>'
    + '</div></body></html>';
}

function escapeHtml(s) {
  if (s == null) return '';
  return String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function renderLegal(model) {
  const legal = model.legal || {};
  const metadataSource = _metadataSource(model);
  const sourceValue = legal.source_url
    ? (/^https?:\/\//i.test(legal.source_url)
      ? `<a href="${escapeHtml(legal.source_url)}" target="_blank" rel="noopener">${escapeHtml(legal.source_url)}</a>`
      : escapeHtml(legal.source_url))
    : _detailStatus('Not provided by source');

  const rows = [
    [T('License'), legal.license ? escapeHtml(legal.license) : _detailStatus('Not provided by source')],
    [T('Commercial use'), _commercialUseValue(legal.commercial_use)],
    [T('License text'), legal.license_text ? escapeHtml(legal.license_text) : _detailStatus('License text not provided by source')],
    [T('Copyright'), legal.copyright ? escapeHtml(legal.copyright) : _detailStatus('Not provided by source')],
    [T('Source'), sourceValue],
    [T('Source profile'), metadataSource.source_profile ? escapeHtml(metadataSource.source_profile) : _detailStatus('Metadata pending')],
    [T('Last metadata sync'), _lastMetadataSync(model) ? escapeHtml(_lastMetadataSync(model)) : _detailStatus('Metadata pending')],
  ];

  return `<div class="mz-legal-grid">
    ${rows.map(([label, value]) => `<div class="mz-legal-item">
      <h4>${escapeHtml(label)}</h4>
      <div class="mz-legal-value">${value}</div>
    </div>`).join('')}
  </div>${_commercialUseWarning(legal.commercial_use)}`;
}

function renderDownloadButtons(model, scope = 'inline') {
  const qlite = model.model_file || '';
  const qpro = model.model_file_qpro || '';
  const helpScope = escapeHtml(scope);
  let html = '';
  if (model.downloaded_qlite !== undefined || model.downloaded_qpro !== undefined) {
    if (model.downloaded_qlite) html += `<span class="mz-download-badge ready">✅ Q-Lite</span>`;
    if (model.downloaded_qpro) html += `<span class="mz-download-badge ready">✅ Q-Pro</span>`;
  } else if (model.downloaded) {
    html += `<span class="mz-download-badge ready">✓ ${T('Downloaded')}</span>`;
  }
  if (qlite && _dxAppAlive) {
    html += `<button class="mz-btn mz-btn-primary" data-model-id="${escapeHtml(model.id)}" data-quant="qlite" data-help-id="detail-download-${helpScope}-qlite">
      ⬇ ${T('Download Q-Lite')}</button>`;
  }
  if (qpro && _dxAppAlive) {
    html += `<button class="mz-btn mz-btn-outline" data-model-id="${escapeHtml(model.id)}" data-quant="qpro" data-help-id="detail-download-${helpScope}-qpro">
      ⬇ ${T('Download Q-Pro')}</button>`;
  }
  if (!_dxAppAlive) {
    html += `<span style="font-size:12px;color:var(--warning)">${T('DX App is not running. Run Inference needs the DX App module (port 8080) — launch DX AI Studio (it auto-starts DX App) or start the DX App module, then retry.')}</span>`;
  }
  return html;
}

function initDownloadButtons(container) {
  container.querySelectorAll('[data-model-id][data-quant]').forEach(btn => {
    btn.addEventListener('click', (event) => {
      downloadModel(event, btn.dataset.modelId || '', btn.dataset.quant || '');
    });
  });
}

async function downloadModel(event, modelId, quantType) {
  const btn = event.target.closest('button');
  const btnArea = btn?.parentElement;
  if (!btnArea) return;

  const statusId = `dl-status-${quantType}`;
  let statusEl = document.getElementById(statusId);
  if (!statusEl) {
    statusEl = document.createElement('div');
    statusEl.id = statusId;
    statusEl.style.cssText = 'margin-top:8px;font-size:13px';
    btnArea.appendChild(statusEl);
  }

  try {
    const resp = await fetch(modelzooApiUrl('/api/proxy/modelzoo/download'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: modelId, quant: quantType })
    });
    const data = await resp.json();
    if (!data.ok) {
      setModelZooStatusHtml(statusEl, `<span style="color:var(--error)">${T('Download failed')}: ${escapeHtml(data.error || '')}</span>`);
      return;
    }

    btn.style.display = 'none';
    setModelZooStatusHtml(statusEl, `
      <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
        <div style="flex:1;min-width:120px;height:6px;background:var(--bg-3);border-radius:3px;overflow:hidden">
          <div id="dl-bar-${quantType}" style="width:0%;height:100%;background:var(--accent);transition:width .3s"></div>
        </div>
        <span id="dl-pct-${quantType}">0%</span>
        <span style="color:var(--text-3)">${T('Downloading')}</span>
        <button class="mz-btn mz-btn-outline" style="font-size:12px;padding:2px 8px"
          data-cancel-download>✕ ${T('Cancel Download')}</button>
      </div>`);
    const cancelBtn = statusEl.querySelector('[data-cancel-download]');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', () => {
        cancelDownload(modelId, quantType);
      });
    }

    const pollId = setInterval(async () => {
      try {
        const sr = await fetch(modelzooApiUrl('/api/proxy/modelzoo/status'));
        const sd = await sr.json();
        const pct = sd.progress ?? 0;
        const bar = document.getElementById(`dl-bar-${quantType}`);
        const pctEl = document.getElementById(`dl-pct-${quantType}`);
        if (bar) bar.style.width = pct + '%';
        if (pctEl) pctEl.textContent = pct + '%';
        if (sd.status === 'complete' || pct >= 100) {
          clearInterval(pollId);
          setModelZooStatusHtml(statusEl, `<span style="color:var(--success)">✅ ${T('Download complete')}</span>`);
          btn.style.display = '';
        } else if (sd.status === 'error') {
          clearInterval(pollId);
          setModelZooStatusHtml(statusEl, `<span style="color:var(--error)">${T('Download failed')}: ${escapeHtml(sd.error || '')}</span>`);
          btn.style.display = '';
        } else if (sd.status === 'cancelled') {
          clearInterval(pollId);
          setModelZooStatusHtml(statusEl, `<span style="color:var(--text-3)">${T('Download cancelled')}</span>`);
          btn.style.display = '';
        }
      } catch (_) { /* polling error, continue */ }
    }, 2000);
  } catch (e) {
    setModelZooStatusHtml(statusEl, `<span style="color:var(--error)">${T('Download failed')}: ${escapeHtml(e.message)}</span>`);
  }
}

async function cancelDownload(modelId, quantType) {
  try {
    await fetch(modelzooApiUrl('/api/proxy/modelzoo/stop'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: modelId, quant: quantType })
    });
  } catch (_) { /* ignore */ }
}

function initBeforeAfterSliders() {
  const slider = document.getElementById('baSlider');
  const after = document.getElementById('baAfter');
  if (!slider || !after) return;

  let dragging = false;
  const container = slider.parentElement;

  function updateSlider(clientX) {
    const rect = container.getBoundingClientRect();
    let pct = ((clientX - rect.left) / rect.width) * 100;
    pct = Math.max(0, Math.min(100, pct));
    slider.style.left = pct + '%';
    after.style.clipPath = 'inset(0 ' + (100 - pct) + '% 0 0)';
  }

  let sliderRaf = null;
  let pendingClientX = null;
  function scheduleSliderUpdate(clientX) {
    pendingClientX = clientX;
    if (sliderRaf) return;
    sliderRaf = requestAnimationFrame(() => {
      sliderRaf = null;
      updateSlider(pendingClientX);
    });
  }

  slider.addEventListener('mousedown', () => { dragging = true; });
  document.addEventListener('mousemove', (e) => { if (dragging) scheduleSliderUpdate(e.clientX); });
  document.addEventListener('mouseup', () => { dragging = false; });
  slider.addEventListener('touchstart', () => { dragging = true; });
  document.addEventListener('touchmove', (e) => { if (dragging) scheduleSliderUpdate(e.touches[0].clientX); });
  document.addEventListener('touchend', () => { dragging = false; });
}

function initOverlayOpacitySliders(root) {
  const scope = root || document;
  scope.querySelectorAll('[data-overlay-opacity-target]').forEach(input => {
    if (input.dataset.overlayOpacityBound) return;
    input.dataset.overlayOpacityBound = '1';
    let overlayRaf = null;
    let pendingValue = input.value;
    function scheduleOverlayUpdate() {
      pendingValue = input.value;
      if (overlayRaf) return;
      overlayRaf = requestAnimationFrame(() => {
        overlayRaf = null;
        const target = document.getElementById(input.dataset.overlayOpacityTarget);
        if (target) target.style.opacity = Number(pendingValue) / 100;
      });
    }
    input.addEventListener('input', scheduleOverlayUpdate);
    scheduleOverlayUpdate();
  });
}
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
