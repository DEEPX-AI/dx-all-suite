/**
 * DX Stream — 데모 런처
 * 데모 카드 렌더링, 시작/중지, WebRTC 연결
 */
DXStream._runningDemoId = null;
DXStream._startingDemo = false;

/* ── XSS 방지: HTML 특수문자 이스케이프 ── */
function _escHtml(s) {
    if (s == null) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

var _demoCatI18n = {
    object_detection: { en: 'Object Detection', ko: '객체 감지', es: 'Detección', ja: '物体検出', 'zh-CN': '目标检测', 'zh-TW': '物件偵測' },
    face_detection:   { en: 'Face Detection',   ko: '얼굴 감지', es: 'Rostro',    ja: '顔検出',   'zh-CN': '人脸检测', 'zh-TW': '人臉偵測' },
    pose_estimation:  { en: 'Pose Estimation',  ko: '자세 추정', es: 'Pose',      ja: '姿勢推定', 'zh-CN': '姿态估计', 'zh-TW': '姿勢估計' },
    segmentation:     { en: 'Segmentation',     ko: '분할',      es: 'Segmentación', ja: 'セグメンテーション', 'zh-CN': '分割', 'zh-TW': '分割' },
    tracking:         { en: 'Tracking',         ko: '추적',      es: 'Seguimiento', ja: '追跡', 'zh-CN': '追踪', 'zh-TW': '追蹤' },
    multi_stream:     { en: 'Multi-Stream',     ko: '멀티 스트림', es: 'Multi',    ja: 'マルチストリーム', 'zh-CN': '多路流', 'zh-TW': '多路串流' },
    secondary:        { en: 'Secondary',        ko: '2차 추론',  es: 'Secundario', ja: '二次推論', 'zh-CN': '二次推理', 'zh-TW': '二次推論' }
};
function _demoCatLabel(cat) {
    var t = _demoCatI18n[cat];
    if (!t) return cat || '';
    return t[DXStream.S.lang] || t.en || cat || '';
}

function _demoText(d, field) {
    var lang = DXStream.S.lang || 'en';
    return d[field + '_' + lang] || d[field + '_en'] || '';
}

var _demoReasonI18n = {
    missing_model: {
        en: 'Model not installed: ', ko: '모델 미설치: ', es: 'Modelo no instalado: ',
        ja: 'モデル未インストール: ', 'zh-CN': '模型未安装: ', 'zh-TW': '模型未安裝: '
    },
    missing_config_file: {
        en: 'Missing config file: ', ko: '설정 파일 없음: ', es: 'Falta el archivo de configuración: ',
        ja: '設定ファイルなし: ', 'zh-CN': '缺少配置文件: ', 'zh-TW': '缺少設定檔: '
    },
    missing_runtime_script: {
        en: 'Missing runtime script: ', ko: '런타임 스크립트 없음: ', es: 'Falta el script de runtime: ',
        ja: 'ランタイムスクリプトなし: ', 'zh-CN': '缺少运行时脚本: ', 'zh-TW': '缺少執行階段腳本: '
    },
    missing_sample_video: {
        en: 'Missing sample video: ', ko: '샘플 비디오 없음: ', es: 'Falta el video de muestra: ',
        ja: 'サンプル動画なし: ', 'zh-CN': '缺少示例视频: ', 'zh-TW': '缺少範例影片: '
    },
    missing_npu_device: {
        en: 'NPU device not found', ko: 'NPU 장치 없음', es: 'Dispositivo NPU no encontrado',
        ja: 'NPUデバイスなし', 'zh-CN': '未找到 NPU 设备', 'zh-TW': '找不到 NPU 裝置'
    },
    missing_dxstream_plugin: {
        en: 'DxStream GStreamer plugin not installed (run build.sh)',
        ko: 'DxStream GStreamer 플러그인 미설치 (build.sh 실행 필요)',
        es: 'Plugin GStreamer de DxStream no instalado (ejecute build.sh)',
        ja: 'DxStream GStreamerプラグイン未インストール（build.shを実行）',
        'zh-CN': '未安装 DxStream GStreamer 插件（运行 build.sh）',
        'zh-TW': '未安裝 DxStream GStreamer 外掛程式（執行 build.sh）'
    }
};

function _demoReasonItemText(item) {
    if (!item || !item.code) return '';
    var labels = _demoReasonI18n[item.code];
    if (!labels) return item.path ? (item.code + ': ' + item.path) : item.code;
    var label = labels[DXStream.S.lang] || labels.en || item.code;
    return item.path ? label + item.path : label;
}

function _demoUnavailableReason(availability) {
    var items = availability.reason_items || [];
    if (Array.isArray(items) && items.length > 0) {
        return items.map(_demoReasonItemText).filter(Boolean).join('; ');
    }
    return availability.reason || '';
}

DXStream.demoInit = async function () {
    DXStream.setPlaybackMode(DXStream._playbackMode); // sync toggle UI with persisted choice
    var grid = DXStream.$('demo-grid');
    if (grid) grid.innerHTML = '<div class="loading-placeholder"><span class="spin"></span>' +
        '<span class="ko">데모 로드 중…</span><span class="en">Loading demos…</span></div>';
    var demos = await DXStream.api('/api/demos');
    if (demos.error) {
        if (grid) grid.innerHTML = '<div class="empty-state"><span class="txt-dim">' +
            T('Failed to load demos') + '</span></div>';
        return;
    }
    DXStream._allDemos = demos;
    _renderDemoCards(demos);
};

function _renderDemoCards(demos) {
    var grid = DXStream.$('demo-grid');
    if (!grid) return;
    if (!demos || demos.length === 0) {
        grid.innerHTML = '<div class="empty-state"><span class="txt-dim">' +
            '<span class="ko">해당하는 데모가 없습니다</span>' +
            '<span class="en">No demos found</span></span></div>';
        return;
    }
    var runId = DXStream._runningDemoId;
    grid.innerHTML = demos.map(function (d) {
        var availability = d.availability || {};
        var reason = _demoUnavailableReason(availability) || d.reason || '';
        return `
        <div class="demo-card${d.id === runId ? ' demo-running' : ''}" data-id="${d.id}" data-category="${_escHtml(d.category)}">
            <div class="demo-card-header">
                <span class="demo-card-num">#${d.id}</span>
                ${d.id === runId ? '<span class="status-pill pill-running">▶</span>' : ''}
                <span class="status-pill ${d.available ? 'pill-ok' : 'pill-warn'}">${d.available ? '✓' : '⚠'}</span>
            </div>
            <h3 class="demo-card-title">
                ${_escHtml(_demoText(d, 'name'))}
            </h3>
            <p class="txt-dim txt-sm">
                ${_escHtml(_demoText(d, 'description'))}
            </p>
            <div class="demo-card-meta">
                <span class="demo-card-model">📦 ${_escHtml(d.model)}</span>
                <span class="demo-card-cat">${_escHtml(_demoCatLabel(d.category))}</span>
            </div>
            ${!d.available && reason ? '<p class="txt-xs txt-warn demo-unavailable-reason">' + _escHtml(reason) + '</p>' : ''}
            ${d.pipeline_type === 'rtsp' ? '<input class="demo-rtsp-input" id="rtsp-url-' + d.id + '" type="text" placeholder="rtsp://host:port/path" title="RTSP" style="width:100%;box-sizing:border-box;margin:2px 0 6px;padding:6px 8px;border:1px solid var(--border);border-radius:6px;background:var(--bg-0,var(--bg-2));color:var(--text-1);font-size:12px"><p class="txt-xs txt-dim" style="margin:0 0 6px"><span class="ko">RTSP 주소 입력 (비우면 데모 CCTV 사용)</span><span class="en">Enter an RTSP URL (blank = demo CCTV)</span><span class="ja">RTSP URLを入力 (空欄=デモCCTV)</span><span class="zh-CN">输入RTSP地址 (留空=演示CCTV)</span><span class="zh-TW">輸入RTSP位址 (留空=示範CCTV)</span><span class="es">Ingrese URL RTSP (vacío = CCTV demo)</span></p>' : ''}
            <div class="demo-card-actions">
                <button class="btn btn-primary btn-sm" onclick="DXStream._startDemo(${d.id})"
                    ${!d.available || d.id === runId ? 'disabled' : ''} id="start-demo-${d.id}"
                    ${d.id === runId ? 'style="display:none"' : ''}>
                    <span class="ko">실행</span><span class="en">Start</span>
                </button>
                <button class="btn btn-ghost btn-sm" onclick="DXStream._stopDemo(${d.id})"
                    ${d.id !== runId ? 'style="display:none"' : ''} id="stop-demo-${d.id}">
                    <span class="ko">중지</span><span class="en">Stop</span>
                </button>
            </div>
        </div>
    `;
    }).join('');
}

// MJPEG mode has no WebRTC getStats. Poll the server's frame counter once a second and diff it
// for a reliable FPS, shown in the same bottom-left overlay as WebRTC (#webrtc-stats-overlay).
// (Counting <img> 'load' events was flaky — a multipart stream may fire 'load' only once.)
var _mjpegFpsTimer = null, _mjpegLastFrames = -1;
function _startMjpegFps() {
    _stopMjpegFps();
    _mjpegLastFrames = -1;
    _mjpegFpsTimer = setInterval(function () {
        DXStream.api('/api/stream/stats').then(function (s) {
            if (!s || typeof s.frames !== 'number') return;
            var overlay = DXStream.$('webrtc-stats-overlay');
            if (!overlay) return;
            if (_mjpegLastFrames < 0) { _mjpegLastFrames = s.frames; overlay.textContent = '… FPS'; return; }
            var fps = Math.max(0, s.frames - _mjpegLastFrames); // 1s interval → frames/sec
            _mjpegLastFrames = s.frames;
            overlay.textContent = fps + ' FPS';
        }).catch(function () {});
    }, 1000);
}
function _stopMjpegFps() {
    if (_mjpegFpsTimer) { clearInterval(_mjpegFpsTimer); _mjpegFpsTimer = null; }
    _mjpegLastFrames = -1;
}
// Show the terminal command for the demo's reference run script (true, un-encoded performance).
function _setPerfCmd(id) {
    var cmdEl = DXStream.$('demo-perf-cmd');
    if (!cmdEl) return;
    var d = (DXStream._allDemos || []).find(function (x) { return x.id === id; });
    if (d && d.runtime_script) cmdEl.textContent = 'bash dx_stream/pipelines/' + d.runtime_script;
}

// Playback mode: 'local' → WebRTC (low-latency, same PC/LAN); 'remote' → MJPEG (works over any
// network/tunnel). Explicit user choice, persisted. Remote sends forceMjpeg so the server skips
// WebRTC entirely (no waiting for an ICE negotiation that can't complete across NAT).
DXStream._playbackMode = (function () {
    try { return localStorage.getItem('dxStreamPlaybackMode') || 'local'; } catch (e) { return 'local'; }
})();
DXStream.setPlaybackMode = function (mode, btn) {
    DXStream._playbackMode = (mode === 'remote') ? 'remote' : 'local';
    try { localStorage.setItem('dxStreamPlaybackMode', DXStream._playbackMode); } catch (e) {}
    // Sync every playback-mode bar (Demo page + Pipeline Builder) so the choice is consistent.
    document.querySelectorAll('.playback-mode-bar button[data-mode]').forEach(function (b) {
        b.classList.toggle('active', b.getAttribute('data-mode') === DXStream._playbackMode);
    });
    var localHint = DXStream.$('playback-mode-hint-local');
    var remoteHint = DXStream.$('playback-mode-hint-remote');
    if (localHint) localHint.style.display = (DXStream._playbackMode === 'local') ? '' : 'none';
    if (remoteHint) remoteHint.style.display = (DXStream._playbackMode === 'remote') ? '' : 'none';
};

// Render the MJPEG stream (<img>) in the video area, hiding the WebRTC <video>. Shared by the
// initial mjpeg response and the WebRTC→MJPEG fallback path.
function _showMjpegStream(videoSection) {
    videoSection = videoSection || DXStream.$('demo-video-section');
    var video = DXStream.$('webrtc-video');
    if (video) video.style.display = 'none';
    var mjpegImg = DXStream.$('mjpeg-stream');
    if (!mjpegImg) {
        mjpegImg = document.createElement('img');
        mjpegImg.id = 'mjpeg-stream';
        mjpegImg.style.cssText = 'width:100%;height:auto;border-radius:8px;background:#000;';
        var container = video ? video.parentNode : videoSection;
        if (container) container.appendChild(mjpegImg);
    }
    mjpegImg.style.display = '';
    mjpegImg.src = '/api/stream/mjpeg?' + Date.now();
    _startMjpegFps(mjpegImg);
    if (videoSection) videoSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Fragmented-MP4 (H264) over HTTP via Media Source Extensions — for remote/tunnel viewers ──
// H264's inter-frame compression keeps 1080p at ~2-4 Mbps (vs MJPEG's ~60), so it fits an SSH
// port-forward; WebRTC (UDP) can't. We fetch the continuous video/mp4 byte stream (init segment +
// fragments) and append it to a <video> SourceBuffer.
var _MSE_MIME_CANDIDATES = [
    'video/mp4; codecs="avc1.42E01E"',  // H264 baseline 3.0 (what Chrome/Firefox decode most reliably)
    'video/mp4; codecs="avc1.42E028"',  // baseline 4.0
    'video/mp4; codecs="avc1.4D401E"',  // main 3.0 (defensive)
    'video/mp4'
];
function _mseSupported() {
    if (!('MediaSource' in window)) return false;
    return _MSE_MIME_CANDIDATES.some(function (m) {
        try { return MediaSource.isTypeSupported(m); } catch (e) { return false; }
    });
}
function _mseMime() {
    for (var i = 0; i < _MSE_MIME_CANDIDATES.length; i++) {
        try { if (MediaSource.isTypeSupported(_MSE_MIME_CANDIDATES[i])) return _MSE_MIME_CANDIDATES[i]; } catch (e) {}
    }
    return _MSE_MIME_CANDIDATES[0];
}
// Derive the EXACT codec string from the fMP4 init segment's avcC box (bytes after 'avcC':
// configurationVersion, AVCProfileIndication, profile_compatibility, AVCLevelIndication). The HW
// encoder's profile/LEVEL varies per demo resolution, so a hardcoded guess (e.g. baseline L3.0)
// mismatches L4.0 streams → MSE accepts the bytes but the decoder renders nothing (black). Using
// the real codec string makes every demo play. Returns e.g. "avc1.42c028" or null if not found.
function _avcCodecsFromBytes(u8) {
    // Return an ordered list of candidate mime strings derived from the init segment's avcC:
    // the exact profile/compat/LEVEL first, then same-level variants (standard compat, main
    // profile) as defensive fallbacks. Empty if avcC not yet present. Getting the LEVEL right is
    // what matters — declaring L3.0 for an L4.0 stream makes the decoder render nothing (black).
    if (!u8) return [];
    for (var i = 0; i + 8 < u8.length; i++) {
        if (u8[i] === 0x61 && u8[i + 1] === 0x76 && u8[i + 2] === 0x63 && u8[i + 3] === 0x43) { // 'avcC'
            var h = function (n) { return (n < 16 ? '0' : '') + n.toString(16); };
            var prof = h(u8[i + 5]), compat = h(u8[i + 6]), lvl = h(u8[i + 7]);
            var mk = function (p, c) { return 'video/mp4; codecs="avc1.' + p + c + lvl + '"'; };
            return [mk(prof, compat), mk(prof, 'e0'), mk('4d', '40'), mk('64', '00')];
        }
    }
    return [];
}
function _concatU8(a, b) {
    if (!a) return b;
    var out = new Uint8Array(a.length + b.length);
    out.set(a, 0); out.set(b, a.length);
    return out;
}

var _fmp4 = null;
function _showFmp4Stream(videoSection) {
    videoSection = videoSection || DXStream.$('demo-video-section');
    var video = DXStream.$('webrtc-video');
    var mjpegImg = DXStream.$('mjpeg-stream');
    if (mjpegImg) mjpegImg.style.display = 'none';
    if (!_mseSupported()) { DXStream._fallbackToMjpeg(DXStream._runningDemoId); return; }
    _fmp4PlayInto(video);
    if (videoSection) videoSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Core MSE player, reusable for the demo page and the Pipeline Builder (they pass different
// <video> elements). Fetches /api/stream/fmp4 and feeds it to a SourceBuffer.
function _fmp4PlayInto(video) {
    _stopFmp4();
    if (!video) return;
    video.srcObject = null;
    video.style.display = '';
    video.muted = true;
    video.playsInline = true;

    var ms = new MediaSource();
    // st.sb is created lazily once the init segment arrives and we know the real codec string.
    var st = { ms: ms, video: video, sb: null, queue: [], reader: null, stopped: false,
               mime: null, initBuf: null };
    _fmp4 = st;
    video.src = URL.createObjectURL(ms);
    ms.addEventListener('sourceopen', function () {
        if (st.stopped) return;
        _fmp4Fetch(st);   // SourceBuffer added inside, after the codec is known
    });
    video.play().catch(function () {});
    _startFmp4Fps(video);
}
// Create the SourceBuffer from the actual stream codec (parsed from the buffered init segment),
// then flush the buffered init bytes into it. Falls back to the static candidate list if avcC
// can't be found. Returns true once the SourceBuffer exists.
function _fmp4EnsureSourceBuffer(st) {
    if (st.sb) return true;
    if (st.ms.readyState !== 'open') return false;
    var derived = _avcCodecsFromBytes(st.initBuf);
    var mime = null;
    for (var k = 0; k < derived.length; k++) {
        try { if (MediaSource.isTypeSupported(derived[k])) { mime = derived[k]; break; } } catch (e) {}
    }
    // Wait for more bytes until avcC is seen — unless we've buffered plenty (give up, use fallback).
    if (!derived.length && st.initBuf && st.initBuf.length < 262144) return false;
    if (!mime) mime = _mseMime();
    st.mime = mime;
    try {
        st.sb = st.ms.addSourceBuffer(mime);
        st.sb.mode = 'sequence';  // auto-sequence timestamps (smooth over EOS restarts)
    } catch (e) {
        DXStream.toast(T('MSE init failed, using MJPEG: ') + e.message, 'warn');
        DXStream._fallbackToMjpeg(DXStream._runningDemoId);
        return false;
    }
    st.sb.addEventListener('updateend', function () { _fmp4Pump(st); _fmp4KeepLive(st); });
    if (st.initBuf && st.initBuf.length) { st.queue.push(st.initBuf); st.initBuf = null; }
    _fmp4Pump(st);
    return true;
}
function _fmp4Fetch(st) {
    fetch('/api/stream/fmp4').then(function (resp) {
        if (!resp.ok || !resp.body) throw new Error('HTTP ' + resp.status);
        st.reader = resp.body.getReader();
        (function read() {
            st.reader.read().then(function (r) {
                if (st.stopped) { try { st.reader.cancel(); } catch (e) {} return; }
                if (r.done) return;
                if (!st.sb) {
                    // Buffer bytes until we can read the codec from the init segment's avcC box.
                    st.initBuf = _concatU8(st.initBuf, r.value);
                    _fmp4EnsureSourceBuffer(st);
                } else {
                    st.queue.push(r.value);
                    _fmp4Pump(st);
                }
                read();
            }).catch(function () {});
        })();
    }).catch(function (e) {
        if (!st.stopped) DXStream.toast(T('fMP4 stream error: ') + e.message, 'error');
    });
}
function _fmp4Pump(st) {
    if (!st.sb || st.stopped || st.ms.readyState !== 'open' || st.sb.updating || !st.queue.length) return;
    var chunk = st.queue.shift();
    try {
        st.sb.appendBuffer(chunk);
    } catch (e) {
        if (e && e.name === 'QuotaExceededError') { st.queue.unshift(chunk); _fmp4Trim(st, true); }
        // otherwise drop the chunk and keep going
    }
}
function _fmp4Trim(st, aggressive) {
    try {
        var sb = st.sb, v = st.video;
        if (!sb || sb.updating || !sb.buffered.length) return;
        var start = sb.buffered.start(0);
        var end = sb.buffered.end(sb.buffered.length - 1);
        var cutoff = aggressive ? (end - 2) : (v.currentTime - 4);
        if (cutoff > start + 0.5) sb.remove(start, cutoff);
    } catch (e) {}
}
function _fmp4KeepLive(st) {
    _fmp4Trim(st, false);
    try {
        var v = st.video, sb = st.sb;
        if (sb.buffered.length) {
            var end = sb.buffered.end(sb.buffered.length - 1);
            if (end - v.currentTime > 4) v.currentTime = end - 0.3;  // bound latency near live edge
        }
    } catch (e) {}
}
function _stopFmp4() {
    _stopFmp4Fps();
    var st = _fmp4;
    if (!st) return;
    st.stopped = true;
    try { if (st.reader) st.reader.cancel(); } catch (e) {}
    try { if (st.ms && st.ms.readyState === 'open') st.ms.endOfStream(); } catch (e) {}
    var v = st.video;
    if (v) {
        try { v.pause(); } catch (e) {}
        try { if (v.src) URL.revokeObjectURL(v.src); } catch (e) {}
        v.removeAttribute('src');
        try { v.load(); } catch (e) {}
    }
    _fmp4 = null;
}
var _fmp4FpsTimer = null, _fmp4LastFrames = -1;
function _startFmp4Fps(video) {
    _stopFmp4Fps();
    _fmp4LastFrames = -1;
    var _zeroSecs = 0, _fellBack = false;
    _fmp4FpsTimer = setInterval(function () {
        var q = video.getVideoPlaybackQuality ? video.getVideoPlaybackQuality() : null;
        var f = q ? q.totalVideoFrames : (video.webkitDecodedFrameCount || 0);
        // Stall guard: if the fMP4/MSE path decoded ZERO frames after several seconds (data may
        // be arriving but the browser's MSE decoder rendered nothing — codec/container quirk),
        // transparently fall back to MJPEG, which is a plain <img> over HTTP and always renders.
        if (!_fellBack) {
            if (f === 0) {
                _zeroSecs += 1;
                if (_zeroSecs >= 4) {
                    _fellBack = true;
                    DXStream.toast(T('Video decode stalled — switching to MJPEG'), 'warn');
                    DXStream._fallbackToMjpeg(DXStream._runningDemoId);
                    return;
                }
            } else {
                _zeroSecs = 0;
            }
        }
        var overlay = DXStream.$('webrtc-stats-overlay');
        if (!overlay) return;
        if (_fmp4LastFrames < 0) { _fmp4LastFrames = f; overlay.textContent = '… FPS'; return; }
        overlay.textContent = Math.max(0, f - _fmp4LastFrames) + ' FPS';
        _fmp4LastFrames = f;
    }, 1000);
}
function _stopFmp4Fps() {
    if (_fmp4FpsTimer) { clearInterval(_fmp4FpsTimer); _fmp4FpsTimer = null; }
    _fmp4LastFrames = -1;
}
// Exposed for the Pipeline Builder (stream-pipeline-api.js), which streams into its own <video>.
DXStream._mseSupported = _mseSupported;
DXStream._fmp4PlayInto = _fmp4PlayInto;
DXStream._fmp4Stop = _stopFmp4;

// WebRTC couldn't connect (remote/NAT/tunnel). Restart this demo forcing MJPEG on the server,
// then show the MJPEG stream. Guarded so it only runs once per start.
DXStream._fallbackToMjpeg = async function (id) {
    if (DXStream._mjpegFallbackFor === id) return;
    DXStream._mjpegFallbackFor = id;
    if (DXStream._runningDemoId !== id) return; // demo was stopped/changed meanwhile
    try {
        // Tear down whatever transport was attempted (WebRTC peer / fMP4 fetch+MSE + its timers)
        // so we don't leave a background stream running alongside the MJPEG one.
        try { if (DXStream.webrtc && DXStream.webrtc.disconnect) DXStream.webrtc.disconnect(); } catch (e) {}
        try { _stopFmp4(); } catch (e) {}
        DXStream.toast(T('WebRTC unavailable from here — switching to MJPEG…'), 'info');
        var resp = await DXStream.postJ('/api/demos/' + id + '/start', { forceMjpeg: true });
        if (resp && resp.error) { DXStream.toast(resp.error, 'error'); return; }
        _showMjpegStream(DXStream.$('demo-video-section'));
    } catch (e) {
        DXStream.toast(T('MJPEG fallback failed: ') + (e && e.message ? e.message : e), 'error');
    }
};

DXStream._startDemo = async function (id) {
    if (DXStream._startingDemo) {
        DXStream.toast(T('Demo start already in progress'), 'warn');
        return;
    }
    DXStream._startingDemo = true;
    DXStream._mjpegFallbackFor = null; // allow WebRTC→MJPEG fallback for this fresh start
    var startBtn = DXStream.$('start-demo-' + id);
    if (startBtn) startBtn.disabled = true;

    try {
        DXStream.toast(T('Starting demo…'), 'info');
        var webrtcPayloadTypes = await DXStream.webrtc.preferredPayloadTypes();
        var _startBody = { webrtcPayloadTypes: webrtcPayloadTypes };
        // Remote mode → MJPEG directly. fMP4/MSE proved unreliable across the SSH tunnel (the
        // browser's MSE decoder renders nothing for the HW-encoded stream), so skip it and use
        // MJPEG — a plain <img> over HTTP that always renders and is low-latency. Local mode
        // keeps WebRTC (lowest latency on the same LAN).
        if (DXStream._playbackMode === 'remote') {
            _startBody.forceMjpeg = true;
        }
        // RTSP demos: pass the user-entered rtsp:// URL as the source (backend routes any
        // "://" value through as the pipeline URI). Blank falls back to the demo's default CCTV.
        var _rtspEl = DXStream.$('rtsp-url-' + id);
        if (_rtspEl && _rtspEl.value.trim()) _startBody.video = _rtspEl.value.trim();
        var resp = await DXStream.postJ('/api/demos/' + id + '/start', _startBody);
        if (resp.error) {
            DXStream.toast(resp.error, 'error');
            return;
        }
        if (resp.output_mode === 'webrtc') {
            var status = await _waitDemoStarted(id, resp.pipeline_id);
            if (status && status.error) {
                DXStream.toast(status.error, 'error');
                return;
            }
        }
        DXStream._runningDemoId = id;
        _setPerfCmd(id);
        DXStream.toast(T('Demo started'), 'success');

        // UI 토글: 실행 → 중지 버튼
        if (startBtn) startBtn.style.display = 'none';
        var stopBtn = DXStream.$('stop-demo-' + id);
        if (stopBtn) stopBtn.style.display = '';

        // 실행 중 카드 하이라이트
        var card = startBtn ? startBtn.closest('.demo-card') : null;
        if (card) card.classList.add('demo-running');

        // 비디오 연결
        if (resp.output_mode === 'mjpeg' || resp.output_mode === 'webrtc' || resp.output_mode === 'fmp4') {
            var videoSection = DXStream.$('demo-video-section');
            if (videoSection) {
                videoSection.style.display = '';
            }
            var demo = DXStream._allDemos ? DXStream._allDemos.find(function (d) { return d.id === id; }) : null;
            if (demo) {
                var titleEl = DXStream.$('demo-video-title');
                if (titleEl) titleEl.textContent = '#' + id + ' ' + _demoText(demo, 'name');
                var modelEl = DXStream.$('demo-model-info');
                if (modelEl) modelEl.textContent = '📦 ' + (demo.model || '--');
                var pipeEl = DXStream.$('demo-pipeline-info');
                if (pipeEl) pipeEl.textContent = demo.category || '';
            }

            if (resp.output_mode === 'mjpeg') {
                _showMjpegStream(videoSection);
            } else if (resp.output_mode === 'fmp4') {
                _showFmp4Stream(videoSection);
            } else {
                var video = DXStream.$('webrtc-video');
                // Try WebRTC (low-latency, no re-encode). If it can't connect — remote viewer
                // over a tunnel/NAT where the board only offers unroutable LAN host candidates —
                // the client gives up after CONNECT_TIMEOUT and we transparently switch this demo
                // to MJPEG, which streams over the same HTTP proxy and works from anywhere.
                if (video) DXStream.webrtc.connect(video, false, function () { DXStream._fallbackToMjpeg(id); });
            }
        } else {
            DXStream.toast(T('Native display mode (fpsdisplaysink)'), 'info');
        }
    } finally {
        DXStream._startingDemo = false;
        if (startBtn && DXStream._runningDemoId == null) startBtn.disabled = false;
    }
};

function _demoStatusDelay(attempt) {
    return Math.min(250 * Math.pow(1.5, attempt), 2000);
}

async function _waitDemoStarted(id, pipelineId) {
    var deadline = Date.now() + 12000;
    var attempt = 0;
    while (Date.now() < deadline) {
        var status = await DXStream.api('/api/pipeline/status');
        if (status.error) return status;
        var pipelineMatch = !pipelineId || status.pipeline_id === pipelineId;
        if (status.running && pipelineMatch) return status;
        await new Promise(function (resolve) {
            setTimeout(resolve, _demoStatusDelay(attempt++));
        });
    }
    return { error: T('Demo start timed out. Retry or check the runtime.') };
}

DXStream._stopDemo = async function (id) {
    DXStream.webrtc.disconnect();
    var demoId = (id != null) ? id : DXStream._runningDemoId;
    if (demoId != null) {
        await DXStream.postJ('/api/demos/' + demoId + '/stop', {});
        // UI 토글: 중지 → 실행 버튼
        var startBtn = DXStream.$('start-demo-' + demoId);
        var stopBtn = DXStream.$('stop-demo-' + demoId);
        if (startBtn) { startBtn.style.display = ''; startBtn.disabled = false; }
        if (stopBtn) stopBtn.style.display = 'none';
        // 실행 중 카드 하이라이트 해제
        var card = startBtn ? startBtn.closest('.demo-card') : null;
        if (card) card.classList.remove('demo-running');
    } else {
        await DXStream.postJ('/api/pipeline/stop', {});
    }

    // 비디오 섹션 숨김 및 정리
    var videoSection = DXStream.$('demo-video-section');
    if (document.fullscreenElement === videoSection && document.exitFullscreen) {
        try { await document.exitFullscreen(); } catch (e) {}
    }
    if (videoSection) videoSection.style.display = 'none';
    _stopFmp4();  // tear down MSE stream (fetch reader + MediaSource) if remote/fMP4 was active
    var video = DXStream.$('webrtc-video');
    if (video) { video.srcObject = null; video.style.display = ''; }
    var mjpegImg = DXStream.$('mjpeg-stream');
    if (mjpegImg) { mjpegImg.src = ''; mjpegImg.style.display = 'none'; }
    _stopMjpegFps();
    var titleEl = DXStream.$('demo-video-title');
    if (titleEl) titleEl.textContent = '--';
    var statsOverlay = DXStream.$('webrtc-stats-overlay');
    if (statsOverlay) statsOverlay.textContent = '';

    DXStream._runningDemoId = null;
    DXStream.toast(T('Demo stopped'), 'info');
};

DXStream.filterDemos = function (cat, btn) {
    var bar = DXStream.$('demo-filter-bar');
    if (bar) {
        bar.querySelectorAll('.btn').forEach(function (b) { b.classList.remove('active'); });
        // btn 이 없으면 data-cat으로 찾기
        if (btn) {
            btn.classList.add('active');
        } else if (bar) {
            var match = bar.querySelector('[data-cat="' + cat + '"]');
            if (match) match.classList.add('active');
        }
    }
    if (!DXStream._allDemos) return;
    if (cat === 'all') {
        _renderDemoCards(DXStream._allDemos);
    } else {
        _renderDemoCards(DXStream._allDemos.filter(function (d) {
            return d.category === cat;
        }));
    }
};

DXStream.stopDemo = function () {
    DXStream._stopDemo(DXStream._runningDemoId);
};

DXStream.toggleFullscreen = function () {
    var target = DXStream.$('demo-video-section') || DXStream.$('demo-video') || DXStream.$('webrtc-video');
    if (!target) return;
    if (document.fullscreenElement) {
        document.exitFullscreen();
    } else {
        target.requestFullscreen().catch(function () {});
    }
};
if (typeof registerStreamLangRefresher === 'function') {
  registerStreamLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined' && DXStream.S && DXStream.S.currentPage && typeof DXStream.nav === 'function') {
      DXStream.nav(DXStream.S.currentPage);
    }
  });
}
