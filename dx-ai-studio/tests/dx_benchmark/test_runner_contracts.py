"""Static-asset behavior checks for the benchmark dashboard/settings frontend.

NOTE: this file used to also cover contract conformance for the vendored
dx_benchmark/core/ runner package (BenchmarkResultProtocol, ModelResult,
PipelineResult, pipeline_sweeps, report_models, report_renderers,
run_orchestrator, reporter). That package was removed — the studio is a pure
viewer now and benchmark execution lives in the standalone dx-benchmark tool.
The tests below, which only exercise the bundled static JS, are unaffected
and were kept.
"""

from pathlib import Path

_JS_ROOT = Path(__file__).resolve().parents[2] / "dx_benchmark" / "static" / "js"


def _read_js(name: str) -> str:
    return (_JS_ROOT / name).read_text(encoding="utf-8")


def _extract_function_body(source: str, name: str) -> str:
    anchor = f"function {name}("
    start = source.find(anchor)
    assert start != -1, f"{name} function not found"
    open_pos = source.find("{", start)
    assert open_pos != -1, f"{name} opening brace not found"
    depth = 0
    for pos in range(open_pos, len(source)):
        char = source[pos]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[open_pos + 1:pos]
    raise AssertionError(f"{name} function braces are not balanced")


class TestDashboardNoLocalhostEdgeGuide:
    """dashboard.js must not hardcode http://localhost:8096."""

    def test_dashboard_js_no_localhost_8096(self):
        src = _read_js("dashboard.js")
        assert "http://localhost:8096" not in src, (
            "dashboard.js must not hardcode http://localhost:8096 for EdgeGuide"
        )

    def test_dashboard_js_no_fixed_8096_edgeguide_port(self):
        src = _read_js("dashboard.js")
        assert ":8096" not in src, (
            "dashboard.js must derive direct EdgeGuide links from origin/config, not fixed :8096"
        )

    def test_dashboard_js_edgeguide_base_function_is_used_at_link_sites(self):
        src = _read_js("dashboard.js")
        body = _extract_function_body(src, "_edgeGuideBase")

        assert "return '/planner/'" in body
        assert "plannerBaseUrl" in body and "planner_url" in body
        assert "_edgeGuideUrl" in src
        assert src.count("_appendEdgeGuideLink(") >= 2

    def test_dashboard_js_edgeguide_uses_launcher_not_new_tab(self):
        src = _read_js("dashboard.js")
        assert "window.open" not in src, (
            "dashboard.js must not open EdgeGuide in a new browser tab"
        )
        assert "target = '_blank'" not in src and 'target="_blank"' not in src, (
            "dashboard.js must not use target=_blank for EdgeGuide links"
        )
        nav_body = _extract_function_body(src, "_navigateToEdgeGuide")
        assert "_launcherLaunch()" in nav_body
        assert "launchFn('planner', query)" in nav_body
        launch_body = _extract_function_body(src, "_launcherLaunch")
        assert "typeof w.launch === 'function'" in launch_body

    def test_dashboard_js_direct_port_heuristic_skips_well_known_ports(self):
        src = _read_js("dashboard.js")
        body = _extract_function_body(src, "_edgeGuideBase")

        assert "currentPort > 1024" in body


class TestSettingsDeploymentFixed:
    """settings.js must not show misleading 'Saved' alert for deployment-fixed config."""

    def test_settings_js_no_save_button(self):
        """Settings panel must not contain a save button for path config."""
        src = _read_js("settings.js")
        assert "Settings.save()" not in src, (
            "settings.js must not have a save button calling Settings.save()"
        )

    def test_settings_js_shows_deployment_fixed_notice(self):
        """Settings panel must contain deployment-fixed or configured-at-deployment copy."""
        src = _read_js("settings.js")
        src_lower = src.lower()
        assert ("deployment" in src_lower or "read-only" in src_lower
                or "read only" in src_lower), (
            "settings.js must explain that settings are deployment-fixed or read-only"
        )

    def test_settings_js_no_misleading_save_alert(self):
        """settings.js must not alert a success message after POST."""
        src = _read_js("settings.js")
        assert "alert(" not in src or "Save" not in src.split("alert(")[1].split(")")[0] if "alert(" in src else True, (
            "settings.js must not show misleading 'Saved ✅' alert"
        )

    def test_settings_js_populates_runtime_values_from_server(self):
        """settings.js load() must populate thermal/benchmark fields from /api/config."""
        src = _read_js("settings.js")
        for field_id in ["settCooldownTemp", "settWaitInterval",
                         "settIterations", "settWarmup", "settFpsThreshold"]:
            assert field_id in src, f"settings.js must reference {field_id}"
        # load() must assign these from server data, not just hardcode in HTML
        load_block = src.split("load:")[1] if "load:" in src else ""
        for key in ["cooldown_temp", "wait_interval", "iterations",
                     "warmup", "fps_threshold"]:
            assert key in load_block, (
                f"settings.js load() must read '{key}' from server response"
            )
