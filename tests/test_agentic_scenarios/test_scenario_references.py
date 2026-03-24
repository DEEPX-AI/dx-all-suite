# SPDX-License-Identifier: Apache-2.0
"""
Tests for scenario references: agents, skills, and file paths.

Validates:
- @agent-name references in guides point to existing agent .md files
- /skill-name references in guides point to existing skill .md files
- Agent files referenced in scenarios actually exist on disk
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

import pytest

from .conftest import (
    GUIDE_PAIRS,
    PROJECT_ROOTS,
    GuidePair,
    agent_names_from_dir,
    extract_agent_references,
    extract_skill_references,
    list_md_files,
    read_markdown,
    skill_names_from_dir,
)


# ---------------------------------------------------------------------------
# Build the ground truth: all agents and skills that exist on disk
# ---------------------------------------------------------------------------


def _collect_all_agents() -> Dict[str, Path]:
    """Collect all agent names -> file path from all .deepx/agents/ dirs."""
    agents: Dict[str, Path] = {}
    for name, root in PROJECT_ROOTS.items():
        agents_dir = root / ".deepx" / "agents"
        if agents_dir.exists():
            for f in list_md_files(agents_dir):
                agents[f.stem] = f
    return agents


def _collect_agents_from_agents_md() -> Set[str]:
    """Collect agent names listed in AGENTS.md files (virtual/logical agents)."""
    agents: Set[str] = set()
    for name, root in PROJECT_ROOTS.items():
        agents_md = root / "AGENTS.md"
        if agents_md.exists():
            text = agents_md.read_text(encoding="utf-8")
            agents.update(extract_agent_references(text))
    return agents


def _collect_all_skills() -> Dict[str, Path]:
    """Collect all skill names -> file path from .deepx/skills/ and .opencode/skills/ dirs."""
    skills: Dict[str, Path] = {}
    for name, root in PROJECT_ROOTS.items():
        # .deepx/skills/ — flat .md files
        skills_dir = root / ".deepx" / "skills"
        if skills_dir.exists():
            for f in list_md_files(skills_dir):
                skills[f.stem] = f
        # .opencode/skills/ — subdirectories with SKILL.md
        oc_skills_dir = root / ".opencode" / "skills"
        if oc_skills_dir.exists():
            for d in oc_skills_dir.iterdir():
                if d.is_dir() and (d / "SKILL.md").exists():
                    skills.setdefault(d.name, d / "SKILL.md")
    return skills


ALL_AGENTS = _collect_all_agents()
ALL_AGENTS_LOGICAL = _collect_agents_from_agents_md()
ALL_VALID_AGENTS = set(ALL_AGENTS.keys()) | ALL_AGENTS_LOGICAL
ALL_SKILLS = _collect_all_skills()


# ---------------------------------------------------------------------------
# Agent reference tests
# ---------------------------------------------------------------------------


class TestAgentReferences:
    """Agents referenced in guides must have corresponding .md files."""

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_en_agent_references_exist(self, pair: GuidePair):
        """Every @agent-name in EN guide must map to an existing agent file
        or be listed in an AGENTS.md as a logical agent."""
        en_text = read_markdown(pair.en_path)
        refs = extract_agent_references(en_text)
        if not refs:
            pytest.skip(f"No @agent references found in {pair.label} EN guide")

        missing = [a for a in set(refs) if a not in ALL_VALID_AGENTS]
        assert not missing, (
            f"{pair.label} EN guide references agents that don't exist:\n"
            f"  Missing: {missing}\n"
            f"  Available agents: {sorted(ALL_VALID_AGENTS)}"
        )

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_ko_agent_references_exist(self, pair: GuidePair):
        """Every @agent-name in KO guide must map to an existing agent file
        or be listed in an AGENTS.md as a logical agent."""
        ko_text = read_markdown(pair.ko_path)
        refs = extract_agent_references(ko_text)
        if not refs:
            pytest.skip(f"No @agent references found in {pair.label} KO guide")

        missing = [a for a in set(refs) if a not in ALL_VALID_AGENTS]
        assert not missing, (
            f"{pair.label} KO guide references agents that don't exist:\n"
            f"  Missing: {missing}\n"
            f"  Available agents: {sorted(ALL_VALID_AGENTS)}"
        )

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_en_ko_agent_references_match(self, pair: GuidePair):
        """EN and KO guides must reference the same set of agents."""
        en_text = read_markdown(pair.en_path)
        ko_text = read_markdown(pair.ko_path)
        en_refs = set(extract_agent_references(en_text))
        ko_refs = set(extract_agent_references(ko_text))
        if not en_refs and not ko_refs:
            pytest.skip(f"No agent references in {pair.label}")

        en_only = en_refs - ko_refs
        ko_only = ko_refs - en_refs
        assert not en_only and not ko_only, (
            f"{pair.label}: Agent references differ between EN and KO.\n"
            f"  EN-only: {en_only or 'none'}\n"
            f"  KO-only: {ko_only or 'none'}"
        )


# ---------------------------------------------------------------------------
# Skill reference tests
# ---------------------------------------------------------------------------


class TestSkillReferences:
    """Skills referenced in guides must have corresponding .md files."""

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_en_skill_references_exist(self, pair: GuidePair):
        """Every /skill-name in EN guide must map to an existing skill file."""
        en_text = read_markdown(pair.en_path)
        refs = extract_skill_references(en_text)
        if not refs:
            pytest.skip(f"No skill references found in {pair.label} EN guide")

        missing = [s for s in set(refs) if s not in ALL_SKILLS]
        assert not missing, (
            f"{pair.label} EN guide references skills that don't exist:\n"
            f"  Missing: {missing}\n"
            f"  Available skills: {sorted(ALL_SKILLS.keys())}"
        )

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_ko_skill_references_exist(self, pair: GuidePair):
        """Every /skill-name in KO guide must map to an existing skill file."""
        ko_text = read_markdown(pair.ko_path)
        refs = extract_skill_references(ko_text)
        if not refs:
            pytest.skip(f"No skill references found in {pair.label} KO guide")

        missing = [s for s in set(refs) if s not in ALL_SKILLS]
        assert not missing, (
            f"{pair.label} KO guide references skills that don't exist:\n"
            f"  Missing: {missing}\n"
            f"  Available skills: {sorted(ALL_SKILLS.keys())}"
        )


# ---------------------------------------------------------------------------
# Agent infrastructure completeness
# ---------------------------------------------------------------------------


class TestAgentInfrastructure:
    """Each project with .deepx/ must have valid agent infrastructure."""

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items() if k != "suite"],
        ids=[k for k in PROJECT_ROOTS if k != "suite"],
    )
    def test_agents_dir_exists(self, project: str, root: Path):
        """Projects with .deepx/ must have an agents/ subdirectory."""
        deepx = root / ".deepx"
        if not deepx.exists():
            pytest.skip(f"{project} has no .deepx/ directory")
        agents_dir = deepx / "agents"
        assert agents_dir.exists(), (
            f"{project}: .deepx/ exists but .deepx/agents/ is missing"
        )

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items() if k != "suite"],
        ids=[k for k in PROJECT_ROOTS if k != "suite"],
    )
    def test_skills_dir_exists(self, project: str, root: Path):
        """Projects with .deepx/ must have a skills/ subdirectory."""
        deepx = root / ".deepx"
        if not deepx.exists():
            pytest.skip(f"{project} has no .deepx/ directory")
        skills_dir = deepx / "skills"
        assert skills_dir.exists(), (
            f"{project}: .deepx/ exists but .deepx/skills/ is missing"
        )

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items() if k != "suite"],
        ids=[k for k in PROJECT_ROOTS if k != "suite"],
    )
    def test_agents_are_not_empty(self, project: str, root: Path):
        """Agent .md files must have meaningful content (>50 bytes)."""
        agents_dir = root / ".deepx" / "agents"
        if not agents_dir.exists():
            pytest.skip(f"{project} has no .deepx/agents/")
        for agent_file in list_md_files(agents_dir):
            size = agent_file.stat().st_size
            assert size > 50, (
                f"{project}: Agent file {agent_file.name} is too small ({size} bytes)"
            )

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items() if k != "suite"],
        ids=[k for k in PROJECT_ROOTS if k != "suite"],
    )
    def test_skills_are_not_empty(self, project: str, root: Path):
        """Skill .md files must have meaningful content (>50 bytes)."""
        skills_dir = root / ".deepx" / "skills"
        if not skills_dir.exists():
            pytest.skip(f"{project} has no .deepx/skills/")
        for skill_file in list_md_files(skills_dir):
            size = skill_file.stat().st_size
            assert size > 50, (
                f"{project}: Skill file {skill_file.name} is too small ({size} bytes)"
            )


# ---------------------------------------------------------------------------
# Cross-check: every agent on disk is referenced by at least one guide
# ---------------------------------------------------------------------------


class TestOrphanedAgents:
    """Agents and skills on disk should be referenced by at least one guide."""

    def test_no_orphaned_agents(self, all_guide_pairs):
        """Every agent file should be referenced in at least one guide."""
        all_referenced: Set[str] = set()
        for pair in all_guide_pairs:
            en_text = read_markdown(pair.en_path)
            all_referenced.update(extract_agent_references(en_text))

        orphaned = set(ALL_AGENTS.keys()) - all_referenced
        # This is a warning-level test — orphaned agents are not necessarily bugs
        if orphaned:
            pytest.xfail(
                f"Agents exist on disk but are not referenced in any guide: {orphaned}"
            )

    def test_no_orphaned_skills(self, all_guide_pairs):
        """Every skill file should be referenced in at least one guide."""
        all_referenced: Set[str] = set()
        for pair in all_guide_pairs:
            en_text = read_markdown(pair.en_path)
            all_referenced.update(extract_skill_references(en_text))

        orphaned = set(ALL_SKILLS.keys()) - all_referenced
        if orphaned:
            pytest.xfail(
                f"Skills exist on disk but are not referenced in any guide: {orphaned}"
            )
