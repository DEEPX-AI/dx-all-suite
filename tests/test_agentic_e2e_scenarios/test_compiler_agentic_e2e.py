# SPDX-License-Identifier: Apache-2.0
"""
Agentic E2E Test: dx-compiler Scenario #2 — Download + Compile Model to DXNN

Runs Copilot CLI inside dx-compiler/ with a prompt requesting end-to-end
compilation of a yolo26n model to DXNN format.  The agent is expected to:
1. Download the model (ONNX or PT → ONNX export)
2. Generate a compilation config.json
3. Actually compile the model to produce a .dxnn file

Mode behaviour:
- autopilot: --no-ask-user flag skips brainstorming, fully autonomous
- manual: follows brainstorming workflow, then download + compile (shell-based)

Guide reference:
    dx-compiler/source/docs/05_DX-COMPILER_Agentic_Development.md — Scenario 2
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
    pytest.mark.agentic_e2e_copilot_cli_autopilot,
]

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

SCENARIO_PROMPT = (
    "Compile yolo26n model to dxnn"
)

# Prompt source: dx-compiler/source/docs/05_DX-COMPILER_Agentic_Development.md — Scenario 2
# The --no-ask-user CLI flag ensures fully autonomous execution (no brainstorming).
# Manual mode uses the same base prompt via test.sh (shell-based, copilot -i).


# ---------------------------------------------------------------------------
# Module-scoped fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def scenario(copilot_runner, copilot_cli_artifacts_dir) -> ScenarioResult:
    """Execute dx-compiler Scenario #2 via Copilot CLI."""
    return copilot_runner.run(
        prompt=SCENARIO_PROMPT,
        workdir=COMPILER_ROOT,
        scenario_key="compiler",
        session_log_dir=copilot_cli_artifacts_dir,
        timeout=1200,  # download + compilation may take longer
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestExecution:
    """Copilot CLI execution basics."""

    def test_exit_code_zero(self, scenario: ScenarioResult):
        """Copilot CLI exits successfully."""
        assert scenario.succeeded, format_scenario_failure(scenario)

    def test_completed_within_timeout(self, scenario: ScenarioResult):
        """Execution finishes within the configured timeout."""
        assert scenario.duration_seconds < 1200, (
            f"Scenario took {scenario.duration_seconds:.0f}s (limit: 1200s)"
        )

    def test_start_sentinel_emitted(self, scenario: ScenarioResult):
        """Agent emits [DX-AGENTIC-DEV: START] before any other text."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        verify_start_sentinel(scenario)


class TestGeneratedFiles:
    """Verify expected compilation artifacts were generated."""

    def test_config_json_exists(self, scenario: ScenarioResult):
        """A compilation config.json is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
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
            pytest.skip("Copilot execution failed")
        assert len(scenario.all_generated_files) > 0, (
            f"No files generated.\n"
            f"Search dirs: {scenario.output_dirs}"
        )

    def test_onnx_model_acquired(self, scenario: ScenarioResult):
        """An ONNX model file was downloaded or exported."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        onnx_files = scenario.generated_onnx_files
        # Also check for .pt files (intermediate download)
        pt_files = [
            f for f in scenario.all_generated_files
            if f.suffix in (".pt", ".pth")
        ]
        assert len(onnx_files) > 0 or len(pt_files) > 0, (
            f"No model files (.onnx, .pt, .pth) found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "The agent should download the model before compilation."
        )

    def test_dxnn_compiled(self, scenario: ScenarioResult):
        """A compiled .dxnn model file was produced."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        dxnn_files = scenario.generated_dxnn_files
        assert len(dxnn_files) > 0, (
            f"No .dxnn files found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "The agent should compile the model to produce a .dxnn file."
        )


class TestMandatoryArtifacts:
    """Verify mandatory deployment artifacts exist in session directory."""

    def test_setup_sh_exists(self, scenario: ScenarioResult):
        """setup.sh environment setup script is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        setup_files = [
            f for f in scenario.all_generated_files
            if f.name == "setup.sh"
        ]
        assert len(setup_files) > 0, (
            f"No setup.sh found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "The agent MUST generate setup.sh for environment setup."
        )

    def test_run_sh_exists(self, scenario: ScenarioResult):
        """run.sh inference launcher script is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        run_files = [
            f for f in scenario.all_generated_files
            if f.name == "run.sh"
        ]
        assert len(run_files) > 0, (
            f"No run.sh found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "The agent MUST generate run.sh as a one-command inference launcher."
        )

    def test_verify_py_exists(self, scenario: ScenarioResult):
        """verify.py ONNX vs DXNN comparison script is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        verify_files = [
            f for f in scenario.all_generated_files
            if f.name == "verify.py"
        ]
        assert len(verify_files) > 0, (
            f"No verify.py found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "The agent MUST generate verify.py for ONNX vs DXNN verification."
        )

    def test_session_log_exists(self, scenario: ScenarioResult):
        """session.log with actual command output is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        log_files = [
            f for f in scenario.all_generated_files
            if f.name == "session.log"
        ]
        assert len(log_files) > 0, (
            f"No session.log found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "The agent MUST capture actual command output to session.log."
        )


class TestCodeQuality:
    """Validate generated compilation artifacts."""

    def test_config_json_has_compilation_keys(self, scenario: ScenarioResult):
        """config.json contains compilation-related keys."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        config_files = [
            f for f in scenario.generated_json_files
            if f.name == "config.json"
        ]
        if not config_files:
            pytest.skip("No config.json generated")

        data = verify_json_structure(config_files[0])
        # Compilation config should have model-related keys
        # (exact schema depends on DX-COM, but common keys include these)
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
            pytest.skip("Copilot execution failed")
        for py_file in scenario.generated_py_files:
            verify_python_syntax(py_file)

    def test_compilation_script_references_dxcom(self, scenario: ScenarioResult):
        """If a compilation script is generated, it references DX-COM."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
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
