# SPDX-License-Identifier: Apache-2.0
"""Tests for e2e_runner --redo-env-failures (PR3).

Detect env-failed rounds (cert/SSL, codex model-refresh, copilot empty-unknown)
from a completed run, delete their records + result dirs, and reset state so
--resume re-runs them to the target count. Classification delegates to the
shared SSOT (agent_analyzer/lib/env_failure.py) so the runner and the analyzer
agree on what an env failure is.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parents[1]  # .deepx/tests/
sys.path.insert(0, str(_TESTS_DIR))

import e2e_runner as er  # noqa: E402


# --- fixtures: synthesise a scenario subdir on disk -------------------------

def _make_scenario(parent: Path, name: str, *, files: dict | None = None,
                   session_subdir: str | None = None,
                   empty_unknown: bool = False) -> Path:
    """Create a <prefix>__<scenario> subdir with the given files.

    files: {filename: text}. session_subdir: name of a dx-agent-dev output
    dir to create (empty). empty_unknown: create an empty session-logs-unknown/.
    """
    sd = parent / name
    sd.mkdir(parents=True, exist_ok=True)
    for fn, txt in (files or {}).items():
        (sd / fn).write_text(txt, encoding="utf-8")
    if session_subdir:
        (sd / session_subdir).mkdir(parents=True, exist_ok=True)
    if empty_unknown:
        (sd / "session-logs-unknown").mkdir(parents=True, exist_ok=True)
    return sd


DONE_MD = "Run complete.\n[DX-AGENT-DEV: DONE (output-dir: dx-compiler/dx-agent-dev/x)]\n"
START_ONLY_MD = "[DX-AGENT-DEV: START]\nworking...\n"
REAL_WORK_JSONL = (
    '{"type":"assistant","content":"..."}\n' * 30
    + '{"type":"tool_use","name":"bash"}\n' * 30
)
CERT_JSONL = '{"type":"error","error":{"name":"UnknownError","data":{"message":"unable to verify the first certificate"}}}\n'


# --- _classify_round_scenario -----------------------------------------------

def test_classify_valid_done(tmp_path):
    sd = _make_scenario(tmp_path, "claude_code__compiler",
                        files={"x-session.md": DONE_MD,
                               "x-stream.jsonl": REAL_WORK_JSONL})
    verdict, sigs = er._classify_round_scenario(sd)
    assert verdict == "valid"


def test_classify_cert_envfail(tmp_path):
    sd = _make_scenario(tmp_path, "cursor_cli__suite",
                        files={"x-session.md": START_ONLY_MD,
                               "x-stream.jsonl": CERT_JSONL})
    verdict, sigs = er._classify_round_scenario(sd)
    assert verdict == "envfail"
    assert "cert" in sigs


def test_classify_incomplete_real_work(tmp_path):
    sd = _make_scenario(tmp_path, "cursor_cli__suite",
                        files={"x-session.md": START_ONLY_MD,
                               "x-stream.jsonl": REAL_WORK_JSONL},
                        session_subdir="dx-agent-dev-out")
    verdict, sigs = er._classify_round_scenario(sd)
    assert verdict == "incomplete"
    assert not sigs


def test_classify_empty_unknown_envfail(tmp_path):
    sd = _make_scenario(tmp_path, "copilot_cli__compiler", empty_unknown=True)
    verdict, sigs = er._classify_round_scenario(sd)
    assert verdict == "envfail"


def test_classify_skip_empty(tmp_path):
    sd = _make_scenario(tmp_path, "copilot_cli__compiler")
    verdict, sigs = er._classify_round_scenario(sd)
    assert verdict == "skip"


def test_classify_codex_modelrefresh_zero_cmd(tmp_path):
    md = (START_ONLY_MD
          + "ERROR codex_models_manager: failed to refresh available models: timeout\n"
          + "**Commands:** 0 total\n")
    sd = _make_scenario(tmp_path, "codex_cli__dx_app",
                        files={"x-session.md": md})
    verdict, sigs = er._classify_round_scenario(sd)
    assert verdict == "envfail"
    assert "model-refresh-timeout" in sigs


def test_classify_codex_modelrefresh_with_cmd_incomplete(tmp_path):
    # codex R5 compiler: model-refresh warning BUT 96 commands of real work, no DONE
    md = (START_ONLY_MD
          + "WARNING failed to refresh available models: timeout\n"
          + "**Commands:** 96 total\n")
    sd = _make_scenario(tmp_path, "codex_cli__compiler",
                        files={"x-session.md": md, "x-stream.jsonl": REAL_WORK_JSONL},
                        session_subdir="dx-agent-dev-out")
    verdict, sigs = er._classify_round_scenario(sd)
    assert verdict == "incomplete"


# --- _analyze_round_env -----------------------------------------------------

def test_analyze_round_counts(tmp_path):
    rd = tmp_path / "20260527_010101_abc123_claude-code-autopilot"
    rd.mkdir()
    _make_scenario(rd, "claude_code__compiler", files={"a-session.md": DONE_MD})
    _make_scenario(rd, "claude_code__dx_app", files={"b-session.md": DONE_MD})
    _make_scenario(rd, "claude_code__suite",
                   files={"c-session.md": START_ONLY_MD, "c-stream.jsonl": CERT_JSONL})
    (rd / "manifest.json").write_text("{}", encoding="utf-8")
    (rd / "SUMMARY.md").write_text("summary", encoding="utf-8")
    valid, incomplete, envfail, total, sigs = er._analyze_round_env(rd)
    assert (valid, incomplete, envfail, total) == (2, 0, 1, 3)
    assert "cert" in sigs


# --- _round_delete_worthy (criterion) ---------------------------------------

def test_delete_worthy_cert_taint():
    # 4 valid + 1 incomplete + 1 cert envfail → cert taint → delete
    assert er._round_delete_worthy(valid=4, incomplete=1, envfail=1, total=6,
                                   sigs={"cert"}) is True


def test_delete_worthy_env_majority():
    assert er._round_delete_worthy(valid=1, incomplete=0, envfail=5, total=6,
                                   sigs={"model-refresh-timeout"}) is True


def test_delete_worthy_rate_limit_minority():
    # 4 valid + 2 rate-limit envfail (MINORITY, not >valid) → still delete-worthy:
    # rate-limit is transient-fixable like cert, and a partially rate-limited round
    # must not silently pollute a model-eval comparison (real case: opus4.8 R2).
    assert er._round_delete_worthy(valid=4, incomplete=0, envfail=2, total=6,
                                   sigs={"rate-limit"}) is True


def test_keep_incomplete_no_cert():
    # 5 valid + 1 incomplete, no cert/rate-limit → keep (analyzer handles per-session)
    assert er._round_delete_worthy(valid=5, incomplete=1, envfail=0, total=6,
                                   sigs=set()) is False


def test_keep_all_valid():
    assert er._round_delete_worthy(valid=6, incomplete=0, envfail=0, total=6,
                                   sigs=set()) is False


def test_empty_round_not_delete_worthy():
    assert er._round_delete_worthy(valid=0, incomplete=0, envfail=0, total=0,
                                   sigs=set()) is False


# --- redo_env_failures (end-to-end on a synthetic state+results layout) -----

def _build_run(tmp_path, monkeypatch):
    """Lay out runner_state/<run>/state.json + results/<run>/<dirs>/ on tmp."""
    run_id = "20260527_999999"
    state_root = tmp_path / "runner_state"
    results_root = tmp_path / "results"
    monkeypatch.setattr(er, "RUNNER_STATE_DIR", state_root)
    monkeypatch.setattr(er, "RESULTS_ROOT", results_root)

    run_results = results_root / run_id
    run_results.mkdir(parents=True)

    def _round_dir(ts, tool, scenarios):
        rd = run_results / f"{ts}_aaa111_{tool}-autopilot"
        rd.mkdir()
        for scen, kind in scenarios.items():
            key = f"{tool.replace('-', '_')}__{scen}"
            if kind == "valid":
                _make_scenario(rd, key, files={"s-session.md": DONE_MD})
            elif kind == "cert":
                _make_scenario(rd, key, files={"s-session.md": START_ONLY_MD,
                                               "s-stream.jsonl": CERT_JSONL})
            elif kind == "incomplete":
                _make_scenario(rd, key, files={"s-session.md": START_ONLY_MD,
                                               "s-stream.jsonl": REAL_WORK_JSONL},
                               session_subdir="out")
        (rd / "manifest.json").write_text("{}", encoding="utf-8")
        return rd.name

    # claude R1 valid (all 6 valid), R2 cert-tainted (5 valid + 1 cert)
    r1 = _round_dir("20260527_000001", "claude-code",
                    {s: "valid" for s in
                     ("compiler", "dx_app", "dx_stream", "dx_stream_cascaded", "runtime", "suite")})
    r2_scen = {s: "valid" for s in ("compiler", "dx_app", "dx_stream", "dx_stream_cascaded", "runtime")}
    r2_scen["suite"] = "cert"
    r2 = _round_dir("20260527_000002", "claude-code", r2_scen)

    state_dir = state_root / run_id
    state_dir.mkdir(parents=True)
    (state_dir / "logs").mkdir()
    state = {
        "run_id": run_id, "target_rounds": 2, "thinking": False,
        "mode": "sequential", "tools": ["claude-code"], "runner_pid": None,
        "status": "done",
        "tool_states": {
            "claude-code": {
                "completed": [
                    {"round": 1, "result_dir_name": r1, "exit_code": 0,
                     "start_utc": "2026-05-27T00:00:01Z", "end_utc": "2026-05-27T00:10:01Z",
                     "artifact_dirs": []},
                    {"round": 2, "result_dir_name": r2, "exit_code": 1,
                     "start_utc": "2026-05-27T00:00:02Z", "end_utc": "2026-05-27T00:10:02Z",
                     "artifact_dirs": []},
                ],
                "in_progress": None, "status": "done", "pid": None,
            }
        },
    }
    (state_dir / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
    return run_id, state_root, results_root, r1, r2


def test_redo_env_failures_deletes_cert_round(tmp_path, monkeypatch):
    run_id, state_root, results_root, r1, r2 = _build_run(tmp_path, monkeypatch)

    flagged = er.redo_env_failures(run_id)

    # R2 (cert-tainted) flagged; R1 (all valid) not flagged
    rounds = {(f["tool"], f["round"]) for f in flagged}
    assert ("claude-code", 2) in rounds
    assert ("claude-code", 1) not in rounds

    # R2 result dir deleted; R1 kept
    assert not (results_root / run_id / r2).exists()
    assert (results_root / run_id / r1).exists()

    # state: R2 record removed, status reset so resume re-runs
    state = json.loads((state_root / run_id / "state.json").read_text())
    ts = state["tool_states"]["claude-code"]
    assert [c["round"] for c in ts["completed"]] == [1]
    assert ts["status"] == "running"
    assert ts["in_progress"] is None
    assert state["status"] == "running"


def test_redo_env_failures_noop_when_clean(tmp_path, monkeypatch):
    run_id, state_root, results_root, r1, r2 = _build_run(tmp_path, monkeypatch)
    # Make R2's suite valid too → no env failures
    r2_suite = results_root / run_id / r2 / "claude_code__suite"
    for f in r2_suite.iterdir():
        f.unlink()
    (r2_suite / "s-session.md").write_text(DONE_MD, encoding="utf-8")

    flagged = er.redo_env_failures(run_id)
    assert flagged == []
    # both rounds preserved
    assert (results_root / run_id / r1).exists()
    assert (results_root / run_id / r2).exists()
    state = json.loads((state_root / run_id / "state.json").read_text())
    assert [c["round"] for c in state["tool_states"]["claude-code"]["completed"]] == [1, 2]
