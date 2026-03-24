# SPDX-License-Identifier: Apache-2.0
"""
Agentic E2E Test: dx-runtime Scenario #2 — Route to dx_app AND dx_stream

Runs Copilot CLI inside dx-runtime/ with a prompt that requires BOTH a
standalone detection app (dx_app routing) and a real-time streaming pipeline
(dx_stream routing).  The dx-runtime router should classify the request,
decompose it into two sub-tasks, and route each to the appropriate sub-agent.

This scenario is distinct from:
- dx_app scenario: directly builds inside dx_app/ (no router involved)
- dx_stream scenario: directly builds inside dx_stream/ (no router involved)
- suite scenario: cross-project compiler + app (different axis of integration)

Guide reference:
    dx-runtime/docs/source/agentic_development.md — Scenario 2
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
    pytest.mark.agentic_e2e_autopilot,
]

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

SCENARIO_PROMPT = (
    "Build a yolo26n standalone detection app and a real-time streaming pipeline for it"
)

# Prompt source: dx-runtime/docs/source/agentic_development.md — Scenario 2
# This prompt tests the runtime router's ability to route to BOTH dx_app
# (standalone inference app) and dx_stream (GStreamer pipeline app).


# ---------------------------------------------------------------------------
# Module-scoped fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def scenario(copilot_runner, agentic_e2e_artifacts_dir) -> ScenarioResult:
    """Execute dx-runtime Scenario #2 via Copilot CLI."""
    return copilot_runner.run(
        prompt=SCENARIO_PROMPT,
        workdir=RUNTIME_ROOT,
        scenario_key="runtime",
        session_log_dir=agentic_e2e_artifacts_dir,
        timeout=600,  # two sub-tasks: dx_app + dx_stream
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
        assert scenario.duration_seconds < 600, (
            f"Scenario took {scenario.duration_seconds:.0f}s (limit: 600s)"
        )

    def test_start_sentinel_emitted(self, scenario: ScenarioResult):
        """Agent emits [DX-AGENTIC-DEV: START] before any other text."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        verify_start_sentinel(scenario)


class TestRouting:
    """Verify that dx-runtime correctly routed to both dx_app and dx_stream."""

    def test_python_files_generated(self, scenario: ScenarioResult):
        """Python files are generated (routing produced output)."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        assert len(scenario.generated_py_files) > 0, (
            f"No .py files found — routing may have failed.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_detection_app_patterns(self, scenario: ScenarioResult):
        """Generated code contains detection/inference patterns (dx_app routing)."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
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
            pytest.skip("Copilot execution failed")
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
            pytest.skip("Copilot execution failed")
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
            "a standalone detection app.\n"
            f"Files: {[f.name for f in py_files]}"
        )
        assert found_stream, (
            "dx_stream domain not found in output — router did not produce "
            "a streaming pipeline app.\n"
            f"Files: {[f.name for f in py_files]}"
        )


class TestMandatoryArtifacts:
    """Verify mandatory deployment artifacts exist in session directory."""

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
    """Validate generated code quality."""

    def test_all_python_files_valid_syntax(self, scenario: ScenarioResult):
        """All generated .py files parse without SyntaxError."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        for py_file in scenario.generated_py_files:
            verify_python_syntax(py_file)

    def test_config_json_valid(self, scenario: ScenarioResult):
        """If config.json exists, it is valid JSON."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        config_files = [
            f for f in scenario.generated_json_files
            if f.name == "config.json"
        ]
        for config_file in config_files:
            verify_json_structure(config_file)
