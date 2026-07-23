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
