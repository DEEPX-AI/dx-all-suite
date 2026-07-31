/* ===== Constants ===== */
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
// Shared ORT explanation (ONNX Runtime CPU-offload) — used by filter labels + table headers.
var ORT_TIP = "ORT (ONNX Runtime)\n- ON: model's CPU part offloaded to host CPU via ONNX Runtime → output matches the source ONNX (standard post-processing).\n- OFF: NPU-only output → needs a model-specific post-processor.";
// NPU % means two different things by metric family (see methodology note).
var UTIL_TIP = "NPU core utilization sampled by dxtop during the run, averaged over the measurement window (sustained load).";
var OCC_TIP = "NPU occupancy = NPU compute time / total frame time (from the profiler). Latency is a sub-second single-core run that dxtop's ~1 Hz sampler cannot measure, so occupancy is derived from profiler timing instead.";
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
  { key: 'capacity', title: 'Max Channel Trend', metricLabel: 'Max Channel', axisLabel: 'Max Channel', resultKind: 'e2e_multi_capacity', valueKey: 'capacity_streams', precision: 0 },
];
// Two conceptual groups for the Version Trend small-multiples: model-inference metrics (NPU is
// the bottleneck, though inference still uses some host/CPU offload) vs. host+NPU end-to-end
// pipeline metrics. Rendered as colour-coded blocks so each metric's character is obvious at a
// glance. `keys` reference TREND_METRICS entries in display order.
var TREND_GROUPS = [
  { id: 'npu',  label: 'NPU Performance',     desc: 'model inference', keys: ['latency', 'throughput'] },
  { id: 'pipe', label: 'End-to-End Pipeline', desc: 'host + NPU (decode → pre → infer → post)', input: 'FHD · 30 FPS', keys: ['e2e', 'capacity'] },
];
function _metricByKey(k){ return TREND_METRICS.filter(function(m){ return m.key === k; })[0]; }

function sizeOrd(key) { var v = SIZE_ORDER[key]; return v !== undefined ? v : 99; }

/* ===== State ===== */
var state = {
  dataset: null,
  task: 'object_detection', size: 'n', ort: true,
  selectedEnvId: null, chartData: [],
  fpsTask: 'object_detection', fpsOrt: true,
  fpsSelectedEnvId: null, fpsChartData: [],
  selectedRunIds: {},
  selectedVersion: null,
  detailEnvId: null, detailVersion: null, detailMetric: 'all', detailTask: 'object_detection', detailOrt: 'all',
  trendHwId: null, trendTask: 'object_detection', trendOrt: true,
  trendData: [], trendSelectedIdx: -1, trendCharts: [], trendRunByVersion: {},
};

/* ===== Helpers ===== */
// Input resolution per task (architectural; stable across suite versions — unlike the .dxnn
// filename, which changed between releases, so charts are captioned by config, not by filename).
var _TASK_RES = {
  object_detection: '640×640',
  pose_estimation:  '640×640',
  segmentation:     '640×640',
  oriented_bbox:    '1024×1024',
  classification:   '224×224',
};
// Worst status across a row's source metrics (non-ok surfaced so partial/failed never hides).
function _rowStatus(sts){var bad=sts.filter(function(s){return s&&s!=='ok';});if(bad.length){var uniq=[];bad.forEach(function(s){if(uniq.indexOf(s)<0)uniq.push(s);});return uniq.join(', ');}return sts.filter(function(s){return s;}).length?'ok':'-';}
function envLabel(env) { return (env.env_id || env.hw_id || env.hostname); }
function fmt(v, d) { if (v === null || v === undefined) return '-'; var n = Number(v); return Number.isNaN(n) ? '-' : n.toFixed(d === undefined ? 1 : d); }
// Tolerant fallback ONLY: prefer the stamped `size` field (version-proof).
// Handles legacy "yolo26n"/"yolo26n-cls" and new "yolo26-n_640x640" naming.
function modelSizeChar(name) { var m = String(name||'').match(/yolo26-?([nslmx])(?:[-_.]|$)/i); return m ? m[1].toLowerCase() : ''; }
function sizeOf(r) { return (r && r.size) || modelSizeChar(r && r.model); }
function formatInputShape(shape) {
  if (!shape || !Array.isArray(shape)) return '-';
  if (shape.length === 4) return shape[1] + '\u00d7' + shape[2];
  return shape.join('\u00d7');
}
function formatMemMB(mb) { if (mb == null) return '-'; return Number(mb).toFixed(1); }
function escHtml(s) { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
// Status pill shared by all result tables (E2E overview + Detailed Data) for consistent styling.
function _statusBadge(s){var st=s||'-';var sc=st==='ok'?'ok':(st==='-'?'':(st==='partial'?'warn':'bad'));return sc?'<span class="status status--'+sc+'">'+escHtml(st)+'</span>':escHtml(st);}
// Status cell shared by the E2E Overview + Detailed E2E tables: run completeness (n/req)
// and any status_reason surface in the tooltip ONLY when a run was incomplete; a clean
// run shows a bare badge. Single source of truth so both E2E tables render status alike.
function _statusCellRuns(r){var parts=[],rn=r.runs,rq=r.requested_runs;if(rn!=null&&rq!=null&&rn<rq)parts.push(rn+'/'+rq+' runs completed');if(r.status_reason)parts.push(r.status_reason);if(!parts.length)return '<td>'+_statusBadge(r.status)+'</td>';var tip=(r.status||'-')+': '+parts.join(' — ');return '<td title="'+escHtml(tip)+'">'+_statusBadge(r.status)+'</td>';}
function _fmtTemp(lo,hi){if(lo==null&&hi==null)return'-';var a=lo!=null?Math.round(lo):'?';var b=hi!=null?Math.round(hi):'?';return a===b?String(a):a+'~'+b;}
function _fmtClock(lo,hi){if(lo==null&&hi==null)return'\u2014';var a=lo!=null?Math.round(lo):'?';var b=hi!=null?Math.round(hi):'?';return a===b?String(a):a+'~'+b;}
// Single source of truth for the NPU clock cell (value + throttle badge/tooltip), shared
// by the E2E FPS Overview table and the Detailed Data tables so the tooltip never diverges.
function _clkCell(lo,hi,nom){var s=_fmtClock(lo,hi);if(lo!=null&&nom!=null&&lo<nom)s='<span class="clk-throttled" title="Clock dropped below nominal ('+Math.round(nom)+' MHz) under sustained load \u2014 throttling">'+s+'</span>';return s;}
function stripAnsi(s) { return typeof s === 'string' ? s.replace(/\x1b\[[0-9;]*m/g, '') : s; }
function _history(kind){return ((state.dataset.history||{})[kind])||((state.dataset.summaries||{})[kind])||[];}
/* ---- Annotation helpers (decoder / bound-type / thermal / SDK stack / protocol) ---- */
// HW vs SW video decoder — determines the E2E pipeline ceiling (SW decode is the bottleneck).
function _decoderKind(name){
  if(!name||name==='unknown')return null;
  var n=String(name).toLowerCase();
  if(/avdec|libav|ffdec|openh264|software/.test(n))return {kind:'SW',name:name};
  if(/vaapi|va(h264|dec)|v4l2|mpp|nvh264|nvdec|nvv4l2|d3d11|amfdec|qsv/.test(n))return {kind:'HW',name:name};
  return {kind:'?',name:name};
}
function _nominalClock(envId){var e=_envById(envId);return (e&&e.npu_clock_mhz)?e.npu_clock_mhz:1000;}
// Compact per-point SDK label for the Version Trend x-axis (full stack shows in the detail panel).
function _trendSwLabel(snap){var e=snap&&snap.environment;if(!e)return null;var rt=cleanVer(e.rt_version);return rt?('rt '+rt):null;}
// Per-metric subtitle shown directly under each Version Trend chart title: what the metric
// measures and which performance dimension it reflects (no measurement-protocol detail).
function _trendMetricSubtitle(key){
  switch(key){
    case 'latency':    return 'Single-inference latency — NPU inference speed';
    case 'throughput': return 'Inference throughput (FPS) — NPU compute performance';
    case 'e2e':        return 'Full-pipeline FPS per channel — delivered throughput';
    case 'capacity':   return 'Max concurrent channels — multi-channel scalability';
    default:           return '';
  }
}
// Concise E2E-only note for the E2E table (Latency/Throughput belong to other tables/the trend).
function _e2eNote(){
  return '<span class="measure-note"><b>E2E</b> = full pipeline (decode → pre → infer → post) · <b>sustained/warm</b></span>';
}
/* Selected-run comparisons are driven from state.dataset.history.e2e_single and friends. */
function _envById(envId){return (state.dataset.environments||[]).find(function(env){return env.env_id===envId;})||null;}
function _allSuiteVersions(){
  var seen={},out=[];
  (state.dataset.runs||[]).forEach(function(r){var v=r.dx_all_suite_version||'unknown';if(!seen[v]){seen[v]=true;out.push(v);}});
  out.sort(function(a,b){return _cmpSuiteVer(b,a);});   // _cmpSuiteVer sorts ascending; reverse for newest-first
  return out;
}
function _runsForEnvVersion(envId,version){
  var rows=(state.dataset.runs||[]).filter(function(r){return r.env_id===envId && (r.dx_all_suite_version||'unknown')===version;});
  rows.sort(function(a,b){return (b.run_id||'').localeCompare(a.run_id||'');});
  return rows;
}
function _runIdForEnvVersion(envId,version){var rows=_runsForEnvVersion(envId,version);return rows.length?rows[0].run_id:null;}
function _getRunOptions(envId){var rows=(state.dataset.runs||[]).filter(function(r){return r.env_id===envId;});rows.sort(function(a,b){return (b.run_id||'').localeCompare(a.run_id||'');});return rows;}
function _getSelectedRunId(envId){
  if(Object.prototype.hasOwnProperty.call(state.selectedRunIds,envId))return state.selectedRunIds[envId];
  var env=_envById(envId);return env?env.latest_run_id:null;
}
function _initSelectedRunIds(){
  var vers=_allSuiteVersions();
  state.selectedVersion=vers.length?vers[0]:null;                 // latest (semver desc)
  (state.dataset.environments||[]).forEach(function(env){
    state.selectedRunIds[env.env_id]=state.selectedVersion
      ? _runIdForEnvVersion(env.env_id,state.selectedVersion)
      : env.latest_run_id;
  });
}
function _applySelectedVersion(version,preferredEnvId){
  state.selectedVersion=version;
  (state.dataset.environments||[]).forEach(function(env){
    state.selectedRunIds[env.env_id]=_runIdForEnvVersion(env.env_id,version);
  });
  renderRunSelectors('fpsRunSelectors');renderRunSelectors('overviewRunSelectors');
  refreshFpsCompare(preferredEnvId);refreshChart(preferredEnvId);
}
// Populate the detail-tab version dropdown from the runs available for the selected env.
function syncDetailVersionFilter(){
  var sel=document.getElementById('detailVersionFilter');if(!sel)return;
  var envId=state.detailEnvId;var runs=envId?_getRunOptions(envId):[];
  var vers=[];runs.forEach(function(r){var v=r.dx_all_suite_version;if(v&&vers.indexOf(v)<0)vers.push(v);});
  vers.sort(function(a,b){return String(b).localeCompare(String(a));});  // newest first
  sel.innerHTML=vers.map(function(v){return '<option value="'+escHtml(v)+'">dx-all-suite '+escHtml(v)+'</option>';}).join('');
  sel.disabled=!vers.length;
  if(!state.detailVersion||vers.indexOf(state.detailVersion)<0)state.detailVersion=vers.length?vers[0]:null;
  sel.value=state.detailVersion||'';
}
function syncDetailRunFilter(){
  var sel=document.getElementById('detailRunFilter');if(!sel)return;
  var envId=state.detailEnvId;var runs=envId?_getRunOptions(envId):[];
  if(state.detailVersion)runs=runs.filter(function(r){return r.dx_all_suite_version===state.detailVersion;});
  sel.innerHTML=runs.map(function(run){return '<option value="'+escHtml(run.run_id)+'">'+escHtml(run.run_id)+'</option>';}).join('');
  sel.disabled=!runs.length;
  if(runs.length){var cur=_getSelectedRunId(envId);var ok=runs.some(function(r){return r.run_id===cur;});sel.value=ok?cur:runs[0].run_id;state.selectedRunIds[envId]=sel.value;}
}
function _handleRunSelectionChange(envId,runId){state.selectedRunIds[envId]=runId;refreshFpsCompare(envId);refreshChart(envId);if(state.detailEnvId===envId){syncDetailRunFilter();renderDetailTables();}}
function renderRunSelectors(targetId){
  var target=document.getElementById(targetId);if(!target)return;
  var envs=state.dataset.environments||[];
  if(!envs.length){target.innerHTML='<p class="empty-state small">No environments available.</p>';return;}
  var vers=_allSuiteVersions();
  var verOpts=vers.map(function(v){return '<option value="'+escHtml(v)+'"'+(v===state.selectedVersion?' selected':'')+'>'+escHtml(v)+'</option>';}).join('');
  var items=envs.map(function(env){
    var name=escHtml(env.env_id||env.hostname);
    var runs=_runsForEnvVersion(env.env_id,state.selectedVersion);
    if(!runs.length){
      return '<span class="run-inline-item run-inline-missing">'+name+' · (no '+escHtml(state.selectedVersion||'?')+')</span>';
    }
    var cur=_getSelectedRunId(env.env_id);
    var opts=runs.map(function(r){return '<option value="'+escHtml(r.run_id)+'"'+(r.run_id===cur?' selected':'')+'>'+escHtml(r.run_id)+'</option>';}).join('');
    return '<label class="run-inline-item"><span class="run-inline-name">'+name+'</span><select class="env-run-select" data-run-env="'+escHtml(env.env_id)+'">'+opts+'</select></label>';
  }).join('');
  target.innerHTML='<label class="ubar-field"><span>dx-all-suite version</span><select data-version-select>'+verOpts+'</select></label><span class="run-inline-label">Run per environment</span><div class="run-inline">'+items+'</div>';
  var vsel=target.querySelector('select[data-version-select]');
  if(vsel)vsel.addEventListener('change',function(){_applySelectedVersion(this.value);});
  target.querySelectorAll('select[data-run-env]').forEach(function(sel){
    sel.addEventListener('change',function(){_handleRunSelectionChange(this.dataset.runEnv,this.value);});
  });
}

/* ===== Dataset ===== */
function loadEmbeddedDataset() {
  var el = document.getElementById('embedded-dataset'); if (!el) return null;
  try { var t = el.textContent.trim(); return (!t || t === '__DATASET_JSON__') ? null : JSON.parse(t); } catch(e) { return null; }
}
async function loadDataset() {
  var ds = loadEmbeddedDataset(); if (ds) return ds;
  var r = await fetch('dataset.json'); if (r.ok) return r.json();
  throw new Error('Cannot load dataset.');
}

/* ===== Environment Info Renderer ===== */
function _infoRows(r) { return r.map(function(row) { return '<div class="info-row"><span class="info-key">'+escHtml(row[0])+'</span><span class="info-val">'+escHtml(String(row[1]||'-'))+'</span></div>'; }).join(''); }
function cleanVer(v) { if (typeof v !== 'string') return v; return v.replace(/^DXRT\s+/i,'').replace(/\+.*$/,'').replace(/-dirty$/,'').replace(/-\d+-g[0-9a-f]+$/,'').replace(/^v(?=\d)/i,''); }
function renderHostInfo(el, env) {
  var rows = [['Hostname',env.hostname],['OS',env.os],['Kernel',env.kernel],['Architecture',env.arch],['CPU',env.cpu],['CPU Cores',env.cpu_count],['RAM',env.ram_gb?env.ram_gb+' GB':'-']];
  el.innerHTML = _infoRows(rows);
}
function renderToolsInfo(el, env) {
  var rows = [['DX-Benchmark',cleanVer(env.benchmark_tool_version)||'-'],['DX-Stream',cleanVer(env.dx_stream_version)||'-'],['GStreamer',cleanVer(env.gstreamer_version)||'-']];
  el.innerHTML = _infoRows(rows);
}
function renderNpuInfo(el, env) {
  var rows = [['NPU',env.npu_product||env.npu_sku||'-'],['Product',env.npu_sku||'-'],['DXRT',cleanVer(env.rt_version)],['RT Driver',cleanVer(env.rt_driver)],['PCIe Driver',cleanVer(env.pcie_driver)],['Firmware',cleanVer(env.firmware)],['Clock',env.npu_clock_mhz?env.npu_clock_mhz+' MHz':'-'],['Memory',env.memory],['Board',(env.board && env.board !== 'unknown') ? env.board : '-'],['PCIe',env.pcie]];
  el.innerHTML = _infoRows(rows);
}

/* ===== Model Metadata (single task) ===== */
function renderModelMetaForTask(container, env, task) {
  var models = (env.benchmarked_models || []).filter(function(m) { return m.task === task; });
  if (!models.length) { container.innerHTML = '<p class="empty-state small">No data for this task.</p>'; return; }
  models.sort(function(a,b) { return sizeOrd(a.size) - sizeOrd(b.size); });
  var html = '<table class="summary-table bench-table"><colgroup><col style="width:34%"><col style="width:8%"><col style="width:14%"><col style="width:14%"><col style="width:15%"><col style="width:15%"></colgroup><thead><tr><th>Model</th><th>Size</th><th>Input</th><th>NPU Mem (MB)</th><th>DXNN Format</th><th>DX-COM</th></tr></thead><tbody>';
  models.forEach(function(m) {
    var input = formatInputShape(m.input_tensor_shape || m.input_size);
    var mem = formatMemMB(m.total_memory_mb);
    html += '<tr><td>' + escHtml(m.name||'-') + '</td><td>' + (m.size||'-').toUpperCase() + '</td><td>' + input + '</td><td>' + mem + '</td><td>' + escHtml(stripAnsi(m.format_version)||'-') + '</td><td>' + escHtml(stripAnsi(m.dxcom_version)||'-') + '</td></tr>';
  });
  html += '</tbody></table>';
  container.innerHTML = html;
}

/* Concise decode-path summary (Codec | Decoder SW/HW | perf flags) from pipeline_caps.
   Shared by the E2E FPS Overview tab and the Detailed Data E2E card for a consistent look. */
function _decodePathSummary(rows){
  var caps=null;for(var ci=0;ci<rows.length;ci++){if(rows[ci].pipeline_caps){caps=rows[ci].pipeline_caps;break;}}
  if(!caps)return '';
  var parts=[];
  if(caps.video_codec)parts.push('<b>Codec:</b> '+escHtml(caps.video_codec));
  var decName=null;for(var di=0;di<rows.length;di++){if(rows[di].decoder&&rows[di].decoder!=='unknown'){decName=rows[di].decoder;break;}}
  if(decName){var _dk=_decoderKind(decName);var _dtip=_dk?(_dk.kind==='HW'?'Hardware-accelerated video decode — offloads decoding from the host CPU to dedicated video hardware':(_dk.kind==='SW'?'Software video decode on the host CPU':'Video decode backend')):'';var _db=_dk?(' <span class="tag tag--'+(_dk.kind==='SW'?'sw':(_dk.kind==='HW'?'hw':'warn'))+'" title="'+escHtml(_dtip)+'">'+_dk.kind+'</span>'):'';parts.push('<b>Decoder:</b> '+escHtml(decName)+_db);}
  var _df=caps.decoder_src_format,_pf=caps.dxpreprocess_sink_format;
  if(_df&&_pf&&_df!==_pf)parts.push('<b>Color space:</b> '+escHtml(_df)+'→'+escHtml(_pf)+' <span class="tag tag--warn" title="decoder output and preprocess input formats differ → color-convert inserted (CPU cost)">convert</span>');
  var _dm=caps.decoder_src_memory,_pm=caps.dxpreprocess_sink_memory;
  if(_dm&&_dm!=='None'&&(!_pm||_pm==='None'))parts.push('<b>Memory:</b> '+escHtml(_dm)+' → system RAM <span class="tag tag--warn" title="Decoder outputs VA-API surfaces (not system RAM); each frame is copied to system RAM for preprocessing — an extra copy a software decoder avoids.">extra copy</span>');
  if(caps.dxpreprocess_backend)parts.push('<b>Preprocess Backend:</b> '+escHtml(caps.dxpreprocess_backend));
  return '<p class="decode-path-summary">'+parts.join(' &nbsp;|&nbsp; ')+'</p>';
}

/* ===== E2E Results Table ===== */
function renderE2eTable(container, envId, task, useOrt, runId) {
  var rows = _history('e2e_single').filter(function(r) {
    return r.env_id === envId && r.run_id===runId && r.task === task && r.use_ort === useOrt;
  });
  rows.sort(function(a,b) { return sizeOrd(sizeOf(a)) - sizeOrd(sizeOf(b)); });
  if (!rows.length) { container.innerHTML = '<p class="empty-state">No E2E data for this selection.</p>'; return; }

  var html = '';
  var _nomClk = _nominalClock(envId);
  /* caption (what the table shows) under the title; then the per-environment decode path,
     right above the table. */
  html += '<div class="table-caption">'+_e2eNote()+'</div>';
  html += _decodePathSummary(rows);

  html += '<table class="summary-table"><thead><tr><th>Model</th><th>E2E FPS</th><th>CPU%</th><th>NPU Avg% <span class="ort-info" title="'+UTIL_TIP+'">\u24d8</span></th><th>NPU Max%</th><th>NPU Temp \u00b0C</th><th>NPU MHz</th><th>Host RSS (MiB)</th><th>Status</th></tr></thead><tbody>';
  rows.forEach(function(r) {
    var fpsS=fmt(r.avg_e2e_fps,1);if(r.fps_std!=null)fpsS+=' <span class="detail-std">\u00b1'+fmt(r.fps_std,1)+'</span>';
    var tempS=_fmtTemp(r.npu_temp_min_c,r.npu_temp_max_c);
    var clkS=_clkCell(r.npu_clock_mhz_min,r.npu_clock_mhz_max,_nomClk);
    html += '<tr><td>'+escHtml(r.model)+'</td><td class="metric-primary">'+fpsS+'</td><td>'+fmt(r.avg_cpu_pct,0)+'</td><td>'+fmt(r.npu_total_avg_pct,1)+'</td><td>'+fmt(r.npu_total_max_pct,1)+'</td><td>'+tempS+'</td><td>'+clkS+'</td><td>'+fmt(r.max_rss_mib,0)+'</td>'+_statusCellRuns(r)+'</tr>';
  });
  html += '</tbody></table>';
  container.innerHTML = html;
}

/* ===== Full Metrics Chart (pure Canvas) ===== */
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
    this._canvas.width=w*dpr; this._canvas.height=h*dpr;
    this._canvas.style.width=w+'px'; this._canvas.style.height=h+'px';
    this._canvas.getContext('2d').scale(dpr,dpr); this._scheduleDraw();
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
    var data=this._data,cv=this._canvas,ctx=cv.getContext('2d');var lay=this._layout();var W=lay.W,H=lay.H,P=lay.P,CW=lay.CW,CH=lay.CH;ctx.clearRect(0,0,W,H);
    if(!data.length){ctx.fillStyle='#888';ctx.font='14px sans-serif';ctx.textAlign='center';ctx.fillText('No data for this selection',W/2,H/2);return;}
    var sc=this._scales(data);var fpsCeil=sc.fpsCeil,latCeil=sc.latCeil;
    var n=data.length,gW=CW/n,bW=gW*0.34;
    var fpsY=function(v){return P.top+CH-(v/fpsCeil)*CH;};var latY=function(v){return P.top+CH-(v/latCeil)*CH;};
    var gX=function(i){return P.left+i*gW+gW*0.1;};var midX=function(i){return P.left+i*gW+gW*0.5;};
    var C_TP={fill:'rgba(91,141,239,0.60)',hi:'rgba(91,141,239,0.90)',line:'rgb(91,141,239)',dim:'rgba(91,141,239,0.25)'};
    var C_E2E={fill:'rgba(46,204,113,0.60)',hi:'rgba(46,204,113,0.90)',line:'rgb(46,204,113)',dim:'rgba(46,204,113,0.25)'};
    var C_LAT='rgb(231,76,60)';var C_MAX='rgb(136,84,208)';var self=this;
    /* Grid */ctx.strokeStyle='rgba(0,0,0,0.065)';ctx.lineWidth=1;for(var g=0;g<=5;g++){var gy=P.top+CH*g/5;ctx.beginPath();ctx.moveTo(P.left,gy);ctx.lineTo(P.left+CW,gy);ctx.stroke();}
    /* Axes */ctx.strokeStyle='rgba(0,0,0,0.18)';ctx.lineWidth=1.5;[[P.left,P.top,P.left,P.top+CH],[P.left,P.top+CH,P.left+CW,P.top+CH],[P.left+CW,P.top,P.left+CW,P.top+CH]].forEach(function(l){ctx.beginPath();ctx.moveTo(l[0],l[1]);ctx.lineTo(l[2],l[3]);ctx.stroke();});
    /* Y left */ctx.textAlign='right';for(var t=0;t<=5;t++){var tv=fpsCeil*(5-t)/5,ty=P.top+CH*t/5;ctx.fillStyle='#444';ctx.font='11px sans-serif';ctx.fillText(Math.round(tv),P.left-6,ty+4);}
    /* Y right */ctx.textAlign='left';for(var t2=0;t2<=5;t2++){var tv2=latCeil*(5-t2)/5,ty2=P.top+CH*t2/5;ctx.fillStyle=C_LAT;ctx.font='11px sans-serif';ctx.fillText(Math.round(tv2),P.left+CW+8,ty2+4);}
    /* Axis titles */
    ctx.save();ctx.fillStyle='#333';ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.translate(14,P.top+CH/2);ctx.rotate(-Math.PI/2);ctx.fillText('FPS',0,0);ctx.restore();
    ctx.save();ctx.fillStyle=C_LAT;ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.translate(W-14,P.top+CH/2);ctx.rotate(Math.PI/2);ctx.fillText('Latency (ms)',0,0);ctx.restore();
    /* Bars */
    data.forEach(function(d,i){
      var sel=d.envId===self._selectedId;var hi=sel||i===self._hoverIdx;
      if(d.missing){var mgx=P.left+i*gW;ctx.save();ctx.fillStyle='rgba(0,0,0,0.045)';ctx.fillRect(mgx+2,P.top,gW-4,CH);ctx.fillStyle='#9aa0a6';ctx.font='italic 11px sans-serif';ctx.textAlign='center';ctx.fillText('no '+(state.selectedVersion||'data'),mgx+gW/2,P.top+CH/2);ctx.restore();return;}
      if(d.throughput!=null){var bx=gX(i),by=fpsY(d.throughput),bh=P.top+CH-by;ctx.fillStyle=sel?C_TP.hi:(self._selectedId&&!sel?C_TP.dim:(hi?C_TP.hi:C_TP.fill));ctx.fillRect(bx,by,bW-2,bh);ctx.strokeStyle=C_TP.line;ctx.lineWidth=sel?2:1;ctx.strokeRect(bx,by,bW-2,bh);ctx.fillStyle=C_TP.line;ctx.font='bold 10px sans-serif';ctx.textAlign='center';ctx.fillText(Math.round(d.throughput),bx+(bW-2)/2,by-4);}
      if(d.e2eFps!=null){var bx2=gX(i)+bW,by2=fpsY(d.e2eFps),bh2=P.top+CH-by2;ctx.fillStyle=sel?C_E2E.hi:(self._selectedId&&!sel?C_E2E.dim:(hi?C_E2E.hi:C_E2E.fill));ctx.fillRect(bx2+1,by2,bW-2,bh2);ctx.strokeStyle=C_E2E.line;ctx.lineWidth=sel?2:1;ctx.strokeRect(bx2+1,by2,bW-2,bh2);ctx.fillStyle='#1a1a1a';ctx.font='bold 10px sans-serif';ctx.textAlign='center';ctx.fillText(Math.round(d.e2eFps),bx2+1+(bW-2)/2,by2-4);}
      if(d.maxChannels!=null&&d.e2eFps!=null){var badgeX=gX(i)+bW+(bW-2)/2;var badgeY=fpsY(d.e2eFps)-20;var txt='Max '+d.maxChannels+'ch';ctx.font='bold 9px sans-serif';var tw=ctx.measureText(txt).width;var px=4,py=2,rr=4;var rx=badgeX-tw/2-px,ry=badgeY-8-py;var rw=tw+px*2,rh=12+py*2;ctx.fillStyle='rgba(136,84,208,0.15)';ctx.beginPath();ctx.moveTo(rx+rr,ry);ctx.lineTo(rx+rw-rr,ry);ctx.quadraticCurveTo(rx+rw,ry,rx+rw,ry+rr);ctx.lineTo(rx+rw,ry+rh-rr);ctx.quadraticCurveTo(rx+rw,ry+rh,rx+rw-rr,ry+rh);ctx.lineTo(rx+rr,ry+rh);ctx.quadraticCurveTo(rx,ry+rh,rx,ry+rh-rr);ctx.lineTo(rx,ry+rr);ctx.quadraticCurveTo(rx,ry,rx+rr,ry);ctx.closePath();ctx.fill();ctx.strokeStyle=C_MAX;ctx.lineWidth=1;ctx.stroke();ctx.fillStyle=C_MAX;ctx.textAlign='center';ctx.fillText(txt,badgeX,badgeY);}
      if(sel){ctx.save();ctx.strokeStyle='rgba(27,107,88,0.8)';ctx.lineWidth=3;ctx.setLineDash([6,3]);var sx=gX(i)-4,sw=bW*2+6;ctx.strokeRect(sx,P.top,sw,CH);ctx.setLineDash([]);ctx.restore();}
    });
    /* Latency line */
    var pts=data.map(function(d,i){return{x:midX(i),y:d.latency!=null?latY(d.latency):null,v:d.latency};});
    ctx.strokeStyle=C_LAT;ctx.lineWidth=2;ctx.setLineDash([8,5]);ctx.beginPath();var started=false;
    pts.forEach(function(p){if(p.y==null)return;if(!started){ctx.moveTo(p.x,p.y);started=true;}else{ctx.lineTo(p.x,p.y);}});ctx.stroke();ctx.setLineDash([]);
    pts.forEach(function(p){if(p.y==null)return;ctx.save();ctx.translate(p.x,p.y);ctx.rotate(Math.PI/4);ctx.fillStyle=C_LAT;ctx.fillRect(-5,-5,10,10);ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.strokeRect(-5,-5,10,10);ctx.restore();ctx.fillStyle=C_LAT;ctx.font='bold 10px sans-serif';ctx.textAlign='center';ctx.fillText(p.v.toFixed(1)+' ms',p.x,p.y-14);});
    /* X labels */ctx.fillStyle='#333';data.forEach(function(d,i){var parts=d.label.split('\n'),lx=midX(i);parts.forEach(function(part,pi){ctx.font=pi===0?'600 11px sans-serif':'11px sans-serif';ctx.textAlign='center';ctx.fillText(part,lx,P.top+CH+16+pi*14);});});
    /* Legend */
    var items=[{c:C_LAT,bc:C_LAT,label:'NPU Latency (Single-Core)',line:true},{c:C_TP.fill,bc:C_TP.line,label:'NPU Throughput (Multi-Core)',line:false},{c:C_E2E.fill,bc:C_E2E.line,label:'E2E FPS (Single-Channel)',line:false},{c:C_MAX,bc:C_MAX,label:'Max Channels (\u2265 30fps)',line:false,badge:true}];
    var lx=P.left,ly=22;items.forEach(function(it){if(it.line){ctx.strokeStyle=it.c;ctx.lineWidth=2;ctx.setLineDash([6,4]);ctx.beginPath();ctx.moveTo(lx,ly);ctx.lineTo(lx+20,ly);ctx.stroke();ctx.setLineDash([]);ctx.save();ctx.translate(lx+10,ly);ctx.rotate(Math.PI/4);ctx.fillStyle=it.c;ctx.fillRect(-4,-4,8,8);ctx.restore();}else if(it.badge){ctx.fillStyle='rgba(136,84,208,0.15)';ctx.fillRect(lx,ly-7,18,14);ctx.strokeStyle=it.bc;ctx.lineWidth=1;ctx.strokeRect(lx,ly-7,18,14);ctx.fillStyle=it.c;ctx.font='bold 8px sans-serif';ctx.textAlign='center';ctx.fillText('ch',lx+9,ly+3);}else{ctx.fillStyle=it.c;ctx.fillRect(lx,ly-7,18,14);ctx.strokeStyle=it.bc;ctx.lineWidth=1;ctx.strokeRect(lx,ly-7,18,14);}ctx.fillStyle='#333';ctx.font='12px sans-serif';ctx.textAlign='left';ctx.fillText(it.label,lx+24,ly+4);lx+=ctx.measureText(it.label).width+44;});
  },
  _hitTest: function(e){var rect=this._canvas.getBoundingClientRect();var x=e.clientX-rect.left;var lay=this._layout();if(x<lay.P.left||x>lay.P.left+lay.CW||!this._data.length)return -1;return Math.min(Math.floor((x-lay.P.left)/(lay.CW/this._data.length)),this._data.length-1);},
  _handleClick: function(e){var i=this._hitTest(e);if(i>=0&&this._onClick)this._onClick(i,this._data[i]);},
  _handleHover: function(e){var i=this._hitTest(e);if(i!==this._hoverIdx){this._hoverIdx=i;this._canvas.style.cursor=i>=0?'pointer':'default';this._scheduleDraw();}},
  _handleLeave: function(){this._hoverIdx=-1;this._canvas.style.cursor='default';this._scheduleDraw();},
};

/* ===== FPS Compare Chart ===== */
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
  _resize: function(){var el=this._canvas.parentElement,dpr=window.devicePixelRatio||1;var w=el.clientWidth,h=el.clientHeight;this._canvas.width=w*dpr;this._canvas.height=h*dpr;this._canvas.style.width=w+'px';this._canvas.style.height=h+'px';this._canvas.getContext('2d').scale(dpr,dpr);this._scheduleDraw();},
  _scheduleDraw: function(){var s=this;if(s._raf)cancelAnimationFrame(s._raf);s._raf=requestAnimationFrame(function(){s._draw();});},
  _layout: function(){var dpr=window.devicePixelRatio||1;var W=this._canvas.width/dpr,H=this._canvas.height/dpr;var P={top:55,right:30,bottom:90,left:72};return {W:W,H:H,P:P,CW:W-P.left-P.right,CH:H-P.top-P.bottom};},
  _niceMax: function(v){if(v<=0)return 10;var e=Math.pow(10,Math.floor(Math.log10(v)));var f=v/e;return (f<=1.5?2:f<=3?4:f<=6?8:10)*e;},
  _draw: function() {
    var data=this._data,cv=this._canvas,ctx=cv.getContext('2d');var lay=this._layout();
    var W=lay.W,H=lay.H,P=lay.P,CW=lay.CW,CH=lay.CH;ctx.clearRect(0,0,W,H);
    if(!data.length){ctx.fillStyle='#888';ctx.font='14px sans-serif';ctx.textAlign='center';ctx.fillText('No data for this selection',W/2,H/2);return;}
    /* Adaptive Y-axis */
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
    /* Max channels lookup */
    var capMap={};
    _history('e2e_multi_capacity').forEach(function(r){
      if(r.use_ort!==state.fpsOrt)return;if((r.task||'')!==state.fpsTask)return;
      if(r.run_id!==_getSelectedRunId(r.env_id))return;
      var sz=sizeOf(r);
      var k=r.env_id+'|'+sz;
      if(!capMap[k]||r.capacity_streams>capMap[k])capMap[k]=r.capacity_streams;
    });
    /* Grid */ctx.strokeStyle='rgba(0,0,0,0.065)';ctx.lineWidth=1;for(var g=0;g<=5;g++){var gy=P.top+CH*g/5;ctx.beginPath();ctx.moveTo(P.left,gy);ctx.lineTo(P.left+CW,gy);ctx.stroke();}
    /* Axes */ctx.strokeStyle='rgba(0,0,0,0.18)';ctx.lineWidth=1.5;[[P.left,P.top,P.left,P.top+CH],[P.left,P.top+CH,P.left+CW,P.top+CH]].forEach(function(l){ctx.beginPath();ctx.moveTo(l[0],l[1]);ctx.lineTo(l[2],l[3]);ctx.stroke();});
    /* Y ticks */ctx.textAlign='right';ctx.fillStyle='#444';ctx.font='11px sans-serif';
    for(var t=0;t<=5;t++){var tv=fpsCeil-(fpsCeil-floor)*t/5,ty=P.top+CH*t/5;ctx.fillText(Math.round(tv),P.left-6,ty+4);}
    /* Y title */ctx.save();ctx.fillStyle='#333';ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.translate(14,P.top+CH/2);ctx.rotate(-Math.PI/2);ctx.fillText('E2E FPS',0,0);ctx.restore();
    /* Bars */
    data.forEach(function(d,i){
      var sel=d.envId===self._selectedId;var hi=sel||i===self._hoverIdx;
      if(d.missing){var mgx=P.left+i*gW;ctx.save();ctx.fillStyle='rgba(0,0,0,0.045)';ctx.fillRect(mgx+2,P.top,gW-4,CH);ctx.fillStyle='#9aa0a6';ctx.font='italic 11px sans-serif';ctx.textAlign='center';ctx.fillText('no '+(state.selectedVersion||'data'),mgx+gW/2,P.top+CH/2);ctx.restore();return;}
      SIZE_KEYS.forEach(function(sz,si){
        var v=d.sizes[sz];if(v==null)return;
        var bx=gX(i,si),by=fpsY(v),bh=P.top+CH-by;var sc=SIZE_COLORS[sz];
        var barFill=sel?sc.hi:(self._selectedId&&!sel?sc.dim:(hi?sc.hi:sc.fill));
        ctx.fillStyle=barFill;ctx.fillRect(bx+1,by,subW-2,bh);
        ctx.strokeStyle=sc.line;ctx.lineWidth=sel?2:1;ctx.strokeRect(bx+1,by,subW-2,bh);
        ctx.fillStyle=sc.line;ctx.font='bold 9px sans-serif';ctx.textAlign='center';ctx.fillText(Math.round(v),bx+subW/2,by-4);
        /* Max Ch badge per size */
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
      if(sel){ctx.save();ctx.strokeStyle='rgba(27,107,88,0.9)';ctx.lineWidth=3;ctx.setLineDash([6,3]);var sx=P.left+i*gW+2;ctx.strokeRect(sx,P.top-2,gW-4,CH+4);ctx.setLineDash([]);ctx.restore();}
    });
    /* X labels */ctx.fillStyle='#333';data.forEach(function(d,i){var parts=d.label.split('\n'),lx=midX(i);parts.forEach(function(part,pi){ctx.font=pi===0?'600 11px sans-serif':'11px sans-serif';ctx.textAlign='center';ctx.fillText(part,lx,P.top+CH+16+pi*14);});});
    /* Legend */
    var lx=P.left,ly=22;
    SIZE_KEYS.forEach(function(sz){var sc=SIZE_COLORS[sz];ctx.fillStyle=sc.fill;ctx.fillRect(lx,ly-7,18,14);ctx.strokeStyle=sc.line;ctx.lineWidth=1;ctx.strokeRect(lx,ly-7,18,14);var label=sz.toUpperCase()+' ('+SIZE_LABELS[sz]+')';ctx.fillStyle='#333';ctx.font='12px sans-serif';ctx.textAlign='left';ctx.fillText(label,lx+22,ly+4);lx+=ctx.measureText(label).width+40;});
    ctx.fillStyle='rgba(136,84,208,0.12)';ctx.fillRect(lx,ly-7,18,14);ctx.strokeStyle='rgb(136,84,208)';ctx.lineWidth=1;ctx.strokeRect(lx,ly-7,18,14);ctx.fillStyle='rgb(136,84,208)';ctx.font='bold 8px sans-serif';ctx.textAlign='center';ctx.fillText('ch',lx+9,ly+3);ctx.fillStyle='#333';ctx.font='12px sans-serif';ctx.textAlign='left';ctx.fillText('Max Ch (\u2265 30fps)',lx+22,ly+4);
  },
  _hitTest: function(e){var rect=this._canvas.getBoundingClientRect();var x=e.clientX-rect.left;var lay=this._layout();if(x<lay.P.left||x>lay.P.left+lay.CW||!this._data.length)return -1;return Math.min(Math.floor((x-lay.P.left)/(lay.CW/this._data.length)),this._data.length-1);},
  _handleClick: function(e){var i=this._hitTest(e);if(i>=0&&this._onClick)this._onClick(i,this._data[i]);},
  _handleHover: function(e){var i=this._hitTest(e);if(i!==this._hoverIdx){this._hoverIdx=i;this._canvas.style.cursor=i>=0?'pointer':'default';this._scheduleDraw();}},
  _handleLeave: function(){this._hoverIdx=-1;this._canvas.style.cursor='default';this._scheduleDraw();},
};

/* ===== Chart data helpers ===== */
function getChartData() {
  var sz=state.size;var task=state.task;var useOrt=state.ort;var results=[];
  var modelRows=_history('model');var e2eRows=_history('e2e_single');var capRows=_history('e2e_multi_capacity');
  (state.dataset.environments||[]).forEach(function(env){
    var eid=env.env_id;var runId=_getSelectedRunId(eid);
    // No run at the selected suite version -> keep the env as a placeholder column
    // (drawn greyed with a "no <version>" label) instead of silently dropping it.
    if(runId==null){results.push({env:env,envId:eid,label:envLabel(env),missing:true,throughput:null,e2eFps:null,latency:null,maxChannels:null});return;}
    var tRow=modelRows.find(function(r){return r.env_id===eid&&r.run_id===runId&&r.size===sz&&r.task===task&&r.use_ort===useOrt&&r.family==='throughput';});
    var lRow=modelRows.find(function(r){return r.env_id===eid&&r.run_id===runId&&r.size===sz&&r.task===task&&r.use_ort===useOrt&&r.family==='latency';});
    var eRow=e2eRows.find(function(r){return r.env_id===eid&&r.run_id===runId&&r.size===sz&&r.task===task&&r.use_ort===useOrt;});
    var cRow=capRows.find(function(r){return r.env_id===eid&&r.run_id===runId&&r.size===sz&&r.task===task&&r.use_ort===useOrt;});
    if(tRow||eRow){results.push({env:env,envId:eid,label:envLabel(env),throughput:tRow?tRow.fps:null,e2eFps:eRow?eRow.avg_e2e_fps:null,latency:lRow?lRow.latency_ms:null,maxChannels:cRow?cRow.capacity_streams:null});}
  });
  // Real entries ascending by E2E FPS; missing-version placeholders pushed to the right.
  results.sort(function(a,b){if(!!a.missing!==!!b.missing)return a.missing?1:-1;return(a.e2eFps||0)-(b.e2eFps||0);});return results;
}
function refreshChart(preferredEnvId) {
  var data=getChartData();state.chartData=data;
  var tm=TASK_MAP[state.task]||{},res=_TASK_RES[state.task]||'';
  document.getElementById('chartSubtitle').textContent=(tm.label||state.task)+' · '+(SIZE_LABELS[state.size]||state.size)+(res?' · '+res:'')+' · ORT '+(state.ort?'ON':'OFF');
  if(!data.length){
    state.selectedEnvId=null;
    document.getElementById('overviewDetail').style.display='none';
    Chart.update(data,null);return;
  }
  var selected=null;
  if(preferredEnvId){for(var i=0;i<data.length;i++){if(data[i].envId===preferredEnvId&&!data[i].missing){selected=data[i];break;}}}
  if(!selected){for(var j=0;j<data.length;j++){if(!data[j].missing){selected=data[j];break;}}}
  if(selected){state.selectedEnvId=selected.envId;renderEnvDetail(selected.env,{scroll:false});}
  else{state.selectedEnvId=null;document.getElementById('overviewDetail').style.display='none';}
  Chart.update(data,state.selectedEnvId);
}
function getFpsCompareData() {
  var useOrt=state.fpsOrt;var task=state.fpsTask;var results=[];var e2eRows=_history('e2e_single');
  (state.dataset.environments||[]).forEach(function(env){
    var eid=env.env_id;var runId=_getSelectedRunId(eid);var sizes={};var hasAny=false;
    // No run at the selected suite version -> greyed "no <version>" placeholder column.
    if(runId==null){SIZE_KEYS.forEach(function(sz){sizes[sz]=null;});results.push({env:env,envId:eid,label:envLabel(env),sizes:sizes,missing:true});return;}
    SIZE_KEYS.forEach(function(sz){var eRow=e2eRows.find(function(r){return r.env_id===eid&&r.run_id===runId&&r.size===sz&&r.task===task&&r.use_ort===useOrt;});if(eRow){sizes[sz]=eRow.avg_e2e_fps;hasAny=true;}else{sizes[sz]=null;}});
    if(hasAny){results.push({env:env,envId:eid,label:envLabel(env),sizes:sizes});}
  });
  results.sort(function(a,b){if(!!a.missing!==!!b.missing)return a.missing?1:-1;var sum=function(d){var s=0;SIZE_KEYS.forEach(function(sz){if(d.sizes[sz]!=null)s+=d.sizes[sz];});return s;};return sum(a)-sum(b);});return results;
}
function refreshFpsCompare(preferredEnvId) {
  var data=getFpsCompareData();state.fpsChartData=data;
  document.getElementById('fpsChartSubtitle').textContent='Single Channel \u00b7 30 FPS \u00b7 FHD';
  if(!data.length){
    state.fpsSelectedEnvId=null;
    document.getElementById('fpsDetail').style.display='none';
    FpsChart.update(data,null);
    return;
  }
  var selected=null,idx=-1;
  if(preferredEnvId){for(var i=0;i<data.length;i++){if(data[i].envId===preferredEnvId&&!data[i].missing){selected=data[i];idx=i;break;}}}
  if(!selected){for(var j=0;j<data.length;j++){if(!data[j].missing){selected=data[j];idx=j;break;}}}
  if(selected){handleFpsEnvClick(idx,selected,{scroll:false});}
  else{state.fpsSelectedEnvId=null;document.getElementById('fpsDetail').style.display='none';FpsChart.update(data,null);}
}

function handleFpsEnvClick(idx,d,options) {
  options=options||{};
  if(d&&d.missing)return;
  state.fpsSelectedEnvId=d.envId;
  var panel=document.getElementById('fpsDetail');panel.style.display='';
  document.getElementById('fpsDetailTitle').textContent='Details — '+(d.env.env_id||d.env.hostname);
  renderHostInfo(document.getElementById('fpsEnvHostInfo'),d.env);
  renderNpuInfo(document.getElementById('fpsEnvNpuInfo'),d.env);
  renderToolsInfo(document.getElementById('fpsEnvToolsInfo'),d.env);
  document.getElementById('fpsModelMetaTitle').textContent='Benchmarked Models – '+TASK_MAP[state.fpsTask].label;
  renderModelMetaForTask(document.getElementById('fpsModelMetaSection'),d.env,state.fpsTask);
  var runId=_getSelectedRunId(d.envId);
  document.getElementById('fpsE2eTableTitle').textContent='E2E FPS (Single-Channel) \u2013 '+TASK_MAP[state.fpsTask].label+' \u00b7 ORT '+(state.fpsOrt?'ON':'OFF')+' \u00b7 '+runId;
  renderE2eTable(document.getElementById('fpsE2eTableContent'),d.envId,state.fpsTask,state.fpsOrt,runId);
  /* View trend link */
  var hwId=_envToHwId(d.env);
  if(hwId&&_hwIdHasSnapshots(hwId)){
    var link=document.createElement('p');link.className='trend-link';link.innerHTML='<a href="#" id="fpsTrendLink">\u2192 View version trend for this environment</a>';
    document.getElementById('fpsE2eTableContent').appendChild(link);
    document.getElementById('fpsTrendLink').addEventListener('click',function(e){e.preventDefault();_switchToTrend(hwId);});
  }
  if(options.scroll!==false){panel.scrollIntoView({behavior:'smooth',block:'nearest'});}
  FpsChart.update(state.fpsChartData,state.fpsSelectedEnvId);
}

function initFpsFilters() {
  document.getElementById('fpsTaskFilter').value=state.fpsTask;
  document.getElementById('fpsOrtFilter').value=state.fpsOrt?'on':'off';
  document.getElementById('fpsTaskFilter').addEventListener('change',function(){state.fpsTask=this.value;refreshFpsCompare();});
  document.getElementById('fpsOrtFilter').addEventListener('change',function(){state.fpsOrt=this.value==='on';refreshFpsCompare();});
}

/* ===== Environment Detail (Full Metrics) ===== */
function renderEnvDetail(env,options) {
  options=options||{};
  var panel=document.getElementById('overviewDetail');panel.style.display='';
  document.getElementById('overviewDetailTitle').textContent='Details — '+(env.env_id||env.hostname);
  renderHostInfo(document.getElementById('envHostInfo'),env);
  renderNpuInfo(document.getElementById('envNpuInfo'),env);
  renderToolsInfo(document.getElementById('envToolsInfo'),env);
  document.getElementById('overviewModelMetaTitle').textContent='Benchmarked Models – '+TASK_MAP[state.task].label;
  renderModelMetaForTask(document.getElementById('overviewModelMetaSection'),env,state.task);
  /* View trend link */
  var hwId=_envToHwId(env);
  if(hwId&&_hwIdHasSnapshots(hwId)){
    var link=document.createElement('p');link.className='trend-link';link.innerHTML='<a href="#" id="overviewTrendLink">\u2192 View version trend for this environment</a>';
    document.getElementById('overviewModelMetaSection').appendChild(link);
    document.getElementById('overviewTrendLink').addEventListener('click',function(e){e.preventDefault();_switchToTrend(hwId);});
  }
  if(options.scroll!==false)panel.scrollIntoView({behavior:'smooth',block:'nearest'});
}

/* ===== Tabs ===== */
function initTabs() {
  document.querySelectorAll('.tab').forEach(function(btn){
    btn.addEventListener('click',function(){
      var target=this.dataset.tab;
      document.querySelectorAll('.tab').forEach(function(b){b.classList.remove('active');});
      document.querySelectorAll('.tab-content').forEach(function(c){c.classList.remove('active');});
      this.classList.add('active');document.getElementById('tab-'+target).classList.add('active');
      if(target==='fps-compare'){renderRunSelectors('fpsRunSelectors');refreshFpsCompare(state.fpsSelectedEnvId);}
      else if(target==='overview'){renderRunSelectors('overviewRunSelectors');refreshChart(state.selectedEnvId);}
      if(target==='fps-compare')FpsChart._resize();
      if(target==='overview')Chart._resize();
      if(target==='detail')renderDetailTables();
      if(target==='version-trend')resizeTrendChart();
    });
  });
}

/* ===== Overview Filters ===== */
function initOverviewFilters() {
  document.getElementById('taskFilter').value=state.task;
  document.getElementById('sizeFilter').value=state.size;
  document.getElementById('ortFilter').value=state.ort?'on':'off';
  document.getElementById('taskFilter').addEventListener('change',function(){state.task=this.value;refreshChart();});
  document.getElementById('sizeFilter').addEventListener('change',function(){state.size=this.value;refreshChart();});
  document.getElementById('ortFilter').addEventListener('change',function(){state.ort=this.value==='on';refreshChart();});
}

/* ===== Detail Tab ===== */
function initDetailTab() {
  var sel=document.getElementById('detailEnvFilter');
  var verSel=document.getElementById('detailVersionFilter');
  var runSel=document.getElementById('detailRunFilter');
  sel.innerHTML=(state.dataset.environments||[]).map(function(e){return '<option value="'+e.env_id+'">'+escHtml(e.env_id||e.hostname)+'</option>';}).join('');
  if(state.dataset.environments.length){state.detailEnvId=state.dataset.environments[0].env_id;sel.value=state.detailEnvId;}
  syncDetailVersionFilter();syncDetailRunFilter();
  sel.addEventListener('change',function(){state.detailEnvId=this.value;state.detailVersion=null;syncDetailVersionFilter();syncDetailRunFilter();renderDetailTables();});
  if(verSel)verSel.addEventListener('change',function(){state.detailVersion=this.value||null;syncDetailRunFilter();renderDetailTables();});
  runSel.addEventListener('change',function(){if(state.detailEnvId)_handleRunSelectionChange(state.detailEnvId,this.value);});
  document.getElementById('detailTaskFilter').value=state.detailTask;
  document.getElementById('detailOrtFilter').value=state.detailOrt;
  document.getElementById('detailTaskFilter').addEventListener('change',function(){state.detailTask=this.value;renderDetailTables();});
  document.getElementById('detailOrtFilter').addEventListener('change',function(){state.detailOrt=this.value;renderDetailTables();});
  renderDetailTables();  // render on init (consistent with the other tabs), not only on tab-switch
}

// Detailed Data tab = the full per-run record, mirroring REPORT.md: one section per METRIC
// (each metric is a separate measurement with its own std/temp/clock/runs), grouped by task.
function renderDetailTables() {
  var target=document.getElementById('detailTables');var envId=state.detailEnvId;
  if(!envId){target.innerHTML='<div class="empty-state">No environment selected.</div>';return;}
  var _detailRuns=_getRunOptions(envId);
  var runId=_getSelectedRunId(envId)||(_detailRuns.length?_detailRuns[0].run_id:null);
  var nom=_nominalClock(envId);
  var ortF=state.detailOrt,taskF=state.detailTask,metF=state.detailMetric;
  function want(k){return metF==='all'||metF===k;}
  function ortMatch(uo){return ortF==='all'||ortF===(uo?'on':'off');}
  function collect(src,fam){var by={};_history(src).forEach(function(r){if(r.env_id!==envId||r.run_id!==runId)return;if(fam&&r.family!==fam)return;if(!ortMatch(r.use_ort))return;if(taskF!=='all'&&r.task!==taskF)return;(by[r.task]=by[r.task]||[]).push(r);});return by;}
  var thr=want('throughput')?collect('model','throughput'):{},lat=want('latency')?collect('model','latency'):{},e2e=want('e2e')?collect('e2e_single',null):{},cap=want('multi')?collect('e2e_multi_capacity',null):{};
  function taskOrd(a,b){var oa=TASK_ORDER[a],ob=TASK_ORDER[b];return(oa!==undefined?oa:99)-(ob!==undefined?ob:99);}
  function sortRows(rows){return rows.slice().sort(function(a,b){var d=sizeOrd(sizeOf(a))-sizeOrd(sizeOf(b));return d!==0?d:(a.use_ort?1:0)-(b.use_ort?1:0);});}
  function stdSpan(v,s,d){var b=fmt(v,d);if(v!=null&&s!=null)b+=' <span class="detail-std">±'+fmt(s,d)+'</span>';return b;}
  function mhzTd(r){return '<td>'+_clkCell(r.npu_clock_mhz_min,r.npu_clock_mhz_max,nom)+'</td>';}
  function stTd(s){return '<td>'+_statusBadge(s)+'</td>';}
  // Status cell with a tooltip explaining a non-ok flag (reason + which stream counts failed).
  function stTdReason(r){var reason=r.status_reason,scs=r.failed_stream_counts;if(!reason&&!(scs&&scs.length))return stTd(r.status);var scPart=(scs&&scs.length)?(' @ sc=['+scs.join(',')+']'):'';var tip=(r.status||'-')+scPart+(reason?(': '+reason):'');return '<td title="'+escHtml(tip)+'">'+_statusBadge(r.status)+'</td>';}
  function msOrt(r){return '<td>'+escHtml(r.model)+'</td><td>'+((sizeOf(r)||'-')+'').toUpperCase()+'</td><td>'+(r.use_ort?'ON':'OFF')+'</td>';}
  function section(title,sub,by,head,rowFn,preHtml,key){var tasks=Object.keys(by).sort(taskOrd);if(!tasks.length)return '';var inner=tasks.map(function(t){var body=sortRows(by[t]).map(rowFn).join('');return '<h4 class="detail-task">'+(TASK_MAP[t]?TASK_MAP[t].label:t)+'</h4><div class="table-scroll"><table class="summary-table detail-table"><thead><tr>'+head+'</tr></thead><tbody>'+body+'</tbody></table></div>';}).join('');return '<section class="detail-metric" id="dm-'+key+'"><h2 class="detail-metric-title">'+title+(sub?' <span class="detail-metric-sub">'+sub+'</span>':'')+'</h2>'+(preHtml||'')+inner+'</section>';}

  var runObj=(state.dataset.runs||[]).filter(function(r){return r.run_id===runId&&r.env_id===envId;})[0]||{};
  var dateStr=(runObj.timestamp||'').slice(0,10)||(runId||'').slice(0,8);
  // decode-path summary lives inside the E2E card (E2E-specific info), detected regardless of task/ORT filter
  var e2eRows=_history('e2e_single').filter(function(r){return r.env_id===envId&&r.run_id===runId;});

  var secThr=section('Model Throughput','multi-core, async',thr,
    '<th>Model</th><th>Size</th><th>ORT <span class="ort-info" title="'+ORT_TIP+'">ⓘ</span></th><th>FPS</th><th>CPU%</th><th>NPU Avg% <span class="ort-info" title="'+UTIL_TIP+'">ⓘ</span></th><th>NPU Max%</th><th>Temp °C</th><th>MHz</th><th>Status</th>',
    function(r){return '<tr>'+msOrt(r)+'<td class="metric-primary">'+stdSpan(r.fps,r.fps_std,1)+'</td><td>'+fmt(r.cpu_pct,0)+'</td><td>'+fmt(r.npu_total_avg_pct,1)+'</td><td>'+fmt(r.npu_total_max_pct,1)+'</td><td>'+_fmtTemp(r.npu_temp_min_c,r.npu_temp_max_c)+'</td>'+mhzTd(r)+stTd(r.status)+'</tr>';},'','throughput');
  var secLat=section('Model Latency','single-core, sync',lat,
    '<th>Model</th><th>Size</th><th>ORT <span class="ort-info" title="'+ORT_TIP+'">ⓘ</span></th><th>Latency (ms)</th><th>NPU % <span class="ort-info" title="'+OCC_TIP+'">ⓘ</span></th><th>Temp °C</th><th>Status</th>',
    function(r){return '<tr>'+msOrt(r)+'<td class="metric-primary">'+stdSpan(r.latency_ms,r.latency_ms_std,2)+'</td><td>'+fmt(r.npu_occupancy_pct,1)+'</td><td>'+_fmtTemp(r.npu_temp_min_c,r.npu_temp_max_c)+'</td>'+stTd(r.status)+'</tr>';},'','latency');
  var secE2e=section('E2E FPS (Single-Channel)','single-channel',e2e,
    '<th>Model</th><th>Size</th><th>ORT <span class="ort-info" title="'+ORT_TIP+'">ⓘ</span></th><th>E2E FPS</th><th>CPU%</th><th>NPU Avg% <span class="ort-info" title="'+UTIL_TIP+'">ⓘ</span></th><th>NPU Max%</th><th>Temp °C</th><th>MHz</th><th>Host RSS (MiB)</th><th>Status</th>',
    function(r){return '<tr>'+msOrt(r)+'<td class="metric-primary">'+stdSpan(r.avg_e2e_fps,r.fps_std,1)+'</td><td>'+fmt(r.avg_cpu_pct,0)+'</td><td>'+fmt(r.npu_total_avg_pct,1)+'</td><td>'+fmt(r.npu_total_max_pct,1)+'</td><td>'+_fmtTemp(r.npu_temp_min_c,r.npu_temp_max_c)+'</td>'+mhzTd(r)+'<td>'+fmt(r.max_rss_mib,0)+'</td>'+_statusCellRuns(r)+'</tr>';},
    _decodePathSummary(e2eRows),'e2e');
  var secMul=section('Max Channel Capacity','max channels ≥ threshold',cap,
    '<th>Model</th><th>Size</th><th>ORT <span class="ort-info" title="'+ORT_TIP+'">ⓘ</span></th><th>Max Channels</th><th>Per-Ch FPS</th><th>FPS Threshold</th><th>Status</th>',
    function(r){return '<tr>'+msOrt(r)+'<td class="metric-primary">'+(r.capacity_streams!=null?r.capacity_streams:'-')+'</td><td>'+fmt(r.capacity_per_channel_fps,1)+'</td><td>'+fmt(r.fps_threshold,0)+'</td>'+stTdReason(r)+'</tr>';},'','multi');

  // Two metric families surfaced as color-coded groups so users grasp each metric's character:
  //  · NPU Performance    — model inference (Throughput + Latency)          → green
  //  · End-to-End Pipeline — host + NPU (decode → pre → infer → post) (E2E + Max Channel) → blue
  // Ordered to match the per-model measurement sequence: latency → throughput → e2e → multi.
  var npu=[{h:secLat,id:'dm-latency',lb:'Latency'},{h:secThr,id:'dm-throughput',lb:'Throughput'}].filter(function(c){return c.h;});
  var pipe=[{h:secE2e,id:'dm-e2e',lb:'E2E'},{h:secMul,id:'dm-multi',lb:'Max Channel'}].filter(function(c){return c.h;});
  // Reuse the Version Trend tab's group chrome (.trend-group) so both tabs look identical:
  // colour-coded left border + tinted header band + subtle tint; cards stacked in a padded body.
  function grpBlock(cls,label,desc,arr,inputNote){return arr.length?'<div class="trend-group trend-group--'+cls+'"><div class="trend-group-head"><span class="trend-group-label">'+label+'</span><span class="trend-group-desc">'+desc+'</span>'+(inputNote?'<span class="trend-group-input">Input: '+inputNote+'</span>':'')+'</div><div class="detail-group-body">'+arr.map(function(c){return c.h;}).join('')+'</div></div>':'';}
  var groupsHtml=grpBlock('npu','NPU Performance','model inference',npu)
               +grpBlock('pipe','End-to-End Pipeline','host + NPU (decode → pre → infer → post)',pipe,'FHD · 30 FPS');
  if(!groupsHtml)groupsHtml='<section class="panel"><div class="empty-state">No data for this selection.</div></section>';

  // run-level context (Environment + Benchmarked Models), collapsed by default, same detail-group/detail-sub layout as other tabs
  var snap=(state.dataset.snapshots||[]).filter(function(s){return s.run_id===runId&&s.env_id===envId;})[0];
  var env=snap&&snap.environment,modelTasks=[],detailsHtml='';
  if(env){
    var dMeta=escHtml(envId)+(runObj.dx_all_suite_version?' · '+escHtml(runObj.dx_all_suite_version):'')+(dateStr?' · '+escHtml(dateStr):'');
    var envSub='<div class="detail-sub detail-sub--env"><h3 class="detail-sub-title">Environment</h3><div class="env-detail-grid env-detail-grid--3"><div class="env-detail-col"><h3>Host PC</h3><div id="detailEnvHostInfo"></div></div><div class="env-detail-col"><h3>NPU</h3><div id="detailEnvNpuInfo"></div></div><div class="env-detail-col"><h3>Tools</h3><div id="detailEnvToolsInfo"></div></div></div></div>';
    var seen={};(env.benchmarked_models||[]).forEach(function(m){if(m.task&&!seen[m.task]){seen[m.task]=1;modelTasks.push(m.task);}});
    if(taskF!=='all')modelTasks=modelTasks.filter(function(t){return t===taskF;});
    modelTasks.sort(taskOrd);
    var mm=modelTasks.map(function(t){return '<h4 class="detail-task">'+(TASK_MAP[t]?TASK_MAP[t].label:t)+'</h4><div class="table-scroll" id="detailModelMeta_'+t+'"></div>';}).join('');
    var modelsSub='<div class="detail-sub detail-sub--models"><h3 class="detail-sub-title">Benchmarked Models</h3>'+(mm||'<p class="empty-state small">No models for this task.</p>')+'</div>';
    detailsHtml='<details class="panel detail-group" id="dm-details"><summary><span class="dg-caret" aria-hidden="true">▸</span><span class="dg-titlewrap"><span class="dg-title">Environment &amp; Benchmarked Models</span><span class="dg-meta">'+dMeta+'</span></span><span class="dg-hint"></span></summary>'+envSub+modelsSub+'</details>';
  }

  // sticky in-page jump nav for the long "All metrics" view (color-coded by group)
  var jump='';
  if(metF==='all'&&(npu.length||pipe.length)){
    var jl=function(arr,c){return arr.map(function(x){return '<a class="'+c+'" href="#'+x.id+'">'+escHtml(x.lb)+'</a>';}).join('');};
    jump='<nav class="detail-jump" aria-label="Jump to metric section"><span class="detail-jump-label">↓ Jump to</span>'+jl(npu,'jl--npu')+jl(pipe,'jl--pipe')+(env?'<a class="jl--muted" href="#dm-details">Details</a>':'')+'</nav>';
  }

  // Concise methodology note so the numbers are read correctly (collapsed by default).
  var methodNote='<details class="panel detail-group detail-method" id="dm-method"><summary><span class="dg-caret" aria-hidden="true">▸</span><span class="dg-titlewrap"><span class="dg-title">How to read these metrics</span></span><span class="dg-hint"></span></summary><div class="detail-sub"><ul class="method-note">'
    +'<li><b>Latency</b> — single-core sync, 300 loops ×1, measured from cold.</li>'
    +'<li><b>Throughput</b> — multi-core async, sustained 30&nbsp;s ×3.</li>'
    +'<li><b>E2E</b> — full GStreamer pipeline (decode → pre → infer → post) ×3.</li>'
    +'<li><b>Max Channels</b> — most streams still meeting the FPS threshold.</li>'
    +'<li><b>NPU %</b> — Throughput/E2E show <i>core utilization</i> sampled by dxtop over the run. Latency shows <i>occupancy</i> (NPU time ÷ total frame time, from the profiler).</li>'
    +'<li><b>MHz / throttle</b> — A red clock means it fell below the nominal rated clock under load (throttling).</li>'
    +'</ul></div></details>';
  target.innerHTML=jump+methodNote+groupsHtml+detailsHtml;
  if(env){
    renderHostInfo(document.getElementById('detailEnvHostInfo'),env);
    renderNpuInfo(document.getElementById('detailEnvNpuInfo'),env);
    renderToolsInfo(document.getElementById('detailEnvToolsInfo'),env);
    modelTasks.forEach(function(t){var el=document.getElementById('detailModelMeta_'+t);if(el)renderModelMetaForTask(el,env,t);});
  }
}

/* ===== Meta ===== */
// Build hash read from this page's own app.js?v=<hash> ref (stamped by the builder).
// Lets a viewer confirm at a glance whether a reload picked up a rebuild (the date
// alone is day-granular and can't distinguish two builds on the same day).
function _buildStamp(){var s=document.querySelector('script[src*="app.js"]');if(!s)return null;var m=/[?&]v=([0-9a-f]{6,})/.exec(s.getAttribute('src')||'');return m?m[1]:null;}
function renderMeta() {
  var m=state.dataset.meta||{};
  var build=_buildStamp();
  document.getElementById('meta').innerHTML=
    '<div><strong>Environments</strong><span>'+(m.environment_count||0)+'</span></div>'+
    '<div><strong>Generated</strong><span>'+(m.generated_at?new Date(m.generated_at).toLocaleDateString():'-')+'</span></div>'+
    (build?'<div><strong>Build</strong><span title="dashboard content hash — changes on every rebuild">'+escHtml(build)+'</span></div>':'');
}

/* ===== Version Trend helpers ===== */
function _envToHwId(env){
  if(!env)return null;
  if(env.hw_id)return env.hw_id;
  var h=env.hostname||'unknown',s=env.npu_sku||'unknown';
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
function _switchToTrend(hwId){
  document.querySelectorAll('.tab').forEach(function(b){b.classList.remove('active');});
  document.querySelectorAll('.tab-content').forEach(function(c){c.classList.remove('active');});
  document.querySelector('[data-tab="version-trend"]').classList.add('active');
  document.getElementById('tab-version-trend').classList.add('active');
  var sel=document.getElementById('trendEnvFilter');
  sel.value=hwId;state.trendHwId=hwId;
  refreshTrend();resizeTrendChart();
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
  chart._resize=function(){var el=this._canvas.parentElement,dpr=window.devicePixelRatio||1;var w=el.clientWidth,h=el.clientHeight;this._canvas.width=w*dpr;this._canvas.height=h*dpr;this._canvas.style.width=w+'px';this._canvas.style.height=h+'px';this._canvas.getContext('2d').scale(dpr,dpr);this._scheduleDraw();};
  chart._scheduleDraw=function(){var s=this;if(s._raf)cancelAnimationFrame(s._raf);s._raf=requestAnimationFrame(function(){s._draw();});};
  chart._layout=function(){var dpr=window.devicePixelRatio||1;var W=this._canvas.width/dpr,H=this._canvas.height/dpr;var P={top:(this._showLegend===false?26:55),right:30,bottom:(this._showLegend===false?54:80),left:72};return{W:W,H:H,P:P,CW:W-P.left-P.right,CH:H-P.top-P.bottom};};
  chart._niceMax=function(v){if(v<=0)return 10;var e=Math.pow(10,Math.floor(Math.log10(v)));var f=v/e;return(f<=2?2:f<=5?5:10)*e;};
  chart._draw=function(){
    var data=this._data,cv=this._canvas,ctx=cv.getContext('2d');
    var lay=this._layout();var W=lay.W,H=lay.H,P=lay.P,CW=lay.CW,CH=lay.CH;
    ctx.clearRect(0,0,W,H);
    if(!data.length||!data[0].points||!data[0].points.length){ctx.fillStyle='#888';ctx.font='14px sans-serif';ctx.textAlign='center';ctx.fillText((state.dataset.snapshots||[]).length?('No trend data for '+this._metric.metricLabel.toLowerCase()+' with this selection'):'No snapshot history available. Build the dashboard from nested results/{hw_id}/{run_id} data to see version trend.',W/2,H/2);return;}
    var nPts=data[0].points.length;var maxVal=0,minVal=Infinity;
    data.forEach(function(line){line.points.forEach(function(point){if(point.value!=null){maxVal=Math.max(maxVal,point.value);minVal=Math.min(minVal,point.value);}});});
    if(minVal===Infinity)minVal=0;
    var range=maxVal-minVal;var pad=Math.max(range*0.2,maxVal*0.02,1);var rawFloor=minVal-pad;var rawCeil=maxVal+pad;var ystep=(rawCeil-rawFloor)/5;var ymag=Math.pow(10,Math.floor(Math.log10(Math.max(ystep,1e-9))));var ynorm=ystep/ymag;var niceStep=(ynorm<=1?1:ynorm<=2?2:ynorm<=5?5:10)*ymag;var floor=Math.max(0,Math.floor(rawFloor/niceStep)*niceStep);var ceil=Math.ceil(rawCeil/niceStep)*niceStep;if(ceil<=floor)ceil=floor+niceStep*5;
    var xMargin=nPts<=1?0:Math.max(40,Math.min(CW*0.08,80));var xSpan=CW-2*xMargin;var self=this;var xPos=function(i){return P.left+xMargin+(nPts===1?xSpan/2:i*(xSpan/Math.max(nPts-1,1)));};var yPos=function(v){return P.top+CH-((v-floor)/(ceil-floor||1))*CH;};var hasSelection=self._selectedIdx>=0&&self._selectedIdx<nPts;var groupWidth=nPts===1?Math.min(xSpan*0.6,96):Math.max(36,Math.min(90,(xSpan/Math.max(nPts-1,1))-14));
    ctx.strokeStyle='rgba(0,0,0,0.065)';ctx.lineWidth=1;for(var g=0;g<=5;g++){var gy=P.top+CH*g/5;ctx.beginPath();ctx.moveTo(P.left,gy);ctx.lineTo(P.left+CW,gy);ctx.stroke();}
    ctx.strokeStyle='rgba(0,0,0,0.18)';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(P.left,P.top);ctx.lineTo(P.left,P.top+CH);ctx.stroke();ctx.beginPath();ctx.moveTo(P.left,P.top+CH);ctx.lineTo(P.left+CW,P.top+CH);ctx.stroke();
    ctx.textAlign='right';ctx.fillStyle='#444';ctx.font='11px sans-serif';for(var t=0;t<=5;t++){var tv=ceil-(ceil-floor)*t/5;ctx.fillText(Math.round(tv),P.left-6,P.top+CH*t/5+4);}ctx.save();ctx.fillStyle='#333';ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.translate(14,P.top+CH/2);ctx.rotate(-Math.PI/2);ctx.fillText(this._metric.axisLabel,0,0);ctx.restore();
    if(hasSelection){var selectedX=xPos(self._selectedIdx);var groupLeft=Math.max(P.left,Math.min(selectedX-groupWidth/2,P.left+CW-groupWidth));ctx.save();ctx.fillStyle='rgba(27,107,88,0.06)';ctx.fillRect(groupLeft,P.top-2,groupWidth,CH+4);ctx.strokeStyle='rgba(27,107,88,0.9)';ctx.lineWidth=3;ctx.setLineDash([6,3]);ctx.strokeRect(groupLeft,P.top-2,groupWidth,CH+4);ctx.setLineDash([]);ctx.restore();}
    var _labelGap=13;function _spreadLabels(items){items.sort(function(a,b){return a.baseY-b.baseY;});for(var pass=0;pass<4;pass++){for(var j=1;j<items.length;j++){var gap=items[j].y-items[j-1].y;if(gap<_labelGap){var shift=(_labelGap-gap)/2;items[j-1].y-=Math.ceil(shift);items[j].y+=Math.ceil(shift);}}items.sort(function(a,b){return a.y-b.y;});}return items;}
    var colLabels={};data.forEach(function(line,li){line.points.forEach(function(point,i){if(point.value==null)return;if(!colLabels[i])colLabels[i]=[];colLabels[i].push({lineIdx:li,baseY:yPos(point.value)-10,y:yPos(point.value)-10,value:point.value});});});Object.keys(colLabels).forEach(function(k){_spreadLabels(colLabels[k]);});
    data.forEach(function(line,li){var sc=SIZE_COLORS[line.size]||SIZE_COLORS.n;ctx.save();ctx.globalAlpha=hasSelection?0.72:1;ctx.strokeStyle=sc.line;ctx.lineWidth=2.5;ctx.beginPath();var started=false;line.points.forEach(function(point,i){if(point.value==null)return;var x=xPos(i),y=yPos(point.value);if(!started){ctx.moveTo(x,y);started=true;}else{ctx.lineTo(x,y);}});ctx.stroke();ctx.restore();line.points.forEach(function(point,i){if(point.value==null)return;var x=xPos(i),y=yPos(point.value);var isSelectedColumn=i===self._selectedIdx;var isHoveredColumn=i===self._hoverIdx;var r=isSelectedColumn?7:(isHoveredColumn?6:5);ctx.fillStyle=hasSelection?(isSelectedColumn?sc.hi:(isHoveredColumn?sc.fill:sc.dim)):(isHoveredColumn?sc.hi:sc.fill);ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.strokeStyle=sc.line;ctx.lineWidth=isSelectedColumn?3:1.5;ctx.stroke();var labelY=y-10;var cl=colLabels[i];if(cl){for(var ci=0;ci<cl.length;ci++){if(cl[ci].lineIdx===li){labelY=cl[ci].y;break;}}}var isEmphasized=isSelectedColumn||isHoveredColumn;var labelText=_formatTrendValue(self._metric,point.value);ctx.font=isEmphasized?'bold 11px sans-serif':'10px sans-serif';ctx.textAlign='center';ctx.globalAlpha=hasSelection?(isEmphasized?1:0.7):1;if(isEmphasized){ctx.strokeStyle='#fff';ctx.lineWidth=3;ctx.lineJoin='round';ctx.strokeText(labelText,x,labelY);ctx.fillStyle='#111';ctx.fillText(labelText,x,labelY);}else{ctx.strokeStyle='#fff';ctx.lineWidth=3;ctx.lineJoin='round';ctx.strokeText(labelText,x,labelY);ctx.fillStyle='#111';ctx.fillText(labelText,x,labelY);}ctx.globalAlpha=1;});});
    if(data[0]&&data[0].points){data[0].points.forEach(function(point,i){var x=xPos(i);var isSelectedColumn=i===self._selectedIdx;var isHoveredColumn=i===self._hoverIdx;ctx.fillStyle=hasSelection?(isSelectedColumn?'#333':(isHoveredColumn?'#5d6572':'rgba(93,101,114,0.55)')):'#333';ctx.font=isSelectedColumn?'600 11px sans-serif':'11px sans-serif';ctx.textAlign='center';ctx.fillText(point.dateLabel||'',x,P.top+CH+16);});}
    if(this._showLegend===false)return;var lx=P.left,ly=22;SIZE_KEYS.forEach(function(sz){var sc=SIZE_COLORS[sz];ctx.fillStyle=sc.fill;ctx.beginPath();ctx.arc(lx+6,ly,5,0,Math.PI*2);ctx.fill();ctx.strokeStyle=sc.line;ctx.lineWidth=1.5;ctx.stroke();var label=sz.toUpperCase()+' ('+SIZE_LABELS[sz]+')';ctx.fillStyle='#333';ctx.font='12px sans-serif';ctx.textAlign='left';ctx.fillText(label,lx+16,ly+4);lx+=ctx.measureText(label).width+35;});
  };
  chart._hitTest=function(e){var rect=this._canvas.getBoundingClientRect();var x=e.clientX-rect.left;var lay=this._layout();var data=this._data;if(!data.length||!data[0].points||!data[0].points.length)return -1;var nPts=data[0].points.length;var xM=nPts<=1?0:Math.max(40,Math.min(lay.CW*0.08,80));var xS=lay.CW-2*xM;if(nPts===1)return Math.abs(x-(lay.P.left+xM+xS/2))<30?0:-1;var step=xS/Math.max(nPts-1,1);var idx=Math.round((x-lay.P.left-xM)/step);if(idx<0||idx>=nPts)return -1;var hitX=lay.P.left+xM+idx*step;return Math.abs(x-hitX)<Math.max(20,step*0.4)?idx:-1;};
  chart._handleClick=function(e){var i=this._hitTest(e);if(i>=0&&this._onClick)this._onClick(i);};
  chart._handleHover=function(e){var i=this._hitTest(e);if(i!==this._hoverIdx){this._hoverIdx=i;this._canvas.style.cursor=i>=0?'pointer':'default';this._scheduleDraw();}};
  chart._handleLeave=function(){this._hoverIdx=-1;this._canvas.style.cursor='default';this._scheduleDraw();};
  chart._ro=new ResizeObserver(chart._resize.bind(chart));chart._ro.observe(canvas.parentElement);canvas.addEventListener('click',chart._handleClick.bind(chart));canvas.addEventListener('mousemove',chart._handleHover.bind(chart));canvas.addEventListener('mouseleave',chart._handleLeave.bind(chart));chart._resize();
  return chart;
}
function resizeTrendChart(){(state.trendCharts||[]).forEach(function(c){c.chart._resize();});}
function _suiteVer(snap){return snap.dx_all_suite_version||'unknown';}
function _cmpSuiteVer(a,b){
  if(a===b)return 0;
  if(a==='unknown')return 1; if(b==='unknown')return -1;
  function parse(v){
    var s=String(v).replace(/^v/i,'');
    var parts=s.split('-');                                  // "2.4.0-rc.4" -> ["2.4.0","rc.4"]
    var nums=parts[0].split('.').map(function(n){var x=parseInt(n,10);return isNaN(x)?0:x;});
    return {nums:nums, pre:parts.length>1?parts.slice(1).join('-'):null};  // pre=null => release
  }
  var A=parse(a),B=parse(b);
  var m=Math.max(A.nums.length,B.nums.length);
  for(var i=0;i<m;i++){var x=A.nums[i]||0,y=B.nums[i]||0;if(x!==y)return x-y;}
  // Same numeric core: a release ranks ABOVE its pre-releases.
  if(A.pre===null&&B.pre!==null)return 1;
  if(A.pre!==null&&B.pre===null)return -1;
  if(A.pre!==null&&B.pre!==null){var c=A.pre.localeCompare(B.pre);if(c!==0)return c;}
  return String(a).localeCompare(String(b));
}
function _trendVersionsForHw(hwId){
  var seen={},out=[];
  (state.dataset.snapshots||[]).forEach(function(s){if(s.hw_id!==hwId)return;var v=_suiteVer(s);if(!seen[v]){seen[v]=true;out.push(v);}});
  out.sort(_cmpSuiteVer);   // ascending — matches chart X order
  return out;
}
function _trendRunsForVersion(hwId,version){
  var out=(state.dataset.snapshots||[]).filter(function(s){return s.hw_id===hwId&&_suiteVer(s)===version;});
  out.sort(function(a,b){return (a.run_id||'')<(b.run_id||'')?1:-1;});   // latest run_id first
  return out;
}
function renderTrendRunSelectors(){
  var el=document.getElementById('trendRunSelectors');if(!el)return;
  var hwId=state.trendHwId;var versions=_trendVersionsForHw(hwId);
  el.innerHTML=versions.map(function(v){
    var runs=_trendRunsForVersion(hwId,v);if(!runs.length)return '';
    var cur=(state.trendRunByVersion&&state.trendRunByVersion[v])||runs[0].run_id;
    var opts=runs.map(function(s){return '<option value="'+escHtml(s.run_id)+'"'+(s.run_id===cur?' selected':'')+'>'+escHtml(s.run_id)+'</option>';}).join('');
    return '<label class="run-inline-item"><span class="run-inline-name">dx-all-suite '+escHtml(v)+'</span><select data-trend-run-ver="'+escHtml(v)+'">'+opts+'</select></label>';
  }).join('');
  el.querySelectorAll('select[data-trend-run-ver]').forEach(function(sel){
    sel.addEventListener('change',function(){state.trendRunByVersion[this.dataset.trendRunVer]=this.value;refreshTrend();});
  });
}
function getTrendData(hwId,task,useOrt,metricKey){
  var metric=_trendMetricByKey(metricKey);
  var snaps=(state.dataset.snapshots||[]).filter(function(s){return s.hw_id===hwId;});
  if(!snaps.length)return[];
  /* group snapshots by suite version; the selected run per version (state.trendRunByVersion) drives the point, else latest */
  var byVer={};
  snaps.forEach(function(snap){var v=_suiteVer(snap);(byVer[v]=byVer[v]||[]).push(snap);});
  var versions=Object.keys(byVer).sort(_cmpSuiteVer);
  var lines=SIZE_KEYS.map(function(sz){return{size:sz,points:[]};});
  versions.forEach(function(v){
    var list=byVer[v];
    var wantRun=state.trendRunByVersion?state.trendRunByVersion[v]:null;
    var snap=wantRun?list.find(function(s){return s.run_id===wantRun;}):null;
    if(!snap)snap=list.slice().sort(function(a,b){return (a.run_id||'')<(b.run_id||'')?1:-1;})[0];  // latest run_id
    SIZE_KEYS.forEach(function(sz,si){
      var value=_snapshotMetricValue(snap,task,useOrt,metric,sz);
      /* dateLabel = version (x-axis label). Run identity lives in the top run-per-version selector. */
      lines[si].points.push({value:value!=null?Number(value):null,dateLabel:v,swLabel:_trendSwLabel(snap),run_id:snap.run_id,snap:snap});
    });
  });
  return lines;
}
function hideTrendEnvDetail(){var panel=document.getElementById('trendEnvDetail');if(panel)panel.style.display='none';var metaPanel=document.getElementById('trendModelMetaPanel');if(metaPanel)metaPanel.style.display='none';}
function renderTrendEnvDetail(snap,options){
  options=options||{};var panel=document.getElementById('trendEnvDetail');if(!panel)return;var env=snap&&snap.environment;if(!env){panel.style.display='none';document.getElementById('trendModelMetaPanel').style.display='none';return;}panel.style.display='';var dateStr=snap.timestamp?snap.timestamp.substring(0,10):snap.run_id;var verStr=snap.dx_all_suite_version||'unknown';document.getElementById('trendEnvDetailTitle').textContent='Details \u2014 '+(env.env_id||env.hostname||'Environment')+' \u00b7 DX-AS '+verStr+' \u00b7 '+dateStr+' \u00b7 '+snap.run_id;renderHostInfo(document.getElementById('trendEnvHostInfo'),env);renderNpuInfo(document.getElementById('trendEnvNpuInfo'),env);renderToolsInfo(document.getElementById('trendEnvToolsInfo'),env);
  var metaPanel=document.getElementById('trendModelMetaPanel');metaPanel.style.display='';document.getElementById('trendModelMetaTitle').textContent='Benchmarked Models \u2013 '+TASK_MAP[state.trendTask].label;renderModelMetaForTask(document.getElementById('trendModelMetaSection'),env,state.trendTask);
  if(options.scroll!==false)panel.scrollIntoView({behavior:'smooth',block:'nearest'});
}
function refreshTrend(){
  var hwId=state.trendHwId;var task=state.trendTask;var useOrt=state.trendOrt;
  var subtitle=document.getElementById('trendGridSubtitle');
  if(subtitle)subtitle.textContent=(TASK_MAP[task]?TASK_MAP[task].label:task)+'  \u00b7  ORT '+(useOrt?'ON':'OFF');
  /* All four metrics share the same X-axis (suite versions for this hw/task/ort). */
  var selectedIdx=-1;
  (state.trendCharts||[]).forEach(function(c){
    c.data=getTrendData(hwId,task,useOrt,c.metric.key);
    if(selectedIdx<0)selectedIdx=_latestTrendPointIndex(c.data);
  });
  state.trendData=(state.trendCharts[0]&&state.trendCharts[0].data)||[];  // primary series drives shared selection
  state.trendSelectedIdx=selectedIdx;
  if(selectedIdx>=0){handleTrendPointClick(selectedIdx,{scroll:false});}
  else{hideTrendEnvDetail();(state.trendCharts||[]).forEach(function(c){c.chart.update(c.data,-1);});}
}
function handleTrendPointClick(idx,options){
  options=options||{};state.trendSelectedIdx=idx;
  (state.trendCharts||[]).forEach(function(c){c.chart.update(c.data,idx);});  // sync the version cursor across all 4 charts
  var data=state.trendData||[];var snap=null;if(data.length&&data[0].points[idx])snap=data[0].points[idx].snap;
  if(!snap){hideTrendEnvDetail();return;}renderTrendEnvDetail(snap,options);
}
function renderTrendLegend(){
  var el=document.getElementById('trendGridLegend');if(!el)return;
  el.innerHTML=SIZE_KEYS.map(function(sz){var sc=SIZE_COLORS[sz];return '<span class="tg-leg"><span class="tg-dot" style="background:'+sc.fill+';border-color:'+sc.line+'"></span>'+sz.toUpperCase()+' ('+SIZE_LABELS[sz]+')</span>';}).join('');
}
function initTrendChart(){
  var grid=document.getElementById('trendGrid');if(!grid)return;
  grid.innerHTML='';state.trendCharts=[];renderTrendLegend();
  /* One small-multiple per metric, arranged into two colour-coded group blocks (NPU inference vs.
     host+NPU pipeline). The in-canvas size legend is suppressed in favour of the shared legend above.
     trendCharts stays in TREND_GROUPS/keys order (latency first) — refreshTrend() drives shared
     selection off trendCharts[0]. */
  TREND_GROUPS.forEach(function(group){
    var block=document.createElement('section');block.className='trend-group trend-group--'+group.id;
    var head=document.createElement('div');head.className='trend-group-head';
    head.innerHTML='<span class="trend-group-label">'+escHtml(group.label)+'</span>'
      +'<span class="trend-group-desc">'+escHtml(group.desc)+'</span>'
      +(group.input?'<span class="trend-group-input">Input: '+escHtml(group.input)+'</span>':'');
    var gGrid=document.createElement('div');gGrid.className='trend-group-grid';
    block.appendChild(head);block.appendChild(gGrid);grid.appendChild(block);
    group.keys.forEach(function(key){
      var metric=_metricByKey(key);if(!metric)return;
      var cell=document.createElement('div');cell.className='trend-cell';
      var title=document.createElement('div');title.className='trend-cell-title';title.textContent=metric.metricLabel;
      var sub=document.createElement('div');sub.className='trend-cell-sub';sub.innerHTML=_trendMetricSubtitle(metric.key);
      var box=document.createElement('div');box.className='trend-cell-canvas';
      var canvas=document.createElement('canvas');canvas.id='trendChart-'+metric.key;
      box.appendChild(canvas);cell.appendChild(title);cell.appendChild(sub);cell.appendChild(box);gGrid.appendChild(cell);
      var chart=createTrendChart(canvas,function(idx){handleTrendPointClick(idx);});
      chart._showLegend=false;chart.setMetric(metric);
      state.trendCharts.push({metric:metric,chart:chart,data:[]});
    });
  });
}
function initTrendTab(){
  var sel=document.getElementById('trendEnvFilter');var hwIds=_getUniqueHwIds();sel.innerHTML=hwIds.map(function(id){return '<option value="'+escHtml(id)+'">'+escHtml(id)+'</option>';}).join('');if(hwIds.length){state.trendHwId=hwIds[0];sel.value=hwIds[0];}state.trendTask='object_detection';state.trendOrt=true;state.trendRunByVersion={};renderTrendRunSelectors();sel.addEventListener('change',function(){state.trendHwId=this.value;state.trendRunByVersion={};renderTrendRunSelectors();refreshTrend();});document.getElementById('trendTaskFilter').addEventListener('change',function(){state.trendTask=this.value;refreshTrend();});document.getElementById('trendOrtFilter').addEventListener('change',function(){state.trendOrt=this.value==='on';refreshTrend();});refreshTrend();
}

/* ===== Main ===== */
async function main() {
  try{state.dataset=await loadDataset();}catch(e){document.querySelector('.chart-container').innerHTML='<div class="empty-state" style="margin:80px auto">Failed to load dataset: '+e.message+'</div>';return;}
  _initSelectedRunIds();renderMeta();initTabs();renderRunSelectors('fpsRunSelectors');renderRunSelectors('overviewRunSelectors');initFpsFilters();initOverviewFilters();
  FpsChart.init(document.getElementById('fpsCompareChart'),handleFpsEnvClick);
  Chart.init(document.getElementById('mainChart'),function(idx,d){if(d&&d.missing)return;state.selectedEnvId=d.envId;renderEnvDetail(d.env,{scroll:true});Chart.update(state.chartData,state.selectedEnvId);});
  refreshFpsCompare();refreshChart();initDetailTab();
  /* Version Trend tab */
  if((state.dataset.snapshots||[]).length){
    initTrendChart();
    initTrendTab();
  }
}
main();
