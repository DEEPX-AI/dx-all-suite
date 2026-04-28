# SPDX-License-Identifier: Apache-2.0
"""
Agentic E2E Test: dx_stream Scenario #1 — Build a Detection Pipeline with Tracking

Runs Copilot CLI inside dx_stream/ with a prompt requesting a detection
pipeline using yolo26n with tracking on an RTSP camera.  Verifies that the
generated pipeline script contains expected GStreamer element chains.

Phase 11c+11d additions:
- TestMandatoryArtifacts: session.json, README.md, run_*.sh existence
- x264enc tune=zerolatency enforcement
- Session log saved check

Guide reference:
    dx_stream/docs/source/docs/08_DX-STREAM_Agentic_Development.md — Scenario 1
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
    pytest.mark.agentic_e2e_copilot_cli_autopilot,
]

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

SCENARIO_PROMPT = (
    "Build a real-time detection pipeline with yolo26n"
)

# Prompt source: dx-runtime/dx_stream/docs/source/docs/08_DX-STREAM_Agentic_Development.md — Scenario 1


# ---------------------------------------------------------------------------
# Module-scoped fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def scenario(copilot_runner, stream_copilot_cli_artifacts_dir) -> ScenarioResult:
    """Execute dx_stream Scenario #1 via Copilot CLI."""
    return copilot_runner.run(
        prompt=SCENARIO_PROMPT,
        workdir=STREAM_ROOT,
        scenario_key="dx_stream",
        session_log_dir=stream_copilot_cli_artifacts_dir,
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
        assert scenario.duration_seconds < 300, (
            f"Scenario took {scenario.duration_seconds:.0f}s (limit: 300s)"
        )

    def test_session_log_saved(self, scenario: ScenarioResult):
        """Session transcript is saved via --share."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed — skipping log check")
        if scenario.session_log:
            assert scenario.session_log.stat().st_size > 0, (
                "Session log exists but is empty"
            )

    def test_start_sentinel_emitted(self, scenario: ScenarioResult):
        """Agent emits [DX-AGENTIC-DEV: START] before any other text."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        verify_start_sentinel(scenario)


class TestGeneratedFiles:
    """Verify expected pipeline files were generated."""

    def test_python_files_exist(self, scenario: ScenarioResult):
        """At least one Python file is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        assert len(scenario.generated_py_files) > 0, (
            f"No .py files found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_pipeline_script_exists(self, scenario: ScenarioResult):
        """A pipeline-related Python file is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        pipeline_files = [
            f for f in scenario.generated_py_files
            if any(kw in f.name.lower() for kw in [
                "pipeline", "stream", "detect", "main", "app",
            ])
        ]
        # If no specifically named file, any .py file counts
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
            pytest.skip("Copilot execution failed")
        for py_file in scenario.generated_py_files:
            verify_python_syntax(py_file)

    def test_pipeline_has_gstreamer_elements(self, scenario: ScenarioResult):
        """Pipeline script references expected DX GStreamer elements."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")

        # At least one file should contain GStreamer / DX element references
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
            pytest.skip("Copilot execution failed")
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

    def test_pipeline_references_rtsp(self, scenario: ScenarioResult):
        """Pipeline references RTSP source or URI source element."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")

        rtsp_patterns = ["rtsp", "rtspsrc", "urisrc", "uridecodebin", "uri"]
        found_rtsp = False
        for f in py_files:
            content = f.read_text(encoding="utf-8").lower()
            if any(p in content for p in rtsp_patterns):
                found_rtsp = True
                break
        assert found_rtsp, (
            "No RTSP source reference found in generated pipeline files"
        )

    def test_x264enc_has_tune_zerolatency(self, scenario: ScenarioResult):
        """If x264enc is used anywhere, it MUST have tune=zerolatency.

        Phase 11b fix: bare x264enc (without tune=zerolatency) causes
        B-frame buffering deadlocks in GStreamer pipelines.
        """
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")

        for f in scenario.all_generated_files:
            if not f.is_file():
                continue
            # Check both .py and .sh files
            if f.suffix not in (".py", ".sh"):
                continue
            content = f.read_text(encoding="utf-8")
            # Find all x264enc occurrences
            if "x264enc" not in content:
                continue
            # x264enc is present — verify tune=zerolatency is also present
            # For Python: 'x264enc tune=zerolatency' or 'x264enc ... tune=zerolatency'
            # For shell: same patterns in gst-launch-1.0 strings
            lines_with_x264 = [
                (i + 1, line) for i, line in enumerate(content.splitlines())
                if "x264enc" in line
            ]
            for lineno, line in lines_with_x264:
                # Check if tune=zerolatency appears on the same line or
                # in the broader pipeline string context
                if "tune=zerolatency" not in line and "tune = zerolatency" not in line:
                    # Also check if tune=zerolatency appears in a nearby context
                    # (multi-line pipeline strings)
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
    """Verify mandatory deliverable files exist in session directory.

    Phase 11c: The File Creation Checklist in dx-build-pipeline-app.md
    is a MANDATORY HARD-GATE. All four files MUST be present.
    """

    def test_session_json_exists(self, scenario: ScenarioResult):
        """session.json build metadata file is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        session_files = [
            f for f in scenario.all_generated_files
            if f.name == "session.json"
        ]
        assert len(session_files) > 0, (
            f"No session.json found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "The agent MUST generate session.json (HARD-GATE in dx-build-pipeline-app.md)."
        )

    def test_session_json_structure(self, scenario: ScenarioResult):
        """session.json has valid JSON structure with expected keys."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        session_files = [
            f for f in scenario.all_generated_files
            if f.name == "session.json"
        ]
        if not session_files:
            pytest.skip("No session.json generated")
        data = verify_json_structure(session_files[0])
        # session.json should have at minimum: model, category, or pipeline_type
        all_keys_flat = str(data).lower()
        expected_concepts = ["model", "category", "pipeline", "date", "timestamp"]
        found = [c for c in expected_concepts if c in all_keys_flat]
        assert len(found) >= 1, (
            f"session.json lacks expected metadata concepts.\n"
            f"Expected at least one of: {expected_concepts}\n"
            f"Found keys: {list(data.keys()) if isinstance(data, dict) else type(data)}"
        )

    def test_readme_md_exists(self, scenario: ScenarioResult):
        """README.md usage documentation file is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        readme_files = [
            f for f in scenario.all_generated_files
            if f.name.lower() == "readme.md"
        ]
        assert len(readme_files) > 0, (
            f"No README.md found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "The agent MUST generate README.md (HARD-GATE in dx-build-pipeline-app.md)."
        )

    def test_readme_has_run_instructions(self, scenario: ScenarioResult):
        """README.md contains running instructions."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        readme_files = [
            f for f in scenario.all_generated_files
            if f.name.lower() == "readme.md"
        ]
        if not readme_files:
            pytest.skip("No README.md generated")
        content = readme_files[0].read_text(encoding="utf-8").lower()
        run_indicators = ["run", "usage", "how to", "execute", "launch", "bash", "```"]
        found = any(ind in content for ind in run_indicators)
        assert found, (
            "README.md does not contain running instructions.\n"
            "Expected at least one of: run, usage, how to, execute, launch, code block"
        )

    def test_run_script_exists(self, scenario: ScenarioResult):
        """run_<app>.sh shell script wrapper is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        run_scripts = [
            f for f in scenario.all_generated_files
            if f.name.startswith("run_") and f.name.endswith(".sh")
        ]
        assert len(run_scripts) > 0, (
            f"No run_*.sh script found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "The agent MUST generate run_<app>.sh (HARD-GATE in dx-build-pipeline-app.md)."
        )

    def test_run_script_is_executable_or_has_shebang(self, scenario: ScenarioResult):
        """run_<app>.sh has a shebang line or executable permission."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        run_scripts = [
            f for f in scenario.all_generated_files
            if f.name.startswith("run_") and f.name.endswith(".sh")
        ]
        if not run_scripts:
            pytest.skip("No run_*.sh generated")
        script = run_scripts[0]
        content = script.read_text(encoding="utf-8")
        has_shebang = content.startswith("#!/")
        import stat
        is_executable = bool(script.stat().st_mode & stat.S_IXUSR)
        assert has_shebang or is_executable, (
            f"{script.name} has no shebang and is not executable.\n"
            f"Expected #!/bin/bash or #!/usr/bin/env bash at the top."
        )

    def test_pipeline_py_exists(self, scenario: ScenarioResult):
        """pipeline.py (or equivalent main pipeline script) is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        # Accept pipeline.py or any .py file with pipeline/detection/app in name
        pipeline_files = [
            f for f in scenario.generated_py_files
            if any(kw in f.name.lower() for kw in [
                "pipeline", "detect", "app", "main", "stream",
            ])
        ]
        assert len(pipeline_files) > 0, (
            f"No pipeline Python file found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"Python files: {[f.name for f in scenario.generated_py_files]}\n"
            "The agent MUST generate pipeline.py (HARD-GATE in dx-build-pipeline-app.md)."
        )
