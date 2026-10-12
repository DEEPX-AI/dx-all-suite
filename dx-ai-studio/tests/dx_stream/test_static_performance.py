import subprocess
from pathlib import Path

import pytest
from tests.browser_support import resolve_node_executable


ROOT = Path(__file__).resolve().parents[2]
STREAM_JS = ROOT / "dx_stream/static/js"
STREAM_HTML = ROOT / "dx_stream/templates/index.html"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_all_pipeline_sources() -> str:
    """Joins every split pipeline file plus the original into one string."""
    files = [
        "stream-pipeline-state.js",
        "stream-pipeline-api.js",
        "stream-pipeline-serialization.js",
        "stream-pipeline-renderer.js",
        "stream-pipeline.js",
    ]
    parts = []
    for f in files:
        p = STREAM_JS / f
        if p.exists():
            parts.append(p.read_text(encoding="utf-8"))
    return "\n".join(parts)


def _function_body(source: str, signature: str) -> str:
    start = source.index(signature)
    paren = source.index("(", start)
    depth = 0
    close_paren = None
    for pos in range(paren, len(source)):
        if source[pos] == "(":
            depth += 1
        elif source[pos] == ")":
            depth -= 1
            if depth == 0:
                close_paren = pos
                break
    assert close_paren is not None
    brace = source.index("{", close_paren)
    depth = 0
    for pos in range(brace, len(source)):
        if source[pos] == "{":
            depth += 1
        elif source[pos] == "}":
            depth -= 1
            if depth == 0:
                return source[brace + 1:pos]
    raise AssertionError(f"Could not parse function body for {signature}")


def test_pipeline_canvas_refresh_is_raf_scheduled_for_hot_paths():
    source = _read_all_pipeline_sources()
    move_body = _function_body(source, "function _canvasMouseMove(")
    wheel_body = _function_body(source, "function _canvasWheel(")
    init_body = _function_body(source, "function _initCanvas(")

    assert "function _scheduleCanvasRefresh(" in source
    assert "_canvasRefreshRaf = requestAnimationFrame(function ()" in source
    assert "_scheduleCanvasRefresh();" in move_body
    assert "_refreshCanvas();" not in move_body
    assert "_scheduleCanvasRefresh();" in wheel_body
    assert "_refreshCanvas();" not in wheel_body
    assert "window.addEventListener('resize', scheduleResize)" in init_body
    assert "setTimeout(resize, 100)" in init_body


def test_command_preview_updates_on_structure_changes_not_canvas_repaint():
    source = _read_all_pipeline_sources()
    refresh_body = _function_body(source, "function _refreshCanvas(")
    push_body = _function_body(source, "function _pushHistory(")

    assert "function _scheduleCommandPreview(" in source
    assert "_updateCommandPreview();" not in refresh_body
    assert "_scheduleCommandPreview();" in push_body


def test_pipeline_hot_paths_use_cached_theme_colors():
    source = _read_all_pipeline_sources()
    refresh_body = _function_body(source, "function _refreshCanvas(")

    assert "function _cachePipelineThemeColors(" in source
    assert "function _themeColor(" in source
    assert "ctx.fillStyle = _themeColor('bg0')" in refresh_body
    assert "getComputedStyle(document.documentElement)" not in refresh_body


def test_minimap_and_edge_hit_testing_avoid_repeated_linear_work():
    source = _read_all_pipeline_sources()
    edge_body = _function_body(source, "function _hitEdge(")
    dist_body = _function_body(source, "function _distToBezierSq(")
    minimap_body = _function_body(source, "function _drawMinimap(")

    assert "function _getPipelineNodeMap(" in source
    assert "function _edgeBoundsContains(" in source
    assert "_getPipelineNodeMap(st)" in edge_body
    assert "_edgeBoundsContains(wx, wy, x1, y1, x2, y2, threshold)" in edge_body
    assert "_distToBezierSq(wx, wy, x1, y1, x2, y2) < threshold * threshold" in edge_body
    assert "Math.sqrt" not in dist_body
    assert "st.nodes.find" not in minimap_body
    assert "function _ensureMinimapCanvasSize(" in source
    assert "_ensureMinimapCanvasSize(mmCanvas, container)" in minimap_body


def test_history_draft_save_is_debounced():
    source = _read_all_pipeline_sources()
    push_body = _function_body(source, "function _pushHistory(")

    assert "var _draftSaveTimer = null;" in source
    assert "function _scheduleDraftSave(" in source
    assert "setTimeout(function ()" in source
    assert "_scheduleDraftSave(snap);" in push_body
    assert "localStorage.setItem" not in push_body


def test_dashboard_poll_and_sparkline_avoid_unnecessary_work():
    source = _read(STREAM_JS / "stream-dashboard.js")
    init_body = _function_body(source, "DXStream.dashboardInit = function (")
    fetch_body = _function_body(source, "async function _fetchStatus(")
    spark_body = _function_body(source, "function _drawSparkline(")
    stat_body = _function_body(source, "function _updateStat(")

    assert "function _dashboardVisible(" in source
    assert "if (!_dashboardVisible()) return;" in fetch_body
    assert "document.addEventListener('visibilitychange'" in source
    assert "_fetchStatus();" in init_body
    assert "Promise.all([" in fetch_body
    assert "DXStream.api('/api/status')" in fetch_body
    assert "DXStream.api('/api/pipeline/status')" in fetch_body
    assert "function _setTextIfChanged(" in source
    assert "_setTextIfChanged(val, text);" in stat_body
    assert "_setClassIfChanged(el, nextClass);" in stat_body
    assert "if (canvas.width !== nextW) canvas.width = nextW;" in spark_body
    assert "if (canvas.height !== nextH) canvas.height = nextH;" in spark_body
    assert "canvas.width = parent.clientWidth || 200" not in spark_body


def test_stream_setup_log_polling_skips_hidden_and_appends_changes():
    source = _read(STREAM_JS / "stream-setup.js")
    poll_body = _function_body(source, "function _startLogPoll(")

    assert "function _streamSetupVisible(" in source
    assert "if (!_streamSetupVisible()) return;" in poll_body
    assert "function _appendSetupLog(" in source
    assert "_appendSetupLog(logEl, r.log);" in poll_body
    assert "logEl.textContent = r.log;" not in poll_body


def test_command_preview_commits_only_when_output_changes():
    source = _read_all_pipeline_sources()
    preview_body = _function_body(source, "function _updateCommandPreview(")

    assert "var _lastCommandPreviewText = null;" in source
    assert "function _setCommandPreviewText(" in source
    assert "_setCommandPreviewText(el, 'gst-launch-1.0 ...', true);" in preview_body
    assert "_setCommandPreviewText(el, cmd, false);" in preview_body
    assert "el.innerHTML = '<span class=\"txt-dim\">gst-launch-1.0 ...</span>';" not in preview_body
    assert "el.textContent = cmd;" not in preview_body


def test_webrtc_stops_ice_poll_after_connection_established():
    source = _read(STREAM_JS / "webrtc-client.js")
    ice_body = _function_body(source, "function _startICEPoll(")

    assert "function _stopICEPoll(" in source
    assert "_stopICEPoll();" in source
    assert "pc.oniceconnectionstatechange" in source
    assert "connected' || pc.iceConnectionState === 'completed'" in source
    assert "if (_pollTimer) return;" in ice_body


def test_webrtc_error_banner_persists_and_is_not_auto_hidden():
    """A stream failure keeps its error banner up (no auto-hide).

    It stays until recovery or a user action (_clearError); the display logic has no
    auto-hide timer (setTimeout).
    """
    source = _read(STREAM_JS / "webrtc-client.js")

    assert "function _showError(" in source, "persistent error banner missing"
    assert "function _clearError(" in source, "error dismiss/recovery path missing"

    show_body = _function_body(source, "function _showError(")
    # Persistent: no auto-hide timer.
    assert "setTimeout" not in show_body, "error banner must not auto-hide via setTimeout"
    # The banner offers retry/close.
    assert "DXStream.webrtc.retry()" in show_body
    assert "_clearError()" in show_body

    # Receiving a track (recovery) clears the error.
    ontrack_region = source[source.index("pc.ontrack"):source.index("pc.onicecandidate")]
    assert "_clearError()" in ontrack_region, "recovery must clear the error banner"

    # After the last retry it falls back to MJPEG (_giveUp → _onFail callback):
    # when WebRTC cannot connect remotely/behind NAT, switch to MJPEG instead of a dead banner.
    retry_body = _function_body(source, "function _attemptRetry(")
    assert "_giveUp(" in retry_body
    giveup_body = _function_body(source, "function _giveUp(")
    assert "_onFail(" in giveup_body, "give-up path must invoke the MJPEG-fallback callback"


def test_pipeline_webrtc_fallback_restores_state_after_forced_mjpeg_failure():
    """The static JavaScript contract must reset controls when forced MJPEG cannot start."""
    source = _read(STREAM_JS / "stream-pipeline-api.js")
    reset_body = _function_body(source, "function _resetPipelineAfterFallbackFailure(")
    run_body = _function_body(source, "DXStream.pipelineRun = async function (")

    assert "DXStream._wirePipelineMjpeg = function" in source
    assert "DXStream._pipeRunning = false" in reset_body
    assert "_updatePipelineButtons();" in reset_body
    assert "DXStream.toast(" in reset_body
    assert "forceMjpeg: true" in run_body
    assert "if (r2 && !r2.error && r2.output_mode === 'mjpeg')" in run_body
    assert "_resetPipelineAfterFallbackFailure(" in run_body
    assert ".catch(function (error)" in run_body


@pytest.mark.requires_node
def test_pipeline_webrtc_fallback_failure_resets_controls_at_runtime():
    """Execute both forced-MJPEG failure paths through the WebRTC callback."""
    node = resolve_node_executable()
    if not node:
        pytest.skip("node not available")

    script = r"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync(process.argv[1], 'utf8');

function assert(condition, message) {
    if (!condition) {
        throw new Error(message);
    }
}

async function runCase(name, forcedMjpegResponse) {
    const runButton = { disabled: false };
    const stopButton = { disabled: true };
    const videoSection = { style: {}, scrollIntoView() {} };
    const pipeVideo = { style: {}, parentNode: { appendChild() {} } };
    const requests = [];
    const toasts = [];
    let onWebrtcFailure = null;
    const context = {
        console,
        Promise,
        Object,
        Date,
        document: {
            createElement() {
                return { style: {}, parentNode: null };
            },
        },
        T(value) { return value; },
        DXStream: {
            _pipeRunning: false,
            _pipeState: { nodes: [], edges: [] },
            $(id) {
                return {
                    'btn-pipeline-run': runButton,
                    'btn-pipeline-stop': stopButton,
                    'pipeline-video-section': videoSection,
                    'pipeline-webrtc-video': pipeVideo,
                }[id] || null;
            },
            toast(message, level) {
                toasts.push({ message, level });
            },
            webrtc: {
                preferredPayloadTypes() {
                    return Promise.resolve([]);
                },
                connect(video, withAudio, callback) {
                    onWebrtcFailure = callback;
                },
            },
            postJ(path, body) {
                requests.push({ path, body });
                if (requests.length === 1) {
                    return Promise.resolve({ output_mode: 'webrtc' });
                }
                return forcedMjpegResponse();
            },
        },
    };

    vm.createContext(context);
    vm.runInContext(source, context);
    await context.DXStream.pipelineRun();

    assert(onWebrtcFailure, name + ': WebRTC failure callback was not registered');
    assert(context.DXStream._pipeRunning, name + ': initial pipeline run did not start');
    assert(runButton.disabled, name + ': Run was not disabled while running');
    assert(!stopButton.disabled, name + ': Stop was not enabled while running');

    onWebrtcFailure('ICE connection failed');
    await new Promise((resolve) => setImmediate(resolve));

    assert(requests.length === 2, name + ': forced MJPEG rerun was not requested');
    assert(requests[1].body.forceMjpeg === true, name + ': rerun did not force MJPEG');
    assert(!context.DXStream._pipeRunning, name + ': pipeline state was not reset');
    assert(!runButton.disabled, name + ': Run was not restored');
    assert(stopButton.disabled, name + ': Stop was not restored');
    assert(
        toasts.some((toast) => toast.level === 'error' &&
            toast.message.indexOf('MJPEG fallback failed:') === 0),
        name + ': fallback error was not reported'
    );
}

(async function () {
    await runCase('HTTP-error JSON', function () {
        return Promise.resolve({ error: 'forced MJPEG returned HTTP 503' });
    });
    await runCase('network rejection', function () {
        return Promise.reject(new Error('network unavailable'));
    });
    console.log('OK: WebRTC fallback failures reset pipeline controls');
})().catch((error) => {
    console.error(error.stack || error);
    process.exit(1);
});
"""
    result = subprocess.run(
        [node, "-e", script, str(STREAM_JS / "stream-pipeline-api.js")],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK: WebRTC fallback failures reset pipeline controls" in result.stdout


def test_webrtc_surfaces_stall_as_bus_error_state():
    """A frame stall while streaming (black screen from a bus error)
    surfaces an error state.
    """
    source = _read(STREAM_JS / "webrtc-client.js")
    stats_body = _function_body(source, "function _startStatsPoll(")

    assert "framesDecoded" in stats_body, "stall watchdog must track decoded frames"
    assert "STALL_LIMIT" in source, "stall threshold missing"
    assert "_showError(" in stats_body, "stalled stream must surface an error state"
    # Clear the error once frames advance again.
    assert "_clearError()" in stats_body


# Stream pipeline split — contract tests

def test_stream_pipeline_split_files_exist():
    """Every split pipeline JS file exists."""
    expected_files = [
        "stream-pipeline-state.js",
        "stream-pipeline-api.js",
        "stream-pipeline-serialization.js",
        "stream-pipeline-renderer.js",
    ]
    for f in expected_files:
        assert (STREAM_JS / f).exists(), f"Missing: {f}"


def test_stream_pipeline_split_script_order_in_html():
    """index.html loads the pipeline scripts in the right order."""
    html = _read(STREAM_HTML)
    expected = [
        "static/js/stream-pipeline-state.js",
        "static/js/stream-pipeline-api.js",
        "static/js/stream-pipeline-serialization.js",
        "static/js/stream-pipeline-renderer.js",
        "static/js/stream-pipeline.js",
    ]
    positions = []
    for script in expected:
        pos = html.find(script)
        assert pos != -1, f"Script not found in HTML: {script}"
        positions.append(pos)
    # Order check
    for i in range(len(positions) - 1):
        assert positions[i] < positions[i + 1], (
            f"Script order wrong: {expected[i]} should come before {expected[i + 1]}"
        )


def test_stream_runtime_scripts_are_content_hash_versioned():
    """Runtime scripts get a v= hash so Firefox does not reuse stale WebRTC JS."""
    import server

    handler = object.__new__(server.DXStreamHandler)
    html = handler.render_html_with_asset_hashes(_read(STREAM_HTML), asset_scope="dx_stream")

    for script in (
        "/static/js/webrtc-client.js",
        "/static/js/stream-demo.js",
        "/static/js/stream-pipeline-api.js",
    ):
        assert f'src="{script}?m=dx_stream&v=' in html
        assert f'src="{script}"' not in html
        assert f'src="{script.lstrip("/")}"' not in html


def test_stream_pipeline_namespace_in_state_file():
    """stream-pipeline-state.js defines the window.DXStreamPipeline namespace."""
    source = _read(STREAM_JS / "stream-pipeline-state.js")
    assert "window.DXStreamPipeline" in source


def test_stream_pipeline_namespace_bridges_existing_public_api():
    """The split namespace is linked explicitly to the existing public DXStream API."""
    source = _read(STREAM_JS / "stream-pipeline-state.js")
    assert "window.DXStreamPipeline.publicApi = DXStream" in source


def test_stream_pipeline_state_contains_core_state():
    """stream-pipeline-state.js holds the core state variables and constants."""
    source = _read(STREAM_JS / "stream-pipeline-state.js")
    assert "DXStream._pipeState" in source
    assert "DXStream._pipeRunning" in source
    assert "var _NODE_W" in source
    assert "function _cachePipelineThemeColors(" in source
    assert "function _scheduleDraftSave(" in source


def test_stream_pipeline_api_contains_server_methods():
    """stream-pipeline-api.js holds the server API methods."""
    source = _read(STREAM_JS / "stream-pipeline-api.js")
    assert "DXStream.pipelineValidate" in source
    assert "DXStream.pipelineRun" in source
    assert "DXStream.pipelineStop" in source
    assert "DXStream.savePipelineToServer" in source
    assert "DXStream.exportPipeline" in source


def test_stream_pipeline_serialization_contains_history():
    """stream-pipeline-serialization.js holds the history/preset code."""
    source = _read(STREAM_JS / "stream-pipeline-serialization.js")
    assert "function _pushHistory(" in source
    assert "function _restoreHistory(" in source
    assert "DXStream._undo" in source
    assert "DXStream._redo" in source
    assert "DXStream.loadPreset" in source


def test_stream_pipeline_renderer_contains_canvas():
    """stream-pipeline-renderer.js holds the canvas/rendering code."""
    source = _read(STREAM_JS / "stream-pipeline-renderer.js")
    assert "function _initCanvas(" in source
    assert "function _refreshCanvas(" in source
    assert "function _drawNode(" in source
    assert "function _drawMinimap(" in source
    assert "function _canvasMouseDown(" in source


def test_stream_pipeline_bootstrap_wraps_init():
    """stream-pipeline.js keeps the pipelineInit wrapper (context menu + touch bindings)."""
    source = _read(STREAM_JS / "stream-pipeline.js")
    assert "_origPipelineInit" in source
    assert "DXStream.pipelineInit" in source


def test_stream_pipeline_bootstrap_preserves_init_promise_chain():
    """The pipelineInit wrapper preserves the original async init's Promise and error propagation."""
    source = _read(STREAM_JS / "stream-pipeline.js")
    body = _function_body(source, "DXStream.pipelineInit = async function (")
    assert "await _origPipelineInit();" in body




def test_stream_demo_dispatches_webrtc_connect_for_webrtc_mode():
    """In WebRTC mode stream-demo.js calls connect(video, ...) and passes an
    MJPEG fallback callback for a failed connection."""
    source = _read(STREAM_JS / "stream-demo.js")
    assert "DXStream.webrtc.connect(video" in source
    assert "output_mode === 'webrtc'" in source or "output_mode === 'mjpeg'" in source
    # Switch to MJPEG automatically when WebRTC cannot connect remotely/behind NAT.
    assert "_fallbackToMjpeg" in source
    assert "forceMjpeg" in source


def test_webrtc_client_exposes_payload_type_preflight():
    """webrtc-client.js can compute the browser's VP8 payload type before the server starts."""
    source = _read(STREAM_JS / "webrtc-client.js")
    assert "preferredPayloadTypes" in source
    assert "createOffer()" in source
    assert "rtpmap" in source


def test_stream_demo_sends_webrtc_payload_types_to_start():
    """The demo start request passes the browser's RTP PT (Firefox etc.) to the server."""
    source = _read(STREAM_JS / "stream-demo.js")
    assert "await DXStream.webrtc.preferredPayloadTypes()" in source
    assert "webrtcPayloadTypes" in source


def test_stream_demo_uses_mjpeg_img_for_mjpeg_mode():
    """In MJPEG mode stream-demo.js points at /api/stream/mjpeg."""
    source = _read(STREAM_JS / "stream-demo.js")
    assert "/api/stream/mjpeg" in source
    assert "output_mode === 'mjpeg'" in source


def test_stream_playback_mode_is_explicit_local_vs_remote():
    """Playback is an explicit Local (WebRTC) / Remote (MJPEG) choice.
    Remote requests forceMjpeg from the server because fMP4/MSE does not render over an SSH
    tunnel. A Local WebRTC that does not connect falls back to MJPEG."""
    js = _read(STREAM_JS / "stream-demo.js")
    html = _read(STREAM_HTML)
    assert "setPlaybackMode" in js
    assert "_playbackMode === 'remote'" in js
    assert "_startBody.forceMjpeg = true" in js
    assert 'data-mode="local"' in html and 'data-mode="remote"' in html
    # Apart from the explicit choice, a Local WebRTC that does not connect starts the MJPEG fallback after 9 s.
    wc = _read(STREAM_JS / "webrtc-client.js")
    connect_body = _function_body(wc, "function connect(")
    assert "CONNECT_TIMEOUT" in connect_body
    assert "_giveUp('timeout')" in connect_body


def test_remote_uses_fmp4_h264_over_http_via_mse():
    """When the server answers output_mode 'fmp4', the page plays fMP4 (H264) over HTTP via MSE."""
    js = _read(STREAM_JS / "stream-demo.js")
    assert "/api/stream/fmp4" in js
    assert "MediaSource" in js and "addSourceBuffer" in js
    assert "appendBuffer" in js
    assert "_showFmp4Stream" in js


def test_mjpeg_fps_uses_server_frame_counter_in_bottom_overlay():
    """MJPEG FPS polls the server frame counter (/api/stream/stats) and shows it in the single
    bottom-left #webrtc-stats-overlay (no top-right #video-overlay/#fps-display)."""
    js = _read(STREAM_JS / "stream-demo.js")
    html = _read(STREAM_HTML)
    assert "/api/stream/stats" in js
    assert "webrtc-stats-overlay" in js
    # No green top-right overlay.
    assert 'id="video-overlay"' not in html
    assert 'id="fps-display"' not in html
    # No counting of img 'load' events (unreliable).
    assert "addEventListener('load'" not in js


def test_stream_pipeline_api_dispatches_webrtc_for_webrtc_mode():
    """stream-pipeline-api.js handles WebRTC/MJPEG/fMP4 output and, like the demo page,
    requests reliable MJPEG in Remote mode (_playbackMode)."""
    source = _read(STREAM_JS / "stream-pipeline-api.js")
    assert "DXStream.webrtc.connect(pipeVideo, false, function" in source
    assert "await DXStream.webrtc.preferredPayloadTypes()" in source
    assert "webrtcPayloadTypes" in source
    assert "/api/stream/mjpeg" in source
    assert "output_mode === 'webrtc'" in source or "output_mode === 'mjpeg'" in source
    # Pipeline Builder run must honor the same Local/Remote choice as demos.
    assert "_playbackMode === 'remote'" in source
    assert "_runBody.forceMjpeg = true" in source
    assert "output_mode === 'fmp4'" in source
    assert "_fmp4PlayInto" in source


# Setup UI — no split-download option


def test_stream_setup_no_longer_sends_model_video_split_options():
    script = (STREAM_JS / "stream-setup.js").read_text(encoding="utf-8")
    assert "setup-opt-models" not in script
    assert "setup-opt-videos" not in script
    assert "body.models" not in script
    assert "body.videos" not in script


def test_stream_setup_template_hides_split_download_options():
    html = _read(STREAM_HTML)
    assert 'id="setup-opt-models"' not in html
    assert 'id="setup-opt-videos"' not in html


# Demo/Model filter & availability reason


def test_stream_demo_filters_match_dev_runtime_surface():
    """Demo filters come from the categories in /api/demos, not a fixed bar — no filter for a category
    that has no demo (classification · obb_detection)."""
    html = _read(STREAM_HTML)
    js = _read(STREAM_JS / "stream-demo.js")
    assert 'id="demo-filter-bar"' not in html
    assert "cats.push(d.category)" in js


def test_stream_model_filters_come_from_the_loaded_catalog():
    """Category buttons are built from the received list, not fixed in HTML: the list is either the manifest
    (depth estimation, no OBB) or the built-in one (OBB), so fixed buttons would mismatch one of them."""
    html = _read(STREAM_HTML)
    model_filter = html[html.index('id="models-filter-bar"'):html.index('id="models-search"')]
    assert model_filter.count("data-cat=") == 1 and 'data-cat="all"' in model_filter
    js = _read(STREAM_JS / "stream-models.js")
    assert "function _renderModelFilters(models)" in js
    assert "cats.indexOf(m.category) === -1" in js


def test_stream_model_filter_keeps_search_and_highlights_button():
    js = _read(STREAM_JS / "stream-models.js")
    body = js[js.index("DXStream.filterModels = function"):js.index("function _modelDesc")]
    assert "search.value = ''" not in body
    assert "bar.querySelector('[data-cat=\"' + cat + '\"]')" in body


def test_stream_demo_renders_unavailable_reason():
    script = (STREAM_JS / "stream-demo.js").read_text(encoding="utf-8")
    assert "function _escHtml" in script
    assert "d.availability" in script
    assert "function _demoUnavailableReason" in script
    assert "availability.reason_items" in script
    assert "_demoUnavailableReason(availability)" in script
    assert "disabled" in script


def test_stream_demo_localizes_structured_unavailable_reasons():
    script = (STREAM_JS / "stream-demo.js").read_text(encoding="utf-8")
    assert "missing_runtime_script" in script
    assert "Missing runtime script: " in script
    assert "런타임 스크립트 없음: " in script
    assert "missing_config_file" in script
    assert "Missing config file: " in script
    assert "설정 파일 없음: " in script
