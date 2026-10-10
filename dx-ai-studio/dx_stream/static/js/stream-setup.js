/**
 * DX Stream — 설정 페이지
 * 빌드/모델 다운로드 상태 확인, 실행, 로그 폴링
 */
DXStream._setupLogSource = null;
DXStream._setupRunning = false;
DXStream._setupCompletedSteps = {};

// stepId → HTML log element ID 매핑
var _setupLogIds = {
    'stream-deps': 'setup-log-stream-deps',
    'build': 'setup-log-build',
    'download-models': 'setup-log-download',
    'runtime-deps': 'setup-log-runtime',
    'driver': 'setup-log-driver',
    'webrtc-deps': 'setup-log-webrtc-deps',
};
var _setupBadgeIds = {
    'stream-deps': 'stream-deps',
    'build': 'build',
    'download-models': 'download',
    'runtime-deps': 'runtime',
    'driver': 'driver',
    'webrtc-deps': 'webrtc-deps',
};
DXStream._setupFailedSteps = {};

// 뱃지 · 다음 단계 · 막대는 공용 단계 목록이 칠한다 (shared/static/dx-steps.js, 아이콘 체계 단계 2b).
// 여기서는 상태와 한 줄의 짧은 사실만 알린다.
function _setupIco(name) {
    return (typeof window !== 'undefined' && typeof window.DXIcon === 'function') ? window.DXIcon(name) : '';
}
function _setupStep(stepId, state, facts) {
    var root = typeof document !== 'undefined' && document.getElementById('setup-steps');
    if (!root || !window.DXSteps || !stepId) return;
    window.DXSteps.set(root, stepId, state, facts ? { facts: facts } : undefined);
}
// 끝났는지는 서버 상태, 이 화면에서 방금 끝낸 단계, 방금 실패한 단계 순서로 본다.
function _setupStepFrom(stepId, ok, facts) {
    var done = ok || DXStream._setupCompletedSteps[stepId];
    _setupStep(stepId, done ? 'done' : (DXStream._setupFailedSteps[stepId] ? 'failed' : 'todo'), done ? facts : []);
}
function _basename(p) {
    return String(p || '').split('/').filter(Boolean).pop() || '';
}

function _streamSetupVisible() {
    return typeof document === 'undefined' || !document.hidden;
}

function _appendSetupLog(logEl, text) {
    if (!logEl) return;
    var next = String(text || '');
    var prev = logEl._lastSetupLogText || '';
    if (next === prev) return;
    if (prev && next.indexOf(prev) === 0) {
        logEl.insertAdjacentText('beforeend', next.slice(prev.length));
    } else {
        logEl.textContent = next;
    }
    logEl._lastSetupLogText = next;
    logEl.scrollTop = logEl.scrollHeight;
}

var _stepNames = {
    'stream-deps':     { ko: '빌드 도구',    ja: 'ビルドツール',      'zh-CN': '构建工具', 'zh-TW': '建置工具', es: 'Herramientas de compilación', en: 'Build Tools' },
    'build':           { ko: '빌드',         ja: 'ビルド',           'zh-CN': '构建',     'zh-TW': '建置',     es: 'Compilar', en: 'Build' },
    'download-models': { ko: '모델 다운로드', ja: 'モデルダウンロード','zh-CN': '下载模型', 'zh-TW': '下載模型', es: 'Descargar modelos', en: 'Download Models' },
    'runtime-deps':    { ko: '런타임 의존성', ja: 'ランタイム依存関係','zh-CN': '运行时依赖','zh-TW': '執行時期相依性', es: 'Dependencias de tiempo de ejecución', en: 'Runtime Dependencies' },
    'driver':          { ko: '드라이버',     ja: 'ドライバ',         'zh-CN': '驱动程序', 'zh-TW': '驅動程式', es: 'Controlador', en: 'Driver' },
    'webrtc-deps':     { ko: 'WebRTC 의존성', ja: 'WebRTC依存関係',  'zh-CN': 'WebRTC依赖', 'zh-TW': 'WebRTC相依性', es: 'Dependencias de WebRTC', en: 'WebRTC Dependencies' }
};
function _stepLabel(id) {
    var names = _stepNames[id];
    if (!names) return id;
    return names[DXStream.S.lang] || names.en || id;
}

DXStream.setupInit = async function () {
    var status = await DXStream.api('/api/setup/status');
    if (status.error) {
        DXStream.toast(T('Status check failed'), 'error');
        return;
    }
    _updateSetupBadge('build', status.build);
    _updateSetupBadge('download', status['download-models']);
    // A step still running on the server (the page was left, or the language changed — both stop
    // the poll): pick its log and Stop button back up instead of showing an idle step.
    if (status.running && !DXStream._setupPollTimer) _resumeRunningStep(status.running);

    // 모델 다운로드 진행률 표시
    var dl = status['download-models'];
    if (dl) {
        var progressText = DXStream.$('setup-download-text');
        if (progressText) progressText.textContent = dl.installed + '/' + dl.total;
    }

    // runtime/driver 뱃지도 갱신 (상태 API에서 간접 확인)
    var sysStatus = await DXStream.api('/api/status');
    if (!sysStatus.error) {
        var info = sysStatus.system_info || {};
        // stream-deps: 빌드 툴체인(gstreamer 포함) 설치 여부로 간접 판단
        _setupStepFrom('stream-deps', sysStatus.gstreamer && sysStatus.gstreamer.installed,
            [info.gstreamer_version ? 'GStreamer ' + String(info.gstreamer_version).replace(/^GStreamer\s*/i, '') : '']);
        // runtime: gstreamer 설치 여부로 판단
        _setupStepFrom('runtime-deps', sysStatus.gstreamer && sysStatus.gstreamer.installed,
            [sysStatus.gstreamer && sysStatus.gstreamer.plugin ? 'dxstream' : '']);
        // driver: npu 감지 여부로 판단
        var drvOk = DXStream._setupCompletedSteps['driver'] || (sysStatus.npu && sysStatus.npu.ok);
        _setupStepFrom('driver', drvOk,
            ((sysStatus.npu && sysStatus.npu.devices) || []).map(_basename).concat([info.npu_driver_version || '']));
        // webrtc-deps: nice_plugin 여부로 판단
        _setupStepFrom('webrtc-deps', sysStatus.webrtc && sysStatus.webrtc.ok && sysStatus.webrtc.nice_plugin,
            ['gstreamer1.0-nice']);
        if (sysStatus.system_info) {
            var el;
            el = DXStream.$('setup-os-info'); if (el) el.textContent = info.os || '--';
            el = DXStream.$('setup-gst-version'); if (el) el.textContent = info.gstreamer_version || '--';
            el = DXStream.$('setup-npu-driver'); if (el) el.textContent = info.npu_driver_version || '--';
            el = DXStream.$('setup-python-version'); if (el) el.textContent = info.python_version || '--';
        }
        var detailMap = {
            'setup-detail-runtime': sysStatus.gstreamer && sysStatus.gstreamer.installed
                ? DXStream._L('GStreamer 설치됨','GStreamer installed','GStreamerインストール済','GStreamer已安装','GStreamer已安裝','GStreamer instalado')
                : DXStream._L('GStreamer 미설치','GStreamer not installed','GStreamer未インストール','GStreamer未安装','GStreamer未安裝','GStreamer no instalado'),
            'setup-detail-driver': sysStatus.npu && sysStatus.npu.ok
                ? DXStream._L('NPU 감지됨','NPU detected','NPU検出済','NPU已检测','NPU已偵測','NPU detectada')
                : DXStream._L('NPU 미감지','NPU not detected','NPU未検出','NPU未检测','NPU未偵測','NPU no detectada')
        };
        Object.keys(detailMap).forEach(function(id) {
            var detailEl = DXStream.$(id);
            if (detailEl) detailEl.textContent = detailMap[id];
        });
    }

    // 환경 점검도 같이 실행
    DXStream.checkEnvironment();
};

function _updateSetupBadge(id, data) {
    var stepId = id === 'download' ? 'download-models' : id;
    var facts = [];
    if (stepId === 'build' && data && data.path) facts = [_basename(data.path)];
    if (stepId === 'download-models' && data && data.total) facts = [data.installed + '/' + data.total + ' ' + T('files')];
    _setupStepFrom(stepId, data && data.ok, facts);
}
function _markSetupStepDone(stepId) {
    if (!stepId) return;
    DXStream._setupCompletedSteps[stepId] = true;
    delete DXStream._setupFailedSteps[stepId];
    _setupStep(stepId, 'done');
}

// sudo가 필요한 스텝 목록
var _sudoSteps = { 'stream-deps': true, 'build': true, 'webrtc-deps': true, 'runtime-deps': true, 'driver': true };

// POST a setup step and return {ok, data} reading the JSON body regardless of HTTP status
// (the shared api() drops the body on non-2xx, hiding the 'sudo_auth' code).
async function _postSetupBody(stepId, payload) {
    try {
        var r = await fetch(DXStream._base + '/api/setup/' + stepId, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        var data = {};
        try { data = await r.json(); } catch (e) { data = {}; }
        return { ok: r.ok, data: data };
    } catch (e) {
        return { ok: false, data: { error: 'network', message: String(e) } };
    }
}

DXStream.runSetup = async function (stepId) {
    if (DXStream._setupRunning) {
        DXStream.toast(T('Another task is already running'), 'error');
        return;
    }

    var body = {};
    if (stepId === 'build') {
        var cleanEl = DXStream.$('setup-opt-clean');
        var debugEl = DXStream.$('setup-opt-debug');
        if (cleanEl) body.clean = cleanEl.checked;
        if (debugEl) body.debug = debugEl.checked;
    }
    var logId = _setupLogIds[stepId];
    var logEl = logId ? DXStream.$(logId) : null;
    var stopBtn = DXStream.$('setup-stop-btn');

    // POST that reads the JSON body regardless of HTTP status. The shared api() drops the
    // body on non-2xx, so we do our own fetch to see the 'sudo_auth' code (wrong/expired
    // sudo password) and re-prompt instead of leaving the card stuck on "Preparing…".
    async function _postSetup(payload) {
        try {
            var r = await fetch(DXStream._base + '/api/setup/' + stepId, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            var data = {};
            try { data = await r.json(); } catch (e) { data = {}; }
            return { ok: r.ok, data: data };
        } catch (e) {
            return { ok: false, data: { error: 'network', message: String(e) } };
        }
    }

    function _showPreparing() {
        if (logEl) { logEl.style.display = ''; logEl.textContent = T('Preparing…') + '\n'; logEl._lastSetupLogText = ''; }
        DXStream._setupRunning = true;
        DXStream._lastSetupExitCode = null;
        if (stopBtn) stopBtn.style.display = '';
    }
    function _resetRun() {
        DXStream._setupRunning = false;
        if (stopBtn) stopBtn.style.display = 'none';
    }

    var result;
    if (_sudoSteps[stepId]) {
        var authFailed = false;
        while (true) {
            var desc = authFailed
                ? DXStream._L('비밀번호가 올바르지 않습니다. 다시 입력하세요.','Incorrect password. Please try again.','パスワードが正しくありません。もう一度入力してください。','密码不正确，请重新输入。','密碼不正確，請重新輸入。','Contraseña incorrecta. Inténtelo de nuevo.')
                : DXStream._L('이 작업은 관리자 권한이 필요합니다.','This operation requires administrator privileges.','この操作には管理者権限が必要です。','此操作需要管理员权限。','此操作需要管理員權限。','Esta operación requiere privilegios de administrador.');
            var pw = await DXStream.inputModal(
                DXStream._L('sudo 인증','sudo Authentication','sudo認証','sudo认证','sudo認證','Autenticación sudo'),
                { description: desc, type: 'password',
                  placeholder: DXStream._L('비밀번호 입력','Enter password','パスワード入力','输入密码','輸入密碼','Introduzca la contraseña') }
            );
            if (!pw) {
                DXStream.toast(T('Cancelled'), 'info');
                return;
            }
            body.password = pw;
            _showPreparing();
            result = await _postSetup(body);
            if (!result.ok && result.data && result.data.error === 'sudo_auth') {
                _resetRun();
                if (logEl) { logEl.textContent = ''; logEl.style.display = 'none'; }
                authFailed = true;
                continue;  // wrong sudo password → re-prompt
            }
            break;
        }
    } else {
        _showPreparing();
        result = await _postSetup(body);
    }

    if (!result.ok) {
        _resetRun();
        var msg = (result.data && (result.data.message || result.data.error)) || T('failed');
        DXStream.toast(T('Run failed: ') + msg, 'error');
        return;
    }
    DXStream.toast(_stepLabel(stepId) + ' ' + T('started'), 'info');

    // 로그 폴링 시작
    _startLogPoll(stepId, logEl);
};

function _resumeRunningStep(stepId) {
    var logId = _setupLogIds[stepId];
    var logEl = logId ? DXStream.$(logId) : null;
    DXStream._setupRunning = true;
    var stopBtn = DXStream.$('setup-stop-btn');
    if (stopBtn) stopBtn.style.display = '';
    _startLogPoll(stepId, logEl);
}

function _startLogPoll(stepId, logEl) {
    if (DXStream._setupPollTimer) clearInterval(DXStream._setupPollTimer);
    // 로그는 비어 있으면 숨겨 두고, 실행이 시작되면 보인다 (Run All 도 이 길로 온다).
    if (logEl) logEl.style.display = '';
    delete DXStream._setupFailedSteps[stepId];
    _setupStep(stepId, 'running');

    DXStream._setupPollTimer = setInterval(async function () {
        if (!_streamSetupVisible()) return;
        var r = await DXStream.api('/api/setup/log?step=' + encodeURIComponent(stepId));
        if (r.log && logEl) {
            _appendSetupLog(logEl, r.log);
        }
        if (stepId === 'download-models' && r.log) {
            var progBar = DXStream.$('setup-download-progress');
            var progFill = DXStream.$('setup-download-fill');
            var progText = DXStream.$('setup-download-text');
            var match = r.log.match(/\[PROGRESS\]\s*(\d+)\/(\d+)/);
            if (match && progBar) {
                progBar.style.display = '';
                var pct = Math.round(parseInt(match[1], 10) / parseInt(match[2], 10) * 100);
                if (progFill) progFill.style.width = pct + '%';
                if (progText) progText.textContent = pct + '%';
            }
            if (r.done && progBar) progBar.style.display = 'none';
        }
        if (r.done) {
            clearInterval(DXStream._setupPollTimer);
            DXStream._setupPollTimer = null;
            DXStream._setupRunning = false;
            DXStream._lastSetupExitCode = r.exit_code;
            var stopBtn = DXStream.$('setup-stop-btn');
            if (stopBtn) stopBtn.style.display = 'none';
            if (r.exit_code === 0) {
                DXStream.toast(_stepLabel(stepId) + ' ' + T('completed'), 'success');
                _markSetupStepDone(stepId);
            } else {
                DXStream.toast(_stepLabel(stepId) + ' ' + T('Failed') + ' (exit ' + r.exit_code + ')', 'error');
                DXStream._setupFailedSteps[stepId] = true;
                _setupStep(stepId, 'failed');
            }
            // 설정 상태 + 대시보드 갱신
            DXStream.setupInit();
            // 대시보드 status polling 재시작
            if (typeof DXStream.startStatusPolling === 'function') {
                DXStream.startStatusPolling();
            }
        }
    }, 1500);
}

DXStream.clearLog = function (logKey) {
    var logEl = DXStream.$('setup-log-' + logKey);
    if (logEl) { logEl.textContent = ''; logEl._lastSetupLogText = ''; logEl.style.display = 'none'; }
};

DXStream.retrySetup = function (stepId) {
    DXStream.clearLog(stepId);
    DXStream.runSetup(stepId);
};

var _cachedSudoPwd = null;

DXStream._setupCleanup = function() {
    _cachedSudoPwd = null;
    DXStream._setupRunning = false;
    var stopBtn = DXStream.$('setup-stop-btn');
    if (stopBtn) stopBtn.style.display = 'none';
};

DXStream.setupRunAll = async function() {
    var btn = DXStream.$('setup-run-all');
    var prog = DXStream.$('setup-run-all-progress');
    var stopBtn = DXStream.$('setup-stop-btn');
    if (DXStream._setupRunning) {
        DXStream.toast(DXStream._L('다른 작업이 이미 실행 중입니다','Another task is already running','別のタスクが実行中です','另一个任务正在运行','另一個任務正在執行','Ya hay otra tarea en ejecución'), 'warn');
        return;
    }

    var steps = ['stream-deps', 'runtime-deps', 'driver', 'build', 'download-models', 'webrtc-deps'];
    // "Set up the rest (n)" — 끝난 단계는 다시 돌리지 않는다 (dx_app Run All 과 같은 규칙).
    steps = steps.filter(function (id) {
        var li = document.querySelector('#setup-steps .dx-step[data-step="' + id + '"]');
        return !li || li.dataset.state !== 'done';
    });
    if (!steps.length) {
        DXStream.toast(DXStream._L('이미 모두 설치되어 있습니다','Everything is already installed','すべてインストール済みです','已全部安装','已全部安裝','Todo está ya instalado'), 'ok');
        return;
    }
    if (btn) btn.disabled = true;
    if (stopBtn) stopBtn.style.display = '';

    _cachedSudoPwd = await DXStream.inputModal(
        DXStream._L('sudo 인증','sudo Authentication','sudo認証','sudo认证','sudo認證','Autenticación sudo'),
        { description: DXStream._L('Run All에 관리자 권한이 필요합니다.','Run All requires administrator privileges.','Run Allには管理者権限が必要です。','全部执行需要管理员权限。','全部執行需要管理員權限。','Configurar todo requiere privilegios de administrador.'),
          type: 'password', placeholder: DXStream._L('비밀번호 입력','Enter password','パスワード入力','输入密码','輸入密碼','Introduzca la contraseña') }
    );
    if (!_cachedSudoPwd) {
        if (btn) btn.disabled = false;
        if (stopBtn) stopBtn.style.display = 'none';
        return;
    }

    var i;
    for (i = 0; i < steps.length; i++) {
        var stepId = steps[i];
        if (prog) {
            prog.style.display = '';
            prog.textContent = (i + 1) + '/' + steps.length + ' ' + (_stepNames[stepId] ? _stepLabel(stepId) : stepId);
        }

        var body = { password: _cachedSudoPwd };
        if (stepId === 'build') {
            var c = DXStream.$('setup-opt-clean'); if (c) body.clean = c.checked;
            var d = DXStream.$('setup-opt-debug'); if (d) body.debug = d.checked;
        }
        var logEl = DXStream.$(_setupLogIds[stepId]);
        var result, cancelled = false;
        while (true) {
            DXStream._setupRunning = true;
            DXStream._lastSetupExitCode = null;
            result = await _postSetupBody(stepId, body);
            if (!result.ok && result.data && result.data.error === 'sudo_auth') {
                // wrong/expired sudo password → re-prompt, update the cached one, retry this step
                DXStream._setupRunning = false;
                var npw = await DXStream.inputModal(
                    DXStream._L('sudo 인증','sudo Authentication','sudo認証','sudo认证','sudo認證','Autenticación sudo'),
                    { description: DXStream._L('비밀번호가 올바르지 않습니다. 다시 입력하세요.','Incorrect password. Please try again.','パスワードが正しくありません。もう一度入力してください。','密码不正确，请重新输入。','密碼不正確，請重新輸入。','Contraseña incorrecta. Inténtelo de nuevo.'),
                      type: 'password', placeholder: DXStream._L('비밀번호 입력','Enter password','パスワード入力','输入密码','輸入密碼','Introduzca la contraseña') }
                );
                if (!npw) { cancelled = true; break; }
                _cachedSudoPwd = npw;
                body.password = npw;
                continue;
            }
            break;
        }
        if (cancelled) {
            DXStream._setupRunning = false;
            DXStream.toast(DXStream._L('취소됨','Cancelled','キャンセルしました','已取消','已取消','Cancelado'), 'info');
            break;
        }
        if (!result.ok) {
            DXStream._setupRunning = false;
            DXStream._lastSetupExitCode = 1;
            var _m = (result.data && (result.data.message || result.data.error)) || 'failed';
            DXStream.toast(DXStream._L('실행 실패: ','Run failed: ','実行失敗: ','运行失败: ','執行失敗: ','Error al ejecutar: ') + _m, 'err');
            break;
        }
        if (logEl) _startLogPoll(stepId, logEl);
        while (DXStream._setupRunning) {
            await new Promise(function(resolve) { setTimeout(resolve, 1500); });
        }
        if (DXStream._lastSetupExitCode !== 0) break;
    }

    _cachedSudoPwd = null;
    if (btn) btn.disabled = false;
    if (prog) prog.style.display = 'none';
    if (stopBtn) stopBtn.style.display = 'none';
    if (i === steps.length) DXStream.toast(DXStream._L('전체 실행 완료!','Run All complete!','全実行完了!','全部执行完成!','全部執行完成!','¡Todo completado!'), 'ok');
    DXStream.setupInit();
};

DXStream.setupStop = async function() {
    try {
        var r = await DXStream.postJ('/api/setup/stop', {});
        if (r.ok) DXStream.toast(DXStream._L('중단됨','Stopped','中断済','已中断','已中斷','Detenido'), 'warn');
        else DXStream.toast(DXStream._L('중단 실패','Stop failed','中断失敗','中断失败','中斷失敗','No se pudo detener'), 'err');
    } catch (e) {
        DXStream.toast(DXStream._L('중단 오류: ','Stop error: ','中断エラー: ','中断错误: ','中斷錯誤: ','Error al detener: ') + e.message, 'err');
    }
};

DXStream.runDiagnostics = async function() {
    var btn = DXStream.$('stream-diag-run-btn');
    var sum = DXStream.$('stream-diag-summary');
    var res = DXStream.$('stream-diag-results');
    if (btn) { btn.disabled = true; btn.innerHTML = _setupIco('spinner') + ' <span>' + T('Running…') + '</span>'; }
    if (res) res.innerHTML = '<p class="txt-dim">' + DXStream._L('진단 실행 중…','Running diagnostics…','診断実行中…','诊断运行中…','診斷執行中…','Ejecutando diagnóstico…') + '</p>';
    try {
        var r = await DXStream.api('/api/diagnostics');
        var lang = (typeof DXI18n !== 'undefined' ? DXI18n.lang : 'en');
        var langKey = lang.replace('-', '');
        var html = '';
        r.checks.forEach(function(c) {
            var label = typeof c.label === 'object' ? (c.label[langKey] || c.label.en) : c.label;
            var severity = c.severity === 'advisory' ? 'advisory' : 'blocker';
            var cardClass = c.ok ? 'diag-card-ok' : (severity === 'advisory' ? 'diag-card-warn' : 'diag-card-fail');
            var statusText = c.ok ? 'OK' : (severity === 'advisory' ? 'WARN' : 'FAIL');
            var fix = '';
            if (!c.ok && c.fix) {
                var fixText = typeof c.fix === 'object' ? (c.fix[langKey] || c.fix.en) : c.fix;
                fix = '<div class="diag-card-fix">' + _setupIco('info') + ' ' + DXStream.escHtml(fixText) + '</div>';
            }
            html += '<div class="diag-card ' + cardClass + '">'
                + '<div class="diag-card-title">' + _setupIco(c.ok ? 'check' : (severity === 'advisory' ? 'alert' : 'x')) + ' ' + statusText + ' ' + DXStream.escHtml(label) + '</div>'
                + '<div class="diag-card-detail">' + DXStream.escHtml(c.detail) + '</div>'
                + fix + '</div>';
        });
        if (res) res.innerHTML = html;
        if (sum) {
            var severitySummary = r.severity_summary || {};
            var blockerFailures = Number(severitySummary.blockers) || 0;
            var advisoryFailures = Number(severitySummary.advisories) || 0;
            var passedCount = Number(r.passed) || 0;
            var totalCount = Number(r.total) || 0;
            var runtimeReady = r.runtime_ready === true;
            var summaryClass = r.all_ok ? 'diag-pass' : (runtimeReady ? 'diag-warn' : 'diag-fail');
            var summaryText = r.all_ok ? 'OK' : (runtimeReady
                ? DXStream._L('경고와 함께 준비됨','READY WITH WARNINGS','警告付きで準備完了','就绪（有警告）','就緒（有警告）','LISTO CON ADVERTENCIAS')
                : DXStream._L('실패','FAIL','失敗','失败','失敗','FALLO'));
            var bf = blockerFailures, af = advisoryFailures;
            sum.style.display = '';
            sum.innerHTML = '<div class="diag-summary-bar ' + summaryClass + '">'
                + DXStream.escHtml(summaryText) + ' <strong>' + passedCount + '/' + totalCount + '</strong> '
                + DXStream._L('검사 통과','checks passed','検査合格','检查通过','檢查通過','comprobaciones superadas')
                + ' · ' + DXStream._L('실패 ' + bf, bf + (bf === 1 ? ' failure' : ' failures'), '失敗 ' + bf + ' 件', bf + ' 个失败', bf + ' 個失敗', bf + (bf === 1 ? ' fallo' : ' fallos'))
                + ' · ' + DXStream._L('경고 ' + af, af + (af === 1 ? ' warning' : ' warnings'), '警告 ' + af + ' 件', af + ' 个警告', af + ' 個警告', af + (af === 1 ? ' advertencia' : ' advertencias'))
                + '</div>';
        }
        if (r.all_ok) DXStream.toast(DXStream._L('모든 진단 통과!','All diagnostics passed!','すべての診断に合格!','所有诊断通过!','所有診斷通過!','¡Todos los diagnósticos superados!'), 'ok');
        else if (r.runtime_ready) DXStream.toast(DXStream._L('경고와 함께 실행 준비됨','Ready with warnings','警告付きで準備完了','已准备就绪，但有警告','已準備就緒，但有警告','Listo con advertencias'), 'warn');
        else DXStream.toast(DXStream._L('차단 검사 실패','Blocking checks failed','ブロッカー検査が失敗','阻塞检查失败','阻擋檢查失敗','Fallaron comprobaciones obligatorias'), 'err');
    } catch (e) {
        DXStream.toast(DXStream._L('진단 오류: ','Diagnostics error: ','診断エラー: ','诊断错误: ','診斷錯誤: ','Error de diagnóstico: ') + e.message, 'err');
    }
    if (btn) {
        btn.disabled = false;
        btn.innerHTML = _setupIco('play') + ' <span data-i18n="Run diagnostics">' + T('Run diagnostics') + '</span>';
    }
};

DXStream.checkEnvironment = async function () {
    var tbody = DXStream.$('setup-env-tbody');
    if (!tbody) return;

    var status = await DXStream.api('/api/status');
    if (status.error) return;

    _setEnvRow('gst', status.gstreamer.ok,
        status.gstreamer.installed
            ? (status.gstreamer.plugin ? T('Plugin OK') : T('No plugin'))
            : T('Not installed'));
    _setEnvRow('npu', status.npu.ok,
        status.npu.ok ? status.npu.devices.join(', ') : T('Not detected'));
    if (status.build) {
        _setEnvRow('plugin', status.build.ok,
            status.build.ok ? (status.build.path || T('OK')) : T('Not built'));
    }
    _setEnvRow('model', status.models.ok,
        status.models.installed + '/' + status.models.total + ' ' + T('files'));
    _setEnvRow('video', status.videos.ok,
        status.videos.count + ' ' + T('files'));
    // WebRTC — 서버 nice_plugin 상태 반영
    if (status.webrtc) {
        var wOk = status.webrtc.ok && status.webrtc.nice_plugin;
        _setEnvRow('webrtc', wOk,
            wOk ? 'gstreamer1.0-nice ' + T('OK') : T('gstreamer1.0-nice not installed'));
    } else {
        _setEnvRow('webrtc', false, T('Not checked'));
    }
};

function _setEnvRow(key, ok, detail) {
    var statusEl = DXStream.$('env-' + key + '-status');
    var detailEl = DXStream.$('env-' + key + '-detail');
    if (statusEl) {
        // 단계 목록의 상태 표시와 같은 모양 (아이콘 + 말).
        statusEl.className = 'dx-step-state ' + (ok ? 'is-done' : 'is-todo');
        statusEl.innerHTML = _setupIco(ok ? 'check' : 'alert') + '<span>' + T(ok ? 'Ready' : 'Needs setup') + '</span>';
    }
    if (detailEl) detailEl.textContent = detail;
}
if (typeof registerStreamLangRefresher === 'function') {
  registerStreamLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined' && DXStream.S && DXStream.S.currentPage && typeof DXStream.nav === 'function') {
      DXStream.nav(DXStream.S.currentPage);
    }
  });
}
