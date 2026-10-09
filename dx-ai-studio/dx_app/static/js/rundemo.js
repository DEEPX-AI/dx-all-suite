// dx_app/static/js/rundemo.js
// Run Demo GUI: fetch /api/demos and lay them out on the shared demo stage
// (shared/static/dx-demo-stage.js, spec 2026-10-01): a result stage on top
// (preview · options · Run · result) and cards below that only choose which
// demo the stage shows. Options are segmented toggles (input/code/mode/post)
// gated by each demo's real availability; Run maps them to an /api/run body
// (rundemoBody) and paints the result dict on the stage.
'use strict';

var RUNDEMO = { loaded: false, demos: [], groups: [], sel: {}, results: {}, ctl: null, stage: null, current: null, runSeq: 0 };
// sel[idx] = {input,code,mode,post}; results[idx] = {res, isVideo} | {error} — the last run of
// that demo, shown again when the demo is reopened on the stage.

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
  // demo.media = which sample files are on disk (/api/demos). A sample that isn't downloaded is
  // never the default and can't be picked — Run would only answer "File not found".
  var media = demo.media || {};
  if (demo.category === '3d_object_detection') {
    input.bin = true; // fixed .bin chip — no video/image for this task
  } else {
    input.image = media.image !== false;
    input.video = !demo.image_only && media.video !== false;
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

// ─── render (shared demo stage) ────────────────────────────────────────────
function rundemoRender(demos, groups) {
  var root = document.getElementById('rundemo-root');
  if (!root) return;
  if (!window.DXDemoStage) { root.textContent = ''; return; }
  var byGroup = {};
  demos.forEach(function (d) { (byGroup[d.group] = byGroup[d.group] || []).push(d); });
  var order = ((groups && groups.length) ? groups : Object.keys(byGroup)).filter(function (g) {
    return (byGroup[g] || []).length;
  });
  var list = [];
  order.forEach(function (g) { list = list.concat(byGroup[g]); });
  if (!list.length) {
    root.innerHTML = '<div class="txt-dim txt-sm" style="padding:20px">'
      + esc(_T6('데모가 없습니다.', 'No demos.', 'デモがありません。', '暂无演示。', '暫無示範。', 'No hay demostraciones.'))
      + '</div>';
    return;
  }
  list.forEach(function (d) {
    var av = rundemoAvail(d);
    RUNDEMO.sel[d.idx] = runnable(d)
      ? { input: av.defaults.input, code: av.defaults.code, mode: av.defaults.mode, post: av.defaults.post }
      : null;
  });
  RUNDEMO.ctl = window.DXDemoStage.mount(root, {
    items: list.map(_rundemoItem),
    filters: [{ key: 'all', label: 'All' }].concat(order.map(function (g) { return { key: g, label: g }; })),
    labels: _rundemoLabels(),
    onSelect: function (item, stage) { _rundemoOpen(+item.id, stage); },
    onSetup: function () { if (typeof nav === 'function') nav('setup'); },
    onRender: _rundemoTranslate
  });
}
if (typeof window !== 'undefined') window.rundemoRender = rundemoRender;

function _rundemoLabels() {
  return {
    setup: _T6('설정하기', 'Set up', 'セットアップ', '去设置', '前往設定', 'Configurar'),
    none: _T6('Setup에서 모델을 설치하면 데모를 실행할 수 있습니다.', 'Install a model in Setup to run a demo.',
      'Setup でモデルをインストールするとデモを実行できます。', '在 Setup 中安装模型即可运行演示。',
      '在 Setup 中安裝模型即可執行示範。', 'Instale un modelo en Setup para ejecutar una demo.'),
    ready: _T6('준비됨', 'Ready', '準備完了', '就绪', '就緒', 'Listo'),
    running: _T6('실행 중', 'Running', '実行中', '运行中', '執行中', 'En ejecución'),
    unready: _T6('설치 필요', 'Needs setup', 'セットアップが必要', '需要安装', '需要安裝', 'Requiere instalación')
  };
}

// 언어가 바뀌면 card 의 글자와 열린 demo 의 panel 만 다시 — 고른 설정 · 결과는 RUNDEMO 에 남아 있다 (A-8)
if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshRunDemoLanguage() {
    if (!RUNDEMO.ctl) return;
    RUNDEMO.ctl.relabel({ labels: _rundemoLabels(), items: RUNDEMO.demos.map(_rundemoItem) });
    var cur = RUNDEMO.ctl.current();
    var d = cur && cur.ready && RUNDEMO.stage ? _rundemoDemo(+cur.id) : null;
    if (!d) return;
    RUNDEMO.stage.opts.innerHTML = _rundemoOptsHtml(d);
    _rundemoUpdateBlockUI(d);
    _rundemoPaint(d.idx);
  });
}

// One card/stage item per demo. The reason is one short line; the file name and the fix go to
// the tooltip (사용자 결정 2026-10-01 #6).
function _rundemoItem(d) {
  var avail = d.avail || {};
  var ready = runnable(d);
  var modelMissing = avail.model_exists === false;
  var reason = modelMissing
    ? _T6('모델 미설치', 'Model not installed', 'モデル未インストール', '模型未安装', '模型未安裝', 'Modelo no instalado')
    : _T6('실행 가능한 빌드 없음', 'No runnable build', '実行可能なビルドなし', '没有可运行的构建', '沒有可執行的建置', 'Sin build ejecutable');
  var fix = modelMissing
    ? _T6('Setup의 Demo Quick Start로 설치하세요', 'use Demo Quick Start on Setup', 'Setup の Demo Quick Start でインストール',
        '请在 Setup 的 Demo Quick Start 中安装', '請在 Setup 的 Demo Quick Start 中安裝', 'use Demo Quick Start en Setup')
    : _T6('DX-APP/DX-Runtime 빌드를 먼저 완료하세요', 'complete the DX-APP/DX-Runtime build first',
        '先に DX-APP/DX-Runtime のビルドを完了', '请先完成 DX-APP/DX-Runtime 构建', '請先完成 DX-APP/DX-Runtime 建置',
        'complete primero el build de DX-APP/DX-Runtime');
  return {
    id: String(d.idx),
    title: _rundemoTitle(d),
    category: d.group,
    task: { icon: _rundemoTaskIcoName(d), label: _rundemoTaskName(d) },
    thumb: d.thumbnail || '',
    ready: ready,
    sub: d.model || (d.run_ref && d.run_ref.model_file) || '',
    reason: ready ? '' : reason,
    reasonTitle: ready ? '' : (reason + ': ' + (d.model || d.model_name || '') + ' — ' + fix)
  };
}

// task 아이콘은 Model Zoo 와 같은 한 표 (sprite 의 task-<key>, 아이콘 체계 단계 3). 두 task 를 묶은 데모
// (object_detection_x_semantic_segmentation) 는 앞의 task 로.
function _rundemoTaskIcoName(d) {
  var cat = String((d.run_ref && d.run_ref.category) || d.category || '').split('_x_')[0];
  return /^[a-z0-9_]+$/.test(cat) ? 'task-' + cat : 'models';
}
function _rundemoIco(name, cls) {
  return (typeof window.DXIcon === 'function') ? window.DXIcon(name, cls ? { cls: cls } : undefined) : '';
}
// 라벨은 "Object Detection   (YOLOv7)" — 앞은 task, 괄호 안은 모델. card 는 task 를 한 번, 제목에는 모델만
// 쓴다 (사용자 확정 2026-09-29).
function _rundemoSplitLabel(d) {
  var m = /^(.*?)\s*\(([^)]*)\)\s*$/.exec(String(d.label || ''));
  return m ? { task: m[1].trim(), model: m[2].trim() } : { task: d.group || '', model: String(d.label || d.model_name || '') };
}
function _rundemoTitle(d) { return _rundemoSplitLabel(d).model; }
function _rundemoTaskName(d) { return _rundemoSplitLabel(d).task; }

// task 이름 · group 이름은 그린 뒤 data-i18n 을 붙인다 — 언어를 바꾸면 공용 applyLang 이 제자리에서
// 바꾼다 (card 를 다시 그리면 고른 입력 · 모드와 결과가 사라진다). 마크업 문자열에 data-i18n 을 직접 쓰지
// 않는 것은 정적 검사 (tests/test_i18n_span_gate.py) 가 그 식을 사전 key 로 읽기 때문이다.
function _rundemoTranslate(el) {
  el.querySelectorAll('.dds-task > span, .dds-fbtn').forEach(function (s) {
    if (!s.hasAttribute('data-i18n')) s.setAttribute('data-i18n', s.textContent);
  });
  if (window.DXI18n && typeof window.DXI18n.applyLang === 'function') window.DXI18n.applyLang(el);
}

function _rundemoDemo(idx) {
  return RUNDEMO.demos.find(function (x) { return x.idx === idx; });
}

// One option row: label + segmented buttons, plain text (spec: not the old monospace INPUT/CODE).
function _rundemoAxisHtml(axis, options, activeVal, axisLabel) {
  var btns = options.map(function (o) {
    return '<button type="button" class="' + (o.val === activeVal ? 'is-on' : '') + '" data-axis="' + axis
      + '" data-val="' + esc(o.val) + '"' + (o.disabled ? ' disabled' : '') + (o.title ? ' title="' + esc(o.title) + '"' : '')
      + '>' + esc(o.label) + '</button>';
  }).join('');
  return '<div class="dds-opt" data-axis-row="' + axis + '">'
    + '<span class="dds-opt-label">' + esc(axisLabel) + '</span>'
    + '<div class="dds-seg" data-axis="' + axis + '">' + btns + '</div></div>';
}

function _rundemoOptsHtml(d) {
  var av = rundemoAvail(d);
  var sel = RUNDEMO.sel[d.idx];
  var h = '';
  if (av.input.bin) {
    h += _rundemoAxisHtml('input', [{ val: 'bin', label: '.bin', disabled: true }], 'bin',
      _T6('입력', 'Input', '入力', '输入', '輸入', 'Entrada'));
  } else {
    var media = d.media || {};
    var notDl = function (f) {
      return _T6('샘플을 받지 않았습니다', 'Sample not downloaded', 'サンプル未ダウンロード', '示例未下载', '範例未下載',
        'Muestra no descargada') + (f ? ': ' + f : '');
    };
    h += _rundemoAxisHtml('input', [
      { val: 'video', label: _T6('영상', 'Video', '動画', '视频', '影片', 'Video'), disabled: !av.input.video,
        title: media.video === false && !d.image_only ? notDl(d.default_video) : '' },
      { val: 'image', label: _T6('이미지', 'Image', '画像', '图片', '圖片', 'Imagen'), disabled: !av.input.image,
        title: media.image === false ? notDl(d.default_image) : '' }
    ], sel.input, _T6('입력', 'Input', '入力', '输入', '輸入', 'Entrada'));
  }
  h += _rundemoAxisHtml('code', [
    { val: 'python', label: 'Python', disabled: !av.code.python },
    { val: 'cpp', label: 'C++', disabled: !av.code.cpp }
  ], sel.code, _T6('구현', 'Code', '実装', '实现', '實作', 'Código'));
  h += _rundemoAxisHtml('mode', [
    { val: 'sync', label: _T6('동기', 'Sync', '同期', '同步', '同步', 'Síncrono'), disabled: !av.mode.sync },
    { val: 'async', label: _T6('비동기', 'Async', '非同期', '异步', '異步', 'Asíncrono'), disabled: !av.mode.async }
  ], sel.mode, _T6('모드', 'Mode', 'モード', '模式', '模式', 'Modo'));
  if (av.post) {
    h += _rundemoAxisHtml('post', [
      { val: 'off', label: _T6('끄기', 'Off', 'オフ', '关闭', '關閉', 'Desactivado') },
      { val: 'on', label: 'C++', disabled: !_rundemoPostEnabled(d.avail || {}, sel.code, sel.mode) }
    ], sel.post ? 'on' : 'off', _T6('후처리', 'Postprocess', '後処理', '后处理', '後處理', 'Postproceso'));
  }
  return h;
}

// The stage opened this demo (card click, or the first ready one on load).
function _rundemoOpen(idx, stage) {
  var d = _rundemoDemo(idx);
  if (!d || !RUNDEMO.sel[idx]) return;
  RUNDEMO.current = idx;
  RUNDEMO.stage = stage;            // mount() opens the first demo before it returns the controller
  if (!stage.opts._rdWired) {       // the panel elements live as long as the stage — wire once
    stage.opts._rdWired = true;
    stage.opts.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-axis]');
      if (b && !b.disabled && RUNDEMO.current != null) _rundemoToggle(RUNDEMO.current, b.dataset.axis, b.dataset.val);
    });
    stage.actions.addEventListener('click', function (e) {
      var b = e.target.closest('.dds-run');
      if (!b || RUNDEMO.current == null) return;
      if (b.classList.contains('is-stop')) rundemoStop();
      else rundemoRun(RUNDEMO.current);
    });
  }
  stage.opts.innerHTML = _rundemoOptsHtml(d);
  _rundemoUpdateBlockUI(d);
  _rundemoPaint(idx);
}

// Re-derive enablement for the demo's CURRENT selection and refresh the stage's toggle buttons
// in place (does not rebuild the stage, so a shown result stays).
function _rundemoUpdateBlockUI(d) {
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
  if (RUNDEMO.current !== d.idx || !RUNDEMO.stage) return;
  RUNDEMO.stage.opts.querySelectorAll('button[data-axis]').forEach(function (btn) {
    var axis = btn.getAttribute('data-axis'), val = btn.getAttribute('data-val');
    var disabled = btn.disabled;
    if (axis === 'mode' && val === 'sync') disabled = !syncNow;
    else if (axis === 'mode' && val === 'async') disabled = !asyncNow;
    else if (axis === 'post' && val === 'on') disabled = !postNow;
    else if (axis === 'input' && val === 'bin') disabled = true; // fixed, non-selectable
    btn.disabled = disabled;
    var activeVal = axis === 'post' ? (sel.post ? 'on' : 'off') : sel[axis];
    btn.classList.toggle('is-on', val === activeVal);
  });
}

function _rundemoRunBtn(stop) {
  return stop
    ? '<button type="button" class="dds-run is-stop">' + _rundemoIco('stop', 'dds-ico') + '<span>'
      + esc(_T6('중지', 'Stop', '停止', '停止', '停止', 'Detener')) + '</span></button>'
    : '<button type="button" class="dds-run">' + _rundemoIco('play', 'dds-ico') + '<span>'
      + esc(_T6('실행', 'Run', '実行', '运行', '執行', 'Ejecutar')) + '</span></button>';
}

function _rundemoPreview(d, dim) {
  return d.thumbnail ? '<img class="dds-preview' + (dim ? ' is-dim' : '') + '" src="' + esc(d.thumbnail) + '" alt="">' : '';
}

// 비동기 실행은 프레임별 NPU 지연을 재지 않아 "0.00" 을 돌려준다. 0 은 측정값이 아니므로 — 로 보인다 (release audit A-17).
function _rundemoNum(v, unit) {
  return (v === undefined || v === null || v === '' || !(parseFloat(v) > 0)) ? '—' : (v + (unit ? ' ' + unit : ''));
}

// Paint the stage for demo idx: running (progress over the preview) · a finished result · ready.
function _rundemoPaint(idx) {
  var st = RUNDEMO.stage;
  if (!st || RUNDEMO.current !== idx) return;
  var d = _rundemoDemo(idx);
  st.setMetrics([]); st.setBars([]); st.extra.innerHTML = '';
  if (RUNDEMO.running && RUNDEMO.activeIdx === idx) {
    st.setMedia(_rundemoPreview(d, true));
    var ov = document.createElement('div');
    ov.className = 'dds-overlay';
    if (RUNDEMO.prog) ov.appendChild(RUNDEMO.prog);
    st.media.appendChild(ov);
    st.setState('running', _T6('실행 중', 'Running', '実行中', '运行中', '執行中', 'En ejecución'));
    st.actions.innerHTML = _rundemoRunBtn(true);
    return;
  }
  st.actions.innerHTML = _rundemoRunBtn(false);
  var out = RUNDEMO.results[idx];
  if (!out) {
    st.setMedia(_rundemoPreview(d, false));
    st.setState('ready', _T6('준비됨', 'Ready', '準備完了', '就绪', '就緒', 'Listo'));
    return;
  }
  if (out.error) {
    st.setMedia(_rundemoPreview(d, true));
    st.setState('failed', _T6('실패', 'Failed', '失敗', '失败', '失敗', 'Falló'));
    st.extra.innerHTML = '<p class="dds-note is-error">' + _rundemoIco('x', 'dds-ico') + '<span>' + esc(out.error) + '</span></p>';
    return;
  }
  var r = out.res;
  if (r.result_video_url) {
    st.setMedia('<video src="' + esc(r.result_video_url) + '" controls autoplay muted loop playsinline></video>');
  } else if (r.result_image && !out.isVideo) {
    st.setMedia('<img src="data:image/jpeg;base64,' + r.result_image + '" alt="result" onclick="previewImg(this.src)">');
  } else {
    st.setMedia(_rundemoPreview(d, true));
  }
  st.setMetrics([
    { value: _rundemoNum(r.fps), label: 'FPS', accent: true },
    { value: _rundemoNum(r.latency, 'ms'), label: _T6('NPU 지연', 'NPU latency', 'NPU レイテンシ', 'NPU 延迟', 'NPU 延遲', 'Latencia NPU') },
    { value: _rundemoNum(r.elapsed_s, 's'), label: _T6('전체', 'Total', '合計', '总计', '總計', 'Total') }
  ]);
  var pipe = (r.perf && r.perf.pipeline) || [];
  st.setBars(pipe.map(function (p) { return { label: p.step, ms: p.latency_ms }; }));
  var ok = r.exit_code === 0;
  st.setState(ok ? 'done' : 'failed', ok ? _T6('완료', 'Done', '完了', '完成', '完成', 'Completado')
    : _T6('비정상 종료', 'Exited', '異常終了', '异常退出', '異常結束', 'Salida anómala') + ' (' + r.exit_code + ')');
  var x = '';
  if (r.video_note && !r.result_video_url) {
    x += '<p class="dds-note is-warn">' + _rundemoIco('alert', 'dds-ico') + '<span>' + esc(T(r.video_note)) + '</span></p>';
  }
  if (!ok) {
    x += '<p class="dds-note is-error">' + _rundemoIco('alert', 'dds-ico') + '<span>'
      + esc(T('Inference exited abnormally (exit code: ') + r.exit_code + T('). Check Full Output for details.')) + '</span></p>';
  }
  if (r.output) {
    x += '<details><summary>' + esc(_T6('전체 출력', 'Full output', '全出力', '完整输出', '完整輸出', 'Salida completa'))
      + '</summary><pre>' + esc(r.output) + '</pre></details>';
  }
  st.extra.innerHTML = x;
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
  var d = _rundemoDemo(idx);
  var sel = RUNDEMO.sel[idx];
  if (!d || !sel) return;

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

  // sel.post is a boolean; rundemoBody's contract is the toggle value ('on' / 'off').
  var body = rundemoBody(d, { input: sel.input, code: sel.code, mode: sel.mode, post: sel.post ? 'on' : 'off' });
  RUNDEMO.running = true;
  RUNDEMO.activeIdx = idx;
  RUNDEMO.results[idx] = null;
  // The progress block lives outside the stage so it survives switching to another demo and back.
  RUNDEMO.prog = document.createElement('div');
  if (RUNDEMO.ctl) RUNDEMO.ctl.setRunning(String(idx));
  _rundemoPaint(idx);

  // All inputs use the batch path: process file → save annotated mp4/image → return and
  // display full-size. Batch produces a real playable video (C++ sync / Python) at full
  // resolution; async-C++ empty-video cases surface a Sync note.
  rundemoRunBatch(idx, d, body, RUNDEMO.prog);
}
if (typeof window !== 'undefined') window.rundemoRun = rundemoRun;

// Batch path: POST /api/run (via runWithProgress), keep the result for this demo and paint it
// on the stage if the demo is still the one shown.
function rundemoRunBatch(idx, d, body, progEl) {
  var seq = ++RUNDEMO.runSeq;
  // runWithProgress (defined in inference.js) shows a live progress bar via /api/run_async,
  // falling back to the blocking /api/run; returns the same result shape either way.
  var _run = (typeof runWithProgress === 'function')
    ? runWithProgress(body, progEl)
    : (window.renderInferenceSpinner(progEl), postJ('/api/run', body));
  function _done(out) {
    if (seq !== RUNDEMO.runSeq) return;      // stopped (or superseded) — drop the late result
    RUNDEMO.results[idx] = out;
    RUNDEMO.running = false;
    RUNDEMO.activeIdx = null;
    RUNDEMO.prog = null;
    if (RUNDEMO.ctl) RUNDEMO.ctl.setRunning(null);
    _rundemoPaint(idx);
  }
  _run.then(function (res) {
    if (!res || res.error) {
      _done({ error: (res && (res.error || res.message)) || _T6('알 수 없는 오류', 'Unknown error', '不明なエラー', '未知错误', '未知錯誤', 'Error desconocido') });
      return;
    }
    _done({ res: res, isVideo: body.input_type === 'video' });
  }).catch(function (e) {
    // Without this, a rejected fetch (server restarted mid-run, connection dropped,
    // proxy/browser timeout on a slow C++ run) would leave the stage spinning forever.
    _done({ error: (e && e.message) || _T6('요청 실패', 'Request failed', 'リクエスト失敗', '请求失败', '請求失敗', 'Solicitud fallida') });
  });
}
if (typeof window !== 'undefined') window.rundemoRunBatch = rundemoRunBatch;


function rundemoStop() {
  postJ('/api/stop', {}).then(function () {
    var idx = RUNDEMO.activeIdx;
    RUNDEMO.runSeq++;                 // the stopped run's late result is dropped
    RUNDEMO.running = false;
    RUNDEMO.activeIdx = null;
    RUNDEMO.prog = null;
    if (RUNDEMO.ctl) RUNDEMO.ctl.setRunning(null);
    if (idx != null) { RUNDEMO.results[idx] = null; _rundemoPaint(idx); }
    toast(_T6('중지됨', 'Stopped', '停止しました', '已停止', '已停止', 'Detenido'), 'info');
  });
}
if (typeof window !== 'undefined') window.rundemoStop = rundemoStop;

// Click handler for every toggle option on the stage.
function _rundemoToggle(idx, axis, val) {
  var d = _rundemoDemo(idx);
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

// Node smoke-test hook: expose the pure fns via module.exports when running under node.
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { rundemoAvail: rundemoAvail, rundemoBody: rundemoBody, runnable: runnable };
}
