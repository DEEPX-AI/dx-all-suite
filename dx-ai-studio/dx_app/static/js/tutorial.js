/* ═══════════════════════════════════════════════════════════════
   DX App — Tutorial Definitions v2.1 (Audit Fix)
   12 sections, ~115 steps — 6-language (ko/en/ja/zh-CN/zh-TW/es)
   Removed: dashboard, community, planner (separate apps)
   Fixed: chat widget selectors (class-based)
   Added: r-topk, r-alpha, export controls, compiler options,
          notification drawer
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  function goPage(p) { if (typeof nav === 'function') nav(p); }

  function _prepRunSingleTab() {
    goPage('run');
    if (typeof toggleRunTab === 'function') toggleRunTab('single');
  }

  function _mockToast() {
    var wrap = document.getElementById('toast-wrap');
    if (!wrap) return;
    wrap.innerHTML = '';
    var el = document.createElement('div');
    el.id = 'dxt-mock-toast';
    el.className = 'toast toast-ok show';
    el.textContent = 'Tutorial preview';
    wrap.appendChild(el);
  }

  function _dismissMockToast() {
    var wrap = document.getElementById('toast-wrap');
    if (wrap) wrap.innerHTML = '';
  }

  function _closeNotifDrawer() {
    var drawer = document.getElementById('notif-drawer');
    if (drawer && drawer.classList.contains('open') && typeof toggleNotifDrawer === 'function') {
      toggleNotifDrawer();
    }
  }

  function _prepRunExportArea() {
    _prepRunSingleTab();
    // Return a promise the engine awaits (see _showStep): the export card lives
    // well below the fold, so we scroll it into view ONCE and wait for the
    // smooth-scroll to settle before the spotlight is measured. Without this the
    // engine placed the box mid-scroll on empty space (the "points at nothing"
    // flash). One anchor (the card) keeps all three export steps consistent.
    return new Promise(function (resolve) {
      setTimeout(function () {
        var card = document.getElementById('run-export-card');
        if (card) card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(resolve, 500);
      }, 100);
    });
  }

  function _mockLightbox() {
    var dlg = document.getElementById('gallery-lightbox');
    if (!dlg) return;
    var body = document.getElementById('lb-body');
    if (body && !body.children.length) {
      var img = document.createElement('img');
      img.src = 'data:image/svg+xml,' + encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180"><rect width="100%" height="100%" fill="#1a2332"/><text x="50%" y="50%" fill="#8b949e" font-size="14" text-anchor="middle" dy=".3em">Tutorial preview</text></svg>'
      );
      img.alt = 'Tutorial preview';
      img.style.maxWidth = '100%';
      body.appendChild(img);
    }
    var title = document.getElementById('lb-title');
    if (title) title.textContent = 'sample_output.jpg';
    dlg.classList.add('dxt-tutorial-dialog');
    if (dlg.open && typeof dlg.close === 'function') dlg.close();
    if (typeof dlg.show === 'function') dlg.show();
    else if (!dlg.open) dlg.setAttribute('open', '');
  }

  function _closeLightbox() {
    var dlg = document.getElementById('gallery-lightbox');
    if (dlg) {
      dlg.classList.remove('dxt-tutorial-dialog');
      if (dlg.open && typeof dlg.close === 'function') dlg.close();
    }
    if (typeof closeLightbox === 'function') closeLightbox();
  }

  function _closeChatWindow() {
    // The chat tour opens the assistant via the FAB; close it on exit so it isn't left
    // floating open after the tour (toggles the FAB only if the window is currently open).
    if (document.querySelector('.dx-chat-window.open')) {
      var fab = document.querySelector('.dx-chat-fab');
      if (fab) fab.click();
    }
  }

  function _scrollToTarget(selector) {
    var el = document.querySelector(selector);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function _mockModelzooCartFallback() {
    var cart = document.getElementById('mz-cart');
    if (!cart) return;
    cart.style.display = '';
    cart.innerHTML = '<div class="mz-cart-summary">'
      + '<div class="mz-cart-left"><span class="mz-cart-icon">🛒</span> <strong>2</strong> models · <span class="txt-dim">4 files</span></div>'
      + '<div class="mz-cart-right"><button class="btn btn-acc btn-sm" type="button">📥 Download All (4)</button></div>'
      + '</div>';
  }

  function _prepModelzooCartDemo() {
    goPage('modelzoo');
    var cart = document.getElementById('mz-cart');
    if (!cart) return;
    if (window.MZ && typeof mzRenderCart === 'function' && MZ.models && MZ.models.length >= 2) {
      MZ.cart = {};
      MZ.cart[MZ.models[0].name] = { qlite: true, qpro: false };
      MZ.cart[MZ.models[1].name] = { qlite: false, qpro: true };
      mzRenderCart();
    } else {
      _mockModelzooCartFallback();
    }
    cart.classList.add('dxt-tutorial-pin');
    setTimeout(function () {
      cart.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }, 300);
  }

  function _clearModelzooCartDemo() {
    var cart = document.getElementById('mz-cart');
    if (cart) cart.classList.remove('dxt-tutorial-pin');
  }

  function _orderGlobalFirst(list) {
    var idx = list.findIndex(function (s) { return s.id === 'global'; });
    if (idx > 0) {
      var globalSec = list.splice(idx, 1)[0];
      list.unshift(globalSec);
    }
    return list;
  }

  function _showSegParams() {
    var sel = document.getElementById('r-cat');
    if (sel) {
      sel.value = 'segmentation';
      sel.dispatchEvent(new Event('change'));
    }
    var row = document.getElementById('r-params-seg');
    if (row) row.classList.remove('hidden');
  }

  // Confidence + NMS live in #r-params-detect, which updateRunParams() hides
  // unless the category is a detection task. Force a detection category so the
  // #r-conf / #r-nms spotlights have a visible target.
  function _showDetectParams() {
    var sel = document.getElementById('r-cat');
    if (sel) {
      sel.value = 'object_detection';
      sel.dispatchEvent(new Event('change'));
      if (typeof onRCat === 'function') onRCat();
    }
    var row = document.getElementById('r-params-detect');
    if (row) row.classList.remove('hidden');
  }

  /* ════════════════════════════════════════════════════════════
     SECTIONS
     ════════════════════════════════════════════════════════════ */
  var sections = [

    { id:'setup', icon:'⚙️',
      title:{ ko: '⚙️ Setup & Install', en: '⚙️ Setup & Install', ja: '⚙️ セットアップ & インストール', 'zh-CN': '⚙️ 设置与安装', 'zh-TW': '⚙️ 設定與安裝', es: '⚙️ Configuración e instalación' },
      description:{ ko: '의존성 설치부터 NPU 드라이버까지 5단계 설치 과정 (DX-COM은 Launcher Compiler 모듈)', en: '5-step installation through NPU driver (DX-COM lives in the Launcher Compiler module)', ja: '依存関係からNPUドライバまでの5ステップ（DX-COMはLauncher Compilerモジュール）', 'zh-CN': '从依赖项到NPU驱动的5步安装（DX-COM在 Launcher Compiler 模块）', 'zh-TW': '從依賴項到NPU驅動的5步安裝（DX-COM在 Launcher Compiler 模組）', es: 'Instalación en 5 pasos hasta el controlador NPU (DX-COM está en el módulo Compiler del Launcher)' },
      beforeStart:function(){ goPage('setup'); },
      steps:[
        { target:'#page-setup h1', position:'bottom',
          title:{ ko: 'Setup & Install 페이지', en: 'Setup & Install Page', ja: 'セットアップ & インストール ページ', 'zh-CN': '设置与安装页面', 'zh-TW': '設定與安裝頁面', es: 'Página de configuración e instalación' },
          content:{ ko: '이 페이지에서 시스템 의존성 설치, 빌드, 샘플 데이터 다운로드를 <strong>위→아래, 왼→오른쪽</strong> 순서대로 진행합니다. 각 카드의 <strong>Install/Build</strong> 버튼을 클릭하면 백그라운드에서 실행됩니다.', en: 'Run dependency installation, builds, and sample downloads <strong>top-to-bottom, left-to-right</strong>. Click <strong>Install/Build</strong> on each card to run in background.', ja: '依存関係のインストール、ビルド、サンプルのダウンロードを<strong>上から下、左から右</strong>の順に実行します。各カードの<strong>Install/Build</strong>をクリックするとバックグラウンドで実行されます。', 'zh-CN': '按<strong>从上到下、从左到右</strong>的顺序执行依赖项安装、构建和示例下载。点击各卡片上的<strong>Install/Build</strong>按钮在后台运行。', 'zh-TW': '按<strong>由上至下、由左至右</strong>的順序執行依賴項安裝、建置和範例下載。點擊各卡片上的<strong>Install/Build</strong>按鈕在背景執行。', es: 'Ejecute la instalación de dependencias, compilaciones y descargas de muestras <strong>de arriba abajo y de izquierda a derecha</strong>. Haga clic en <strong>Instalar/Compilar</strong> en cada tarjeta para ejecutar en segundo plano.' } },
        { target:'.setup-grid .setup-card:nth-child(1)', position:'bottom',
          title:{ ko: '① DX-APP 의존성 설치', en: '① DX-APP Dependencies', ja: '① DX-APP 依存関係', 'zh-CN': '① DX-APP 依赖项', 'zh-TW': '① DX-APP 依賴項', es: '① Dependencias de DX-APP' },
          content:{ ko: 'cmake, gcc, ninja, OpenCV 등 C++ 빌드에 필요한 시스템 패키지를 설치합니다. <strong>Install</strong> 클릭 → 하단 로그 영역에서 실시간 진행 확인. 완료 시 상단에 <strong>✅</strong> 배지가 표시됩니다.', en: 'Installs system packages for C++ build (cmake, gcc, ninja, OpenCV). Click <strong>Install</strong> → check real-time progress in log area. Shows <strong>✅</strong> badge when done.', ja: 'C++ビルドに必要なシステムパッケージ（cmake, gcc, ninja, OpenCV）をインストールします。<strong>Install</strong>をクリック → ログエリアでリアルタイム進捗を確認。完了時に<strong>✅</strong>バッジが表示されます。', 'zh-CN': '安装C++构建所需的系统包（cmake、gcc、ninja、OpenCV）。点击<strong>Install</strong> → 在日志区域查看实时进度。完成后显示<strong>✅</strong>标记。', 'zh-TW': '安裝C++建置所需的系統套件（cmake、gcc、ninja、OpenCV）。點擊<strong>Install</strong> → 在日誌區域查看即時進度。完成後顯示<strong>✅</strong>標記。', es: 'Instala paquetes del sistema para la compilación en C++ (cmake, gcc, ninja, OpenCV). Haga clic en <strong>Instalar</strong> → consulte el progreso en tiempo real en el área de registro. Muestra la insignia <strong>✅</strong> al finalizar.' } },
        { target:'.setup-grid .setup-card:nth-child(2)', position:'bottom',
          title:{ ko: '② DX-APP 빌드', en: '② DX-APP Build', ja: '② DX-APP ビルド', 'zh-CN': '② DX-APP 构建', 'zh-TW': '② DX-APP 建置', es: '② Compilación de DX-APP' },
          content:{ ko: 'C++ 데모 바이너리를 cmake Release 모드로 컴파일합니다. ①번이 완료된 후 진행하세요. 빌드 시간은 약 2~5분 소요됩니다.', en: 'Compiles C++ demo binaries with cmake Release mode. Run after step ① is complete. Build takes about 2-5 minutes.', ja: 'cmake Releaseモードで C++ デモバイナリをコンパイルします。ステップ①完了後に実行してください。ビルド時間は約2〜5分です。', 'zh-CN': '使用cmake Release模式编译C++演示程序。请在步骤①完成后执行。构建约需2-5分钟。', 'zh-TW': '使用cmake Release模式編譯C++範例程式。請在步驟①完成後執行。建置約需2-5分鐘。', es: 'Compila binarios de demostración en C++ con cmake en modo Release. Ejecútelo después de completar el paso ①. La compilación tarda aproximadamente de 2 a 5 minutos.' } },
        { target:'.setup-grid .setup-card:nth-child(3)', position:'bottom',
          title:{ ko: '③ 샘플 에셋 다운로드', en: '③ Sample Assets', ja: '③ サンプルアセット', 'zh-CN': '③ 示例资源', 'zh-TW': '③ 範例資源', es: '③ Recursos de muestra' },
          content:{ ko: 'AI 추론에 사용할 사전 컴파일된 샘플 모델(.dxnn)과 데모 비디오를 다운로드합니다. Run Inference, Benchmark에서 사용됩니다.', en: 'Downloads pre-compiled sample models (.dxnn) and demo videos for Run Inference and Benchmark.', ja: 'Run InferenceとBenchmarkで使用する事前コンパイル済みサンプルモデル（.dxnn）とデモビデオをダウンロードします。', 'zh-CN': '下载用于推理和基准测试的预编译示例模型（.dxnn）和演示视频。', 'zh-TW': '下載用於推論和基準測試的預編譯範例模型（.dxnn）和示範影片。', es: 'Descarga modelos de muestra precompilados (.dxnn) y videos de demostración para Run Inference y Benchmark.' } },
        { target:'.setup-grid .setup-card:nth-child(4)', position:'bottom',
          title:{ ko: '④ DX-Runtime 의존성', en: '④ DX-Runtime Dependencies', ja: '④ DX-Runtime 依存関係', 'zh-CN': '④ DX-Runtime 依赖项', 'zh-TW': '④ DX-Runtime 依賴項', es: '④ Dependencias de DX-Runtime' },
          content:{ ko: 'NPU 런타임에 필요한 cmake, ONNX Runtime 등의 패키지를 설치합니다.', en: 'Installs packages required for NPU runtime (cmake, ONNX Runtime, etc.).', ja: 'NPUランタイムに必要なパッケージ（cmake, ONNX Runtime等）をインストールします。', 'zh-CN': '安装NPU运行时所需的软件包（cmake、ONNX Runtime等）。', 'zh-TW': '安裝NPU執行環境所需的套件（cmake、ONNX Runtime等）。', es: 'Instala paquetes necesarios para el runtime de NPU (cmake, ONNX Runtime, etc.).' } },
        { target:'.setup-grid .setup-card:nth-child(5)', position:'bottom',
          title:{ ko: '⑤ NPU Linux Driver', en: '⑤ NPU Linux Driver', ja: '⑤ NPU Linux ドライバ', 'zh-CN': '⑤ NPU Linux 驱动', 'zh-TW': '⑤ NPU Linux 驅動', es: '⑤ Controlador Linux de NPU' },
          content:{ ko: 'DeepX NPU 하드웨어 드라이버를 설치합니다. <strong>sudo 비밀번호</strong>가 필요하며, 하단의 <strong>⌨️ Manual Input</strong> 버튼으로 stdin 입력 필드를 열어 비밀번호를 입력하세요.', en: 'Installs the DeepX NPU hardware driver. Requires <strong>sudo password</strong> — click <strong>⌨️ Manual Input</strong> below to open the stdin field.', ja: 'DeepX NPUハードウェアドライバをインストールします。<strong>sudo パスワード</strong>が必要です — 下部の<strong>⌨️ Manual Input</strong>をクリックしてstdin入力フィールドを開いてください。', 'zh-CN': '安装DeepX NPU硬件驱动程序。需要<strong>sudo密码</strong> — 点击下方的<strong>⌨️ Manual Input</strong>打开标准输入字段。', 'zh-TW': '安裝DeepX NPU硬體驅動程式。需要<strong>sudo密碼</strong> — 點擊下方的<strong>⌨️ Manual Input</strong>開啟標準輸入欄位。', es: 'Instala el controlador de hardware NPU de DeepX. Requiere <strong>contraseña de sudo</strong> — haga clic en <strong>⌨️ Entrada manual</strong> abajo para abrir el campo stdin.' } },
        { target:'#setup-log', position:'top',
          title:{ ko: '실행 로그 영역', en: 'Execution Log Area', ja: '実行ログ エリア', 'zh-CN': '执行日志区域', 'zh-TW': '執行日誌區域', es: 'Área de registro de ejecución' },
          content:{ ko: '각 설치/빌드 작업의 <strong>실시간 로그</strong>가 여기에 표시됩니다. <strong>🔄 Refresh Status</strong>로 전체 상태를 갱신하고, <strong>⌨️ Manual Input</strong>으로 sudo 비밀번호 등을 입력할 수 있습니다.', en: '<strong>Real-time logs</strong> for each install/build task appear here. Use <strong>🔄 Refresh Status</strong> to update all, and <strong>⌨️ Manual Input</strong> for sudo passwords.', ja: '各インストール/ビルドタスクの<strong>リアルタイムログ</strong>がここに表示されます。<strong>🔄 Refresh Status</strong>で全体を更新、<strong>⌨️ Manual Input</strong>でsudoパスワードを入力できます。', 'zh-CN': '各安装/构建任务的<strong>实时日志</strong>在此显示。使用<strong>🔄 Refresh Status</strong>刷新全部状态，<strong>⌨️ Manual Input</strong>输入sudo密码。', 'zh-TW': '各安裝/建置任務的<strong>即時日誌</strong>在此顯示。使用<strong>🔄 Refresh Status</strong>重新整理全部狀態，<strong>⌨️ Manual Input</strong>輸入sudo密碼。', es: 'Aquí aparecen los <strong>registros en tiempo real</strong> de cada tarea de instalación/compilación. Utilice <strong>🔄 Actualizar estado</strong> para actualizar todo y <strong>⌨️ Entrada manual</strong> para contraseñas de sudo.' } },
        { target:'#diag-run-btn', position:'bottom',
          title:{ ko: '설치 진단 실행', en: 'Run Diagnostics', ja: '診断実行', 'zh-CN': '运行诊断', 'zh-TW': '執行診斷', es: 'Ejecutar diagnósticos' },
          content:{ ko: '<strong>▶ Run Diagnostics</strong>를 클릭하면 설치 후 시스템 상태를 자동 점검합니다. NPU 드라이버, 런타임 버전, 의존성 등을 확인하여 문제를 조기에 발견합니다.', en: 'Click <strong>▶ Run Diagnostics</strong> to auto-check system after installation. Verifies NPU driver, runtime version, and dependencies to detect issues early.', ja: '<strong>▶ Run Diagnostics</strong>をクリックして、インストール後のシステムを自動チェックします。NPUドライバ、ランタイムバージョン、依存関係を確認し、問題を早期に検出します。', 'zh-CN': '点击<strong>▶ Run Diagnostics</strong>在安装后自动检查系统。验证NPU驱动、运行时版本和依赖项，及早发现问题。', 'zh-TW': '點擊<strong>▶ Run Diagnostics</strong>在安裝後自動檢查系統。驗證NPU驅動、執行環境版本和依賴項，及早發現問題。', es: 'Haga clic en <strong>▶ Ejecutar diagnósticos</strong> para comprobar automáticamente el sistema tras la instalación. Verifica el controlador NPU, la versión del runtime y las dependencias para detectar problemas a tiempo.' } },
      ]
    },

    { id:'models', icon:'📦',
      title:{ ko: '📦 Models', en: '📦 Models', ja: '📦 モデル一覧', 'zh-CN': '📦 模型列表', 'zh-TW': '📦 模型列表', es: '📦 Modelos' },
      description:{ ko: '설치된 AI 모델 목록 확인 및 필터링', en: 'View and filter installed AI models', ja: 'インストール済みAIモデルの一覧とフィルタリング', 'zh-CN': '查看和筛选已安装的AI模型', 'zh-TW': '檢視和篩選已安裝的AI模型', es: 'Ver y filtrar modelos de IA instalados' },
      prerequisite:'setup',
      prerequisiteMessage:{ ko: '모델을 보려면 먼저 Setup에서 샘플 모델을 다운로드하세요.', en: 'Download sample models in Setup first.', ja: 'まずセットアップでサンプルモデルをダウンロードしてください。', 'zh-CN': '请先在设置中下载示例模型。', 'zh-TW': '請先在設定中下載範例模型。', es: 'Descargue primero modelos de muestra en Configuración.' },
      beforeStart:function(){ goPage('models'); },
      steps:[
        { target:'#cat-chips', position:'bottom',
          title:{ ko: '카테고리 필터 칩', en: 'Category Filter Chips', ja: 'カテゴリフィルタ チップ', 'zh-CN': '分类筛选标签', 'zh-TW': '分類篩選標籤', es: 'Chips de filtro por categoría' },
          content:{ ko: '<strong>Detection, Classification, Segmentation, Pose, Depth</strong> 등 카테고리별로 모델을 필터링합니다. 칩을 클릭하면 해당 카테고리 모델만 표시됩니다.', en: 'Filter models by <strong>Detection, Classification, Segmentation, Pose, Depth</strong> etc. Click a chip to show only that category.', ja: '<strong>Detection、Classification、Segmentation、Pose、Depth</strong>等のカテゴリでモデルをフィルタリングします。チップをクリックすると該当カテゴリのみ表示されます。', 'zh-CN': '按<strong>Detection、Classification、Segmentation、Pose、Depth</strong>等分类筛选模型。点击标签仅显示该分类。', 'zh-TW': '按<strong>Detection、Classification、Segmentation、Pose、Depth</strong>等分類篩選模型。點擊標籤僅顯示該分類。', es: 'Filtre modelos por <strong>Detection, Classification, Segmentation, Pose, Depth</strong>, etc. Haga clic en un chip para mostrar solo esa categoría.' } },
        { target:'#m-search', position:'bottom',
          title:{ ko: '모델 검색', en: 'Model Search', ja: 'モデル検索', 'zh-CN': '模型搜索', 'zh-TW': '模型搜尋', es: 'Búsqueda de modelos' },
          content:{ ko: '모델 이름을 입력하면 <strong>실시간으로 테이블이 필터링</strong>됩니다. 예: "yolo"를 입력하면 YOLOv5, YOLOv8 등이 표시됩니다.', en: 'Type a model name for <strong>real-time table filtering</strong>. e.g., "yolo" shows YOLOv5, YOLOv8, etc.', ja: 'モデル名を入力すると<strong>リアルタイムでテーブルがフィルタリング</strong>されます。例："yolo"でYOLOv5、YOLOv8等が表示されます。', 'zh-CN': '输入模型名称进行<strong>实时表格筛选</strong>。例如输入"yolo"将显示YOLOv5、YOLOv8等。', 'zh-TW': '輸入模型名稱進行<strong>即時表格篩選</strong>。例如輸入"yolo"將顯示YOLOv5、YOLOv8等。', es: 'Escriba un nombre de modelo para <strong>filtrar la tabla en tiempo real</strong>. p. ej., "yolo" muestra YOLOv5, YOLOv8, etc.' } },
        { target:'#m-table', position:'top',
          title:{ ko: '모델 테이블', en: 'Model Table', ja: 'モデルテーブル', 'zh-CN': '模型列表', 'zh-TW': '模型列表', es: 'Tabla de modelos' },
          content:{ ko: '각 모델의 <strong>이름, 카테고리, C++/Python 지원 여부, 실행 모드(Sync/Async), 메타 정보, 파일 크기</strong>를 확인합니다. Actions 열의 버튼으로 빠른 실행이 가능합니다.', en: 'View each model\'s <strong>name, category, C++/Python support, mode (Sync/Async), meta info, file size</strong>. Use Actions column for quick run.', ja: '各モデルの<strong>名前、カテゴリ、C++/Python対応、モード（Sync/Async）、メタ情報、ファイルサイズ</strong>を確認します。Actions列のボタンで素早く実行できます。', 'zh-CN': '查看各模型的<strong>名称、分类、C++/Python支持、模式（Sync/Async）、元信息、文件大小</strong>。可通过Actions列按钮快速运行。', 'zh-TW': '檢視各模型的<strong>名稱、分類、C++/Python支援、模式（Sync/Async）、中繼資料、檔案大小</strong>。可透過Actions欄按鈕快速執行。', es: 'Consulte el <strong>nombre, categoría, compatibilidad C++/Python, modo (Sync/Async), metadatos y tamaño de archivo</strong> de cada modelo. Utilice la columna Actions para una ejecución rápida.' } },
      ]
    },

    { id:'run-single', icon:'▶️',
      title:{ ko: '▶️ Run Inference (Single)', en: '▶️ Run Inference (Single)', ja: '▶️ 推論実行（シングル）', 'zh-CN': '▶️ 运行推理（单次）', 'zh-TW': '▶️ 執行推論（單次）', es: '▶️ Run Inference (Single)' },
      description:{ ko: '단일 이미지/비디오에 대한 AI 추론 실행', en: 'Run AI inference on a single image or video', ja: '単一の画像/ビデオに対するAI推論の実行', 'zh-CN': '对单张图片或视频运行AI推理', 'zh-TW': '對單張圖片或影片執行AI推論', es: 'Ejecutar inferencia de IA en una sola imagen o video' },
      prerequisite:'setup',
      beforeStart:function(){ _prepRunSingleTab(); },
      steps:[
        { target:'.run-tab-bar', position:'bottom',
          title:{ ko: 'Single / Continuous 탭', en: 'Single / Continuous Tabs', ja: 'シングル / 連続 タブ', 'zh-CN': '单次/连续 选项卡', 'zh-TW': '單次/連續 分頁', es: 'Pestañas Single / Continuous' },
          content:{ ko: '<strong>📷 Single</strong>: 이미지 1장 또는 비디오 1개에 대한 추론. <strong>🔄 Continuous</strong>: 비디오/카메라/RTSP 스트림에 대한 연속 추론. 탭을 클릭하여 전환합니다.', en: '<strong>📷 Single</strong>: Inference on one image/video. <strong>🔄 Continuous</strong>: Continuous inference on streams. Click tabs to switch.', ja: '<strong>📷 Single</strong>：画像/ビデオ1件に対する推論。<strong>🔄 Continuous</strong>：ストリームへの連続推論。タブをクリックして切り替えます。', 'zh-CN': '<strong>📷 Single</strong>：对一张图片/视频进行推理。<strong>🔄 Continuous</strong>：对流进行连续推理。点击选项卡切换。', 'zh-TW': '<strong>📷 Single</strong>：對一張圖片/影片進行推論。<strong>🔄 Continuous</strong>：對串流進行連續推論。點擊分頁切換。', es: '<strong>📷 Single</strong>: inferencia en una imagen/video. <strong>🔄 Continuous</strong>: inferencia continua en flujos. Haga clic en las pestañas para cambiar.' } },
        { target:'.radio-group', position:'right',
          title:{ ko: '입력 타입 선택', en: 'Input Type', ja: '入力タイプ', 'zh-CN': '输入类型', 'zh-TW': '輸入類型', es: 'Tipo de entrada' },
          content:{ ko: '<strong>🖼 Image</strong>: 단일 이미지 추론. <strong>🎬 Video</strong>: 비디오 파일 프레임별 추론. 라디오 버튼으로 전환하면 하단 입력 영역이 변경됩니다.', en: '<strong>🖼 Image</strong>: Single image inference. <strong>🎬 Video</strong>: Per-frame video inference. Switching radio buttons changes the input area below.', ja: '<strong>🖼 Image</strong>：単一画像推論。<strong>🎬 Video</strong>：ビデオのフレーム別推論。ラジオボタンを切り替えると下部の入力エリアが変わります。', 'zh-CN': '<strong>🖼 Image</strong>：单张图片推理。<strong>🎬 Video</strong>：视频逐帧推理。切换单选按钮后下方输入区域会改变。', 'zh-TW': '<strong>🖼 Image</strong>：單張圖片推論。<strong>🎬 Video</strong>：影片逐幀推論。切換單選按鈕後下方輸入區域會改變。', es: '<strong>🖼 Imagen</strong>: inferencia en una sola imagen. <strong>🎬 Video</strong>: inferencia por fotograma en video. Al cambiar los botones de radio, cambia el área de entrada inferior.' },
          beforeStep: function() { var radio = document.getElementById('r-input-img'); if (radio && !radio.checked) radio.click(); } },
        { target:'#r-cat', position:'right',
          title:{ ko: '카테고리 선택', en: 'Select Category', ja: 'カテゴリ選択', 'zh-CN': '选择分类', 'zh-TW': '選擇分類', es: 'Seleccionar categoría' },
          content:{ ko: '<strong>Object Detection, Classification, Segmentation, Pose Estimation</strong> 등의 AI 태스크 카테고리를 선택합니다. 선택에 따라 아래 모델 목록이 변경됩니다. 카테고리를 선택하면 해당 작업에 맞는 추가 파라미터가 표시됩니다 (Classification → Top-K, Segmentation → Alpha 등).', en: 'Select AI task category: <strong>Detection, Classification, Segmentation, Pose</strong> etc. Model list updates accordingly. Selecting a category shows task-specific parameters (Classification → Top-K, Segmentation → Alpha, etc.).', ja: 'AIタスクカテゴリを選択：<strong>Detection、Classification、Segmentation、Pose</strong>等。選択に応じてモデルリストが更新されます。カテゴリ選択によりタスク固有パラメータが表示されます（Classification → Top-K、Segmentation → Alpha等）。', 'zh-CN': '选择AI任务分类：<strong>Detection、Classification、Segmentation、Pose</strong>等。模型列表随之更新。选择分类后显示任务特定参数（Classification → Top-K、Segmentation → Alpha等）。', 'zh-TW': '選擇AI任務分類：<strong>Detection、Classification、Segmentation、Pose</strong>等。模型列表隨之更新。選擇分類後顯示任務特定參數（Classification → Top-K、Segmentation → Alpha等）。', es: 'Seleccione la categoría de tarea de IA: <strong>Detection, Classification, Segmentation, Pose</strong>, etc. La lista de modelos se actualiza en consecuencia. Al seleccionar una categoría, se muestran parámetros específicos (Classification → Top-K, Segmentation → Alpha, etc.).' } },
        { target:'#r-model', position:'right',
          title:{ ko: '모델 선택', en: 'Select Model', ja: 'モデル選択', 'zh-CN': '选择模型', 'zh-TW': '選擇模型', es: 'Seleccionar modelo' },
          content:{ ko: '선택한 카테고리에서 사용할 <strong>AI 모델</strong>을 선택합니다. 예: YOLOv8n, ResNet50, DeepLabV3 등', en: 'Select the <strong>AI model</strong> from chosen category. e.g., YOLOv8n, ResNet50, DeepLabV3.', ja: '選択したカテゴリから<strong>AIモデル</strong>を選択します。例：YOLOv8n、ResNet50、DeepLabV3。', 'zh-CN': '从所选分类中选择<strong>AI模型</strong>。例如：YOLOv8n、ResNet50、DeepLabV3。', 'zh-TW': '從所選分類中選擇<strong>AI模型</strong>。例如：YOLOv8n、ResNet50、DeepLabV3。', es: 'Seleccione el <strong>modelo de IA</strong> de la categoría elegida. p. ej., YOLOv8n, ResNet50, DeepLabV3.' } },
        { target:'#r-lang', position:'right',
          title:{ ko: '실행 언어', en: 'Language', ja: '実行言語', 'zh-CN': '执行语言', 'zh-TW': '執行語言', es: 'Idioma' },
          content:{ ko: '<strong>C++</strong>(컴파일된 고성능)과 <strong>Python</strong>(스크립트) 중 선택합니다. C++이 일반적으로 더 빠릅니다.', en: 'Choose <strong>C++</strong> (compiled, high-performance) or <strong>Python</strong> (scripted). C++ is generally faster.', ja: '<strong>C++</strong>（コンパイル済み、高性能）または<strong>Python</strong>（スクリプト）を選択します。一般的にC++の方が高速です。', 'zh-CN': '选择<strong>C++</strong>（编译型，高性能）或<strong>Python</strong>（脚本型）。C++通常更快。', 'zh-TW': '選擇<strong>C++</strong>（編譯型，高效能）或<strong>Python</strong>（腳本型）。C++通常更快。', es: 'Elija <strong>C++</strong> (compilado, alto rendimiento) o <strong>Python</strong> (script). C++ suele ser más rápido.' } },
        { target:'#r-mode', position:'right',
          title:{ ko: '실행 모드 (Sync/Async)', en: 'Execution Mode (Sync/Async)', ja: '実行モード（Sync/Async）', 'zh-CN': '执行模式（同步/异步）', 'zh-TW': '執行模式（同步/非同步）', es: 'Modo de ejecución (Sync/Async)' },
          content:{ ko: '<strong>Sync</strong>: 한 프레임 추론이 끝난 후 다음 프레임 처리. <strong>Async</strong>: 추론과 전처리를 파이프라인으로 병렬 처리하여 더 높은 FPS를 달성합니다.', en: '<strong>Sync</strong>: Process next frame after current completes. <strong>Async</strong>: Pipeline inference and preprocessing for higher FPS.', ja: '<strong>Sync</strong>：現在のフレーム処理完了後に次のフレームを処理。<strong>Async</strong>：推論と前処理をパイプラインで並列処理し、より高いFPSを実現します。', 'zh-CN': '<strong>Sync</strong>：当前帧完成后处理下一帧。<strong>Async</strong>：将推理与预处理流水线并行以获得更高FPS。', 'zh-TW': '<strong>Sync</strong>：當前幀完成後處理下一幀。<strong>Async</strong>：將推論與預處理以管線並行以獲得更高FPS。', es: '<strong>Sync</strong>: procesa el siguiente fotograma cuando termina el actual. <strong>Async</strong>: canaliza inferencia y preprocesamiento para mayor FPS.' } },
        { target:'#r-dev', position:'right',
          title:{ ko: 'Device ID', en: 'Device ID', ja: 'デバイス ID', 'zh-CN': '设备 ID', 'zh-TW': '裝置 ID', es: 'ID de dispositivo' },
          content:{ ko: '추론을 실행할 <strong>NPU 디바이스 번호</strong>를 선택합니다. 여러 NPU가 장착된 시스템에서는 특정 디바이스를 지정할 수 있습니다.', en: 'Select the <strong>NPU device number</strong> for inference. On multi-NPU systems, you can target a specific device.', ja: '推論に使用する<strong>NPUデバイス番号</strong>を選択します。複数NPUシステムでは特定のデバイスを指定できます。', 'zh-CN': '选择推理所用的<strong>NPU设备编号</strong>。在多NPU系统中可指定特定设备。', 'zh-TW': '選擇推論所用的<strong>NPU裝置編號</strong>。在多NPU系統中可指定特定裝置。', es: 'Seleccione el <strong>número de dispositivo NPU</strong> para la inferencia. En sistemas con varias NPU, puede elegir un dispositivo concreto.' } },
        { target:'#r-conf', position:'right',
          title:{ ko: 'Confidence Threshold', en: 'Confidence Threshold', ja: '信頼度しきい値', 'zh-CN': '置信度阈值', 'zh-TW': '信賴度閾值', es: 'Umbral de confianza' },
          content:{ ko: '모델 출력의 <strong>최소 신뢰도 임계값</strong>(0~1)입니다. 값이 높을수록 확실한 결과만 표시되고, 낮을수록 더 많은 결과가 표시됩니다. Detection에서 기본값은 <strong>0.25</strong>입니다.', en: '<strong>Minimum confidence threshold</strong> (0-1) for model output. Higher = fewer but more confident results. Default <strong>0.25</strong> for Detection.', ja: 'モデル出力の<strong>最小信頼度しきい値</strong>（0〜1）。値が高いほど確実な結果のみ表示されます。Detectionのデフォルトは<strong>0.25</strong>です。', 'zh-CN': '模型输出的<strong>最小置信度阈值</strong>（0-1）。值越高结果越少但越可靠。Detection默认值为<strong>0.25</strong>。', 'zh-TW': '模型輸出的<strong>最小信賴度閾值</strong>（0-1）。值越高結果越少但越可靠。Detection預設值為<strong>0.25</strong>。', es: '<strong>Umbral mínimo de confianza</strong> (0-1) para la salida del modelo. Un valor más alto = menos resultados pero más confiables. Valor predeterminado <strong>0.25</strong> para Detection.' },
          beforeStep: function() { _showDetectParams(); } },
        { target:'#r-nms', position:'right',
          title:{ ko: 'NMS IoU Threshold', en: 'NMS IoU Threshold', ja: 'NMS IoU しきい値', 'zh-CN': 'NMS IoU 阈值', 'zh-TW': 'NMS IoU 閾值', es: 'Umbral NMS IoU' },
          content:{ ko: '<strong>Non-Maximum Suppression</strong>의 IoU 임계값입니다. 겹치는 바운딩 박스를 제거하는 기준으로, 값이 낮을수록 더 공격적으로 중복을 제거합니다. Detection 전용 파라미터입니다.', en: '<strong>Non-Maximum Suppression</strong> IoU threshold. Controls overlapping bounding box removal. Lower = more aggressive dedup. Detection only.', ja: '<strong>Non-Maximum Suppression</strong>のIoUしきい値。重複するバウンディングボックスの除去を制御します。値が低いほど積極的に重複を除去します。Detection専用パラメータです。', 'zh-CN': '<strong>Non-Maximum Suppression</strong> IoU阈值。控制重叠边界框的去除。值越低去重越积极。仅用于Detection。', 'zh-TW': '<strong>Non-Maximum Suppression</strong> IoU閾值。控制重疊邊界框的去除。值越低去重越積極。僅用於Detection。', es: 'Umbral IoU de <strong>Non-Maximum Suppression</strong>. Controla la eliminación de cajas delimitadoras superpuestas. Un valor más bajo = deduplicación más agresiva. Solo Detection.' },
          beforeStep: function() { _showDetectParams(); } },
        { target:'#r-topk', position:'right',
          title:{ ko: 'Top-K 결과 수', en: 'Top-K Results', ja: 'Top-K 結果数', 'zh-CN': 'Top-K 结果数', 'zh-TW': 'Top-K 結果數', es: 'Resultados Top-K' },
          content:{ ko: '<strong>Classification</strong> 카테고리 선택 시 표시되는 슬라이더입니다. 상위 <strong>K개의 분류 결과</strong>를 표시합니다. 값이 클수록 더 많은 후보 클래스가 결과에 포함됩니다 (기본값: 5).', en: 'Slider shown when <strong>Classification</strong> category is selected. Displays the top <strong>K classification results</strong>. Higher values include more candidate classes (default: 5).', ja: '<strong>Classification</strong>カテゴリ選択時に表示されるスライダーです。上位<strong>K個の分類結果</strong>を表示します。値が大きいほどより多くの候補クラスが含まれます（デフォルト：5）。', 'zh-CN': '选择<strong>Classification</strong>分类时显示的滑块。显示前<strong>K个分类结果</strong>。值越大包含的候选类别越多（默认：5）。', 'zh-TW': '選擇<strong>Classification</strong>分類時顯示的滑桿。顯示前<strong>K個分類結果</strong>。值越大包含的候選類別越多（預設：5）。', es: 'Control deslizante que aparece al seleccionar la categoría <strong>Classification</strong>. Muestra los <strong>K mejores resultados de clasificación</strong>. Valores más altos incluyen más clases candidatas (predeterminado: 5).' },
          beforeStep: function() { var sel = document.getElementById('r-cat'); if(sel) { sel.value='classification'; sel.dispatchEvent(new Event('change')); } } },
        { target:'#r-alpha', position:'right',
          title:{ ko: '오버레이 투명도 (Alpha)', en: 'Overlay Alpha', ja: 'オーバーレイ透明度（Alpha）', 'zh-CN': '叠加透明度（Alpha）', 'zh-TW': '疊加透明度（Alpha）', es: 'Alpha de superposición' },
          content:{ ko: '<strong>Segmentation</strong> 카테고리 선택 시 표시되는 슬라이더입니다. 분할 <strong>마스크 오버레이의 투명도</strong>(0~1)를 조절합니다. 0이면 투명, 1이면 불투명합니다 (기본값: 0.6).', en: 'Slider shown when <strong>Segmentation</strong> category is selected. Adjusts <strong>mask overlay transparency</strong> (0-1). 0 = transparent, 1 = opaque (default: 0.6).', ja: '<strong>Segmentation</strong>カテゴリ選択時に表示されるスライダーです。<strong>マスクオーバーレイの透明度</strong>（0〜1）を調整します。0=透明、1=不透明（デフォルト：0.6）。', 'zh-CN': '选择<strong>Segmentation</strong>分类时显示的滑块。调整<strong>蒙版叠加透明度</strong>（0-1）。0=透明，1=不透明（默认：0.6）。', 'zh-TW': '選擇<strong>Segmentation</strong>分類時顯示的滑桿。調整<strong>遮罩疊加透明度</strong>（0-1）。0=透明，1=不透明（預設：0.6）。', es: 'Control deslizante que aparece al seleccionar la categoría <strong>Segmentation</strong>. Ajusta la <strong>transparencia de la máscara superpuesta</strong> (0-1). 0 = transparente, 1 = opaco (predeterminado: 0.6).' },
          beforeStep: function() { _showSegParams(); } },
        { target:'#img-grid', position:'top',
          title:{ ko: '샘플 이미지 선택', en: 'Select Sample Image', ja: 'サンプル画像の選択', 'zh-CN': '选择示例图片', 'zh-TW': '選擇範例圖片', es: 'Seleccionar imagen de muestra' },
          content:{ ko: '제공된 <strong>샘플 이미지 썸네일</strong> 중 하나를 클릭하여 입력으로 사용합니다. 비디오 모드에서는 비디오 파일 선택 드롭다운이 나타납니다.', en: 'Click a <strong>sample image thumbnail</strong> to use as input. In video mode, a video file dropdown appears.', ja: '<strong>サンプル画像のサムネイル</strong>をクリックして入力として使用します。ビデオモードではビデオファイルのドロップダウンが表示されます。', 'zh-CN': '点击<strong>示例图片缩略图</strong>作为输入。在视频模式下会出现视频文件下拉列表。', 'zh-TW': '點擊<strong>範例圖片縮圖</strong>作為輸入。在影片模式下會出現影片檔案下拉選單。', es: 'Haga clic en una <strong>miniatura de imagen de muestra</strong> para usarla como entrada. En modo video, aparece un menú desplegable de archivos de video.' } },
        { target:'#r-run-btn', position:'right',
          title:{ ko: '▶ Run Inference', en: '▶ Run Inference', ja: '▶ 推論実行', 'zh-CN': '▶ 运行推理', 'zh-TW': '▶ 執行推論', es: '▶ Ejecutar inferencia' },
          content:{ ko: '설정을 마친 후 이 버튼을 클릭하면 <strong>NPU에서 AI 추론이 실행</strong>됩니다. 결과(바운딩 박스, 분류 결과 등)가 우측 Result 영역에 표시됩니다.', en: 'After configuration, click to <strong>run AI inference on NPU</strong>. Results (bounding boxes, classification, etc.) appear in the Result area.', ja: '設定完了後にクリックして<strong>NPU上でAI推論を実行</strong>します。結果（バウンディングボックス、分類等）が結果エリアに表示されます。', 'zh-CN': '配置完成后点击以<strong>在NPU上运行AI推理</strong>。结果（边界框、分类等）显示在结果区域。', 'zh-TW': '配置完成後點擊以<strong>在NPU上執行AI推論</strong>。結果（邊界框、分類等）顯示在結果區域。', es: 'Tras configurar, haga clic para <strong>ejecutar inferencia de IA en la NPU</strong>. Los resultados (cajas delimitadoras, clasificación, etc.) aparecen en el área Result.' } },
        { target:'#run-result-card', position:'left',
          title:{ ko: '추론 결과', en: 'Inference Result', ja: '推論結果', 'zh-CN': '推理结果', 'zh-TW': '推論結果', es: 'Resultado de inferencia' },
          content:{ ko: '추론이 완료되면 <strong>결과 이미지, FPS, 지연시간, 검출된 객체 정보</strong>가 표시됩니다. 이미지를 클릭하면 원본 크기로 미리보기가 가능합니다.', en: 'After inference, shows <strong>result image, FPS, latency, detected object info</strong>. Click image for full-size preview.', ja: '推論完了後、<strong>結果画像、FPS、レイテンシ、検出オブジェクト情報</strong>が表示されます。画像をクリックするとフルサイズプレビューが可能です。', 'zh-CN': '推理完成后显示<strong>结果图片、FPS、延迟、检测对象信息</strong>。点击图片可全尺寸预览。', 'zh-TW': '推論完成後顯示<strong>結果圖片、FPS、延遲、偵測物件資訊</strong>。點擊圖片可全尺寸預覽。', es: 'Tras la inferencia, muestra la <strong>imagen de resultado, FPS, latencia e información de objetos detectados</strong>. Haga clic en la imagen para vista previa a tamaño completo.' } },
        { target:'#run-export-card', position:'top',
          title:{ ko: '📦 Export Model Package', en: '📦 Export Model Package', ja: '📦 モデルパッケージ エクスポート', 'zh-CN': '📦 导出模型包', 'zh-TW': '📦 匯出模型套件', es: '📦 Exportar paquete de modelo' },
          content:{ ko: '현재 선택한 모델의 <strong>소스 코드, config, 모델 파일을 패키징</strong>하여 Outputs 페이지에서 다운로드할 수 있습니다. C++/Python 또는 Both 중 선택 가능합니다.', en: '<strong>Package source code, config, and model file</strong> of current model for download on Outputs page. Choose C++/Python/Both.', ja: '現在のモデルの<strong>ソースコード、設定、モデルファイルをパッケージ化</strong>してOutputsページでダウンロード可能にします。C++/Python/Both から選択できます。', 'zh-CN': '将当前模型的<strong>源代码、配置和模型文件打包</strong>，可在Outputs页面下载。可选择C++/Python/Both。', 'zh-TW': '將當前模型的<strong>原始碼、配置和模型檔案打包</strong>，可在Outputs頁面下載。可選擇C++/Python/Both。', es: '<strong>Empaqueta el código fuente, la configuración y el archivo del modelo</strong> actual para descargarlo en la página Outputs. Elija C++/Python/Ambos.' },
          beforeStep: function() { return _prepRunExportArea(); } },
        { target:'#r-export-lang', position:'right',
          title:{ ko: 'Export 언어 선택', en: 'Export Language', ja: 'エクスポート言語', 'zh-CN': '导出语言', 'zh-TW': '匯出語言', es: 'Idioma de exportación' },
          content:{ ko: '내보낼 모델 패키지의 <strong>언어를 선택</strong>합니다. <strong>Both (C++ & Python)</strong>, <strong>C++ only</strong>, <strong>Python only</strong> 중 선택 가능합니다.', en: 'Select the <strong>language</strong> for the export package: <strong>Both (C++ & Python)</strong>, <strong>C++ only</strong>, or <strong>Python only</strong>.', ja: 'エクスポートパッケージの<strong>言語</strong>を選択します：<strong>Both (C++ & Python)</strong>、<strong>C++ only</strong>、<strong>Python only</strong>。', 'zh-CN': '选择导出包的<strong>语言</strong>：<strong>Both (C++ & Python)</strong>、<strong>C++ only</strong>或<strong>Python only</strong>。', 'zh-TW': '選擇匯出套件的<strong>語言</strong>：<strong>Both (C++ & Python)</strong>、<strong>C++ only</strong>或<strong>Python only</strong>。',           es: 'Seleccione el <strong>idioma</strong> del paquete de exportación: <strong>Ambos (C++ y Python)</strong>, <strong>solo C++</strong> o <strong>solo Python</strong>.' },
          beforeStep: function() { return _prepRunExportArea(); } },
        { target:'#r-export-btn', position:'top',
          title:{ ko: '📦 내보내기 실행', en: '📦 Run Export', ja: '📦 エクスポート実行', 'zh-CN': '📦 执行导出', 'zh-TW': '📦 執行匯出', es: '📦 Ejecutar exportación' },
          content:{ ko: '<strong>📦 내보내기</strong> 버튼을 클릭하면 선택한 언어로 모델 소스 코드, config, 바이너리를 패키징합니다. 결과는 <strong>Outputs 페이지</strong>에서 다운로드할 수 있습니다.', en: 'Click <strong>📦 Export</strong> to package model source code, config, and binary in the selected language. Download from the <strong>Outputs page</strong>.', ja: '<strong>📦 Export</strong>をクリックして、選択した言語でモデルのソースコード、設定、バイナリをパッケージ化します。<strong>Outputsページ</strong>からダウンロードできます。', 'zh-CN': '点击<strong>📦 Export</strong>以所选语言打包模型源代码、配置和二进制文件。从<strong>Outputs页面</strong>下载。', 'zh-TW': '點擊<strong>📦 Export</strong>以所選語言打包模型原始碼、配置和二進位檔案。從<strong>Outputs頁面</strong>下載。',           es: 'Haga clic en <strong>📦 Exportar</strong> para empaquetar el código fuente, la configuración y el binario del modelo en el idioma seleccionado. Descárguelo desde la <strong>página Outputs</strong>.' },
          beforeStep: function() { return _prepRunExportArea(); } },
        { target:'#r-stop-btn', position:'right',
          title:{ ko: '추론 중단', en: 'Stop Inference', ja: '推論中断', 'zh-CN': '停止推理', 'zh-TW': '停止推論', es: 'Detener inferencia' },
          content:{ ko: '추론이 실행 중일 때 이 버튼을 클릭하면 <strong>현재 추론을 즉시 중단</strong>합니다. 비디오 모드에서 긴 추론을 중간에 멈출 때 유용합니다.', en: 'Click to <strong>immediately stop the running inference</strong>. Useful for stopping long video inference midway.', ja: 'クリックして<strong>実行中の推論を即座に中断</strong>します。長時間のビデオ推論を途中で停止する際に便利です。', 'zh-CN': '点击以<strong>立即停止正在运行的推理</strong>。适用于中途停止较长的视频推理。', 'zh-TW': '點擊以<strong>立即停止正在執行的推論</strong>。適用於中途停止較長的影片推論。', es: 'Haga clic para <strong>detener de inmediato la inferencia en ejecución</strong>. Útil para interrumpir inferencia larga en video.' },
          beforeStep: function() { var btn = document.getElementById('r-stop-btn'); if (btn) btn.classList.remove('hidden'); } },
        { target:'#r-video', position:'right',
          title:{ ko: '비디오 파일 선택', en: 'Select Video File', ja: 'ビデオファイル選択', 'zh-CN': '选择视频文件', 'zh-TW': '選擇影片檔案', es: 'Seleccionar archivo de video' },
          content:{ ko: '입력 타입을 <strong>🎬 Video</strong>로 선택하면 나타나는 드롭다운입니다. 다운로드된 <strong>샘플 비디오 파일</strong> 목록에서 선택하세요.', en: 'Dropdown that appears when <strong>🎬 Video</strong> input type is selected. Choose from the list of downloaded <strong>sample video files</strong>.', ja: '<strong>🎬 Video</strong>入力タイプ選択時に表示されるドロップダウンです。ダウンロード済みの<strong>サンプルビデオファイル</strong>一覧から選択します。', 'zh-CN': '选择<strong>🎬 Video</strong>输入类型时出现的下拉列表。从已下载的<strong>示例视频文件</strong>列表中选择。', 'zh-TW': '選擇<strong>🎬 Video</strong>輸入類型時出現的下拉選單。從已下載的<strong>範例影片檔案</strong>列表中選擇。', es: 'Menú desplegable que aparece al seleccionar el tipo de entrada <strong>🎬 Video</strong>. Elija entre la lista de <strong>archivos de video de muestra</strong> descargados.' },
          beforeStep: function() { var radio = document.getElementById('r-input-vid'); if (radio) radio.click(); } },
      ]
    },

    { id:'run-cont', icon:'🔄',
      title:{ ko: '🔄 Run Inference (Continuous)', en: '🔄 Run Inference (Continuous)', ja: '🔄 推論実行（連続）', 'zh-CN': '🔄 运行推理（连续）', 'zh-TW': '🔄 執行推論（連續）', es: '🔄 Run Inference (Continuous)' },
      description:{ ko: '비디오/카메라/RTSP 스트림 연속 추론', en: 'Continuous inference on video/camera/RTSP streams', ja: 'ビデオ/カメラ/RTSPストリームの連続推論', 'zh-CN': '视频/摄像头/RTSP流的连续推理', 'zh-TW': '影片/攝影機/RTSP串流的連續推論', es: 'Inferencia continua en flujos de video/cámara/RTSP' },
      prerequisite:'setup',
      beforeStart:function(){ goPage('run'); if(typeof toggleRunTab==='function') toggleRunTab('continuous'); },
      steps:[
        { target:'#c-input-type', position:'right',
          title:{ ko: '입력 소스 선택', en: 'Input Source', ja: '入力ソース', 'zh-CN': '输入源', 'zh-TW': '輸入來源', es: 'Fuente de entrada' },
          content:{ ko: '<strong>🎬 Video</strong>(파일), <strong>📹 Camera</strong>(USB 웹캠), <strong>📡 RTSP</strong>(네트워크 스트림) 중 입력 소스를 선택합니다.', en: 'Select input source: <strong>🎬 Video</strong> (file), <strong>📹 Camera</strong> (USB webcam), <strong>📡 RTSP</strong> (network stream).', ja: '入力ソースを選択：<strong>🎬 Video</strong>（ファイル）、<strong>📹 Camera</strong>（USBウェブカメラ）、<strong>📡 RTSP</strong>（ネットワークストリーム）。', 'zh-CN': '选择输入源：<strong>🎬 Video</strong>（文件）、<strong>📹 Camera</strong>（USB摄像头）、<strong>📡 RTSP</strong>（网络流）。', 'zh-TW': '選擇輸入來源：<strong>🎬 Video</strong>（檔案）、<strong>📹 Camera</strong>（USB攝影機）、<strong>📡 RTSP</strong>（網路串流）。', es: 'Seleccione la fuente de entrada: <strong>🎬 Video</strong> (archivo), <strong>📹 Camera</strong> (webcam USB), <strong>📡 RTSP</strong> (flujo de red).' } },
        { target:'#c-lang', position:'right',
          title:{ ko: '언어 & 모드 설정', en: 'Language & Mode', ja: '言語 & モード', 'zh-CN': '语言与模式', 'zh-TW': '語言與模式', es: 'Idioma y modo' },
          content:{ ko: '<strong>C++/Python</strong> 실행 언어와 <strong>Sync/Async</strong> 모드를 선택합니다. Async 모드는 파이프라인 병렬 처리로 더 높은 FPS를 제공합니다.', en: 'Select <strong>C++/Python</strong> language and <strong>Sync/Async</strong> mode. Async pipelines preprocessing and inference for higher FPS.', ja: '<strong>C++/Python</strong>実行言語と<strong>Sync/Async</strong>モードを選択します。Asyncモードは前処理と推論をパイプライン並列処理し、より高いFPSを実現します。', 'zh-CN': '选择<strong>C++/Python</strong>执行语言和<strong>Sync/Async</strong>模式。Async模式将预处理和推理流水线并行以获得更高FPS。', 'zh-TW': '選擇<strong>C++/Python</strong>執行語言和<strong>Sync/Async</strong>模式。Async模式將預處理和推論以管線並行以獲得更高FPS。', es: 'Seleccione el idioma <strong>C++/Python</strong> y el modo <strong>Sync/Async</strong>. Async canaliza preprocesamiento e inferencia para mayor FPS.' } },
        { target:'#c-dev', position:'right',
          title:{ ko: 'Device ID', en: 'Device ID', ja: 'デバイス ID', 'zh-CN': '设备 ID', 'zh-TW': '裝置 ID', es: 'ID de dispositivo' },
          content:{ ko: '연속 추론에 사용할 <strong>NPU 디바이스</strong>를 선택합니다. 모든 슬롯이 동일한 디바이스에서 실행됩니다.', en: 'Select <strong>NPU device</strong> for continuous inference. All slots run on the same device.', ja: '連続推論に使用する<strong>NPUデバイス</strong>を選択します。すべてのスロットは同じデバイスで実行されます。', 'zh-CN': '选择连续推理所用的<strong>NPU设备</strong>。所有槽位在同一设备上运行。', 'zh-TW': '選擇連續推論所用的<strong>NPU裝置</strong>。所有插槽在同一裝置上執行。', es: 'Seleccione el <strong>dispositivo NPU</strong> para inferencia continua. Todas las ranuras usan el mismo dispositivo.' } },
        { target:'#c-slots', position:'right',
          title:{ ko: '📦 모델 슬롯', en: '📦 Model Slots', ja: '📦 モデルスロット', 'zh-CN': '📦 模型槽位', 'zh-TW': '📦 模型插槽', es: '📦 Ranuras de modelo' },
          content:{ ko: '<strong>최대 8개 모델 슬롯</strong>을 추가하여 서로 다른 AI 모델을 동시에 실행할 수 있습니다. 각 슬롯에서 카테고리와 모델을 선택하세요.', en: 'Add up to <strong>8 model slots</strong> to run different AI models simultaneously. Select category and model in each slot.', ja: '最大<strong>8つのモデルスロット</strong>を追加して、異なるAIモデルを同時実行できます。各スロットでカテゴリとモデルを選択してください。', 'zh-CN': '最多添加<strong>8个模型槽位</strong>同时运行不同的AI模型。在每个槽位中选择分类和模型。', 'zh-TW': '最多新增<strong>8個模型插槽</strong>同時執行不同的AI模型。在每個插槽中選擇分類和模型。', es: 'Añada hasta <strong>8 ranuras de modelo</strong> para ejecutar distintos modelos de IA simultáneamente. Seleccione categoría y modelo en cada ranura.' } },
        { target:'#c-add-btn', position:'right',
          title:{ ko: '슬롯 추가', en: 'Add Slot', ja: 'スロット追加', 'zh-CN': '添加槽位', 'zh-TW': '新增插槽', es: 'Añadir ranura' },
          content:{ ko: '<strong>＋ Add Model</strong>을 클릭하면 새 슬롯이 추가됩니다. 최대 8개까지 가능하며, 각 슬롯은 독립적으로 모델을 선택할 수 있습니다.', en: 'Click <strong>＋ Add Model</strong> to add a new slot. Up to 8 slots, each independently configurable.', ja: '<strong>＋ Add Model</strong>をクリックして新しいスロットを追加します。最大8スロットまで、各スロットは独立して設定できます。', 'zh-CN': '点击<strong>＋ Add Model</strong>添加新槽位。最多8个槽位，每个可独立配置。', 'zh-TW': '點擊<strong>＋ Add Model</strong>新增插槽。最多8個插槽，每個可獨立配置。', es: 'Haga clic en <strong>＋ Añadir modelo</strong> para añadir una ranura. Hasta 8 ranuras, cada una configurable de forma independiente.' } },
        { target:'#c-start-btn', position:'right',
          title:{ ko: '▶ Start Continuous', en: '▶ Start Continuous', ja: '▶ 連続推論開始', 'zh-CN': '▶ 开始连续推理', 'zh-TW': '▶ 開始連續推論', es: '▶ Iniciar Continuous' },
          content:{ ko: '모든 슬롯 설정을 마친 후 이 버튼을 클릭하면 <strong>연속 추론이 시작</strong>됩니다. 우측 Live Display에서 각 슬롯의 MJPEG 라이브 스트림을 확인할 수 있습니다.', en: 'Click to <strong>start continuous inference</strong>. View MJPEG live streams for each slot in the Live Display on the right.', ja: 'クリックして<strong>連続推論を開始</strong>します。右側のLive Displayで各スロットのMJPEGライブストリームを確認できます。', 'zh-CN': '点击<strong>开始连续推理</strong>。在右侧Live Display中查看各槽位的MJPEG实时画面。', 'zh-TW': '點擊<strong>開始連續推論</strong>。在右側Live Display中檢視各插槽的MJPEG即時畫面。', es: 'Haga clic para <strong>iniciar inferencia continua</strong>. Vea flujos MJPEG en vivo de cada ranura en Live Display a la derecha.' } },
        { target:'#c-timer', position:'left',
          title:{ ko: '실행 타이머', en: 'Run Timer', ja: '実行タイマー', 'zh-CN': '运行计时器', 'zh-TW': '執行計時器', es: 'Temporizador de ejecución' },
          content:{ ko: '연속 추론이 시작되면 <strong>경과 시간</strong>이 표시됩니다. 빨간 점이 깜빡이면 추론이 실행 중입니다.', en: 'Shows <strong>elapsed time</strong> when continuous inference is running. Blinking red dot = inference active.', ja: '連続推論実行中の<strong>経過時間</strong>を表示します。赤い点の点滅 = 推論実行中。', 'zh-CN': '连续推理运行时显示<strong>已用时间</strong>。红点闪烁 = 推理进行中。', 'zh-TW': '連續推論執行時顯示<strong>已用時間</strong>。紅點閃爍 = 推論進行中。', es: 'Muestra el <strong>tiempo transcurrido</strong> mientras la inferencia continua está activa. Punto rojo parpadeante = inferencia activa.' } },
        { target:'#c-grid', position:'right',
          title:{ ko: '결과 그리드 & 라이브 뷰', en: 'Result Grid & Live View', ja: '結果グリッド & ライブビュー', 'zh-CN': '结果网格与实时画面', 'zh-TW': '結果網格與即時畫面', es: 'Cuadrícula de resultados y vista en vivo' },
          content:{ ko: '각 모델 슬롯의 <strong>추론 결과가 그리드</strong>로 표시됩니다. 비디오/카메라 모드에서는 <strong>MJPEG 라이브 스트림</strong>으로 실시간 결과를 확인할 수 있습니다.', en: 'Inference results for each slot shown in a <strong>grid</strong>. In video/camera mode, view <strong>MJPEG live streams</strong> for real-time results.', ja: '各スロットの推論結果が<strong>グリッド</strong>で表示されます。ビデオ/カメラモードでは<strong>MJPEGライブストリーム</strong>でリアルタイム結果を確認できます。', 'zh-CN': '各槽位的推理结果以<strong>网格</strong>形式显示。在视频/摄像头模式下，通过<strong>MJPEG实时流</strong>查看实时结果。', 'zh-TW': '各插槽的推論結果以<strong>網格</strong>形式顯示。在影片/攝影機模式下，透過<strong>MJPEG即時串流</strong>查看即時結果。', es: 'Los resultados de inferencia de cada ranura se muestran en una <strong>cuadrícula</strong>. En modo video/cámara, vea <strong>flujos MJPEG en vivo</strong> para resultados en tiempo real.' } },
        { target:'#c-summary', position:'top',
          title:{ ko: '성능 요약', en: 'Performance Summary', ja: '性能サマリー', 'zh-CN': '性能摘要', 'zh-TW': '效能摘要', es: 'Resumen de rendimiento' },
          content:{ ko: '연속 추론 종료 후 각 슬롯의 <strong>평균 FPS, 총 프레임 수, 처리 시간</strong> 등의 성능 요약이 표시됩니다.', en: 'After stopping, shows <strong>average FPS, total frames, processing time</strong> summary for each slot.', ja: '停止後、各スロットの<strong>平均FPS、総フレーム数、処理時間</strong>のサマリーが表示されます。', 'zh-CN': '停止后显示各槽位的<strong>平均FPS、总帧数、处理时间</strong>摘要。', 'zh-TW': '停止後顯示各插槽的<strong>平均FPS、總幀數、處理時間</strong>摘要。', es: 'Al detener, muestra un resumen de <strong>FPS promedio, fotogramas totales y tiempo de procesamiento</strong> por ranura.' },
          beforeStep: function() { var el = document.getElementById('c-summary'); if (el) el.style.display = ''; } },
        { target:'#c-stop-btn', position:'right',
          title:{ ko: '연속 추론 중단', en: 'Stop Continuous', ja: '連続推論中断', 'zh-CN': '停止连续推理', 'zh-TW': '停止連續推論', es: 'Detener Continuous' },
          content:{ ko: '연속 추론 실행 중 이 버튼을 클릭하면 <strong>모든 슬롯의 추론을 즉시 중단</strong>합니다. 중단 후 성능 요약이 표시됩니다.', en: 'Click to <strong>stop inference on all slots immediately</strong>. Performance summary is shown after stopping.', ja: 'クリックして<strong>全スロットの推論を即座に中断</strong>します。停止後に性能サマリーが表示されます。', 'zh-CN': '点击以<strong>立即停止所有槽位的推理</strong>。停止后显示性能摘要。', 'zh-TW': '點擊以<strong>立即停止所有插槽的推論</strong>。停止後顯示效能摘要。', es: 'Haga clic para <strong>detener de inmediato la inferencia en todas las ranuras</strong>. Tras detener, se muestra el resumen de rendimiento.' },
          beforeStep: function() { var el = document.getElementById('c-stop-btn'); if (el) el.classList.remove('hidden'); } },
        { target:'#c-camera', position:'right',
          title:{ ko: '카메라 선택', en: 'Select Camera', ja: 'カメラ選択', 'zh-CN': '选择摄像头', 'zh-TW': '選擇攝影機', es: 'Seleccionar cámara' },
          content:{ ko: '입력 소스를 <strong>📹 Camera</strong>로 선택하면 나타납니다. 연결된 <strong>USB 웹캠 디바이스</strong>(/dev/video0 등)를 선택합니다.', en: 'Appears when <strong>📹 Camera</strong> input is selected. Choose from connected <strong>USB webcam devices</strong> (/dev/video0, etc.).', ja: '<strong>📹 Camera</strong>入力選択時に表示されます。接続されている<strong>USBウェブカメラデバイス</strong>（/dev/video0等）から選択します。', 'zh-CN': '选择<strong>📹 Camera</strong>输入时出现。从已连接的<strong>USB摄像头设备</strong>（/dev/video0等）中选择。', 'zh-TW': '選擇<strong>📹 Camera</strong>輸入時出現。從已連接的<strong>USB攝影機裝置</strong>（/dev/video0等）中選擇。', es: 'Aparece al seleccionar entrada <strong>📹 Camera</strong>. Elija entre los <strong>dispositivos webcam USB</strong> conectados (/dev/video0, etc.).' },
          beforeStep: function() { var sel = document.getElementById('c-input-type'); if (sel) { sel.value = 'camera'; sel.dispatchEvent(new Event('change')); } } },
        { target:'#c-rtsp-ip', position:'right',
          title:{ ko: 'RTSP 주소 입력', en: 'RTSP Address', ja: 'RTSP アドレス', 'zh-CN': 'RTSP 地址', 'zh-TW': 'RTSP 地址', es: 'Dirección RTSP' },
          content:{ ko: '입력 소스를 <strong>📡 RTSP</strong>로 선택하면 나타납니다. 네트워크 카메라의 <strong>RTSP 서버 주소(IP:Port)</strong>를 입력합니다.', en: 'Appears when <strong>📡 RTSP</strong> input is selected. Enter the <strong>RTSP server address (IP:Port)</strong> of the network camera.', ja: '<strong>📡 RTSP</strong>入力選択時に表示されます。ネットワークカメラの<strong>RTSPサーバーアドレス（IP:Port）</strong>を入力します。', 'zh-CN': '选择<strong>📡 RTSP</strong>输入时出现。输入网络摄像头的<strong>RTSP服务器地址（IP:Port）</strong>。', 'zh-TW': '選擇<strong>📡 RTSP</strong>輸入時出現。輸入網路攝影機的<strong>RTSP伺服器地址（IP:Port）</strong>。', es: 'Aparece al seleccionar entrada <strong>📡 RTSP</strong>. Introduzca la <strong>dirección del servidor RTSP (IP:Puerto)</strong> de la cámara de red.' },
          beforeStep: function() { var sel = document.getElementById('c-input-type'); if (sel) { sel.value = 'rtsp'; sel.dispatchEvent(new Event('change')); } } },
      ]
    },

    { id:'bench', icon:'⏱️',
      title:{ ko: '⏱️ Benchmark', en: '⏱️ Benchmark', ja: '⏱️ ベンチマーク', 'zh-CN': '⏱️ 基准测试', 'zh-TW': '⏱️ 基準測試', es: '⏱️ Benchmark' },
      description:{ ko: '다중 모델 FPS 성능 비교', en: 'Multi-model FPS performance comparison', ja: '複数モデルのFPS性能比較', 'zh-CN': '多模型FPS性能对比', 'zh-TW': '多模型FPS效能對比', es: 'Comparación de rendimiento FPS con varios modelos' },
      prerequisite:'setup',
      beforeStart:function(){ goPage('bench'); },
      steps:[
        { target:'.bench-left', position:'right',
          title:{ ko: '벤치마크 설정', en: 'Benchmark Settings', ja: 'ベンチマーク設定', 'zh-CN': '基准测试设置', 'zh-TW': '基準測試設定', es: 'Configuración de Benchmark' },
          content:{ ko: '좌측 패널에서 <strong>카테고리, 언어(C++/Python), 실행 모드, 입력 타입</strong>을 설정합니다. 아래에서 <strong>Loop Count</strong>(반복 횟수)를 지정하세요. 높을수록 정확한 FPS 측정이 가능합니다.', en: 'Set <strong>category, language, mode, input type</strong> in the left panel. Set <strong>Loop Count</strong> below for iterations. Higher = more accurate FPS.', ja: '左パネルで<strong>カテゴリ、言語、モード、入力タイプ</strong>を設定します。下部で<strong>Loop Count</strong>（繰り返し回数）を指定します。値が大きいほど正確なFPS測定が可能です。', 'zh-CN': '在左侧面板设置<strong>分类、语言、模式、输入类型</strong>。在下方设置<strong>Loop Count</strong>循环次数。值越高FPS测量越准确。', 'zh-TW': '在左側面板設定<strong>分類、語言、模式、輸入類型</strong>。在下方設定<strong>Loop Count</strong>循環次數。值越高FPS測量越準確。', es: 'Configure <strong>categoría, idioma, modo y tipo de entrada</strong> en el panel izquierdo. Establezca <strong>Loop Count</strong> abajo para las iteraciones. Un valor más alto = FPS más preciso.' } },
        { target:'#b-cat', position:'right',
          title:{ ko: '카테고리 필터', en: 'Category Filter', ja: 'カテゴリフィルタ', 'zh-CN': '分类筛选', 'zh-TW': '分類篩選', es: 'Filtro de categoría' },
          content:{ ko: '벤치마크할 모델의 <strong>AI 태스크 카테고리</strong>를 선택합니다. 선택에 따라 우측 모델 테이블이 해당 카테고리 모델만 표시합니다.', en: 'Select <strong>AI task category</strong> for benchmarking. The model table on the right filters to show only matching models.', ja: 'ベンチマーク対象の<strong>AIタスクカテゴリ</strong>を選択します。右側のモデルテーブルが該当カテゴリのモデルのみ表示されます。', 'zh-CN': '选择基准测试的<strong>AI任务分类</strong>。右侧模型列表将筛选显示匹配的模型。', 'zh-TW': '選擇基準測試的<strong>AI任務分類</strong>。右側模型列表將篩選顯示匹配的模型。', es: 'Seleccione la <strong>categoría de tarea de IA</strong> para el benchmark. La tabla de modelos a la derecha se filtra para mostrar solo los modelos coincidentes.' } },
        { target:'#b-input-type', position:'right',
          title:{ ko: '입력 타입 선택', en: 'Input Type', ja: '入力タイプ', 'zh-CN': '输入类型', 'zh-TW': '輸入類型', es: 'Tipo de entrada' },
          content:{ ko: '<strong>🖼 Image, 🎬 Video, 📹 Camera, 📡 RTSP</strong> 중 벤치마크 입력 소스를 선택합니다. Image 모드에서는 Loop Count만큼 반복, Video 모드에서는 해당 프레임 수를 처리합니다.', en: 'Select benchmark input: <strong>🖼 Image, 🎬 Video, 📹 Camera, 📡 RTSP</strong>. Image mode repeats Loop Count times; Video mode processes that many frames.', ja: 'ベンチマーク入力を選択：<strong>🖼 Image、🎬 Video、📹 Camera、📡 RTSP</strong>。Imageモードではループ回数分繰り返し、Videoモードではそのフレーム数を処理します。', 'zh-CN': '选择基准测试输入：<strong>🖼 Image、🎬 Video、📹 Camera、📡 RTSP</strong>。Image模式重复Loop Count次；Video模式处理对应帧数。', 'zh-TW': '選擇基準測試輸入：<strong>🖼 Image、🎬 Video、📹 Camera、📡 RTSP</strong>。Image模式重複Loop Count次；Video模式處理對應幀數。', es: 'Seleccione la entrada del benchmark: <strong>🖼 Imagen, 🎬 Video, 📹 Camera, 📡 RTSP</strong>. En modo imagen, repite Loop Count veces; en modo video, procesa esa cantidad de fotogramas.' } },
        { target:'#b-loop', position:'right',
          title:{ ko: 'Loop Count (반복 횟수)', en: 'Loop Count', ja: 'ループ回数', 'zh-CN': '循环次数', 'zh-TW': '循環次數', es: 'Recuento de bucles' },
          content:{ ko: '추론을 반복 실행할 횟수입니다. 기본값 <strong>100</strong>이면 모델당 100번 추론 후 평균 FPS를 계산합니다. Image 입력 시 반복 횟수, Video 입력 시 프레임 수로 동작합니다.', en: 'Number of inference iterations. Default <strong>100</strong> = run 100 inferences per model and average FPS. For video, processes that many frames.', ja: '推論の繰り返し回数です。デフォルト<strong>100</strong> = モデルごとに100回推論を実行し、平均FPSを算出します。ビデオの場合はそのフレーム数を処理します。', 'zh-CN': '推理迭代次数。默认<strong>100</strong> = 每个模型运行100次推理并计算平均FPS。视频模式处理对应帧数。', 'zh-TW': '推論迭代次數。預設<strong>100</strong> = 每個模型執行100次推論並計算平均FPS。影片模式處理對應幀數。', es: 'Número de iteraciones de inferencia. Predeterminado <strong>100</strong> = 100 inferencias por modelo y FPS promedio. En video, procesa esa cantidad de fotogramas.' } },
        { target:'#bench-sel', position:'left',
          title:{ ko: '모델 선택 테이블', en: 'Model Selection Table', ja: 'モデル選択テーブル', 'zh-CN': '模型选择列表', 'zh-TW': '模型選擇列表', es: 'Tabla de selección de modelos' },
          content:{ ko: '우측 테이블에서 <strong>벤치마크할 모델을 체크박스로 선택</strong>합니다. <strong>☑ All</strong>로 전체 선택, <strong>☐ None</strong>으로 전체 해제가 가능합니다.', en: '<strong>Select models to benchmark via checkboxes</strong> in the right table. <strong>☑ All</strong> to select all, <strong>☐ None</strong> to deselect.', ja: '右側テーブルで<strong>チェックボックスからベンチマーク対象モデルを選択</strong>します。<strong>☑ All</strong>で全選択、<strong>☐ None</strong>で全解除します。', 'zh-CN': '在右侧列表中<strong>通过复选框选择基准测试模型</strong>。<strong>☑ All</strong>全选，<strong>☐ None</strong>全部取消。', 'zh-TW': '在右側列表中<strong>透過勾選框選擇基準測試模型</strong>。<strong>☑ All</strong>全選，<strong>☐ None</strong>全部取消。', es: '<strong>Seleccione modelos para benchmark con casillas</strong> en la tabla derecha. <strong>☑ Todos</strong> para seleccionar todo, <strong>☐ Ninguno</strong> para deseleccionar.' } },
        { target:'#b-run-btn', position:'right',
          title:{ ko: '⏱️ Start Benchmark', en: '⏱️ Start Benchmark', ja: '⏱️ ベンチマーク開始', 'zh-CN': '⏱️ 开始基准测试', 'zh-TW': '⏱️ 開始基準測試', es: '⏱️ Iniciar Benchmark' },
          content:{ ko: '선택한 모델들에 대해 <strong>순차적으로 벤치마크를 실행</strong>합니다. 각 모델마다 지정된 횟수만큼 추론을 반복하고 FPS/Latency를 측정합니다.', en: '<strong>Runs benchmark sequentially</strong> on selected models. Each model runs specified iterations and measures FPS/Latency.', ja: '選択したモデルに対して<strong>順次ベンチマークを実行</strong>します。各モデルが指定回数の推論を実行し、FPS/レイテンシを測定します。', 'zh-CN': '对所选模型<strong>依次执行基准测试</strong>。每个模型运行指定次数并测量FPS/延迟。', 'zh-TW': '對所選模型<strong>依次執行基準測試</strong>。每個模型執行指定次數並測量FPS/延遲。', es: '<strong>Ejecuta el benchmark secuencialmente</strong> en los modelos seleccionados. Cada modelo ejecuta las iteraciones indicadas y mide FPS/Latency.' } },
        { target:'#b-result-card', position:'top',
          title:{ ko: '결과 확인 & Export', en: 'Results & Export', ja: '結果 & エクスポート', 'zh-CN': '结果与导出', 'zh-TW': '結果與匯出', es: 'Resultados y exportación' },
          content:{ ko: '벤치마크 완료 후 <strong>결과 테이블</strong>(모델별 FPS, Latency, Status)과 <strong>FPS 비교 차트</strong>가 하단에 표시됩니다. <strong>📄 Export Report</strong> 버튼으로 벤치마크 리포트를 다운로드할 수 있습니다.', en: 'After benchmarking, a <strong>results table</strong> (per-model FPS, Latency, Status) and <strong>FPS comparison chart</strong> appear below. Use <strong>📄 Export Report</strong> to download.', ja: 'ベンチマーク完了後、下部に<strong>結果テーブル</strong>（モデル別FPS、レイテンシ、ステータス）と<strong>FPS比較チャート</strong>が表示されます。<strong>📄 Export Report</strong>でダウンロードできます。', 'zh-CN': '基准测试完成后，下方显示<strong>结果表格</strong>（各模型FPS、延迟、状态）和<strong>FPS对比图表</strong>。使用<strong>📄 Export Report</strong>下载报告。', 'zh-TW': '基準測試完成後，下方顯示<strong>結果表格</strong>（各模型FPS、延遲、狀態）和<strong>FPS對比圖表</strong>。使用<strong>📄 Export Report</strong>下載報告。', es: 'Tras el benchmark, aparecen abajo una <strong>tabla de resultados</strong> (FPS, Latency y Status por modelo) y un <strong>gráfico comparativo de FPS</strong>. Utilice <strong>📄 Export Report</strong> para descargar.' },
          beforeStep: function() { var el = document.getElementById('b-result-card'); if (el) el.classList.remove('hidden'); } },
        { target:'#bench-chart', position:'top',
          title:{ ko: '📊 FPS 비교 차트', en: '📊 FPS Comparison Chart', ja: '📊 FPS 比較チャート', 'zh-CN': '📊 FPS 对比图表', 'zh-TW': '📊 FPS 對比圖表', es: '📊 Gráfico comparativo de FPS' },
          content:{ ko: '벤치마크 결과를 <strong>막대 차트</strong>로 시각화합니다. 모델별 FPS를 한눈에 비교하여 최적의 모델을 선택할 수 있습니다.', en: 'Visualizes benchmark results as a <strong>bar chart</strong>. Compare FPS across models at a glance to find the optimal one.', ja: 'ベンチマーク結果を<strong>棒グラフ</strong>で可視化します。モデル間のFPSを一目で比較し、最適なモデルを見つけることができます。', 'zh-CN': '以<strong>柱状图</strong>可视化基准测试结果。一目了然地对比各模型FPS，找到最佳模型。', 'zh-TW': '以<strong>柱狀圖</strong>視覺化基準測試結果。一目了然地對比各模型FPS，找到最佳模型。', es: 'Visualiza los resultados del benchmark como un <strong>gráfico de barras</strong>. Compare FPS entre modelos de un vistazo para encontrar el óptimo.' },
          beforeStep: function() { var el = document.getElementById('b-result-card'); if (el) el.classList.remove('hidden'); } },
        { target:'#b-stop-btn', position:'bottom',
          title:{ ko: '벤치마크 중단', en: 'Stop Benchmark', ja: 'ベンチマーク中断', 'zh-CN': '停止基准测试', 'zh-TW': '停止基準測試', es: 'Detener Benchmark' },
          content:{ ko: '벤치마크 실행 중 이 버튼을 클릭하면 <strong>현재 모델의 벤치마크를 중단</strong>합니다. 이미 완료된 모델의 결과는 유지됩니다.', en: 'Click to <strong>stop the current model\'s benchmark</strong>. Results for already completed models are preserved.', ja: 'クリックして<strong>現在のモデルのベンチマークを停止</strong>します。完了済みモデルの結果は保持されます。', 'zh-CN': '点击以<strong>停止当前模型的基准测试</strong>。已完成模型的结果会保留。', 'zh-TW': '點擊以<strong>停止當前模型的基準測試</strong>。已完成模型的結果會保留。', es: 'Haga clic para <strong>detener el benchmark del modelo actual</strong>. Se conservan los resultados de los modelos ya completados.' },
          beforeStep: function() { var el = document.getElementById('b-stop-btn'); if (el) el.classList.remove('hidden'); } },
      ]
    },

    { id:'compare', icon:'🔀',
      title:{ ko: '🔀 A/B Compare', en: '🔀 A/B Compare', ja: '🔀 A/B 比較', 'zh-CN': '🔀 A/B 对比', 'zh-TW': '🔀 A/B 對比', es: '🔀 A/B Compare' },
      description:{ ko: '2~8개 모델 동시 비교 실행', en: 'Run 2-8 models side by side', ja: '2〜8モデルの並列比較実行', 'zh-CN': '2-8个模型并排运行', 'zh-TW': '2-8個模型並排執行', es: 'Ejecute de 2 a 8 modelos en paralelo' },
      prerequisite:'setup',
      beforeStart:function(){ goPage('compare'); },
      steps:[
        { target:'#ab-cols', position:'bottom',
          title:{ ko: '슬롯 수 설정', en: 'Slot Count', ja: 'スロット数', 'zh-CN': '槽位数', 'zh-TW': '插槽數', es: 'Número de ranuras' },
          content:{ ko: '상단에서 <strong>슬롯 수(2/4/6/8)</strong>를 선택합니다. 슬롯이 많을수록 더 많은 모델을 동시에 비교할 수 있습니다.', en: 'Select <strong>slot count (2/4/6/8)</strong> at top. More slots = more simultaneous model comparisons.', ja: '上部で<strong>スロット数（2/4/6/8）</strong>を選択します。スロットが多いほどより多くのモデルを同時に比較できます。', 'zh-CN': '在顶部选择<strong>槽位数（2/4/6/8）</strong>。槽位越多可同时对比的模型越多。', 'zh-TW': '在頂部選擇<strong>插槽數（2/4/6/8）</strong>。插槽越多可同時對比的模型越多。', es: 'Seleccione el <strong>número de ranuras (2/4/6/8)</strong> arriba. Más ranuras = más comparaciones simultáneas de modelos.' } },
        { target:'#ab-itype', position:'bottom',
          title:{ ko: '입력 타입 & 공유 입력', en: 'Input Type & Shared Input', ja: '入力タイプ & 共有入力', 'zh-CN': '输入类型与共享输入', 'zh-TW': '輸入類型與共享輸入', es: 'Tipo de entrada y entrada compartida' },
          content:{ ko: '<strong>File, Camera, RTSP</strong> 중 입력 타입을 선택합니다. 모든 슬롯이 <strong>동일한 입력</strong>을 공유하여 공정한 비교가 가능합니다.', en: 'Select input type: <strong>File, Camera, RTSP</strong>. All slots share the <strong>same input</strong> for fair comparison.', ja: '入力タイプを選択：<strong>File、Camera、RTSP</strong>。公平な比較のため全スロットが<strong>同じ入力</strong>を共有します。', 'zh-CN': '选择输入类型：<strong>File、Camera、RTSP</strong>。所有槽位共享<strong>相同输入</strong>以确保公平对比。', 'zh-TW': '選擇輸入類型：<strong>File、Camera、RTSP</strong>。所有插槽共享<strong>相同輸入</strong>以確保公平對比。', es: 'Seleccione el tipo de entrada: <strong>File, Camera, RTSP</strong>. Todas las ranuras comparten la <strong>misma entrada</strong> para una comparación justa.' } },
        { target:'#ab-panels', position:'top',
          title:{ ko: '비교 슬롯 패널', en: 'Comparison Slot Panels', ja: '比較スロット パネル', 'zh-CN': '对比槽位面板', 'zh-TW': '對比插槽面板', es: 'Paneles de ranuras de comparación' },
          content:{ ko: '각 슬롯에서 <strong>카테고리와 모델을 개별적으로 선택</strong>합니다. 예를 들어 슬롯 A에 YOLOv5s, 슬롯 B에 YOLOv8n을 넣어 성능을 비교할 수 있습니다.', en: '<strong>Select category and model independently</strong> in each slot. e.g., Slot A = YOLOv5s, Slot B = YOLOv8n for comparison.', ja: '各スロットで<strong>カテゴリとモデルを個別に選択</strong>します。例：スロットA = YOLOv5s、スロットB = YOLOv8n で性能比較。', 'zh-CN': '在每个槽位中<strong>独立选择分类和模型</strong>。例如：槽位A = YOLOv5s，槽位B = YOLOv8n进行对比。', 'zh-TW': '在每個插槽中<strong>獨立選擇分類和模型</strong>。例如：插槽A = YOLOv5s，插槽B = YOLOv8n進行對比。', es: '<strong>Seleccione categoría y modelo de forma independiente</strong> en cada ranura. p. ej., Ranura A = YOLOv5s, Ranura B = YOLOv8n para comparar.' } },
        { target:'#ab-run-btn', position:'bottom',
          title:{ ko: '▶ Run All 실행', en: '▶ Run All', ja: '▶ 全て実行', 'zh-CN': '▶ 全部运行', 'zh-TW': '▶ 全部執行', es: '▶ Ejecutar todo' },
          content:{ ko: '<strong>▶ Run All</strong>을 클릭하면 모든 슬롯이 동시에 추론을 실행합니다. 각 슬롯에 결과 이미지와 FPS/Latency가 표시되어 시각적으로 비교할 수 있습니다.', en: 'Click <strong>▶ Run All</strong> to run all slots simultaneously. Each slot displays its result image and FPS/Latency for visual comparison.', ja: '<strong>▶ Run All</strong>をクリックして全スロットを同時に実行します。各スロットに結果画像とFPS/レイテンシが表示され、視覚的に比較できます。', 'zh-CN': '点击<strong>▶ Run All</strong>同时运行所有槽位。每个槽位显示结果图片和FPS/延迟以进行直观对比。', 'zh-TW': '點擊<strong>▶ Run All</strong>同時執行所有插槽。每個插槽顯示結果圖片和FPS/延遲以進行直觀對比。', es: 'Haga clic en <strong>▶ Run All</strong> para ejecutar todas las ranuras simultáneamente. Cada ranura muestra su imagen de resultado y FPS/Latency para comparación visual.' },
          beforeStep: function() { _scrollToTarget('#ab-cols'); } },
        { target:'#ab-compare-card', position:'top',
          title:{ ko: '📊 Performance Comparison', en: '📊 Performance Comparison', ja: '📊 性能比較', 'zh-CN': '📊 性能对比', 'zh-TW': '📊 效能對比', es: '📊 Comparación de rendimiento' },
          content:{ ko: '모든 슬롯 추론 완료 후 <strong>Performance Comparison 테이블</strong>이 나타납니다. 슬롯별 <strong>모델명, FPS, Latency</strong>를 직접 비교하여 최적의 모델을 판단하세요.', en: 'After all slots finish, a <strong>Performance Comparison table</strong> appears. Compare <strong>model name, FPS, Latency</strong> per slot to find the optimal model.', ja: '全スロットの完了後、<strong>Performance Comparison テーブル</strong>が表示されます。スロット別の<strong>モデル名、FPS、レイテンシ</strong>を比較して最適なモデルを判断します。', 'zh-CN': '所有槽位完成后出现<strong>性能对比表</strong>。对比各槽位的<strong>模型名称、FPS、延迟</strong>以找到最佳模型。', 'zh-TW': '所有插槽完成後出現<strong>效能對比表</strong>。對比各插槽的<strong>模型名稱、FPS、延遲</strong>以找到最佳模型。', es: 'Cuando todas las ranuras terminan, aparece una <strong>tabla de comparación de rendimiento</strong>. Compare <strong>nombre del modelo, FPS y Latency</strong> por ranura para encontrar el modelo óptimo.' },
          beforeStep: function() { var el = document.getElementById('ab-compare-card'); if (el) el.classList.remove('hidden'); } },
      ]
    },

    { id:'modelzoo', icon:'📥',
      title:{ ko: '📥 ModelZoo', en: '📥 ModelZoo', ja: '📥 ModelZoo', 'zh-CN': '📥 ModelZoo', 'zh-TW': '📥 ModelZoo', es: '📥 ModelZoo' },
      description:{ ko: 'AI 모델 검색 및 다운로드', en: 'Browse and download AI models', ja: 'AIモデルの検索とダウンロード', 'zh-CN': '浏览和下载AI模型', 'zh-TW': '瀏覽和下載AI模型', es: 'Explore y descargue modelos de IA' },
      beforeStart:function(){ goPage('modelzoo'); },
      steps:[
        { target:'#mz-source', position:'right',
          title:{ ko: '소스 선택', en: 'Source Selection', ja: 'ソース選択', 'zh-CN': '源选择', 'zh-TW': '來源選擇', es: 'Selección de origen' },
          content:{ ko: '<strong>🔒 Internal</strong>: 사내 폐쇄망 모델 저장소. <strong>🌐 Public</strong>: 공개 모델 저장소. 네트워크 환경에 따라 소스를 선택하세요.', en: '<strong>🔒 Internal</strong>: Private model repository. <strong>🌐 Public</strong>: Public model repo. Select based on network environment.', ja: '<strong>🔒 Internal</strong>：プライベートモデルリポジトリ。<strong>🌐 Public</strong>：公開モデルリポジトリ。ネットワーク環境に応じて選択してください。', 'zh-CN': '<strong>🔒 Internal</strong>：私有模型仓库。<strong>🌐 Public</strong>：公开模型仓库。根据网络环境选择。', 'zh-TW': '<strong>🔒 Internal</strong>：私有模型儲存庫。<strong>🌐 Public</strong>：公開模型儲存庫。依網路環境選擇。', es: '<strong>🔒 Internal</strong>: repositorio privado de modelos. <strong>🌐 Public</strong>: repositorio público. Seleccione según el entorno de red.' } },
        { target:'#mz-task-chips', position:'bottom',
          title:{ ko: '태스크 필터', en: 'Task Filter', ja: 'タスクフィルタ', 'zh-CN': '任务筛选', 'zh-TW': '任務篩選', es: 'Filtro de tarea' },
          content:{ ko: '<strong>Detection, Classification, Segmentation, Pose</strong> 등 태스크 유형별로 모델을 필터링합니다.', en: 'Filter models by task type: <strong>Detection, Classification, Segmentation, Pose</strong>, etc.', ja: 'タスクタイプでモデルをフィルタリング：<strong>Detection、Classification、Segmentation、Pose</strong>等。', 'zh-CN': '按任务类型筛选模型：<strong>Detection、Classification、Segmentation、Pose</strong>等。', 'zh-TW': '按任務類型篩選模型：<strong>Detection、Classification、Segmentation、Pose</strong>等。', es: 'Filtre modelos por tipo de tarea: <strong>Detection, Classification, Segmentation, Pose</strong>, etc.' } },
        { target:'#mz-search', position:'bottom',
          title:{ ko: '모델 검색', en: 'Model Search', ja: 'モデル検索', 'zh-CN': '模型搜索', 'zh-TW': '模型搜尋', es: 'Búsqueda de modelos' },
          content:{ ko: '모델 이름으로 <strong>실시간 검색</strong>합니다.', en: '<strong>Real-time search</strong> by model name.', ja: 'モデル名による<strong>リアルタイム検索</strong>。', 'zh-CN': '按模型名称<strong>实时搜索</strong>。', 'zh-TW': '按模型名稱<strong>即時搜尋</strong>。', es: '<strong>Búsqueda en tiempo real</strong> por nombre de modelo.' } },
        { target:'#mz-table', position:'right',
          title:{ ko: '모델 테이블', en: 'Model Table', ja: 'モデルテーブル', 'zh-CN': '模型列表', 'zh-TW': '模型列表', es: 'Tabla de modelos' },
          content:{ ko: '각 모델의 <strong>태스크, 이름, 클래스, 데이터셋, 입력 크기, 파라미터 수, 라이선스, 정확도</strong>를 확인합니다. <strong>Q-Lite/Q-Pro</strong> 두 가지 양자화 버전의 DXNN과 JSON config를 개별 다운로드할 수 있습니다.', en: 'View each model\'s <strong>task, name, class, dataset, input size, params, license, accuracy</strong>. Download <strong>Q-Lite/Q-Pro</strong> DXNN and JSON config individually.', ja: '各モデルの<strong>タスク、名前、クラス、データセット、入力サイズ、パラメータ数、ライセンス、精度</strong>を確認します。<strong>Q-Lite/Q-Pro</strong>のDXNNとJSON設定を個別にダウンロードできます。', 'zh-CN': '查看各模型的<strong>任务、名称、类别、数据集、输入尺寸、参数量、许可证、精度</strong>。可单独下载<strong>Q-Lite/Q-Pro</strong> DXNN和JSON配置。', 'zh-TW': '檢視各模型的<strong>任務、名稱、類別、資料集、輸入尺寸、參數量、授權、準確度</strong>。可單獨下載<strong>Q-Lite/Q-Pro</strong> DXNN和JSON設定。', es: 'Consulte la <strong>tarea, nombre, clase, conjunto de datos, tamaño de entrada, parámetros, licencia y precisión</strong> de cada modelo. Descargue individualmente el DXNN <strong>Q-Lite/Q-Pro</strong> y la configuración JSON.' } },
        { target:'#mz-cart', position:'top',
          title:{ ko: '장바구니 & 일괄 다운로드', en: 'Cart & Batch Download', ja: 'カート & 一括ダウンロード', 'zh-CN': '购物车与批量下载', 'zh-TW': '購物車與批次下載', es: 'Carrito y descarga por lotes' },
          content:{ ko: '모델 체크박스를 선택하면 하단에 <strong>장바구니 바</strong>가 나타납니다. <strong>☑ Select All, 🆕 New Only, Q-Lite All, Q-Pro All</strong> 버튼으로 빠르게 선택하고, 장바구니에서 <strong>일괄 다운로드</strong>를 실행하세요. 다운로드 진행률이 표시됩니다.', en: 'Check model checkboxes to show the <strong>cart bar</strong> at bottom. Use <strong>☑ Select All, 🆕 New Only, Q-Lite All, Q-Pro All</strong> for quick selection, then <strong>batch download</strong> from cart.', ja: 'モデルのチェックボックスを選択すると下部に<strong>カートバー</strong>が表示されます。<strong>☑ Select All、🆕 New Only、Q-Lite All、Q-Pro All</strong>で素早く選択し、カートから<strong>一括ダウンロード</strong>します。', 'zh-CN': '勾选模型复选框后底部显示<strong>购物车栏</strong>。使用<strong>☑ Select All、🆕 New Only、Q-Lite All、Q-Pro All</strong>快速选择，然后从购物车<strong>批量下载</strong>。', 'zh-TW': '勾選模型勾選框後底部顯示<strong>購物車列</strong>。使用<strong>☑ Select All、🆕 New Only、Q-Lite All、Q-Pro All</strong>快速選擇，然後從購物車<strong>批次下載</strong>。', es: 'Marque las casillas de modelos para mostrar la <strong>barra del carrito</strong> abajo. Utilice <strong>☑ Seleccionar todo, 🆕 Solo nuevos, Q-Lite All, Q-Pro All</strong> para selección rápida y luego <strong>descarga por lotes</strong> desde el carrito.' },
          beforeStep: function() { _prepModelzooCartDemo(); },
          afterStep: function() { _clearModelzooCartDemo(); } },
      ]
    },

    { id:'compiler', icon:'🛠️',
      title:{ ko: '🛠️ Compiler', en: '🛠️ Compiler', ja: '🛠️ Compiler', 'zh-CN': '🛠️ Compiler', 'zh-TW': '🛠️ Compiler', es: '🛠️ Compiler' },
      description:{ ko: 'Launcher의 Compiler 모듈에서 ONNX→DXNN 변환', en: 'Convert ONNX→DXNN in the Launcher Compiler module', ja: 'LauncherのCompilerモジュールでONNX→DXNN変換', 'zh-CN': '在 Launcher 的 Compiler 模块中转换 ONNX→DXNN', 'zh-TW': '在 Launcher 的 Compiler 模組中轉換 ONNX→DXNN', es: 'Convierta ONNX→DXNN en el módulo Compiler del Launcher' },
      prerequisite:'setup',
      prerequisiteMessage:{ ko: '먼저 Setup에서 런타임 의존성을 설치하세요.', en: 'Install runtime dependencies in Setup first.', ja: 'まずセットアップでランタイム依存関係をインストールしてください。', 'zh-CN': '请先在设置中安装运行时依赖项。', 'zh-TW': '請先在設定中安裝執行環境依賴項。', es: 'Instale primero las dependencias de runtime en Configuración.' },
      beforeStart:function(){ goPage('reference'); },
      steps:[
        { target:'#ref-filter-bar', position:'bottom',
          title:{ ko: 'Compiler Reference', en: 'Compiler Reference', ja: 'Compiler Reference', 'zh-CN': 'Compiler 参考', 'zh-TW': 'Compiler 參考', es: 'Referencia Compiler' },
          content:{ ko: 'Reference 필터에서 <strong>Compiler</strong> 칩을 선택하면 DX-COM 설치·ONNX 그래프·컴파일 워크플로우 문서를 볼 수 있습니다. 실제 GUI는 Launcher 상단 <strong>Compiler</strong> 탭에서 실행합니다.', en: 'Select the <strong>Compiler</strong> chip in Reference filters for DX-COM setup, ONNX graph, and compile workflow docs. Run the full GUI from the Launcher <strong>Compiler</strong> tab.', ja: 'Referenceフィルタで<strong>Compiler</strong>チップを選ぶと、DX-COMセットアップ・ONNXグラフ・コンパイルワークフローのドキュメントが表示されます。実際のGUIはLauncher上部の<strong>Compiler</strong>タブから起動します。', 'zh-CN': '在 Reference 筛选中选择 <strong>Compiler</strong> 标签可查看 DX-COM 安装、ONNX 图和编译流程文档。完整 GUI 请从 Launcher 顶部 <strong>Compiler</strong> 选项卡启动。', 'zh-TW': '在 Reference 篩選中選擇 <strong>Compiler</strong> 標籤可查看 DX-COM 安裝、ONNX 圖和編譯流程文件。完整 GUI 請從 Launcher 頂部 <strong>Compiler</strong> 標籤啟動。', es: 'Seleccione el chip <strong>Compiler</strong> en los filtros Reference para documentación de DX-COM, gráfico ONNX y flujo de compilación. Ejecute la GUI completa desde la pestaña <strong>Compiler</strong> del Launcher.' } },
        { target:'#ref-content', position:'top',
          title:{ ko: 'Compiler 워크플로우', en: 'Compiler Workflow', ja: 'Compilerワークフロー', 'zh-CN': 'Compiler 工作流', 'zh-TW': 'Compiler 工作流程', es: 'Flujo Compiler' },
          content:{ ko: 'DX App에서는 모델 그래프(📊 Graph) 버튼으로 Compiler viewer를 열 수 있습니다. ONNX 업로드 → config → compile → .dxnn 출력은 <strong>Compiler 모듈</strong>에서 수행하세요.', en: 'In DX App, the 📊 Graph button opens the Compiler viewer for ONNX models. Upload ONNX → configure → compile → .dxnn output happens in the dedicated <strong>Compiler module</strong>.', ja: 'DX Appでは📊 GraphボタンでCompilerビューアを開けます。ONNXアップロード→設定→コンパイル→.dxnn出力は<strong>Compilerモジュール</strong>で行います。', 'zh-CN': '在 DX App 中，📊 Graph 按钮可为 ONNX 模型打开 Compiler 查看器。ONNX 上传→配置→编译→.dxnn 输出请在<strong>Compiler 模块</strong>中完成。', 'zh-TW': '在 DX App 中，📊 Graph 按鈕可為 ONNX 模型開啟 Compiler 檢視器。ONNX 上傳→設定→編譯→.dxnn 輸出請在<strong>Compiler 模組</strong>中完成。', es: 'En DX App, el botón 📊 Graph abre el visor Compiler para modelos ONNX. La carga ONNX → configuración → compilación → salida .dxnn ocurre en el <strong>módulo Compiler</strong> dedicado.' } },
      ]
    },

    { id:'outputs', icon:'📁',
      title:{ ko: '📁 Outputs', en: '📁 Outputs', ja: '📁 出力ファイル', 'zh-CN': '📁 输出文件', 'zh-TW': '📁 輸出檔案', es: '📁 Outputs' },
      description:{ ko: '추론 결과 파일 확인 및 다운로드', en: 'View and download inference output files', ja: '推論出力ファイルの確認とダウンロード', 'zh-CN': '查看和下载推理输出文件', 'zh-TW': '檢視和下載推論輸出檔案', es: 'Ver y descargar archivos de salida de inferencia' },
      beforeStart:function(){ goPage('outputs'); _closeLightbox(); },
      steps:[
        { target:'.out-toolbar', position:'bottom',
          title:{ ko: '도구 모음 & 뷰 전환', en: 'Toolbar & View Toggle', ja: 'ツールバー & ビュー切替', 'zh-CN': '工具栏与视图切换', 'zh-TW': '工具列與檢視切換', es: 'Barra de herramientas y cambio de vista' },
          content:{ ko: '상단 도구 모음에서 <strong>📊 Table</strong>과 <strong>🖼 Grid</strong> 뷰를 전환합니다. Grid 뷰는 이미지/비디오 썸네일을 보여주고, Table 뷰는 상세 정보 목록을 표시합니다.', en: 'Switch between <strong>📊 Table</strong> and <strong>🖼 Grid</strong> views in the toolbar. Grid shows thumbnails; Table shows detailed file listings.', ja: 'ツールバーで<strong>📊 Table</strong>と<strong>🖼 Grid</strong>ビューを切り替えます。Gridはサムネイル表示、Tableは詳細ファイル一覧を表示します。', 'zh-CN': '在工具栏中切换<strong>📊 Table</strong>和<strong>🖼 Grid</strong>视图。Grid显示缩略图；Table显示详细文件列表。', 'zh-TW': '在工具列中切換<strong>📊 Table</strong>和<strong>🖼 Grid</strong>檢視。Grid顯示縮圖；Table顯示詳細檔案列表。', es: 'Cambie entre vistas <strong>📊 Table</strong> y <strong>🖼 Grid</strong> en la barra de herramientas. Grid muestra miniaturas; Table muestra listados detallados de archivos.' } },
        { target:'#out-filters', position:'bottom',
          title:{ ko: '파일 타입 필터', en: 'File Type Filters', ja: 'ファイルタイプ フィルタ', 'zh-CN': '文件类型筛选', 'zh-TW': '檔案類型篩選', es: 'Filtros por tipo de archivo' },
          content:{ ko: '<strong>이미지, 비디오, 아카이브(ZIP)</strong> 등 파일 타입별로 필터링합니다. 특정 유형의 출력 파일만 빠르게 찾을 수 있습니다.', en: 'Filter by file type: <strong>images, videos, archives (ZIP)</strong>. Quickly find specific output file types.', ja: 'ファイルタイプでフィルタリング：<strong>画像、ビデオ、アーカイブ（ZIP）</strong>。特定の出力ファイルタイプを素早く見つけることができます。', 'zh-CN': '按文件类型筛选：<strong>图片、视频、压缩包（ZIP）</strong>。快速查找特定输出文件类型。', 'zh-TW': '按檔案類型篩選：<strong>圖片、影片、壓縮檔（ZIP）</strong>。快速查找特定輸出檔案類型。', es: 'Filtre por tipo de archivo: <strong>imágenes, videos, archivos (ZIP)</strong>. Encuentre rápidamente tipos concretos de archivos de salida.' } },
        { target:'#out-gallery', position:'top',
          title:{ ko: '갤러리 그리드', en: 'Gallery Grid', ja: 'ギャラリー グリッド', 'zh-CN': '图库网格', 'zh-TW': '圖庫網格', es: 'Cuadrícula de galería' },
          content:{ ko: 'Grid 뷰에서 출력 파일이 <strong>카드 형태의 썸네일</strong>로 표시됩니다. 카드를 클릭하면 Lightbox 미리보기가 열립니다. 각 카드에 <strong>📥 다운로드</strong> 버튼이 있습니다.', en: 'In Grid view, output files appear as <strong>thumbnail cards</strong>. Click a card for Lightbox preview. Each card has a <strong>📥 download</strong> button.', ja: 'Gridビューでは出力ファイルが<strong>サムネイルカード</strong>として表示されます。カードをクリックするとLightboxプレビューが開きます。各カードに<strong>📥 ダウンロード</strong>ボタンがあります。', 'zh-CN': '在Grid视图中，输出文件以<strong>缩略图卡片</strong>形式显示。点击卡片打开Lightbox预览。每张卡片有<strong>📥 下载</strong>按钮。', 'zh-TW': '在Grid檢視中，輸出檔案以<strong>縮圖卡片</strong>形式顯示。點擊卡片開啟Lightbox預覽。每張卡片有<strong>📥 下載</strong>按鈕。', es: 'En vista Grid, los archivos de salida aparecen como <strong>tarjetas con miniatura</strong>. Haga clic en una tarjeta para vista previa Lightbox. Cada tarjeta tiene un botón de <strong>📥 descarga</strong>.' } },
        { target:'#out-table', position:'bottom',
          title:{ ko: '출력 파일 테이블', en: 'Output Files Table', ja: '出力ファイル テーブル', 'zh-CN': '输出文件列表', 'zh-TW': '輸出檔案列表', es: 'Tabla de archivos de salida' },
          content:{ ko: 'Run Inference, Benchmark, A/B Compare, Export Package에서 생성된 <strong>모든 출력 파일</strong>(이미지, 비디오, 리포트, 패키지)을 확인합니다. 각 파일의 <strong>크기, 수정 시간</strong>이 표시되며, 우측 버튼으로 <strong>다운로드</strong>할 수 있습니다.', en: 'View <strong>all output files</strong> (images, videos, reports, packages) from Run Inference, Benchmark, Compare, Export. Shows <strong>size, modified time</strong>, with <strong>download</strong> buttons.', ja: 'Run Inference、Benchmark、Compare、Exportからの<strong>全出力ファイル</strong>（画像、ビデオ、レポート、パッケージ）を確認します。<strong>サイズ、更新時間</strong>が表示され、<strong>ダウンロード</strong>ボタンがあります。', 'zh-CN': '查看来自Run Inference、Benchmark、Compare、Export的<strong>所有输出文件</strong>（图片、视频、报告、包）。显示<strong>大小、修改时间</strong>，带<strong>下载</strong>按钮。', 'zh-TW': '檢視來自Run Inference、Benchmark、Compare、Export的<strong>所有輸出檔案</strong>（圖片、影片、報告、套件）。顯示<strong>大小、修改時間</strong>，帶<strong>下載</strong>按鈕。', es: 'Vea <strong>todos los archivos de salida</strong> (imágenes, videos, informes, paquetes) de Run Inference, Benchmark, Compare y Export. Muestra <strong>tamaño y hora de modificación</strong>, con botones de <strong>descarga</strong>.' },
          beforeStep: function() { if (typeof setOutView === 'function') setOutView('table'); } },
        { target:'#gallery-lightbox', position:'right',
          title:{ ko: '🔍 Lightbox 미리보기', en: '🔍 Lightbox Preview', ja: '🔍 Lightbox プレビュー', 'zh-CN': '🔍 Lightbox 预览', 'zh-TW': '🔍 Lightbox 預覽', es: '🔍 Vista previa Lightbox' },
          content:{ ko: '이미지/비디오를 클릭하면 <strong>전체 화면 Lightbox</strong>가 열립니다. <strong>📥 다운로드</strong>와 <strong>Before/After 비교</strong>로 원본과 결과를 비교할 수 있습니다.', en: 'Click an image/video to open <strong>full-screen Lightbox</strong>. Use <strong>📥 Download</strong> and <strong>Before/After Compare</strong> to overlay-compare original and result.', ja: '画像/ビデオをクリックして<strong>フルスクリーンLightbox</strong>を開きます。<strong>📥 ダウンロード</strong>と<strong>Before/After Compare</strong>ボタンで比較できます。', 'zh-CN': '点击图片/视频打开<strong>全屏Lightbox</strong>。使用<strong>📥 下载</strong>和<strong>Before/After Compare</strong>对比原图和结果。', 'zh-TW': '點擊圖片/影片開啟<strong>全螢幕Lightbox</strong>。使用<strong>📥 下載</strong>和<strong>Before/After Compare</strong>對比原圖和結果。', es: 'Haga clic en una imagen/video para abrir <strong>Lightbox a pantalla completa</strong>. Utilice <strong>📥 Download</strong> y <strong>Before/After Compare</strong> para comparar original y resultado.' },
          beforeStep:function(){ if (typeof setOutView === 'function') setOutView('grid'); _mockLightbox(); },
          afterStep:function(){ _closeLightbox(); } },
      ]
    },

    { id:'global', icon:'🌐',
      title:{ ko: '🌐 글로벌 UI 요소', en: '🌐 Global UI Elements', ja: '🌐 グローバルUI要素', 'zh-CN': '🌐 全局UI元素', 'zh-TW': '🌐 全域UI元素', es: '🌐 Elementos globales de la interfaz' },
      description:{ ko: '사이드바, 상단 바, 알림, NPU 모니터 등', en: 'Sidebar, top bar, notifications, NPU monitor', ja: 'サイドバー、トップバー、通知、NPUモニター', 'zh-CN': '侧边栏、顶部栏、通知、NPU监控', 'zh-TW': '側邊欄、頂部列、通知、NPU監控', es: 'Barra lateral, barra superior, notificaciones, monitor NPU' },
      beforeStart:function(){ _closeLightbox(); _closeNotifDrawer(); _closeChatWindow(); },
      steps:[
        { target:'#sidebar', position:'right',
          title:{ ko: '사이드바 네비게이션', en: 'Sidebar Navigation', ja: 'サイドバー ナビゲーション', 'zh-CN': '侧边栏导航', 'zh-TW': '側邊欄導覽', es: 'Navegación de barra lateral' },
          content:{ ko: '좌측 사이드바에서 모든 페이지(Setup, Models, Run, Bench, Compare, ModelZoo, Compiler, Outputs, Reference)로 이동합니다. <strong>☰ 버튼</strong>으로 접기/펼치기가 가능합니다.', en: 'Navigate to all pages from the left sidebar. Use <strong>☰ button</strong> to collapse/expand.', ja: '左サイドバーからすべてのページに移動できます。<strong>☰ ボタン</strong>で折りたたみ/展開が可能です。', 'zh-CN': '从左侧边栏导航到所有页面。使用<strong>☰ 按钮</strong>折叠/展开。', 'zh-TW': '從左側邊欄導覽至所有頁面。使用<strong>☰ 按鈕</strong>折疊/展開。', es: 'Navegue a todas las páginas desde la barra lateral izquierda. Utilice el <strong>botón ☰</strong> para contraer/expandir.' } },
        { target:'.topbar', position:'bottom',
          title:{ ko: '상단 바', en: 'Top Bar', ja: 'トップバー', 'zh-CN': '顶部栏', 'zh-TW': '頂部列', es: 'Barra superior' },
          content:{ ko: '<strong>현재 페이지 제목</strong>, <strong>NPU 온도</strong>, <strong>메모리 사용량</strong> 등이 표시됩니다. 우측 공유 툴바에서 언어·튜토리얼을 사용합니다.', en: 'Shows the <strong>page title</strong>, <strong>NPU temperature</strong>, and <strong>memory usage</strong>. Use language and tutorial from the shared toolbar on the right.', ja: '<strong>ページタイトル</strong>、<strong>NPU温度</strong>、<strong>メモリ使用量</strong>などが表示されます。右の共通ツールバーで言語・チュートリアルを利用します。', 'zh-CN': '显示<strong>页面标题</strong>、<strong>NPU温度</strong>和<strong>内存使用</strong>。使用右侧共享工具栏的语言和教程。', 'zh-TW': '顯示<strong>頁面標題</strong>、<strong>NPU溫度</strong>和<strong>記憶體使用</strong>。使用右側共用工具列的語言與教學。', es: 'Muestra el <strong>título de página</strong>, <strong>temperatura NPU</strong> y <strong>uso de memoria</strong>. Use idioma y tutorial desde la barra compartida a la derecha.' } },
        { target:'#dxToolbar', position:'bottom',
          title:{ ko: '공유 툴바', en: 'Shared Toolbar', ja: '共通ツールバー', 'zh-CN': '共享工具栏', 'zh-TW': '共用工具列', es: 'Barra de herramientas compartida' },
          content:{ ko: '<strong>🌏 언어</strong>, <strong>🎓 튜토리얼</strong> 버튼이 모든 페이지에서 동일하게 동작합니다. 언어 메뉴는 드롭다운으로 열리며 튜토리얼 중에는 자동으로 닫힙니다.', en: 'The <strong>🌏 language</strong> and <strong>🎓 tutorial</strong> buttons work the same on every page. The language menu opens as a dropdown and closes automatically during tutorial steps.', ja: '<strong>🌏言語</strong>、<strong>🎓チュートリアル</strong>ボタンは全ページで同じように動作します。言語メニューはドロップダウンで開き、チュートリアル中は自動的に閉じます。', 'zh-CN': '<strong>🌏语言</strong>和<strong>🎓教程</strong>按钮在所有页面行为一致。语言菜单以下拉方式打开，教程步骤中会自动关闭。', 'zh-TW': '<strong>🌏語言</strong>和<strong>🎓教學</strong>按鈕在所有頁面行為一致。語言選單以下拉方式開啟，教學步驟中會自動關閉。', es: 'Los botones <strong>🌏 idioma</strong> y <strong>🎓 tutorial</strong> funcionan igual en todas las páginas. El menú de idioma se abre como desplegable y se cierra automáticamente durante el tutorial.' },
          beforeStep: function() {
            var el = document.getElementById('dxToolbar') || document.getElementById('langToggle');
            if (el) el.scrollIntoView({ block: 'nearest', inline: 'nearest' });
          } },
        { target:'.notif-bell', position:'left',
          title:{ ko: '알림 벨', en: 'Notification Bell', ja: '通知ベル', 'zh-CN': '通知铃铛', 'zh-TW': '通知鈴鐺', es: 'Campana de notificaciones' },
          content:{ ko: '🔔 벨 아이콘을 클릭하면 <strong>알림 서랍</strong>이 열립니다. 시스템 경고, 설치 완료, 에러 등의 이력을 확인합니다.', en: 'Click the 🔔 bell to open the <strong>notification drawer</strong> with system alerts, install completions, and errors.', ja: '🔔ベルアイコンをクリックすると<strong>通知ドロワー</strong>が開きます。システム警告、インストール完了、エラーなどの履歴を確認できます。', 'zh-CN': '点击🔔铃铛打开<strong>通知抽屉</strong>，查看系统警告、安装完成和错误等历史。', 'zh-TW': '點擊🔔鈴鐺開啟<strong>通知抽屜</strong>，檢視系統警告、安裝完成和錯誤等歷史。', es: 'Haga clic en la campana 🔔 para abrir el <strong>cajón de notificaciones</strong> con alertas del sistema, instalaciones completadas y errores.' } },
        { target:'#notif-drawer', position:'left',
          title:{ ko: '알림 서랍', en: 'Notification Drawer', ja: '通知ドロワー', 'zh-CN': '通知抽屉', 'zh-TW': '通知抽屜', es: 'Panel de notificaciones' },
          content:{ ko: '시스템 경고, 설치 완료, 에러 발생 등의 <strong>알림 이력</strong>을 확인할 수 있습니다. 다음 단계로 넘어가면 자동으로 닫힙니다.', en: 'View <strong>notification history</strong> including system alerts, installation completions, and errors. Closes automatically when you advance.', ja: 'システム警告、インストール完了、エラーなどの<strong>通知履歴</strong>を確認できます。次のステップに進むと自動的に閉じます。', 'zh-CN': '查看<strong>通知历史</strong>，包括系统警告、安装完成和错误。进入下一步时自动关闭。', 'zh-TW': '檢視<strong>通知歷史</strong>，包括系統警告、安裝完成和錯誤。進入下一步時自動關閉。', es: 'Consulte el <strong>historial de notificaciones</strong>, incluidas alertas del sistema, instalaciones completadas y errores. Se cierra automáticamente al avanzar.' },
          beforeStep: function() {
            if (typeof toggleNotifDrawer === 'function') {
              var el = document.getElementById('notif-drawer');
              if (el && !el.classList.contains('open')) toggleNotifDrawer();
            }
          },
          afterStep: function() { _closeNotifDrawer(); } },
        { target:'#dxt-mock-toast', position:'top',
          title:{ ko: '알림 (Toast)', en: 'Notifications (Toast)', ja: '通知（トースト）', 'zh-CN': '通知（Toast）', 'zh-TW': '通知（Toast）', es: 'Notificaciones (Toast)' },
          content:{ ko: '작업 완료, 오류, 경고 등은 우하단에 <strong>토스트 알림</strong>으로 표시됩니다. 초록색=성공, 빨간색=오류, 노란색=경고. 3초 후 자동 사라집니다.', en: 'Action results appear as <strong>toast notifications</strong> at bottom-right. Green=success, Red=error, Yellow=warning. Auto-dismiss after 3s.', ja: '操作結果は右下に<strong>トースト通知</strong>として表示されます。緑=成功、赤=エラー、黄=警告。3秒後に自動消去されます。', 'zh-CN': '操作结果以<strong>Toast通知</strong>形式在右下角显示。绿色=成功，红色=错误，黄色=警告。3秒后自动消失。', 'zh-TW': '操作結果以<strong>Toast通知</strong>形式在右下角顯示。綠色=成功，紅色=錯誤，黃色=警告。3秒後自動消失。', es: 'Los resultados de acciones aparecen como <strong>notificaciones toast</strong> abajo a la derecha. Verde=éxito, Rojo=error, Amarillo=advertencia. Se cierran automáticamente tras 3 s.' },
          beforeStep: function() { _closeNotifDrawer(); _mockToast(); },
          afterStep: function() { _dismissMockToast(); } },
      ]
    },

    { id:'lab', icon:'🧪',
      title:{ ko: '🧪 Lab', en: '🧪 Lab', ja: '🧪 ラボ', 'zh-CN': '🧪 实验室', 'zh-TW': '🧪 實驗室', es: '🧪 Laboratorio' },
      description:{ ko: '모델·작업 확장, 실험, 안전한 변경 미리보기', en: 'Model/task extensions, experiments, and safe change previews', ja: 'モデル・タスク拡張、実験、安全な変更プレビュー', 'zh-CN': '模型/任务扩展、实验与安全变更预览', 'zh-TW': '模型/任務擴充、實驗與安全變更預覽', es: 'Extensiones de modelos/tareas, experimentos y vistas previas seguras' },
      beforeStart:function(){ goPage('lab'); if(typeof initLabPage==='function') initLabPage(); },
      steps:[
        { target:'#lab-home', position:'bottom',
          title:{ ko: 'Lab 홈 카드', en: 'Lab Home Cards', ja: 'Labホームカード', 'zh-CN': 'Lab 首页卡片', 'zh-TW': 'Lab 首頁卡片', es: 'Tarjetas de inicio Lab' },
          content:{ ko: '<strong>모델 추가, 작업 생성, 실험 실행, 생성 파일, 안전 센터</strong> 흐름을 선택합니다. 각 카드는 단계별 마법사로 안내합니다.', en: 'Choose flows for <strong>add model, create task, experiment, generated files, safety center</strong>. Each card opens a step-by-step wizard.', ja: '<strong>モデル追加、タスク作成、実験、生成ファイル、安全センター</strong>のフローを選択します。各カードはステップごとのウィザードを開きます。', 'zh-CN': '选择<strong>添加模型、创建任务、实验、生成文件、安全中心</strong>流程。每张卡片打开分步向导。', 'zh-TW': '選擇<strong>新增模型、建立任務、實驗、產生檔案、安全中心</strong>流程。每張卡片開啟分步精靈。', es: 'Elija flujos para <strong>añadir modelo, crear tarea, experimento, archivos generados y centro de seguridad</strong>. Cada tarjeta abre un asistente paso a paso.' } },
        { target:'#lab-flow-root', position:'top',
          title:{ ko: 'Lab 마법사', en: 'Lab Wizard', ja: 'Labウィザード', 'zh-CN': 'Lab 向导', 'zh-TW': 'Lab 精靈', es: 'Asistente Lab' },
          content:{ ko: '선택한 흐름의 <strong>단계별 폼, 미리보기, 적용/롤백 안내</strong>가 이 영역에 렌더링됩니다.', en: 'The selected flow renders <strong>step forms, previews, and apply/rollback guidance</strong> in this area.', ja: '選択したフローの<strong>ステップフォーム、プレビュー、適用/ロールバック案内</strong>がこの領域に表示されます。', 'zh-CN': '所选流程在此区域渲染<strong>分步表单、预览以及应用/回滚指引</strong>。', 'zh-TW': '所選流程在此區域渲染<strong>分步表單、預覽以及套用/復原指引</strong>。', es: 'El flujo seleccionado muestra aquí <strong>formularios por pasos, vistas previas y guía de aplicar/revertir</strong>.' } },
        { target:'#lab-advanced-tools', position:'top',
          title:{ ko: '고급 도구', en: 'Advanced Tools', ja: '高度なツール', 'zh-CN': '高级工具', 'zh-TW': '進階工具', es: 'Herramientas avanzadas' },
          content:{ ko: 'Developer 모드의 <strong>모델 추가/삭제, 스켈레톤, Git 커밋, 패키지 추출</strong> 탭을 Lab 페이지에서 직접 사용합니다.', en: 'Use Developer tabs for <strong>add/delete model, skeleton, Git commit, package extract</strong> directly on the Lab page.', ja: 'Developerモードの<strong>モデル追加/削除、スケルトン、Gitコミット、パッケージ抽出</strong>タブをLabページで直接使用します。', 'zh-CN': '在 Lab 页面直接使用 Developer 的<strong>添加/删除模型、骨架、Git 提交、包提取</strong>选项卡。', 'zh-TW': '在 Lab 頁面直接使用 Developer 的<strong>新增/刪除模型、骨架、Git 提交、套件擷取</strong>分頁。', es: 'Use en la página Lab las pestañas Developer de <strong>añadir/eliminar modelo, skeleton, commit Git y extracción de paquetes</strong>.' } },
        { target:'.dev-tabs', position:'top',
          title:{ ko: 'Developer 탭', en: 'Developer Tabs', ja: 'Developerタブ', 'zh-CN': 'Developer 选项卡', 'zh-TW': 'Developer 分頁', es: 'Pestañas Developer' },
          content:{ ko: '고급 도구 영역에서 작업 유형별 탭을 전환합니다. 출력 로그는 각 패널 하단에 표시됩니다.', en: 'Switch task tabs in Advanced Tools. Output logs appear at the bottom of each panel.', ja: '高度なツール領域でタスク別タブを切り替えます。出力ログは各パネル下部に表示されます。', 'zh-CN': '在高级工具区域切换任务选项卡。输出日志显示在各面板底部。', 'zh-TW': '在進階工具區域切換任務分頁。輸出日誌顯示在各面板底部。', es: 'Cambie pestañas de tarea en Herramientas avanzadas. Los registros aparecen al final de cada panel.' } },
      ]
    },

    { id:'developer', icon:'🔧', helpOnly:true,
      title:{ ko: '🔧 Developer Mode', en: '🔧 Developer Mode', ja: '🔧 開発者モード', 'zh-CN': '🔧 开发者模式', 'zh-TW': '🔧 開發者模式', es: '🔧 Modo desarrollador' },
      steps:[] },
  ];

  /* ════════════════════════════════════════════════════════════
     HELP TOOLTIPS — per-page
     ════════════════════════════════════════════════════════════ */
/* ════════════════════════════════════════════════════════════
     REFERENCE DOCS
     ════════════════════════════════════════════════════════════ */
  var referenceDocs = [
    { id:'ref-setup', icon:'⚙️', title:{ ko: 'Setup & Install', en: 'Setup & Install', ja: 'セットアップ & インストール', 'zh-CN': '设置与安装', 'zh-TW': '設定與安裝', es: 'Configuración e instalación' },
      body:{ ko: '<p>5단계 초기 설정 (DX-COM Compiler는 Launcher Compiler 탭):</p><ul><li><strong>①</strong> DX-APP Dependencies — cmake, gcc, ninja, OpenCV 등</li><li><strong>②</strong> DX-APP Build — C++ Release 빌드</li><li><strong>③</strong> Sample Assets — 모델(.dxnn) + 데모 비디오</li><li><strong>④</strong> DX-Runtime Dependencies</li><li><strong>⑤</strong> NPU Driver — sudo 필요</li></ul><p>위→아래, 왼→오른쪽 순서. 로그창에서 실시간 확인.</p>', en: '<p>5-step setup (DX-COM Compiler is in the Launcher Compiler tab):</p><ul><li><strong>①</strong> DX-APP Dependencies</li><li><strong>②</strong> DX-APP Build</li><li><strong>③</strong> Sample Assets</li><li><strong>④</strong> DX-Runtime Deps</li><li><strong>⑤</strong> NPU Driver (sudo)</li></ul>', ja: '<p>5ステップのセットアップ（DX-COM CompilerはLauncher Compilerタブ）:</p><ul><li><strong>①</strong> DX-APP 依存関係</li><li><strong>②</strong> DX-APP ビルド</li><li><strong>③</strong> サンプルアセット</li><li><strong>④</strong> DX-Runtime 依存関係</li><li><strong>⑤</strong> NPUドライバ（sudo必要）</li></ul>', 'zh-CN': '<p>5步设置（DX-COM Compiler 在 Launcher Compiler 标签）:</p><ul><li><strong>①</strong> DX-APP 依赖项</li><li><strong>②</strong> DX-APP 构建</li><li><strong>③</strong> 示例资源</li><li><strong>④</strong> DX-Runtime 依赖项</li><li><strong>⑤</strong> NPU驱动（需sudo）</li></ul>', 'zh-TW': '<p>5步設定（DX-COM Compiler 在 Launcher Compiler 標籤）:</p><ul><li><strong>①</strong> DX-APP 依賴項</li><li><strong>②</strong> DX-APP 建置</li><li><strong>③</strong> 範例資源</li><li><strong>④</strong> DX-Runtime 依賴項</li><li><strong>⑤</strong> NPU驅動（需sudo）</li></ul>', es: '<p>Configuración en 5 pasos (DX-COM Compiler está en la pestaña Compiler del Launcher):</p><ul><li><strong>①</strong> Dependencias DX-APP</li><li><strong>②</strong> Compilación DX-APP</li><li><strong>③</strong> Recursos de muestra</li><li><strong>④</strong> Dependencias DX-Runtime</li><li><strong>⑤</strong> Controlador NPU (sudo)</li></ul>' } },
    { id:'ref-run', icon:'▶️', title:{ ko: 'Run Inference', en: 'Run Inference', ja: '推論実行', 'zh-CN': '运行推理', 'zh-TW': '執行推論', es: 'Ejecutar inferencia' },
      body:{ ko: '<ul><li><strong>Single</strong> — 이미지/비디오 1개 추론</li><li><strong>Continuous</strong> — 비디오/카메라/RTSP 연속 추론, 최대 8슬롯</li><li>파라미터: Confidence, NMS IoU, Top-K, Alpha</li><li>Export Package로 소스+모델 패키징</li></ul>', en: '<ul><li><strong>Single</strong> — one image/video</li><li><strong>Continuous</strong> — video/camera/RTSP, up to 8 slots</li><li>Params: Confidence, NMS, Top-K, Alpha</li><li>Export Package</li></ul>', ja: '<ul><li><strong>Single</strong> — 画像/ビデオ1件</li><li><strong>Continuous</strong> — ビデオ/カメラ/RTSP、最大8スロット</li><li>パラメータ：Confidence、NMS、Top-K、Alpha</li><li>エクスポートパッケージ</li></ul>', 'zh-CN': '<ul><li><strong>Single</strong> — 单张图片/视频</li><li><strong>Continuous</strong> — 视频/摄像头/RTSP，最多8个槽位</li><li>参数：Confidence、NMS、Top-K、Alpha</li><li>导出包</li></ul>', 'zh-TW': '<ul><li><strong>Single</strong> — 單張圖片/影片</li><li><strong>Continuous</strong> — 影片/攝影機/RTSP，最多8個插槽</li><li>參數：Confidence、NMS、Top-K、Alpha</li><li>匯出套件</li></ul>', es: '<ul><li><strong>Single</strong> — una imagen/video</li><li><strong>Continuous</strong> — video/cámara/RTSP, hasta 8 ranuras</li><li>Parámetros: Confidence, NMS, Top-K, Alpha</li><li>Exportar paquete</li></ul>' } },
    { id:'ref-bench', icon:'⏱️', title:{ ko: 'Benchmark', en: 'Benchmark', ja: 'ベンチマーク', 'zh-CN': '基准测试', 'zh-TW': '基準測試', es: 'Benchmark' },
      body:{ ko: '<ul><li>다중 모델 선택 → 순차 벤치마크</li><li>Loop Count로 반복 횟수 설정</li><li>FPS 비교 차트 + 결과 테이블</li><li>📄 Export Report</li></ul>', en: '<ul><li>Multi-model selection → sequential benchmark</li><li>Loop count setting</li><li>FPS chart + results table</li><li>📄 Export Report</li></ul>', ja: '<ul><li>複数モデル選択 → 順次ベンチマーク</li><li>ループ回数設定</li><li>FPSチャート + 結果テーブル</li><li>📄 レポートエクスポート</li></ul>', 'zh-CN': '<ul><li>多模型选择 → 顺序基准测试</li><li>循环次数设置</li><li>FPS图表 + 结果表格</li><li>📄 导出报告</li></ul>', 'zh-TW': '<ul><li>多模型選擇 → 順序基準測試</li><li>循環次數設定</li><li>FPS圖表 + 結果表格</li><li>📄 匯出報告</li></ul>', es: '<ul><li>Selección multi-modelo → benchmark secuencial</li><li>Configuración de loop count</li><li>Gráfico FPS + tabla de resultados</li><li>📄 Export Report</li></ul>' } },
    { id:'ref-compare', icon:'🔀', title:{ ko: 'A/B Compare', en: 'A/B Compare', ja: 'A/B 比較', 'zh-CN': 'A/B 对比', 'zh-TW': 'A/B 對比', es: 'A/B Compare' },
      body:{ ko: '<ul><li>2~8 슬롯 동시 비교</li><li>동일 입력(파일/카메라/RTSP) 공유</li><li>Performance Comparison 테이블</li></ul>', en: '<ul><li>2-8 slot simultaneous comparison</li><li>Shared input</li><li>Performance comparison table</li></ul>', ja: '<ul><li>2〜8スロット同時比較</li><li>共有入力</li><li>性能比較テーブル</li></ul>', 'zh-CN': '<ul><li>2-8槽位同时对比</li><li>共享输入</li><li>性能对比表</li></ul>', 'zh-TW': '<ul><li>2-8插槽同時對比</li><li>共享輸入</li><li>效能對比表</li></ul>', es: '<ul><li>Comparación simultánea de 2-8 ranuras</li><li>Entrada compartida</li><li>Tabla de comparación de rendimiento</li></ul>' } },
    { id:'ref-mz', icon:'📥', title:{ ko: 'ModelZoo', en: 'ModelZoo', ja: 'ModelZoo', 'zh-CN': 'ModelZoo', 'zh-TW': 'ModelZoo', es: 'ModelZoo' },
      body:{ ko: '<ul><li>Internal(폐쇄망) / Public 소스</li><li>태스크 필터 + 검색</li><li>Q-Lite / Q-Pro DXNN 개별 다운로드</li><li>장바구니 일괄 다운로드</li></ul>', en: '<ul><li>Internal / Public sources</li><li>Task filter + search</li><li>Q-Lite / Q-Pro DXNN download</li><li>Cart batch download</li></ul>', ja: '<ul><li>Internal / Public ソース</li><li>タスクフィルタ + 検索</li><li>Q-Lite / Q-Pro DXNNダウンロード</li><li>カート一括ダウンロード</li></ul>', 'zh-CN': '<ul><li>Internal / Public 源</li><li>任务筛选 + 搜索</li><li>Q-Lite / Q-Pro DXNN下载</li><li>购物车批量下载</li></ul>', 'zh-TW': '<ul><li>Internal / Public 來源</li><li>任務篩選 + 搜尋</li><li>Q-Lite / Q-Pro DXNN下載</li><li>購物車批次下載</li></ul>', es: '<ul><li>Orígenes Internal / Public</li><li>Filtro de tarea + búsqueda</li><li>Descarga DXNN Q-Lite / Q-Pro</li><li>Descarga por lotes con carrito</li></ul>' } },
    { id:'ref-comp', icon:'🛠️', title:{ ko: 'DX-COM Compiler', en: 'DX-COM Compiler', ja: 'DX-COM コンパイラ', 'zh-CN': 'DX-COM 编译器', 'zh-TW': 'DX-COM 編譯器', es: 'Compilador DX-COM' },
      body:{ ko: '<ul><li>ONNX 업로드 → Inspect → 전처리 → PPU → 컴파일 → Test Run → Deploy</li><li>프리셋으로 원클릭 설정</li><li>JSON Config 로드/Export</li><li>ONNX/DXNN 그래프 시각화</li><li>컴파일 히스토리</li></ul>', en: '<ul><li>Upload → Inspect → Preprocessing → PPU → Compile → Test → Deploy</li><li>Presets for one-click setup</li><li>JSON config load/export</li><li>Graph visualization</li><li>Compile history</li></ul>', ja: '<ul><li>アップロード → Inspect → 前処理 → PPU → コンパイル → テスト → デプロイ</li><li>ワンクリックセットアップのプリセット</li><li>JSON設定の読込/エクスポート</li><li>グラフ可視化</li><li>コンパイル履歴</li></ul>', 'zh-CN': '<ul><li>上传 → Inspect → 预处理 → PPU → 编译 → 测试 → 部署</li><li>一键设置预设</li><li>JSON配置加载/导出</li><li>图可视化</li><li>编译历史</li></ul>', 'zh-TW': '<ul><li>上傳 → Inspect → 預處理 → PPU → 編譯 → 測試 → 部署</li><li>一鍵設定預設</li><li>JSON配置載入/匯出</li><li>圖視覺化</li><li>編譯歷史</li></ul>', es: '<ul><li>Cargar → Inspect → Preprocessing → PPU → Compile → Test → Deploy</li><li>Presets para configuración con un clic</li><li>Carga/exportación de configuración JSON</li><li>Visualización de grafos</li><li>Historial de compilación</li></ul>' } },
    { id:'ref-shortcuts', icon:'⌨️', title:{ ko: '키보드 단축키', en: 'Keyboard Shortcuts', ja: 'キーボード ショートカット', 'zh-CN': '键盘快捷键', 'zh-TW': '鍵盤快捷鍵', es: 'Atajos de teclado' },
      body:{ ko: '<ul><li><strong>Esc</strong> — 튜토리얼 종료 / TOC 닫기</li><li><strong>←/→</strong> — 튜토리얼 이전/다음</li><li><strong>Enter</strong> — 다음 단계</li></ul>', en: '<ul><li><strong>Esc</strong> — Close tutorial / TOC</li><li><strong>←/→</strong> — Tutorial prev/next</li><li><strong>Enter</strong> — Next step</li></ul>', ja: '<ul><li><strong>Esc</strong> — チュートリアル / 目次を閉じる</li><li><strong>←/→</strong> — チュートリアル 前/次</li><li><strong>Enter</strong> — 次のステップ</li></ul>', 'zh-CN': '<ul><li><strong>Esc</strong> — 关闭教程 / 目录</li><li><strong>←/→</strong> — 教程 上一步/下一步</li><li><strong>Enter</strong> — 下一步</li></ul>', 'zh-TW': '<ul><li><strong>Esc</strong> — 關閉教學 / 目錄</li><li><strong>←/→</strong> — 教學 上一步/下一步</li><li><strong>Enter</strong> — 下一步</li></ul>', es: '<ul><li><strong>Esc</strong> — Cerrar tutorial / TOC</li><li><strong>←/→</strong> — Tutorial anterior/siguiente</li><li><strong>Enter</strong> — Siguiente paso</li></ul>' } },
  ];

  /* ════════════════════════════════════════════════════════════
     INITIALIZATION
     ════════════════════════════════════════════════════════════ */
  _orderGlobalFirst(sections);

  window.DXTutorial.create({
    appId: 'app',
    sections: sections,
    referenceDocs: referenceDocs,
    toolbarSelector: '#dxToolbar',
    skipButtons: true,
    getLang: function () {
      return (window.DXI18n && window.DXI18n.lang) || localStorage.getItem('dx-lang') || 'en';
    },
    onNav: function (p) { goPage(p); },
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
