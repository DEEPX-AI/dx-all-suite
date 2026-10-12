(function() {
    'use strict';
    DXStream.custom = {};

    function _esc(v) { return (DXStream.escHtml ? DXStream.escHtml(v) : String(v)); }
    function _srv(msg) { return (window.translateServerError ? window.translateServerError(msg) : msg); }

    // Library names come from folder names on disk — escaped, and the Build button carries the name
    // in data-lib (a name with a quote broke the old inline onclick; markup in it was rendered).
    DXStream.custom.loadLibraries = function() {
        DXStream.api('/api/custom-library').then(function(libs) {
            var grid = DXStream.$('custom-lib-grid');
            if (!grid) return;
            if (!Array.isArray(libs)) {
                grid.innerHTML = '<p class="txt-dim">' + _esc(_srv((libs && libs.error) || '')) + '</p>';
                return;
            }
            if (!libs.length) {
                grid.innerHTML = '<p class="txt-dim">' + T('No libraries found') + '</p>';
                return;
            }
            grid.innerHTML = libs.map(function(lib) {
                return '<div class="card">' +
                    '<div class="card-title">' + _esc(lib.name) + '</div>' +
                    '<span class="card-badge">' + (lib.built ? ((typeof DXIcon === 'function') ? DXIcon('check') : '') + ' ' + T('Built') : ((typeof DXIcon === 'function') ? DXIcon('alert') : '') + ' ' + T('Not built')) + '</span>' +
                    (lib.has_meson && !lib.built ?
                        '<button class="btn btn-sm mt4" data-lib="' + _esc(lib.name) + '">' + T('Build') + '</button>' : '') +
                '</div>';
            }).join('');
            grid.querySelectorAll('button[data-lib]').forEach(function(b) {
                b.addEventListener('click', function() { DXStream.custom.build(b.dataset.lib); });
            });
        });
    };
    // Tab switch refreshes the list (it was loaded once, when the script loaded).
    DXStream.customInit = function() { DXStream.custom.loadLibraries(); };

    DXStream.custom.upload = function() {
        var name = DXStream.$('custom-lib-name').value.trim();
        var fileInput = DXStream.$('custom-lib-files');
        if (!name || !fileInput.files.length) {
            DXStream.toast(T('Enter name and select files'), 'warn');
            return;
        }
        var files = {};
        var remaining = fileInput.files.length;
        Array.from(fileInput.files).forEach(function(f) {
            var reader = new FileReader();
            reader.onload = function(e) {
                files[f.name] = btoa(e.target.result);
                remaining--;
                if (remaining === 0) {
                    DXStream.postJ('/api/custom-library/upload', { name: name, files: files }).then(function(data) {
                        // A refused upload (binary file, bad name) must not start a build.
                        if (!data || data.error) {
                            DXStream.toast(T('Upload failed') + ': ' + _srv((data && data.error) || ''), 'error');
                            return;
                        }
                        DXStream.custom.loadLibraries();
                        DXStream.custom.build(name);
                    });
                }
            };
            reader.readAsBinaryString(f);
        });
    };

    // Upload a user .dxnn model → MODELS_DIR, then refresh pipeline assets so it appears in
    // DxInfer's model-path dropdown. Dedicated path so users stop mis-dropping .dxnn into the
    // (text-only) custom-library uploader ("DXNN file upload fails").
    DXStream.uploadModel = function() {
        var input = DXStream.$('model-upload-file');
        var statusEl = DXStream.$('model-upload-status');
        var setStatus = function(msg, icon) { if (!statusEl) return; if (icon && typeof DXIcon === 'function') DXIcon.label(statusEl, icon, msg); else statusEl.textContent = msg; };
        if (!input || !input.files.length) { setStatus(T('Select a .dxnn file first')); return; }
        var f = input.files[0];
        if (!/\.dxnn$/i.test(f.name)) { setStatus(T('Model file must be a .dxnn binary')); return; }
        var fd = new FormData();
        fd.append('model', f, f.name);
        setStatus(T('Uploading...'));
        fetch((DXStream._base || '') + '/api/models/upload', { method: 'POST', body: fd })
        .then(function(r) { return r.json().then(function(d) { return { ok: r.ok, d: d }; }); })
        .then(function(res) {
            if (!res.ok || !res.d.uploaded) {
                setStatus(T('Upload failed') + ': ' + _srv((res.d && (res.d.message || res.d.error)) || ''), 'x');   // the code (bad_request) told users nothing
                return;
            }
            setStatus(res.d.name, 'check');
            // refresh asset lists so the model-path dropdown includes the new model
            if (typeof DXStream.api === 'function') {
                DXStream.api('/api/pipeline/assets').then(function(a) {
                    if (a && !a.error) DXStream._pipeAssets = a;
                });
            }
        })
        .catch(function(e) { setStatus(e.message, 'x'); });
    };

    // `sudo meson install` needs a password on most hosts — asked here like Stream Setup does.
    DXStream.custom.build = async function(name) {
        var logCard = DXStream.$('custom-build-log-card');
        var logPre = DXStream.$('custom-build-log');
        if (logCard) logCard.style.display = '';
        if (logPre) logPre.textContent = T('Starting build...');
        var body = {};
        var res = await DXStream.postJ('/api/custom-library/' + encodeURIComponent(name) + '/build', body);
        var wrong = false;
        while (res && (res.error_code === 'need_sudo' || res.error_code === 'sudo_auth')) {
            wrong = wrong || res.error_code === 'sudo_auth';
            var pw = await DXStream.inputModal(
                DXStream._L('sudo 인증','sudo Authentication','sudo認証','sudo认证','sudo認證','Autenticación sudo'),
                { description: wrong
                    ? DXStream._L('비밀번호가 올바르지 않습니다. 다시 입력하세요.','Incorrect password. Please try again.','パスワードが正しくありません。もう一度入力してください。','密码不正确，请重新输入。','密碼不正確，請重新輸入。','Contraseña incorrecta. Inténtelo de nuevo.')
                    : DXStream._L('이 작업은 관리자 권한이 필요합니다.','This operation requires administrator privileges.','この操作には管理者権限が必要です。','此操作需要管理员权限。','此操作需要管理員權限。','Esta operación requiere privilegios de administrador.'),
                  type: 'password',
                  placeholder: DXStream._L('비밀번호 입력','Enter password','パスワード入力','输入密码','輸入密碼','Introduzca la contraseña') });
            if (!pw) {
                if (logPre) logPre.textContent = T('Cancelled');
                return;
            }
            body.password = pw;
            res = await DXStream.postJ('/api/custom-library/' + encodeURIComponent(name) + '/build', body);
            wrong = true;
        }
        if (!res || res.error) {
            // A refused build never started; do not poll a stale log.
            var msg = _srv((res && res.error) || '');
            if (logPre) logPre.textContent = msg;
            DXStream.toast(T('Build failed') + ': ' + msg, 'error');
            return;
        }
        DXStream.custom.pollBuild();
    };

    DXStream.custom.pollBuild = function() {
        DXStream.api('/api/custom-library/build-log').then(function(data) {
            var logPre = DXStream.$('custom-build-log');
            if (logPre) logPre.textContent = data.log || '';
            if (!data.done) {
                setTimeout(DXStream.custom.pollBuild, 1000);
            } else {
                DXStream.custom.loadLibraries();
            }
        });
    };

    DXStream.custom.loadLibraries();
})();
if (typeof registerStreamLangRefresher === 'function') {
  registerStreamLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined' && DXStream.S && DXStream.S.currentPage && typeof DXStream.nav === 'function') {
      DXStream.nav(DXStream.S.currentPage);
    }
  });
}
