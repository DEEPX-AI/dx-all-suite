# SPDX-License-Identifier: Apache-2.0
"""Tests for e2e_monitor.py DEFAULT-path interactive run selection.

The default invocation (no args) should, when stdin is a TTY and more than one
run exists, prompt the user to pick a run (like --select) and then live-monitor
the chosen run. When stdin is NOT a TTY (piped/scripted), or only one run
exists, or a run-id/--list/--select/--status is given, it must NOT prompt.

Covers:
  - _should_prompt_default  (PURE decision matrix for whether to prompt)
  - _select_run_id          (list + prompt + resolve → run_id | None, input injectable)
  - _resolve_selection      (already tested in test_monitor_list_select.py; a couple
                             extra cases here for the index/None edges used by the
                             default path)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest  # noqa: F401

_E2E_DIR = Path(__file__).resolve().parents[1]  # .deepx/e2e/
sys.path.insert(0, str(_E2E_DIR))

import e2e_monitor as mon  # noqa: E402


# --- _should_prompt_default -------------------------------------------------
# Signature:
#   _should_prompt_default(run_id_arg, is_list, is_select, is_status, isatty, num_runs) -> bool
# True ONLY when: no run_id_arg AND not list AND not select AND not status
#                 AND isatty AND num_runs > 1. False otherwise.


def test_should_prompt_default_true_when_tty_and_multiple_runs():
    assert mon._should_prompt_default(None, False, False, False, True, 3) is True
    assert mon._should_prompt_default(None, False, False, False, True, 2) is True


def test_should_prompt_default_false_when_not_tty():
    # Piped / scripted → keep latest-run behavior, never prompt.
    assert mon._should_prompt_default(None, False, False, False, False, 3) is False


def test_should_prompt_default_false_when_single_run():
    assert mon._should_prompt_default(None, False, False, False, True, 1) is False
    assert mon._should_prompt_default(None, False, False, False, True, 0) is False


def test_should_prompt_default_false_when_run_id_given():
    assert mon._should_prompt_default("20260612_215200", False, False, False, True, 3) is False


def test_should_prompt_default_false_when_list():
    assert mon._should_prompt_default(None, True, False, False, True, 3) is False


def test_should_prompt_default_false_when_select():
    assert mon._should_prompt_default(None, False, True, False, True, 3) is False


def test_should_prompt_default_false_when_status():
    assert mon._should_prompt_default(None, False, False, True, True, 3) is False


# --- _select_run_id ---------------------------------------------------------
# Signature:
#   _select_run_id(run_ids, input_fn=input) -> Optional[str]
# Prints the indexed list, prompts once via input_fn, resolves via
# _resolve_selection. EOFError / KeyboardInterrupt → None (clean quit).

RUN_IDS = ["20260612_210247", "20260612_215200", "20260612_194959"]


def test_select_run_id_index_picks_nth(capsys):
    chosen = mon._select_run_id(RUN_IDS, input_fn=lambda _prompt: "2")
    assert chosen == "20260612_215200"


def test_select_run_id_quit_returns_none():
    chosen = mon._select_run_id(RUN_IDS, input_fn=lambda _prompt: "q")
    assert chosen is None


def test_select_run_id_eof_returns_none():
    def _raise_eof(_prompt):
        raise EOFError

    chosen = mon._select_run_id(RUN_IDS, input_fn=_raise_eof)
    assert chosen is None


def test_select_run_id_keyboard_interrupt_returns_none():
    def _raise_kbi(_prompt):
        raise KeyboardInterrupt

    chosen = mon._select_run_id(RUN_IDS, input_fn=_raise_kbi)
    assert chosen is None


def test_select_run_id_empty_run_ids_returns_none():
    # No runs at all → None without prompting.
    called = {"n": 0}

    def _spy(_prompt):
        called["n"] += 1
        return "1"

    chosen = mon._select_run_id([], input_fn=_spy)
    assert chosen is None
    assert called["n"] == 0  # never prompted


# --- _resolve_selection edge cases used by the default path -----------------

def test_resolve_selection_index_and_none():
    assert mon._resolve_selection("2", RUN_IDS) == "20260612_215200"
    assert mon._resolve_selection("q", RUN_IDS) is None
