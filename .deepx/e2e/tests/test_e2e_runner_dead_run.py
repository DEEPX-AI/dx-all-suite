# SPDX-License-Identifier: Apache-2.0
"""Tests for two related force-killed-run fixes in e2e_runner.

FIX 1 — _cmdline_is_running_launcher / _find_runner_pids_by_cmdline:
  Control-command invocations (--abort, --stop, --status, --list, --cleanup,
  --redo-env-failures) must NOT be returned as "running launcher" candidates.
  Only a real launcher cmdline (containing --rounds) with the run_id matches.

FIX 2 — _finalize_dead_run + do_abort / do_stop dead-pid fallback:
  When a run is FORCE-KILLED (SIGKILL / TaskStop / exit 144) its state.json
  is left with status="running" and tool_states[tool]["status"]="running".
  Calling _finalize_dead_run must set both the run-level and per-tool statuses
  to the requested terminal_status and clear in_progress; the already-terminal
  tools must be left untouched.
  do_abort with a dead-pid run must end with state status="aborted".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parents[1]  # .deepx/e2e/
sys.path.insert(0, str(_TESTS_DIR))

import e2e_runner as er  # noqa: E402


# ---------------------------------------------------------------------------
# FIX 1 — _cmdline_is_running_launcher predicate
# ---------------------------------------------------------------------------

RUN_ID = "20260601_120000"
SELF_PID = 99999  # fake self-pid that won't match any of our test pids
OTHER_PID = 12345


def _launcher_cmd(extra: str = "") -> str:
    """Return a cmdline that looks like a real running launcher."""
    return (
        f"python3 /repo/.deepx/e2e/e2e_runner.py "
        f"--tools claude-code --rounds 5 --run-id {RUN_ID} {extra}"
    ).strip()


@pytest.mark.parametrize("flag", er._CONTROL_FLAGS)
def test_control_flag_not_a_running_launcher(flag):
    """Any cmdline containing a control flag is NOT a running launcher."""
    cmd = (
        f"python3 /repo/.deepx/e2e/e2e_runner.py "
        f"{flag} --run-id {RUN_ID} --force"
    )
    assert er._cmdline_is_running_launcher(cmd, RUN_ID, SELF_PID, OTHER_PID) is False


def test_rounds_launcher_with_run_id_is_launcher():
    """A --rounds launcher cmdline containing the run_id IS a running launcher."""
    cmd = _launcher_cmd()
    assert er._cmdline_is_running_launcher(cmd, RUN_ID, SELF_PID, OTHER_PID) is True


def test_launcher_without_run_id_not_matched():
    """A launcher for a *different* run_id must not be returned."""
    cmd = (
        "python3 /repo/.deepx/e2e/e2e_runner.py "
        "--tools claude-code --rounds 5 --run-id 20260101_000000"
    )
    assert er._cmdline_is_running_launcher(cmd, RUN_ID, SELF_PID, OTHER_PID) is False


def test_self_pid_excluded():
    """The current process is never returned, even with a matching cmdline."""
    cmd = _launcher_cmd()
    assert er._cmdline_is_running_launcher(cmd, RUN_ID, OTHER_PID, OTHER_PID) is False


def test_non_runner_script_not_matched():
    """A cmdline that mentions a different script is not matched."""
    cmd = f"python3 /repo/.deepx/e2e/e2e_monitor.py --run-id {RUN_ID}"
    assert er._cmdline_is_running_launcher(cmd, RUN_ID, SELF_PID, OTHER_PID) is False


# ---------------------------------------------------------------------------
# FIX 2 — _finalize_dead_run
# ---------------------------------------------------------------------------

def _build_state(tmp_path: Path, monkeypatch) -> tuple[str, "er.RunState"]:
    """Build a minimal stale state with two tools, one still "running"."""
    run_id = "20260601_dead01"
    state_root = tmp_path / "runner_state"
    monkeypatch.setattr(er, "RUNNER_STATE_DIR", state_root)

    state_dir = state_root / run_id
    state_dir.mkdir(parents=True)
    (state_dir / "logs").mkdir()

    data = {
        "run_id": run_id,
        "target_rounds": 3,
        "thinking": False,
        "mode": "sequential",
        "tools": ["claude-code", "copilot-cli"],
        "runner_pid": None,
        "status": "running",
        "tool_states": {
            "claude-code": {
                "completed": [],
                "in_progress": {"round": 1, "start_utc": "2026-06-01T12:00:00Z"},
                "status": "running",
                "pid": None,
            },
            "copilot-cli": {
                "completed": [{"round": 1}],
                "in_progress": None,
                "status": "done",
                "pid": None,
            },
        },
    }
    state_path = state_dir / "state.json"
    state_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Load via RunState so we have a real object
    state = er.RunState.load(state_path)
    return run_id, state


def test_finalize_dead_run_sets_terminal_status(tmp_path, monkeypatch):
    """_finalize_dead_run sets run-level status to terminal_status."""
    _rid, state = _build_state(tmp_path, monkeypatch)
    er._finalize_dead_run(state, "aborted")

    reloaded = json.loads(state.path.read_text())
    assert reloaded["status"] == "aborted"


def test_finalize_dead_run_finalizes_running_tool(tmp_path, monkeypatch):
    """Running tool state is set to terminal_status and in_progress cleared."""
    _rid, state = _build_state(tmp_path, monkeypatch)
    er._finalize_dead_run(state, "aborted")

    reloaded = json.loads(state.path.read_text())
    ts = reloaded["tool_states"]["claude-code"]
    assert ts["status"] == "aborted"
    assert ts["in_progress"] is None


def test_finalize_dead_run_leaves_done_tool_untouched(tmp_path, monkeypatch):
    """A tool already in terminal 'done' state must not be touched."""
    _rid, state = _build_state(tmp_path, monkeypatch)
    er._finalize_dead_run(state, "aborted")

    reloaded = json.loads(state.path.read_text())
    ts = reloaded["tool_states"]["copilot-cli"]
    assert ts["status"] == "done"  # unchanged


def test_finalize_dead_run_returns_count(tmp_path, monkeypatch):
    """Return value is the number of per-tool states that were finalized."""
    _rid, state = _build_state(tmp_path, monkeypatch)
    count = er._finalize_dead_run(state, "aborted")
    # Only claude-code was "running" — copilot-cli was "done"
    assert count == 1


def test_finalize_dead_run_stopped_variant(tmp_path, monkeypatch):
    """Works with 'stopped' as the terminal status too."""
    _rid, state = _build_state(tmp_path, monkeypatch)
    er._finalize_dead_run(state, "stopped")

    reloaded = json.loads(state.path.read_text())
    assert reloaded["status"] == "stopped"
    assert reloaded["tool_states"]["claude-code"]["status"] == "stopped"


# ---------------------------------------------------------------------------
# FIX 2 — do_abort on a dead-pid run reconciles to "aborted"
# ---------------------------------------------------------------------------

def _build_dead_run_state(tmp_path: Path, monkeypatch) -> tuple[str, Path]:
    """Build a state.json whose runner_pid is guaranteed dead."""
    run_id = "20260601_deadrun"
    state_root = tmp_path / "runner_state"
    monkeypatch.setattr(er, "RUNNER_STATE_DIR", state_root)

    state_dir = state_root / run_id
    state_dir.mkdir(parents=True)
    (state_dir / "logs").mkdir()

    # pid=999999999 is always dead on any real Linux system
    data = {
        "run_id": run_id,
        "target_rounds": 2,
        "thinking": False,
        "mode": "sequential",
        "tools": ["claude-code"],
        "runner_pid": 999999999,
        "status": "running",
        "tool_states": {
            "claude-code": {
                "completed": [],
                "in_progress": {"round": 1, "start_utc": "2026-06-01T00:00:00Z"},
                "status": "running",
                "pid": None,
            },
        },
    }
    state_path = state_dir / "state.json"
    state_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return run_id, state_path


def test_do_abort_dead_pid_reconciles_to_aborted(tmp_path, monkeypatch, capsys):
    """do_abort on a force-killed (dead-pid) run finalizes state to 'aborted'."""
    run_id, state_path = _build_dead_run_state(tmp_path, monkeypatch)

    # Prevent _find_runner_pids_by_cmdline from scanning real /proc
    # (we want to simulate "no live runner found anywhere").
    monkeypatch.setattr(er, "_find_runner_pids_by_cmdline", lambda rid: [])

    # Call the function directly — do NOT invoke the CLI.
    ret = er.do_abort(run_id, force=True)
    assert ret == 0

    reloaded = json.loads(state_path.read_text())
    assert reloaded["status"] == "aborted"
    ts = reloaded["tool_states"]["claude-code"]
    assert ts["status"] == "aborted"
    assert ts["in_progress"] is None

    captured = capsys.readouterr()
    assert "reconciled stale state to 'aborted'" in captured.err


def test_do_abort_live_runner_keeps_abort_requested(tmp_path, monkeypatch):
    """When a live runner IS signaled, status stays 'abort-requested' (existing behavior)."""
    run_id, state_path = _build_dead_run_state(tmp_path, monkeypatch)

    fake_live_pid = 77777

    # Simulate: runner_pid (999999999) is dead, but cmdline scan returns one live pid.
    # Monkeypatch _pid_alive so 999999999 → False (dead), everything else → True.
    original_pid_alive = er._pid_alive
    def fake_pid_alive(pid):
        if pid == 999999999:
            return False
        return original_pid_alive(pid)
    monkeypatch.setattr(er, "_pid_alive", fake_pid_alive)

    # Monkeypatch _find_runner_pids_by_cmdline to return our fake live pid.
    monkeypatch.setattr(er, "_find_runner_pids_by_cmdline", lambda rid: [fake_live_pid])

    # Monkeypatch os.kill to record calls and not actually signal anyone.
    kill_calls: list[tuple[int, int]] = []
    def fake_kill(pid: int, sig: int) -> None:
        kill_calls.append((pid, sig))
    monkeypatch.setattr(er.os, "kill", fake_kill)

    ret = er.do_abort(run_id, force=True)
    assert ret == 0

    # A signal was attempted at the fake live pid
    assert any(pid == fake_live_pid for pid, _sig in kill_calls)

    # Status must be "abort-requested", not "aborted"
    reloaded = json.loads(state_path.read_text())
    assert reloaded["status"] == "abort-requested"
