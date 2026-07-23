/* ═══════════════════════════════════════════════════════════════
   DX EdgeGuide — Workspace Tutorial Definitions
   Progressive workspace, 6-language help metadata
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  function ensureWorkspaceRecommendation() {
    if (typeof runRecommendation === 'function' && typeof PlannerWorkspace !== 'undefined' && !PlannerWorkspace.hasStarted()) {
      runRecommendation();
      PlannerWorkspace.showRecommendations();
    }
  }

  function ensureWorkspaceDetail() {
    ensureWorkspaceRecommendation();
    var first = document.querySelector('#recommend-cards .rec-card');
    if (first) first.click();
  }

  function _scrollTo(sel) {
    var el = document.querySelector(sel);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  /* Instant (non-smooth) scroll so the target is settled before the engine measures
     the spotlight ~150ms after beforeStep — smooth scroll would still be mid-flight. */
  function _reveal(sel) {
    var el = document.querySelector(sel);
    if (!el) return;
    if (el.hidden) el.hidden = false;  // un-hide elements gated behind the `hidden` attribute
    el.scrollIntoView({ block: 'center' });
  }

  /* The priority drawer opens/closes with a ~0.42s CSS transition. If the spotlight is
     captured mid-transition its box is mis-sized and never refreshed. Resolve only once
     the drawer geometry has settled (transitionend, with a timeout fallback for the
     no-transition / reduced-motion cases). */
  function _awaitDrawerSettled() {
    var drawer = document.getElementById('requirementsStep2');
    return new Promise(function (resolve) {
      if (!drawer) { setTimeout(resolve, 60); return; }
      var done = false;
      var onEnd = function (e) {
        if (e.target !== drawer) return;
        if (e.propertyName === 'width' || e.propertyName === 'max-width' || e.propertyName === 'transform') finish();
      };
      var finish = function () {
        if (done) return;
        done = true;
        drawer.removeEventListener('transitionend', onEnd);
        resolve();
      };
      drawer.addEventListener('transitionend', onEnd);
      setTimeout(finish, 520);
    });
  }

  function _openPriorityPanel() {
    if (typeof WizardController !== 'undefined' && WizardController.goToSetupStep) {
      WizardController.goToSetupStep(2);
      if (WizardController.unlockSetupSteps) WizardController.unlockSetupSteps();
    } else {
      var btn = document.getElementById('btnSetupNext');
      if (btn && !btn.hidden) btn.click();
    }
    var stage = document.getElementById('requirementsWizardStage');
    if (stage) stage.classList.add('is-priority-open');
    return _awaitDrawerSettled();
  }

  /* The "Next → priority" step spotlights #btnSetupNext, but once a recommendation has
     run _syncSetupSteps() forces that button hidden (showBoth => both panels shown, no
     Next). Restore the step-1 view: collapse the drawer and force the Next button visible
     so the step has a real, aligned target, then wait for the collapse to settle. */
  function _revealSetupNext() {
    _ensureSetupStep1();
    var stage = document.getElementById('requirementsWizardStage');
    var step2 = document.getElementById('requirementsStep2');
    var next = document.getElementById('btnSetupNext');
    var back = document.getElementById('btnSetupBack');
    if (stage) stage.classList.remove('is-priority-open');
    if (step2) step2.setAttribute('aria-hidden', 'true');
    if (next) next.hidden = false;
    if (back) back.hidden = true;
    return _awaitDrawerSettled();
  }

  function _ensureSetupStep1() {
    if (typeof WizardController !== 'undefined' && WizardController.resetSetupForTutorial) {
      WizardController.resetSetupForTutorial();
    } else if (typeof WizardController !== 'undefined' && WizardController.goToSetupStep) {
      WizardController.goToSetupStep(1);
    }
  }

  var sections = [
    { id: 'overview', icon: '🏠',
      title: { ko: '🏠 전체 소개', en: '🏠 Overview', ja: '🏠 概要', 'zh-CN': '🏠 概述', 'zh-TW': '🏠 概述', es: '🏠 Resumen general' },
      description: { ko: 'EdgeGuide 한 화면 워크스페이스 구성 소개', en: 'Introduction to the EdgeGuide single-screen workspace', ja: 'EdgeGuideの1画面ワークスペースの紹介', 'zh-CN': 'EdgeGuide单屏工作区介绍', 'zh-TW': 'EdgeGuide單一畫面工作區介紹', es: 'Introducción al espacio de trabajo de una sola pantalla de DX EdgeGuide' },
      steps: [
        { target: '.planner-topbar', position: 'bottom',
          title: { ko: 'DX EdgeGuide', en: 'DX EdgeGuide', ja: 'DX EdgeGuide', 'zh-CN': 'DX EdgeGuide', 'zh-TW': 'DX EdgeGuide', es: 'DX EdgeGuide' },
          content: { ko: '워크로드 조건을 입력하면 DEEPX Edge AI 제품을 추천하고, 선택한 추천의 상세 수치까지 한 화면에서 확인합니다.', en: 'Enter workload requirements, get DEEPX Edge AI recommendations, and inspect selected metrics in one workspace.', ja: 'ワークロード条件を入力し、DEEPX Edge AI製品の推奨と選択項目の詳細指標を1つのワークスペースで確認します。', 'zh-CN': '输入工作负载条件，在一个工作区中查看DEEPX Edge AI推荐和所选指标详情。', 'zh-TW': '輸入工作負載條件，在一個工作區中查看DEEPX Edge AI推薦和所選指標詳情。', es: 'Ingrese los requisitos de la carga de trabajo, obtenga recomendaciones de productos DEEPX Edge AI y consulte las métricas seleccionadas en un solo espacio de trabajo.' } },
        { target: '#plannerWorkspace', position: 'bottom',
          title: { ko: 'Progressive workspace', en: 'Progressive workspace', ja: 'Progressive workspace', 'zh-CN': 'Progressive workspace', 'zh-TW': 'Progressive workspace', es: 'Espacio de trabajo progresivo' },
          content: { ko: '처음에는 조건 패널만 보이고, 추천 실행 후 결과 패널이 열리며, 추천 항목을 선택하면 상세/비교 패널이 추가됩니다.', en: 'The requirements panel appears first, recommendations open after the button action, and details appear after selecting a card.', ja: '最初は要件パネルのみ表示され、推奨実行後に結果パネル、カード選択後に詳細パネルが表示されます。', 'zh-CN': '初始只显示条件面板，执行推荐后打开结果面板，选择卡片后显示详情面板。', 'zh-TW': '初始只顯示條件面板，執行推薦後打開結果面板，選擇卡片後顯示詳情面板。', es: 'Al inicio solo aparece el panel de requisitos; tras ejecutar la recomendación se abre el panel de resultados y, al seleccionar una tarjeta, se añade el panel de detalle y comparación.' } },
        { target: '#langToggle', position: 'left',
          title: { ko: '언어 전환', en: 'Language toggle', ja: '言語切り替え', 'zh-CN': '语言切换', 'zh-TW': '語言切換', es: 'Selector de idioma' },
          content: { ko: '상단 언어 버튼으로 UI와 튜토리얼 문구를 전환합니다.', en: 'Use the language button to switch both UI and tutorial text.', ja: '上部の言語ボタンでUIとチュートリアル文を切り替えます。', 'zh-CN': '使用顶部语言按钮切换界面和教程文本。', 'zh-TW': '使用頂部語言按鈕切換介面和教學文字。', es: 'Utilice el botón de idioma en la parte superior para cambiar la interfaz y los textos del tutorial.' },
          beforeStep: function () { _scrollTo('#langToggle'); } },
        { target: '#scopeBanner', position: 'bottom',
          title: { ko: '벤치마크 범위', en: 'Benchmark scope', ja: 'ベンチマーク範囲', 'zh-CN': '基准范围', 'zh-TW': '基準範圍', es: 'Alcance del benchmark' },
          content: { ko: 'YOLO26 DX Benchmark 실측 데이터만 사용한다는 범위 안내입니다. 다른 모델은 Benchmark / Model Zoo에서 확인하세요.', en: 'Explains that rankings use YOLO26 DX Benchmark measurements only. Use Benchmark / Model Zoo for other models.', ja: 'YOLO26 DX Benchmark 実測データのみを使う旨を示します。他モデルは Benchmark / Model Zoo で確認してください。', 'zh-CN': '说明排名仅使用 YOLO26 DX Benchmark 实测数据。其他模型请在 Benchmark / Model Zoo 查看。', 'zh-TW': '說明排名僅使用 YOLO26 DX Benchmark 實測資料。其他模型請在 Benchmark / Model Zoo 查看。', es: 'Indica que las recomendaciones usan solo mediciones DX Benchmark de YOLO26. Para otros modelos, use Benchmark / Model Zoo.' } },
        { target: '#workflowSteps', position: 'bottom',
          title: { ko: '4단계 흐름', en: 'Four-step flow', ja: '4段階フロー', 'zh-CN': '四步流程', 'zh-TW': '四步流程', es: 'Flujo de cuatro pasos' },
          content: { ko: '시나리오 → 추천 → 근거 → 구매 순으로 진행합니다. 각 단계가 열리면 단계 표시가 갱신됩니다.', en: 'Progress through Scenario → Pick → Evidence → Buy. Step markers update as each panel opens.', ja: 'シナリオ → 推奨 → 根拠 → 購入の順に進みます。各パネルが開くとステップ表示が更新されます。', 'zh-CN': '按 场景 → 推荐 → 依据 → 购买 推进。每打开一个面板，步骤标记会更新。', 'zh-TW': '依 情境 → 推薦 → 依據 → 購買 推進。每開啟一個面板，步驟標記會更新。', es: 'Avance por Escenario → Elegir → Evidencia → Comprar. Los indicadores se actualizan al abrir cada panel.' } },
        { target: '#scopeBanner [data-open-methodology]', position: 'bottom',
          title: { ko: '추천 원리', en: 'How ranking works', ja: '推奨の仕組み', 'zh-CN': '推荐原理', 'zh-TW': '推薦原理', es: 'Cómo funciona el ranking' },
          content: { ko: '노란 원리 버튼을 누르면 산출식, 데이터 출처, 면책 안내가 포함된 방법론 대화상자가 열립니다.', en: 'The yellow methodology button opens a dialog with formulas, data sources, and disclaimer notes.', ja: '黄色の原理解説ボタンで、計算式・データ出典・免責事項を含む方法論ダイアログが開きます。', 'zh-CN': '点击黄色原理按钮可打开含公式、数据来源与免责声明的方法论对话框。', 'zh-TW': '點擊黃色原理按鈕可開啟含公式、資料來源與免責聲明的方法論對話框。', es: 'El botón amarillo de metodología abre un diálogo con fórmulas, fuentes de datos y avisos legales.' },
          beforeStep: function () { _reveal('#scopeBanner [data-open-methodology]'); } }
      ]
    },

    { id: 'requirements', icon: '⚙️',
      title: { ko: '⚙️ 조건 설정', en: '⚙️ Requirements', ja: '⚙️ 要件設定', 'zh-CN': '⚙️ 条件设置', 'zh-TW': '⚙️ 條件設定', es: '⚙️ Configuración de requisitos' },
      description: { ko: 'AI 작업, 모델 크기, 채널, FPS, 런타임, 우선순위 설정', en: 'Configure task, model size, channels, FPS, runtime, and priority', ja: 'AIタスク、モデルサイズ、チャンネル、FPS、ランタイム、優先度を設定', 'zh-CN': '配置任务、模型大小、通道、FPS、运行时和优先级', 'zh-TW': '設定任務、模型大小、通道、FPS、執行環境和優先順序', es: 'Configure la tarea de IA, el tamaño del modelo, los canales, el FPS, el entorno de ejecución y la prioridad' },
      beforeStart: function () { _ensureSetupStep1(); },
      steps: [
        { target: '#requirementsPanel', position: 'right',
          title: { ko: '조건 패널', en: 'Requirements panel', ja: '要件パネル', 'zh-CN': '条件面板', 'zh-TW': '條件面板', es: 'Panel de requisitos' },
          content: { ko: '추천에 필요한 모든 입력값을 이 패널에서 조정합니다. 첫 추천 이후 변경 사항은 자동으로 결과에 반영됩니다.', en: 'Adjust all inputs for recommendation here. After the first run, changes refresh results automatically.', ja: '推奨に必要な入力をここで調整します。初回実行後の変更は自動で結果へ反映されます。', 'zh-CN': '在此调整推荐所需的全部输入。首次运行后，变更会自动刷新结果。', 'zh-TW': '在此調整推薦所需的全部輸入。首次執行後，變更會自動重新整理結果。', es: 'Ajuste en este panel todos los valores de entrada para la recomendación. Tras la primera ejecución, los cambios se reflejan automáticamente en los resultados.' } },
        { target: '#scenarioChips', position: 'bottom',
          title: { ko: '빠른 시나리오', en: 'Quick scenarios', ja: 'クイックシナリオ', 'zh-CN': '快速场景', 'zh-TW': '快速情境', es: 'Escenarios rápidos' },
          content: { ko: 'CCTV, 리테일, 포즈 등 자주 쓰는 조합을 한 번에 채웁니다. 이후 우선순위 단계로 이동합니다.', en: 'Prefill common CCTV, retail, and pose workloads, then continue to the priority step.', ja: 'CCTV、小売、ポーズなどよく使う条件を一括入力し、優先度ステップへ進みます。', 'zh-CN': '一键填入常见 CCTV、零售、姿态等组合，然后进入优先级步骤。', 'zh-TW': '一鍵填入常見 CCTV、零售、姿態等組合，然後進入優先順序步驟。', es: 'Complete de un clic escenarios habituales (CCTV, retail, pose) y pase al paso de prioridad.' } },
        { target: '#task-card', position: 'bottom',
          title: { ko: 'AI 작업 유형', en: 'AI task type', ja: 'AIタスクタイプ', 'zh-CN': 'AI任务类型', 'zh-TW': 'AI任務類型', es: 'Tipo de tarea de IA' },
          content: { ko: 'Object Detection, Pose, Segmentation 등 실행할 모델 태스크를 선택합니다.', en: 'Choose the model task such as Object Detection, Pose, or Segmentation.', ja: 'Object Detection、Pose、Segmentationなど実行するモデルタスクを選択します。', 'zh-CN': '选择Object Detection、Pose、Segmentation等模型任务。', 'zh-TW': '選擇Object Detection、Pose、Segmentation等模型任務。', es: 'Seleccione la tarea del modelo que desee ejecutar, como Object Detection, Pose o Segmentation.' } },
        { target: '#size-card', position: 'bottom',
          title: { ko: '모델 크기', en: 'Model size', ja: 'モデルサイズ', 'zh-CN': '模型大小', 'zh-TW': '模型大小', es: 'Tamaño del modelo' },
          content: { ko: 'n은 가장 빠르고 x는 가장 무겁습니다. 속도와 정확도 트레이드오프를 기준으로 선택합니다.', en: 'n is fastest while x is heaviest. Choose based on speed and accuracy tradeoffs.', ja: 'nは最速、xは最も重いモデルです。速度と精度のトレードオフで選択します。', 'zh-CN': 'n最快，x最重。根据速度与精度权衡选择。', 'zh-TW': 'n最快，x最重。根據速度與精度權衡選擇。', es: 'n es el más rápido y x el más pesado. Elija según el equilibrio entre velocidad y precisión.' } },
        { target: '#ops-card', position: 'right',
          title: { ko: '운영 조건', en: 'Operating requirements', ja: '運用要件', 'zh-CN': '运行要求', 'zh-TW': '運行需求', es: 'Requisitos de operación' },
          content: { ko: '채널 수, 목표 FPS, ONNX Runtime/Native, FPS 여유, 최대 latency(프리셋 또는 직접 입력)를 설정합니다.', en: 'Set channels, target FPS, ONNX Runtime/Native, FPS headroom, and max latency (preset or custom ms).', ja: 'チャンネル数、目標FPS、ONNX Runtime/Native、FPSヘッドルーム、最大レイテンシ（プリセットまたは直接入力）を設定します。', 'zh-CN': '设置通道数、目标 FPS、ONNX Runtime/Native、FPS 余量和最大延迟（预设或自定义 ms）。', 'zh-TW': '設定通道數、目標 FPS、ONNX Runtime/Native、FPS 餘量和最大延遲（預設或自訂 ms）。', es: 'Configure canales, FPS objetivo, ONNX Runtime/Native, margen FPS y latencia máx. (preset o ms personalizado).' } },
        { target: '#fpsHeadroom', position: 'right',
          title: { ko: 'FPS 여유', en: 'FPS headroom', ja: 'FPSヘッドルーム', 'zh-CN': 'FPS 余量', 'zh-TW': 'FPS 餘量', es: 'Margen FPS' },
          content: { ko: '목표 FPS보다 약간 높게 잡아 안정적인 채널 산정을 합니다. 예: 10%면 effectiveTarget = target × 1.1', en: 'Adds margin above target FPS for safer channel estimates (e.g. 10% → effectiveTarget = target × 1.1).', ja: '目標FPSより少し高めに設定し、安定したチャンネル推定を行います（例: 10% → effectiveTarget = target × 1.1）。', 'zh-CN': '在目标 FPS 之上留出余量以更稳妥地估算通道（如 10% → effectiveTarget = target × 1.1）。', 'zh-TW': '在目標 FPS 之上留出餘量以更穩妥地估算通道（如 10% → effectiveTarget = target × 1.1）。', es: 'Añade margen sobre el FPS objetivo para estimar canales con más seguridad (p. ej. 10% → effectiveTarget = target × 1.1).' } },
        { target: '#maxLatencyPreset', position: 'right',
          title: { ko: '최대 latency', en: 'Max latency', ja: '最大レイテンシ', 'zh-CN': '最大延迟', 'zh-TW': '最大延遲', es: 'Latencia máx.' },
          content: { ko: '프리셋(ms)을 고르거나 옆 입력란에 직접 ms를 입력합니다. 비우면 latency 조건은 적용하지 않습니다.', en: 'Pick a preset (ms) or type a custom value. Leave empty to skip the latency filter.', ja: 'プリセット(ms)を選ぶか、横の入力欄に直接 ms を入力します。空欄ならレイテンシ条件は適用しません。', 'zh-CN': '选择预设(ms)或在旁输入自定义 ms。留空则不应用延迟条件。', 'zh-TW': '選擇預設(ms)或在旁輸入自訂 ms。留空則不套用延遲條件。', es: 'Elija un preset (ms) o escriba un valor. Déjelo vacío para omitir el filtro de latencia.' } },
        { target: '#btnSetupNext', position: 'right',
          title: { ko: '다음: 우선순위', en: 'Next: priority', ja: '次へ: 優先度', 'zh-CN': '下一步：优先级', 'zh-TW': '下一步：優先順序', es: 'Siguiente: prioridad' },
          content: { ko: '조건 입력 후 이 버튼으로 우선순위 패널을 오른쪽에서 슬라이드 인합니다. 1단계 조건 화면은 그대로 보입니다.', en: 'After entering requirements, this slides the priority panel in from the right while the requirements step stays visible.', ja: '要件入力後、このボタンで優先度パネルが右からスライドインします。条件ステップはそのまま表示されます。', 'zh-CN': '输入条件后，此按钮从右侧滑入优先级面板，条件步骤仍保持可见。', 'zh-TW': '輸入條件後，此按鈕從右側滑入優先順序面板，條件步驟仍保持可見。', es: 'Tras ingresar requisitos, desliza el panel de prioridad desde la derecha; el paso de condiciones sigue visible.' },
          beforeStep: function () { var p = _revealSetupNext(); _reveal('#btnSetupNext'); return p; } },
        { target: '#priority-card', position: 'right',
          title: { ko: '추천 우선순위', en: 'Ranking priority', ja: '推奨優先度', 'zh-CN': '推荐优先级', 'zh-TW': '推薦優先順序', es: 'Prioridad de clasificación' },
          content: { ko: '채널 수, 성능, 전력 중 무엇을 우선할지 선택한 뒤 추천 버튼으로 실행합니다.', en: 'Choose max channels, performance, or power priority, then press Recommend.', ja: 'チャンネル数、性能、電力の優先度を選び、推奨ボタンで実行します。', 'zh-CN': '选择通道数、性能或功耗优先级后，点击推荐按钮执行。', 'zh-TW': '選擇通道數、效能或功耗優先順序後，點擊推薦按鈕執行。', es: 'Elija prioridad de canales, rendimiento o consumo y pulse Recomendar.' },
          beforeStep: function () { return _openPriorityPanel().then(function () { _reveal('#priority-card'); }); } },
        { target: '#btnRecommend', position: 'top',
          title: { ko: '추천 실행', en: 'Run recommendation', ja: '推奨を実行', 'zh-CN': '执行推荐', 'zh-TW': '執行推薦', es: 'Ejecutar recomendación' },
          content: { ko: '우선순위까지 설정한 뒤 추천을 실행합니다. URL 파라미터로 들어오면 입력이 채워진 뒤 자동으로 추천이 실행됩니다(Benchmark 연동).', en: 'Run recommendation after priority is set. URL parameters prefill inputs and auto-run (Benchmark deeplink).', ja: '優先度設定後に推奨を実行します。URL パラメータでは入力を事前入力したうえで自動実行します（Benchmark 連携）。', 'zh-CN': '设置优先级后执行推荐。URL 参数会预填并自动运行（Benchmark 深链）。', 'zh-TW': '設定優先順序後執行推薦。URL 參數會預填並自動執行（Benchmark 深鏈）。', es: 'Ejecute la recomendación tras definir la prioridad. Los parámetros URL completan entradas y se ejecutan solos (enlace desde Benchmark).' },
          beforeStep: function () { return _openPriorityPanel().then(function () { _reveal('#btnRecommend'); }); } }
      ]
    },

    { id: 'recommendations', icon: '📊',
      title: { ko: '📊 추천 결과', en: '📊 Recommendations', ja: '📊 推奨結果', 'zh-CN': '📊 推荐结果', 'zh-TW': '📊 推薦結果', es: '📊 Resultados de recomendación' },
      description: { ko: '조건 요약, 처리량 차트, 추천 카드 확인', en: 'Review condition summary, throughput chart, and recommendation cards', ja: '条件サマリー、スループットチャート、推奨カードを確認', 'zh-CN': '查看条件摘要、吞吐量图表和推荐卡片', 'zh-TW': '查看條件摘要、吞吐量圖表和推薦卡片', es: 'Revise el resumen de condiciones, el gráfico de rendimiento y las tarjetas de recomendación' },
      beforeStart: ensureWorkspaceRecommendation,
      steps: [
        { target: '#recommendationsPanel', position: 'left',
          title: { ko: '추천 패널', en: 'Recommendations panel', ja: '推奨パネル', 'zh-CN': '推荐面板', 'zh-TW': '推薦面板', es: 'Panel de recomendaciones' },
          content: { ko: '조건에 맞는 플랫폼 순위와 충족 여부를 한눈에 확인합니다.', en: 'Review ranked platforms and whether they meet your workload.', ja: '条件に合うプラットフォーム順位と充足状況を確認します。', 'zh-CN': '查看符合条件的平台排名和达标情况。', 'zh-TW': '查看符合條件的平台排名和達標情況。', es: 'Consulte de un vistazo el ranking de plataformas y si satisfacen su carga de trabajo.' } },
        { target: '#conditionSummary', position: 'bottom',
          title: { ko: '조건 요약', en: 'Condition summary', ja: '条件サマリー', 'zh-CN': '条件摘要', 'zh-TW': '條件摘要', es: 'Resumen de condiciones' },
          content: { ko: '현재 task, size, 채널 수, FPS, 런타임 설정을 칩 형태로 보여줍니다.', en: 'Shows current task, size, channel count, FPS, and runtime as compact chips.', ja: '現在のtask、size、チャンネル数、FPS、ランタイムをコンパクトに表示します。', 'zh-CN': '以标签形式显示当前task、size、通道数、FPS和运行时。', 'zh-TW': '以標籤形式顯示目前task、size、通道數、FPS和執行環境。', es: 'Muestra la tarea, el tamaño, el número de canales, el FPS y el entorno de ejecución actuales en forma de etiquetas.' } },
        { target: '#recommendSummary', position: 'bottom',
          title: { ko: '결과 요약', en: 'Result summary', ja: '結果サマリー', 'zh-CN': '结果摘要', 'zh-TW': '結果摘要', es: 'Resumen de resultados' },
          content: { ko: '요구 조건을 충족하는 항목과 부족한 항목 수를 빠르게 확인합니다.', en: 'Quickly see how many platforms meet vs fall short of your requirement.', ja: '要件を充足するプラットフォームと不足するプラットフォームの件数を素早く確認します。', 'zh-CN': '快速查看达标与不足的平台数量。', 'zh-TW': '快速查看達標與不足的平台數量。', es: 'Consulte rápidamente cuántas plataformas cumplen o no su requisito.' } },
        { target: '#recommendationsPanel [data-open-methodology]', position: 'left',
          title: { ko: '원리 (결과)', en: 'Methodology (results)', ja: '原理解説（結果）', 'zh-CN': '原理（结果）', 'zh-TW': '原理（結果）', es: 'Metodología (resultados)' },
          content: { ko: '추천 헤더의 노란 원리 버튼으로도 방법론과 면책 안내를 열 수 있습니다.', en: 'The yellow chip in the recommendations header also opens methodology and disclaimers.', ja: '推奨ヘッダーの黄色ボタンからも方法論と免責事項を開けます。', 'zh-CN': '推荐标题栏的黄色原理按钮也可打开方法论与免责声明。', 'zh-TW': '推薦標題列的黃色原理按鈕也可開啟方法論與免責聲明。', es: 'El botón amarillo del encabezado de recomendaciones también abre metodología y avisos.' } },
        { target: '#autoRefreshNote', position: 'bottom',
          title: { ko: '자동 갱신', en: 'Auto refresh', ja: '自動更新', 'zh-CN': '自动刷新', 'zh-TW': '自動重新整理', es: 'Actualización automática' },
          content: { ko: '첫 추천 이후 조건을 바꾸면 결과가 자동으로 다시 계산됩니다.', en: 'After the first run, changing requirements automatically recalculates results.', ja: '初回実行後、条件を変更すると結果が自動で再計算されます。', 'zh-CN': '首次运行后，修改条件会自动重新计算结果。', 'zh-TW': '首次執行後，修改條件會自動重新計算結果。', es: 'Tras la primera ejecución, cambiar requisitos recalcula los resultados automáticamente.' },
          beforeStep: function () { ensureWorkspaceRecommendation(); _reveal('#autoRefreshNote'); } },
        { target: '#overviewChart', position: 'top',
          title: { ko: '처리량 차트', en: 'Throughput chart', ja: 'スループットチャート', 'zh-CN': '吞吐量图表', 'zh-TW': '吞吐量圖表', es: 'Gráfico de rendimiento' },
          content: { ko: '플랫폼별 throughput FPS를 비교합니다. 막대를 선택하면 해당 플랫폼 상세 패널이 열립니다.', en: 'Compares throughput FPS by platform. Select a bar to open that platform in the detail panel.', ja: 'プラットフォーム別throughput FPSを比較します。バーを選択すると詳細パネルが開きます。', 'zh-CN': '比较各平台throughput FPS。选择柱条可打开对应详情面板。', 'zh-TW': '比較各平台throughput FPS。選擇長條可打開對應詳情面板。', es: 'Compare el throughput FPS por plataforma. Al seleccionar una barra, se abre el panel de detalle de esa plataforma.' } },
        { target: '#recommend-cards .rec-card', position: 'right',
          title: { ko: '추천 카드', en: 'Recommendation card', ja: '推奨カード', 'zh-CN': '推荐卡片', 'zh-TW': '推薦卡片', es: 'Tarjeta de recomendación' },
          content: { ko: '카드 전체를 클릭하거나 Enter/Space로 선택할 수 있습니다. 상세 보기 버튼도 같은 패널을 엽니다.', en: 'Click the card or use Enter/Space to select it. The detail button opens the same panel.', ja: 'カード全体のクリック、またはEnter/Spaceで選択できます。詳細ボタンも同じパネルを開きます。', 'zh-CN': '可点击整张卡片或使用Enter/Space选择。详情按钮打开同一面板。', 'zh-TW': '可點擊整張卡片或使用Enter/Space選擇。詳情按鈕打開同一面板。', es: 'Puede hacer clic en la tarjeta completa o usar Enter/Espacio para seleccionarla. El botón de detalle abre el mismo panel.' },
          beforeStep: function () { _reveal('#recommend-cards .rec-card'); } }
      ]
    },

    { id: 'details', icon: '🔍',
      title: { ko: '🔍 상세 / 비교', en: '🔍 Details / Compare', ja: '🔍 詳細 / 比較', 'zh-CN': '🔍 详情 / 比较', 'zh-TW': '🔍 詳情 / 比較', es: '🔍 Detalle / Comparación' },
      description: { ko: '선택 플랫폼의 dense 수치, 비교, 벤치마크 근거 확인', en: 'Inspect dense metrics, comparison, and benchmark evidence', ja: '選択プラットフォームの詳細指標、比較、ベンチマーク根拠を確認', 'zh-CN': '查看所选平台的详细指标、比较和基准依据', 'zh-TW': '查看所選平台的詳細指標、比較和基準依據', es: 'Consulte las métricas detalladas, la comparación y la evidencia de benchmarks de la plataforma seleccionada' },
      beforeStart: ensureWorkspaceDetail,
      steps: [
        { target: '#detailPanel', position: 'left',
          title: { ko: '상세 패널', en: 'Detail panel', ja: '詳細パネル', 'zh-CN': '详情面板', 'zh-TW': '詳情面板', es: 'Panel de detalle' },
          content: { ko: '선택한 추천의 성능, 전력, 채널 근거를 한 패널에서 계속 비교합니다.', en: 'Keeps performance, power, and channel evidence visible for the selected recommendation.', ja: '選択した推奨の性能、電力、チャンネル根拠を1つのパネルで比較できます。', 'zh-CN': '在一个面板中持续查看所选推荐的性能、功耗和通道依据。', 'zh-TW': '在一個面板中持續查看所選推薦的效能、功耗和通道依據。', es: 'Mantiene visibles en un solo panel el rendimiento, el consumo eléctrico y la evidencia de canales de la recomendación seleccionada.' } },
        { target: '#recommendation-facts', position: 'left',
          title: { ko: '핵심 수치', en: 'Key facts', ja: '主要指標', 'zh-CN': '关键指标', 'zh-TW': '關鍵指標', es: 'Métricas clave' },
          content: { ko: '요구 채널, 목표 FPS, 최대 채널, latency, throughput, TOPS/W를 바로 보여줍니다.', en: 'Shows required channels, target FPS, max channels, latency, throughput, and TOPS/W.', ja: '要求チャンネル、目標FPS、最大チャンネル、latency、throughput、TOPS/Wを表示します。', 'zh-CN': '显示所需通道、目标FPS、最大通道、latency、throughput和TOPS/W。', 'zh-TW': '顯示所需通道、目標FPS、最大通道、latency、throughput和TOPS/W。', es: 'Muestra directamente los canales requeridos, el FPS objetivo, el máximo de canales, latencia, throughput y TOPS/W.' } },
        { target: '#platform-summary', position: 'left',
          title: { ko: '플랫폼 스펙', en: 'Platform specs', ja: 'プラットフォーム仕様', 'zh-CN': '平台规格', 'zh-TW': '平台規格', es: 'Especificaciones de plataforma' },
          content: { ko: 'NPU, TOPS, TDP, DRAM, Host 정보를 요약합니다.', en: 'Summarizes NPU, TOPS, TDP, DRAM, and host information.', ja: 'NPU、TOPS、TDP、DRAM、Host情報を要約します。', 'zh-CN': '汇总NPU、TOPS、TDP、DRAM和Host信息。', 'zh-TW': '彙總NPU、TOPS、TDP、DRAM和Host資訊。', es: 'Resume la información de NPU, TOPS, TDP, DRAM y host.' } },
        { target: '#radarChart', position: 'left',
          title: { ko: '레이더 차트', en: 'Radar chart', ja: 'レーダーチャート', 'zh-CN': '雷达图', 'zh-TW': '雷達圖', es: 'Gráfico de radar' },
          content: { ko: 'FPS, 채널, 전력 효율, 안정성, TOPS를 정규화해 현재 플랫폼과 비교 대상을 시각화합니다.', en: 'Normalizes FPS, channels, power efficiency, stability, and TOPS for current and compared platforms.', ja: 'FPS、チャンネル、電力効率、安定性、TOPSを正規化して比較します。', 'zh-CN': '将FPS、通道、能效、稳定性和TOPS标准化后进行比较。', 'zh-TW': '將FPS、通道、能效、穩定性和TOPS標準化後進行比較。', es: 'Normaliza FPS, canales, eficiencia energética, estabilidad y TOPS para visualizar la plataforma actual frente a la de comparación.' } },
        { target: '#compare-dropdown', position: 'left',
          title: { ko: '비교 대상 선택', en: 'Select comparison', ja: '比較対象を選択', 'zh-CN': '选择比较对象', 'zh-TW': '選擇比較對象', es: 'Seleccionar comparación' },
          content: { ko: '다른 플랫폼을 선택하면 레이더와 비교 요약 테이블이 즉시 갱신됩니다.', en: 'Select another platform to refresh the radar and comparison summary immediately.', ja: '別のプラットフォームを選ぶと、レーダーと比較サマリーが即時更新されます。', 'zh-CN': '选择其他平台后，雷达图和比较摘要会立即刷新。', 'zh-TW': '選擇其他平台後，雷達圖和比較摘要會立即重新整理。', es: 'Al elegir otra plataforma, el gráfico de radar y la tabla resumida de comparación se actualizan al instante.' } },
        { target: '#comparison-summary', position: 'left',
          title: { ko: '비교 요약', en: 'Comparison summary', ja: '比較サマリー', 'zh-CN': '比较摘要', 'zh-TW': '比較摘要', es: 'Resumen de comparación' },
          content: { ko: '현재 플랫폼과 비교 대상의 NPU, Host, TOPS, TDP, throughput, 최대 채널을 표로 비교합니다.', en: 'Compares NPU, host, TOPS, TDP, throughput, and max channels in a table.', ja: 'NPU、Host、TOPS、TDP、throughput、最大チャンネルを表で比較します。', 'zh-CN': '以表格比较NPU、Host、TOPS、TDP、throughput和最大通道。', 'zh-TW': '以表格比較NPU、Host、TOPS、TDP、throughput和最大通道。', es: 'Compara en tabla la NPU, el host, TOPS, TDP, throughput y máximo de canales entre la plataforma actual y la de comparación.' } },
        { target: '#task-tabs', position: 'top',
          title: { ko: '태스크별 탐색', en: 'Task exploration', ja: 'タスク別探索', 'zh-CN': '按任务浏览', 'zh-TW': '按任務瀏覽', es: 'Exploración por tarea' },
          content: { ko: '다른 태스크의 데이터도 같은 플랫폼 안에서 빠르게 훑어볼 수 있습니다.', en: 'Quickly browse other task data for the same platform.', ja: '同じプラットフォーム内で他タスクのデータも素早く確認できます。', 'zh-CN': '可快速浏览同一平台的其他任务数据。', 'zh-TW': '可快速瀏覽同一平台的其他任務資料。', es: 'Puede revisar rápidamente los datos de otras tareas dentro de la misma plataforma.' } },
        { target: '#benchmark-table', position: 'top',
          title: { ko: '벤치마크 테이블', en: 'Benchmark table', ja: 'ベンチマーク表', 'zh-CN': '基准测试表', 'zh-TW': '基準測試表', es: 'Tabla de benchmarks' },
          content: { ko: '모델 크기별 latency, throughput, 최대 채널을 정렬 가능한 표로 제공합니다.', en: 'Provides sortable latency, throughput, and max-channel data by model size.', ja: 'モデルサイズ別のlatency、throughput、最大チャンネルをソート可能な表で提供します。', 'zh-CN': '按模型大小提供可排序的latency、throughput和最大通道数据。', 'zh-TW': '按模型大小提供可排序的latency、throughput和最大通道資料。', es: 'Proporciona latencia, throughput y máximo de canales por tamaño de modelo en una tabla ordenable.' } },
        { target: '#groupBarChart', position: 'top',
          title: { ko: '모델 크기 차트', en: 'Model-size chart', ja: 'モデルサイズチャート', 'zh-CN': '模型大小图表', 'zh-TW': '模型大小圖表', es: 'Gráfico por tamaño de modelo' },
          content: { ko: '모델 크기별 latency FPS와 throughput FPS를 비교하며, 막대를 선택하면 해당 조건으로 다시 추천합니다.', en: 'Compares latency FPS and throughput FPS by model size; selecting a bar re-runs with that size.', ja: 'モデルサイズ別のlatency FPSとthroughput FPSを比較し、バー選択でその条件に再推奨します。', 'zh-CN': '比较各模型大小的latency FPS和throughput FPS，选择柱条会按该大小重新推荐。', 'zh-TW': '比較各模型大小的latency FPS和throughput FPS，選擇長條會按該大小重新推薦。', es: 'Compare latency FPS y throughput FPS por tamaño de modelo; al seleccionar una barra, vuelve a ejecutar la recomendación con ese tamaño.' } },
        { target: '#multi-stream-evidence', position: 'top',
          title: { ko: 'Multi-stream 근거', en: 'Multi-stream evidence', ja: 'Multi-stream根拠', 'zh-CN': 'Multi-stream依据', 'zh-TW': 'Multi-stream依據', es: 'Evidencia multi-stream' },
          content: { ko: '채널 수 산정에 사용된 stream_count, per-channel FPS, total FPS 측정값을 확인합니다.', en: 'Shows stream_count, per-channel FPS, and total FPS measurements used for channel estimates.', ja: 'チャンネル推定に使われたstream_count、per-channel FPS、total FPS測定値を確認します。', 'zh-CN': '显示用于通道估算的stream_count、per-channel FPS和total FPS测量值。', 'zh-TW': '顯示用於通道估算的stream_count、per-channel FPS和total FPS測量值。', es: 'Consulte los valores medidos de stream_count, FPS por canal y FPS total utilizados para estimar el número de canales.' } },
        { target: '#commercePanel', position: 'left',
          title: { ko: '구매 / 문의', en: 'Buy / contact', ja: '購入 / 問い合わせ', 'zh-CN': '购买 / 咨询', 'zh-TW': '購買 / 諮詢', es: 'Comprar / contacto' },
          content: { ko: '선택 플랫폼의 DEEPX 제품 정보와 견적 문의 링크입니다. 가격은 DEEPX에 문의하세요.', en: 'DEEPX product info and quote links for the selected platform. Contact DEEPX for pricing.', ja: '選択プラットフォームの DEEPX 製品情報・見積リンクです。価格は DEEPX へお問い合わせください。', 'zh-CN': '所选平台的 DEEPX 产品信息与询价链接。价格请联系 DEEPX。', 'zh-TW': '所選平台的 DEEPX 產品資訊與詢價連結。價格請聯絡 DEEPX。', es: 'Enlaces de producto y cotización DEEPX para la plataforma seleccionada. Consultar precio a DEEPX.' } }
      ]
    },
  ];
var referenceDocs = [
    { id: 'ref-workspace', icon: '🔄',
      title: { ko: '사용 흐름', en: 'Usage flow', ja: '利用フロー', 'zh-CN': '使用流程', 'zh-TW': '使用流程', es: 'Flujo de uso' },
      body: { ko: '<h3>사용 흐름</h3><ol><li>시나리오 칩 또는 task/size/ops로 조건을 입력합니다.</li><li>다음 → 채널·성능·전력 우선순위 → 추천 실행.</li><li>카드나 차트 막대를 선택해 상세/비교/구매 패널을 확인합니다.</li></ol>',
              en: '<h3>Usage flow</h3><ol><li>Enter requirements via scenario chips or task/size/ops fields.</li><li>Next → set channels/performance/power priority → Run recommendation.</li><li>Select a card or chart bar to inspect details, comparison, and commerce links.</li></ol>',
              ja: '<h3>利用フロー</h3><ol><li>シナリオチップまたは task/size/ops で条件を入力します。</li><li>次へ → チャンネル/性能/電力の優先度 → 推奨実行。</li><li>カードまたはチャートバーで詳細・比較・購入パネルを確認します。</li></ol>',
              'zh-CN': '<h3>使用流程</h3><ol><li>通过场景标签或 task/size/ops 输入条件。</li><li>下一步 → 设置通道/性能/功耗优先级 → 执行推荐。</li><li>选择卡片或图表柱条查看详情、比较与购买链接。</li></ol>',
              'zh-TW': '<h3>使用流程</h3><ol><li>透過情境標籤或 task/size/ops 輸入條件。</li><li>下一步 → 設定通道/效能/功耗優先順序 → 執行推薦。</li><li>選擇卡片或圖表長條查看詳情、比較與購買連結。</li></ol>',
              es: '<h3>Flujo de uso</h3><ol><li>Ingrese requisitos con chips de escenario o campos task/size/ops.</li><li>Siguiente → prioridad canales/rendimiento/consumo → Ejecutar recomendación.</li><li>Seleccione tarjeta o barra para detalle, comparación y enlaces comerciales.</li></ol>' } },
    { id: 'ref-recommend', icon: '🎯',
      title: { ko: '추천 기준', en: 'Recommendation basis', ja: '推奨基準', 'zh-CN': '推荐依据', 'zh-TW': '推薦依據', es: 'Base de recomendación' },
      body: { ko: '<h3>추천 원리</h3><ul><li>선택한 task/size/runtime의 benchmark와 multi-stream 데이터를 사용합니다.</li><li>요구 채널을 충족하는 플랫폼을 먼저 보여줍니다.</li><li>채널, 성능, 전력 우선순위에 따라 정렬이 달라집니다.</li></ul>',
              en: '<h3>How recommendations work</h3><ul><li>Uses benchmark and multi-stream data for the selected task, size, and runtime.</li><li>Platforms meeting required channels are ranked first.</li><li>Sorting changes by channels, performance, or power priority.</li></ul>',
              ja: '<h3>推奨の仕組み</h3><ul><li>選択task、size、runtimeのbenchmarkとmulti-streamデータを使います。</li><li>要求チャンネルを満たすプラットフォームを優先します。</li><li>チャンネル、性能、電力の優先度で並び順が変わります。</li></ul>',
              'zh-CN': '<h3>推荐原理</h3><ul><li>使用所选task、size、runtime的benchmark和multi-stream数据。</li><li>优先展示满足所需通道的平台。</li><li>排序会随通道、性能或功耗优先级变化。</li></ul>',
              'zh-TW': '<h3>推薦原理</h3><ul><li>使用所選task、size、runtime的benchmark和multi-stream資料。</li><li>優先顯示滿足所需通道的平台。</li><li>排序會隨通道、效能或功耗優先順序變化。</li></ul>',
              es: '<h3>Cómo funcionan las recomendaciones</h3><ul><li>Utiliza datos de benchmark y multi-stream de la task, el size y el runtime seleccionados.</li><li>Las plataformas que cumplen los canales requeridos aparecen primero.</li><li>El orden cambia según la prioridad de canales, rendimiento o consumo eléctrico.</li></ul>' } },
    { id: 'ref-detail', icon: '📈',
      title: { ko: '상세 패널', en: 'Detail panel', ja: '詳細パネル', 'zh-CN': '详情面板', 'zh-TW': '詳情面板', es: 'Panel de detalle' },
      body: { ko: '<h3>상세 패널</h3><ul><li>핵심 수치: throughput, latency, TOPS/W</li><li>비교: 드롭다운으로 다른 플랫폼과 주요 수치를 비교</li><li>근거: benchmark table과 multi-stream 측정값 확인</li></ul>',
              en: '<h3>Detail panel</h3><ul><li>Key metrics: throughput, latency, TOPS/W</li><li>Comparison: use the dropdown to compare with another platform</li><li>Evidence: inspect benchmark table and multi-stream measurements</li></ul>',
              ja: '<h3>詳細パネル</h3><ul><li>主要指標: throughput、latency、TOPS/W</li><li>比較: ドロップダウンで他プラットフォームと比較</li><li>根拠: benchmark表とmulti-stream測定値を確認</li></ul>',
              'zh-CN': '<h3>详情面板</h3><ul><li>关键指标：throughput、latency、TOPS/W</li><li>比较：使用下拉框与其他平台比较</li><li>依据：查看benchmark表和multi-stream测量值</li></ul>',
              'zh-TW': '<h3>詳情面板</h3><ul><li>關鍵指標: throughput、latency、TOPS/W</li><li>比較: 使用下拉框與其他平台比較</li><li>依據: 查看benchmark表和multi-stream測量值</li></ul>',
              es: '<h3>Panel de detalle</h3><ul><li>Métricas clave: throughput, latencia, TOPS/W</li><li>Comparación: utilice el menú desplegable para comparar con otra plataforma</li><li>Evidencia: consulte la tabla de benchmarks y las mediciones multi-stream</li></ul>' } }
  ];

  window.DXTutorial.create({
    appId: 'edgeguide',
    sections: sections,
    referenceDocs: referenceDocs,
    toolbarSelector: '#dxToolbar',
    skipButtons: true,
    getLang: function () {
      return typeof DXI18n !== 'undefined' ? DXI18n.lang : 'ko';
    },
    onNav: function () {},
    onComplete: function (sectionId) {
      var engine = window._dxTutorial;
      var sec = engine.sections.find(function (s) { return s.id === sectionId; });
      if (typeof toast === 'function' && sec) {
        toast('✅ "' + engine._t(sec.title) + '" ' + engine._tl('tutorial complete!'), 'ok');
      }
    },
    patchNav: function () {}
  });
})();
