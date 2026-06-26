# SPDX-License-Identifier: Apache-2.0
"""Unit tests for salvage-status features.

Part A tests (cleanup_resume_scenarios.py):
  - _write_salvage_status: writes file, merges fields, refreshes updated_at, creates dir.
  - run_cleanup_resume: invokes status_cb with correct status transitions on happy-path
    and max-attempts path.

Part B tests (e2e_monitor.py):
  - _format_salvage: pure formatter — running+alive, running+stale, complete, max-attempts.
  - _load_salvage: returns None when file missing or malformed.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import List

import pytest

# ---------------------------------------------------------------------------
# Module import setup
# ---------------------------------------------------------------------------

_E2E_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_E2E_DIR))

import cleanup_resume_scenarios as crs  # noqa: E402
import e2e_monitor as mon  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers shared with test_cleanup_resume_scenarios.py
# ---------------------------------------------------------------------------

ALL_SCENARIOS = ["compiler", "dx_app", "dx_stream", "dx_stream_cascaded", "runtime", "suite"]
PREFIX = "claude_code"

DONE_MD = "Session complete.\n[DX-AGENT-DEV: DONE (output-dir: dx-compiler/dx-agent-dev/x)]\n"
RATE_LIMIT_MD = "You have hit your session limit.\nusage limit reached|9999999999 please retry later.\n"
REAL_WORK_JSONL = (
    '{"type":"assistant","content":"working..."}\n' * 30
    + '{"type":"tool_use","name":"bash"}\n' * 30
)


def _make_manifest(base_dir: Path, scenarios: List[str], prefix: str = PREFIX) -> None:
    artifacts = {}
    for s in scenarios:
        key = f"{prefix}__{s}"
        subdir = base_dir / key
        artifacts[key] = {"path": str(subdir), "relative_path": f"dx-agent-dev/e2e-tests/{key}", "contents": []}
    manifest = {
        "session_id": "test-session", "created_at": "2026-06-12 00:00:00",
        "exit_status": 0, "run_id": "test_run", "tool": "claude-code",
        "artifacts": artifacts,
    }
    (base_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _make_scenario_subdir(parent: Path, prefix: str, scenario: str, *, valid: bool = False, rate_limited: bool = False) -> Path:
    subdir = parent / f"{prefix}__{scenario}"
    subdir.mkdir(parents=True, exist_ok=True)
    if valid:
        (subdir / f"{scenario}-claude-code-session.md").write_text(DONE_MD, encoding="utf-8")
        (subdir / f"{scenario}-claude-code-stream.jsonl").write_text(REAL_WORK_JSONL, encoding="utf-8")
    elif rate_limited:
        (subdir / f"{scenario}-claude-code-session.md").write_text(RATE_LIMIT_MD, encoding="utf-8")
    return subdir


def _make_fake_round_dir(tmp_path: Path, scenarios: List[str]) -> Path:
    round_dir = tmp_path / "round"
    round_dir.mkdir(exist_ok=True)
    for s in scenarios:
        subdir = round_dir / f"{PREFIX}__{s}"
        subdir.mkdir(exist_ok=True)
    _make_manifest(round_dir, scenarios)
    return round_dir


# ---------------------------------------------------------------------------
# Part A: _write_salvage_status
# ---------------------------------------------------------------------------

class TestWriteSalvageStatus:
    def test_creates_salvage_json_with_fields(self, tmp_path, monkeypatch):
        """_write_salvage_status creates the file with the given fields."""
        monkeypatch.setattr(crs, "RUNNER_STATE_DIR", tmp_path / "runner_state")
        run_id = "20260612_test"
        crs._write_salvage_status(
            run_id,
            tool="claude-code",
            model="claude-opus-4-8",
            round_dir="20260612_215200_eb135a_claude-code-autopilot",
            scenarios=["runtime", "suite"],
            status="running",
            attempt=1,
            pid=12345,
            started_at="2026-06-12T21:52:00",
        )
        salvage_path = tmp_path / "runner_state" / run_id / "salvage.json"
        assert salvage_path.exists()
        data = json.loads(salvage_path.read_text())
        assert data["tool"] == "claude-code"
        assert data["status"] == "running"
        assert data["attempt"] == 1
        assert data["pid"] == 12345
        assert "updated_at" in data

    def test_creates_dir_if_absent(self, tmp_path, monkeypatch):
        """State dir is created automatically."""
        monkeypatch.setattr(crs, "RUNNER_STATE_DIR", tmp_path / "no_such_dir")
        crs._write_salvage_status("myrun", status="running", attempt=1)
        assert (tmp_path / "no_such_dir" / "myrun" / "salvage.json").exists()

    def test_merges_fields_preserves_existing(self, tmp_path, monkeypatch):
        """Second call merges new fields without erasing prior ones."""
        monkeypatch.setattr(crs, "RUNNER_STATE_DIR", tmp_path / "runner_state")
        run_id = "merge_test"
        crs._write_salvage_status(run_id, tool="claude-code", status="running", attempt=1)
        crs._write_salvage_status(run_id, status="complete", attempt=2)
        data = json.loads((tmp_path / "runner_state" / run_id / "salvage.json").read_text())
        # Both writes should be present
        assert data["tool"] == "claude-code"
        assert data["status"] == "complete"
        assert data["attempt"] == 2

    def test_refreshes_updated_at(self, tmp_path, monkeypatch):
        """updated_at changes between calls (monotonically non-decreasing)."""
        monkeypatch.setattr(crs, "RUNNER_STATE_DIR", tmp_path / "runner_state")
        run_id = "ts_test"
        crs._write_salvage_status(run_id, status="running", attempt=1)
        t1 = json.loads((tmp_path / "runner_state" / run_id / "salvage.json").read_text())["updated_at"]
        time.sleep(0.01)
        crs._write_salvage_status(run_id, status="running", attempt=2)
        t2 = json.loads((tmp_path / "runner_state" / run_id / "salvage.json").read_text())["updated_at"]
        # updated_at should be a string and second one >= first
        assert isinstance(t1, str)
        assert isinstance(t2, str)
        assert t2 >= t1

    def test_tolerates_corrupt_existing_file(self, tmp_path, monkeypatch):
        """If the existing salvage.json is corrupt JSON, write proceeds cleanly."""
        monkeypatch.setattr(crs, "RUNNER_STATE_DIR", tmp_path / "runner_state")
        run_id = "corrupt_test"
        state_dir = tmp_path / "runner_state" / run_id
        state_dir.mkdir(parents=True)
        (state_dir / "salvage.json").write_text("{BROKEN JSON", encoding="utf-8")
        # Should not raise
        crs._write_salvage_status(run_id, status="running", attempt=1)
        data = json.loads((state_dir / "salvage.json").read_text())
        assert data["status"] == "running"


# ---------------------------------------------------------------------------
# Part A: run_cleanup_resume invokes status_cb correctly
# ---------------------------------------------------------------------------

class TestRunCleanupResumeStatusCb:
    def test_happy_path_cb_running_then_complete(self, tmp_path):
        """Happy-path: cb called with running(attempt=1) then complete(attempt=1)."""
        round_dir = _make_fake_round_dir(tmp_path, ALL_SCENARIOS)
        cb_calls: list = []

        def runner_fn(scenarios):
            partial = tmp_path / "partial"
            partial.mkdir(exist_ok=True)
            for s in scenarios:
                _make_scenario_subdir(partial, PREFIX, s, valid=True)
            _make_manifest(partial, scenarios)
            return partial

        def status_cb(status: str, attempt: int, **_extra):
            cb_calls.append({"status": status, "attempt": attempt})

        result = crs.run_cleanup_resume(
            round_dir=round_dir,
            prefix=PREFIX,
            scenarios=["runtime", "suite"],
            runner_fn=runner_fn,
            sleep_fn=lambda s: None,
            now_fn=lambda: 1000.0,
            max_attempts=4,
            fallback_wait=10,
            status_cb=status_cb,
        )

        assert result["status"] == "complete"
        # First call: running attempt=1; last call: complete attempt=1
        assert cb_calls[0] == {"status": "running", "attempt": 1}
        assert cb_calls[-1] == {"status": "complete", "attempt": 1}

    def test_max_attempts_cb_ends_with_max_attempts_status(self, tmp_path):
        """Max-attempts path: cb ends with status='max-attempts'."""
        round_dir = _make_fake_round_dir(tmp_path, ALL_SCENARIOS)
        attempt_count = [0]
        cb_calls: list = []

        def runner_fn(scenarios):
            attempt_count[0] += 1
            partial = tmp_path / f"partial_{attempt_count[0]}"
            partial.mkdir(exist_ok=True)
            for s in scenarios:
                _make_scenario_subdir(partial, PREFIX, s, rate_limited=True)
            _make_manifest(partial, scenarios)
            return partial

        def status_cb(status: str, attempt: int, **_extra):
            cb_calls.append({"status": status, "attempt": attempt})

        result = crs.run_cleanup_resume(
            round_dir=round_dir,
            prefix=PREFIX,
            scenarios=["runtime"],
            runner_fn=runner_fn,
            sleep_fn=lambda s: None,
            now_fn=lambda: 1000.0,
            transcript_reader=lambda rd, sc: "",
            max_attempts=2,
            fallback_wait=1,
            status_cb=status_cb,
        )

        assert result["status"] == "max-attempts"
        # Last cb call should be max-attempts
        assert cb_calls[-1]["status"] == "max-attempts"

    def test_no_status_cb_runs_without_error(self, tmp_path):
        """When status_cb=None (default), run_cleanup_resume works normally."""
        round_dir = _make_fake_round_dir(tmp_path, ALL_SCENARIOS)

        def runner_fn(scenarios):
            partial = tmp_path / "partial_no_cb"
            partial.mkdir(exist_ok=True)
            for s in scenarios:
                _make_scenario_subdir(partial, PREFIX, s, valid=True)
            _make_manifest(partial, scenarios)
            return partial

        # No status_cb passed — must not raise
        result = crs.run_cleanup_resume(
            round_dir=round_dir,
            prefix=PREFIX,
            scenarios=["runtime"],
            runner_fn=runner_fn,
            sleep_fn=lambda s: None,
            now_fn=lambda: 1000.0,
        )
        assert result["status"] == "complete"

    def test_retry_cb_calls_include_incremented_attempt(self, tmp_path):
        """On retry, cb is called with attempt=2 before running again."""
        round_dir = _make_fake_round_dir(tmp_path, ALL_SCENARIOS)
        attempt_count = [0]
        cb_calls: list = []

        def runner_fn(scenarios):
            attempt_count[0] += 1
            partial = tmp_path / f"partial_{attempt_count[0]}"
            partial.mkdir(exist_ok=True)
            for s in scenarios:
                if attempt_count[0] == 1:
                    _make_scenario_subdir(partial, PREFIX, s, rate_limited=True)
                else:
                    _make_scenario_subdir(partial, PREFIX, s, valid=True)
            _make_manifest(partial, scenarios)
            return partial

        def status_cb(status: str, attempt: int, **_extra):
            cb_calls.append({"status": status, "attempt": attempt})

        result = crs.run_cleanup_resume(
            round_dir=round_dir,
            prefix=PREFIX,
            scenarios=["runtime"],
            runner_fn=runner_fn,
            sleep_fn=lambda s: None,
            now_fn=lambda: 1000.0,
            transcript_reader=lambda rd, sc: "",
            max_attempts=4,
            fallback_wait=1,
            status_cb=status_cb,
        )
        assert result["status"] == "complete"
        assert result["attempts"] == 2
        # Should have: running(1), running(2), complete(2)
        statuses = [(c["status"], c["attempt"]) for c in cb_calls]
        assert ("running", 1) in statuses
        assert ("running", 2) in statuses
        assert ("complete", 2) in statuses


# ---------------------------------------------------------------------------
# Part B: _format_salvage (pure, no live process needed)
# ---------------------------------------------------------------------------

class TestFormatSalvage:
    def _base_salvage(self, **overrides) -> dict:
        d = {
            "tool": "claude-code",
            "model": "claude-opus-4-8",
            "round_dir": "20260612_215200_eb135a_claude-code-autopilot",
            "scenarios": ["runtime", "suite"],
            "status": "running",
            "attempt": 2,
            "pid": 99999,
            "started_at": "2026-06-12T21:52:00",
            "updated_at": "2026-06-12T22:10:00",
        }
        d.update(overrides)
        return d

    def test_running_alive(self):
        s = self._base_salvage(status="running", attempt=2)
        line = mon._format_salvage(s, pid_alive=True)
        assert "running" in line
        assert "attempt 2" in line
        assert "[LIVE]" in line
        assert "runtime,suite" in line
        assert "[stale" not in line

    def test_running_stale_pid_dead(self):
        s = self._base_salvage(status="running", attempt=3)
        line = mon._format_salvage(s, pid_alive=False)
        assert "running" in line
        assert "stale" in line
        assert "[LIVE]" not in line

    def test_complete(self):
        s = self._base_salvage(status="complete", attempt=1)
        line = mon._format_salvage(s, pid_alive=False)
        assert "complete" in line
        assert "LIVE" not in line
        assert "stale" not in line

    def test_max_attempts(self):
        s = self._base_salvage(status="max-attempts", attempt=4)
        line = mon._format_salvage(s, pid_alive=False)
        assert "max-attempts" in line or "exhausted" in line

    def test_scenarios_in_output(self):
        s = self._base_salvage(scenarios=["compiler", "dx_app"])
        line = mon._format_salvage(s, pid_alive=True)
        assert "compiler" in line
        assert "dx_app" in line

    def test_round_dir_in_output(self):
        s = self._base_salvage(round_dir="20260612_999999_zzz_claude-code-autopilot")
        line = mon._format_salvage(s, pid_alive=False)
        assert "20260612_999999_zzz" in line


# ---------------------------------------------------------------------------
# Part B: _load_salvage
# ---------------------------------------------------------------------------

class TestLoadSalvage:
    def test_returns_none_when_file_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(mon, "RUNNER_STATE_DIR", tmp_path / "runner_state")
        result = mon._load_salvage("nonexistent_run_id")
        assert result is None

    def test_returns_dict_when_valid(self, tmp_path, monkeypatch):
        monkeypatch.setattr(mon, "RUNNER_STATE_DIR", tmp_path / "runner_state")
        state_dir = tmp_path / "runner_state" / "myrun"
        state_dir.mkdir(parents=True)
        data = {"status": "running", "attempt": 1, "tool": "claude-code"}
        (state_dir / "salvage.json").write_text(json.dumps(data), encoding="utf-8")
        result = mon._load_salvage("myrun")
        assert result is not None
        assert result["status"] == "running"

    def test_returns_none_on_corrupt_json(self, tmp_path, monkeypatch):
        monkeypatch.setattr(mon, "RUNNER_STATE_DIR", tmp_path / "runner_state")
        state_dir = tmp_path / "runner_state" / "badrun"
        state_dir.mkdir(parents=True)
        (state_dir / "salvage.json").write_text("{NOT VALID JSON", encoding="utf-8")
        result = mon._load_salvage("badrun")
        assert result is None
