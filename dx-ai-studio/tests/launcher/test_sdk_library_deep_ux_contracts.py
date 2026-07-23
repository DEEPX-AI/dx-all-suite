"""SDK Library deep document exploration UX contracts.

Validates structural invariants for breadcrumb, search summary,
selected state, and retry behaviors in sdk-library.js and sdk-library.css.
"""
import re
from pathlib import Path

import pytest

STATIC = Path(__file__).resolve().parents[2] / "launcher" / "static"


@pytest.fixture()
def sdk_js():
    return (STATIC / "sdk-library.js").read_text(encoding="utf-8")


@pytest.fixture()
def sdk_css():
    return (STATIC / "sdk-library.css").read_text(encoding="utf-8")


def _function_body(source, name):
    match = re.search(
        rf"(?:async\s+)?function\s+{name}\b.*?(?=\n\s*(?:async\s+)?function\s+\w+\b|\Z)",
        source,
        re.DOTALL,
    )
    assert match, f"{name} function not found"
    return match.group(0)


def _css_rule(source, selector):
    match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", source, re.DOTALL)
    assert match, f"{selector} rule not found"
    return re.sub(r"\s+", "", match.group(1))




class TestBreadcrumbAndSelectionContracts:
    """sdk-library.js must expose breadcrumb/selection helpers."""

    @pytest.mark.parametrize("symbol", [
        "buildDocumentTrail",
        "renderDocumentTrail",
        "updateSelectedDocumentState",
        "renderSearchSummary",
        "clearSearchSummary",
    ])
    def test_helper_symbols_exist(self, sdk_js, symbol):
        assert symbol in sdk_js, f"Missing helper: {symbol}"

    def test_buildDocumentTrail_called_from_openBookViewer(self, sdk_js):
        # openBookViewer body should invoke buildDocumentTrail
        body = _function_body(sdk_js, "openBookViewer")
        assert "buildDocumentTrail" in body, \
            "openBookViewer must call buildDocumentTrail"

    def test_renderDocumentTrail_called_from_openBookViewer(self, sdk_js):
        body = _function_body(sdk_js, "openBookViewer")
        assert "renderDocumentTrail" in body, \
            "openBookViewer must call renderDocumentTrail"

    def test_updateSelectedDocumentState_called_from_openBookViewer(self, sdk_js):
        body = _function_body(sdk_js, "openBookViewer")
        assert "updateSelectedDocumentState" in body, \
            "openBookViewer must call updateSelectedDocumentState"

    def test_openBookViewer_does_not_precompute_unused_trail(self, sdk_js):
        body = _function_body(sdk_js, "openBookViewer")
        assert "var _trail" not in body, (
            "openBookViewer must not keep a dead buildDocumentTrail assignment"
        )

    def test_renderDocumentTrail_inserts_current_path_after_viewer_header(self, sdk_js):
        body = _function_body(sdk_js, "renderDocumentTrail")
        assert "sdk-viewer-container" in body, (
            "renderDocumentTrail must insert breadcrumb in the viewer container"
        )
        assert "header.parentNode.insertBefore(container, header.nextSibling)" in body, (
            "breadcrumb must render after the header as its own full-width row"
        )
        assert "header.insertBefore(container" not in body, (
            "breadcrumb must not be inserted inside the flex header"
        )

    def test_updateSelectedDocumentState_scopes_section_lookup_to_drawer(self, sdk_js):
        body = _function_body(sdk_js, "updateSelectedDocumentState")
        assert "drawerEl.querySelector" in body, (
            "section selection must be scoped to the selected drawer"
        )

    def test_updateSelectedDocumentState_escapes_css_attribute_selectors(self, sdk_js):
        body = _function_body(sdk_js, "updateSelectedDocumentState")
        assert "CSS.escape(trail.drawer.id)" in body, (
            "drawer selector must escape data-backed IDs"
        )
        assert "CSS.escape(trail.section.id)" in body, (
            "section selector must escape data-backed IDs"
        )

    @pytest.mark.parametrize("function_name", ["searchCabinet", "searchListView"])
    def test_renderSearchSummary_called_from_search_paths(self, sdk_js, function_name):
        body = _function_body(sdk_js, function_name)
        assert "renderSearchSummary(q, matchCount)" in body, (
            f"{function_name} must call renderSearchSummary with query and result count"
        )

    @pytest.mark.parametrize("function_name", ["searchCabinet", "searchListView"])
    def test_clearSearchSummary_called_when_query_empty(self, sdk_js, function_name):
        body = _function_body(sdk_js, function_name)
        empty_branch = body.find("if (!q)")
        assert empty_branch != -1, f"{function_name} must have an empty-query branch"
        clear_pos = body.find("clearSearchSummary()", empty_branch)
        return_pos = body.find("return", empty_branch)
        assert clear_pos != -1, f"{function_name} must clear summary for empty query"
        assert return_pos == -1 or clear_pos < return_pos, (
            f"{function_name} must clear summary before returning from empty query"
        )

    def test_applyQuery_routes_doc_to_viewer_refresh_path(self, sdk_js):
        body = _function_body(sdk_js, "applyQuery")
        assert "parsed.doc" in body, "applyQuery must handle document route state"
        assert "openBookViewer(book" in body, (
            "applyQuery must restore documents through openBookViewer"
        )

    def test_applyQuery_routes_query_to_search_rendering_paths(self, sdk_js):
        body = _function_body(sdk_js, "applyQuery")
        assert "searchCabinet(parsed.q.toLowerCase())" in body
        assert "searchListView(parsed.q.toLowerCase())" in body

    def test_applyQuery_clears_search_summary_for_empty_query(self, sdk_js):
        body = _function_body(sdk_js, "applyQuery")
        query_branch = body.find("if (searchInput && parsed.q !== undefined)")
        assert query_branch != -1, "applyQuery must handle restored q state"
        clear_pos = body.find("clearSearchSummary()", query_branch)
        doc_pos = body.find("// Apply doc", query_branch)
        assert clear_pos != -1, "applyQuery must clear summary when restored q is empty"
        assert doc_pos == -1 or clear_pos < doc_pos, (
            "applyQuery must clear stale search summary before applying doc state"
        )


class TestCSSSelectors:
    """sdk-library.css must contain deep-UX selectors."""

    @pytest.mark.parametrize("selector", [
        ".sdk-breadcrumb",
        ".sdk-breadcrumb-item",
        ".sdk-search-summary",
        ".sdk-selected",
        ".sdk-current-path",
    ])
    def test_css_selector_exists(self, sdk_css, selector):
        assert selector in sdk_css, f"Missing CSS selector: {selector}"


class TestSdkSelectionHighlightContracts:
    """Document selection state must not leave persistent click outlines."""

    def test_closeBookViewer_clears_document_selection_state(self, sdk_js):
        body = _function_body(sdk_js, "closeBookViewer")
        assert "clearSelectedDocumentState()" in body, (
            "closing the document viewer must clear stale .sdk-selected classes"
        )

    def test_clearSelectedDocumentState_removes_sdk_selected_classes(self, sdk_js):
        body = _function_body(sdk_js, "clearSelectedDocumentState")
        assert "document.querySelectorAll('.sdk-selected')" in body
        assert "classList.remove('sdk-selected')" in body

    def test_sdk_selected_does_not_draw_global_outline(self, sdk_css):
        rule = _css_rule(sdk_css, ".sdk-selected")
        assert "outline:" not in rule
        assert "box-shadow:" not in rule




class TestRetryContracts:
    """Retry actions must exist and must not push history."""

    @pytest.mark.parametrize("symbol", [
        "retryLoadSdkData",
        "retryLoadDocument",
        "renderSdkRetryAction",
    ])
    def test_retry_symbols_exist(self, sdk_js, symbol):
        assert symbol in sdk_js, f"Missing retry helper: {symbol}"

    def test_retryLoadDocument_no_history_push(self, sdk_js):
        match = re.search(
            r"function retryLoadDocument\b[^}]*\}",
            sdk_js, re.DOTALL,
        )
        assert match, "retryLoadDocument function not found"
        body = match.group(0)
        assert "history.pushState" not in body, \
            "retryLoadDocument must not call history.pushState"
        assert "history.replaceState" not in body, \
            "retryLoadDocument must not call history.replaceState"
        assert "history: 'push'" not in body, \
            "retryLoadDocument must not push via LauncherRouter"

    def test_retryLoadSdkData_resets_initialized_flag_before_init(self, sdk_js):
        body = _function_body(sdk_js, "retryLoadSdkData")
        reset_pos = body.find("_sdkInitialized = false")
        init_pos = body.find("initSdkLibrary()")
        assert reset_pos != -1, "retryLoadSdkData must allow initSdkLibrary to re-run"
        assert init_pos != -1, "retryLoadSdkData must call initSdkLibrary"
        assert reset_pos < init_pos, (
            "retryLoadSdkData must reset _sdkInitialized before calling initSdkLibrary"
        )

    def test_initSdkLibrary_binds_keydown_once(self, sdk_js):
        assert "_keydownBound" in sdk_js, "SDK Library must track keydown binding"
        body = _function_body(sdk_js, "initSdkLibrary")
        assert "if (!_keydownBound)" in body, (
            "initSdkLibrary must guard document keydown listener registration"
        )
        add_pos = body.find("document.addEventListener('keydown', handleKeydown)")
        mark_pos = body.find("_keydownBound = true")
        assert add_pos != -1, "initSdkLibrary must bind handleKeydown"
        assert mark_pos != -1, "initSdkLibrary must mark keydown as bound"
        assert add_pos < mark_pos, "keydown binding flag must be set after listener add"


class TestPdfFallbackContracts:
    """PDF viewer must check availability before rendering iframes."""

    def test_pdf_status_helper_uses_launcher_status_api(self, sdk_js):
        body = _function_body(sdk_js, "checkPdfAvailability")
        assert "/api/sdk-pdf-status?path=" in body
        assert "encodeURIComponent(path)" in body
        assert "await res.json()" in body

    def test_pdf_unavailable_renderer_has_retry_and_no_iframe(self, sdk_js):
        body = _function_body(sdk_js, "renderPdfUnavailable")
        assert "sdk-doc-error" in body
        assert "PDF is not packaged" in body
        assert "renderSdkRetryAction" in body
        assert "<iframe" not in body

    def test_openBookViewer_checks_pdf_status_before_iframe(self, sdk_js):
        body = _function_body(sdk_js, "openBookViewer")
        pdf_pos = body.index("if (book.type === 'pdf')")
        status_pos = body.index("await checkPdfAvailability(book.path)", pdf_pos)
        iframe_pos = body.index("sdk-pdf-frame", pdf_pos)
        unavailable_pos = body.index("renderPdfUnavailable(body, book)", pdf_pos)

        assert status_pos < iframe_pos
        assert status_pos < unavailable_pos
        assert "pdfInfo.available && pdfInfo.url" in body[pdf_pos:]

    def test_retryLoadDocument_reuses_openBookViewer_without_history_push(self, sdk_js):
        body = _function_body(sdk_js, "retryLoadDocument")
        assert "openBookViewer(book, null, { updateUrl: false })" in body
        assert "history.pushState" not in body
        assert "requestSdkUrlUpdate" not in body


class TestSearchSummaryLocalization:
    """Search summary must show localized copy for all 5 languages."""

    def test_renderSearchSummary_uses_t_helper(self, sdk_js):
        # renderSearchSummary body should use _t(...) for localization
        body = _function_body(sdk_js, "renderSearchSummary")
        assert "_t(" in body, "renderSearchSummary must use _t() for localization"




@pytest.fixture()
def tutorial_js():
    return (STATIC / "sdk-tutorial.js").read_text(encoding="utf-8")


class TestReleaseConsoleLogGating:
    """console.log('[SDK Library]' / '[SDK Tutorial]' must not fire
    unconditionally — they must be gated behind DX_DEBUG_SDK."""

    _LOG_PATTERN = re.compile(
        r"""console\.log\(\s*['"]?\[SDK (Library|Tutorial)\]"""
    )
    _GUARD = "DX_DEBUG_SDK"

    def test_sdk_library_no_ungated_console_log(self, sdk_js):
        """sdk-library.js must not contain bare console.log('[SDK Library]')."""
        for m in self._LOG_PATTERN.finditer(sdk_js):
            # 해당 줄 전체를 추출하여 가드 확인
            line_start = sdk_js.rfind("\n", 0, m.start()) + 1
            line = sdk_js[line_start : sdk_js.find("\n", m.end())]
            assert self._GUARD in line or "if" in sdk_js[max(0, line_start - 80) : line_start], (
                f"Ungated release console.log found in sdk-library.js: {line.strip()}"
            )

    def test_sdk_tutorial_no_ungated_console_log(self, tutorial_js):
        """sdk-tutorial.js must not contain bare console.log('[SDK Tutorial]')."""
        for m in self._LOG_PATTERN.finditer(tutorial_js):
            line_start = tutorial_js.rfind("\n", 0, m.start()) + 1
            line = tutorial_js[line_start : tutorial_js.find("\n", m.end())]
            assert self._GUARD in line or "if" in tutorial_js[max(0, line_start - 80) : line_start], (
                f"Ungated release console.log found in sdk-tutorial.js: {line.strip()}"
            )




class TestSdkEscapePropagation:
    """Escape handlers in sdk-library.js must stop immediate propagation."""

    def test_viewer_escape_stops_immediate_propagation(self, sdk_js):
        body = _function_body(sdk_js, "handleKeydown")
        viewer_escape = body.find("closeBookViewer()")
        assert viewer_escape != -1, "handleKeydown must call closeBookViewer on Escape"
        # Between Escape and closeBookViewer there must be stopImmediatePropagation
        escape_pos = body.rfind("Escape", 0, viewer_escape)
        segment = body[escape_pos:viewer_escape + 100]
        assert "stopImmediatePropagation" in segment, (
            "Escape in viewer must call stopImmediatePropagation"
        )

    def test_overlay_escape_stops_immediate_propagation(self, sdk_js):
        body = _function_body(sdk_js, "handleKeydown")
        overlay_escape = body.find("toggleArchOverlay()")
        assert overlay_escape != -1, "handleKeydown must call toggleArchOverlay on Escape"
        segment = body[overlay_escape:overlay_escape + 120]
        assert "stopImmediatePropagation" in segment, (
            "Escape in arch overlay must call stopImmediatePropagation"
        )

    def test_library_escape_stops_immediate_propagation(self, sdk_js):
        body = _function_body(sdk_js, "handleKeydown")
        lib_escape = body.find("hideSdkLibraryView()")
        assert lib_escape != -1, "handleKeydown must call hideSdkLibraryView on Escape"
        segment = body[lib_escape:lib_escape + 120]
        assert "stopImmediatePropagation" in segment, (
            "Escape in SDK library view must call stopImmediatePropagation"
        )




class TestSdkOverlayStateExposed:
    """sdk-library.js must expose _sdkLibHasOverlay for launcher guard."""

    def test_sdk_lib_has_overlay_exposed(self, sdk_js):
        assert "_sdkLibHasOverlay" in sdk_js, (
            "sdk-library.js must expose window._sdkLibHasOverlay "
            "for launcher Escape isolation"
        )

    def test_sdk_lib_has_overlay_checks_arch_overlay(self, sdk_js):
        overlay_pos = sdk_js.find("_sdkLibHasOverlay")
        assert overlay_pos != -1
        segment = sdk_js[overlay_pos:overlay_pos + 200]
        assert "sdkArchOverlay" in segment, (
            "_sdkLibHasOverlay must check sdkArchOverlay element"
        )
