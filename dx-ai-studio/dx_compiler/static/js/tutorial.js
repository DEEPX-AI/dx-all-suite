/**
 * DX Compiler — 5개 멀티 튜토리얼
 * Quick Start | Graph Viewer | Config Wizard | Advanced | Agentic Auto Compile
 * 6-language support (ko/en/ja/zh-CN/zh-TW/es)
 *
 * 수정 이력:
 *  - beforeStep 추가: 동적/숨겨진 요소 사전 표시
 *  - 존재하지 않는 타겟 수정 (.progress-container → #result, .input-shape-row → #btn-add-input)
 *  - 위자드 스텝 네비게이션(wizGoTo) 연동
 *  - 채팅 위젯 셀렉터 수정 (.chat-widget-toggle → .dx-chat-fab)
 *  - 미커버 기능 스텝 추가 (zoom, expand-all, wizard-close 등)
 *  - 챗봇 위젯 스텝(quick-start 마지막 단계, ai-assist 섹션 전체) 제거 → 런처 튜토리얼로 통합
 */
(function () {
  'use strict';

  function openWizardStep(step) {
    var wiz = document.getElementById('config-wizard');
    if (wiz) wiz.style.display = 'flex';
    // wizard-step 직접 전환 (wizGoTo는 클로저 내부 함수)
    document.querySelectorAll('.wizard-step').forEach(function (s) {
      s.classList.toggle('active', parseInt(s.dataset.step) === step);
    });
    document.querySelectorAll('.step-dot').forEach(function (d) {
      var ds = parseInt(d.dataset.step);
      d.classList.toggle('active', ds === step);
      d.classList.toggle('completed', ds < step);
    });
    var prevBtn = document.getElementById('wiz-prev');
    if (prevBtn) prevBtn.style.display = step > 1 ? '' : 'none';
  }

  function openResumeCard() {
    if (typeof window.setResumeCardOpen === 'function') {
      window.setResumeCardOpen(true);
    } else {
      var card = document.getElementById('resume-card');
      var header = document.getElementById('resume-card-header');
      if (card) card.classList.remove('collapsed');
      if (header) header.setAttribute('aria-expanded', 'true');
    }
  }

  // Compile-range node-selection UI (#ns-* buttons) is created on demand by
  // ViewerPanel.enterNodeSelectionMode(). For the tutorial we spawn it so each
  // range-configuration step can spotlight its own distinct control.
  function ensureNodeSelectionUI() {
    if (window.ViewerPanel && typeof window.ViewerPanel.enterNodeSelectionMode === 'function'
        && !document.getElementById('ns-toolbar')) {
      window.ViewerPanel.enterNodeSelectionMode({}, null);
    }
  }

  function exitNodeSelectionUI() {
    if (window.ViewerPanel && typeof window.ViewerPanel.exitNodeSelectionMode === 'function'
        && document.getElementById('ns-toolbar')) {
      window.ViewerPanel.exitNodeSelectionMode();
    }
  }

  function _scrollTo(sel) {
    var el = document.querySelector(sel);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function _scrollViewer(sel) {
    return function () { _scrollTo(sel); };
  }

  var quickStartSteps = [
    { target: '#header', position: 'bottom',
      title: { en: 'Welcome', ko: 'DX Compiler에 오신 걸 환영합니다', ja: 'ようこそ', 'zh-CN': '欢迎', 'zh-TW': '歡迎', es: 'Bienvenido' },
      content: { en: 'Welcome to DX Compiler. You can switch language at the top right.', ko: 'DX Compiler에 오신 걸 환영합니다. 우측 상단에서 언어를 전환할 수 있습니다.', ja: 'DX Compilerへようこそ。右上で言語を切り替えられます。', 'zh-CN': '欢迎使用DX Compiler。您可以在右上角切换语言。', 'zh-TW': '歡迎使用DX Compiler。您可以在右上角切換語言。', es: 'Bienvenido a DX Compiler. Puede cambiar el idioma en la esquina superior derecha.' } },
    { target: '#setup-panel', position: 'left',
      title: { en: 'Setup Panel', ko: '설정 패널', ja: 'セットアップパネル', 'zh-CN': '设置面板', 'zh-TW': '設定面板', es: 'Panel de configuración' },
      content: { en: 'Set up your compile environment here. Check the status of SDK, sample models, and calibration data.', ko: '여기서 컴파일 환경을 설정합니다. SDK, 샘플 모델, 캘리브레이션 데이터 상태를 확인하세요.', ja: 'ここでコンパイル環境を設定します。SDK、サンプルモデル、キャリブレーションデータの状態を確認してください。', 'zh-CN': '在此设置编译环境。检查SDK、示例模型和校准数据的状态。', 'zh-TW': '在此設定編譯環境。檢查SDK、範例模型和校準資料的狀態。', es: 'Configure aquí su entorno de compilación. Compruebe el estado del SDK, los modelos de ejemplo y los datos de calibración.' } },
    { target: '#setup-toggle', position: 'left',
      title: { en: 'Toggle Panel', ko: '패널 접기/펼치기', ja: 'パネル切替', 'zh-CN': '折叠/展开面板', 'zh-TW': '折疊/展開面板', es: 'Alternar panel' },
      content: { en: 'Click to collapse or expand the Setup Panel.', ko: '클릭하여 설정 패널을 접거나 펼칩니다.', ja: 'クリックしてセットアップパネルを折りたたみ/展開します。', 'zh-CN': '点击折叠或展开设置面板。', 'zh-TW': '點擊折疊或展開設定面板。', es: 'Haga clic para contraer o expandir el panel de configuración.' } },
    { target: '#setup-install-btn', position: 'left',
      title: { en: 'Install SDK', ko: 'SDK 설치', ja: 'SDKインストール', 'zh-CN': '安装SDK', 'zh-TW': '安裝SDK', es: 'Instalar SDK' },
      content: { en: 'DX Compiler SDK is required. Click Install to set it up automatically.', ko: 'DX Compiler SDK가 필요합니다. 설치 버튼을 클릭하면 자동으로 설치됩니다.', ja: 'DX Compiler SDKが必要です。インストールをクリックすると自動的にセットアップされます。', 'zh-CN': '需要DX Compiler SDK。点击安装以自动设置。', 'zh-TW': '需要DX Compiler SDK。點擊安裝以自動設定。', es: 'Se requiere el SDK de DX Compiler. Haga clic en Instalar para configurarlo automáticamente.' } },
    { target: '#setup-download-btn', position: 'left',
      title: { en: 'Download Samples', ko: '샘플 다운로드', ja: 'サンプルダウンロード', 'zh-CN': '下载示例', 'zh-TW': '下載範例', es: 'Descargar muestras' },
      content: { en: 'Download sample models and calibration data to try out.', ko: '체험용 샘플 모델과 캘리브레이션 데이터를 다운로드합니다.', ja: 'サンプルモデルとキャリブレーションデータをダウンロードして試します。', 'zh-CN': '下载示例模型和校准数据进行试用。', 'zh-TW': '下載範例模型和校準資料進行試用。', es: 'Descargue modelos de ejemplo y datos de calibración para probar.' } },
    { target: '#model-dropzone', position: 'left',
      title: { en: 'Model Input', ko: '모델 입력', ja: 'モデル入力', 'zh-CN': '模型输入', 'zh-TW': '模型輸入', es: 'Entrada de modelo' },
      content: { en: 'Drag & drop an ONNX model, or type the server path directly.', ko: 'ONNX 모델을 드래그앤드롭하거나, 텍스트 필드에 서버 경로를 직접 입력합니다.', ja: 'ONNXモデルをドラッグ＆ドロップするか、サーバーパスを直接入力します。', 'zh-CN': '拖放ONNX模型，或直接输入服务器路径。', 'zh-TW': '拖放ONNX模型，或直接輸入伺服器路徑。', es: 'Arrastre y suelte un modelo ONNX, o escriba la ruta del servidor directamente.' } },
    { target: '#sample-select-btn', position: 'left',
      title: { en: 'Sample Model', ko: '샘플 모델 선택', ja: 'サンプルモデル', 'zh-CN': '示例模型', 'zh-TW': '範例模型', es: 'Modelo de ejemplo' },
      content: { en: 'Select a downloaded sample model. Paths are filled in automatically.', ko: '다운로드한 샘플 모델을 바로 선택할 수 있습니다. 경로가 자동으로 입력됩니다.', ja: 'ダウンロードしたサンプルモデルを選択します。パスが自動的に入力されます。', 'zh-CN': '选择已下载的示例模型。路径将自动填充。', 'zh-TW': '選擇已下載的範例模型。路徑將自動填入。', es: 'Seleccione un modelo de ejemplo descargado. Las rutas se rellenan automáticamente.' },
      beforeStep: function () {
        var c = document.getElementById('sample-select-container');
        if (c) c.style.display = '';
      } },
    { target: '#config-dropzone', position: 'left',
      title: { en: 'Config', ko: '설정 파일', ja: '設定ファイル', 'zh-CN': '配置文件', 'zh-TW': '設定檔', es: 'Configuración' },
      content: { en: 'Upload a config JSON or create one with Build Config.', ko: '설정 JSON을 업로드하거나 Build Config로 직접 생성합니다.', ja: '設定JSONをアップロードするか、Build Configで作成します。', 'zh-CN': '上传配置JSON或使用Build Config创建。', 'zh-TW': '上傳設定JSON或使用Build Config建立。', es: 'Cargue un JSON de configuración o créelo con Build Config.' } },
    { target: '#output_dir', position: 'left',
      title: { en: 'Output', ko: '출력 경로', ja: '出力パス', 'zh-CN': '输出路径', 'zh-TW': '輸出路徑', es: 'Salida' },
      content: { en: 'Output directory for compiled results.', ko: '컴파일 결과물이 저장될 경로입니다.', ja: 'コンパイル結果の出力ディレクトリです。', 'zh-CN': '编译结果的输出目录。', 'zh-TW': '編譯結果的輸出目錄。', es: 'Directorio de salida para los resultados compilados.' } },
    { target: '#compile-main-btn', position: 'left',
      title: { en: 'Compile', ko: '컴파일', ja: 'コンパイル', 'zh-CN': '编译', 'zh-TW': '編譯', es: 'Compilar' },
      content: { en: 'Start compilation when everything is ready.', ko: '모든 준비가 완료되면 컴파일을 시작합니다.', ja: '準備が整ったらコンパイルを開始します。', 'zh-CN': '一切准备就绪后开始编译。', 'zh-TW': '一切準備就緒後開始編譯。', es: 'Inicie la compilación cuando todo esté listo.' } },
    { target: '#result', position: 'left',
      title: { en: 'Progress', ko: '진행률', ja: '進捗', 'zh-CN': '进度', 'zh-TW': '進度', es: 'Progreso' },
      content: { en: 'Progress bar and current compilation phase are shown here in real-time during compilation.', ko: '컴파일 중 진행률 바와 현재 페이즈가 이 영역에 실시간으로 표시됩니다.', ja: 'コンパイル中にプログレスバーと現在のフェーズがリアルタイムで表示されます。', 'zh-CN': '编译期间进度条和当前编译阶段将在此实时显示。', 'zh-TW': '編譯期間進度條和目前編譯階段將在此即時顯示。', es: 'Durante la compilación, la barra de progreso y la fase actual se muestran aquí en tiempo real.' } },
    { target: '#log-panel', position: 'top',
      title: { en: 'Logs', ko: '로그', ja: 'ログ', 'zh-CN': '日志', 'zh-TW': '日誌', es: 'Registros' },
      content: { en: 'View compile logs in real-time. This panel appears during compilation. Toggle to save space.', ko: '컴파일 로그를 실시간으로 확인합니다. 컴파일 중 이 패널이 나타나며, 접기/펼치기로 공간을 조절하세요.', ja: 'コンパイルログをリアルタイムで確認します。このパネルはコンパイル中に表示されます。折りたたんでスペースを節約できます。', 'zh-CN': '实时查看编译日志。此面板在编译期间显示。可折叠以节省空间。', 'zh-TW': '即時查看編譯日誌。此面板在編譯期間顯示。可折疊以節省空間。', es: 'Vea los registros de compilación en tiempo real. Este panel aparece durante la compilación. Contraiga para ahorrar espacio.' },
      beforeStep: function () {
        var lp = document.getElementById('log-panel');
        if (lp && lp.style.display === 'none') lp.style.display = '';
      } },
    { target: '#result', position: 'top',
      title: { en: 'Result', ko: '결과', ja: '結果', 'zh-CN': '结果', 'zh-TW': '結果', es: 'Resultado' },
      content: { en: 'Compilation results (success/failure) appear here.', ko: '컴파일 성공/실패 결과가 여기에 표시됩니다.', ja: 'コンパイル結果（成功/失敗）がここに表示されます。', 'zh-CN': '编译结果（成功/失败）显示在此处。', 'zh-TW': '編譯結果（成功/失敗）顯示在此處。', es: 'Los resultados de compilación (éxito o fallo) aparecen aquí.' } },
    { target: '#save-summary-btn', position: 'left',
      title: { en: 'Summary', ko: '모델 요약', ja: 'モデルサマリー', 'zh-CN': '模型摘要', 'zh-TW': '模型摘要', es: 'Resumen' },
      content: { en: 'Save model summary as HTML after compilation.', ko: '컴파일 완료 후 모델 요약을 HTML로 저장합니다.', ja: 'コンパイル完了後にモデルサマリーをHTMLとして保存します。', 'zh-CN': '编译完成后将模型摘要保存为HTML。', 'zh-TW': '編譯完成後將模型摘要儲存為HTML。', es: 'Guarde el resumen del modelo como HTML tras la compilación.' } },
  ];

  var graphViewerSteps = [
    { target: '.viewer-panel', position: 'right', title: { en: 'Graph Viewer', ko: '그래프 뷰어', ja: 'グラフビューア', 'zh-CN': '模型图查看器', 'zh-TW': '圖形檢視器', es: 'Visor de gráficos' }, content: { en: 'Visualize model graphs on the left panel.', ko: '좌측에서 모델 그래프를 시각화합니다.', ja: '左パネルでモデルグラフを視覚化します。', 'zh-CN': '在左侧面板中可视化模型图。', 'zh-TW': '在左側面板中視覺化模型圖形。', es: 'Visualice los gráficos del modelo en el panel izquierdo.' } },
    { target: '.viewer-tab', position: 'bottom', title: { en: 'Phase Tabs', ko: '페이즈 탭', ja: 'フェーズタブ', 'zh-CN': '阶段选项卡', 'zh-TW': '階段標籤', es: 'Pestañas de fase' }, content: { en: 'Switch between Input/Prepared/Surgery/Partition/DXNN graphs and the Quant Diagnosis report tab.', ko: 'Input/Prepared/Surgery/Partition/DXNN 탭과 Quant Diagnosis 보고서 탭을 전환합니다.', ja: 'Input/Prepared/Surgery/Partition/DXNN グラフと量子化診断レポートタブを切り替えます。', 'zh-CN': '在 Input/Prepared/Surgery/Partition/DXNN 图与量化诊断报告标签之间切换。', 'zh-TW': '在 Input/Prepared/Surgery/Partition/DXNN 圖形與量化診斷報告分頁之間切換。', es: 'Alterne entre los gráficos Input/Prepared/Surgery/Partition/DXNN y la pestaña de diagnóstico cuant.' } },
    { target: '.viewer-tab[data-phase="qxnn"]', position: 'bottom',
      title: { en: 'Quant Diagnosis', ko: '양자화 진단', ja: '量子化診断', 'zh-CN': '量化诊断', 'zh-TW': '量化診斷', es: 'Diagnóstico cuant.' },
      content: { en: 'After compile with Quant Diagnosis enabled, open this tab to view the HTML report. Use "Resume from this QXNN" to prefill the re-quantization panel.', ko: '양자화 진단을 켠 컴파일 후 이 탭에서 HTML 보고서를 확인합니다. "이 QXNN에서 재개"로 재양자화 패널 경로를 채울 수 있습니다.', ja: '量子化診断を有効にしてコンパイル後、このタブで HTML レポートを表示します。「この QXNN から再開」で再量子化パネルにパスを入力できます。', 'zh-CN': '启用量化诊断编译后，在此标签查看 HTML 报告。可用“从此 QXNN 恢复”预填重新量化面板。', 'zh-TW': '啟用量化診斷編譯後，在此分頁查看 HTML 報告。可用「從此 QXNN 恢復」預填重新量化面板。', es: 'Tras compilar con diagnóstico cuant. activado, abra esta pestaña para ver el informe HTML. Use "Reanudar desde este QXNN" para rellenar el panel de recuantización.' } },
    { target: '#viewer-svg', position: 'right', title: { en: 'Navigation', ko: '탐색', ja: 'ナビゲーション', 'zh-CN': '导航', 'zh-TW': '導覽', es: 'Navegación' }, content: { en: 'Drag to pan, scroll to zoom.', ko: '마우스 드래그로 이동, 스크롤로 확대/축소합니다.', ja: 'ドラッグで移動、スクロールでズームします。', 'zh-CN': '拖拽平移，滚动缩放。', 'zh-TW': '拖曳平移，滾動縮放。', es: 'Arrastre para desplazar, desplace la rueda para hacer zoom.' } },
    { target: '#viewer-status-bar', position: 'top', title: { en: 'Controls', ko: '제어', ja: 'コントロール', 'zh-CN': '控制', 'zh-TW': '控制', es: 'Controles' }, content: { en: 'Use +/- zoom buttons and Fit button. Shows Nodes/Edges/Zoom info.', ko: '+/- 줌 버튼, Fit 버튼으로 그래프 크기를 조절합니다. Nodes/Edges/Zoom 수치도 표시됩니다.', ja: '+/-ズームボタンとFitボタンを使用します。Nodes/Edges/Zoom情報が表示されます。', 'zh-CN': '使用+/-缩放按钮和适应按钮。显示节点/边/缩放信息。', 'zh-TW': '使用+/-縮放按鈕和適應按鈕。顯示節點/邊/縮放資訊。', es: 'Use los botones +/- de zoom y el botón Fit. Muestra información de nodos/aristas/zoom.' }, beforeStep: _scrollViewer('#viewer-status-bar') },
    { target: '#zoom-in', position: 'top',
      title: { en: 'Zoom In', ko: '확대', ja: 'ズームイン', 'zh-CN': '放大', 'zh-TW': '放大', es: 'Acercar' },
      content: { en: 'Click to zoom into the graph.', ko: '클릭하여 그래프를 확대합니다.', ja: 'クリックしてグラフを拡大します。', 'zh-CN': '点击放大图。', 'zh-TW': '點擊放大圖形。', es: 'Haga clic para acercar el gráfico.' },
      beforeStep: _scrollViewer('#zoom-in') },
    { target: '#zoom-out', position: 'top',
      title: { en: 'Zoom Out', ko: '축소', ja: 'ズームアウト', 'zh-CN': '缩小', 'zh-TW': '縮小', es: 'Alejar' },
      content: { en: 'Click to zoom out of the graph.', ko: '클릭하여 그래프를 축소합니다.', ja: 'クリックしてグラフを縮小します。', 'zh-CN': '点击缩小图。', 'zh-TW': '點擊縮小圖形。', es: 'Haga clic para alejar el gráfico.' },
      beforeStep: _scrollViewer('#zoom-out') },
    { target: '#zoom-fit', position: 'top',
      title: { en: 'Fit View', ko: '화면 맞춤', ja: '画面フィット', 'zh-CN': '适应视图', 'zh-TW': '適應檢視', es: 'Ajustar vista' },
      content: { en: 'Fit the entire graph into the visible area.', ko: '전체 그래프를 화면에 맞춰 표시합니다.', ja: 'グラフ全体を表示領域に収めます。', 'zh-CN': '将整个图缩放至适合可见区域。', 'zh-TW': '將整個圖形適應到可見區域。', es: 'Ajuste todo el gráfico al área visible.' },
      beforeStep: _scrollViewer('#zoom-fit') },
    { target: '#collapse-all', position: 'top', title: { en: 'Collapse All', ko: '모두 접기', ja: 'すべて折りたたむ', 'zh-CN': '全部折叠', 'zh-TW': '全部折疊', es: 'Contraer todo' }, content: { en: 'Collapse all subgraphs for an overview (Partition/DXNN tabs).', ko: '서브그래프를 모두 접어 전체 구조를 한눈에 봅니다 (Partition/DXNN 탭).', ja: 'すべてのサブグラフを折りたたんで全体を俯瞰します（Partition/DXNNタブ）。', 'zh-CN': '折叠所有子图以获取概览（Partition/DXNN选项卡）。', 'zh-TW': '折疊所有子圖以取得概覽（Partition/DXNN標籤）。', es: 'Contraiga todos los subgrafos para una vista general (pestañas Partition/DXNN).' },
      beforeStep: _scrollViewer('#collapse-all') },
    { target: '#expand-all', position: 'top',
      title: { en: 'Expand All', ko: '모두 펼치기', ja: 'すべて展開', 'zh-CN': '全部展开', 'zh-TW': '全部展開', es: 'Expandir todo' },
      content: { en: 'Expand all collapsed subgraphs to see full detail.', ko: '접힌 서브그래프를 모두 펼쳐 전체 상세를 확인합니다.', ja: '折りたたまれたサブグラフをすべて展開して詳細を表示します。', 'zh-CN': '展开所有折叠的子图以查看完整细节。', 'zh-TW': '展開所有折疊的子圖以查看完整細節。', es: 'Expanda todos los subgrafos contraídos para ver el detalle completo.' },
      beforeStep: _scrollViewer('#expand-all') },
    { target: '#explorer-toggle', position: 'right', title: { en: 'Explorer', ko: '익스플로러', ja: 'エクスプローラー', 'zh-CN': '节点浏览器', 'zh-TW': '節點瀏覽器', es: 'Explorador' }, content: { en: 'Browse nodes by category (Compute/Memory/Activation etc).', ko: '익스플로러를 열어 노드를 카테고리별로 탐색합니다.', ja: 'カテゴリ別にノードを参照します（Compute/Memory/Activationなど）。', 'zh-CN': '按类别浏览节点（Compute/Memory/Activation等）。', 'zh-TW': '按類別瀏覽節點（Compute/Memory/Activation等）。', es: 'Explore nodos por categoría (Compute/Memory/Activation, etc.).' } },
    { target: '#search-input', position: 'bottom', title: { en: 'Search', ko: '검색', ja: '検索', 'zh-CN': '搜索', 'zh-TW': '搜尋', es: 'Buscar' }, content: { en: 'Press Ctrl+F to search nodes, op_types, and tensors. Use arrow keys to navigate results.', ko: 'Ctrl+F로 노드명, op_type, 텐서명을 검색합니다. 방향키로 결과를 탐색합니다.', ja: 'Ctrl+Fでノード名、op_type、テンソル名を検索します。方向キーで結果を移動します。', 'zh-CN': '按Ctrl+F搜索节点、op_type和张量。使用方向键浏览结果。', 'zh-TW': '按Ctrl+F搜尋節點、op_type和張量。使用方向鍵瀏覽結果。', es: 'Pulse Ctrl+F para buscar nodos, op_types y tensores. Use las flechas para navegar por los resultados.' } },
    { target: '#node-info', position: 'left',
      title: { en: 'Node Details', ko: '노드 상세', ja: 'ノード詳細', 'zh-CN': '节点详情', 'zh-TW': '節點詳情', es: 'Detalles del nodo' },
      content: { en: 'Click a node to see op_type and tensor info. Click a tensor to navigate to it.', ko: '노드를 클릭하면 op_type, 입출력 텐서 정보가 표시됩니다. 텐서를 클릭하면 해당 위치로 이동합니다.', ja: 'ノードをクリックするとop_typeとテンソル情報が表示されます。テンソルをクリックするとその位置に移動します。', 'zh-CN': '点击节点查看op_type和张量信息。点击张量导航到该位置。', 'zh-TW': '點擊節點查看op_type和張量資訊。點擊張量導覽到該位置。', es: 'Haga clic en un nodo para ver op_type e información de tensores. Haga clic en un tensor para ir a su ubicación.' },
      beforeStep: function () {
        var ni = document.getElementById('node-info');
        if (ni && ni.style.display === 'none') ni.style.display = '';
      } },
    { target: '#viewer-svg', position: 'right', title: { en: 'Edge Details', ko: '엣지 상세', ja: 'エッジ詳細', 'zh-CN': '边详情', 'zh-TW': '邊詳情', es: 'Detalles de arista' }, content: { en: 'Click an edge for tensor detail popup and auto-zoom to related nodes.', ko: '엣지를 클릭하면 텐서 상세 팝업이 나타나고 관련 노드로 자동 줌합니다.', ja: 'エッジをクリックするとテンソル詳細ポップアップが表示され、関連ノードに自動ズームします。', 'zh-CN': '点击边查看张量详情弹窗并自动缩放到相关节点。', 'zh-TW': '點擊邊查看張量詳情彈窗並自動縮放到相關節點。', es: 'Haga clic en una arista para ver un popup con detalles del tensor y zoom automático a nodos relacionados.' } },
    { target: '#legend', position: 'left', title: { en: 'Legend', ko: '범례', ja: '凡例', 'zh-CN': '图例', 'zh-TW': '圖例', es: 'Leyenda' }, content: { en: 'Color legend for node types. Subgraphs can be individually toggled.', ko: '범례에서 노드 종류별 색상을 확인합니다. 서브그래프는 개별적으로 접기/펼치기할 수 있습니다.', ja: 'ノードタイプの色凡例です。サブグラフは個別に切り替えられます。', 'zh-CN': '节点类型的颜色图例。子图可以单独切换。', 'zh-TW': '節點類型的顏色圖例。子圖可以個別切換。', es: 'Leyenda de colores por tipo de nodo. Los subgrafos se pueden alternar individualmente.' } },
  ];

  var configWizardSteps = [
    { target: '#config_build_toggle', position: 'left',
      title: { en: 'Build Config', ko: '설정 생성', ja: '設定を生成', 'zh-CN': '生成配置', 'zh-TW': '產生設定', es: 'Build Config' },
      content: { en: 'Check Build Config to open the configuration wizard.', ko: 'Build Config를 체크하면 설정 마법사가 열립니다.', ja: 'Build Configにチェックを入れると設定ウィザードが開きます。', 'zh-CN': '勾选Build Config打开配置向导。', 'zh-TW': '勾選Build Config開啟設定精靈。', es: 'Marque Build Config para abrir el asistente de configuración.' } },
    { target: '#btn-auto-detect', position: 'bottom',
      title: { en: 'Auto Detect', ko: '자동 감지', ja: '自動検出', 'zh-CN': '自动检测', 'zh-TW': '自動偵測', es: 'Detección automática' },
      content: { en: 'Automatically detect input tensors from the model.', ko: '모델에서 입력 텐서를 자동으로 감지합니다.', ja: 'モデルから入力テンソルを自動検出します。', 'zh-CN': '从模型自动检测输入张量。', 'zh-TW': '從模型自動偵測輸入張量。', es: 'Detecte automáticamente los tensores de entrada del modelo.' },
      beforeStep: function () { openWizardStep(1); } },
    { target: '#btn-add-input', position: 'bottom',
      title: { en: 'Add Input Row', ko: '입력 행 추가', ja: '入力行を追加', 'zh-CN': '添加输入行', 'zh-TW': '新增輸入行', es: 'Añadir fila de entrada' },
      content: { en: 'Add a new input shape row manually. Use Auto Detect or add rows with this button, then review name and shape.', ko: '입력 shape 행을 수동으로 추가합니다. Auto Detect 또는 이 버튼으로 행을 추가한 뒤 이름과 shape을 확인하세요.', ja: '入力シェイプ行を手動で追加します。Auto Detectまたはこのボタンで行を追加し、名前とシェイプを確認してください。', 'zh-CN': '手动添加新的输入形状行。使用自动检测或此按钮添加行，然后检查名称和形状。', 'zh-TW': '手動新增輸入形狀行。使用自動偵測或此按鈕新增行，然後檢查名稱和形狀。', es: 'Añada manualmente una fila de forma de entrada. Use Detección automática o este botón, y revise nombre y forma.' },
      beforeStep: function () { openWizardStep(1); } },
    { target: '.mode-card', position: 'bottom',
      title: { en: 'Loader Mode', ko: '로더 선택', ja: 'ローダーモード', 'zh-CN': '加载器模式', 'zh-TW': '載入器模式', es: 'Modo de cargador' },
      content: { en: 'Choose Default (real data) or Dummy (random tensor) loader.', ko: 'Default(실제 데이터) 또는 Dummy(랜덤 텐서) 로더를 선택합니다.', ja: 'Default（実データ）またはDummy（ランダムテンソル）ローダーを選択します。', 'zh-CN': '选择Default（真实数据）或Dummy（随机张量）加载器。', 'zh-TW': '選擇Default（真實資料）或Dummy（隨機張量）載入器。', es: 'Elija el cargador Default (datos reales) o Dummy (tensor aleatorio).' },
      beforeStep: function () { openWizardStep(2); } },
    { target: '#wiz-dataset-path', position: 'bottom',
      title: { en: 'Dataset', ko: '데이터셋', ja: 'データセット', 'zh-CN': '数据集', 'zh-TW': '資料集', es: 'Conjunto de datos' },
      content: { en: 'Specify calibration dataset path and file extensions.', ko: '캘리브레이션 데이터셋 경로와 파일 확장자를 지정합니다.', ja: 'キャリブレーションデータセットのパスとファイル拡張子を指定します。', 'zh-CN': '指定校准数据集路径和文件扩展名。', 'zh-TW': '指定校準資料集路徑和檔案副檔名。', es: 'Especifique la ruta del conjunto de calibración y las extensiones de archivo.' },
      beforeStep: function () { openWizardStep(3); } },
    { target: '#prep-select', position: 'bottom',
      title: { en: 'Preprocessing', ko: '전처리', ja: '前処理', 'zh-CN': '预处理', 'zh-TW': '預處理', es: 'Preprocesamiento' },
      content: { en: 'Add preprocessing transforms (resize, normalize, etc.) to the pipeline.', ko: 'resize, normalize 등 14종 전처리를 순서대로 파이프라인에 추가합니다.', ja: '前処理（resize、normalizeなど）をパイプラインに追加します。', 'zh-CN': '将预处理变换（resize、normalize等）添加到管线。', 'zh-TW': '將預處理轉換（resize、normalize等）新增到管線。', es: 'Añada transformaciones de preprocesamiento (resize, normalize, etc.) a la canalización.' },
      beforeStep: function () { openWizardStep(3); } },
    { target: '#wiz-calib-num', position: 'bottom',
      title: { en: 'Calibration', ko: '보정 설정', ja: 'キャリブレーション', 'zh-CN': '校准设置', 'zh-TW': '校準設定', es: 'Calibración' },
      content: { en: 'Set calibration sample count and method (EMA/MinMax).', ko: '보정 샘플 수와 방법(EMA/MinMax)을 설정합니다.', ja: 'キャリブレーションのサンプル数と方法（EMA/MinMax）を設定します。', 'zh-CN': '设置校准样本数和方法（EMA/MinMax）。', 'zh-TW': '設定校準樣本數和方法（EMA/MinMax）。', es: 'Configure el número de muestras y el método de calibración (EMA/MinMax).' },
      beforeStep: function () { openWizardStep(3); } },
    { target: '#wiz-json-preview', position: 'bottom',
      title: { en: 'Preview', ko: 'JSON 미리보기', ja: 'プレビュー', 'zh-CN': '预览', 'zh-TW': '預覽', es: 'Vista previa' },
      content: { en: 'Preview the generated config JSON.', ko: '생성될 설정 JSON을 미리 확인합니다.', ja: '生成される設定JSONをプレビューします。', 'zh-CN': '预览生成的配置JSON。', 'zh-TW': '預覽產生的設定JSON。', es: 'Previsualice el JSON de configuración generado.' },
      beforeStep: function () { openWizardStep(4); } },
    { target: '#wiz-next', position: 'top',
      title: { en: 'Apply', ko: '적용', ja: '適用', 'zh-CN': '应用', 'zh-TW': '套用', es: 'Aplicar' },
      content: { en: 'Click "Use This Config" to auto-fill the config path in the compile form.', ko: 'Use This Config를 클릭하면 컴파일 폼에 config 경로가 자동 입력됩니다.', ja: '「Use This Config」をクリックするとコンパイルフォームに設定パスが自動入力されます。', 'zh-CN': '点击“Use This Config”自动填充编译表单中的配置路径。', 'zh-TW': '點擊「Use This Config」自動填入編譯表單中的設定路徑。', es: 'Haga clic en "Use This Config" para rellenar automáticamente la ruta de configuración en el formulario de compilación.' },
      beforeStep: function () { openWizardStep(4); } },
    { target: '#wiz-prev', position: 'top',
      title: { en: 'Back', ko: '이전 단계', ja: '戻る', 'zh-CN': '返回', 'zh-TW': '返回', es: 'Atrás' },
      content: { en: 'Go back to the previous wizard step.', ko: '이전 마법사 단계로 돌아갑니다.', ja: '前のウィザードステップに戻ります。', 'zh-CN': '返回向导的上一步。', 'zh-TW': '返回上一步精靈步驟。', es: 'Vuelva al paso anterior del asistente.' },
      beforeStep: function () { openWizardStep(2); } },
    { target: '.wizard-close', position: 'bottom',
      title: { en: 'Close Wizard', ko: '마법사 닫기', ja: 'ウィザードを閉じる', 'zh-CN': '关闭向导', 'zh-TW': '關閉精靈', es: 'Cerrar asistente' },
      content: { en: 'Close the config wizard without applying.', ko: '설정을 적용하지 않고 마법사를 닫습니다.', ja: '設定を適用せずにウィザードを閉じます。', 'zh-CN': '关闭配置向导，不应用任何设置。', 'zh-TW': '不套用設定關閉精靈。', es: 'Cierre el asistente de configuración sin aplicar cambios.' },
      beforeStep: function () {
        var wiz = document.getElementById('config-wizard');
        if (wiz) wiz.style.display = 'flex';
      } },
  ];

  // The tutorial opens the full-screen #config-wizard overlay on these steps but had no
  // teardown, so leaving/finishing the section left it covering the compiler UI. Give
  // every step an afterStep that closes it; the next wizard step's beforeStep reopens it,
  // so it stays visible during the walkthrough but is closed on completion or an early exit.
  (function () {
    var _closeWiz = function () {
      var wiz = document.getElementById('config-wizard');
      if (wiz) wiz.style.display = 'none';
    };
    configWizardSteps.forEach(function (s) { if (!s.afterStep) s.afterStep = _closeWiz; });
  })();

  var advancedSteps = [
    { target: '#opt_level', position: 'left', title: { en: 'Optimization', ko: '최적화 수준', ja: '最適化レベル', 'zh-CN': '优化级别', 'zh-TW': '最佳化等級', es: 'Optimización' }, content: { en: 'Choose Standard (0) or Advanced (1) optimization level.', ko: '최적화 수준을 Standard(0) 또는 Advanced(1)로 선택합니다.', ja: 'Standard(0)またはAdvanced(1)の最適化レベルを選択します。', 'zh-CN': '选择Standard(0)或Advanced(1)优化级别。', 'zh-TW': '選擇Standard(0)或Advanced(1)最佳化等級。', es: 'Elija el nivel de optimización Standard (0) o Advanced (1).' } },
    { target: '#aggressive_partitioning', position: 'left', title: { en: 'Partitioning', ko: '파티셔닝', ja: 'パーティショニング', 'zh-CN': '分区', 'zh-TW': '分區', es: 'Particionado' }, content: { en: 'Check to remove NPU task count limit.', ko: '체크하면 NPU 태스크 수 제한을 해제합니다.', ja: 'チェックするとNPUタスク数の制限が解除されます。', 'zh-CN': '勾选以移除NPU任务数量限制。', 'zh-TW': '勾選以移除NPU工作數量限制。', es: 'Marque para eliminar el límite de tareas NPU.' } },
    { target: '#gen_log', position: 'left', title: { en: 'Log File', ko: '로그 파일', ja: 'ログファイル', 'zh-CN': '日志文件', 'zh-TW': '日誌檔案', es: 'Archivo de registro' }, content: { en: 'Save compile log as a file in the output directory.', ko: '체크하면 컴파일 로그를 출력 디렉토리에 파일로 저장합니다.', ja: 'コンパイルログを出力ディレクトリにファイルとして保存します。', 'zh-CN': '将编译日志保存为输出目录中的文件。', 'zh-TW': '將編譯日誌儲存為輸出目錄中的檔案。', es: 'Guarde el registro de compilación como archivo en el directorio de salida.' } },
    { target: '#quant_diagnosis', position: 'left', title: { en: 'Quant Diagnosis', ko: '양자화 진단', ja: '量子化診断', 'zh-CN': '量化诊断', 'zh-TW': '量化診斷', es: 'Diagnóstico cuant.' }, content: { en: 'Enable to generate a quantization diagnosis HTML report under quant_diagnosis/. A diagnosis failure does not fail the compile.', ko: '체크하면 quant_diagnosis/ 아래에 양자화 진단 HTML 보고서를 생성합니다. 진단 실패는 컴파일 실패로 이어지지 않습니다.', ja: '有効にすると quant_diagnosis/ 配下に量子化診断 HTML レポートを生成します。診断失敗はコンパイル失敗になりません。', 'zh-CN': '勾选后在 quant_diagnosis/ 下生成量化诊断 HTML 报告。诊断失败不会导致编译失败。', 'zh-TW': '勾選後在 quant_diagnosis/ 下產生量化診斷 HTML 報告。診斷失敗不會導致編譯失敗。', es: 'Active para generar un informe HTML de diagnóstico en quant_diagnosis/. Un fallo de diagnóstico no falla la compilación.' } },
    { target: '#model_server_path', position: 'left', title: { en: 'Server Path', ko: '서버 경로', ja: 'サーバーパス', 'zh-CN': '服务器路径', 'zh-TW': '伺服器路徑', es: 'Ruta del servidor' }, content: { en: 'Use server file paths directly for model and config.', ko: '서버에 있는 파일을 직접 경로로 지정할 수 있습니다 (모델/설정 모두).', ja: 'モデルと設定にサーバーのファイルパスを直接使用します。', 'zh-CN': '直接使用服务器文件路径指定模型和配置。', 'zh-TW': '直接使用伺服器檔案路徑指定模型和設定。', es: 'Use rutas de archivos del servidor directamente para modelo y configuración.' } },
    { target: '#config_path', position: 'left',
      title: { en: 'Config Path', ko: '설정 경로', ja: '設定パス', 'zh-CN': '配置路径', 'zh-TW': '設定路徑', es: 'Ruta de configuración' },
      content: { en: 'Path to the compile config JSON file. Auto-filled when using Build Config wizard.', ko: '컴파일 설정 JSON 파일 경로입니다. Build Config 마법사 사용 시 자동 입력됩니다.', ja: 'コンパイル設定JSONファイルのパスです。Build Configウィザード使用時に自動入力されます。', 'zh-CN': '编译配置JSON文件的路径。使用Build Config向导时自动填充。', 'zh-TW': '編譯設定JSON檔案的路徑。使用Build Config精靈時自動填入。', es: 'Ruta al archivo JSON de configuración de compilación. Se rellena automáticamente al usar el asistente Build Config.' } },
    { target: '#config_server_path', position: 'left',
      title: { en: 'Config Server Path', ko: '설정 서버 경로', ja: '設定サーバーパス', 'zh-CN': '配置服务器路径', 'zh-TW': '設定伺服器路徑', es: 'Ruta de configuración en el servidor' },
      content: { en: 'Check to specify a server-side path for the config file instead of uploading.', ko: '체크하면 설정 파일을 업로드 대신 서버 경로로 직접 지정합니다.', ja: 'チェックすると設定ファイルをアップロードせずにサーバーパスで指定します。', 'zh-CN': '勾选以指定配置文件的服务器端路径而非上传。', 'zh-TW': '勾選以指定設定檔的伺服器端路徑而非上傳。', es: 'Marque para especificar una ruta en el servidor para el archivo de configuración en lugar de cargarlo.' } },
    { target: '.advanced-options summary', position: 'left', title: { en: 'Advanced Options', ko: '고급 옵션', ja: '詳細オプション', 'zh-CN': '高级选项', 'zh-TW': '進階選項', es: 'Opciones avanzadas' }, content: { en: 'Open to configure DXQ Enhancement settings.', ko: '고급 옵션을 펼치면 DXQ Enhancement를 설정할 수 있습니다.', ja: '開くとDXQ Enhancement設定を構成できます。', 'zh-CN': '打开以配置DXQ增强设置。', 'zh-TW': '展開以設定DXQ增強設定。', es: 'Abra para configurar los ajustes de DXQ Enhancement.' } },
    { target: '#dxq-auto', position: 'left',
      title: { en: 'Auto (Q-PRO)', ko: '자동 (Q-PRO)', ja: '自動 (Q-PRO)', 'zh-CN': '自动 (Q-PRO)', 'zh-TW': '自動 (Q-PRO)', es: 'Auto (Q-PRO)' },
      content: { en: 'Let dx_com auto-select the DXQ scheme with Q-PRO tuning. Disables manual DXQ presets when enabled.', ko: 'dx_com Q-PRO 튜닝으로 DXQ 방식을 자동 선택합니다. 활성화 시 수동 DXQ 프리셋은 비활성화됩니다.', ja: 'dx_com の Q-PRO チューニングで DXQ スキームを自動選択します。有効時は手動 DXQ プリセットが無効になります。', 'zh-CN': '让 dx_com 通过 Q-PRO 调优自动选择 DXQ 方案。启用后禁用手动 DXQ 预设。', 'zh-TW': '讓 dx_com 透過 Q-PRO 調校自動選擇 DXQ 方案。啟用後停用手動 DXQ 預設。', es: 'Permita que dx_com seleccione automáticamente el esquema DXQ con ajuste Q-PRO. Desactiva los presets DXQ manuales.' },
      beforeStep: function () {
        var det = document.querySelector('.advanced-options');
        if (det && !det.open) det.open = true;
      } },
    { target: '.dxq-fieldset', position: 'left',
      title: { en: 'DXQ Enhancement', ko: 'DXQ 양자화', ja: 'DXQ拡張', 'zh-CN': 'DXQ增强', 'zh-TW': 'DXQ增強', es: 'DXQ Enhancement' },
      content: { en: 'Fine-tune quantization with DXQ-P0~P5 presets. Each has unique parameters.', ko: 'DXQ-P0~P5 프리셋으로 양자화를 미세조정합니다. 각 프리셋은 고유한 파라미터를 가집니다.', ja: 'DXQ-P0〜P5プリセットで量子化を微調整します。各プリセットには固有のパラメータがあります。', 'zh-CN': '使用DXQ-P0~P5预设微调量化。每个预设有独特的参数。', 'zh-TW': '使用DXQ-P0~P5預設微調量化。每個預設有獨特的參數。', es: 'Ajuste la cuantización con los presets DXQ-P0~P5. Cada uno tiene parámetros únicos.' },
      beforeStep: function () {
        var det = document.querySelector('.advanced-options');
        if (det && !det.open) det.open = true;
      } },
    { target: '#node-selection', position: 'left', title: { en: 'Node Selection', ko: '노드 선택', ja: 'ノード選択', 'zh-CN': '节点选择', 'zh-TW': '節點選擇', es: 'Selección de nodos' }, content: { en: 'Enable compile range selection mode. Select nodes on graph after PREPARE phase.', ko: '컴파일 범위 선택 모드를 활성화합니다. PREPARE 완료 후 그래프에서 노드를 선택합니다.', ja: 'コンパイル範囲選択モードを有効にします。PREPAREフェーズ後にグラフ上でノードを選択します。', 'zh-CN': '启用编译范围选择模式。PREPARE阶段后在图上选择节点。', 'zh-TW': '啟用編譯範圍選擇模式。PREPARE階段後在圖上選擇節點。', es: 'Active el modo de selección de rango de compilación. Seleccione nodos en el gráfico tras la fase PREPARE.' } },
    { target: '#ns-input-btn', position: 'left', title: { en: 'Input Nodes', ko: '입력 노드', ja: '入力ノード', 'zh-CN': '输入节点', 'zh-TW': '輸入節點', es: 'Nodos de entrada' }, content: { en: 'After enabling, click the input node button (#ns-input-btn, appears after PREPARE) to select start nodes on the graph.', ko: '활성화 후, 입력 노드 설정 버튼(#ns-input-btn, PREPARE 후 표시)을 클릭하여 시작 노드를 선택합니다.', ja: '有効化後、入力ノードボタン(#ns-input-btn、PREPARE後に表示)をクリックしてグラフ上の開始ノードを選択します。', 'zh-CN': '启用后，点击输入节点按钮(#ns-input-btn，PREPARE后显示)以在图上选择起始节点。', 'zh-TW': '啟用後，點擊輸入節點按鈕(#ns-input-btn，PREPARE後顯示)以在圖上選擇起始節點。', es: 'Tras activarlo, haga clic en el botón de nodo de entrada (#ns-input-btn, visible tras PREPARE) para seleccionar nodos de inicio en el gráfico.' }, beforeStep: ensureNodeSelectionUI },
    { target: '#ns-output-btn', position: 'left', title: { en: 'Output Nodes', ko: '출력 노드', ja: '出力ノード', 'zh-CN': '输出节点', 'zh-TW': '輸出節點', es: 'Nodos de salida' }, content: { en: 'Click the output node button (#ns-output-btn) to select end nodes on the graph.', ko: '출력 노드 설정 버튼(#ns-output-btn)을 클릭하여 끝 노드를 선택합니다.', ja: '出力ノードボタン(#ns-output-btn)をクリックしてグラフ上の終了ノードを選択します。', 'zh-CN': '点击输出节点按钮(#ns-output-btn)以在图上选择结束节点。', 'zh-TW': '點擊輸出節點按鈕(#ns-output-btn)以在圖上選擇結束節點。', es: 'Haga clic en el botón de nodo de salida (#ns-output-btn) para seleccionar nodos finales en el gráfico.' }, beforeStep: ensureNodeSelectionUI },
    { target: '#ns-calc-btn', position: 'left', title: { en: 'Calculate Range', ko: '범위 계산', ja: '範囲計算', 'zh-CN': '计算范围', 'zh-TW': '計算範圍', es: 'Calcular rango' }, content: { en: 'Click Calculate (#ns-calc-btn) to see included/excluded nodes highlighted by color.', ko: '범위 계산 버튼(#ns-calc-btn)을 클릭하면 포함/제외 노드가 색상으로 구분됩니다.', ja: '計算(#ns-calc-btn)をクリックすると、含まれる/除外されるノードが色で強調表示されます。', 'zh-CN': '点击计算(#ns-calc-btn)以通过颜色高亮显示包含/排除的节点。', 'zh-TW': '點擊計算(#ns-calc-btn)以透過顏色高亮顯示包含/排除的節點。', es: 'Haga clic en Calcular (#ns-calc-btn) para ver los nodos incluidos/excluidos resaltados por color.' }, beforeStep: ensureNodeSelectionUI },
    { target: '#ns-resume-btn', position: 'left', title: { en: 'Resume', ko: '재개', ja: '再開', 'zh-CN': '恢复', 'zh-TW': '恢復', es: 'Reanudar' }, content: { en: 'Click Resume Compilation (#ns-resume-btn) to continue with selected range.', ko: 'Resume Compilation(#ns-resume-btn)을 클릭하면 선택한 범위로 컴파일을 재개합니다.', ja: 'Resume Compilation(#ns-resume-btn)をクリックして選択した範囲でコンパイルを続行します。', 'zh-CN': '点击Resume Compilation(#ns-resume-btn)以选定范围继续编译。', 'zh-TW': '點擊Resume Compilation(#ns-resume-btn)以選定範圍繼續編譯。', es: 'Haga clic en Resume Compilation (#ns-resume-btn) para continuar con el rango seleccionado.' }, beforeStep: ensureNodeSelectionUI },
    { target: '#resume-card-header', position: 'left',
      title: { en: 'Resume from QXNN', ko: 'QXNN에서 재개', ja: 'QXNN から再開', 'zh-CN': '从 QXNN 恢复', 'zh-TW': '從 QXNN 恢復', es: 'Reanudar desde QXNN' },
      content: { en: 'Re-quantize from an existing .qxnn artifact to produce a new .dxnn — independent of compile-range resume.', ko: '기존 .qxnn에서 재양자화하여 새 .dxnn을 만듭니다. 컴파일 범위 재개와는 별개 기능입니다.', ja: '既存の .qxnn から再量子化して新しい .dxnn を生成します。コンパイル範囲再開とは別機能です。', 'zh-CN': '从现有 .qxnn 重新量化生成新 .dxnn——与编译范围恢复无关。', 'zh-TW': '從現有 .qxnn 重新量化產生新 .dxnn——與編譯範圍恢復無關。', es: 'Recuantice desde un .qxnn existente para un nuevo .dxnn; independiente de la reanudación por rango.' },
      beforeStep: function () { exitNodeSelectionUI(); openResumeCard(); } },
    { target: '#qxnn_path', position: 'left',
      title: { en: 'QXNN Path', ko: 'QXNN 경로', ja: 'QXNN パス', 'zh-CN': 'QXNN 路径', 'zh-TW': 'QXNN 路徑', es: 'Ruta QXNN' },
      content: { en: 'Enter the server path to a .qxnn artifact. You can prefill it from the Quant Diagnosis tab after compile.', ko: '서버에 있는 .qxnn 아티팩트 경로를 입력합니다. 컴파일 후 Quant Diagnosis 탭에서 미리 채울 수 있습니다.', ja: 'サーバー上の .qxnn アーティファクトパスを入力します。コンパイル後の量子化診断タブから事前入力できます。', 'zh-CN': '输入服务器上 .qxnn 工件的路径。编译后可从量化诊断标签预填。', 'zh-TW': '輸入伺服器上 .qxnn 工件的路徑。編譯後可從量化診斷分頁預填。', es: 'Introduzca la ruta del servidor a un artefacto .qxnn. Puede rellenarla desde la pestaña de diagnóstico tras compilar.' },
      beforeStep: function () { openResumeCard(); } },
    { target: '#resume-form .resume-btn', position: 'left',
      title: { en: 'Start Re-quantization', ko: '재양자화 시작', ja: '再量子化開始', 'zh-CN': '开始重新量化', 'zh-TW': '開始重新量化', es: 'Iniciar recuantización' },
      content: { en: 'Submit to re-quantize from the QXNN path and write a new .dxnn to the output directory.', ko: 'QXNN 경로에서 재양자화를 실행하고 출력 디렉터리에 새 .dxnn을 생성합니다.', ja: 'QXNN パスから再量子化を実行し、出力ディレクトリに新しい .dxnn を書き出します。', 'zh-CN': '从 QXNN 路径提交重新量化，并在输出目录写入新 .dxnn。', 'zh-TW': '從 QXNN 路徑提交重新量化，並在輸出目錄寫入新 .dxnn。', es: 'Envíe para recuantizar desde la ruta QXNN y escribir un nuevo .dxnn en el directorio de salida.' },
      beforeStep: function () { openResumeCard(); } },
  ];

  var agenticAutoCompileSteps = [
    { target: '#agentic-agent-select', position: 'left',
      title: { ko: '에이전트 자동 컴파일', en: 'Agentic Auto Compile', ja: 'エージェント自動コンパイル', 'zh-CN': '智能体自动编译', 'zh-TW': '代理程式自動編譯', es: 'Compilación con agente' },
      content: { ko: '모델 이름·경로·URL만 주면 .deepx 에이전트가 다운로드·변환·컴파일·검증까지 합니다. ⚡는 질문 없이 한 번에, 💬는 대화형으로 진행합니다.', en: 'Give a model name/path/URL and the .deepx agent downloads, converts, compiles and verifies it. ⚡ runs to completion without asking; 💬 is interactive.', ja: 'モデル名・パス・URL を渡すと .deepx エージェントが取得・変換・コンパイル・検証します。⚡は質問なしで一気に、💬は対話型で進みます。', 'zh-CN': '提供模型名称/路径/URL，.deepx 智能体会下载、转换、编译并验证。⚡ 无提问一次完成；💬 为交互式。', 'zh-TW': '提供模型名稱/路徑/URL，.deepx 代理程式會下載、轉換、編譯並驗證。⚡ 無提問一次完成；💬 為互動式。', es: 'Indique un nombre/ruta/URL de modelo y el agente .deepx lo descarga, convierte, compila y verifica. ⚡ se ejecuta sin preguntar; 💬 es interactivo.' } },
    { target: '#auto-compile-noninteractive', position: 'left',
      title: { ko: '⚡ 질문 없이 자동 컴파일', en: '⚡ Auto Compile (no interaction)', ja: '⚡ 自動コンパイル（質問なし）', 'zh-CN': '⚡ 自动编译（无交互）', 'zh-TW': '⚡ 自動編譯（無互動）', es: '⚡ Compilar auto (sin interacción)' },
      content: { ko: '에이전트가 추가 질문 없이 모든 단계를 자동으로 완료합니다.', en: 'The agent completes all steps automatically without any additional questions.', ja: 'エージェントが追加の質問なしにすべてのステップを自動で完了します。', 'zh-CN': '智能体无需额外提问，自动完成所有步骤。', 'zh-TW': '代理程式無需額外提問，自動完成所有步驟。', es: 'El agente completa todos los pasos automáticamente sin preguntas adicionales.' } },
    { target: '#auto-compile-interactive', position: 'left',
      title: { ko: '💬 대화형 자동 컴파일', en: '💬 Auto Compile (interactive)', ja: '💬 自動コンパイル（対話型）', 'zh-CN': '💬 自动编译（交互式）', 'zh-TW': '💬 自動編譯（互動式）', es: '💬 Compilar auto (interactivo)' },
      content: { ko: '에이전트가 각 단계마다 확인을 거치며 대화형으로 진행합니다. 세밀한 제어가 필요할 때 사용하세요.', en: 'The agent proceeds interactively, confirming at each step. Use this for finer control.', ja: 'エージェントが各ステップで確認しながら対話型で進みます。細かい制御が必要な場合に使用してください。', 'zh-CN': '智能体在每个步骤进行确认，以交互方式进行。需要精细控制时使用。', 'zh-TW': '代理程式在每個步驟進行確認，以互動方式進行。需要精細控制時使用。', es: 'El agente avanza de forma interactiva, confirmando en cada paso. Úselo para un control más preciso.' } },
  ];

  function getLang() {
    return (window.DXI18n && DXI18n.lang) ? DXI18n.lang : (localStorage.getItem('dx-lang') || 'en');
  }

  DXTutorial.create({
    appId: 'dx_compiler',
    getLang: getLang,
    toolbarSelector: '#dxToolbar',
    skipButtons: true,
    onNav: function () {},
    onComplete: function (sectionId) {
      console.info('[DX Compiler Tutorial] section complete:', sectionId);
    },
    patchNav: function () {},
    sections: [
      { id: 'quick-start', icon: '📖',
        title: { en: '📖 Quick Start', ko: '📖 빠른 시작', ja: '📖 クイックスタート', 'zh-CN': '📖 快速入门', 'zh-TW': '📖 快速入門', es: '📖 Inicio rápido' },
        description: { en: 'Compile an ONNX model step by step', ko: 'ONNX 모델 컴파일을 단계별로 알아봅니다', ja: 'ONNXモデルのコンパイルをステップバイステップで学びます', 'zh-CN': '逐步编译ONNX模型', 'zh-TW': '逐步編譯ONNX模型', es: 'Compile un modelo ONNX paso a paso' },
        steps: quickStartSteps },
      { id: 'graph-viewer', icon: '📊',
        title: { en: '📊 Graph Viewer', ko: '📊 그래프 뷰어', ja: '📊 グラフビューア', 'zh-CN': '📊 模型图查看器', 'zh-TW': '📊 圖形檢視器', es: '📊 Visor de gráficos' },
        description: { en: 'Navigate and inspect compilation graphs', ko: '컴파일 그래프를 탐색하고 상세 정보를 확인합니다', ja: 'コンパイルグラフを探索して確認します', 'zh-CN': '浏览和检查编译图', 'zh-TW': '瀏覽和檢查編譯圖形', es: 'Navegue e inspeccione los gráficos de compilación' },
        steps: graphViewerSteps },
      { id: 'config-wizard', icon: '⚙️',
        title: { en: '⚙️ Config Wizard', ko: '⚙️ 설정 마법사', ja: '⚙️ 設定ウィザード', 'zh-CN': '⚙️ 配置向导', 'zh-TW': '⚙️ 設定精靈', es: '⚙️ Asistente de configuración' },
        description: { en: 'Build a compile config JSON', ko: '컴파일 설정 JSON을 생성합니다', ja: 'コンパイル設定JSONを生成します', 'zh-CN': '生成编译配置JSON', 'zh-TW': '產生編譯設定JSON', es: 'Genere un JSON de configuración de compilación' },
        steps: configWizardSteps },
      { id: 'advanced', icon: '🔬',
        title: { en: '🔬 Advanced', ko: '🔬 고급 기능', ja: '🔬 高度な機能', 'zh-CN': '🔬 高级功能', 'zh-TW': '🔬 進階功能', es: '🔬 Avanzado' },
        description: { en: 'DXQ, Quant Diagnosis, Node Selection, QXNN Resume', ko: 'DXQ 양자화, 양자화 진단, 노드 선택, QXNN 재개', ja: 'DXQ量子化、量子化診断、ノード選択、QXNN再開', 'zh-CN': 'DXQ量化、量化诊断、节点选择、QXNN恢复', 'zh-TW': 'DXQ量化、量化診斷、節點選擇、QXNN恢復', es: 'DXQ, diagnóstico cuant., selección de nodos, reanudación QXNN' },
        steps: advancedSteps },
      { id: 'agentic-auto-compile', icon: '🤖',
        title: { ko: '🤖 에이전트 자동 컴파일', en: '🤖 Agentic Auto Compile', ja: '🤖 エージェント自動コンパイル', 'zh-CN': '🤖 智能体自动编译', 'zh-TW': '🤖 代理程式自動編譯', es: '🤖 Compilación con agente' },
        description: { ko: '.deepx 에이전트로 모델 다운로드·변환·컴파일·검증을 자동화합니다', en: 'Automate model download, conversion, compilation and verification with .deepx agents', ja: '.deepx エージェントでモデルの取得・変換・コンパイル・検証を自動化します', 'zh-CN': '使用 .deepx 智能体自动化模型下载、转换、编译和验证', 'zh-TW': '使用 .deepx 代理程式自動化模型下載、轉換、編譯和驗證', es: 'Automatice la descarga, conversión, compilación y verificación de modelos con agentes .deepx' },
        steps: agenticAutoCompileSteps },
    ],
  });
})();
