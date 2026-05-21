#!/usr/bin/env python3
"""
e2e_runner.py — Reusable multi-round parallel E2E test runner for DEEPX Agentic Dev.

Usage examples:
    # Run 5 rounds for all tools (parallel)
    python .deepx/tests/e2e_runner.py --rounds 5

    # Run 5 rounds for specific tools only
    python .deepx/tests/e2e_runner.py --rounds 5 --tools claude-code,copilot-cli

    # Run with thinking / high-reasoning mode
    python .deepx/tests/e2e_runner.py --rounds 5 --thinking

    # Resume: auto-detect completed rounds and continue to target
    python .deepx/tests/e2e_runner.py --rounds 5 --resume

    # Resume a specific previous run
    python .deepx/tests/e2e_runner.py --rounds 5 --resume --run-id 20260521_100000

    # Show current run status
    python .deepx/tests/e2e_runner.py --status

    # List all previous runs
    python .deepx/tests/e2e_runner.py --list

    # Gracefully stop the current run after the active round finishes
    python .deepx/tests/e2e_runner.py --stop --run-id 20260521_100000

    # Abort the current run immediately
    python .deepx/tests/e2e_runner.py --abort --run-id 20260521_100000 --force

    # Delete artifacts for round 3 of all tools
    python .deepx/tests/e2e_runner.py --cleanup --round 3

    # Delete artifacts for round 3 of a specific tool set
    python .deepx/tests/e2e_runner.py --cleanup --round 3 --tools claude-code

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
from typing import Dict, List, Optional

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
RESULTS_ROOT = REPO_ROOT / "dx-agentic-dev/e2e-tests/results"
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
    "claude-code": "agentic-e2e-claude-code-autopilot",
    "copilot-cli": "agentic-e2e-copilot-cli-autopilot",
    "cursor-cli": "agentic-e2e-cursor-cli-autopilot",
    "opencode-cli": "agentic-e2e-opencode-cli-autopilot",
    "codex-cli": "agentic-e2e-codex-cli-autopilot",
}

# Thinking / high-reasoning mode env vars per tool
THINKING_ENV: Dict[str, Dict[str, str]] = {
    "claude-code": {"DX_AGENTIC_E2E_CLAUDE_CODE_EXTRA_ARGS": "--effort xhigh"},
    "copilot-cli": {"DX_AGENTIC_E2E_COPILOT_EXTRA_ARGS": "--effort xhigh"},
    "opencode-cli": {"DX_AGENTIC_E2E_OPENCODE_EXTRA_ARGS": "--variant high"},
    "codex-cli": {"DX_AGENTIC_E2E_CODEX_EXTRA_ARGS": '-c model_reasoning_effort="xhigh"'},
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

    def __init__(self, run_id: str, target_rounds: int, tools: List[str], thinking: bool):
        self.run_id = run_id
        self.path = RUNNER_STATE_DIR / run_id / "state.json"
        self.log_dir = RUNNER_STATE_DIR / run_id / "logs"
        self.data: dict = {
            "run_id": run_id,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "target_rounds": target_rounds,
            "thinking": thinking,
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

def detect_completed_from_results(tools: List[str], target_rounds: int) -> Dict[str, List[dict]]:
    """Scan results/ dir and group completed rounds per tool by timestamp order."""
    per_tool: Dict[str, List[dict]] = {t: [] for t in tools}
    if not RESULTS_ROOT.exists():
        return per_tool

    entries = sorted(RESULTS_ROOT.iterdir(), key=lambda p: p.name)
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
    """Extract generated agentic-dev session dirs from manifest symlink targets."""
    if not manifest_path.exists():
        return []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    dirs: List[str] = []
    for artifact in data.get("artifacts", {}).values():
        # artifact.path = autopilot staging dir (e.g. .../dx_app/dx-agentic-dev/e2e-tests/.../autopilot/<ts>)
        ap = artifact.get("path", "")
        if ap:
            dirs.append(ap)
        # contents[*].target = actual generated session dir (e.g. .../dx-agentic-dev/20260521-..._yolo26n_detection)
        for c in artifact.get("contents", []):
            if c.get("type") == "symlink":
                tgt = c.get("target", "")
                if tgt and "dx-agentic-dev" in tgt and tgt not in dirs:
                    dirs.append(tgt)
    return dirs


def _find_new_result_dir(tool: str, snapshot: set) -> Optional[str]:
    """Return name of the new result dir created after *snapshot*."""
    if not RESULTS_ROOT.exists():
        return None
    for entry in RESULTS_ROOT.iterdir():
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
    _log(f"[{tool}] ABORT during round {round_num} — killing PID {proc.pid}", log_path)
    try:
        proc.terminate()
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            proc.kill()
        except ProcessLookupError:
            return
        proc.wait()


def run_tool_rounds(
    tool: str,
    state: RunState,
    thinking: bool,
    log_dir: Path,
) -> None:
    """Run remaining rounds for *tool* sequentially, updating state after each."""
    log_path = log_dir / f"{tool}.log"
    log_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    if thinking:
        env.update(THINKING_ENV.get(tool, {}))

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
        total = state.target_rounds
        _log(f"[{tool}] Round {round_num}/{total} START", log_path)
        state.mark_start(tool, round_num)

        results_snapshot: set = set(RESULTS_ROOT.iterdir()) if RESULTS_ROOT.exists() else set()
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
            )

        with _state_lock:
            state.data["tool_states"][tool]["pid"] = proc.pid
            state.save()

        while proc.poll() is None:
            time.sleep(2)
            if _abort_event.is_set() or (state.path.parent / "ABORT").exists():
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

        result_dir_name = _find_new_result_dir(tool, results_snapshot)
        artifact_dirs: List[str] = []
        if result_dir_name:
            artifact_dirs = _collect_artifact_dirs(RESULTS_ROOT / result_dir_name / "manifest.json")

        _log(f"[{tool}] Round {round_num}/{total} DONE (exit={exit_code})", log_path)
        state.mark_done(tool, round_num, result_dir_name, exit_code, artifact_dirs)

    _log(f"[{tool}] All {state.target_rounds} rounds complete.", log_path)
    with _state_lock:
        state.data["tool_states"][tool]["status"] = "done"
        state.save()


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
) -> int:
    """Launch all tools in parallel; return overall exit code (0 = all passed)."""
    _abort_event.clear()
    state = _resolve_state(tools, target_rounds, thinking, resume, run_id)
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
    print(f"  Tools: {', '.join(tools)}")
    print(f"  Target: {target_rounds} rounds  Thinking: {thinking}")
    for t in tools:
        done = state.completed_count(t)
        rem = state.remaining(t)
        print(f"    {t}: {done} done, {rem} remaining")
    print(f"{'='*60}\n")

    futures_map = {}
    overall_ok = True
    saw_abort = False
    saw_stop = False

    with ThreadPoolExecutor(max_workers=len(tools)) as pool:
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
) -> RunState:
    """Load existing state (--resume) or create a fresh one."""
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

        # Fallback: scan results/ dir and build state from existing dirs
        print("No existing state found; scanning results/ to detect completed rounds...")
        per_tool = detect_completed_from_results(tools, target_rounds)
        new_run_id = _make_run_id()
        state = RunState(new_run_id, target_rounds, tools, thinking)
        for t in tools:
            state.data["tool_states"][t]["completed"] = per_tool.get(t, [])
            done = len(state.data["tool_states"][t]["completed"])
            state.data["tool_states"][t]["status"] = "done" if done >= target_rounds else "pending"
        state.data["runner_pid"] = os.getpid()
        state.save()
        return state

    # Fresh run
    new_run_id = _make_run_id()
    state = RunState(new_run_id, target_rounds, tools, thinking)
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
                _delete_round_artifacts(tool, entry)
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



def _delete_round_artifacts(tool: str, entry: dict) -> None:
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
        rd = RESULTS_ROOT / result_dir_name
        if rd.exists():
            shutil.rmtree(rd, ignore_errors=True)
            print(f"    deleted result dir: {rd.name}")



def _cleanup_from_results(round_nums: List[int], tools: List[str]) -> int:
    """Cleanup without state.json: scan results/ and delete by ordinal round number."""
    per_tool = detect_completed_from_results(tools, max(round_nums) + 1)
    for tool in tools:
        entries = per_tool.get(tool, [])
        for entry in entries:
            if entry["round"] in round_nums:
                _delete_round_artifacts(tool, entry)
    return 0



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
        print(f"Runner is not active for run_id={state.run_id} (runner_pid={runner_pid}).", file=sys.stderr)
        return 1

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

    runner_pid = state.data.get("runner_pid")
    if _pid_alive(runner_pid):
        try:
            os.kill(int(runner_pid), signal.SIGTERM)
        except OSError as exc:
            print(f"Warning: failed to signal runner PID {runner_pid}: {exc}", file=sys.stderr)

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
    Otherwise derive from tool_states.
    """
    top = data.get("status")
    # Only trust top-level if it's a terminal state (set by runner on completion)
    if top in ("done", "aborted", "stopped"):
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
        print(f"Target     : {target} rounds  Thinking: {d.get('thinking', False)}")
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
        description="Reusable multi-round parallel E2E test runner for DEEPX Agentic Dev.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--rounds", type=int, default=5, help="Target number of rounds per tool (default: 5)")
    p.add_argument(
        "--tools",
        default=",".join(ALL_TOOLS),
        help=f"Comma-separated tool list (default: all). Options: {', '.join(ALL_TOOLS)}",
    )
    p.add_argument("--thinking", action="store_true", help="Enable thinking/high-reasoning mode for each tool")
    p.add_argument("--resume", action="store_true", help="Auto-detect completed rounds and continue to target")
    p.add_argument("--run-id", dest="run_id", help="Specify a previous run ID")
    p.add_argument("--status", action="store_true", help="Show current run status and exit")
    p.add_argument("--cleanup", action="store_true", help="Delete artifacts for specified rounds")
    p.add_argument("--stop", action="store_true", help="Gracefully stop a running session after the current round")
    p.add_argument("--abort", action="store_true", help="Abort a running session immediately")
    p.add_argument("--force", action="store_true", help="Do not prompt for confirmation with --abort")
    p.add_argument("--list", dest="list_runs", action="store_true", help="List known runs and exit")
    p.add_argument("--round", dest="round_nums", type=str, help="Round number(s) to clean up, e.g. 3 or 2,3,4")
    return p



def _handle_sigterm(signum, frame) -> None:  # type: ignore[no-untyped-def]
    _abort_event.set()



def main() -> int:
    signal.signal(signal.SIGTERM, _handle_sigterm)

    parser = build_parser()
    args = parser.parse_args()

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

    tools = [t.strip() for t in args.tools.split(",") if t.strip() in ALL_TOOLS]
    if not tools:
        print(f"ERROR: no valid tools specified. Valid: {', '.join(ALL_TOOLS)}", file=sys.stderr)
        return 2

    if args.cleanup:
        if not args.round_nums:
            print("ERROR: --cleanup requires --round N (e.g. --round 3)", file=sys.stderr)
            return 2
        round_nums = [int(r.strip()) for r in args.round_nums.split(",") if r.strip().isdigit()]
        return cleanup_rounds(round_nums, tools, args.run_id)

    return run_all(tools, args.rounds, args.thinking, args.resume, args.run_id)


if __name__ == "__main__":
    sys.exit(main())
