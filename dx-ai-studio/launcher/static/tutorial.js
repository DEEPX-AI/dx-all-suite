
(function () {
  'use strict';

  // Tutorial mode is ON by default; it's only off when the user explicitly turned it off.
  const _stored = localStorage.getItem('dx-tutorial-mode');
  let _tutorialMode = _stored !== 'off';
  const _lang = () => localStorage.getItem('dx-lang') || 'en';
  let _engine = null;
// Launcher 자체 화면을 위한 튜토리얼 섹션이다. iframe 모듈 튜토리얼은 각 모듈이 소유한다.
  const sections = [
    { id: 'home', icon: 'home',
      title: { en: 'Launcher Home', ko: '런처 홈', ja: 'ランチャーホーム', 'zh-CN': '启动器主页', 'zh-TW': '啟動器首頁', es: 'Inicio del iniciador' },
      description: { en: 'Open DX modules and shared resources from the launcher shell.', ko: '런처 셸에서 DX 모듈과 공유 리소스를 엽니다.', ja: 'ランチャーシェルからDXモジュールと共有リソースを開きます。', 'zh-CN': '从启动器外壳打开DX模块和共享资源。', 'zh-TW': '從啟動器殼層開啟DX模組和共用資源。', es: 'Abra módulos DX y recursos compartidos desde el shell del iniciador.' },
      beforeStart: function () {
        // Navigating home mid-start would trigger setVisibleView → suspendAllTutorialChrome
        // → _dxTutorial.stop(), nulling _curSection and killing the tour that just started.
        // Only navigate when actually inside a module, and shield that nav with a flag so
        // suspendAllTutorialChrome skips stopping this (tutorial-driven) transition.
        var ns = window.DXLauncher;
        if (typeof goHome === 'function' && ns && ns.currentApp) {
          // navigate() is async (ensureStudioReady().then(navigateNow)) so setVisibleView
          // — and its suspendAllTutorialChrome — run in a later microtask/tick. Hold the
          // shield past that gap via a timer rather than resetting it synchronously.
          ns._tutorialDrivenNav = true;
          goHome();
          setTimeout(function () { ns._tutorialDrivenNav = false; }, 800);
        }
        if (ns && typeof ns.tryCompleteLauncherBoot === 'function') {
          ns.tryCompleteLauncherBoot();
        }
      },
      steps: [
        // 무대의 순서대로 (spec 2026-09-23 §9): 입력 → 예시 → 소개 → 모듈 → 책 → 위젯 둘 → 막대 → 투어 줄 → 챗.
        { target: '#homeAskForm .ask-box', position: 'bottom',
          title: { en: 'Describe it', ko: '말로 설명하기', ja: '言葉で伝える', 'zh-CN': '用一句话描述', 'zh-TW': '用一句話描述', es: 'Descríbalo' },
          content: { en: 'Type what you want in plain words and press <strong>Build it</strong>. The agent picks a model, compiles it, builds the app and measures it on this NPU. A request that names a tool — "compile yolo26n to DXNN" — opens that module directly.', ko: '만들고 싶은 것을 평소 말로 적고 <strong>만들기</strong> 를 누르세요. 에이전트가 모델을 고르고, 컴파일하고, 앱을 만들어 이 NPU에서 측정합니다. 도구를 콕 집은 요청 ("compile yolo26n to DXNN")은 그 모듈을 바로 엽니다.', ja: '作りたいものを普段の言葉で書き、<strong>作る</strong>を押します。エージェントがモデルを選び、コンパイルし、アプリを作ってこの NPU で測定します。ツールを名指しする依頼（"compile yolo26n to DXNN"）はそのモジュールを直接開きます。', 'zh-CN': '用平常的话写下你想做的东西，然后点<strong>开始构建</strong>。智能体会选模型、编译、构建应用，并在这块 NPU 上实测。点名某个工具的请求（如 "compile yolo26n to DXNN"）会直接打开对应模块。', 'zh-TW': '用平常的話寫下你想做的東西，然後按<strong>開始建構</strong>。智能體會選模型、編譯、建構應用，並在這塊 NPU 上實測。點名某個工具的請求（如 "compile yolo26n to DXNN"）會直接開啟對應模組。', es: 'Escriba lo que quiere con sus palabras y pulse <strong>Construir</strong>. El agente elige el modelo, lo compila, crea la app y la mide en esta NPU. Una petición que nombra una herramienta —"compile yolo26n to DXNN"— abre ese módulo directamente.' } },
        { target: '#homeAskChips', position: 'bottom',
          title: { en: 'Start from a real build', ko: '실제로 만든 예제에서 시작', ja: '実際に作った例から', 'zh-CN': '从真实案例开始', 'zh-TW': '從真實案例開始', es: 'Empiece por un caso real' },
          content: { en: 'Each example fills in the exact prompt that built one of the DX Agent Dev showcases. Read it, change what you like, then build. <strong>+5</strong> shows the rest.', ko: '예시를 누르면 DX Agent Dev 쇼케이스 하나를 실제로 만든 요청 문장이 그대로 채워집니다. 읽고 원하는 대로 고친 뒤 만드세요. <strong>+5</strong> 로 나머지 예시를 봅니다.', ja: '例を押すと、DX Agent Dev のショーケースを実際に作ったプロンプトがそのまま入ります。読んで、好きに直してから作ってください。<strong>+5</strong> で残りの例を表示します。', 'zh-CN': '每个示例都会填入真正做出某个 DX Agent Dev 展示案例的原始提示词。读一读、按需修改，再构建。<strong>+5</strong> 显示其余示例。', 'zh-TW': '每個範例都會填入真正做出某個 DX Agent Dev 展示案例的原始提示詞。讀一讀、依需要修改，再建構。<strong>+5</strong> 顯示其餘範例。', es: 'Cada ejemplo rellena el prompt exacto con el que se creó uno de los casos de DX Agent Dev. Léalo, cambie lo que quiera y construya. <strong>+5</strong> muestra el resto.' } },
        { target: '#homeStage .stage-films', position: 'bottom',
          title: { en: 'Platform and ecosystem', ko: '플랫폼과 생태계', ja: 'プラットフォームとエコシステム', 'zh-CN': '平台与生态', 'zh-TW': '平台與生態', es: 'Plataforma y ecosistema' },
          content: { en: 'The first opens the <strong>platform overview</strong> with every module; the second shows the <strong>Physical AI ecosystem</strong> — Ultralytics YOLO, PaddlePaddle and Raspberry Pi around the DEEPX NPU.', ko: '첫 번째는 모든 모듈을 담은 <strong>플랫폼 개요</strong>, 두 번째는 DEEPX NPU를 둘러싼 <strong>Physical AI 생태계</strong> (Ultralytics YOLO · PaddlePaddle · Raspberry Pi)를 엽니다.', ja: '1つ目は全モジュールをまとめた<strong>プラットフォーム概要</strong>、2つ目は DEEPX NPU を中心にした <strong>Physical AI エコシステム</strong>（Ultralytics YOLO・PaddlePaddle・Raspberry Pi）を開きます。', 'zh-CN': '第一个打开包含所有模块的<strong>平台概览</strong>，第二个展示以 DEEPX NPU 为中心的 <strong>Physical AI 生态</strong>（Ultralytics YOLO、PaddlePaddle、Raspberry Pi）。', 'zh-TW': '第一個開啟包含所有模組的<strong>平台概覽</strong>，第二個展示以 DEEPX NPU 為中心的 <strong>Physical AI 生態</strong>（Ultralytics YOLO、PaddlePaddle、Raspberry Pi）。', es: 'El primero abre la <strong>visión general de la plataforma</strong> con todos los módulos; el segundo muestra el <strong>ecosistema de IA física</strong>: Ultralytics YOLO, PaddlePaddle y Raspberry Pi alrededor de la NPU DEEPX.' } },
        { target: '#studioGrid', position: 'bottom',
          title: { en: 'Eight modules', ko: '여덟 개의 모듈', ja: '8つのモジュール', 'zh-CN': '八个模块', 'zh-TW': '八個模組', es: 'Ocho módulos' },
          content: { en: 'Each icon opens its module in place — it grows from the icon and folds back into it when you return. Icons swell as your cursor nears them; a <strong>dimmed</strong> one means that module\'s server is offline or not installed. Hover to see what it does.', ko: '아이콘을 누르면 그 자리에서 모듈이 열립니다 — 아이콘에서 커지고, 돌아오면 다시 아이콘으로 접힙니다. 커서가 다가가면 아이콘이 커지고, <strong>흐린</strong> 아이콘은 그 모듈 서버가 꺼져 있거나 설치되지 않았다는 뜻입니다. 가리키면 하는 일이 보입니다.', ja: 'アイコンを押すとその場でモジュールが開きます。アイコンから広がり、戻るとアイコンへたたまれます。カーソルを近づけるとアイコンが大きくなり、<strong>薄い</strong>アイコンはそのモジュールのサーバーが停止中か未インストールです。ポイントすると役割が表示されます。', 'zh-CN': '点击图标会就地打开模块——从图标展开，返回时再收回图标。光标靠近时图标会放大；<strong>变暗</strong>的图标表示该模块的服务器未运行或未安装。悬停可查看它的用途。', 'zh-TW': '點擊圖示會就地開啟模組——從圖示展開，返回時再收回圖示。游標靠近時圖示會放大；<strong>變暗</strong>的圖示表示該模組的伺服器未執行或未安裝。停留可查看它的用途。', es: 'Cada icono abre su módulo en el sitio: crece desde el icono y vuelve a él al regresar. Los iconos se agrandan al acercar el cursor; uno <strong>atenuado</strong> indica que su servidor está apagado o no instalado. Pase el cursor para ver qué hace.' } },
        { target: '.about-book-card.sdk-card', position: 'bottom',
          title: { en: 'SDK Library', ko: 'SDK 라이브러리', ja: 'SDK ライブラリ', 'zh-CN': 'SDK 库', 'zh-TW': 'SDK 庫', es: 'Biblioteca SDK' },
          content: { en: 'Open the <strong>SDK Library</strong> to browse technical documentation without leaving the launcher shell.', ko: '런처를 벗어나지 않고 <strong>SDK Library</strong>에서 기술 문서를 탐색합니다.', ja: 'ランチャーを離れずに<strong>SDK Library</strong>で技術ドキュメントを閲覧します。', 'zh-CN': '无需离开启动器即可在<strong>SDK Library</strong>中浏览技术文档。', 'zh-TW': '無需離開啟動器即可在<strong>SDK Library</strong>中瀏覽技術文件。', es: 'Abra <strong>SDK Library</strong> para explorar documentación técnica sin salir del launcher.' } },
        { target: '.about-book-card:not(.sdk-card)', position: 'bottom',
          title: { en: 'About DEEPX', ko: 'About DEEPX', ja: 'About DEEPX', 'zh-CN': 'About DEEPX', 'zh-TW': 'About DEEPX', es: 'About DEEPX' },
          content: { en: 'Open the <strong>interactive DEEPX encyclopedia</strong> — explore hotspots on the DX-M1/DX-M2 chip die and click through the company\'s technology, product, and vision stories.', ko: '<strong>인터랙티브 DEEPX 백과사전</strong>을 엽니다 — DX-M1/DX-M2 칩 다이의 핫스팟을 탐험하고 기술·제품·비전 스토리를 클릭으로 살펴보세요.', ja: '<strong>インタラクティブなDEEPX百科事典</strong>を開きます — DX-M1/DX-M2チップダイのホットスポットを探索し、技術・製品・ビジョンのストーリーをクリックで閲覧できます。', 'zh-CN': '打开<strong>DEEPX 交互式百科全书</strong>——探索 DX-M1/DX-M2 芯片裸片上的热点，点击浏览公司的技术、产品与愿景故事。', 'zh-TW': '開啟<strong>DEEPX 互動式百科全書</strong>——探索 DX-M1/DX-M2 晶片裸晶上的熱點，點擊瀏覽公司的技術、產品與願景故事。', es: 'Abra la <strong>enciclopedia interactiva de DEEPX</strong>: explore los puntos clave del die de los chips DX-M1/DX-M2 y recorra las historias de tecnología, producto y visión de la empresa.' } },
        { target: '#homeDevice', position: 'right',
          title: { en: 'This DX-M1', ko: '이 DX-M1', ja: 'この DX-M1', 'zh-CN': '这块 DX-M1', 'zh-TW': '這塊 DX-M1', es: 'Este DX-M1' },
          content: { en: 'The live state of the NPU in this PC — one bar per core, then temperature, clock and power. The widget dims when no DX-M1 is connected. Click it to open <strong>Monitor</strong>.', ko: '이 PC에 꽂힌 NPU의 지금 상태 — 코어마다 막대 하나, 그리고 온도 · 클럭 · 전력. DX-M1이 연결되어 있지 않으면 위젯이 흐려집니다. 누르면 <strong>Monitor</strong> 가 열립니다.', ja: 'この PC の NPU の今の状態です。コアごとのバーと、温度・クロック・電力。DX-M1 が未接続だとウィジェットが暗くなります。クリックすると <strong>Monitor</strong> が開きます。', 'zh-CN': '这台电脑中 NPU 的实时状态——每个核心一根柱条，以及温度、时钟和功耗。未连接 DX-M1 时组件会变暗。点击打开 <strong>Monitor</strong>。', 'zh-TW': '這台電腦中 NPU 的即時狀態——每個核心一根長條，以及溫度、時脈和功耗。未連接 DX-M1 時元件會變暗。點擊開啟 <strong>Monitor</strong>。', es: 'Estado en vivo de la NPU de este PC: una barra por núcleo, más temperatura, reloj y consumo. El widget se atenúa si no hay un DX-M1 conectado. Haga clic para abrir <strong>Monitor</strong>.' } },
        { target: '#homeMeasured', position: 'left',
          title: { en: 'Measured here', ko: '여기서 잰 값', ja: 'ここで測った値', 'zh-CN': '在这里实测', 'zh-TW': '在這裡實測', es: 'Medido aquí' },
          content: { en: 'The FPS of YOLO26n for each task, measured on this device. It moves to the next task every 5 seconds and waits while you point at it. The count below opens <strong>Benchmark</strong>.', ko: '작업마다 YOLO26n을 이 장치에서 잰 FPS 입니다. 5초마다 다음 작업으로 넘어가고, 가리키고 있으면 기다립니다. 아래 개수를 누르면 <strong>Benchmark</strong> 가 열립니다.', ja: 'タスクごとに YOLO26n をこのデバイスで測った FPS です。5秒ごとに次のタスクへ移り、ポイント中は待ちます。下の件数をクリックすると <strong>Benchmark</strong> が開きます。', 'zh-CN': '每个任务的 YOLO26n 在本设备上实测的 FPS。每 5 秒切换到下一个任务，悬停时暂停。点击下方的数量打开 <strong>Benchmark</strong>。', 'zh-TW': '每個任務的 YOLO26n 在本裝置上實測的 FPS。每 5 秒切換到下一個任務，停留時暫停。點擊下方的數量開啟 <strong>Benchmark</strong>。', es: 'FPS de YOLO26n para cada tarea, medidos en este dispositivo. Pasa a la siguiente tarea cada 5 segundos y espera mientras lo señala. El recuento de abajo abre <strong>Benchmark</strong>.' } },
        { target: '#homeBar', position: 'top',
          title: { en: 'DEEPX Developers', ko: 'DEEPX Developers', ja: 'DEEPX Developers', 'zh-CN': 'DEEPX Developers', 'zh-TW': 'DEEPX Developers', es: 'DEEPX Developers' },
          content: { en: 'Links to <strong>DEEPX Developers</strong> — get started, software downloads, tech docs, documents, Model Zoo, GitHub and deepx.ai, each in a new tab. On a closed network they turn off and say <strong>Offline</strong>.', ko: '<strong>DEEPX Developers</strong> 바로가기 — 시작하기, 소프트웨어 다운로드, 기술 문서, 문서, Model Zoo, GitHub, deepx.ai. 새 탭에서 열립니다. 닫힌 망에서는 꺼지고 <strong>오프라인</strong> 이라고 알려줍니다.', ja: '<strong>DEEPX Developers</strong> へのリンク — はじめに、ソフトウェアダウンロード、技術ドキュメント、ドキュメント、Model Zoo、GitHub、deepx.ai。新しいタブで開きます。インターネットに届かない環境では無効になり<strong>オフライン</strong>と表示します。', 'zh-CN': '<strong>DEEPX Developers</strong> 快捷入口 — 快速开始、软件下载、技术文档、文档、Model Zoo、GitHub 和 deepx.ai，均在新标签页打开。在封闭网络中会停用并显示<strong>离线</strong>。', 'zh-TW': '<strong>DEEPX Developers</strong> 快捷入口 — 快速開始、軟體下載、技術文件、文件、Model Zoo、GitHub 和 deepx.ai，均在新分頁開啟。在封閉網路中會停用並顯示<strong>離線</strong>。', es: 'Enlaces a <strong>DEEPX Developers</strong>: primeros pasos, descargas de software, documentación técnica, documentos, Model Zoo, GitHub y deepx.ai, cada uno en una pestaña nueva. En una red cerrada se desactivan y muestran <strong>Sin conexión</strong>.' } },
        { target: '#homeTour', position: 'bottom',
          beforeStep: function () {
            var rb = document.getElementById('replayBtn');
            if (rb) rb.style.display = '';
          },
          title: { en: 'Tutorial and intro', ko: '튜토리얼과 인트로', ja: 'チュートリアルとイントロ', 'zh-CN': '教程与片头', 'zh-TW': '教學與片頭', es: 'Tutorial e intro' },
          content: { en: '<strong>Tutorial Mode</strong> is on by default, so each module starts its own guided tour when you open it — switch it off here anytime. <strong>Replay Intro</strong> plays the opening animation again.', ko: '<strong>튜토리얼 모드</strong> 는 기본으로 켜져 있어 모듈을 열 때마다 그 모듈의 안내가 시작됩니다 — 언제든 여기서 끌 수 있습니다. <strong>인트로 재생</strong> 은 시작 애니메이션을 다시 보여줍니다.', ja: '<strong>チュートリアルモード</strong>は既定でオンで、モジュールを開くたびにそのガイドが始まります。ここでいつでもオフにできます。<strong>イントロ再生</strong>で冒頭のアニメーションをもう一度見られます。', 'zh-CN': '<strong>教程模式</strong>默认开启，每次打开模块都会启动该模块的引导——可随时在这里关闭。<strong>重播片头</strong>会再次播放开场动画。', 'zh-TW': '<strong>教學模式</strong>預設開啟，每次開啟模組都會啟動該模組的導覽——可隨時在這裡關閉。<strong>重播片頭</strong>會再次播放開場動畫。', es: 'El <strong>modo tutorial</strong> está activado por defecto: cada módulo inicia su recorrido guiado al abrirlo; desactívelo aquí cuando quiera. <strong>Repetir intro</strong> vuelve a reproducir la animación inicial.' } },
        { target: '.dx-chat-fab', position: 'left',
          title: { en: 'AI Chatbot', ko: 'AI 챗봇', ja: 'AIチャットボット', 'zh-CN': 'AI聊天机器人', 'zh-TW': 'AI聊天機器人', es: 'Chatbot de IA' },
          content: { en: 'The <strong>assistant</strong> is in every DX AI Studio module — ask about DEEPX models, the SDK, the compiler or how a module works. <strong>DEEPX Agent</strong> in its header opens the web version in a new tab.', ko: '<strong>어시스턴트</strong> 는 DX AI Studio의 모든 모듈에 있습니다 — DEEPX 모델, SDK, 컴파일러, 모듈 사용법을 물어보세요. 머리의 <strong>DEEPX Agent</strong> 는 웹 버전을 새 탭에서 엽니다.', ja: '<strong>アシスタント</strong>は DX AI Studio のすべてのモジュールにあります。DEEPX のモデル、SDK、コンパイラ、モジュールの使い方を聞いてください。ヘッダーの <strong>DEEPX Agent</strong> は Web 版を新しいタブで開きます。', 'zh-CN': '<strong>助手</strong>存在于 DX AI Studio 的每个模块中——可以询问 DEEPX 模型、SDK、编译器或模块用法。顶部的 <strong>DEEPX Agent</strong> 会在新标签页打开网页版。', 'zh-TW': '<strong>助手</strong>存在於 DX AI Studio 的每個模組中——可以詢問 DEEPX 模型、SDK、編譯器或模組用法。頂部的 <strong>DEEPX Agent</strong> 會在新分頁開啟網頁版。', es: 'El <strong>asistente</strong> está en todos los módulos de DX AI Studio: pregunte por los modelos DEEPX, el SDK, el compilador o cómo funciona un módulo. <strong>DEEPX Agent</strong> en su cabecera abre la versión web en una pestaña nueva.' } },
        { target: '.dx-chat-settings-provider', position: 'left',
          title: { en: 'Choose a Provider', ko: '제공자 선택', ja: 'プロバイダーを選択', 'zh-CN': '选择提供商', 'zh-TW': '選擇提供商', es: 'Elegir un proveedor' },
          content: { en: 'In chat settings, pick an API-key provider — <strong>OpenAI, Anthropic, Google, GitHub Models, or a Custom endpoint</strong> — or go fully offline with no key at all: <strong>local</strong> (your own Ollama-compatible server) or <strong>agent-cli</strong> (reuse an already-logged-in claude/copilot/cursor/opencode CLI).', ko: '챗봇 설정에서 API 키 제공자 — <strong>OpenAI, Anthropic, Google, GitHub Models, 또는 Custom endpoint</strong> — 를 선택하거나, 키 없이 완전 오프라인으로 사용할 수 있는 <strong>local</strong>(자체 Ollama 호환 서버) 또는 <strong>agent-cli</strong>(이미 로그인된 claude/copilot/cursor/opencode CLI 재사용)를 선택하세요.', ja: 'チャット設定で API キー方式のプロバイダー — <strong>OpenAI、Anthropic、Google、GitHub Models、または Custom endpoint</strong> — を選択するか、キー不要で完全オフラインの <strong>local</strong>(自前の Ollama 互換サーバー)または <strong>agent-cli</strong>(ログイン済みの claude/copilot/cursor/opencode CLI を再利用)を選べます。', 'zh-CN': '在聊天设置中选择需要 API 密钥的提供商——<strong>OpenAI、Anthropic、Google、GitHub Models 或 Custom endpoint</strong>——或选择完全离线、无需密钥的 <strong>local</strong>(您自己的 Ollama 兼容服务器)或 <strong>agent-cli</strong>(复用已登录的 claude/copilot/cursor/opencode CLI)。', 'zh-TW': '在聊天設定中選擇需要 API 金鑰的提供商——<strong>OpenAI、Anthropic、Google、GitHub Models 或 Custom endpoint</strong>——或選擇完全離線、不需金鑰的 <strong>local</strong>(您自己的 Ollama 相容伺服器)或 <strong>agent-cli</strong>(重複使用已登入的 claude/copilot/cursor/opencode CLI)。', es: 'En la configuración del chat, elija un proveedor con clave API — <strong>OpenAI, Anthropic, Google, GitHub Models o un endpoint personalizado</strong> — o use el modo totalmente sin conexión y sin clave: <strong>local</strong> (su propio servidor compatible con Ollama) o <strong>agent-cli</strong> (reutilice una CLI claude/copilot/cursor/opencode ya autenticada).' },
          beforeStep: function () {
            var fab = document.querySelector('.dx-chat-fab');
            if (fab && !document.querySelector('.dx-chat-window.open')) fab.click();
            setTimeout(function () {
              var settingsBtn = document.querySelector('.dx-chat-header-btn[data-action="settings"]');
              if (settingsBtn) settingsBtn.click();
            }, 200);
          },
          afterStep: function () {
            var closeBtn = document.querySelector('.dx-chat-settings-close');
            if (closeBtn) closeBtn.click();
          } },
        /* 제안 질문 칸은 비어 있을 때가 많아 (높이 0) 창 전체를 가리킨다. 투어가 끝나면 열어 둔 창을 닫는다 (release audit L-10) */
        { target: '.dx-chat-window.open', position: 'left',
          title: { en: 'Ask & Refresh Knowledge', ko: '질문하기 & 지식 새로고침', ja: '質問と知識の更新', 'zh-CN': '提问与刷新知识', 'zh-TW': '提問與刷新知識', es: 'Preguntar y actualizar conocimiento' },
          content: { en: 'Click a <strong>suggested question</strong> to get started quickly, or type your own — e.g. "ask the chatbot to explain a failed compile error" in DX Compiler. Use <strong>Refresh knowledge</strong> to re-sync the bot\'s SDK knowledge with the latest .deepx docs.', ko: '<strong>추천 질문</strong>을 클릭해 빠르게 시작하거나 직접 입력하세요 — 예: DX Compiler에서 "컴파일 실패 오류를 챗봇에게 설명해달라고 요청". <strong>지식 새로고침</strong>으로 챗봇의 SDK 지식을 최신 .deepx 문서와 재동기화할 수 있습니다.', ja: '<strong>おすすめの質問</strong>をクリックしてすぐに始めるか、自分で入力してください — 例：DX Compilerで「コンパイル失敗エラーをチャットボットに説明してもらう」。<strong>知識を更新</strong>でボットのSDK知識を最新の.deepxドキュメントと再同期できます。', 'zh-CN': '点击<strong>推荐问题</strong>快速开始，或自行输入——例如在 DX Compiler 中「让聊天机器人解释一次编译失败的错误」。使用<strong>刷新知识</strong>可将机器人的 SDK 知识与最新的 .deepx 文档重新同步。', 'zh-TW': '點擊<strong>推薦問題</strong>快速開始，或自行輸入——例如在 DX Compiler 中「請聊天機器人解釋一次編譯失敗的錯誤」。使用<strong>刷新知識</strong>可將機器人的 SDK 知識與最新的 .deepx 文件重新同步。', es: 'Haga clic en una <strong>pregunta sugerida</strong> para empezar rápido, o escriba la suya — por ejemplo, en DX Compiler: "pídale al chatbot que explique un error de compilación fallido". Use <strong>Actualizar conocimiento</strong> para resincronizar el conocimiento del SDK del bot con la documentación .deepx más reciente.' },
          beforeStep: function () {
            var fab = document.querySelector('.dx-chat-fab');
            if (fab && !document.querySelector('.dx-chat-window.open')) fab.click();
          },
          afterStep: function () {
            if (window.DXChat && typeof DXChat.toggle === 'function' && document.querySelector('.dx-chat-window.open')) DXChat.toggle();
          } }
      ] }
  ];

  function toggleTutorialMode() {
    _tutorialMode = !_tutorialMode;
    localStorage.setItem('dx-tutorial-mode', _tutorialMode ? 'on' : 'off');
    updateTutorialUI();
    sendTutorialModeToIframe();
  }

  function updateTutorialUI() {
    const sw = document.getElementById('dxt-mode-switch');
    if (sw) {
      sw.className = 'dxt-lc-switch' + (_tutorialMode ? ' on' : '');
      sw.setAttribute('aria-checked', String(_tutorialMode));
    }
    const label = document.getElementById('dxt-mode-label');
    if (label) {
      label.textContent = _tutorialMode ? 'ON' : 'OFF';
      label.className = 'dxt-lc-mode' + (_tutorialMode ? ' is-on' : '');
    }
    // 네비 버튼 피드백
    const navBtn = document.querySelector('.dxt-toggle-btn');
    if (navBtn) {
      navBtn.style.opacity = _tutorialMode ? '1' : '0.5';
      var _tutorialLabels = {en:'Tutorial Mode',ko:'튜토리얼 모드',ja:'チュートリアルモード','zh-CN':'教程模式','zh-TW':'教學模式',es:'Modo tutorial'};
      navBtn.title = (_tutorialLabels[_lang()] || _tutorialLabels.en) + ': '
                   + (_tutorialMode ? 'ON' : 'OFF');
    }
  }

  function sendTutorialModeToIframe() {
    const iframe = document.getElementById('appIframe');
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.postMessage({
        type: _tutorialMode ? 'dx-tutorial-start' : 'dx-tutorial-stop'
      }, '*');
    }
  }

  function buildTutorialCard() {
    // 무대의 투어 자리 (spec 2026-09-23 §5.1). 없으면 예전처럼 #landing 끝.
    const tour = document.getElementById('homeTour');
    const landing = document.getElementById('landing');
    if (!landing) return;

    const card = document.createElement('div');
    card.className = 'dxt-launcher-card';
    card.id = 'dxt-tutorial-card';
    card.onclick = toggleTutorialMode;
    card.innerHTML = `
      <span class="dxt-lc-icon">${(typeof DXIcon === 'function') ? DXIcon('graduation') : ''}</span>
      <div class="dxt-lc-text">
        <div class="dxt-lc-title">
          <span id="dxt-mode-title" data-i18n="Tutorial Mode">Tutorial Mode</span>
          <span id="dxt-mode-label" aria-hidden="true" class="dxt-lc-mode${_tutorialMode ? ' is-on' : ''}">${_tutorialMode ? 'ON' : 'OFF'}</span>
        </div>
        <div class="dxt-lc-desc" data-i18n="Automatically start interactive tutorials when launching apps">Automatically start interactive tutorials when launching apps
        </div>
      </div>
      <button type="button" class="dxt-lc-switch ${_tutorialMode ? 'on' : ''}" id="dxt-mode-switch"
              role="switch" aria-checked="${_tutorialMode}" aria-labelledby="dxt-mode-title"
              onclick="event.stopPropagation()"></button>
    `;

    if (tour) tour.insertBefore(card, tour.firstChild);
    else landing.appendChild(card);

    const sw = card.querySelector('.dxt-lc-switch');
    sw.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleTutorialMode();
    });

    // CSS 주입
    if (!document.getElementById('dxt-card-style')) {
      const style = document.createElement('style');
      style.id = 'dxt-card-style';
      style.textContent = `
        /* The card is already inserted into #homeTour, inside #landing —
           position:fixed was the only thing lifting it out of the page, onto
           the hero. In flow it sits where the DOM already put it. Colours come
           from the theme; the hard-coded dark ones survived light mode as a
           dark panel with dark text. */
        .dxt-launcher-card {
          display: flex; align-items: center; gap: 12px;
          width: 100%; max-width: 1680px;
          margin: var(--sp-5) auto 0; box-sizing: border-box;
          background: var(--ap-panel);
          border: 0; border-radius: 18px;
          box-shadow: var(--ap-shadow);
          padding: 13px 16px; cursor: pointer;
        }
        .dxt-launcher-card:hover { background: var(--ap-panel); }
        .dxt-launcher-card .dxt-lc-text { flex: 1; min-width: 0; }
        .dxt-launcher-card .dxt-lc-icon { display: none; }
        .dxt-launcher-card .dxt-lc-title { font-size: var(--ap-t-lead); font-weight: 500; color: var(--ap-ink); }
        .dxt-launcher-card .dxt-lc-desc { font-size: var(--ap-t-body); color: var(--ap-ink-3); margin-top: 1px; }
        .dxt-launcher-card .dxt-lc-mode { margin-left: 6px; font-size: var(--ap-t-body); color: var(--ap-ink-3); }
        .dxt-launcher-card .dxt-lc-mode.is-on { color: var(--ap-blue); }
        .dxt-launcher-card .dxt-lc-switch {
          width: 40px; height: 22px; border-radius: 11px; border: none;
          background: var(--ap-fill); cursor: pointer; position: relative;
          transition: background 0.2s; flex-shrink: 0;
        }
        .dxt-launcher-card .dxt-lc-switch::after {
          content: ''; position: absolute; top: 3px; left: 3px;
          width: 16px; height: 16px; border-radius: 50%;
          background: var(--ap-on-blue); transition: transform 0.2s;
        }
        .dxt-launcher-card .dxt-lc-switch.on { background: var(--ap-green); }
        .dxt-launcher-card .dxt-lc-switch.on::after { transform: translateX(18px); }

      `;
      document.head.appendChild(style);
    }
  }

  function addNavTutorialBtn() {
    const topRight = document.querySelector('.top-bar-right');
    if (!topRight) return;
    const btn = document.createElement('button');
    btn.className = 'dx-toolbar-btn dxt-toggle-btn';
    var _tutorialLabels = {en:'Tutorial Mode',ko:'튜토리얼 모드',ja:'チュートリアルモード','zh-CN':'教程模式','zh-TW':'教學模式',es:'Modo tutorial'};
    btn.title = _tutorialLabels[_lang()] || _tutorialLabels.en;
    /* SF Symbols 계열 라인 글리프 — 이모지는 chrome 에 안 어울린다 */
    btn.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8l9-4 9 4-9 4-9-4z"/><path d="M7 10.5V16c0 1.1 2.2 2 5 2s5-.9 5-2v-5.5"/></svg>';
    btn.addEventListener('click', toggleTutorialMode);
    topRight.insertBefore(btn, topRight.firstChild);
  }

  function hookIframeLoad() {
    const iframe = document.getElementById('appIframe');
    if (!iframe) return;
    iframe.addEventListener('load', () => {
      if (_tutorialMode) {
        // Give the iframe app time to initialize, then send message
        setTimeout(sendTutorialModeToIframe, 600);
      }
    });
  }

  function connectLauncherToolbar() {
    if (!_engine) {
      console.warn('[LauncherTutorial] toolbar restore skipped: tutorial engine is not ready');
      return;
    }
    if (typeof DXToolbar !== 'undefined' && typeof DXToolbar.connectTutorial === 'function') {
      DXToolbar.connectTutorial(_engine, { owner: 'launcher' });
    }
  }

  function suspendLauncherTutorial() {
    if (_engine && typeof _engine.suspend === 'function') {
      _engine.suspend();
      return;
    }
    if (window._dxTutorial && typeof window._dxTutorial.suspend === 'function') {
      window._dxTutorial.suspend();
    }
  }

  function initLauncherHelp() {
    if (typeof DXTutorial === 'undefined') return;

    function startWhenShellReady() {
      if (document.documentElement.classList.contains('launcher-boot-pending') ||
          document.getElementById('splashOverlay') ||
          (window.DXLauncher && typeof DXLauncher.isLauncherShellBlocked === 'function' &&
           DXLauncher.isLauncherShellBlocked())) {
        setTimeout(startWhenShellReady, 150);
        return;
      }
      DXTutorial.create({
      appId: 'launcher',
      sections: sections,
      getLang: function () {
        return (typeof DXI18n !== 'undefined' && DXI18n.lang) || _lang();
      },
      setupButtons: function (engine) {
        _engine = engine;
        connectLauncherToolbar();
      }
    });
    window.LauncherTutorial = {
      connectToolbar: connectLauncherToolbar,
      suspend: suspendLauncherTutorial,
      engine: function () { return _engine; }
    };
    }

    startWhenShellReady();
  }

  function init() {
    buildTutorialCard();
    // addNavTutorialBtn() — DXToolbar v2 handles this
    hookIframeLoad();
    initLauncherHelp();
    updateTutorialUI();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window._dxTutorialMode = {
    toggle: toggleTutorialMode,
    isOn: () => _tutorialMode
  };

})();
if (typeof DXI18n !== 'undefined' && typeof DXI18n.onLangChange === 'function') {
  DXI18n.onLangChange(function() {
    if (typeof DXLauncher !== 'undefined' && typeof DXLauncher.refreshLauncherChrome === 'function') DXLauncher.refreshLauncherChrome();
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
