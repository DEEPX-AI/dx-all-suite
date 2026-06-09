# SPDX-License-Identifier: Apache-2.0
"""Unit tests for ``parse_claude_session`` project-path encoding and lookup.

These pin down the rule that Claude Code uses when forming
``~/.claude/projects/<encoded>/`` directory names — namely, that **every**
non-alphanumeric character (not just '/') becomes '-'.  The historical bug
was that ``encode_project_path`` only replaced '/', leaving '_' intact, so
sub-project workdirs like ``dx-runtime/dx_app`` never resolved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# dx_transcripts is on PYTHONPATH=.deepx/tools/src (see tools/tests run command)
from dx_transcripts import parse_claude_session as pcs


def test_encode_underscore_to_dash():
    """Underscores in path segments MUST become '-' (Claude Code's actual rule)."""
    assert pcs.encode_project_path("/dx-runtime/dx_app") == "-dx-runtime-dx-app"
    assert pcs.encode_project_path("/dx-runtime/dx_stream") == "-dx-runtime-dx-stream"


def test_encode_dots_to_dash():
    """Dots also become '-'."""
    assert pcs.encode_project_path("/home/.claude") == "-home--claude"


def test_encode_slash_only_path_unchanged():
    """Regression guard — slash-only paths still encode correctly."""
    assert pcs.encode_project_path("/dx-compiler") == "-dx-compiler"


def test_find_project_dir_resolves_underscore_path(tmp_path, monkeypatch):
    """The exact bug case: an underscore in the workdir must resolve."""
    fake_projects = tmp_path / "projects"
    target = fake_projects / "-dx-runtime-dx-app"
    target.mkdir(parents=True)
    monkeypatch.setattr(pcs, "CLAUDE_PROJECTS_DIR", fake_projects)

    resolved = pcs.find_project_dir("/dx-runtime/dx_app")
    assert resolved is not None
    assert resolved == target


def test_find_project_dir_legacy_fallback(tmp_path, monkeypatch):
    """Backward compat: a directory created under the OLD encoding (only '/'→'-')
    must still resolve, so existing local environments are not broken."""
    fake_projects = tmp_path / "projects"
    legacy_target = fake_projects / "-dx-runtime-dx_app"  # underscore preserved
    legacy_target.mkdir(parents=True)
    monkeypatch.setattr(pcs, "CLAUDE_PROJECTS_DIR", fake_projects)

    resolved = pcs.find_project_dir("/dx-runtime/dx_app")
    assert resolved is not None
    assert resolved == legacy_target


def test_find_sessions_by_uuid_bypasses_time_filter(tmp_path, monkeypatch):
    """``find_sessions(session_id=...)`` must not depend on workdir encoding
    nor on the after/before time filter — this is the path the conftest fix
    uses to bypass jsonl-flush timing races."""
    fake_projects = tmp_path / "projects"
    proj_dir = fake_projects / "-any-encoded-name"
    proj_dir.mkdir(parents=True)
    target_uuid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    target_file = proj_dir / f"{target_uuid}.jsonl"
    # Minimal jsonl that _extract_metadata can parse — a single user event
    target_file.write_text(
        '{"type":"user","timestamp":"2026-05-22T11:00:00.000Z",'
        '"sessionId":"' + target_uuid + '","cwd":"/anything","gitBranch":"main",'
        '"version":"x","userType":"external"}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(pcs, "CLAUDE_PROJECTS_DIR", fake_projects)

    metas = pcs.find_sessions(session_id=target_uuid)
    assert len(metas) == 1
    assert metas[0].session_id == target_uuid
