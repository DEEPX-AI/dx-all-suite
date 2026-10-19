/**
 * DX Stream — dashboard page
 * Polls system status every 5 s and applies i18n
 */
DXStream.dashboardInit = function () {
    _fetchStatus();
    if (!DXStream._statusTimer) {
        DXStream._statusTimer = setInterval(_fetchStatus, 5000);
    }
};

function _dashboardVisible() {
    return typeof document === 'undefined' || !document.hidden;
}

async function _fetchStatus() {
    if (!_dashboardVisible()) return;
    var responses = await Promise.all([
        DXStream.api('/api/status'),
        DXStream.api('/api/pipeline/status'),
    ]);
    var data = responses[0];
    var pipeResp = responses[1];
    if (data.error) {
        _updateStat('npu', false, T('Status check failed'));
        return;
    }

    _updateStat('npu', data.npu.ok,
        data.npu.ok
            ? data.npu.devices.length + ' ' + T('device(s)')
            : T('Not detected'));
    _updateStat('gstreamer', data.gstreamer.ok,
        data.gstreamer.installed
            ? (data.gstreamer.plugin ? T('Plugin OK') : T('No plugin'))
            : T('Not installed'));
    _updateStat('models', data.models.ok,
        data.models.installed + '/' + data.models.total);
    _updateStat('videos', data.videos.ok,
        data.videos.count + ' ' + T('files'));

    if (data.build) {
        _updateStat('build', data.build.ok,
            data.build.ok ? T('Built') : T('Not built'));
    }

    _updatePipelineBadge(pipeResp);
    _renderPipelineOverview(pipeResp);
    _setPerfPolling(!!(pipeResp && pipeResp.running));
}

/* ── The running pipeline and its numbers ──
   /api/status carries no perf fields, so the numbers come from elsewhere:
   FPS is the frame-count delta from /api/stream/stats (MJPEG · fMP4 — WebRTC is received by the browser,
   so it shows on the Demo page), NPU usage from DX Monitor (/dx_monitor/api/hw_status, launcher only).
   There is no latency row because nothing measures it. */
var _perfTimer = null;
var _perfPrev = null;
var _perfRunKey = null;
var _demoNames = null;

function _demoName(id) {
    if (_demoNames === null) {
        _demoNames = {};
        DXStream.api('/api/demos').then(function (r) {
            var list = (r && (r.demos || r)) || [];
            if (Array.isArray(list)) list.forEach(function (d) { _demoNames[d.id] = d; });
            var box = DXStream.$('pipeline-overview');
            if (box) box.dataset.state = '';
            _fetchStatus();
        });
    }
    var d = _demoNames[id];
    if (!d) return 'Demo ' + id;
    var lang = (window.DXI18n && DXI18n.lang) || 'en';
    return d['name_' + lang.replace('-', '_')] || d['name_' + lang] || d.name_en || d.name || ('Demo ' + id);
}

function _renderPipelineOverview(data) {
    var box = DXStream.$('pipeline-overview');
    if (!box) return;
    var lang = (window.DXI18n && DXI18n.lang) || 'en';
    var running = !!(data && data.running);
    var key = running ? [data.pipeline_id, data.demo_id, data.output_mode, lang].join('|') : 'idle|' + lang;
    if (box.dataset.state === key) return;
    box.dataset.state = key;
    var esc = DXStream.escHtml || function (s) { return String(s); };
    if (!running) {
        box.innerHTML = '<div class="pipeline-placeholder"><span class="txt-dim">' +
            esc(T('No active pipeline — run a demo or build a pipeline')) + '</span></div>';
        return;
    }
    var name = data.demo_id != null ? _demoName(data.demo_id) : T('Custom pipeline');
    var mode = { webrtc: 'WebRTC', mjpeg: 'MJPEG', fmp4: 'fMP4' }[data.output_mode] || '';
    var target = data.demo_id != null ? 'demo' : 'pipeline';
    box.innerHTML = '<div class="pipe-live">' +
        '<span class="pipe-live-dot" aria-hidden="true"></span>' +
        '<div class="pipe-live-text"><div class="pipe-live-name">' + esc(name) + '</div>' +
        (mode ? '<div class="txt-dim txt-sm">' + esc(mode) + '</div>' : '') + '</div>' +
        '<button type="button" class="btn btn-sm" onclick="DXStream.nav(\'' + target + '\')">' +
        esc(target === 'demo' ? T('Open Demo Launcher') : T('Open Pipeline Builder')) + '</button></div>';
}

function _setPerfPolling(on) {
    if (on && !_perfTimer) {
        _perfPrev = null;
        _perfTimer = setInterval(_perfTick, 1000);
        _perfTick();
    } else if (!on && _perfTimer) {
        clearInterval(_perfTimer);
        _perfTimer = null;
        _perfPrev = null;
    }
}

function _avgUtilization(hw) {
    var vals = [];
    ((hw && hw.npus) || []).forEach(function (n) {
        (n.utilization || []).forEach(function (u) { if (typeof u === 'number' && u >= 0) vals.push(u); });
    });
    if (!vals.length) return null;
    return vals.reduce(function (a, b) { return a + b; }, 0) / vals.length;
}

function _perfTick() {
    if (DXStream.S.currentPage !== 'dashboard') { _setPerfPolling(false); return; }
    if (!_dashboardVisible()) return;
    Promise.all([
        DXStream.api('/api/stream/stats'),
        fetch('/dx_monitor/api/hw_status', { cache: 'no-store', credentials: 'same-origin' })
            .then(function (r) { return r.ok ? r.json() : null; })
            .catch(function () { return null; })
    ]).then(function (rs) {
        var stats = rs[0] || {};
        var now = Date.now();
        var fps = null;
        if ((stats.mode === 'mjpeg' || stats.mode === 'fmp4') && typeof stats.frames === 'number') {
            if (_perfPrev && stats.frames >= _perfPrev.frames && now > _perfPrev.t) {
                fps = (stats.frames - _perfPrev.frames) * 1000 / (now - _perfPrev.t);
            }
            _perfPrev = { frames: stats.frames, t: now };
        }
        _updatePerfTable({ fps: fps, npu: _avgUtilization(rs[1]), mode: stats.mode });
    });
}

DXStream.updatePipelineBadge = function (data) { _updatePipelineBadge(data); };
function _updatePipelineBadge(data) {
    var badge = DXStream.$('pipeline-status');
    if (!badge) return;
    if (data && data.running) {
        _setLabelIfChanged(badge, 'play', T('Running'));
        _setClassIfChanged(badge, 'status-pill pill-running');
    } else {
        _setTextIfChanged(badge, T('Idle'));
        _setClassIfChanged(badge, 'status-pill pill-idle');
    }
}

// Rewrite icon + text only when they change, so each poll does not churn the DOM.
function _setLabelIfChanged(el, icon, text) {
    var key = icon + '|' + text;
    if (el.dataset.dxLabel === key) return;
    el.dataset.dxLabel = key;
    if (typeof DXIcon === 'function' && DXIcon.label) DXIcon.label(el, icon, text);
    else el.textContent = text;
}

function _setTextIfChanged(el, text) {
    if (el && el.textContent !== text) el.textContent = text;
}

function _setClassIfChanged(el, className) {
    if (el && el.className !== className) el.className = className;
}

function _updateStat(id, ok, text) {
    var el = DXStream.$('stat-' + id);
    if (!el) return;
    var nextClass = 'stat ' + (ok ? 'stat-ok' : 'stat-warn');
    _setClassIfChanged(el, nextClass);
    var val = el.querySelector('.stat-value');
    if (val) _setTextIfChanged(val, text);
    var icon = el.querySelector('.stat-icon');
    if (icon) _setLabelIfChanged(icon, ok ? 'check' : 'alert', '');
}

if (typeof document !== 'undefined') {
    document.addEventListener('visibilitychange', function () {
        if (_dashboardVisible()) _fetchStatus();
    });
}

// Quick Launch: open the demo on the stage once the list has loaded, then start it — only if it
// can run. Starting before the list (and the stage) exists, or without the availability check,
// turns a demo that needs setup into a raw 424.
DXStream.quickLaunchDemo = async function (demoId) {
    DXStream._allDemos = null;            // judge on the list this visit loads, not an old one
    DXStream.nav('demo');
    for (var i = 0; i < 80 && !(DXStream._demoCtl && DXStream._allDemos); i++) {
        await new Promise(function (r) { setTimeout(r, 100); });
    }
    var d = (DXStream._allDemos || []).find(function (x) { return x.id === demoId; });
    if (DXStream._demoCtl) DXStream._demoCtl.select(String(demoId));
    if (!d) return;
    if (!d.available) {
        var why = (typeof _demoUnavailableReason === 'function') ? _demoUnavailableReason(d.availability || {}) : '';
        DXStream.toast(T('Needs setup') + (why ? ': ' + why : ''), 'warn');
        return;
    }
    if (typeof DXStream._startDemo === 'function') DXStream._startDemo(demoId);
};

DXStream._perfHistory = { fps: [], npu: [] };
var _PERF_MAX_POINTS = 60;

function _updatePerfTable(p) {
    if (!p) return;
    var $ = DXStream.$;

    var fpsEl = $('perf-fps-current');
    if (p.fps != null) {
        if (fpsEl) { fpsEl.textContent = Math.round(p.fps); fpsEl.removeAttribute('title'); }
        DXStream._perfHistory.fps.push(p.fps);
        if (DXStream._perfHistory.fps.length > _PERF_MAX_POINTS) DXStream._perfHistory.fps.shift();
    } else if (fpsEl && p.mode === 'webrtc') {
        fpsEl.textContent = '—';
        fpsEl.title = T('With WebRTC the browser receives the video; see FPS on the Demo page.');
    }
    if (p.npu != null) {
        var npuEl = $('perf-npu-current');
        if (npuEl) npuEl.textContent = Math.round(p.npu) + '%';
        DXStream._perfHistory.npu.push(p.npu);
        if (DXStream._perfHistory.npu.length > _PERF_MAX_POINTS) DXStream._perfHistory.npu.shift();
    }

    _updatePerfAggregates('fps', DXStream._perfHistory.fps, '');
    _updatePerfAggregates('npu', DXStream._perfHistory.npu, '%');

    _drawSparkline('chart-fps', DXStream._perfHistory.fps, 0, 60, '#30d158');
    _drawSparkline('chart-npu', DXStream._perfHistory.npu, 0, 100, '#8b5cf6');
}

function _updatePerfAggregates(key, arr, suffix) {
    if (arr.length === 0) return;
    var sum = 0, max = -Infinity;
    for (var i = 0; i < arr.length; i++) {
        sum += arr[i];
        if (arr[i] > max) max = arr[i];
    }
    var avg = sum / arr.length;
    var avgEl = DXStream.$('perf-' + key + '-avg');
    var maxEl = DXStream.$('perf-' + key + '-max');
    if (avgEl) avgEl.textContent = Math.round(avg) + suffix;
    if (maxEl) maxEl.textContent = Math.round(max) + suffix;
}

function _drawSparkline(canvasId, data, minVal, maxVal, color) {
    var canvas = DXStream.$(canvasId);
    if (!canvas || data.length < 2) return;
    var parent = canvas.parentElement;
    var nextW = parent.clientWidth || 200;
    var nextH = parent.clientHeight || 48;
    if (canvas.width !== nextW) canvas.width = nextW;
    if (canvas.height !== nextH) canvas.height = nextH;
    var ctx = canvas.getContext('2d');
    var w = canvas.width, h = canvas.height;
    var range = (maxVal - minVal) || 1;
    var step = w / (_PERF_MAX_POINTS - 1);

    ctx.clearRect(0, 0, w, h);

    ctx.beginPath();
    ctx.moveTo(0, h);
    for (var i = 0; i < data.length; i++) {
        var x = i * step;
        var y = h - ((data[i] - minVal) / range) * (h - 4);
        if (i === 0) ctx.lineTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.lineTo((data.length - 1) * step, h);
    ctx.closePath();
    var r = parseInt(color.slice(1,3),16), g = parseInt(color.slice(3,5),16), b = parseInt(color.slice(5,7),16);
    ctx.fillStyle = 'rgba(' + r + ',' + g + ',' + b + ',0.12)';
    ctx.fill();

    ctx.beginPath();
    for (var j = 0; j < data.length; j++) {
        var lx = j * step;
        var ly = h - ((data[j] - minVal) / range) * (h - 4);
        if (j === 0) ctx.moveTo(lx, ly);
        else ctx.lineTo(lx, ly);
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.stroke();
}
if (typeof registerStreamLangRefresher === 'function') {
  registerStreamLangRefresher(function() {
    // The header status badge is otherwise rewritten only by the poll; refresh it now so a language switch shows at once
    var badge = DXStream.$('pipeline-status');
    if (badge && /pill-running/.test(badge.className)) { delete badge.dataset.dxLabel; _setLabelIfChanged(badge, 'play', T('Running')); }
    else if (badge && /pill-idle/.test(badge.className)) badge.textContent = T('Idle');
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined' && DXStream.S && DXStream.S.currentPage && typeof DXStream.nav === 'function') {
      DXStream.nav(DXStream.S.currentPage);
    }
  });
}
