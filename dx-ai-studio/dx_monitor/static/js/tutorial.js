(function () {
  'use strict';

  function _scrollTo(sel) {
    var el = document.querySelector(sel);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function _ensureMonitorDemo() {
    if (typeof renderNPUTopo !== 'function') return;
    var topo = document.getElementById('npu-topo');
    if (topo && !topo.querySelector('.npu-card')) {
      renderNPUTopo({
        mock: true,
        npus: [{
          id: 0, mock: true, temp_avg: 42.5, voltage_avg: 850, clock_avg: 1200,
          dram_pct: 35, dram_used_mb: 256, dram_total_mb: 512, utilization: [45],
          cores: 1, firmware_version: '1.0.0-mock', device_variant: 'DX-M1'
        }]
      });
    }
    if (typeof renderSysInfo === 'function') {
      var table = document.getElementById('sysinfo-table');
      if (table && !table.querySelector('tbody tr')) {
        renderSysInfo({
          os: 'Linux', hostname: 'dx-monitor-demo', cpu_model: 'Demo CPU', cpu_cores: 8,
          mem_total_gb: 32, python: '3.12', opencv: '4.x', dx_rt_version: 'demo',
          dx_app_version: 'demo', npu_count: 1, npu_pci: ['00:00.0'],
          dx_engine_available: true, sdk_version: 'demo', driver_version: 'demo',
          pcie_driver_version: 'demo', uptime: 'tutorial'
        });
      }
    }
    if (typeof renderEvents === 'function') {
      var log = document.getElementById('event-log');
      if (log && !log.querySelector('.event-row')) {
        if (typeof S !== 'undefined') {
          S.lastEvents = [{
            timestamp: Math.floor(Date.now() / 1000),
            level: 'INFO',
            message: 'Tutorial demo event — monitor heartbeat OK'
          }];
        }
        renderEvents();
      }
    }
    if (typeof S !== 'undefined') S.isMock = true;
    if (typeof _updateMockBanner === 'function') _updateMockBanner();
  }

  function _clearMonitorMock() {
    if (typeof S !== 'undefined') S.isMock = false;
    if (typeof _updateMockBanner === 'function') _updateMockBanner();
  }

  var sections = [

    { id: 'overview', icon: '🖥️',
      title: { ko: '🖥️ 모니터 개요', en: '🖥️ Monitor Overview', ja: '🖥️ モニター概要', 'zh-CN': '🖥️ 监控概述', 'zh-TW': '🖥️ 監控概述', es: '🖥️ Resumen del monitor' },
      description: { ko: 'DX Monitor의 전체 레이아웃과 주요 기능 소개', en: 'Introduction to the overall layout and key features of DX Monitor', ja: 'DX Monitorの全体レイアウトと主要機能の紹介', 'zh-CN': 'DX Monitor的整体布局和主要功能介绍', 'zh-TW': 'DX Monitor的整體佈局和主要功能介紹', es: 'Introducción al diseño general y funciones principales de DX Monitor' },
      steps: [
        { target: '.app-title', position: 'bottom',
          title: { ko: 'DX Monitor', en: 'DX Monitor', ja: 'DX Monitor', 'zh-CN': 'DX Monitor', 'zh-TW': 'DX Monitor', es: 'DX Monitor' },
          content: { ko: '<strong>DX Monitor</strong>는 NPU의 온도·전압·클럭·DRAM, CPU, 메모리, 런타임 이벤트를 <strong>실시간으로 추적</strong>하는 모니터링 도구입니다.', en: '<strong>DX Monitor</strong> tracks NPU temperature, voltage, clock, DRAM, CPU, memory, and runtime events in <strong>real time</strong>.', ja: '<strong>DX Monitor</strong>はNPUの温度・電圧・クロック・DRAM、CPU、メモリ、ランタイムイベントを<strong>リアルタイムで追跡</strong>する監視ツールです。', 'zh-CN': '<strong>DX Monitor</strong>实时追踪NPU温度、电压、时钟、DRAM、CPU、内存和运行时事件。', 'zh-TW': '<strong>DX Monitor</strong>即時追蹤NPU溫度、電壓、時脈、DRAM、CPU、記憶體和執行時事件。', es: '<strong>DX Monitor</strong> rastrea en <strong>tiempo real</strong> la temperatura, voltaje, reloj y DRAM del NPU, CPU, memoria y eventos de tiempo de ejecución.' } },
        { target: '#dxToolbar', position: 'left',
          title: { ko: '공유 툴바', en: 'Shared Toolbar', ja: '共有ツールバー', 'zh-CN': '共享工具栏', 'zh-TW': '共用工具列', es: 'Barra de herramientas compartida' },
          content: { ko: '언어 선택, 튜토리얼 컨트롤, 런처 동기화 기능을 제공하는 <strong>공유 툴바</strong>입니다.', en: '<strong>Shared Toolbar</strong> provides language selection, tutorial controls, and launcher synchronization.', ja: '言語選択、チュートリアルコントロール、ランチャー同期機能を提供する<strong>共有ツールバー</strong>です。', 'zh-CN': '<strong>共享工具栏</strong>提供语言选择、教程控件和启动器同步功能。', 'zh-TW': '<strong>共用工具列</strong>提供語言選擇、教學控制項和啟動器同步功能。', es: 'La <strong>barra de herramientas compartida</strong> ofrece selección de idioma, controles de tutorial y sincronización con el launcher.' },
          beforeStep: function () { _scrollTo('#dxToolbar'); } },
        { target: '#langToggle', position: 'left',
          title: { ko: '언어 전환', en: 'Language Toggle', ja: '言語切替', 'zh-CN': '语言切换', 'zh-TW': '語言切換', es: 'Cambio de idioma' },
          content: { ko: '클릭하면 UI 언어를 전환합니다. 모든 텍스트가 즉시 변경되며, 설정은 브라우저에 저장됩니다.', en: 'Click to switch the UI language. All text changes instantly and the setting is saved in the browser.', ja: 'クリックするとUI言語を切り替えます。すべてのテキストが即座に変更され、設定はブラウザに保存されます。', 'zh-CN': '点击切换UI语言。所有文本即时更改，设置保存在浏览器中。', 'zh-TW': '點擊切換UI語言。所有文字即時變更，設定儲存於瀏覽器中。', es: 'Haga clic para cambiar el idioma de la interfaz. Todo el texto se actualiza al instante y la configuración se guarda en el navegador.' },
          beforeStep: function () { _scrollTo('#langToggle'); } },
      ]
    },

    { id: 'controls', icon: '🎛️',
      title: { ko: '🎛️ 상태 및 컨트롤', en: '🎛️ Status & Controls', ja: '🎛️ ステータスとコントロール', 'zh-CN': '🎛️ 状态与控制', 'zh-TW': '🎛️ 狀態與控制' , es: '🎛️ Estado y controles' },
      description: { ko: '상태 카드, 시간 범위, 메트릭 모드 컨트롤', en: 'Status cards, time range, and metric mode controls', ja: 'ステータスカード、時間範囲、メトリックモードコントロール', 'zh-CN': '状态卡片、时间范围和指标模式控件', 'zh-TW': '狀態卡片、時間範圍和指標模式控制項' , es: 'Tarjetas de estado, rango temporal y controles de modo de métricas' },
      prerequisite: 'overview',
      prerequisiteMessage: { ko: '먼저 개요 섹션을 완료하세요.', en: 'Complete the Overview section first.', ja: '先に概要セクションを完了してください。', 'zh-CN': '请先完成概述部分。', 'zh-TW': '請先完成概述部分。' , es: 'Complete primero la sección de resumen.' },
      steps: [
        { target: '#status-bar', position: 'bottom',
          title: { ko: '상태 카드', en: 'Status Cards', ja: 'ステータスカード', 'zh-CN': '状态卡片', 'zh-TW': '狀態卡片' , es: 'Tarjetas de estado' },
          content: { ko: '상단 카드는 현재 NPU/시스템 상태를 요약하며, <strong>경고/위험 임계값</strong>을 시각적으로 표시합니다.', en: 'Top cards summarize current NPU/system health and display <strong>warning/critical thresholds</strong> visually.', ja: '上部カードは現在のNPU/システム状態を要約し、<strong>警告/危険しきい値</strong>を視覚的に表示します。', 'zh-CN': '顶部卡片汇总当前NPU/系统运行状态，并直观显示<strong>警告/危急阈值</strong>。', 'zh-TW': '頂部卡片摘要當前NPU/系統運行狀態，並直觀顯示<strong>警告/危急閾值</strong>。' , es: 'Las tarjetas superiores resumen el estado actual del NPU/sistema y muestran visualmente los <strong>umbrales de advertencia/críticos</strong>.' },
          beforeStep: function () { _scrollTo('#status-bar'); } },
        { target: '#time-range-btns', position: 'bottom',
          title: { ko: '시간 범위', en: 'Time Range', ja: '時間範囲', 'zh-CN': '时间范围', 'zh-TW': '時間範圍' , es: 'Rango temporal' },
          content: { ko: '<strong>실시간, 5분, 15분, 30분, 1시간, 전체 히스토리</strong> 중 원하는 시간 창을 선택합니다.', en: 'Select a time window: <strong>realtime, 5m, 15m, 30m, 1h, and all-history</strong>.', ja: '<strong>リアルタイム、5分、15分、30分、1時間、全履歴</strong>から時間ウィンドウを選択します。', 'zh-CN': '选择时间窗口：<strong>实时、5分钟、15分钟、30分钟、1小时和全部历史</strong>。', 'zh-TW': '選擇時間窗口：<strong>即時、5分鐘、15分鐘、30分鐘、1小時和全部歷史</strong>。' , es: 'Seleccione una ventana temporal: <strong>tiempo real, 5 min, 15 min, 30 min, 1 h e historial completo</strong>.' },
          beforeStep: function () {
            _scrollTo('#time-range-btns');
            if (typeof setTimeRange === 'function') setTimeRange('rt');
          } },
        { target: '#chart-mode-btns', position: 'bottom',
          title: { ko: '메트릭 모드', en: 'Metric Modes', ja: 'メトリックモード', 'zh-CN': '指标模式', 'zh-TW': '指標模式' , es: 'Modos de métricas' },
          content: { ko: '<strong>온도, 전압, 클럭, DRAM, 사용률, CPU, 메모리, 코어 차트</strong> 및 <strong>전체 보기</strong> 모드 간에 전환합니다.', en: 'Switch among <strong>temperature, voltage, clock, DRAM, utilization, CPU, memory, core charts</strong>, and <strong>view-all</strong> mode.', ja: '<strong>温度、電圧、クロック、DRAM、使用率、CPU、メモリ、コアチャート</strong>と<strong>全体表示</strong>モードを切り替えます。', 'zh-CN': '在<strong>温度、电压、时钟、DRAM、利用率、CPU、内存、核心图表</strong>和<strong>查看全部</strong>模式间切换。', 'zh-TW': '在<strong>溫度、電壓、時脈、DRAM、使用率、CPU、記憶體、核心圖表</strong>和<strong>檢視全部</strong>模式間切換。' , es: 'Alterne entre <strong>temperatura, voltaje, reloj, DRAM, utilización, CPU, memoria, gráficos de núcleos</strong> y el modo <strong>ver todo</strong>.' },
          beforeStep: function () {
            _scrollTo('#chart-mode-btns');
            if (typeof setChartMode === 'function') setChartMode('temp');
          } },
      ]
    },

    { id: 'charts', icon: '📈',
      title: { ko: '📈 차트 모니터링', en: '📈 Chart Monitoring', ja: '📈 チャートモニタリング', 'zh-CN': '📈 图表监控', 'zh-TW': '📈 圖表監控' , es: '📈 Monitorización de gráficos' },
      description: { ko: '차트 영역과 개별 메트릭 차트 모드', en: 'Chart area and individual metric chart modes', ja: 'チャート領域と個別メトリックチャートモード', 'zh-CN': '图表区域和各指标图表模式', 'zh-TW': '圖表區域和各指標圖表模式' , es: 'Área de gráficos y modos de gráficos de métricas individuales' },
      prerequisite: 'controls',
      prerequisiteMessage: { ko: '먼저 상태 및 컨트롤 섹션을 완료하세요.', en: 'Complete the Status & Controls section first.', ja: '先にステータスとコントロールセクションを完了してください。', 'zh-CN': '请先完成状态与控制部分。', 'zh-TW': '請先完成狀態與控制部分。' , es: 'Complete primero la sección Estado y controles.' },
      steps: [
        { target: '#chart-area', position: 'top',
          title: { ko: '차트 영역', en: 'Chart Area', ja: 'チャート領域', 'zh-CN': '图表区域', 'zh-TW': '圖表區域' , es: 'Área de gráficos' },
          content: { ko: 'NPU/시스템별 행이 스트림 히스토리에서 다시 그려지며, 선택한 <strong>모드/범위를 유지</strong>합니다.', en: 'Per-NPU/system rows redraw from streamed history without clearing the selected <strong>mode/range</strong>.', ja: 'NPU/システムごとの行がストリーム履歴から再描画され、選択した<strong>モード/範囲を維持</strong>します。', 'zh-CN': '每个NPU/系统行从流式历史重绘，不清除选定的<strong>模式/范围</strong>。', 'zh-TW': '每個NPU/系統行從串流歷史重繪，不清除選定的<strong>模式/範圍</strong>。' , es: 'Las filas por NPU/sistema se redibujan desde el historial en streaming sin borrar el <strong>modo/rango</strong> seleccionado.' },
          beforeStep: function () { _scrollTo('#chart-area'); } },
        { target: '#cm-temp', position: 'bottom',
          title: { ko: 'NPU 온도', en: 'NPU Temperature', ja: 'NPU温度', 'zh-CN': 'NPU温度', 'zh-TW': 'NPU溫度' , es: 'Temperatura del NPU' },
          content: { ko: 'NPU <strong>평균 온도</strong> 차트 모드입니다. 55°C 이상이면 경고 색상으로 표시됩니다.', en: 'NPU <strong>average temperature</strong> chart mode. Warning colors above 55°C.', ja: 'NPU<strong>平均温度</strong>チャートモードです。55°C以上で警告色が表示されます。', 'zh-CN': 'NPU<strong>平均温度</strong>图表模式。超过55°C时显示警告颜色。', 'zh-TW': 'NPU<strong>平均溫度</strong>圖表模式。超過55°C時顯示警告顏色。' , es: 'Modo de gráfico de <strong>temperatura media</strong> del NPU. Colores de advertencia por encima de 55 °C.' },
          beforeStep: function () {
            _scrollTo('#cm-temp');
            if (typeof setChartMode === 'function') setChartMode('temp');
          } },
        { target: '#cm-cpu', position: 'bottom',
          title: { ko: 'CPU 부하', en: 'CPU Load', ja: 'CPU負荷', 'zh-CN': 'CPU负载', 'zh-TW': 'CPU負載' , es: 'Carga de CPU' },
          content: { ko: '<strong>CPU 평균 부하</strong>를 차트로 추적합니다. 80%를 초과하면 프로세스를 점검하세요.', en: 'Tracks <strong>CPU average load</strong> in chart form. Investigate processes if above 80%.', ja: '<strong>CPU平均負荷</strong>をチャートで追跡します。80%を超えたらプロセスを確認してください。', 'zh-CN': '以图表追踪<strong>CPU平均负载</strong>。超过80%时请检查进程。', 'zh-TW': '以圖表追蹤<strong>CPU平均負載</strong>。超過80%時請檢查程序。' , es: 'Rastrea la <strong>carga media de CPU</strong> en forma de gráfico. Si supera el 80 %, revise los procesos.' },
          beforeStep: function () {
            _scrollTo('#cm-cpu');
            if (typeof setChartMode === 'function') setChartMode('cpu');
          } },
        { target: '#cm-util', position: 'bottom',
          title: { ko: 'NPU 사용률', en: 'NPU Utilization', ja: 'NPU使用率', 'zh-CN': 'NPU利用率', 'zh-TW': 'NPU使用率' , es: 'Utilización del NPU' },
          content: { ko: '<strong>NPU 연산 코어 사용률(%)</strong>을 추적합니다. 추론 시 상승하고 대기 시 낮게 유지됩니다.', en: 'Tracks <strong>NPU compute core utilization (%)</strong>. Rises during inference, stays low when idle.', ja: '<strong>NPU演算コア使用率（%）</strong>を追跡します。推論時に上昇し、アイドル時は低く維持されます。', 'zh-CN': '追踪<strong>NPU计算核心利用率（%）</strong>。推理时升高，空闲时保持较低。', 'zh-TW': '追蹤<strong>NPU計算核心使用率（%）</strong>。推論時升高，閒置時保持較低。' , es: 'Rastrea la <strong>utilización (%)</strong> de los núcleos de cómputo del NPU. Sube durante la inferencia y se mantiene baja en inactivo.' },
          beforeStep: function () {
            _scrollTo('#cm-util');
            if (typeof setChartMode === 'function') setChartMode('util');
          } },
        { target: '#cm-all', position: 'bottom',
          title: { ko: '전체 보기', en: 'View All', ja: '全体表示', 'zh-CN': '查看全部', 'zh-TW': '檢視全部' , es: 'Ver todo' },
          content: { ko: '모든 메트릭 차트를 <strong>그리드</strong>로 동시에 표시합니다. 전체 시스템 상태를 한눈에 파악할 수 있습니다.', en: 'Displays all metric charts in a <strong>grid</strong> simultaneously for a complete system overview at a glance.', ja: 'すべてのメトリックチャートを<strong>グリッド</strong>で同時に表示します。システム全体の状態を一目で把握できます。', 'zh-CN': '以<strong>网格</strong>同时显示所有指标图表，便于一览系统全局。', 'zh-TW': '以<strong>網格</strong>同時顯示所有指標圖表，便於一覽系統全域。' , es: 'Muestra todos los gráficos de métricas en una <strong>cuadrícula</strong> a la vez para una visión global del sistema.' },
          beforeStep: function () {
            _scrollTo('#cm-all');
            if (typeof setChartMode === 'function') setChartMode('all');
          } },
      ]
    },

    { id: 'topology', icon: '🔌',
      title: { ko: '🔌 토폴로지 및 시스템', en: '🔌 Topology & System', ja: '🔌 トポロジーとシステム', 'zh-CN': '🔌 拓扑与系统', 'zh-TW': '🔌 拓撲與系統' , es: '🔌 Topología y sistema' },
      description: { ko: 'NPU 토폴로지, 상태, 시스템 정보 테이블', en: 'NPU topology, status, and system information table', ja: 'NPUトポロジー、ステータス、システム情報テーブル', 'zh-CN': 'NPU拓扑、状态和系统信息表', 'zh-TW': 'NPU拓撲、狀態和系統資訊表' , es: 'Topología del NPU, estado y tabla de información del sistema' },
      prerequisite: 'charts',
      prerequisiteMessage: { ko: '먼저 차트 모니터링 섹션을 완료하세요.', en: 'Complete the Chart Monitoring section first.', ja: '先にチャートモニタリングセクションを完了してください。', 'zh-CN': '请先完成图表监控部分。', 'zh-TW': '請先完成圖表監控部分。' , es: 'Complete primero la sección Monitorización de gráficos.' },
      beforeStart: function () { _ensureMonitorDemo(); },
      steps: [
        { target: '#npu-topo', position: 'right',
          title: { ko: 'NPU 토폴로지', en: 'NPU Topology', ja: 'NPUトポロジー', 'zh-CN': 'NPU拓扑', 'zh-TW': 'NPU拓撲' , es: 'Topología del NPU' },
          content: { ko: '각 NPU 디바이스의 <strong>온도, 전압, 클럭, DRAM, 사용률</strong>과 펌웨어/칩/보드 메타데이터를 표시합니다.', en: 'Shows per-device <strong>temperature, voltage, clock, DRAM, utilization</strong> and firmware/chip/board metadata.', ja: '各NPUデバイスの<strong>温度、電圧、クロック、DRAM、使用率</strong>とファームウェア/チップ/ボードメタデータを表示します。', 'zh-CN': '显示每个设备的<strong>温度、电压、时钟、DRAM、利用率</strong>和固件/芯片/板卡元数据。', 'zh-TW': '顯示每個裝置的<strong>溫度、電壓、時脈、DRAM、使用率</strong>和韌體/晶片/板卡中繼資料。' , es: 'Muestra por dispositivo <strong>temperatura, voltaje, reloj, DRAM, utilización</strong> y metadatos de firmware/chip/placa.' },
          beforeStep: function () { _ensureMonitorDemo(); _scrollTo('#npu-topo'); },
          afterStep: function () { _clearMonitorMock(); } },
        { target: '#npu-status-label', position: 'bottom',
          title: { ko: 'NPU 상태 배지', en: 'NPU Status Badge', ja: 'NPUステータスバッジ', 'zh-CN': 'NPU状态徽章', 'zh-TW': 'NPU狀態徽章' , es: 'Indicador de estado del NPU' },
          content: { ko: '감지된 NPU 개수 또는 <strong>모의 데이터</strong> 여부를 나타냅니다.', en: 'Shows detected NPU count or whether <strong>mock data</strong> is active.', ja: '検出されたNPU数または<strong>モックデータ</strong>の有無を示します。', 'zh-CN': '显示检测到的NPU数量或是否使用<strong>模拟数据</strong>。', 'zh-TW': '顯示偵測到的NPU數量或是否使用<strong>模擬資料</strong>。' , es: 'Muestra el número de NPUs detectados o si están activos <strong>datos simulados</strong>.' },
          beforeStep: function () { _scrollTo('#npu-status-label'); } },
        { target: '#sysinfo-table', position: 'left',
          title: { ko: '시스템 정보', en: 'System Information', ja: 'システム情報', 'zh-CN': '系统信息', 'zh-TW': '系統資訊' , es: 'Información del sistema' },
          content: { ko: 'OS, 호스트, CPU, 메모리, SDK/드라이버, PCI, DX Engine 가용성 등의 <strong>시스템 환경 정보</strong>를 테이블로 표시합니다.', en: 'Displays <strong>system environment</strong> rows: OS, host, CPU, memory, SDK/driver, PCI, and DX engine availability.', ja: 'OS、ホスト、CPU、メモリ、SDK/ドライバー、PCI、DX Engine可用性などの<strong>システム環境情報</strong>をテーブルで表示します。', 'zh-CN': '以表格显示<strong>系统环境</strong>：OS、主机、CPU、内存、SDK/驱动、PCI和DX引擎可用性。', 'zh-TW': '以表格顯示<strong>系統環境</strong>：OS、主機、CPU、記憶體、SDK/驅動、PCI和DX引擎可用性。' , es: 'Muestra en tabla la <strong>información del entorno del sistema</strong>: SO, host, CPU, memoria, SDK/driver, PCI y disponibilidad de DX Engine.' },
          beforeStep: function () { _scrollTo('#sysinfo-table'); } },
      ]
    },

    { id: 'events', icon: '📋',
      title: { ko: '📋 런타임 이벤트', en: '📋 Runtime Events', ja: '📋 ランタイムイベント', 'zh-CN': '📋 运行时事件', 'zh-TW': '📋 執行時事件' , es: '📋 Eventos de tiempo de ejecución' },
      description: { ko: '최근 모니터 이벤트와 이벤트 카운트', en: 'Recent monitor events and event count', ja: '最近のモニターイベントとイベントカウント', 'zh-CN': '最近的监控事件和事件计数', 'zh-TW': '最近的監控事件和事件計數' , es: 'Eventos recientes del monitor y recuento de eventos' },
      prerequisite: 'topology',
      prerequisiteMessage: { ko: '먼저 토폴로지 및 시스템 섹션을 완료하세요.', en: 'Complete the Topology & System section first.', ja: '先にトポロジーとシステムセクションを完了してください。', 'zh-CN': '请先完成拓扑与系统部分。', 'zh-TW': '請先完成拓撲與系統部分。' , es: 'Complete primero la sección Topología y sistema.' },
      beforeStart: function () { _ensureMonitorDemo(); },
      steps: [
        { target: '#event-log', position: 'top',
          title: { ko: '런타임 이벤트', en: 'Runtime Events', ja: 'ランタイムイベント', 'zh-CN': '运行时事件', 'zh-TW': '執行時事件' , es: 'Eventos de tiempo de ejecución' },
          content: { ko: '최근 모니터 이벤트를 <strong>심각도 배지, 타임스탬프</strong>와 함께 표시하며 자동 갱신됩니다.', en: 'Shows recent monitor events with <strong>severity badges, timestamps</strong>, and auto-refresh.', ja: '最近のモニターイベントを<strong>重大度バッジ、タイムスタンプ</strong>と共に表示し、自動更新されます。', 'zh-CN': '显示最近的监控事件，带有<strong>严重性徽章、时间戳</strong>，并自动刷新。', 'zh-TW': '顯示最近的監控事件，帶有<strong>嚴重性徽章、時間戳</strong>，並自動重新整理。' , es: 'Muestra eventos recientes del monitor con <strong>indicadores de gravedad y marcas de tiempo</strong>, con actualización automática.' },
          beforeStep: function () { _ensureMonitorDemo(); _scrollTo('#event-log'); },
          afterStep: function () { _clearMonitorMock(); } },
        { target: '#event-count', position: 'left',
          title: { ko: '이벤트 수', en: 'Event Count', ja: 'イベント数', 'zh-CN': '事件计数', 'zh-TW': '事件計數' , es: 'Recuento de eventos' },
          content: { ko: '이벤트 수 배지이며, <strong>언어 변경</strong> 시 카운트 레이블이 다시 그려집니다.', en: 'Event count badge — the count label <strong>repaints on language changes</strong>.', ja: 'イベント数バッジで、<strong>言語変更</strong>時にカウントラベルが再描画されます。', 'zh-CN': '事件计数徽章——<strong>更改语言</strong>时计数标签会自动更新。', 'zh-TW': '事件計數徽章——<strong>語言變更</strong>時計數標籤會自動更新。' , es: 'Indicador del recuento de eventos: la etiqueta del contador se <strong>vuelve a dibujar al cambiar el idioma</strong>.' },
          beforeStep: function () { _scrollTo('#event-count'); } },
      ]
    },

  ];

  var referenceDocs = [
    { id: 'sse', icon: '📡', title: { ko: 'SSE 스트림', en: 'SSE Stream', ja: 'SSEストリーム', 'zh-CN': 'SSE流', 'zh-TW': 'SSE串流' , es: 'Flujo SSE' },
      body: { ko: '<p><strong>Server-Sent Events (SSE)</strong>를 통해 <code>/api/hw_stream</code>에서 ~1.5초마다 NPU·시스템 데이터를 실시간으로 수신합니다.</p><p>SSE를 사용할 수 없는 환경(리버스 프록시 등)에서는 6초 이내에 응답이 없으면 자동으로 <strong>3초 폴링</strong> 방식으로 전환됩니다.</p><p>30초 후 SSE 재연결을 시도합니다.</p>', en: '<p>Receives NPU & system data every ~1.5s from <code>/api/hw_stream</code> via <strong>Server-Sent Events (SSE)</strong>.</p><p>Automatically falls back to <strong>3s polling</strong> if no SSE response within 6s (e.g., behind a reverse proxy).</p><p>Attempts SSE reconnect after 30s.</p>', ja: '<p><strong>Server-Sent Events（SSE）</strong>を通じて<code>/api/hw_stream</code>から約1.5秒ごとにNPU・システムデータをリアルタイムで受信します。</p><p>SSEが利用できない環境（リバースプロキシなど）では、6秒以内に応答がない場合自動的に<strong>3秒ポーリング</strong>方式に切り替わります。</p><p>30秒後にSSE再接続を試みます。</p>', 'zh-CN': '<p>通过<strong>Server-Sent Events（SSE）</strong>从<code>/api/hw_stream</code>约每1.5秒实时接收NPU和系统数据。</p><p>如果6秒内没有SSE响应（例如在反向代理后），自动回退到<strong>3秒轮询</strong>方式。</p><p>30秒后尝试重新连接SSE。</p>', 'zh-TW': '<p>透過<strong>Server-Sent Events（SSE）</strong>從<code>/api/hw_stream</code>約每1.5秒即時接收NPU和系統資料。</p><p>如果6秒內沒有SSE回應（例如在反向代理後），自動回退到<strong>3秒輪詢</strong>方式。</p><p>30秒後嘗試重新連接SSE。</p>', es: '<p>Recibe datos del NPU y del sistema cada ~1,5 s desde <code>/api/hw_stream</code> mediante <strong>Server-Sent Events (SSE)</strong>.</p><p>Si no hay respuesta SSE en 6 s (p. ej., detrás de un proxy inverso), cambia automáticamente a <strong>sondeo cada 3 s</strong>.</p><p>Intenta reconectar SSE tras 30 s.</p>' } },
    { id: 'mock', icon: '🧪', title: { ko: 'Mock 데이터', en: 'Mock Data', ja: 'モックデータ', 'zh-CN': '模拟数据', 'zh-TW': '模擬資料' , es: 'Datos simulados' },
      body: { ko: '<p>NPU가 연결되지 않은 환경에서는 <strong>시뮬레이션 데이터(Mock)</strong>로 동작합니다. NPU 상태 배지에 "모의 데이터"가 표시됩니다.</p><p>CPU, 메모리, 디스크는 실제 값을 사용합니다.</p>', en: '<p>Operates with <strong>simulated (mock) data</strong> when no NPU is connected. The NPU status badge shows "Mock Data".</p><p>CPU, memory, and disk values are always real.</p>', ja: '<p>NPUが接続されていない環境では<strong>シミュレーションデータ（モック）</strong>で動作します。NPUステータスバッジに「モックデータ」と表示されます。</p><p>CPU、メモリ、ディスクは実際の値を使用します。</p>', 'zh-CN': '<p>当没有NPU连接时，使用<strong>模拟（Mock）数据</strong>运行。NPU状态徽章显示“模拟数据”。</p><p>CPU、内存和磁盘始终使用真实值。</p>', 'zh-TW': '<p>當沒有NPU連接時，使用<strong>模擬（Mock）資料</strong>運行。NPU狀態徽章顯示「模擬資料」。</p><p>CPU、記憶體和磁碟始終使用真實值。</p>', es: '<p>Funciona con <strong>datos simulados (mock)</strong> cuando no hay NPU conectado. El indicador de estado del NPU muestra «Mock Data».</p><p>Los valores de CPU, memoria y disco son siempre reales.</p>' } },
    { id: 'temp-color', icon: '🌡️', title: { ko: '온도 색상 코딩', en: 'Temperature Color Coding', ja: '温度カラーコーディング', 'zh-CN': '温度颜色编码', 'zh-TW': '溫度顏色編碼' , es: 'Codificación de color por temperatura' },
      body: { ko: '<ul><li>🟢 <strong>< 40°C</strong>: 정상</li><li>🟡 <strong>40–55°C</strong>: 주의</li><li>🔴 <strong>> 55°C</strong>: 경고 — 냉각 환경 점검 권장</li></ul>', en: '<ul><li>🟢 <strong>< 40°C</strong>: Normal</li><li>🟡 <strong>40–55°C</strong>: Caution</li><li>🔴 <strong>> 55°C</strong>: Warning — check cooling environment</li></ul>', ja: '<ul><li>🟢 <strong>< 40°C</strong>: 正常</li><li>🟡 <strong>40–55°C</strong>: 注意</li><li>🔴 <strong>> 55°C</strong>: 警告 — 冷却環境の確認を推奨</li></ul>', 'zh-CN': '<ul><li>🟢 <strong>< 40°C</strong>: 正常</li><li>🟡 <strong>40–55°C</strong>: 注意</li><li>🔴 <strong>> 55°C</strong>: 警告 — 建议检查散热环境</li></ul>', 'zh-TW': '<ul><li>🟢 <strong>< 40°C</strong>: 正常</li><li>🟡 <strong>40–55°C</strong>: 注意</li><li>🔴 <strong>> 55°C</strong>: 警告 — 建議檢查散熱環境</li></ul>', es: '<ul><li>🟢 <strong>< 40 °C</strong>: Normal</li><li>🟡 <strong>40–55 °C</strong>: Precaución</li><li>🔴 <strong>> 55 °C</strong>: Advertencia — revise el entorno de refrigeración</li></ul>' } },
    { id: 'metrics', icon: '📊', title: { ko: '메트릭 설명', en: 'Metric Descriptions', ja: 'メトリック説明', 'zh-CN': '指标说明', 'zh-TW': '指標說明' , es: 'Descripción de métricas' },
      body: { ko: '<table style="width:100%;border-collapse:collapse"><tr><th style="text-align:left">메트릭</th><th>단위</th><th>설명</th></tr><tr><td>🌡️ NPU 온도</td><td>°C</td><td>NPU 다이 평균 온도</td></tr><tr><td>⚡ 전압</td><td>mV</td><td>NPU 전원 전압</td></tr><tr><td>🔄 클럭</td><td>MHz</td><td>NPU 동작 클럭</td></tr><tr><td>🌡️ 코어 온도</td><td>°C</td><td>NPU 코어별 온도</td></tr><tr><td>💻 CPU 부하</td><td>-</td><td>CPU 평균 로드 (코어 정규화)</td></tr><tr><td>🧠 메모리</td><td>%</td><td>시스템 RAM 사용률</td></tr><tr><td>💾 NPU DRAM</td><td>%</td><td>NPU 전용 DRAM 사용률</td></tr><tr><td>⚙️ NPU 사용률</td><td>%</td><td>NPU 연산 코어 사용률</td></tr></table>', en: '<table style="width:100%;border-collapse:collapse"><tr><th style="text-align:left">Metric</th><th>Unit</th><th>Description</th></tr><tr><td>🌡️ NPU Temp</td><td>°C</td><td>NPU die average temperature</td></tr><tr><td>⚡ Voltage</td><td>mV</td><td>NPU supply voltage</td></tr><tr><td>🔄 Clock</td><td>MHz</td><td>NPU operating clock</td></tr><tr><td>🌡️ Core Temp</td><td>°C</td><td>Per-core NPU temperatures</td></tr><tr><td>💻 CPU Load</td><td>-</td><td>CPU avg load (normalized by cores)</td></tr><tr><td>🧠 Memory</td><td>%</td><td>System RAM usage</td></tr><tr><td>💾 NPU DRAM</td><td>%</td><td>NPU dedicated DRAM usage</td></tr><tr><td>⚙️ NPU Util</td><td>%</td><td>NPU compute core utilization</td></tr></table>', ja: '<table style="width:100%;border-collapse:collapse"><tr><th style="text-align:left">メトリック</th><th>単位</th><th>説明</th></tr><tr><td>🌡️ NPU温度</td><td>°C</td><td>NPUダイ平均温度</td></tr><tr><td>⚡ 電圧</td><td>mV</td><td>NPU電源電圧</td></tr><tr><td>🔄 クロック</td><td>MHz</td><td>NPU動作クロック</td></tr><tr><td>🌡️ コア温度</td><td>°C</td><td>NPUコア別温度</td></tr><tr><td>💻 CPU負荷</td><td>-</td><td>CPU平均ロード（コア正規化）</td></tr><tr><td>🧠 メモリ</td><td>%</td><td>システムRAM使用率</td></tr><tr><td>💾 NPU DRAM</td><td>%</td><td>NPU専用DRAM使用率</td></tr><tr><td>⚙️ NPU使用率</td><td>%</td><td>NPU演算コア使用率</td></tr></table>', 'zh-CN': '<table style="width:100%;border-collapse:collapse"><tr><th style="text-align:left">指标</th><th>单位</th><th>说明</th></tr><tr><td>🌡️ NPU温度</td><td>°C</td><td>NPU芯片平均温度</td></tr><tr><td>⚡ 电压</td><td>mV</td><td>NPU供电电压</td></tr><tr><td>🔄 时钟</td><td>MHz</td><td>NPU工作时钟</td></tr><tr><td>🌡️ 核心温度</td><td>°C</td><td>NPU各核心温度</td></tr><tr><td>💻 CPU负载</td><td>-</td><td>CPU平均负载（按核心归一化）</td></tr><tr><td>🧠 内存</td><td>%</td><td>系统RAM使用率</td></tr><tr><td>💾 NPU DRAM</td><td>%</td><td>NPU专用DRAM使用率</td></tr><tr><td>⚙️ NPU利用率</td><td>%</td><td>NPU计算核心利用率</td></tr></table>', 'zh-TW': '<table style="width:100%;border-collapse:collapse"><tr><th style="text-align:left">指標</th><th>單位</th><th>說明</th></tr><tr><td>🌡️ NPU溫度</td><td>°C</td><td>NPU晶片平均溫度</td></tr><tr><td>⚡ 電壓</td><td>mV</td><td>NPU供電電壓</td></tr><tr><td>🔄 時脈</td><td>MHz</td><td>NPU工作時脈</td></tr><tr><td>🌡️ 核心溫度</td><td>°C</td><td>NPU各核心溫度</td></tr><tr><td>💻 CPU負載</td><td>-</td><td>CPU平均負載（按核心歸一化）</td></tr><tr><td>🧠 記憶體</td><td>%</td><td>系統RAM使用率</td></tr><tr><td>💾 NPU DRAM</td><td>%</td><td>NPU專用DRAM使用率</td></tr><tr><td>⚙️ NPU使用率</td><td>%</td><td>NPU計算核心使用率</td></tr></table>', es: '<table style="width:100%;border-collapse:collapse"><tr><th style="text-align:left">Métrica</th><th>Unidad</th><th>Descripción</th></tr><tr><td>🌡️ Temp. NPU</td><td>°C</td><td>Temperatura media del die del NPU</td></tr><tr><td>⚡ Voltaje</td><td>mV</td><td>Voltaje de alimentación del NPU</td></tr><tr><td>🔄 Reloj</td><td>MHz</td><td>Reloj de funcionamiento del NPU</td></tr><tr><td>🌡️ Temp. del núcleo</td><td>°C</td><td>Temperaturas por núcleo del NPU</td></tr><tr><td>💻 Carga de CPU</td><td>-</td><td>Carga media de CPU (normalizada por núcleos)</td></tr><tr><td>🧠 Memoria</td><td>%</td><td>Uso de RAM del sistema</td></tr><tr><td>💾 NPU DRAM</td><td>%</td><td>Uso de DRAM dedicada del NPU</td></tr><tr><td>⚙️ Util. NPU</td><td>%</td><td>Utilización de núcleos de cómputo del NPU</td></tr></table>' } }  ];

  window.DXTutorial.create({
    appId: 'monitor',
    sections: sections,
    referenceDocs: referenceDocs,
    toolbarSelector: '#dxToolbar',
    skipButtons: true,
    getLang: function () {
      if (typeof DXI18n !== 'undefined' && DXI18n.lang) return DXI18n.lang;
      return localStorage.getItem('dx-lang') || 'en';
    },
    onNav: function () {},
    onComplete: function (sectionId) {
      var engine = window._dxTutorial;
      var lang = engine.getLang();
      var sec = engine.sections.find(function (s) { return s.id === sectionId; });
      if (sec) {
        var msg = '✅ "' + engine._t(sec.title) + '" ' + engine._tl('tutorial complete!');
        if (typeof toast === 'function') toast(msg, 'ok');
        else console.info('[DXTutorial]', msg);
      }
    }
  });

})();
