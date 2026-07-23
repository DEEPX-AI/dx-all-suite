from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
JS_DIR = ROOT / "dx_app/static/js"
SHARED_I18N = ROOT / "shared/static/i18n.js"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def test_inference_run_media_is_cached_and_selection_is_incremental():
    source = _read(JS_DIR / "inference.js")
    load_body = _function_body(source, "function loadRunImages(")
    pick_body = _function_body(source, "function pickImg(")

    assert "var _runMediaCache={};" in source
    assert "var _lastRunImageCategory=null;" in source
    assert "_renderRunMedia(cat,_runMediaCache[cat]);" in load_body
    # images + videos are still fetched together and cached per category; the images URL
    # now carries a ?category= filter (built into imgUrl above the Promise.all).
    assert "Promise.all([api(imgUrl),api('/api/videos')])" in load_body
    assert "/api/images?category=" in load_body
    assert "document.querySelectorAll('.img-item')" not in pick_body
    assert "var _lastSelectedRunImageEl=null;" in source
    assert "_lastSelectedRunImageEl.classList.remove('selected')" in pick_body


def test_live_sparkline_reuses_svg_nodes_instead_of_replacing_html():
    source = _read(JS_DIR / "inference.js")
    update_body = _function_body(source, "function _updateSlotStats(")

    assert "function _updateLiveSparkline(" in source
    assert "_updateLiveSparkline(chartEl,lslot.confHistory,400,42);" in update_body
    assert "chartEl.innerHTML" not in update_body
    assert "polyline.setAttribute('points',geom.pts)" in source
    assert "circle.setAttribute('cx',geom.lx.toFixed(1))" in source



def test_charts_resize_canvas_only_when_size_changes():
    source = _read(ROOT / "shared" / "static" / "dx-charts.js")
    line_body = _function_body(source, "function drawLineChart(")
    bar_body = _function_body(source, "function drawBarChart(")

    assert "function _prepareChartCanvas(" in source
    assert "if(canvas.width!==pixelW||canvas.height!==pixelH)" in source
    assert "ctx.setTransform(1,0,0,1,0,0)" in source
    assert "var prepared=_prepareChartCanvas(canvas,true)" in line_body
    assert "var prepared=_prepareChartCanvas(canvas,false)" in bar_body
    assert "canvas.width=W*2" not in line_body
    assert "canvas.width=W*2" not in bar_body
    assert "getBoundingClientRect()" not in line_body
    assert "getBoundingClientRect()" not in bar_body


def test_i18n_apply_lang_can_scope_to_active_page_only():
    utils = _read(JS_DIR / "utils.js")
    shared = _read(SHARED_I18N)
    nav_body = _function_body(utils, "function nav(")
    refresh_body = _function_body(utils, "function refreshActivePageLanguage(")

    assert "function _applyLangToActivePage(" in utils
    assert "DXI18n.applyLang(active||document)" in utils
    assert "_applyLangToActivePage();" in nav_body
    assert "_applyLangToActivePage();" in refresh_body
    assert "function _applyDOM(root)" in shared
    assert "var scope = root || document;" in shared


def test_notification_history_rerenders_only_when_drawer_is_open():
    source = _read(JS_DIR / "utils.js")
    refresh_body = _function_body(source, "function refreshActivePageLanguage(")

    assert "function _isNotifDrawerOpen(" in source
    assert "if(_isNotifDrawerOpen())_renderNotifHistory();" in refresh_body


def test_setup_log_polling_append_only_new_content():
    # The in-app compiler was removed; the append-only log renderer (compRenderLogAppend)
    # now lives in setup.js and is used by the Setup page's step-log poller.
    setup = _read(JS_DIR / "setup.js")
    setup_start = _function_body(setup, "function _setupDoRun(")
    setup_poll = _function_body(setup, "function setupPollLog(")

    assert "function compRenderLogAppend(" in setup
    assert "SETUP._renderedLogText='';" in setup_start
    assert "compRenderLogAppend(logEl,r.log,SETUP);" in setup_poll
    assert "logEl.innerHTML=compColorLog(r.log)" not in setup_poll


def test_live_timer_updates_at_display_resolution_only():
    source = _read(JS_DIR / "inference.js")
    start_body = _function_body(source, "async function contStart(")

    assert "setInterval(function(){" in start_body
    assert "},1000);" in start_body
    assert "},500);" not in start_body


def test_continuous_result_status_skips_same_value_text_writes():
    source = _read(JS_DIR / "inference.js")
    result_body = _function_body(source, "function contShowResult(")

    assert "function setTextIfChanged(" in source
    assert "setTextIfChanged(statusEl,T('❌ Error'));" in result_body
    assert "setTextIfChanged(statusEl,T('✅ Done'));" in result_body
    assert "setTextIfChanged(fpsEl,res.fps+' FPS');" in result_body
    assert "statusEl.textContent" not in result_body
    assert "fpsEl.textContent" not in result_body


def test_toolbar_settings_uses_global_nav_not_private_goPage():
    html = (ROOT / "dx_app/templates/index.html").read_text(encoding="utf-8")
    assert "onSettings: function(){ nav('setup'); }" in html
    assert "onSettings: function(){ goPage('setup'); }" not in html


def test_inference_error_hints_use_i18n_not_korean_literals():
    source = _read(JS_DIR / "inference.js")
    korean_fragments = [
        "dx_engine\uc774 \uc2e4\ud589 \uc911\uc778\uc9c0",
        "\ubaa8\ub378 \ud30c\uc77c \ub610\ub294 \uc2e4\ud589\ud30c\uc77c",
        "\ucd94\ub860 \uc2dc\uac04\uc774 \ucd08\uacfc",
    ]
    for frag in korean_fragments:
        assert frag not in source, (
            f"inference.js still contains Korean literal: {frag!r}"
        )
    assert "T('Check that dx_engine is running" in source
    assert "T('Check the model file or executable path" in source
    assert "T('Inference timed out" in source


def test_benchmark_error_badge_shown_regardless_of_exit_code():
    """res.error must produce ERROR badge even when exit_code is non-null."""
    source = _read(JS_DIR / "benchmark.js")
    doBench_body = _function_body(source, "async function doBench(")
    detail_body = _function_body(source, "function showBenchDetail(")
    report_body = _function_body(source, "function benchExportReport(")

    # isErr must be !!res.error (truthy check), not res.error && res.exit_code==null
    assert "var isErr=!!res.error;" in doBench_body, (
        "doBench: isErr should be !!res.error, not gated on exit_code==null"
    )
    assert "res.error&&res.exit_code==null" not in doBench_body, (
        "doBench: still uses old exit_code==null gate for error detection"
    )
    # showBenchDetail error banner must not gate on exit_code==null
    assert "r.error&&r.exit_code==null" not in detail_body, (
        "showBenchDetail: error banner still gated on exit_code==null"
    )
    assert "if(r.error){" in detail_body, (
        "showBenchDetail: error banner should trigger on any truthy r.error"
    )
    # benchReport status must not gate on exit_code==null
    assert "r.error&&r.exit_code==null" not in report_body, (
        "benchReport: status still gated on exit_code==null"
    )


def test_compare_set_ab_cols_no_document_click_listener_leak():
    """setABCols must not leak anonymous document click listeners on every call."""
    source = _read(JS_DIR / "compare.js")
    body = _function_body(source, "function setABCols(")

    # Must use stored handler to avoid leak
    assert "var _abDocClickHandler=" in source or "_abDocClickHandler=null" in source, (
        "compare.js missing _abDocClickHandler for listener management"
    )
    # Must remove old listener before adding new one
    assert "document.removeEventListener('click',_abDocClickHandler)" in body, (
        "setABCols does not remove previous click listener before adding a new one"
    )
    assert "_abDocClickHandler=function(e){" in body, (
        "setABCols does not assign handler to _abDocClickHandler"
    )


def test_continuous_processing_state_set_per_slot_not_pre_marked():
    """Processing class must only be set inside the sequential loop,
    not pre-applied to all slots before the loop starts."""
    source = _read(JS_DIR / "inference.js")
    start_body = _function_body(source, "async function contStart(")
    grid_body = _function_body(source, "function contRenderGrid(")

    # contRenderGrid must NOT pre-set processing class or processing text
    assert "processing" not in grid_body, (
        "contRenderGrid pre-marks slots with processing class"
    )
    assert "Processing" not in grid_body, (
        "contRenderGrid pre-marks slots with Processing text"
    )
    # contStart must set processing state inside the for loop (already is per-slot)
    assert "slot.className='cont-slot processing'" in start_body or \
           'slot.className="cont-slot processing"' in start_body, (
        "contStart must set processing class per-slot in the sequential loop"
    )

    # Slots waiting for their turn should show 'Waiting…' not 'Processing…'
    assert "T('⏳ Waiting…')" in grid_body or "T('▶ Press Start to begin inference')" in grid_body, (
        "contRenderGrid should show a non-processing placeholder for pending slots"
    )


def test_run_media_cache_has_ttl_or_invalidation():
    """_runMediaCache must have TTL metadata or an invalidation function."""
    source = _read(JS_DIR / "inference.js")

    # Must have an invalidation function
    assert "function _invalidateRunMediaCache(" in source, (
        "inference.js missing _invalidateRunMediaCache() function"
    )
    # Cache entries should have a timestamp for TTL
    load_body = _function_body(source, "function loadRunImages(")
    assert "_ts:" in load_body or "Date.now()" in load_body, (
        "loadRunImages does not store timestamp for cache TTL"
    )


def test_initCmpSlider_no_anonymous_document_listener_leak():
    """initCmpSlider must store handler refs and remove them on drag stop."""
    source = _read(JS_DIR / "inference.js")
    body = _function_body(source, "function initCmpSlider(")

    # Must store handler references in named variables, not anonymous functions
    assert "document.addEventListener('mousemove',function(e)" not in body, (
        "initCmpSlider leaks anonymous mousemove listener on document"
    )
    assert "document.addEventListener('mouseup',function(" not in body, (
        "initCmpSlider leaks anonymous mouseup listener on document"
    )
    assert "document.addEventListener('touchmove',function(e)" not in body, (
        "initCmpSlider leaks anonymous touchmove listener on document"
    )
    assert "document.addEventListener('touchend',function(" not in body, (
        "initCmpSlider leaks anonymous touchend listener on document"
    )

    # Must remove document listeners when drag stops
    assert "document.removeEventListener('mousemove'" in body, (
        "initCmpSlider never removes mousemove listener from document"
    )
    assert "document.removeEventListener('mouseup'" in body, (
        "initCmpSlider never removes mouseup listener from document"
    )
    assert "document.removeEventListener('touchmove'" in body, (
        "initCmpSlider never removes touchmove listener from document"
    )
    assert "document.removeEventListener('touchend'" in body, (
        "initCmpSlider never removes touchend listener from document"
    )


def test_invalidateRunMediaCache_called_outside_own_definition():
    """_invalidateRunMediaCache must be called somewhere other than its definition."""
    source = _read(JS_DIR / "inference.js")
    # Remove the function definition to find call sites
    defn_body = _function_body(source, "function _invalidateRunMediaCache(")
    defn_start = source.index("function _invalidateRunMediaCache(")
    defn_end = defn_start + len("function _invalidateRunMediaCache(") + len(defn_body) + 2
    rest = source[:defn_start] + source[defn_end:]

    assert "_invalidateRunMediaCache(" in rest, (
        "_invalidateRunMediaCache is defined but never called anywhere"
    )


def test_doRun_has_inflight_guard_before_await():
    """doRun must set an in-flight guard or disable r-run-btn before awaiting postJ."""
    source = _read(JS_DIR / "inference.js")
    body = _function_body(source, "async function doRun(")

    # Must check and set a guard at the top of the function
    assert "_runInFlight" in body, (
        "doRun missing _runInFlight guard variable"
    )
    # Guard must be checked early (return if already in flight)
    assert (
        "if(_runInFlight)return;" in body
        or "if(_runInFlight){return;}" in body
        or "if(_runInFlight){return}" in body
        or "if(_runInFlight){toast(T('Run already in progress'),'warn');return}" in body
    ), (
        "doRun does not early-return when _runInFlight is true"
    )
    # Guard must be set before the await
    guard_set_pos = body.index("_runInFlight=true")
    await_pos = body.index("await postJ")
    assert guard_set_pos < await_pos, (
        "doRun sets _runInFlight after the await instead of before"
    )
    # Guard must be cleared in a finally block
    assert "_runInFlight=false" in body, (
        "doRun never resets _runInFlight to false"
    )
    assert "finally{" in body or "finally {" in body, (
        "doRun does not use try/finally to guarantee guard reset"
    )

    # Module-level declaration
    assert "var _runInFlight=false;" in source, (
        "inference.js missing top-level _runInFlight declaration"
    )


def test_setup_run_all_button_has_exactly_one_span_per_language():
    """setup-run-all button must have exactly one span per language."""
    html = (ROOT / "dx_app/templates/index.html").read_text(encoding="utf-8")
    import re
    # Extract the setup-run-all button element
    match = re.search(r'id="setup-run-all"[^>]*>(.*?)</button>', html, re.DOTALL)
    assert match, "setup-run-all button not found in index.html"
    btn_content = match.group(1)
    expected_langs = ["ko", "en", "es", "ja", "zh-CN", "zh-TW"]
    for lang in expected_langs:
        count = btn_content.count(f'class="{lang}"')
        assert count == 1, (
            f"setup-run-all button has {count} <span class=\"{lang}\"> elements, expected exactly 1"
        )
