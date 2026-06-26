# SPDX-License-Identifier: Apache-2.0
"""
Tests for dx-agent-dev-gen generator correctness.

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

# Co-located tool tests — no test-package (avoid shadowing the real
# `dx_agent_dev_gen` import package), so define the repo roots locally.
# .deepx/tools/tests/dx_agent_dev_gen/test_generator.py → parents[4] == suite root
SUITE_ROOT = Path(__file__).resolve().parents[4]
PROJECT_ROOTS = {
    "suite": SUITE_ROOT,
    "compiler": SUITE_ROOT / "dx-compiler",
    "runtime": SUITE_ROOT / "dx-runtime",
    "app": SUITE_ROOT / "dx-runtime" / "dx_app",
    "stream": SUITE_ROOT / "dx-runtime" / "dx_stream",
}


# ---------------------------------------------------------------------------
# Generator package availability
# ---------------------------------------------------------------------------


class TestGeneratorPackage:
    """dx-agent-dev-gen must be installed and functional."""

    def test_importable(self):
        """Package can be imported."""
        import dx_agent_dev_gen
        assert dx_agent_dev_gen.__version__

    def test_cli_version(self):
        """CLI --version works."""
        from dx_agent_dev_gen.cli import main
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
        """dx-agent-gen check must exit 0 (no drift)."""
        from dx_agent_dev_gen.generator import Generator

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
            f"Run: dx-agent-gen generate"
        )


# ---------------------------------------------------------------------------
# Frontmatter transformation
# ---------------------------------------------------------------------------


class TestFrontmatterTransformation:
    """Capabilities → tools mapping must be correct."""

    def test_copilot_tools_mapping(self):
        """COPILOT_TOOLS dict must have all standard capabilities."""
        from dx_agent_dev_gen.constants import COPILOT_TOOLS
        required = {"read", "edit", "search", "execute", "sub-agent", "ask-user"}
        assert required.issubset(COPILOT_TOOLS.keys())

    def test_claude_tools_mapping(self):
        """CLAUDE_TOOLS dict must have all standard capabilities."""
        from dx_agent_dev_gen.constants import CLAUDE_TOOLS
        required = {"read", "edit", "search", "execute", "sub-agent", "ask-user"}
        assert required.issubset(CLAUDE_TOOLS.keys())

    def test_capabilities_to_tools_expansion(self):
        """capabilities_to_tools must return sorted deduplicated tools."""
        from dx_agent_dev_gen.transformers import capabilities_to_tools
        from dx_agent_dev_gen.constants import COPILOT_TOOLS

        result = capabilities_to_tools(["read", "edit"], COPILOT_TOOLS)
        assert isinstance(result, list)
        assert result == sorted(set(result))  # sorted + deduped
        assert len(result) > 0

    def test_routes_to_handoffs(self):
        """routes-to entries must convert to handoffs with correct keys."""
        from dx_agent_dev_gen.transformers import routes_to_handoffs

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
        """dx-agent-gen check --platform instructions must be clean."""
        from dx_agent_dev_gen.generator import Generator

        gen = Generator(root)
        clean, report = gen.check(platform="instructions")
        assert clean, (
            f"{project}: Instruction drift:\n" + "\n".join(report)
        )


# ---------------------------------------------------------------------------
# Prune — remove stale generator outputs (orphans), never hand-authored files
# ---------------------------------------------------------------------------


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_min_repo(tmp_path: Path) -> Path:
    """A minimal repo with one skill + one agent so generate() produces outputs."""
    deepx = tmp_path / ".deepx"
    _write(
        deepx / "skills" / "dx-foo" / "SKILL.md",
        "---\nname: dx-foo\ndescription: Foo skill for tests.\n---\n\nBody of foo.\n",
    )
    _write(
        deepx / "agents" / "dx-bar.md",
        "---\nname: dx-bar\ndescription: Bar agent for tests.\n"
        "capabilities: [read, execute]\n---\n\nBar agent body.\n",
    )
    return tmp_path


class TestGeneratorPrune:
    """`prune` removes orphan outputs (renamed/removed source) but preserves
    live generated files AND hand-authored files."""

    AUTO_MARKER = "AUTO-GENERATED from .deepx/"

    def _inject_orphans(self, repo: Path):
        """Returns (orphans, keepers) path lists."""
        orphans = [
            repo / ".github" / "skills" / "dx-old" / "SKILL.md",
            repo / ".claude" / "skills" / "dx-old" / "SKILL.md",
            repo / ".cursor" / "rules" / "skill-dx-old.mdc",
            repo / ".github" / "agents" / "dx-oldagent.agent.md",
            repo / ".claude" / "agents" / "dx-oldagent.md",
            repo / ".opencode" / "agents" / "dx-oldagent.md",
            repo / ".cursor" / "rules" / "dx-oldagent.mdc",  # orphan agent rule
        ]
        for o in orphans:
            # orphan agent rule must carry the gen marker to be eligible
            body = f"<!-- {self.AUTO_MARKER} -->\nstale\n" if o.suffix == ".mdc" else "stale\n"
            _write(o, body)
        # hand-authored cursor rule WITHOUT the gen marker — must be preserved
        hand = repo / ".cursor" / "rules" / "python-example.mdc"
        _write(hand, "---\ndescription: hand-authored\n---\nKeep me.\n")
        return orphans, [hand]

    def test_prune_dry_run_lists_orphans_only(self, tmp_path):
        from dx_agent_dev_gen.generator import Generator

        repo = _make_min_repo(tmp_path)
        gen = Generator(repo)
        gen.generate(platform="all")
        live = set(gen._collect_expected("all"))
        orphans, keepers = self._inject_orphans(repo)

        removed, report = gen.prune(platform="all", dry_run=True)
        removed = set(removed)

        def _covered(p: Path) -> bool:
            # prune may remove a whole skill dir, which subsumes its SKILL.md
            return p in removed or any(parent in removed for parent in p.parents)

        # every injected orphan is flagged (directly or via its parent dir)
        for o in orphans:
            assert _covered(o), f"orphan not flagged: {o.relative_to(repo)}\n{report}"
        # hand-authored + live outputs are NOT flagged
        for k in keepers:
            assert k not in removed, f"hand-authored wrongly flagged: {k}"
        assert not (live & removed), "live generated output wrongly flagged for prune"
        # dry-run must not delete anything
        for o in orphans:
            assert o.exists(), "dry-run deleted a file"

    def test_prune_deletes_orphans_preserves_rest(self, tmp_path):
        from dx_agent_dev_gen.generator import Generator

        repo = _make_min_repo(tmp_path)
        gen = Generator(repo)
        gen.generate(platform="all")
        live = set(gen._collect_expected("all"))
        orphans, keepers = self._inject_orphans(repo)

        gen.prune(platform="all", dry_run=False)

        for o in orphans:
            assert not o.exists(), f"orphan not pruned: {o.relative_to(repo)}"
        for k in keepers:
            assert k.exists(), f"hand-authored file wrongly deleted: {k}"
        for f in live:
            assert f.exists(), f"live generated file wrongly deleted: {f}"

    def test_prune_is_idempotent(self, tmp_path):
        from dx_agent_dev_gen.generator import Generator

        repo = _make_min_repo(tmp_path)
        gen = Generator(repo)
        gen.generate(platform="all")
        self._inject_orphans(repo)
        gen.prune(platform="all", dry_run=False)
        removed2, _ = gen.prune(platform="all", dry_run=False)
        assert removed2 == [], "second prune should find nothing"

    def test_generate_prune_integration_via_cli(self, tmp_path):
        from dx_agent_dev_gen.cli import main

        repo = _make_min_repo(tmp_path)
        # first generate to lay down live outputs
        assert main(["generate", "--repo", str(repo)]) == 0
        orphans, keepers = self._inject_orphans(repo)
        # generate --prune should remove orphans in one pass
        rc = main(["generate", "--repo", str(repo), "--prune"])
        assert rc == 0
        for o in orphans:
            assert not o.exists(), f"generate --prune left orphan: {o.relative_to(repo)}"
        for k in keepers:
            assert k.exists(), f"generate --prune deleted hand-authored: {k}"
