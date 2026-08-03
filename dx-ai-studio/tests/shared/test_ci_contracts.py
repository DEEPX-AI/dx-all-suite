"""CI runner contracts — align with dx_app run_tc.sh / self-hosted gate."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BROWSER_SUITE_PATHS = {
    "tests/i18n_audit/test_browser_copy_audit.py",
    "tests/launcher/test_sdk_library_module_nav_browser.py",
    "tests/shared/test_browser_runtime.py",
    "tests/test_iframe_lang_sync_browser.py",
    "tests/test_tutorial_e2e_journey.py",
    "tests/test_tutorial_spotlight_spot_check.py",
    "tests/test_ux_visual_gate.py",
    "tests/test_zoom_full_audit.py",
    "tests/test_zoom_layout_contracts.py",
    "tests/test_zoom_modal_audit.py",
}


def test_run_ci_script_exists_and_executable():
    script = ROOT / "scripts" / "run_ci.sh"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    assert "tests/launcher/" in text
    assert "tests/dx_agent_dev/" in text
    assert "i18n_audit_gate.sh" in text


def test_release_ver_matches_studio_version_ssot():
    release_ver = (ROOT / "release.ver").read_text(encoding="utf-8").strip()
    studio_js = (ROOT / "shared" / "static" / "studio-version.js").read_text(encoding="utf-8")
    assert release_ver.startswith("v")
    semver = release_ver.lstrip("v")
    assert f"semver: '{semver}'" in studio_js


def test_ci_workflow_uses_self_hosted_runner():
    workflow = (
        ROOT.parent / ".github" / "workflows" / "dx-ai-studio-pytest.yml"
    ).read_text(encoding="utf-8")
    assert "self-hosted" in workflow
    assert "run_ci.sh" in workflow
    assert "ubuntu-latest" not in workflow
    assert "ci-browser-smoke" not in workflow


def test_i18n_smoke_workflow_is_manual_dispatch_only():
    workflow = (
        ROOT.parent / ".github" / "workflows" / "dx-ai-studio-i18n-audit.yml"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "pull_request:" not in workflow


def test_run_ci_excludes_browser_tests_from_default_gate():
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    assert "BROWSER_TESTS=(" in script
    missing = sorted(path for path in BROWSER_SUITE_PATHS if path not in script)
    assert not missing, f"Browser suite inventory is incomplete: {missing}"
    assert '"${IGNORE_BROWSER[@]}"' in script
    assert 'RUN_BROWSER=1' in script or "--browser" in script


def test_run_ci_prefilters_explicit_root_browser_paths():
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    stage_five = script.split('== 5/6 Module + shared + root contract suites (no browser) ==', 1)[1]

    assert "ROOT_TESTS=()" in script
    assert "for _root_test in tests/test_*.py; do" in script
    assert 'if [[ "$_root_test" == "$_bt" ]]; then' in script
    assert '"${ROOT_TESTS[@]}"' in stage_five
    assert "tests/test_*.py" not in stage_five


def test_run_ci_runs_browser_suites_in_isolated_pytest_processes():
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    assert 'for _bt in "${BROWSER_TESTS[@]}"; do' in script
    assert '"$PY" -m pytest "$_bt" -q --tb=short' in script


def test_i18n_browser_audit_uses_test_interpreter_without_forced_browser_download():
    script = (ROOT / "scripts" / "i18n_browser_audit.sh").read_text(encoding="utf-8")
    assert '"$VENV_PYTHON" -c "import playwright"' in script
    assert "playwright install chromium" not in script


def test_ci_dependency_manifest_covers_collection_dependencies():
    manifest = ROOT / "requirements-ci.txt"
    assert manifest.is_file()

    package_names = {
        line.split(";", 1)[0].split("[", 1)[0]
        .split("<", 1)[0].split(">", 1)[0].split("=", 1)[0]
        .strip().lower()
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert {
        "pytest", "numpy", "onnx", "pillow", "playwright", "jinja2", "cffi"
    } <= package_names
