/* ═══════════════════════════════════════════════════════════════
   DX Agent Dev — Tutorial Definitions
   5 sections (overview / console / controls / showcase / activity),
   reference docs, 6-language support (ko/en/ja/zh-CN/zh-TW/es)
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  function _scrollTo(sel) {
    var el = document.querySelector(sel);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function _ensureConsoleStatusBar() {
    var bar = document.getElementById('console-status-bar');
    if (!bar) return;
    bar.removeAttribute('hidden');
    bar.style.display = 'block';
    bar.style.minHeight = '24px';
    if (!bar.textContent || !bar.textContent.trim()) {
      bar.textContent = 'Session output: workspace/agent-sessions/demo-session/';
    }
    bar.scrollIntoView({ block: 'nearest' });
  }

  var sections = [

    { id: 'overview', icon: '🖥️',
      title: { ko: '🖥️ 콘솔 개요', en: '🖥️ Console Overview', ja: '🖥️ コンソール概要', 'zh-CN': '🖥️ 控制台概述', 'zh-TW': '🖥️ 主控台概述', es: '🖥️ Resumen de la consola' },
      description: { ko: 'DX Agent Dev의 전체 구성과 핵심 기능 소개', en: 'Introduction to the layout and key features of DX Agent Dev', ja: 'DX Agent Devの全体構成と主要機能の紹介', 'zh-CN': 'DX Agent Dev的整体布局和主要功能介绍', 'zh-TW': 'DX Agent Dev的整體佈局和主要功能介紹', es: 'Introducción al diseño y funciones clave de DX Agent Dev' },
      steps: [
        { target: '.app-title', position: 'bottom',
          title: { ko: 'DX Agent Dev', en: 'DX Agent Dev', ja: 'DX Agent Dev', 'zh-CN': 'DX Agent Dev', 'zh-TW': 'DX Agent Dev', es: 'DX Agent Dev' },
          content: { ko: '<strong>DX Agent Dev</strong>는 <strong>자연어 명령</strong>만으로 NPU 애플리케이션을 만드는 AI 코딩 콘솔입니다. 만들고 싶은 것을 설명하면 AI 에이전트가 코드를 작성·실행합니다.', en: '<strong>DX Agent Dev</strong> is an AI coding console that builds NPU applications from <strong>natural-language commands</strong>. Describe what you want and the AI agent writes and runs the code.', ja: '<strong>DX Agent Dev</strong>は<strong>自然言語の指示</strong>だけでNPUアプリケーションを作成するAIコーディングコンソールです。作りたいものを説明すると、AIエージェントがコードを記述・実行します。', 'zh-CN': '<strong>DX Agent Dev</strong>是仅凭<strong>自然语言指令</strong>构建NPU应用的AI编码控制台。描述您的需求，AI智能体即可编写并运行代码。', 'zh-TW': '<strong>DX Agent Dev</strong>是僅憑<strong>自然語言指令</strong>建構NPU應用的AI編碼主控台。描述您的需求，AI代理程式即可編寫並執行程式碼。', es: '<strong>DX Agent Dev</strong> es una consola de codificación con IA que crea aplicaciones NPU con <strong>comandos en lenguaje natural</strong>. Describa lo que quiere y el agente de IA escribe y ejecuta el código.' } },
        { target: '.toolbar', position: 'left',
          title: { ko: '공유 툴바', en: 'Shared Toolbar', ja: '共有ツールバー', 'zh-CN': '共享工具栏', 'zh-TW': '共用工具列', es: 'Barra de herramientas compartida' },
          content: { ko: '언어 선택, <strong>🎓 튜토리얼</strong>, 런처 동기화를 제공하는 <strong>공유 툴바</strong>입니다. 모든 모듈에서 동일하게 동작합니다.', en: 'The <strong>shared toolbar</strong> provides language selection, the <strong>🎓 tutorial</strong>, and launcher sync. It behaves identically across all modules.', ja: '言語選択、<strong>🎓 チュートリアル</strong>、ランチャー同期を提供する<strong>共有ツールバー</strong>です。すべてのモジュールで同じように動作します。', 'zh-CN': '提供语言选择、<strong>🎓 教程</strong>和启动器同步的<strong>共享工具栏</strong>。在所有模块中行为一致。', 'zh-TW': '提供語言選擇、<strong>🎓 教學</strong>和啟動器同步的<strong>共用工具列</strong>。在所有模組中行為一致。', es: 'La <strong>barra de herramientas compartida</strong> ofrece selección de idioma, el <strong>🎓 tutorial</strong> y sincronización con el launcher. Se comporta igual en todos los módulos.' } },
      ]
    },

    { id: 'console', icon: '💬',
      title: { ko: '💬 콘솔 사용', en: '💬 Using the Console', ja: '💬 コンソールの使い方', 'zh-CN': '💬 使用控制台', 'zh-TW': '💬 使用主控台', es: '💬 Uso de la consola' },
      description: { ko: '채팅형 UI, 상태줄, Activity 패널로 앱 빌드 진행 확인', en: 'Build apps with chat-style replies, a status line, and the Activity panel', ja: 'チャット形式UI、ステータス行、Activityパネルでアプリ構築の進捗を確認', 'zh-CN': '通过聊天式回复、状态行和 Activity 面板查看构建进度', 'zh-TW': '透過聊天式回覆、狀態列和 Activity 面板查看建構進度', es: 'Cree apps con respuestas estilo chat, una línea de estado y el panel Activity' },
      prerequisite: 'overview',
      prerequisiteMessage: { ko: '먼저 개요 섹션을 완료하세요.', en: 'Complete the Overview section first.', ja: '先に概要セクションを完了してください。', 'zh-CN': '请先完成概述部分。', 'zh-TW': '請先完成概述部分。', es: 'Complete primero la sección de resumen.' },
      steps: [
        { target: '.console-role-hint', position: 'bottom',
          title: { ko: '메인 빌드 채팅', en: 'Main Build Chat', ja: 'メインビルドチャット', 'zh-CN': '主构建聊天', 'zh-TW': '主建構聊天', es: 'Chat principal de construcción' },
          content: { ko: '가운데 <strong>Agent Console</strong>이 NPU 앱을 만드는 <strong>메인 채팅</strong>입니다. 우하단 <strong>💬 SDK Help</strong>는 SDK 질문용 보조 창입니다.', en: 'The center <strong>Agent Console</strong> is the <strong>main chat</strong> for building NPU apps. The bottom-right <strong>💬 SDK Help</strong> button is for SDK Q&amp;A only.', ja: '中央の<strong>Agent Console</strong>がNPUアプリ構築の<strong>メインチャット</strong>です。右下の<strong>💬 SDK Help</strong>はSDK質問用の補助ウィンドウです。', 'zh-CN': '中间的 <strong>Agent Console</strong> 是构建 NPU 应用的<strong>主聊天</strong>。右下角 <strong>💬 SDK Help</strong> 仅用于 SDK 问答。', 'zh-TW': '中間的 <strong>Agent Console</strong> 是建構 NPU 應用的<strong>主聊天</strong>。右下角 <strong>💬 SDK Help</strong> 僅用於 SDK 問答。', es: 'La <strong>Agent Console</strong> central es el <strong>chat principal</strong> para crear apps NPU. El botón <strong>💬 SDK Help</strong> (abajo a la derecha) es solo para preguntas del SDK.' } },
        { target: '#status-badge', position: 'bottom',
          title: { ko: '상태 배지', en: 'Status Badge', ja: 'ステータスバッジ', 'zh-CN': '状态徽章', 'zh-TW': '狀態徽章', es: 'Indicador de estado' },
          content: { ko: '에이전트 상태 — <strong>준비됨</strong>, <strong>실행 중</strong>, <strong>완료됨</strong>, <strong>실패</strong>. 실행 중에는 새 요청이 잠시 제한됩니다.', en: 'Agent state — <strong>Ready</strong>, <strong>Running</strong>, <strong>Completed</strong>, or <strong>Failed</strong>. New requests are blocked while running.', ja: 'エージェント状態 — <strong>準備完了</strong>、<strong>実行中</strong>、<strong>完了</strong>、<strong>失敗</strong>。実行中は新しいリクエストが一時的に制限されます。', 'zh-CN': '智能体状态 — <strong>就绪</strong>、<strong>运行中</strong>、<strong>已完成</strong>或<strong>失败</strong>。运行时新请求会被阻止。', 'zh-TW': '代理程式狀態 — <strong>就緒</strong>、<strong>執行中</strong>、<strong>已完成</strong>或<strong>失敗</strong>。執行時新請求會被阻擋。', es: 'Estado del agente — <strong>Listo</strong>, <strong>Ejecutando</strong>, <strong>Completado</strong> o <strong>Fallido</strong>. Las nuevas solicitudes se bloquean mientras se ejecuta.' } },
        { target: '#console-status-bar', position: 'bottom',
          title: { ko: '상태줄', en: 'Status Line', ja: 'ステータス行', 'zh-CN': '状态行', 'zh-TW': '狀態列', es: 'Línea de estado' },
          content: { ko: '재연결, 세션 시작, 완료 시간, <code>workspace/agent-sessions/</code> 출력 경로 등 <strong>진행 상태</strong>가 여기 표시됩니다. 채팅 말풍선과 분리됩니다.', en: 'Shows <strong>progress details</strong> — reconnections, session start, finish time, and the <code>workspace/agent-sessions/</code> output path — separate from chat bubbles.', ja: '再接続、セッション開始、完了時間、<code>workspace/agent-sessions/</code> 出力パスなどの<strong>進行状態</strong>がここに表示されます。チャット吹き出しとは分離されています。', 'zh-CN': '显示<strong>进度详情</strong> — 重连、会话开始、完成时间及 <code>workspace/agent-sessions/</code> 输出路径 — 与聊天气泡分开。', 'zh-TW': '顯示<strong>進度詳情</strong> — 重連、工作階段開始、完成時間及 <code>workspace/agent-sessions/</code> 輸出路徑 — 與聊天氣泡分開。', es: 'Muestra <strong>detalles del progreso</strong> — reconexiones, inicio de sesión, tiempo de finalización y la ruta de salida <code>workspace/agent-sessions/</code> — separado de las burbujas del chat.' },
          beforeStep: function () { _ensureConsoleStatusBar(); },
          afterStep: function () {
            // Revert the status bar the tutorial revealed, unless a real session has
            // populated it (in which case it no longer shows our demo placeholder text).
            var bar = document.getElementById('console-status-bar');
            if (!bar) return;
            if (bar.textContent.trim() === 'Session output: workspace/agent-sessions/demo-session/') {
              bar.textContent = '';
              bar.setAttribute('hidden', '');
              bar.style.display = '';
              bar.style.minHeight = '';
            }
          } },
        { target: '#console-output', position: 'top',
          title: { ko: '채팅 출력', en: 'Chat Output', ja: 'チャット出力', 'zh-CN': '聊天输出', 'zh-TW': '聊天輸出', es: 'Salida del chat' },
          content: { ko: '에이전트 답변은 <strong>마크다운 말풍선</strong>으로 스트리밍됩니다. 셸·도구 실행은 아래 <strong>Agent activity</strong> 접이 패널에 모입니다.', en: 'Agent replies <strong>stream as markdown chat bubbles</strong>. Shell and tool runs collect in the collapsible <strong>Agent activity</strong> panel below.', ja: 'エージェントの回答は<strong>Markdownのチャット吹き出し</strong>としてストリーミングされます。シェル・ツール実行は下の<strong>Agent activity</strong>折りたたみパネルに集まります。', 'zh-CN': '智能体回复以<strong>Markdown 聊天气泡</strong>流式显示。Shell 和工具运行汇总在下方可折叠的 <strong>Agent activity</strong> 面板。', 'zh-TW': '代理程式回覆以<strong>Markdown 聊天氣泡</strong>串流顯示。Shell 和工具執行彙總在下方可摺疊的 <strong>Agent activity</strong> 面板。', es: 'Las respuestas del agente se <strong>transmiten como burbujas de chat Markdown</strong>. Las ejecuciones de shell y herramientas se recopilan en el panel plegable <strong>Agent activity</strong> de abajo.' } },
        { target: '#console-input', position: 'top',
          title: { ko: '자연어 입력', en: 'Natural-Language Input', ja: '自然言語入力', 'zh-CN': '自然语言输入', 'zh-TW': '自然語言輸入', es: 'Entrada en lenguaje natural' },
          content: { ko: '만들고 싶은 NPU 앱을 <strong>평범한 문장으로</strong> 설명하세요. 예: "카메라로 객체를 탐지하는 앱 만들어줘".', en: 'Describe the NPU app you want in <strong>plain language</strong>. e.g., "Build an app that detects objects from a camera".', ja: '作りたいNPUアプリを<strong>普通の文章で</strong>説明してください。例：「カメラで物体を検出するアプリを作って」。', 'zh-CN': '用<strong>普通语言</strong>描述您想要的NPU应用。例如：“构建一个从摄像头检测物体的应用”。', 'zh-TW': '用<strong>普通語言</strong>描述您想要的NPU應用。例如：「建構一個從攝影機偵測物體的應用」。', es: 'Describa la app NPU que quiere en <strong>lenguaje sencillo</strong>. Ej.: «Crea una app que detecte objetos con la cámara».' } },
        { target: '#console-send', position: 'left',
          title: { ko: '전송', en: 'Send', ja: '送信', 'zh-CN': '发送', 'zh-TW': '傳送', es: 'Enviar' },
          content: { ko: '입력한 명령을 에이전트에게 보냅니다. <strong>Enter</strong> 키로도 전송할 수 있습니다.', en: 'Sends your command to the agent. You can also press <strong>Enter</strong>.', ja: '入力した指示をエージェントに送信します。<strong>Enter</strong>キーでも送信できます。', 'zh-CN': '将您的指令发送给智能体。也可以按<strong>Enter</strong>键发送。', 'zh-TW': '將您的指令傳送給代理程式。也可以按<strong>Enter</strong>鍵傳送。', es: 'Envíe su comando al agente. También puede pulsar <strong>Enter</strong>.' } },
      ]
    },

    { id: 'controls', icon: '🤖',
      title: { ko: '🤖 에이전트 & 모델', en: '🤖 Agent & Model', ja: '🤖 エージェント & モデル', 'zh-CN': '🤖 智能体与模型', 'zh-TW': '🤖 代理程式與模型', es: '🤖 Agente y modelo' },
      description: { ko: '코딩 에이전트와 모델을 선택', en: 'Select the coding agent and model', ja: 'コーディングエージェントとモデルを選択', 'zh-CN': '选择编码智能体和模型', 'zh-TW': '選擇編碼代理程式和模型', es: 'Selecciona el agente de codificación y el modelo' },
      prerequisite: 'console',
      prerequisiteMessage: { ko: '먼저 콘솔 섹션을 완료하세요.', en: 'Complete the Console section first.', ja: '先にコンソールセクションを完了してください。', 'zh-CN': '请先完成控制台部分。', 'zh-TW': '請先完成主控台部分。', es: 'Complete primero la sección de consola.' },
      steps: [
        { target: '#agent-select', position: 'bottom',
          title: { ko: '에이전트 선택', en: 'Agent Select', ja: 'エージェント選択', 'zh-CN': '智能体选择', 'zh-TW': '代理程式選擇', es: 'Selección de agente' },
          content: { ko: '사용할 코딩 에이전트를 고릅니다 — <strong>Claude, Codex, Copilot, Cursor, OpenCode</strong>. 설치된 에이전트만 활성화됩니다.', en: 'Choose the coding agent to use — <strong>Claude, Codex, Copilot, Cursor, OpenCode</strong>. Only installed agents are enabled.', ja: '使用するコーディングエージェントを選びます — <strong>Claude、Codex、Copilot、Cursor、OpenCode</strong>。インストール済みのエージェントのみ有効になります。', 'zh-CN': '选择要使用的编码智能体 — <strong>Claude、Codex、Copilot、Cursor、OpenCode</strong>。仅启用已安装的智能体。', 'zh-TW': '選擇要使用的編碼代理程式 — <strong>Claude、Codex、Copilot、Cursor、OpenCode</strong>。僅啟用已安裝的代理程式。', es: 'Elija el agente de codificación — <strong>Claude, Codex, Copilot, Cursor, OpenCode</strong>. Solo están activos los agentes instalados.' },
          beforeStep: function () {
            var c = document.getElementById('agent-controls');
            if (c) c.removeAttribute('hidden');
            _scrollTo('#agent-select');
          },
          afterStep: function () {
            // The app (fillAgentControls) hides #agent-controls when no agents exist.
            // Re-apply that state so the tour doesn't leave an empty toolbar visible;
            // if agents are present (#agent-select has options), leave it shown.
            var c = document.getElementById('agent-controls');
            var sel = document.getElementById('agent-select');
            if (c && (!sel || sel.options.length === 0)) c.setAttribute('hidden', '');
          } },
        { target: '#model-select', position: 'bottom',
          title: { ko: '모델 선택', en: 'Model Select', ja: 'モデル選択', 'zh-CN': '模型选择', 'zh-TW': '模型選擇', es: 'Selección de modelo' },
          content: { ko: '선택한 에이전트가 지원하는 <strong>모델</strong>을 고릅니다. 에이전트를 바꾸면 모델 목록이 자동으로 갱신됩니다.', en: 'Pick a <strong>model</strong> supported by the selected agent. The model list refreshes automatically when you change the agent.', ja: '選択したエージェントが対応する<strong>モデル</strong>を選びます。エージェントを変更するとモデルリストが自動的に更新されます。', 'zh-CN': '选择所选智能体支持的<strong>模型</strong>。更换智能体时模型列表会自动刷新。', 'zh-TW': '選擇所選代理程式支援的<strong>模型</strong>。更換代理程式時模型清單會自動重新整理。', es: 'Elija un <strong>modelo</strong> compatible con el agente seleccionado. La lista se actualiza al cambiar de agente.' },
          beforeStep: function () { _scrollTo('#model-select'); } },
        { target: '#mode-select', position: 'bottom',
          title: { ko: '진행 방식', en: 'Interaction', ja: '実行モード', 'zh-CN': '交互方式', 'zh-TW': '互動方式', es: 'Interacción' },
          content: { ko: '대화형(질문하며 진행)과 자동(질문 없이 한 번에 완료) 중 선택합니다.', en: 'Choose Interactive (agent asks questions) or Autopilot (runs to completion without asking).', ja: '対話型（質問しながら進行）と Autopilot（質問せず一気に完了）を選択します。', 'zh-CN': '选择交互式（提问推进）或 Autopilot（无提问一次完成）。', 'zh-TW': '選擇互動式（提問推進）或 Autopilot（無提問一次完成）。', es: 'Elija Interactivo (el agente pregunta) o Autopilot (completa sin preguntar).' },
          beforeStep: function () { _scrollTo('#mode-select'); } },
      ]
    },

    { id: 'showcase', icon: '🖼️',
      title: { ko: '🖼️ 쇼케이스 갤러리', en: '🖼️ Showcase Gallery', ja: '🖼️ ショーケースギャラリー', 'zh-CN': '🖼️ 展示区', 'zh-TW': '🖼️ 展示區', es: '🖼️ Galería de showcases' },
      description: { ko: '양옆 예시 카드에서 Agent Dev 세션 결과물 둘러보기', en: 'Browse example Agent Dev session outputs in the side panels', ja: '左右の例カードでAgent Devセッション成果物を閲覧', 'zh-CN': '在两侧示例卡片中浏览 Agent Dev 会话成果', 'zh-TW': '在兩側範例卡片中瀏覽 Agent Dev 工作階段成果', es: 'Explore resultados de sesiones Agent Dev en los paneles laterales' },
      prerequisite: 'controls',
      prerequisiteMessage: { ko: '먼저 에이전트 & 모델 섹션을 완료하세요.', en: 'Complete the Agent & Model section first.', ja: '先にエージェント & モデルセクションを完了してください。', 'zh-CN': '请先完成智能体与模型部分。', 'zh-TW': '請先完成代理程式與模型部分。', es: 'Complete primero la sección Agente y modelo.' },
      steps: [
        { target: '#examples-left', position: 'right',
          title: { ko: '왼쪽 쇼케이스', en: 'Left Showcase Panel', ja: '左ショーケース', 'zh-CN': '左侧展示区', 'zh-TW': '左側展示區', es: 'Panel showcase izquierdo' },
          content: { ko: '왼쪽 패널에 <strong>Agent Dev 쇼케이스</strong> 카드가 표시됩니다. 카드를 클릭하면 해당 세션의 README·GIF·transcript 등 산출물을 새 탭에서 엽니다.', en: 'The left panel lists <strong>Agent Dev showcase</strong> cards. Click a card to open session README, GIFs, transcripts, and other artifacts in a new tab.', ja: '左パネルに<strong>Agent Devショーケース</strong>カードが表示されます。カードをクリックすると、そのセッションのREADME・GIF・transcriptなどを新しいタブで開きます。', 'zh-CN': '左侧面板显示 <strong>Agent Dev 展示区</strong> 卡片。点击卡片可在新标签页打开该会话的 README、GIF、transcript 等产物。', 'zh-TW': '左側面板顯示 <strong>Agent Dev 展示區</strong> 卡片。點擊卡片可在新分頁開啟該工作階段的 README、GIF、transcript 等產物。', es: 'El panel izquierdo muestra tarjetas de <strong>showcases de Agent Dev</strong>. Haga clic para abrir README, GIFs, transcripts y otros artefactos de la sesión en una pestaña nueva.' } },
        { target: '#examples-right', position: 'left',
          title: { ko: '오른쪽 쇼케이스', en: 'Right Showcase Panel', ja: '右ショーケース', 'zh-CN': '右侧展示区', 'zh-TW': '右側展示區', es: 'Panel showcase derecho' },
          content: { ko: '오른쪽 패널도 동일한 형식입니다. 에이전트 CLI가 없을 때는 가운데 대신 <strong>갤러리 모드</strong>로 전환되어 예시만 탐색할 수 있습니다.', en: 'The right panel uses the same layout. When no agent CLI is installed, the center switches to <strong>gallery mode</strong> so you can browse examples only.', ja: '右パネルも同じ形式です。エージェントCLIがない場合は中央の代わりに<strong>ギャラリーモード</strong>になり、例のみ閲覧できます。', 'zh-CN': '右侧面板格式相同。未安装 agent CLI 时，中间会切换为<strong>画廊模式</strong>，仅可浏览示例。', 'zh-TW': '右側面板格式相同。未安裝 agent CLI 時，中間會切換為<strong>畫廊模式</strong>，僅可瀏覽範例。', es: 'El panel derecho usa el mismo formato. Si no hay CLI de agente instalado, el centro cambia a <strong>modo galería</strong> para explorar solo ejemplos.' } },
        { target: '#showcase-gallery', position: 'top',
          title: { ko: '갤러리 모드', en: 'Gallery Mode', ja: 'ギャラリーモード', 'zh-CN': '画廊模式', 'zh-TW': '畫廊模式', es: 'Modo galería' },
          content: { ko: '에이전트를 사용할 수 없을 때 콘솔 입력 대신 이 영역에 쇼케이스가 표시됩니다. 정상 환경에서는 양옆 패널을 사용하세요.', en: 'When agents are unavailable, showcases appear here instead of the chat form. In a ready environment, use the side panels.', ja: 'エージェントが利用できない場合、チャット入力の代わりにここにショーケースが表示されます。通常は左右パネルを使用してください。', 'zh-CN': '智能体不可用时，此区域显示展示区而非聊天表单。正常环境下请使用两侧面板。', 'zh-TW': '代理程式不可用時，此區域顯示展示區而非聊天表單。正常環境下請使用兩側面板。', es: 'Cuando los agentes no están disponibles, los showcases aparecen aquí en lugar del formulario de chat. En un entorno listo, use los paneles laterales.' },
          beforeStep: function () {
            var g = document.getElementById('showcase-gallery');
            if (!g) return;
            // If the app already rendered the degraded gallery (real no-agent mode), leave it.
            if (!g.hasAttribute('hidden') && g.textContent.trim()) { _scrollTo('#showcase-gallery'); return; }
            // Otherwise mimic gallery mode: hide the chat form and drop in a placeholder note so
            // the spotlight lands on a visibly-sized showcase area. An empty #showcase-gallery is a
            // 0-height sliver wedged under the still-visible chat form, so the spotlight looked wrong.
            var form = document.getElementById('console-form');
            if (form && !form.hasAttribute('hidden')) { form.setAttribute('hidden', ''); g.dataset.dxtTutorialForm = '1'; }
            g.dataset.dxtTutorialMock = '1';
            g.innerHTML = '';
            var note = document.createElement('p');
            note.className = 'gallery-note';
            note.textContent = (typeof T === 'function')
              ? T('The agent is unavailable in this environment. Browse the showcases.')
              : 'The agent is unavailable in this environment. Browse the showcases.';
            g.appendChild(note);
            g.removeAttribute('hidden');
            _scrollTo('#showcase-gallery');
          },
          afterStep: function () {
            // Revert only the gallery/form state this tutorial forced open (tagged above);
            // a real degraded-mode gallery rendered by the app is left untouched.
            var g = document.getElementById('showcase-gallery');
            if (!g || g.dataset.dxtTutorialMock !== '1') return;
            g.innerHTML = '';
            g.setAttribute('hidden', '');
            delete g.dataset.dxtTutorialMock;
            if (g.dataset.dxtTutorialForm === '1') {
              var form = document.getElementById('console-form');
              if (form) form.removeAttribute('hidden');
              delete g.dataset.dxtTutorialForm;
            }
          } },
      ]
    },

    { id: 'activity', icon: '📋',
      title: { ko: '📋 Agent Activity', en: '📋 Agent Activity', ja: '📋 Agent Activity', 'zh-CN': '📋 Agent Activity', 'zh-TW': '📋 Agent Activity', es: '📋 Agent Activity' },
      description: { ko: '도구·셸 실행 로그를 접이 패널에서 확인', en: 'Inspect tool and shell runs in the collapsible activity panel', ja: 'ツール・シェル実行ログを折りたたみパネルで確認', 'zh-CN': '在可折叠 Activity 面板中查看工具与 Shell 运行日志', 'zh-TW': '在可摺疊 Activity 面板中查看工具與 Shell 執行日誌', es: 'Revise ejecuciones de herramientas y shell en el panel plegable Activity' },
      prerequisite: 'console',
      prerequisiteMessage: { ko: '먼저 콘솔 섹션을 완료하세요.', en: 'Complete the Console section first.', ja: '先にコンソールセクションを完了してください。', 'zh-CN': '请先完成控制台部分。', 'zh-TW': '請先完成主控台部分。', es: 'Complete primero la sección de consola.' },
      steps: [
        { target: '#console-output', position: 'top',
          title: { ko: 'Activity 패널 위치', en: 'Where Activity Lives', ja: 'Activityパネルの位置', 'zh-CN': 'Activity 面板位置', 'zh-TW': 'Activity 面板位置', es: 'Ubicación de Activity' },
          content: { ko: '에이전트가 도구나 셸을 실행하면 채팅 말풍선 아래에 <strong>Agent activity</strong> 접이 패널이 생성됩니다. 스트리밍 답변과 실행 로그가 분리됩니다.', en: 'When the agent runs tools or shell commands, a collapsible <strong>Agent activity</strong> panel appears below chat bubbles — keeping streamed replies separate from execution logs.', ja: 'エージェントがツールやシェルを実行すると、チャット吹き出しの下に<strong>Agent activity</strong>折りたたみパネルが生成されます。ストリーミング回答と実行ログが分離されます。', 'zh-CN': '智能体运行工具或 Shell 时，聊天气泡下方会出现可折叠的 <strong>Agent activity</strong> 面板，将流式回复与执行日志分开。', 'zh-TW': '代理程式執行工具或 Shell 時，聊天氣泡下方會出現可摺疊的 <strong>Agent activity</strong> 面板，將串流回覆與執行日誌分開。', es: 'Cuando el agente ejecuta herramientas o shell, aparece un panel plegable <strong>Agent activity</strong> bajo las burbujas de chat, separando respuestas en streaming de los registros de ejecución.' } },
        { target: '#console-status-bar', position: 'bottom',
          title: { ko: '세션 상태 vs Activity', en: 'Status Line vs Activity', ja: 'ステータス行 vs Activity', 'zh-CN': '状态行与 Activity', 'zh-TW': '狀態列與 Activity', es: 'Línea de estado vs Activity' },
          content: { ko: '<strong>상태줄</strong>은 재연결·세션 경로 등 메타 정보를, <strong>Activity</strong>는 명령 stdout/stderr를 표시합니다. 둘 다 채팅 본문과 분리되어 있습니다.', en: 'The <strong>status line</strong> shows meta info (reconnect, session path); <strong>Activity</strong> shows command stdout/stderr. Both stay separate from chat prose.', ja: '<strong>ステータス行</strong>は再接続・セッションパスなどのメタ情報、<strong>Activity</strong>はコマンドのstdout/stderrを表示します。どちらもチャット本文とは分離されています。', 'zh-CN': '<strong>状态行</strong>显示重连、会话路径等元信息；<strong>Activity</strong>显示命令 stdout/stderr。两者均与聊天正文分离。', 'zh-TW': '<strong>狀態列</strong>顯示重連、工作階段路徑等元資訊；<strong>Activity</strong>顯示命令 stdout/stderr。兩者均與聊天正文分離。', es: 'La <strong>línea de estado</strong> muestra metadatos (reconexión, ruta de sesión); <strong>Activity</strong> muestra stdout/stderr de comandos. Ambos permanecen separados del texto del chat.' },
          beforeStep: function () { _ensureConsoleStatusBar(); },
          afterStep: function () {
            var bar = document.getElementById('console-status-bar');
            if (!bar) return;
            if (bar.textContent.trim() === 'Session output: workspace/agent-sessions/demo-session/') {
              bar.textContent = '';
              bar.setAttribute('hidden', '');
              bar.style.display = '';
              bar.style.minHeight = '';
            }
          } },
        { target: '.activity-panel', position: 'top',
          title: { ko: 'Activity 패널', en: 'Activity Panel', ja: 'Activityパネル', 'zh-CN': 'Activity 面板', 'zh-TW': 'Activity 面板', es: 'Panel Activity' },
          content: { ko: '에이전트가 shell·도구를 실행하면 채팅 아래에 <strong>Agent activity</strong> 접이 패널이 생깁니다. 요약 줄을 펼쳐 stdout/stderr 로그를 확인하세요.', en: 'When the agent runs shell or tool commands, a collapsible <strong>Agent activity</strong> panel appears below chat. Expand the summary row to read stdout/stderr logs.', ja: 'エージェントがshell・ツールを実行すると、チャットの下に<strong>Agent activity</strong>折りたたみパネルが現れます。サマリー行を展開してstdout/stderrログを確認します。', 'zh-CN': '智能体运行 shell 或工具时，聊天下方会出现可折叠的 <strong>Agent activity</strong> 面板。展开摘要行查看 stdout/stderr 日志。', 'zh-TW': '代理程式執行 shell 或工具時，聊天下方會出現可摺疊的 <strong>Agent activity</strong> 面板。展開摘要列查看 stdout/stderr 日誌。', es: 'Cuando el agente ejecuta shell o herramientas, aparece un panel plegable <strong>Agent activity</strong> bajo el chat. Expanda la fila de resumen para leer los registros stdout/stderr.' },
          beforeStep: function () {
            var out = document.getElementById('console-output');
            if (!out) return;
            var panel = out.querySelector('.activity-panel');
            if (!panel) {
              var block = document.createElement('div');
              block.className = 'console-turn';
              block.dataset.dxtTutorialMock = '1';  // tag so afterStep removes only OUR fake panel
              panel = document.createElement('details');
              panel.className = 'activity-panel';
              panel.open = true;
              var summary = document.createElement('summary');
              summary.className = 'activity-summary';
              summary.textContent = 'Agent activity (1)';
              panel.appendChild(summary);
              var body = document.createElement('div');
              body.className = 'activity-body';
              body.textContent = '$ dxrt-cli -s\nSanity check PASSED!';
              panel.appendChild(body);
              block.appendChild(panel);
              out.appendChild(block);
            } else {
              panel.removeAttribute('hidden');
              panel.open = true;
            }
          },
          afterStep: function () {
            // Remove the fake activity panel this tutorial injected so it doesn't linger
            // among real chat turns after the tour ends (only ours, tagged above).
            var out = document.getElementById('console-output');
            var mock = out && out.querySelector('.console-turn[data-dxt-tutorial-mock]');
            if (mock) mock.remove();
          } },
      ]
    },

  ];

  var referenceDocs = [
    { id: 'flow', icon: '🛠️', title: { ko: '빌드 흐름', en: 'Build Flow', ja: 'ビルドフロー', 'zh-CN': '构建流程', 'zh-TW': '建構流程', es: 'Flujo de construcción' },
      body: { ko: '<p><strong>자연어 → NPU 앱</strong> 빌드 흐름:</p><ol><li>Agent Console에 만들 앱을 설명합니다.</li><li>선택한 CLI 에이전트가 <code>.deepx</code> 하네스를 읽고 코드를 작성·실행합니다.</li><li>답변은 채팅 말풍선으로, 도구/셸은 <strong>Agent activity</strong> 패널에 표시됩니다.</li><li>생성물은 <code>workspace/agent-sessions/</code>에 저장됩니다. 양옆 <strong>쇼케이스</strong>에서 예시를 볼 수 있습니다.</li></ol>', en: '<p><strong>Natural language → NPU app</strong> build flow:</p><ol><li>Describe the app in the Agent Console.</li><li>The selected CLI agent reads the <code>.deepx</code> harness and writes/runs code.</li><li>Replies appear as chat bubbles; tools/shell output goes to the <strong>Agent activity</strong> panel.</li><li>Outputs are saved under <code>workspace/agent-sessions/</code>. Browse examples in the side <strong>showcases</strong>.</li></ol>', ja: '<p><strong>自然言語 → NPUアプリ</strong>のビルドフロー：</p><ol><li>Agent Consoleで作りたいアプリを説明します。</li><li>選択したCLIエージェントが<code>.deepx</code>ハーネスを読み、コードを記述・実行します。</li><li>回答はチャット吹き出し、ツール/シェルは<strong>Agent activity</strong>パネルに表示されます。</li><li>生成物は<code>workspace/agent-sessions/</code>に保存されます。左右の<strong>ショーケース</strong>で例を確認できます。</li></ol>', 'zh-CN': '<p><strong>自然语言 → NPU应用</strong>构建流程：</p><ol><li>在 Agent Console 描述您想要的应用。</li><li>所选 CLI 智能体读取 <code>.deepx</code> harness 并编写/运行代码。</li><li>回复以聊天气泡显示；工具/Shell 输出进入 <strong>Agent activity</strong> 面板。</li><li>输出保存到 <code>workspace/agent-sessions/</code>。可在两侧<strong>展示区</strong>查看示例。</li></ol>', 'zh-TW': '<p><strong>自然語言 → NPU應用</strong>建構流程：</p><ol><li>在 Agent Console 描述您想要的應用。</li><li>所選 CLI 代理程式讀取 <code>.deepx</code> harness 並編寫/執行程式碼。</li><li>回覆以聊天氣泡顯示；工具/Shell 輸出進入 <strong>Agent activity</strong> 面板。</li><li>輸出儲存至 <code>workspace/agent-sessions/</code>。可在兩側<strong>展示區</strong>查看範例。</li></ol>', es: '<p>Flujo de construcción <strong>lenguaje natural → app NPU</strong>:</p><ol><li>Describa la app en Agent Console.</li><li>El agente CLI seleccionado lee el harness <code>.deepx</code> y escribe/ejecuta código.</li><li>Las respuestas aparecen como burbujas de chat; la salida de herramientas/shell va al panel <strong>Agent activity</strong>.</li><li>La salida se guarda en <code>workspace/agent-sessions/</code>. Explore ejemplos en los <strong>showcases</strong> laterales.</li></ol>' } },
    { id: 'sdk-help', icon: '💬', title: { ko: 'SDK Help (💬)', en: 'SDK Help (💬)', ja: 'SDK Help (💬)', 'zh-CN': 'SDK Help (💬)', 'zh-TW': 'SDK Help (💬)', es: 'SDK Help (💬)' },
      body: { ko: '<p>우하단 <strong>💬 SDK Help</strong>는 Agent Console과 별개입니다. SDK 문서·개념 질문용이며, NPU 앱 <strong>코드 생성</strong>은 가운데 Agent Console에서 하세요.</p>', en: '<p>The bottom-right <strong>💬 SDK Help</strong> is separate from the Agent Console. Use it for SDK documentation and concept questions; <strong>build NPU app code</strong> in the center Agent Console.</p>', ja: '<p>右下の<strong>💬 SDK Help</strong>はAgent Consoleとは別です。SDKドキュメントや概念の質問用で、NPUアプリの<strong>コード生成</strong>は中央のAgent Consoleで行います。</p>', 'zh-CN': '<p>右下角 <strong>💬 SDK Help</strong> 与 Agent Console 分开。用于 SDK 文档和概念问答；<strong>生成 NPU 应用代码</strong>请使用中间 Agent Console。</p>', 'zh-TW': '<p>右下角 <strong>💬 SDK Help</strong> 與 Agent Console 分開。用於 SDK 文件和概念問答；<strong>產生 NPU 應用程式碼</strong>請使用中間 Agent Console。</p>', es: '<p>El <strong>💬 SDK Help</strong> (abajo a la derecha) es independiente de Agent Console. Úselo para documentación y conceptos del SDK; <strong>genere código de apps NPU</strong> en la Agent Console central.</p>' } },
    { id: 'agents', icon: '🤖', title: { ko: '지원 에이전트', en: 'Supported Agents', ja: '対応エージェント', 'zh-CN': '支持的智能体', 'zh-TW': '支援的代理程式', es: 'Agentes compatibles' },
      body: { ko: '<p>여러 코딩 에이전트를 선택할 수 있습니다:</p><ul><li><strong>Claude</strong> · <strong>Codex</strong> · <strong>Copilot</strong> · <strong>Cursor</strong> · <strong>OpenCode</strong></li></ul><p>각 에이전트는 고유한 모델 목록을 가지며, 시스템에 <strong>설치된 에이전트만</strong> 선택할 수 있습니다.</p>', en: '<p>Several coding agents are selectable:</p><ul><li><strong>Claude</strong> · <strong>Codex</strong> · <strong>Copilot</strong> · <strong>Cursor</strong> · <strong>OpenCode</strong></li></ul><p>Each agent has its own model list, and <strong>only installed agents</strong> can be selected.</p>', ja: '<p>複数のコーディングエージェントを選択できます：</p><ul><li><strong>Claude</strong> · <strong>Codex</strong> · <strong>Copilot</strong> · <strong>Cursor</strong> · <strong>OpenCode</strong></li></ul><p>各エージェントは独自のモデルリストを持ち、システムに<strong>インストール済みのエージェントのみ</strong>選択できます。</p>', 'zh-CN': '<p>可选择多种编码智能体：</p><ul><li><strong>Claude</strong> · <strong>Codex</strong> · <strong>Copilot</strong> · <strong>Cursor</strong> · <strong>OpenCode</strong></li></ul><p>每个智能体都有自己的模型列表，且<strong>仅可选择已安装的智能体</strong>。</p>', 'zh-TW': '<p>可選擇多種編碼代理程式：</p><ul><li><strong>Claude</strong> · <strong>Codex</strong> · <strong>Copilot</strong> · <strong>Cursor</strong> · <strong>OpenCode</strong></li></ul><p>每個代理程式都有自己的模型清單，且<strong>僅可選擇已安裝的代理程式</strong>。</p>', es: '<p>Puede elegir entre varios agentes de codificación:</p><ul><li><strong>Claude</strong> · <strong>Codex</strong> · <strong>Copilot</strong> · <strong>Cursor</strong> · <strong>OpenCode</strong></li></ul><p>Cada agente tiene su propia lista de modelos y <strong>solo se pueden seleccionar los instalados</strong>.</p>' } },
    { id: 'mock', icon: '🧪', title: { ko: 'Mock 모드', en: 'Mock Mode', ja: 'モックモード', 'zh-CN': '模拟模式', 'zh-TW': '模擬模式', es: 'Modo simulación' },
      body: { ko: '<p>설치된 실제 CLI가 없을 때는 <strong>Mock 모드</strong>로 동작합니다. 실제 코드 실행 없이 콘솔 흐름(입력 → 스트리밍 → 결과)을 시뮬레이션하여 UI를 안전하게 체험할 수 있습니다.</p>', en: '<p>When no real CLI is installed, the console runs in <strong>Mock mode</strong>. It simulates the flow (input → streaming → result) without executing real code, so you can safely explore the UI.</p>', ja: '<p>実際のCLIがインストールされていない場合は<strong>モックモード</strong>で動作します。実際のコード実行なしにコンソールの流れ（入力 → ストリーミング → 結果）をシミュレートし、UIを安全に体験できます。</p>', 'zh-CN': '<p>当未安装真实CLI时，控制台以<strong>模拟模式</strong>运行。它在不执行真实代码的情况下模拟流程（输入 → 流式传输 → 结果），让您安全地探索UI。</p>', 'zh-TW': '<p>當未安裝真實CLI時，主控台以<strong>模擬模式</strong>運行。它在不執行真實程式碼的情況下模擬流程（輸入 → 串流 → 結果），讓您安全地探索UI。</p>', es: '<p>Cuando no hay un CLI real instalado, la consola funciona en <strong>modo simulación</strong>. Simula el flujo (entrada → streaming → resultado) sin ejecutar código real, para que pueda explorar la UI con seguridad.</p>' } },
  ];

  window.DXTutorial.create({
    appId: 'agent_dev',
    sections: sections,
    referenceDocs: referenceDocs,
    toolbarSelector: '#dxToolbar',
    skipButtons: true,
    getLang: function () {
      return (window.DXI18n && window.DXI18n.lang) || localStorage.getItem('dx-lang') || 'en';
    },
    onNav: function () {},
    onComplete: function (sectionId) {
      var engine = window._dxTutorial;
      var sec = engine.sections.find(function (s) { return s.id === sectionId; });
      if (sec) {
        var msg = '✅ "' + engine._t(sec.title) + '" ' + engine._tl('tutorial complete!');
        if (typeof toast === 'function') toast(msg, 'ok');
        else console.info('[DXTutorial]', msg);
      }
    }
  });

  // Re-run the active step on language change so its dynamically-rendered console/gallery
  // content (written in beforeStep/afterStep) is redrawn in the new language, not just the
  // tooltip text the engine already refreshes.
  if (window.DXI18n && typeof DXI18n.onLangChange === 'function') {
    DXI18n.onLangChange(function () {
      var engine = window._dxTutorial;
      if (engine && engine._curSection && typeof engine._showStep === 'function') {
        engine._showStep();
      }
    });
  }

})();
