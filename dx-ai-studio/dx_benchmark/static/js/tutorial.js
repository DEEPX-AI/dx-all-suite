/* ═══════════════════════════════════════════════════════════════
   DX Benchmark — Tutorial Definitions v2.1
   10 sections, 60 steps, 6-language support (ko/en/ja/zh-CN/zh-TW/es)
   - v2.0: 동적 요소 가드 보강, 깨진 셀렉터 수정, 누락 기능 18개 스텝 추가,
           차트/로그 position 수정, 챗봇 beforeStep 타이밍 보정
   - v2.1: redesigned-dashboard rework (Task 7) — new "ORT ON/OFF" section
           (dashboard-ort), Detailed Data thermal/throttle + run Status
           columns step, Full Metrics NPU identity (Product/SKU/Modules/
           Device Count) step. Version-Trend targets already repointed by
           5a fix — verified still correct, left untouched.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  function switchTab(t) { if (typeof BenchApp !== 'undefined') BenchApp.switchTab(t); }

  function _scrollTo(sel) {
    var el = document.querySelector(sel);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function _openOverviewEnvDetail() {
    switchTab('dashboard');
    var tab = document.querySelector('.dashboard-tab[data-tab="overview"]');
    if (tab) tab.click();
    if (typeof refreshChart === 'function') refreshChart();
  }

  function _openFpsEnvDetail() {
    switchTab('dashboard');
    var tab = document.querySelector('.dashboard-tab[data-tab="fps-compare"]');
    if (tab) tab.click();
    if (typeof refreshFpsCompare === 'function') refreshFpsCompare();
  }

  function _ensureEdgeGuideLink() {
    _openOverviewEnvDetail();
    var link = document.querySelector('#envDetail .edgeguide-link, #fpsEnvDetail .edgeguide-link');
    if (!link) {
      var panel = document.getElementById('envDetail') || document.getElementById('fpsEnvDetail');
      if (panel) {
        var stub = document.createElement('a');
        stub.className = 'edgeguide-link';
        stub.href = '#';
        stub.textContent = 'EdgeGuide (tutorial demo)';
        panel.appendChild(stub);
      }
    }
  }

  // ── Tutorial mock helpers ────────────────────────────────────────────
  // Some panels/sections only appear after a transient interaction the tour
  // cannot perform on demand: clicking a trend-chart POINT reveals the
  // snapshot env-detail + model-meta panels; clicking a RUN ITEM renders the
  // result sections (+ optional Markdown report). Mirror the dx_app /
  // dx_modelzoo pattern: inject a clearly-labelled "Tutorial preview" into the
  // REAL container so each step has a real, visible element to spotlight, then
  // clear it on step exit (afterStep).
  function _lang() { return localStorage.getItem('dx-lang') || 'en'; }
  function _lc(m) { return m[_lang()] || m.en; }
  var _PREVIEW = { ko:'튜토리얼 미리보기', en:'Tutorial preview', ja:'チュートリアルプレビュー', 'zh-CN':'教程预览', 'zh-TW':'教程預覽', es:'Vista previa del tutorial' };
  function _previewBadge() {
    return '<span class="tag tag--warn" style="font-size:11px;margin-left:6px">🔎 ' + _lc(_PREVIEW) + '</span>';
  }
  function _infoRowsHtml(rows) {
    return rows.map(function (r) {
      return '<div class="info-row"><span class="info-key">' + r[0] + '</span><span class="info-val">' + r[1] + '</span></div>';
    }).join('');
  }

  // Issue 6 — shared, formatted command block (identical across all languages).
  // The tooltip body has no <pre>/<code> styling, so a bare multi-line block
  // rendered as run-on text. Style it inline as a real fenced code block.
  var _RUN_CODE =
    '<pre style="background:#0d1117;border:1px solid #30363d;border-radius:6px;' +
    'padding:10px 12px;margin:8px 0;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;' +
    'font-size:12px;line-height:1.7;white-space:pre;overflow-x:auto;color:#c9d1d9"><code>cd dx-benchmark\n' +
    './run.sh run</code></pre>';

  // Issues 1 & 2 — trend snapshot panels (revealed by clicking a chart point).
  function _revealTrendSnapshot() {
    var env = document.getElementById('trendEnvDetail');
    if (env) {
      env.style.display = '';
      env.setAttribute('data-dxt-mock', '1');
      var t = document.getElementById('trendEnvDetailTitle');
      if (t) t.innerHTML = 'E2E FPS · DX-M1 · v2.9.0 · run_demo' + _previewBadge();
      var host = document.getElementById('trendEnvHostInfo');
      if (host) host.innerHTML = _infoRowsHtml([['Hostname', 'dx-host'], ['OS', 'Ubuntu 22.04'], ['CPU', 'x86_64'], ['RAM', '32 GB']]);
      var npu = document.getElementById('trendEnvNpuInfo');
      if (npu) npu.innerHTML = _infoRowsHtml([['Product', 'DX-M1'], ['DXRT', '2.9.0'], ['Firmware', '2.1.0'], ['Memory', '4 GB']]);
      var tools = document.getElementById('trendEnvToolsInfo');
      if (tools) tools.innerHTML = _infoRowsHtml([['dx_stream', '1.8.0'], ['GStreamer', '1.20.3']]);
    }
    var meta = document.getElementById('trendModelMetaPanel');
    if (meta) {
      meta.style.display = '';
      meta.setAttribute('data-dxt-mock', '1');
      var mt = document.getElementById('trendModelMetaTitle');
      if (mt) mt.innerHTML = 'Benchmarked Models – Object Detection · run_demo' + _previewBadge();
      var sec = document.getElementById('trendModelMetaSection');
      if (sec) sec.innerHTML = '<table class="summary-table bench-table"><thead><tr><th>Model</th><th>Size</th><th>Input</th><th>NPU Mem (MB)</th><th>DXNN Format</th></tr></thead><tbody>' +
        '<tr><td>YOLOv5</td><td>S</td><td>640×640</td><td>28</td><td>6</td></tr>' +
        '<tr><td>YOLOv5</td><td>M</td><td>640×640</td><td>52</td><td>6</td></tr>' +
        '</tbody></table>';
    }
  }
  function _mockTrendSnapshot() {
    switchTab('dashboard');
    var tab = document.querySelector('.dashboard-tab[data-tab="version-trend"]');
    if (tab) tab.click();
    return new Promise(function (resolve) {
      var tries = 0;
      var poll = setInterval(function () {
        tries++;
        if (document.getElementById('trendEnvDetail') || tries > 25) {
          clearInterval(poll);
          _revealTrendSnapshot();
          resolve();
        }
      }, 120);
    });
  }
  function _clearTrendSnapshot() {
    ['trendEnvDetail', 'trendModelMetaPanel'].forEach(function (id) {
      var p = document.getElementById(id);
      if (p && p.getAttribute('data-dxt-mock') === '1') {
        p.style.display = 'none';
        p.removeAttribute('data-dxt-mock');
      }
    });
  }

  // Issues 3 & 4 — result sections + Markdown report (revealed by clicking a run item).
  var _savedRunDetail = null;
  function _injectRunDetail(host) {
    if (_savedRunDetail === null) _savedRunDetail = host.innerHTML;
    var badge = _previewBadge();
    var envJson = '{\n  "hostname": "dx-host",\n  "npu_sku": "DX-M1",\n  "dxrt": "2.9.0"\n}';
    var modelJson = '{\n  "yolov5s": { "e2e_fps": 312.4, "latency_ms": 3.2 },\n  "yolov5m": { "e2e_fps": 188.1, "latency_ms": 5.3 }\n}';
    host.innerHTML =
      '<div class="run-detail" id="dxt-mock-rundetail">' +
        '<section class="result-section result-section--report" data-help-id="bench-result-report">' +
          '<h2>' + _tl('View Report') + badge + '</h2>' +
          '<div class="report-content">' +
            '<h3>DX-M1 · run_demo</h3>' +
            '<p>Object Detection benchmark summary (2 models, ORT on).</p>' +
            '<table class="summary-table bench-table"><thead><tr><th>Model</th><th>E2E FPS</th><th>Latency (ms)</th></tr></thead><tbody>' +
              '<tr><td>YOLOv5-S</td><td>312.4</td><td>3.2</td></tr>' +
              '<tr><td>YOLOv5-M</td><td>188.1</td><td>5.3</td></tr>' +
            '</tbody></table>' +
          '</div>' +
        '</section>' +
        '<section class="result-section result-section--raw" data-help-id="bench-result-raw">' +
          '<h2>' + _tl('Raw Data') + '</h2>' +
          '<details class="result-section" open><summary>environment</summary><pre class="json-view">' + envJson + '</pre></details>' +
          '<details class="result-section" open><summary>model results</summary><pre class="json-view">' + modelJson + '</pre></details>' +
          '<details class="result-section"><summary>pipeline results</summary><pre class="json-view">{ ... }</pre></details>' +
          '<details class="result-section"><summary>multi stream results</summary><pre class="json-view">{ ... }</pre></details>' +
        '</section>' +
      '</div>';
  }
  function _mockRunDetail() {
    switchTab('results');
    return new Promise(function (resolve) {
      var tries = 0;
      var poll = setInterval(function () {
        tries++;
        var host = document.getElementById('runDetail');
        if (host) { clearInterval(poll); _injectRunDetail(host); resolve(); }
        else if (tries > 25) { clearInterval(poll); resolve(); }
      }, 120);
    });
  }
  function _clearRunDetail() {
    var host = document.getElementById('runDetail');
    if (host && _savedRunDetail !== null) { host.innerHTML = _savedRunDetail; _savedRunDetail = null; }
  }

  // _tl helper (translate label) is provided by the engine at runtime; provide
  // a safe fallback used only during static parsing/tests.
  function _tl(s) {
    try { if (window._dxTutorial && typeof window._dxTutorial._tl === 'function') return window._dxTutorial._tl(s); } catch (e) {}
    return s;
  }

  var sections = [

    { id:'dashboard-fps', icon:'📊',
      title:{ko:'📊 E2E FPS Overview', en:'📊 E2E FPS Overview', ja:'📊 E2E FPS概要', 'zh-CN':'📊 E2E FPS概览', 'zh-TW':'📊 E2E FPS概述', es:'📊 Resumen E2E FPS'},
      description:{ko:'전체 플랫폼의 E2E FPS를 한눈에 비교하는 대시보드', en:'Dashboard comparing E2E FPS across all platforms at a glance', ja:'全プラットフォームのE2E FPSを一覧で比較するダッシュボード', 'zh-CN':'一目了然地比较所有平台E2E FPS的仪表盘', 'zh-TW':'一覽比較所有平台E2E FPS的儀表板', es:'Panel que compara el E2E FPS de todas las plataformas de un vistazo'},
      beforeStart: function () {
        return new Promise(function (resolve) {
          switchTab('dashboard');
          setTimeout(function () {
            var tab = document.querySelector('.dashboard-tab[data-tab="fps-compare"]');
            if (tab) tab.click();
            resolve();
          }, 400);
        });
      },
      steps:[
        { target:'.main-tab[data-tab="dashboard"]', position:'bottom',
          title:{ko:'Dashboard 탭', en:'Dashboard Tab', ja:'Dashboardタブ', 'zh-CN':'Dashboard 选项卡', 'zh-TW':'Dashboard 分頁', es:'Pestaña Dashboard'},
          content:{ko:'모든 벤치마크 데이터를 시각화하는 <strong>메인 화면</strong>입니다. 4개 서브탭(E2E FPS Overview, Full Metrics, Detailed Data, Version Trend)으로 구성되어 있습니다.', en:'The <strong>main screen</strong> that visualizes all benchmark data. It consists of 4 sub-tabs: E2E FPS Overview, Full Metrics, Detailed Data, and Version Trend.', ja:'すべてのベンチマークデータを可視化する<strong>メイン画面</strong>です。4つのサブタブ（E2E FPS Overview、Full Metrics、Detailed Data、Version Trend）で構成されています。', 'zh-CN':'这是将所有基准测试数据可视化的<strong>主界面</strong>。由4个子选项卡（E2E FPS Overview、Full Metrics、Detailed Data、Version Trend）组成。', 'zh-TW':'這是將所有基準測試資料視覺化的<strong>主畫面</strong>。由4個子分頁（E2E FPS Overview、Full Metrics、Detailed Data、Version Trend）組成。', es:'La <strong>pantalla principal</strong> que visualiza todos los datos del benchmark. Consta de 4 subpestañas: E2E FPS Overview, Full Metrics, Detailed Data y Version Trend.'} },
        { target:'.dashboard-tab[data-tab="fps-compare"]', position:'bottom',
          title:{ko:'E2E FPS Overview', en:'E2E FPS Overview', ja:'E2E FPS概要', 'zh-CN':'E2E FPS概览', 'zh-TW':'E2E FPS概述', es:'Resumen E2E FPS'},
          content:{ko:'전체 플랫폼의 <strong>E2E FPS</strong>를 한눈에 비교합니다. 그룹 바 차트로 모델 크기별 성능 차이를 직관적으로 파악할 수 있습니다.', en:'Compare <strong>E2E FPS</strong> across all platforms at a glance. Group bar charts make it intuitive to see performance differences by model size.', ja:'全プラットフォームの<strong>E2E FPS</strong>を一覧で比較します。グループバーチャートでモデルサイズ別のパフォーマンス差を直感的に把握できます。', 'zh-CN':'一目了然地比较所有平台的<strong>E2E FPS</strong>。通过分组柱状图直观了解不同模型大小的性能差异。', 'zh-TW':'一覽比較所有平台的<strong>E2E FPS</strong>。透過分組長條圖直觀了解不同模型大小的效能差異。', es:'Compare el <strong>E2E FPS</strong> de todas las plataformas de un vistazo. Los gráficos de barras agrupadas permiten ver de forma intuitiva las diferencias de rendimiento por tamaño de modelo.'} },
        { target:'#fpsRunSelectors', position:'bottom',
          title:{ko:'Run Selector', en:'Run Selector', ja:'Runセレクター', 'zh-CN':'Run选择器', 'zh-TW':'Run選擇器', es:'Selector de Run'},
          content:{ko:'각 플랫폼별로 비교할 <strong>벤치마크 실행(run)</strong>을 선택합니다. 드롭다운에서 원하는 run을 선택하면 차트가 자동으로 갱신됩니다.', en:'Select which <strong>benchmark run</strong> to compare per platform. The chart auto-updates when you select a run from the dropdown.', ja:'各プラットフォームで比較する<strong>ベンチマーク実行（run）</strong>を選択します。ドロップダウンからrunを選択するとチャートが自動更新されます。', 'zh-CN':'选择各平台要比较的<strong>基准测试运行（run）</strong>。从下拉菜单选择run后图表会自动更新。', 'zh-TW':'選擇各平台要比較的<strong>基準測試運行（run）</strong>。從下拉選單選擇run後圖表會自動更新。', es:'Seleccione qué <strong>ejecución de benchmark (run)</strong> comparar por plataforma. El gráfico se actualiza automáticamente al elegir un run en el menú desplegable.'} },
        { target:'#fpsTaskFilter', position:'bottom',
          title:{ko:'Task 필터', en:'Task Filter', ja:'Taskフィルター', 'zh-CN':'Task筛选', 'zh-TW':'Task篩選', es:'Filtro de Task'},
          content:{ko:'<strong>Object Detection, Pose, Segmentation</strong> 등 AI 태스크별 필터링을 합니다. 원하는 태스크만 선택하여 비교 범위를 좁힐 수 있습니다.', en:'Filter by AI task type such as <strong>Object Detection, Pose, Segmentation</strong>. Narrow down comparison scope by selecting desired tasks.', ja:'<strong>Object Detection、Pose、Segmentation</strong>などAIタスク別にフィルタリングします。目的のタスクだけ選択して比較範囲を絞ることができます。', 'zh-CN':'按<strong>Object Detection、Pose、Segmentation</strong>等AI任务类型进行筛选。可以只选择所需任务来缩小比较范围。', 'zh-TW':'按<strong>Object Detection、Pose、Segmentation</strong>等AI任務類型進行篩選。可以只選擇所需任務來縮小比較範圍。', es:'Filtre por tipo de tarea de IA como <strong>Object Detection, Pose, Segmentation</strong>. Restrinja el ámbito de comparación seleccionando las tareas deseadas.'} },
        { target:'#fpsOrtFilter', position:'bottom',
          title:{ko:'ORT 필터', en:'ORT Filter', ja:'ORTフィルター', 'zh-CN':'ORT筛选', 'zh-TW':'ORT篩選', es:'Filtro ORT'},
          content:{ko:'<strong>ONNX Runtime(ORT)</strong> 사용 여부로 필터링합니다. ORT On/Off 조건에 따라 FPS 차이를 비교할 수 있습니다.', en:'Filter by <strong>ONNX Runtime (ORT)</strong> usage. Compare FPS differences between ORT On/Off conditions.', ja:'<strong>ONNX Runtime（ORT）</strong>使用有無でフィルタリングします。ORT On/Off条件によるFPS差を比較できます。', 'zh-CN':'按<strong>ONNX Runtime（ORT）</strong>使用与否进行筛选。可以比较ORT开/关条件下的FPS差异。', 'zh-TW':'按<strong>ONNX Runtime（ORT）</strong>使用與否進行篩選。可以比較ORT開/關條件下的FPS差異。', es:'Filtre por uso de <strong>ONNX Runtime (ORT)</strong>. Compare las diferencias de FPS entre las condiciones ORT activado/desactivado.'} },
        { target:'#fpsCompareChart', position:'bottom',
          title:{ko:'FPS 비교 차트', en:'FPS Comparison Chart', ja:'FPS比較チャート', 'zh-CN':'FPS比较图表', 'zh-TW':'FPS比較圖表', es:'Gráfico de comparación FPS'},
          content:{ko:'모델 크기(<strong>N/S/M/L/X</strong>)별 그룹 바 차트입니다. <strong>Max Channel</strong> 배지가 표시되며, 바를 클릭하면 하단에 환경 상세 정보를 확인할 수 있습니다.', en:'Group bar chart by model size (<strong>N/S/M/L/X</strong>). Shows <strong>Max Channel</strong> badges. Click bars for environment details below.', ja:'モデルサイズ（<strong>N/S/M/L/X</strong>）別のグループバーチャートです。<strong>Max Channel</strong>バッジが表示され、バーをクリックすると下部に環境詳細情報を確認できます。', 'zh-CN':'按模型大小（<strong>N/S/M/L/X</strong>）分组的柱状图。显示<strong>Max Channel</strong>标记，点击柱形可在下方查看环境详细信息。', 'zh-TW':'按模型大小（<strong>N/S/M/L/X</strong>）分組的長條圖。顯示<strong>Max Channel</strong>標記，點擊長條可在下方查看環境詳細資訊。', es:'Gráfico de barras agrupadas por tamaño de modelo (<strong>N/S/M/L/X</strong>). Muestra insignias de <strong>Max Channel</strong>. Haga clic en las barras para ver los detalles del entorno abajo.'} },
        { target:'#fpsEnvDetail', position:'top',
          title:{ko:'환경 상세', en:'Environment Detail', ja:'環境詳細', 'zh-CN':'环境详情', 'zh-TW':'環境詳情', es:'Detalle del entorno'},
          content:{ko:'차트에서 <strong>바를 클릭</strong>하면 하단에 환경 상세 패널이 나타납니다. 클릭한 플랫폼의 <strong>Host PC, NPU, 소프트웨어</strong> 정보를 3열 레이아웃으로 확인할 수 있습니다.', en:'<strong>Click a bar</strong> in the chart to reveal the environment detail panel below. It shows <strong>Host PC, NPU, and software</strong> info in a 3-column layout for the clicked platform.', ja:'チャートで<strong>バーをクリック</strong>すると下部に環境詳細パネルが表示されます。クリックしたプラットフォームの<strong>Host PC、NPU、ソフトウェア</strong>情報を3列レイアウトで確認できます。', 'zh-CN':'在图表中<strong>点击柱形</strong>后，下方会出现环境详情面板。可以三列布局查看所点击平台的<strong>Host PC、NPU、软件</strong>信息。', 'zh-TW':'在圖表中<strong>點擊長條</strong>後，下方會出現環境詳情面板。可以三欄佈局查看所點擊平台的<strong>Host PC、NPU、軟體</strong>資訊。', es:'<strong>Haga clic en una barra</strong> del gráfico para mostrar el panel de detalle del entorno abajo. Muestra la información de <strong>Host PC, NPU y software</strong> en un diseño de 3 columnas para la plataforma seleccionada.'},
          beforeStep:function(){ _openFpsEnvDetail(); _scrollTo('#fpsEnvDetail'); } },
        { target:'#fpsModelMetaPanel', position:'top',
          title:{ko:'벤치마크 모델 정보', en:'Benchmark Model Info', ja:'ベンチマークモデル情報', 'zh-CN':'基准测试模型信息', 'zh-TW':'基準測試模型資訊', es:'Información del modelo de benchmark'},
          content:{ko:'차트 바를 클릭하면 환경 상세 아래에 <strong>모델 메타데이터 패널</strong>이 함께 나타납니다. 테스트된 모델의 <strong>입력 해상도, NPU 메모리 사용량, DXNN 포맷</strong>을 확인할 수 있습니다.', en:'Clicking a chart bar also reveals the <strong>model metadata panel</strong> below the environment detail. Check <strong>input resolution, NPU memory usage, and DXNN format</strong> of tested models.', ja:'チャートバーをクリックすると環境詳細の下に<strong>モデルメタデータパネル</strong>が表示されます。テストされたモデルの<strong>入力解像度、NPUメモリ使用量、DXNNフォーマット</strong>を確認できます。', 'zh-CN':'点击图表柱形后，环境详情下方会同时显示<strong>模型元数据面板</strong>。可以查看测试模型的<strong>输入分辨率、NPU内存使用量、DXNN格式</strong>。', 'zh-TW':'點擊圖表長條後，環境詳情下方會同時顯示<strong>模型中繼資料面板</strong>。可以查看測試模型的<strong>輸入解析度、NPU記憶體使用量、DXNN格式</strong>。', es:'Al hacer clic en una barra del gráfico también se muestra el <strong>panel de metadatos del modelo</strong> debajo del detalle del entorno. Consulte la <strong>resolución de entrada, uso de memoria NPU y formato DXNN</strong> de los modelos probados.'},
          beforeStep:function(){ _openFpsEnvDetail(); _scrollTo('#fpsModelMetaPanel'); } },
      ]
    },

    { id:'dashboard-metrics', icon:'📈',
      title:{ko:'📈 Full Metrics', en:'📈 Full Metrics', ja:'📈 Full Metrics', 'zh-CN':'📈 Full Metrics', 'zh-TW':'📈 Full Metrics', es:'📈 Full Metrics'},
      description:{ko:'NPU Throughput, E2E FPS, Latency 3중 메트릭 분석', en:'Triple metric analysis: NPU Throughput, E2E FPS, Latency', ja:'NPU Throughput、E2E FPS、Latencyのトリプルメトリクス分析', 'zh-CN':'NPU吞吐量、E2E FPS、延迟三重指标分析', 'zh-TW':'NPU吞吐量、E2E FPS、延遲三重指標分析', es:'Análisis triple de métricas: NPU Throughput, E2E FPS, Latency'},
      beforeStart: function () {
        return new Promise(function (resolve) {
          switchTab('dashboard');
          setTimeout(function () {
            var tab = document.querySelector('.dashboard-tab[data-tab="overview"]');
            if (tab) tab.click();
            resolve();
          }, 400);
        });
      },
      steps:[
        { target:'.dashboard-tab[data-tab="overview"]', position:'bottom',
          title:{ko:'Full Metrics 서브탭', en:'Full Metrics Sub-tab', ja:'Full Metricsサブタブ', 'zh-CN':'Full Metrics子选项卡', 'zh-TW':'Full Metrics子分頁', es:'Subpestaña Full Metrics'},
          content:{ko:'<strong>NPU Throughput, E2E FPS, Latency</strong> 3가지 핵심 메트릭을 동시에 비교하는 서브탭입니다. 다각적 성능 분석에 최적화되어 있습니다.', en:'A sub-tab for simultaneously comparing three core metrics: <strong>NPU Throughput, E2E FPS, Latency</strong>. Optimized for multi-dimensional performance analysis.', ja:'<strong>NPU Throughput、E2E FPS、Latency</strong>の3つのコアメトリクスを同時に比較するサブタブです。多角的なパフォーマンス分析に最適化されています。', 'zh-CN':'同时比较<strong>NPU吞吐量、E2E FPS、延迟</strong>三个核心指标的子选项卡。针对多维性能分析进行了优化。', 'zh-TW':'同時比較<strong>NPU吞吐量、E2E FPS、延遲</strong>三個核心指標的子分頁。針對多維效能分析進行了最佳化。', es:'Subpestaña para comparar simultáneamente tres métricas clave: <strong>NPU Throughput, E2E FPS, Latency</strong>. Optimizada para el análisis multidimensional del rendimiento.'} },
        { target:'#taskFilter', position:'right',
          title:{ko:'Task 필터', en:'Task Filter', ja:'Taskフィルター', 'zh-CN':'Task筛选', 'zh-TW':'Task篩選', es:'Filtro de Task'},
          content:{ko:'<strong>AI 태스크</strong>별로 벤치마크 결과를 필터링합니다. 필터를 변경하면 차트와 테이블이 즉시 갱신됩니다.', en:'Filter benchmark results by <strong>AI task</strong>. Charts and tables update immediately when filters change.', ja:'<strong>AIタスク</strong>別にベンチマーク結果をフィルタリングします。フィルターを変更するとチャートとテーブルが即座に更新されます。', 'zh-CN':'按<strong>AI任务</strong>筛选基准测试结果。更改筛选条件后图表和表格会立即更新。', 'zh-TW':'按<strong>AI任務</strong>篩選基準測試結果。更改篩選條件後圖表和表格會立即更新。', es:'Filtre los resultados del benchmark por <strong>tarea de IA</strong>. Los gráficos y tablas se actualizan al instante al cambiar los filtros.'} },
        { target:'#sizeFilter', position:'right',
          title:{ko:'Size 필터', en:'Size Filter', ja:'Sizeフィルター', 'zh-CN':'Size筛选', 'zh-TW':'Size篩選', es:'Filtro de Size'},
          content:{ko:'모델 크기(<strong>N/S/M/L/X</strong>)별 필터링입니다. 특정 모델 크기의 성능만 비교하고 싶을 때 사용합니다.', en:'Filter by model size (<strong>N/S/M/L/X</strong>). Use when you want to compare performance of a specific model size.', ja:'モデルサイズ（<strong>N/S/M/L/X</strong>）別のフィルタリングです。特定のモデルサイズのパフォーマンスだけを比較したい場合に使用します。', 'zh-CN':'按模型大小（<strong>N/S/M/L/X</strong>）进行筛选。当需要只比较特定模型大小的性能时使用。', 'zh-TW':'按模型大小（<strong>N/S/M/L/X</strong>）進行篩選。當需要只比較特定模型大小的效能時使用。', es:'Filtre por tamaño de modelo (<strong>N/S/M/L/X</strong>). Úselo cuando desee comparar el rendimiento de un tamaño de modelo concreto.'} },
        { target:'#ortFilter', position:'right',
          title:{ko:'ORT 필터', en:'ORT Filter', ja:'ORTフィルター', 'zh-CN':'ORT筛选', 'zh-TW':'ORT篩選', es:'Filtro ORT'},
          content:{ko:'<strong>ONNX Runtime(ORT)</strong> On/Off 조건으로 필터링합니다. ORT 적용에 따른 메트릭 변화를 비교할 수 있습니다.', en:'Filter by <strong>ONNX Runtime (ORT)</strong> On/Off. Compare metric changes with ORT applied.', ja:'<strong>ONNX Runtime（ORT）</strong> On/Off条件でフィルタリングします。ORT適用によるメトリクス変化を比較できます。', 'zh-CN':'按<strong>ONNX Runtime（ORT）</strong>开/关条件进行筛选。可以比较应用ORT后的指标变化。', 'zh-TW':'按<strong>ONNX Runtime（ORT）</strong>開/關條件進行篩選。可以比較套用ORT後的指標變化。', es:'Filtre por <strong>ONNX Runtime (ORT)</strong> activado/desactivado. Compare los cambios de métricas con ORT aplicado.'} },
        { target:'#mainChart', position:'top',
          title:{ko:'3중 메트릭 차트', en:'Triple Metric Chart', ja:'トリプルメトリクスチャート', 'zh-CN':'三重指标图表', 'zh-TW':'三重指標圖表', es:'Gráfico de triple métrica'},
          content:{ko:'<strong>NPU Throughput, E2E FPS, Latency</strong>를 하나의 차트에서 비교합니다. 바를 클릭하면 해당 플랫폼의 환경 상세 패널이 열립니다.', en:'Compare <strong>NPU Throughput, E2E FPS, Latency</strong> in a single chart. Click a bar to open the environment detail panel for that platform.', ja:'<strong>NPU Throughput、E2E FPS、Latency</strong>を1つのチャートで比較します。バーをクリックするとそのプラットフォームの環境詳細パネルが開きます。', 'zh-CN':'在一个图表中比较<strong>NPU吞吐量、E2E FPS、延迟</strong>。点击柱形可打开该平台的环境详情面板。', 'zh-TW':'在一個圖表中比較<strong>NPU吞吐量、E2E FPS、延遲</strong>。點擊長條可打開該平台的環境詳情面板。', es:'Compare <strong>NPU Throughput, E2E FPS, Latency</strong> en un solo gráfico. Haga clic en una barra para abrir el panel de detalle del entorno de esa plataforma.'} },
        { target:'#envDetail', position:'top',
          title:{ko:'환경 상세 패널', en:'Environment Detail Panel', ja:'環境詳細パネル', 'zh-CN':'环境详情面板', 'zh-TW':'環境詳情面板', es:'Panel de detalle del entorno'},
          content:{ko:'차트에서 <strong>바를 클릭</strong>하면 하단에 환경 상세 패널이 나타납니다. <strong>Host/NPU/SW 정보</strong>를 3열 레이아웃으로 확인할 수 있습니다.', en:'<strong>Click a bar</strong> in the chart to reveal the environment detail panel below. It displays <strong>Host/NPU/SW info</strong> in a 3-column layout.', ja:'チャートで<strong>バーをクリック</strong>すると下部に環境詳細パネルが表示されます。<strong>Host/NPU/SW情報</strong>を3列レイアウトで確認できます。', 'zh-CN':'在图表中<strong>点击柱形</strong>后，下方会出现环境详情面板。可以三列布局查看<strong>Host/NPU/SW信息</strong>。', 'zh-TW':'在圖表中<strong>點擊長條</strong>後，下方會出現環境詳情面板。可以三欄佈局查看<strong>Host/NPU/SW資訊</strong>。', es:'<strong>Haga clic en una barra</strong> del gráfico para mostrar el panel de detalle del entorno abajo. Muestra la <strong>información Host/NPU/SW</strong> en un diseño de 3 columnas.'},
          beforeStep:function(){ _openOverviewEnvDetail(); _scrollTo('#envDetail'); } },
        { target:'#overviewModelMetaPanel', position:'top',
          title:{ko:'벤치마크 모델 메타데이터', en:'Benchmark Model Metadata', ja:'ベンチマークモデルメタデータ', 'zh-CN':'基准测试模型元数据', 'zh-TW':'基準測試模型中繼資料', es:'Metadatos del modelo de benchmark'},
          content:{ko:'차트 바를 클릭하면 환경 상세 아래에 <strong>모델 메타데이터 패널</strong>이 함께 표시됩니다. 벤치마크에 사용된 모델의 <strong>입력 크기, NPU DRAM 사용량, 포맷</strong> 등을 확인합니다.', en:'Clicking a chart bar also reveals the <strong>model metadata panel</strong>. View metadata of benchmarked models including <strong>input size, NPU DRAM usage, format</strong>, and more.', ja:'チャートバーをクリックすると環境詳細の下に<strong>モデルメタデータパネル</strong>が表示されます。ベンチマークに使用されたモデルの<strong>入力サイズ、NPU DRAM使用量、フォーマット</strong>などを確認します。', 'zh-CN':'点击图表柱形后，环境详情下方还会显示<strong>模型元数据面板</strong>。可以查看基准测试中使用的模型的<strong>输入大小、NPU DRAM使用量、格式</strong>等信息。', 'zh-TW':'點擊圖表長條後，環境詳情下方還會顯示<strong>模型中繼資料面板</strong>。可以查看基準測試中使用的模型的<strong>輸入大小、NPU DRAM使用量、格式</strong>等資訊。', es:'Al hacer clic en una barra del gráfico también se muestra el <strong>panel de metadatos del modelo</strong>. Consulte metadatos de los modelos evaluados, incluidos <strong>tamaño de entrada, uso de DRAM NPU, formato</strong> y más.'},
          beforeStep:function(){ _openOverviewEnvDetail(); _scrollTo('#overviewModelMetaPanel'); } },
        { target:'#envNpuInfo', position:'top',
          title:{ko:'NPU 식별 정보', en:'NPU Identity', ja:'NPU識別情報', 'zh-CN':'NPU识别信息', 'zh-TW':'NPU識別資訊', es:'Identidad del NPU'},
          content:{ko:'NPU 열에는 <strong>Product, SKU, Modules, Device Count</strong>가 추가되어 어떤 NPU 제품/구성인지 명확히 식별할 수 있습니다. Host PC 열의 <strong>제품명</strong> 항목과 함께 확인하면 멀티 모듈 보드(예: <code>H1-Quattro ×1</code>)도 구분됩니다.', en:'The NPU column now includes <strong>Product, SKU, Modules, and Device Count</strong> so you can identify exactly which NPU product/configuration was tested. Combined with the <strong>Product Name</strong> entry in the Host PC column, multi-module boards (e.g. <code>H1-Quattro ×1</code>) are distinguishable too.', ja:'NPU列に<strong>Product、SKU、Modules、Device Count</strong>が追加され、テストされたNPU製品・構成を正確に識別できるようになりました。Host PC列の<strong>製品名</strong>と合わせて確認すると、マルチモジュールボード（例：<code>H1-Quattro ×1</code>）も区別できます。', 'zh-CN':'NPU列现在包含<strong>Product、SKU、Modules、Device Count</strong>，可以准确识别所测试的NPU产品/配置。结合Host PC列的<strong>产品名称</strong>项，还能区分多模块板卡（例如<code>H1-Quattro ×1</code>）。', 'zh-TW':'NPU欄現在包含<strong>Product、SKU、Modules、Device Count</strong>，可以準確識別所測試的NPU產品/組態。結合Host PC欄的<strong>產品名稱</strong>項，還能區分多模組板卡（例如<code>H1-Quattro ×1</code>）。', es:'La columna NPU ahora incluye <strong>Product, SKU, Modules y Device Count</strong>, de modo que puede identificar con exactitud qué producto/configuración de NPU se probó. Junto con el campo <strong>Nombre del producto</strong> de la columna Host PC, también se distinguen las placas multimódulo (p. ej. <code>H1-Quattro ×1</code>).'},
          beforeStep:function(){ _openOverviewEnvDetail(); _scrollTo('#envNpuInfo'); } },
        { target:'.trend-link', position:'bottom',
          title:{ko:'트렌드 링크', en:'Trend Link', ja:'トレンドリンク', 'zh-CN':'趋势链接', 'zh-TW':'趨勢連結', es:'Enlace de tendencia'},
          content:{ko:'환경 상세 패널이 열린 상태에서 <strong>트렌드 링크</strong>를 찾아 클릭하면 <strong>Version Trend</strong> 서브탭으로 이동하여 SW 버전별 성능 추이를 확인할 수 있습니다.', en:'When the environment detail panel is open, find and click the <strong>Trend Link</strong> to navigate to the <strong>Version Trend</strong> sub-tab for performance trends across SW versions.', ja:'環境詳細パネルが開いている状態で<strong>トレンドリンク</strong>を見つけてクリックすると、<strong>Version Trend</strong>サブタブに移動してSWバージョン別のパフォーマンス推移を確認できます。', 'zh-CN':'在环境详情面板打开的状态下，找到并点击<strong>趋势链接</strong>即可跳转到<strong>Version Trend</strong>子选项卡，查看各SW版本的性能趋势。', 'zh-TW':'在環境詳情面板開啟的狀態下，找到並點擊<strong>趨勢連結</strong>即可跳轉到<strong>Version Trend</strong>子分頁，查看各SW版本的效能趨勢。', es:'Con el panel de detalle del entorno abierto, localice y haga clic en el <strong>enlace de tendencia</strong> para ir a la subpestaña <strong>Version Trend</strong> y ver la evolución del rendimiento por versión de SW.'},
          beforeStep:function(){ _openOverviewEnvDetail(); _scrollTo('.trend-link'); } },
      ]
    },

    { id:'dashboard-detail', icon:'📋',
      title:{ko:'📋 Detailed Data', en:'📋 Detailed Data', ja:'📋 Detailed Data', 'zh-CN':'📋 Detailed Data', 'zh-TW':'📋 Detailed Data', es:'📋 Detailed Data'},
      description:{ko:'원시 수치 테이블로 상세 데이터 탐색', en:'Explore detailed data with raw numeric tables', ja:'生データテーブルで詳細データを探索', 'zh-CN':'通过原始数据表格探索详细数据', 'zh-TW':'透過原始資料表格探索詳細資料', es:'Explore datos detallados con tablas numéricas en bruto'},
      beforeStart: function () {
        return new Promise(function (resolve) {
          switchTab('dashboard');
          setTimeout(function () {
            var tab = document.querySelector('.dashboard-tab[data-tab="detail"]');
            if (tab) tab.click();
            resolve();
          }, 400);
        });
      },
      steps:[
        { target:'.dashboard-tab[data-tab="detail"]', position:'bottom',
          title:{ko:'Detailed Data 서브탭', en:'Detailed Data Sub-tab', ja:'Detailed Dataサブタブ', 'zh-CN':'Detailed Data子选项卡', 'zh-TW':'Detailed Data子分頁', es:'Subpestaña Detailed Data'},
          content:{ko:'벤치마크 결과를 <strong>원시 수치 테이블</strong>로 확인합니다. 열 정렬, Best 하이라이트 등 데이터 분석 기능을 제공합니다.', en:'View benchmark results as <strong>raw numeric tables</strong>. Provides data analysis features like column sorting and Best highlights.', ja:'ベンチマーク結果を<strong>生データテーブル</strong>で確認します。列ソート、Bestハイライトなどのデータ分析機能を提供します。', 'zh-CN':'以<strong>原始数据表格</strong>查看基准测试结果。提供列排序、最佳值高亮等数据分析功能。', 'zh-TW':'以<strong>原始資料表格</strong>查看基準測試結果。提供欄位排序、最佳值醒目提示等資料分析功能。', es:'Consulte los resultados del benchmark como <strong>tablas numéricas en bruto</strong>. Ofrece funciones de análisis como ordenación por columnas y resaltado de mejores valores.'} },
        { target:'#detailEnvFilter', position:'right',
          title:{ko:'환경 필터', en:'Environment Filter', ja:'環境フィルター', 'zh-CN':'环境筛选', 'zh-TW':'環境篩選', es:'Filtro de entorno'},
          content:{ko:'<strong>환경(플랫폼)</strong>별로 데이터를 필터링합니다. 특정 하드웨어의 결과만 확인하고 싶을 때 사용합니다.', en:'Filter data by <strong>environment (platform)</strong>. Use when you want to see results for specific hardware.', ja:'<strong>環境（プラットフォーム）</strong>別にデータをフィルタリングします。特定のハードウェアの結果のみ確認したい場合に使用します。', 'zh-CN':'按<strong>环境（平台）</strong>筛选数据。当需要只查看特定硬件的结果时使用。', 'zh-TW':'按<strong>環境（平台）</strong>篩選資料。當需要只查看特定硬體的結果時使用。', es:'Filtre los datos por <strong>entorno (plataforma)</strong>. Úselo cuando desee ver resultados de hardware específico.'} },
        { target:'#detailRunFilter', position:'right',
          title:{ko:'Run 필터', en:'Run Filter', ja:'Runフィルター', 'zh-CN':'Run筛选', 'zh-TW':'Run篩選', es:'Filtro de Run'},
          content:{ko:'특정 <strong>벤치마크 실행(run)</strong>의 결과만 필터링합니다. 여러 실행 간 비교 분석에 유용합니다.', en:'Filter results for a specific <strong>benchmark run</strong>. Useful for comparison analysis across multiple runs.', ja:'特定の<strong>ベンチマーク実行（run）</strong>の結果のみフィルタリングします。複数実行間の比較分析に有用です。', 'zh-CN':'只筛选特定<strong>基准测试运行（run）</strong>的结果。对多次运行之间的比较分析很有用。', 'zh-TW':'只篩選特定<strong>基準測試運行（run）</strong>的結果。對多次運行之間的比較分析很有用。', es:'Filtre los resultados de una <strong>ejecución de benchmark (run)</strong> concreta. Útil para comparar varias ejecuciones.'} },
        { target:'#detailTaskFilter', position:'right',
          title:{ko:'Task 필터', en:'Task Filter', ja:'Taskフィルター', 'zh-CN':'Task筛选', 'zh-TW':'Task篩選', es:'Filtro de Task'},
          content:{ko:'<strong>AI 태스크</strong>(Detection, Pose, Segmentation 등)별로 테이블 데이터를 필터링합니다.', en:'Filter table data by <strong>AI task</strong> (Detection, Pose, Segmentation, etc.).', ja:'<strong>AIタスク</strong>（Detection、Pose、Segmentationなど）別にテーブルデータをフィルタリングします。', 'zh-CN':'按<strong>AI任务</strong>（Detection、Pose、Segmentation等）筛选表格数据。', 'zh-TW':'按<strong>AI任務</strong>（Detection、Pose、Segmentation等）篩選表格資料。', es:'Filtre los datos de la tabla por <strong>tarea de IA</strong> (Detection, Pose, Segmentation, etc.).'} },
        { target:'#detailOrtFilter', position:'right',
          title:{ko:'ORT 필터', en:'ORT Filter', ja:'ORTフィルター', 'zh-CN':'ORT筛选', 'zh-TW':'ORT篩選', es:'Filtro ORT'},
          content:{ko:'<strong>ONNX Runtime(ORT)</strong> On/Off 조건으로 테이블을 필터링합니다.', en:'Filter tables by <strong>ONNX Runtime (ORT)</strong> On/Off condition.', ja:'<strong>ONNX Runtime（ORT）</strong> On/Off条件でテーブルをフィルタリングします。', 'zh-CN':'按<strong>ONNX Runtime（ORT）</strong>开/关条件筛选表格。', 'zh-TW':'按<strong>ONNX Runtime（ORT）</strong>開/關條件篩選表格。', es:'Filtre las tablas por condición <strong>ONNX Runtime (ORT)</strong> activado/desactivado.'} },
        { target:'#detailTables', position:'top',
          title:{ko:'태스크별 테이블', en:'Per-Task Tables', ja:'タスク別テーブル', 'zh-CN':'按任务分类的表格', 'zh-TW':'按任務分類的表格', es:'Tablas por tarea'},
          content:{ko:'각 AI 태스크별로 분리된 테이블에서 <strong>NPU Throughput, E2E FPS, Latency</strong> 수치를 확인합니다. 열 헤더를 클릭하여 정렬할 수 있습니다.', en:'Check <strong>NPU Throughput, E2E FPS, Latency</strong> values in separate tables per AI task. Click column headers to sort.', ja:'各AIタスク別に分離されたテーブルで<strong>NPU Throughput、E2E FPS、Latency</strong>の数値を確認します。列ヘッダーをクリックしてソートできます。', 'zh-CN':'在按各AI任务分开的表格中查看<strong>NPU吞吐量、E2E FPS、延迟</strong>数值。点击列标题可进行排序。', 'zh-TW':'在按各AI任務分開的表格中查看<strong>NPU吞吐量、E2E FPS、延遲</strong>數值。點擊欄位標題可進行排序。', es:'Consulte los valores de <strong>NPU Throughput, E2E FPS, Latency</strong> en tablas separadas por tarea de IA. Haga clic en los encabezados de columna para ordenar.'} },
        { target:null, position:'left',
          title:{ko:'Best 값 강조', en:'Best Value Highlight', ja:'Best値ハイライト', 'zh-CN':'最佳值高亮', 'zh-TW':'最佳值醒目提示', es:'Resaltado del mejor valor'},
          content:{ko:'데이터가 로드되면 각 메트릭에서 <strong>가장 좋은 값</strong>이 자동으로 강조 표시됩니다. 테이블에서 <strong class="cell-best">초록색 강조</strong>된 셀을 확인하세요.', en:'When data is loaded, the <strong>best value</strong> for each metric is automatically highlighted. Look for <strong class="cell-best">green highlighted</strong> cells in the table.', ja:'データがロードされると各メトリクスで<strong>最も良い値</strong>が自動的にハイライト表示されます。テーブルの<strong class="cell-best">緑色でハイライト</strong>されたセルを確認してください。', 'zh-CN':'数据加载后，各指标中的<strong>最佳值</strong>会自动高亮显示。请查看表格中<strong class="cell-best">绿色高亮</strong>的单元格。', 'zh-TW':'資料載入後，各指標中的<strong>最佳值</strong>會自動醒目提示顯示。請查看表格中<strong class="cell-best">綠色醒目提示</strong>的儲存格。', es:'Al cargar los datos, el <strong>mejor valor</strong> de cada métrica se resalta automáticamente. Busque celdas <strong class="cell-best">resaltadas en verde</strong> en la tabla.'} },
        { target:'#detailTables', position:'top',
          title:{ko:'온도·상태 열', en:'Thermal & Status Columns', ja:'温度・ステータス列', 'zh-CN':'温度与状态列', 'zh-TW':'溫度與狀態欄', es:'Columnas de temperatura y estado'},
          content:{ko:'각 테이블에는 <strong>NPU 온도 (°C)</strong>와 <strong>NPU 클럭 (MHz)</strong> 열이 포함되어 있습니다. 온도가 낮아지며 클럭이 떨어지면 호박색 <strong class="tag tag--warn">스로틀링됨</strong> 배지가 표시됩니다. 실행 조건에 이상이 있으면(재개/재시도) <strong>상태</strong> 열에 <strong class="tag tag--warn">Partial</strong>/<strong class="tag tag--err">Timeout</strong>/<strong class="tag tag--err">Error</strong> 배지가 나타나며, 마우스를 올리면 상세 사유를 확인할 수 있습니다.', en:'Each table includes <strong>NPU Temp (°C)</strong> and <strong>NPU Clock (MHz)</strong> columns. When thermal throttling drops the clock, an amber <strong class="tag tag--warn">Throttled</strong> badge appears. If a run condition needed a resume/retry, the <strong>Status</strong> column shows a <strong class="tag tag--warn">Partial</strong>/<strong class="tag tag--err">Timeout</strong>/<strong class="tag tag--err">Error</strong> badge — hover it for details.', ja:'各テーブルには<strong>NPU温度 (°C)</strong>と<strong>NPUクロック (MHz)</strong>の列が含まれます。サーマルスロットリングでクロックが低下すると、琥珀色の<strong class="tag tag--warn">スロットリング中</strong>バッジが表示されます。実行条件でresume/retryが発生した場合、<strong>ステータス</strong>列に<strong class="tag tag--warn">Partial</strong>/<strong class="tag tag--err">Timeout</strong>/<strong class="tag tag--err">Error</strong>バッジが表示され、ホバーすると詳細な理由を確認できます。', 'zh-CN':'每个表格都包含<strong>NPU温度 (°C)</strong>和<strong>NPU时钟频率 (MHz)</strong>列。当温度限频导致时钟下降时，会显示琥珀色的<strong class="tag tag--warn">限频</strong>标记。如果运行条件发生了续跑/重试，<strong>状态</strong>列会显示<strong class="tag tag--warn">Partial</strong>/<strong class="tag tag--err">Timeout</strong>/<strong class="tag tag--err">Error</strong>标记，悬停可查看详细原因。', 'zh-TW':'每個表格都包含<strong>NPU溫度 (°C)</strong>和<strong>NPU時脈 (MHz)</strong>欄。當溫度降頻導致時脈下降時，會顯示琥珀色的<strong class="tag tag--warn">降頻</strong>標記。如果執行條件發生了續跑/重試，<strong>狀態</strong>欄會顯示<strong class="tag tag--warn">Partial</strong>/<strong class="tag tag--err">Timeout</strong>/<strong class="tag tag--err">Error</strong>標記，將滑鼠停留在上方可查看詳細原因。', es:'Cada tabla incluye las columnas <strong>Temp. NPU (°C)</strong> y <strong>Reloj NPU (MHz)</strong>. Cuando la limitación térmica reduce el reloj, aparece una insignia ámbar de <strong class="tag tag--warn">Limitado</strong>. Si una condición de ejecución necesitó reanudarse o reintentarse, la columna <strong>Estado</strong> muestra una insignia <strong class="tag tag--warn">Partial</strong>/<strong class="tag tag--err">Timeout</strong>/<strong class="tag tag--err">Error</strong>; pase el cursor sobre ella para ver el detalle.'} },
      ]
    },

    { id:'dashboard-trend', icon:'📉',
      title:{ko:'📉 Version Trend', en:'📉 Version Trend', ja:'📉 Version Trend', 'zh-CN':'📉 Version Trend', 'zh-TW':'📉 Version Trend', es:'📉 Version Trend'},
      description:{ko:'SW 버전별 성능 추이를 시계열로 추적', en:'Track performance trends across SW versions over time', ja:'SWバージョン別のパフォーマンス推移を時系列で追跡', 'zh-CN':'按SW版本追踪性能趋势的时间序列', 'zh-TW':'按SW版本追蹤效能趨勢的時間序列', es:'Siga la evolución del rendimiento por versiones de SW a lo largo del tiempo'},
      beforeStart: function () {
        return new Promise(function (resolve) {
          switchTab('dashboard');
          setTimeout(function () {
            var tab = document.querySelector('.dashboard-tab[data-tab="version-trend"]');
            if (tab) tab.click();
            resolve();
          }, 400);
        });
      },
      steps:[
        { target:'.dashboard-tab[data-tab="version-trend"]', position:'bottom',
          title:{ko:'Version Trend 서브탭', en:'Version Trend Sub-tab', ja:'Version Trendサブタブ', 'zh-CN':'Version Trend子选项卡', 'zh-TW':'Version Trend子分頁', es:'Subpestaña Version Trend'},
          content:{ko:'SW 버전 업데이트에 따른 <strong>성능 변화</strong>를 시계열 라인 차트로 추적합니다. 리그레션 탐지에 유용합니다.', en:'Track <strong>performance changes</strong> across SW version updates with time-series line charts. Useful for regression detection.', ja:'SWバージョン更新に伴う<strong>パフォーマンス変化</strong>を時系列ラインチャートで追跡します。リグレッション検出に有用です。', 'zh-CN':'通过时间序列折线图追踪SW版本更新引起的<strong>性能变化</strong>。对回归检测很有用。', 'zh-TW':'透過時間序列折線圖追蹤SW版本更新引起的<strong>效能變化</strong>。對迴歸偵測很有用。', es:'Siga los <strong>cambios de rendimiento</strong> tras actualizaciones de SW con gráficos de líneas temporales. Útil para detectar regresiones.'} },
        { target:'#trendEnvFilter', position:'right',
          title:{ko:'환경 필터', en:'Environment Filter', ja:'環境フィルター', 'zh-CN':'环境筛选', 'zh-TW':'環境篩選', es:'Filtro de entorno'},
          content:{ko:'트렌드를 분석할 <strong>환경(플랫폼)</strong>을 선택합니다. 선택한 환경의 버전별 성능 추이를 확인할 수 있습니다.', en:'Select the <strong>environment (platform)</strong> for trend analysis. View performance trends across versions for the selected environment.', ja:'トレンドを分析する<strong>環境（プラットフォーム）</strong>を選択します。選択した環境のバージョン別パフォーマンス推移を確認できます。', 'zh-CN':'选择要分析趋势的<strong>环境（平台）</strong>。可以查看所选环境各版本的性能趋势。', 'zh-TW':'選擇要分析趨勢的<strong>環境（平台）</strong>。可以查看所選環境各版本的效能趨勢。', es:'Seleccione el <strong>entorno (plataforma)</strong> para el análisis de tendencias. Consulte la evolución del rendimiento por versiones del entorno elegido.'} },
        { target:'#trendTaskFilter', position:'right',
          title:{ko:'Task 필터', en:'Task Filter', ja:'Taskフィルター', 'zh-CN':'Task筛选', 'zh-TW':'Task篩選', es:'Filtro de Task'},
          content:{ko:'트렌드를 분석할 <strong>AI 태스크</strong>를 선택합니다. 태스크별로 버전 간 성능 변화를 추적할 수 있습니다.', en:'Select the <strong>AI task</strong> for trend analysis. Track performance changes across versions per task.', ja:'トレンドを分析する<strong>AIタスク</strong>を選択します。タスク別にバージョン間のパフォーマンス変化を追跡できます。', 'zh-CN':'选择要分析趋势的<strong>AI任务</strong>。可以按任务追踪各版本之间的性能变化。', 'zh-TW':'選擇要分析趨勢的<strong>AI任務</strong>。可以按任務追蹤各版本之間的效能變化。', es:'Seleccione la <strong>tarea de IA</strong> para el análisis de tendencias. Siga los cambios de rendimiento por versión y por tarea.'} },
        { target:'#trendOrtFilter', position:'right',
          title:{ko:'ORT 필터', en:'ORT Filter', ja:'ORTフィルター', 'zh-CN':'ORT筛选', 'zh-TW':'ORT篩選', es:'Filtro ORT'},
          content:{ko:'<strong>ONNX Runtime(ORT)</strong> On/Off 조건으로 트렌드를 필터링합니다.', en:'Filter trends by <strong>ONNX Runtime (ORT)</strong> On/Off condition.', ja:'<strong>ONNX Runtime（ORT）</strong> On/Off条件でトレンドをフィルタリングします。', 'zh-CN':'按<strong>ONNX Runtime（ORT）</strong>开/关条件筛选趋势。', 'zh-TW':'按<strong>ONNX Runtime（ORT）</strong>開/關條件篩選趨勢。', es:'Filtre las tendencias por condición <strong>ONNX Runtime (ORT)</strong> activado/desactivado.'} },
        { target:'.trend-version-filter-panel', position:'right',
          title:{ko:'dx-all-suite 버전 필터', en:'dx-all-suite Version Filter', ja:'dx-all-suite バージョンフィルター', 'zh-CN':'dx-all-suite 版本筛选', 'zh-TW':'dx-all-suite 版本篩選', es:'Filtro de versión de dx-all-suite'},
          content:{ko:'이제 <strong>메트릭 드롭다운</strong> 대신 각 지표별로 분리된 차트가 표시되며, 표시할 <strong>dx-all-suite 버전</strong>을 선택/해제할 수 있는 필터를 제공합니다. <strong>All</strong>/<strong>None</strong> 버튼으로 모든 버전을 한 번에 선택하거나 해제하세요.', en:'Instead of a metric dropdown, this tab now shows a separate chart per metric and lets you filter which <strong>dx-all-suite versions</strong> are displayed. Use the <strong>All</strong>/<strong>None</strong> buttons to toggle all versions at once.', ja:'メトリックドロップダウンの代わりに、指標ごとに分離されたチャートが表示され、表示する<strong>dx-all-suiteバージョン</strong>を選択できるフィルターが提供されます。<strong>All</strong>/<strong>None</strong>ボタンで一括切り替えができます。', 'zh-CN':'不再使用指标下拉菜单，此标签页现在为每个指标显示单独的图表，并提供筛选<strong>dx-all-suite版本</strong>的功能。使用<strong>All</strong>/<strong>None</strong>按钮可一次性切换所有版本的显示。', 'zh-TW':'不再使用指標下拉選單，此分頁現在為每個指標顯示獨立的圖表，並提供篩選<strong>dx-all-suite版本</strong>的功能。使用<strong>All</strong>/<strong>None</strong>按鈕可一次切換所有版本的顯示。', es:'En lugar de un menú desplegable de métricas, esta pestaña ahora muestra un gráfico independiente por métrica y permite filtrar qué <strong>versiones de dx-all-suite</strong> se muestran. Use los botones <strong>All</strong>/<strong>None</strong> para alternar todas las versiones a la vez.'} },
        { target:'.trend-charts-grid', position:'top',
          title:{ko:'지표별 차트 그리드', en:'Per-Metric Chart Grid', ja:'指標別チャートグリッド', 'zh-CN':'按指标分类的图表网格', 'zh-TW':'按指標分類的圖表網格', es:'Cuadrícula de gráficos por métrica'},
          content:{ko:'<strong>NPU Throughput, E2E FPS, Latency, Capacity</strong> 등 각 메트릭이 별도의 작은 차트(스몰 멀티플)로 표시되며, 모델 크기별 <strong>5개 라인(N/S/M/L/X)</strong>으로 버전 간 성능 추이를 보여줍니다. 포인트를 클릭하면 해당 스냅샷의 상세 정보를 확인할 수 있습니다.', en:'Each metric (<strong>NPU Throughput, E2E FPS, Latency, Capacity</strong>) is shown as its own small chart (small multiples), with <strong>5 lines (N/S/M/L/X)</strong> by model size tracking performance across versions. Click a point to see that snapshot\'s details.', ja:'<strong>NPU Throughput、E2E FPS、Latency、Capacity</strong>などの各メトリクスが個別の小さなチャート（スモールマルチプル）で表示され、モデルサイズ別の<strong>5本のライン（N/S/M/L/X）</strong>でバージョン間のパフォーマンス推移を示します。ポイントをクリックするとそのスナップショットの詳細情報を確認できます。', 'zh-CN':'<strong>NPU吞吐量、E2E FPS、延迟、Capacity</strong>等各项指标以独立的小图表（小倍数图）形式显示，并以按模型大小分类的<strong>5条折线（N/S/M/L/X）</strong>展示各版本间的性能趋势。点击数据点可查看该快照的详细信息。', 'zh-TW':'<strong>NPU吞吐量、E2E FPS、延遲、Capacity</strong>等各項指標以獨立的小圖表（小倍數圖）形式顯示，並以按模型大小分類的<strong>5條折線（N/S/M/L/X）</strong>展示各版本間的效能趨勢。點擊資料點可查看該快照的詳細資訊。', es:'Cada métrica (<strong>NPU Throughput, E2E FPS, Latency, Capacity</strong>) se muestra en su propio gráfico pequeño (small multiples), con <strong>5 líneas (N/S/M/L/X)</strong> por tamaño de modelo que siguen el rendimiento entre versiones. Haga clic en un punto para ver los detalles de esa instantánea.'} },
        { target:'#trendEnvDetail', position:'top',
          title:{ko:'스냅샷 상세', en:'Snapshot Detail', ja:'スナップショット詳細', 'zh-CN':'快照详情', 'zh-TW':'快照詳情', es:'Detalle de instantánea'},
          content:{ko:'트렌드 차트에서 <strong>포인트를 클릭</strong>하면 하단에 해당 시점의 <strong>환경 상세 정보</strong> 패널이 나타납니다. 포인트를 클릭하여 확인해 보세요.', en:'<strong>Click a point</strong> in the trend chart to reveal the <strong>environment details</strong> panel below for that snapshot.', ja:'トレンドチャートで<strong>ポイントをクリック</strong>すると下部にその時点の<strong>環境詳細情報</strong>パネルが表示されます。', 'zh-CN':'在趋势图表中<strong>点击数据点</strong>后，下方会出现该时间点的<strong>环境详细信息</strong>面板。', 'zh-TW':'在趨勢圖表中<strong>點擊資料點</strong>後，下方會出現該時間點的<strong>環境詳細資訊</strong>面板。', es:'<strong>Haga clic en un punto</strong> del gráfico de tendencia para mostrar abajo el panel de <strong>detalles del entorno</strong> de esa instantánea.'},
          beforeStep:_mockTrendSnapshot, afterStep:_clearTrendSnapshot },
        { target:'#trendModelMetaPanel', position:'top',
          title:{ko:'스냅샷 모델 정보', en:'Snapshot Model Info', ja:'スナップショットモデル情報', 'zh-CN':'快照模型信息', 'zh-TW':'快照模型資訊', es:'Información del modelo en la instantánea'},
          content:{ko:'트렌드 차트 포인트를 클릭하면 환경 상세와 함께 <strong>모델 메타데이터</strong> 패널도 나타납니다. 해당 시점의 <strong>입력 해상도, NPU 메모리, 포맷</strong>을 확인할 수 있습니다.', en:'Clicking a trend chart point also reveals the <strong>model metadata</strong> panel. Check <strong>input resolution, NPU memory, format</strong> at that snapshot point.', ja:'トレンドチャートのポイントをクリックすると環境詳細とともに<strong>モデルメタデータ</strong>パネルも表示されます。その時点の<strong>入力解像度、NPUメモリ、フォーマット</strong>を確認できます。', 'zh-CN':'点击趋势图表数据点后，还会同时显示<strong>模型元数据</strong>面板。可以查看该时间点的<strong>输入分辨率、NPU内存、格式</strong>。', 'zh-TW':'點擊趨勢圖表資料點後，還會同時顯示<strong>模型中繼資料</strong>面板。可以查看該時間點的<strong>輸入解析度、NPU記憶體、格式</strong>。', es:'Al hacer clic en un punto del gráfico de tendencia también se muestra el panel de <strong>metadatos del modelo</strong>. Consulte la <strong>resolución de entrada, memoria NPU y formato</strong> en ese instante.'},
          beforeStep:_mockTrendSnapshot, afterStep:_clearTrendSnapshot },
      ]
    },

    { id:'dashboard-ort', icon:'🔀',
      title:{ko:'🔀 ORT ON/OFF', en:'🔀 ORT ON/OFF', ja:'🔀 ORT ON/OFF', 'zh-CN':'🔀 ORT ON/OFF', 'zh-TW':'🔀 ORT ON/OFF', es:'🔀 ORT ON/OFF'},
      description:{ko:'동일 모델·환경에서 ONNX Runtime On/Off 성능 차이 비교', en:'Compare ONNX Runtime On/Off performance for the same model and environment', ja:'同一モデル・環境でONNX Runtime On/Offのパフォーマンス差を比較', 'zh-CN':'比较相同模型和环境下ONNX Runtime开/关的性能差异', 'zh-TW':'比較相同模型與環境下ONNX Runtime開/關的效能差異', es:'Compare el rendimiento de ONNX Runtime activado/desactivado para el mismo modelo y entorno'},
      beforeStart: function () {
        return new Promise(function (resolve) {
          switchTab('dashboard');
          setTimeout(function () {
            var tab = document.querySelector('.dashboard-tab[data-tab="ort-compare"]');
            if (tab) tab.click();
            resolve();
          }, 400);
        });
      },
      steps:[
        { target:'.dashboard-tab[data-tab="ort-compare"]', position:'bottom',
          title:{ko:'ORT ON/OFF 서브탭', en:'ORT ON/OFF Sub-tab', ja:'ORT ON/OFFサブタブ', 'zh-CN':'ORT ON/OFF子选项卡', 'zh-TW':'ORT ON/OFF子分頁', es:'Subpestaña ORT ON/OFF'},
          content:{ko:'<strong>ONNX Runtime(ORT)</strong>를 켰을 때와 껐을 때의 성능을 나란히 비교하는 서브탭입니다. 동일한 모델·환경 조건에서 ORT가 CPU/NPU 부하 분배에 미치는 영향을 확인할 수 있습니다.', en:'A sub-tab that compares performance with <strong>ONNX Runtime (ORT)</strong> turned on versus off, side by side. See how ORT affects the CPU/NPU workload balance for the same model and environment.', ja:'<strong>ONNX Runtime（ORT）</strong>をオンにした場合とオフにした場合のパフォーマンスを並べて比較するサブタブです。同一のモデル・環境条件でORTがCPU/NPUの負荷分散に与える影響を確認できます。', 'zh-CN':'并排比较开启和关闭<strong>ONNX Runtime（ORT）</strong>时性能的子选项卡。可以在相同模型和环境条件下查看ORT对CPU/NPU负载分配的影响。', 'zh-TW':'並排比較開啟和關閉<strong>ONNX Runtime（ORT）</strong>時效能的子分頁。可以在相同模型與環境條件下查看ORT對CPU/NPU負載分配的影響。', es:'Una subpestaña que compara el rendimiento con <strong>ONNX Runtime (ORT)</strong> activado frente a desactivado, uno junto a otro. Vea cómo afecta ORT al equilibrio de carga CPU/NPU para el mismo modelo y entorno.'} },
        { target:'#ortEnvFilter', position:'right',
          title:{ko:'환경 필터', en:'Environment Filter', ja:'環境フィルター', 'zh-CN':'环境筛选', 'zh-TW':'環境篩選', es:'Filtro de entorno'},
          content:{ko:'비교할 <strong>환경(플랫폼)</strong>을 선택합니다. 선택한 환경에서 실행된 ORT ON/OFF 결과만 차트와 테이블에 표시됩니다.', en:'Select the <strong>environment (platform)</strong> to compare. Only ORT ON/OFF results from the selected environment are shown in the chart and table.', ja:'比較する<strong>環境（プラットフォーム）</strong>を選択します。選択した環境で実行されたORT ON/OFF結果のみがチャートとテーブルに表示されます。', 'zh-CN':'选择要比较的<strong>环境（平台）</strong>。图表和表格中只会显示所选环境下运行的ORT开/关结果。', 'zh-TW':'選擇要比較的<strong>環境（平台）</strong>。圖表和表格中只會顯示所選環境下執行的ORT開/關結果。', es:'Seleccione el <strong>entorno (plataforma)</strong> a comparar. El gráfico y la tabla solo muestran los resultados ORT ON/OFF del entorno seleccionado.'} },
        { target:'#ortTaskFilter', position:'right',
          title:{ko:'Task 필터', en:'Task Filter', ja:'Taskフィルター', 'zh-CN':'Task筛选', 'zh-TW':'Task篩選', es:'Filtro de Task'},
          content:{ko:'비교할 <strong>AI 태스크</strong>를 선택합니다. 태스크를 바꾸면 차트와 상세 테이블이 즉시 갱신됩니다.', en:'Select the <strong>AI task</strong> to compare. The chart and detail table update immediately when you change the task.', ja:'比較する<strong>AIタスク</strong>を選択します。タスクを変更するとチャートと詳細テーブルが即座に更新されます。', 'zh-CN':'选择要比较的<strong>AI任务</strong>。更改任务后图表和详情表格会立即更新。', 'zh-TW':'選擇要比較的<strong>AI任務</strong>。更改任務後圖表和詳情表格會立即更新。', es:'Seleccione la <strong>tarea de IA</strong> a comparar. El gráfico y la tabla de detalle se actualizan al instante al cambiar la tarea.'} },
        { target:'#ortMetricFilter', position:'right',
          title:{ko:'메트릭 필터', en:'Metric Filter', ja:'メトリックフィルター', 'zh-CN':'指标筛选', 'zh-TW':'指標篩選', es:'Filtro de métrica'},
          content:{ko:'비교할 <strong>성능 메트릭</strong>을 선택합니다. <strong>Throughput(FPS), E2E FPS, Latency, Max Channels</strong> 중에서 고를 수 있습니다.', en:'Select the <strong>performance metric</strong> to compare. Choose from <strong>Throughput (FPS), E2E FPS, Latency, Max Channels</strong>.', ja:'比較する<strong>パフォーマンスメトリック</strong>を選択します。<strong>Throughput（FPS）、E2E FPS、Latency、Max Channels</strong>から選択できます。', 'zh-CN':'选择要比较的<strong>性能指标</strong>。可从<strong>吞吐量(FPS)、E2E FPS、延迟、Max Channels</strong>中选择。', 'zh-TW':'選擇要比較的<strong>效能指標</strong>。可從<strong>吞吐量(FPS)、E2E FPS、延遲、Max Channels</strong>中選擇。', es:'Seleccione la <strong>métrica de rendimiento</strong> a comparar. Elija entre <strong>Rendimiento (FPS), E2E FPS, Latency, Max Channels</strong>.'} },
        { target:'#ortCompareChart', position:'top',
          title:{ko:'ORT 비교 차트', en:'ORT Comparison Chart', ja:'ORT比較チャート', 'zh-CN':'ORT比较图表', 'zh-TW':'ORT比較圖表', es:'Gráfico de comparación ORT'},
          content:{ko:'모델 크기별로 <strong>ORT ON</strong>과 <strong>ORT OFF</strong> 막대가 나란히 표시되는 그룹 바 차트입니다. 막대 위의 <strong>퍼센트 차이(Δ%)</strong> 라벨로 ORT 적용 효과를 바로 확인할 수 있습니다.', en:'A grouped bar chart showing <strong>ORT ON</strong> and <strong>ORT OFF</strong> bars side by side per model size. The <strong>percent delta (Δ%)</strong> label above each pair shows the effect of ORT at a glance.', ja:'モデルサイズごとに<strong>ORT ON</strong>と<strong>ORT OFF</strong>のバーが並んで表示されるグループバーチャートです。バー上の<strong>パーセント差分（Δ%）</strong>ラベルでORT適用の効果を一目で確認できます。', 'zh-CN':'按模型大小并排显示<strong>ORT ON</strong>和<strong>ORT OFF</strong>柱形的分组柱状图。柱形上方的<strong>百分比差异（Δ%）</strong>标签可让您一目了然地看到ORT的效果。', 'zh-TW':'按模型大小並排顯示<strong>ORT ON</strong>和<strong>ORT OFF</strong>長條的分組長條圖。長條上方的<strong>百分比差異（Δ%）</strong>標籤可讓您一眼看出ORT的效果。', es:'Un gráfico de barras agrupadas que muestra las barras de <strong>ORT ON</strong> y <strong>ORT OFF</strong> una junto a otra por tamaño de modelo. La etiqueta de <strong>diferencia porcentual (Δ%)</strong> sobre cada par muestra el efecto de ORT de un vistazo.'} },
        { target:'#ortCompareTableContent', position:'top',
          title:{ko:'ORT 비교 상세 테이블', en:'ORT Comparison Detail Table', ja:'ORT比較詳細テーブル', 'zh-CN':'ORT比较详情表格', 'zh-TW':'ORT比較詳情表格', es:'Tabla de detalle de comparación ORT'},
          content:{ko:'모델 크기별 <strong>ORT ON, ORT OFF, 차이(Delta), 차이 %</strong> 값을 정리한 표입니다. 초록/빨강 색으로 ORT ON이 더 나은지 OFF가 더 나은지 바로 알 수 있습니다.', en:'A table listing <strong>ORT ON, ORT OFF, Delta, and Delta %</strong> values per model size. Green/red coloring shows at a glance whether ORT ON or OFF performs better.', ja:'モデルサイズごとの<strong>ORT ON、ORT OFF、差分（Delta）、差分%</strong>値をまとめた表です。緑/赤の色分けでORT ONとOFFのどちらが優れているか一目でわかります。', 'zh-CN':'按模型大小列出<strong>ORT ON、ORT OFF、差值（Delta）、差值%</strong>数值的表格。绿色/红色配色可一目了然地看出ORT ON和OFF哪个表现更好。', 'zh-TW':'按模型大小列出<strong>ORT ON、ORT OFF、差值（Delta）、差值%</strong>數值的表格。綠色/紅色配色可一眼看出ORT ON和OFF哪個表現更好。', es:'Una tabla que enumera los valores de <strong>ORT ON, ORT OFF, Delta y Delta %</strong> por tamaño de modelo. El color verde/rojo muestra de un vistazo si ORT ON u OFF rinde mejor.'} },
      ]
    },

    { id:'results', icon:'📁',
      title:{ko:'📁 Results Browser', en:'📁 Results Browser', ja:'📁 結果ブラウザ', 'zh-CN':'📁 结果浏览器', 'zh-TW':'📁 結果瀏覽器', es:'📁 Explorador de resultados'},
      description:{ko:'벤치마크 결과 탐색 및 리포트 확인', en:'Browse benchmark results and check reports', ja:'ベンチマーク結果の閲覧とレポート確認', 'zh-CN':'浏览基准测试结果并查看报告', 'zh-TW':'瀏覽基準測試結果並查看報告', es:'Explore los resultados del benchmark y consulte los informes'},
      beforeStart:function(){ switchTab('results'); },
      steps:[
        { target:'.main-tab[data-tab="results"]', position:'bottom',
          title:{ko:'Results 탭', en:'Results Tab', ja:'Resultsタブ', 'zh-CN':'Results选项卡', 'zh-TW':'Results分頁', es:'Pestaña Results'},
          content:{ko:'벤치마크 실행 결과를 탐색하는 탭입니다. <strong>HW 카드 → Run 목록 → 결과 섹션</strong> 순서로 drill-down합니다.', en:'Tab for browsing benchmark results. Drill down: <strong>HW card → Run list → Result sections</strong>.', ja:'ベンチマーク実行結果を閲覧するタブです。<strong>HWカード → Run一覧 → 結果セクション</strong>の順でドリルダウンします。', 'zh-CN':'浏览基准测试执行结果的选项卡。按<strong>HW卡片 → Run列表 → 结果区域</strong>的顺序逐级展开。', 'zh-TW':'瀏覽基準測試執行結果的分頁。按<strong>HW卡片 → Run列表 → 結果區域</strong>的順序逐級展開。', es:'Pestaña para explorar resultados del benchmark. Profundice: <strong>tarjeta HW → lista de Run → secciones de resultados</strong>.'} },
        { target:'.hw-card-grid', position:'bottom',
          title:{ko:'Hardware 카드 목록', en:'Hardware Card Grid', ja:'Hardwareカード一覧', 'zh-CN':'硬件卡片列表', 'zh-TW':'硬體卡片列表', es:'Cuadrícula de tarjetas de hardware'},
          content:{ko:'테스트된 <strong>하드웨어 환경 목록</strong>입니다. 각 카드에는 플랫폼 이름과 run 수가 표시됩니다. 카드를 클릭하여 해당 환경의 run 목록을 확인하세요.', en:'List of <strong>tested hardware environments</strong>. Each card shows platform name and run count. Click a card to see its run list.', ja:'テストされた<strong>ハードウェア環境一覧</strong>です。各カードにはプラットフォーム名とrun数が表示されます。カードをクリックしてその環境のrun一覧を確認してください。', 'zh-CN':'<strong>已测试的硬件环境列表</strong>。每张卡片显示平台名称和运行次数。点击卡片查看该环境的运行列表。', 'zh-TW':'<strong>已測試的硬體環境列表</strong>。每張卡片顯示平台名稱和執行次數。點擊卡片查看該環境的執行列表。', es:'Lista de <strong>entornos de hardware probados</strong>. Cada tarjeta muestra el nombre de la plataforma y el número de runs. Haga clic en una tarjeta para ver su lista de runs.'},
          beforeStep: function () {
            var tab = document.querySelector('.main-tab[data-tab="results"]');
            if (tab) tab.click();
            return new Promise(function (resolve) {
              var attempts = 0;
              var poll = setInterval(function () {
                attempts++;
                if (document.querySelector('.hw-card-grid') || attempts > 25) {
                  clearInterval(poll);
                  resolve();
                }
              }, 200);
            });
          } },
        { target:'.hw-card', position:'bottom',
          title:{ko:'Hardware 카드 선택', en:'Select Hardware Card', ja:'Hardwareカード選択', 'zh-CN':'选择硬件卡片', 'zh-TW':'選擇硬體卡片', es:'Seleccionar tarjeta de hardware'},
          content:{ko:'개별 <strong>HW 카드</strong>를 클릭하면 해당 플랫폼의 벤치마크 실행 기록(run 목록)이 나타납니다. 🖥️ 아이콘과 플랫폼 이름, run 수를 확인하세요.', en:'Click an individual <strong>HW card</strong> to reveal the benchmark run history for that platform. Check the 🖥️ icon, platform name, and run count.', ja:'個別の<strong>HWカード</strong>をクリックするとそのプラットフォームのベンチマーク実行履歴（run一覧）が表示されます。🖥️アイコンとプラットフォーム名、run数を確認してください。', 'zh-CN':'点击单个<strong>HW卡片</strong>后会显示该平台的基准测试运行记录（run列表）。请查看🖥️图标、平台名称和运行次数。', 'zh-TW':'點擊單個<strong>HW卡片</strong>後會顯示該平台的基準測試執行記錄（run列表）。請查看🖥️圖示、平台名稱和執行次數。', es:'Haga clic en una <strong>tarjeta HW</strong> para ver el historial de ejecuciones de benchmark de esa plataforma. Consulte el icono 🖥️, el nombre de la plataforma y el número de runs.'} },
        { target:'.run-list', position:'right',
          title:{ko:'Run 목록', en:'Run List', ja:'Run一覧', 'zh-CN':'Run列表', 'zh-TW':'Run列表', es:'Lista de Run'},
          content:{ko:'선택한 HW의 <strong>벤치마크 실행 기록</strong>입니다. 📋 아이콘이 있는 run은 <strong>Markdown 리포트</strong>를 포함합니다.', en:'<strong>Benchmark run history</strong> for the selected HW. Runs with 📋 icon include <strong>Markdown reports</strong>.', ja:'選択したHWの<strong>ベンチマーク実行履歴</strong>です。📋アイコンがあるrunは<strong>Markdownレポート</strong>を含みます。', 'zh-CN':'所选HW的<strong>基准测试运行记录</strong>。带有📋图标的run包含<strong>Markdown报告</strong>。', 'zh-TW':'所選HW的<strong>基準測試執行記錄</strong>。帶有��圖示的run包含<strong>Markdown報告</strong>。', es:'<strong>Historial de ejecuciones de benchmark</strong> del HW seleccionado. Los runs con icono 📋 incluyen <strong>informes Markdown</strong>.'},
          beforeStep:function(){
            var card = document.querySelector('.hw-card');
            if (card) card.click();
          } },
        { target:'.run-item', position:'right',
          title:{ko:'Run 항목 선택', en:'Select Run Item', ja:'Run項目選択', 'zh-CN':'选择Run项目', 'zh-TW':'選擇Run項目', es:'Seleccionar elemento Run'},
          content:{ko:'개별 <strong>run 항목</strong>을 클릭하면 해당 실행의 상세 결과가 하단에 표시됩니다. <strong>📋 배지</strong>가 있으면 Markdown 리포트가 포함되어 있습니다.', en:'Click an individual <strong>run item</strong> to display detailed results below. A <strong>📋 badge</strong> indicates a Markdown report is included.', ja:'個別の<strong>run項目</strong>をクリックすると下部にその実行の詳細結果が表示されます。<strong>📋バッジ</strong>がある場合はMarkdownレポートが含まれています。', 'zh-CN':'点击单个<strong>run项目</strong>后，下方会显示该运行的详细结果。如果有<strong>📋标记</strong>则包含Markdown报告。', 'zh-TW':'點擊單個<strong>run項目</strong>後，下方會顯示該執行的詳細結果。如果有<strong>📋標記</strong>則包含Markdown報告。', es:'Haga clic en un <strong>elemento run</strong> para mostrar abajo los resultados detallados. Una <strong>insignia 📋</strong> indica que incluye un informe Markdown.'} },
        { target:'.result-section--raw', position:'top',
          title:{ko:'결과 섹션', en:'Result Section', ja:'結果セクション', 'zh-CN':'结果区域', 'zh-TW':'結果區域', es:'Sección de resultados'},
          content:{ko:'Run 항목을 클릭하면 결과 섹션이 나타납니다. <strong>Environment, Model Results, Pipeline, Multi-Stream</strong> 등의 섹션을 접이식(<code>&lt;details&gt;</code>)으로 탐색할 수 있습니다.', en:'Click a run item to reveal result sections. Explore <strong>Environment, Model Results, Pipeline, Multi-Stream</strong> in collapsible (<code>&lt;details&gt;</code>) format.', ja:'Run項目をクリックすると結果セクションが表示されます。<strong>Environment、Model Results、Pipeline、Multi-Stream</strong>などのセクションを折りたたみ式（<code>&lt;details&gt;</code>）で探索できます。', 'zh-CN':'点击Run项目后会出现结果区域。可以折叠式（<code>&lt;details&gt;</code>）浏览<strong>Environment、Model Results、Pipeline、Multi-Stream</strong>等区域。', 'zh-TW':'點擊Run項目後會出現結果區域。可以折疊式（<code>&lt;details&gt;</code>）瀏覽<strong>Environment、Model Results、Pipeline、Multi-Stream</strong>等區域。', es:'Haga clic en un elemento run para mostrar las secciones de resultados. Explore <strong>Environment, Model Results, Pipeline, Multi-Stream</strong> en formato plegable (<code>&lt;details&gt;</code>).'},
          beforeStep:_mockRunDetail, afterStep:_clearRunDetail },
        { target:'.result-section--report', position:'top',
          title:{ko:'Markdown 리포트', en:'Markdown Report', ja:'Markdownレポート', 'zh-CN':'Markdown报告', 'zh-TW':'Markdown報告', es:'Informe Markdown'},
          content:{ko:'📋 배지가 있는 run을 선택하면 <strong>Markdown 형식의 리포트</strong>가 결과 섹션에 표시됩니다. 환경 정보, 모델별 성능, 요약 등이 구조화되어 표시됩니다. <em>(리포트는 run 선택 후 API에서 동적으로 로드됩니다)</em>', en:'Select a run with 📋 badge to view a <strong>Markdown-formatted report</strong> in the result section. Environment info, per-model performance, and summaries are displayed in structured format. <em>(Reports are dynamically loaded from API after run selection)</em>', ja:'📋バッジがあるrunを選択すると<strong>Markdown形式のレポート</strong>が結果セクションに表示されます。環境情報、モデル別パフォーマンス、サマリーが構造化されて表示されます。<em>（レポートはrun選択後にAPIから動的にロードされます）</em>', 'zh-CN':'选择带有📋标记的run后，<strong>Markdown格式的报告</strong>会显示在结果区域。环境信息、各模型性能、摘要以结构化形式显示。<em>（报告在选择run后从API动态加载）</em>', 'zh-TW':'選擇帶有📋標記的run後，<strong>Markdown格式的報告</strong>會顯示在結果區域。環境資訊、各模型效能、摘要以結構化形式顯示。<em>（報告在選擇run後從API動態載入）</em>', es:'Seleccione un run con insignia 📋 para ver un <strong>informe en formato Markdown</strong> en la sección de resultados. La información del entorno, el rendimiento por modelo y los resúmenes se muestran de forma estructurada. <em>(Los informes se cargan dinámicamente desde la API tras seleccionar el run)</em>'},
          beforeStep:_mockRunDetail, afterStep:_clearRunDetail },
      ]
    },

    { id:'run-cli', icon:'▶️',
      title:{ko:'▶️ 벤치마크 실행', en:'▶️ Run Benchmarks', ja:'▶️ ベンチマーク実行', 'zh-CN':'▶️ 运行基准测试', 'zh-TW':'▶️ 執行基準測試', es:'▶️ Ejecutar benchmarks'},
      description:{ko:'웹 UI는 결과 조회 전용 — 터미널에서 벤치마크 실행', en:'Web UI is view-only — run benchmarks from the terminal', ja:'Web UIは結果閲覧専用 — ターミナルでベンチマーク実行', 'zh-CN':'Web UI 仅用于查看结果 — 请在终端运行基准测试', 'zh-TW':'Web UI 僅用於查看結果 — 請在終端機執行基準測試', es:'La UI web es solo de consulta — ejecute benchmarks en la terminal'},
      beforeStart:function(){ switchTab('dashboard'); },
      steps:[
        { target:'.main-tabs', position:'bottom',
          title:{ko:'CLI 전용 실행', en:'CLI-Only Execution', ja:'CLI専用実行', 'zh-CN':'仅 CLI 执行', 'zh-TW':'僅 CLI 執行', es:'Ejecución solo por CLI'},
          content:{ko:'이 모듈의 웹 화면은 <strong>결과 조회·비교</strong>용입니다. 새 벤치마크를 실행하려면 서버 호스트의 터미널에서 DX Benchmark CLI를 사용하세요.', en:'The web UI is for <strong>browsing and comparing results</strong> only. To run a new benchmark, use the DX Benchmark CLI on the server host terminal.', ja:'このモジュールのWeb画面は<strong>結果閲覧・比較</strong>用です。新しいベンチマークを実行するには、サーバーホストのターミナルでDX Benchmark CLIを使用してください。', 'zh-CN':'本模块 Web 界面仅用于<strong>浏览和比较结果</strong>。要运行新基准测试，请在服务器终端使用 DX Benchmark CLI。', 'zh-TW':'本模組 Web 介面僅用於<strong>瀏覽和比較結果</strong>。要執行新基準測試，請在伺服器終端機使用 DX Benchmark CLI。', es:'La UI web sirve solo para <strong>consultar y comparar resultados</strong>. Para ejecutar un nuevo benchmark, use DX Benchmark CLI en la terminal del servidor.'} },
        { target:'.main-tab[data-tab="results"]', position:'bottom',
          title:{ko:'실행 명령', en:'Run Commands', ja:'実行コマンド', 'zh-CN':'运行命令', 'zh-TW':'執行命令', es:'Comandos de ejecución'},
          content:{ko:'<p>서버 호스트 터미널에서 새 벤치마크를 실행합니다:</p>' + _RUN_CODE + '<p>완료 후 <strong>Results</strong> 탭에서 <code>results/</code> 데이터를 확인하세요. 자세한 내용은 Reference의 <strong>CLI Execution</strong> 문서를 참고하세요.</p>', en:'<p>Run a new benchmark from the server host terminal:</p>' + _RUN_CODE + '<p>When finished, open the <strong>Results</strong> tab to view <code>results/</code> data. See the <strong>CLI Execution</strong> reference doc for details.</p>', ja:'<p>サーバーホストのターミナルで新しいベンチマークを実行します：</p>' + _RUN_CODE + '<p>完了後、<strong>Results</strong> タブで <code>results/</code> データを確認してください。詳細は Reference の <strong>CLI Execution</strong> ドキュメントを参照してください。</p>', 'zh-CN':'<p>在服务器主机终端运行新的基准测试：</p>' + _RUN_CODE + '<p>完成后，在 <strong>Results</strong> 选项卡查看 <code>results/</code> 数据。详见 Reference 中的 <strong>CLI Execution</strong> 文档。</p>', 'zh-TW':'<p>在伺服器主機終端機執行新的基準測試：</p>' + _RUN_CODE + '<p>完成後，在 <strong>Results</strong> 分頁查看 <code>results/</code> 資料。詳見 Reference 中的 <strong>CLI Execution</strong> 文件。</p>', es:'<p>Ejecute un nuevo benchmark desde la terminal del host del servidor:</p>' + _RUN_CODE + '<p>Al terminar, abra la pestaña <strong>Results</strong> para ver los datos de <code>results/</code>. Consulte la referencia <strong>CLI Execution</strong> para más detalles.</p>'} },
      ]
    },

    { id:'settings', icon:'⚙️',
      title:{ko:'⚙️ Settings', en:'⚙️ Settings', ja:'⚙️ 設定', 'zh-CN':'⚙️ 设置', 'zh-TW':'⚙️ 設定', es:'⚙️ Ajustes'},
      description:{ko:'벤치마크 실행 환경 설정', en:'Configure benchmark execution settings', ja:'ベンチマーク実行環境の設定', 'zh-CN':'配置基准测试执行环境', 'zh-TW':'設定基準測試執行環境', es:'Configure los ajustes de ejecución del benchmark'},
      beforeStart:function(){ switchTab('settings'); },
      steps:[
        { target:'.main-tab[data-tab="settings"]', position:'bottom',
          title:{ko:'Settings 탭', en:'Settings Tab', ja:'Settingsタブ', 'zh-CN':'Settings选项卡', 'zh-TW':'Settings分頁', es:'Pestaña Settings'},
          content:{ko:'벤치마크 실행에 필요한 <strong>환경 설정</strong>을 관리합니다. 경로, 온도, 반복 횟수 등 다양한 파라미터를 조절할 수 있습니다.', en:'Manage <strong>configuration settings</strong> for benchmark execution. Adjust parameters like paths, temperature, iteration count, and more.', ja:'ベンチマーク実行に必要な<strong>環境設定</strong>を管理します。パス、温度、繰り返し回数など様々なパラメータを調整できます。', 'zh-CN':'管理基准测试执行所需的<strong>环境配置</strong>。可以调整路径、温度、重复次数等各种参数。', 'zh-TW':'管理基準測試執行所需的<strong>環境設定</strong>。可以調整路徑、溫度、重複次數等各種參數。', es:'Gestione los <strong>ajustes de configuración</strong> para la ejecución del benchmark. Modifique parámetros como rutas, temperatura, número de iteraciones y más.'} },
        { target:'#settCooldownTemp', position:'right',
          title:{ko:'Cooldown 온도', en:'Cooldown Temperature', ja:'Cooldown温度', 'zh-CN':'Cooldown温度', 'zh-TW':'Cooldown溫度', es:'Temperatura de Cooldown'},
          content:{ko:'벤치마크 간 <strong>대기 온도 임계값(°C)</strong>입니다. NPU 온도가 이 값 이하로 내려갈 때까지 다음 벤치마크 시작을 대기합니다.', en:'<strong>Wait temperature threshold (°C)</strong> between benchmarks. Waits until NPU temperature drops below this value before starting next benchmark.', ja:'ベンチマーク間の<strong>待機温度閾値（°C）</strong>です。NPU温度がこの値以下に下がるまで次のベンチマーク開始を待機します。', 'zh-CN':'基准测试之间的<strong>等待温度阈值（°C）</strong>。等待NPU温度降至此值以下后才开始下一次基准测试。', 'zh-TW':'基準測試之間的<strong>等待溫度閾值（°C）</strong>。等待NPU溫度降至此值以下後才開始下一次基準測試。', es:'<strong>Umbral de temperatura de espera (°C)</strong> entre benchmarks. Espera a que la temperatura del NPU baje de este valor antes de iniciar el siguiente benchmark.'} },
        { target:'#settWaitInterval', position:'right',
          title:{ko:'Wait Interval', en:'Wait Interval', ja:'Wait Interval', 'zh-CN':'Wait Interval', 'zh-TW':'Wait Interval', es:'Intervalo de espera'},
          content:{ko:'반복 간 <strong>대기 시간(초)</strong>입니다. 각 벤치마크 반복 사이에 지정된 시간만큼 대기합니다.', en:'<strong>Delay (seconds)</strong> between iterations. Waits the specified time between each benchmark iteration.', ja:'繰り返し間の<strong>待機時間（秒）</strong>です。各ベンチマーク繰り返しの間に指定された時間だけ待機します。', 'zh-CN':'每次重复之间的<strong>等待时间（秒）</strong>。在每次基准测试重复之间等待指定的时间。', 'zh-TW':'每次重複之間的<strong>等待時間（秒）</strong>。在每次基準測試重複之間等待指定的時間。', es:'<strong>Retardo (segundos)</strong> entre iteraciones. Espera el tiempo indicado entre cada iteración del benchmark.'} },
        { target:'#settIterations', position:'right',
          title:{ko:'반복 횟수', en:'Iterations', ja:'繰り返し回数', 'zh-CN':'迭代次数', 'zh-TW':'迭代次數', es:'Iteraciones'},
          content:{ko:'벤치마크 <strong>반복 실행 횟수</strong>입니다. 값이 클수록 측정 결과의 신뢰도가 높아지지만 실행 시간이 증가합니다.', en:'Number of <strong>benchmark iterations</strong>. Higher values increase measurement reliability but also increase execution time.', ja:'ベンチマークの<strong>繰り返し実行回数</strong>です。値が大きいほど測定結果の信頼性が高まりますが、実行時間が増加します。', 'zh-CN':'基准测试的<strong>重复执行次数</strong>。值越大测量结果的可靠性越高，但执行时间也会增加。', 'zh-TW':'基準測試的<strong>重複執行次數</strong>。值越大測量結果的可靠性越高，但執行時間也會增加。', es:'Número de <strong>iteraciones del benchmark</strong>. Valores más altos aumentan la fiabilidad de la medición, pero también el tiempo de ejecución.'} },
        { target:'#settWarmup', position:'right',
          title:{ko:'Warmup 횟수', en:'Warmup Runs', ja:'Warmup回数', 'zh-CN':'Warmup次数', 'zh-TW':'Warmup次數', es:'Ejecuciones de Warmup'},
          content:{ko:'측정 전 <strong>워밍업 실행 횟수</strong>입니다. 초기 성능 불안정을 제거하기 위해 지정된 횟수만큼 사전 실행합니다.', en:'Number of <strong>warmup runs</strong> before measurement. Pre-runs the specified count to eliminate initial performance instability.', ja:'測定前の<strong>ウォームアップ実行回数</strong>です。初期パフォーマンスのばらつきを取り除くために指定回数だけ事前実行します。', 'zh-CN':'测量前的<strong>预热运行次数</strong>。为消除初始性能不稳定而预先运行指定次数。', 'zh-TW':'測量前的<strong>預熱執行次數</strong>。為消除初始效能不穩定而預先執行指定次數。', es:'Número de <strong>ejecuciones de warmup</strong> antes de la medición. Ejecuta previamente el recuento indicado para eliminar la inestabilidad inicial del rendimiento.'} },
        { target:'#settFpsThreshold', position:'right',
          title:{ko:'FPS 임계값', en:'FPS Threshold', ja:'FPS閾値', 'zh-CN':'FPS阈值', 'zh-TW':'FPS閾值', es:'Umbral FPS'},
          content:{ko:'<strong>최소 FPS 기준값</strong>입니다. 이 값 이하의 FPS 결과는 경고로 표시되거나 리포트에서 하이라이트됩니다.', en:'<strong>Minimum FPS threshold</strong>. FPS results below this value are flagged as warnings or highlighted in reports.', ja:'<strong>最小FPS基準値</strong>です。この値以下のFPS結果は警告として表示されるか、レポートでハイライトされます。', 'zh-CN':'<strong>最小FPS基准值</strong>。低于此值的FPS结果将显示为警告或在报告中高亮。', 'zh-TW':'<strong>最小FPS基準值</strong>。低於此值的FPS結果將顯示為警告或在報告中醒目提示。', es:'<strong>Umbral mínimo de FPS</strong>. Los resultados por debajo de este valor se marcan como advertencias o se resaltan en los informes.'} },
        { target:'.settings-notice', position:'bottom',
          title:{ko:'배포 고정 설정', en:'Deployment-fixed Settings', ja:'デプロイ固定設定', 'zh-CN':'部署固定设置', 'zh-TW':'部署固定設定', es:'Ajustes fijos en el despliegue'},
          content:{ko:'이 릴리즈에서는 경로와 실행 파라미터가 <strong>배포 시점에 고정</strong>됩니다. 변경하려면 서버 시작 전 설정 파일을 수정하세요.', en:'In this release, paths and runtime parameters are <strong>fixed at deployment</strong>. Edit configuration files before starting the server to change them.', ja:'このリリースではパスと実行パラメータは<strong>デプロイ時に固定</strong>されます。変更するにはサーバー起動前に設定ファイルを編集してください。', 'zh-CN':'此版本中的路径和运行参数在<strong>部署时固定</strong>。如需更改，请在启动服务器前编辑配置文件。', 'zh-TW':'此版本中的路徑與執行參數在<strong>部署時固定</strong>。如需變更，請在啟動伺服器前編輯設定檔。', es:'En esta versión, las rutas y los parámetros de ejecución están <strong>fijados en el despliegue</strong>. Edite los archivos de configuración antes de iniciar el servidor para modificarlos.'} },
      ]
    },

    { id:'edgeguide-link', icon:'💰',
      title:{ko:'💰 EdgeGuide 연동', en:'💰 EdgeGuide Integration', ja:'💰 EdgeGuide連携', 'zh-CN':'💰 EdgeGuide集成', 'zh-TW':'💰 EdgeGuide整合', es:'💰 Integración con EdgeGuide'},
      description:{ko:'벤치마크 필터 조건으로 EdgeGuide 최적 제품 추천', en:'Get optimal product recommendations via EdgeGuide with benchmark filters', ja:'ベンチマークフィルター条件でEdgeGuide最適製品を推薦', 'zh-CN':'通过基准测试筛选条件获取EdgeGuide最佳产品推荐', 'zh-TW':'透過基準測試篩選條件獲取EdgeGuide最佳產品推薦', es:'Obtenga recomendaciones de producto óptimas en EdgeGuide con los filtros del benchmark'},
      prerequisite:'dashboard-metrics',
      beforeStart: function () {
        return new Promise(function (resolve) {
          switchTab('dashboard');
          setTimeout(function () {
            var tab = document.querySelector('.dashboard-tab[data-tab="overview"]');
            if (tab) tab.click();
            resolve();
          }, 400);
        });
      },
      steps:[
        { target:'#edgeguideBtn', position:'bottom',
          title:{ko:'EdgeGuide 버튼', en:'EdgeGuide Button', ja:'EdgeGuideボタン', 'zh-CN':'EdgeGuide按钮', 'zh-TW':'EdgeGuide按鈕', es:'Botón EdgeGuide'},
          content:{ko:'<strong>💰 EdgeGuide</strong> 버튼을 클릭하면 현재 벤치마크 필터 조건(Task, Size, ORT)을 그대로 EdgeGuide에 전달하여 <strong>최적 제품 추천</strong>을 받을 수 있습니다.', en:'Click the <strong>💰 EdgeGuide</strong> button to pass current benchmark filter conditions (Task, Size, ORT) to EdgeGuide for <strong>optimal product recommendations</strong>.', ja:'<strong>💰 EdgeGuide</strong>ボタンをクリックすると、現在のベンチマークフィルター条件（Task、Size、ORT）をそのままEdgeGuideに渡して<strong>最適製品推薦</strong>を受けることができます。', 'zh-CN':'点击<strong>💰 EdgeGuide</strong>按钮后，会将当前基准测试筛选条件（Task、Size、ORT）直接传递给EdgeGuide以获取<strong>最佳产品推荐</strong>。', 'zh-TW':'點擊<strong>💰 EdgeGuide</strong>按鈕後，會將目前基準測試篩選條件（Task、Size、ORT）直接傳遞給EdgeGuide以獲取<strong>最佳產品推薦</strong>。', es:'Haga clic en el botón <strong>💰 EdgeGuide</strong> para enviar a EdgeGuide las condiciones de filtro actuales del benchmark (Task, Size, ORT) y obtener <strong>recomendaciones de producto óptimas</strong>.'} },
        { target:'.edgeguide-link', position:'top',
          title:{ko:'상세 패널의 EdgeGuide 링크', en:'EdgeGuide Link in Detail Panel', ja:'詳細パネルのEdgeGuideリンク', 'zh-CN':'详情面板中的EdgeGuide链接', 'zh-TW':'詳情面板中的EdgeGuide連結', es:'Enlace EdgeGuide en el panel de detalle'},
          content:{ko:'차트 바를 클릭하여 환경 상세 패널을 연 후, 패널 내 <strong>EdgeGuide 링크</strong>(<code>.edgeguide-link</code>)를 찾아 클릭하면 해당 플랫폼 조건에 맞는 <strong>제품 비교 및 추천</strong> 페이지로 이동합니다.', en:'After clicking a chart bar to open the environment detail panel, find and click the <strong>EdgeGuide link</strong> (<code>.edgeguide-link</code>) within the panel to navigate to a <strong>product comparison and recommendation</strong> page tailored to that platform.', ja:'チャートバーをクリックして環境詳細パネルを開いた後、パネル内の<strong>EdgeGuideリンク</strong>（<code>.edgeguide-link</code>）を見つけてクリックすると、そのプラットフォーム条件に合った<strong>製品比較および推薦</strong>ページに移動します。', 'zh-CN':'点击图表柱形打开环境详情面板后，找到面板内的<strong>EdgeGuide链接</strong>（<code>.edgeguide-link</code>）并点击，即可跳转到符合该平台条件的<strong>产品比较和推荐</strong>页面。', 'zh-TW':'點擊圖表長條打開環境詳情面板後，找到面板內的<strong>EdgeGuide連結</strong>（<code>.edgeguide-link</code>）並點擊，即可跳轉到符合該平台條件的<strong>產品比較和推薦</strong>頁面。', es:'Tras hacer clic en una barra del gráfico para abrir el panel de detalle del entorno, localice y haga clic en el <strong>enlace EdgeGuide</strong> (<code>.edgeguide-link</code>) del panel para ir a una página de <strong>comparación y recomendación de productos</strong> adaptada a esa plataforma.'},
          beforeStep:function(){ _ensureEdgeGuideLink(); _scrollTo('.edgeguide-link'); } },
      ]
    },
  ];

  var referenceDocs = [
    { id:'ref-dashboard', icon:'📊', title:{ko:'Dashboard 가이드', en:'Dashboard Guide', ja:'ダッシュボードガイド', 'zh-CN':'仪表盘指南', 'zh-TW':'儀表板指南', es:'Guía del panel'},
      body:{ko:'<h3>5개 서브탭</h3><ul><li><strong>E2E FPS Overview</strong>: 전체 플랫폼 FPS 비교 (그룹 바 차트)</li><li><strong>Full Metrics</strong>: NPU Throughput + E2E FPS + Latency 3중 메트릭</li><li><strong>Detailed Data</strong>: 원시 수치 테이블, 열 정렬, Best 하이라이트, NPU 온도/클럭·상태 배지</li><li><strong>Version Trend</strong>: dx-all-suite 버전 필터 + 지표별 소형 차트</li><li><strong>ORT ON/OFF</strong>: 동일 모델·환경에서 ORT On/Off 성능 비교</li></ul><p>모든 서브탭에서 차트 바/포인트를 클릭하면 환경 상세 패널이 열립니다.</p>', en:'<h3>5 Sub-tabs</h3><ul><li><strong>E2E FPS Overview</strong>: Cross-platform FPS comparison</li><li><strong>Full Metrics</strong>: NPU Throughput + E2E FPS + Latency triple metrics</li><li><strong>Detailed Data</strong>: Raw numeric tables with sorting, Best highlights, and NPU temp/clock + status badges</li><li><strong>Version Trend</strong>: dx-all-suite version filter + per-metric small charts</li><li><strong>ORT ON/OFF</strong>: Compare ORT On/Off performance for the same model and environment</li></ul><p>Click chart bars/points in any sub-tab to open the environment detail panel.</p>', ja:'<h3>5つのサブタブ</h3><ul><li><strong>E2E FPS Overview</strong>：全プラットフォームFPS比較（グループバーチャート）</li><li><strong>Full Metrics</strong>：NPU Throughput + E2E FPS + Latencyトリプルメトリクス</li><li><strong>Detailed Data</strong>：生データテーブル、列ソート、Bestハイライト、NPU温度/クロック・ステータスバッジ</li><li><strong>Version Trend</strong>：dx-all-suiteバージョンフィルター + 指標別スモールチャート</li><li><strong>ORT ON/OFF</strong>：同一モデル・環境でのORT On/Offパフォーマンス比較</li></ul><p>すべてのサブタブでチャートバー/ポイントをクリックすると環境詳細パネルが開きます。</p>', 'zh-CN':'<h3>5个子选项卡</h3><ul><li><strong>E2E FPS Overview</strong>：全平台FPS比较（分组柱状图）</li><li><strong>Full Metrics</strong>：NPU吞吐量 + E2E FPS + 延迟三重指标</li><li><strong>Detailed Data</strong>：原始数据表格、列排序、最佳值高亮、NPU温度/时钟频率与状态标记</li><li><strong>Version Trend</strong>：dx-all-suite版本筛选 + 按指标分类的小图表</li><li><strong>ORT ON/OFF</strong>：比较相同模型与环境下ORT开/关的性能</li></ul><p>在所有子选项卡中点击图表柱形/数据点可打开环境详情面板。</p>', 'zh-TW':'<h3>5個子分頁</h3><ul><li><strong>E2E FPS Overview</strong>：全平台FPS比較（分組長條圖）</li><li><strong>Full Metrics</strong>：NPU吞吐量 + E2E FPS + 延遲三重指標</li><li><strong>Detailed Data</strong>：原始資料表格、欄位排序、最佳值醒目提示、NPU溫度/時脈與狀態標記</li><li><strong>Version Trend</strong>：dx-all-suite版本篩選 + 按指標分類的小圖表</li><li><strong>ORT ON/OFF</strong>：比較相同模型與環境下ORT開/關的效能</li></ul><p>在所有子分頁中點擊圖表長條/資料點可打開環境詳情面板。</p>', es:'<h3>5 subpestañas</h3><ul><li><strong>E2E FPS Overview</strong>: comparación de FPS entre plataformas</li><li><strong>Full Metrics</strong>: triple métrica NPU Throughput + E2E FPS + Latency</li><li><strong>Detailed Data</strong>: tablas numéricas en bruto con ordenación, resaltado de mejores valores e insignias de temperatura/reloj NPU y estado</li><li><strong>Version Trend</strong>: filtro de versión de dx-all-suite + gráficos pequeños por métrica</li><li><strong>ORT ON/OFF</strong>: compare el rendimiento ORT activado/desactivado para el mismo modelo y entorno</li></ul><p>Haga clic en barras o puntos del gráfico en cualquier subpestaña para abrir el panel de detalle del entorno.</p>'} },
    { id:'ref-cli', icon:'▶️', title:{ko:'CLI 실행', en:'CLI Execution', ja:'CLI実行', 'zh-CN':'CLI执行', 'zh-TW':'CLI執行', es:'Ejecución por CLI'},
      body:{ko:'<h3>벤치마크 실행</h3><p>웹 UI는 결과 조회 전용입니다. 실행은 터미널에서 수행하세요.</p><ol><li><code>cd dx-benchmark</code></li><li><code>./run.sh run</code></li><li>완료 후 Results/Dashboard에서 <code>results/</code> 데이터 확인</li></ol>', en:'<h3>Run Benchmarks</h3><p>The web UI is view-only. Run from a terminal:</p><ol><li><code>cd dx-benchmark</code></li><li><code>./run.sh run</code></li><li>View <code>results/</code> in Dashboard/Results when done</li></ol>', ja:'<h3>ベンチマーク実行</h3><p>Web UIは結果閲覧専用です。ターミナルで実行してください。</p><ol><li><code>cd dx-benchmark</code></li><li><code>./run.sh run</code></li><li>完了後 Dashboard/Results で <code>results/</code> を確認</li></ol>', 'zh-CN':'<h3>运行基准测试</h3><p>Web UI仅用于查看结果。请在终端中运行：</p><ol><li><code>cd dx-benchmark</code></li><li><code>./run.sh run</code></li><li>完成后在 Dashboard/Results 查看 <code>results/</code></li></ol>', 'zh-TW':'<h3>執行基準測試</h3><p>Web UI僅用於查看結果。請在終端機執行：</p><ol><li><code>cd dx-benchmark</code></li><li><code>./run.sh run</code></li><li>完成後在 Dashboard/Results 查看 <code>results/</code></li></ol>', es:'<h3>Ejecutar benchmarks</h3><p>La UI web es solo de consulta. Ejecute en terminal:</p><ol><li><code>cd dx-benchmark</code></li><li><code>./run.sh run</code></li><li>Consulte <code>results/</code> en Dashboard/Results al terminar</li></ol>'} },
    { id:'ref-results', icon:'📁', title:{ko:'결과 탐색', en:'Results Browser', ja:'結果ブラウザ', 'zh-CN':'结果浏览器', 'zh-TW':'結果瀏覽器', es:'Explorador de resultados'},
      body:{ko:'<h3>탐색 흐름</h3><p><strong>HW 카드 선택 → Run 목록 → 결과 섹션</strong> 순서로 탐색합니다. 📋 아이콘이 있는 run은 Markdown 리포트를 포함합니다.</p>', en:'<h3>Browse Flow</h3><p><strong>Select HW card → Run list → Result sections</strong>. Runs with 📋 icon include Markdown reports.</p>', ja:'<h3>閲覧フロー</h3><p><strong>HWカード選択 → Run一覧 → 結果セクション</strong>の順で探索します。📋アイコンがあるrunはMarkdownレポートを含みます。</p>', 'zh-CN':'<h3>浏览流程</h3><p><strong>选择HW卡片 → Run列表 → 结果区域</strong>的顺序进行浏览。带有📋图标的run包含Markdown报告。</p>', 'zh-TW':'<h3>瀏覽流程</h3><p><strong>選擇HW卡片 → Run列表 → 結果區域</strong>的順序進行瀏覽。帶有📋圖示的run包含Markdown報告。</p>', es:'<h3>Flujo de exploración</h3><p><strong>Seleccione tarjeta HW → lista de Run → secciones de resultados</strong>. Los runs con icono 📋 incluyen informes Markdown.</p>'} },
    { id:'ref-settings', icon:'⚙️', title:{ko:'설정', en:'Settings', ja:'設定', 'zh-CN':'设置', 'zh-TW':'設定', es:'Ajustes'},
      body:{ko:'<h3>설정 항목</h3><ul><li><strong>Cooldown Temp</strong>: 벤치마크 간 대기 온도</li><li><strong>Wait</strong>: 반복 간 대기 시간</li><li><strong>Iterations</strong>: 반복 횟수</li><li><strong>Warmup</strong>: 워밍업 횟수</li><li><strong>FPS Threshold</strong>: 최소 FPS 기준</li></ul>', en:'<h3>Settings</h3><ul><li><strong>Cooldown Temp</strong>: Wait temperature between benchmarks</li><li><strong>Wait</strong>: Delay between iterations</li><li><strong>Iterations</strong>: Number of iterations</li><li><strong>Warmup</strong>: Warmup count</li><li><strong>FPS Threshold</strong>: Minimum FPS threshold</li></ul>', ja:'<h3>設定項目</h3><ul><li><strong>Cooldown Temp</strong>：ベンチマーク間の待機温度</li><li><strong>Wait</strong>：繰り返し間の待機時間</li><li><strong>Iterations</strong>：繰り返し回数</li><li><strong>Warmup</strong>：ウォームアップ回数</li><li><strong>FPS Threshold</strong>：最小FPS基準</li></ul>', 'zh-CN':'<h3>设置项目</h3><ul><li><strong>Cooldown Temp</strong>：基准测试间等待温度</li><li><strong>Wait</strong>：重复间等待时间</li><li><strong>Iterations</strong>：重复次数</li><li><strong>Warmup</strong>：预热次数</li><li><strong>FPS Threshold</strong>：最小FPS基准</li></ul>', 'zh-TW':'<h3>設定項目</h3><ul><li><strong>Cooldown Temp</strong>：基準測試間等待溫度</li><li><strong>Wait</strong>：重複間等待時間</li><li><strong>Iterations</strong>：重複次數</li><li><strong>Warmup</strong>：預熱次數</li><li><strong>FPS Threshold</strong>：最小FPS基準</li></ul>', es:'<h3>Ajustes</h3><ul><li><strong>Cooldown Temp</strong>: temperatura de espera entre benchmarks</li><li><strong>Wait</strong>: retardo entre iteraciones</li><li><strong>Iterations</strong>: número de iteraciones</li><li><strong>Warmup</strong>: recuento de warmup</li><li><strong>FPS Threshold</strong>: umbral mínimo de FPS</li></ul>'} },
    { id:'ref-edgeguide', icon:'💰', title:{ko:'EdgeGuide 연동', en:'EdgeGuide Integration', ja:'EdgeGuide連携', 'zh-CN':'EdgeGuide集成', 'zh-TW':'EdgeGuide整合', es:'Integración con EdgeGuide'},
      body:{ko:'<h3>EdgeGuide 연동</h3><p>💰 버튼 또는 환경 상세 패널의 링크를 클릭하면 현재 벤치마크 필터 조건(Task, Size, ORT)을 그대로 EdgeGuide에 전달하여 최적 제품 추천을 받을 수 있습니다.</p>', en:'<h3>EdgeGuide Integration</h3><p>Click the 💰 button or the link in environment detail panel to pass current benchmark filters (Task, Size, ORT) to EdgeGuide for optimal product recommendation.</p>', ja:'<h3>EdgeGuide連携</h3><p>💰ボタンまたは環境詳細パネルのリンクをクリックすると、現在のベンチマークフィルター条件（Task、Size、ORT）をそのままEdgeGuideに渡して最適製品推薦を受けることができます。</p>', 'zh-CN':'<h3>EdgeGuide集成</h3><p>点击💰按钮或环境详情面板中的链接，即可将当前基准测试筛选条件（Task、Size、ORT）直接传递给EdgeGuide以获取最佳产品推荐。</p>', 'zh-TW':'<h3>EdgeGuide整合</h3><p>點擊💰按鈕或環境詳情面板中的連結，即可將目前基準測試篩選條件（Task、Size、ORT）直接傳遞給EdgeGuide以獲取最佳產品推薦。</p>', es:'<h3>Integración con EdgeGuide</h3><p>Haga clic en el botón 💰 o en el enlace del panel de detalle del entorno para enviar a EdgeGuide los filtros actuales del benchmark (Task, Size, ORT) y obtener la recomendación de producto óptima.</p>'} },
  ];

  window.DXTutorial.create({
    appId: 'benchmark',
    sections: sections,
    referenceDocs: referenceDocs,
    toolbarSelector: '#dxToolbar',
    skipButtons: true,
    getLang: function () { return localStorage.getItem('dx-lang') || 'en'; },
    onNav: function (tab) { switchTab(tab); },
    onComplete: function (sectionId) {
      var engine = window._dxTutorial;
      var lang = engine.getLang();
      var sec = engine.sections.find(function (s) { return s.id === sectionId; });
      if (typeof toast === 'function' && sec) {
        toast('✅ "' + engine._t(sec.title) + '" ' + engine._tl('tutorial complete!'), 'ok');
      }
    },
    patchNav: function () {}
  });
})();
