"""DX Monitor dashboard regression contracts."""

from pathlib import Path
import re
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]
MONITOR = ROOT / "dx_monitor"
SHARED = ROOT / "shared" / "static"
DASHBOARD_UTILS = MONITOR / "static" / "js" / "utils.js"
DASHBOARD_JS = MONITOR / "static" / "js" / "dashboard.js"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


_DASHBOARD_TELEMETRY_VM = r"""
const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

const elements = {};
function makeElement() {
    return {className: '', style: {display: 'none'}, textContent: '', innerHTML: ''};
}
[
    'mock-banner', 'telemetry-status', 'status-bar', 'npu-status-label',
    'npu-topo', 'chart-area'
].forEach(function(id) { elements[id] = makeElement(); });

const context = {
    console,
    localStorage: {getItem() { return 'en'; }},
    document: {
        documentElement: {},
        getElementById(id) { return elements[id] || null; },
        createElement() {
            let html = '';
            return {
                set textContent(value) { html = String(value); },
                get innerHTML() { return html; },
            };
        },
    },
    getComputedStyle() {
        return {getPropertyValue() { return '#000'; }};
    },
    requestAnimationFrame() {},
    setInterval() { return 1; },
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), context, {filename: process.argv[1]});
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), context, {filename: process.argv[2]});

function npu() {
    return {
        id: 0,
        cores: 1,
        temperatures: [42.0],
        temp_avg: 42.0,
        voltage_avg: 700.0,
        clock_avg: 900.0,
        dram_pct: 25.0,
        utilization: [15.0],
    };
}
function apply(payload) {
    context.__payload = payload;
    vm.runInContext('_applyHWData(__payload)', context);
}
function state() {
    return JSON.parse(vm.runInContext(
        'JSON.stringify({mode:S.telemetryMode,isMock:S.isMock,samples:S.rtData.length})',
        context,
    ));
}

apply({npus: [npu()], cpu_load: 2.0, mem_pct: 30.0, telemetry: {source_mode: 'real'}});
assert.deepStrictEqual(state(), {mode: 'real', isMock: false, samples: 1});
assert.strictEqual(elements['telemetry-status'].style.display, 'none');
assert.strictEqual(elements['mock-banner'].style.display, 'none');

apply({npus: [npu()], cpu_load: 2.0, mem_pct: 30.0, telemetry: {source_mode: 'stale'}});
assert.strictEqual(state().mode, 'stale');
assert(elements['telemetry-status'].className.includes('degraded stale'));
assert.strictEqual(elements['telemetry-status'].textContent, '⚠ NPU telemetry is not current.');
assert.strictEqual(elements['telemetry-status'].style.display, 'inline');
assert(elements['status-bar'].innerHTML.includes('NPU telemetry is not current'));

apply({
    npus: [], cpu_load: 2.0, mem_pct: 30.0,
    telemetry: {source_mode: 'unavailable', diagnostics: ['worker offline']},
});
assert.strictEqual(state().mode, 'unavailable');
assert(elements['telemetry-status'].className.includes('degraded unavailable'));
assert(elements['telemetry-status'].textContent.includes('worker offline'));
assert(elements['status-bar'].innerHTML.includes('NPU telemetry unavailable'));
assert(elements['npu-topo'].innerHTML.includes('NPU telemetry unavailable'));
vm.runInContext("S.chartMode='all'; drawCharts();", context);
assert(elements['chart-area'].innerHTML.includes('NPU telemetry unavailable'));
assert(elements['chart-area'].innerHTML.includes('chart-grid-system'));

apply({npus: [npu()], cpu_load: 2.0, mem_pct: 30.0, telemetry: {source_mode: 'mock'}});
assert.strictEqual(state().mode, 'mock');
assert.strictEqual(state().isMock, true);
assert.strictEqual(elements['telemetry-status'].style.display, 'none');
assert.strictEqual(elements['mock-banner'].style.display, 'inline');
assert(elements['mock-banner'].textContent.includes('Mock Mode'));
assert(elements['status-bar'].innerHTML.includes('Mock'));
assert.strictEqual(elements['npu-status-label'].textContent, 'Mock Data');
assert(elements['npu-topo'].innerHTML.includes('Mock'));

apply({npus: [npu()], cpu_load: 2.0, mem_pct: 30.0});
assert.strictEqual(state().mode, 'real');
assert.strictEqual(state().isMock, false);
assert.strictEqual(elements['telemetry-status'].style.display, 'none');
assert.strictEqual(elements['mock-banner'].style.display, 'none');
assert(elements['status-bar'].innerHTML.includes('Mock') === false);
assert.strictEqual(elements['npu-status-label'].textContent, '1 NPU(s)');
assert.strictEqual(state().samples, 5);

console.log('OK: dashboard telemetry transitions');
"""


def run_dashboard_telemetry_vm() -> str:
        node = shutil.which("node")
        if not node:
                pytest.skip("node is required for dashboard runtime test")
        result = subprocess.run(
                [node, "-e", _DASHBOARD_TELEMETRY_VM, str(DASHBOARD_UTILS), str(DASHBOARD_JS)],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        return result.stdout


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


def test_dashboard_source_uses_plain_es5_syntax_only():
    """Reject ES6+ syntax/APIs in the authored dashboard source only.

    This contract deliberately permits ordinary functions, callbacks, Promise
    chaining, and other ES5-compatible behavior. It does not inspect bundled
    or minified assets.
    """
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    prohibited_patterns = {
        r"\basync\s+function\b": "async function",
        r"\bawait\s+": "await",
        r"\bconst\b": "const",
        r"\bconst\s*\[": "const destructuring",
        r"\bPromise\.all\b": "Promise.all",
        r"\bNumber\.isFinite\b": "Number.isFinite",
        r"\.fill\s*\(": "Array.prototype.fill",
        r"\bArray\.from\b": "Array.from",
    }

    for pattern, feature in prohibited_patterns.items():
        assert not re.search(pattern, dashboard), f"dashboard source uses {feature}"


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
    refresh_body = extract_braced_body(dashboard, "function refreshDash()")

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


def test_telemetry_status_template_and_clock_control_contract():
    """The dashboard exposes telemetry status and a deterministic Clock icon."""
    template = read_text(MONITOR / "templates" / "index.html")

    assert 'id="telemetry-status"' in template
    assert template.index('id="sse-status"') < template.index('id="telemetry-status"')
    assert "cm-clock" in template
    assert "🔄" not in template
    assert 'class="icon-clock"' in template
    assert 'aria-hidden="true"' in template
    assert "��" not in template


def test_clock_controls_use_deterministic_accessibility_icon():
    """Static and dynamic Clock labels must not rely on an emoji glyph."""
    template = read_text(MONITOR / "templates" / "index.html")
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    css = read_text(MONITOR / "static" / "css" / "style.css")

    assert "🔄" not in template
    assert "🔄" not in dashboard
    assert 'class="icon-clock"' in template
    assert 'class="icon-clock"' in dashboard
    assert 'aria-hidden="true"' in dashboard
    assert ".icon-clock" in css
    assert "currentColor" in css


def test_dashboard_tracks_telemetry_mode_and_safely_updates_visible_status():
    """Every hardware payload must update a safe, user-visible stale/unavailable state."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    refresh_body = extract_braced_body(dashboard, "function refreshDash()")
    apply_body = extract_braced_body(dashboard, "function _applyHWData(d)")
    telemetry_body = extract_braced_body(dashboard, "function _updateTelemetryStatus(hw)")

    assert "telemetry.source_mode" in dashboard
    assert "S.telemetryMode" in telemetry_body
    assert "_updateTelemetryStatus(hw)" in refresh_body
    assert "_updateTelemetryStatus(d)" in apply_body
    assert "stale" in telemetry_body and "unavailable" in telemetry_body
    assert "textContent" in telemetry_body
    assert "diagnostics" in telemetry_body and "error" in telemetry_body
    assert "innerHTML" not in telemetry_body, (
        "telemetry diagnostics must not be injected as HTML"
    )


def test_polling_applies_valid_telemetry_payloads_even_when_they_include_errors():
    """An unavailable payload may include ``error`` and still must reach the renderer."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    poll_body = extract_braced_body(dashboard, "function _startHWPoll()")

    assert "_applyHWData(d)" in poll_body
    assert "d&&!d.error" not in poll_body.replace(" ", "")
    assert re.search(r"if\s*\(d\s*&&\s*typeof d\s*===\s*['\"]object['\"]\)", poll_body), (
        "polling must apply every object payload, including unavailable payloads with errors"
    )


def test_telemetry_state_invalidates_status_and_chart_layout_caches():
    """Changing real/stale/unavailable/mock must rebuild cached dashboard DOM."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    status_body = extract_braced_body(dashboard, "function _hwStatusSignature(hw)")
    single_body = extract_braced_body(
        dashboard, "function _drawSingleMode(area,data,tl,npuCount,mode)"
    )
    all_body = extract_braced_body(dashboard, "function _drawAllMode(area,data,tl,npuCount)")
    single_key = re.search(r"var layoutKey=([^;]+);", single_body)
    all_key = re.search(r"var layoutKey=([^;]+);", all_body)

    assert "telemetryMode" in status_body
    assert single_key and "telemetryMode" in single_key.group(1)
    assert all_key and "telemetryMode" in all_key.group(1)


def test_npu_telemetry_no_data_messages_preserve_system_charts():
    """Unavailable/stale NPU telemetry must not remove CPU, memory, and core charts."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    status_body = extract_braced_body(dashboard, "function renderStatusBar(hw)")
    topo_body = extract_braced_body(dashboard, "function renderNPUTopo(hw)")
    single_body = extract_braced_body(
        dashboard, "function _drawSingleMode(area,data,tl,npuCount,mode)"
    )
    all_body = extract_braced_body(dashboard, "function _drawAllMode(area,data,tl,npuCount)")

    assert "NPU telemetry unavailable" in status_body
    assert "NPU telemetry unavailable" in topo_body
    assert "NPU telemetry unavailable" in single_body
    assert "NPU telemetry unavailable" in all_body
    assert 'data-help-id="npu-telemetry-no-data"' in all_body
    assert "chart-grid-system" in all_body
    assert all_body.index('data-help-id="npu-telemetry-no-data"') < all_body.index(
        'data-help-id="chart-label-system"'
    )


def test_dashboard_resolves_nested_mock_and_legacy_telemetry_states():
    """Nested worker provenance must drive mock UI state without breaking legacy APIs."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    state_body = extract_braced_body(dashboard, "function _telemetryState(hw)")
    refresh_body = extract_braced_body(dashboard, "function refreshDash()")
    apply_body = extract_braced_body(dashboard, "function _applyHWData(d)")

    assert "telemetry.source_mode==='mock'" in state_body
    assert "return'real'" in state_body, (
        "legacy successful hardware payloads without telemetry provenance must remain usable"
    )
    assert "S.isMock=_telemetryState(hw)==='mock'" in refresh_body
    assert "S.isMock=_telemetryState(d)==='mock'" in apply_body


def test_nested_mock_provenance_labels_status_and_topology_cards():
    """Nested mock provenance must label every UI surface, not only the banner."""
    dashboard = read_text(MONITOR / "static" / "js" / "dashboard.js")
    status_body = extract_braced_body(dashboard, "function renderStatusBar(hw)")
    topo_body = extract_braced_body(dashboard, "function renderNPUTopo(hw)")

    assert "var mockMode=_telemetryState(hw)==='mock';" in status_body
    assert "n.mock||mockMode" in status_body
    assert "var mockMode=_telemetryState(hw)==='mock';" in topo_body
    assert "mockMode?T('Mock Data')" in topo_body
    assert "n.mock||mockMode" in topo_body


def test_dashboard_telemetry_state_transitions_at_runtime():
    """Execute real/stale/unavailable/mock/legacy payload transitions in Node."""
    assert "OK: dashboard telemetry transitions" in run_dashboard_telemetry_vm()


def test_charts_redraw_on_resize_and_visibility():
    """Launcher embeds each module in an <iframe>; the first drawCharts() can run before
    the iframe is laid out/visible, and without a resize/visibility redraw the charts stay
    blank until a manual reload. The dashboard must install a ResizeObserver on the chart
    area plus resize/visibility/pageshow redraws so charts render on first show."""
    dashboard = read_text(DASHBOARD_JS)
    assert "ResizeObserver" in dashboard and "chart-area" in dashboard
    assert "visibilitychange" in dashboard
    assert "'resize'" in dashboard or '"resize"' in dashboard
    # each hook must trigger a chart redraw
    assert "requestAnimationFrame(drawCharts)" in dashboard
