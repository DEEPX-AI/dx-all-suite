"""Source-contract tests for launcher JS router files.

These tests read the JavaScript source files and assert structural contracts
that must hold for correct browser history / deep-link behaviour.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
STATIC = ROOT / "launcher" / "static"


def _read(name):
    return (STATIC / name).read_text(encoding="utf-8")



def test_popstate_calls_restore_from_location():
    src = _read("launcher.js")
    assert "popstate" in src
    assert "queueRouteRestore" in src
    # popstate handler must reference window.location
    pop_match = re.search(r"popstate.*?queueRouteRestore\((.*?)\)", src, re.DOTALL)
    assert pop_match, "popstate handler must call queueRouteRestore"
    arg = pop_match.group(1).strip()
    assert "location" in arg, f"queueRouteRestore arg should reference location, got: {arg}"



def test_restore_handles_about_and_sdk():
    src = _read("launcher-app-frame.js")
    assert "restoreFromLocation" in src
    assert "'/about'" in src or '"/about"' in src
    assert "'/sdk-library'" in src or '"/sdk-library"' in src


def test_restore_handles_all_app_paths():
    state_src = _read("launcher-state.js")
    frame_src = _read("launcher-app-frame.js")
    # Extract APP_PATHS keys from state
    app_keys = re.findall(r"(\w+)\s*:\s*'/\w+/'", state_src)
    assert len(app_keys) >= 7, f"Expected >=7 APP_PATHS entries, got {app_keys}"
    # restoreFromLocation must use appFromPath which iterates APP_PATHS
    assert "appFromPath" in frame_src


def test_restore_unknown_path_shows_home():
    src = _read("launcher-app-frame.js")
    # restoreFromLocation should call _showHome for unknown paths
    fn_match = re.search(
        r"function\s+restoreFromLocation\b.*?(\}\s*\n\s*\n|\}\s*$|\}\s*return)",
        src,
        re.DOTALL,
    )
    assert fn_match, "restoreFromLocation function must exist"
    fn_body = fn_match.group(0)
    assert "_showHome" in fn_body, "Unknown paths must fall through to _showHome"



def test_show_app_carries_suffix_and_query():
    src = _read("launcher-app-frame.js")
    fn_match = re.search(r"function\s+_showApp\b(.*?)(\n\s*function\b|\n\s*return\s*\{)", src, re.DOTALL)
    assert fn_match, "_showApp function must exist"
    fn_body = fn_match.group(1)
    assert "suffix" in fn_body, "_showApp must handle suffix"
    assert "query" in fn_body or "rawQuery" in fn_body, "_showApp must handle query"


def test_hidden_app_iframe_preserves_module_state_without_blank_reset():
    """Leaving app view must not navigate module iframes to about:blank."""
    src = _read("launcher-app-frame.js")
    assert "appIframePool" in src
    assert "loadAppIframeIfNeeded" in src
    assert "resetHiddenIframe" not in src
    assert "about:blank" not in src


def test_setVisibleView_preserves_sdk_and_about_state():
    """Switching views must hide SDK/About without destructive close* teardown."""
    src = _read("launcher-app-frame.js")
    fn_match = re.search(
        r"function\s+setVisibleView\b(.*?)(\n\s*function\b|\n\s*//\s*──)",
        src, re.DOTALL,
    )
    assert fn_match, "setVisibleView must exist"
    body = fn_match.group(0)
    assert "hideSdkLibraryView" in body, (
        "setVisibleView must hide SDK via hideSdkLibraryView"
    )
    assert "closeSdkLibrary" not in body, (
        "setVisibleView must not call closeSdkLibrary (destroys viewer on leave)"
    )
    assert "closeAboutPanel" not in body, (
        "setVisibleView must not call closeAboutPanel (resets About scroll on leave)"
    )
    assert "suspendAllTutorialChrome" in body, (
        "setVisibleView must suspend tutorial overlays before switching views"
    )
    assert "stopEmbeddedModuleTutorial" in body, (
        "setVisibleView must stop embedded module tutorials when leaving app view"
    )
    assert "LauncherTutorial.connectToolbar" in body, (
        "setVisibleView must restore launcher tutorial toolbar on home/about"
    )


    src = _read("launcher-app-frame.js")
    fn_match = re.search(r"function\s+_showApp\b(.*?)(\n\s*function\b|\n\s*return\s*\{)", src, re.DOTALL)
    assert fn_match, "_showApp function must exist"
    fn_body = fn_match.group(1)
    assert "loadAppIframeIfNeeded" in fn_body
    assert "forceReload" in fn_body



def test_nav_tab_config_contains_expected_entries():
    src = _read("launcher-app-frame.js")
    config_match = re.search(r"NAV_TAB_CONFIG\s*=\s*\[(.*?)\];", src, re.DOTALL)
    assert config_match, "NAV_TAB_CONFIG must exist"
    config_body = config_match.group(1)
    expected_apps = ["app", "stream", "zoo", "compiler", "planner", "benchmark", "dx_monitor", "sdk-library", "about"]
    for app_name in expected_apps:
        assert f"'{app_name}'" in config_body or f'"{app_name}"' in config_body, \
            f"NAV_TAB_CONFIG must include {app_name}"



def test_active_classes_include_required_variants():
    src = _read("launcher-app-frame.js")
    classes_match = re.search(r"NAV_ACTIVE_CLASSES\s*=\s*\[(.*?)\]", src)
    assert classes_match, "NAV_ACTIVE_CLASSES must exist"
    classes_body = classes_match.group(1)
    for cls in ["active", "active-stream", "active-zoo"]:
        assert f"'{cls}'" in classes_body or f'"{cls}"' in classes_body, \
            f"NAV_ACTIVE_CLASSES must include {cls}"



@pytest.mark.parametrize("alias", [
    "window.launch",
    "window.goHome",
    "window.showAboutView",
    "window.showSdkLibrary",
    "window.LauncherRouter",
])
def test_public_aliases_are_registered(alias):
    src = _read("launcher.js")
    assert alias in src, f"{alias} must be registered in launcher.js"



class TestUpdateSdkLibraryQueryContract:
    """LauncherRouter must expose updateSdkLibraryQuery for SDK URL management."""

    @pytest.fixture(scope="class")
    def frame_src(self):
        return _read("launcher-app-frame.js")

    def test_function_exists(self, frame_src):
        assert "updateSdkLibraryQuery" in frame_src

    def test_exported_on_LauncherRouter(self, frame_src):
        # Must appear in the return object of the LauncherRouter IIFE
        assert re.search(r"updateSdkLibraryQuery\s*:\s*updateSdkLibraryQuery", frame_src)

    def test_accepts_query_and_options(self, frame_src):
        # Function signature must accept at least two parameters
        match = re.search(r"function\s+updateSdkLibraryQuery\s*\(([^)]*)\)", frame_src)
        assert match, "updateSdkLibraryQuery must be a named function"
        params = [p.strip() for p in match.group(1).split(",") if p.strip()]
        assert len(params) >= 2, f"Expected >=2 params, got {params}"

    def test_handles_push_and_replace_history(self, frame_src):
        # Must reference both 'push' and 'replace' semantics
        fn_match = re.search(
            r"function\s+updateSdkLibraryQuery\b(.*?)(\n\s*function\b|\n\s*return\s*\{)",
            frame_src, re.DOTALL
        )
        assert fn_match, "updateSdkLibraryQuery function body not found"
        body = fn_match.group(1)
        assert "'push'" in body or '"push"' in body, "must handle push"
        assert "'replace'" in body or '"replace"' in body, "must handle replace"

    def test_builds_sdk_library_url(self, frame_src):
        fn_match = re.search(
            r"function\s+updateSdkLibraryQuery\b(.*?)(\n\s*function\b|\n\s*return\s*\{)",
            frame_src, re.DOTALL
        )
        assert fn_match
        body = fn_match.group(1)
        assert "/sdk-library" in body



class TestShowSdkApplyQueryContract:
    """_showSdk must call SDKLibrary.init() before SDKLibrary.applyQuery()."""

    @pytest.fixture(scope="class")
    def frame_src(self):
        return _read("launcher-app-frame.js")

    def test_show_sdk_calls_init_before_applyQuery(self, frame_src):
        fn_match = re.search(
            r"function\s+_showSdk\b(.*?)(\n\s*function\b|\n\s*return\s*\{)",
            frame_src, re.DOTALL
        )
        assert fn_match, "_showSdk function body not found"
        body = fn_match.group(1)
        init_pos = body.find("SDKLibrary.init()")
        apply_pos = body.find("SDKLibrary.applyQuery")
        assert init_pos >= 0, "_showSdk must call SDKLibrary.init()"
        assert apply_pos >= 0, "_showSdk must call SDKLibrary.applyQuery"
        assert init_pos < apply_pos, "init() must come before applyQuery()"

    def test_show_sdk_preserves_query_string(self, frame_src):
        fn_match = re.search(
            r"function\s+_showSdk\b(.*?)(\n\s*function\b|\n\s*return\s*\{)",
            frame_src, re.DOTALL
        )
        assert fn_match
        body = fn_match.group(1)
        assert "query" in body, "_showSdk must handle query"

    def test_show_sdk_passes_restore_source(self, frame_src):
        fn_match = re.search(
            r"function\s+_showSdk\b(.*?)(\n\s*function\b|\n\s*return\s*\{)",
            frame_src, re.DOTALL
        )
        assert fn_match
        body = fn_match.group(1)
        assert re.search(r"source\s*:\s*['\"]restore['\"]", body) or \
               re.search(r"opts\s*&&\s*opts\.source\s*\|\|\s*['\"]restore['\"]", body) or \
               re.search(r"source.*restore", body), \
            "_showSdk must pass source:'restore' default"



class TestPopstateSourceContract:
    """popstate handler must pass source:'popstate' for sdk-library restoration."""

    @pytest.fixture(scope="class")
    def launcher_src(self):
        return _read("launcher.js")

    @pytest.fixture(scope="class")
    def frame_src(self):
        return _read("launcher-app-frame.js")

    def test_popstate_passes_source_popstate(self, launcher_src):
        # popstate handler must pass opts with source: 'popstate'
        assert re.search(r"source\s*:\s*['\"]popstate['\"]", launcher_src), \
            "popstate handler must pass { source: 'popstate' }"

    def test_restoreFromLocation_accepts_opts(self, frame_src):
        # restoreFromLocation must accept a second parameter (opts)
        match = re.search(r"function\s+restoreFromLocation\s*\(([^)]*)\)", frame_src)
        assert match, "restoreFromLocation must exist"
        params = [p.strip() for p in match.group(1).split(",") if p.strip()]
        assert len(params) >= 2, f"restoreFromLocation must accept opts param, got {params}"

    def test_show_sdk_receives_popstate_source(self, frame_src):
        # restoreFromLocation must pass source through to _showSdk
        fn_match = re.search(
            r"function\s+restoreFromLocation\b(.*?)(\n\s*function\b|\n\s*return\s*\{)",
            frame_src, re.DOTALL
        )
        assert fn_match
        body = fn_match.group(1)
        assert "source" in body, "restoreFromLocation must propagate source"



class TestShowSdkRouteContract:
    """_showSdk must commit /sdk-library paths with query, never APP_PATHS/iframe URLs."""

    @pytest.fixture(scope="class")
    def frame_src(self):
        return _read("launcher-app-frame.js")

    @pytest.fixture(scope="class")
    def state_src(self):
        return _read("launcher-state.js")

    def test_show_sdk_commits_sdk_library_path(self, frame_src):
        """_showSdk must build URL as '/sdk-library' + optional query."""
        fn_match = re.search(
            r"function\s+_showSdk\b(.*?)(\n\s*function\b|\n\s*return\s*\{)",
            frame_src, re.DOTALL
        )
        assert fn_match, "_showSdk function body not found"
        body = fn_match.group(1)
        assert "'/sdk-library'" in body or '"/sdk-library"' in body, \
            "_showSdk must use /sdk-library as base URL"
        assert "_commitHistory" in body, "_showSdk must call _commitHistory"

    def test_show_sdk_appends_query_to_url(self, frame_src):
        """_showSdk must append opts.query to the committed URL."""
        fn_match = re.search(
            r"function\s+_showSdk\b(.*?)(\n\s*function\b|\n\s*return\s*\{)",
            frame_src, re.DOTALL
        )
        assert fn_match
        body = fn_match.group(1)
        # Must have logic to append query string to url
        assert "opts" in body and "query" in body, \
            "_showSdk must use opts.query for URL building"
        assert "'?'" in body or '"?"' in body, \
            "_showSdk must join query with '?'"

    def test_show_sdk_does_not_use_app_paths(self, frame_src, state_src):
        """_showSdk must never reference APP_PATHS or use /stream/, /app/ style iframe URLs."""
        fn_match = re.search(
            r"function\s+_showSdk\b(.*?)(\n\s*function\b|\n\s*return\s*\{)",
            frame_src, re.DOTALL
        )
        assert fn_match
        body = fn_match.group(1)
        assert "APP_PATHS" not in body, "_showSdk must not reference APP_PATHS"
        # Must not commit any iframe/app path
        assert "iframe" not in body.lower(), "_showSdk must not reference iframe"

    def test_nav_config_contains_all_expected_entries(self, frame_src):
        """NAV_TAB_CONFIG must include sdk-library, about, and all 7 app routes."""
        config_match = re.search(r"NAV_TAB_CONFIG\s*=\s*\[(.*?)\];", frame_src, re.DOTALL)
        assert config_match, "NAV_TAB_CONFIG must exist"
        config_body = config_match.group(1)
        expected = [
            "sdk-library", "about",
            "app", "stream", "zoo",
            "compiler", "planner", "benchmark", "dx_monitor",
        ]
        for name in expected:
            assert f"'{name}'" in config_body or f'"{name}"' in config_body, \
                f"NAV_TAB_CONFIG must include '{name}'"

    def _show_sdk_body(self, frame_src):
        """Extract _showSdk function body for scoped assertions."""
        fn_match = re.search(
            r"function\s+_showSdk\b(.*?)(\n\s*function\b|\n\s*return\s*\{)",
            frame_src, re.DOTALL
        )
        assert fn_match, "_showSdk function body not found"
        return fn_match.group(1)

    def test_active_nav_uses_current_app(self, frame_src):
        """Active nav must be driven by ns.currentApp / updateNavTabs inside _showSdk."""
        body = self._show_sdk_body(frame_src)
        assert "ns.currentApp" in body, "_showSdk must set ns.currentApp"
        assert "updateNavTabs" in body, "_showSdk must call updateNavTabs"



class TestSerializeSdkQueryURLSearchParams:
    """_serializeSdkQuery must accept both plain objects and URLSearchParams."""

    @pytest.fixture(scope="class")
    def frame_src(self):
        return _read("launcher-app-frame.js")

    def test_serialize_checks_get_method(self, frame_src):
        fn_match = re.search(
            r"function\s+_serializeSdkQuery\b(.*?)(\n\s*function\b|\n\s*return\s*\{)",
            frame_src, re.DOTALL
        )
        assert fn_match, "_serializeSdkQuery function body not found"
        body = fn_match.group(1)
        assert ".get(" in body, \
            "_serializeSdkQuery must call .get() to support URLSearchParams"
        assert "typeof" in body or "get" in body, \
            "_serializeSdkQuery must detect URLSearchParams-like input"



def test_show_sdk_does_not_commit_history_on_popstate():
    """_showSdk must guard _commitHistory so it is skipped when source is popstate."""
    src = _read("launcher-app-frame.js")
    fn_match = re.search(
        r"function\s+_showSdk\b(.*?)(\n\s*function\b|\n\s*function\s+updateSdkLibraryQuery\b)",
        src,
        re.DOTALL,
    )
    assert fn_match, "_showSdk function body not found"
    body = fn_match.group(1)
    # Must have a source variable derived from opts
    assert "source" in body, "_showSdk must compute source from opts"
    # _commitHistory must be inside a guard that excludes popstate
    history_guard = re.search(
        r"if\s*\(\s*source\s*!==\s*['\"]popstate['\"]\s*\)\s*\{(?P<body>[^}]*)\}",
        body,
        re.DOTALL,
    )
    assert history_guard, "_showSdk must guard _commitHistory with source !== 'popstate'"
    assert "_commitHistory" in history_guard.group("body"), \
        "_commitHistory must be inside the source !== 'popstate' guard"
