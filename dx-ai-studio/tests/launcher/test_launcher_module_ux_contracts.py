"""Source-contract tests for launcher module entry deep UX.

Asserts health-gated launch, timeout, retry, active card states,
and invalid route recovery behavior in launcher-app-frame.js / style.css.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
STATIC = ROOT / "launcher" / "static"


def _read(name):
    return (STATIC / name).read_text(encoding="utf-8")


def _function_body(source, name):
    match = re.search(
        rf"function\s+{name}\b(.*?)(\n\s*function\b|\n\s*return\s*\{{)",
        source,
        re.DOTALL,
    )
    assert match, f"{name} function body not found"
    return match.group(1)




def test_module_launch_uses_health_gate_before_iframe_load():
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    assert "resolveModuleHealth" in show_app or "checkHealth" in show_app
    assert show_app.find("resolveModuleHealth") < show_app.find("loadAppIframeIfNeeded")


def test_module_load_timeout_is_sane_for_remote_access():
    """Load timeout must exist and sit in a sane range. Raised from 8000→20000 so remote
    (higher-latency) access doesn't spuriously trip "Load timeout"; Retry still covers transients."""
    import re
    src = _read("launcher-app-frame.js")
    assert "MODULE_LOAD_TIMEOUT_MS" in src
    assert "load-timeout" in src or "timeout" in src
    m = re.search(r"MODULE_LOAD_TIMEOUT_MS\s*=\s*(\d+)", src)
    assert m, "MODULE_LOAD_TIMEOUT_MS assignment not found"
    value = int(m.group(1))
    assert 8000 <= value <= 30000, f"timeout {value}ms out of sane range"


def test_module_unavailable_state_has_retry_without_duplicate_history():
    src = _read("launcher-app-frame.js")
    assert "renderModuleUnavailable" in src
    assert "retryModuleLaunch" in src
    retry_body = _function_body(src, "retryModuleLaunch")
    assert "_commitHistory" not in retry_body




def test_module_entry_css_states():
    css = _read("style.css")
    for selector in [
        ".module-entry-state",
        ".module-entry-loading",
        ".module-entry-error",
        ".module-retry-btn",
    ]:
        assert selector in css, f"Missing CSS selector: {selector}"


def test_module_loading_spinner_css():
    """CSS has a spinner rule scoped inside .module-entry-loading."""
    css = _read("style.css")
    assert ".module-entry-loading .spinner" in css




def test_active_module_card_toggle():
    """updateNavTabs or updateActiveModuleCards toggles active state on orbital cards."""
    src = _read("launcher-app-frame.js")
    assert "updateActiveModuleCards" in src
    body = _function_body(src, "updateActiveModuleCards")
    assert "orbital-card" in body or "active-module-card" in body
    assert "ns.currentApp" in body or "currentApp" in body


def test_invalid_route_recovery_notice():
    """restoreFromLocation calls a visible recovery notice for unknown paths."""
    src = _read("launcher-app-frame.js")
    assert "renderRouteRecoveryNotice" in src
    # Must be called in the fallback path of restoreFromLocation
    restore_body = _function_body(src, "restoreFromLocation")
    assert "renderRouteRecoveryNotice" in restore_body




def test_resolve_module_health_accepts_options_and_force_guard():
    """resolveModuleHealth accepts opts param and has !force cache guard."""
    src = _read("launcher-app-frame.js")
    body = _function_body(src, "resolveModuleHealth")
    assert "opts" in body or "options" in body
    assert "forceHealth" in body
    assert "!force" in body


def test_show_app_passes_opts_to_resolve_module_health():
    """_showApp passes health opts (with forceHealth on user nav) to resolveModuleHealth."""
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    assert re.search(r"resolveModuleHealth\(appKey,\s*healthOpts\)", show_app)
    assert "forceHealth = true" in show_app




def test_module_scoped_load_timer_variable_exists():
    """Module-scoped _moduleLoadTimer variable is declared."""
    src = _read("launcher-app-frame.js")
    assert "_moduleLoadTimer" in src
    assert re.search(r"var\s+_moduleLoadTimer\s*=\s*null", src)


def test_show_app_clears_module_load_timer_at_start():
    """_showApp clears any existing _moduleLoadTimer at the start."""
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    # Timer cleanup must appear before resolveModuleHealth call
    timer_clear_pos = show_app.find("_moduleLoadTimer")
    health_pos = show_app.find("resolveModuleHealth")
    assert timer_clear_pos < health_pos, "Timer cleanup must precede health resolution"
    assert "clearTimeout(_moduleLoadTimer)" in show_app


def test_show_app_stores_timeout_in_module_scoped_timer():
    """_showApp stores setTimeout result in _moduleLoadTimer."""
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    assert "_moduleLoadTimer = setTimeout" in show_app


def test_show_app_clears_stale_iframe_onload_at_start():
    """_showApp nullifies iframe.onload before starting new load."""
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    # iframe.onload = null must appear before resolveModuleHealth
    onload_null_pos = show_app.find("iframe.onload = null")
    health_pos = show_app.find("resolveModuleHealth")
    assert onload_null_pos != -1, "iframe.onload = null not found"
    assert onload_null_pos < health_pos




def test_retry_passes_skip_history_and_force_health():
    """retryModuleLaunch passes skipHistory: true and forceHealth: true."""
    src = _read("launcher-app-frame.js")
    retry_body = _function_body(src, "retryModuleLaunch")
    assert "skipHistory: true" in retry_body or "skipHistory:true" in retry_body
    assert "forceHealth: true" in retry_body or "forceHealth:true" in retry_body


def test_show_app_respects_skip_history_for_commit_history():
    """_showApp skips _commitHistory when opts.skipHistory is true."""
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    assert "skipHistory" in show_app
    assert "_commitHistory" in show_app




def test_health_then_has_stale_navigation_guard():
    """The .then() callback checks ns.currentApp !== appKey before rendering."""
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    # Guard must appear inside the .then callback, before renderModuleLoading
    then_pos = show_app.find(".then(function")
    assert then_pos != -1
    after_then = show_app[then_pos:]
    guard_pos = after_then.find("ns.currentApp !== appKey")
    loading_pos = after_then.find("renderModuleLoading")
    assert guard_pos != -1, "Stale-navigation guard not found in .then() body"
    assert guard_pos < loading_pos, "Guard must precede renderModuleLoading"


def test_health_then_clears_timer_before_new_timeout():
    """The .then() callback clears _moduleLoadTimer before setting a new setTimeout."""
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    then_pos = show_app.find(".then(function")
    after_then = show_app[then_pos:]
    # Find the clearTimeout inside the callback (after the guard, before setTimeout)
    clear_pos = after_then.find("clearTimeout(_moduleLoadTimer)")
    set_pos = after_then.find("_moduleLoadTimer = setTimeout")
    assert clear_pos != -1, "clearTimeout not found inside .then() body"
    assert clear_pos < set_pos, "Timer clear must precede new setTimeout"




def test_health_promise_chain_has_catch():
    """resolveModuleHealth(...).then(...) must be followed by .catch(...)."""
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    then_pos = show_app.find("resolveModuleHealth")
    assert then_pos != -1
    after_health = show_app[then_pos:]
    assert ".catch(" in after_health, ".catch() missing from health promise chain"


def test_health_catch_surfaces_error_and_renders_state():
    """The .catch() handler logs, disarms pending load work, and renders error state."""
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    catch_pos = show_app.find(".catch(function")
    assert catch_pos != -1, ".catch(function handler not found"
    catch_body = show_app[catch_pos:]
    assert "console.error" in catch_body, "catch must surface error via console.error"
    assert "clearTimeout(_moduleLoadTimer)" in catch_body, (
        "catch must disarm a pending module load timer"
    )
    assert "_moduleLoadTimer = null" in catch_body, (
        "catch must clear the module load timer handle"
    )
    assert "iframe.onload = null" in catch_body, (
        "catch must disarm a pending iframe.onload handler"
    )
    assert (
        "renderModuleUnavailable" in catch_body or "error" in catch_body
    ), "catch must render an error/unavailable state"
    assert "retryModuleLaunch" in catch_body, "catch must offer retry path"


def test_timeout_callback_has_stale_navigation_guard():
    """setTimeout callback checks ns.currentApp !== appKey before rendering timeout."""
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    # Find the setTimeout inside the .then() callback
    then_pos = show_app.find(".then(function")
    after_then = show_app[then_pos:]
    set_timeout_pos = after_then.find("_moduleLoadTimer = setTimeout(function")
    assert set_timeout_pos != -1
    timeout_body = after_then[set_timeout_pos:]
    # Guard must appear before the failure handler in the timeout body. The timeout
    # delegates to handleModuleEntryFailure (bounded auto-retry that falls back to
    # renderModuleUnavailable once the self-heal window is exhausted).
    guard_pos = timeout_body.find("ns.currentApp !== appKey")
    fail_pos = timeout_body.find("handleModuleEntryFailure")
    assert guard_pos != -1, "Stale-navigation guard not found in timeout callback"
    assert fail_pos != -1, "timeout callback must delegate to handleModuleEntryFailure"
    assert guard_pos < fail_pos, "Guard must precede failure handling in timeout"


def test_iframe_onload_has_stale_navigation_guard():
    """Module iframe onload delegates to finishModuleEntry with stale-navigation guard."""
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    onload_pos = show_app.find("iframe.onload = function()")
    assert onload_pos != -1, "iframe.onload handler not found in _showApp"
    onload_body = show_app[onload_pos:onload_pos + 200]
    assert "finishModuleEntry" in onload_body, "iframe.onload must call finishModuleEntry"

    finish_body = _function_body(src, "finishModuleEntry")
    guard_pos = finish_body.find("ns.currentApp !== appKey")
    clear_pos = finish_body.find("clearModuleEntryState")
    assert guard_pos != -1, "Stale-navigation guard not found in finishModuleEntry"
    assert guard_pos < clear_pos, "Guard must precede clearModuleEntryState in finishModuleEntry"
    load_state_pos = finish_body.find("loadState = 'loaded'")
    assert load_state_pos != -1, "finishModuleEntry must mark iframe loadState before guard"
    assert load_state_pos < guard_pos, "loadState update must precede stale-navigation guard"


def test_show_app_clears_stale_module_entry_state_immediately():
    """Switching modules must drop the previous module's entry overlay before health/load."""
    show_app = _function_body(_read("launcher-app-frame.js"), "_showApp")
    assign_pos = show_app.find("ns.currentApp = appKey")
    clear_pos = show_app.find("clearModuleEntryState()")
    assert assign_pos != -1 and clear_pos != -1, "_showApp must clear module entry state"
    assert clear_pos < assign_pos + 120, (
        "clearModuleEntryState must run near the start of _showApp"
    )


def test_show_app_disarms_background_iframe_onloads():
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    assert "disarmModuleIframeLoads" in show_app, (
        "_showApp must disarm stale onload handlers on background iframes"
    )


def test_show_app_refreshes_health_on_user_navigation():
    show_app = _function_body(_read("launcher-app-frame.js"), "_showApp")
    assert "forceHealth = true" in show_app, (
        "_showApp must force fresh health checks on user-initiated navigation"
    )




def test_route_recovery_notice_css_exists():
    """CSS defines a .route-recovery-notice rule."""
    css = _read("style.css")
    assert ".route-recovery-notice" in css




def test_render_module_loading_uses_textcontent_not_innerhtml():
    """renderModuleLoading must use textContent for title/message, not innerHTML with moduleDisplayName."""
    src = _read("launcher-app-frame.js")
    body = _function_body(src, "renderModuleLoading")
    # Must not concatenate moduleDisplayName into innerHTML
    assert "innerHTML" not in body, (
        "renderModuleLoading should not use innerHTML for dynamic content"
    )
    assert "textContent" in body, (
        "renderModuleLoading should set title/message via textContent"
    )
    assert "moduleDisplayName" in body, (
        "renderModuleLoading should still use moduleDisplayName for the title"
    )


def test_render_module_unavailable_uses_textcontent_not_innerhtml():
    """renderModuleUnavailable must use textContent for title/message, not innerHTML with moduleDisplayName."""
    src = _read("launcher-app-frame.js")
    body = _function_body(src, "renderModuleUnavailable")
    # Must not concatenate moduleDisplayName into innerHTML
    assert "innerHTML" not in body, (
        "renderModuleUnavailable should not use innerHTML for dynamic content"
    )
    assert "textContent" in body, (
        "renderModuleUnavailable should set title/message via textContent"
    )
    assert "moduleDisplayName" in body, (
        "renderModuleUnavailable should still use moduleDisplayName for the title"
    )


def test_show_app_does_not_call_update_active_module_cards_directly():
    """_showApp must not call updateActiveModuleCards() directly; it is synced via updateNavTabs."""
    src = _read("launcher-app-frame.js")
    show_app = _function_body(src, "_showApp")
    # updateNavTabs should be present
    assert "updateNavTabs()" in show_app, "_showApp must call updateNavTabs()"
    # updateActiveModuleCards should NOT appear as a direct call in _showApp
    # (it is called internally by updateNavTabs)
    lines = show_app.split("\n")
    direct_calls = [
        line for line in lines
        if "updateActiveModuleCards()" in line and "updateNavTabs" not in line
    ]
    assert not direct_calls, (
        "_showApp should not call updateActiveModuleCards() directly; "
        "active card sync is owned by updateNavTabs"
    )




class TestNavTabKeyboardAccessibility:
    """Nav tabs must have tabindex, role=button, and Enter/Space key activation."""

    @pytest.fixture(scope="class")
    def build_nav_body(self):
        src = _read("launcher-app-frame.js")
        match = re.search(
            r"function\s+_buildNavTabs\b(.*?)(\n\s*function\b|\n\s*\}$)",
            src, re.DOTALL,
        )
        assert match, "_buildNavTabs function body not found"
        return match.group(1)

    def test_nav_tabs_have_tabindex(self, build_nav_body):
        assert "tabindex" in build_nav_body or "tabIndex" in build_nav_body, (
            "Nav tabs must set tabindex for keyboard focusability"
        )

    def test_nav_tabs_have_role_button(self, build_nav_body):
        assert "role" in build_nav_body, (
            "Nav tabs must set role='button' for screen readers"
        )

    def test_nav_tabs_have_keydown_activation(self, build_nav_body):
        assert "keydown" in build_nav_body, (
            "Nav tabs must have keydown listener for Enter/Space activation"
        )




class TestHealthDotsCompleteness:
    """Health dots in index.html must include Benchmark and Monitor."""

    def test_dot_benchmark_exists_in_html(self):
        html = (STATIC / "index.html").read_text(encoding="utf-8")
        assert 'id="dotBenchmark"' in html, (
            "index.html missing dotBenchmark health dot"
        )

    def test_dot_monitor_exists_in_html(self):
        html = (STATIC / "index.html").read_text(encoding="utf-8")
        assert 'id="dotMonitor"' in html, (
            "index.html missing dotMonitor health dot"
        )

    def test_health_check_updates_dot_benchmark(self):
        src = _read("launcher-app-frame.js")
        assert "setDot('dotBenchmark'" in src or 'setDot("dotBenchmark"' in src, (
            "checkHealth must call setDot for dotBenchmark"
        )

    def test_health_check_updates_dot_monitor(self):
        src = _read("launcher-app-frame.js")
        assert "setDot('dotMonitor'" in src or 'setDot("dotMonitor"' in src, (
            "checkHealth must call setDot for dotMonitor"
        )




class TestCheckHealthCatchOrbitalStatus:
    """checkHealth .catch() must call _setOrbStatus(false) for all seven modules."""

    ORB_IDS = [
        "orbStatusApp",
        "orbStatusStream",
        "orbStatusZoo",
        "orbStatusCompiler",
        "orbStatusPlanner",
        "orbStatusBenchmark",
        "orbStatusMonitor",
    ]

    def _catch_body(self):
        src = _read("launcher-app-frame.js")
        # Extract the catch block of checkHealth
        fn_match = re.search(
            r"function\s+checkHealth\b(.*?)(\n\s*function\b|\n\s*//\s*──)",
            src, re.DOTALL,
        )
        assert fn_match, "checkHealth function not found"
        body = fn_match.group(1)
        catch_pos = body.find(".catch(function")
        assert catch_pos != -1, ".catch(function not found in checkHealth"
        return body[catch_pos:]

    @pytest.mark.parametrize("orb_id", ORB_IDS)
    def test_catch_sets_orb_status_false(self, orb_id):
        catch_body = self._catch_body()
        assert (
            f"_setOrbStatus('{orb_id}', false)" in catch_body
            or f'_setOrbStatus("{orb_id}", false)' in catch_body
        ), f"checkHealth catch must call _setOrbStatus('{orb_id}', false)"

    def test_catch_has_status_monitor_false(self):
        """catch block must also call setStatus('statusMonitor', false)."""
        catch_body = self._catch_body()
        assert (
            "setStatus('statusMonitor', false)" in catch_body
            or 'setStatus("statusMonitor", false)' in catch_body
        ), "checkHealth catch must call setStatus('statusMonitor', false)"




class TestLiveModulePortLabels:
    """Home orbital cards show runtime ports from /api/health, not hardcoded defaults."""

    def test_update_module_port_labels_function_exists(self):
        src = _read("launcher-app-frame.js")
        assert "function updateModulePortLabels" in src

    def test_update_hub_launcher_port_function_exists(self):
        src = _read("launcher-app-frame.js")
        assert "function updateHubLauncherPort" in src

    def test_check_health_calls_port_label_updaters(self):
        src = _read("launcher-app-frame.js")
        body = _function_body(src, "checkHealth")
        assert "updateModulePortLabels(data)" in body
        assert "updateHubLauncherPort(data)" in body

    def test_check_health_catch_resets_port_labels(self):
        catch_body = TestCheckHealthCatchOrbitalStatus()._catch_body()
        assert "updateModulePortLabels({})" in catch_body
        assert "updateHubLauncherPort({})" in catch_body

    def test_orbital_cards_use_placeholder_ports_not_legacy_defaults(self):
        html = _read("index.html")
        for legacy in (":8080", ":8093", ":8094", ":8095", ":8096", ":8097", ":8098", ":8099"):
            assert legacy not in html, f"index.html still hardcodes legacy port {legacy}"
        assert 'id="hubLauncherPort"' in html

    def test_port_updater_scopes_to_orbital_cards_with_data_app(self):
        src = _read("launcher-app-frame.js")
        body = _function_body(src, "updateModulePortLabels")
        assert ".orbital-card[data-app]" in body
        assert "MODULE_PORT_HEALTH_KEYS" in body
        assert "dx_monitor: 'monitor'" in src or 'dx_monitor: "monitor"' in src
