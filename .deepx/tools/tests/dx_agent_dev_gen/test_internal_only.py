# SPDX-License-Identifier: Apache-2.0
"""
Tests for dx_agent_dev_gen.internal_only — the shared skip-predicate used by
the agent-parity / canonical-source / header conformance checks to tolerate
internal-only, hand-authored `.github/agents/*.md` files (release-excluded,
e.g. copilot-pr-review.md, dx_stream's dxr-* review agents) that never reach
the public github.com export.
"""

from __future__ import annotations

from pathlib import Path

from dx_agent_dev_gen.internal_only import (
    is_internal_only_agent,
    release_excluded_paths,
)


def _write(path: Path, content: str = "content") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


class TestReleaseExcludedPaths:
    def test_missing_file_returns_empty_set(self, tmp_path):
        """No .github/release-excluded → empty set, not an error."""
        assert release_excluded_paths(tmp_path) == set()

    def test_lists_non_comment_non_blank_lines(self, tmp_path):
        _write(
            tmp_path / ".github" / "release-excluded",
            "# comment\n"
            ".github/agents/copilot-pr-review.md\n"
            "\n"
            "dx_stream/apps/face_recognition\n",
        )
        assert release_excluded_paths(tmp_path) == {
            ".github/agents/copilot-pr-review.md",
            "dx_stream/apps/face_recognition",
        }

    def test_trailing_slash_stripped(self, tmp_path):
        _write(tmp_path / ".github" / "release-excluded", ".github/agents/dxr-kb/\n")
        assert release_excluded_paths(tmp_path) == {".github/agents/dxr-kb"}


class TestIsInternalOnlyAgent:
    def test_release_excluded_listing_is_internal_only(self, tmp_path):
        """(a) Listed in .github/release-excluded -> True, even with no header/source."""
        _write(
            tmp_path / ".github" / "release-excluded",
            ".github/agents/copilot-pr-review.md\n",
        )
        agent = _write(
            tmp_path / ".github" / "agents" / "copilot-pr-review.md",
            "hand-authored review prompt, no header",
        )
        assert is_internal_only_agent(tmp_path, agent) is True

    def test_hand_authored_no_header_no_source_is_internal_only(self, tmp_path):
        """(b) No release-excluded entry, but no header and no .deepx source -> True."""
        agent = _write(
            tmp_path / ".github" / "agents" / "dxr-planner.agent.md",
            "---\ndescription: hand-authored\n---\nbody",
        )
        assert is_internal_only_agent(tmp_path, agent) is True

    def test_generated_file_with_header_is_not_internal_only(self, tmp_path):
        """(c) AUTO-GENERATED header present -> False (real generated file)."""
        agent = _write(
            tmp_path / ".github" / "agents" / "dx-model-manager.agent.md",
            "<!-- AUTO-GENERATED: do not edit -->\nbody",
        )
        assert is_internal_only_agent(tmp_path, agent) is False

    def test_source_exists_but_header_missing_is_real_drift(self, tmp_path):
        """(d) Has a .deepx/agents/<stem>.md source but no header -> False, so
        parity/header checks still flag this as drift instead of silently
        skipping it."""
        _write(
            tmp_path / ".deepx" / "agents" / "dx-model-manager.md",
            "canonical source",
        )
        agent = _write(
            tmp_path / ".github" / "agents" / "dx-model-manager.agent.md",
            "body without the marker",
        )
        assert is_internal_only_agent(tmp_path, agent) is False

    def test_missing_release_excluded_file_falls_back_to_header_source_check(
        self, tmp_path
    ):
        """(e) No .github/release-excluded at all -> release_excluded_paths is
        empty, and the header/source check still applies correctly."""
        agent = _write(
            tmp_path / ".github" / "agents" / "copilot-pr-review.md",
            "hand-authored, no header",
        )
        assert is_internal_only_agent(tmp_path, agent) is True

    def test_plain_md_suffix_stem_resolution(self, tmp_path):
        """Non-'.agent.md' .github files (e.g. plain *.md) resolve their stem
        by stripping only '.md', not '.agent.md'."""
        _write(tmp_path / ".deepx" / "agents" / "copilot-pr-review.md", "source")
        agent = _write(
            tmp_path / ".github" / "agents" / "copilot-pr-review.md",
            "<!-- AUTO-GENERATED -->\nbody",
        )
        assert is_internal_only_agent(tmp_path, agent) is False
