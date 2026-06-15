# SPDX-License-Identifier: Apache-2.0
"""Tests for e2e_monitor.py validity- & salvage-awareness.

Covers the three new PURE functions:
  - _round_status      (single round → valid / env-failed / incomplete / re-running)
  - _run_round_statuses (a run's results dir → R1..RN status list)
  - _validity_summary   (compact one-liner for --list)

Round dirs are staged on tmp_path with valid / env-failed / incomplete scenario
subdirs, mirroring test_e2e_runner_env_redo.py (DONE sentinel vs rate-limit blob).
Classification is delegated to e2e_runner via e2e_monitor, so the fixtures use
the same scenario shapes the runner understands.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_E2E_DIR = Path(__file__).resolve().parents[1]  # .deepx/e2e/
sys.path.insert(0, str(_E2E_DIR))

import e2e_monitor as mon  # noqa: E402


# --- scenario blobs (shapes the runner classifier understands) --------------

DONE_MD = "Run complete.\n[DX-AGENT-DEV: DONE (output-dir: dx-compiler/dx-agent-dev/x)]\n"
START_ONLY_MD = "[DX-AGENT-DEV: START]\nworking...\n"
REAL_WORK_JSONL = (
    '{"type":"assistant","content":"..."}\n' * 30
    + '{"type":"tool_use","name":"bash"}\n' * 30
)
RATE_LIMIT_JSONL = (
    '{"type":"error","error":{"message":"rate limit exceeded; please wait and retry"}}\n'
)


def _make_scenario(parent: Path, name: str, *, files: dict | None = None,
                   session_subdir: str | None = None) -> Path:
    sd = parent / name
    sd.mkdir(parents=True, exist_ok=True)
    for fn, txt in (files or {}).items():
        (sd / fn).write_text(txt, encoding="utf-8")
    if session_subdir:
        (sd / session_subdir).mkdir(parents=True, exist_ok=True)
    return sd


def _valid_scenario(parent: Path, name: str) -> Path:
    return _make_scenario(parent, name, files={"s-session.md": DONE_MD})


def _rate_limit_scenario(parent: Path, name: str) -> Path:
    return _make_scenario(parent, name,
                          files={"s-session.md": START_ONLY_MD,
                                 "s-stream.jsonl": RATE_LIMIT_JSONL})


def _incomplete_scenario(parent: Path, name: str) -> Path:
    return _make_scenario(parent, name,
                          files={"s-session.md": START_ONLY_MD,
                                 "s-stream.jsonl": REAL_WORK_JSONL},
                          session_subdir="out")


def _round(parent: Path, ts: str, scenarios: dict) -> Path:
    """Stage a <ts>_aaa111_claude-code-autopilot round dir with scenarios."""
    rd = parent / f"{ts}_aaa111_claude-code-autopilot"
    rd.mkdir(parents=True)
    for scen, kind in scenarios.items():
        key = f"claude_code__{scen}"
        if kind == "valid":
            _valid_scenario(rd, key)
        elif kind == "rate-limit":
            _rate_limit_scenario(rd, key)
        elif kind == "incomplete":
            _incomplete_scenario(rd, key)
    (rd / "manifest.json").write_text("{}", encoding="utf-8")
    return rd


# --- sanity: classifier reused from e2e_runner is available -----------------

def test_e2e_runner_import_available():
    # The monitor must successfully import the runner's classifier; otherwise
    # every round would degrade to "empty" and these tests would be meaningless.
    assert mon._E2E_RUNNER is not None
    valid, incomplete, envfail, total, sigs = mon._analyze_round_env(Path("/nonexistent"))
    assert (valid, incomplete, envfail, total) == (0, 0, 0, 0)


# --- _round_status ----------------------------------------------------------

def test_round_status_valid(tmp_path):
    rd = _round(tmp_path, "20260612_000001",
                {s: "valid" for s in ("compiler", "dx_app", "suite")})
    st = mon._round_status(rd, salvage=None, salvage_pid_alive=False)
    assert st["status"] == "valid"
    assert st["counts"][0] == 3  # valid count


def test_round_status_env_failed_rate_limit(tmp_path):
    rd = _round(tmp_path, "20260612_000002",
                {"compiler": "valid", "dx_app": "valid", "suite": "rate-limit"})
    st = mon._round_status(rd, salvage=None, salvage_pid_alive=False)
    assert st["status"] == "env-failed"
    assert "pending re-run" in st["detail"]


def test_round_status_incomplete_only(tmp_path):
    rd = _round(tmp_path, "20260612_000003",
                {"compiler": "valid", "dx_app": "incomplete"})
    st = mon._round_status(rd, salvage=None, salvage_pid_alive=False)
    assert st["status"] == "incomplete"


def test_round_status_empty(tmp_path):
    rd = tmp_path / "20260612_000099_aaa111_claude-code-autopilot"
    rd.mkdir()
    st = mon._round_status(rd, salvage=None, salvage_pid_alive=False)
    assert st["status"] == "empty"


def test_round_status_re_running_not_classified(tmp_path):
    # A round matching a LIVE salvage marker is reported re-running WITHOUT
    # classification — even though its scenarios currently look rate-limited.
    rd = _round(tmp_path, "20260612_000004",
                {"compiler": "valid", "suite": "rate-limit"})
    salvage = {
        "status": "running",
        "round_dir": rd.name,
        "attempt": 2,
        "scenarios": ["compiler", "suite"],
        "pid": 12345,
    }
    st = mon._round_status(rd, salvage=salvage, salvage_pid_alive=True)
    assert st["status"] == "re-running"
    assert "attempt 2" in st["detail"]
    assert "compiler" in st["detail"]


def test_round_status_re_running_ignored_when_pid_dead(tmp_path):
    # Salvage marker present but pid dead → fall back to classification.
    rd = _round(tmp_path, "20260612_000005",
                {"compiler": "valid", "suite": "rate-limit"})
    salvage = {"status": "running", "round_dir": rd.name, "attempt": 1,
               "scenarios": ["suite"], "pid": 999999}
    st = mon._round_status(rd, salvage=salvage, salvage_pid_alive=False)
    assert st["status"] == "env-failed"


def test_round_status_re_running_only_matching_dir(tmp_path):
    # Salvage live but targeting a DIFFERENT round → this round is classified.
    rd = _round(tmp_path, "20260612_000006",
                {s: "valid" for s in ("compiler", "dx_app")})
    salvage = {"status": "running", "round_dir": "some_other_round-autopilot",
               "attempt": 1, "scenarios": ["suite"], "pid": 12345}
    st = mon._round_status(rd, salvage=salvage, salvage_pid_alive=True)
    assert st["status"] == "valid"


# --- _run_round_statuses ----------------------------------------------------

def test_run_round_statuses_five_rounds(tmp_path):
    results = tmp_path / "results" / "20260612_194959"
    results.mkdir(parents=True)
    six = ("compiler", "dx_app", "dx_stream", "dx_stream_cascaded", "runtime", "suite")

    _round(results, "20260612_210247", {s: "valid" for s in six})              # R1 valid
    _round(results, "20260612_215200", {s: "valid" for s in six})              # R2 valid
    r3 = _round(results, "20260612_215213",                                    # R3 re-running
                {s: "valid" for s in six[:-1]} | {"suite": "rate-limit"})
    _round(results, "20260612_215228",                                         # R4 env-failed
           {s: "valid" for s in six[:-1]} | {"suite": "rate-limit"})
    _round(results, "20260612_215242",                                         # R5 env-failed
           {s: "valid" for s in six[:-1]} | {"suite": "rate-limit"})

    salvage = {"status": "running", "round_dir": r3.name, "attempt": 1,
               "scenarios": list(six), "pid": 12345}

    # Pretend the salvage pid is alive by monkeypatching _pid_alive.
    orig = mon._pid_alive
    mon._pid_alive = lambda pid: True
    try:
        statuses = mon._run_round_statuses(results, salvage)
    finally:
        mon._pid_alive = orig

    assert [s["round_index"] for s in statuses] == [1, 2, 3, 4, 5]
    assert [s["status"] for s in statuses] == [
        "valid", "valid", "re-running", "env-failed", "env-failed",
    ]


def test_run_round_statuses_state_excludes_scratch_dir(tmp_path):
    """With state, enumerate ONLY the canonical rounds — a transient salvage
    scratch autopilot dir on disk must NOT appear as a phantom extra round."""
    results = tmp_path / "results" / "20260612_194959"
    results.mkdir(parents=True)
    six = ("compiler", "dx_app", "dx_stream", "dx_stream_cascaded", "runtime", "suite")
    r1 = _round(results, "20260612_210247", {s: "valid" for s in six})
    r2 = _round(results, "20260612_215200", {s: "valid" for s in six})
    # A transient cleanup_resume scratch dir on disk (NOT in state.completed):
    _round(results, "20260615_141417", {"runtime": "valid"})

    state = {"tool_states": {"claude-code": {"completed": [
        {"round": 1, "result_dir_name": r1.name},
        {"round": 2, "result_dir_name": r2.name},
    ]}}}
    statuses = mon._run_round_statuses(results, None, state)
    assert [s["round_index"] for s in statuses] == [1, 2]
    assert {s["round_dir"] for s in statuses} == {r1.name, r2.name}  # scratch excluded


def test_run_round_statuses_missing_dir(tmp_path):
    assert mon._run_round_statuses(tmp_path / "nope", None) == []


# --- _validity_summary ------------------------------------------------------

def test_validity_summary_mixed():
    statuses = [
        {"round_index": 1, "status": "valid"},
        {"round_index": 2, "status": "valid"},
        {"round_index": 3, "status": "re-running"},
        {"round_index": 4, "status": "env-failed"},
        {"round_index": 5, "status": "env-failed"},
    ]
    assert mon._validity_summary(statuses) == "valid:2/5 ⟳R3 ✗R4,R5"


def test_validity_summary_all_valid():
    statuses = [{"round_index": i, "status": "valid"} for i in range(1, 6)]
    assert mon._validity_summary(statuses) == "valid:5/5"


# --- _monitor_should_exit (live loop should keep refreshing during salvage) ---

def _data(*statuses):
    return {"tools": [f"t{i}" for i in range(len(statuses))],
            "tool_states": {f"t{i}": {"status": s} for i, s in enumerate(statuses)}}

def test_monitor_should_exit_all_done_no_salvage():
    assert mon._monitor_should_exit(_data("done"), False) is True

def test_monitor_should_exit_all_done_but_salvage_active():
    # state says done, but a salvage is re-running in place → keep refreshing
    assert mon._monitor_should_exit(_data("done"), True) is False

def test_monitor_should_exit_not_all_done():
    assert mon._monitor_should_exit(_data("done", "running"), False) is False

def test_monitor_should_exit_not_done_and_salvage():
    assert mon._monitor_should_exit(_data("running"), True) is False
