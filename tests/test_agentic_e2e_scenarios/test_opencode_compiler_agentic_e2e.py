# SPDX-License-Identifier: Apache-2.0
"""
Agentic E2E Test (OpenCode): dx-compiler Scenario — Download + Compile Model

Runs the OpenCode CLI inside dx-compiler/ with a prompt requesting
end-to-end compilation of a yolo26n model to DXNN format.

This is the OpenCode counterpart of ``test_compiler_agentic_e2e.py`` (Copilot CLI)
and ``test_cursor_compiler_agentic_e2e.py`` (Cursor CLI).
"""

from __future__ import annotations

import pytest

from .conftest import (
    COMPILER_ROOT,
    ScenarioResult,
    format_scenario_failure,
    verify_json_structure,
    verify_python_syntax,
    verify_start_sentinel,
)

pytestmark = [
    pytest.mark.agentic_e2e_opencode_cli_autopilot,
]

SCENARIO_PROMPT = (
    "Compile yolo26n model to dxnn"
)


@pytest.fixture(scope="module")
def scenario(opencode_runner, opencode_artifacts_dir) -> ScenarioResult:
    """Execute dx-compiler Scenario via OpenCode CLI."""
    return opencode_runner.run(
        prompt=SCENARIO_PROMPT,
        workdir=COMPILER_ROOT,
        scenario_key="compiler",
        session_log_dir=opencode_artifacts_dir,
        timeout=1500,
    )


class TestExecution:
    """OpenCode CLI execution basics."""

    def test_exit_code_zero(self, scenario: ScenarioResult):
        """OpenCode CLI exits successfully."""
        assert scenario.succeeded, format_scenario_failure(scenario)

    def test_completed_within_timeout(self, scenario: ScenarioResult):
        """Execution finishes within the configured timeout."""
        assert scenario.duration_seconds < 1500, (
            f"Scenario took {scenario.duration_seconds:.0f}s (limit: 1500s)"
        )

    def test_start_sentinel_emitted(self, scenario: ScenarioResult):
        """Agent emits [DX-AGENTIC-DEV: START] before any other text."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        verify_start_sentinel(scenario)


class TestGeneratedFiles:
    """Verify expected compilation artifacts were generated."""

    def test_config_json_exists(self, scenario: ScenarioResult):
        """A compilation config.json is generated."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        config_files = [
            f for f in scenario.generated_json_files
            if f.name == "config.json"
        ]
        assert len(config_files) > 0, (
            f"No config.json found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_some_files_generated(self, scenario: ScenarioResult):
        """At least one output file is generated (config or script)."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        assert len(scenario.all_generated_files) > 0, (
            f"No files generated.\n"
            f"Search dirs: {scenario.output_dirs}"
        )

    def test_onnx_model_acquired(self, scenario: ScenarioResult):
        """An ONNX model file was downloaded or exported."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        onnx_files = scenario.generated_onnx_files
        pt_files = [
            f for f in scenario.all_generated_files
            if f.suffix in (".pt", ".pth")
        ]
        assert len(onnx_files) > 0 or len(pt_files) > 0, (
            f"No model files (.onnx, .pt, .pth) found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_dxnn_compiled(self, scenario: ScenarioResult):
        """A compiled .dxnn model file was produced."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        dxnn_files = scenario.generated_dxnn_files
        assert len(dxnn_files) > 0, (
            f"No .dxnn files found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )


class TestMandatoryArtifacts:
    """Verify mandatory deployment artifacts exist in session directory."""

    def test_setup_sh_exists(self, scenario: ScenarioResult):
        """setup.sh environment setup script is generated."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        setup_files = [f for f in scenario.all_generated_files if f.name == "setup.sh"]
        assert len(setup_files) > 0, (
            f"No setup.sh found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_run_sh_exists(self, scenario: ScenarioResult):
        """run.sh inference launcher script is generated."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        run_files = [f for f in scenario.all_generated_files if f.name == "run.sh"]
        assert len(run_files) > 0, (
            f"No run.sh found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_verify_py_exists(self, scenario: ScenarioResult):
        """verify.py ONNX vs DXNN comparison script is generated."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        verify_files = [f for f in scenario.all_generated_files if f.name == "verify.py"]
        assert len(verify_files) > 0, (
            f"No verify.py found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_session_log_exists(self, scenario: ScenarioResult):
        """session.log with actual command output is generated."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        log_files = [f for f in scenario.all_generated_files if f.name == "session.log"]
        assert len(log_files) > 0, (
            f"No session.log found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )


class TestCodeQuality:
    """Validate generated compilation artifacts."""

    def test_config_json_has_compilation_keys(self, scenario: ScenarioResult):
        """config.json contains compilation-related keys."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        config_files = [
            f for f in scenario.generated_json_files
            if f.name == "config.json"
        ]
        if not config_files:
            pytest.skip("No config.json generated")
        data = verify_json_structure(config_files[0])
        all_keys_flat = str(data).lower()
        expected_concepts = ["input", "model", "onnx"]
        found = [c for c in expected_concepts if c in all_keys_flat]
        assert len(found) >= 1, (
            f"config.json lacks expected compilation concepts.\n"
            f"Expected at least one of: {expected_concepts}\n"
            f"Found keys: {list(data.keys()) if isinstance(data, dict) else type(data)}"
        )

    def test_python_scripts_valid_syntax(self, scenario: ScenarioResult):
        """Any generated Python scripts have valid syntax."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        for py_file in scenario.generated_py_files:
            verify_python_syntax(py_file)

    def test_compilation_script_references_dxcom(self, scenario: ScenarioResult):
        """If a compilation script is generated, it references DX-COM."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python scripts generated (config-only is acceptable)")
        dxcom_patterns = [
            "dx-com", "dxcom", "dx_com", "DX-COM", "DXCOM",
            "compile", "compiler", "onnx",
        ]
        found = False
        for f in py_files:
            content = f.read_text(encoding="utf-8").lower()
            if any(p.lower() in content for p in dxcom_patterns):
                found = True
                break
        assert found, (
            "No DX-COM or compilation references in generated scripts:\n"
            + "\n".join(f"  - {f.name}" for f in py_files)
        )
