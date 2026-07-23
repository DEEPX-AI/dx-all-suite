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
  '(No response)': { ko: '(응답 없음)', ja: '(応答なし)', es: '(Sin respuesta)', 'zh-CN': '(无响应)', 'zh-TW': '(無回應)' },
  '⚠️ Connection error: Unable to reach server.': { ko: '⚠️ 연결 오류: 서버에 연결할 수 없습니다.', ja: '⚠️ 接続エラー: サーバーに接続できません。', es: '⚠️ Error de conexión: no se puede acceder al servidor.', 'zh-CN': '⚠️ 连接错误：无法访问服务器。', 'zh-TW': '⚠️ 連線錯誤：無法連線至伺服器。' },
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
  'DX Assistant': { ko: 'DX 어시스턴트', ja: 'DXアシスタント', es: 'Asistente DX', 'zh-CN': 'DX 助手', 'zh-TW': 'DX 助手' },
  '⚠️ AI assistant is not configured. Open chat settings to register your API key. Basic guidance is available without AI. <button type="button" class="dx-chat-banner-action" data-action="settings-open">Open settings</button>': {
    ko: '⚠️ AI 어시스턴트가 설정되지 않았습니다. 채팅 설정에서 API 키를 등록하세요. 기본 안내는 AI 없이도 가능합니다. <button type="button" class="dx-chat-banner-action" data-action="settings-open">설정 열기</button>',
    ja: '⚠️ AIアシスタントが設定されていません。チャット設定でAPIキーを登録してください。基本ガイドはAIなしでも利用できます。<button type="button" class="dx-chat-banner-action" data-action="settings-open">設定を開く</button>',
    es: '⚠️ El asistente de IA no está configurado. Abra la configuración del chat para registrar su clave API. La guía básica está disponible sin IA. <button type="button" class="dx-chat-banner-action" data-action="settings-open">Abrir ajustes</button>',
    'zh-CN': '⚠️ AI 助手未配置。请在聊天设置中注册 API 密钥。基本指南无需 AI 也可使用。<button type="button" class="dx-chat-banner-action" data-action="settings-open">打开设置</button>',
    'zh-TW': '⚠️ AI 助手未設定。請在聊天設定中註冊 API 金鑰。基本指南無需 AI 也可使用。<button type="button" class="dx-chat-banner-action" data-action="settings-open">開啟設定</button>',
  },
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
  let _configured = false;
  let _els = {};
  let _headerTitle = null;

  function _chatLang() {
    return (typeof DXI18n !== 'undefined' && DXI18n.lang)
      || (typeof localStorage !== 'undefined' && localStorage.getItem('dx-lang'))
      || 'en';
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


  function _buildDOM() {
    const fab = document.createElement('button');
    fab.className = 'dx-chat-fab';
    fab.setAttribute('aria-label', 'Chat');
    fab.innerHTML = '💬';
    fab.addEventListener('click', toggle);
    document.body.appendChild(fab);
    _els.fab = fab;

    const win = document.createElement('div');
    win.className = 'dx-chat-window';
    win.innerHTML = [
      '<div class="dx-chat-header">',
      '  <span class="dx-chat-header-title">' + _t('DX Assistant') + '</span>',
      '  <div class="dx-chat-header-actions">',
      '    <button class="dx-chat-header-btn" data-action="settings" title="' + _t('AI settings', 'AI 설정') + '" aria-label="' + _t('AI settings', 'AI 설정') + '">⚙️</button>',
      '    <button class="dx-chat-header-btn" data-action="clear" title="' + _t('Clear chat', '대화 초기화') + '">🗑️</button>',
      '    <button class="dx-chat-header-btn" data-action="close" title="' + _t('Close', '닫기') + '">✕</button>',
      '  </div>',
      '</div>',
      '<div class="dx-chat-banner" style="display:none"></div>',
      '<div class="dx-chat-settings-panel" hidden>',
      '  <form class="dx-chat-settings-form">',
      '    <div class="dx-chat-settings-title">' + _t('AI Assistant Settings', 'AI 어시스턴트 설정') + '</div>',
      '    <label class="dx-chat-settings-field">',
      '      <span>' + _t('Provider', '제공자') + '</span>',
      '      <select class="dx-chat-settings-provider">',
      '        <option value="openai">OpenAI</option>',
      '        <option value="github">GitHub Models</option>',
      '        <option value="custom">Custom endpoint</option>',
      '        <option value="local">' + _t('Local / Self-hosted', '로컬 / 자체 호스팅') + '</option>',
      '        <option value="agent-cli">' + _t('Coding agent (CLI login)', '코딩 에이전트 (CLI 로그인)') + '</option>',
      '        <option value="anthropic">Anthropic</option>',
      '        <option value="google">Google</option>',
      '      </select>',
      '    </label>',
      '    <label class="dx-chat-settings-field">',
      '      <span>API Key</span>',
      '      <input class="dx-chat-settings-api-key" type="password" autocomplete="off" placeholder="sk-...">',
      '    </label>',
      '    <label class="dx-chat-settings-field">',
      '      <span>Model</span>',
      '      <input class="dx-chat-settings-model" type="text" placeholder="gpt-4o-mini">',
      '      <select class="dx-chat-settings-model-select" hidden></select>',
      '    </label>',
      '    <label class="dx-chat-settings-field dx-chat-settings-endpoint-field" hidden>',
      '      <span>Endpoint</span>',
      '      <input class="dx-chat-settings-endpoint" type="url" placeholder="https://api.example.com/v1/chat/completions">',
      '    </label>',
      '    <label class="dx-chat-settings-field">',
      '      <span>' + _t('Temperature', '온도') + ' <strong class="dx-chat-settings-temp-value">0.7</strong></span>',
      '      <input class="dx-chat-settings-temp" type="range" min="0" max="2" step="0.1" value="0.7">',
      '    </label>',
      '    <div class="dx-chat-settings-actions">',
      '      <button type="button" class="dx-chat-settings-test">' + _t('Test', '테스트') + '</button>',
      '      <button type="button" class="dx-chat-settings-refresh-kb" title="' + _t('Re-sync SDK knowledge from .deepx', '.deepx에서 SDK 지식 재동기화') + '">' + _t('Refresh knowledge', '지식 새로고침') + '</button>',
      '      <button type="submit" class="dx-chat-settings-save">' + _t('Save', '저장') + '</button>',
      '      <button type="button" class="dx-chat-settings-close" data-action="settings-close">' + _t('Close', '닫기') + '</button>',
      '    </div>',
      '    <div class="dx-chat-settings-status" aria-live="polite"></div>',
      '  </form>',
      '</div>',
      '<div class="dx-chat-messages"></div>',
      '<div class="dx-chat-suggestions"></div>',
      '<div class="dx-chat-input-area">',
      '  <textarea class="dx-chat-input" placeholder="' + _t('Ask a question...', '질문을 입력하세요...') + '" rows="1"></textarea>',
      '  <button class="dx-chat-send-btn" aria-label="Send">➤</button>',
      '</div>',
    ].join('\n');
    document.body.appendChild(win);
    _els.win = win;
    _els.banner = win.querySelector('.dx-chat-banner');
    _els.settingsPanel = win.querySelector('.dx-chat-settings-panel');
    _els.settingsForm = win.querySelector('.dx-chat-settings-form');
    _els.settingsProvider = win.querySelector('.dx-chat-settings-provider');
    _els.settingsApiKey = win.querySelector('.dx-chat-settings-api-key');
    _els.settingsModel = win.querySelector('.dx-chat-settings-model');
    _els.settingsModelSelect = win.querySelector('.dx-chat-settings-model-select');
    _els.settingsEndpoint = win.querySelector('.dx-chat-settings-endpoint');
    _els.settingsEndpointField = win.querySelector('.dx-chat-settings-endpoint-field');
    _els.settingsTemp = win.querySelector('.dx-chat-settings-temp');
    _els.settingsTempVal = win.querySelector('.dx-chat-settings-temp-value');
    _els.settingsStatus = win.querySelector('.dx-chat-settings-status');
    _els.settingsTestBtn = win.querySelector('.dx-chat-settings-test');
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

    win.querySelector('[data-action="close"]').addEventListener('click', toggle);
    win.querySelector('[data-action="clear"]').addEventListener('click', _clearHistory);
    win.querySelector('[data-action="settings"]').addEventListener('click', _openSettingsPanel);
    win.querySelector('[data-action="settings-close"]').addEventListener('click', _closeSettingsPanel);
    _els.settingsForm.addEventListener('submit', _saveSettings);
    _els.settingsTestBtn.addEventListener('click', _testSettingsConnection);
    if (_els.settingsRefreshKb) _els.settingsRefreshKb.addEventListener('click', _refreshKnowledge);
    _els.settingsProvider.addEventListener('change', () => {
      _toggleSettingsEndpoint();
      _setApiKeyPlaceholder();
    });
    _els.settingsTemp.addEventListener('input', () => {
      _els.settingsTempVal.textContent = _els.settingsTemp.value;
    });

    if (typeof DXI18n !== 'undefined') {
      DXI18n.onLangChange(function() {
        if (_els.input) _els.input.placeholder = _t('Ask a question...', '질문을 입력하세요...');
        if (_headerTitle) {
          const titleEl = _els.win && _els.win.querySelector('.dx-chat-header-title');
          if (titleEl) {
            titleEl.textContent = _headerTitle[DXI18n.lang] || _headerTitle.en || titleEl.textContent;
          }
        }
        var settingsBtn = win.querySelector('[data-action="settings"]');
        if (settingsBtn) settingsBtn.title = _t('AI settings', 'AI 설정');
        var clearBtn = win.querySelector('[data-action="clear"]');
        if (clearBtn) clearBtn.title = _t('Clear chat', '대화 초기화');
        var closeBtn = win.querySelector('[data-action="close"]');
        if (closeBtn) closeBtn.title = _t('Close', '닫기');
        _renderConfigBanner();
      });
    }

    _history.forEach(m => _renderMessage(m.role, m.content, false));
    _scrollBottom();
  }


  function toggle() {
    _open = !_open;
    _els.win.classList.toggle('open', _open);
    _els.fab.classList.toggle('open', _open);
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
        _finishAI(aiEl, '⚠️ ' + (err.error || 'Error'));
        return;
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let fullText = '';
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
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

      if (!fullText) fullText = _t('(No response)', '(응답 없음)');
      _finishAI(aiEl, fullText);

    } catch (err) {
      _finishAI(aiEl, _t('⚠️ Connection error: Unable to reach server.', '⚠️ 연결 오류: 서버에 연결할 수 없습니다.'));
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

  function _finishAI(el, text) {
    el.innerHTML = _renderMarkdown(text);
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


  function _renderConfigBanner() {
    if (!_els.banner) return;
    if (!_configured) {
      _els.banner.innerHTML = _t(
        '⚠️ AI assistant is not configured. Open chat settings to register your API key. Basic guidance is available without AI. <button type="button" class="dx-chat-banner-action" data-action="settings-open">Open settings</button>',
        '⚠️ AI 어시스턴트가 설정되지 않았습니다. 채팅 설정에서 API 키를 등록하세요. 기본 안내는 AI 없이도 가능합니다. <button type="button" class="dx-chat-banner-action" data-action="settings-open">설정 열기</button>'
      );
      const bannerBtn = _els.banner.querySelector('[data-action="settings-open"]');
      if (bannerBtn) bannerBtn.addEventListener('click', _openSettingsPanel);
      _els.banner.style.display = 'block';
    } else {
      _els.banner.style.display = 'none';
    }
  }

  function _checkConfig() {
    fetch(_apiUrl('/api/chat/config'))
      .then(r => r.json())
      .then(data => {
        _configured = data.configured;
        _renderConfigBanner();
      })
      .catch(() => {
        // Config endpoint not available — hide banner
      });
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

  function _loadSettings() {
    fetch(_apiUrl('/api/chat/config'))
      .then(r => r.json())
      .then(data => {
        const chatApiKey = _els.settingsApiKey;
        if (data.configured) {
          _els.settingsProvider.value = data.provider || 'openai';
          _els.settingsModel.value = data.model || '';
          _els.settingsEndpoint.value = data.endpoint || '';
          const temp = data.temperature != null ? data.temperature : 0.7;
          _els.settingsTemp.value = temp;
          _els.settingsTempVal.textContent = temp;
          chatApiKey.value = '';
          _setApiKeyPlaceholder(data.api_key);
        } else {
          if (!_els.settingsProvider.value) _els.settingsProvider.value = 'openai';
          if (!_els.settingsModel.value) _els.settingsModel.value = '';
          _els.settingsEndpoint.value = '';
          _els.settingsTemp.value = 0.7;
          _els.settingsTempVal.textContent = '0.7';
          chatApiKey.value = '';
          _setApiKeyPlaceholder();
        }
        _toggleSettingsEndpoint();
      })
      .catch(() => _showSettingsStatus(_t('Unable to load settings.', '설정을 불러올 수 없습니다.'), 'error'));
  }

  function _isKeylessProvider(provider) {
    return provider === 'local' || provider === 'agent-cli';
  }

  function _toggleSettingsEndpoint() {
    const provider = _els.settingsProvider ? _els.settingsProvider.value : '';
    const isLocal = provider === 'local';
    const isAgentCli = provider === 'agent-cli';
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
        anthropic: 'claude-3-5-haiku-20241022',
        google: 'gemini-1.5-flash',
        custom: 'your-model-name',
        local: 'qwen2.5 / deepseek-r1 / …',
        'agent-cli': 'claude / opencode / cursor / copilot / codex',
      };
      _els.settingsModel.placeholder = modelHints[provider] || 'gpt-4o-mini';
    }
    if (isAgentCli) {
      _showSettingsStatus(
        _t('Uses your logged-in coding-agent CLI — pick the agent below.',
           '로그인된 코딩 에이전트 CLI를 사용합니다 — 아래에서 에이전트를 선택하세요.'),
        '');
    }
    _updateModelChooser(provider);
  }

  // Show the Model field as a click-to-select dropdown when models are discoverable
  // (local runtime / coding-agent CLI); free-text input for HTTP providers.
  function _showModelSelect(show) {
    if (_els.settingsModelSelect) _els.settingsModelSelect.hidden = !show;
    if (_els.settingsModel) _els.settingsModel.hidden = show;
  }
  function _fillModelSelect(models, current) {
    const sel = _els.settingsModelSelect;
    if (!sel) return;
    sel.innerHTML = '';
    models.forEach(function (m) {
      const o = document.createElement('option');
      o.value = m; o.textContent = m;
      if (m === current) o.selected = true;
      sel.appendChild(o);
    });
  }
  function _updateModelChooser(provider) {
    const cur = (_els.settingsModel && _els.settingsModel.value) || '';
    if (provider === 'agent-cli') {
      _fillModelSelect(['claude', 'opencode', 'cursor', 'copilot', 'codex'], cur || 'claude');
      _showModelSelect(true);
    } else if (provider === 'local') {
      const base = ((_els.settingsEndpoint && _els.settingsEndpoint.value) || 'http://localhost:11434').trim();
      fetch(_apiUrl('/api/chat/local/models?base=' + encodeURIComponent(base)))
        .then(r => r.json())
        .then(function (d) {
          const models = (d && d.models) || [];
          if (models.length) {
            _fillModelSelect(models, cur || models[0]);
            _showModelSelect(true);
            _showSettingsStatus(_t('Found models: ', '발견된 모델: ') + models.join(', '), 'success');
          } else {
            _showModelSelect(false);
            _showSettingsStatus(
              _t('No local runtime detected. Start one (e.g. `ollama pull deepseek-r1`) then retry.',
                 '로컬 런타임이 감지되지 않았습니다. 먼저 실행하세요 (예: `ollama pull deepseek-r1`) 후 재시도.'),
              'error');
          }
        })
        .catch(function () { _showModelSelect(false); });
    } else {
      _showModelSelect(false);  // HTTP providers (openai/anthropic/…) → free-text model
    }
  }

  function _setApiKeyPlaceholder(maskedKey) {
    if (!_els.settingsApiKey) return;
    if (maskedKey) {
      _els.settingsApiKey.placeholder = maskedKey;
      return;
    }
    _els.settingsApiKey.placeholder = _els.settingsProvider && _els.settingsProvider.value === 'github'
      ? 'ghp_...'
      : 'sk-...';
  }

  function _settingsPayload() {
    const provider = _els.settingsProvider.value;
    const keyless = _isKeylessProvider(provider);
    const apiKey = _els.settingsApiKey.value.trim();
    const useSelect = _els.settingsModelSelect && !_els.settingsModelSelect.hidden;
    const model = (useSelect ? _els.settingsModelSelect.value : _els.settingsModel.value).trim();
    if (!keyless && !apiKey) {
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

  function _saveSettings(e) {
    if (e) e.preventDefault();
    const body = _settingsPayload();
    if (!body) return false;
    _showSettingsStatus(_t('Saving...', '저장 중...'), '');
    fetch(_apiUrl('/api/chat/config'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
      .then(r => r.json().then(data => ({ ok: r.ok, data })))
      .then(({ ok, data }) => {
        if (ok && data.ok) {
          _showSettingsStatus(_t('Saved.', '저장 완료.'), 'success');
          _configured = true;
          _checkConfig();
          setTimeout(_closeSettingsPanel, 800);
        } else {
          _showSettingsStatus('❌ ' + (data.error || 'Error'), 'error');
        }
      })
      .catch(() => _showSettingsStatus(_t('Connection failed.', '연결 실패.'), 'error'));
    return false;
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
          _showSettingsStatus('❌ ' + ((data && data.error) || 'Error'), 'error');
        }
      })
      .catch(() => _showSettingsStatus(_t('Refresh failed.', '새로고침 실패.'), 'error'));
  }

  function _testSettingsConnection() {
    const body = _settingsPayload();
    if (!body) return;
    _showSettingsStatus(_t('Testing...', '테스트 중...'), '');
    fetch(_apiUrl('/api/chat/config/test'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
      .then(r => r.json())
      .then(data => {
        if (data.ok) {
          _showSettingsStatus(_t('Connected: ', '연결 성공: ') + (data.response || '').slice(0, 80), 'success');
        } else {
          _showSettingsStatus('❌ ' + (data.error || 'Failed'), 'error');
        }
      })
      .catch(() => _showSettingsStatus(_t('Connection failed.', '연결 실패.'), 'error'));
  }

  function _showSettingsStatus(msg, cls) {
    if (!_els.settingsStatus) return;
    _els.settingsStatus.textContent = msg;
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
