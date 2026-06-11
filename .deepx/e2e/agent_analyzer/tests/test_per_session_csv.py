# SPDX-License-Identifier: Apache-2.0
"""per_session.csv writer must include env-failure columns (T3/T4).

Verifies the actual CSV roundtrip — that ``write_csv(extra_columns=…)`` emits
``env_failure_signature`` + ``no_done_cause`` in the header AND populates the
values from the SessionEval rows.
"""
from __future__ import annotations

import csv
import sys
import tempfile
from pathlib import Path

_ANALYZER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ANALYZER))

from lib.aggregate import SessionEval  # noqa: E402
from lib.report import write_csv  # noqa: E402
from analyze import _PER_SESSION_EXTRA_COLUMNS  # noqa: E402


def _mk(**overrides) -> SessionEval:
    base = dict(
        round_index=1, tool="claude-code", scenario="suite", model="opus-4.6",
        session_id="sid-test", output_dirs=[], exit_status=None,
        duration_sec=None, has_start=False, has_done=False,
        tool_call_count=0, transcript_length=0,
    )
    base.update(overrides)
    return SessionEval(**base)


def test_csv_header_contains_env_columns(tmp_path):
    ev = _mk(env_failure_signature="rate-limit", output_tokens=0)
    out = tmp_path / "per_session.csv"
    write_csv([ev], out, extra_columns=_PER_SESSION_EXTRA_COLUMNS)
    with out.open() as f:
        reader = csv.DictReader(f)
        assert "env_failure_signature" in reader.fieldnames
        assert "no_done_cause" in reader.fieldnames
        rows = list(reader)
    assert rows[0]["env_failure_signature"] == "rate-limit"
    assert rows[0]["no_done_cause"] == ""  # T4 will populate; empty for now


def test_csv_populates_signature_per_session(tmp_path):
    evals = [
        _mk(session_id="ok", env_failure_signature="", has_done=True, output_tokens=2000),
        _mk(session_id="cert", env_failure_signature="cert", output_tokens=500),
        _mk(session_id="rl", env_failure_signature="rate-limit", output_tokens=0),
    ]
    out = tmp_path / "per_session.csv"
    write_csv(evals, out, extra_columns=_PER_SESSION_EXTRA_COLUMNS)
    with out.open() as f:
        by_sid = {r["session_id"]: r for r in csv.DictReader(f)}
    assert by_sid["ok"]["env_failure_signature"] == ""
    assert by_sid["cert"]["env_failure_signature"] == "cert"
    assert by_sid["rl"]["env_failure_signature"] == "rate-limit"


def test_extra_columns_keep_base_columns(tmp_path):
    # Sanity: adding extras must not drop any pre-existing base column.
    out = tmp_path / "per_session.csv"
    write_csv([_mk()], out, extra_columns=_PER_SESSION_EXTRA_COLUMNS)
    with out.open() as f:
        fields = csv.DictReader(f).fieldnames
    for required in ("run_id", "round", "tool", "scenario", "overall_score",
                     "has_start", "has_done", "session_id", "output_dirs"):
        assert required in fields, f"missing base column: {required}"
