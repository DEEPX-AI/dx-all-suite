# SPDX-License-Identifier: Apache-2.0
"""
Agentic E2E Test: dx_stream Scenario #2 — Build a Cascaded Detection + Classification Pipeline

Runs Copilot CLI inside dx_stream/ with a prompt requesting a cascaded pipeline
using yolo26n for primary detection and a secondary classification stage.
Verifies cascaded-specific GStreamer elements (DxRoiExtract) and pipeline_category.

R24: Expands E2E coverage beyond single_model to exercise the cascaded category.
"""

from __future__ import annotations

import os
import shutil as _shutil
import subprocess as _sp

import pytest

from .conftest import (
    DEFAULT_COPILOT_CASCADED_TIMEOUT,
    STREAM_ROOT,
    ScenarioResult,
    format_scenario_failure,
    verify_json_structure,
    verify_python_syntax,
    verify_start_sentinel,
)

# R48: module-level dxroiextract availability check — computed once at import time.
# Static checks (TestCodeQuality, TestMandatoryArtifacts) run even when the
# GStreamer plugin is absent; only runtime execution tests are guarded.
try:
    _dxroiextract_available: bool = (
        _shutil.which("gst-inspect-1.0") is not None
        and _sp.run(
            ["gst-inspect-1.0", "dxroiextract"],
            capture_output=True, timeout=15,
        ).returncode == 0
    )
except Exception:
    _dxroiextract_available = True

pytestmark = [
    pytest.mark.agentic_e2e_copilot_cli_autopilot,
]

SCENARIO_PROMPT = (
    "Build a cascaded pipeline using yolo26n for primary object detection "
    "and a secondary classification stage for detected objects"
)


@pytest.fixture(scope="module")
def scenario(copilot_runner, stream_copilot_cascaded_artifacts_dir) -> ScenarioResult:
    """Execute dx_stream cascaded Scenario via Copilot CLI."""
    import re as _re
    # R50: Copilot cascaded scenario needs a larger budget than single_model (900s vs 600s)
    # because Copilot's brainstorming pass is longer and it often retries within a session.
    result = copilot_runner.run(
        prompt=SCENARIO_PROMPT,
        workdir=STREAM_ROOT,
        scenario_key="dx_stream",
        session_log_dir=stream_copilot_cascaded_artifacts_dir,
        timeout=DEFAULT_COPILOT_CASCADED_TIMEOUT,
    )
    # R33: use DONE sentinel path as primary output_dir to prevent cross-tool
    # contamination when multiple tools create *_cascaded/ directories concurrently.
    _done_match = _re.search(
        r'\[DX-AGENTIC-DEV: DONE \(output-dir: ([^)]+)\)\]', result.stdout or ""
    )
    if _done_match:
        _primary = result.workdir / _done_match.group(1).strip()
        result.output_dirs = [_primary] if _primary.exists() else []
    else:
        # R28 fallback: filter to only directories named with "cascaded"
        result.output_dirs = [d for d in result.output_dirs if "cascaded" in d.name]
    # R63: de-duplicate when fallback resolves multiple cascaded dirs (cross-tool contamination)
    if len(result.output_dirs) > 1:
        import logging as _logging
        _logging.getLogger(__name__).warning(
            "Multiple cascaded dirs found (%d): %s — selecting most recently created",
            len(result.output_dirs), [d.name for d in result.output_dirs],
        )
        result.output_dirs = [max(result.output_dirs, key=lambda d: d.stat().st_mtime)]
    # R78: diagnostic — short cascaded sessions (<360 s) may indicate premature termination
    _MIN_CASCADED_DURATION_WARNING = 360
    if result.duration_seconds < _MIN_CASCADED_DURATION_WARNING:
        import logging as _logging
        _logging.getLogger(__name__).warning(
            "Copilot cascaded session completed in %.0f s (< %d s threshold) — "
            "session may have terminated prematurely; check artifact quality",
            result.duration_seconds, _MIN_CASCADED_DURATION_WARNING,
        )
    return result


class TestExecution:
    """Copilot CLI execution basics."""

    def test_exit_code_zero(self, scenario: ScenarioResult):
        """Copilot CLI exits successfully."""
        assert scenario.succeeded, format_scenario_failure(scenario)

    def test_completed_within_timeout(self, scenario: ScenarioResult):
        """Execution finishes within the configured timeout."""
        # R50: Copilot cascaded uses DEFAULT_COPILOT_CASCADED_TIMEOUT (900 s default);
        # +10 s tolerance for wall-clock measurement overshoot at exact timeout boundary.
        limit = DEFAULT_COPILOT_CASCADED_TIMEOUT
        assert scenario.duration_seconds < limit + 10, (
            f"Scenario took {scenario.duration_seconds:.0f}s (limit: {limit}s)"
        )

    def test_session_log_saved(self, scenario: ScenarioResult):
        """Session transcript is saved via --share."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed — skipping log check")
        if scenario.session_log:
            assert scenario.session_log.stat().st_size > 0, (
                "Session log exists but is empty"
            )

    def test_session_log_has_meaningful_content(self, scenario: ScenarioResult):
        """session.log must contain at least 10 non-empty lines of actual output."""
        if not _dxroiextract_available:
            pytest.skip("dxroiextract plugin not installed — runtime pipeline execution skipped")
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        if not scenario.session_log or not scenario.session_log.exists():
            pytest.skip("No session.log found")
        log = scenario.session_log.read_text(encoding="utf-8")
        lines = [line for line in log.splitlines() if line.strip()]
        assert len(lines) >= 10, (
            f"session.log has only {len(lines)} non-empty lines (minimum: 10).\n"
            "Fix: session.log should contain actual command output, not just EOS markers."
        )
        # R55: content pattern checks — extended marker vocabulary covers skip/ok paths.
        assert "Pipeline" in log, (
            "session.log must contain pipeline execution output (missing 'Pipeline')"
        )
        assert any(kw in log for kw in (
            "End of stream", "Pipeline stopped", "complete", "PASS",
            "Pipeline execution", "[OK]",
        )), (
            "session.log must contain a completion marker "
            "(expected: 'End of stream', 'Pipeline stopped', 'complete', 'PASS', "
            "'Pipeline execution', or '[OK]')"
        )

    def test_start_sentinel_emitted(self, scenario: ScenarioResult):
        """Agent emits [DX-AGENTIC-DEV: START] before any other text."""
        if not _dxroiextract_available:
            pytest.skip("dxroiextract plugin not installed — runtime pipeline execution skipped")
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
                "pipeline", "stream", "detect", "main", "app", "cascade",
            ])
        ]
        target = pipeline_files if pipeline_files else scenario.generated_py_files
        assert len(target) > 0, (
            f"No pipeline script found.\n"
            f"Python files: {[f.name for f in scenario.generated_py_files]}"
        )


class TestCodeQuality:
    """Validate generated cascaded pipeline code quality."""

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
        dx_elements = [
            "dxinfer", "dxpreprocess", "dxosd",
            "DxInfer", "DxPreprocess", "DxOsd",
        ]
        found_elements = False
        for f in py_files:
            content = f.read_text(encoding="utf-8")
            if any(elem in content for elem in dx_elements):
                found_elements = True
                break
        assert found_elements, (
            "No DX GStreamer elements found in generated files"
        )

    def test_pipeline_has_cascaded_roi_extract(self, scenario: ScenarioResult):
        """Cascaded pipeline must include DxRoiExtract for feeding secondary stage."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        roi_patterns = ["dxroiextract", "DxRoiExtract", "dx_roi_extract", "roi_extract"]
        found_roi = False
        for f in py_files:
            content = f.read_text(encoding="utf-8").lower()
            if any(p.lower() in content for p in roi_patterns):
                found_roi = True
                break
        assert found_roi, (
            "Cascaded pipeline missing DxRoiExtract element.\n"
            "Fix: a cascaded pipeline MUST use DxRoiExtract to crop detections "
            "for the secondary classification stage."
        )

    def test_cascaded_roi_extract_in_pipeline_string(self, scenario: ScenarioResult):
        """dxroiextract must appear as a quoted GStreamer element string, not only in comments."""
        import re as _re
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        found = False
        for f in py_files:
            content = f.read_text(encoding="utf-8")
            if _re.search(r"""['"]\s*dxroiextract\s*['"]""", content, _re.IGNORECASE):
                found = True
                break
        assert found, (
            "dxroiextract must appear as a quoted GStreamer element string in pipeline construction, "
            "not only in comments or variable names.\n"
            "Fix: the pipeline string must contain 'dxroiextract' as a literal element "
            "(e.g., '... ! dxroiextract ! ...'). A comment-only mention does not satisfy this check."
        )

    def test_pipeline_has_two_inference_stages(self, scenario: ScenarioResult):
        """Cascaded pipeline must have at least two DxInfer elements (primary + secondary)."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        for f in py_files:
            content = f.read_text(encoding="utf-8").lower()
            count = content.count("dxinfer")
            if count >= 2:
                return
        pytest.fail(
            "Cascaded pipeline should contain at least 2 DxInfer elements "
            "(one for primary detection, one for secondary classification)."
        )

    def test_pipeline_has_output_recording(self, scenario: ScenarioResult):
        """pipeline.py must support --output file recording via tee."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        pipeline_files = [
            f for f in py_files
            if any(kw in f.name.lower() for kw in ["pipeline", "detect", "app", "main", "stream", "cascade"])
        ]
        target = pipeline_files if pipeline_files else py_files
        found_recording = False
        for f in target:
            content = f.read_text(encoding="utf-8")
            if "--output" in content or "tee name=" in content:
                found_recording = True
                break
        assert found_recording, (
            "pipeline.py must implement tee-based file recording.\n"
            "Fix: add --output argument to argparse and tee name=t dual-sink code path."
        )

    def test_run_script_invokes_pipeline(self, scenario: ScenarioResult):
        """run_<app>.sh or run_cascaded.sh should invoke pipeline.py."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        scripts = list(scenario.output_dir.glob("run_*.sh")) if scenario.output_dir else []
        scripts = [s for s in scripts if s.name != "run.sh"]
        if not scripts:
            pytest.skip("No run_<app>.sh script found")
        content = scripts[0].read_text(encoding="utf-8")
        assert "pipeline.py" in content, (
            f"{scripts[0].name} does not invoke pipeline.py\n"
            "Fix: run_<app>.sh MUST delegate to 'python pipeline.py', "
            "not embed gst-launch-1.0 inline."
        )

    def test_x264enc_has_tune_zerolatency(self, scenario: ScenarioResult):
        """If x264enc is used anywhere, it MUST have tune=zerolatency."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
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

    def test_pipeline_has_dxrate_for_rtsp(self, scenario: ScenarioResult):
        """R87: Cascaded RTSP pipeline path must include dxrate element.

        Cascaded pipelines reference RTSP input — the same dxrate requirement that
        applies to single_model pipelines must be enforced here too.
        """
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        for f in py_files:
            content = f.read_text(encoding="utf-8")
            if "rtsp://" in content:
                assert "dxrate" in content.lower(), (
                    f"{f.name}: cascaded pipeline handles RTSP but is missing dxrate element.\n"
                    "Fix: add 'dxrate max-rate=30' after decodebin in the RTSP source branch."
                )


class TestMandatoryArtifacts:
    """Verify mandatory deliverable files exist in cascaded session directory."""

    def test_session_json_exists(self, scenario: ScenarioResult):
        """session.json build metadata file is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        session_files = [f for f in scenario.all_generated_files if f.name == "session.json"]
        assert len(session_files) > 0, (
            f"No session.json found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_session_json_pipeline_category_is_cascaded(self, scenario: ScenarioResult):
        """session.json pipeline_category must be 'cascaded'."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        import json
        session_files = [f for f in scenario.all_generated_files if f.name == "session.json"]
        if not session_files:
            pytest.skip("No session.json generated")
        data = json.loads(session_files[0].read_text(encoding="utf-8"))
        category = data.get("pipeline_category", "")
        assert "cascaded" in category.lower(), (
            f"session.json pipeline_category '{category}' is not 'cascaded'.\n"
            "Fix: set pipeline_category to 'cascaded' in session.json."
        )

    def test_session_json_model_is_dx_model(self, scenario: ScenarioResult):
        """session.json 'model' must be the DX model name, not the AI agent model."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        import json
        import re as _re
        session_files = [f for f in scenario.all_generated_files if f.name == "session.json"]
        if not session_files:
            pytest.skip("No session.json generated")
        data = json.loads(session_files[0].read_text(encoding="utf-8"))
        model = data.get("model", "")
        forbidden = ("claude", "gpt", "gemini", "sonnet", "opus", "haiku")
        assert not any(kw in model.lower() for kw in forbidden), (
            f"session.json 'model' field '{model}' contains an AI model name."
        )
        # R77: positive assertion — must look like a DXNN model name (alphanumeric + underscore)
        assert _re.match(r'^[A-Za-z0-9_]+$', model), (
            f"session.json 'model' field '{model}' does not look like a DXNN model name "
            "(expected alphanumeric + underscore only, e.g., 'yolo26n', 'EfficientNet_Lite0')."
        )

    def test_readme_md_exists(self, scenario: ScenarioResult):
        """README.md usage documentation file is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        readme_files = [f for f in scenario.all_generated_files if f.name.lower() == "readme.md"]
        assert len(readme_files) > 0, (
            f"No README.md found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
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
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_setup_sh_exists(self, scenario: ScenarioResult):
        """setup.sh environment setup script is generated."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        setup_scripts = [f for f in scenario.all_generated_files if f.name == "setup.sh"]
        assert len(setup_scripts) > 0, (
            f"No setup.sh found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "The agent MUST generate setup.sh (HARD-GATE in dx-build-pipeline-app.md)."
        )

    def test_session_html_export_exists(self, scenario: ScenarioResult):
        """session.html export should be present for Copilot CLI tool."""
        if scenario.output_dir is None:
            pytest.skip("No output directory detected")
        assert (scenario.output_dir / "session.html").exists(), (
            "session.html not found — tool export may have changed format or been skipped"
        )

    def test_session_id_has_agent_identifier(self, scenario: ScenarioResult):
        """R80: session.json session_id must include the agent identifier 'copilot'."""
        if not scenario.succeeded:
            pytest.skip("Copilot execution failed")
        import json
        session_files = [f for f in scenario.all_generated_files if f.name == "session.json"]
        if not session_files:
            pytest.skip("No session.json found")
        data = json.loads(session_files[0].read_text(encoding="utf-8"))
        sid = data.get("session_id", "")
        assert "copilot" in sid, (
            f"session.json session_id '{sid}' does not contain agent identifier 'copilot'.\n"
            "Fix: session_id must use format YYYYMMDD-HHMMSS_<agent>_<model>_<task> "
            "where <agent> is 'copilot'."
        )
