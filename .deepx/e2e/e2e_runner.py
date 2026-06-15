#!/usr/bin/env python3
"""
e2e_runner.py — Reusable multi-round E2E test runner for DEEPX Agent-Driven Dev.

Default execution model is SEQUENTIAL (one tool at a time) so per-tool
duration metrics are not skewed by NPU/CPU contention. Use --parallel to
run all tools concurrently when throughput matters more than measurement
fidelity.

Usage examples:
    # Run 5 rounds for all tools sequentially (default)
    python .deepx/e2e/e2e_runner.py --rounds 5

    # Run 5 rounds in parallel mode
    python .deepx/e2e/e2e_runner.py --rounds 5 --parallel

    # Run 5 rounds for specific tools only
    python .deepx/e2e/e2e_runner.py --rounds 5 --tools claude-code,copilot-cli

    # Run with thinking / high-reasoning mode
    python .deepx/e2e/e2e_runner.py --rounds 5 --thinking

    # Resume: auto-detect completed rounds and continue to target
    python .deepx/e2e/e2e_runner.py --rounds 5 --resume

    # Resume a specific previous run
    python .deepx/e2e/e2e_runner.py --rounds 5 --resume --run-id 20260521_100000

    # Show current run status (no --rounds needed)
    python .deepx/e2e/e2e_runner.py --status

    # List all previous runs
    python .deepx/e2e/e2e_runner.py --list

    # Gracefully stop the current run after the active round finishes
    python .deepx/e2e/e2e_runner.py --stop --run-id 20260521_100000

    # Abort the current run immediately
    python .deepx/e2e/e2e_runner.py --abort --run-id 20260521_100000 --force

    # Delete artifacts for round 3 of all tools
    python .deepx/e2e/e2e_runner.py --cleanup --round 3

    # Delete artifacts for round 3 of a specific tool set
    python .deepx/e2e/e2e_runner.py --cleanup --round 3 --tools claude-code

See .deepx/tests/README.md for full documentation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Optional Rich support for enhanced display
try:
    from rich.console import Console as RichConsole
    from rich.table import Table as RichTable
    from rich.text import Text as RichText
    from rich.panel import Panel as RichPanel
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = (SCRIPT_DIR / "../..").resolve()
TEST_SH = SCRIPT_DIR / "test.sh"
RESULTS_ROOT = REPO_ROOT / "dx-agent-dev/e2e-tests/results"
RUNNER_STATE_DIR = SCRIPT_DIR / "runner_state"

# ---------------------------------------------------------------------------
# Tool configuration
# ---------------------------------------------------------------------------

ALL_TOOLS: List[str] = [
    "claude-code",
    "copilot-cli",
    "cursor-cli",
    "opencode-cli",
    "codex-cli",
]

# test.sh command name for each tool
TOOL_CMD: Dict[str, str] = {
    "claude-code": "agent-driven-e2e-claude-code-autopilot",
    "copilot-cli": "agent-driven-e2e-copilot-cli-autopilot",
    "cursor-cli": "agent-driven-e2e-cursor-cli-autopilot",
    "opencode-cli": "agent-driven-e2e-opencode-cli-autopilot",
    "codex-cli": "agent-driven-e2e-codex-cli-autopilot",
}

# Thinking / high-reasoning mode env vars per tool
THINKING_ENV: Dict[str, Dict[str, str]] = {
    "claude-code": {"DX_AGENT_E2E_CLAUDE_CODE_EXTRA_ARGS": "--effort xhigh"},
    "copilot-cli": {"DX_AGENT_E2E_COPILOT_EXTRA_ARGS": "--effort xhigh"},
    "opencode-cli": {"DX_AGENT_E2E_OPENCODE_EXTRA_ARGS": "--variant high"},
    "codex-cli": {"DX_AGENT_E2E_CODEX_EXTRA_ARGS": '-c model_reasoning_effort="xhigh"'},
    "cursor-cli": {},  # quota exceeded; auto fallback, no thinking mode
}

# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

_state_lock = threading.Lock()
_abort_event = threading.Event()


class StopRequested(Exception):
    """Graceful stop requested via sentinel file."""


class AbortRequested(Exception):
    """Immediate abort requested via sentinel file or SIGTERM."""


class RunState:
    """Manages runner_state/<run_id>/state.json and provides thread-safe updates."""

    def __init__(
        self,
        run_id: str,
        target_rounds: int,
        tools: List[str],
        thinking: bool,
        mode: str = "sequential",
    ):
        self.run_id = run_id
        self.path = RUNNER_STATE_DIR / run_id / "state.json"
        self.log_dir = RUNNER_STATE_DIR / run_id / "logs"
        self.data: dict = {
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "target_rounds": target_rounds,
            "thinking": thinking,
            "mode": mode,
            "tools": tools,
            "runner_pid": None,
            "status": "pending",
            "tool_states": {
                t: {"completed": [], "in_progress": None, "status": "pending", "pid": None}
                for t in tools
            },
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.path)
        # Update "latest" symlink
        latest = RUNNER_STATE_DIR / "latest"
        latest.unlink(missing_ok=True)
        latest.symlink_to(self.run_id)

    @classmethod
    def load(cls, path: Path) -> "RunState":
        data = json.loads(path.read_text(encoding="utf-8"))
        _normalize_state_data(data)
        obj = cls.__new__(cls)
        obj.run_id = data["run_id"]
        obj.path = path
        obj.log_dir = path.parent / "logs"
        obj.data = data
        return obj

    @classmethod
    def find_latest(cls) -> Optional[Path]:
        """Return path to the most recent state.json, or None."""
        latest = RUNNER_STATE_DIR / "latest"
        if latest.is_symlink():
            target = RUNNER_STATE_DIR / latest.readlink()
            candidate = target / "state.json"
            if candidate.exists():
                return candidate
        # Fallback: newest by mtime
        candidates = sorted(
            (
                p
                for p in (RUNNER_STATE_DIR.glob("*/state.json") if RUNNER_STATE_DIR.exists() else [])
                if p.parent.name != "latest"
            ),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return candidates[0] if candidates else None

    # ------------------------------------------------------------------
    # Round tracking (thread-safe)
    # ------------------------------------------------------------------

    def mark_start(self, tool: str, round_num: int) -> None:
        with _state_lock:
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            self.data["tool_states"][tool]["in_progress"] = {
                "round": round_num,
                "start_utc": ts,
            }
            self.data["tool_states"][tool]["status"] = "running"
            self.save()

    def mark_done(
        self,
        tool: str,
        round_num: int,
        result_dir_name: Optional[str],
        exit_code: int,
        artifact_dirs: List[str],
    ) -> None:
        with _state_lock:
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            ts_state = self.data["tool_states"][tool]
            start_utc = (ts_state.get("in_progress") or {}).get("start_utc", ts)
            ts_state.setdefault("completed", []).append(
                {
                    "round": round_num,
                    "result_dir_name": result_dir_name,
                    "exit_code": exit_code,
                    "start_utc": start_utc,
                    "end_utc": ts,
                    "artifact_dirs": artifact_dirs,
                }
            )
            ts_state["in_progress"] = None
            ts_state["pid"] = None
            target = self.data["target_rounds"]
            done = len(ts_state["completed"])
            ts_state["status"] = "done" if done >= target else "running"
            self.save()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def completed_count(self, tool: str) -> int:
        return len(self.data["tool_states"].get(tool, {}).get("completed", []))

    def remaining(self, tool: str) -> int:
        return max(0, self.data["target_rounds"] - self.completed_count(tool))

    def next_round_num(self, tool: str) -> int:
        return self.completed_count(tool) + 1

    @property
    def target_rounds(self) -> int:
        return self.data["target_rounds"]

    @property
    def thinking(self) -> bool:
        return self.data.get("thinking", False)

    @property
    def tools(self) -> List[str]:
        return self.data.get("tools", ALL_TOOLS)


def _normalize_state_data(data: dict) -> None:
    data.setdefault("thinking", False)
    # Old state files (pre-sequential default) had no mode field. They were
    # written under the parallel-by-default era, so preserve that for legacy.
    data.setdefault("mode", "parallel")
    data.setdefault("tools", ALL_TOOLS)
    data.setdefault("runner_pid", None)
    data.setdefault("status", "pending")
    data.setdefault("tool_states", {})
    for tool in data.get("tools", ALL_TOOLS):
        ts = data["tool_states"].setdefault(tool, {})
        ts.setdefault("completed", [])
        ts.setdefault("in_progress", None)
        ts.setdefault("status", "pending")
        ts.setdefault("pid", None)


# ---------------------------------------------------------------------------
# Detect completed rounds from results/ (used for --resume without state.json)
# ---------------------------------------------------------------------------

def run_results_dir(run_id: str) -> Path:
    """Return the per-run results directory (results/<run_id>/)."""
    return RESULTS_ROOT / run_id


def detect_completed_from_results(
    tools: List[str], target_rounds: int, run_id: Optional[str] = None,
) -> Dict[str, List[dict]]:
    """Scan results/<run_id>/ and group completed rounds per tool by timestamp order.

    If run_id is None, returns empty dict — the new run-id layout requires an
    explicit run scope. Legacy flat results should be migrated via
    migrate_results_to_run_id.py before --resume.
    """
    per_tool: Dict[str, List[dict]] = {t: [] for t in tools}
    if not run_id:
        return per_tool
    run_dir = run_results_dir(run_id)
    if not run_dir.exists():
        return per_tool

    entries = sorted(run_dir.iterdir(), key=lambda p: p.name)
    for entry in entries:
        if not entry.is_dir():
            continue
        for tool in tools:
            # result dir name pattern: 20260521_090012_<hash>_<tool>-autopilot
            if f"{tool}-autopilot" in entry.name or tool.replace("-", "_") + "_autopilot" in entry.name:
                manifest_path = entry / "manifest.json"
                exit_code = _read_exit_from_manifest(manifest_path)
                artifact_dirs = _collect_artifact_dirs(manifest_path)
                round_num = len(per_tool[tool]) + 1
                per_tool[tool].append(
                    {
                        "round": round_num,
                        "result_dir_name": entry.name,
                        "exit_code": exit_code,
                        "start_utc": None,
                        "end_utc": None,
                        "artifact_dirs": artifact_dirs,
                    }
                )
                break  # matched tool

    return per_tool


def _read_exit_from_manifest(manifest_path: Path) -> int:
    if not manifest_path.exists():
        return -1
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return data.get("exit_status", -1)
    except Exception:
        return -1


def _collect_artifact_dirs(manifest_path: Path) -> List[str]:
    """Extract generated agent-driven-dev session dirs from manifest symlink targets."""
    if not manifest_path.exists():
        return []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    dirs: List[str] = []
    for artifact in data.get("artifacts", {}).values():
        # artifact.path = autopilot staging dir (e.g. .../dx_app/dx-agent-dev/e2e-tests/.../autopilot/<ts>)
        ap = artifact.get("path", "")
        if ap:
            dirs.append(ap)
        # contents[*].target = actual generated session dir (e.g. .../dx-agent-dev/20260521-..._yolo26n_detection)
        for c in artifact.get("contents", []):
            if c.get("type") == "symlink":
                tgt = c.get("target", "")
                if tgt and "dx-agent-dev" in tgt and tgt not in dirs:
                    dirs.append(tgt)
    return dirs


def _find_new_result_dir(tool: str, snapshot: set, run_id: str) -> Optional[str]:
    """Return name of the new result dir created in results/<run_id>/ after *snapshot*."""
    run_dir = run_results_dir(run_id)
    if not run_dir.exists():
        return None
    for entry in run_dir.iterdir():
        if entry.is_dir() and entry not in snapshot:
            if f"{tool}-autopilot" in entry.name or tool.replace("-", "_") + "_autopilot" in entry.name:
                return entry.name
    return None


# ---------------------------------------------------------------------------
# Single-tool runner
# ---------------------------------------------------------------------------

def _check_sentinel(state: RunState) -> None:
    """Check for STOP/ABORT sentinel files. Raise if found."""
    if _abort_event.is_set():
        raise AbortRequested()
    state_dir = state.path.parent
    if (state_dir / "ABORT").exists():
        raise AbortRequested()
    if (state_dir / "STOP").exists():
        raise StopRequested()


def _terminate_process(proc: subprocess.Popen, log_path: Path, tool: str, round_num: int) -> None:
    """Kill the entire process group spawned for this round.

    proc is started with start_new_session=True, so its PID is the PGID of
    bash → pytest → agent CLI. Signal the whole group so the agent (typically
    a grandchild of bash) terminates alongside its shell wrapper. SIGTERM
    first with a 10s grace, then SIGKILL.
    """
    try:
        pgid = os.getpgid(proc.pid)
    except ProcessLookupError:
        _log(f"[{tool}] ABORT during round {round_num} — PID {proc.pid} already exited", log_path)
        return
    _log(f"[{tool}] ABORT during round {round_num} — killing PGID {pgid} (SIGTERM)", log_path)
    try:
        os.killpg(pgid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        return
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        _log(f"[{tool}] ABORT — SIGTERM grace expired, escalating to SIGKILL on PGID {pgid}", log_path)
        try:
            os.killpg(pgid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            return
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass


# Stale state file globs that tools leave at sub-project root and that a
# *different* round's agent may read to discover (and illegally reuse) a prior
# session directory. See AGENTS.md:957 "Previous session reference PROHIBITED".
# The harness scrubs these before each round so the agent starts clean.
_STALE_STATE_GLOBS = (
    ".codex_*",
    ".cursor_*",
    ".copilot_*",
    ".current_*",
    ".active_*",
    ".tmp_dx_*",
    ".dx_session_*",
    ".dx_work_*",
)

# Sub-project roots where a tool may write its state file. Relative to REPO_ROOT.
_STATE_FILE_SUB_ROOTS = (
    "dx-compiler",
    "dx-runtime",
    "dx-runtime/dx_app",
    "dx-runtime/dx_stream",
)


def _scrub_stale_state_files(log_path: Path, tool: str) -> int:
    """Remove cross-round/cross-tool stale state files before launching a round.

    Returns count of files removed (for logging).
    """
    removed = 0
    for sub in _STATE_FILE_SUB_ROOTS:
        root = REPO_ROOT / sub
        if not root.is_dir():
            continue
        for pat in _STALE_STATE_GLOBS:
            for stale in root.glob(pat):
                # Skip directories (only target small marker files)
                if stale.is_dir():
                    continue
                try:
                    stale.unlink(missing_ok=True)
                    removed += 1
                except OSError:
                    pass
    if removed:
        _log(f"[{tool}] Pre-round cleanup: removed {removed} stale state file(s)", log_path)
    return removed


def _run_single_round(
    tool: str,
    state: RunState,
    env: Dict[str, str],
    run_dir: Path,
    log_path: Path,
    round_num: int,
) -> int:
    """Execute one round for *tool*. Updates state via mark_start/mark_done.

    Raises AbortRequested if the ABORT sentinel fires mid-round (after marking
    this tool as aborted in state). Returns the subprocess exit code on normal
    completion. Caller is responsible for STOP/ABORT pre-checks.
    """
    total = state.target_rounds
    # Pre-flight: scrub stale state files so this round's agent does not
    # discover a prior round's session_id via a leftover .codex_* / .current_*
    # marker file. Defense-in-depth against the agent-side rule violation.
    _scrub_stale_state_files(log_path, tool)
    _log(f"[{tool}] Round {round_num}/{total} START", log_path)
    state.mark_start(tool, round_num)

    results_snapshot: set = set(run_dir.iterdir()) if run_dir.exists() else set()
    cmd = ["bash", str(TEST_SH), TOOL_CMD[tool]]

    with open(log_path, "a", encoding="utf-8") as flog:
        flog.write(f"\n{'='*60}\n[{_now()}] {tool} Round {round_num}/{total} START\n{'='*60}\n")
        flog.flush()
        proc = subprocess.Popen(
            cmd,
            cwd=str(REPO_ROOT),
            env=env,
            stdout=flog,
            stderr=subprocess.STDOUT,
            # New session → new process group, so _terminate_process()
            # can killpg() the entire bash → pytest → agent-CLI tree on abort.
            start_new_session=True,
        )

    with _state_lock:
        state.data["tool_states"][tool]["pid"] = proc.pid
        state.save()

    # Hoist the ABORT path out of the loop and emit a single diagnostic so
    # we can confirm the polling loop is actually entered when --abort is
    # later invoked.
    abort_path = state.path.parent / "ABORT"
    _log(
        f"[{tool}] Polling PID {proc.pid} (PGID={proc.pid}) for completion. "
        f"ABORT sentinel: {abort_path}",
        log_path,
    )
    while proc.poll() is None:
        time.sleep(2)
        if _abort_event.is_set() or abort_path.exists():
            _log(f"[{tool}] ABORT detected during round {round_num} polling", log_path)
            _terminate_process(proc, log_path, tool, round_num)
            with _state_lock:
                state.data["tool_states"][tool]["in_progress"] = None
                state.data["tool_states"][tool]["pid"] = None
                state.data["tool_states"][tool]["status"] = "aborted"
                state.save()
            raise AbortRequested()

    exit_code = proc.returncode
    with _state_lock:
        state.data["tool_states"][tool]["pid"] = None
        state.save()

    result_dir_name = _find_new_result_dir(tool, results_snapshot, state.run_id)
    artifact_dirs: List[str] = []
    if result_dir_name:
        artifact_dirs = _collect_artifact_dirs(run_dir / result_dir_name / "manifest.json")

    _log(f"[{tool}] Round {round_num}/{total} DONE (exit={exit_code})", log_path)
    state.mark_done(tool, round_num, result_dir_name, exit_code, artifact_dirs)
    return exit_code


def _tool_env(state: RunState, tool: str, thinking: bool) -> Dict[str, str]:
    """Build subprocess env for *tool*: inherits parent + DX_RUN_ID + thinking overrides.

    Also emits metadata env vars so ``conftest.pytest_sessionfinish`` can record
    the run's intent (mode, applied THINKING_ENV) in ``manifest.json``. This
    lets the analyzer distinguish NT vs TH rounds and which reasoning_effort
    argument was actually injected per tool — information that was previously
    only knowable from the user's notes.
    """
    import json as _json
    env = os.environ.copy()
    # Propagate run_id so conftest.pytest_sessionfinish writes results into
    # results/<run_id>/<session_id>/ instead of the flat results/ layout.
    env["DX_RUN_ID"] = state.run_id
    env["DX_TOOL"] = tool
    env["DX_THINKING_MODE"] = "TH" if thinking else "NT"
    applied = THINKING_ENV.get(tool, {}) if thinking else {}
    if thinking:
        env.update(applied)
    # Serialize the dict (possibly empty for cursor-cli) so manifest can show
    # exactly which reasoning_effort args were injected this round.
    env["DX_THINKING_ENV_APPLIED"] = _json.dumps(applied, ensure_ascii=False)
    return env


def run_tool_rounds(
    tool: str,
    state: RunState,
    thinking: bool,
    log_dir: Path,
) -> None:
    """Tool-major: run all remaining rounds for *tool* back-to-back.

    Used by parallel mode (one thread per tool). Sequential mode iterates
    round-major via run_round_major() instead.
    """
    log_path = log_dir / f"{tool}.log"
    log_dir.mkdir(parents=True, exist_ok=True)
    env = _tool_env(state, tool, thinking)
    run_dir = run_results_dir(state.run_id)

    while state.remaining(tool) > 0:
        # Check sentinel BEFORE starting next round.
        try:
            _check_sentinel(state)
        except StopRequested:
            _log(f"[{tool}] STOP requested. Finishing.", log_path)
            with _state_lock:
                ts = state.data["tool_states"][tool]
                if ts.get("status") != "done":
                    ts["status"] = "stopped"
                state.save()
            return
        except AbortRequested:
            _log(f"[{tool}] ABORT requested.", log_path)
            with _state_lock:
                ts = state.data["tool_states"][tool]
                ts["in_progress"] = None
                ts["pid"] = None
                ts["status"] = "aborted"
                state.save()
            raise

        round_num = state.next_round_num(tool)
        _run_single_round(tool, state, env, run_dir, log_path, round_num)

    _log(f"[{tool}] All {state.target_rounds} rounds complete.", log_path)
    with _state_lock:
        state.data["tool_states"][tool]["status"] = "done"
        state.save()


def run_round_major(
    tools: List[str],
    state: RunState,
    thinking: bool,
    log_dir: Path,
) -> bool:
    """Sequential round-major iteration: R1 across all tools, then R2 across all tools, etc.

    Distributes per-tool session quota across rounds so a quota wall on one
    tool affects only that tool's later rounds (not the whole batch). Also
    enables clean mid-run partial reports — after iteration k completes,
    every tool has exactly the same number of rounds banked.

    Sentinel handling:
      - STOP fired between rounds: graceful — currently active tool finishes
        its round, remaining tools' remaining rounds are marked "stopped".
      - ABORT fired (any time): current tool's active round is killed and
        marked aborted; remaining tools' remaining rounds are marked aborted.

    Returns True if all rounds completed with exit_code 0 across the board,
    False otherwise.
    """
    target_rounds = state.target_rounds
    log_dir.mkdir(parents=True, exist_ok=True)
    run_dir = run_results_dir(state.run_id)
    overall_ok = True

    def _mark_remaining(status: str) -> None:
        with _state_lock:
            for t in tools:
                ts = state.data["tool_states"][t]
                if state.remaining(t) > 0 and ts.get("status") not in ("done", "aborted"):
                    ts["status"] = status
            state.save()

    for round_idx in range(1, target_rounds + 1):
        for tool in tools:
            log_path = log_dir / f"{tool}.log"
            # Resume safety: skip if this tool already has this round banked.
            if state.completed_count(tool) >= round_idx:
                continue
            # Check sentinel between rounds so --stop is honored mid-batch.
            try:
                _check_sentinel(state)
            except StopRequested:
                _log(
                    f"[runner] STOP requested at R{round_idx} / {tool}. "
                    f"Marking unstarted tools as stopped.",
                    log_path,
                )
                _mark_remaining("stopped")
                return overall_ok
            except AbortRequested:
                _log(f"[runner] ABORT requested at R{round_idx} / {tool}.", log_path)
                _mark_remaining("aborted")
                return False

            env = _tool_env(state, tool, thinking)
            try:
                exit_code = _run_single_round(tool, state, env, run_dir, log_path, round_idx)
                if exit_code != 0:
                    overall_ok = False
            except AbortRequested:
                # _run_single_round already marked this tool as aborted.
                _log(
                    f"[runner] ABORT during {tool} R{round_idx}. "
                    f"Marking remaining tools aborted.",
                    log_path,
                )
                _mark_remaining("aborted")
                return False

    # All rounds completed naturally — mark each tool with no remaining rounds as done.
    with _state_lock:
        for t in tools:
            ts = state.data["tool_states"][t]
            if state.remaining(t) == 0 and ts.get("status") != "done":
                ts["status"] = "done"
        state.save()
    return overall_ok


def _log(msg: str, log_path: Path) -> None:
    ts = _now()
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _now() -> str:
    return datetime.now().strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Parallel orchestration
# ---------------------------------------------------------------------------

def run_all(
    tools: List[str],
    target_rounds: int,
    thinking: bool,
    resume: bool,
    run_id: Optional[str],
    sequential: bool = True,
) -> int:
    """Launch tools according to mode (sequential by default; --parallel to fan out).

    Sequential mode (default) runs each tool to completion before the next starts,
    eliminating NPU/CPU contention so per-tool duration metrics reflect single-tool
    baseline. Pass sequential=False (via --parallel CLI flag) to run all tools
    concurrently. Returns overall exit code (0 = all passed).
    """
    mode = "sequential" if sequential else "parallel"
    _abort_event.clear()
    state = _resolve_state(tools, target_rounds, thinking, resume, run_id, mode=mode)
    log_dir = state.log_dir

    for fname in ["STOP", "ABORT"]:
        sentinel = state.path.parent / fname
        sentinel.unlink(missing_ok=True)

    with _state_lock:
        state.data["runner_pid"] = os.getpid()
        state.data["status"] = "running"
        state.save()

    all_done = all(state.remaining(t) == 0 for t in tools)
    if all_done:
        with _state_lock:
            state.data["runner_pid"] = None
            state.data["status"] = "done"
            state.save()
        print(f"All tools already at {target_rounds} rounds. Nothing to do.")
        print("Use --status to inspect results, or increase --rounds.")
        return 0

    print(f"\n{'='*60}")
    print(f"  E2E Runner  run_id={state.run_id}")
    print(f"  Tools: {', '.join(tools)}  (mode: {mode})")
    print(f"  Target: {target_rounds} rounds  Thinking: {thinking}")
    for t in tools:
        done = state.completed_count(t)
        rem = state.remaining(t)
        print(f"    {t}: {done} done, {rem} remaining")
    print(f"{'='*60}\n")

    overall_ok = True
    saw_abort = False
    saw_stop = False

    if sequential:
        # Round-major iteration: R1 across all tools, then R2 across all tools.
        # See run_round_major() docstring for rationale (session quota
        # distribution + mid-run partial reports).
        try:
            overall_ok = run_round_major(tools, state, thinking, log_dir)
        except Exception as exc:
            print(f"  [runner] ERROR during round-major iteration: {exc}")
            overall_ok = False
        # Inspect tool statuses to detect stop/abort sentinels
        tool_statuses = {
            state.data["tool_states"][t].get("status", "pending") for t in tools
        }
        if "aborted" in tool_statuses:
            saw_abort = True
        if "stopped" in tool_statuses:
            saw_stop = True
    else:
        # Parallel: one worker per tool, each runs all its rounds tool-major
        # via run_tool_rounds (original behavior).
        futures_map = {}
        with ThreadPoolExecutor(max_workers=max(1, len(tools))) as pool:
            for tool in tools:
                if state.remaining(tool) > 0:
                    f = pool.submit(run_tool_rounds, tool, state, thinking, log_dir)
                    futures_map[f] = tool

            for f in as_completed(futures_map):
                tool = futures_map[f]
                try:
                    f.result()
                    completed = state.data["tool_states"][tool]["completed"]
                    failed = sum(1 for r in completed if r["exit_code"] != 0)
                    if failed:
                        print(f"  [{tool}] {failed} round(s) had non-zero exit.")
                        overall_ok = False
                    if state.data["tool_states"][tool].get("status") == "stopped":
                        saw_stop = True
                except AbortRequested:
                    print(f"  [{tool}] ABORT requested.")
                    saw_abort = True
                    overall_ok = False
                    with _state_lock:
                        state.data["status"] = "aborted"
                        state.save()
                except Exception as exc:
                    print(f"  [{tool}] ERROR: {exc}")
                    overall_ok = False
                    with _state_lock:
                        state.data["tool_states"][tool]["status"] = "error"
                        state.save()

    final_status = _derive_overall_status(state, overall_ok, saw_abort, saw_stop)
    with _state_lock:
        state.data["runner_pid"] = None
        state.data["status"] = final_status
        state.save()

    print(f"\n{'='*60}")
    print(f"  E2E Runner COMPLETE  run_id={state.run_id}  status={final_status}")
    for t in tools:
        completed = state.data["tool_states"][t]["completed"]
        ok = sum(1 for r in completed if r["exit_code"] == 0)
        ng = sum(1 for r in completed if r["exit_code"] != 0)
        print(f"    {t}: {ok} PASS  {ng} FAIL  (total {len(completed)}/{target_rounds})")
    print(f"  State: {state.path}")
    print(f"{'='*60}\n")

    return 0 if final_status in {"done", "stopped"} and overall_ok else 1



def _resolve_state(
    tools: List[str],
    target_rounds: int,
    thinking: bool,
    resume: bool,
    run_id: Optional[str],
    mode: str = "parallel",
) -> RunState:
    """Load existing state (--resume) or create a fresh one.

    On resume, the loaded state's existing mode is preserved (cannot change mode
    of a running batch). On fresh run, the supplied mode is recorded.
    """
    if resume:
        # Try explicit run_id first
        if run_id:
            p = RUNNER_STATE_DIR / run_id / "state.json"
            if p.exists():
                state = RunState.load(p)
                print(f"Resuming run_id={run_id} from {p}")
                state.data["target_rounds"] = target_rounds
                state.data["runner_pid"] = os.getpid()
                state.save()
                return state
            print(f"WARNING: --run-id {run_id} not found; falling back to results/ detection")

        # Try "latest" symlink
        latest_path = RunState.find_latest()
        if latest_path:
            state = RunState.load(latest_path)
            print(f"Resuming latest run_id={state.run_id}")
            state.data["target_rounds"] = target_rounds
            state.data["runner_pid"] = os.getpid()
            state.save()
            return state

        # Fallback: scan results/<run_id>/ if an explicit run_id was given;
        # otherwise create a fresh run. (Legacy flat results/ recovery removed
        # — use migrate_results_to_run_id.py to convert before --resume.)
        print("No existing state found; creating fresh run state.")
        per_tool: Dict[str, List[dict]] = {t: [] for t in tools}
        if run_id:
            per_tool = detect_completed_from_results(tools, target_rounds, run_id=run_id)
        new_run_id = run_id or _make_run_id()
        state = RunState(new_run_id, target_rounds, tools, thinking, mode=mode)
        for t in tools:
            state.data["tool_states"][t]["completed"] = per_tool.get(t, [])
            done = len(state.data["tool_states"][t]["completed"])
            state.data["tool_states"][t]["status"] = "done" if done >= target_rounds else "pending"
        state.data["runner_pid"] = os.getpid()
        state.save()
        return state

    # Fresh run
    new_run_id = _make_run_id()
    state = RunState(new_run_id, target_rounds, tools, thinking, mode=mode)
    state.data["runner_pid"] = os.getpid()
    state.save()
    return state


def _make_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _derive_overall_status(state: RunState, overall_ok: bool, saw_abort: bool, saw_stop: bool) -> str:
    tool_statuses = {state.data["tool_states"].get(t, {}).get("status", "pending") for t in state.tools}
    if saw_abort or "aborted" in tool_statuses:
        return "aborted"
    if saw_stop or "stopped" in tool_statuses:
        return "stopped"
    if "error" in tool_statuses:
        return "error"
    if all(state.remaining(t) == 0 for t in state.tools):
        return "done" if overall_ok else "done-with-failures"
    return "running" if overall_ok else "partial"


# ---------------------------------------------------------------------------
# Cleanup command
# ---------------------------------------------------------------------------

def cleanup_rounds(round_nums: List[int], tools: List[str], run_id: Optional[str]) -> int:
    """Delete all artifacts for the specified round numbers and tools."""
    state_path = _find_state_path(run_id)
    if state_path is None:
        # Try to infer from results/ directly
        return _cleanup_from_results(round_nums, tools)

    state = RunState.load(state_path)
    deleted_any = False

    for tool in tools:
        ts = state.data["tool_states"].get(tool, {})
        remaining_completed = []
        for entry in ts.get("completed", []):
            if entry["round"] in round_nums:
                _delete_round_artifacts(tool, entry, run_id=state.run_id)
                deleted_any = True
            else:
                remaining_completed.append(entry)
        ts["completed"] = remaining_completed
        if not remaining_completed and ts.get("status") == "done":
            ts["status"] = "pending"

    if deleted_any:
        state.save()
        print("Cleanup complete. State updated.")
    else:
        print("No matching rounds found in state.")
    return 0



def _delete_round_artifacts(tool: str, entry: dict, run_id: Optional[str] = None) -> None:
    rn = entry["round"]
    result_dir_name = entry.get("result_dir_name")
    artifact_dirs = entry.get("artifact_dirs", [])

    print(f"  [{tool}] Round {rn}: deleting {len(artifact_dirs)} artifact dir(s)...")
    for ad in artifact_dirs:
        p = Path(ad)
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
            print(f"    deleted: {p}")
        else:
            print(f"    (not found): {p}")

    if result_dir_name:
        # Prefer the run-id-scoped path; fall back to flat layout for legacy.
        candidates = []
        if run_id:
            candidates.append(run_results_dir(run_id) / result_dir_name)
        candidates.append(RESULTS_ROOT / result_dir_name)  # legacy / pre-migration
        for rd in candidates:
            if rd.exists():
                shutil.rmtree(rd, ignore_errors=True)
                print(f"    deleted result dir: {rd}")
                break



def _cleanup_from_results(round_nums: List[int], tools: List[str]) -> int:
    """Cleanup without state.json: requires a run_id to know which subdir to scan.

    With the run-id layout, results/ is no longer flat — bare --cleanup without
    state.json or --run-id cannot determine which results dir to inspect.
    """
    print(
        "ERROR: --cleanup without an active state.json requires --run-id "
        "(results/ is now organized by run_id).",
        file=sys.stderr,
    )
    return 2


# ---------------------------------------------------------------------------
# Environment-failure detection + redo (--redo-env-failures)
# ---------------------------------------------------------------------------
#
# Detect rounds lost to environment issues (corporate TLS/SSL cert, codex
# model-refresh timeout, copilot empty-unknown) and delete them so --resume
# re-runs to target. Classification primitives are imported from the shared SSOT
# (agent_analyzer/lib/env_failure.py) so the runner and the analyzer agree on
# what counts as an env failure. The dir-structure heuristics (rendered-DONE,
# real-work markers, empty-unknown, output-session-dir presence) live here
# because they are runner orchestration, not text-signature detection.

# Mirror lib/session.py SENTINEL_* — DONE detection scans RENDERED transcripts
# only (never raw stream.jsonl, whose `read`-tool outputs can echo doc text
# containing the sentinel format → false positive).
_SENTINEL_START = "[DX-AGENT-DEV: START]"
_SENTINEL_DONE_RE = re.compile(r"\[DX-AGENT-DEV:\s*DONE(?:\s*\(output-dir:\s*[^)]*\))?\]")
# Rendered-transcript filename suffixes (what the harness scans for sentinels)
_TRANSCRIPT_SUFFIXES = ("-session.md", "-session.txt", "-session.html",
                        "session.md", "session.txt", "session.html")
# A scenario with real LLM interaction but no DONE is "incomplete" (a genuine
# attempt), NOT an env failure — must NOT be deleted.
_REAL_WORK_MARKERS = ('"type":"assistant"', "tool_use", "tool_call",
                      "function_call", "item.completed", "turn.completed")
_MIN_REAL_BLOB = 500
_CODEX_COMMANDS_RE = re.compile(r"Commands:\*{0,2}\s*(\d+)\s*total")


_ENV_FAILURE_MOD = None  # memoized SSOT module (loaded once per process)


def _load_env_failure():
    """Load the shared env-failure SSOT (agent_analyzer/lib/env_failure.py).

    Loaded by explicit file path via importlib so the runner has no hard
    package-import dependency on the analyzer and no sys.path pollution.
    env_failure.py imports only stdlib, so it loads standalone cleanly.
    Memoized — classification touches it once per scenario.
    """
    global _ENV_FAILURE_MOD
    if _ENV_FAILURE_MOD is not None:
        return _ENV_FAILURE_MOD
    import importlib.util
    ef_path = SCRIPT_DIR / "agent_analyzer" / "lib" / "env_failure.py"
    spec = importlib.util.spec_from_file_location("dx_e2e_env_failure", ef_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load env_failure SSOT from {ef_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _ENV_FAILURE_MOD = mod
    return mod


def _read_scenario_blob(scen_dir: Path) -> str:
    """Concatenate all text artifacts in a scenario dir (recursive) for
    env-signature detection — includes raw stream.jsonl where cert errors land."""
    blob: List[str] = []
    for f in scen_dir.rglob("*"):
        if f.is_file() and f.suffix in (".jsonl", ".md", ".log", ".txt", ".html"):
            try:
                blob.append(f.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                pass
    return "\n".join(blob)


def _has_real_done_sentinel(scen_dir: Path) -> bool:
    """True iff a DONE sentinel appears in a RENDERED transcript (session.md/.txt/.html)."""
    for f in scen_dir.rglob("*"):
        if not f.is_file():
            continue
        if any(f.name.endswith(sfx) for sfx in _TRANSCRIPT_SUFFIXES):
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if _SENTINEL_DONE_RE.search(text):
                return True
    return False


def _codex_command_count(scen_dir: Path) -> Optional[int]:
    """Parse codex session.md '**Commands:** N total'. None if absent.

    Distinguishes a codex env failure (model-refresh-timeout + Commands=0 → the
    model never loaded) from a codex incomplete run (model-refresh WARNING but
    Commands>0 → recovered and worked, e.g. R5 compiler with 96 commands)."""
    for f in scen_dir.rglob("*-session.md"):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        m = _CODEX_COMMANDS_RE.search(text)
        if m:
            return int(m.group(1))
    return None


def _has_output_session_dir(scen_dir: Path) -> bool:
    """True iff the scenario produced an agent output dir (any subdir other than
    the empty session-logs-unknown/ placeholder)."""
    try:
        for c in scen_dir.iterdir():
            if c.is_dir() and c.name != "session-logs-unknown":
                return True
    except OSError:
        pass
    return False


def _classify_round_scenario(scen_dir: Path) -> Tuple[str, set]:
    """Return ("valid"|"envfail"|"incomplete"|"skip", signature_set) for one scenario.

    valid:      DONE sentinel in a rendered transcript (work completed).
    envfail:    env signature (cert / model-refresh / empty-unknown) or
                effectively-empty output — DELETE-worthy.
    incomplete: real LLM interaction but no DONE and no env signature — a
                genuine attempt (KEEP; the analyzer handles it per-session).
    skip:       no artifacts at all (not a real scenario slot).

    The env vs incomplete decision delegates to the shared SSOT
    (env_failure.is_env_failure) so the runner and analyzer stay in lockstep.
    """
    ef = _load_env_failure()
    sigs: set = set()
    has_any_file = any(f.is_file() for f in scen_dir.rglob("*"))
    unknown_dir = scen_dir / "session-logs-unknown"
    if not has_any_file:
        # copilot env failure leaves ONLY an empty session-logs-unknown/ dir.
        if unknown_dir.is_dir():
            return ("envfail", {"empty-unknown"})
        return ("skip", sigs)

    if _has_real_done_sentinel(scen_dir):
        return ("valid", sigs)

    blob = _read_scenario_blob(scen_dir)
    has_start = _SENTINEL_START in blob
    cmd_count = _codex_command_count(scen_dir)
    sig = ef.detect_env_signature(blob, command_count=cmd_count)
    if sig:
        sigs.add(sig)
    # copilot empty-unknown can co-exist with stray files (tiny blob).
    if unknown_dir.is_dir():
        try:
            unknown_empty = not any(unknown_dir.iterdir())
        except OSError:
            unknown_empty = True
        if unknown_empty and len(blob.strip()) < 50:
            sigs.add("empty-unknown")

    has_real_work = (any(m in blob for m in _REAL_WORK_MARKERS)
                     and len(blob) >= _MIN_REAL_BLOB)
    has_output_dirs = _has_output_session_dir(scen_dir)

    is_env = ef.is_env_failure(
        env_signature=sig,
        has_start=has_start,
        has_done=False,
        exit_status=None,
        has_output_dirs=has_output_dirs,
        output_tokens=(1 if has_real_work else 0),
        tool_call_count=(cmd_count if cmd_count is not None else (1 if has_real_work else 0)),
    )
    if "empty-unknown" in sigs:
        is_env = True  # env loss even without a text signature
    return ("envfail" if is_env else "incomplete", sigs)


def _analyze_round_env(result_dir: Path) -> Tuple[int, int, int, int, set]:
    """Return (valid, incomplete, envfail, total, signatures) across a round's scenarios."""
    if not result_dir.is_dir():
        return (0, 0, 0, 0, set())
    valid = incomplete = envfail = total = 0
    sigs: set = set()
    for sd in sorted(result_dir.iterdir()):
        if not sd.is_dir():
            continue
        verdict, s = _classify_round_scenario(sd)
        if verdict == "skip":
            continue
        total += 1
        sigs |= s
        if verdict == "valid":
            valid += 1
        elif verdict == "incomplete":
            incomplete += 1
        else:
            envfail += 1
    return (valid, incomplete, envfail, total, sigs)


def _round_delete_worthy(valid: int, incomplete: int, envfail: int,
                         total: int, sigs: set) -> bool:
    """Round-level deletion criterion. Delete-worthy when ANY of:
      (1) env failures are the MAJORITY (envfail > valid + incomplete), or
      (2) ANY cert/SSL scenario is present — cert is a transient FIXABLE issue
          (NODE_EXTRA_CA_CERTS), so re-running the whole round yields a clean
          set, preferable to keeping a round with a permanently-broken scenario.
      (3) ANY rate-limit/usage-limit scenario is present — like cert, this is a
          transient FIXABLE issue (wait for the quota reset, then re-run yields a
          clean round). Without this, a round with e.g. 4 valid + 2 rate-limited
          scenarios (envfail not a majority) would be KEPT, silently polluting a
          model-eval comparison with environment-failed scenarios. Round-level
          redo is coarse (it re-runs the valid scenarios too), but a clean round
          is worth more than salvaging a few scenarios for eval integrity.
    KEPT: rounds with only incomplete (real-but-no-DONE) scenarios and no cert /
    rate-limit (e.g. cursor R1/R5: 5 valid + 1 incomplete; codex R5: 5 valid + 1
    model-refresh incomplete) — no fixable env taint."""
    if total <= 0:
        return False
    return (envfail > (valid + incomplete)
            or ("cert" in sigs)
            or ("rate-limit" in sigs))


def detect_env_failed_rounds(state: "RunState", run_id: str) -> List[dict]:
    """Scan a run's completed rounds and return those that are env-fail rounds."""
    out: List[dict] = []
    for tool, ts in state.data.get("tool_states", {}).items():
        for rec in ts.get("completed", []):
            rdir_name = rec.get("result_dir_name")
            rdir = run_results_dir(run_id) / rdir_name if rdir_name else None
            valid, incomplete, envfail, total, sigs = (
                _analyze_round_env(rdir) if rdir else (0, 0, 0, 0, set())
            )
            if _round_delete_worthy(valid, incomplete, envfail, total, sigs):
                out.append({
                    "tool": tool,
                    "round": rec.get("round"),
                    "result_dir_name": rdir_name,
                    "valid": valid,
                    "incomplete": incomplete,
                    "envfail": envfail,
                    "total": total,
                    "reason": (f"{valid}v/{incomplete}i/{envfail}e of {total}, "
                               f"sigs={sorted(sigs)}"),
                    "artifact_dirs": rec.get("artifact_dirs", []),
                })
    return out


def redo_env_failures(run_id: Optional[str]) -> List[dict]:
    """Detect + delete env-fail round records and reset state so --resume re-runs.

    Returns the list of flagged rounds (empty when the run is clean). Deletes
    each flagged round's result dir + agent output dirs and removes its record
    from tool_states[tool].completed, then relabels kept rounds 1..N and resets
    status to 'running' so the resume flow tops each tool back up to target.
    """
    state_path = _find_state_path(run_id)
    if state_path is None:
        print("ERROR: --redo-env-failures requires an existing run "
              "(--run-id or a latest state.json).", file=sys.stderr)
        return []
    state = RunState.load(state_path)
    rid = state.run_id

    flagged = detect_env_failed_rounds(state, rid)
    if not flagged:
        print(f"[redo-env] run {rid}: no env-failure rounds detected — all clean.")
        return []

    to_remove = {(f["tool"], f["round"]) for f in flagged}
    print(f"[redo-env] run {rid}: {len(flagged)} env-failure round(s) flagged:")
    for f in flagged:
        print(f"  {f['tool']:<14} R{f['round']}  ({f['reason']})")

    target = state.target_rounds
    for tool, ts in state.data.get("tool_states", {}).items():
        kept: List[dict] = []
        for rec in ts.get("completed", []):
            if (tool, rec.get("round")) in to_remove:
                _delete_round_artifacts(tool, rec, run_id=rid)
            else:
                kept.append(rec)
        # Relabel kept rounds 1..N (by start order) so there are no gaps/dups.
        kept.sort(key=lambda r: (r.get("start_utc") or "", r.get("round") or 0))
        for i, rec in enumerate(kept, start=1):
            rec["round"] = i
        ts["completed"] = kept
        ts["in_progress"] = None
        ts["pid"] = None
        ts["status"] = "done" if len(kept) >= target else "running"

    # Reset overall status so the resume flow proceeds.
    state.data["status"] = "running"
    state.data["finished_at"] = None
    state.save()
    print(f"[redo-env] removed {len(flagged)} round(s); state reset to 'running' "
          f"— re-run with --resume --run-id {rid} to refill to {target}.")
    return flagged



def _find_state_path(run_id: Optional[str]) -> Optional[Path]:
    if run_id:
        p = RUNNER_STATE_DIR / run_id / "state.json"
        return p if p.exists() else None
    return RunState.find_latest()


# ---------------------------------------------------------------------------
# Stop / abort / list commands
# ---------------------------------------------------------------------------

def _pid_alive(pid: Optional[int]) -> bool:
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
    except (OSError, ValueError, TypeError):
        return False
    return True


# Control-command flags that indicate a *non-launcher* e2e_runner.py invocation
# (abort, stop, status, list, cleanup, redo-env-failures).  A real *running*
# launcher has --rounds and none of these flags.
_CONTROL_FLAGS: tuple = (
    "--abort",
    "--stop",
    "--status",
    "--list",
    "--cleanup",
    "--redo-env-failures",
)


def _cmdline_is_running_launcher(cmdline_str: str, run_id: str, self_pid: int, pid: int) -> bool:
    """Return True iff *cmdline_str* looks like a live launcher for *run_id*.

    Criteria (all must hold):
    - Is not the current process (pid != self_pid).
    - Contains "e2e_runner.py".
    - Contains the run_id string.
    - Does NOT contain any control flag (--abort / --stop / --status /
      --list / --cleanup / --redo-env-failures) — those indicate a sibling
      control-command invocation, not a running launcher.
    """
    if pid == self_pid:
        return False
    if "e2e_runner.py" not in cmdline_str:
        return False
    if run_id not in cmdline_str:
        return False
    if any(flag in cmdline_str for flag in _CONTROL_FLAGS):
        return False
    return True


def _find_runner_pids_by_cmdline(run_id: str) -> List[int]:
    """Find live e2e_runner.py launcher processes that aren't this one.

    Used as a fallback when state.json's runner_pid is null/stale (a known
    race where runner_pid gets cleared prematurely). Scans /proc/<pid>/cmdline
    for "e2e_runner.py" + run_id and excludes the current process AND any
    sibling control-command invocations (--abort, --stop, --status, --list,
    --cleanup, --redo-env-failures).  Caller still has to decide whether to
    signal; this just enumerates candidates.
    """
    candidates: List[int] = []
    proc_root = Path("/proc")
    if not proc_root.is_dir():
        return candidates
    self_pid = os.getpid()
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        try:
            cmd = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            continue
        if _cmdline_is_running_launcher(cmd, run_id, self_pid, pid):
            candidates.append(pid)
    return candidates



def _finalize_dead_run(state: "RunState", terminal_status: str) -> int:
    """Reconcile a stale (force-killed) run to a terminal state.

    Sets run-level status to *terminal_status* and, for every tool whose
    per-tool status is "running" or whose *in_progress* slot is non-None,
    sets that tool's status to *terminal_status* and clears *in_progress*.
    Saves via the existing _state_lock + state.save() pattern.

    Returns the number of per-tool states that were finalized (0 if the run
    was already in a clean state).
    """
    finalized = 0
    with _state_lock:
        state.data["status"] = terminal_status
        for _tool, ts in (state.data.get("tool_states") or {}).items():
            if ts.get("status") == "running" or ts.get("in_progress"):
                ts["status"] = terminal_status
                ts["in_progress"] = None
                finalized += 1
        state.save()
    return finalized


def do_stop(run_id: Optional[str]) -> int:
    state_path = _find_state_path(run_id)
    if state_path is None:
        print("No run state found.", file=sys.stderr)
        return 1

    state = RunState.load(state_path)
    if all(state.remaining(tool) == 0 for tool in state.tools):
        print("Nothing to stop: all tools are already complete.")
        return 0

    runner_pid = state.data.get("runner_pid")
    if not _pid_alive(runner_pid):
        # No live runner found via runner_pid.  Also try /proc cmdline scan.
        cmdline_pids = _find_runner_pids_by_cmdline(state.run_id)
        if not cmdline_pids:
            # Truly dead — reconcile stale state so --status no longer shows "running".
            n = _finalize_dead_run(state, "stopped")
            print(
                f"No live runner/worker — reconciled stale state to 'stopped' "
                f"({n} tool state(s) finalized).",
                file=sys.stderr,
            )
            return 0
        # Live processes found via cmdline; fall through to normal STOP sentinel path.
        runner_pid = None  # will signal via cmdline fallback below if needed

    stop_path = state.path.parent / "STOP"
    payload = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "requester_pid": os.getpid(),
    }
    stop_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with _state_lock:
        state.data["status"] = "stop-requested"
        state.save()

    print(f"STOP requested for run_id={state.run_id}. Active rounds will finish before stopping.")
    return 0



def do_abort(run_id: Optional[str], force: bool) -> int:
    state_path = _find_state_path(run_id)
    if state_path is None:
        print("No run state found.", file=sys.stderr)
        return 1

    if not force:
        answer = input("Are you sure? (y/N) ").strip().lower()
        if answer not in {"y", "yes"}:
            print("Abort cancelled.")
            return 1

    state = RunState.load(state_path)
    abort_path = state.path.parent / "ABORT"
    payload = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "requester_pid": os.getpid(),
    }
    abort_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    signaled_runner = False
    runner_pid = state.data.get("runner_pid")
    if _pid_alive(runner_pid):
        try:
            os.kill(int(runner_pid), signal.SIGTERM)
            signaled_runner = True
            print(f"SIGTERM sent to runner PID {runner_pid}.")
        except OSError as exc:
            print(f"Warning: failed to signal runner PID {runner_pid}: {exc}", file=sys.stderr)

    # Fallback A: state.json's runner_pid was null/stale (known race). Scan
    # /proc for live e2e_runner.py processes and signal them. Safe because the
    # ABORT sentinel was already written above — even if we signal the wrong
    # runner, an unrelated runner ignores sentinels of other runs.
    if not signaled_runner:
        for pid in _find_runner_pids_by_cmdline(state.run_id):
            try:
                os.kill(pid, signal.SIGTERM)
                signaled_runner = True
                print(f"Fallback: SIGTERM sent to candidate runner PID {pid} (via /proc cmdline match).")
            except (ProcessLookupError, PermissionError) as exc:
                print(f"Warning: failed to signal candidate PID {pid}: {exc}", file=sys.stderr)

    # Fallback B: directly killpg the per-tool subprocesses recorded in
    # state.json. Belt-and-suspenders: if the worker polling loop never
    # detects the ABORT sentinel (Bug 2 hypothesis), this still tears down
    # the active bash → pytest → agent trees because each was launched with
    # start_new_session=True (own process group).
    killed_groups = []
    for tool, ts in (state.data.get("tool_states") or {}).items():
        pid = ts.get("pid")
        if not pid or not _pid_alive(pid):
            continue
        try:
            pgid = os.getpgid(int(pid))
        except (ProcessLookupError, OSError):
            continue
        try:
            os.killpg(pgid, signal.SIGTERM)
            killed_groups.append((tool, pid, pgid))
        except (ProcessLookupError, PermissionError):
            pass
    if killed_groups:
        for tool, pid, pgid in killed_groups:
            print(f"Fallback: SIGTERM sent to {tool} process group (PID={pid}, PGID={pgid}).")

    if not signaled_runner and not killed_groups:
        # No live process found at all — the run was force-killed (e.g. SIGKILL /
        # TaskStop / exit 144).  Reconcile stale state immediately so that
        # e2e_monitor.py no longer shows the run as "running".
        n = _finalize_dead_run(state, "aborted")
        print(
            f"No live runner/worker — reconciled stale state to 'aborted' "
            f"({n} tool state(s) finalized).",
            file=sys.stderr,
        )
    else:
        # A live worker was signaled; it will finalize per-tool states when it
        # detects the ABORT sentinel.  Set run-level status to abort-requested
        # so --status surfaces the intent immediately.
        with _state_lock:
            state.data["status"] = "abort-requested"
            state.save()

    print(f"ABORT requested for run_id={state.run_id}.")
    return 0



def show_list() -> None:
    if not RUNNER_STATE_DIR.exists():
        print("No runner_state directory found.")
        return

    latest_path = RunState.find_latest()
    latest_run_id = latest_path.parent.name if latest_path else None
    states = sorted(
        (p for p in RUNNER_STATE_DIR.glob("*/state.json") if p.parent.name != "latest"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not states:
        print("No runs found.")
        return

    print(f"{'Latest':<7} {'Run ID':<18} {'Created':<20} {'Rounds':<10} {'Thinking':<9} {'Status':<20} Progress")
    print(f"{'-'*7} {'-'*18} {'-'*20} {'-'*10} {'-'*9} {'-'*20} {'-'*40}")
    for state_path in states:
        state = RunState.load(state_path)
        d = state.data
        progress = ", ".join(
            f"{tool}:{len(d['tool_states'].get(tool, {}).get('completed', []))}/{d.get('target_rounds', '?')}"
            for tool in d.get("tools", ALL_TOOLS)
        )
        marker = "*" if d.get("run_id") == latest_run_id else ""
        print(
            f"{marker:<7} {d.get('run_id', '?'):<18} {d.get('created_at', '?'):<20} "
            f"{str(d.get('target_rounds', '?')):<10} {str(d.get('thinking', False)):<9} "
            f"{_derive_list_status(d):<20} {progress}"
        )



def _derive_list_status(data: dict) -> str:
    """Derive overall run status from tool-level statuses.

    Terminal states stored at top-level (done, aborted, stopped) take precedence.
    In-flight request states (abort-requested, stop-requested) are also surfaced
    so callers see the intent immediately — they shouldn't look like "running".
    Otherwise derive from tool_states.
    """
    top = data.get("status")
    # Terminal states set by runner on completion
    if top in ("done", "aborted", "stopped"):
        return top
    # In-flight request states set by do_abort / do_stop — surface them so
    # --status / --list don't show stale "running" after abort/stop was issued.
    if top in ("abort-requested", "stop-requested"):
        return top
    # Derive from tool-level statuses
    statuses = {ts.get("status", "pending") for ts in data.get("tool_states", {}).values()}
    if "aborted" in statuses:
        return "aborted"
    if "stopped" in statuses:
        return "stopped"
    if "running" in statuses:
        return "running"
    if statuses == {"done"}:
        return "done"
    return "pending"


# ---------------------------------------------------------------------------
# Status command
# ---------------------------------------------------------------------------

def show_status(run_id: Optional[str]) -> None:
    state_path = _find_state_path(run_id)
    if state_path is None:
        print("No run state found. Run `e2e_runner.py --rounds N` to start.")
        return

    state = RunState.load(state_path)
    d = state.data
    target = d.get("target_rounds", "?")
    thinking = "ON" if d.get("thinking") else "OFF"
    overall_status = _derive_list_status(d)

    if _HAS_RICH:
        console = RichConsole()
        header = RichText(
            f"E2E Runner Status  run_id={d['run_id']}  target={target}R  thinking={thinking}  status={overall_status}",
            style="bold",
        )
        console.print(header)
        console.print(f"  State: {state_path}\n")

        # Summary table matching monitor's live TUI format
        tbl = RichTable(expand=True, border_style="dim")
        tbl.add_column("Tool", style="cyan", no_wrap=True, min_width=14)
        tbl.add_column("Done", justify="right", style="green", min_width=4)
        tbl.add_column("Fail", justify="right", style="red", min_width=4)
        tbl.add_column("Rem", justify="right", style="yellow", min_width=4)
        tbl.add_column("Status", min_width=8)
        tbl.add_column("PID", justify="right", min_width=6)
        tbl.add_column("Timing", min_width=20)

        for tool in d.get("tools", ALL_TOOLS):
            ts = d["tool_states"].get(tool, {})
            completed = ts.get("completed", [])
            ok = sum(1 for r in completed if r.get("exit_code") == 0)
            ng = sum(1 for r in completed if r.get("exit_code") != 0)
            rem = max(0, (int(target) if isinstance(target, int) else 0) - len(completed))
            status = ts.get("status", "pending")
            pid_str = str(ts.get("pid") or "—")
            timing = _format_timing_for_status(ts)
            tbl.add_row(tool, str(ok), str(ng) if ng else "—", str(rem), status, pid_str, timing)

        console.print(RichPanel(tbl, title="Round Progress", border_style="green"))

        # Completed Rounds detail
        detail_tbl = RichTable(title="Completed Rounds", expand=True, border_style="dim")
        detail_tbl.add_column("Tool", style="cyan", no_wrap=True)
        detail_tbl.add_column("Round", justify="right")
        detail_tbl.add_column("Start", no_wrap=True)
        detail_tbl.add_column("End", no_wrap=True)
        detail_tbl.add_column("Duration", no_wrap=True)
        detail_tbl.add_column("Exit", justify="right")
        detail_tbl.add_column("Result Dir", no_wrap=True)
        has_rows = False
        for tool in d.get("tools", ALL_TOOLS):
            ts = d["tool_states"].get(tool, {})
            for entry in ts.get("completed", []):
                has_rows = True
                start_utc = entry.get("start_utc", "")
                end_utc = entry.get("end_utc", "")
                start_short = _short_ts(start_utc)
                end_short = _short_ts(end_utc)
                dur = _format_duration(_duration_seconds(start_utc, end_utc))
                ec = str(entry.get("exit_code", "?"))
                ec_style = "green" if ec == "0" else "red"
                result_dir = entry.get("result_dir_name", "—")
                detail_tbl.add_row(
                    tool, f"R{entry.get('round', '?')}", start_short, end_short,
                    dur, RichText(ec, style=ec_style), result_dir or "—"
                )
        if has_rows:
            console.print(detail_tbl)
        console.print()
    else:
        # Plain text fallback (original format)
        print(f"\nRun ID     : {d['run_id']}")
        print(f"Created    : {d.get('created_at', '?')}")
        print(f"Target     : {target} rounds  Thinking: {d.get('thinking', False)}  Mode: {d.get('mode', 'parallel')}")
        print(f"Status     : {overall_status}")
        print(f"Runner PID : {d.get('runner_pid') or '—'}")
        print(f"State      : {state_path}\n")

        print(f"{'Tool':<16} {'Done':>5} {'Fail':>5} {'Status':<14} {'PID':>8} Last result dir")
        print(f"{'-'*16} {'-'*5} {'-'*5} {'-'*14} {'-'*8} {'-'*40}")
        for tool in d.get("tools", ALL_TOOLS):
            ts = d["tool_states"].get(tool, {})
            completed = ts.get("completed", [])
            ok = sum(1 for r in completed if r.get("exit_code") == 0)
            ng = sum(1 for r in completed if r.get("exit_code") != 0)
            status = ts.get("status", "?")
            pid = ts.get("pid") or "—"
            last = completed[-1].get("result_dir_name") if completed else "—"
            print(f"{tool:<16} {ok:>5} {ng:>5} {status:<14} {str(pid):>8} {last or '—'}")
        print()

        for tool in d.get("tools", ALL_TOOLS):
            ts = d["tool_states"].get(tool, {})
            completed = ts.get("completed", [])
            ip = ts.get("in_progress")

            print(f"[{tool}]")
            if completed:
                for entry in completed:
                    start_utc = entry.get("start_utc") or "?"
                    end_utc = entry.get("end_utc") or "?"
                    duration = _format_duration(_duration_seconds(entry.get("start_utc"), entry.get("end_utc")))
                    result_dir = entry.get("result_dir_name") or "—"
                    print(
                        f"  Round {entry.get('round', '?'):>2}: {start_utc} -> {end_utc}  "
                        f"duration={duration}  exit={entry.get('exit_code', '?')}  result={result_dir}"
                    )
            else:
                print("  No completed rounds.")

            if ip:
                elapsed = _format_duration(_elapsed_seconds(ip.get("start_utc")))
                print(
                    f"  In progress: round {ip.get('round', '?')} since {ip.get('start_utc', '?')}  "
                    f"elapsed={elapsed}  pid={ts.get('pid') or '—'}"
                )
            print()


def _short_ts(ts: Optional[str]) -> str:
    """Extract local HH:MM from ISO timestamp."""
    if not ts:
        return "—"
    dt = _parse_utc(ts)
    if dt:
        return dt.astimezone().strftime("%H:%M")
    try:
        return ts[11:16] if len(ts) > 16 else ts
    except Exception:
        return "—"


def _format_timing_for_status(tool_state: dict) -> str:
    """Format timing string for status display."""
    status = tool_state.get("status", "pending")
    if status == "running":
        ip = tool_state.get("in_progress") or {}
        round_num = ip.get("round", "?")
        start_utc = ip.get("start_utc")
        if not start_utc:
            return f"R{round_num}"
        elapsed = _format_duration(_elapsed_seconds(start_utc))
        start_short = _short_ts(start_utc)
        return f"R{round_num} {start_short} ({elapsed}+)"
    if status == "done":
        completed = tool_state.get("completed", [])
        if not completed:
            return "—"
        last = completed[-1]
        dur = _format_duration(_duration_seconds(last.get("start_utc"), last.get("end_utc")))
        return f"last: {dur}"
    return "—"



def _parse_utc(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None



def _duration_seconds(start_utc: Optional[str], end_utc: Optional[str]) -> Optional[float]:
    start_dt = _parse_utc(start_utc)
    end_dt = _parse_utc(end_utc)
    if not start_dt or not end_dt:
        return None
    return max(0.0, (end_dt - start_dt).total_seconds())



def _elapsed_seconds(start_utc: Optional[str]) -> Optional[float]:
    start_dt = _parse_utc(start_utc)
    if not start_dt:
        return None
    return max(0.0, (datetime.now(timezone.utc) - start_dt).total_seconds())



def _format_duration(seconds: Optional[float]) -> str:
    if seconds is None:
        return "?"
    total = int(seconds)
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{secs:02d}s"
    if minutes:
        return f"{minutes}m{secs:02d}s"
    return f"{secs}s"



def _summarize_log_timings(log_path: Path) -> Optional[str]:
    if not log_path.exists():
        return None
    try:
        lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return None

    pattern = re.compile(r"^\[(\d{2}:\d{2}:\d{2})\]\s+(.*)$")
    scenario_start: Dict[str, str] = {}
    durations: List[int] = []
    for line in lines:
        match = pattern.match(line)
        if not match:
            continue
        ts, msg = match.groups()
        if "Scenario" not in msg:
            continue
        name = msg
        if " START" in msg:
            name = msg.rsplit(" START", 1)[0]
            scenario_start[name] = ts
        elif " DONE" in msg and name:
            name = msg.rsplit(" DONE", 1)[0]
            start_ts = scenario_start.pop(name, None)
            if start_ts:
                start_dt = datetime.strptime(start_ts, "%H:%M:%S")
                end_dt = datetime.strptime(ts, "%H:%M:%S")
                durations.append(int((end_dt - start_dt).total_seconds()))
    if not durations:
        return None
    avg = sum(durations) / len(durations)
    return f"scenarios={len(durations)} avg={_format_duration(avg)} max={_format_duration(max(durations))}"


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="e2e_runner.py",
        description="Reusable multi-round E2E test runner for DEEPX Agent-Driven Dev (sequential by default).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    # No default — required for actions that launch/resume a run. Status/list/
    # stop/abort/cleanup commands do not need --rounds (enforced in main()).
    p.add_argument("--rounds", type=int, default=None,
                   help="Target number of rounds per tool (required when starting or resuming a run)")
    p.add_argument(
        "--tools",
        default=",".join(ALL_TOOLS),
        help=f"Comma-separated tool list (default: all). Options: {', '.join(ALL_TOOLS)}",
    )
    p.add_argument("--thinking", action="store_true", help="Enable thinking/high-reasoning mode for each tool")
    # Per-tool model overrides — translate to the matching DX_AGENT_E2E_*_MODEL env
    # var when the subprocess is launched. Useful for sweeping a single tool across
    # multiple backend models (e.g. opus-4.6 vs opus-4.8 in copilot-cli).
    p.add_argument("--copilot-model",  dest="copilot_model",  default=None,
                   help="Override copilot-cli backend model (sets DX_AGENT_E2E_MODEL)")
    p.add_argument("--codex-model",    dest="codex_model",    default=None,
                   help="Override codex-cli backend model (sets DX_AGENT_E2E_MODEL for codex)")
    p.add_argument("--opencode-model", dest="opencode_model", default=None,
                   help="Override opencode-cli backend model (sets DX_AGENT_E2E_OPENCODE_MODEL)")
    p.add_argument("--claude-model",   dest="claude_model",   default=None,
                   help="Override claude-code backend model (sets DX_AGENT_E2E_CLAUDE_CODE_MODEL)")
    p.add_argument("--cursor-model",   dest="cursor_model",   default=None,
                   help="Override cursor-cli backend model (sets DX_AGENT_E2E_CURSOR_MODEL)")
    p.add_argument(
        "--parallel",
        action="store_true",
        help="Run tools concurrently (one thread per tool). Default: sequential one-at-a-time.",
    )
    p.add_argument("--resume", action="store_true", help="Auto-detect completed rounds and continue to target")
    p.add_argument("--run-id", dest="run_id", help="Specify a previous run ID")
    p.add_argument("--status", action="store_true", help="Show current run status and exit")
    p.add_argument("--cleanup", action="store_true", help="Delete artifacts for specified rounds")
    p.add_argument("--stop", action="store_true", help="Gracefully stop a running session after the current round")
    p.add_argument("--abort", action="store_true", help="Abort a running session immediately")
    p.add_argument("--force", action="store_true", help="Do not prompt for confirmation with --abort")
    p.add_argument("--list", dest="list_runs", action="store_true", help="List known runs and exit")
    p.add_argument("--round", dest="round_nums", type=str, help="Round number(s) to clean up, e.g. 3 or 2,3,4")
    p.add_argument(
        "--redo-env-failures", dest="redo_env_failures", action="store_true",
        help="Detect env-failed rounds (cert/SSL, codex model-refresh, copilot "
             "empty-unknown), delete them, and reset state so --resume re-runs to target",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="With --redo-env-failures: report env-failed rounds without deleting",
    )
    return p



def do_redo_env_failures(run_id: Optional[str], dry_run: bool = False) -> int:
    """Control command for --redo-env-failures.

    Default: detect env-fail rounds, delete them, and reset state so a
    subsequent --resume refills to target. With --dry-run: report only.
    """
    state_path = _find_state_path(run_id)
    if state_path is None:
        print("ERROR: --redo-env-failures requires an existing run "
              "(--run-id or a latest state.json).", file=sys.stderr)
        return 2
    state = RunState.load(state_path)
    rid = state.run_id

    if dry_run:
        flagged = detect_env_failed_rounds(state, rid)
        if not flagged:
            print(f"[redo-env] run {rid}: no env-failure rounds detected — all clean.")
            return 0
        print(f"[redo-env] run {rid}: {len(flagged)} env-failure round(s) "
              f"(dry-run — nothing deleted):")
        for f in flagged:
            print(f"  {f['tool']:<14} R{f['round']}  ({f['reason']})")
        print(f"\n  Re-run without --dry-run to delete + reset for --resume.")
        return 0

    flagged = redo_env_failures(run_id)
    if flagged:
        target = state.target_rounds
        print(f"\n  Next: python {Path(__file__).name} --resume "
              f"--run-id {rid} --rounds {target} "
              f"--tools {','.join(state.tools)}")
    return 0


def _handle_sigterm(signum, frame) -> None:  # type: ignore[no-untyped-def]
    _abort_event.set()



def main() -> int:
    signal.signal(signal.SIGTERM, _handle_sigterm)

    parser = build_parser()
    args = parser.parse_args()

    # Read-only / control commands — do not require --rounds.
    if args.list_runs:
        show_list()
        return 0
    if args.stop:
        return do_stop(args.run_id)
    if args.abort:
        return do_abort(args.run_id, args.force)
    if args.status:
        show_status(args.run_id)
        return 0
    if args.redo_env_failures:
        return do_redo_env_failures(args.run_id, dry_run=args.dry_run)

    tools = [t.strip() for t in args.tools.split(",") if t.strip() in ALL_TOOLS]
    if not tools:
        print(f"ERROR: no valid tools specified. Valid: {', '.join(ALL_TOOLS)}", file=sys.stderr)
        return 2

    # Translate --<tool>-model CLI flags into the env vars conftest reads.
    # Note: copilot and codex both consume DX_AGENT_E2E_MODEL, so running
    # both tools in the same invocation with conflicting overrides is unsupported.
    _MODEL_ENV_MAP = {
        "copilot_model":  "DX_AGENT_E2E_MODEL",
        "codex_model":    "DX_AGENT_E2E_MODEL",
        "opencode_model": "DX_AGENT_E2E_OPENCODE_MODEL",
        "claude_model":   "DX_AGENT_E2E_CLAUDE_CODE_MODEL",
        "cursor_model":   "DX_AGENT_E2E_CURSOR_MODEL",
    }
    for arg_name, env_name in _MODEL_ENV_MAP.items():
        val = getattr(args, arg_name, None)
        if val:
            os.environ[env_name] = val
            print(f"  [model override] {env_name}={val}")

    if args.cleanup:
        if not args.round_nums:
            print("ERROR: --cleanup requires --round N (e.g. --round 3)", file=sys.stderr)
            return 2
        round_nums = [int(r.strip()) for r in args.round_nums.split(",") if r.strip().isdigit()]
        return cleanup_rounds(round_nums, tools, args.run_id)

    # Launching or resuming a run requires an explicit target.
    if args.rounds is None:
        parser.error("--rounds is required when starting or resuming a run")
    if args.rounds < 1:
        parser.error(f"--rounds must be >= 1 (got {args.rounds})")

    # Sequential is the default; --parallel opts into concurrent execution.
    sequential = not args.parallel

    return run_all(
        tools,
        args.rounds,
        args.thinking,
        args.resume,
        args.run_id,
        sequential=sequential,
    )


if __name__ == "__main__":
    sys.exit(main())
