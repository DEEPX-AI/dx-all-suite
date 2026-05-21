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

    # Delete artifacts for round 3 of all tools
    python .deepx/tests/e2e_runner.py --cleanup --round 3

    # Delete artifacts for round 3 of a specific tool
    python .deepx/tests/e2e_runner.py --cleanup --round 3 --tool claude-code

See .deepx/tests/README.md for full documentation.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

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
    "claude-code":  "agentic-e2e-claude-code-autopilot",
    "copilot-cli":  "agentic-e2e-copilot-cli-autopilot",
    "cursor-cli":   "agentic-e2e-cursor-cli-autopilot",
    "opencode-cli": "agentic-e2e-opencode-cli-autopilot",
    "codex-cli":    "agentic-e2e-codex-cli-autopilot",
}

# Thinking / high-reasoning mode env vars per tool
THINKING_ENV: Dict[str, Dict[str, str]] = {
    "claude-code":  {"DX_AGENTIC_E2E_CLAUDE_CODE_EXTRA_ARGS": "--effort xhigh"},
    "copilot-cli":  {"DX_AGENTIC_E2E_COPILOT_EXTRA_ARGS": "--effort xhigh"},
    "opencode-cli": {"DX_AGENTIC_E2E_OPENCODE_EXTRA_ARGS": "--variant high"},
    "codex-cli":    {"DX_AGENTIC_E2E_CODEX_EXTRA_ARGS": '-c model_reasoning_effort="xhigh"'},
    "cursor-cli":   {},  # quota exceeded; auto fallback, no thinking mode
}

# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

_state_lock = threading.Lock()


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
            "tool_states": {
                t: {"completed": [], "in_progress": None, "status": "pending"}
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
            (RUNNER_STATE_DIR.glob("*/state.json") if RUNNER_STATE_DIR.exists() else []),
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
            ts_state["completed"].append(
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
        round_num = state.next_round_num(tool)
        total = state.target_rounds

        _log(f"[{tool}] Round {round_num}/{total} START", log_path)
        state.mark_start(tool, round_num)

        # Snapshot results/ before run to detect the new result dir
        results_snapshot: set = set(RESULTS_ROOT.iterdir()) if RESULTS_ROOT.exists() else set()

        cmd = ["bash", str(TEST_SH), TOOL_CMD[tool]]
        with open(log_path, "a", encoding="utf-8") as flog:
            flog.write(f"\n{'='*60}\n[{_now()}] {tool} Round {round_num}/{total} START\n{'='*60}\n")
            flog.flush()
            proc = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                env=env,
                stdout=flog,
                stderr=subprocess.STDOUT,
            )

        exit_code = proc.returncode
        result_dir_name = _find_new_result_dir(tool, results_snapshot)
        artifact_dirs: List[str] = []
        if result_dir_name:
            artifact_dirs = _collect_artifact_dirs(RESULTS_ROOT / result_dir_name / "manifest.json")

        _log(f"[{tool}] Round {round_num}/{total} DONE (exit={exit_code})", log_path)
        state.mark_done(tool, round_num, result_dir_name, exit_code, artifact_dirs)

    _log(f"[{tool}] All {state.target_rounds} rounds complete.", log_path)


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
    state = _resolve_state(tools, target_rounds, thinking, resume, run_id)
    log_dir = state.log_dir

    all_done = all(state.remaining(t) == 0 for t in tools)
    if all_done:
        print(f"All tools already at {target_rounds} rounds. Nothing to do.")
        print(f"Use --status to inspect results, or increase --rounds.")
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
    with ThreadPoolExecutor(max_workers=len(tools)) as pool:
        for tool in tools:
            if state.remaining(tool) > 0:
                f = pool.submit(run_tool_rounds, tool, state, thinking, log_dir)
                futures_map[f] = tool

        for f in as_completed(futures_map):
            tool = futures_map[f]
            try:
                f.result()
                failed = sum(
                    1 for r in state.data["tool_states"][tool]["completed"] if r["exit_code"] != 0
                )
                if failed:
                    print(f"  [{tool}] {failed} round(s) had non-zero exit.")
                    overall_ok = False
            except Exception as exc:
                print(f"  [{tool}] ERROR: {exc}")
                overall_ok = False

    print(f"\n{'='*60}")
    print(f"  E2E Runner COMPLETE  run_id={state.run_id}")
    for t in tools:
        completed = state.data["tool_states"][t]["completed"]
        ok = sum(1 for r in completed if r["exit_code"] == 0)
        ng = sum(1 for r in completed if r["exit_code"] != 0)
        print(f"    {t}: {ok} PASS  {ng} FAIL  (total {len(completed)}/{target_rounds})")
    print(f"  State: {state.path}")
    print(f"{'='*60}\n")

    return 0 if overall_ok else 1


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
                # Update target in case caller raised it
                state.data["target_rounds"] = target_rounds
                state.save()
                return state
            print(f"WARNING: --run-id {run_id} not found; falling back to results/ detection")

        # Try "latest" symlink
        latest_path = RunState.find_latest()
        if latest_path:
            state = RunState.load(latest_path)
            print(f"Resuming latest run_id={state.run_id}")
            state.data["target_rounds"] = target_rounds
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
        state.save()
        return state

    # Fresh run
    new_run_id = _make_run_id()
    state = RunState(new_run_id, target_rounds, tools, thinking)
    state.save()
    return state


def _make_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


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
# Status command
# ---------------------------------------------------------------------------

def show_status(run_id: Optional[str]) -> None:
    state_path = _find_state_path(run_id)
    if state_path is None:
        print("No run state found. Run `e2e_runner.py --rounds N` to start.")
        return

    state = RunState.load(state_path)
    d = state.data
    print(f"\nRun ID  : {d['run_id']}")
    print(f"Created : {d.get('created_at', '?')}")
    print(f"Target  : {d['target_rounds']} rounds  Thinking: {d.get('thinking', False)}")
    print(f"State   : {state_path}\n")
    print(f"{'Tool':<16} {'Done':>5} {'Fail':>5} {'Status':<10} Last result dir")
    print(f"{'-'*16} {'-'*5} {'-'*5} {'-'*10} {'-'*40}")
    for tool in d.get("tools", ALL_TOOLS):
        ts = d["tool_states"].get(tool, {})
        completed = ts.get("completed", [])
        ok = sum(1 for r in completed if r["exit_code"] == 0)
        ng = sum(1 for r in completed if r["exit_code"] != 0)
        status = ts.get("status", "?")
        last = completed[-1]["result_dir_name"] if completed else "—"
        print(f"{tool:<16} {ok:>5} {ng:>5} {status:<10} {last or '—'}")
    print()

    # Show in-progress
    for tool in d.get("tools", ALL_TOOLS):
        ip = d["tool_states"].get(tool, {}).get("in_progress")
        if ip:
            print(f"  {tool}: Round {ip['round']} in progress since {ip.get('start_utc', '?')}")


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
    p.add_argument("--run-id", dest="run_id", help="Specify a previous run ID (use with --resume or --cleanup)")
    p.add_argument("--status", action="store_true", help="Show current run status and exit")
    p.add_argument("--cleanup", action="store_true", help="Delete artifacts for specified rounds")
    p.add_argument("--round", dest="round_nums", type=str, help="Round number(s) to clean up, e.g. 3 or 2,3,4")
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    tools = [t.strip() for t in args.tools.split(",") if t.strip() in ALL_TOOLS]
    if not tools:
        print(f"ERROR: no valid tools specified. Valid: {', '.join(ALL_TOOLS)}", file=sys.stderr)
        return 2

    if args.status:
        show_status(args.run_id)
        return 0

    if args.cleanup:
        if not args.round_nums:
            print("ERROR: --cleanup requires --round N (e.g. --round 3)", file=sys.stderr)
            return 2
        round_nums = [int(r.strip()) for r in args.round_nums.split(",") if r.strip().isdigit()]
        return cleanup_rounds(round_nums, tools, args.run_id)

    return run_all(tools, args.rounds, args.thinking, args.resume, args.run_id)


if __name__ == "__main__":
    sys.exit(main())
