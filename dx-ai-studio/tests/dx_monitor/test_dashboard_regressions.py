"""DX Monitor dashboard regression contracts."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
MONITOR = ROOT / "dx_monitor"
SHARED = ROOT / "shared" / "static"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_braced_body(source: str, anchor: str) -> str:
    start = source.find(anchor)
    assert start != -1, f"anchor {anchor!r} not found"
    open_pos = source.find("{", start)
    assert open_pos != -1, f"opening brace after {anchor!r} not found"
    depth = 0
    for pos in range(open_pos, len(source)):
        char = source[pos]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[open_pos + 1:pos]
    raise AssertionError(f"unmatched braces after {anchor!r}")


def css_rule(css: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{([^}}]+)\}}", css)
    assert match, f"{selector} rule not found"
    return match.group(1)


def test_dashboard_never_renders_negative_npu_dram_percent():
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    status_body = extract_braced_body(dashboard, "function renderStatusBar(hw)")
    topo_body = extract_braced_body(dashboard, "function renderNPUTopo(hw)")

    assert "function _normalizeDramPct" in dashboard
    assert "function _formatDramPct" in dashboard
    assert "_formatDramPct(worstDram)" in status_body
    assert "_formatDramPct(dramPct)" in topo_body
    assert "worstDram.toFixed(1)+'%'" not in status_body
    assert "(n.dram_pct||0).toFixed(1)+'%'" not in topo_body


def test_dashboard_keeps_invalid_npu_dram_out_of_realtime_series():
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    apply_body = extract_braced_body(dashboard, "function _applyHWData(d)")
    extract_body = extract_braced_body(dashboard, "function _extractSeries(data,cfg,npuIdx)")

    assert "dram:_normalizeDramPct(n.dram_pct)" in apply_body
    assert "dram:+(n.dram_pct||0).toFixed(1)" not in apply_body
    assert "n?_seriesValue(n[cfg.npuKey]):null" in extract_body


def test_shared_line_chart_skips_missing_metric_samples():
    charts = read_text(SHARED / "dx-charts.js")
    draw_body = extract_braced_body(charts, "function drawLineChart(canvas,datasets,opts)")

    assert "function _chartFiniteValues" in charts
    assert "_chartFiniteValues(datasets)" in draw_body
    assert "if(_chartFiniteValues([ds]).length<2)return" in draw_body
    assert "if(v==null||!Number.isFinite(v))" in draw_body
    assert "ctx.moveTo" in draw_body and "ctx.lineTo" in draw_body


def test_monitor_language_menu_parent_stacks_above_monitor_content():
    css = read_text(MONITOR / "static" / "css" / "style.css")
    top_bar = css_rule(css, ".top-bar")
    toolbar = css_rule(css, ".toolbar")
    monitor_main = css_rule(css, ".monitor-main")

    z_match = re.search(r"z-index\s*:\s*(\d+)\s*;", top_bar)
    assert z_match, ".top-bar must declare an explicit z-index"
    assert int(z_match.group(1)) >= 1000
    assert "overflow: visible" in top_bar
    assert "position: relative" in toolbar
    toolbar_z = re.search(r"z-index\s*:\s*(\d+)\s*;", toolbar)
    assert toolbar_z, ".toolbar must stack language dropdown above toolbar siblings"
    assert int(toolbar_z.group(1)) >= 1
    # Must not tie with shared popup layer (10000)
    assert int(toolbar_z.group(1)) != 10000
    assert "z-index" not in monitor_main




def test_sse_reconnect_delay_not_30s():
    """Client SSE reconnect delay must not be 30000ms (too long)."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    assert "setTimeout(startSSE,30000)" not in dashboard, (
        "SSE reconnect delay is still 30000ms — should be ≤5000ms"
    )


def test_sse_error_handler_exposes_degraded_state():
    """SSE onerror must expose a degraded/fallback state indicator in the DOM."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    sse_error_body = extract_braced_body(dashboard, "S.sseSource.onerror=function()")
    assert "degraded" in sse_error_body or "sse-status" in sse_error_body, (
        "SSE error handler must expose a visible degraded/fallback state"
    )


def test_draw_all_mode_does_not_replace_inner_html_every_tick():
    """_drawAllMode must cache layout and skip innerHTML when chart set is unchanged."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    all_body = extract_braced_body(dashboard, "function _drawAllMode(area,data,tl,npuCount)")
    assert "_chartLayoutKey" in all_body, (
        "_drawAllMode must use a layout key to cache DOM structure"
    )
    # area.innerHTML=h must only appear inside a _chartLayoutKey conditional block
    assert re.search(r"_chartLayoutKey\s*!==\s*layoutKey", all_body), (
        "_drawAllMode must compare _chartLayoutKey to detect layout changes"
    )


def test_draw_single_mode_does_not_replace_inner_html_every_tick():
    """_drawSingleMode must cache layout and skip innerHTML when chart set is unchanged."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    single_body = extract_braced_body(dashboard, "function _drawSingleMode(area,data,tl,npuCount,mode)")
    assert "_chartLayoutKey" in single_body, (
        "_drawSingleMode must use a layout key to cache DOM structure"
    )
    assert re.search(r"_chartLayoutKey\s*!==\s*layoutKey", single_body), (
        "_drawSingleMode must compare _chartLayoutKey to detect layout changes"
    )




def test_sse_timeout_callback_schedules_reconnect():
    """SSE 6-second timeout path must schedule setTimeout(startSSE,...) after fallback."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    timeout_body = extract_braced_body(
        dashboard, "var sseTimeout=setTimeout(function()"
    )
    assert "setTimeout(startSSE" in timeout_body, (
        "SSE timeout callback must schedule reconnect via setTimeout(startSSE,...)"
    )


def test_layout_key_includes_mock_flag_single():
    """_drawSingleMode layout key must include S.isMock so mock label changes rebuild DOM."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    single_body = extract_braced_body(
        dashboard, "function _drawSingleMode(area,data,tl,npuCount,mode)"
    )
    key_match = re.search(r"var layoutKey=([^;]+);", single_body)
    assert key_match, "layoutKey assignment not found in _drawSingleMode"
    assert "isMock" in key_match.group(1) or "mock" in key_match.group(1).lower(), (
        "_drawSingleMode layoutKey must include S.isMock"
    )


def test_layout_key_includes_mock_flag_all():
    """_drawAllMode layout key must include S.isMock so mock label changes rebuild DOM."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    all_body = extract_braced_body(
        dashboard, "function _drawAllMode(area,data,tl,npuCount)"
    )
    key_match = re.search(r"var layoutKey=([^;]+);", all_body)
    assert key_match, "layoutKey assignment not found in _drawAllMode"
    assert "isMock" in key_match.group(1) or "mock" in key_match.group(1).lower(), (
        "_drawAllMode layoutKey must include S.isMock"
    )




def test_events_no_duplicate_initial_fetch():
    """pollEvents() must not be called immediately after setInterval(pollEvents,...).

    The pattern `setInterval(pollEvents,...); pollEvents();` causes a redundant
    initial HTTP request.  Either guard with a first-run flag or remove the
    immediate call so the first poll happens only after the interval fires.
    """
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    # The raw unguarded pattern must not appear
    assert "setInterval(pollEvents" in dashboard, "setInterval(pollEvents) must exist"
    lines = dashboard.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("setInterval(pollEvents"):
            # Next non-blank line must NOT be a bare `pollEvents();`
            for j in range(i + 1, min(i + 3, len(lines))):
                next_line = lines[j].strip()
                if not next_line:
                    continue
                assert next_line != "pollEvents();", (
                    "Immediate pollEvents() after setInterval causes double initial fetch. "
                    "Remove the bare call or guard it with a first-run flag."
                )
                break


def test_monitor_z_index_ladder_no_shared_toolbar_conflict():
    """Monitor z-index layers must not tie with shared toolbar popup z-index (10000).

    .top-bar should sit in the header band (1000–9999).
    .toolbar should position children but NOT use the same z-index as the shared
    lang-menu popup (10000 in toolbar.css).
    """
    css = read_text(MONITOR / "static" / "css" / "style.css")
    toolbar_rule = css_rule(css, ".toolbar")

    # Shared toolbar.css .dx-lang-menu uses z-index:10000
    # Monitor .toolbar must NOT also declare z-index:10000
    toolbar_z = re.search(r"z-index\s*:\s*(\d+)", toolbar_rule)
    if toolbar_z:
        val = int(toolbar_z.group(1))
        assert val != 10000, (
            ".toolbar z-index must not equal shared .dx-lang-menu popup layer (10000)"
        )


def test_mock_mode_page_level_banner_exists():
    """When S.isMock is true, a page-level mock indicator must be rendered.

    The mock banner must be set from refreshDash or _applyHWData so it is
    visible on first load — not only inside detailed NPU topology cards.
    """
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")

    # There must be a mock-banner or mock-indicator element reference
    assert "mock-banner" in dashboard, (
        "Dashboard must reference a 'mock-banner' element for page-level mock indicator"
    )

    # The banner must be updated from _applyHWData or renderStatusBar or refreshDash
    apply_body = extract_braced_body(dashboard, "function _applyHWData(d)")
    status_body = extract_braced_body(dashboard, "function renderStatusBar(hw)")
    refresh_body = extract_braced_body(dashboard, "async function refreshDash()")

    # Direct reference or via _updateMockBanner helper
    mock_update_found = (
        "mock-banner" in apply_body
        or "mock-banner" in status_body
        or "mock-banner" in refresh_body
        or "_updateMockBanner" in apply_body
        or "_updateMockBanner" in status_body
        or "_updateMockBanner" in refresh_body
    )
    assert mock_update_found, (
        "mock-banner must be updated in _applyHWData, renderStatusBar, or refreshDash "
        "(directly or via _updateMockBanner)"
    )


def test_mock_banner_show_overrides_css_display_none():
    """_updateMockBanner must set an explicit display value (not empty string)
    when showing the banner, because .mock-banner CSS has display:none.

    Setting el.style.display='' removes the inline override and lets the
    CSS display:none win, keeping the banner invisible.
    """
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    banner_body = extract_braced_body(dashboard, "function _updateMockBanner()")

    # The show branch must NOT use display='' (empty string)
    assert "el.style.display=''" not in banner_body, (
        "_updateMockBanner sets display='' which cannot override CSS display:none. "
        "Use an explicit value like 'inline' or 'inline-block'."
    )

    # The show branch must use an explicit display value
    show_match = re.search(r"el\.style\.display='(inline(?:-block)?|block)'", banner_body)
    assert show_match, (
        "_updateMockBanner must set display to 'inline', 'inline-block', or 'block' "
        "to override the CSS display:none rule."
    )


def test_dashboard_shows_no_data_for_npu_with_no_valid_temperature_sensors():
    """F-15: a dead temperature sensor (cores==0, all channels == -32768 sentinel) must
    NOT render as '0.0°C' with an OK/green badge. The temp card must guard on cores/
    temperatures and fall back to a no-data state."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    # A cores/temperatures guard must gate the temperature rendering.
    assert re.search(r"n\.cores[^\n]*n\.temperatures|hasTemp", dashboard), \
        "NPU temp card does not guard on cores/temperatures (F-15)"
    # The °C value must be conditional (not unconditionally temp_avg||0).
    assert "hasTemp?" in dashboard.replace(" ", ""), \
        "temperature value is not conditional on sensor validity (F-15)"
