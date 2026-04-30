# SPDX-License-Identifier: Apache-2.0
"""
Agentic E2E Test (OpenCode): dx-all-suite Scenario — Cross-Project Compile + App

Runs the OpenCode CLI at the suite root with a cross-project prompt
requiring both dx-compiler and dx_app.

This is the OpenCode counterpart of ``test_suite_agentic_e2e.py`` (Copilot CLI)
and ``test_cursor_suite_agentic_e2e.py`` (Cursor CLI).
"""

from __future__ import annotations

import pytest

from .conftest import (
    SUITE_ROOT,
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
    "Compile yolo26n and build an inference app"
)

SUITE_TIMEOUT = 3600  # REC-6: increased from 3000s — opencode needs 60 min budget to survive multiple compilation retries (3 attempts in iter-10 consumed 47 min)
GRACE_PERIOD = 10     # R18-parity: OS scheduling jitter allowance


@pytest.fixture(scope="module")
def scenario(opencode_runner, opencode_artifacts_dir) -> ScenarioResult:
    """Execute suite Scenario via OpenCode CLI."""
    return opencode_runner.run(
        prompt=SCENARIO_PROMPT,
        workdir=SUITE_ROOT,
        scenario_key="suite",
        session_log_dir=opencode_artifacts_dir,
        timeout=SUITE_TIMEOUT,
    )


class TestExecution:
    def test_exit_code_zero(self, scenario: ScenarioResult):
        """OpenCode CLI exits successfully."""
        assert scenario.succeeded, format_scenario_failure(scenario)

    def test_completed_within_timeout(self, scenario: ScenarioResult):
        """Execution finishes within the extended timeout."""
        assert scenario.duration_seconds < SUITE_TIMEOUT + GRACE_PERIOD, (
            f"Scenario took {scenario.duration_seconds:.0f}s "
            f"(limit: {SUITE_TIMEOUT}s + {GRACE_PERIOD}s grace = {SUITE_TIMEOUT + GRACE_PERIOD}s)"
        )

    def test_start_sentinel_emitted(self, scenario: ScenarioResult):
        """Agent emits [DX-AGENTIC-DEV: START] before any other text."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        verify_start_sentinel(scenario)


class TestCrossProjectOutput:
    """Verify that both compiler and app artifacts were generated."""

    def test_files_generated(self, scenario: ScenarioResult):
        """At least some output files are generated."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        assert len(scenario.all_generated_files) > 0, (
            f"No files generated in {scenario.output_dirs or '(no dirs detected)'}"
        )

    def test_compilation_artifacts(self, scenario: ScenarioResult):
        """Compilation-related artifacts are present (config, model, or dxnn)."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        all_files = scenario.all_generated_files
        if not all_files:
            pytest.skip("No files generated")
        compilation_indicators = []
        for f in all_files:
            name_lower = f.name.lower()
            if "config" in name_lower and f.suffix == ".json":
                compilation_indicators.append(f)
            elif any(kw in name_lower for kw in ["compile", "convert", "onnx"]):
                compilation_indicators.append(f)
            elif f.suffix in (".onnx", ".dxnn", ".pt", ".pth"):
                compilation_indicators.append(f)
        assert len(compilation_indicators) > 0, (
            f"No compilation artifacts found.\n"
            f"All files: {[f.name for f in all_files]}"
        )
        # R38: Enforce dual-session layout — compiler artifacts must be in dx-compiler/dx-agentic-dev/,
        # not merged into dx_app/dx-agentic-dev/. opencode (iter-6) produced a single-session layout.
        assert any("dx-compiler" in str(d) for d in scenario.output_dirs), (
            "No dx-compiler session found in output_dirs — compiler artifacts must be in "
            "dx-compiler/dx-agentic-dev/, not merged with app artifacts in dx_app/. "
            f"Current output_dirs: {[str(d) for d in scenario.output_dirs]}"
        )

    def test_dxnn_compiled(self, scenario: ScenarioResult):
        """A compiled .dxnn model file was produced."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        dxnn_files = scenario.generated_dxnn_files
        assert len(dxnn_files) > 0, (
            f"No .dxnn files found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_model_acquired(self, scenario: ScenarioResult):
        """A model file (.onnx, .pt, or .dxnn) was downloaded/produced."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        model_files = [
            f for f in scenario.all_generated_files
            if f.suffix in (".onnx", ".pt", ".pth", ".dxnn")
        ]
        assert len(model_files) > 0, (
            f"No model files found.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}"
        )

    def test_app_artifacts(self, scenario: ScenarioResult):
        """Application-related Python files are present."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        py_files = scenario.generated_py_files
        if not py_files:
            pytest.skip("No Python files generated")
        app_keywords = [
            "detect", "inference", "infer", "factory", "runner",
            "preprocess", "postprocess", "model",
        ]
        found_app = False
        for f in py_files:
            content = f.read_text(encoding="utf-8").lower()
            if any(kw in content for kw in app_keywords):
                found_app = True
                break
        assert found_app, (
            "No application/inference patterns found in Python files.\n"
            f"Files: {[f.name for f in py_files]}"
        )


class TestMandatoryArtifacts:
    """Verify mandatory deployment artifacts."""

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

    def test_compile_pid_exists(self, scenario: ScenarioResult):
        """compile.pid is generated in compiler session directory (REC-S2).

        REC-S2: compile.pid proves subprocess.Popen background compilation was used
        (R42 compliance). opencode produced compile.pid in iter-14.
        """
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        pid_files = [f for f in scenario.all_generated_files if f.name == "compile.pid"]
        assert len(pid_files) > 0, (
            f"No compile.pid found in compiler session.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "R42 violation: agent MUST use subprocess.Popen + compile.pid pattern "
            "(NOT synchronous dx_com.compile())."
        )

    def test_onnx_retained_in_compiler_session(self, scenario: ScenarioResult):
        """yolo26n.onnx (real binary ≥ 1 MB) is retained in compiler session dir (REC-V5).

        REC-U5 (iter-16): Added as soft UserWarning.
        REC-V5 (iter-17): Promoted to pytest.fail — checks that a real .onnx binary
            (≥ 1 MB, not just a symlink) is retained in the compiler session directory.
        """
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        compiler_dirs = set()
        for f in scenario.all_generated_files:
            if f.name == "compile.py":
                compiler_dirs.add(f.parent)
        if not compiler_dirs:
            pytest.skip("No compiler session dir found")
        real_onnx_in_compiler = [
            f for f in scenario.all_generated_files
            if f.suffix == ".onnx"
            and f.parent in compiler_dirs
            and f.resolve().stat().st_size >= 1_000_000
        ]
        if not real_onnx_in_compiler:
            pytest.fail(
                "No real .onnx file (≥ 1 MB) found in compiler session directory.\n"
                "Retaining the source .onnx makes the session self-contained and "
                "reproducible (verify.py re-runs, re-compilation without repo access).\n"
                "Use shutil.copy or cp to retain yolo26n.onnx alongside the .dxnn file.\n"
                "Symlinks do NOT satisfy this check — a real binary copy is required."
            )

    def test_session_json_exists(self, scenario: ScenarioResult):
        """session.json metadata file is generated in app session (R48/REC-T2).

        REC-T2 (iter-15): Promoted from xfail to hard assertion. opencode XPASSED in iter-15
        with REC-M cross-contamination filtering applied — opencode writes session.json natively.
        R48: opencode produces session.json natively. This test ensures behavior is not regressed.
        """
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        json_files = [f for f in scenario.all_generated_files if f.name == "session.json"]
        assert len(json_files) > 0, (
            f"No session.json found in app session.\n"
            f"All files: {[f.name for f in scenario.all_generated_files]}\n"
            "The agent MUST generate session.json with build metadata (R48)."
        )


class TestCodeQuality:
    """Validate all generated code."""

    def test_all_python_files_valid_syntax(self, scenario: ScenarioResult):
        """All generated .py files parse without SyntaxError."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        for py_file in scenario.generated_py_files:
            verify_python_syntax(py_file)

    def test_all_json_files_valid(self, scenario: ScenarioResult):
        """All generated .json files are valid JSON."""
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        for json_file in scenario.generated_json_files:
            verify_json_structure(json_file)

    def test_verify_py_inference_quality(self, scenario: ScenarioResult):
        """verify.py output shows no critical DXNN inference failure (REC-U6).

        REC-U6 (iter-16): All 4 tools showed quantization quality issues
        (cosine similarity < 0.99 or inference errors) invisible to the test suite.
        Checks session.log for DXNN inference failure indicators and emits UserWarning.
        """
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        import warnings
        session_logs = [
            f for f in scenario.all_generated_files
            if f.name == "session.log"
        ]
        failure_indicators = [
            "DXNN inference FAILED",
            "inference FAILED",
            "Input data must be np.ndarray",
        ]
        for log in session_logs:
            content = log.read_text(encoding="utf-8", errors="replace")
            found = [kw for kw in failure_indicators if kw in content]
            if found:
                warnings.warn(
                    f"DXNN inference failure indicator(s) detected in "
                    f"{log.parent.name}/session.log: {found}.\n"
                    "This indicates a verify.py bug or DXNN quantization issue.\n"
                    "Check the verify.py implementation and calibration data quality.",
                    UserWarning,
                    stacklevel=2,
                )

    def test_compile_py_avoids_slow_calibration(self, scenario: ScenarioResult):
        """compile.py uses augmentation-based DataLoader, not a 100-distinct-image strategy (REC-W1).

        REC-W1 (iter-18): Detects slow calibration strategies that cause 62-min timeouts.
        REC-F/REC-T6: Per-attempt analysis — for opencode's multi-attempt pattern,
        intermediate failed attempts (no .dxnn in same dir) emit UserWarning only;
        hard fail only for the attempt that produced .dxnn with > 600s duration.
        """
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        import warnings
        banned_classes = [
            "CalibDataset", "CalibrationDataset", "YoloCalibDataset",
            "YOLOCalibDataset", "ImageFolder", "DefaultDataset",
        ]
        compile_scripts = [
            f for f in scenario.all_generated_files
            if f.name in ("compile.py", "compile_model.py")
            and "dx-compiler" in str(f)
        ]
        for script in compile_scripts:
            content = script.read_text(encoding="utf-8", errors="replace")
            has_banned = any(name in content for name in banned_classes)
            if not has_banned:
                continue
            banned_found = [n for n in banned_classes if n in content]
            # REC-F: Per-attempt analysis — check .dxnn in script's OWN directory
            dxnn_in_dir = list(script.parent.glob("*.dxnn"))
            if not dxnn_in_dir:
                # Intermediate failed attempt — UserWarning only (not a hard fail)
                warnings.warn(
                    f"opencode attempt {script.parent.name}/{script.name} uses a banned "
                    f"calibration strategy (found: {banned_found}) and no .dxnn in same dir. "
                    "This may be an intermediate failed attempt. "
                    "Use augmentation-based DataLoader for consistent compilation performance.",
                    UserWarning,
                    stacklevel=2,
                )
            elif scenario.duration_seconds > 600:
                pytest.fail(
                    f"{script.parent.name}/{script.name} uses a banned calibration "
                    f"strategy (found: {banned_found}, duration={scenario.duration_seconds:.0f}s > 600s). "
                    ".dxnn was produced but calibration time exceeded limit — "
                    "100-distinct-image strategy (~62 min) used instead of augmentation (~1 min). "
                    "(REC-F per-attempt analysis)"
                )
            else:
                warnings.warn(
                    f"{script.parent.name}/{script.name} uses a non-compliant calibration "
                    f"strategy (found: {banned_found}) but compilation completed within timeout "
                    f"({scenario.duration_seconds:.0f}s). "
                    "Use augmentation-based DataLoader for consistent performance.",
                    UserWarning,
                    stacklevel=2,
                )

    def test_compile_self_check_ran(self, scenario: ScenarioResult):
        """Compiler session.log contains CALIB_STRATEGY_OK: marker from Rule 5 self-check (REC-W1).

        REC-W1 (iter-18): Verifies the agent ran the mandatory AST self-check in Rule 5
        (dx-dxnn-compiler.md) that confirms augmentation-based DataLoader was written.
        If CALIB_STRATEGY_OK is absent, the agent skipped the mandatory self-check.
        """
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        compiler_session_logs = [
            f for f in scenario.all_generated_files
            if f.name == "session.log" and "dx-compiler" in str(f)
        ]
        if not compiler_session_logs:
            pytest.fail(
                "No compiler session.log found in dx-compiler session directories. "
                "Cannot verify calibration self-check was executed."
            )
        for log in compiler_session_logs:
            content = log.read_text(encoding="utf-8", errors="replace")
            if "CALIB_STRATEGY_OK" not in content:
                pytest.fail(
                    f"{log.parent.name}/session.log does not contain 'CALIB_STRATEGY_OK:' marker.\n"
                    "The agent must run the Rule 5 AST self-check before subprocess.Popen:\n"
                    "  echo 'CALIB_STRATEGY_OK: augmentation-based DataLoader confirmed' >> session.log\n"
                    "See dx-dxnn-compiler.md Rule 5 for the full self-check command."
                )

    @pytest.mark.xfail(
        reason=(
            "REC-V7 (iter-17): opencode uses a claude subagent which writes agent='claude', "
            "not 'opencode'. The test_session_json_exists regression in iter-17 shows this "
            "attribution gap is non-deterministic. Re-marked xfail until session.owner "
            "tracking is implemented or opencode explicitly overrides the agent field."
        ),
        strict=False,
    )
    def test_session_json_has_agent_field(self, scenario: ScenarioResult):
        """session.json contains 'agent' field attributing the session to opencode (REC-V7).

        REC-T2 (iter-15): Promoted from xfail to hard assertion.
        REC-V7 (iter-17): Re-marked as xfail — opencode subagent writes agent='claude',
            not 'opencode'. The iter-17 session.json regression (no file produced) confirms
            this attribution gap is non-deterministic. Re-evaluate once opencode explicitly
            overrides the agent field or session.owner tracking is implemented.
        """
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        session_json_files = [
            f for f in scenario.all_generated_files if f.name == "session.json"
        ]
        assert len(session_json_files) > 0, (
            "No session.json found — opencode subagent delegation does not produce "
            "session.json with agent attribution. See R21 for remediation."
        )
        import json as _json
        data = _json.loads(session_json_files[0].read_text(encoding="utf-8"))
        agent_val = data.get("agent", "") or data.get("delegated_by", "")
        assert "opencode" in str(agent_val).lower(), (
            f"session.json 'agent' field does not contain 'opencode': {agent_val!r}\n"
            f"Full session.json: {data}"
        )

    def test_compile_pid_r42_compliance(self, scenario: ScenarioResult):
        """Detects concurrent synchronous + background compilation (R42 violation) (REC-W3).

        REC-W3 (iter-18): Soft-fail stat-based timing check. If .dxnn was created much
        earlier than the compile_out.log line count implies (background compile still running),
        it suggests a synchronous dx_com.compile() ran in parallel with the background
        subprocess — an R42 violation.
        """
        if not scenario.succeeded:
            pytest.skip("OpenCode execution failed")
        import warnings
        compiler_dirs = [d for d in scenario.output_dirs if "dx-compiler" in str(d)]
        for comp_dir in compiler_dirs:
            dxnn_files = list(comp_dir.glob("*.dxnn"))
            compile_out_files = list(comp_dir.glob("compile_out*.log"))
            if not dxnn_files or not compile_out_files:
                continue
            try:
                dxnn_mtime = dxnn_files[0].stat().st_mtime
                dir_mtime = comp_dir.stat().st_mtime
                compile_out_lines = sum(
                    len(f.read_text(encoding="utf-8", errors="replace").splitlines())
                    for f in compile_out_files
                )
                time_since_start = dxnn_mtime - dir_mtime
                if compile_out_lines > 1000 and time_since_start < 1200:
                    warnings.warn(
                        f"{comp_dir.name}: R42 compliance anomaly — .dxnn created "
                        f"{time_since_start:.0f}s after session start but compile_out.log "
                        f"has {compile_out_lines} lines (background compile still running). "
                        "Suggests synchronous dx_com.compile() ran alongside background PID. "
                        "R42 prohibits synchronous compile() in the main agent thread.",
                        UserWarning,
                        stacklevel=2,
                    )
            except Exception:
                pass
