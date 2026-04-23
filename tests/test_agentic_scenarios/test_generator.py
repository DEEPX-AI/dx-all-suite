# SPDX-License-Identifier: Apache-2.0
"""
Tests for dx-agentic-dev-gen generator correctness.

Validates:
- Generator package is importable and CLI is functional
- Generator check is clean for all 5 repos (no drift)
- Generator is idempotent (generate twice = same output)
- Canonical source completeness (.deepx/agents/ → platform counterparts)
- Frontmatter transformation rules
- Generated files have AUTO-GENERATED header
- .github/skills/ is not a symlink (inline copy)
- KO files have same section structure as EN
- No leftover template placeholders in generated files
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from .conftest import PROJECT_ROOTS, SUITE_ROOT


# ---------------------------------------------------------------------------
# Generator package availability
# ---------------------------------------------------------------------------


class TestGeneratorPackage:
    """dx-agentic-dev-gen must be installed and functional."""

    def test_importable(self):
        """Package can be imported."""
        import dx_agentic_dev_gen
        assert dx_agentic_dev_gen.__version__

    def test_cli_version(self):
        """CLI --version works."""
        from dx_agentic_dev_gen.cli import main
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0


# ---------------------------------------------------------------------------
# Generator check clean (no drift)
# ---------------------------------------------------------------------------


class TestGeneratorCheckClean:
    """All 5 repos must have no drift between .deepx/ and generated files."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_check_clean(self, project: str, root: Path):
        """dx-agentic-gen check must exit 0 (no drift)."""
        from dx_agentic_dev_gen.generator import Generator

        gen = Generator(root)
        clean, report = gen.check(platform="all")
        assert clean, (
            f"{project}: Generator drift detected:\n" + "\n".join(report)
        )


# ---------------------------------------------------------------------------
# Canonical source completeness
# ---------------------------------------------------------------------------


class TestCanonicalSourceCompleteness:
    """Every platform agent file must have a .deepx/agents/ canonical source."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_github_agents_have_canonical_source(self, project: str, root: Path):
        """Every .github/agents/*.agent.md has a .deepx/agents/*.md source."""
        github_agents = root / ".github" / "agents"
        deepx_agents = root / ".deepx" / "agents"
        if not github_agents.exists():
            pytest.skip(f"{project}: no .github/agents/")
        if not deepx_agents.exists():
            pytest.skip(f"{project}: no .deepx/agents/")

        orphans = []
        for gh_file in sorted(github_agents.glob("*.agent.md")):
            stem = gh_file.stem.replace(".agent", "")
            deepx_file = deepx_agents / f"{stem}.md"
            if not deepx_file.exists():
                orphans.append(gh_file.name)
        assert not orphans, (
            f"{project}: .github/agents/ files without .deepx/agents/ source: {orphans}"
        )

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_opencode_agents_have_canonical_source(self, project: str, root: Path):
        """Every .opencode/agents/*.md has a .deepx/agents/*.md source."""
        oc_agents = root / ".opencode" / "agents"
        deepx_agents = root / ".deepx" / "agents"
        if not oc_agents.exists():
            pytest.skip(f"{project}: no .opencode/agents/")
        if not deepx_agents.exists():
            pytest.skip(f"{project}: no .deepx/agents/")

        orphans = []
        for oc_file in sorted(oc_agents.glob("*.md")):
            deepx_file = deepx_agents / oc_file.name
            if not deepx_file.exists():
                orphans.append(oc_file.name)
        assert not orphans, (
            f"{project}: .opencode/agents/ files without .deepx/agents/ source: {orphans}"
        )


# ---------------------------------------------------------------------------
# Generated file header
# ---------------------------------------------------------------------------


class TestGeneratedHeader:
    """Generated files must have AUTO-GENERATED header."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_github_agents_have_header(self, project: str, root: Path):
        """Generated .github/agents/ files must contain AUTO-GENERATED marker."""
        github_agents = root / ".github" / "agents"
        if not github_agents.exists():
            pytest.skip(f"{project}: no .github/agents/")

        missing = []
        for f in sorted(github_agents.glob("*.agent.md")):
            content = f.read_text(encoding="utf-8")
            if "AUTO-GENERATED" not in content:
                missing.append(f.name)
        assert not missing, (
            f"{project}: .github/agents/ files missing AUTO-GENERATED header: {missing}"
        )

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_claude_agents_have_header(self, project: str, root: Path):
        """Generated .claude/agents/ files must contain AUTO-GENERATED marker."""
        claude_agents = root / ".claude" / "agents"
        if not claude_agents.exists():
            pytest.skip(f"{project}: no .claude/agents/")

        missing = []
        for f in sorted(claude_agents.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            if "AUTO-GENERATED" not in content:
                missing.append(f.name)
        assert not missing, (
            f"{project}: .claude/agents/ files missing AUTO-GENERATED header: {missing}"
        )


# ---------------------------------------------------------------------------
# No symlinks for .github/skills/
# ---------------------------------------------------------------------------


class TestNoSymlinks:
    """.github/skills/ must be a real directory (inline copy), not symlink."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_github_skills_not_symlink(self, project: str, root: Path):
        github_skills = root / ".github" / "skills"
        if not github_skills.exists():
            pytest.skip(f"{project}: no .github/skills/")
        assert not github_skills.is_symlink(), (
            f"{project}: .github/skills/ is still a symlink. "
            f"Run: dx-agentic-gen generate"
        )


# ---------------------------------------------------------------------------
# Frontmatter transformation
# ---------------------------------------------------------------------------


class TestFrontmatterTransformation:
    """Capabilities → tools mapping must be correct."""

    def test_copilot_tools_mapping(self):
        """COPILOT_TOOLS dict must have all standard capabilities."""
        from dx_agentic_dev_gen.constants import COPILOT_TOOLS
        required = {"read", "edit", "search", "execute", "sub-agent", "ask-user"}
        assert required.issubset(COPILOT_TOOLS.keys())

    def test_claude_tools_mapping(self):
        """CLAUDE_TOOLS dict must have all standard capabilities."""
        from dx_agentic_dev_gen.constants import CLAUDE_TOOLS
        required = {"read", "edit", "search", "execute", "sub-agent", "ask-user"}
        assert required.issubset(CLAUDE_TOOLS.keys())

    def test_capabilities_to_tools_expansion(self):
        """capabilities_to_tools must return sorted deduplicated tools."""
        from dx_agentic_dev_gen.transformers import capabilities_to_tools
        from dx_agentic_dev_gen.constants import COPILOT_TOOLS

        result = capabilities_to_tools(["read", "edit"], COPILOT_TOOLS)
        assert isinstance(result, list)
        assert result == sorted(set(result))  # sorted + deduped
        assert len(result) > 0

    def test_routes_to_handoffs(self):
        """routes-to entries must convert to handoffs with correct keys."""
        from dx_agentic_dev_gen.transformers import routes_to_handoffs

        routes = [
            {"label": "Build", "target": "dx-builder", "description": "Route to builder"},
        ]
        handoffs = routes_to_handoffs(routes)
        assert len(handoffs) == 1
        h = handoffs[0]
        assert h["label"] == "Build"
        assert h["agent"] == "dx-builder"
        assert h["prompt"] == "Route to builder"
        assert h["send"] is False


# ---------------------------------------------------------------------------
# Instruction template validation
# ---------------------------------------------------------------------------


class TestTemplatePlaceholders:
    """Generated instruction files must not have leftover {{...}} placeholders."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_no_leftover_placeholders(self, project: str, root: Path):
        """CLAUDE.md, AGENTS.md, copilot-instructions.md must not contain {{...}}."""
        import re

        pattern = re.compile(r"\{\{[A-Z_:]+\}\}")
        instruction_files = [
            root / "CLAUDE.md",
            root / "AGENTS.md",
            root / ".github" / "copilot-instructions.md",
            root / "CLAUDE-KO.md",
            root / "AGENTS-KO.md",
            root / ".github" / "copilot-instructions-KO.md",
        ]
        leftover = []
        for f in instruction_files:
            if f.exists():
                content = f.read_text(encoding="utf-8")
                matches = pattern.findall(content)
                if matches:
                    leftover.append(f"{f.name}: {matches}")
        assert not leftover, (
            f"{project}: Leftover template placeholders: {leftover}"
        )


class TestKOStructuralParity:
    """KO instruction files must have the same section structure as EN."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_ko_sections_match_en(self, project: str, root: Path):
        """KO files must have same number of ## headings as EN counterparts."""
        import re

        pairs = [
            ("CLAUDE.md", "CLAUDE-KO.md"),
            ("AGENTS.md", "AGENTS-KO.md"),
            ("copilot-instructions.md", "copilot-instructions-KO.md"),
        ]
        heading_re = re.compile(r"^#{1,3} ", re.MULTILINE)
        mismatches = []
        for en_name, ko_name in pairs:
            if "copilot" in en_name:
                en_path = root / ".github" / en_name
                ko_path = root / ".github" / ko_name
            else:
                en_path = root / en_name
                ko_path = root / ko_name
            if not en_path.exists() or not ko_path.exists():
                continue
            en_count = len(heading_re.findall(en_path.read_text(encoding="utf-8")))
            ko_count = len(heading_re.findall(ko_path.read_text(encoding="utf-8")))
            if en_count != ko_count:
                mismatches.append(
                    f"{en_name}({en_count}) != {ko_name}({ko_count})"
                )
        assert not mismatches, (
            f"{project}: KO/EN heading count mismatch: {mismatches}"
        )


class TestInstructionGeneratorClean:
    """Instruction generation must match disk for all repos."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_instructions_check_clean(self, project: str, root: Path):
        """dx-agentic-gen check --platform instructions must be clean."""
        from dx_agentic_dev_gen.generator import Generator

        gen = Generator(root)
        clean, report = gen.check(platform="instructions")
        assert clean, (
            f"{project}: Instruction drift:\n" + "\n".join(report)
        )
