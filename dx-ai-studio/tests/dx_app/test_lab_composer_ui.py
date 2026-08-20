"""RED static contracts for the DOM-safe progressive Lab Composer UI."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "dx_app" / "templates" / "index.html"
COMPOSER_JS = ROOT / "dx_app" / "static" / "js" / "lab-composer.js"
GRAPH_JS = ROOT / "dx_app" / "static" / "js" / "lab-composer-graph.js"
LAB_PORTAL_JS = ROOT / "dx_app" / "static" / "js" / "lab-portal.js"
I18N_JS = ROOT / "dx_app" / "static" / "js" / "i18n.js"
COMPOSER_I18N_KEYS = {
    "Quick Start",
    "Templates",
    "Customize",
    "Undo",
    "Redo",
    "Save Output",
    "Select input asset",
    "Device ID",
    "Device ID must be a non-negative integer",
    "Plugin palette",
    "Drag a custom plugin to Preprocess or Postprocess",
    "Custom plugin",
    "Save Recipe",
    "Export Recipe",
    "Import Recipe",
    "Run Package",
    "Developer Package",
    "Reusable Recipe",
    "Export Preflight",
    "Recipe saved",
    "Recipe import failed",
    "Recipe export failed",
    "Choose a recipe JSON file",
    "Copy-out verified",
    "Plugins",
    "Validation",
    "Add custom preprocess",
    "Add custom postprocess",
    "Apply Plugin Scaffold",
    "Run Workflow",
    "Export Package",
    "Workflow validation blocked",
    "Builder",
    "Runnable Models",
    "Compatible Assets",
    "Canvas",
    "Inspector",
    "Drop model here",
    "Drop asset here",
    "Built-in Factory Component",
    "Plugin execution requires Factory integration",
    "Preprocessing is resolved by the selected model Factory.",
    "Postprocess settings",
    "No postprocess settings are available for this model.",
    "Postprocess implementation",
    "Standard postprocess",
    "C++ postprocess",
    "The core chain is fixed so the selected DX App Factory and SyncRunner remain executable.",
    "Fit view",
    "Zoom in",
    "Zoom out",
    "Validate graph",
    "Graph ready",
    "Graph blocked",
    "Missing required connection",
    "Connection is not allowed",
    "Core stages are fixed",
    "Plugin scaffold",
    "Pick a runnable model to build and run a workflow.",
}
LOCALES = ("ko", "ja", "zh-CN", "zh-TW", "es")

COMPOSER_ROUTES = (
    "/api/lab/composer/quick_start",
    "/api/lab/composer/template",
    "/api/lab/composer/customize",
    "/api/lab/composer/plugin/dry_run",
    "/api/lab/composer/plugin/apply",
    "/api/lab/composer/run",
    "/api/lab/composer/recipe/export",
    "/api/lab/composer/recipe/import",
    "/api/lab/composer/export",
)


def _composer_source():
    return COMPOSER_JS.read_text(encoding="utf-8")


def _graph_source():
    return GRAPH_JS.read_text(encoding="utf-8")


def test_lab_has_composer_card_with_quick_start_and_templates():
    html = INDEX.read_text(encoding="utf-8")
    source = _composer_source()

    assert 'data-lab-flow="composer"' in html
    assert "Quick Start" in source
    assert "Templates" in source


def test_lab_opens_composer_first_with_builder_regions():
    html = INDEX.read_text(encoding="utf-8")
    portal = LAB_PORTAL_JS.read_text(encoding="utf-8")
    source = _composer_source()

    assert html.index('id="lab-card-composer"') < html.index('id="lab-card-add-model"')
    assert "function _openComposerByDefault" in portal
    assert "await _openComposerByDefault();" in portal
    for name in ("ComposerState", "ComposerApi", "ComposerRenderer"):
        assert name in source
    for region in (
        "lab-composer-palette",
        "lab-composer-canvas",
        "lab-composer-inspector",
    ):
        assert region in source
    assert GRAPH_JS.exists()


def test_customize_is_progressive_after_initial_workflow_exists():
    source = _composer_source()

    assert "Customize" in source
    assert "currentWorkflow" in source
    assert "if (!currentWorkflow)" in source
    for node_name in ("Input", "Preprocess", "Inference", "Postprocess", "Visualize"):
        assert node_name in source


def test_workflow_preview_exposes_server_resolved_model_and_input():
    source = _composer_source()

    assert "function renderWorkflowSummary" in source
    assert "workflow.model" in source
    assert "workflow.input" in source


def test_builder_canvas_is_a_real_constrained_visual_graph():
    source = _composer_source()
    graph = _graph_source()

    assert "function renderBuilderCanvas" in source
    assert "lab-composer-canvas" in source
    assert "LabComposerGraph.create" in source
    assert "graph_layout" in source
    assert "fixedBuilderNodes" not in source
    assert "lab-composer-node-chain" not in source
    assert "graph.hidden = !currentWorkflow" not in source
    for contract in (
        "window.LabComposerGraph",
        "ComposerGraphState",
        "document.createElement('canvas')",
        "drawEdges",
        "drawPorts",
        "pointerdown",
        "pointermove",
        "wheel",
        "minimap",
        "historyIndex",
        "validateLegalEdges",
        "getLayout",
        "setWorkflow",
        "destroy",
    ):
        assert contract in graph


def test_graph_editor_is_loaded_before_composer_and_remains_dom_safe():
    html = INDEX.read_text(encoding="utf-8")
    graph = _graph_source()

    assert html.index("lab-composer-graph.js") < html.index("lab-composer.js")
    assert "innerHTML" not in graph
    assert "document.createElement" in graph
    assert ".textContent" in graph


def test_graph_editor_removes_the_fallback_resize_listener_on_destroy():
    graph = _graph_source()

    assert "window.addEventListener('resize', resize);" in graph
    assert "window.removeEventListener('resize', resize);" in graph


def test_graph_node_click_does_not_sync_layout_without_movement():
    graph = _graph_source()

    assert "moved: false" in graph
    assert "state.drag.moved = true;" in graph
    assert "state.pan.moved = true;" in graph
    assert re.search(
        r"var changed = Boolean\(\s*"
        r"\(state\.drag && state\.drag\.moved\) \|\|\s*"
        r"\(state\.pan && state\.pan\.moved\)\s*\);",
        graph,
    )


def test_builder_reuses_trusted_selection_actions_for_lists_and_drag_drop():
    source = _composer_source()

    assert "function applyModelSelection" in source
    assert "function applyAssetSelection" in source
    assert "MODEL_DRAG_MIME" in source
    assert "ASSET_DRAG_MIME" in source
    assert "model_selection" in source
    assert "input_selection" in source


def test_blocked_validation_disables_run_and_export_controls():
    source = _composer_source()

    assert 'validation.status !== "ready"' in source
    assert "runButton.disabled = blocked" in source
    assert "exportButton.disabled = blocked" in source
    assert "graphValidation.blocked" in source


def test_run_posts_only_the_server_issued_manifest_id():
    source = _composer_source()

    # Run is now async-first (progress bar) with a sync fallback; BOTH endpoints must post
    # ONLY the server-issued manifest_id — no client workflow payload smuggled in.
    assert '"/api/lab/composer/run_async"' in source
    assert '"/api/lab/composer/run"' in source
    assert re.search(
        r'request\(\s*"/api/lab/composer/run_async",\s*\{\s*manifest_id: manifestId\s*}\s*\)',
        source,
    )
    assert re.search(
        r'request\(\s*"/api/lab/composer/run",\s*\{\s*manifest_id: manifestId\s*}\s*\)',
        source,
    )
    # runWorkflow feeds only the server-issued manifest id into the progress runner
    assert "runComposerWithProgress(currentWorkflow.manifest_id)" in source
    assert "JSON.parse(runPayload)" not in source
    assert "JSON.stringify({ workflow:" not in source


def test_composer_distinguishes_model_load_errors_and_safe_package_downloads():
    source = _composer_source()

    assert "modelLoadError = true" in source
    assert "safeOutputUrl(result.download.url)" in source


def test_customize_uses_server_validated_patches_and_confirmed_plugin_scaffolds():
    source = _composer_source()

    assert "function applyCustomization" in source
    assert "function applyPluginScaffold" in source
    assert "customizationHistory" in source
    assert "Undo" in source
    assert "Redo" in source
    assert '"/api/lab/composer/customize"' in source
    assert "'/api/lab/composer/plugin/dry_run'" in source
    assert "'/api/lab/composer/plugin/apply'" in source
    assert "workflow: currentWorkflow.workflow" not in source


def test_customize_graph_inspector_keeps_plugin_actions_and_local_status():
    source = _composer_source()

    assert "lab-composer-graph-status" in _graph_source()
    assert "updateGraphActionState" in source
    assert "Add custom preprocess" in source
    assert "Add custom postprocess" in source
    assert "save_output" in source


def test_builtin_processor_inspector_uses_server_capabilities_and_persists_safe_settings():
    source = _composer_source()

    assert "processor_capabilities" in source
    assert "function processorCapabilities" in source
    assert "function appendBuiltInProcessorControls" in source
    assert "Preprocessing is resolved by the selected model Factory." in source
    assert "Postprocess settings" in source
    assert "No postprocess settings are available for this model." in source
    assert "Postprocess implementation" in source
    assert "Standard postprocess" in source
    assert "C++ postprocess" in source
    assert "implementation_options" in source
    assert "tunable_keys" in source
    assert "tunable_defaults" in source
    assert "config_overrides" in source
    assert "postprocess_implementation" in source
    assert "execution: { config_overrides:" in source
    assert "execution: { postprocess_implementation:" in source


def test_customize_supports_server_validated_model_asset_and_plugin_drag_actions():
    source = _composer_source()

    assert "model_selection" in source
    assert "input_selection" in source
    assert "loadCompatibleAssets" in source
    assert "dragstart" in source
    assert "dragover" in source
    assert "drop" in source
    assert "planPluginScaffold(stage, language)" in source


def test_recipe_and_export_controls_use_server_validated_workflow_operations():
    source = _composer_source()

    assert "function saveRecipe" in source
    assert "function exportRecipe" in source
    assert "function importRecipe" in source
    assert "function renderRecipeControls" in source
    assert "function renderExportPanel" in source
    assert "FileReader" in source
    assert "'/api/lab/composer/recipe/export'" in source
    assert "'/api/lab/composer/recipe/import'" in source
    assert "package_type: packageType" in source
    assert "manifest_id: currentWorkflow.manifest_id" in source
    assert "recipe: recipe" in source
    assert "workflow: currentWorkflow.workflow" not in source


def test_recipe_download_defers_blob_url_cleanup_until_after_click():
    source = _composer_source()

    assert "function downloadRecipe" in source
    assert "link.click();" in source
    assert "setTimeout(function () { URL.revokeObjectURL(url); }, 0);" in source


def test_recipe_import_and_package_download_validate_response_shapes():
    source = _composer_source()

    assert "recipe === null || Array.isArray(recipe)" in source
    assert "typeof result.download.name !== 'string'" in source


def test_composer_uses_dom_apis_and_text_content_without_inner_html():
    source = _composer_source()

    assert "document.createElement" in source
    assert ".textContent" in source
    assert "innerHTML" not in source


def test_composer_ui_names_every_server_composer_route():
    source = _composer_source()

    for route in COMPOSER_ROUTES:
        assert route in source


def test_all_composer_strings_have_six_locale_coverage():
    source = _composer_source() + "\n" + _graph_source()
    translations = I18N_JS.read_text(encoding="utf-8")

    for key in COMPOSER_I18N_KEYS:
        assert f"T('{key}')" in source
        match = re.search(
            rf"'{re.escape(key)}':\s*\{{(.*?)\n\s*\}}\s*(?:,|\n)",
            translations,
            re.S,
        )
        assert match, key
        entry = match.group(1)
        assert all(f"{locale}:" in entry or f"'{locale}':" in entry for locale in LOCALES), key


def test_package_type_choices_have_localized_non_english_labels():
    translations = I18N_JS.read_text(encoding="utf-8")

    for key in ("Run Package", "Developer Package", "Reusable Recipe"):
        match = re.search(
            rf"'{re.escape(key)}':\s*\{{(.*?)\n\s*\}}\s*(?:,|\n)",
            translations,
            re.S,
        )
        assert match, key
        entry = match.group(1)
        for locale in ("ko", "ja", "zh-CN", "zh-TW"):
            localized = re.search(rf"'?{re.escape(locale)}'?\s*:\s*'([^']+)'", entry)
            assert localized, f"{key}: {locale}"
            assert localized.group(1) != key, f"{key}: {locale}"

def test_runnable_model_palette_dedupes_shared_model_file():
    """A single .dxnn reachable via both an SDK example name and a registry alias
    (yolov5 / yolov5s) must appear once in the palette. Dedup is applied to the
    server model list before it becomes the palette source."""
    source = _composer_source()

    assert "function dedupeRunnableModels" in source
    assert "dedupeRunnableModels(data.filter(isRunnable))" in source
    assert "model.model_file" in source
    # keeps the config-bearing entry; server still re-resolves identity at run time
    assert "function hasConfig" in source


def test_empty_canvas_shows_actionable_start_hint():
    """Before a model is chosen the fixed chain renders greyed 'Unavailable' nodes; an
    actionable hint must tell the user the single action that starts a workflow."""
    source = _composer_source()

    assert "startHint" in source
    assert "lab-composer-start-hint" in source
    assert "if (!currentWorkflow)" in source


def test_composer_reregisters_language_change_to_retranslate():
    """Composer renders with T() at build time, so it must re-render on a language
    switch (DXI18n.applyLang cannot swap already-built text nodes)."""
    source = _composer_source()

    assert "function refreshComposerLanguage" in source
    assert "onLangChange" in source
    assert "_DX_I18N_CALLBACKS" in source


def test_result_panel_sits_directly_under_run_actions():
    """The run→result feedback loop must not require scrolling past recipe/export."""
    source = _composer_source()

    render_body = source[source.index("function render()"):]
    render_body = render_body[:render_body.index("container.appendChild(shell);")]
    assert render_body.index("renderActions(shell);") \
        < render_body.index("renderResult(shell);") \
        < render_body.index("renderRecipeControls(shell);")


def test_inspector_uses_compact_pickers_not_duplicate_full_asset_model_lists():
    """The full browseable/draggable model+asset lists live once in the palette; the
    Inspector shows compact per-node pickers so the same long list is not rendered
    twice at once. Trusted server-validated mutations are preserved."""
    source = _composer_source()

    assert "function appendInspectorAssetPicker" in source
    assert "function appendInspectorModelPicker" in source
    assert "appendInspectorAssetPicker(inspector)" in source
    assert "appendInspectorModelPicker(inspector)" in source
    # palette keeps the full draggable lists
    assert "appendAssetChoices(palette)" in source
    assert "appendModelChoices(palette)" in source
    # inspector pickers reuse the trusted mutations, not raw workflow payloads
    assert "applyAssetSelection(select.value)" in source
    assert "applyModelSelection(model)" in source


def test_asset_picker_renders_lazy_thumbnails_dom_safely():
    """The Compatible Assets palette shows image thumbnails so users pick inputs visually,
    not by filename. Previews are server-downscaled (via /api/asset-thumb) rather than the
    full-res original, path-encoded, lazy-loaded, DOM-safe, and fall back to the filename
    caption for non-image or missing files."""
    source = _composer_source()

    assert "function appendAssetThumbnail" in source
    assert "function isImageAssetPath" in source
    assert "lab-composer-asset-grid" in source
    # downscaled preview endpoint, path safely encoded into the query string
    assert "/api/asset-thumb?w=160&f=' + encodeURIComponent(path)" in source
    assert "img.loading = 'lazy'" in source
    assert "document.createElement('img')" in source
    assert "img.style.display = 'none'" in source  # graceful fallback on load error
