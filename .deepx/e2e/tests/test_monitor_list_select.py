# SPDX-License-Identifier: Apache-2.0
"""Tests for e2e_monitor.py --list effective-status + --select run picker.

Covers the new PURE helpers added for reality-reflecting --list and the
interactive run selector:
  - _effective_status     (state status + live salvage → "re-running" | passthrough)
  - _resolve_selection    (index / run_id / substring → run_id | None)
  - _list_progress_cell   (validity-led Progress cell with "(N ran)" context)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest  # noqa: F401

_E2E_DIR = Path(__file__).resolve().parents[1]  # .deepx/e2e/
sys.path.insert(0, str(_E2E_DIR))

import e2e_monitor as mon  # noqa: E402


# --- _effective_status ------------------------------------------------------

def test_effective_status_live_salvage_rerunning():
    salvage = {"status": "running", "pid": 12345}
    assert mon._effective_status("done", salvage, True) == "re-running"


def test_effective_status_no_salvage_passthrough():
    assert mon._effective_status("done", None, False) == "done"
    assert mon._effective_status("running", None, False) == "running"
    assert mon._effective_status("aborted", None, False) == "aborted"


def test_effective_status_salvage_pid_dead_passthrough():
    # Salvage marker present but its process is dead → not re-running.
    salvage = {"status": "running", "pid": 999999}
    assert mon._effective_status("done", salvage, False) == "done"


def test_effective_status_salvage_not_running_passthrough():
    # Salvage present but not in "running" state → passthrough even if pid alive.
    salvage = {"status": "complete", "pid": 12345}
    assert mon._effective_status("done", salvage, True) == "done"


# --- _resolve_selection -----------------------------------------------------

RUN_IDS = ["20260612_210247", "20260612_215200", "20260612_194959"]


def test_resolve_selection_index():
    assert mon._resolve_selection("3", RUN_IDS) == "20260612_194959"
    assert mon._resolve_selection("1", RUN_IDS) == "20260612_210247"


def test_resolve_selection_exact_run_id():
    assert mon._resolve_selection("20260612_215200", RUN_IDS) == "20260612_215200"


def test_resolve_selection_substring():
    assert mon._resolve_selection("194959", RUN_IDS) == "20260612_194959"


def test_resolve_selection_quit_empty_invalid():
    assert mon._resolve_selection("q", RUN_IDS) is None
    assert mon._resolve_selection("", RUN_IDS) is None
    assert mon._resolve_selection("99", RUN_IDS) is None  # out of range
    assert mon._resolve_selection("nomatch", RUN_IDS) is None


def test_resolve_selection_ambiguous_substring_none():
    # A substring matching >1 run_id is ambiguous → None (no silent first-match).
    ids = ["20260612_210247", "20260612_215200"]
    assert mon._resolve_selection("202606", ids) is None


# --- _list_progress_cell ----------------------------------------------------

MIXED_STATUSES = [
    {"round_index": 1, "status": "valid"},
    {"round_index": 2, "status": "valid"},
    {"round_index": 3, "status": "re-running"},
    {"round_index": 4, "status": "env-failed"},
    {"round_index": 5, "status": "env-failed"},
]


def test_list_progress_cell_mixed():
    cell = mon._list_progress_cell(MIXED_STATUSES, 5, "claude-code", 5)
    assert cell == "valid:2/5 ⟳R3 ✗R4,R5  (5 ran)"


def test_list_progress_cell_all_valid():
    statuses = [{"round_index": i, "status": "valid"} for i in range(1, 6)]
    cell = mon._list_progress_cell(statuses, 5, "claude-code", 5)
    assert cell == "valid:5/5  (5 ran)"


def test_list_progress_cell_fallback_when_empty():
    # No validity classification available → fall back to <tool>:<completed>/<target>.
    cell = mon._list_progress_cell([], 5, "claude-code", 5)
    assert cell == "claude-code:5/5"
