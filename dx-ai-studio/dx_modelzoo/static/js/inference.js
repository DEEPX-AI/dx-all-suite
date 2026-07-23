'use strict';

/* HTML attribute escaping to prevent injection when filenames are interpolated */
function _escAttr(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

/* -----------------------------------------------------------------------
 * Execution-path selector — flatten model.variants into one dropdown.
 * value = "<lang>|<variant>"; the backend run_inference resolves the file
 * (cpp binary or python script, incl. the *_cpp_postprocess variants).
 * ---------------------------------------------------------------------- */
const _VARIANT_LABELS = {
  sync: 'Sync',
  async: 'Async',
  sync_cpp_postprocess: 'Sync · C++ postproc',
  async_cpp_postprocess: 'Async · C++ postproc',
};
const _LANG_LABELS = { cpp: 'C++', python: 'Python' };

/* -----------------------------------------------------------------------
 * Special-input categories — these models don't take a single ordinary photo
 * (image pair / point cloud / etc.), so they never ship a browsable sample
 * gallery (model.sample_dir is unset). Without an explanation the "Sample not
 * available" message reads like a bug; clarify that "Use Default" still works
 * because the built-in default input matches what the model actually expects.
 * ---------------------------------------------------------------------- */
const _SPECIAL_INPUT_MESSAGES = {
  embedding: 'This model compares an image pair (two images) instead of a single photo — that is expected, not an error. Use "Use Default" below to run it with the built-in sample.',
  reid: 'This model compares a person image pair (two person crops) instead of a single photo — that is expected, not an error. Use "Use Default" below to run it with the built-in sample.',
  object_pose_estimation: 'This model needs a specialized pose-estimation input (DOPE format), not a regular photo — that is expected, not an error. Use "Use Default" below to run it with the built-in sample.',
  '3d_object_detection': 'This model needs a LiDAR point cloud (.bin file), not a photo — that is expected, not an error. Use "Use Default" below to run it with the built-in sample.',
  hand_landmark: 'This model needs a specialized hand-landmark input, not a regular photo — that is expected, not an error. Use "Use Default" below to run it with the built-in sample.',
  hand_detection: 'This model needs a specialized hand-detection input, not a regular photo — that is expected, not an error. Use "Use Default" below to run it with the built-in sample.',
  attribute_recognition: 'This model needs a person-attribute recognition input, not a regular photo — that is expected, not an error. Use "Use Default" below to run it with the built-in sample.',
};

function _specialInputSampleMsg(category) {
  const key = _SPECIAL_INPUT_MESSAGES[category];
  return key ? T(key) : null;
}

function _buildExecPathOptions(model) {
  const v = (model && model.variants) || {};
  const opts = [];
  // reid/embedding render their pair-comparison result (similarity + SAME/DIFFERENT) only
  // in the python visualizer; the C++ runner emits no image. Offer python first (= default)
  // for those tasks so "Use Default" produces a visible result.
  const cat = model && model.category;
  const langOrder = (cat === 'reid' || cat === 'embedding') ? ['python', 'cpp'] : ['cpp', 'python'];
  langOrder.forEach(lang => {
    (v[lang] || []).forEach(variant => {
      opts.push({
        value: `${lang}|${variant}`,
        label: `${_LANG_LABELS[lang] || lang} · ${T(_VARIANT_LABELS[variant] || variant)}`,
      });
    });
  });
  return opts;
}

/* Read the chosen execution path (defaults to cpp/sync when no selector present). */
function _currentExecPath() {
  const sel = document.getElementById('infExecPath');
  const raw = (sel && sel.value) || 'cpp|sync';
  const [lang, ...rest] = raw.split('|');
  return { lang: lang || 'cpp', variant: rest.join('|') || 'sync' };
}

function renderInferencePanel(model) {
  const container = document.getElementById('inferencePanel');
  if (!container) return;

  const disabled = !_dxAppAlive;
  const disabledAttr = disabled ? 'disabled' : '';
  const disabledMsg = disabled
    ? `<p style="color:var(--warning);font-size:13px;margin-top:8px">⚠️ ${T('DX App is not running. Run Inference needs the DX App module (port 8080) — launch DX AI Studio (it auto-starts DX App) or start the DX App module, then retry.')}</p>`
    : '';
  // Inference needs the .dxnn locally. Without it the backend returns a confusing
  // "File not found" — gate the run controls and tell the user to download first.
  const isDownloaded = !!(model.downloaded_qlite || model.downloaded_qpro || model.downloaded);
  const runDisabledAttr = (disabled || !isDownloaded) ? 'disabled' : '';
  const notDownloadedMsg = (!disabled && !isDownloaded)
    ? `<p style="color:var(--warning);font-size:13px;margin-top:8px">⚠️ ${T('Download the model first to run inference.')}</p>`
    : '';
  // The image the model's representative thumbnail was generated from. "Use Default"
  // runs the demo on exactly this, so the result matches what the catalog shows.
  const demoInput = model.demo_input || '';
  const eDemo = _escAttr(demoInput);
  const samplePath = demoInput || model.sample_image || (model.example_images?.original) || '';
  const hasSampleMetadata = !!model.sample_dir;
  const sampleDisabledAttr = disabled || !hasSampleMetadata || !isDownloaded ? 'disabled' : '';
  const specialInputMsg = _specialInputSampleMsg(model.category);
  const sampleUnavailableMsg = hasSampleMetadata
    ? ''
    : `<p style="color:var(--text-3);font-size:13px;margin-top:8px">ℹ️ ${specialInputMsg || T('Sample not available for this model')}</p>`;
  const eId = _escAttr(model.id);
  const eCat = _escAttr(model.category);
  const eFile = _escAttr(model.model_file);

  // Execution-path selector (C++/Python × Sync/Async × Python/C++ postprocess).
  // Only the paths that actually exist on disk are offered (model.variants).
  const execOpts = _buildExecPathOptions(model);
  const execPathSelectHtml = execOpts.length > 1
    ? `<div class="mz-exec-path-row">
         <label class="mz-exec-path-label" for="infExecPath">⚙ ${T('Execution path')}</label>
         <select id="infExecPath" class="mz-exec-select" ${runDisabledAttr}>
           ${execOpts.map(o => `<option value="${_escAttr(o.value)}">${escapeHtml(o.label)}</option>`).join('')}
         </select>
       </div>`
    : '';

  container.innerHTML = `
    <div class="mz-inference-panel">
      <h3>🔬 ${T('Run Inference')}</h3>
      ${disabledMsg}
      ${notDownloadedMsg}
      <div class="mz-input-mode-tabs" style="margin-top:16px">
        <button class="mz-tab-btn active" id="tabUpload"
          data-model-id="${eId}" data-category="${eCat}" data-model-file="${eFile}"
          onclick="switchInferenceTabFromButton(this, 'upload')"
          ${disabledAttr}>
          📁 ${T('Upload Image')}
        </button>
        <button class="mz-tab-btn" id="tabSample"
          data-model-id="${eId}" data-category="${eCat}" data-model-file="${eFile}"
          onclick="switchInferenceTabFromButton(this, 'sample')"
          ${sampleDisabledAttr}>
          🖼 ${T('Sample Image')}
        </button>
      </div>
      ${sampleUnavailableMsg}
      ${execPathSelectHtml}

      <!-- Upload 탭 패널 -->
      <div id="tabPanelUpload" class="mz-tab-panel" style="margin-top:12px">
        <label class="mz-btn mz-btn-outline" id="inferenceUploadTrigger" data-help-id="inference-upload-trigger" style="cursor:pointer" ${runDisabledAttr}>
          📁 ${T('Choose File')}
          <input type="file" accept="image/*" id="inferenceFileInput" style="display:none"
            data-model-id="${eId}" data-category="${eCat}" data-model-file="${eFile}"
            onchange="onInferenceFileSelectedFromInput(this)"
            ${runDisabledAttr}>
        </label>
        <button class="mz-btn mz-btn-primary" id="btnRunDefault" style="margin-left:8px" ${runDisabledAttr}
          data-model-id="${eId}" data-category="${eCat}" data-model-file="${eFile}" data-demo-input="${eDemo}"
          onclick="runDefaultInferenceFromButton(this)">
          ▶ ${T('Use Default')}
        </button>
        ${samplePath ? `<p style="font-size:12px;color:var(--text-3);margin-top:8px">📷 ${T('Default sample')}: <code>${_escAttr(samplePath)}</code></p>` : ''}
      </div>

      <!-- Sample 탭 패널 -->
      <div id="tabPanelSample" class="mz-tab-panel" style="display:none;margin-top:12px">
        <div id="sampleImageGrid" class="mz-sample-grid">
          <span style="color:var(--text-3);font-size:13px">${T('Loading...')}</span>
        </div>
        <div style="margin-top:12px">
          <button class="mz-btn mz-btn-primary" id="btnRunSample" ${sampleDisabledAttr} disabled
            data-model-id="${eId}" data-category="${eCat}" data-model-file="${eFile}"
            onclick="runSampleInferenceFromButton(this)">
            ▶ ${T('Run Inference')}
          </button>
        </div>
      </div>

      <!-- 미리보기 + 결과 -->
      <div id="inferencePreviewArea" class="mz-inference-preview" style="display:none">
        <div class="mz-preview-col">
          <div class="mz-preview-label">${T('Input')}</div>
          <img id="inferenceInputPreview" src="" alt="input" style="max-width:100%">
        </div>
        <div class="mz-preview-col">
          <div class="mz-preview-label">${T('Result')}</div>
          <div id="inferenceResult"></div>
        </div>
      </div>

      <!-- Upload 모드 단독 결과 -->
      <div id="inferenceResultUpload" style="margin-top:16px"></div>
    </div>
  `;
}

/* -----------------------------------------------------------------------
 * data-attribute 기반 onclick 헬퍼 — inline JS 문자열 보간 제거
 * ---------------------------------------------------------------------- */
function switchInferenceTabFromButton(btn, tab) {
  const d = btn.dataset;
  switchInferenceTab(tab, d.modelId, d.category, d.modelFile);
}

function onInferenceFileSelectedFromInput(input) {
  const d = input.dataset;
  onInferenceFileSelected(input, d.modelId, d.category, d.modelFile);
}

function runDefaultInferenceFromButton(btn) {
  const d = btn.dataset;
  runDefaultInference(d.modelId, d.category, d.modelFile, d.demoInput);
}

function runSampleInferenceFromButton(btn) {
  const d = btn.dataset;
  runSampleInference(d.modelId, d.category, d.modelFile);
}

function switchInferenceTab(tab, modelId, category, modelFile) {
  const tabUpload = document.getElementById('tabUpload');
  const tabSample = document.getElementById('tabSample');
  const panelUpload = document.getElementById('tabPanelUpload');
  const panelSample = document.getElementById('tabPanelSample');
  if (!tabUpload || !tabSample) return;

  if (tab === 'sample') {
    tabUpload.classList.remove('active');
    tabSample.classList.add('active');
    if (panelUpload) panelUpload.style.display = 'none';
    if (panelSample) panelSample.style.display = '';
    loadSampleImages(modelId, category, modelFile);
  } else {
    tabSample.classList.remove('active');
    tabUpload.classList.add('active');
    if (panelSample) panelSample.style.display = 'none';
    if (panelUpload) panelUpload.style.display = '';
  }
}

async function loadSampleImages(modelId, category, modelFile) {
  const grid = document.getElementById('sampleImageGrid');
  if (!grid) return;
  grid.innerHTML = `<span style="color:var(--text-3);font-size:13px">${T('Loading...')}</span>`;

  try {
    const resp = await fetch(modelzooApiUrl(`/api/sample-images?model_id=${encodeURIComponent(modelId)}&category=${encodeURIComponent(category)}`));
    if (!resp.ok) {
      grid.innerHTML = `<span style="color:var(--text-3);font-size:13px">${T('Failed to load images')}: HTTP ${resp.status}</span>`;
      return;
    }
    const data = await resp.json();
    if (!data.ok || !data.images || data.images.length === 0) {
      grid.innerHTML = `<span style="color:var(--text-3);font-size:13px">${T('No sample images available')}</span>`;
      return;
    }

    if (!data.sample_dir) {
      const specialInputMsg = _specialInputSampleMsg(category);
      grid.innerHTML = `<span style="color:var(--text-3);font-size:13px">${specialInputMsg || T('Sample not available for this model')}</span>`;
      return;
    }
    const sampleDir = data.sample_dir;
    grid.innerHTML = data.images.map(fname => {
      const isDefault = fname === data.default;
      const escaped = _escAttr(fname);
      return `<div class="mz-sample-thumb${isDefault ? ' selected' : ''}"
                   data-filename="${escaped}"
                   data-sample-dir="${_escAttr(sampleDir)}"
                   onclick="onSampleThumbClick(this)">
        <img src="${modelzooApiUrl(`/api/sample-image/${encodeURIComponent(fname)}`)}" alt="${escaped}"
             loading="lazy" title="${escaped}">
        <span class="mz-thumb-name">${escaped}</span>
      </div>`;
    }).join('');

    if (data.default) {
      const defaultThumb = grid.querySelector(`[data-filename="${CSS.escape(data.default)}"]`);
      if (defaultThumb) {
        _selectSampleThumb(defaultThumb);
      }
    }
  } catch (e) {
    grid.innerHTML = `<span style="color:var(--error);font-size:13px">${T('Failed to load images')}: ${escapeHtml(String(e.message))}</span>`;
  }
}

function _selectSampleThumb(thumb) {
  thumb.closest('.mz-sample-grid')?.querySelectorAll('.mz-sample-thumb').forEach(t => {
    t.classList.remove('selected');
  });
  thumb.classList.add('selected');

  const preview = document.getElementById('inferenceInputPreview');
  const previewArea = document.getElementById('inferencePreviewArea');
  if (preview) {
    preview.src = modelzooApiUrl(`/api/sample-image/${encodeURIComponent(thumb.dataset.filename)}`);
  }
  if (previewArea) previewArea.style.display = 'flex';

  const runBtn = document.getElementById('btnRunSample');
  if (runBtn) runBtn.disabled = false;

  clearInferenceResults();
}

function onSampleThumbClick(thumb) {
  _selectSampleThumb(thumb);
}

async function runSampleInference(modelId, category, modelFile) {
  const selected = document.querySelector('.mz-sample-thumb.selected');
  if (!selected) return;
  const filename = selected.dataset.filename;
  const sampleDir = selected.dataset.sampleDir;
  if (!sampleDir) return;
  await runInference(modelId, category, modelFile, `${sampleDir}/${filename}`, null, true);
}

async function onInferenceFileSelected(input, modelId, category, modelFile) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async (e) => {
    const base64 = e.target.result.split(',')[1];
    await runInference(modelId, category, modelFile, null, base64, false);
  };
  reader.readAsDataURL(file);
}

async function runDefaultInference(modelId, category, modelFile, demoInput) {
  // Pass the catalog's representative image so the demo reproduces the shown result.
  // Falls back to the backend's own default when the model has no flat-file sample.
  await runInference(modelId, category, modelFile, demoInput || null, null, false);
}

function clearInferenceResults() {
  const r1 = document.getElementById('inferenceResult');
  const r2 = document.getElementById('inferenceResultUpload');
  if (r1) r1.innerHTML = '';
  if (r2) r2.innerHTML = '';
}

/* -----------------------------------------------------------------------
 * runInference — 공통 inference 실행
 * isSample: true → #inferenceResult (preview area)
 *           false → #inferenceResultUpload (upload area)
 * ---------------------------------------------------------------------- */
async function runInference(modelId, category, modelFile, imagePath, imageBase64, isSample) {
  const resultDivId = isSample ? 'inferenceResult' : 'inferenceResultUpload';
  const resultDiv = document.getElementById(resultDivId);
  if (!resultDiv) return;

  clearInferenceResults();

  resultDiv.innerHTML = `<div style="display:flex;align-items:center;gap:8px">
    <div class="mz-spinner"></div> ${T('Running...')}
  </div>`;

  try {
    const { lang, variant } = _currentExecPath();
    const body = {
      model_name: modelId,
      category: category,
      model_file: modelFile,
      lang: lang,
      variant: variant,
      input_type: 'image',
      save_output: false,
    };
    if (imageBase64) body.image_base64 = imageBase64;
    if (imagePath) body.image_path = imagePath;

    const resp = await fetch(modelzooApiUrl('/api/proxy/inference'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await resp.json();

    const dxAppUnavailable = ((!data.ok && data.code === 'DX_APP_UNAVAILABLE') ||
      data.error === 'DX_APP_UNAVAILABLE');
    if (dxAppUnavailable) {
      resultDiv.innerHTML = `<p style="color:var(--error)">⚠️ ${T('DX App is not running. Run Inference needs the DX App module (port 8080) — launch DX AI Studio (it auto-starts DX App) or start the DX App module, then retry.')}</p>`;
      _dxAppAlive = false;
      document.getElementById('dxAppStatus')?.classList.remove('alive');
      return;
    }

    if (data.error) {
      const msg = /dx_postprocess/.test(String(data.error))
        ? `⚠️ ${T('This path needs the dx_postprocess module (C++ postprocess), which is not installed. Build it in dx_app or pick another execution path.')}`
        : `${T('Inference failed')}: ${escapeHtml(String(data.error))}`;
      resultDiv.innerHTML = `<p style="color:var(--error)">${msg}</p>`;
      return;
    }

    let html = '<div class="mz-inference-result">';
    const hasImage = !!(data.result_image || data.image);
    if (hasImage) {
      const imgSrc = `data:image/jpeg;base64,${data.result_image || data.image}`;
      html += `<img src="${imgSrc}" alt="Result" style="max-width:100%">`;
    }
    // Tasks with no output image (classification, depth, pose, ...) return their result as
    // task_last_pred (human-readable list) / task_summary (aggregated). Render it so the user
    // sees the actual prediction instead of an empty result.
    const preds = Array.isArray(data.task_last_pred) ? data.task_last_pred.filter(Boolean) : [];
    if (!hasImage && preds.length) {
      const tagLabel = data.task_tag ? `<div class="mz-pred-tag">${escapeHtml(String(data.task_tag))}</div>` : '';
      html += `<div class="mz-pred-list">${tagLabel}` +
        preds.map(p => `<div class="mz-pred-item">${escapeHtml(String(p))}</div>`).join('') +
        `</div>`;
    } else if (!hasImage && data.task_summary && typeof data.task_summary === 'object' && Object.keys(data.task_summary).length) {
      const rows = Object.entries(data.task_summary).map(([k, v]) => {
        const conf = (v && typeof v === 'object' && v.conf_avg != null) ? ` (${(v.conf_avg * 100).toFixed(1)}%)` : '';
        return `<div class="mz-pred-item">${escapeHtml(String(k))}${escapeHtml(conf)}</div>`;
      });
      html += `<div class="mz-pred-list">${rows.join('')}</div>`;
    } else if (!hasImage) {
      // Ran successfully but produced neither image nor parseable predictions.
      html += `<p style="color:var(--text-3)">${data.exit_code === 0 ? T('Inference completed (no visual output for this task).') : T('No result produced.')}</p>`;
    }
    html += '</div>';
    if (data.fps) escapeHtml(String(data.fps));
    if (data.latency) escapeHtml(String(data.latency));
    if (data.task_tags) escapeHtml(String(data.task_tags));
    // Common-format performance summary that every C++/Python example emits
    // (PERFORMANCE SUMMARY pipeline: Read/Preprocess/Inference/Postprocess + Overall FPS),
    // already parsed by the backend into data.perf. Falls back to the fps/latency line.
    html += _renderPerfBlock(data);

    resultDiv.innerHTML = html;
    if (!isSample) {
      const previewArea = document.getElementById('inferencePreviewArea');
      if (previewArea) previewArea.style.display = 'none';
    }

    if (isSample) {
      const previewArea = document.getElementById('inferencePreviewArea');
      if (previewArea) previewArea.style.display = 'flex';
    }
  } catch (e) {
    resultDiv.innerHTML = `<p style="color:var(--error)">${T('Inference failed')}: ${escapeHtml(String(e.message))}</p>`;
  }
}

/* -----------------------------------------------------------------------
 * _renderPerfBlock — render the common-format PERFORMANCE SUMMARY.
 * Uses data.perf (per-stage pipeline) when present; otherwise the fps/latency line.
 * ---------------------------------------------------------------------- */
function _renderPerfBlock(data) {
  const perf = data && data.perf;
  const pipeline = (perf && Array.isArray(perf.pipeline)) ? perf.pipeline : [];

  let summary = '<div class="mz-inference-stats">';
  if (perf && perf.overall_fps) {
    summary += `<div>${T('Overall FPS')}: <span class="stat-value">${escapeHtml(String(perf.overall_fps))}</span></div>`;
  } else if (data.fps) {
    summary += `<div>${T('FPS')}: <span class="stat-value">${escapeHtml(String(data.fps))}</span></div>`;
  }
  if (data.latency) summary += `<div>${T('Latency')}: <span class="stat-value">${escapeHtml(String(data.latency))}ms</span></div>`;
  if (perf && perf.total_frames) summary += `<div>${T('Frames')}: <span class="stat-value">${escapeHtml(String(perf.total_frames))}</span></div>`;
  summary += '</div>';

  if (!pipeline.length) return summary;

  const rows = pipeline.map(s => {
    const asyncBadge = s.is_async ? ` <span class="mz-perf-async">async</span>` : '';
    const lat = (s.latency_ms != null) ? `${s.latency_ms} ms` : '—';
    const tput = (s.throughput_fps != null) ? `${s.throughput_fps} FPS` : '—';
    return `<tr><th>${escapeHtml(String(s.step))}${asyncBadge}</th>
      <td>${escapeHtml(lat)}</td><td>${escapeHtml(tput)}</td></tr>`;
  }).join('');

  const table = `<table class="mz-perf-table">
    <thead><tr><th>${T('Stage')}</th><th>${T('Latency')}</th><th>${T('Throughput')}</th></tr></thead>
    <tbody>${rows}</tbody></table>`;

  return summary + `<details class="mz-perf-details" open>
    <summary>${T('Performance pipeline')}</summary>${table}</details>`;
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
