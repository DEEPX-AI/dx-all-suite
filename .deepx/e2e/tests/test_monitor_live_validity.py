# SPDX-License-Identifier: Apache-2.0
"""Tests for e2e_monitor.py LIVE/snapshot validity & effective-status enrichment.

Covers the three fixes that surface salvage validity in the live monitor + snapshot:
  - Fix 1: Round Progress "Status" reflects an active salvage as "re-running"
           (_progress_status_label + _make_progress_table salvage_active=True).
  - Fix 2: Completed Rounds table gains a per-round "Validity" column matched by
           result_dir_name (_make_completed_rounds_table(data, statuses)).
  - Fix 3: a shared _statuses_for(run_id, data) helper used by the live loop,
           print_snapshot, and _print_validity_block.

Round dirs are staged on tmp_path mirroring test_monitor_validity.py (DONE
sentinel = valid, rate-limit blob = env-failed). Table rendering is asserted by
capturing a rich Console into a StringIO (no brittle markup-string assertions).
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

_E2E_DIR = Path(__file__).resolve().parents[1]  # .deepx/e2e/
sys.path.insert(0, str(_E2E_DIR))

import e2e_monitor as mon  # noqa: E402


# --- scenario blobs (shapes the runner classifier understands) --------------

DONE_MD = "Run complete.\n[DX-AGENT-DEV: DONE (output-dir: dx-compiler/dx-agent-dev/x)]\n"
START_ONLY_MD = "[DX-AGENT-DEV: START]\nworking...\n"
RATE_LIMIT_JSONL = (
    '{"type":"error","error":{"message":"rate limit exceeded; please wait and retry"}}\n'
)


def _valid_scenario(parent: Path, name: str) -> Path:
    sd = parent / name
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "s-session.md").write_text(DONE_MD, encoding="utf-8")
    return sd


def _rate_limit_scenario(parent: Path, name: str) -> Path:
    sd = parent / name
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "s-session.md").write_text(START_ONLY_MD, encoding="utf-8")
    (sd / "s-stream.jsonl").write_text(RATE_LIMIT_JSONL, encoding="utf-8")
    return sd


def _round(parent: Path, ts: str, scenarios: dict) -> Path:
    rd = parent / f"{ts}_aaa111_claude-code-autopilot"
    rd.mkdir(parents=True)
    for scen, kind in scenarios.items():
        key = f"claude_code__{scen}"
        if kind == "valid":
            _valid_scenario(rd, key)
        elif kind == "rate-limit":
            _rate_limit_scenario(rd, key)
    (rd / "manifest.json").write_text("{}", encoding="utf-8")
    return rd


def _render(renderable) -> str:
    """Render a rich renderable into a plain string via a StringIO Console."""
    from rich.console import Console

    buf = io.StringIO()
    Console(file=buf, width=200, force_terminal=False, no_color=True).print(renderable)
    return buf.getvalue()


# --- Fix 1: progress status label -------------------------------------------

def test_progress_status_label_done_active_is_rerunning():
    assert mon._progress_status_label("done", True) == "re-running"


def test_progress_status_label_running_inactive_is_running():
    assert mon._progress_status_label("running", False) == "running"


def test_progress_status_label_done_inactive_is_done():
    assert mon._progress_status_label("done", False) == "done"


def test_progress_status_label_any_active_is_rerunning():
    # Any state + active salvage → re-running (mirrors _effective_status).
    assert mon._progress_status_label("running", True) == "re-running"
    assert mon._progress_status_label("pending", True) == "re-running"


def test_make_progress_table_salvage_active_renders_rerunning():
    data = {
        "target_rounds": 5,
        "tools": ["claude-code"],
        "tool_states": {"claude-code": {"status": "done", "completed": [
            {"round": 1, "exit_code": 0},
        ]}},
    }
    out = _render(mon._make_progress_table(data, None, salvage_active=True))
    assert "re-running" in out
    # The "all complete" scenarios text must be replaced while re-running.
    assert "all complete" not in out


def test_make_progress_table_no_salvage_keeps_done():
    data = {
        "target_rounds": 5,
        "tools": ["claude-code"],
        "tool_states": {"claude-code": {"status": "done", "completed": [
            {"round": 1, "exit_code": 0},
        ]}},
    }
    out = _render(mon._make_progress_table(data, None, salvage_active=False))
    assert "done" in out
    assert "re-running" not in out


# --- Fix 2: completed-rounds validity column --------------------------------

def test_completed_rounds_table_shows_validity_icons():
    statuses = [
        {"round_index": 1, "round_dir": "r1-autopilot", "status": "valid"},
        {"round_index": 2, "round_dir": "r2-autopilot", "status": "env-failed",
         "detail": "rate-limit — pending re-run"},
    ]
    data = {
        "tools": ["claude-code"],
        "tool_states": {"claude-code": {"completed": [
            {"round": 1, "result_dir_name": "r1-autopilot", "exit_code": 0,
             "start_utc": "2026-06-12T10:00:00Z", "end_utc": "2026-06-12T10:30:00Z"},
            {"round": 2, "result_dir_name": "r2-autopilot", "exit_code": 1,
             "start_utc": "2026-06-12T11:00:00Z", "end_utc": "2026-06-12T11:30:00Z"},
        ]}},
    }
    tbl = mon._make_completed_rounds_table(data, statuses)
    assert tbl is not None
    out = _render(tbl)
    assert "Validity" in out
    assert "valid" in out
    assert "env-failed" in out


def test_completed_rounds_table_no_match_shows_dash():
    statuses = [{"round_index": 1, "round_dir": "other-autopilot", "status": "valid"}]
    data = {
        "tools": ["claude-code"],
        "tool_states": {"claude-code": {"completed": [
            {"round": 1, "result_dir_name": "r1-autopilot", "exit_code": 0},
        ]}},
    }
    out = _render(mon._make_completed_rounds_table(data, statuses))
    assert "—" in out


def test_completed_rounds_table_statuses_none_still_renders():
    # Backwards-compatible: no statuses → still a valid table (Validity = —).
    data = {
        "tools": ["claude-code"],
        "tool_states": {"claude-code": {"completed": [
            {"round": 1, "result_dir_name": "r1-autopilot", "exit_code": 0},
        ]}},
    }
    tbl = mon._make_completed_rounds_table(data, None)
    assert tbl is not None
    out = _render(tbl)
    assert "Validity" in out


# --- Fix 3: _statuses_for shared helper -------------------------------------

def test_statuses_for_active_salvage(tmp_path, monkeypatch):
    results = tmp_path / "results" / "20260612_194959"
    results.mkdir(parents=True)
    six = ("compiler", "dx_app", "dx_stream", "dx_stream_cascaded", "runtime", "suite")
    r1 = _round(results, "20260612_210247", {s: "valid" for s in six})
    r2 = _round(results, "20260612_215213",
                {s: "valid" for s in six[:-1]} | {"suite": "rate-limit"})

    salvage = {"status": "running", "round_dir": r2.name, "attempt": 1,
               "scenarios": list(six), "pid": 12345}

    monkeypatch.setattr(mon._E2E_RUNNER, "run_results_dir", lambda rid: results)
    monkeypatch.setattr(mon, "_load_salvage", lambda rid: salvage)
    monkeypatch.setattr(mon, "_pid_alive", lambda pid: True)

    state = {"tool_states": {"claude-code": {"completed": [
        {"round": 1, "result_dir_name": r1.name},
        {"round": 2, "result_dir_name": r2.name},
    ]}}}
    statuses, sv, active = mon._statuses_for("20260612_194959", state)
    assert active is True
    assert sv == salvage
    assert [s["status"] for s in statuses] == ["valid", "re-running"]


def test_statuses_for_no_salvage(tmp_path, monkeypatch):
    results = tmp_path / "results" / "20260612_194959"
    results.mkdir(parents=True)
    six = ("compiler", "dx_app", "dx_stream", "dx_stream_cascaded", "runtime", "suite")
    r1 = _round(results, "20260612_210247", {s: "valid" for s in six})

    monkeypatch.setattr(mon._E2E_RUNNER, "run_results_dir", lambda rid: results)
    monkeypatch.setattr(mon, "_load_salvage", lambda rid: None)
    monkeypatch.setattr(mon, "_pid_alive", lambda pid: False)

    state = {"tool_states": {"claude-code": {"completed": [
        {"round": 1, "result_dir_name": r1.name},
    ]}}}
    statuses, sv, active = mon._statuses_for("20260612_194959", state)
    assert active is False
    assert sv is None
    assert [s["status"] for s in statuses] == ["valid"]


def test_statuses_for_missing_dir_never_crashes(monkeypatch):
    monkeypatch.setattr(mon._E2E_RUNNER, "run_results_dir",
                        lambda rid: Path("/nonexistent/results/x"))
    monkeypatch.setattr(mon, "_load_salvage", lambda rid: None)
    statuses, sv, active = mon._statuses_for("missing", {})
    assert statuses == []
    assert active is False
