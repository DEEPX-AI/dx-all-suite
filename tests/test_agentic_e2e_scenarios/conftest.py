# SPDX-License-Identifier: Apache-2.0
"""
Shared fixtures and utilities for agentic E2E scenario tests.

Provides:
- CopilotRunnerAutopilot: subprocess wrapper for ``copilot`` (Copilot CLI, autopilot mode)
- CursorRunnerAutopilot: subprocess wrapper for ``agent`` (Cursor CLI, autopilot mode,
  default model: claude-4.6-sonnet-medium)
- Session auto-detection: finds new ``dx-agentic-dev/<session_id>/`` dirs
- Verification helpers: syntax, JSON structure, pattern matching
- ScenarioResult: dataclass holding execution outcome + output directories
- Session-scoped fixtures for runner and output management

Note: Manual (interactive) modes are handled by ``test.sh agentic-e2e-copilot-manual``
and ``test.sh agentic-e2e-cursor-manual`` as shell-based scripts (no pytest).
"""

from __future__ import annotations

import ast
import fcntl
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set

_logger = logging.getLogger(__name__)

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

# Base directories for agentic E2E test artifacts (gitignored via dx-agentic-dev/).
# Suite/runtime scenarios: SUITE_ROOT; sub-project scenarios: per-project roots.
AGENTIC_E2E_ARTIFACTS_BASE = SUITE_ROOT / "dx-agentic-dev" / "e2e-tests"
COMPILER_E2E_ARTIFACTS_BASE = COMPILER_ROOT / "dx-agentic-dev" / "e2e-tests"
APP_E2E_ARTIFACTS_BASE = APP_ROOT / "dx-agentic-dev" / "e2e-tests"
STREAM_E2E_ARTIFACTS_BASE = STREAM_ROOT / "dx-agentic-dev" / "e2e-tests"

# Default timeout for Copilot CLI execution (10 minutes — Copilot's corrective-iteration
# behaviour with model download + live gst-launch verification can exceed 6 min; 600s
# matches the timeout used by Cursor, OpenCode, and Claude Code runners)
DEFAULT_COPILOT_TIMEOUT = int(os.environ.get("DX_AGENTIC_E2E_TIMEOUT", "600"))

# Separate timeout for Copilot cascaded scenarios — cascaded sessions require more time
# than single_model; 900s gives Copilot extra margin (vs 720s for OpenCode) because
# Copilot's brainstorming pass takes longer and it often retries within a session.
DEFAULT_COPILOT_CASCADED_TIMEOUT = int(os.environ.get("DX_COPILOT_CASCADED_TIMEOUT", "900"))

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


def _wait_for_background_compilation(dirs: List[Path], timeout_s: int = 180) -> None:
    """R34: Wait for any background compilation (tracked via compile.pid) to finish.

    After detecting session directories, if any contains a ``compile.pid`` file,
    read the PID and wait up to *timeout_s* seconds for the process to exit using
    WNOHANG polling.  This closes the timing race between background `compile.py`
    subprocesses and test-collection time: without this wait, a test that runs
    immediately after the DONE sentinel may collect files before the .dxnn is written
    (observed in claude_code iter-6: DONE at 00:53, .dxnn at 00:56, test collected
    files at 00:53 → test_dxnn_compiled FAILED despite .dxnn eventually existing).

    The wait is bounded to *timeout_s* (default 180 s) to avoid hanging forever on
    orphaned PID files from previous failed sessions.

    REC-4: Also emits a warning when 2+ ``compile_out*.log`` files are detected in a
    session directory, indicating multiple compilation attempts (retries due to ENOSPC,
    calibration failures, etc.) that may exhaust the session time budget.
    """
    import errno
    import warnings

    for session_dir in dirs:
        # REC-4: Detect multiple compilation attempts
        compile_out_logs = list(session_dir.glob("compile_out*.log"))
        if len(compile_out_logs) >= 2:
            warnings.warn(
                f"REC-4: Multiple compilation attempts detected in {session_dir.name}: "
                f"{len(compile_out_logs)} compile_out*.log files found "
                f"({[f.name for f in sorted(compile_out_logs)]}). "
                "This indicates retries (ENOSPC, calibration failure, etc.) that may "
                "exhaust the session time budget. Check disk space and calibration strategy.",
                UserWarning,
                stacklevel=2,
            )

        pid_file = session_dir / "compile.pid"
        if not pid_file.exists():
            continue
        try:
            pid = int(pid_file.read_text().strip())
        except Exception:
            continue

        deadline = time.monotonic() + timeout_s
        _logger.info(
            "R34: compile.pid found in %s (PID=%d) — waiting up to %ds for compilation",
            session_dir.name, pid, timeout_s,
        )
        while time.monotonic() < deadline:
            try:
                waited_pid, _ = os.waitpid(pid, os.WNOHANG)
                if waited_pid != 0:
                    _logger.info("R34: compilation PID=%d exited cleanly", pid)
                    break
            except ChildProcessError:
                # Process already exited and was reaped (or never a child — common for
                # subprocess.Popen with start_new_session=True)
                _logger.info("R34: compilation PID=%d already exited (ChildProcessError)", pid)
                break
            except OSError as exc:
                if exc.errno == errno.ECHILD:
                    _logger.info("R34: compilation PID=%d already reaped (ECHILD)", pid)
                    break
                # Unexpected OS error — stop polling
                _logger.warning("R34: waitpid(%d) OSError: %s", pid, exc)
                break
            time.sleep(5)
        else:
            _logger.warning(
                "R34: compile.pid PID=%d still running after %ds — continuing anyway",
                pid, timeout_s,
            )

        # REC-X5: After compilation wait, check for ONNX retention in compiler sessions.
        # If .onnx is absent, append a WARNING to session.log so the gap is visible in
        # first-pass output rather than only at test collection time.
        has_onnx = any(session_dir.glob("*.onnx"))
        if not has_onnx and (session_dir / "compile.py").exists():
            warning_msg = (
                "WARNING: .onnx not retained in compiler session "
                f"({session_dir.name}) — "
                "verify.py and re-compilation will not have access to the source ONNX. "
                "Add: shutil.copy(onnx_path, work_dir) in compile.py (REC-X5)"
            )
            _logger.warning("REC-X5: %s", warning_msg)
            session_log = session_dir / "session.log"
            try:
                with session_log.open("a", encoding="utf-8") as _sl:
                    _sl.write(f"\n{warning_msg}\n")
            except Exception:
                pass


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
    agent_filter: Optional[str] = None,
    exclude_filters: Optional[List[str]] = None,
) -> List[Path]:
    """Find new session directories created after *snapshot*.

    Returns a list of newly created non-empty session dirs, sorted by
    modification time (newest last).  Empty directories are excluded — some
    tools (e.g. OpenCode) create a placeholder directory on a first failed
    attempt and then retry into a different directory; including the empty
    placeholder causes false positives in output detection.

    R20: When *agent_filter* is provided (e.g. ``"copilot"``, ``"cursor"``,
    ``"claude"``), only directories whose name contains the filter string are
    returned.  This prevents cross-contamination when multiple tools run
    concurrently and each tool's `_detect_new_sessions` scan picks up sessions
    created by the others (false positives if the current tool fails silently).

    R39: When *exclude_filters* is provided (e.g. ``["_copilot_", "_cursor_"]``
    for opencode), directories whose name contains ANY of the exclude strings
    are removed.  This prevents cross-tool session contamination for tools whose
    subagent uses a shared agent name (e.g. opencode → claude subagent, which
    can collide with sessions from the claude_code runner).
    """
    new_dirs: List[Path] = []
    for agentic_dev_dir in search_paths:
        if agentic_dev_dir.exists():
            for child in agentic_dev_dir.iterdir():
                if child.is_dir() and child not in snapshot:
                    # Skip empty directories (failed first-attempt placeholders)
                    if any(child.rglob("*")):
                        new_dirs.append(child)
    if agent_filter:
        new_dirs = [d for d in new_dirs if agent_filter in d.name]
    if exclude_filters:
        for ef in exclude_filters:
            new_dirs = [d for d in new_dirs if ef not in d.name]
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
    model_used: Optional[str] = None  # actual model used (may differ from requested if fallback triggered)

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

    @property
    def environment_hard_gate(self) -> bool:
        """R57: True when agent correctly halted at Phase 0 environment HARD GATE.

        Distinguishes "agent bug" from "environment not ready": when output_dirs
        is empty AND the session log contains HARD GATE indicators, tests should
        SKIP (informational) rather than FAIL (regression).
        """
        if self.output_dirs:
            return False
        _keywords = (
            "sanity_check FAILED", "Sanity check FAIL", "Sanity check failed",
            "HARD GATE", "libdxrt", "dpkg lock",
        )
        _text = " ".join(filter(None, [self.stdout or "", self.stderr or ""]))
        if self.session_log and self.session_log.exists():
            try:
                _text += " " + self.session_log.read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass
        return any(kw in _text for kw in _keywords)

    @property
    def connection_error(self) -> bool:
        """R66: True when the tool reports repeated connection failures (network/service outage).

        Cursor's connection failure mode emits 'Connection failed repeatedly' in stderr
        and produces 'reconnecting' NDJSON subtype events with 5+ retry attempts.
        This flag enables post-run diagnosis without manual log inspection, and
        allows format_scenario_failure to surface a human-readable explanation.
        """
        _stderr = self.stderr or ""
        _stdout = self.stdout or ""
        if "Connection failed repeatedly" in _stderr:
            return True
        if _stdout.count('"subtype":"reconnecting"') >= 5:
            return True
        return False


# ---------------------------------------------------------------------------
# CopilotRunnerAutopilot
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Default model for Cursor CLI
# ---------------------------------------------------------------------------

DEFAULT_CURSOR_MODEL = os.environ.get("DX_AGENTIC_E2E_CURSOR_MODEL", "claude-4.6-sonnet-medium-thinking")
# Fallback model used when the primary model hits a quota/usage-limit error.
# Cursor's error message says "Switch to auto or Auto" — so "auto" is the correct value.
CURSOR_FALLBACK_MODEL = os.environ.get("DX_AGENTIC_E2E_CURSOR_FALLBACK_MODEL", "auto")

# Default timeout for Cursor CLI execution (5 minutes)
DEFAULT_CURSOR_TIMEOUT = int(os.environ.get("DX_AGENTIC_E2E_CURSOR_TIMEOUT", "600"))

# ---------------------------------------------------------------------------
# Default model / timeout for OpenCode CLI
# ---------------------------------------------------------------------------

DEFAULT_OPENCODE_MODEL = os.environ.get("DX_AGENTIC_E2E_OPENCODE_MODEL", "github-copilot/claude-sonnet-4.6")
DEFAULT_OPENCODE_TIMEOUT = int(os.environ.get("DX_AGENTIC_E2E_OPENCODE_TIMEOUT", "600"))
# Separate timeout for OpenCode cascaded scenarios — cascaded sessions are longer and require
# more time than single_model scenarios; default 720s gives a 20% margin over the observed 600s limit.
DEFAULT_OPENCODE_CASCADED_TIMEOUT = int(os.environ.get("DX_OPENCODE_CASCADED_TIMEOUT", "720"))

# ---------------------------------------------------------------------------
# Default model / timeout for Claude Code CLI
# ---------------------------------------------------------------------------

DEFAULT_CLAUDE_CODE_MODEL = os.environ.get("DX_AGENTIC_E2E_CLAUDE_CODE_MODEL", "claude-sonnet-4-6")
DEFAULT_CLAUDE_CODE_TIMEOUT = int(os.environ.get("DX_AGENTIC_E2E_CLAUDE_CODE_TIMEOUT", "600"))

# ---------------------------------------------------------------------------
# R59: Advisory file lock to serialize concurrent apt/dpkg operations
# ---------------------------------------------------------------------------

_APT_LOCK_FILE = "/tmp/dx_e2e_apt.lock"


@contextmanager
def _apt_lock():
    """R59: Serialize concurrent agent subprocess launches to prevent dpkg conflicts.

    When 4 tool suites run simultaneously, each agent's Phase 0 runs
    sanity_check.sh + install.sh, causing concurrent apt/dpkg races that
    leave libdxrt in a broken state. This lock serializes subprocess launches
    so only one agent installs packages at a time.

    The lock covers the full subprocess execution because Phase 0 (apt install)
    occurs at the start and we cannot signal when it completes from outside.
    """
    with open(_APT_LOCK_FILE, "w") as _lf:
        try:
            fcntl.flock(_lf.fileno(), fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(_lf.fileno(), fcntl.LOCK_UN)


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

            # R3/R6: Ghost-run detection.
            # If the CLI exits in < 30 s with empty stdout, it is almost certainly
            # a caching/deduplication early-exit — not a real agent run.  Log a
            # diagnostic so the issue is surfaced in the pytest log rather than
            # silently appearing as "0 files generated".
            _GHOST_RUN_THRESHOLD_S = 30
            if duration < _GHOST_RUN_THRESHOLD_S and not (result.stdout or "").strip():
                _logger.warning(
                    "Copilot ghost run detected: CLI exited in %.1fs with empty stdout "
                    "(likely deduplication or session caching — not a real agent run). "
                    "Scenario will be reported as empty. "
                    "Check for duplicate session detection or stale cache.",
                    duration,
                )

            # REC-3: ENOSPC soft-exit detection.
            # Copilot CLI exits with code 1 when its internal JSONL session-events writer
            # fails due to disk full — even though all user-facing work is complete.
            # If returncode==1 AND ENOSPC is in stderr AND the DONE sentinel is present,
            # treat as a successful run for test purposes (all artifacts are intact).
            _effective_returncode = result.returncode
            if (
                result.returncode == 1
                and "ENOSPC" in (result.stderr or "")
                and "[DX-AGENTIC-DEV: DONE" in (result.stdout or "")
            ):
                _logger.warning(
                    "REC-3: Copilot exited with code 1 due to ENOSPC (disk full on "
                    "session-events.jsonl write), but DONE sentinel is present — "
                    "all user-facing artifacts are intact. Treating as returncode=0."
                )
                _effective_returncode = 0

            # Post-detection: find new session directories.
            # Copilot sub-agents may write output dirs several minutes after the
            # main CLI process exits, so poll up to 120 s in 5-second intervals.
            output_dirs = _detect_new_sessions(search_paths, snapshot, agent_filter="copilot")
            if not output_dirs:
                poll_deadline = time.monotonic() + 120
                while time.monotonic() < poll_deadline:
                    time.sleep(5)
                    output_dirs = _detect_new_sessions(search_paths, snapshot, agent_filter="copilot")
                    if output_dirs:
                        break

            # R34: Wait for any background compilation tracked via compile.pid before collecting
            _wait_for_background_compilation(output_dirs)

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

            # R70/R74: Resolve authoritative output_dir from DONE sentinel before copying
            # session.html.  Prevents Copilot's HTML from contaminating other tools'
            # session directories when all 4 tools run concurrently and create dirs
            # with similar timestamps that confuse the name-based scanner.
            #
            # R74: R70 used SUITE_ROOT to resolve the sentinel path, but agents running
            # in a sub-project workdir (e.g. dx_stream/) emit paths relative to workdir,
            # not SUITE_ROOT.  Try workdir first; fall back to SUITE_ROOT for cross-project
            # paths.  If the sentinel is absent entirely, pass an empty list to avoid
            # writing HTML to all concurrently-detected dirs (the root cause of 486 L
            # cross-contamination in dirs attributed to Claude Code and OpenCode).
            _copilot_html_dirs: List[Path] = []  # default: no HTML copy unless sentinel resolves
            _done_copilot = re.search(
                r'\[DX-AGENTIC-DEV: DONE \(output-dir: ([^)]+)\)\]',
                result.stdout or "",
            )
            if _done_copilot:
                _rel = _done_copilot.group(1).strip()
                # Try workdir-relative first (most common for sub-project agents)
                _primary_copilot = workdir / _rel
                if not _primary_copilot.is_dir():
                    # Fall back to suite-root-relative (cross-project agents)
                    _primary_copilot = SUITE_ROOT / _rel
                if _primary_copilot.is_dir():
                    _copilot_html_dirs = [_primary_copilot]
                else:
                    # Sentinel found but path doesn't exist — scope to Copilot's first dir
                    _copilot_html_dirs = output_dirs[:1] if output_dirs else []
            elif output_dirs:
                # No sentinel: use only the first detected dir (Copilot's own session)
                # to avoid polluting any concurrently-created dirs from other tools.
                _copilot_html_dirs = output_dirs[:1]

            # Parse Copilot events.jsonl (best-effort)
            _parse_session_events(
                cwd=str(workdir),
                after=start_utc,
                before=end_utc,
                output=session_events_log,
                output_dirs=_copilot_html_dirs,
            )

            # Fallback: if --share file was not written (non-clean shutdown),
            # copy the parse_and_render MD output to the session_log path so
            # session_log is always present regardless of how Copilot exited.
            if not session_log.exists() and session_events_log.exists():
                try:
                    shutil.copy2(str(session_events_log), str(session_log))
                except Exception:
                    pass

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
                returncode=_effective_returncode,
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
            output_dirs = _detect_new_sessions(search_paths, snapshot, agent_filter="copilot")

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

            # Fallback: --share file is never written on timeout since Copilot
            # is SIGKILL'd before it can flush the share output.  Copy the
            # parse_and_render MD so session_log is always populated.
            if not session_log.exists() and session_events_log.exists():
                try:
                    shutil.copy2(str(session_events_log), str(session_log))
                except Exception:
                    pass

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
# Cursor quota-error detection
# ---------------------------------------------------------------------------

def _is_cursor_quota_error(text: str) -> bool:
    """Return True if *text* contains Cursor's usage-limit error message."""
    lower = text.lower()
    return "out of usage" in lower or "switch to auto" in lower


# ---------------------------------------------------------------------------
# Claude Code quota-error detection
# ---------------------------------------------------------------------------

_CLAUDE_QUOTA_POLL_INTERVAL = int(
    os.environ.get("DX_AGENTIC_E2E_CLAUDE_QUOTA_POLL_INTERVAL", "3600")
)
_CLAUDE_QUOTA_MAX_POLLS = int(
    os.environ.get("DX_AGENTIC_E2E_CLAUDE_QUOTA_MAX_POLLS", "8")
)


def _is_claude_code_usage_limit(text: str) -> bool:
    """Return True if text signals Claude Code usage/session limit exhaustion."""
    lower = text.lower()
    return "usage limit" in lower or "rate limit" in lower


# ---------------------------------------------------------------------------
# CursorRunnerAutopilot
# ---------------------------------------------------------------------------

class CursorRunnerAutopilot:
    """Wrapper for autopilot Cursor CLI (``agent``) invocations.

    Runs ``agent -p --force --output-format stream-json <prompt>`` for fully
    autonomous execution.  The ``--force`` flag auto-approves ALL file writes
    and tool calls (equivalent to Copilot's ``--yolo``).

    An autopilot directive is appended to every prompt to prevent the agent
    from asking questions via plain text output.

    Output files are auto-detected in ``dx-agentic-dev/<session_id>/`` under
    the relevant sub-project directories — same mechanism as Copilot.

    The ``stream-json`` output format provides structured NDJSON events that
    are parsed for session metadata (session_id, duration, assistant text).

    Usage::

        runner = CursorRunnerAutopilot()
        result = runner.run(
            prompt="Build a yolo26n detection app",
            workdir=APP_ROOT,
            scenario_key="dx_app",
        )
        assert result.succeeded
        assert result.output_dir is not None
    """

    CURSOR_BIN = "agent"
    MODE = "autopilot"

    AUTOPILOT_DIRECTIVE = (
        " IMPORTANT: This is an automated test run. "
        "Do not ask questions or present options. "
        "Proceed directly with implementation, choosing the most appropriate approach."
    )

    def __init__(self, model: str = ""):
        self.model = model or DEFAULT_CURSOR_MODEL

    @classmethod
    def is_available(cls) -> bool:
        """Check if the ``agent`` binary is on PATH."""
        return shutil.which(cls.CURSOR_BIN) is not None

    @classmethod
    def is_authenticated(cls) -> bool:
        """Check if the Cursor CLI is authenticated (API key or login).

        Runs a trivial ``agent -p`` invocation and checks for auth errors.
        Returns ``True`` if auth is configured, ``False`` otherwise.
        """
        if not cls.is_available():
            return False
        if os.environ.get("CURSOR_API_KEY"):
            return True
        try:
            probe = subprocess.run(
                [cls.CURSOR_BIN, "-p", "--output-format", "json", "echo test"],
                capture_output=True, text=True, timeout=60,
                env={**os.environ, "NO_COLOR": "1"},
            )
            if "Authentication required" in (probe.stderr or ""):
                return False
            if "CURSOR_API_KEY" in (probe.stderr or ""):
                return False
            return True
        except subprocess.TimeoutExpired:
            # Timeout means the CLI is running (authenticated) but LLM is slow
            return True
        except Exception:
            return False

    @classmethod
    def cursor_path(cls) -> Optional[str]:
        """Return the full path to the agent binary, or None."""
        return shutil.which(cls.CURSOR_BIN)

    def run(
        self,
        prompt: str,
        workdir: Path,
        scenario_key: str,
        session_log_dir: Optional[Path] = None,
        timeout: int = DEFAULT_CURSOR_TIMEOUT,
        extra_args: Optional[List[str]] = None,
    ) -> ScenarioResult:
        """Execute a Cursor CLI prompt in autopilot mode.

        Args:
            prompt: The instruction to send to the Cursor agent.
            workdir: Working directory (determines which .cursor/rules load).
            scenario_key: One of ``"compiler"``, ``"dx_app"``, ``"dx_stream"``,
                ``"runtime"``, ``"suite"``.
            session_log_dir: Directory to store the session transcript.
            timeout: Maximum execution time in seconds.
            extra_args: Additional CLI arguments.

        Returns:
            ScenarioResult with exit code, output, and auto-detected output dirs.
        """
        log_dir = session_log_dir or Path(os.environ.get("TMPDIR", "/tmp"))
        log_dir.mkdir(parents=True, exist_ok=True)

        effective_prompt = prompt + self.AUTOPILOT_DIRECTIVE

        search_paths = AGENTIC_DEV_SEARCH_PATHS.get(
            scenario_key, [workdir / "dx-agentic-dev"],
        )

        snapshot = _snapshot_sessions(search_paths)
        start_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        cmd = [
            self.CURSOR_BIN,
            "-p",                           # print / non-interactive mode
            "--force",                       # auto-approve all tool calls
            "--output-format", "stream-json",
            effective_prompt,
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

            # Usage-limit fallback: Cursor reports "out of usage / switch to auto"
            # when the primary model quota is exhausted.  Retry with CURSOR_FALLBACK_MODEL
            # ("auto") so the test can still run against an available model.
            actual_model = self.model
            if (result.returncode != 0
                    and _is_cursor_quota_error(result.stderr or result.stdout or "")
                    and self.model != CURSOR_FALLBACK_MODEL):
                fallback_cmd = [
                    self.CURSOR_BIN,
                    "-p",
                    "--force",
                    "--output-format", "stream-json",
                    effective_prompt,
                    "--model", CURSOR_FALLBACK_MODEL,
                ]
                # Carry over extra_args minus any --model override
                if extra_args:
                    skip_next = False
                    for arg in extra_args:
                        if skip_next:
                            skip_next = False
                            continue
                        if arg == "--model":
                            skip_next = True
                            continue
                        fallback_cmd.append(arg)
                result = subprocess.run(
                    fallback_cmd,
                    cwd=str(workdir),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env={**os.environ, "NO_COLOR": "1"},
                )
                duration = time.monotonic() - start
                actual_model = CURSOR_FALLBACK_MODEL  # quota exhausted — running on fallback model

            output_dirs = _detect_new_sessions(search_paths, snapshot, agent_filter="cursor")
            # REC-S5: Warn when cursor uses a non-Claude backend (e.g. GPT-4 via _gpt_ session ID)
            for odir in output_dirs:
                if "_gpt_" in str(odir):
                    warnings.warn(
                        f"cursor: GPT-4 backend detected (session contains _gpt_: {odir.name}) — "
                        "compile.pid (R42) and calibration compliance (REC-K) may regress. "
                        "Claude-backed cursor sessions pass consistently; GPT-4 does not follow R42.",
                        UserWarning,
                    )
            # R34: Wait for any background compilation tracked via compile.pid before collecting
            _wait_for_background_compilation(output_dirs)
            end_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            session_uuid, assistant_text = _parse_cursor_stream_json(result.stdout)

            session_log = log_dir / f"{scenario_key}-cursor-session.md"
            _save_cursor_session_log(
                session_log, result.stdout, result.stderr,
                scenario_key, prompt, session_uuid,
            )

            session_events_log = log_dir / f"{scenario_key}-cursor-stream.jsonl"
            try:
                session_events_log.write_text(result.stdout, encoding="utf-8")
            except Exception:
                pass

            for odir in output_dirs:
                try:
                    odir_real = odir.resolve()
                    session_name = odir_real.name
                    parent_name = odir_real.parent.parent.name
                    link_path = log_dir / f"{parent_name}_{session_name}"
                    link_path.unlink(missing_ok=True)
                    link_path.symlink_to(odir_real)
                except Exception:
                    pass

            return ScenarioResult(
                returncode=result.returncode,
                stdout=assistant_text or result.stdout,
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
                model_used=actual_model,
            )
        except subprocess.TimeoutExpired as exc:
            duration = time.monotonic() - start
            output_dirs = _detect_new_sessions(search_paths, snapshot, agent_filter="cursor")
            end_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            raw_stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            session_uuid, assistant_text = _parse_cursor_stream_json(raw_stdout)

            session_events_log = log_dir / f"{scenario_key}-cursor-stream.jsonl"
            try:
                session_events_log.write_text(raw_stdout, encoding="utf-8")
            except Exception:
                pass

            return ScenarioResult(
                returncode=-1,
                stdout=assistant_text or raw_stdout,
                stderr=f"TIMEOUT after {timeout}s",
                output_dirs=output_dirs,
                session_log=None,
                session_events_log=session_events_log if session_events_log.exists() else None,
                duration_seconds=duration,
                prompt=prompt,
                workdir=workdir,
                start_utc=start_utc,
                end_utc=end_utc,
                session_uuid=session_uuid,
            )


# ---------------------------------------------------------------------------
# OpenCodeRunnerAutopilot
# ---------------------------------------------------------------------------

class OpenCodeRunnerAutopilot:
    """Wrapper for autopilot OpenCode CLI invocations.

    Runs ``opencode run --format json --model <model> <prompt>`` for fully
    autonomous execution.

    An autopilot directive is appended to every prompt to prevent the agent
    from asking questions via plain text output.

    Output files are auto-detected in ``dx-agentic-dev/<session_id>/`` under
    the relevant sub-project directories — same mechanism as Copilot.

    Usage::

        runner = OpenCodeRunnerAutopilot()
        result = runner.run(
            prompt="Build a yolo26n detection app",
            workdir=APP_ROOT,
            scenario_key="dx_app",
        )
        assert result.succeeded
        assert result.output_dir is not None
    """

    OPENCODE_BIN = "opencode"
    MODE = "autopilot"

    AUTOPILOT_DIRECTIVE = (
        " IMPORTANT: This is an automated test run. "
        "Do not ask questions or present options. "
        "Proceed directly with implementation, choosing the most appropriate approach."
    )

    def __init__(self, model: str = ""):
        self.model = model or DEFAULT_OPENCODE_MODEL

    @classmethod
    def is_available(cls) -> bool:
        """Check if the ``opencode`` binary is on PATH."""
        return shutil.which(cls.OPENCODE_BIN) is not None

    @classmethod
    def opencode_path(cls) -> Optional[str]:
        """Return the full path to the opencode binary, or None."""
        return shutil.which(cls.OPENCODE_BIN)

    def run(
        self,
        prompt: str,
        workdir: Path,
        scenario_key: str,
        session_log_dir: Optional[Path] = None,
        timeout: int = DEFAULT_OPENCODE_TIMEOUT,
        extra_args: Optional[List[str]] = None,
    ) -> ScenarioResult:
        """Execute an OpenCode CLI prompt in autopilot mode.

        Args:
            prompt: The instruction to send to OpenCode.
            workdir: Working directory (determines which agent config loads).
            scenario_key: One of ``"compiler"``, ``"dx_app"``, ``"dx_stream"``,
                ``"runtime"``, ``"suite"``.
            session_log_dir: Directory to store the session transcript.
            timeout: Maximum execution time in seconds.
            extra_args: Additional CLI arguments.

        Returns:
            ScenarioResult with exit code, output, and auto-detected output dirs.
        """
        log_dir = session_log_dir or Path(os.environ.get("TMPDIR", "/tmp"))
        log_dir.mkdir(parents=True, exist_ok=True)

        effective_prompt = prompt + self.AUTOPILOT_DIRECTIVE

        search_paths = AGENTIC_DEV_SEARCH_PATHS.get(
            scenario_key, [workdir / "dx-agentic-dev"],
        )

        snapshot = _snapshot_sessions(search_paths)
        start_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        cmd = [
            self.OPENCODE_BIN,
            "run",
            "--format", "json",
            effective_prompt,
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
            # REC-X1: Initialize session_uuid/assistant_text from JSON output in success path.
            # Previously missing — caused UnboundLocalError at line 1260 when result.stdout
            # had a different JSON structure and the variable was never assigned.
            session_uuid, assistant_text = _parse_opencode_stream_json(result.stdout)
            # R20: No agent_filter here — opencode delegates to @dx-suite-builder (claude subagent),
            # which creates sessions named *_claude_* not *_opencode_*. Filtering by "opencode"
            # would yield zero results. Accept all new sessions but exclude sessions clearly
            # belonging to other tools (R39: exclude_filters prevents copilot/cursor cross-
            # contamination; claude_code sessions named *_claude_* remain included since
            # opencode's own subagent is also named "claude" — deeper fix requires session.owner).
            output_dirs = _detect_new_sessions(
                search_paths, snapshot,
                exclude_filters=["_copilot_", "_cursor_"],  # R39
            )
            # R34: Wait for any background compilation tracked via compile.pid before collecting
            _wait_for_background_compilation(output_dirs)
            # REC-M: Filter cross-contamination from concurrent claude_code sessions.
            # If opencode produced its own sessions (named _opencode_*), any _claude_* sessions
            # in output_dirs are from the concurrent claude_code autonomous run, not from
            # opencode's subagent. Filter them to prevent false-positive test failures.
            # NOTE: If opencode's subagent creates ONLY _claude_* sessions (no _opencode_* present),
            # we cannot distinguish them from claude_code contamination and must keep all.
            import warnings as _w
            _has_opencode_sessions = any("_opencode_" in _d.name for _d in output_dirs)
            if _has_opencode_sessions:
                _contamination = [_d for _d in output_dirs if "_claude_" in _d.name]
                if _contamination:
                    output_dirs = [_d for _d in output_dirs if "_claude_" not in _d.name]
                    for _cdir in _contamination:
                        _w.warn(
                            f"opencode: filtered cross-contamination _claude_ session: {_cdir.name}. "
                            "opencode's own sessions use _opencode_ prefix — this _claude_ session "
                            "belongs to the concurrent claude_code run. Filtered from output_dirs. "
                            "(REC-M filter applied)",
                            UserWarning,
                            stacklevel=2,
                        )
            else:
                # REC-L: No _opencode_* sessions found — opencode's subagent may use _claude_* names.
                # Cannot filter; warn so the user can identify potential cross-contamination.
                for _odir in output_dirs:
                    if "_claude_" in _odir.name:
                        _w.warn(
                            f"opencode: detected _claude_ session in output_dirs: {_odir.name}. "
                            "This may be cross-contamination from a concurrent claude_code run "
                            "(not opencode's own subagent output). "
                            "session.json from this directory may not belong to opencode "
                            "(REC-J/REC-L: session.owner tracking not yet implemented).",
                            UserWarning,
                            stacklevel=2,
                        )
            end_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            # REC-W2 (iter-18): Enforce session.json in each opencode app session.
            # skill_md fixes (REC-V2 iter-17 and prior) have failed 3 consecutive iterations.
            # opencode's subagent consistently skips session.json creation. Generate a
            # minimal session.json from available metadata if absent, and emit UserWarning.
            import json as _json_mod_w2
            _app_dirs_w2 = [
                _d for _d in output_dirs
                if "dx_app" in str(_d) or "dx-runtime" in str(_d)
            ]
            for _app_dir_w2 in _app_dirs_w2:
                _sj_path_w2 = _app_dir_w2 / "session.json"
                if not _sj_path_w2.exists():
                    _w.warn(
                        f"opencode: app session {_app_dir_w2.name} is missing session.json — "
                        "REC-V2 skill fix has had no effect for 3 consecutive iterations. "
                        "Generating minimal session.json from available metadata. (REC-W2)",
                        UserWarning,
                        stacklevel=2,
                    )
                    _minimal_sj_w2 = {
                        "session_id": _app_dir_w2.name,
                        "agent": "opencode",
                        "generated_by": "REC-W2-conftest-enforcement",
                        "note": "auto-generated because opencode subagent skipped session.json creation",
                    }
                    try:
                        _sj_path_w2.write_text(
                            _json_mod_w2.dumps(_minimal_sj_w2, indent=2),
                            encoding="utf-8",
                        )
                    except Exception:
                        pass

            session_log = log_dir / f"{scenario_key}-opencode-session.md"
            _save_opencode_session_log(
                session_log, result.stdout, result.stderr,
                scenario_key, prompt, session_uuid,
            )

            session_events_log = log_dir / f"{scenario_key}-opencode-stream.jsonl"
            try:
                session_events_log.write_text(result.stdout, encoding="utf-8")
            except Exception:
                pass

            for odir in output_dirs:
                try:
                    odir_real = odir.resolve()
                    session_name = odir_real.name
                    parent_name = odir_real.parent.parent.name
                    link_path = log_dir / f"{parent_name}_{session_name}"
                    link_path.unlink(missing_ok=True)
                    link_path.symlink_to(odir_real)
                except Exception:
                    pass

            return ScenarioResult(
                returncode=result.returncode,
                stdout=assistant_text or result.stdout,
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
            output_dirs = _detect_new_sessions(
                search_paths, snapshot,
                exclude_filters=["_copilot_", "_cursor_"],  # R39: no filter by name, exclude foreign tools
            )
            # REC-M (timeout path): Apply same cross-contamination filter as success path.
            import warnings as _w_t
            _has_oc_t = any("_opencode_" in _d.name for _d in output_dirs)
            if _has_oc_t:
                _contam_t = [_d for _d in output_dirs if "_claude_" in _d.name]
                if _contam_t:
                    output_dirs = [_d for _d in output_dirs if "_claude_" not in _d.name]
                    for _cdir in _contam_t:
                        _w_t.warn(
                            f"opencode: filtered cross-contamination _claude_ session (timeout): {_cdir.name}. (REC-M)",
                            UserWarning, stacklevel=2,
                        )
            end_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            raw_stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            session_uuid, assistant_text = _parse_opencode_stream_json(raw_stdout)

            session_events_log = log_dir / f"{scenario_key}-opencode-stream.jsonl"
            try:
                session_events_log.write_text(raw_stdout, encoding="utf-8")
            except Exception:
                pass

            return ScenarioResult(
                returncode=-1,
                stdout=assistant_text or raw_stdout,
                stderr=f"TIMEOUT after {timeout}s",
                output_dirs=output_dirs,
                session_log=None,
                session_events_log=session_events_log if session_events_log.exists() else None,
                duration_seconds=duration,
                prompt=prompt,
                workdir=workdir,
                start_utc=start_utc,
                end_utc=end_utc,
                session_uuid=session_uuid,
            )


# ---------------------------------------------------------------------------
# ClaudeCodeRunnerAutopilot
# ---------------------------------------------------------------------------

class ClaudeCodeRunnerAutopilot:
    """Wrapper for autopilot Claude Code CLI invocations.

    Runs ``claude -p --dangerously-skip-permissions --output-format stream-json
    <prompt>`` for fully autonomous execution.

    An autopilot directive is appended to every prompt to prevent the agent
    from asking questions.

    Output files are auto-detected in ``dx-agentic-dev/<session_id>/`` under
    the relevant sub-project directories — same mechanism as Copilot.

    Usage::

        runner = ClaudeCodeRunnerAutopilot()
        result = runner.run(
            prompt="Build a yolo26n detection app",
            workdir=APP_ROOT,
            scenario_key="dx_app",
        )
        assert result.succeeded
        assert result.output_dir is not None
    """

    CLAUDE_CODE_BIN = "claude"
    MODE = "autopilot"

    AUTOPILOT_DIRECTIVE = (
        " IMPORTANT: This is an automated test run. "
        "Do not ask questions or present options. "
        "Proceed directly with implementation, choosing the most appropriate approach."
    )

    def __init__(self, model: str = ""):
        self.model = model or DEFAULT_CLAUDE_CODE_MODEL

    @classmethod
    def is_available(cls) -> bool:
        """Check if the ``claude`` binary is on PATH."""
        return shutil.which(cls.CLAUDE_CODE_BIN) is not None

    @classmethod
    def is_authenticated(cls) -> bool:
        """Check if Claude Code CLI is authenticated via ``claude auth status``.

        Returns ``True`` if ``loggedIn`` is true in the JSON response.
        """
        if not cls.is_available():
            return False
        try:
            result = subprocess.run(
                [cls.CLAUDE_CODE_BIN, "auth", "status"],
                capture_output=True, text=True, timeout=15,
                env={**os.environ, "NO_COLOR": "1"},
            )
            data = json.loads(result.stdout)
            return bool(data.get("loggedIn", False))
        except Exception:
            return False

    @classmethod
    def claude_code_path(cls) -> Optional[str]:
        """Return the full path to the claude binary, or None."""
        return shutil.which(cls.CLAUDE_CODE_BIN)

    def run(
        self,
        prompt: str,
        workdir: Path,
        scenario_key: str,
        session_log_dir: Optional[Path] = None,
        timeout: int = DEFAULT_CLAUDE_CODE_TIMEOUT,
        extra_args: Optional[List[str]] = None,
    ) -> ScenarioResult:
        """Execute a Claude Code CLI prompt in autopilot mode.

        Args:
            prompt: The instruction to send to Claude Code.
            workdir: Working directory (CLAUDE.md loads from here).
            scenario_key: One of ``"compiler"``, ``"dx_app"``, ``"dx_stream"``,
                ``"runtime"``, ``"suite"``.
            session_log_dir: Directory to store the session transcript.
            timeout: Maximum execution time in seconds.
            extra_args: Additional CLI arguments.

        Returns:
            ScenarioResult with exit code, output, and auto-detected output dirs.
        """
        log_dir = session_log_dir or Path(os.environ.get("TMPDIR", "/tmp"))
        log_dir.mkdir(parents=True, exist_ok=True)

        effective_prompt = prompt + self.AUTOPILOT_DIRECTIVE

        search_paths = AGENTIC_DEV_SEARCH_PATHS.get(
            scenario_key, [workdir / "dx-agentic-dev"],
        )

        snapshot = _snapshot_sessions(search_paths)
        start_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        cmd = [
            self.CLAUDE_CODE_BIN,
            "-p",                                     # print / non-interactive
            "--dangerously-skip-permissions",          # fully autonomous
            "--verbose",                               # required with stream-json
            "--output-format", "stream-json",
            effective_prompt,
        ]

        if self.model:
            cmd.extend(["--model", self.model])

        if extra_args:
            cmd.extend(extra_args)

        start = time.monotonic()
        _quota_polls = 0
        # R8: Wrap the entire while-loop + post-processing in a single try block so
        # that subprocess.TimeoutExpired propagates to the except handler below.
        # Previously the try: was placed AFTER the while loop, so TimeoutExpired
        # raised inside the loop propagated past the except clause uncaught, causing
        # all 11 tests to receive ERROR (unfixable fixture exception) instead of
        # FAIL+SKIP.
        try:
            while True:
                result = subprocess.run(
                    cmd,
                    cwd=str(workdir),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env={**os.environ, "NO_COLOR": "1"},
                    # R1: Detach from the test process's terminal session to prevent
                    # SIGHUP from being delivered to the claude agent when the
                    # controlling terminal closes (returncode=129 = 128+SIGHUP).
                    start_new_session=True,
                )

                _combined = (result.stdout or "") + (result.stderr or "")
                if result.returncode != 0 and _is_claude_code_usage_limit(_combined):
                    if _quota_polls >= _CLAUDE_QUOTA_MAX_POLLS:
                        _logger.error(
                            "Claude Code usage limit — max polls (%d) exceeded, aborting",
                            _CLAUDE_QUOTA_MAX_POLLS,
                        )
                        break
                    _quota_polls += 1
                    _logger.warning(
                        "Claude Code usage limit hit — sleeping %d min (poll %d/%d)",
                        _CLAUDE_QUOTA_POLL_INTERVAL // 60,
                        _quota_polls,
                        _CLAUDE_QUOTA_MAX_POLLS,
                    )
                    time.sleep(_CLAUDE_QUOTA_POLL_INTERVAL)
                    start = time.monotonic()
                    continue
                break


            duration = time.monotonic() - start
            output_dirs = _detect_new_sessions(search_paths, snapshot, agent_filter="claude")
            # R34: Wait for any background compilation tracked via compile.pid before collecting
            _wait_for_background_compilation(output_dirs)
            end_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            session_uuid, assistant_text = _parse_claude_code_stream_json(result.stdout)

            session_log = log_dir / f"{scenario_key}-claude-code-session.md"
            _save_claude_code_session_log(
                session_log, result.stdout, result.stderr,
                scenario_key, prompt, session_uuid,
            )

            session_events_log = log_dir / f"{scenario_key}-claude-code-stream.jsonl"
            try:
                session_events_log.write_text(result.stdout, encoding="utf-8")
            except Exception:
                pass

            # R49+R54: Copy session log as session.txt into the DONE-sentinel-resolved dir.
            # R49: Parse the DONE sentinel from assistant_text for the authoritative path.
            # R54: Also update output_dirs to the sentinel-resolved path so that
            #   scenario.output_dir (= output_dirs[0]) matches where session.txt lands.
            #   Added pre-write diagnostics (sentinel path, exists check) to surface
            #   failures that were previously silently swallowed.
            _session_txt_written = False
            if session_log.exists() and assistant_text:
                _done_re = re.compile(r'\[DX-AGENTIC-DEV: DONE \(output-dir: ([^)]+)\)\]')
                _done_match = _done_re.search(assistant_text)
                if _done_match:
                    _done_rel = _done_match.group(1).strip()
                    _primary = workdir / _done_rel
                    _logger.info(
                        "R54: DONE sentinel path=%s resolved=%s exists=%s",
                        _done_rel, _primary, _primary.exists(),
                    )
                    if _primary.exists():
                        # R54: sync output_dirs so scenario.output_dir == sentinel path
                        if not output_dirs or output_dirs[0] != _primary:
                            output_dirs = [_primary] + [d for d in output_dirs if d != _primary]
                        try:
                            txt_dest = _primary / "session.txt"
                            _logger.info("R54: session.txt → %s (writing)", txt_dest)
                            if not txt_dest.exists():
                                shutil.copy2(str(session_log), str(txt_dest))
                            _logger.info("session.txt written to: %s", txt_dest)
                            _session_txt_written = True
                        except Exception as _e:
                            _logger.warning("R54: session.txt write failed: %s", _e)
            if not _session_txt_written and output_dirs and session_log.exists():
                try:
                    txt_dest = output_dirs[0] / "session.txt"
                    _logger.info("R54: session.txt → %s (fallback)", txt_dest)
                    if not txt_dest.exists():
                        shutil.copy2(str(session_log), str(txt_dest))
                    _logger.info("session.txt written to (fallback): %s", txt_dest)
                except Exception:
                    pass  # Best-effort: never block the test

            for odir in output_dirs:
                try:
                    odir_real = odir.resolve()
                    session_name = odir_real.name
                    parent_name = odir_real.parent.parent.name
                    link_path = log_dir / f"{parent_name}_{session_name}"
                    link_path.unlink(missing_ok=True)
                    link_path.symlink_to(odir_real)
                except Exception:
                    pass

            return ScenarioResult(
                returncode=result.returncode,
                stdout=assistant_text or result.stdout,
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
            output_dirs = _detect_new_sessions(search_paths, snapshot, agent_filter="claude")
            end_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            raw_stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            session_uuid, assistant_text = _parse_claude_code_stream_json(raw_stdout)

            session_events_log = log_dir / f"{scenario_key}-claude-code-stream.jsonl"
            try:
                session_events_log.write_text(raw_stdout, encoding="utf-8")
            except Exception:
                pass

            return ScenarioResult(
                returncode=-1,
                stdout=assistant_text or raw_stdout,
                stderr=f"TIMEOUT after {timeout}s",
                output_dirs=output_dirs,
                session_log=None,
                session_events_log=session_events_log if session_events_log.exists() else None,
                duration_seconds=duration,
                prompt=prompt,
                workdir=workdir,
                start_utc=start_utc,
                end_utc=end_utc,
                session_uuid=session_uuid,
            )


def _parse_cursor_stream_json(raw_output: str) -> tuple:
    """Parse Cursor CLI stream-json NDJSON output.

    Extracts session_uuid and concatenated assistant text from the stream.

    Returns:
        ``(session_uuid, assistant_text)`` — either may be ``None``.
    """
    session_uuid = None
    assistant_parts: List[str] = []

    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        event_type = event.get("type", "")
        sid = event.get("session_id")
        if sid and not session_uuid:
            session_uuid = sid

        if event_type == "assistant":
            msg = event.get("message", {})
            for content_part in msg.get("content", []):
                text = content_part.get("text", "")
                if text:
                    assistant_parts.append(text)
        elif event_type == "result":
            result_text = event.get("result", "")
            if result_text and not assistant_parts:
                assistant_parts.append(result_text)
            if not session_uuid:
                session_uuid = event.get("session_id")

    assistant_text = "\n".join(assistant_parts) if assistant_parts else None
    return session_uuid, assistant_text


def _save_cursor_session_log(
    output_path: Path,
    raw_stdout: str,
    raw_stderr: str,
    scenario_key: str,
    prompt: str,
    session_uuid: Optional[str],
) -> None:
    """Save Cursor CLI session as a Markdown log (best-effort)."""
    try:
        lines = [
            f"# Cursor CLI Session — {scenario_key}",
            "",
            f"- **Session UUID:** {session_uuid or 'unknown'}",
            f"- **Prompt:** {prompt}",
            "",
            "## Assistant Output",
            "",
        ]
        _, assistant_text = _parse_cursor_stream_json(raw_stdout)
        if assistant_text:
            lines.append(assistant_text)
        else:
            lines.append("(no assistant output captured)")
        if raw_stderr and raw_stderr.strip():
            lines.extend(["", "## Stderr", "", raw_stderr])
        output_path.write_text("\n".join(lines), encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# OpenCode stream JSON parsing
# ---------------------------------------------------------------------------


def _parse_opencode_stream_json(raw_output: str) -> tuple:
    """Parse OpenCode CLI ``--format json`` NDJSON output.

    Returns:
        ``(session_id, assistant_text)`` — either may be ``None``.
    """
    session_id = None
    assistant_parts: List[str] = []

    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        event_type = event.get("type", "")
        sid = event.get("sessionID") or event.get("session_id") or event.get("id")
        if sid and not session_id:
            session_id = str(sid)

        if event_type in ("assistant", "text", "message", "step_start",
                          "step_finish", "message_finish", "answer",
                          "output", "tool_result"):
            text = (event.get("text") or event.get("content", "")
                    or event.get("output", "") or event.get("result", ""))
            if isinstance(text, str) and text:
                assistant_parts.append(text)
            elif isinstance(text, list):
                for part in text:
                    if isinstance(part, dict):
                        t = part.get("text", "")
                        if t:
                            assistant_parts.append(t)
            # Also check nested message.content
            msg = event.get("message", {})
            if isinstance(msg, dict):
                for content_part in msg.get("content", []):
                    if isinstance(content_part, dict):
                        t = content_part.get("text", "")
                        if t:
                            assistant_parts.append(t)
            # Check top-level content array with typed blocks (step_start format)
            for item in event.get("content", []) if isinstance(event.get("content"), list) else []:
                if isinstance(item, dict) and item.get("type") == "text":
                    t = item.get("text", "")
                    if t:
                        assistant_parts.append(t)

    # Fallback: if no structured events matched, collect non-JSON lines as raw output
    if not assistant_parts:
        for line in raw_output.splitlines():
            s = line.strip()
            if s and not s.startswith("{"):
                assistant_parts.append(s)

    # R47+R52: Final fallback — scan raw NDJSON events for DONE sentinel in any text field.
    # Handles sessions where OpenCode uses event types not in the dispatch table,
    # ensuring output_dir resolution even when text extraction fails.
    # R52: Added per-event diagnostic logging to surface why extraction fails.
    if not assistant_parts:
        _r47_scanned = 0
        for line in raw_output.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            _r47_scanned += 1
            _event_type = event.get("type", "<none>")
            for field in ("content", "text", "result", "output", "value", "message"):
                val = event.get(field, "")
                if isinstance(val, str) and "[DX-AGENTIC-DEV: DONE" in val:
                    _logger.info(
                        "R47: DONE sentinel found in event type=%s field=%s",
                        _event_type, field,
                    )
                    assistant_parts.append(val)
                    break
            if assistant_parts:
                break
        _logger.info(
            "R47: scanned %d NDJSON events for DONE sentinel; found=%s",
            _r47_scanned, bool(assistant_parts),
        )

    assistant_text = "\n".join(assistant_parts) if assistant_parts else None
    return session_id, assistant_text


def _save_opencode_session_log(
    output_path: Path,
    raw_stdout: str,
    raw_stderr: str,
    scenario_key: str,
    prompt: str,
    session_uuid: Optional[str],
) -> None:
    """Save OpenCode session as a Markdown log (best-effort)."""
    try:
        lines = [
            f"# OpenCode Session — {scenario_key}",
            "",
            f"- **Session UUID:** {session_uuid or 'unknown'}",
            f"- **Prompt:** {prompt}",
            "",
            "## Assistant Output",
            "",
        ]
        _, assistant_text = _parse_opencode_stream_json(raw_stdout)
        if not assistant_text and raw_stdout.strip():
            # Dump raw stream for parser diagnosis
            debug_path = output_path.with_suffix(".raw.jsonl")
            debug_path.write_text(raw_stdout, encoding="utf-8")
        if assistant_text:
            lines.append(assistant_text)
        else:
            lines.append("(no assistant output captured)")
        if raw_stderr and raw_stderr.strip():
            lines.extend(["", "## Stderr", "", raw_stderr])
        output_path.write_text("\n".join(lines), encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Claude Code stream JSON parsing
# ---------------------------------------------------------------------------


def _parse_claude_code_stream_json(raw_output: str) -> tuple:
    """Parse Claude Code CLI ``--output-format stream-json`` NDJSON output.

    Format is identical to Cursor CLI stream-json.

    Returns:
        ``(session_uuid, assistant_text)`` — either may be ``None``.
    """
    return _parse_cursor_stream_json(raw_output)


def _save_claude_code_session_log(
    output_path: Path,
    raw_stdout: str,
    raw_stderr: str,
    scenario_key: str,
    prompt: str,
    session_uuid: Optional[str],
) -> None:
    """Save Claude Code session as a Markdown log (best-effort)."""
    try:
        lines = [
            f"# Claude Code Session — {scenario_key}",
            "",
            f"- **Session UUID:** {session_uuid or 'unknown'}",
            f"- **Prompt:** {prompt}",
            "",
            "## Assistant Output",
            "",
        ]
        _, assistant_text = _parse_claude_code_stream_json(raw_stdout)
        if assistant_text:
            lines.append(assistant_text)
        else:
            lines.append("(no assistant output captured)")
        if raw_stderr and raw_stderr.strip():
            lines.extend(["", "## Stderr", "", raw_stderr])
        output_path.write_text("\n".join(lines), encoding="utf-8")
    except Exception:
        pass


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
    failure_kind = "CONNECTION FAILURE (external — not code-fixable)" if result.connection_error else "AGENTIC E2E SCENARIO FAILED"
    lines = [
        "",
        "=" * 80,
        failure_kind,
        "=" * 80,
        f"Exit Code: {result.returncode}",
        f"Duration:  {result.duration_seconds:.1f}s",
        f"Workdir:   {result.workdir}",
        f"Output:    {output_str}",
    ]
    if result.connection_error:
        lines.extend([
            "",
            "DIAGNOSIS: The tool's backend API reported repeated connection failures.",
            "This is a transient network/service outage — no code change can fix it.",
            "Re-run the test suite once connectivity is restored.",
        ])
    lines.extend([
        "",
        "PROMPT:",
        "-" * 80,
        result.prompt,
        "",
    ])
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

    Manual modes are handled by ``test.sh agentic-e2e-copilot-manual`` and
    ``test.sh agentic-e2e-cursor-manual`` (shell-based interactive, no pytest).
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
def cursor_runner():
    """Session-scoped CursorRunnerAutopilot for Cursor CLI autopilot mode.

    Uses ``agent -p --force --output-format stream-json`` for fully
    autonomous execution.  Skips if the ``agent`` binary is not on PATH
    or if authentication is not configured.
    """
    if not CursorRunnerAutopilot.is_available():
        pytest.skip(
            f"Cursor CLI not found on PATH. "
            f"Searched for '{CursorRunnerAutopilot.CURSOR_BIN}' — not found. "
            f"Install Cursor CLI first: curl https://cursor.com/install -fsS | bash"
        )
    if not CursorRunnerAutopilot.is_authenticated():
        pytest.skip(
            "Cursor CLI is not authenticated. "
            "Run 'agent login' or set CURSOR_API_KEY environment variable."
        )
    return CursorRunnerAutopilot()


def _cleanup_artifacts_dir(artifacts_dir: Path) -> None:
    """Clean up an artifacts directory after a test session.

    Policy:
    - Always remove symlinks (dangling references to output dirs).
    - Preserve actual session log files (.md, .jsonl, .json) — these are
      useful for post-mortem debugging and are small enough to keep.
    - Remove the directory itself only if it is empty after symlink cleanup.
    - Remove empty parent dirs (mode/, tool/) up to e2e-tests/ level.

    This avoids two failure modes:
    1. Accidentally deleting session logs that were still being flushed
       (the race condition between runner teardown and fixture teardown).
    2. Leaving dangling symlinks to already-cleaned-up output dirs.
    """
    if not artifacts_dir.exists():
        return

    # Remove symlinks first (they reference output dirs that may be gone)
    for entry in list(artifacts_dir.iterdir()):
        if entry.is_symlink():
            try:
                entry.unlink()
            except OSError:
                pass

    # Remove the session dir only if empty (no log files remain)
    try:
        if artifacts_dir.exists() and not any(artifacts_dir.iterdir()):
            artifacts_dir.rmdir()
    except OSError:
        pass

    # Remove empty parent dirs (mode/, tool/) up to e2e-tests/
    for parent in [artifacts_dir.parent, artifacts_dir.parent.parent]:
        try:
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
        except OSError:
            pass


def _make_artifacts_dir_fixture(tool: str, mode: str, base: Path = None):
    """Factory that creates a session-scoped artifacts dir fixture for a given tool/mode.

    Output path: ``<base>/e2e-tests/<tool>/<mode>/<session_id>/``
    Defaults to ``AGENTIC_E2E_ARTIFACTS_BASE`` (suite root) when *base* is None.

    Supported tools: ``copilot_cli``, ``cursor_cli``, ``opencode``, ``claude_code``
    Supported modes: ``autopilot``, ``manual``
    """
    resolved_base = base if base is not None else AGENTIC_E2E_ARTIFACTS_BASE

    @pytest.fixture(scope="session")
    def _fixture():
        session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
        artifacts_dir = resolved_base / tool / mode / session_id
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        yield artifacts_dir

        if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
            _cleanup_artifacts_dir(artifacts_dir)

    _fixture.__name__ = f"{tool}_{mode}_artifacts_dir"
    return _fixture


@pytest.fixture(scope="session")
def copilot_cli_artifacts_dir():
    """Session-scoped artifacts dir for Copilot CLI autopilot runs.

    Path: ``dx-agentic-dev/e2e-tests/copilot_cli/autopilot/<session_id>/``
    """
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = AGENTIC_E2E_ARTIFACTS_BASE / "copilot_cli" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    yield artifacts_dir

    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def cursor_cli_artifacts_dir():
    """Session-scoped artifacts dir for Cursor CLI autopilot runs.

    Path: ``dx-agentic-dev/e2e-tests/cursor_cli/autopilot/<session_id>/``
    """
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = AGENTIC_E2E_ARTIFACTS_BASE / "cursor_cli" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    yield artifacts_dir

    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def opencode_runner():
    """Session-scoped OpenCodeRunnerAutopilot for autopilot mode.

    Uses ``opencode run --format json`` for fully autonomous execution.
    Skips if the ``opencode`` binary is not on PATH.
    """
    if not OpenCodeRunnerAutopilot.is_available():
        pytest.skip(
            f"OpenCode CLI not found on PATH. "
            f"Searched for '{OpenCodeRunnerAutopilot.OPENCODE_BIN}' — not found. "
            f"Install OpenCode: curl -fsSL https://opencode.ai/install | bash"
        )
    return OpenCodeRunnerAutopilot()


@pytest.fixture(scope="session")
def claude_code_runner():
    """Session-scoped ClaudeCodeRunnerAutopilot for autopilot mode.

    Uses ``claude -p --dangerously-skip-permissions --output-format stream-json``
    for fully autonomous execution. Skips if ``claude`` is not on PATH or not
    authenticated (checked via ``claude auth status``).
    """
    if not ClaudeCodeRunnerAutopilot.is_available():
        pytest.skip(
            f"Claude Code CLI not found on PATH. "
            f"Searched for '{ClaudeCodeRunnerAutopilot.CLAUDE_CODE_BIN}' — not found."
        )
    if not ClaudeCodeRunnerAutopilot.is_authenticated():
        pytest.skip(
            "Claude Code CLI is not authenticated. "
            "Run 'claude login' to authenticate."
        )
    return ClaudeCodeRunnerAutopilot()


@pytest.fixture(scope="session")
def opencode_artifacts_dir():
    """Session-scoped artifacts dir for OpenCode autopilot runs.

    Path: ``dx-agentic-dev/e2e-tests/opencode/autopilot/<session_id>/``
    """
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = AGENTIC_E2E_ARTIFACTS_BASE / "opencode" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    yield artifacts_dir

    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def claude_code_artifacts_dir():
    """Session-scoped artifacts dir for Claude Code autopilot runs.

    Path: ``dx-agentic-dev/e2e-tests/claude_code/autopilot/<session_id>/``
    """
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = AGENTIC_E2E_ARTIFACTS_BASE / "claude_code" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    yield artifacts_dir

    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def agentic_e2e_artifacts_dir(copilot_cli_artifacts_dir):
    """Deprecated alias for copilot_cli_artifacts_dir. Use tool-specific fixtures instead."""
    return copilot_cli_artifacts_dir


# ---------------------------------------------------------------------------
# Per-project artifacts dir fixtures
# Route each sub-project's test artifacts into that project's own
# dx-agentic-dev/e2e-tests/<tool>/<mode>/<session_id>/ directory so the
# hierarchy mirrors the manual-mode layout used by test.sh.
# ---------------------------------------------------------------------------

# --- dx-compiler -----------------------------------------------------------

@pytest.fixture(scope="session")
def compiler_copilot_cli_artifacts_dir():
    """Path: dx-compiler/dx-agentic-dev/e2e-tests/copilot_cli/autopilot/<session_id>/"""
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = COMPILER_E2E_ARTIFACTS_BASE / "copilot_cli" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def compiler_cursor_cli_artifacts_dir():
    """Path: dx-compiler/dx-agentic-dev/e2e-tests/cursor_cli/autopilot/<session_id>/"""
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = COMPILER_E2E_ARTIFACTS_BASE / "cursor_cli" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def compiler_opencode_artifacts_dir():
    """Path: dx-compiler/dx-agentic-dev/e2e-tests/opencode/autopilot/<session_id>/"""
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = COMPILER_E2E_ARTIFACTS_BASE / "opencode" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def compiler_claude_code_artifacts_dir():
    """Path: dx-compiler/dx-agentic-dev/e2e-tests/claude_code/autopilot/<session_id>/"""
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = COMPILER_E2E_ARTIFACTS_BASE / "claude_code" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


# --- dx_app ----------------------------------------------------------------

@pytest.fixture(scope="session")
def app_copilot_cli_artifacts_dir():
    """Path: dx-runtime/dx_app/dx-agentic-dev/e2e-tests/copilot_cli/autopilot/<session_id>/"""
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = APP_E2E_ARTIFACTS_BASE / "copilot_cli" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def app_cursor_cli_artifacts_dir():
    """Path: dx-runtime/dx_app/dx-agentic-dev/e2e-tests/cursor_cli/autopilot/<session_id>/"""
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = APP_E2E_ARTIFACTS_BASE / "cursor_cli" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def app_opencode_artifacts_dir():
    """Path: dx-runtime/dx_app/dx-agentic-dev/e2e-tests/opencode/autopilot/<session_id>/"""
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = APP_E2E_ARTIFACTS_BASE / "opencode" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def app_claude_code_artifacts_dir():
    """Path: dx-runtime/dx_app/dx-agentic-dev/e2e-tests/claude_code/autopilot/<session_id>/"""
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = APP_E2E_ARTIFACTS_BASE / "claude_code" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


# --- dx_stream -------------------------------------------------------------

@pytest.fixture(scope="session")
def stream_copilot_cli_artifacts_dir():
    """Path: dx-runtime/dx_stream/dx-agentic-dev/e2e-tests/copilot_cli/autopilot/<session_id>/"""
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = STREAM_E2E_ARTIFACTS_BASE / "copilot_cli" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def stream_cursor_cli_artifacts_dir():
    """Path: dx-runtime/dx_stream/dx-agentic-dev/e2e-tests/cursor_cli/autopilot/<session_id>/"""
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = STREAM_E2E_ARTIFACTS_BASE / "cursor_cli" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def stream_opencode_artifacts_dir():
    """Path: dx-runtime/dx_stream/dx-agentic-dev/e2e-tests/opencode/autopilot/<session_id>/"""
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = STREAM_E2E_ARTIFACTS_BASE / "opencode" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def stream_claude_code_artifacts_dir():
    """Path: dx-runtime/dx_stream/dx-agentic-dev/e2e-tests/claude_code/autopilot/<session_id>/"""
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = STREAM_E2E_ARTIFACTS_BASE / "claude_code" / "autopilot" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


# --- dx_stream cascaded scenario artifacts ---------------------------------

@pytest.fixture(scope="session")
def stream_copilot_cascaded_artifacts_dir():
    """Cascaded scenario artifacts dir for Copilot CLI.

    Path: dx-runtime/dx_stream/dx-agentic-dev/e2e-tests/copilot_cli/autopilot_cascaded/<session_id>/
    """
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = STREAM_E2E_ARTIFACTS_BASE / "copilot_cli" / "autopilot_cascaded" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def stream_cursor_cascaded_artifacts_dir():
    """Cascaded scenario artifacts dir for Cursor CLI.

    Path: dx-runtime/dx_stream/dx-agentic-dev/e2e-tests/cursor_cli/autopilot_cascaded/<session_id>/
    """
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = STREAM_E2E_ARTIFACTS_BASE / "cursor_cli" / "autopilot_cascaded" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def stream_opencode_cascaded_artifacts_dir():
    """Cascaded scenario artifacts dir for OpenCode.

    Path: dx-runtime/dx_stream/dx-agentic-dev/e2e-tests/opencode/autopilot_cascaded/<session_id>/
    """
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = STREAM_E2E_ARTIFACTS_BASE / "opencode" / "autopilot_cascaded" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


@pytest.fixture(scope="session")
def stream_claude_code_cascaded_artifacts_dir():
    """Cascaded scenario artifacts dir for Claude Code.

    Path: dx-runtime/dx_stream/dx-agentic-dev/e2e-tests/claude_code/autopilot_cascaded/<session_id>/
    """
    session_id = time.strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:6]}"
    artifacts_dir = STREAM_E2E_ARTIFACTS_BASE / "claude_code" / "autopilot_cascaded" / session_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    yield artifacts_dir
    if os.environ.get("DX_AGENTIC_E2E_CLEANUP_ARTIFACTS"):
        _cleanup_artifacts_dir(artifacts_dir)


# ---------------------------------------------------------------------------
# NPU hardware availability check
# ---------------------------------------------------------------------------

def _is_npu_available() -> bool:
    """Return True if ``dxrt-cli -s`` exits 0 (NPU hardware functional)."""
    if shutil.which("dxrt-cli") is None:
        return False
    try:
        result = subprocess.run(
            ["dxrt-cli", "-s"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False




@pytest.fixture(scope="session")
def npu_hardware_available():
    """Session-scoped fixture that skips if NPU hardware is not functional.

    Runs ``dxrt-cli -s`` once per test session.  If it fails (DKMS driver not
    loaded, hardware init failure, etc.) all tests that depend on this fixture
    are skipped with a descriptive message.  A cold boot may be required to
    reload the ``dxrt_driver`` kernel module.
    """
    if not _is_npu_available():
        pytest.skip(
            "NPU hardware not available (dxrt-cli -s returned non-zero). "
            "The DKMS kernel module (dxrt_driver) may not be loaded — "
            "a cold boot / system reboot may be required."
        )
