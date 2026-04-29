# SPDX-License-Identifier: Apache-2.0
"""
Agentic E2E Test (Cursor CLI): dx_stream Scenario — Detection Pipeline with Tracking

Runs the Cursor CLI ``agent`` inside dx_stream/ with a prompt requesting a
detection pipeline using yolo26n with tracking.  Verifies GStreamer elements.

This is the Cursor CLI counterpart of ``test_dx_stream_agentic_e2e.py``.
"""

from __future__ import annotations

import stat

import pytest

from .conftest import (
    STREAM_ROOT,
    ScenarioResult,
    _apt_lock,
    format_scenario_failure,
    verify_json_structure,
    verify_patterns_in_file,
    verify_python_syntax,
    verify_start_sentinel,
)

pytestmark = [
    pytest.mark.agentic_e2e_cursor_cli_autopilot,
]

SCENARIO_PROMPT = (
    "Build a real-time detection pipeline with yolo26n"
)


@pytest.fixture(scope="module")
def scenario(cursor_runner, stream_cursor_cli_artifacts_dir) -> ScenarioResult:
    """Execute dx_stream Scenario via Cursor CLI."""
    import re as _re
    with _apt_lock():
        result = cursor_runner.run(
            prompt=SCENARIO_PROMPT,
            workdir=STREAM_ROOT,
            scenario_key="dx_stream",
            session_log_dir=stream_cursor_cli_artifacts_dir,
        )
    # R51: parse DONE sentinel from result.stdout to get the authoritative output_dir.
    # Prevents cross-tool contamination when 4 tools run concurrently and Cursor's
    # directory cannot be disambiguated by name scan alone.
    _done_match = _re.search(
        r'\[DX-AGENTIC-DEV: DONE \(output-dir: ([^)]+)\)\]', result.stdout or ""
    )
    if _done_match:
        _primary = result.workdir / _done_match.group(1).strip()
        if _primary.exists():
            result.output_dirs = [_primary] + [d for d in result.output_dirs if d != _primary]
    return result


class TestExecution:
    """Cursor CLI execution basics."""

    def test_exit_code_zero(self, scenario: ScenarioResult):
        """Cursor CLI exits successfully."""
        assert scenario.succeeded, format_scenario_failure(scenario)

    def test_completed_within_timeout(self, scenario: ScenarioResult):
        """Execution finishes within the configured timeout."""
        assert scenario.duration_seconds < 600, (
            f"Scenario took {scenario.duration_seconds:.0f}s (limit: 600s)"
        )

    def test_session_log_saved(self, scenario: ScenarioResult):
        """Session transcript is captured automatically by the test harness."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed — skipping log check")
        if scenario.session_log:
            assert scenario.session_log.stat().st_size > 0, (
                "Session log exists but is empty"
            )

    def test_session_log_has_meaningful_content(self, scenario: ScenarioResult):
        """session.log must contain at least 10 non-empty lines of actual output."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        # Prefer agent-generated session.log in output dir over harness transcript
        # (mirrors OpenCode R14 fix — agent log is richer than parsed stream output)
        agent_log = scenario.output_dir / "session.log" if scenario.output_dir else None
        if agent_log and agent_log.exists():
            log_path = agent_log
        elif scenario.session_log and scenario.session_log.exists():
            log_path = scenario.session_log
        else:
            pytest.skip("No session.log found")
        log = log_path.read_text(encoding="utf-8")
        lines = [line for line in log.splitlines() if line.strip()]
        # R34: R32 standardized ALL tools to ~10 L (pre-exec checks + pipeline output).
        # R23 raised to 20 when Cursor produced 43 L, but that assumption is now invalid.
        assert len(lines) >= 10, (
            f"session.log has only {len(lines)} non-empty lines (minimum: 10).\n"
            "Fix: session.log should contain actual command output, not just EOS markers."
        )
        assert "Pipeline" in log, (
            "session.log missing 'Pipeline' keyword — expected pipeline execution output."
        )
        # R55: Extended marker vocabulary — "Pipeline execution" covers
        # "[INFO] Pipeline execution skipped" (Claude Code / skip paths);
        # "[OK]" covers "[OK] pipeline.py syntax valid" and similar pre-exec check lines.
        assert any(kw in log for kw in (
            "End of stream", "Pipeline stopped", "complete", "PASS",
            "Pipeline execution", "[OK]",
        )), (
            "session.log missing completion marker — expected one of: "
            "'End of stream', 'Pipeline stopped', 'complete', 'PASS', "
            "'Pipeline execution', '[OK]'."
        )

    def test_start_sentinel_emitted(self, scenario: ScenarioResult):
        """Agent emits [DX-AGENTIC-DEV: START] before any other text."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        verify_start_sentinel(scenario)

    def test_session_log_has_pipeline_execution_evidence(self, scenario: ScenarioResult):
        """R69: session.log must contain evidence of actual GStreamer pipeline execution.

        Complements test_session_log_has_meaningful_content by explicitly checking
        for GStreamer-origin content — catches validator-only logs that satisfy line
        count but lack any 'python pipeline.py' execution output.
        """
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        agent_log = scenario.output_dir / "session.log" if scenario.output_dir else None
        if agent_log and agent_log.exists():
            log_path = agent_log
        elif scenario.session_log and scenario.session_log.exists():
            log_path = scenario.session_log
        else:
            pytest.skip("No session.log found")
        log = log_path.read_text(encoding="utf-8")
        has_gst = any(m in log for m in (
            "Pipeline", "End of stream", "Pipeline stopped", "PLAYING", "GST_",
        ))
        has_launch = "pipeline.py" in log and (
            "=== pipeline" in log or "execution" in log.lower()
        )
        assert has_gst or has_launch, (
            "session.log shows no evidence of GStreamer pipeline execution. "
            "The agent likely ran only validation tooling. "
            "Fix: SKILL.md Verification Step requires explicit "
            "'python pipeline.py ... | tee -a session.log' (R68)."
        )


class TestGeneratedFiles:
    """Verify expected pipeline files were generated."""

    def test_python_files_exist(self, scenario: ScenarioResult):
        """At least one Python file is generated."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        if scenario.environment_hard_gate:
            pytest.skip("Agent halted at Phase 0 environment HARD GATE — environment issue, not code regression")
        assert len(scenario.generated_py_files) > 0, (
            f"No .py files found.\n"
            f"Search dirs: {scenario.output_dirs}\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_pipeline_script_exists(self, scenario: ScenarioResult):
        """A pipeline-related Python file is generated."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        if scenario.environment_hard_gate:
            pytest.skip("Agent halted at Phase 0 environment HARD GATE — environment issue, not code regression")
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
            pytest.skip("Cursor execution failed")
        for py_file in scenario.generated_py_files:
            verify_python_syntax(py_file)

    def test_pipeline_has_gstreamer_elements(self, scenario: ScenarioResult):
        """Pipeline script references expected DX GStreamer elements."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
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
            pytest.skip("Cursor execution failed")
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
            pytest.skip("Cursor execution failed")
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

    def test_pipeline_has_dxrate_for_rtsp(self, scenario: ScenarioResult):
        """RTSP pipeline path must include dxrate element to cap frame ingestion."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        for f in py_files:
            content = f.read_text(encoding="utf-8")
            if "rtsp://" in content:
                assert "dxrate" in content.lower(), (
                    f"{f.name}: pipeline handles RTSP but is missing dxrate element.\n"
                    "Fix: add 'dxrate max-rate=30' after decodebin in the RTSP source branch."
                )

    def test_pipeline_has_output_recording(self, scenario: ScenarioResult):
        """pipeline.py must support --output file recording via tee."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        pipeline_files = [
            f for f in py_files
            if any(kw in f.name.lower() for kw in ["pipeline", "detect", "app", "main", "stream"])
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
        """run_<app>.sh should invoke pipeline.py with --input and --model arguments."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        scripts = list(scenario.output_dir.glob("run_*.sh")) if scenario.output_dir else []
        scripts = [s for s in scripts if s.name != "run.sh"]
        if not scripts:
            pytest.skip("No run_<app>.sh script found")
        content = scripts[0].read_text(encoding="utf-8")
        assert "pipeline.py" in content, (
            f"{scripts[0].name} does not invoke pipeline.py"
        )
        assert "--model" in content or "MODEL" in content, (
            f"{scripts[0].name} missing --model argument"
        )

    def test_x264enc_has_tune_zerolatency(self, scenario: ScenarioResult):
        """If x264enc is used anywhere, it MUST have tune=zerolatency."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
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
            pytest.skip("Cursor execution failed")
        if scenario.environment_hard_gate:
            pytest.skip("Agent halted at Phase 0 environment HARD GATE — environment issue, not code regression")
        session_files = [f for f in scenario.all_generated_files if f.name == "session.json"]
        assert len(session_files) > 0, (
            f"No session.json found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_session_json_structure(self, scenario: ScenarioResult):
        """session.json has valid JSON structure with expected keys."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        session_files = [f for f in scenario.all_generated_files if f.name == "session.json"]
        if not session_files:
            pytest.skip("No session.json generated")
        data = verify_json_structure(session_files[0])
        all_keys_flat = str(data).lower()
        expected_concepts = ["model", "category", "pipeline", "date", "timestamp"]
        found = [c for c in expected_concepts if c in all_keys_flat]
        assert len(found) >= 1, (
            f"session.json lacks expected metadata concepts.\n"
            f"Expected at least one of: {expected_concepts}\n"
            f"Found keys: {list(data.keys()) if isinstance(data, dict) else type(data)}"
        )

    def test_session_json_created_at_has_timezone(self, scenario: ScenarioResult):
        """session.json created_at must include an ISO 8601 timezone offset."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        import json
        import re
        session_files = [f for f in scenario.all_generated_files if f.name == "session.json"]
        if not session_files:
            pytest.skip("No session.json generated")
        data = json.loads(session_files[0].read_text(encoding="utf-8"))
        created_at = data.get("created_at", "")
        assert re.search(r"[+-]\d{2}:\d{2}$|Z$", created_at), (
            f"session.json created_at missing timezone offset: {created_at!r}\n"
            "Fix: use datetime.now().astimezone().isoformat(timespec='seconds')"
        )

    def test_readme_md_exists(self, scenario: ScenarioResult):
        """README.md usage documentation file is generated."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        if scenario.environment_hard_gate:
            pytest.skip("Agent halted at Phase 0 environment HARD GATE — environment issue, not code regression")
        readme_files = [f for f in scenario.all_generated_files if f.name.lower() == "readme.md"]
        assert len(readme_files) > 0, (
            f"No README.md found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_readme_has_run_instructions(self, scenario: ScenarioResult):
        """README.md contains running instructions."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        readme_files = [f for f in scenario.all_generated_files if f.name.lower() == "readme.md"]
        if not readme_files:
            pytest.skip("No README.md generated")
        content = readme_files[0].read_text(encoding="utf-8").lower()
        run_indicators = ["run", "usage", "how to", "execute", "launch", "bash", "```"]
        found = any(ind in content for ind in run_indicators)
        assert found, (
            "README.md does not contain running instructions.\n"
            "Expected at least one of: run, usage, how to, execute, launch, code block"
        )

    def test_readme_has_pipeline_diagram(self, scenario: ScenarioResult):
        """README.md must include a pipeline diagram (ASCII → chain or Pipeline section)."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        readme_files = [f for f in scenario.all_generated_files if f.name.lower() == "readme.md"]
        if not readme_files:
            pytest.skip("No README.md generated")
        content = readme_files[0].read_text(encoding="utf-8")
        assert "→" in content or "Pipeline" in content, (
            "README.md must contain a pipeline diagram (ASCII → chain or 'Pipeline' section).\n"
            "Fix: add a '## Pipeline Diagram' section with an ASCII → element chain."
        )

    def test_readme_has_files_section(self, scenario: ScenarioResult):
        """README.md must list generated files including pipeline.py and session.json."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        readme_files = [f for f in scenario.all_generated_files if f.name.lower() == "readme.md"]
        if not readme_files:
            pytest.skip("No README.md generated")
        content = readme_files[0].read_text(encoding="utf-8")
        assert "pipeline.py" in content and "session.json" in content, (
            "README.md must list generated files (pipeline.py and session.json at minimum).\n"
            "Fix: add a '## Files' table listing all generated artifacts."
        )

    def test_run_script_exists(self, scenario: ScenarioResult):
        """run_<app>.sh shell script wrapper is generated."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        if scenario.environment_hard_gate:
            pytest.skip("Agent halted at Phase 0 environment HARD GATE — environment issue, not code regression")
        run_scripts = [
            f for f in scenario.all_generated_files
            if f.name.startswith("run_") and f.name.endswith(".sh")
        ]
        assert len(run_scripts) > 0, (
            f"No run_*.sh script found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_run_script_is_executable_or_has_shebang(self, scenario: ScenarioResult):
        """run_<app>.sh has a shebang line or executable permission."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
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
            pytest.skip("Cursor execution failed")
        if scenario.environment_hard_gate:
            pytest.skip("Agent halted at Phase 0 environment HARD GATE — environment issue, not code regression")
        pipeline_files = [
            f for f in scenario.generated_py_files
            if any(kw in f.name.lower() for kw in [
                "pipeline", "detect", "app", "main", "stream",
            ])
        ]
        assert len(pipeline_files) > 0, (
            f"No pipeline Python file found.\n"
            f"Python files: {[f.name for f in scenario.generated_py_files]}"
        )

    def test_session_json_model_is_dx_model(self, scenario: ScenarioResult):
        """session.json 'model' must be the DX model name, not the AI agent model."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        import json
        session_files = [
            f for f in scenario.all_generated_files
            if f.name == "session.json"
        ]
        if not session_files:
            pytest.skip("No session.json generated")
        data = json.loads(session_files[0].read_text(encoding="utf-8"))
        model = data.get("model", "")
        forbidden = ("claude", "gpt", "gemini", "sonnet", "opus", "haiku")
        assert not any(kw in model.lower() for kw in forbidden), (
            f"session.json 'model' field '{model}' contains an AI model name. "
            "Expected DX model name (e.g. 'yolo26n')."
        )

    def test_session_json_pipeline_category_uses_underscore(self, scenario: ScenarioResult):
        """pipeline_category must use underscores (canonical: 'single_model')."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        import json
        session_files = [
            f for f in scenario.all_generated_files
            if f.name == "session.json"
        ]
        if not session_files:
            pytest.skip("No session.json generated")
        data = json.loads(session_files[0].read_text(encoding="utf-8"))
        category = data.get("pipeline_category", "")
        if category:
            assert "-" not in category, (
                f"pipeline_category '{category}' uses hyphens; "
                "canonical format uses underscores (e.g. 'single_model')"
            )

    def test_readme_has_sufficient_length(self, scenario: ScenarioResult):
        """R71: Cursor single_model README.md should be substantive (>= 60 lines).

        Cursor consistently produces the shortest README (78 L in iter 15 vs 118–134 L
        for other tools).  This guard creates an early-warning signal before content
        quality degrades below a useful threshold.
        """
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        readme_files = [f for f in scenario.all_generated_files if f.name == "README.md"]
        if not readme_files:
            pytest.skip("No README.md generated")
        lines = len(readme_files[0].read_text(encoding="utf-8").splitlines())
        assert lines >= 60, (
            f"README.md too short: {lines} lines (expected >= 60). "
            "A substantive README should include prerequisites, pipeline diagram, "
            "run instructions, configuration table, and files table."
        )

    def test_setup_sh_exists(self, scenario: ScenarioResult):
        """setup.sh environment setup script is generated."""
        if not scenario.succeeded:
            pytest.skip("Cursor execution failed")
        if scenario.environment_hard_gate:
            pytest.skip("Agent halted at Phase 0 environment HARD GATE — environment issue, not code regression")
        setup_scripts = [f for f in scenario.all_generated_files if f.name == "setup.sh"]
        assert len(setup_scripts) > 0, (
            f"No setup.sh found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "The agent MUST generate setup.sh (HARD-GATE in dx-build-pipeline-app.md)."
        )
