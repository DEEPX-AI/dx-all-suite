# SPDX-License-Identifier: Apache-2.0
"""Tests for e2e_monitor.py PER-SCENARIO status enrichment.

Covers the per-scenario granularity added on top of the per-round validity:
  - Fix A: Round Validity table gains a "Scenarios" column showing a compact
           per-scenario breakdown (cmp/app/str/csc/rt/ste with icons), and
           _round_status carries a "scenarios" dict (+ "rerun_targets" when
           re-running).
  - Fix B: Round Progress "Scenarios (current round)" restores per-scenario
           detail for the salvage's CURRENT re-run round (salvage-aware).

New PURE helpers under test:
  - _round_scenarios(round_dir) -> {scenario: verdict}
  - _scenario_cells(scenarios, rerun_targets=None) -> "cmp✓ app✓ ..."

Round dirs are staged on tmp_path mirroring test_monitor_validity.py
(DONE sentinel = valid, rate-limit blob = env-failed, real-work-no-DONE =
incomplete). Classification is delegated to e2e_runner via e2e_monitor.
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
REAL_WORK_JSONL = (
    '{"type":"assistant","content":"..."}\n' * 30
    + '{"type":"tool_use","name":"bash"}\n' * 30
)
RATE_LIMIT_JSONL = (
    '{"type":"error","error":{"message":"rate limit exceeded; please wait and retry"}}\n'
)

SIX = ("compiler", "dx_app", "dx_stream", "dx_stream_cascaded", "runtime", "suite")


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


def _render(renderable) -> str:
    """Render a rich renderable into a plain string via a StringIO Console."""
    from rich.console import Console

    buf = io.StringIO()
    Console(file=buf, width=240, force_terminal=False, no_color=True).print(renderable)
    return buf.getvalue()


# --- _round_scenarios -------------------------------------------------------

def test_round_scenarios_four_valid_two_envfail(tmp_path):
    rd = _round(tmp_path, "20260612_000001",
                {s: "valid" for s in SIX[:4]}
                | {"runtime": "rate-limit", "suite": "rate-limit"})
    scn = mon._round_scenarios(rd)
    assert scn == {
        "compiler": "valid",
        "dx_app": "valid",
        "dx_stream": "valid",
        "dx_stream_cascaded": "valid",
        "runtime": "envfail",
        "suite": "envfail",
    }


def test_round_scenarios_missing_dir_is_skip(tmp_path):
    # Only stage 4 of 6 scenarios → the two missing scenario subdirs are "skip".
    rd = _round(tmp_path, "20260612_000002", {s: "valid" for s in SIX[:4]})
    scn = mon._round_scenarios(rd)
    assert scn["runtime"] == "skip"
    assert scn["suite"] == "skip"
    assert scn["compiler"] == "valid"


def test_round_scenarios_incomplete(tmp_path):
    rd = _round(tmp_path, "20260612_000003",
                {"compiler": "valid", "dx_app": "incomplete"})
    scn = mon._round_scenarios(rd)
    assert scn["dx_app"] == "incomplete"


# --- _scenario_cells --------------------------------------------------------

def test_scenario_cells_basic():
    scn = {
        "compiler": "valid",
        "dx_app": "valid",
        "dx_stream": "valid",
        "dx_stream_cascaded": "valid",
        "runtime": "envfail",
        "suite": "envfail",
    }
    assert mon._scenario_cells(scn) == "cmp✓ app✓ str✓ csc✓ rt✗ ste✗"


def test_scenario_cells_canonical_order_and_icons():
    scn = {
        "compiler": "skip",
        "dx_app": "incomplete",
        "dx_stream": "valid",
        "dx_stream_cascaded": "skip",
        "runtime": "envfail",
        "suite": "valid",
    }
    # canonical order; · skip, △ incomplete, ✓ valid, ✗ envfail
    assert mon._scenario_cells(scn) == "cmp· app△ str✓ csc· rt✗ ste✓"


def test_scenario_cells_rerun_targets_override():
    scn = {
        "compiler": "valid",
        "dx_app": "valid",
        "dx_stream": "valid",
        "dx_stream_cascaded": "valid",
        "runtime": "envfail",
        "suite": "envfail",
    }
    out = mon._scenario_cells(scn, rerun_targets={"runtime", "suite"})
    # runtime + suite are targets AND not-yet-valid → ⟳; others unchanged
    assert out == "cmp✓ app✓ str✓ csc✓ rt⟳ ste⟳"


def test_scenario_cells_valid_target_shows_done_not_rerunning():
    # Real R4 case: salvage targeted ALL 6, but cmp..rt already merged (valid);
    # only suite still re-running. A VALID target must show ✓, not ⟳.
    scn = {
        "compiler": "valid", "dx_app": "valid", "dx_stream": "valid",
        "dx_stream_cascaded": "valid", "runtime": "valid", "suite": "skip",
    }
    out = mon._scenario_cells(scn, rerun_targets=set(mon.ROUND_SCENARIO_KEYS))
    assert out == "cmp✓ app✓ str✓ csc✓ rt✓ ste⟳"


# --- _round_status carries scenarios (+ rerun_targets when re-running) ------

def test_round_status_includes_scenarios(tmp_path):
    rd = _round(tmp_path, "20260612_000010",
                {s: "valid" for s in SIX[:-1]} | {"suite": "rate-limit"})
    st = mon._round_status(rd, salvage=None, salvage_pid_alive=False)
    assert "scenarios" in st
    assert st["scenarios"]["suite"] == "envfail"
    assert st["scenarios"]["compiler"] == "valid"
    # No active salvage → no rerun_targets key (or empty).
    assert not st.get("rerun_targets")


def test_round_status_rerunning_includes_rerun_targets(tmp_path):
    rd = _round(tmp_path, "20260612_000011",
                {s: "valid" for s in SIX[:-1]} | {"suite": "rate-limit"})
    salvage = {
        "status": "running",
        "round_dir": rd.name,
        "attempt": 1,
        "scenarios": ["runtime", "suite"],
        "pid": 12345,
    }
    st = mon._round_status(rd, salvage=salvage, salvage_pid_alive=True)
    assert st["status"] == "re-running"
    assert "scenarios" in st
    assert st["rerun_targets"] == {"runtime", "suite"}


# --- render smoke: Round Validity table per-scenario column -----------------

def test_validity_table_renders_scenario_cells(tmp_path, monkeypatch):
    results = tmp_path / "results" / "20260612_194959"
    results.mkdir(parents=True)
    r1 = _round(results, "20260612_210247", {s: "valid" for s in SIX})
    r2 = _round(results, "20260612_215213",
                {s: "valid" for s in SIX[:-1]} | {"suite": "rate-limit"})

    monkeypatch.setattr(mon._E2E_RUNNER, "run_results_dir", lambda rid: results)
    monkeypatch.setattr(mon, "_load_salvage", lambda rid: None)
    monkeypatch.setattr(mon, "_pid_alive", lambda pid: False)

    state = {"tool_states": {"claude-code": {"completed": [
        {"round": 1, "result_dir_name": r1.name},
        {"round": 2, "result_dir_name": r2.name},
    ]}}}
    statuses, _sv, _active = mon._statuses_for("20260612_194959", state)
    out = _render(mon._make_validity_table(statuses))
    assert "Scenarios" in out
    # R1: all six valid
    assert "cmp✓ app✓ str✓ csc✓ rt✓ ste✓" in out
    # R2: suite env-failed
    assert "ste✗" in out


# --- render smoke: Round Progress current-round salvage detail --------------

def test_progress_table_salvage_shows_per_scenario_detail(tmp_path, monkeypatch):
    results = tmp_path / "results" / "20260612_194959"
    results.mkdir(parents=True)
    # R1/R2/R3 canonical; R3 is the round being re-run (runtime+suite targets).
    _round(results, "20260612_210247", {s: "valid" for s in SIX})
    _round(results, "20260612_215200", {s: "valid" for s in SIX})
    r3 = _round(results, "20260612_215213",
                {s: "valid" for s in SIX[:-2]}
                | {"runtime": "rate-limit", "suite": "rate-limit"})

    salvage = {
        "status": "running",
        "round_dir": r3.name,
        "attempt": 2,
        "scenarios": ["runtime", "suite"],
        "pid": 12345,
    }
    monkeypatch.setattr(mon._E2E_RUNNER, "run_results_dir", lambda rid: results)
    monkeypatch.setattr(mon, "_pid_alive", lambda pid: True)

    data = {
        "run_id": "20260612_194959",
        "target_rounds": 5,
        "tools": ["claude-code"],
        "tool_states": {"claude-code": {"status": "done", "completed": [
            {"round": 1, "result_dir_name": "x", "exit_code": 0},
        ]}},
    }
    out = _render(mon._make_progress_table(
        data, None, salvage=salvage, salvage_active=True))
    # Per-scenario re-running detail for the R3 targets (not yet merged → ⟳).
    assert "re-running R3" in out
    assert "rt⟳" in out
    assert "ste⟳" in out
    # The bare "re-running…" fallback must NOT be the displayed text.
    assert "re-running…" not in out
