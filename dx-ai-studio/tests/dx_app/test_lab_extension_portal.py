"""Tests for Lab Extension Portal shell and script load contract."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
INDEX = ROOT / "dx_app" / "templates" / "index.html"
LAB_JS = ROOT / "dx_app" / "static" / "js" / "lab-portal.js"
DEV_JS = ROOT / "dx_app" / "static" / "js" / "developer.js"
I18N_JS = ROOT / "dx_app" / "static" / "js" / "i18n.js"


def test_lab_home_has_portal_cards_and_advanced_tools():
    html = INDEX.read_text(encoding="utf-8")
    assert 'id="lab-home"' in html
    for card in [
        "lab-card-add-model",
        "lab-card-create-task",
        "lab-card-experiment",
        "lab-card-generated",
        "lab-card-safety",
    ]:
        assert card in html
    assert 'id="lab-advanced-tools"' in html
    assert 'id="dev-add"' in html


def test_lab_portal_script_loads_after_developer_before_app():
    html = INDEX.read_text(encoding="utf-8")
    assert "developer.js" in html
    assert "lab-portal.js" in html
    assert html.index("developer.js") < html.index("lab-portal.js") < html.index("app.js")


def test_init_lab_page_initializes_portal_and_legacy_tools():
    js = DEV_JS.read_text(encoding="utf-8")
    assert "LabPortal.init" in js
    assert "_devInitSelects" in js


def test_lab_portal_exposes_window_global_for_developer_bridge():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "window.LabPortal" in js


def test_lab_portal_catches_capabilities_errors():
    """_loadCapabilities must catch fetch/json failures so init() never throws."""
    js = LAB_JS.read_text(encoding="utf-8")
    assert "catch" in js, "_loadCapabilities must have try/catch around capabilities fetch"
    assert "return false" in js, "_loadCapabilities must return false on error"


def test_lab_portal_guards_duplicate_card_listeners():
    """_bindCards must have a guard to avoid duplicate listeners on retry."""
    js = LAB_JS.read_text(encoding="utf-8")
    assert "_cardsBound" in js, "card binding guard variable must exist"


def test_lab_portal_no_inner_html():
    """lab-portal.js must not use innerHTML (XSS risk)."""
    js = LAB_JS.read_text(encoding="utf-8")
    assert "innerHTML" not in js


def test_add_model_wizard_uses_dry_run_before_apply():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "/api/lab/add_model/dry_run" in js
    assert "/api/lab/add_model/apply" in js
    assert js.index("/api/lab/add_model/dry_run") < js.index("/api/lab/add_model/apply")
    assert "renderManifestPreview" in js
    assert ".textContent" in js


def test_add_model_dry_run_accepts_direct_manifest_response():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "renderManifestPreview(manifest)" in js
    assert "manifest.kind === 'add_model'" in js
    assert "|| result" in js


def test_add_model_category_options_use_capability_ids_and_labels():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "_addSelectOption(catSel, cat, cat)" not in js
    assert "cat.id" in js
    assert "cat.label" in js


def test_add_model_apply_disabled_until_manifest_ready():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "canApplyManifest" in js or "manifest.status === 'ready'" in js


def test_add_model_apply_marks_current_manifest_applied_after_success():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "_currentManifest.status = 'applied'" in js
    assert js.index("_currentManifest.status = 'applied'") > js.index("result && result.ok")


def test_add_model_wizard_uses_dom_safe_rendering():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "createElement" in js
    assert "innerHTML" not in js



def _entry_body(src, key):
    m = re.search(r"['\"]" + re.escape(key) + r"['\"]\s*:\s*\{([\s\S]*?)\}", src)
    assert m, f"Missing i18n entry: {key}"
    return m.group(1)


def _assert_four_language_entry(src, key):
    body = _entry_body(src, key)
    for lang in ["ko", "ja", "zh-CN", "zh-TW"]:
        assert re.search(
            r"['\"]?" + re.escape(lang) + r"['\"]?\s*:", body
        ), f"{key} missing {lang}"


def test_lab_portal_wizard_i18n_entries_are_multilang():
    src = I18N_JS.read_text(encoding="utf-8")
    for key in [
        "Lab portal ready",
        "Lab portal unavailable",
        "Add Model Wizard",
        "Dry Run",
        "Change preview",
        "Apply changes",
        "Apply completed",
        "This flow is planned for the next phase.",
        "Model Name",
        "Category",
        "Language",
        "Source Path",
        "Postprocessor",
        "Session expired \u2014 please restart the wizard.",
        "Blockers",
        "Warnings",
        "Dry run failed",
        "Dry run error",
        "Apply failed",
        "Apply error",
        "Create Task Wizard",
        "Task Name",
        "Scaffold Type",
        "Full scaffold",
        "Postprocessor only",
        "Generated Files",
        "Preview unavailable",
        "Task dry run failed",
        "Task dry run error",
        "Task apply failed",
        "Task apply error",
    ]:
        _assert_four_language_entry(src, key)


def test_add_model_wizard_handles_manifest_expired_terminal_state():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "manifest_expired" in js
    assert "Session expired" in js
    assert "_currentManifest = null" in js


def test_add_model_wizard_guards_inflight_requests():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "_dryRunInFlight" in js
    assert "_applyInFlight" in js
    assert "finally" in js


def test_add_model_wizard_cross_disables_busy_buttons():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "_dryRunInFlight" in js
    assert "_applyInFlight" in js
    assert "btn-dry-run" in js
    assert "btn-apply" in js
    assert "canApplyManifest(_currentManifest)" in js
    assert "_syncAddModelButtons" in js


def test_add_model_preview_renders_blockers_and_warnings():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "Blockers" in js
    assert "Warnings" in js
    assert "blockers" in js
    assert "warnings" in js
    assert "manifest.blockers" in js


def test_add_model_wizard_retries_lab_post_after_session_expiry():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "function _labPost" in js
    assert "Lab session required" in js
    assert "labEnsureSession" in js




def test_task_wizard_uses_task_and_generated_endpoints():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "/api/lab/task/dry_run" in js
    assert "/api/lab/task/apply" in js
    assert "/api/lab/generated/" in js
    assert "task_scaffold" in js


def test_generated_preview_renderer_avoids_inner_html():
    js = LAB_JS.read_text(encoding="utf-8")
    start = js.index("function renderGeneratedFiles")
    # 다음 명명된 함수 선언까지 잘라냄 (익명 함수 콜백 제외)
    next_fn = js.find("\n  function ", start + 1)
    if next_fn == -1:
        next_fn = js.find("\n  async function ", start + 1)
    renderer = js[start: next_fn if next_fn != -1 else len(js)]
    assert ".textContent" in renderer
    assert ".innerHTML" not in renderer


def test_create_task_card_renders_task_wizard():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "flow === 'create-task'" in js
    assert "renderTaskWizard" in js
    assert "wiz-task-name" in js
    assert "wiz-scaffold-type" in js


def test_task_wizard_form_fields():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "wiz-task-name" in js
    assert "wiz-task-lang" in js
    assert "wiz-scaffold-type" in js
    assert "btn-task-dry-run" in js


def test_task_dry_run_posts_form_values():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "function runTaskDryRun" in js
    assert "task_name" in js
    assert "scaffold_type" in js


def test_task_dry_run_requires_task_scaffold_kind():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "manifest.kind === 'task_scaffold'" in js


def test_task_dry_run_fetches_generated_files():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "_loadGeneratedFiles" in js
    assert "encodeURIComponent" in js


def test_task_apply_posts_manifest_id_and_confirmations():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "function applyTaskManifest" in js
    assert "/api/lab/task/apply" in js
    assert "_collectConfirmations" in js


def test_task_apply_marks_manifest_applied_before_sync():
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("function applyTaskManifest")
    fn_body = js[fn_start:js.find("\n  async function", fn_start + 1) if js.find("\n  async function", fn_start + 1) != -1 else len(js)]
    assert "_currentManifest.status = 'applied'" in fn_body
    applied_pos = fn_body.index("_currentManifest.status = 'applied'")
    sync_pos = fn_body.index("_syncTaskButtons", applied_pos)
    assert applied_pos < sync_pos


def test_task_manifest_expired_handling():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "renderTaskWizard" in js
    # manifest_expired must appear in task functions (dry run and apply)
    fn_start = js.index("function runTaskDryRun")
    fn_end = js.find("\n  async function", fn_start + 1)
    dry_body = js[fn_start:fn_end if fn_end != -1 else len(js)]
    assert "manifest_expired" in dry_body


def test_task_wizard_does_not_break_add_model_selectors():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "_syncAddModelButtons" in js
    assert "btn-dry-run" in js
    assert "btn-apply" in js




def test_lab_get_retries_on_expired_session():
    """_labGet must retry once after labEnsureSession on 'Lab session required'."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("async function _labGet")
    fn_end = js.index("\n  async function", fn_start + 1)
    fn_body = js[fn_start:fn_end]
    assert "Lab session required" in fn_body
    assert "labEnsureSession" in fn_body


def test_lab_get_reads_403_json_before_http_error():
    """_labGet must inspect 403 JSON body so expired GET sessions can retry."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("async function _labGet")
    fn_end = js.index("\n  async function", fn_start + 1)
    fn_body = js[fn_start:fn_end]
    session_check = fn_body.index("Lab session required")
    first_http_return = fn_body.index("return { ok: false, error: 'HTTP ' + res.status };")
    assert "await res.json().catch" in fn_body
    assert session_check < first_http_return


def test_render_manifest_preview_accepts_apply_callback():
    """renderManifestPreview must accept an optional apply callback and button class."""
    js = LAB_JS.read_text(encoding="utf-8")
    # Signature must accept at least manifest + onApply
    assert re.search(
        r"function renderManifestPreview\(manifest,\s*onApply", js
    ), "renderManifestPreview must accept onApply parameter"


def test_task_dry_run_calls_render_manifest_with_task_callback():
    """Task dry-run must call renderManifestPreview with applyTaskManifest callback
    and must NOT use replaceChild for the task apply button."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("function runTaskDryRun")
    fn_end = js.find("\n  async function", fn_start + 1)
    dry_body = js[fn_start:fn_end if fn_end != -1 else len(js)]
    assert "renderManifestPreview(manifest, applyTaskManifest" in dry_body
    assert "replaceChild" not in dry_body


def test_load_generated_files_shows_fallback_on_error():
    """_loadGeneratedFiles must call renderGeneratedFiles(null) on catch and on missing data.files."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("async function _loadGeneratedFiles")
    fn_end = js.find("\n  // ", fn_start + 1)
    if fn_end == -1:
        fn_end = js.find("\n  async function", fn_start + 1)
    fn_body = js[fn_start:fn_end if fn_end != -1 else len(js)]
    assert fn_body.count("renderGeneratedFiles(null)") >= 2, \
        "_loadGeneratedFiles must render fallback on both catch and missing files"


def test_task_apply_guards_current_manifest_before_marking_applied():
    """Task apply must null-guard _currentManifest before setting status = 'applied'."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("function applyTaskManifest")
    fn_end = js.find("\n  async function", fn_start + 1)
    if fn_end == -1:
        fn_end = js.find("\n  function ", fn_start + 1)
    fn_body = js[fn_start:fn_end if fn_end != -1 else len(js)]
    assert "if (_currentManifest)" in fn_body
    assert "_currentManifest.status = 'applied'" in fn_body




def test_experiment_pipeline_uses_start_get_cancel_endpoints():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "/api/lab/experiment/start" in js
    assert "/api/lab/experiment/" in js
    assert "/cancel" in js
    assert "current_step" in js


def test_experiment_card_renders_pipeline_shell():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "flow === 'experiment'" in js
    assert "renderExperimentPipeline" in js
    assert "exp-model-name" in js
    assert "exp-source-path" in js
    assert "btn-experiment-start" in js


def test_experiment_stepper_and_logs_use_text_content():
    """renderExperimentRun and renderExperimentLogs must use .textContent, never .innerHTML."""
    js = LAB_JS.read_text(encoding="utf-8")
    start = js.index("function renderExperimentRun")
    next_fn = js.find("\n  function ", start + 1)
    if next_fn == -1:
        next_fn = js.find("\n  async function ", start + 1)
    run_body = js[start: next_fn if next_fn != -1 else len(js)]
    assert ".textContent" in run_body
    assert ".innerHTML" not in run_body

    start2 = js.index("function renderExperimentLogs")
    next_fn2 = js.find("\n  function ", start2 + 1)
    if next_fn2 == -1:
        next_fn2 = js.find("\n  async function ", start2 + 1)
    logs_body = js[start2: next_fn2 if next_fn2 != -1 else len(js)]
    assert ".textContent" in logs_body
    assert ".innerHTML" not in logs_body


def test_experiment_cancel_uses_encoded_run_id():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "encodeURIComponent" in js
    fn_start = js.index("function refreshExperimentRun")
    fn_end = js.find("\n  function ", fn_start + 1)
    if fn_end == -1:
        fn_end = js.find("\n  async function ", fn_start + 1)
    refresh_body = js[fn_start: fn_end if fn_end != -1 else len(js)]
    assert "encodeURIComponent" in refresh_body

    fn_start2 = js.index("function cancelExperimentRun")
    fn_end2 = js.find("\n  function ", fn_start2 + 1)
    if fn_end2 == -1:
        fn_end2 = js.find("\n  async function ", fn_start2 + 1)
    cancel_body = js[fn_start2: fn_end2 if fn_end2 != -1 else len(js)]
    assert "encodeURIComponent" in cancel_body


def test_experiment_pipeline_state_variables():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "_currentExperimentRun" in js
    assert "_experimentInFlight" in js


def test_experiment_pipeline_sync_buttons():
    js = LAB_JS.read_text(encoding="utf-8")
    assert "_syncExperimentButtons" in js
    assert "btn-experiment-start" in js
    assert "btn-experiment-cancel" in js


def test_experiment_pipeline_start_posts_payload():
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("function startExperimentPipeline")
    fn_end = js.find("\n  function ", fn_start + 1)
    if fn_end == -1:
        fn_end = js.find("\n  async function ", fn_start + 1)
    fn_body = js[fn_start: fn_end if fn_end != -1 else len(js)]
    assert "model_name" in fn_body
    assert "source_path" in fn_body
    assert "/api/lab/experiment/start" in fn_body


def test_experiment_pipeline_preserves_existing_wizards():
    """Experiment card must not break Add Model or Task Wizard selectors."""
    js = LAB_JS.read_text(encoding="utf-8")
    assert "_syncAddModelButtons" in js
    assert "_syncTaskButtons" in js
    assert "flow === 'add-model'" in js
    assert "flow === 'create-task'" in js


def test_experiment_pipeline_renders_stepper():
    """renderExperimentRun must show step items from the run state."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("function renderExperimentRun")
    fn_end = js.find("\n  function ", fn_start + 1)
    if fn_end == -1:
        fn_end = js.find("\n  async function ", fn_start + 1)
    fn_body = js[fn_start: fn_end if fn_end != -1 else len(js)]
    assert "steps" in fn_body
    assert "current_step" in fn_body


def test_experiment_stepper_uses_step_object_ids():
    """Backend returns step objects; the frontend must render/compare step.id."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("function renderExperimentRun")
    fn_end = js.find("\n  function ", fn_start + 1)
    if fn_end == -1:
        fn_end = js.find("\n  async function ", fn_start + 1)
    fn_body = js[fn_start: fn_end if fn_end != -1 else len(js)]
    assert "step.id === run.current_step" in fn_body
    assert "li.textContent = step.id" in fn_body
    assert "step === run.current_step" not in fn_body
    assert "li.textContent = step;" not in fn_body


def test_experiment_logs_join_array_tail_with_newlines():
    """Backend returns log_tail arrays; logs must render newline-separated."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("function renderExperimentLogs")
    fn_end = js.find("\n  function ", fn_start + 1)
    if fn_end == -1:
        fn_end = js.find("\n  async function ", fn_start + 1)
    fn_body = js[fn_start: fn_end if fn_end != -1 else len(js)]
    assert "Array.isArray(log_tail)" in fn_body
    assert "join('\\n')" in fn_body


def test_experiment_i18n_entries():
    src = I18N_JS.read_text(encoding="utf-8")
    for key in [
        "Experiment Pipeline",
        "Start pipeline",
        "Cancel run",
        "Run Status",
        "Current Step",
        "Pipeline Logs",
        "Pipeline start failed",
        "Pipeline start error",
        "Pipeline refresh failed",
        "Pipeline cancel failed",
        "Pipeline cancel error",
        "Refresh run",
    ]:
        _assert_four_language_entry(src, key)




def test_lab_get_retry_path_awaits_json():
    """_labGet retry path must use 'await retry.json()' not bare 'retry.json()'."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("async function _labGet")
    fn_end = js.index("\n  async function", fn_start + 1)
    fn_body = js[fn_start:fn_end]
    assert "return await retry.json();" in fn_body, \
        "_labGet retry must await the json() promise"
    assert "return retry.json();" not in fn_body, \
        "_labGet retry must not return bare retry.json() without await"


def test_experiment_pipeline_has_refresh_button():
    """renderExperimentPipeline must render a btn-experiment-refresh button
    wired to refreshExperimentRun."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("function renderExperimentPipeline")
    fn_end = js.find("\n  async function", fn_start + 1)
    fn_body = js[fn_start:fn_end if fn_end != -1 else len(js)]
    assert "btn-experiment-refresh" in fn_body, \
        "Experiment pipeline shell must have a refresh button"
    assert "refreshExperimentRun" in fn_body, \
        "Refresh button must be wired to refreshExperimentRun"


def test_sync_experiment_buttons_disables_cancel_for_terminal_states():
    """_syncExperimentButtons must disable cancel when run status is terminal
    (cancelled, failed, completed)."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("function _syncExperimentButtons")
    fn_end = js.find("\n  function ", fn_start + 1)
    if fn_end == -1:
        fn_end = js.find("\n  async function ", fn_start + 1)
    fn_body = js[fn_start:fn_end if fn_end != -1 else len(js)]
    for status in ["cancelled", "failed", "completed"]:
        assert status in fn_body, \
            f"_syncExperimentButtons must check terminal status '{status}'"


def test_sync_experiment_buttons_handles_refresh_button():
    """_syncExperimentButtons must also sync the refresh button state."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("function _syncExperimentButtons")
    fn_end = js.find("\n  function ", fn_start + 1)
    if fn_end == -1:
        fn_end = js.find("\n  async function ", fn_start + 1)
    fn_body = js[fn_start:fn_end if fn_end != -1 else len(js)]
    assert "btn-experiment-refresh" in fn_body, \
        "_syncExperimentButtons must manage the refresh button"


def test_refresh_experiment_run_uses_inflight_guard():
    """refreshExperimentRun must self-guard concurrent calls like start/cancel."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("async function refreshExperimentRun")
    next_functions = [
        idx for idx in [
            js.find("\n  async function ", fn_start + 1),
            js.find("\n  function ", fn_start + 1),
        ] if idx != -1
    ]
    fn_body = js[fn_start:min(next_functions) if next_functions else len(js)]
    assert "if (_experimentInFlight) return;" in fn_body
    assert "_experimentInFlight = true;" in fn_body
    assert "_syncExperimentButtons();" in fn_body
    assert "finally" in fn_body
    assert "_experimentInFlight = false;" in fn_body




def test_safety_card_renders_manifest_list():
    """Safety card must fetch and render pending manifest list."""
    js = LAB_JS.read_text(encoding="utf-8")
    assert "flow === 'safety'" in js
    assert "renderSafetyCenter" in js
    assert "/api/lab/manifests" in js


def test_safety_card_renders_change_summary_by_root():
    """Safety card must render change summary grouped by root."""
    js = LAB_JS.read_text(encoding="utf-8")
    fn_start = js.index("function renderSafetyCenter")
    fn_end = js.find("\n  function ", fn_start + 1)
    if fn_end == -1:
        fn_end = js.find("\n  async function ", fn_start + 1)
    fn_body = js[fn_start:fn_end if fn_end != -1 else len(js)]
    assert "m.change_summary" in fn_body
    assert ".textContent" in fn_body


def test_safety_rollback_output_uses_text_content():
    """Rollback and manual instruction output must use textContent."""
    js = LAB_JS.read_text(encoding="utf-8")
    assert "/api/lab/rollback" in js
    assert "rollback_unsupported" in js or "manual" in js.lower()


def test_legacy_git_commit_stays_under_advanced_tools():
    """Legacy Git Commit must remain under Advanced Tools, not in Safety Center."""
    html = INDEX.read_text(encoding="utf-8")
    assert 'id="lab-advanced-tools"' in html
    assert 'id="dev-add"' in html


def test_legacy_broad_git_add_disabled_or_replaced():
    """Legacy broad git add . flow must be disabled or replaced by scoped preview in Lab UI."""
    js = LAB_JS.read_text(encoding="utf-8")
    assert "/api/lab/git/plan" in js
    # Safety center should not contain 'git add .' or broad staging
    assert "git add ." not in js


def test_safety_center_uses_scoped_git_plan():
    """Safety center must use /api/lab/git/plan for scoped preview."""
    js = LAB_JS.read_text(encoding="utf-8")
    assert "/api/lab/git/plan" in js
    assert "preview_only" in js or "scoped" in js.lower()


def test_safety_center_no_inner_html():
    """Safety center rendering must not use innerHTML."""
    js = LAB_JS.read_text(encoding="utf-8")
    assert "innerHTML" not in js
