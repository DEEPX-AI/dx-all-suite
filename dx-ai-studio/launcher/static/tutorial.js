
(function () {
  'use strict';

  // Tutorial mode is ON by default; it's only off when the user explicitly turned it off.
  const _stored = localStorage.getItem('dx-tutorial-mode');
  let _tutorialMode = _stored !== 'off';
  const _lang = () => localStorage.getItem('dx-lang') || 'en';
  let _engine = null;
// Launcher 자체 화면을 위한 튜토리얼 섹션이다. iframe 모듈 튜토리얼은 각 모듈이 소유한다.
  const sections = [
    { id: 'home', icon: '🏠',
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
        { target: '#dxt-tutorial-card', position: 'right',
          title: { en: 'Tutorial Mode', ko: '튜토리얼 모드', ja: 'チュートリアルモード', 'zh-CN': '教程模式', 'zh-TW': '教學模式', es: 'Modo tutorial' },
          content: { en: 'This is <strong>Tutorial Mode</strong> — <strong>on by default</strong>, so interactive tutorials start automatically when you open a module. Don\'t want them? Turn it <strong>off</strong> here anytime.', ko: '여기가 <strong>튜토리얼 모드</strong>입니다 — <strong>기본으로 켜져</strong> 있어 모듈을 열면 인터랙티브 튜토리얼이 자동으로 시작됩니다. 원치 않으면 언제든 여기서 <strong>끄세요</strong>.', ja: 'これが<strong>チュートリアルモード</strong>です — <strong>デフォルトでオン</strong>なので、モジュールを開くとインタラクティブチュートリアルが自動的に始まります。不要ならいつでもここで<strong>オフ</strong>にできます。', 'zh-CN': '这是<strong>教程模式</strong>——<strong>默认开启</strong>，打开模块时会自动启动交互式教程。不需要？随时在此<strong>关闭</strong>。', 'zh-TW': '這是<strong>教學模式</strong>——<strong>預設開啟</strong>，開啟模組時會自動啟動互動式教學。不需要？隨時在此<strong>關閉</strong>。', es: 'Este es el <strong>modo tutorial</strong>: <strong>activado por defecto</strong>, así que los tutoriales interactivos se inician automáticamente al abrir un módulo. ¿No los quieres? Desactívalo <strong>aquí</strong> cuando quieras.' } },
        { target: '.top-bar', position: 'bottom',
          title: { en: 'Launcher Shell', ko: '런처 셸', ja: 'ランチャーシェル', 'zh-CN': '启动器外壳', 'zh-TW': '啟動器殼層', es: 'Shell del iniciador' },
          content: { en: 'The launcher shell keeps <strong>DX AI Studio branding</strong>, module status, and shared controls visible while you browse home and SDK Library.', ko: '런처 셸은 홈과 SDK Library를 탐색하는 동안 <strong>DX AI Studio 브랜딩</strong>, 모듈 상태, 공유 컨트롤을 유지합니다.', ja: 'ランチャーシェルはホームとSDK Libraryを閲覧中も<strong>DX AI Studioブランド</strong>、モジュール状態、共通コントロールを表示します。', 'zh-CN': '启动器外壳在浏览主页和 SDK Library 时保持<strong>DX AI Studio 品牌</strong>、模块状态和共享控件可见。', 'zh-TW': '啟動器殼層在瀏覽首頁和 SDK Library 時保持<strong>DX AI Studio 品牌</strong>、模組狀態和共用控制項可見。', es: 'El shell del iniciador mantiene visibles la <strong>marca DX AI Studio</strong>, el estado de los módulos y los controles compartidos mientras navega por inicio y SDK Library.' } },
        { target: '#launcherToolbar', position: 'bottom',
          title: { en: 'Shared Top Toolbar', ko: '공유 상단 툴바', ja: '共通トップツールバー', 'zh-CN': '共享顶部工具栏', 'zh-TW': '共用頂部工具列', es: 'Barra superior compartida' },
          content: { en: 'The top toolbar hosts <strong>language (🌏)</strong> and <strong>tutorial (🎓)</strong> for every launcher view.', ko: '상단 툴바에서 <strong>언어(🌏)</strong>, <strong>튜토리얼(🎓)</strong>을 사용합니다.', ja: '上部ツールバーで<strong>言語(🌏)</strong>、<strong>チュートリアル(🎓)</strong>を利用します。', 'zh-CN': '顶部工具栏提供<strong>语言(🌏)</strong>和<strong>教程(🎓)</strong>。', 'zh-TW': '頂部工具列提供<strong>語言(🌏)</strong>和<strong>教學(🎓)</strong>。', es: 'La barra superior incluye <strong>idioma (🌏)</strong> y <strong>tutorial (🎓)</strong>.' } },
        { target: '.status-dots', position: 'bottom',
          title: { en: 'Module Health Dots', ko: '모듈 상태 점', ja: 'モジュール状態ドット', 'zh-CN': '模块状态点', 'zh-TW': '模組狀態點', es: 'Indicadores de módulos' },
          content: { en: '<strong>Green</strong> means the module server is reachable; <strong>red</strong> means it is offline or not installed yet.', ko: '<strong>초록</strong>은 모듈 서버 연결 가능, <strong>빨강</strong>은 오프라인 또는 미설치 상태입니다.', ja: '<strong>緑</strong>はモジュールサーバー到達可能、<strong>赤</strong>はオフラインまたは未インストールです。', 'zh-CN': '<strong>绿色</strong>表示模块服务器可访问；<strong>红色</strong>表示离线或未安装。', 'zh-TW': '<strong>綠色</strong>表示模組伺服器可連線；<strong>紅色</strong>表示離線或未安裝。', es: '<strong>Verde</strong> = servidor del módulo accesible; <strong>rojo</strong> = sin conexión o no instalado.' } },
        { target: '#orbitalContainer', position: 'bottom',
          title: { en: 'Launch DX Modules', ko: 'DX 모듈 실행', ja: 'DXモジュール起動', 'zh-CN': '启动DX模块', 'zh-TW': '啟動DX模組', es: 'Iniciar módulos DX' },
          content: { en: 'Pick an orbital card to open App, Stream, Compiler, Monitor, and other DX AI Studio modules inside the shared frame.', ko: '오비탈 카드에서 App, Stream, Compiler, Monitor 등 DX AI Studio 모듈을 공유 프레임에서 실행합니다.', ja: 'オービタルカードからApp、Stream、Compiler、MonitorなどのDX AI Studioモジュールを共有フレームで開きます。', 'zh-CN': '从轨道卡片打开 App、Stream、Compiler、Monitor 等 DX AI Studio 模块。', 'zh-TW': '從軌道卡片開啟 App、Stream、Compiler、Monitor 等 DX AI Studio 模組。', es: 'Elija una tarjeta orbital para abrir App, Stream, Compiler, Monitor y otros módulos de DX AI Studio.' } },
        { target: '#ecosystemPoster', position: 'right', skipScroll: true,
          title: { en: 'Physical AI Ecosystem', ko: 'Physical AI 생태계', ja: 'Physical AI エコシステム', 'zh-CN': 'Physical AI 生态系统', 'zh-TW': 'Physical AI 生態系統', es: 'Ecosistema de IA física' },
          content: { en: 'Click this poster to see how DEEPX connects the <strong>Physical AI ecosystem</strong> — Ultralytics YOLO, PaddlePaddle, and Raspberry Pi around the DEEPX NPU.', ko: '이 포스터를 클릭하면 DEEPX가 <strong>Physical AI 생태계</strong>(Ultralytics YOLO · PaddlePaddle · Raspberry Pi)를 어떻게 잇는지 볼 수 있습니다.', ja: 'このポスターをクリックすると、DEEPXが<strong>Physical AIエコシステム</strong>（Ultralytics YOLO・PaddlePaddle・Raspberry Pi）をどうつなぐかを確認できます。', 'zh-CN': '点击此海报，了解 DEEPX 如何连接<strong>Physical AI 生态系统</strong>——Ultralytics YOLO、PaddlePaddle 与树莓派。', 'zh-TW': '點擊此海報，了解 DEEPX 如何連接<strong>Physical AI 生態系統</strong>——Ultralytics YOLO、PaddlePaddle 與樹莓派。', es: 'Haga clic en este póster para ver cómo DEEPX conecta el <strong>ecosistema de IA física</strong>: Ultralytics YOLO, PaddlePaddle y Raspberry Pi en torno a la NPU de DEEPX.' } },
        { target: '#landingPoster', position: 'right',
          title: { en: 'Explore Platform', ko: '플랫폼 탐색', ja: 'プラットフォーム探索', 'zh-CN': '探索平台', 'zh-TW': '探索平台', es: 'Explorar plataforma' },
          content: { en: 'Click the poster to open the <strong>platform overview</strong> with module specs and quick product context.', ko: '포스터를 클릭하면 <strong>플랫폼 개요</strong>와 모듈 사양을 볼 수 있습니다.', ja: 'ポスターをクリックすると<strong>プラットフォーム概要</strong>とモジュール仕様を開きます。', 'zh-CN': '点击海报打开<strong>平台概览</strong>和模块规格。', 'zh-TW': '點擊海報開啟<strong>平台概覽</strong>和模組規格。', es: 'Haga clic en el póster para abrir la <strong>visión general de la plataforma</strong> y las especificaciones de los módulos.' } },
        { target: '.about-book-card:not(.sdk-card)', position: 'bottom',
          title: { en: 'About DEEPX', ko: 'About DEEPX', ja: 'About DEEPX', 'zh-CN': 'About DEEPX', 'zh-TW': 'About DEEPX', es: 'About DEEPX' },
          content: { en: 'Open the <strong>interactive DEEPX encyclopedia</strong> — explore hotspots on the DX-M1/DX-M2 chip die and click through the company\'s technology, product, and vision stories.', ko: '<strong>인터랙티브 DEEPX 백과사전</strong>을 엽니다 — DX-M1/DX-M2 칩 다이의 핫스팟을 탐험하고 기술·제품·비전 스토리를 클릭으로 살펴보세요.', ja: '<strong>インタラクティブなDEEPX百科事典</strong>を開きます — DX-M1/DX-M2チップダイのホットスポットを探索し、技術・製品・ビジョンのストーリーをクリックで閲覧できます。', 'zh-CN': '打开<strong>DEEPX 交互式百科全书</strong>——探索 DX-M1/DX-M2 芯片裸片上的热点，点击浏览公司的技术、产品与愿景故事。', 'zh-TW': '開啟<strong>DEEPX 互動式百科全書</strong>——探索 DX-M1/DX-M2 晶片裸晶上的熱點，點擊瀏覽公司的技術、產品與願景故事。', es: 'Abra la <strong>enciclopedia interactiva de DEEPX</strong>: explore los puntos clave del die de los chips DX-M1/DX-M2 y recorra las historias de tecnología, producto y visión de la empresa.' } },
        { target: '.about-book-card.sdk-card', position: 'bottom',
          title: { en: 'SDK Library', ko: 'SDK Library', ja: 'SDK Library', 'zh-CN': 'SDK Library', 'zh-TW': 'SDK Library', es: 'SDK Library' },
          content: { en: 'Open the <strong>SDK Library</strong> to browse technical documentation without leaving the launcher shell.', ko: '런처를 벗어나지 않고 <strong>SDK Library</strong>에서 기술 문서를 탐색합니다.', ja: 'ランチャーを離れずに<strong>SDK Library</strong>で技術ドキュメントを閲覧します。', 'zh-CN': '无需离开启动器即可在<strong>SDK Library</strong>中浏览技术文档。', 'zh-TW': '無需離開啟動器即可在<strong>SDK Library</strong>中瀏覽技術文件。', es: 'Abra <strong>SDK Library</strong> para explorar documentación técnica sin salir del launcher.' } },
        { target: '#deepxLinks', position: 'top', skipScroll: true,
          title: { en: 'DEEPX Resources', ko: 'DEEPX 리소스', ja: 'DEEPXリソース', 'zh-CN': 'DEEPX 资源', 'zh-TW': 'DEEPX 資源', es: 'Recursos DEEPX' },
          content: { en: 'Quick links to DEEPX\'s official sites — docs, the <strong>DEEPX Agent</strong> (ask anything), Model Zoo, downloads, GitHub, and deepx.ai. Each opens in a new tab.', ko: 'DEEPX 공식 사이트 바로가기 — 문서, <strong>DEEPX Agent</strong>(무엇이든 질문), Model Zoo, 다운로드, GitHub, deepx.ai. 각 항목은 새 탭에서 열립니다.', ja: 'DEEPX公式サイトへのショートカット — ドキュメント、<strong>DEEPX Agent</strong>（何でも質問）、Model Zoo、ダウンロード、GitHub、deepx.ai。それぞれ新しいタブで開きます。', 'zh-CN': 'DEEPX 官方站点快捷入口 — 文档、<strong>DEEPX Agent</strong>（有问必答）、Model Zoo、下载、GitHub 和 deepx.ai。均在新标签页打开。', 'zh-TW': 'DEEPX 官方網站快捷入口 — 文件、<strong>DEEPX Agent</strong>（有問必答）、Model Zoo、下載、GitHub 和 deepx.ai。均在新分頁開啟。', es: 'Accesos directos a los sitios oficiales de DEEPX: documentación, el <strong>DEEPX Agent</strong> (pregunte lo que sea), Model Zoo, descargas, GitHub y deepx.ai. Cada uno se abre en una pestaña nueva.' } },
        { target: '#replayBtn', position: 'top', skipScroll: true,
          beforeStep: function () {
            var rb = document.getElementById('replayBtn');
            if (rb) rb.style.display = '';
          },
          title: { en: 'Replay Intro', ko: '인트로 재생', ja: 'イントロ再生', 'zh-CN': '重播介绍', 'zh-TW': '重播介紹', es: 'Repetir introducción' },
          content: { en: 'Replay the DX AI Studio intro animation from the beginning.', ko: 'DX AI Studio 인트로 애니메이션을 처음부터 다시 재생합니다.', ja: 'DX AI Studioのイントロアニメーションを最初から再生します。', 'zh-CN': '从头重播 DX AI Studio 介绍动画。', 'zh-TW': '從頭重播 DX AI Studio 介紹動畫。', es: 'Repita la animación de introducción de DX AI Studio desde el inicio.' } },
        { target: '.dx-chat-fab', position: 'left',
          title: { en: '💬 AI Chatbot', ko: '💬 AI 챗봇', ja: '💬 AIチャットボット', 'zh-CN': '💬 AI聊天机器人', 'zh-TW': '💬 AI聊天機器人', es: '💬 Chatbot de IA' },
          content: { en: 'The <strong>💬 assistant</strong> is available in every DX AI Studio module. Click it anytime to ask about DeepX models, the SDK, the compiler, or how any module works.', ko: '<strong>💬 어시스턴트</strong>는 모든 DX AI Studio 모듈에서 사용할 수 있습니다. 언제든 클릭하여 DeepX 모델, SDK, 컴파일러, 각 모듈 사용법에 대해 질문하세요.', ja: '<strong>💬 アシスタント</strong>はすべてのDX AI Studioモジュールで利用できます。いつでもクリックして、DeepXモデル、SDK、コンパイラ、各モジュールの使い方について質問できます。', 'zh-CN': '<strong>💬 助手</strong>在每个 DX AI Studio 模块中都可用。随时点击，询问关于 DeepX 模型、SDK、编译器或任意模块用法的问题。', 'zh-TW': '<strong>💬 助手</strong>在每個 DX AI Studio 模組中都可使用。隨時點擊，詢問關於 DeepX 模型、SDK、編譯器或任意模組用法的問題。', es: 'El <strong>asistente 💬</strong> está disponible en todos los módulos de DX AI Studio. Haga clic en cualquier momento para preguntar sobre modelos DeepX, el SDK, el compilador o el funcionamiento de cualquier módulo.' } },
        { target: '.dx-chat-settings-provider', position: 'left',
          title: { en: 'Choose a Provider', ko: '제공자 선택', ja: 'プロバイダーを選択', 'zh-CN': '选择提供商', 'zh-TW': '選擇提供商', es: 'Elegir un proveedor' },
          content: { en: 'In chat settings (⚙️), pick an API-key provider — <strong>OpenAI, Anthropic, Google, GitHub Models, or a Custom endpoint</strong> — or go fully offline with no key at all: <strong>local</strong> (your own Ollama-compatible server) or <strong>agent-cli</strong> (reuse an already-logged-in claude/copilot/cursor/opencode CLI).', ko: '챗봇 설정(⚙️)에서 API 키 제공자 — <strong>OpenAI, Anthropic, Google, GitHub Models, 또는 Custom endpoint</strong> — 를 선택하거나, 키 없이 완전 오프라인으로 사용할 수 있는 <strong>local</strong>(자체 Ollama 호환 서버) 또는 <strong>agent-cli</strong>(이미 로그인된 claude/copilot/cursor/opencode CLI 재사용)를 선택하세요.', ja: 'チャット設定(⚙️)で API キー方式のプロバイダー — <strong>OpenAI、Anthropic、Google、GitHub Models、または Custom endpoint</strong> — を選択するか、キー不要で完全オフラインの <strong>local</strong>(自前の Ollama 互換サーバー)または <strong>agent-cli</strong>(ログイン済みの claude/copilot/cursor/opencode CLI を再利用)を選べます。', 'zh-CN': '在聊天设置(⚙️)中选择需要 API 密钥的提供商——<strong>OpenAI、Anthropic、Google、GitHub Models 或 Custom endpoint</strong>——或选择完全离线、无需密钥的 <strong>local</strong>(您自己的 Ollama 兼容服务器)或 <strong>agent-cli</strong>(复用已登录的 claude/copilot/cursor/opencode CLI)。', 'zh-TW': '在聊天設定(⚙️)中選擇需要 API 金鑰的提供商——<strong>OpenAI、Anthropic、Google、GitHub Models 或 Custom endpoint</strong>——或選擇完全離線、不需金鑰的 <strong>local</strong>(您自己的 Ollama 相容伺服器)或 <strong>agent-cli</strong>(重複使用已登入的 claude/copilot/cursor/opencode CLI)。', es: 'En la configuración del chat (⚙️), elija un proveedor con clave API — <strong>OpenAI, Anthropic, Google, GitHub Models o un endpoint personalizado</strong> — o use el modo totalmente sin conexión y sin clave: <strong>local</strong> (su propio servidor compatible con Ollama) o <strong>agent-cli</strong> (reutilice una CLI claude/copilot/cursor/opencode ya autenticada).' },
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
        { target: '.dx-chat-suggestions', position: 'left',
          title: { en: 'Ask & Refresh Knowledge', ko: '질문하기 & 지식 새로고침', ja: '質問と知識の更新', 'zh-CN': '提问与刷新知识', 'zh-TW': '提問與刷新知識', es: 'Preguntar y actualizar conocimiento' },
          content: { en: 'Click a <strong>suggested question</strong> to get started quickly, or type your own — e.g. "ask the chatbot to explain a failed compile error" in DX Compiler. Use <strong>Refresh knowledge</strong> (⚙️) to re-sync the bot\'s SDK knowledge with the latest .deepx docs.', ko: '<strong>추천 질문</strong>을 클릭해 빠르게 시작하거나 직접 입력하세요 — 예: DX Compiler에서 "컴파일 실패 오류를 챗봇에게 설명해달라고 요청". <strong>지식 새로고침</strong>(⚙️)으로 챗봇의 SDK 지식을 최신 .deepx 문서와 재동기화할 수 있습니다.', ja: '<strong>おすすめの質問</strong>をクリックしてすぐに始めるか、自分で入力してください — 例：DX Compilerで「コンパイル失敗エラーをチャットボットに説明してもらう」。<strong>知識を更新</strong>(⚙️)でボットのSDK知識を最新の.deepxドキュメントと再同期できます。', 'zh-CN': '点击<strong>推荐问题</strong>快速开始，或自行输入——例如在 DX Compiler 中「让聊天机器人解释一次编译失败的错误」。使用<strong>刷新知识</strong>(⚙️)可将机器人的 SDK 知识与最新的 .deepx 文档重新同步。', 'zh-TW': '點擊<strong>推薦問題</strong>快速開始，或自行輸入——例如在 DX Compiler 中「請聊天機器人解釋一次編譯失敗的錯誤」。使用<strong>刷新知識</strong>(⚙️)可將機器人的 SDK 知識與最新的 .deepx 文件重新同步。', es: 'Haga clic en una <strong>pregunta sugerida</strong> para empezar rápido, o escriba la suya — por ejemplo, en DX Compiler: "pídale al chatbot que explique un error de compilación fallido". Use <strong>Actualizar conocimiento</strong> (⚙️) para resincronizar el conocimiento del SDK del bot con la documentación .deepx más reciente.' },
          beforeStep: function () {
            var fab = document.querySelector('.dx-chat-fab');
            if (fab && !document.querySelector('.dx-chat-window.open')) fab.click();
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
    if (sw) sw.className = 'dxt-lc-switch' + (_tutorialMode ? ' on' : '');
    const label = document.getElementById('dxt-mode-label');
    if (label) {
      label.textContent = _tutorialMode ? 'ON' : 'OFF';
      label.style.color = _tutorialMode ? '#58a6ff' : '#888';
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
    // orbital 레이아웃: footer 위에 삽입
    const footer = document.querySelector('.landing-footer');
    const landing = document.getElementById('landing');
    if (!landing) return;

    const card = document.createElement('div');
    card.className = 'dxt-launcher-card';
    card.id = 'dxt-tutorial-card';
    card.onclick = toggleTutorialMode;
    card.innerHTML = `
      <span class="dxt-lc-icon">🎓</span>
      <div class="dxt-lc-text">
        <div class="dxt-lc-title">
          <span class="ko">Tutorial Mode</span>
          <span class="en">Tutorial Mode</span>
          <span class="ja">Tutorial Mode</span>
          <span class="zh-CN">Tutorial Mode</span>
          <span class="zh-TW">Tutorial Mode</span>
          <span class="es">Modo tutorial</span>
          <span id="dxt-mode-label" style="margin-left:6px;font-size:12px;color:${_tutorialMode ? '#58a6ff' : '#888'}">${_tutorialMode ? 'ON' : 'OFF'}</span>
        </div>
        <div class="dxt-lc-desc">
          <span class="ko">앱 실행 시 인터랙티브 튜토리얼을 자동으로 시작합니다</span>
          <span class="en">Automatically start interactive tutorials when launching apps</span>
          <span class="ja">アプリ起動時にインタラクティブチュートリアルを自動的に開始します</span>
          <span class="zh-CN">启动应用时自动开始交互式教程</span>
          <span class="zh-TW">啟動應用程式時自動開始互動式教學</span>
          <span class="es">Inicia automáticamente tutoriales interactivos al abrir aplicaciones</span>
        </div>
      </div>
      <button class="dxt-lc-switch ${_tutorialMode ? 'on' : ''}" id="dxt-mode-switch"
              onclick="event.stopPropagation()"></button>
    `;

    if (footer) landing.insertBefore(card, footer);
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
        .dxt-launcher-card {
          position: fixed; top: 64px; left: 14px;
          display: flex; align-items: center; gap: 10px;
          background: rgba(30, 35, 50, 0.92); backdrop-filter: blur(12px);
          border: 1px solid rgba(88, 166, 255, 0.25); border-radius: 10px;
          padding: 10px 18px; cursor: pointer; z-index: 100;
          box-shadow: 0 4px 24px rgba(0,0,0,0.3);
          transition: border-color 0.2s, box-shadow 0.2s;
          max-width: 360px;
        }
        .dxt-launcher-card:hover {
          border-color: rgba(88, 166, 255, 0.5);
          box-shadow: 0 4px 32px rgba(88, 166, 255, 0.15);
        }
        .dxt-lc-icon { font-size: 28px; }
        .dxt-lc-title { font-size: 15px; font-weight: 600; color: #e6edf3; }
        .dxt-lc-desc { font-size: 12px; color: #8b949e; margin-top: 2px; }
        .dxt-lc-switch {
          width: 44px; height: 24px; border-radius: 12px; border: none;
          background: #484f58; cursor: pointer; position: relative;
          transition: background 0.2s; flex-shrink: 0;
        }
        .dxt-lc-switch::after {
          content: ''; position: absolute; top: 3px; left: 3px;
          width: 18px; height: 18px; border-radius: 50%;
          background: #fff; transition: transform 0.2s;
        }
        .dxt-lc-switch.on { background: #58a6ff; }
        .dxt-lc-switch.on::after { transform: translateX(20px); }

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
    btn.innerHTML = '🎓';
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
