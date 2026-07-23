"""CI runner contracts — align with dx_app run_tc.sh / self-hosted gate."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


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
    assert "test_iframe_lang_sync_browser.py" in script
    assert 'RUN_BROWSER=1' in script or "--browser" in script
