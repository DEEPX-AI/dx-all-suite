"""Entry UX / i18n source and data contracts.

Validates structural invariants for launcher static assets:
- Language map completeness in JSON data files
- JavaScript module API surface (window.SDKLibrary, window.AboutDeepX)
- History API delegation (sdk-library.js must not call pushState/replaceState)
- DXI18n.onLangChange registration
- index.html iframe postMessage scoping
- Hardcoded chrome string elimination (i18n wrappers required)
- SDK empty/not-found/error visible state contracts
"""
import json
import re
from pathlib import Path

import pytest

STATIC = Path(__file__).resolve().parents[2] / "launcher" / "static"

REQUIRED_LANGS = {"en", "ko", "ja", "zh-CN", "zh-TW", "es"}



def assert_lang_map(value, path: str):
    """Assert value is a dict with all REQUIRED_LANGS as keys with non-empty values."""
    assert isinstance(value, dict), f"{path}: expected dict, got {type(value).__name__}"
    missing = REQUIRED_LANGS - set(value.keys())
    assert not missing, f"{path}: missing languages {missing}"
    for lang in REQUIRED_LANGS:
        assert value[lang], f"{path}[{lang}] is empty"


def _check_recursive_lang_maps(obj, path: str, errors: list):
    """Recursively find dicts that look like language maps and verify completeness."""
    if isinstance(obj, dict):
        keys = set(obj.keys())
        if keys & REQUIRED_LANGS and not (keys - REQUIRED_LANGS - {"default"}):
            missing = REQUIRED_LANGS - keys
            if missing:
                errors.append(f"{path}: missing {missing}")
            for lang in REQUIRED_LANGS & keys:
                if not obj[lang]:
                    errors.append(f"{path}[{lang}] is empty")
        else:
            for k, v in obj.items():
                _check_recursive_lang_maps(v, f"{path}.{k}", errors)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _check_recursive_lang_maps(item, f"{path}[{i}]", errors)


def _load_json(filename: str):
    return json.loads((STATIC / filename).read_text(encoding="utf-8"))


def _read_js(filename: str) -> str:
    return (STATIC / filename).read_text(encoding="utf-8")



class TestSdkLibraryDataLangMaps:
    """Drawer and section labels must be complete 5-language maps."""

    @pytest.fixture(scope="class")
    def data(self):
        return _load_json("sdk-library-data.json")

    def test_drawer_labels_complete(self, data):
        for i, drawer in enumerate(data["drawers"]):
            assert_lang_map(drawer["label"], f"drawers[{i}].label")

    def test_section_labels_complete(self, data):
        for i, drawer in enumerate(data["drawers"]):
            for j, section in enumerate(drawer.get("sections", [])):
                assert_lang_map(
                    section["label"],
                    f"drawers[{i}].sections[{j}].label",
                )

    def test_recursive_lang_maps_complete(self, data):
        """All language-map objects in sdk-library-data must have all 6 languages."""
        errors: list = []
        _check_recursive_lang_maps(data, "sdk-library-data", errors)
        assert not errors, "\n".join(errors)

    def test_drawers_have_required_fields(self, data):
        """Each drawer must have id, label, icon, color, sections."""
        for i, drawer in enumerate(data["drawers"]):
            for key in ("id", "label", "icon", "color", "sections"):
                assert key in drawer, f"drawers[{i}] missing field '{key}'"

    def test_sections_have_required_fields(self, data):
        """Each section must have id, label, icon, files."""
        for i, drawer in enumerate(data["drawers"]):
            for j, section in enumerate(drawer.get("sections", [])):
                for key in ("id", "label", "icon", "files"):
                    assert key in section, \
                        f"drawers[{i}].sections[{j}] missing field '{key}'"

    def test_files_have_required_fields(self, data):
        """Each file must have path, title, size."""
        for i, drawer in enumerate(data["drawers"]):
            for j, section in enumerate(drawer.get("sections", [])):
                for k, f in enumerate(section.get("files", [])):
                    for key in ("path", "title", "size"):
                        assert key in f, \
                            f"drawers[{i}].sections[{j}].files[{k}] missing field '{key}'"



class TestAboutDataLangMaps:
    """Recursively check that any dict keyed by language codes is complete."""

    @pytest.fixture(scope="class")
    def data(self):
        return _load_json("about-data.json")

    def test_no_incomplete_lang_maps(self, data):
        errors: list = []
        _check_recursive_lang_maps(data, "about-data", errors)
        assert not errors, "\n".join(errors)

    def test_hero_section_lang_maps(self, data):
        """Hero slogan, subtitle, and stat labels must be complete."""
        assert_lang_map(data["hero"]["slogan"], "about-data.hero.slogan")
        assert_lang_map(data["hero"]["subtitle"], "about-data.hero.subtitle")
        for i, stat in enumerate(data["hero"]["stats"]):
            assert_lang_map(stat["label"], f"about-data.hero.stats[{i}].label")



class TestLauncherAppFrameContracts:
    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("launcher-app-frame.js")

    def test_exposes_restoreFromLocation(self, source):
        """launcher-app-frame.js exposes restoreFromLocation (current name for
        route restoration logic; will be extended with updateSdkLibraryQuery in Task 1)."""
        assert "restoreFromLocation" in source

    def test_exposes_updateSdkLibraryQuery(self, source):
        assert "updateSdkLibraryQuery" in source

    def test_sdk_library_restore_calls_applyQuery_with_restore_source(self, source):
        assert re.search(r"SDKLibrary\.applyQuery\(.+source\s*:\s*['\"]restore['\"]", source)

    def test_popstate_calls_applyQuery_with_popstate_source(self, source):
        assert re.search(r"SDKLibrary\.applyQuery\(.+source\s*:\s*['\"]popstate['\"]", source)

    def test_nav_tab_module_names_are_english_fixed(self, source):
        """Top-bar module tabs stay English regardless of UI language."""
        assert "NAV_TAB_LABELS" in source
        assert "label: NAV_TAB_LABELS" in source or "label: NAV_TAB_LABELS[" in source
        assert "getLabel" not in re.search(r"NAV_TAB_CONFIG\s*=\s*\[(.*?)\];", source, re.S).group(1)
        assert "🦁 モデルズー" not in source
        assert "📊 基准测试" not in source
        assert "📊 基準測試" not in source
        assert "STATUS_DOT_LABELS" in source
        assert "statusLabelZoo" in source

    def test_status_dot_labels_have_ids_in_index_html(self):
        html = (STATIC / "index.html").read_text(encoding="utf-8")
        for label_id in (
            "statusLabelApp",
            "statusLabelStream",
            "statusLabelZoo",
            "statusLabelCompiler",
            "statusLabelPlanner",
            "statusLabelBenchmark",
            "statusLabelMonitor",
            "statusLabelAgent",
        ):
            assert f'id="{label_id}"' in html, f"missing {label_id} in index.html"



class TestAboutDeepXContracts:
    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("about-deepx.js")

    def test_exposes_window_AboutDeepX(self, source):
        assert "window.AboutDeepX" in source

    def test_AboutDeepX_has_init(self, source):
        assert re.search(r"init\s*:", source)

    def test_AboutDeepX_has_refresh(self, source):
        assert re.search(r"refresh\s*:", source)

    def test_AboutDeepX_has_reset(self, source):
        assert re.search(r"reset\s*:", source)

    def test_registers_onLangChange(self, source):
        assert "DXI18n.onLangChange" in source

    def test_has_renderDeveloperHub(self, source):
        assert "function renderDeveloperHub" in source
        assert "aboutDeveloper" in source

    def test_has_renderNewsCard(self, source):
        assert "function renderNewsCard" in source
        assert "about-news-link" in source



class TestSdkLibraryJsContracts:
    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("sdk-library.js")

    def test_exposes_window_SDKLibrary(self, source):
        assert "window.SDKLibrary" in source

    def test_SDKLibrary_has_init(self, source):
        assert re.search(r"init\s*:", source)

    def test_SDKLibrary_has_refresh(self, source):
        assert re.search(r"refresh\s*:", source)

    def test_SDKLibrary_has_reset(self, source):
        assert re.search(r"reset\s*:", source)

    def test_SDKLibrary_has_applyQuery(self, source):
        assert re.search(r"applyQuery\s*:", source)

    def test_no_direct_pushState(self, source):
        assert "history.pushState" not in source

    def test_no_direct_replaceState(self, source):
        assert "history.replaceState" not in source

    def test_uses_decodeURIComponent(self, source):
        assert "decodeURIComponent" in source

    def test_has_findBookByPath(self, source):
        assert "findBookByPath" in source

    def test_calls_LauncherRouter_updateSdkLibraryQuery(self, source):
        assert "LauncherRouter.updateSdkLibraryQuery" in source

    def test_malformed_doc_triggers_not_found_ui(self, source):
        """parseSdkQuery must flag malformed doc values and applyQuery must render not-found."""
        assert "_malformedDoc" in source
        assert re.search(r"parsed\._malformedDoc", source), \
            "applyQuery must check parsed._malformedDoc to surface invalid doc paths"



class TestSdkLibraryHistoryPolicy:
    """SDK Library interactions must use correct push/replace semantics."""

    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("sdk-library.js")

    def test_open_viewer_requests_push(self, source):
        # openBookViewer must call requestSdkUrlUpdate with 'push'
        fn_match = re.search(
            r"(async\s+)?function\s+openBookViewer\b(.*?)(\n\s*function\b|\n\s*\}\s*$)",
            source, re.DOTALL
        )
        assert fn_match, "openBookViewer function must exist"
        body = fn_match.group(0)
        assert re.search(r"requestSdkUrlUpdate\(.+['\"]push['\"]", body), \
            "openBookViewer must call requestSdkUrlUpdate with 'push'"

    def test_close_viewer_requests_push(self, source):
        fn_match = re.search(
            r"function\s+closeBookViewer\b(.*?)(\n\s*function\b|\n\s*(async\s+)?function\b|\n\s*//\s*──)",
            source, re.DOTALL
        )
        assert fn_match, "closeBookViewer function must exist"
        body = fn_match.group(0)
        assert re.search(r"requestSdkUrlUpdate\(.+['\"]push['\"]", body), \
            "closeBookViewer must call requestSdkUrlUpdate with 'push'"

    def test_search_requests_replace(self, source):
        # setupSearch or search handler must use 'replace'
        assert re.search(r"requestSdkUrlUpdate\(\s*\{\s*q\s*:", source), \
            "search must call requestSdkUrlUpdate with q patch"
        # Find the requestSdkUrlUpdate call with q: and check it uses 'replace'
        matches = re.findall(r"requestSdkUrlUpdate\(\s*\{[^}]*q\s*:[^}]*\}\s*,\s*['\"](\w+)['\"]", source)
        assert 'replace' in matches, f"search requestSdkUrlUpdate must use 'replace', got {matches}"

    def test_view_switch_requests_replace(self, source):
        # switchView must use 'replace' (through requestSdkUrlUpdate)
        fn_match = re.search(
            r"function\s+switchView\b(.*?)(\n\s*function\b|\n\s*(async\s+)?function\b)",
            source, re.DOTALL
        )
        assert fn_match, "switchView function must exist"
        body = fn_match.group(0)
        assert re.search(r"requestSdkUrlUpdate\(.+['\"]replace['\"]", body), \
            "switchView must call requestSdkUrlUpdate with 'replace'"

    def test_drawer_handlers_do_not_call_url_update(self, source):
        # openDrawer and closeDrawer must not call requestSdkUrlUpdate
        for fn_name in ['openDrawer', 'closeDrawer']:
            fn_match = re.search(
                r"function\s+" + fn_name + r"\b(.*?)(\n\s*function\b|\n\s*(async\s+)?function\b)",
                source, re.DOTALL
            )
            if fn_match:
                body = fn_match.group(0)
                assert "requestSdkUrlUpdate" not in body, \
                    f"{fn_name} must not call requestSdkUrlUpdate directly"

    def test_registers_onLangChange(self, source):
        assert "DXI18n.onLangChange" in source



class TestSdkLibraryEncodingContracts:
    """openBookViewer must NOT double-encode; _serializeSdkQuery encodes once."""

    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("sdk-library.js")

    def test_openBookViewer_does_not_call_encodeDocPath(self, source):
        fn_match = re.search(
            r"(async\s+)?function\s+openBookViewer\b(.*?)(\n\s*function\b|\n\s*\}\s*$)",
            source, re.DOTALL,
        )
        assert fn_match, "openBookViewer must exist"
        body = fn_match.group(0)
        assert "encodeDocPath" not in body, \
            "openBookViewer must pass raw path to requestSdkUrlUpdate (no encodeDocPath)"

    def test_serializer_encodes_doc_once(self):
        frame_src = _read_js("launcher-app-frame.js")
        fn_match = re.search(
            r"function\s+_serializeSdkQuery\b(.*?)(\n\s*function\b|\n\s*return\s*\{)",
            frame_src, re.DOTALL,
        )
        assert fn_match, "_serializeSdkQuery must exist"
        body = fn_match.group(1)
        assert "encodeURIComponent" in body, \
            "_serializeSdkQuery must call encodeURIComponent for doc"


class TestSdkLibraryViewerCloseContracts:
    """closeBookViewer URL-push must be guarded by open-state and updateUrl."""

    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("sdk-library.js")

    def test_closeBookViewer_accepts_options(self, source):
        match = re.search(r"function\s+closeBookViewer\s*\(([^)]*)\)", source)
        assert match, "closeBookViewer must exist"
        params = match.group(1).strip()
        assert params, "closeBookViewer must accept an options parameter"

    def test_closeBookViewer_guards_url_update_by_open_state(self, source):
        fn_match = re.search(
            r"function\s+closeBookViewer\b(.*?)(\n\s*function\b|\n\s*(async\s+)?function\b|\n\s*//\s*──)",
            source, re.DOTALL,
        )
        assert fn_match
        body = fn_match.group(0)
        assert re.search(r"wasOpen|was_open|isOpen", body), \
            "closeBookViewer must check if viewer was open before pushing URL"

    def test_closeBookViewer_respects_updateUrl_option(self, source):
        fn_match = re.search(
            r"function\s+closeBookViewer\b(.*?)(\n\s*function\b|\n\s*(async\s+)?function\b|\n\s*//\s*──)",
            source, re.DOTALL,
        )
        assert fn_match
        body = fn_match.group(0)
        assert "updateUrl" in body, \
            "closeBookViewer must check updateUrl option"

    def test_hideSdkLibraryView_preserves_viewer_state(self, source):
        fn_match = re.search(
            r"function\s+hideSdkLibraryView\b(.*?)(\n\s*function\b|\n\s*window\b|\n\s*\}\s*$)",
            source, re.DOTALL,
        )
        assert fn_match, "hideSdkLibraryView must exist"
        body = fn_match.group(0)
        assert "closeBookViewer" not in body, (
            "hideSdkLibraryView must not tear down the book viewer on navigation"
        )
        assert "restoreLauncherToolbarOwner" in body, (
            "hideSdkLibraryView must restore launcher toolbar ownership"
        )

    def test_closeSdkLibrary_delegates_to_hide(self, source):
        fn_match = re.search(
            r"function\s+closeSdkLibrary\b(.*?)(\n\s*function\b|\n\s*window\b|\n\s*\}\s*$)",
            source, re.DOTALL,
        )
        assert fn_match, "closeSdkLibrary must exist"
        body = fn_match.group(0)
        assert "hideSdkLibraryView" in body, (
            "closeSdkLibrary must delegate to hideSdkLibraryView without destroying viewer state"
        )
        assert "closeBookViewer" not in body, (
            "closeSdkLibrary must not call closeBookViewer on navigation hide"
        )

    def test_explicit_close_still_pushes(self, source):
        """Viewer close button and Escape must call closeBookViewer() without updateUrl:false."""
        # Close button: addEventListener('click', closeBookViewer)
        assert re.search(r"addEventListener\(\s*['\"]click['\"].*closeBookViewer\s*\)", source), \
            "Close button must call closeBookViewer (no updateUrl:false)"
        # Escape in viewer: closeBookViewer() without options (may span lines)
        escape_match = re.search(r"Escape.*?closeBookViewer\(\s*\)", source, re.DOTALL)
        assert escape_match, \
            "Escape key in viewer must call closeBookViewer() without suppressing URL update"



class TestIndexHtmlContracts:
    @pytest.fixture(scope="class")
    def source(self):
        return (STATIC / "index.html").read_text(encoding="utf-8")

    def test_postMessage_only_for_module_iframes(self, source):
        """Language postMessage must target module iframes, not same-shell About/SDK views."""
        lines = source.splitlines()

        post_lines = [
            (i, line.strip())
            for i, line in enumerate(lines)
            if "postMessage" in line and "lang" in line.lower()
        ]
        assert post_lines, "Expected at least one language postMessage line"

        for line_idx, line in post_lines:
            assert "AboutDeepX" not in line, (
                f"postMessage must not target AboutDeepX: {line}"
            )
            assert "SDKLibrary" not in line, (
                f"postMessage must not target SDKLibrary: {line}"
            )

        block = "\n".join(lines)
        assert (
            "broadcastToModuleIframes" in block
            or "document.getElementById('appIframe')" in block
        ), "Language sync must use broadcastToModuleIframes or active appIframe"



class TestSdkLibraryChromeI18n:
    """SDK-specific topbar titles and visible chrome must use _t() i18n wrapper.

    Common language/tutorial/help chrome is owned by the shared Launcher toolbar,
    not by SDK Library, because SDK Library shares the Launcher DOM.
    """

    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("sdk-library.js")

    def test_sdk_does_not_render_common_language_button(self, source):
        """SDK Library must not render its own language button."""
        assert "sdk-toolbar-lang" not in source, \
            "SDK Library must use the shared Launcher language dropdown"
        assert "langBtn.title" not in source, \
            "SDK Library must not own common language button title chrome"

    def test_sdk_does_not_render_common_tutorial_button(self, source):
        """SDK Library must not render its own tutorial button."""
        assert "sdkTutorialBtn" not in source, \
            "SDK Library must use #dxToolbarTutorial from the shared Launcher toolbar"
        assert "tutBtn.title" not in source, \
            "SDK Library must not own common tutorial button title chrome"

    def test_sdk_does_not_render_common_help_button(self, source):
        """SDK Library must not render its own help button (Help Mode removed)."""
        assert "sdkHelpBtn" not in source, \
            "SDK Library must not render a local help button"
        assert "helpBtn.title" not in source, \
            "SDK Library must not own common help button title chrome"

    def test_topbar_list_toggle_title_i18n(self, source):
        """List View toggle title must use _t()."""
        assert re.search(r"""title=['"].*\$\{_t\([^)]*'List View'""", source) or \
               re.search(r'title="\$\{_t\(', source) or \
               re.search(r"title\s*=\s*['\"]?\$\{_t\([^)]*List", source) or \
               re.search(r"_t\(\s*['\"]List View['\"]", source), \
            "List View toggle title must use _t()"

    def test_topbar_cabinet_toggle_title_i18n(self, source):
        """Cabinet View toggle title must use _t()."""
        assert re.search(r"_t\(\s*['\"]Cabinet View['\"]", source) or \
               re.search(r"_t\(\s*['\"]Cabinet['\"]", source), \
            "Cabinet View toggle title must use _t()"

    def test_topbar_architecture_button_title_i18n(self, source):
        """Architecture button title must use _t()."""
        match = re.search(r"_t\(\s*['\"]Architecture['\"]", source)
        assert match, "Architecture button title must use _t()"

    def test_viewer_close_title_i18n(self, source):
        """Viewer close button must have i18n title."""
        # Either the title attribute in HTML uses _t or is set in JS via _t
        assert re.search(r"_t\(\s*['\"]Close['\"]", source), \
            "Viewer close button title must use _t()"

    def test_search_placeholder_i18n(self, source):
        """Search input placeholder must use _t()."""
        assert re.search(r"_t\(\s*['\"]Search", source), \
            "Search placeholder must use _t()"

    def test_empty_state_i18n(self, source):
        """Empty/no-results state must use _t()."""
        assert re.search(r"_t\([^)]*['\"]No results", source) or \
               re.search(r"_t\([^)]*['\"]No documents", source), \
            "Empty state text must use _t()"

    def test_error_state_i18n(self, source):
        """Error state must use _t()."""
        assert re.search(r"_t\([^)]*['\"]Failed to load", source), \
            "Error state must use _t()"

    def test_not_found_state_i18n(self, source):
        """Not-found state must use _t()."""
        assert re.search(r"_t\([^)]*['\"]Document Not Found", source) or \
               re.search(r"_t\([^)]*['\"]Not found", source), \
            "Not-found state must use _t()"

    def test_language_hook_refreshes_chrome(self, source):
        """DXI18n.onLangChange callback must trigger a re-render of the view."""
        assert "onLangChange" in source, "onLangChange must be registered"
        assert "renderView" in source, "renderView must exist"
        # Find all onLangChange callbacks and check at least one calls renderView
        matches = re.findall(
            r"onLangChange\(\s*function\s*\([^)]*\)\s*\{([\s\S]*?)\}\s*\)",
            source
        )
        assert matches, "onLangChange callback must exist"
        has_render = any("renderView" in body for body in matches)
        assert has_render, \
            "At least one onLangChange callback must call renderView to refresh visible chrome"


class TestAboutDeepXChromeI18n:
    """About nav labels and error/retry text must use T() i18n helper."""

    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("about-deepx.js")

    def test_nav_labels_use_lang_maps(self, source):
        """ABOUT_NAV_LABELS must cover all 5 languages."""
        assert "ABOUT_NAV_LABELS" in source
        # Each nav entry must have all 5 language keys
        for section in ("aboutDeveloper", "aboutCompany", "aboutTech", "aboutProducts",
                        "aboutInvestment", "aboutPartners", "aboutNews"):
            assert re.search(
                rf"{section}\s*:\s*\{{[^}}]*en\s*:", source
            ), f"ABOUT_NAV_LABELS.{section} must have 'en' key"
            assert re.search(
                rf"{section}\s*:\s*\{{[^}}]*zh-CN", source
            ), f"ABOUT_NAV_LABELS.{section} must have 'zh-CN' key"

    def test_error_text_uses_T(self, source):
        """Error display must use T() helper."""
        assert re.search(r"T\(\s*\{[^}]*en\s*:\s*['\"]Failed", source), \
            "Error text must use T({ en: 'Failed...' })"

    def test_retry_text_uses_T(self, source):
        """Retry button must use T() helper."""
        assert re.search(r"T\(\s*\{[^}]*en\s*:\s*['\"]Retry", source), \
            "Retry text must use T({ en: 'Retry' })"



class TestSdkLibraryVisibleStates:
    """SDK Library must have visible not-found, empty-search, and error states."""

    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("sdk-library.js")

    @pytest.fixture(scope="class")
    def css(self):
        return (STATIC / "sdk-library.css").read_text(encoding="utf-8")

    def test_render_doc_not_found_exists(self, source):
        """_renderDocNotFound function must exist."""
        assert re.search(r"function\s+_renderDocNotFound", source)

    def test_doc_not_found_has_class_hook(self, source):
        """Not-found render must use a CSS class for styling."""
        fn = re.search(
            r"function\s+_renderDocNotFound\b(.*?)(\n\s*(?:async\s+)?function\b)",
            source, re.DOTALL
        )
        assert fn, "_renderDocNotFound must exist"
        body = fn.group(0)
        assert "sdk-not-found" in body, \
            "_renderDocNotFound must apply 'sdk-not-found' CSS class"

    def test_empty_search_state_exists(self, source):
        """SDK Library must render an empty search state."""
        assert re.search(r"function\s+_renderEmptySearch|sdk-empty-search", source), \
            "Empty search state render function or class must exist"

    def test_empty_search_has_class_hook(self, source):
        """Empty search state must use a CSS class hook."""
        assert "sdk-empty-search" in source, \
            "Empty search must use 'sdk-empty-search' CSS class"

    def test_empty_search_wired_in_searchCabinet(self, source):
        """searchCabinet must invoke empty search state rendering."""
        fn = re.search(
            r"function\s+searchCabinet\b(.*?)(\n\s*function\b)",
            source, re.DOTALL
        )
        assert fn, "searchCabinet must exist"
        body = fn.group(0)
        assert "_showEmptySearch" in body or "_renderEmptySearch" in body, \
            "searchCabinet must call _showEmptySearch or _renderEmptySearch for zero results"

    def test_empty_search_wired_in_searchListView(self, source):
        """searchListView must invoke empty search state rendering."""
        fn = re.search(
            r"function\s+searchListView\b(.*?)(\n\s*function\b)",
            source, re.DOTALL
        )
        assert fn, "searchListView must exist"
        body = fn.group(0)
        assert "_showEmptySearch" in body or "_renderEmptySearch" in body, \
            "searchListView must call _showEmptySearch or _renderEmptySearch for zero results"

    def test_empty_search_cleared_when_query_empty(self, source):
        """Both search functions must clear empty state when query is empty."""
        assert "_clearEmptySearch" in source, \
            "A _clearEmptySearch helper must exist to remove the empty state"
        # Verify it's called in both search functions
        cabinet_fn = re.search(
            r"function\s+searchCabinet\b(.*?)(\n\s*function\b)", source, re.DOTALL
        )
        list_fn = re.search(
            r"function\s+searchListView\b(.*?)(\n\s*function\b)", source, re.DOTALL
        )
        assert cabinet_fn and "_clearEmptySearch" in cabinet_fn.group(0)
        assert list_fn and "_clearEmptySearch" in list_fn.group(0)

    def test_error_state_exists(self, source):
        """renderSdkError function must exist."""
        assert re.search(r"function\s+renderSdkError", source)

    def test_error_state_has_class_hook(self, source):
        """Error panel must use a CSS class hook."""
        fn = re.search(
            r"function\s+renderSdkError\b(.*?)(\n\s*function\b)",
            source, re.DOTALL
        )
        assert fn, "renderSdkError must exist"
        body = fn.group(0)
        assert "sdk-error" in body, \
            "renderSdkError must apply 'sdk-error' CSS class"

    def test_error_state_has_retry(self, source):
        """Error state must have a retry button."""
        fn = re.search(
            r"function\s+renderSdkError\b(.*?)(\n\s*function\b)",
            source, re.DOTALL
        )
        assert fn
        body = fn.group(0)
        assert "sdk-retry-btn" in body, "Error state must have retry button"

    def test_doc_load_error_visible_in_viewer(self, source):
        """Document fetch failure must show error in viewer body."""
        fn = re.search(
            r"(async\s+)?function\s+openBookViewer\b(.*?)(\n\s*function\b|\n\s*\}\s*$)",
            source, re.DOTALL,
        )
        assert fn, "openBookViewer must exist"
        body = fn.group(0)
        assert re.search(r"sdk-doc-error|_t\([^)]*Failed to load", body), \
            "openBookViewer catch block must render visible error with class or i18n text"

    def test_css_has_not_found_styles(self, css):
        """CSS must define .sdk-not-found styles."""
        assert ".sdk-not-found" in css

    def test_css_has_empty_search_styles(self, css):
        """CSS must define .sdk-empty-search styles."""
        assert ".sdk-empty-search" in css

    def test_css_has_error_styles(self, css):
        """CSS must define .sdk-error styles."""
        assert ".sdk-error" in css



class TestToolbarHandlerLeakGuard:
    """SDK must not keep legacy toolbar handlers after shared toolbar handoff."""

    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("sdk-library.js")

    @pytest.fixture(scope="class")
    def sdk_tutorial_source(self):
        return _read_js("sdk-tutorial.js")

    def test_legacy_sdk_toolbar_outside_click_handler_removed(self, source):
        """Removed SDK language dropdown must not leave a document click handler."""
        assert "_toolbarOutsideClickHandler" not in source
        assert "_toolbarOutsideClickBound" not in source

    def test_legacy_sdk_toolbar_language_hook_removed(self, source):
        """Removed SDK language dropdown must not keep a toolbar-specific lang hook."""
        assert "_toolbarLangRefreshHandler" not in source
        assert "_toolbarLangHookBound" not in source
        assert "onLangChange(_toolbarLangRefreshHandler)" not in source

    def test_sdk_library_keeps_single_lifecycle_language_hook(self, source):
        """SDK Library still needs one guarded lifecycle language callback."""
        on_lang_change_calls = re.findall(r"DXI18n\.onLangChange\s*\(", source)
        assert len(on_lang_change_calls) == 1, \
            "SDK Library should register one guarded lifecycle language callback"
        assert "_languageHookRegistered" in source
        assert re.search(r"if\s*\(\s*_languageHookRegistered\s*\)\s*return", source), \
            "registerLanguageHook must guard against duplicate registration"

    def test_sdk_tutorial_uses_shared_toolbar_owner(self, sdk_tutorial_source):
        """SDK tutorial/help buttons must be bound through shared DXToolbar."""
        assert "DXToolbar.connectTutorial" in sdk_tutorial_source
        assert "owner: 'sdk_library'" in sdk_tutorial_source or \
               'owner: "sdk_library"' in sdk_tutorial_source

    def test_sdk_exit_cleanup_hook_exists(self, sdk_tutorial_source):
        """SDK view exit must clean help/tutorial overlays before owner restore."""
        assert "function beforeLeave" in sdk_tutorial_source
        assert "hideTOC" in sdk_tutorial_source
        assert "stop" in sdk_tutorial_source



class TestViewerCloseTitleRefresh:
    """Viewer close button title must be refreshed on language change via helper."""

    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("sdk-library.js")

    def test_refreshViewerChrome_helper_exists(self, source):
        """_refreshViewerChrome helper must exist."""
        assert re.search(r"function\s+_refreshViewerChrome", source), \
            "_refreshViewerChrome helper function must exist"

    def test_refreshViewerChrome_sets_close_title(self, source):
        """_refreshViewerChrome must set .sdk-viewer-close title via _t()."""
        fn = re.search(
            r"function\s+_refreshViewerChrome\b(.*?)(\n\s*function\b)",
            source, re.DOTALL
        )
        assert fn, "_refreshViewerChrome must exist"
        body = fn.group(0)
        assert "sdk-viewer-close" in body, \
            "_refreshViewerChrome must target .sdk-viewer-close"
        assert "_t(" in body, \
            "_refreshViewerChrome must use _t() for i18n"

    def test_language_hook_calls_refreshViewerChrome(self, source):
        """The registerLanguageHook onLangChange callback must call _refreshViewerChrome."""
        fn = re.search(
            r"function\s+registerLanguageHook\b(.*?)(\n\s*function\b)",
            source, re.DOTALL
        )
        assert fn, "registerLanguageHook must exist"
        body = fn.group(0)
        assert "_refreshViewerChrome" in body, \
            "registerLanguageHook's onLangChange callback must call _refreshViewerChrome"

    def test_init_calls_refreshViewerChrome(self, source):
        """initSdkLibrary must call _refreshViewerChrome."""
        fn = re.search(
            r"(async\s+)?function\s+initSdkLibrary\b(.*?)(\n\s*function\b)",
            source, re.DOTALL
        )
        assert fn, "initSdkLibrary must exist"
        body = fn.group(0)
        assert "_refreshViewerChrome" in body, \
            "initSdkLibrary must call _refreshViewerChrome"



class TestSearchListViewCardTracking:
    """searchListView must track content card matches separately from sidebar."""

    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("sdk-library.js")

    def test_searchListView_has_separate_content_match_var(self, source):
        """searchListView must have a separate variable for content card matches."""
        fn = re.search(
            r"function\s+searchListView\b(.*?)(\n\s*function\b)",
            source, re.DOTALL
        )
        assert fn, "searchListView must exist"
        body = fn.group(0)
        assert re.search(r"contentCardMatch|cardMatch|contentMatch", body), \
            "searchListView must track content card matches in a dedicated variable"

    def test_searchListView_empty_state_based_on_cards(self, source):
        """Empty state decision must be based on content card matches, not sidebar."""
        fn = re.search(
            r"function\s+searchListView\b(.*?)(\n\s*function\b)",
            source, re.DOTALL
        )
        assert fn, "searchListView must exist"
        body = fn.group(0)
        # The empty state condition should reference the card match variable
        assert re.search(
            r"if\s*\(\s*!contentCardMatch|if\s*\(\s*!cardMatch|if\s*\(\s*!contentMatch",
            body
        ), "Empty state must be conditional on content card match count (not anyMatch)"

    def test_searchListView_does_not_mix_sidebar_into_empty_state(self, source):
        """searchListView must not use a single anyMatch for both sidebar and content."""
        fn = re.search(
            r"function\s+searchListView\b(.*?)(\n\s*function\b)",
            source, re.DOTALL
        )
        assert fn, "searchListView must exist"
        body = fn.group(0)
        # Should NOT have a pattern where sidebar match sets anyMatch that controls empty state
        lines = body.split('\n')
        # Ensure no single 'anyMatch' variable is used for both sidebar groups and empty state
        has_any_match_for_empty = bool(re.search(r"if\s*\(\s*!anyMatch\s*\)\s*_showEmptySearch", body))
        assert not has_any_match_for_empty, \
            "Must not use a single anyMatch for both sidebar and content empty-state decision"




class TestWave2D_HtmlLangDefault:
    """index.html must default to lang='en' since the default UI is English."""

    def test_html_lang_is_en(self):
        html = (STATIC / "index.html").read_text(encoding="utf-8")
        assert re.search(r'<html\s+lang="en"', html), (
            "index.html must use lang='en' as default (not 'ko')"
        )


class TestWave2D_OrbitalCardAccessibility:
    """Orbital cards must be keyboard-accessible with role=button and Enter/Space activation."""

    def test_orbital_cards_have_role_button_setup(self):
        src = (STATIC / "launcher-app-frame.js").read_text(encoding="utf-8")
        assert "role" in src and "button" in src, (
            "launcher-app-frame.js must set role='button' on orbital cards"
        )
        assert re.search(r"\.setAttribute\(['\"]role['\"],\s*['\"]button['\"]\)", src), (
            "orbital cards must get role='button' via setAttribute"
        )

    def test_orbital_cards_have_keydown_enter_space_handler(self):
        src = (STATIC / "launcher-app-frame.js").read_text(encoding="utf-8")
        assert re.search(r"addEventListener\(['\"]keydown['\"]", src), (
            "orbital cards must have a keydown event listener"
        )
        assert "Enter" in src or "key === 'Enter'" in src, (
            "keydown handler must respond to Enter key"
        )
        assert "' '" in src or "key === ' '" in src, (
            "keydown handler must respond to Space key"
        )
        assert ".click()" in src, (
            "keydown handler must trigger click on the card"
        )


class TestWave2D_SdkLibrarySpanishSupport:
    """sdk-library.js _t() must accept a 6th 'es' argument and return it for Spanish."""

    def test_t_function_has_es_parameter(self):
        src = (STATIC / "sdk-library.js").read_text(encoding="utf-8")
        match = re.search(r"function\s+_t\(([^)]+)\)", src)
        assert match, "_t function not found"
        params = [p.strip() for p in match.group(1).split(",")]
        assert len(params) >= 6, f"_t must have at least 6 params (got {len(params)}): {params}"
        assert "es" in params, "_t must include 'es' parameter"

    def test_t_function_maps_es_language(self):
        src = (STATIC / "sdk-library.js").read_text(encoding="utf-8")
        fn_match = re.search(
            r"function\s+_t\b(.*?)(\n\s*function\b)",
            src, re.DOTALL
        )
        assert fn_match, "_t function body not found"
        body = fn_match.group(1)
        assert "es:" in body or "'es'" in body, (
            "_t map must include 'es' key for Spanish"
        )

    def test_t_call_sites_have_six_arguments(self):
        """All _t() call sites in sdk-library.js must pass 6 arguments (including es)."""
        src = (STATIC / "sdk-library.js").read_text(encoding="utf-8")
        # Find all _t( calls - match balanced parens for multi-line calls
        calls = re.finditer(r"_t\(", src)
        for call in calls:
            start = call.start()
            # Skip the function definition itself
            preceding = src[max(0, start - 20):start]
            if "function" in preceding:
                continue
            # Count commas to determine arg count (args = commas + 1)
            depth = 0
            commas = 0
            i = call.end()
            while i < len(src):
                ch = src[i]
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    if depth == 0:
                        break
                    depth -= 1
                elif ch == "," and depth == 0:
                    commas += 1
                i += 1
            arg_count = commas + 1
            line_num = src[:start].count("\n") + 1
            assert arg_count >= 6, (
                f"_t() call at line {line_num} has only {arg_count} args, needs 6 (including es)"
            )


class TestWave2D_SplashSpanishSpans:
    """launcher-splash.js must include Spanish spans in proceed prompt and replay."""

    def test_showProceedPrompt_has_es_span(self):
        src = (STATIC / "launcher-splash.js").read_text(encoding="utf-8")
        fn_match = re.search(
            r"function\s+_showProceedPrompt\b(.*?)(\n\s*function\b)",
            src, re.DOTALL
        )
        assert fn_match, "_showProceedPrompt function not found"
        body = fn_match.group(1)
        assert 'class="es"' in body, (
            "_showProceedPrompt must include a <span class='es'> for Spanish"
        )

    def test_replaySplash_skip_has_es_span(self):
        src = (STATIC / "launcher-splash.js").read_text(encoding="utf-8")
        fn_match = re.search(
            r"function\s+replaySplash\b(.*?)(\n\s*\/\*|$)",
            src, re.DOTALL
        )
        assert fn_match, "replaySplash function not found"
        body = fn_match.group(1)
        assert 'class="es"' in body, (
            "replaySplash must include <span class='es'> for Spanish"
        )

    def test_replaySplash_core_text_has_es_span(self):
        src = (STATIC / "launcher-splash.js").read_text(encoding="utf-8")
        fn_match = re.search(
            r"function\s+replaySplash\b(.*?)(\n\s*\/\*|$)",
            src, re.DOTALL
        )
        assert fn_match, "replaySplash function not found"
        body = fn_match.group(1)
        # splash-core-text section must have es span
        core_text_pos = body.find("splash-core-text")
        assert core_text_pos != -1, "replaySplash must contain splash-core-text"
        core_text_section = body[core_text_pos:core_text_pos + 500]
        assert 'class="es"' in core_text_section, (
            "splash-core-text in replaySplash must include Spanish span"
        )




class TestAboutSubtitleLocalization:
    """About DEEPX header uses the shared DXBrand component; its subtitle must stay localized
    across all UI languages (rendered by DXBrand.mount in about-deepx.js, not static HTML)."""

    def test_about_uses_shared_brand_slot(self):
        """index.html must host the shared brand slot (unified with modules), not bespoke logo."""
        html = (STATIC / "index.html").read_text(encoding="utf-8")
        assert 'id="aboutBrand"' in html and "dx-brand-slot" in html, (
            "About header must use the shared dx-brand-slot (#aboutBrand)"
        )
        assert "about-logo-sub" not in html, (
            "bespoke about-logo markup must be gone; use DXBrand instead"
        )

    def test_about_brand_subtitle_has_all_required_langs(self):
        """DXBrand.mount for About must pass a subtitle object covering every UI language."""
        js = (STATIC / "about-deepx.js").read_text(encoding="utf-8")
        assert "target: '#aboutBrand'" in js, "mountAboutBrand must target #aboutBrand"
        for lang in ("en", "ko", "ja", "zh-CN", "zh-TW", "es"):
            key = f"'{lang}'" if "-" in lang else lang
            assert re.search(rf"{re.escape(key)}\s*:\s*'", js), (
                f"About brand subtitle missing language '{lang}'"
            )




class TestNoComingSoonPlaceholder:
    """about-data.json must not expose a visible 'Coming Soon' placeholder."""

    def test_about_data_no_coming_soon_text(self):
        data = _load_json("about-data.json")
        errors = []
        _find_coming_soon(data, "about-data", errors)
        assert not errors, (
            "about-data.json contains 'Coming Soon' placeholder:\n"
            + "\n".join(errors)
        )


def _find_coming_soon(obj, path, errors):
    """Recursively check for 'Coming Soon' in string values."""
    if isinstance(obj, str):
        if "Coming Soon" in obj:
            errors.append(f"{path} = {obj!r}")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _find_coming_soon(v, f"{path}.{k}", errors)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _find_coming_soon(item, f"{path}[{i}]", errors)




class TestAboutHasActivePanelNotHardcoded:
    """_aboutHasActivePanel must check real state, not always return false."""

    def test_about_has_active_panel_not_hardcoded_false(self):
        src = _read_js("about-deepx.js")
        # Must not have a getter that always returns false
        assert "get: function() { return false; }" not in src, (
            "_aboutHasActivePanel is hardcoded to return false; "
            "must check actual overlay/panel state"
        )

    def test_about_has_active_panel_getter_checks_visibility_and_scroll(self):
        """Getter must check About view visibility and scroll position."""
        src = _read_js("about-deepx.js")
        # Property getter must reference the about view element and scrollTop
        assert "aboutScroll" in src or "about-view" in src, (
            "_aboutHasActivePanel getter must reference About view element"
        )
        assert "scrollTop" in src, (
            "_aboutHasActivePanel getter must check scrollTop"
        )
        # Getter must be non-trivial: check visibility
        prop_match = re.search(
            r"_aboutHasActivePanel.*?get:\s*function\(\)\s*\{(.*?)\}",
            src, re.DOTALL,
        )
        assert prop_match, "_aboutHasActivePanel getter not found"
        getter_body = prop_match.group(1)
        assert "visible" in getter_body or "display" in getter_body, (
            "Getter must check visibility of the About view"
        )
        assert "scrollTop" in getter_body, (
            "Getter must check scrollTop inside the getter body"
        )






class TestAboutBookCardKeyboardAccess:
    """about-book-card elements must be keyboard accessible."""

    @pytest.fixture(scope="class")
    def html_source(self):
        return (STATIC / "index.html").read_text(encoding="utf-8")

    def test_about_book_card_has_role_button(self, html_source):
        cards = re.findall(r'<div\s+class="about-book-card[^"]*"[^>]*>', html_source)
        assert cards, "about-book-card elements must exist"
        for card in cards:
            assert 'role="button"' in card, (
                f"about-book-card must have role=\"button\": {card[:80]}"
            )

    def test_about_book_card_has_tabindex(self, html_source):
        cards = re.findall(r'<div\s+class="about-book-card[^"]*"[^>]*>', html_source)
        for card in cards:
            assert 'tabindex="0"' in card, (
                f"about-book-card must have tabindex=\"0\": {card[:80]}"
            )


class TestLandingPosterKeyboardAccess:
    """#landingPoster must be keyboard accessible."""

    @pytest.fixture(scope="class")
    def html_source(self):
        return (STATIC / "index.html").read_text(encoding="utf-8")

    def test_landing_poster_has_role_button(self, html_source):
        match = re.search(r'<div[^>]*id="landingPoster"[^>]*>', html_source)
        assert match, "landingPoster element must exist"
        assert 'role="button"' in match.group(0), (
            "landingPoster must have role=\"button\""
        )

    def test_landing_poster_has_tabindex(self, html_source):
        match = re.search(r'<div[^>]*id="landingPoster"[^>]*>', html_source)
        assert match, "landingPoster element must exist"
        assert 'tabindex="0"' in match.group(0), (
            "landingPoster must have tabindex=\"0\""
        )


class TestAboutNavTabKeyboardAccess:
    """about-nav-tab elements must be keyboard focusable."""

    @pytest.fixture(scope="class")
    def html_source(self):
        return (STATIC / "index.html").read_text(encoding="utf-8")

    def test_about_nav_tab_has_tabindex(self, html_source):
        tabs = re.findall(r'<a\s+class="about-nav-tab"[^>]*>', html_source)
        assert tabs, "about-nav-tab elements must exist"
        for tab in tabs:
            assert 'tabindex="0"' in tab, (
                f"about-nav-tab must have tabindex=\"0\": {tab[:80]}"
            )

    def test_about_nav_tab_has_role_button(self, html_source):
        tabs = re.findall(r'<a\s+class="about-nav-tab"[^>]*>', html_source)
        for tab in tabs:
            assert 'role="button"' in tab, (
                f"about-nav-tab must have role=\"button\": {tab[:80]}"
            )


class TestLandingPosterEnterSpace:
    """launcher-app-frame.js must bind Enter/Space on #landingPoster."""

    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("launcher-app-frame.js")

    def test_poster_keydown_binding(self, source):
        assert "landingPoster" in source, "launcher-app-frame.js must reference landingPoster"
        assert re.search(
            r"landingPoster.*keydown|keydown.*landingPoster",
            source, re.DOTALL,
        ), "landingPoster must have a keydown listener"


class TestAboutBookCardEnterSpace:
    """launcher-app-frame.js must bind Enter/Space on about-book-card."""

    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("launcher-app-frame.js")

    def test_about_book_card_keydown_binding(self, source):
        assert "about-book-card" in source, "launcher-app-frame.js must reference about-book-card"
        assert re.search(
            r"about-book-card.*keydown|keydown.*about-book-card",
            source, re.DOTALL,
        ), "about-book-card must have a keydown listener"


class TestAboutNavTabEnterSpace:
    """about-deepx.js must bind Enter/Space on about-nav-tab."""

    @pytest.fixture(scope="class")
    def source(self):
        return _read_js("about-deepx.js")

    def test_about_nav_tab_keydown_binding(self, source):
        assert re.search(
            r"about-nav-tab.*keydown|keydown.*about-nav-tab",
            source, re.DOTALL,
        ), "about-nav-tab must have a keydown listener in about-deepx.js"


class TestEscapeAboutActivePanel:
    """Escape when About has active panel must call closeAboutPanel."""

    def test_escape_about_active_panel_calls_close_about_panel(self):
        """When currentApp is about and _aboutHasActivePanel is true,
        Escape must call window.closeAboutPanel()."""
        src = _read_js("launcher.js")
        assert "closeAboutPanel" in src, (
            "launcher.js Escape handler must call closeAboutPanel "
            "when About has an active panel"
        )

    def test_escape_about_active_panel_branch_exists(self):
        """Escape handler must have a branch for about + active panel true."""
        src = _read_js("launcher.js")
        # Must have logic: if about and _aboutHasActivePanel → closeAboutPanel
        assert re.search(
            r"_aboutHasActivePanel.*closeAboutPanel|closeAboutPanel.*_aboutHasActivePanel",
            src, re.DOTALL,
        ), (
            "Escape handler must branch on _aboutHasActivePanel "
            "and call closeAboutPanel"
        )




class TestLauncherEscapeDefersToSdk:
    """Launcher Escape handler must not call goHome when SDK
    has an active viewer or architecture overlay open."""

    def test_escape_guards_sdk_viewer_before_go_home(self):
        """When currentApp is sdk-library and viewer is open,
        launcher must skip goHome so SDK handler closes the viewer."""
        src = _read_js("launcher.js")
        assert re.search(
            r"_sdkLibHasViewer",
            src,
        ), (
            "launcher.js Escape handler must check _sdkLibHasViewer "
            "to avoid goHome when SDK viewer is open"
        )

    def test_escape_guards_sdk_overlay_before_go_home(self):
        """When currentApp is sdk-library and arch overlay is open,
        launcher must skip goHome so SDK handler closes the overlay."""
        src = _read_js("launcher.js")
        assert re.search(
            r"_sdkLibHasOverlay",
            src,
        ), (
            "launcher.js Escape handler must check _sdkLibHasOverlay "
            "to avoid goHome when SDK arch overlay is open"
        )

    def test_sdk_guard_precedes_go_home_for_sdk_library(self):
        """The SDK viewer/overlay guard must appear before the
        generic currentApp goHome branch in the Escape block."""
        src = _read_js("launcher.js")
        # Find the Escape handler that contains goHome (skip splash Escape).
        idx = 0
        escape_block_start = -1
        while True:
            pos = src.find("e.key === 'Escape'", idx)
            if pos == -1:
                break
            # Check if this block contains goHome
            block_end = src.find("\n    if (e.", pos + 1)
            candidate = src[pos:block_end] if block_end != -1 else src[pos:]
            if "goHome" in candidate:
                escape_block_start = pos
                break
            idx = pos + 1
        assert escape_block_start != -1, "Escape handler with goHome not found"
        # Narrow to just this Escape block
        escape_block = src[escape_block_start:]
        next_handler = escape_block.find("\n    if (e.", 1)
        if next_handler != -1:
            escape_block = escape_block[:next_handler]
        viewer_pos = escape_block.find("_sdkLibHasViewer")
        overlay_pos = escape_block.find("_sdkLibHasOverlay")
        assert viewer_pos != -1, "_sdkLibHasViewer guard missing in Escape block"
        assert overlay_pos != -1, "_sdkLibHasOverlay guard missing in Escape block"
        go_home_pos = escape_block.find("ns.goHome()", max(viewer_pos, overlay_pos))
        if go_home_pos == -1:
            go_home_pos = escape_block.find("goHome()", max(viewer_pos, overlay_pos))
        assert go_home_pos != -1, (
            "goHome call not found after SDK guards in Escape block"
        )
        assert viewer_pos < go_home_pos, (
            "_sdkLibHasViewer guard must precede goHome"
        )
        assert overlay_pos < go_home_pos, (
            "_sdkLibHasOverlay guard must precede goHome"
        )
