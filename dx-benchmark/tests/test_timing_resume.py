"""Resume must preserve the ORIGINAL run start.

Bug: `timing`/`timing_history` are only persisted at finalize. If the original
run is interrupted before finalize (kill/crash/hang-timeout), its start is never
written, so a later ``--resume`` stamps the resume session's start into
``timing.start`` — which then no longer matches the run directory name
(``run_id`` = ``YYYYMMDD_HHMMSS`` = the original start). Real occurrence:
``ROCK5B+_M1/20260716_084033`` whose ``timing.start`` read ``2026-07-18 09:01``.

The resolver must recover the original start from the run-dir name when prior
timing is absent, rather than falling back to the resume session's start.
"""
from pathlib import Path

from benchmark.__main__ import _resolve_overall_start_iso, _start_from_run_dir


def test_recover_start_from_dir_when_prior_timing_missing():
    existing_fp = {"dx_all_suite_version": "v2.3.3"}  # interrupted run: no "timing"
    out_dir = Path("/x/results/ROCK5B+_M1/20260716_084033")
    session_start = "2026-07-18 09:01:57"  # the --resume session, 2 days later
    assert _resolve_overall_start_iso(existing_fp, out_dir, session_start) == "2026-07-16 08:40:33"


def test_prefer_recorded_prior_start():
    existing_fp = {"timing": {"start": "2026-07-16 08:40:33"}}
    out_dir = Path("/x/results/env/20260716_084033")
    assert _resolve_overall_start_iso(existing_fp, out_dir, "2026-07-18 09:01:57") == "2026-07-16 08:40:33"


def test_fresh_run_dir_matches_session_start():
    out_dir = Path("/x/results/env/20260716_084033")
    assert _resolve_overall_start_iso({}, out_dir, "2026-07-16 08:40:33") == "2026-07-16 08:40:33"


def test_unparseable_dir_falls_back_to_session():
    out_dir = Path("/x/results/env/not-a-timestamp")
    assert _resolve_overall_start_iso({}, out_dir, "2026-07-18 09:01:57") == "2026-07-18 09:01:57"


def test_start_from_run_dir_parsing():
    assert _start_from_run_dir(Path("/a/b/20260716_084033")) == "2026-07-16 08:40:33"
    assert _start_from_run_dir(Path("/a/b/garbage")) is None
