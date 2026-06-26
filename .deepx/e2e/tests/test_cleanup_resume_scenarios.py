# SPDX-License-Identifier: Apache-2.0
"""Unit tests for cleanup_resume_scenarios.py.

All tests use injected fakes — NO real autopilot, NO real test.sh, NO real sleep.
Requires: stdlib + pytest only.

Test coverage:
  - delete_scenarios: subdirs removed, manifest artifacts pruned.
  - merge_scenarios: subdirs moved from source, manifest artifacts updated.
  - run_cleanup_resume loop:
      (a) happy path — first attempt succeeds.
      (b) one rate-limit then success — sleep called, second attempt succeeds.
      (c) max-attempts exhausted — returns {"status":"max-attempts"}.
  - main() --dry-run: prints test.sh command and DX_RUN_ID, exits 0.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import List, Optional
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------

_E2E_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_E2E_DIR))

import cleanup_resume_scenarios as crs  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers to build fake round dirs
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
    """Write a minimal manifest.json with entries for each scenario."""
    artifacts = {}
    for s in scenarios:
        key = f"{prefix}__{s}"
        subdir = base_dir / key
        artifacts[key] = {
            "path": str(subdir),
            "relative_path": f"dx-agent-dev/e2e-tests/{key}",
            "contents": [],
        }
    manifest = {
        "session_id": "test-session",
        "created_at": "2026-06-12 00:00:00",
        "exit_status": 0,
        "run_id": "test_run",
        "tool": "claude-code",
        "artifacts": artifacts,
    }
    (base_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _make_scenario_subdir(
    parent: Path,
    prefix: str,
    scenario: str,
    *,
    valid: bool = False,
    rate_limited: bool = False,
) -> Path:
    """Create a ``{prefix}__{scenario}`` subdir with appropriate content.

    Exactly one of valid/rate_limited should be True. Empty dir if neither.
    """
    subdir = parent / f"{prefix}__{scenario}"
    subdir.mkdir(parents=True, exist_ok=True)
    if valid:
        (subdir / f"{scenario}-claude-code-session.md").write_text(DONE_MD, encoding="utf-8")
        (subdir / f"{scenario}-claude-code-stream.jsonl").write_text(REAL_WORK_JSONL, encoding="utf-8")
    elif rate_limited:
        (subdir / f"{scenario}-claude-code-session.md").write_text(RATE_LIMIT_MD, encoding="utf-8")
    # else: empty dir → "skip" or "envfail" depending on classify logic
    return subdir


# ---------------------------------------------------------------------------
# Tests: delete_scenarios
# ---------------------------------------------------------------------------

class TestDeleteScenarios:
    def test_deletes_subdirs_and_manifest_entries(self, tmp_path):
        """Build a fake round_dir with 6 scenarios; delete runtime+suite."""
        round_dir = tmp_path / "round"
        round_dir.mkdir()

        # Create 6 scenario subdirs
        for s in ALL_SCENARIOS:
            _make_scenario_subdir(round_dir, PREFIX, s, valid=True)

        # Write manifest with all 6
        _make_manifest(round_dir, ALL_SCENARIOS)

        # Delete runtime + suite
        removed = crs.delete_scenarios(round_dir, PREFIX, ["runtime", "suite"])

        # Returned keys
        assert set(removed) == {"claude_code__runtime", "claude_code__suite"}

        # Subdirs gone
        assert not (round_dir / "claude_code__runtime").exists()
        assert not (round_dir / "claude_code__suite").exists()

        # The other 4 subdirs still exist
        for s in ["compiler", "dx_app", "dx_stream", "dx_stream_cascaded"]:
            assert (round_dir / f"claude_code__{s}").is_dir()

        # Manifest has exactly 4 entries left
        manifest = json.loads((round_dir / "manifest.json").read_text())
        assert set(manifest["artifacts"].keys()) == {
            "claude_code__compiler",
            "claude_code__dx_app",
            "claude_code__dx_stream",
            "claude_code__dx_stream_cascaded",
        }

    def test_tolerates_missing_scenarios(self, tmp_path):
        """Deleting a non-existent scenario is silent; returns only what was in manifest."""
        round_dir = tmp_path / "round"
        round_dir.mkdir()

        # Only compiler exists
        _make_scenario_subdir(round_dir, PREFIX, "compiler", valid=True)
        _make_manifest(round_dir, ["compiler"])

        removed = crs.delete_scenarios(round_dir, PREFIX, ["compiler", "runtime"])
        # Only compiler was in manifest
        assert removed == ["claude_code__compiler"]
        assert not (round_dir / "claude_code__compiler").exists()

    def test_handles_symlink_subdirs(self, tmp_path):
        """Symlinks (as created by conftest.pytest_sessionfinish) are removed without following."""
        round_dir = tmp_path / "round"
        round_dir.mkdir()
        real_target = tmp_path / "real_compiler_dir"
        real_target.mkdir()
        (real_target / "file.txt").write_text("data")

        # Create a symlink subdir like conftest does
        link = round_dir / "claude_code__compiler"
        link.symlink_to(real_target)

        _make_manifest(round_dir, ["compiler"])

        removed = crs.delete_scenarios(round_dir, PREFIX, ["compiler"])
        assert removed == ["claude_code__compiler"]

        # Symlink is gone but real target still exists
        assert not link.exists()
        assert not link.is_symlink()
        assert real_target.is_dir()
        assert (real_target / "file.txt").exists()

    def test_no_manifest_is_tolerated(self, tmp_path):
        """No manifest.json present — delete still removes subdirs, returns []."""
        round_dir = tmp_path / "round"
        round_dir.mkdir()
        _make_scenario_subdir(round_dir, PREFIX, "runtime", valid=True)

        # No manifest
        removed = crs.delete_scenarios(round_dir, PREFIX, ["runtime"])
        assert removed == []  # nothing in manifest to remove
        assert not (round_dir / "claude_code__runtime").exists()


# ---------------------------------------------------------------------------
# Tests: merge_scenarios
# ---------------------------------------------------------------------------

class TestMergeScenarios:
    def test_merges_subdirs_and_manifest(self, tmp_path):
        """round_dir has 4 scenarios; source_dir has runtime+suite; merge → 6."""
        round_dir = tmp_path / "round"
        round_dir.mkdir()
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # round_dir: 4 valid scenarios
        for s in ["compiler", "dx_app", "dx_stream", "dx_stream_cascaded"]:
            _make_scenario_subdir(round_dir, PREFIX, s, valid=True)
        _make_manifest(round_dir, ["compiler", "dx_app", "dx_stream", "dx_stream_cascaded"])

        # source_dir: 2 newly-run scenarios
        for s in ["runtime", "suite"]:
            _make_scenario_subdir(source_dir, PREFIX, s, valid=True)
        _make_manifest(source_dir, ["runtime", "suite"])

        # Merge
        merged = crs.merge_scenarios(round_dir, source_dir, PREFIX, ["runtime", "suite"])

        assert set(merged) == {"claude_code__runtime", "claude_code__suite"}

        # Both subdirs now exist in round_dir
        assert (round_dir / "claude_code__runtime").is_dir()
        assert (round_dir / "claude_code__suite").is_dir()

        # Subdir files were moved (not copied)
        assert (round_dir / "claude_code__runtime" / "runtime-claude-code-session.md").exists()

        # Source subdirs are gone (moved)
        assert not (source_dir / "claude_code__runtime").exists()
        assert not (source_dir / "claude_code__suite").exists()

        # round_dir manifest now has all 6 entries
        manifest = json.loads((round_dir / "manifest.json").read_text())
        assert set(manifest["artifacts"].keys()) == {
            f"claude_code__{s}" for s in ALL_SCENARIOS
        }

    def test_replaces_existing_scenario(self, tmp_path):
        """If round_dir already has a (failed) scenario subdir, merge replaces it."""
        round_dir = tmp_path / "round"
        round_dir.mkdir()
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # round_dir has a rate-limited runtime subdir
        _make_scenario_subdir(round_dir, PREFIX, "runtime", rate_limited=True)
        _make_manifest(round_dir, ["runtime"])

        # source_dir has a newly-run valid runtime
        _make_scenario_subdir(source_dir, PREFIX, "runtime", valid=True)
        _make_manifest(source_dir, ["runtime"])

        merged = crs.merge_scenarios(round_dir, source_dir, PREFIX, ["runtime"])
        assert merged == ["claude_code__runtime"]

        # runtime subdir now contains DONE content
        content = (round_dir / "claude_code__runtime" / "runtime-claude-code-session.md").read_text()
        assert "[DX-AGENT-DEV: DONE" in content

    def test_tolerates_missing_source_scenario(self, tmp_path):
        """Source dir missing a scenario → that scenario is silently skipped."""
        round_dir = tmp_path / "round"
        round_dir.mkdir()
        source_dir = tmp_path / "source"
        source_dir.mkdir()

        _make_manifest(round_dir, [])
        _make_manifest(source_dir, [])

        # Only "suite" exists in source, not "runtime"
        _make_scenario_subdir(source_dir, PREFIX, "suite", valid=True)
        _make_manifest(source_dir, ["suite"])

        merged = crs.merge_scenarios(round_dir, source_dir, PREFIX, ["runtime", "suite"])
        # Only suite was moved (runtime was missing)
        assert merged == ["claude_code__suite"]


# ---------------------------------------------------------------------------
# Fake e2e_runner._classify_round_scenario for classify_scenarios tests
# ---------------------------------------------------------------------------

class TestClassifyScenarios:
    def test_classifies_valid_scenario(self, tmp_path, monkeypatch):
        """A scenario with a DONE sentinel classifies as 'valid'."""
        round_dir = tmp_path / "round"
        round_dir.mkdir()
        _make_scenario_subdir(round_dir, PREFIX, "compiler", valid=True)

        # classify_scenarios imports e2e_runner; it is already importable
        verdicts = crs.classify_scenarios(round_dir, PREFIX, ["compiler"])
        assert verdicts["compiler"] == "valid"

    def test_missing_subdir_classifies_as_skip(self, tmp_path):
        """Non-existent subdir → 'skip'."""
        round_dir = tmp_path / "round"
        round_dir.mkdir()

        verdicts = crs.classify_scenarios(round_dir, PREFIX, ["runtime"])
        assert verdicts["runtime"] == "skip"


# ---------------------------------------------------------------------------
# Tests: find_newest_autopilot_dir
# ---------------------------------------------------------------------------

class TestFindNewestAutopilotDir:
    def test_finds_newest_not_excluded(self, tmp_path):
        run_results = tmp_path / "results" / "run1"
        run_results.mkdir(parents=True)

        dirs = [
            "20260612_200000_aaa_claude-code-autopilot",
            "20260612_210000_bbb_claude-code-autopilot",
            "20260612_220000_ccc_claude-code-autopilot",
        ]
        for d in dirs:
            (run_results / d).mkdir()

        # Exclude the newest
        newest = crs.find_newest_autopilot_dir(run_results, exclude={"20260612_220000_ccc_claude-code-autopilot"})
        assert newest is not None
        assert newest.name == "20260612_210000_bbb_claude-code-autopilot"

    def test_returns_none_if_all_excluded(self, tmp_path):
        run_results = tmp_path / "results" / "run1"
        run_results.mkdir(parents=True)
        (run_results / "20260612_200000_aaa_claude-code-autopilot").mkdir()

        result = crs.find_newest_autopilot_dir(
            run_results,
            exclude={"20260612_200000_aaa_claude-code-autopilot"},
        )
        assert result is None


# ---------------------------------------------------------------------------
# Tests: run_cleanup_resume loop
# ---------------------------------------------------------------------------

class FakeClassifier:
    """Controls which verdicts classify_scenarios returns per call."""

    def __init__(self, verdicts_sequence: list):
        """verdicts_sequence: list of dicts {scenario: verdict}, one per call."""
        self._seq = iter(verdicts_sequence)

    def __call__(self, round_dir, prefix, scenarios):
        try:
            return next(self._seq)
        except StopIteration:
            return {s: "valid" for s in scenarios}


def _make_fake_round_dir(tmp_path: Path, scenarios: List[str]) -> Path:
    """Build a minimal fake round_dir with manifest."""
    round_dir = tmp_path / "round"
    round_dir.mkdir(exist_ok=True)
    for s in scenarios:
        subdir = round_dir / f"{PREFIX}__{s}"
        subdir.mkdir(exist_ok=True)
    _make_manifest(round_dir, scenarios)
    return round_dir


def _make_fake_partial_dir(
    tmp_path: Path,
    name: str,
    scenarios: List[str],
    *,
    valid: bool = True,
    rate_limited: bool = False,
) -> Path:
    """Build a fake partial round dir (as test.sh would produce)."""
    partial = tmp_path / name
    partial.mkdir(exist_ok=True)
    for s in scenarios:
        _make_scenario_subdir(partial, PREFIX, s, valid=valid, rate_limited=rate_limited)
    _make_manifest(partial, scenarios)
    return partial


class TestRunCleanupResume:
    def test_happy_path_completes_in_one_attempt(self, tmp_path):
        """runner_fn returns a partial dir with valid scenarios → status='complete', no sleep.

        The runner_fn ONLY creates the partial dir and returns it.
        run_cleanup_resume handles delete + merge internally.
        """
        round_dir = _make_fake_round_dir(tmp_path, ALL_SCENARIOS)

        calls: List[List[str]] = []

        def runner_fn(scenarios: List[str]) -> Path:
            calls.append(list(scenarios))
            # Create a partial dir with all valid scenarios
            partial = tmp_path / "partial_happy"
            partial.mkdir(exist_ok=True)
            for s in scenarios:
                _make_scenario_subdir(partial, PREFIX, s, valid=True)
            _make_manifest(partial, scenarios)
            return partial

        sleep_calls: List[float] = []

        result = crs.run_cleanup_resume(
            round_dir=round_dir,
            prefix=PREFIX,
            scenarios=["runtime", "suite"],
            runner_fn=runner_fn,
            sleep_fn=sleep_calls.append,
            now_fn=lambda: 1000.0,
            max_attempts=4,
            fallback_wait=3600,
        )

        assert result["status"] == "complete"
        assert result["attempts"] == 1
        assert sleep_calls == []
        assert calls == [["runtime", "suite"]]

    def test_one_rate_limit_then_success(self, tmp_path):
        """First attempt: runtime still rate-limited → sleep → second attempt: all valid.

        runner_fn creates partial dirs with the appropriate content per attempt.
        run_cleanup_resume merges them and classifies the result.
        """
        round_dir = _make_fake_round_dir(tmp_path, ALL_SCENARIOS)

        attempt_count = [0]
        sleep_calls: List[float] = []

        def runner_fn(scenarios: List[str]) -> Path:
            attempt_count[0] += 1
            attempt = attempt_count[0]
            # Attempt 1: runtime rate-limited; attempt 2: all valid
            partial = tmp_path / f"partial_{attempt}"
            partial.mkdir(exist_ok=True)
            for s in scenarios:
                if attempt == 1 and s == "runtime":
                    _make_scenario_subdir(partial, PREFIX, s, rate_limited=True)
                else:
                    _make_scenario_subdir(partial, PREFIX, s, valid=True)
            _make_manifest(partial, scenarios)
            return partial

        result = crs.run_cleanup_resume(
            round_dir=round_dir,
            prefix=PREFIX,
            scenarios=["runtime", "suite"],
            runner_fn=runner_fn,
            sleep_fn=sleep_calls.append,
            now_fn=lambda: 1000.0,
            transcript_reader=lambda rd, sc: "",  # no text → fallback_wait
            max_attempts=4,
            fallback_wait=10,
        )

        assert result["status"] == "complete"
        assert result["attempts"] == 2
        # Sleep was called once (between attempt 1 and 2)
        assert len(sleep_calls) == 1
        assert sleep_calls[0] == 10.0  # fallback_wait

    def test_max_attempts_exhausted(self, tmp_path):
        """Always rate-limited → status='max-attempts'."""
        round_dir = _make_fake_round_dir(tmp_path, ALL_SCENARIOS)

        attempt_count = [0]

        def runner_fn(scenarios: List[str]) -> Path:
            attempt_count[0] += 1
            partial = tmp_path / f"partial_{attempt_count[0]}"
            partial.mkdir(exist_ok=True)
            for s in scenarios:
                _make_scenario_subdir(partial, PREFIX, s, rate_limited=True)
            _make_manifest(partial, scenarios)
            return partial

        sleep_calls: List[float] = []

        result = crs.run_cleanup_resume(
            round_dir=round_dir,
            prefix=PREFIX,
            scenarios=["runtime", "suite"],
            runner_fn=runner_fn,
            sleep_fn=sleep_calls.append,
            now_fn=lambda: 1000.0,
            transcript_reader=lambda rd, sc: "",
            max_attempts=3,
            fallback_wait=5,
        )

        assert result["status"] == "max-attempts"
        assert "still_failed" in result
        assert result["attempts"] == 3
        # Sleep was called max_attempts - 1 times (not after the last attempt)
        assert len(sleep_calls) == 2

    def test_sleep_uses_parsed_reset_time(self, tmp_path):
        """When transcript contains a rate-limit epoch, sleep uses parse_reset_seconds."""
        from e2e_resilient_run import parse_reset_seconds  # verify importable

        round_dir = _make_fake_round_dir(tmp_path, ALL_SCENARIOS)
        attempt_count = [0]

        # Epoch 4600 with now=1000 → wait=3600s
        RATE_LIMIT_EPOCH_TEXT = "usage limit reached|4600 please wait"

        def runner_fn(scenarios: List[str]) -> Path:
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

        sleep_calls: List[float] = []

        result = crs.run_cleanup_resume(
            round_dir=round_dir,
            prefix=PREFIX,
            scenarios=["runtime"],
            runner_fn=runner_fn,
            sleep_fn=sleep_calls.append,
            now_fn=lambda: 1000.0,
            transcript_reader=lambda rd, sc: RATE_LIMIT_EPOCH_TEXT,
            max_attempts=4,
            fallback_wait=9999,  # should NOT be used (parsed time = 3600)
        )

        assert result["status"] == "complete"
        assert result["attempts"] == 2
        assert len(sleep_calls) == 1
        assert sleep_calls[0] == 3600  # parsed from epoch


# ---------------------------------------------------------------------------
# Tests: main() --dry-run
# ---------------------------------------------------------------------------

class TestMainDryRun:
    def test_dry_run_prints_command_and_exits_zero(self, tmp_path, capsys):
        """--dry-run prints DX_RUN_ID and -k 'runtime or suite', exits 0."""
        # Build a fake round dir structure
        run_id = "20260612_194959"
        round_name = "20260612_215200_eb135a_claude-code-autopilot"
        results_root = tmp_path / "dx-agent-dev" / "e2e-tests" / "results"
        round_dir = results_root / run_id / round_name
        round_dir.mkdir(parents=True)
        for s in ALL_SCENARIOS:
            _make_scenario_subdir(round_dir, PREFIX, s, valid=True)
        _make_manifest(round_dir, ALL_SCENARIOS)

        # Monkey-patch RESULTS_ROOT in the module
        orig_results_root = crs.RESULTS_ROOT
        crs.RESULTS_ROOT = results_root
        try:
            rc = crs.main([
                "--run-id", run_id,
                "--round-dir", round_name,
                "--scenarios", "runtime,suite",
                "--tool", "claude-code",
                "--dry-run",
            ])
        finally:
            crs.RESULTS_ROOT = orig_results_root

        assert rc == 0
        captured = capsys.readouterr()
        out = captured.out

        # Must contain DX_RUN_ID and the -k expression
        assert "DX_RUN_ID=20260612_194959" in out
        assert '-k "runtime or suite"' in out
        assert "test.sh" in out
        assert "agent-driven-e2e-claude-code-autopilot" in out
        assert "DRY RUN" in out

    def test_dry_run_with_model_and_thinking(self, tmp_path, capsys):
        """--dry-run with --model and --thinking shows the model env var."""
        run_id = "test_run"
        round_name = "20260612_000000_aaa_claude-code-autopilot"
        results_root = tmp_path / "dx-agent-dev" / "e2e-tests" / "results"
        round_dir = results_root / run_id / round_name
        round_dir.mkdir(parents=True)
        _make_manifest(round_dir, ["runtime"])
        _make_scenario_subdir(round_dir, PREFIX, "runtime", valid=True)

        orig = crs.RESULTS_ROOT
        crs.RESULTS_ROOT = results_root
        try:
            rc = crs.main([
                "--run-id", run_id,
                "--round-dir", round_name,
                "--scenarios", "runtime",
                "--tool", "claude-code",
                "--model", "claude-opus-4-6",
                "--thinking",
                "--dry-run",
            ])
        finally:
            crs.RESULTS_ROOT = orig

        assert rc == 0
        captured = capsys.readouterr()
        out = captured.out
        assert "DX_AGENT_E2E_CLAUDE_CODE_MODEL=claude-opus-4-6" in out
        assert "effort" in out  # thinking env shows --effort xhigh


# ---------------------------------------------------------------------------
# Tests: scenario_subdir helper
# ---------------------------------------------------------------------------

class TestScenarioSubdir:
    def test_returns_correct_path(self, tmp_path):
        p = crs.scenario_subdir(tmp_path, "claude_code", "runtime")
        assert p == tmp_path / "claude_code__runtime"

    def test_different_prefix(self, tmp_path):
        p = crs.scenario_subdir(tmp_path, "copilot_cli", "suite")
        assert p == tmp_path / "copilot_cli__suite"


# --- _supersede_partial_dir (retire scratch dir post-merge) ------------------
import cleanup_resume_scenarios as _crs

def test_supersede_renames_nonempty_scratch_dir(tmp_path):
    d = tmp_path / "20260615_141417_da18c2_claude-code-autopilot"
    d.mkdir()
    (d / "manifest.json").write_text("{}")
    (d / "SUMMARY.md").write_text("x")
    _crs._supersede_partial_dir(d)
    assert not d.exists()
    renamed = tmp_path / "superseded__20260615_141417_da18c2_claude-code-autopilot"
    assert renamed.is_dir() and (renamed / "manifest.json").exists()

def test_supersede_removes_empty_scratch_dir(tmp_path):
    d = tmp_path / "20260615_999999_aaaaaa_claude-code-autopilot"
    d.mkdir()
    _crs._supersede_partial_dir(d)
    assert not d.exists()
    assert not (tmp_path / ("superseded__" + d.name)).exists()

def test_supersede_idempotent_on_already_superseded(tmp_path):
    d = tmp_path / "superseded__20260615_141417_da18c2_claude-code-autopilot"
    d.mkdir(); (d / "manifest.json").write_text("{}")
    _crs._supersede_partial_dir(d)
    assert d.is_dir()  # left as-is, no double prefix

def test_find_newest_excludes_superseded(tmp_path):
    (tmp_path / "20260615_100000_aaaaaa_claude-code-autopilot").mkdir()
    (tmp_path / "superseded__20260615_120000_bbbbbb_claude-code-autopilot").mkdir()
    newest = _crs.find_newest_autopilot_dir(tmp_path, set())
    assert newest is not None and not newest.name.startswith("superseded__")
