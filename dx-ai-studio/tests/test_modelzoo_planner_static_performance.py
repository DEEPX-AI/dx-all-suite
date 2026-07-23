from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLANNER_JS = ROOT / "dx_planner/static/js"
MODELZOO_JS = ROOT / "dx_modelzoo/static/js"


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


def test_planner_recommendation_and_resize_redraw_are_debounced():
    source = _read(PLANNER_JS / "planner.js")
    init_body = _function_body(source, "async function initConfigurator(")
    resize_body = _function_body(source, "function observeOverviewChartResize(")
    run_body = _function_body(source, "function runRecommendation(")

    assert "let _recommendationDebounceTimer = null;" in source
    assert "let _lastRecommendationSignature = null;" in source
    assert "function recommendationSignature(" in source
    assert "function scheduleRecommendation(options)" in source
    assert "setTimeout(() => {" in source
    assert "if (signature !== _lastRecommendationSignature || !_lastResults)" in run_body
    assert "RecommendEngine.recommend(inputs, platforms)" in run_body
    assert "runRecommendation(opts);" in _function_body(source, "function scheduleRecommendation(")
    assert "scheduleRecommendation({ preserveSelection: true });" in init_body
    assert "runRecommendation({ preserveSelection: true });" not in init_body
    assert "let _overviewResizeTimer = null;" in source
    assert "scheduleOverviewChartRedraw({ debounce: true });" in resize_body


def test_planner_charts_cache_theme_colors():
    source = _read(PLANNER_JS / "charts.js")
    theme_body = _function_body(source, "function getThemeColor(")

    assert "let _plannerThemeColorCache = null;" in source
    assert "function cachePlannerThemeColors(" in source
    assert "return (_plannerThemeColorCache || cachePlannerThemeColors())[varName] || '';" in theme_body
    assert "getComputedStyle(document.documentElement)" not in theme_body


def test_planner_explorer_batches_task_tab_render_and_joins_options():
    source = _read(PLANNER_JS / "explorer.js")
    tabs_body = _function_body(source, "\n  _renderTaskTabs(platform, inputs)")
    radar_body = _function_body(source, "\n  _renderRadar(platform, platforms, inputs, result)")

    assert "_taskTabRenderFrame: null" in source
    assert "_scheduleTaskTabRender(platform, nextInputs, null);" in tabs_body
    assert "requestAnimationFrame(() => {" in _function_body(source, "\n  _scheduleTaskTabRender(platform, inputs, result)")
    for direct_call in (
        "this._renderFacts(platform, nextInputs, null)",
        "this._renderRadar(platform, DataLoader.getPlatforms(), nextInputs, null)",
        "this._renderGroupBar(platform, nextInputs)",
        "this._renderTable(platform, nextInputs)",
    ):
        assert direct_call not in tabs_body
    assert "const options = platforms" in radar_body
    assert "dd.innerHTML += '<option" not in radar_body


def test_planner_escape_html_avoids_throwaway_dom_nodes():
    source = _read(PLANNER_JS / "explorer.js")
    esc_body = _function_body(source, "\n  _escHtml(value)")

    assert "document.createElement" not in esc_body
    assert ".replace(/&/g, '&amp;')" in esc_body
    assert ".replace(/</g, '&lt;')" in esc_body


def test_modelzoo_catalog_viewport_commits_only_changed_html_and_debounces_state_save():
    source = _read(MODELZOO_JS / "catalog.js")
    card_body = _function_body(source, "\n  _renderCardViewport(container, models, start, end)")
    list_body = _function_body(source, "\n  _renderListViewport(container, models, start, end)")
    save_body = _function_body(source, "\n  _saveState()")

    assert "_lastViewportSignature: ''" in source
    assert "_stateSaveTimer: null" in source
    assert "_commitViewportHtml(container, html, savedScrollTop, signature);" in card_body
    assert "_commitViewportHtml(container, html, savedScrollTop, signature);" in list_body
    assert "container.innerHTML = html" not in card_body
    assert "container.innerHTML = html" not in list_body
    assert "clearTimeout(this._stateSaveTimer)" in save_body
    assert "setTimeout(() => {" in save_body
    assert "sessionStorage.setItem" not in save_body
    assert "function _commitCatalogStateSave(state)" in source


def test_modelzoo_detail_sliders_are_raf_scheduled():
    source = _read(MODELZOO_JS / "detail.js")
    ba_body = _function_body(source, "function initBeforeAfterSliders(")
    overlay_body = _function_body(source, "function initOverlayOpacitySliders(")

    assert "data-overlay-opacity-target=\"overlayImg\"" in source
    assert "oninput=\"document.getElementById('overlayImg')" not in source
    assert "let sliderRaf = null;" in ba_body
    assert "function scheduleSliderUpdate(clientX)" in ba_body
    assert "requestAnimationFrame(() => {" in ba_body
    assert "scheduleSliderUpdate(e.clientX);" in ba_body
    assert "scheduleSliderUpdate(e.touches[0].clientX);" in ba_body
    assert "let overlayRaf = null;" in overlay_body
    assert "requestAnimationFrame(() => {" in overlay_body


def test_modelzoo_health_poll_updates_detail_actions_without_full_rerender():
    app = _read(MODELZOO_JS / "app.js")
    detail = _read(MODELZOO_JS / "detail.js")
    health_body = _function_body(app, "async function checkDxAppHealth(")

    assert "function refreshDetailActionBarsForHealth(" in detail
    assert "data-detail-action-bar" in detail
    assert "data-detail-downloads" in detail
    assert "refreshDetailActionBarsForHealth();" in health_body
    assert "renderDetailPage(getModelIdFromHash(location.hash));" not in health_body


def test_modelzoo_download_status_writes_only_when_changed():
    source = _read(MODELZOO_JS / "detail.js")
    start_body = _function_body(source, "async function downloadModel(")

    assert "function setModelZooStatusHtml(" in source
    assert "if (el._lastModelZooStatusHtml === html) return;" in source
    assert "setModelZooStatusHtml(statusEl," in start_body
    assert "statusEl.innerHTML =" not in start_body
