// dx_app/static/js/rundemo.js
// Run Demo GUI: fetch /api/demos, render category sections + per-demo blocks
// with segmented toggles (input/code/mode/post) gated by each demo's real
// availability. Also wires each block's Run/Stop: maps selected toggles to
// an /api/run body (rundemoBody), calls it, and renders inline via the
// shared window.renderInferenceResult (Task 4).
'use strict';

var RUNDEMO = { loaded: false, demos: [], groups: [], sel: {} }; // sel[idx] = {input,code,mode,post}

// Layout-only CSS for the group/grid/axis-row structure below, built purely
// from the design tokens already defined in style.css. This module's brief
// is scoped to rundemo.js + templates/index.html only, so instead of adding
// rules to style.css this injects one <style> tag the first time it runs.
// Toggle look-and-feel itself reuses the existing .chip / .chip.active pills.
// The card/grid/group/chip layout now lives in style.css (redesigned Run Demo block).
// This inline sheet keeps ONLY the result-area containment: renderInferenceResult /
// renderInferenceError markup (long error strings, <pre> Full Output, perf grid, compare
// canvas) is sized for the wide Run panel, so force every child to wrap or scroll INSIDE the
// narrow demo card — nothing spills past the card.
var _RUNDEMO_CSS = ''
  + '.rundemo-result *{max-width:100%;box-sizing:border-box}'
  + '.rundemo-result p,.rundemo-result span,.rundemo-result div,.rundemo-result td,.rundemo-result code'
  +   '{overflow-wrap:anywhere;word-break:break-word}'
  + '.rundemo-result pre{white-space:pre-wrap;word-break:break-word;overflow-x:auto}'
  + '.rundemo-result img,.rundemo-result video,.rundemo-result canvas{max-width:100%;height:auto}';
function _rundemoInjectStyle() {
  if (document.getElementById('rundemo-inline-style')) return;
  var s = document.createElement('style');
  s.id = 'rundemo-inline-style';
  s.textContent = _RUNDEMO_CSS;
  document.head.appendChild(s);
}

// ─── 6-language inline helper (mirrors i18n.js's _T5, adds es) ────────────
function _T6(ko, en, ja, zhCN, zhTW, es) {
  var lang = (window.DXI18n && window.DXI18n.lang) || 'en';
  if (lang === 'ko') return ko || en;
  if (lang === 'ja') return ja || en;
  if (lang === 'zh-CN') return zhCN || en;
  if (lang === 'zh-TW') return zhTW || en;
  if (lang === 'es') return es || en;
  return en;
}

// ─── PURE, TESTABLE fn: per-demo toggle availability ──────────────────────
// demo: {category, image_only, async_full, avail:{cpp_sync,cpp_async,py_sync,
//        py_async,py_sync_cpp_postprocess,py_async_cpp_postprocess,model_exists}}
// returns {input:{video,image,bin}, code:{python,cpp}, mode:{sync,async},
//          post:boolean, defaults:{input,code,mode,post}}
function rundemoAvail(demo) {
  demo = demo || {};
  var avail = demo.avail || {};

  var input = { bin: false, video: false, image: false };
  if (demo.category === '3d_object_detection') {
    input.bin = true; // fixed .bin chip — no video/image for this task
  } else {
    input.image = true;
    input.video = !demo.image_only;
  }

  var code = {
    python: !!(avail.py_sync || avail.py_async || avail.py_sync_cpp_postprocess || avail.py_async_cpp_postprocess),
    cpp: !!(avail.cpp_sync || avail.cpp_async)
  };

  // Default to the native C++ example when its binary is built — that is exactly what the
  // terminal run_demo.sh runs, and every C++ task runner writes an annotated output video
  // reliably. Fall back to Python only when there is no C++ build (e.g. a fresh clone that
  // hasn't run build.sh). Whichever the user then picks in the Code selector is honored
  // verbatim — cpp runs cpp, python runs python (no silent switching).
  var defaultCode = code.cpp ? 'cpp' : 'python';
  var syncEnabled = _rundemoSyncEnabled(demo, avail, defaultCode);
  var asyncEnabled = _rundemoAsyncEnabled(demo, avail, defaultCode);
  var mode = { sync: syncEnabled, async: asyncEnabled };

  // Coarse: does this demo have C++ postprocess (python-only) at all, in
  // either mode? The block recomputes the fine-grained per-mode enablement.
  var post = !!(avail.py_sync_cpp_postprocess || avail.py_async_cpp_postprocess);
  var defaultPost = !!(defaultCode === 'python' && avail.py_sync_cpp_postprocess);

  var defaultInput = input.video ? 'video' : (input.image ? 'image' : (input.bin ? 'bin' : null));
  // Default mode must be one that is actually ENABLED: prefer sync, fall back
  // to async if sync is unavailable for the default code. If neither mode is
  // enabled (edge case — code.python/cpp true only via a postprocess-only
  // flag), keep 'sync' as a label only; runnable() callers must not dispatch
  // in that state (see rundemoRun's guard).
  var defaultMode = syncEnabled ? 'sync' : (asyncEnabled ? 'async' : 'sync');

  return {
    input: input,
    code: code,
    mode: mode,
    post: post,
    defaults: { input: defaultInput, code: defaultCode, mode: defaultMode, post: defaultPost }
  };
}
if (typeof window !== 'undefined') window.rundemoAvail = rundemoAvail;

// ─── PURE, TESTABLE fn: can this demo run at all? ─────────────────────────
// Gate (A): model not downloaded (avail.model_exists === false).
// Gate (B): no runnable build (neither python nor cpp code available).
// demo: same shape as rundemoAvail's param.
function runnable(demo) {
  demo = demo || {};
  var avail = demo.avail || {};
  if (avail.model_exists === false) return false;
  var code = rundemoAvail(demo).code;
  return !!(code.python || code.cpp);
}
if (typeof window !== 'undefined') window.runnable = runnable;

// Internal helpers reused by the render/recompute logic below (not part of
// the pure-fn contract above, but implement the exact same rules so a code
// or mode toggle can recompute enablement for the block that changed).
function _rundemoAsyncEnabled(demo, avail, codeSel) {
  return codeSel === 'cpp' ? !!avail.cpp_async : !!(avail.py_async && demo.async_full);
}
function _rundemoSyncEnabled(demo, avail, codeSel) {
  return codeSel === 'cpp' ? !!avail.cpp_sync : !!(avail.py_sync || avail.py_sync_cpp_postprocess);
}
function _rundemoPostEnabled(avail, codeSel, modeSel) {
  if (codeSel !== 'python') return false;
  return modeSel === 'async' ? !!avail.py_async_cpp_postprocess : !!avail.py_sync_cpp_postprocess;
}

// ─── fetch + init ──────────────────────────────────────────────────────────
function rundemoInit() {
  if (RUNDEMO.loaded) return; // guard against double-run (nav() may call this repeatedly)
  RUNDEMO.loaded = true;
  _rundemoInjectStyle();
  var root = document.getElementById('rundemo-root');
  if (!root) return;
  root.innerHTML = '<div class="txt-dim txt-sm" style="padding:20px">'
    + esc(_T6('불러오는 중…', 'Loading…', '読み込み中…', '加载中…', '載入中…', 'Cargando…'))
    + '</div>';
  api('/api/demos').then(function (r) {
    if (!r || !r.ok || !r.demos || !r.demos.length) {
      root.innerHTML = '<div class="txt-dim txt-sm" style="padding:20px">'
        + esc(_T6(
          '데모 목록을 사용할 수 없습니다. run_demo.sh를 확인하세요.',
          'Demo list unavailable. Check run_demo.sh.',
          'デモ一覧を利用できません。run_demo.sh を確認してください。',
          '演示列表不可用，请检查 run_demo.sh。',
          '示範清單無法使用，請檢查 run_demo.sh。',
          'Lista de demostraciones no disponible. Verifique run_demo.sh.'))
        + '</div>';
      return;
    }
    RUNDEMO.demos = r.demos;
    RUNDEMO.groups = r.groups || [];
    rundemoRender(r.demos, RUNDEMO.groups);
  });
}
if (typeof window !== 'undefined') window.rundemoInit = rundemoInit;

// Force a full re-fetch + re-render of /api/demos (e.g. after Setup's Demo
// Quick Start installs models — rundemoInit()'s RUNDEMO.loaded guard would
// otherwise keep showing the stale not-runnable gating until a page reload).
function rundemoReload() {
  RUNDEMO.loaded = false;
  rundemoInit();
}
if (typeof window !== 'undefined') window.rundemoReload = rundemoReload;

// ─── render ────────────────────────────────────────────────────────────────
function rundemoRender(demos, groups) {
  var root = document.getElementById('rundemo-root');
  if (!root) return;
  var byGroup = {};
  demos.forEach(function (d) {
    (byGroup[d.group] = byGroup[d.group] || []).push(d);
  });
  var order = (groups && groups.length) ? groups : Object.keys(byGroup);
  var groupsHtml = order.map(function (g) {
    var list = byGroup[g] || [];
    if (!list.length) return '';
    var hue = (_RUNDEMO_HUE && _RUNDEMO_HUE[g]) || 'var(--accent)';
    return '<div class="rundemo-group" style="--c:' + hue + '">'
      + '<div class="rundemo-group-hd"><span class="rd-rail"></span>'
      + '<h3 class="rundemo-group-title">' + esc(g) + '</h3>'
      + '<span class="rd-gcount">' + list.length + '</span><span class="rd-gline"></span></div>'
      + '<div class="rundemo-grid">' + list.map(_rundemoBlockHtml).join('') + '</div>'
      + '</div>';
  }).join('');
  var html = groupsHtml ? ('<div class="rundemo-groups">' + groupsHtml + '</div>') : '';
  root.innerHTML = html || ('<div class="txt-dim txt-sm" style="padding:20px">'
    + esc(_T6('데모가 없습니다.', 'No demos.', 'デモがありません。', '暂无演示。', '暫無示範。', 'No hay demostraciones.'))
    + '</div>');
  demos.forEach(function (d) { _rundemoUpdateBlockUI(d); });
}
if (typeof window !== 'undefined') window.rundemoRender = rundemoRender;

// Reuses the existing .chip/.chip.active pill classes as-is (already used
// elsewhere, e.g. ModelZoo task filters). Greyed/non-clickable "disabled"
// look is applied inline, mirroring the codebase's own .btn:disabled rule
// (opacity .35, no pointer events) — no CSS file is touched by this module.
var _RUNDEMO_DISABLED_STYLE = 'opacity:.35;cursor:not-allowed;pointer-events:none';
function _rundemoAxisHtml(idx, axis, options, activeVal, axisLabel) {
  var opts = options.map(function (o) {
    var isActive = o.val === activeVal;
    var cls = 'chip rundemo-chip' + (isActive ? ' active' : '') + (o.disabled ? ' disabled' : '');
    var disAttr = o.disabled ? ' disabled style="' + _RUNDEMO_DISABLED_STYLE + '"' : '';
    return '<button type="button" class="' + cls + '" data-axis="' + axis + '" data-val="' + esc(o.val) + '"' + disAttr
      + ' onclick="_rundemoToggle(' + idx + ',\'' + axis + '\',\'' + o.val + '\')">' + esc(o.label) + '</button>';
  }).join('');
  return '<div class="rundemo-axis" data-axis-row="' + axis + '">'
    + '<span class="rundemo-axis-label txt-dim txt-xs">' + esc(axisLabel) + '</span>'
    + '<div class="rundemo-chipgroup" data-axis="' + axis + '">' + opts + '</div>'
    + '</div>';
}

// Not-runnable hint block: reuses the existing .setup-card/.rundemo-block
// shell and .btn classes so it looks native, but renders a 6-lang notice +
// nav('setup') handoff instead of toggles/Run. avail.model_exists===false
// takes priority (case A) over the no-build case (case B) since installing
// the model is the more actionable first step for the user.
function _rundemoNotRunnableHtml(d, av) {
  var avail = d.avail || {};
  var modelMissing = avail.model_exists === false;
  var msg = modelMissing
    ? _T6('모델 미설치 — Setup의 Demo Quick Start로 설치하세요',
        'Model not installed — use Demo Quick Start on Setup',
        'モデル未インストール — SetupのDemo Quick Startでインストールしてください',
        '模型未安装 — 请在 Setup 的 Demo Quick Start 中安装',
        '模型未安裝 — 請在 Setup 的 Demo Quick Start 中安裝',
        'Modelo no instalado — instálelo desde Demo Quick Start en Setup')
    : _T6('실행 가능한 빌드 없음 — DX-APP/DX-Runtime 빌드를 먼저 완료하세요',
        'No runnable build — complete DX-APP/DX-Runtime build first',
        '実行可能なビルドがありません — 先にDX-APP/DX-Runtimeのビルドを完了してください',
        '没有可运行的构建 — 请先完成 DX-APP/DX-Runtime 构建',
        '沒有可執行的建置 — 請先完成 DX-APP/DX-Runtime 建置',
        'Sin build ejecutable — complete primero el build de DX-APP/DX-Runtime');
  var inner = '<div class="rundemo-notice rd-notice">' + esc(msg) + '</div>'
    + '<div class="rundemo-actions rd-foot">'
    + '<button type="button" class="rd-run rd-run-ghost" onclick="nav(\'setup\')">'
    + esc(_T6('설정으로', 'Go to Setup', 'セットアップへ', '前往设置', '前往設定', 'Ir a Configuración')) + ' &rarr;</button>'
    + '</div>';
  return _rundemoShell(d, { inner: inner });
}

// Category → hue, drawn from the shared semantic tokens (dx-tokens.css) so the demo page
// stays consistent with dx_stream's cat-* coloring. Keyed by demo group.
var _RUNDEMO_HUE = {
  'Detection': 'var(--info)', 'Segmentation': 'var(--npu)',
  'Keypoint & Pose': 'var(--warning)', 'Pose & Landmark': 'var(--warning)',
  'Depth Estimation': 'var(--accent-strong,#7C5CFC)', 'Recognition': 'var(--success)',
  'Image Restoration': 'var(--emerald,#10b981)', 'Classification': 'var(--success)',
  'Hand Detection': 'var(--warning)', 'Driving & 3D': 'var(--vpu,#e879f9)', 'PPU': 'var(--accent)'
};
function _rundemoHue(d) { return _RUNDEMO_HUE[d.group] || 'var(--accent)'; }

// New demo-card shell (design refactor). Keeps every functional hook intact: the id
// #rundemo-block-<idx>, the .rundemo-axes chip rows (data-axis/data-val + _rundemoToggle,
// which _rundemoUpdateBlockUI drives), the Run/Stop actions, and #rundemo-result-<idx>.
// `inner` is the axes+actions markup; `foot` optionally overrides the action row.
function _rundemoShell(d, opts) {
  opts = opts || {};
  var hue = _rundemoHue(d);
  var thumb = d.thumbnail
    ? '<img class="rd-thumb" src="' + esc(d.thumbnail) + '" alt="" loading="lazy" onerror="this.style.display=\'none\'">'
    : '';
  return '<div class="rd-card rundemo-block" id="rundemo-block-' + d.idx + '" data-cat="' + esc(d.group) + '" style="--c:' + hue + '">'
    + '<div class="rd-prev">' + thumb
    + '<span class="rd-tag">' + esc(d.group) + '</span></div>'
    + '<div class="rd-body">'
    + '<div class="rd-title">' + esc(d.label) + '</div>'
    + '<div class="rd-model">' + esc(d.model_name) + '</div>'
    + (opts.inner || '')
    + '<button type="button" class="rd-result-bar" onclick="_rundemoToggleResult(' + d.idx + ')">'
    + '<span class="rd-chev"></span>'
    + '<span class="rd-result-lbl">' + esc(_T6('결과', 'Result', '結果', '结果', '結果', 'Resultado')) + '</span>'
    + '</button>'
    + '<div class="rundemo-result" id="rundemo-result-' + d.idx + '"></div>'
    + '</div></div>';
}

// Collapse/expand a finished inference result in place (the bar only shows when the result
// area is non-empty — see the :has() rule in style.css).
function _rundemoToggleResult(idx) {
  var c = document.getElementById('rundemo-block-' + idx);
  if (c) c.classList.toggle('rd-collapsed');
}
if (typeof window !== 'undefined') window._rundemoToggleResult = _rundemoToggleResult;

function _rundemoBlockHtml(d) {
  var av = rundemoAvail(d);

  if (!runnable(d)) {
    // Case A/B short-circuit: no toggles are rendered, so the Task 6
    // defensive gap (default-code fallback marking the cpp chip active
    // when neither code is available) cannot surface here — there is no
    // toggle row at all in this path.
    RUNDEMO.sel[d.idx] = null;
    return _rundemoNotRunnableHtml(d, av);
  }

  RUNDEMO.sel[d.idx] = {
    input: av.defaults.input,
    code: av.defaults.code,
    mode: av.defaults.mode,
    post: av.defaults.post
  };
  var sel = RUNDEMO.sel[d.idx];

  var axesHtml = '';
  if (av.input.bin) {
    axesHtml += _rundemoAxisHtml(d.idx, 'input', [{ val: 'bin', label: '.bin', disabled: true }], 'bin',
      _T6('입력', 'Input', '入力', '输入', '輸入', 'Entrada'));
  } else {
    axesHtml += _rundemoAxisHtml(d.idx, 'input', [
      { val: 'video', label: _T6('영상', 'Video', '動画', '视频', '影片', 'Video'), disabled: !av.input.video },
      { val: 'image', label: _T6('이미지', 'Image', '画像', '图片', '圖片', 'Imagen'), disabled: !av.input.image }
    ], sel.input, _T6('입력', 'Input', '入力', '输入', '輸入', 'Entrada'));
  }

  axesHtml += _rundemoAxisHtml(d.idx, 'code', [
    { val: 'python', label: 'Python', disabled: !av.code.python },
    { val: 'cpp', label: 'C++', disabled: !av.code.cpp }
  ], sel.code, _T6('구현', 'Code', '実装', '实现', '實作', 'Código'));

  axesHtml += _rundemoAxisHtml(d.idx, 'mode', [
    { val: 'sync', label: _T6('동기', 'Sync', '同期', '同步', '同步', 'Síncrono'), disabled: !av.mode.sync },
    { val: 'async', label: _T6('비동기', 'Async', '非同期', '异步', '異步', 'Asíncrono'), disabled: !av.mode.async }
  ], sel.mode, _T6('모드', 'Mode', 'モード', '模式', '模式', 'Modo'));

  if (av.post) {
    axesHtml += _rundemoAxisHtml(d.idx, 'post', [
      { val: 'off', label: _T6('끄기', 'Off', 'オフ', '关闭', '關閉', 'Desactivado'), disabled: false },
      { val: 'on', label: _T6('C++ 후처리', 'C++ Postproc', 'C++後処理', 'C++后处理', 'C++後處理', 'Postproc C++'), disabled: !_rundemoPostEnabled(d.avail || {}, sel.code, sel.mode) }
    ], sel.post ? 'on' : 'off', _T6('후처리', 'Postprocess', '後処理', '后处理', '後處理', 'Postproceso'));
  }

  var inner = '<div class="rundemo-axes rd-controls">' + axesHtml + '</div>'
    + '<div class="rundemo-actions rd-foot">'
    + '<button type="button" class="rd-run" onclick="if(window.rundemoRun)rundemoRun(' + d.idx + ')">'
    + '<span class="rd-play"></span>' + esc(_T6('실행', 'Run', '実行', '运行', '執行', 'Ejecutar')) + '</button>'
    + '<button type="button" class="rd-stop" title="Stop" onclick="if(window.rundemoStop)rundemoStop()">'
    + '<span class="rd-sq"></span></button>'
    + '</div>';
  return _rundemoShell(d, { inner: inner });
}

// Re-derive enablement for the block's CURRENT selection and refresh the
// 'active'/'disabled' classes on already-rendered chip buttons in place
// (does not rebuild the DOM, so the result area is left untouched).
function _rundemoUpdateBlockUI(d) {
  var block = document.getElementById('rundemo-block-' + d.idx);
  if (!block) return;
  var sel = RUNDEMO.sel[d.idx];
  if (!sel) return;
  var avail = d.avail || {};

  var syncNow = _rundemoSyncEnabled(d, avail, sel.code);
  var asyncNow = _rundemoAsyncEnabled(d, avail, sel.code);
  // Self-correct the selected mode if the Code toggle just disabled it —
  // prefer switching to whichever mode IS enabled; if neither is enabled
  // (edge case), leave sel.mode as-is (rundemoRun guards against dispatch).
  if (sel.mode === 'async' && !asyncNow) sel.mode = syncNow ? 'sync' : sel.mode;
  else if (sel.mode === 'sync' && !syncNow) sel.mode = asyncNow ? 'async' : sel.mode;
  var postNow = _rundemoPostEnabled(avail, sel.code, sel.mode);
  if (sel.post && !postNow) sel.post = false;

  block.querySelectorAll('.rundemo-chipgroup').forEach(function (grp) {
    var axis = grp.getAttribute('data-axis');
    grp.querySelectorAll('.rundemo-chip').forEach(function (btn) {
      var val = btn.getAttribute('data-val');
      var disabled = false;
      if (axis === 'mode' && val === 'sync') disabled = !syncNow;
      else if (axis === 'mode' && val === 'async') disabled = !asyncNow;
      else if (axis === 'post' && val === 'on') disabled = !postNow;
      else if (axis === 'input' && val === 'bin') disabled = true; // fixed, non-selectable
      btn.disabled = disabled;
      btn.classList.toggle('disabled', disabled);
      btn.setAttribute('style', disabled ? _RUNDEMO_DISABLED_STYLE : '');
      var activeVal = axis === 'post' ? (sel.post ? 'on' : 'off') : sel[axis];
      btn.classList.toggle('active', val === activeVal);
    });
  });
}

// ─── PURE, TESTABLE fn: selected toggles → /api/run body ──────────────────
// demo: one entry from RUNDEMO.demos (has run_ref{model_name,category,model_file},
//       default_video, default_image). sel: {input,code,mode,post} (RUNDEMO.sel[idx]).
// Mirrors inference.js doRun()'s body shape exactly (see /api/run contract above).
function rundemoBody(demo, sel) {
  demo = demo || {};
  sel = sel || {};
  var ref = demo.run_ref || {};
  var lang = sel.code === 'cpp' ? 'cpp' : 'python';
  var variant = sel.mode || 'sync';
  if (lang === 'python' && sel.post === 'on') variant += '_cpp_postprocess';
  var input_type = sel.input === 'video' ? 'video' : 'image'; // 'image' and 'bin' both → image_path
  var body = {
    model_name: ref.model_name,
    category: ref.category,
    model_file: ref.model_file,
    lang: lang,
    variant: variant,
    input_type: input_type,
    device_id: 0,
    config_overrides: {}
  };
  if (input_type === 'video') body.video_path = demo.default_video;
  else body.image_path = demo.default_image; // covers plain image AND 3d '.bin' (sel.input==='bin')
  return body;
}
if (typeof window !== 'undefined') window.rundemoBody = rundemoBody;

// ─── Run / Stop wiring (single active run) ────────────────────────────────
RUNDEMO.running = false;
RUNDEMO.activeIdx = null;

function rundemoRun(idx) {
  var d = RUNDEMO.demos.find(function (x) { return x.idx === idx; });
  var sel = RUNDEMO.sel[idx];
  var resultEl = document.getElementById('rundemo-result-' + idx);
  if (!d || !sel || !resultEl) return;

  if (RUNDEMO.running) {
    toast(_T6('다른 데모가 실행 중입니다', 'Another demo is running', '別のデモが実行中です',
      '另一个演示正在运行', '另一個示範正在執行', 'Otra demostración está en ejecución'), 'warn');
    return;
  }

  // Defensive guard: never dispatch a variant that isn't actually available
  // (e.g. the edge case where neither sync nor async is enabled for the
  // selected code — see rundemoAvail's defaultMode comment).
  var avail = d.avail || {};
  var modeOk = sel.mode === 'async' ? _rundemoAsyncEnabled(d, avail, sel.code) : _rundemoSyncEnabled(d, avail, sel.code);
  if (!modeOk) {
    toast(_T6('선택한 모드를 사용할 수 없습니다', 'Selected mode is unavailable', '選択したモードは利用できません',
      '所选模式不可用', '所選模式不可用', 'El modo seleccionado no está disponible'), 'err');
    return;
  }

  var body = rundemoBody(d, sel);
  RUNDEMO.running = true;
  RUNDEMO.activeIdx = idx;
  window.renderInferenceSpinner(resultEl);

  // All inputs use the batch path: process file → save annotated mp4/image → return and
  // display full-size. The old live MJPEG screen-grab (Xvfb + mss) rendered quarter-size and
  // laggy via /api/live_frame polling, so it was removed. Batch produces a real playable video
  // (C++ sync / Python) at full resolution; async-C++ empty-video cases surface a Sync note.
  rundemoRunBatch(idx, d, body, resultEl);
}
if (typeof window !== 'undefined') window.rundemoRun = rundemoRun;

// Batch path: POST /api/run, render the saved result (image, or Python-saved video mp4).
// Also the graceful fallback when live streaming isn't available on this board.
function rundemoRunBatch(idx, d, body, resultEl) {
  // runWithProgress (defined in inference.js) shows a live progress bar via /api/run_async,
  // falling back to the blocking /api/run; returns the same result shape either way.
  var _run = (typeof runWithProgress === 'function')
    ? runWithProgress(body, resultEl)
    : (window.renderInferenceSpinner(resultEl), postJ('/api/run', body));
  _run.then(function (res) {
    if (!res || res.error) {
      var errMsg = (res && (res.error || res.message)) || _T6('알 수 없는 오류', 'Unknown error', '不明なエラー', '未知错误', '未知錯誤', 'Error desconocido');
      window.renderInferenceError(resultEl, errMsg, '');
      return;
    }
    res._isVideo = (body.input_type === 'video');
    res._cat = d.run_ref.category;
    res._beforeSrc = null; // Run Demo has no before/after compare — plain result image
    window.renderInferenceResult(resultEl, res);
  }).catch(function (e) {
    // Without this, a rejected fetch (server restarted mid-run, connection dropped,
    // proxy/browser timeout on a slow C++ run) skips the .then, so the spinner is never
    // replaced → "Running inference…" spins forever. Mirror inference.js doRun's recovery.
    window.renderInferenceError(resultEl,
      (e && e.message) || _T6('요청 실패', 'Request failed', 'リクエスト失敗', '请求失败', '請求失敗', 'Solicitud fallida'), '');
  }).finally(function () {
    RUNDEMO.running = false;
    RUNDEMO.activeIdx = null;
  });
}
if (typeof window !== 'undefined') window.rundemoRunBatch = rundemoRunBatch;

// Live-stream a video demo: start a C++ live job (renders to Xvfb), show its MJPEG frames
// via <img src="/api/live_frame">, and poll /api/live_poll for the example's own perf log.
function rundemoRunLive(idx, d, body, resultEl) {
  var liveBody = {
    model_name: body.model_name, category: body.category, model_file: body.model_file,
    lang: 'cpp',   // live streaming is C++ only (renders annotated frames to the display)
    variant: (body.variant || 'sync').replace('_cpp_postprocess', ''),
    input_type: 'video', video_path: body.video_path,
    device_id: 0, slot_idx: 0, n_total_slots: 1
  };
  var _clear = function () { RUNDEMO.running = false; RUNDEMO.activeIdx = null; };
  postJ('/api/run_live', liveBody).then(function (res) {
    if (!res || res.error) {
      // ANY live failure → fall back to the batch save-then-return path, which reliably
      // produces a playable output video with zero extra deps. Previously only three
      // error_keys triggered the fallback (live_deps_missing / binary_not_found /
      // live_cpp_only); any other live error just showed a message with NO video — e.g. a
      // demo whose live start fails for an unlisted reason (superpoint on a board without
      // Xvfb) would silently show nothing even though its batch run works fine.
      rundemoRunBatch(idx, d, body, resultEl);   // batch (C++ --save / Python save) → playable mp4
      return;
    }
    var jobId = res.job_id;
    resultEl.innerHTML =
      '<div class="rundemo-live">' +
      '<img id="rundemo-live-img-' + idx + '" src="/api/live_frame?slot=0&t=' + Date.now() + '" ' +
        'style="width:100%;display:block;border-radius:8px;background:#000" alt="live"/>' +
      '<div id="rundemo-live-perf-' + idx + '" class="rundemo-live-perf txt-xs txt-dim mt8"></div>' +
      '<button class="btn btn-sm mt8" onclick="rundemoStopLive(' + idx + ')">■ ' +
        _T6('중지', 'Stop', '停止', '停止', '停止', 'Detener') + '</button>' +
      '</div>';
    if (RUNDEMO._live && RUNDEMO._live.pollInt) clearInterval(RUNDEMO._live.pollInt);
    RUNDEMO._live = { idx: idx, jobId: jobId, pollInt: null };
    RUNDEMO._live.pollInt = setInterval(function () {
      api('/api/live_poll?id=' + jobId).then(function (p) {
        if (!p || p.error) return;
        var perf = document.getElementById('rundemo-live-perf-' + idx);
        if (perf) {
          var preds = (p.last_pred || []).slice(0, 3).join(', ');
          perf.textContent = (p.task_summary || '') +
            '  |  FPS ~' + (p.fps_est != null ? p.fps_est : '—') +
            '  |  ' + _T6('프레임', 'frames', 'フレーム', '帧', '幀', 'frames') + ' ' + (p.frames || 0) +
            (preds ? '  |  ' + preds : '');
        }
        if (!p.running) rundemoStopLive(idx);   // job ended (video finished / crashed)
      }).catch(function () {});
    }, 1000);
  }).catch(function () {
    // Network/transport failure starting the live job → fall back to batch too (never leave
    // the user with a spinner-then-error and no video when batch would work).
    rundemoRunBatch(idx, d, body, resultEl);
  });
}
if (typeof window !== 'undefined') window.rundemoRunLive = rundemoRunLive;

function rundemoStopLive(idx) {
  if (RUNDEMO._live && RUNDEMO._live.pollInt) clearInterval(RUNDEMO._live.pollInt);
  RUNDEMO._live = null;
  postJ('/api/live_stop', { slot_idx: 0 }).catch(function () {});
  RUNDEMO.running = false;
  RUNDEMO.activeIdx = null;
  var img = document.getElementById('rundemo-live-img-' + idx);
  if (img) img.removeAttribute('src');   // close the MJPEG connection
}
if (typeof window !== 'undefined') window.rundemoStopLive = rundemoStopLive;

function rundemoStop() {
  // If a live video job is streaming, stop it via the live path (not the batch /api/stop).
  if (RUNDEMO._live) { rundemoStopLive(RUNDEMO._live.idx); return; }
  postJ('/api/stop', {}).then(function () {
    var idx = RUNDEMO.activeIdx;
    RUNDEMO.running = false;
    RUNDEMO.activeIdx = null;
    if (idx != null) {
      var resultEl = document.getElementById('rundemo-result-' + idx);
      if (resultEl) resultEl.innerHTML = '';
    }
    toast(_T6('중지됨', 'Stopped', '停止しました', '已停止', '已停止', 'Detenido'), 'info');
  });
}
if (typeof window !== 'undefined') window.rundemoStop = rundemoStop;

// Click handler for every toggle option in every block.
function _rundemoToggle(idx, axis, val) {
  var d = RUNDEMO.demos.find(function (x) { return x.idx === idx; });
  var sel = RUNDEMO.sel[idx];
  if (!d || !sel) return;
  var av = rundemoAvail(d);

  if (axis === 'input') {
    if (val === 'bin') return; // fixed chip, not selectable
    if (val === 'video' && !av.input.video) return;
    if (val === 'image' && !av.input.image) return;
    sel.input = val;
  } else if (axis === 'code') {
    if (val === 'python' && !av.code.python) return;
    if (val === 'cpp' && !av.code.cpp) return;
    sel.code = val; // mode/post enablement is code-dependent — recomputed below
  } else if (axis === 'mode') {
    if (val === 'sync' && !_rundemoSyncEnabled(d, d.avail || {}, sel.code)) return;
    if (val === 'async' && !_rundemoAsyncEnabled(d, d.avail || {}, sel.code)) return;
    sel.mode = val; // post enablement is mode-dependent — recomputed below
  } else if (axis === 'post') {
    var wantOn = val === 'on';
    if (wantOn && !_rundemoPostEnabled(d.avail || {}, sel.code, sel.mode)) return;
    sel.post = wantOn;
  }
  _rundemoUpdateBlockUI(d);
}
if (typeof window !== 'undefined') window._rundemoToggle = _rundemoToggle;

// Node smoke-test hook: expose rundemoAvail via module.exports when running
// under node (see the throwaway assertion script used during development;
// no test code is left resident in this file beyond this guard).
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { rundemoAvail: rundemoAvail, rundemoBody: rundemoBody, runnable: runnable };
}
