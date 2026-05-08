# SPDX-License-Identifier: Apache-2.0
"""
Agentic E2E Test (Claude Code): dx-runtime Scenario — Route to dx_app AND dx_stream

Runs the Claude Code CLI inside dx-runtime/ with a prompt that requires
BOTH a standalone detection app and a streaming pipeline.

This is the Claude Code counterpart of ``test_runtime_agentic_e2e.py`` (Copilot CLI)
and ``test_cursor_runtime_agentic_e2e.py`` (Cursor CLI).
"""

from __future__ import annotations

import pytest

from .conftest import (
    RUNTIME_ROOT,
    ScenarioResult,
    format_scenario_failure,
    verify_json_structure,
    verify_python_syntax,
    verify_start_sentinel,
)

pytestmark = [
    pytest.mark.agentic_e2e_claude_code_autopilot,
]

SCENARIO_PROMPT = (
    "Build a yolo26n standalone detection app and a real-time streaming pipeline for it"
)


@pytest.fixture(scope="module")
def scenario(claude_code_runner, claude_code_artifacts_dir) -> ScenarioResult:
    """Execute dx-runtime Scenario via Claude Code CLI."""
    return claude_code_runner.run(
        prompt=SCENARIO_PROMPT,
        workdir=RUNTIME_ROOT,
        scenario_key="runtime",
        session_log_dir=claude_code_artifacts_dir,
        timeout=900,
    )


class TestExecution:
    """Claude Code CLI execution basics."""

    def test_exit_code_zero(self, scenario: ScenarioResult):
        """Claude Code CLI exits successfully."""
        assert scenario.succeeded, format_scenario_failure(scenario)

    def test_completed_within_timeout(self, scenario: ScenarioResult):
        """Execution finishes within the configured timeout."""
        assert scenario.duration_seconds < 900, (
            f"Scenario took {scenario.duration_seconds:.0f}s (limit: 900s)"
        )

    def test_start_sentinel_emitted(self, scenario: ScenarioResult):
        """Agent emits [DX-AGENTIC-DEV: START] before any other text."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        verify_start_sentinel(scenario)


class TestRouting:
    """Verify that dx-runtime correctly routed to both dx_app and dx_stream."""

    def test_python_files_generated(self, scenario: ScenarioResult):
        """Python files are generated (routing produced output)."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        assert len(scenario.generated_py_files) > 0, (
            f"No .py files found — routing may have failed.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_detection_app_patterns(self, scenario: ScenarioResult):
        """Generated code contains detection/inference patterns (dx_app routing)."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        detection_keywords = [
            "detect", "inference", "infer", "model", "preprocess",
            "postprocess", "yolo", "bbox", "bounding",
        ]
        found = False
        for f in py_files:
            content = f.read_text(encoding="utf-8").lower()
            if any(kw in content for kw in detection_keywords):
                found = True
                break
        assert found, (
            "No detection/inference patterns found — dx_app routing may have failed.\n"
            f"Files: {[f.name for f in py_files]}"
        )

    def test_pipeline_patterns(self, scenario: ScenarioResult):
        """Generated code contains GStreamer/pipeline patterns (dx_stream routing)."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        pipeline_keywords = [
            "pipeline", "gstreamer", "gst", "dxinfer", "dxpreprocess",
            "dxosd", "dx_infer", "dx_preprocess", "dx_osd",
            "stream", "element", "rtsp", "uridecodebin",
        ]
        found = False
        for f in py_files:
            content = f.read_text(encoding="utf-8").lower()
            if any(kw in content for kw in pipeline_keywords):
                found = True
                break
        assert found, (
            "No GStreamer/pipeline patterns found — dx_stream routing may have failed.\n"
            f"Files: {[f.name for f in py_files]}"
        )

    def test_both_domains_covered(self, scenario: ScenarioResult):
        """Both dx_app (detection) and dx_stream (pipeline) outputs exist."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        app_keywords = ["detect", "inference", "infer", "factory", "runner"]
        stream_keywords = [
            "pipeline", "gstreamer", "gst", "dxinfer", "dxpreprocess",
            "stream", "element",
        ]
        found_app = False
        found_stream = False
        for f in py_files:
            content = f.read_text(encoding="utf-8").lower()
            if any(kw in content for kw in app_keywords):
                found_app = True
            if any(kw in content for kw in stream_keywords):
                found_stream = True
        assert found_app, (
            "dx_app domain not found in output — router did not produce "
            "a standalone detection app."
        )
        assert found_stream, (
            "dx_stream domain not found in output — router did not produce "
            "a streaming pipeline app."
        )


class TestCodeQuality:
    """Validate generated code quality."""

    def test_all_python_files_valid_syntax(self, scenario: ScenarioResult):
        """All generated .py files parse without SyntaxError."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        for py_file in scenario.generated_py_files:
            verify_python_syntax(py_file)

    def test_config_json_valid(self, scenario: ScenarioResult):
        """If config.json exists, it is valid JSON."""
        if not scenario.succeeded:
            pytest.skip("Claude Code execution failed")
        config_files = [
            f for f in scenario.generated_json_files
            if f.name == "config.json"
        ]
        for config_file in config_files:
            verify_json_structure(config_file)
