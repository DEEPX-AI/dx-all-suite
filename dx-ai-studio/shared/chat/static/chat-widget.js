/**
 * DX Chat Widget — Shared AI Chat UI Component
 * 5개 DX 앱에서 공통으로 사용하는 채팅 위젯.
 *
 * Usage:
 *   <link rel="stylesheet" href="/static/shared/chat-widget.css">
 *   <script src="/static/shared/chat-widget.js"></script>
 *   <script>DXChat.init({ appName: 'dx_app' });</script>
 */

window._DX_CHAT_I18N = window._DX_CHAT_I18N || {
  'AI settings': { ko: 'AI 설정', ja: 'AI設定', es: 'Configuración de IA', 'zh-CN': 'AI 设置', 'zh-TW': 'AI 設定' },
  'Clear chat': { ko: '대화 초기화', ja: 'チャットをクリア', es: 'Borrar chat', 'zh-CN': '清空聊天', 'zh-TW': '清除聊天' },
  'Close': { ko: '닫기', ja: '閉じる', es: 'Cerrar', 'zh-CN': '关闭', 'zh-TW': '關閉' },
  'AI Assistant Settings': { ko: 'AI 어시스턴트 설정', ja: 'AIアシスタント設定', es: 'Configuración del asistente de IA', 'zh-CN': 'AI 助手设置', 'zh-TW': 'AI 助手設定' },
  'Provider': { ko: '제공자', ja: 'プロバイダー', es: 'Proveedor', 'zh-CN': '提供商', 'zh-TW': '提供者' },
  'Local / Self-hosted': { ko: '로컬 / 자체 호스팅', ja: 'ローカル / セルフホスト', es: 'Local / Autohospedado', 'zh-CN': '本地 / 自托管', 'zh-TW': '本機 / 自架' },
  'Coding agent (CLI login)': { ko: '코딩 에이전트 (CLI 로그인)', ja: 'コーディングエージェント (CLIログイン)', es: 'Agente de codificación (inicio CLI)', 'zh-CN': '编码智能体 (CLI 登录)', 'zh-TW': '編碼智能體 (CLI 登入)' },
  'Temperature': { ko: '온도', ja: '温度', es: 'Temperatura', 'zh-CN': '温度', 'zh-TW': '溫度' },
  'Test': { ko: '테스트', ja: 'テスト', es: 'Probar', 'zh-CN': '测试', 'zh-TW': '測試' },
  'Re-sync SDK knowledge from .deepx': { ko: '.deepx에서 SDK 지식 재동기화', ja: '.deepxからSDK知識を再同期', es: 'Resincronizar conocimiento SDK desde .deepx', 'zh-CN': '从 .deepx 重新同步 SDK 知识', 'zh-TW': '從 .deepx 重新同步 SDK 知識' },
  'Refresh knowledge': { ko: '지식 새로고침', ja: '知識を更新', es: 'Actualizar conocimiento', 'zh-CN': '刷新知识', 'zh-TW': '重新整理知識' },
  'Save': { ko: '저장', ja: '保存', es: 'Guardar', 'zh-CN': '保存', 'zh-TW': '儲存' },
  'Ask a question...': { ko: '질문을 입력하세요...', ja: '質問を入力...', es: 'Escriba su pregunta...', 'zh-CN': '输入您的问题...', 'zh-TW': '輸入您的問題...' },
  'Custom…': { ko: '직접 입력…', ja: 'カスタム…', es: 'Personalizado…', 'zh-CN': '自定义…', 'zh-TW': '自訂…' },
  '(No response)': { ko: '(응답 없음)', ja: '(応答なし)', es: '(Sin respuesta)', 'zh-CN': '(无响应)', 'zh-TW': '(無回應)' },
  'Connection error: Unable to reach server.': { ko: '연결 오류: 서버에 연결할 수 없습니다.', ja: '接続エラー: サーバーに接続できません。', es: 'Error de conexión: no se puede acceder al servidor.', 'zh-CN': '连接错误：无法访问服务器。', 'zh-TW': '連線錯誤：無法連線至伺服器。' },
  'Unable to load settings.': { ko: '설정을 불러올 수 없습니다.', ja: '設定を読み込めません。', es: 'No se pudieron cargar los ajustes.', 'zh-CN': '无法加载设置。', 'zh-TW': '無法載入設定。' },
  'Uses your logged-in coding-agent CLI — pick the agent below.': { ko: '로그인된 코딩 에이전트 CLI를 사용합니다 — 아래에서 에이전트를 선택하세요.', ja: 'ログイン済みコーディングエージェントCLIを使用します — 下でエージェントを選択してください。', es: 'Usa su CLI de agente de codificación con sesión iniciada — elija el agente abajo.', 'zh-CN': '使用已登录的编码智能体 CLI — 请在下方选择智能体。', 'zh-TW': '使用已登入的編碼智能體 CLI — 請在下方選擇智能體。' },
  'Found models: ': { ko: '발견된 모델: ', ja: '検出されたモデル: ', es: 'Modelos encontrados: ', 'zh-CN': '发现的模型：', 'zh-TW': '發現的模型：' },
  'No local runtime detected. Start one (e.g. `ollama pull deepseek-r1`) then retry.': { ko: '로컬 런타임이 감지되지 않았습니다. 먼저 실행하세요 (예: `ollama pull deepseek-r1`) 후 재시도.', ja: 'ローカルランタイムが検出されません。起動してから再試行してください (例: `ollama pull deepseek-r1`)。', es: 'No se detectó un runtime local. Inícielo (p. ej. `ollama pull deepseek-r1`) y vuelva a intentarlo.', 'zh-CN': '未检测到本地运行时。请先启动（例如 `ollama pull deepseek-r1`）后重试。', 'zh-TW': '未偵測到本機執行環境。請先啟動（例如 `ollama pull deepseek-r1`）後重試。' },
  'Please enter an API key.': { ko: 'API 키를 입력해주세요.', ja: 'APIキーを入力してください。', es: 'Introduzca una clave API.', 'zh-CN': '请输入 API 密钥。', 'zh-TW': '請輸入 API 金鑰。' },
  'Please enter a model.': { ko: '모델을 입력해주세요.', ja: 'モデルを入力してください。', es: 'Introduzca un modelo.', 'zh-CN': '请输入模型。', 'zh-TW': '請輸入模型。' },
  'Saving...': { ko: '저장 중...', ja: '保存中...', es: 'Guardando...', 'zh-CN': '保存中...', 'zh-TW': '儲存中...' },
  'Saved.': { ko: '저장 완료.', ja: '保存しました。', es: 'Guardado.', 'zh-CN': '已保存。', 'zh-TW': '已儲存。' },
  'Connection failed.': { ko: '연결 실패.', ja: '接続に失敗しました。', es: 'Conexión fallida.', 'zh-CN': '连接失败。', 'zh-TW': '連線失敗。' },
  'Re-syncing SDK knowledge...': { ko: 'SDK 지식 재동기화 중...', ja: 'SDK知識を再同期中...', es: 'Resincronizando conocimiento SDK...', 'zh-CN': '正在重新同步 SDK 知识...', 'zh-TW': '正在重新同步 SDK 知識...' },
  'Knowledge updated (': { ko: '지식 갱신됨 (', ja: '知識を更新しました (', es: 'Conocimiento actualizado (', 'zh-CN': '知识已更新（', 'zh-TW': '知識已更新（' },
  ' sources).': { ko: '개 소스).', ja: ' ソース).', es: ' fuentes).', 'zh-CN': ' 个来源）。', 'zh-TW': ' 個來源）。' },
  'Refresh failed.': { ko: '새로고침 실패.', ja: '更新に失敗しました。', es: 'Error al actualizar.', 'zh-CN': '刷新失败。', 'zh-TW': '重新整理失敗。' },
  'Testing...': { ko: '테스트 중...', ja: 'テスト中...', es: 'Probando...', 'zh-CN': '测试中...', 'zh-TW': '測試中...' },
  'Connected: ': { ko: '연결 성공: ', ja: '接続成功: ', es: 'Conectado: ', 'zh-CN': '已连接：', 'zh-TW': '已連線：' },
  'Open DEEPX Agent on the web': { ko: '웹에서 DEEPX Agent 열기', ja: 'Web で DEEPX Agent を開く', es: 'Abrir DEEPX Agent en la web', 'zh-CN': '在网页中打开 DEEPX Agent', 'zh-TW': '在網頁中開啟 DEEPX Agent' },
  'Chat': { ko: '채팅', ja: 'チャット', es: 'Chat', 'zh-CN': '聊天', 'zh-TW': '聊天' },
  'Send': { ko: '보내기', ja: '送信', es: 'Enviar', 'zh-CN': '发送', 'zh-TW': '傳送' },
  'API Key': { ko: 'API 키', ja: 'API キー', es: 'Clave de API', 'zh-CN': 'API 密钥', 'zh-TW': 'API 金鑰' },
  'Model': { ko: '모델', ja: 'モデル', es: 'Modelo', 'zh-CN': '模型', 'zh-TW': '模型' },
  'Endpoint': { ko: '엔드포인트', ja: 'エンドポイント', es: 'Endpoint', 'zh-CN': '端点', 'zh-TW': '端點' },
  'Custom endpoint': { ko: '직접 지정한 엔드포인트', ja: 'カスタムエンドポイント', es: 'Endpoint personalizado', 'zh-CN': '自定义端点', 'zh-TW': '自訂端點' },
  'Answering with your {agent} login': { ko: '{agent} 계정으로 답합니다', ja: '{agent} のログインで回答します', es: 'Responde con su sesión de {agent}', 'zh-CN': '使用您的 {agent} 登录回答', 'zh-TW': '使用您的 {agent} 登入回答' },
  'Basic guidance only': { ko: '기본 안내만 할 수 있습니다', ja: '基本ガイドのみ', es: 'Solo guía básica', 'zh-CN': '仅基本指南', 'zh-TW': '僅基本指南' },
  'Change': { ko: '변경', ja: '変更', es: 'Cambiar', 'zh-CN': '更改', 'zh-TW': '變更' },
  'Connect AI': { ko: 'AI 연결', ja: 'AI を接続', es: 'Conectar IA', 'zh-CN': '连接 AI', 'zh-TW': '連接 AI' },
  'Which AI should answer?': { ko: '어떤 AI 로 답할까요?', ja: 'どの AI で回答しますか?', es: '¿Qué IA debe responder?', 'zh-CN': '由哪个 AI 回答?', 'zh-TW': '由哪個 AI 回答?' },
  'Coding agent on this PC': { ko: '이 PC 의 coding agent', ja: 'この PC のコーディングエージェント', es: 'Agente de codificación de este PC', 'zh-CN': '本机的编码智能体', 'zh-TW': '本機的編碼智能體' },
  'No API key — uses your CLI login. Recommended': { ko: 'API key 불필요 — CLI 로그인을 씁니다. 추천', ja: 'API key 不要 — CLI のログインを使用。おすすめ', es: 'Sin API key: usa su sesión de la CLI. Recomendado', 'zh-CN': '无需 API key — 使用 CLI 登录。推荐', 'zh-TW': '無需 API key — 使用 CLI 登入。推薦' },
  'My local LLM server': { ko: '내 local LLM server', ja: '自分のローカル LLM サーバー', es: 'Mi servidor LLM local', 'zh-CN': '我的本地 LLM 服务器', 'zh-TW': '我的本機 LLM 伺服器' },
  'Ollama, LM Studio, llama.cpp …': { ko: 'Ollama, LM Studio, llama.cpp …', ja: 'Ollama, LM Studio, llama.cpp …', es: 'Ollama, LM Studio, llama.cpp …', 'zh-CN': 'Ollama, LM Studio, llama.cpp …', 'zh-TW': 'Ollama, LM Studio, llama.cpp …' },
  'Cloud API key': { ko: 'cloud API key', ja: 'クラウド API key', es: 'API key en la nube', 'zh-CN': '云 API key', 'zh-TW': '雲端 API key' },
  'OpenAI, Anthropic, Google, GitHub Models …': { ko: 'OpenAI, Anthropic, Google, GitHub Models …', ja: 'OpenAI, Anthropic, Google, GitHub Models …', es: 'OpenAI, Anthropic, Google, GitHub Models …', 'zh-CN': 'OpenAI, Anthropic, Google, GitHub Models …', 'zh-TW': 'OpenAI, Anthropic, Google, GitHub Models …' },
  'Agent': { ko: '에이전트', ja: 'エージェント', es: 'Agente', 'zh-CN': '智能体', 'zh-TW': '代理程式' },
  'signed in': { ko: '로그인됨', ja: 'ログイン済み', es: 'sesión iniciada', 'zh-CN': '已登录', 'zh-TW': '已登入' },
  'sign in: {cmd}': { ko: '로그인 필요: {cmd}', ja: 'ログインが必要: {cmd}', es: 'inicie sesión: {cmd}', 'zh-CN': '需要登录: {cmd}', 'zh-TW': '需要登入: {cmd}' },
  'Advanced': { ko: '고급', ja: '詳細', es: 'Avanzado', 'zh-CN': '高级', 'zh-TW': '進階' },
  'Checking the connection…': { ko: '연결을 확인하는 중…', ja: '接続を確認しています…', es: 'Comprobando la conexión…', 'zh-CN': '正在检查连接…', 'zh-TW': '正在檢查連線…' },
  'Save anyway': { ko: '그래도 저장', ja: 'それでも保存', es: 'Guardar de todos modos', 'zh-CN': '仍然保存', 'zh-TW': '仍然儲存' },
  'Back to automatic': { ko: '자동으로 되돌리기', ja: '自動に戻す', es: 'Volver a automático', 'zh-CN': '恢复自动', 'zh-TW': '恢復自動' },
  'Saved without a test.': { ko: '테스트 없이 저장했습니다.', ja: 'テストせずに保存しました。', es: 'Guardado sin prueba.', 'zh-CN': '已保存（未测试）。', 'zh-TW': '已儲存（未測試）。' },
  'Leave blank to keep the saved key': { ko: '비워 두면 저장된 key 를 씁니다', ja: '空欄なら保存済みの key を使います', es: 'Déjelo vacío para conservar la key guardada', 'zh-CN': '留空则使用已保存的 key', 'zh-TW': '留空則使用已儲存的 key' },
  'DX Assistant': { ko: 'DX 어시스턴트', ja: 'DXアシスタント', es: 'Asistente DX', 'zh-CN': 'DX 助手', 'zh-TW': 'DX 助手' },
};

/** Per-module chat panel titles (6 languages). Keyed by DXChat.init appName. */
window._DX_CHAT_HEADER_TITLES = window._DX_CHAT_HEADER_TITLES || {
  launcher: {
    en: 'DX AI Studio Help',
    ko: 'DX AI Studio 도움말',
    ja: 'DX AI Studioヘルプ',
    es: 'Ayuda DX AI Studio',
    'zh-CN': 'DX AI Studio 帮助',
    'zh-TW': 'DX AI Studio 說明',
  },
  dx_app: {
    en: 'DX App Help',
    ko: 'DX App 도움말',
    ja: 'DX Appヘルプ',
    es: 'Ayuda DX App',
    'zh-CN': 'DX App 帮助',
    'zh-TW': 'DX App 說明',
  },
  dx_stream: {
    en: 'DX Stream Help',
    ko: 'DX Stream 도움말',
    ja: 'DX Streamヘルプ',
    es: 'Ayuda DX Stream',
    'zh-CN': 'DX Stream 帮助',
    'zh-TW': 'DX Stream 說明',
  },
  dx_compiler: {
    en: 'DX Compiler Help',
    ko: 'DX Compiler 도움말',
    ja: 'DX Compilerヘルプ',
    es: 'Ayuda DX Compiler',
    'zh-CN': 'DX Compiler 帮助',
    'zh-TW': 'DX Compiler 說明',
  },
  dx_planner: {
    en: 'DX EdgeGuide Help',
    ko: 'DX EdgeGuide 도움말',
    ja: 'DX EdgeGuideヘルプ',
    es: 'Ayuda DX EdgeGuide',
    'zh-CN': 'DX EdgeGuide 帮助',
    'zh-TW': 'DX EdgeGuide 說明',
  },
  dx_benchmark: {
    en: 'DX Benchmark Help',
    ko: 'DX Benchmark 도움말',
    ja: 'DX Benchmarkヘルプ',
    es: 'Ayuda DX Benchmark',
    'zh-CN': 'DX Benchmark 帮助',
    'zh-TW': 'DX Benchmark 說明',
  },
  dx_monitor: {
    en: 'DX Monitor Help',
    ko: 'DX Monitor 도움말',
    ja: 'DX Monitorヘルプ',
    es: 'Ayuda DX Monitor',
    'zh-CN': 'DX Monitor 帮助',
    'zh-TW': 'DX Monitor 說明',
  },
  dx_modelzoo: {
    en: 'DX Model Zoo Help',
    ko: 'DX Model Zoo 도움말',
    ja: 'DX Model Zooヘルプ',
    es: 'Ayuda DX Model Zoo',
    'zh-CN': 'DX Model Zoo 帮助',
    'zh-TW': 'DX Model Zoo 說明',
  },
  dx_agent_dev: {
    en: 'Agent Dev Help',
    ko: 'Agent Dev 도움말',
    ja: 'Agent Devヘルプ',
    es: 'Ayuda Agent Dev',
    'zh-CN': 'Agent Dev 帮助',
    'zh-TW': 'Agent Dev 說明',
  },
  sdk_library: {
    en: 'SDK Library Help',
    ko: 'SDK Library 도움말',
    ja: 'SDK Libraryヘルプ',
    es: 'Ayuda SDK Library',
    'zh-CN': 'SDK Library 帮助',
    'zh-TW': 'SDK Library 說明',
  },
};

const DXChat = (() => {

  let _open = false;
  let _sending = false;
  let _pendingContext = null;
  let _history = [];
  let _appName = '';
  let _status = null;      // the last GET /api/chat/config — what is saved, who answers now, the CLIs here
  let _els = {};
  let _headerTitle = null;

  function _chatLang() {
    return (typeof DXI18n !== 'undefined' && DXI18n.lang)
      || (typeof localStorage !== 'undefined' && localStorage.getItem('dx-lang'))
      || 'en';
  }

  /* 공용 아이콘 (shared/static/dx-icon.js). 없으면 빈 자리 — 챗이 아이콘 때문에 멈추지 않게. */
  function _ico(name) {
    return (window.DXIcon && typeof window.DXIcon === 'function') ? window.DXIcon(name) : '';
  }

  function _t(en, ko) {
    const dict = window._DX_CHAT_I18N || {};
    const entry = dict[en];
    if (entry) {
      const lang = _chatLang();
      return entry[lang] || entry.en || en;
    }
    if (typeof T === 'function') return T(en, ko);
    const lang = _chatLang();
    if (lang === 'ko' && ko) return ko;
    return en;
  }


  function init(opts) {
    /* 다시 부르면 (SDK Library 가 그렇다) 대상 앱 · 제목만 바꾼다 — 예전에는 위젯을 하나 더 만들어 같은 자리에
       채팅 버튼이 두 개 겹쳤다 (2026-10-02 release audit). */
    if (_els.fab && document.body.contains(_els.fab)) {
      _appName = (opts && opts.appName) || _appName;
      _headerTitle = (opts && opts.headerTitle)
        || (window._DX_CHAT_HEADER_TITLES && window._DX_CHAT_HEADER_TITLES[_appName])
        || _headerTitle;
      var titleEl = _els.win && _els.win.querySelector('.dx-chat-header-title');
      if (titleEl && _headerTitle) {
        var lang = (typeof DXI18n !== 'undefined') ? DXI18n.lang : 'en';
        titleEl.textContent = _headerTitle[lang] || _headerTitle.en || titleEl.textContent;
      }
      return;
    }
    _appName = (opts && opts.appName) || 'dx_app';
    _headerTitle = (opts && opts.headerTitle)
      || (window._DX_CHAT_HEADER_TITLES && window._DX_CHAT_HEADER_TITLES[_appName])
      || null;
    if (!_headerTitle) {
      _headerTitle = window._DX_CHAT_I18N && window._DX_CHAT_I18N['DX Assistant']
        ? Object.assign({ en: 'DX Assistant' }, window._DX_CHAT_I18N['DX Assistant'])
        : { en: 'DX Assistant', ko: 'DX 어시스턴트' };
    }
    _loadHistory();
    _buildDOM();
    _checkConfig();
  }


  /* 글자 · 이름은 key 로 달아 두고 언어가 바뀌면 다시 번역한다 (release audit L-14: 'API Key' · 'Model' ·
     'Endpoint' · 'Custom endpoint' 는 영어 고정이었고, 다른 글자는 처음 그린 언어에 머물렀다).
     data-chat-t → 글자, data-chat-tip → title + aria-label, data-chat-title → title, data-chat-ph → placeholder. */
  function _relabel() {
    var win = _els.win;
    if (!win) return;
    win.querySelectorAll('[data-chat-t]').forEach(function (el) { el.textContent = _t(el.dataset.chatT); });
    win.querySelectorAll('[data-chat-tip]').forEach(function (el) {
      el.title = _t(el.dataset.chatTip);
      el.setAttribute('aria-label', el.title);
    });
    win.querySelectorAll('[data-chat-title]').forEach(function (el) { el.title = _t(el.dataset.chatTitle); });
    win.querySelectorAll('[data-chat-ph]').forEach(function (el) {
      el.placeholder = _t(el.dataset.chatPh);
      el.setAttribute('aria-label', el.placeholder);   // a placeholder is not a name (2026-10-11 a11y)
    });
    if (_els.fab) _els.fab.setAttribute('aria-label', _open ? _t('Close', '닫기') : _t('Chat'));
    if (_headerTitle) {
      var titleEl = win.querySelector('.dx-chat-header-title');
      if (titleEl) titleEl.textContent = _headerTitle[_chatLang()] || _headerTitle.en || titleEl.textContent;
    }
  }


  function _buildDOM() {
    const fab = document.createElement('button');
    fab.className = 'dx-chat-fab';
    fab.setAttribute('aria-label', _t('Chat'));
    fab.innerHTML = _ico('chat');
    fab.addEventListener('click', toggle);
    document.body.appendChild(fab);
    _els.fab = fab;

    const win = document.createElement('div');
    win.className = 'dx-chat-window';
    win.innerHTML = [
      '<div class="dx-chat-header">',
      '  <span class="dx-chat-header-title">' + _t('DX Assistant') + '</span>',
      '  <div class="dx-chat-header-actions">',
      /* 웹 챗봇 (DEEPX Agent) 은 launcher 막대에 따로 있던 링크였다. 같은 "물어보기" 이므로
         챗 안에서 연다 — 모든 모듈의 챗에 생긴다 (spec 2026-09-23 §5.7). */
      '    <a class="dx-chat-header-link" href="https://deepx.rapidflare.ai/" target="_blank" rel="noopener noreferrer" data-chat-tip="Open DEEPX Agent on the web">DEEPX Agent <span aria-hidden="true">↗</span></a>',
      '    <button class="dx-chat-header-btn" data-action="settings" data-chat-tip="AI settings">' + _ico('gear') + '</button>',
      '    <button class="dx-chat-header-btn" data-action="clear" data-chat-tip="Clear chat">' + _ico('trash') + '</button>',
      '    <button class="dx-chat-header-btn" data-action="close" data-chat-tip="Close">' + _ico('x') + '</button>',
      '  </div>',
      '</div>',
      '<div class="dx-chat-source" aria-live="polite"></div>',
      '<div class="dx-chat-settings-panel" hidden>',
      '  <form class="dx-chat-settings-form">',
      '    <div class="dx-chat-settings-title" data-chat-t="AI Assistant Settings"></div>',
      /* 질문 하나 — 어떤 AI 로 답할까 (spec 2026-10-11 chat settings §3.4). provider select 는 cloud 일 때만 보이고,
         agent · local 은 radio 가 그 값을 정한다. */
      '    <fieldset class="dx-chat-settings-kind">',
      '      <legend data-chat-t="Which AI should answer?"></legend>',
      '      <label class="dx-chat-kind-card"><input type="radio" name="dx-chat-kind" value="agent">',
      '        <span><b data-chat-t="Coding agent on this PC"></b><small data-chat-t="No API key — uses your CLI login. Recommended"></small></span></label>',
      '      <label class="dx-chat-kind-card"><input type="radio" name="dx-chat-kind" value="local">',
      '        <span><b data-chat-t="My local LLM server"></b><small data-chat-t="Ollama, LM Studio, llama.cpp …"></small></span></label>',
      '      <label class="dx-chat-kind-card"><input type="radio" name="dx-chat-kind" value="cloud">',
      '        <span><b data-chat-t="Cloud API key"></b><small data-chat-t="OpenAI, Anthropic, Google, GitHub Models …"></small></span></label>',
      '    </fieldset>',
      '    <label class="dx-chat-settings-field dx-chat-field-agent">',
      '      <span data-chat-t="Agent"></span>',
      '      <select class="dx-chat-settings-agent"></select>',
      '    </label>',
      '    <label class="dx-chat-settings-field dx-chat-field-provider">',
      '      <span data-chat-t="Provider"></span>',
      '      <select class="dx-chat-settings-provider">',
      '        <option value="openai">OpenAI</option>',
      '        <option value="anthropic">Anthropic</option>',
      '        <option value="google">Google</option>',
      '        <option value="github">GitHub Models</option>',
      '        <option value="custom" data-chat-t="Custom endpoint"></option>',
      '        <option value="local" hidden data-chat-t="Local / Self-hosted"></option>',
      '        <option value="agent-cli" hidden data-chat-t="Coding agent (CLI login)"></option>',
      '      </select>',
      '    </label>',
      '    <label class="dx-chat-settings-field">',
      '      <span data-chat-t="API Key"></span>',
      '      <input class="dx-chat-settings-api-key" type="password" autocomplete="off" placeholder="sk-...">',
      '    </label>',
      '    <label class="dx-chat-settings-field dx-chat-field-model">',
      '      <span data-chat-t="Model"></span>',
      '      <select class="dx-chat-settings-model-select" hidden></select>',
      '      <select class="dx-chat-settings-agentmodel-select" data-chat-tip="Model" hidden></select>',
      '      <input class="dx-chat-settings-model" type="text" data-chat-tip="Model" placeholder="gpt-4o-mini" autocomplete="off" hidden>',
      '    </label>',
      '    <label class="dx-chat-settings-field dx-chat-settings-endpoint-field" hidden>',
      '      <span data-chat-t="Endpoint"></span>',
      '      <input class="dx-chat-settings-endpoint" type="url" placeholder="https://api.example.com/v1/chat/completions">',
      '    </label>',
      '    <details class="dx-chat-settings-advanced">',
      '      <summary data-chat-t="Advanced"></summary>',
      '      <label class="dx-chat-settings-field">',
      '        <span><span data-chat-t="Temperature"></span> <strong class="dx-chat-settings-temp-value">0.7</strong></span>',
      '        <input class="dx-chat-settings-temp" type="range" min="0" max="2" step="0.1" value="0.7">',
      '      </label>',
      '      <button type="button" class="dx-chat-settings-refresh-kb" data-chat-title="Re-sync SDK knowledge from .deepx" data-chat-t="Refresh knowledge"></button>',
      '    </details>',
      '    <div class="dx-chat-settings-actions">',
      '      <button type="submit" class="dx-chat-settings-save" data-chat-t="Save"></button>',
      '      <button type="button" class="dx-chat-settings-close" data-action="settings-close" data-chat-t="Close"></button>',
      '      <button type="button" class="dx-chat-settings-reset" hidden data-chat-t="Back to automatic"></button>',
      '    </div>',
      '    <div class="dx-chat-settings-status" aria-live="polite"></div>',
      '    <button type="button" class="dx-chat-settings-force" hidden data-chat-t="Save anyway"></button>',
      '  </form>',
      '</div>',
      '<div class="dx-chat-messages"></div>',
      '<div class="dx-chat-suggestions"></div>',
      '<div class="dx-chat-input-area">',
      '  <textarea class="dx-chat-input" data-chat-ph="Ask a question..." rows="1"></textarea>',
      '  <button class="dx-chat-send-btn" data-chat-tip="Send">' + _ico('send') + '</button>',
      '</div>',
    ].join('\n');
    document.body.appendChild(win);
    _els.win = win;
    _relabel();
    _els.source = win.querySelector('.dx-chat-source');
    _els.agentSelect = win.querySelector('.dx-chat-settings-agent');
    _els.fieldAgent = win.querySelector('.dx-chat-field-agent');
    _els.fieldProvider = win.querySelector('.dx-chat-field-provider');
    _els.forceBtn = win.querySelector('.dx-chat-settings-force');
    _els.resetBtn = win.querySelector('.dx-chat-settings-reset');
    _els.settingsPanel = win.querySelector('.dx-chat-settings-panel');
    _els.settingsForm = win.querySelector('.dx-chat-settings-form');
    _els.settingsProvider = win.querySelector('.dx-chat-settings-provider');
    _els.settingsApiKey = win.querySelector('.dx-chat-settings-api-key');
    _els.settingsModel = win.querySelector('.dx-chat-settings-model');
    _els.settingsModelSelect = win.querySelector('.dx-chat-settings-model-select');
    _els.agentModelSelect = win.querySelector('.dx-chat-settings-agentmodel-select');
    _els.settingsEndpoint = win.querySelector('.dx-chat-settings-endpoint');
    _els.settingsEndpointField = win.querySelector('.dx-chat-settings-endpoint-field');
    _els.settingsTemp = win.querySelector('.dx-chat-settings-temp');
    _els.settingsTempVal = win.querySelector('.dx-chat-settings-temp-value');
    _els.settingsStatus = win.querySelector('.dx-chat-settings-status');
    _els.settingsRefreshKb = win.querySelector('.dx-chat-settings-refresh-kb');
    _els.messages = win.querySelector('.dx-chat-messages');
    _els.suggestions = win.querySelector('.dx-chat-suggestions');
    _els.input = win.querySelector('.dx-chat-input');
    _els.sendBtn = win.querySelector('.dx-chat-send-btn');

    if (_headerTitle) {
      const titleEl = win.querySelector('.dx-chat-header-title');
      if (titleEl) {
        const lang = (typeof DXI18n !== 'undefined') ? DXI18n.lang : 'en';
        titleEl.textContent = _headerTitle[lang] || _headerTitle.en || titleEl.textContent;
      }
    }

    _els.sendBtn.addEventListener('click', () => _send());
    _els.input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        _send();
      }
    });
    _els.input.addEventListener('input', _autoResize);
    /* Escape: 설정 → 창 순서로 닫는다. capture 라 launcher 의 Escape (모듈 닫기) 보다 먼저, 처리했으면 표시
       (release audit X-1 — 채팅에서 Escape 를 누르면 모듈을 떠나고 답이 끊겼다). */
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape' || e.defaultPrevented) return;
      if (_els.settingsPanel && _els.settingsPanel.classList.contains('open')) {
        _closeSettingsPanel();
        e.preventDefault();
      } else if (_open) {
        toggle();
        _els.fab.focus();
        e.preventDefault();
      }
    }, true);

    win.querySelector('[data-action="close"]').addEventListener('click', toggle);
    win.querySelector('[data-action="clear"]').addEventListener('click', _clearHistory);
    win.querySelector('[data-action="settings"]').addEventListener('click', _openSettingsPanel);
    win.querySelector('[data-action="settings-close"]').addEventListener('click', _closeSettingsPanel);
    _els.settingsForm.addEventListener('submit', _saveSettings);
    win.querySelectorAll('input[name=dx-chat-kind]').forEach(function (r) {
      r.addEventListener('change', function () { _setKind(r.value); });
    });
    _els.agentSelect.addEventListener('change', function () { _updateModelChooser('agent-cli'); });
    _els.resetBtn.addEventListener('click', _resetToAuto);
    if (_els.settingsRefreshKb) _els.settingsRefreshKb.addEventListener('click', _refreshKnowledge);
    _els.settingsProvider.addEventListener('change', () => {
      if (_els.settingsModel) _els.settingsModel.value = '';  // clear stale model on provider switch
      _toggleSettingsEndpoint();
      _setApiKeyPlaceholder();
    });
    if (_els.settingsModelSelect) _els.settingsModelSelect.addEventListener('change', _onModelSelectChange);
    // Local: 적은 endpoint 의 model 을 찾는다 — 예전에는 provider 를 바꿀 때만, 그때의 (빈) endpoint 로 찾아
    // LM Studio · llama.cpp · 다른 host 의 Ollama 는 끝내 model 이 안 나왔다 (2026-10-11 실사용 감사).
    if (_els.settingsEndpoint) {
      var _endpointTimer = null;
      var _lookupLocal = function () {
        clearTimeout(_endpointTimer);
        _endpointTimer = null;
        if (_els.settingsProvider.value === 'local') _updateModelChooser('local');
      };
      _els.settingsEndpoint.addEventListener('change', _lookupLocal);
      _els.settingsEndpoint.addEventListener('input', function () {
        clearTimeout(_endpointTimer);
        _endpointTimer = setTimeout(_lookupLocal, 600);
      });
    }
    _els.settingsTemp.addEventListener('input', () => {
      _els.settingsTempVal.textContent = _els.settingsTemp.value;
    });

    if (typeof DXI18n !== 'undefined') {
      DXI18n.onLangChange(function() {
        _relabel();
        _renderSource();
      });
    }

    _history.forEach(m => _renderMessage(m.role, m.content, false));
    _scrollBottom();
  }


  function toggle() {
    _open = !_open;
    _els.win.classList.toggle('open', _open);
    _els.fab.classList.toggle('open', _open);
    /* 열리면 닫기 표시로 바뀐다 — 예전에는 말풍선 이모지를 45° 돌렸는데, 아이콘을 돌리면 기울어진 말풍선일 뿐이다. */
    _els.fab.innerHTML = _ico(_open ? 'x' : 'chat');
    _els.fab.setAttribute('aria-label', _open ? _t('Close', '닫기') : _t('Chat'));
    if (_open) {
      _els.input.focus();
      _scrollBottom();
    }
  }


  function _send() {
    const text = _els.input.value.trim();
    if (!text || _sending) return;

    _sending = true;
    _els.sendBtn.disabled = true;
    _els.suggestions.style.display = 'none';

    _history.push({ role: 'user', content: text });
    _renderMessage('user', text, false);
    _els.input.value = '';
    _autoResize();

    const aiEl = _renderMessage('ai', '', true);

    _streamChat(text, aiEl).finally(() => {
      _sending = false;
      _els.sendBtn.disabled = false;
      _saveHistory();
    });
  }

  // Detect launcher app prefix (e.g. /app/, /stream/) for correct API routing
  function _apiUrl(endpoint) {
    const match = window.location.pathname.match(/^\/(app|stream|zoo|compiler|planner|benchmark)(\/|$)/);
    if (match) return '/' + match[1] + endpoint;
    return endpoint;
  }

  async function _streamChat(message, aiEl) {
    const body = JSON.stringify({
      message: message,
      history: _history.slice(0, -1).slice(-8),  // Last 8 messages (4 turns)
      lang: (typeof DXI18n !== 'undefined') ? DXI18n.lang : 'en',
      context: _pendingContext || undefined,
    });
    _pendingContext = null;

    try {
      const resp = await fetch(_apiUrl('/api/chat'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body,
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: 'Unknown error' }));
        _finishAI(aiEl, err.error || 'Error', { error: true });
        return;
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let fullText = '';
      let buffer = '';
      let streamDone = false;

      // Finish on the explicit [DONE] sentinel — do NOT rely solely on stream EOF.
      // When the chatbot runs inside a module iframe, /api/chat is proxied by the
      // launcher and the browser-facing connection may stay open (keep-alive) after
      // the response, so reader.read() never reports done. Waiting on EOF then hangs
      // this promise, its .finally() never resets _sending, and the next send is
      // silently blocked by the `!text || _sending` guard (arrow appears dead).
      while (!streamDone) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') { streamDone = true; break; }
            try {
              const parsed = JSON.parse(data);
              if (parsed.token) {
                fullText += parsed.token;
                _updateAI(aiEl, fullText);
              }
            } catch (e) {
              // Ignore parse errors for partial SSE data
            }
          }
        }
      }

      // Release the (possibly still-open) connection so the socket is freed.
      try { await reader.cancel(); } catch (e) { /* already closed */ }

      if (!fullText) fullText = _t('(No response)', '(응답 없음)');
      _finishAI(aiEl, fullText);

    } catch (err) {
      _finishAI(aiEl, _t('Connection error: Unable to reach server.', '연결 오류: 서버에 연결할 수 없습니다.'), { error: true });
    }
  }


  function _renderMessage(role, content, isStreaming) {
    const el = document.createElement('div');
    el.className = 'dx-chat-msg ' + role;

    if (role === 'ai' && isStreaming) {
      el.innerHTML = '<div class="dx-chat-typing"><span></span><span></span><span></span></div>';
    } else {
      el.innerHTML = role === 'ai' ? _renderMarkdown(content) : _escapeHtml(content);
    }

    _els.messages.appendChild(el);
    _scrollBottom();
    return el;
  }

  function _updateAI(el, text) {
    el.innerHTML = _renderMarkdown(text);
    _scrollBottom();
  }

  function _finishAI(el, text, opts) {
    el.innerHTML = _renderMarkdown(text);
    /* 오류는 말풍선 색과 경고 아이콘으로 — 예전에는 글 앞의 이모지였다 (spec 2026-09-29 아이콘 체계). */
    if (opts && opts.error) {
      el.classList.add('is-error');
      el.insertAdjacentHTML('afterbegin', _ico('alert') + ' ');
    }
    _history.push({ role: 'assistant', content: text });
    _scrollBottom();
  }


  function _renderMarkdown(text) {
    if (!text) return '';
    let html = _escapeHtml(text);

    // Code blocks (```...```)
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
      return '<pre><code>' + code.trim() + '</code></pre>';
    });

    // Inline code (`...`)
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Bold (**...**)
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Italic (*...*)
    html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');

    // Tables (simple: | col | col | ...)
    html = html.replace(/((?:\|[^\n]+\|\n?)+)/g, (block) => {
      const rows = block.trim().split('\n').filter(r => r.trim());
      if (rows.length < 2) return block;
      // Check if second row is separator
      const isSep = /^\|[\s\-:|]+\|$/.test(rows[1].trim());
      let table = '<table>';
      rows.forEach((row, i) => {
        if (isSep && i === 1) return; // skip separator row
        const cells = row.split('|').filter((c, ci, arr) => ci > 0 && ci < arr.length - 1);
        const tag = (isSep && i === 0) ? 'th' : 'td';
        table += '<tr>' + cells.map(c => '<' + tag + '>' + c.trim() + '</' + tag + '>').join('') + '</tr>';
      });
      table += '</table>';
      return table;
    });

    // Unordered lists (- item or * item)
    html = html.replace(/(?:^|\n)((?:[\-\*] [^\n]+\n?)+)/g, (block) => {
      const items = block.trim().split('\n');
      return '<ul>' + items.map(item => '<li>' + item.replace(/^[\-\*] /, '') + '</li>').join('') + '</ul>';
    });

    // Ordered lists (1. item)
    html = html.replace(/(?:^|\n)((?:\d+\. [^\n]+\n?)+)/g, (block) => {
      const items = block.trim().split('\n');
      return '<ol>' + items.map(item => '<li>' + item.replace(/^\d+\. /, '') + '</li>').join('') + '</ol>';
    });

    // Line breaks
    html = html.replace(/\n/g, '<br>');

    return html;
  }

  function _escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }


  var _PROVIDER_LABEL = { openai: 'OpenAI', anthropic: 'Anthropic', google: 'Google', github: 'GitHub Models',
                          custom: 'Custom endpoint', local: 'Local / Self-hosted' };

  /* 지금 누가 답하는지 한 줄로 늘 보인다 (spec 2026-10-11 chat settings §3.4). 예전에는 "API 키를 등록하세요" 경고였다 —
     로그인된 coding agent 로 key 없이 답할 수 있는 PC 에서도. */
  function _renderSource() {
    var el = _els.source;
    if (!el || !_status) return;
    var src = _status.source || { kind: 'none' };
    var label;
    if (src.kind === 'none') label = _t('Basic guidance only');
    else if (src.provider === 'agent-cli') label = _t('Answering with your {agent} login').replace('{agent}', src.agent || 'CLI');
    else label = _t(_PROVIDER_LABEL[src.provider] || src.provider) + (src.model ? ' · ' + src.model : '');
    el.className = 'dx-chat-source' + (src.kind === 'none' ? ' is-none' : '');
    el.innerHTML = '<span class="dx-chat-source-dot" aria-hidden="true"></span><span class="dx-chat-source-text"></span>' +
      '<button type="button" class="dx-chat-source-change"></button>';
    el.querySelector('.dx-chat-source-text').textContent = label;
    var btn = el.querySelector('button');
    btn.textContent = src.kind === 'none' ? _t('Connect AI') : _t('Change');
    btn.addEventListener('click', _openSettingsPanel);
  }

  function _checkConfig() {
    return fetch(_apiUrl('/api/chat/config'))
      .then(r => r.json())
      .then(data => {
        _status = data || {};
        _renderSource();
        return _status;
      })
      .catch(() => null);   // config endpoint not available — no status line
  }


  function _openSettingsPanel() {
    if (!_els.settingsPanel) return;
    _els.settingsPanel.hidden = false;
    _els.settingsPanel.classList.add('open');
    _showSettingsStatus('', '');
    _loadSettings();
  }

  function _closeSettingsPanel() {
    if (!_els.settingsPanel) return;
    _els.settingsPanel.classList.remove('open');
    _els.settingsPanel.hidden = true;
  }

  function _kindOf(provider) {
    return provider === 'agent-cli' ? 'agent' : provider === 'local' ? 'local' : 'cloud';
  }

  function _setKind(kind) {
    var r = _els.win.querySelector('input[name=dx-chat-kind][value=' + kind + ']');
    if (r) r.checked = true;
    if (_els.fieldAgent) _els.fieldAgent.hidden = kind !== 'agent';
    if (_els.fieldProvider) _els.fieldProvider.hidden = kind !== 'cloud';
    if (kind === 'agent') _els.settingsProvider.value = 'agent-cli';
    else if (kind === 'local') _els.settingsProvider.value = 'local';
    else if (_els.settingsProvider.value === 'agent-cli' || _els.settingsProvider.value === 'local') {
      _els.settingsProvider.value = 'openai';
    }
    _setApiKeyPlaceholder(_savedKeyFor(_els.settingsProvider.value));
    _toggleSettingsEndpoint();
  }

  function _savedKeyFor(provider) {
    return (_status && _status.configured && _status.provider === provider) ? _status.api_key : null;
  }

  /* 설치된 CLI 만, 로그인 상태와 함께. 로그인이 필요하면 그 명령을 보인다. */
  function _fillAgents(current) {
    var sel = _els.agentSelect;
    if (!sel) return;
    var rows = ((_status && _status.agents) || []).filter(function (a) { return a.installed; });
    sel.innerHTML = rows.map(function (a) {
      var state = a.authenticated === false ? _t('sign in: {cmd}').replace('{cmd}', a.login_hint)
        : a.authenticated === true ? _t('signed in') : '';
      return '<option value="' + _escapeHtml(a.name) + '"' + (a.name === current ? ' selected' : '') + '>' +
        _escapeHtml(a.name + (state ? ' — ' + state : '')) + '</option>';
    }).join('');
  }

  function _loadSettings() {
    _checkConfig().then(function (data) {
      if (!data) { _showSettingsStatus(_t('Unable to load settings.', '설정을 불러올 수 없습니다.'), 'error'); return; }
      var src = data.source || {};
      var saved = !!data.configured;
      var provider = saved ? (data.provider || 'openai') : null;
      var model = saved ? (data.model || '') : '';
      var agent = provider === 'agent-cli' ? (model.split('::')[0] || src.agent) : src.agent;
      _fillAgents(agent);
      _els.settingsModel.value = provider === 'agent-cli' ? (model.split('::')[1] || '') : model;
      _els.settingsEndpoint.value = saved ? (data.endpoint || '') : '';
      var temp = saved && data.temperature != null ? data.temperature : 0.7;
      _els.settingsTemp.value = temp;
      _els.settingsTempVal.textContent = temp;
      _els.settingsApiKey.value = '';
      if (provider) _els.settingsProvider.value = provider;
      var anyAgent = (data.agents || []).some(function (a) { return a.installed; });
      _setKind(provider ? _kindOf(provider) : (anyAgent ? 'agent' : 'local'));
      if (_els.resetBtn) _els.resetBtn.hidden = !saved;
      if (_els.forceBtn) _els.forceBtn.hidden = true;
    });
  }

  function _isKeylessProvider(provider) {
    return provider === 'local' || provider === 'agent-cli';
  }

  // Model preset suggestions per HTTP provider, surfaced as a <datalist> dropdown on the
  // Model field. These are SUGGESTIONS — the field stays free-text, so a user can still type
  // any exact model id their key exposes (newer/older than this list). Ordered newest-first.
  var _MODEL_PRESETS = {
    openai: [
      'gpt-5.6-terra', 'gpt-5.6-sol', 'gpt-5.6-luna',
      'gpt-5.5', 'gpt-5.4', 'gpt-5.4-mini', 'gpt-5.4-nano',
      'gpt-4.1', 'gpt-4.1-mini', 'gpt-4o', 'gpt-4o-mini',
      'o4-mini', 'o3', 'o3-mini',
    ],
    anthropic: [
      'claude-opus-5', 'claude-sonnet-5', 'claude-haiku-4-5-20251001',
      'claude-opus-4-8', 'claude-opus-4-7', 'claude-opus-4-6',
      'claude-sonnet-4-6', 'claude-sonnet-4-5', 'claude-fable-5',
      'claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022',
    ],
    google: [
      'gemini-3.1-pro-preview', 'gemini-3-flash-preview', 'gemini-3.5-flash',
      'gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-1.5-pro', 'gemini-1.5-flash',
    ],
    github: [
      'gpt-5.6-terra', 'gpt-5.6-sol', 'gpt-5.6-luna', 'gpt-5.5', 'gpt-5.4',
      'gpt-4.1', 'gpt-4o', 'gpt-4o-mini',
      'claude-opus-5', 'claude-sonnet-5', 'claude-opus-4-8', 'claude-sonnet-4-6',
      'gemini-3.1-pro-preview', 'gemini-3-flash-preview', 'gemini-2.5-pro',
    ],
  };
  var _CUSTOM_OPT = '__custom__';   // sentinel option → reveals the free-text model input

  function _fillSelect(sel, models, current) {
    if (!sel) return;
    sel.innerHTML = models.map(function (m) {
      return '<option value="' + _escapeHtml(m) + '"' + (m === current ? ' selected' : '') +
             '>' + _escapeHtml(m) + '</option>';
    }).join('');
  }

  function _toggleSettingsEndpoint() {
    const provider = _els.settingsProvider ? _els.settingsProvider.value : '';
    const isLocal = provider === 'local';
    // Endpoint field shown for custom and local (local = base URL); not for agent-cli.
    if (_els.settingsEndpointField) {
      _els.settingsEndpointField.hidden = !(provider === 'custom' || isLocal);
    }
    // Keyless providers (local runtime, CLI-login agent) need no API key.
    if (_els.settingsApiKey) {
      const keyField = _els.settingsApiKey.closest('.dx-chat-settings-field');
      if (keyField) keyField.hidden = _isKeylessProvider(provider);
    }
    if (_els.settingsEndpoint && isLocal && !_els.settingsEndpoint.value) {
      _els.settingsEndpoint.placeholder = 'http://localhost:11434';
    }
    if (_els.settingsModel && !_els.settingsModel.value) {
      const modelHints = {
        github: 'gpt-4o-mini',
        openai: 'gpt-4o-mini',
        anthropic: 'claude-haiku-4-5-20251001',
        google: 'gemini-1.5-flash',
        custom: 'your-model-name',
        local: 'qwen2.5 / deepseek-r1 / …',
        'agent-cli': 'claude / opencode / cursor / copilot / codex',
      };
      _els.settingsModel.placeholder = modelHints[provider] || 'gpt-4o-mini';
    }
    _updateModelChooser(provider);
  }

  // Model chooser — three controls share the "Model" row:
  //   settingsModelSelect   primary styled dropdown (API presets / agent list / local models)
  //   agentModelSelect      agent-cli only: the chosen agent's model list (like dx_agent_dev)
  //   settingsModel (text)  free-text override (API "Custom…" / custom endpoint / no-runtime)
  function _fetchAgentModels(agent, current) {
    var sel = _els.agentModelSelect;
    if (!sel) return;
    // Cross-module: /agent/* is proxied to dx_agent_dev by the launcher (same origin).
    fetch('/agent/api/agent/models?agent=' + encodeURIComponent(agent))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var models = (d && d.models) || [];
        if (!models.length) { sel.hidden = true; sel.innerHTML = ''; return; }
        _fillSelect(sel, models, (current && models.indexOf(current) !== -1) ? current
          : (d.default_model && models.indexOf(d.default_model) !== -1 ? d.default_model : models[0]));
        sel.hidden = false;
      })
      .catch(function () { sel.hidden = true; sel.innerHTML = ''; });
  }

  function _updateModelChooser(provider) {
    var cur = (_els.settingsModel && _els.settingsModel.value) || '';
    var modelSel = _els.settingsModelSelect;
    if (_els.agentModelSelect) _els.agentModelSelect.hidden = true;

    if (provider === 'agent-cli') {
      // The agent comes from its own select; the model row shows that agent's models (settingsModel = sub-model).
      var agent = (_els.agentSelect && _els.agentSelect.value) || 'claude';
      if (modelSel) modelSel.hidden = true;
      if (_els.settingsModel) _els.settingsModel.hidden = true;
      _fetchAgentModels(agent, cur);
      return;
    }

    if (provider === 'local') {
      var base = ((_els.settingsEndpoint && _els.settingsEndpoint.value) || 'http://localhost:11434').trim();
      fetch(_apiUrl('/api/chat/local/models?base=' + encodeURIComponent(base)))
        .then(function (r) { return r.json(); })
        .then(function (d) {
          var models = (d && d.models) || [];
          if (models.length) {
            _fillSelect(modelSel, models, cur || models[0]);
            if (modelSel) modelSel.hidden = false;
            if (_els.settingsModel) _els.settingsModel.hidden = true;
            _showSettingsStatus(_t('Found models: ', '발견된 모델: ') + models.join(', '), 'success');
          } else {
            if (modelSel) modelSel.hidden = true;
            if (_els.settingsModel) _els.settingsModel.hidden = false;
            _showSettingsStatus(
              _t('No local runtime detected. Start one (e.g. `ollama pull deepseek-r1`) then retry.',
                 '로컬 런타임이 감지되지 않았습니다. 먼저 실행하세요 (예: `ollama pull deepseek-r1`) 후 재시도.'),
              'error');
          }
        })
        .catch(function () {
          if (modelSel) modelSel.hidden = true;
          if (_els.settingsModel) _els.settingsModel.hidden = false;
        });
      return;
    }

    if (provider === 'custom') {   // free-text only
      if (modelSel) modelSel.hidden = true;
      if (_els.settingsModel) _els.settingsModel.hidden = false;
      return;
    }

    // API providers (openai/anthropic/google/github): styled preset dropdown + "Custom…".
    var presets = _MODEL_PRESETS[provider] || [];
    var isCustom = !!cur && presets.indexOf(cur) === -1;
    if (modelSel) {
      modelSel.innerHTML = presets.map(function (m) {
        return '<option value="' + _escapeHtml(m) + '"' + (m === cur ? ' selected' : '') +
               '>' + _escapeHtml(m) + '</option>';
      }).join('') + '<option value="' + _CUSTOM_OPT + '"' + (isCustom ? ' selected' : '') +
        '>' + _escapeHtml(_t('Custom…', '직접 입력…')) + '</option>';
      modelSel.hidden = false;
    }
    if (_els.settingsModel) _els.settingsModel.hidden = !isCustom;
  }

  // React to dropdown changes: agent-cli → reload that agent's models; API → reveal the
  // free-text input only when "Custom…" is chosen.
  function _onModelSelectChange() {
    var provider = _els.settingsProvider ? _els.settingsProvider.value : '';
    var val = _els.settingsModelSelect ? _els.settingsModelSelect.value : '';
    if (provider !== 'agent-cli' && provider !== 'local' && provider !== 'custom') {
      if (_els.settingsModel) _els.settingsModel.hidden = (val !== _CUSTOM_OPT);
    }
  }

  function _setApiKeyPlaceholder(maskedKey) {
    if (!_els.settingsApiKey) return;
    if (maskedKey) {
      _els.settingsApiKey.placeholder = maskedKey;
      _els.settingsApiKey.title = _t('Leave blank to keep the saved key');
      return;
    }
    _els.settingsApiKey.title = '';
    _els.settingsApiKey.placeholder = _els.settingsProvider && _els.settingsProvider.value === 'github'
      ? 'ghp_...'
      : 'sk-...';
  }

  function _settingsPayload() {
    const provider = _els.settingsProvider.value;
    const keyless = _isKeylessProvider(provider);
    const apiKey = _els.settingsApiKey.value.trim();
    const selVal = (_els.settingsModelSelect && !_els.settingsModelSelect.hidden)
      ? _els.settingsModelSelect.value : '';
    let model;
    if (provider === 'agent-cli') {
      // Encode "<agent>::<submodel>" (submodel optional → agent default).
      const agent = (_els.agentSelect && _els.agentSelect.value) || 'claude';
      const sub = (_els.agentModelSelect && !_els.agentModelSelect.hidden)
        ? (_els.agentModelSelect.value || '').trim() : '';
      model = sub ? (agent + '::' + sub) : agent;
    } else if (selVal && selVal !== _CUSTOM_OPT) {
      model = selVal.trim();                          // dropdown pick (API preset / local model)
    } else {
      model = (_els.settingsModel.value || '').trim(); // free-text (Custom… / custom endpoint)
    }
    if (!keyless && !apiKey && !_savedKeyFor(provider)) {   // blank keeps the saved key of the same provider
      _showSettingsStatus(_t('Please enter an API key.', 'API 키를 입력해주세요.'), 'error');
      return null;
    }
    if (!model) {
      _showSettingsStatus(_t('Please enter a model.', '모델을 입력해주세요.'), 'error');
      return null;
    }
    return {
      provider: provider,
      api_key: apiKey,
      model: model,
      endpoint: _els.settingsEndpoint.value.trim(),
      temperature: parseFloat(_els.settingsTemp.value),
    };
  }

  /* 저장은 먼저 연결을 확인한다. 실패하면 이유를 보이고 "그래도 저장" 을 건넨다 (지금 망이 막혀 있어도 설정해 두려는 경우). */
  function _postConfig(body) {
    if (_els.forceBtn) _els.forceBtn.hidden = true;
    _showSettingsStatus(body.force ? _t('Saving...', '저장 중...') : _t('Checking the connection…'), '');
    return fetch(_apiUrl('/api/chat/config'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
      .then(r => r.json().then(d => ({ ok: r.ok, d: d })))
      .then(({ ok, d }) => {
        if (ok && d.ok) {
          _showSettingsStatus(d.tested ? _t('Connected: ', '연결 성공: ') + (d.response || '').slice(0, 80)
                                       : _t('Saved without a test.'), 'success');
          _checkConfig();
          setTimeout(_closeSettingsPanel, 900);
        } else {
          _showSettingsStatus(d.error || 'Error', 'error');
          if (d.tested && _els.forceBtn) {
            _els.forceBtn.hidden = false;
            _els.forceBtn.onclick = function () { _postConfig(Object.assign({}, body, { force: true })); };
          }
        }
      })
      .catch(() => _showSettingsStatus(_t('Connection failed.', '연결 실패.'), 'error'));
  }

  function _saveSettings(e) {
    if (e) e.preventDefault();
    const body = _settingsPayload();
    if (body) _postConfig(body);
    return false;
  }

  function _resetToAuto() {
    fetch(_apiUrl('/api/chat/config'), { method: 'DELETE' })
      .then(() => _checkConfig())
      .then(() => _closeSettingsPanel());
  }

  function _refreshKnowledge() {
    _showSettingsStatus(_t('Re-syncing SDK knowledge...', 'SDK 지식 재동기화 중...'), '');
    fetch(_apiUrl('/api/chat/knowledge/refresh'), { method: 'POST' })
      .then(r => r.json())
      .then(data => {
        if (data && data.ok) {
          _showSettingsStatus(
            _t('Knowledge updated (', '지식 갱신됨 (') + data.sources + _t(' sources).', '개 소스).'),
            'success');
        } else {
          _showSettingsStatus(((data && data.error) || 'Error'), 'error');
        }
      })
      .catch(() => _showSettingsStatus(_t('Refresh failed.', '새로고침 실패.'), 'error'));
  }

  function _showSettingsStatus(msg, cls) {
    if (!_els.settingsStatus) return;
    _els.settingsStatus.textContent = msg;
    if (cls === 'error') _els.settingsStatus.insertAdjacentHTML('afterbegin', _ico('alert') + ' ');
    _els.settingsStatus.className = 'dx-chat-settings-status' + (cls ? ' ' + cls : '');
  }


  function showSuggestions(suggestions) {
    if (!_els.suggestions || !Array.isArray(suggestions) || !suggestions.length) {
      _els.suggestions.style.display = 'none';
      return;
    }
    _els.suggestions.innerHTML = '';
    suggestions.forEach(s => {
      const chip = document.createElement('button');
      chip.className = 'dx-chat-suggestion';
      chip.textContent = s;
      chip.addEventListener('click', () => {
        _els.input.value = s;
        _send();
      });
      _els.suggestions.appendChild(chip);
    });
    _els.suggestions.style.display = 'flex';
  }


  function _loadHistory() {
    try {
      const raw = sessionStorage.getItem('dx-chat-history-' + _appName);
      _history = raw ? JSON.parse(raw) : [];
    } catch (e) {
      _history = [];
    }
  }

  function _saveHistory() {
    try {
      sessionStorage.setItem('dx-chat-history-' + _appName, JSON.stringify(_history));
    } catch (e) {
      // Storage full or unavailable
    }
  }

  function _clearHistory() {
    _history = [];
    _saveHistory();
    _els.messages.innerHTML = '';
    _els.suggestions.style.display = 'none';
  }


  function _scrollBottom() {
    if (_els.messages) {
      _els.messages.scrollTop = _els.messages.scrollHeight;
    }
  }

  function _autoResize() {
    const el = _els.input;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 100) + 'px';
  }

  function openWith(opts) {
    opts = opts || {};
    if (!_els.window.classList.contains('open')) toggle();
    if (opts.message && _els.input) _els.input.value = opts.message;
    if (opts.context) _pendingContext = opts.context;
    if (opts.autoSend) _send();
  }


  return {
    init,
    toggle,
    showSuggestions,
    openWith,
  };
})();
