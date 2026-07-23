/**
 * DX Stream — 대시보드 페이지
 * 시스템 상태 5초 폴링, i18n 적용
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
            data.build.ok ? T('OK') : T('Not built'));
    }

    // 성능 지표 업데이트 (서버가 perf 필드 제공 시)
    _updatePerfTable(data);

    _updatePipelineBadge(pipeResp);
}

function _updatePipelineBadge(data) {
    var badge = DXStream.$('pipeline-status');
    if (!badge) return;
    if (data && data.running) {
        _setTextIfChanged(badge, '▶ ' + T('Running'));
        _setClassIfChanged(badge, 'status-pill pill-running');
    } else {
        _setTextIfChanged(badge, T('Idle'));
        _setClassIfChanged(badge, 'status-pill pill-idle');
    }
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
    if (icon) _setTextIfChanged(icon, ok ? '✅' : '⚠️');
}

if (typeof document !== 'undefined') {
    document.addEventListener('visibilitychange', function () {
        if (_dashboardVisible()) _fetchStatus();
    });
}

DXStream.quickLaunchDemo = function (demoId) {
    DXStream.nav('demo');
    // 데모 페이지 초기화 후 자동 시작
    setTimeout(function () {
        if (typeof DXStream._startDemo === 'function') {
            DXStream._startDemo(demoId);
        }
    }, 400);
};

DXStream._perfHistory = { fps: [], npu: [] };
var _PERF_MAX_POINTS = 60;

function _updatePerfTable(data) {
    if (!data || !data.perf) return;
    var p = data.perf;
    var $ = DXStream.$;

    if (p.fps != null) {
        var fpsEl = $('perf-fps-current');
        if (fpsEl) fpsEl.textContent = Math.round(p.fps);
        DXStream._perfHistory.fps.push(p.fps);
        if (DXStream._perfHistory.fps.length > _PERF_MAX_POINTS) DXStream._perfHistory.fps.shift();
    }
    if (p.latency != null) {
        var latEl = $('perf-latency-current');
        if (latEl) latEl.textContent = p.latency.toFixed(1) + ' ms';
    }
    if (p.e2e != null) {
        var e2eEl = $('perf-e2e-current');
        if (e2eEl) e2eEl.textContent = p.e2e.toFixed(1) + ' ms';
    }
    if (p.npu_util != null) {
        var npuEl = $('perf-npu-current');
        if (npuEl) npuEl.textContent = Math.round(p.npu_util) + '%';
        DXStream._perfHistory.npu.push(p.npu_util);
        if (DXStream._perfHistory.npu.length > _PERF_MAX_POINTS) DXStream._perfHistory.npu.shift();
    }

    _updatePerfAggregates('fps', DXStream._perfHistory.fps, '');
    _updatePerfAggregates('npu', DXStream._perfHistory.npu, '%');

    _drawSparkline('chart-fps', DXStream._perfHistory.fps, 0, 60, '#3FB950');
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
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined' && DXStream.S && DXStream.S.currentPage && typeof DXStream.nav === 'function') {
      DXStream.nav(DXStream.S.currentPage);
    }
  });
}
