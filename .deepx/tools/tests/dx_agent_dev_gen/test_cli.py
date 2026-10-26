# SPDX-License-Identifier: Apache-2.0
"""
Tests for dx-agent-gen CLI error handling.

A RuntimeError raised by the generator (e.g. an unresolved template
placeholder) must surface cleanly with exit code 1 — not an uncaught
traceback. `generate` has no report to preserve, so it still surfaces the
error as a clean `error: <msg>` on stderr (see test below). `check` (as of
polish round Q6) instead catches the RuntimeError internally per-platform
and folds it into the report as an `ERROR: <platform>: <msg>` line, so any
drift already found in OTHER platforms is not lost — cli.py's try/except
around `check` remains only as a safety net for anything check() does not
itself catch.
"""

from __future__ import annotations

from pathlib import Path

import pytest


def _mk_repo_with_bad_template(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".deepx" / "templates" / "en").mkdir(parents=True)
    (repo / ".deepx" / "templates" / "en" / "CLAUDE.md.tmpl").write_text(
        "{{FOO}}\n", encoding="utf-8"
    )
    return repo


def test_check_reports_runtime_error_cleanly(tmp_path, capsys):
    from dx_agent_dev_gen.cli import main

    repo = _mk_repo_with_bad_template(tmp_path)
    rc = main(["check", "--repo", str(repo)])
    captured = capsys.readouterr()

    assert rc == 1
    assert "ERROR: instructions:" in captured.out
    assert "FOO" in captured.out
    # No uncaught traceback reached stderr.
    assert captured.err == ""


def test_generate_reports_runtime_error_cleanly(tmp_path, capsys):
    from dx_agent_dev_gen.cli import main

    repo = _mk_repo_with_bad_template(tmp_path)
    rc = main(["generate", "--repo", str(repo)])
    captured = capsys.readouterr()

    assert rc == 1
    assert "error:" in captured.err
    assert "FOO" in captured.err


def test_unexpected_exception_exits_2_as_internal_failure(tmp_path, capsys, monkeypatch):
    """A crash inside the generator (anything that is not the documented
    RuntimeError contract) must NOT look like drift (rc 1): report it as an
    internal failure with rc 2 and keep the traceback on stderr for debugging.
    (GHES run 982: a TypeError at import time was reported as 'out of date'.)"""
    from dx_agent_dev_gen import generator as gen_mod
    from dx_agent_dev_gen.cli import main

    repo = _mk_repo_with_bad_template(tmp_path)

    def boom(self, platform="all"):
        raise ValueError("boom")

    monkeypatch.setattr(gen_mod.Generator, "check", boom)
    rc = main(["check", "--repo", str(repo)])
    captured = capsys.readouterr()

    assert rc == 2
    assert "error: internal failure" in captured.err
    assert "ValueError" in captured.err and "boom" in captured.err
    assert "Traceback" in captured.err
