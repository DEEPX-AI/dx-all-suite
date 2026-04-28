# SPDX-License-Identifier: Apache-2.0
"""
Agentic E2E Test (OpenCode): dx_app Scenario — Build a Python Detection App

Runs the OpenCode CLI inside dx_app/ with a prompt that requests a
yolo26n person detection app.  Verifies that the generated code follows the
IFactory pattern with the expected file structure and content.

This is the OpenCode counterpart of ``test_dx_app_agentic_e2e.py`` (Copilot CLI)
and ``test_cursor_dx_app_agentic_e2e.py`` (Cursor CLI).
"""

from __future__ import annotations

import pytest

from .conftest import (
    APP_ROOT,
    ScenarioResult,
    format_scenario_failure,
    verify_file_tree,
    verify_json_structure,
    verify_patterns_in_file,
    verify_python_syntax,
    verify_start_sentinel,
)

pytestmark = [
    pytest.mark.agentic_e2e_opencode_cli_autopilot,
]

SCENARIO_PROMPT = (
    "Build a yolo26n detection app"
)


@pytest.fixture(scope="module")
def scenario(opencode_runner, opencode_artifacts_dir) -> ScenarioResult:
    """Execute dx_app Scenario via OpenCode CLI."""
    return opencode_runner.run(
        prompt=SCENARIO_PROMPT,
        workdir=APP_ROOT,
        scenario_key="dx_app",
        session_log_dir=opencode_artifacts_dir,
        timeout=1200,
    )


class TestExecution:
    """OpenCode CLI execution basics."""

    def test_exit_code_zero(self, scenario: ScenarioResult):
        """OpenCode CLI exits successfully."""
        assert scenario.succeeded, format_scenario_failure(scenario)

    def test_completed_within_timeout(self, scenario: ScenarioResult):
        """Execution finishes within the configured timeout."""
        assert scenario.duration_seconds < 1200, (
            f"Scenario took {scenario.duration_seconds:.0f}s (limit: 1200s)"
        )

    def test_start_sentinel_emitted(self, scenario: ScenarioResult):
        """Agent emits [DX-AGENTIC-DEV: START] before any other text."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        verify_start_sentinel(scenario)


class TestGeneratedFiles:
    """Verify that the expected files were generated."""

    def test_python_files_exist(self, scenario: ScenarioResult):
        """At least one Python file is generated."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        assert len(scenario.generated_py_files) > 0, (
            f"No .py files found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_config_json_exists(self, scenario: ScenarioResult):
        """A config.json file is generated."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        json_files = [f for f in scenario.generated_json_files if f.name == "config.json"]
        assert len(json_files) > 0, (
            f"No config.json found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_factory_file_exists(self, scenario: ScenarioResult):
        """A factory file (*_factory.py or *factory*.py) is generated."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        factory_files = [
            f for f in scenario.generated_py_files
            if "factory" in f.name.lower()
        ]
        assert len(factory_files) > 0, (
            f"No factory file found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"Python files: {[f.name for f in scenario.generated_py_files]}"
        )


class TestCodeQuality:
    """Validate generated code quality (static checks only)."""

    def test_all_python_files_valid_syntax(self, scenario: ScenarioResult):
        """All generated .py files parse without SyntaxError."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        for py_file in scenario.generated_py_files:
            verify_python_syntax(py_file)

    def test_config_json_structure(self, scenario: ScenarioResult):
        """config.json has the expected structure for a detection app."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        config_files = [f for f in scenario.generated_json_files if f.name == "config.json"]
        if not config_files:
            pytest.skip("No config.json generated")
        for config_file in config_files:
            verify_json_structure(config_file)

    def test_factory_has_required_patterns(self, scenario: ScenarioResult):
        """Factory file contains IFactory pattern elements."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        factory_files = [
            f for f in scenario.generated_py_files
            if "factory" in f.name.lower()
        ]
        if not factory_files:
            pytest.skip("No factory file generated")
        verify_patterns_in_file(
            factory_files[0],
            patterns=[
                r"class\s+\w+",
                r"def\s+\w*create\w*",
            ],
            description="IFactory pattern",
        )

    def test_runner_has_inference_patterns(self, scenario: ScenarioResult):
        """Runner/main file contains inference-related patterns."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        runner_files = [
            f for f in py_files
            if "runner" in f.name.lower() or "main" in f.name.lower()
               or "inference" in f.name.lower() or "detect" in f.name.lower()
        ]
        target_files = runner_files if runner_files else py_files
        found_inference = False
        for f in target_files:
            content = f.read_text(encoding="utf-8")
            if any(kw in content.lower() for kw in [
                "inferenceengine", "inference_engine", "infer",
                "preprocess", "postprocess", "model",
            ]):
                found_inference = True
                break
        assert found_inference, (
            f"No inference-related patterns found in generated files:\n"
            + "\n".join(f"  - {f.name}" for f in target_files)
        )
