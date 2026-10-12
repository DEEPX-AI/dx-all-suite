"""Tests never run a real agent CLI.

A test that sends a run without naming an agent gets the server default adapter (copilot); on a machine
with copilot installed and signed in, that spends real premium requests. All tests set
`DX_AGENT_NO_REAL_RUN=1`, and with it set an adapter does not execute the real CLI on PATH. Tests that use
a fake script (tmp) still run.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path


def test_the_test_session_forbids_real_agent_runs():
    assert os.environ.get("DX_AGENT_NO_REAL_RUN") == "1"


def test_a_real_cli_on_path_is_refused(tmp_path, monkeypatch):
    from dx_agent_dev.core.adapters.copilot import CopilotAdapter

    real = tmp_path / "bin" / "copilot"
    real.parent.mkdir()
    real.write_text("#!/bin/sh\necho SHOULD-NOT-RUN > \"$HOME/ran\"\n")
    real.chmod(real.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("PATH", str(real.parent))
    monkeypatch.setenv("HOME", str(tmp_path))
    events = list(CopilotAdapter().run("hi", tmp_path, [str(tmp_path)]))
    assert events and events[0]["type"] == "error", events
    assert "test" in events[0]["text"].lower()
    assert not (tmp_path / "ran").exists(), "진짜 CLI 가 돌았다"


def test_a_fake_cli_path_still_runs(tmp_path):
    """Tests that drive an adapter with a fake script: anything not on PATH is not blocked."""
    from dx_agent_dev.core.adapters.copilot import CopilotAdapter

    fake = tmp_path / "fake-copilot"
    fake.write_text("#!/bin/sh\necho hello\n")
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    events = list(CopilotAdapter(cli_path=str(fake)).run("hi", tmp_path, [str(tmp_path)]))
    assert not any(e.get("type") == "error" and "test" in e.get("text", "").lower() for e in events), events
