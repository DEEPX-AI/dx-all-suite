# SPDX-License-Identifier: Apache-2.0
"""
Shared fixtures and utilities for agentic E2E scenario tests.

Provides:
- CopilotRunnerAutopilot: subprocess wrapper for ``copilot`` CLI (autopilot mode)
- Session auto-detection: finds new ``dx-agentic-dev/<session_id>/`` dirs
- Verification helpers: syntax, JSON structure, pattern matching
- ScenarioResult: dataclass holding execution outcome + output directories
- Session-scoped fixtures for runner and output management

Note: Manual (interactive) mode is handled by ``test.sh agentic-e2e-manual``
directly as a shell-based script (no pytest). See test.sh for details.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set

import pytest

# Import session log parser (sibling module)
_TESTS_DIR = Path(__file__).resolve().parents[1]
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from parse_copilot_session import (  # noqa: E402
    find_sessions,
    has_start_sentinel,
    parse_and_render,
    parse_session,
)

# ---------------------------------------------------------------------------
# Path constants (same roots as test_agentic_scenarios)
# ---------------------------------------------------------------------------

SUITE_ROOT = Path(__file__).resolve().parents[2]  # dx-all-suite/
COMPILER_ROOT = SUITE_ROOT / "dx-compiler"
RUNTIME_ROOT = SUITE_ROOT / "dx-runtime"
APP_ROOT = RUNTIME_ROOT / "dx_app"
STREAM_ROOT = RUNTIME_ROOT / "dx_stream"

# Base directory for agentic E2E test artifacts (gitignored via dx-agentic-dev/)
AGENTIC_E2E_ARTIFACTS_BASE = SUITE_ROOT / "dx-agentic-dev" / "e2e-tests"

# Default timeout for Copilot CLI execution (5 minutes)
DEFAULT_COPILOT_TIMEOUT = int(os.environ.get("DX_AGENTIC_E2E_TIMEOUT", "300"))

# Model to use for agentic E2E tests (override via env var)
DEFAULT_COPILOT_MODEL = os.environ.get("DX_AGENTIC_E2E_MODEL", "claude-sonnet-4.6")


# ---------------------------------------------------------------------------
# Session auto-detection: dx-agentic-dev/<session_id>/ discovery
# ---------------------------------------------------------------------------

# Each scenario may produce output in one or more dx-agentic-dev/ directories.
# Cross-project scenarios (suite, runtime) may route to sub-projects.
AGENTIC_DEV_SEARCH_PATHS: Dict[str, List[Path]] = {
    "compiler": [COMPILER_ROOT / "dx-agentic-dev"],
    "dx_app": [APP_ROOT / "dx-agentic-dev"],
    "dx_stream": [STREAM_ROOT / "dx-agentic-dev"],
    "runtime": [
        RUNTIME_ROOT / "dx-agentic-dev",
        APP_ROOT / "dx-agentic-dev",
        STREAM_ROOT / "dx-agentic-dev",
    ],
    "suite": [
        SUITE_ROOT / "dx-agentic-dev",
        COMPILER_ROOT / "dx-agentic-dev",
        APP_ROOT / "dx-agentic-dev",
        STREAM_ROOT / "dx-agentic-dev",
        RUNTIME_ROOT / "dx-agentic-dev",
    ],
}


def _snapshot_sessions(search_paths: List[Path]) -> Set[Path]:
    """Snapshot existing session directories under the given search paths."""
    existing: Set[Path] = set()
    for agentic_dev_dir in search_paths:
        if agentic_dev_dir.exists():
            for child in agentic_dev_dir.iterdir():
                if child.is_dir():
                    existing.add(child)
    return existing


def _detect_new_sessions(
    search_paths: List[Path],
    snapshot: Set[Path],
) -> List[Path]:
    """Find new session directories created after *snapshot*.

    Returns a list of newly created session dirs, sorted by modification time
    (newest last).
    """
    new_dirs: List[Path] = []
    for agentic_dev_dir in search_paths:
        if agentic_dev_dir.exists():
            for child in agentic_dev_dir.iterdir():
                if child.is_dir() and child not in snapshot:
                    new_dirs.append(child)
    return sorted(new_dirs, key=lambda p: p.stat().st_mtime)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ScenarioResult:
    """Result of a Copilot CLI scenario execution.

    ``output_dirs`` contains all auto-detected session directories (one per
    sub-project that produced output).  For single-project scenarios this
    list typically has one entry; cross-project scenarios (suite) may have
    multiple.

    The ``output_dir`` convenience property returns the first (primary)
    directory, or ``None`` if nothing was detected.
    """

    returncode: int
    stdout: str
    stderr: str
    output_dirs: List[Path]
    session_log: Optional[Path]
    session_events_log: Optional[Path]
    duration_seconds: float
    prompt: str
    workdir: Path
    start_utc: Optional[str] = None
    end_utc: Optional[str] = None
    session_uuid: Optional[str] = None

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0

    @property
    def output_dir(self) -> Optional[Path]:
        """Primary output directory (first detected)."""
        return self.output_dirs[0] if self.output_dirs else None

    def _collect_files(self, glob_pattern: str) -> List[Path]:
        """Collect files matching *glob_pattern* across all output_dirs."""
        files: List[Path] = []
        for d in self.output_dirs:
            if d.exists():
                files.extend(d.rglob(glob_pattern))
        return sorted(files)

    @property
    def generated_py_files(self) -> List[Path]:
        """All .py files generated across output directories."""
        return self._collect_files("*.py")

    @property
    def generated_json_files(self) -> List[Path]:
        """All .json files generated across output directories."""
        return self._collect_files("*.json")

    @property
    def all_generated_files(self) -> List[Path]:
        """All files generated across output directories."""
        files: List[Path] = []
        for d in self.output_dirs:
            if d.exists():
                files.extend(f for f in d.rglob("*") if f.is_file())
        return sorted(files)

    @property
    def generated_onnx_files(self) -> List[Path]:
        """All .onnx files generated across output directories."""
        return self._collect_files("*.onnx")

    @property
    def generated_dxnn_files(self) -> List[Path]:
        """All .dxnn files generated across output directories."""
        return self._collect_files("*.dxnn")


# ---------------------------------------------------------------------------
# CopilotRunnerAutopilot
# ---------------------------------------------------------------------------

class CopilotRunnerAutopilot:
    """Wrapper for autopilot Copilot CLI invocations.

    Runs ``copilot -p <prompt> --yolo --no-ask-user -s`` for fully autonomous
    execution.  The ``--no-ask-user`` flag disables the ``ask_user`` tool so
    the agent never blocks on questions.

    Additionally, an autopilot directive is appended to every prompt to prevent
    the agent from asking questions via plain text output (which ``--no-ask-user``
    alone does not prevent — it only disables the ``ask_user`` tool call).

    Output files are auto-detected in ``dx-agentic-dev/<session_id>/`` under
    the relevant sub-project directories.  The prompt does NOT need to specify
    an output directory — copilot-instructions.md enforces Output Isolation.

    Usage::

        runner = CopilotRunnerAutopilot()
        result = runner.run(
            prompt="Build a yolo26n detection app",
            workdir=APP_ROOT,
            scenario_key="dx_app",
        )
        assert result.succeeded
        assert result.output_dir is not None
    """

    COPILOT_BIN = "copilot"
    MODE = "autopilot"

    # Appended to every prompt in autopilot mode.  The --no-ask-user flag only
    # disables the ask_user *tool*; the agent can still output questions as
    # plain text and exit without generating files.  This directive prevents that.
    AUTOPILOT_DIRECTIVE = (
        " IMPORTANT: This is an automated test run. "
        "Do not ask questions or present options. "
        "Proceed directly with implementation, choosing the most appropriate approach."
    )

    def __init__(self, model: str = ""):
        self.model = model or DEFAULT_COPILOT_MODEL

    # -- availability checks ------------------------------------------------

    @classmethod
    def is_available(cls) -> bool:
        """Check if copilot binary is on PATH."""
        return shutil.which(cls.COPILOT_BIN) is not None

    @classmethod
    def copilot_path(cls) -> Optional[str]:
        """Return the full path to the copilot binary, or None."""
        return shutil.which(cls.COPILOT_BIN)

    # -- execution ----------------------------------------------------------

    def run(
        self,
        prompt: str,
        workdir: Path,
        scenario_key: str,
        session_log_dir: Optional[Path] = None,
        timeout: int = DEFAULT_COPILOT_TIMEOUT,
        extra_args: Optional[List[str]] = None,
    ) -> ScenarioResult:
        """Execute a Copilot CLI prompt in autopilot mode.

        The prompt should NOT include an output directory — Copilot's
        ``copilot-instructions.md`` Output Isolation rule automatically writes
        generated files to ``dx-agentic-dev/<session_id>/`` within the target
        sub-project.

        After execution, this method auto-detects the new session directory
        by comparing a pre-run snapshot of ``dx-agentic-dev/`` contents with
        the post-run state.

        Args:
            prompt: The instruction to send to Copilot.
            workdir: Working directory (determines which copilot-instructions load).
            scenario_key: One of ``"compiler"``, ``"dx_app"``, ``"dx_stream"``,
                ``"runtime"``, ``"suite"``.  Determines which ``dx-agentic-dev/``
                paths to search for output.
            session_log_dir: Directory to store the session transcript.
                If ``None``, uses a temp directory.
            timeout: Maximum execution time in seconds.
            extra_args: Additional CLI arguments.

        Returns:
            ScenarioResult with exit code, output, and auto-detected output dirs.
        """
        # Session log location
        log_dir = session_log_dir or Path(os.environ.get("TMPDIR", "/tmp"))
        log_dir.mkdir(parents=True, exist_ok=True)
        # Filenames are updated with UUID suffix after copilot exits
        session_log = log_dir / f"{scenario_key}-copilot-session.md"

        # Build effective prompt (original + autopilot directive)
        effective_prompt = prompt + self.AUTOPILOT_DIRECTIVE

        # Determine search paths for this scenario
        search_paths = AGENTIC_DEV_SEARCH_PATHS.get(
            scenario_key, [workdir / "dx-agentic-dev"],
        )

        # Pre-snapshot: record existing session directories
        snapshot = _snapshot_sessions(search_paths)

        # Record start timestamp for events.jsonl parsing
        start_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        cmd = [
            self.COPILOT_BIN,
            "-p", effective_prompt,
            "--yolo",                # --allow-all-tools --allow-all-paths --allow-all-urls
            "--no-ask-user",         # fully autonomous
            "-s",                    # silent (agent response only)
            f"--share={session_log}",  # save session transcript
        ]

        if self.model:
            cmd.extend(["--model", self.model])

        if extra_args:
            cmd.extend(extra_args)

        start = time.monotonic()
        try:
            result = subprocess.run(
                cmd,
                cwd=str(workdir),
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, "NO_COLOR": "1"},
            )
            duration = time.monotonic() - start

            # Post-detection: find new session directories
            output_dirs = _detect_new_sessions(search_paths, snapshot)

            # Record end timestamp
            end_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            # Extract copilot CLI session UUID for artifact naming
            session_uuid, session_state_dir = _extract_session_info(
                cwd=str(workdir), after=start_utc, before=end_utc,
            )
            uuid_suffix = session_uuid or "unknown"

            # Session-logs directory with UUID
            session_logs_dir = log_dir / f"session-logs-{uuid_suffix}"
            session_logs_dir.mkdir(parents=True, exist_ok=True)

            session_events_log = session_logs_dir / f"{scenario_key}-session_logs-{uuid_suffix}.md"

            # Parse Copilot events.jsonl (best-effort)
            _parse_session_events(
                cwd=str(workdir),
                after=start_utc,
                before=end_utc,
                output=session_events_log,
                output_dirs=output_dirs,
            )

            # Copy events.jsonl for traceability
            if session_state_dir:
                events_src = Path(session_state_dir) / "events.jsonl"
                if events_src.exists():
                    events_dest = log_dir / f"{scenario_key}-copilot-events-{uuid_suffix}.jsonl"
                    try:
                        shutil.copy2(str(events_src), str(events_dest))
                    except Exception:
                        pass  # Best-effort

            # Symlinks: create in log_dir for each detected output dir
            # Pattern: <parent_name>_<session_name> -> <real_path>
            for odir in output_dirs:
                try:
                    odir_real = odir.resolve()
                    session_name = odir_real.name
                    parent_name = odir_real.parent.parent.name  # e.g. dx-compiler
                    link_path = log_dir / f"{parent_name}_{session_name}"
                    link_path.unlink(missing_ok=True)
                    link_path.symlink_to(odir_real)
                except Exception:
                    pass  # Best-effort

            return ScenarioResult(
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                output_dirs=output_dirs,
                session_log=session_log if session_log.exists() else None,
                session_events_log=session_events_log if session_events_log.exists() else None,
                duration_seconds=duration,
                prompt=prompt,
                workdir=workdir,
                start_utc=start_utc,
                end_utc=end_utc,
                session_uuid=session_uuid,
            )
        except subprocess.TimeoutExpired as exc:
            duration = time.monotonic() - start

            # Still try to detect any partial output
            output_dirs = _detect_new_sessions(search_paths, snapshot)

            # Extract session info even on timeout (best-effort)
            end_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            session_uuid, session_state_dir = _extract_session_info(
                cwd=str(workdir), after=start_utc, before=end_utc,
            )
            uuid_suffix = session_uuid or "unknown"

            # Session-logs directory with UUID
            session_logs_dir = log_dir / f"session-logs-{uuid_suffix}"
            session_logs_dir.mkdir(parents=True, exist_ok=True)

            session_events_log = session_logs_dir / f"{scenario_key}-session_logs-{uuid_suffix}.md"

            # Parse events even on timeout (best-effort)
            _parse_session_events(
                cwd=str(workdir),
                after=start_utc,
                before=end_utc,
                output=session_events_log,
                output_dirs=output_dirs,
            )

            # Copy events.jsonl for traceability
            if session_state_dir:
                events_src = Path(session_state_dir) / "events.jsonl"
                if events_src.exists():
                    events_dest = log_dir / f"{scenario_key}-copilot-events-{uuid_suffix}.jsonl"
                    try:
                        shutil.copy2(str(events_src), str(events_dest))
                    except Exception:
                        pass  # Best-effort

            # Symlinks: create in log_dir for each detected output dir
            # Pattern: <parent_name>_<session_name> -> <real_path>
            for odir in output_dirs:
                try:
                    odir_real = odir.resolve()
                    session_name = odir_real.name
                    parent_name = odir_real.parent.parent.name  # e.g. dx-compiler
                    link_path = log_dir / f"{parent_name}_{session_name}"
                    link_path.unlink(missing_ok=True)
                    link_path.symlink_to(odir_real)
                except Exception:
                    pass  # Best-effort

            return ScenarioResult(
                returncode=-1,
                stdout=exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
                stderr=f"TIMEOUT after {timeout}s",
                output_dirs=output_dirs,
                session_log=session_log if session_log.exists() else None,
                session_events_log=session_events_log if session_events_log.exists() else None,
                duration_seconds=duration,
                prompt=prompt,
                workdir=workdir,
                start_utc=start_utc,
                end_utc=end_utc,
                session_uuid=session_uuid,
            )


# ---------------------------------------------------------------------------
# Copilot session UUID + state dir extraction (best-effort)
# ---------------------------------------------------------------------------


def _extract_session_info(
    cwd: str, after: str, before: str,
) -> tuple:
    """Extract copilot CLI session UUID and state directory path.

    Returns:
        ``(session_uuid, session_state_dir)`` — either may be ``None``.
    """
    try:
        sessions = find_sessions(cwd=cwd, after=after, before=before)
        if sessions:
            return sessions[0].session_id, sessions[0].session_dir
    except Exception:
        pass
    return None, None


# ---------------------------------------------------------------------------
# Session events.jsonl parsing (best-effort)
# ---------------------------------------------------------------------------

def _parse_session_events(
    cwd: str,
    after: str,
    before: str,
    output: Path,
    output_dirs: Optional[List[Path]] = None,
) -> None:
    """Parse Copilot session events.jsonl into Markdown and HTML reports.

    Generates both formats:
    - ``<output>`` — Markdown report (original behaviour)
    - ``<output_stem>.html`` — self-contained HTML report

    If *output_dirs* is provided, copies the HTML report into the first
    detected session directory as ``session.html`` for self-contained
    output archival.

    This is best-effort — failures are silently ignored so they never
    block test execution or validation.
    """
    try:
        # Markdown (original)
        parse_and_render(cwd=cwd, after=after, before=before, output=output)
    except Exception:
        pass  # Best-effort: never fail the test

    try:
        # HTML
        html_output = output.with_suffix(".html")
        parse_and_render(
            cwd=cwd, after=after, before=before, output=html_output, fmt="html",
        )
        # Copy HTML into detected session dir(s)
        if output_dirs and html_output.exists():
            for d in output_dirs:
                if d.is_dir():
                    shutil.copy2(str(html_output), str(d / "session.html"))
    except Exception:
        pass  # Best-effort: never fail the test


# ---------------------------------------------------------------------------
# Verification helpers
# ---------------------------------------------------------------------------

def verify_python_syntax(filepath: Path) -> None:
    """Assert that a Python file has valid syntax (ast.parse).

    Raises AssertionError with a clear message on failure.
    """
    source = filepath.read_text(encoding="utf-8")
    try:
        ast.parse(source, filename=str(filepath))
    except SyntaxError as exc:
        pytest.fail(
            f"Invalid Python syntax in {filepath.name}:\n"
            f"  Line {exc.lineno}: {exc.msg}\n"
            f"  {exc.text}"
        )


def verify_json_structure(
    filepath: Path,
    required_keys: Optional[List[str]] = None,
) -> dict:
    """Assert that a JSON file is valid and contains required keys.

    Returns the parsed JSON dict.
    """
    text = filepath.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        pytest.fail(f"Invalid JSON in {filepath.name}: {exc}")

    if required_keys:
        missing = [k for k in required_keys if k not in data]
        if missing:
            pytest.fail(
                f"{filepath.name} missing required keys: {missing}\n"
                f"  Found keys: {list(data.keys())}"
            )
    return data


def verify_patterns_in_file(
    filepath: Path,
    patterns: List[str],
    description: str = "",
) -> None:
    """Assert that a file contains all specified regex patterns.

    Args:
        filepath: File to check.
        patterns: List of regex patterns that must all be found.
        description: Context for error messages.
    """
    content = filepath.read_text(encoding="utf-8")
    missing = []
    for pattern in patterns:
        if not re.search(pattern, content):
            missing.append(pattern)
    if missing:
        ctx = f" ({description})" if description else ""
        pytest.fail(
            f"{filepath.name}{ctx} missing expected patterns:\n"
            + "\n".join(f"  - {p}" for p in missing)
        )


def verify_file_tree(
    base_dir: Path,
    expected_patterns: List[str],
) -> List[Path]:
    """Assert that at least one file matches each glob pattern.

    Args:
        base_dir: Root directory to search.
        expected_patterns: Glob patterns (e.g., "**/*.py", "**/config.json").

    Returns:
        List of all matched files across all patterns.
    """
    all_matched = []
    missing = []
    for pattern in expected_patterns:
        matches = list(base_dir.glob(pattern))
        if not matches:
            missing.append(pattern)
        all_matched.extend(matches)
    if missing:
        existing = [str(f.relative_to(base_dir)) for f in base_dir.rglob("*") if f.is_file()]
        pytest.fail(
            f"Missing expected files in {base_dir}:\n"
            + "\n".join(f"  - {p}" for p in missing)
            + f"\n\nExisting files:\n"
            + "\n".join(f"  - {f}" for f in existing[:30])
        )
    return all_matched


def format_scenario_failure(result: ScenarioResult) -> str:
    """Format a clear error message for a failed scenario execution."""
    output_str = ", ".join(str(d) for d in result.output_dirs) if result.output_dirs else "(none detected)"
    lines = [
        "",
        "=" * 80,
        "COPILOT AGENTIC E2E SCENARIO FAILED",
        "=" * 80,
        f"Exit Code: {result.returncode}",
        f"Duration:  {result.duration_seconds:.1f}s",
        f"Workdir:   {result.workdir}",
        f"Output:    {output_str}",
        "",
        "PROMPT:",
        "-" * 80,
        result.prompt,
        "",
    ]
    if result.stdout:
        lines.extend([
            "STDOUT (last 50 lines):",
            "-" * 80,
            "\n".join(result.stdout.splitlines()[-50:]),
            "",
        ])
    if result.stderr:
        lines.extend([
            "STDERR (last 30 lines):",
            "-" * 80,
            "\n".join(result.stderr.splitlines()[-30:]),
            "",
        ])
    if result.session_log and result.session_log.exists():
        lines.append(f"Session log: {result.session_log}")
    if result.session_events_log and result.session_events_log.exists():
        lines.append(f"Parsed events log: {result.session_events_log}")
    lines.append("=" * 80)
    return "\n".join(lines)


def verify_start_sentinel(result: ScenarioResult) -> None:
    """Assert that the agent emitted ``[DX-AGENTIC-DEV: START]`` in the session.

    Checks two sources:
    1. The captured ``stdout`` of the Copilot CLI run (``-s`` mode outputs
       agent text directly).
    2. The parsed session events from ``events.jsonl`` (via
       ``parse_copilot_session``).

    Raises ``pytest.fail`` with a diagnostic message if the sentinel is
    missing from both sources.
    """
    import re as _re

    _START_RE = _re.compile(r"\[DX-AGENTIC-DEV:\s*START\]")

    # Quick check: stdout from the copilot CLI process
    if _START_RE.search(result.stdout or ""):
        return

    # Thorough check: re-parse the session events.jsonl
    if result.start_utc and result.end_utc:
        try:
            sessions = find_sessions(
                cwd=str(result.workdir),
                after=result.start_utc,
                before=result.end_utc,
            )
            for meta in sessions:
                parsed = parse_session(meta)
                if has_start_sentinel(parsed):
                    return
        except Exception:
            pass  # Fall through to failure

    pytest.fail(
        "Agent did not emit [DX-AGENTIC-DEV: START] sentinel.\n"
        "The copilot-instructions.md requires the agent to output this marker\n"
        "before any other text in its first response.\n"
        f"Workdir: {result.workdir}\n"
        f"Session log: {result.session_events_log}"
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Mode detection: set by test.sh via DX_AGENTIC_E2E_MODE env var
# Valid value: "autopilot" (default)
# Manual mode is handled by test.sh directly (shell-based, no pytest).
AGENTIC_E2E_MODE = os.environ.get("DX_AGENTIC_E2E_MODE", "autopilot")

_RUNNER_CLASSES = {
    "autopilot": CopilotRunnerAutopilot,
}


@pytest.fixture(scope="session")
def copilot_runner():
    """Session-scoped CopilotRunnerAutopilot for autopilot mode.

    Uses ``--yolo --no-ask-user -s`` flags for fully autonomous execution.
    Mode is determined by ``DX_AGENTIC_E2E_MODE`` env var (set by test.sh).

    Manual mode is handled by ``test.sh agentic-e2e-manual`` directly
    (shell-based interactive, no pytest).
    """
    runner_cls = _RUNNER_CLASSES.get(AGENTIC_E2E_MODE, CopilotRunnerAutopilot)
    if not runner_cls.is_available():
        pytest.skip(
            f"Copilot CLI not found on PATH. "
            f"Searched for '{runner_cls.COPILOT_BIN}' — not found. "
            f"Install Copilot CLI first (see README.md)."
        )
    return runner_cls()


@pytest.fixture(scope="session")
def agentic_e2e_artifacts_dir():
    """Session-scoped base directory for all agentic E2E test artifacts.

    Creates ``dx-agentic-dev/e2e-tests/<session_id>/`` and cleans up after
    the session unless ``DX_AGENTIC_E2E_KEEP_ARTIFACTS=1`` is set.
    """
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = AGENTIC_E2E_ARTIFACTS_BASE / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    yield artifacts_dir

    # Cleanup unless explicitly kept
    if not os.environ.get("DX_AGENTIC_E2E_KEEP_ARTIFACTS"):
        shutil.rmtree(artifacts_dir, ignore_errors=True)
        # Also remove parent if empty
        if AGENTIC_E2E_ARTIFACTS_BASE.exists() and not any(AGENTIC_E2E_ARTIFACTS_BASE.iterdir()):
            AGENTIC_E2E_ARTIFACTS_BASE.rmdir()
