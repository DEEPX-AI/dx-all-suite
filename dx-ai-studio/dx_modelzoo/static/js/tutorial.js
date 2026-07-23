/* ═══════════════════════════════════════════════════════════════
   DX ModelZoo — Tutorial Definitions
   7 sections, ~47 steps, 6-language support
   ───────────────────────────────────────────────────────────────
   Audit-based revision:
     A. Replaced fragile nth-child selectors with stable IDs
        (#sectionUseCase, #sectionExample, #sectionCompile,
         #sectionLegal — added in detail.js)
     B. Added existence guards for conditional elements
        (.mz-download-badge, downloadModel button, .mz-spec-table)
        Changed type-specific targets to target:null
        (.mz-ba-container, #overlayImg, #classificationResults)
     C. Fixed tooltip positions (#dxAppStatus→bottom,
        #catalogContainer→bottom, .mz-code-copy→top)
     D. Added steps for uncovered features (inference upload/run,
        individual code tabs, ONNX/graph viewer, card click,
        chat input/send)
     E. Verified chat selectors (.dx-chat-*)
     F. Increased pollFor timeout to 5s
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  // detail 페이지로 이동하는 공통 헬퍼 — Promise 반환
  // route()가 detailView를 display='' 처리 후 renderDetailPage()가 API 호출,
  // renderDetail() 완료 시에만 .mz-back-btn이 DOM에 생김 → 그때까지 폴링
  function goDetail() {
    return new Promise(function(resolve) {
      var cardTries = 0;
      (function waitCard() {
        var firstCard = document.querySelector('#catalogContainer .mz-card');
        if (firstCard) {
          var modelId = firstCard.getAttribute('data-model-id') || firstCard.getAttribute('data-id') || firstCard.dataset.modelId || firstCard.dataset.id;
          if (modelId) {
            location.hash = 'model=' + encodeURIComponent(modelId);
            var btnTries = 0;
            (function waitBtn() {
              var dv = document.getElementById('detailView');
              var header = document.querySelector('#detailView .mz-detail-header');
              var badge = document.querySelector('#detailView .mz-detail-hero-badges .mz-download-badge');
              var badgeRect = badge ? badge.getBoundingClientRect() : null;
              var badgeReady = !!(badgeRect && badgeRect.width > 0 && badgeRect.height > 0);
              if (document.querySelector('.mz-back-btn') && dv && dv.style.display !== 'none' && header && badgeReady) {
                return resolve();
              }
              if (++btnTries >= 80) return resolve();
              setTimeout(waitBtn, 100);
            })();
            return;
          }
        }
        if (++cardTries >= 30) return resolve();
        setTimeout(waitCard, 100);
      })();
    });
  }

  // 비동기 DOM 폴링 헬퍼 (최대 maxTries × 100ms, 기본 50회 = 5초)
  function pollFor(selector, maxTries) {
    var limit = maxTries || 50;
    var tries = 0;
    (function poll() {
      if (document.querySelector(selector)) return;
      if (++tries >= limit) return;
      setTimeout(poll, 100);
    })();
  }

  function scrollTo(selector) {
    var el = document.querySelector(selector);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function _ensureCategoryChip() {
    pollFor('#categoryChips .mz-category-option:nth-child(2)', 50);
    var chip = document.querySelector('#categoryChips .mz-category-option:nth-child(2)');
    if (chip) chip.scrollIntoView({ block: 'nearest' });
  }

  function _scrollToDownloadBadge() {
    var badge = document.querySelector('#detailView .mz-detail-hero-badges .mz-download-badge');
    if (badge) badge.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  }

  // ── Tutorial mock helpers ────────────────────────────────────────────
  // Several detail-page features are type-specific (before_after / overlay /
  // classified example widgets) or transient (download progress + completion,
  // inference results) and are therefore absent when the tour opens an
  // arbitrary model. Mirror the dx_app / dx_stream pattern: inject a labelled
  // #dxt-mock-* preview into the REAL container so each step has a real,
  // visible element to spotlight, then clear it on step exit (afterStep chain).
  function _lang() { return localStorage.getItem('dx-lang') || 'en'; }
  function _lc(m) { return m[_lang()] || m.en; }
  function _mockImg(label) {
    return 'data:image/svg+xml,' + encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" width="280" height="150">' +
      '<rect width="100%" height="100%" fill="#1a2332"/>' +
      '<text x="50%" y="50%" fill="#8b949e" font-size="13" text-anchor="middle" dy=".3em">' +
      (label || 'Tutorial preview') + '</text></svg>');
  }
  function _clearMocks() {
    document.querySelectorAll('[id^="dxt-mock-"]').forEach(function (n) { n.remove(); });
  }

  // Inject a demo of one example display type into the real #sectionExample.
  function _mockExample(kind) {
    var host = document.querySelector('#sectionExample');
    if (!host) return;
    var old = document.getElementById('dxt-mock-example');
    if (old) old.remove();
    var box = document.createElement('div');
    box.id = 'dxt-mock-example';
    box.style.cssText = 'margin:12px 0;padding:12px;border:1px dashed var(--border,#3a3a3a);border-radius:8px;background:var(--bg-2,#161b22)';
    if (kind === 'before_after') {
      box.innerHTML = '<div class="mz-ba-container" style="position:relative;max-width:280px">' +
        '<img src="' + _mockImg('After') + '" class="mz-example-image" style="width:100%;display:block">' +
        '<div class="mz-ba-slider" style="position:absolute;top:0;bottom:0;left:50%;width:3px;background:var(--accent,#4c8dff);cursor:ew-resize"></div>' +
        '</div>' +
        '<div style="display:flex;justify-content:space-between;font-size:12px;color:var(--text-3);margin-top:6px"><span>Before</span><span>After</span></div>';
    } else if (kind === 'overlay') {
      box.innerHTML = '<div class="mz-example-overlay" style="max-width:280px">' +
        '<img src="' + _mockImg('Overlay') + '" id="overlayImg" class="mz-example-overlay-result" style="width:100%;display:block;opacity:.6">' +
        '<label style="display:flex;align-items:center;gap:8px;margin-top:8px;font-size:14px">' +
        '<input type="range" min="0" max="100" value="60"> Overlay</label></div>';
    } else if (kind === 'classified') {
      var bars = [['golden retriever', 0.92], ['labrador', 0.05], ['dingo', 0.02]].map(function (r) {
        return '<div style="display:flex;align-items:center;gap:8px;margin:4px 0;font-size:13px">' +
          '<span style="width:110px">' + r[0] + '</span>' +
          '<span style="flex:1;height:10px;background:var(--bg-3,#0d1117);border-radius:5px;overflow:hidden">' +
          '<span style="display:block;height:100%;width:' + (r[1] * 100) + '%;background:var(--accent,#4c8dff)"></span></span>' +
          '<span>' + (r[1] * 100).toFixed(0) + '%</span></div>';
      }).join('');
      box.innerHTML = '<div id="classificationResults" class="mz-classified-results" style="max-width:340px">' + bars + '</div>';
    }
    host.appendChild(box);
    box.scrollIntoView({ block: 'center' });
  }

  // Inject a download progress bar / completion badge into the real download area.
  function _mockDownload(state) {
    var host = document.querySelector('#detailView [data-detail-downloads]') ||
      document.querySelector('#detailView .mz-detail-hero-badges');
    if (!host) return;
    var old = document.getElementById('dxt-mock-dl');
    if (old) old.remove();
    var box = document.createElement('div');
    box.id = 'dxt-mock-dl';
    box.style.cssText = 'margin-top:8px;font-size:13px;width:100%';
    if (state === 'complete') {
      box.innerHTML = '<span class="mz-download-badge ready" style="color:var(--success,#3fb950)">✅ ' +
        _lc({ ko: '다운로드 완료', en: 'Download complete', ja: 'ダウンロード完了', 'zh-CN': '下载完成', 'zh-TW': '下載完成', es: 'Descarga completada' }) + '</span>';
    } else {
      box.innerHTML = '<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">' +
        '<div style="flex:1;min-width:120px;height:6px;background:var(--bg-3,#0d1117);border-radius:3px;overflow:hidden">' +
        '<div style="width:65%;height:100%;background:var(--accent,#4c8dff)"></div></div>' +
        '<span>65%</span><span style="color:var(--text-3)">' +
        _lc({ ko: '다운로드 중', en: 'Downloading', ja: 'ダウンロード中', 'zh-CN': '下载中', 'zh-TW': '下載中', es: 'Descargando' }) + '</span>' +
        '<button class="mz-btn mz-btn-outline" style="font-size:12px;padding:2px 8px">✕</button></div>';
    }
    host.appendChild(box);
    host.scrollIntoView({ block: 'center' });
  }

  // Open the inference panel and inject a completed inference-result preview.
  function _mockInference() {
    var panel = document.querySelector('#inferencePanel');
    if (panel) { var det = panel.closest('details'); if (det) det.open = true; }
    var host = document.querySelector('#inferenceResultUpload') || panel;
    if (!host) return;
    var old = document.getElementById('dxt-mock-inf');
    if (old) old.remove();
    var box = document.createElement('div');
    box.id = 'dxt-mock-inf';
    box.style.cssText = 'margin-top:12px';
    box.innerHTML = '<div class="mz-inference-result" style="max-width:320px">' +
      '<img src="' + _mockImg('Result') + '" style="max-width:100%;display:block">' +
      '<div class="mz-pred-list" style="margin-top:8px"><span class="mz-pred-tag">person</span>' +
      '<div class="mz-pred-item">person (98%)</div><div class="mz-pred-item">car (91%)</div></div></div>' +
      '<div class="mz-inference-stats" style="display:flex;gap:16px;margin-top:8px;font-size:13px">' +
      '<div>FPS: <span class="stat-value">142</span></div>' +
      '<div>Latency: <span class="stat-value">7.0ms</span></div></div>';
    host.appendChild(box);
    box.scrollIntoView({ block: 'center' });
  }

  var sections = [

    { id: 'topbar', icon: '🔝',
      title: { ko: '🔝 상단 바', en: '🔝 Top Bar', ja: '🔝 トップバー', 'zh-CN': '🔝 顶部栏', 'zh-TW': '🔝 頂部列', es: '🔝 Barra superior' },
      description: { ko: '상단 바 UI 요소 소개', en: 'Top bar UI elements overview', ja: 'トップバーUI要素の紹介', 'zh-CN': '顶部栏UI元素概览', 'zh-TW': '頂部列UI元素概覽', es: 'Descripción general de los elementos de la barra superior' },
      steps: [
        { target: '.mz-topbar', position: 'bottom',
          title: { ko: '상단 바', en: 'Top Bar', ja: 'トップバー', 'zh-CN': '顶部栏', 'zh-TW': '頂部列', es: 'Barra superior' },
          content: { ko: 'ModelZoo의 <strong>상단 바</strong>입니다. 모델 카운트, 테마/언어 전환, DX App 연결 상태를 한눈에 확인할 수 있습니다.', en: 'The ModelZoo <strong>top bar</strong>. View model count, theme/language toggle, and DX App connection status at a glance.', ja: 'ModelZoo の<strong>トップバー</strong>です。モデル数、テーマ/言語切替、DX App接続状態を一目で確認できます。', 'zh-CN': '模型库<strong>顶部栏</strong>。一目了然地查看模型数量、主题/语言切换和DX App连接状态。', 'zh-TW': '模型庫<strong>頂部列</strong>。一目了然地查看模型數量、主題/語言切換和DX App連線狀態。', es: 'La <strong>barra superior</strong> de ModelZoo. Vea de un vistazo el recuento de modelos, el selector de tema/idioma y el estado de conexión de DX App.' } },
        { target: '#modelCount', position: 'bottom',
          title: { ko: '모델 카운트', en: 'Model Count', ja: 'モデル数', 'zh-CN': '模型数量', 'zh-TW': '模型數量', es: 'Recuento de modelos' },
          content: { ko: '현재 필터 조건에 맞는 <strong>모델 수</strong>를 표시합니다. 카테고리 필터나 검색어에 따라 실시간으로 변경됩니다.', en: 'Shows the <strong>number of models</strong> matching current filters. Updates in real-time as you filter or search.', ja: '現在のフィルター条件に一致する<strong>モデル数</strong>を表示します。フィルターや検索に応じてリアルタイムに更新されます。', 'zh-CN': '显示与当前筛选条件匹配的<strong>模型数量</strong>。随筛选或搜索实时更新。', 'zh-TW': '顯示與目前篩選條件匹配的<strong>模型數量</strong>。隨篩選或搜尋即時更新。', es: 'Muestra el <strong>número de modelos</strong> que coinciden con los filtros actuales. Se actualiza en tiempo real al filtrar o buscar.' } },
        { target: '#langToggle', position: 'left',
          title: { ko: '언어 전환', en: 'Language Toggle', ja: '言語切替', 'zh-CN': '语言切换', 'zh-TW': '語言切換', es: 'Selector de idioma' },
          content: { ko: '<strong>한국어/English</strong> 전환 버튼입니다. 모델 설명, UI 텍스트, 튜토리얼 내용 모두 전환됩니다.', en: 'Switch between <strong>Korean/English</strong>. All model descriptions, UI text, and tutorial content will change.', ja: '<strong>韓国語/English</strong>を切り替えます。モデル説明、UIテキスト、チュートリアル内容がすべて切り替わります。', 'zh-CN': '切换<strong>韩语/English</strong>。所有模型描述、UI文本和教程内容都将更改。', 'zh-TW': '切換<strong>韓語/English</strong>。所有模型描述、UI文字和教學內容都將更改。', es: 'Cambie entre <strong>coreano/inglés</strong>. Cambiarán todas las descripciones de modelos, textos de la interfaz y contenido del tutorial.' } },
        // position: bottom — 8×8px dot이므로 left보다 bottom이 안전
        { target: '#dxAppStatus', position: 'bottom',
          title: { ko: 'DX App 상태', en: 'DX App Status', ja: 'DX App 状態', 'zh-CN': 'DX App 状态', 'zh-TW': 'DX App 狀態', es: 'Estado de DX App' },
          content: { ko: '🟢 <strong>초록</strong> = DX App 연결됨 (다운로드 가능), 🔴 <strong>빨강</strong> = 오프라인 (다운로드 불가). DX App이 실행 중이어야 모델 다운로드가 가능합니다.', en: '🟢 <strong>Green</strong> = DX App connected (downloads available), 🔴 <strong>Red</strong> = offline (downloads unavailable). DX App must be running for model downloads.', ja: '🟢 <strong>緑</strong> = DX App接続済み（ダウンロード可能）、🔴 <strong>赤</strong> = オフライン（ダウンロード不可）。モデルのダウンロードにはDX Appの実行が必要です。', 'zh-CN': '🟢 <strong>绿色</strong> = DX App已连接（可下载），🔴 <strong>红色</strong> = 离线（无法下载）。模型下载需要DX App运行。', 'zh-TW': '🟢 <strong>綠色</strong> = DX App已連線（可下載），🔴 <strong>紅色</strong> = 離線（無法下載）。模型下載需要DX App執行。', es: '🟢 <strong>Verde</strong> = DX App conectada (descargas disponibles), 🔴 <strong>Rojo</strong> = sin conexión (descargas no disponibles). DX App debe estar en ejecución para descargar modelos.' } },
      ]
    },

    { id: 'catalog', icon: '📋',
      title: { ko: '📋 카탈로그 탐색', en: '📋 Catalog Browse', ja: '📋 カタログ閲覧', 'zh-CN': '📋 目录浏览', 'zh-TW': '📋 目錄瀏覽', es: '📋 Explorar catálogo' },
      description: { ko: '모델 검색, 필터링, 정렬 방법', en: 'Search, filter, and sort models', ja: 'モデルの検索、フィルター、ソート方法', 'zh-CN': '搜索、筛选和排序模型', 'zh-TW': '搜尋、篩選和排序模型', es: 'Busque, filtre y ordene modelos' },
      beforeStart: function () { if (location.hash) location.hash = ''; },
      steps: [
        { target: '#categoryChips', position: 'bottom',
          title: { ko: '카테고리 필터', en: 'Category Filters', ja: 'カテゴリフィルター', 'zh-CN': '类别筛选', 'zh-TW': '類別篩選', es: 'Filtros de categoría' },
          content: { ko: '<strong>칩</strong>을 클릭하여 카테고리별로 모델을 필터링합니다. 여러 칩을 동시에 선택하여 <strong>다중 필터</strong>도 가능합니다.', en: 'Click <strong>chips</strong> to filter models by category. Select multiple chips for <strong>multi-filtering</strong>.', ja: '<strong>チップ</strong>をクリックしてカテゴリ別にモデルをフィルタリングします。複数のチップを選択して<strong>複合フィルター</strong>も可能です。', 'zh-CN': '点击<strong>标签</strong>按类别筛选模型。选择多个标签进行<strong>多重筛选</strong>。', 'zh-TW': '點擊<strong>標籤</strong>按類別篩選模型。選擇多個標籤進行<strong>多重篩選</strong>。', es: 'Haga clic en las <strong>etiquetas</strong> para filtrar modelos por categoría. Seleccione varias etiquetas para <strong>filtrado múltiple</strong>.' } },
        { target: '#categoryChips', position: 'bottom',
          title: { ko: '"전체" 칩', en: '"All" Chip', ja: '「全体」チップ', 'zh-CN': '"全部"标签', 'zh-TW': '「全部」標籤', es: 'Etiqueta "All"' },
          content: { ko: '첫 번째 칩은 <strong>전체 보기(All)</strong>입니다. 클릭하면 모든 필터가 해제되어 전체 모델이 표시됩니다.', en: 'The first chip is <strong>All</strong>. Click to clear all filters and show every model.', ja: '最初のチップは<strong>全体表示（All）</strong>です。クリックするとすべてのフィルターが解除され、全モデルが表示されます。', 'zh-CN': '第一个标签是<strong>全部（All）</strong>。点击清除所有筛选条件，显示所有模型。', 'zh-TW': '第一個標籤是<strong>全部（All）</strong>。點擊清除所有篩選條件，顯示所有模型。', es: 'La primera etiqueta es <strong>All</strong>. Haga clic para borrar todos los filtros y mostrar todos los modelos.' } },
        { target: '#categoryChips .mz-category-option:nth-child(2)', position: 'bottom',
          title: { ko: '카테고리 칩', en: 'Category Chips', ja: 'カテゴリチップ', 'zh-CN': '类别标签', 'zh-TW': '類別標籤', es: 'Etiquetas de categoría' },
          content: { ko: '각 칩에는 <strong>아이콘 + 카테고리명 + 개수 배지</strong>가 표시됩니다. 예: 🎯 Detection (12). 여러 칩을 동시 선택하면 OR 조건으로 필터링됩니다.', en: 'Each chip shows <strong>icon + category name + count badge</strong>. e.g., 🎯 Detection (12). Multi-select applies OR filter.', ja: '各チップには<strong>アイコン + カテゴリ名 + 個数バッジ</strong>が表示されます。例：🎯 Detection (12)。複数選択でOR条件フィルタリングされます。', 'zh-CN': '每个标签显示<strong>图标 + 类别名 + 数量标记</strong>。例如：🎯 Detection (12)。多选时应用OR筛选。', 'zh-TW': '每個標籤顯示<strong>圖示 + 類別名 + 數量標記</strong>。例如：🎯 Detection (12)。多選時套用OR篩選。', es: 'Cada etiqueta muestra <strong>icono + nombre de categoría + insignia de conteo</strong>. p. ej., 🎯 Detection (12). La selección múltiple aplica filtro OR.' },
          beforeStep: function () { _ensureCategoryChip(); } },
        { target: '#searchInput', position: 'bottom',
          title: { ko: '모델 검색', en: 'Model Search', ja: 'モデル検索', 'zh-CN': '模型搜索', 'zh-TW': '模型搜尋', es: 'Búsqueda de modelos' },
          content: { ko: '모델 이름, 카테고리, 클래스명으로 <strong>실시간 검색</strong>합니다. 예: "yolo"를 입력하면 YOLOv5, YOLOv8 등이 즉시 필터링됩니다.', en: 'Search by model name, category, or class in <strong>real-time</strong>. e.g., typing "yolo" instantly filters to YOLOv5, YOLOv8, etc.', ja: 'モデル名、カテゴリ、クラス名で<strong>リアルタイム検索</strong>します。例：「yolo」と入力するとYOLOv5、YOLOv8などが即座にフィルタリングされます。', 'zh-CN': '按模型名称、类别或类名进行<strong>实时搜索</strong>。例如：输入"yolo"即可立即筛选出YOLOv5、YOLOv8等。', 'zh-TW': '按模型名稱、類別或類名進行<strong>即時搜尋</strong>。例如：輸入"yolo"即可立即篩選出YOLOv5、YOLOv8等。', es: 'Busque por nombre, categoría o clase del modelo en <strong>tiempo real</strong>. p. ej., al escribir "yolo" se filtra al instante a YOLOv5, YOLOv8, etc.' } },
        { target: '#btnCardView', position: 'bottom',
          title: { ko: '카드 뷰', en: 'Card View', ja: 'カードビュー', 'zh-CN': '卡片视图', 'zh-TW': '卡片檢視', es: 'Vista de tarjetas' },
          content: { ko: '모델을 <strong>카드 그리드</strong> 형태로 표시합니다. 각 카드에 모델명, FPS 배지, 다운로드 상태 배지가 표시됩니다.', en: 'Display models as a <strong>card grid</strong>. Each card shows model name, FPS badge, and download status badge.', ja: 'モデルを<strong>カードグリッド</strong>形式で表示します。各カードにモデル名、FPSバッジ、ダウンロード状態バッジが表示されます。', 'zh-CN': '以<strong>卡片网格</strong>形式显示模型。每张卡片显示模型名称、FPS标记和下载状态标记。', 'zh-TW': '以<strong>卡片網格</strong>形式顯示模型。每張卡片顯示模型名稱、FPS標記和下載狀態標記。', es: 'Muestre los modelos como una <strong>cuadrícula de tarjetas</strong>. Cada tarjeta muestra el nombre del modelo, la insignia FPS y el estado de descarga.' } },
        { target: '#btnListView', position: 'bottom',
          title: { ko: '리스트 뷰', en: 'List View', ja: 'リストビュー', 'zh-CN': '列表视图', 'zh-TW': '列表檢視', es: 'Vista de lista' },
          content: { ko: '<strong>테이블 형태</strong>로 표시합니다. 헤더를 클릭하면 해당 열 기준으로 <strong>오름차순/내림차순 정렬</strong>됩니다.', en: 'Display as a <strong>table</strong>. Click column headers to <strong>sort ascending/descending</strong>.', ja: '<strong>テーブル形式</strong>で表示します。ヘッダーをクリックすると該当列で<strong>昇順/降順ソート</strong>されます。', 'zh-CN': '以<strong>表格</strong>形式显示。点击列标题进行<strong>升序/降序排序</strong>。', 'zh-TW': '以<strong>表格</strong>形式顯示。點擊欄位標題進行<strong>升序/降序排序</strong>。', es: 'Muestre como <strong>tabla</strong>. Haga clic en los encabezados de columna para <strong>ordenar ascendente/descendente</strong>.' } },
        { target: '#sortSelect', position: 'bottom',
          title: { ko: '정렬', en: 'Sort', ja: 'ソート', 'zh-CN': '排序', 'zh-TW': '排序', es: 'Ordenar' },
          content: { ko: '<strong>이름순, 카테고리순, FPS순</strong>으로 정렬할 수 있습니다. 카드 뷰와 리스트 뷰 모두에 적용됩니다.', en: 'Sort by <strong>name, category, or FPS</strong>. Applies to both card and list views.', ja: '<strong>名前順、カテゴリ順、FPS順</strong>でソートできます。カードビューとリストビュー両方に適用されます。', 'zh-CN': '按<strong>名称、类别或FPS</strong>排序。适用于卡片视图和列表视图。', 'zh-TW': '按<strong>名稱、類別或FPS</strong>排序。適用於卡片檢視和列表檢視。', es: 'Ordene por <strong>nombre, categoría o FPS</strong>. Aplica a las vistas de tarjetas y de lista.' } },
        // Spotlight the first actual catalog card (scoped to #catalogContainer so it never
        // latches onto a stray .mz-card elsewhere in the DOM). position: bottom — the sticky
        // topbar can cover a 'top' callout.
        { target: '#catalogContainer .mz-card', position: 'bottom',
          title: { ko: '모델 카드', en: 'Model Cards', ja: 'モデルカード', 'zh-CN': '模型卡片', 'zh-TW': '模型卡片', es: 'Tarjetas de modelo' },
          content: { ko: '각 카드를 클릭하면 해당 모델의 <strong>상세 페이지</strong>로 이동합니다. 카드에는 모델명, 카테고리 아이콘, FPS 성능 배지(Q-Lite/Q-Pro), 다운로드 상태(✅/📥)가 표시됩니다.', en: 'Click any card to open its <strong>detail page</strong>. Each card shows the model name, category icon, FPS badges (Q-Lite/Q-Pro), and download status (✅/📥).', ja: '各カードをクリックすると該当モデルの<strong>詳細ページ</strong>に移動します。カードにはモデル名、カテゴリアイコン、FPSバッジ（Q-Lite/Q-Pro）、ダウンロード状態（✅/📥）が表示されます。', 'zh-CN': '点击任意卡片进入其<strong>模型详情页</strong>。每张卡片显示模型名称、类别图标、FPS 标记（Q-Lite/Q-Pro）和下载状态（✅/📥）。', 'zh-TW': '點擊任意卡片進入其<strong>模型詳情頁</strong>。每張卡片顯示模型名稱、類別圖示、FPS 標記（Q-Lite/Q-Pro）和下載狀態（✅/📥）。', es: 'Haga clic en cualquier tarjeta para abrir su <strong>página de detalle</strong>. Cada tarjeta muestra el nombre del modelo, el icono de categoría, las insignias FPS (Q-Lite/Q-Pro) y el estado de descarga (✅/📥).' },
          beforeStep: function () { scrollTo('#catalogContainer .mz-card'); } },
      ]
    },

    { id: 'detail', icon: '🔍',
      title: { ko: '🔍 모델 상세', en: '🔍 Model Detail', ja: '🔍 モデル詳細', 'zh-CN': '🔍 模型详情', 'zh-TW': '🔍 模型詳情', es: '🔍 Detalle del modelo' },
      description: { ko: '모델 사양, 설명, 법적 정보 확인', en: 'View model specs, description, and legal info', ja: 'モデルの仕様、説明、法的情報の確認', 'zh-CN': '查看模型规格、描述和法律信息', 'zh-TW': '查看模型規格、描述和法律資訊', es: 'Vea especificaciones, descripción e información legal del modelo' },
      prerequisite: 'catalog',
      prerequisiteMessage: { ko: '먼저 카탈로그 섹션을 완료하세요.', en: 'Complete the Catalog section first.', ja: '先にカタログセクションを完了してください。', 'zh-CN': '请先完成目录部分。', 'zh-TW': '請先完成目錄部分。', es: 'Complete primero la sección Catálogo.' },
      beforeStart: function () { return goDetail(); },
      steps: [
        { target: '.mz-back-btn', position: 'right',
          title: { ko: '뒤로 가기', en: 'Back Button', ja: '戻るボタン', 'zh-CN': '返回按钮', 'zh-TW': '返回按鈕', es: 'Botón Atrás' },
          content: { ko: '이 버튼을 클릭하면 <strong>카탈로그 목록</strong>으로 돌아갑니다.', en: 'Click to return to the <strong>catalog list</strong>.', ja: 'クリックすると<strong>カタログリスト</strong>に戻ります。', 'zh-CN': '点击返回<strong>目录列表</strong>。', 'zh-TW': '點擊返回<strong>目錄列表</strong>。', es: 'Haga clic para volver a la <strong>lista del catálogo</strong>.' } },
        { target: '.mz-detail-title', position: 'bottom',
          title: { ko: '모델 이름', en: 'Model Name', ja: 'モデル名', 'zh-CN': '模型名称', 'zh-TW': '模型名稱', es: 'Nombre del modelo' },
          content: { ko: '선택된 모델의 <strong>이름</strong>이 큰 글씨로 표시됩니다.', en: 'The selected model\'s <strong>name</strong> is displayed prominently.', ja: '選択されたモデルの<strong>名前</strong>が大きく表示されます。', 'zh-CN': '所选模型的<strong>名称</strong>醒目显示。', 'zh-TW': '所選模型的<strong>名稱</strong>醒目顯示。', es: 'El <strong>nombre</strong> del modelo seleccionado se muestra de forma destacada.' } },
        // 안정적 ID 사용 (기존 nth-child(3) → #sectionUseCase)
        { target: '#sectionUseCase', position: 'bottom',
          title: { ko: '사용 사례', en: 'Use Case', ja: 'ユースケース', 'zh-CN': '使用场景', 'zh-TW': '使用案例', es: 'Caso de uso' },
          content: { ko: '모델의 <strong>용도와 설명</strong>이 한/영 양쪽으로 표시됩니다. 어떤 상황에서 이 모델을 사용하는지 확인하세요.', en: 'Model <strong>description and use cases</strong> in both Korean/English. Understand when to use this model.', ja: 'モデルの<strong>用途と説明</strong>が韓/英両方で表示されます。このモデルをどのような状況で使用するか確認してください。', 'zh-CN': '模型的<strong>描述和使用场景</strong>以韩语/英语双语显示。了解何时使用此模型。', 'zh-TW': '模型的<strong>描述和使用案例</strong>以韓語/英語雙語顯示。了解何時使用此模型。', es: 'La <strong>descripción y casos de uso</strong> del modelo en coreano/inglés. Comprenda cuándo usar este modelo.' } },
        // .mz-spec-table은 specification 필드가 없으면 생성되지 않음 — 가드 추가
        { target: '.mz-spec-table', position: 'top',
          title: { ko: '사양', en: 'Specifications', ja: '仕様', 'zh-CN': '规格', 'zh-TW': '規格', es: 'Especificaciones' },
          content: { ko: '<strong>해상도, FPS(Q-Lite/Q-Pro), 파라미터 수, 입력 크기</strong> 등의 기술 사양을 테이블로 확인합니다.', en: 'View technical specs in a table: <strong>resolution, FPS (Q-Lite/Q-Pro), parameter count, input size</strong>.', ja: 'テーブルで技術仕様を確認します：<strong>解像度、FPS（Q-Lite/Q-Pro）、パラメータ数、入力サイズ</strong>。', 'zh-CN': '以表格形式查看技术规格：<strong>分辨率、FPS（Q-Lite/Q-Pro）、参数数量、输入尺寸</strong>。', 'zh-TW': '以表格形式查看技術規格：<strong>解析度、FPS（Q-Lite/Q-Pro）、參數數量、輸入尺寸</strong>。', es: 'Vea especificaciones técnicas en una tabla: <strong>resolución, FPS (Q-Lite/Q-Pro), recuento de parámetros, tamaño de entrada</strong>.' },
          beforeStep: function () { scrollTo('#sectionSpec'); } },
        // 안정적 ID 사용 (기존 nth-child(6) → #sectionCompile)
        { target: '#sectionCompile', position: 'top',
          title: { ko: '컴파일 가이드', en: 'Compile Guide', ja: 'コンパイルガイド', 'zh-CN': '编译指南', 'zh-TW': '編譯指南', es: 'Guía de compilación' },
          content: { ko: '<strong>ONNX 다운로드 링크</strong>와 <strong>모델 그래프 보기 버튼</strong>이 있습니다. 모델의 연산 그래프는 dx-compiler 뷰어에서 열립니다.', en: 'Find <strong>ONNX download links</strong> and a <strong>View Model Graph button</strong>. The model\'s operator graph opens in the dx-compiler viewer.', ja: '<strong>ONNXダウンロードリンク</strong>と<strong>モデルグラフ表示ボタン</strong>があります。モデルの演算グラフは dx-compiler ビューアで開きます。', 'zh-CN': '此处有<strong>ONNX下载链接</strong>和<strong>查看模型图按钮</strong>。模型的算子图在 dx-compiler 查看器中打开。', 'zh-TW': '此處有<strong>ONNX下載連結</strong>和<strong>檢視模型圖按鈕</strong>。模型的運算子圖在 dx-compiler 檢視器中開啟。', es: 'Encuentre <strong>enlaces de descarga ONNX</strong> y un <strong>botón Ver grafo del modelo</strong>. El grafo de operadores se abre en el visor de dx-compiler.' },
          beforeStep: function () { scrollTo('#sectionCompile'); } },
        // 안정적 ID 사용 (기존 nth-child(8) → #sectionLegal)
        { target: '#sectionLegal', position: 'top',
          title: { ko: '법적 정보', en: 'Legal Info', ja: '法的情報', 'zh-CN': '法律信息', 'zh-TW': '法律資訊', es: 'Información legal' },
          content: { ko: '모델의 <strong>라이선스, 저작권, 원본 소스 링크</strong> 정보입니다. 상업적 사용 전 라이선스를 확인하세요.', en: 'Model <strong>license, copyright, and source links</strong>. Check the license before commercial use.', ja: 'モデルの<strong>ライセンス、著作権、ソースリンク</strong>情報です。商用利用前にライセンスを確認してください。', 'zh-CN': '模型的<strong>许可证、版权和来源链接</strong>信息。商业使用前请查看许可证。', 'zh-TW': '模型的<strong>授權、版權和來源連結</strong>資訊。商業使用前請查看授權。', es: '<strong>Licencia, derechos de autor y enlaces de origen</strong> del modelo. Revise la licencia antes del uso comercial.' },
          beforeStep: function () { scrollTo('#sectionLegal'); } },
        { target: '#sectionExample', position: 'top',
          title: { ko: '상세 페이지 완료', en: 'Detail Page Complete', ja: '詳細ページ完了', 'zh-CN': '详情页完成', 'zh-TW': '詳情頁完成', es: 'Página de detalle completada' },
          content: { ko: '모델 상세 페이지의 주요 섹션을 모두 살펴봤습니다. 다음으로 <strong>예제 이미지, 다운로드, 추론</strong> 섹션을 확인하세요.', en: 'You\'ve explored all major sections. Next, check <strong>examples, downloads, and inference</strong>.', ja: 'モデル詳細ページの主要セクションをすべて確認しました。次に<strong>サンプル画像、ダウンロード、推論</strong>セクションを確認してください。', 'zh-CN': '您已浏览所有主要部分。接下来请查看<strong>示例、下载和推理</strong>。', 'zh-TW': '您已瀏覽所有主要部分。接下來請查看<strong>範例、下載和推論</strong>。', es: 'Ha explorado todas las secciones principales. A continuación, revise <strong>ejemplos, descargas e inferencia</strong>.' },
          beforeStep: function () { scrollTo('#sectionExample'); } },
      ]
    },

    { id: 'examples', icon: '🖼️',
      title: { ko: '🖼️ 예제 이미지', en: '🖼️ Example Images', ja: '🖼️ サンプル画像', 'zh-CN': '🖼️ 示例图像', 'zh-TW': '🖼️ 範例影像', es: '🖼️ Imágenes de ejemplo' },
      description: { ko: '5가지 유형의 모델 예제 확인', en: 'View 5 types of model examples', ja: '5種類のモデルサンプルを確認', 'zh-CN': '查看5种模型示例类型', 'zh-TW': '查看5種模型範例類型', es: 'Vea 5 tipos de ejemplos de modelos' },
      prerequisite: 'detail',
      prerequisiteMessage: { ko: '먼저 모델 상세 섹션을 완료하세요.', en: 'Complete the Model Detail section first.', ja: '先にモデル詳細セクションを完了してください。', 'zh-CN': '请先完成模型详情部分。', 'zh-TW': '請先完成模型詳情部分。', es: 'Complete primero la sección Detalle del modelo.' },
      beforeStart: function () { return goDetail(); },
      steps: [
        // 안정적 ID 사용 (기존 nth-child(4) → #sectionExample)
        { target: '#sectionExample', position: 'bottom',
          title: { ko: '예제 섹션', en: 'Example Section', ja: 'サンプルセクション', 'zh-CN': '示例部分', 'zh-TW': '範例區段', es: 'Sección de ejemplos' },
          content: { ko: '모델 유형에 따라 예제 이미지가 <strong>5가지 표시 방식</strong> 중 하나로 렌더링됩니다: 비포/에프터, 오버레이, 분류 결과, 갤러리(유사도), 단일 이미지.', en: 'Depending on the model type, example images render in one of <strong>5 display styles</strong>: before/after, overlay, classification, gallery (similarity), single image.', ja: 'モデルの種類に応じて、サンプル画像は<strong>5種類の表示方式</strong>のいずれかでレンダリングされます：ビフォー/アフター、オーバーレイ、分類結果、ギャラリー（類似度）、単一画像。', 'zh-CN': '根据模型类型，示例图像以<strong>5种显示方式</strong>之一渲染：前后对比、叠加、分类结果、图库（相似度）、单张图像。', 'zh-TW': '根據模型類型，範例影像以<strong>5種顯示方式</strong>之一呈現：前後對比、疊加、分類結果、圖庫（相似度）、單張影像。', es: 'Según el tipo de modelo, las imágenes de ejemplo se muestran en uno de <strong>5 estilos de visualización</strong>: antes/después, superposición, clasificación, galería (similitud) e imagen única.' } },
        // .mz-ba-container는 before_after 타입 모델에서만 존재 → 튜토리얼 미리보기를 주입해 스팟라이트
        { target: '#dxt-mock-example', position: 'bottom',
          title: { ko: '비포/에프터 슬라이더', en: 'Before-After Slider', ja: 'ビフォー/アフター スライダー', 'zh-CN': '前后对比滑块', 'zh-TW': '前後對比滑桿', es: 'Control deslizante antes/después' },
          content: { ko: '<strong>before_after</strong> 타입 모델에서는 중앙 핸들을 드래그하여 원본과 추론 결과를 비교합니다. Detection, Segmentation 모델에서 주로 사용됩니다.', en: 'In <strong>before_after</strong> type models, drag the center handle to compare original and inference result. Used in Detection, Segmentation models.', ja: '<strong>before_after</strong>タイプのモデルでは、中央のハンドルをドラッグして元画像と推論結果を比較します。Detection、Segmentationモデルで主に使用されます。', 'zh-CN': '在<strong>before_after</strong>类型模型中，拖动中间滑块比较原图和推理结果。主要用于检测、分割模型。', 'zh-TW': '在<strong>before_after</strong>類型模型中，拖動中間滑桿比較原圖和推論結果。主要用於偵測、分割模型。', es: 'En modelos tipo <strong>before_after</strong>, arrastre el control central para comparar el original y el resultado de inferencia. Se usa en modelos Detection y Segmentation.' },
          beforeStep: function () { _mockExample('before_after'); } },
        // #overlayImg는 overlay 타입 모델에서만 존재 → 튜토리얼 미리보기를 주입해 스팟라이트
        { target: '#dxt-mock-example', position: 'bottom',
          title: { ko: '오버레이', en: 'Overlay', ja: 'オーバーレイ', 'zh-CN': '叠加', 'zh-TW': '疊加', es: 'Superposición' },
          content: { ko: '<strong>overlay</strong> 타입 모델에서는 슬라이더로 추론 결과의 투명도를 조절합니다. Segmentation, Depth 모델에서 사용됩니다.', en: 'In <strong>overlay</strong> type models, adjust inference result opacity with the slider. Used in Segmentation, Depth models.', ja: '<strong>overlay</strong>タイプのモデルでは、スライダーで推論結果の透明度を調整します。Segmentation、Depthモデルで使用されます。', 'zh-CN': '在<strong>overlay</strong>类型模型中，使用滑块调整推理结果的透明度。用于分割、深度模型。', 'zh-TW': '在<strong>overlay</strong>類型模型中，使用滑桿調整推論結果的透明度。用於分割、深度模型。', es: 'En modelos tipo <strong>overlay</strong>, ajuste la opacidad del resultado de inferencia con el control deslizante. Se usa en modelos Segmentation y Depth.' },
          beforeStep: function () { _mockExample('overlay'); } },
        // #classificationResults는 classified 타입 모델에서만 존재 → 튜토리얼 미리보기를 주입해 스팟라이트
        { target: '#dxt-mock-example', position: 'bottom',
          title: { ko: '분류 결과', en: 'Classification Result', ja: '分類結果', 'zh-CN': '分类结果', 'zh-TW': '分類結果', es: 'Resultado de clasificación' },
          content: { ko: '<strong>classified</strong> 타입 모델에서는 상위 N개의 분류 클래스와 확률이 바 차트로 표시됩니다. Classification 모델에서 사용됩니다.', en: 'In <strong>classified</strong> type models, top-N classes and probabilities are shown as a bar chart. Used in Classification models.', ja: '<strong>classified</strong>タイプのモデルでは、上位N個の分類クラスと確率がバーチャートで表示されます。Classificationモデルで使用されます。', 'zh-CN': '在<strong>classified</strong>类型模型中，前N个分类类别和概率以条形图显示。用于分类模型。', 'zh-TW': '在<strong>classified</strong>類型模型中，前N個分類類別和機率以長條圖顯示。用於分類模型。', es: 'En modelos tipo <strong>classified</strong>, las N clases principales y sus probabilidades se muestran como gráfico de barras. Se usa en modelos Classification.' },
          beforeStep: function () { _mockExample('classified'); } },
        { target: '#sectionExample', position: 'top',
          title: { ko: '예제 유형 안내', en: 'Example Types', ja: 'サンプルタイプ', 'zh-CN': '示例类型', 'zh-TW': '範例類型', es: 'Tipos de ejemplo' },
          content: { ko: '모델마다 다른 예제 유형이 표시됩니다: <strong>비포/에프터</strong>(Detection), <strong>오버레이</strong>(Segmentation/Depth), <strong>분류 바</strong>(Classification), <strong>갤러리</strong>(Re-ID/유사도), <strong>단일 이미지</strong>(기본). 현재 모델에 맞는 유형만 활성화됩니다.', en: 'Each model shows different example types: <strong>before/after</strong> (Detection), <strong>overlay</strong> (Segmentation/Depth), <strong>classification bars</strong> (Classification), <strong>gallery</strong> (Re-ID/similarity), <strong>single image</strong> (default). Only the type matching the current model is active.', ja: 'モデルごとに異なるサンプルタイプが表示されます：<strong>ビフォー/アフター</strong>（Detection）、<strong>オーバーレイ</strong>（Segmentation/Depth）、<strong>分類バー</strong>（Classification）、<strong>ギャラリー</strong>（Re-ID/類似度）、<strong>単一画像</strong>（デフォルト）。現在のモデルに該当するタイプのみ有効になります。', 'zh-CN': '每个模型显示不同的示例类型：<strong>前后对比</strong>（检测）、<strong>叠加</strong>（分割/深度）、<strong>分类条</strong>（分类）、<strong>图库</strong>（Re-ID/相似度）、<strong>单张图像</strong>（默认）。仅当前模型对应的类型处于激活状态。', 'zh-TW': '每個模型顯示不同的範例類型：<strong>前後對比</strong>（偵測）、<strong>疊加</strong>（分割/深度）、<strong>分類條</strong>（分類）、<strong>圖庫</strong>（Re-ID/相似度）、<strong>單張影像</strong>（預設）。僅目前模型對應的類型處於啟用狀態。', es: 'Cada modelo muestra distintos tipos de ejemplo: <strong>antes/después</strong> (Detection), <strong>superposición</strong> (Segmentation/Depth), <strong>barras de clasificación</strong> (Classification), <strong>galería</strong> (Re-ID/similitud), <strong>imagen única</strong> (predeterminado). Solo está activo el tipo que corresponde al modelo actual.' },
          beforeStep: function () { scrollTo('#sectionExample'); } },
      ]
    },

    { id: 'download', icon: '📥',
      title: { ko: '📥 모델 다운로드', en: '📥 Model Download', ja: '📥 モデルダウンロード', 'zh-CN': '📥 模型下载', 'zh-TW': '📥 模型下載', es: '📥 Descarga de modelos' },
      description: { ko: '모델 다운로드 프로세스 안내', en: 'Model download process guide', ja: 'モデルダウンロードプロセスガイド', 'zh-CN': '模型下载流程指南', 'zh-TW': '模型下載流程指南', es: 'Guía del proceso de descarga de modelos' },
      prerequisite: 'detail',
      prerequisiteMessage: { ko: '먼저 모델 상세 섹션을 완료하세요.', en: 'Complete the Model Detail section first.', ja: '先にモデル詳細セクションを完了してください。', 'zh-CN': '请先完成模型详情部分。', 'zh-TW': '請先完成模型詳情部分。', es: 'Complete primero la sección Detalle del modelo.' },
      beforeStart: function () { return goDetail(); },
      steps: [
        // Hero badges always render via renderDetail() — goDetail() waits for visible bbox
        { target: '#detailView .mz-detail-hero-badges .mz-download-badge', position: 'bottom',
          title: { ko: '다운로드 상태', en: 'Download Status', ja: 'ダウンロード状態', 'zh-CN': '下载状态', 'zh-TW': '下載狀態', es: 'Estado de descarga' },
          content: { ko: '✅ = 이미 다운로드됨, 📥 = 다운로드 가능. <strong>Q-Lite</strong>(경량)와 <strong>Q-Pro</strong>(고성능) 두 가지 버전이 있습니다.', en: '✅ = already downloaded, 📥 = available. Two versions: <strong>Q-Lite</strong> (lightweight) and <strong>Q-Pro</strong> (high-performance).', ja: '✅ = ダウンロード済み、📥 = ダウンロード可能。<strong>Q-Lite</strong>（軽量版）と<strong>Q-Pro</strong>（高性能版）の2つのバージョンがあります。', 'zh-CN': '✅ = 已下载，📥 = 可下载。两个版本：<strong>Q-Lite</strong>（轻量版）和<strong>Q-Pro</strong>（高性能版）。', 'zh-TW': '✅ = 已下載，📥 = 可下載。兩個版本：<strong>Q-Lite</strong>（輕量版）和<strong>Q-Pro</strong>（高效能版）。', es: '✅ = ya descargado, 📥 = disponible. Dos versiones: <strong>Q-Lite</strong> (ligera) y <strong>Q-Pro</strong> (alto rendimiento).' },
          beforeStep: function () { scrollTo('.mz-detail-header'); _scrollToDownloadBadge(); } },
        // 실제 다운로드 버튼은 data 속성 기반으로 렌더링된다.
        { target: '[data-model-id][data-quant]', position: 'bottom',
          title: { ko: '다운로드 버튼', en: 'Download Button', ja: 'ダウンロードボタン', 'zh-CN': '下载按钮', 'zh-TW': '下載按鈕', es: 'Botón de descarga' },
          content: { ko: 'Q-Lite 또는 Q-Pro 버전을 선택한 후 이 버튼을 클릭하면 <strong>다운로드가 시작</strong>됩니다. DX App이 연결된 상태에서만 표시됩니다.', en: 'Select Q-Lite or Q-Pro version, then click to <strong>start download</strong>. Only visible when DX App is connected.', ja: 'Q-LiteまたはQ-Proバージョンを選択し、クリックして<strong>ダウンロードを開始</strong>します。DX Appが接続されている場合のみ表示されます。', 'zh-CN': '选择Q-Lite或Q-Pro版本，然后点击<strong>开始下载</strong>。仅在DX App连接时显示。', 'zh-TW': '選擇Q-Lite或Q-Pro版本，然後點擊<strong>開始下載</strong>。僅在DX App連線時顯示。', es: 'Seleccione la versión Q-Lite o Q-Pro y haga clic para <strong>iniciar la descarga</strong>. Solo visible cuando DX App está conectada.' },
          beforeStep: function () { scrollTo('.mz-detail-header'); } },
        // 진행 상태는 다운로드 중에만 존재 → 튜토리얼 미리보기(진행바)를 주입해 스팟라이트
        { target: '#dxt-mock-dl', position: 'bottom',
          title: { ko: '진행률', en: 'Progress', ja: '進捗', 'zh-CN': '进度', 'zh-TW': '進度', es: 'Progreso' },
          content: { ko: '다운로드 중에는 <strong>진행바와 퍼센트</strong>가 표시됩니다. 취소 버튼으로 언제든 중단할 수 있습니다.', en: 'During download, a <strong>progress bar and percentage</strong> appear. Cancel anytime with the cancel button.', ja: 'ダウンロード中は<strong>プログレスバーとパーセント</strong>が表示されます。キャンセルボタンでいつでも中断できます。', 'zh-CN': '下载过程中会显示<strong>进度条和百分比</strong>。随时可以点击取消按钮中断。', 'zh-TW': '下載過程中會顯示<strong>進度條和百分比</strong>。隨時可以點擊取消按鈕中斷。', es: 'Durante la descarga, aparecen una <strong>barra de progreso y un porcentaje</strong>. Puede cancelar en cualquier momento con el botón Cancelar.' },
          beforeStep: function () { _mockDownload('progress'); } },
        // 실제 상단 바의 DX App 상태 표시등을 스팟라이트
        { target: '#dxAppStatus', position: 'bottom',
          title: { ko: 'DX App 필요', en: 'DX App Required', ja: 'DX App 必要', 'zh-CN': '需要DX App', 'zh-TW': '需要DX App', es: 'DX App requerida' },
          content: { ko: '모델 다운로드에는 <strong>DX App이 실행 중</strong>이어야 합니다. 상단 바의 DX App 상태가 🟢인지 확인하세요.', en: '<strong>DX App must be running</strong> for downloads. Check the DX App status indicator (🟢) in the top bar.', ja: 'モデルのダウンロードには<strong>DX Appが実行中</strong>である必要があります。トップバーのDX App状態が🟢であることを確認してください。', 'zh-CN': '模型下载需要<strong>DX App正在运行</strong>。请检查顶部栏的DX App状态指示器（🟢）。', 'zh-TW': '模型下載需要<strong>DX App正在執行</strong>。請檢查頂部列的DX App狀態指示器（🟢）。', es: '<strong>DX App debe estar en ejecución</strong> para descargar. Compruebe el indicador de estado de DX App (🟢) en la barra superior.' } },
        // 완료 배지는 다운로드 완료 후에만 존재 → 튜토리얼 미리보기(✅ 배지)를 주입해 스팟라이트
        { target: '#dxt-mock-dl', position: 'bottom',
          title: { ko: '다운로드 완료', en: 'Download Complete', ja: 'ダウンロード完了', 'zh-CN': '下载完成', 'zh-TW': '下載完成', es: 'Descarga completada' },
          content: { ko: '다운로드 완료 시 ✅ 배지로 변경됩니다. 실패하면 에러 메시지가 표시되며 재시도할 수 있습니다.', en: 'Badge changes to ✅ on completion. On failure, an error message appears and you can retry.', ja: '完了するとバッジが✅に変わります。失敗した場合はエラーメッセージが表示され、再試行できます。', 'zh-CN': '完成后标记变为✅。失败时会显示错误消息，可以重试。', 'zh-TW': '完成後標記變為✅。失敗時會顯示錯誤訊息，可以重試。', es: 'Al completarse, la insignia cambia a ✅. Si falla, aparece un mensaje de error y puede reintentar.' },
          beforeStep: function () { _mockDownload('complete'); } },
        // ONNX 모델 링크 — onnx_url이 있는 모델에서만 존재
        { target: '#btnOnnxLink', position: 'bottom',
          title: { ko: 'ONNX 모델 링크', en: 'ONNX Model Link', ja: 'ONNXモデルリンク', 'zh-CN': 'ONNX模型链接', 'zh-TW': 'ONNX模型連結', es: 'Enlace de modelo ONNX' },
          content: { ko: '<strong>ONNX 원본 모델</strong>을 다운로드할 수 있는 링크입니다. NPU 컴파일 전 원본 모델이 필요할 때 사용하세요.', en: 'Link to download the <strong>original ONNX model</strong>. Use when you need the source model before NPU compilation.', ja: '<strong>ONNX元モデル</strong>をダウンロードできるリンクです。NPUコンパイル前にソースモデルが必要な場合に使用してください。', 'zh-CN': '下载<strong>原始ONNX模型</strong>的链接。在NPU编译前需要源模型时使用。', 'zh-TW': '下載<strong>原始ONNX模型</strong>的連結。在NPU編譯前需要來源模型時使用。', es: 'Enlace para descargar el <strong>modelo ONNX original</strong>. Úselo cuando necesite el modelo fuente antes de la compilación para NPU.' },
          beforeStep: function () { scrollTo('#sectionCompile'); } },
        // 모델 그래프 보기 버튼 — 항상 존재
        { target: '#btnDxtronCompiler', position: 'bottom',
          title: { ko: '모델 그래프 보기', en: 'View Model Graph', ja: 'モデルグラフを表示', 'zh-CN': '查看模型图', 'zh-TW': '檢視模型圖', es: 'Ver grafo del modelo' },
          content: { ko: '<strong>모델 그래프</strong>를 dx-compiler 그래프 뷰어에서 새 탭으로 엽니다. ONNX 모델의 연산 그래프를 확인할 수 있습니다.', en: 'Opens the <strong>model graph</strong> in the dx-compiler graph viewer in a new tab. Inspect the ONNX model\'s operator graph.', ja: '<strong>モデルグラフ</strong>を dx-compiler グラフビューアで新しいタブで開きます。ONNXモデルの演算グラフを確認できます。', 'zh-CN': '在新标签页的 dx-compiler 图形查看器中打开<strong>模型图形</strong>。可查看 ONNX 模型的算子图。', 'zh-TW': '在新分頁的 dx-compiler 圖形檢視器中開啟<strong>模型圖形</strong>。可檢視 ONNX 模型的運算子圖。', es: 'Abre el <strong>grafo del modelo</strong> en el visor de grafos de dx-compiler en una pestaña nueva. Inspeccione el grafo de operadores del modelo ONNX.' },
          beforeStep: function () { scrollTo('#sectionCompile'); } },
      ]
    },

    { id: 'inference', icon: '🔬',
      title: { ko: '🔬 라이브 추론', en: '🔬 Live Inference', ja: '🔬 ライブ推論', 'zh-CN': '🔬 实时推理', 'zh-TW': '🔬 即時推論', es: '🔬 Inferencia en vivo' },
      description: { ko: '데모 코드 확인 및 추론 실행', en: 'View demo code and run inference', ja: 'デモコードの確認と推論の実行', 'zh-CN': '查看演示代码并运行推理', 'zh-TW': '查看示範程式碼並執行推論', es: 'Vea el código de demostración y ejecute inferencia' },
      prerequisite: 'detail',
      prerequisiteMessage: { ko: '먼저 모델 상세 섹션을 완료하세요.', en: 'Complete the Model Detail section first.', ja: '先にモデル詳細セクションを完了してください。', 'zh-CN': '请先完成模型详情部分。', 'zh-TW': '請先完成模型詳情部分。', es: 'Complete primero la sección Detalle del modelo.' },
      beforeStart: function () { return goDetail(); },
      steps: [
        { target: '#demoSection', position: 'bottom',
          title: { ko: '데모 코드', en: 'Demo Code', ja: 'デモコード', 'zh-CN': '演示代码', 'zh-TW': '示範程式碼', es: 'Código de demostración' },
          content: { ko: '<strong>C++, Python, CLI</strong> 3가지 언어의 예제 코드를 제공합니다. 탭을 전환하여 각 언어별 사용법을 확인하세요.', en: 'Provides example code in <strong>C++, Python, CLI</strong>. Switch tabs to see usage for each language.', ja: '<strong>C++、Python、CLI</strong>の3言語のサンプルコードを提供します。タブを切り替えて各言語の使用方法を確認してください。', 'zh-CN': '提供<strong>C++、Python、CLI</strong>三种语言的示例代码。切换标签查看各语言的用法。', 'zh-TW': '提供<strong>C++、Python、CLI</strong>三種語言的範例程式碼。切換標籤查看各語言的用法。', es: 'Proporciona código de ejemplo en <strong>C++, Python, CLI</strong>. Cambie de pestaña para ver el uso de cada idioma.' },
          beforeStep: function () { scrollTo('#demoSection'); } },
        // .mz-code-tabs는 비동기 loadDemoCode() API 완료 후 생성 — pollFor 5초 대기
        { target: '.mz-code-tabs', position: 'bottom',
          title: { ko: '코드 탭', en: 'Code Tabs', ja: 'コードタブ', 'zh-CN': '代码标签', 'zh-TW': '程式碼標籤', es: 'Pestañas de código' },
          content: { ko: '각 탭을 클릭하면 해당 <strong>언어별 예제 코드</strong>가 표시됩니다. 코드는 모델에 맞게 자동 생성됩니다.', en: 'Click each tab to view <strong>language-specific example code</strong>. Code is auto-generated for the selected model.', ja: '各タブをクリックすると該当<strong>言語別サンプルコード</strong>が表示されます。コードはモデルに合わせて自動生成されます。', 'zh-CN': '点击每个标签查看<strong>特定语言的示例代码</strong>。代码根据所选模型自动生成。', 'zh-TW': '點擊每個標籤查看<strong>特定語言的範例程式碼</strong>。程式碼根據所選模型自動產生。', es: 'Haga clic en cada pestaña para ver <strong>código de ejemplo específico del idioma</strong>. El código se genera automáticamente para el modelo seleccionado.' },
          beforeStep: function () { pollFor('.mz-code-tabs', 50); } },
        { target: '.mz-code-tab', position: 'bottom',
          title: { ko: '개별 코드 탭', en: 'Individual Code Tab', ja: '個別コードタブ', 'zh-CN': '单独代码标签', 'zh-TW': '個別程式碼標籤', es: 'Pestaña de código individual' },
          content: { ko: '<strong>C++, Python, CLI</strong> 중 원하는 언어의 탭을 클릭하세요. 선택한 탭의 예제 코드만 표시됩니다.', en: 'Click a <strong>C++, Python, or CLI</strong> tab. Only the selected language\'s example code is shown.', ja: '<strong>C++、Python、CLI</strong>の中から希望する言語のタブをクリックしてください。選択したタブのサンプルコードのみ表示されます。', 'zh-CN': '点击<strong>C++、Python或CLI</strong>标签。仅显示所选语言的示例代码。', 'zh-TW': '點擊<strong>C++、Python或CLI</strong>標籤。僅顯示所選語言的範例程式碼。', es: 'Haga clic en una pestaña de <strong>C++, Python o CLI</strong>. Solo se muestra el código de ejemplo del idioma seleccionado.' },
          beforeStep: function () { pollFor('.mz-code-tab', 50); } },
        // position: top — 코드 블록 안쪽(left)이 아닌 위쪽에 표시
        { target: '.mz-code-copy', position: 'top',
          title: { ko: '코드 복사', en: 'Copy Code', ja: 'コードコピー', 'zh-CN': '复制代码', 'zh-TW': '複製程式碼', es: 'Copiar código' },
          content: { ko: '📋 버튼을 클릭하면 현재 표시된 코드가 <strong>클립보드에 복사</strong>됩니다.', en: 'Click 📋 to <strong>copy the displayed code to clipboard</strong>.', ja: '📋ボタンをクリックすると現在表示されているコードが<strong>クリップボードにコピー</strong>されます。', 'zh-CN': '点击📋将显示的代码<strong>复制到剪贴板</strong>。', 'zh-TW': '點擊📋將顯示的程式碼<strong>複製到剪貼簿</strong>。', es: 'Haga clic en 📋 para <strong>copiar el código mostrado al portapapeles</strong>.' },
          beforeStep: function () { pollFor('.mz-code-copy', 50); } },
        // 안정적 ID 사용 (기존 nth-child(4) details summary → #sectionExample details summary)
        { target: '#sectionExample details summary', position: 'bottom',
          title: { ko: '추론 패널', en: 'Inference Panel', ja: '推論パネル', 'zh-CN': '推理面板', 'zh-TW': '推論面板', es: 'Panel de inferencia' },
          content: { ko: '이 <strong>summary</strong>를 클릭하면 추론 실행 패널이 펼쳐집니다. 이미지를 업로드하거나 기본 이미지로 추론을 실행할 수 있습니다.', en: 'Click this <strong>summary</strong> to expand the inference panel. Upload an image or use default images to run inference.', ja: 'この<strong>summary</strong>をクリックすると推論実行パネルが展開されます。画像をアップロードするかデフォルト画像で推論を実行できます。', 'zh-CN': '点击此<strong>摘要</strong>展开推理面板。上传图像或使用默认图像运行推理。', 'zh-TW': '點擊此<strong>摘要</strong>展開推論面板。上傳影像或使用預設影像執行推論。', es: 'Haga clic en este <strong>summary</strong> para expandir el panel de inferencia. Suba una imagen o use imágenes predeterminadas para ejecutar inferencia.' },
          beforeStep: function () { scrollTo('#sectionExample details summary'); } },
        { target: '#inferencePanel', position: 'top',
          title: { ko: '추론 실행', en: 'Run Inference', ja: '推論実行', 'zh-CN': '运行推理', 'zh-TW': '執行推論', es: 'Ejecutar inferencia' },
          content: { ko: '이미지를 업로드하거나 기본 이미지를 선택한 후 <strong>실행 버튼</strong>을 클릭합니다. NPU에서 실시간 추론이 수행됩니다.', en: 'Upload an image or select a default, then click <strong>Run</strong>. Real-time inference runs on the NPU.', ja: '画像をアップロードするかデフォルトを選択し、<strong>実行ボタン</strong>をクリックします。NPUでリアルタイム推論が実行されます。', 'zh-CN': '上传图像或选择默认图像，然后点击<strong>运行</strong>。在NPU上执行实时推理。', 'zh-TW': '上傳影像或選擇預設影像，然後點擊<strong>執行</strong>。在NPU上執行即時推論。', es: 'Suba una imagen o seleccione una predeterminada y haga clic en <strong>Run</strong>. La inferencia en tiempo real se ejecuta en la NPU.' },
          beforeStep: function () {
            var d = document.querySelector('#inferencePanel');
            if (d) { var det = d.closest('details'); if (det) det.open = true; }
          } },
        { target: '#inferenceUploadTrigger', position: 'bottom',
          title: { ko: '이미지 업로드', en: 'Upload Image', ja: '画像アップロード', 'zh-CN': '上传图像', 'zh-TW': '上傳影像', es: 'Subir imagen' },
          content: { ko: '<strong>📁 Upload Image</strong> 버튼을 클릭하여 추론할 이미지를 선택합니다. JPG, PNG 등 이미지 파일을 지원합니다.', en: 'Click <strong>📁 Upload Image</strong> to select an image for inference. Supports JPG, PNG, and other image formats.', ja: '<strong>📁 Upload Image</strong>ボタンをクリックして推論する画像を選択します。JPG、PNGなどの画像ファイルに対応しています。', 'zh-CN': '点击<strong>📁 Upload Image</strong>选择推理图像。支持JPG、PNG等图像格式。', 'zh-TW': '點擊<strong>📁 Upload Image</strong>選擇推論影像。支援JPG、PNG等影像格式。', es: 'Haga clic en <strong>📁 Upload Image</strong> para seleccionar una imagen para inferencia. Admite JPG, PNG y otros formatos de imagen.' },
          beforeStep: function () {
            var d = document.querySelector('#inferencePanel');
            if (d) { var det = d.closest('details'); if (det) det.open = true; }
            pollFor('#inferenceUploadTrigger', 30);
          } },
        { target: '#btnRunDefault', position: 'bottom',
          title: { ko: '기본 이미지 실행', en: 'Use Default Image', ja: 'デフォルト画像使用', 'zh-CN': '使用默认图像', 'zh-TW': '使用預設影像', es: 'Usar imagen predeterminada' },
          content: { ko: '<strong>▶ Use Default</strong> 버튼을 클릭하면 모델에 포함된 <strong>기본 샘플 이미지</strong>로 즉시 추론을 실행합니다.', en: 'Click <strong>▶ Use Default</strong> to instantly run inference with the model\'s <strong>built-in sample image</strong>.', ja: '<strong>▶ Use Default</strong>ボタンをクリックすると、モデルに含まれる<strong>デフォルトサンプル画像</strong>で即座に推論を実行します。', 'zh-CN': '点击<strong>▶ Use Default</strong>使用模型的<strong>内置样本图像</strong>立即运行推理。', 'zh-TW': '點擊<strong>▶ Use Default</strong>使用模型的<strong>內建範例影像</strong>立即執行推論。', es: 'Haga clic en <strong>▶ Use Default</strong> para ejecutar inferencia al instante con la <strong>imagen de muestra integrada</strong> del modelo.' },
          beforeStep: function () {
            var d = document.querySelector('#inferencePanel');
            if (d) { var det = d.closest('details'); if (det) det.open = true; }
            pollFor('#btnRunDefault', 30);
          } },
        // 추론 결과는 실행 후에만 존재 → 튜토리얼 미리보기(결과+통계)를 주입해 스팟라이트
        { target: '#dxt-mock-inf', position: 'top',
          title: { ko: '추론 결과', en: 'Inference Results', ja: '推論結果', 'zh-CN': '推理结果', 'zh-TW': '推論結果', es: 'Resultados de inferencia' },
          content: { ko: '추론 완료 후 <strong>FPS, Latency, 감지 태그</strong> 등의 결과가 표시됩니다. 결과 이미지에 바운딩 박스나 분할 마스크가 오버레이됩니다.', en: 'After inference, <strong>FPS, latency, detection tags</strong> appear. Result image shows bounding boxes or segmentation masks.', ja: '推論完了後、<strong>FPS、レイテンシ、検出タグ</strong>などの結果が表示されます。結果画像にバウンディングボックスやセグメンテーションマスクがオーバーレイされます。', 'zh-CN': '推理完成后显示<strong>FPS、延迟、检测标签</strong>等结果。结果图像上显示边界框或分割掩码。', 'zh-TW': '推論完成後顯示<strong>FPS、延遲、偵測標籤</strong>等結果。結果影像上顯示邊界框或分割遮罩。', es: 'Tras la inferencia, aparecen <strong>FPS, latencia y etiquetas de detección</strong>. La imagen de resultado muestra cuadros delimitadores o máscaras de segmentación.' },
          beforeStep: function () { _mockInference(); } },
      ]
    },

  ];

  // Clear any injected #dxt-mock-* preview when leaving a step (advance / prev /
  // stop / section jump). The next step's beforeStep re-injects what it needs,
  // so only the current step's mock is ever present.
  (function () {
    ['examples', 'download', 'inference'].forEach(function (secId) {
      var sec = sections.find(function (s) { return s.id === secId; });
      if (!sec) return;
      sec.steps.forEach(function (st) {
        var prev = st.afterStep;
        st.afterStep = function () { if (prev) prev(); _clearMocks(); };
      });
    });
  })();

  window.DXTutorial.create({
    appId: 'modelzoo',
    sections: sections,
    toolbarSelector: '#dxToolbar',
    skipButtons: true,
    getLang: function () { return localStorage.getItem('dx-lang') || 'en'; },
    onNav: function (page) {
      if (page === 'catalog') location.hash = '';
    }
  });
})();
