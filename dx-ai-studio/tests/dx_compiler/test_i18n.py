"""Static i18n contracts for DX Compiler."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPILER = ROOT / "dx_compiler"

I18N_SOURCE_FILES = [
    COMPILER / "templates" / "index.html",
    COMPILER / "templates" / "partials" / "setup_panel.html",
    COMPILER / "templates" / "partials" / "config_wizard.html",
    COMPILER / "static" / "js" / "setup_panel.js",
    COMPILER / "static" / "js" / "viewer_panel.js",
    COMPILER / "static" / "js" / "config_wizard.js",
    COMPILER / "static" / "js" / "tutorial.js",
]

# Technical identifiers and units that should read identically across target languages.
T_KEY_ALLOWLIST = {
    "ONNX",
    "DXNN",
    "NPU",
    "DXQ-P0",
    "DXQ-P1",
    "DXQ-P2",
    "DXQ-P3",
    "DXQ-P4",
    "DXQ-P5",
    "EMA",
    "MinMax",
    "PCIe",
    "FPS",
    "SDK",
}

TARGET_LANGS = ("ko", "ja", "zh-CN", "zh-TW", "es")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def compiler_i18n_source() -> str:
    return read_text(COMPILER / "static" / "js" / "compiler-i18n.js")


def test_compiler_i18n_js_has_commas_before_spanish_entries():
    source = compiler_i18n_source()
    missing = re.findall(r"'zh-TW':\s*'(?:\\.|[^'\\])*'\s*\n\s*es:", source)
    assert not missing, missing[:5]


def dict_section() -> str:
    return compiler_i18n_source().split("window._DX_I18N_PLACEHOLDERS")[0]


def dict_keys() -> set[str]:
    return set(re.findall(r"'((?:\\.|[^'\\])+)':\s*\{", dict_section()))


def dict_entry(key: str) -> str:
    source = dict_section()
    match = re.search(rf"'{re.escape(key)}':\s*\{{(.*?)\n\s*\}},", source, re.S)
    return match.group(1) if match else ""


def t_keys(path: Path) -> set[str]:
    source = read_text(path)
    single = re.findall(r"\bT\('((?:\\.|[^'\\])+)'", source)
    double = re.findall(r'\bT\("((?:\\.|[^"\\])+)"', source)
    return set(single + double)




def test_compiler_i18n_loads_before_shared_i18n():
    html = read_text(COMPILER / "templates" / "base.html")
    assert html.index("/static/js/compiler-i18n.js") < html.index("/static/shared/i18n.js")


def test_setup_panel_uses_apply_lang_not_missing_apply():
    source = read_text(COMPILER / "static" / "js" / "setup_panel.js")
    assert "DXI18n.applyLang" in source
    assert "DXI18n.apply()" not in source




def test_compiler_t_keys_are_in_dictionary_or_allowlisted():
    keys = dict_keys()
    missing: dict[str, list[str]] = {}
    for path in I18N_SOURCE_FILES:
        unresolved = sorted(k for k in t_keys(path) if k not in keys and k not in T_KEY_ALLOWLIST)
        if unresolved:
            missing[str(path.relative_to(COMPILER))] = unresolved
    assert not missing, missing


def test_compiler_dictionary_entries_cover_target_languages():
    incomplete = {}
    for key in dict_keys():
        if key in T_KEY_ALLOWLIST:
            continue
        entry = dict_entry(key)
        missing_langs = [lang for lang in TARGET_LANGS if f"{lang}:" not in entry and f"'{lang}':" not in entry]
        if missing_langs:
            incomplete[key] = missing_langs
    assert not incomplete, incomplete


def test_config_wizard_dynamic_input_warning_uses_message_constant():
    source = read_text(COMPILER / "static" / "js" / "config_wizard.js")
    assert "DYNAMIC_INPUTS:" in source
    assert "T(MESSAGES.DYNAMIC_INPUTS)" in source
    assert not re.search(
        r"T\(['\"]Note: Automatic input detection did not fill shapes",
        source,
    )


def test_compiler_i18n_defines_placeholder_dictionary():
    source = compiler_i18n_source()
    assert "window._DX_I18N_PLACEHOLDERS" in source
    for placeholder in (
        "/path/to/model.onnx",
        "/path/to/config.json",
        "/path/to/output",
        "Search nodes / tensors...",
        "/path/to/dataset",
    ):
        assert placeholder in source




def test_compiler_dynamic_ui_registers_language_refresh_hooks():
    setup_src = read_text(COMPILER / "static" / "js" / "setup_panel.js")
    viewer_src = read_text(COMPILER / "static" / "js" / "viewer_panel.js")
    assert "DXI18n.onLangChange" in setup_src
    assert "DXI18n.onLangChange" in viewer_src
    assert "refreshLanguage" in setup_src
    assert "refreshLanguage" in viewer_src


def test_viewer_language_refresh_preserves_node_selection_type():
    source = read_text(COMPILER / "static" / "js" / "viewer_panel.js")
    start = source.index("function refreshLanguage()")
    end = source.index("if (window.DXI18n", start)
    refresh_section = source[start:end]
    assert "if (nodeSelectionMode)" in refresh_section
    node_selection_section = refresh_section[refresh_section.index("if (nodeSelectionMode)") :]
    expected_order = [
        "hideNodeSelectionUI();",
        "showNodeSelectionUI();",
        "setNodeSelectionType(nodeSelectionType);",
        "renderNodeSelectionLists();",
        "updateNodeSelectionVisuals();",
    ]
    last_pos = -1
    for needle in expected_order:
        pos = node_selection_section.find(needle)
        assert pos > last_pos, needle
        last_pos = pos


def test_viewer_language_refresh_preserves_search_match_count():
    source = read_text(COMPILER / "static" / "js" / "viewer_panel.js")
    assert re.search(r"var\s+lastSearchCount\s*=\s*null;", source)

    update_start = source.index("function updateStatusSearchCount")
    update_end = source.index("function setupExplorer", update_start)
    update_section = source[update_start:update_end]
    assert "lastSearchCount = count;" in update_section

    refresh_start = source.index("function refreshLanguage()")
    refresh_end = source.index("if (window.DXI18n", refresh_start)
    refresh_section = source[refresh_start:refresh_end]
    assert "if (lastSearchCount !== null)" in refresh_section
    assert "updateStatusSearchCount(lastSearchCount);" in refresh_section


def test_setup_action_buttons_not_selected_by_auto_i18n_selectors():
    """Setup action buttons must not be matched by _DX_I18N_SELECTORS.

    _translateEl() writes el.textContent which destroys child spans.
    Setup action buttons have .setup-action-icon/.setup-action-label spans
    and are translated manually by _setActionButton(); auto-translation
    would clobber those spans and freeze the text in one language.
    """
    source = compiler_i18n_source()
    m = re.search(r"window\._DX_I18N_SELECTORS\s*=\s*['\"](.+?)['\"]", source)
    assert m, "_DX_I18N_SELECTORS not found"
    selectors = [s.strip() for s in m.group(1).split(",")]
    # .btn-small is too broad — it matches .setup-action-btn parents
    assert ".btn-small" not in selectors, (
        "_DX_I18N_SELECTORS contains .btn-small which matches setup action buttons; "
        "use more specific selectors for non-setup .btn-small elements"
    )


def test_setup_action_buttons_preserve_icons_outside_data_i18n():
    html = read_text(COMPILER / "templates" / "partials" / "setup_panel.html")
    setup_src = read_text(COMPILER / "static" / "js" / "setup_panel.js")
    problems = []
    if "setup-action-icon" not in html and "setActionButton" not in setup_src:
        problems.append("missing icon-preserving setup action button mechanism")
    if 'id="setup-install-btn" data-i18n=' in html:
        problems.append("setup install button has whole-button data-i18n in HTML")
    if 'id="setup-download-btn" data-i18n=' in html:
        problems.append("setup download button has whole-button data-i18n in HTML")
    if re.search(r"installBtn\.setAttribute\(['\"]data-i18n['\"]", setup_src):
        problems.append("setup install button re-adds whole-button data-i18n in JS")
    if re.search(r"downloadBtn\.setAttribute\(['\"]data-i18n['\"]", setup_src):
        problems.append("setup download button re-adds whole-button data-i18n in JS")
    assert not problems, problems


def test_setup_panel_marks_success_immediately_on_complete_events():
    setup_src = read_text(COMPILER / "static" / "js" / "setup_panel.js")
    assert "_markSdkInstalled()" in setup_src
    assert "_markSamplesDownloaded()" in setup_src
    assert "installSucceeded = true;" in setup_src
    assert "downloadSucceeded = true;" in setup_src
    assert "this._markSdkInstalled();" in setup_src
    assert "this._markSamplesDownloaded();" in setup_src


def test_node_selection_unsupported_message_i18n_covers_all_languages():
    key = "Node selection is unavailable in subprocess compile mode. Compilation will continue without range selection."
    entry = dict_entry(key)
    assert entry, f"Missing dictionary entry for {key!r}"
    for lang in ("ko", "ja", "zh-CN", "zh-TW", "es"):
        assert f"{lang}:" in entry or f"'{lang}':" in entry


def test_node_selection_capability_feedback_is_wired_to_feature_check_and_sse():
    template = read_text(COMPILER / "templates" / "index.html")
    viewer = read_text(COMPILER / "static" / "js" / "viewer_panel.js")

    feature_start = template.index("fetch('/feature-check')")
    feature_end = template.index("}).catch", feature_start)
    feature_section = template[feature_start:feature_end]
    progress_start = template.index("source.addEventListener('progress'")
    progress_end = template.index("source.addEventListener('model_ready'", progress_start)
    progress_section = template[progress_start:progress_end]

    assert "ViewerPanel.applyCompilerCapabilities(data)" in feature_section
    assert "ViewerPanel.applyCompilerCapabilities(data)" in progress_section
    assert "function applyCompilerCapabilities(data)" in viewer
    assert "node_selection_unsupported_subprocess" in viewer
    assert "document.getElementById('node-selection')" in viewer
    assert "nodeSelection.disabled = true" in viewer or "nodeSelection.disabled=true" in viewer
    assert "nodeSelection.checked = false" in viewer or "nodeSelection.checked=false" in viewer




def test_checkpoint_resume_copy_removed_but_range_resume_copy_remains():
    """Checkpoint-file resume tokens must be gone; compile-range resume must stay."""
    template = read_text(COMPILER / "templates" / "index.html")
    tutorial = read_text(COMPILER / "static" / "js" / "tutorial.js")
    i18n = read_text(COMPILER / "static" / "js" / "compiler-i18n.js")

    for token in (
        "checkpoint-form",
        "ckpt_output_dir",
        "ckpt_output_name",
        "Server path to checkpoint .dxnn",
        "/compile/checkpoint",
        "Resume from Checkpoint",
    ):
        assert token not in template, f"template still contains {token!r}"
        assert token not in tutorial, f"tutorial still contains {token!r}"
        assert token not in i18n, f"i18n still contains {token!r}"

    # compile-range resume must be preserved
    assert "ns-resume-btn" in tutorial
    assert "Resume Compilation" in tutorial


def test_checkpoint_form_static_surface_removed():
    """Checkpoint form HTML section and CSS rule must be removed."""
    template = read_text(COMPILER / "templates" / "index.html")
    css = read_text(COMPILER / "static" / "css" / "style.css")

    assert "checkpoint-form" not in template
    assert "ckpt_" not in template
    assert "/compile/checkpoint" not in template
    assert ".checkpoint-form" not in css
    # compile-range resume button must still exist in viewer_panel.js
    assert "ns-resume-btn" in read_text(COMPILER / "static" / "js" / "viewer_panel.js")


def test_tutorial_advanced_card_no_checkpoint_visible_copy():
    """Advanced tutorial card description must not advertise checkpoint functionality."""
    tutorial = read_text(COMPILER / "static" / "js" / "tutorial.js")

    # Visible checkpoint terms must be absent in all locales
    for term in ("Checkpoint", "체크포인트", "チェックポイント", "检查点", "檢查點"):
        assert term not in tutorial, (
            f"tutorial.js still contains visible checkpoint term {term!r}"
        )

    # compile-range resume wording must be preserved
    assert "ns-resume-btn" in tutorial
    assert "Resume Compilation" in tutorial
