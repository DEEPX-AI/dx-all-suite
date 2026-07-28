(function() {
    'use strict';
    DXStream.custom = {};

    DXStream.custom.loadLibraries = function() {
        fetch('/api/custom-library').then(function(r) { return r.json(); })
        .then(function(libs) {
            var grid = DXStream.$('custom-lib-grid');
            if (!grid) return;
            if (!libs.length) {
                grid.innerHTML = '<p class="txt-dim">' + T('No libraries found') + '</p>';
                return;
            }
            grid.innerHTML = libs.map(function(lib) {
                return '<div class="card">' +
                    '<div class="card-title">' + lib.name + '</div>' +
                    '<span class="card-badge">' + (lib.built ? '✅ Built' : '⚠️ Not built') + '</span>' +
                    (lib.has_meson && !lib.built ?
                        '<button class="btn btn-sm mt4" onclick="DXStream.custom.build(\'' + lib.name + '\')">' +
                        T('Build') + '</button>' : '') +
                '</div>';
            }).join('');
        });
    };

    DXStream.custom.upload = function() {
        var name = DXStream.$('custom-lib-name').value.trim();
        var fileInput = DXStream.$('custom-lib-files');
        if (!name || !fileInput.files.length) {
            alert(T('Enter name and select files'));
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
                    fetch('/api/custom-library/upload', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ name: name, files: files })
                    }).then(function(r) { return r.json(); })
                    .then(function(data) {
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
        var setStatus = function(msg) { if (statusEl) statusEl.textContent = msg; };
        if (!input || !input.files.length) { setStatus(T('Select a .dxnn file first')); return; }
        var f = input.files[0];
        if (!/\.dxnn$/i.test(f.name)) { setStatus(T('Model file must be a .dxnn binary')); return; }
        var fd = new FormData();
        fd.append('model', f, f.name);
        setStatus(T('Uploading...'));
        fetch('/api/models/upload', { method: 'POST', body: fd })
        .then(function(r) { return r.json().then(function(d) { return { ok: r.ok, d: d }; }); })
        .then(function(res) {
            if (!res.ok || !res.d.uploaded) {
                setStatus('❌ ' + ((res.d && res.d.error) || T('Upload failed')));
                return;
            }
            setStatus('✅ ' + res.d.name);
            // refresh asset lists so the model-path dropdown includes the new model
            if (typeof DXStream.api === 'function') {
                DXStream.api('/api/pipeline/assets').then(function(a) {
                    if (a && !a.error) DXStream._pipeAssets = a;
                });
            }
        })
        .catch(function(e) { setStatus('❌ ' + e.message); });
    };

    DXStream.custom.build = function(name) {
        var logCard = DXStream.$('custom-build-log-card');
        var logPre = DXStream.$('custom-build-log');
        if (logCard) logCard.style.display = '';
        if (logPre) logPre.textContent = T('Starting build...');

        fetch('/api/custom-library/' + name + '/build', { method: 'POST' })
        .then(function(r) { return r.json(); })
        .then(function() { DXStream.custom.pollBuild(); });
    };

    DXStream.custom.pollBuild = function() {
        fetch('/api/custom-library/build-log')
        .then(function(r) { return r.json(); })
        .then(function(data) {
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
