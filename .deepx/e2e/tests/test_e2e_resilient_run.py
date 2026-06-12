"""
Unit tests for e2e_resilient_run.py.

All tests use injected fakes — NO real subprocess, NO real sleep, NO real time.time().
Requires: stdlib + pytest only.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple
import importlib
import types

import pytest

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------

# We need to import from the parent directory (.deepx/e2e/)
_E2E_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_E2E_DIR))

from e2e_resilient_run import (
    build_runner_cmd,
    completed_rounds,
    parse_reset_seconds,
    run_resilient,
    RUNNER_STATE_DIR,
)


# ===========================================================================
# parse_reset_seconds
# ===========================================================================


class TestParseResetSeconds:
    """Tests for parse_reset_seconds(text, now_epoch)."""

    def test_epoch_pipe_form(self):
        """'usage limit reached|4600' with now=1000 → 3600s wait."""
        text = "You have usage limit reached|4600 please wait."
        assert parse_reset_seconds(text, now_epoch=1000.0) == 3600

    def test_epoch_pipe_past_clamps_to_zero(self):
        """If epoch is already past, wait = 0 (not negative)."""
        text = "usage limit reached|1000"
        assert parse_reset_seconds(text, now_epoch=5000.0) == 0

    def test_resets_at_json_form(self):
        """'"resetsAt":4600' with now=1000 → 3600s."""
        text = 'The API responded with {"resetsAt":4600, "status":"limited"}'
        assert parse_reset_seconds(text, now_epoch=1000.0) == 3600

    def test_resets_at_bare_epoch(self):
        """'resets at 4600' (10-digit epoch form) with now=1000 → 3600s."""
        text = "Your session resets at 1751234600 and will be available then."
        now = 1751234600 - 3600
        assert parse_reset_seconds(text, now_epoch=float(now)) == 3600

    def test_session_limit_epoch(self):
        """'session limit · resets <epoch>' form."""
        text = "session limit · resets 4600"
        assert parse_reset_seconds(text, now_epoch=1000.0) == 3600

    def test_clock_form_pm(self):
        """'resets at 3pm' — compute seconds until 3 PM today (or tomorrow)."""
        # Fix now to 2pm (14:00:00) on some day
        # struct_time: year=2026, month=1, day=1, hour=14, min=0, sec=0
        # 3pm = 15:00 → diff = 3600s
        now_epoch = _epoch_for_localtime(2026, 1, 1, 14, 0, 0)
        text = "Your session limit · resets at 3pm"
        result = parse_reset_seconds(text, now_epoch=now_epoch)
        assert result == 3600

    def test_clock_form_with_minutes(self):
        """'resets at 3:30pm' — compute seconds until 15:30."""
        now_epoch = _epoch_for_localtime(2026, 1, 1, 14, 0, 0)
        text = "resets at 3:30pm"
        result = parse_reset_seconds(text, now_epoch=now_epoch)
        assert result == 5400  # 1.5 hours = 5400s

    def test_clock_form_roll_to_tomorrow(self):
        """'resets at 3pm' when it's already 4pm → should roll to tomorrow = 23h."""
        now_epoch = _epoch_for_localtime(2026, 1, 1, 16, 0, 0)  # 4pm
        text = "resets at 3pm"
        result = parse_reset_seconds(text, now_epoch=now_epoch)
        # 3pm tomorrow = 23 hours from 4pm today
        assert result == 23 * 3600

    def test_clock_form_24h(self):
        """'resets 15:00' (24h clock, no am/pm)."""
        now_epoch = _epoch_for_localtime(2026, 1, 1, 14, 0, 0)
        text = "resets 15:00"
        result = parse_reset_seconds(text, now_epoch=now_epoch)
        assert result == 3600

    def test_no_match_returns_none(self):
        """Plain text with no reset patterns returns None."""
        text = "Everything is fine. No limits applied here."
        assert parse_reset_seconds(text, now_epoch=1000.0) is None

    def test_picks_soonest_of_multiple(self):
        """When multiple matches exist, returns the smallest non-negative value."""
        # Two epoch forms: wait=3600 and wait=7200
        text = "usage limit reached|4600 and also resetsAt:8200"
        # now=1000, epoch 4600→3600s, epoch 8200→7200s → pick 3600
        result = parse_reset_seconds(text, now_epoch=1000.0)
        assert result == 3600

    def test_empty_text_returns_none(self):
        """Empty string returns None."""
        assert parse_reset_seconds("", now_epoch=1000.0) is None

    def test_case_insensitive_epoch(self):
        """'USAGE LIMIT REACHED|4600' should match (case-insensitive)."""
        text = "USAGE LIMIT REACHED|4600"
        assert parse_reset_seconds(text, now_epoch=1000.0) == 3600


# ===========================================================================
# build_runner_cmd
# ===========================================================================


class TestBuildRunnerCmd:
    """Tests for build_runner_cmd(...)."""

    RUNNER = "/path/to/e2e_runner.py"

    def test_claude_code_maps_to_claude_model_flag(self):
        cmd = build_runner_cmd(
            runner=self.RUNNER,
            tool="claude-code",
            model="claude-opus-4-8",
            rounds=5,
            thinking=False,
            resume=False,
            run_id=None,
        )
        assert "--claude-model" in cmd
        idx = cmd.index("--claude-model")
        assert cmd[idx + 1] == "claude-opus-4-8"

    def test_copilot_cli_maps_to_copilot_model_flag(self):
        cmd = build_runner_cmd(
            runner=self.RUNNER,
            tool="copilot-cli",
            model="gpt-4o",
            rounds=3,
            thinking=False,
            resume=False,
            run_id=None,
        )
        assert "--copilot-model" in cmd

    def test_codex_cli_maps_to_codex_model_flag(self):
        cmd = build_runner_cmd(
            runner=self.RUNNER,
            tool="codex-cli",
            model="o3",
            rounds=3,
            thinking=False,
            resume=False,
            run_id=None,
        )
        assert "--codex-model" in cmd

    def test_opencode_cli_maps_to_opencode_model_flag(self):
        cmd = build_runner_cmd(
            runner=self.RUNNER,
            tool="opencode-cli",
            model="claude-opus-4-8",
            rounds=3,
            thinking=False,
            resume=False,
            run_id=None,
        )
        assert "--opencode-model" in cmd

    def test_cursor_cli_maps_to_cursor_model_flag(self):
        cmd = build_runner_cmd(
            runner=self.RUNNER,
            tool="cursor-cli",
            model="claude-opus-4-8",
            rounds=3,
            thinking=False,
            resume=False,
            run_id=None,
        )
        assert "--cursor-model" in cmd

    def test_resume_adds_resume_and_run_id(self):
        cmd = build_runner_cmd(
            runner=self.RUNNER,
            tool="claude-code",
            model="claude-opus-4-8",
            rounds=5,
            thinking=False,
            resume=True,
            run_id="20260612_120000",
        )
        assert "--resume" in cmd
        assert "--run-id" in cmd
        idx = cmd.index("--run-id")
        assert cmd[idx + 1] == "20260612_120000"

    def test_thinking_adds_thinking_flag(self):
        cmd = build_runner_cmd(
            runner=self.RUNNER,
            tool="claude-code",
            model="claude-opus-4-8",
            rounds=5,
            thinking=True,
            resume=False,
            run_id=None,
        )
        assert "--thinking" in cmd

    def test_no_thinking_no_flag(self):
        cmd = build_runner_cmd(
            runner=self.RUNNER,
            tool="claude-code",
            model="claude-opus-4-8",
            rounds=5,
            thinking=False,
            resume=False,
            run_id=None,
        )
        assert "--thinking" not in cmd

    def test_no_resume_no_resume_flag(self):
        cmd = build_runner_cmd(
            runner=self.RUNNER,
            tool="claude-code",
            model="claude-opus-4-8",
            rounds=5,
            thinking=False,
            resume=False,
            run_id=None,
        )
        assert "--resume" not in cmd
        assert "--run-id" not in cmd

    def test_rounds_included(self):
        cmd = build_runner_cmd(
            runner=self.RUNNER,
            tool="claude-code",
            model="m",
            rounds=7,
            thinking=False,
            resume=False,
            run_id=None,
        )
        assert "--rounds" in cmd
        idx = cmd.index("--rounds")
        assert cmd[idx + 1] == "7"


# ===========================================================================
# completed_rounds
# ===========================================================================


class TestCompletedRounds:
    """Tests for completed_rounds(state_path, tool)."""

    def _write_state(self, tmp_path: Path, tool: str, completed_count: int) -> Path:
        """Write a minimal state.json with N completed rounds for *tool*."""
        state_path = tmp_path / "state.json"
        state = {
            "run_id": "test_run",
            "target_rounds": 5,
            "tool_states": {
                tool: {
                    "completed": [
                        {
                            "round": i + 1,
                            "result_dir_name": f"dir_{i}",
                            "exit_code": 0,
                            "start_utc": "2026-01-01T00:00:00Z",
                            "end_utc": "2026-01-01T01:00:00Z",
                            "artifact_dirs": [],
                        }
                        for i in range(completed_count)
                    ],
                    "in_progress": None,
                    "status": "running",
                    "pid": None,
                }
            },
        }
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state_path

    def test_returns_correct_count(self, tmp_path):
        state_path = self._write_state(tmp_path, "claude-code", 3)
        assert completed_rounds(state_path, "claude-code") == 3

    def test_zero_completed(self, tmp_path):
        state_path = self._write_state(tmp_path, "claude-code", 0)
        assert completed_rounds(state_path, "claude-code") == 0

    def test_missing_tool_returns_zero(self, tmp_path):
        state_path = self._write_state(tmp_path, "claude-code", 3)
        # Ask for a tool not present in the state
        assert completed_rounds(state_path, "copilot-cli") == 0

    def test_missing_file_returns_zero(self, tmp_path):
        missing_path = tmp_path / "nonexistent" / "state.json"
        assert completed_rounds(missing_path, "claude-code") == 0

    def test_corrupt_json_returns_zero(self, tmp_path):
        state_path = tmp_path / "state.json"
        state_path.write_text("NOT VALID JSON {{{", encoding="utf-8")
        assert completed_rounds(state_path, "claude-code") == 0

    def test_empty_file_returns_zero(self, tmp_path):
        state_path = tmp_path / "state.json"
        state_path.write_text("", encoding="utf-8")
        assert completed_rounds(state_path, "claude-code") == 0

    def test_five_completed(self, tmp_path):
        state_path = self._write_state(tmp_path, "claude-code", 5)
        assert completed_rounds(state_path, "claude-code") == 5


# ===========================================================================
# run_resilient — fake infrastructure
# ===========================================================================


class FakeRunner:
    """Scriptable fake runner_fn.

    Provide a list of "scripts" — each script is called in order and returns
    (returncode, stdout, run_id).  The run_id is auto-assigned from the first
    fresh run and reused for redo calls.

    Each script is a callable (cmd: list) -> (rc, stdout, run_id), or a tuple
    (rc, stdout, run_id) for convenience.
    """

    def __init__(self, scripts: list):
        self.calls: List[List[str]] = []
        self._scripts = list(scripts)
        self._idx = 0

    def __call__(self, cmd: List[str]) -> Tuple[int, str, str]:
        self.calls.append(list(cmd))
        if self._idx >= len(self._scripts):
            raise AssertionError(f"FakeRunner called more times than scripted ({self._idx})")
        script = self._scripts[self._idx]
        self._idx += 1
        if callable(script):
            return script(cmd)
        return tuple(script)  # type: ignore[return-value]


class FakeSleep:
    """Records sleep durations without actually sleeping."""

    def __init__(self):
        self.calls: List[float] = []

    def __call__(self, secs: float) -> None:
        self.calls.append(secs)


class TestRunResilient:
    """Tests for run_resilient(...)."""

    RUNNER = "/fake/e2e_runner.py"
    TOOL = "claude-code"
    MODEL = "claude-opus-4-8"
    ROUNDS = 3
    NOW = 1000.0
    RUN_ID = "20260612_120000"

    def _make_state(self, tmp_path: Path, completed: int) -> None:
        """Write a state.json for the fake run_id with N completed rounds."""
        state_dir = tmp_path / self.RUN_ID
        state_dir.mkdir(parents=True, exist_ok=True)
        state = {
            "run_id": self.RUN_ID,
            "target_rounds": self.ROUNDS,
            "tool_states": {
                self.TOOL: {
                    "completed": [
                        {"round": i + 1, "result_dir_name": f"d{i}", "exit_code": 0,
                         "start_utc": "Z", "end_utc": "Z", "artifact_dirs": []}
                        for i in range(completed)
                    ],
                    "in_progress": None,
                    "status": "running" if completed < self.ROUNDS else "done",
                    "pid": None,
                }
            },
        }
        (state_dir / "state.json").write_text(json.dumps(state), encoding="utf-8")

    def _call(self, runner_fn, sleep_fn, tmp_path, *, transcript="", **kwargs):
        """Helper to call run_resilient with injected fakes + tmp RUNNER_STATE_DIR."""
        import e2e_resilient_run as m
        orig = m.RUNNER_STATE_DIR
        m.RUNNER_STATE_DIR = tmp_path
        try:
            return run_resilient(
                runner=self.RUNNER,
                tool=self.TOOL,
                model=self.MODEL,
                rounds=self.ROUNDS,
                thinking=False,
                runner_fn=runner_fn,
                sleep_fn=sleep_fn,
                now_fn=lambda: self.NOW,
                transcript_reader=lambda rid: transcript,
                **kwargs,
            )
        finally:
            m.RUNNER_STATE_DIR = orig

    # --- (a) Happy path: first run completes target ---

    def test_happy_path_complete_on_first_attempt(self, tmp_path):
        """First run completes all rounds — no sleep, status=complete."""
        # After fresh run: state has ROUNDS completed
        def fake_run(cmd):
            self._make_state(tmp_path, completed=self.ROUNDS)
            return (0, f"E2E Runner  run_id={self.RUN_ID}\nE2E Runner COMPLETE  run_id={self.RUN_ID}", self.RUN_ID)

        fake_runner = FakeRunner([fake_run])
        fake_sleep = FakeSleep()

        result = self._call(fake_runner, fake_sleep, tmp_path)

        assert result["status"] == "complete"
        assert result["run_id"] == self.RUN_ID
        assert result["attempts"] == 1
        assert fake_sleep.calls == [], "No sleep expected on first-run completion"
        # Only one call: the fresh run (no redo needed)
        assert len(fake_runner.calls) == 1

    # --- (b) One rate-limit then success ---

    def test_one_rate_limit_then_success(self, tmp_path):
        """Attempt 0: incomplete → redo removes 1 → sleep ~1800s → attempt 1 resumes → complete."""
        call_count = [0]

        def fake_run(cmd):
            call_count[0] += 1
            n = call_count[0]
            if n == 1:
                # Fresh run: completes 1 of ROUNDS
                self._make_state(tmp_path, completed=1)
                return (0, f"E2E Runner  run_id={self.RUN_ID}", self.RUN_ID)
            elif n == 2:
                # redo-env-failures: removes 1
                return (0, f"[redo-env] removed 1 round(s); state reset to 'running'", "")
            elif n == 3:
                # Resume: completes all rounds
                self._make_state(tmp_path, completed=self.ROUNDS)
                return (0, f"E2E Runner  run_id={self.RUN_ID}", self.RUN_ID)
            else:
                raise AssertionError(f"Unexpected call #{n}")

        fake_runner = FakeRunner([fake_run, fake_run, fake_run])
        fake_sleep = FakeSleep()

        # Transcript has a parseable reset time: now=1000, epoch 2800 → 1800s
        transcript = "usage limit reached|2800"

        result = self._call(
            fake_runner, fake_sleep, tmp_path,
            transcript=transcript,
        )

        assert result["status"] == "complete"
        assert result["attempts"] == 2
        # Sleep was called once with ~1800s
        assert len(fake_sleep.calls) == 1
        assert fake_sleep.calls[0] == 1800

        # 2nd attempt should use --resume and --run-id
        resume_cmd = fake_runner.calls[2]  # call index 2 = 3rd call = resume run
        assert "--resume" in resume_cmd
        assert "--run-id" in resume_cmd
        idx = resume_cmd.index("--run-id")
        assert resume_cmd[idx + 1] == self.RUN_ID

    # --- (c) Non-env incomplete: redo reports 0 removed → stop ---

    def test_non_env_incomplete_stops_immediately(self, tmp_path):
        """redo-env-failures removes 0 rounds → status=incomplete-nonenv, no loop."""
        call_count = [0]

        def fake_run(cmd):
            call_count[0] += 1
            n = call_count[0]
            if n == 1:
                # Fresh run: only 1 of ROUNDS
                self._make_state(tmp_path, completed=1)
                return (1, f"E2E Runner  run_id={self.RUN_ID}", self.RUN_ID)
            elif n == 2:
                # redo: no env-failure rounds
                return (0, "no env-failure rounds detected — all clean.", "")
            else:
                raise AssertionError(f"Unexpected call #{n}: should have stopped after 2")

        fake_runner = FakeRunner([fake_run, fake_run])
        fake_sleep = FakeSleep()

        result = self._call(fake_runner, fake_sleep, tmp_path)

        assert result["status"] == "incomplete-nonenv"
        assert result["attempts"] == 1
        # No sleep
        assert fake_sleep.calls == []
        # Only 2 calls: fresh run + redo check
        assert len(fake_runner.calls) == 2

    # --- (d) max-attempts: always rate-limited → stops at max_attempts ---

    def test_max_attempts_exhausted(self, tmp_path):
        """Always incomplete + redo removes rounds → exhausts max_attempts."""
        call_count = [0]

        def fake_run(cmd):
            call_count[0] += 1
            n = call_count[0]
            # Alternate: odd = run (partial), even = redo (removes 1)
            if n % 2 == 1:
                # Run call: always incomplete
                self._make_state(tmp_path, completed=1)
                return (0, f"E2E Runner  run_id={self.RUN_ID}", self.RUN_ID)
            else:
                # Redo call: always removes 1
                return (0, "[redo-env] removed 1 round(s)", "")

        max_attempts = 3
        # For 3 attempts: 3 runs + 2 redos (no redo after last run, but loop exits)
        # Actually: attempt 1 run, attempt 1 redo+sleep, attempt 2 run,
        # attempt 2 redo+sleep, attempt 3 run → max_attempts reached.
        # Total runner calls = 3 runs + 2 redos = 5
        scripts = [fake_run] * 10  # more than enough
        fake_runner = FakeRunner(scripts)
        fake_sleep = FakeSleep()

        result = self._call(
            fake_runner, fake_sleep, tmp_path,
            max_attempts=max_attempts,
            fallback_wait=60,
        )

        assert result["status"] == "max-attempts"
        assert result["attempts"] == max_attempts
        # Sleep was called max_attempts-1 times (between attempts)
        assert len(fake_sleep.calls) == max_attempts - 1

    # --- fallback_wait used when no transcript reset time ---

    def test_fallback_wait_used_when_no_reset_in_transcript(self, tmp_path):
        """When transcript has no parseable reset time, fallback_wait is used."""
        call_count = [0]

        def fake_run(cmd):
            call_count[0] += 1
            n = call_count[0]
            if n == 1:
                self._make_state(tmp_path, completed=1)
                return (0, f"E2E Runner  run_id={self.RUN_ID}", self.RUN_ID)
            elif n == 2:
                return (0, "[redo-env] removed 1 round(s)", "")
            elif n == 3:
                self._make_state(tmp_path, completed=self.ROUNDS)
                return (0, f"E2E Runner  run_id={self.RUN_ID}", self.RUN_ID)
            else:
                raise AssertionError(f"Unexpected call #{n}")

        fake_runner = FakeRunner([fake_run, fake_run, fake_run])
        fake_sleep = FakeSleep()

        result = self._call(
            fake_runner, fake_sleep, tmp_path,
            transcript="No reset info here",
            fallback_wait=7777,
        )

        assert result["status"] == "complete"
        assert fake_sleep.calls == [7777]


# ===========================================================================
# Helper
# ===========================================================================


def _epoch_for_localtime(year, month, day, hour, minute, second) -> float:
    """Return epoch for a specific local time (using time.mktime)."""
    import time as t
    tm = t.struct_time((year, month, day, hour, minute, second, 0, 0, -1))
    return t.mktime(tm)
