# SPDX-License-Identifier: Apache-2.0
"""
Agentic E2E Test (Claude Code): dx_stream Scenario — Detection Pipeline with Tracking

Runs the Claude Code CLI inside dx_stream/ with a prompt requesting a
detection pipeline using yolo26n with tracking.  Verifies GStreamer elements.

This is the Claude Code counterpart of ``test_dx_stream_agentic_e2e.py`` (Copilot CLI)
and ``test_cursor_dx_stream_agentic_e2e.py`` (Cursor CLI).
"""

from __future__ import annotations

import pytest

from .conftest import (
    STREAM_ROOT,
    ScenarioResult,
    format_scenario_failure,
    verify_json_structure,
    verify_patterns_in_file,
    verify_python_syntax,
    verify_start_sentinel,
)

pytestmark = [
    pytest.mark.agentic_e2e_claude_code_autopilot,
]

SCENARIO_PROMPT = (
    "Build a real-time detection pipeline with yolo26n"
)


@pytest.fixture(scope="module")
def scenario(claude_code_runner, stream_claude_code_artifacts_dir) -> ScenarioResult:
    """Execute dx_stream Scenario via Claude Code CLI."""
    return claude_code_runner.run(
        prompt=SCENARIO_PROMPT,
        workdir=STREAM_ROOT,
        scenario_key="dx_stream",
        session_log_dir=stream_claude_code_artifacts_dir,
    )


class TestExecution:
    """Claude Code CLI execution basics."""

    def test_exit_code_zero(self, scenario: ScenarioResult):
        """Claude Code CLI exits successfully."""
        assert scenario.succeeded, format_scenario_failure(scenario)

    def test_completed_within_timeout(self, scenario: ScenarioResult):
        """Execution finishes within the configured timeout."""
        assert scenario.duration_seconds < 600, (
            f"Scenario took {scenario.duration_seconds:.0f}s (limit: 600s)"
        )

    def test_start_sentinel_emitted(self, scenario: ScenarioResult):
        """Agent emits [DX-AGENTIC-DEV: START] before any other text."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        verify_start_sentinel(scenario)


class TestGeneratedFiles:
    """Verify expected pipeline files were generated."""

    def test_python_files_exist(self, scenario: ScenarioResult):
        """At least one Python file is generated."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        assert len(scenario.generated_py_files) > 0, (
            f"No .py files found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_pipeline_script_exists(self, scenario: ScenarioResult):
        """A pipeline-related Python file is generated."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        pipeline_files = [
            f for f in scenario.generated_py_files
            if any(kw in f.name.lower() for kw in [
                "pipeline", "stream", "detect", "main", "app",
            ])
        ]
        target = pipeline_files if pipeline_files else scenario.generated_py_files
        assert len(target) > 0, (
            f"No pipeline script found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"Python files: {[f.name for f in scenario.generated_py_files]}"
        )


class TestCodeQuality:
    """Validate generated pipeline code quality."""

    def test_all_python_files_valid_syntax(self, scenario: ScenarioResult):
        """All generated .py files parse without SyntaxError."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        for py_file in scenario.generated_py_files:
            verify_python_syntax(py_file)

    def test_pipeline_has_gstreamer_elements(self, scenario: ScenarioResult):
        """Pipeline script references expected DX GStreamer elements."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        dx_elements = [
            "dxinfer", "dxpreprocess", "dxosd", "dxtracker",
            "DxInfer", "DxPreprocess", "DxOsd", "DxTracker",
            "dx_infer", "dx_preprocess", "dx_osd", "dx_tracker",
        ]
        found_elements = False
        for f in py_files:
            content = f.read_text(encoding="utf-8")
            if any(elem in content for elem in dx_elements):
                found_elements = True
                break
        assert found_elements, (
            f"No DX GStreamer elements found in generated files:\n"
            + "\n".join(f"  - {f.name}" for f in py_files)
            + f"\nExpected at least one of: {dx_elements[:4]}"
        )

    def test_pipeline_has_tracking_element(self, scenario: ScenarioResult):
        """Pipeline includes a tracker element (DxTracker or equivalent)."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        tracker_patterns = ["dxtracker", "DxTracker", "dx_tracker", "tracker"]
        found_tracker = False
        for f in py_files:
            content = f.read_text(encoding="utf-8").lower()
            if any(t.lower() in content for t in tracker_patterns):
                found_tracker = True
                break
        assert found_tracker, (
            "No tracker element found in generated pipeline files"
        )

    def test_x264enc_has_tune_zerolatency(self, scenario: ScenarioResult):
        """If x264enc is used anywhere, it MUST have tune=zerolatency."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        for f in scenario.all_generated_files:
            if not f.is_file() or f.suffix not in (".py", ".sh"):
                continue
            content = f.read_text(encoding="utf-8")
            if "x264enc" not in content:
                continue
            lines_with_x264 = [
                (i + 1, line) for i, line in enumerate(content.splitlines())
                if "x264enc" in line
            ]
            for lineno, line in lines_with_x264:
                if "tune=zerolatency" not in line and "tune = zerolatency" not in line:
                    context_start = max(0, lineno - 5)
                    context_end = min(len(content.splitlines()), lineno + 5)
                    context = "\n".join(content.splitlines()[context_start:context_end])
                    if "tune=zerolatency" not in context and "tune = zerolatency" not in context:
                        pytest.fail(
                            f"{f.name}:{lineno}: x264enc used without tune=zerolatency\n"
                            f"  Line: {line.strip()}\n"
                            f"  Fix: x264enc tune=zerolatency (prevents B-frame deadlock)"
                        )


class TestMandatoryArtifacts:
    """Verify mandatory deliverable files exist in session directory."""

    def test_session_json_exists(self, scenario: ScenarioResult):
        """session.json build metadata file is generated."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        session_files = [f for f in scenario.all_generated_files if f.name == "session.json"]
        assert len(session_files) > 0, (
            f"No session.json found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_readme_md_exists(self, scenario: ScenarioResult):
        """README.md usage documentation file is generated."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        readme_files = [f for f in scenario.all_generated_files if f.name.lower() == "readme.md"]
        assert len(readme_files) > 0, (
            f"No README.md found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_run_script_exists(self, scenario: ScenarioResult):
        """run_<app>.sh shell script wrapper is generated."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        run_scripts = [
            f for f in scenario.all_generated_files
            if f.name.startswith("run_") and f.name.endswith(".sh")
        ]
        assert len(run_scripts) > 0, (
            f"No run_*.sh script found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )
