# SPDX-License-Identifier: Apache-2.0
"""Tests for move_round.py — cross-run-id round transplant tool.

All tests use tmp_path fixtures; no real run data is touched.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# --- Import move_round from sibling directory --------------------------------
_E2E_DIR = Path(__file__).resolve().parents[1]  # .deepx/e2e/
sys.path.insert(0, str(_E2E_DIR))

import move_round as mr  # noqa: E402

# ---------------------------------------------------------------------------
# Sentinel constants (mirrors test_e2e_runner_env_redo.py)
# ---------------------------------------------------------------------------
DONE_MD = (
    "Run complete.\n"
    "[DX-AGENT-DEV: DONE (output-dir: dx-compiler/dx-agent-dev/x)]\n"
)
START_ONLY_MD = "[DX-AGENT-DEV: START]\nworking...\n"
REAL_WORK_JSONL = (
    '{"type":"assistant","content":"..."}\n' * 30
    + '{"type":"tool_use","name":"bash"}\n' * 30
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_scenario(
    parent: Path,
    name: str,
    *,
    session_md: str = DONE_MD,
    stream_jsonl: str = REAL_WORK_JSONL,
) -> Path:
    """Create a <prefix>__<scenario> subdir with transcript files."""
    sd = parent / name
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "x-session.md").write_text(session_md, encoding="utf-8")
    (sd / "x-stream.jsonl").write_text(stream_jsonl, encoding="utf-8")
    return sd


def _make_round_dir(
    base: Path,
    name: str,
    prefix: str = "claude_code",
    scenarios: list[str] | None = None,
    *,
    incomplete_suite: bool = False,
) -> Path:
    """Build a round dir with scenario subdirs + manifest.json + SUMMARY.md."""
    rd = base / name
    rd.mkdir(parents=True, exist_ok=True)

    if scenarios is None:
        scenarios = ["compiler", "dx_app", "dx_stream", "dx_stream_cascaded", "runtime", "suite"]

    for i, scen in enumerate(scenarios):
        if incomplete_suite and scen == "suite":
            _make_scenario(rd, f"{prefix}__{scen}", session_md=START_ONLY_MD)
        else:
            _make_scenario(rd, f"{prefix}__{scen}")

    manifest = {
        "session_id": name,
        "created_at": "2026-06-15 08:28:57",
        "exit_status": 0,
        "run_id": "source_run",
        "tool": "claude-code",
        "mode": "NT",
        "artifacts": {
            f"{prefix}__{scen}": {"path": f"/fake/{scen}", "relative_path": f"fake/{scen}"}
            for scen in scenarios
        },
    }
    (rd / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (rd / "SUMMARY.md").write_text("# Summary\nFake.\n", encoding="utf-8")
    return rd


def _make_state(
    state_root: Path,
    run_id: str,
    completed: list[dict],
    tool: str = "claude-code",
) -> Path:
    """Create a runner_state/<run_id>/state.json with the given completed list."""
    state_dir = state_root / run_id
    state_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "run_id": run_id,
        "target_rounds": 5,
        "tool_states": {
            tool: {
                "completed": completed,
                "in_progress": None,
                "status": "done",
                "pid": None,
            }
        },
    }
    state_path = state_dir / "state.json"
    state_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return state_path


# ===========================================================================
# Tests: round_is_fully_valid
# ===========================================================================

class TestRoundIsFullyValid:
    def test_all_six_valid(self, tmp_path):
        """Six scenario subdirs all with DONE sentinel → (True, all 'valid')."""
        rd = _make_round_dir(tmp_path, "round_dir")
        all_valid, verdicts = mr.round_is_fully_valid(rd, "claude_code")
        assert all_valid is True
        assert len(verdicts) == 6
        assert all(v == "valid" for v in verdicts.values())

    def test_incomplete_suite(self, tmp_path):
        """One scenario (suite) lacks DONE sentinel → (False, suite='incomplete')."""
        rd = _make_round_dir(tmp_path, "round_dir", incomplete_suite=True)
        all_valid, verdicts = mr.round_is_fully_valid(rd, "claude_code")
        assert all_valid is False
        # Find the suite scenario key
        suite_key = next(k for k in verdicts if k.endswith("__suite"))
        assert verdicts[suite_key] == "incomplete"
        # Other five should be valid
        other = [v for k, v in verdicts.items() if not k.endswith("__suite")]
        assert all(v == "valid" for v in other)

    def test_empty_round_dir(self, tmp_path):
        """Round dir with no matching prefix → (False, {})."""
        rd = tmp_path / "empty_round"
        rd.mkdir()
        (rd / "manifest.json").write_text("{}", encoding="utf-8")
        all_valid, verdicts = mr.round_is_fully_valid(rd, "claude_code")
        assert all_valid is False
        assert verdicts == {}

    def test_wrong_prefix_ignored(self, tmp_path):
        """Subdirs for a different prefix are not matched."""
        rd = _make_round_dir(tmp_path, "round_dir", prefix="copilot_cli")
        # Query with claude_code prefix — no matches
        all_valid, verdicts = mr.round_is_fully_valid(rd, "claude_code")
        assert all_valid is False
        assert verdicts == {}


# ===========================================================================
# Tests: rewrite_manifest_run_id
# ===========================================================================

class TestRewriteManifestRunId:
    def test_run_id_updated(self, tmp_path):
        """New run_id is written; other fields are preserved."""
        rd = _make_round_dir(tmp_path, "round_dir")
        original = json.loads((rd / "manifest.json").read_text())
        assert original["run_id"] == "source_run"

        mr.rewrite_manifest_run_id(rd, "new_run_id_XYZ")

        updated = json.loads((rd / "manifest.json").read_text())
        assert updated["run_id"] == "new_run_id_XYZ"

    def test_artifacts_preserved(self, tmp_path):
        """artifacts map and all other keys are not disturbed."""
        rd = _make_round_dir(tmp_path, "round_dir")
        original = json.loads((rd / "manifest.json").read_text())

        mr.rewrite_manifest_run_id(rd, "another_run")

        updated = json.loads((rd / "manifest.json").read_text())
        assert updated["artifacts"] == original["artifacts"]
        assert updated["session_id"] == original["session_id"]
        assert updated["tool"] == original["tool"]

    def test_unicode_safe(self, tmp_path):
        """ensure_ascii=False — non-ASCII values survive the round-trip."""
        rd = tmp_path / "round_dir"
        rd.mkdir()
        data = {"run_id": "old", "note": "한국어 테스트 🎉"}
        (rd / "manifest.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        mr.rewrite_manifest_run_id(rd, "new_run")
        updated = json.loads((rd / "manifest.json").read_text(encoding="utf-8"))
        assert updated["note"] == "한국어 테스트 🎉"
        assert updated["run_id"] == "new_run"


# ===========================================================================
# Tests: state_remove_round / state_add_round
# ===========================================================================

class TestStateRoundTrip:
    def _entry(self, name: str, round_num: int = 1) -> dict:
        return {
            "round": round_num,
            "result_dir_name": name,
            "exit_code": 0,
            "start_utc": "2026-06-15T00:00:00Z",
            "end_utc": "2026-06-15T01:00:00Z",
            "artifact_dirs": [],
        }

    def test_remove_exact_match(self, tmp_path):
        """state_remove_round with exact result_dir_name returns entry + removes it."""
        state_path = _make_state(
            tmp_path, "run1",
            [self._entry("20260615_round1"), self._entry("20260615_round2", 2)],
        )
        removed = mr.state_remove_round(state_path, "claude-code", "20260615_round1")
        assert removed is not None
        assert removed["result_dir_name"] == "20260615_round1"

        data = json.loads(state_path.read_text())
        remaining = data["tool_states"]["claude-code"]["completed"]
        assert len(remaining) == 1
        assert remaining[0]["result_dir_name"] == "20260615_round2"

    def test_remove_not_found_returns_none(self, tmp_path):
        """Removing a non-existent entry returns None; state is saved unchanged."""
        state_path = _make_state(tmp_path, "run1", [self._entry("20260615_round1")])
        removed = mr.state_remove_round(state_path, "claude-code", "does_not_exist")
        assert removed is None
        # State is still saved (side-effect is a no-op remove)
        data = json.loads(state_path.read_text())
        assert len(data["tool_states"]["claude-code"]["completed"]) == 1

    def test_add_creates_structure(self, tmp_path):
        """state_add_round creates tool_states[tool]["completed"] if missing."""
        state_dir = tmp_path / "run2"
        state_dir.mkdir()
        state_path = state_dir / "state.json"
        state_path.write_text(json.dumps({"run_id": "run2"}), encoding="utf-8")

        entry = self._entry("20260615_round_new")
        mr.state_add_round(state_path, "claude-code", entry)

        data = json.loads(state_path.read_text())
        completed = data["tool_states"]["claude-code"]["completed"]
        assert len(completed) == 1
        assert completed[0]["result_dir_name"] == "20260615_round_new"

    def test_round_trip_remove_add(self, tmp_path):
        """Remove from source state, add to destination state — round-trip integrity."""
        from_state = _make_state(
            tmp_path, "from_run",
            [self._entry("round_A"), self._entry("round_B", 2)],
        )
        to_state = _make_state(tmp_path, "to_run", [self._entry("existing_round")])

        removed = mr.state_remove_round(from_state, "claude-code", "round_A")
        assert removed is not None
        mr.state_add_round(to_state, "claude-code", removed)

        from_data = json.loads(from_state.read_text())
        to_data = json.loads(to_state.read_text())

        from_completed = from_data["tool_states"]["claude-code"]["completed"]
        to_completed = to_data["tool_states"]["claude-code"]["completed"]

        assert len(from_completed) == 1
        assert from_completed[0]["result_dir_name"] == "round_B"
        assert len(to_completed) == 2
        assert any(e["result_dir_name"] == "round_A" for e in to_completed)


# ===========================================================================
# Tests: move_round end-to-end
# ===========================================================================

ROUND_NAME = "20260615_082857_d640d1_claude-code-autopilot"
REPLACE_NAME = "20260612_215242_43cb91_claude-code-autopilot"


def _setup_e2e_fixture(tmp_path: Path):
    """Build a minimal but realistic temp tree for move_round e2e tests."""
    results_root = tmp_path / "results"
    state_root = tmp_path / "state"

    FROM_RUN = "20260615_070604"
    TO_RUN = "20260612_194959"

    # Source: one fully-valid round
    _make_round_dir(results_root / FROM_RUN, ROUND_NAME)
    from_state = _make_state(
        state_root, FROM_RUN,
        [
            {
                "round": 1,
                "result_dir_name": ROUND_NAME,
                "exit_code": 0,
                "start_utc": "2026-06-15T00:00:00Z",
                "end_utc": "2026-06-15T02:00:00Z",
                "artifact_dirs": [],
            }
        ],
    )

    # Destination: has a replace target + one other completed round
    _make_round_dir(results_root / TO_RUN, REPLACE_NAME)
    _make_state(
        state_root, TO_RUN,
        [
            {
                "round": 5,
                "result_dir_name": REPLACE_NAME,
                "exit_code": 1,
                "start_utc": "2026-06-12T10:00:00Z",
                "end_utc": "2026-06-12T11:00:00Z",
                "artifact_dirs": [],
            },
            {
                "round": 4,
                "result_dir_name": "20260612_215228_1e8ff7_claude-code-autopilot",
                "exit_code": 0,
                "start_utc": "2026-06-12T09:00:00Z",
                "end_utc": "2026-06-12T10:00:00Z",
                "artifact_dirs": [],
            },
        ],
    )

    return results_root, state_root, FROM_RUN, TO_RUN


class TestMoveRoundE2E:
    def test_successful_move_with_replace(self, tmp_path):
        """Full move: source dir moved, manifest rewritten, replace dir gone,
        source state cleared, dest state gains the entry."""
        results_root, state_root, FROM_RUN, TO_RUN = _setup_e2e_fixture(tmp_path)

        summary = mr.move_round(
            FROM_RUN,
            ROUND_NAME,
            TO_RUN,
            tool="claude-code",
            replace_round_dir=REPLACE_NAME,
            results_root=results_root,
            state_root=state_root,
            require_valid=True,
        )

        # Source dir is gone
        assert not (results_root / FROM_RUN / ROUND_NAME).exists()

        # Dest dir now exists
        dest_dir = results_root / TO_RUN / ROUND_NAME
        assert dest_dir.is_dir()

        # manifest run_id rewritten
        manifest = json.loads((dest_dir / "manifest.json").read_text())
        assert manifest["run_id"] == TO_RUN

        # Replace dir is gone
        assert not (results_root / TO_RUN / REPLACE_NAME).exists()

        # Source state: round removed
        from_data = json.loads((state_root / FROM_RUN / "state.json").read_text())
        from_completed = from_data["tool_states"]["claude-code"]["completed"]
        assert not any(e["result_dir_name"] == ROUND_NAME for e in from_completed)

        # Dest state: REPLACE_NAME gone, ROUND_NAME added
        to_data = json.loads((state_root / TO_RUN / "state.json").read_text())
        to_completed = to_data["tool_states"]["claude-code"]["completed"]
        assert not any(e["result_dir_name"] == REPLACE_NAME for e in to_completed)
        assert any(e["result_dir_name"] == ROUND_NAME for e in to_completed)

        # Summary dict
        assert ROUND_NAME in summary["moved_to"]
        assert summary["replaced"] == REPLACE_NAME

    def test_require_valid_refusal(self, tmp_path):
        """require_valid=True refuses a round that has an incomplete suite."""
        results_root = tmp_path / "results"
        state_root = tmp_path / "state"
        FROM_RUN = "run_bad"
        TO_RUN = "run_dest"

        _make_round_dir(results_root / FROM_RUN, ROUND_NAME, incomplete_suite=True)
        _make_state(state_root, FROM_RUN, [])
        _make_state(state_root, TO_RUN, [])
        (results_root / TO_RUN).mkdir(parents=True, exist_ok=True)

        with pytest.raises(ValueError, match="NOT fully valid"):
            mr.move_round(
                FROM_RUN,
                ROUND_NAME,
                TO_RUN,
                results_root=results_root,
                state_root=state_root,
                require_valid=True,
            )

        # Source dir must still exist (nothing was moved)
        assert (results_root / FROM_RUN / ROUND_NAME).is_dir()

    def test_no_require_valid_moves_incomplete(self, tmp_path):
        """require_valid=False allows moving a round with an incomplete suite."""
        results_root = tmp_path / "results"
        state_root = tmp_path / "state"
        FROM_RUN = "run_bad"
        TO_RUN = "run_dest"

        _make_round_dir(results_root / FROM_RUN, ROUND_NAME, incomplete_suite=True)
        _make_state(
            state_root, FROM_RUN,
            [{"round": 1, "result_dir_name": ROUND_NAME, "exit_code": 1,
              "start_utc": "2026-06-15T00:00:00Z", "end_utc": "2026-06-15T01:00:00Z",
              "artifact_dirs": []}],
        )
        _make_state(state_root, TO_RUN, [])
        (results_root / TO_RUN).mkdir(parents=True, exist_ok=True)

        summary = mr.move_round(
            FROM_RUN, ROUND_NAME, TO_RUN,
            results_root=results_root,
            state_root=state_root,
            require_valid=False,
        )
        assert (results_root / TO_RUN / ROUND_NAME).is_dir()
        assert not (results_root / FROM_RUN / ROUND_NAME).exists()

    def test_source_not_found(self, tmp_path):
        """Raises FileNotFoundError when source round dir does not exist."""
        results_root = tmp_path / "results"
        state_root = tmp_path / "state"
        (results_root / "from_run").mkdir(parents=True)
        (results_root / "to_run").mkdir(parents=True)

        with pytest.raises(FileNotFoundError):
            mr.move_round(
                "from_run", "nonexistent_round", "to_run",
                results_root=results_root,
                state_root=state_root,
            )


# ===========================================================================
# Tests: CLI --dry-run
# ===========================================================================

class TestMainDryRun:
    def test_dry_run_prints_and_exits_0(self, tmp_path, capsys):
        """--dry-run prints intended actions, changes nothing, exits 0."""
        results_root = tmp_path / "results"
        state_root = tmp_path / "state"
        FROM_RUN = "20260615_070604"
        TO_RUN = "20260612_194959"

        _make_round_dir(results_root / FROM_RUN, ROUND_NAME)
        _make_state(state_root, FROM_RUN, [
            {"round": 1, "result_dir_name": ROUND_NAME, "exit_code": 0,
             "start_utc": "2026-06-15T00:00:00Z", "end_utc": "2026-06-15T01:00:00Z",
             "artifact_dirs": []}
        ])
        _make_state(state_root, TO_RUN, [])
        (results_root / TO_RUN).mkdir(parents=True, exist_ok=True)

        rc = mr.main([
            "--from-run-id", FROM_RUN,
            "--from-round-dir", ROUND_NAME,
            "--to-run-id", TO_RUN,
            "--replace-round-dir", REPLACE_NAME,
            "--dry-run",
            "--results-root", str(results_root),
            "--state-root", str(state_root),
        ])

        assert rc == 0

        out = capsys.readouterr().out
        assert "DRY-RUN" in out
        assert "shutil.move" in out
        assert "rewrite_manifest_run_id" in out
        assert "state_remove_round" in out
        assert "state_add_round" in out

        # Nothing was moved
        assert (results_root / FROM_RUN / ROUND_NAME).is_dir()
        # Dest dir was NOT created for the round
        assert not (results_root / TO_RUN / ROUND_NAME).exists()

    def test_dry_run_blocked_when_invalid(self, tmp_path, capsys):
        """--dry-run exits 2 when require_valid=True and source is invalid."""
        results_root = tmp_path / "results"
        state_root = tmp_path / "state"
        FROM_RUN = "run_src"
        TO_RUN = "run_dst"

        _make_round_dir(results_root / FROM_RUN, ROUND_NAME, incomplete_suite=True)
        _make_state(state_root, FROM_RUN, [])
        (results_root / TO_RUN).mkdir(parents=True, exist_ok=True)

        rc = mr.main([
            "--from-run-id", FROM_RUN,
            "--from-round-dir", ROUND_NAME,
            "--to-run-id", TO_RUN,
            "--dry-run",
            "--results-root", str(results_root),
            "--state-root", str(state_root),
        ])

        assert rc == 2
        err = capsys.readouterr().err
        assert "NOT fully valid" in err
